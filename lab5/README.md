# Lab 5: Chain-of-Thought (CoT) and Self-Consistency

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements advanced prompt engineering and stochastic sampling techniques based on the seminal paper by Wang et al. (ICLR 2023), *"Self-Consistency Improves Chain of Thought Reasoning in Language Models"*:
1. **Chain-of-Thought Prompting**: Few-shot demonstrations that encourage explicit intermediate step-by-step reasoning before producing a final answer.
2. **Stochastic Sampling**: Non-zero temperature decoding ($T \in [0.5, 0.9]$) generating a diverse ensemble of $k$ distinct reasoning trajectories for each question.
3. **Majority Voting (Self-Consistency)**: Parsing final numeric answers from reasoning paths and selecting the modal answer $\arg\max_a \sum_{i=1}^k \mathbb{I}(a_i = a)$.
4. **Sample Complexity Analysis**: Evaluating how accuracy and voting margins scale with ensemble size $k \in \{1, 3, 5, 10, 20\}$.

---

## Directory Contents

| File | Description |
|---|---|
| `questions.py` | Benchmark set of multi-step arithmetic word problems with ground-truth answers. |
| `exp5_cot_selfconsistency.py` | CoT sampler and self-consistency majority voting implementation. |
| `exp5_exercises.py` | Sensitivity analysis across temperatures ($T=0.2, 0.7, 1.2$) and sample sizes. |
| `make_plots.py` | Generates accuracy scaling curves and consensus distribution plots. |
| `make_report.py` | Compiles the formatted report with figures into `LAB_5_U23AI042.doc`. |
| `LAB_5_U23AI042.doc` | Final laboratory report deliverable. |
| `outputs/` | Contains sampled reasoning paths, vote tallies, and text output logs. |

---

## How to Run

```bash
# Run CoT and self-consistency simulations
python exp5_cot_selfconsistency.py
python exp5_exercises.py

# Generate plots and compile report
python make_plots.py
python make_report.py
```
