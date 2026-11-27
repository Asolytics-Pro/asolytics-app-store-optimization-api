# Asolytics Public API Endpoints

- Source docs: `https://app.asolytics.pro/api/public-api/documentation`
- Source OpenAPI: `https://app.asolytics.pro/api/public-api/docs?public-api-docs.json`
- Generated from spec version: `1.0.0-beta`
- Generated at: `2026-11-27T13:08:47.888326+00:00`

## Authentication

- Header: `X-PUBLIC-API-TOKEN`

## Analytics

### `GET /public-api/v1/analytics/app-store/time-series`

- Summary: App Store analytics time series
- Notes: App Store Connect analytics of the project's app by day, week or month — the data of the *App Store analytics* page of the dashboard, read through the project's App Store analytics connection (the connection of the project owner or of a team lead above them; a user the project is shared with reads through it too). When an incentive-traffic integration is connected, motivated installs are moved out of `Search` into a separate `Incentive` traffic source, as in the dashboard. The request and the answer have the same frame as `/v1/analytics/google-play/time-series`: `group_by`, `group_values[]`, `filters[<dimension>][]`, and `series: [{group: {key, title}, metrics: {<measure>: {total, type, points}}}]`. **What one request can ask** (App Store Connect's own limits — anything else is refused with 422 before the store is asked, nothing charged): - `measures[]` — one or two of `proceeds`, `sales`, `totalDownloads` (= `units` + `redownloads`), `redownloads`, `units` (first-time downloads), `pageViewCount`, `impressionsTotal`, `impressionsTotalUnique`. Apple refuses three or more with a breakdown; every series carries all the requested measures. - `group_by` (required) — `country`, `traffic_source`, `app_referrer` or `web_referrer`. - **Apple returns only the top 10 groups**, ranked by the first measure. Particular groups can be asked for only by country: `group_by=country` with `group_values[]` (ISO codes, up to 10 — ten named countries always come back in full); for more countries, split them into calls of 10. `group_values[]` with another `group_by` is a 422. - `filters[country][]` (up to 10 ISO codes, summed) and `filters[traffic_source][]` narrow the data; values of one filter are OR-ed, the two filters AND-ed. The `group_by` dimension cannot also be a filter (with `group_by=country` pick the countries with `group_values[]`). - `filters[traffic_source][]` does not combine with `group_by=app_referrer` / `web_referrer`: referrers exist only for referral traffic. **Traffic sources** (`group.key` with `group_by=traffic_source`, values of `filters[traffic_source][]`): `Search` (App Store search), `Other` (App Store browse), `AppRef` (app referrer), `WebRef` (web referrer), `EventNotification`, `Volume Purchase`, `Unknown`. The answer may carry more sources than Apple's — `Incentive`, and others added by integrations connected to the account (they cannot be filtered by); a moved amount is taken from the source it belongs to, so the sources still add up to Apple's total and none goes below zero. Country groups are keyed by ISO code. There is no `overall` series: App Store answers always come broken down. **History** reaches back as far as the plan allows (`store_analytics_max_deep`, 403 otherwise). The last one or two days may still be incomplete in App Store Connect. **Retries.** The store is read through shared connections and answers are cached for an hour. `429` with `reason: busy` — the connections serve other requests, retry after the `Retry-After` seconds; `503` `warming_up` — the store session is being signed in, retry in about a minute; `503` `unavailable` — the store or the session failed, retry later. Calls are also limited per minute per account (the team owner for members) — `429` with `Retry-After`; a call refused as invalid (422) before the store is asked does not count against the limit. `409` — the App Store analytics cannot be read for the project: `reason: not_connected` — it is not connected (`how_to_connect` says how), `reason: insufficient_permissions` — the access granted in App Store Connect lacks the permissions to read the analytics (`how_to_fix` says what to change; retrying does not help until it is fixed). **Costs:** 10 tokens per call that returns data — an empty answer and a cached one included. Validation errors, 403, 404, 409, 429 and 503 are free. At least 10 tokens on balance are required before the store is asked (402).
- Parameters:

`project_id` - in `query` - integer - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`frequency` - in `query` - string - enum: day, week, month
`measures[]` - in `query` - array<string> - required - maxItems=2
`group_by` - in `query` - string - required - enum: country, traffic_source, app_referrer, web_referrer
`group_values[]` - in `query` - array<string> - maxItems=10
`filters[country][]` - in `query` - array<string> - maxItems=10
`filters[traffic_source][]` - in `query` - array<string> - maxItems=7

### `GET /public-api/v1/analytics/google-play/dimension-values`

- Summary: Google Play analytics dimension values
- Notes: The values Play Console lists for the project's app in every analytics dimension, keyed by the dimension names of `group_by` / `filters[…]` — the keys to pass in `group_values[]` and `filters[<dimension>][]` of `/v1/analytics/google-play/time-series`. Each value comes with its title and the installers count Google ranks the list by; search terms are Google's top list only. The list is cached for a day. `409` — Google Play Console is not connected for the project (the body says how to connect it); `429` / `503`, retries and the per-minute limit — as in the time series. **Costs:** 1 token per call (a cached answer included). 404, 409, 429 and 503 are free.
- Parameters:

`project_id` - in `query` - integer - required

### `GET /public-api/v1/analytics/google-play/time-series`

- Summary: Google Play analytics: time series and table
- Notes: Play Console acquisition of the project's app — store listing visitors, installers and conversion rate, the data of the *Google Play analytics* page of the dashboard, read through the project's Play Console connection (the connection of the project owner or of a team lead above them; a user the project is shared with reads through it too). The request and the `series` have the same frame as `/v1/analytics/app-store/time-series`. One call returns both parts of the page: - `series` — the **daily** series of the overall (`group.key` = `overall`) and of the requested `group_values[]` only, all three metrics each; - `table` — totals of the range over **every** value of the `group_by` dimension Google reports (not only `group_values[]`), each with the value of the previous period of the same length and the change. Start with no `group_values[]` to see in `table` which values carry data, then ask for their series. **What one request can ask:** - `group_by` — the breakdown dimension (default `country`): `country`, `traffic_source`, `search_term`, `store_listing`, `language`, `install_state`, `utm_source`, `utm_campaign`, `custom_audience`. - `group_values[]` — up to 50 values of the `group_by` dimension to draw a series for (countries as ISO codes). - `filters[<dimension>][]` (same dimension names, up to 50 values each) narrow both parts — values of one dimension are OR-ed, dimensions AND-ed. The `group_by` dimension cannot also be a filter (422) — pick its values with `group_values[]`. - Values come from `/v1/analytics/google-play/dimension-values` (or the `table` keys); a value Google does not list for the app is refused with 422 before the data is asked for (free). Search terms are Google's top list only. **History:** Play Console keeps about the **last 90 days**: a `date_from` earlier than 90 days before today (UTC) is refused with 422 (free), the message names the earliest allowed date. Also capped by the plan's store analytics history (`store_analytics_max_deep`, 403 with `earliest_date`). **Retries.** The store is read through shared connections and answers are cached for an hour. `429` with `reason: busy` — retry after the `Retry-After` seconds; `503` `unavailable` — the store or the session failed, retry later. Calls are also limited per minute per account (the team owner for members) — `429` with `Retry-After`; a call refused as invalid (422) before the store is asked does not count against the limit. `409` — Google Play Console is not connected for the project (the body says how to connect it). **Costs:** 10 tokens per call that returns data (series and table together) — an empty answer and a cached one included. Validation errors, 403, 404, 409, 429 and 503 are free. At least 10 tokens on balance are required before the store is asked (402).
- Parameters:

`project_id` - in `query` - integer - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`group_by` - in `query` - string - enum: country, traffic_source, search_term, store_listing, language, install_state, utm_source, utm_campaign, custom_audience
`group_values[]` - in `query` - array<string> - maxItems=50
`filters[country][]` - in `query` - array<string> - maxItems=50
`filters[traffic_source][]` - in `query` - array<string> - maxItems=50
`filters[search_term][]` - in `query` - array<string> - maxItems=50
`filters[store_listing][]` - in `query` - array<string> - maxItems=50
`filters[language][]` - in `query` - array<string> - maxItems=50
`filters[install_state][]` - in `query` - array<string> - maxItems=50
`filters[utm_source][]` - in `query` - array<string> - maxItems=50
`filters[utm_campaign][]` - in `query` - array<string> - maxItems=50
`filters[custom_audience][]` - in `query` - array<string> - maxItems=50

## Applications

### `GET /public-api/v1/applications/availability`

- Summary: Applications availability
- Notes: Returns the list of countries in which each of the given apps is currently live in the store. Apps available nowhere (taken down, not yet released, region-blocked everywhere we check) are omitted from the response entirely. **Costs:** 10 tokens per app present in the response. A request whose apps are all unavailable returns an empty list and is free.
- Parameters:

`origin_ids[]` - in `query` - array<string> - required - maxItems=10

### `GET /public-api/v1/applications/info`

- Summary: Application info
- Notes: Returns the app card: icon, rating and number of ratings, developer (name, site), app site, privacy policy URL, store categories, release and last update dates, last version, size (App Store only), average days between releases, age in days, in-app purchase price range in USD and when its metadata last changed. Pass `country_code` to also get the rating, number of ratings and whether the app is live in that country (`country` block); for the list of all countries where the app is live use `/v1/applications/availability`. Without it `rating` is the mean of the latest per-country ratings and `votes_count` their sum. Ratings come from scans of the last month only: an app not scanned for a month has `rating: null`. For the rating over time use `/v1/applications/ratings`; for installs and revenue, `/v1/applications/installs` and `/v1/applications/revenue`; for the title/subtitle/description text, `/v1/applications/metadata`. The app's price and age rating are not provided. Returns 404 if the `origin_id` doesn't resolve to a known application; 422 for a `country_code` the app's store does not have. **Costs:** 15 tokens per call without `country_code`, 20 tokens with it.
- Parameters:

`origin_id` - in `query` - string - required
`country_code` - in `query` - string

### `GET /public-api/v1/applications/installs`

- Summary: Application installs history
- Notes: Returns monthly **estimated** installs for a single application across every country we currently track (or only the `country_codes[]` you pass), for each month in the requested range. Values are estimates derived from store signals — not measured installs — and are emitted as `null` for months we couldn't estimate (sparsely-tracked apps, or the most recent month while it's still being computed). Returns 404 if the `origin_id` doesn't resolve to a known application. **Costs:** 10 tokens per emitted (country, month) pair carrying a non-null value (`0` counts; `null` does not). Minimum 10 tokens per call — charged even if the entire grid is null.
- Parameters:

`origin_id` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`country_codes[]` - in `query` - array<string> - maxItems=50

### `GET /public-api/v1/applications/metadata`

- Summary: Applications metadata
- Notes: Returns the latest text metadata (title, sub_title, description) of the given apps in the requested locales — the same text the store currently shows on each app's listing page. Only locales that actually carry data are emitted; `origin_id`s we don't have indexed are silently absent. **Costs:** 5 tokens per returned (app, locale) pair. A request that returns no pairs is free.
- Parameters:

`origin_ids[]` - in `query` - array<string> - required - maxItems=10
`locales[]` - in `query` - array<string> - required - maxItems=10

### `GET /public-api/v1/applications/metadata/media`

- Summary: Applications media
- Notes: Returns the latest screenshots and preview videos of the given apps in the requested locales — the same media the store currently shows on each app's listing page. Each screenshot carries its `device` and 0-based `position` so you can reconstruct the gallery order. Only locales that actually carry media are emitted; `origin_id`s we don't have indexed are silently absent. **Costs:** 5 tokens per returned (app, locale) pair. A request that returns no pairs is free.
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
- Notes: Returns the app's **latest known** ranking position for each of the requested keywords in the given store/country. Because keywords are parsed on independent schedules, each keyword carries its own `date` — they will not always share the same parse day. Keywords the app does not currently rank for are omitted from the response. The store (Google Play / App Store) is inferred from the `origin_id`. **Costs:** 3 tokens per started bucket of 30 requested keywords, minimum 15 per call (billed on the request, not the number of rows returned).
- Parameters:

`origin_id` - in `query` - string - required
`country_code` - in `query` - string - required
`keywords[]` - in `query` - array<string> - required - maxItems=1000

### `GET /public-api/v1/applications/ratings`

- Summary: Application ratings history
- Notes: Returns the app's average rating and total number of ratings day by day in each requested country, as the store showed them on the days we scanned the app. Both are the store's running values (the number of ratings is a total, not the day's new ratings). History goes back about 6 months (`date_from` no earlier than the 1st of the current month − 6 months), at most 90 days per call. Days we did not scan are absent — the history can have gaps; a country with no scans in the window (or one the app's store does not have) comes back with an empty `history`. Returns 404 if the `origin_id` doesn't resolve to a known application. For the latest rating alone use `/v1/applications/info`. **Costs:** 3 tokens per returned (day, country) pair. A request that returns no days is free.
- Parameters:

`origin_id` - in `query` - string - required
`country_codes[]` - in `query` - array<string> - required - maxItems=10
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/applications/revenue`

- Summary: Application revenue history
- Notes: Returns monthly **estimated** revenue (USD) for a single application across every country we currently track (or only the `country_codes[]` you pass), for each month in the requested range. Values are estimates derived from store signals — not measured revenue — and are emitted as `null` for months we couldn't estimate (sparsely-tracked apps, or the most recent month while it's still being computed). Returns 404 if the `origin_id` doesn't resolve to a known application. **Costs:** 10 tokens per emitted (country, month) pair carrying a non-null value (`0` counts; `null` does not). Minimum 10 tokens per call — charged even if the entire grid is null.
- Parameters:

`origin_id` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`country_codes[]` - in `query` - array<string> - maxItems=50

### `GET /public-api/v1/applications/timeline`

- Summary: Application update timeline
- Notes: Returns what changed in an app's store listing, day by day (the Update Timeline): title, subtitle, description, screenshots, icon, version, size and preview videos. Each day lists one **fact** per changed type; a fact's `changes` group the locales that changed from the same state to the same state, each with `before` (the previous state and the day it was first seen) and `after`. Only days with changes are listed, newest first. History goes back about 6 months (`date_from` no earlier than the 1st of the current month − 6 months), at most 90 days per call. Use `types[]` and `locales[]` to fetch only what you need — they also make the call cheaper. `size` exists on the App Store only and comes with a release: a release that kept the size is not a size change. Screenshots and videos are compared per device, so only the changed devices are shown. `before` is null when a locale or a device appears for the first time. Returns 404 if the `origin_id` doesn't resolve to a known application. **Costs:** 1 token per returned fact — a (date, type) pair with a change: a title updated in many locales on one day is 1 fact, a title and screenshots changed on the same day are 2. A request with no changes is free.
- Parameters:

`origin_id` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required
`types[]` - in `query` - array<string> - maxItems=8
`locales[]` - in `query` - array<string> - maxItems=10

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

### `GET /public-api/v1/competitors/finder`

- Summary: Find competitor candidates
- Notes: Suggests apps that compete with the project app in a store country — the same search as the *Competitors Finder* of the dashboard. Candidates are drawn from the store tops of the project's tracked keywords and of its recommended keywords, from related and similar apps, and come ordered by relevance (apps with at least 300 ratings in the country first). Each candidate is `{origin_id, title, subtitle}`; why an app was suggested is not returned. Apps already marked in the project (`competitor`, `non_competitor` or `indirect_competitor`, see `/v1/competitors`) and the project app itself are never suggested — after marking candidates with `/v1/competitors/mark` (it takes up to 100 `competitor_origin_ids`) the next call shows the rest. For more about a candidate use `/v1/applications/metadata`. **Slow first call:** the search reads the project's recommended keywords for the country; if they were never computed for this project and country, this call computes them first, which can take **several minutes** (later calls are fast). Expect a long response on the first call for a new country, and retry rather than call in parallel. **Costs:** 20 tokens per call, charged after the result is built; requires at least 20 tokens on balance before the search starts (otherwise 402, nothing computed).
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required
`limit` - in `query` - integer

### `POST /public-api/v1/competitors/mark`

- Summary: Mark competitors
- Notes: Marks apps (by their store `origin_id`) as `competitor`, `non_competitor` or `indirect_competitor` for the project. Pass **either** `competitor_origin_id` (one app) **or** `competitor_origin_ids` (up to 100 apps in one call), not both. Idempotent — re-marking with the same state is a no-op; re-marking with a different state moves the app to that state. The response lists what happened to every requested app: `processed` — marked; `not_found` — no app is known for that `origin_id` (take ids from `/v1/competitors/finder` or `/v1/live-search`); `skipped` — the app belongs to the other store than the project's (a competitor must be in the project's store). With the single `competitor_origin_id` an unknown app is a 404 instead, as before. **Plan limits:** marking spends the project's per-plan allowance — direct and indirect competitors share `max_competitors_project`, non-competitors have `max_not_competitors_project`. Only apps not yet counted there spend it (re-marking, or moving an app between direct and indirect, is free). If the call would go over the allowance it answers 403 with the limit key, and **nothing** is marked or charged. Check the room left beforehand with `/v1/subscription/limits?project_id=…`. **Costs:** 1 token per app in the request — **every** requested app is billed, including those reported as `not_found` or `skipped` (an `origin_id` repeated in the list counts once); a single `competitor_origin_id` costs 1. Charged before marking; a single-app call answered with 404 is free.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `competitor_origin_id`: string — Store origin id of one competitor app — App Store: numeric track id; Google Play: bundle id. Required unless `competitor_origin_ids` is given; not allowed together with it.
- `competitor_origin_ids`: array<string> — Store origin ids of up to 100 apps to mark in one call (duplicates collapsed). Required unless `competitor_origin_id` is given; not allowed together with it.
- `state` required: string (competitor, non_competitor, indirect_competitor)

### `POST /public-api/v1/competitors/unmark`

- Summary: Unmark competitors
- Notes: Removes any competitor mark of the given apps (by their store `origin_id`) within the project — the apps drop out of the competitors list entirely and free their slots of the plan allowance. Pass **either** `competitor_origin_id` (one app) **or** `competitor_origin_ids` (up to 100 apps in one call), not both. Unmarking an app that has no mark is a no-op. The response lists what happened to every requested app: `processed` — unmarked; `not_found` — no app is known for that `origin_id`; `skipped` — the app belongs to the other store than the project's (it can't be marked in this project in the first place). With the single `competitor_origin_id` an unknown app is a 404 instead, as before. **Costs:** 1 token per app in the request — **every** requested app is billed, including those reported as `not_found` or `skipped` (an `origin_id` repeated in the list counts once); a single `competitor_origin_id` costs 1. Charged before unmarking; a single-app call answered with 404 is free.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `competitor_origin_id`: string — Store origin id of one competitor app — App Store: numeric track id; Google Play: bundle id. Required unless `competitor_origin_ids` is given; not allowed together with it.
- `competitor_origin_ids`: array<string> — Store origin ids of up to 100 apps to unmark in one call (duplicates collapsed). Required unless `competitor_origin_id` is given; not allowed together with it.

## Keywords

### `GET /public-api/v1/keywords/metrics`

- Summary: Keywords latest metrics
- Notes: Returns a snapshot of one or more latest metrics for up to 250 keywords in a (store, country). Each keyword in the response appears exactly once in the same order and casing as the request; duplicate keywords are deduplicated. Only the requested metrics are present on each keyword object. Metrics that resolve to null (no scan data available) are omitted from the billed pairs but still appear in the response as null. **Metric availability by store:** - `popularity` — App Store only (raw scan); Google Play omits the `popularity` field, only `mlp_popularity` is returned. - `max_popularity` — App Store: `year_max_popularity` (raw) and `synthetic_year_max_popularity` (mlp). Google Play: `mlp_max_popularity` only (`all_time_max_popularity`). - `impressions` — App Store: estimated daily impressions derived from both real and synthetic popularity. Google Play: `mlp_impressions` only. - `difficulty` — both stores, single value (no real/mlp split). - `language` — both stores, country-independent, single value. **Costs:** per (keyword, metric) pair where the resolved value is non-null — 5 tokens for `popularity` and `max_popularity`, 1 token for `impressions`, `difficulty` and `language`; minimum 1 token per call.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=250
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`metrics[]` - in `query` - array<string> - required - maxItems=50

### `GET /public-api/v1/keywords/popularity`

- Summary: Keywords popularity history
- Notes: Returns per-keyword popularity history for a (store, country) across the requested date range. For App Store each date carries both `popularity` (raw scan) and `mlp_popularity` (the ML-derived synthetic value that smooths over scan gaps); for Google Play only `mlp_popularity` is returned because GP stores a single popularity column. Only dates with real scans are emitted — no gap-filling, no interpolation. Up to 1000 keywords per request; `date_from` cannot reach further back than the start of (current month − 6 months). **Costs:** 2 tokens per (keyword, date) pair returned, minimum 5 tokens per keyword that has any history. Keywords with no scans in range are free, so is a request with no scans at all.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=1000
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/keywords/ranking`

