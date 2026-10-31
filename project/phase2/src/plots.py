"""
Step 3: draw the figures from results/summary.json.

    python src/plots.py

Writes figures/fig1_accuracy_vs_cost.png, fig2_stopping.png,
fig3_cost.png and fig4_window_ablation.png.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e6e5e1"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # SC, ESC, AC

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.family": "DejaVu Sans",
    "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left",
})


def load():
    with open(os.path.join(ROOT, "results", "summary.json"), encoding="utf-8") as f:
        return json.load(f)


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/" + name)


def fig_accuracy_vs_cost(S):
    agg, L = S["agg"], S["max_samples"]
    esc, ac = agg[S["esc_name"]], agg["AC (Beta 0.95, L=%d)" % L]
    ks = list(range(1, L + 1))
    mean = [agg["SC-%d" % k]["correct"][0] for k in ks]
    std = [agg["SC-%d" % k]["correct"][1] for k in ks]

    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.fill_between(ks, [m - s for m, s in zip(mean, std)],
                    [m + s for m, s in zip(mean, std)], color=BLUE, alpha=0.15,
                    linewidth=0)
    ax.plot(ks, mean, color=BLUE, linewidth=2, marker="o", markersize=3.5,
            label="Self-consistency, fixed k (band = ±1 std over runs)")
    ax.axhline(S["greedy"]["correct"], color=MUTED, linewidth=1.2, linestyle="--",
               label="CoT greedy, 1 call")
    for a, color, marker, label in ((esc, ORANGE, "D", "ESC (w=%d)" % S["window"]),
                                    (ac, AQUA, "s", "Adaptive-Consistency")):
        ax.errorbar(a["samples"][0], a["correct"][0], yerr=a["correct"][1],
                    xerr=a["samples"][1], color=color, marker=marker,
                    markersize=8, capsize=3, linewidth=1.5, linestyle="none",
                    markeredgecolor=SURFACE, markeredgewidth=1.5, label=label,
                    zorder=5)
    rs = S["random_stop_runs"]
    ax.plot(esc["samples"][0], sum(rs) / len(rs), marker="x", color=INK2,
            markersize=8, markeredgewidth=2, linestyle="none",
            label="Random stopping, ESC's budgets (ablation)", zorder=4)
    ax.set_xlabel("Samples per question (mean)")
    ax.set_ylabel("Exact-match accuracy (%)")
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_title("Accuracy against sampling budget: GSM8K subset (n=%d), %d runs"
                 % (S["n_questions"], len(S["runs"])))
    ax.legend(frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.17), ncol=2)
    save(fig, "fig1_accuracy_vs_cost.png")


def fig_cost(S):
    agg, L = S["agg"], S["max_samples"]
    k_hi = S["k_matched"][1]
    names = [("SC-%d\n(matched)" % k_hi, "SC-%d" % k_hi, BLUE),
             ("SC-%d\n(full)" % L, "SC-%d" % L, BLUE),
             ("ESC", S["esc_name"], ORANGE),
             ("AC", "AC (Beta 0.95, L=%d)" % L, AQUA)]
    panels = [("Samples per question", lambda a: a["samples"]),
              ("Total tokens per question",
               lambda a: (a["prompt_tokens"][0] + a["completion_tokens"][0],
                          (a["prompt_tokens"][1] ** 2
                           + a["completion_tokens"][1] ** 2) ** 0.5)),
              ("Sequential rounds per question", lambda a: a["rounds"]),
              ("Latency per question (s)", lambda a: a["latency_s"])]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.1))
    for ax, (title, get) in zip(axes, panels):
        vals = [get(agg[key]) for _, key, _ in names]
        bars = ax.bar(range(len(names)), [v[0] for v in vals], width=0.6,
                      yerr=[v[1] for v in vals], capsize=3,
                      color=[c for _, _, c in names],
                      error_kw={"ecolor": INK2, "elinewidth": 1})
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v[0] + v[1],
                    ("%.0f" if v[0] >= 100 else "%.1f") % v[0],
                    ha="center", va="bottom", fontsize=8.5, color=INK)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([n for n, _, _ in names], fontsize=8)
        ax.set_title(title, fontsize=9.5)
        ax.grid(axis="x", visible=False)
        ax.margins(y=0.15)
    fig.suptitle("Cost of each strategy (mean over runs, bars = ±1 std)",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig3_cost.png")


def fig_stopping(S):
    stats = S["stop_stats"]
    keys = list(stats)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    shares = [stats[k]["share"] for k in keys]
    bars = ax.bar(range(len(keys)), shares, width=0.6,
                  color=[ORANGE] * (len(keys) - 1) + [MUTED])
    for b, k in zip(bars, keys):
        acc = stats[k]["accuracy"]
        label = "%.0f%%" % stats[k]["share"]
        if acc is not None:
            label += "\n(%.0f%% correct)" % acc
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, label,
                ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(["stopped in\n" + k if k != "no stop"
                        else "never stopped\n(all %d samples)" % S["max_samples"]
                        for k in keys], fontsize=8.5)
    ax.set_ylabel("Share of question-runs (%)")
    ax.set_title("Where ESC stops, and how often the stop is right")
    ax.grid(axis="x", visible=False)
    ax.margins(y=0.25)
    save(fig, "fig2_stopping.png")


def fig_window(S):
    agg = S["agg"]
    ws = [2, 3, 4, 5, 10]
    key = lambda w: S["esc_name"] if w == S["window"] else "ESC w=%d" % w
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.3))
    for ax, metric, title in ((axes[0], "correct", "Accuracy (%)"),
                              (axes[1], "samples", "Samples per question")):
        m = [agg[key(w)][metric][0] for w in ws]
        s = [agg[key(w)][metric][1] for w in ws]
        ax.errorbar(range(len(ws)), m, yerr=s, color=ORANGE, marker="D",
                    markersize=6, linewidth=2, capsize=3)
        ref = agg["SC-%d" % S["max_samples"]][metric][0]
        ax.axhline(ref, color=BLUE, linewidth=1.2, linestyle="--")
        ax.text(len(ws) - 1, ref, " SC-%d" % S["max_samples"], color=INK2,
                fontsize=8.5, va="bottom", ha="right")
        ax.set_xticks(range(len(ws)))
        ax.set_xticklabels(ws)
        ax.set_xlabel("ESC window size w")
        ax.set_title(title, fontsize=10)
    fig.suptitle("Window-size ablation (max %d samples)" % S["max_samples"],
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig4_window_ablation.png")


if __name__ == "__main__":
    S = load()
    fig_accuracy_vs_cost(S)
    fig_stopping(S)
    fig_cost(S)
    fig_window(S)
