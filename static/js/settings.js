document.addEventListener('DOMContentLoaded', function() {
    // Получаем все элементы формы
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const notificationsSelect = document.getElementById('notifications');
    const twoFactorAuthSelect = document.getElementById('two_factor_auth');
    
    // Кнопки сохранения настроек
    const saveProfileBtn = document.getElementById('save-profile');
    const saveNotificationsBtn = document.getElementById('save-notifications');
    const saveSecurityBtn = document.getElementById('save-security');
    const deleteAccountBtn = document.getElementById('delete-account');
    
    // Функция отображения уведомления
    function showNotification(message, isSuccess = true) {
        // Проверяем, существует ли уже уведомление
        let notification = document.querySelector('.notification');
        
        if (!notification) {
            // Создаем новый элемент уведомления
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
        }
        
        // Устанавливаем класс в зависимости от типа уведомления
        notification.className = isSuccess ? 'notification success' : 'notification error';
        notification.textContent = message;
        
        // Показываем уведомление
        notification.style.display = 'block';
        
        // Скрываем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
    
    // Обработчик сохранения профиля
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', function() {
            // Проверяем, заполнены ли поля
            if (!usernameInput.value.trim()) {
                showNotification('Пожалуйста, введите имя пользователя', false);
                return;
            }
            
            // Эмуляция отправки данных на сервер
            setTimeout(() => {
                showNotification('Профиль успешно сохранен!');
            }, 500);
        });
    }
    
    // Обработчик сохранения настроек уведомлений
    if (saveNotificationsBtn) {
        saveNotificationsBtn.addEventListener('click', function() {
            // Эмуляция отправки данных на сервер
            setTimeout(() => {
                showNotification('Настройки уведомлений сохранены!');
            }, 500);
        });
    }
    
    // Обработчик сохранения настроек безопасности
    if (saveSecurityBtn) {
        saveSecurityBtn.addEventListener('click', function() {
            // Эмуляция отправки данных на сервер
            setTimeout(() => {
                showNotification('Настройки безопасности сохранены!');
            }, 500);
        });
    }
    
    // Обработчик удаления аккаунта
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function() {
            // Показываем диалог подтверждения
            if (confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие невозможно отменить.')) {
                // Эмуляция отправки запроса на удаление
                setTimeout(() => {
                    showNotification('Аккаунт успешно удален. Перенаправление...', true);
                    // Перенаправление на страницу входа через 2 секунды
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                }, 1000);
            }
        });
    }
    
    // Добавляем стили для уведомлений
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            display: none;
            animation: slideIn 0.3s ease-out;
        }
        
        .success {
            background-color: #2ecc71;
        }
        
        .error {
            background-color: #e74c3c;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});
