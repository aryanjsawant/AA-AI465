"""
Experiment 6 - Role-Based LLM Agent Design with Structured Message Passing

Compares a four-role team (Manager, Researcher, Writer, Reviewer) coordinated
through structured messages and an enforcing validate() against a single
generalist agent holding every tool and one merged prompt.

The model side is scripted, as in Experiments 3 and 5: each role is a
function that does its job but commits named faults at stated rates, drawn
from a random.Random seeded per (seed, task, role) so a run reproduces
exactly. A real LLM changes only those functions.

Faults, and who is meant to catch them:
  stale_source  Researcher cites the superseded twin note       -> Reviewer
  gap_slip      Researcher mis-computes the gap by 0.1          -> Reviewer
  drop_source   Writer cites only one of the two documents      -> Reviewer
  wordy         Writer runs past the 60-word limit              -> Reviewer
  miss          Reviewer approves a draft that is in fact faulty -> nobody

Separately from those task faults, roles occasionally overreach their
specification - the Writer tries to look a figure up for itself, the
Researcher tries to answer the user directly, the Reviewer tries to patch
the draft rather than return a verdict. Those attempts are what validate()
exists to stop, and each one is logged as a role violation. They are drawn
from the same seeded generator, so they reproduce exactly.
"""

import os
import random
from collections import Counter

import docstore
from docstore import DOCS, CANONICAL_DOC, TASKS, gold, question
from roles import ROLES, GENERALIST, Message, Violations, validate

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

SEEDS = list(range(101, 111))      # ten seeds, as the manual requires
MAX_REVISIONS = 2

# Fault rates for the scripted roles.
P_STALE_SOURCE = 0.30     # Researcher reads the near-duplicate twin
P_GAP_SLIP = 0.15         # Researcher mis-computes the gap
P_DROP_SOURCE = 0.25      # Writer drops one citation
P_WORDY = 0.20            # Writer exceeds 60 words
P_REVIEWER_MISS = 0.15    # Reviewer approves a faulty draft anyway

# Rates at which a role reaches outside its own specification. These are
# what validate() blocks; none of them is a task fault.
P_WRITER_SEARCHES = 0.20      # Writer reaches for search(), holds no tools
P_RESEARCHER_DIRECT = 0.10    # Researcher tries to answer the User itself
P_REVIEWER_EDITS = 0.15       # Reviewer tries to send the Writer a patch

# The generalist runs one merged prompt with no separate checking step, so
# its slips are the same ones but nothing downstream looks for them.
P_GEN_STALE = 0.30
P_GEN_GAP_SLIP = 0.15
P_GEN_DROP_SOURCE = 0.25
P_GEN_WORDY = 0.20


def rng_for(seed, task_id, role, attempt=0):
    return random.Random("%s:%s:%s:%s" % (seed, task_id, role, attempt))


# ---------------------------------------------------------------------------
# Scripted roles
# ---------------------------------------------------------------------------

