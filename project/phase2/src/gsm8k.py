"""
GSM8K loading, the fixed task subset, and the answer checker.

The checker is plain code, not an LLM judge: GSM8K answers are single
numbers, so exact match after normalisation is enough. Its agreement with
hand labels is checked separately (see results/checker_audit.csv).
"""

import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

_NUM = r"-?\d[\d,]*(?:\.\d+)?"


def load_test():
    path = os.path.join(DATA, "gsm8k_test.jsonl")
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            rows.append({"idx": i, "question": r["question"],
                         "gold": normalise(r["answer"].split("####")[-1])})
    return rows


def make_subset(size, seed):
    """Draw the subset once and store it; later calls read the stored file."""
    path = os.path.join(DATA, "subset_ids.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)["ids"]
    # A prefix of one seeded shuffle, so a larger subset extends a smaller one.
    order = list(range(len(load_test())))
    random.Random(seed).shuffle(order)
    ids = order[:size]
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"benchmark": "GSM8K test", "seed": seed, "ids": ids}, f)
    return ids


def normalise(s):
    """'$1,200.00' -> '1200', ' 3.50 ' -> '3.5'. None if there is no number."""
    m = re.search(_NUM, str(s))
    if not m:
        return None
    x = float(m.group(0).replace(",", ""))
    return str(int(x)) if x == int(x) else repr(round(x, 6))


def extract_answer(text, strict=False):
    """The answer a reply commits to, as a normalised number string.

    1. The number after the last answer marker. The prompt asks for
       "Final answer: <number>"; "the answer is <number>" is accepted too.
    2. If there is no marker, the last number in the reply, which is the
       usual convention for scoring GSM8K. About one reply in seven from
       this model forgets the marker line, so without this step a correct
       solution would often count as no answer.

    strict=True switches step 2 off; evaluate.py reports both readings.
    None means no answer was found. Such a sample never matches gold and
    never matches another sample, so it cannot make a window unanimous.
    """
    hits = re.findall(r"(?:final answer|answer is)[^\d\-\n]{0,15}(" + _NUM + ")",
                      text, flags=re.IGNORECASE)
    if hits:
        return normalise(hits[-1])
    if strict:
        return None
    numbers = re.findall(r"(?<![\w.])" + _NUM, text)
    return normalise(numbers[-1]) if numbers else None


def is_correct(pred, gold):
    return pred is not None and pred == gold
