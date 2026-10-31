"""
One-time setup for a clean checkout: fetch what is too large to commit.

    python src/download.py

    data/gsm8k_test.jsonl                      GSM8K test split (already in the repo)
    models/qwen2.5-1.5b-instruct-q4_k_m.gguf   1.1 GB model file
    bin/                                       llama.cpp CPU build for Windows x64

On Linux or macOS, install llama.cpp yourself (or use Ollama) and point
LLM_BASE_URL at its OpenAI-compatible endpoint; the model file is the same.
"""

import hashlib
import os
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GSM8K_URL = ("https://raw.githubusercontent.com/openai/grade-school-math/"
             "master/grade_school_math/data/test.jsonl")
MODEL_URL = ("https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/"
             "main/qwen2.5-1.5b-instruct-q4_k_m.gguf")
MODEL_SHA256 = "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"
LLAMA_URL = ("https://github.com/ggml-org/llama.cpp/releases/download/b11429/"
             "llama-b11429-bin-win-cpu-x64.zip")


def fetch(url, path):
    if os.path.exists(path):
        print("have", os.path.relpath(path, ROOT))
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print("downloading", url)
    urllib.request.urlretrieve(url, path + ".part")
    os.replace(path + ".part", path)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    fetch(GSM8K_URL, os.path.join(ROOT, "data", "gsm8k_test.jsonl"))

    model = os.path.join(ROOT, "models", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
    fetch(MODEL_URL, model)
    if sha256(model) != MODEL_SHA256:
        sys.exit("Model file hash differs from the one the results were "
                 "produced with. The upstream file may have changed.")
    print("model hash ok")

    if os.name == "nt":
        server = os.path.join(ROOT, "bin", "llama-server.exe")
        if not os.path.exists(server):
            archive = os.path.join(ROOT, "bin", "llama.zip")
            fetch(LLAMA_URL, archive)
            with zipfile.ZipFile(archive) as z:
                z.extractall(os.path.join(ROOT, "bin"))
            os.remove(archive)
        print("have bin/llama-server.exe")
    else:
        print("Not Windows: install llama.cpp and start llama-server yourself "
              "(see README).")


if __name__ == "__main__":
    main()
