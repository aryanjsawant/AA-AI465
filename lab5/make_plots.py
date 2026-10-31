"""
Experiment 5 - figures.

Imports the experiment modules directly and re-runs the same functions the
console programs call, so every number plotted here is the number printed in
outputs/, not a transcription of it.

Figures produced in outputs/:
  exp5_fig1_comparison.png   the three configurations by accuracy and by calls
  exp5_fig2_tallies.png      the per-question vote tally at k=7
  exp5_fig3_k_sweep.png      accuracy and total calls against k
  exp5_fig4_abstention.png   coverage vs accuracy-on-answered for two margins
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from questions import QUESTIONS
from exp5_cot_selfconsistency import (
    run,
    generate_trace,
    extract_answer,
    majority_vote,
    canonical_number,
    DEFAULT_K,
    DEFAULT_SEED,
)
from exp5_exercises import (
    K_VALUES,
    SEEDS,
    MARGINS,
    run_self_consistency,
    vote_with_abstention,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")
os.makedirs(OUTDIR, exist_ok=True)

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 9
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

# Categorical slots 1-3 of the validated palette (blue, orange, aqua); assigned
# in fixed order and never cycled. Every chart also carries printed values, so
# identity is never colour alone.
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"

CONFIGS = ["direct", "cot_greedy", "cot_self_consistency"]
CONFIG_LABELS = {
    "direct": "Direct",
    "cot_greedy": "CoT greedy",
    "cot_self_consistency": "CoT self-consistency\n(k=%d)" % DEFAULT_K,
}
CONFIG_COLORS = {"direct": BLUE, "cot_greedy": ORANGE, "cot_self_consistency": AQUA}


def _save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[OK] saved %s" % name)


def _grid(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def fig1_comparison(results):
    """Accuracy and cost are different measures, so they get one panel each
    rather than a second y-axis on one panel."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8))
    labels = [CONFIG_LABELS[c] for c in CONFIGS]
    colors = [CONFIG_COLORS[c] for c in CONFIGS]

    accs = [results[c]["accuracy"] for c in CONFIGS]
    bars = ax1.bar(labels, accs, color=colors, width=0.55)
    for bar, acc, c in zip(bars, accs, CONFIGS):
        r = results[c]
        ax1.text(bar.get_x() + bar.get_width() / 2, acc + 0.02,
                 "%.2f\n(%d/%d)" % (acc, r["correct_count"], r["num_questions"]),
                 ha="center", va="bottom", fontsize=8.5, color=INK)
    ax1.set_ylim(0, 1.18)
    ax1.set_ylabel("Accuracy")
    ax1.set_title("Accuracy", fontsize=10, color=INK, pad=8)
    _grid(ax1)

    calls = [results[c]["total_calls"] for c in CONFIGS]
    bars = ax2.bar(labels, calls, color=colors, width=0.55)
    for bar, n in zip(bars, calls):
        ax2.text(bar.get_x() + bar.get_width() / 2, n + max(calls) * 0.02,
                 str(n), ha="center", va="bottom", fontsize=8.5, color=INK)
    ax2.set_ylim(0, max(calls) * 1.18)
    ax2.set_ylabel("Model calls")
    ax2.set_title("Cost (model calls)", fontsize=10, color=INK, pad=8)
    _grid(ax2)

    fig.suptitle("The three configurations: what the extra calls buy",
                 fontsize=11.5, color=INK, y=1.02)
    _save(fig, "exp5_fig1_comparison.png")


