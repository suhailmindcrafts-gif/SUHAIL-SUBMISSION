# SUHAIL-SUBMISSION

## UI Animation Case Studies

Two micro-interaction projects on one page: **01 Who we serve** (23 animated trade icons) and **02 A reactive orb for AI states** (the B-BOT orb and chat demo), each with its case study.

## Deploy to Vercel

The production website is self-contained into a single fast `index.html` (all CSS, JS, and 60 icon layers inlined) plus `vercel.json`.

**Option A, GitHub (Zero-config):**
1. Import this repository in Vercel (*Add New → Project*).
2. Leave all settings at default (**Root Directory: `./`**, Framework Preset: **Other**, no build step needed).
3. Click **Deploy**. (Deploying from `site/` as root directory is also fully supported).

**Option B, Command line:**
```bash
npx vercel deploy --prod
```
Vercel prints a public URL you can share.

## Editing

- Edit **`trade-icons.html`**, the readable source page. It loads icon layers from `icons/layers/`, so preview it through a local server (for example `python3 -m http.server`), not by opening the file directly.
- Then rebuild the deployable page:

```bash
python3 tools/build_site.py
```

  This inlines the optimised icon layers, strips comments and indentation, and rewrites `site/index.html` and `site/vercel.json`. It uses only the Python standard library.

- Only if you change the icon artwork in `icons/layers/`, re-run `tools/optimize_icons.py` first (it needs Pillow: `pip install pillow`).

## What's where

| Path | What it is |
|---|---|
| `site/` | **Deploy this.** Built, single-file website |
| `trade-icons.html` | Editable source page |
| `icons/` | Original icon cut-outs, their animation layers, and optimised crops (`icons/web/`) |
| `icon gif/` | Exported GIFs of the icon animations (not part of the website) |
| `tools/` | Build and icon optimisation scripts |

## Why it loads fast

- **One request:** HTML, CSS, JS and all 60 icon layers ship in a single ~73 KB (compressed) file.
- **Lossless, cropped icons:** each layer is cropped to its painted area and kept pixel-exact.
- **Non-blocking font:** text appears immediately in the system font and switches to Figtree when it arrives.
- **Off-screen work is skipped:** case studies aren't rendered until scrolled near, and the orbs pause while out of view.
- **No libraries or frameworks.**
