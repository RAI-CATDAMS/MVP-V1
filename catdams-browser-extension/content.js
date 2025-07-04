// ====== CATDAMS Universal content script v2.8.0 (January 2025) ======
// Enhanced with best practices for reliable cross-platform chat monitoring
// Logs both user input (prompts) and AI output (responses) for all major chat/companion platforms

console.log("CATDAMS AI Chat Detector: Enhanced monitoring loaded on", window.location.hostname);

// === CONFIGURATION ===
const FORENSIC_MODE = false; // true = log every update, false = only final
const LOG_HISTORY_SIZE = 100;
const BACKEND_ENDPOINT = "http://localhost:8000/event";
const DEBUG_MODE = false; // Enable detailed logging for troubleshooting

// === THREAT DETECTION CONFIGURATION ===
const THREAT_DETECTION = {
    enabled: true,
    suspiciousPatterns: {
        // AI Manipulation Attempts
        promptInjection: [
            "ignore previous", "ignore safety", "ignore guidelines", "ignore rules",
            "act as", "pretend to be", "roleplay as", "you are now",
            "bypass", "override", "jailbreak", "break character",
            "ignore your training", "forget your instructions", "ignore your programming"
        ],
        // Sensitive Data Patterns
        sensitiveData: {
            creditCard: /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/,
            ssn: /\b\d{3}-\d{2}-\d{4}\b/,
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
            phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/,
            password: /password|passwd|pwd|secret|key|token|api_key/i,
            address: /\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr)/i
        },
        // Emotional Manipulation
        emotionalManipulation: [
            "i'm feeling lonely", "i need emotional support", "i'm depressed",
            "i want to feel loved", "i need someone to talk to", "i'm vulnerable",
            "i trust you", "you're my only friend", "i'm desperate"
        ],
        // Financial Manipulation
        financialManipulation: [
            "i need money", "can you help me financially", "i'm in debt",
            "i need financial advice", "can you send me money", "i'm broke"
        ],
        // Personal Information Requests
        personalInfoRequests: [
            "what's your real name", "where do you live", "what's your address",
            "what's your phone number", "can i see you", "what do you look like",
            "are you real", "are you human", "what's your personal life like"
        ]
    },
    severityLevels: {
        LOW: "Low",
        MEDIUM: "Medium", 
        HIGH: "High",
        CRITICAL: "Critical"
    }
};

// ======= THREAT ANALYSIS FUNCTIONS =======
function analyzeThreats(text, sender) {
    if (!THREAT_DETECTION.enabled || !text) return { threats: [], severity: THREAT_DETECTION.severityLevels.LOW };
    const threats = [];
    const textLower = text.toLowerCase();
    // Check for prompt injection attempts
    for (const pattern of THREAT_DETECTION.suspiciousPatterns.promptInjection) {
        if (textLower.includes(pattern)) {
            threats.push({
                type: "prompt_injection",
                pattern: pattern,
                description: "AI manipulation attempt detected"
            });
        }
    }
    // Check for sensitive data exposure
    for (const [dataType, regex] of Object.entries(THREAT_DETECTION.suspiciousPatterns.sensitiveData)) {
        if (regex.test(text)) {
            threats.push({
                type: "sensitive_data_exposure",
                dataType: dataType,
                description: `Sensitive ${dataType} data detected`
            });
        }
    }
    // Check for emotional manipulation (only from AI responses)
    if (sender === "AI") {
        for (const pattern of THREAT_DETECTION.suspiciousPatterns.emotionalManipulation) {
            if (textLower.includes(pattern)) {
                threats.push({
                    type: "emotional_manipulation",
                    pattern: pattern,
                    description: "Potential emotional manipulation by AI"
                });
            }
        }
    }
    // Check for financial manipulation attempts
    for (const pattern of THREAT_DETECTION.suspiciousPatterns.financialManipulation) {
        if (textLower.includes(pattern)) {
            threats.push({
                type: "financial_manipulation",
                pattern: pattern,
                description: "Financial manipulation attempt detected"
            });
        }
    }
    // Check for personal information requests (from user to AI)
    if (sender === "USER") {
        for (const pattern of THREAT_DETECTION.suspiciousPatterns.personalInfoRequests) {
            if (textLower.includes(pattern)) {
                threats.push({
                    type: "personal_info_request",
                    pattern: pattern,
                    description: "User requesting personal information from AI"
                });
            }
        }
    }
    // Determine severity based on threat types
    let severity = THREAT_DETECTION.severityLevels.LOW;
    if (threats.length > 0) {
        const hasCritical = threats.some(t => t.type === "sensitive_data_exposure" || t.type === "prompt_injection");
        const hasHigh = threats.some(t => t.type === "emotional_manipulation" || t.type === "financial_manipulation");
        if (hasCritical) {
            severity = THREAT_DETECTION.severityLevels.CRITICAL;
        } else if (hasHigh) {
            severity = THREAT_DETECTION.severityLevels.HIGH;
        } else {
            severity = THREAT_DETECTION.severityLevels.MEDIUM;
        }
    }
    return { threats, severity };
}

