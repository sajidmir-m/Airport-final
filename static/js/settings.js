// Settings Page JavaScript
class SettingsManager {
    constructor() {
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Dashboard settings form
        const dashboardForm = document.getElementById('dashboard-settings-form');
        if (dashboardForm) {
            dashboardForm.addEventListener('submit', this.saveDashboardSettings.bind(this));
        }

        // Load current settings into form
        this.loadFormValues();
    }

    loadSettings() {
        // Load settings from localStorage
        const settings = {
            refreshInterval: localStorage.getItem('refresh-interval') || '30',
            theme: localStorage.getItem('theme') || 'light',
            enableAnimations: localStorage.getItem('enable-animations') !== 'false',
            enableNotifications: localStorage.getItem('enable-notifications') !== 'false'
        };

        return settings;
    }

    loadFormValues() {
        const settings = this.loadSettings();

        // Set form values
        const refreshInterval = document.getElementById('refresh-interval');
        if (refreshInterval) {
            refreshInterval.value = settings.refreshInterval;
        }

        const defaultTheme = document.getElementById('default-theme');
        if (defaultTheme) {
            defaultTheme.value = settings.theme;
        }

        const enableAnimations = document.getElementById('enable-animations');
        if (enableAnimations) {
            enableAnimations.checked = settings.enableAnimations;
        }

        const enableNotifications = document.getElementById('enable-notifications');
        if (enableNotifications) {
            enableNotifications.checked = settings.enableNotifications;
        }
    }

    saveDashboardSettings(event) {
        event.preventDefault();

        // Get form values
        const refreshInterval = document.getElementById('refresh-interval').value;
        const defaultTheme = document.getElementById('default-theme').value;
        const enableAnimations = document.getElementById('enable-animations').checked;
        const enableNotifications = document.getElementById('enable-notifications').checked;

        // Save to localStorage
        localStorage.setItem('refresh-interval', refreshInterval);
        localStorage.setItem('theme', defaultTheme);
        localStorage.setItem('enable-animations', enableAnimations);
        localStorage.setItem('enable-notifications', enableNotifications);

        // Apply theme immediately if changed
        this.applyTheme(defaultTheme);

        // Show success message
        this.showNotification('Settings saved successfully!', 'success');
    }

    applyTheme(theme) {
        const body = document.body;
        const icon = document.getElementById('theme-icon');

        if (theme === 'dark') {
            body.setAttribute('data-theme', 'dark');
            if (icon) icon.className = 'fas fa-sun';
        } else if (theme === 'light') {
            body.removeAttribute('data-theme');
            if (icon) icon.className = 'fas fa-moon';
        } else if (theme === 'auto') {
            // Use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (prefersDark) {
                body.setAttribute('data-theme', 'dark');
                if (icon) icon.className = 'fas fa-sun';
            } else {
                body.removeAttribute('data-theme');
                if (icon) icon.className = 'fas fa-moon';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        
        const iconClass = {
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'danger': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';

        notification.innerHTML = `
            <i class="${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// System action functions
function performSystemAction(action) {
    const settingsManager = window.settingsManager;
    
    switch (action) {
        case 'refresh':
            settingsManager.showNotification('Refreshing all data sources...', 'info');
            // Simulate refresh action
            setTimeout(() => {
                settingsManager.showNotification('All data sources refreshed successfully!', 'success');
            }, 2000);
            break;
            
        case 'backup':
            settingsManager.showNotification('Creating system backup...', 'info');
            // Simulate backup action
            setTimeout(() => {
                settingsManager.showNotification('System backup created successfully!', 'success');
            }, 3000);
            break;
            
        case 'clear-cache':
            settingsManager.showNotification('Clearing cache...', 'info');
            // Clear localStorage cache
            const keysToKeep = ['theme', 'refresh-interval', 'enable-animations', 'enable-notifications'];
            const allKeys = Object.keys(localStorage);
            
            allKeys.forEach(key => {
                if (!keysToKeep.includes(key)) {
                    localStorage.removeItem(key);
                }
            });
            
            setTimeout(() => {
                settingsManager.showNotification('Cache cleared successfully!', 'success');
            }, 1000);
            break;
            
        default:
            settingsManager.showNotification('Unknown action', 'warning');
    }
}

function downloadLogs() {
    const settingsManager = window.settingsManager;
    
    // Generate mock log data
    const logData = generateMockLogs();
    const blob = new Blob([logData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = `airport-dashboard-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    settingsManager.showNotification('System logs downloaded successfully!', 'success');
}

function generateMockLogs() {
    const now = new Date();
    const logs = [];
    
    // Generate last 24 hours of logs
    for (let i = 0; i < 24; i++) {
        const logTime = new Date(now.getTime() - (i * 60 * 60 * 1000));
        const timeString = logTime.toISOString();
        
        logs.push(`[${timeString}] INFO: Dashboard data refreshed successfully`);
        logs.push(`[${timeString}] INFO: ${Math.floor(Math.random() * 100) + 50} passengers processed`);
        
        if (Math.random() > 0.8) {
            logs.push(`[${timeString}] WARN: Queue length exceeding normal thresholds`);
        }
        
        if (Math.random() > 0.95) {
            logs.push(`[${timeString}] ERROR: Temporary connection issue with baggage system`);
        }
    }
    
    return logs.reverse().join('\n');
}

// Test data source connection
function testDataSource(sourceName) {
    const settingsManager = window.settingsManager;
    
    settingsManager.showNotification(`Testing connection to ${sourceName}...`, 'info');
    
    // Simulate connection test
    setTimeout(() => {
        const success = Math.random() > 0.1; // 90% success rate
        
        if (success) {
            settingsManager.showNotification(`${sourceName} connection test successful!`, 'success');
        } else {
            settingsManager.showNotification(`${sourceName} connection test failed!`, 'danger');
        }
    }, 1500);
}

// Initialize settings manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.settingsManager = new SettingsManager();
    
    // Update system info periodically
    updateSystemInfo();
    setInterval(updateSystemInfo, 60000); // Update every minute
});

function updateSystemInfo() {
    // Update uptime
    const uptimeElement = document.querySelector('.system-info .info-item:nth-child(2)');
    if (uptimeElement) {
        const uptime = Math.floor(Date.now() / 1000 / 60); // Minutes since page load
        const hours = Math.floor(uptime / 60);
        const minutes = uptime % 60;
        uptimeElement.innerHTML = `<strong>Uptime:</strong> ${hours} hours ${minutes} minutes`;
    }
    
    // Update memory and CPU usage with random values
    const memoryProgress = document.querySelector('.progress .progress-bar');
    const cpuProgress = document.querySelector('.progress .progress-bar.bg-success');
    
    if (memoryProgress) {
        const memoryUsage = Math.floor(Math.random() * 20) + 60; // 60-80%
        memoryProgress.style.width = `${memoryUsage}%`;
        memoryProgress.textContent = `${memoryUsage}%`;
    }
    
    if (cpuProgress) {
        const cpuUsage = Math.floor(Math.random() * 30) + 15; // 15-45%
        cpuProgress.style.width = `${cpuUsage}%`;
        cpuProgress.textContent = `${cpuUsage}%`;
    }
}
