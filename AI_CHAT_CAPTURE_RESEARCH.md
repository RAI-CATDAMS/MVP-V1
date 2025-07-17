# AI/Chatbot Interaction Capture - Deep Research & Best Practices

## 🔍 **Current State Analysis**

After extensive research of current AI chat platforms and browser extension techniques, here are the most reliable methods for capturing AI/chatbot interactions:

## 🎯 **Critical Success Factors for Message Capture**

### **1. Multi-Layer Capture Strategy**
The most reliable approach combines multiple capture methods:

#### **Layer 1: DOM Mutation Observer (Primary)**
```javascript
// Best practice: Scoped MutationObserver with debouncing
class MutationObserverCapture {
    constructor() {
        this.observers = new Map();
        this.debounceTimers = new Map();
        this.lastCaptureTime = 0;
        this.minInterval = 500; // 500ms minimum between captures
    }

    startCapture(platform) {
        const config = {
            childList: true,
            subtree: true,
            attributes: false, // Only watch for new nodes
            characterData: false
        };

        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            if (now - this.lastCaptureTime < this.minInterval) return;

            const hasRelevantChanges = mutations.some(mutation => 
                mutation.addedNodes.length > 0 && 
                this.isRelevantNode(mutation.addedNodes[0])
            );

            if (hasRelevantChanges) {
                this.debounceCapture(platform);
            }
        });

        const target = this.getTargetElement(platform);
        if (target) {
            observer.observe(target, config);
            this.observers.set(platform, observer);
        }
    }

    debounceCapture(platform) {
        clearTimeout(this.debounceTimers.get(platform));
        this.debounceTimers.set(platform, setTimeout(() => {
            this.captureMessages(platform);
            this.lastCaptureTime = Date.now();
        }, 200));
    }
}
```

#### **Layer 2: Event-Based Capture (Secondary)**
```javascript
// Capture user input events
class EventCapture {
    constructor() {
        this.inputElements = new Set();
        this.capturedInputs = new Set();
    }

    startInputCapture() {
        // Monitor for new input elements
        const inputObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.setupInputListeners(node);
                    }
                });
            });
        });

        inputObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Setup existing inputs
        this.setupExistingInputs();
    }

    setupInputListeners(element) {
        if (this.isInputElement(element) && !this.inputElements.has(element)) {
            this.inputElements.add(element);
            
            // Multiple event types for reliability
            ['keydown', 'input', 'change'].forEach(eventType => {
                element.addEventListener(eventType, (e) => {
                    this.handleInputEvent(e, element);
                }, { passive: true });
            });
        }
    }

    handleInputEvent(event, element) {
        if (event.key === 'Enter' && !event.shiftKey) {
            const text = this.extractText(element);
            if (text && !this.capturedInputs.has(text)) {
                this.capturedInputs.add(text);
                this.captureUserMessage(text);
            }
        }
    }
}
```

#### **Layer 3: Network Interception (Advanced)**
```javascript
// Intercept network requests for API-based chats
class NetworkCapture {
    constructor() {
        this.interceptedRequests = new Set();
    }

    startNetworkCapture() {
        // Use Service Worker for network interception
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('network-capture-sw.js');
        }

        // Fallback: Monitor fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            this.interceptFetchRequest(args[0], response);
            return response;
        };
    }

    interceptFetchRequest(url, response) {
        if (this.isChatAPI(url)) {
            response.clone().json().then(data => {
                this.extractMessagesFromAPI(data);
            }).catch(() => {});
        }
    }
}
```

## 🏗️ **Platform-Specific Optimizations**

### **ChatGPT (chat.openai.com)**
```javascript
class ChatGPTCapture {
    constructor() {
        this.selectors = {
            user: [
                '[data-message-author-role="user"]',
                '.markdown.prose.w-full.break-words',
                'div[data-message-author-role="user"]'
            ],
            ai: [
                '[data-message-author-role="assistant"]',
                '.markdown.prose.w-full.break-words',
                'div[data-message-author-role="assistant"]'
            ],
            input: [
                'textarea[data-id="root"]',
                'textarea[placeholder*="Message"]',
                'div[contenteditable="true"]'
            ]
        };
    }

    captureMessages() {
        // Capture user messages
        this.selectors.user.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isNewMessage(element)) {
                    const text = this.extractText(element);
                    this.captureUserMessage(text);
                }
            });
        });

        // Capture AI messages
        this.selectors.ai.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isCompleteMessage(element)) {
                    const text = this.extractText(element);
                    this.captureAIMessage(text);
                }
            });
        });
    }

    isCompleteMessage(element) {
        // Check if message is fully loaded
        return !element.querySelector('.animate-pulse') && 
               !element.querySelector('[data-testid="loading"]') &&
               element.textContent.trim().length > 10;
    }
}
```