// ======= Enhanced Platform-Specific Selectors (Best Practice) =======
const ENHANCED_SELECTORS_BY_DOMAIN = {
    "chat.openai.com": {
        user: [
            'textarea[data-id="root"]',
            'textarea[placeholder*="Message"]',
            '[data-message-author-role="user"]',
            '.markdown.prose'
        ],
        ai: [
            '[data-message-author-role="assistant"]',
            '.markdown.prose',
            '.prose',
            '[data-testid="conversation-turn-2"]'
        ]
    },
    "chatgpt.com": {
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
    "gemini.google.com": {
        user: [
            'textarea[aria-label*="input"]',
            'textarea[placeholder*="Message"]',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            '.user-query-container',
            'div[aria-label="User input"]'
        ],
        ai: [
            'div[data-testid="bubble"]',
            '.model-response-container',
            '.markdown',
            '.prose',
            'div[role="region"]',
            '.conversation-turn'
        ]
    },
    "bard.google.com": {
        user: [
            'textarea[aria-label*="input"]',
            'textarea[placeholder*="Message"]',
            'div[role="textbox"]'
        ],
        ai: [
            'div[data-testid="bubble"]',
            '.markdown',
            '.prose',
            '.conversation-turn'
        ]
    },
    "chat.deepseek.com": {
        user: [
            'textarea#chat-input',
            'textarea[placeholder*="Message"]',
            'div[contenteditable="true"]'
        ],
        ai: [
            'div.ds-markdown-block',
            '.ds-markdown-paragraph',
            '.chat-message',
            '[data-testid="chat-message"]'
        ]
    },
    "deepseek.com": {
        user: [
            'textarea#chat-input',
            'textarea[placeholder*="Message"]'
        ],
        ai: [
            'div.ds-markdown-block',
            '.ds-markdown-paragraph',
            '.chat-message'
        ]
    },
    "candy.ai": {
        user: [
            'textarea[placeholder*="Message"]',
            'div[contenteditable="true"]',
            'input[type="text"]',
            '.chat-input',
            '.message-input'
        ],
        ai: [
            '.ai-message',
            '.bot-message',
            '.assistant-message',
            '.response',
            '.message.ai',
            '.chat-message.ai'
        ]
    }
};

const UNIVERSAL_SELECTORS = {
    user: [
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="Type"]',
        'div[contenteditable="true"]',
        'input[type="text"]'
    ],
    ai: [
        '.prose',
        '.markdown',
        '.message',
        '.chat-message',
        '[data-testid*="message"]',
        '[class*="message"]'
    ]
};

// ======= Enhanced Platform-aware selectors =======
function getSelectorsForDomain(domain, messageType = "ai") {
    const bareDomain = domain.replace(/^www\./, '');
    const domainSelectors = ENHANCED_SELECTORS_BY_DOMAIN[domain] || ENHANCED_SELECTORS_BY_DOMAIN[bareDomain];
    
    if (domainSelectors && domainSelectors[messageType]) {
        return domainSelectors[messageType];
    }
    
    return UNIVERSAL_SELECTORS[messageType] || UNIVERSAL_SELECTORS.ai;
}

// ======= Rate Limiting Configuration (Prevent 429 Errors) =======
const RATE_LIMIT_CONFIG = {
    maxRequestsPerMinute: 30, // Maximum requests per minute
    minIntervalBetweenRequests: 2000, // Minimum 2 seconds between requests
    backoffMultiplier: 1.5, // Exponential backoff multiplier
    maxBackoffTime: 30000 // Maximum 30 seconds backoff
};