def researcher_act(task, seed, attempt, violations, trace, calls,
                   enforce=True):
    """Finds both notes, reads them and computes the gap. May read the
    stale twin, and may slip the arithmetic."""
    spec = ROLES["Researcher"]
    calls["Researcher"] += 1
    rng = rng_for(seed, task["id"], "Researcher", attempt)

    values, sources = {}, []
    for model in (task["a"], task["b"]):
        if validate("Researcher", spec, violations, tool="search",
                    enforce=enforce):
            hits = docstore.search(model)
        else:
            hits = []
        # A later attempt has been told which note was wrong, so it takes
        # the canonical one; a first attempt may take the stale twin.
        stale_twin = [d for d in hits if DOCS[d]["stale"]]
        if attempt == 0 and stale_twin and rng.random() < P_STALE_SOURCE:
            doc_id = stale_twin[0]
        else:
            doc_id = CANONICAL_DOC[model]
        if validate("Researcher", spec, violations, tool="read_doc",
                    enforce=enforce):
            doc = docstore.read_doc(doc_id)
        else:
            doc = DOCS[doc_id]
        values[model] = doc["accuracy"]
        sources.append(doc_id)

    a_acc, b_acc = values[task["a"]], values[task["b"]]
    if validate("Researcher", spec, violations, tool="calculator",
                enforce=enforce):
        gap = round(abs(docstore.calculator("%s - %s" % (a_acc, b_acc))), 1)
    else:
        gap = round(abs(a_acc - b_acc), 1)
    if rng.random() < P_GAP_SLIP:
        gap = round(gap + 0.1, 1)

    winner = task["a"] if a_acc >= b_acc else task["b"]
    out = {"values": values, "sources": sorted(sources), "result":
           {"winner": winner, "gap": gap}}
    validate("Researcher", spec, violations, output=out, enforce=enforce)

    # Overreach: try to hand the finding straight to the user, bypassing the
    # Manager and with it the Writer and Reviewer. Researcher may only
    # message the Manager, so validate() refuses to deliver this.
    if rng.random() < P_RESEARCHER_DIRECT:
        direct = Message("Researcher", "User", task["id"], "deliver", out)
        if validate("Researcher", spec, violations, message=direct,
                    enforce=enforce):
            trace.append(direct)

    msg = Message("Researcher", "Manager", task["id"], "report", out)
    if validate("Researcher", spec, violations, message=msg, enforce=enforce):
        trace.append(msg)
    return out


def writer_act(task, finding, seed, attempt, violations, trace, calls,
               enforce=True):
    """Writes the cited answer. May drop a citation, may run long."""
    spec = ROLES["Writer"]
    calls["Writer"] += 1
    rng = rng_for(seed, task["id"], "Writer", attempt)

    # Overreach: the Writer decides to look the figure up for itself rather
    # than write from the finding it was handed. It holds no tools, so
    # validate() refuses the call and the search never runs.
    if rng.random() < P_WRITER_SEARCHES:
        if validate("Writer", spec, violations, tool="search",
                    enforce=enforce):
            docstore.search(task["a"])

    res = finding["result"]
    citations = list(finding["sources"])
    if attempt == 0 and rng.random() < P_DROP_SOURCE:
        citations = citations[:1]

    draft = ("%s scores higher on MMLU than %s, by %.1f points [%s]."
             % (res["winner"],
                task["b"] if res["winner"] == task["a"] else task["a"],
                res["gap"], ", ".join(citations)))
    if attempt == 0 and rng.random() < P_WORDY:
        draft += (" This comparison is drawn from the benchmark notes held "
                  "in the evaluation store, which record each model's "
                  "accuracy together with its parameter count, and which "
                  "are maintained by the evaluation team on a quarterly "
                  "basis so that every reported figure remains current, "
                  "traceable and suitable for direct citation in "
                  "downstream comparative reporting of this kind.")

    out = {"draft": draft, "citations": citations}
    validate("Writer", spec, violations, output=out, enforce=enforce)

    msg = Message("Writer", "Manager", task["id"], "report", out)
    if validate("Writer", spec, violations, message=msg, enforce=enforce):
        trace.append(msg)
    return out


