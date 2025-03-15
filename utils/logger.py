import logging
import os
from database.database import log_message

class DBHandler(logging.Handler):
    """Handler for sending logs to database"""
    def emit(self, record):
        log_msg = self.format(record)
        log_message(record.levelname, log_msg)

def setup_logger():
    """Configure logging for the application"""
    # Create a custom logger
    logger = logging.getLogger('crypto_bot')
    logger.setLevel(logging.DEBUG)
    
    # Check if logger already has handlers
    if not logger.hasHandlers():
        # Create handlers
        c_handler = logging.StreamHandler()  # Console handler
        c_handler.setLevel(logging.INFO)
        
        # Ensure logs directory exists
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler
        log_file = os.path.join(logs_dir, 'bot.log')
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        # Add database handler
        try:
            db_handler = DBHandler()
            db_handler.setLevel(logging.INFO)
            db_handler.setFormatter(formatter)
            logger.addHandler(db_handler)
        except Exception as e:
            logger.error(f"Unable to initialize database handler: {e}")
    
    return logger
