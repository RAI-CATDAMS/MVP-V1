// CATDAMS Enhanced Background Script
// This file provides comprehensive threat detection and monitoring capabilities for the CATDAMS browser extension.

// Enhanced configuration with threat intelligence integration
const CONFIG = {
    // Core detection settings
    DETECTION_INTERVAL: 2000,
    SESSION_TIMEOUT: 300000, // 5 minutes
    MAX_RETRIES: 3,
    
    // Threat intelligence settings
    THREAT_INTELLIGENCE_ENABLED: true,
    TI_UPDATE_INTERVAL: 300000, // 5 minutes
    TI_CACHE_DURATION: 3600000, // 1 hour
    
    // Behavioral analysis settings
    BEHAVIORAL_ANALYSIS_ENABLED: true,
    BEHAVIORAL_THRESHOLD: 0.7,
    BEHAVIORAL_WINDOW: 60000, // 1 minute
    
    // Performance optimization
    PERFORMANCE_MONITORING: true,
    MEMORY_THRESHOLD: 50, // MB
    CPU_THRESHOLD: 80, // percentage
    
    // Enhanced logging
    LOG_LEVEL: 'info', // debug, info, warn, error
    LOG_TO_CONSOLE: true,
    LOG_TO_STORAGE: true,
    
    // Session management
    SESSION_PERSISTENCE: true,
    SESSION_ENCRYPTION: true,
    SESSION_COMPRESSION: true
};

// Enhanced threat intelligence cache
let threatIntelligenceCache = {
    signatures: new Map(),
    patterns: new Map(),
    indicators: new Map(),
    lastUpdate: 0,
    updateInProgress: false
};

// Enhanced session management
let activeSessions = new Map();
let sessionHistory = new Map();
let behavioralData = new Map();

// Enhanced performance monitoring
let performanceMetrics = {
    memoryUsage: 0,
    cpuUsage: 0,
    detectionLatency: [],
    falsePositiveRate: 0,
    threatDetectionRate: 0,
    lastOptimization: Date.now()
};

// Enhanced threat detection engine
class EnhancedThreatDetector {
    constructor() {
        this.detectionModules = new Map();
        this.analysisQueue = [];
        this.processing = false;
        this.stats = {
            totalDetections: 0,
            truePositives: 0,
            falsePositives: 0,
            processingTime: 0
        };
    }

    // Initialize all detection modules
    async initialize() {
        console.log('[CATDAMS] Initializing enhanced threat detection engine...');
        
        // Core detection modules
        this.detectionModules.set('tdc_ai1', new TDCAI1Module());
        this.detectionModules.set('tdc_ai2', new TDCAI2Module());
        this.detectionModules.set('tdc_ai3', new TDCAI3Module());
        this.detectionModules.set('tdc_ai4', new TDCAI4Module());
        this.detectionModules.set('tdc_ai5', new TDCAI5Module());
        this.detectionModules.set('tdc_ai6', new TDCAI6Module());
        this.detectionModules.set('tdc_ai7', new TDCAI7Module());
        this.detectionModules.set('tdc_ai8', new TDCAI8Module());
        
        // Enhanced modules
        this.detectionModules.set('behavioral', new BehavioralAnalysisModule());
        this.detectionModules.set('sentiment', new SentimentAnalysisModule());
        this.detectionModules.set('temporal', new TemporalAnalysisModule());
        this.detectionModules.set('contextual', new ContextualAnalysisModule());
        
        // Initialize each module
        for (const [name, module] of this.detectionModules) {
            try {
                await module.initialize();
                console.log(`[CATDAMS] Module ${name} initialized successfully`);
            } catch (error) {
                console.error(`[CATDAMS] Failed to initialize module ${name}:`, error);
            }
        }
        
        console.log('[CATDAMS] Enhanced threat detection engine initialized');
    }

    // Enhanced threat analysis with multi-module coordination
    async analyzeThreat(data, context) {
        const startTime = Date.now();
        const analysisId = this.generateAnalysisId();
        
        console.log(`[CATDAMS] Starting enhanced threat analysis ${analysisId}`);
        
        try {
            // Prepare analysis context
            const analysisContext = {
                id: analysisId,
                timestamp: Date.now(),
                sessionId: context.sessionId,
                tabId: context.tabId,
                url: context.url,
                userAgent: context.userAgent,
                behavioralData: behavioralData.get(context.sessionId) || [],
                threatIntelligence: await this.getThreatIntelligence(),
                performance: performanceMetrics
            };
            
            // Queue analysis
            this.analysisQueue.push({
                data,
                context: analysisContext,
                priority: this.calculatePriority(data, analysisContext)
            });
            
            // Process queue if not already processing
            if (!this.processing) {
                await this.processAnalysisQueue();
            }
            
            this.stats.totalDetections++;
            this.stats.processingTime = Date.now() - startTime;
            
            return { analysisId, status: 'queued' };
            
        } catch (error) {
            console.error('[CATDAMS] Error in threat analysis:', error);
            throw error;
        }
    }

    // Process analysis queue with priority handling
    async processAnalysisQueue() {
        if (this.processing || this.analysisQueue.length === 0) return;
        
        this.processing = true;
        
        try {
            // Sort by priority
            this.analysisQueue.sort((a, b) => b.priority - a.priority);
            
            while (this.analysisQueue.length > 0) {
                const analysis = this.analysisQueue.shift();
                await this.processAnalysis(analysis);
                
                // Yield control to prevent blocking
                await new Promise(resolve => setTimeout(resolve, 10));
            }
        } finally {
            this.processing = false;
        }
    }

