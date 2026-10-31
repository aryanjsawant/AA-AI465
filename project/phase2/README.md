# AI465 Research Project, Phase 2 (U23AI042)

**Objective (approved in Phase 1).** To evaluate early-stopping self-consistency
(ESC; window 5, at most 20 samples) for arithmetic word problems on a fixed
random subset of 50 questions from the GSM8K test set (1,319 questions), using
the open-weight Qwen2.5-1.5B-Instruct model run locally, compared against
fixed-size self-consistency (SC) at a matched sample budget, measured by
exact-match accuracy and by samples, tokens, sequential rounds and wall-clock
latency per question, each reported as mean and standard deviation over three
seeded runs.

Primary paper: Li et al., *Escape Sky-high Cost: Early-stopping
Self-Consistency for Multi-step Reasoning*, ICLR 2024 (arXiv:2401.10480).

## What is in this folder

| Path | What it is |
|---|---|
| `config.json` | Pinned configuration: model, decoding settings, subset, seeds, window, budget |
| `prompts/` | Every prompt as a file: `system.txt`, `fewshot.json`, `cot_user.txt` |
| `data/gsm8k_test.jsonl`, `data/subset_ids.json` | Benchmark and the fixed subset |
| `src/llm.py` | Client for the local model server (standard library only) |
| `src/gsm8k.py` | Data loading, subset, answer extraction, exact match |
| `src/methods.py` | SC, ESC, Adaptive-Consistency: the stopping rules |
| `src/sample.py` | Step 1: draws the samples, writes one trace per (run, question) |
| `src/evaluate.py` | Step 2: traces to tables (no model calls) |
| `src/plots.py` | Step 3: tables to figures |
| `demo.py` | Live ESC on one question |
| `traces/` | Full traces of the reported runs: prompt, every sample, tokens, timing |
| `results/` | `per_question.csv`, `summary.csv`, `table_main.md`, `failure_cases.md`, `checker_audit.csv`, `summary.json` |
| `figures/` | The four figures of the report |
| `report/` | Report and slides, and the scripts that build them |

## Environment

- Windows 11, Python 3.12, CPU only (4 cores, 16 GB RAM). No GPU, no API key.
- Model: `qwen2.5-1.5b-instruct-q4_k_m.gguf` from
  <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF>
  (sha256 `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`).
- Runtime: llama.cpp `llama-server`, build b11429 (commit d81235049), CPU x64.
- Decoding: temperature 0.7, top-p 0.9, top-k off, min-p 0, repeat penalty 1.0,
  at most 256 new tokens. Greedy baseline: temperature 0.
- Seeds: run seeds 11, 22, 33; each sample gets the seed
  `run * 1,000,000 + question * 100 + sample index`. Subset seed 465.
- Runs made on 6 October 2026.

Environment variables: none are required. `LLM_BASE_URL` overrides the server
address (default `http://127.0.0.1:8088/v1`), and `LLM_API_KEY` is sent as a
bearer token only if it is set, for use with a remote OpenAI-compatible
endpoint. No key is stored in this repository.

## Install

```
pip install -r requirements.txt     # only needed for figures and the report
python src/download.py              # model file (1.1 GB) and llama.cpp into models/ and bin/
```

## Reproduce

```
start_server.bat                    # terminal 1: leave running
python src/sample.py                # terminal 2: step 1, writes traces/
python build_all.py                 # steps 2 and 3, report, slides and the zip
python demo.py --task 6             # live demo on one question
```

Good demo questions: `--task 6` (an early stop on the right answer),
`--task 42` (GSM8K question 99, which often stops early on a wrong answer) and
`--task 3` (never stops, uses the whole budget).

`build_all.py` runs these in order; each can also be run on its own:

```
python src/evaluate.py              # step 2: writes results/  (Table 1, failure cases)
python src/evaluate.py --strict     # same with the strict checker, to results/strict/
python src/plots.py                 # step 3: writes figures/  (Figures 1 to 4)
python report/build_report.py       # report PDF (needs Word)
python report/build_slides.py       # slides (needs PowerPoint)
```

| Output | Command |
|---|---|
| Table 1 (`results/table_main.md`, `summary.csv`) | `python src/evaluate.py` |
| Figures 1 to 4 (`figures/*.png`) | `python src/plots.py` |
| Failure cases (`results/failure_cases.md`) | `python src/evaluate.py` |

Steps 2 and 3 read only the saved traces, so the whole result table
regenerates from this checkout in a few seconds with no model at all.

Step 1 is the expensive part: 50 questions x 3 runs x 20 samples = 3,000
sampled generations plus 50 greedy calls, about 0.3M completion tokens and
0.25M prompt tokens. On the laptop above the reported run took 3.2 hours of wall-clock time
(3.1 hours of generation) with other programs open, and cost nothing. `sample.py` is resumable: finished
traces are skipped, so it can be stopped and started again. Use
`python src/sample.py --limit 3` for a five-minute smoke test.

Sampling is seeded, but llama.cpp does not promise bit-identical output across
machines or thread counts, so a fresh step 1 will give slightly different
samples. The saved traces are the record of the reported numbers.

## How the comparison is kept fair

For every (run, question) the model is sampled in four sequential rounds of
five until 20 samples exist. Every method then reads from that one pool: SC-k
takes the first k samples, ESC reads whole rounds until its rule fires. The
model, prompt, decoding settings and samples are identical across methods; the
only thing that differs is the rule that decides when to stop.

- **Matched budget.** SC is evaluated at every k from 1 to 20; the matched
  baseline is SC at ESC's average sample count, rounded down and up.
- **Ablation.** Random stopping: ESC's per-question sample counts are shuffled
  across questions, so the budget is the same but no longer informed by the
  answers. This isolates the stopping signal.
- **Cost.** Samples, sequential rounds, prompt tokens (one prompt per round,
  shared by its samples), completion tokens, and latency from the measured
  wall-clock time of each round.
- **Judging.** No LLM judge. GSM8K answers are numbers, so the checker is
  exact match in code (`src/gsm8k.py`); `results/checker_audit.csv` holds 40
  random samples for checking it by hand.

## What is mine and what is borrowed

Written for this project: everything in `src/`, `demo.py`, `prompts/`,
`report/*.py`. The three worked examples in `prompts/fewshot.json` are my own
and are not taken from GSM8K.

Borrowed, unmodified:
- llama.cpp (inference server): <https://github.com/ggml-org/llama.cpp>
- Qwen2.5-1.5B-Instruct GGUF weights: <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF>
- GSM8K: <https://github.com/openai/grade-school-math>

Re-implemented from the papers' descriptions, not copied from their code:
ESC (Algorithm 1 of Li et al., 2024) and the Beta stopping rule of
Adaptive-Consistency (Aggarwal et al., 2023), both in `src/methods.py`.

AI assistance: an AI coding assistant (Claude) was used to write and debug
the code and to draft the report.
