/**
 * Charts and visualization for Crypto Bot Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts on the page
    initCharts();
});

/**
 * Initialize all charts on the page
 */
function initCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Charts will not be rendered.');
        return;
    }
    
    // Define chart color schemes
    const chartColors = {
        primary: '#3498db',
        secondary: '#2ecc71',
        danger: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db',
        success: '#2ecc71',
        dark: '#2c3e50',
        gray: '#95a5a6',
        green: '#00C853',
        red: '#FF5252'
    };
    
    // Initialize different chart types
    initUserInteractionsChart();
    initActiveUsersChart();
    initCryptoComparisonChart();
}

/**
 * Initialize user interactions chart
 */
function initUserInteractionsChart() {
    const userInteractionsChart = document.getElementById('userInteractionsChart');
    
    if (!userInteractionsChart) return;
    
    // Example data - in a real app, this would come from the server
    const data = {
        labels: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
        datasets: [{
            label: 'Активные пользователи',
            data: [65, 59, 80, 81, 56, 55, 40],
            backgroundColor: 'rgba(52, 152, 219, 0.2)',
            borderColor: 'rgba(52, 152, 219, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(52, 152, 219, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(52, 152, 219, 1)',
            tension: 0.4
        }, {
            label: 'Новые пользователи',
            data: [28, 48, 40, 19, 86, 27, 90],
            backgroundColor: 'rgba(46, 204, 113, 0.2)',
            borderColor: 'rgba(46, 204, 113, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(46, 204, 113, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(46, 204, 113, 1)',
            tension: 0.4
        }]
    };
    
    new Chart(userInteractionsChart, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Initialize active users chart
 */
function initActiveUsersChart() {
    const activeUsersChart = document.getElementById('activeUsersChart');
    
    if (!activeUsersChart) return;
    
    // Example data - in a real app, this would come from the server
    const data = {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [{
            label: 'Активные пользователи (сегодня)',
            data: [12, 8, 15, 35, 42, 30],
            backgroundColor: 'rgba(52, 152, 219, 0.2)',
            borderColor: 'rgba(52, 152, 219, 1)',
            fill: true
        }]
    };
    
    new Chart(activeUsersChart, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize crypto comparison chart
 */
function initCryptoComparisonChart() {
    const cryptoComparisonChart = document.getElementById('cryptoComparisonChart');
    
    if (!cryptoComparisonChart) return;
    
    // Example data - in a real app, this would come from the server
    const data = {
        labels: ['1 Jan', '2 Jan', '3 Jan', '4 Jan', '5 Jan', '6 Jan', '7 Jan'],
        datasets: [{
            label: 'BTC',
            data: [42000, 41500, 43000, 44500, 45000, 43500, 44000],
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.1)',
            borderWidth: 2,
            fill: false
        }, {
            label: 'ETH',
            data: [3200, 3100, 3250, 3400, 3450, 3300, 3350],
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            borderWidth: 2,
            fill: false
        }, {
            label: 'SOL',
            data: [140, 135, 145, 155, 160, 150, 155],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2,
            fill: false
        }]
    };
    
    new Chart(cryptoComparisonChart, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Load market data chart for a specific cryptocurrency
 */
function loadMarketDataChart(symbol, timeframe, containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    // Show loading state
    container.innerHTML = '<div class="chart-loading">Загрузка данных...</div>';
    
    // Fetch data from the server
    fetch(`/api/market_data?symbol=${symbol}&timeframe=${timeframe}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = `<div class="chart-error">Ошибка: ${data.error}</div>`;
                return;
            }
            
            // Clear container and create canvas
            container.innerHTML = '';
            const canvas = document.createElement('canvas');
            container.appendChild(canvas);
            
            // Create chart
            createCandlestickChart(canvas, data, symbol, timeframe);
        })
        .catch(error => {
            console.error('Error loading market data:', error);
            container.innerHTML = '<div class="chart-error">Не удалось загрузить данные</div>';
        });
}

/**
 * Create a candlestick chart
 */
function createCandlestickChart(canvas, data, symbol, timeframe) {
    // Check if data is available
    if (!data || !data.ohlc || data.ohlc.length === 0) {
        canvas.parentNode.innerHTML = '<div class="chart-error">Нет данных для отображения</div>';
        return;
    }
    
    // Format the data for Chart.js
    const timestamps = data.ohlc.map(candle => new Date(candle[0]));
    const opens = data.ohlc.map(candle => candle[1]);
    const highs = data.ohlc.map(candle => candle[2]);
    const lows = data.ohlc.map(candle => candle[3]);
    const closes = data.ohlc.map(candle => candle[4]);
    
    // Create chart
    new Chart(canvas, {
        type: 'line', // Use line as base
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Цена',
                data: closes,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(timeframe)
                    },
                    title: {
                        display: true,
                        text: 'Время'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Цена (USDT)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `${symbol} (${timeframe})`
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            return [
                                `Открытие: ${opens[index]}`,
                                `Максимум: ${highs[index]}`,
                                `Минимум: ${lows[index]}`,
                                `Закрытие: ${closes[index]}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

/**
 * Get the appropriate time unit based on timeframe
 */
function getTimeUnit(timeframe) {
    switch(timeframe) {
        case '1m':
        case '5m':
        case '15m':
            return 'minute';
        case '30m':
        case '1h':
        case '4h':
            return 'hour';
        case '1d':
            return 'day';
        case '1w':
            return 'week';
        default:
            return 'day';
    }
}
