import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.style.use("default")
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

HERE = Path(__file__).parent
OUTDIR = HERE / "outputs"
OUTDIR.mkdir(exist_ok=True)

COLORS = {
    "bfs": "#0275d8",
    "ucs": "#5cb85c",
    "reactive": "#d9534f",
    "deliberative": "#0275d8",
    "hybrid": "#9b6ba6",
    "safe": "#5cb85c",
    "wall": "#2b2b2b",
    "free": "#f7f7f5",
    "path": "#f0ad4e",
    "start": "#5cb85c",
    "goal": "#d9534f",
    "pit": "#8b0000",
    "hazard": "#f4cccc",
}


def read_kv(path):

    data = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            key, _, rest = line.partition(" ")
            data.setdefault(key, []).append(rest)
    return data


def parse_cells(token):
    return [tuple(int(x) for x in pair.split(",")) for pair in token.split()]


def draw_grid(ax, grid_rows, path=None, marks=None, title=""):

    rows, cols = len(grid_rows), len(grid_rows[0])
    img = np.ones((rows, cols, 3))
    for r, row in enumerate(grid_rows):
        for c, ch in enumerate(row):
            img[r, c] = (0.17, 0.17, 0.17) if ch == "#" else (0.97, 0.97, 0.95)
            if ch == "O":
                img[r, c] = (0.55, 0.0, 0.0)

    marks = marks or {}
    for (r, c), color in marks.items():
        img[r, c] = color

    if path:
        for (r, c) in path:
            if grid_rows[r][c] not in "SG":
                img[r, c] = (0.94, 0.68, 0.19)

    ax.imshow(img, interpolation="nearest")
    for r, row in enumerate(grid_rows):
        for c, ch in enumerate(row):
            if ch == "S":
                ax.text(c, r, "S", ha="center", va="center", fontsize=9,
                        fontweight="bold", color="white")
            elif ch == "G":
                ax.text(c, r, "G", ha="center", va="center", fontsize=9,
                        fontweight="bold", color="white")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#999")


