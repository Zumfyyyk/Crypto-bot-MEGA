import logging
import os
from database.database import log_message

class DBHandler(logging.Handler):
    """Обработчик логов для записи в базу данных."""
    def emit(self, record):
        log_msg = self.format(record)  # Создаем форматированное сообщение
        log_message(record.levelname, log_msg)  # Запись логов в базу данных

def setup_logger():
    """Настройка логгера для сайта и бота."""
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Логгер для сайта
    site_logger = logging.getLogger('site_logger')
    site_handler = logging.FileHandler(os.path.join(log_dir, 'site.log'))
    site_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    site_handler.setFormatter(site_formatter)
    site_logger.addHandler(site_handler)
    site_logger.setLevel(logging.INFO)
    
    # Логгер для бота
    bot_logger = logging.getLogger('bot_logger')
    bot_handler = logging.FileHandler(os.path.join(log_dir, 'bot.log'))
    bot_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    bot_handler.setFormatter(bot_formatter)
    bot_logger.addHandler(bot_handler)
    bot_logger.setLevel(logging.INFO)
    
    return site_logger, bot_logger
