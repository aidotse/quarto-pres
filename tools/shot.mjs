// Screenshot rendered slides in headless Chromium, to check layout without a
// browser at hand. Render first (`quarto render index.qmd`), then e.g.:
//
//   node tools/shot.mjs                                  every slide at 1920x1080
//   node tools/shot.mjs results-table 12 --size 1920x1080,820x1180
//   node tools/shot.mjs --list                           numbers, ids and titles
//
// Slides are given by id or by number (DOM order, so uncounted appendix slides
// are included). Images go to shots/<W>x<H>/<nn>-<id>.png. Exits non-zero if
// the page logged a JavaScript error.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const USAGE = `usage: node tools/shot.mjs [slide ...] [options]

  slide             slide id (results-table) or number (1 = title); default: all
  --size WxH,...    viewport sizes, default 1920x1080 (portrait tablet: 820x1180)
  --frags all|none  show every fragment (default) or none
  --wait MS         settle time per slide for charts and animations, default 1500
  --out DIR         output directory, default shots/
  --offline         block all network requests and report what was blocked
  --list            print slide numbers, ids and titles instead of screenshots
  --html PATH|URL   deck to open, default index.html`;

const opts = { size: "1920x1080", frags: "all", wait: "1500", out: "shots", html: null };
const flags = new Set(), targets = [];
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "-h" || a === "--help") { console.log(USAGE); process.exit(0); }
  else if (a === "--offline" || a === "--list") flags.add(a.slice(2));
  else if (a.startsWith("--") && a.slice(2) in opts) opts[a.slice(2)] = argv[++i];
  else if (a.startsWith("--")) { console.error(`unknown option ${a}\n\n${USAGE}`); process.exit(2); }
  else targets.push(a);
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = opts.html ?? path.join(root, "index.html");
const url = /^https?:/.test(html) ? html : pathToFileURL(path.resolve(html)).href;
if (url.startsWith("file:") && !fs.existsSync(fileURLToPath(url))) {
  console.error(`${html} not found; run \`quarto render index.qmd\` first`);
  process.exit(2);
}
const sizes = opts.size.split(",").map((s) => s.split("x").map(Number));

const browser = await chromium.launch();
const errors = [], blocked = new Set();
let failed = false;

for (const [width, height] of sizes) {
  const page = await browser.newPage({ viewport: { width, height } });
  page.on("pageerror", (e) => errors.push(`${width}x${height} pageerror: ${e.message}`));
  page.on("console", (m) => {
    // Blocked requests surface as console errors; they are reported separately.
    if (m.type() !== "error" || /net::ERR_FAILED/.test(m.text())) return;
    // A missing file only says "Failed to load resource"; name it.
    const where = /Failed to load/.test(m.text()) ? ` (${m.location().url.replace(/^.*?\/(?=assets\/|index_files\/|style\.css)/, "")})` : "";
    errors.push(`${width}x${height} console: ${m.text()}${where}`);
  });
  if (flags.has("offline")) {
    await page.route("**/*", (r) => {
      const u = r.request().url();
      if (/^(file|data|blob):/.test(u)) return r.continue();
      blocked.add(new URL(u).origin);
      return r.abort();
    });
  }
  await page.goto(url);
  await page.waitForFunction(() => window.Reveal && Reveal.isReady());

  // Leaf slides in document order (vertical stacks contain nested sections).
  const slides = await page.evaluate(() =>
    [...document.querySelectorAll(".reveal .slides section:not(.stack)")].map((s) => ({
      id: s.id,
      title: (s.querySelector("h1, h2")?.textContent ?? "").trim().replace(/\s+/g, " "),
      uncounted: s.dataset.visibility === "uncounted",
    })),
  );

  if (flags.has("list")) {
    slides.forEach((s, i) => console.log(`${String(i + 1).padStart(3)}  ${s.id.padEnd(36)} ${s.title}${s.uncounted ? "  (uncounted)" : ""}`));
    await page.close();
    break;
  }

  const picked = targets.length ? targets : slides.map((_, i) => String(i + 1));
  const dir = path.join(opts.out, `${width}x${height}`);
  fs.mkdirSync(dir, { recursive: true });

  for (const t of picked) {
    const n = /^\d+$/.test(t) ? Number(t) : slides.findIndex((s) => s.id === t) + 1;
    if (n < 1 || n > slides.length) { console.error(`no slide "${t}" (try --list)`); failed = true; continue; }
    await page.evaluate(([n, all]) => {
      const s = document.querySelectorAll(".reveal .slides section:not(.stack)")[n - 1];
      const { h, v } = Reveal.getIndices(s);
      Reveal.slide(h, v, all ? 999 : -1);
    }, [n, opts.frags === "all"]);
    await page.waitForTimeout(Number(opts.wait));
    const file = path.join(dir, `${String(n).padStart(2, "0")}-${slides[n - 1].id || "slide"}.png`);
    await page.screenshot({ path: file });
    console.log(file);
  }
  await page.close();
}
await browser.close();

if (blocked.size) console.log(`blocked (offline): ${[...blocked].join(" ")}`);
if (errors.length) console.error(errors.join("\n"));
process.exit(errors.length || failed ? 1 : 0);
