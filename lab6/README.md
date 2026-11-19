# Lab 6: Multi-Agent Collaboration and Role-Based Systems

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements multi-agent architectures where specialized LLM agents collaborate, critique, and refine complex task deliverables:
1. **Persona & Role Specialization**:
   - **Planner**: Decomposes high-level instructions into structured task DAGs.
   - **Researcher**: Queries the local knowledge base (`docstore.py`) to gather domain facts and evidence.
   - **Synthesizer**: Integrates research findings into a cohesive draft solution.
   - **Critic**: Evaluates candidate drafts against rigor, accuracy, and completeness rubrics, returning actionable revision feedback.
2. **Workflow Topologies**:
   - *Sequential Pipeline*: Linear handoff ($\text{Planner} \rightarrow \text{Researcher} \rightarrow \text{Synthesizer} \rightarrow \text{Critic}$).
   - *Iterative Refinement Loop*: Cyclic debate between Synthesizer and Critic until convergence criteria or round limits are satisfied.
3. **Communication Overhead**: Quantifying token consumption, round count, and quality gains compared to single-agent baselines.

---

## Directory Contents

| File | Description |
|---|---|
| `roles.py` | System prompts, behavioral guidelines, and interfaces for each agent role. |
| `docstore.py` | In-memory document retrieval store supporting researcher lookups. |
| `exp6_role_agents.py` | Orchestration engine executing multi-agent debate and refinement loops. |
| `exp6_exercises.py` | Ablation studies: impact of critic strictness and communication round bounds. |
| `make_plots.py` | Generates interaction flow diagrams, convergence curves, and token cost charts. |
| `make_report.py` | Compiles the formatted report with figures into `LAB_6_U23AI042.doc`. |
| `LAB_6_U23AI042.doc` | Final laboratory report deliverable. |
| `outputs/` | Contains multi-agent conversation transcripts and final artifacts. |

---

## How to Run

```bash
# Run multi-agent orchestrator
python exp6_role_agents.py
python exp6_exercises.py

# Generate plots and compile report
python make_plots.py
python make_report.py
```
