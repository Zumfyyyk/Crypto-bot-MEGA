import ccxt.async_support as ccxt
import logging
import asyncio
from config.config import BYBIT_API_KEY, BYBIT_SECRET
from typing import Optional, List, Dict, Any
import time
import os

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BybitAPI:
    def __init__(self):
        """Инициализация соединения с Bybit API."""
        if not BYBIT_API_KEY or not BYBIT_SECRET:
            logger.warning("API-ключи Bybit не указаны или недействительны. Работаем в режиме без аутентификации.")
        
        # В режиме без аутентификации
        self.exchange = ccxt.bybit({
            'apiKey': BYBIT_API_KEY if BYBIT_API_KEY else None,
            'secret': BYBIT_SECRET if BYBIT_SECRET else None,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self._markets = None
        self._last_market_update = 0
        self._market_update_interval = 60 * 5  # 5 минут

    async def get_markets(self, force_update=False) -> Optional[Dict[str, Any]]:
        """Получение списка доступных рынков с кэшированием."""
        current_time = time.time()
        if (not self._markets or 
            force_update or 
            current_time - self._last_market_update > self._market_update_interval):
            try:
                self._markets = await self.exchange.load_markets()
                self._last_market_update = current_time
                logger.info("Список рынков обновлён")
            except Exception as e:
                logger.error(f"Ошибка при загрузке рынков: {e}")
                if not self._markets:  # Возвращаем None только если нет кэшированных данных
                    return None
        return self._markets

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1m', 
                          limit: int = 100, retries: int = 3) -> Optional[List]:
        """Получение OHLCV данных с повторными попытками при ошибке."""
        for attempt in range(retries):
            try:
                await self.exchange.load_markets()
                data = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                logger.info(f"Получены данные OHLCV для {symbol}, таймфрейм {timeframe}")
                return data
            except ccxt.RequestTimeout:
                logger.warning(f"Таймаут при получении OHLCV для {symbol}, попытка {attempt+1}/{retries}")
                if attempt == retries - 1:
                    logger.error(f"Превышено максимальное количество попыток для {symbol}")
                    return None
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка при получении OHLCV для {symbol}: {e}")
                return None

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Получение текущих данных тикера для указанного символа."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            logger.info(f"Получены данные тикера для {symbol}")
            return ticker
        except Exception as e:
            logger.error(f"Ошибка при получении тикера для {symbol}: {e}")
            return None

    async def fetch_market_info(self, symbol: str) -> Optional[Dict]:
        """Получение информации о рынке для указанного символа."""
        try:
            markets = await self.get_markets()
            if not markets or symbol not in markets:
                logger.error(f"Рынок {symbol} не найден")
                return None
            return markets[symbol]
        except Exception as e:
            logger.error(f"Ошибка при получении информации о рынке {symbol}: {e}")
            return None

    async def close(self):
        """Безопасное закрытие соединения с биржей."""
        try:
            await self.exchange.close()
            logger.info("Соединение с Bybit закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с биржей: {e}")

# Создание singleton-экземпляра
bybit_api = BybitAPI()

async def fetch_market_sentiment():
    """Получение общего настроения рынка."""
    try:
        # В реальном приложении здесь будет анализ данных
        # Для примера возвращаем заглушку
        sentiment = "Нейтральное настроение рынка"
        return sentiment
    except Exception as e:
        logger.error(f"Ошибка при получении настроения рынка: {e}")
        return "Данные о настроении рынка временно недоступны"

async def fetch_top_gainers(limit=5):
    """Получение списка топовых растущих активов."""
    try:
        markets = await bybit_api.get_markets()
        if not markets:
            logger.warning("Не удалось получить данные о рынках. Возвращаем пример данных.")
            # Возвращаем пример данных, когда API недоступно
            return [
                {"symbol": "BTC/USDT", "last": 67000, "percentage": 2.5},
                {"symbol": "ETH/USDT", "last": 3500, "percentage": 1.8},
                {"symbol": "XRP/USDT", "last": 0.52, "percentage": 1.2},
                {"symbol": "SOL/USDT", "last": 120, "percentage": 0.9},
                {"symbol": "ADA/USDT", "last": 0.45, "percentage": 0.7}
            ][:limit]
        
        # Получаем данные тикеров для основных криптовалют
        tickers = []
        symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol][:20]  # Ограничиваем для производительности
        
        for symbol in symbols:
            ticker = await bybit_api.fetch_ticker(symbol)
            if ticker:
                tickers.append(ticker)
        
        # Если не получили ни одного тикера, вернем пример данных
        if not tickers:
            logger.warning("Не удалось получить данные тикеров. Возвращаем пример данных.")
            return [
                {"symbol": "BTC/USDT", "last": 67000, "percentage": 2.5},
                {"symbol": "ETH/USDT", "last": 3500, "percentage": 1.8},
                {"symbol": "XRP/USDT", "last": 0.52, "percentage": 1.2},
                {"symbol": "SOL/USDT", "last": 120, "percentage": 0.9},
                {"symbol": "ADA/USDT", "last": 0.45, "percentage": 0.7}
            ][:limit]
        
        # Сортируем по проценту изменения
        tickers.sort(key=lambda x: x['percentage'] if 'percentage' in x else 0, reverse=True)
        return tickers[:limit]
    except Exception as e:
        logger.error(f"Ошибка при получении топовых растущих активов: {e}")
        return [
            {"symbol": "BTC/USDT", "last": 67000, "percentage": 2.5},
            {"symbol": "ETH/USDT", "last": 3500, "percentage": 1.8},
            {"symbol": "XRP/USDT", "last": 0.52, "percentage": 1.2},
            {"symbol": "SOL/USDT", "last": 120, "percentage": 0.9},
            {"symbol": "ADA/USDT", "last": 0.45, "percentage": 0.7}
        ][:limit]

