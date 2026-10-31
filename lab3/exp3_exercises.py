"""
Experiment 3 - Exercises

Exercise 1: Harden dispatch() so malformed JSON, an unknown tool name, a
wrong argument name and an exception raised inside a tool each produce a
structured error observation instead of crashing.

Exercise 2: Register a fourth tool, csv_mean, that reads a CSV file and
returns the mean of a named column.
"""

import csv
import json
import os

from exp3_tool_agent import TOOL_REGISTRY, TOOL_SCHEMAS, calculator, days_between, unit_convert

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Exercise 2: a fourth tool - csv_mean
# ---------------------------------------------------------------------------

def csv_mean(path, column):
    """Read a CSV file and return the mean of a named numeric column."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise KeyError(f"column '{column}' not found in {path}")
        values = [float(row[column]) for row in reader if row[column] != ""]
    if not values:
        raise ValueError(f"column '{column}' has no numeric values")
    return sum(values) / len(values)


TOOL_REGISTRY_EXT = dict(TOOL_REGISTRY)
TOOL_REGISTRY_EXT["csv_mean"] = csv_mean

TOOL_SCHEMAS_EXT = TOOL_SCHEMAS + [
    {
        "name": "csv_mean",
        "description": "Read a CSV file and return the mean of a named column.",
        "arguments": {
            "path": {"type": "string", "description": "Path to the CSV file"},
            "column": {"type": "string", "description": "Name of the numeric column to average"},
        },
    }
]


# ---------------------------------------------------------------------------
# Exercise 1: hardened dispatch with structured error observations
# ---------------------------------------------------------------------------

def dispatch_safe(tool_call_raw, registry=TOOL_REGISTRY_EXT, schemas=TOOL_SCHEMAS_EXT):
    """
    Same contract as dispatch(), but never raises. On any failure it
    returns {"error": {"type": ..., "message": ...}} instead of an
    "observation" key, so the loop can keep going.
    """
    # 1. malformed JSON
    try:
        call = json.loads(tool_call_raw)
    except json.JSONDecodeError as e:
        return {"request": tool_call_raw, "error": {"type": "malformed_json", "message": str(e)}}

    name = call.get("tool")
    args = call.get("arguments", {})

    # 2. unknown tool name
    if name not in registry:
        return {"request": call, "error": {"type": "unknown_tool", "message": f"'{name}' is not registered"}}

    # 3. wrong argument name
    schema = next(s for s in schemas if s["name"] == name)
    expected_args = set(schema["arguments"].keys())
    given_args = set(args.keys())
    unexpected = given_args - expected_args
    missing = expected_args - given_args
    if unexpected or missing:
        return {
            "request": call,
            "error": {
                "type": "bad_arguments",
                "message": f"unexpected={sorted(unexpected)} missing={sorted(missing)}",
            },
        }

    # 4. exception raised inside the tool
    fn = registry[name]
    try:
        result = fn(**args)
    except Exception as e:
        return {
            "request": call,
            "error": {"type": f"tool_exception:{type(e).__name__}", "message": str(e)},
        }

    return {"request": call, "arguments": args, "observation": result}


# ---------------------------------------------------------------------------
# Demonstration calls: one of each error kind, plus the csv_mean success case
# ---------------------------------------------------------------------------

DEMO_CALLS = [
    # malformed JSON (missing closing brace)
    '{"tool": "calculator", "arguments": {"expression": "sqrt(9)"}',
    # unknown tool name
    '{"tool": "weather_lookup", "arguments": {"city": "Surat"}}',
    # wrong argument name (should be "expression", not "expr")
    '{"tool": "calculator", "arguments": {"expr": "1 + 1"}}',
    # exception raised inside a tool (unsupported conversion)
    '{"tool": "unit_convert", "arguments": {"value": 10, "frm": "km", "to": "kg"}}',
]


SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_temperatures.csv")


def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("=== Exercise 1: structured error handling ===")
    for i, call in enumerate(DEMO_CALLS, 1):
        emit(f"\n--- Demo {i} ---")
        emit(f"Request : {call}")
        result = dispatch_safe(call)
        emit(f"Result  : {json.dumps(result)}")

    emit("\n=== Exercise 2: csv_mean tool ===")
    csv_path = SAMPLE_CSV_PATH
    emit(f"Using sample CSV at {csv_path}")

    schema_entry = next(s for s in TOOL_SCHEMAS_EXT if s["name"] == "csv_mean")
    emit(f"Schema  : {json.dumps(schema_entry)}")

    call = json.dumps({"tool": "csv_mean", "arguments": {"path": csv_path, "column": "temperature"}})
    emit(f"Request : {call}")
    result = dispatch_safe(call)
    emit(f"Result  : {json.dumps(result)}")

    out_path = os.path.join(OUT_DIR, "exp3_exercises.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n[saved output to {out_path}]")


if __name__ == "__main__":
    main()
