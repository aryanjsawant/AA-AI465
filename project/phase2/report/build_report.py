"""
Builds the Phase 2 report (at most four pages) from results/summary.json and
the figures, as .docx, and exports it to PDF through Word.

    python report/build_report.py

Every number in the text is read from results/, so the report follows the
data if the experiment is re-run. The interpretation in ANALYSIS was written
against the reported runs and should be re-read if the numbers move.
"""

import json
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ROLL = "U23AI042"
DOCX = os.path.join(HERE, "RP2_%s_report.docx" % ROLL)
PDF = os.path.join(HERE, "RP2_%s_report.pdf" % ROLL)

with open(os.path.join(ROOT, "results", "summary.json"), encoding="utf-8") as f:
    S = json.load(f)
with open(os.path.join(ROOT, "results", "strict", "summary.json"),
          encoding="utf-8") as f:
    STRICT = json.load(f)
with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as f:
    CFG = json.load(f)

A = S["agg"]
L, W, N = S["max_samples"], S["window"], S["n_questions"]
ESC = A[S["esc_name"]]
AC = A["AC (Beta 0.95, L=%d)" % L]
K_LO, K_HI = S["k_matched"]
SC = lambda k: A["SC-%d" % k]
G = S["greedy"]


def pm(pair, d=1):
    return ("%." + str(d) + "f ± %." + str(d) + "f") % (pair[0], pair[1])


def tot(a):
    return a["prompt_tokens"][0] + a["completion_tokens"][0]


RAND = S["random_stop_runs"]
RAND_MEAN = sum(RAND) / len(RAND)
D = S["diffs"]
D_FLOOR = D["ESC - SC-%d (matched, floor)" % K_LO]
D_CEIL = D["ESC - SC-%d (matched, ceil)" % K_HI]
D_RAND = D["ESC - random stopping"]
STOP = S["stop_stats"]
EARLY_N = sum(v["n"] for k, v in STOP.items() if k != "no stop")
EARLY_SHARE = 100 - STOP["no stop"]["share"]
SAVED = 100 * (L - ESC["samples"][0]) / L
HOURS = S["total_sampling_seconds"] / 3600

OBJECTIVE = (
    "To evaluate early-stopping self-consistency (ESC; window 5, at most 20 "
    "samples) for arithmetic word problems on a fixed random subset of 50 "
    "questions from the GSM8K test set (1,319 questions), using the "
    "open-weight Qwen2.5-1.5B-Instruct model run locally, compared against "
    "fixed-size self-consistency (SC) at a matched sample budget, measured by "
    "exact-match accuracy and by samples, tokens, sequential rounds and "
    "wall-clock latency per question, each reported as mean and standard "
    "deviation over three seeded runs.")

if N == CFG["subset_size"]:
    DEVIATION = ("The objective was implemented as approved, with no change "
                 "of scope.")
else:
    DEVIATION = (
        "Declared reduction of scope: %d of the 50 questions are reported. "
        "Sampling on the laptop CPU ran at roughly four minutes per question "
        "(three runs of 20 samples), about twice the Phase 1 estimate, "
        "because the machine was shared with other work. The subset is a "
        "prefix of one seeded shuffle, so these are the first %d of the same "
        "50, not a different selection, and src/sample.py resumes from where "
        "it stopped. Nothing else was changed." % (N, N))

