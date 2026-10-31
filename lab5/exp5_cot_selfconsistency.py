"""
Experiment 5 - Chain-of-Thought Reasoning and Self-Consistency by Sampling

Compares three ways of answering the same question set:
  1. Direct       - question only, temperature 0, a single trace.
  2. CoT greedy   - question + worked examples, temperature 0, a single
                    trace, always following one fixed reasoning path.
  3. CoT self-consistency - same prompt, temperature 0.7, k sampled
                    traces, extract every trace's answer and take a
                    majority vote.

The model side is scripted, as in Experiment 3: REASONERS holds, per
question, a correct step-by-step path plus one or two distinct wrong
paths a real model might plausibly take (a common arithmetic slip, a
misapplied order of operations, an off-by-one). Greedy decoding always
follows one fixed path per question (the "most natural" one for that
prompt, which for a couple of trap questions IS the wrong path, since
that is exactly how greedy CoT fails in practice). Sampling at
temperature 0.7 uses a seeded random.Random per (question, sample index)
to choose between the paths with fixed probabilities, so repeated runs
with the same seed reproduce exactly the same distribution of traces.
"""

import os
import random
import re
from collections import Counter

from questions import QUESTIONS

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

DEFAULT_K = 7
DEFAULT_SEED = 42


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

DIRECT_PROMPT = """Answer the question with only the final number. Do not
show any working.

Question: {question}
Final Answer:"""

COT_PROMPT = """Solve each question by writing your reasoning step by step,
then state the result on its own line as shown.

Example 1:
Question: A basket has 14 mangoes. 5 are given away. How many are left?
Reasoning: Start with 14 mangoes. Giving away 5 leaves 14 - 5 = 9.
Final Answer: 9

Example 2:
Question: A car travels at 40 km/h for 3 hours. How far does it go?
Reasoning: Distance = speed x time = 40 * 3 = 120.
Final Answer: 120

Example 3:
Question: A pack has 4 rows of 6 eggs. 2 eggs break. How many whole eggs
remain?
Reasoning: Total eggs = 4 * 6 = 24. Removing the 2 broken eggs leaves
24 - 2 = 22.
Final Answer: 22

Now solve this one the same way.
Question: {question}
Reasoning:"""


# ---------------------------------------------------------------------------
# Scripted reasoner: per-question correct path + wrong path(s)
# ---------------------------------------------------------------------------
# Each entry is a function reasoning_fn(path) -> (trace_text, numeric_answer)
# "path" selects which of the scripted solution strategies to render.

def _q01(path):
    if path == "correct":
        return ("Start with 23 apples. Selling 8 in the morning leaves "
                "23 - 8 = 15. Selling 6 more in the afternoon leaves "
                "15 - 6 = 9.", 9)
    # wrong: subtracts only the morning sales
    return ("Start with 23 apples. Selling 8 in the morning leaves "
            "23 - 8 = 15. The afternoon sale is a separate tally and "
            "does not change the shop's remaining stock.", 15)


def _q02(path):
    if path == "correct":
        return ("Distance = speed x time = 60 * 2.5 = 150 km.", 150)
    # wrong: rounds the time down to 2 hours first
    return ("Distance = speed x time. Rounding 2.5 hours to 2 hours for "
            "simplicity: 60 * 2 = 120 km.", 120)


def _q03(path):
    if path == "correct":
        return ("3 boxes of 12 pens give 3 * 12 = 36 pens. 2 boxes of 8 "
                "pens give 2 * 8 = 16 pens. Total = 36 + 16 = 52.", 52)
    # wrong: averages the box sizes instead of computing each group
    return ("There are 5 boxes in total, averaging (12 + 8) / 2 = 10 "
            "pens per box, so total = 5 * 10 = 50.", 50)


def _q04(path):
    if path == "correct":
        return ("Litres filled = rate x time = 15 * 8 = 120.", 120)
    # wrong: off-by-one, uses 7 minutes instead of 8
    return ("Counting the minutes as the pipe runs: after minute 1, 2, "
            "..., up to minute 7 the tank has 15 * 7 = 105 litres.", 105)


