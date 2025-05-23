 // ==CATDAMS Gemini Chat Logger (Updated & Refined Selectors, Fixed for Backend)==
// Purpose: Reliably log user prompts and AI responses from Google Gemini for CATDAMS backend.

console.log("CATDAMS Gemini Chat Logger Loaded (Backend Fix Build).");

// --- Configuration ---
const CONFIG = {
    BACKEND_ENDPOINT: 'https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest',
    AGENT_ID: "catdams-gemini-ext",
    USER_ID: "michael-varga",
    AGENT_VERSION: "v1.4.1",
    POLICY_VERSION: "2024-05",
    PROCESS_DEBOUNCE_DELAY: 1200,
    INITIAL_LOAD_DELAY: 3500
};

// --- Persistent Session ID (per tab/window) ---
const SESSION_ID = `sess-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 8)}`;

// --- DOM Selectors for Google Gemini ---
const GEMINI_SELECTORS = {
    inputArea: 'div[contenteditable="true"][role="textbox"]',
    chatTranscriptItem: 'div[role="listitem"], div[data-testid*="chat-message"]',
    userMessageContent: [
        'div[data-is-user-message="true"]',
        'div.message-item-text-model-id-user',
        'div.user-text-content',
        'span[data-text-content]'
    ],
    aiMessageContent: [
        'div[data-is-ai-response="true"]',
        'div.message-item-text-model-id-2',
        'div.model-response-content',
        'span[data-text-content]'
    ],
    sendButton: 'button[aria-label="Send message"], button[data-testid="send-button"], div.send-button'
};

/**
 * Recursively finds elements within a given root, piercing open Shadow DOMs.
 */
function findElementsInDOM(root, selector) {
    let foundElements = [];
    try {
        foundElements = Array.from(root.querySelectorAll(selector));
    } catch (e) {
        console.warn(`[CATDAMS-DOM] QuerySelector failed for "${selector}" on root:`, root, e);
    }
    const shadowRoots = Array.from(root.querySelectorAll('*'))
        .filter(el => el.shadowRoot && el.shadowRoot.mode === 'open')
        .map(el => el.shadowRoot);
    for (const shadowRootEl of shadowRoots) {
        foundElements = foundElements.concat(findElementsInDOM(shadowRootEl, selector));
    }
    return foundElements;
}

/**
 * Extracts the latest user prompt and AI response from the Gemini DOM.
 * If selectors fail, attempts brute-force fallback extraction.
 */
function extractChat() {
    let userPrompt = "";
    let aiResponse = "";
    let extractedUserBubbleText = "";
    let extractedAiBubbleText = "";

    // Step 1: Get User Prompt
    const inputArea = findElementsInDOM(document.body, GEMINI_SELECTORS.inputArea)[0];
    if (inputArea && inputArea.innerText) {
        userPrompt = inputArea.innerText.trim();
    }

    // Then, find the last displayed message from the transcript
    const chatItems = findElementsInDOM(document.body, GEMINI_SELECTORS.chatTranscriptItem);

    if (chatItems.length > 0) {
        const lastChatItem = chatItems[chatItems.length - 1];

        // Try to find user message content within the last chat item
        for (const sel of GEMINI_SELECTORS.userMessageContent) {
            const userTextEl = findElementsInDOM(lastChatItem, sel)[0];
            if (userTextEl && userTextEl.innerText) {
                extractedUserBubbleText = userTextEl.innerText.trim();
                break;
            }
        }

        if (extractedUserBubbleText && extractedUserBubbleText !== userPrompt) {
            userPrompt = extractedUserBubbleText;
        }

        // Step 2: Get AI Response
        for (const sel of GEMINI_SELECTORS.aiMessageContent) {
            const aiTextEl = findElementsInDOM(lastChatItem, sel)[0];
            if (aiTextEl && aiTextEl.innerText) {
                extractedAiBubbleText = aiTextEl.innerText.trim();
                break;
            }
        }
    }

    aiResponse = extractedAiBubbleText;

    // Brute-force fallback: If either userPrompt or aiResponse is missing, get two largest visible text blobs as last resort
    if (!userPrompt || !aiResponse) {
        const allSpans = Array.from(document.body.querySelectorAll('span,div'));
        const textSpans = allSpans.filter(el =>
            el.offsetParent !== null && el.innerText && el.innerText.trim().length > 0
        );
        textSpans.sort((a, b) => b.innerText.length - a.innerText.length);
        if (!userPrompt && textSpans[0]) userPrompt = textSpans[0].innerText.trim();
        if (!aiResponse && textSpans[1]) aiResponse = textSpans[1].innerText.trim();
    }

    return { userPrompt, aiResponse };
}