def plot_reference():
    data = read_kv(OUTDIR / "bfs_data.txt")
    grid_rows = data["grid"]
    path = parse_cells(data["path"][0])
    plan_len = int(data["plan_length"][0])
    expanded = int(data["expanded"][0])
    passable = int(data["passable"][0])
    reactive_reached = int(data["reactive_reached"][0])
    reactive_steps = int(data["reactive_steps"][0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Experiment 2: Deliberative BFS Agent vs Reactive Baseline",
                 fontsize=14, fontweight="bold", y=0.98)

    draw_grid(ax1, grid_rows, path=path,
              title="BFS plan (%d steps, %d/%d cells expanded)"
                    % (plan_len, expanded, passable))

    labels = ["Deliberative\n(BFS)", "Reactive\n(greedy Manhattan)"]
    steps = [plan_len, reactive_steps]
    reached = [True, bool(reactive_reached)]
    bar_colors = [COLORS["deliberative"] if r else "#c0c0c0" for r in [True, reached[1]]]
    bars = ax2.bar(labels, steps, color=[COLORS["deliberative"], COLORS["reactive"]], alpha=0.85)
    for bar, r, s in zip(bars, reached, steps):
        tag = "reached goal" if r else "stuck in loop\n(never reaches goal)"
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 "%d steps\n%s" % (s, tag), ha="center", fontsize=9)
    ax2.set_ylabel("Steps taken", fontsize=11, fontweight="bold")
    ax2.set_title("Outcome comparison", fontsize=10, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y", linestyle="--")
    ax2.set_ylim(0, max(steps) * 1.4)

    plt.tight_layout()
    plt.savefig(OUTDIR / "exp2_reference.png", dpi=300, bbox_inches="tight")
    print("[OK] Saved: exp2_reference.png")
    plt.close()


def plot_exercise_1():
    data = read_kv(OUTDIR / "ucs_data.txt")
    grid_rows = data["grid"]
    terrain_rows = data["terrain"]
    bfs_path = parse_cells(data["bfs_path"][0])
    ucs_path = parse_cells(data["ucs_path"][0])
    bfs_cost = int(data["bfs_cost"][0])
    ucs_cost = int(data["ucs_cost"][0])
    bfs_steps = int(data["bfs_steps"][0])
    ucs_steps = int(data["ucs_steps"][0])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
    fig.suptitle("Exercise 1: Uniform-Cost Search on a Terrain-Weighted Grid",
                 fontsize=14, fontweight="bold", y=1.02)

    rows, cols = len(grid_rows), len(grid_rows[0])
    cost_img = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            cost_img[r, c] = int(terrain_rows[r][c])
    im = axes[0].imshow(cost_img, cmap="YlOrRd", vmin=1, vmax=9)
    for r in range(rows):
        for c in range(cols):
            axes[0].text(c, r, terrain_rows[r][c], ha="center", va="center", fontsize=8)
    axes[0].set_xticks([]); axes[0].set_yticks([])
    axes[0].set_title("Terrain cost grid\n(1=open ground, 9=swamp)", fontsize=10, fontweight="bold")

    draw_grid(axes[1], grid_rows, path=bfs_path,
              title="A. BFS path\n%d steps, true cost %d" % (bfs_steps, bfs_cost))
    draw_grid(axes[2], grid_rows, path=ucs_path,
              title="B. UCS path\n%d steps, cost %d" % (ucs_steps, ucs_cost))

    plt.tight_layout()
    plt.savefig(OUTDIR / "exp2_ex1_uniform_cost.png", dpi=300, bbox_inches="tight")
    print("[OK] Saved: exp2_ex1_uniform_cost.png")
    plt.close()


    fig2, ax = plt.subplots(figsize=(6, 4.5))
    labels = ["BFS\n(minimises steps)", "Uniform-cost search\n(minimises cost)"]
    costs = [bfs_cost, ucs_cost]
    bars = ax.bar(labels, costs, color=[COLORS["bfs"], COLORS["ucs"]], alpha=0.85)
    for bar, v in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3, str(v), ha="center", fontweight="bold")
    ax.set_ylabel("True path cost under terrain grid", fontsize=11, fontweight="bold")
    ax.set_title("BFS ignores terrain; UCS minimises it", fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y", linestyle="--")
    plt.tight_layout()
    plt.savefig(OUTDIR / "exp2_ex1_cost_comparison.png", dpi=300, bbox_inches="tight")
    print("[OK] Saved: exp2_ex1_cost_comparison.png")
    plt.close()


def plot_exercise_2():
    data = read_kv(OUTDIR / "replan_data.txt")
    reached = int(data["reached"][0])
    replans = int(data["replans"][0])
    steps = int(data["steps"][0])
    bumps = int(data["bumps"][0])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = ["Original plan\nlength", "Actual steps\ntaken", "Bumps\n(failed moves)", "Re-plans\ntriggered"]
    values = [22, steps, bumps, replans]
    colors = [COLORS["bfs"], COLORS["hybrid"], COLORS["reactive"], "#5cb85c"]
    bars = ax.bar(labels, values, color=colors, alpha=0.85)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5, str(v), ha="center", fontweight="bold")
    ax.set_ylabel("Count", fontsize=11, fontweight="bold")
    ax.set_title("Exercise 2: Cost of Discovering a Blocked Cell Mid-Plan\n"
                 "(goal reached = %s)" % ("yes" if reached else "no"),
                 fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y", linestyle="--")
    plt.tight_layout()
    plt.savefig(OUTDIR / "exp2_ex2_replan.png", dpi=300, bbox_inches="tight")
    print("[OK] Saved: exp2_ex2_replan.png")
    plt.close()


def plot_exercise_3():
    data = read_kv(OUTDIR / "hybrid_data.txt")
    grid_rows = data["grid"]
    plain_steps = int(data["plain_steps"][0])
    plain_unsafe = int(data["plain_unsafe"][0])
    hybrid_steps = int(data["hybrid_steps"][0])
    hybrid_vetoes = int(data["hybrid_vetoes"][0])
    safe_steps = int(data["safe_steps"][0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Exercise 3: Hybrid Agent — Reactive Pit-Avoidance Filters a BFS Plan",
                 fontsize=14, fontweight="bold", y=0.98)

    draw_grid(ax1, grid_rows,
              title="World: pits (dark red) and their hazard margin")

    labels = ["A. Pure\ndeliberative", "B. Hybrid\n(BFS + veto)", "C. BFS on\nsafe model"]
    steps_vals = [plain_steps, hybrid_steps, safe_steps]
    unsafe_flags = [plain_unsafe > 0, False, False]
    bar_colors = [COLORS["reactive"] if u else COLORS["safe"] for u in unsafe_flags]
    bars = ax2.bar(labels, steps_vals, color=bar_colors, alpha=0.85)
    for bar, v, u in zip(bars, steps_vals, unsafe_flags):
        tag = "enters hazard margin" if u else "stays safe"
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.3, "%d\n(%s)" % (v, tag),
                 ha="center", fontsize=8.5)
    ax2.set_ylabel("Steps to goal", fontsize=11, fontweight="bold")
    ax2.set_title("Hybrid agent vetoed %d unsafe proposals,\nreached the goal in the same "
                  "%d steps as A" % (hybrid_vetoes, hybrid_steps), fontsize=10, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y", linestyle="--")
    ax2.set_ylim(0, max(steps_vals) * 1.4)

    plt.tight_layout()
    plt.savefig(OUTDIR / "exp2_ex3_hybrid.png", dpi=300, bbox_inches="tight")
    print("[OK] Saved: exp2_ex3_hybrid.png")
    plt.close()


def create_summary_table():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("tight")
    ax.axis("off")

    data = [
        ["Reference", "BFS agent vs\ngreedy reactive", "BFS finds the spiral's optimal 22-step\nroute; reactive baseline loops forever",
         "Deliberative\n(only one that finishes)"],
        ["Exercise 1", "BFS vs\nuniform-cost search", "BFS ignores terrain, pays for the swamp;\nUCS re-routes and pays less",
         "UCS\n(minimises true cost)"],
        ["Exercise 2", "Plan, block a cell,\nre-plan", "A single bump is enough to detect a stale\nmodel; agent re-plans from where it stands",
         "Re-planning\n(handles a changing world)"],
        ["Exercise 3", "Hybrid: BFS +\nreactive pit veto", "Reactive layer vetoes every unsafe step\nBFS proposes, with no cost in path length",
         "Hybrid\n(safety + optimality)"],
    ]
    headers = ["Part", "Agents Tested", "Key Finding", "Winner"]
    table = ax.table(cellText=data, colLabels=headers, cellLoc="left", loc="center",
                     colWidths=[0.12, 0.2, 0.43, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.3)

    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor("#2d5a6b")
        cell.set_text_props(weight="bold", color="white")
    for i in range(1, 5):
        for j in range(4):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor("#f0f0f0")
            cell.set_text_props(verticalalignment="center")

    plt.title("Lab 2 (Experiment 2) Summary", fontsize=13, fontweight="bold", pad=20)
    plt.savefig(OUTDIR / "summary_table.png", dpi=300, bbox_inches="tight",
               facecolor="white", edgecolor="none")
    print("[OK] Saved: summary_table.png")
    plt.close()


if __name__ == "__main__":
    print("Generating plots for Lab 2...\n")
    try:
        plot_reference()
        plot_exercise_1()
        plot_exercise_2()
        plot_exercise_3()
        create_summary_table()
        print("\n[SUCCESS] All plots saved to: %s" % OUTDIR)
    except FileNotFoundError as e:
        print("\n[ERROR] Missing data file: %s" % e)
        print("Run exp2_bfs_agent.py, exp2_ex1_uniform_cost.py, exp2_ex2_replan.py")
        print("and exp2_ex3_hybrid.py first - they write the *_data.txt files this")
        print("script reads.")

