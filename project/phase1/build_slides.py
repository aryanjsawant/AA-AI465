"""
Builds the Phase 1 slide deck (8 slides) and exports it to PDF.

    python build_slides.py
"""

import os

from slidekit import BLUE, INK2, MUTED, ORANGE, PANEL, WHITE, Deck, to_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROLL = "U23AI042"
FIG = os.path.join(HERE, "figures")
PPTX = os.path.join(HERE, "RP1_%s_slides.pptx" % ROLL)
PDF = os.path.join(HERE, "RP1_%s_slides.pdf" % ROLL)

d = Deck("AI465 Research Project, Phase 1   |   %s" % ROLL)

# 1 ---------------------------------------------------------------- title
s = d.slide()
d.text(s, "AI465 Agentic AI   |   Research Project, Phase 1", 0.9, 1.5, 11, 0.4,
       size=16, color=MUTED)
d.text(s, "Early-Stopping Self-Consistency", 0.9, 2.1, 11.5, 1.0, size=46,
       bold=True)
d.text(s, "Is the saving still a gain at a matched budget on a small "
       "open-weight model?", 0.9, 3.2, 11, 1.0, size=24, color=INK2)
d.text(s, ["Roll No. %s" % ROLL,
           "Syllabus unit: LLMs as reasoning engines (chain-of-thought and "
           "self-consistency)"], 0.9, 5.2, 11, 0.9, size=16, color=INK2)

# 2 --------------------------------------------------------------- papers
s = d.slide("Three papers, one narrow problem", "Papers")
d.text(s, "How many samples does self-consistency really need?", 0.9, 1.55,
       11.5, 0.5, size=20, color=INK2)
rows = [
    ("PRIMARY", "Li et al., ICLR 2024",
     "Escape Sky-high Cost: Early-stopping Self-Consistency for Multi-step "
     "Reasoning", "Stops sampling when a window of answers is unanimous. "
     "Public code. Six benchmarks, three models.", ORANGE),
    ("CONTEXT", "Wang et al., ICLR 2023",
     "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
     "The method being made cheaper: sample many solutions, take the "
     "majority answer.", BLUE),
    ("CONTEXT", "Aggarwal et al., EMNLP 2023",
     "Let's Sample Step by Step: Adaptive-Consistency",
     "The earlier adaptive rule: stop when a Beta posterior passes 0.95.",
     BLUE),
]
for i, (tag, venue, title, note, color) in enumerate(rows):
    y = 2.3 + i * 1.5
    d.panel(s, 0.9, y, 11.5, 1.3)
    chip = d.panel(s, 1.1, y + 0.2, 1.25, 0.36, color)
    d.text(s, tag, 1.1, y + 0.24, 1.25, 0.3, size=12, bold=True, color=WHITE,
           align="center")
    d.text(s, venue, 1.1, y + 0.72, 2.6, 0.4, size=14, color=INK2)
    d.text(s, title, 3.6, y + 0.17, 8.6, 0.5, size=18, bold=True)
    d.text(s, note, 3.6, y + 0.68, 8.6, 0.5, size=15, color=INK2)

# 3 -------------------------------------------------------------- problem
s = d.slide("Self-consistency works, and it is expensive", "Problem")
d.bullets(s, [
    ("Chain of thought, greedy: ", "one solution, one answer. An early slip "
     "is never recovered."),
    ("Self-consistency (SC): ", "sample L solutions at temperature 0.7 and "
     "return the most frequent answer."),
    ("The price: ", "cost grows in step with L, and L is the same for an easy "
     "question as for a hard one."),
], 0.9, 1.8, 6.6, 3.6, size=20, gap=16)
d.panel(s, 8.0, 1.8, 4.4, 3.5)
d.text(s, "about $2,000", 8.0, 2.25, 4.4, 0.9, size=44, bold=True,
       align="center")
d.text(s, ["SC with 64 samples over the MATH", "benchmark on GPT-4",
           "(Li et al., Sec. 1)"], 8.2, 3.5, 4.0, 1.3, size=16, color=INK2,
       align="center")
