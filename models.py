import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cryptography.fernet import Fernet
import base64
import logging
from database import db

# Настройка логирования
logger = logging.getLogger(__name__)

def get_encryption_key():
    """Получение ключа шифрования из переменной окружения или создание нового"""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Генерируем и сохраняем новый ключ, если его нет
        key = Fernet.generate_key().decode()
        # В продакшене следует сохранить ключ в более безопасном месте
        # или использовать системы управления секретами
        logger.warning("ENCRYPTION_KEY не найден, сгенерирован новый ключ")
    return key

class User(UserMixin, db.Model):
    """Модель пользователя системы"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    
    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Установка хешированного пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ApiKey(db.Model):
    """Модель для хранения API ключей в зашифрованном виде"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # Название для идентификации ключа
    exchange = db.Column(db.String(50), nullable=False)  # Название биржи (bybit, binance и т.д.)
    api_key_encrypted = db.Column(db.Text, nullable=False)  # Зашифрованный API ключ
    api_secret_encrypted = db.Column(db.Text, nullable=False)  # Зашифрованный API секрет
    permissions = db.Column(db.String(100), default="read")  # Права доступа (read, trade, etc)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_used = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    _cipher_suite = None
    
    @classmethod
    def get_cipher_suite(cls):
        """Получение или инициализация объекта шифрования"""
        if cls._cipher_suite is None:
            encryption_key = get_encryption_key().encode()
            if len(encryption_key) != 44:  # Проверка длины ключа Fernet
                # Дополняем ключ до требуемой длины с помощью base64
                padding = 44 - len(encryption_key)
                if padding > 0:
                    encryption_key += b'=' * padding
            try:
                cls._cipher_suite = Fernet(encryption_key)
            except Exception as e:
                logger.error(f"Ошибка при инициализации Fernet: {e}")
                # Создаем новый ключ в случае ошибки
                cls._cipher_suite = Fernet(Fernet.generate_key())
        return cls._cipher_suite
    
    def set_api_key(self, api_key):
        """Шифрование и сохранение API ключа"""
        cipher_suite = self.get_cipher_suite()
        self.api_key_encrypted = cipher_suite.encrypt(api_key.encode()).decode()
    
    def set_api_secret(self, api_secret):
        """Шифрование и сохранение API секрета"""
        cipher_suite = self.get_cipher_suite()
        self.api_secret_encrypted = cipher_suite.encrypt(api_secret.encode()).decode()
    
    def get_api_key(self):
        """Расшифровка и получение API ключа"""
        try:
            cipher_suite = self.get_cipher_suite()
            return cipher_suite.decrypt(self.api_key_encrypted.encode()).decode()
        except Exception as e:
            logger.error(f"Ошибка при расшифровке API ключа: {e}")
            return None
    
    def get_api_secret(self):
        """Расшифровка и получение API секрета"""
        try:
            cipher_suite = self.get_cipher_suite()
            return cipher_suite.decrypt(self.api_secret_encrypted.encode()).decode()
        except Exception as e:
            logger.error(f"Ошибка при расшифровке API секрета: {e}")
            return None
    
    def update_last_used(self):
        """Обновление времени последнего использования ключа"""
        self.last_used = datetime.now()
        db.session.commit()
    
    def __repr__(self):
        return f'<ApiKey {self.name} ({self.exchange})>'


class Log(db.Model):
    """Модель для хранения логов системы"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10), nullable=False)  # INFO, ERROR, etc.
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    source = db.Column(db.String(50), nullable=True)  # Источник лога (бот, админ-панель, etc)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Кто вызвал событие
    
    def __repr__(self):
        return f'<Log {self.level}: {self.message[:50]}>'


class SupportMessage(db.Model):
    """Модель для хранения сообщений поддержки"""
    __tablename__ = 'support_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # ID пользователя Telegram
    username = db.Column(db.String(100), nullable=True)  # Username пользователя Telegram
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<SupportMessage {self.id}: {self.message[:50]}>'


class Setting(db.Model):
    """Модель для хранения настроек системы"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # Категория настройки
    description = db.Column(db.String(255), nullable=True)  # Описание настройки
    is_encrypted = db.Column(db.Boolean, default=False)  # Флаг, указывающий, зашифровано ли значение
    
    _cipher_suite = None
    
    @classmethod
    def get_cipher_suite(cls):
        """Получение или инициализация объекта шифрования"""
        if cls._cipher_suite is None:
            encryption_key = get_encryption_key().encode()
            if len(encryption_key) != 44:  # Проверка длины ключа Fernet
                padding = 44 - len(encryption_key)
                if padding > 0:
                    encryption_key += b'=' * padding
            cls._cipher_suite = Fernet(encryption_key)
        return cls._cipher_suite
    
    def set_value(self, value, encrypt=False):
        """Установка значения настройки, с возможностью шифрования"""
        if encrypt:
            cipher_suite = self.get_cipher_suite()
            self.value = cipher_suite.encrypt(value.encode()).decode()
            self.is_encrypted = True
        else:
            self.value = value
            self.is_encrypted = False
    
    def get_value(self):
        """Получение значения настройки, с расшифровкой при необходимости"""
        if not self.is_encrypted:
            return self.value
        
        try:
            cipher_suite = self.get_cipher_suite()
            return cipher_suite.decrypt(self.value.encode()).decode()
        except Exception as e:
            logger.error(f"Ошибка при расшифровке значения настройки: {e}")
            return None
    
    def __repr__(self):
        return f'<Setting {self.key}>'


class PriceAlert(db.Model):
    """Модель для уведомлений о ценах"""
    __tablename__ = 'price_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # ID пользователя Telegram
    symbol = db.Column(db.String(20), nullable=False)  # Символ криптовалюты (BTC, ETH, etc)
    price = db.Column(db.Float, nullable=False)  # Целевая цена
    condition = db.Column(db.String(10), nullable=False)  # Условие (above, below)
    is_triggered = db.Column(db.Boolean, default=False)  # Было ли уведомление отправлено
    created_at = db.Column(db.DateTime, default=datetime.now)
    triggered_at = db.Column(db.DateTime, nullable=True)  # Когда было отправлено
    
    def __repr__(self):
        return f'<PriceAlert {self.symbol} {self.condition} {self.price}>'


class TradingSignal(db.Model):
    """Модель для торговых сигналов"""
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)  # Символ криптовалюты
    timeframe = db.Column(db.String(10), nullable=False)  # Таймфрейм (1h, 4h, 1d, etc)
    signal_type = db.Column(db.String(20), nullable=False)  # Тип сигнала (buy, sell, hold)
    price = db.Column(db.Float, nullable=False)  # Цена в момент сигнала
    confidence = db.Column(db.Float, nullable=True)  # Уверенность в сигнале (0-1)
    indicators = db.Column(db.Text, nullable=True)  # JSON с показателями индикаторов
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_sent = db.Column(db.Boolean, default=False)  # Был ли сигнал отправлен пользователям
    
    def __repr__(self):
        return f'<TradingSignal {self.symbol} {self.timeframe} {self.signal_type}>'