// Records page: load, search/filter, view + edit in a modal, delete.

let ALL = [];
let currentId = null;

const rowsEl = document.getElementById("rows");
const countEl = document.getElementById("count");
const q = document.getElementById("q");
const fStatus = document.getElementById("f-status");
const fViolation = document.getElementById("f-violation");
const overlay = document.getElementById("overlay");
const editForm = document.getElementById("m-body"); // we render a form inside

function render(list) {
  countEl.textContent = list.length;
  if (!list.length) {
    rowsEl.innerHTML = `<tr><td class="empty" colspan="11">No records found. <a href="new-nol.html">Add your first NOL →</a></td></tr>`;
    return;
  }
  rowsEl.innerHTML = list.map(r => `
    <tr onclick="openDetail('${r.id}')">
      <td class="nol">${escapeHtml(r.NOL_Number) || "—"}</td>
      <td>${fmtDate(r.Issue_Date)}</td>
      <td>${fmtDate(r.Date_Received)}</td>
      <td>${escapeHtml(r.Type_of_Violation) || "—"}</td>
      <td>${escapeHtml(r.Vehicle_Number) || "—"}</td>
      <td>${escapeHtml(r.License_Plate_Number) || "—"}</td>
      <td>${escapeHtml((r.Violation_Location || "").slice(0, 26)) || "—"}</td>
      <td>${r.Fine_Amount ? "$" + escapeHtml(r.Fine_Amount) : "—"}</td>
      <td>${fmtDate(r.Due_Date)}</td>
      <td>${escapeHtml(r.Case_Status) || "—"}</td>
      <td>${statusBadge(r.Status)}</td>
    </tr>`).join("");
}

function applyFilters() {
  const text = q.value.toLowerCase().trim();
  const st = fStatus.value;
  const vi = fViolation.value;
  render(ALL.filter(r => {
    const hit = !text || [r.NOL_Number, r.License_Plate_Number, r.Violation_Location, r.Type_of_Violation, r.Vehicle_Number]
      .some(f => f && f.toLowerCase().includes(text));
    return hit && (!st || (r.Status || "") === st) && (!vi || (r.Type_of_Violation || "") === vi);
  }));
}

async function openDetail(id) {
  currentId = id;
  let r;
  try { r = await API.getRecord(id); } catch { return; }
  document.getElementById("m-nol").textContent = r.NOL_Number || "Unknown NOL";
  // Editable form, pre-filled, rendered from the same schema as the Add page.
  document.getElementById("m-body").innerHTML =
    `<form id="editform" class="edit-form">${renderSchema(r)}</form>`;
  overlay.classList.add("show");
}

function closeDetail() { overlay.classList.remove("show"); currentId = null; }

document.getElementById("m-close").addEventListener("click", closeDetail);
document.getElementById("m-close2").addEventListener("click", closeDetail);
overlay.addEventListener("click", e => { if (e.target === overlay) closeDetail(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDetail(); });

document.getElementById("m-save").addEventListener("click", async () => {
  if (!currentId) return;
  const ef = document.getElementById("editform");
  if (!ef) return;
  const data = Object.fromEntries(new FormData(ef));
  if (!data.NOL_Number) { showAlert("alerts", "NOL number cannot be empty.", "err"); return; }
  const btn = document.getElementById("m-save");
  const orig = btn.textContent;
  btn.disabled = true; btn.textContent = "Saving…";
  try {
    await API.updateRecord(currentId, data);
    ALL = await API.listRecords();
    applyFilters();
    closeDetail();
    showAlert("alerts", "Changes saved.", "ok");
  } catch (e) {
    showAlert("alerts", e.message, "err");
  } finally {
    btn.disabled = false; btn.textContent = orig;
  }
});

document.getElementById("m-delete").addEventListener("click", async () => {
  if (!currentId) return;
  if (!confirm("Delete this NOL record? This cannot be undone.")) return;
  try {
    await API.deleteRecord(currentId);
    closeDetail();
    ALL = await API.listRecords();
    applyFilters();
    showAlert("alerts", "Record deleted.", "ok");
  } catch (e) { showAlert("alerts", e.message, "err"); }
});

q.addEventListener("input", applyFilters);
fStatus.addEventListener("change", applyFilters);
fViolation.addEventListener("change", applyFilters);

(async () => {
  try { ALL = await API.listRecords(); applyFilters(); }
  catch { rowsEl.innerHTML = `<tr><td class="empty" colspan="11">Could not reach the server.</td></tr>`; }
})();
