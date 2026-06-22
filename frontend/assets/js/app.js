// Shared UI helpers.

function fmtDate(s) {
  if (!s) return "—";
  const d = new Date(s);
  if (isNaN(d)) return s;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function statusBadge(status) {
  const s = (status || "").toUpperCase();
  const map = { OPEN: "b-open", CLOSED: "b-closed", PENDING: "b-pending", DISMISSED: "b-dismissed" };
  return `<span class="badge ${map[s] || "b-pending"}">${status || "—"}</span>`;
}

function showAlert(containerId, message, type = "ok") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${type === "ok" ? "✓" : "⚠"} ${message}</div>`;
  if (type === "ok") setTimeout(() => (el.innerHTML = ""), 4000);
}

function escapeHtml(str) {
  return (str || "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Mark the active nav link based on the current page.
document.addEventListener("DOMContentLoaded", () => {
  const here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach(a => {
    if (a.getAttribute("href") === here) a.classList.add("active");
  });

  // If the Gemini key isn't set on the backend, surface a gentle banner.
  const banner = document.getElementById("keywarn");
  if (banner) {
    API.health().then(h => { if (!h.gemini_key_set) banner.classList.add("show"); })
       .catch(() => {});
  }
});
