"""Static matplotlib figures for the "Libraries Compared" slides.

Generates the demo data once and writes it to assets/compare/data.js, so the
Plotly and ECharts versions on those slides plot exactly the same numbers,
then renders the matplotlib versions as SVGs next to it. The deck itself never
runs Python; re-run this only when the data or the styling changes:

    python -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
    .venv/bin/python tools/compare_charts.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "compare"

# Design tokens from style.css (:root)
SERIES = ["#3987e5", "#d95926", "#199e70"]
ACCENT, SURFACE = "#FECB00", "#121F2B"
INK, BODY, MUTED = "#ffffff", "#cecece", "#9aa5b1"
GRID, AXIS = (1, 1, 1, 0.07), (1, 1, 1, 0.22)

# Figures are drawn at the size they are shown on the 1920x1080 canvas, so
# font sizes match the interactive charts pixel for pixel.
W_PX, H_PX, DPI = 540, 560, 100
PX = 72 / DPI


def training_data():
    rng = np.random.default_rng(7)
    steps = np.arange(0, 60001, 500)

    def runs(a, b, k, drift, noise):
        trend = a + b * np.exp(-steps / k) + drift * np.maximum(0, steps - 32000) / 28000
        jitter = rng.normal(0, noise, (5, steps.size)) * (1 + 3 * np.exp(-steps / 6000))
        return trend + jitter

    def stats(r):
        return np.round(r.mean(0), 4).tolist(), np.round(r.std(0), 4).tolist()

    train, val = stats(runs(1.48, 2.7, 7000, 0, 0.018)), stats(runs(1.70, 2.5, 7500, 0.14, 0.03))
    best = int(np.argmin(val[0]))
    return {
        "steps": steps.tolist(),
        "series": [
            {"name": "Train", "mean": train[0], "std": train[1]},
            {"name": "Validation", "mean": val[0], "std": val[1]},
        ],
        "best": {"step": int(steps[best]), "loss": val[0][best]},
    }


BARS = {
    "benchmarks": ["MMLU", "GSM8K", "HumanEval", "ARC-C"],
    "models": [
        {"name": "Baseline 7B", "y": [61.2, 48.5, 33.1, 72.4], "e": [0.7, 1.5, 1.9, 0.9]},
        {"name": "+ Retrieval", "y": [66.0, 51.2, 35.4, 76.9], "e": [0.6, 1.3, 2.1, 0.8]},
        {"name": "+ Self-reflection", "y": [69.4, 60.3, 44.8, 80.1], "e": [0.5, 1.2, 1.7, 0.7]},
    ],
}



def style():
    plt.rcParams.update({
        "svg.fonttype": "none",  # keep text as text, in the deck's font
        "font.family": "sans-serif",
        "font.sans-serif": ["Office Sans", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 18 * PX,
        "text.color": BODY,
        "axes.facecolor": "none",
        "figure.facecolor": "none",
        "savefig.facecolor": "none",
        "axes.edgecolor": AXIS,
        "axes.labelcolor": BODY,
        "axes.labelsize": 19 * PX,
        "axes.labelpad": 10 * PX,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 1,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 17 * PX,
        "ytick.labelsize": 17 * PX,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.major.pad": 8 * PX,
        "ytick.major.pad": 8 * PX,
        "legend.frameon": False,
        "legend.fontsize": 18 * PX,
        "svg.hashsalt": "deck",  # stable ids, so re-running gives identical files
    })


def legend_on_top(ax, ncol):
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol, borderaxespad=0.3,
              handlelength=1.2, columnspacing=1.2, labelcolor=BODY)


def plot_training(d):
    fig, ax = plt.subplots(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, layout="constrained")
    steps = np.array(d["steps"])
    for s, color in zip(d["series"], SERIES):
        m, sd = np.array(s["mean"]), np.array(s["std"])
        ax.fill_between(steps, m - sd, m + sd, color=color, alpha=0.16, linewidth=0)
        ax.plot(steps, m, color=color, linewidth=3.5 * PX, label=s["name"])
    b = d["best"]
    ax.plot(b["step"], b["loss"], "o", markersize=14 * PX, color=ACCENT,
            markeredgecolor=SURFACE, markeredgewidth=3 * PX, zorder=5)
    ax.annotate(f"Best checkpoint\nstep {b['step'] / 1000:.1f}k · loss {b['loss']:.3f}",
                (b["step"], b["loss"]), xytext=(0, 70 * PX), textcoords="offset points",
                ha="center", color=INK, fontsize=17 * PX, fontweight="bold",
                arrowprops={"arrowstyle": "-", "color": ACCENT, "linewidth": 2 * PX})
    ax.set(xlim=(0, 60000), ylim=(1.3, 4.6), xlabel="Training step", ylabel="Cross-entropy loss")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k" if v else "0"))
    legend_on_top(ax, 2)
    return fig


def plot_bars(d):
    fig, ax = plt.subplots(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI, layout="constrained")
    x, n = np.arange(len(d["benchmarks"])), len(d["models"])
    width = 0.78 / n
    for k, (m, color) in enumerate(zip(d["models"], SERIES)):
        ax.bar(x + (k - (n - 1) / 2) * width, m["y"], width * 0.92, yerr=m["e"], color=color,
               label=m["name"], error_kw={"ecolor": (1, 1, 1, 0.6), "elinewidth": 2 * PX, "capsize": 4, "capthick": 2 * PX})
    ax.set(ylim=(0, 100), ylabel="Accuracy (%)", xticks=x)
    ax.set_xticklabels(d["benchmarks"], color=BODY)
    ax.grid(axis="x", visible=False)
    legend_on_top(ax, 1)
    return fig


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"training": training_data(), "bars": BARS}
    (OUT / "data.js").write_text(
        "/* Generated by tools/compare_charts.py; shared by the Plotly, ECharts and matplotlib versions. */\n"
        f"window.CompareData = {json.dumps(data, separators=(',', ':'))};\n")
    style()
    for name, fig in [("training", plot_training(data["training"])), ("bars", plot_bars(data["bars"]))]:
        fig.savefig(OUT / f"{name}.svg", metadata={"Date": None})
        plt.close(fig)
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
