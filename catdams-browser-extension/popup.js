// ====== CATDAMS Popup Controller ======
// Handles UI interactions and configuration management

class CATDAMSPopupController {
    constructor() {
        this.startTime = Date.now();
        this.stats = {
            messagesProcessed: 0,
            threatsDetected: 0,
            sessionsActive: 0,
            errors: 0
        };
        
        this.initialize();
    }

    async initialize() {
        try {
            this.setupEventListeners();
            await this.loadConfiguration();
            await this.updateStats();
            this.startStatusUpdates();
            
            console.log('[CATDAMS Popup] Initialized successfully');
        } catch (error) {
            console.error('[CATDAMS Popup] Initialization error:', error);
        }
    }

    setupEventListeners() {
        // Toggle switches
        document.getElementById('threatDetectionToggle').addEventListener('click', () => {
            this.toggleSetting('threatDetection.enabled');
        });
        
        document.getElementById('realtimeToggle').addEventListener('click', () => {
            this.toggleSetting('threatDetection.realTime');
        });
        
        document.getElementById('logStorageToggle').addEventListener('click', () => {
            this.toggleSetting('errorHandling.logToStorage');
        });
        
        document.getElementById('circuitBreakerToggle').addEventListener('click', () => {
            this.toggleSetting('backend.circuitBreaker.enabled');
        });

        // Log level buttons
        document.querySelectorAll('.log-level button').forEach(button => {
            button.addEventListener('click', () => {
                this.setLogLevel(button.dataset.level);
            });
        });

        // Action buttons
        document.getElementById('clearLogsBtn').addEventListener('click', () => {
            this.clearLogs();
        });
        
        document.getElementById('exportLogsBtn').addEventListener('click', () => {
            this.exportLogs();
        });
        
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshStats();
        });
    }

    async loadConfiguration() {
        try {
            const result = await chrome.storage.local.get(['catdams_config']);
            const config = result.catdams_config || {};
            
            // Update toggle states
            this.updateToggle('threatDetectionToggle', config.threatDetection?.enabled !== false);
            this.updateToggle('realtimeToggle', config.threatDetection?.realTime !== false);
            this.updateToggle('logStorageToggle', config.errorHandling?.logToStorage !== false);
            this.updateToggle('circuitBreakerToggle', config.backend?.circuitBreaker?.enabled !== false);
            
            // Update log level
            const logLevel = config.errorHandling?.logLevel || 'info';
            this.updateLogLevel(logLevel);
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to load configuration:', error);
        }
    }

    updateToggle(elementId, isActive) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.toggle('active', isActive);
        }
    }

    updateLogLevel(level) {
        document.querySelectorAll('.log-level button').forEach(button => {
            button.classList.toggle('active', button.dataset.level === level);
        });
    }

    async toggleSetting(settingPath) {
        try {
            const result = await chrome.storage.local.get(['catdams_config']);
            const config = result.catdams_config || {};
            
            // Navigate to the setting and toggle it
            const keys = settingPath.split('.');
            let current = config;
            for (let i = 0; i < keys.length - 1; i++) {
                if (!(keys[i] in current)) {
                    current[keys[i]] = {};
                }
                current = current[keys[i]];
            }
            
            const lastKey = keys[keys.length - 1];
            current[lastKey] = !current[lastKey];
            
            // Save configuration
            await chrome.storage.local.set({ catdams_config: config });
            
            // Update UI
            this.loadConfiguration();
            
            // Notify background script
            chrome.runtime.sendMessage({
                type: 'config_updated',
                config: config
            });
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to toggle setting:', error);
        }
    }

    async setLogLevel(level) {
        try {
            const result = await chrome.storage.local.get(['catdams_config']);
            const config = result.catdams_config || {};
            
            if (!config.errorHandling) {
                config.errorHandling = {};
            }
            config.errorHandling.logLevel = level;
            
            await chrome.storage.local.set({ catdams_config: config });
            this.updateLogLevel(level);
            
            // Notify background script
            chrome.runtime.sendMessage({
                type: 'config_updated',
                config: config
            });
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to set log level:', error);
        }
    }

    async updateStats() {
        try {
            // Get stats from background script
            chrome.runtime.sendMessage({ type: 'get_stats' }, (response) => {
                if (response && response.stats) {
                    this.stats = { ...this.stats, ...response.stats };
                    this.updateStatsDisplay();
                }
            });
            
            // Calculate uptime
            const uptime = Math.floor((Date.now() - this.startTime) / 60000);
            document.getElementById('uptime').textContent = `${uptime}m`;
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to update stats:', error);
        }
    }

    updateStatsDisplay() {
        document.getElementById('messagesProcessed').textContent = this.stats.messagesProcessed || 0;
        document.getElementById('threatsDetected').textContent = this.stats.threatsDetected || 0;
        document.getElementById('sessionsActive').textContent = this.stats.sessionsActive || 0;
    }

    startStatusUpdates() {
        // Update stats every 5 seconds
        setInterval(() => {
            this.updateStats();
        }, 5000);
        
        // Update status indicator
        setInterval(() => {
            this.updateStatusIndicator();
        }, 2000);
    }

    async updateStatusIndicator() {
        try {
            const indicator = document.getElementById('statusIndicator');
            
            // Check if background script is responsive
            chrome.runtime.sendMessage({ type: 'ping' }, (response) => {
                if (chrome.runtime.lastError) {
                    indicator.style.background = '#f44336'; // Red
                } else {
                    indicator.style.background = '#4CAF50'; // Green
                }
            });
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to update status indicator:', error);
        }
    }

    async clearLogs() {
        try {
            await chrome.storage.local.remove(['catdams_log', 'catdams_error_log']);
            
            // Reset stats
            this.stats = {
                messagesProcessed: 0,
                threatsDetected: 0,
                sessionsActive: 0,
                errors: 0
            };
            this.updateStatsDisplay();
            
            // Show feedback
            this.showNotification('Logs cleared successfully');
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to clear logs:', error);
            this.showNotification('Failed to clear logs', 'error');
        }
    }

    async exportLogs() {
        try {
            const result = await chrome.storage.local.get(['catdams_log', 'catdams_error_log']);
            const logs = {
                timestamp: new Date().toISOString(),
                regular_logs: result.catdams_log || [],
                error_logs: result.catdams_error_log || [],
                stats: this.stats
            };
            
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `catdams-logs-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            this.showNotification('Logs exported successfully');
            
        } catch (error) {
            console.error('[CATDAMS Popup] Failed to export logs:', error);
            this.showNotification('Failed to export logs', 'error');
        }
    }

    async refreshStats() {
        await this.updateStats();
        this.showNotification('Stats refreshed');
    }

    showNotification(message, type = 'success') {
        // Create temporary notification
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#f44336' : '#4CAF50'};
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CATDAMSPopupController();
});

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style); 