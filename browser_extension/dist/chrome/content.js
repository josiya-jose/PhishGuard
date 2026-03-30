// Skip browser internal pages and extension pages
if (!window.location.href.startsWith("http")) {
  throw new Error("PhishGuard: Skipping non-http page");
}
if (window.location.href.includes(chrome.runtime.id)) {
  throw new Error("PhishGuard: Skipping extension page");
}

// Send URL to background.js to scan
chrome.runtime.sendMessage(
  { action: "scanUrl", url: window.location.href },
  (data) => {
    if (!data) return;

    // Show banner only for meaningful risk
    if (data.risk_score >= 70) {
      showPhishingAlert(data);
      sendBrowserNotification(data);
    }
  }
);

function showPhishingAlert(data) {
  if (document.getElementById("phishguard-overlay")) return;

  const risk = parseFloat(data.risk_score) || 0;
  const aps = parseFloat(data.anti_phishing_score) || 0;

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
      animation: phishguard-slide-in 0.4s ease;
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
      </style>

      <div style="
        max-width: 900px; margin: 0 auto;
        padding: 14px 20px;
        display: flex; align-items: center;
        gap: 14px; flex-wrap: wrap;
      ">

        <!-- Icon -->
        <div style="
          width: 42px; height: 42px;
          background: ${colorDim};
          border: 1px solid ${color};
          border-radius: 8px;
          display: flex; align-items: center;
          justify-content: center;
          font-size: 20px;
          animation: phishguard-pulse 2s infinite;
        ">
          ${icon}
        </div>

        <!-- Text -->
        <div style="flex: 1; min-width: 200px;">
          <div style="
            color: ${color};
            font-size: 15px;
            font-weight: 700;
            text-transform: uppercase;
          ">
            ${icon} ${data.risk_level} — This site may be phishing!
          </div>
          <div style="
            color: #8892b0;
            font-size: 12px;
            font-family: monospace;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 500px;
          ">
            ${truncate(window.location.href, 70)}
          </div>
        </div>

        <!-- Scores -->
        <div style="display: flex; gap: 10px;">

          <!-- Risk Score -->
          <div style="
            background: rgba(0,0,0,0.4);
            border: 1px solid #1e2535;
            border-radius: 8px;
            padding: 8px 14px;
            text-align: center;
          ">
            <div style="font-size: 10px; color: #6c7086; font-family: monospace;">
              RISK SCORE
            </div>
            <div style="
              font-size: 22px;
              font-weight: 700;
              color: ${color};
              font-family: monospace;
            ">
              ${risk.toFixed(2)}%
            </div>
          </div>

          <!-- Anti-Phishing Score -->
          <div style="
            background: rgba(0,0,0,0.4);
            border: 1px solid #1e2535;
            border-radius: 8px;
            padding: 8px 14px;
            text-align: center;
          ">
            <div style="font-size: 10px; color: #6c7086; font-family: monospace;">
              ANTI-PHISHING SCORE
            </div>
            <div style="
              font-size: 22px;
              font-weight: 700;
              color: #3dffa0;
              font-family: monospace;
            ">
              ${aps.toFixed(2)}%
            </div>
          </div>

        </div>

        <!-- Buttons -->
        <div style="display: flex; gap: 8px;">
          <button onclick="document.getElementById('phishguard-overlay').remove()" style="
            background: transparent;
            border: 1px solid ${color};
            color: ${color};
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
          ">
            DISMISS
          </button>

          <button onclick="document.getElementById('phishguard-overlay').remove()" style="
            background: rgba(255,255,255,0.06);
            border: 1px solid #1e2535;
            color: #6c7086;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
          ">
            Proceed
          </button>
        </div>

      </div>

      <!-- Risk bar -->
      <div style="height: 3px; background: #1e2535;">
        <div style="
          height: 100%;
          width: ${risk}%;
          background: ${color};
          box-shadow: 0 0 8px ${color};
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
        body: `${data.risk_level} detected!\nRisk: ${parseFloat(data.risk_score).toFixed(2)}%`,
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