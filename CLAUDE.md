# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Marketing website for **BIG-MARK — Remonty Mieszkań**, a Polish apartment‑renovation
company. The brand assets are the logo ([assets/big-mark_logo_transparent.png](assets/big-mark_logo_transparent.png))
and 10 real work photos in [assets/photos/](assets/photos/) (`gallery-01.jpeg` … `gallery-10.jpeg`).

The goal is to reproduce the design template in
[assets/Flampt Webflow Website Copier/](assets/Flampt%20Webflow%20Website%20Copier/)
**1:1, including its animations**, rebranded for BIG‑MARK, then deploy it to
**Hostinger as a static HTML/PHP site**.

## Target stack & why

- **Plain HTML5 + CSS3 + vanilla JS**, with **PHP only for the contact form** (`mail()` / SMTP).
- **No build step / no framework / no Node tooling.** Files must upload to Hostinger
  shared hosting and run as‑is. Anything requiring a compile step (React, Astro, SASS that
  isn't pre‑compiled, bundlers) is out of scope — it breaks the "upload 1:1" requirement.
- The reference template is itself a static HTML/CSS/JS export, so the work is to
  **adapt** it, not rebuild from scratch.

## The reference template (the source of truth for design)

[assets/Flampt Webflow Website Copier/](assets/Flampt%20Webflow%20Website%20Copier/) is a
**Webflow export** of the "Flampt" construction/roofing theme. Structure:

- `index.html` — single, **minified** long‑line page (Home layout). ~134 animated elements.
- `css/flampt.webflow.shared.*.css` — entire stylesheet. All classes are prefixed **`rt-`**
  (e.g. `rt-hero-v...`, `rt-service-v...`, `rt-process-v...`, `rt-pricing-v...`,
  `rt-contact-v...`). The CSS covers many page variants, but only the Home page is exported.
- `js/` — animation runtime, load order matters:
  - `gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js` — GSAP scroll/text animations
  - `jquery-3.5.1.min.*.js`
  - `webflow.*.js` + `webflow.schunk.*.js` — **Webflow IX2** interactions engine
  - `webfont.js` — loads Google **Inter** font (weights 300–700)
- `images/` (146 files) — `.svg` icons/masks, `.avif`/`.webp` photos, hashed Webflow names.
- `media/` (4 files) — hero background `.mp4`/`.webm` videos.

### How the animations actually work (critical)

There are **two** animation systems, both must be preserved for a 1:1 result:

1. **Webflow IX2** — driven by `data-w-id="..."` attributes on elements (134 of them) plus
   inline `<style>` setting initial transform/opacity states. The `webflow.*.js` runtime reads
   these and plays scroll/hover/load timelines. If you change/remove a `data-w-id` or its
   paired initial inline style, that element's animation breaks.
2. **GSAP** (ScrollTrigger + SplitText) — for marquee, split‑text reveal, and scroll‑pinned
   effects layered on top of IX2.

Fonts load via `WebFont.load({ google: { families: ["Inter:300,400,500,600,700"] }})`.

## Working conventions for this repo

- **Don't hand‑edit the files inside `Flampt Webflow Website Copier/`.** Treat that folder as
  the read‑only reference. Build the BIG‑MARK site as a **copy** (the user will direct where —
  likely repo root) and modify the copy.
- **Rebrand mapping** when adapting copy/content:
  - Domain: roofing/construction → **apartment renovation (remont mieszkań)**.
  - Language: English → **Polish**.
  - Replace template stock images with `assets/photos/gallery-*.jpeg` and the BIG‑MARK logo.
  - Brand colors come from the logo: charcoal/near‑black + amber/gold accent on white.
    Map these onto the template's CSS color variables rather than rewriting the stylesheet.
- **Preserve `data-w-id` attributes and their paired inline initial‑state styles** when editing
  markup, or animations silently stop working.
- **Asset paths must stay web‑safe.** The original photo folder (Cyrillic name + trailing space,
  spaced filenames) was already renamed to `assets/photos/gallery-NN.jpeg` for this reason —
  keep new asset names lowercase, no spaces, ASCII.
- Some template markup still points at `website-files.com` CDN URLs (12 refs) and
  `googleapis`/`gstatic`. For a self‑contained Hostinger deploy, **localize remaining CDN
  references** (download the asset into `images/`/`media/` and repoint), except Google Fonts
  which can stay remote.

## Verifying / previewing locally

No build. For static preview: open the HTML directly, or serve the folder, e.g.
`php -S localhost:8000` (also exercises any `.php` form handler) or `python3 -m http.server`.
Run from the directory that contains the page so relative `css/`, `js/`, `images/`, `media/`
paths resolve.

## Deployment

Target is **Hostinger** shared hosting (HTML/PHP). Final deliverable = the static files +
PHP contact handler, uploaded via Hostinger File Manager / FTP. No server‑side runtime beyond
PHP is available — design accordingly.
