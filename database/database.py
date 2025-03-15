import sqlite3
import logging
import os
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы для базы данных
DB_NAME = 'crypto_bot.db'

def create_connection():
    """Создание соединения с базой данных SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Доступ к столбцам по названию
        return conn
    except sqlite3.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None

def create_tables():
    """Создание необходимых таблиц, если их нет."""
    try:
        # Убедимся, что директория для файла базы данных существует
        db_dir = os.path.dirname(DB_NAME)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()

            # Создание таблицы logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Создание таблицы settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT
                )
            ''')

            # Создание таблицы support_messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS support_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            logger.info("Таблицы успешно созданы или уже существуют.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблиц: {e}")

def log_message(level, message):
    """Запись лог-сообщения в базу данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('INSERT INTO logs (level, message) VALUES (?, ?)', (level, message))
            conn.commit()
            logger.debug(f"Лог записан: [{level}] {message}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при записи лога: {e}")

def get_logs(limit=50):
    """Получение последних логов из базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return []
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении логов: {e}")
        return []

def save_setting(key, value):
    """Сохранение настройки в базе данных и обновление config.py."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
            conn.commit()
            logger.info(f"Настройка сохранена: {key} = {value}")
            
            # Обновляем config.py
            update_config_file(key, value)
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении настройки: {e}")

def update_config_file(key, value):
    """Обновление config.py при изменении настройки."""
    config_path = os.path.join(os.getcwd(), 'config', 'config.py')
    try:
        with open(config_path, 'r') as file:
            lines = file.readlines()
        
        updated = False
        with open(config_path, 'w') as file:
            for line in lines:
                if line.startswith(f"{key} ="):
                    # Обновляем существующую строку
                    file.write(f"{key} = '{value}'\n")
                    updated = True
                else:
                    file.write(line)
            
            if not updated:
                # Добавляем новую строку, если ключ не найден
                file.write(f"{key} = '{value}'\n")
        
        logger.info(f"Файл config.py обновлен: {key} = {value}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении config.py: {e}")

def get_setting(key):
    """Получение значения настройки по ключу."""
    try:
        with create_connection() as conn:
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении настройки: {e}")
        return None

def delete_setting(key):
    """Удаление настройки из базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
            conn.commit()
            logger.info(f"Настройка удалена: {key}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при удалении настройки: {e}")

def save_support_message(user_id, message):
    """Сохранение сообщения поддержки в базу данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute('INSERT INTO support_messages (user_id, message) VALUES (?, ?)', 
                           (user_id, message))
            conn.commit()
            logger.info(f"Сохранено сообщение поддержки от пользователя {user_id}")
            # Получаем ID вставленной записи
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении сообщения поддержки: {e}")
        return None

def get_support_message_by_id(message_id):
    """Получение сообщения поддержки по ID."""
    try:
        with create_connection() as conn:
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM support_messages WHERE id = ?', (message_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении сообщения поддержки: {e}")
        return None

def get_support_messages():
    """Получение всех сообщений поддержки из базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return []
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM support_messages ORDER BY timestamp DESC')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении сообщений поддержки: {e}")
        return []

def respond_to_support_message(message_id, response):
    """Отправка ответа на сообщение поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('UPDATE support_messages SET response = ? WHERE id = ?', 
                           (response, message_id))
            conn.commit()
            logger.info(f"Сохранен ответ на сообщение поддержки #{message_id}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении ответа на сообщение поддержки: {e}")

def clear_all_logs():
    """Очистка всех логов."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('DELETE FROM logs')
            conn.commit()
            logger.info("Все логи удалены.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при удалении всех логов: {e}")

def clear_all_support_messages():
    """Очистка всех сообщений поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('DELETE FROM support_messages')
            conn.commit()
            logger.info("Все сообщения поддержки удалены.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при удалении всех сообщений поддержки: {e}")

def get_unanswered_support_messages():
    """Получение необработанных сообщений поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return []
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM support_messages WHERE response IS NULL')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении необработанных сообщений: {e}")
        return []

def column_exists(cursor, table_name, column_name):
    """Проверяет, существует ли столбец в таблице."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row["name"] for row in cursor.fetchall()]
    return column_name in columns

def table_exists(cursor, table_name):
    """Проверяет, существует ли таблица в базе данных."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def migrate_database():
    """Обновление структуры базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()

            # Проверяем существование таблицы logs
            if not table_exists(cursor, "logs"):
                cursor.execute('''
                    CREATE TABLE logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        source TEXT DEFAULT NULL,
                        user_id INTEGER DEFAULT NULL
                    )
                ''')
                logger.info("Таблица logs создана заново.")
            else:
                # Добавляем недостающие столбцы в таблицу logs
                if not column_exists(cursor, "logs", "source"):
                    cursor.execute('''
                        ALTER TABLE logs ADD COLUMN source TEXT DEFAULT NULL
                    ''')
                if not column_exists(cursor, "logs", "user_id"):
                    cursor.execute('''
                        ALTER TABLE logs ADD COLUMN user_id INTEGER DEFAULT NULL
                    ''')

            # Проверяем существование таблицы support_messages
            if not table_exists(cursor, "support_messages"):
                cursor.execute('''
                    CREATE TABLE support_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username TEXT DEFAULT NULL,
                        message TEXT,
                        response TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT 0
                    )
                ''')
                logger.info("Таблица support_messages создана заново.")
            else:
                # Добавляем недостающие столбцы в таблицу support_messages
                if not column_exists(cursor, "support_messages", "username"):
                    cursor.execute('''
                        ALTER TABLE support_messages ADD COLUMN username TEXT DEFAULT NULL
                    ''')
                if not column_exists(cursor, "support_messages", "is_read"):
                    cursor.execute('''
                        ALTER TABLE support_messages ADD COLUMN is_read BOOLEAN DEFAULT 0
                    ''')

            # Добавляем недостающие столбцы в таблицу settings
            if not column_exists(cursor, "settings", "category"):
                cursor.execute('''
                    ALTER TABLE settings ADD COLUMN category TEXT DEFAULT NULL
                ''')
            if not column_exists(cursor, "settings", "description"):
                cursor.execute('''
                    ALTER TABLE settings ADD COLUMN description TEXT DEFAULT NULL
                ''')
            if not column_exists(cursor, "settings", "is_encrypted"):
                cursor.execute('''
                    ALTER TABLE settings ADD COLUMN is_encrypted BOOLEAN DEFAULT 0
                ''')

            conn.commit()
            logger.info("Миграция базы данных выполнена успешно.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            logger.warning("Миграция пропущена: столбцы уже существуют.")
        else:
            logger.error(f"Ошибка при миграции базы данных: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при миграции базы данных: {e}")
