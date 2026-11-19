# Lab 2: Deliberative Goal-Based Agents with Search

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements deliberative goal-based agents using classical graph search algorithms in grid-world navigation:
1. **Breadth-First Search (BFS) Agent**: Explores state spaces level-by-level to guarantee the shortest path in unweighted uniform-cost grids.
2. **Uniform Cost Search (UCS) Agent**: Dijkstra-based state expansion handling weighted terrain costs (e.g., mud cells $c=5$, gravel $c=2$, open floor $c=1$).
3. **Dynamic Replanning Agent**: Detects unforeseen obstacle appearance during execution, invalidates obsolete path prefixes, and replans online from the current agent coordinate.
4. **Hybrid Reflex-Deliberative Agent**: Combines low-latency reactive reflex rules (instant local collision avoidance) with global deliberative path replanning.

---

## Directory Contents

| File | Description |
|---|---|
| `exp2_bfs_agent.py` | Baseline grid-world navigation using BFS queue-based frontier expansion. |
| `exp2_ex1_uniform_cost.py` | Priority-queue driven UCS agent finding minimum-cost paths across heterogeneous terrain. |
| `exp2_ex2_replan.py` | Dynamic environment replanning simulation when static maps encounter live blocked cells. |
| `exp2_ex3_hybrid.py` | Two-layer architecture: reactive collision reflex + deliberative global pathfinder. |
| `make_plots.py` | Generates grid maps, search trees, and cost comparison charts. |
| `make_animation.py` | Produces step-by-step navigation visualizations. |
| `make_report.py` | Compiles the full report with embedded figures into `LAB_2_U23AI042.doc`. |
| `LAB_2_U23AI042.doc` | Final laboratory report submission deliverable. |
| `outputs/` | Contains search trace logs (`.txt`), path coordinates, and metric summaries. |

---

## How to Run

```bash
# Run search simulations
python exp2_bfs_agent.py
python exp2_ex1_uniform_cost.py
python exp2_ex2_replan.py
python exp2_ex3_hybrid.py

# Generate visual outputs and compile deliverable
python make_plots.py
python make_animation.py
python make_report.py
```
