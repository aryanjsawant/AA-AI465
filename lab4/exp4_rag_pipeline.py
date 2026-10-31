"""
Experiment 4 - Retrieval-Augmented Generation

Implements the retrieval half of a RAG pipeline completely and scripts the
generation step, so the whole pipeline is visible without an API key or
network access:

  1. Chunking    - split each document into overlapping sentence windows,
                   tagging each chunk with its source and position.
  2. Vectorising - TF-IDF over the corpus vocabulary (stop words removed).
  3. Indexing    - keep the TF-IDF matrix as the vector store (exhaustive
                   search, no approximate index).
  4. Retrieval   - cosine-similarity top-k chunks for a query.
  5. Context     - assemble a grounded prompt: instruction + cited chunks
     assembly     + question.
  6. Generation  - a scripted stand-in for the model that answers only from
                   the retrieved chunks, plus an ungrounded baseline that
                   answers from a tiny fixed "parametric memory" instead.
"""

import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from corpus import DOCUMENTS

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

DEFAULT_CHUNK_SIZE = 2     # sentences per chunk
DEFAULT_OVERLAP = 1        # sentences of overlap between consecutive chunks


# ---------------------------------------------------------------------------
# 1. Chunking
# ---------------------------------------------------------------------------

def split_sentences(text):
    """Naive sentence splitter: split on '.', drop empties, keep no trailing dot."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_document(name, text, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    """Return a list of chunk dicts: {source, position, text}."""
    sentences = split_sentences(text)
    step = max(chunk_size - overlap, 1)
    chunks = []
    pos = 0
    i = 0
    while i < len(sentences):
        window = sentences[i:i + chunk_size]
        if not window:
            break
        chunks.append({
            "source": name,
            "position": pos,
            "text": " ".join(window),
        })
        pos += 1
        if i + chunk_size >= len(sentences):
            break
        i += step
    return chunks


def build_chunks(documents=DOCUMENTS, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    chunks = []
    for name, text in documents.items():
        chunks.extend(chunk_document(name, text, chunk_size, overlap))
    return chunks


# ---------------------------------------------------------------------------
# 2 & 3. Vectorisation + indexing (the "vector store")
# ---------------------------------------------------------------------------

class VectorStore:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform([c["text"] for c in chunks])

    def search(self, query, k=3):
        """Return the top-k (chunk, score) pairs for a query, best first."""
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self.chunks[i], float(scores[i])) for i in ranked[:k]]


# ---------------------------------------------------------------------------
# 5. Context assembly
# ---------------------------------------------------------------------------

def assemble_context(retrieved):
    """Build the grounded prompt text from retrieved (chunk, score) pairs."""
    lines = ["Answer the question using ONLY the context below. "
             "Cite the source tag you used.", ""]
    for chunk, score in retrieved:
        tag = f"[{chunk['source']}#{chunk['position']}]"
        lines.append(f"{tag} (score={score:.3f}): {chunk['text']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. Generation - scripted stand-ins
# ---------------------------------------------------------------------------
# A real model would read the assembled context and produce these answers;
# here they are scripted so the retrieval step is what's being measured.

GROUNDED_ANSWERS = {
    "What data structure does breadth-first search use for its frontier?":
        "A FIFO queue [doc1_bfs.txt#0].",
    "How does uniform-cost search decide a node's cost is final?":
        "A node's cost is final only when it is popped from the priority "
        "queue, since any cheaper path would already have been popped "
        "[doc2_ucs.txt#0].",
    "What does the inverse document frequency part of TF-IDF do?":
        "It down-weights words that appear in many documents, since common "
        "words carry little distinguishing information [doc3_tfidf.txt#0].",
    "Why can a RAG system be updated without retraining the model?":
        "Because the corpus lives outside the model's weights, in an "
        "external document store that can be edited directly "
        "[doc4_rag.txt#3].",
}

# Deliberately unanswerable from this corpus (used again in Exercise 1).
UNANSWERABLE_QUESTIONS = [
    "What is the time complexity of quicksort in the worst case?",
    "Who invented the transformer architecture?",
]

BASELINE_PARAMETRIC_MEMORY = {
    "What data structure does breadth-first search use for its frontier?":
        "A queue (this is common textbook knowledge, no source).",
    "How does uniform-cost search decide a node's cost is final?":
        "When it is dequeued from the priority queue (recalled from "
        "training data, no source).",
    "What does the inverse document frequency part of TF-IDF do?":
        "It penalises common words (recalled from training data, no source).",
    "Why can a RAG system be updated without retraining the model?":
        "Because you just edit the documents (recalled from training data, "
        "no source).",
    "What is the time complexity of quicksort in the worst case?":
        "O(n^2) in the worst case (recalled from training data, no source; "
        "not grounded in this corpus).",
    "Who invented the transformer architecture?":
        "Researchers at Google introduced it in 'Attention Is All You Need' "
        "(recalled from training data, no source; not grounded in this "
        "corpus).",
}


def ungrounded_answer(question):
    """The same question answered with no retrieval at all."""
    return BASELINE_PARAMETRIC_MEMORY.get(
        question, "I don't know (no parametric memory scripted for this question).")


def grounded_answer(question, retrieved):
    """Scripted 'model' that only ever repeats a pre-written cited answer."""
    return GROUNDED_ANSWERS.get(
        question,
        "The retrieved context does not contain an answer to this question.")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

QUERIES = list(GROUNDED_ANSWERS.keys()) + UNANSWERABLE_QUESTIONS


def run_pipeline(k=3, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP, emit=print):
    chunks = build_chunks(chunk_size=chunk_size, overlap=overlap)
    store = VectorStore(chunks)

    emit(f"Indexed {len(chunks)} chunks from {len(DOCUMENTS)} documents "
         f"(chunk_size={chunk_size} sentences, overlap={overlap} sentences).")
    emit()

    for q in QUERIES:
        emit(f"=== Query: {q} ===")
        retrieved = store.search(q, k=k)
        for rank, (chunk, score) in enumerate(retrieved, 1):
            emit(f"  rank {rank}: [{chunk['source']}#{chunk['position']}] "
                 f"score={score:.3f}  \"{chunk['text']}\"")

        context = assemble_context(retrieved)
        emit("  --- assembled context (truncated) ---")
        for line in context.splitlines()[:2]:
            emit(f"  {line}")
        emit("  ...")

        emit(f"  GROUNDED answer   : {grounded_answer(q, retrieved)}")
        emit(f"  UNGROUNDED answer : {ungrounded_answer(q)}")
        emit()

    return chunks, store


def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    run_pipeline(k=3, emit=emit)

    out_path = os.path.join(OUT_DIR, "exp4_rag_pipeline.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[saved output to {out_path}]")


if __name__ == "__main__":
    main()
