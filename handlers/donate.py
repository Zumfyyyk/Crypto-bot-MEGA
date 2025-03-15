from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Данные кошельков для доната
WALLETS = {
    "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "ETH": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "USDT (TRC-20)": "TGS1VpxqCUkbhT7PYHhXmptj1kLQE5Z2u9"
}

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду доната."""
    donate_menu = [
        [KeyboardButton("BTC"), KeyboardButton("ETH")],
        [KeyboardButton("USDT (TRC-20)"), KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(donate_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 Поддержка проекта\n\n"
        "Выберите криптовалюту для пожертвования:",
        reply_markup=reply_markup
    )

async def show_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает адрес кошелька для выбранной криптовалюты."""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем выбранную криптовалюту из callback_data
    crypto = query.data.replace("donate_", "")
    
    if crypto in WALLETS:
        wallet_address = WALLETS[crypto]
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("💰 Другая криптовалюта", callback_data="donate")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"💰 *Адрес кошелька {crypto}*\n\n"
            f"`{wallet_address}`\n\n"
            "Спасибо за вашу поддержку! Это помогает нам развивать бота и добавлять новые функции."
        )
        
        await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        # Если криптовалюта не найдена, возвращаемся к выбору
        await donate_command(update, context)

def get_donate_handler():
    """Возвращает обработчик для функции доната."""
    return CallbackQueryHandler(
        lambda update, context: (
            donate_command(update, context) 
            if update.callback_query.data == "donate" 
            else show_wallet(update, context)
        ),
        pattern="^donate|donate_"
    )
