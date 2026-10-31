"""
Step 2 of the experiment: read the traces and produce every number that is
reported. No model is called here, so this step is free and deterministic.

    python src/evaluate.py
    python src/evaluate.py --strict   # sensitivity check, see gsm8k.extract_answer

Writes to results/:
    per_question.csv   one row per (run, question, method)
    summary.csv        the main table, mean and std over runs
    summary.json       everything the plots and the report read
    table_main.md      the main table, formatted
    failure_cases.md   early stops on a wrong answer, with trace paths
    checker_audit.csv  40 random samples for checking the answer extractor
"""

import csv
import glob
import json
import os
import random
import statistics as st

import gsm8k
import llm
import methods

CFG = llm.CONFIG
W, L = CFG["window"], CFG["max_samples"]
TRACES = os.path.join(llm.ROOT, "traces")
RESULTS = os.path.join(llm.ROOT, "results")
STRICT = False   # set by --strict: marker-only answer extraction


# --- loading ---------------------------------------------------------------

def load_run(name):
    """{idx: question record} for one run directory; answers are re-extracted
    from the stored text so the checker in gsm8k.py is the single authority."""
    out = {}
    for path in sorted(glob.glob(os.path.join(TRACES, name, "q*.json"))):
        with open(path, encoding="utf-8") as f:
            t = json.load(f)
        samples = [s for r in t["rounds"] for s in r["samples"]]
        out[t["idx"]] = {
            "idx": t["idx"],
            "gold": t["gold"],
            "path": os.path.relpath(path, llm.ROOT).replace("\\", "/"),
            "preds": [gsm8k.extract_answer(s["text"], STRICT) for s in samples],
            "texts": [s["text"] for s in samples],
            "ctok": [s["completion_tokens"] for s in samples],
            "ptok": max(s["prompt_tokens"] for s in samples),
            "round_wall": [r["wall_s"] for r in t["rounds"]],
            "round_size": len(t["rounds"][0]["samples"]),
            "errors": sum(1 for s in samples if s["error"]),
        }
    return out


def cost(q, n, rounds):
    """Cost of a strategy that used the first n samples in `rounds` requests.

    prompt tokens : the prompt is sent once per request and shared by the
                    samples of that request (the accounting of ESC, Table 7).
    latency       : time this machine took to produce the first n samples,
                    from the measured wall-clock time of each sampling round;
                    a partly used round is charged in proportion.
    """
    size = q["round_size"]
    full, part = divmod(n, size)
    latency = sum(q["round_wall"][:full])
    if part:
        latency += q["round_wall"][full] * part / size
    return {"samples": n, "rounds": rounds,
            "prompt_tokens": q["ptok"] * rounds,
            "completion_tokens": sum(q["ctok"][:n]),
            "latency_s": latency}


def record(q, answer, n, rounds):
    return {"answer": answer, "correct": gsm8k.is_correct(answer, q["gold"]),
            **cost(q, n, rounds)}


# --- strategies ------------------------------------------------------------

def strategies(k_matched):
    table = {"SC-%d" % k: (lambda q, k=k: methods.sc(q["preds"], k))
             for k in range(1, L + 1)}
    table["ESC (w=%d, L=%d)" % (W, L)] = lambda q: methods.esc(q["preds"], W, L)
    table["AC (Beta 0.95, L=%d)" % L] = \
        lambda q: methods.adaptive_consistency(q["preds"], L)
    for w in (2, 3, 4, 10):
        table["ESC w=%d" % w] = lambda q, w=w: methods.esc(q["preds"], w, L)
    return table


def mean_std(xs):
    return (st.mean(xs), st.stdev(xs) if len(xs) > 1 else 0.0)


METRICS = ["correct", "samples", "rounds", "prompt_tokens",
           "completion_tokens", "latency_s"]


def aggregate(per_run_rows):
    """per_run_rows: {run: [record per question]} -> mean and std over runs
    of each metric's per-question mean."""
    out = {}
    for m in METRICS:
        per_run = [st.mean(float(r[m]) for r in rows)
                   for rows in per_run_rows.values()]
        if m == "correct":
            per_run = [100 * x for x in per_run]
        out[m] = mean_std(per_run)
        out[m + "_runs"] = per_run
    return out


