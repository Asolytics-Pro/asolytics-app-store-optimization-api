# Asolytics Public API Endpoints

- Source docs: `https://app.asolytics.pro/api/public-api/documentation`
- Source OpenAPI: `https://app.asolytics.pro/api/public-api/docs?public-api-docs.json`
- Generated from spec version: `1.0.0-alpha`
- Generated at: `2026-06-18T18:24:01.072654+00:00`

## Authentication

- Header: `X-PUBLIC-API-TOKEN`

## Applications

### `GET /public-api/v1/applications/availability`

- Summary: Applications availability
- Notes: Returns the list of countries in which each of the given apps is currently live in the store. Apps available nowhere (taken down, not yet released, region-blocked everywhere we check) are omitted from the response entirely. **Costs:** 10 tokens per app present in the response. A request whose apps are all unavailable returns an empty list and is free.
- Parameters:

`origin_ids[]` - in `query` - array<string> - required - maxItems=10

### `GET /public-api/v1/applications/installs`

- Summary: Application installs history
- Notes: Returns monthly **estimated** installs for a single application across every country we currently track, for each month in the requested range. Values are estimates derived from store signals — not measured installs — and are emitted as `null` for months we couldn't estimate (sparsely-tracked apps, or the most recent month while it's still being computed). Returns 404 if the `origin_id` doesn't resolve to a known application. **Costs:** 5 tokens per emitted (country, month) pair carrying a non-null value (`0` counts; `null` does not). Minimum 5 tokens per call — charged even if the entire grid is null.
- Parameters:

`origin_id` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/applications/metadata`

- Summary: Applications metadata
- Notes: Returns the latest text metadata (title, sub_title, description) of the given apps in the requested locales — the same text the store currently shows on each app's listing page. Only locales that actually carry data are emitted; `origin_id`s we don't have indexed are silently absent. **Costs:** 10 tokens per returned (app, locale) pair. A request that returns no pairs is free.
- Parameters:

`origin_ids[]` - in `query` - array<string> - required - maxItems=10
`locales[]` - in `query` - array<string> - required - maxItems=10

### `GET /public-api/v1/applications/metadata/media`

- Summary: Applications media
- Notes: Returns the latest screenshots and preview videos of the given apps in the requested locales — the same media the store currently shows on each app's listing page. Each screenshot carries its `device` and 0-based `position` so you can reconstruct the gallery order. Only locales that actually carry media are emitted; `origin_id`s we don't have indexed are silently absent. **Costs:** 10 tokens per returned (app, locale) pair. A request that returns no pairs is free.
- Parameters:

`origin_ids[]` - in `query` - array<string> - required - maxItems=10
`locales[]` - in `query` - array<string> - required - maxItems=10

### `GET /public-api/v1/applications/ranking`

- Summary: Application ranking history
- Notes: Returns the ranking history of a single application in the given country, as a paginated flat list of `{date, keyword, position}` rows — one row per scanned (date, keyword) pair the app ranks for, across every keyword we cover (no keyword filter). Supports a position-range filter and sorting by `date`, `position` or `keyword`; pipeline is filter → sort → paginate, so `total` / `total_pages` reflect the filtered universe. The window cannot exceed **7 days** and `date_from` cannot reach further back than the 1st of (current month − 5 months). Returns 404 if the `origin_id` doesn't resolve to a known application; apps with no scans in range return an empty page (still billed the minimum). **Costs:** `max(5, ceil(rows_on_page / 20))` tokens — 1 token per started bucket of 20 rows on the returned page, with a floor of 5 charged even on empty responses.
- Parameters:

`origin_id` - in `query` - string - required
`country_code` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`page` - in `query` - integer
`per_page` - in `query` - integer
`sort_by` - in `query` - string - enum: date, position, keyword
`sort_order` - in `query` - string - enum: asc, desc
`filters[position][from]` - in `query` - integer
`filters[position][to]` - in `query` - integer

### `GET /public-api/v1/applications/ranking/latest-by-keywords`

- Summary: Latest ranking position per keyword
- Notes: Returns the app's **latest known** ranking position for each of the requested keywords in the given store/country. Because keywords are parsed on independent schedules, each keyword carries its own `date` — they will not always share the same parse day. Keywords the app does not currently rank for are omitted from the response. The store (Google Play / App Store) is inferred from the `origin_id`. **Costs:** 1 token per 30 requested keywords, minimum 5 per call (billed on the request, not the number of rows returned).
- Parameters:

`origin_id` - in `query` - string - required
`country_code` - in `query` - string - required
`keywords[]` - in `query` - array<string> - required - maxItems=1000

### `GET /public-api/v1/applications/revenue`

- Summary: Application revenue history
- Notes: Returns monthly **estimated** revenue (USD) for a single application across every country we currently track, for each month in the requested range. Values are estimates derived from store signals — not measured revenue — and are emitted as `null` for months we couldn't estimate (sparsely-tracked apps, or the most recent month while it's still being computed). Returns 404 if the `origin_id` doesn't resolve to a known application. **Costs:** 5 tokens per emitted (country, month) pair carrying a non-null value (`0` counts; `null` does not). Minimum 5 tokens per call — charged even if the entire grid is null.
- Parameters:

`origin_id` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/applications/versions`

