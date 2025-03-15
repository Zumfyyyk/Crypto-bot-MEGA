/**
 * Управление темой и анимациями интерфейса
 */

// Функция для переключения темы
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Сохраняем выбор темы в localStorage
    localStorage.setItem('theme', newTheme);
    
    // Применяем тему к документу
    applyTheme(newTheme);
    
    // Обновляем иконку переключателя темы
    updateThemeToggleIcon(newTheme);
}

// Функция для применения темы
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

// Функция для обновления иконки переключателя темы
function updateThemeToggleIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Если светлая тема, показываем иконку луны (для переключения на темную)
        // Если темная тема, показываем иконку солнца (для переключения на светлую)
        themeToggle.innerHTML = theme === 'light' 
            ? '<i class="fas fa-moon"></i>' 
            : '<i class="fas fa-sun"></i>';
    }
}

// Функция для инициализации мобильного меню
function initMobileMenu() {
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarNav = document.getElementById('navbar-nav');
    
    if (navbarToggle && navbarNav) {
        navbarToggle.addEventListener('click', function() {
            navbarNav.classList.toggle('active');
        });
    }
}

// Функция для инициализации анимаций
function initAnimations() {
    // Анимации для карточек при прокрутке
    const animateElements = document.querySelectorAll('.card, .stat-card');
    
    // Опции для Intersection Observer
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    // Обработчик для Intersection Observer
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, options);
    
    // Добавляем наблюдение за элементами
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Применяем сохраненную тему или темную тему по умолчанию
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    updateThemeToggleIcon(savedTheme);
    
    // Инициализируем мобильное меню
    initMobileMenu();
    
    // Добавляем обработчик для кнопки переключения темы
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Инициализируем анимации
    initAnimations();
});