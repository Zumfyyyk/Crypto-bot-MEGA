import logging
import signal
import sys
from app import app
from logger import setup_logger

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/site.log"),
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def shutdown_handler(signal_received, frame):
    """Обрабатывает сигнал остановки (Ctrl+C)."""
    logger.info("Остановка приложения...")
    sys.exit(0)

if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Запуск приложения")
    
    # Обработка сигнала остановки
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