### **Google Gemini (gemini.google.com)**
```javascript
class GeminiCapture {
    constructor() {
        this.selectors = {
            user: [
                'div[data-testid="user-message"]',
                '.user-query-container',
                'div[aria-label="User input"]'
            ],
            ai: [
                '[data-testid="bubble"]',
                '.response-content',
                '.ai-response',
                'div[data-testid="response"]'
            ],
            input: [
                'textarea[aria-label*="input"]',
                'div[role="textbox"]',
                'div[contenteditable="true"]'
            ]
        };
    }

    captureMessages() {
        // Gemini uses streaming responses, so we need to wait for completion
        this.selectors.ai.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isStreamingComplete(element)) {
                    const text = this.extractText(element);
                    this.captureAIMessage(text);
                }
            });
        });
    }

    isStreamingComplete(element) {
        // Check for streaming completion indicators
        return !element.querySelector('.typing-indicator') &&
               !element.querySelector('[data-testid="streaming"]') &&
               element.textContent.trim().length > 10;
    }
}
```

### **DeepSeek (chat.deepseek.com)**
```javascript
class DeepSeekCapture {
    constructor() {
        this.selectors = {
            user: [
                'textarea#chat-input',
                'div[contenteditable="true"]',
                '.user-message',
                '.human-message'
            ],
            ai: [
                '.ds-markdown-paragraph',
                '.chat-message',
                '.markdown',
                'div.ds-markdown-block'
            ],
            input: [
                'textarea#chat-input',
                'div[contenteditable="true"]',
                'input[type="text"]'
            ]
        };
    }

    captureMessages() {
        // DeepSeek has specific markdown rendering
        this.selectors.ai.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isMarkdownComplete(element)) {
                    const text = this.extractMarkdownText(element);
                    this.captureAIMessage(text);
                }
            });
        });
    }

    extractMarkdownText(element) {
        // Preserve markdown formatting for better analysis
        return element.innerHTML || element.textContent;
    }
}
```

## 🔧 **Advanced Capture Techniques**

### **1. Streaming Response Handling**
```javascript
class StreamingCapture {
    constructor() {
        this.streamingMessages = new Map();
        this.completionChecks = new Map();
    }

    handleStreamingMessage(platform, messageId, partialText) {
        if (!this.streamingMessages.has(messageId)) {
            this.streamingMessages.set(messageId, {
                platform,
                startTime: Date.now(),
                text: '',
                lastUpdate: Date.now()
            });
        }

        const message = this.streamingMessages.get(messageId);
        message.text = partialText;
        message.lastUpdate = Date.now();

        // Check for completion
        this.checkStreamingCompletion(messageId);
    }

    checkStreamingCompletion(messageId) {
        const message = this.streamingMessages.get(messageId);
        if (!message) return;

        const timeSinceUpdate = Date.now() - message.lastUpdate;
        
        // Consider complete if no updates for 2 seconds
        if (timeSinceUpdate > 2000) {
            this.captureCompleteMessage(message);
            this.streamingMessages.delete(messageId);
        }
    }
}
```

### **2. Message Deduplication**
```javascript
class MessageDeduplicator {
    constructor() {
        this.messageHashes = new Set();
        this.conversationHistory = new Map();
        this.hashAlgorithm = 'sha-256';
    }

    async generateMessageHash(text, sender, platform) {
        const data = `${sender}:${platform}:${text}`;
        const encoder = new TextEncoder();
        const dataBuffer = encoder.encode(data);
        const hashBuffer = await crypto.subtle.digest(this.hashAlgorithm, dataBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    async isDuplicate(text, sender, platform) {
        const hash = await this.generateMessageHash(text, sender, platform);
        return this.messageHashes.has(hash);
    }

    async addMessage(text, sender, platform) {
        const hash = await this.generateMessageHash(text, sender, platform);
        this.messageHashes.add(hash);
        
        // Cleanup old hashes (keep last 1000)
        if (this.messageHashes.size > 1000) {
            const hashes = Array.from(this.messageHashes);
            this.messageHashes.clear();
            hashes.slice(-500).forEach(h => this.messageHashes.add(h));
        }
    }
}
```

