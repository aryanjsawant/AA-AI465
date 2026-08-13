"""
Experiment 1 - Simple Reflex (Reactive) Agent : The Vacuum-Cleaner World
Agentic AI (IA462), Semester VIII - SVNIT Surat

Reference program.  Python standard library only; no agent framework is used
(Rules and Regulations, clause 3.1).  Every part of the perception-action loop
- the environment, the percept, the condition-action rules and the driver loop
- appears explicitly below.

Design note (agent-environment separation):
    The environment owns the TRUE state (dirt in both squares, agent location,
    score).  It exposes exactly two methods to the outside world:
        percept()        -> (location, status)   what the sensors report
        execute(action)  -> reward              what the actuators do
    The agent is a pure function.  It receives nothing but the percept and
    returns nothing but an action.  It has no memory and no model of the world.
"""

CLEAN = "Clean"
DIRTY = "Dirty"

SUCK, LEFT, RIGHT, NOOP = "Suck", "Left", "Right", "NoOp"

REWARD_SUCK = +10      # cleaning is rewarded          (Algorithm, step 2)
REWARD_MOVE = -1       # every movement costs energy   (Algorithm, step 2)


# --------------------------------------------------------------------------- #
# 1. The environment: it holds the true state of the world.
# --------------------------------------------------------------------------- #
class VacuumEnvironment:
    """Two squares, A and B, each Clean or Dirty."""

    def __init__(self, status=None, location="A"):
        # status maps square name -> CLEAN / DIRTY
        self.status = dict(status) if status else {"A": DIRTY, "B": DIRTY}
        self.location = location
        self.score = 0          # task performance measure (+10 suck, -1 move)
        self.clean_credit = 0   # PEAS measure: +1 per clean square per step

    # -- sensors ------------------------------------------------------------ #
    def percept(self):
        """All the agent is ever allowed to see."""
        return (self.location, self.status[self.location])

    # -- actuators ---------------------------------------------------------- #
    def execute(self, action):
        """Apply an action to the world and return the reward it earned."""
        reward = 0
        if action == SUCK:
            if self.status[self.location] == DIRTY:
                self.status[self.location] = CLEAN
                reward = REWARD_SUCK
        elif action == LEFT:
            self.location = "A"
            reward = REWARD_MOVE
        elif action == RIGHT:
            self.location = "B"
            reward = REWARD_MOVE
        elif action == NOOP:
            reward = 0
        else:
            raise ValueError("unknown action: %r" % (action,))

        self.score += reward
        return reward

    # -- book-keeping ------------------------------------------------------- #
    def tick_clean_credit(self):
        """+1 for each square that is clean at this time step (PEAS measure)."""
        gained = sum(1 for s in self.status.values() if s == CLEAN)
        self.clean_credit += gained
        return gained

    def world_state(self):
        return "A=%-5s  B=%-5s  agent@%s" % (
            self.status["A"], self.status["B"], self.location)


# --------------------------------------------------------------------------- #
# 2. The agent: a pure function from percept to action.  No internal state.
# --------------------------------------------------------------------------- #
def simple_reflex_agent(percept):
    """Condition-action rules of Russell & Norvig's reflex vacuum agent.

        if status is Dirty      -> Suck
        else if location is A   -> Right
        else                    -> Left
    """
    location, status = percept
    if status == DIRTY:
        return SUCK
    elif location == "A":
        return RIGHT
    else:
        return LEFT


def noop_when_clean_agent(percept):
    """A second, equally memoryless rule table, used in RUN 4 as a control.

        if status is Dirty -> Suck   else -> NoOp

    It removes the oscillation, and with it the agent's only way of ever
    reaching the other square.
    """
    location, status = percept
    return SUCK if status == DIRTY else NOOP


# --------------------------------------------------------------------------- #
# 3. The perception-action loop.
# --------------------------------------------------------------------------- #
def run(env, agent, steps):
    print("Initial state : %s" % env.world_state())
    print("Performance   : score = %d" % env.score)
    print()
    header = "%-5s | %-16s | %-6s | %-25s | %-7s | %-6s | %s" % (
        "Step", "Percept", "Action", "Resulting world state",
        "Reward", "Score", "CleanCredit")
    print(header)
    print("-" * len(header))

    for t in range(1, steps + 1):
        percept = env.percept()          # 1. perceive
        action = agent(percept)          # 2. decide  (condition-action rules)
        reward = env.execute(action)     # 3. act
        env.tick_clean_credit()          # 4. environment scores the time step

        print("%-5d | %-16s | %-6s | %-25s | %+7d | %+6d | %d" % (
            t, "(%s, %s)" % percept, action, env.world_state(),
            reward, env.score, env.clean_credit))

    print()
    print("Final state   : %s" % env.world_state())
    print("Performance   : score = %d   (clean-square credit = %d over %d steps)"
          % (env.score, env.clean_credit, steps))
    return env.score


if __name__ == "__main__":
    print("=" * 96)
    print("EXPERIMENT 1 - SIMPLE REFLEX AGENT - VACUUM-CLEANER WORLD")
    print("=" * 96)
    print()

    print(">>> RUN 1 : both squares initially Dirty, agent starts at A, 10 steps")
    print()
    env = VacuumEnvironment(status={"A": DIRTY, "B": DIRTY}, location="A")
    run(env, simple_reflex_agent, steps=10)

    print()
    print("=" * 96)
    print(">>> RUN 2 : only B dirty, agent starts at A, 10 steps")
    print()
    env2 = VacuumEnvironment(status={"A": CLEAN, "B": DIRTY}, location="A")
    run(env2, simple_reflex_agent, steps=10)

    print()
    print("=" * 96)
    print(">>> RUN 3 : effect of the horizon - same start, increasing step budget")
    print()
    print("%-8s | %-12s | %s" % ("Steps", "Final score", "Clean-square credit"))
    print("-" * 48)
    for n in (2, 5, 10, 20, 50, 100):
        e = VacuumEnvironment(status={"A": DIRTY, "B": DIRTY}, location="A")
        for _ in range(n):
            e.execute(simple_reflex_agent(e.percept()))
            e.tick_clean_credit()
        print("%-8d | %-12d | %d" % (n, e.score, e.clean_credit))
    print()
    print("The score falls by 1 for every step after the world is clean:")
    print("the reflex agent oscillates A -> B -> A -> ... for ever.")

    print()
    print("=" * 96)
    print(">>> RUN 4 : control - can a different rule table fix it without memory?")
    print("            rules: Dirty -> Suck, Clean -> NoOp;  world: only B dirty")
    print()
    env4 = VacuumEnvironment(status={"A": CLEAN, "B": DIRTY}, location="A")
    run(env4, noop_when_clean_agent, steps=10)
    print()
    print("It stops paying the movement cost, but it never reaches B either:")
    print("B stays dirty for ever.  The percept (A, Clean) has to be mapped to")
    print("exactly one action, and the same percept occurs both when the world")
    print("is finished and when B is still dirty.  No memoryless rule table can")
    print("be right in both cases - the limitation is the architecture, not the")
    print("choice of rules.")
