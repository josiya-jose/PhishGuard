function getStatus(aps) {
  if (aps >= 75) return "Secure";
  if (aps >= 40) return "Suspicious";
  return "Dangerous";
}

// Tests
console.assert(getStatus(80) === "Secure");
console.assert(getStatus(75) === "Secure");
console.assert(getStatus(50) === "Suspicious");
console.assert(getStatus(20) === "Dangerous");

console.log("Frontend tests passed successfully");