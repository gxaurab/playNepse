# playNepse 
serves it through a role based gated API and a live-updating dashboard.
It is something that I have wanted to build for myself, that's why I didn't try building it all at once. 
## How it is working?
- Cloudflare tunneling: You are directly sending request to my laptop via cloudflare tunnel. But I should always have it running. 
- Login credentials is shared in the email

## What's not working / not built 

 Want to be upfront to save time about what's missing rather than have you find it:

- No news crawlers, so there are no
  articles in the database. The tables, queue and run tracking are ready for it, and the plan is in the
  "News categorization" section, but nothing actually crawls news today.
- No categorization, so Analysts can't correct anything. Since there's no news, there's no tagging,
  no recategorize endpoint and no correction screen. 
- No report export for Analysts.
- The dashboard is only partly done. The company page (price/VWAP/volume chart, live updates, login,
  roles) works. The "News" and "Behavior analysis" sections on that page are empty placeholders. The
  analysis itself works, but only through the API (`/behavior-summary`, `/compare`), not on frontend
- Compare page and Admin screen are placeholders. Crawl runs, triggering jobs and user management
  all work, but only through the API / Swagger (`/api/admin/...`), not in the UI.
- Floorsheet history is thin: NEPSE only exposes the current day, so broker analysis covers just the
  days I collected (currently one).
- **Not built:** docker-compose, CI, anomaly alerts, and the bonus price-direction classifier. Tests only
  cover auth/RBAC.

Most of my time went into searching all over the internet for data until i found a good github repo, it saved me off manual scraping. But RBAC, websockets, celery, cloudflaredeployment RBAC has been achieved. I'd rather hand in something smaller that genuinely works than bunch of vibe coded screens. 


## Tech stack

| Layer | Choice | 
|---|---|
| API | FastAPI, SQLAlchemy, Pydantic | 
| Database | Postgre + TimescaleDB: "prices" is a hypertable | 
| Queue / scheduler | Celery + Redis + Celery Beat(cron-style schedule, Per-task rate limits and retries with backoff) |
| Real time comm | FastAPI WebSocket + Redis pub/sub |
| Frontend | Vite + React + ts, TanStack (for tanstackquery invalidations), Recharts, Tailwind | 
| Auth | JWT in an httpOnly cookie | 

## Interesting thing found during research: `NepseUnofficialApi` client github
Used for: `getPriceVolumeHistory(date)`, `getFloorSheet()`

#### How it works?
Daily OHLCV: getPriceVolumeHistory(date) returns every symbol's open, high, low, close, volume, turnover, trades and average traded price for one date. The job loops over the last N calendar days, skips off days fri/sat, treats empty days as holidays, and upserts the watchlist rows. The average traded price is total value divided by total quantity, which is the day's VWAP, so VWAP is available for every day without needing the floorsheet.
> Result: 25 trading days per company (2026-08-17 to 2026-09-30) 

Floorsheet: getFloorSheet() returns the full market floorsheet for the current trading (today) day only.
The per-symbol, dated endpoint (getFloorSheetOf) returns HTTP 403 from every environment tried, so past days are not reachable through this source.
Broker member IDs are null in this feed, but broker names are present, so the job stores the names.
Celery Beat collects the floorsheet after market close every trading day, so the sample grows automatically at 3:25 pm.



## Status against the brief

| Work | Status |
|---|---|
| NEPSE daily OHLCV (1 month, 6 self choosen companies -- (inside config file)) | Done |
| Floorsheet (buyer/seller broker, qty, rate) | Done for days collected, broker name only available |
| Queue + per-source rate limit + scheduler + manual trigger | Done (Celery, Redis, Celery Beat) |
| Crawl run monitoring and failure logging | Done (`crawl_runs` table, Admin API) |
| Time-series storage | Done (TimescaleDB hypertable on `prices`) |
| Behavior analysis (VWAP, pressure, anomalies, brokers, news vs next day) | Done (computed on read) |
| Cross-company comparison | Done (`/api/compare`) |
| RBAC (Admin / Analyst / Viewer), enforced server-side | Done |
| Live updates (WebSocket) | Done (`/ws/updates`) |
| Dashboard (auth, company chart, live indicator) | Done |
| News crawlers and categorization | **Not completed in the time limit**. Schema, queue and run tracking are in place; design below |


Design rules:

1. **One codebase, three processes.** `backend/app` runs as the API, the Celery worker and Celery Beat; only the start command differs.
2. **Postgres as database.** Redis only carries the job queue and live events.
3. **Workers write, the API reads.** The API never fetches external data it only enqueues jobs.
4. **Analysis is computed on read** with pandas. A month of daily data per company is tiny, so there are no derived tables to keep in sync.
5. **Every job writes a `crawl_runs` row** (status, timings, item count, error). That table is the Admin monitoring and failure view.
6. **Add stock watchlist in config.** `config/companies.yaml`. Synced into the DB on startup and every job reads the DB watchlist, so adding a company needs no code change.



