document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const botStatusElement = document.getElementById('botStatus');
    const toggleBotButton = document.getElementById('toggleBotButton');
    const toggleInfoButton = document.getElementById('toggleInfoButton');
    const closeInfoButton = document.getElementById('closeInfoButton');
    const infoContainer = document.getElementById('infoContainer');
    
    // Инициализация состояния
    let botRunning = false;
    
    // Проверка статуса бота при загрузке страницы
    checkBotStatus();
    
    // Настройка кнопки переключения бота
    if (toggleBotButton) {
        toggleBotButton.addEventListener('click', toggleBot);
    }
    
    // Настройка кнопок для информационного блока
    if (toggleInfoButton) {
        toggleInfoButton.addEventListener('click', function() {
            infoContainer.style.display = 'block';
            toggleInfoButton.style.display = 'none';
        });
    }
    
    if (closeInfoButton) {
        closeInfoButton.addEventListener('click', function() {
            infoContainer.style.display = 'none';
            toggleInfoButton.style.display = 'block';
        });
    }
    
    // Функция для проверки статуса бота
    function checkBotStatus() {
        fetch('/bot_status')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'error') {
                    console.error('Ошибка в API:', data.message);
                    updateBotStatusText('Ошибка: ' + data.message);
                    return;
                }
                updateBotUI(data.status === 'running');
            })
            .catch(error => {
                console.error('Ошибка при проверке статуса бота:', error);
                updateBotStatusText('Ошибка при проверке статуса');
            });
    }
    
    // Функция для переключения состояния бота
    function toggleBot() {
        const endpoint = botRunning ? '/stop_bot' : '/start_bot';
        
        // Обновляем UI для отображения процесса
        toggleBotButton.disabled = true;
        updateBotStatusText(botRunning ? 'Останавливаем бота...' : 'Запускаем бота...');
        
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                console.error('Ошибка в API:', data.message);
                updateBotStatusText('Ошибка: ' + data.message);
                toggleBotButton.disabled = false;
                return;
            }
            botRunning = data.status === 'running';
            updateBotUI(botRunning);
            
            // Проверяем статус бота через 2 секунды для подтверждения
            setTimeout(checkBotStatus, 2000);
        })
        .catch(error => {
            console.error('Ошибка при переключении состояния бота:', error);
            updateBotStatusText('Ошибка: ' + error.message);
            toggleBotButton.disabled = false;
        });
    }
    
    // Функция для обновления текста статуса бота
    function updateBotStatusText(text) {
        if (botStatusElement) {
            botStatusElement.textContent = 'Статус бота: ' + text;
        }
    }
    
    // Функция для обновления UI в зависимости от состояния бота
    function updateBotUI(isRunning) {
        botRunning = isRunning;
        
        if (toggleBotButton) {
            toggleBotButton.textContent = botRunning ? 'Остановить бота' : 'Запустить бота';
            toggleBotButton.classList.toggle('stop', botRunning);
            toggleBotButton.disabled = false;
        }
        
        if (botStatusElement) {
            updateBotStatusText(botRunning ? 'работает' : 'остановлен');
            botStatusElement.style.color = botRunning ? '#2ecc71' : '#e74c3c';
        }
    }
    
    // Периодическая проверка статуса бота
    setInterval(checkBotStatus, 10000); // Проверяем каждые 10 секунд

    // Функция для отправки запроса на проверку API-ключа
    function testApiKey(keyId) {
        fetch(`/test_api_key/${keyId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('API ключ успешно проверен и активирован.');
            } else {
                alert(`Ошибка проверки API ключа: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при проверке API ключа.');
        });
    }
});
