// ==CATDAMS Universal AI Chat Logger (Top 10 Platforms)==
// Detects/logs user and AI chats on 10 major chatbots. Backend-ready and privacy-first.

console.log("CATDAMS Universal AI Chat Logger Loaded.");

// --- Anonymous User ID (per browser install) ---
function getOrCreateUserId() {
    let uid = localStorage.getItem("catdams_uid");
    if (!uid) {
        uid = `anon-${Math.random().toString(36).substr(2, 8)}`;
        localStorage.setItem("catdams_uid", uid);
    }
    return uid;
}

const CONFIG = {
    BACKEND_ENDPOINT: 'https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest',
    AGENT_ID: "catdams-universal-ext",
    USER_ID: getOrCreateUserId(),
    AGENT_VERSION: "v1.0.0",
    POLICY_VERSION: "2024-05",
    PROCESS_DEBOUNCE_DELAY: 1200,
    INITIAL_LOAD_DELAY: 3500
};
const SESSION_ID = `sess-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 8)}`;

const HOST = window.location.hostname;

// --- Site-Specific Selectors and Extractors ---
const PLATFORM_DEFS = [
    {
        name: "ChatGPT",
        host: "chat.openai.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector('textarea');
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const messageDivs = Array.from(document.querySelectorAll("div[data-message-author-role]"));
            const userBubbles = messageDivs.filter(el => el.getAttribute('data-message-author-role') === "user");
            const aiBubbles = messageDivs.filter(el => el.getAttribute('data-message-author-role') === "assistant");
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Gemini",
        host: "gemini.google.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const inputArea = document.querySelector('div[contenteditable="true"][role="textbox"]');
            if (inputArea && inputArea.innerText) userPrompt = inputArea.innerText.trim();
            const chatItems = document.querySelectorAll('div[role="listitem"], div[data-testid*="chat-message"]');
            if (chatItems.length) {
                const lastChat = chatItems[chatItems.length - 1];
                let userBub = lastChat.querySelector('div[data-is-user-message="true"], div.message-item-text-model-id-user, div.user-text-content, span[data-text-content]');
                if (userBub && userBub.innerText) userPrompt = userBub.innerText.trim();
                let aiBub = lastChat.querySelector('div[data-is-ai-response="true"], div.message-item-text-model-id-2, div.model-response-content, span[data-text-content]');
                if (aiBub && aiBub.innerText) aiResponse = aiBub.innerText.trim();
            }
            if (!userPrompt || !aiResponse) {
                const textEls = Array.from(document.querySelectorAll('span,div')).filter(el =>
                    el.offsetParent !== null && el.innerText && el.innerText.trim().length > 0
                );
                textEls.sort((a, b) => b.innerText.length - a.innerText.length);
                if (!userPrompt && textEls[0]) userPrompt = textEls[0].innerText.trim();
                if (!aiResponse && textEls[1]) aiResponse = textEls[1].innerText.trim();
            }
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Claude",
        host: "claude.ai",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const msgDivs = Array.from(document.querySelectorAll('.message, .Message'));
            const userBubbles = msgDivs.filter(el =>
                el.className && el.className.toLowerCase().includes("user") ||
                el.getAttribute('role') === "user"
            );
            const aiBubbles = msgDivs.filter(el =>
                el.className && el.className.toLowerCase().includes("assistant") ||
                el.getAttribute('role') === "assistant"
            );
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "DeepSeek",
        host: "chat.deepseek.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector('textarea');
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const chatItems = Array.from(document.querySelectorAll('.message-item, .chat-item'));
            const userBubbles = chatItems.filter(el =>
                el.className && el.className.toLowerCase().includes("user")
            );
            const aiBubbles = chatItems.filter(el =>
                el.className && (
                    el.className.toLowerCase().includes("assistant") ||
                    el.className.toLowerCase().includes("ai")
                )
            );
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Poe",
        host: "poe.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const userBubbles = Array.from(document.querySelectorAll(".UserMessage"));
            const aiBubbles = Array.from(document.querySelectorAll(".BotMessage, .AssistantMessage, .MessageGroup"));
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Perplexity",
        host: "www.perplexity.ai",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const userBubbles = Array.from(document.querySelectorAll('.user-message'));
            const aiBubbles = Array.from(document.querySelectorAll('.ai-message, .response, .assistant-message'));
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "HuggingChat",
        host: "huggingface.co",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const msgGroups = Array.from(document.querySelectorAll('.chat-message, .message-group'));
            const userBubbles = msgGroups.filter(el =>
                el.className && el.className.toLowerCase().includes("user")
            );
            const aiBubbles = msgGroups.filter(el =>
                el.className && el.className.toLowerCase().includes("assistant")
            );
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Replika",
        host: "replika.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const msgDivs = Array.from(document.querySelectorAll('.text-message, .user-message, .bot-message'));
            const userBubbles = msgDivs.filter(el =>
                el.className && (el.className.toLowerCase().includes("user") || el.className.toLowerCase().includes("me"))
            );
            const aiBubbles = msgDivs.filter(el =>
                el.className && (el.className.toLowerCase().includes("bot") || el.className.toLowerCase().includes("ai"))
            );
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "You.com",
        host: "you.com",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const userBubbles = Array.from(document.querySelectorAll('.chatMessage.user, .userMessage, .user-bubble'));
            const aiBubbles = Array.from(document.querySelectorAll('.chatMessage.ai, .aiMessage, .ai-bubble'));
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    },
    {
        name: "Pi.ai",
        host: "pi.ai",
        extract: function () {
            let userPrompt = "", aiResponse = "";
            const textarea = document.querySelector("textarea");
            if (textarea && textarea.value.trim()) userPrompt = textarea.value.trim();
            const bubbles = Array.from(document.querySelectorAll('.message, .user-message, .ai-message'));
            const userBubbles = bubbles.filter(el =>
                el.className && el.className.toLowerCase().includes("user")
            );
            const aiBubbles = bubbles.filter(el =>
                el.className && (el.className.toLowerCase().includes("ai") || el.className.toLowerCase().includes("bot"))
            );
            if (userBubbles.length) userPrompt = userBubbles[userBubbles.length - 1].innerText.trim();
            if (aiBubbles.length) aiResponse = aiBubbles[aiBubbles.length - 1].innerText.trim();
            return { userPrompt, aiResponse };
        }
    }
];

