// API client — talks to the FastAPI backend on the same origin.
// Because the backend serves this frontend too, the base URL is just "".
const API = {
  async health() {
    const r = await fetch("/api/health");
    return r.json();
  },

  async stats() {
    const r = await fetch("/api/stats");
    return r.json();
  },

  async listRecords() {
    const r = await fetch("/api/records");
    return r.json();
  },

  async getRecord(id) {
    const r = await fetch(`/api/records/${id}`);
    if (!r.ok) throw new Error("Record not found");
    return r.json();
  },

  async createRecord(record) {
    const r = await fetch("/api/records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "Save failed");
    return r.json();
  },

  async deleteRecord(id) {
    const r = await fetch(`/api/records/${id}`, { method: "DELETE" });
    if (!r.ok) throw new Error("Delete failed");
    return r.json();
  },

  async updateRecord(id, record) {
    const r = await fetch(`/api/records/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    if (!r.ok) throw new Error((await r.json()).detail || "Update failed");
    return r.json();
  },

  async extract(file) {
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch("/api/extract", { method: "POST", body: fd });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || "Extraction failed");
    return data.fields;
  },

  exportUrl() {
    return "/api/records/export.xlsx";
  },

  async memoDefaults(record) {
    const r = await fetch("/api/memo-defaults", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    return r.json();
  },

  async generateMemo(record, memo, scan) {
    const fd = new FormData();
    fd.append("record", JSON.stringify(record));
    fd.append("memo", JSON.stringify(memo));
    if (scan) fd.append("scan", scan);
    const r = await fetch("/api/memo", { method: "POST", body: fd });
    if (!r.ok) {
      let detail = "Memo generation failed";
      try { detail = (await r.json()).detail || detail; } catch (e) {}
      throw new Error(detail);
    }
    const cd = r.headers.get("Content-Disposition") || "";
    const m = cd.match(/filename="?([^"]+)"?/);
    const filename = m ? m[1] : "memo.pdf";
    const blob = await r.blob();
    return { blob, filename };
  },
};