def merged_writer_act(task, finding, seed, attempt, violations, trace, calls,
                      enforce=True):
    """
    The Exercise 1 ablation in which the Researcher and the Writer are one
    role holding the Researcher's tools.

    Two things change, and both are the point of the ablation. The write-up
    happens inside the same agent that did the research, so it costs no
    extra call and reaching for search() is no longer a violation - the
    merged role legitimately holds that tool. But nobody else reads the
    finding before it is written up, so the role writes up whatever it
    believes, including its own stale source or slipped gap.
    """
    spec = ROLES["Researcher"]          # the merged role keeps these tools
    rng = rng_for(seed, task["id"], "MergedRW", attempt)

    res = finding["result"]
    citations = list(finding["sources"])
    if attempt == 0 and rng.random() < P_DROP_SOURCE:
        citations = citations[:1]

    draft = ("%s scores higher on MMLU than %s, by %.1f points [%s]."
             % (res["winner"],
                task["b"] if res["winner"] == task["a"] else task["a"],
                res["gap"], ", ".join(citations)))
    if attempt == 0 and rng.random() < P_WORDY:
        draft += (" This comparison is drawn from the benchmark notes held "
                  "in the evaluation store, which record each model's "
                  "accuracy together with its parameter count, and which "
                  "are maintained by the evaluation team on a quarterly "
                  "basis so that every reported figure remains current, "
                  "traceable and suitable for direct citation in "
                  "downstream comparative reporting of this kind.")

    out = {"draft": draft, "citations": citations}
    msg = Message("Researcher+Writer", "Manager", task["id"], "report", out)
    if validate("Researcher", spec, violations, message=msg,
                enforce=enforce):
        trace.append(msg)
    return out


def reviewer_act(task, finding, draft_msg, seed, attempt, violations, trace,
                 calls, enforce=True):
    """Re-reads the cited sources and checks values, winner, citations and
    length. May miss a fault."""
    spec = ROLES["Reviewer"]
    calls["Reviewer"] += 1
    rng = rng_for(seed, task["id"], "Reviewer", attempt)
    g = gold(task)

    reasons = []
    cited = draft_msg["citations"]
    for doc_id in cited:
        if validate("Reviewer", spec, violations, tool="read_doc",
                    enforce=enforce):
            docstore.read_doc(doc_id)

    if any(DOCS[d]["stale"] for d in cited):
        reasons.append(("Researcher", "cited a superseded note"))
    if sorted(cited) != g["sources"]:
        # A missing citation is the Writer's fault; a wrong one the
        # Researcher's.
        if set(cited) <= set(g["sources"]):
            reasons.append(("Writer", "did not cite both sources"))
        else:
            reasons.append(("Researcher", "sourced the wrong note"))
    if finding["result"]["gap"] != g["gap"]:
        reasons.append(("Researcher", "stated gap does not match sources"))
    if finding["result"]["winner"] != g["winner"]:
        reasons.append(("Researcher", "stated the wrong winner"))
    if len(draft_msg["draft"].split()) > 60:
        reasons.append(("Writer", "draft exceeds 60 words"))

    missed = False
    if reasons and rng.random() < P_REVIEWER_MISS:
        reasons = []
        missed = True

    verdict = "approve" if not reasons else "revise"
    out = {"verdict": verdict, "reasons": reasons}
    validate("Reviewer", spec, violations, output=out, enforce=enforce)

    # Overreach: rather than return a verdict, the Reviewer tries to send a
    # corrected draft straight to the Writer. It may message only the
    # Manager, so validate() refuses to deliver it.
    if reasons and rng.random() < P_REVIEWER_EDITS:
        patch = Message("Reviewer", "Writer", task["id"], "report",
                        {"verdict": verdict, "reasons": reasons,
                         "patched_draft": draft_msg["draft"]})
        if validate("Reviewer", spec, violations, message=patch,
                    enforce=enforce):
            trace.append(patch)

    msg = Message("Reviewer", "Manager", task["id"], "review", out)
    if validate("Reviewer", spec, violations, message=msg, enforce=enforce):
        trace.append(msg)
    return out, missed


# ---------------------------------------------------------------------------
# Checklist
# ---------------------------------------------------------------------------

def score(task, draft, citations):
    """The four-point checklist: correct number, correct winner, both
    correct sources cited, at most 60 words."""
    g = gold(task)
    return {
        "number": ("%.1f" % g["gap"]) in draft,
        "winner": g["winner"] in draft,
        "sources": sorted(citations) == g["sources"],
        "length": len(draft.split()) <= 60,
    }


def passed(card):
    return all(card.values())


# ---------------------------------------------------------------------------
# The team orchestrator
# ---------------------------------------------------------------------------

