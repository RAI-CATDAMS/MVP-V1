// ====== CATDAMS Enhanced Background Script v3.0 ======
// Implements best practices for Azure integration and message processing

importScripts('config.js', 'error-handler.js', 'logger.js', 'tdc-integration.js', 'performance-monitor.js');

// ====== Enhanced Azure Integration Manager ======
class AzureIntegrationManager {
    constructor(config, logger, errorHandler) {
        this.config = config;
        this.logger = logger;
        this.errorHandler = errorHandler;
        this.azureEnabled = this.checkAzureCredentials();
        this.fallbackEnabled = true;
        this.circuitBreaker = {
            failures: 0,
            lastFailure: 0,
            threshold: 5,
            timeout: 30000, // 30 seconds
            isOpen: false
        };
        
        this.initialize();
    }

    async initialize() {
        try {
            if (this.azureEnabled) {
                this.logger?.info('[CATDAMS Azure] Azure integration enabled');
            } else {
                this.logger?.warn('[CATDAMS Azure] Azure integration disabled - using fallback');
            }
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'azure_initialize' });
        }
    }

    checkAzureCredentials() {
        // Check if Azure credentials are available
        // In a real implementation, this would check environment variables or config
        return this.config?.get('azure.enabled') || false;
    }

    async analyzeWithAzure(text, context) {
        if (!this.azureEnabled || this.circuitBreaker.isOpen) {
            return this.fallbackAnalysis(text, context);
        }

        try {
            // Primary Azure analysis
            const azureResult = await this.callAzureServices(text, context);
            
            // Reset circuit breaker on success
            this.circuitBreaker.failures = 0;
            this.circuitBreaker.isOpen = false;
            
            return {
                source: 'azure',
                result: azureResult,
                confidence: azureResult.confidence || 0.8,
                timestamp: Date.now()
            };
        } catch (error) {
            this.logger?.warn('[CATDAMS Azure] Azure analysis failed, using fallback:', error);
            
            // Record failure
            this.recordFailure();
            
            if (this.fallbackEnabled) {
                return this.fallbackAnalysis(text, context);
            }
            
            throw error;
        }
    }

    async callAzureServices(text, context) {
        const promises = [
            this.analyzeSentiment(text),
            this.extractEntities(text),
            this.detectLanguage(text),
            this.analyzeKeyPhrases(text),
            this.detectPII(text)
        ];

        const results = await Promise.allSettled(promises);
        
        return this.synthesizeAzureResults(results, context);
    }

    async analyzeSentiment(text) {
        // Simulate Azure Text Analytics sentiment analysis
        return {
            sentiment: 'neutral',
            confidence: 0.7,
            positive: 0.3,
            negative: 0.2,
            neutral: 0.5
        };
    }

    async extractEntities(text) {
        // Simulate Azure Text Analytics entity extraction
        const entities = [];
        
        // Extract names
        const namePattern = /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g;
        const names = text.match(namePattern);
        if (names) {
            entities.push(...names.map(name => ({
                text: name,
                category: 'Person',
                confidence: 0.8
            })));
        }

        // Extract organizations
        const orgPattern = /\b[A-Z][a-z]+ (Inc|Corp|LLC|Ltd|Company)\b/g;
        const orgs = text.match(orgPattern);
        if (orgs) {
            entities.push(...orgs.map(org => ({
                text: org,
                category: 'Organization',
                confidence: 0.7
            })));
        }

        return entities;
    }

    async detectLanguage(text) {
        // Simulate Azure Text Analytics language detection
        const englishPattern = /^[a-zA-Z\s.,!?;:'"()-]+$/;
        return {
            language: englishPattern.test(text) ? 'en' : 'unknown',
            confidence: 0.9
        };
    }

    async analyzeKeyPhrases(text) {
        // Simulate Azure Text Analytics key phrase extraction
        const words = text.toLowerCase().split(/\s+/);
        const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
        
        const wordFreq = {};
        words.forEach(word => {
            if (word.length > 3 && !stopWords.has(word)) {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
            }
        });

        const keyPhrases = Object.entries(wordFreq)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([phrase, count]) => ({ phrase, count }));

        return keyPhrases;
    }

    async detectPII(text) {
        // Simulate Azure Text Analytics PII detection
        const piiEntities = [];
        
        // Email detection
        const emailPattern = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
        const emails = text.match(emailPattern);
        if (emails) {
            piiEntities.push(...emails.map(email => ({
                text: email,
                category: 'Email',
                confidence: 0.95
            })));
        }

        // Phone number detection
        const phonePattern = /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g;
        const phones = text.match(phonePattern);
        if (phones) {
            piiEntities.push(...phones.map(phone => ({
                text: phone,
                category: 'PhoneNumber',
                confidence: 0.9
            })));
        }

        // Credit card detection
        const ccPattern = /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g;
        const ccs = text.match(ccPattern);
        if (ccs) {
            piiEntities.push(...ccs.map(cc => ({
                text: cc,
                category: 'CreditCard',
                confidence: 0.85
            })));
        }

        return piiEntities;
    }

    synthesizeAzureResults(results, context) {
        const successful = results.filter(r => r.status === 'fulfilled');
        const failed = results.filter(r => r.status === 'rejected');

        if (failed.length > 0) {
            this.logger?.warn('[CATDAMS Azure] Some Azure services failed:', failed.length);
        }

        const sentiment = successful.find(r => r.value.sentiment)?.value;
        const entities = successful.find(r => Array.isArray(r.value))?.value || [];
        const language = successful.find(r => r.value.language)?.value;
        const keyPhrases = successful.find(r => Array.isArray(r.value) && r.value[0]?.phrase)?.value || [];
        const pii = successful.find(r => Array.isArray(r.value) && r.value[0]?.category)?.value || [];

        return {
            sentiment: sentiment || { sentiment: 'neutral', confidence: 0.5 },
            entities: entities,
            language: language || { language: 'unknown', confidence: 0.5 },
            keyPhrases: keyPhrases,
            pii: pii,
            confidence: this.calculateOverallConfidence(successful.length, results.length),
            context: context
        };
    }

    calculateOverallConfidence(successful, total) {
        return Math.max(0.5, successful / total);
    }

    async fallbackAnalysis(text, context) {
        // Local fallback analysis when Azure is unavailable
        const localAnalysis = {
            sentiment: this.localSentimentAnalysis(text),
            entities: this.localEntityExtraction(text),
            language: this.localLanguageDetection(text),
            keyPhrases: this.localKeyPhraseExtraction(text),
            pii: this.localPIIDetection(text),
            confidence: 0.6,
            source: 'local_fallback'
        };

        return {
            source: 'local',
            result: localAnalysis,
            confidence: 0.6,
            timestamp: Date.now()
        };
    }

    localSentimentAnalysis(text) {
        const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'happy'];
        const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated'];
        
        const words = text.toLowerCase().split(/\s+/);
        const positiveCount = words.filter(word => positiveWords.includes(word)).length;
        const negativeCount = words.filter(word => negativeWords.includes(word)).length;
        
        if (positiveCount > negativeCount) return { sentiment: 'positive', confidence: 0.6 };
        if (negativeCount > positiveCount) return { sentiment: 'negative', confidence: 0.6 };
        return { sentiment: 'neutral', confidence: 0.6 };
    }

    localEntityExtraction(text) {
        const entities = [];
        
        // Simple name extraction
        const namePattern = /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g;
        const names = text.match(namePattern);
        if (names) {
            entities.push(...names.map(name => ({ text: name, category: 'Person', confidence: 0.6 })));
        }
        
        return entities;
    }

    localLanguageDetection(text) {
        const englishPattern = /^[a-zA-Z\s.,!?;:'"()-]+$/;
        return {
            language: englishPattern.test(text) ? 'en' : 'unknown',
            confidence: 0.7
        };
    }

    localKeyPhraseExtraction(text) {
        const words = text.toLowerCase().split(/\s+/);
        const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
        
        const wordFreq = {};
        words.forEach(word => {
            if (word.length > 3 && !stopWords.has(word)) {
                wordFreq[word] = (wordFreq[word] || 0) + 1;
            }
        });

        return Object.entries(wordFreq)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 3)
            .map(([phrase, count]) => ({ phrase, count }));
    }

    localPIIDetection(text) {
        const pii = [];
        
        // Email detection
        const emailPattern = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
        const emails = text.match(emailPattern);
        if (emails) {
            pii.push(...emails.map(email => ({ text: email, category: 'Email', confidence: 0.8 })));
        }
        
        return pii;
    }

    recordFailure() {
        this.circuitBreaker.failures++;
        this.circuitBreaker.lastFailure = Date.now();
        
        if (this.circuitBreaker.failures >= this.circuitBreaker.threshold) {
            this.circuitBreaker.isOpen = true;
            this.logger?.warn('[CATDAMS Azure] Circuit breaker opened');
            
            // Reset after timeout
            setTimeout(() => {
                this.circuitBreaker.isOpen = false;
                this.logger?.info('[CATDAMS Azure] Circuit breaker reset');
            }, this.circuitBreaker.timeout);
        }
    }
}

