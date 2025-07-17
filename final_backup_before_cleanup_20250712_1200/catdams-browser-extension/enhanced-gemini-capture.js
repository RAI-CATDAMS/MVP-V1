// Enhanced Gemini User Input Capture with Comprehensive Debugging
// This is an improved version of the Gemini capture logic

function enhancedGeminiUserInputCapture() {
    if (!window.location.hostname.includes('gemini.google.com')) {
        console.log('[CATDAMS][Gemini] Not on Gemini domain, skipping');
        return false;
    }
    
    console.log('[CATDAMS][Gemini] Enhanced capture initialized');
    
    let lastGeminiPrompt = "";
    let captureAttempts = 0;
    const maxAttempts = 10;
    
    // Enhanced selectors with multiple fallbacks
    const enhancedUserSelectors = [
        // Primary selectors
        'textarea[aria-label*="input"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
        '.user-query-container',
        'div[aria-label="User input"]',
        
        // Extended selectors
        'div[data-testid*="input"]',
        'div[data-testid*="user"]',
        'div[role="textbox"][contenteditable="true"]',
        'textarea[data-testid*="input"]',
        'div[class*="input"]',
        'div[class*="user"]',
        'div[class*="query"]',
        'div[class*="prompt"]',
        
        // Generic fallbacks
        'textarea',
        'input[type="text"]',
        'div[contenteditable]'
    ];
    
    function debugElement(element, index) {
        if (!element) return;
        console.log(`[CATDAMS][Gemini][Debug] Element ${index}:`, {
            tagName: element.tagName,
            className: element.className,
            id: element.id,
            placeholder: element.placeholder,
            'aria-label': element.getAttribute('aria-label'),
            'data-testid': element.getAttribute('data-testid'),
            contenteditable: element.getAttribute('contenteditable'),
            role: element.getAttribute('role'),
            value: element.value ? element.value.substring(0, 50) + '...' : 'N/A',
            innerText: element.innerText ? element.innerText.substring(0, 50) + '...' : 'N/A',
            textContent: element.textContent ? element.textContent.substring(0, 50) + '...' : 'N/A'
        });
    }
    
    function scanGeminiUserPrompt() {
        console.log('[CATDAMS][Gemini] Scanning for user input...');
        captureAttempts++;
        
        let foundInput = false;
        
        // Try enhanced selectors
        for (const selector of enhancedUserSelectors) {
            const elements = document.querySelectorAll(selector);
            console.log(`[CATDAMS][Gemini] Selector "${selector}": ${elements.length} elements found`);
            
            if (elements.length > 0) {
                elements.forEach((element, index) => {
                    debugElement(element, index);
                    
                    // Try multiple ways to get text content
                    const text = element.value || element.innerText || element.textContent || '';
                    const trimmedText = text.trim();
                    
                    if (trimmedText && trimmedText !== lastGeminiPrompt) {
                        console.log(`[CATDAMS][Gemini][USER] Found new input via "${selector}":`, trimmedText);
                        lastGeminiPrompt = trimmedText;
                        logMessageOnce(trimmedText, "USER", "gemini");
                        foundInput = true;
                    }
                });
            }
        }
        
        // If no input found, try scanning chat history for recent user messages
        if (!foundInput) {
            console.log('[CATDAMS][Gemini] No input found, scanning chat history...');
            scanChatHistoryForUserMessages();
        }
        
        // Schedule retry if needed
        if (!foundInput && captureAttempts < maxAttempts) {
            console.log(`[CATDAMS][Gemini] No input found, retrying in 1 second (attempt ${captureAttempts}/${maxAttempts})`);
            setTimeout(scanGeminiUserPrompt, 1000);
        }
        
        return foundInput;
    }
    
    function scanChatHistoryForUserMessages() {
        // Look for user messages in the chat history
        const userMessageSelectors = [
            '[data-testid*="user"]',
            '[class*="user"]',
            '[role="user"]',
            '.user-message',
            '.human-message',
            '[data-message-author-role="user"]'
        ];
        
        for (const selector of userMessageSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                const lastElement = elements[elements.length - 1];
                const text = lastElement.innerText || lastElement.textContent || '';
                const trimmedText = text.trim();
                
                if (trimmedText && trimmedText !== lastGeminiPrompt) {
                    console.log(`[CATDAMS][Gemini][USER] Found user message in history via "${selector}":`, trimmedText);
                    lastGeminiPrompt = trimmedText;
                    logMessageOnce(trimmedText, "USER", "gemini");
                    return true;
                }
            }
        }
        
        return false;
    }
    
    // Enhanced input event monitoring
    function setupInputMonitoring() {
        console.log('[CATDAMS][Gemini] Setting up input monitoring...');
        
        // Monitor all potential input elements
        const inputElements = document.querySelectorAll('textarea, div[contenteditable="true"], input[type="text"]');
        console.log(`[CATDAMS][Gemini] Found ${inputElements.length} input elements to monitor`);
        
        inputElements.forEach((inputElement, index) => {
            if (inputElement.__catdams_enhanced_listener) {
                console.log(`[CATDAMS][Gemini] Element ${index} already has listener, skipping`);
                return;
            }
            
            inputElement.__catdams_enhanced_listener = true;
            debugElement(inputElement, index);
            
            // Multiple event listeners for redundancy
            const events = ['keydown', 'input', 'change', 'paste'];
            
            events.forEach(eventType => {
                inputElement.addEventListener(eventType, function(e) {
                    console.log(`[CATDAMS][Gemini] ${eventType} event on element ${index}`);
                    
                    // For keydown, check for Enter key
                    if (eventType === 'keydown' && e.key === 'Enter' && !e.shiftKey) {
                        console.log('[CATDAMS][Gemini] Enter key pressed, scanning for input...');
                        setTimeout(scanGeminiUserPrompt, 200);
                    }
                    
                    // For other events, scan after a delay
                    if (eventType !== 'keydown') {
                        setTimeout(scanGeminiUserPrompt, 300);
                    }
                });
            });
        });
    }
    
    // Enhanced DOM observation
    function setupDOMObservation() {
        console.log('[CATDAMS][Gemini] Setting up DOM observation...');
        
        let chatRoot = document.querySelector('main') || document.body;
        if (chatRoot && !chatRoot.__catdams_enhanced_gemini_observer) {
            const observer = new MutationObserver((mutations) => {
                const hasAddedNodes = mutations.some(mutation => mutation.addedNodes.length > 0);
                const hasAttributeChanges = mutations.some(mutation => mutation.type === 'attributes');
                
                if (hasAddedNodes || hasAttributeChanges) {
                    console.log('[CATDAMS][Gemini] DOM changed, scanning for updates...');
                    
                    // Check for AI responses
                    const aiReply = scanGeminiAIResponse();
                    if (aiReply && aiReply !== lastLoggedAI_gemini) {
                        console.log('[CATDAMS][Gemini][AI] Found AI response:', aiReply);
                        logMessageOnce(aiReply, "AI", "gemini");
                        lastLoggedAI_gemini = aiReply;
                    }
                    
                    // Re-scan for user input
                    setTimeout(scanGeminiUserPrompt, 500);
                }
            });
            
            observer.observe(chatRoot, { 
                childList: true, 
                subtree: true,
                attributes: true,
                attributeFilter: ['value', 'innerText', 'textContent'],
                characterData: false
            });
            
            chatRoot.__catdams_enhanced_gemini_observer = true;
            console.log('[CATDAMS][Gemini] DOM observer attached');
        }
    }
    
    // Periodic scanning as fallback
    function setupPeriodicScanning() {
        console.log('[CATDAMS][Gemini] Setting up periodic scanning...');
        
        // Initial scan
        setTimeout(scanGeminiUserPrompt, 2000);
        
        // Periodic scans every 3 seconds
        setInterval(() => {
            console.log('[CATDAMS][Gemini] Periodic scan...');
            scanGeminiUserPrompt();
        }, 3000);
    }
    
    // Initialize all capture methods
    setupInputMonitoring();
    setupDOMObservation();
    setupPeriodicScanning();
    
    // Re-setup monitoring when DOM changes (for dynamic content)
    const setupObserver = new MutationObserver(() => {
        console.log('[CATDAMS][Gemini] DOM structure changed, re-setting up monitoring...');
        setTimeout(setupInputMonitoring, 1000);
    });
    
    setupObserver.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
    
    console.log('[CATDAMS][Gemini] Enhanced capture setup complete');
    return true;
}

// Export for use in content.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { enhancedGeminiUserInputCapture };
} 