def random_stop_accuracy(run, esc_rows, seed, n_perm=500):
    """Ablation of the stopping rule: keep ESC's budgets, discard its signal.

    ESC's per-question sample counts are shuffled across questions, so the
    total budget and its spread are untouched but which question gets how
    many samples no longer depends on the answers. Each question is then
    answered by SC with the count it was handed. Averaged over n_perm
    shuffles.
    """
    rng = random.Random(seed)
    ids = sorted(run)
    budgets = [esc_rows[i]["samples"] for i in ids]
    accs = []
    for _ in range(n_perm):
        rng.shuffle(budgets)
        hits = [gsm8k.is_correct(methods.sc(run[i]["preds"], b)[0], run[i]["gold"])
                for i, b in zip(ids, budgets)]
        accs.append(100 * st.mean(hits))
    return st.mean(accs)


# --- main ------------------------------------------------------------------

def main():
    os.makedirs(RESULTS, exist_ok=True)
    runs = {s: load_run("run_%d" % s) for s in CFG["run_seeds"]}
    greedy = load_run("greedy")
    # Only questions finished in every run are scored, so all runs and all
    # methods cover the same task set.
    ids = sorted(set.intersection(*[set(r) for r in runs.values()], set(greedy)))
    runs = {s: {i: r[i] for i in ids} for s, r in runs.items()}
    n_q = len(ids)
    print("questions scored: %d, runs: %d" % (n_q, len(runs)))

    esc_name = "ESC (w=%d, L=%d)" % (W, L)
    table = strategies(None)
    rows = {name: {s: {i: record(run[i], *fn(run[i])) for i in ids}
                   for s, run in runs.items()}
            for name, fn in table.items()}
    agg = {name: aggregate({s: list(r.values()) for s, r in per.items()})
           for name, per in rows.items()}

    # Matched budget: SC with the same number of samples as ESC used on
    # average, rounded down and rounded up.
    esc_mean = agg[esc_name]["samples"][0]
    k_lo, k_hi = int(esc_mean), min(L, int(esc_mean) + 1)

    # Greedy chain of thought (temperature 0, deterministic: one run).
    g_rows = [record(greedy[i], greedy[i]["preds"][0], 1, 1) for i in ids]
    g = {m: st.mean(float(r[m]) for r in g_rows) for m in METRICS}
    g["correct"] *= 100

    # Stopping-rule ablation.
    rand = [random_stop_accuracy(runs[s], rows[esc_name][s], seed=s)
            for s in runs]

    # Paired differences, computed inside each run and then averaged.
    def paired(a, b):
        return mean_std([x - y for x, y in zip(agg[a]["correct_runs"],
                                               agg[b]["correct_runs"])])

    diffs = {
        "ESC - SC-%d (matched, floor)" % k_lo: paired(esc_name, "SC-%d" % k_lo),
        "ESC - SC-%d (matched, ceil)" % k_hi: paired(esc_name, "SC-%d" % k_hi),
        "ESC - SC-%d (full budget)" % L: paired(esc_name, "SC-%d" % L),
        "ESC - random stopping": mean_std(
            [x - y for x, y in zip(agg[esc_name]["correct_runs"], rand)]),
    }

    # How ESC behaves: where it stops and how often a stop is right.
    stop_stats = {}
    for j in list(range(L // W)) + [None]:
        n = hit = 0
        for s, run in runs.items():
            for i in ids:
                if methods.esc_stop_round(run[i]["preds"], W, L) == j:
                    n += 1
                    hit += rows[esc_name][s][i]["correct"]
        key = "no stop" if j is None else "window %d" % (j + 1)
        stop_stats[key] = {"share": 100 * n / (n_q * len(runs)),
                           "accuracy": 100 * hit / n if n else None, "n": n}
    agree = mean_std([100 * st.mean(
        rows[esc_name][s][i]["answer"] == rows["SC-%d" % L][s][i]["answer"]
        for i in ids) for s in runs])

    all_preds = [p for run in runs.values() for q in run.values()
                 for p in q["preds"]]
    all_tok = [t for run in runs.values() for q in run.values()
               for t in q["ctok"]]
    sample_acc = mean_std([100 * st.mean(
        gsm8k.is_correct(p, q["gold"]) for q in run.values() for p in q["preds"])
        for run in runs.values()])

    # ---- files ----
    with open(os.path.join(RESULTS, "per_question.csv"), "w", newline="",
              encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["run", "idx", "gold", "method", "answer"] + METRICS)
        for i, r in zip(ids, g_rows):
            wr.writerow(["greedy", i, greedy[i]["gold"], "CoT greedy",
                         r["answer"]] + [round(float(r[m]), 3) for m in METRICS])
        for name, per in rows.items():
            for s, r in per.items():
                for i in ids:
                    wr.writerow([s, i, runs[s][i]["gold"], name, r[i]["answer"]]
                                + [round(float(r[i][m]), 3) for m in METRICS])

    sc_ks = sorted({1, W, k_lo, k_hi, 10, 15, L})
    main_methods = ["SC-%d" % k for k in sc_ks] + [
        esc_name, "AC (Beta 0.95, L=%d)" % L]
    header = ["method", "accuracy_mean", "accuracy_std", "samples", "rounds",
              "prompt_tokens", "completion_tokens", "total_tokens",
              "latency_s_mean", "latency_s_std"]
    table_rows = [["CoT greedy (T=0)", g["correct"], "", 1, 1,
                   g["prompt_tokens"], g["completion_tokens"],
                   g["prompt_tokens"] + g["completion_tokens"],
                   g["latency_s"], ""]]
    for name in main_methods:
        a = agg[name]
        table_rows.append([name, a["correct"][0], a["correct"][1],
                           a["samples"][0], a["rounds"][0],
                           a["prompt_tokens"][0], a["completion_tokens"][0],
                           a["prompt_tokens"][0] + a["completion_tokens"][0],
                           a["latency_s"][0], a["latency_s"][1]])
    e = agg[esc_name]
    table_rows.append(["Random stopping (ablation)", st.mean(rand),
                       st.stdev(rand), e["samples"][0], e["rounds"][0],
                       e["prompt_tokens"][0], "", "", "", ""])
    with open(os.path.join(RESULTS, "summary.csv"), "w", newline="",
              encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        for r in table_rows:
            wr.writerow([round(x, 2) if isinstance(x, float) else x for x in r])

    def fmt(x, d=1):
        return "" if x == "" else ("%." + str(d) + "f") % x

    lines = ["| Method | Accuracy % (mean ± std) | Samples | Rounds | "
             "Prompt tok | Completion tok | Total tok | Latency s |",
             "|---|---|---|---|---|---|---|---|"]
    for r in table_rows:
        acc = fmt(r[1]) + (" ± " + fmt(r[2]) if r[2] != "" else "")
        lat = fmt(r[8]) + (" ± " + fmt(r[9]) if r[9] != "" else "")
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r[0], acc, fmt(r[3], 2), fmt(r[4], 2), fmt(r[5], 0), fmt(r[6], 0),
            fmt(r[7], 0), lat))
    lines += ["", "Paired accuracy differences (percentage points, mean ± std "
              "over runs):", ""]
    lines += ["- %s: %+.2f ± %.2f" % (k, v[0], v[1]) for k, v in diffs.items()]
    with open(os.path.join(RESULTS, "table_main.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))

    # Failure cases: ESC stopped early on a wrong unanimous window.
    cases = []
    for s, run in runs.items():
        for i in ids:
            q = run[i]
            j = methods.esc_stop_round(q["preds"], W, L)
            if j is not None and not rows[esc_name][s][i]["correct"]:
                cases.append((s, i, j, q))
    with open(os.path.join(RESULTS, "failure_cases.md"), "w",
              encoding="utf-8") as f:
        f.write("# ESC early stops on a wrong answer\n\n"
                "%d of %d early stops were wrong.\n\n"
                % (len(cases), sum(v["n"] for k, v in stop_stats.items()
                                   if k != "no stop")))
        for s, i, j, q in cases:
            sc_full = rows["SC-%d" % L][s][i]
            f.write("## run %d, question %d (stopped in window %d)\n\n"
                    "- trace: `%s`\n- gold: %s\n- all %d answers: %s\n"
                    "- SC-%d answer: %s (%s)\n\nFirst sample of the stopping "
                    "window:\n\n```\n%s\n```\n\n"
                    % (s, i, j + 1, q["path"], q["gold"], L, q["preds"], L,
                       sc_full["answer"],
                       "correct" if sc_full["correct"] else "wrong",
                       q["texts"][j * W].strip()))

        # The other way to fail: no window is ever unanimous and the final
        # vote is wrong. Listed where it happened in every run, i.e. where
        # the model is wrong on the question rather than unlucky.
        always_wrong = [i for i in ids
                        if not any(rows[esc_name][s][i]["correct"] for s in runs)]
        f.write("# Questions ESC answered wrong in every run\n\n"
                "%d of %d questions.\n\n" % (len(always_wrong), n_q))
        for i in always_wrong:
            s = CFG["run_seeds"][0]
            q = runs[s][i]
            answer = rows[esc_name][s][i]["answer"]
            tally = sorted(((q["preds"].count(p), p) for p in set(q["preds"])),
                           key=lambda t: -t[0])
            wrong = next((t for t, p in zip(q["texts"], q["preds"])
                          if p == answer), q["texts"][0])
            f.write("## question %d\n\n- trace: `%s`\n- gold: %s\n"
                    "- ESC answers per run: %s\n- answer tally in run %d "
                    "(count x answer): %s\n- ESC samples used in run %d: %d\n\n"
                    "A sample giving the voted answer:\n\n```\n%s\n```\n\n"
                    % (i, q["path"], q["gold"],
                       [rows[esc_name][r][i]["answer"] for r in runs], s,
                       ", ".join("%dx %s" % t for t in tally), s,
                       rows[esc_name][s][i]["samples"], wrong.strip()))

    # Audit sheet for the answer checker.
    rng = random.Random(CFG["subset_seed"])
    pool = [(s, i, n) for s in runs for i in ids for n in range(L)]
    audit_path = os.path.join(RESULTS, "checker_audit.csv")
    labels = {}   # hand labels already filled in are carried over
    if os.path.exists(audit_path):
        with open(audit_path, newline="", encoding="utf-8") as f:
            labels = {(r["trace"], r["sample_index"]): r["hand_label"]
                      for r in csv.DictReader(f)}
    with open(audit_path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["trace", "sample_index", "gold", "reply_tail",
                     "extracted", "checker_says_correct", "hand_label"])
        for s, i, n in rng.sample(pool, min(40, len(pool))):
            q = runs[s][i]
            wr.writerow([q["path"], n, q["gold"],
                         q["texts"][n].strip()[-220:].replace("\n", " / "),
                         q["preds"][n],
                         int(gsm8k.is_correct(q["preds"][n], q["gold"])),
                         labels.get((q["path"], str(n)), "")])

    summary = {
        "n_questions": n_q, "runs": list(runs), "window": W, "max_samples": L,
        "esc_name": esc_name, "k_matched": [k_lo, k_hi],
        "greedy": g, "agg": agg, "random_stop_runs": rand, "diffs": diffs,
        "stop_stats": stop_stats, "esc_sc_agreement": agree,
        "sample_accuracy": sample_acc,
        "unparsed_pct": 100 * all_preds.count(None) / len(all_preds),
        "call_errors": sum(q["errors"] for run in runs.values()
                           for q in run.values()),
        "mean_completion_tokens_per_sample": st.mean(all_tok),
        "prompt_tokens_mean": st.mean(q["ptok"] for q in runs[CFG["run_seeds"][0]].values()),
        "total_samples": len(all_preds),
        "total_completion_tokens": sum(all_tok),
        "total_sampling_seconds": sum(w for run in runs.values()
                                      for q in run.values()
                                      for w in q["round_wall"]),
        "failure_cases": len(cases),
        "always_wrong": len(always_wrong),
        "esc_samples_per_question": {
            str(s): [rows[esc_name][s][i]["samples"] for i in ids] for s in runs},
        "first_window_agreement": {
            str(s): [max(run[i]["preds"][:W].count(p) for p in set(run[i]["preds"][:W]))
                     if any(p is not None for p in run[i]["preds"][:W]) else 0
                     for i in ids] for s, run in runs.items()},
    }
    with open(os.path.join(RESULTS, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("\nstop statistics:", json.dumps(stop_stats, indent=1))
    print("ESC/SC-%d agreement: %.1f ± %.1f" % (L, *agree))
    print("per-sample accuracy: %.1f ± %.1f, unparsed %.1f%%"
          % (*sample_acc, summary["unparsed_pct"]))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="count a reply without an answer marker as no answer; "
                         "writes to results/strict/")
    if ap.parse_args().strict:
        STRICT = True
        RESULTS = os.path.join(RESULTS, "strict")
    main()
