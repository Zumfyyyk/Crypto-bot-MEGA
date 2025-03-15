from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import logging
import psutil
import platform
from datetime import datetime

# Настройка логгера
logger = logging.getLogger(__name__)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду информации."""
    info_menu = [
        [KeyboardButton("ℹ️ О боте"), KeyboardButton("🛠️ Статус системы")],
        [KeyboardButton("📚 Как пользоваться"), KeyboardButton("📜 Команды")],
        [KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(info_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "ℹ️ Информация\n\n"
        "Выберите раздел, чтобы узнать больше о боте:",
        reply_markup=reply_markup
    )

async def show_about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о боте."""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру для возврата
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "ℹ️ *О боте*\n\n"
        "Crypto Bot Assistant — это Telegram-бот для анализа криптовалютных данных, "
        "работающий на бирже Bybit и поддерживающий функции анализа графиков, "
        "статистики рынка и связи с пользователями.\n\n"
        "Версия: 1.0.0\n"
        "Разработчик: Никита Харченко (Zumfyyyk)\n\n"
        "Бот предоставляет актуальные данные о криптовалютных рынках, "
        "графики цен и технический анализ в удобном формате."
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус системы."""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру для возврата и обновления статуса
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить", callback_data="system_status")],
        [InlineKeyboardButton("◀️ Назад", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Получаем информацию о системе
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        uptime_str = str(uptime).split('.')[0]  # Без миллисекунд
        
        message_text = (
            "🛠️ *Статус системы*\n\n"
            f"🖥️ CPU: {cpu_usage}%\n"
            f"🧠 Память: {memory_usage}%\n"
            f"⏱️ Время работы: {uptime_str}\n"
            f"🌐 ОС: {platform.system()} {platform.release()}\n"
            f"🖥️ Платформа: {platform.machine()}\n\n"
            "Статус: 🟢 Рабочий"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении статуса системы: {e}")
        message_text = (
            "🛠️ *Статус системы*\n\n"
            "❌ Не удалось получить данные о системе.\n\n"
            f"Ошибка: {str(e)}"
        )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает инструкцию по использованию бота."""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру для возврата
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📚 *Как пользоваться ботом*\n\n"
        "1️⃣ *Начало работы:* Отправьте команду /start, чтобы увидеть главное меню.\n\n"
        "2️⃣ *Анализ криптовалют:* Выберите функцию «Анализ» в главном меню, затем выберите "
        "криптовалюту и таймфрейм для просмотра графика.\n\n"
        "3️⃣ *Рыночная информация:* Выберите функцию «Рынок», чтобы увидеть топ растущих и падающих "
        "активов, а также общий обзор рынка.\n\n"
        "4️⃣ *Настроение рынка:* Выберите функцию «Сентимент», чтобы увидеть текущее настроение "
        "рынка, основанное на различных индикаторах.\n\n"
        "5️⃣ *Поддержка:* Если у вас возникли вопросы или проблемы, выберите функцию «Поддержка» "
        "и отправьте сообщение. Мы ответим вам как можно скорее.\n\n"
        "Бот предоставляет интуитивно понятный интерфейс с кнопками для навигации по всем функциям."
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список доступных команд."""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру для возврата
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📜 *Доступные команды*\n\n"
        "/start - Запустить бота и показать главное меню\n"
        "/analysis - Анализ криптовалют и графики\n"
        "/market - Информация о рынке\n"
        "/sentiment - Анализ настроения рынка\n"
        "/support - Обратиться в поддержку\n"
        "/donate - Поддержать проект\n"
        "/info - Информация о боте и инструкции\n\n"
        "Помимо команд, вы можете использовать интерактивные кнопки в сообщениях для навигации."
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

def get_info_handler():
    """Возвращает обработчик для функции информации."""
    return CallbackQueryHandler(
        lambda update, context: (
            info_command(update, context) if update.callback_query.data == "info"
            else show_about_bot(update, context) if update.callback_query.data == "about_bot"
            else show_system_status(update, context) if update.callback_query.data == "system_status"
            else show_how_to_use(update, context) if update.callback_query.data == "how_to_use"
            else show_commands(update, context)
        ),
        pattern="^info|about_bot|system_status|how_to_use|commands$"
    )