    // Process individual analysis with all modules
    async processAnalysis(analysis) {
        const { data, context } = analysis;
        const results = {
            analysisId: context.id,
            timestamp: Date.now(),
            sessionId: context.sessionId,
            tabId: context.tabId,
            url: context.url,
            modules: {},
            overallRisk: 0,
            confidence: 0,
            recommendations: [],
            metadata: {
                processingTime: 0,
                modulesUsed: [],
                threatIntelligenceUsed: false
            }
        };
        
        const startTime = Date.now();
        
        try {
            // Run all detection modules in parallel
            const modulePromises = Array.from(this.detectionModules.entries()).map(
                async ([name, module]) => {
                    try {
                        const moduleResult = await module.analyze(data, context);
                        return [name, moduleResult];
                    } catch (error) {
                        console.error(`[CATDAMS] Module ${name} analysis failed:`, error);
                        return [name, { error: error.message, risk: 0, confidence: 0 }];
                    }
                }
            );
            
            const moduleResults = await Promise.all(modulePromises);
            
            // Aggregate results
            let totalRisk = 0;
            let totalConfidence = 0;
            let moduleCount = 0;
            
            for (const [name, result] of moduleResults) {
                if (result && !result.error) {
                    results.modules[name] = result;
                    totalRisk += result.risk || 0;
                    totalConfidence += result.confidence || 0;
                    moduleCount++;
                    results.metadata.modulesUsed.push(name);
                }
            }
            
            // Calculate overall metrics
            if (moduleCount > 0) {
                results.overallRisk = totalRisk / moduleCount;
                results.confidence = totalConfidence / moduleCount;
            }
            
            // Generate recommendations
            results.recommendations = this.generateRecommendations(results);
            
            // Update behavioral data
            this.updateBehavioralData(context.sessionId, results);
            
            // Store results
            await this.storeAnalysisResults(results);
            
            // Send to dashboard
            await this.sendToDashboard(results);
            
            results.metadata.processingTime = Date.now() - startTime;
            
            console.log(`[CATDAMS] Analysis ${context.id} completed in ${results.metadata.processingTime}ms`);
            
        } catch (error) {
            console.error(`[CATDAMS] Analysis ${context.id} failed:`, error);
            results.error = error.message;
        }
        
        return results;
    }

    // Calculate analysis priority based on data characteristics
    calculatePriority(data, context) {
        let priority = 1;
        
        // Higher priority for suspicious patterns
        if (data.content && data.content.includes('threat')) priority += 5;
        if (data.content && data.content.includes('attack')) priority += 5;
        if (data.content && data.content.includes('exploit')) priority += 5;
        
        // Higher priority for high-risk sessions
        const sessionData = behavioralData.get(context.sessionId);
        if (sessionData && sessionData.riskLevel > 0.7) priority += 3;
        
        // Higher priority for new sessions
        if (!sessionData) priority += 2;
        
        return priority;
    }

    // Generate actionable recommendations
    generateRecommendations(results) {
        const recommendations = [];
        
        if (results.overallRisk > 0.8) {
            recommendations.push({
                type: 'high_risk',
                action: 'immediate_block',
                description: 'High-risk activity detected. Consider blocking this session.',
                priority: 'critical'
            });
        }
        
        if (results.overallRisk > 0.6) {
            recommendations.push({
                type: 'medium_risk',
                action: 'monitor_closely',
                description: 'Suspicious activity detected. Monitor this session closely.',
                priority: 'high'
            });
        }
        
        // Module-specific recommendations
        for (const [moduleName, moduleResult] of Object.entries(results.modules)) {
            if (moduleResult.recommendations) {
                recommendations.push(...moduleResult.recommendations);
            }
        }
        
        return recommendations;
    }

    // Update behavioral data for session
    updateBehavioralData(sessionId, results) {
        if (!behavioralData.has(sessionId)) {
            behavioralData.set(sessionId, {
                startTime: Date.now(),
                activities: [],
                riskLevel: 0,
                patterns: new Set(),
                anomalies: []
            });
        }
        
        const sessionData = behavioralData.get(sessionId);
        sessionData.activities.push({
            timestamp: Date.now(),
            risk: results.overallRisk,
            confidence: results.confidence,
            modules: Object.keys(results.modules)
        });
        
        // Update risk level
        const recentActivities = sessionData.activities.slice(-10);
        sessionData.riskLevel = recentActivities.reduce((sum, activity) => sum + activity.risk, 0) / recentActivities.length;
        
        // Detect patterns
        if (results.overallRisk > 0.5) {
            sessionData.patterns.add('high_risk_activity');
        }
        
        // Detect anomalies
        if (results.overallRisk > sessionData.riskLevel * 2) {
            sessionData.anomalies.push({
                timestamp: Date.now(),
                risk: results.overallRisk,
                description: 'Unusual spike in risk level'
            });
        }
    }

    // Store analysis results
    async storeAnalysisResults(results) {
        try {
            // Store in session history
            if (!sessionHistory.has(results.sessionId)) {
                sessionHistory.set(results.sessionId, []);
            }
            sessionHistory.get(results.sessionId).push(results);
            
            // Keep only recent history
            const history = sessionHistory.get(results.sessionId);
            if (history.length > 100) {
                history.splice(0, history.length - 100);
            }
            
            // Store in chrome.storage for persistence
            await chrome.storage.local.set({
                [`analysis_${results.analysisId}`]: results,
                [`session_${results.sessionId}`]: {
                    lastUpdate: Date.now(),
                    riskLevel: results.overallRisk,
                    analysisCount: history.length
                }
            });
            
        } catch (error) {
            console.error('[CATDAMS] Failed to store analysis results:', error);
        }
    }

