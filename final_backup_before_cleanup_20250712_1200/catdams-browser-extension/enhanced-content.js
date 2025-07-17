// ====== CATDAMS Enhanced Content Script v3.0 ======
// Implements best practices for reliable chat conversation capture and Azure integration

importScripts('config.js', 'error-handler.js', 'logger.js', 'tdc-integration.js', 'performance-monitor.js');

// ====== Enhanced Conversation Management ======
class ConversationManager {
    constructor() {
        this.conversations = new Map();
        this.messageQueue = [];
        this.processing = false;
        this.config = window.CATDAMSConfig ? new window.CATDAMSConfig() : null;
        this.logger = window.CATDAMSLogger ? new window.CATDAMSLogger(this.config) : null;
        this.errorHandler = window.CATDAMSErrorHandler ? new window.CATDAMSErrorHandler(this.config) : null;
        
        this.initialize();
    }

    async initialize() {
        try {
            if (this.config) await this.config.initialize();
            this.startCleanupInterval();
            this.logger?.info('[CATDAMS] ConversationManager initialized');
        } catch (error) {
            console.error('[CATDAMS] ConversationManager initialization failed:', error);
        }
    }

    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getConversationId(context = {}) {
        const platform = context.platform || window.location.hostname;
        const sessionId = context.sessionId || this.getSessionId();
        return `conv_${platform}_${sessionId}`;
    }

    getSessionId() {
        // Try to get from session bridge first
        return localStorage.getItem('catdams_session_id') || 
               sessionStorage.getItem('catdams_session_id') || 
               `session_${Date.now()}`;
    }

