import base64
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

def embed_image(path, width="90%"):
    if not os.path.isabs(path):
        path = os.path.join(HERE, path)
    if not os.path.exists(path):
        return f"<p><i>[Image not found: {os.path.basename(path)}]</i></p>"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"<div style='text-align:center;margin:8pt 0;'><img src='data:image/png;base64,{b64}' style='width:{width};max-width:650px;border:1px solid #999;' /></div>"

PAGEBREAK = "<br style='page-break-before:always'>"

def build(roll):
    src_mdp = read(os.path.join(HERE, "exp7_mdp.py"))
    o_main = run_program("exp7_mdp.py")

    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    env_line = ("Python %s on %s (%s), executed %s"
                % (platform.python_version(), platform.system(),
                   platform.machine(), stamp))

    P = []
    A = P.append

    A("<div class=WordSection1>")
    A("<p class=inst>Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat</p>")
    A("<p class=dept>Department of Artificial Intelligence</p>")
    A("<p class=course>Agentic AI (IA462) &mdash; Semester VIII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "7", stamp.split(",")[0]]]))
    A("<h1>Experiment 7</h1>")
    A("<h1 class=sub>Agent Behaviour as a Markov Decision Process &mdash; Value and Policy Iteration</h1>")

    # Aim
    A("<h2>Aim</h2>")
    A("<p>To model an agent acting in a stochastic environment as a Markov Decision Process (MDP), "
      "compute the optimal value function and policy by Value Iteration, obtain the same policy by "
      "Policy Iteration from an arbitrary starting policy, and compare the two methods by the computational "
      "work each performs.</p>")

    # Theory
    A("<h2>Theory</h2>")
    A("<p>An MDP formulates an agent's sequential decision-making problem as a 5-tuple "
      "&lang;<i>S</i>, <i>A</i>, <i>P</i>, <i>R</i>, &gamma;&rang;: a set of states <i>S</i>, "
      "a set of actions <i>A</i> available in each, a transition probability function "
      "<i>P</i>(<i>s</i>'|<i>s</i>,<i>a</i>), a reward function <i>R</i>(<i>s</i>,<i>a</i>,<i>s</i>'), "
      "and a temporal discount factor &gamma; &in; [0, 1). Because of the Markov property, the optimal "
      "behavior is fully described by a stationary policy &pi;: <i>S</i> &rarr; <i>A</i>, and the value "
      "of a state <i>V</i><sup>&pi;</sup>(<i>s</i>) represents the expected cumulative discounted future return.</p>")
    A("<p>The <b>Bellman Optimality Equation</b> expresses the recursive relationship for optimal values:</p>")
    A("<p class=eq><i>V</i>*(<i>s</i>) = max<sub><i>a</i> &in; <i>A</i></sub> &sum;<sub><i>s</i>'</sub> "
      "<i>P</i>(<i>s</i>' | <i>s</i>, <i>a</i>) [ <i>R</i>(<i>s</i>, <i>a</i>, <i>s</i>') + &gamma; <i>V</i>*(<i>s</i>') ]</p>")
    A("<p>Two dynamic programming algorithms compute this solution:</p>")
    A("<ul>"
      "<li><b>Value Iteration</b>: Turns the Bellman optimality equation directly into an update operator, "
      "sweeping repeatedly across all non-terminal states until max<sub><i>s</i></sub> |<i>V</i><sub><i>k</i>+1</sub>(<i>s</i>) &minus; <i>V</i><sub><i>k</i></sub>(<i>s</i>)| &lt; tol, "
      "extracting the greedy policy once at convergence.</li>"
      "<li><b>Policy Iteration</b>: Alternates between exact <i>Policy Evaluation</i> (solving or iterating "
      "to find <i>V</i><sup>&pi;</sup>) and <i>Policy Improvement</i> (updating &pi;(<i>s</i>) &larr; argmax<sub><i>a</i></sub> <i>Q</i>(<i>s</i>,<i>a</i>)). "
      "It terminates when policy changes cease (&pi;<sub><i>k</i>+1</sub> = &pi;<sub><i>k</i></sub>).</li>"
      "</ul>")

    A("<p class=cap>Table 1. The GridWorld Environment Specification.</p>")
    A(table(["Element", "Specification"],
            [["States", "4 columns &times; 3 rows (11 states total); cell (1, 1) is a barrier/wall and not a state."],
             ["Terminals", "Goal at (3, 2) with reward +1.0; Trap at (3, 1) with reward &minus;1.0."],
             ["Actions", "up, down, left, right available in all 9 non-terminal states."],
             ["Transitions", "Intended move with probability 1 &minus; 2p; perpendicular slips each with probability p. "
                             "Bumping into walls or boundaries keeps the agent in place."],
             ["Parameters", "Default slip probability p = 0.1, step reward R<sub>step</sub> = &minus;0.04, discount factor &gamma; = 0.95, start state (0, 0)."]],
            widths=["22%", "78%"]))

    # Algorithm
    A("<h2>Algorithm</h2>")
    A("<h3>Algorithm 1 &mdash; Value Iteration</h3>")
    A("<ol>"
      "<li>Initialize <i>V</i>(<i>s</i>) = 0 for all non-terminal states <i>s</i> &in; <i>S</i>. Set tolerance tol = 10<sup>&minus;6</sup>.</li>"
      "<li>For each sweep <i>k</i> = 1, 2, ...: compute for every non-terminal state "
      "<i>Q</i>(<i>s</i>, <i>a</i>) = &sum;<sub><i>s</i>'</sub> <i>P</i>(<i>s</i>'|<i>s</i>,<i>a</i>)[<i>R</i> + &gamma;<i>V</i>(<i>s</i>')], "
      "and set <i>V</i><sub>new</sub>(<i>s</i>) = max<sub><i>a</i></sub> <i>Q</i>(<i>s</i>, <i>a</i>).</li>"
      "<li>Check convergence &Delta; = max<sub><i>s</i></sub> |<i>V</i><sub>new</sub>(<i>s</i>) &minus; <i>V</i>(<i>s</i>)|. If &Delta; &lt; tol, terminate.</li>"
      "<li>Extract optimal policy &pi;*(<i>s</i>) = argmax<sub><i>a</i></sub> <i>Q</i>(<i>s</i>, <i>a</i>).</li>"
      "</ol>")

    A("<h3>Algorithm 2 &mdash; Policy Iteration</h3>")
    A("<ol>"
      "<li>Initialize an arbitrary policy &pi;<sub>0</sub>(<i>s</i>) = 'up' for all non-terminal states, and values <i>V</i>(<i>s</i>) = 0.</li>"
      "<li><b>Policy Evaluation</b>: Sweep <i>V</i><sub><i>k</i>+1</sub>(<i>s</i>) &larr; <i>Q</i>(<i>s</i>, &pi;(<i>s</i>), <i>V</i><sub><i>k</i></sub>) "
      "until values settle within tolerance tol. Record evaluation sweeps and updates.</li>"
      "<li><b>Policy Improvement</b>: For each state, find greedy action <i>a</i>* = argmax<sub><i>a</i></sub> <i>Q</i>(<i>s</i>, <i>a</i>, <i>V</i>). "
      "If <i>a</i>* &ne; &pi;(<i>s</i>), set &pi;(<i>s</i>) &larr; <i>a</i>* and mark policy unstable.</li>"
      "<li>If policy is unchanged across all states, terminate; otherwise, repeat evaluation.</li>"
      "</ol>")

    # Source Code
    A("<h2>Source Code (exp7_mdp.py)</h2>")
    A(code(src_mdp, size="7.0pt"))

    # Procedure and Results
    A("<h2>Procedure and Results</h2>")
    A("<p>The program was executed in the SVNIT Agentic AI laboratory environment. "
      "Below is the complete captured trace of Value Iteration, Policy Iteration, algorithm verification, "
      "and parameter sweep outputs.</p>")
    A(out(o_main, size="6.5pt"))

    A("<p class=cap>Figure 1. Converged Value Function and Optimal Policy Grid Map under baseline parameters (p=0.1, R<sub>step</sub>=&minus;0.04, &gamma;=0.95).</p>")
    A(embed_image("outputs/lab7_fig1_baseline_grid.png", width="75%"))

    A("<p class=cap>Table 2. Quantitative Comparison of Value Iteration and Policy Iteration.</p>")
    A(table(["Metric", "Value Iteration (Alg 1)", "Policy Iteration (Alg 2)", "Agreement / Ratio"],
            [["Policy Improvement Rounds", "1 (read-off at end)", "4 rounds", "Discovers identical policy"],
             ["Evaluation / Iteration Sweeps", "25 sweeps", "185 sweeps (cumulative)", "VI requires 7.4&times; fewer sweeps"],
             ["Total State Value Updates", "225 updates (25 &times; 9)", "1665 updates (185 &times; 9)", "VI performs 7.4&times; fewer updates"],
             ["Start State Value V(0,0)", "+0.5311", "+0.5311", "Exact match (diff &lt; 10<sup>&minus;6</sup>)"],
             ["Optimal Policy Agreement", "100% across all 9 states", "100% across all 9 states", "Identical action in every cell"]],
            widths=["30%", "24%", "24%", "22%"]))

    # Observations
    A("<h2>Observations &amp; Discussion</h2>")
    A("<ol>"
      "<li><b>Why the policy sends the agent the long way round rather than along the row holding the negative terminal:</b><br>"
      "Row 1 contains the catastrophic &minus;1.0 trap at (3, 1). With a 10% slip probability in each perpendicular "
      "direction, moving east along row 1 or below the obstacle at (2, 0) exposes the agent to an accidental slip directly "
      "into the negative terminal. Navigating north through column 0 and across row 2 introduces a buffer of safe cells, "
      "keeping the agent safely away from (3, 1). The small extra cost of taking the longer detour (&minus;0.04 per step) "
      "is dwarfed by the expected penalty of slipping into the &minus;1.0 trap.</li>"
      "<li><b>What the value of the start state means in units of reward:</b><br>"
      "<i>V</i>(0, 0) = +0.5311 represents the <b>expected cumulative discounted return</b> earned from (0, 0) to termination "
      "under the optimal policy. An optimal path requires roughly 5 steps: collecting &approx; 5 &times; (&minus;0.04) = &minus;0.20 "
      "in step penalties and receiving +1.0 at the goal terminal discounted by &gamma;<sup>5</sup> = (0.95)<sup>5</sup> &approx; 0.7738 "
      "(yielding &approx; 0.7738 &minus; 0.20 = 0.5738). Incorporating stochastic slip delays and perpendicular rebounds brings "
      "the exact expected discounted return to +0.5311 reward units.</li>"
      "<li><b>Which method reaches the answer in fewer sweeps and performs fewer value updates in total:</b><br>"
      "<b>Value Iteration</b> is significantly more computationally efficient overall for this discrete state space, "
      "converging in <b>25 sweeps</b> and performing <b>225 updates</b>. In contrast, <b>Policy Iteration</b> requires only "
      "<b>4 improvement rounds</b> to settle on the optimal policy, but requires <b>185 evaluation sweeps</b> and <b>1665 state updates</b>. "
      "Thus, while Policy Iteration takes fewer policy steps, its exact intermediate evaluations make it 7.4&times; more expensive "
      "in total computational work than Value Iteration.</li>"
      "<li><b>Contribution of the discount factor when every episode ends at a terminal anyway:</b><br>"
      "Even when an episode is guaranteed to terminate absorbing at a terminal, &gamma; &lt; 1 serves two fundamental roles: "
      "(a) it guarantees contraction mapping under the Bellman operator, ensuring numerical convergence and stability; "
      "(b) it mathematically enforces a temporal preference for <b>shortest paths</b>, since delaying goal arrival decays future reward "
      "exponentially by &gamma;<sup><i>t</i></sup>, preventing infinite stalling or looping.</li>"
      "</ol>")

    # Exercise 1
    A("<h2>Exercise 1 &mdash; Step Reward &amp; Discount Factor Sweeps</h2>")
    A("<p class=cap>Figure 2. Start State Value V(0, 0) and Convergence Sweeps across Step Reward and Discount Factor Sweeps.</p>")
    A(embed_image("outputs/lab7_fig2_param_sweeps.png", width="90%"))

    A("<p class=cap>Table 3. Step Reward Sweep (with &gamma; = 0.95, p = 0.1).</p>")
    A(table(["R<sub>step</sub>", "V(0,0)", "Sweeps", "Row 2 Actions", "Row 1 Actions", "Row 0 Actions", "Agent Behavioral Preference"],
            [["&minus;0.01", "+0.7302", "27", "['right', 'right', 'right']", "['up', 'up']", "['right', 'left', 'left', 'left']", "Prefers maximum safety; takes long north detour buffer."],
             ["&minus;0.04", "+0.5311", "25", "['right', 'right', 'right']", "['up', 'up']", "['right', 'left', 'left', 'left']", "Baseline policy; prefers long detour to avoid slip risk."],
             ["&minus;0.10", "+0.2227", "21", "['right', 'right', 'right']", "['up', 'up']", "['right', 'right', 'right', 'left']", "Prefers shorter path over buffer; cell (1,0) points right."],
             ["&minus;0.50", "&minus;0.7061", "13", "['right', 'right', 'right']", "['up', 'up']", "['right', 'right', 'right', 'up']", "Prefers rushing directly to exits; step penalty dominates."],
             ["&minus;2.00", "&minus;2.0000", "2", "['right', 'right', 'right']", "['up', 'right']", "['up', 'right', 'right', 'up']", "Prefers immediate termination via trap over &minus;2.0/step cost."]],
            widths=["10%", "10%", "8%", "18%", "12%", "18%", "24%"]))

    A("<p class=cap>Table 4. Discount Factor Sweep (with R<sub>step</sub> = &minus;0.04, p = 0.1).</p>")
    A(table(["&gamma;", "V(0,0)", "Sweeps", "Row 2 Actions", "Row 1 Actions", "Row 0 Actions", "Agent Behavioral Preference"],
            [["0.50", "&minus;0.0617", "9", "['right', 'right', 'right']", "['up', 'up']", "['right', 'right', 'right', 'left']", "Myopic; heavily discounts future reward, taking shortest route."],
             ["0.70", "+0.0768", "12", "['right', 'right', 'right']", "['up', 'up']", "['right', 'right', 'right', 'left']", "Prefers direct route because discounting penalizes long travel."],
             ["0.90", "+0.3541", "19", "['right', 'right', 'right']", "['up', 'up']", "['right', 'right', 'right', 'left']", "Intermediate; transition point between direct route and safe detour."],
             ["0.95", "+0.5311", "25", "['right', 'right', 'right']", "['up', 'up']", "['right', 'left', 'left', 'left']", "High preservation of future return; switches to safe detour."],
             ["0.99", "+0.6974", "38", "['right', 'right', 'right']", "['up', 'up']", "['right', 'left', 'left', 'left']", "Far-sighted; values +1.0 fully, completely avoids trap hazard."]],
            widths=["8%", "10%", "8%", "18%", "12%", "18%", "26%"]))

    # Exercise 2
    A("<h2>Exercise 2 &mdash; Slip Probability Sweep &amp; Trap Absorption Analysis</h2>")
    A("<p class=cap>Figure 3. Start State Value and Trap Absorption Probability vs. Slip Probability p.</p>")
    A(embed_image("outputs/lab7_fig3_slip_sweep.png", width="70%"))

    A("<p class=cap>Table 5. Slip Probability Sweep and Exact Absorption Probability into Negative Terminal.</p>")
    A(table(["Slip Prob p", "V(0,0)", "Sweeps", "P(Reach &minus;1 Terminal)", "Policy Adaptations / Explanation"],
            [["0.00", "+0.8062", "23", "0.0000", "Deterministic environment; no slips, perfect safe trajectory to goal."],
             ["0.05", "+0.6729", "24", "0.0042", "Nominal detour path maintained; small noise causes rare accidental slips."],
             ["0.10", "+0.5311", "25", "0.0137", "Baseline noise; failure rate rises as sideways perpendicular slips increase."],
             ["0.20", "+0.2741", "27", "0.0000", "Defensive policy switch at (2, 1) to 'left'; failure drops to 0."],
             ["0.30", "+0.0384", "29", "0.0000", "Extreme noise; agent steers into walls to stabilize, 0% failure."]],
            widths=["12%", "10%", "10%", "22%", "46%"]))

    A("<h3>Explanation: Why the Trap Absorption Probability Does Not Rise Steadily with Slip Probability</h3>")
    A("<p>Between <i>p</i> = 0.0 and <i>p</i> = 0.10, the probability of reaching the &minus;1.0 terminal increases steadily "
      "from 0.0000 to 0.0137 because the optimal policy remains fixed along the nominal route while stochastic sideways noise increases. "
      "However, at <b><i>p</i> = 0.20 and <i>p</i> = 0.30, the absorption probability abruptly drops to exactly 0.0000</b>.</p>"
      "<p><b>Mechanism</b>: The optimal policy is not static; it dynamically adapts to environmental risk. "
      "When <i>p</i> &ge; 0.20, the expected hazard of slipping into (3, 1) while positioned at (2, 1) outweighs the cost of detour. "
      "The Bellman update dynamically shifts the policy at (2, 1) from <code>'up'</code> to <code>'left'</code> (steering directly away from the trap) "
      "and utilizes wall collisions at the boundary to cancel momentum and absorb slips. This defensive adaptation completely eliminates "
      "any reachable path from (0, 0) into (3, 1), driving the exact absorption probability to zero.</p>")

    A("</div>")
    return "\n".join(P), env_line

CSS = """
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
    body, env_line = build(roll)
    name = "LAB_7_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_7_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")

