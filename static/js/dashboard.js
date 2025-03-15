/**
 * Main JavaScript file for Crypto Bot Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar toggle functionality
    initSidebar();
    
    // Initialize bot status checker
    initBotStatusChecker();
    
    // Initialize bot control buttons
    initBotControls();
    
    // Initialize flash message dismissal
    initFlashMessages();
});

/**
 * Initialize sidebar toggle functionality for mobile view
 */
function initSidebar() {
    const sidebarToggler = document.querySelector('.sidebar-toggler');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggler && sidebar) {
        sidebarToggler.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && event.target !== sidebarToggler) {
                sidebar.classList.remove('open');
            }
        });
    }
}

/**
 * Initialize bot status checker - polls the API to check bot status
 */
function initBotStatusChecker() {
    const statusIndicator = document.getElementById('botStatusIndicator');
    
    if (statusIndicator) {
        // Check bot status every 5 seconds
        checkBotStatus();
        setInterval(checkBotStatus, 5000);
    }
    
    /**
     * Check bot status from API
     */
    function checkBotStatus() {
        fetch('/bot_status')
            .then(response => response.json())
            .then(data => {
                updateBotStatusUI(data.status);
            })
            .catch(error => {
                console.error('Error checking bot status:', error);
                updateBotStatusUI('error');
            });
    }
    
    /**
     * Update the UI based on bot status
     */
    function updateBotStatusUI(status) {
        if (!statusIndicator) return;
        
        // Remove all status classes
        statusIndicator.classList.remove('status-success', 'status-danger', 'status-warning');
        
        // Update text and add appropriate class
        if (status === 'running') {
            statusIndicator.textContent = 'Работает';
            statusIndicator.classList.add('status-success');
            
            // Update start/stop button state
            const startBtn = document.getElementById('startBotBtn');
            const stopBtn = document.getElementById('stopBotBtn');
            
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
        } 
        else if (status === 'stopped') {
            statusIndicator.textContent = 'Остановлен';
            statusIndicator.classList.add('status-danger');
            
            // Update start/stop button state
            const startBtn = document.getElementById('startBotBtn');
            const stopBtn = document.getElementById('stopBotBtn');
            
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        } 
        else {
            statusIndicator.textContent = 'Ошибка';
            statusIndicator.classList.add('status-warning');
        }
    }
}

/**
 * Initialize bot control buttons
 */
function initBotControls() {
    const startBotBtn = document.getElementById('startBotBtn');
    const stopBotBtn = document.getElementById('stopBotBtn');
    
    if (startBotBtn) {
        startBotBtn.addEventListener('click', function() {
            startBot();
        });
    }
    
    if (stopBotBtn) {
        stopBotBtn.addEventListener('click', function() {
            stopBot();
        });
    }
    
    /**
     * Start the bot via API
     */
    function startBot() {
        // Show loading state
        if (startBotBtn) {
            startBotBtn.disabled = true;
            startBotBtn.innerHTML = '<span class="spinner"></span> Запуск...';
        }
        
        fetch('/start_bot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (startBotBtn) {
                startBotBtn.innerHTML = 'Запустить бота';
            }
            
            if (data.status === 'running') {
                showNotification('Бот успешно запущен', 'success');
            } else {
                showNotification(data.message || 'Не удалось запустить бота', 'error');
                if (startBotBtn) startBotBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error starting bot:', error);
            showNotification('Ошибка при запуске бота', 'error');
            
            if (startBotBtn) {
                startBotBtn.disabled = false;
                startBotBtn.innerHTML = 'Запустить бота';
            }
        });
    }
    
    /**
     * Stop the bot via API
     */
    function stopBot() {
        // Show loading state
        if (stopBotBtn) {
            stopBotBtn.disabled = true;
            stopBotBtn.innerHTML = '<span class="spinner"></span> Остановка...';
        }
        
        fetch('/stop_bot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (stopBotBtn) {
                stopBotBtn.innerHTML = 'Остановить бота';
            }
            
            if (data.status === 'stopped') {
                showNotification('Бот успешно остановлен', 'success');
            } else {
                showNotification(data.message || 'Не удалось остановить бота', 'error');
                if (stopBotBtn) stopBotBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error stopping bot:', error);
            showNotification('Ошибка при остановке бота', 'error');
            
            if (stopBotBtn) {
                stopBotBtn.disabled = false;
                stopBotBtn.innerHTML = 'Остановить бота';
            }
        });
    }
}

/**
 * Initialize flash message dismissal
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(function(message) {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', function() {
            message.remove();
        });
        
        message.appendChild(closeBtn);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300); // Matches transition duration
        }, 5000);
    });
}

/**
 * Show a notification to the user
 */
function showNotification(message, type = 'info') {
    const notificationsContainer = document.getElementById('notifications');
    
    if (!notificationsContainer) {
        // Create notifications container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'notifications';
        container.className = 'notifications';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add to container
    document.getElementById('notifications').appendChild(notification);
    
    // Add event listener to close button
    notification.querySelector('.notification-close').addEventListener('click', function() {
        notification.remove();
    });
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        notification.classList.add('fade-out');
        setTimeout(function() {
            notification.remove();
        }, 300); // Matches transition duration
    }, 5000);
    
    return notification;
}
