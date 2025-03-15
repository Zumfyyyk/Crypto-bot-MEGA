from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import logging
from handlers.start import start_command

# Настройка логгера
logger = logging.getLogger(__name__)

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопки Назад - возврат в главное меню."""
    query = update.callback_query
    await query.answer()
    
    # Очищаем данные пользователя
    context.user_data.clear()
    
    # Создаем новое сообщение с главным меню вместо изменения текущего
    user = update.effective_user
    logger.info(f"Пользователь {user.id} вернулся в главное меню")
    
    # Создаем клавиатуру с основными функциями
    keyboard = [
        [
            InlineKeyboardButton("📊 Анализ", callback_data="analysis"),
            InlineKeyboardButton("💹 Рынок", callback_data="market")
        ],
        [
            InlineKeyboardButton("🔍 Сентимент", callback_data="sentiment"),
            InlineKeyboardButton("ℹ️ Информация", callback_data="info")
        ],
        [
            InlineKeyboardButton("🛟 Поддержка", callback_data="support"),
            InlineKeyboardButton("💰 Донат", callback_data="donate")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я Криптовалютный бот-помощник, который поможет тебе анализировать "
        "рынок и отслеживать изменения цен.\n\n"
        "Что я умею:\n"
        "• Анализировать графики криптовалют\n"
        "• Показывать информацию о рынке\n"
        "• Отслеживать настроение рынка\n"
        "• Предоставлять аналитическую информацию\n\n"
        "Выберите функцию:"
    )
    
    # Редактируем текущее сообщение или отправляем новое, если редактирование не удалось
    try:
        await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_message,
            reply_markup=reply_markup
        )

def get_back_handler():
    """Возвращает обработчик для кнопки возврата в главное меню."""
    return CallbackQueryHandler(back_to_main, pattern="^back_to_main$")  # Убрали back_menu