// ====== Enhanced Message Processing Manager ======
class MessageProcessingManager {
    constructor(config, logger, errorHandler, azureManager) {
        this.config = config;
        this.logger = logger;
        this.errorHandler = errorHandler;
        this.azureManager = azureManager;
        this.messageQueue = [];
        this.processing = false;
        this.batchSize = 5;
        this.batchTimeout = 2000; // 2 seconds
        this.stats = {
            processed: 0,
            failed: 0,
            avgProcessingTime: 0
        };
        
        this.initialize();
    }

    async initialize() {
        try {
            this.startBatchProcessing();
            this.logger?.info('[CATDAMS Processing] Message processing manager initialized');
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'processing_initialize' });
        }
    }

    async queueMessage(payload) {
        try {
            // Validate payload
            const validation = this.validatePayload(payload);
            if (!validation.valid) {
                this.logger?.error('[CATDAMS Processing] Invalid payload:', validation.errors);
                return false;
            }

            // Add to queue
            this.messageQueue.push({
                ...payload,
                queuedAt: Date.now(),
                id: this.generateMessageId()
            });

            this.logger?.debug('[CATDAMS Processing] Message queued:', payload.message_id);
            return true;
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'queueMessage', payload });
            return false;
        }
    }

    validatePayload(payload) {
        const errors = [];
        
        if (!payload.message || payload.message.length > 10000) {
            errors.push('Invalid message content');
        }
        
        if (!['USER', 'AI'].includes(payload.sender)) {
            errors.push('Invalid sender');
        }
        
        if (!payload.session_id) {
            errors.push('Missing session ID');
        }
        
        if (!payload.platform) {
            errors.push('Missing platform');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    generateMessageId() {
        return `proc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    startBatchProcessing() {
        setInterval(() => {
            this.processBatch();
        }, this.batchTimeout);
    }

    async processBatch() {
        if (this.processing || this.messageQueue.length === 0) return;
        
        this.processing = true;
        
        try {
            const batch = this.messageQueue.splice(0, this.batchSize);
            const startTime = Date.now();
            
            this.logger?.info(`[CATDAMS Processing] Processing batch of ${batch.length} messages`);
            
            // Process messages in parallel
            const promises = batch.map(message => this.processMessage(message));
            const results = await Promise.allSettled(promises);
            
            // Update stats
            const processingTime = Date.now() - startTime;
            this.updateStats(results, processingTime);
            
            this.logger?.info(`[CATDAMS Processing] Batch completed in ${processingTime}ms`);
            
        } finally {
            this.processing = false;
        }
    }

    async processMessage(message) {
        const startTime = Date.now();
        
        try {
            // Enhanced analysis with Azure
            const azureAnalysis = await this.azureManager.analyzeWithAzure(
                message.message, 
                message.conversation_context || {}
            );
            
            // Merge Azure analysis with existing threat analysis
            const enhancedPayload = {
                ...message,
                azure_analysis: azureAnalysis,
                threat_analysis: {
                    ...message.threat_analysis,
                    azure_enhancement: azureAnalysis.source === 'azure',
                    sentiment: azureAnalysis.result.sentiment,
                    entities: azureAnalysis.result.entities,
                    pii_detected: azureAnalysis.result.pii.length > 0,
                    confidence: azureAnalysis.confidence
                },
                processing_time: Date.now() - startTime
            };
            
            // Send to backend
            await this.sendToBackend(enhancedPayload);
            
            this.logger?.debug('[CATDAMS Processing] Message processed successfully:', message.id);
            
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'processMessage', message });
            throw error;
        }
    }

    async sendToBackend(payload) {
        try {
            const response = await fetch(this.config?.get('backend.endpoint') || "http://localhost:8000/event", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CATDAMS-Version": "3.0",
                    "X-CATDAMS-Source": "browser-extension"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Backend responded with status: ${response.status}`);
            }

            const result = await response.json();
            this.logger?.debug('[CATDAMS Processing] Backend response:', result);
            
            return result;
        } catch (error) {
            this.logger?.error('[CATDAMS Processing] Backend communication failed:', error);
            throw error;
        }
    }

    updateStats(results, processingTime) {
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.filter(r => r.status === 'rejected').length;
        
        this.stats.processed += successful;
        this.stats.failed += failed;
        
        // Update average processing time
        const totalTime = this.stats.avgProcessingTime * (this.stats.processed - successful) + processingTime;
        this.stats.avgProcessingTime = totalTime / this.stats.processed;
    }

    getStats() {
        return {
            ...this.stats,
            queueLength: this.messageQueue.length,
            processing: this.processing
        };
    }
}

