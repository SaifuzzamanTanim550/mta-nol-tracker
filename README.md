# MTA NOL Tracker

**Notice of Liability tracking system**
MABSTOA — Metropolitan Transportation Authority Bus Company · East New York Depot

A full-stack web app that replaces the manual Access data-entry process. Upload an
NOL PDF, let Google Gemini read it and fill in the fields, review, and save. Every
record lands in a searchable log and an Excel tracker you can download anytime.

---

## What it does

- **AI extraction** — upload the NOL PDF; Gemini pulls the notice number, dates,
  fine, plate, location, and violation type into the form for you to review.
- **Record log** — searchable, filterable table of every NOL.
- **Excel tracker** — download an up-to-date `.xlsx` of all records with one click.
- **Dashboard** — live counts of total, open, pending, and dismissed notices.

## Tech

- **Backend:** FastAPI (Python) — serves the API *and* the frontend on one port.
- **Frontend:** HTML / CSS / JavaScript, MTA design system.
- **AI:** Google Gemini (free tier).
- **Storage:** JSON record store; Excel generated on demand.
- **Deploy:** Docker-ready; runs on Render, Railway, or any container host.

## Project structure

```
backend/    FastAPI app, routers, Gemini service, Excel export, storage
frontend/   dashboard, add-NOL, records pages + assets
data/        records.json + generated spreadsheet (gitignored)
run.sh       one command to run everything
```

---

## Run it (GitHub Codespaces — easiest)

1. Open the repo in a Codespace (green **Code** button → **Codespaces** → **Create**).
   Dependencies install automatically.
2. Add your Gemini key once:
   - Open the `.env` file (created for you on first run).
   - Set `GEMINI_API_KEY=` to your key from
     [aistudio.google.com](https://aistudio.google.com) → **API Keys** → **Create API key**.
3. Start the app:
   ```bash
   ./run.sh
   ```
4. Codespaces opens the forwarded port — that's the app. The key persists in your
   Codespace, so next time you only need `./run.sh`.

## Run it locally

```bash
cp .env.example .env        # then paste your key into .env
./run.sh                    # http://localhost:8000
```

## Run with Docker

```bash
docker build -t nol-tracker .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key_here nol-tracker
```

---

## Deploy (Render)

1. Push this repo to GitHub.
2. On Render: **New → Web Service**, point it at the repo.
3. Render detects the `Dockerfile`. No build command needed.
4. Add an environment variable: `GEMINI_API_KEY = your key`.
5. Deploy. The key stays in Render's environment — never in the code.

---

## Security

The Gemini API key is **never** committed or shipped to the browser. It's read from
the environment (`.env` locally, the host's environment variables in production), and
`.env` is gitignored. The browser only ever talks to this app's own backend.


---

*Built for the MABSTOA Emerging Talent Internship Program, Summer 2026.*
