"""
Thin client for a local OpenAI-compatible chat endpoint (llama.cpp
`llama-server`, or Ollama's /v1 endpoint).

Only the standard library is used, so there is nothing to install for the
client side. One *round* is a set of n samples drawn for the same prompt at
the same time: the n requests are sent concurrently, each with its own seed,
and the round's wall-clock time is measured around the whole set. This is the
unit ESC calls a sampling window.
"""

import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as f:
    CONFIG = json.load(f)

# The endpoint is the only thing read from the environment. No API key is
# needed for a local server; LLM_API_KEY is sent only if it is set.
BASE_URL = os.environ.get("LLM_BASE_URL", CONFIG["base_url"]).rstrip("/")
API_KEY = os.environ.get("LLM_API_KEY", "")


def load_prompt(name):
    with open(os.path.join(ROOT, "prompts", name), encoding="utf-8") as f:
        return f.read().strip()


SYSTEM_PROMPT = load_prompt("system.txt")
USER_TEMPLATE = load_prompt("cot_user.txt")
FEWSHOT = json.loads(load_prompt("fewshot.json"))


def build_messages(question):
    """System message, the worked examples as earlier chat turns, then the task."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in FEWSHOT:
        messages.append({"role": "user",
                         "content": USER_TEMPLATE.format(question=ex["question"])})
        messages.append({"role": "assistant", "content": ex["answer"]})
    messages.append({"role": "user",
                     "content": USER_TEMPLATE.format(question=question)})
    return messages


def _post(payload, timeout):
    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 **({"Authorization": "Bearer " + API_KEY} if API_KEY else {})},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def complete(messages, seed, temperature=None, retries=3):
    """One model call. Returns a dict that is written to the trace as is.

    A failed call is retried with a short back-off; if it still fails the
    error is returned in the record (text = "") instead of raising, so one
    bad request costs one unparsable sample, not the whole run.
    """
    dec = CONFIG["decoding"]
    payload = {
        "model": CONFIG["model"],
        "messages": messages,
        "temperature": dec["temperature"] if temperature is None else temperature,
        "top_p": dec["top_p"],
        "top_k": dec["top_k"],
        "min_p": dec["min_p"],
        "repeat_penalty": dec["repeat_penalty"],
        "max_tokens": dec["max_tokens"],
        "seed": seed,
    }
    last_error = None
    for attempt in range(retries):
        t0 = time.perf_counter()
        try:
            out = _post(payload, timeout=CONFIG["request_timeout_s"])
            choice = out["choices"][0]
            usage = out.get("usage", {})
            return {
                "seed": seed,
                "text": choice["message"]["content"] or "",
                "finish_reason": choice.get("finish_reason"),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "latency_s": round(time.perf_counter() - t0, 3),
                "error": None,
            }
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError,
                ConnectionError) as e:
            last_error = repr(e)
            time.sleep(2 * (attempt + 1))
    return {"seed": seed, "text": "", "finish_reason": "error",
            "prompt_tokens": 0, "completion_tokens": 0, "latency_s": 0.0,
            "error": last_error}


def sample_round(messages, seeds, temperature=None):
    """Draw len(seeds) samples concurrently. Returns (samples, wall_seconds)."""
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(seeds)) as pool:
        samples = list(pool.map(
            lambda s: complete(messages, s, temperature), seeds))
    return samples, round(time.perf_counter() - t0, 3)


def server_info():
    """Model identity as reported by the server, stored with every run."""
    try:
        req = urllib.request.Request(BASE_URL + "/models")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("id") for m in data.get("data", [])]
    except Exception as e:  # server down: the caller reports it and stops
        return {"error": repr(e)}
