# Lab 7: Agent Behaviour as a Markov Decision Process (MDP)

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment models an agent acting in a stochastic environment as a Markov Decision Process (MDP), implementing exact dynamic programming and model-free reinforcement learning:
1. **$4 \times 3$ GridWorld Formulation**:
   - 11 states (9 non-terminal, 2 terminal: Goal $+1.0$ at $(3, 2)$, Trap $-1.0$ at $(3, 1)$, obstacle at $(1, 1)$).
   - Stochastic transitions: Intended direction $1 - 2p$, perpendicular slips $p$ ($p=0.1$).
   - Step cost $R_{\text{step}} = -0.04$, discount factor $\gamma = 0.95$.
2. **Value Iteration (VI)**: Iterative application of the Bellman optimality backup:
   $$V_{k+1}(s) = \max_{a} \sum_{s'} P(s' \mid s, a) [R(s, a, s') + \gamma V_k(s')]$$
   Tracking convergence via maximum Bellman residual $\Delta_k = \max_s |V_{k+1}(s) - V_k(s)| < \theta$.
3. **Policy Iteration (PI)**: Alternating Policy Evaluation (exact linear system solve $(I - \gamma P_\pi) V_\pi = R_\pi$) and Policy Improvement ($\pi_{k+1} = \text{greedy}(V_{\pi_k})$).
4. **Computational Work Comparison**: Comparing operations, state backups, and wall-clock convergence between VI and PI.
5. **Exercises**:
   - *Exercise 1 (Q-Learning)*: Model-free temporal difference control over 5,000 episodes with $\epsilon$-greedy exploration ($\epsilon=0.1$, $\alpha=0.1$).
   - *Exercise 2 (Step Reward Sweep)*: Sensitivity analysis across $R_{\text{step}} \in \{-2.0, -0.4, -0.04, -0.005, +0.01\}$ demonstrating risk-taking, detour, and suicide agent behaviors.

---

## Deliverables & Files

| File | Description |
|---|---|
| `lab7.ipynb` / `LAB_7_U23AI042.ipynb` | Complete, fully executed interactive Jupyter notebook with math, code, visualizations, and answers. |
| `exp7_mdp.py` | Standalone script running VI, PI, Q-learning, step-reward sweep, and exporting plots to `outputs/`. |
| `make_report.py` | Compiles the self-contained report `LAB_7_U23AI042.doc` with embedded base64 figures and discussion. |
| `LAB_7_U23AI042.doc` | Final laboratory report deliverable. |
| `Agentic_AI_Lab7_Experiment7.pdf` | Official lab task sheet. |
| `outputs/` | Contains `exp7_mdp.txt` and high-resolution figures (`lab7_fig1` to `fig4`). |

---

## How to Run

```bash
# Run standalone simulation and generate figures
python exp7_mdp.py

# Recompile laboratory report
python make_report.py

# Run or view notebook
jupyter notebook LAB_7_U23AI042.ipynb
```
