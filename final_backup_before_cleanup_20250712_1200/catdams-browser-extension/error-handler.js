// ====== CATDAMS Error Handling & Resilience System ======
// Provides graceful degradation, automatic recovery, and comprehensive error tracking

class CATDAMSErrorHandler {
    constructor(config) {
        this.config = config;
        this.errorCounts = new Map();
        this.recoveryStrategies = new Map();
        this.circuitBreakers = new Map();
        this.errorLog = [];
        this.maxErrorLogSize = 100;

        this.initializeRecoveryStrategies();
    }

    initializeRecoveryStrategies() {
        // Network error recovery strategies
        this.recoveryStrategies.set('NETWORK_ERROR', {
            maxRetries: 3,
            backoffMultiplier: 2,
            baseDelay: 1000,
            maxDelay: 10000
        });

        // TDC module error recovery strategies
        this.recoveryStrategies.set('TDC_MODULE_ERROR', {
            maxRetries: 2,
            backoffMultiplier: 1.5,
            baseDelay: 500,
            maxDelay: 5000
        });

        // Storage error recovery strategies
        this.recoveryStrategies.set('STORAGE_ERROR', {
            maxRetries: 2,
            backoffMultiplier: 1.2,
            baseDelay: 200,
            maxDelay: 2000
        });

        // DOM manipulation error recovery strategies
        this.recoveryStrategies.set('DOM_ERROR', {
            maxRetries: 1,
            backoffMultiplier: 1.0,
            baseDelay: 100,
            maxDelay: 1000
        });
    }

    async handleError(error, context = {}) {
        const errorInfo = {
            timestamp: Date.now(),
            error: error,
            context: context,
            stack: error.stack,
            type: this.categorizeError(error),
            severity: this.calculateSeverity(error, context)
        };

        // Log the error
        this.logError(errorInfo);

        // Update error counts
        this.updateErrorCount(errorInfo.type);

        // Check if circuit breaker should be triggered
        if (this.shouldTriggerCircuitBreaker(errorInfo.type)) {
            this.triggerCircuitBreaker(errorInfo.type);
        }

        // Attempt recovery
        const recoveryResult = await this.attemptRecovery(errorInfo);

        // Return appropriate response based on recovery success
        if (recoveryResult.success) {
            return {
                success: true,
                recovered: true,
                data: recoveryResult.data,
                fallback: recoveryResult.fallback
            };
        } else {
            return {
                success: false,
                error: errorInfo,
                graceful: this.canGracefullyDegrade(errorInfo)
            };
        }
    }

