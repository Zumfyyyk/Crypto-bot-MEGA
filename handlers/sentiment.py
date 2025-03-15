from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import logging
from services.bybit_api import fetch_market_sentiment, fetch_top_gainers, fetch_top_losers

# Настройка логгера
logger = logging.getLogger(__name__)

async def sentiment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду анализа настроения рынка."""
    sentiment_menu = [
        [KeyboardButton("📈 Топ растущих"), KeyboardButton("📉 Топ падающих")],
        [KeyboardButton("📊 Обзор рынка"), KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(sentiment_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔍 Настроение рынка\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    
    query = update.callback_query
    if query:
        await query.answer()
    
    # Отправляем сообщение о загрузке
    if query:
        await query.edit_message_text("⏳ Анализирую настроение рынка...")
    else:
        await update.message.reply_text("⏳ Анализирую настроение рынка...")
    
    try:
        # Получаем данные о настроении рынка
        sentiment = await fetch_market_sentiment()
        
        # Получаем данные о топ растущих и падающих активах
        gainers = await fetch_top_gainers(3)  # Для краткости ограничиваем до 3
        losers = await fetch_top_losers(3)
        
        # На основе соотношения растущих и падающих определяем общее настроение
        if gainers and losers:
            # Подсчитываем средний процент изменения для топовых активов
            avg_gainers_change = sum(ticker['percentage'] * 100 for ticker in gainers) / len(gainers)
            avg_losers_change = sum(ticker['percentage'] * 100 for ticker in losers) / len(losers)
            
            # Определяем настроение на основе изменений
            if avg_gainers_change > abs(avg_losers_change) * 1.5:
                market_mood = "🟢 *Бычье*"
                description = "Рынок демонстрирует сильное бычье настроение. Большинство активов растет."
            elif abs(avg_losers_change) > avg_gainers_change * 1.5:
                market_mood = "🔴 *Медвежье*"
                description = "Рынок демонстрирует сильное медвежье настроение. Большинство активов падает."
            else:
                market_mood = "🟡 *Нейтральное*"
                description = "Рынок демонстрирует смешанные сигналы. Нет четкого направления движения."
        else:
            market_mood = "⚪ *Неопределенное*"
            description = "Не удалось определить настроение рынка из-за недостаточного количества данных."
        
        # Формируем сообщение с данными
        message_text = (
            "🔍 *Анализ настроения рынка*\n\n"
            f"Текущее настроение: {market_mood}\n\n"
            f"{description}\n\n"
        )
        
        # Добавляем информацию о топ растущих активах
        if gainers and len(gainers) > 0:
            message_text += "📈 *Топ растущих активов:*\n"
            for ticker in gainers:
                symbol = ticker['symbol'].split('/')[0]
                change = ticker['percentage'] * 100
                message_text += f"• {symbol}: {change:+.2f}%\n"
            message_text += "\n"
        
        # Добавляем информацию о топ падающих активах
        if losers and len(losers) > 0:
            message_text += "📉 *Топ падающих активов:*\n"
            for ticker in losers:
                symbol = ticker['symbol'].split('/')[0]
                change = ticker['percentage'] * 100
                message_text += f"• {symbol}: {change:+.2f}%\n"
            message_text += "\n"
        
        # Добавляем рекомендации на основе настроения
        if market_mood == "🟢 *Бычье*":
            message_text += (
                "💡 *Рекомендации:*\n"
                "• Можно рассмотреть возможность входа в длинные позиции\n"
                "• Особое внимание обратите на активы с наибольшим ростом\n"
                "• Не забывайте про управление рисками и стоп-лоссы"
            )
        elif market_mood == "🔴 *Медвежье*":
            message_text += (
                "💡 *Рекомендации:*\n"
                "• Соблюдайте осторожность при открытии новых позиций\n"
                "• Можно рассмотреть возможность входа в короткие позиции\n"
                "• Следите за уровнями поддержки ключевых активов"
            )
        else:
            message_text += (
                "💡 *Рекомендации:*\n"
                "• Будьте осторожны, рынок показывает смешанные сигналы\n"
                "• Торгуйте с меньшим объемом, чем обычно\n"
                "• Обращайте внимание на индивидуальные активы, а не на весь рынок"
            )
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="sentiment"),
                InlineKeyboardButton("💹 Рынок", callback_data="market")
            ],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Ошибка при анализе настроения рынка: {e}")
        
        # Создаем клавиатуру для возврата
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"❌ Произошла ошибка при анализе настроения рынка: {str(e)}"
        
        if query:
            await query.edit_message_text(message_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message_text, reply_markup=reply_markup)

def get_sentiment_handler():
    """Возвращает обработчик для функции анализа настроения рынка."""
    return CallbackQueryHandler(sentiment_command, pattern="^sentiment$")