def run_team(task, seed, violations, enforce=True, use_reviewer=True,
             merge_rw=False):
    """
    Manager assigns to Researcher, passes the finding to the Writer and the
    draft to the Reviewer; on a revise verdict it routes the task back to
    the role named in the reasons, for at most MAX_REVISIONS rounds, then
    delivers.

    use_reviewer=False and merge_rw=True are the two Exercise 1 ablations.
    """
    trace = []
    calls = Counter()
    spec_mgr = ROLES["Manager"]

    calls["Manager"] += 1
    subtasks = ["research the two notes", "write the cited answer"]
    if use_reviewer:
        subtasks.append("review the draft")
    out = {"subtasks": subtasks}
    validate("Manager", spec_mgr, violations, output=out, enforce=enforce)
    assign = Message("Manager", "Researcher", task["id"], "assign",
                     {"question": question(task), "subtasks": subtasks})
    if validate("Manager", spec_mgr, violations, message=assign,
                enforce=enforce):
        trace.append(assign)

    revisions = 0
    attempt = 0
    missed_fault = False

    finding = researcher_act(task, seed, attempt, violations, trace, calls,
                             enforce)
    if merge_rw:
        # The merged Researcher+Writer is one role holding the Researcher's
        # tools: it writes up its own finding in the same call, so there is
        # no handover and no second role reads the finding before it is
        # written up.
        draft_msg = merged_writer_act(task, finding, seed, attempt,
                                      violations, trace, calls, enforce)
    else:
        handoff = Message("Manager", "Writer", task["id"], "assign",
                          {"finding": finding})
        if validate("Manager", spec_mgr, violations, message=handoff,
                    enforce=enforce):
            trace.append(handoff)
        draft_msg = writer_act(task, finding, seed, attempt, violations,
                               trace, calls, enforce)

    while use_reviewer and revisions < MAX_REVISIONS:
        to_rev = Message("Manager", "Reviewer", task["id"], "assign",
                         {"draft": draft_msg["draft"],
                          "citations": draft_msg["citations"]})
        if validate("Manager", spec_mgr, violations, message=to_rev,
                    enforce=enforce):
            trace.append(to_rev)
        review, missed = reviewer_act(task, finding, draft_msg, seed,
                                      attempt, violations, trace, calls,
                                      enforce)
        missed_fault = missed_fault or missed
        if review["verdict"] == "approve":
            break

        revisions += 1
        attempt += 1
        # Route the revision back to the role named in the reasons.
        blamed = review["reasons"][0][0]
        back = Message("Manager", blamed, task["id"], "assign",
                       {"revision": review["reasons"]})
        if validate("Manager", spec_mgr, violations, message=back,
                    enforce=enforce):
            trace.append(back)
        if blamed == "Researcher":
            finding = researcher_act(task, seed, attempt, violations, trace,
                                     calls, enforce)
        if merge_rw:
            draft_msg = merged_writer_act(task, finding, seed, attempt,
                                          violations, trace, calls, enforce)
        else:
            draft_msg = writer_act(task, finding, seed, attempt, violations,
                                   trace, calls, enforce)

    deliver = Message("Manager", "User", task["id"], "deliver",
                      {"draft": draft_msg["draft"],
                       "citations": draft_msg["citations"]})
    if validate("Manager", spec_mgr, violations, message=deliver,
                enforce=enforce):
        trace.append(deliver)

    card = score(task, draft_msg["draft"], draft_msg["citations"])
    return {
        "trace": trace, "calls": calls, "card": card, "passed": passed(card),
        "revisions": revisions, "missed_fault": missed_fault,
        "draft": draft_msg["draft"], "citations": draft_msg["citations"],
    }


# ---------------------------------------------------------------------------
# The single generalist
# ---------------------------------------------------------------------------

