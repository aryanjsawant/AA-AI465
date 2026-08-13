"""
Builds the lab record for Experiment 1 as a Word document.

    python make_report.py U21AI001

It re-runs all three programs, captures the output of THIS machine's execution,
and writes LAB_1_<ROLL_NO>.doc next to this script.  The .doc is Word HTML:
double-click it and Word opens it as a normal editable document.

Standard library only.
"""

import html
import os
import platform
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")

DEFAULT_ROLL = "U23AI042"
STUDENT_NAME = ""          # optional: put your name here


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def run_program(script):
    """Execute a program and capture exactly what it printed."""
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


# --------------------------------------------------------------------------- #
# the document
# --------------------------------------------------------------------------- #
def build(roll):
    src_main = read(os.path.join(HERE, "exp1_reflex_agent.py"))
    src_ex1 = read(os.path.join(HERE, "exp1_ex1_model_based.py"))
    src_ex2 = read(os.path.join(HERE, "exp1_ex2_corridor.py"))
    src_ex3 = read(os.path.join(HERE, "exp1_ex3_stochastic_dirt.py"))

    o_main = run_program("exp1_reflex_agent.py")
    o_ex1 = run_program("exp1_ex1_model_based.py")
    o_ex2 = run_program("exp1_ex2_corridor.py")
    o_ex3 = run_program("exp1_ex3_stochastic_dirt.py")

    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    env_line = ("Python %s on %s (%s), executed %s"
                % (platform.python_version(), platform.system(),
                   platform.machine(), stamp))

    P = []
    A = P.append

    # ---------------------------------------------------------------- title #
    A("<div class=WordSection1>")
    A("<p class=inst>Sardar Vallabhbhai National Institute of Technology "
      "(SVNIT), Surat</p>")
    A("<p class=dept>Department of Artificial Intelligence</p>")
    A("<p class=course>Agentic AI (IA462) &mdash; Semester VIII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "1", stamp.split(",")[0]]]))
    A("<h1>Experiment 1</h1>")
    A("<h1 class=sub>Simple Reflex (Reactive) Agent &mdash; "
      "The Vacuum-Cleaner World</h1>")

    # ------------------------------------------------------------------ aim #
    A("<h2>Aim</h2>")
    A("<p>To implement a reactive agent that maps percepts directly to actions "
      "through condition&ndash;action rules, and to measure its behaviour with "
      "a performance score in a simulated environment.</p>")

    # --------------------------------------------------------------- theory #
    A("<h2>Theory</h2>")
    A("<p>An agent is anything that perceives its environment through sensors "
      "and acts upon it through actuators. The <i>simple reflex agent</i> is "
      "the smallest architecture that still earns the name. It holds a fixed "
      "set of condition&ndash;action rules, matches the current percept "
      "against the conditions, and executes the action of the rule that fires. "
      "It stores no history, builds no model of the world and performs no "
      "look-ahead, so its behaviour is a pure function of the percept it is "
      "looking at at this instant: the same percept always produces the same "
      "action, whatever happened before.</p>")
    A("<p>Russell and Norvig's vacuum-cleaner world is the standard testbed "
      "for this architecture. There are two squares, A and B; each is either "
      "Clean or Dirty; the agent occupies one of them and can Suck, move Left, "
      "move Right, or do nothing. Cleaning is rewarded and movement costs "
      "energy, so the agent cannot simply thrash about and still score well.</p>")
    A("<p>This experiment also fixes the agent&ndash;environment interface that "
      "every later experiment reuses. The environment object owns the truth: "
      "the dirt status of both squares, the agent's location and the score. It "
      "exposes exactly two operations to the outside world &mdash; "
      "<span class=m>percept()</span>, which returns what the sensors can see, "
      "and <span class=m>execute(action)</span>, which applies an actuator "
      "command and returns the reward it earned. The agent is a plain Python "
      "function that receives the percept and returns an action; it never "
      "reads the environment's attributes. Everything the agent knows, it "
      "knows because it was told through a percept.</p>")
    A("<p>The instructive part of the experiment is the failure mode. Because "
      "the percept <span class=m>(A, Clean)</span> carries no information about "
      "square B, the rule table must map it to one fixed action. Mapping it to "
      "<i>Right</i> makes the agent oscillate for ever once both squares are "
      "clean, bleeding one point per step; mapping it to <i>NoOp</i> makes the "
      "agent freeze on square A and never discover that B is dirty. Both runs "
      "are reproduced below. The fix is not a better rule table &mdash; it is "
      "internal state, which is Experiment 2.</p>")

    A("<p class=cap>Table 1. PEAS description of the task environment.</p>")
    A(table(["PEAS component", "Specification for this experiment"],
            [["Performance measure",
              "+10 for each successful Suck and &minus;1 for every movement "
              "(energy cost), as prescribed by the algorithm. The PEAS-level "
              "measure of the manual &mdash; +1 for each clean square at each "
              "time step &mdash; is also tracked, in the column "
              "<span class=m>CleanCredit</span>, so that the two views of "
              "&quot;performance&quot; can be compared."],
             ["Environment",
              "Two squares A and B, each Clean or Dirty; deterministic, static "
              "(until Exercise 3), discrete, and fully observable only "
              "locally &mdash; the agent sees the square it stands on and "
              "nothing else."],
             ["Actuators", "Suck, Left, Right, NoOp"],
             ["Sensors",
              "Location sensor and dirt sensor, giving the percept "
              "(location, status)"]],
            widths=["25%", "75%"]))

    A("<p class=cap>Table 2. The condition&ndash;action rule table implemented "
      "in <span class=m>simple_reflex_agent()</span>.</p>")
    A(table(["Rule", "Condition (percept)", "Action"],
            [["R1", "(any square, Dirty)", "Suck"],
             ["R2", "(A, Clean)", "Right"],
             ["R3", "(B, Clean)", "Left"]],
            widths=["10%", "55%", "35%"]))

    # ------------------------------------------------------------ algorithm #
    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Build an environment class holding the dirt status of both "
      "locations, the agent's location and a performance score.</li>"
      "<li>Implement <span class=m>percept()</span>, returning "
      "(location, status), and <span class=m>execute(action)</span>, applying "
      "Suck / Left / Right with rewards +10 and &minus;1.</li>"
      "<li>Implement the agent as a pure function: if the current square is "
      "dirty then Suck, otherwise move to the other square.</li>"
      "<li>Run the perception&ndash;action loop for a fixed number of steps: "
      "perceive, decide, act, score the time step.</li>"
      "<li>Report the initial state, the percept&ndash;action trace of every "
      "step, and the final state with the performance score.</li>"
      "</ol>")
    A("<p>The loop itself is four lines, and they are the whole of agency at "
      "this level:</p>")
    A(code("for t in range(1, steps + 1):\n"
           "    percept = env.percept()          # 1. perceive\n"
           "    action  = agent(percept)         # 2. decide  (rule table)\n"
           "    reward  = env.execute(action)    # 3. act\n"
           "    env.tick_clean_credit()          # 4. score the time step\n",
           size="9pt"))

    # ---------------------------------------------------- program and result #
    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<h3>Program &mdash; exp1_reflex_agent.py</h3>")
    A(code(src_main))

    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A("<p class=cap>Snapshot of the console output "
      "(%s).</p>" % html.escape(env_line))
    A(out(o_main))

    # ----------------------------------------------------------observations #
    A(PAGEBREAK)
    A("<h2>Observations</h2>")
    A("<h3>1. Why the agent keeps moving after both squares are clean</h3>")
    A("<p>The agent has exactly one input, the percept of the square it stands "
      "on, and that percept does not mention the other square. At step 5 of "
      "RUN 1 the agent perceives <span class=m>(A, Clean)</span>; it perceived "
      "exactly the same thing at step 2, when B was still dirty. Nothing in "
      "the agent distinguishes the two situations, so it must take the same "
      "action in both. Rule R2 says <i>Right</i>, and it says <i>Right</i> for "
      "ever: the agent walks A &rarr; B &rarr; A &rarr; B, paying &minus;1 a "
      "step for work it has already finished.</p>")
    A("<p>RUN 4 is the control that shows this is not a bad choice of rules. "
      "Replacing R2 and R3 with &quot;if Clean then NoOp&quot; does stop the "
      "oscillation &mdash; and in a world where only B is dirty the agent then "
      "sits on the clean square A for all ten steps, scores 0 and leaves B "
      "dirty for ever. One memoryless table wastes energy; the other never "
      "finishes the job. Since both worlds present the identical percept "
      "<span class=m>(A, Clean)</span>, no memoryless table can be correct in "
      "both. The limitation is architectural.</p>")

    A("<h3>2. How the performance score changes with the number of steps</h3>")
    A("<p>RUN 3 measures this directly. Starting from both squares dirty, the "
      "agent needs three steps to clean the world (Suck, Right, Suck) and "
      "reaches its maximum score of +19 at step 3. Every step after that is a "
      "movement, so for a horizon of <i>n</i> &ge; 3 steps the final score is "
      "exactly</p>")
    A("<p class=eq>score(n) = 19 &minus; (n &minus; 3)</p>")
    A("<p>which is +12 at n = 10, +2 at n = 20, &minus;28 at n = 50 and "
      "&minus;78 at n = 100. The score crosses zero at n = 22 and then falls "
      "without bound: the agent's lifetime performance is a strictly "
      "decreasing function of how long it is allowed to live, because it has "
      "no way to recognise that it is done. Under the PEAS-style measure the "
      "picture inverts &mdash; <span class=m>CleanCredit</span> grows by +2 "
      "per step once the world is clean, so the same behaviour looks perfect. "
      "Which agent is &quot;good&quot; is decided by the performance measure, "
      "not by the agent; this is the point of insisting that rationality is "
      "always relative to a stated measure.</p>")

    A("<h3>3. What this says about the need for internal state</h3>")
    A("<p>The agent's trouble is not that its rules are wrong but that its "
      "percept is smaller than the state it needs to act on. The world has "
      "four states (A/B &times; the two dirt bits); the agent can distinguish "
      "only two percepts per location. Two bits of memory &mdash; a remembered "
      "status for A and for B &mdash; close that gap exactly, and Exercise 1 "
      "measures what they are worth: +19 against +2 over twenty steps, with "
      "the gap widening by one point per additional step for ever. That is the "
      "step from the reflex agent to the model-based reflex agent, and it is "
      "the smallest amount of state that buys anything at all.</p>")

    # ------------------------------------------------------------ exercise 1 #
    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Model-based variant, compared over 20 steps</h2>")
    A("<p><b>Task.</b> Add a model-based variant that remembers the status of "
      "both squares and executes a no-op once everything is known to be clean; "
      "compare scores over 20 steps.</p>")
    A("<p><b>Approach.</b> The agent becomes an object rather than a pure "
      "function, because it now carries state between calls. Its model is a "
      "dictionary <span class=m>{A: Unknown, B: Unknown}</span>, filled in only "
      "from percepts the agent has actually received &mdash; it never reads the "
      "environment. When the agent sucks it records the square as Clean, since "
      "it knows the effect of its own action; this is the &quot;model of how "
      "the world evolves&quot; half of the model-based architecture. The rules "
      "then fire on the model rather than on the bare percept, which is what "
      "makes the NoOp decision possible.</p>")
    A("<h3>Program &mdash; exp1_ex1_model_based.py</h3>")
    A(code(src_ex1))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex1))
    A("<h3>Discussion</h3>")
    A("<p>Both agents behave identically for the first three steps and clean "
      "the world at the same moment; the model-based agent is not a better "
      "cleaner. The difference is entirely in knowing when to stop. At step 3 "
      "the model reads <span class=m>{A: Clean, B: Clean}</span>, the NoOp rule "
      "fires, and the score freezes at +19 while the reflex agent's decays to "
      "+2. The gap after n steps is (n &minus; 3) points and grows without "
      "limit.</p>")
    A("<p>The <span class=m>CleanCredit</span> column is worth reading beside "
      "it: both agents score 38 there, because both left the world clean. The "
      "two agents are indistinguishable under one performance measure and "
      "differ by 17 points under the other. Memory bought nothing about the "
      "state of the world &mdash; it bought the ability to stop paying for "
      "actions that no longer achieve anything.</p>")
    A("<p>One caveat visible in the trace: the model-based agent's belief is "
      "only sound because the environment is static. Nothing else in the world "
      "changes the squares, so a fact recorded once stays true. Exercise 3 "
      "removes that guarantee and the same agent becomes the worst of the "
      "four.</p>")

    # ------------------------------------------------------------ exercise 2 #
    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; A 1 &times; N corridor</h2>")
    A("<p><b>Task.</b> Extend the world to a 1 &times; N corridor of N squares "
      "with random initial dirt and adapt the rules.</p>")
    A("<p><b>Approach.</b> The environment generalises to a list of N squares; "
      "the percept grows two boolean wall sensors, "
      "<span class=m>(location, status, at_left_wall, at_right_wall)</span>, "
      "because an agent that cannot feel a wall cannot even turn round. Three "
      "agents are compared on the identical world (seeded, so the dirt layout "
      "is reproducible):</p>")
    A("<ul>"
      "<li><b>A. Naive reflex</b> &mdash; Dirty &rarr; Suck; at the right wall "
      "&rarr; Left; otherwise &rarr; Right. Memoryless, the direct "
      "generalisation of the two-square rules.</li>"
      "<li><b>B. Reflex + heading</b> &mdash; the same rules plus a single bit "
      "of state, the direction the agent is currently travelling, flipped at "
      "each wall.</li>"
      "<li><b>C. Model-based</b> &mdash; a belief over all N squares plus the "
      "heading; NoOp once every square is believed clean.</li>"
      "</ul>")
    A("<h3>Program &mdash; exp1_ex2_corridor.py</h3>")
    A(code(src_ex2))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex2))
    A("<h3>Discussion</h3>")
    A("<p>Scenario 1 is deliberately flattering: the agent starts at the left "
      "wall, so &quot;always go Right unless at the right wall&quot; happens to "
      "sweep the whole corridor, and agents A and B score identically (+24). "
      "The rule looks adequate.</p>")
    A("<p>Scenario 2 starts the same agent in the middle and the naive rule "
      "collapses. It sweeps rightwards, bounces off the right wall, and then "
      "&mdash; having no memory of where it came from &mdash; the rule "
      "&quot;not at the right wall, so go Right&quot; fires again and sends it "
      "straight back. It is trapped oscillating between the last two squares "
      "for the rest of its life, and the two dirty squares to its left are "
      "never cleaned: final score +2 with 2 squares still dirty, against +24 "
      "and a clean corridor for the agent that carries one extra bit. In the "
      "scaling table this holds for every N tested: the naive agent leaves 2 "
      "or 3 squares dirty, both stateful agents leave none.</p>")
    A("<p>This is a sharper version of the two-square lesson. In the two-square "
      "world memorylessness cost energy; here it costs correctness &mdash; part "
      "of the task simply never gets done, no matter how long the agent runs. "
      "It is also a useful piece of engineering intuition: the heading bit is "
      "the cheapest state imaginable, and it converts a broken agent into a "
      "complete one. The full belief over N squares adds one further thing, "
      "termination, worth another 9 to 11 points over 20 steps.</p>")

    # ------------------------------------------------------------ exercise 3 #
    A(PAGEBREAK)
    A("<h2>Exercise 3 &mdash; Dirt reappears with probability 0.1 per step</h2>")
    A("<p><b>Task.</b> Make dirt reappear with probability 0.1 per step and "
      "discuss whether the reflex agent is now rational.</p>")
    A("<p><b>Approach.</b> After the agent acts, every clean square is "
      "re-dirtied independently with probability p. The world is now "
      "<i>dynamic</i>: it changes while the agent is deliberating, and a fact "
      "the agent recorded a moment ago may already be false. Four agents are "
      "run against the same seeded stream of re-dirtying events, so any "
      "difference in score is caused by the policy and not by luck:</p>")
    A("<ul>"
      "<li><b>Simple reflex</b> &mdash; the original memoryless agent.</li>"
      "<li><b>Model-based + NoOp</b> &mdash; the winner of Exercise 1, "
      "unchanged.</li>"
      "<li><b>Model-based + decay(3)</b> &mdash; the same agent, except that a "
      "square it has not seen for 3 steps is demoted back to Unknown, so a "
      "stale belief stops justifying a NoOp.</li>"
      "<li><b>Lazy</b> &mdash; never moves, sucks whatever it is standing on. "
      "A do-nothing baseline that any claim of rationality has to beat.</li>"
      "</ul>")
    A("<h3>Program &mdash; exp1_ex3_stochastic_dirt.py</h3>")
    A(code(src_ex3))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex3))
    A("<h3>Discussion &mdash; is the reflex agent rational now?</h3>")
    A("<p>A rational agent is one that, for each percept sequence, selects the "
      "action expected to maximise the performance measure, given the evidence "
      "of its percepts and whatever knowledge it has built in. Rationality is "
      "therefore relative to four things &mdash; the measure, the environment, "
      "the actuators and the sensors &mdash; and three of those have just "
      "changed. The honest answer the numbers support is: <b>the reflex agent "
      "is no longer dominated, but it is still not rational.</b></p>")
    A("<p><b>What improved.</b> In the static world, movement after cleaning "
      "was pure waste. In the stochastic world the agent's sensors are local, "
      "so moving is the only way to <i>find out</i> whether the other square "
      "has become dirty: patrolling is now sensing as well as travelling, and "
      "it pays for itself. Over 200 runs of 30 steps the reflex agent goes "
      "from being 17 points behind the model-based NoOp agent at p = 0 to "
      "ahead of it by p = 0.10 (47.16 against 45.65), and far ahead at p = 0.40 "
      "(163.54 against 133.70). On the PEAS measure, cleanliness of the world "
      "per time step, the reflex agent is the best of the four at every "
      "non-zero p.</p>")
    A("<p><b>What did not improve.</b> The reflex agent still never weighs the "
      "&minus;1 cost of a move against the probability of finding dirt at the "
      "other end. At small p that is a real error, and the lazy baseline "
      "exposes it: at p = 0.02 doing nothing scores 14.85 while patrolling "
      "scores 3.44. An agent that walks back and forth to check a square that "
      "is dirty two per cent of the time is not behaving rationally, it is "
      "merely behaving. A rational policy here would depend on p and on the "
      "ratio of the suck reward to the movement cost, and would need to be "
      "derived, not guessed &mdash; which is the decision-theoretic agent, not "
      "the reflex agent.</p>")
    A("<p><b>The most interesting casualty is memory.</b> The model-based agent "
      "that won Exercise 1 is the worst performer on cleanliness at every "
      "non-zero p (38.38 at p = 0.10 against the reflex agent's 54.53). Its "
      "model is not wrong when it is written; it goes stale, and the agent "
      "keeps acting on it, sitting still and issuing NoOp while both squares "
      "quietly turn dirty behind its back. Adding a three-step decay to the "
      "same belief fixes it and produces the best agent in the table over the "
      "whole middle range of p (58.03 at p = 0.10). The lesson is that internal "
      "state is only an asset if the agent also knows how fast it rots &mdash; "
      "in a dynamic environment a model needs a refresh policy, and that is "
      "precisely the sensing/updating machinery the later experiments "
      "build.</p>")

    # ------------------------------------------------------------ conclusion #
    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>A simple reflex agent for the vacuum-cleaner world was implemented "
      "from first principles: an environment owning the true state and exposing "
      "only <span class=m>percept()</span> and "
      "<span class=m>execute(action)</span>, an agent that is a pure function "
      "from percept to action, and a perception&ndash;action loop connecting "
      "the two. The agent cleans both squares in three steps and reaches its "
      "peak score of +19, after which it oscillates for ever and loses one "
      "point per step, ending at +12 after 10 steps and &minus;78 after 100. A "
      "control run confirmed that no memoryless rule table avoids this: the "
      "alternative rules stop the oscillation only by never reaching the other "
      "square.</p>")
    A("<p>Three exercises quantified what the missing state is worth. Two bits "
      "of memory and a NoOp rule turn +2 into +19 over twenty steps "
      "(Exercise 1). In a 1 &times; N corridor started from the middle, a "
      "single heading bit is the difference between finishing the job and "
      "leaving squares permanently dirty (Exercise 2). When dirt returns with "
      "probability p, patrolling becomes sensing and the memoryless agent "
      "stops being dominated, while the agent with an un-refreshed model "
      "becomes the worst of the four; a belief with a decay rule is best "
      "(Exercise 3).</p>")
    A("<p>The general point carried into the later experiments is that agent "
      "architecture, performance measure and environment cannot be judged "
      "separately. The same agent is excellent under one measure and terrible "
      "under another, and the same memory is an asset in a static world and a "
      "liability in a dynamic one.</p>")

    # ------------------------------------------------------------ appendix #
    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "exp1_reflex_agent.py, exp1_ex1_model_based.py, "
              "exp1_ex2_corridor.py, exp1_ex3_stochastic_dirt.py, "
              "make_report.py"],
             ["Libraries used",
              "Python standard library only (<span class=m>random</span>, "
              "<span class=m>subprocess</span>, <span class=m>html</span>, "
              "<span class=m>datetime</span>). No agent framework or "
              "orchestration library was used, in accordance with clause 3.1 "
              "of the Rules and Regulations."],
             ["Reproducibility",
              "All random worlds are seeded (corridor seed 7; stochastic runs "
              "seeds 1000&ndash;1199), so every figure in this record "
              "reproduces exactly. Removing the seed varies the dirt layout "
              "but not the conclusions."],
             ["Sources consulted",
              "S. Russell and P. Norvig, <i>Artificial Intelligence: A Modern "
              "Approach</i>, chapter 2 (agents, PEAS, rationality, the vacuum "
              "world); course manual for Experiment 1."]],
            widths=["22%", "78%"]))
    A("<p class=note>All output reproduced above was produced by executing the "
      "programs listed in this record on the machine and at the time stated in "
      "the table.</p>")
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
    body, env_line = build(roll)
    name = "LAB_1_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_1_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