### **3. Conversation Context Preservation**
```javascript
class ConversationContext {
    constructor() {
        this.conversations = new Map();
        this.currentConversationId = null;
    }

    getConversationId(platform, sessionId) {
        return `${platform}_${sessionId}_${this.getDateKey()}`;
    }

    addMessage(conversationId, message) {
        if (!this.conversations.has(conversationId)) {
            this.conversations.set(conversationId, {
                id: conversationId,
                platform: message.platform,
                startTime: Date.now(),
                messages: [],
                participants: new Set(),
                context: {}
            });
        }

        const conversation = this.conversations.get(conversationId);
        conversation.messages.push(message);
        conversation.participants.add(message.sender);
        conversation.lastActivity = Date.now();

        // Update context
        this.updateConversationContext(conversation, message);
    }

    updateConversationContext(conversation, message) {
        // Track conversation patterns
        conversation.context.messageCount = conversation.messages.length;
        conversation.context.duration = Date.now() - conversation.startTime;
        conversation.context.lastSender = message.sender;
        
        // Track escalation patterns
        if (message.threat_analysis) {
            conversation.context.threatLevel = message.threat_analysis.severity;
            conversation.context.threatCount = (conversation.context.threatCount || 0) + 1;
        }
    }
}
```

## 🚀 **Performance Optimizations**

### **1. Efficient DOM Queries**
```javascript
class OptimizedDOMCapture {
    constructor() {
        this.cachedSelectors = new Map();
        this.queryCache = new Map();
        this.cacheTimeout = 5000; // 5 seconds
    }

    querySelector(selector, context = document) {
        const cacheKey = `${selector}_${context === document ? 'doc' : 'ctx'}`;
        const cached = this.queryCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.elements;
        }

        const elements = context.querySelectorAll(selector);
        this.queryCache.set(cacheKey, {
            elements: Array.from(elements),
            timestamp: Date.now()
        });

        return Array.from(elements);
    }

    clearCache() {
        const now = Date.now();
        for (const [key, value] of this.queryCache.entries()) {
            if (now - value.timestamp > this.cacheTimeout) {
                this.queryCache.delete(key);
            }
        }
    }
}
```

### **2. Batch Processing**
```javascript
class BatchProcessor {
    constructor() {
        this.messageQueue = [];
        this.processing = false;
        this.batchSize = 10;
        this.batchTimeout = 1000; // 1 second
    }

    addMessage(message) {
        this.messageQueue.push(message);
        
        if (this.messageQueue.length >= this.batchSize) {
            this.processBatch();
        } else if (!this.processing) {
            setTimeout(() => this.processBatch(), this.batchTimeout);
        }
    }

    async processBatch() {
        if (this.processing || this.messageQueue.length === 0) return;
        
        this.processing = true;
        const batch = this.messageQueue.splice(0, this.batchSize);
        
        try {
            // Process messages in parallel
            const promises = batch.map(message => this.processMessage(message));
            await Promise.allSettled(promises);
        } finally {
            this.processing = false;
            
            // Process remaining messages
            if (this.messageQueue.length > 0) {
                setTimeout(() => this.processBatch(), 100);
            }
        }
    }
}
```

## 🔒 **Reliability & Error Handling**

### **1. Graceful Degradation**
```javascript
class ReliableCapture {
    constructor() {
        this.captureMethods = [
            new MutationObserverCapture(),
            new EventCapture(),
            new NetworkCapture()
        ];
        this.fallbackMethod = new UniversalCapture();
        this.healthMonitor = new HealthMonitor();
    }

    startCapture(platform) {
        // Try primary methods first
        for (const method of this.captureMethods) {
            try {
                method.startCapture(platform);
                this.healthMonitor.recordSuccess(method.constructor.name);
            } catch (error) {
                this.healthMonitor.recordFailure(method.constructor.name, error);
            }
        }

        // Start fallback method
        this.fallbackMethod.startCapture(platform);
    }

    handleCaptureFailure(method, error) {
        console.warn(`[CATDAMS] Capture method ${method} failed:`, error);
        
        // Switch to fallback if primary methods are failing
        if (this.healthMonitor.getFailureRate(method) > 0.5) {
            this.activateFallback();
        }
    }
}
```

### **2. Health Monitoring**
```javascript
class HealthMonitor {
    constructor() {
        this.stats = new Map();
        this.alerts = [];
    }

    recordSuccess(method) {
        const stats = this.getStats(method);
        stats.successCount++;
        stats.lastSuccess = Date.now();
        this.updateSuccessRate(method);
    }

    recordFailure(method, error) {
        const stats = this.getStats(method);
        stats.failureCount++;
        stats.lastFailure = Date.now();
        stats.lastError = error.message;
        this.updateSuccessRate(method);
        
        if (this.getFailureRate(method) > 0.8) {
            this.raiseAlert(method, 'High failure rate');
        }
    }

    getFailureRate(method) {
        const stats = this.getStats(method);
        const total = stats.successCount + stats.failureCount;
        return total > 0 ? stats.failureCount / total : 0;
    }
}
```