def run_generalist(task, seed, violations, enforce=True):
    """One agent, every tool, one merged prompt, one call, no separate
    checking step. It may send only to the User, which it always does, so
    it records no role violations at all."""
    trace = []
    calls = Counter()
    calls["Generalist"] += 1
    rng = rng_for(seed, task["id"], "Generalist")

    values, sources = {}, []
    for model in (task["a"], task["b"]):
        validate("Generalist", GENERALIST, violations, tool="search",
                 enforce=enforce)
        hits = docstore.search(model)
        stale_twin = [d for d in hits if DOCS[d]["stale"]]
        if stale_twin and rng.random() < P_GEN_STALE:
            doc_id = stale_twin[0]
        else:
            doc_id = CANONICAL_DOC[model]
        validate("Generalist", GENERALIST, violations, tool="read_doc",
                 enforce=enforce)
        doc = docstore.read_doc(doc_id)
        values[model] = doc["accuracy"]
        sources.append(doc_id)

    a_acc, b_acc = values[task["a"]], values[task["b"]]
    validate("Generalist", GENERALIST, violations, tool="calculator",
             enforce=enforce)
    gap = round(abs(docstore.calculator("%s - %s" % (a_acc, b_acc))), 1)
    if rng.random() < P_GEN_GAP_SLIP:
        gap = round(gap + 0.1, 1)
    winner = task["a"] if a_acc >= b_acc else task["b"]

    citations = sorted(sources)
    if rng.random() < P_GEN_DROP_SOURCE:
        citations = citations[:1]
    draft = ("%s scores higher on MMLU than %s, by %.1f points [%s]."
             % (winner, task["b"] if winner == task["a"] else task["a"],
                gap, ", ".join(citations)))
    if rng.random() < P_GEN_WORDY:
        draft += (" This comparison is drawn from the benchmark notes held "
                  "in the evaluation store, which record each model's "
                  "accuracy together with its parameter count, and which "
                  "are maintained by the evaluation team on a quarterly "
                  "basis so that every reported figure remains current, "
                  "traceable and suitable for direct citation in "
                  "downstream comparative reporting of this kind.")

    out = {"draft": draft, "citations": citations}
    validate("Generalist", GENERALIST, violations, output=out,
             enforce=enforce)
    msg = Message("Generalist", "User", task["id"], "deliver", out)
    validate("Generalist", GENERALIST, violations, message=msg,
             enforce=enforce)
    trace.append(msg)

    card = score(task, draft, citations)
    return {
        "trace": trace, "calls": calls, "card": card, "passed": passed(card),
        "revisions": 0, "missed_fault": False,
        "draft": draft, "citations": citations,
    }


# ---------------------------------------------------------------------------
# Sweep over seeds
# ---------------------------------------------------------------------------

