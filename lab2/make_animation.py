import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from exp2_bfs_agent import GridEnvironment, DeliberativeAgent, GRID_MAIN

HERE = Path(__file__).parent
OUTDIR = HERE / "outputs"
OUTDIR.mkdir(exist_ok=True)


def build_frame_image(grid_rows, path, upto):
    rows, cols = len(grid_rows), len(grid_rows[0])
    img = np.ones((rows, cols, 3))
    for r, row in enumerate(grid_rows):
        for c, ch in enumerate(row):
            img[r, c] = (0.16, 0.16, 0.16) if ch == "#" else (0.97, 0.97, 0.95)
    for i, (r, c) in enumerate(path):
        if i <= upto and grid_rows[r][c] not in "SG":
            img[r, c] = (0.94, 0.68, 0.19) if i < upto else (0.15, 0.55, 0.85)
    return img


def main():
    env = GridEnvironment(GRID_MAIN)
    agent = DeliberativeAgent(GRID_MAIN)
    result = agent.make_plan(env.start, env.goal)
    path = result["path"]
    grid_rows = GRID_MAIN

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    fig.suptitle("Experiment 2 — Deliberative Agent Executing Its BFS Plan",
                 fontsize=12, fontweight="bold")
    im = ax.imshow(build_frame_image(grid_rows, path, 0), interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    status = ax.text(0.02, -0.05, "", transform=ax.transAxes, fontsize=10)

    agent_dot, = ax.plot([], [], marker="o", markersize=16, color="#1565c0",
                         markeredgecolor="white", markeredgewidth=1.5, zorder=5)

    for r, row in enumerate(grid_rows):
        for c, ch in enumerate(row):
            if ch == "S":
                ax.text(c, r, "S", ha="center", va="center", fontsize=9,
                        fontweight="bold", color="white", zorder=4)
            elif ch == "G":
                ax.text(c, r, "G", ha="center", va="center", fontsize=9,
                        fontweight="bold", color="white", zorder=4)

    def update(frame):
        im.set_data(build_frame_image(grid_rows, path, frame))
        r, c = path[frame]
        agent_dot.set_data([c], [r])
        status.set_text("step %d / %d   position %s   %s"
                        % (frame, len(path) - 1, path[frame],
                           "GOAL REACHED" if frame == len(path) - 1 else "executing plan..."))
        return im, agent_dot, status

    anim = animation.FuncAnimation(fig, update, frames=len(path),
                                   interval=220, blit=False, repeat=True)

    out_path = OUTDIR / "exp2_animation.gif"
    anim.save(str(out_path), writer=animation.PillowWriter(fps=5))
    print("[OK] Saved: %s" % out_path)

    if "--show" in sys.argv:
        plt.show()


if __name__ == "__main__":
    main()

