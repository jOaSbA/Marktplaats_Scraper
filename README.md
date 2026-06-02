# Creami Watch

A tiny watcher that checks Marktplaats for new listings matching a search term
(default: **ninja creami**) and pushes an alert to your phone. It runs entirely
on GitHub's free scheduled runners — nothing to plug in, no PC left running.

## How it works

1. A GitHub Actions cron job runs `check_creami.py` every 15 minutes.
2. The script calls Marktplaats' internal search API and compares the results
   against `seen.json` (the list of ads it already told you about).
3. Any genuinely new listing triggers a push notification via **ntfy.sh**.
4. The updated `seen.json` is committed back to the repo so the next run
   remembers what it already saw.

The very first run only *seeds* `seen.json` and sends no notifications, so you
don't get spammed with every existing Creami at once.

## Setup (about 10 minutes)

### 1. Get a phone notification channel (ntfy)

1. Install the **ntfy** app (iOS / Android) or use the web app.
2. Make up a hard-to-guess topic name.
3. In the app, subscribe to that topic.

### 2. Create the repository

1. Make a new GitHub repo and add these files to it:
   - `check_creami.py`
   - `requirements.txt`
   - `.github/workflows/creami-watch.yml`
2. A **public** repo gets unlimited Actions minutes. A private repo works too
   but free accounts have a monthly minute budget — at every 15 minutes you'll
   use a meaningful chunk of it, so either go public (your `seen.json` is
   harmless to expose) or widen the cron interval to `*/30`.

### 3. Add your ntfy topic as a secret

In the repo: **Settings → Secrets and variables → Actions → New repository
secret**.

- Name: `NTFY_TOPIC`
- Value: your topic name (e.g. `creami-watch-x7f9q2`)

The topic is read from a secret rather than hard-coded so it stays out of the
public code.

### 4. Turn it on

- Go to the **Actions** tab, enable workflows if prompted.
- Open **Creami Watch** and click **Run workflow** once to do the initial seed.
- After that it runs automatically on the schedule.

## Customising

- **Different search term:** edit `SEARCH_QUERY` in the workflow's `env:` block
  (e.g. `"ninja creami deluxe"`).
- **Check more / less often:** change the `cron` line in the workflow.
- **Self-hosted ntfy:** set a `NTFY_SERVER` secret pointing at your own server.
- **Newest-first results:** open your browser's Network tab on a real
  Marktplaats search, find the `/lrp/api/search` request, and copy whatever sort
  parameters it sends into the `params` dict in `check_creami.py`.

## A couple of honest caveats

- This uses an **undocumented** internal API. It works today, but Marktplaat
  can change the field names or response shape without warning; if alerts stsop,
  check the Actions log and adjust `parse_listing()`.
- Keep the interval reasonable (every 15 min is plenty). Hammering the endpoint
  is both rude and a good way to get your runner IP throttled.
- Scraping is generally against Marktplaats' terms of service. For low-frequency
  personal use this is rarely an issue, but it's your call.

## Running locally (optional)

```bash
pip install -r requirements.txt
export NTFY_TOPIC="creami-watch-x7f9q2"
export SEARCH_QUERY="ninja creami"
python check_creami.py
```
"# Marktplaats_Scraper" 
