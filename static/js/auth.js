/**
 * Authentication related JavaScript for Crypto Bot Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize login form
    initLoginForm();
    
    // Initialize animation effects
    initAnimations();
});

/**
 * Initialize login form validation and submission
 */
function initLoginForm() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            // Only prevent default if we need to validate
            if (!validateLoginForm()) {
                event.preventDefault();
            } else {
                // Add loading state
                const submitButton = loginForm.querySelector('button[type="submit"]');
                submitButton.innerHTML = '<span class="spinner"></span> Вход...';
                submitButton.disabled = true;
            }
        });
    }
    
    /**
     * Validate the login form
     * @returns {boolean} Whether the form is valid
     */
    function validateLoginForm() {
        const username = document.getElementById('username');
        const password = document.getElementById('password');
        let isValid = true;
        
        // Reset previous errors
        clearErrors();
        
        // Validate username
        if (!username.value.trim()) {
            showError(username, 'Имя пользователя обязательно');
            isValid = false;
        }
        
        // Validate password
        if (!password.value.trim()) {
            showError(password, 'Пароль обязателен');
            isValid = false;
        }
        
        return isValid;
    }
    
    /**
     * Show an error message for a form field
     */
    function showError(inputElement, message) {
        const formGroup = inputElement.closest('.form-group');
        const errorElement = document.createElement('div');
        
        errorElement.className = 'form-error';
        errorElement.textContent = message;
        
        formGroup.classList.add('has-error');
        formGroup.appendChild(errorElement);
        
        // Focus the first field with an error
        if (!document.querySelector('.form-group.has-error input:focus')) {
            inputElement.focus();
        }
    }
    
    /**
     * Clear all error messages
     */
    function clearErrors() {
        const errorElements = document.querySelectorAll('.form-error');
        const errorGroups = document.querySelectorAll('.form-group.has-error');
        
        errorElements.forEach(function(element) {
            element.remove();
        });
        
        errorGroups.forEach(function(group) {
            group.classList.remove('has-error');
        });
    }
}

/**
 * Initialize animations for the login page
 */
function initAnimations() {
    // Add animation class to auth card after a short delay
    const authCard = document.querySelector('.auth-card');
    
    if (authCard) {
        setTimeout(function() {
            authCard.classList.add('animate-in');
        }, 100);
    }
    
    // Add subtle floating animation to logo
    const authLogo = document.querySelector('.auth-logo');
    
    if (authLogo) {
        authLogo.classList.add('floating');
    }
    
    // Add animation when form submitted
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            if (authCard) {
                authCard.classList.add('submitting');
            }
        });
    }
}

/**
 * Fade out login page during form submission
 */
function fadeOutLoginPage() {
    const authWrapper = document.querySelector('.auth-wrapper');
    
    if (authWrapper) {
        authWrapper.classList.add('fade-out');
    }
    
    return true; // Allow form submission to continue
}
