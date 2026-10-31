"""
Small fixed corpus for Experiment 4 (Retrieval-Augmented Generation).

Four short documents on related but distinct topics, checked into
docs/ as plain .txt files, so that TF-IDF retrieval has real signal to
work with and questions outside the corpus have no chunk that
legitimately matches.
"""

import os

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

DOC_NAMES = ["doc1_bfs.txt", "doc2_ucs.txt", "doc3_tfidf.txt", "doc4_rag.txt"]


def _load(name):
    with open(os.path.join(DOCS_DIR, name), encoding="utf-8") as f:
        return f.read().strip()


DOCUMENTS = {name: _load(name) for name in DOC_NAMES}
