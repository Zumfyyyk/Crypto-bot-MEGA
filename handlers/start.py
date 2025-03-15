from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import logging
from handlers.analysis import analysis_command
from handlers.market import market_command
from handlers.sentiment import sentiment_command
from handlers.info import info_command
from handlers.support import support_command
from handlers.donate import donate_command

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запустил бота")
    
    # Главное меню
    main_menu = [
        [KeyboardButton("📊 Анализ"), KeyboardButton("💹 Рынок")],
        [KeyboardButton("🔍 Сентимент"), KeyboardButton("ℹ️ Информация")],
        [KeyboardButton("🛟 Поддержка"), KeyboardButton("💰 Донат")],
        [KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!!\n\n"
        "Я Криптовалютный бот-помощник, который поможет тебе анализировать рынок и отслеживать изменения цен.\n\n"
        "Что я умею:\n"
        "• Анализировать графики криптовалют\n"
        "• Показывать информацию о рынке\n"
        "• Отслеживать настроение рынка\n"
        "• Предоставлять аналитическую информацию\n\n"
        "Выберите функцию:"
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор пользователя из главного меню."""
    user_input = update.message.text
    logger.info(f"Пользователь {update.effective_user.id} выбрал: {user_input}")
    
    if user_input == "📊 Анализ":
        await analysis_command(update, context)
    elif user_input == "💹 Рынок":
        await market_command(update, context)
    elif user_input == "🔍 Сентимент":
        await sentiment_command(update, context)
    elif user_input == "ℹ️ Информация":
        await info_command(update, context)
    elif user_input == "🛟 Поддержка":
        await support_command(update, context)
    elif user_input == "💰 Донат":
        await donate_command(update, context)
    elif user_input == "◀️ Назад":
        await start_command(update, context)
    else:
        await update.message.reply_text("❌ Неизвестная команда. Пожалуйста, выберите опцию из меню.")

def get_start_handler():
    """Возвращает обработчики для команды /start и главного меню."""
    return [
        CommandHandler("start", start_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
    ]
