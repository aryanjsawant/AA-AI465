import os

from exp2_bfs_agent import (
    Grid, GridEnvironment, DeliberativeAgent, breadth_first_plan,
    neighbours, plan_marks, manhattan,
    START, GOAL, WALL, PIT, MOVES, DELTA, HERE, OUTDIR,
)


def pit_adjacent_cells(grid):

    unsafe = set()
    pits = grid.cells_with(PIT)
    for r in range(grid.rows):
        for c in range(grid.cols):
            if not grid.passable((r, c)):
                continue
            for pr, pc in pits:
                if abs(pr - r) <= 1 and abs(pc - c) <= 1:
                    unsafe.add((r, c))
                    break
    return unsafe


def reactive_veto(cell, unsafe_cells):

    return cell in unsafe_cells


def safe_model(grid, unsafe_cells):
    safe = grid.copy()
    for cell in unsafe_cells:
        if safe.at(cell) not in (START, GOAL):
            safe.set(cell, "#")
    return safe


class HybridAgent(DeliberativeAgent):
    def __init__(self, model_rows, unsafe_cells):
        super().__init__(model_rows)
        self.unsafe_cells = set(unsafe_cells)
        self.vetoes = 0

    def safe_next_step(self, current):

        action = self.peek_action()
        dr, dc = DELTA[action]
        target = (current[0] + dr, current[1] + dc)

        if reactive_veto(target, self.unsafe_cells):
            self.vetoes += 1
            self.model.set(target, "#")
            self.make_plan(current, self.goal_cell)
            action = self.peek_action() if self.has_plan_left() else None
        return action


def run_hybrid(env, agent, trace=True):
    agent.goal_cell = env.goal
    agent.make_plan(env.start, env.goal)
    if trace:
        header = "%-5s | %-6s | %-9s | %-9s | %s" % (
            "Step", "Action", "From", "To", "Note")
        print(header)
        print("-" * len(header))

    while not env.at_goal():
        action = agent.safe_next_step(env.location)
        if action is None:
            if trace:
                print("No safe route remains from %s - hybrid agent halts "
                      "rather than accept an unsafe step." % (env.location,))
            return False
        before = env.location
        moved, contents = env.execute(action)
        agent.cursor += 1
        if trace:
            print("%-5d | %-6s | %-9s | %-9s | %s" % (
                env.steps, action, str(before), str(env.location),
                "" if moved else "bump (%s)" % contents))
    if trace:
        print()
        print("Goal reached. Steps=%d, bumps=%d, reactive vetoes=%d"
              % (env.steps, env.bumps, agent.vetoes))
    return True


GRID = [
    "S............",
    ".....O.......",
    ".............",
    "...O.........",
    ".............",
    "............G",
]


if __name__ == "__main__":
    print("EXERCISE 3 - HYBRID AGENT: REACTIVE PIT-AVOIDANCE FILTERS A BFS PLAN")
    print()

    grid = Grid(GRID)
    env = GridEnvironment(GRID)
    unsafe = pit_adjacent_cells(grid)

    plain_res = breadth_first_plan(grid, env.start, env.goal)
    plain_unsafe_steps = sum(1 for c in plain_res["path"] if c in unsafe)

    env2 = GridEnvironment(GRID)
    agent = HybridAgent(GRID, unsafe)
    reached = run_hybrid(env2, agent, trace=False)

    safe_grid = safe_model(grid, unsafe)
    safe_res = breadth_first_plan(safe_grid, env.start, env.goal)

    print("Grid (O = pit, ~ = hazard margin the reactive rule refuses):")
    hazard_marks = dict((c, "~") for c in unsafe if grid.at(c) == ".")
    print(grid.render(hazard_marks))
    print()

    print("A. Pure deliberative plan (%d steps, %d cells inside hazard margin):"
          % (len(plain_res["plan"]), plain_unsafe_steps))
    print(grid.render(plan_marks(plain_res["path"], env.start, env.goal)))
    print()

    print("B. Hybrid agent's actual path (%d steps, %d reactive vetoes):"
          % (env2.steps, agent.vetoes))
    print(env2.grid.render(dict((c, "*") for c in env2.trail)))


    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "hybrid_data.txt"), "w", encoding="utf-8") as fh:
        fh.write("plain_steps %d\n" % len(plain_res["plan"]))
        fh.write("plain_unsafe %d\n" % plain_unsafe_steps)
        fh.write("hybrid_steps %d\n" % env2.steps)
        fh.write("hybrid_vetoes %d\n" % agent.vetoes)
        fh.write("safe_steps %s\n" % (len(safe_res["plan"]) if safe_res["found"] else -1))
        for row in GRID:
            fh.write("grid %s\n" % row)

