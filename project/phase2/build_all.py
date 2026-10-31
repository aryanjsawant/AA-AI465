"""
Everything after sampling, in one command: tables, figures, report, slides
and the submission archive. No model is needed.

    python build_all.py
"""

import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ROLL = "U23AI042"
ARCHIVE = os.path.join(os.path.dirname(ROOT), "RP2_%s.zip" % ROLL)

STEPS = [
    ["src/evaluate.py"],
    ["src/evaluate.py", "--strict"],
    ["src/plots.py"],
    ["report/build_report.py"],
    ["report/build_slides.py"],
]

# Left out of the archive: the 1.1 GB model and the llama.cpp binaries
# (src/download.py fetches both), caches, and Office lock files.
SKIP_DIRS = {"models", "bin", "__pycache__"}


def main():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for step in STEPS:
        print("\n>>> python " + " ".join(step), flush=True)
        subprocess.run([sys.executable] + step, cwd=ROOT, env=env, check=True)

    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name.startswith(("~$", "_")) or name.endswith(".part"):
                    continue
                path = os.path.join(folder, name)
                z.write(path, os.path.join("RP2_%s" % ROLL,
                                           os.path.relpath(path, ROOT)))
    print("\nwrote %s (%.1f MB)" % (ARCHIVE, os.path.getsize(ARCHIVE) / 1e6))


if __name__ == "__main__":
    main()
