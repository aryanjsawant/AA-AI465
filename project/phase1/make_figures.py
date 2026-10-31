"""
Figures for the Phase 1 summary and slides.

fig_esc_windows.png   how ESC cuts the sampling budget into windows
                      (example answers after Figure 1 of Li et al., 2024)
fig_paper_table1.png  GSM8K numbers read from Table 1 of Li et al., 2024
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": MUTED,
    "ytick.color": MUTED, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "axes.axisbelow": True, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.titlelocation": "left",
})


def fig_windows():
    answers = [3, 2, 3, 3, 4, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 4, 3, 2, 3, 4]
    w = 5
    fig, ax = plt.subplots(figsize=(9, 2.9))
    ax.set_xlim(-0.6, 23.4)
    ax.set_ylim(-2.0, 3.4)
    ax.axis("off")
    for row, (label, used) in enumerate((("SC", 20), ("ESC", 10))):
        y = 2.0 - row * 2.0
        ax.text(-0.5, y + 0.4, label, fontsize=13, fontweight="bold", va="center")
        for i, a in enumerate(answers):
            x = 1.0 + i + (i // w) * 0.5
            drawn = i < used
            color = (BLUE if row == 0 else ORANGE) if drawn else SURFACE
            ax.add_patch(FancyBboxPatch(
                (x, y), 0.8, 0.8, boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=color, edgecolor=color if drawn else GRID,
                linewidth=1.2, alpha=0.9 if drawn else 1))
            ax.text(x + 0.4, y + 0.4, str(a), ha="center", va="center",
                    fontsize=11, color="white" if drawn else GRID,
                    fontweight="bold")
    ax.text(1.0, 3.05, "20 samples in one request, then vote: answer 3",
            fontsize=9.5, color=INK2)
    ax.text(1.0, -0.3, "window 1:\nanswers differ,\nkeep sampling",
            fontsize=9, color=INK2, va="top")
    ax.text(6.5, -0.3, "window 2:\nall five agree,\nstop and return 3",
            fontsize=9, color=INK, va="top", fontweight="bold")
    ax.text(12.0, -0.3, "windows 3 and 4 are never requested:\n10 samples saved",
            fontsize=9, color=INK2, va="top")
    fig.savefig(os.path.join(FIG, "fig_esc_windows.png"), dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def fig_table1():
    models = ["GPT-4", "GPT-3.5-Turbo", "Llama-2 7b"]
    used = [7.98, 14.65, 31.21]        # ESC average samples, budget L = 40
    gain = [89.29 - 89.07, 85.67 - 84.82, 21.74 - 21.52]  # ESC minus L-hat-SC
    sc_acc = [89.29, 85.69, 21.75]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1))
    ax = axes[0]
    labels = ["%s\n(SC accuracy %.1f%%)" % (m, acc)
              for m, acc in zip(models, sc_acc)]
    bars = ax.barh(labels[::-1], used[::-1], height=0.55, color=ORANGE)
    for b, u in zip(bars, used[::-1]):
        ax.text(u + 0.6, b.get_y() + b.get_height() / 2,
                "%.1f  (%.0f%% saved)" % (u, 100 * (40 - u) / 40),
                va="center", fontsize=9)
    ax.set_xlim(0, 46)
    ax.set_xticks([0, 10, 20, 30, 40])
    ax.set_xlabel("Samples ESC used per question, out of a budget of 40 (GSM8K)")
    ax.set_title("The saving shrinks as the model gets weaker")
    ax.grid(axis="y", visible=False)

    ax = axes[1]
    bars = ax.bar(models, gain, width=0.5, color=ORANGE)
    for b, g in zip(bars, gain):
        ax.text(b.get_x() + b.get_width() / 2, g + 0.02, "+%.2f" % g,
                ha="center", fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Accuracy points")
    ax.set_title("ESC minus SC at the same sample budget\n(no variance reported)")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_paper_table1.png"), dpi=200,
                bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_windows()
    fig_table1()
    print("wrote", FIG)
