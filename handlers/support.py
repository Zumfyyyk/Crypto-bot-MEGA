from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
import logging
import datetime
from database.database import save_support_message, get_support_messages, get_support_message_by_id, respond_to_support_message

# Состояния диалога
WAITING_FOR_MESSAGE = 1

# Настройка логгера
logger = logging.getLogger(__name__)

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду поддержки."""
    support_menu = [
        [KeyboardButton("✉️ Написать в поддержку")],
        [KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(support_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "🛟 Техническая поддержка\n\n"
        "Если у вас возникли вопросы или проблемы при использовании бота, "
        "вы можете написать в поддержку. Мы постараемся ответить вам как можно скорее.",
        reply_markup=reply_markup
    )

async def start_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает диалог для отправки сообщения в поддержку."""
    query = update.callback_query
    await query.answer()
    
    message_text = (
        "✏️ *Отправка сообщения в поддержку*\n\n"
        "Пожалуйста, опишите ваш вопрос или проблему подробно. "
        "Мы ответим как можно скорее.\n\n"
        "Отправьте ваше сообщение прямо сейчас или нажмите 'Отмена'."
    )
    
    # Создаем клавиатуру с кнопкой отмены
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    return WAITING_FOR_MESSAGE

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученное сообщение поддержки."""
    user = update.effective_user
    message_text = update.message.text
    
    # Сохраняем сообщение в базу данных
    message_id = save_support_message(user.id, message_text)
    
    if message_id:
        # Создаем клавиатуру для возврата
        keyboard = [[InlineKeyboardButton("◀️ Назад в главное меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response_text = (
            "✅ *Сообщение отправлено!*\n\n"
            "Ваше сообщение успешно отправлено в поддержку. "
            "Мы ответим вам как можно скорее.\n\n"
            "Спасибо за обращение!"
        )
        
        await update.message.reply_text(response_text, reply_markup=reply_markup, parse_mode="Markdown")
        
        # Логируем получение сообщения
        logger.info(f"Получено сообщение поддержки от пользователя {user.id}: {message_text[:50]}...")
    else:
        # В случае ошибки
        keyboard = [[InlineKeyboardButton("🔄 Попробовать снова", callback_data="send_support_message")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ *Произошла ошибка*\n\nНе удалось отправить сообщение. Пожалуйста, попробуйте позже.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        logger.error(f"Ошибка при сохранении сообщения поддержки от пользователя {user.id}")
    
    return ConversationHandler.END

async def cancel_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет отправку сообщения поддержки."""
    query = update.callback_query
    if query:
        await query.answer()
        await support_command(update, context)
    
    return ConversationHandler.END

async def check_support_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверяет статус предыдущих запросов в поддержку."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Получаем все сообщения пользователя из базы данных
    try:
        messages = get_support_messages()
        user_messages = [m for m in messages if m['user_id'] == user.id]
        
        if not user_messages:
            # Если у пользователя нет сообщений
            await query.edit_message_text(
                "📭 *У вас пока нет обращений в поддержку*\n\n"
                "Вы можете отправить новое сообщение в поддержку.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Отправить сообщение", callback_data="send_support_message")],
                    [InlineKeyboardButton("◀️ Назад", callback_data="support")]
                ]),
                parse_mode="Markdown"
            )
            return
        
        # Формируем сообщение с последними обращениями
        message_text = "📋 *Ваши обращения в поддержку:*\n\n"
        
        # Ограничиваем количество отображаемых сообщений
        for i, msg in enumerate(user_messages[-5:]):  # Показываем последние 5 сообщений
            timestamp = msg['timestamp']
            date_str = timestamp.strftime("%d.%m.%Y %H:%M")
            status = "✅ Отвечено" if msg['response'] else "⏳ В обработке"
            
            message_text += f"{i+1}. *{date_str}*\n"
            message_text += f"Сообщение: {msg['message'][:50]}...\n"
            message_text += f"Статус: {status}\n"
            
            if msg['response']:
                message_text += f"Ответ: {msg['response'][:50]}...\n"
            
            message_text += "\n"
        
        # Добавляем клавиатуру
        keyboard = [
            [InlineKeyboardButton("📝 Новое сообщение", callback_data="send_support_message")],
            [InlineKeyboardButton("◀️ Назад", callback_data="support")]
        ]
        
        await query.edit_message_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    except Exception as e:
        logger.error(f"Ошибка при получении истории сообщений: {e}")
        await query.edit_message_text(
            "❌ *Произошла ошибка*\n\n"
            "Не удалось получить историю обращений. Пожалуйста, попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Назад", callback_data="support")]
            ]),
            parse_mode="Markdown"
        )

def get_support_handler():
    """Возвращает обработчик для функции поддержки."""
    support_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("support", support_command),
            CallbackQueryHandler(support_command, pattern="^support$"),
            CallbackQueryHandler(start_support_message, pattern="^send_support_message$"),
            CallbackQueryHandler(check_support_status, pattern="^check_support_status$")
        ],
        states={
            WAITING_FOR_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_message)]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_support, pattern="^support$"),
            CallbackQueryHandler(support_command, pattern="^back_to_main$")
        ]
    )
    
    return support_conv_handler
