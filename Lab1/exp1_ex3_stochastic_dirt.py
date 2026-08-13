"""
Experiment 1 - Exercise 3
Dirt reappears with probability p = 0.1 per square per time step.
Is the simple reflex agent rational now?

Three agents are compared under the same stream of random events:
    A. simple reflex          - patrols for ever, no memory
    B. model-based + NoOp     - the Exercise-1 agent, stops when it believes
                                the world is clean
    C. model-based + decay    - keeps a belief but distrusts it once it is
                                stale, so it resumes patrolling

Agentic AI (IA462), SVNIT Surat.  Standard library only; no agent framework.
"""

import random

from exp1_reflex_agent import (
    VacuumEnvironment, simple_reflex_agent,
    CLEAN, DIRTY, SUCK, LEFT, RIGHT, NOOP,
)
from exp1_ex1_model_based import ModelBasedReflexAgent


# --------------------------------------------------------------------------- #
# Environment : the two-square world, but dirt reappears stochastically.
# --------------------------------------------------------------------------- #
class StochasticVacuumEnvironment(VacuumEnvironment):
    def __init__(self, p_dirt=0.1, seed=None, **kwargs):
        super().__init__(**kwargs)
        self.p_dirt = p_dirt
        self.rng = random.Random(seed)
        self.redirtied = 0

    def step_world(self):
        """Called once per time step, after the agent has acted."""
        events = []
        for square in ("A", "B"):
            if self.status[square] == CLEAN and self.rng.random() < self.p_dirt:
                self.status[square] = DIRTY
                self.redirtied += 1
                events.append(square)
        return events


# --------------------------------------------------------------------------- #
# Agent C : model-based agent whose belief decays.  A square not seen for
#           `patience` steps is demoted back to "Unknown", so the agent goes
#           and looks instead of sitting on a stale model.
# --------------------------------------------------------------------------- #
class DecayingModelAgent:
    def __init__(self, patience=3):
        self.model = {"A": "Unknown", "B": "Unknown"}
        self.age = {"A": 0, "B": 0}
        self.patience = patience

    def __call__(self, percept):
        location, status = percept

        # age every belief by one step, then refresh the one we can see
        for s in self.age:
            self.age[s] += 1
            if self.age[s] > self.patience:
                self.model[s] = "Unknown"       # too old to trust
        self.model[location] = status
        self.age[location] = 0

        if status == DIRTY:
            self.model[location] = CLEAN
            return SUCK
        if all(v == CLEAN for v in self.model.values()):
            return NOOP
        return RIGHT if location == "A" else LEFT

    def dump(self):
        return "{A:%s/%d, B:%s/%d}" % (self.model["A"][:5], self.age["A"],
                                       self.model["B"][:5], self.age["B"])


# --------------------------------------------------------------------------- #
def run(p_dirt, agent_factory, steps, seed, trace=False, label=""):
    env = StochasticVacuumEnvironment(
        p_dirt=p_dirt, seed=seed, status={"A": DIRTY, "B": DIRTY}, location="A")
    agent = agent_factory()

    if trace:
        print(label)
        header = "%-5s | %-16s | %-6s | %-22s | %-6s | %-11s | %s" % (
            "Step", "Percept", "Action", "World after action", "Score",
            "CleanCredit", "Re-dirtied")
        print(header)
        print("-" * len(header))

    for t in range(1, steps + 1):
        percept = env.percept()
        action = agent(percept)
        env.execute(action)
        env.tick_clean_credit()          # score the world as the agent left it
        events = env.step_world()        # then nature dirties squares again

        if trace:
            print("%-5d | %-16s | %-6s | %-22s | %+6d | %-11d | %s" % (
                t, "(%s, %s)" % percept, action, env.world_state(),
                env.score, env.clean_credit,
                ",".join(events) if events else "-"))

    if trace:
        print("Final : %s   score = %+d   clean-square credit = %d   "
              "re-dirtying events = %d"
              % (env.world_state(), env.score, env.clean_credit, env.redirtied))
        print()
    return env.score, env.clean_credit, env.redirtied


