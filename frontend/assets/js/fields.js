// Shared NOL field schema. Both the Add page and the Records edit modal render
// from this, so the two always stay in sync. Edit a dropdown here once and it
// updates everywhere.

const VIOLATION_TYPES = [
  "ACE", "Bus Lane", "Courtesy", "Parking", "Red Light",
  "School Bus Safety", "Speeding", "Weigh in Motion", "Work Zone Safety",
];

const ENFORCEMENT_AGENCIES = ["NYCDOT", "YPVB", "NCTPVA", "NYSDOT", "COY", "TOH"];

const DEPOTS = [
  "100", "BCC", "BK Division", "BKLUN RD", "BPK", "BUS TECH", "BX DIV", "BS RD",
  "CHL", "CMF", "CPT", "CRS", "CST", "ECH", "ENY", "FLT", "FRK", "FRP", "GRD",
  "GRD CMF", "GUN", "JAM", "JFK", "JGL", "KBG", "LGA", "LRL", "MAN RD", "MCH MER",
  "MJQ", "MTV", "P&E", "QNS RD", "QUV", "REV", "SEM", "SI RD", "SPK", "STG",
  "UPK", "WFR", "YON", "YUK", "ZER CMF", "ZER Trns",
];

const DIVISIONS = [
  "Bronx", "Brooklyn", "BUS TECHNOLOGY", "Collection & Services", "ENY CMF",
  "Facilities", "Grand Avenue CMF", "Labor Relations", "Manhattan",
  "Queens North", "Queens South", "Road Operations", "Safety",
  "Safety & Training", "Staten Island", "Trans Support", "Zerega CMF",
];

const CASE_STATUSES = [
  "Paid after Due Date", "Pending Driver Info", "Pending Payment",
  "Pending Discipline", "Closed", "Dismissed", "Non-PO", "Non-PO Late Fee",
  "Late Fee - Dept", "TBH - MTA Budget", "Dispute", "2DOF-Request Dismissal",
  "DOF-Deemed Guilty", "DOF-Not Guilty", "TSDAmtPaid_BalRef2Bu", "On-Hold",
];

// Grouped so related fields sit together and are easy to follow.
const NOL_SCHEMA = [
  {
    group: "NOL Details",
    fields: [
      { key: "NOL_Number", label: "NOL Number (Notice #)", type: "text", required: true, placeholder: "From the scanned NOL" },
      { key: "Issue_Date", label: "NOL Date (Issue Date)", type: "date" },
      { key: "Date_Received", label: "Date Received", type: "date" },
      { key: "Type_of_Violation", label: "Type of Violation", type: "select", options: VIOLATION_TYPES },
      { key: "Enforcement_Agency", label: "Enforcement Agency", type: "select", options: ENFORCEMENT_AGENCIES },
    ],
  },
  {
    group: "Violation",
    fields: [
      { key: "Violation_Date", label: "Violation Date", type: "date" },
      { key: "Violation_Time", label: "Violation Time", type: "time" },
      { key: "Violation_Location", label: "Violation Location", type: "text", wide: true },
      { key: "Speed_Over_Limit", label: "Speed Over Limit", type: "text", placeholder: "Leave blank unless needed" },
    ],
  },
  {
    group: "Vehicle & Assignment",
    fields: [
      { key: "License_Plate_Number", label: "License Plate Number", type: "text" },
      { key: "Vehicle_Number", label: "Vehicle Number", type: "text" },
      { key: "Depot_Assigned_To", label: "Depot / Assigned To", type: "select", options: DEPOTS },
      { key: "Division", label: "Division", type: "select", options: DIVISIONS },
      { key: "Vehicle_Parked_At", label: "Vehicle Parked At", type: "text" },
    ],
  },
  {
    group: "Financial",
    fields: [
      { key: "Fine_Amount", label: "Amount Due ($)", type: "number", step: "0.01", placeholder: "From the NOL" },
      { key: "Due_Date", label: "Due Date", type: "date" },
      { key: "TSD_Amount", label: "TSD Amount", type: "number", step: "0.01" },
      { key: "Budget_2_Pay", label: "Budget 2 Pay", type: "number", step: "0.01" },
      { key: "Late_Fee", label: "Late Fee", type: "number", step: "0.01" },
    ],
  },
  {
    group: "Notices & Memo",
    fields: [
      { key: "Memo_Date", label: "Memo Date", type: "date" },
      { key: "Notice_2nd_Date", label: "2nd Notice Date", type: "date" },
      { key: "Notice_3rd_Date", label: "3rd Notice Date", type: "date" },
    ],
  },
  {
    group: "Case Tracking",
    fields: [
      { key: "Case_Status", label: "Case Status", type: "select", options: CASE_STATUSES },
      { key: "Status", label: "Status", type: "select", options: ["OPEN", "CLOSED"] },
    ],
  },
  {
    group: "Remarks Pertaining to NOL",
    fields: [
      { key: "Remarks", label: "Remarks Pertaining to NOL", type: "textarea", full: true },
    ],
  },
];

function _opt(value, selected) {
  const v = escapeHtml(value);
  return `<option value="${v}"${value === selected ? " selected" : ""}>${v}</option>`;
}

function fieldHtml(f, record) {
  const val = record && record[f.key] != null ? String(record[f.key]) : "";
  const wide = f.wide ? " span-2" : "";
  const req = f.required ? " required" : "";
  let control;
  if (f.type === "select") {
    const opts = f.options.map(o => _opt(o, val)).join("");
    control = `<select name="${f.key}"${req}><option value="">Select…</option>${opts}</select>`;
  } else if (f.type === "textarea") {
    control = `<textarea name="${f.key}" rows="5" placeholder="Notes about this NOL…">${escapeHtml(val)}</textarea>`;
  } else {
    const step = f.step ? ` step="${f.step}"` : "";
    const ph = f.placeholder ? ` placeholder="${escapeHtml(f.placeholder)}"` : "";
    control = `<input type="${f.type}" name="${f.key}" value="${escapeHtml(val)}"${step}${ph}${req} />`;
  }
  return `<div class="field${wide}"><label>${escapeHtml(f.label)}</label>${control}</div>`;
}

// Render every group as section label + grid. Pass a record to pre-fill (edit
// mode); pass nothing for a blank form (add mode).
function renderSchema(record) {
  return NOL_SCHEMA.map(group => {
    const isFull = group.fields.length === 1 && group.fields[0].full;
    const gridClass = isFull ? "grid grid-1" : "grid";
    const note = group.note ? `<p class="section-note">${escapeHtml(group.note)}</p>` : "";
    const fields = group.fields.map(f => fieldHtml(f, record)).join("");
    return `<div class="section-label">${escapeHtml(group.group)}</div>${note}<div class="${gridClass}">${fields}</div>`;
  }).join("");
}