def fig2_tallies(results):
    """Stacked votes per question at k=7, split by whether the votes went to the
    gold answer. Colour follows the answer's correctness, not its rank, so the
    one question where the wrong answer wins the vote reads correctly."""
    sc = {pq["id"]: pq for pq in results["cot_self_consistency"]["per_question"]}
    greedy = {pq["id"]: pq for pq in results["cot_greedy"]["per_question"]}

    ids = [q["id"] for q in QUESTIONS]
    gold_votes, wrong_votes, lost = [], [], []
    for qid in ids:
        pq = sc[qid]
        tally = pq["tally"] or {}
        g = tally.get(pq["gold"], 0)
        gold_votes.append(g)
        wrong_votes.append(sum(tally.values()) - g)
        lost.append(not pq["correct"])

    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    x = range(len(ids))
    # 2px surface gap between the stacked segments.
    ax.bar(x, gold_votes, color=AQUA, width=0.6,
           label="Votes for the gold answer")
    ax.bar(x, wrong_votes, bottom=[g + 0.06 for g in gold_votes], color=ORANGE,
           width=0.6, label="Votes for a wrong answer")

    for i, (g, w, bad) in enumerate(zip(gold_votes, wrong_votes, lost)):
        if g:
            ax.text(i, g / 2, str(g), ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold")
        if w:
            ax.text(i, g + w / 2 + 0.06, str(w), ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")
        if bad:
            ax.text(i, g + w + 0.25, "wrong answer\nwins the vote", ha="center",
                    va="bottom", fontsize=7, color=ORANGE, fontweight="bold",
                    linespacing=1.3)

    ax.set_xticks(list(x))
    ax.set_xticklabels(ids, fontsize=8.5)
    # Greedy's per-question outcome on its own row under the axis, so it cannot
    # collide with the neighbouring tick label.
    for i, qid in enumerate(ids):
        ok = greedy[qid]["correct"]
        ax.annotate("greedy\n%s" % ("OK" if ok else "WRONG"),
                    xy=(i, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -26), textcoords="offset points",
                    ha="center", va="top", fontsize=7,
                    color=MUTED if ok else ORANGE,
                    fontweight="normal" if ok else "bold", linespacing=1.3)

    ax.set_ylabel("Votes (of k=%d traces)" % DEFAULT_K)
    ax.set_ylim(0, DEFAULT_K + 1.6)
    ax.set_title("Vote tally per question at k=%d, seed=%d\n"
                 "(bars fall short of %d where a trace was unparsable)"
                 % (DEFAULT_K, DEFAULT_SEED, DEFAULT_K), fontsize=10.5,
                 color=INK, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.22), ncol=2)
    _grid(ax)
    _save(fig, "exp5_fig2_tallies.png")


def fig3_k_sweep():
    """Exercise 1: mean accuracy over the seed set, and total calls, against k."""
    mean_accs, all_accs, total_calls = [], [], []
    for k in K_VALUES:
        accs = [run_self_consistency(QUESTIONS, k, seed)[0] for seed in SEEDS]
        all_accs.append(accs)
        mean_accs.append(sum(accs) / len(accs))
        total_calls.append(k * len(QUESTIONS) * len(SEEDS))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8))
    xs = range(len(K_VALUES))

    # Per-seed points behind the mean line, so the spread that makes the curve
    # non-monotonic is visible rather than hidden by the average.
    for i, accs in enumerate(all_accs):
        ax1.scatter([i] * len(accs), accs, s=26, color=BLUE, alpha=0.35,
                    edgecolors="none", zorder=2)
    ax1.plot(xs, mean_accs, color=BLUE, linewidth=2, marker="o", markersize=7,
             markeredgecolor="white", markeredgewidth=1.5, zorder=3,
             label="Mean over %d seeds" % len(SEEDS))
    for i, a in enumerate(mean_accs):
        ax1.annotate("%.2f" % a, (i, a), textcoords="offset points",
                     xytext=(0, 11), ha="center", fontsize=8, color=INK)
    ax1.set_xticks(list(xs))
    ax1.set_xticklabels([str(k) for k in K_VALUES])
    ax1.set_xlabel("k (sampled traces per question)")
    ax1.set_ylabel("Accuracy")
    ax1.set_ylim(0, 1.15)
    ax1.set_title("Accuracy against k", fontsize=10, color=INK, pad=8)
    ax1.legend(frameon=False, fontsize=8, loc="lower right")
    _grid(ax1)

    ax2.plot(xs, total_calls, color=ORANGE, linewidth=2, marker="o", markersize=7,
             markeredgecolor="white", markeredgewidth=1.5)
    for i, n in enumerate(total_calls):
        ax2.annotate(str(n), (i, n), textcoords="offset points",
                     xytext=(0, 11), ha="center", fontsize=8, color=INK)
    ax2.set_xticks(list(xs))
    ax2.set_xticklabels([str(k) for k in K_VALUES])
    ax2.set_xlabel("k (sampled traces per question)")
    ax2.set_ylabel("Total model calls (%d seeds)" % len(SEEDS))
    ax2.set_ylim(0, max(total_calls) * 1.18)
    # k is plotted on evenly spaced categorical ticks, so this line bends even
    # though calls are exactly k x questions x seeds.
    ax2.set_title("Cost against k", fontsize=10, color=INK, pad=8)
    _grid(ax2)

    fig.suptitle("Exercise 1 - accuracy flattens while cost keeps climbing",
                 fontsize=11.5, color=INK, y=1.02)
    _save(fig, "exp5_fig3_k_sweep.png")


def fig4_abstention():
    """Exercise 2: coverage and accuracy-on-answered at each margin."""
    coverages, accuracies = [], []
    for margin in MARGINS:
        answered = 0
        correct = 0
        for q in QUESTIONS:
            gold = canonical_number(q["gold"])
            answers = []
            for i in range(DEFAULT_K):
                trace_text, _ = generate_trace(q["id"], "sample",
                                               sample_index=i, seed=DEFAULT_SEED)
                ans = extract_answer(trace_text)
                if ans is not None:
                    answers.append(ans)
            _w, tally = majority_vote(answers)
            decision, status = vote_with_abstention(tally, margin)
            if status == "answered":
                answered += 1
                correct += int(decision == gold)
        coverages.append(answered / len(QUESTIONS))
        accuracies.append(correct / answered if answered else 0.0)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    x = range(len(MARGINS))
    width = 0.34
    b1 = ax.bar([i - width / 2 - 0.01 for i in x], coverages, width=width,
                color=BLUE, label="Coverage (questions answered)")
    b2 = ax.bar([i + width / 2 + 0.01 for i in x], accuracies, width=width,
                color=AQUA, label="Accuracy on the answered subset")
    for bars, vals in ((b1, coverages), (b2, accuracies)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, "%.2f" % v,
                    ha="center", va="bottom", fontsize=8.5, color=INK)

    ax.set_xticks(list(x))
    ax.set_xticklabels(["margin = %d vote%s" % (m, "" if m == 1 else "s")
                        for m in MARGINS])
    ax.set_ylabel("Proportion")
    ax.set_ylim(0, 1.2)
    ax.set_title("Exercise 2 - abstention trades coverage for precision\n"
                 "(k=%d, seed=%d)" % (DEFAULT_K, DEFAULT_SEED),
                 fontsize=10.5, color=INK, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.12), ncol=2)
    _grid(ax)
    _save(fig, "exp5_fig4_abstention.png")


def main():
    print("Generating figures for Lab 5 ...")
    results = {c: run(c, k=DEFAULT_K, seed=DEFAULT_SEED) for c in CONFIGS}
    fig1_comparison(results)
    fig2_tallies(results)
    fig3_k_sweep()
    fig4_abstention()
    print("Figures written to %s" % OUTDIR)


if __name__ == "__main__":
    main()
