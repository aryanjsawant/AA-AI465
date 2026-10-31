"""
Builds the Phase 1 written summary (two pages) as .docx and exports it to PDF
through Word.

    python build_summary.py
"""

import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROLL = "U23AI042"
DOCX = os.path.join(HERE, "RP1_%s.docx" % ROLL)
PDF = os.path.join(HERE, "RP1_%s.pdf" % ROLL)

TITLE = ("Early-Stopping Self-Consistency: is the saving still a gain at a "
         "matched budget on a small open-weight model?")

PAPERS = [
    ("[1] Primary. ", "Y. Li, P. Yuan, S. Feng, B. Pan, X. Wang, B. Sun, H. Wang, "
     "K. Li. Escape Sky-high Cost: Early-stopping Self-Consistency for "
     "Multi-step Reasoning. ICLR 2024. arXiv:2401.10480. Code: "
     "github.com/Yiwei98/ESC."),
    ("[2] Context. ", "X. Wang, J. Wei, D. Schuurmans, Q. V. Le, E. H. Chi, "
     "S. Narang, A. Chowdhery, D. Zhou. Self-Consistency Improves Chain of "
     "Thought Reasoning in Language Models. ICLR 2023."),
    ("[3] Context. ", "P. Aggarwal, A. Madaan, Y. Yang, Mausam. Let's Sample "
     "Step by Step: Adaptive-Consistency for Efficient Reasoning and Coding "
     "with LLMs. EMNLP 2023. arXiv:2305.11860."),
]

METHOD = [
    "Self-consistency (SC) [2] answers a reasoning question by sampling many "
    "chain-of-thought solutions at a non-zero temperature and returning the "
    "most frequent final answer. It beats a single greedy answer, but the cost "
    "grows in proportion to the number of samples, and that number is fixed in "
    "advance for every question, easy or hard. The authors put the price of "
    "SC with 64 samples over the MATH benchmark on GPT-4 at about 2,000 dollars.",

    "ESC starts from the point that SC needs only the most frequent answer, "
    "not the whole answer distribution. It cuts the budget of L samples into "
    "consecutive windows of w samples and, after each window, checks one "
    "condition: are all w answers identical? If they are, sampling stops and "
    "that answer is returned. If not, the window is kept and the next one is "
    "drawn; when no window is ever unanimous, all L samples are voted on "
    "exactly as in SC (Algorithm 1). The rule has no threshold to tune, which "
    "is the authors' argument against Adaptive-Consistency [3], where a Beta "
    "posterior is checked against a 0.95 confidence threshold after every "
    "single sample. Two additions support the rule: a z-test argument that an "
    "early stop rarely disagrees with full SC (Sec. 2.3), and a control scheme "
    "that predicts cost and accuracy for a choice of (w, L) from the first "
    "window alone (Sec. 2.4).",

    "The evaluation covers six benchmarks (MATH, GSM8K, CommonsenseQA, "
    "StrategyQA, Last Letters, Coin Flip) on GPT-4, GPT-3.5-Turbo and Llama-2 "
    "7b, with the few-shot prompts of Wei et al., temperature 0.7, w = 5 and "
    "L = 40 (0.5, 8 and 64 for MATH). The headline result is on GSM8K with "
    "GPT-4: ESC reaches the same 89.29% as SC with 40 samples while drawing "
    "7.98 samples per question on average (Table 1).",
]

GAPS = [
    ("Gap 1 (evaluation): the matched-budget gain is smaller than the noise "
     "nobody reported. ",
     "Table 1 has a row for SC given the same average number of samples as "
     "ESC. On GSM8K, ESC is ahead of it by 0.22 points (GPT-4), 0.85 "
     "(GPT-3.5-Turbo) and 0.22 (Llama-2 7b). Sec. 3.2 states that results are "
     "averaged over 10 runs and that the variance is omitted for space. On "
     "1,319 questions, 0.22 points is three questions. Without a standard "
     "deviation the claim that ESC gets higher accuracy at the same cost "
     "cannot be told apart from sampling noise, and this is the claim that "
     "matters, since saving samples against SC-40 is trivially possible by "
     "running SC-8."),
    ("Gap 2 (cost and latency): cost is counted in samples and dollars, never "
     "in time. ",
     "Table 1 counts samples and Table 7 counts tokens and dollars for the two "
     "API models; no wall-clock figure appears anywhere. This hides a real "
     "price of the method: SC can ask for all L samples in one parallel "
     "request, while Algorithm 1 must wait for each window before deciding on "
     "the next, up to L/w = 8 sequential requests. For Llama-2 7b on GSM8K, "
     "ESC still draws 31.21 of 40 samples, so it saves 22% of the samples but "
     "needs about six round trips where SC needs one."),
    ("Gap 3 (generality): the saving depends on model strength, and the "
     "open-weight evidence is one model that mostly fails. ",
     "On GSM8K the samples saved fall from 80% (GPT-4) to 63% (GPT-3.5) to "
     "22% (Llama-2 7b); on MATH, Llama-2 uses 62.48 of 64 (Table 1). The "
     "paper notes the correlation itself (Sec. 3.2). Llama-2 7b scores 21.75% "
     "on GSM8K, so there is no data point for a model of middling accuracy, "
     "none for a model small enough to run on a laptop, and the zero-shot "
     "check is on GPT-3.5 only (Fig. 4). The 2025 follow-up from the same "
     "group (DSC, Findings of NAACL) adds Mistral-7B, and as far as I can find "
     "reports neither variance nor latency."),
    ("Gap 4 (assumption): the guarantee is about agreeing with SC, not about "
     "being right, and it is quoted for a window the experiments mostly do "
     "not use. ",
     "Sec. 2.3 derives z >= sqrt(w) for an early stop on a non-modal answer "
     "and quotes a probability of at most 0.002 for w = 8. Five of the six "
     "benchmarks use w = 5 (Sec. 3.2), where the same formula gives about "
     "0.013, six times weaker. Table 5 reports only the overlap between ESC "
     "and SC answers. When the model's most likely answer is itself wrong, a "
     "unanimous window stops sampling on that wrong answer, and the paper "
     "gives no figure for how often a stop is correct."),
]

