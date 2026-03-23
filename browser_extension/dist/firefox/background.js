const API_URL = "http://127.0.0.1:8000/predict-extension";

const keepAlive = () => setInterval(chrome.runtime.getPlatformInfo, 20000);
chrome.runtime.onStartup.addListener(keepAlive);
keepAlive();

chrome.runtime.onInstalled.addListener(() => {
  console.log("PhishGuard installed and ready.");
});

// Handle failed page loads
chrome.webNavigation.onErrorOccurred.addListener(async (details) => {
  if (details.frameId !== 0) return;
  if (!details.url.startsWith("http")) return;
  if (details.url.includes(chrome.runtime.id)) return;

  const url = details.url;
  const tabId = details.tabId;
  console.log("PhishGuard: Page failed to load, scanning:", url);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) return;

    const data = await response.json();
    console.log("PhishGuard result:", data);

    if (data.risk_score >= 70) {
      const warningUrl = chrome.runtime.getURL("warning.html") +
        `?url=${encodeURIComponent(url)}` +
        `&risk=${data.risk_score}` +
        `&aps=${data.anti_phishing_score}` + 
        `&confidence=${data.confidence}` +
        `&level=${encodeURIComponent(data.risk_level)}`;

      chrome.tabs.update(tabId, { url: warningUrl, active: true }, (tab) => {
        if (chrome.runtime.lastError) {
          chrome.tabs.create({ url: warningUrl, active: true });
        } else if (tab) {
          chrome.windows.update(tab.windowId, { focused: true });
        }
      });
    }

  } catch (err) {
    console.warn("PhishGuard: Backend unreachable.", err.message);
  }
});

// Listen for messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

  // Handle scan request from content.js
  if (request.action === "scanUrl") {
    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: request.url }),
    })
      .then(r => r.json())
      .then(data => {
        console.log("PhishGuard scan result:", data);
        sendResponse(data);
      })
      .catch(err => {
        console.warn("PhishGuard: scan failed", err.message);
        sendResponse(null);
      });
    return true; // Keep message channel open for async response
  }

  // Handle popup request
  if (request.action === "getCurrentTab") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        sendResponse({ url: tabs[0].url, title: tabs[0].title });
      } else {
        sendResponse({ url: null });
      }
    });
    return true;
  }
});