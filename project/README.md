# AI465 Research Project: Early-Stopping Self-Consistency on Open-Weight LLMs

**Course:** Agentic AI (IA462)  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)  
**Topic:** Evaluating Early-Stopping Self-Consistency (ESC) on Low-Resource Open-Weight Language Models  

---

## 1. Project Background & Motivation

While Large Language Models (LLMs) demonstrate remarkable multi-step reasoning capabilities with **Chain-of-Thought (CoT)** prompting, standard greedy decoding often errs on complex arithmetic questions. **Self-Consistency (SC)** (Wang et al., ICLR 2023) resolves this by sampling $N$ independent reasoning paths at non-zero temperature and selecting the modal answer via majority voting. However, fixed-budget SC multiplies compute, latency, and monetary cost by $N \times$ for *every* question regardless of difficulty.

**Early-Stopping Self-Consistency (ESC)** (Li et al., ICLR 2024) addresses this inefficiency by sampling in sequential windows of size $w$. If all $w$ reasoning paths in a window agree on the identical parsed answer, the generation halts immediately and returns that consensus answer; otherwise, sampling continues up to a maximum budget $L$.

### The Research Question
Li et al. validated ESC primarily on large-scale proprietary or dense models (e.g., ChatGPT, Claude, LLaMA-65B) where base accuracy is high ($\ge 80\%$) and consensus is almost always genuine. **This research project replicates and critically evaluates ESC on edge-deployable, low-resource, quantized open-weight models**—specifically `Qwen2.5-1.5B-Instruct` (Q4_K_M 4-bit quantization, 1.1 GB footprint) running entirely locally on CPU without external API dependencies.

---

## 2. Project Organization

The research project was executed and delivered in two formal phases:

```
project/
├── AI465_Research_Project_Phase1.pdf   # Phase 1 project handout and rubric
├── AI465_Research_Project_Phase2.pdf   # Phase 2 project guidelines
├── papers/                             # Core scientific literature
│   ├── 2203.11171v4.pdf                # Wang et al., 2023 (Self-Consistency)
│   ├── 2305.11860v2.pdf                # Aggarwal et al., 2023 (Adaptive Consistency)
│   └── 2401.10480v1.pdf                # Li et al., 2024 (Early-Stopping Self-Consistency)
├── phase1/                             # Phase 1: Survey, Formulation & Proposal
│   ├── RP1_U23AI042.docx / .pdf        # Formal research proposal paper
│   ├── RP1_U23AI042_slides.pptx / .pdf # Presentation slide deck
│   ├── build_slides.py                 # Automated slide generator
│   ├── build_summary.py                # Proposal summary generator
│   └── figures/                        # Architectural and algorithmic schematics
└── phase2/                             # Phase 2: Experimental Framework & Results
    ├── README.md                       # Comprehensive phase 2 technical documentation
    ├── config.json                     # Pinned experiment configuration
    ├── data/                           # GSM8K benchmark test set & fixed 50-question subset
    ├── src/                            # Modular engine (llm, gsm8k, methods, sample, evaluate, plots)
    ├── traces/                         # 3,000+ raw inference traces across 3 seeded runs
    ├── results/                        # Summary metrics, Table 1, failure cases, checker audits
    ├── figures/                        # High-resolution publication figures (Fig 1 to 4)
    ├── report/                         # Full report (.docx, .pdf) and slide deck (.pptx, .pdf)
    ├── demo_output.txt                 # Working trace demonstrations across 5 diagnostic scenarios
    └── build_all.py                    # End-to-end evaluation, plotting, and report build pipeline
```

---

## 3. Summary of Findings (Phase 2)

Tested on a stratified 50-question subset of **GSM8K** across 3 seeded runs (150 evaluations per configuration, totaling 3,000 sampled trajectories plus greedy baselines):

| Method | Accuracy | Mean Samples / Question | Mean Tokens / Question | Sequential Rounds | Latency / Question |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Greedy ($T=0$)** | $48.00\% \pm 0.00\%$ | $1.00 \pm 0.00$ | $239.3 \pm 0.0$ | $1.0 \pm 0.0$ | $1.25\text{s}$ |
| **Fixed SC ($k=5$)** | $59.33\% \pm 1.89\%$ | $5.00 \pm 0.00$ | $1,192.8 \pm 14.2$ | $1.0 \pm 0.0$ | $6.21\text{s}$ |
| **Fixed SC ($k=10$)** | $60.67\% \pm 2.49\%$ | $10.00 \pm 0.00$ | $2,385.1 \pm 28.5$ | $1.0 \pm 0.0$ | $12.44\text{s}$ |
| **Fixed SC ($k=20$)** | $\mathbf{62.67\%} \pm 1.89\%$ | $20.00 \pm 0.00$ | $4,770.2 \pm 57.0$ | $1.0 \pm 0.0$ | $24.87\text{s}$ |
| **Adaptive Consistency** | $61.33\% \pm 1.89\%$ | $8.45 \pm 0.25$ | $2,015.4 \pm 62.1$ | $2.3 \pm 0.1$ | $10.51\text{s}$ |
| **ESC ($w=5, L=20$)** | $\mathbf{62.00\%} \pm 1.63\%$ | $\mathbf{6.90} \pm 0.16$ | $\mathbf{1,645.7} \pm 38.8$ | $\mathbf{1.4} \pm 0.0$ | $\mathbf{8.58\text{s}}$ |

### Key Takeaways:
1. **Dramatic Efficiency Gains**: ESC achieves **$62.00\%$ accuracy**—statistically indistinguishable from the exhaustive 20-sample SC baseline ($62.67\%$)—while requiring only **$6.90$ samples** on average. This delivers a **$65.5\%$ reduction in sample calls**, a **$62.7\%$ savings in total token consumption**, and a **$2.7\times$ speedup** in wall-clock latency.
2. **Early Stopping Rate**: Over $70\%$ of questions trigger early stopping within Window 1 ($n=5$), demonstrating that clear reasoning problems do not benefit from surplus sampling.
3. **The Low-Parameter Hazard (False Consensus)**: Unlike in large LLMs, 1.5B models can suffer from *shared systematic failure modes*. In question GSM8K-99, the model repeatedly committed the identical arithmetic misinterpretation across all 5 initial trajectories, halting early with unanimous false consensus on the wrong answer. This underscores the need for semantic or confidence verification when deploying ESC on small models.

---

## 4. Quickstart: Reproducing Phase 2

All traces and outputs are cached in the repository, enabling instantaneous reproduction of all tables and figures without running the model:

```bash
cd project/phase2

# Step 1: Re-evaluate traces and regenerate results tables
python src/evaluate.py

# Step 2: Regenerate publication figures
python src/plots.py

# Step 3: Run live demo on a question
python demo.py --task 6

# Or run the complete automated build suite
python build_all.py
```
