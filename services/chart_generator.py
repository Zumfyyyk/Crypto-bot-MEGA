import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import io
import base64
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from services.bybit_api import fetch_ohlcv

# Setup logger
logger = logging.getLogger('crypto_bot.chart_generator')

def convert_timestamp(timestamp_ms: int) -> datetime:
    """Convert millisecond timestamp to datetime"""
    return datetime.fromtimestamp(timestamp_ms / 1000)

async def generate_candlestick_chart(
    symbol: str, 
    timeframe: str = '1h', 
    limit: int = 50,
    title: Optional[str] = None
) -> Optional[io.BytesIO]:
    """Generate a candlestick chart for a cryptocurrency pair"""
    try:
        # Fetch OHLCV data
        ohlcv_data = await fetch_ohlcv(symbol, timeframe, limit)
        if not ohlcv_data or len(ohlcv_data) < 5:
            logger.error(f"Insufficient OHLCV data for {symbol}")
            return None
        
        # Prepare data
        timestamps = [convert_timestamp(candle[0]) for candle in ohlcv_data]
        opens = [candle[1] for candle in ohlcv_data]
        highs = [candle[2] for candle in ohlcv_data]
        lows = [candle[3] for candle in ohlcv_data]
        closes = [candle[4] for candle in ohlcv_data]
        volumes = [candle[5] for candle in ohlcv_data]
        
        # Create figure and axis
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[4, 1], 
                                      gridspec_kw={'hspace': 0.1})
        
        # Plot candlesticks
        width = 0.6
        width2 = 0.05
        
        up_candles = [i for i in range(len(closes)) if closes[i] >= opens[i]]
        down_candles = [i for i in range(len(closes)) if closes[i] < opens[i]]
        
        # Plot up candles
        ax1.bar(up_candles, [highs[i] - lows[i] for i in up_candles], width=width2, 
                bottom=lows, color='black', zorder=1)
        ax1.bar(up_candles, [closes[i] - opens[i] for i in up_candles], width=width, 
                bottom=opens, color='green', zorder=2)
        
        # Plot down candles
        ax1.bar(down_candles, [highs[i] - lows[i] for i in down_candles], width=width2, 
                bottom=lows, color='black', zorder=1)
        ax1.bar(down_candles, [closes[i] - opens[i] for i in down_candles], width=width, 
                bottom=opens, color='red', zorder=2)
        
        # Plot volume
        ax2.bar(up_candles, [volumes[i] for i in up_candles], width=width, color='green', alpha=0.5)
        ax2.bar(down_candles, [volumes[i] for i in down_candles], width=width, color='red', alpha=0.5)
        
        # Set x-axis labels to show dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.setp(ax1.get_xticklabels(), visible=False)
        
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        fig.autofmt_xdate()
        
        # Set chart title
        if title:
            chart_title = title
        else:
            chart_title = f"{symbol} - {timeframe}"
        
        ax1.set_title(chart_title)
        ax1.grid(True, alpha=0.3)
        ax2.grid(True, alpha=0.3)
        
        ax1.set_ylabel('Цена')
        ax2.set_ylabel('Объем')
        
        # Add moving averages
        if len(closes) >= 20:
            ma20 = np.convolve(closes, np.ones(20)/20, mode='valid')
            ma20_indices = range(20-1, len(closes))
            ax1.plot(ma20_indices, ma20, color='blue', linewidth=1.5, label='MA20')
            
        if len(closes) >= 50:
            ma50 = np.convolve(closes, np.ones(50)/50, mode='valid')
            ma50_indices = range(50-1, len(closes))
            ax1.plot(ma50_indices, ma50, color='orange', linewidth=1.5, label='MA50')
            
        ax1.legend()
        
        # Save figure to BytesIO buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        buffer.seek(0)
        
        return buffer
    
    except Exception as e:
        logger.error(f"Error generating candlestick chart for {symbol}: {e}")
        return None

async def generate_price_comparison_chart(symbols: List[str], timeframe: str = '1d', limit: int = 30) -> Optional[io.BytesIO]:
    """Generate a chart comparing price performance of multiple cryptocurrencies"""
    try:
        plt.figure(figsize=(12, 7))
        
        for symbol in symbols:
            ohlcv_data = await fetch_ohlcv(symbol, timeframe, limit)
            if not ohlcv_data or len(ohlcv_data) < 5:
                logger.warning(f"Insufficient data for {symbol}, skipping")
                continue
                
            # Extract closing prices and normalize to percentage change from first point
            closes = [candle[4] for candle in ohlcv_data]
            base = closes[0]
            normalized = [(price / base - 1) * 100 for price in closes]
            
            # Plot normalized prices
            plt.plot(range(len(normalized)), normalized, label=symbol.split('/')[0], linewidth=2)
        
        plt.title(f"Сравнение динамики цен ({timeframe})")
        plt.xlabel("Периоды")
        plt.ylabel("Изменение в % от начальной цены")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        
        return buffer
    
    except Exception as e:
        logger.error(f"Error generating price comparison chart: {e}")
        return None

def chart_to_base64(buffer: io.BytesIO) -> str:
    """Convert chart buffer to base64 for embedding in HTML"""
    if not buffer:
        return ""
        
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"
