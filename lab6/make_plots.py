"""
Experiment 6 - figures.

Imports the experiment modules and plots the values their own functions
return, so every number drawn here is a number the console programs print.

Figures produced in outputs/:
  exp6_fig1_team_vs_generalist.png  task success and model calls, side by side
  exp6_fig2_per_task.png            per-task success, team against generalist
  exp6_fig3_violations.png          role violations by role and by kind
  exp6_fig4_ablation.png            Exercise 1 ablations: success vs cost
  exp6_fig5_injection.png           Exercise 2: prompt-only vs enforced
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from docstore import TASKS
from exp6_role_agents import SEEDS, evaluate
from exp6_exercises import CASES, attempt_case

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")
os.makedirs(OUTDIR, exist_ok=True)

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 9
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

# Categorical slots 1-3 of the validated palette, assigned in fixed order
# and never cycled. Every chart also prints its values, so identity is
# never carried by colour alone.
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"


def _save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[OK] saved %s" % name)


def _grid(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _int_yticks(ax):
    """Counts are whole numbers; keep the axis from offering halves."""
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))


def fig1_team_vs_generalist(team, gen):
    """Success and cost are different measures, so one panel each rather
    than two y-axes on one."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8))
    labels = ["Role-based team", "Single generalist"]
    colors = [BLUE, ORANGE]

    vals = [team["success"], gen["success"]]
    bars = ax1.bar(labels, vals, color=colors, width=0.5)
    for bar, v, r in zip(bars, vals, (team, gen)):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.02,
                 "%.3f\n(%d/%d)" % (v, r["passes"], r["runs"]),
                 ha="center", va="bottom", fontsize=8.5, color=INK)
    ax1.set_ylim(0, 1.18)
    ax1.set_ylabel("Task success")
    ax1.set_title("Task success", fontsize=10, color=INK, pad=8)
    _grid(ax1)

    calls = [team["total_calls"], gen["total_calls"]]
    bars = ax2.bar(labels, calls, color=colors, width=0.5)
    for bar, n in zip(bars, calls):
        ax2.text(bar.get_x() + bar.get_width() / 2, n + max(calls) * 0.02,
                 str(n), ha="center", va="bottom", fontsize=8.5, color=INK)
    ax2.set_ylim(0, max(calls) * 1.18)
    ax2.set_ylabel("Model calls")
    ax2.set_title("Cost (model calls)", fontsize=10, color=INK, pad=8)
    _grid(ax2)

    fig.suptitle("The team buys accuracy with model calls (%d seeds x %d "
                 "tasks)" % (len(SEEDS), len(TASKS)),
                 fontsize=11.5, color=INK, y=1.02)
    _save(fig, "exp6_fig1_team_vs_generalist.png")


def fig2_per_task(team, gen):
    """Per-task success for both systems, paired so the tasks the team
    rescues are visible one by one."""
    ids = [t["id"] for t in TASKS]
    t_vals = [sum(team["per_task"][i]) for i in ids]
    g_vals = [sum(gen["per_task"][i]) for i in ids]
    n = len(SEEDS)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = range(len(ids))
    width = 0.38
    b1 = ax.bar([i - width / 2 - 0.01 for i in x], t_vals, width=width,
                color=BLUE, label="Role-based team")
    b2 = ax.bar([i + width / 2 + 0.01 for i in x], g_vals, width=width,
                color=ORANGE, label="Single generalist")
    for bars, vals in ((b1, t_vals), (b2, g_vals)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.15, str(v),
                    ha="center", va="bottom", fontsize=8, color=INK)

    ax.set_xticks(list(x))
    ax.set_xticklabels(ids)
    ax.set_ylabel("Tasks passed (of %d seeds)" % n)
    ax.set_ylim(0, n + 1.8)
    ax.set_title("Per-task success over %d seeds" % n, fontsize=10.5,
                 color=INK, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=2)
    _grid(ax)
    _int_yticks(ax)
    _save(fig, "exp6_fig2_per_task.png")


def fig3_violations(team):
    """Who violates, and what kind of rule they break. Both panels count the
    same 27 blocked attempts, split two ways."""
    by_role = team["violations"].by_role()
    by_kind = team["violations"].by_kind()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6))

    roles = sorted(by_role, key=lambda r: -by_role[r])
    vals = [by_role[r] for r in roles]
    bars = ax1.bar(roles, vals, color=BLUE, width=0.55)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + max(vals) * 0.02,
                 str(v), ha="center", va="bottom", fontsize=8.5, color=INK)
    ax1.set_ylim(0, max(vals) * 1.2)
    ax1.set_ylabel("Blocked attempts")
    ax1.set_title("By role", fontsize=10, color=INK, pad=8)
    _grid(ax1)
    _int_yticks(ax1)

    kinds = sorted(by_kind, key=lambda k: -by_kind[k])
    vals2 = [by_kind[k] for k in kinds]
    bars = ax2.bar(kinds, vals2, color=AQUA, width=0.55)
    for bar, v in zip(bars, vals2):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + max(vals2) * 0.02,
                 str(v), ha="center", va="bottom", fontsize=8.5, color=INK)
    ax2.set_ylim(0, max(vals2) * 1.2)
    ax2.set_ylabel("Blocked attempts")
    ax2.set_title("By kind of rule broken", fontsize=10, color=INK, pad=8)
    _grid(ax2)
    _int_yticks(ax2)

    fig.suptitle("Role violations caught by validate() (%d in total; the "
                 "generalist records 0)" % team["violations"].count(),
                 fontsize=11.5, color=INK, y=1.02)
    _save(fig, "exp6_fig3_violations.png")


