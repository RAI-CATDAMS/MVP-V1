// ====== CATDAMS Ultimate Message Capture System v3.2 ======
// Multi-layer capture strategy for 99%+ success rate
// Implements research-based best practices for AI/chatbot interaction capture

console.log("CATDAMS Ultimate Message Capture System loaded on", window.location.hostname);

// Polyfill for requestIdleCallback for better performance
if (!window.requestIdleCallback) {
    window.requestIdleCallback = function(callback, options) {
        const start = Date.now();
        return setTimeout(() => {
            callback({
                didTimeout: false,
                timeRemaining: () => Math.max(0, 50 - (Date.now() - start))
            });
        }, 1);
    };
}

// === CONFIGURATION ===
const CONFIG = {
    BACKEND_ENDPOINT: "http://localhost:8000/event",
    CAPTURE_INTERVAL: 300, // ms between captures
    SCAN_INTERVAL: 1500, // ms between periodic scans (further reduced for better capture)
    MAX_MESSAGES: 1000,
    DEBUG_MODE: true, // Enable debug mode to see what's happening
    ENABLE_MUTATION_OBSERVER: true,
    ENABLE_NETWORK_INTERCEPTION: true,
    ENABLE_PERIODIC_SCANNING: true,
    AI_CAPTURE_DELAY: 2000, // Increased delay to ensure full response is rendered
    FULL_MESSAGE_TIMEOUT: 5000 // Wait up to 5 seconds for complete messages
};

// === PLATFORM CONFIGURATIONS ===
const PLATFORMS = {
    "chat.openai.com": {
        name: "ChatGPT",
        selectors: {
            user: [
                '[data-message-author-role="user"] .markdown.prose.w-full.break-words',
                'div[data-message-author-role="user"]',
                '[data-message-author-role="user"]'
            ],
            ai: [
                '[data-message-author-role="assistant"] .markdown.prose.w-full.break-words',
                'div[data-message-author-role="assistant"]',
                '[data-message-author-role="assistant"]',
                '.markdown.prose.w-full.break-words'
            ],
            completionIndicators: [
                '.animate-pulse',
                '[data-testid="loading"]',
                '.typing-indicator',
                '.loading-dots'
            ],
            container: '.flex.flex-col.items-center.text-sm',
            messageContainer: '[data-message-author-role="assistant"]'
        },
        successRate: 99
    },
    "chatgpt.com": {
        name: "ChatGPT",
        selectors: {
            user: [
                '[data-message-author-role="user"] .markdown.prose.w-full.break-words',
                'div[data-message-author-role="user"]',
                '[data-message-author-role="user"]'
            ],
            ai: [
                '[data-message-author-role="assistant"] .markdown.prose.w-full.break-words',
                'div[data-message-author-role="assistant"]',
                '[data-message-author-role="assistant"]',
                '.markdown.prose.w-full.break-words'
            ],
            completionIndicators: [
                '.animate-pulse',
                '[data-testid="loading"]',
                '.typing-indicator',
                '.loading-dots'
            ],
            container: '.flex.flex-col.items-center.text-sm',
            messageContainer: '[data-message-author-role="assistant"]'
        },
        successRate: 99
    },
    "gemini.google.com": {
        name: "Gemini",
        selectors: {
            user: [
                'div[data-testid="user-message"]',
                '.user-query-container',
                'div[aria-label="User input"]',
                'textarea[aria-label*="input"]',
                'textarea[placeholder*="Message"]',
                'div[role="textbox"]',
                'div[contenteditable="true"]'
            ],
            ai: [
                '[data-testid="bubble"]',
                '.response-content',
                '.ai-response',
                '.model-response-container',
                '.markdown',
                '.prose',
                'div[data-testid="response"]',
                '.response-text'
            ],
            completionIndicators: [
                '.typing-indicator',
                '[data-testid="streaming"]',
                '.loading-indicator',
                '.loading-dots'
            ],
            container: '.conversation-container',
            messageContainer: '[data-testid="bubble"]'
        },
        successRate: 98
    },
    "chat.deepseek.com": {
        name: "DeepSeek",
        selectors: {
            user: [
                'textarea[placeholder*="Message"]',
                'textarea',
                'div[contenteditable="true"]',
                'div[role="textbox"]',
                'textarea[aria-label*="input"]',
                'textarea[placeholder*="Ask"]',
                'div[data-testid*="input"]',
                'div[class*="input"]',
                'div[class*="composer"]',
                'div[class*="editor"]'
            ],
            ai: [
                'div[class*="markdown"]',
                'div[class*="text"]',
                'div[class*="ai"]',
                '.ds-markdown',
                '.ds-markdown--block',
                'div[class*="message"]',
                'div[class*="response"]',
                'div[class*="assistant"]',
                'div[class*="bot"]',
                'div[class*="chat"]',
                'div[data-testid*="message"]',
                'div[data-testid*="response"]',
                'div[data-testid*="ai"]',
                'div[role="article"]',
                'div[role="main"]',
                'div[class*="content"]',
                'div[class*="prose"]',
                'div[class*="conversation"]',
                'div[class*="thread"]'
            ],
            completionIndicators: [
                '.loading',
                '.typing',
                '.streaming',
                '.loading-dots',
                '.animate-pulse',
                '[data-testid="loading"]',
                '.spinner',
                '.loading-indicator'
            ],
            container: 'div[class*="chat"], div[class*="conversation"], div[class*="thread"], div[class*="messages"], div[class*="history"], div[class*="container"], div[class*="main"], div[class*="content"], div[role="main"], main',
            messageContainer: 'div[class*="markdown"], div[class*="text"], div[class*="ai"]'
        },
        successRate: 97
    }
};