- Summary: Application version history
- Notes: Returns the full version history of a single application, newest-first — every release we've captured from the store, with the developer's release notes when present. Returns 404 if the `origin_id` doesn't resolve to a known application; apps with no captured versions return an empty `versions` list (still billed). **Costs:** 10 tokens per call.
- Parameters:

`origin_id` - in `query` - string - required

## Balance

### `GET /public-api/v1/balance`

- Summary: Get token balance
- Notes: Returns the user's current public-API token balance along with the last 100 balance transactions (newest first). Each transaction carries its `cause` (the endpoint key that triggered the debit, `null` for system rows like the monthly balance renewal), a signed `amount` (debits are negative), the timestamp, and a pointer back to the originating public-API request (`null` for system rows). The full `cause_details` payload is intentionally not exposed here — treat the list as a quick activity feed, not a complete audit trail. **Costs:** 1 token per call.

## Common Catalogs

### `GET /public-api/v1/common-catalogs/categories`

- Summary: List categories
- Notes: Returns the store-chart categories for the given store. Each entry's `key` is the value to pass as `category_key` on `/v1/store-charts`. The list changes rarely; cache it on your side. **Costs:** 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY

### `GET /public-api/v1/common-catalogs/clusters`

- Summary: List clusters
- Notes: Returns the chart clusters for the given store — App Store: top-free / top-paid / top-grossing × iPhone / iPad; Google Play: the equivalent set. Each entry's `key` is the value to pass as `cluster_key` on `/v1/store-charts`. The list changes rarely; cache it on your side. **Costs:** 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY

### `GET /public-api/v1/common-catalogs/countries`

- Summary: List countries
- Notes: Returns the countries we support for the given store — the valid values for every `country_code` parameter elsewhere in the API. The list changes rarely; cache it on your side rather than calling on every request. **Costs:** 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY

### `GET /public-api/v1/common-catalogs/devices`

- Summary: List devices
- Notes: Returns the device keys we support for the given store — `IPHONE` and `IPAD` on App Store, `MOBILE` on Google Play. These are the valid values for every `device` parameter elsewhere in the API (live-search, store-charts). The list changes rarely; cache it on your side. **Costs:** 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY

### `GET /public-api/v1/common-catalogs/locales`

- Summary: List locales
- Notes: Returns the locales we support for the given store — the valid values for `locales[]` on the applications/metadata and applications/metadata/media endpoints. The list changes rarely; cache it on your side rather than calling on every request. **Costs:** 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY

## Competitors

### `GET /public-api/v1/competitors`