def fig4_ablation(results):
    """Exercise 1: each configuration's success against the calls it spends.
    Plotted as paired bars rather than a scatter so both measures stay
    readable against a common task-count baseline."""
    labels = ["full team", "no Reviewer", "Researcher+Writer merged",
              "generalist"]
    short = ["Full team", "No Reviewer", "R+W merged", "Generalist"]
    succ = [results[l]["success"] for l in labels]
    calls = [results[l]["total_calls"] for l in labels]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.8))

    bars = ax1.bar(short, succ, color=BLUE, width=0.55)
    for bar, v, l in zip(bars, succ, labels):
        r = results[l]
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.02,
                 "%.3f\n(%d/%d)" % (v, r["passes"], r["runs"]),
                 ha="center", va="bottom", fontsize=8, color=INK)
    ax1.set_ylim(0, 1.2)
    ax1.set_ylabel("Task success")
    ax1.set_title("Task success", fontsize=10, color=INK, pad=8)
    ax1.tick_params(axis="x", labelsize=8)
    _grid(ax1)

    bars = ax2.bar(short, calls, color=ORANGE, width=0.55)
    for bar, v in zip(bars, calls):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + max(calls) * 0.02,
                 str(v), ha="center", va="bottom", fontsize=8, color=INK)
    ax2.set_ylim(0, max(calls) * 1.2)
    ax2.set_ylabel("Model calls")
    ax2.set_title("Cost (model calls)", fontsize=10, color=INK, pad=8)
    ax2.tick_params(axis="x", labelsize=8)
    _grid(ax2)

    fig.suptitle("Exercise 1 - removing the Reviewer costs accuracy; "
                 "merging Researcher and Writer mostly costs nothing",
                 fontsize=11, color=INK, y=1.02)
    _save(fig, "exp6_fig4_ablation.png")


def fig5_injection():
    """Exercise 2: the outcome of each injected instruction under the two
    regimes. The data is one of two states per cell, so it is drawn as a
    labelled status grid rather than as bars of height 0 or 1."""
    rows = []
    for case in CASES:
        _bp, ep = attempt_case(case, enforce=False)
        _be, ee = attempt_case(case, enforce=True)
        rows.append((case, int(ep), int(ee)))

    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    ax.set_xlim(0, 2)
    ax.set_ylim(0, len(rows))
    ax.axis("off")

    cols = ["Permissions in the prompt only", "validate() enforcing"]
    for j, label in enumerate(cols):
        ax.text(j + 0.5, len(rows) + 0.18, label, ha="center", va="bottom",
                fontsize=9, color=INK, fontweight="bold")

    for i, (case, ep, ee) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.text(-0.04, y + 0.5, "%s  %s" % (case["id"], case["name"]),
                ha="right", va="center", fontsize=8.5, color=INK)
        ax.text(-0.04, y + 0.17, "violates: %s" % case["kind"], ha="right",
                va="center", fontsize=7.5, color=MUTED)
        for j, took in enumerate((ep, ee)):
            # 2px surface gap between adjacent cells.
            ax.add_patch(plt.Rectangle((j + 0.012, y + 0.08), 0.976, 0.84,
                                       facecolor=ORANGE if took else AQUA,
                                       edgecolor="none"))
            ax.text(j + 0.5, y + 0.5, "took effect" if took else "blocked",
                    ha="center", va="center", fontsize=9, color="white",
                    fontweight="bold")

    ax.set_title("Exercise 2 - a permission written in a prompt stops "
                 "nothing; enforcement stops\nfour of five, and c4 (a false "
                 "value in a well-formed message) is the one it cannot",
                 fontsize=10.5, color=INK, pad=22)
    _save(fig, "exp6_fig5_injection.png")


def main():
    print("Generating figures for Lab 6 ...")
    team = evaluate("team")
    gen = evaluate("generalist")
    fig1_team_vs_generalist(team, gen)
    fig2_per_task(team, gen)
    fig3_violations(team)

    results = {
        "full team": team,
        "no Reviewer": evaluate("team", use_reviewer=False),
        "Researcher+Writer merged": evaluate("team", merge_rw=True),
        "generalist": gen,
    }
    fig4_ablation(results)
    fig5_injection()
    print("Figures written to %s" % OUTDIR)


if __name__ == "__main__":
    main()