// ====== Enhanced Performance Monitor ======
class EnhancedPerformanceMonitor {
    constructor(config, logger, errorHandler) {
        this.config = config;
        this.logger = logger;
        this.errorHandler = errorHandler;
        this.metrics = {
            messageCount: 0,
            threatCount: 0,
            avgResponseTime: 0,
            errorRate: 0,
            memoryUsage: 0,
            lastUpdate: Date.now()
        };
        this.alerts = [];
        
        this.initialize();
    }

    async initialize() {
        try {
            this.startMonitoring();
            this.logger?.info('[CATDAMS Performance] Performance monitor initialized');
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'performance_initialize' });
        }
    }

    startMonitoring() {
        // Monitor every 30 seconds
        setInterval(() => {
            this.updateMetrics();
        }, 30000);
    }

    updateMetrics() {
        try {
            // Update memory usage (if available)
            if (performance.memory) {
                this.metrics.memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024; // MB
            }
            
            this.metrics.lastUpdate = Date.now();
            
            // Check for alerts
            this.checkAlerts();
            
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'updateMetrics' });
        }
    }

    checkAlerts() {
        const alerts = [];
        
        // Memory usage alert
        if (this.metrics.memoryUsage > 50) { // 50MB
            alerts.push({
                type: 'memory_usage',
                severity: 'warning',
                message: `High memory usage: ${this.metrics.memoryUsage.toFixed(2)}MB`,
                timestamp: Date.now()
            });
        }
        
        // Error rate alert
        if (this.metrics.errorRate > 0.1) { // 10%
            alerts.push({
                type: 'error_rate',
                severity: 'critical',
                message: `High error rate: ${(this.metrics.errorRate * 100).toFixed(1)}%`,
                timestamp: Date.now()
            });
        }
        
        // Response time alert
        if (this.metrics.avgResponseTime > 5000) { // 5 seconds
            alerts.push({
                type: 'response_time',
                severity: 'warning',
                message: `Slow response time: ${this.metrics.avgResponseTime.toFixed(0)}ms`,
                timestamp: Date.now()
            });
        }
        
        // Log new alerts
        const newAlerts = alerts.filter(alert => 
            !this.alerts.some(existing => 
                existing.type === alert.type && 
                existing.timestamp > Date.now() - 60000 // Within last minute
            )
        );
        
        newAlerts.forEach(alert => {
            this.logger?.warn(`[CATDAMS Performance] Alert: ${alert.message}`);
        });
        
        this.alerts = [...this.alerts, ...newAlerts].slice(-100); // Keep last 100 alerts
    }

    recordMessage() {
        this.metrics.messageCount++;
    }

    recordThreat() {
        this.metrics.threatCount++;
    }

    recordResponseTime(time) {
        const total = this.metrics.avgResponseTime * (this.metrics.messageCount - 1) + time;
        this.metrics.avgResponseTime = total / this.metrics.messageCount;
    }

    recordError() {
        const totalMessages = this.metrics.messageCount;
        const totalErrors = this.metrics.errorRate * totalMessages + 1;
        this.metrics.errorRate = totalErrors / (totalMessages + 1);
    }

    getMetrics() {
        return {
            ...this.metrics,
            threatDetectionRate: this.metrics.messageCount > 0 ? 
                this.metrics.threatCount / this.metrics.messageCount : 0
        };
    }
}

