---
name: asolytics-api
version: 1.2.0
description: Use the Asolytics Public API for ASO research and automation. Trigger this skill when the agent needs to query app metadata, availability, versions, installs, revenue, rankings, keyword metrics, live search results, forced ranking re-checks, recommended keywords, tracked keywords, tracking folders, competitors, projects (own and shared), per-country keyword counts, balance, subscription/plan limits, or store charts from Asolytics. Also use it when a user wants curl examples, lightweight integrations, or repeatable reporting workflows against the Asolytics API.
homepage: https://github.com/Asolytics-Pro/asolytics-app-store-optimization-api
---

# Asolytics Public API

## Overview

Use this skill to work against the Asolytics Public API safely and efficiently.
Prefer the bundled references over re-discovering the API from scratch, and refresh the spec before relying on exact request or response shapes if the docs may have changed.

## Workflow

1. Read [references/api-overview.md](references/api-overview.md) first for auth, base URL, and endpoint families.
2. Read [references/endpoints.md](references/endpoints.md) when you need endpoint-level parameters or request body fields.
3. Read [references/openapi.json](references/openapi.json) only when exact schema details or edge cases matter.
4. Prefer small, cheap requests first because the API is alpha and some endpoints consume tokens.
5. Use `GET /public-api/v1/balance` when token awareness matters before running a wide query.

## Auth

Send the personal public API token in the `X-PUBLIC-API-TOKEN` header.
Prefer an environment variable such as `ASOLYTICS_PUBLIC_API_TOKEN` instead of pasting secrets into files or commits.

If the token is missing, ask the user for it. If they don't have one yet, walk them through getting it:

1. Create a free Asolytics account (or log in): https://app.asolytics.pro/login
2. Open the profile page and copy the public API token: https://app.asolytics.pro/profile
3. Export it locally so it isn't pasted into chats or commits: `export ASOLYTICS_PUBLIC_API_TOKEN="<token>"`