def _q05(path):
    if path == "correct":
        return ("Selling price after a 25% markup on 80 is "
                "80 * 1.25 = 100. A 25% discount on 100 is "
                "100 * 0.75 = 75.", 75)
    # wrong (the "natural" but incorrect shortcut): treats the two 25%
    # changes as cancelling out and returns the original cost price
    return ("A 25% increase followed by a 25% decrease cancels out, so "
            "the final price equals the original cost price of 80.", 80)


def _q06(path):
    if path == "correct":
        return ("5 rows of 9 chairs give 5 * 9 = 45 chairs. Removing 4 "
                "chairs leaves 45 - 4 = 41.", 41)
    # wrong: removes 4 chairs from each row instead of 4 chairs total
    return ("5 rows of 9 chairs give 5 * 9 = 45 chairs. Removing 4 "
            "chairs from every row removes 5 * 4 = 20 chairs, leaving "
            "45 - 20 = 25.", 25)


def _q07(path):
    if path == "correct":
        return ("6 full days pay 6 * 400 = 2400. Half a day pays "
                "400 / 2 = 200. Total pay = 2400 + 200 = 2600.", 2600)
    # wrong (the "natural" but incorrect shortcut): rounds the half day
    # up to a full day
    return ("6 full days plus a half day is rounded up to 7 full days, "
            "so total pay = 7 * 400 = 2800.", 2800)


def _q08(path):
    if path == "correct":
        return ("Area of a rectangle = length x width = 12 * 7 = 84 "
                "square metres.", 84)
    # wrong: adds instead of multiplying
    return ("Combining the two sides gives 12 + 7 = 19, taken as the "
            "area in square metres.", 19)


def _q09(path):
    if path == "correct":
        return ("Stations 1 through 9 are 9 points on the route. The "
                "number of gaps between consecutive stations is one "
                "fewer than the number of stations: 9 - 1 = 8.", 8)
    # wrong (the "natural" but incorrect shortcut): off-by-one, counts
    # the stations themselves as the number of gaps
    return ("There are stations numbered 1 to 9, so there are 9 "
            "stretches of road counted directly from the station "
            "numbers.", 9)


def _q10(path):
    if path == "correct":
        return ("Flour needed = 250 * 4 = 1000 grams. Subtracting the "
                "100 grams already available leaves 1000 - 100 = 900.", 900)
    # wrong: subtracts 100 grams per batch instead of once overall
    return ("Flour needed per batch after using the 100 grams available "
            "is 250 - 100 = 150 per batch, so total = 150 * 4 = 600.", 600)


REASONERS = {
    "q01": _q01, "q02": _q02, "q03": _q03, "q04": _q04, "q05": _q05,
    "q06": _q06, "q07": _q07, "q08": _q08, "q09": _q09, "q10": _q10,
}

# The path greedy (temperature 0) always takes for each question. Most
# questions greedy solves correctly; q05, q07 and q09 are deliberately
# built so that greedy's single fixed path is the plausible-but-wrong
# shortcut, matching the assignment's requirement that greedy be
# demonstrably fragile on at least a couple of questions.
GREEDY_PATH = {
    "q01": "correct", "q02": "correct", "q03": "correct", "q04": "correct",
    "q05": "wrong", "q06": "correct", "q07": "wrong", "q08": "correct",
    "q09": "wrong", "q10": "correct",
}

# Sampling distribution at temperature 0.7: probability of the correct
# path vs. the wrong path, per question. The correct path is kept as the
# plurality outcome so that self-consistency's majority vote lands on the
# right answer even for the three questions where greedy alone fails.
SAMPLE_P_CORRECT = {
    "q01": 0.85, "q02": 0.85, "q03": 0.80, "q04": 0.80, "q05": 0.60,
    "q06": 0.85, "q07": 0.65, "q08": 0.85, "q09": 0.60, "q10": 0.80,
}

