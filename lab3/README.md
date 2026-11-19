# Lab 3: Tool-Using Agent with External Computation

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements an autonomous tool-augmented agent capable of interacting with deterministic computational tools and APIs to overcome the mathematical and factual limitations of pure language models:
1. **Tool Schema & Registry**: Structured tool definitions with strict parameter validation and type schemas.
2. **Deterministic Dispatcher**: Action parser that routes user queries to appropriate tools (e.g., arithmetic calculator, CSV data analyzer, unit converter).
3. **Execution Safety & Limits**: Exception handling, boundary checking, and recursion budget controls to prevent infinite tool-call loops.
4. **Tool Use Loop**: Multi-turn reasoning loop interleaving Thought $\rightarrow$ Action $\rightarrow$ Observation $\rightarrow$ Final Response.

---

## Directory Contents

| File | Description |
|---|---|
| `exp3_tool_agent.py` | Core agent loop implementing tool selection, dispatch, and response synthesis. |
| `exp3_exercises.py` | Advanced exercises: error recovery, malformed parameter handling, multi-tool chained queries. |
| `sample_temperatures.csv` | Weather and temperature tabular dataset used for data analysis tool execution. |
| `make_report.py` | Compiles the formatted report with output traces into `LAB_3_U23AI042.doc`. |
| `LAB_3_U23AI042.doc` | Final laboratory report deliverable. |
| `outputs/` | Contains detailed execution logs and tool interaction transcripts. |

---

## How to Run

```bash
# Run tool-using agent
python exp3_tool_agent.py
python exp3_exercises.py

# Generate report
python make_report.py
```
