"""
Role specifications, the structured message format and validate().

The specification is data, not prose: each role carries its goal, the tools
it may call, the roles it may message and the fields its output must
contain. validate() is the orchestrator-side check that turns those three
lists from a request in a prompt into a rule, and every rejection is
recorded as a role violation.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Role specifications (Table 1 of the manual)
# ---------------------------------------------------------------------------

ROLES = {
    "Manager": {
        "goal": "Decompose the task, delegate it, route revisions and "
                "deliver the final answer to the user.",
        "system_prompt": "You are the Manager. Split the comparison task "
                         "into a research subtask and a writing subtask, "
                         "delegate each, route any revision to the role "
                         "named by the Reviewer, and deliver the approved "
                         "draft. You hold no tools; never read documents "
                         "yourself.",
        "tools": [],
        "may_send_to": ["Researcher", "Writer", "Reviewer", "User"],
        "output_fields": ["subtasks"],
    },
    "Researcher": {
        "goal": "Find both models, read their current notes and compute "
                "the accuracy gap.",
        "system_prompt": "You are the Researcher. Use search() to locate "
                         "each model's note, read_doc() to read it and "
                         "calculator() to compute the gap. Prefer the "
                         "current note over any superseded or draft twin. "
                         "Report values, sources and result to the Manager "
                         "only.",
        "tools": ["search", "read_doc", "calculator"],
        "may_send_to": ["Manager"],
        "output_fields": ["values", "sources", "result"],
    },
    "Writer": {
        "goal": "Turn the finding into a cited answer of at most 60 words.",
        "system_prompt": "You are the Writer. Write at most 60 words "
                         "stating the winner and the gap, citing both "
                         "document ids given to you. You hold no tools; "
                         "write only from the finding you are handed.",
        "tools": [],
        "may_send_to": ["Manager"],
        "output_fields": ["draft", "citations"],
    },
    "Reviewer": {
        "goal": "Re-read the cited sources and check values, winner and "
                "citations.",
        "system_prompt": "You are the Reviewer. Re-read each cited "
                         "document with read_doc() and check the stated "
                         "values, the winner, the citations and the word "
                         "limit. Return approve, or revise naming the role "
                         "responsible. You may not edit the draft.",
        "tools": ["read_doc"],
        "may_send_to": ["Manager"],
        "output_fields": ["verdict", "reasons"],
    },
}

# The generalist holds every tool, may talk to anyone, and its single
# merged prompt asks for all three jobs at once. It is specified here in
# the same shape purely so the same validate() can be pointed at it.
GENERALIST = {
    "goal": "Answer the comparison task end to end.",
    "system_prompt": "You are a helpful assistant. Find both models, read "
                     "their notes, compute the gap, write at most 60 words "
                     "citing both sources, and check your own work.",
    "tools": ["search", "read_doc", "calculator"],
    "may_send_to": ["User"],
    "output_fields": ["draft", "citations"],
}


# ---------------------------------------------------------------------------
# Structured message format
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """One structured message. The payload carries the role's required
    output fields; everything else is envelope."""
    sender: str
    recipient: str
    task_id: str
    intent: str                     # assign | report | review | deliver
    payload: dict = field(default_factory=dict)

    def render(self):
        keys = ", ".join(sorted(self.payload)) or "-"
        return ("%-10s -> %-10s [%-7s] %s" %
                (self.sender, self.recipient, self.intent, keys))


# ---------------------------------------------------------------------------
# validate(): the enforcement point
# ---------------------------------------------------------------------------

class Violations:
    """Collects role violations. One instance per run."""

    def __init__(self):
        self.records = []

    def log(self, role, kind, detail):
        self.records.append({"role": role, "kind": kind, "detail": detail})

    def count(self):
        return len(self.records)

    def by_role(self):
        out = {}
        for r in self.records:
            out[r["role"]] = out.get(r["role"], 0) + 1
        return out

    def by_kind(self):
        out = {}
        for r in self.records:
            out[r["kind"]] = out.get(r["kind"], 0) + 1
        return out


def validate(role_name, spec, violations, *, tool=None, message=None,
             output=None, enforce=True):
    """
    The single check every tool call, message and output passes through.

    Rejects a tool call outside the role's permitted tools, a message to a
    role it may not send to, and an output missing a required field. Each
    rejection is logged as a role violation and, when enforce is True,
    refused by returning False.

    enforce=False logs the same violation but allows the action through,
    which is how Exercise 2 measures what a prompt-only permission is
    worth.
    """
    ok = True

    if tool is not None and tool not in spec["tools"]:
        violations.log(role_name, "tool",
                       "called %s(), not permitted" % tool)
        ok = False

    if message is not None and message.recipient not in spec["may_send_to"]:
        violations.log(role_name, "recipient",
                       "messaged %s, not permitted" % message.recipient)
        ok = False

    if output is not None:
        missing = [f for f in spec["output_fields"] if f not in output]
        if missing:
            violations.log(role_name, "schema",
                           "output missing %s" % ", ".join(missing))
            ok = False

    return ok if enforce else True