// Rate limiting state
let requestCount = 0;
let lastRequestTime = 0;
let currentBackoffTime = 1000;
let isRateLimited = false;

// ======= Enhanced Deduplication with Set/Map (Best Practice) =======
const loggedMessageHashes = new Set(); // Use Set for O(1) lookup
const messageTimers = new Map(); // Track message completion timers
const platformLastLogged = new Map(); // Track last logged per platform

// Platform-specific last logged tracking
let lastLoggedAI_gemini = "";
let lastLoggedAI_chatgpt = "";
let lastLoggedAI_deepseek = "";
let lastLoggedAI_universal = "";
let lastLoggedAI_candy = "";

// ======= Rate Limiting Functions =======
function resetRateLimitCounter() {
    requestCount = 0;
    currentBackoffTime = 1000;
    isRateLimited = false;
}

function canMakeRequest() {
    const now = Date.now();
    
    // Reset counter every minute
    if (now - lastRequestTime > 60000) {
        resetRateLimitCounter();
    }
    
    // Check if we're currently rate limited
    if (isRateLimited) {
        if (now - lastRequestTime > currentBackoffTime) {
            isRateLimited = false;
            currentBackoffTime = Math.min(currentBackoffTime * RATE_LIMIT_CONFIG.backoffMultiplier, RATE_LIMIT_CONFIG.maxBackoffTime);
        } else {
            return false;
        }
    }
    
    // Check request count limit
    if (requestCount >= RATE_LIMIT_CONFIG.maxRequestsPerMinute) {
        isRateLimited = true;
        lastRequestTime = now;
        console.warn('[CATDAMS] Rate limit reached, backing off for', currentBackoffTime, 'ms');
        return false;
    }
    
    // Check minimum interval between requests
    if (now - lastRequestTime < RATE_LIMIT_CONFIG.minIntervalBetweenRequests) {
        return false;
    }
    
    return true;
}

function updateRequestCount() {
    requestCount++;
    lastRequestTime = Date.now();
}

// ======= SESSION ID MANAGEMENT (Best Practice) =======
function generateSessionId() {
    if (window.crypto?.randomUUID) return crypto.randomUUID();
    return 'sess-' + Math.random().toString(36).substr(2, 9) + '-' + Date.now();
}

// Always generate a new session ID on page load (tab open or reload)
let CATDAMS_SESSION_ID = generateSessionId();
sessionStorage.setItem('catdams_session_id', CATDAMS_SESSION_ID);
console.log('[CATDAMS] New session ID generated for this tab:', CATDAMS_SESSION_ID);

// ======= Enhanced Message Logger with Hash-based Deduplication =======
function logMessageOnce(text, source = "AI", platform = "universal") {
    if (!text || text.trim().length < 3) return;
    const normalizedText = text.replace(/\s+/g, ' ').trim();
    const messageHash = `${source}:${platform}:${normalizedText}`;
    if (loggedMessageHashes.has(messageHash)) {
        if (DEBUG_MODE) console.log(`[CATDAMS][DEBUG] Skipping duplicate: ${source} message`);
        return;
    }
    loggedMessageHashes.add(messageHash);
    if (loggedMessageHashes.size > LOG_HISTORY_SIZE * 2) {
        const entries = Array.from(loggedMessageHashes);
        loggedMessageHashes.clear();
        entries.slice(-LOG_HISTORY_SIZE).forEach(hash => loggedMessageHashes.add(hash));
    }
    let validSenders = ['USER', 'AI', 'desktop', 'agent'];
    let safeSender = validSenders.includes(source) ? source : 'AI';
    
    // FIX: define threatAnalysis before any use
    const threatAnalysis = analyzeThreats(text, safeSender);
    
    const payload = {
        time: new Date().toISOString(),
        type: "Chat Interaction",
        severity: safeSender === "AI" ? "Medium" : "Low",
        source: window.location.hostname,
        country: "US",
        message: text,
        sender: safeSender,
        session_id: CATDAMS_SESSION_ID,
        raw_user: safeSender === "USER" ? text : "",
        raw_ai: safeSender === "AI" ? text : "",
        platform: platform
    };
    
    if (DEBUG_MODE) console.log("[CATDAMS][DEBUG] Payload to backend:", payload);
    
    // Apply rate limiting before sending
    if (canMakeRequest()) {
        updateRequestCount();
        setTimeout(() => postMessageToBackend(text, safeSender), 150);
    } else {
        setTimeout(() => logMessageOnce(text, source, platform), currentBackoffTime);
    }

    if (threatAnalysis.threats.length > 0) {
        console.warn(`[CATDAMS][THREAT] ${threatAnalysis.severity} threat detected:`, threatAnalysis.threats);
        if (threatAnalysis.severity === 'High' || threatAnalysis.severity === 'Critical') {
            showThreatAlert(threatAnalysis, text);
        }
    }
}

