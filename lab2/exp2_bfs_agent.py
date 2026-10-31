import os
import random
import sys
import time
from collections import deque

FREE, WALL, START, GOAL, PIT = ".", "#", "S", "G", "O"


MOVES = (("Up", -1, 0), ("Right", 0, 1), ("Down", 1, 0), ("Left", 0, -1))
DELTA = dict((name, (dr, dc)) for name, dr, dc in MOVES)


class Grid:


    def __init__(self, rows):
        self.cells = [list(r) for r in rows]
        self.rows = len(self.cells)
        self.cols = len(self.cells[0])
        if any(len(r) != self.cols for r in self.cells):
            raise ValueError("grid rows are not all the same length")


    def inside(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def at(self, cell):

        return self.cells[cell[0]][cell[1]] if self.inside(cell) else WALL

    def passable(self, cell):
        return self.inside(cell) and self.at(cell) != WALL

    def find(self, ch):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c] == ch:
                    return (r, c)
        raise ValueError("no %r in the grid" % ch)

    def cells_with(self, ch):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.cells[r][c] == ch]

    def passable_count(self):
        return sum(1 for r in range(self.rows) for c in range(self.cols)
                   if self.passable((r, c)))


    def set(self, cell, ch):
        self.cells[cell[0]][cell[1]] = ch

    def copy(self):
        return Grid(["".join(r) for r in self.cells])

    def rows_as_strings(self):
        return ["".join(r) for r in self.cells]


    def render(self, marks=None, indent="    ", ruler=True):

        marks = marks or {}
        lines = []
        if ruler:
            lines.append(indent + "   " +
                         "".join(str(c % 10) for c in range(self.cols)))
        for r in range(self.rows):
            row = "".join(marks.get((r, c), self.cells[r][c])
                          for c in range(self.cols))
            lines.append("%s%2d %s" % (indent, r, row))
        return "\n".join(lines)


def neighbours(grid, cell):

    for name, dr, dc in MOVES:
        nxt = (cell[0] + dr, cell[1] + dc)
        if grid.passable(nxt):
            yield name, nxt


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class GridEnvironment:


    def __init__(self, grid_rows, terrain_rows=None):
        self.grid = grid_rows.copy() if isinstance(grid_rows, Grid)            else Grid(grid_rows)
        self.start = self.grid.find(START)
        self.goal = self.grid.find(GOAL)
        self.location = self.start


        self.terrain = Grid(terrain_rows) if terrain_rows else None
        self.steps = 0
        self.cost_paid = 0
        self.bumps = 0
        self.trail = [self.start]


    def percept(self):

        view = dict((name, self.grid.at((self.location[0] + dr,
                                         self.location[1] + dc)))
                    for name, dr, dc in MOVES)
        return (self.location, view)

    def at_goal(self):
        return self.location == self.goal

    def cost_of(self, cell):
        return int(self.terrain.at(cell)) if self.terrain else 1


    def execute(self, action):

        dr, dc = DELTA[action]
        target = (self.location[0] + dr, self.location[1] + dc)
        contents = self.grid.at(target)
        self.steps += 1
        if not self.grid.passable(target):
            self.bumps += 1
            return False, contents
        self.location = target
        self.cost_paid += self.cost_of(target)
        self.trail.append(target)
        return True, contents


    def block(self, cell):

        self.grid.set(cell, WALL)

    def compact(self):
        return "@%s  steps=%d  cost=%d  bumps=%d" % (
            self.location, self.steps, self.cost_paid, self.bumps)


def breadth_first_plan(model, start, goal):
    frontier = deque([start])
    parent = {start: None}
    dist = {start: 0}
    expanded = []

    while frontier:
        cell = frontier.popleft()
        expanded.append(cell)

        if cell == goal:
            return {"found": True,
                    "plan": actions_from(parent, goal),
                    "path": path_from(parent, goal),
                    "parent": parent, "dist": dist, "expanded": expanded}

        for action, nxt in neighbours(model, cell):
            if nxt not in parent:
                parent[nxt] = (cell, action)
                dist[nxt] = dist[cell] + 1
                frontier.append(nxt)


    return {"found": False, "plan": None, "path": None,
            "parent": parent, "dist": dist, "expanded": expanded}