- Summary: List competitors
- Notes: Returns the apps marked as competitors on the project, optionally filtered by state. Competitor state is tracked in the project store's US country (the public API hides per-country state — each app has exactly one state in the list). Each entry carries the competitor app's basic info and its current state (`competitor`, `non_competitor`, `indirect_competitor`). **Costs:** 10 tokens per call.
- Parameters:

`project_id` - in `query` - integer - required
`filters[competitor_state][]` - in `query` - array<string> - maxItems=50

### `POST /public-api/v1/competitors/mark`

- Summary: Mark a competitor
- Notes: Marks an app (by its store `origin_id`) as `competitor`, `non_competitor` or `indirect_competitor` for the project. Idempotent — re-marking with the same state is a no-op; re-marking with a different state moves the app to that state. Returns 404 if the `competitor_origin_id` doesn't resolve to a known app. **Costs:** 1 token per call.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `competitor_origin_id` required: string — Store origin id of the competitor app — App Store: numeric track id; Google Play: bundle id.
- `state` required: string (competitor, non_competitor, indirect_competitor)

### `POST /public-api/v1/competitors/unmark`

- Summary: Unmark a competitor
- Notes: Removes any competitor mark for the given app (by its store `origin_id`) within the project — the app drops out of the competitors list entirely. Returns 404 if the `competitor_origin_id` doesn't resolve to a known app. **Costs:** 1 token per call.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `competitor_origin_id` required: string — Store origin id of the competitor app — App Store: numeric track id; Google Play: bundle id.

## Keywords

### `GET /public-api/v1/keywords/metrics`

- Summary: Keywords latest metrics
- Notes: Returns a snapshot of one or more latest metrics for up to 250 keywords in a (store, country). Each keyword in the response appears exactly once in the same order and casing as the request; duplicate keywords are deduplicated. Only the requested metrics are present on each keyword object. Metrics that resolve to null (no scan data available) are omitted from the billed pairs but still appear in the response as null. **Metric availability by store:** - `popularity` — App Store only (raw scan); Google Play omits the `popularity` field, only `mlp_popularity` is returned. - `max_popularity` — App Store: `year_max_popularity` (raw) and `synthetic_year_max_popularity` (mlp). Google Play: `mlp_max_popularity` only (`all_time_max_popularity`). - `impressions` — App Store: estimated daily impressions derived from both real and synthetic popularity. Google Play: `mlp_impressions` only. - `difficulty` — both stores, single value (no real/mlp split). - `language` — both stores, country-independent, single value. **Costs:** 1 token per (keyword, metric) pair where the resolved value is non-null; minimum 1 token per call.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=250
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`metrics[]` - in `query` - array<string> - required - maxItems=50

### `GET /public-api/v1/keywords/popularity`