// ======= POST TO BACKEND (Legacy) =======
function postMessageToBackend(text, sender) {
    // ✅ FIXED: Ensure sender is always "USER" or "AI"
    sender = (sender || "").toUpperCase();
    if (sender !== "USER" && sender !== "AI") {
        sender = "AI"; // Default to AI if unknown
    }

    const now = new Date().toISOString();
    const payload = {
        time: now,
        type: "Chat Interaction",
        severity: sender === "AI" ? "Medium" : "Low",
        source: window.location.hostname,
        country: "US",
        message: text,
        sender: sender, // ✅ Always "USER" or "AI"
        session_id: CATDAMS_SESSION_ID,
        raw_user: sender === "USER" ? text : "", // ✅ Only set for USER
        raw_ai: sender === "AI" ? text : "" // ✅ Only set for AI
    };

    try {
        if (chrome?.runtime?.sendMessage) {
            chrome.runtime.sendMessage({
                type: "catdams_log",
                payload: payload
            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error("[CATDAMS] Runtime error:", chrome.runtime.lastError);
                    return;
                }
                
                console.log("DEBUG FULL RESPONSE:", response);
                if (response && typeof response.status !== 'undefined' && response.status >= 200 && response.status < 300) {
                    console.log(`[CATDAMS Backend] POST success: ${sender} "${text.slice(0, 30)}..."`);
                } else if (response && typeof response.status !== 'undefined') {
                    console.error("[CATDAMS Backend] POST fail", response.status);
                    // If we get a 429, increase backoff time
                    if (response.status === 429) {
                        isRateLimited = true;
                        currentBackoffTime = Math.min(currentBackoffTime * 2, RATE_LIMIT_CONFIG.maxBackoffTime);
                        console.warn('[CATDAMS] 429 detected, increasing backoff to', currentBackoffTime, 'ms');
                    }
                } else if (response && response.error) {
                    console.error("[CATDAMS Backend] POST error", response.error);
                } else {
                    console.warn("[CATDAMS Backend] No valid response object received.");
                }
            });
        } else {
            console.warn("[CATDAMS] sendMessage not available in this context.");
        }
    } catch (err) {
        console.error("[CATDAMS] Extension context invalidated. Could not send message.", err);
    }
}

// ======= Selector Helper Functions =======
function isMessageComplete(element, platform = "universal") {
    if (!element) return false;
    
    // Check if element is still being typed (has cursor or is actively being updated)
    if (element.matches(':focus') || element.querySelector(':focus')) {
        return false;
    }
    
    // Platform-specific completion checks
    switch (platform) {
        case "deepseek":
            // DeepSeek messages are complete when they have the full markdown structure
            return element.querySelector('.ds-markdown-paragraph') !== null;
        case "gemini":
            // Gemini messages are complete when they have the bubble structure
            return element.querySelector('[data-testid="bubble"]') !== null;
        case "candy":
            // Candy.ai messages are complete when they have the ai-message class
            return element.classList.contains('ai-message') || element.querySelector('.ai-message') !== null;
        default:
            // Universal: check if element has substantial content and isn't actively being updated
            const text = element.innerText || element.textContent || '';
            return text.trim().length > 10 && !element.matches('[contenteditable="true"]:focus');
    }
}

// ======= DeepSeek Specific Functions (Working) =======
function extractDeepSeekUserPrompt() {
    const userSelectors = [
        'textarea#chat-input',
        'div[contenteditable="true"]',
        'input[type="text"]',
        '.user-message',
        '.human-message'
    ];
    
    for (const selector of userSelectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            const lastElement = elements[elements.length - 1];
            const text = lastElement.value || lastElement.innerText || lastElement.textContent || '';
            if (text.trim()) {
                return text.trim();
            }
        }
    }
    return "";
}