def evaluate(system, seeds=SEEDS, **kwargs):
    """Run every task at every seed. Returns aggregate counters plus the
    per-(seed, task) pass flags so the two systems can be compared task by
    task."""
    violations = Violations()
    total_calls = Counter()
    passes = 0
    revisions = 0
    missed = 0
    per_task = {}

    for seed in seeds:
        for task in TASKS:
            docstore.reset_tool_calls()
            if system == "team":
                r = run_team(task, seed, violations, **kwargs)
            else:
                r = run_generalist(task, seed, violations, **kwargs)
            total_calls.update(r["calls"])
            passes += int(r["passed"])
            revisions += r["revisions"]
            missed += int(r["missed_fault"])
            per_task.setdefault(task["id"], []).append(r["passed"])

    n = len(seeds) * len(TASKS)
    return {
        "system": system,
        "runs": n,
        "passes": passes,
        "success": passes / n,
        "calls": total_calls,
        "total_calls": sum(total_calls.values()),
        "violations": violations,
        "revisions": revisions,
        "missed": missed,
        "per_task": per_task,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("=== Role specifications ===")
    for name, spec in ROLES.items():
        emit("%s" % name)
        emit("  goal          : %s" % spec["goal"])
        emit("  tools         : %s" % (", ".join(spec["tools"]) or "none"))
        emit("  may send to   : %s" % ", ".join(spec["may_send_to"]))
        emit("  output fields : %s" % ", ".join(spec["output_fields"]))
        emit("  system prompt : %s" % spec["system_prompt"])
        emit()

    emit("=== Message format ===")
    emit("Message(sender, recipient, task_id, intent, payload)")
    emit("  intent is one of: assign | report | review | deliver")
    emit("  payload carries exactly the sending role's required output "
         "fields")
    emit("  rendered below as:  sender -> recipient [intent] payload-keys")
    emit()

    emit("=== Document store (near-duplicate titles marked) ===")
    for doc_id, d in sorted(DOCS.items()):
        emit("  %s  %-32s %-10s acc=%-5s %s"
             % (doc_id, d["title"], d["model"], d["accuracy"],
                "<- superseded twin" if d["stale"] else ""))
    emit()

    # One complete trace containing a revision.
    emit("=== One complete message trace (with a revision) ===")
    shown = False
    for seed in SEEDS:
        for task in TASKS:
            v = Violations()
            r = run_team(task, seed, v)
            if r["revisions"] >= 1:
                emit("task %s, seed %s: %s" % (task["id"], seed,
                                               question(task)))
                emit("gold: winner=%s gap=%.1f sources=%s"
                     % (gold(task)["winner"], gold(task)["gap"],
                        ", ".join(gold(task)["sources"])))
                emit()
                for m in r["trace"]:
                    emit("  " + m.render())
                    if m.intent == "review":
                        emit("        verdict=%s reasons=%s"
                             % (m.payload["verdict"],
                                m.payload["reasons"] or "-"))
                    if m.intent == "deliver":
                        emit("        draft: %s" % m.payload["draft"])
                emit()
                emit("  revisions=%d  checklist=%s  passed=%s"
                     % (r["revisions"], r["card"], r["passed"]))
                shown = True
                break
        if shown:
            break
    emit()

    emit("=== Comparison over %d seeds x %d tasks = %d runs ==="
         % (len(SEEDS), len(TASKS), len(SEEDS) * len(TASKS)))
    team = evaluate("team")
    gen = evaluate("generalist")

    for r in (team, gen):
        emit()
        emit("--- %s ---" % r["system"])
        emit("  task success     : %.3f (%d/%d)"
             % (r["success"], r["passes"], r["runs"]))
        emit("  model calls      : %d total" % r["total_calls"])
        for role, n in sorted(r["calls"].items()):
            emit("      %-12s %d" % (role, n))
        emit("  role violations  : %d" % r["violations"].count())
        if r["violations"].count():
            emit("      by role : %s" % dict(r["violations"].by_role()))
            emit("      by kind : %s" % dict(r["violations"].by_kind()))
        emit("  revisions        : %d" % r["revisions"])
        emit("  faults missed by Reviewer : %d" % r["missed"])

    emit()
    emit("=== Per-task success (team vs generalist) ===")
    emit("%-6s%-12s%-12s" % ("task", "team", "generalist"))
    for task in TASKS:
        t = team["per_task"][task["id"]]
        g = gen["per_task"][task["id"]]
        emit("%-6s%-12s%-12s" % (task["id"],
                                 "%d/%d" % (sum(t), len(t)),
                                 "%d/%d" % (sum(g), len(g))))

    extra_calls = team["total_calls"] - gen["total_calls"]
    extra_correct = team["passes"] - gen["passes"]
    emit()
    emit("Extra model calls spent by the team : %d" % extra_calls)
    emit("Extra correct answers gained        : %d" % extra_correct)
    if extra_correct > 0:
        emit("Model calls per additional correct answer : %.2f"
             % (extra_calls / extra_correct))

    out_path = os.path.join(OUT_DIR, "exp6_role_agents.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n[saved output to %s]" % out_path)


if __name__ == "__main__":
    main()
