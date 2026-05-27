# Wiring the Discover Klear.ai prototype to DigiFlow

The Discover Klear.ai prototype captures every visitor's form data + behavior into a JSON record and POSTs it to a webhook. The webhook is now a first-class endpoint on **DigiFlow's FastAPI** (Railway-hosted), backed by a shared SQLite store that DigiFlow's Streamlit `Leads` page reads.

This setup file replaces the old `SETUP_SHEETS.md` (Make.com → Google Sheet path) — DigiFlow is now the canonical lead destination.

## Architecture (what lives where)

```text
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│ purpleicecube.github.io/        │         │  DigiFlow Railway container     │
│   discover-klear-ai/            │         │   FastAPI (integrations_api.py) │
│                                 │  POST   │                                 │
│   captureData() builds JSON ───────────▶  │  /webhooks/leads/<funnel_id>    │
│                                 │         │     ↓                           │
└─────────────────────────────────┘         │  leads_store.insert_lead(...)   │
                                            │     ↓                           │
                                            │  data/leads.sqlite              │
                                            └─────────────────────────────────┘
                                                        ↑ read
                                            ┌─────────────────────────────────┐
                                            │  DigiFlow Streamlit (locally    │
                                            │  OR via the /webhooks/leads/.../│
                                            │  export bridge on Streamlit     │
                                            │  Cloud — auth-gated)            │
                                            │                                 │
                                            │  pages/10_Leads.py              │
                                            │   • table + filters             │
                                            │   • drill-in to full payload    │
                                            │   • CSV download                │
                                            └─────────────────────────────────┘
```

## Step-by-step

### 1. Confirm DigiFlow's Railway deploy has the new code

This setup assumes you've already pulled the latest DigiFlow commit (which adds `leads_store.py`, `leads_registry.py`, `pages/10_Leads.py`, and the new `/webhooks/leads/...` routes). Railway should auto-rebuild from your DigiFlow repo on push. Verify by hitting the health endpoint:

```bash
curl https://<your-digiflow-railway-host>/webhooks/leads/_funnels
```

You should see JSON listing `discover-klear-ai` as a registered funnel.

### 2. Grab the webhook URL

The webhook for this prototype is:

```text
https://<your-digiflow-railway-host>/webhooks/leads/discover-klear-ai
```

Get your Railway host from the Railway dashboard for the DigiFlow project.

### 3. Paste the URL into the prototype

Open `index.html` in this repo, find this line near the top of the `<script>` block:

```js
const CAPTURE_WEBHOOK_URL = ''; // <-- paste DigiFlow Railway URL here
```

Replace `''` with your full webhook URL:

```js
const CAPTURE_WEBHOOK_URL = 'https://digiflow-production.up.railway.app/webhooks/leads/discover-klear-ai';
```

Commit + push to `main`. GitHub Pages auto-rebuilds in ~60s.

### 4. Verify end-to-end

1. Open <https://purpleicecube.github.io/discover-klear-ai/> in an incognito window
2. Fill in slide 3 (ICP) + slide 5 (CTA + BANT)
3. Click **Book my time**
4. The prototype POSTs to DigiFlow before opening the Bookings page
5. On DigiFlow (running locally with `streamlit run About.py`), open the **Leads** page (10_Leads). The new row should appear

If the row doesn't land, open the prototype's DevTools console — you'll see either:

- `[Discover Klear.ai] Lead captured →` (worked locally to console + localStorage)
- A `fetch` error pointing at why the POST failed (wrong Railway URL, Railway not redeployed with the new code, or Origin not registered)

## Origin allow-list

The capture endpoint checks the `Origin` header against the funnel's `allowed_origins` list (in DigiFlow's `data/leads_registry.json`). For Discover Klear.ai, defaults allow:

- `https://purpleicecube.github.io` (the public live URL)
- `http://localhost:8000` / `http://127.0.0.1:8000` (local prototype testing)
- `http://localhost:5173` (Vite default, for local dev servers)

To allow a new origin (e.g., moving to `https://discoverklearai.com`), add it to `allowed_origins` in DigiFlow's `data/leads_registry.json` and redeploy.

## Why no Bearer token on the capture endpoint?

The prototype is a public static site. Any auth token in the client-side JavaScript would be discoverable in the page source. The capture endpoint uses Origin checking + pre-registered funnel_ids as its spam-resistance layer. Appropriate for show-and-tell traffic.

The **read** side (GET `/webhooks/leads/<funnel_id>/export`) DOES require a Bearer token (`LEADS_EXPORT_TOKEN`) because that data is sensitive.

## Local development

If you'd rather POST to a local DigiFlow instance:

1. From `WS021_KlearMarketing/06_KlearOpen/klearopen-app/`:

   ```bash
   uvicorn integrations_api:app --port 8502 --reload
   ```

2. Set the prototype's webhook URL to `http://localhost:8502/webhooks/leads/discover-klear-ai`
3. Set the origin to `http://localhost:8000` (or whatever you're serving the prototype from) — it's already in the allow-list

## What data lands

Every lead captured looks like this:

```json
{
  "timestamp": "2026-05-27T20:14:53.221Z",
  "terminal_reached": "book_meeting",
  "time_on_site_seconds": 184,
  "slides_visited": [1, 2, 3, 4, 5],
  "page_url": "https://purpleicecube.github.io/discover-klear-ai/",
  "referrer": "https://klear.ai/",
  "explicit": {
    "org_name": "Acme Insurance",
    "role": "claims-manager",
    "responsibilities": ["claims-handling", "audits-compliance"],
    "org_type": "pc-carrier",
    "email": "darrel@klear.ai",
    "company": "Klear.ai",
    "timeline": "this-quarter",
    "budget": "allocated",
    "extras": "Looking for visibility tools"
  },
  "inferred": { "deal_status": "qualified_deal" }
}
```

DigiFlow's `leads_store` extracts top-level identifying fields (email, company, role, etc.) into indexed SQLite columns for fast filtering. The full payload is preserved verbatim in `payload_json`, so future schema additions flow through without migrations.

## Important caveat: filesystem separation in production

**Locally** (you running both FastAPI and Streamlit on your machine), the Leads page reads the same SQLite file the FastAPI writes — works out of the box.

**In production** (FastAPI on Railway, Streamlit on Streamlit Cloud), they run on **separate filesystems**. Leads land in Railway's SQLite; Streamlit Cloud can't see them directly. The `/webhooks/leads/<funnel_id>/export` endpoint (Bearer-token auth via `LEADS_EXPORT_TOKEN`) is in place as a bridge — a follow-up loop in DigiFlow's Leads page would fetch from there when running on Streamlit Cloud. Out of scope for this round; for now demo from local DigiFlow.