Do this before running any write or paid requests.

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  "https://app.asolytics.pro/public-api/v1/balance"
```

## Common Patterns

### Catalog Bootstrap

Resolve lookup data before building other requests:

1. Countries
2. Locales
3. Devices
4. Categories
5. Clusters
6. Projects

This avoids guessing valid `store`, `country_code`, `device`, `category_key`, `cluster_key`, and `project_id` values.

### App Intelligence

Use the Applications endpoints for:

- current listing metadata
- screenshots and media
- store availability
- version history
- installs and revenue history
- ranking history (full history, or the latest known position per keyword via `applications/ranking/latest-by-keywords`)

Start with the narrowest possible app set because some metadata endpoints bill per returned pair.

### Keyword Workflows

Use the Keywords and Recommended Keywords endpoints for:

- ranking history — note the position shape is `{position, item: {origin_id, title}}` (the older `app_info` key is gone)
- popularity history
- latest keyword metrics
- live search top 50
- recommended keyword review — `recommended-keywords` is **paginated** (`page`/`per_page`, 100–1000); loop until `pagination.current_page == pagination.total_pages`, and narrow with `filters[recommended_keyword_state][]` (recommended/tracked/declined) or `filters[sources][]` (meta/competitors/suggestions/rankings/related)
- forced ranking re-checks — `POST keywords/ranking/force-recheck` queues an on-demand re-scan of the store top for up to 500 phrases in one (store, country); it returns `{"status": "accepted"}` immediately and the fresh positions appear in `keywords/ranking` / `applications/ranking` a few minutes later

### Forced Re-checks Are Expensive

`keywords/ranking/force-recheck` bills **per unique phrase, at queue time** (not on completion): 15 tokens, **+1** with a `webhook`, **+1** more with `webhook.include_positions` — 15 / 16 / 17 each. Duplicates are collapsed case-insensitively and billed once. Confirm the phrase list with the user before firing a large batch, and check `balance` first.

Webhooks deliver one POST per phrase: `{request: {id}, task: {keyword, country_code, store}, result: {status}}`, plus `result.positions` (up to 50 `{position, item: {origin_id}}` entries) when `include_positions` is on. The callback URL must be public http/https — private, loopback, and link-local hosts are rejected; non-200 replies are retried twice, then dropped.

When the user wants automation, prefer plain HTTP calls and return the exact request payload you used.

### Tracking Maintenance

Use Tracking Keywords and Tracking Folders for:

- listing tracked keywords — optionally narrowed by `filters[folder_ids][]` (max 100 folder ids) and collapsed with `filters[deduplicate_modificators]=true`, which merges phrases differing only by case or leading/trailing punctuation into one row (off by default)
- adding tracked keywords
- deleting tracked keywords by `keyword_ids`
- creating folders
- renaming folders, editing their description, and toggling `settings.cross_country` via `PATCH tracking/folders/{folder}`
- adding or removing keywords inside folders

**Cross-country folders.** A folder is cross-country by default (`settings.cross_country = true`): a keyword added to it in one country counts as being in that folder in every country of the project. With `false` the membership is country-scoped. This changes two things:

- `DELETE tracking/folders/{folder}/keywords` takes an optional `country_code` — omit it to drop the keyword from the folder everywhere, pass it to drop only that country's membership of a country-scoped folder (ignored for cross-country folders).
- untracking a keyword in one country only removes it from that country's country-scoped folders; elsewhere it stays.

Fetch first, mutate second. For delete operations, resolve ids and current contents before issuing the write request.

### Competitors and Charts

Use Competitors and Store Charts for:

- listing current competitors
- marking or unmarking a competitor
- retrieving top-500 charts by store, country, cluster, category, and device

### Project & Account Insight

Use Projects and Subscription for cheap, high-level dashboards:

- `projects/list` returns projects the caller owns, projects **shared** with them, and — for enterprise team leads/owners — projects owned by members below them. Each project carries `access.owner.email` and `access.level` (`read` / `edit` / `owner`). Check `access.level` before proposing a write: a `read` project will reject tracking, folder, competitor, and decline calls.
- `projects/countries-keywords-counts` — per-country tracked / recommended / ranking keyword counts plus their day-over-day `dynamic`, for one project. A cheap snapshot of project breadth; note it reflects the **previous day** (use the list endpoints for exact, current values).
- `subscription/limits` — plan `total` vs `used` for keywords, apps, archived apps, and public API tokens. Pair with `GET /public-api/v1/balance` whenever quota or token headroom matters before a wide query.

## Guardrails

- Treat the API as unstable unless the current OpenAPI spec confirms the shape you expect.
- A `403` from any project-scoped endpoint means the token has no access to that `project_id` — re-read `projects/list` and its `access.level` instead of retrying.
- Do not hardcode secrets in source files, shell history snippets, or Git commits.
- Call out token-related costs when a request fans out across many apps, locales, or keywords.
- Prefer read-only endpoints before any state-changing request.
- Echo the exact endpoint, query parameters, and JSON body in your answer when the user asks for integration help.

## Staying Up To Date

This skill is versioned (see the `version` in the frontmatter above and the `VERSION` file). A newer version may be published on GitHub.

When this skill is first invoked in a session, do a lightweight update check (skip silently if offline or if it fails):

1. Read the local version from the `VERSION` file in this skill folder.
2. Fetch the latest published version:
   `https://raw.githubusercontent.com/Asolytics-Pro/asolytics-app-store-optimization-api/main/skills/asolytics-api/VERSION`
3. If the remote version is greater than the local one, tell the user a new version is available and what changed (see `https://raw.githubusercontent.com/Asolytics-Pro/asolytics-app-store-optimization-api/main/CHANGELOG.md`), then **offer** to update — don't update without asking.
4. If they accept, run `scripts/update.sh` from this skill folder. It backs up the current folder and overlays the latest files from GitHub in place. Then confirm the new version from `VERSION`.

Do not check more than once per session, and never block real work on the check.

## Resources

- `VERSION`: current skill version, used for the self-update check.
- `references/api-overview.md`: fast orientation and usage guidance.
- `references/endpoints.md`: generated endpoint inventory grouped by tag.
- `references/openapi.json`: raw public OpenAPI snapshot.
- `scripts/sync_openapi.py`: refresh the OpenAPI snapshot and regenerate `endpoints.md`.
- `scripts/update.sh`: update this installed skill to the latest GitHub version.
