document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);

  const url = decodeURIComponent(params.get("url") || "");
  const risk = params.get("risk");
  const level = decodeURIComponent(params.get("level") || "High Risk");

  if (!risk || !url) {
    document.getElementById("expiredCard").style.display = "block";
  } else {
    document.getElementById("warningCard").style.display = "block";

    const riskNum = parseFloat(risk) || 0;
    const safeNum = 100 - riskNum;

    document.getElementById("riskScore").textContent =
      riskNum.toFixed(2) + "%";

    document.getElementById("safeScore").textContent =
      safeNum.toFixed(2) + "%";

    document.getElementById("flaggedUrl").textContent = url;
    document.getElementById("riskBadge").textContent = level;
    document.getElementById("barPct").textContent =
      riskNum.toFixed(2) + "%";

    setTimeout(() => {
      document.getElementById("riskBar").style.width = riskNum + "%";
    }, 200);

    document.getElementById("proceedBtn").addEventListener("click", () => {
      window.location.href = url;
    });
  }
});