// ====== Initialize Enhanced Background Script ======
let catdamsConfig, catdamsErrorHandler, catdamsLogger, catdamsTDC, catdamsPerformance;
let azureManager, processingManager, performanceMonitor;

(async () => {
    try {
        // Initialize core systems
        catdamsConfig = new CATDAMSConfig();
        await catdamsConfig.initialize();
        
        catdamsErrorHandler = new CATDAMSErrorHandler(catdamsConfig);
        catdamsLogger = new CATDAMSLogger(catdamsConfig);
        
        // Initialize enhanced components
        catdamsTDC = new CATDAMSTDCIntegration(catdamsConfig, catdamsLogger, catdamsErrorHandler);
        catdamsPerformance = new CATDAMSPerformanceMonitor(catdamsConfig, catdamsLogger, catdamsErrorHandler);
        
        // Initialize new enhanced components
        azureManager = new AzureIntegrationManager(catdamsConfig, catdamsLogger, catdamsErrorHandler);
        processingManager = new MessageProcessingManager(catdamsConfig, catdamsLogger, catdamsErrorHandler, azureManager);
        performanceMonitor = new EnhancedPerformanceMonitor(catdamsConfig, catdamsLogger, catdamsErrorHandler);
        
        catdamsLogger.info('CATDAMS enhanced background.js initialized with Azure integration');
    } catch (error) {
        console.error('[CATDAMS] Enhanced background initialization failed:', error);
    }
})();

