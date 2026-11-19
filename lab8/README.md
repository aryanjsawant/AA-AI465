# Lab 8: Game-Theoretic Intuition for Agent Interaction — Equilibria and Repeated Play

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment investigates strategic multi-agent interaction, cooperative equilibria, and evolutionary stability through classical and repeated game theory:
1. **Normal-Form Prisoner's Dilemma**:
   - Payoff structure: Temptation $T = 5$, Reward $R = 3$, Punishment $P = 1$, Sucker's payoff $S = 0$, satisfying $T > R > P > S$ and $2R > T + S$.
   - Identification of dominant strategies and the unique Nash Equilibrium $(\text{Defect}, \text{Defect})$ vs Pareto optimal $(\text{Cooperate}, \text{Cooperate})$.
2. **Axelrod Round-Robin Tournament**:
   - Tournament simulation across 8 prominent repeated strategies:
     - **AllC**: Always Cooperate.
     - **AllD**: Always Defect.
     - **TFT (Tit-for-Tat)**: Cooperates initially, then copies the opponent's previous move.
     - **Grim Trigger**: Cooperates until the opponent defects once, then defects forever.
     - **Pavlov (Win-Stay, Lose-Shift)**: Cooperates if both agreed on previous round; switches otherwise.
     - **Random**: Plays Cooperate or Defect with equal probability.
     - **TF2T (Tit-for-Two-Tats)**: Forgiving variant that defects only after two consecutive opponent defections.
     - **STFT (Suspicious Tit-for-Tat)**: Defects on the first round, then mirrors.
3. **Noisy Environments & Misperception (Noise Sweep)**:
   - Introducing execution error where an intended action is inverted with probability $\epsilon \in [0.0, 0.25]$.
   - Demonstrating the fragility of brittle retaliatory strategies (Grim Trigger) and the breakdown of mutual cooperation without forgiveness.
4. **Infinitely Repeated Games & Folk Theorem**:
   - Discount factor and continuation probability $\delta \in [0.5, 0.99]$.
   - Verification of the Folk Theorem threshold: $\delta \ge \frac{T - R}{T - P} = \frac{5 - 3}{5 - 1} = 0.5$ for sustaining cooperative subgame perfect equilibria.

---

## Deliverables & Files

| File | Description |
|---|---|
| `lab8.ipynb` / `LAB_8_U23AI042.ipynb` | Fully executed, self-contained Jupyter notebook with complete mathematical derivations, Axelrod simulation engine, and interactive visualizations. |
| `outputs/lab8_fig1_tournament_matrix.png` | Pairwise payoff heatmap and cumulative tournament leaderboard across all 8 strategies. |
| `outputs/lab8_fig2_noise_sweep.png` | Average payoff degradation curves as execution noise $\epsilon$ increases from $0\%$ to $25\%$. |
| `outputs/lab8_fig3_continuation_prob.png` | Cooperation sustainability and expected total payoffs as a function of continuation probability $\delta$. |

---

## How to Run

```bash
# View or run the notebook
jupyter notebook LAB_8_U23AI042.ipynb

# Or re-execute via root notebook builder
python build_notebooks.py
```
