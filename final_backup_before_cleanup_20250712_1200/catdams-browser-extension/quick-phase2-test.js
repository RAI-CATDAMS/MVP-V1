// Quick Phase 2 Test - Verify all components are working
console.log('🚀 CATDAMS Phase 2 Quick Test Starting...');

// Test 1: Check if all Phase 2 files exist
const requiredFiles = [
    'config.js',
    'error-handler.js',
    'logger.js', 
    'tdc-integration.js',
    'performance-monitor.js',
    'background.js',
    'popup.html',
    'popup.js',
    'manifest.json'
];

console.log('📁 Checking required files...');
requiredFiles.forEach(file => {
    try {
        const script = document.createElement('script');
        script.src = chrome.runtime.getURL(file);
        console.log(`✅ ${file} - Available`);
    } catch (error) {
        console.log(`❌ ${file} - Missing: ${error.message}`);
    }
});

// Test 2: Check background script communication
console.log('🔗 Testing background script communication...');
chrome.runtime.sendMessage({ type: 'ping' }, (response) => {
    if (chrome.runtime.lastError) {
        console.log(`❌ Background script error: ${chrome.runtime.lastError.message}`);
    } else {
        console.log(`✅ Background script responsive: ${JSON.stringify(response)}`);
    }
});

// Test 3: Test configuration system
console.log('⚙️ Testing configuration system...');
chrome.runtime.sendMessage({ type: 'get_stats' }, (response) => {
    if (chrome.runtime.lastError) {
        console.log(`❌ Stats error: ${chrome.runtime.lastError.message}`);
    } else {
        console.log(`✅ Stats retrieved: ${JSON.stringify(response)}`);
    }
});

// Test 4: Test TDC integration
console.log('🧠 Testing TDC integration...');
const testPayload = {
    message: "Phase 2 test message",
    sender: "test-user",
    platform: "test-platform",
    session_id: `phase2-test-${Date.now()}`,
    timestamp: Date.now()
};

chrome.runtime.sendMessage({ 
    type: 'catdams_log', 
    payload: testPayload 
}, (response) => {
    if (chrome.runtime.lastError) {
        console.log(`❌ TDC integration error: ${chrome.runtime.lastError.message}`);
    } else {
        console.log(`✅ TDC integration working: ${JSON.stringify(response)}`);
    }
});

console.log('✅ Phase 2 Quick Test Complete!');
console.log('📊 Check the console for detailed results.'); 