# CATDAMS Extension Analysis: Gemini User Input Capture Issues

## How the Extension Currently Works

### 1. **Message Capture Flow**
```
User types → Content Script detects → Background Script processes → Backend receives
```

### 2. **Content Script Architecture**
- **Platform-specific functions**: `geminiUserInputCapture()`, `chatgptUserInputCapture()`, etc.
- **Universal fallback**: `captureUserInputUniversal()` for unknown platforms
- **Multiple detection methods**:
  - Real-time input monitoring (keydown events)
  - DOM mutation observation (for AI responses)
  - Periodic scanning of chat history

### 3. **Current Gemini Selectors**
```javascript
"gemini.google.com": {
    user: [
        'textarea[aria-label*="input"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
        '.user-query-container',
        'div[aria-label="User input"]'
    ],
    ai: [
        'div[data-testid="bubble"]',
        '.model-response-container',
        '.markdown',
        '.prose',
        'div[role="region"]',
        '.conversation-turn'
    ]
}
```

## Identified Issues with Gemini Capture

### 1. **Selector Mismatch**
The current selectors may not match Gemini's actual DOM structure. Gemini frequently updates its UI, and the selectors may be outdated.

### 2. **Timing Issues**
- **Input capture timing**: The extension waits for Enter key press, but Gemini might use different submission methods
- **DOM observation timing**: MutationObserver might not catch all input changes
- **Debouncing**: 100ms delay might be too short for Gemini's UI updates

### 3. **Input Method Detection**
Gemini might use:
- Dynamic contenteditable elements
- Custom input components
- Different aria-labels or data attributes
- Shadow DOM elements (not accessible via standard selectors)

### 4. **Message State Detection**
The `isMessageComplete()` function might not correctly identify when Gemini messages are finalized.

## Specific Problems

### 1. **User Input Not Detected**
- Selectors don't match actual DOM elements
- Input events not properly bound
- Timing issues with DOM updates

### 2. **AI Responses Captured but User Input Missing**
- AI response selectors work but user input selectors fail
- Different DOM structures for user vs AI messages

### 3. **Inconsistent Capture**
- Works sometimes but not always
- Depends on page state or user interaction patterns

## Recommended Solutions

### 1. **Enhanced Gemini Selectors**
```javascript
"gemini.google.com": {
    user: [
        // Current selectors
        'textarea[aria-label*="input"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
        '.user-query-container',
        'div[aria-label="User input"]',
        // New potential selectors
        'div[data-testid*="input"]',
        'div[data-testid*="user"]',
        'div[role="textbox"][contenteditable="true"]',
        'textarea[data-testid*="input"]',
        'div[class*="input"]',
        'div[class*="user"]'
    ]
}
```

### 2. **Multiple Capture Strategies**
- **Real-time monitoring**: Enhanced event listeners
- **Periodic scanning**: More frequent DOM scanning
- **Mutation observation**: Better DOM change detection
- **Fallback methods**: Multiple approaches for redundancy

### 3. **Improved Timing**
- Longer debounce delays (200-500ms)
- Multiple observation points
- Retry mechanisms for failed captures

### 4. **Debug Logging**
- Enhanced logging for Gemini-specific functions
- DOM structure analysis
- Event capture verification

## Testing Approach

1. **Run the test script** on gemini.google.com to identify actual DOM structure
2. **Update selectors** based on findings
3. **Implement enhanced capture logic** with multiple fallbacks
4. **Add comprehensive logging** for debugging
5. **Test with various user interaction patterns**

## Next Steps

1. Use the test script to analyze actual Gemini DOM structure
2. Update selectors based on findings
3. Implement enhanced capture logic
4. Add comprehensive debugging
5. Test thoroughly with real user interactions 