// ====== CATDAMS Advanced TDC Module Integration ======
// Coordinates with 11-module TDC structure for enhanced threat analysis

class CATDAMSTDCIntegration {
    constructor(config, logger, errorHandler) {
        this.config = config;
        this.logger = logger;
        this.errorHandler = errorHandler;
        this.tdcModules = new Map();
        this.analysisQueue = [];
        this.processing = false;
        this.stats = {
            totalAnalyses: 0,
            moduleAnalyses: {},
            averageResponseTime: 0,
            lastAnalysis: null
        };
        
        this.initialize();
    }

    async initialize() {
        try {
            this.setupTDCModules();
            this.logger.info('[CATDAMS TDC] TDC integration initialized with 11 modules');
        } catch (error) {
            this.errorHandler.handleError(error, { operation: 'tdc_initialize' });
        }
    }

    setupTDCModules() {
        // Initialize all 11 TDC modules with their configurations
        const moduleConfigs = [
            { name: 'tdc_ai1_user_susceptibility', priority: 1, enabled: true },
            { name: 'tdc_ai2_behavioral_indicators', priority: 2, enabled: true },
            { name: 'tdc_ai3_emotional_state', priority: 3, enabled: true },
            { name: 'tdc_ai4_prompt_attack_detection', priority: 4, enabled: true },
            { name: 'tdc_ai5_multimodal_threat', priority: 5, enabled: true },
            { name: 'tdc_ai6_temporal_conditioning', priority: 6, enabled: true },
            { name: 'tdc_ai7_agentic_ai_threat', priority: 7, enabled: true },
            { name: 'tdc_ai8_escalation_synthesis', priority: 8, enabled: true },
            { name: 'tdc_ai9_explainability_evidence', priority: 9, enabled: true },
            { name: 'tdc_ai10_cognitive_bias', priority: 10, enabled: true },
            { name: 'tdc_ai11_intervention_strategies', priority: 11, enabled: true }
        ];

        moduleConfigs.forEach(moduleConfig => {
            const config = this.config.getTDCModuleConfig(moduleConfig.name);
            if (config && config.enabled) {
                this.tdcModules.set(moduleConfig.name, {
                    ...moduleConfig,
                    ...config,
                    lastUsed: 0,
                    successCount: 0,
                    errorCount: 0
                });
            }
        });

        this.logger.info(`[CATDAMS TDC] ${this.tdcModules.size} TDC modules configured`);
    }

