"""
Builds the Phase 2 slide deck (10 slides) from results/summary.json and the
figures, and exports it to PDF.

    python report/build_slides.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_report as R                                         # noqa: E402
from slidekit import BLUE, INK2, MUTED, ORANGE, PANEL, WHITE, Deck, to_pdf  # noqa: E402

FIG = os.path.join(R.ROOT, "figures")
PPTX = os.path.join(HERE, "RP2_%s_slides.pptx" % R.ROLL)
PDF = os.path.join(HERE, "RP2_%s_slides.pdf" % R.ROLL)
S, A, ESC, AC, SC = R.S, R.A, R.ESC, R.AC, R.SC
L, W, N, K_LO, K_HI = R.L, R.W, R.N, R.K_LO, R.K_HI

d = Deck("AI465 Research Project, Phase 2   |   %s" % R.ROLL)


def stat(s, x, y, w, value, label, color=None):
    d.panel(s, x, y, w, 1.55)
    d.text(s, value, x, y + 0.15, w, 0.7, size=32, bold=True, align="center")
    d.text(s, label, x + 0.15, y + 0.9, w - 0.3, 0.6, size=13, color=INK2,
           align="center")


# 1 ---------------------------------------------------------------- title
s = d.slide()
d.text(s, "AI465 Agentic AI   |   Research Project, Phase 2", 0.9, 1.5, 11, 0.4,
       size=16, color=MUTED)
d.text(s, "Early-Stopping Self-Consistency", 0.9, 2.1, 11.5, 1.0, size=46,
       bold=True)
d.text(s, "On a small open-weight model at a matched budget: fewer samples, "
       "no clear accuracy gain, more tokens", 0.9, 3.2, 11, 1.0, size=24, color=INK2)
d.text(s, ["Roll No. %s" % R.ROLL,
           "Implementation and evaluation of the objective approved in Phase 1"],
       0.9, 5.2, 11, 0.9, size=16, color=INK2)

# 2 ------------------------------------------------------------ objective
s = d.slide("The approved objective, and what was built", "Objective")
d.panel(s, 0.9, 1.65, 11.55, 2.1)
d.text(s, R.OBJECTIVE, 1.15, 1.8, 11.05, 1.9, size=17, bold=True)
d.bullets(s, [
    ("Built: ", "greedy CoT and SC-k baselines, ESC, a random-stopping "
     "ablation, Adaptive-Consistency for context, a resumable sampler with "
     "full traces, an offline evaluator and a live demo."),
    ("Scope: ", R.DEVIATION),
], 0.9, 4.1, 11.55, 2.6, size=16, gap=10)

# 3 ---------------------------------------------------------------- setup
s = d.slide("Pinned configuration", "Setup")
d.table(s, [["Item", "Value"]] + [list(r) for r in R.SETUP_ROWS], 0.9, 1.65,
        11.55, 4.6, col_widths=[1.9, 9.65], size=13, numeric=False)
d.text(s, "Prompts are files in prompts/. Every run writes one JSON trace per "
       "question. Tables regenerate from the traces with no model call.",
       0.9, 6.35, 11.55, 0.5, size=14, color=INK2)

# 4 --------------------------------------------------------------- design
s = d.slide("One pool of samples, so only the stopping rule differs", "Design")
d.image(s, os.path.join(R.ROOT, "..", "phase1", "figures",
                        "fig_esc_windows.png"), 0.9, 1.6, w=7.6)
d.bullets(s, [
    ("Sample once: ", "%d rounds of %d per question and run." % (L // W, W)),
    ("SC-k: ", "reads the first k samples."),
    ("ESC: ", "reads whole rounds until one is unanimous."),
    ("Same: ", "model, prompt, decoding, samples."),
], 8.8, 1.7, 3.9, 3.0, size=16, gap=9)
for i, (head, body) in enumerate([
    ("Matched budget", "SC at ESC's mean sample count, rounded down (k = %d) "
     "and up (k = %d)." % (K_LO, K_HI)),
    ("Ablation", "Random stopping: ESC's sample counts shuffled across "
     "questions. Same budget, no signal."),
    ("Cost", "Samples, sequential rounds, prompt and completion tokens, "
     "measured wall-clock time per round."),
]):
    x = 0.9 + i * 3.9
    d.panel(s, x, 4.75, 3.7, 1.95)
    d.text(s, head, x + 0.2, 4.9, 3.3, 0.4, size=16, bold=True, color=BLUE)
    d.text(s, body, x + 0.2, 5.35, 3.3, 1.3, size=14)

# 5 -------------------------------------------------------------- results
s = d.slide("Results: mean and standard deviation over 3 runs", "Results")
rows = R.table_rows()
esc_row = next(i for i, r in enumerate(rows) if r[0].startswith("ESC"))
d.table(s, rows, 0.9, 1.6, 11.55, 4.4,
        col_widths=[3.25, 1.75, 1.1, 1.0, 1.15, 1.15, 1.1, 1.05], size=12.5,
        highlight_rows=(esc_row,))
d.text(s, "%d GSM8K questions, costs per question. Prompt tokens: one prompt "
       "per round. Source: results/summary.csv, python src/evaluate.py." % N,
       0.9, 6.3, 11.55, 0.5, size=13, color=INK2)

# 6 ------------------------------------------------------------ finding 1
s = d.slide("Finding 1: no detectable accuracy gain at a matched budget",
            "Analysis")
d.image(s, os.path.join(FIG, "fig1_accuracy_vs_cost.png"), 0.9, 1.6, h=4.6)
d.text(s, "Checker-sensitive: with replies that lack an answer line scored as "
       "no answer, ESC is ahead by %+.1f ± %.1f points. Not settled at this "
       "sample size." % (R.SD_CEIL[0], R.SD_CEIL[1]), 0.9, 6.3, 8.3, 0.6,
       size=13, color=INK2)
stat(s, 9.4, 1.7, 3.0, "%.1f%%" % ESC["correct"][0],
     "ESC, %.1f samples per question" % ESC["samples"][0])
stat(s, 9.4, 3.4, 3.0, "%.1f%%" % SC(K_HI)["correct"][0],
     "SC-%d, the same budget" % K_HI)
stat(s, 9.4, 5.1, 3.0, "%+.1f ± %.1f" % (R.D_CEIL[0], R.D_CEIL[1]),
     "paired difference in points")

# 7 ------------------------------------------------------------ finding 2
s = d.slide("Finding 2: fewer samples, but more tokens and more rounds",
            "Analysis")
d.image(s, os.path.join(FIG, "fig3_cost.png"), 0.9, 1.6, w=11.55)
d.bullets(s, [
    ("%.0f%% fewer samples than SC-%d, " % (R.SAVED, L),
     "with the same answers (agreement %.0f%%)." % S["esc_sc_agreement"][0]),
    ("%.0f%% more total tokens: " % (100 * (R.tot(ESC) / R.tot(SC(L)) - 1)),
     "every window re-sends the %d-token prompt."
     % round(S["prompt_tokens_mean"])),
    ("%.1f sequential rounds against 1. " % ESC["rounds"][0],
     "Behind a parallel API the rounds are the latency."),
], 0.9, 5.05, 11.55, 1.8, size=16, gap=6)

# 8 ------------------------------------------------------------ finding 3
s = d.slide("Finding 3: the stopping signal is precise, and worth little", "Ablation")
d.image(s, os.path.join(FIG, "fig2_stopping.png"), 0.9, 1.6, h=3.5)
d.image(s, os.path.join(FIG, "fig4_window_ablation.png"), 7.1, 1.7, w=5.5)
d.bullets(s, [
    ("Random stopping with the same budgets: ",
     "%.1f%%. The signal is worth %+.1f ± %.1f points."
     % (R.RAND_MEAN, R.D_RAND[0], R.D_RAND[1])),
    ("Early stops: ", "%d of %d question-runs; %d of them wrong."
     % (R.EARLY_N, N * len(S["runs"]), S["failure_cases"])),
    ("Window size: ", "w = 2 uses %.1f samples for %.1f%%; w = 10 uses %.1f "
     "for %.1f%%." % (A["ESC w=2"]["samples"][0], A["ESC w=2"]["correct"][0],
                      A["ESC w=10"]["samples"][0], A["ESC w=10"]["correct"][0])),
], 0.9, 5.25, 11.55, 1.6, size=16, gap=6)

# 9 --------------------------------------------------------- failure case
s = d.slide("A failure read from the trace: a confident wrong stop",
            "Failure case")
d.panel(s, 0.9, 1.65, 5.6, 4.9)
d.text(s, "Question 99", 1.15, 1.8, 5.1, 0.4, size=15, bold=True, color=BLUE)
d.text(s, "Mary receives 18 new potted plants. She already has 2 on each of "
       "her 40 window ledges. She gives away 1 plant from each ledge. How "
       "many plants does she keep?", 1.15, 2.2, 5.1, 1.5, size=15)
d.text(s, "Gold: 58", 1.15, 3.75, 5.1, 0.4, size=17, bold=True)
d.text(s, "Run 11, first window", 1.15, 4.4, 5.1, 0.4, size=15, bold=True,
       color=BLUE)
d.text(s, "40    40    40    40    40", 1.15, 4.8, 5.1, 0.4, size=15)
d.text(s, "ESC stops after 5 samples and returns 40. Of all 20 samples, 18 "
       "say 40.", 1.15, 5.4, 5.1, 0.8, size=15)
d.panel(s, 6.8, 1.65, 5.65, 2.2, PANEL)
d.text(s, "From the trace (traces/run_11/q0099.json)", 7.05, 1.8, 5.2, 0.4,
       size=15, bold=True, color=BLUE)
d.text(s, "\"Mary has 2 plants on each of 40 ledges, so she has 2 * 40 = 80 "
       "plants already. She will give away 1 plant per ledge ... 80 - 40 = "
       "40.\"", 7.05, 2.2, 5.2, 1.6, size=15, italic=True)
d.bullets(s, [
    ("Cause: ", "the 18 new plants in the first sentence are never used."),
    ("Unanimity measures consistency, ", "not correctness."),
    ("No harm here: ", "SC-20 returns 40 as well, so ESC lost nothing and "
     "saved 15 samples."),
    ("%d of %d early stops were wrong; " % (S["failure_cases"], R.EARLY_N),
     "%d of %d questions are wrong in every run." % (S["always_wrong"], N)),
], 6.8, 4.1, 5.65, 2.6, size=15, gap=8)

# 10 --------------------------------------------------------- limitations
s = d.slide("Limitations, next steps and the demo", "Close")
d.text(s, "Limitations", 0.9, 1.65, 5.6, 0.4, size=17, bold=True, color=BLUE)
d.bullets(s, [
    "%d questions, one model, one prompt: only large effects are visible." % N,
    "L = 20, not the paper's 40.",
    "Greedy baseline %.0f%% against 73.2%% published for this model "
    "(4-bit weights, own prompt, small n)." % R.G["correct"],
    "Latency from a shared laptop; the round count is the portable figure.",
], 0.9, 2.1, 5.6, 3.2, size=15, gap=8)
d.text(s, "With four more weeks", 6.9, 1.65, 5.6, 0.4, size=17, bold=True,
       color=BLUE)
d.bullets(s, [
    "Full 1,319 questions and L = 40 on a GPU.",
    "A second, stronger open-weight model.",
    "Latency against a hosted API with parallel sampling.",
    "ESC with the prompt cached across windows.",
], 6.9, 2.1, 5.6, 3.2, size=15, gap=8)
d.panel(s, 0.9, 5.3, 11.55, 1.4, ORANGE)
d.text(s, "Live demo:   python demo.py --task 6", 1.15, 5.45, 11.0, 0.5,
       size=22, bold=True, color=WHITE)
d.text(s, "ESC on one GSM8K question, window by window, with the trace "
       "written to traces/demo/.", 1.15, 6.05, 11.0, 0.5, size=15, color=WHITE)

d.save(PPTX)
to_pdf(PPTX, PDF)
print("wrote", PPTX, "and", PDF)