    // Send results to dashboard
    async sendToDashboard(results) {
        try {
            // Send to all dashboard tabs
            const tabs = await chrome.tabs.query({ url: '*://*/dashboard*' });
            
            for (const tab of tabs) {
                try {
                    await chrome.tabs.sendMessage(tab.id, {
                        type: 'CATDAMS_ANALYSIS_RESULT',
                        data: results
                    });
                } catch (error) {
                    console.warn(`[CATDAMS] Failed to send to dashboard tab ${tab.id}:`, error);
                }
            }
            
        } catch (error) {
            console.error('[CATDAMS] Failed to send results to dashboard:', error);
        }
    }

    // Get threat intelligence data
    async getThreatIntelligence() {
        if (!CONFIG.THREAT_INTELLIGENCE_ENABLED) {
            return null;
        }
        
        // Check if cache is valid
        if (Date.now() - threatIntelligenceCache.lastUpdate < CONFIG.TI_CACHE_DURATION) {
            return threatIntelligenceCache;
        }
        
        // Update threat intelligence
        if (!threatIntelligenceCache.updateInProgress) {
            threatIntelligenceCache.updateInProgress = true;
            
            try {
                // Fetch from threat intelligence sources
                const tiData = await this.fetchThreatIntelligence();
                threatIntelligenceCache = { ...threatIntelligenceCache, ...tiData };
                threatIntelligenceCache.lastUpdate = Date.now();
                
                console.log('[CATDAMS] Threat intelligence updated');
            } catch (error) {
                console.error('[CATDAMS] Failed to update threat intelligence:', error);
            } finally {
                threatIntelligenceCache.updateInProgress = false;
            }
        }
        
        return threatIntelligenceCache;
    }

    // Fetch threat intelligence from external sources
    async fetchThreatIntelligence() {
        // This would integrate with actual threat intelligence APIs
        // For now, return mock data
        return {
            signatures: new Map([
                ['malware_pattern_1', { type: 'malware', confidence: 0.9, description: 'Known malware pattern' }],
                ['phishing_pattern_1', { type: 'phishing', confidence: 0.8, description: 'Phishing attempt pattern' }],
                ['exploit_pattern_1', { type: 'exploit', confidence: 0.85, description: 'Exploit attempt pattern' }]
            ]),
            patterns: new Map([
                ['suspicious_behavior_1', { type: 'behavioral', confidence: 0.7, description: 'Suspicious user behavior' }],
                ['data_exfiltration_1', { type: 'data_exfiltration', confidence: 0.9, description: 'Data exfiltration attempt' }]
            ]),
            indicators: new Map([
                ['ip_blacklist_1', { type: 'ip', confidence: 0.95, description: 'Known malicious IP' }],
                ['domain_blacklist_1', { type: 'domain', confidence: 0.9, description: 'Known malicious domain' }]
            ])
        };
    }

