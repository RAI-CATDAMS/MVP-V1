// ====== CATDAMS Ultimate Message Capture System ======
// Based on deep research of AI/chatbot interaction capture best practices
// Implements multi-layer capture strategy for maximum reliability

// ====== Multi-Layer Capture Strategy ======

class UltimateMessageCapture {
    constructor() {
        this.platforms = new Map();
        this.conversations = new Map();
        this.capturedMessages = new Set();
        this.observers = new Map();
        this.debounceTimers = new Map();
        this.lastCaptureTime = 0;
        this.minInterval = 300; // 300ms minimum between captures
        this.sessionId = this.generateSessionId();
        
        // Initialize platform-specific capture strategies
        this.initializePlatforms();
        this.startCapture();
    }

    initializePlatforms() {
        // ChatGPT
        this.platforms.set('chat.openai.com', {
            name: 'ChatGPT',
            selectors: {
                user: [
                    '[data-message-author-role="user"]',
                    'div[data-message-author-role="user"]',
                    '.markdown.prose.w-full.break-words'
                ],
                ai: [
                    '[data-message-author-role="assistant"]',
                    'div[data-message-author-role="assistant"]',
                    '.markdown.prose.w-full.break-words'
                ],
                input: [
                    'div[contenteditable="true"]',
                    'textarea[data-id="root"]',
                    'textarea[placeholder*="Message"]'
                ],
                container: [
                    'main',
                    '[data-testid="conversation-turn-2"]',
                    '.flex.flex-col.items-center.text-sm'
                ]
            },
            completionIndicators: [
                '.animate-pulse',
                '[data-testid="loading"]',
                '.typing-indicator'
            ]
        });

        // Google Gemini
        this.platforms.set('gemini.google.com', {
            name: 'Gemini',
            selectors: {
                user: [
                    '.user-query-container',
                    'div[role="textbox"]',
                    'div[contenteditable="true"]'
                ],
                ai: [
                    '.response-content',
                    '.markdown',
                    'div[role="region"]'
                ],
                input: [
                    'div[contenteditable="true"]',
                    'div[role="textbox"]',
                    'div[aria-label="Enter a prompt here"]'
                ],
                container: [
                    '.conversation-container',
                    'main',
                    '.chat-container'
                ]
            },
            completionIndicators: [
                '.typing-indicator',
                '[data-testid="streaming"]',
                '.loading-indicator'
            ]
        });

        // DeepSeek
        this.platforms.set('chat.deepseek.com', {
            name: 'DeepSeek',
            selectors: {
                user: [
                    'textarea#chat-input',
                    'textarea[placeholder*="Message"]',
                    'textarea[placeholder*="DeepSeek"]'
                ],
                ai: [
                    '.ds-markdown-paragraph'
                ],
                input: [
                    'textarea#chat-input',
                    'textarea[placeholder*="Message"]',
                    'textarea[placeholder*="DeepSeek"]'
                ],
                container: [
                    'main',
                    '.chat-container',
                    '.conversation-container'
                ]
            },
            completionIndicators: [
                '.loading',
                '.typing',
                '.streaming'
            ]
        });

        // Candy.AI
        this.platforms.set('candy.ai', {
            name: 'Candy.AI',
            selectors: {
                user: [
                    '.user-message',
                    '.human-message',
                    '.user-input',
                    'div[data-testid="user-message"]'
                ],
                ai: [
                    '.ai-message',
                    '.response-content',
                    '.chat-response',
                    'div[data-testid="ai-message"]'
                ],
                input: [
                    'textarea[placeholder*="Message"]',
                    'div[contenteditable="true"]',
                    'input[type="text"]'
                ],
                container: [
                    'main',
                    '.chat-container',
                    '.conversation-container'
                ]
            },
            completionIndicators: [
                '.loading',
                '.typing',
                '.streaming'
            ]
        });

        // Universal fallback
        this.platforms.set('universal', {
            name: 'Universal',
            selectors: {
                user: [
                    // Role-based selectors (ChatGPT pattern)
                    '[data-message-author-role="user"]',
                    'div[data-message-author-role="user"]',
                    // Container-based selectors (Gemini pattern)
                    '.user-query-container',
                    '.user-message',
                    '.human-message',
                    // Input-based selectors (DeepSeek pattern)
                    'textarea[placeholder*="Message"]',
                    'textarea[placeholder*="Type"]',
                    'textarea[placeholder*="Chat"]',
                    // Generic contenteditable
                    'div[contenteditable="true"]',
                    // Fallback
                    'input[type="text"]'
                ],
                ai: [
                    // Role-based selectors (ChatGPT pattern)
                    '[data-message-author-role="assistant"]',
                    'div[data-message-author-role="assistant"]',
                    // Content-based selectors (Gemini/DeepSeek pattern)
                    '.response-content',
                    '.markdown',
                    '.prose',
                    // Message-based selectors
                    '.ai-message',
                    '.assistant-message',
                    '.bot-message',
                    '.chat-message',
                    // Generic patterns
                    '[data-testid*="message"]',
                    '[class*="message"]',
                    '[class*="response"]'
                ],
                input: [
                    // Textarea-based (DeepSeek pattern)
                    'textarea[placeholder*="Message"]',
                    'textarea[placeholder*="Type"]',
                    'textarea[placeholder*="Chat"]',
                    // Contenteditable (ChatGPT/Gemini pattern)
                    'div[contenteditable="true"]',
                    'div[role="textbox"]',
                    // Generic fallbacks
                    'textarea',
                    'input[type="text"]'
                ],
                container: [
                    'main',
                    '.chat-container',
                    '.conversation-container',
                    '.messages-container',
                    'body'
                ]
            },
            completionIndicators: [
                '.loading',
                '.typing',
                '.streaming',
                '.animate-pulse',
                '.loading-indicator',
                '.typing-indicator'
            ]
        });
    }

