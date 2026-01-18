// background.js - Service worker for the Chrome extension
// Handles extension lifecycle and communication

chrome.runtime.onInstalled.addListener(() => {
  console.log('CAPTCHA Challenge Extension installed');
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'captchaPassed') {
    console.log('CAPTCHA validation passed!');
    // You can trigger additional actions here
    sendResponse({ success: true });
  }
  return true; // Keep message channel open for async response
});
