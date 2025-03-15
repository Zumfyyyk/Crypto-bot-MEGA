import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Использование неинтерактивного бэкенда
from io import BytesIO
from services.bybit_api import fetch_ohlcv_async
import logging
import numpy as np

logger = logging.getLogger(__name__)

async def generate_chart(symbol: str, timeframe: str, limit: int = 30, data=None):
    """Генерация графика свечей для криптовалюты."""
    try:
        if not data:
            data = await fetch_ohlcv_async(symbol, timeframe, limit=limit)
            if not data or len(data) < 2:
                logger.error(f"Недостаточно данных для построения графика {symbol}")
                return None
        
        # Создаем фигуру подходящего размера
        plt.figure(figsize=(12, 6))
        
        # Конвертируем временные метки и извлекаем OHLC данные
        times = [datetime.datetime.fromtimestamp(candle[0] / 1000) for candle in data]
        opens = np.array([float(candle[1]) for candle in data])
        highs = np.array([float(candle[2]) for candle in data])
        lows = np.array([float(candle[3]) for candle in data])
        closes = np.array([float(candle[4]) for candle in data])
        
        # Определяем цвета свечей
        colors = ['green' if close >= open else 'red' for open, close in zip(opens, closes)]
        
        # Рисуем свечи
        for i in range(len(data)):
            # Фитиль (высокая-низкая цена)
            plt.plot([times[i], times[i]], [lows[i], highs[i]], color='black', linewidth=1)
            
            # Тело свечи (открытие-закрытие)
            if closes[i] >= opens[i]:
                # Бычья свеча (зеленая)
                rect_bottom = opens[i]
                rect_height = closes[i] - opens[i]
            else:
                # Медвежья свеча (красная)
                rect_bottom = closes[i]
                rect_height = opens[i] - closes[i]
            
            # Для более широких свечей на графике
            width = 0.7 * (times[1] - times[0]).total_seconds() / 86400 if i < len(data) - 1 else 0.7
            plt.bar(times[i], rect_height, bottom=rect_bottom, color=colors[i], width=width, alpha=0.8)
        
        # Добавляем скользящую среднюю (MA-20)
        if len(closes) >= 20:
            ma_20 = np.convolve(closes, np.ones(20)/20, mode='valid')
            plt.plot(times[19:], ma_20, color='blue', linestyle='-', linewidth=1.5, label='MA-20')

        # Добавляем индикаторы RSI и Bollinger Bands
        if len(closes) >= 14:
            rsi = calculate_rsi(closes, 14)
            plt.plot(times[-len(rsi):], rsi, color='purple', linestyle='--', label='RSI (14)')
        
        if len(closes) >= 20:
            upper_band, lower_band = calculate_bollinger_bands(closes, 20)
            plt.fill_between(times[-len(upper_band):], upper_band, lower_band, color='gray', alpha=0.2, label='Bollinger Bands')
        
        # Добавляем заголовок и сетку
        plt.title(f"{symbol} - {timeframe}")
        plt.xlabel('Время')
        plt.ylabel('Цена')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()  # Автоматическая подгонка элементов
        
        # Сохраняем в буфер
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        
        logger.info(f"График успешно создан для {symbol}, таймфрейм {timeframe}")
        return buffer
    except Exception as e:
        logger.error(f"Ошибка при создании графика для {symbol}: {e}")
        return None

async def generate_market_overview_chart(market_data):
    """Генерация сводного графика рынка (топ-5 по объему)."""
    try:
        if not market_data or len(market_data) == 0:
            logger.error("Нет данных для создания обзорного графика рынка")
            return None
        
        # Создаем фигуру
        plt.figure(figsize=(14, 8))
        
        # Подготавливаем данные для графика
        symbols = [data['symbol'].split('/')[0] for data in market_data]  # Берем только базовую валюту
        changes = [data['percentage'] * 100 if 'percentage' in data else 0 for data in market_data]  # В процентах
        
        # Цвета в зависимости от изменения
        colors = ['green' if change >= 0 else 'red' for change in changes]
        
        # Создаем горизонтальную столбчатую диаграмму
        plt.barh(symbols, changes, color=colors, alpha=0.7)
        
        # Добавляем значения к столбцам
        for i, v in enumerate(changes):
            plt.text(v + 0.1, i, f"{v:.2f}%", va='center')
        
        # Добавляем заголовок и сетку
        plt.title("Обзор изменений на рынке криптовалют (последние 24ч)")
        plt.xlabel('Изменение цены (%)')
        plt.ylabel('Криптовалюты')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.5)  # Линия на нуле
        plt.grid(True, axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Сохраняем в буфер
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        
        logger.info("Обзорный график рынка успешно создан")
        return buffer
    except Exception as e:
        logger.error(f"Ошибка при создании обзорного графика рынка: {e}")
        return None

def calculate_rsi(closes, period=14):
    """Расчет индикатора RSI."""
    # ...реализация...

def calculate_macd(closes, short_period=12, long_period=26, signal_period=9):
    """Расчет индикатора MACD."""
    # ...реализация...

def calculate_bollinger_bands(closes, period=20, std_dev=2):
    """Расчет полос Боллинджера."""
    # ...реализация...

def calculate_kdj(highs, lows, closes, period=14):
    """Расчет индикатора KDJ."""
    # ...реализация...