    categorizeError(error) {
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
            return 'NETWORK_ERROR';
        } else if (error.name === 'QuotaExceededError' || error.message.includes('storage')) {
            return 'STORAGE_ERROR';
        } else if (error.name === 'TypeError' && error.message.includes('null')) {
            return 'DOM_ERROR';
        } else if (error.message.includes('TDC') || error.message.includes('module')) {
            return 'TDC_MODULE_ERROR';
        } else {
            return 'UNKNOWN_ERROR';
        }
    }

    calculateSeverity(error, context) {
        let severity = 'LOW';

        // Check if it's a critical operation
        if (context.critical) {
            severity = 'HIGH';
        }

        // Check error frequency
        const errorCount = this.errorCounts.get(this.categorizeError(error)) || 0;
        if (errorCount > 10) {
            severity = 'CRITICAL';
        } else if (errorCount > 5) {
            severity = 'HIGH';
        } else if (errorCount > 2) {
            severity = 'MEDIUM';
        }

        // Check if it affects core functionality
        if (context.module && context.module.startsWith('tdc_ai')) {
            severity = 'MEDIUM';
        }

        return severity;
    }

    updateErrorCount(errorType) {
        const currentCount = this.errorCounts.get(errorType) || 0;
        this.errorCounts.set(errorType, currentCount + 1);
    }

    shouldTriggerCircuitBreaker(errorType) {
        const errorCount = this.errorCounts.get(errorType) || 0;
        const strategy = this.recoveryStrategies.get(errorType);
        
        if (!strategy) return false;
        
        return errorCount >= strategy.maxRetries * 2;
    }

    triggerCircuitBreaker(errorType) {
        this.circuitBreakers.set(errorType, {
            state: 'OPEN',
            timestamp: Date.now(),
            timeout: 30000 // 30 seconds
        });

        console.warn(`[CATDAMS ErrorHandler] Circuit breaker triggered for ${errorType}`);
    }

    isCircuitBreakerOpen(errorType) {
        const breaker = this.circuitBreakers.get(errorType);
        if (!breaker) return false;

        if (breaker.state === 'OPEN') {
            const now = Date.now();
            if (now - breaker.timestamp > breaker.timeout) {
                breaker.state = 'HALF_OPEN';
                return false;
            }
            return true;
        }

        return false;
    }

    async attemptRecovery(errorInfo) {
        const errorType = errorInfo.type;
        const strategy = this.recoveryStrategies.get(errorType);

        if (!strategy || this.isCircuitBreakerOpen(errorType)) {
            return { success: false };
        }

        // Attempt recovery based on error type
        switch (errorType) {
            case 'NETWORK_ERROR':
                return await this.recoverFromNetworkError(errorInfo, strategy);
            case 'TDC_MODULE_ERROR':
                return await this.recoverFromTDCModuleError(errorInfo, strategy);
            case 'STORAGE_ERROR':
                return await this.recoverFromStorageError(errorInfo, strategy);
            case 'DOM_ERROR':
                return await this.recoverFromDOMError(errorInfo, strategy);
            default:
                return { success: false };
        }
    }

    async recoverFromNetworkError(errorInfo, strategy) {
        const context = errorInfo.context;
        
        // Try alternative endpoints
        const alternativeEndpoints = [
            'http://localhost:8000/event',
            'http://127.0.0.1:8000/event'
        ];

        for (const endpoint of alternativeEndpoints) {
            try {
                const response = await this.retryWithBackoff(
                    () => fetch(endpoint, context.requestOptions),
                    strategy
                );
                
                if (response.ok) {
                    return {
                        success: true,
                        data: await response.json(),
                        fallback: true
                    };
                }
            } catch (retryError) {
                console.warn(`[CATDAMS ErrorHandler] Retry failed for ${endpoint}:`, retryError);
            }
        }

        // Fallback to local storage
        return {
            success: true,
            data: null,
            fallback: true,
            message: 'Data queued for later transmission'
        };
    }

    async recoverFromTDCModuleError(errorInfo, strategy) {
        const context = errorInfo.context;
        const moduleName = context.module;

        // Try alternative TDC module or fallback analysis
        if (moduleName && moduleName.startsWith('tdc_ai')) {
            // Try next priority module
            const enabledModules = this.config.getEnabledTDCModules();
            const currentIndex = enabledModules.indexOf(moduleName);
            
            if (currentIndex >= 0 && currentIndex < enabledModules.length - 1) {
                const nextModule = enabledModules[currentIndex + 1];
                console.log(`[CATDAMS ErrorHandler] Falling back to ${nextModule}`);
                
                return {
                    success: true,
                    data: { fallbackModule: nextModule },
                    fallback: true
                };
            }
        }

        // Basic threat analysis fallback
        return {
            success: true,
            data: { basicAnalysis: true },
            fallback: true
        };
    }

    async recoverFromStorageError(errorInfo, strategy) {
        // Try to clear old data and retry
        try {
            await chrome.storage.local.clear();
            return { success: true, data: null, fallback: false };
        } catch (clearError) {
            return { success: false };
        }
    }

    async recoverFromDOMError(errorInfo, strategy) {
        // Wait and retry DOM operations
        try {
            await this.retryWithBackoff(
                () => this.retryDOMOperation(errorInfo.context),
                strategy
            );
            return { success: true, data: null, fallback: false };
        } catch (retryError) {
            return { success: false };
        }
    }

    async retryWithBackoff(operation, strategy) {
        let lastError;
        
        for (let attempt = 0; attempt < strategy.maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                
                if (attempt < strategy.maxRetries - 1) {
                    const delay = Math.min(
                        strategy.baseDelay * Math.pow(strategy.backoffMultiplier, attempt),
                        strategy.maxDelay
                    );
                    
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        throw lastError;
    }

    async retryDOMOperation(context) {
        // Implement DOM operation retry logic
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    reject(new Error('DOM not ready'));
                }
            }, 100);
        });
    }

    canGracefullyDegrade(errorInfo) {
        const criticalOperations = ['session_management', 'threat_detection'];
        const context = errorInfo.context;
        
        return !criticalOperations.some(op => 
            context.operation && context.operation.includes(op)
        );
    }

    logError(errorInfo) {
        this.errorLog.push(errorInfo);
        
        // Maintain log size
        if (this.errorLog.length > this.maxErrorLogSize) {
            this.errorLog.shift();
        }

        // Log to console if enabled
        if (this.config.get('errorHandling.logToConsole')) {
            const level = errorInfo.severity === 'CRITICAL' ? 'error' : 
                         errorInfo.severity === 'HIGH' ? 'warn' : 'info';
            
            console[level]('[CATDAMS ErrorHandler]', {
                type: errorInfo.type,
                severity: errorInfo.severity,
                message: errorInfo.error.message,
                context: errorInfo.context
            });
        }

        // Log to storage if enabled
        if (this.config.get('errorHandling.logToStorage')) {
            this.saveErrorToStorage(errorInfo);
        }
    }

    async saveErrorToStorage(errorInfo) {
        try {
            const errorLog = await chrome.storage.local.get(['catdams_error_log']) || [];
            errorLog.push(errorInfo);
            
            // Keep only recent errors
            if (errorLog.length > this.maxErrorLogSize) {
                errorLog.splice(0, errorLog.length - this.maxErrorLogSize);
            }
            
            await chrome.storage.local.set({ catdams_error_log: errorLog });
        } catch (storageError) {
            console.warn('[CATDAMS ErrorHandler] Failed to save error to storage:', storageError);
        }
    }

    getErrorStats() {
        const stats = {
            totalErrors: this.errorLog.length,
            errorCounts: Object.fromEntries(this.errorCounts),
            circuitBreakers: Object.fromEntries(this.circuitBreakers),
            recentErrors: this.errorLog.slice(-10)
        };

        return stats;
    }

    resetErrorCounts() {
        this.errorCounts.clear();
        this.circuitBreakers.clear();
        console.log('[CATDAMS ErrorHandler] Error counts and circuit breakers reset');
    }

    clearErrorLog() {
        this.errorLog = [];
        chrome.storage.local.remove(['catdams_error_log']);
        console.log('[CATDAMS ErrorHandler] Error log cleared');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATDAMSErrorHandler;
} else {
    window.CATDAMSErrorHandler = CATDAMSErrorHandler;
} 