/**
 * Builds the data payload according to the defined schema (no title, no url).
 */
function buildPayload(userPrompt, aiResponse) {
    const now = new Date().toISOString();
    return {
        agent_id: CONFIG.AGENT_ID,
        session_id: SESSION_ID,
        user_id: CONFIG.USER_ID,
        timestamp: now,
        messages: [
            {
                sequence: 1,
                sender: "user",
                text: userPrompt || "",
                time: now
            },
            {
                sequence: 2,
                sender: "ai",
                text: aiResponse || "",
                time: now
            }
        ],
        metadata: {
            agent_version: CONFIG.AGENT_VERSION,
            policy_version: CONFIG.POLICY_VERSION,
            os: navigator.platform,
            application: "Google-Gemini-Web",
            language: navigator.language || "en-US"
            // (REMOVED) url, title
        }
    };
}

/**
 * Posts the constructed payload to the backend.
 */
async function postToBackend(payload) {
    console.log("[CATDAMS-Backend] Outgoing payload:", JSON.stringify(payload, null, 2));
    try {
        const res = await fetch(CONFIG.BACKEND_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const errorText = await res.text();
            console.error(`[CATDAMS-Backend ERROR] Backend response not OK (${res.status}):`, errorText);
        } else {
            console.log("[CATDAMS-Backend SUCCESS] Data sent to backend.");
        }
    } catch (err) {
        console.error("[CATDAMS-Backend ERROR] Network or fetch operation failed:", err);
    }
}

// --- Main Logging Logic with Deduplication and Debouncing ---
let lastLoggedUserPrompt = "";
let lastLoggedAiResponse = "";
let processChatTimeout = null;

/**
 * Core logic: extracts, checks, and sends data. Debounced for stability.
 */
function processAndSendChatData() {
    clearTimeout(processChatTimeout);

    processChatTimeout = setTimeout(() => {
        const { userPrompt, aiResponse } = extractChat();

        if (!userPrompt || !aiResponse) {
            return;
        }

        // Deduplication: Only send if this specific pair hasn't been logged before.
        if (userPrompt === lastLoggedUserPrompt && aiResponse === lastLoggedAiResponse) {
            return;
        }

        const payload = buildPayload(userPrompt, aiResponse);
        postToBackend(payload);

        lastLoggedUserPrompt = userPrompt;
        lastLoggedAiResponse = aiResponse;

    }, CONFIG.PROCESS_DEBOUNCE_DELAY);
}

// --- Event Listeners and Observers ---

// 1. MutationObserver for dynamic content changes
const observer = new MutationObserver(() => {
    processAndSendChatData();
});
observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: false
});
console.log("[CATDAMS] MutationObserver initialized on document.body.");

// 2. Optional: Direct trigger for "Send message" button clicks
let sendButtonObserver = null;
function attachSendButtonListener() {
    const sendButton = findElementsInDOM(document.body, GEMINI_SELECTORS.sendButton)[0];
    if (sendButton) {
        if (!sendButton.__catdams_listener_attached) {
            sendButton.addEventListener('click', () => {
                setTimeout(processAndSendChatData, 100);
            });
            sendButton.__catdams_listener_attached = true;
            if (sendButtonObserver) {
                sendButtonObserver.disconnect();
                sendButtonObserver = null;
            }
        }
    } else {
        if (!sendButtonObserver) {
            sendButtonObserver = new MutationObserver(() => {
                attachSendButtonListener();
            });
            const chatInputArea = findElementsInDOM(document.body, 'form[role="complementary"]')[0] || document.body;
            sendButtonObserver.observe(chatInputArea, { childList: true, subtree: true });
        }
    }
}
attachSendButtonListener();

// 3. Optional: Listen for Enter key press in the contenteditable div
document.addEventListener('keydown', (event) => {
    const inputArea = findElementsInDOM(document.body, GEMINI_SELECTORS.inputArea)[0];
    if (event.key === 'Enter' && event.target === inputArea) {
        setTimeout(processAndSendChatData, 100);
    }
});

// 4. Initial check on page load, ensuring DOM is fully ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        processAndSendChatData();
    }, CONFIG.INITIAL_LOAD_DELAY);
});

// Fallback for cases where DOMContentLoaded already fired
if (document.readyState === 'complete') {
    setTimeout(() => {
        processAndSendChatData();
    }, CONFIG.INITIAL_LOAD_DELAY);
}