    // Generate unique analysis ID
    generateAnalysisId() {
        return `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get detection statistics
    getStats() {
        return {
            ...this.stats,
            queueLength: this.analysisQueue.length,
            processing: this.processing,
            modulesCount: this.detectionModules.size
        };
    }
}

// Enhanced detection modules
class TDCAI1Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI1 Module initialized');
    }
    
    async analyze(data, context) {
        // Risk analysis implementation
        const risk = this.calculateRisk(data);
        const confidence = this.calculateConfidence(data);
        
        return {
            risk,
            confidence,
            type: 'risk_analysis',
            details: {
                riskFactors: this.identifyRiskFactors(data),
                mitigation: this.suggestMitigation(risk)
            }
        };
    }
    
    calculateRisk(data) {
        // Implement risk calculation logic
        return Math.random() * 0.5; // Placeholder
    }
    
    calculateConfidence(data) {
        return 0.8; // Placeholder
    }
    
    identifyRiskFactors(data) {
        return ['factor1', 'factor2']; // Placeholder
    }
    
    suggestMitigation(risk) {
        return risk > 0.7 ? 'immediate_action' : 'monitor';
    }
}

class TDCAI2Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI2 Module initialized');
    }
    
    async analyze(data, context) {
        // AIRS analysis implementation
        return {
            risk: Math.random() * 0.4,
            confidence: 0.75,
            type: 'airs_analysis',
            details: {
                airsScore: this.calculateAIRSScore(data),
                recommendations: this.generateAIRSRecommendations()
            }
        };
    }
    
    calculateAIRSScore(data) {
        return Math.random() * 100;
    }
    
    generateAIRSRecommendations() {
        return ['recommendation1', 'recommendation2'];
    }
}

class TDCAI3Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI3 Module initialized');
    }
    
    async analyze(data, context) {
        // Temporal analysis implementation
        return {
            risk: Math.random() * 0.3,
            confidence: 0.7,
            type: 'temporal_analysis',
            details: {
                temporalPatterns: this.analyzeTemporalPatterns(data),
                timeBasedRisk: this.calculateTimeBasedRisk()
            }
        };
    }
    
    analyzeTemporalPatterns(data) {
        return ['pattern1', 'pattern2'];
    }
    
    calculateTimeBasedRisk() {
        return Math.random() * 0.5;
    }
}

class TDCAI4Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI4 Module initialized');
    }
    
    async analyze(data, context) {
        // Deep analysis implementation
        return {
            risk: Math.random() * 0.6,
            confidence: 0.85,
            type: 'deep_analysis',
            details: {
                deepInsights: this.generateDeepInsights(data),
                complexityScore: this.calculateComplexityScore()
            }
        };
    }
    
    generateDeepInsights(data) {
        return ['insight1', 'insight2'];
    }
    
    calculateComplexityScore() {
        return Math.random() * 100;
    }
}

class TDCAI5Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI5 Module initialized');
    }
    
    async analyze(data, context) {
        // AMIC analysis implementation
        return {
            risk: Math.random() * 0.4,
            confidence: 0.8,
            type: 'amic_analysis',
            details: {
                amicScore: this.calculateAMICScore(data),
                contextAnalysis: this.analyzeContext()
            }
        };
    }
    
    calculateAMICScore(data) {
        return Math.random() * 100;
    }
    
    analyzeContext() {
        return ['context1', 'context2'];
    }
}

class TDCAI6Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI6 Module initialized');
    }
    
    async analyze(data, context) {
        // AIPC analysis implementation
        return {
            risk: Math.random() * 0.5,
            confidence: 0.75,
            type: 'aipc_analysis',
            details: {
                aipcScore: this.calculateAIPCScore(data),
                classification: this.classifyContent()
            }
        };
    }
    
    calculateAIPCScore(data) {
        return Math.random() * 100;
    }
    
    classifyContent() {
        return 'classification_result';
    }
}

class TDCAI7Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI7 Module initialized');
    }
    
    async analyze(data, context) {
        // AIRM analysis implementation
        return {
            risk: Math.random() * 0.4,
            confidence: 0.8,
            type: 'airm_analysis',
            details: {
                airmScore: this.calculateAIRMScore(data),
                riskMetrics: this.calculateRiskMetrics()
            }
        };
    }
    
    calculateAIRMScore(data) {
        return Math.random() * 100;
    }
    
    calculateRiskMetrics() {
        return {
            metric1: Math.random() * 100,
            metric2: Math.random() * 100
        };
    }
}

class TDCAI8Module {
    async initialize() {
        console.log('[CATDAMS] TDC AI8 Module initialized');
    }
    
    async analyze(data, context) {
        // Sentiment analysis implementation
        return {
            risk: Math.random() * 0.3,
            confidence: 0.7,
            type: 'sentiment_analysis',
            details: {
                sentiment: this.analyzeSentiment(data),
                emotionalIndicators: this.detectEmotionalIndicators()
            }
        };
    }
    
    analyzeSentiment(data) {
        return 'neutral'; // positive, negative, neutral
    }
    
    detectEmotionalIndicators() {
        return ['indicator1', 'indicator2'];
    }
}

class BehavioralAnalysisModule {
    async initialize() {
        console.log('[CATDAMS] Behavioral Analysis Module initialized');
    }
    
    async analyze(data, context) {
        const sessionData = behavioralData.get(context.sessionId);
        if (!sessionData) {
            return { risk: 0, confidence: 0.5, type: 'behavioral_analysis' };
        }
        
        const behavioralRisk = this.calculateBehavioralRisk(sessionData);
        
        return {
            risk: behavioralRisk,
            confidence: 0.8,
            type: 'behavioral_analysis',
            details: {
                behavioralPatterns: this.identifyPatterns(sessionData),
                anomalyScore: this.calculateAnomalyScore(sessionData),
                recommendations: this.generateBehavioralRecommendations(behavioralRisk)
            }
        };
    }
    
    calculateBehavioralRisk(sessionData) {
        return sessionData.riskLevel || 0;
    }
    
    identifyPatterns(sessionData) {
        return Array.from(sessionData.patterns);
    }
    
    calculateAnomalyScore(sessionData) {
        return sessionData.anomalies.length * 0.1;
    }
    
    generateBehavioralRecommendations(risk) {
        if (risk > 0.7) {
            return ['immediate_session_termination', 'user_notification'];
        } else if (risk > 0.4) {
            return ['enhanced_monitoring', 'behavioral_tracking'];
        }
        return ['continue_monitoring'];
    }
}

class SentimentAnalysisModule {
    async initialize() {
        console.log('[CATDAMS] Sentiment Analysis Module initialized');
    }
    
    async analyze(data, context) {
        const sentiment = this.analyzeSentiment(data.content || '');
        
        return {
            risk: this.calculateSentimentRisk(sentiment),
            confidence: 0.7,
            type: 'sentiment_analysis',
            details: {
                sentiment,
                emotionalIndicators: this.detectEmotionalIndicators(data.content || ''),
                riskFactors: this.identifySentimentRiskFactors(sentiment)
            }
        };
    }
    
    analyzeSentiment(content) {
        // Simple sentiment analysis
        const negativeWords = ['threat', 'attack', 'hack', 'exploit', 'malware'];
        const positiveWords = ['safe', 'secure', 'trust', 'help'];
        
        const negativeCount = negativeWords.filter(word => content.toLowerCase().includes(word)).length;
        const positiveCount = positiveWords.filter(word => content.toLowerCase().includes(word)).length;
        
        if (negativeCount > positiveCount) return 'negative';
        if (positiveCount > negativeCount) return 'positive';
        return 'neutral';
    }
    
    calculateSentimentRisk(sentiment) {
        switch (sentiment) {
            case 'negative': return 0.6;
            case 'neutral': return 0.3;
            case 'positive': return 0.1;
            default: return 0.3;
        }
    }
    
    detectEmotionalIndicators(content) {
        const indicators = [];
        if (content.includes('!')) indicators.push('exclamation');
        if (content.includes('?')) indicators.push('questioning');
        if (content.includes('...')) indicators.push('uncertainty');
        return indicators;
    }
    
    identifySentimentRiskFactors(sentiment) {
        if (sentiment === 'negative') {
            return ['hostile_tone', 'threatening_language'];
        }
        return [];
    }
}

class TemporalAnalysisModule {
    async initialize() {
        console.log('[CATDAMS] Temporal Analysis Module initialized');
    }
    
    async analyze(data, context) {
        const temporalRisk = this.calculateTemporalRisk(context);
        
        return {
            risk: temporalRisk,
            confidence: 0.75,
            type: 'temporal_analysis',
            details: {
                timeBasedPatterns: this.analyzeTimePatterns(context),
                sessionDuration: this.calculateSessionDuration(context),
                activityFrequency: this.calculateActivityFrequency(context)
            }
        };
    }
    
    calculateTemporalRisk(context) {
        const now = Date.now();
        const sessionStart = activeSessions.get(context.sessionId)?.startTime || now;
        const sessionDuration = now - sessionStart;
        
        // Higher risk for very long or very short sessions
        if (sessionDuration > 3600000) return 0.4; // > 1 hour
        if (sessionDuration < 60000) return 0.3; // < 1 minute
        
        return 0.2;
    }
    
    analyzeTimePatterns(context) {
        return ['pattern1', 'pattern2'];
    }
    
    calculateSessionDuration(context) {
        const session = activeSessions.get(context.sessionId);
        if (!session) return 0;
        return Date.now() - session.startTime;
    }
    
    calculateActivityFrequency(context) {
        const sessionData = behavioralData.get(context.sessionId);
        if (!sessionData) return 0;
        
        const recentActivities = sessionData.activities.filter(
            activity => Date.now() - activity.timestamp < 60000
        );
        
        return recentActivities.length;
    }
}

class ContextualAnalysisModule {
    async initialize() {
        console.log('[CATDAMS] Contextual Analysis Module initialized');
    }
    
    async analyze(data, context) {
        const contextualRisk = this.calculateContextualRisk(data, context);
        
        return {
            risk: contextualRisk,
            confidence: 0.8,
            type: 'contextual_analysis',
            details: {
                contextFactors: this.analyzeContextFactors(data, context),
                environmentalRisk: this.calculateEnvironmentalRisk(context),
                userContext: this.analyzeUserContext(context)
            }
        };
    }
    
    calculateContextualRisk(data, context) {
        let risk = 0.2; // Base risk
        
        // URL-based risk
        if (context.url && this.isSuspiciousURL(context.url)) {
            risk += 0.3;
        }
        
        // User agent risk
        if (context.userAgent && this.isSuspiciousUserAgent(context.userAgent)) {
            risk += 0.2;
        }
        
        // Content-based risk
        if (data.content && this.containsSuspiciousContent(data.content)) {
            risk += 0.3;
        }
        
        return Math.min(risk, 1.0);
    }
    
    isSuspiciousURL(url) {
        const suspiciousPatterns = [
            /\.xyz$/,
            /\.tk$/,
            /\.ml$/,
            /suspicious/,
            /malware/
        ];
        
        return suspiciousPatterns.some(pattern => pattern.test(url));
    }
    
    isSuspiciousUserAgent(userAgent) {
        const suspiciousPatterns = [
            /bot/i,
            /crawler/i,
            /spider/i,
            /scraper/i
        ];
        
        return suspiciousPatterns.some(pattern => pattern.test(userAgent));
    }
    
    containsSuspiciousContent(content) {
        const suspiciousKeywords = [
            'password',
            'credit card',
            'ssn',
            'social security',
            'bank account'
        ];
        
        return suspiciousKeywords.some(keyword => 
            content.toLowerCase().includes(keyword)
        );
    }
    
    analyzeContextFactors(data, context) {
        return ['factor1', 'factor2'];
    }
    
    calculateEnvironmentalRisk(context) {
        return Math.random() * 0.3;
    }
    
    analyzeUserContext(context) {
        return {
            sessionAge: this.calculateSessionAge(context),
            activityLevel: this.calculateActivityLevel(context)
        };
    }
    
    calculateSessionAge(context) {
        const session = activeSessions.get(context.sessionId);
        if (!session) return 0;
        return Date.now() - session.startTime;
    }
    
    calculateActivityLevel(context) {
        const sessionData = behavioralData.get(context.sessionId);
        if (!sessionData) return 'low';
        
        const activityCount = sessionData.activities.length;
        if (activityCount > 50) return 'high';
        if (activityCount > 20) return 'medium';
        return 'low';
    }
}

// Enhanced session management
class EnhancedSessionManager {
    constructor() {
        this.sessions = new Map();
        this.sessionTimeout = CONFIG.SESSION_TIMEOUT;
        this.cleanupInterval = setInterval(() => this.cleanupSessions(), 60000);
    }

    createSession(sessionId, context) {
        const session = {
            id: sessionId,
            startTime: Date.now(),
            lastActivity: Date.now(),
            context,
            status: 'active',
            metadata: {
                userAgent: context.userAgent,
                url: context.url,
                tabId: context.tabId
            }
        };
        
        this.sessions.set(sessionId, session);
        activeSessions.set(sessionId, session);
        
        console.log(`[CATDAMS] Session ${sessionId} created`);
        return session;
    }

    updateSession(sessionId, data) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.lastActivity = Date.now();
            session.data = data;
        }
    }

    endSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.status = 'ended';
            session.endTime = Date.now();
            
            // Store session summary
            this.storeSessionSummary(session);
            
            console.log(`[CATDAMS] Session ${sessionId} ended`);
        }
    }

    cleanupSessions() {
        const now = Date.now();
        const expiredSessions = [];
        
        for (const [sessionId, session] of this.sessions) {
            if (now - session.lastActivity > this.sessionTimeout) {
                expiredSessions.push(sessionId);
            }
        }
        
        for (const sessionId of expiredSessions) {
            this.endSession(sessionId);
            this.sessions.delete(sessionId);
            activeSessions.delete(sessionId);
        }
        
        if (expiredSessions.length > 0) {
            console.log(`[CATDAMS] Cleaned up ${expiredSessions.length} expired sessions`);
        }
    }

    async storeSessionSummary(session) {
        try {
            const summary = {
                id: session.id,
                startTime: session.startTime,
                endTime: session.endTime,
                duration: session.endTime - session.startTime,
                status: session.status,
                metadata: session.metadata,
                riskLevel: behavioralData.get(session.id)?.riskLevel || 0,
                activityCount: behavioralData.get(session.id)?.activities.length || 0
            };
            
            await chrome.storage.local.set({
                [`session_summary_${session.id}`]: summary
            });
            
        } catch (error) {
            console.error('[CATDAMS] Failed to store session summary:', error);
        }
    }

    getSession(sessionId) {
        return this.sessions.get(sessionId);
    }

    getAllSessions() {
        return Array.from(this.sessions.values());
    }
}

// Enhanced performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = performanceMetrics;
        this.monitoringInterval = setInterval(() => this.updateMetrics(), 30000);
    }

    async updateMetrics() {
        try {
            // Update memory usage
            if (chrome.system && chrome.system.memory) {
                const memoryInfo = await chrome.system.memory.getInfo();
                this.metrics.memoryUsage = memoryInfo.capacity - memoryInfo.availableCapacity;
            }
            
            // Update CPU usage (if available)
            if (chrome.system && chrome.system.cpu) {
                const cpuInfo = await chrome.system.cpu.getInfo();
                this.metrics.cpuUsage = this.calculateCPUUsage(cpuInfo);
            }
            
            // Check for performance issues
            this.checkPerformanceIssues();
            
        } catch (error) {
            console.error('[CATDAMS] Failed to update performance metrics:', error);
        }
    }

    calculateCPUUsage(cpuInfo) {
        // Simplified CPU usage calculation
        return Math.random() * 100; // Placeholder
    }

    checkPerformanceIssues() {
        const issues = [];
        
        if (this.metrics.memoryUsage > CONFIG.MEMORY_THRESHOLD) {
            issues.push('high_memory_usage');
        }
        
        if (this.metrics.cpuUsage > CONFIG.CPU_THRESHOLD) {
            issues.push('high_cpu_usage');
        }
        
        if (issues.length > 0) {
            console.warn('[CATDAMS] Performance issues detected:', issues);
            this.optimizePerformance();
        }
    }

    optimizePerformance() {
        console.log('[CATDAMS] Initiating performance optimization...');
        
        // Clear old cache entries
        this.clearOldCache();
        
        // Optimize detection engine
        this.optimizeDetectionEngine();
        
        this.metrics.lastOptimization = Date.now();
    }

    clearOldCache() {
        const now = Date.now();
        const maxAge = 3600000; // 1 hour
        
        // Clear old threat intelligence cache
        if (now - threatIntelligenceCache.lastUpdate > maxAge) {
            threatIntelligenceCache.signatures.clear();
            threatIntelligenceCache.patterns.clear();
            threatIntelligenceCache.indicators.clear();
        }
        
        // Clear old session history
        for (const [sessionId, history] of sessionHistory) {
            if (history.length > 50) {
                history.splice(0, history.length - 50);
            }
        }
    }

    optimizeDetectionEngine() {
        // Reduce detection frequency if performance is poor
        if (this.metrics.cpuUsage > 90) {
            CONFIG.DETECTION_INTERVAL = Math.min(CONFIG.DETECTION_INTERVAL * 1.5, 5000);
        }
    }

    getMetrics() {
        return { ...this.metrics };
    }
}

// Enhanced logging system
class EnhancedLogger {
    constructor() {
        this.logLevel = CONFIG.LOG_LEVEL;
        this.logToConsole = CONFIG.LOG_TO_CONSOLE;
        this.logToStorage = CONFIG.LOG_TO_STORAGE;
        this.logBuffer = [];
        this.maxBufferSize = 1000;
    }

    log(level, message, data = null) {
        const logEntry = {
            timestamp: Date.now(),
            level,
            message,
            data
        };
        
        if (this.shouldLog(level)) {
            if (this.logToConsole) {
                this.logToConsole(level, message, data);
            }
            
            if (this.logToStorage) {
                this.logBuffer.push(logEntry);
                
                if (this.logBuffer.length > this.maxBufferSize) {
                    this.flushLogBuffer();
                }
            }
        }
    }

    shouldLog(level) {
        const levels = { debug: 0, info: 1, warn: 2, error: 3 };
        return levels[level] >= levels[this.logLevel];
    }

    logToConsole(level, message, data) {
        const prefix = `[CATDAMS ${level.toUpperCase()}]`;
        if (data) {
            console[level](prefix, message, data);
        } else {
            console[level](prefix, message);
        }
    }

    async flushLogBuffer() {
        if (this.logBuffer.length === 0) return;
        
        try {
            const logs = [...this.logBuffer];
            this.logBuffer = [];
            
            await chrome.storage.local.set({
                [`logs_${Date.now()}`]: logs
            });
            
        } catch (error) {
            console.error('[CATDAMS] Failed to flush log buffer:', error);
        }
    }

    debug(message, data) { this.log('debug', message, data); }
    info(message, data) { this.log('info', message, data); }
    warn(message, data) { this.log('warn', message, data); }
    error(message, data) { this.log('error', message, data); }
}

// Global instances
let threatDetector;
let sessionManager;
let performanceMonitor;
let logger;

// Initialize enhanced background script
async function initializeEnhancedBackground() {
    console.log('[CATDAMS] Initializing enhanced background script...');
    
    try {
        // Initialize logger first
        logger = new EnhancedLogger();
        logger.info('Enhanced background script starting...');
        
        // Initialize core components
        threatDetector = new EnhancedThreatDetector();
        sessionManager = new EnhancedSessionManager();
        performanceMonitor = new PerformanceMonitor();
        
        // Initialize threat detector
        await threatDetector.initialize();
        
        // Load configuration
        await loadConfiguration();
        
        // Start monitoring
        startMonitoring();
        
        logger.info('Enhanced background script initialized successfully');
        
    } catch (error) {
        console.error('[CATDAMS] Failed to initialize enhanced background script:', error);
        throw error;
    }
}

// Load configuration from storage
async function loadConfiguration() {
    try {
        const stored = await chrome.storage.local.get('catdams_config');
        if (stored.catdams_config) {
            Object.assign(CONFIG, stored.catdams_config);
            logger.info('Configuration loaded from storage');
        }
    } catch (error) {
        logger.error('Failed to load configuration:', error);
    }
}

// Save configuration to storage
async function saveConfiguration() {
    try {
        await chrome.storage.local.set({ catdams_config: CONFIG });
        logger.info('Configuration saved to storage');
    } catch (error) {
        logger.error('Failed to save configuration:', error);
    }
}

// Start monitoring
function startMonitoring() {
    // Monitor tab updates
    chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
        if (changeInfo.status === 'complete' && tab.url) {
            await handleTabUpdate(tabId, tab);
        }
    });
    
    // Monitor tab removal
    chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
        handleTabRemoval(tabId);
    });
    
    // Monitor messages from content scripts
    chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
        await handleMessage(message, sender, sendResponse);
        return true; // Keep message channel open for async response
    });
    
    logger.info('Monitoring started');
}

// Handle tab updates
async function handleTabUpdate(tabId, tab) {
    try {
        const sessionId = generateSessionId(tabId);
        
        // Create or update session
        if (!sessionManager.getSession(sessionId)) {
            sessionManager.createSession(sessionId, {
                tabId,
                url: tab.url,
                userAgent: tab.userAgent,
                sessionId
            });
        } else {
            sessionManager.updateSession(sessionId, { url: tab.url });
        }
        
        // Analyze page content if available
        if (tab.url && tab.url.startsWith('http')) {
            await analyzePageContent(tabId, tab.url);
        }
        
    } catch (error) {
        logger.error('Error handling tab update:', error);
    }
}

// Handle tab removal
function handleTabRemoval(tabId) {
    try {
        const sessionId = generateSessionId(tabId);
        sessionManager.endSession(sessionId);
    } catch (error) {
        logger.error('Error handling tab removal:', error);
    }
}

// Handle messages from content scripts
async function handleMessage(message, sender, sendResponse) {
    try {
        switch (message.type) {
            case 'catdams_log':
                // Call the threat analysis pipeline with the payload
                const sessionId = sender.tab ? generateSessionId(sender.tab.id) : 'unknown-session';
                const context = {
                    sessionId,
                    tabId: sender.tab ? sender.tab.id : null,
                    url: sender.tab ? sender.tab.url : null,
                    userAgent: sender.tab ? sender.tab.userAgent : null
                };
                const result = await threatDetector.analyzeThreat(message.payload, context);
                // --- Begin robust backend POST logic (restored from old background.js) ---
                async function checkIfSessionFileExists() {
                    try {
                        const res = await fetch("http://localhost:3009/session-id");
                        return res.ok;
                    } catch (err) {
                        console.warn("[CATDAMS] Could not reach session bridge:", err.message);
                        return false;
                    }
                }
                function sendSessionIdToHelper(session_id) {
                    if (chrome.runtime && chrome.runtime.sendNativeMessage) {
                        chrome.runtime.sendNativeMessage(
                            "com.catdams.sessionhelper",
                            { session_id: session_id },
                            function(response) {
                                if (chrome.runtime.lastError) {
                                    console.error("[CATDAMS] Native message error:", chrome.runtime.lastError.message);
                                } else {
                                    console.log("[CATDAMS] Native message success:", response);
                                }
                            }
                        );
                    }
                }
                function logThreatAnalysis(payload) {
                    if (payload.threat_analysis && payload.threat_analysis.threats && payload.threat_analysis.threats.length > 0) {
                        console.warn(`[CATDAMS][THREAT] ${payload.severity} threat detected on ${payload.source}:`, {
                            threatTypes: payload.threat_analysis.threats.map(t => t.type),
                            messagePreview: payload.message ? payload.message.substring(0, 100) : '',
                            sender: payload.sender
                        });
                    }
                }
                async function handleCatdamsPost(payload) {
                    // Ensure session_id is populated
                    if (!payload.session_id || payload.session_id === "unknown-session") {
                        try {
                            const res = await fetch("http://localhost:3009/session-id");
                            if (res.ok) {
                                const sessionIdText = await res.text();
                                payload.session_id = sessionIdText.trim();
                                console.log("[CATDAMS] 🆔 Assigned session_id from bridge:", payload.session_id);
                            } else {
                                console.warn("[CATDAMS] ❌ Failed to fetch session_id from bridge");
                            }
                        } catch (err) {
                            console.error("[CATDAMS] ⚠️ Session ID fetch error:", err.message);
                        }
                    } else {
                        const exists = await checkIfSessionFileExists();
                        if (!exists) {
                            sendSessionIdToHelper(payload.session_id);
                        }
                    }
                    // Log threat analysis if present
                    logThreatAnalysis(payload);
                    // Send to backend
                    try {
                        const res = await fetch("http://localhost:8000/event", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(payload)
                        });
                        if ([200, 201, 202].includes(res.status)) {
                            const messagePreview = payload.message ? payload.message.substring(0, 50) : "[no message]";
                            console.log(`[CATDAMS Backend] ✅ POST success (${res.status}): ${payload.sender} \"${messagePreview}...\"`);
                            if (payload.threat_analysis && payload.threat_analysis.threats && payload.threat_analysis.threats.length > 0) {
                                console.warn(`[CATDAMS Backend] ⚠️ Threat data sent: ${payload.threat_analysis.threats.length} threats detected`);
                            }
                            return { status: res.status };
                        } else {
                            console.warn(`[CATDAMS Backend] ⚠️ Unexpected status: ${res.status}`);
                            return { status: res.status, error: `Unexpected status code: ${res.status}` };
                        }
                    } catch (error) {
                        console.error("[CATDAMS Backend] ❌ Network error:", error.message);
                        return { status: "error", error: error.message };
                    }
                }
                // --- End robust backend POST logic ---
                const backendResponse = await handleCatdamsPost(message.payload);
                sendResponse({ ...result, backend: backendResponse });
                break;

            case 'CATDAMS_ANALYZE_CONTENT':
                await handleContentAnalysis(message.data, sender, sendResponse);
                break;
                
            case 'CATDAMS_GET_SESSION_INFO':
                handleSessionInfoRequest(message.sessionId, sendResponse);
                break;
                
            case 'CATDAMS_GET_STATS':
                handleStatsRequest(sendResponse);
                break;
                
            case 'CATDAMS_UPDATE_CONFIG':
                await handleConfigUpdate(message.config, sendResponse);
                break;
                
            default:
                logger.warn('Unknown message type:', message.type);
                sendResponse({ error: 'Unknown message type' });
        }
    } catch (error) {
        logger.error('Error handling message:', error);
        sendResponse({ error: error.message });
    }
}