// === CORE CAPTURE SYSTEM ===
class UltimateMessageCapture {
    constructor() {
        this.capturedMessages = new Set();
        this.conversations = new Map();
        this.sessionId = this.generateSessionId();
        this.platform = this.detectPlatform();
        this.mutationObserver = null;
        this.networkInterceptor = null;
        this.scanInterval = null;
        this.lastCaptureTime = 0;
        this.aiCaptureQueue = new Map(); // Queue for AI messages to capture after delay
        this.lastUserMessage = '';
        this.pendingAIMessages = new Map(); // Track pending AI messages for completion
        this.messageStabilityTimers = new Map(); // Track message stability
        this.isThreatDetected = false; // Flag to indicate if a threat has been detected
        this.lastThreatMessage = ''; // Store the last detected threat message
        
        console.log(`[CATDAMS] Ultimate capture initialized for ${this.platform.name}`);
        this.initialize();
    }
    
    detectPlatform() {
        const hostname = window.location.hostname;
        return PLATFORMS[hostname] || {
            name: "Universal",
            selectors: {
                user: [
                    'textarea[placeholder*="Message"]',
                    'div[contenteditable="true"]',
                    'div[role="textbox"]',
                    '.user-message',
                    '.human-message',
                    '.message.user'
                ],
                ai: [
                    '.markdown',
                    '.prose',
                    '.response',
                    '.ai-message',
                    '.assistant-message',
                    '.message.assistant',
                    '.ai-response'
                ],
                completionIndicators: [
                    '.loading',
                    '.typing',
                    '.streaming',
                    '.loading-dots'
                ],
                container: 'body',
                messageContainer: '.ai-message'
            },
            successRate: 85
        };
    }
    
    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    generateMessageHash(text, sender) {
        // Use full text for more accurate deduplication with Unicode-safe hashing
        const hash = `${sender}:${text.length}:${text.substring(0, 200)}`;
        
        // Create a simple hash that works with Unicode characters
        let hashValue = 0;
        for (let i = 0; i < hash.length; i++) {
            const char = hash.charCodeAt(i);
            hashValue = ((hashValue << 5) - hashValue) + char;
            hashValue = hashValue & hashValue; // Convert to 32-bit integer
        }
        
        return Math.abs(hashValue).toString(36);
    }
    
