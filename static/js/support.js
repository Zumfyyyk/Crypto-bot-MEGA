document.addEventListener('DOMContentLoaded', function() {
    // Функция для загрузки сообщений поддержки
    function loadSupportMessages() {
        fetch('/support_messages')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка при загрузке сообщений');
                }
                return response.json();
            })
            .then(data => {
                displayMessages(data);
            })
            .catch(error => {
                console.error('Ошибка:', error);
                showError('Не удалось загрузить сообщения. Попробуйте обновить страницу.');
            });
    }

    // Функция для отображения сообщений
    function displayMessages(messages) {
        const messagesContainer = document.getElementById('messages');
        if (!messagesContainer) return;

        // Очищаем контейнер
        messagesContainer.innerHTML = '';

        if (messages.length === 0) {
            messagesContainer.innerHTML = '<div class="no-messages">Нет сообщений в поддержку</div>';
            return;
        }

        // Создаем элементы для каждого сообщения
        messages.forEach(message => {
            const messageItem = document.createElement('div');
            messageItem.className = 'message-item';

            const messageHeader = document.createElement('h3');
            messageHeader.textContent = `Сообщение от пользователя ID: ${message.user_id}`;
            
            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = message.message;
            
            const messageInfo = document.createElement('div');
            messageInfo.className = 'message-info';
            messageInfo.textContent = `Отправлено: ${new Date(message.timestamp).toLocaleString()}`;
            
            const responseForm = document.createElement('form');
            responseForm.className = 'response-form';
            responseForm.action = '/respond';
            responseForm.method = 'POST';
            
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'message_id';
            hiddenInput.value = message.id;
            
            const textarea = document.createElement('textarea');
            textarea.name = 'response';
            textarea.placeholder = 'Введите ваш ответ...';
            textarea.required = true;
            
            if (message.response) {
                textarea.value = message.response;
                textarea.disabled = true;
            }
            
            const submitButton = document.createElement('button');
            submitButton.type = 'submit';
            submitButton.textContent = message.response ? 'Ответ отправлен' : 'Отправить ответ';
            submitButton.disabled = !!message.response;
            
            responseForm.appendChild(hiddenInput);
            responseForm.appendChild(textarea);
            responseForm.appendChild(submitButton);
            
            messageItem.appendChild(messageHeader);
            messageItem.appendChild(messageText);
            messageItem.appendChild(messageInfo);
            
            if (message.response) {
                const responseText = document.createElement('div');
                responseText.className = 'response-text';
                responseText.innerHTML = `<strong>Ваш ответ:</strong> ${message.response}`;
                messageItem.appendChild(responseText);
            }
            
            messageItem.appendChild(responseForm);
            messagesContainer.appendChild(messageItem);
        });
    }

    // Функция для отображения ошибок
    function showError(message) {
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }

    // Загружаем сообщения поддержки при загрузке страницы
    loadSupportMessages();

    // Добавляем стили для отображения сообщений
    const style = document.createElement('style');
    style.textContent = `
        .no-messages {
            text-align: center;
            padding: 30px;
            color: #777;
            font-style: italic;
        }
        
        .error-message {
            text-align: center;
            padding: 20px;
            color: #e74c3c;
            background-color: #ffebee;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .message-item {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            padding: 20px;
        }
        
        .message-text {
            margin: 15px 0;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 8px;
        }
        
        .response-text {
            margin: 15px 0;
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 8px;
        }
    `;
    document.head.appendChild(style);
});
