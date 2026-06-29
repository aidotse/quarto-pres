# quarto-pres

Pristine presentations with [Quarto](https://quarto.org/) and [Reveal.js](https://revealjs.com/).

## 🛠️ Prerequisites

To render or edit this presentation, you will need to install Quarto on your local machine.

1. **Download Quarto:** Go to the [Quarto Downloads page](https://quarto.org/docs/get-started/) and install the version for your operating system.
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

### Option 2: Standalone index.html

This embeds all necessary files and data directly into the `index.html` file itself. It sacrifices file size for portability:

```bash
quarto render index.qmd -M embed-resources:true
```

## 📁 Repository Structure

* `index.qmd`: The main Markdown source file containing all slide content and layout code.
* `style.css`: Custom CSS overrides for Reveal.js and specific slide layouts.
* `assets/`: Contains all images, logos, and background graphics used in the deck.
* `export.sh`: Quick script for exporting all required assets into an `output.zip`.
