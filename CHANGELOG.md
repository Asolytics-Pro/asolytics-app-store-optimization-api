# Changelog

All notable changes to the `asolytics-api` skill. Versions here are **skill** versions (`skills/asolytics-api/VERSION`), not API versions — the Asolytics Public API itself is now `1.0.0-beta`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] — 2026-11-27

Synced against the API docs as of 2026-11-27 (API `1.0.0-alpha` → `1.0.0-beta`).

### Added

- **Store analytics** (needs a connected store account; `409` otherwise):
  - `GET /v1/analytics/app-store/time-series` — App Store Connect impressions, product page views, downloads (first-time and redownloads), proceeds; by day, week or month; by country, source type, referring app or website. 10 tokens per call with data.
  - `GET /v1/analytics/google-play/time-series` — Play Console store listing visitors, installers, conversion; daily series plus a period-over-period table in one call; by country, source, search term, listing, language, UTM. 10 tokens per call with data.
  - `GET /v1/analytics/google-play/dimension-values` — valid Google Play breakdown and filter values. 1 token.
- `GET /v1/applications/timeline` — day-by-day listing change history (texts, screenshots, icon, version, size, video). 1 token per (date, type) fact.
- `GET /v1/applications/info` — app summary; with `country_code` also the rating and availability there. 15 / 20 tokens.
- `GET /v1/applications/ratings` — rating and ratings count by day and country. 3 tokens per (day, country).
- `GET /v1/competitors/finder` — competitor candidates, as in the dashboard. 20 tokens.
- `GET /v1/projects/competitors-in-top` — which marked apps are in the store top for given keywords, and at which positions. 1 token per unique keyword, min 10.
- `GET /v1/keywords/suggestions/live` — store search suggestions right now. 10 tokens if any suggestion comes back.
- `GET /v1/keywords/suggestions/history` — collected search suggestions by day, up to 10 countries. 1 token per (country, day).
- `GET /v1/metadata-keywords` — keywords from the metadata of the project app and its competitors. 1 token per started 10 returned.
- `GET` / `PUT` / `DELETE /v1/recommended-keywords/autoapprove-settings` — read, save and stop auto-approve of recommended keywords. 1 / 10 / 10 tokens.
- `POST /v1/projects` — add an app to projects (10 tokens); `POST /v1/projects/archive` — archive a project (1 token).

### Changed

- `POST /v1/competitors/mark` and `/unmark` accept `competitor_origin_ids` (up to 100) as an alternative to one `competitor_origin_id`; every requested app is billed 1 token, including `not_found` / `skipped`.
- `GET /v1/applications/installs` and `/revenue` take `country_codes[]`.
- `GET /v1/projects/list` returns `is_archived` and `integrations` (`app_store_analytics` / `google_play_analytics` / `incentive_traffic`: `connected` / `pending` / `error` with `error_reason` / `not_connected`).
- `GET /v1/subscription/limits` with `project_id` also returns the project's competitor limits.
- `POST /v1/tracking/folders` and `PATCH /v1/tracking/folders/{folder}` document `422` validation errors (`name` ≤ 32, `description` ≤ 1000 chars).
- **Token prices:** `applications/metadata` and `applications/metadata/media` 10 → 5 per (app, locale); `keywords/ranking` 1 → 2 per (keyword, date); `keywords/popularity` 1 → 2 per (keyword, date), min 5 per keyword with history; `keywords/metrics` 5 for `popularity` / `max_popularity`, 1 for `impressions` / `difficulty` / `language` (was 1 for all); `applications/ranking/latest-by-keywords` 3 per started 30 keywords, min 15 (was 1 per 30, min 5).

### Housekeeping

- `scripts/sync_openapi.py` now resolves `$ref` parameters (the new analytics endpoints use shared components; the script crashed on them).
- Regenerated `references/openapi.json` and `references/endpoints.md`; updated `SKILL.md`, `references/api-overview.md` and `README.md`; bumped everything to 1.3.0.