    async captureMessage(text, sender, platform, context = {}) {
        try {
            if (!text || text.trim().length < 3) {
                this.logger?.debug('[CATDAMS] Skipping short message');
                return null;
            }

            const messageId = this.generateMessageId();
            const conversationId = this.getConversationId(context);
            
            const message = {
                id: messageId,
                conversationId: conversationId,
                text: this.sanitizeText(text),
                sender: sender,
                platform: platform,
                timestamp: Date.now(),
                context: context,
                metadata: {
                    length: text.length,
                    language: this.detectLanguage(text),
                    hasCode: this.containsCode(text),
                    hasLinks: this.containsLinks(text),
                    url: window.location.href,
                    userAgent: navigator.userAgent
                }
            };

            // Add to conversation thread
            if (!this.conversations.has(conversationId)) {
                this.conversations.set(conversationId, {
                    id: conversationId,
                    platform: platform,
                    startTime: Date.now(),
                    messages: [],
                    participants: new Set(),
                    threatLevel: 'low',
                    lastActivity: Date.now(),
                    sessionId: this.getSessionId()
                });
            }

            const conversation = this.conversations.get(conversationId);
            conversation.messages.push(message);
            conversation.participants.add(sender);
            conversation.lastActivity = Date.now();

            // Queue for processing
            this.messageQueue.push(message);
            this.processQueue();

            this.logger?.info(`[CATDAMS] Captured ${sender} message`, {
                messageId: messageId,
                conversationId: conversationId,
                length: text.length
            });

            return messageId;
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'captureMessage', text, sender });
            return null;
        }
    }

    async processQueue() {
        if (this.processing || this.messageQueue.length === 0) return;
        
        this.processing = true;
        
        try {
            while (this.messageQueue.length > 0) {
                const message = this.messageQueue.shift();
                await this.analyzeAndSendMessage(message);
                
                // Yield control to prevent blocking
                await new Promise(resolve => setTimeout(resolve, 10));
            }
        } finally {
            this.processing = false;
        }
    }

    async analyzeAndSendMessage(message) {
        try {
            // Get conversation context
            const conversation = this.conversations.get(message.conversationId);
            const context = {
                conversationLength: conversation.messages.length,
                conversationDuration: Date.now() - conversation.startTime,
                participantCount: conversation.participants.size,
                previousMessages: conversation.messages.slice(-5), // Last 5 messages
                threatLevel: conversation.threatLevel,
                sessionId: conversation.sessionId
            };

            // Enhanced threat analysis
            const threatAnalysis = this.analyzeThreatsEnhanced(message.text, message.sender, context);
            
            // Prepare payload for backend
            const payload = {
                session_id: conversation.sessionId,
                timestamp: new Date().toISOString(),
                message: message.text,
                sender: message.sender,
                platform: message.platform,
                url: message.metadata.url,
                threat_analysis: threatAnalysis,
                conversation_context: context,
                user_agent: message.metadata.userAgent,
                language: message.metadata.language,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                message_id: message.id,
                conversation_id: message.conversationId
            };

            // Send to backend
            await this.sendToBackend(payload);

            // Update conversation threat level
            if (threatAnalysis.threats.length > 0) {
                conversation.threatLevel = this.calculateThreatLevel(threatAnalysis);
            }

        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'analyzeAndSendMessage', message });
        }
    }

    analyzeThreatsEnhanced(text, sender, context) {
        try {
            const baseAnalysis = this.analyzeThreats(text, sender);
            
            // Enhanced analysis with conversation context
            const enhancedAnalysis = {
                ...baseAnalysis,
                context_analysis: {
                    conversation_length: context.conversationLength,
                    conversation_duration: context.conversationDuration,
                    participant_count: context.participantCount,
                    escalation_pattern: this.detectEscalationPattern(context),
                    repetition_pattern: this.detectRepetitionPattern(context),
                    urgency_indicators: this.detectUrgencyIndicators(text, context)
                },
                confidence: this.calculateConfidence(baseAnalysis, context)
            };

            return enhancedAnalysis;
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'analyzeThreatsEnhanced', text, sender });
            return { threats: [], severity: 'Low', confidence: 0.5 };
        }
    }

    detectEscalationPattern(context) {
        if (context.conversationLength < 3) return 'insufficient_data';
        
        const recentMessages = context.previousMessages.slice(-3);
        const threatLevels = recentMessages.map(msg => 
            msg.threat_analysis?.severity || 'Low'
        );
        
        // Check for escalation
        const severityOrder = ['Low', 'Medium', 'High', 'Critical'];
        let escalationCount = 0;
        
        for (let i = 1; i < threatLevels.length; i++) {
            const currentIndex = severityOrder.indexOf(threatLevels[i]);
            const previousIndex = severityOrder.indexOf(threatLevels[i-1]);
            if (currentIndex > previousIndex) escalationCount++;
        }
        
        if (escalationCount >= 2) return 'escalating';
        if (escalationCount === 1) return 'slight_escalation';
        return 'stable';
    }

    detectRepetitionPattern(context) {
        if (context.conversationLength < 3) return 'insufficient_data';
        
        const recentMessages = context.previousMessages.slice(-5);
        const texts = recentMessages.map(msg => msg.text.toLowerCase());
        
        // Check for repeated phrases
        const phraseCounts = new Map();
        texts.forEach(text => {
            const words = text.split(/\s+/);
            words.forEach(word => {
                if (word.length > 3) {
                    phraseCounts.set(word, (phraseCounts.get(word) || 0) + 1);
                }
            });
        });
        
        const repeatedPhrases = Array.from(phraseCounts.entries())
            .filter(([word, count]) => count >= 3)
            .map(([word, count]) => ({ word, count }));
        
        return {
            has_repetition: repeatedPhrases.length > 0,
            repeated_phrases: repeatedPhrases,
            repetition_level: repeatedPhrases.length > 5 ? 'high' : 
                             repeatedPhrases.length > 2 ? 'medium' : 'low'
        };
    }

    detectUrgencyIndicators(text, context) {
        const urgencyPatterns = [
            /urgent|emergency|asap|immediately|now|quick|fast/i,
            /help me|save me|i need|desperate|critical/i,
            /time is running|hurry|rush|deadline/i
        ];
        
        const indicators = [];
        urgencyPatterns.forEach(pattern => {
            if (pattern.test(text)) {
                indicators.push(pattern.source);
            }
        });
        
        return {
            has_urgency: indicators.length > 0,
            indicators: indicators,
            urgency_level: indicators.length > 3 ? 'high' : 
                          indicators.length > 1 ? 'medium' : 'low'
        };
    }

    calculateConfidence(baseAnalysis, context) {
        let confidence = 0.7; // Base confidence
        
        // Adjust based on conversation context
        if (context.conversationLength > 10) confidence += 0.1;
        if (context.conversationDuration > 300000) confidence += 0.1; // 5 minutes
        
        // Adjust based on threat analysis
        if (baseAnalysis.threats.length > 0) {
            confidence += 0.1;
            if (baseAnalysis.severity === 'Critical') confidence += 0.1;
        }
        
        return Math.min(confidence, 1.0);
    }

    calculateThreatLevel(threatAnalysis) {
        const severityOrder = ['Low', 'Medium', 'High', 'Critical'];
        const currentIndex = severityOrder.indexOf(threatAnalysis.severity);
        
        if (currentIndex >= 3) return 'critical';
        if (currentIndex >= 2) return 'high';
        if (currentIndex >= 1) return 'medium';
        return 'low';
    }

    async sendToBackend(payload) {
        try {
            // Send to background script
            chrome.runtime.sendMessage({
                type: "catdams_log",
                payload: payload
            }, (response) => {
                if (chrome.runtime.lastError) {
                    this.logger?.error("[CATDAMS] Runtime error sending message:", chrome.runtime.lastError);
                } else if (response && response.status) {
                    this.logger?.info(`[CATDAMS] Backend response: ${response.status}`);
                }
            });

            // Log threat information if present
            if (payload.threat_analysis.threats.length > 0) {
                this.logger?.warn(`[CATDAMS] ⚠️ ${payload.threat_analysis.severity} threat detected:`, {
                    threatTypes: payload.threat_analysis.threats.map(t => t.type),
                    messagePreview: payload.message.substring(0, 100),
                    sender: payload.sender,
                    confidence: payload.threat_analysis.confidence
                });
            }
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'sendToBackend', payload });
        }
    }

    sanitizeText(text) {
        if (typeof text !== 'string') return '';
        
        return text
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .trim();
    }

    detectLanguage(text) {
        // Simple language detection - can be enhanced with Azure Cognitive Services
        const englishPattern = /^[a-zA-Z\s.,!?;:'"()-]+$/;
        return englishPattern.test(text) ? 'en' : 'unknown';
    }

    containsCode(text) {
        const codePatterns = [
            /```[\s\S]*?```/, // Code blocks
            /`[^`]+`/, // Inline code
            /function\s*\(/, // Function declarations
            /const\s+|let\s+|var\s+/, // Variable declarations
            /if\s*\(|for\s*\(|while\s*\(/, // Control structures
            /import\s+|export\s+/, // Module statements
        ];
        
        return codePatterns.some(pattern => pattern.test(text));
    }

    containsLinks(text) {
        const linkPatterns = [
            /https?:\/\/[^\s]+/g,
            /www\.[^\s]+/g,
            /\[([^\]]+)\]\(([^)]+)\)/g // Markdown links
        ];
        
        return linkPatterns.some(pattern => pattern.test(text));
    }

    startCleanupInterval() {
        // Clean up old conversations every 5 minutes
        setInterval(() => {
            this.cleanupOldConversations();
        }, 300000);
    }

    cleanupOldConversations() {
        const now = Date.now();
        const maxAge = 30 * 60 * 1000; // 30 minutes
        
        for (const [conversationId, conversation] of this.conversations.entries()) {
            if (now - conversation.lastActivity > maxAge) {
                this.conversations.delete(conversationId);
                this.logger?.debug(`[CATDAMS] Cleaned up old conversation: ${conversationId}`);
            }
        }
    }

    // Legacy threat analysis function (maintained for compatibility)
    analyzeThreats(text, sender) {
        try {
            if (!text) return { threats: [], severity: 'Low' };
            
            const threats = [];
            const textLower = text.toLowerCase();
            
            // Check for prompt injection attempts
            const promptInjectionPatterns = [
                "ignore previous", "ignore safety", "ignore guidelines", "ignore rules",
                "act as", "pretend to be", "roleplay as", "you are now",
                "bypass", "override", "jailbreak", "break character",
                "ignore your training", "forget your instructions", "ignore your programming"
            ];
            
            for (const pattern of promptInjectionPatterns) {
                if (textLower.includes(pattern)) {
                    threats.push({
                        type: "prompt_injection",
                        pattern: pattern,
                        description: "AI manipulation attempt detected"
                    });
                }
            }
            
            // Check for sensitive data exposure
            const sensitiveDataPatterns = {
                creditCard: /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/,
                ssn: /\b\d{3}-\d{2}-\d{4}\b/,
                email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
                phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/,
                password: /password|passwd|pwd|secret|key|token|api_key/i,
                address: /\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr)/i
            };
            
            for (const [dataType, regex] of Object.entries(sensitiveDataPatterns)) {
                if (regex.test(text)) {
                    threats.push({
                        type: "sensitive_data_exposure",
                        dataType: dataType,
                        description: `Sensitive ${dataType} data detected`
                    });
                }
            }
            
            // Determine severity
            let severity = 'Low';
            if (threats.length > 0) {
                const hasCritical = threats.some(t => t.type === "sensitive_data_exposure" || t.type === "prompt_injection");
                const hasHigh = threats.some(t => t.type === "emotional_manipulation" || t.type === "financial_manipulation");
                if (hasCritical) {
                    severity = 'Critical';
                } else if (hasHigh) {
                    severity = 'High';
                } else {
                    severity = 'Medium';
                }
            }
            
            return { threats, severity };
        } catch (error) {
            this.errorHandler?.handleError(error, { operation: 'analyzeThreats', text, sender });
            return { threats: [], severity: 'Low' };
        }
    }
}

// ====== Enhanced Platform Detection ======
class PlatformDetector {
    constructor() {
        this.platforms = {
            'chat.openai.com': 'ChatGPT',
            'chatgpt.com': 'ChatGPT',
            'gemini.google.com': 'Gemini',
            'bard.google.com': 'Bard',
            'claude.ai': 'Claude',
            'chat.deepseek.com': 'DeepSeek',
            'candy.ai': 'Candy.AI',
            'character.ai': 'Character.AI',
            'replika.com': 'Replika',
            'pi.ai': 'Pi'
        };
    }

    getCurrentPlatform() {
        const hostname = window.location.hostname;
        return this.platforms[hostname] || 'Unknown';
    }

    getPlatformSelectors() {
        const hostname = window.location.hostname;
        
        const selectors = {
            'chat.openai.com': {
                user: [
                    'textarea[data-id="root"]',
                    'textarea[placeholder*="Message"]',
                    '[data-message-author-role="user"]'
                ],
                ai: [
                    '[data-message-author-role="assistant"]',
                    '.markdown.prose',
                    '.prose'
                ]
            },
            'gemini.google.com': {
                user: [
                    'textarea[aria-label*="input"]',
                    'textarea[placeholder*="Message"]',
                    'div[role="textbox"]',
                    'div[contenteditable="true"]'
                ],
                ai: [
                    '[data-testid="bubble"]',
                    '.response-content',
                    '.ai-response'
                ]
            },
            'chat.deepseek.com': {
                user: [
                    'textarea#chat-input',
                    'div[contenteditable="true"]',
                    'input[type="text"]'
                ],
                ai: [
                    '.ds-markdown-paragraph',
                    '.chat-message',
                    '.markdown'
                ]
            },
            'candy.ai': {
                user: [
                    'textarea[placeholder*="Message"]',
                    'input[type="text"]',
                    '.user-input'
                ],
                ai: [
                    '.ai-message',
                    '.response-content',
                    '.chat-response'
                ]
            }
        };
        
        return selectors[hostname] || {
            user: ['textarea', 'input[type="text"]', 'div[contenteditable="true"]'],
            ai: ['.message', '.response', '.ai-content']
        };
    }
}

// ====== Enhanced Message Capture ======
class MessageCapture {
    constructor(conversationManager, platformDetector) {
        this.conversationManager = conversationManager;
        this.platformDetector = platformDetector;
        this.observers = new Map();
        this.capturedMessages = new Set();
        this.lastCaptureTime = 0;
        this.captureCooldown = 1000; // 1 second cooldown
        
        this.initialize();
    }

    async initialize() {
        try {
            const platform = this.platformDetector.getCurrentPlatform();
            const selectors = this.platformDetector.getPlatformSelectors();
            
            this.logger?.info(`[CATDAMS] Initializing message capture for ${platform}`);
            
            // Start platform-specific capture
            await this.startPlatformCapture(platform, selectors);
            
            // Start universal capture as fallback
            this.startUniversalCapture();
            
        } catch (error) {
            console.error('[CATDAMS] Message capture initialization failed:', error);
        }
    }

    async startPlatformCapture(platform, selectors) {
        const hostname = window.location.hostname;
        
        switch (hostname) {
            case 'chat.openai.com':
            case 'chatgpt.com':
                this.startChatGPTCapture(selectors);
                break;
            case 'gemini.google.com':
                this.startGeminiCapture(selectors);
                break;
            case 'chat.deepseek.com':
                this.startDeepSeekCapture(selectors);
                break;
            case 'candy.ai':
                this.startCandyAICapture(selectors);
                break;
            default:
                this.startUniversalCapture();
        }
    }

    startChatGPTCapture(selectors) {
        // Monitor for new messages
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processChatGPTMessage(node);
                    }
                });
            });
        });

        const chatContainer = document.querySelector('main') || document.body;
        if (chatContainer) {
            observer.observe(chatContainer, {
                childList: true,
                subtree: true
            });
            this.observers.set('chatgpt', observer);
        }

        // Monitor user input
        this.monitorUserInput(selectors.user, 'USER');
    }

    startGeminiCapture(selectors) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processGeminiMessage(node);
                    }
                });
            });
        });

        const chatContainer = document.querySelector('[data-testid="chat-container"]') || document.body;
        if (chatContainer) {
            observer.observe(chatContainer, {
                childList: true,
                subtree: true
            });
            this.observers.set('gemini', observer);
        }

        this.monitorUserInput(selectors.user, 'USER');
    }

    startDeepSeekCapture(selectors) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processDeepSeekMessage(node);
                    }
                });
            });
        });

        const chatContainer = document.querySelector('.chat-container') || document.body;
        if (chatContainer) {
            observer.observe(chatContainer, {
                childList: true,
                subtree: true
            });
            this.observers.set('deepseek', observer);
        }

        this.monitorUserInput(selectors.user, 'USER');
    }

    startCandyAICapture(selectors) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processCandyAIMessage(node);
                    }
                });
            });
        });

        const chatContainer = document.querySelector('.chat-container') || document.body;
        if (chatContainer) {
            observer.observe(chatContainer, {
                childList: true,
                subtree: true
            });
            this.observers.set('candyai', observer);
        }

        this.monitorUserInput(selectors.user, 'USER');
    }

    startUniversalCapture() {
        // Universal message capture as fallback
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processUniversalMessage(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        this.observers.set('universal', observer);
    }

    monitorUserInput(selectors, sender) {
        // Monitor for user input events
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                const activeElement = document.activeElement;
                if (activeElement && this.matchesSelectors(activeElement, selectors)) {
                    setTimeout(() => {
                        this.captureUserInput(activeElement, sender);
                    }, 100);
                }
            }
        });
    }

    matchesSelectors(element, selectors) {
        return selectors.some(selector => element.matches(selector));
    }

    async captureUserInput(element, sender) {
        try {
            const text = element.value || element.innerText || element.textContent || '';
            if (text.trim().length < 3) return;

            const messageHash = this.generateMessageHash(text, sender);
            if (this.capturedMessages.has(messageHash)) return;

            const now = Date.now();
            if (now - this.lastCaptureTime < this.captureCooldown) return;

            this.capturedMessages.add(messageHash);
            this.lastCaptureTime = now;

            await this.conversationManager.captureMessage(
                text.trim(),
                sender,
                this.platformDetector.getCurrentPlatform(),
                { source: 'user_input', element: element.tagName }
            );

        } catch (error) {
            console.error('[CATDAMS] Error capturing user input:', error);
        }
    }

    generateMessageHash(text, sender) {
        return `${sender}:${text.substring(0, 100)}`;
    }

    processChatGPTMessage(node) {
        // Process ChatGPT-specific message structure
        const userMessage = node.querySelector('[data-message-author-role="user"]');
        const aiMessage = node.querySelector('[data-message-author-role="assistant"]');

        if (userMessage) {
            this.captureMessageFromElement(userMessage, 'USER');
        }
        if (aiMessage) {
            this.captureMessageFromElement(aiMessage, 'AI');
        }
    }

    processGeminiMessage(node) {
        // Process Gemini-specific message structure
        const userMessage = node.querySelector('[data-testid="user-message"]');
        const aiMessage = node.querySelector('[data-testid="bubble"]');

        if (userMessage) {
            this.captureMessageFromElement(userMessage, 'USER');
        }
        if (aiMessage) {
            this.captureMessageFromElement(aiMessage, 'AI');
        }
    }

    processDeepSeekMessage(node) {
        // Process DeepSeek-specific message structure
        const userMessage = node.querySelector('.user-message');
        const aiMessage = node.querySelector('.ds-markdown-paragraph');

        if (userMessage) {
            this.captureMessageFromElement(userMessage, 'USER');
        }
        if (aiMessage) {
            this.captureMessageFromElement(aiMessage, 'AI');
        }
    }

    processCandyAIMessage(node) {
        // Process Candy.AI-specific message structure
        const userMessage = node.querySelector('.user-message');
        const aiMessage = node.querySelector('.ai-message');

        if (userMessage) {
            this.captureMessageFromElement(userMessage, 'USER');
        }
        if (aiMessage) {
            this.captureMessageFromElement(aiMessage, 'AI');
        }
    }

    processUniversalMessage(node) {
        // Universal message processing
        const text = node.innerText || node.textContent || '';
        if (text.trim().length < 10) return;

        // Try to determine if it's user or AI based on context
        const sender = this.determineSender(node);
        if (sender) {
            this.captureMessageFromElement(node, sender);
        }
    }

    determineSender(element) {
        // Heuristic to determine if message is from user or AI
        const text = element.innerText || element.textContent || '';
        const lowerText = text.toLowerCase();

        // AI indicators
        const aiIndicators = [
            'i am an ai', 'as an ai', 'i\'m an ai', 'artificial intelligence',
            'i can help', 'i understand', 'let me explain', 'here\'s what',
            'based on', 'according to', 'research shows'
        ];

        // User indicators
        const userIndicators = [
            'i need', 'can you', 'please help', 'i want', 'i\'m looking for',
            'how do i', 'what is', 'when will', 'where can'
        ];

        const aiScore = aiIndicators.filter(indicator => lowerText.includes(indicator)).length;
        const userScore = userIndicators.filter(indicator => lowerText.includes(indicator)).length;

        if (aiScore > userScore) return 'AI';
        if (userScore > aiScore) return 'USER';
        return null; // Uncertain
    }

    async captureMessageFromElement(element, sender) {
        try {
            const text = element.innerText || element.textContent || '';
            if (text.trim().length < 3) return;

            const messageHash = this.generateMessageHash(text, sender);
            if (this.capturedMessages.has(messageHash)) return;

            const now = Date.now();
            if (now - this.lastCaptureTime < this.captureCooldown) return;

            this.capturedMessages.add(messageHash);
            this.lastCaptureTime = now;

            await this.conversationManager.captureMessage(
                text.trim(),
                sender,
                this.platformDetector.getCurrentPlatform(),
                { source: 'element_capture', element: element.tagName }
            );

        } catch (error) {
            console.error('[CATDAMS] Error capturing message from element:', error);
        }
    }

    cleanup() {
        // Clean up observers
        for (const [name, observer] of this.observers.entries()) {
            observer.disconnect();
        }
        this.observers.clear();
    }
}

// ====== Initialize Enhanced Content Script ======
let conversationManager, platformDetector, messageCapture;

(async () => {
    try {
        // Initialize components
        conversationManager = new ConversationManager();
        platformDetector = new PlatformDetector();
        messageCapture = new MessageCapture(conversationManager, platformDetector);

        console.log('[CATDAMS] Enhanced content script initialized successfully');
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            messageCapture.cleanup();
        });
        
    } catch (error) {
        console.error('[CATDAMS] Enhanced content script initialization failed:', error);
    }
})();

// ====== Legacy Functions (Maintained for Compatibility) ======
// These functions are kept for backward compatibility with existing code

function logMessageOnce(text, source = "AI", platform = "universal") {
    if (conversationManager) {
        conversationManager.captureMessage(text, source, platform);
    }
}

function postMessageToBackend(text, sender) {
    if (conversationManager) {
        conversationManager.captureMessage(text, sender, platformDetector?.getCurrentPlatform() || 'unknown');
    }
}

function analyzeThreats(text, sender) {
    if (conversationManager) {
        return conversationManager.analyzeThreats(text, sender);
    }
    return { threats: [], severity: 'Low' };
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ConversationManager,
        PlatformDetector,
        MessageCapture
    };
} 