async def fetch_top_losers(limit=5):
    """Получение списка топовых падающих активов."""
    try:
        markets = await bybit_api.get_markets()
        if not markets:
            logger.warning("Не удалось получить данные о рынках. Возвращаем пример данных.")
            # Возвращаем пример данных, когда API недоступно
            return [
                {"symbol": "DOGE/USDT", "last": 0.12, "percentage": -2.1},
                {"symbol": "LTC/USDT", "last": 75, "percentage": -1.8},
                {"symbol": "DOT/USDT", "last": 6.2, "percentage": -1.4},
                {"symbol": "LINK/USDT", "last": 14.2, "percentage": -1.2},
                {"symbol": "MATIC/USDT", "last": 0.65, "percentage": -0.9}
            ][:limit]
        
        # Получаем данные тикеров для основных криптовалют
        tickers = []
        symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol][:20]  # Ограничиваем для производительности
        
        for symbol in symbols:
            ticker = await bybit_api.fetch_ticker(symbol)
            if ticker:
                tickers.append(ticker)
        
        # Если не получили ни одного тикера, вернем пример данных
        if not tickers:
            logger.warning("Не удалось получить данные тикеров. Возвращаем пример данных.")
            return [
                {"symbol": "DOGE/USDT", "last": 0.12, "percentage": -2.1},
                {"symbol": "LTC/USDT", "last": 75, "percentage": -1.8},
                {"symbol": "DOT/USDT", "last": 6.2, "percentage": -1.4},
                {"symbol": "LINK/USDT", "last": 14.2, "percentage": -1.2},
                {"symbol": "MATIC/USDT", "last": 0.65, "percentage": -0.9}
            ][:limit]
        
        # Сортируем по проценту изменения
        tickers.sort(key=lambda x: x['percentage'] if 'percentage' in x else 0)
        return tickers[:limit]
    except Exception as e:
        logger.error(f"Ошибка при получении топовых падающих активов: {e}")
        return [
            {"symbol": "DOGE/USDT", "last": 0.12, "percentage": -2.1},
            {"symbol": "LTC/USDT", "last": 75, "percentage": -1.8},
            {"symbol": "DOT/USDT", "last": 6.2, "percentage": -1.4},
            {"symbol": "LINK/USDT", "last": 14.2, "percentage": -1.2},
            {"symbol": "MATIC/USDT", "last": 0.65, "percentage": -0.9}
        ][:limit]

# Методы-обертки для упрощения импорта
async def fetch_ohlcv_async(symbol: str, timeframe: str = '1m', limit: int = 100):
    """Обертка для метода fetch_ohlcv класса BybitAPI."""
    return await bybit_api.fetch_ohlcv(symbol, timeframe, limit)

async def fetch_ticker(symbol: str):
    """Обертка для метода fetch_ticker класса BybitAPI."""
    return await bybit_api.fetch_ticker(symbol)

async def fetch_markets():
    """Обертка для метода get_markets класса BybitAPI."""
    return await bybit_api.get_markets()

async def close_connection():
    """Закрытие соединения с биржей."""
    await bybit_api.close()
