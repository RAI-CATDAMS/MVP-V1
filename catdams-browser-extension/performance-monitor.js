// ====== CATDAMS Performance Monitor & Optimizer ======
// Comprehensive performance monitoring, optimization, and security hardening

class CATDAMSPerformanceMonitor {
    constructor(config, logger, errorHandler) {
        this.config = config;
        this.logger = logger;
        this.errorHandler = errorHandler;
        this.metrics = {
            memoryUsage: 0,
            cpuUsage: 0,
            detectionLatency: [],
            falsePositiveRate: 0,
            threatDetectionRate: 0,
            lastOptimization: Date.now(),
            performanceScore: 100
        };
        
        this.optimizationHistory = [];
        this.securityChecks = new Map();
        this.performanceThresholds = {
            memoryThreshold: config.get('performance.memoryThreshold', 50),
            cpuThreshold: config.get('performance.cpuThreshold', 80),
            latencyThreshold: 1000, // 1 second
            maxLogSize: config.get('performance.maxLogSize', 1000)
        };
        
        this.initialize();
    }

    async initialize() {
        try {
            this.setupSecurityChecks();
            this.startMonitoring();
            this.logger.info('[CATDAMS Performance] Performance monitor initialized');
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'performance_initialize' });
        }
    }

    setupSecurityChecks() {
        // Content Security Policy checks
        this.securityChecks.set('csp', {
            enabled: true,
            lastCheck: 0,
            violations: []
        });

        // Input validation checks
        this.securityChecks.set('input_validation', {
            enabled: true,
            lastCheck: 0,
            violations: []
        });

        // Data sanitization checks
        this.securityChecks.set('data_sanitization', {
            enabled: true,
            lastCheck: 0,
            violations: []
        });

        // Encryption checks
        this.securityChecks.set('encryption', {
            enabled: true,
            lastCheck: 0,
            violations: []
        });
    }

    startMonitoring() {
        // Monitor performance every 30 seconds
        setInterval(() => {
            this.updateMetrics();
        }, 30000);

        // Run security checks every 60 seconds
        setInterval(() => {
            this.runSecurityChecks();
        }, 60000);

        // Optimize performance every 5 minutes
        setInterval(() => {
            this.optimizePerformance();
        }, 300000);

        // Cleanup old data every 10 minutes
        setInterval(() => {
            this.cleanupOldData();
        }, 600000);
    }

    async updateMetrics() {
        try {
            // Memory usage (approximate)
            this.metrics.memoryUsage = this.estimateMemoryUsage();
            
            // CPU usage (approximate based on processing time)
            this.metrics.cpuUsage = this.estimateCPUUsage();
            
            // Performance score calculation
            this.metrics.performanceScore = this.calculatePerformanceScore();
            
            // Check if optimization is needed
            if (this.shouldOptimize()) {
                await this.optimizePerformance();
            }
            
            this.logger.debug('[CATDAMS Performance] Metrics updated', this.metrics);
            
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'updateMetrics' });
        }
    }

    estimateMemoryUsage() {
        try {
            // Estimate memory usage based on stored data
            const storageData = JSON.stringify(localStorage).length + 
                              JSON.stringify(sessionStorage).length;
            
            // Approximate memory usage in MB
            return Math.round(storageData / 1024 / 1024 * 100) / 100;
        } catch (error) {
            return 0;
        }
    }

    estimateCPUUsage() {
        try {
            // Estimate CPU usage based on processing time
            const processingTime = this.metrics.detectionLatency.length > 0 ?
                this.metrics.detectionLatency.reduce((sum, time) => sum + time, 0) / 
                this.metrics.detectionLatency.length : 0;
            
            // Convert to percentage (rough estimate)
            return Math.min(100, Math.round(processingTime / 10));
        } catch (error) {
            return 0;
        }
    }

    calculatePerformanceScore() {
        let score = 100;
        
        // Deduct points for high memory usage
        if (this.metrics.memoryUsage > this.performanceThresholds.memoryThreshold) {
            score -= 20;
        }
        
        // Deduct points for high CPU usage
        if (this.metrics.cpuUsage > this.performanceThresholds.cpuThreshold) {
            score -= 20;
        }
        
        // Deduct points for high latency
        const avgLatency = this.metrics.detectionLatency.length > 0 ?
            this.metrics.detectionLatency.reduce((sum, time) => sum + time, 0) / 
            this.metrics.detectionLatency.length : 0;
        
        if (avgLatency > this.performanceThresholds.latencyThreshold) {
            score -= 15;
        }
        
        // Deduct points for high false positive rate
        if (this.metrics.falsePositiveRate > 0.1) { // 10%
            score -= 10;
        }
        
        return Math.max(0, score);
    }

    shouldOptimize() {
        return this.metrics.performanceScore < 70 || 
               this.metrics.memoryUsage > this.performanceThresholds.memoryThreshold ||
               this.metrics.cpuUsage > this.performanceThresholds.cpuThreshold;
    }

    async optimizePerformance() {
        try {
            this.logger.info('[CATDAMS Performance] Starting performance optimization');
            
            const optimizations = [];
            
            // Memory optimization
            if (this.metrics.memoryUsage > this.performanceThresholds.memoryThreshold) {
                optimizations.push(await this.optimizeMemory());
            }
            
            // CPU optimization
            if (this.metrics.cpuUsage > this.performanceThresholds.cpuThreshold) {
                optimizations.push(await this.optimizeCPU());
            }
            
            // Latency optimization
            const avgLatency = this.metrics.detectionLatency.length > 0 ?
                this.metrics.detectionLatency.reduce((sum, time) => sum + time, 0) / 
                this.metrics.detectionLatency.length : 0;
            
            if (avgLatency > this.performanceThresholds.latencyThreshold) {
                optimizations.push(await this.optimizeLatency());
            }
            
            // Log optimization results
            if (optimizations.length > 0) {
                this.optimizationHistory.push({
                    timestamp: Date.now(),
                    optimizations: optimizations,
                    performanceScore: this.metrics.performanceScore
                });
                
                this.logger.info('[CATDAMS Performance] Optimization completed', {
                    optimizations: optimizations,
                    newScore: this.metrics.performanceScore
                });
            }
            
            this.metrics.lastOptimization = Date.now();
            
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'optimizePerformance' });
        }
    }

    async optimizeMemory() {
        try {
            // Clear old logs
            await this.clearOldLogs();
            
            // Clear old cache
            await this.clearOldCache();
            
            // Optimize storage
            await this.optimizeStorage();
            
            return 'memory_optimized';
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Memory optimization failed:', error);
            return 'memory_optimization_failed';
        }
    }

    async optimizeCPU() {
        try {
            // Reduce processing frequency for non-critical operations
            this.adjustProcessingFrequency();
            
            // Optimize detection algorithms
            this.optimizeDetectionAlgorithms();
            
            return 'cpu_optimized';
        } catch (error) {
            this.logger.error('[CATDAMS Performance] CPU optimization failed:', error);
            return 'cpu_optimization_failed';
        }
    }

    async optimizeLatency() {
        try {
            // Implement request batching
            this.implementRequestBatching();
            
            // Optimize network requests
            this.optimizeNetworkRequests();
            
            return 'latency_optimized';
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Latency optimization failed:', error);
            return 'latency_optimization_failed';
        }
    }

    async clearOldLogs() {
        try {
            const result = await chrome.storage.local.get(['catdams_log', 'catdams_error_log']);
            
            // Keep only recent logs
            const maxLogSize = this.performanceThresholds.maxLogSize;
            
            if (result.catdams_log && result.catdams_log.length > maxLogSize) {
                result.catdams_log = result.catdams_log.slice(-maxLogSize);
            }
            
            if (result.catdams_error_log && result.catdams_error_log.length > maxLogSize) {
                result.catdams_error_log = result.catdams_error_log.slice(-maxLogSize);
            }
            
            await chrome.storage.local.set({
                catdams_log: result.catdams_log || [],
                catdams_error_log: result.catdams_error_log || []
            });
            
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Failed to clear old logs:', error);
        }
    }

    async clearOldCache() {
        try {
            // Clear old TDC results
            const result = await chrome.storage.local.get(['catdams_tdc_results']);
            if (result.catdams_tdc_results && result.catdams_tdc_results.length > 50) {
                result.catdams_tdc_results = result.catdams_tdc_results.slice(-50);
                await chrome.storage.local.set({ catdams_tdc_results: result.catdams_tdc_results });
            }
            
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Failed to clear old cache:', error);
        }
    }

    async optimizeStorage() {
        try {
            // Compress stored data
            const result = await chrome.storage.local.get();
            const compressedData = {};
            
            for (const [key, value] of Object.entries(result)) {
                if (typeof value === 'string' && value.length > 1000) {
                    // Simple compression for large strings
                    compressedData[key] = this.compressString(value);
                } else {
                    compressedData[key] = value;
                }
            }
            
            await chrome.storage.local.set(compressedData);
            
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Failed to optimize storage:', error);
        }
    }

    compressString(str) {
        // Simple compression - remove unnecessary whitespace
        return str.replace(/\s+/g, ' ').trim();
    }

    adjustProcessingFrequency() {
        // Adjust detection intervals based on performance
        const currentInterval = this.config.get('performance.detectionInterval', 2000);
        
        if (this.metrics.performanceScore < 50) {
            // Increase interval for better performance
            this.config.set('performance.detectionInterval', Math.min(currentInterval * 1.5, 5000));
        } else if (this.metrics.performanceScore > 90) {
            // Decrease interval for better detection
            this.config.set('performance.detectionInterval', Math.max(currentInterval * 0.8, 1000));
        }
    }

    optimizeDetectionAlgorithms() {
        // Optimize threat detection patterns
        const patterns = this.config.get('threatDetection.patterns');
        if (patterns) {
            // Cache compiled regex patterns
            for (const [type, patternList] of Object.entries(patterns)) {
                if (Array.isArray(patternList)) {
                    patterns[type] = patternList.map(pattern => 
                        typeof pattern === 'string' ? new RegExp(pattern, 'i') : pattern
                    );
                }
            }
        }
    }

    implementRequestBatching() {
        // Implement request batching for better performance
        this.batchRequests = true;
        this.batchTimeout = 100; // 100ms batch window
        this.pendingRequests = [];
    }

    optimizeNetworkRequests() {
        // Optimize network request patterns
        const backendConfig = this.config.get('backend');
        if (backendConfig) {
            // Implement connection pooling
            backendConfig.connectionPooling = true;
            backendConfig.maxConnections = 5;
        }
    }

    async runSecurityChecks() {
        try {
            const securityReport = {
                timestamp: Date.now(),
                checks: {}
            };
            
            // CSP Check
            if (this.securityChecks.get('csp').enabled) {
                securityReport.checks.csp = await this.checkCSP();
            }
            
            // Input Validation Check
            if (this.securityChecks.get('input_validation').enabled) {
                securityReport.checks.input_validation = await this.checkInputValidation();
            }
            
            // Data Sanitization Check
            if (this.securityChecks.get('data_sanitization').enabled) {
                securityReport.checks.data_sanitization = await this.checkDataSanitization();
            }
            
            // Encryption Check
            if (this.securityChecks.get('encryption').enabled) {
                securityReport.checks.encryption = await this.checkEncryption();
            }
            
            // Log security report
            this.logger.info('[CATDAMS Performance] Security check completed', securityReport);
            
            // Store security report
            await this.storeSecurityReport(securityReport);
            
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'runSecurityChecks' });
        }
    }

    async checkCSP() {
        try {
            // Check if CSP is properly configured
            const metaTags = document.querySelectorAll('meta[http-equiv="Content-Security-Policy"]');
            return {
                status: metaTags.length > 0 ? 'enabled' : 'disabled',
                violations: []
            };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }

    async checkInputValidation() {
        try {
            // Check input validation patterns
            const validationPatterns = [
                /<script/i,
                /javascript:/i,
                /on\w+\s*=/i
            ];
            
            const violations = [];
            
            // Check recent messages for validation issues
            const result = await chrome.storage.local.get(['catdams_log']);
            if (result.catdams_log) {
                const recentLogs = result.catdams_log.slice(-10);
                recentLogs.forEach(log => {
                    if (log.data && log.data.message) {
                        validationPatterns.forEach(pattern => {
                            if (pattern.test(log.data.message)) {
                                violations.push({
                                    pattern: pattern.source,
                                    message: log.data.message.substring(0, 50)
                                });
                            }
                        });
                    }
                });
            }
            
            return {
                status: violations.length === 0 ? 'clean' : 'violations_detected',
                violations: violations
            };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }

    async checkDataSanitization() {
        try {
            // Check if data is properly sanitized
            const result = await chrome.storage.local.get(['catdams_log']);
            const sanitizationIssues = [];
            
            if (result.catdams_log) {
                const recentLogs = result.catdams_log.slice(-10);
                recentLogs.forEach(log => {
                    if (log.data && log.data.message) {
                        // Check for unsanitized HTML
                        if (/<[^>]*>/.test(log.data.message)) {
                            sanitizationIssues.push({
                                type: 'unsanitized_html',
                                message: log.data.message.substring(0, 50)
                            });
                        }
                    }
                });
            }
            
            return {
                status: sanitizationIssues.length === 0 ? 'clean' : 'issues_detected',
                issues: sanitizationIssues
            };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }

    async checkEncryption() {
        try {
            // Check if sensitive data is encrypted
            const result = await chrome.storage.local.get(['catdams_config']);
            const encryptionIssues = [];
            
            if (result.catdams_config) {
                // Check for unencrypted sensitive data
                const sensitiveKeys = ['api_key', 'password', 'token', 'secret'];
                const configStr = JSON.stringify(result.catdams_config);
                
                sensitiveKeys.forEach(key => {
                    if (configStr.includes(key) && !configStr.includes('encrypted')) {
                        encryptionIssues.push({
                            type: 'unencrypted_sensitive_data',
                            key: key
                        });
                    }
                });
            }
            
            return {
                status: encryptionIssues.length === 0 ? 'secure' : 'issues_detected',
                issues: encryptionIssues
            };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }

    async storeSecurityReport(report) {
        try {
            const existingReports = await chrome.storage.local.get(['catdams_security_reports']);
            const reports = existingReports.catdams_security_reports || [];
            
            reports.push(report);
            
            // Keep only recent reports (last 20)
            if (reports.length > 20) {
                reports.splice(0, reports.length - 20);
            }
            
            await chrome.storage.local.set({ catdams_security_reports: reports });
            
        } catch (error) {
            this.logger.error('[CATDAMS Performance] Failed to store security report:', error);
        }
    }

    async cleanupOldData() {
        try {
            // Cleanup old optimization history
            if (this.optimizationHistory.length > 50) {
                this.optimizationHistory = this.optimizationHistory.slice(-50);
            }
            
            // Cleanup old performance metrics
            if (this.metrics.detectionLatency.length > 100) {
                this.metrics.detectionLatency = this.metrics.detectionLatency.slice(-100);
            }
            
            this.logger.debug('[CATDAMS Performance] Cleanup completed');
            
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'cleanupOldData' });
        }
    }

    recordDetectionLatency(latency) {
        this.metrics.detectionLatency.push(latency);
        
        // Keep only recent latencies
        if (this.metrics.detectionLatency.length > 100) {
            this.metrics.detectionLatency = this.metrics.detectionLatency.slice(-100);
        }
    }

    updateDetectionRates(truePositives, falsePositives, totalDetections) {
        if (totalDetections > 0) {
            this.metrics.threatDetectionRate = truePositives / totalDetections;
            this.metrics.falsePositiveRate = falsePositives / totalDetections;
        }
    }

    getMetrics() {
        return {
            ...this.metrics,
            optimizationHistory: this.optimizationHistory.slice(-10),
            securityChecks: Object.fromEntries(this.securityChecks)
        };
    }

    getPerformanceReport() {
        return {
            timestamp: Date.now(),
            metrics: this.metrics,
            recommendations: this.generatePerformanceRecommendations(),
            optimizationHistory: this.optimizationHistory.slice(-5)
        };
    }

    generatePerformanceRecommendations() {
        const recommendations = [];
        
        if (this.metrics.performanceScore < 70) {
            recommendations.push('Performance optimization recommended');
        }
        
        if (this.metrics.memoryUsage > this.performanceThresholds.memoryThreshold) {
            recommendations.push('Memory usage is high - consider cleanup');
        }
        
        if (this.metrics.cpuUsage > this.performanceThresholds.cpuThreshold) {
            recommendations.push('CPU usage is high - consider reducing processing frequency');
        }
        
        if (this.metrics.falsePositiveRate > 0.1) {
            recommendations.push('High false positive rate - consider adjusting detection thresholds');
        }
        
        return recommendations;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATDAMSPerformanceMonitor;
} else {
    window.CATDAMSPerformanceMonitor = CATDAMSPerformanceMonitor;
} 