# Implementation Guide — Self-Updating GitHub Profile Card

This project renders a **profile README card** (`dark_mode.svg` / `light_mode.svg`) that
GitHub auto-refreshes **every day** with your live stats (repos, commits, followers,
lines of code, account age…) via GitHub Actions + the GitHub GraphQL API.

Based on [Andrew Grant's daily-readme pipeline](https://github.com/Andrew6rant/Andrew6rant),
restructured with a generator script (`gen_card.py`), embedded photo, and custom layout.

```
┌─────────────────── how it fits together ───────────────────┐
│                                                            │
│  gen_card.py ──writes──▶ dark_mode.svg + light_mode.svg    │
│  (layout, palette,       (static parts + photo + ids)      │
│   photo embed)                  │                          │
│                                 ▼                          │
│  today.py ◀──secrets──  .github/workflows/build.yaml       │
│  (GraphQL stats)        (push to main + 04:00 UTC cron)    │
│         │                                                  │
│         └──rewrites <tspan id="*_data"> nightly──▶ SVGs    │
│                                     │                      │
│                                     ▼                      │
│  README.md  ◀── embeds both SVGs via <picture> (auto        │
│               light/dark switch on GitHub)                  │
└────────────────────────────────────────────────────────────┘
```

## Repo layout

| File | Role |
|---|---|
| `gen_card.py` | **Source of truth for the card design.** Rebuilds both SVGs from scratch: layout, colors, icons, embedded photo. Run this after any visual change, then commit the output. |
| `src/profile.png` | Full-res profile photo (personal — **not** published; keep in `.gitignore`). |
| `src/profile_card.jpg` | Optimized 680px JPEG that `gen_card.py` base64-embeds into the SVGs (regenerate with the `sips` command in `gen_card.py`'s comment; on Windows/Linux use ImageMagick: `magick src/profile.png -resize 680 -quality 78 src/profile_card.jpg`). |
| `dark_mode.svg` / `light_mode.svg` | Generated cards. `today.py` overwrites the stat values inside them nightly; they are otherwise never hand-edited. |
| `today.py` | Queries GitHub's GraphQL v4 API and rewrites the `<tspan>` values (by `id`) in both SVGs. |
| `README.md` | Embeds the two SVGs with a `<picture>` tag so GitHub follows your theme setting. |
| `.github/workflows/build.yaml` | GitHub Actions: runs `today.py` on every push to `main` and daily at 04:00 UTC, then commits + pushes the updated SVGs. |
| `cache/requirements.txt` | Python deps for the workflow (`requests`, `lxml`). |

## Requirements

- GitHub account + a **same-named public repo** (e.g. `youruser/youruser`) — this is the
  one repo whose root `README.md` GitHub renders on your profile page.
- Python 3.9+ with `requests` and `lxml` (`pip install -r cache/requirements.txt`) — only
  needed locally if you regenerate cards by hand; CI installs it itself.

## Setup

### 1. Create the profile repository
On GitHub, create a **public** repository named exactly after your username
(`<username>/<username>`). Its root `README.md` becomes your profile README.

### 2. Copy this project into it
Clone/fork this repo and rename files as needed, or copy its contents into your new
repo's root. Make sure `git origin` points at **your** repo:

```bash
git remote set-url origin https://github.com/<username>/<username>.git
```

### 3. Create a Personal Access Token
The workflow needs read access to your profile stats.

- GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → New.
- Resource owner: yourself. Repository access: **Only select repositories** → `<username>/<username>`
  (or All repositories).
- Under **Permissions → Account → Following followers, profile details, and star data → Read-only**
  (this covers followers/starring/watching, which the legacy REST can't read for other users).
- No expiration (or remember to rotate), then generate and copy the token.

### 4. Add repository secrets
Repo → Settings → Secrets and variables → Actions → New repository secret:

| Name | Value |
|---|---|
| `ACCESS_TOKEN` | the PAT from step 3 |
| `USER_NAME` | your GitHub username, e.g. `codejeroo` |

### 5. Personalize
- **Design** — open `gen_card.py` and edit any of: `W/H/RX0/RXE` (canvas + right-panel
  origin), `DARK`/`LIGHT` (palettes), `ICONS`, or the section coordinates inside
  `Card.render()`. Swap the photo: drop a new `src/profile.png`, run the `sips`/`magick`
  command noted in `gen_card.py`, then regenerate.
- **Content** — your handles, headline, bio quote etc. live in `Card.render()`
  (the `kv(...)` / `text(...)` calls).
- **Stats** — the ids `today.py` fills are `age_data, repo_data, contrib_data, star_data,
  commit_data, follower_data, loc_data, loc_add, loc_del`. `today.py` computes them from
  GraphQL (account age from your account's `createdAt`, LOC from your public commits'
  diff stats, with caching in `cache/`). If you change the design, keep those `id`
  attributes on the `<tspan>`s that should auto-update.

### 6. Regenerate and publish
```bash
python3 gen_card.py          # rebuilds dark_mode.svg + light_mode.svg
git add -A && git commit -m "Profile card"
git push origin main         # the push triggers the workflow immediately
```
On GitHub: Actions → **README build** → (if it's not running yet) **Run workflow**.
The bot commits `Updated README` with fresh numbers; your profile shows the card and
refreshes daily at 04:00 UTC.

## How the pieces talk to each other

- **SVG as `<img>`** — GitHub serves the raw SVG into an `<img>`, so: no JavaScript, no
  external image/font references (hence the photo's base64 data URI). Internal `<style>`
  and SMIL animation (`<animate>` — the blinking STATUS light) do work.
- **`gen_card.py` → SVG** — deterministic full rebuild; safe to run anytime. The two
  files are identical in structure, so the `<picture media="(prefers-color-scheme…">`
  in `README.md` gives you automatic theme switching.
- **`today.py` → SVG** — lxml parse, then `find_and_replace(root, '<id>', value)`
  rewrites only the `<tspan>`s matched by `id`. Null-safe: values whose elements were
  removed from the design are silently skipped, so layout changes never break CI.
- **Workflow** — `actions/checkout@v4` → `setup-python@v5` (3.12) → pip cache →
  `python today.py` → commit & push as `codejeroo/GitHub-Actions-Bot` (edit the name/email
  lines in `build.yaml` for yours).

## Troubleshooting

- **Workflow fails with 401/Bad credentials** — PAT expired, wrong scope, or secret names
  differ. Needs Account → *Following followers, profile details, and star data* → Read-only.
- **Stats didn't change** — check Actions run logs; the commit message `Updated README`
  with no diff means values were already current (cache). Delete the `cache/` JSON files
  in the repo to force a full recount.
- **Card looks broken after editing `gen_card.py`** — regenerate and open the SVG in a
  browser (not the macOS QuickLook popup, which crops wide SVGs and can mislead).
- **Photo not showing** — the asset path in `PHOTO_PATH` must exist relative to where you
  run `python3 gen_card.py` (repo root), and the SVG must stay valid XML after embedding.
- **Don't commit your full-res `src/profile.png` or any token** — add to `.gitignore`
  if you publish this repo.

## License / attribution

This project is based on Andrew Grant's (Andrew6rant) daily-readme pipeline (2022–2025).
Keep that attribution if you fork it publicly.