def actions_from(parent, goal):

    plan, cell = [], goal
    while parent[cell] is not None:
        cell, action = parent[cell]
        plan.append(action)
    plan.reverse()
    return plan


def path_from(parent, goal):

    path, cell = [goal], goal
    while parent[cell] is not None:
        cell = parent[cell][0]
        path.append(cell)
    path.reverse()
    return path


class DeliberativeAgent:


    def __init__(self, model_rows, planner=breadth_first_plan):
        self.model = model_rows.copy() if isinstance(model_rows, Grid)            else Grid(model_rows)
        self.planner = planner
        self.plan = []
        self.cursor = 0
        self.result = None
        self.plans_built = 0
        self.nodes_expanded = 0


    def make_plan(self, start, goal):
        self.result = self.planner(self.model, start, goal)
        self.plans_built += 1
        self.nodes_expanded += len(self.result["expanded"])
        self.plan = self.result["plan"] or []
        self.cursor = 0
        return self.result


    def has_plan_left(self):
        return self.cursor < len(self.plan)

    def peek_action(self):
        return self.plan[self.cursor]

    def next_action(self):
        action = self.plan[self.cursor]
        self.cursor += 1
        return action


def execute_plan(env, agent, trace=True, label=""):
    if trace:
        if label:
            print(label)
        header = "%-5s | %-6s | %-9s | %-9s | %s" % (
            "Step", "Action", "From", "To", "Moved?")
        print(header)
        print("-" * len(header))

    while agent.has_plan_left():
        before = env.location
        action = agent.next_action()
        moved, contents = env.execute(action)
        if trace:
            print("%-5d | %-6s | %-9s | %-9s | %s" % (
                env.steps, action, str(before), str(env.location),
                "yes" if moved else "NO (%s)" % contents))

    reached = env.at_goal()
    if trace:
        print("Result: %s   %s" % (
            "GOAL REACHED" if reached else "goal NOT reached", env.compact()))
        print()
    return reached


def plan_marks(path, start, goal):

    marks = dict((cell, "*") for cell in path)
    marks[start] = "S"
    marks[goal] = "G"
    return marks


def render_distances(model, dist, indent="    "):

    lines = [indent + "    " + "".join("%3d" % c for c in range(model.cols))]
    for r in range(model.rows):
        row = []
        for c in range(model.cols):
            if not model.passable((r, c)):
                row.append("  #")
            elif (r, c) in dist:
                row.append("%3d" % dist[(r, c)])
            else:
                row.append("  .")
        lines.append("%s%3d %s" % (indent, r, "".join(row)))
    return "\n".join(lines)


def animate(grid_rows, path, delay=0.20, title="deliberative agent executing its BFS plan"):
    grid = Grid(grid_rows)
    start, goal = grid.find(START), grid.find(GOAL)
    for k, cell in enumerate(path):
        sys.stdout.write("\033[2J\033[H")
        print("EXPERIMENT 2 - %s\n" % title)
        marks = {}
        for i, p in enumerate(path):
            marks[p] = "+" if i <= k else "*"
        marks[start] = "S"
        marks[goal] = "G"
        marks[cell] = "A"
        print(grid.render(marks))
        print("\n    step %d of %d    at %s    plan remaining: %d actions"
              % (k, len(path) - 1, cell, len(path) - 1 - k))
        print("\n    A = agent   + = already travelled   * = still planned")
        sys.stdout.flush()
        time.sleep(delay)
    print("\n    GOAL REACHED in %d steps.\n" % (len(path) - 1))