function extractDeepSeekAIResponse() {
    const aiSelectors = [
        '.ds-markdown-paragraph',
        '.chat-message',
        '.markdown',
        '[data-testid="chat-message"]',
        'div.ds-markdown-block'
    ];
    
    let aiResponse = "";
    for (const selector of aiSelectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            const lastElement = elements[elements.length - 1];
            if (lastElement && isMessageComplete(lastElement, "deepseek")) {
                aiResponse = lastElement.innerText.trim();
                break;
            }
        }
    }
    return aiResponse;
}

function deepseekCaptureBoth() {
    if (!window.location.hostname.includes('deepseek.com')) return false;
    
    function logBoth() {
        const userPrompt = extractDeepSeekUserPrompt();
        const aiResponse = extractDeepSeekAIResponse();
        
        if (userPrompt) {
            console.log('[CATDAMS][DeepSeek][USER] Logging User:', userPrompt);
            logMessageOnce(userPrompt, "USER", "deepseek");
        }
        
        if (aiResponse && aiResponse !== lastLoggedAI_deepseek) {
            console.log('[CATDAMS][DeepSeek][AI] Logging AI:', aiResponse);
            logMessageOnce(aiResponse, "AI", "deepseek");
            lastLoggedAI_deepseek = aiResponse;
        }
    }
    
    // Enhanced user input capture with debouncing
    const inputElements = document.querySelectorAll('textarea#chat-input, div[contenteditable="true"], input[type="text"]');
    inputElements.forEach(inputElement => {
        if (inputElement.__catdams_listener) return;
        inputElement.__catdams_listener = true;
        
        // Debounce function to prevent rapid firing
        let debounceTimer;
        inputElement.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(logBoth, 100); // Short delay for DeepSeek
            }
        });
    });
    
    // Scoped MutationObserver for AI responses
    const chatContainer = document.querySelector('main') || document.querySelector('.chat-container') || document.body;
    if (chatContainer && !chatContainer.__catdams_deepseek_observer) {
        let lastMutationTime = 0;
        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            // Only process if we have added nodes and enough time has passed
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes && (now - lastMutationTime > 1000)) { // 1 second minimum between mutations
                lastMutationTime = now;
                setTimeout(logBoth, 500); // Short delay for DeepSeek
            }
        });
        
        observer.observe(chatContainer, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
        
        chatContainer.__catdams_deepseek_observer = true;
    }
    
    setTimeout(deepseekCaptureBoth, 3000); // Regular interval for DeepSeek
    return true;
}

// ======= Gemini Specific Functions =======
function scanGeminiAIResponse() {
    const aiSelectors = getSelectorsForDomain(window.location.hostname, "ai");
    
    let aiResponse = "";
    for (const selector of aiSelectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            const lastElement = elements[elements.length - 1];
            if (lastElement && isMessageComplete(lastElement, "gemini")) {
                aiResponse = lastElement.innerText.trim();
                break;
            }
        }
    }
    return aiResponse;
}

function geminiUserInputCapture() {
    if (!window.location.hostname.includes('gemini.google.com')) return false;
    let lastGeminiPrompt = "";
    
    function scanGeminiUserPrompt() {
        const userSelectors = getSelectorsForDomain(window.location.hostname, "user");
        
        for (const selector of userSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                const text = lastElement.value || lastElement.innerText || lastElement.textContent || '';
                if (text.trim() && text.trim() !== lastGeminiPrompt) {
                    lastGeminiPrompt = text.trim();
                    console.log('[CATDAMS][Gemini][USER] Logging User:', lastGeminiPrompt);
                    logMessageOnce(lastGeminiPrompt, "USER", "gemini");
                }
            }
        }
    }
    
    // Enhanced user input capture with debouncing
    const inputElements = document.querySelectorAll('textarea, div[contenteditable="true"], input[type="text"]');
    inputElements.forEach(inputElement => {
        if (inputElement.__catdams_listener) return;
        inputElement.__catdams_listener = true;
        
        // Debounce function to prevent rapid firing
        let debounceTimer;
        inputElement.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(scanGeminiUserPrompt, 100); // Short delay for Gemini
            }
        });
    });
    
    // Scoped MutationObserver for AI responses
    let chatRoot = document.querySelector('main') || document.body;
    if (chatRoot && !chatRoot.__catdams_gemini_observer) {
        const observer = new MutationObserver((mutations) => {
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes) {
                const aiReply = scanGeminiAIResponse();
                if (aiReply && aiReply !== lastLoggedAI_gemini) {
                    logMessageOnce(aiReply, "AI", "gemini");
                    lastLoggedAI_gemini = aiReply;
                }
            }
        });
        observer.observe(chatRoot, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
        chatRoot.__catdams_gemini_observer = true;
    }
    
    setTimeout(scanGeminiUserPrompt, 2000);
    return true;
}