- Summary: Keywords popularity history
- Notes: Returns per-keyword popularity history for a (store, country) across the requested date range. For App Store each date carries both `popularity` (raw scan) and `mlp_popularity` (the ML-derived synthetic value that smooths over scan gaps); for Google Play only `mlp_popularity` is returned because GP stores a single popularity column. Only dates with real scans are emitted — no gap-filling, no interpolation. Up to 1000 keywords per request; `date_from` cannot reach further back than the start of (current month − 6 months). **Costs:** 1 token per (keyword, date) pair returned. A request with no scans in range is free.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=1000
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/keywords/ranking`

- Summary: Keywords ranking history
- Notes: Returns the top-50 ranking history per keyword for a (store, country) across the requested date range. For each date we emit the apps in their store-shown order with `origin_id` and current title. Dates without a scan are skipped — no gap-filling; apps we couldn't resolve to a known origin are dropped from the positions list. Up to 500 keywords per request; `date_from` cannot reach further back than the start of (current month − 6 months). **Costs:** 1 token per (keyword, date) pair returned. A request with no scans in range is free.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=500
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

## Live Search

### `GET /public-api/v1/live-search`

- Summary: Live search top 50
- Notes: Returns the live (real-time) top-50 search results for a keyword in the given (store, country, device) — what a user would currently see on the store's search results page, including paid ad placements alongside organic items. On App Store each item carries its `type` (`apps`, `preorder`, `app-bundles`, `developers`, `editorial-items`, `in-apps`, `subscription`); Google Play returns apps only. `is_paid` marks ad placements and `position` is the 1-based rank in the full list with paid items counted. Items we couldn't resolve to a known origin are silently dropped. **Costs:** 20 tokens per call that returns at least one item; 5 tokens per call that returns an empty list (empty isn't necessarily an error — the keyword may simply have no live matches).
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`keyword` - in `query` - string - required
`country_code` - in `query` - string - required
`device` - in `query` - string - required - enum: IPHONE, IPAD, MOBILE

## Projects

### `GET /public-api/v1/projects/countries-keywords-counts`

- Summary: Get per-country keyword counters
- Notes: Returns, for every store country of the project, the tracked / recommended / ranking keyword counters together with their day-over-day `dynamic`. The result is keyed by 2-letter country code. **Note:** these counters are pre-aggregated and reflect the **previous day's** snapshot, so they may lag the real data by up to a day. For exact, up-to-the-moment values use the list endpoints directly (e.g. `/v1/tracking/keywords`, `/v1/recommended-keywords`, `/v1/applications/ranking`). **Costs:** 20 tokens per call.
- Parameters:

`project_id` - in `query` - integer - required

### `GET /public-api/v1/projects/list`

- Summary: List user projects
- Notes: Returns every project (app + country) belonging to the authenticated user. The `id` of each project is what every project-scoped endpoint (tracking, recommended-keywords, competitors) expects as `project_id`. **Costs:** 10 tokens per call.

## Recommended Keywords

### `GET /public-api/v1/recommended-keywords`

- Summary: List recommended keywords
- Notes: Returns the keywords we recommend you track for a project in the given country, surfaced from the project's app metadata, competitors' metadata, store suggestions, current rankings and related keywords. Each entry carries the phrase, the `sources` that proposed it and its current `state` (`recommended` — fresh suggestion, `tracked` — already in your tracking set, `declined` — you previously dismissed it via `/decline`). Filter by state or by source(s) to narrow the working set. The result is paginated — `pagination.total` reflects the filtered universe. **Costs:** `max(10, ceil(returned / 100))` tokens — minimum 10 per call, then 1 extra token for every started bucket of 100 keywords returned on the page.
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required
`page` - in `query` - integer
`per_page` - in `query` - integer
`filters[recommended_keyword_state][]` - in `query` - array<string> - maxItems=50
`filters[sources][]` - in `query` - array<string> - maxItems=50

### `POST /public-api/v1/recommended-keywords/decline`

- Summary: Decline recommended keywords
- Notes: Dismisses recommended keywords by their phrase so they stop appearing in the default `/recommended-keywords` listing. Declined keywords remain queryable via `filters[recommended_keyword_state][]=declined`. Reversible — see `/recommended-keywords/undecline`. **Costs:** 1 token per call regardless of how many phrases are listed.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keywords` required: array<string>

### `POST /public-api/v1/recommended-keywords/undecline`

- Summary: Undecline recommended keywords
- Notes: Reverses a previous decline — the listed phrases will surface as `recommended` again the next time their sources still propose them. **Costs:** 1 token per call regardless of how many phrases are listed.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keywords` required: array<string>

## Store Charts

### `GET /public-api/v1/store-charts`

- Summary: Store chart top-500
- Notes: Returns the top-500 chart positions for a (store, country, cluster, category, device) day-by-day across the requested range. Each day's `positions` are sorted ascending by rank; apps not yet indexed on our side are silently skipped. The window cannot exceed **1 week**. **Costs:** 10 tokens per day actually returned in `history` — you only pay for data we delivered. Minimum 10 tokens per call, so a misspelled cluster/category that yields no days still costs 10.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country` - in `query` - string - required
`cluster_key` - in `query` - string - required
`category_key` - in `query` - string - required
`device` - in `query` - string - required - enum: IPHONE, IPAD, MOBILE
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

## Subscription

### `GET /public-api/v1/subscription/limits`

