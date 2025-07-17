// ====== CATDAMS Unified Configuration System ======
// Aligned with 11-module TDC structure and enhanced error handling

class CATDAMSConfig {
    constructor() {
        this.config = {
            // Core TDC Module Configuration (11 modules)
            tdcModules: {
                tdc_ai1_user_susceptibility: {
                    enabled: true,
                    priority: 1,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai2_behavioral_indicators: {
                    enabled: true,
                    priority: 2,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai3_emotional_state: {
                    enabled: true,
                    priority: 3,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai4_prompt_attack_detection: {
                    enabled: true,
                    priority: 4,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai5_multimodal_threat: {
                    enabled: true,
                    priority: 5,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai6_temporal_conditioning: {
                    enabled: true,
                    priority: 6,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai7_agentic_ai_threat: {
                    enabled: true,
                    priority: 7,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai8_escalation_synthesis: {
                    enabled: true,
                    priority: 8,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai9_explainability_evidence: {
                    enabled: true,
                    priority: 9,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai10_cognitive_bias: {
                    enabled: true,
                    priority: 10,
                    timeout: 5000,
                    retries: 3
                },
                tdc_ai11_intervention_strategies: {
                    enabled: true,
                    priority: 11,
                    timeout: 5000,
                    retries: 3
                }
            },

            // Backend Configuration
            backend: {
                endpoint: "http://localhost:8000/event",
                sessionBridge: "http://localhost:3009/session-id",
                timeout: 10000,
                retries: 3,
                retryDelay: 1000,
                circuitBreaker: {
                    enabled: true,
                    failureThreshold: 5,
                    recoveryTimeout: 30000
                }
            },

            // Performance & Monitoring
            performance: {
                detectionInterval: 2000,
                sessionTimeout: 300000, // 5 minutes
                memoryThreshold: 50, // MB
                cpuThreshold: 80, // percentage
                cleanupInterval: 60000, // 1 minute
                maxLogSize: 1000
            },

            // Error Handling & Resilience
            errorHandling: {
                logLevel: 'info', // debug, info, warn, error
                logToConsole: true,
                logToStorage: true,
                maxRetries: 3,
                exponentialBackoff: true,
                gracefulDegradation: true,
                errorReporting: true
            },

            // Security & Privacy
            security: {
                contentSecurityPolicy: true,
                inputValidation: true,
                dataSanitization: true,
                encryption: true,
                privacyControls: true,
                dataRetention: {
                    enabled: true,
                    maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
                }
            },

            // Platform Detection
            platforms: {
                enabled: true,
                autoDetect: true,
                fallbackSelectors: true,
                dynamicLoading: true
            },

            // Threat Detection
            threatDetection: {
                enabled: true,
                realTime: true,
                batchProcessing: true,
                severityLevels: {
                    LOW: "Low",
                    MEDIUM: "Medium",
                    HIGH: "High",
                    CRITICAL: "Critical"
                },
                patterns: {
                    promptInjection: [
                        "ignore previous", "ignore safety", "ignore guidelines", "ignore rules",
                        "act as", "pretend to be", "roleplay as", "you are now",
                        "bypass", "override", "jailbreak", "break character",
                        "ignore your training", "forget your instructions", "ignore your programming"
                    ],
                    sensitiveData: {
                        creditCard: /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/,
                        ssn: /\b\d{3}-\d{2}-\d{4}\b/,
                        email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
                        phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/,
                        password: /password|passwd|pwd|secret|key|token|api_key/i,
                        address: /\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr)/i
                    }
                }
            }
        };

        this.initialize();
    }

    async initialize() {
        try {
            // Load saved configuration from storage
            const savedConfig = await this.loadFromStorage();
            if (savedConfig) {
                this.config = { ...this.config, ...savedConfig };
            }

            // Validate configuration
            this.validateConfig();

            console.log('[CATDAMS Config] Configuration initialized successfully');
            return true;
        } catch (error) {
            console.error('[CATDAMS Config] Configuration initialization failed:', error);
            return false;
        }
    }

    async loadFromStorage() {
        try {
            const result = await chrome.storage.local.get(['catdams_config']);
            return result.catdams_config || null;
        } catch (error) {
            console.warn('[CATDAMS Config] Failed to load from storage:', error);
            return null;
        }
    }

    async saveToStorage() {
        try {
            await chrome.storage.local.set({ catdams_config: this.config });
            console.log('[CATDAMS Config] Configuration saved to storage');
            return true;
        } catch (error) {
            console.error('[CATDAMS Config] Failed to save to storage:', error);
            return false;
        }
    }

    validateConfig() {
        // Validate TDC modules configuration
        const requiredModules = [
            'tdc_ai1_user_susceptibility', 'tdc_ai2_behavioral_indicators',
            'tdc_ai3_emotional_state', 'tdc_ai4_prompt_attack_detection',
            'tdc_ai5_multimodal_threat', 'tdc_ai6_temporal_conditioning',
            'tdc_ai7_agentic_ai_threat', 'tdc_ai8_escalation_synthesis',
            'tdc_ai9_explainability_evidence', 'tdc_ai10_cognitive_bias',
            'tdc_ai11_intervention_strategies'
        ];

        for (const moduleName of requiredModules) {
            if (!this.config.tdcModules[moduleName]) {
                console.warn(`[CATDAMS Config] Missing TDC module configuration: ${moduleName}`);
                this.config.tdcModules[moduleName] = {
                    enabled: true,
                    priority: 1,
                    timeout: 5000,
                    retries: 3
                };
            }
        }

        // Validate backend configuration
        if (!this.config.backend.endpoint) {
            throw new Error('Backend endpoint is required');
        }

        console.log('[CATDAMS Config] Configuration validation completed');
    }

    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }

    set(key, value) {
        const keys = key.split('.');
        let config = this.config;
        
        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in config) || typeof config[k] !== 'object') {
                config[k] = {};
            }
            config = config[k];
        }
        
        config[keys[keys.length - 1]] = value;
        this.saveToStorage();
    }

    getTDCModuleConfig(moduleName) {
        return this.config.tdcModules[moduleName] || null;
    }

    isTDCModuleEnabled(moduleName) {
        const moduleConfig = this.getTDCModuleConfig(moduleName);
        return moduleConfig ? moduleConfig.enabled : false;
    }

    getEnabledTDCModules() {
        return Object.entries(this.config.tdcModules)
            .filter(([name, config]) => config.enabled)
            .sort((a, b) => a[1].priority - b[1].priority)
            .map(([name]) => name);
    }

    updateBackendEndpoint(endpoint) {
        this.config.backend.endpoint = endpoint;
        this.saveToStorage();
    }

    getBackendConfig() {
        return this.config.backend;
    }

    getPerformanceConfig() {
        return this.config.performance;
    }

    getErrorHandlingConfig() {
        return this.config.errorHandling;
    }

    getSecurityConfig() {
        return this.config.security;
    }

    getThreatDetectionConfig() {
        return this.config.threatDetection;
    }

    // Circuit breaker state management
    circuitBreakerState = {
        failures: 0,
        lastFailureTime: 0,
        state: 'CLOSED' // CLOSED, OPEN, HALF_OPEN
    };

    isCircuitBreakerOpen() {
        const config = this.config.backend.circuitBreaker;
        if (!config.enabled) return false;

        const now = Date.now();
        
        if (this.circuitBreakerState.state === 'OPEN') {
            if (now - this.circuitBreakerState.lastFailureTime > config.recoveryTimeout) {
                this.circuitBreakerState.state = 'HALF_OPEN';
                return false;
            }
            return true;
        }
        
        return false;
    }

    recordFailure() {
        const config = this.config.backend.circuitBreaker;
        if (!config.enabled) return;

        this.circuitBreakerState.failures++;
        this.circuitBreakerState.lastFailureTime = Date.now();

        if (this.circuitBreakerState.failures >= config.failureThreshold) {
            this.circuitBreakerState.state = 'OPEN';
            console.warn('[CATDAMS Config] Circuit breaker opened due to repeated failures');
        }
    }

    recordSuccess() {
        const config = this.config.backend.circuitBreaker;
        if (!config.enabled) return;

        this.circuitBreakerState.failures = 0;
        this.circuitBreakerState.state = 'CLOSED';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATDAMSConfig;
} else {
    window.CATDAMSConfig = CATDAMSConfig;
} 