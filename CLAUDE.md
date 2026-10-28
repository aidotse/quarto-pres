# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-deck Quarto + Reveal.js presentation template (AI Sweden branding) that doubles as a "design menu": one example slide per visual element, meant to be copied into real decks. There is no application code, test suite, or linter — the only "build" is rendering `index.qmd` to HTML.

## Commands

```bash
quarto preview index.qmd                          # live-reload dev server
quarto render index.qmd                           # lean build: index.html + index_files/ (this is also the CI check)
quarto render index.qmd --profile standalone      # single self-contained, offline index.html (~20 MB)
./export.sh                                       # render, then zip index.html, index_files/, assets/, style.css into output.zip
```

`*.html`, `*_files/`, `.quarto/`, and `*.zip` are gitignored — rendered output is never committed. A green render does not mean the slides look right; check visually (charts and diagrams are drawn client-side).

## Architecture

- `index.qmd` — all slides. Front matter holds the Reveal.js config: a nominal **1920×1080** canvas, `html-math-method: mathml`, and `include-in-header` script tags for the vendored libraries and `assets/js/deck.js`. `# [NN]{.section-num} Title` headings are section dividers (they also group slides into vertical stacks; navigation stays linear).
- `_quarto.yml` / `_quarto-standalone.yml` — the folder is a Quarto project only so the `standalone` profile can override options. Document front matter beats profiles, so any option the profile must change (currently `chalkboard`, which is incompatible with `embed-resources`) must live in `_quarto.yml`, not in `index.qmd`.
- `style.css` — design tokens in `:root` (brand colours, `--series-1..8` chart palette validated for colour-blind safety on `--surface`, `--mermaid-*` vars read by Quarto's Mermaid theme) followed by reusable component classes (`.card`, `.grid2/3/4`, `.grid-2-1`, `.stat`, `.takeaway`, `.chart`, `.chart-steps`, ...). Prefer these classes over inline styles. The accent yellow is for emphasis only, never a regular series colour.
- `assets/js/deck.js` — shared chart theme (`Deck.layout()`, `Deck.config`, `Deck.colors` read from the CSS vars, seeded `Deck.rng()`), plus lifecycle: charts register with `Deck.chart(id, init)` / `Deck.steps(id, {init, step})` in inline `<script>` blocks next to their container and are only drawn when their slide first becomes visible (hidden slides have zero size). `step(el, i)` is re-called on every fragment change with the highest visible fragment index (−1 = none). It also handles `.count` count-up numbers, `.spark` sparklines, and a pointer fix for `img-comparison-slider` under Reveal's CSS scaling.
- `assets/js/responsive.js` — resizes Reveal's logical canvas to the window: landscape keeps width 1920 (height 1080–1440), ultrawide keeps height 1080 (width up to 2520), portrait uses width 1080 and adds `body.portrait`. It exposes `--slide-w`/`--slide-h` (chart heights are `calc()`s of these), disables Reveal's automatic mobile scroll view (`scrollActivationWidth: 0` — `null` would not deactivate it), and calls `Deck.resize()`. Slides are flex columns whose blocks get `margin-top: auto`, so spare height is shared evenly; captions that must stick to the block above (`.lead`, `.chart-note`, ...) are excluded in `style.css`. Inline pixel values are relative to the current canvas, so prefer layout classes and `var(--slide-h)`-based sizes. Print/PDF mode skips all of this.
- `assets/vendor/` — Plotly, D3, img-comparison-slider and the STIX Two Math font are vendored (no CDNs) so both builds work offline. Mermaid comes bundled with Quarto.
- **`hide-ui` state**: `data-state="hide-ui"` on a slide hides the global logo and footer.

## Gotchas

- Mermaid HTML labels are measured in scaled screen pixels, so they clip when Reveal scales the slide; use `htmlLabels: false` (top level of the cell's `config`, not under `flowchart`).
- `echo: true` is set globally, so `{mermaid}` cells need `%%| echo: false`. Mermaid config goes in a `---\nconfig: ...\n---` block inside the cell; Gantt task text colours can only be set via `themeVariables` (Mermaid's own ID-scoped `!important` rules beat page CSS).
- `###` headings inside a slide become nested `<section>`s that Reveal counts as extra slides; use styled spans instead (except inside `.panel-tabset`, where Quarto converts them to tabs).
- Pandoc wraps bracketed spans in a `<p>`, so flex/grid containers of spans need `p { display: contents }` or `display: block` children (see `.logo-wall`, `.legend`, `.stat`).

## Deployment

Two parallel CI configs do the same thing and must be kept in sync:
- `.github/workflows/quarto-pages.yml` (GitHub Pages)
- `.gitlab-ci.yml` (GitLab Pages)

On PRs/MRs they only run `quarto render index.qmd`. On `main` they render and then copy **only** `index.html`, `index_files/`, `assets/`, and `style.css` into `public/`. Any new local resource referenced by the deck must live under `assets/` — or else be added to both CI configs and `export.sh`, otherwise it will be missing from the deployed/exported presentation.
