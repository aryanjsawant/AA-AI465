import html
import os
import platform
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")

DEFAULT_ROLL = "U23AI042"
STUDENT_NAME = ""


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def run_program(script):

    print("  running %s ..." % script)
    proc = subprocess.run([sys.executable, script], cwd=HERE,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("%s failed:\n%s" % (script, proc.stderr))
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, script.replace(".py", ".txt")), "w",
              encoding="utf-8") as fh:
        fh.write(proc.stdout)
    return proc.stdout


def code(text, size="7.5pt"):
    return ("<pre class=code style='font-size:%s'>%s</pre>"
            % (size, html.escape(text.rstrip())))


def out(text, size="6.5pt"):
    return ("<pre class=out style='font-size:%s'>%s</pre>"
            % (size, html.escape(text.rstrip())))


def table(headers, rows, widths=None):
    w = widths or ([None] * len(headers))
    th = "".join("<th%s>%s</th>" % ((" style='width:%s'" % x) if x else "", h)
                 for h, x in zip(headers, w))
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in row)
                 for row in rows)
    return "<table class=g><tr>%s</tr>%s</table>" % (th, tr)


PAGEBREAK = "<br style='page-break-before:always'>"


def build(roll):
    src_main = read(os.path.join(HERE, "exp2_bfs_agent.py"))
    src_ex1 = read(os.path.join(HERE, "exp2_ex1_uniform_cost.py"))
    src_ex2 = read(os.path.join(HERE, "exp2_ex2_replan.py"))
    src_ex3 = read(os.path.join(HERE, "exp2_ex3_hybrid.py"))

    o_main = run_program("exp2_bfs_agent.py")
    o_ex1 = run_program("exp2_ex1_uniform_cost.py")
    o_ex2 = run_program("exp2_ex2_replan.py")
    o_ex3 = run_program("exp2_ex3_hybrid.py")

    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    env_line = ("Python %s on %s (%s), executed %s"
                % (platform.python_version(), platform.system(),
                   platform.machine(), stamp))

    P = []
    A = P.append


    A("<div class=WordSection1>")
    A("<p class=inst>Sardar Vallabhbhai National Institute of Technology "
      "(SVNIT), Surat</p>")
    A("<p class=dept>Department of Artificial Intelligence</p>")
    A("<p class=course>Agentic AI (IA462) &mdash; Semester VIII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "2", stamp.split(",")[0]]]))
    A("<h1>Experiment 2</h1>")
    A("<h1 class=sub>Deliberative (Goal-Based) Agent &mdash; "
      "Planning with Search</h1>")


    A("<h2>Aim</h2>")
    A("<p>To implement a deliberative agent that holds an internal model of "
      "a grid world, plans a complete path to its goal with breadth-first "
      "search, and then executes the plan.</p>")


    A("<h2>Theory</h2>")
    A("<p>A deliberative agent decides by reasoning over an internal world "
      "model rather than reacting to the current percept: it searches the "
      "space of action sequences for one that reaches the goal, commits to "
      "that plan, and executes it. This sense&ndash;plan&ndash;act "
      "architecture contrasts with the sense&ndash;react loop of Experiment "
      "1; hybrid architectures layer both, using reactive rules for "
      "immediate hazards and deliberation for long-horizon goals.</p>")
    A("<p>Breadth-first search over the grid guarantees a shortest path in "
      "number of steps, because its FIFO frontier expands cells in order of "
      "distance from the start: the first time a cell is reached, it has "
      "been reached by the fewest possible moves. The parent map built "
      "during search doubles as the plan &mdash; walking it backwards from "
      "the goal and reversing yields the action sequence. Separating the "
      "planning phase (over the model) from the execution phase (in the "
      "world) exposes deliberation's central assumption: that the model is "
      "correct and the world does not change mid-plan. Each exercise below "
      "deliberately breaks a different part of that assumption.</p>")
    A("<p>The agent&ndash;environment interface follows Experiment 1's "
      "pattern. The environment owns the true grid, the agent's position "
      "and the step count, and exposes only "
      "<span class=m>percept()</span> &mdash; LOCAL sensing of the four "
      "neighbouring cells, never the whole map &mdash; and "
      "<span class=m>execute(action)</span>. The agent owns a separate "
      "MODEL: its private belief about what the grid looks like. It plans "
      "over the model and acts in the world. In the reference program the "
      "two happen to agree exactly, which is precisely the assumption a "
      "purely deliberative agent depends on.</p>")

    A("<p class=cap>Table 1. PEAS description of the task environment.</p>")
    A(table(["PEAS component", "Specification for this experiment"],
            [["Performance measure",
              "Reaching the goal cell in as few steps (Reference, Exercise "
              "2, 3) or as little accumulated terrain cost (Exercise 1) as "
              "possible; correctly reporting failure when no path exists."],
             ["Environment",
              "A grid of free cells, walls and (Exercise 3) pits; static in "
              "the reference program and Exercises 1 and 3, made dynamic in "
              "Exercise 2 when a cell is blocked mid-execution; fully "
              "observable to the PLANNER (which reads the whole model) but "
              "only LOCALLY observable to the agent's sensors during "
              "execution."],
             ["Actuators", "Up, Down, Left, Right (attempted moves)"],
             ["Sensors",
              "Local percept: current position and the contents of the four "
              "neighbouring cells"]],
            widths=["25%", "75%"]))

    A("<p class=cap>Table 2. Contrast between the two architectures used in "
      "this record.</p>")
    A(table(["Property", "Reactive (Experiment 1)", "Deliberative (this experiment)"],
            [["Decides from", "the current percept only", "a search over an internal model"],
             ["Memory", "none (pure function)", "a committed multi-step plan"],
             ["Look-ahead", "none", "full, up to the goal"],
             ["Handles a changing world", "immediately (every step is fresh)",
              "only if failure detection + re-planning is added (Exercise 2)"],
             ["Optimality", "not guaranteed",
              "guaranteed in steps (BFS) or cost (UCS, Exercise 1), given a "
              "correct model"]],
            widths=["22%", "34%", "44%"]))


    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Encode the world as a character grid with start S, goal G and "
      "obstacles #; this grid is the agent's internal model.</li>"
      "<li>Run BFS from S, recording for each visited cell its parent and "
      "the move that reached it.</li>"
      "<li>Reconstruct the action sequence by following parents back from "
      "G and reversing.</li>"
      "<li>Execute the plan step by step and verify the goal is "
      "reached.</li>"
      "</ol>")
    A("<p>The planner and the executor are two separate loops, and keeping "
      "them separate is the whole point of the experiment:</p>")
    A(code("# planning phase - all inside the agent's head, before any action\n"
           "def breadth_first_plan(model, start, goal):\n"
           "    frontier = deque([start]); parent = {start: None}\n"
           "    while frontier:\n"
           "        cell = frontier.popleft()\n"
           "        if cell == goal:\n"
           "            return reconstruct(parent, goal)   # walk back, reverse\n"
           "        for action, nxt in neighbours(model, cell):\n"
           "            if nxt not in parent:\n"
           "                parent[nxt] = (cell, action); frontier.append(nxt)\n\n"
           "# execution phase - runs afterwards, one action at a time, in the world\n"
           "while agent.has_plan_left():\n"
           "    action = agent.next_action()\n"
           "    moved, contents = env.execute(action)\n",
           size="8.5pt"))


    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<h3>Program &mdash; exp2_bfs_agent.py</h3>")
    A(code(src_main))

    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A("<p class=cap>Snapshot of the console output "
      "(%s).</p>" % html.escape(env_line))
    A(out(o_main))

    A(PAGEBREAK)
    A("<p class=cap>Figure 1. The BFS plan through the spiral maze (left) "
      "and the outcome comparison against a greedy-reactive baseline "
      "(right). Generated by make_plots.py from this run's own data.</p>")
    A("<img src='outputs/exp2_reference.png' style='width:100%25;'>")


    A(PAGEBREAK)
    A("<h2>Observations</h2>")
    A("<h3>1. Why BFS's plan is provably shortest, and how the frontier "
      "proves an unreachable goal</h3>")
    A("<p>Because the frontier is a FIFO queue, cells are expanded in "
      "non-decreasing order of distance from S. The first time any cell is "
      "reached, that arrival used the fewest possible edges &mdash; a later, "
      "longer route to the same cell is simply never recorded, since "
      "<span class=m>parent[nxt]</span> is only set once. RUN 1 confirms "
      "this: the distance map printed alongside the plan shows the cell "
      "(5,5) at distance 22, and the executed plan is exactly 22 actions "
      "long. RUN 4 shows the same mechanism used negatively &mdash; sealing "
      "the one doorway into the goal chamber empties the queue after "
      "visiting every reachable cell, which is a proof of unreachability, "
      "not a search failure.</p>")

    A("<h3>2. Why a reactive agent cannot solve this maze at all</h3>")
    A("<p>RUN 3's greedy-reactive baseline always steps into whichever "
      "passable neighbour is closest to the goal in Manhattan distance. It "
      "reaches cell (2,5) and stalls: every one of its passable neighbours "
      "is <i>farther</i> from the goal, so the rule has no admissible move "
      "and repeats the same two-cell oscillation, detected and reported "
      "after three repeats. The spiral's shortest route requires walking "
      "twelve steps around a ring, most of them increasing the Manhattan "
      "distance &mdash; a commitment no locally-greedy rule can make, "
      "because it never looks further than one step ahead. This is the "
      "direct, concrete version of viva question 1's contrast.</p>")

    A("<h3>3. The cost of planning: cells expanded vs. plan length</h3>")
    A("<p>RUN 1 expands 68 of the maze's 75 passable cells to find a "
      "22-step plan &mdash; BFS pays for its optimality guarantee by "
      "visiting nearly every reachable cell once, not just the ones on the "
      "final path. This is the standard trade-off uninformed search makes: "
      "correctness and optimality in exchange for exploring the whole "
      "reachable state space, which motivates A* (viva question 2) once a "
      "heuristic that estimates remaining distance is available &mdash; "
      "A* would expand only the cells plausibly on a shortest route, not "
      "every reachable cell.</p>")


    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Uniform-cost search over a terrain-weighted grid</h2>")
    A("<p><b>Task.</b> Replace BFS with uniform-cost search where each cell "
      "has a terrain cost read from a second grid.</p>")
    A("<p><b>Approach.</b> A second character grid of digits gives the cost "
      "of <i>entering</i> each cell. The frontier becomes a priority queue "
      "keyed on accumulated cost <span class=m>g(n)</span> rather than a "
      "FIFO queue, and the goal test moves from expansion-on-first-sight to "
      "expansion-on-POP &mdash; the moment the goal is actually popped off "
      "the priority queue, its cost is provably minimal, because every "
      "cheaper alternative would have been popped first. A world is built "
      "with a block of cost-9 &quot;swamp&quot; cells directly on the "
      "geometrically shortest route, with a cost-1 detour around it, so "
      "that the two searches are forced to disagree.</p>")
    A("<h3>Program &mdash; exp2_ex1_uniform_cost.py</h3>")
    A(code(src_ex1))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex1))
    A(PAGEBREAK)
    A("<p class=cap>Figure 2. Terrain grid and the two planned paths "
      "(left three panels); true cost of each (right).</p>")
    A("<img src='outputs/exp2_ex1_uniform_cost.png' style='width:100%25;'>")
    A("<img src='outputs/exp2_ex1_cost_comparison.png' style='width:55%25; margin-top:6pt;'>")
    A("<h3>Discussion</h3>")
    A("<p>BFS, blind to the terrain grid, takes the route with the fewest "
      "hops and walks straight through the swamp, paying 22. Uniform-cost "
      "search re-routes around the swamp entirely and pays only 14, because "
      "its priority-queue key is the accumulated <i>cost</i>, not the "
      "number of moves. Executing the UCS plan through the cost-aware "
      "environment confirms the prediction exactly: the cost the "
      "environment actually pays matches the cost the planner computed "
      "before taking a single step, since both read the same terrain "
      "model.</p>")
    A("<p>This answers viva question 2's second half directly: BFS is only "
      "optimal when every action has identical cost. The moment costs "
      "differ, an uninformed search needs the priority-queue discipline of "
      "uniform-cost search (or A* once a heuristic is added) to remain "
      "optimal; BFS's FIFO order no longer corresponds to increasing true "
      "cost, so it can be, and here is, actively suboptimal.</p>")


    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; Detect a blocked cell mid-plan and re-plan</h2>")
    A("<p><b>Task.</b> After planning, block one cell of the path and make "
      "the agent detect the failure during execution and re-plan from its "
      "current position.</p>")
    A("<p><b>Approach.</b> The agent executes its original BFS plan "
      "normally. Partway through execution, the environment's "
      "<span class=m>block()</span> method &mdash; standing in for nature, "
      "not the agent &mdash; turns one of the plan's cells into a wall. "
      "The agent has no way to sense this in advance: it only discovers it "
      "when <span class=m>execute()</span> returns "
      "<span class=m>moved=False</span>. On that signal, the agent corrects "
      "the one cell in its model, discards the unexecuted tail of the old "
      "plan outright, and re-invokes BFS with its <i>current</i> location "
      "as the new start. A second, harder scenario blocks the only doorway "
      "into the goal chamber, so that re-planning legitimately finds no "
      "route and must report failure rather than loop.</p>")
    A("<h3>Program &mdash; exp2_ex2_replan.py</h3>")
    A(code(src_ex2))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex2))
    A(PAGEBREAK)
    A("<p class=cap>Figure 3. Original plan length vs. actual steps, bumps "
      "and re-plans triggered by the mid-execution block.</p>")
    A("<img src='outputs/exp2_ex2_replan.png' style='width:60%25;'>")
    A("<h3>Discussion</h3>")
    A("<p>A single bump is enough: the agent needs no richer sensing than "
      "the one bit its actuator already reports. Detection is cheap "
      "precisely because deliberative execution is already checking whether "
      "each action succeeded; the only addition is deciding what to do when "
      "it doesn't. Repair is equally direct &mdash; because BFS is fast to "
      "re-run, and because the parent map it built is discarded and rebuilt "
      "from scratch rather than patched, there is no risk of the new plan "
      "inheriting a stale assumption from the old one.</p>")
    A("<p>The harder scenario is the more informative of the two: when the "
      "sealed doorway removes the only route, re-planning from the agent's "
      "new position still returns <span class=m>found=False</span>, and the "
      "agent halts and reports failure rather than retrying the same bump "
      "forever. This is exactly viva question 3's answer: deliberative "
      "planning assumes the model stays correct and the world stays static "
      "for the whole execution. Re-planning does not remove that assumption "
      "&mdash; it narrows the window in which it must hold to a single "
      "step, by checking the assumption after every action and repairing "
      "the model the instant it is violated.</p>")


    A(PAGEBREAK)
    A("<h2>Exercise 3 &mdash; Hybrid agent: reactive pit-avoidance filters "
      "the deliberative plan</h2>")
    A("<p><b>Task.</b> Implement a hybrid agent: reactive rule &lsquo;never "
      "step into a cell adjacent to a pit&rsquo; filtering the deliberative "
      "plan.</p>")
    A("<p><b>Approach.</b> BFS plans over the grid exactly as before, with "
      "no notion of &lsquo;pit&rsquo; at all &mdash; a pit cell is simply "
      "impassable, but the cells <i>next to</i> it are ordinary free cells "
      "as far as the search is concerned, so BFS may propose walking "
      "directly alongside one. A thin reactive layer, structurally "
      "identical to Experiment 1's condition&ndash;action rule, is "
      "consulted immediately before each planned action reaches the "
      "actuators: if the proposed step would land in a cell adjacent to a "
      "pit, the layer vetoes it, marks that cell as unsafe in the model, "
      "and triggers the same on-the-spot re-plan used in Exercise 2. A "
      "third baseline plans directly on a grid with the hazard margin "
      "removed in advance, to show the same outcome is reachable either by "
      "filtering at execution time or by encoding the constraint before "
      "planning.</p>")
    A("<h3>Program &mdash; exp2_ex3_hybrid.py</h3>")
    A(code(src_ex3))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex3))
    A(PAGEBREAK)
    A("<p class=cap>Figure 4. The hazard map and a comparison of pure "
      "deliberative, hybrid and hazard-pre-planned agents.</p>")
    A("<img src='outputs/exp2_ex3_hybrid.png' style='width:100%25;'>")
    A("<h3>Discussion</h3>")
    A("<p>The pure deliberative plan (A) is shortest in principle but walks "
      "through the hazard margin three times, because BFS was never told "
      "pits matter. The hybrid agent (B) starts from that same plan and "
      "vetoes every one of the five unsafe proposals it encounters, "
      "re-planning around each one, and still reaches the goal in the same "
      "number of steps as the hazard-free baseline (C) &mdash; the safety "
      "constraint cost nothing here because a same-length safe alternative "
      "happened to exist locally at each veto point.</p>")
    A("<p>Agents B and C reach an identical outcome from opposite "
      "directions: C bakes the constraint into the model before planning "
      "even starts, which is cheaper when the hazard map is fully known in "
      "advance and static; B keeps deliberation unaware of the constraint "
      "and enforces it as a late filter, which costs a little more "
      "computation (repeated re-planning) but degrades gracefully if a "
      "hazard is discovered only during execution &mdash; exactly the "
      "situation Exercise 2 already covers. This is the concrete answer to "
      "viva question 1: the reactive layer contributes nothing about the "
      "goal (it would veto the same step on a random walk with no "
      "destination at all), and the deliberative layer contributes nothing "
      "about immediate safety once planning has finished; hybridising them "
      "assigns each concern to the architecture that handles it "
      "naturally.</p>")


    A(PAGEBREAK)
    A("<h2>Real-time execution trace</h2>")
    A("<p>The reference program also supports "
      "<span class=m>python exp2_bfs_agent.py --animate</span>, which "
      "replays the committed plan one action at a time in the terminal, "
      "redrawing the maze each step, and "
      "<span class=m>make_animation.py</span>, which renders the same "
      "replay as an animated GIF (<span class=m>outputs/exp2_animation.gif"
      "</span>) using matplotlib. Neither changes how the agent decides "
      "anything &mdash; the whole plan was already fixed by RUN 1 before "
      "the first frame is drawn &mdash; they only make the "
      "sense&ndash;plan&ndash;act separation visible: planning happens "
      "once, instantaneously from the viewer's perspective, and execution "
      "is the only part that unfolds over time.</p>")


    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>A deliberative agent was implemented from first principles: an "
      "environment exposing only local percepts and an execute-action "
      "interface, an agent holding a private model of the grid, "
      "breadth-first search building a provably shortest plan over that "
      "model, and an executor running the plan step by step. In a spiral "
      "maze designed so the shortest route spends most of its length moving "
      "away from the goal, the deliberative agent reached it in the "
      "optimal 22 steps while a greedy-reactive baseline entered a "
      "permanent two-cell loop and never arrived &mdash; a direct "
      "demonstration of why look-ahead planning, not just better local "
      "rules, is sometimes structurally necessary.</p>")
    A("<p>Three exercises then broke, one at a time, the assumptions that "
      "make plain BFS planning work. Uniform-cost search showed that BFS's "
      "shortest-path guarantee is specific to equal-cost actions, and is "
      "actively wrong (paying 22 instead of 14 in the terrain world) the "
      "moment costs differ. Re-planning showed that a single failed-move "
      "signal is enough to detect a stale model and recover by re-invoking "
      "the same planner from the agent's current position &mdash; and, when "
      "no recovery is possible, to prove that fact rather than loop. The "
      "hybrid agent showed that a reactive safety filter can sit on top of "
      "an unmodified deliberative planner, catching hazards the search "
      "itself has no concept of, at little or no cost to path length.</p>")
    A("<p>The thread connecting all three: deliberation is only as good as "
      "the model and the cost function it searches over, and only as safe "
      "as its willingness to check its own plan against a changing world. "
      "Making those checks explicit &mdash; a cost-aware frontier, a "
      "bump-triggered re-plan, a reactive veto &mdash; is what turns a "
      "one-shot planner into an agent that can actually be trusted to act "
      "in a world it does not fully control.</p>")


    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "exp2_bfs_agent.py, exp2_ex1_uniform_cost.py, "
              "exp2_ex2_replan.py, exp2_ex3_hybrid.py, make_plots.py, "
              "make_animation.py, make_report.py"],
             ["Libraries used",
              "Python standard library only (<span class=m>collections</span>, "
              "<span class=m>heapq</span>, <span class=m>itertools</span>, "
              "<span class=m>subprocess</span>, <span class=m>html</span>) "
              "for every agent program; Matplotlib (permitted, Table 1) for "
              "<span class=m>make_plots.py</span> and "
              "<span class=m>make_animation.py</span> only. No agent "
              "framework or orchestration library was used, in accordance "
              "with clause 3.1 of the Rules and Regulations."],
             ["Reproducibility",
              "All worlds are fixed character grids, and BFS/UCS expand "
              "successors in a fixed action order, so every run of every "
              "program reproduces exactly &mdash; there is no randomness in "
              "this experiment."],
             ["Sources consulted",
              "S. Russell and P. Norvig, <i>Artificial Intelligence: A "
              "Modern Approach</i>, chapters 2 and 3 (agent architectures, "
              "uninformed search, uniform-cost search); course manual for "
              "Experiment 2."]],
            widths=["22%", "78%"]))
    A("<p class=note>All output reproduced above was produced by executing "
      "the programs listed in this record on the machine and at the time "
      "stated in the table.</p>")
    A("</div>")

    return "".join(P), env_line


