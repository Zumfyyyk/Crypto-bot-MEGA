document.addEventListener('DOMContentLoaded', function() {
    // Функция для анимации исчезновения страницы логина при отправке формы
    window.fadeOutLoginPage = function() {
        const loginContainer = document.querySelector('.login-container');
        if (loginContainer) {
            loginContainer.classList.add('fade-out');
            // Небольшая задержка перед отправкой формы для завершения анимации
            setTimeout(() => {
                return true; // Продолжить отправку формы
            }, 500);
        }
        return true;
    };

    // Проверка наличия ошибки и добавление анимации встряски
    const errorMessage = document.querySelector('.error-message');
    if (errorMessage) {
        const loginContainer = document.querySelector('.login-container');
        if (loginContainer) {
            // Добавляем класс для анимации встряски
            loginContainer.classList.add('shake');
            
            // Удаляем класс через некоторое время
            setTimeout(() => {
                loginContainer.classList.remove('shake');
            }, 500);
        }
    }

    // Добавляем стиль анимации встряски для случаев с ошибкой
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);
});
