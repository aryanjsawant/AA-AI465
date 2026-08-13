"""
Experiment 1 - Exercise 1
Model-based reflex agent : remembers the status of both squares and executes a
no-op once everything is known to be clean.  Scores are compared over 20 steps.

Agentic AI (IA462), SVNIT Surat.  Standard library only; no agent framework.
"""

from exp1_reflex_agent import (
    VacuumEnvironment, simple_reflex_agent,
    CLEAN, DIRTY, SUCK, LEFT, RIGHT, NOOP,
)


# --------------------------------------------------------------------------- #
# The model-based agent.  It is NOT a pure function: it carries a model of the
# world between calls.  The model is built only from percepts it has actually
# received - it never reads the environment's private state.
# --------------------------------------------------------------------------- #
class ModelBasedReflexAgent:
    """Reflex rules + internal state (a belief about both squares)."""

    def __init__(self):
        # "Unknown" until the agent has visited the square itself.
        self.model = {"A": "Unknown", "B": "Unknown"}

    def __call__(self, percept):
        location, status = percept

        # ---- update internal state from the percept --------------------- #
        self.model[location] = status

        # ---- condition-action rules over the MODEL, not just the percept - #
        if status == DIRTY:
            self.model[location] = CLEAN     # sucking will clean it
            return SUCK
        if all(v == CLEAN for v in self.model.values()):
            return NOOP                      # nothing left to do: stop moving
        return RIGHT if location == "A" else LEFT

    def dump(self):
        return "{A: %s, B: %s}" % (self.model["A"], self.model["B"])


def run_agent(env, agent, steps, label, show_model=False):
    print("%s" % label)
    header = "%-5s | %-16s | %-6s | %-25s | %-6s | %s" % (
        "Step", "Percept", "Action", "Resulting world state", "Score",
        "Agent's internal model" if show_model else "CleanCredit")
    print(header)
    print("-" * len(header))
    for t in range(1, steps + 1):
        percept = env.percept()
        action = agent(percept)
        env.execute(action)
        env.tick_clean_credit()
        tail = agent.dump() if show_model else str(env.clean_credit)
        print("%-5d | %-16s | %-6s | %-25s | %+6d | %s" % (
            t, "(%s, %s)" % percept, action, env.world_state(),
            env.score, tail))
    print("Final : %s   score = %+d   clean-square credit = %d"
          % (env.world_state(), env.score, env.clean_credit))
    print()
    return env.score, env.clean_credit


if __name__ == "__main__":
    STEPS = 20
    START = {"A": DIRTY, "B": DIRTY}

    print("=" * 100)
    print("EXERCISE 1 - SIMPLE REFLEX  vs  MODEL-BASED REFLEX  (20 steps)")
    print("=" * 100)
    print()

    env_a = VacuumEnvironment(status=START, location="A")
    s_reflex, c_reflex = run_agent(
        env_a, simple_reflex_agent, STEPS,
        ">>> A. Simple reflex agent (no internal state)")

    env_b = VacuumEnvironment(status=START, location="A")
    s_model, c_model = run_agent(
        env_b, ModelBasedReflexAgent(), STEPS,
        ">>> B. Model-based reflex agent (remembers both squares)",
        show_model=True)

    print("=" * 100)
    print("COMPARISON OVER %d STEPS" % STEPS)
    print("=" * 100)
    print("%-32s | %-12s | %s" % ("Agent", "Task score", "Clean-square credit"))
    print("-" * 74)
    print("%-32s | %-12d | %d" % ("Simple reflex", s_reflex, c_reflex))
    print("%-32s | %-12d | %d" % ("Model-based reflex", s_model, c_model))
    print("-" * 74)
    print("%-32s | %-12d | %d" % ("Difference (model - reflex)",
                                  s_model - s_reflex, c_model - c_reflex))
    print()
    print("Both agents clean the world in the same first three steps.  After")
    print("that the simple reflex agent pays -1 per step for ever, while the")
    print("model-based agent recognises that its model shows both squares")
    print("Clean and issues NoOp at zero cost.")