CSS = """
@page WordSection1 { size: 21.0cm 29.7cm; margin: 1.6cm 1.5cm 1.6cm 1.5cm; }
div.WordSection1 { page: WordSection1; }
body { font-family: 'Times New Roman', serif; font-size: 11.0pt; color: #000; }
p { margin: 0 0 7pt 0; text-align: justify; line-height: 1.25; }
p.inst { text-align: center; font-size: 13pt; font-weight: bold; margin-bottom: 2pt; }
p.dept { text-align: center; font-size: 11.5pt; font-weight: bold; margin-bottom: 2pt; }
p.course { text-align: center; font-size: 11pt; margin-bottom: 6pt; }
p.cap { font-size: 9.5pt; font-weight: bold; margin: 10pt 0 4pt 0; text-align: left; }
p.eq { text-align: center; font-style: italic; margin: 6pt 0; }
p.note { font-size: 9.5pt; font-style: italic; margin-top: 10pt; }
h1 { font-size: 14pt; text-align: center; margin: 14pt 0 4pt 0; }
h1.sub { font-size: 12.5pt; margin-top: 0; }
h2 { font-size: 12pt; margin: 14pt 0 6pt 0; border-bottom: 1px solid #888;
     padding-bottom: 2pt; }
h3 { font-size: 11pt; font-style: italic; margin: 10pt 0 4pt 0; }
ol, ul { margin: 0 0 8pt 0; }
li { margin-bottom: 3pt; text-align: justify; line-height: 1.25; }
table.g { border-collapse: collapse; width: 100%; margin: 0 0 8pt 0;
          font-size: 10pt; }
table.g th { border: 1px solid #666; background: #ececec; padding: 4pt;
             text-align: left; vertical-align: top; }
table.g td { border: 1px solid #666; padding: 4pt; vertical-align: top;
             text-align: left; }
pre.code, pre.out { font-family: Consolas, 'Courier New', monospace;
    border: 1px solid #999; background: #f6f6f6; padding: 5pt;
    white-space: pre; line-height: 1.15; margin: 0 0 8pt 0; }
pre.out { background: #fbfbfb; }
span.m { font-family: Consolas, 'Courier New', monospace; font-size: 9.5pt; }
hr { border: 0; border-top: 1.5px solid #000; margin: 4pt 0 8pt 0; }
img { border: 1px solid #999; }
"""

TEMPLATE = """<html xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:w="urn:schemas-microsoft-com:office:word"
xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<!--[if gte mso 9]><xml><w:WordDocument>
<w:View>Print</w:View><w:Zoom>100</w:Zoom>
</w:WordDocument></xml><![endif]-->
<style>%(css)s</style>
</head>
<body>%(body)s</body>
</html>
"""


if __name__ == "__main__":
    roll = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROLL


    subprocess.run([sys.executable, "make_plots.py"], cwd=HERE, check=True)

    body, env_line = build(roll)
    name = "LAB_2_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_2_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")

