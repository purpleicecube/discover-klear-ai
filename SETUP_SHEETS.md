# Setting up the Google Sheets capture (Make.com → Sheet)

The Discover Klear.ai prototype collects every visitor's form data + behavior into a JSON record and POSTs it to a webhook. Right now the webhook URL is empty, so captures fall back to **console + localStorage** for show-and-tell only. To start landing rows in a Google Sheet, follow the steps below — about 10 minutes, one-time.

## What you'll end up with

- A Google Sheet (one you create + own) with a new row per lead
- A Make.com scenario that listens to the webhook and writes rows
- A webhook URL you paste into `app.js` / `index.html` (one line of code) and push

## Step-by-step

### 1. Create the destination Google Sheet

1. Go to [sheets.google.com](https://sheets.google.com) and **+ New blank sheet**
2. Name it: `Discover Klear.ai Leads`
3. In row 1, add these column headers (one per cell, A→):

   ```
   timestamp | terminal_reached | time_on_site_seconds | slides_visited | page_url | referrer | deal_status | org_name | role | responsibilities | org_type | email | company | timeline | budget | extras
   ```

4. That's it — leave the rest empty. Make.com fills it.

### 2. Sign up for Make.com

1. Go to [make.com](https://www.make.com) → **Sign up free** (use the Google account that owns the Sheet so authorization is easier)
2. Free tier: 1,000 operations/month — plenty for show-and-tell volumes

### 3. Create the scenario

1. From the Make.com dashboard: **Scenarios → Create a new scenario**
2. Click the **+** circle → search for and pick **Webhooks** → **Custom webhook**
3. Click **Add** to create a new webhook, name it `discover-klear-ai-capture` → **Save**
4. Make.com displays a URL like `https://hook.us2.make.com/abc123…` — **copy this URL**, you need it in step 5
5. Click **OK** on the webhook module
6. Click the **+** to the right of the webhook module → search for and pick **Google Sheets** → **Add a Row**
7. Click **Add** under the Google Sheets connection → **Sign in with Google** → authorize Make.com to access your Sheets
8. Fill in:
   - **Spreadsheet:** `Discover Klear.ai Leads` (the one you made)
   - **Sheet name:** `Sheet1` (or whatever your tab is called)
   - **Table contains headers:** Yes
9. The form will now show each column. Map them from the webhook payload:

   | Column | Map to (drag from left pane) |
   | ----- | ----- |
   | timestamp | `timestamp` |
   | terminal_reached | `terminal_reached` |
   | time_on_site_seconds | `time_on_site_seconds` |
   | slides_visited | `slides_visited` (it's an array — Make.com will join with commas) |
   | page_url | `page_url` |
   | referrer | `referrer` |
   | deal_status | `inferred.deal_status` |
   | org_name | `explicit.org_name` |
   | role | `explicit.role` |
   | responsibilities | `explicit.responsibilities` (array) |
   | org_type | `explicit.org_type` |
   | email | `explicit.email` |
   | company | `explicit.company` |
   | timeline | `explicit.timeline` |
   | budget | `explicit.budget` |
   | extras | `explicit.extras` |

10. Click **OK**, then **Save** the scenario (floppy disk icon, bottom toolbar)
11. Toggle the scenario **ON** (the green switch, bottom-left)

### 4. Test the webhook (optional but recommended)

From a terminal, replace `<URL>` with the webhook URL Make.com gave you:

```bash
curl -X POST <URL> \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2026-05-27T20:00:00Z","terminal_reached":"test","time_on_site_seconds":60,"slides_visited":[1,2,3,4,5],"page_url":"test","referrer":null,"explicit":{"org_name":"Test Co","role":"claims-manager","responsibilities":["claims-handling"],"org_type":"pc-carrier","email":"test@test.com","company":"Test Inc","timeline":"this-quarter","budget":"allocated","extras":"test"},"inferred":{"deal_status":"qualified_deal"}}'
```

Then check your Sheet — a new row should appear within a few seconds. If not, look at the scenario's run history in Make.com for the error.

### 5. Paste the webhook URL into the prototype

1. Open `index.html` in this repo
2. Find this line near the top of the `<script>` block:

   ```js
   const CAPTURE_WEBHOOK_URL = ''; // <-- paste your webhook URL here
   ```

3. Replace `''` with the URL Make.com gave you:

   ```js
   const CAPTURE_WEBHOOK_URL = 'https://hook.us2.make.com/abc123…';
   ```

4. Commit + push to `main`. GitHub Pages auto-rebuilds in ~60s.

### 6. Verify end-to-end

1. Open <https://purpleicecube.github.io/discover-klear-ai/> in an incognito window
2. Fill in the form fields (org, role, responsibilities, org type, email, timeline, budget, extras)
3. Click **Book my time**
4. Switch to your Google Sheet — a new row should land within seconds

That's it. Every visitor who clicks Book my time (or abandons after visiting >1 slide) will now write a row to your sheet.

## Want to also pipe to HubSpot / Salesforce later?

Make.com supports both directly. Add a second module to the scenario after Google Sheets, pick HubSpot/Salesforce, map the same fields. The prototype's webhook payload doesn't change.

## Troubleshooting

- **Rows aren't appearing** → Check Make.com → Scenario → History tab. Each webhook hit is logged; click into a failed run to see why.
- **Webhook URL got disabled** → Make.com pauses scenarios after long inactivity. Re-toggle the scenario ON.
- **Want richer data later** → The `app.js` capture record is JSON; you can add new fields to the payload and just add columns to the sheet + map in Make.com without changing the webhook URL.

## Cost note

- Make.com free tier: 1,000 operations/month (1 lead capture = 1 op for the webhook + 1 op for the Sheet write = ~2 ops per lead, so ~500 leads/month free)
- Google Sheets: free, unlimited rows (well, up to 10M cells which is a lot of rows)
- GitHub Pages: free hosting