- Summary: Keywords ranking history
- Notes: Returns the top-50 ranking history per keyword for a (store, country) across the requested date range. For each date we emit the apps in their store-shown order with `origin_id` and current title. Dates without a scan are skipped — no gap-filling; apps we couldn't resolve to a known origin are dropped from the positions list. Up to 500 keywords per request; `date_from` cannot reach further back than the start of (current month − 6 months). **Costs:** 2 tokens per (keyword, date) pair returned. A request with no scans in range is free.
- Parameters:

`keywords[]` - in `query` - array<string> - required - maxItems=500
`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`country_code` - in `query` - string - required
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `POST /public-api/v1/keywords/ranking/force-recheck`

- Summary: Force a keyword ranking re-check
- Notes: Orders an on-demand re-scan of the store top for the given phrases in a (store, country). The call returns as soon as the re-check is queued — the fresh positions land in our storage a few minutes later and can be read through `/v1/keywords/ranking` or `/v1/applications/ranking`. Supply `webhook.url` to be notified: we POST one message per phrase as soon as its scan is done. Up to 500 phrases per request; duplicates (case-insensitive) are collapsed and billed once. **Webhook payload:** `{request: {id}, task: {keyword, country_code, store}, result: {status}}` where `request.id` is the `request.id` of this response. With `webhook.include_positions = true` the result also carries `positions` — the scanned top as `[{position, item: {origin_id}}, …]`, capped at 50 entries; an empty array means the scan found nothing. We ignore the response body and only look at the status code: a non-200 is retried twice with a growing delay, then dropped. Redirects are not followed and the request times out after a few seconds. The callback host must resolve to a public address — private, loopback and link-local targets are rejected and the notice is dropped without retries. **Costs:** 15 tokens per unique phrase, **+1** with a webhook, **+1** more with `include_positions` — so 15 / 16 / 17 per phrase, charged when the re-check is queued (not when it completes).

- Request body:

- Content-Type: `application/json`
- `keywords` required: array<string> — Phrases to re-check (max 500, each ≤80 chars).
- `store` required: string (APP_STORE, GOOGLE_PLAY)
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `webhook`: object — When present, a POST is sent per completed phrase.

### `GET /public-api/v1/keywords/suggestions/history`

- Summary: Keyword search suggestions history
- Notes: Returns, for one phrase in up to 10 countries of a store, the search suggestions (autocomplete) the store showed for it day by day, with their positions. Only data we have already collected is returned — no new scan is ordered. A day on which the phrase was not scanned is omitted; a day on which it was scanned but the store suggested nothing comes back with an empty `suggestions` list. Countries come back in request order (duplicates collapsed); a country with no scans in the range, or one the store doesn't serve, comes back with an empty `history`. The phrase is matched case-insensitively and echoed as requested. `date_from` cannot reach further back than the start of (current month − 6 months), `date_to` cannot be in the future, and the range may cover at most 90 days (both ends included). **Costs:** 1 token per (country, day) pair in the response, scanned-but-empty days included; minimum 1 token per call.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`keyword` - in `query` - string - required
`country_codes[]` - in `query` - array<string> - required - maxItems=10
`date_from` - in `query` - string - required
`date_to` - in `query` - string - required

### `GET /public-api/v1/keywords/suggestions/live`

- Summary: Keyword search suggestions now
- Notes: Returns, for one phrase in up to 10 countries of a store, the search suggestions (autocomplete) the store shows for it **now**, with their positions — asked from the store at request time, unlike `/v1/keywords/suggestions/history`, which only returns what we collected on past days. A non-empty answer is cached for up to an hour per (phrase, country), so a repeated call within the hour returns the same list; an empty one is not cached. Countries come back in request order (duplicates collapsed); a country for which the store suggests nothing comes back with an empty `suggestions` list — the same happens when the store could not be asked, so retry later before concluding a phrase has no suggestions. The phrase is matched case-insensitively and echoed as requested. Every country must exist in the store (else 422). Suggestions carry no metrics — get popularity and the like with `/v1/keywords/metrics`. Requires a plan with keyword suggestions. **Costs:** 10 tokens per call that returns at least one suggestion (in any country), charged after the result is built. A call where every country comes back empty is free.
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`keyword` - in `query` - string - required
`country_codes[]` - in `query` - array<string> - required - maxItems=10

## Live Search

### `GET /public-api/v1/live-search`

- Summary: Live search top 50
- Notes: Returns the live (real-time) top-50 search results for a keyword in the given (store, country, device) — what a user would currently see on the store's search results page, including paid ad placements alongside organic items. On App Store each item carries its `type` (`apps`, `preorder`, `app-bundles`, `developers`, `editorial-items`, `in-apps`, `subscription`); Google Play returns apps only. `is_paid` marks ad placements and `position` is the 1-based rank in the full list with paid items counted. Items we couldn't resolve to a known origin are silently dropped. **Costs:** 20 tokens per call that returns at least one item; 5 tokens per call that returns an empty list (empty isn't necessarily an error — the keyword may simply have no live matches).
- Parameters:

`store` - in `query` - string - required - enum: APP_STORE, GOOGLE_PLAY
`keyword` - in `query` - string - required
`country_code` - in `query` - string - required
`device` - in `query` - string - required - enum: IPHONE, IPAD, MOBILE

## Metadata Keywords

### `GET /public-api/v1/metadata-keywords`

- Summary: List metadata keywords
- Notes: Returns the keywords found in the metadata of the project app and of its competitors in a country, and whose metadata each one comes from — the *metadata keywords* of the dashboard. Use it to see which keywords the project already covers and which ones competitors use and it doesn't. Each entry is `{keyword, source, competitor_origin_ids}`: `source` lists `app` (the project app has it) and/or `competitor` (at least one competitor has it), `competitor_origin_ids` names those competitors. What is read: the latest **title and subtitle** (Google Play: short description) of the apps in every locale of the country's store front — not descriptions or in-app texts; competitors are the apps marked `competitor` in the project (`/v1/competitors`), not indirect or non-competitors. Only keywords with popularity above 5 in the country are kept. Keywords carry no metrics — get popularity, ranking etc. with `/v1/keywords/metrics` / `/v1/keywords/ranking`. Ordered by popularity in the country, most popular first; paginated. **Costs:** 1 token per started 10 keywords on the returned page (`ceil(returned / 10)`), minimum 1 token per call.
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required
`page` - in `query` - integer
`per_page` - in `query` - integer

## Projects

### `POST /public-api/v1/projects`

- Summary: Create a project
- Notes: Adds an app to the caller's projects, exactly like adding an app in the dashboard. The app is addressed by its store `origin_id` (App Store numeric id or Google Play package name); the store is taken from the app. The app must already be known to Asolytics: if it is not (404), find it first with `/v1/live-search` — every app a live search returns is saved, and then this call succeeds. `country_code` is the country the project starts in (it gets the first warm-up); it must be in `/v1/common-catalogs/countries` of the app's store, otherwise 422 before anything is billed. What happens on success: the project uses one slot of the plan's `max_apps` limit (counted for the whole team, see `/v1/subscription/limits`), then — asynchronously, in the background — tracking/ranking/metadata/recommended keywords are warmed up for every country of the store, the ASO Score is calculated, and the owner is subscribed to the weekly e-mail report for `country_code`. Data appears over the next minutes; the new project is immediately visible in `/v1/projects/list`. One project per app per user: if the caller already has this app (also when it is archived) the answer is 409 with the existing `project_id` and `is_archived` — nothing is billed. An archived project cannot be restored through the API, only in the dashboard. At most 15 successful creations per hour per account (a team shares the owner's allowance); over it — 429 with `Retry-After`. **Costs:** 10 tokens per created project, billed before the project is created. Rejected calls (validation, 403, 404, 409, 429, 503) are free.

- Request body:

- Content-Type: `application/json`
- `origin_id` required: string — Store id of the app (`origin_id` from `/v1/live-search` or `app_info.origin_id` elsewhere).
- `country_code` required: string — Starting country, from `/v1/common-catalogs/countries` for the app's store.

### `POST /public-api/v1/projects/archive`

- Summary: Archive a project
- Notes: Archives a project, exactly like the dashboard's *Archive* action. Owner only: the caller must have `access.level = owner` in `/v1/projects/list` (403 otherwise). An archived project stays in `/v1/projects/list` with `is_archived: true` and keeps its data, but it no longer takes a `max_apps` slot — it takes a `max_archived_apps` slot instead (403 `PublicApiProjectLimitExceededSchema` when the plan has that limit and it is full, see `/v1/subscription/limits`). **There is no unarchive in the public API** — an archived project can be brought back only by the user in the dashboard. Ask the user before archiving. Archiving an already archived project changes nothing and answers 200 with `already_archived: true`. **Costs:** 1 token per call, billed before the project is archived (also for an already archived project). Rejected calls (403, 404) are free.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.

### `GET /public-api/v1/projects/competitors-in-top`

- Summary: Get project competitors in the top of keywords
- Notes: For every requested keyword, returns which of the project's marked apps — competitors, indirect competitors and non-competitors — are in the store top of the given country and at which positions. This is the data behind the *Competitors in top 10* column of the internal reports, for an arbitrary list of keywords. Competitor marks belong to the project and do not depend on `country_code`, which only selects the store top. Without `date` each keyword uses its own latest top scan, so `date` may differ between keywords. With `date` only scans of that day are used. A keyword without a scan (on the requested day or at all) comes back with `date: null` and empty groups. Apps outside `top_size` and apps not marked in the project are not returned. Keywords differing only in case are merged into the first one. **Costs:** 1 token per unique requested keyword, minimum 10 tokens per call. Billed on the request, whether or not a keyword has top data.
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required
`keywords[]` - in `query` - array<string> - required - maxItems=500
`date` - in `query` - string
`top_size` - in `query` - integer

### `GET /public-api/v1/projects/countries-keywords-counts`

- Summary: Get per-country keyword counters
- Notes: Returns, for every store country of the project, the tracked / recommended / ranking keyword counters together with their day-over-day `dynamic`. The result is keyed by 2-letter country code. **Note:** these counters are pre-aggregated and reflect the **previous day's** snapshot, so they may lag the real data by up to a day. For exact, up-to-the-moment values use the list endpoints directly (e.g. `/v1/tracking/keywords`, `/v1/recommended-keywords`, `/v1/applications/ranking`). **Costs:** 20 tokens per call.
- Parameters:

`project_id` - in `query` - integer - required

### `GET /public-api/v1/projects/list`

- Summary: List user projects
- Notes: Returns every project (app + country) the authenticated user can access: projects they own, projects shared with them, and — for enterprise team leads/owners — projects owned by members below them in the team. Each project carries an `access` block with the project `owner`'s email and the caller's `level` (`read`/`edit`/`owner`). The `id` of each project is what every project-scoped endpoint (tracking, recommended-keywords, competitors, analytics) expects as `project_id`. `integrations` tells whether the project's store analytics will answer — `connected` / `pending` / `error` (with `error_reason`) / `not_connected` per integration — so a client can skip the analytics calls that would answer 409, and show what to connect. **Costs:** 10 tokens per call.

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

### `DELETE /public-api/v1/recommended-keywords/autoapprove-settings`

- Summary: Stop recommended keywords auto-approve
- Notes: Turns auto-approve off for the project in **all** countries by deleting its settings — the same as *Stop auto-approve* in the dashboard. Keywords auto-approve has already added stay in tracking (remove them with `DELETE /v1/tracking/keywords` if needed). The settings are not kept: to turn auto-approve back on, send the full set again with `PUT`; to stop only some countries, `PUT` the set without them instead. Deleting when auto-approve is already off is a no-op success. Requires EDIT access. **Costs:** 10 tokens per call, billed before deleting. Rejected calls (403, 404) are free.
- Parameters:

`project_id` - in `query` - integer - required

### `GET /public-api/v1/recommended-keywords/autoapprove-settings`

- Summary: Get recommended keywords auto-approve settings
- Notes: Returns the project's auto-approve settings — the rules by which recommended keywords (see `/v1/recommended-keywords`) are added to tracking automatically, the same settings as *Auto-approve* in the dashboard. `enabled: false` means auto-approve is off. The shape is exactly what `PUT` accepts: to change one country or one filter, read the settings here, edit them and send the whole set back with `PUT`. How it works: in every country of `country_codes`, each time the project's recommended keywords are recalculated (regular warm-ups, and right after every `PUT`), the recommended keywords that match the country's filters — the country's entry in `specific` if there is one, otherwise the common `filters` — and are not tracked yet and not declined are added to tracking. Requires EDIT access to the project. **Costs:** 1 token per call.
- Parameters:

`project_id` - in `query` - integer - required

### `PUT /public-api/v1/recommended-keywords/autoapprove-settings`

- Summary: Save recommended keywords auto-approve settings
- Notes: Turns on (or changes) auto-approve of recommended keywords for the project — the same as saving *Auto-approve* in the dashboard. **Full replacement:** the body becomes the project's only settings; countries and filters not in the body are dropped. To add a country or change one filter, first read the current settings with `GET /v1/recommended-keywords/autoapprove-settings`, edit them and send the whole set here. Body: `country_codes` — the countries auto-approve runs in (from `/v1/common-catalogs/countries` of the project's store, otherwise 422); `filters` — the criteria for those countries, all set ones must match: ranges `{from, to}` (inclusive) `range_sap` (current popularity), `range_max_sap` (year-max popularity), `range_impression` (estimated daily impressions), `range_difficulty`, `range_rank` (the project app's position; unranked keywords never match), `range_top_competitors` (marked competitors in the top 10, `includeIndirect` to count indirect ones too), `range_top_non_competitors`; lists `{list: […]}` `sources` (`import`, `meta`, `related`, `competitors`, `rankings`, `suggestions`) and `language` (e.g. `English`). The example sets every criterion to show the shape — a typical rule uses two or three; `specific` — optional per-country overrides, each country must be in `country_codes`, and such a country uses only its own filters. Every country must end up with at least one criterion. **Effect:** every save recalculates the project's recommended keywords in every listed country and adds the matching ones — not tracked yet and not declined — to tracking, in the background (minutes for a large country). After that it keeps running on every regular recalculation until stopped with `DELETE`. Added keywords use the plan's `max_keywords` limit (when it is full nothing more is added); auto-approve stops adding in a country once it has 10 000 tracked keywords. Requires EDIT access. At most 10 successful saves per hour per project; over it — 429 with `Retry-After`. **Costs:** 10 tokens per save, billed before saving. Rejected calls (validation, 403, 404, 429) are free; keywords added to tracking by auto-approve are not billed.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_codes` required: array<string> — Countries to auto-approve in, from `/v1/common-catalogs/countries` for the project's store.
- `filters` required: PublicApiAutoapproveFiltersSchema
- `specific`: array<object> — Optional per-country overrides; a listed country uses only these filters.

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
- Notes: Returns the plan limits of the authenticated user's current subscription — `max_keywords`, `max_apps`, `max_archived_apps` and `max_public_api_tokens` — each as a `total` (allowance: the plan's limit plus the add-on packages bought on top of it) / `used` (currently consumed) pair. Team members see their team owner's plan and add-ons. Pass `project_id` to also get the per-project competitor allowances of that project — `max_competitors_project` (direct and indirect competitors share it) and `max_not_competitors_project` (non-competitors) — counted exactly as `/v1/competitors/mark` checks them, so you can see the room left before marking. Plans without per-project competitor limits do not report them. Without `project_id` they are absent. **Costs:** 1 token per call.
- Parameters:

`project_id` - in `query` - integer

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
- Notes: Renames a folder, updates its description and/or its cross-country setting. Omit a field to leave it unchanged. With `settings.cross_country = true` the folder spans every country of the project — a keyword added to it in one country is reported as belonging to the folder in all of them; with `false` the folder membership is country-scoped. New folders are cross-country by default. Returns 404 if the folder doesn't belong to any project of the authenticated user. **Costs:** 1 token per call.
- Parameters:

`folder` - in `path` - integer - required

- Request body:

- Content-Type: `application/json`
- `name`: string
- `description`: string
- `settings`: object

### `DELETE /public-api/v1/tracking/folders/{folder}/keywords`

- Summary: Remove keywords from folder
- Notes: Removes the given keywords (by phrase) from a folder. The keywords stay tracked on the project — only the folder membership is removed. Returns 404 if the project or folder doesn't belong to the authenticated user. **`country_code` is optional.** Omit it and the keyword leaves the folder entirely — in every country, exactly as it behaves for a cross-country folder (`settings.cross_country = true`). Pass it and a country-scoped folder (`settings.cross_country = false`) loses the membership of that country only, keeping the keyword in the folder in its other countries. For a cross-country folder the parameter changes nothing: such a folder holds a single membership shared by all countries, so removing it always removes it everywhere. **Costs:** 1 token per 100 keywords in the request, minimum 1 per call.
- Parameters:

`folder` - in `path` - integer - required

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code`: string — Optional. Sourced from `/v1/common-catalogs/countries`. Omit it to remove the keyword from the folder in every country; pass it to remove only this country's membership of a country-scoped folder. Ignored for cross-country folders.
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
- Notes: Returns every keyword you currently track on a project for the given country, with each keyword's detected language and the folders it belongs to. A cross-country folder (`settings.cross_country = true`, see `GET /v1/tracking/folders`) is reported for the keyword in every country it is tracked in, no matter which country it was added to the folder from; a country-scoped folder only in its own country. Dropping a keyword from tracking in one country only takes it out of country-scoped folders of that country — in the remaining countries it stays in its folders. Use the endpoint to enumerate the tracking set you're billing against, and to feed the `keyword_ids` parameter of the delete endpoint. **Costs:** 1 token per 100 returned keywords, minimum 1 per call.
- Parameters:

`project_id` - in `query` - integer - required
`country_code` - in `query` - string - required
`filters[folder_ids][]` - in `query` - array<integer> - maxItems=100
`filters[deduplicate_modificators]` - in `query` - boolean

### `POST /public-api/v1/tracking/keywords`

- Summary: Add tracked keywords
- Notes: Starts tracking the given keywords on a project for the given country. Keywords already tracked are silently de-duplicated and not billed. Returns 403 if the request would push the project past the plan's tracked-keyword limit — nothing is added in that case. **Costs:** 5 tokens per *new* keyword actually added. A request consisting entirely of already-tracked keywords is free.

- Request body:

- Content-Type: `application/json`
- `project_id` required: integer — Sourced from `/v1/projects/list`.
- `country_code` required: string — Sourced from `/v1/common-catalogs/countries`.
- `keywords` required: array<string>
