# Asolytics Public API Overview

## Base URL

- `https://app.asolytics.pro`

## Documentation

- Human docs: `https://app.asolytics.pro/api/public-api/documentation`
- OpenAPI JSON: `https://app.asolytics.pro/api/public-api/docs?public-api-docs.json`

## Authentication

- Header: `X-PUBLIC-API-TOKEN`
- Scheme type in OpenAPI: `apiKey`
- Recommended local env var: `ASOLYTICS_PUBLIC_API_TOKEN`

## Stability Notes

- The docs describe the API as `1.0.0-alpha`.
- Endpoint shapes, parameters, response formats, and token costs may change.
- Re-check the bundled OpenAPI snapshot before relying on exact field names.

## Fast Start

```bash
export ASOLYTICS_PUBLIC_API_TOKEN="..."

curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  "https://app.asolytics.pro/public-api/v1/balance"
```

## Endpoint Families

### Applications

- Metadata
- Media
- Availability
- Versions
- Installs history
- Revenue history
- Ranking history
- Latest ranking position per keyword (`applications/ranking/latest-by-keywords`)

### Common Catalogs

- Countries
- Locales
- Devices
- Categories
- Clusters

Use these first when the user does not already know valid store, locale, country, category, cluster, or device values.

### Keywords

- Ranking history (positions are `{position, item: {origin_id, title}}`)
- Popularity history
- Latest metrics
- Live search top 50
- Forced ranking re-check (`keywords/ranking/force-recheck`) — on-demand re-scan of up to 500 phrases, optional per-phrase webhook; 15 tokens per unique phrase, +1 with a webhook, +1 more with `include_positions`
- Recommended keywords (paginated; filter by state and source)
- Decline and undecline actions

### Tracking

- Tracked keywords (filter by `filters[folder_ids][]`, collapse case/punctuation variants with `filters[deduplicate_modificators]`)
- Tracking folders, cross-country or country-scoped (`settings.cross_country`, cross-country by default)
- Add, delete, patch, and folder assignment operations (folder removal takes an optional `country_code`)

### Competitors

- List competitors
- Mark competitor
- Unmark competitor

### Subscription

- Plan limits — `total` vs `used` for keywords, apps, archived apps, and public API tokens (`subscription/limits`)

### Other

- Balance
- Projects list — owned, shared, and (for enterprise leads) team members' projects, each with `access.owner.email` and `access.level` (`read`/`edit`/`owner`)
- Per-country keyword counters (`projects/countries-keywords-counts`)
- Store charts

## Project Access

Every project-scoped endpoint (tracking, folders, recommended keywords, competitors, per-country counters) answers `403 {"error": "Access to the project is denied"}` when the token has no access to that `project_id`. Read `access.level` from `projects/list` before writing: `read` projects reject mutations.

## Practical Workflow

1. Resolve `project_id` from `/public-api/v1/projects/list` if the task is project-scoped.
2. Resolve catalog values if the task requires `store`, `country_code`, `locale`, `device`, `cluster_key`, or `category_key`.
3. Check `/public-api/v1/balance` if the user is cost-sensitive.
4. Run the smallest read-only request that answers the question.
5. Only then issue write requests such as competitor marking or tracking changes.

## High-Value Examples

### Current app listing text

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  --get "https://app.asolytics.pro/public-api/v1/applications/metadata" \
  --data-urlencode "origin_ids[]=1234567890" \
  --data-urlencode "locales[]=en-US"
```

### Latest keyword metrics

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  --get "https://app.asolytics.pro/public-api/v1/keywords/metrics" \
  --data-urlencode "keywords[]=photo editor" \
  --data-urlencode "store=APP_STORE" \
  --data-urlencode "country_code=US" \
  --data-urlencode "metrics[]=popularity"
```

### Create a tracking folder

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "https://app.asolytics.pro/public-api/v1/tracking/folders" \
  -d '{"project_id":123,"name":"Core Keywords","description":"Tier 1 terms"}'
```

### Latest position per keyword

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  --get "https://app.asolytics.pro/public-api/v1/applications/ranking/latest-by-keywords" \
  --data-urlencode "origin_id=1234567890" \
  --data-urlencode "country_code=US" \
  --data-urlencode "keywords[]=fitness app" \
  --data-urlencode "keywords[]=workout tracker"
```

### Force a ranking re-check (with webhook)

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "https://app.asolytics.pro/public-api/v1/keywords/ranking/force-recheck" \
  -d '{
        "keywords": ["photo editor", "video maker"],
        "store": "APP_STORE",
        "country_code": "US",
        "webhook": {"url": "https://example.com/asolytics/recheck", "include_positions": true}
      }'
```

### Plan limits (total vs used)

```bash
curl -sS \
  -H "X-PUBLIC-API-TOKEN: $ASOLYTICS_PUBLIC_API_TOKEN" \
  "https://app.asolytics.pro/public-api/v1/subscription/limits"
```
