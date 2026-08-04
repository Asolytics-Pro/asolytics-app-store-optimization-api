# Asolytics API — App Store Optimization (ASO) Agent Skill

An agent skill for the **[Asolytics](https://asolytics.pro/) Public API** - the App Store Optimization (ASO) API for App Store and Google Play keyword research, app rankings, keyword metrics, competitor analysis, installs & revenue estimates, and store charts.

**API docs:** https://app.asolytics.pro/api/public-api/documentation


## What you can get

This is mainly an **ASO research & intelligence API** — pull keyword and app data for **any app** on the App Store and Google Play, not just your own:

| Area | What you get |
| --- | --- |
| **Keyword metrics** | Popularity (search volume), results count, and other metrics for any keyword — plus **popularity history** over time and an app's **ranking history** for a keyword. |
| **Live search results** | The real **top-50 search results** for any keyword, country, and store — fetched live, right now. |
| **Keyword ideas** | Recommended keywords Asolytics suggests for a project — filterable by state and source. |
| **App metadata** | Current store listing for any app — title, subtitle, description, screenshots & media, version history, and the countries it's available in. |
| **Installs & revenue estimates** | Monthly **estimated installs** and **revenue**, per app and per country. |
| **Rankings & store charts** | An app's category and keyword **ranking history** (or the **latest position per keyword** in one call), plus full **top-500 store charts** by country, category, and device. |
| **On-demand re-checks** | Force a **fresh rank scan** for up to 500 phrases at once, with an optional **webhook** per phrase when the scan lands. |
| **Competitors** | The competitor set for any app. |
| **Lookups** | Reference data to build valid queries: countries, locales, devices, categories, and clusters. |

It can also **manage your own Asolytics workspace** in one place — your projects (owned and **shared with you**, including **per-country keyword counts**), tracked keywords & folders, competitor marks, your **plan limits** (`total` vs `used`), and your remaining API **token balance** (the API is metered).

Full endpoint-by-endpoint reference: [`skills/asolytics-api/references/endpoints.md`](skills/asolytics-api/references/endpoints.md). What changed between releases: [`CHANGELOG.md`](CHANGELOG.md).

## 1️⃣ Before you start

You need a free Asolytics account and your personal API token:

1. **Register a free account** (or log in): **https://app.asolytics.pro/login**
2. **Open your profile and copy the API token:** **https://app.asolytics.pro/profile**
3. The skill will ask you for it when needed (or you can set it once as the `ASOLYTICS_PUBLIC_API_TOKEN` environment variable).


## 2️⃣ Install

A skill is a folder named `asolytics-api/` that lives inside your agent's `skills/` directory. Installing = putting that folder in the right place.

### Option A — Just ask your agent (easiest)

If you use Claude Code, Codex, or a similar agent, paste this prompt to it and let it do the work:

```markdown
Install the Asolytics ASO skill for me. First ask whether to install it globally (in my home skills folder, available in every project) or a project-local level (in this project's skills folder, scoped to this repo).
Then clone `https://github.com/Asolytics-Pro/asolytics-app-store-optimization-api` and copy its `skills/asolytics-api` folder into the matching directory: global → `~/.claude/skills/` (Claude Code) or `~/.codex/skills/` (Codex); project-local → `./.claude/skills/` (Claude Code) or `./.codex/skills/` (Codex).
Create the directory if it doesn't exist, then confirm where it's installed.
```

The agent will ask which option you want and run the right commands. No terminal knowledge required.

### Option B — `npx skills` (recommended — works with any agent)

The [Skills CLI](https://github.com/vercel-labs/skills) installs this skill into any supported agent — Claude Code, Codex, Cursor, OpenCode, and 60+ more. It asks which agent and scope, or you pass flags:

```bash
# Interactive — it picks up your agent and asks global vs project:
npx skills add https://github.com/Asolytics-Pro/asolytics-app-store-optimization-api --skill asolytics-api
```

### Option C — Claude Code plugin (one-line install + auto-updates)

This repo is also a Claude Code plugin marketplace, so Claude Code users can install it without copying files. In Claude Code, run:

```text
/plugin marketplace add Asolytics-Pro/asolytics-app-store-optimization-api
/plugin install asolytics-api@asolytics
```

Installed this way, the plugin updates through Claude Code's plugin system (run `/plugin` to manage it).

### Option D — Copy it yourself (terminal)

First get the files: click the green **Code → Download ZIP** on GitHub and unzip it, **or** run:

```bash
git clone https://github.com/Asolytics-Pro/asolytics-app-store-optimization-api.git
cd asolytics-app-store-optimization-api
```

Then copy the skill folder to **either** a global **or** a project-local location:

```bash
# --- Claude Code / Claude Desktop ---
# Global (every project):
mkdir -p ~/.claude/skills && cp -R skills/asolytics-api ~/.claude/skills/
# Project-local (run from inside your project; commit it to share with your team):
mkdir -p .claude/skills && cp -R skills/asolytics-api .claude/skills/

# --- OpenAI Codex ---
# Global:
mkdir -p ~/.codex/skills && cp -R skills/asolytics-api ~/.codex/skills/
# Project-local:
mkdir -p .codex/skills && cp -R skills/asolytics-api .codex/skills/
```

For any other agent, copy the `skills/asolytics-api/` folder into that agent's global or project skills directory (most agents use the same `skills/<name>/` layout).

### After installing

Restart your agent if it was already running, then ask it something like:
> *"Use the Asolytics api skill to show the top-50 live search results for 'photo editor' in the US App Store."*

The first time, the agent will ask for your API token — paste it (or set it as the `ASOLYTICS_PUBLIC_API_TOKEN` environment variable so you only do it once).

## Updating the skill

The skill is versioned. When a newer version is published here on GitHub, the skill itself will **notice and offer to update** the next time you use it — just say yes. Under the hood it runs `scripts/update.sh`, which backs up your current copy and installs the latest files.

You can also update manually any time — run `update.sh` from wherever you installed the skill:

```bash
# global install:
bash ~/.claude/skills/asolytics-api/scripts/update.sh      # or ~/.codex/skills/...
# project-local install (from the project root):
bash .claude/skills/asolytics-api/scripts/update.sh        # or .codex/skills/...
```

## Keeping the API reference fresh

The Asolytics API is in alpha and can change. To refresh the bundled API snapshot (endpoint list & schemas) at any time:

```bash
python3 skills/asolytics-api/scripts/sync_openapi.py
```

It re-downloads the latest spec and regenerates `references/openapi.json` and `references/endpoints.md`.

## License

MIT — see [LICENSE](LICENSE).

> **Keywords:** Asolytics API · App Store Optimization API · ASO API · ASO keyword research · App rankings API · App Store & Google Play Top Charts 