// Handle content analysis requests
async function handleContentAnalysis(data, sender, sendResponse) {
    try {
        const sessionId = generateSessionId(sender.tab.id);
        const context = {
            sessionId,
            tabId: sender.tab.id,
            url: sender.tab.url,
            userAgent: sender.tab.userAgent
        };
        
        const result = await threatDetector.analyzeThreat(data, context);
        sendResponse(result);
        
    } catch (error) {
        logger.error('Error in content analysis:', error);
        sendResponse({ error: error.message });
    }
}

// Handle session info requests
function handleSessionInfoRequest(sessionId, sendResponse) {
    try {
        const session = sessionManager.getSession(sessionId);
        const behavioral = behavioralData.get(sessionId);
        const history = sessionHistory.get(sessionId);
        
        sendResponse({
            session,
            behavioral,
            history: history ? history.slice(-10) : [] // Last 10 entries
        });
        
    } catch (error) {
        logger.error('Error getting session info:', error);
        sendResponse({ error: error.message });
    }
}

// Handle stats requests
function handleStatsRequest(sendResponse) {
    try {
        const stats = {
            threatDetector: threatDetector.getStats(),
            sessions: {
                active: sessionManager.getAllSessions().length,
                total: sessionHistory.size
            },
            performance: performanceMonitor.getMetrics(),
            behavioral: {
                totalSessions: behavioralData.size,
                highRiskSessions: Array.from(behavioralData.values()).filter(s => s.riskLevel > 0.7).length
            }
        };
        
        sendResponse(stats);
        
    } catch (error) {
        logger.error('Error getting stats:', error);
        sendResponse({ error: error.message });
    }
}

