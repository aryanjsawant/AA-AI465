import heapq
import itertools
import os

from exp2_bfs_agent import (
    Grid, GridEnvironment, DeliberativeAgent, breadth_first_plan,
    neighbours, plan_marks, execute_plan, manhattan,
    START, GOAL, WALL, MOVES, HERE, OUTDIR,
)


def uniform_cost_plan(model, terrain, start, goal):
    counter = itertools.count()
    frontier = [(0, next(counter), start)]
    best_cost = {start: 0}
    parent = {start: None}
    expanded = []
    closed = set()

    while frontier:
        cost, _, cell = heapq.heappop(frontier)
        if cell in closed:
            continue
        closed.add(cell)
        expanded.append(cell)

        if cell == goal:
            plan, path = [], [goal]
            cur = goal
            while parent[cur] is not None:
                cur, action = parent[cur]
                plan.append(action)
                path.append(cur)
            plan.reverse()
            path.reverse()
            return {"found": True, "plan": plan, "path": path,
                    "cost": cost, "dist": best_cost, "expanded": expanded}

        for action, nxt in neighbours(model, cell):
            step_cost = int(terrain.at(nxt))
            new_cost = cost + step_cost
            if nxt not in best_cost or new_cost < best_cost[nxt]:
                best_cost[nxt] = new_cost
                parent[nxt] = (cell, action)
                heapq.heappush(frontier, (new_cost, next(counter), nxt))

    return {"found": False, "plan": None, "path": None, "cost": None,
            "dist": best_cost, "expanded": expanded}


class UniformCostAgent(DeliberativeAgent):


    def __init__(self, model_rows, terrain_rows):
        super().__init__(model_rows)
        self.terrain = Grid(terrain_rows)

    def make_plan(self, start, goal):
        self.result = uniform_cost_plan(self.model, self.terrain, start, goal)
        self.plans_built += 1
        self.nodes_expanded += len(self.result["expanded"])
        self.plan = self.result["plan"] or []
        self.cursor = 0
        return self.result


def render_cost(grid, cost, indent="    "):

    lines = [indent + "    " + "".join("%2d" % c for c in range(cost.cols))]
    for r in range(grid.rows):
        row = []
        for c in range(grid.cols):
            row.append(" #" if not grid.passable((r, c)) else " %s" % cost.at((r, c)))
        lines.append("%s%3d %s" % (indent, r, "".join(row)))
    return "\n".join(lines)


GRID = [
    "S........",
    ".........",
    "....G....",
    ".........",
    ".........",
]

TERRAIN = [
    "111111111",
    "111111111",
    "1111511111"[:9],
    "111111111",
    "111111111",
]


TERRAIN = [
    "111111111",
    "119999111",
    "111191111",
    "119999111",
    "111111111",
]


def build_scenario():
    grid = Grid(GRID)
    terrain = Grid(TERRAIN)
    assert grid.rows == terrain.rows and grid.cols == terrain.cols
    return grid, terrain


if __name__ == "__main__":
    print("EXERCISE 1 - UNIFORM-COST SEARCH OVER A TERRAIN-WEIGHTED GRID")
    print()

    grid, terrain = build_scenario()
    env = GridEnvironment(GRID)

    bfs_res = breadth_first_plan(grid, env.start, env.goal)
    bfs_cost = sum(int(terrain.at(cell)) for cell in bfs_res["path"][1:])

    agent = UniformCostAgent(GRID, TERRAIN)
    ucs_res = agent.make_plan(env.start, env.goal)

    env2 = GridEnvironment(GRID, terrain_rows=TERRAIN)
    execute_plan(env2, agent, trace=False)

    print("Grid:")
    print(grid.render())
    print()
    print("Terrain cost grid:")
    print(render_cost(grid, terrain))
    print()

    print("BFS plan (%d steps, true cost %d):" % (len(bfs_res["plan"]), bfs_cost))
    print(grid.render(plan_marks(bfs_res["path"], env.start, env.goal)))
    print()

    print("UCS plan (%d steps, cost %d):" % (len(ucs_res["plan"]), ucs_res["cost"]))
    print(grid.render(plan_marks(ucs_res["path"], env.start, env.goal)))


    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "ucs_data.txt"), "w", encoding="utf-8") as fh:
        fh.write("bfs_steps %d\n" % len(bfs_res["plan"]))
        fh.write("bfs_cost %d\n" % bfs_cost)
        fh.write("ucs_steps %d\n" % len(ucs_res["plan"]))
        fh.write("ucs_cost %d\n" % ucs_res["cost"])
        fh.write("bfs_path %s\n" % " ".join("%d,%d" % c for c in bfs_res["path"]))
        fh.write("ucs_path %s\n" % " ".join("%d,%d" % c for c in ucs_res["path"]))
        for row in GRID:
            fh.write("grid %s\n" % row)
        for row in TERRAIN:
            fh.write("terrain %s\n" % row)