- Summary: Get subscription limits
- Notes: Returns the plan limits of the authenticated user's current subscription — `max_keywords`, `max_apps`, `max_archived_apps` and `max_public_api_tokens` — each as a `total` (plan allowance) / `used` (currently consumed) pair. Team members see their team owner's plan. **Costs:** 1 token per call.

## Tracking Folders

### `GET /public-api/v1/tracking/folders`

- Summary: List folders
- Notes: Returns the keyword folders defined on a project — the groupings you can use to organise tracked keywords (e.g. by theme, campaign or language). **Costs:** 1 token per call.
- Parameters:

`project_id` - in `query` - integer - required

### `POST /public-api/v1/tracking/folders`

- Summary: Create folder
- Notes: Creates a new empty folder on a project. The returned folder id feeds the folder-keywords endpoints to populate it. **Costs:** 1 token per call.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `name` required: string
- `description`: string

### `DELETE /public-api/v1/tracking/folders/{folder}`

- Summary: Delete folder
- Notes: Deletes a folder. The keywords inside the folder remain tracked on the project — only the folder grouping is removed. Returns 404 if the folder doesn't belong to any project of the authenticated user. **Costs:** 1 token per call.
- Parameters:

`folder` - in `path` - integer - required

### `PATCH /public-api/v1/tracking/folders/{folder}`

- Summary: Update folder
- Notes: Renames a folder and/or updates its description. Omit a field to leave it unchanged. Returns 404 if the folder doesn't belong to any project of the authenticated user. **Costs:** 1 token per call.
- Parameters:

`folder` - in `path` - integer - required

- Request body:

- Content-Type: `application/json`
- `name`: string
- `description`: string

### `DELETE /public-api/v1/tracking/folders/{folder}/keywords`

- Summary: Remove keywords from folder
- Notes: Removes the given keywords (by phrase) from a folder. The keywords stay tracked on the project — only the folder membership is removed. Returns 404 if the project or folder doesn't belong to the authenticated user. **Costs:** 1 token per 100 keywords in the request, minimum 1 per call.
- Parameters:

`folder` - in `path` - integer - required

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `keywords` required: array<string>

### `POST /public-api/v1/tracking/folders/{folder}/keywords`

- Summary: Add keywords to folder
- Notes: Adds the given keywords (by phrase) to a folder on a project for the given country. Idempotent — keywords already in the folder are a no-op. Returns 404 if the project or folder doesn't belong to the authenticated user. **Costs:** 1 token per 100 keywords in the request, minimum 1 per call.
- Parameters:

`folder` - in `path` - integer - required

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keywords` required: array<string>

## Tracking Keywords

### `DELETE /public-api/v1/tracking/keywords`

- Summary: Delete tracked keywords
- Notes: Stops tracking the given keywords by their numeric `keyword_ids` (from `GET /v1/tracking/keywords`). Removed keywords stop counting against the plan's tracked-keyword limit and we stop collecting their positions going forward — historical positions remain queryable via `/v1/keywords/ranking` for as long as the date range covers them. **Costs:** 1 token per call regardless of how many keywords were removed.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keyword_ids` required: array<integer> — Sourced from `GET /v1/tracking/keywords`.

### `GET /public-api/v1/tracking/keywords`

- Summary: List tracked keywords
- Notes: Returns every keyword you currently track on a project for the given country, with each keyword's detected language and the folders it belongs to. Use it to enumerate the tracking set you're billing against, and to feed the `keyword_ids` parameter of the delete endpoint. **Costs:** 1 token per 100 returned keywords, minimum 1 per call.
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required

### `POST /public-api/v1/tracking/keywords`

- Summary: Add tracked keywords
- Notes: Starts tracking the given keywords on a project for the given country. Keywords already tracked are silently de-duplicated and not billed. Returns 403 if the request would push the project past the plan's tracked-keyword limit — nothing is added in that case. **Costs:** 5 tokens per *new* keyword actually added. A request consisting entirely of already-tracked keywords is free.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keywords` required: array<string>
