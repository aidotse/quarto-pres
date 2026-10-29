# quarto-pres

Pristine presentations with [Quarto](https://quarto.org/) and [Reveal.js](https://revealjs.com/).

## 🛠️ Prerequisites

To render or edit this presentation, you will need to install Quarto on your local machine.

1. **Download Quarto:** Go to the [Quarto Downloads page](https://quarto.org/docs/get-started/) and install the version for your operating system. CI builds with Quarto *1.9.38* (pinned in both CI configs), so use that version locally if a newer one renders differently.
2. **Verify Installation:** Open your terminal and run:
   ```bash
   quarto check
   ```

*(Optional)* If you are using VS Code, installing the **Quarto extension** is highly recommended for syntax highlighting and live previews.

## 🚀 Running the Presentation Locally

To work on the presentation and see your changes update in real-time, navigate to this directory in your terminal and run:

```bash
quarto preview index.qmd
```
This will spin up a local development server and open the presentation in your default web browser. Any changes you save to the `.qmd` or `style.css` files will instantly refresh the browser.

## 📦 Building for Production

### Option 1: Lean index.html

This will generate an `index.html` file alongside an `index_files/` directory: 

```bash
quarto render index.qmd
```

*Note: The `index_files/` directory contains all the heavy Reveal.js JavaScript and CSS dependencies. It is intentionally ignored by `.gitignore`.*

To automatically render the presentation and package it alongside all required files and directores, you can run

```bash
export.sh
```

### Option 2: Standalone index.html (works offline)

This embeds all necessary files and data directly into a single `index.html` that works fully offline, e.g. for a conference room without Wi-Fi. It sacrifices file size (~20 MB) for portability:

```bash
quarto render index.qmd --profile standalone
```

The `standalone` profile (`_quarto-standalone.yml`) turns on `embed-resources` and disables the chalkboard plugin, which cannot be embedded. Everything else (charts, diagrams, math, images) is bundled; only third-party embeds such as the YouTube and Datawrapper iframes still need a connection.

## 📁 Repository Structure

* `index.qmd`: The main Markdown source file containing all slide content, including the small inline `<script>` blocks that build each chart.
* `style.css`: Design tokens (colours, chart palette) and the reusable classes used by the slides (`.card`, `.grid3`, `.stat`, `.takeaway`, `.chart`, ...).
* `assets/`: All images, logos, and background graphics used in the deck.
  * `assets/js/deck.js`: Shared chart theme plus helpers that draw charts when their slide is first shown and step them with fragments.
  * `assets/js/responsive.js`: Fits the slide canvas to the screen (see below).
  * `assets/vendor/`: Locally bundled libraries ([Plotly](https://plotly.com/javascript/), [D3](https://d3js.org/), [img-comparison-slider](https://github.com/sneas/img-comparison-slider), [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator)) and the STIX Two Math font, so the deck never depends on a CDN.
* `references.bib`: BibTeX entries cited with `[@key]`; the bibliography is rendered at build time onto the References slide.
* `_quarto.yml` / `_quarto-standalone.yml`: Project defaults and the offline single-file profile.
* `export.sh`: Quick script for exporting all required assets into an `output.zip`.
* `tools/shot.mjs`: Dev-only screenshot helper for checking the rendered slides at any screen size (`node tools/shot.mjs --help`; needs `npm install` in `tools/`).

## 📐 Responsive Layout

The deck adapts to the screen it is shown on instead of letterboxing a fixed 1920×1080 canvas:

* *Landscape* keeps a 1920-wide canvas and grows taller on 16:10 and 4:3 screens; ultrawide screens get a wider canvas (up to 21:9).
* *Portrait* (phones, tablets) switches to a 1080-wide canvas and stacks columns and grids into a single column.
* Each slide shares any spare height evenly between its blocks, and charts scale with the canvas.

When designing a slide, use the layout classes (`.grid2`, `.grid-2-1`, `.columns`, `.chart`, ...) rather than fixed pixel sizes so it reflows. PDF export (`?print-pdf`) keeps the fixed 1920×1080 layout.

## 🎨 What's on the Menu

The deck doubles as a catalogue of elements to copy from, grouped into sections you can jump to from the agenda:

* *Text, layout & code:* cards, callouts, stat tiles with count-up numbers, step-by-step equations, tabsets, a quiz, a paper-style results table (best/second-best marking), code highlighting, citations and footnotes.
* *Images & media:* full-bleed images, framed figures with rounded corners, YouTube and web embeds, a local (offline) video, a before/after image slider, a logo wall.
* *Diagrams & planning:* Mermaid Gantt charts and flowcharts, a draggable D3 network.
* *Scientific plots for ML:* training curves, error bars, violins, quantiles, confusion matrix, ROC/PR, 3D embeddings, scaling laws, Pareto fronts, parallel coordinates.
* *Showing model outputs:* an LLM conversation that types itself out, token-level attribution, a qualitative results grid.
* *Presenting:* speaker tools, credits, a closing slide with a QR code to the hosted deck, and an appendix of backup slides and references that don't count towards the slide number.

Press `S` on any slide to see speaker notes explaining how it is built.

To add a chart, give it a container and register a builder; it is drawn the first time its slide is shown:

```html
<div id="my-chart" class="chart"></div>
<script>
Deck.chart("my-chart", (el) => {
  Plotly.newPlot(el, [{ x: [1, 2, 3], y: [3, 1, 2] }], Deck.layout({ yaxis: { title: { text: "Loss" } } }), Deck.config);
});
</script>
```
