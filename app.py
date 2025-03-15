import os
import logging
import asyncio
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import ADMIN_USERNAME, ADMIN_PASSWORD, TELEGRAM_TOKEN
from logger import setup_logger
import nest_asyncio
import socket

# Импортируем базу данных
from database import db
from database.database import migrate_database, save_setting  # Добавляем save_setting

# Инициализируем приложение
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", 'your_secret_key')

# Настраиваем базу данных SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'crypto_bot.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"  # Используем SQLite
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Инициализируем SQLAlchemy с Flask
db.init_app(app)

# Настройка логгера
site_logger, bot_logger = setup_logger()

# Настройка базового логирования
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

# Инициализация asyncio
nest_asyncio.apply()

# Импорт моделей (должен быть после инициализации db)
import models

# Инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Настраиваем функцию загрузки пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# Переменная для отслеживания процесса бота
bot_process = None

# Создаем таблицы в базе данных и начальные данные
with app.app_context():
    migrate_database()  # Выполняем миграцию базы данных
    db.create_all()
    
    # Создаем администратора, если его еще нет
    admin = models.User.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        # Проверяем, существует ли пользователь с таким email
        admin_email = "admin@example.com"
        existing_email = models.User.query.filter_by(email=admin_email).first()
        
        # Если email уже занят, добавляем случайный суффикс
        if existing_email:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            admin_email = f"admin{timestamp}@example.com"
            
        admin = models.User(
            username=ADMIN_USERNAME,
            email=admin_email,
            is_admin=True
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        site_logger.info(f"Создан административный аккаунт: {ADMIN_USERNAME}")
    
    # Настройка для шифрования API ключей
    encryption_key_setting = models.Setting.query.filter_by(key="ENCRYPTION_KEY").first()
    if not encryption_key_setting:
        from cryptography.fernet import Fernet
        new_key = Fernet.generate_key().decode()
        encryption_key_setting = models.Setting(
            key="ENCRYPTION_KEY",
            category="security",
            description="Ключ для шифрования API ключей"
        )
        encryption_key_setting.set_value(new_key, encrypt=False)
        db.session.add(encryption_key_setting)
        db.session.commit()
        # Устанавливаем переменную окружения для текущего процесса
        os.environ["ENCRYPTION_KEY"] = new_key
        site_logger.info("Сгенерирован новый ключ шифрования")
    else:
        # Устанавливаем переменную окружения из базы данных
        os.environ["ENCRYPTION_KEY"] = encryption_key_setting.get_value()

async def respond_to_user(context, user_id, response):
    """Отправляет ответ пользователю через Telegram."""
    if context:
        try:
            await context.bot.send_message(chat_id=user_id, text=response)
            site_logger.info(f"Ответ отправлен пользователю {user_id}")
        except Exception as e:
            site_logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Получаем логи из базы данных
    logs = models.Log.query.order_by(models.Log.timestamp.desc()).limit(10).all()
    # Получаем сообщения поддержки
    support_messages = models.SupportMessage.query.order_by(models.SupportMessage.timestamp.desc()).all()
    # Получаем статистику
    total_logs = models.Log.query.count()
    total_messages = models.SupportMessage.query.count()
    unread_messages = models.SupportMessage.query.filter_by(is_read=False).count()
    
    # Возвращаем шаблон с данными
    return render_template(
        'index.html', 
        logs=logs, 
        support_messages=support_messages,
        total_logs=total_logs,
        total_messages=total_messages,
        unread_messages=unread_messages
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Если пользователь уже авторизован, перенаправляем на дашборд
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Обработка формы логина
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Ищем пользователя в базе данных
        user = models.User.query.filter_by(username=username).first()
        
        # Проверяем пароль
        if user and user.check_password(password):
            # Авторизуем пользователя
            login_user(user)
            
            # Обновляем время последнего входа
            user.last_login = datetime.now()
            db.session.commit()
            
            # Логируем успешный вход
            site_logger.info(f"Пользователь {username} успешно вошел в систему.")
            
            # Добавляем запись в лог
            log_entry = models.Log(
                level="INFO",
                message=f"Пользователь {username} успешно вошел в систему.",
                source="admin_panel",
                user_id=user.id
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Перенаправляем на дашборд
            return redirect(url_for('dashboard'))
        else:
            # Логируем неудачную попытку входа
            site_logger.warning(f"Неудачная попытка входа с логином: {username}")
            
            # Добавляем запись в лог
            log_entry = models.Log(
                level="WARNING",
                message=f"Неудачная попытка входа с логином: {username}",
                source="admin_panel"
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Возвращаем страницу с сообщением об ошибке
            return render_template('login.html', error='Неверный логин или пароль')
    
    # Отображаем форму логина
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Записываем в лог
    site_logger.info(f"Пользователь {current_user.username} вышел из системы.")
    
    # Добавляем запись в лог
    log_entry = models.Log(
        level="INFO",
        message=f"Пользователь {current_user.username} вышел из системы.",
        source="admin_panel",
        user_id=current_user.id
    )
    db.session.add(log_entry)
    db.session.commit()
    
    # Выходим из системы
    logout_user()
    
    # Перенаправляем на страницу логина
    return redirect(url_for('login'))

@app.route('/settings')
@login_required
def settings():
    # Получаем настройки пользователя
    return render_template('settings.html')

@app.route('/api_keys')
@login_required
def api_keys():
    """Отображение всех добавленных API ключей."""
    # Получаем добавленные ключи из базы данных
    from database.database import get_setting
    api_keys = []

    # Проверяем наличие ключей в базе данных
    bybit_api_key = get_setting("BYBIT_API_KEY")
    bybit_secret = get_setting("BYBIT_SECRET")
    if bybit_api_key:
        api_keys.append({
            "name": "Bybit",
            "exchange": "Bybit",
            "key": bybit_api_key,
            "secret": bybit_secret,
            "permissions": "trade",  # Пример значения
            "created_at": datetime.now(),  # Пример значения
            "last_used": None,  # Пример значения
            "is_active": True,  # Пример значения
        })

    telegram_token = get_setting("TELEGRAM_TOKEN")
    if telegram_token:
        api_keys.append({
            "name": "Telegram Bot",
            "exchange": "Telegram",
            "key": telegram_token,
            "permissions": "bot",
            "created_at": datetime.now(),  # Пример значения
            "last_used": None,  # Пример значения
            "is_active": True,  # Пример значения
        })

    return render_template('api_keys.html', api_keys=api_keys)

@app.route('/add_api_key', methods=['GET', 'POST'])
@login_required
def add_api_key():
    """Добавление нового API ключа."""
    if request.method == 'POST':
        key_type = request.form['type']
        
        if key_type == 'exchange':
            exchange = request.form['exchange']
            api_key = request.form['api_key']
            api_secret = request.form['api_secret']
            
            # Сохраняем ключи в базе данных и обновляем config.py
            save_setting(f"{exchange.upper()}_API_KEY", api_key)
            save_setting(f"{exchange.upper()}_SECRET", api_secret)
            site_logger.info(f"Пользователь {current_user.username} добавил API ключ для {exchange}.")
        
        elif key_type == 'bot':
            bot_api_key = request.form['bot_api_key']
            
            # Сохраняем токен Telegram бота в базе данных и обновляем config.py
            save_setting("TELEGRAM_TOKEN", bot_api_key)
            site_logger.info(f"Пользователь {current_user.username} добавил токен Telegram бота.")
        
        flash('API ключ успешно добавлен/обновлен', 'success')
        return redirect(url_for('api_keys'))
        
    return render_template('add_api_key.html')

@app.route('/delete_api_key/<string:key_id>', methods=['POST'])  # Change key_name to key_id
@login_required
def delete_api_key(key_id):
    """Удаление API ключа."""
    if key_id == "Telegram Bot":
        save_setting("TELEGRAM_TOKEN", None)
    else:
        save_setting(f"{key_id.upper()}_API_KEY", None)
        save_setting(f"{key_id.upper()}_SECRET", None)
    
    site_logger.info(f"Пользователь {current_user.username} удалил API ключ {key_id}.")
    flash('API ключ успешно удален', 'success')
    return redirect(url_for('api_keys'))

@app.route('/view_logs')
@login_required
def view_logs():
    # Получаем логи из базы данных
    logs = models.Log.query.order_by(models.Log.timestamp.desc()).limit(50).all()
    return render_template('logger.html', logs=logs)

@app.route('/support')
@login_required
def support():
    # Получаем все сообщения поддержки
    support_messages = models.SupportMessage.query.order_by(models.SupportMessage.timestamp.desc()).all()
    return render_template('support.html', support_messages=support_messages)

@app.route('/respond', methods=['POST'])
@login_required
def respond():
    message_id = request.form['message_id']
    response = request.form['response']
    
    # Находим сообщение
    message = models.SupportMessage.query.get_or_404(message_id)
    
    # Обновляем сообщение
    message.response = response
    message.is_read = True
    db.session.commit()
    
    # Отправляем ответ пользователю
    user_id = message.user_id
    asyncio.run(respond_to_user(app.telegram_context, user_id, response))
    
    # Логируем ответ
    site_logger.info(f"Ответ на сообщение {message_id} отправлен.")
    
    # Добавляем запись в лог
    log_entry = models.Log(
        level="INFO",
        message=f"Отправлен ответ на сообщение поддержки от пользователя {user_id}",
        source="admin_panel",
        user_id=current_user.id
    )
    db.session.add(log_entry)
    db.session.commit()
    
    flash('Ответ отправлен', 'success')
    return redirect(url_for('support'))

@app.route('/start_bot', methods=['POST'])
def start_bot():
    try:
        global bot_process
        # Проверяем, не запущен ли уже бот
        if bot_process is not None and bot_process.poll() is None:
            return jsonify(status="running", message="Бот уже запущен")
        
        # Запускаем процесс бота
        bot_process = subprocess.Popen(['python', 'bot.py'])
        site_logger.info("Бот запущен.")
        
        # Проверяем через короткий интервал, что бот успешно запущен
        if bot_process.poll() is not None:  # Процесс завершился сразу
            error_msg = f"Не удалось запустить бота. Код возврата: {bot_process.returncode}"
            site_logger.error(error_msg)
            return jsonify(status="error", message=error_msg)
            
        return jsonify(status="running")
    except Exception as e:
        error_msg = f"Ошибка при запуске бота: {str(e)}"
        site_logger.error(error_msg)
        return jsonify(status="error", message=error_msg)

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    try:
        global bot_process
        if bot_process is None or bot_process.poll() is not None:
            return jsonify(status="stopped", message="Бот уже остановлен")
            
        # Мягко останавливаем процесс
        bot_process.terminate()
        try:
            # Ждем завершения с таймаутом
            bot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Если процесс не завершился вовремя - прерываем принудительно
            bot_process.kill()
            site_logger.warning("Бот принудительно остановлен после таймаута.")
            
        site_logger.info("Бот остановлен.")
        return jsonify(status="stopped")
    except Exception as e:
        error_msg = f"Ошибка при остановке бота: {str(e)}"
        site_logger.error(error_msg)
        return jsonify(status="error", message=error_msg)

@app.route('/bot_status', methods=['GET'])
def bot_status():
    try:
        global bot_process
        # Проверяем процесс
        if bot_process and bot_process.poll() is None:
            return jsonify(status="running")
        return jsonify(status="stopped")
    except Exception as e:
        site_logger.error(f"Ошибка при проверке статуса бота: {e}")
        return jsonify(status="error", message=str(e))

@app.route('/clear_logs', methods=['POST'])
@login_required
def clear_logs():
    # Удаляем все логи из базы данных
    models.Log.query.delete()
    db.session.commit()
    
    # Логируем действие
    site_logger.info(f"Пользователь {current_user.username} очистил все логи.")
    
    # Создаем новую запись о очистке логов
    log_entry = models.Log(
        level="INFO",
        message=f"Пользователь {current_user.username} очистил все логи",
        source="admin_panel",
        user_id=current_user.id
    )
    db.session.add(log_entry)
    db.session.commit()
    
    flash('Логи успешно очищены', 'success')
    return redirect(url_for('view_logs'))

@app.route('/test_bot_api_key', methods=['POST'])
@login_required
def test_bot_api_key():
    # Получаем ключ Telegram бота
    bot_api_key = models.Setting.query.filter_by(key="TELEGRAM_API_KEY").first()
    if not bot_api_key or not bot_api_key.value:
        flash('Ключ Telegram бота не найден.', 'danger')
        return redirect(url_for('api_keys'))
    
    try:
        # Тестируем ключ, отправляя сообщение самому себе
        from telegram import Bot
        bot = Bot(token=bot_api_key.value)
        bot.send_message(chat_id=current_user.id, text="Тестовое сообщение: ключ Telegram бота работает!")
        flash('Ключ Telegram бота успешно протестирован.', 'success')
    except Exception as e:
        site_logger.error(f"Ошибка при тестировании ключа Telegram бота: {e}")
        flash(f'Ошибка при тестировании ключа: {e}', 'danger')
    
    return redirect(url_for('api_keys'))

if __name__ == "__main__":
    # Логируем токен Telegram для проверки
    site_logger.info(f"Токен Telegram: {TELEGRAM_TOKEN[:10]}...")  # Логируем первые символы токена
    # Добавляем контекст Telegram при запуске бота
    app.telegram_context = None
    
    # Получаем локальный IP-адрес
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Выводим информацию о доступе
    print(f"Сайт доступен локально по адресу: http://127.0.0.1:5000")
    print(f"Сайт доступен в локальной сети по адресу: http://{local_ip}:5000")
    
    # Запускаем приложение
    app.run(host="0.0.0.0", port=5000, debug=True)
