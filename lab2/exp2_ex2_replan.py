import os

from exp2_bfs_agent import (
    GridEnvironment, DeliberativeAgent, plan_marks, manhattan,
    GRID_MAIN, HERE, OUTDIR,
)


def run_with_replanning(env, agent, block_cell, block_after_step, trace=True):

    agent.make_plan(env.start, env.goal)

    successful_moves = 0
    blocked_announced = False
    replans = 0
    trail = [env.location]

    while not env.at_goal():
        if not agent.has_plan_left():
            return False, replans, trail

        if (not blocked_announced and successful_moves >= block_after_step
                and block_cell != env.location):
            env.block(block_cell)
            blocked_announced = True

        before = env.location
        action = agent.peek_action()
        moved, contents = env.execute(action)
        agent.cursor += 1

        if moved:
            successful_moves += 1
            trail.append(env.location)
        else:
            blocked_cell = (before[0] + {"Up": -1, "Down": 1}.get(action, 0),
                            before[1] + {"Left": -1, "Right": 1}.get(action, 0))
            agent.model.set(blocked_cell, "#")
            agent.make_plan(env.location, env.goal)
            replans += 1

    return True, replans, trail


if __name__ == "__main__":
    print("EXERCISE 2 - BLOCK A CELL MID-PLAN; DETECT THE FAILURE; RE-PLAN")
    print()

    env = GridEnvironment(GRID_MAIN)
    agent = DeliberativeAgent(GRID_MAIN)


    BLOCK_CELL = (0, 3)
    BLOCK_AFTER = 1

    reached, replans, trail = run_with_replanning(env, agent, BLOCK_CELL, BLOCK_AFTER)

    print("Grid (X = cell that gets blocked mid-plan):")
    print(env.grid.render({BLOCK_CELL: "X"}))
    print()
    print("Actual path taken, including the detour after re-planning:")
    print(env.grid.render(dict((c, "*") for c in trail)))
    print()
    print("Goal reached: %s   steps: %d   bumps: %d   re-plans: %d"
          % (reached, env.steps, env.bumps, replans))


    env2 = GridEnvironment(GRID_MAIN)
    agent2 = DeliberativeAgent(GRID_MAIN)
    reached2, replans2, trail2 = run_with_replanning(
        env2, agent2, (7, 5), block_after_step=14)


    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "replan_data.txt"), "w", encoding="utf-8") as fh:
        fh.write("reached %d\n" % (1 if reached else 0))
        fh.write("replans %d\n" % replans)
        fh.write("steps %d\n" % env.steps)
        fh.write("bumps %d\n" % env.bumps)

