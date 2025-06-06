// ====== CATDAMS Universal content script v2.6 (June 2025) ======
// Logs both user input (prompts) and AI output (responses) for all major chat/companion platforms

console.log("CATDAMS AI Chat Detector: Universal monitoring loaded on", window.location.hostname);

// === CONFIGURATION ===
const FORENSIC_MODE = false; // true = log every update, false = only final
const LOG_HISTORY_SIZE = 100;
const BACKEND_ENDPOINT = "http://localhost:8000/event";

// ======= SESSION ID MANAGEMENT =======
function generateSessionID() {
    // RFC4122 version 4 compliant UUID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Assign a unique session ID per tab/session
const CATDAMS_SESSION_ID = generateSessionID();

// ======= Deduplication =======
const messageTimers = new WeakMap();
const loggedMessages = [];
function logMessageOnce(text, source = "AI") {
    if (!text) return;
    const normText = (source + ":" + text.replace(/\s+/g, ' ').trim());
    if (loggedMessages.includes(normText)) return;
    loggedMessages.push(normText);
    if (loggedMessages.length > LOG_HISTORY_SIZE) loggedMessages.shift();
    console.log(`[CATDAMS] ${source} Message captured:`, text);
    postMessageToBackend(text, source);
}

// ======= POST TO BACKEND (VIA BACKGROUND SCRIPT) =======
function postMessageToBackend(text, sender) {
    const now = new Date().toISOString();
    const payload = {
        time: now,
        type: "Chat Interaction",      // Fill this in with actual type if you have it!
        severity: sender === "AI" ? "Medium" : "Low",
        source: window.location.hostname,
        country: "US",                 // Optionally geolocate for real country
        message: text,
        sender: sender,
        session_id: CATDAMS_SESSION_ID // <<=== SESSION ID ADDED HERE
    };
    chrome.runtime.sendMessage({
        type: "catdams_log",
        payload: payload
    }, (response) => {
        console.log("DEBUG FULL RESPONSE:", response);
        if (response && response.status && response.status >= 200 && response.status < 300) {
            console.log(`[CATDAMS Backend] POST success: ${sender} "${text.slice(0, 30)}..."`);
        } else if (response && response.status) {
            console.error("[CATDAMS Backend] POST fail", response.status);
        } else if (response && response.error) {
            console.error("[CATDAMS Backend] POST error", response.error);
        }
    });
}

// ======= SELECTORS (Old Code, Preserved) =======
const SELECTORS_BY_DOMAIN = {
    "chat.openai.com": [
        '.flex.flex-col.items-center > div',
        '.prose', '.markdown',
        '[data-message-author-role="assistant"]',
        '[data-message-author-role="user"]'
    ],
    "chatgpt.com": [
        '.flex.flex-col.items-center > div', '.prose', '.markdown',
        '[data-message-author-role="assistant"]', '[data-message-author-role="user"]'
    ],
    "gemini.google.com": [
        '[data-testid="bubble"]',
        '.ProseMirror',
        '.conversation-turn',
        '.markdown',
        'textarea',
        'div[aria-label="User input"]',
        '.leading-actions-wrapper'
    ],
    "bard.google.com": [
        '.markdown', '.ProseMirror', '.conversation-turn',
        '[data-testid="bubble"]', 'textarea'
    ],
    "chat.deepseek.com": [
        '.ds-markdown-paragraph',
        'textarea#chat-input',
        '.chat-message', '.markdown', '[data-testid="chat-message"]',
        'div.ds-markdown-block'
    ],
    "deepseek.com": [
        '.ds-markdown-paragraph', 'textarea#chat-input', '.chat-message', '.markdown', '[data-testid="chat-message"]'
    ]
};

const UNIVERSAL_SELECTORS = [
    '[data-testid*="message"]', '[data-testid*="chat"]',
    '[class*="message"]', '[class*="chat"]',
    '.prose', '.markdown', '.msg', '.text-lg', '.conversation-turn', '.message__text', '.chat__message'
];

// ======= Platform-aware selectors =======
function getSelectorsForDomain(domain) {
    const bareDomain = domain.replace(/^www\./, '');
    return SELECTORS_BY_DOMAIN[domain] || SELECTORS_BY_DOMAIN[bareDomain] || UNIVERSAL_SELECTORS;
}

// ======= DeepSeek Extraction (FULL LEGACY) =======
function extractDeepSeekUserPrompt() {
    let userPrompt = "";
    const chatList = document.querySelector('main div[class*="overflow"]') || document.querySelector('main > div > div');
    if (chatList) {
        const allChildren = Array.from(chatList.children).filter(n => n.innerText && n.innerText.trim().length > 0);
        if (allChildren.length) {
            let candidate = null;
            if (allChildren.length % 2 === 0) {
                candidate = allChildren[allChildren.length - 2];
            } else {
                candidate = allChildren[allChildren.length - 1];
            }
            if (candidate && candidate.innerText) {
                userPrompt = candidate.innerText.trim();
            }
        }
    }
    if (!userPrompt) {
        const userDivs = Array.from(document.querySelectorAll('div[class^="9"], div[class^="8"], div[class^="7"], div[class^="6"], div[class^="5"], div[class^="4"], div[class^="3"], div[class^="2"], div[class^="1"]'));
        if (userDivs.length) {
            userPrompt = userDivs[userDivs.length - 1].innerText.trim();
        }
    }
    if (!userPrompt) {
        const textarea = document.querySelector('textarea#chat-input');
        if (textarea && textarea.value.trim()) {
            userPrompt = textarea.value.trim();
        }
    }
    return userPrompt;
}

function extractDeepSeekAIResponse() {
    let aiResponse = "";
    const aiBlocks = Array.from(document.querySelectorAll('div.ds-markdown-block'));
    if (aiBlocks.length) {
        const lastAIBlock = aiBlocks[aiBlocks.length - 1];
        let parts = [];
        lastAIBlock.querySelectorAll('p,li,pre,code').forEach(el => {
            if (el.innerText && el.offsetParent !== null) parts.push(el.innerText.trim());
        });
        aiResponse = parts.join('\n').replace(/\n{2,}/g, '\n').trim();
        if (!aiResponse && lastAIBlock.innerText) aiResponse = lastAIBlock.innerText.trim();
    }
    return aiResponse;
}

function deepseekCaptureBoth() {
    if (!window.location.hostname.includes('deepseek')) return false;

    function logBoth() {
        const userPrompt = extractDeepSeekUserPrompt();
        const aiResponse = extractDeepSeekAIResponse();
        if (userPrompt) logMessageOnce(userPrompt, "USER");
        if (aiResponse) logMessageOnce(aiResponse, "AI");
    }

    const textarea = document.querySelector('textarea#chat-input');
    if (textarea && !textarea.__catdams_listener) {
        textarea.__catdams_listener = true;
        textarea.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                setTimeout(logBoth, 100);
            }
        });
    }

    let mainEl = document.querySelector('main') || document.body;
    if (mainEl && !mainEl.__catdams_deepseek_observer) {
        const observer = new MutationObserver(() => setTimeout(logBoth, 150));
        observer.observe(mainEl, { childList: true, subtree: true });
        mainEl.__catdams_deepseek_observer = true;
    }
    setTimeout(deepseekCaptureBoth, 3000);
    return true;
}