def run_greedy_reactive(env, budget=200, trace_first=12):
    if trace_first:
        print("%-5s | %-9s | %-6s | %-9s | %s" % (
            "Step", "At", "Action", "To", "Manhattan distance to goal"))
        print("-" * 66)
    seen = {}
    for t in range(1, budget + 1):
        location, view = env.percept()
        best, best_d = None, None
        for name, dr, dc in MOVES:
            if view[name] == WALL:
                continue
            d = manhattan((location[0] + dr, location[1] + dc), env.goal)
            if best_d is None or d < best_d:
                best, best_d = name, d
        if best is None:
            return False
        env.execute(best)
        if t <= trace_first:
            print("%-5d | %-9s | %-6s | %-9s | %d" % (
                t, str(location), best, str(env.location), best_d))
        if env.at_goal():
            return True
        key = (location, env.location)
        seen[key] = seen.get(key, 0) + 1
        if seen[key] == 3:
            return False
    return False


GRID_MAIN = [
    "S..........",
    ".####.####.",
    ".#.......#.",
    ".#.#####.#.",
    ".#.#...#.#.",
    ".#.#.G.#.#.",
    ".#.#...#.#.",
    ".#.##.##.#.",
    ".#.......#.",
    ".#########.",
    "...........",
]


GRID_SEALED = list(GRID_MAIN)
GRID_SEALED[7] = ".#.#####.#."

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")


def random_maze(rows, cols, seed=None):
    rng = random.Random(seed)
    rows = rows if rows % 2 == 1 else rows + 1
    cols = cols if cols % 2 == 1 else cols + 1
    cells = [["#"] * cols for _ in range(rows)]

    def carve(r, c):
        cells[r][c] = "."
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        rng.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and cells[nr][nc] == "#":
                cells[r + dr // 2][c + dc // 2] = "."
                carve(nr, nc)

    carve(1, 1)

    reachable = [(r, c) for r in range(rows) for c in range(cols)
                if cells[r][c] == "." and (r, c) != (1, 1)]
    gr, gc = rng.choice(reachable)
    cells[1][1] = "S"
    cells[gr][gc] = "G"
    return ["".join(row) for row in cells]


if __name__ == "__main__":
    use_random = "--random" in sys.argv
    world = random_maze(11, 15) if use_random else GRID_MAIN

    if "--animate" in sys.argv:
        agent = DeliberativeAgent(world)
        env = GridEnvironment(world)
        res = agent.make_plan(env.start, env.goal)
        animate(world, res["path"])
        sys.exit(0)

    print("EXPERIMENT 2 - DELIBERATIVE (GOAL-BASED) AGENT - BFS PLANNING")
    print()

    env = GridEnvironment(world)
    agent = DeliberativeAgent(world)
    result = agent.make_plan(env.start, env.goal)

    print("Grid:")
    print(env.grid.render())
    print()
    print("Plan (%d actions): %s" % (len(agent.plan), agent.plan))
    print()
    print("Path taken ( * = visited cell ):")
    print(agent.model.render(plan_marks(result["path"], env.start, env.goal)))
    print()

    execute_plan(env, agent, trace=False)
    print("Goal reached: %s   steps: %d" % (env.at_goal(), env.steps))


    env_r = GridEnvironment(world)
    reached = run_greedy_reactive(env_r, trace_first=0)


    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "bfs_data.txt"), "w", encoding="utf-8") as fh:
        fh.write("plan_length %d\n" % len(agent.plan))
        fh.write("expanded %d\n" % len(result["expanded"]))
        fh.write("passable %d\n" % agent.model.passable_count())
        fh.write("reactive_reached %d\n" % (1 if reached else 0))
        fh.write("reactive_steps %d\n" % env_r.steps)
        fh.write("path %s\n" % " ".join("%d,%d" % c for c in result["path"]))
        for row in world:
            fh.write("grid %s\n" % row)

