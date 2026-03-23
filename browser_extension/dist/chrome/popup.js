// popup.js - PhishGuard Extension Logic

const API_URL = "http://localhost:8000/predict";

const scanBtn = document.getElementById("scanBtn");
const urlDisplay = document.getElementById("urlDisplay");
const resultCard = document.getElementById("resultCard");
const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const errorMsg = document.getElementById("errorMsg");
const riskBadge = document.getElementById("riskBadge");
const riskScore = document.getElementById("riskScore");
const antiScore = document.getElementById("antiScore");
const ensembleProb = document.getElementById("ensembleProb");
const riskBar = document.getElementById("riskBar");
const safeBar = document.getElementById("safeBar");

let currentUrl = "";

document.addEventListener("DOMContentLoaded", async () => {
  chrome.runtime.sendMessage({ action: "getCurrentTab" }, (response) => {
    if (response && response.url) {
      currentUrl = response.url;
      urlDisplay.textContent = truncateUrl(currentUrl);
      urlDisplay.title = currentUrl;
    } else {
      urlDisplay.textContent = "Unable to get URL";
      scanBtn.disabled = true;
    }
  });
});

scanBtn.addEventListener("click", async () => {
  if (!currentUrl) return;

  resultCard.classList.add("hidden");
  errorState.classList.add("hidden");
  loadingState.classList.remove("hidden");
  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl }),
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();
    displayResult(data);
  } catch (err) {
    showError(err.message.includes("Failed to fetch")
      ? "Cannot connect to backend. Make sure the server is running on port 8000."
      : err.message
    );
  } finally {
    loadingState.classList.add("hidden");
    scanBtn.disabled = false;
    scanBtn.textContent = "Scan Again";
  }
});

function displayResult(data) {
  riskBadge.textContent = data.risk_level;
  riskBadge.className = "risk-badge " + getRiskClass(data.risk_level);
  riskScore.textContent = data.risk_score + "%";
  antiScore.textContent = data.anti_phishing_score + "%";
  ensembleProb.textContent = (data.ensemble_probability * 100).toFixed(1) + "%";
  riskBar.style.width = data.risk_score + "%";
  safeBar.style.width = data.anti_phishing_score + "%";
  riskBar.className = "bar-fill risk-fill " + getRiskClass(data.risk_level);
  resultCard.className = "result-card " + getRiskClass(data.risk_level);
  resultCard.classList.remove("hidden");
}

function getRiskClass(level) {
  if (level === "High Risk") return "high-risk";
  if (level === "Medium Risk") return "medium-risk";
  return "low-risk";
}

function showError(message) {
  errorMsg.textContent = message;
  errorState.classList.remove("hidden");
}

function truncateUrl(url, maxLen = 45) {
  return url.length > maxLen ? url.substring(0, maxLen) + "..." : url;
}