d.text(s, "Most questions do not need all L samples. Which ones do?", 0.9,
       5.9, 11.5, 0.5, size=22, bold=True)

# 4 --------------------------------------------------------------- method
s = d.slide("ESC: stop when one window agrees with itself", "Method")
d.image(s, os.path.join(FIG, "fig_esc_windows.png"), 0.9, 1.6, w=8.3)
d.bullets(s, [
    ("Loop: ", "draw w samples, check if all w answers are equal."),
    ("Equal: ", "stop, return that answer."),
    ("Not equal: ", "keep them, draw the next window."),
    ("Budget spent: ", "vote over all L, exactly as SC."),
], 9.5, 1.7, 3.3, 3.6, size=16, gap=10)
d.panel(s, 0.9, 5.0, 11.5, 1.6)
d.bullets(s, [
    ("No threshold to tune. ", "Adaptive-Consistency checks a Beta posterior "
     "against 0.95 after every single sample."),
    ("Two supports: ", "a z-test bound that an early stop rarely disagrees "
     "with full SC (Sec. 2.3), and a control scheme that predicts cost and "
     "accuracy for a choice of (w, L) (Sec. 2.4)."),
], 1.15, 5.15, 11.0, 1.4, size=16, gap=6)

# 5 ----------------------------------------------------------- evaluation
s = d.slide("What the paper tested and what it reported", "Evaluation")
d.table(s, [
    ["Setting", "Value"],
    ["Benchmarks", "MATH, GSM8K, CSQA, StrategyQA, Last Letters, Coin Flip"],
    ["Models", "GPT-4, GPT-3.5-Turbo, Llama-2 7b"],
    ["Prompts", "few-shot chain of thought (Wei et al.)"],
    ["Decoding", "temperature 0.7 (0.5 for MATH)"],
    ["ESC settings", "w = 5, L = 40 (8 and 64 for MATH)"],
    ["Runs", "average of 10, variance omitted"],
], 0.9, 1.7, 6.3, 3.4, col_widths=[1.7, 4.6], size=14, numeric=False)
d.panel(s, 7.6, 1.7, 4.8, 3.4)
d.text(s, "GSM8K, GPT-4 (Table 1)", 7.85, 1.85, 4.4, 0.4, size=15, color=INK2)
d.text(s, "89.29%", 7.85, 2.3, 4.4, 0.9, size=48, bold=True)
d.text(s, "the same accuracy as SC with 40 samples", 7.85, 3.25, 4.4, 0.4,
       size=15, color=INK2)
d.text(s, "7.98 samples", 7.85, 3.8, 4.4, 0.6, size=30, bold=True)
d.text(s, "per question instead of 40", 7.85, 4.45, 4.4, 0.4, size=15,
       color=INK2)
d.text(s, "Reported saving in samples: GSM8K 80%, StrategyQA 77%, CSQA 79%, "
       "Coin Flip 84%, Last Letters 67%, MATH 34% (abstract).", 0.9, 5.6, 11.5,
       0.9, size=17, color=INK2)

# 6 ----------------------------------------------------------- gaps 1 + 2
s = d.slide("Gaps 1 and 2: the comparison that matters is unmeasured",
            "Research gaps")
for i, (kind, head, body) in enumerate([
    ("EVALUATION", "The matched-budget gain is smaller than the noise nobody "
     "reported",
     ["Table 1: ESC beats SC at the same sample count by 0.22, 0.85 and 0.22 "
      "points on GSM8K.",
      "Sec. 3.2: \"averaged over 10 runs and omit variance\".",
      "0.22 points of 1,319 questions is three questions."]),
    ("COST AND LATENCY", "Cost is counted in samples and dollars, never in "
     "time",
     ["Tables 1 and 7: samples, tokens, dollars. No wall-clock figure.",
      "SC asks for L samples in one parallel request. Algorithm 1 waits for "
      "each window: up to L/w = 8 round trips.",
      "Llama-2 7b on GSM8K: 22% of samples saved, about six round trips."]),
]):
    x = 0.9 + i * 5.9
    d.panel(s, x, 1.7, 5.6, 4.9)
    d.panel(s, x + 0.25, 1.95, 2.3, 0.36, BLUE)
    d.text(s, kind, x + 0.25, 1.99, 2.3, 0.3, size=12, bold=True, color=WHITE,
           align="center")
    d.text(s, head, x + 0.25, 2.5, 5.1, 1.0, size=20, bold=True)
    d.bullets(s, body, x + 0.25, 3.6, 5.1, 2.9, size=16, gap=10)