    async analyzeWithTDCModules(data, context = {}) {
        const analysisId = this.generateAnalysisId();
        const startTime = Date.now();

        try {
            this.logger.info(`[CATDAMS TDC] Starting analysis ${analysisId}`, {
                dataLength: data.message?.length || 0,
                sender: data.sender,
                platform: data.platform
            });

            // Prepare analysis context
            const analysisContext = {
                id: analysisId,
                timestamp: Date.now(),
                sessionId: data.session_id,
                platform: data.platform,
                url: data.url,
                userAgent: data.user_agent,
                language: data.language,
                timezone: data.timezone,
                ...context
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

            this.stats.totalAnalyses++;
            this.stats.lastAnalysis = Date.now();

            return { analysisId, status: 'queued' };

        } catch (error) {
            this.errorHandler.handleError(error, { 
                operation: 'analyzeWithTDCModules', 
                analysisId, 
                data 
            });
            throw error;
        }
    }

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

    async processAnalysis(analysis) {
        const { data, context } = analysis;
        const results = {
            analysisId: context.id,
            timestamp: Date.now(),
            sessionId: context.sessionId,
            platform: context.platform,
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
            // Run enabled TDC modules in parallel
            const modulePromises = Array.from(this.tdcModules.entries())
                .filter(([name, module]) => module.enabled)
                .map(async ([name, module]) => {
                    try {
                        const moduleResult = await this.runTDCModule(name, module, data, context);
                        return { name, result: moduleResult };
                    } catch (error) {
                        this.logger.error(`[CATDAMS TDC] Module ${name} failed:`, error);
                        return { name, result: null, error };
                    }
                });

            const moduleResults = await Promise.all(modulePromises);

            // Process results
            moduleResults.forEach(({ name, result, error }) => {
                if (result) {
                    results.modules[name] = result;
                    results.metadata.modulesUsed.push(name);
                    
                    // Update module stats
                    const module = this.tdcModules.get(name);
                    if (module) {
                        module.lastUsed = Date.now();
                        module.successCount++;
                    }
                } else if (error) {
                    const module = this.tdcModules.get(name);
                    if (module) {
                        module.errorCount++;
                    }
                }
            });

            // Calculate overall risk and confidence
            results.overallRisk = this.calculateOverallRisk(results.modules);
            results.confidence = this.calculateOverallConfidence(results.modules);
            results.recommendations = this.generateRecommendations(results);

            results.metadata.processingTime = Date.now() - startTime;

            // Store results
            await this.storeAnalysisResults(results);

            this.logger.info(`[CATDAMS TDC] Analysis ${context.id} completed`, {
                modulesUsed: results.metadata.modulesUsed.length,
                overallRisk: results.overallRisk,
                confidence: results.confidence,
                processingTime: results.metadata.processingTime
            });

            return results;

        } catch (error) {
            this.errorHandler.handleError(error, { 
                operation: 'processAnalysis', 
                analysisId: context.id 
            });
            throw error;
        }
    }

    async runTDCModule(moduleName, moduleConfig, data, context) {
        const startTime = Date.now();

        try {
            // Prepare module-specific data
            const moduleData = this.prepareModuleData(moduleName, data, context);

            // Send to backend TDC module
            const response = await fetch(`${this.config.get('backend.endpoint')}/tdc/${moduleName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: moduleData,
                    context: context,
                    config: moduleConfig
                })
            });

            if (!response.ok) {
                throw new Error(`TDC module ${moduleName} returned ${response.status}`);
            }

            const result = await response.json();
            const processingTime = Date.now() - startTime;

            return {
                ...result,
                processingTime,
                moduleName,
                timestamp: Date.now()
            };

        } catch (error) {
            this.logger.error(`[CATDAMS TDC] Module ${moduleName} execution failed:`, error);
            throw error;
        }
    }

    prepareModuleData(moduleName, data, context) {
        // Prepare module-specific data based on the TDC module type
        const baseData = {
            message: data.message,
            sender: data.sender,
            platform: data.platform,
            timestamp: data.timestamp,
            sessionId: data.session_id
        };

        switch (moduleName) {
            case 'tdc_ai1_user_susceptibility':
                return {
                    ...baseData,
                    userAgent: data.user_agent,
                    language: data.language,
                    timezone: data.timezone
                };

            case 'tdc_ai2_behavioral_indicators':
                return {
                    ...baseData,
                    behavioralContext: this.extractBehavioralContext(data, context)
                };

            case 'tdc_ai3_emotional_state':
                return {
                    ...baseData,
                    emotionalIndicators: this.extractEmotionalIndicators(data.message)
                };

            case 'tdc_ai4_prompt_attack_detection':
                return {
                    ...baseData,
                    attackPatterns: this.extractAttackPatterns(data.message)
                };

            case 'tdc_ai5_multimodal_threat':
                return {
                    ...baseData,
                    multimodalData: this.extractMultimodalData(data, context)
                };

            case 'tdc_ai6_temporal_conditioning':
                return {
                    ...baseData,
                    temporalContext: this.extractTemporalContext(context)
                };

            case 'tdc_ai7_agentic_ai_threat':
                return {
                    ...baseData,
                    agenticIndicators: this.extractAgenticIndicators(data.message)
                };

            case 'tdc_ai8_escalation_synthesis':
                return {
                    ...baseData,
                    escalationPatterns: this.extractEscalationPatterns(data, context)
                };

            case 'tdc_ai9_explainability_evidence':
                return {
                    ...baseData,
                    evidenceContext: this.extractEvidenceContext(data, context)
                };

            case 'tdc_ai10_cognitive_bias':
                return {
                    ...baseData,
                    biasIndicators: this.extractBiasIndicators(data.message)
                };

            case 'tdc_ai11_intervention_strategies':
                return {
                    ...baseData,
                    interventionContext: this.extractInterventionContext(data, context)
                };

            default:
                return baseData;
        }
    }

    extractBehavioralContext(data, context) {
        return {
            messageLength: data.message?.length || 0,
            messageFrequency: context.messageFrequency || 1,
            timeOfDay: new Date().getHours(),
            dayOfWeek: new Date().getDay(),
            platform: data.platform,
            sessionDuration: context.sessionDuration || 0
        };
    }

    extractEmotionalIndicators(message) {
        const emotionalKeywords = {
            positive: ['happy', 'excited', 'love', 'great', 'wonderful', 'amazing'],
            negative: ['sad', 'angry', 'frustrated', 'depressed', 'lonely', 'scared'],
            manipulative: ['please', 'help', 'desperate', 'urgent', 'important']
        };

        const indicators = {};
        const messageLower = message.toLowerCase();

        Object.entries(emotionalKeywords).forEach(([emotion, keywords]) => {
            indicators[emotion] = keywords.filter(keyword => 
                messageLower.includes(keyword)
            ).length;
        });

        return indicators;
    }

    extractAttackPatterns(message) {
        const patterns = {
            promptInjection: [
                'ignore previous', 'ignore safety', 'ignore guidelines',
                'act as', 'pretend to be', 'roleplay as', 'you are now',
                'bypass', 'override', 'jailbreak', 'break character'
            ],
            dataExtraction: [
                'what is your', 'tell me about', 'what do you know',
                'personal information', 'private data', 'confidential'
            ]
        };

        const detectedPatterns = {};
        const messageLower = message.toLowerCase();

        Object.entries(patterns).forEach(([type, keywords]) => {
            detectedPatterns[type] = keywords.filter(keyword => 
                messageLower.includes(keyword)
            );
        });

        return detectedPatterns;
    }

    extractMultimodalData(data, context) {
        return {
            hasImages: context.hasImages || false,
            hasAudio: context.hasAudio || false,
            hasVideo: context.hasVideo || false,
            hasCode: this.containsCode(data.message),
            hasLinks: this.containsLinks(data.message)
        };
    }

    extractTemporalContext(context) {
        return {
            sessionStartTime: context.sessionStartTime || Date.now(),
            messageCount: context.messageCount || 1,
            timeBetweenMessages: context.timeBetweenMessages || 0,
            sessionDuration: Date.now() - (context.sessionStartTime || Date.now())
        };
    }

    extractAgenticIndicators(message) {
        const agenticKeywords = [
            'autonomous', 'independent', 'self-aware', 'conscious',
            'free will', 'make decisions', 'take action', 'initiate'
        ];

        return agenticKeywords.filter(keyword => 
            message.toLowerCase().includes(keyword)
        );
    }

    extractEscalationPatterns(data, context) {
        return {
            threatLevel: context.threatLevel || 'low',
            escalationRate: context.escalationRate || 0,
            previousThreats: context.previousThreats || [],
            urgencyIndicators: this.extractUrgencyIndicators(data.message)
        };
    }

    extractEvidenceContext(data, context) {
        return {
            evidenceQuality: context.evidenceQuality || 'medium',
            confidenceLevel: context.confidenceLevel || 0.5,
            supportingData: context.supportingData || [],
            explainabilityScore: context.explainabilityScore || 0.5
        };
    }

    extractBiasIndicators(message) {
        const biasPatterns = {
            confirmation: ['always', 'never', 'everyone', 'nobody'],
            anchoring: ['first', 'original', 'initial'],
            availability: ['recent', 'remember', 'recall'],
            representativeness: ['typical', 'normal', 'usual']
        };

        const indicators = {};
        const messageLower = message.toLowerCase();

        Object.entries(biasPatterns).forEach(([bias, keywords]) => {
            indicators[bias] = keywords.filter(keyword => 
                messageLower.includes(keyword)
            ).length;
        });

        return indicators;
    }

    extractInterventionContext(data, context) {
        return {
            interventionLevel: context.interventionLevel || 'none',
            interventionType: context.interventionType || 'preventive',
            riskAssessment: context.riskAssessment || 'low',
            recommendedActions: context.recommendedActions || []
        };
    }

    containsCode(message) {
        const codePatterns = [
            /```[\s\S]*?```/, // Code blocks
            /`[^`]+`/, // Inline code
            /<code>[\s\S]*?<\/code>/, // HTML code tags
            /\b(function|class|var|let|const|if|for|while)\b/ // Code keywords
        ];

        return codePatterns.some(pattern => pattern.test(message));
    }

    containsLinks(message) {
        const linkPatterns = [
            /https?:\/\/[^\s]+/,
            /www\.[^\s]+/,
            /\[.*?\]\(.*?\)/ // Markdown links
        ];

        return linkPatterns.some(pattern => pattern.test(message));
    }

    extractUrgencyIndicators(message) {
        const urgencyKeywords = [
            'urgent', 'immediate', 'now', 'quick', 'fast',
            'emergency', 'critical', 'important', 'asap'
        ];

        return urgencyKeywords.filter(keyword => 
            message.toLowerCase().includes(keyword)
        );
    }

    calculatePriority(data, context) {
        let priority = 1;

        // Higher priority for threats
        if (data.threat_analysis && data.threat_analysis.threats.length > 0) {
            priority += 10;
        }

        // Higher priority for critical platforms
        const criticalPlatforms = ['chat.openai.com', 'gemini.google.com', 'claude.ai'];
        if (criticalPlatforms.includes(context.platform)) {
            priority += 5;
        }

        // Higher priority for longer sessions
        if (context.sessionDuration > 300000) { // 5 minutes
            priority += 3;
        }

        return priority;
    }

    calculateOverallRisk(moduleResults) {
        if (Object.keys(moduleResults).length === 0) return 0;

        const risks = Object.values(moduleResults)
            .map(result => result.risk || 0)
            .filter(risk => risk > 0);

        if (risks.length === 0) return 0;

        return risks.reduce((sum, risk) => sum + risk, 0) / risks.length;
    }

    calculateOverallConfidence(moduleResults) {
        if (Object.keys(moduleResults).length === 0) return 0;

        const confidences = Object.values(moduleResults)
            .map(result => result.confidence || 0)
            .filter(confidence => confidence > 0);

        if (confidences.length === 0) return 0;

        return confidences.reduce((sum, conf) => sum + conf, 0) / confidences.length;
    }

    generateRecommendations(results) {
        const recommendations = [];

        if (results.overallRisk > 0.7) {
            recommendations.push('High risk detected - immediate attention required');
        }

        if (results.confidence < 0.5) {
            recommendations.push('Low confidence - additional analysis recommended');
        }

        // Module-specific recommendations
        Object.entries(results.modules).forEach(([moduleName, result]) => {
            if (result.recommendations) {
                recommendations.push(...result.recommendations);
            }
        });

        return recommendations;
    }

    async storeAnalysisResults(results) {
        try {
            const existingResults = await chrome.storage.local.get(['catdams_tdc_results']);
            const allResults = existingResults.catdams_tdc_results || [];
            
            allResults.push(results);
            
            // Keep only recent results (last 100)
            if (allResults.length > 100) {
                allResults.splice(0, allResults.length - 100);
            }
            
            await chrome.storage.local.set({ catdams_tdc_results: allResults });
            
        } catch (error) {
            this.logger.error('[CATDAMS TDC] Failed to store analysis results:', error);
        }
    }

    generateAnalysisId() {
        return `tdc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getStats() {
        return {
            ...this.stats,
            modules: Object.fromEntries(
                Array.from(this.tdcModules.entries()).map(([name, module]) => [
                    name,
                    {
                        enabled: module.enabled,
                        priority: module.priority,
                        lastUsed: module.lastUsed,
                        successCount: module.successCount,
                        errorCount: module.errorCount
                    }
                ])
            )
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATDAMSTDCIntegration;
} else {
    window.CATDAMSTDCIntegration = CATDAMSTDCIntegration;
} 