## Pipeline and scheduling

- **Queues:** a `market` queue for NEPSE jobs (and a `default` queue). The design is one queue per source. news portals would each get their own queue in future.
- **Rate limiting:** set per task with Celery `rate_limit`, plus a delay between date requests in the backfill.
- **Retries:** failed tasks are retried with exponential backoff (`autoretry_for`, `retry_backoff`and `max_retries=2`).
  | Time | Job |
  |---|---|
  | 3:20 | Prices backfill, last 5 days (re-pulls the day after close, so partial intraday rows get corrected) |
  | 3:25 | Floorsheet collection |

- **Manual trigger:** `POST /api/admin/crawl-runs` (Admin only) enqueues a job.
- **Failures:** every job runs inside `track_run()`. It records the status and the error message in `crawl_runs`. Failure are comes through `GET /api/admin/crawl-runs` and in the Admin view.
- **Made sure no idempotent writes:** upserts the floorsheet database rows insert on `contract_id` with `ON CONFLICT DO NOTHING`.


## News categorization (explored news source only, not completed)
Database table exists tho (`news` with a unique URL, `news_tags` with a per-company confidence, `tag_corrections` for the Analyst correction log)
My intended approach:

1. **Crawl:** plain HTTP (httpx + BeautifulSoup) against the server-rendered listing pages of sharesansar and merolagani, with no headless browser. Use ScrapflyAPI for blockings, which directly bypasses everything.
2. **Next step:** embedding similarity (article vs company profile) stored with pgvector in the same Postgres, to catch indirect mentions. Multilingual embeddings is not feasible.possible for nepali news. But It will be a very decent research area to work on. I saw a lot of Nepali news portals, translation to english changes the semantics.

## Role-based access control

| Role | Permissions |
|---|---|
| Admin | Everything, plus watchlist management, re trigger and monitoring, and user management(very large works to do)|
| Analyst | View all data (and correct categorization, once news tagging gets completed) |
| Viewer | Read-only |

- Every route declares `Depends(require_role(...))` or `Depends(get_current_user)` on the server side. The role is loaded from the database on each request.
- The login endpoint sets an httpOnly, SameSite=Lax cookie. A Bearer header is also accepted for the Swagger's Authorize button works.
- The WebSocket authenticates from the same cookie and closes with code 1008 when the cookie is invalid.

## API overview

| Method | Endpoint | Role |
|---|---|---|
| POST | `/api/auth/login`, `/api/auth/logout` | public |
| GET | `/api/auth/me` | any |
| GET | `/api/companies` | any |
| POST / PATCH | `/api/companies`, `/api/companies/{id}` | admin |
| GET | `/api/companies/{id}/prices?range=7d\|30d\|90d` | any |
| GET | `/api/companies/{id}/behavior-summary?range=` | any |
| GET | `/api/compare?range=` | any |
| GET / POST / PATCH | `/api/admin/users` | admin |
| GET / POST | `/api/admin/crawl-runs` | admin |
| WS | `/ws/updates` | any (cookie) |

Errors example if it arises: `{"error": {"code", "message", "details"}}`. 

## Running locally

Prerequisites: Docker, Python 3.11+, Node 20+.

```bash
# 1. Infrastructure
docker run -d --name local-redis -p 6379:6379 redis:7-alpine
docker run -d --name local-postgres -p 5432:5432 -e POSTGRES_PASSWORD=<password> \
  -v pg_ts_data:/var/lib/postgresql/data timescale/timescaledb:latest-pg16
docker exec local-postgres psql -U postgres -c "CREATE DATABASE playnepse;"

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL, JWT_SECRET, seed user credentials
fastapi dev app/main.py         # creates tables and the hypertable, seeds users, syncs the watchlist
python -m app.cli backfill --days 45
python -m app.cli floorsheet    # run after market close (15:00 NPT)

# 3. Workers (separate terminals)
celery -A app.celery_app worker -Q market,default -l info
celery -A app.celery_app beat -l info

# 4. Frontend
cd ../frontend
npm install
npm run dev                     # http://localhost:5173 (proxies /api and /ws to :8000)
```

### Adding a company

Add an entry to `config/companies.yaml` (symbol, name, sector, aliases) and restart the API. The next scheduled or manual job picks it up.


## Findings

<!-- Fill from GET /api/compare?range=30d and the behavior summaries. Keep it to one short paragraph per point, with numbers. -->

- **Most interesting pattern:** `<e.g. SYMBOL had N volume anomalies (z ≥ 2); on X of them the close was below VWAP and CLV was negative, i.e. heavy volume was distribution, not accumulation>`



## What I would do next

1. Think more before making the news crawlers and tagger because this could be trigger to moves.
2. Privately host it 
3. Notifications to Telegram Bot.
4. Gemini API or some AI integrate to make it analyze for more insights/predictions.