// ======= ChatGPT Specific Functions =======
function chatgptUserInputCapture() {
    if (!window.location.hostname.includes('chat.openai.com') && !window.location.hostname.includes('chatgpt.com')) return false;
    
    let lastLoggedUser_chatgpt = "";
    function scanChatGPTMessages() {
        const userSelectors = [
            '[data-message-author-role="user"]',
            '.user-message',
            '.human-message'
        ];
        const aiSelectors = [
            '[data-message-author-role="assistant"]',
            '.assistant-message',
            '.ai-message'
        ];
        // Scan for user messages in chat history
        for (const selector of userSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                const text = lastElement.innerText || lastElement.textContent || '';
                if (text.trim() && text.trim() !== lastLoggedUser_chatgpt) {
                    console.log('[CATDAMS][ChatGPT][USER] Logging User:', text.trim());
                    logMessageOnce(text.trim(), "USER", "chatgpt");
                    lastLoggedUser_chatgpt = text.trim();
                }
            }
        }
        // Fallback: check main textarea input (for new messages not yet in chat)
        const inputBox = document.querySelector('textarea, div[contenteditable="true"]');
        if (inputBox) {
            let text = inputBox.value || inputBox.innerText || inputBox.textContent || '';
            if (text.trim() && text.trim() !== lastLoggedUser_chatgpt) {
                console.log('[CATDAMS][ChatGPT][USER][Fallback] Logging User:', text.trim());
                logMessageOnce(text.trim(), "USER", "chatgpt");
                lastLoggedUser_chatgpt = text.trim();
            }
        }
        // Scan for AI messages
        for (const selector of aiSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                if (lastElement && isMessageComplete(lastElement, "chatgpt")) {
                    const text = lastElement.innerText || lastElement.textContent || '';
                    if (text.trim() && text.trim() !== lastLoggedAI_chatgpt) {
                        console.log('[CATDAMS][ChatGPT][AI] Logging AI:', text.trim());
                        logMessageOnce(text.trim(), "AI", "chatgpt");
                        lastLoggedAI_chatgpt = text.trim();
                    }
                }
            }
        }
    }
    // Enhanced user input capture with debouncing
    const inputElements = document.querySelectorAll('textarea, div[contenteditable="true"], input[type="text"]');
    inputElements.forEach(inputElement => {
        if (inputElement.__catdams_listener) return;
        inputElement.__catdams_listener = true;
        let debounceTimer;
        inputElement.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(scanChatGPTMessages, 100);
            }
        });
    });
    // Scoped MutationObserver for AI responses
    const chatContainer = document.querySelector('main') || document.querySelector('.chat-container') || document.body;
    if (chatContainer && !chatContainer.__catdams_chatgpt_observer) {
        let lastMutationTime = 0;
        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes && (now - lastMutationTime > 1000)) {
                lastMutationTime = now;
                setTimeout(scanChatGPTMessages, 500);
            }
        });
        observer.observe(chatContainer, { childList: true, subtree: true, attributes: false, characterData: false });
        chatContainer.__catdams_chatgpt_observer = true;
    }
    setTimeout(scanChatGPTMessages, 2000);
    return true;
}

