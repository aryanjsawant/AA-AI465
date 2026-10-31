"""SVNIT Surat — Department of Artificial Intelligence
Agentic AI (IA462) — Semester VIII
Experiment 7: Agent Behaviour as a Markov Decision Process — Value and Policy Iteration
Roll No: U23AI042
"""

import os
import numpy as np

# ── 1. Environment & MDP Formulation ──
ACTIONS = ["up", "down", "left", "right"]
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
    prob_map = {}
    ns = get_next_cell(s, a)
    prob_map[ns] = prob_map.get(ns, 0.0) + (1.0 - 2 * p)
    for pa in PERP[a]:
        pns = get_next_cell(s, pa)
        prob_map[pns] = prob_map.get(pns, 0.0) + p
    return list(prob_map.items())

def q_value(s, a, V, step_r=-0.04, gamma=0.95, p=0.1):
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

def policy_iteration(step_r=-0.04, gamma=0.95, p=0.1, tol=1e-6):
    pi = {s: "up" for s in NON_TERMINALS}
    V = {s: 0.0 for s in NON_TERMINALS}
    rounds = 0
    total_eval_sweeps = 0
    total_updates = 0
    while True:
        rounds += 1
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

def display_grid(V, pi=None, title=""):
    print(f"\n{'='*30} {title} {'='*30}")
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

def compute_absorption_prob(pi, p):
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

if __name__ == "__main__":
    all_valid = all(
        abs(sum(prob for _, prob in transitions(s, a)) - 1.0) < 1e-9
        for s in NON_TERMINALS for a in ACTIONS
    )
    print(f"MDP Initialized: {len(STATES)} states ({len(NON_TERMINALS)} non-terminal, {len(TERMINALS)} terminal).")
    print(f"All transition probability distributions sum to 1.0: {all_valid}")

    # Value Iteration
    V_vi, pi_vi, vi_sweeps = value_iteration()
    display_grid(V_vi, pi_vi, "Value Iteration Converged Values & Policy")
    print(f"\nSweeps to convergence: {vi_sweeps}")
    print(f"Total value updates:   {vi_sweeps * len(NON_TERMINALS)} ({vi_sweeps} sweeps x {len(NON_TERMINALS)} states)")
    print(f"Start state V(0, 0):   {V_vi[(0, 0)]:.4f}")

    # Policy Iteration
    V_pi, pi_pi, pi_rounds, pi_eval_sweeps, pi_updates = policy_iteration()
    display_grid(V_pi, pi_pi, "Policy Iteration Converged Values & Policy")
    print(f"\nImprovement rounds:        {pi_rounds}")
    print(f"Total evaluation sweeps:   {pi_eval_sweeps}")
    print(f"Total value updates:       {pi_updates}")
    print(f"Start state V(0, 0):       {V_pi[(0, 0)]:.4f}")

    # Verification
    max_diff = max(abs(V_vi[s] - V_pi[s]) for s in NON_TERMINALS)
    policy_agreement = all(pi_vi[s] == pi_pi[s] for s in NON_TERMINALS)
    print(f"\n--- Verification with Algorithm 1 ---")
    print(f"Policies agree across all states: {policy_agreement}")
    print(f"Maximum difference in state values: {max_diff:.2e} (< tolerance 1e-6)")

    # Exercise 1: Step reward sweep
    print("\n" + "=" * 80)
    print("EXERCISE 1A: STEP REWARD SWEEP (gamma = 0.95, p = 0.1)")
    print("=" * 80)
    for r in [-0.01, -0.04, -0.1, -0.5, -2.0]:
        V, pi, sw = value_iteration(step_r=r, gamma=0.95, p=0.1)
        print(f"R_step = {r:+5.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d}")
        print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

    # Exercise 1: Discount factor sweep
    print("\n" + "=" * 80)
    print("EXERCISE 1B: DISCOUNT FACTOR SWEEP (R_step = -0.04, p = 0.1)")
    print("=" * 80)
    for g in [0.5, 0.7, 0.9, 0.95, 0.99]:
        V, pi, sw = value_iteration(step_r=-0.04, gamma=g, p=0.1)
        print(f"gamma  = {g:5.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d}")
        print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

    # Exercise 2: Slip sweep
    print("\n" + "=" * 80)
    print("EXERCISE 2: SLIP PROBABILITY SWEEP (R_step = -0.04, gamma = 0.95)")
    print("=" * 80)
    for p in [0.0, 0.05, 0.1, 0.2, 0.3]:
        V, pi, sw = value_iteration(step_r=-0.04, gamma=0.95, p=p)
        prob_neg = compute_absorption_prob(pi, p)
        print(f"p = {p:4.2f} | V(0,0) = {V[(0,0)]:+7.4f} | Sweeps = {sw:2d} | P(reach -1) = {prob_neg:7.4f}")
        print(f"  Policy: Row 2={[pi[(c,2)] for c in range(3)]} | Row 1={[pi[(0,1)], pi[(2,1)]]} | Row 0={[pi[(c,0)] for c in range(4)]}")

