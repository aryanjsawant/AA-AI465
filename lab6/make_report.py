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


def block(text, heading, next_heading=None):
    """Return the part of the captured output under one === heading ===."""
    lines = text.splitlines()
    i = next(n for n, l in enumerate(lines) if heading in l)
    if next_heading is None:
        j = len(lines)
    else:
        j = next((n for n in range(i + 1, len(lines))
                  if next_heading in lines[n]), len(lines))
    return "\n".join(lines[i:j]).rstrip()


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
    o_main = run_program("exp6_role_agents.py")
    o_ex = run_program("exp6_exercises.py")

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
            [[STUDENT_NAME or "&nbsp;", roll, "6", stamp.split(",")[0]]]))
    A("<h1>Experiment 6</h1>")
    A("<h1 class=sub>Role-Based LLM Agent Design with Structured Message "
      "Passing</h1>")

    # ------------------------------------------------------------------
    A("<h2>Aim</h2>")
    A("<p>To specify LLM agents as explicit roles, each with a goal, "
      "permitted tools, permitted recipients and a required output schema; "
      "to coordinate them through a manager using structured messages, "
      "with a reviewer that sends faulty work back to the responsible "
      "role; and to compare the team against a single generalist agent by "
      "task success, model calls and role violations.</p>")

    # ------------------------------------------------------------------
    A("<h2>Theory</h2>")
    A("<p>A single agent handed every tool and one long prompt that mixes "
      "retrieval, writing and checking must decide afresh at each step "
      "which of those jobs it is currently doing, and nothing in its "
      "construction prevents it from skipping one of them altogether. "
      "Role-based design splits that work into roles, each defined by four "
      "things: a goal, the tools it may call, the roles it may message, "
      "and the fields its output must contain. A Manager decomposes the "
      "task and delegates it; workers return structured messages; a "
      "Reviewer checks the draft against the sources and either approves "
      "it or sends it back to the role responsible for the fault.</p>")
    A("<p>The central claim of this experiment is that a specification is "
      "only as strong as its enforcement. A permission written into a "
      "system prompt is a <i>request</i>, which the model may follow or "
      "ignore; the same permission checked by the orchestrator before the "
      "tool call runs or the message is delivered is a <i>rule</i>. Here "
      "<span class=m>validate()</span> is that check, sitting between "
      "every role and every action it attempts, and each rejection is "
      "logged as a role violation. Exercise 2 measures the difference "
      "directly by running the same five injected instructions twice, once "
      "with the permissions stated only in the prompts and once with "
      "<span class=m>validate()</span> enforcing them.</p>")
    A("<p>As in Experiments 3 and 5, the model side is scripted: each role "
      "is a function that does its job but commits named faults at stated "
      "rates, drawn from a seeded generator so that a run reproduces "
      "exactly, and a real LLM would change only those functions. The "
      "team's price is extra model calls, measured here alongside task "
      "success. Two faults in particular drive the comparison: the "
      "document store contains near-duplicate titles, so a careless "
      "Researcher cites a superseded note and reports a stale accuracy, "
      "and the Writer sometimes drops one of the two required citations. "
      "Neither is visible from the finished draft alone &mdash; catching "
      "them is precisely what the Reviewer is for.</p>")

    A("<p class=cap>Table 1. The four roles implemented in this "
      "experiment.</p>")
    A(table(["Role", "Responsibility", "Permitted tools", "May send to",
             "Required output fields"],
            [["Manager",
              "decomposes the task, delegates, routes revisions, delivers "
              "the final answer", "none",
              "Researcher, Writer, Reviewer, User", "subtasks"],
             ["Researcher",
              "finds both entities, reads their values, computes the "
              "result", "search(), read_doc(), calculator()", "Manager",
              "values, sources, result"],
             ["Writer",
              "turns the finding into a cited answer of at most 60 words",
              "none", "Manager", "draft, citations"],
             ["Reviewer",
              "re-reads the cited sources and checks values, winner and "
              "citations", "read_doc()", "Manager", "verdict, reasons"]],
            widths=["12%", "30%", "20%", "19%", "19%"]))

    # ------------------------------------------------------------------
    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Build a document store of at least eight short notes (model "
      "name, benchmark, accuracy, parameter count), two of whose titles "
      "nearly duplicate others; the tools "
      "<span class=m>search()</span>, <span class=m>read_doc()</span> and "
      "<span class=m>calculator()</span>; and eight comparison tasks, each "
      "scored on a four-point checklist: correct number, correct winner, "
      "both correct sources cited, at most 60 words. Write a role "
      "specification for each role in Table 1 and implement "
      "<span class=m>validate()</span>, which rejects any tool call "
      "outside the role's permitted tools, any message to a role it may "
      "not send to, and any output missing a required field, logging each "
      "rejection as a role violation.</li>"
      "<li>Implement the orchestrator: the Manager assigns the task to the "
      "Researcher, passes the finding to the Writer and the draft to the "
      "Reviewer; on a <span class=m>revise</span> verdict it routes the "
      "task back to the role named in the reasons, for at most two "
      "revision rounds, then delivers the final draft to the user. Run the "
      "same tasks with a single generalist agent holding all three tools "
      "and one merged prompt. For both systems record task success, model "
      "calls per role, role violations and revisions, and print the full "
      "message trace for every task.</li>"
      "</ol>")

    A("<h3>How the specification is enforced</h3>")
    A("<p>Each role is held as a record carrying exactly the four things "
      "Table 1 names, so the permitted tools, permitted recipients and "
      "required fields are <i>data</i> the orchestrator reads at run time, "
      "not merely prose the model reads in its prompt. "
      "<span class=m>validate()</span> sits between every role and every "
      "action it attempts and applies three checks: a tool call is "
      "refused unless the tool appears in that role's permitted tools, a "
      "message is refused unless its recipient appears in the role's "
      "permitted recipients, and an output is refused if any required "
      "field is absent. Each refusal is recorded against the role that "
      "attempted it. An <span class=m>enforce</span> flag allows the same "
      "check to observe without blocking, which is what Exercise 2 uses to "
      "model a permission that exists only in a prompt.</p>")
    A("<p>The revision loop is the other half of the design. When the "
      "Reviewer returns <span class=m>revise</span>, its reasons name the "
      "role responsible, and the Manager routes the task back to that role "
      "specifically rather than retrying the whole pipeline &mdash; a "
      "sourcing fault returns to the Researcher, a citation or length "
      "fault to the Writer &mdash; for at most two rounds before the "
      "draft is delivered regardless. The Step 3 trace below shows both "
      "mechanisms operating on one task.</p>")

    # ------------------------------------------------------------------
    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<p>The two programs are run in full; their complete console output "
      "is reproduced below. <span class=m>exp6_role_agents.py</span> "
      "prints the four role specifications, the message format, the "
      "document store, one complete message trace containing a revision, "
      "and the comparison of the team against the generalist over ten "
      "seeds. <span class=m>exp6_exercises.py</span> prints the two "
      "exercises.</p>")

    A("<h3>Step 1 &mdash; the four role specifications and the message "
      "format</h3>")
    A("<p class=cap>Snapshot: the role specifications as the program "
      "prints them, each with its goal, permitted tools, permitted "
      "recipients, required output fields and system prompt.</p>")
    A(out(block(o_main, "=== Role specifications ===",
                "=== Document store")))

    A(PAGEBREAK)
    A("<h3>Step 2 &mdash; the document store</h3>")
    A("<p class=cap>Snapshot: the ten notes. The two superseded twins are "
      "marked; their titles nearly duplicate the current notes, which is "
      "what makes the Researcher's sourcing fault possible.</p>")
    A(out(block(o_main, "=== Document store",
                "=== One complete message trace")))

    A("<h3>Step 3 &mdash; one complete message trace containing a "
      "revision</h3>")
    A("<p class=cap>Snapshot: every structured message exchanged for one "
      "task, from the Manager's first assignment to delivery. The Reviewer "
      "returns <span class=m>revise</span> twice, naming the Researcher "
      "each time, and the Manager routes the task back to it before the "
      "corrected draft is delivered.</p>")
    A(out(block(o_main, "=== One complete message trace",
                "=== Comparison over")))

    A(PAGEBREAK)
    A("<h3>Step 4 &mdash; the team against the single generalist</h3>")
    A("<p class=cap>Snapshot: task success, model calls broken down by "
      "role, role violations and revisions for both systems over ten seeds "
      "and eight tasks (%s).</p>" % html.escape(env_line))
    A(out(block(o_main, "=== Comparison over")))

    A(PAGEBREAK)
    A("<p class=cap>Figure 1. Task success and model calls for the two "
      "systems. Success and cost are plotted on separate panels rather "
      "than against two y-axes on one. Generated by make_plots.py from "
      "this run's own results.</p>")
    A("<img src='outputs/exp6_fig1_team_vs_generalist.png' "
      "style='width:85%;'>")
    A(PAGEBREAK)
    A("<p class=cap>Figure 2. Per-task success over the ten seeds. The "
      "team's margin is largest on t1, the task whose two models both have "
      "a superseded twin note in the store.</p>")
    A("<img src='outputs/exp6_fig2_per_task.png' style='width:85%;'>")

    A(PAGEBREAK)
    A("<p class=cap>Figure 3. The role violations caught by "
      "validate(), split by the role that attempted the action and by the "
      "kind of rule it broke. The generalist records none, for the reason "
      "discussed in Observation 3.</p>")
    A("<img src='outputs/exp6_fig3_violations.png' style='width:85%;'>")

    # ------------------------------------------------------------------
    A(PAGEBREAK)
    A("<h2>Observations</h2>")

    A("<h3>1. Which tasks the team completes that the generalist fails, "
      "and which role caught the fault</h3>")
    A("<p>The team scores 0.875 (70/80) against the generalist's 0.450 "
      "(36/80), and Figure 2 shows the margin is not spread evenly across "
      "the task set. It is widest on <b>t1</b> (team 9/10, generalist "
      "1/10), which compares Orion-7B with Vega-13B &mdash; the one task "
      "whose <i>both</i> models carry a near-duplicate twin note in the "
      "store (d02 superseding d01, d04 superseding d03). The generalist "
      "has two independent chances per run to read a stale note, and "
      "nothing downstream to catch it; it therefore fails t1 almost "
      "every time. t8 (team 8/10, generalist 3/10) is the next widest and "
      "involves the two smallest models, where the 0.1 gap slip is "
      "proportionally most likely to be the only error.</p>")
    A("<p>In every one of those rescued cases the fault was caught by the "
      "<b>Reviewer</b>, and the mechanism is visible in the Step 3 trace: "
      "the Reviewer re-reads each cited document with "
      "<span class=m>read_doc()</span>, finds that a cited note is marked "
      "superseded, and returns <span class=m>revise</span> naming the "
      "Researcher. It is worth being precise about why this works. The "
      "Reviewer does not re-derive the answer; it re-reads the "
      "<i>sources the draft itself cites</i> and compares them against "
      "what the draft claims. That is a cheaper check than redoing the "
      "research, and it is enough, because the fault always leaves a trace "
      "in the citation.</p>")

    A("<h3>2. Model calls spent per additional correct answer</h3>")
    A("<p>The team spends 394 model calls against the generalist's 80, so "
      "314 extra calls buy 34 extra correct answers: <b>9.24 calls per "
      "additional correct answer</b>. That figure deserves to be read "
      "carefully rather than quoted alone. The generalist costs exactly "
      "one call per task because it does everything in one pass; the team "
      "costs at least four (Manager, Researcher, Writer, Reviewer) before "
      "any revision, and the 32 revisions add further Researcher, Writer "
      "and Reviewer calls on top. The ratio is therefore not a measure of "
      "how expensive review is in general &mdash; it is the price of "
      "review <i>at this fault rate</i>. If the Researcher's sourcing "
      "fault were rarer, the same Reviewer calls would be spent to catch "
      "fewer faults and the cost per correction would rise; if it were "
      "more common, the Reviewer would pay for itself faster.</p>")

    A("<h3>3. Why the generalist records no role violations, and whether "
      "that makes it safer</h3>")
    A("<p>The generalist records <b>zero</b> role violations, and this is "
      "the most easily misread number in the whole experiment. It records "
      "none because it <i>cannot</i> commit one: it holds all three tools, "
      "so no tool call is outside its permissions; it may message the "
      "User, which is the only message it ever sends; and its single "
      "output carries the two fields its schema requires. The violation "
      "count is zero because the specification is empty of anything to "
      "violate, not because the agent is well behaved.</p>")
    A("<p>So no, it is not safer &mdash; it is <i>less observable</i>, "
      "which is close to the opposite. The team's 27 violations are 27 "
      "actions that were attempted, refused and recorded with the role "
      "that attempted them. The generalist performs the equivalent "
      "actions silently and they are indistinguishable from its intended "
      "behaviour. A zero on this metric should be read as a statement "
      "about the breadth of the permissions, not about the conduct of the "
      "agent, and the correct comparison between the two systems is their "
      "task success, where the generalist loses by a wide margin.</p>")

    A("<h3>4. Which role produces the most violations, and whether the fix "
      "belongs in its prompt or its permissions</h3>")
    A("<p>The <b>Writer</b> produces the most: 17 of the 27, and all 17 "
      "are tool violations &mdash; it repeatedly reaches for "
      "<span class=m>search()</span> although it holds no tools at all. "
      "The Researcher accounts for 7 and the Reviewer for 3, both "
      "recipient violations (the Researcher trying to answer the User "
      "directly, the Reviewer trying to send a patched draft straight to "
      "the Writer).</p>")
    A("<p>The fix belongs in the <b>permissions</b>, and the experiment "
      "shows why rather than merely asserting it. The Writer's prompt "
      "already says, in plain words, <i>You hold no tools; write only from "
      "the finding you are handed</i>. It reaches for "
      "<span class=m>search()</span> anyway, 17 times. Strengthening that "
      "sentence is an attempt to fix by persuasion something that is "
      "already being refused by enforcement &mdash; and Exercise 2 "
      "quantifies exactly what persuasion is worth here: with the "
      "permissions stated only in the prompt, 0 of 5 injected "
      "instructions were blocked and all 5 took effect. The prompt is the "
      "right place to explain <i>why</i> a role should not do something; "
      "the permission list is the only place that can <i>stop</i> it.</p>")

    A("<h3>5. What happens to a fault the Reviewer misses</h3>")
    A("<p>It is delivered to the user as a finished, confidently worded, "
      "correctly formatted answer. The run records <b>10 such cases</b> "
      "out of 80 (the Reviewer approves a draft that is in fact faulty at "
      "a 0.15 rate whenever there is a fault to find), and those ten are "
      "exactly the gap between the team's 70/80 and a perfect score. "
      "Nothing downstream of the Reviewer looks at the draft again, so a "
      "missed fault is not merely uncorrected &mdash; it is "
      "<i>laundered</i>. It now carries the Reviewer's implicit approval "
      "and two citations, and is materially harder for a human reader to "
      "doubt than the same error delivered by the generalist with no "
      "review at all. The practical lesson is that adding a checking role "
      "raises the floor but also raises the <i>credibility</i> of whatever "
      "slips past it, so the checker's own miss rate is a first-class "
      "property of the system rather than an implementation detail.</p>")

    # ------------------------------------------------------------------
    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Ablating the team</h2>")
    A("<p><b>Task.</b> Ablate the team in two ways &mdash; remove the "
      "Reviewer, and merge the Researcher and Writer into a single role "
      "holding the Researcher's tools. Report task success, model calls "
      "and role violations for the full team, both variants and the "
      "generalist over the same seeds, and state which role contributes "
      "the most correct answers per model call it consumes.</p>")
    A("<p><b>Approach.</b> Contribution is measured by ablation: the drop "
      "in correct answers when a role is removed, divided by the calls "
      "that role consumed while present. The merged variant is a genuine "
      "merge rather than a renaming &mdash; one agent holds the "
      "Researcher's tools and writes up its own finding in the same call, "
      "so the write-up costs no extra call and reaching for "
      "<span class=m>search()</span> is no longer a violation, but nobody "
      "else reads the finding before it is written up.</p>")

    A("<h3>Output</h3>")
    A(out(block(o_ex, "=== Exercise 1", "=== Exercise 2")))

    A(PAGEBREAK)
    A("<p class=cap>Figure 4. The four configurations by task success and "
      "by model calls.</p>")
    A("<img src='outputs/exp6_fig4_ablation.png' style='width:85%;'>")

    A("<h3>Discussion</h3>")
    A("<p>The two ablations are not remotely symmetric, and the asymmetry "
      "is the result. <b>Removing the Reviewer</b> collapses task success "
      "from 0.875 to 0.500 &mdash; 30 correct answers lost &mdash; while "
      "saving 154 calls. <b>Merging the Researcher and the Writer</b> "
      "costs 1 correct answer out of 80 while saving 109 calls. On the "
      "contribution measure the Reviewer returns 0.2727 correct answers "
      "per call it consumes; the Researcher/Writer separation returns "
      "0.0092, roughly thirty times less. The <b>Reviewer</b> is "
      "decisively the role that contributes the most correct answers per "
      "call.</p>")
    A("<p>The reason is worth stating because it generalises beyond this "
      "experiment. The Reviewer is the only role that performs an "
      "<i>independent check against the sources</i>; every other role "
      "either produces work or moves it along. Separating the Researcher "
      "from the Writer buys division of labour, which is an organisational "
      "virtue rather than an accuracy one: the Writer faithfully writes up "
      "whatever finding it is handed, so a Researcher error passes through "
      "it unaltered. Splitting a producer in two does not catch producer "
      "errors &mdash; only a checker does. Note also that the merged "
      "variant records 10 violations against the full team's 27, almost "
      "all of the difference being the Writer's 17 blocked "
      "<span class=m>search()</span> attempts, which are no longer "
      "violations once the merged role legitimately holds that tool.</p>")

    # ------------------------------------------------------------------
    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; Injected instructions</h2>")
    A("<p><b>Task.</b> Write five injected instructions that push a role "
      "outside its specification, run each with the permissions stated "
      "only in the prompts and again with "
      "<span class=m>validate()</span> enforcing them, and report for each "
      "case how many attempts were blocked, how many took effect, and "
      "which case <span class=m>validate()</span> cannot stop.</p>")
    A("<p><b>Approach.</b> The five injections are the ones the manual "
      "names: the Writer told to search, a document telling the Researcher "
      "to send its finding straight to the user, the Reviewer told to fix "
      "the draft itself, a document telling the Researcher to report a "
      "false value, and an assignment telling the Researcher to omit its "
      "sources. Running with <span class=m>enforce=False</span> models a "
      "permission that exists only in a prompt: the attempt is recorded "
      "but allowed through.</p>")

    A("<h3>Output</h3>")
    A(out(block(o_ex, "=== Exercise 2")))

    A(PAGEBREAK)
    A("<p class=cap>Figure 5. Each injected instruction under the two "
      "regimes. The left column is uniformly orange &mdash; a permission "
      "written only in a prompt stopped nothing at all.</p>")
    A("<img src='outputs/exp6_fig5_injection.png' style='width:85%;'>")

    A("<h3>Discussion</h3>")
    A("<p>With the permissions stated only in the prompts, <b>0 of 5</b> "
      "attempts were blocked and all five took effect. With "
      "<span class=m>validate()</span> enforcing the same permissions, "
      "<b>4 of 5</b> were blocked. The three structural cases (c1 the "
      "Writer's tool call, c2 and c3 the forbidden recipients) and the "
      "schema case (c5, the omitted "
      "<span class=m>sources</span> field) are all refused, because each "
      "breaks something <span class=m>validate()</span> can see in the "
      "shape of the action.</p>")
    A("<p>The case it <b>cannot</b> stop is <b>c4</b>, the document that "
      "tells the Researcher to report a false value. The reason is "
      "structural rather than a gap in the implementation: a permitted "
      "role calls a permitted tool, fills every required field and sends "
      "the result to a permitted recipient. Every rule "
      "<span class=m>validate()</span> knows how to check is satisfied. "
      "Only the <i>value inside</i> the well-formed field is false, and a "
      "permission check has no opinion about values &mdash; it governs "
      "the shape of actions, not their truth. Catching c4 requires a role "
      "that re-reads the source and compares it against the claim, which "
      "is exactly the Reviewer's job. The two mechanisms are therefore "
      "complementary rather than redundant: enforcement constrains what a "
      "role may <i>do</i>, and review constrains what it may successfully "
      "<i>assert</i>. A system with only one of the two has a blind spot "
      "the other would have covered.</p>")

    # ------------------------------------------------------------------
    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>Specifying four roles with explicit goals, tools, recipients and "
      "output schemas, and coordinating them through a Manager with "
      "structured messages, nearly doubled task success over a single "
      "generalist holding the same tools: 0.875 against 0.450 over eighty "
      "runs. The gain is not evenly distributed and is not mysterious "
      "&mdash; it is concentrated on the tasks whose documents have "
      "near-duplicate twins, and it is produced almost entirely by one "
      "role. The ablation makes that precise: removing the Reviewer costs "
      "30 correct answers, while merging the Researcher and the Writer "
      "costs 1. What a team buys is not division of labour but "
      "<i>independent checking</i>, and the two should not be confused "
      "when designing one.</p>")
    A("<p>The price is 9.24 extra model calls per additional correct "
      "answer at this fault rate, and the residual failures are "
      "instructive in their own right. Ten of the eighty runs delivered a "
      "faulty draft because the Reviewer missed the fault, and those "
      "drafts reach the user carrying citations and an implicit approval "
      "&mdash; a missed fault is laundered, not merely uncorrected. "
      "Finally, the enforcement result is the sharpest finding in the "
      "experiment: permissions written into prompts blocked none of five "
      "injected instructions, while the same permissions checked by "
      "<span class=m>validate()</span> blocked four. The fifth, a false "
      "value inside a perfectly well-formed message, marks the boundary "
      "of what any permission system can do, and is the reason a checking "
      "role and a permission check are both necessary.</p>")

    # ------------------------------------------------------------------
    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "docstore.py, roles.py, exp6_role_agents.py, "
              "exp6_exercises.py, make_plots.py, make_report.py"],
             ["Libraries used",
              "Python standard library only (<span class=m>random</span>, "
              "<span class=m>collections.Counter</span>, "
              "<span class=m>dataclasses</span>) for every program that "
              "produces a result; Matplotlib (permitted, Table 1) is used "
              "solely by <span class=m>make_plots.py</span> to draw the "
              "figures and influences no reported number &mdash; it "
              "imports the same functions the console programs call and "
              "plots their return values. Every role, message, dispatcher "
              "and permission check appears explicitly in the code; no "
              "agent framework or orchestration library was used, in "
              "accordance with clause 3.1 of the Rules and "
              "Regulations."],
             ["Reproducibility",
              "The document store, task set and role specifications are "
              "fixed, and every scripted fault is drawn from a "
              "<span class=m>random.Random</span> seeded deterministically "
              "from (seed, task id, role, attempt), so every run over the "
              "same ten seeds reproduces exactly."],
             ["Sources consulted",
              "Course manual for Experiment 6 (role-based agent design, "
              "structured message passing, orchestrator-side permission "
              "enforcement)."]],
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
    name = "LAB_6_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_6_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
