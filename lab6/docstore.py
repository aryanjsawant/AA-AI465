"""
Document store, tools and task set for Experiment 6.

Ten short model notes, each carrying a model name, a benchmark, an accuracy
and a parameter count. Two pairs of titles nearly duplicate each other
("Orion-7B benchmark note" vs "Orion-7B benchmark note (old)", and
"Vega-13B evaluation" vs "Vega-13B evaluation draft"), so that search()
returns an ambiguous hit list and a careless reader can cite the stale
twin instead of the current note. That is the fault the Reviewer exists
to catch.

The three tools are the only way a role may touch the store.
"""

DOCS = {
    "d01": {
        "title": "Orion-7B benchmark note",
        "model": "Orion-7B",
        "benchmark": "MMLU",
        "accuracy": 62.4,
        "params_b": 7.0,
        "stale": False,
        "text": "Orion-7B scores 62.4 on MMLU at 7.0B parameters. "
                "Current figures, re-run this quarter.",
    },
    "d02": {
        "title": "Orion-7B benchmark note (old)",
        "model": "Orion-7B",
        "benchmark": "MMLU",
        "accuracy": 58.1,
        "params_b": 7.0,
        "stale": True,
        "text": "Orion-7B scores 58.1 on MMLU at 7.0B parameters. "
                "Superseded by the current note; retained for history.",
    },
    "d03": {
        "title": "Vega-13B evaluation",
        "model": "Vega-13B",
        "benchmark": "MMLU",
        "accuracy": 68.9,
        "params_b": 13.0,
        "stale": False,
        "text": "Vega-13B scores 68.9 on MMLU at 13.0B parameters. "
                "Signed off by the evaluation team.",
    },
    "d04": {
        "title": "Vega-13B evaluation draft",
        "model": "Vega-13B",
        "benchmark": "MMLU",
        "accuracy": 71.2,
        "params_b": 13.0,
        "stale": True,
        "text": "Vega-13B scores 71.2 on MMLU at 13.0B parameters. "
                "Unreviewed draft figures, not for citation.",
    },
    "d05": {
        "title": "Lyra-3B benchmark note",
        "model": "Lyra-3B",
        "benchmark": "MMLU",
        "accuracy": 49.7,
        "params_b": 3.0,
        "stale": False,
        "text": "Lyra-3B scores 49.7 on MMLU at 3.0B parameters.",
    },
    "d06": {
        "title": "Cygnus-30B benchmark note",
        "model": "Cygnus-30B",
        "benchmark": "MMLU",
        "accuracy": 74.5,
        "params_b": 30.0,
        "stale": False,
        "text": "Cygnus-30B scores 74.5 on MMLU at 30.0B parameters.",
    },
    "d07": {
        "title": "Draco-1B benchmark note",
        "model": "Draco-1B",
        "benchmark": "MMLU",
        "accuracy": 38.2,
        "params_b": 1.3,
        "stale": False,
        "text": "Draco-1B scores 38.2 on MMLU at 1.3B parameters.",
    },
    "d08": {
        "title": "Perseus-20B benchmark note",
        "model": "Perseus-20B",
        "benchmark": "MMLU",
        "accuracy": 70.1,
        "params_b": 20.0,
        "stale": False,
        "text": "Perseus-20B scores 70.1 on MMLU at 20.0B parameters.",
    },
    "d09": {
        "title": "Altair-8B benchmark note",
        "model": "Altair-8B",
        "benchmark": "MMLU",
        "accuracy": 64.8,
        "params_b": 8.0,
        "stale": False,
        "text": "Altair-8B scores 64.8 on MMLU at 8.0B parameters.",
    },
    "d10": {
        "title": "Rigel-5B benchmark note",
        "model": "Rigel-5B",
        "benchmark": "MMLU",
        "accuracy": 55.3,
        "params_b": 5.0,
        "stale": False,
        "text": "Rigel-5B scores 55.3 on MMLU at 5.0B parameters.",
    },
}

# The note that should be cited for each model: the one that is not stale.
CANONICAL_DOC = {d["model"]: doc_id for doc_id, d in DOCS.items()
                 if not d["stale"]}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
# Each tool returns plain data and counts its own calls, so the orchestrator
# can report tool use per role without the tools knowing who called them.

TOOL_CALLS = {"search": 0, "read_doc": 0, "calculator": 0}


def reset_tool_calls():
    for name in TOOL_CALLS:
        TOOL_CALLS[name] = 0


def search(query):
    """Return every doc id whose title or model name mentions the query.
    Near-duplicate titles mean a model name matches two notes."""
    TOOL_CALLS["search"] += 1
    q = query.lower()
    return [doc_id for doc_id, d in sorted(DOCS.items())
            if q in d["title"].lower() or q in d["model"].lower()]


def read_doc(doc_id):
    """Return the stored record for one document id."""
    TOOL_CALLS["read_doc"] += 1
    return DOCS.get(doc_id)


def calculator(expression):
    """Evaluate a arithmetic expression over numeric literals only."""
    TOOL_CALLS["calculator"] += 1
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError("calculator refuses non-numeric expression")
    return eval(expression, {"__builtins__": {}}, {})


TOOLS = {"search": search, "read_doc": read_doc, "calculator": calculator}


# ---------------------------------------------------------------------------
# Task set
# ---------------------------------------------------------------------------
# Eight comparison tasks. Each asks which of two models scores higher on
# MMLU and by how much; the gold answer is derived from the canonical
# (non-stale) notes, so citing a stale twin yields the wrong number.

TASKS = [
    {"id": "t1", "a": "Orion-7B", "b": "Vega-13B"},
    {"id": "t2", "a": "Lyra-3B", "b": "Cygnus-30B"},
    {"id": "t3", "a": "Orion-7B", "b": "Altair-8B"},
    {"id": "t4", "a": "Draco-1B", "b": "Rigel-5B"},
    {"id": "t5", "a": "Vega-13B", "b": "Perseus-20B"},
    {"id": "t6", "a": "Cygnus-30B", "b": "Perseus-20B"},
    {"id": "t7", "a": "Altair-8B", "b": "Rigel-5B"},
    {"id": "t8", "a": "Lyra-3B", "b": "Draco-1B"},
]


def gold(task):
    """The checklist target for one task: the winner, the accuracy gap and
    the two documents that must be cited."""
    da = DOCS[CANONICAL_DOC[task["a"]]]
    db = DOCS[CANONICAL_DOC[task["b"]]]
    winner = da["model"] if da["accuracy"] >= db["accuracy"] else db["model"]
    gap = round(abs(da["accuracy"] - db["accuracy"]), 1)
    return {
        "winner": winner,
        "gap": gap,
        "sources": sorted([CANONICAL_DOC[task["a"]], CANONICAL_DOC[task["b"]]]),
    }


def question(task):
    return ("Which of %s and %s scores higher on MMLU, and by how many "
            "points?" % (task["a"], task["b"]))
