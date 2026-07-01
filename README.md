# Marktplaats Watch

A tiny watcher that checks Marktplaats for new listings matching a search term
and pushes an alert to your phone. It runs entirely on GitHub's free scheduled
runners — nothing to plug in, no PC left running.

## How it works

1. A GitHub Actions cron job runs `main.py` every 15 minutes.
2. The script calls Marktplaats' internal search API and compares the results
   against `seen.json` (the list of ads it already told you about).
3. Any genuinely new listing triggers a push notification via **ntfy.sh**.
4. The updated `seen.json` is committed back to the repo so the next run
   remembers what it already saw.

The very first run only *seeds* `seen.json` and sends no notifications, so you
don't get spammed with every existing listing at once.

If a run fails for a real reason (e.g. Marktplaats blocks the request, or ntfy
is unreachable), the workflow itself still succeeds — you get a push
notification about the error instead of a "workflow run failed" email. No
new listings is not an error and never triggers anything.

## Setup (about 10 minutes)

### 1. Get a phone notification channel (ntfy)

1. Install the **ntfy** app (iOS / Android) or use the web app.
2. Make up a hard-to-guess topic name.
3. In the app, subscribe to that topic.

### 2. Create the repository

1. Make a new GitHub repo and add these files to it:
   - `main.py` and the `scraper/` package
   - `requirements.txt`
   - `.github/workflows/marktplaats-watch.yml`
2. A **public** repo gets unlimited Actions minutes. A private repo works too
   but free accounts have a monthly minute budget — at every 15 minutes you'll
   use a meaningful chunk of it, so either go public (your `seen.json` is
   harmless to expose) or widen the cron interval to `*/30`.

### 3. Configure your search — secret + variable

In the repo: **Settings → Secrets and variables → Actions**. Secrets and
variables live on the same page, just under different tabs.

- Tab **Secrets** → New repository secret:
  - Name: `NTFY_TOPIC`
  - Value: your topic name (e.g. `watch-x7f9q2`)
  - Read from a secret rather than hard-coded so it stays out of the public code.
- Tab **Variables** → New repository variable:
  - Name: `SEARCH_QUERY`
  - Value: whatever you want to search for (e.g. `"iphone 13"`, `"racefiets"`, anything)
  - Optional: `NTFY_TAGS` if you want different ntfy emoji tags than the default `bell`.

### 4. Turn it on

- Go to the **Actions** tab, enable workflows if prompted.
- Open **Marktplaats Watch** and click **Run workflow** once to do the initial seed.
- After that it runs automatically on the schedule.

## Customising

- **Search term:** edit the `SEARCH_QUERY` repository variable (Settings →
  Secrets and variables → Actions → Variables) — no code changes or commits needed.
- **Check more / less often:** change the `cron` line in the workflow.
- **Self-hosted ntfy:** set a `NTFY_SERVER` secret pointing at your own server.
- **Newest-first results:** open your browser's Network tab on a real
  Marktplaats search, find the `/lrp/api/search` request, and copy whatever sort
  parameters it sends into the `params` dict in `scraper/sources/marktplaats.py`.

## A couple of honest caveats

- This uses an **undocumented** internal API. It works today, but Marktplaats
  can change the field names or response shape without warning; if alerts stop,
  check the Actions log and adjust `parse_listing()`.
- Keep the interval reasonable (every 15 min is plenty). Hammering the endpoint
  is both rude and a good way to get your runner IP throttled.
- Scraping is generally against Marktplaats' terms of service. For low-frequency
  personal use this is rarely an issue, but it's your call.

## Running locally (optional)

```bash
pip install -r requirements.txt
export NTFY_TOPIC="watch-x7f9q2"
export SEARCH_QUERY="your search term"
python main.py
```