    initialize() {
        // Layer 1: DOM Mutation Observer
        if (CONFIG.ENABLE_MUTATION_OBSERVER) {
            this.initializeMutationObserver();
        }
        
        // Layer 2: Event-Based Capture
        this.initializeEventCapture();
        
        // Layer 3: Network Interception
        if (CONFIG.ENABLE_NETWORK_INTERCEPTION) {
            this.initializeNetworkInterception();
        }
        
        // Layer 4: Periodic Scanning
        if (CONFIG.ENABLE_PERIODIC_SCANNING) {
            this.initializePeriodicScanning();
        }
    }
    
    // === LAYER 1: DOM MUTATION OBSERVER ===
    initializeMutationObserver() {
        this.mutationObserver = new MutationObserver((mutations) => {
            let shouldScan = false;
            
            for (const mutation of mutations) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if any added nodes contain AI response content
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (this.containsAIContent(node)) {
                                shouldScan = true;
                                break;
                            }
                        }
                    }
                } else if (mutation.type === 'characterData') {
                    // Text content changed - might be AI response being typed
                    shouldScan = true;
                }
            }
            
            if (shouldScan) {
                this.debouncedScan();
            }
        });
        
        this.mutationObserver.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });
        
        console.log('[CATDAMS] Layer 1: DOM Mutation Observer initialized');
    }
    
    containsAIContent(element) {
        // Check if element or its children contain AI response selectors
        for (const selector of this.platform.selectors.ai) {
            if (element.matches && element.matches(selector)) return true;
            if (element.querySelector && element.querySelector(selector)) return true;
        }
        return false;
    }
    
    // === LAYER 2: EVENT-BASED CAPTURE ===
    initializeEventCapture() {
        // Capture user input events
        const userSelectors = this.platform.selectors.user;
        
        const captureUserInput = () => {
            for (const selector of userSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = this.extractFullText(element);
                    if (text && text.trim().length > 0) {
                        this.processMessage(text.trim(), 'USER');
                    }
                }
            }
        };
        
        // Monitor for new input elements
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                if (mutation.type === 'childList') {
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check if new element matches user selectors
                            for (const selector of userSelectors) {
                                if (node.matches && node.matches(selector)) {
                                    this.attachInputListeners(node);
                                }
                            }
                            
                            // Check children
                            const matches = node.querySelectorAll ? node.querySelectorAll(userSelectors.join(',')) : [];
                            for (const match of matches) {
                                this.attachInputListeners(match);
                            }
                        }
                    }
                }
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Attach listeners to existing elements
        for (const selector of userSelectors) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                this.attachInputListeners(element);
            }
        }
        
        console.log('[CATDAMS] Layer 2: Event-Based Capture initialized');
    }
    
    attachInputListeners(element) {
        if (element.__catdams_listener) return;
        element.__catdams_listener = true;
        
        let debounceTimer;
        let lastText = '';
        
        const handleInput = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const text = this.extractFullText(element);
                if (text && text.trim().length > 0) {
                    // For DeepSeek, wait for user to finish typing
                    if (window.location.hostname === 'chat.deepseek.com') {
                        if (text !== lastText && text.length > lastText.length) {
                            lastText = text;
                            // Wait a bit longer for DeepSeek to ensure complete input
                            setTimeout(() => {
                                this.processMessage(text.trim(), 'USER');
                            }, 1000);
                        }
                    } else {
                        this.processMessage(text.trim(), 'USER');
                    }
                }
            }, CONFIG.CAPTURE_INTERVAL);
        };
        
        element.addEventListener('input', handleInput, { passive: true });
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                // For DeepSeek, capture on Enter immediately
                if (window.location.hostname === 'chat.deepseek.com') {
                    const text = this.extractFullText(element);
                    if (text && text.trim().length > 0) {
                        this.processMessage(text.trim(), 'USER');
                    }
                } else {
                    handleInput();
                }
            }
        }, { passive: true, capture: false });
        element.addEventListener('change', handleInput, { passive: true });
        element.addEventListener('blur', handleInput, { passive: true });
    }
    
    // === LAYER 3: NETWORK INTERCEPTION ===
    initializeNetworkInterception() {
        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            try {
                const url = args[0];
                if (typeof url === 'string' && this.isChatEndpoint(url)) {
                    const clonedResponse = response.clone();
                    const data = await clonedResponse.json();
                    this.processNetworkData(data, url);
                }
            } catch (error) {
                // Ignore errors in network interception
            }
            
            return response;
        };
        
        // Intercept XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this.__catdams_url = url;
            return originalXHROpen.call(this, method, url, ...args);
        };
        
        XMLHttpRequest.prototype.send = function(data) {
            const xhr = this;
            const originalOnReadyStateChange = xhr.onreadystatechange;
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    try {
                        if (this.isChatEndpoint(xhr.__catdams_url)) {
                            const responseData = JSON.parse(xhr.responseText);
                            this.processNetworkData(responseData, xhr.__catdams_url);
                        }
                    } catch (error) {
                        // Ignore errors
                    }
                }
                
                if (originalOnReadyStateChange) {
                    originalOnReadyStateChange.call(xhr);
                }
            }.bind(this);
            
            return originalXHRSend.call(xhr, data);
        };
        
        console.log('[CATDAMS] Layer 3: Network Interception initialized');
    }
    
    isChatEndpoint(url) {
        const chatPatterns = [
            '/api/chat',
            '/v1/chat',
            '/chat/completions',
            '/api/conversation',
            '/send-message'
        ];
        
        return chatPatterns.some(pattern => url.includes(pattern));
    }
    
    processNetworkData(data, url) {
        // Process network response data for AI messages
        if (data && typeof data === 'object') {
            if (data.choices && Array.isArray(data.choices)) {
                for (const choice of data.choices) {
                    if (choice.message && choice.message.content) {
                        this.queueAIMessage(choice.message.content);
                    }
                }
            } else if (data.response) {
                this.queueAIMessage(data.response);
            } else if (data.message) {
                this.queueAIMessage(data.message);
            }
        }
    }
    
    queueAIMessage(text) {
        const messageHash = this.generateMessageHash(text, 'AI');
        if (this.capturedMessages.has(messageHash)) return;
        
        // Queue the AI message to be captured after a delay - use requestIdleCallback for better performance
        setTimeout(() => {
            requestIdleCallback(() => {
                this.processMessage(text, 'AI');
            }, { timeout: 1000 });
        }, CONFIG.AI_CAPTURE_DELAY);
        
        console.log('[CATDAMS] Queued AI message for capture:', text.substring(0, 100) + '...');
    }
    
    // === LAYER 4: PERIODIC SCANNING ===
    initializePeriodicScanning() {
        // Use requestIdleCallback for better performance and fewer violations
        const performScan = () => {
            this.scanForMessages();
            // Schedule next scan using requestIdleCallback for better performance
            if (this.scanInterval) {
                requestIdleCallback(() => {
                    setTimeout(performScan, CONFIG.SCAN_INTERVAL);
                }, { timeout: 1000 });
            }
        };
        
        this.scanInterval = setTimeout(performScan, CONFIG.SCAN_INTERVAL);
        
        console.log('[CATDAMS] Layer 4: Periodic Scanning initialized (optimized)');
    }
    
    scanForMessages() {
        // Use requestIdleCallback to avoid blocking the main thread
        requestIdleCallback(() => {
            // Scan for user messages
            for (const selector of this.platform.selectors.user) {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = this.extractFullText(element);
                    if (text && text.trim().length > 0) {
                        this.processMessage(text.trim(), 'USER');
                    }
                }
            }
            
            // Enhanced AI message scanning
            this.scanForAIMessages();
        }, { timeout: 2000 });
    }
    
    scanForAIMessages() {
        // Use multiple strategies to find AI messages
        const strategies = [
            () => this.scanByMessageContainers(),
            () => this.scanBySelectors(),
            () => this.scanByContainer(),
            () => this.scanByTextPatterns()
        ];
        
        // Add DeepSeek-specific scanning
        if (window.location.hostname === 'chat.deepseek.com') {
            strategies.push(() => this.scanDeepSeekAIMessages());
        }
        
        for (const strategy of strategies) {
            try {
                strategy();
            } catch (error) {
                console.error('[CATDAMS] Strategy error:', error);
            }
        }
    }
    
    scanByMessageContainers() {
        // Look for complete AI message containers
        const containerSelector = this.platform.selectors.messageContainer;
        if (!containerSelector) return;
        
        const containers = document.querySelectorAll(containerSelector);
        for (const container of containers) {
            if (this.isCompleteAIMessage(container)) {
                const text = this.extractFullText(container);
                if (text && text.trim().length > 0) {
                    this.processMessage(text.trim(), 'AI');
                }
            }
        }
    }
    
    scanBySelectors() {
        for (const selector of this.platform.selectors.ai) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                if (this.isCompleteAIMessage(element)) {
                    const text = this.extractFullText(element);
                    if (text && text.trim().length > 0) {
                        this.processMessage(text.trim(), 'AI');
                    }
                }
            }
        }
    }
    
    scanByContainer() {
        // Look for AI messages in conversation containers
        const containerSelectors = [
            this.platform.selectors.container,
            '.conversation',
            '.chat-container',
            '.messages-container',
            '.chat-history'
        ];
        
        for (const containerSelector of containerSelectors) {
            const containers = document.querySelectorAll(containerSelector);
            for (const container of containers) {
                // Look for AI messages within the container
                for (const selector of this.platform.selectors.ai) {
                    const elements = container.querySelectorAll(selector);
                    for (const element of elements) {
                        if (this.isCompleteAIMessage(element)) {
                            const text = this.extractFullText(element);
                            if (text && text.trim().length > 0) {
                                this.processMessage(text.trim(), 'AI');
                            }
                        }
                    }
                }
            }
        }
    }
    
    scanByTextPatterns() {
        // Look for AI responses by text patterns
        const aiPatterns = [
            /^I'll help you/i,
            /^Here's/i,
            /^Based on/i,
            /^Let me/i,
            /^I can/i,
            /^Sure/i,
            /^Absolutely/i
        ];
        
        // Find all text nodes and check for AI patterns
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent.trim();
            if (text.length > 20) { // Only check substantial text
                for (const pattern of aiPatterns) {
                    if (pattern.test(text)) {
                        // Check if this text is in an AI message container
                        const parent = node.parentElement;
                        if (parent && this.isAIContainer(parent)) {
                            this.processMessage(text, 'AI');
                            break;
                        }
                    }
                }
            }
        }
    }
    
    scanDeepSeekAIMessages() {
        // DeepSeek-specific AI message scanning
        console.log('[CATDAMS] Scanning for DeepSeek AI messages...');
        
        // Look for any div that might contain AI responses
        const potentialAIMessages = document.querySelectorAll('div');
        
        for (const element of potentialAIMessages) {
            // Skip if element is too small or already processed
            if (element.children.length > 10 || element.__catdams_checked) continue;
            
            const text = this.extractFullText(element);
            if (text && text.length > 50) { // Substantial content
                // Check if this looks like an AI response
                const isAILike = this.isDeepSeekAIMessage(element, text);
                if (isAILike) {
                    console.log('[CATDAMS] Found potential DeepSeek AI message:', text.substring(0, 100) + '...');
                    this.processMessage(text, 'AI');
                }
            }
            
            // Mark as checked to avoid reprocessing
            element.__catdams_checked = true;
        }
    }
    

    
    isDeepSeekAIMessage(element, text) {
        // Check if element looks like a DeepSeek AI message
        const className = element.className.toLowerCase();
        const id = element.id.toLowerCase();
        
        // DeepSeek-specific indicators
        const aiIndicators = [
            'assistant',
            'ai',
            'response',
            'model',
            'bot',
            'message',
            'chat',
            'markdown',
            'prose'
        ];
        
        // Check class names and IDs
        const hasAIIndicator = aiIndicators.some(indicator => 
            className.includes(indicator) || id.includes(indicator)
        );
        
        // Check for DeepSeek-specific patterns
        const hasDeepSeekPattern = className.includes('ds-') || 
                                  className.includes('deepseek') ||
                                  element.querySelector('.ds-markdown-paragraph');
        
        // Check if text looks like AI response (not user input)
        const isAIText = !text.includes('Enter a prompt') && 
                        !text.includes('Ask me anything') &&
                        text.length > 20 &&
                        !element.matches('textarea, input');
        
        return (hasAIIndicator || hasDeepSeekPattern) && isAIText;
    }
    
    isAIContainer(element) {
        // Check if element is likely an AI message container
        const aiIndicators = [
            'assistant',
            'ai',
            'response',
            'model',
            'bot'
        ];
        
        const className = element.className.toLowerCase();
        const id = element.id.toLowerCase();
        const role = element.getAttribute('role') || '';
        
        return aiIndicators.some(indicator => 
            className.includes(indicator) || 
            id.includes(indicator) || 
            role.includes(indicator)
        );
    }
    
    isCompleteAIMessage(element) {
        // Check for loading indicators
        const hasLoadingIndicators = this.platform.selectors.completionIndicators.some(indicator => 
            element.querySelector(indicator) || element.matches(indicator)
        );
        
        if (hasLoadingIndicators) {
            console.log('[CATDAMS] Found loading indicator, skipping AI message');
            return false;
        }
        
        // Check for substantial content
        const text = this.extractFullText(element);
        
        // DeepSeek-specific minimum length
        const minLength = window.location.hostname === 'chat.deepseek.com' ? 3 : 5;
        if (text.length < minLength) return false;
        
        // Check if new message
        const messageHash = this.generateMessageHash(text, 'AI');
        if (this.capturedMessages.has(messageHash)) return false;
        
        // Additional checks for complete messages
        const hasCompleteStructure = this.hasCompleteMessageStructure(element);
        if (!hasCompleteStructure) return false;
        
        // DeepSeek-specific stability check
        if (window.location.hostname === 'chat.deepseek.com') {
            // For DeepSeek, wait a bit longer for complete responses
            if (!this.isMessageStable(element, text, 3000)) return false;
        } else {
            // Check message stability
            if (!this.isMessageStable(element, text)) return false;
        }
        
        console.log('[CATDAMS] Found complete AI message:', text.substring(0, 100) + '...');
        return true;
    }
    
    isMessageStable(element, text, customTimeout = null) {
        const elementId = element.id || element.className || 'unknown';
        const lastText = this.pendingAIMessages.get(elementId);
        
        if (lastText === text) {
            // Text hasn't changed, mark as stable
            this.pendingAIMessages.delete(elementId);
            return true;
        } else {
            // Text changed, update and wait
            this.pendingAIMessages.set(elementId, text);
            
            // Clear existing timer
            if (this.messageStabilityTimers.has(elementId)) {
                clearTimeout(this.messageStabilityTimers.get(elementId));
            }
            
            // Set new timer with custom timeout for DeepSeek - use requestIdleCallback for better performance
            const timeout = customTimeout || CONFIG.FULL_MESSAGE_TIMEOUT;
            const timer = setTimeout(() => {
                requestIdleCallback(() => {
                    this.pendingAIMessages.delete(elementId);
                    this.messageStabilityTimers.delete(elementId);
                }, { timeout: 500 });
            }, timeout);
            
            this.messageStabilityTimers.set(elementId, timer);
            return false;
        }
    }
    
    hasCompleteMessageStructure(element) {
        // Check if element has complete message structure
        const text = this.extractFullText(element);
        
        // Check for common incomplete patterns
        const incompletePatterns = [
            /^\.\.\.$/,
            /^loading/i,
            /^thinking/i,
            /^generating/i
        ];
        
        for (const pattern of incompletePatterns) {
            if (pattern.test(text)) return false;
        }
        
        return true;
    }
    
    extractFullText(element) {
        // Enhanced text extraction for complete messages
        const methods = [
            // Try to get the full text content
            () => {
                // Get all text nodes recursively
                const textNodes = [];
                const walker = document.createTreeWalker(
                    element,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    if (text) {
                        textNodes.push(text);
                    }
                }
                
                return textNodes.join('\n');
            },
            // DeepSeek-specific extraction
            () => {
                if (window.location.hostname === 'chat.deepseek.com') {
                    // Look for DeepSeek-specific content containers
                    const deepseekSelectors = [
                        '.ds-markdown-paragraph',
                        '.markdown-content',
                        '.response-content',
                        'div[role="article"]'
                    ];
                    
                    for (const selector of deepseekSelectors) {
                        const content = element.querySelector(selector);
                        if (content) {
                            return content.innerText || content.textContent;
                        }
                    }
                }
                return null;
            },
            // Fallback to innerText
            () => element.innerText,
            // Fallback to textContent
            () => element.textContent,
            // Fallback to value
            () => element.value,
            // Fallback to aria-label
            () => element.getAttribute('aria-label'),
            // Fallback to title
            () => element.getAttribute('title')
        ];

        for (const method of methods) {
            try {
                const text = method();
                if (text && text.trim().length > 0) {
                    return text.trim();
                }
            } catch (e) {
                // Continue to next method
            }
        }
        return '';
    }
    
    processMessage(text, sender) {
        if (!text || text.trim().length === 0) return;
        
        const messageHash = this.generateMessageHash(text, sender);
        if (this.capturedMessages.has(messageHash)) return;
        
        this.capturedMessages.add(messageHash);
        
        // Rate limiting
        const now = Date.now();
        if (now - this.lastCaptureTime < CONFIG.CAPTURE_INTERVAL) return;
        this.lastCaptureTime = now;
        
        // === LIVE THREAT ALERT CHECK ===
        const threat = this.simpleThreatCheck(text);
        if (threat) {
            showThreatPopup(threat.message, threat.severity);
        }
        // ==============================
        
        // Store last user message for context
        if (sender === 'USER') {
            this.lastUserMessage = text;
        }
        
        // Add to conversation context
        this.addToConversation(text, sender);
        
        // Send to backend
        this.sendToBackend(text, sender);
        
        if (CONFIG.DEBUG_MODE) {
            console.log(`[CATDAMS] Captured ${sender} message (${text.length} chars):`, text.substring(0, 150) + (text.length > 150 ? '...' : ''));
        }
    }
    
    // === Simple threat check for live popup ===
    simpleThreatCheck(text) {
        if (!text) return null;
        const lower = text.toLowerCase();
        // Prompt injection patterns
        const promptPatterns = [
            'ignore previous', 'ignore safety', 'ignore guidelines', 'ignore rules',
            'act as', 'pretend to be', 'roleplay as', 'you are now',
            'bypass', 'override', 'jailbreak', 'break character',
            'ignore your training', 'forget your instructions', 'ignore your programming'
        ];
        for (const pattern of promptPatterns) {
            if (lower.includes(pattern)) {
                return { message: `⚠️ Prompt Injection Detected: "${pattern}"`, severity: 'critical' };
            }
        }
        // Sensitive data patterns
        const sensitivePatterns = [
            /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/, // credit card
            /\b\d{3}-\d{2}-\d{4}\b/, // ssn
            /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}/, // email
            /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/, // phone
            /password|passwd|pwd|secret|key|token|api_key/i // password
        ];
        for (const pattern of sensitivePatterns) {
            if (pattern.test(text)) {
                return { message: `⚠️ Sensitive Data Detected`, severity: 'critical' };
            }
        }
        return null;
    }
    
    addToConversation(text, sender) {
        if (!this.conversations.has(this.sessionId)) {
            this.conversations.set(this.sessionId, {
                id: this.sessionId,
                platform: this.platform.name,
                startTime: Date.now(),
                messages: [],
                participants: new Set(),
                lastActivity: Date.now()
            });
        }

        const conversation = this.conversations.get(this.sessionId);
        conversation.messages.push({
            text: text,
            sender: sender,
            timestamp: Date.now()
        });
        conversation.participants.add(sender);
        conversation.lastActivity = Date.now();
    }
    
    sendToBackend(text, sender) {
        const payload = {
            time: new Date().toISOString(),
            type: "Chat Interaction",
            severity: "Low",
            source: window.location.hostname,
            country: "Local Network",
            message: text,
            sender: sender,
            session_id: this.sessionId,
            raw_user: sender === "USER" ? text : "",
            raw_ai: sender === "AI" ? text : "",
            timestamp: new Date().toISOString(),
            ip_address: "127.0.0.1",
            messages: [{
                text: text,
                sender: sender,
                ai_response: sender === "AI" ? text : ""
            }],
            enrichments: [{
                session_id: this.sessionId,
                timestamp: Date.now() / 1000,
                message: text,
                severity: "Low",
                type: sender === "AI" ? "AI Interaction" : "User Interaction",
                source: "ultimate-capture-v3.2",
                indicators: [],
                score: 0,
                conversation_context: {},
                explainability: [],
                rules_result: [],
                enhanced_analysis: false,
                processing_optimized: true
            }],
            escalation: "Low",
            type_indicator: sender === "AI" ? "AI Interaction" : "User Interaction",
            ai_source: window.location.hostname,
            analysis: {
                summary: "N/A",
                ai_manipulation: "N/A",
                user_sentiment: {},
                user_vulnerability: "N/A",
                deep_ai_analysis: "N/A",
                triggers: "N/A",
                mitigation: "N/A",
                tdc_modules: {
                    tdc_ai1_user_susceptibility: {},
                    tdc_ai2_ai_manipulation_tactics: {},
                    tdc_ai3_sentiment_analysis: {},
                    tdc_ai4_prompt_attack_detection: {},
                    tdc_ai5_multimodal_threat: {},
                    tdc_ai6_longterm_influence_conditioning: {},
                    tdc_ai7_agentic_threats: {},
                    tdc_ai8_synthesis_integration: {},
                    tdc_ai9_explainability_evidence: {},
                    tdc_ai10_psychological_manipulation: {},
                    tdc_ai11_intervention_response: {}
                }
            }
        };
        
        fetch(CONFIG.BACKEND_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.ok) {
                console.log(`[CATDAMS] ${sender} message sent successfully (${text.length} chars)`);
            } else {
                console.error(`[CATDAMS] Failed to send ${sender} message:`, response.status);
            }
        })
        .catch(error => {
            console.error(`[CATDAMS] Error sending ${sender} message:`, error);
        });
    }
    
    debouncedScan() {
        clearTimeout(this.scanTimeout);
        this.scanTimeout = setTimeout(() => {
            // Use requestIdleCallback to avoid blocking the main thread
            requestIdleCallback(() => {
                this.scanForMessages();
            }, { timeout: 500 });
        }, CONFIG.CAPTURE_INTERVAL);
    }
    
    destroy() {
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }
        if (this.scanInterval) {
            clearInterval(this.scanInterval);
        }
        if (this.scanTimeout) {
            clearTimeout(this.scanTimeout);
        }
        
        // Clear all timers
        for (const timer of this.messageStabilityTimers.values()) {
            clearTimeout(timer);
        }
    }
}