// --- Helper Functions ---
function buildPayload(userPrompt, aiResponse, platform) {
    const now = new Date().toISOString();
    return {
        agent_id: CONFIG.AGENT_ID,
        session_id: SESSION_ID,
        user_id: CONFIG.USER_ID,
        timestamp: now,
        messages: [
            { sequence: 1, sender: "user", text: userPrompt || "", time: now },
            { sequence: 2, sender: "ai", text: aiResponse || "", time: now }
        ],
        metadata: {
            agent_version: CONFIG.AGENT_VERSION,
            policy_version: CONFIG.POLICY_VERSION,
            os: navigator.platform,
            application: platform,
            language: navigator.language || "en-US"
        }
    };
}

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

// --- Main Logic: Detect Platform, Observe, Log ---
let lastLoggedUserPrompt = "";
let lastLoggedAiResponse = "";
let processChatTimeout = null;

function processAndSendChatData(extractor, platformName) {
    clearTimeout(processChatTimeout);

    processChatTimeout = setTimeout(() => {
        const { userPrompt, aiResponse } = extractor();
        if (!userPrompt || !aiResponse) return;
        if (userPrompt === lastLoggedUserPrompt && aiResponse === lastLoggedAiResponse) return;

        const payload = buildPayload(userPrompt, aiResponse, platformName);
        postToBackend(payload);

        lastLoggedUserPrompt = userPrompt;
        lastLoggedAiResponse = aiResponse;
    }, CONFIG.PROCESS_DEBOUNCE_DELAY);
}

const platformObj = PLATFORM_DEFS.find(p => HOST.includes(p.host));
if (platformObj) {
    const observer = new MutationObserver(() => {
        processAndSendChatData(platformObj.extract, platformObj.name);
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    console.log(`[CATDAMS] Monitoring ${platformObj.name} (${platformObj.host})`);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') setTimeout(() => processAndSendChatData(platformObj.extract, platformObj.name), 100);
    });
    setTimeout(() => processAndSendChatData(platformObj.extract, platformObj.name), CONFIG.INITIAL_LOAD_DELAY);

    if (document.readyState === 'complete') {
        setTimeout(() => processAndSendChatData(platformObj.extract, platformObj.name), CONFIG.INITIAL_LOAD_DELAY);
    }
} else {
    console.log(`[CATDAMS] No supported AI chat platform detected on ${HOST}`);
}
