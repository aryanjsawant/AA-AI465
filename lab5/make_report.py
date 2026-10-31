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
    src_questions = read(os.path.join(HERE, "questions.py"))
    src_main = read(os.path.join(HERE, "exp5_cot_selfconsistency.py"))
    src_ex = read(os.path.join(HERE, "exp5_exercises.py"))

    o_main = run_program("exp5_cot_selfconsistency.py")
    o_ex = run_program("exp5_exercises.py")

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
            [[STUDENT_NAME or "&nbsp;", roll, "5", stamp.split(",")[0]]]))
    A("<h1>Experiment 5</h1>")
    A("<h1 class=sub>Chain-of-Thought Reasoning and Self-Consistency by "
      "Sampling</h1>")

    A("<h2>Aim</h2>")
    A("<p>To generate several sampled reasoning traces for the same "
      "question, extract the final answer from each, select an answer by "
      "majority vote, and compare the accuracy and cost of that scheme "
      "against a single greedy chain-of-thought trace and against "
      "answering with no reasoning at all.</p>")

    A("<h2>Theory</h2>")
    A("<p>A model that is asked only for an answer must commit to it in a "
      "single step, with nothing to condition on but the question itself. "
      "Chain-of-thought prompting changes what that step conditions on: "
      "the model is asked to write out intermediate reasoning first, so "
      "the tokens that eventually state the answer are conditioned on the "
      "working, not just on the question. The gain this brings is real "
      "but fragile in one specific way &mdash; at temperature zero the "
      "model always follows the single most likely path through that "
      "reasoning, and if an error enters early in that path, the model "
      "keeps conditioning on its own mistake for the rest of the trace "
      "and never revisits it.</p>")
    A("<p>Self-consistency addresses exactly that fragility by exploiting "
      "an asymmetry between correct and incorrect reasoning: there are "
      "usually several different correct ways to reach the right answer, "
      "but wrong turns tend to scatter across several different wrong "
      "answers rather than agreeing with each other. Sampling the same "
      "question k times at a non-zero temperature, extracting the stated "
      "final answer from every trace, and returning the most frequent one "
      "therefore tends to beat a single greedy trace &mdash; not because "
      "the mode is the most likely single trace (greedy already picks the "
      "most likely token at every step, not the most likely conclusion), "
      "but because correct traces reinforce each other in the vote while "
      "incorrect traces split their votes across different wrong answers. "
      "The price paid for this is k model calls per question instead of "
      "one.</p>")
    A("<p>Since there is no live model available here, the model side is "
      "scripted exactly as in Experiment 3: a fixed function stands in "
      "for the model and returns a trace for a given question, decoding "
      "mode and sample index, so that the whole voting mechanism is "
      "visible without an API key. Substituting a real instruction-tuned "
      "model only ever changes that one function. Two pattern-breaks are "
      "worth flagging up front because they show up directly in the "
      "output below. First, the vote is taken over <i>extracted</i> "
      "answers, not raw traces, so a trace that states its result in an "
      "unparseable or unexpected form contributes nothing to the tally "
      "&mdash; it must be counted as a separate failure mode rather than "
      "silently dropped or treated as a wrong answer. Second, two "
      "traces that state the same value in different textual forms (for "
      "instance <span class=m>2.67</span> and <span class=m>2.670</span>) "
      "must be normalised to one canonical form before voting, or they "
      "will incorrectly split what is really a single answer into two "
      "smaller ones.</p>")

    A("<p class=cap>Table 1. The three configurations compared in this "
      "experiment.</p>")
    A(table(["Configuration", "Prompt", "Decoding", "Calls / question", "Answer selected by"],
            [["Direct", "question only", "temperature 0", "1", "the single trace"],
             ["CoT greedy", "question + worked examples", "temperature 0", "1", "the single trace"],
             ["CoT self-consistency", "question + worked examples", "temperature 0.7", "k",
              "majority vote over k traces"]],
            widths=["18%", "24%", "16%", "14%", "28%"]))

    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Build a question set of at least eight arithmetic/logic word "
      "problems with gold answers, write the Direct and chain-of-thought "
      "prompt templates, and implement "
      "<span class=m>extract_answer()</span>, which finds the stated "
      "final answer in a trace, normalises it to a canonical form, and "
      "returns <span class=m>None</span> when no answer can be found.</li>"
      "<li>Implement <span class=m>run(configuration)</span>: take one "
      "trace per question for the two greedy configurations and k sampled "
      "traces per question for self-consistency; extract every answer, "
      "discard the ones that could not be parsed, return the most "
      "frequent remaining answer, and record per configuration the "
      "accuracy, the number of model calls, and the number of traces with "
      "no extractable answer. Print the vote tally for every question.</li>"
      "</ol>")
    A(code("def extract_answer(trace_text):\n"
           "    match = _FINAL_ANSWER_RE.search(trace_text)\n"
           "    if not match:\n"
           "        return None\n"
           "    numeric_part = re.match(r\"[-+]?\\d+(\\.\\d+)?\", match.group(1).strip())\n"
           "    if not numeric_part:\n"
           "        return None\n"
           "    return canonical_number(float(numeric_part.group(0)))\n\n"
           "def majority_vote(answers):\n"
           "    tally = Counter(answers)\n"
           "    if not tally:\n"
           "        return None, tally\n"
           "    best_count = max(tally.values())\n"
           "    tied = [a for a, c in tally.items() if c == best_count]\n"
           "    return min(tied, key=lambda a: float(a)), tally",
           size="8.5pt"))

    A(PAGEBREAK)
    A("<h3>Question set</h3>")
    A("<p>Ten word problems, checked into <span class=m>questions.py</span> "
      "as a static list of dicts with a unique id and a gold numeric "
      "answer. Most are single- or two-step arithmetic that a correct "
      "reasoning path reaches directly; three (q05, q07, q09) are built "
      "so that a plausible-looking shortcut &mdash; treating a markup and "
      "an equal discount as cancelling out, rounding a half day up to a "
      "full day, and an off-by-one in counting gaps between stations "
      "&mdash; is at least as natural as the correct multi-step solution, "
      "which is what lets a single greedy trace fail on them while "
      "sampling several traces and voting can still recover the right "
      "answer.</p>")
    A(code(src_questions))

    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<h3>Program &mdash; exp5_cot_selfconsistency.py</h3>")
    A(code(src_main))

    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A("<p class=cap>Snapshot of the console output "
      "(%s), including both prompt templates, one complete chain-of-"
      "thought trace, the per-question vote tallies for self-consistency, "
      "and the final 3-way comparison table.</p>" % html.escape(env_line))
    A(out(o_main))

    A(PAGEBREAK)
    A("<p class=cap>Figure 1. The three configurations by accuracy (left) "
      "and by model calls (right). Accuracy and cost are plotted on "
      "separate panels rather than against two y-axes on one. Generated by "
      "make_plots.py from this run's own results.</p>")
    A("<img src='outputs/exp5_fig1_comparison.png' style='width:100%;'>")
    A("<p class=cap>Figure 2. The vote tally for every question at k=7, "
      "split by whether each vote went to the gold answer, with greedy's "
      "outcome on the same question marked beneath the axis. Bars totalling "
      "fewer than 7 votes are questions where a sampled trace was "
      "unparsable and therefore discarded before the vote.</p>")
    A("<img src='outputs/exp5_fig2_tallies.png' style='width:100%;'>")

    A(PAGEBREAK)
    A("<h2>Observations</h2>")
    A("<h3>1. Which questions self-consistency corrects that greedy gets "
      "wrong, and what their vote tallies have in common</h3>")
    A("<p>CoT greedy scores 7/10 (accuracy 0.70), getting q05, q07 and "
      "q09 wrong because its single fixed path takes exactly the "
      "plausible-looking shortcut built into each of those three "
      "questions (treating the markup and discount as cancelling out, "
      "rounding the half day up, and an off-by-one on the station count). "
      "Self-consistency at k=7 scores 9/10 (accuracy 0.90), correcting "
      "q07 (tally 2600:4, 2800:1) and q09 (tally 8:6, 9:1) but not q05 "
      "(tally 80:4, 75:3). What the two corrected tallies have in common "
      "is a clear plurality for the correct answer &mdash; the wrong "
      "shortcut is still sampled, but only once out of seven traces in "
      "both cases, so the correct path's traces dominate the vote. q05 is "
      "the case that stays wrong, and its tally is exactly the one "
      "question here where the wrong shortcut (4 votes) actually "
      "outnumbers the correct path (3 votes) &mdash; self-consistency can "
      "only recover the right answer when correct traces are the "
      "plurality, not automatically on every question.</p>")

    A("<h3>2. What a narrow winning margin tells you about the answer "
      "that won</h3>")
    A("<p>q05's tally of 80:4 against 75:3 out of seven traces is the "
      "narrowest margin in the whole run, and it is also the one question "
      "where the vote winner is wrong. A narrow margin means the sampled "
      "traces were nearly evenly split between two (or more) distinct "
      "reasoning paths, which is precisely the situation where the "
      "plurality answer is least trustworthy &mdash; a small change in "
      "which traces happened to be sampled, or a slightly different seed, "
      "could easily have flipped the winner (Exercise 1's per-seed rows "
      "for k=1 and k=3 show exactly this kind of run-to-run swing). A wide "
      "margin, by contrast (for example q03 and q04's unanimous 6/6 "
      "votes, or q01 and q09's 6:1 splits), means almost every sampled "
      "reasoning path agreed, which is a much stronger indication that "
      "the winning answer reflects the question's actual structure rather "
      "than a close coin flip between two competing shortcuts.</p>")

    A("<h3>3. Model calls spent per additional correct answer</h3>")
    A("<p>Direct and CoT greedy each spend 10 calls (one per question) "
      "for 7 correct answers. Self-consistency at k=7 spends 70 calls for "
      "9 correct answers &mdash; 60 additional calls for 2 additional "
      "correct answers relative to greedy, i.e. 30 calls per additional "
      "correct answer at this k. Exercise 1's sweep makes the same "
      "trade-off explicit as k grows: mean accuracy rises from 0.660 at "
      "k=1 to 0.960 at k=9 while total calls (summed over 5 seeds) rise "
      "from 50 to 450, and accuracy stops improving appreciably beyond "
      "k=9 (k=15 also reaches 0.960 but at 750 calls) &mdash; so the calls "
      "spent per correct answer keep climbing well after the accuracy "
      "gain has flattened out, which is the direct cost of self-"
      "consistency's k-times-the-calls price.</p>")

    A("<h3>4. Why unparsable traces must be counted separately from "
      "wrongly-answered traces</h3>")
    A("<p>The self-consistency run above extracts a numeric answer from "
      "65 of the 70 sampled traces and finds no parseable "
      "&ldquo;Final Answer:&rdquo; line in the other 5 &mdash; those 5 "
      "are excluded from every vote tally entirely rather than being "
      "counted as votes for a wrong answer. Collapsing the two categories "
      "would corrupt the measurement in two directions at once: folding "
      "unparsable traces into &ldquo;wrong&rdquo; would understate the "
      "model's reasoning accuracy by blaming it for an output-formatting "
      "failure it may not have made, while silently dropping them without "
      "reporting the count would hide a real, separate failure mode "
      "&mdash; a model that reasons correctly but states its answer in an "
      "unexpected form is a formatting problem to fix in the prompt or "
      "the extractor, not a reasoning problem to fix by sampling more "
      "traces. Reporting them separately is also what makes the vote "
      "tallies interpretable: a tally that sums to less than k is "
      "immediately legible as k minus however many traces the extractor "
      "discarded.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Sweeping k over {1, 3, 5, 9, 15}</h2>")
    A("<p><b>Task.</b> Sweep k over 1, 3, 5, 9 and 15, repeating each "
      "setting with several different seeds, and report accuracy and "
      "total model calls for each k. State the k beyond which accuracy "
      "stops improving appreciably, and the calls spent per correct "
      "answer at that point.</p>")
    A("<p><b>Approach.</b> Each k in {1, 3, 5, 9, 15} is run against the "
      "full question set with five different seeds (11, 22, 33, 44, 55); "
      "mean accuracy is averaged over the five seeds and total calls is "
      "summed over them (k &times; 10 questions &times; 5 seeds).</p>")
    A("<h3>Program &mdash; exp5_exercises.py</h3>")
    A(code(src_ex))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex))
    A("<p class=cap>Figure 3. Mean accuracy over the five seeds against k "
      "(left, with each seed's individual accuracy shown as a faint point "
      "behind the mean) and total model calls against k (right). The "
      "per-seed spread is what makes the mean dip slightly at k=5; k is "
      "drawn on evenly spaced ticks, so the cost line bends even though "
      "calls are exactly k &times; 10 questions &times; 5 seeds.</p>")
    A("<img src='outputs/exp5_fig3_k_sweep.png' style='width:100%;'>")
    A("<h3>Discussion</h3>")
    A("<p>Mean accuracy rises steadily and noisily at small k (0.660 at "
      "k=1, with individual seeds ranging from 0.40 to 0.80, showing how "
      "unstable a single sample or a small sample is) up through 0.860 at "
      "k=3 and 0.840 at k=5, before reaching 0.960 at k=9 and staying at "
      "0.960 at k=15 &mdash; so k=9 is the point beyond which accuracy "
      "stops improving appreciably in this run; doubling k to 15 buys no "
      "further mean accuracy at all, only 300 more calls. At k=9 the mean "
      "number of correct answers per seed is 9.60/10, for 90 calls per "
      "seed, giving 90 / 9.60 &asymp; 9.38 calls per correct answer at the "
      "plateau &mdash; noticeably worse than the 10/7 &asymp; 1.43 calls "
      "per correct answer of greedy CoT, which is the concrete cost of "
      "buying the extra ~2 correct answers that self-consistency recovers "
      "on this question set. The mean also masks real per-seed variance "
      "(k=5 dips to 0.60 accuracy on seed 11, worse than several k=1 "
      "seeds), which is exactly why the exercise asks for several seeds "
      "rather than reporting a single run's number as if it were k's true "
      "accuracy.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; Abstention by vote margin</h2>")
    A("<p><b>Task.</b> Add an abstention rule that answers only when the "
      "winning answer leads the runner-up by at least a stated margin, "
      "and otherwise declines to answer. Report coverage and accuracy on "
      "the answered subset for two different margins, and discuss the "
      "trade-off.</p>")
    A("<p><b>Approach.</b> Margin is defined as an absolute vote-count "
      "lead of the winning answer over the runner-up "
      "(<span class=m>winner_votes - runnerup_votes &ge; margin</span>); "
      "a question with only one distinct extracted answer is treated as "
      "having a runner-up count of 0, so a unanimous vote always clears "
      "any margin tested here. Two margins are tested at k=7, seed=42: "
      "margin=1 (answer whenever the winner has any lead at all) and "
      "margin=2 (require a lead of at least two votes).</p>")
    A("<p class=cap>Figure 4. Coverage and accuracy on the answered subset "
      "at each margin. Raising the margin from 1 to 2 drops one question "
      "(q05, the 4&ndash;3 split) out of the answered set, which is "
      "precisely the question the vote got wrong.</p>")
    A("<img src='outputs/exp5_fig4_abstention.png' style='width:70%;'>")
    A("<h3>Discussion</h3>")
    A("<p>At margin=1, coverage is 1.00 (10/10 questions answered) with "
      "accuracy-on-answered of 0.90 (9/10) &mdash; identical to the "
      "unconstrained self-consistency result, since every question in "
      "this run has at least a 1-vote lead for its plurality answer. At "
      "margin=2, the rule abstains on exactly q05 &mdash; the same "
      "question flagged in Observation 2 as having the narrowest margin "
      "in the whole run (80:4 vs 75:3, a lead of only 1 vote) &mdash; "
      "dropping coverage to 0.90 (9/10) but raising accuracy-on-answered "
      "to a perfect 1.00 (9/9). The trade-off is therefore visible in a "
      "single concrete case: tightening the margin from 1 to 2 sacrifices "
      "10% coverage but removes precisely the one question the system was "
      "actually going to get wrong, because a narrow margin and a wrong "
      "answer coincided here. That is not a guarantee &mdash; a narrow "
      "margin only signals higher uncertainty in the vote, not certain "
      "wrongness &mdash; but it shows abstention buys a genuine accuracy "
      "improvement on the questions it still answers, at the cost of "
      "leaving the harder questions unanswered rather than answering them "
      "wrong.</p>")

    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>The chain-of-thought self-consistency pipeline was implemented "
      "end to end on a fixed ten-question set: two prompt templates "
      "(Direct and worked-example CoT), a scripted per-question reasoner "
      "that renders a correct path and one or two plausible wrong paths, "
      "a regex-based <span class=m>extract_answer()</span> that "
      "normalises numeric answers to a canonical form and returns "
      "<span class=m>None</span> on unparseable traces, and a majority "
      "vote with a documented tie-break rule. Direct and CoT-greedy both "
      "scored 7/10 at 10 model calls each, since greedy's single fixed "
      "path takes the plausible-but-wrong shortcut on three questions "
      "built specifically to contain one; self-consistency at k=7 scored "
      "9/10 at 70 calls, correcting two of those three by plurality vote "
      "while its remaining error coincided with the single narrowest vote "
      "margin observed anywhere in the run.</p>")
    A("<p>The two exercises then quantified that trade-off directly. "
      "Sweeping k over {1, 3, 5, 9, 15} across five seeds each showed "
      "mean accuracy climbing from 0.660 to a 0.960 plateau reached at "
      "k=9, at a marginal cost of about 9.38 calls per correct answer at "
      "that plateau versus roughly 1.43 for greedy CoT &mdash; the price "
      "of self-consistency's k-times-the-calls scaling made concrete. "
      "Adding an abstention rule keyed on the winning margin then showed "
      "that the question self-consistency still gets wrong is exactly the "
      "one with the thinnest vote margin: tightening the margin "
      "requirement from 1 to 2 votes dropped coverage from 1.00 to 0.90 "
      "but raised accuracy on the answered subset from 0.90 to a perfect "
      "1.00, by declining to answer precisely the question the vote was "
      "least confident about.</p>")

    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "questions.py, exp5_cot_selfconsistency.py, "
              "exp5_exercises.py, make_plots.py, make_report.py"],
             ["Libraries used",
              "Python standard library only (<span class=m>random</span>, "
              "<span class=m>re</span>, <span class=m>collections."
              "Counter</span>) for every program that produces a result; "
              "Matplotlib (permitted, Table 1) is used solely by "
              "<span class=m>make_plots.py</span> to draw the figures, and "
              "influences no reported number &mdash; it imports the same "
              "functions the console programs call and plots their return "
              "values. No agent framework, orchestration library, "
              "or external API/network access was used, in accordance "
              "with clause 3.1 of the Rules and Regulations."],
             ["Reproducibility",
              "The question set and gold answers are fixed, every sampled "
              "trace is drawn from a <span class=m>random.Random</span> "
              "seeded deterministically from (seed, question id, sample "
              "index), and the greedy path per question is fixed, so "
              "every run at a given seed and k reproduces exactly."],
             ["Sources consulted",
              "Course manual for Experiment 5 (chain-of-thought prompting, "
              "self-consistency by sampling, majority voting over "
              "extracted answers)."]],
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
    name = "LAB_5_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_5_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
