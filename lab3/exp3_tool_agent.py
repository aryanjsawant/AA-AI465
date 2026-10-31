"""
Experiment 3 - Tool-Using Agent (Function-Calling Pattern)

Implements the runtime half of LLM function calling:
  - a tool registry (name -> Python function)
  - a JSON schema for each tool (the artifact a real model would be shown)
  - dispatch(): parse a structured tool call, look it up in the registry,
    invoke it, and wrap the result as an observation

The "model side" is scripted here (a fixed sequence of tool calls) so the
whole contract is visible without an API key or network access.
"""

import json
import math
import os
from datetime import date

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Tools - ordinary Python functions
# ---------------------------------------------------------------------------

def calculator(expression):
    """Evaluate an arithmetic expression in a restricted namespace."""
    allowed_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "pi": math.pi,
    }
    # no builtins exposed - a plain eval(expression) would let the model
    # run arbitrary code (import os, open(...), etc.)
    code = compile(expression, "<calculator>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"use of '{name}' is not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names)


def days_between(d1, d2):
    """Whole number of days between two ISO YYYY-MM-DD dates."""
    date1 = date.fromisoformat(d1)
    date2 = date.fromisoformat(d2)
    return abs((date2 - date1).days)


_CONVERSIONS = {
    ("km", "miles"): lambda v: v * 0.621371,
    ("miles", "km"): lambda v: v / 0.621371,
    ("kg", "lb"): lambda v: v * 2.20462,
    ("lb", "kg"): lambda v: v / 2.20462,
    ("c", "f"): lambda v: v * 9 / 5 + 32,
    ("f", "c"): lambda v: (v - 32) * 5 / 9,
}


def unit_convert(value, frm, to):
    """Convert value between km/miles, kg/lb or C/F."""
    key = (frm.lower(), to.lower())
    if key not in _CONVERSIONS:
        raise ValueError(f"unsupported conversion: {frm} -> {to}")
    return _CONVERSIONS[key](value)


# ---------------------------------------------------------------------------
# Tool registry: name -> function
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "calculator": calculator,
    "days_between": days_between,
    "unit_convert": unit_convert,
}

# JSON schemas exposed to the model. Each entry gives the model everything
# it needs to *call* the tool correctly without ever seeing its Python body.
TOOL_SCHEMAS = [
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression in a restricted "
                        "namespace (sqrt, pow, pi are available).",
        "arguments": {
            "expression": {"type": "string", "description": "Arithmetic expression, e.g. 'sqrt(16) + 2'"}
        },
    },
    {
        "name": "days_between",
        "description": "Compute the whole number of days between two ISO dates.",
        "arguments": {
            "d1": {"type": "string", "description": "First date, YYYY-MM-DD"},
            "d2": {"type": "string", "description": "Second date, YYYY-MM-DD"},
        },
    },
    {
        "name": "unit_convert",
        "description": "Convert a numeric value between km/miles, kg/lb or degC/degF.",
        "arguments": {
            "value": {"type": "number", "description": "Value to convert"},
            "frm": {"type": "string", "description": "Source unit"},
            "to": {"type": "string", "description": "Target unit"},
        },
    },
]


# ---------------------------------------------------------------------------
# 2. dispatch(): parse -> look up -> invoke -> wrap as observation
# ---------------------------------------------------------------------------

def dispatch(tool_call_json):
    """
    tool_call_json: a JSON string of the form
        '{"tool": "<name>", "arguments": {...}}'
    Returns a structured observation dict.
    """
    call = json.loads(tool_call_json)          # parse
    name = call["tool"]
    args = call.get("arguments", {})

    fn = TOOL_REGISTRY[name]                   # look up
    result = fn(**args)                        # invoke

    return {                                   # wrap as observation
        "tool": name,
        "arguments": args,
        "observation": result,
    }


# ---------------------------------------------------------------------------
# Scripted "model side": a fixed sequence of tool calls
# ---------------------------------------------------------------------------

SCRIPTED_CALLS = [
    '{"tool": "calculator", "arguments": {"expression": "sqrt(144) + pow(2, 3)"}}',
    '{"tool": "days_between", "arguments": {"d1": "2026-01-01", "d2": "2026-08-20"}}',
    '{"tool": "unit_convert", "arguments": {"value": 100, "frm": "km", "to": "miles"}}',
    '{"tool": "unit_convert", "arguments": {"value": 98.6, "frm": "f", "to": "c"}}',
    '{"tool": "calculator", "arguments": {"expression": "pi * pow(3, 2)"}}',
]


def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("=== Tool schemas presented to the model ===")
    emit(json.dumps(TOOL_SCHEMAS, indent=2))
    emit()

    emit("=== Scripted tool calls and observations ===")
    for i, call_json in enumerate(SCRIPTED_CALLS, 1):
        emit(f"\n--- Call {i} ---")
        emit(f"Request : {call_json}")
        observation = dispatch(call_json)
        emit(f"Observation: {json.dumps(observation)}")

    out_path = os.path.join(OUT_DIR, "exp3_tool_agent.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n[saved output to {out_path}]")


if __name__ == "__main__":
    main()