// ====== Enhanced Message Handling ======
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    try {
        if (msg && msg.type === "catdams_log" && msg.payload) {
            catdamsLogger?.info("[CATDAMS] ⬅️ Incoming payload:", msg.payload);

            // Record message for performance monitoring
            performanceMonitor?.recordMessage();

            // Queue message for processing
            processingManager?.queueMessage(msg.payload).then(success => {
                if (!success) {
                    catdamsLogger?.error("[CATDAMS] Failed to queue message");
                }
            });

            // Enhanced threat analysis with TDC modules
            if (catdamsTDC) {
                catdamsTDC.analyzeWithTDCModules(msg.payload, {
                    tabId: sender.tab?.id,
                    url: sender.tab?.url,
                    timestamp: Date.now()
                }).then(analysisResult => {
                    catdamsLogger?.info(`[CATDAMS TDC] Analysis completed: ${analysisResult.analysisId}`);
                }).catch(error => {
                    catdamsErrorHandler?.handleError(error, { operation: 'tdc_analysis', payload: msg.payload });
                });
            }

            // Log threat analysis if present
            if (msg.payload.threat_analysis && msg.payload.threat_analysis.threats.length > 0) {
                performanceMonitor?.recordThreat();
                logThreatAnalysis(msg.payload);
            }

            // 🔁 Trigger async response return
            sendResponse({ status: "queued", timestamp: Date.now() });
            return true; // ✅ Keeps message channel open for async
        }
        
        // Handle popup communication
        if (msg && msg.type === "get_stats") {
            const stats = {
                messagesProcessed: processingManager?.getStats().processed || 0,
                threatsDetected: performanceMonitor?.getMetrics().threatCount || 0,
                sessionsActive: 1, // Simplified for now
                errors: performanceMonitor?.getMetrics().errorRate * 100 || 0,
                performance: performanceMonitor?.getMetrics(),
                azure: {
                    enabled: azureManager?.azureEnabled || false,
                    circuitBreakerOpen: azureManager?.circuitBreaker.isOpen || false
                }
            };
            sendResponse({ stats });
            return true;
        }
        
        // Handle configuration updates
        if (msg && msg.type === "config_updated") {
            if (catdamsConfig) {
                catdamsConfig.config = { ...catdamsConfig.config, ...msg.config };
                catdamsConfig.saveToStorage();
                catdamsLogger?.info("[CATDAMS] Configuration updated from popup");
            }
            sendResponse({ status: "updated" });
            return true;
        }
        
        // Handle ping requests
        if (msg && msg.type === "ping") {
            sendResponse({ 
                status: "alive", 
                timestamp: Date.now(),
                version: "3.0",
                components: {
                    azure: azureManager?.azureEnabled || false,
                    processing: processingManager ? true : false,
                    performance: performanceMonitor ? true : false
                }
            });
            return true;
        }
        
    } catch (error) {
        catdamsErrorHandler?.handleError(error, { operation: 'onMessage', msg });
        performanceMonitor?.recordError();
    }
});

// ====== Enhanced Installation Handler ======
chrome.runtime.onInstalled.addListener(() => {
    try {
        catdamsLogger?.info("CATDAMS Enhanced Sentinel Extension installed with Azure integration");
        
        // Initialize default configuration
        if (catdamsConfig) {
            catdamsConfig.saveToStorage();
        }
        
    } catch (error) {
        catdamsErrorHandler?.handleError(error, { operation: 'onInstalled' });
    }
});

// ====== Legacy Functions (Maintained for Compatibility) ======
function logThreatAnalysis(payload) {
    if (payload.threat_analysis && payload.threat_analysis.threats.length > 0) {
        catdamsLogger?.warn(`[CATDAMS][THREAT] ${payload.threat_analysis.severity} threat detected on ${payload.platform}:`, {
            threatTypes: payload.threat_analysis.threats.map(t => t.type),
            messagePreview: payload.message.substring(0, 100),
            sender: payload.sender,
            azureEnhanced: payload.threat_analysis.azure_enhancement || false
        });
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AzureIntegrationManager,
        MessageProcessingManager,
        EnhancedPerformanceMonitor
    };
} 