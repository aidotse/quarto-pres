# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-deck Quarto + Reveal.js presentation template (AI Sweden branding) that doubles as a "design menu": one example slide per visual element, meant to be copied into real decks. There is no application code, test suite, or linter; the only "build" is rendering `index.qmd` to HTML.

User-facing docs live in `README.md` and are not repeated here. `grep -n '^##' README.md` finds:
- Prerequisites and Running locally
- Building for Production: lean, `export.sh`, and what the `standalone` build embeds
- Repository Structure: one line per file
- Responsive Layout: the behaviour as the user sees it
- What's on the Menu: all elements, plus a minimal `Deck.chart` example

Update the matching README section when you add or remove a menu element, a vendored library or a top-level file.

## Commands

```bash
quarto preview index.qmd                          # live-reload dev server
quarto render index.qmd                           # lean build: index.html + index_files/ (this is also the CI check)
quarto render index.qmd --profile standalone      # single self-contained, offline index.html (~20 MB)
./export.sh                                       # render, then zip index.html, index_files/, assets/, style.css into output.zip
node tools/shot.mjs --list                        # slide numbers, ids, titles (needs a render; see Verifying)
```

`*.html`, `*_files/`, `.quarto/`, and `*.zip` are gitignored; rendered output is never committed.

## Architecture

Each JS/CSS file documents itself in its header comment; read that before changing it.

- `index.qmd`: all slides; the Reveal.js config is in the front matter. Header scripts load in this order: vendored libraries, `responsive.js`, `deck.js`. Section dividers are `# [NN]{.section-num} Title {#id}`.
- `_quarto.yml` / `_quarto-standalone.yml`: document front matter beats profiles, so any option the `standalone` profile changes must live in `_quarto.yml` (currently `chalkboard`, which can't be embedded).
- `style.css`: tokens in `:root`, then one commented block per component. All portrait overrides are in the last block, "Responsive layout". Use `--series-1..8` in fixed order; the accent yellow is for emphasis only. Prefer shared classes and `var(--slide-h)` sizes to inline pixels, which don't reflow.
- `assets/js/deck.js`: chart theme and helpers. Charts register with `Deck.chart` / `Deck.steps` and are drawn when their slide is first shown.
- `assets/js/responsive.js`: fits the canvas to the window and sets `body.portrait`, `--slide-w` and `--slide-h`. Off in `?print-pdf`. Keep `scrollActivationWidth: 0`: `null` doesn't disable Reveal's mobile scroll view.
- `references.bib`: cited as `[@key]`. Quarto makes the References slide `.smaller`, so `#refs` sizes are relative to 0.7em.
- `assets/vendor/`: Plotly, D3, img-comparison-slider, qrcode-generator, Apache ECharts and the STIX Two Math font, so both builds work offline. Mermaid ships with Quarto. ECharts charts use `Deck.echarts(el, option)` (theme + SVG renderer) instead of `Deck.layout()`.
- `tools/`: dev-only helpers with their own `package.json`; not deployed. `compare_charts.py` (`tools/requirements.txt`) regenerates `assets/compare/`; change the data or Python styling there, never the generated files.
- `data-state="hide-ui"` on a slide hides the global logo and footer.

## Gotchas

- Slides marked `visibility="uncounted"` (the appendix) are excluded from `Reveal.getSlides()`; reach them via their `#/id` hash. `visibility="hidden"` slides are removed from the output entirely.
- Link to a slide with a plain `[text](#slide-id)`; Quarto rewrites it to Reveal's `#/slide-id`. Writing `#/slide-id` yourself produces a broken `#//slide-id`.
- Class names are global across components: e.g. the results-table badge is styled as `span.ours` so it doesn't hit the `.msg.ours` chat bubble.
- Pandoc turns unknown attributes into `data-*` (`{who="Baseline"}` → `data-who`), which CSS can read with `attr()`.
- Mermaid HTML labels are measured in scaled screen pixels, so they clip when Reveal scales the slide; use `htmlLabels: false` (top level of the cell's `config`, not under `flowchart`).
- `echo: true` is set globally, so `{mermaid}` cells need `%%| echo: false`. Mermaid config goes in a `---\nconfig: ...\n---` block inside the cell. Gantt task text colours can only be set via `themeVariables`, because Mermaid's own ID-scoped `!important` rules beat page CSS.
- `###` headings inside a slide become nested `<section>`s that Reveal counts as extra slides; use styled spans instead (except inside `.panel-tabset`, where Quarto converts them to tabs).
- Pandoc wraps bracketed spans in a `<p>`, so flex/grid containers of spans need `p { display: contents }` or `display: block` children (see `.logo-wall`, `.legend`, `.stat`).

## Verifying

A green render does not mean the slides look right: charts and diagrams are drawn client-side, and layouts must also hold in portrait. After rendering, screenshot the slides you touched and look at them:

```bash
(cd tools && npm install && npx playwright install chromium)   # once
node tools/shot.mjs results-table 14 --size 1920x1080,820x1180   # slide ids or numbers → shots/<W>x<H>/
node tools/shot.mjs --offline                                     # every slide, network blocked
```

The script exits non-zero on page JavaScript errors and on missing files (it names the file). By default every fragment is shown (`--frags none` for the initial state); slides with typewriter text or long animations may need a longer `--wait`. Check `--offline` against the standalone build too; only the YouTube and Datawrapper iframes should be blocked. For interactions (hover, drag, sliders), write a throwaway Playwright script in the same style.

## Deployment

Two parallel CI configs do the same thing and must be kept in sync:
- `.github/workflows/quarto-pages.yml` (GitHub Pages)
- `.gitlab-ci.yml` (GitLab Pages)

Both pin the Quarto version (`QUARTO_VERSION`, currently 1.9.38, also stated in the README's Prerequisites); bump all three together and re-check the deck. Dependabot (`.github/dependabot.yml`) bumps the actions and `tools/` monthly, but not Quarto.

- On every PR/MR, into any branch, `test-build` renders the lean and standalone builds, assembles `public/` like the deploy, and runs `tools/shot.mjs --offline` on both. That catches JS errors and files missing from the deployed set. On GitHub, the rendered decks and screenshots are uploaded as the `deck-preview` artifact.
- `test-build` is the required status check on `main`, and admins can't bypass it. Keep the job name, and don't add path filters that skip it, or PRs into `main` will wait forever for a check that never reports.
- On `main` (push or manual run) the CI renders, then copies **only** `index.html`, `index_files/`, `assets/` and `style.css` into `public/` and deploys. Any new local resource referenced by the deck must live under `assets/`, or else be added to both CI configs and `export.sh`.
