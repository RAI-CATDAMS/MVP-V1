// ====== ChatGPT DOM Selector Analysis Script ======
// Comprehensive testing and identification of ChatGPT DOM elements
// For reliable message capture in CATDAMS browser extension

console.log("🔍 ChatGPT Selector Analysis Started");

// ====== CONFIGURATION ======
const TEST_CONFIG = {
    scanInterval: 2000, // 2 seconds
    maxScans: 30, // 30 scans = 1 minute
    debugMode: true,
    logToConsole: true,
    saveResults: true
};

// ====== TEST RESULTS STORAGE ======
let testResults = {
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    scans: [],
    selectors: {
        user: [],
        ai: [],
        input: [],
        container: [],
        completionIndicators: []
    },
    recommendations: [],
    successRate: 0
};

// ====== KNOWN CHATGPT SELECTORS TO TEST ======
const CHATGPT_SELECTORS = {
    // User message selectors
    user: [
        '[data-message-author-role="user"]',
        'div[data-message-author-role="user"]',
        '.markdown.prose.w-full.break-words',
        '.prose.w-full.break-words',
        '.user-message',
        '.human-message',
        '[data-testid="conversation-turn-2"]',
        '.flex.flex-col.items-center.text-sm.h-full.dark\\:bg-gray-800',
        '.group.w-full.text-gray-800.dark\\:text-gray-100.border-b.border-black\\/10.dark\\:border-gray-900\\/50'
    ],
    
    // AI response selectors
    ai: [
        '[data-message-author-role="assistant"]',
        'div[data-message-author-role="assistant"]',
        '.markdown.prose.w-full.break-words',
        '.prose.w-full.break-words',
        '.assistant-message',
        '.ai-message',
        '.bot-message',
        '[data-testid="conversation-turn-3"]',
        '.flex.flex-col.items-center.text-sm.h-full.dark\\:bg-gray-800'
    ],
    
    // Input field selectors
    input: [
        'textarea[data-id="root"]',
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="Send a message"]',
        'textarea[placeholder*="ChatGPT"]',
        'div[contenteditable="true"]',
        'textarea[data-testid="chat-input"]',
        'textarea[aria-label*="input"]',
        'textarea[aria-label*="message"]',
        'textarea[role="textbox"]',
        'input[type="text"]',
        '.chat-input',
        '.message-input'
    ],
    
    // Container selectors
    container: [
        'main',
        '[data-testid="conversation-turn-2"]',
        '.flex.flex-col.items-center.text-sm',
        '.flex.flex-col.items-center.text-sm.h-full.dark\\:bg-gray-800',
        '.group.w-full.text-gray-800.dark\\:text-gray-100.border-b.border-black\\/10.dark\\:border-gray-900\\/50',
        '.conversation-container',
        '.chat-container',
        '.messages-container'
    ],
    
    // Completion indicators
    completionIndicators: [
        '.animate-pulse',
        '[data-testid="loading"]',
        '.typing-indicator',
        '.loading-indicator',
        '.streaming',
        '.thinking',
        '.generating',
        '.animate-spin',
        '.loading',
        '.typing'
    ]
};

// ====== SCANNING FUNCTIONS ======

function scanForElements() {
    const scan = {
        timestamp: new Date().toISOString(),
        elements: {
            user: [],
            ai: [],
            input: [],
            container: [],
            completionIndicators: []
        },
        textSamples: {
            user: [],
            ai: [],
            input: []
        }
    };
    
    // Scan for user messages
    CHATGPT_SELECTORS.user.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const text = extractText(element);
            if (text && text.trim().length > 0) {
                scan.elements.user.push({
                    selector: selector,
                    text: text.substring(0, 100),
                    length: text.length,
                    classes: element.className,
                    attributes: getElementAttributes(element)
                });
                scan.textSamples.user.push(text.substring(0, 50));
            }
        });
    });
    
    // Scan for AI messages
    CHATGPT_SELECTORS.ai.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const text = extractText(element);
            if (text && text.trim().length > 0) {
                scan.elements.ai.push({
                    selector: selector,
                    text: text.substring(0, 100),
                    length: text.length,
                    classes: element.className,
                    attributes: getElementAttributes(element)
                });
                scan.textSamples.ai.push(text.substring(0, 50));
            }
        });
    });
    
    // Scan for input fields
    CHATGPT_SELECTORS.input.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const text = extractText(element);
            scan.elements.input.push({
                selector: selector,
                text: text.substring(0, 100),
                length: text.length,
                classes: element.className,
                attributes: getElementAttributes(element),
                isVisible: isElementVisible(element),
                isFocused: element === document.activeElement
            });
            if (text) scan.textSamples.input.push(text.substring(0, 50));
        });
    });
    
    // Scan for containers
    CHATGPT_SELECTORS.container.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            scan.elements.container.push({
                selector: selector,
                classes: element.className,
                attributes: getElementAttributes(element),
                childCount: element.children.length,
                isVisible: isElementVisible(element)
            });
        });
    });
    
    // Scan for completion indicators
    CHATGPT_SELECTORS.completionIndicators.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            scan.elements.completionIndicators.push({
                selector: selector,
                classes: element.className,
                attributes: getElementAttributes(element),
                isVisible: isElementVisible(element)
            });
        });
    });
    
    return scan;
}