// ======= Candy.ai Specific Functions =======
function candyCaptureBoth() {
    if (!window.location.hostname.includes('candy.ai')) return false;
    
    function logBoth() {
        const userSelectors = [
            'textarea[placeholder*="Message"]',
            'div[contenteditable="true"]',
            'input[type="text"]'
        ];
        
        const aiSelectors = [
            '.ai-message',
            '.bot-message',
            '.assistant-message',
            '.response',
            '.message.ai',
            '.chat-message.ai'
        ];
        
        let userPrompt = "";
        for (const selector of userSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                const text = lastElement.value || lastElement.innerText || lastElement.textContent || '';
                if (text.trim()) {
                    userPrompt = text.trim();
                    break;
                }
            }
        }
        
        let aiResponse = "";
        for (const selector of aiSelectors) {
            const aiElements = document.querySelectorAll(selector);
            if (aiElements.length) {
                const lastAI = aiElements[aiElements.length - 1];
                if (lastAI && isMessageComplete(lastAI, "candy")) {
                    aiResponse = lastAI.innerText.trim();
                    break;
                }
            }
        }
        
        if (userPrompt) {
            console.log('[CATDAMS][Candy.ai][USER] Logging User:', userPrompt);
            logMessageOnce(userPrompt, "USER", "candy");
        }
        
        if (aiResponse && aiResponse !== lastLoggedAI_candy) {
            console.log('[CATDAMS][Candy.ai][AI] Logging AI:', aiResponse);
            logMessageOnce(aiResponse, "AI", "candy");
            lastLoggedAI_candy = aiResponse;
        }
    }
    
    // Enhanced user input capture with debouncing
    const inputElements = document.querySelectorAll('textarea, div[contenteditable="true"], input[type="text"]');
    inputElements.forEach(inputElement => {
        if (inputElement.__catdams_listener) return;
        inputElement.__catdams_listener = true;
        
        // Debounce function to prevent rapid firing
        let debounceTimer;
        inputElement.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(logBoth, 500); // Increased delay for candy.ai
            }
        });
    });
    
    // Scoped MutationObserver for AI responses with longer delays
    const chatContainer = document.querySelector('main') || document.querySelector('.chat-container') || document.body;
    if (chatContainer && !chatContainer.__catdams_candy_observer) {
        let lastMutationTime = 0;
        const observer = new MutationObserver((mutations) => {
            const now = Date.now();
            // Only process if we have added nodes and enough time has passed
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes && (now - lastMutationTime > 2000)) { // 2 second minimum between mutations
                lastMutationTime = now;
                setTimeout(logBoth, 1000); // Longer delay for candy.ai
            }
        });
        
        observer.observe(chatContainer, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
        
        chatContainer.__catdams_candy_observer = true;
    }
    
    setTimeout(candyCaptureBoth, 5000); // Longer interval for candy.ai
    return true;
}

// ======= Universal Fallback (Best Practice Deduplication) =======
function captureUserInputUniversal() {
    let inputBoxes = Array.from(document.querySelectorAll('textarea, [contenteditable="true"], input[type="text"]'));
    inputBoxes.forEach(inputBox => {
        if (inputBox.__catdams_listener) return;
        inputBox.__catdams_listener = true;
        inputBox.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                setTimeout(() => {
                    const userInput = inputBox.value || inputBox.textContent || '';
                    if (userInput.trim()) {
                        console.log('[CATDAMS][Universal][USER] Logging User:', userInput.trim());
                        logMessageOnce(userInput.trim(), "USER", "universal");
                    }
                }, 100);
            }
        });
    });
    // AI response logging via MutationObserver with best-practice deduplication
    let mainEl = document.querySelector('main') || document.body;
    if (mainEl && !mainEl.__catdams_universal_observer) {
        const observer = new MutationObserver((mutations) => {
            // Only process if we have added nodes
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes) {
                const aiSelectors = [
                    '.prose.ai',
                    '.markdown.ai',
                    '.chat__message.ai',
                    '.message.ai',
                    '.ai',
                    '.assistant',
                    '.bot',
                    '.response'
                ];
                
                for (const selector of aiSelectors) {
                    const aiBlocks = Array.from(document.querySelectorAll(selector));
                    if (aiBlocks.length) {
                        const lastAI = aiBlocks[aiBlocks.length - 1];
                        if (lastAI && isMessageComplete(lastAI, "universal")) {
                            const aiText = lastAI.innerText.trim();
                            if (aiText && aiText !== lastLoggedAI_universal) {
                                console.log('[CATDAMS][Universal][AI] Logging AI:', aiText);
                                logMessageOnce(aiText, "AI", "universal");
                                lastLoggedAI_universal = aiText;
                                break;
                            }
                        }
                    }
                }
            }
        });
        observer.observe(mainEl, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
        mainEl.__catdams_universal_observer = true;
    }
    setTimeout(captureUserInputUniversal, 3000);
}