IMPLEMENTED = [
    "Baseline. Chain-of-thought with greedy decoding (one call) and SC "
    "(Wang et al., 2023) at every sample count k from 1 to %d." % L,

    "Method under study. ESC (Li et al., 2024, Algorithm 1): samples are "
    "drawn in windows of %d; if all answers in a window are equal, sampling "
    "stops and that answer is returned; otherwise the next window is drawn, "
    "and after %d samples the usual majority vote is taken." % (W, L),

    "One pool of samples for all methods. For each run and question the model "
    "is sampled in %d sequential rounds of %d. SC-k reads the first k samples "
    "and ESC reads whole rounds until its rule fires. Model, prompt, decoding "
    "settings and samples are therefore identical across methods, and the only "
    "thing that differs is the stopping rule (src/methods.py, 90 lines)."
    % (L // W, W),

    "Ablation and context. (i) Random stopping: ESC's per-question sample "
    "counts are shuffled across questions (500 shuffles), which keeps the "
    "budget and removes the signal. (ii) Window sizes 2, 3, 4, 10. "
    "(iii) Adaptive-Consistency with the Beta rule at 0.95 (Aggarwal et al., "
    "2023), re-implemented from the paper.",

    "Infrastructure. A resumable sampler that writes one JSON trace per run "
    "and question (prompt, every reply, tokens, per-round wall-clock time), "
    "retries failed calls and re-draws a round whose timing was spoilt by a "
    "stall; an evaluator that rebuilds every table from the traces without "
    "calling the model; and demo.py, which runs ESC live on one question.",
]

SETUP_ROWS = [
    ("Model", "Qwen2.5-1.5B-Instruct, GGUF q4_k_m (sha256 6a1a2eb6...434e9407e)"),
    ("Runtime", "llama.cpp llama-server b11429, CPU only, 4 threads, 5 slots"),
    ("Decoding", "temperature 0.7, top-p 0.9, top-k off, repeat penalty 1.0, "
                 "max 256 new tokens; greedy baseline at temperature 0"),
    ("Prompt", "system message + 3 worked examples of my own + question "
               "(prompts/, about %d prompt tokens)" % round(S["prompt_tokens_mean"])),
    ("Tasks", "GSM8K test, subset seed 465, %d questions (data/subset_ids.json)" % N),
    ("Runs", "3, seeds 11, 22, 33; sample seed = run x 10^6 + question x 100 + index"),
    ("Checker", "exact match on the number after \"Final answer\", else the "
                "last number in the reply; no LLM judge"),
    ("Date, cost", "6 October 2026; %d sampled generations, %.2fM completion "
                   "tokens, %.1f h of CPU, zero rupees"
     % (S["total_samples"], S["total_completion_tokens"] / 1e6, HOURS)),
]


def table_rows():
    rows = [["Method", "Accuracy %", "Samples", "Rounds", "Prompt tok",
             "Compl. tok", "Total tok", "Latency s"]]
    rows.append(["CoT greedy (1 call)", "%.1f" % G["correct"], "1", "1",
                 "%.0f" % G["prompt_tokens"], "%.0f" % G["completion_tokens"],
                 "%.0f" % (G["prompt_tokens"] + G["completion_tokens"]),
                 "%.1f" % G["latency_s"]])
    names = [("SC-%d" % k, "SC-%d" % k) for k in sorted({W, K_LO, K_HI, 10, L})]
    labels = {"SC-%d" % K_LO: "SC-%d (matched, floor)" % K_LO,
              "SC-%d" % K_HI: "SC-%d (matched, ceil)" % K_HI,
              "SC-%d" % L: "SC-%d (full budget)" % L}
    names += [(S["esc_name"], "ESC (w=%d, L=%d)" % (W, L)),
              ("AC (Beta 0.95, L=%d)" % L, "Adaptive-Consistency")]
    for key, label in names:
        a = A[key]
        rows.append([labels.get(key, label), pm(a["correct"]),
                     "%.2f" % a["samples"][0], "%.2f" % a["rounds"][0],
                     "%.0f" % a["prompt_tokens"][0],
                     "%.0f" % a["completion_tokens"][0], "%.0f" % tot(a),
                     pm(a["latency_s"])])
    rows.append(["Random stopping (ablation)",
                 "%.1f ± %.1f" % (RAND_MEAN, (sum((x - RAND_MEAN) ** 2 for x in RAND)
                                              / (len(RAND) - 1)) ** 0.5),
                 "%.2f" % ESC["samples"][0], "%.2f" % ESC["rounds"][0],
                 "%.0f" % ESC["prompt_tokens"][0], "", "", ""])
    return rows


if S["failure_cases"] == 0:
    STOP_SENTENCE = ("Every one of the %d early stops landed on the correct "
                     "answer (Figure 2), so the worry in Gap 4 of Phase 1, a "
                     "confident wrong stop, did not occur." % EARLY_N)
else:
    STOP_SENTENCE = ("%d of the %d early stops landed on a wrong answer "
                     "(Figure 2; results/failure_cases.md), the confident "
                     "wrong stop that Gap 4 of Phase 1 pointed at."
                     % (S["failure_cases"], EARLY_N))

S_ESC = STRICT["agg"][STRICT["esc_name"]]
S_KHI = STRICT["k_matched"][1]
SD_FLOOR = STRICT["diffs"]["ESC - SC-%d (matched, floor)" % STRICT["k_matched"][0]]
SD_CEIL = STRICT["diffs"]["ESC - SC-%d (matched, ceil)" % S_KHI]

ANALYSIS = [
    ("Baseline against published numbers. ",
     "Greedy chain of thought scores %.1f%% here; the Qwen team reports 73.2%% "
     "on GSM8K for this model. I did not close that gap. The likely causes are "
     "the 4-bit quantised weights, my own three-example prompt with replies "
     "kept to a few sentences (about %.0f tokens), and the size of the subset: "
     "at n = %d one question is %.1f points. For ESC itself, Table 8 of the "
     "paper (L = 20) gives 10.14 samples for GPT-3.5-Turbo (SC accuracy 85%%) "
     "and 17.06 for Llama-2 7b (21%%). This model, with SC accuracy %.0f%%, "
     "uses %.2f, which is consistent with the published pattern that the "
     "saving follows model accuracy. SC also behaves as published: accuracy "
     "rises from %.1f%% at k = 1 to %.1f%% at k = %d."
     % (G["correct"], S["mean_completion_tokens_per_sample"], N, 100 / N,
        SC(L)["correct"][0], ESC["samples"][0], SC(1)["correct"][0],
        SC(L)["correct"][0], L)),

    ("Finding 1: no detectable accuracy gain at a matched budget. ",
     "ESC scores %s%% using %.2f samples per question. SC given the same "
     "budget scores %s%% (k = %d) and %s%% (k = %d). The paired difference is "
     "%+.1f ± %.1f points against the floor and %+.1f ± %.1f against the "
     "ceiling; in both cases the spread across runs is larger than the "
     "difference, so neither can be told apart from zero. The paper's claim "
     "of higher accuracy at equal cost (0.2 to 0.9 points on GSM8K, no "
     "variance given) is not something an experiment of this size can "
     "confirm or refute."
     % (pm(ESC["correct"]), ESC["samples"][0], pm(SC(K_LO)["correct"]), K_LO,
        pm(SC(K_HI)["correct"]), K_HI, D_FLOOR[0], D_FLOOR[1], D_CEIL[0],
        D_CEIL[1])),

    ("Finding 2: the saving in samples is modest, and in tokens it is "
     "negative. ",
     "ESC stops early on %.0f%% of question-runs and saves %.0f%% of the "
     "samples of SC-%d, with identical answers (agreement %.0f%%). But each "
     "window is a new request that carries the %d-token prompt again, so ESC "
     "sends %.0f prompt tokens per question against %.0f for SC, and its total "
     "is %.0f tokens against %.0f: %.0f%% more than the method it is meant to "
     "make cheaper. It also needs %.1f sequential rounds where SC needs one. "
     "On this CPU the measured latency follows the sample count (%.0f s "
     "against %.0f s), because local generation is compute-bound; behind a "
     "parallel API the round count would be the latency. Adaptive-Consistency "
     "stops sooner (%.1f samples) at the same accuracy, but as one request per "
     "sample it sends %.0f prompt tokens."
     % (EARLY_SHARE, SAVED, L, S["esc_sc_agreement"][0],
        round(S["prompt_tokens_mean"]), ESC["prompt_tokens"][0],
        SC(L)["prompt_tokens"][0], tot(ESC), tot(SC(L)),
        100 * (tot(ESC) / tot(SC(L)) - 1), ESC["rounds"][0],
        ESC["latency_s"][0], SC(L)["latency_s"][0], AC["samples"][0],
        AC["prompt_tokens"][0])),

    ("Finding 3 (ablation): the stopping signal is real but worth little here. ",
     "With ESC's budgets handed out at random, accuracy is %.1f%%, so the "
     "unanimity signal is worth %+.1f ± %.1f points. %s The signal is "
     "precise, but for this model it fires on fewer than half of the "
     "question-runs. Window size trades cost against accuracy (Figure 4): "
     "w = 2 uses %.1f samples for %s%%, w = 10 uses %.1f for %s%%."
     % (RAND_MEAN, D_RAND[0], D_RAND[1], STOP_SENTENCE,
        A["ESC w=2"]["samples"][0], pm(A["ESC w=2"]["correct"]),
        A["ESC w=10"]["samples"][0], pm(A["ESC w=10"]["correct"]))),

    ("Failure case read from a trace (traces/run_11/q0099.json). ",
     "Mary receives 18 new plants, already has 2 on each of 40 ledges, and "
     "gives away 1 per ledge. Gold answer 58. In run 11 the first five "
     "samples all answer 40, so ESC stops after one window and returns 40; "
     "the same happens in run 33. The trace shows the cause: every reply in "
     "the window computes 2 * 40 = 80 and 80 - 40 = 40 and never uses the 18 "
     "new plants from the first sentence. This is the confident wrong stop of "
     "Gap 4: unanimity measures how consistent the model is, not whether it "
     "is right. Here the stop did no harm, since 18 of the 20 samples say 40 "
     "and SC-20 returns 40 as well, so ESC lost nothing and saved 15 samples. "
     "The opposite pattern is in q1052: 13 of 20 samples repeat the slip "
     "140 - 50 + 100 = 290, the seven dissenters block every window, and ESC "
     "spends the full budget on a question where more samples cannot help. "
     "%d of the %d questions are wrong in every run (results/failure_cases.md)."
     % (S.get("always_wrong", 0), N)),

    ("Checker sensitivity, and what it does to Finding 1. ",
     "%.1f%% of replies omit the \"Final answer\" line. The main table reads "
     "the last number of such a reply; the strict reading counts it as no "
     "answer (results/strict/). Under the strict reading ESC scores %s%% at "
     "%.2f samples and is ahead of matched SC by %+.1f ± %.1f points "
     "(k = %d) and %+.1f ± %.1f (k = %d). Findings 2 and 3 are the same under "
     "both readings; Finding 1 is not. With three runs of %d questions, where "
     "one question is %.0f points, I do not regard a matched-budget gain as "
     "either shown or ruled out: it appears under one scoring rule and "
     "disappears under the other."
     % (STRICT["unparsed_pct"], pm(S_ESC["correct"]), S_ESC["samples"][0],
        SD_FLOOR[0], SD_FLOOR[1], STRICT["k_matched"][0], SD_CEIL[0],
        SD_CEIL[1], S_KHI, N, 100 / N)),
]

LIMITS = [
    "Small n: %d questions, one model, one prompt, one benchmark. Standard "
    "deviations of %.0f to %.0f points mean only large effects are visible; "
    "the conclusion is that no gain was detected, not that none exists."
    % (N, min(ESC["correct"][1], SC(L)["correct"][1]),
       max(SC(W)["correct"][1], ESC["correct"][1])),
    "L = 20, not the paper's 40; a larger budget gives ESC more room to save.",
    "The three runs share one pool per run across methods. This makes the "
    "comparison paired, but SC-k always reads the first k samples.",
    "Latency was measured on a shared laptop and varied with its load; the "
    "round count is the more portable figure. SC-k latency for k not a "
    "multiple of 5 is prorated within a round.",
    "The checker was revised once, after the first traces showed missing "
    "answer lines; both readings are reported. The 40-sample audit sheet "
    "(results/checker_audit.csv) is provided for hand checking.",
]

FOUR_WEEKS = (
    "With four more weeks: (1) the full 1,319 questions and L = 40 on a GPU, "
    "to reach the paper's resolution of under one point; (2) a second, "
    "stronger open-weight model (Qwen2.5-7B) to trace the saving against "
    "model accuracy; (3) a real latency study against a hosted API with "
    "parallel sampling; (4) a token-aware ESC that keeps the prompt cached "
    "across windows, which would remove the overhead found in Finding 2.")

AI_LINE = ("An AI assistant (Claude) was used to write and debug the code and "
           "to draft this report; the numbers come from the traces in this "
           "submission.")


# --- document helpers ------------------------------------------------------

def run(par, text, bold=False, italic=False, size=None, color=None):
    r = par.add_run(text)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    if color:
        r.font.color.rgb = RGBColor(*color)
    return r


def para(doc, space_after=3, align=None):
    p = doc.add_paragraph()
    f = p.paragraph_format
    f.space_after, f.space_before, f.line_spacing = Pt(space_after), Pt(0), 1.0
    if align:
        p.alignment = align
    return p


def heading(doc, text):
    p = para(doc, space_after=2)
    p.paragraph_format.space_before = Pt(4)
    run(p, text, bold=True, size=10.5, color=(0x1c, 0x5c, 0xab))


def shade(cell, hex_color):
    tc = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc.append(shd)


def add_table(doc, rows, widths, size=8, header=True, bold_rows=()):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.width = Cm(widths[c])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if header and c > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, str(val), bold=(header and r == 0) or r in bold_rows
                or (not header and c == 0), size=size)
            if header and r == 0:
                shade(cell, "DCE8F7")
            elif r in bold_rows:
                shade(cell, "FDE9DF")
    return t


