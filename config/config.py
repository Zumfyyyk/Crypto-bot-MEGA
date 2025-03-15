import os

# Конфигурация администратора
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')

# Конфигурация Telegram бота
TELEGRAM_TOKEN = '7807041975:AAFK_uUXUiUfyyDPOPu5g-oUdJfor0l9rRU'
TELEGRAM_ADMIN_IDS = list(map(int, os.environ.get('TELEGRAM_ADMIN_IDS', '').split(','))) if os.environ.get('TELEGRAM_ADMIN_IDS') else []

# Конфигурация шифрования
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', '')

# Настройки API
API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))  # Запросов в минуту
API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))  # Секунд на запрос

# API ключи для бирж
BYBIT_API_KEY = os.environ.get('BYBIT_API_KEY', '')
BYBIT_SECRET = os.environ.get('BYBIT_SECRET', '')

# Настройки базы данных
DB_URI = os.environ.get('DATABASE_URL', '')

# Настройки интерфейса
UI_THEME = os.environ.get('UI_THEME', 'dark')
UI_ANIMATION = os.environ.get('UI_ANIMATION', 'enabled')
UI_COLORS = {
    'primary': '#17a2b8',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'gradient_start': '#4a00e0',
    'gradient_end': '#8e2de2'
}

# Настройки хостинга
HOSTING_ENABLED = os.environ.get('HOSTING_ENABLED', 'false').lower() == 'true'
HOSTING_TYPE = os.environ.get('HOSTING_TYPE', 'ngrok')  # Возможные значения: 'ngrok', 'github'
HOSTING_URL = os.environ.get('HOSTING_URL', '')  # URL для хостинга