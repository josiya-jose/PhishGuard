// Skip browser internal pages and warning page
if (!window.location.href.startsWith("http")) {
  throw new Error("PhishGuard: Skipping non-http page");
}
if (window.location.href.includes(chrome.runtime.id)) {
  throw new Error("PhishGuard: Skipping warning page");
}

// Send URL to background.js to scan
chrome.runtime.sendMessage(
  { action: "scanUrl", url: window.location.href },
  (data) => {
    if (!data) return;

    if (data.risk_score >= 30) {
      showPhishingAlert(data);
      sendBrowserNotification(data);
    }
  }
);

function showPhishingAlert(data) {
  if (document.getElementById("phishguard-overlay")) return;

  const isHigh = data.risk_level === "High Risk";
  const color = isHigh ? "#ff4f6d" : "#f5a623";
  const colorDim = isHigh ? "rgba(255,79,109,0.12)" : "rgba(245,166,35,0.12)";
  const icon = isHigh ? "🚨" : "⚠️";

  const overlay = document.createElement("div");
  overlay.id = "phishguard-overlay";
  overlay.innerHTML = `
    <div id="phishguard-banner" style="
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 2147483647;
      background: #0a0d14;
      border-bottom: 2px solid ${color};
      box-shadow: 0 0 30px ${colorDim}, 0 4px 20px rgba(0,0,0,0.6);
      font-family: 'Segoe UI', sans-serif;
      padding: 0;
      animation: phishguard-slide-in 0.4s cubic-bezier(0.4,0,0.2,1);
    ">
      <style>
        @keyframes phishguard-slide-in {
          from { transform: translateY(-100%); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        @keyframes phishguard-pulse {
          0%, 100% { box-shadow: 0 0 0 0 ${color}44; }
          50% { box-shadow: 0 0 0 6px transparent; }
        }
        #phishguard-banner * { box-sizing: border-box; }
        #phishguard-close:hover { background: rgba(255,255,255,0.1) !important; }
        #phishguard-proceed:hover { opacity: 0.8; }
      </style>

      <div style="
        max-width: 900px; margin: 0 auto;
        padding: 14px 20px; display: flex;
        align-items: center; gap: 14px; flex-wrap: wrap;
      ">
        <div style="
          width: 42px; height: 42px;
          background: ${colorDim}; border: 1px solid ${color};
          border-radius: 8px; display: flex; align-items: center;
          justify-content: center; font-size: 20px; flex-shrink: 0;
          animation: phishguard-pulse 2s infinite;
        ">${icon}</div>

        <div style="flex: 1; min-width: 200px;">
          <div style="
            color: ${color}; font-size: 15px; font-weight: 700;
            letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px;
          ">${icon} ${data.risk_level} — This site may be phishing!</div>
          <div style="
            color: #8892b0; font-size: 12px; font-family: monospace;
            white-space: nowrap; overflow: hidden;
            text-overflow: ellipsis; max-width: 500px;
          ">${truncate(window.location.href, 70)}</div>
        </div>

        <div style="display: flex; gap: 10px; flex-shrink: 0;">
          <div style="
            background: rgba(0,0,0,0.4); border: 1px solid #1e2535;
            border-radius: 8px; padding: 8px 14px; text-align: center;
          ">
            <div style="font-size: 10px; color: #6c7086; font-family: monospace; letter-spacing: 1px; margin-bottom: 2px;">RISK SCORE</div>
            <div style="font-size: 22px; font-weight: 700; color: ${color}; font-family: monospace;">${data.risk_score}%</div>
          </div>
          <div style="
            background: rgba(0,0,0,0.4); border: 1px solid #1e2535;
            border-radius: 8px; padding: 8px 14px; text-align: center;
          ">
            <div style="font-size: 10px; color: #6c7086; font-family: monospace; letter-spacing: 1px; margin-bottom: 2px;">SAFE SCORE</div>
            <div style="font-size: 22px; font-weight: 700; color: #3dffa0; font-family: monospace;">${data.anti_phishing_score}%</div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; flex-shrink: 0;">
          <button id="phishguard-close" onclick="document.getElementById('phishguard-overlay').remove()" style="
            background: transparent; border: 1px solid ${color};
            color: ${color}; border-radius: 6px; padding: 8px 16px;
            font-size: 13px; font-weight: 600; cursor: pointer;
            letter-spacing: 1px; transition: background 0.15s;
          ">✕ DISMISS</button>
          <button id="phishguard-proceed" onclick="document.getElementById('phishguard-overlay').remove()" style="
            background: rgba(255,255,255,0.06); border: 1px solid #1e2535;
            color: #6c7086; border-radius: 6px; padding: 8px 16px;
            font-size: 13px; cursor: pointer; letter-spacing: 1px;
            transition: opacity 0.15s;
          ">Proceed anyway</button>
        </div>
      </div>

      <div style="height: 3px; background: #1e2535;">
        <div style="
          height: 100%; width: ${data.risk_score}%;
          background: ${color}; box-shadow: 0 0 8px ${color};
          transition: width 1s ease;
        "></div>
      </div>
    </div>
  `;

  document.documentElement.appendChild(overlay);
}

function sendBrowserNotification(data) {
  if (!("Notification" in window)) return;

  const send = () => {
    if (Notification.permission === "granted") {
      new Notification("⚠️ PhishGuard Alert", {
        body: `${data.risk_level} detected!\nRisk Score: ${data.risk_score}%\n${truncate(window.location.href, 60)}`,
        icon: chrome.runtime.getURL("icons/icon48.png"),
        tag: "phishguard-alert",
        requireInteraction: data.risk_level === "High Risk",
      });
    }
  };

  if (Notification.permission === "default") {
    Notification.requestPermission().then(send);
  } else {
    send();
  }
}

function truncate(str, max) {
  return str.length > max ? str.substring(0, max) + "..." : str;
}