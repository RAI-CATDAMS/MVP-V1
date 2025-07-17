// Test script to analyze Gemini DOM structure
// Run this in the browser console on gemini.google.com

console.log("=== CATDAMS Gemini Selector Analysis ===");

// Test current selectors
const currentSelectors = [
    'textarea[aria-label*="input"]',
    'textarea[placeholder*="Message"]',
    'div[role="textbox"]',
    'div[contenteditable="true"]',
    '.user-query-container',
    'div[aria-label="User input"]'
];

console.log("Testing current user input selectors:");
currentSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    console.log(`${selector}: ${elements.length} elements found`);
    if (elements.length > 0) {
        elements.forEach((el, i) => {
            console.log(`  Element ${i}:`, {
                tagName: el.tagName,
                className: el.className,
                id: el.id,
                placeholder: el.placeholder,
                'aria-label': el.getAttribute('aria-label'),
                'data-testid': el.getAttribute('data-testid'),
                contenteditable: el.getAttribute('contenteditable'),
                value: el.value ? el.value.substring(0, 50) + '...' : 'N/A',
                innerText: el.innerText ? el.innerText.substring(0, 50) + '...' : 'N/A'
            });
        });
    }
});

// Search for potential input elements
console.log("\n=== Searching for potential input elements ===");

// Look for textarea elements
const textareas = document.querySelectorAll('textarea');
console.log(`Found ${textareas.length} textarea elements:`);
textareas.forEach((el, i) => {
    console.log(`  Textarea ${i}:`, {
        placeholder: el.placeholder,
        'aria-label': el.getAttribute('aria-label'),
        'data-testid': el.getAttribute('data-testid'),
        className: el.className,
        id: el.id,
        value: el.value ? el.value.substring(0, 50) + '...' : 'N/A'
    });
});

// Look for contenteditable elements
const contenteditables = document.querySelectorAll('[contenteditable="true"]');
console.log(`\nFound ${contenteditables.length} contenteditable elements:`);
contenteditables.forEach((el, i) => {
    console.log(`  Contenteditable ${i}:`, {
        tagName: el.tagName,
        className: el.className,
        id: el.id,
        'aria-label': el.getAttribute('aria-label'),
        'data-testid': el.getAttribute('data-testid'),
        innerText: el.innerText ? el.innerText.substring(0, 50) + '...' : 'N/A'
    });
});

// Look for elements with "input" in aria-label
const inputAriaElements = document.querySelectorAll('[aria-label*="input"]');
console.log(`\nFound ${inputAriaElements.length} elements with 'input' in aria-label:`);
inputAriaElements.forEach((el, i) => {
    console.log(`  Input aria ${i}:`, {
        tagName: el.tagName,
        className: el.className,
        'aria-label': el.getAttribute('aria-label'),
        'data-testid': el.getAttribute('data-testid')
    });
});

// Look for elements with "message" in placeholder
const messagePlaceholderElements = document.querySelectorAll('[placeholder*="Message"]');
console.log(`\nFound ${messagePlaceholderElements.length} elements with 'Message' in placeholder:`);
messagePlaceholderElements.forEach((el, i) => {
    console.log(`  Message placeholder ${i}:`, {
        tagName: el.tagName,
        className: el.className,
        placeholder: el.placeholder,
        'data-testid': el.getAttribute('data-testid')
    });
});

// Search for recent user messages in chat history
console.log("\n=== Searching for user messages in chat history ===");
const potentialUserMessages = document.querySelectorAll('[data-testid*="user"], [class*="user"], [role="user"]');
console.log(`Found ${potentialUserMessages.length} potential user message elements:`);
potentialUserMessages.forEach((el, i) => {
    console.log(`  User message ${i}:`, {
        tagName: el.tagName,
        className: el.className,
        'data-testid': el.getAttribute('data-testid'),
        role: el.getAttribute('role'),
        innerText: el.innerText ? el.innerText.substring(0, 100) + '...' : 'N/A'
    });
});

console.log("\n=== Analysis Complete ==="); 