# A small fixed fraction of sampled traces state their answer in a form
# extract_answer() cannot parse at all (simulating an off-prompt or
# truncated generation), so unparsable traces show up genuinely rather
# than being asserted in prose.
UNPARSABLE_RATE = 0.05


def render_trace(question_id, path, unparsable=False):
    reasoning, answer = REASONERS[question_id](path)
    if unparsable:
        return f"Reasoning: {reasoning} I believe the result speaks for itself.", None
    return f"Reasoning: {reasoning}\nFinal Answer: {answer}", answer


def generate_trace(question_id, mode, sample_index=0, seed=DEFAULT_SEED):
    """
    mode: "direct", "greedy", or "sample".
    Returns (prompt_used, trace_text, true_numeric_answer_or_None).
    """
    if mode == "direct":
        # Direct prompting skips reasoning; the scripted stand-in answers
        # from the same fixed path greedy would take, since there is no
        # worked-example prompt to steer it toward the correct one.
        path = GREEDY_PATH[question_id]
        _, answer = REASONERS[question_id](path)
        return f"Final Answer: {answer}", answer

    if mode == "greedy":
        path = GREEDY_PATH[question_id]
        trace_text, answer = render_trace(question_id, path)
        return trace_text, answer

    if mode == "sample":
        rng = random.Random(f"{seed}:{question_id}:{sample_index}")
        roll = rng.random()
        if roll < UNPARSABLE_RATE:
            trace_text, answer = render_trace(question_id, "correct", unparsable=True)
            return trace_text, answer
        p_correct = SAMPLE_P_CORRECT[question_id]
        path = "correct" if rng.random() < p_correct else "wrong"
        trace_text, answer = render_trace(question_id, path)
        return trace_text, answer

    raise ValueError(f"unknown mode: {mode}")


# ---------------------------------------------------------------------------
# extract_answer(): parse + normalise
# ---------------------------------------------------------------------------

_FINAL_ANSWER_RE = re.compile(r"Final Answer:\s*([^\n]+)", re.IGNORECASE)


def extract_answer(trace_text):
    """
    Find the "Final Answer: X" line in a trace, normalise it to a
    canonical string, and return None if no such line exists or the
    stated value cannot be parsed as a number.

    Normalisation: strip surrounding whitespace and any trailing unit
    text, parse as a float, then render as an int-looking string when
    the value is whole (e.g. "2.670" and "2.67" both become "2.67", and
    "9.0" becomes "9") so that textually different but semantically
    equal answers do not split the vote.
    """
    match = _FINAL_ANSWER_RE.search(trace_text)
    if not match:
        return None
    raw = match.group(1).strip()
    numeric_part = re.match(r"[-+]?\d+(\.\d+)?", raw)
    if not numeric_part:
        return None
    try:
        value = float(numeric_part.group(0))
    except ValueError:
        return None
    return canonical_number(value)


def canonical_number(value):
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# Voting
# ---------------------------------------------------------------------------

def majority_vote(answers):
    """
    answers: list of canonical answer strings (None entries already
    discarded by the caller). Tie-break rule: the lowest numeric value
    among the tied answers wins, so ties resolve deterministically
    regardless of dict/Counter iteration order.
    Returns (winner_or_None, Counter).
    """
    tally = Counter(answers)
    if not tally:
        return None, tally
    best_count = max(tally.values())
    tied = [a for a, c in tally.items() if c == best_count]
    winner = min(tied, key=lambda a: float(a))
    return winner, tally


# ---------------------------------------------------------------------------
# run(): the three configurations
# ---------------------------------------------------------------------------

