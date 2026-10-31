"""
Step 1 of the experiment: draw the samples and write the traces.

For every question of the subset and every run seed, the model is sampled in
sequential rounds of `window` samples until `max_samples` have been drawn.
This is exactly what ESC does when it never stops early, so one pool of
samples per (run, question) serves every method: SC-k reads the first k
samples, ESC reads whole rounds until its stopping rule fires, and so on.
All methods therefore see the same model, prompt, decoding settings and
samples, and differ only in the rule that decides when to stop.

One JSON trace is written per (run, question). The sampler is resumable:
a finished trace is skipped, so an interrupted run can simply be
started again.

    python src/sample.py              # all runs, whole subset
    python src/sample.py --limit 5    # first 5 questions only (smoke test)
"""

import argparse
import json
import os
import sys
import time

import gsm8k
import llm

CFG = llm.CONFIG
TRACES = os.path.join(llm.ROOT, "traces")


def sample_seed(run_seed, idx, sample_index):
    """A distinct, reproducible seed for every sample of every run."""
    return run_seed * 1_000_000 + idx * 100 + sample_index


def annotate(sample, sample_index, gold):
    sample["sample_index"] = sample_index
    sample["pred"] = gsm8k.extract_answer(sample["text"])
    sample["correct"] = gsm8k.is_correct(sample["pred"], gold)
    return sample


def run_question(row, run_seed):
    """Sampled chain-of-thought: max_samples drawn in rounds of `window`."""
    messages = llm.build_messages(row["question"])
    w, L = CFG["window"], CFG["max_samples"]
    rounds = []
    for r in range(L // w):
        seeds = [sample_seed(run_seed, row["idx"], r * w + j) for j in range(w)]
        samples, wall = llm.sample_round(messages, seeds)
        if wall > CFG["max_round_s"]:
            # The machine was suspended or stalled mid-round. The samples are
            # fine but the timing is not, so the round is drawn again.
            samples, wall = llm.sample_round(messages, seeds)
        rounds.append({
            "round": r,
            "wall_s": wall,
            "samples": [annotate(s, r * w + j, row["gold"])
                        for j, s in enumerate(samples)],
        })
    return {"messages": messages, "rounds": rounds}


def run_greedy(row):
    """Baseline: one chain-of-thought call at temperature 0."""
    messages = llm.build_messages(row["question"])
    samples, wall = llm.sample_round(messages, [0], temperature=0.0)
    return {"messages": messages,
            "rounds": [{"round": 0, "wall_s": wall,
                        "samples": [annotate(samples[0], 0, row["gold"])]}]}


def write_trace(path, row, run_name, body, temperature):
    record = {
        "idx": row["idx"],
        "question": row["question"],
        "gold": row["gold"],
        "run": run_name,
        "model": CFG["model"],
        "runtime": CFG["runtime"],
        "decoding": {**CFG["decoding"], "temperature": temperature},
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        **body,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)  # never leave a half-written trace behind


def keep_awake():
    """Ask Windows not to sleep while the job runs (no-op elsewhere)."""
    if os.name == "nt":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def is_complete(path):
    """A trace counts as done only if it exists and no round stalled."""
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        rounds = json.load(f)["rounds"]
    return all(r["wall_s"] <= CFG["max_round_s"] for r in rounds)


def main():
    keep_awake()
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="only the first N questions of the subset")
    args = ap.parse_args()

    info = llm.server_info()
    if isinstance(info, dict):
        sys.exit("Model server not reachable at %s (%s). Start it first, see "
                 "README." % (llm.BASE_URL, info["error"]))
    print("server models:", info)

    rows = gsm8k.load_test()
    ids = gsm8k.make_subset(CFG["subset_size"], CFG["subset_seed"])[:args.limit]
    run_dirs = {s: os.path.join(TRACES, "run_%d" % s) for s in CFG["run_seeds"]}
    greedy_dir = os.path.join(TRACES, "greedy")
    for d in list(run_dirs.values()) + [greedy_dir]:
        os.makedirs(d, exist_ok=True)

    t0 = time.time()
    # Questions in the outer loop: if the job is cut short, every finished
    # question already has all its runs.
    for n, idx in enumerate(ids, 1):
        row = rows[idx]
        name = "q%04d.json" % idx
        path = os.path.join(greedy_dir, name)
        if not is_complete(path):
            write_trace(path, row, "greedy", run_greedy(row), 0.0)
        for seed, d in run_dirs.items():
            path = os.path.join(d, name)
            if is_complete(path):
                continue
            write_trace(path, row, "run_%d" % seed, run_question(row, seed),
                        CFG["decoding"]["temperature"])
        print("[%d/%d] q%04d done, %.1f min elapsed"
              % (n, len(ids), idx, (time.time() - t0) / 60), flush=True)


if __name__ == "__main__":
    main()
