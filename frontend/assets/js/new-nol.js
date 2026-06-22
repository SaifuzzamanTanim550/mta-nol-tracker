// New NOL page: upload PDF → AI extract → fill form → save.

const form = document.getElementById("form");

// Render all record fields from the shared schema (blank for a new record).
document.getElementById("record-fields").innerHTML = renderSchema({});

const fileInput = document.getElementById("file");
const drop = document.getElementById("drop");
const filebar = document.getElementById("filebar");
const filebarText = document.getElementById("filebar-text");
const filebarX = document.getElementById("filebar-x");
const saveBtn = document.getElementById("save");

// Map free-text AI output onto our exact dropdown options.
function normViolation(v) {
  const t = (v || "").toLowerCase();
  if (/\bace\b|automated camera/.test(t)) return "ACE";
  if (/bus lane/.test(t)) return "Bus Lane";
  if (/red light/.test(t)) return "Red Light";
  if (/school bus/.test(t)) return "School Bus Safety";
  if (/work zone/.test(t)) return "Work Zone Safety";
  if (/weigh/.test(t)) return "Weigh in Motion";
  if (/park/.test(t)) return "Parking";
  if (/courtes/.test(t)) return "Courtesy";
  if (/speed|school zone/.test(t)) return "Speeding";
  return v;
}
function normAgency(v) {
  const t = (v || "").toLowerCase();
  if (/nysdot|state/.test(t)) return "NYSDOT";
  if (/nycdot|dot|dof|finance|transportation/.test(t)) return "NYCDOT";
  return v;
}

function setField(name, value) {
  if (name === "Type_of_Violation") value = normViolation(value);
  if (name === "Enforcement_Agency") value = normAgency(value);
  const el = form.elements[name];
  if (!el || value == null || value === "") return;
  el.value = value;
  el.classList.add("filled");
  setTimeout(() => el.classList.remove("filled"), 1600);
}

async function handleFile(file) {
  if (!file) return;
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    showAlert("alerts", "Please choose a PDF file.", "err");
    return;
  }

  filebar.classList.add("show");
  filebarText.innerHTML = `<span class="spin dark"></span> Reading <strong>${escapeHtml(file.name)}</strong> with AI…`;

  try {
    const fields = await API.extract(file);
    Object.entries(fields).forEach(([k, v]) => setField(k, v));
    filebarText.innerHTML = `Extracted from <strong>${escapeHtml(file.name)}</strong> — please review below`;
    showAlert("alerts", "Fields populated from the document. Review before saving.", "ok");
    autofillMemo();
  } catch (e) {
    filebarText.innerHTML = `<strong>${escapeHtml(file.name)}</strong> attached — AI extraction unavailable, enter fields manually`;
    showAlert("alerts", e.message, "err");
  }
}

drop.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => handleFile(fileInput.files[0]));

drop.addEventListener("dragover", e => { e.preventDefault(); drop.classList.add("over"); });
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", e => {
  e.preventDefault();
  drop.classList.remove("over");
  const f = e.dataTransfer.files[0];
  if (f) { fileInput.files = e.dataTransfer.files; handleFile(f); }
});

filebarX.addEventListener("click", () => {
  fileInput.value = "";
  filebar.classList.remove("show");
});

form.addEventListener("submit", async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  saveBtn.disabled = true;
  saveBtn.innerHTML = `<span class="spin"></span> Saving…`;
  try {
    await API.createRecord(data);
    showAlert("alerts", "NOL record saved. It is now in the Excel tracker and Records list.", "ok");
    form.reset();
    filebar.classList.remove("show");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    showAlert("alerts", err.message, "err");
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save NOL Record";
  }
});


// ---- Memo package ----
const memoEls = {
  round: document.getElementById("m-round"),
  date: document.getElementById("m-date"),
  submit: document.getElementById("m-submit"),
  to: document.getElementById("m-to"),
  depot: document.getElementById("m-depot"),
  from: document.getElementById("m-from"),
  vtype: document.getElementById("m-vtype"),
  re: document.getElementById("m-re"),
};

function recordFromForm() {
  return Object.fromEntries(new FormData(form));
}

async function autofillMemo() {
  try {
    const d = await API.memoDefaults(recordFromForm());
    memoEls.round.value = d.notice_round || "1ST";
    memoEls.date.value = d.memo_date || "";
    memoEls.submit.value = d.submit_by || "";
    memoEls.to.value = d.to_line || "";
    memoEls.depot.value = d.depot_code || "";
    memoEls.from.value = d.from_line || "";
    memoEls.vtype.value = d.vehicle_type_short || "BUS";
    memoEls.re.value = d.re_line || "";
  } catch (e) { /* leave fields as-is */ }
}

document.getElementById("m-autofill").addEventListener("click", autofillMemo);

document.getElementById("genmemo").addEventListener("click", async () => {
  const record = recordFromForm();
  if (!record.NOL_Number) {
    showAlert("alerts", "Enter the NOL number first.", "err");
    return;
  }
  const memo = {
    notice_round: memoEls.round.value,
    memo_date: memoEls.date.value,
    submit_by: memoEls.submit.value,
    to_line: memoEls.to.value,
    depot_code: memoEls.depot.value,
    from_line: memoEls.from.value,
    vehicle_type_short: memoEls.vtype.value || "BUS",
    re_line: memoEls.re.value,
  };
  const scan = fileInput.files[0] || null;
  if (!scan && !confirm("No NOL PDF is attached. Generate the memo without the scanned NOL behind it?")) {
    return;
  }
  const btn = document.getElementById("genmemo");
  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spin dark"></span> Building…`;
  try {
    const { blob, filename } = await API.generateMemo(record, memo, scan);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showAlert("alerts", "Memo package downloaded — " + filename, "ok");
  } catch (e) {
    showAlert("alerts", e.message, "err");
  } finally {
    btn.disabled = false;
    btn.innerHTML = orig;
  }
});