function extractText(element) {
    const methods = [
        () => element.innerText,
        () => element.textContent,
        () => element.value,
        () => element.getAttribute('aria-label'),
        () => element.getAttribute('title'),
        () => element.getAttribute('placeholder')
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

function getElementAttributes(element) {
    const attributes = {};
    for (let attr of element.attributes) {
        attributes[attr.name] = attr.value;
    }
    return attributes;
}

function isElementVisible(element) {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           element.offsetWidth > 0 && 
           element.offsetHeight > 0;
}

// ====== ANALYSIS FUNCTIONS ======

function analyzeResults() {
    const analysis = {
        bestSelectors: {
            user: findBestSelectors('user'),
            ai: findBestSelectors('ai'),
            input: findBestSelectors('input'),
            container: findBestSelectors('container'),
            completionIndicators: findBestSelectors('completionIndicators')
        },
        recommendations: [],
        successRate: calculateSuccessRate()
    };
    
    // Generate recommendations
    if (analysis.bestSelectors.user.length === 0) {
        analysis.recommendations.push("No user message selectors found - ChatGPT may have updated their DOM structure");
    }
    
    if (analysis.bestSelectors.ai.length === 0) {
        analysis.recommendations.push("No AI response selectors found - need to identify new selectors");
    }
    
    if (analysis.bestSelectors.input.length === 0) {
        analysis.recommendations.push("No input field selectors found - user input capture may fail");
    }
    
    if (analysis.successRate < 0.5) {
        analysis.recommendations.push("Low success rate detected - consider updating selectors");
    }
    
    return analysis;
}

function findBestSelectors(type) {
    const selectorCounts = {};
    
    testResults.scans.forEach(scan => {
        scan.elements[type].forEach(element => {
            const selector = element.selector;
            if (!selectorCounts[selector]) {
                selectorCounts[selector] = {
                    count: 0,
                    totalText: 0,
                    samples: []
                };
            }
            selectorCounts[selector].count++;
            selectorCounts[selector].totalText += element.length || 0;
            if (element.text) {
                selectorCounts[selector].samples.push(element.text);
            }
        });
    });
    
    // Sort by count and return top performers
    return Object.entries(selectorCounts)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 5)
        .map(([selector, data]) => ({
            selector: selector,
            count: data.count,
            avgLength: data.totalText / data.count,
            samples: data.samples.slice(0, 3)
        }));
}

function calculateSuccessRate() {
    let totalScans = testResults.scans.length;
    let successfulScans = 0;
    
    testResults.scans.forEach(scan => {
        if (scan.elements.user.length > 0 || scan.elements.ai.length > 0) {
            successfulScans++;
        }
    });
    
    return totalScans > 0 ? successfulScans / totalScans : 0;
}

// ====== MONITORING FUNCTIONS ======

function startMonitoring() {
    console.log("🔍 Starting ChatGPT selector monitoring...");
    
    let scanCount = 0;
    const monitorInterval = setInterval(() => {
        scanCount++;
        
        if (TEST_CONFIG.debugMode) {
            console.log(`📊 Scan ${scanCount}/${TEST_CONFIG.maxScans}`);
        }
        
        const scan = scanForElements();
        testResults.scans.push(scan);
        
        // Log findings
        if (scan.elements.user.length > 0 || scan.elements.ai.length > 0) {
            console.log(`✅ Found elements in scan ${scanCount}:`, {
                user: scan.elements.user.length,
                ai: scan.elements.ai.length,
                input: scan.elements.input.length
            });
        }
        
        // Stop after max scans
        if (scanCount >= TEST_CONFIG.maxScans) {
            clearInterval(monitorInterval);
            finishAnalysis();
        }
    }, TEST_CONFIG.scanInterval);
}

function finishAnalysis() {
    console.log("🎯 Analysis complete! Generating report...");
    
    const analysis = analyzeResults();
    testResults.selectors = analysis.bestSelectors;
    testResults.recommendations = analysis.recommendations;
    testResults.successRate = analysis.successRate;
    
    // Display results
    displayResults();
    
    // Save results
    if (TEST_CONFIG.saveResults) {
        saveResults();
    }
}

function displayResults() {
    console.log("📊 === CHATGPT SELECTOR ANALYSIS RESULTS ===");
    console.log(`Success Rate: ${(testResults.successRate * 100).toFixed(1)}%`);
    console.log(`Total Scans: ${testResults.scans.length}`);
    console.log(`URL: ${testResults.url}`);
    
    console.log("\n🎯 BEST USER SELECTORS:");
    testResults.selectors.user.forEach((selector, index) => {
        console.log(`${index + 1}. ${selector.selector} (${selector.count} matches, avg length: ${selector.avgLength.toFixed(0)})`);
    });
    
    console.log("\n🤖 BEST AI SELECTORS:");
    testResults.selectors.ai.forEach((selector, index) => {
        console.log(`${index + 1}. ${selector.selector} (${selector.count} matches, avg length: ${selector.avgLength.toFixed(0)})`);
    });
    
    console.log("\n⌨️ BEST INPUT SELECTORS:");
    testResults.selectors.input.forEach((selector, index) => {
        console.log(`${index + 1}. ${selector.selector} (${selector.count} matches, avg length: ${selector.avgLength.toFixed(0)})`);
    });
    
    console.log("\n📦 BEST CONTAINER SELECTORS:");
    testResults.selectors.container.forEach((selector, index) => {
        console.log(`${index + 1}. ${selector.selector} (${selector.count} matches)`);
    });
    
    console.log("\n⏳ COMPLETION INDICATORS:");
    testResults.selectors.completionIndicators.forEach((selector, index) => {
        console.log(`${index + 1}. ${selector.selector} (${selector.count} matches)`);
    });
    
    if (testResults.recommendations.length > 0) {
        console.log("\n⚠️ RECOMMENDATIONS:");
        testResults.recommendations.forEach((rec, index) => {
            console.log(`${index + 1}. ${rec}`);
        });
    }
    
    console.log("\n📋 RECOMMENDED SELECTORS FOR CATDAMS:");
    console.log("const CHATGPT_SELECTORS = {");
    console.log("  user: [");
    testResults.selectors.user.slice(0, 3).forEach(selector => {
        console.log(`    '${selector.selector}',`);
    });
    console.log("  ],");
    console.log("  ai: [");
    testResults.selectors.ai.slice(0, 3).forEach(selector => {
        console.log(`    '${selector.selector}',`);
    });
    console.log("  ],");
    console.log("  input: [");
    testResults.selectors.input.slice(0, 3).forEach(selector => {
        console.log(`    '${selector.selector}',`);
    });
    console.log("  ],");
    console.log("  container: [");
    testResults.selectors.container.slice(0, 3).forEach(selector => {
        console.log(`    '${selector.selector}',`);
    });
    console.log("  ],");
    console.log("  completionIndicators: [");
    testResults.selectors.completionIndicators.slice(0, 3).forEach(selector => {
        console.log(`    '${selector.selector}',`);
    });
    console.log("  ]");
    console.log("};");
}

function saveResults() {
    const resultsBlob = new Blob([JSON.stringify(testResults, null, 2)], {
        type: 'application/json'
    });
    
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(resultsBlob);
    downloadLink.download = `chatgpt-selector-analysis-${new Date().toISOString().split('T')[0]}.json`;
    downloadLink.click();
    
    console.log("💾 Results saved to file");
}

// ====== REAL-TIME MONITORING ======

function startRealTimeMonitoring() {
    console.log("🔍 Starting real-time ChatGPT monitoring...");
    
    // Monitor for new messages
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        checkForNewMessages(node);
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log("✅ Real-time monitoring active");
}

function checkForNewMessages(element) {
    // Check if element contains user or AI messages
    const userSelectors = CHATGPT_SELECTORS.user.slice(0, 3);
    const aiSelectors = CHATGPT_SELECTORS.ai.slice(0, 3);
    
    userSelectors.forEach(selector => {
        const matches = element.querySelectorAll(selector);
        matches.forEach(match => {
            const text = extractText(match);
            if (text && text.trim().length > 0) {
                console.log("👤 New USER message detected:", {
                    selector: selector,
                    text: text.substring(0, 100),
                    timestamp: new Date().toISOString()
                });
            }
        });
    });
    
    aiSelectors.forEach(selector => {
        const matches = element.querySelectorAll(selector);
        matches.forEach(match => {
            const text = extractText(match);
            if (text && text.trim().length > 0) {
                console.log("🤖 New AI message detected:", {
                    selector: selector,
                    text: text.substring(0, 100),
                    timestamp: new Date().toISOString()
                });
            }
        });
    });
}

// ====== INITIALIZATION ======

// Wait for page to load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(startMonitoring, 1000);
        setTimeout(startRealTimeMonitoring, 2000);
    });
} else {
    setTimeout(startMonitoring, 1000);
    setTimeout(startRealTimeMonitoring, 2000);
}

// ====== MANUAL TESTING FUNCTIONS ======

window.testChatGPTSelectors = {
    // Manual scan
    scan: () => {
        const scan = scanForElements();
        console.log("🔍 Manual scan results:", scan);
        return scan;
    },
    
    // Test specific selector
    testSelector: (selector) => {
        const elements = document.querySelectorAll(selector);
        console.log(`🔍 Testing selector '${selector}':`, {
            count: elements.length,
            elements: Array.from(elements).map(el => ({
                text: extractText(el).substring(0, 50),
                classes: el.className,
                attributes: getElementAttributes(el)
            }))
        });
        return elements;
    },
    
    // Get current results
    getResults: () => testResults,
    
    // Start monitoring
    startMonitoring: startMonitoring,
    
    // Start real-time monitoring
    startRealTime: startRealTimeMonitoring
};

console.log("✅ ChatGPT Selector Analysis Script Loaded");
console.log("💡 Use window.testChatGPTSelectors.scan() for manual testing");
console.log("💡 Use window.testChatGPTSelectors.testSelector('selector') to test specific selectors"); 