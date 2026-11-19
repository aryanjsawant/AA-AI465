# Lab 1: Reflex and Model-Based Agents

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment investigates the foundational agent architectures in artificial intelligence (Russell & Norvig, Chapter 2) within the classic **Vacuum Cleaner World**:
1. **Simple Reflex Agent**: Actions depend strictly on the current percept (location and dirty/clean status), mapping condition to action without memory.
2. **Model-Based Reflex Agent**: Maintains an internal state representing the world to handle partial observability and avoid redundant actions.
3. **N-Room Corridor Environment**: Generalization from 2 locations to an $N$-cell 1D corridor with wall bounce physics.
4. **Stochastic Dirt Arrival**: Dynamic environment where clean rooms can spontaneously become dirty with arrival probability $p_{\text{dirt}}$, evaluating agent responsiveness.

---

## Directory Contents

| File | Description |
|---|---|
| `exp1_reflex_agent.py` | Baseline 2-room simple reflex agent simulation across all 8 initial states. |
| `exp1_ex1_model_based.py` | Model-based agent maintaining internal room state beliefs to stop when all rooms are clean. |
| `exp1_ex2_corridor.py` | $N$-room linear corridor simulation with performance score benchmarking. |
| `exp1_ex3_stochastic_dirt.py` | Simulation with Poisson/Bernoulli dirt arrival, tracking dirt clearance rates. |
| `make_plots.py` | Generates comparative trajectory and performance score plots in `outputs/`. |
| `make_report.py` | Compiles the complete lab report with embedded figures into `LAB_1_U23AI042.doc`. |
| `LAB_1_U23AI042.doc` | Final laboratory report submission deliverable. |
| `Agentic_AI_Lab1_Experiment1.pdf` | Lab assignment sheet and task specifications. |
| `outputs/` | Contains stdout text logs and generated visualization figures. |

---

## How to Run

```bash
# Run baseline reflex agent
python exp1_reflex_agent.py

# Run exercises
python exp1_ex1_model_based.py
python exp1_ex2_corridor.py
python exp1_ex3_stochastic_dirt.py

# Generate plots and compile report
python make_plots.py
python make_report.py
```
