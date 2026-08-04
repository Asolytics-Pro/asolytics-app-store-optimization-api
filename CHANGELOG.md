# Changelog

All notable changes to the `asolytics-api` skill. Versions here are **skill** versions (`skills/asolytics-api/VERSION`), not API versions — the Asolytics Public API itself is still `1.0.0-alpha`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