// ======= Gemini Extraction (LEGACY) =======
function geminiUserInputCapture() {
    if (!window.location.hostname.includes('gemini.google.com')) return false;

    let lastGeminiPrompt = "";

    function scanGeminiUserPrompt() {
        const userBubbles = Array.from(document.querySelectorAll(
            'div.user-query-container, div[role="heading"][aria-level="2"], div.horizontal-content-container'
        ));
        if (userBubbles.length) {
            let last = userBubbles[userBubbles.length - 1];
            if (last) {
                let userPrompt = last.innerText || last.textContent || '';
                userPrompt = userPrompt.trim();
                if (
                    userPrompt &&
                    userPrompt !== lastGeminiPrompt &&
                    typeof logMessageOnce === "function" &&
                    !loggedMessages.includes("USER:" + userPrompt)
                ) {
                    lastGeminiPrompt = userPrompt;
                    logMessageOnce(userPrompt, "USER");
                }
            }
        }
    }
    let chatRoot = document.querySelector('main') || document.body;
    if (chatRoot && !chatRoot.__catdams_gemini_observer) {
        const observer = new MutationObserver(() => setTimeout(scanGeminiUserPrompt, 120));
        observer.observe(chatRoot, { childList: true, subtree: true });
        chatRoot.__catdams_gemini_observer = true;
    }
    setTimeout(scanGeminiUserPrompt, 2000);
    setTimeout(geminiUserInputCapture, 3000);
    return true;
}

