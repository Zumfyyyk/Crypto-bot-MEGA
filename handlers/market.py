from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import logging
from services.bybit_api import fetch_top_gainers, fetch_top_losers, fetch_market_sentiment
from services.chart import generate_market_overview_chart

# Настройка логгера
logger = logging.getLogger(__name__)

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду рынка и показывает опции."""
    market_menu = [
        [KeyboardButton("📈 Растущие"), KeyboardButton("📉 Падающие")],
        [KeyboardButton("📊 Обзор рынка"), KeyboardButton("🔍 Настроение рынка")],
        [KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(market_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "💹 Информация о рынке\n\n"
        "Выберите, что вы хотите узнать:",
        reply_markup=reply_markup
    )

async def show_top_gainers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает топ растущих криптовалют."""
    query = update.callback_query
    await query.answer()
    
    # Отправляем сообщение о загрузке
    await query.edit_message_text("⏳ Загружаю данные о растущих активах...")
    
    try:
        # Получаем данные о топ-5 растущих активах
        gainers = await fetch_top_gainers(5)
        
        if not gainers or len(gainers) == 0:
            # Создаем клавиатуру для возврата
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ Не удалось получить данные о растущих активах.",
                reply_markup=reply_markup
            )
            return
        
        # Формируем сообщение с данными
        message_text = "📈 *Топ растущих активов (24ч)*\n\n"
        
        for i, ticker in enumerate(gainers):
            symbol = ticker['symbol'].split('/')[0]  # Берем только первую часть пары (без /USDT)
            price = ticker['last']
            change = ticker['percentage'] * 100  # Преобразуем в проценты
            
            message_text += f"{i+1}. *{symbol}*: ${price:.4f} ({change:+.2f}%)\n"
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="top_gainers"),
                InlineKeyboardButton("📉 Показать падающие", callback_data="top_losers")
            ],
            [InlineKeyboardButton("◀️ Назад", callback_data="market")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных о растущих активах: {e}")
        
        # Создаем клавиатуру для возврата
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ Произошла ошибка при получении данных: {str(e)}",
            reply_markup=reply_markup
        )

async def show_top_losers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает топ падающих криптовалют."""
    query = update.callback_query
    await query.answer()
    
    # Отправляем сообщение о загрузке
    await query.edit_message_text("⏳ Загружаю данные о падающих активах...")
    
    try:
        # Получаем данные о топ-5 падающих активах
        losers = await fetch_top_losers(5)
        
        if not losers or len(losers) == 0:
            # Создаем клавиатуру для возврата
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ Не удалось получить данные о падающих активах.",
                reply_markup=reply_markup
            )
            return
        
        # Формируем сообщение с данными
        message_text = "📉 *Топ падающих активов (24ч)*\n\n"
        
        for i, ticker in enumerate(losers):
            symbol = ticker['symbol'].split('/')[0]  # Берем только первую часть пары (без /USDT)
            price = ticker['last']
            change = ticker['percentage'] * 100  # Преобразуем в проценты
            
            message_text += f"{i+1}. *{symbol}*: ${price:.4f} ({change:+.2f}%)\n"
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="top_losers"),
                InlineKeyboardButton("📈 Показать растущие", callback_data="top_gainers")
            ],
            [InlineKeyboardButton("◀️ Назад", callback_data="market")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных о падающих активах: {e}")
        
        # Создаем клавиатуру для возврата
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ Произошла ошибка при получении данных: {str(e)}",
            reply_markup=reply_markup
        )

async def show_market_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает общий обзор рынка."""
    query = update.callback_query
    await query.answer()
    
    # Отправляем сообщение о загрузке
    await query.edit_message_text("⏳ Загружаю данные о рынке...")
    
    try:
        # Получаем данные о топовых активах
        gainers = await fetch_top_gainers(10)
        
        if not gainers или len(gainers) == 0:
            # Создаем клавиатуру для возврата
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ Не удалось получить данные о рынке.",
                reply_markup=reply_markup
            )
            return
        
        # Генерируем график обзора рынка
        chart_buffer = await generate_market_overview_chart(gainers)
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="market_overview"),
                InlineKeyboardButton("📈 Топ растущих", callback_data="top_gainers")
            ],
            [InlineKeyboardButton("◀️ Назад", callback_data="market")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if chart_buffer:
            # Отправляем новое сообщение с графиком
            await query.delete_message()
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=chart_buffer,
                caption="📊 *Обзор рынка криптовалют*\n\nИзменения цен за последние 24 часа.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # Если не удалось создать график, отправляем только текст
            message_text = "📊 *Обзор рынка криптовалют*\n\n"
            
            for i, ticker in enumerate(gainers[:5]):  # Показываем только первые 5
                symbol = ticker['symbol'].split('/')[0]  # Берем только первую часть пары (без /USDT)
                price = ticker['last']
                change = ticker['percentage'] * 100  # Преобразуем в проценты
                
                message_text += f"{symbol}: ${price:.4f} ({change:+.2f}%)\n"
            
            await query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Ошибка при получении обзора рынка: {e}")
        
        # Создаем клавиатуру для возврата
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="market")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ Произошла ошибка при получении обзора рынка: {str(e)}",
            reply_markup=reply_markup
        )

def get_market_handler():
    """Возвращает обработчик для функции рынка."""
    return CallbackQueryHandler(market_command, pattern="^market$")
