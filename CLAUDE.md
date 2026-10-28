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

- `index.qmd`: all slides. Front matter holds the Reveal.js config: a nominal **1920×1080** canvas, `html-math-method: mathml`, `bibliography: references.bib`, and `include-in-header` script tags for the vendored libraries, `responsive.js` and `deck.js` (in that order). `# [NN]{.section-num} Title {#id}` headings are section dividers; they also group slides into vertical stacks, but navigation stays linear.
- `_quarto.yml` / `_quarto-standalone.yml`: the folder is a Quarto project only so the `standalone` profile can override options. Document front matter beats profiles, so any option the profile must change must live in `_quarto.yml`, not `index.qmd`. Currently that is `chalkboard`, which is incompatible with `embed-resources`.
- `style.css`: design tokens in `:root`, then one block per component. Notable tokens:
  - `--series-1..8`: the chart palette, validated for colour-blind safety on `--surface`. Assign series in that fixed order. The accent yellow is for emphasis only, never a regular series colour.
  - `--mermaid-*`: read by Quarto's Mermaid theme.

  Prefer the shared classes over inline styles. The last section ("Responsive layout") holds the flex-column rules and every `body.portrait` override.
- `assets/js/deck.js`: the shared chart theme (`Deck.layout()`, `Deck.config`, `Deck.colors` read from the CSS vars, seeded `Deck.rng()`), plus the slide lifecycle:
  - Charts register with `Deck.chart(id, init)` or `Deck.steps(id, {init, step})` in an inline `<script>` next to their container. They are drawn only when their slide is first shown, because hidden slides have zero size. `step(el, i)` is called again on every fragment change, with the highest visible fragment index (−1 = none).
  - `Deck.resize()` redraws visible charts and marks hidden ones stale.
  - It also handles:
    - `.count` count-up numbers
    - `.spark` sparklines
    - `.typewriter` fragments: typed out on reveal; nested fragments are skipped
    - `Deck.tokens(el, [[token, score], ...])` for token attribution
    - `.qr` codes: the deck URL when served over http, else `data-fallback`
    - a pointer fix for `img-comparison-slider` under Reveal's CSS scaling
- `assets/js/responsive.js`: resizes Reveal's logical canvas to fit the window (the behaviour is described in the README) and adds `body.portrait`.
  - It exposes `--slide-w` / `--slide-h`; chart heights are `calc()`s of these.
  - It disables Reveal's automatic mobile scroll view with `scrollActivationWidth: 0`; `null` would not deactivate it.
  - It calls `Deck.resize()`.

  Slides are flex columns whose blocks get `margin-top: auto`, so spare height is shared evenly. Captions that must stick to the block above (`.lead`, `.chart-note`, ...) are excluded in `style.css`. Inline pixel values are relative to the current canvas, so prefer layout classes and `var(--slide-h)`-based sizes. Print/PDF mode (`?print-pdf`) skips all of this.
- `references.bib`: cited as `[@key]`, resolved by Pandoc at build time, and listed on the `## References` slide (`::: {#refs}`). Quarto makes that slide `.smaller`, so `#refs` sizes are relative to 0.7em.
- `assets/vendor/`: Plotly, D3, img-comparison-slider, qrcode-generator and the STIX Two Math font are vendored (no CDNs), so both builds work offline. Mermaid comes bundled with Quarto.
- `tools/`: dev-only helpers with their own `package.json`. Not deployed.
- **`hide-ui` state**: `data-state="hide-ui"` on a slide hides the global logo and footer.

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

The script exits non-zero on page JavaScript errors. By default every fragment is shown (`--frags none` for the initial state); slides with typewriter text or long animations may need a longer `--wait`. Check `--offline` against the standalone build too; only the YouTube and Datawrapper iframes should be blocked. For interactions (hover, drag, sliders), write a throwaway Playwright script in the same style.

## Deployment

Two parallel CI configs do the same thing and must be kept in sync:
- `.github/workflows/quarto-pages.yml` (GitHub Pages)
- `.gitlab-ci.yml` (GitLab Pages)

On PRs/MRs they only run `quarto render index.qmd`. On `main` they render and then copy **only** `index.html`, `index_files/`, `assets/`, and `style.css` into `public/`. Any new local resource referenced by the deck must live under `assets/`, or else be added to both CI configs and `export.sh`; otherwise it will be missing from the deployed or exported presentation.
