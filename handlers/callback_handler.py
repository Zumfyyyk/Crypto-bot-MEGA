from telegram import Update
from telegram.ext import ContextTypes
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает колбеки, которые не обрабатываются другими обработчиками."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    logger.info(f"Получен необработанный callback от пользователя {user_id}: {callback_data}")
    
    await query.edit_message_text(
        "⚠️ Извините, эта функция в данный момент недоступна или находится в разработке."
    )
