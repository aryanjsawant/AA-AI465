"""
Experiment 1 - Exercise 2
The 1 x N corridor : N squares, random initial dirt, adapted condition-action
rules.  Three agents are compared on the same world.

Agentic AI (IA462), SVNIT Surat.  Standard library only; no agent framework.
"""

import random

CLEAN, DIRTY = "Clean", "Dirty"
SUCK, LEFT, RIGHT, NOOP = "Suck", "Left", "Right", "NoOp"
REWARD_SUCK, REWARD_MOVE = +10, -1


# --------------------------------------------------------------------------- #
# Environment : a 1 x N corridor.  Same interface as the two-square world.
# --------------------------------------------------------------------------- #
class CorridorEnvironment:
    def __init__(self, n, dirt_probability=0.5, location=0, seed=None):
        rng = random.Random(seed)
        self.n = n
        self.status = [DIRTY if rng.random() < dirt_probability else CLEAN
                       for _ in range(n)]
        self.location = location
        self.score = 0

    def percept(self):
        """(location, status, at_left_wall, at_right_wall) - local sensors only."""
        return (self.location,
                self.status[self.location],
                self.location == 0,
                self.location == self.n - 1)

    def execute(self, action):
        reward = 0
        if action == SUCK:
            if self.status[self.location] == DIRTY:
                self.status[self.location] = CLEAN
                reward = REWARD_SUCK
        elif action == LEFT:
            self.location = max(0, self.location - 1)
            reward = REWARD_MOVE
        elif action == RIGHT:
            self.location = min(self.n - 1, self.location + 1)
            reward = REWARD_MOVE
        elif action == NOOP:
            reward = 0
        else:
            raise ValueError("unknown action: %r" % (action,))
        self.score += reward
        return reward

    def world_state(self):
        cells = "".join("." if s == CLEAN else "#" for s in self.status)
        marker = " " * self.location + "^"
        return "[%s]  agent@%d\n%s%s" % (cells, self.location, " " * 1, marker)

    def compact(self):
        return "[%s]@%d" % (
            "".join("." if s == CLEAN else "#" for s in self.status),
            self.location)

    def dirty_left(self):
        return sum(1 for s in self.status if s == DIRTY)


# --------------------------------------------------------------------------- #
# Agent 1 : naive reflex.  Dirty -> Suck, at a wall -> turn, otherwise -> Right.
#           No state at all, so it cannot remember which way it was going.
# --------------------------------------------------------------------------- #
def naive_reflex_agent(percept):
    location, status, at_left, at_right = percept
    if status == DIRTY:
        return SUCK
    if at_right:
        return LEFT
    return RIGHT


# --------------------------------------------------------------------------- #
# Agent 2 : reflex + one bit of state (the current heading).  This is the
#           smallest change that makes the corridor sweepable.
# --------------------------------------------------------------------------- #
class SweepingReflexAgent:
    def __init__(self):
        self.heading = RIGHT          # the single bit of internal state

    def __call__(self, percept):
        location, status, at_left, at_right = percept
        if status == DIRTY:
            return SUCK
        if at_right:
            self.heading = LEFT
        elif at_left:
            self.heading = RIGHT
        return self.heading

    def dump(self):
        return "heading=%s" % self.heading


# --------------------------------------------------------------------------- #
# Agent 3 : model-based.  Keeps a belief about every square and stops once the
#           whole corridor is known to be clean.
# --------------------------------------------------------------------------- #
class ModelBasedCorridorAgent:
    def __init__(self, n):
        self.model = ["Unknown"] * n
        self.heading = RIGHT

    def __call__(self, percept):
        location, status, at_left, at_right = percept
        self.model[location] = status

        if status == DIRTY:
            self.model[location] = CLEAN
            return SUCK
        if all(s == CLEAN for s in self.model):
            return NOOP
        if at_right:
            self.heading = LEFT
        elif at_left:
            self.heading = RIGHT
        return self.heading

    def dump(self):
        return "".join({"Unknown": "?", CLEAN: ".", DIRTY: "#"}[s]
                       for s in self.model)


