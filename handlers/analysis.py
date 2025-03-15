from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import datetime
from services.bybit_api import fetch_ohlcv_async, fetch_ticker
from services.chart import generate_chart
import re

# Настройка логгера
logger = logging.getLogger(__name__)

# Часто используемые пары
POPULAR_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT"]

# Доступные таймфреймы
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду анализа."""
    analysis_menu = [
        [KeyboardButton("BTC/USDT"), KeyboardButton("ETH/USDT")],
        [KeyboardButton("SOL/USDT"), KeyboardButton("XRP/USDT")],
        [KeyboardButton("🔍 Поиск монеты"), KeyboardButton("◀️ Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(analysis_menu, resize_keyboard=True)
    
    await update.message.reply_text(
        "📊 Анализ криптовалют\n\n"
        "Выберите криптовалюту для анализа или воспользуйтесь поиском:",
        reply_markup=reply_markup
    )

async def handle_pair_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор пары и показывает доступные таймфреймы."""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем выбранную пару из callback_data
    pair = query.data.replace("pair_", "")
    
    # Сохраняем выбранную пару в контексте пользователя
    context.user_data["selected_pair"] = pair
    
    # Создаем клавиатуру с таймфреймами
    keyboard = []
    row = []
    for i, tf in enumerate(TIMEFRAMES):
        row.append(InlineKeyboardButton(tf, callback_data=f"timeframe_{tf}"))
        if (i + 1) % 3 == 0 or i == len(TIMEFRAMES) - 1:
            keyboard.append(row)
            row = []
    
    # Добавляем кнопку назад
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="analysis")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    symbol = pair.split('/')[0]  # Получаем символ из пары
    message_text = f"🕒 Выберите таймфрейм для *{symbol}*:"
    
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор таймфрейма и показывает график."""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем выбранный таймфрейм из callback_data
    timeframe = query.data.replace("timeframe_", "")
    
    # Получаем выбранную пару из контекста пользователя
    pair = context.user_data.get("selected_pair")
    
    if not pair:
        await query.edit_message_text("❌ Ошибка: не выбрана пара. Пожалуйста, начните снова командой /analysis")
        return
    
    # Отправляем сообщение о загрузке
    loading_message = await query.edit_message_text(
        f"⏳ Загружаю график для {pair} ({timeframe})...",
        parse_mode="Markdown"
    )
    
    try:
        # Генерируем график
        logger.info(f"Запрос графика для {pair}, таймфрейм {timeframe}")
        chart_buffer = await generate_chart(pair, timeframe, limit=50)
        
        if not chart_buffer:
            # Создаем клавиатуру для возврата
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"timeframe_{timeframe}")],
                [InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")],
                [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"❌ Не удалось получить данные для {pair} ({timeframe}).\n"
                f"Сервис Bybit временно недоступен или не предоставляет данные для этой пары/таймфрейма.",
                reply_markup=reply_markup
            )
            return
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{pair}_{timeframe}"),
                InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")
            ],
            [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем новое сообщение с графиком (из-за ограничений API Telegram)
        try:
            # Пробуем удалить предыдущее сообщение
            await query.delete_message()
        except Exception as e:
            logger.warning(f"Не удалось удалить предыдущее сообщение: {e}")
        
        # Отправляем график в любом случае
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=chart_buffer,
            caption=f"📊 График {pair} ({timeframe})\n\nДанные предоставлены Bybit API",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании графика: {e}")
        
        # Создаем клавиатуру для возврата с разными опциями
        keyboard = [
            [InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"timeframe_{timeframe}")],
            [InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")],
            [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Формируем сообщение об ошибке
        error_message = (
            f"❌ Не удалось создать график для {pair} ({timeframe}).\n\n"
            f"Причина: {str(e)[:100]}...\n\n"
            "Возможные решения:\n"
            "• Попробуйте обновить график\n"
            "• Выберите другую пару/таймфрейм\n"
            "• Попробуйте позже, когда API Bybit будет доступен"
        )
        
        try:
            await query.edit_message_text(error_message, reply_markup=reply_markup)
        except Exception as edit_err:
            logger.error(f"Не удалось отредактировать сообщение: {edit_err}")
            # Отправим новое сообщение, если не можем отредактировать
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                reply_markup=reply_markup
            )

async def handle_refresh_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновляет график для выбранной пары и таймфрейма."""
    query = update.callback_query
    await query.answer()
    
    # Разбираем callback_data для получения пары и таймфрейма
    _, pair, timeframe = query.data.split("_", 2)
    
    try:
        # Отправляем сообщение о загрузке
        await query.edit_message_caption(
            caption=f"⏳ Обновляю график для {pair} ({timeframe})...",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Не удалось обновить сообщение: {e}")
        # Продолжаем работу даже при ошибке редактирования
    
    try:
        # Генерируем обновленный график с большим количеством свечей
        logger.info(f"Запрос обновленного графика для {pair}, таймфрейм {timeframe}")
        chart_buffer = await generate_chart(pair, timeframe, limit=50)
        
        if not chart_buffer:
            # Создаем клавиатуру для возврата с дополнительными опциями
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"refresh_{pair}_{timeframe}")],
                [InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")],
                [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_caption(
                    caption=(f"❌ Не удалось получить данные для {pair} ({timeframe}).\n"
                             f"Сервис Bybit временно недоступен или не предоставляет данные для этой пары/таймфрейма."),
                    reply_markup=reply_markup
                )
            except Exception as edit_err:
                logger.error(f"Ошибка при редактировании сообщения: {edit_err}")
                # Отправляем новое сообщение, если не можем отредактировать
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(f"❌ Не удалось получить данные для {pair} ({timeframe}).\n"
                          f"Сервис Bybit временно недоступен или не предоставляет данные для этой пары/таймфрейма."),
                    reply_markup=reply_markup
                )
            return
        
        # Создаем клавиатуру для других действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{pair}_{timeframe}"),
                InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")
            ],
            [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем новое сообщение с графиком (из-за ограничений API Telegram)
        try:
            # Пробуем удалить предыдущее сообщение
            await query.delete_message()
        except Exception as e:
            logger.warning(f"Не удалось удалить предыдущее сообщение: {e}")
        
        # Отправляем график в любом случае
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=chart_buffer,
            caption=f"📊 График {pair} ({timeframe})\n\nДанные обновлены: {datetime.datetime.now().strftime('%H:%M:%S')}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении графика: {e}")
        
        # Создаем клавиатуру для возврата с дополнительными опциями
        keyboard = [
            [InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"refresh_{pair}_{timeframe}")],
            [InlineKeyboardButton("📈 Другой таймфрейм", callback_data=f"pair_{pair}")],
            [InlineKeyboardButton("◀️ Назад к парам", callback_data="analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Формируем подробное сообщение об ошибке
        error_message = (
            f"❌ Не удалось обновить график для {pair} ({timeframe}).\n\n"
            f"Причина: {str(e)[:100]}...\n\n"
            "Возможные решения:\n"
            "• Попробуйте обновить график снова\n"
            "• Выберите другую пару/таймфрейм\n"
            "• Попробуйте позже, когда API Bybit будет доступен"
        )
        
        try:
            # Пробуем отредактировать текущее сообщение
            await query.edit_message_caption(
                caption=error_message,
                reply_markup=reply_markup
            )
        except Exception as edit_err:
            logger.error(f"Не удалось отредактировать сообщение: {edit_err}")
            # Отправляем новое сообщение, если не можем отредактировать
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                reply_markup=reply_markup
            )

async def handle_search_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на поиск пары."""
    query = update.callback_query
    await query.answer()
    
    message_text = (
        "🔍 *Поиск пары*\n\n"
        "Введите название криптовалюты для поиска (например, BTC, ETH, SOL):"
    )
    
    # Устанавливаем флаг ожидания ввода пары
    context.user_data["awaiting_pair_input"] = True
    
    # Создаем клавиатуру с кнопкой назад
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="analysis")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_pair_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод названия криптовалюты для поиска пары."""
    # Проверяем, что бот ожидает ввод пары
    if not context.user_data.get("awaiting_pair_input"):
        return
    
    # Снимаем флаг ожидания ввода
    context.user_data["awaiting_pair_input"] = False
    
    # Получаем введенный пользователем текст и переводим в верхний регистр
    symbol = update.message.text.strip().upper()
    
    # Проверяем, что введенный текст - валидный символ (только буквы и цифры)
    if not re.match(r'^[A-Z0-9]+$', symbol):
        await update.message.reply_text(
            "❌ Неверный формат. Пожалуйста, введите только буквы и цифры (например, BTC, ETH)."
        )
        return
    
    # Формируем пару с USDT
    pair = f"{symbol}/USDT"
    
    # Проверяем, существует ли такая пара
    try:
        # Пытаемся получить данные для проверки существования пары
        data = await fetch_ohlcv_async(pair, "1m", 1)
        
        if data and len(data) > 0:  # Исправлено: добавлен пробел между and и len
            # Пара существует, предлагаем выбрать таймфрейм
            context.user_data["selected_pair"] = pair
            
            # Создаем клавиатуру с таймфреймами
            keyboard = []
            row = []
            for i, tf in enumerate(TIMEFRAMES):
                row.append(InlineKeyboardButton(tf, callback_data=f"timeframe_{tf}"))
                if (i + 1) % 3 == 0 or i == len(TIMEFRAMES) - 1:
                    keyboard.append(row)
                    row = []
            
            # Добавляем кнопку назад
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="analysis")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Найдена пара *{pair}*\n\n🕒 Выберите таймфрейм:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # Пара не существует
            keyboard = [[InlineKeyboardButton("🔍 Попробовать другую", callback_data="search_pair")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"❌ Пара *{pair}* не найдена или недоступна. Проверьте название и попробуйте снова.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    except Exception as e:
        logger.error(f"Ошибка при проверке пары {pair}: {e}")
        
        keyboard = [[InlineKeyboardButton("🔍 Попробовать другую", callback_data="search_pair")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"❌ Ошибка при поиске пары *{pair}*. Возможно, эта пара не поддерживается.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

def get_analysis_handlers():
    """Возвращает обработчики для функции анализа."""
    return [
        CommandHandler("analysis", analysis_command),
        CallbackQueryHandler(analysis_command, pattern="^analysis$"),  # Убедитесь, что pattern совпадает
        CallbackQueryHandler(handle_pair_selection, pattern="^pair_"),
        CallbackQueryHandler(handle_timeframe_selection, pattern="^timeframe_"),
        CallbackQueryHandler(handle_refresh_chart, pattern="^refresh_"),
        CallbackQueryHandler(handle_search_pair, pattern="^search_pair$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, handle_pair_input)
    ]
