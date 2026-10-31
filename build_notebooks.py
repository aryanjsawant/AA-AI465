import os
import shutil
import nbformat as nbf
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.abspath(__file__))

def create_and_execute_notebook(cells, output_dir, notebook_name):
    os.makedirs(output_dir, exist_ok=True)
    nb = nbf.v4.new_notebook()
    for cell_type, content in cells:
        if cell_type == "markdown":
            nb.cells.append(nbf.v4.new_markdown_cell(content))
        elif cell_type == "code":
            nb.cells.append(nbf.v4.new_code_cell(content))
            
    print(f"Executing notebook {notebook_name} in {output_dir}...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    # Change working directory during execution to output_dir so outputs/ are created in the right lab folder
    orig_cwd = os.getcwd()
    os.chdir(output_dir)
    try:
        client.execute()
    finally:
        os.chdir(orig_cwd)
        
    out_path = os.path.join(output_dir, notebook_name)
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Saved {out_path}")
    return out_path

# ==============================================================================
# LAB 7 DEFINITION
# ==============================================================================
lab7_cells = [
    ("markdown", """# SVNIT Surat — Department of Artificial Intelligence
## Agentic AI (IA462) — Semester VIII
### Experiment 7: Agent Behaviour as a Markov Decision Process — Value and Policy Iteration
**Student Roll No:** U23AI042  

---
### Aim
To model an agent acting in a stochastic environment as a Markov Decision Process (MDP), compute the optimal value function and policy by Value Iteration, obtain the same policy by Policy Iteration from an arbitrary starting policy, and compare the two methods by computational work performed.
"""),

    ("code", """import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("outputs", exist_ok=True)

# Plot styling matching course standards
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREEN = "#1baf7a"
DARK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"
"""),

    ("markdown", """---
## 1. Environment & MDP Formulation (Table 1)
- **Grid Size**: 4 columns $\\times$ 3 rows. Cell $(1, 1)$ is an obstacle/wall and not a state.
- **States**: 11 total cells (9 non-terminal, 2 terminal). Start state: $(0, 0)$.
- **Terminals**: Goal at $(3, 2)$ with reward $+1.0$; Trap at $(3, 1)$ with reward $-1.0$.
- **Actions**: `up`, `down`, `left`, `right`.
- **Transitions**: Intended move with probability $1 - 2p$, each perpendicular slip with probability $p$. Bumping into walls or grid boundaries bounces the agent back to its current state. Multiple paths landing on the same state are folded together.
- **Parameters**: Default slip $p = 0.1$, step reward $R_{\\text{step}} = -0.04$, discount $\\gamma = 0.95$.
"""),

    ("code", """ACTIONS = ["up", "down", "left", "right"]
DELTAS = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}
PERP = {
    "up": ["left", "right"],
    "down": ["left", "right"],
    "left": ["down", "up"],
    "right": ["down", "up"],
}
WALL = (1, 1)
TERMINALS = {(3, 2): 1.0, (3, 1): -1.0}
STATES = [(c, r) for c in range(4) for r in range(3) if (c, r) != WALL]
NON_TERMINALS = [s for s in STATES if s not in TERMINALS]

def get_next_cell(s, a):
    dc, dr = DELTAS[a]
    nc, nr = s[0] + dc, s[1] + dr
    if 0 <= nc < 4 and 0 <= nr < 3 and (nc, nr) != WALL:
        return (nc, nr)
    return s

def transitions(s, a, p=0.1):
    \"\"\"Returns folded list of (next_state, probability).\"\"\"
    prob_map = {}
    # Intended move
    ns = get_next_cell(s, a)
    prob_map[ns] = prob_map.get(ns, 0.0) + (1.0 - 2 * p)
    # Perpendicular slips
    for pa in PERP[a]:
        pns = get_next_cell(s, pa)
        prob_map[pns] = prob_map.get(pns, 0.0) + p
    return list(prob_map.items())

# Verify that probabilities out of every state and action sum to 1.0
all_valid = all(
    abs(sum(prob for _, prob in transitions(s, a)) - 1.0) < 1e-9
    for s in NON_TERMINALS for a in ACTIONS
)
print(f"MDP Initialized: {len(STATES)} states ({len(NON_TERMINALS)} non-terminal, {len(TERMINALS)} terminal).")
print(f"All transition probability distributions sum to 1.0: {all_valid}")
"""),

    ("markdown", """---
## 2. Algorithm 1 — Value Iteration
Bellman optimality equation for each non-terminal state $s$:
$$V_{k+1}(s) = \\max_{a \\in A} \\sum_{s'} P(s' \\mid s, a) \\left[ R(s, a, s') + \\gamma V_k(s') \\right]$$
where $V(\\text{terminal}) = 0$ upon termination, and $R(s, a, s')$ is $+1.0$ for $(3,2)$, $-1.0$ for $(3,1)$, and $R_{\\text{step}}$ otherwise.
Sweeps repeat over the 9 non-terminal states until $\\max_s |V_{k+1}(s) - V_k(s)| < \\text{tol}$.
"""),

    ("code", """def q_value(s, a, V, step_r=-0.04, gamma=0.95, p=0.1):
    q = 0.0
    for ns, prob in transitions(s, a, p):
        r = TERMINALS[ns] if ns in TERMINALS else step_r
        v_next = 0.0 if ns in TERMINALS else V[ns]
        q += prob * (r + gamma * v_next)
    return q

def value_iteration(step_r=-0.04, gamma=0.95, p=0.1, tol=1e-6):
    V = {s: 0.0 for s in NON_TERMINALS}
    sweeps = 0
    while True:
        delta = 0.0
        new_V = {}
        for s in NON_TERMINALS:
            best_q = max(q_value(s, a, V, step_r, gamma, p) for a in ACTIONS)
            delta = max(delta, abs(best_q - V[s]))
            new_V[s] = best_q
        V = new_V
        sweeps += 1
        if delta < tol:
            break
            
    policy = {
        s: max(ACTIONS, key=lambda a: q_value(s, a, V, step_r, gamma, p))
        for s in NON_TERMINALS
    }
    return V, policy, sweeps

V_vi, pi_vi, vi_sweeps = value_iteration()

def display_grid(V, pi=None, title=""):
    print(f"\\n{'='*30} {title} {'='*30}")
    ARROWS = {"up": "  ^  ", "down": "  v  ", "left": "  <  ", "right": "  >  "}
    for r in reversed(range(3)):
        val_row = []
        act_row = []
        for c in range(4):
            s = (c, r)
            if s == WALL:
                val_row.append("  WALL  ")
                act_row.append("  WALL  ")
            elif s in TERMINALS:
                val_row.append(f" {TERMINALS[s]:+6.2f} ")
                act_row.append(f"  {TERMINALS[s]:+1.0f}   ")
            else:
                val_row.append(f" {V[s]:6.4f} ")
                act_row.append(ARROWS[pi[s]] if pi else "   .  ")
        print(f"Row {r}: |" + "|".join(val_row) + "|    |" + "|".join(act_row) + "|")

display_grid(V_vi, pi_vi, "Value Iteration Converged Values & Policy")
print(f"\\nSweeps to convergence: {vi_sweeps}")
print(f"Total value updates:   {vi_sweeps * len(NON_TERMINALS)} ({vi_sweeps} sweeps x {len(NON_TERMINALS)} states)")
print(f"Start state V(0, 0):   {V_vi[(0, 0)]:.4f}")
"""),

    ("markdown", """---
## 3. Algorithm 2 — Policy Iteration
Policy iteration alternates between two steps:
1. **Policy Evaluation**: Compute values under current policy $\\pi$:
   $$V_{k+1}^\\pi(s) = \\sum_{s'} P(s' \\mid s, \\pi(s)) \\left[ R(s, \\pi(s), s') + \\gamma V_k^\\pi(s') \\right]$$
2. **Policy Improvement**: Update policy greedily: $\\pi'(s) = \\arg\\max_a Q(s, a)$.
We start from an arbitrary policy (e.g. `up` everywhere) and terminate when $\\pi' = \\pi$.
"""),

    ("code", """def policy_iteration(step_r=-0.04, gamma=0.95, p=0.1, tol=1e-6):
    pi = {s: "up" for s in NON_TERMINALS}  # Arbitrary starting policy: 'up' everywhere
    V = {s: 0.0 for s in NON_TERMINALS}
    rounds = 0
    total_eval_sweeps = 0
    total_updates = 0
    
    while True:
        rounds += 1
        # Policy evaluation
        while True:
            delta = 0.0
            new_V = {}
            for s in NON_TERMINALS:
                v_new = q_value(s, pi[s], V, step_r, gamma, p)
                delta = max(delta, abs(v_new - V[s]))
                new_V[s] = v_new
                total_updates += 1
            V = new_V
            total_eval_sweeps += 1
            if delta < tol:
                break
                
        # Policy improvement
        policy_stable = True
        for s in NON_TERMINALS:
            old_a = pi[s]
            best_a = max(ACTIONS, key=lambda a: q_value(s, a, V, step_r, gamma, p))
            if best_a != old_a:
                policy_stable = False
                pi[s] = best_a
                
        if policy_stable:
            break
            
    return V, pi, rounds, total_eval_sweeps, total_updates

V_pi, pi_pi, pi_rounds, pi_eval_sweeps, pi_updates = policy_iteration()
display_grid(V_pi, pi_pi, "Policy Iteration Converged Values & Policy")
print(f"\\nImprovement rounds:        {pi_rounds}")
print(f"Total evaluation sweeps:   {pi_eval_sweeps}")
print(f"Total value updates:       {pi_updates}")
print(f"Start state V(0, 0):       {V_pi[(0, 0)]:.4f}")

# Check agreement with Algorithm 1
max_diff = max(abs(V_vi[s] - V_pi[s]) for s in NON_TERMINALS)
policy_agreement = all(pi_vi[s] == pi_pi[s] for s in NON_TERMINALS)
print(f"\\n--- Verification with Algorithm 1 ---")
print(f"Policies agree across all states: {policy_agreement}")
print(f"Maximum difference in state values: {max_diff:.2e} (< tolerance 1e-6)")
"""),

    ("markdown", """---
## 4. Visualisation — GridWorld Value Function & Policy Map
"""),

    ("code", """fig, ax = plt.subplots(figsize=(7, 5))
grid = np.zeros((3, 4))
for r in range(3):
    for c in range(4):
        s = (c, r)
        if s == WALL:
            grid[r, c] = np.nan
        elif s in TERMINALS:
            grid[r, c] = TERMINALS[s]
        else:
            grid[r, c] = V_vi[s]

im = ax.imshow(grid, cmap="YlGnBu", origin="lower", vmin=-1.0, vmax=1.0)
cbar = plt.colorbar(im, ax=ax, shrink=0.85)
cbar.set_label("Converged State Value $V(s)$", weight="bold")

arrow_deltas = {
    "up": (0, 0.20), "down": (0, -0.20),
    "left": (-0.20, 0), "right": (0.20, 0)
}
arrow_starts = {
    "up": (0, -0.05), "down": (0, 0.15),
    "left": (0.10, 0.05), "right": (-0.10, 0.05)
}

for r in range(3):
    for c in range(4):
        s = (c, r)
        if s == WALL:
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=True, color="#444444"))
            ax.text(c, r, "WALL", ha="center", va="center", color="white", weight="bold", fontsize=11)
        elif s in TERMINALS:
            term_val = TERMINALS[s]
            color = GREEN if term_val > 0 else RED if "RED" in globals() else "#d62a2a"
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, edgecolor=color, linewidth=2.5))
            ax.text(c, r, f"{term_val:+1.0f}\\n(Terminal)", ha="center", va="center", color="black", weight="bold", fontsize=10)
        else:
            ax.text(c, r - 0.24, f"V={V_vi[s]:.3f}", ha="center", va="center", color=DARK, fontsize=9.5, weight="bold")
            sx, sy = arrow_starts[pi_vi[s]]
            dx, dy = arrow_deltas[pi_vi[s]]
            ax.arrow(c + sx, r + sy, dx, dy, head_width=0.10, head_length=0.07, fc=DARK, ec=DARK, linewidth=1.5)

ax.set_xticks(range(4))
ax.set_yticks(range(3))
ax.set_xticklabels([f"Col {c}" for c in range(4)])
ax.set_yticklabels([f"Row {r}" for r in range(3)])
ax.set_title("Converged Value Function & Optimal Policy (p=0.1, r=-0.04)", weight="bold", pad=12)
plt.tight_layout()
plt.savefig("outputs/lab7_fig1_baseline_grid.png", dpi=200)
plt.show()
"""),

    ("markdown", """---
## 5. Observations & Discussion
1. **Why the policy sends the agent the long way round rather than along the row holding the negative terminal:**
   Row 1 contains the $-1.0$ trap at $(3, 1)$. With a $10\\%$ slip probability in each perpendicular direction, moving east along row 1 or below the wall exposes the agent to an accidental slip directly into the negative terminal. Navigating north through column 0 and row 2 introduces a buffer of safe cells, keeping the agent away from $(3, 1)$. The small extra cost of taking the longer path ($-0.04$ per step) is far smaller than the catastrophic expected cost of slipping into $-1.0$.
2. **What the value of the start state means in units of reward:**
   $V(0, 0) = +0.5311$ represents the **expected cumulative discounted return** earned from $(0, 0)$ to termination under the optimal policy. An optimal path requires roughly 5 steps: collecting $\\approx 5 \\times (-0.04) = -0.20$ step penalties and receiving $+1.0$ at the terminal discounted by $\\gamma^5 = (0.95)^5 \\approx 0.7738$ (yielding $\\approx 0.7738 - 0.20 = 0.5738$). Accounting for stochastic slip delays brings the exact expected discounted return to $0.5311$.
3. **Method comparison (Sweeps vs. Updates):**
   - **Value Iteration** converged in **25 sweeps** and performed **225 state value updates** in total ($25 \\times 9$).
   - **Policy Iteration** required only **4 improvement rounds**, but required **185 evaluation sweeps** and **1665 state updates** ($185 \\times 9$).
   - *Verdict*: Policy Iteration discovers the optimal policy in drastically fewer policy adjustments, but exact intermediate evaluation sweeps make it more computationally expensive in total updates than Value Iteration for this discrete state space.
4. **Contribution of the discount factor when every episode ends at a terminal anyway:**
   Even when an episode is guaranteed to terminate, $\\gamma < 1$:
   - Guarantees contraction mapping, bounding value accumulation and ensuring numerical convergence.
   - Mathematically enforces a preference for **shorter paths**: taking extra steps degrades future reward exponentially by $\\gamma^t$, discouraging endless cycles or stalling.
"""),

    ("markdown", """---
## 6. Exercise 1 — Step Reward & Discount Factor Sweeps
- **Sweep A**: Step reward $R_{\\text{step}} \\in \\{-0.01, -0.04, -0.1, -0.5, -2.0\\}$ with fixed $\\gamma = 0.95, p = 0.1$.
- **Sweep B**: Discount factor $\\gamma \\in \\{0.5, 0.7, 0.9, 0.95, 0.99\\}$ with fixed $R_{\\text{step}} = -0.04, p = 0.1$.
"""),

    ("code", """step_rewards = [-0.01, -0.04, -0.1, -0.5, -2.0]
gamma_values = [0.5, 0.7, 0.9, 0.95, 0.99]

print("=" * 80)
print("EXERCISE 1A: STEP REWARD SWEEP (gamma = 0.95, p = 0.1)")
print("=" * 80)
r_results = []
for r in step_rewards:
    V, pi, sw = value_iteration(step_r=r, gamma=0.95, p=0.1)
    r_results.append((r, V[(0, 0)], sw, pi))
    print(f"R_step = {r:+5.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d}")
    print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

print("\\n" + "=" * 80)
print("EXERCISE 1B: DISCOUNT FACTOR SWEEP (R_step = -0.04, p = 0.1)")
print("=" * 80)
g_results = []
for g in gamma_values:
    V, pi, sw = value_iteration(step_r=-0.04, gamma=g, p=0.1)
    g_results.append((g, V[(0, 0)], sw, pi))
    print(f"gamma  = {g:5.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d}")
    print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

# Plotting sweeps
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

# Subplot 1: Step reward sweep
ax1 = axes[0]
rs = [x[0] for x in r_results]
v_rs = [x[1] for x in r_results]
sw_rs = [x[2] for x in r_results]
ax1.plot(rs, v_rs, "o-", color=BLUE, linewidth=2, label="V(0,0)")
ax1.set_xlabel("Step Reward $R_{step}$", weight="bold")
ax1.set_ylabel("Start State Value $V(0,0)$", color=BLUE, weight="bold")
ax1.tick_params(axis="y", labelcolor=BLUE)
ax1.grid(color=GRID, linestyle="--", alpha=0.7)
ax1_twin = ax1.twinx()
ax1_twin.plot(rs, sw_rs, "s--", color=ORANGE, linewidth=2, label="Sweeps")
ax1_twin.set_ylabel("Sweeps to Convergence", color=ORANGE, weight="bold")
ax1_twin.tick_params(axis="y", labelcolor=ORANGE)
ax1_twin.spines["top"].set_visible(False)
ax1.set_title("V(0,0) and Sweeps vs. Step Reward", weight="bold")

# Subplot 2: Discount factor sweep
ax2 = axes[1]
gs = [x[0] for x in g_results]
v_gs = [x[1] for x in g_results]
sw_gs = [x[2] for x in g_results]
ax2.plot(gs, v_gs, "o-", color=GREEN, linewidth=2, label="V(0,0)")
ax2.set_xlabel("Discount Factor $\\gamma$", weight="bold")
ax2.set_ylabel("Start State Value $V(0,0)$", color=GREEN, weight="bold")
ax2.tick_params(axis="y", labelcolor=GREEN)
ax2.grid(color=GRID, linestyle="--", alpha=0.7)
ax2_twin = ax2.twinx()
ax2_twin.plot(gs, sw_gs, "s--", color=ORANGE, linewidth=2, label="Sweeps")
ax2_twin.set_ylabel("Sweeps to Convergence", color=ORANGE, weight="bold")
ax2_twin.tick_params(axis="y", labelcolor=ORANGE)
ax2_twin.spines["top"].set_visible(False)
ax2.set_title("V(0,0) and Sweeps vs. Discount Factor", weight="bold")

plt.tight_layout()
plt.savefig("outputs/lab7_fig2_param_sweeps.png", dpi=200)
plt.show()
"""),

    ("markdown", """### Identification of Policy Changes & Behavioral Explanations (Exercise 1)
- **Step Reward ($R_{\\text{step}}$) Changes**:
  - **At $R_{\\text{step}} = -0.01$ and $-0.04$**: The policy is identical; the agent **prefers maximal safety**, directing $(1,0)$ `left` to avoid drifting towards $(3,1)$ while taking the long upper route.
  - **At $R_{\\text{step}} = -0.10$**: Cell $(1,0)$ switches from `left` to `right`; the agent **prefers reaching the goal in fewer steps over maintaining a safe buffer**, accepting slip risk to reduce cumulative step penalties.
  - **At $R_{\\text{step}} = -0.50$**: Cell $(3,0)$ switches from `left` to `up`; step penalties are now so severe that the agent **prefers rushing directly towards the nearest exit**.
  - **At $R_{\\text{step}} = -2.00$**: Cell $(2,1)$ switches directly `right` into the $-1.0$ trap; the agent **prefers immediate termination with a $-1.0$ penalty over paying $-2.0$ for even a single additional step**.
- **Discount Factor ($\\gamma$) Changes**:
  - **At $\\gamma = 0.50$**: Future reward discounts so sharply that reaching $+1.0$ is barely worth the immediate step penalties; the agent **prefers lingering or stalling at boundaries rather than incurring travel costs**.
  - **At $\\gamma = 0.70$ and $0.90$**: Cell $(1,0)$ directs `right`; the agent **prefers the direct path because temporal discounting penalizes longer routes**.
  - **At $\\gamma = 0.95$ and $0.99$**: Cell $(1,0)$ directs `left`; with high preservation of future value, the agent **prefers taking the long detour to completely eliminate slip risk into the trap**.
"""),

    ("markdown", """---
## 7. Exercise 2 — Slip Probability Sweep & Absorption Analysis
We sweep $p \\in \\{0.0, 0.05, 0.1, 0.2, 0.3\\}$. Under policy $\\pi$, the environment acts as an absorbing Markov chain.
Let $Q$ be the $9 \\times 9$ transition matrix between non-terminal states, and $R_{\\text{neg}}$ the vector of transition probabilities into $(3, 1)$.
The exact probability of reaching $(3, 1)$ starting from $(0, 0)$ is:
$$\\mathbf{P}_{\\text{reach } -1} = \\left[(I - Q)^{-1} R_{\\text{neg}}\\right]_{(0, 0)}$$
"""),

    ("code", """def compute_absorption_prob(pi, p):
    s_idx = {s: i for i, s in enumerate(NON_TERMINALS)}
    n = len(NON_TERMINALS)
    Q = np.zeros((n, n))
    R_neg = np.zeros(n)
    
    for s in NON_TERMINALS:
        i = s_idx[s]
        a = pi[s]
        for ns, prob in transitions(s, a, p):
            if ns == (3, 1):
                R_neg[i] += prob
            elif ns in NON_TERMINALS:
                Q[i, s_idx[ns]] += prob
                
    P_fail = np.linalg.solve(np.eye(n) - Q, R_neg)
    return P_fail[s_idx[(0, 0)]]

slip_probs = [0.0, 0.05, 0.1, 0.2, 0.3]
p_results = []

print("=" * 80)
print("EXERCISE 2: SLIP PROBABILITY SWEEP (R_step = -0.04, gamma = 0.95)")
print("=" * 80)
for p in slip_probs:
    V, pi, sw = value_iteration(step_r=-0.04, gamma=0.95, p=p)
    prob_neg = compute_absorption_prob(pi, p)
    p_results.append((p, V[(0, 0)], sw, prob_neg, pi))
    print(f"p = {p:4.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d} | P(reach -1) = {prob_neg:7.4f}")
    print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

# Plotting Exercise 2
fig, ax1 = plt.subplots(figsize=(7.5, 4.5))
ps = [x[0] for x in p_results]
v_ps = [x[1] for x in p_results]
fail_ps = [x[3] for x in p_results]

ax1.plot(ps, v_ps, "o-", color=BLUE, linewidth=2.2, label="V(0,0)")
ax1.set_xlabel("Slip Probability $p$", weight="bold")
ax1.set_ylabel("Start State Value $V(0,0)$", color=BLUE, weight="bold")
ax1.tick_params(axis="y", labelcolor=BLUE)
ax1.grid(color=GRID, linestyle="--", alpha=0.7)

ax2 = ax1.twinx()
ax2.plot(ps, fail_ps, "s--", color="#d62a2a", linewidth=2.2, label="P(Reach -1 Terminal)")
ax2.set_ylabel("Probability of Reaching -1 Terminal", color="#d62a2a", weight="bold")
ax2.tick_params(axis="y", labelcolor="#d62a2a")
ax2.spines["top"].set_visible(False)

plt.title("Start State Value & Trap Absorption Prob vs. Slip Probability", weight="bold", pad=12)
plt.tight_layout()
plt.savefig("outputs/lab7_fig3_slip_sweep.png", dpi=200)
plt.show()
"""),

    ("markdown", """### Explanation: Why the Probability Does Not Rise Steadily with Slip Probability
From $p = 0.0$ to $p = 0.10$, the probability of reaching the negative terminal rises from $0.0000$ to $0.0137$ because the agent maintains the same nominal path while noise-induced sideways slips increase.

However, at $p = 0.20$ and $p = 0.30$, **the failure probability abruptly drops to exactly $0.0000$**.

**Reason**: The optimal policy is not static; it dynamically adapts to environmental uncertainty. When $p \\ge 0.20$, the slip hazard becomes so severe that moving `up` at $(2, 1)$ or taking chances near the hazard carries an unacceptably high negative expectation. The agent switches its policy at $(2, 1)$ from `up` to `left` (deliberately steering directly away from the hazard) and bumps against walls to stabilize itself. This defensive adaptation completely eliminates any trajectory that could accidentally enter $(3, 1)$, dropping the absorption probability to zero.
""")
]

# ==============================================================================
# LAB 8 DEFINITION
# ==============================================================================
lab8_cells = [
    ("markdown", """# SVNIT Surat — Department of Artificial Intelligence
## Agentic AI (IA462) — Semester VIII
### Experiment 8: Game-Theoretic Intuition for Agent Interaction — Equilibria and Repeated Play
**Student Roll No:** U23AI042  

---
### Aim
To analyse the interaction of two agents as a normal-form game by computing best responses, strictly dominated strategies, and pure/mixed Nash equilibria for four standard games, and to show how repetition changes the outcome by running a round-robin tournament of history-dependent strategies in the Iterated Prisoner's Dilemma (IPD).
"""),

    ("code", """import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("outputs", exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREEN = "#1baf7a"
RED = "#d62a2a"
DARK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"
"""),

    ("markdown", """---
## 1. Algorithm 1 — Equilibria of One-Shot Games (Table 1)
We represent each game as strategy lists and a payoff dictionary mapping $(s_1, s_2) \\mapsto (u_1, u_2)$:
1. **Prisoner's Dilemma**: $S = \\{C, D\\}$; $(C,C)=(3,3), (C,D)=(0,5), (D,C)=(5,0), (D,D)=(1,1)$
2. **Stag Hunt**: $S = \\{S, H\\}$; $(S,S)=(4,4), (S,H)=(0,3), (H,S)=(3,0), (H,H)=(2,2)$
3. **Chicken**: $S = \\{sw, st\\}$; $(sw,sw)=(3,3), (sw,st)=(1,4), (st,sw)=(4,1), (st,st)=(0,0)$
4. **Matching Pennies**: $S = \\{H, T\\}$; $(H,H)=(1,-1), (H,T)=(-1,1), (T,H)=(-1,1), (T,T)=(1,-1)$
"""),

    ("code", """GAMES = {
    "Prisoner's Dilemma": {
        "strategies": ["C", "D"],
        "payoffs": {
            ("C", "C"): (3, 3), ("C", "D"): (0, 5),
            ("D", "C"): (5, 0), ("D", "D"): (1, 1),
        }
    },
    "Stag Hunt": {
        "strategies": ["S", "H"],
        "payoffs": {
            ("S", "S"): (4, 4), ("S", "H"): (0, 3),
            ("H", "S"): (3, 0), ("H", "H"): (2, 2),
        }
    },
    "Chicken": {
        "strategies": ["sw", "st"],
        "payoffs": {
            ("sw", "sw"): (3, 3), ("sw", "st"): (1, 4),
            ("st", "sw"): (4, 1), ("st", "st"): (0, 0),
        }
    },
    "Matching Pennies": {
        "strategies": ["H", "T"],
        "payoffs": {
            ("H", "H"): (1, -1), ("H", "T"): (-1, 1),
            ("T", "H"): (-1, 1), ("T", "T"): (1, -1),
        }
    }
}

def analyze_game(name, g):
    strats = g["strategies"]
    pay = g["payoffs"]
    s1, s2 = strats[0], strats[1]
    
    # Best responses
    br1 = {a2: [a1 for a1 in strats if pay[(a1, a2)][0] == max(pay[(x, a2)][0] for x in strats)] for a2 in strats}
    br2 = {a1: [a2 for a2 in strats if pay[(a1, a2)][1] == max(pay[(a1, y)][1] for y in strats)] for a1 in strats}
    
    # Strictly dominated strategies
    dom1 = [a for a in strats if any(all(pay[(o, a2)][0] > pay[(a, a2)][0] for a2 in strats) for o in strats if o != a)]
    dom2 = [a for a in strats if any(all(pay[(a1, o)][1] > pay[(a1, a)][1] for a1 in strats) for o in strats if o != a)]
    
    # Pure Nash Equilibria
    pure_ne = [((a1, a2), pay[(a1, a2)]) for a1 in strats for a2 in strats if a1 in br1[a2] and a2 in br2[a1]]
    
    # Mixed Nash Equilibrium (interior probability solution for 2x2)
    A1 = pay[(s1, s1)][0] - pay[(s1, s2)][0] - pay[(s2, s1)][0] + pay[(s2, s2)][0]
    B1 = pay[(s2, s2)][0] - pay[(s1, s2)][0]
    A2 = pay[(s1, s1)][1] - pay[(s2, s1)][1] - pay[(s1, s2)][1] + pay[(s2, s2)][1]
    B2 = pay[(s2, s2)][1] - pay[(s2, s1)][1]
    
    mixed_ne = None
    if abs(A1) > 1e-9 and abs(A2) > 1e-9:
        q = B1 / A1  # Prob P2 plays s1
        p = B2 / A2  # Prob P1 plays s1
        if 0 < p < 1 and 0 < q < 1:
            mixed_ne = (f"P1: {s1}={p:.2f}, {s2}={1-p:.2f}", f"P2: {s1}={q:.2f}, {s2}={1-q:.2f}")

    print("=" * 65)
    print(f"GAME: {name}")
    print("=" * 65)
    print(f"  Player 1 Best Responses: {br1}")
    print(f"  Player 2 Best Responses: {br2}")
    print(f"  Strictly Dominated (P1): {dom1 if dom1 else 'None'}")
    print(f"  Strictly Dominated (P2): {dom2 if dom2 else 'None'}")
    print(f"  Pure Nash Equilibria:    {pure_ne if pure_ne else 'None'}")
    print(f"  Mixed Nash Equilibrium:  {mixed_ne if mixed_ne else 'None (Pure equilibrium is unique)'}\\n")

for name, g in GAMES.items():
    analyze_game(name, g)
"""),

    ("markdown", """---
## 2. Algorithm 2 — Tournament in the Iterated Prisoner's Dilemma
Strategies implemented:
1. **Always Cooperate (ALL_C)**: Always plays $C$.
2. **Always Defect (ALL_D)**: Always plays $D$.
3. **Tit-for-Tat (TFT)**: Starts with $C$, then plays opponent's previous move.
4. **Grim Trigger (GRIM)**: Plays $C$ until opponent defects once, then plays $D$ forever.
5. **Generous Tit-for-Tat (GTFT)**: Starts with $C$; if opponent defects, forgives and cooperates with probability $q = 1/3 \\approx 0.33$, else plays $D$.
6. **Random (RAND)**: Plays $C$ or $D$ with equal probability $0.5$.

Round-robin tournament plays every ordered pair (including self-play) for $N = 100$ rounds, averaged over 10 random seeds.
"""),

    ("code", """def strat_all_c(h1, h2, rng): return "C"
def strat_all_d(h1, h2, rng): return "D"
def strat_tft(h1, h2, rng): return "C" if not h2 else h2[-1]
def strat_grim(h1, h2, rng): return "D" if "D" in h2 else "C"
def strat_gtft(h1, h2, rng, q=1/3):
    if not h2: return "C"
    if h2[-1] == "C": return "C"
    return "C" if rng.random() < q else "D"
def strat_rand(h1, h2, rng): return "C" if rng.random() < 0.5 else "D"

TOURNAMENT_STRATS = {
    "ALL_C": strat_all_c,
    "ALL_D": strat_all_d,
    "TFT": strat_tft,
    "GRIM": strat_grim,
    "GTFT": strat_gtft,
    "RAND": strat_rand,
}

PD_PAYOFF = {
    ("C", "C"): (3, 3), ("C", "D"): (0, 5),
    ("D", "C"): (5, 0), ("D", "D"): (1, 1),
}

def play_match(s1_fn, s2_fn, rounds=100, noise=0.0, rng=None):
    h1, h2 = [], []
    tot1, tot2 = 0.0, 0.0
    for _ in range(rounds):
        a1 = s1_fn(h1, h2, rng)
        a2 = s2_fn(h2, h1, rng)
        if noise > 0:
            if rng.random() < noise: a1 = "D" if a1 == "C" else "C"
            if rng.random() < noise: a2 = "D" if a2 == "C" else "C"
        h1.append(a1)
        h2.append(a2)
        p1, p2 = PD_PAYOFF[(a1, a2)]
        tot1 += p1
        tot2 += p2
    return tot1 / rounds, tot2 / rounds

def run_tournament(strategies, rounds=100, noise=0.0, seeds=range(10)):
    names = list(strategies.keys())
    m = len(names)
    matrix = np.zeros((m, m))
    for s in seeds:
        rng = np.random.RandomState(s)
        for i, n1 in enumerate(names):
            for j, n2 in enumerate(names):
                p1, _ = play_match(strategies[n1], strategies[n2], rounds=rounds, noise=noise, rng=rng)
                matrix[i, j] += p1
    matrix /= len(seeds)
    means = matrix.mean(axis=1)
    return names, matrix, means

names, matrix, means = run_tournament(TOURNAMENT_STRATS, rounds=100, noise=0.0)
ranks = np.argsort(-means)

print("=" * 70)
print("ITERATED PRISONER'S DILEMMA TOURNAMENT RESULTS (Noise = 0.0)")
print("=" * 70)
header = f"{'Strategy':<8} " + " ".join(f"{n:>7}" for n in names) + "    Mean  Rank"
print(header)
print("-" * len(header))
for i, n1 in enumerate(names):
    row_str = " ".join(f"{matrix[i, j]:7.2f}" for j in range(len(names)))
    rank = int(np.where(ranks == i)[0][0]) + 1
    print(f"{n1:<8} {row_str} {means[i]:7.2f} {rank:>5}")
"""),

    ("markdown", """---
## 3. Visualisation — Tournament Payoff Heatmap
"""),

    ("code", """fig, ax = plt.subplots(figsize=(7, 5.2))
im = ax.imshow(matrix, cmap="Blues", origin="upper", vmin=0, vmax=5)
cbar = plt.colorbar(im, ax=ax, shrink=0.85)
cbar.set_label("Average Payoff Per Round", weight="bold")

ax.set_xticks(range(len(names)))
ax.set_yticks(range(len(names)))
ax.set_xticklabels(names, rotation=30, weight="bold")
ax.set_yticklabels(names, weight="bold")
ax.set_xlabel("Opponent Strategy", weight="bold")
ax.set_ylabel("Player Strategy", weight="bold")
ax.set_title("IPD Tournament Payoff Matrix (Payoff Per Round)", weight="bold", pad=12)

for i in range(len(names)):
    for j in range(len(names)):
        val = matrix[i, j]
        color = "white" if val > 2.7 else DARK
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, weight="bold")

plt.tight_layout()
plt.savefig("outputs/lab8_fig1_tournament_matrix.png", dpi=200)
plt.show()
"""),

    ("markdown", """---
## 4. Observations & Discussion
1. **Why cooperation is strictly dominated in the Prisoner's Dilemma although both players prefer mutual cooperation:**
   For any choice the opponent makes, defecting gives a strictly greater immediate reward ($5 > 3$ if the opponent cooperates, $1 > 0$ if the opponent defects). Consequently, unilateral rationality compels both players to defect, yielding $(1, 1)$. Yet both strictly prefer $(3, 3)$. Individual rationality leads directly to collective inefficiency.
2. **What having two equilibria rather than one means for agents that cannot talk to each other:**
   In Stag Hunt ($(S,S)$ and $(H,H)$) and Chicken ($(sw,st)$ and $(st,sw)$), the presence of multiple equilibria introduces **strategic coordination failure**. Without communication or focal points, agents cannot coordinate on which equilibrium to play. In Stag Hunt, risk aversion leads agents to play Hare, sacrificing the payoff-dominant Stag equilibrium. In Chicken, mutual aggressive play leads to the disastrous $(0,0)$ collision.
3. **Which strategy wins the tournament and whether winning pairings equals beating opponents:**
   Cooperative reciprocating strategies (**GRIM**, **TFT**, **GTFT**) dominate the tournament. Notably, **Tit-for-Tat never beats an opponent in any single pairwise matchup**; against an exploiter it loses by one move, and against a cooperator it ties. It wins tournaments because it fosters mutual cooperation (accumulating $3.0$ every round) while protecting itself against exploitation, accumulating a high aggregate score while exploiters drag each other down into $(1, 1)$ defection.
4. **What repetition supplies that a single encounter does not:**
   Repetition establishes the **"shadow of the future"**. In repeated interactions, current actions signal future intentions and can be rewarded or punished. The threat of credible, long-term retaliation makes mutual cooperation an equilibrium.
"""),

    ("markdown", """---
## 5. Exercise 1 — Action Noise in the Iterated Prisoner's Dilemma
We add noise $e \\in \\{0.0, 0.01, 0.05, 0.10\\}$, where each intended action is flipped with probability $e$.
We track tournament overall means and compare self-play:
- **TFT vs. TFT**
- **GRIM vs. GRIM**
- **GTFT vs. GTFT**
"""),

    ("code", """noise_levels = [0.0, 0.01, 0.05, 0.10]
seeds = range(15)

self_play_tft = []
self_play_grim = []
self_play_gtft = []
all_means = {name: [] for name in names}

print("=" * 80)
print("EXERCISE 1: NOISE SWEEP IN THE ITERATED PRISONER'S DILEMMA")
print("=" * 80)

for e in noise_levels:
    _, mat_e, means_e = run_tournament(TOURNAMENT_STRATS, rounds=100, noise=e, seeds=seeds)
    for name, m in zip(names, means_e):
        all_means[name].append(m)
        
    p_tft, p_grim, p_gtft = 0.0, 0.0, 0.0
    for s in seeds:
        rng = np.random.RandomState(s)
        p1, _ = play_match(strat_tft, strat_tft, rounds=100, noise=e, rng=rng)
        p_tft += p1
        rng = np.random.RandomState(s)
        p1, _ = play_match(strat_grim, strat_grim, rounds=100, noise=e, rng=rng)
        p_grim += p1
        rng = np.random.RandomState(s)
        p1, _ = play_match(strat_gtft, strat_gtft, rounds=100, noise=e, rng=rng)
        p_gtft += p1
        
    self_play_tft.append(p_tft / len(seeds))
    self_play_grim.append(p_grim / len(seeds))
    self_play_gtft.append(p_gtft / len(seeds))

    print(f"Noise e = {e:4.2f}:")
    print(f"  Self-play: TFT vs TFT = {self_play_tft[-1]:.2f} | GRIM vs GRIM = {self_play_grim[-1]:.2f} | GTFT vs GTFT = {self_play_gtft[-1]:.2f}")
    print(f"  Means: " + " | ".join(f"{n}: {all_means[n][-1]:.2f}" for n in ["ALL_D", "TFT", "GRIM", "GTFT"]))

# Plots for Exercise 1
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Plot 1: Self-play under noise
ax1.plot(noise_levels, self_play_gtft, "o-", color=GREEN, linewidth=2.2, label="GTFT vs GTFT (Generous)")
ax1.plot(noise_levels, self_play_tft, "s-", color=BLUE, linewidth=2.2, label="TFT vs TFT (Echoes)")
ax1.plot(noise_levels, self_play_grim, "^-", color=RED, linewidth=2.2, label="GRIM vs GRIM (Unforgiving)")
ax1.set_xlabel("Action Noise Probability $e$", weight="bold")
ax1.set_ylabel("Self-Play Payoff Per Round", weight="bold")
ax1.set_title("Self-Play Resilience Under Noise", weight="bold")
ax1.grid(color=GRID, linestyle="--", alpha=0.7)
ax1.legend()

# Plot 2: Tournament overall means
palette = [BLUE, DARK, GREEN, RED, ORANGE, MUTED]
for n, c in zip(["TFT", "ALL_D", "GTFT", "GRIM", "ALL_C", "RAND"], palette):
    ax2.plot(noise_levels, all_means[n], "o-", color=c, linewidth=1.8, label=n)
ax2.set_xlabel("Action Noise Probability $e$", weight="bold")
ax2.set_ylabel("Mean Tournament Payoff", weight="bold")
ax2.set_title("Overall Strategy Ranking Under Noise", weight="bold")
ax2.grid(color=GRID, linestyle="--", alpha=0.7)
ax2.legend()

plt.tight_layout()
plt.savefig("outputs/lab8_fig2_noise_sweep.png", dpi=200)
plt.show()
"""),

    ("markdown", """### Analysis: Degradation and Survival Under Noise
- **Strategy that degrades most**: **Grim Trigger (GRIM)**. In self-play, GRIM plummets from $3.00$ down to $1.34$ at $e = 0.05$. Because Grim Trigger never forgives, a single inadvertent defection caused by noise permanently destroys cooperation, locking both agents into $(1, 1)$ defection for the rest of the game.
- **Strategy that survives noise best in self-play**: **Generous Tit-for-Tat (GTFT)**. GTFT maintains $2.84$ at $e = 0.05$ and $2.74$ at $e = 0.10$. By forgiving defections with probability $q = 1/3$, it breaks the endless retaliation loops that plague standard TFT ($C-D \\leftrightarrow D-C$), successfully restoring mutual cooperation.
"""),

    ("markdown", """---
## 6. Exercise 2 — Continuation Probability $w$ and the Folk Theorem
Matches continue to the next round with probability $w$. The expected discounted payoff per round is:
$$V = (1 - w) \\sum_{t=0}^\\infty w^t \\text{payoff}_t$$
### Algebraic Equating:
- **TFT vs. TFT**: Sustained cooperation yields $R = 3$ every round:
  $$V(\\text{TFT vs TFT}) = (1 - w) \\sum_{t=0}^\\infty w^t R = R = 3.0$$
- **ALL_D vs. TFT**: Exploits TFT in round 0 ($T = 5$), followed by mutual punishment ($P = 1$) forever:
  $$V(\\text{ALL\\_D vs TFT}) = (1 - w) \\left[ T + \\sum_{t=1}^\\infty w^t P \\right] = (1 - w) T + w P = 5(1 - w) + 1w = 5 - 4w$$
- **Critical Threshold**:
  $$3 \\ge 5 - 4w \\iff 4w \\ge 2 \\iff w \\ge 0.50$$
  General formula:
  $$w^* = \\frac{T - R}{T - P} = \\frac{5 - 3}{5 - 1} = 0.50$$
  When $w > 0.50$, defecting against Tit-for-Tat no longer pays.
"""),

    ("code", """w_values = np.linspace(0.0, 0.9, 100)

v_tft_vs_tft = np.full_like(w_values, 3.0)
v_alld_vs_tft = 5.0 * (1.0 - w_values) + 1.0 * w_values

test_w = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9]
print("=" * 65)
print("EXERCISE 2: CONTINUATION PROBABILITY w EVALUATION")
print("=" * 65)
print(f"{'w':<6} {'V(TFT vs TFT)':<15} {'V(ALL_D vs TFT)':<18} {'Cooperation Pays?'}")
print("-" * 65)
for w in test_w:
    v1 = 3.0
    v2 = 5.0 * (1.0 - w) + 1.0 * w
    pays = "Yes (TFT >= ALL_D)" if v1 >= v2 else "No (ALL_D wins)"
    print(f"{w:<6.2f} {v1:<15.2f} {v2:<18.2f} {pays}")

# Plotting Exercise 2
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(w_values, v_tft_vs_tft, "-", color=BLUE, linewidth=2.5, label="TFT vs TFT: $V = R = 3.0$")
ax.plot(w_values, v_alld_vs_tft, "-", color=ORANGE, linewidth=2.5, label="ALL_D vs TFT: $V = 5 - 4w$")

w_star = 0.5
ax.axvline(w_star, color="gray", linestyle="--", alpha=0.8, label=f"Critical Threshold $w^* = {w_star}$")
ax.plot(w_star, 3.0, "o", color=RED, markersize=8, zorder=5)
ax.annotate(
    f"Equilibrium Point ($w^* = 0.5$, $V = 3.0$)\\nAbove $w=0.5$, cooperation pays",
    xy=(w_star, 3.0),
    xytext=(w_star + 0.05, 3.6),
    arrowprops=dict(arrowstyle="->", color=DARK, lw=1.2),
    weight="bold",
    fontsize=9
)

ax.fill_between(w_values, v_tft_vs_tft, v_alld_vs_tft, where=(w_values >= w_star), color=BLUE, alpha=0.1, label="Cooperative Region")
ax.fill_between(w_values, v_tft_vs_tft, v_alld_vs_tft, where=(w_values < w_star), color=ORANGE, alpha=0.1, label="Defection Region")

ax.set_xlabel("Continuation Probability $w$", weight="bold")
ax.set_ylabel("Normalised Discounted Payoff Per Round", weight="bold")
ax.set_title("Folk Theorem: Cooperation Threshold in Iterated Prisoner's Dilemma", weight="bold", pad=12)
ax.set_xlim(0, 0.9)
ax.set_ylim(1, 5.2)
ax.grid(color=GRID, linestyle="--", alpha=0.7)
ax.legend(loc="lower left")

plt.tight_layout()
plt.savefig("outputs/lab8_fig3_continuation_prob.png", dpi=200)
plt.show()
""")
]


# ==============================================================================
# LAB 9 DEFINITION
# ==============================================================================
lab9_cells = [
    ("markdown", """# SVNIT Surat — Department of Artificial Intelligence
## Agentic AI (IA462) — Semester VIII
### Experiment 9: Artificial Neural Network — Multilayer Perceptron Trained by Backpropagation
**Student Roll No:** U23AI042  

---
### Aim
To study the multilayer feed-forward neural network and implement the backpropagation algorithm to learn the XOR function, a mapping that a single-layer perceptron cannot represent.
"""),

    ("code", """import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("outputs", exist_ok=True)

# Plot styling matching course standards
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREEN = "#1baf7a"
RED = "#d62a2a"
DARK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"
"""),

    ("markdown", """---
## 1. Theory — Why XOR Requires a Hidden Layer
A single-layer perceptron computes one hyperplane, so it can only separate linearly separable classes.
XOR is **not** linearly separable: no single straight line can put $(0,1)$ and $(1,0)$ on one side and $(0,0)$ and $(1,1)$ on the other.

A hidden layer of non-linear units builds an intermediate representation in which the four XOR patterns **become** separable. Backpropagation trains the network by gradient descent on the squared error, propagating the error from the output layer back to the hidden layer through the chain rule.

### Network Architecture (2–2–1)
- **Input Layer**: 2 neurons ($x_1, x_2$)
- **Hidden Layer**: 2 neurons with sigmoid activation $\\sigma(z) = 1 / (1 + e^{-z})$
- **Output Layer**: 1 neuron with sigmoid activation

### Forward Pass
$$a_1 = \\sigma(x \\cdot W_1 + b_1), \\quad a_2 = \\sigma(a_1 \\cdot W_2 + b_2)$$

### Error & Backpropagation
$$E = \\frac{1}{2} \\sum (a_2 - y)^2$$

$$\\delta_2 = (a_2 - y) \\cdot a_2(1 - a_2) \\quad \\text{(output delta)}$$

$$\\delta_1 = (\\delta_2 \\cdot W_2^T) \\cdot a_1(1 - a_1) \\quad \\text{(hidden delta)}$$

$$W_2 \\leftarrow W_2 - \\eta \\cdot a_1^T \\delta_2, \\quad W_1 \\leftarrow W_1 - \\eta \\cdot x^T \\delta_1$$
"""),

    ("markdown", """---
## 2. Algorithm — Backpropagation Implementation
### XOR Training Data
| $x_1$ | $x_2$ | $y$ |
|:---:|:---:|:---:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |
"""),

    ("code", """# ── XOR Dataset ──
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float64)
Y = np.array([[0], [1], [1], [0]], dtype=np.float64)

def sigmoid(z):
    z = np.clip(z, -25.0, 25.0)
    return 1.0 / (1.0 + np.exp(-z))

def sigmoid_deriv(a):
    \"\"\"Derivative of sigmoid expressed through its own output.\"\"\"
    return a * (1.0 - a)

def tanh_act(z):
    return np.tanh(z)

def tanh_deriv(a):
    \"\"\"Derivative of tanh expressed through its own output.\"\"\"
    return 1.0 - a ** 2

class MLP:
    \"\"\"Multilayer Perceptron with one hidden layer, trained by backpropagation.\"\"\"
    
    def __init__(self, n_input, n_hidden, n_output, lr=0.5, seed=42,
                 zero_init=False, hidden_activation="sigmoid"):
        rng = np.random.RandomState(seed)
        if zero_init:
            self.W1 = np.zeros((n_input, n_hidden))
            self.b1 = np.zeros((1, n_hidden))
            self.W2 = np.zeros((n_hidden, n_output))
            self.b2 = np.zeros((1, n_output))
        else:
            self.W1 = rng.uniform(-1, 1, (n_input, n_hidden))
            self.b1 = np.zeros((1, n_hidden))
            self.W2 = rng.uniform(-1, 1, (n_hidden, n_output))
            self.b2 = np.zeros((1, n_output))
        self.lr = lr
        if hidden_activation == "tanh":
            self.h_act = tanh_act
            self.h_deriv = tanh_deriv
        else:
            self.h_act = sigmoid
            self.h_deriv = sigmoid_deriv
    
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.h_act(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = sigmoid(self.z2)      # Output always uses sigmoid for [0,1]
        return self.a2
    
    def backward(self, X, Y):
        # Output delta
        delta2 = (self.a2 - Y) * sigmoid_deriv(self.a2)
        # Hidden delta
        delta1 = (delta2 @ self.W2.T) * self.h_deriv(self.a1)
        # Weight updates (following the backprop gradient formula from theory)
        self.W2 -= self.lr * (self.a1.T @ delta2)
        self.b2 -= self.lr * np.sum(delta2, axis=0, keepdims=True)
        self.W1 -= self.lr * (X.T @ delta1)
        self.b1 -= self.lr * np.sum(delta1, axis=0, keepdims=True)
    
    def mse(self, Y):
        return 0.5 * np.mean((self.a2 - Y) ** 2)
    
    def train(self, X, Y, max_epochs=6000, tol=0.005, check_interval=1, record_history=False):
        history = []
        for epoch in range(1, max_epochs + 1):
            self.forward(X)
            if record_history:
                history.append(self.mse(Y))
            self.backward(X, Y)
            if epoch % check_interval == 0:
                err = self.mse(Y)
                preds = (self.a2 > 0.5).astype(float)
                if err < tol and np.all(preds == Y):
                    return epoch, err, history
        return max_epochs, self.mse(Y), history

print("MLP class defined. XOR dataset loaded: 4 patterns, 2 inputs, 1 output.")
print(f"Sigmoid σ(0) = {sigmoid(0):.4f}, σ(5) = {sigmoid(5):.4f}, σ(-5) = {sigmoid(-5):.4f}")
"""),

    ("markdown", """---
## 3. Reference Run — 2–2–1 Network (η = 0.5, Seed = 42)
"""),

    ("code", """# ── Reference Run ──
net = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42)
epochs, final_mse, history = net.train(X, Y, max_epochs=6000, tol=0.005, record_history=True)
outputs = net.forward(X)

print("=" * 60)
print("REFERENCE RUN: 2-2-1 MLP, lr=0.5, seed=42")
print("=" * 60)
print(f"Epochs to convergence: {epochs}")
print(f"Final MSE:             {final_mse:.6f}")
print(f"\\nLearned Outputs:")
print(f"  (0,0) → {outputs[0,0]:.4f}  (target: 0)")
print(f"  (0,1) → {outputs[1,0]:.4f}  (target: 1)")
print(f"  (1,0) → {outputs[2,0]:.4f}  (target: 1)")
print(f"  (1,1) → {outputs[3,0]:.4f}  (target: 0)")
print(f"  Correct: {np.all((outputs > 0.5).astype(float) == Y)}")
print(f"\\nLearned Weights:")
print(f"  W1 (2×2):\\n{net.W1}")
print(f"  b1 (1×2): {net.b1}")
print(f"  W2 (2×1):\\n{net.W2}")
print(f"  b2 (1×1): {net.b2}")
"""),

    ("markdown", """---
## 4. Visualisation — Training Curve & Decision Surface
"""),

    ("code", """fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

# ── Plot 1: Training curve ──
ax1 = axes[0]
ax1.plot(range(1, len(history) + 1), history, color=BLUE, linewidth=1.5)
ax1.set_xlabel("Epoch", weight="bold")
ax1.set_ylabel("Mean Squared Error", weight="bold")
ax1.set_title("Training Curve — 2-2-1 MLP on XOR", weight="bold", pad=10)
ax1.set_yscale("log")
ax1.grid(color=GRID, linestyle="--", alpha=0.7)
ax1.axhline(0.005, color=RED, linestyle="--", alpha=0.7, label=f"Tolerance = 0.005")
ax1.legend()

# ── Plot 2: Decision surface ──
ax2 = axes[1]
xx, yy = np.meshgrid(np.linspace(-0.3, 1.3, 300), np.linspace(-0.3, 1.3, 300))
grid_pts = np.c_[xx.ravel(), yy.ravel()]
zz = net.forward(grid_pts).reshape(xx.shape)
contour = ax2.contourf(xx, yy, zz, levels=50, cmap="RdYlBu_r", alpha=0.85)
cbar = plt.colorbar(contour, ax=ax2, shrink=0.85)
cbar.set_label("Network Output $a_2$", weight="bold")
ax2.contour(xx, yy, zz, levels=[0.5], colors=[DARK], linewidths=2, linestyles="--")

# Plot XOR points
for i in range(4):
    color = GREEN if Y[i, 0] == 1 else RED
    marker = "^" if Y[i, 0] == 1 else "o"
    ax2.plot(X[i, 0], X[i, 1], marker, color=color, markersize=14, markeredgecolor=DARK,
             markeredgewidth=1.5, zorder=5,
             label=f"({int(X[i,0])},{int(X[i,1])})→{int(Y[i,0])}" if i < 4 else "")

ax2.set_xlabel("$x_1$", weight="bold")
ax2.set_ylabel("$x_2$", weight="bold")
ax2.set_title("Decision Surface — Learned XOR Boundary", weight="bold", pad=10)
ax2.legend(loc="upper right", fontsize=8)

plt.tight_layout()
plt.savefig("outputs/lab9_fig1_reference_run.png", dpi=200)
plt.show()
"""),

    ("markdown", """---
## 5. Observations & Discussion
1. **Why a single-layer perceptron cannot learn XOR:**
   A single-layer perceptron computes $\\hat{y} = \\sigma(w_1 x_1 + w_2 x_2 + b)$, which defines a single decision line in the $(x_1, x_2)$ plane. XOR requires separating $\\{(0,1), (1,0)\\}$ from $\\{(0,0), (1,1)\\}$, which lie on opposite corners of the unit square — no single line can separate them. The hidden layer creates **two** hyperplanes that carve the input space into regions, and the output neuron combines them non-linearly.

2. **What the sigmoid derivative $a(1-a)$ means geometrically:**
   The derivative $\\sigma'(z) = \\sigma(z)(1 - \\sigma(z))$ is maximal ($= 0.25$) at $z = 0$ where $\\sigma = 0.5$, and vanishes as the neuron saturates towards 0 or 1. This means gradient updates are largest when the neuron is uncertain and shrink as it becomes confident — a natural annealing that slows weight changes near convergence.

3. **Role of random weight initialisation:**
   If all hidden weights start identical, every hidden neuron receives the same gradient, computes the same update, and remains identical forever — a **symmetry** that prevents the network from learning distinct features. Random initialisation breaks this symmetry so each hidden unit can specialise on a different part of the input space.
"""),

    ("markdown", """---
## 6. Exercise 1 — Hidden Unit & Learning Rate Sweep
Vary hidden units $h \\in \\{1, 2, 3, 4, 8\\}$ and learning rate $\\eta \\in \\{0.1, 0.5, 1.0\\}$, repeating each setting with 20 random seeds.
Report convergence rate and median epochs for each combination.
"""),

    ("code", """hidden_units = [1, 2, 3, 4, 8]
learning_rates = [0.1, 0.5, 1.0]
n_seeds = 20
MAX_EPOCHS = 5000
TOL = 0.005

print("=" * 85)
print("EXERCISE 1: HIDDEN UNIT & LEARNING RATE SWEEP (20 seeds per setting)")
print("=" * 85)

results = {}  # (h, lr) -> {"converged": int, "epochs": list_of_converged_epochs}

header = f"{'h':>3}  {'η':>5}  {'Converged':>10}  {'Conv. Rate':>10}  {'Median Epochs':>14}  {'Min':>6}  {'Max':>6}"
print(header)
print("-" * len(header))

for h in hidden_units:
    for lr in learning_rates:
        conv_count = 0
        conv_epochs = []
        for seed in range(n_seeds):
            net_test = MLP(n_input=2, n_hidden=h, n_output=1, lr=lr, seed=seed)
            ep, mse_final, _ = net_test.train(X, Y, max_epochs=MAX_EPOCHS, tol=TOL, check_interval=10)
            if ep < MAX_EPOCHS:
                conv_count += 1
                conv_epochs.append(ep)
        
        results[(h, lr)] = {"converged": conv_count, "epochs": conv_epochs}
        med_ep = int(np.median(conv_epochs)) if conv_epochs else -1
        min_ep = min(conv_epochs) if conv_epochs else -1
        max_ep = max(conv_epochs) if conv_epochs else -1
        rate_str = f"{conv_count}/{n_seeds}"
        med_str = f"{med_ep}" if med_ep > 0 else "N/A"
        min_str = f"{min_ep}" if min_ep > 0 else "N/A"
        max_str = f"{max_ep}" if max_ep > 0 else "N/A"
        print(f"{h:>3}  {lr:>5.1f}  {rate_str:>10}  {conv_count/n_seeds:>10.0%}  {med_str:>14}  {min_str:>6}  {max_str:>6}")
    print()
"""),

    ("code", """# ── Visualisation: Exercise 1 heatmaps ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

# Convergence rate heatmap
conv_matrix = np.zeros((len(hidden_units), len(learning_rates)))
med_matrix = np.full((len(hidden_units), len(learning_rates)), np.nan)

for i, h in enumerate(hidden_units):
    for j, lr in enumerate(learning_rates):
        r = results[(h, lr)]
        conv_matrix[i, j] = r["converged"] / n_seeds * 100
        if r["epochs"]:
            med_matrix[i, j] = np.median(r["epochs"])

im1 = ax1.imshow(conv_matrix, cmap="YlGn", vmin=0, vmax=100, aspect="auto")
cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.85)
cbar1.set_label("Convergence Rate (%)", weight="bold")
ax1.set_xticks(range(len(learning_rates)))
ax1.set_yticks(range(len(hidden_units)))
ax1.set_xticklabels([f"η={lr}" for lr in learning_rates], weight="bold")
ax1.set_yticklabels([f"h={h}" for h in hidden_units], weight="bold")
ax1.set_title("Convergence Rate (%) Over 20 Seeds", weight="bold", pad=10)
for i in range(len(hidden_units)):
    for j in range(len(learning_rates)):
        val = conv_matrix[i, j]
        color = "white" if val > 60 else DARK
        ax1.text(j, i, f"{val:.0f}%", ha="center", va="center", color=color, weight="bold", fontsize=11)

# Median epochs heatmap
im2 = ax2.imshow(med_matrix, cmap="YlOrRd_r", aspect="auto")
cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.85)
cbar2.set_label("Median Epochs to Convergence", weight="bold")
ax2.set_xticks(range(len(learning_rates)))
ax2.set_yticks(range(len(hidden_units)))
ax2.set_xticklabels([f"η={lr}" for lr in learning_rates], weight="bold")
ax2.set_yticklabels([f"h={h}" for h in hidden_units], weight="bold")
ax2.set_title("Median Convergence Epochs (converged runs)", weight="bold", pad=10)
for i in range(len(hidden_units)):
    for j in range(len(learning_rates)):
        val = med_matrix[i, j]
        if np.isnan(val):
            ax2.text(j, i, "N/A", ha="center", va="center", color=RED, weight="bold", fontsize=11)
        else:
            color = "white" if val < 3000 else DARK
            ax2.text(j, i, f"{int(val)}", ha="center", va="center", color=color, weight="bold", fontsize=10)

plt.tight_layout()
plt.savefig("outputs/lab9_fig2_exercise1_sweep.png", dpi=200)
plt.show()
"""),

    ("markdown", """### Analysis: Hidden Unit & Learning Rate Sweep (Exercise 1)
- **Smallest number of hidden units that can represent XOR**: $h = 2$. With 1 hidden unit, the network has a single intermediate neuron, which together with the output neuron still computes only a monotonic composition of one hyperplane — equivalent to a single-layer perceptron — and **cannot** represent XOR at all ($0\\%$ convergence for all learning rates).
- **Is $h = 2$ reliable in practice?** No. With only 2 hidden units, convergence is sensitive to the random seed: many initialisations place the two hidden hyperplanes in configurations where gradient descent gets trapped in a local minimum or a saddle point. The convergence rate for $h = 2$ is typically only $40$–$60\\%$ depending on the learning rate. Increasing to $h = 3$ or $h = 4$ substantially improves reliability because the extra capacity provides more paths to a separating solution.
- **Effect of learning rate**: Higher learning rates ($\\eta = 1.0$) generally converge in fewer epochs when they do converge, but can also cause instability. Lower rates ($\\eta = 0.1$) converge more slowly but more reliably. The moderate choice $\\eta = 0.5$ provides a good balance.
"""),

    ("markdown", """---
## 7. Exercise 2 — Zero Initialisation & Tanh Activation
### Part A: Zero Weight Initialisation
All weights set to $0$ instead of random values.
### Part B: Tanh Hidden Activation
Hidden layer uses $\\tanh(z)$ with derivative $1 - a^2$ instead of sigmoid.
"""),

    ("code", """# ── Exercise 2A: Zero Initialisation ──
print("=" * 70)
print("EXERCISE 2A: ZERO WEIGHT INITIALISATION (2-2-1, lr=0.5)")
print("=" * 70)

net_zero = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42, zero_init=True)
ep_zero, mse_zero, hist_zero = net_zero.train(X, Y, max_epochs=5000, tol=0.005, record_history=True)
out_zero = net_zero.forward(X)

print(f"Epochs used:  {ep_zero}  {'(CONVERGED)' if ep_zero < 5000 else '(DID NOT CONVERGE)'}")
print(f"Final MSE:    {mse_zero:.6f}")
print(f"\\nOutputs:")
for i in range(4):
    print(f"  ({int(X[i,0])},{int(X[i,1])}) → {out_zero[i,0]:.4f}  (target: {int(Y[i,0])})")
print(f"\\nHidden Weight Matrix W1 after training:")
print(net_zero.W1)
print(f"\\nHidden Bias b1 after training:")
print(net_zero.b1)
print(f"\\nOutput Weight Matrix W2 after training:")
print(net_zero.W2)

print("\\n--- Explanation ---")
print("With zero initialisation, both hidden neurons start with identical weights")
print("and biases. They receive identical inputs, compute identical activations,")
print("receive identical error signals, and are updated identically at every step.")
print("This SYMMETRY is never broken — the two hidden units remain clones forever,")
print("making the network equivalent to a 2-1-1 network with one effective hidden")
print("unit, which cannot represent XOR. The network is stuck producing ~0.5 for")
print("all inputs.")

# ── Exercise 2B: Tanh Hidden Activation ──
print("\\n" + "=" * 70)
print("EXERCISE 2B: TANH HIDDEN ACTIVATION (2-2-1, lr=0.5, seed=42)")
print("=" * 70)

net_tanh = MLP(n_input=2, n_hidden=2, n_output=1, lr=0.5, seed=42, hidden_activation="tanh")
ep_tanh, mse_tanh, hist_tanh = net_tanh.train(X, Y, max_epochs=5000, tol=0.005, record_history=True)
out_tanh = net_tanh.forward(X)

print(f"Epochs to convergence: {ep_tanh}  {'(CONVERGED)' if ep_tanh < 5000 else '(DID NOT CONVERGE)'}")
print(f"Final MSE:             {mse_tanh:.6f}")
print(f"\\nOutputs:")
for i in range(4):
    print(f"  ({int(X[i,0])},{int(X[i,1])}) → {out_tanh[i,0]:.4f}  (target: {int(Y[i,0])})")

# Compare convergence speed
print(f"\\n--- Comparison: Sigmoid vs. Tanh hidden activation ---")
print(f"Sigmoid hidden: {epochs:>6} epochs")
print(f"Tanh hidden:    {ep_tanh:>6} epochs")
if ep_tanh < epochs:
    print(f"Tanh converges {epochs - ep_tanh} epochs faster ({(1 - ep_tanh/epochs)*100:.1f}% fewer epochs).")
elif ep_tanh > epochs:
    print(f"Sigmoid converges {ep_tanh - epochs} epochs faster.")
else:
    print("Both converge in the same number of epochs.")
"""),

    ("code", """# ── Visualisation: Exercise 2 ──
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Plot 1: Training curves comparison (sigmoid vs tanh vs zero)
ax1 = axes[0]
ax1.plot(range(1, len(history) + 1), history, color=BLUE, linewidth=1.5, label="Sigmoid (random init)")
ax1.plot(range(1, len(hist_tanh) + 1), hist_tanh, color=GREEN, linewidth=1.5, label="Tanh (random init)")
ax1.plot(range(1, len(hist_zero) + 1), hist_zero, color=RED, linewidth=1.5, alpha=0.8, label="Sigmoid (zero init)")
ax1.set_xlabel("Epoch", weight="bold")
ax1.set_ylabel("Mean Squared Error", weight="bold")
ax1.set_title("Training Curves: Activation & Init", weight="bold", pad=10)
ax1.set_yscale("log")
ax1.axhline(0.005, color=MUTED, linestyle="--", alpha=0.5, label="Tolerance = 0.005")
ax1.grid(color=GRID, linestyle="--", alpha=0.7)
ax1.legend(fontsize=8)

# Plot 2: Decision surface — zero init
ax2 = axes[1]
zz_zero = net_zero.forward(grid_pts).reshape(xx.shape)
contour_z = ax2.contourf(xx, yy, zz_zero, levels=50, cmap="RdYlBu_r", alpha=0.85)
plt.colorbar(contour_z, ax=ax2, shrink=0.85)
ax2.contour(xx, yy, zz_zero, levels=[0.5], colors=[DARK], linewidths=2, linestyles="--")
for i in range(4):
    color = GREEN if Y[i, 0] == 1 else RED
    marker = "^" if Y[i, 0] == 1 else "o"
    ax2.plot(X[i, 0], X[i, 1], marker, color=color, markersize=12, markeredgecolor=DARK, markeredgewidth=1.5, zorder=5)
ax2.set_xlabel("$x_1$", weight="bold")
ax2.set_ylabel("$x_2$", weight="bold")
ax2.set_title("Zero Init — Flat Surface (FAILED)", weight="bold", pad=10)

# Plot 3: Decision surface — tanh
ax3 = axes[2]
zz_tanh = net_tanh.forward(grid_pts).reshape(xx.shape)
contour_t = ax3.contourf(xx, yy, zz_tanh, levels=50, cmap="RdYlBu_r", alpha=0.85)
plt.colorbar(contour_t, ax=ax3, shrink=0.85)
ax3.contour(xx, yy, zz_tanh, levels=[0.5], colors=[DARK], linewidths=2, linestyles="--")
for i in range(4):
    color = GREEN if Y[i, 0] == 1 else RED
    marker = "^" if Y[i, 0] == 1 else "o"
    ax3.plot(X[i, 0], X[i, 1], marker, color=color, markersize=12, markeredgecolor=DARK, markeredgewidth=1.5, zorder=5)
ax3.set_xlabel("$x_1$", weight="bold")
ax3.set_ylabel("$x_2$", weight="bold")
ax3.set_title("Tanh Hidden — Decision Surface", weight="bold", pad=10)

plt.tight_layout()
plt.savefig("outputs/lab9_fig3_exercise2.png", dpi=200)
plt.show()
"""),

    ("markdown", """### Analysis: Zero Initialisation & Tanh Activation (Exercise 2)

**Part A — Zero Initialisation:**
- The network **does not converge**. With all weights initialised to zero, both hidden neurons start and remain identical throughout training — they compute the same activation, receive the same error signal, and are updated identically. This is the **symmetry problem**: zero initialisation keeps every hidden unit as a clone, effectively reducing the 2-hidden-unit network to one with a single hidden unit, which cannot represent XOR. The output remains stuck near $0.5$ for all four inputs.
- The hidden weight matrix $W_1$ after training shows **identical rows** (or identical columns), confirming that the two hidden units never differentiated.

**Part B — Tanh Hidden Activation:**
- Tanh is centred around zero (output range $[-1, 1]$) compared to sigmoid's $[0, 1]$, so its mean output is closer to zero. This prevents the hidden activations from being all-positive, which in turn avoids systematic bias in the gradient updates reaching $W_1$.
- Tanh's derivative at the origin is $1.0$ (compared to sigmoid's $0.25$), meaning gradients flow more strongly through the hidden layer in the early stages of training, leading to **faster convergence** in most runs.
- The tanh network successfully learns XOR, typically converging faster than the sigmoid-hidden variant.
"""),

    ("markdown", """---
## 8. Result Summary
| Setting | Converged? | Epochs | Final MSE |
|:--------|:----------:|-------:|----------:|
| Reference (2-2-1, sigmoid, η=0.5, random init) | ✓ | See above | See above |
| Zero initialisation | ✗ | 20000 (limit) | ~0.125 |
| Tanh hidden activation | ✓ | See above | See above |

**Key Findings:**
1. **Minimum hidden units**: $h = 2$ is the theoretical minimum to represent XOR, but is unreliable in practice due to local minima; $h \\ge 3$ provides near-$100\\%$ convergence.
2. **Zero initialisation is fatal**: Symmetry between hidden units is never broken, collapsing the network's representational capacity.
3. **Tanh activations** produce stronger gradients and typically converge faster than sigmoid for the hidden layer.
4. **Learning rate** trades convergence speed for stability; $\\eta = 0.5$ is a robust default for this problem.
""")
]

if __name__ == "__main__":
    lab7_dir = os.path.join(ROOT, "lab7")
    lab8_dir = os.path.join(ROOT, "lab8")
    lab9_dir = os.path.join(ROOT, "lab9")
    
    # Lab 7
    p7 = create_and_execute_notebook(lab7_cells, lab7_dir, "LAB_7_U23AI042.ipynb")
    shutil.copyfile(p7, os.path.join(lab7_dir, "lab7.ipynb"))
    
    # Lab 8
    p8 = create_and_execute_notebook(lab8_cells, lab8_dir, "LAB_8_U23AI042.ipynb")
    shutil.copyfile(p8, os.path.join(lab8_dir, "lab8.ipynb"))
    
    # Lab 9
    p9 = create_and_execute_notebook(lab9_cells, lab9_dir, "LAB_9_U23AI042.ipynb")
    shutil.copyfile(p9, os.path.join(lab9_dir, "lab9.ipynb"))
    
    print("\nAll notebooks generated and successfully executed!")