// ======= ChatGPT Extraction (LEGACY) =======
function chatgptUserInputCapture() {
    if (!window.location.hostname.includes('chat.openai.com')) return false;
    let textarea = document.querySelector('textarea');
    if (textarea) {
        if (!textarea.__catdams_listener) {
            textarea.__catdams_listener = true;
            textarea.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    setTimeout(() => {
                        const userInput = textarea.value || textarea.textContent || '';
                        if (userInput.trim()) {
                            logMessageOnce(userInput.trim(), "USER");
                        }
                    }, 30);
                }
            });
        }
    }
    setTimeout(chatgptUserInputCapture, 3000);
    return true;
}

// ======= Universal Input Fallback (LEGACY) =======
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
                        logMessageOnce(userInput.trim(), "USER");
                    }
                }, 30);
            }
        });
        let sendBtn = inputBox.parentNode && inputBox.parentNode.querySelector('button, [role="button"]');
        if (sendBtn && !sendBtn.__catdams_listener) {
            sendBtn.__catdams_listener = true;
            sendBtn.addEventListener('click', () => {
                setTimeout(() => {
                    const userInput = inputBox.value || inputBox.textContent || '';
                    if (userInput.trim()) {
                        logMessageOnce(userInput.trim(), "USER");
                    }
                }, 30);
            });
        }
    });
    setTimeout(captureUserInputUniversal, 3000);
}

// ======= AI Output Capture =======
function scanAndProcessMessages() {
    const selectors = getSelectorsForDomain(window.location.hostname);
    const messages = [];
    selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(msgDiv => {
            if (!messages.includes(msgDiv)) messages.push(msgDiv);
        });
    });
    messages.forEach(msgDiv => {
        const text = (msgDiv.innerText || msgDiv.textContent || '').trim();
        if (!text) return;
        if (FORENSIC_MODE) {
            logMessageOnce(text, "AI");
        } else {
            if (messageTimers.has(msgDiv)) {
                clearTimeout(messageTimers.get(msgDiv));
            }
            const timer = setTimeout(() => {
                const finalText = (msgDiv.innerText || msgDiv.textContent || '').trim();
                logMessageOnce(finalText, "AI");
            }, 2000);
            messageTimers.set(msgDiv, timer);
        }
    });
}

// ======= Main Observer Logic =======
function startObservingChat() {
    let mainEl = document.querySelector('main') || document.body;
    if (mainEl) {
        const observer = new MutationObserver(scanAndProcessMessages);
        observer.observe(mainEl, { childList: true, subtree: true });
        scanAndProcessMessages();
        console.log(
            FORENSIC_MODE
                ? "[CATDAMS] Forensic mode: logging ALL partials and finals (multi-platform)."
                : "[CATDAMS] Normal mode: logging only finalized, unique messages (multi-platform)."
        );
    } else {
        setTimeout(startObservingChat, 1000);
    }
}

// ======= Initialize =======
window.addEventListener('DOMContentLoaded', startObservingChat);

setTimeout(chatgptUserInputCapture, 500);
setTimeout(geminiUserInputCapture, 500);
setTimeout(deepseekCaptureBoth, 500);

setTimeout(captureUserInputUniversal, 1000);
setTimeout(startObservingChat, 2000);

// ========== END OF CATDAMS UNIVERSAL SCRIPT ==========
