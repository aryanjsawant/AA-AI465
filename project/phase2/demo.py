"""
Live demonstration: ESC on one GSM8K question, window by window.

    python demo.py                 # first question of the subset
    python demo.py --task 7        # 8th question of the subset
    python demo.py --idx 1084      # a GSM8K test index directly
    python demo.py --seed 5        # a different sampling seed

Unlike the main experiment, which always draws the full budget so that every
method can be scored on the same samples, the demo really stops: windows that
ESC does not need are never requested. The run is written to traces/demo/.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import gsm8k      # noqa: E402
import llm        # noqa: E402
import methods    # noqa: E402

CFG = llm.CONFIG


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", type=int, default=0, help="position in the subset")
    ap.add_argument("--idx", type=int, default=None, help="GSM8K test index")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    if isinstance(llm.server_info(), dict):
        sys.exit("Model server not reachable at %s. Start it first, see README."
                 % llm.BASE_URL)

    rows = gsm8k.load_test()
    ids = gsm8k.make_subset(CFG["subset_size"], CFG["subset_seed"])
    row = rows[args.idx if args.idx is not None else ids[args.task]]
    w, L = CFG["window"], CFG["max_samples"]
    messages = llm.build_messages(row["question"])

    print("=" * 72)
    print("GSM8K test question %d" % row["idx"])
    print(row["question"])
    print("=" * 72)
    print("model %s | temperature %.1f | window %d | budget %d samples\n"
          % (CFG["model"], CFG["decoding"]["temperature"], w, L))

    rounds, candidates, answer, stopped = [], [], None, False
    for j in range(L // w):
        seeds = [args.seed * 1_000_000 + row["idx"] * 100 + j * w + i
                 for i in range(w)]
        samples, wall = llm.sample_round(messages, seeds)
        preds = [gsm8k.extract_answer(s["text"]) for s in samples]
        for s, p in zip(samples, preds):
            s["pred"] = p
        rounds.append({"round": j, "wall_s": wall, "samples": samples})
        print("window %d  answers %s  (%.1f s, %d completion tokens)"
              % (j + 1, preds, wall, sum(s["completion_tokens"] for s in samples)))
        if j == 0:
            print("\n  first sample of this window:\n    "
                  + samples[0]["text"].strip().replace("\n", "\n    ") + "\n")
        if methods.window_is_unanimous(preds):
            answer, stopped = preds[0], True
            print("  -> all %d agree: STOP" % w)
            break
        print("  -> answers differ: draw another window")
        candidates += preds
    if not stopped:
        answer = methods.vote(candidates)
        print("  -> budget spent: majority vote over all %d samples" % L)

    used = len(rounds) * w
    tokens = sum(s["completion_tokens"] for r in rounds for s in r["samples"])
    print("\nESC answer : %s" % answer)
    print("gold       : %s   (%s)" % (
        row["gold"], "correct" if gsm8k.is_correct(answer, row["gold"]) else "WRONG"))
    print("cost       : %d of %d samples, %d rounds, %d completion tokens, %.1f s"
          % (used, L, len(rounds), tokens, sum(r["wall_s"] for r in rounds)))
    print("saved      : %d samples that SC-%d would have drawn" % (L - used, L))

    out_dir = os.path.join(llm.ROOT, "traces", "demo")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "q%04d_seed%d.json" % (row["idx"], args.seed))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"idx": row["idx"], "question": row["question"],
                   "gold": row["gold"], "model": CFG["model"],
                   "decoding": CFG["decoding"], "messages": messages,
                   "rounds": rounds, "esc_answer": answer,
                   "stopped_early": stopped,
                   "created": time.strftime("%Y-%m-%d %H:%M:%S")},
                  f, indent=1, ensure_ascii=False)
    print("trace      : %s" % os.path.relpath(path, llm.ROOT))


if __name__ == "__main__":
    main()
