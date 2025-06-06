// ====== CATDAMS Sentinel Extension: background.js ======
// Handles messaging and relays POSTs to backend

chrome.runtime.onInstalled.addListener(() => {
    console.log("CATDAMS Sentinel Extension installed.");
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.type === "catdams_log") {
        // Log the payload for debugging, including session_id
        console.log("[CATDAMS] Forwarding payload to backend:", msg.payload);

        fetch("http://localhost:8000/event", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(msg.payload)
        })
        .then(res => {
            // Accept HTTP 200, 201, and 202 as success
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