# --------------------------------------------------------------------------- #
def run(env, agent, steps, label, trace=True, show_model=False, quiet=False):
    if not quiet:
        print(label)
    if trace and not quiet:
        header = "%-5s | %-28s | %-6s | %-14s | %-6s | %s" % (
            "Step", "Percept", "Action", "World", "Score", "Agent state")
        print(header)
        print("-" * len(header))
    for t in range(1, steps + 1):
        p = env.percept()
        action = agent(p)
        env.execute(action)
        if trace and not quiet:
            state = agent.dump() if show_model else "-"
            print("%-5d | %-28s | %-6s | %-14s | %+6d | %s" % (
                t, "(%d, %s, L=%s, R=%s)" % p, action, env.compact(),
                env.score, state))
    if not quiet:
        print("Final : %s   score = %+d   squares still dirty = %d"
              % (env.compact(), env.score, env.dirty_left()))
        print()
    return env.score, env.dirty_left()


def scenario(n, steps, seed, start, title):
    print("=" * 92)
    print(title)
    print("=" * 92)
    print("Initial world : %s      steps : %d      random seed : %d"
          % (CorridorEnvironment(n, seed=seed, location=start).compact(),
             steps, seed))
    print()

    r1 = run(CorridorEnvironment(n, seed=seed, location=start),
             naive_reflex_agent, steps,
             ">>> A. Naive reflex agent (no state)")
    r2 = run(CorridorEnvironment(n, seed=seed, location=start),
             SweepingReflexAgent(), steps,
             ">>> B. Reflex agent + heading (one bit of state)", show_model=True)
    r3 = run(CorridorEnvironment(n, seed=seed, location=start),
             ModelBasedCorridorAgent(n), steps,
             ">>> C. Model-based agent (belief over all %d squares)" % n,
             show_model=True)

    print("Summary of this scenario")
    print("%-42s | %-12s | %s" % ("Agent", "Score", "Dirty squares left"))
    print("-" * 80)
    for name, res in (("Naive reflex (no state)", r1),
                      ("Reflex + heading (1 bit of state)", r2),
                      ("Model-based (full belief + NoOp)", r3)):
        print("%-42s | %-12d | %d" % (name, res[0], res[1]))
    print()
    return r1, r2, r3


if __name__ == "__main__":
    N, STEPS, SEED = 6, 20, 7

    print("EXERCISE 2 - 1 x %d CORRIDOR WITH RANDOM INITIAL DIRT "
          "( '#' = dirty, '.' = clean )" % N)
    print()

    scenario(N, STEPS, SEED, 0,
             "SCENARIO 1 - agent starts at the LEFT WALL (square 0)")

    scenario(N, STEPS, SEED, N // 2,
             "SCENARIO 2 - agent starts in the MIDDLE (square %d)" % (N // 2))

    print("=" * 92)
    print("SCALING WITH CORRIDOR LENGTH  (start in the middle, %d steps, seed %d)"
          % (STEPS, SEED))
    print("=" * 92)
    print("%-6s | %-14s | %-16s | %-14s | %s" % (
        "N", "naive reflex", "reflex+heading", "model-based",
        "dirty left (naive / heading / model)"))
    print("-" * 100)
    for n in (2, 4, 6, 8, 10):
        start = n // 2
        a = run(CorridorEnvironment(n, seed=SEED, location=start),
                naive_reflex_agent, STEPS, "", quiet=True)
        b = run(CorridorEnvironment(n, seed=SEED, location=start),
                SweepingReflexAgent(), STEPS, "", quiet=True)
        c = run(CorridorEnvironment(n, seed=SEED, location=start),
                ModelBasedCorridorAgent(n), STEPS, "", quiet=True)
        print("%-6d | %-14d | %-16d | %-14d | %d / %d / %d" % (
            n, a[0], b[0], c[0], a[1], b[1], c[1]))
    print()
    print("The naive rule 'if not at the right wall, go Right' has no memory of")
    print("where it came from, so once it bounces off the right wall it is")
    print("trapped between the last two squares and never returns to the dirt")
    print("it left behind.  One bit of state - the heading - is enough to")
    print("sweep the whole corridor; a full belief over the corridor is what")
    print("lets the agent know when to stop.")
