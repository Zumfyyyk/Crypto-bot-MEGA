import logging
import asyncio
import threading
from telegram.ext import ApplicationBuilder, CallbackQueryHandler  # Убедитесь, что CallbackQueryHandler импортирован
from telegram import ReplyKeyboardMarkup  # Add import for ReplyKeyboardMarkup
from flask import Flask, render_template, request, redirect, url_for, jsonify
from handlers.start import get_start_handler
from handlers.analysis import get_analysis_handlers
from handlers.support import get_support_handler
from handlers.market import get_market_handler
from handlers.donate import get_donate_handler
from handlers.info import get_info_handler
from handlers.sentiment import get_sentiment_handler
from handlers.back import get_back_handler
from handlers.callback_handler import handle_callback
from database.database import create_tables, get_logs, get_support_messages, respond_to_support_message, get_support_message_by_id
from config.config import TELEGRAM_TOKEN as TOKEN
from logger import setup_logger
import nest_asyncio
from telegram.error import Conflict  # Добавьте импорт для обработки исключения

# Настройка логгера
site_logger, bot_logger = setup_logger()

# Настройка базового логирования
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Token: {TOKEN}")

create_tables()

app = Flask(__name__)
app.telegram_context = None
bot_running = False  # Флаг для отслеживания статуса бота
bot_application = None  # Хранение экземпляра Application

# Define custom keyboard layouts
main_menu = [
    ["📊 Анализ", "Рынок"],
    ["Сентимент", "Информация"],
    ["Поддержка", "Донат"]
]
back_button = [["Назад"]]

def get_main_menu():
    return ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

def get_back_button():
    return ReplyKeyboardMarkup(back_button, resize_keyboard=True)

async def respond_to_user(user_id, response):
    """Отправляет ответ пользователю через Telegram."""
    if app.telegram_context:
        try:
            await app.telegram_context.bot.send_message(chat_id=user_id, text=response)
            bot_logger.info(f"Ответ отправлен пользователю {user_id}")
        except Exception as e:
            bot_logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")

async def run_bot():
    """Запускает Telegram бота."""
    global bot_application, bot_running
    
    # Проверяем наличие токена
    if not TOKEN or TOKEN.strip() == "":
        error_msg = "Токен Telegram не указан. Бот не может быть запущен."
        bot_logger.critical(error_msg)
        bot_running = False
        raise ValueError(error_msg)
    
    bot_logger.info(f"Используемый токен Telegram: {TOKEN[:10]}...")  # Логируем первые символы токена для проверки
    
    try:
        # Инициализируем бота с улучшенными настройками
        application = ApplicationBuilder().token(TOKEN).http_version("1.1").get_updates_http_version("1.1").build()
        app.telegram_context = application
        bot_application = application  # Сохраняем экземпляр приложения
        bot_logger.info("Приложение Telegram создано успешно.")
        
        # Устанавливаем команды бота для отображения в интерфейсе
        try:
            await application.bot.set_my_commands([])  # Clear default commands
            bot_logger.info("Команды меню бота очищены")
        except Exception as e:
            bot_logger.error(f"Не удалось очистить команды меню: {e}")
        
        # Добавляем обработчики команд
        for handler in get_start_handler():  # Исправлено: добавляем обработчики из списка
            application.add_handler(handler)
        
        for handler in get_analysis_handlers():
            application.add_handler(handler)
        
        application.add_handler(get_support_handler())
        application.add_handler(get_market_handler())
        application.add_handler(get_donate_handler())
        application.add_handler(get_info_handler())
        application.add_handler(get_sentiment_handler())
        application.add_handler(get_back_handler())
        application.add_handler(CallbackQueryHandler(handle_callback))
    
        bot_logger.info("Бот запущен. Нажми CTRL+C для остановки.")
        
        # Запускаем бота с настройкой повторных попыток
        await application.run_polling(
            allowed_updates=["message", "callback_query", "inline_query"],
            drop_pending_updates=True,
            close_loop=False
        )
    except Conflict as e:
        bot_running = False
        bot_logger.error(f"Конфликт: {str(e)}. Убедитесь, что запущен только один экземпляр бота.")
    except Exception as e:
        bot_running = False
        bot_logger.error(f"Ошибка при запуске бота: {str(e)}")
        raise
    finally:
        bot_logger.info("Бот остановлен.")

def main():
    """Основная функция для запуска бота."""
    try:
        # Применяем nest_asyncio для работы asyncio в синхронном окружении Flask
        nest_asyncio.apply()
        
        # Инициализируем новый цикл событий
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Устанавливаем флаг запуска
        global bot_running
        bot_running = True
        
        try:
            # Запускаем бота
            bot_logger.info("Запуск бота...")
            loop.run_until_complete(run_bot())
        except KeyboardInterrupt:
            bot_logger.info("Получен сигнал прерывания. Останавливаем бота...")
        except Exception as e:
            bot_logger.error(f"Произошла ошибка при работе бота: {str(e)}")
            # Если бот остановился из-за ошибки, сбрасываем флаг запуска
            bot_running = False
        finally:
            # Очищаем ресурсы
            loop.close()
            bot_logger.info("Цикл событий asyncio закрыт")
    except Exception as e:
        bot_logger.critical(f"Критическая ошибка в главной функции: {str(e)}")
        # Сбрасываем флаг запуска при критической ошибке
        bot_running = False

if __name__ == "__main__":
    main()
