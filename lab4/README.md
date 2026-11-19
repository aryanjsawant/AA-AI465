# Lab 4: Retrieval-Augmented Generation (RAG) Pipeline Agent

**Course:** Agentic AI (IA462) — Semester VIII  
**Institution:** SVNIT Surat, Department of Artificial Intelligence  
**Student:** Aryan Sawant (Roll No: `U23AI042`)

---

## Overview & Objectives
This experiment implements a grounded Retrieval-Augmented Generation (RAG) pipeline to mitigate hallucinations and anchor language generation to a local document corpus:
1. **Document Ingestion & Chunking**: Sliding-window chunking with configurable overlap over multi-topic technical documents.
2. **Vector Space Indexing**: Term Frequency-Inverse Document Frequency (TF-IDF) embedding matrix and vocabulary mapping.
3. **Similarity Search**: Cosine similarity scoring over query and chunk vectors to retrieve top-$k$ relevant passages.
4. **Context Grounding & Provenance**: Strict citation tracking requiring the agent to identify the exact document and line provenance for every factual claim.

---

## Directory Contents

| File / Folder | Description |
|---|---|
| `corpus.py` | Document loader and preprocessor for text documents. |
| `docs/` | Source corpus containing technical notes (`doc1_bfs.txt`, `doc2_ucs.txt`, etc.). |
| `exp4_rag_pipeline.py` | Full RAG pipeline: chunker, TF-IDF vectorizer, retriever, synthesizer. |
| `exp4_exercises.py` | Ablation experiments: chunk size impact, cosine threshold filtering, query rewrites. |
| `make_report.py` | Compiles the formatted report with output traces into `LAB_4_U23AI042.doc`. |
| `LAB_4_U23AI042.doc` | Final laboratory report deliverable. |
| `outputs/` | Contains retrieval logs, top-$k$ ranked chunks, and synthesis transcripts. |

---

## How to Run

```bash
# Run RAG pipeline and exercises
python exp4_rag_pipeline.py
python exp4_exercises.py

# Generate report
python make_report.py
```
