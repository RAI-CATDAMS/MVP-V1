// DeepSeek DOM Analysis - Simple Test Script
// Copy and paste this entire script into the browser console on chat.deepseek.com

console.log('🔍 DeepSeek DOM Analysis Starting...');

// Simple text extraction
function getText(element) {
    if (!element) return '';
    return element.textContent?.trim() || element.innerText?.trim() || '';
}

// Test user input selectors
console.log('\n🔍 Testing User Input Selectors:');
const userSelectors = [
    'textarea[placeholder*="Message"]',
    'textarea[placeholder*="Ask"]', 
    'textarea[placeholder*="chat"]',
    'textarea[placeholder*="input"]',
    'div[contenteditable="true"]',
    'div[role="textbox"]',
    'textarea',
    'input[type="text"]',
    'div[data-testid*="input"]',
    'div[class*="input"]',
    'div[class*="composer"]',
    'div[class*="editor"]'
];

userSelectors.forEach(selector => {
    try {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            console.log(`✅ ${selector}: ${elements.length} elements found`);
            elements.forEach((el, i) => {
                const text = getText(el);
                if (text.length > 0) {
                    console.log(`   Element ${i+1}: "${text.substring(0, 50)}..." (${text.length} chars)`);
                    console.log(`   Classes: ${el.className}`);
                    console.log(`   ID: ${el.id}`);
                }
            });
        } else {
            console.log(`❌ ${selector}: No elements found`);
        }
    } catch (e) {
        console.log(`❌ ${selector}: Error - ${e.message}`);
    }
});

// Test AI response selectors
console.log('\n🤖 Testing AI Response Selectors:');
const aiSelectors = [
    'div[class*="message"]',
    'div[class*="response"]',
    'div[class*="ai"]',
    'div[class*="assistant"]',
    'div[class*="bot"]',
    'div[class*="chat"]',
    'div[data-testid*="message"]',
    'div[data-testid*="response"]',
    'div[data-testid*="ai"]',
    'div[role="article"]',
    'div[role="main"]',
    'div[class*="content"]',
    'div[class*="text"]',
    'div[class*="markdown"]',
    'div[class*="prose"]',
    'div[class*="conversation"]',
    'div[class*="thread"]'
];

aiSelectors.forEach(selector => {
    try {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            console.log(`✅ ${selector}: ${elements.length} elements found`);
            elements.forEach((el, i) => {
                const text = getText(el);
                if (text.length > 10) {
                    console.log(`   Element ${i+1}: "${text.substring(0, 100)}..." (${text.length} chars)`);
                    console.log(`   Classes: ${el.className}`);
                    console.log(`   ID: ${el.id}`);
                }
            });
        } else {
            console.log(`❌ ${selector}: No elements found`);
        }
    } catch (e) {
        console.log(`❌ ${selector}: Error - ${e.message}`);
    }
});

// Scan for all divs with substantial text content
console.log('\n📦 Scanning for all divs with text content:');
const allDivs = document.querySelectorAll('div');
let messageDivs = [];

allDivs.forEach((div, index) => {
    const text = getText(div);
    if (text.length > 20 && text.length < 5000) { // Reasonable message length
        const hasMessageIndicators = 
            div.className?.toLowerCase().includes('message') ||
            div.className?.toLowerCase().includes('response') ||
            div.className?.toLowerCase().includes('chat') ||
            div.className?.toLowerCase().includes('ai') ||
            div.className?.toLowerCase().includes('assistant') ||
            div.className?.toLowerCase().includes('user') ||
            div.getAttribute('data-testid')?.toLowerCase().includes('message') ||
            div.getAttribute('role') === 'article' ||
            div.getAttribute('role') === 'main';
        
        if (hasMessageIndicators) {
            messageDivs.push({
                element: div,
                text: text,
                className: div.className,
                id: div.id,
                index: index
            });
        }
    }
});

console.log(`Found ${messageDivs.length} potential message divs:`);
messageDivs.forEach((msg, i) => {
    console.log(`\n${i+1}. Text: "${msg.text.substring(0, 100)}..." (${msg.text.length} chars)`);
    console.log(`   Classes: ${msg.className}`);
    console.log(`   ID: ${msg.id}`);
    console.log(`   Index: ${msg.index}`);
});

// Show page structure
console.log('\n🏗️ Page Structure:');
console.log(`Title: ${document.title}`);
console.log(`URL: ${window.location.href}`);
console.log(`Body classes: ${document.body.className}`);

// Find main containers
const mainElements = document.querySelectorAll('main, div[role="main"], div[class*="main"], div[class*="container"]');
console.log(`\nMain elements found: ${mainElements.length}`);
mainElements.forEach((el, i) => {
    console.log(`${i+1}. Tag: ${el.tagName}, Classes: ${el.className}, ID: ${el.id}`);
});

console.log('\n✅ DeepSeek DOM analysis complete!');
console.log('💡 Look for selectors that found elements with actual text content.');
console.log('🎯 Focus on elements with message-like classes or roles.'); 