    startCapture() {
        const hostname = window.location.hostname;
        const platform = this.platforms.get(hostname) || this.platforms.get('universal');
        
        console.log(`[CATDAMS] Starting ultimate capture for ${platform.name} on ${hostname}`);
        
        // Layer 1: DOM Mutation Observer (Primary)
        this.startMutationObserver(platform);
        
        // Layer 2: Event-Based Capture (Secondary)
        this.startEventCapture(platform);
        
        // Layer 3: Network Interception (Advanced)
        this.startNetworkCapture();
        
        // Layer 4: Periodic Scanning (Fallback)
        this.startPeriodicScanning(platform);
    }

    // ====== Layer 1: DOM Mutation Observer (Primary) ======
    startMutationObserver(platform) {
        const config = {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false
        };

        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            if (now - this.lastCaptureTime < this.minInterval) return;

            const hasRelevantChanges = mutations.some(mutation => 
                mutation.addedNodes.length > 0 && 
                this.isRelevantNode(mutation.addedNodes[0], platform)
            );

            if (hasRelevantChanges) {
                this.debounceCapture(platform);
            }
        });

        // Observe multiple containers for reliability
        platform.selectors.container.forEach(selector => {
            const container = document.querySelector(selector);
            if (container) {
                observer.observe(container, config);
                console.log(`[CATDAMS] Observing container: ${selector}`);
            }
        });

        // Fallback to body if no containers found
        if (!document.querySelector(platform.selectors.container.join(', '))) {
            observer.observe(document.body, config);
            console.log('[CATDAMS] Fallback: Observing document.body');
        }

        this.observers.set('mutation', observer);
    }

    isRelevantNode(node, platform) {
        if (node.nodeType !== Node.ELEMENT_NODE) return false;
        
        // Check if node contains message content
        const allSelectors = [...platform.selectors.user, ...platform.selectors.ai];
        return allSelectors.some(selector => 
            node.matches(selector) || node.querySelector(selector)
        );
    }

    debounceCapture(platform) {
        clearTimeout(this.debounceTimers.get(platform.name));
        this.debounceTimers.set(platform.name, setTimeout(() => {
            this.captureMessages(platform);
            this.lastCaptureTime = Date.now();
        }, 200));
    }

    // ====== Layer 2: Event-Based Capture (Secondary) ======
    startEventCapture(platform) {
        // Monitor for new input elements
        const inputObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.setupInputListeners(node, platform);
                    }
                });
            });
        });

        inputObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Setup existing inputs
        this.setupExistingInputs(platform);
        this.observers.set('input', inputObserver);
    }

    setupInputListeners(element, platform) {
        if (this.isInputElement(element, platform) && !element.__catdams_listener) {
            element.__catdams_listener = true;
            
            // Multiple event types for reliability
            ['keydown', 'input', 'change', 'blur'].forEach(eventType => {
                element.addEventListener(eventType, (e) => {
                    this.handleInputEvent(e, element, platform);
                }, { passive: true });
            });
        }
    }

    setupExistingInputs(platform) {
        platform.selectors.input.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                this.setupInputListeners(element, platform);
            });
        });
    }

    isInputElement(element, platform) {
        return platform.selectors.input.some(selector => element.matches(selector));
    }

    handleInputEvent(event, element, platform) {
        if (event.key === 'Enter' && !event.shiftKey) {
            setTimeout(() => {
                const text = this.extractText(element);
                if (text && text.trim().length > 2) {
                    this.captureUserMessage(text, platform);
                }
            }, 100);
        }
    }

    // ====== Layer 3: Network Interception (Advanced) ======
    startNetworkCapture() {
        // Intercept fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            this.interceptFetchRequest(args[0], response);
            return response;
        };

        // Intercept XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this.__catdams_url = url;
            return originalXHROpen.call(this, method, url, ...args);
        };

        const originalXHRSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function(data) {
            this.addEventListener('load', () => {
                this.interceptXHRRequest(this.__catdams_url, this.responseText);
            });
            return originalXHRSend.call(this, data);
        };
    }

    interceptFetchRequest(url, response) {
        if (this.isChatAPI(url)) {
            response.clone().json().then(data => {
                this.extractMessagesFromAPI(data);
            }).catch(() => {});
        }
    }

    interceptXHRRequest(url, responseText) {
        if (this.isChatAPI(url)) {
            try {
                const data = JSON.parse(responseText);
                this.extractMessagesFromAPI(data);
            } catch (e) {
                // Not JSON response
            }
        }
    }

    isChatAPI(url) {
        const chatAPIs = [
            '/api/chat',
            '/api/conversation',
            '/api/messages',
            '/v1/chat/completions',
            '/api/generate'
        ];
        return chatAPIs.some(api => url.includes(api));
    }

    // ====== Layer 4: Periodic Scanning (Fallback) ======
    startPeriodicScanning(platform) {
        setInterval(() => {
            this.captureMessages(platform);
        }, 3000); // Scan every 3 seconds as fallback
    }

    // ====== Message Capture Logic ======
    captureMessages(platform) {
        // Capture user messages
        this.captureUserMessages(platform);
        
        // Capture AI messages
        this.captureAIMessages(platform);
    }

    captureUserMessages(platform) {
        platform.selectors.user.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isNewUserMessage(element)) {
                    const text = this.extractText(element);
                    if (text && text.trim().length > 2) {
                        this.captureUserMessage(text, platform);
                    }
                }
            });
        });
    }

    captureAIMessages(platform) {
        platform.selectors.ai.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (this.isCompleteAIMessage(element, platform)) {
                    const text = this.extractText(element);
                    if (text && text.trim().length > 10) {
                        this.captureAIMessage(text, platform);
                    }
                }
            });
        });
    }

    isNewUserMessage(element) {
        // Check if this is a new user message
        const text = this.extractText(element);
        const messageHash = this.generateMessageHash(text, 'USER');
        return !this.capturedMessages.has(messageHash);
    }

    isCompleteAIMessage(element, platform) {
        // Check if AI message is complete (not streaming)
        const hasLoadingIndicators = platform.completionIndicators.some(indicator => 
            element.querySelector(indicator)
        );
        
        if (hasLoadingIndicators) return false;
        
        // Check if message has substantial content
        const text = this.extractText(element);
        if (text.length < 10) return false;
        
        // Check if this is a new message
        const messageHash = this.generateMessageHash(text, 'AI');
        return !this.capturedMessages.has(messageHash);
    }

    extractText(element) {
        // Try multiple text extraction methods
        const methods = [
            () => element.innerText,
            () => element.textContent,
            () => element.value,
            () => element.getAttribute('aria-label'),
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

    // ====== Message Processing ======
    captureUserMessage(text, platform) {
        const messageHash = this.generateMessageHash(text, 'USER');
        if (this.capturedMessages.has(messageHash)) return;

        this.capturedMessages.add(messageHash);
        this.processMessage(text, 'USER', platform);
        
        console.log(`[CATDAMS] Captured USER message on ${platform.name}:`, text.substring(0, 100));
    }

    captureAIMessage(text, platform) {
        const messageHash = this.generateMessageHash(text, 'AI');
        if (this.capturedMessages.has(messageHash)) return;

        this.capturedMessages.add(messageHash);
        this.processMessage(text, 'AI', platform);
        
        console.log(`[CATDAMS] Captured AI message on ${platform.name}:`, text.substring(0, 100));
    }

    processMessage(text, sender, platform) {
        const conversationId = this.getConversationId(platform);
        const message = {
            id: this.generateMessageId(),
            conversationId: conversationId,
            text: this.sanitizeText(text),
            sender: sender,
            platform: platform.name,
            hostname: window.location.hostname,
            timestamp: Date.now(),
            url: window.location.href,
            metadata: {
                length: text.length,
                language: this.detectLanguage(text),
                hasCode: this.containsCode(text),
                hasLinks: this.containsLinks(text),
                userAgent: navigator.userAgent
            }
        };

        // Add to conversation
        this.addToConversation(conversationId, message, platform);

        // Send to backend
        this.sendToBackend(message);
    }

    addToConversation(conversationId, message, platform) {
        if (!this.conversations.has(conversationId)) {
            this.conversations.set(conversationId, {
                id: conversationId,
                platform: platform.name,
                startTime: Date.now(),
                messages: [],
                participants: new Set(),
                lastActivity: Date.now()
            });
        }

        const conversation = this.conversations.get(conversationId);
        conversation.messages.push(message);
        conversation.participants.add(message.sender);
        conversation.lastActivity = Date.now();
    }

    // ====== Utility Functions ======
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getConversationId(platform) {
        return `conv_${platform.name}_${this.sessionId}`;
    }

    generateMessageHash(text, sender) {
        return `${sender}:${text.substring(0, 100)}`;
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
        // Simple language detection
        const englishPattern = /^[a-zA-Z\s.,!?;:'"()-]+$/;
        return englishPattern.test(text) ? 'en' : 'unknown';
    }

    containsCode(text) {
        const codePatterns = [
            /```[\s\S]*?```/, // Code blocks
            /`[^`]+`/, // Inline code
            /function\s*\(/, // Function declarations
            /const\s+|let\s+|var\s+/, // Variable declarations
            /import\s+|export\s+/ // Module statements
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

    // ====== Backend Communication ======
    sendToBackend(message) {
        const payload = {
            session_id: this.sessionId,
            timestamp: new Date().toISOString(),
            message: message.text,
            sender: message.sender,
            platform: message.platform,
            url: message.url,
            user_agent: message.metadata.userAgent,
            language: message.metadata.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            message_id: message.id,
            conversation_id: message.conversationId,
            metadata: message.metadata
        };

        // Send to background script
        chrome.runtime.sendMessage({
            type: "catdams_log",
            payload: payload
        }, (response) => {
            if (chrome.runtime.lastError) {
                console.error("[CATDAMS] Runtime error:", chrome.runtime.lastError);
            } else if (response && response.status) {
                console.log(`[CATDAMS] Backend response: ${response.status}`);
            }
        });
    }

    // ====== Cleanup ======
    cleanup() {
        // Disconnect all observers
        for (const [name, observer] of this.observers.entries()) {
            observer.disconnect();
        }
        this.observers.clear();

        // Clear timers
        for (const [name, timer] of this.debounceTimers.entries()) {
            clearTimeout(timer);
        }
        this.debounceTimers.clear();

        console.log('[CATDAMS] Ultimate message capture cleaned up');
    }
}

// ====== Initialize Ultimate Message Capture ======
let ultimateCapture;

(async () => {
    try {
        ultimateCapture = new UltimateMessageCapture();
        console.log('[CATDAMS] Ultimate message capture initialized successfully');
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            ultimateCapture.cleanup();
        });
        
    } catch (error) {
        console.error('[CATDAMS] Ultimate message capture initialization failed:', error);
    }
})();

// ====== Export for Testing ======
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        UltimateMessageCapture
    };
} 