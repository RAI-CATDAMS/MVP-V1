// ====== CATDAMS Unified Logger ======
// Robust logging utility for diagnostics, monitoring, and debugging

class CATDAMSLogger {
    constructor(config) {
        this.config = config;
        this.logBuffer = [];
        this.maxBufferSize = 500;
        this.logLevels = ['debug', 'info', 'warn', 'error'];
        this.logToConsole = config.get('errorHandling.logToConsole', true);
        this.logToStorage = config.get('errorHandling.logToStorage', true);
        this.logLevel = config.get('errorHandling.logLevel', 'info');
    }

    shouldLog(level) {
        return this.logLevels.indexOf(level) >= this.logLevels.indexOf(this.logLevel);
    }

    log(level, message, data = null) {
        if (!this.shouldLog(level)) return;
        const entry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            data
        };
        this.logBuffer.push(entry);
        if (this.logBuffer.length > this.maxBufferSize) {
            this.logBuffer.shift();
        }
        if (this.logToConsole) {
            this.logToConsoleMethod(level, message, data);
        }
        if (this.logToStorage) {
            this.saveToStorage(entry);
        }
    }

    logToConsoleMethod(level, message, data) {
        if (data) {
            console[level](`[CATDAMS][${level.toUpperCase()}]`, message, data);
        } else {
            console[level](`[CATDAMS][${level.toUpperCase()}]`, message);
        }
    }

    async saveToStorage(entry) {
        try {
            const result = await chrome.storage.local.get(['catdams_log']);
            const log = result.catdams_log || [];
            log.push(entry);
            if (log.length > this.maxBufferSize) {
                log.splice(0, log.length - this.maxBufferSize);
            }
            await chrome.storage.local.set({ catdams_log: log });
        } catch (error) {
            // Fallback: log to console if storage fails
            console.warn('[CATDAMS Logger] Failed to save log to storage:', error);
        }
    }

    debug(message, data = null) { this.log('debug', message, data); }
    info(message, data = null) { this.log('info', message, data); }
    warn(message, data = null) { this.log('warn', message, data); }
    error(message, data = null) { this.log('error', message, data); }

    async getRecentLogs(count = 50) {
        try {
            const result = await chrome.storage.local.get(['catdams_log']);
            const log = result.catdams_log || [];
            return log.slice(-count);
        } catch (error) {
            return this.logBuffer.slice(-count);
        }
    }

    clearLogs() {
        this.logBuffer = [];
        chrome.storage.local.remove(['catdams_log']);
        if (this.logToConsole) {
            console.info('[CATDAMS Logger] Log buffer and storage cleared');
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATDAMSLogger;
} else {
    window.CATDAMSLogger = CATDAMSLogger;
} 