def picture_row(doc, files, widths):
    p = para(doc, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER)
    for name, w in zip(files, widths):
        p.add_run().add_picture(os.path.join(ROOT, "figures", name), width=Cm(w))


def caption(doc, text):
    p = para(doc, space_after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    run(p, text, italic=True, size=8)


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.6)
    sec.top_margin = sec.bottom_margin = Cm(1.3)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(9.5)
    J = WD_ALIGN_PARAGRAPH.JUSTIFY

    p = para(doc, space_after=0)
    run(p, "AI465 Agentic AI, Research Project Phase 2   |   Roll No. %s" % ROLL,
        size=9, color=(0x52, 0x51, 0x4e))
    p = para(doc, space_after=3)
    run(p, "Early-Stopping Self-Consistency at a matched budget on a small "
        "open-weight model", bold=True, size=13)

    heading(doc, "1. Objective")
    run(para(doc, align=J), OBJECTIVE, italic=True)
    run(para(doc, align=J), DEVIATION)

    heading(doc, "2. What was implemented")
    for text in IMPLEMENTED:
        lead, rest = text.split(". ", 1)
        p = para(doc, space_after=2, align=J)
        run(p, lead + ". ", bold=True)
        run(p, rest)

    heading(doc, "3. Experimental setup (pinned configuration)")
    add_table(doc, SETUP_ROWS, [2.4, 15.2], size=8.5, header=False)

    heading(doc, "4. Results")
    rows = table_rows()
    esc_row = next(i for i, r in enumerate(rows) if r[0].startswith("ESC"))
    add_table(doc, rows, [4.3, 2.3, 1.6, 1.5, 1.9, 1.9, 1.8, 2.3], size=8,
              bold_rows=(esc_row,))
    caption(doc, "Table 1. Mean ± standard deviation over 3 runs of %d "
            "questions; costs are per question. Prompt tokens: one prompt per "
            "round. Regenerate with python src/evaluate.py." % N)
    picture_row(doc, ["fig1_accuracy_vs_cost.png", "fig2_stopping.png"],
                [9.6, 7.9])
    caption(doc, "Figure 1 (left). Accuracy against samples per question. "
            "Figure 2 (right). Where ESC stops and how often the stop is correct.")
    picture_row(doc, ["fig3_cost.png"], [17.0])
    caption(doc, "Figure 3. Cost per question of the matched and full SC "
            "baselines, ESC and Adaptive-Consistency.")

    heading(doc, "5. Analysis")
    for lead, body in ANALYSIS:
        p = para(doc, align=J)
        run(p, lead, bold=True)
        run(p, body)
    picture_row(doc, ["fig4_window_ablation.png"], [11.0])
    caption(doc, "Figure 4. Window-size ablation.")

    heading(doc, "6. Limitations, and what four more weeks would add")
    for text in LIMITS:
        p = para(doc, space_after=1, align=J)
        p.paragraph_format.left_indent = Cm(0.4)
        run(p, "- " + text)
    run(para(doc, align=J), FOUR_WEEKS)
    run(para(doc, space_after=0), AI_LINE, italic=True, size=8.5,
        color=(0x52, 0x51, 0x4e))

    doc.save(DOCX)
    return DOCX


def to_pdf(docx_path, pdf_path):
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        d = word.Documents.Open(docx_path, ReadOnly=True)
        d.ExportAsFixedFormat(pdf_path, 17)   # 17 = wdExportFormatPDF
        d.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    to_pdf(build(), PDF)
    import fitz
    print("wrote", PDF, "pages:", len(fitz.open(PDF)))
