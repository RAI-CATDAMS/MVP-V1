// ====== CATDAMS Sentinel Extension: background.js ======
// Handles messaging and relays POSTs to backend

chrome.runtime.onInstalled.addListener(() => {
    console.log("CATDAMS Sentinel Extension installed.");
});

// Native Messaging: Sends session_id to Python helper
function sendSessionIdToHelper(session_id) {
    chrome.runtime.sendNativeMessage(
        "com.catdams.sessionhelper", // Must match host manifest name
        { session_id: session_id },
        function(response) {
            if (chrome.runtime.lastError) {
                console.error("Failed to send session ID to helper:", chrome.runtime.lastError.message);
            } else {
                console.log("Session ID sent to helper. Response:", response);
            }
        }
    );
}

// Optional: Check if session file exists before sending
async function checkIfSessionFileExists() {
    try {
        const res = await fetch("http://localhost:3009/session-id");
        return res.ok;
    } catch (err) {
        return false;
    }
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.type === "catdams_log") {
        console.log("[CATDAMS] Forwarding payload to backend:", msg.payload);

        if (msg.payload && msg.payload.session_id) {
            checkIfSessionFileExists().then((exists) => {
                if (!exists) {
                    sendSessionIdToHelper(msg.payload.session_id);
                }
            });
        }

        fetch("http://localhost:8000/event", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(msg.payload)
        })
        .then(res => {
            if ([200, 201, 202].includes(res.status)) {
                sendResponse({ status: res.status });
            } else {
                sendResponse({ status: res.status, error: `Unexpected status code: ${res.status}` });
            }
        })
        .catch(e => {
            sendResponse({ status: "error", error: e.toString() });
        });
        return true; // Needed to use async sendResponse
    }
});
