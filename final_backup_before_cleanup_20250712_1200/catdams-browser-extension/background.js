// ====== CATDAMS Sentinel Extension: background.js ======
// Handles messaging and relays POSTs to backend with full message payloads

chrome.runtime.onInstalled.addListener(() => {
    console.log("✅ CATDAMS Sentinel Extension installed with enhanced threat detection.");
});

// ✅ Native Messaging: Sends session_id to Python helper (optional if file missing)
function sendSessionIdToHelper(session_id) {
    chrome.runtime.sendNativeMessage(
        "com.catdams.sessionhelper", // Must match host manifest name
        { session_id: session_id },
        function(response) {
            if (chrome.runtime.lastError) {
                console.error("[CATDAMS] Native message error:", chrome.runtime.lastError.message);
            } else {
                console.log("[CATDAMS] Native message success:", response);
            }
        }
    );
}

// ✅ Optional: Check if session file exists (prevents duplicate session creation)
async function checkIfSessionFileExists() {
    try {
        const res = await fetch("http://localhost:3009/session-id");
        return res.ok;
    } catch (err) {
        console.warn("[CATDAMS] Could not reach session bridge:", err.message);
        return false;
    }
}

// ✅ Enhanced threat analysis logging
function logThreatAnalysis(payload) {
    if (payload.threat_analysis && payload.threat_analysis.threats.length > 0) {
        console.warn(`[CATDAMS][THREAT] ${payload.severity} threat detected on ${payload.source}:`, {
            threatTypes: payload.threat_analysis.threats.map(t => t.type),
            messagePreview: payload.message.substring(0, 100),
            sender: payload.sender
        });
    }
}

// ✅ Main listener for inbound logs from content.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.type === "catdams_log" && msg.payload) {
        console.log("[CATDAMS] ⬅️ Incoming payload:", msg.payload);

        // Log threat analysis if present
        logThreatAnalysis(msg.payload);

        // 🔁 Trigger async response return
        handleCatdamsPost(msg.payload)
            .then(res => {
                try {
                    sendResponse(res);
                } catch (e) {
                    console.warn("[CATDAMS] Message port closed before response:", e);
                }
            })
            .catch(err => {
                console.error("[CATDAMS] Async POST error:", err);
                try {
                    sendResponse({ status: "error", error: err.toString() });
                } catch (e) {
                    console.warn("[CATDAMS] Send error (catch):", e);
                }
            });

        return true; // ✅ Keeps message channel open for async
    }
});

// ✅ Asynchronous backend POST logic with enhanced error handling
async function handleCatdamsPost(payload) {
    // ✅ Ensure session_id is populated (optional - don't fail if bridge is down)
    if (!payload.session_id || payload.session_id === "unknown-session") {
        try {
            const res = await fetch("http://localhost:3009/session-id");
            if (res.ok) {
                const sessionIdText = await res.text();
                payload.session_id = sessionIdText.trim();
                console.log("[CATDAMS] 🆔 Assigned session_id from bridge:", payload.session_id);
            } else {
                console.warn("[CATDAMS] ❌ Failed to fetch session_id from bridge, continuing with existing session_id");
            }
        } catch (err) {
            console.warn("[CATDAMS] ⚠️ Session bridge not available, continuing with existing session_id:", err.message);
        }
    } else {
        // Try to check session bridge but don't fail if it's down
        try {
            const exists = await checkIfSessionFileExists();
            if (!exists) {
                sendSessionIdToHelper(payload.session_id);
            }
        } catch (err) {
            console.warn("[CATDAMS] Session bridge check failed, continuing:", err.message);
        }
    }

    // 🚀 Send to backend with enhanced error handling
    try {
        console.log("[CATDAMS] 🚀 Sending payload to backend:", {
            url: "http://localhost:8000/event",
            method: "POST",
            payloadSize: JSON.stringify(payload).length,
            sender: payload.sender,
            session_id: payload.session_id
        });
        
        const res = await fetch("http://localhost:8000/event", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        console.log("[CATDAMS] 📡 Backend response received:", {
            status: res.status,
            statusText: res.statusText,
            headers: Object.fromEntries(res.headers.entries())
        });

        if ([200, 201, 202].includes(res.status)) {
            const messagePreview = payload.message ? payload.message.substring(0, 50) : "[no message]";
            console.log(`[CATDAMS Backend] ✅ POST success (${res.status}): ${payload.sender} "${messagePreview}..."`);
            
            // Log threat information if present
            if (payload.threat_analysis && payload.threat_analysis.threats.length > 0) {
                console.warn(`[CATDAMS Backend] ⚠️ Threat data sent: ${payload.threat_analysis.threats.length} threats detected`);
            }
            
            return { status: res.status };
        } else {
            console.warn(`[CATDAMS Backend] ⚠️ Unexpected status: ${res.status} - ${res.statusText}`);
            return { status: res.status, error: `Unexpected status code: ${res.status} - ${res.statusText}` };
        }
    } catch (error) {
        console.error("[CATDAMS Backend] ❌ Network error:", error.message);
        console.error("[CATDAMS Backend] ❌ Error details:", {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        return { status: "error", error: error.message };
    }
}