def average(p_dirt, agent_factory, steps, trials):
    tot_s = tot_c = 0
    for k in range(trials):
        s, c, _ = run(p_dirt, agent_factory, steps, seed=1000 + k)
        tot_s += s
        tot_c += c
    return tot_s / trials, tot_c / trials


# --------------------------------------------------------------------------- #
# Agent D : the "lazy" baseline.  It never moves; it only sucks the square it
#           happens to be standing on.  Included because it costs nothing, and
#           in a world where dirt comes to you, doing nothing is a real
#           strategy that any claim of rationality has to beat.
# --------------------------------------------------------------------------- #
def lazy_agent(percept):
    location, status = percept
    return SUCK if status == DIRTY else NOOP


AGENTS = (
    ("Simple reflex (no state)", lambda: simple_reflex_agent),
    ("Model-based + NoOp",       lambda: ModelBasedReflexAgent()),
    ("Model-based + decay(3)",   lambda: DecayingModelAgent(patience=3)),
    ("Lazy (never moves)",       lambda: lazy_agent),
)


if __name__ == "__main__":
    P, STEPS, TRIALS = 0.1, 30, 200

    print("=" * 104)
    print("EXERCISE 3 - DIRT REAPPEARS WITH PROBABILITY p = %.2f PER SQUARE "
          "PER STEP" % P)
    print("=" * 104)
    print()

    print(">>> Sample traces, %d steps, random seed 1000 "
          "(the same stream of re-dirtying events for every agent)" % STEPS)
    print()
    for name, factory in AGENTS:
        run(P, factory, STEPS, seed=1000, trace=True, label=">>> %s" % name)

    print("=" * 104)
    print("AVERAGE OVER %d INDEPENDENT RUNS OF %d STEPS  (p = %.2f)"
          % (TRIALS, STEPS, P))
    print("=" * 104)
    print("%-30s | %-16s | %s" % ("Agent", "Mean task score",
                                  "Mean clean-square credit (max %d)" % (2 * STEPS)))
    print("-" * 92)
    for name, factory in AGENTS:
        s, c = average(P, factory, STEPS, TRIALS)
        print("%-30s | %-16.2f | %.2f" % (name, s, c))

    print()
    print("=" * 104)
    print("SENSITIVITY TO p  (mean task score / mean clean-square credit, "
          "%d runs of %d steps)" % (TRIALS, STEPS))
    print("=" * 104)
    print("%-6s | %s" % ("p", " | ".join("%-19s" % n for n, _ in AGENTS)))
    print("-" * 100)
    for p in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4):
        cells = []
        for name, factory in AGENTS:
            s, c = average(p, factory, STEPS, TRIALS)
            cells.append("%7.2f /%6.2f" % (s, c))
        print("%-6.2f | %s" % (p, " | ".join("%-19s" % c for c in cells)))
    print()
    print("Best agent by task score, and by clean-square credit, at each p:")
    print("%-6s | %-26s | %s" % ("p", "best task score", "best clean-square credit"))
    print("-" * 70)
    for p in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4):
        res = [(name,) + average(p, factory, STEPS, TRIALS)
               for name, factory in AGENTS]
        best_s = max(res, key=lambda r: r[1])
        best_c = max(res, key=lambda r: r[2])
        print("%-6.2f | %-26s | %s" % (p, "%s (%.1f)" % (best_s[0], best_s[1]),
                                       "%s (%.1f)" % (best_c[0], best_c[2])))

    print()
    print("Reading the table: at p = 0 the memoryless agent is dominated - it")
    print("pays -1 for ever.  As p grows, patrolling starts to pay for itself,")
    print("because a square the agent never revisits cannot be cleaned.  The")
    print("agent that only *believes* the world is clean is the one that fails:")
    print("its model is correct when written and wrong one step later.  Note")
    print("also that the do-nothing agent beats the reflex agent at small p:")
    print("the reflex agent is not rational there either, because it pays to")
    print("move without weighing that cost against the chance of finding dirt.")