def run(configuration, questions=QUESTIONS, k=DEFAULT_K, seed=DEFAULT_SEED, emit=print):
    """
    configuration: "direct", "cot_greedy", or "cot_self_consistency".
    Returns a dict with per-question results plus configuration-level
    accuracy, model call count and unparsable-trace count.
    """
    per_question = []
    total_calls = 0
    unparsable_count = 0
    correct_count = 0

    for q in questions:
        gold = canonical_number(q["gold"])

        if configuration == "direct":
            trace_text, _ = generate_trace(q["id"], "direct")
            total_calls += 1
            answer = extract_answer(trace_text)
            if answer is None:
                unparsable_count += 1
            is_correct = (answer == gold)
            per_question.append({
                "id": q["id"], "gold": gold, "answer": answer,
                "correct": is_correct, "tally": None,
            })
            correct_count += int(is_correct)

        elif configuration == "cot_greedy":
            trace_text, _ = generate_trace(q["id"], "greedy")
            total_calls += 1
            answer = extract_answer(trace_text)
            if answer is None:
                unparsable_count += 1
            is_correct = (answer == gold)
            per_question.append({
                "id": q["id"], "gold": gold, "answer": answer,
                "correct": is_correct, "tally": None,
                "trace": trace_text,
            })
            correct_count += int(is_correct)

        elif configuration == "cot_self_consistency":
            answers = []
            for i in range(k):
                trace_text, _ = generate_trace(q["id"], "sample", sample_index=i, seed=seed)
                total_calls += 1
                ans = extract_answer(trace_text)
                if ans is None:
                    unparsable_count += 1
                else:
                    answers.append(ans)
            winner, tally = majority_vote(answers)
            is_correct = (winner == gold)
            per_question.append({
                "id": q["id"], "gold": gold, "answer": winner,
                "correct": is_correct, "tally": tally,
            })
            correct_count += int(is_correct)

        else:
            raise ValueError(f"unknown configuration: {configuration}")

    accuracy = correct_count / len(questions)
    return {
        "configuration": configuration,
        "per_question": per_question,
        "accuracy": accuracy,
        "correct_count": correct_count,
        "num_questions": len(questions),
        "total_calls": total_calls,
        "unparsable_count": unparsable_count,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("=== Direct prompt template ===")
    emit(DIRECT_PROMPT)
    emit()
    emit("=== Chain-of-thought prompt template ===")
    emit(COT_PROMPT)
    emit()

    emit("=== Sample complete CoT trace (question q05, greedy decoding) ===")
    example_trace, _ = generate_trace("q05", "greedy")
    emit(COT_PROMPT.format(question=QUESTIONS[4]["text"]))
    emit(example_trace)
    emit()

    results = {}
    for config in ["direct", "cot_greedy", "cot_self_consistency"]:
        emit(f"=== Running configuration: {config} (k={DEFAULT_K if config == 'cot_self_consistency' else 1}, seed={DEFAULT_SEED}) ===")
        result = run(config, k=DEFAULT_K, seed=DEFAULT_SEED, emit=emit)
        results[config] = result
        for pq in result["per_question"]:
            gold_mark = "OK" if pq["correct"] else "WRONG"
            emit(f"  {pq['id']}: gold={pq['gold']}  answer={pq['answer']}  [{gold_mark}]")
            if pq.get("tally") is not None:
                tally_str = ", ".join(f"{a}:{c}" for a, c in sorted(pq["tally"].items(), key=lambda x: -x[1]))
                emit(f"        vote tally -> {tally_str}")
        emit(f"  accuracy={result['accuracy']:.2f}  "
             f"({result['correct_count']}/{result['num_questions']})  "
             f"calls={result['total_calls']}  "
             f"unparsable={result['unparsable_count']}")
        emit()

    emit("=== 3-way comparison ===")
    emit(f"{'Configuration':<24}{'Accuracy':<12}{'Calls':<10}{'Unparsable':<12}")
    for config in ["direct", "cot_greedy", "cot_self_consistency"]:
        r = results[config]
        emit(f"{config:<24}{r['accuracy']:<12.2f}{r['total_calls']:<10}{r['unparsable_count']:<12}")

    out_path = os.path.join(OUT_DIR, "exp5_cot_selfconsistency.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n[saved output to {out_path}]")


if __name__ == "__main__":
    main()
