"""
Experiment 5 - Exercises

Exercise 1: Sweep k over {1, 3, 5, 9, 15}, repeating each setting with
five different seeds, and report mean accuracy and total model calls per
k. State the k beyond which accuracy stops improving appreciably and the
calls spent per correct answer at that point.

Exercise 2: Add an abstention rule to the self-consistency vote: answer
only if the winning answer's vote count leads the runner-up by at least
`margin` votes; otherwise abstain. Report coverage and accuracy-on-
answered-subset for two margins.
"""

import os

from questions import QUESTIONS
from exp5_cot_selfconsistency import (
    generate_trace,
    extract_answer,
    majority_vote,
    canonical_number,
    DEFAULT_SEED,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Exercise 1: sweep k, multiple seeds
# ---------------------------------------------------------------------------

K_VALUES = [1, 3, 5, 9, 15]
SEEDS = [11, 22, 33, 44, 55]


def run_self_consistency(questions, k, seed):
    """Same logic as run('cot_self_consistency', ...) in the main script,
    factored out here so the sweep can call it once per (k, seed) pair
    without re-importing run() and re-deriving the config name."""
    correct_count = 0
    total_calls = 0
    unparsable_count = 0
    for q in questions:
        gold = canonical_number(q["gold"])
        answers = []
        for i in range(k):
            trace_text, _ = generate_trace(q["id"], "sample", sample_index=i, seed=seed)
            total_calls += 1
            ans = extract_answer(trace_text)
            if ans is None:
                unparsable_count += 1
            else:
                answers.append(ans)
        winner, _tally = majority_vote(answers)
        if winner == gold:
            correct_count += 1
    accuracy = correct_count / len(questions)
    return accuracy, total_calls, unparsable_count


def run_exercise1(emit):
    emit(f"k values: {K_VALUES}")
    emit(f"seeds per k: {SEEDS}")
    emit()

    summary = []
    for k in K_VALUES:
        accuracies = []
        calls_per_seed = []
        for seed in SEEDS:
            acc, calls, unparsable = run_self_consistency(QUESTIONS, k, seed)
            accuracies.append(acc)
            calls_per_seed.append(calls)
            emit(f"  k={k:<3} seed={seed:<4} accuracy={acc:.2f}  calls={calls}  unparsable={unparsable}")
        mean_acc = sum(accuracies) / len(accuracies)
        total_calls = sum(calls_per_seed)
        summary.append((k, mean_acc, total_calls))
        emit(f"  -> k={k}: mean accuracy over {len(SEEDS)} seeds = {mean_acc:.3f}, "
             f"total model calls across those seeds = {total_calls}")
        emit()

    emit("=== Summary: mean accuracy and total calls per k ===")
    emit(f"{'k':<6}{'mean accuracy':<16}{'total calls':<14}")
    for k, mean_acc, total_calls in summary:
        emit(f"{k:<6}{mean_acc:<16.3f}{total_calls:<14}")
    emit()

    # Identify the k beyond which accuracy stops improving appreciably:
    # the first k whose mean accuracy is within 0.01 of the best mean
    # accuracy achieved by any larger or equal k in the sweep.
    best_acc = max(a for _, a, _ in summary)
    plateau_k = None
    for k, mean_acc, total_calls in summary:
        if best_acc - mean_acc <= 0.01:
            plateau_k = k
            plateau_calls = total_calls
            plateau_correct = mean_acc * len(QUESTIONS)
            break
    emit(f"Accuracy plateaus (within 0.01 of the best mean accuracy "
         f"{best_acc:.3f}) starting at k={plateau_k}.")
    calls_per_correct = plateau_calls / plateau_correct
    emit(f"At k={plateau_k}: total calls (summed over {len(SEEDS)} seeds) = "
         f"{plateau_calls}, mean correct answers per seed = "
         f"{plateau_correct:.2f}/{len(QUESTIONS)}, "
         f"so calls spent per correct answer (single seed) = "
         f"{plateau_k * len(QUESTIONS) / plateau_correct:.2f}.")


# ---------------------------------------------------------------------------
# Exercise 2: abstention by vote margin
# ---------------------------------------------------------------------------
# Margin is defined as an absolute vote-count difference between the
# winning answer and the runner-up (votes, not a fraction of k): the
# system answers only if winner_votes - runnerup_votes >= margin.
# A question with only one distinct extracted answer has no runner-up,
# treated as a runner-up count of 0, so it always clears any margin
# tested here (a unanimous vote is the strongest possible signal).

MARGINS = [1, 2]


def vote_with_abstention(tally, margin):
    if not tally:
        return None, "abstain"
    ranked = sorted(tally.items(), key=lambda x: -x[1])
    winner, winner_votes = ranked[0]
    runnerup_votes = ranked[1][1] if len(ranked) > 1 else 0
    if winner_votes - runnerup_votes >= margin:
        return winner, "answered"
    return None, "abstain"


def run_exercise2(emit, k=7, seed=DEFAULT_SEED):
    emit(f"Margin definition: absolute vote-count lead of the winner over "
         f"the runner-up (winner_votes - runnerup_votes >= margin). "
         f"k={k}, seed={seed}.")
    emit()

    for margin in MARGINS:
        emit(f"--- margin={margin} ---")
        answered = 0
        correct_on_answered = 0
        for q in QUESTIONS:
            gold = canonical_number(q["gold"])
            answers = []
            for i in range(k):
                trace_text, _ = generate_trace(q["id"], "sample", sample_index=i, seed=seed)
                ans = extract_answer(trace_text)
                if ans is not None:
                    answers.append(ans)
            _winner_plain, tally = majority_vote(answers)
            decision, status = vote_with_abstention(tally, margin)
            if status == "answered":
                answered += 1
                is_correct = (decision == gold)
                correct_on_answered += int(is_correct)
                mark = "OK" if is_correct else "WRONG"
                emit(f"  {q['id']}: tally={dict(tally)}  -> ANSWERED {decision}  gold={gold}  [{mark}]")
            else:
                emit(f"  {q['id']}: tally={dict(tally)}  -> ABSTAIN  gold={gold}")

        coverage = answered / len(QUESTIONS)
        acc_on_answered = (correct_on_answered / answered) if answered else float("nan")
        emit(f"  coverage={coverage:.2f} ({answered}/{len(QUESTIONS)})  "
             f"accuracy_on_answered={acc_on_answered:.2f} "
             f"({correct_on_answered}/{answered})" if answered else
             f"  coverage={coverage:.2f} ({answered}/{len(QUESTIONS)})  "
             f"accuracy_on_answered=n/a (nothing answered)")
        emit()


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("=== Exercise 1: sweep k over {1, 3, 5, 9, 15}, 5 seeds each ===")
    run_exercise1(emit)

    emit()
    emit("=== Exercise 2: abstention by vote margin ===")
    run_exercise2(emit)

    out_path = os.path.join(OUT_DIR, "exp5_exercises.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[saved output to {out_path}]")


if __name__ == "__main__":
    main()