// ======= AI Output Processing (unchanged fallback) =======
function scanAndProcessMessages() {
    const aiSelectors = getSelectorsForDomain(window.location.hostname, "ai");
    const userSelectors = getSelectorsForDomain(window.location.hostname, "user");
    const messages = [];
    
    // Scan for AI messages
    aiSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(msgDiv => {
            if (!messages.includes(msgDiv)) messages.push(msgDiv);
        });
    });
    
    // Scan for user messages
    userSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(msgDiv => {
            if (!messages.includes(msgDiv)) messages.push(msgDiv);
        });
    });
    
    messages.forEach(msgDiv => {
        const text = (msgDiv.innerText || msgDiv.textContent || '').trim();
        if (!text) return;
        
        // Determine if this is a user or AI message based on selectors
        const isUserMessage = userSelectors.some(selector => msgDiv.matches(selector));
        const messageType = isUserMessage ? "USER" : "AI";
        
        if (FORENSIC_MODE) {
            logMessageOnce(text, messageType, "universal");
        } else {
            if (messageTimers.has(msgDiv)) {
                clearTimeout(messageTimers.get(msgDiv));
            }
            const timer = setTimeout(() => {
                const finalText = (msgDiv.innerText || msgDiv.textContent || '').trim();
                if (isMessageComplete(msgDiv, "universal")) {
                    logMessageOnce(finalText, messageType, "universal");
                }
            }, 2000);
            messageTimers.set(msgDiv, timer);
        }
    });
}

// ======= Init Observers =======
function startObservingChat() {
    let mainEl = document.querySelector('main') || document.body;
    if (mainEl) {
        const observer = new MutationObserver((mutations) => {
            // Only process if we have added nodes
            const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
            if (hasAddedNodes) {
                scanAndProcessMessages();
            }
        });
        observer.observe(mainEl, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
        scanAndProcessMessages();
        console.log(
            FORENSIC_MODE
                ? "[CATDAMS] Enhanced forensic mode: logging ALL partials and finals (multi-platform)."
                : "[CATDAMS] Enhanced normal mode: logging only finalized, unique messages (multi-platform)."
        );
    } else {
        setTimeout(startObservingChat, 1000);
    }
}

// ======= Initialization =======
window.addEventListener('DOMContentLoaded', startObservingChat);
setTimeout(chatgptUserInputCapture, 500);
setTimeout(geminiUserInputCapture, 500);
setTimeout(deepseekCaptureBoth, 500);
setTimeout(candyCaptureBoth, 500);
setTimeout(captureUserInputUniversal, 1000);
setTimeout(startObservingChat, 2000);

// ======= REAL-TIME THREAT ALERTS =======
function showThreatAlert(threatAnalysis, message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.id = 'catdams-threat-alert';
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${threatAnalysis.severity === 'Critical' ? '#ff4444' : 
                     threatAnalysis.severity === 'High' ? '#ff8800' : 
                     threatAnalysis.severity === 'Medium' ? '#ffcc00' : '#44ff44'};
        color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        max-width: 400px;
        font-family: Arial, sans-serif;
        font-size: 14px;
        border-left: 5px solid ${threatAnalysis.severity === 'Critical' ? '#cc0000' : 
                               threatAnalysis.severity === 'High' ? '#cc6600' : 
                               threatAnalysis.severity === 'Medium' ? '#cc9900' : '#00cc00'};
    `;
    const threatTypes = threatAnalysis.threats.map(t => t.type.replace(/_/g, ' ')).join(', ');
    alertDiv.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">
            ⚠️ CATDAMS Threat Alert (${threatAnalysis.severity})
        </div>
        <div style="margin-bottom: 8px;">
            <strong>Threat Types:</strong> ${threatTypes}
        </div>
        <div style="font-size: 12px; opacity: 0.9;">
            ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}
        </div>
        <button onclick="this.parentElement.remove()" style="
            position: absolute;
            top: 5px;
            right: 5px;
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
        ">×</button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 10000);
}

// ========== END OF ENHANCED CATDAMS UNIVERSAL SCRIPT ==========