## 📊 **Azure Integration Best Practices**

### **1. Optimized Payload Structure**
```javascript
class AzureOptimizedPayload {
    constructor() {
        this.azureServices = {
            textAnalytics: true,
            languageDetection: true,
            entityRecognition: true,
            piiDetection: true,
            sentimentAnalysis: true
        };
    }

    createPayload(message, context) {
        return {
            // Core message data
            session_id: context.sessionId,
            timestamp: new Date().toISOString(),
            message: message.text,
            sender: message.sender,
            platform: message.platform,
            url: window.location.href,
            
            // Azure-specific optimizations
            azure_services: this.azureServices,
            text_length: message.text.length,
            language_hint: this.detectLanguageHint(message.text),
            
            // Conversation context for Azure analysis
            conversation_context: {
                message_count: context.messageCount,
                conversation_duration: context.duration,
                previous_messages: context.previousMessages?.slice(-3) || [],
                threat_level: context.threatLevel
            },
            
            // Metadata for Azure processing
            metadata: {
                user_agent: navigator.userAgent,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                language: navigator.language,
                has_code: this.containsCode(message.text),
                has_links: this.containsLinks(message.text)
            }
        };
    }
}
```

### **2. Azure Service Coordination**
```javascript
class AzureServiceCoordinator {
    constructor() {
        this.services = {
            textAnalytics: new AzureTextAnalytics(),
            languageDetection: new AzureLanguageDetection(),
            entityRecognition: new AzureEntityRecognition(),
            piiDetection: new AzurePIIDetection(),
            sentimentAnalysis: new AzureSentimentAnalysis()
        };
        this.circuitBreakers = new Map();
    }

    async analyzeWithAzure(text, context) {
        const promises = [];
        
        // Parallel service calls
        if (this.services.textAnalytics.isEnabled()) {
            promises.push(this.services.textAnalytics.analyze(text));
        }
        
        if (this.services.languageDetection.isEnabled()) {
            promises.push(this.services.languageDetection.detect(text));
        }
        
        if (this.services.entityRecognition.isEnabled()) {
            promises.push(this.services.entityRecognition.extract(text));
        }
        
        if (this.services.piiDetection.isEnabled()) {
            promises.push(this.services.piiDetection.detect(text));
        }
        
        if (this.services.sentimentAnalysis.isEnabled()) {
            promises.push(this.services.sentimentAnalysis.analyze(text));
        }

        // Wait for all services with timeout
        const results = await Promise.allSettled(promises);
        return this.synthesizeResults(results, context);
    }

    synthesizeResults(results, context) {
        const successful = results.filter(r => r.status === 'fulfilled');
        const failed = results.filter(r => r.status === 'rejected');
        
        return {
            success_rate: successful.length / results.length,
            services_used: successful.length,
            services_failed: failed.length,
            results: successful.map(r => r.value),
            context: context,
            timestamp: Date.now()
        };
    }
}
```

## 🎯 **Implementation Priority**

### **Phase 1: Core Capture (Critical)**
1. **Multi-layer capture strategy** with MutationObserver + Event listeners
2. **Platform-specific optimizations** for major AI platforms
3. **Message deduplication** and conversation threading
4. **Basic error handling** and fallback mechanisms

### **Phase 2: Advanced Features**
1. **Streaming response handling** for real-time AI responses
2. **Network interception** for API-based chats
3. **Performance optimizations** with caching and batching
4. **Health monitoring** and reliability improvements

### **Phase 3: Azure Integration**
1. **Optimized payload structure** for Azure services
2. **Service coordination** with circuit breakers
3. **Advanced context preservation** for better analysis
4. **Performance monitoring** and optimization

## 📈 **Success Metrics**

### **Capture Reliability:**
- ✅ Message capture accuracy: >99%
- ✅ No duplicate messages
- ✅ Complete conversation context
- ✅ Real-time capture with <500ms latency

### **Performance:**
- ✅ Memory usage: <50MB
- ✅ CPU usage: <10%
- ✅ No impact on page performance
- ✅ Graceful degradation under load

### **Azure Integration:**
- ✅ 100% payload compatibility with Azure Cognitive Services
- ✅ Optimized for Azure OpenAI analysis
- ✅ Circuit breaker protection
- ✅ Fallback mechanisms when Azure unavailable

This research provides the most reliable and comprehensive approach to capturing AI/chatbot interactions while maintaining compatibility with Azure Cognitive Services and Azure OpenAI for your CATDAMS threat detection system. 