# 7 ----------------------------------------------------------- gaps 3 + 4
s = d.slide("Gaps 3 and 4: weak models and wrong but confident answers",
            "Research gaps")
d.image(s, os.path.join(FIG, "fig_paper_table1.png"), 0.9, 1.6, w=7.4)
d.text(s, "GSM8K numbers from Table 1 of the paper, plotted by me.", 0.9, 4.15,
       7.4, 0.3, size=12, color=MUTED, italic=True)
d.panel(s, 8.6, 1.6, 3.85, 2.6)
d.panel(s, 8.8, 1.78, 1.6, 0.34, BLUE)
d.text(s, "GENERALITY", 8.8, 1.81, 1.6, 0.3, size=11, bold=True, color=WHITE,
       align="center")
d.bullets(s, ["Saving falls 80% to 22% as the model weakens.",
              "Only open-weight model: Llama-2 7b at 21.75%. Nothing in the "
              "middle, nothing laptop-sized."], 8.8, 2.25, 3.5, 1.9, size=14,
          gap=6)
d.panel(s, 0.9, 4.6, 11.55, 2.1)
d.panel(s, 1.1, 4.78, 1.7, 0.34, BLUE)
d.text(s, "ASSUMPTION", 1.1, 4.81, 1.7, 0.3, size=11, bold=True, color=WHITE,
       align="center")
d.bullets(s, [
    ("The bound is about agreeing with SC, not about being right. ",
     "Table 5 reports only the overlap of ESC and SC answers; no figure for "
     "how often a stop lands on a wrong answer."),
    ("It is quoted for w = 8 (at most 0.002). ",
     "Five of six benchmarks use w = 5, where z = sqrt(5) gives about 0.013."),
], 1.1, 5.25, 11.1, 1.4, size=15, gap=6)

# 8 ------------------------------------------------------------ objective
s = d.slide("One objective, taken from Gap 1", "Objective")
d.panel(s, 0.9, 1.65, 11.55, 2.25, PANEL)
d.text(s, "To evaluate early-stopping self-consistency (window 5, at most 20 "
       "samples) for arithmetic word problems on a fixed 50-question subset "
       "of GSM8K test (1,319), with Qwen2.5-1.5B-Instruct run locally, "
       "compared against fixed-size self-consistency at a matched sample "
       "budget, measured by exact-match accuracy and by samples, tokens, "
       "rounds and latency per question, as mean and standard deviation over "
       "three seeded runs.", 1.15, 1.8, 11.05, 2.0, size=18, bold=True)
cols = [
    ("Why this one", ["Repeats the paper's matched-budget row, with the "
                      "variance attached.",
                      "A 1.5B model sits in the regime Gap 3 says is missing.",
                      "Latency and stop-correctness (Gaps 2, 4) come from the "
                      "same traces."]),
    ("Budget", ["20 samples x 50 questions x 3 runs = 3,000 generations.",
                "About 0.3M completion and 0.25M prompt tokens.",
                "Laptop CPU, llama.cpp, three to four hours, zero cost."]),
    ("Plan for Phase 2", ["Baselines first: greedy CoT and SC at k = 1 to 20.",
                          "Then ESC on the same samples, so only the stopping "
                          "rule differs.",
                          "Ablation: random stopping with ESC's budgets."]),
]
for i, (head, items) in enumerate(cols):
    x = 0.9 + i * 3.9
    d.text(s, head, x, 4.2, 3.6, 0.4, size=17, bold=True, color=BLUE)
    d.bullets(s, items, x, 4.65, 3.6, 2.3, size=13.5, gap=5)

d.save(PPTX)
to_pdf(PPTX, PDF)
print("wrote", PPTX, "and", PDF)