// Handle configuration updates
async function handleConfigUpdate(newConfig, sendResponse) {
    try {
        Object.assign(CONFIG, newConfig);
        await saveConfiguration();
        
        logger.info('Configuration updated:', newConfig);
        sendResponse({ success: true });
        
    } catch (error) {
        logger.error('Error updating configuration:', error);
        sendResponse({ error: error.message });
    }
}

// Analyze page content
async function analyzePageContent(tabId, url) {
    try {
        // Inject content script if not already present
        await chrome.scripting.executeScript({
            target: { tabId },
            files: ['content.js']
        });
        
        // Request content analysis
        await chrome.tabs.sendMessage(tabId, {
            type: 'CATDAMS_ANALYZE_PAGE',
            data: { url }
        });
        
    } catch (error) {
        logger.error('Error analyzing page content:', error);
    }
}

// Generate session ID
function generateSessionId(tabId) {
    return `session_${tabId}_${Date.now()}`;
}

// Initialize when extension loads
chrome.runtime.onStartup.addListener(initializeEnhancedBackground);
chrome.runtime.onInstalled.addListener(initializeEnhancedBackground);

// Handle extension startup
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedBackground);
} else {
    initializeEnhancedBackground();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EnhancedThreatDetector,
        EnhancedSessionManager,
        PerformanceMonitor,
        EnhancedLogger,
        CONFIG
    };
} 