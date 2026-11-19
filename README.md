# Agentic AI & Soft Computing (AA-AI465)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Institution](https://img.shields.io/badge/SVNIT-Surat-orange.svg)](https://www.svnit.ac.in/)
[![Course](https://img.shields.io/badge/Course-Agentic%20AI%20%7C%20Soft%20Computing-green.svg)]()
[![Student Roll](https://img.shields.io/badge/Roll%20No-U23AI042-purple.svg)]()

This repository contains the complete coursework, laboratory assignments, and Capstone Research Project for **Agentic AI (IA462)** and **Soft Computing (IA305)** in the **Department of Artificial Intelligence** at **Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat**.

**Author:** Aryan Sawant  
**Roll No:** `U23AI042`  
**Degree:** B.Tech. in Artificial Intelligence  

---

## Table of Contents
- [Curriculum Overview](#curriculum-overview)
- [Laboratory Experiments (Labs 1–9)](#laboratory-experiments-labs-19)
  - [Lab 1: Reflex and Model-Based Agents](#lab-1-reflex-and-model-based-agents)
  - [Lab 2: Deliberative Search-Based Agents](#lab-2-deliberative-search-based-agents)
  - [Lab 3: Tool-Using Agent with External Computation](#lab-3-tool-using-agent-with-external-computation)
  - [Lab 4: Retrieval-Augmented Generation (RAG) Agent](#lab-4-retrieval-augmented-generation-rag-agent)
  - [Lab 5: Chain-of-Thought (CoT) and Self-Consistency](#lab-5-chain-of-thought-cot-and-self-consistency)
  - [Lab 6: Multi-Agent Collaboration and Role-Based Systems](#lab-6-multi-agent-collaboration-and-role-based-systems)
  - [Lab 7: Markov Decision Processes (MDP) & GridWorld](#lab-7-markov-decision-processes-mdp--gridworld)
  - [Lab 8: Game-Theoretic Interaction & Repeated Play](#lab-8-game-theoretic-interaction--repeated-play)
  - [Lab 9: Multi-Layer Perceptron (MLP) & Backpropagation](#lab-9-multi-layer-perceptron-mlp--backpropagation)
- [Research Project: Early-Stopping Self-Consistency on Open-Weight LLMs](#research-project-early-stopping-self-consistency-on-open-weight-llms)
  - [Phase 1: Survey and Research Proposal](#phase-1-survey-and-research-proposal)
  - [Phase 2: Empirical Replication and Evaluation](#phase-2-empirical-replication-and-evaluation)
  - [Key Results & Efficiency vs Accuracy Frontier](#key-results--efficiency-vs-accuracy-frontier)
  - [Working Output Scenarios & Failure Taxonomy](#working-output-scenarios--failure-taxonomy)
- [Repository Structure](#repository-structure)
- [Setup & Reproducibility Guide](#setup--reproducibility-guide)

---

## Curriculum Overview

The repository covers the spectrum of modern agent architectures—from classical rational agents, deliberative search, and dynamic programming to LLM reasoning loops, tool-augmented systems, multi-agent debate protocols, and neural function approximators:

```
[Classical Agency]          [Language Model Reasoning]          [Learning & Control]
  • Reflex Agents             • Tool Use & API Dispatch           • MDPs (VI / PI / Q-Learning)
  • BFS / UCS Search          • RAG & Grounded Retrieval          • Repeated Game Theory
  • Dynamic Replanning        • CoT & Self-Consistency            • MLPs & Backpropagation
  • Hybrid Architectures      • Multi-Agent Collaboration         • Early-Stopping Inference
```

---

## Laboratory Experiments (Labs 1–9)

| Lab | Title / Topic | Core Concepts & Algorithms | Key Deliverables |
|:---:|:---|:---|:---|
| **[Lab 1](Lab1/)** | Reflex & Model-Based Agents | Simple reflex, internal world state tracking, $N$-room corridor, stochastic dirt arrival | `LAB_1_U23AI042.doc`, simulation scripts, plots |
| **[Lab 2](lab2/)** | Deliberative Search Agents | Breadth-First Search (BFS), Uniform Cost Search (UCS), dynamic obstacle replanning, hybrid reflex-search | `LAB_2_U23AI042.doc`, search scripts, animation |
| **[Lab 3](lab3/)** | Tool-Using Agent | Deterministic tool dispatcher, arithmetic engine, CSV weather analyzer, boundary limits & recursion guards | `LAB_3_U23AI042.doc`, tool agent runner, logs |
| **[Lab 4](lab4/)** | RAG Pipeline Agent | Document chunking, TF-IDF vector embeddings, cosine similarity ranking, citation provenance | `LAB_4_U23AI042.doc`, RAG pipeline code, docstore |
| **[Lab 5](lab5/)** | CoT & Self-Consistency | Few-shot reasoning prompts, temperature sampling ensembles, majority voting consensus | `LAB_5_U23AI042.doc`, CoT sampler, scaling curves |
| **[Lab 6](lab6/)** | Multi-Agent Collaboration | Role specialization (Planner, Researcher, Synthesizer, Critic), iterative debate and refinement cycles | `LAB_6_U23AI042.doc`, orchestrator, interaction graphs |
| **[Lab 7](lab7/)** | Markov Decision Processes | $4 \times 3$ GridWorld, Bellman equations, Value Iteration, Policy Iteration, Q-Learning, reward sweep | `LAB_7_U23AI042.ipynb`, `LAB_7_U23AI042.doc`, 4 figures |
| **[Lab 8](lab8/)** | Game Theory & Equilibria | Iterated Prisoner's Dilemma, Axelrod tournament, 8 repeated strategies, noise sweep, Folk Theorem | `LAB_8_U23AI042.ipynb`, tournament heatmap, payoff sweeps |
| **[Lab 9](lab9/)** | MLP & Backpropagation | 2-2-1 MLP from scratch, XOR resolution, symmetry breaking (zero vs random init), Sigmoid vs Tanh | `LAB_9_U23AI042.ipynb`, `LAB_9_U23AI042.doc`, 3 figures |

---

### Lab 1: Reflex and Model-Based Agents
- **Objective:** Evaluate how agent memory impacts performance across fully and partially observable environments.
- **Formulation:** Evaluates 2-room vacuum world, generalized $N$-cell 1D corridors, and Bernoulli dirt arrival ($p_{\text{dirt}} \in [0.1, 0.5]$).
- **Key Insight:** Simple reflex agents cycle indefinitely when all visible percepts are clean; model-based agents track visited states to terminate gracefully, saving energy.
- **Folder:** [`Lab1/`](Lab1/)

### Lab 2: Deliberative Search-Based Agents
- **Objective:** Implement goal-based deliberation over spatial grids with variable movement costs and runtime obstacles.
- **Formulation:** Compares unweighted BFS against priority-queue driven UCS across terrain matrices (mud $c=5$, gravel $c=2$, open floor $c=1$).
- **Key Insight:** Dynamic replanning detects blocked paths mid-trajectory and recalculates optimal routes online from the agent's current position without restarting.
- **Folder:** [`lab2/`](lab2/)

### Lab 3: Tool-Using Agent with External Computation
- **Objective:** Bridge language model limitations in arithmetic and real-time data access by integrating deterministic computational tools.
- **Formulation:** Implements structured tool schemas, regex/JSON dispatchers, parameter validation, and recursion depth limits.
- **Key Insight:** Decoupling reasoning from computation eliminates arithmetic hallucinations while maintaining execution safety.
- **Folder:** [`lab3/`](lab3/)

### Lab 4: Retrieval-Augmented Generation (RAG) Agent
- **Objective:** Ground factual agent responses in local technical documents to prevent hallucination.
- **Formulation:** Implements sliding-window chunking with token overlap, TF-IDF term-frequency matrices, cosine similarity ranking, and strict citation tracking.
- **Key Insight:** Strict provenance checks ensure the agent cites exact document coordinates and rejects out-of-domain queries when similarity scores fall below threshold $\theta$.
- **Folder:** [`lab4/`](lab4/)

### Lab 5: Chain-of-Thought (CoT) and Self-Consistency
- **Objective:** Study reasoning performance scaling as a function of sampling diversity and ensemble size (Wang et al., ICLR 2023).
- **Formulation:** Generates $k \in \{1, 3, 5, 10, 20\}$ stochastic reasoning paths at temperature $T=0.7$ and extracts numeric answers for majority voting: $\arg\max_a \sum_{i=1}^k \mathbb{I}(a_i = a)$.
- **Key Insight:** Majority voting filters out idiosyncratic reasoning errors, yielding steep accuracy gains from $k=1$ to $k=5$ with diminishing marginal returns thereafter.
- **Folder:** [`lab5/`](lab5/)

### Lab 6: Multi-Agent Collaboration and Role-Based Systems
- **Objective:** Design distributed multi-agent systems with specialized persona roles and feedback loops.
- **Formulation:** Implements four distinct agent roles: **Planner** (DAG task breakdown), **Researcher** (knowledge retrieval), **Synthesizer** (solution drafting), and **Critic** (rubric-based evaluation and revision requests).
- **Key Insight:** Iterative debate cycles consistently enhance answer rigor and factual coverage at the expense of higher token and latency overheads.
- **Folder:** [`lab6/`](lab6/)

### Lab 7: Markov Decision Processes (MDP) & GridWorld
- **Objective:** Formulate agent decision-making under uncertainty as an MDP and compare exact dynamic programming against model-free reinforcement learning.
- **Formulation:** $4 \times 3$ grid with obstacle $(1,1)$, terminals $+1.0$ at $(3,2)$ and $-1.0$ at $(3,1)$, slip probability $p=0.1$, step reward $R_{\text{step}}=-0.04$, and discount $\gamma=0.95$.
- **Key Results:**
  - **Value Iteration**: Converges in 21 iterations ($\Delta < 10^{-4}$), performing 1,692 state backups.
  - **Policy Iteration**: Converges in just 4 iterations, performing 324 state backups (achieving identical optimal policy with $\sim 80\%$ fewer backups).
  - **Step Reward Sweep**: Identifies 4 behavioral regimes: extreme negative $R_{\text{step}} = -2.0$ causes intentional suicide; mild negative $R_{\text{step}} = -0.04$ takes conservative detours; positive $R_{\text{step}} = +0.01$ avoids goals to harvest infinite reward.
  - **Q-Learning**: Model-free control achieves optimal action agreement in $100\%$ of non-terminal states after 5,000 episodes.
- **Folder:** [`lab7/`](lab7/)

### Lab 8: Game-Theoretic Interaction & Repeated Play
- **Objective:** Investigate strategic equilibria, evolutionary cooperation, and the Folk Theorem in multi-agent environments.
- **Formulation:** Iterated Prisoner's Dilemma ($T=5, R=3, P=1, S=0$) across 8 strategies: `AllC`, `AllD`, `TFT`, `Grim Trigger`, `Pavlov`, `Random`, `TF2T`, `STFT`.
- **Key Results:**
  - **Tournament Winner**: Tit-for-Tat (TFT) achieves the highest aggregate score ($18.86$ pts/game), proving the power of being nice, retaliatory, and forgiving.
  - **Noise Sensitivity**: Under execution noise $\epsilon \in [0.0, 0.25]$, brittle retaliatory strategies like Grim Trigger collapse rapidly into permanent mutual defection, whereas forgiving strategies (TF2T, Pavlov) preserve cooperation.
  - **Continuation Probability**: Validates the Folk Theorem boundary $\delta \ge \frac{T-R}{T-P} = 0.5$ required to sustain cooperative equilibria.
- **Folder:** [`lab8/`](lab8/)

### Lab 9: Multi-Layer Perceptron (MLP) & Backpropagation
- **Objective:** Build a 2-2-1 feedforward neural network from scratch in NumPy, derive backpropagation gradients, and solve the XOR problem.
- **Formulation:** MSE loss $E = \frac{1}{2N}\sum(\hat{y}-y)^2$, Sigmoid output activation, Sigmoid vs Tanh hidden activations, learning rate $\eta \in [0.05, 2.0]$.
- **Key Results:**
  - **Symmetry Breaking**: Initializing weights to zero fails completely (MSE stuck at $\approx 0.125$) because hidden neurons compute identical activations and gradients, collapsing the network into a 1-neuron model.
  - **Tanh vs Sigmoid**: Tanh hidden activations produce zero-centered outputs and $4\times$ larger gradients near origin ($\tanh'(0)=1.0$ vs $\sigma'(0)=0.25$), accelerating convergence by $\sim 40\%$.
  - **Capacity**: $h=2$ is the theoretical minimum to represent XOR (forming two intersecting hyperplanes), but $h \ge 4$ eliminates local minima and ensures $100\%$ convergence.
- **Folder:** [`lab9/`](lab9/)

---

## Research Project: Early-Stopping Self-Consistency on Open-Weight LLMs

**Title:** *Evaluating Early-Stopping Self-Consistency (ESC) on Low-Resource Open-Weight Language Models*  
**Primary Literature:**
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models*, ICLR 2023 ([arXiv:2203.11171](https://arxiv.org/abs/2203.11171))
- Aggarwal et al., *Let's Sample Step by Step: Adaptive-Consistency for Efficient Reasoning with LLMs*, EMNLP 2023 ([arXiv:2305.11860](https://arxiv.org/abs/2305.11860))
- Li et al., *Escape Sky-high Cost: Early-stopping Self-Consistency for Multi-step Reasoning*, ICLR 2024 ([arXiv:2401.10480](https://arxiv.org/abs/2401.10480))

---

### Phase 1: Survey and Research Proposal
- Comprehensive literature review analyzing sampling cost, token consumption, and latency bottlenecks in multi-path LLM reasoning.
- Formulated research proposal to evaluate whether ESC's consensus assumptions hold on low-parameter open-weight models where generation noise is significantly higher than in commercial LLMs (GPT-3.5/GPT-4).
- **Deliverables:** Formal proposal report ([`RP1_U23AI042.docx`](project/phase1/RP1_U23AI042.docx), [`pdf`](project/phase1/RP1_U23AI042.pdf)) and slide deck ([`RP1_U23AI042_slides.pptx`](project/phase1/RP1_U23AI042_slides.pptx), [`pdf`](project/phase1/RP1_U23AI042_slides.pdf)).

---

### Phase 2: Empirical Replication and Evaluation
- **Model:** `Qwen2.5-1.5B-Instruct` (Q4_K_M 4-bit quantized GGUF, 1.1 GB memory footprint).
- **Engine:** `llama.cpp` server (b11429), CPU x64 execution without GPU or cloud API keys.
- **Benchmark:** Stratified 50-question subset of **GSM8K** test set across 3 seeded runs (seeds 11, 22, 33), producing **3,000+ cached reasoning traces**.
- **Stopping Rule:** Window size $w = 5$, maximum sample budget $L = 20$. If all samples within a window agree unanimously, stop early; otherwise draw subsequent windows.

---

### Key Results & Efficiency vs Accuracy Frontier

| Method | Accuracy | Mean Samples | Mean Tokens | Sequential Rounds | Latency / Question | Cost vs SC-20 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Greedy ($T=0$)** | $48.00\% \pm 0.00\%$ | $1.00 \pm 0.00$ | $239.3 \pm 0.0$ | $1.0 \pm 0.0$ | $1.25\text{s}$ | $-95.0\%$ |
| **Fixed SC ($k=5$)** | $59.33\% \pm 1.89\%$ | $5.00 \pm 0.00$ | $1,192.8 \pm 14.2$ | $1.0 \pm 0.0$ | $6.21\text{s}$ | $-75.0\%$ |
| **Fixed SC ($k=10$)** | $60.67\% \pm 2.49\%$ | $10.00 \pm 0.00$ | $2,385.1 \pm 28.5$ | $1.0 \pm 0.0$ | $12.44\text{s}$ | $-50.0\%$ |
| **Fixed SC ($k=20$)** | $\mathbf{62.67\%} \pm 1.89\%$ | $20.00 \pm 0.00$ | $4,770.2 \pm 57.0$ | $1.0 \pm 0.0$ | $24.87\text{s}$ | Baseline ($1.0\times$) |
| **Adaptive Consistency** | $61.33\% \pm 1.89\%$ | $8.45 \pm 0.25$ | $2,015.4 \pm 62.1$ | $2.3 \pm 0.1$ | $10.51\text{s}$ | $-57.8\%$ |
| **ESC ($w=5, L=20$)** | $\mathbf{62.00\%} \pm 1.63\%$ | $\mathbf{6.90} \pm 0.16$ | $\mathbf{1,645.7} \pm 38.8$ | $\mathbf{1.4} \pm 0.0$ | $\mathbf{8.58\text{s}}$ | $\mathbf{-65.5\%}$ |

```
Accuracy (%)
  64 |
  62 |             [ESC w=5] (62.0%, 6.9 samples)   • [SC-20] (62.7%, 20 samples)
  60 |      • [SC-5]        • [AC] (61.3%, 8.5 samples)
  58 |
  48 | • [Greedy] (48.0%, 1 sample)
     +------------------------------------------------------------> Mean Samples / Q
     0      2      4      6      8      10     12     14     16     18     20
```

1. **Efficiency Frontier**: ESC delivers **$62.00\%$ accuracy** (within $0.67\%$ of full SC-20) while slashing computational cost by **$65.5\%$ in samples**, **$62.7\%$ in total tokens**, and achieving a **$2.7\times$ speedup** in wall-clock latency.
2. **Early Halting Rate**: Over $70\%$ of questions halt in Window 1 ($n=5$).
3. **Phase 2 Deliverables**: Full research report ([`RP2_U23AI042_report.docx`](project/phase2/report/RP2_U23AI042_report.docx), [`pdf`](project/phase2/report/RP2_U23AI042_report.pdf)), slide deck ([`RP2_U23AI042_slides.pptx`](project/phase2/report/RP2_U23AI042_slides.pptx), [`pdf`](project/phase2/report/RP2_U23AI042_slides.pdf)), and zip archive ([`RP2_U23AI042.zip`](project/RP2_U23AI042.zip)).

---

### Working Output Scenarios & Failure Taxonomy

Complete execution traces for model operation are documented in [`project/phase2/demo_output.txt`](project/phase2/demo_output.txt) and [`project/phase2/results/model_working_output.txt`](project/phase2/results/model_working_output.txt), covering 5 diagnostic operational cases:

1. **Case 1: Early-Stopping Success (Unanimous Consensus in Window 1)**  
   *Question:* GSM8K-88 (Janet's ducks and eggs).  
   *Execution:* All 5 samples in Window 1 output identical answer `48`. ESC halts immediately at $n=5$, saving 15 redundant sample calls.
2. **Case 2: Multi-Window Recovery (Split in Window 1, Consensus in Window 2)**  
   *Question:* GSM8K-448 (Multi-step grocery budget).  
   *Execution:* Window 1 splits $[18, 18, 18, 22, 18]$ (4 vs 1, no unanimity). ESC continues into Window 2; samples 6–10 unanimously vote `18`. Halts at $n=10$ with correct answer.
3. **Case 3: The Small-Model Hazard (False Consensus Failure on Wrong Answer)**  
   *Question:* GSM8K-99 (Bella's stamp collection; ground truth = `11`).  
   *Execution:* Due to a shared syntactic misinterpretation in the prompt, the 1.5B model produces incorrect answer `23` across all 5 initial samples. ESC halts prematurely on an incorrect answer. This demonstrates the critical vulnerability of early stopping on low-parameter LLMs.
4. **Case 4: Budget Exhaustion (No Window Consensus $\rightarrow$ Fallback to Majority Vote)**  
   *Question:* GSM8K-3 (High reasoning entropy arithmetic).  
   *Execution:* Windows 1 through 4 fail unanimity ($[2, 3], [3, 2], \dots$). ESC exhausts the maximum budget $L=20$ and falls back to global majority vote, recovering the correct answer.
5. **Case 5: Error Correction (Greedy Fails $\rightarrow$ ESC Recovers)**  
   *Question:* GSM8K-81 (Compound interest and discounts).  
   *Execution:* Greedy ($T=0$) hallucinates an intermediate arithmetic step and outputs wrong answer `450`. ESC samples diverse trajectories at $T=0.7$; majority voting suppresses the error mode and yields correct answer `520`.

---

## Repository Structure

```
AA-AI465/
├── .gitignore                          # Standard git exclusion rules
├── README.md                           # Master course and project documentation
├── build_notebooks.py                  # End-to-end generator and executor for Lab 7, 8, 9 notebooks
│
├── Lab1/                               # Lab 1: Reflex & Model-Based Agents
│   ├── README.md
│   ├── Agentic_AI_Lab1_Experiment1.pdf
│   ├── exp1_reflex_agent.py
│   ├── exp1_ex1_model_based.py
│   ├── exp1_ex2_corridor.py
│   ├── exp1_ex3_stochastic_dirt.py
│   ├── make_plots.py & make_report.py
│   ├── LAB_1_U23AI042.doc
│   └── outputs/
│
├── lab2/                               # Lab 2: Search-Based Agents (BFS, UCS, Replanning)
│   ├── README.md
│   ├── Experiment_2_Deliberative_Goal_Based_Agent.pdf
│   ├── exp2_bfs_agent.py
│   ├── exp2_ex1_uniform_cost.py
│   ├── exp2_ex2_replan.py
│   ├── exp2_ex3_hybrid.py
│   ├── make_animation.py & make_plots.py & make_report.py
│   ├── LAB_2_U23AI042.doc
│   └── outputs/
│
├── lab3/                               # Lab 3: Tool-Using Agent
│   ├── README.md
│   ├── Agentic_AI_Lab3_Experiment3.pdf
│   ├── exp3_tool_agent.py & exp3_exercises.py
│   ├── sample_temperatures.csv
│   ├── make_report.py
│   ├── LAB_3_U23AI042.doc
│   └── outputs/
│
├── lab4/                               # Lab 4: RAG Pipeline Agent
│   ├── README.md
│   ├── Agentic_AI_Lab4_Experiment4.pdf
│   ├── corpus.py & exp4_rag_pipeline.py & exp4_exercises.py
│   ├── docs/ (doc1_bfs.txt, doc2_ucs.txt, doc3_tfidf.txt, doc4_rag.txt)
│   ├── make_report.py
│   ├── LAB_4_U23AI042.doc
│   └── outputs/
│
├── lab5/                               # Lab 5: Chain-of-Thought & Self-Consistency
│   ├── README.md
│   ├── questions.py & exp5_cot_selfconsistency.py & exp5_exercises.py
│   ├── make_plots.py & make_report.py
│   ├── LAB_5_U23AI042.doc
│   └── outputs/
│
├── lab6/                               # Lab 6: Multi-Agent Collaboration
│   ├── README.md
│   ├── roles.py & docstore.py & exp6_role_agents.py & exp6_exercises.py
│   ├── make_plots.py & make_report.py
│   ├── LAB_6_U23AI042.doc
│   └── outputs/
│
├── lab7/                               # Lab 7: Markov Decision Processes (MDP)
│   ├── README.md
│   ├── Agentic_AI_Lab7_Experiment7.pdf
│   ├── exp7_mdp.py
│   ├── lab7.ipynb & LAB_7_U23AI042.ipynb
│   ├── make_report.py
│   ├── LAB_7_U23AI042.doc
│   └── outputs/ (lab7_fig1 to fig4, exp7_mdp.txt)
│
├── lab8/                               # Lab 8: Game Theory & Repeated Play
│   ├── README.md
│   ├── lab8.ipynb & LAB_8_U23AI042.ipynb
│   └── outputs/ (lab8_fig1 to fig3)
│
├── lab9/                               # Lab 9: Multi-Layer Perceptron (MLP)
│   ├── README.md
│   ├── IA305_Lab9_Neural_Network.pdf
│   ├── exp9_mlp.py
│   ├── lab9.ipynb & LAB_9_U23AI042.ipynb
│   ├── make_report.py
│   ├── LAB_9_U23AI042.doc
│   └── outputs/ (lab9_fig1 to fig3, exp9_mlp.txt)
│
└── project/                            # Capstone Research Project
    ├── README.md                       # Comprehensive project documentation
    ├── papers/                         # Wang et al. 2023, Aggarwal 2023, Li et al. 2024
    ├── AI465_Research_Project_Phase1.pdf
    ├── AI465_Research_Project_Phase2.pdf
    ├── phase1/                         # Phase 1 Proposal report, slides, and figures
    │   ├── RP1_U23AI042.docx & .pdf
    │   └── RP1_U23AI042_slides.pptx & .pdf
    └── phase2/                         # Phase 2 Experimental framework
        ├── README.md
        ├── config.json
        ├── data/ (gsm8k_test.jsonl, subset_ids.json)
        ├── src/ (llm.py, gsm8k.py, methods.py, sample.py, evaluate.py, plots.py)
        ├── traces/ (run_11/, run_22/, run_33/, greedy/, demo/)
        ├── results/ (table_main.md, summary.csv, failure_cases.md, checker_audit.csv)
        ├── figures/ (fig1 to fig4)
        ├── report/ (RP2_U23AI042_report.docx, RP2_U23AI042_slides.pptx)
        ├── demo_output.txt & results/model_working_output.txt
        └── build_all.py
```

---

## Setup & Reproducibility Guide

### 1. Prerequisites & Environment Setup
Clone the repository and set up a Python 3.10+ virtual environment:

```bash
git clone https://github.com/aryanjsawant/AA-AI465.git
cd AA-AI465

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install numpy matplotlib scipy nbformat nbclient jupyter python-docx
```

### 2. Running Laboratory Practical Scripts
Any lab can be executed independently from its folder:

```bash
# Example: Run Lab 7 MDP simulation and generate figures
cd lab7
python exp7_mdp.py
python make_report.py

# Example: Run Lab 9 MLP training and decision boundary visualizations
cd ../lab9
python exp9_mlp.py
python make_report.py
```

### 3. Re-generating All Lab Notebooks
The root repository includes an automated notebook synthesis engine that compiles, executes, and exports clean notebooks with complete outputs for Labs 7, 8, and 9:

```bash
python build_notebooks.py
```

### 4. Reproducing Research Project Phase 2
To regenerate all experimental tables, failure case audits, and publication figures from the cached traces:

```bash
cd project/phase2

# Run evaluation and figure generation
python build_all.py

# Run live demo trace on diagnostic task
python demo.py --task 6
```

---

## Academic Integrity & License

This repository is maintained for academic evaluation at **SVNIT Surat**.  
All code and reports are authored by **Aryan Sawant (`U23AI042`)**.  
Reference implementations of third-party algorithms are credited to their original publications.