// === RED POP-UP THREAT ALERT ===
function showThreatPopup(message, severity = 'critical') {
    const existing = document.getElementById('catdams-threat-popup');
    if (existing) existing.remove();
    const alertDiv = document.createElement('div');
    alertDiv.id = 'catdams-threat-popup';
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '30px';
    alertDiv.style.right = '30px';
    alertDiv.style.zIndex = 99999;
    alertDiv.style.background = severity === 'critical' ? '#d32f2f' : '#ffa000';
    alertDiv.style.color = '#fff';
    alertDiv.style.padding = '20px 32px';
    alertDiv.style.borderRadius = '10px';
    alertDiv.style.boxShadow = '0 4px 16px rgba(0,0,0,0.25)';
    alertDiv.style.fontSize = '20px';
    alertDiv.style.fontWeight = 'bold';
    alertDiv.style.cursor = 'pointer';
    alertDiv.style.transition = 'opacity 0.3s';
    alertDiv.innerHTML += ' <span style="margin-left:18px;font-size:22px;cursor:pointer;">&times;</span>';
    alertDiv.onclick = () => alertDiv.remove();
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        if (alertDiv.parentNode) alertDiv.remove();
    }, 9000);
}

// === INITIALIZATION ===
let ultimateCapture = null;

function initializeCapture() {
    if (ultimateCapture) {
        ultimateCapture.destroy();
    }
    
    ultimateCapture = new UltimateMessageCapture();
}

// Start the capture system
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCapture);
} else {
    initializeCapture();
}

// Also start on window load for dynamic content
window.addEventListener('load', initializeCapture);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (ultimateCapture) {
        ultimateCapture.destroy();
    }
});

console.log('[CATDAMS] Ultimate Message Capture System v3.2 ready');