OBJECTIVE = (
    "To evaluate early-stopping self-consistency (window 5, at most 20 "
    "samples) for arithmetic word problems on a fixed random subset of 50 "
    "questions from the GSM8K test set (1,319 questions), using the "
    "open-weight Qwen2.5-1.5B-Instruct model run locally, compared against "
    "fixed-size self-consistency at a matched sample budget, measured by "
    "exact-match accuracy and by samples, tokens, sequential rounds and "
    "wall-clock latency per question, each reported as mean and standard "
    "deviation over three seeded runs.")

TRACE = (
    "The objective comes from Gap 1: it repeats the paper's own matched-budget "
    "comparison with the variance attached. Running it on a 1.5B model places "
    "the test in the regime Gap 3 says is missing, and the latency and "
    "stop-correctness figures needed for Gaps 2 and 4 fall out of the same "
    "traces at no extra cost. The control scheme of Sec. 2.4 is out of scope.")

BUDGET = (
    "Budget: 20 samples x 50 questions x 3 runs = 3,000 sampled generations, "
    "plus 50 greedy calls. At roughly 100 completion tokens each this is about "
    "0.3M completion tokens and 0.25M prompt tokens (a 410-token prompt sent "
    "once per window). The model is a 1.1 GB quantised file served by "
    "llama.cpp on a laptop CPU at about 25 tokens per second, so the full "
    "experiment takes three to four hours and costs nothing. Every other "
    "method (SC at any k, Adaptive-Consistency, ablations) is computed from "
    "the same stored samples, so the comparison is paired and adds no calls.")

AI_LINE = (
    "Use of language models: an AI assistant (Claude) was used to find and "
    "summarise the papers and to help draft this summary; every figure quoted "
    "above was checked against the papers.")


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
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if align:
        p.alignment = align
    return p


def heading(doc, text):
    p = para(doc, space_after=2)
    p.paragraph_format.space_before = Pt(5)
    run(p, text, bold=True, size=10.5, color=(0x1c, 0x5c, 0xab))


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.7)
    sec.top_margin = sec.bottom_margin = Cm(1.4)
    style = doc.styles["Normal"]
    style.font.name, style.font.size = "Calibri", Pt(9.5)

    p = para(doc, space_after=0)
    run(p, "AI465 Agentic AI, Research Project Phase 1", size=9,
        color=(0x52, 0x51, 0x4e))
    p = para(doc, space_after=1)
    run(p, TITLE, bold=True, size=13)
    p = para(doc, space_after=4)
    run(p, "Roll No. %s   |   Syllabus unit: LLMs as reasoning engines "
        "(chain-of-thought and self-consistency)" % ROLL, size=9,
        color=(0x52, 0x51, 0x4e))

    heading(doc, "1. Papers read")
    for tag, cite in PAPERS:
        p = para(doc, space_after=1)
        run(p, tag, bold=True)
        run(p, cite)

    heading(doc, "2. The primary paper: problem and method")
    for text in METHOD:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(p, text)
    p = para(doc, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.add_run().add_picture(os.path.join(HERE, "figures", "fig_esc_windows.png"),
                            width=Cm(12.5))
    p = para(doc, space_after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    run(p, "Figure 1. SC and ESC on one question, with the example answers of "
        "Figure 1 in [1]. Drawn by me.", italic=True, size=8.5)

    heading(doc, "3. Research gaps")
    for lead, body in GAPS:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(p, lead, bold=True)
        run(p, body)
    p = para(doc, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.add_run().add_picture(os.path.join(HERE, "figures", "fig_paper_table1.png"),
                            width=Cm(13.0))
    p = para(doc, space_after=3, align=WD_ALIGN_PARAGRAPH.CENTER)
    run(p, "Figure 2. GSM8K numbers from Table 1 of [1], plotted by me: "
        "evidence for Gaps 3 (left) and 1 (right).", italic=True, size=8.5)

    heading(doc, "4. Objective")
    p = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    run(p, OBJECTIVE, bold=True)
    for text in (TRACE, BUDGET):
        p = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(p, text)
    p = para(doc, space_after=0)
    run(p, AI_LINE, italic=True, size=8.5, color=(0x52, 0x51, 0x4e))

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