## [1.2.0] — 2026-08-04

Synced against the API docs as of 2026-08-04.

### Added

- **`POST /v1/keywords/ranking/force-recheck`** — order an on-demand re-scan of the store top for up to 500 phrases in one (store, country). Returns `{"status": "accepted"}` as soon as the re-check is queued; fresh positions land in `keywords/ranking` / `applications/ranking` minutes later. Optional per-phrase webhook (`webhook.url`, `webhook.headers`, `webhook.include_positions`). Costs 15 tokens per unique phrase, +1 with a webhook, +1 more with `include_positions`.
- **Cross-country tracking folders** — folders now carry `settings.cross_country` (`true` by default). A cross-country folder spans every country of the project; a country-scoped folder (`false`) keeps its membership per country. Toggle it via `PATCH /v1/tracking/folders/{folder}`.
- **Optional `country_code` on `DELETE /v1/tracking/folders/{folder}/keywords`** — omit it to remove the keyword from the folder in every country, pass it to remove only that country's membership of a country-scoped folder.
- **New filters on `GET /v1/tracking/keywords`** — `filters[folder_ids][]` (max 100 folder ids) and `filters[deduplicate_modificators]` (collapse phrases differing only by case or leading/trailing punctuation; off by default).
- **Project access levels** — `GET /v1/projects/list` now returns projects the caller owns, projects shared with them, and (for enterprise team leads/owners) projects owned by members below them. Each project carries `access.owner.email` and `access.level` (`read` / `edit` / `owner`).
- **`403` "Access to the project is denied"** documented on every project-scoped endpoint (tracking, folders, recommended keywords, competitors, per-country counters).

### Changed

- **Breaking (API response):** ranking positions in `GET /v1/keywords/ranking` are now `{position, item: {origin_id, title}}` — the previous `app_info` key is gone.
- `POST /v1/tracking/keywords` can now answer `402` with either the plan-limit error or the project-access error.
- Dropped the stale "async rank tracking jobs" wording from `SKILL.md` — the real, documented endpoint is `keywords/ranking/force-recheck`.

### Housekeeping

- Regenerated `references/openapi.json` and `references/endpoints.md` via `scripts/sync_openapi.py`.
- Updated `SKILL.md`, `references/api-overview.md`, and `README.md`; bumped `VERSION`, `SKILL.md`, `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json` to 1.2.0.

## [1.1.0] — 2026-06-18

### Added

- `GET /v1/applications/ranking/latest-by-keywords` — latest known position per keyword in one call.
- `GET /v1/projects/countries-keywords-counts` — per-country tracked / recommended / ranking keyword counters with day-over-day `dynamic` (reflects the previous day).
- `GET /v1/subscription/limits` — plan `total` vs `used` for keywords, apps, archived apps, and public API tokens (new `Subscription` tag).

### Changed

- **Breaking (API):** `GET /v1/recommended-keywords` is now paginated (`page` / `per_page`, 100–1000) with `filters[recommended_keyword_state][]` and `filters[sources][]`.
- Regenerated the API reference snapshot; updated `SKILL.md`, `references/api-overview.md`, and `README.md`.

## [1.0.1] — 2026-06-12

### Added

- Claude Code plugin marketplace (`.claude-plugin/`) for one-line install.

### Changed

- Hardened `scripts/update.sh`: download validation, timestamped backups (last 3 kept), `rsync --delete` sync with an overlay fallback.
- Hardened `scripts/sync_openapi.py`: explicit User-Agent, request timeout, and actionable error messages; refuses to overwrite references when the fetched spec has no `paths`.

## [1.0.0] — 2026-06-12

### Added

- Initial `asolytics-api` agent skill: `SKILL.md`, `references/api-overview.md`, generated `references/endpoints.md`, the raw `references/openapi.json` snapshot, `scripts/sync_openapi.py`, `scripts/update.sh`, and the version self-check.
