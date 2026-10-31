import html
import os
import platform
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")

DEFAULT_ROLL = "U23AI042"
STUDENT_NAME = ""


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def run_program(script):
    print("  running %s ..." % script)
    proc = subprocess.run([sys.executable, script], cwd=HERE,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("%s failed:\n%s" % (script, proc.stderr))
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, script.replace(".py", ".txt")), "w",
              encoding="utf-8") as fh:
        fh.write(proc.stdout)
    return proc.stdout


def code(text, size="7.5pt"):
    return ("<pre class=code style='font-size:%s'>%s</pre>"
            % (size, html.escape(text.rstrip())))


def out(text, size="6.5pt"):
    return ("<pre class=out style='font-size:%s'>%s</pre>"
            % (size, html.escape(text.rstrip())))


def table(headers, rows, widths=None):
    w = widths or ([None] * len(headers))
    th = "".join("<th%s>%s</th>" % ((" style='width:%s'" % x) if x else "", h)
                 for h, x in zip(headers, w))
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in row)
                 for row in rows)
    return "<table class=g><tr>%s</tr>%s</table>" % (th, tr)


PAGEBREAK = "<br style='page-break-before:always'>"


def build(roll):
    src_main = read(os.path.join(HERE, "exp3_tool_agent.py"))
    src_ex = read(os.path.join(HERE, "exp3_exercises.py"))

    o_main = run_program("exp3_tool_agent.py")
    o_ex = run_program("exp3_exercises.py")

    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    env_line = ("Python %s on %s (%s), executed %s"
                % (platform.python_version(), platform.system(),
                   platform.machine(), stamp))

    P = []
    A = P.append

    A("<div class=WordSection1>")
    A("<p class=inst>Sardar Vallabhbhai National Institute of Technology "
      "(SVNIT), Surat</p>")
    A("<p class=dept>Department of Artificial Intelligence</p>")
    A("<p class=course>Agentic AI (IA462) &mdash; Semester VIII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "3", stamp.split(",")[0]]]))
    A("<h1>Experiment 3</h1>")
    A("<h1 class=sub>Tool-Using Agent &mdash; The Function-Calling Pattern</h1>")

    A("<h2>Aim</h2>")
    A("<p>To implement the runtime half of LLM function calling &mdash; "
      "parsing a structured tool call, dispatching it to a registered "
      "Python function, and returning the result as an observation the "
      "agent can reason over.</p>")

    A("<h2>Theory</h2>")
    A("<p>A language model cannot compute reliably, does not know today's "
      "date and cannot reach external systems. Function calling closes "
      "that gap. The model is shown a set of tool schemas &mdash; for each "
      "tool a name, a description and its argument names and types &mdash; "
      "and instead of replying in prose it emits a structured request "
      "naming one tool and the arguments to call it with. The model itself "
      "executes nothing. The runtime parses the request, looks the name up "
      "in a tool registry, invokes the function and returns the value as "
      "an observation. That division is the whole point of the pattern: "
      "the model decides, the runtime executes, and every side effect "
      "therefore passes through code the developer controls.</p>")
    A("<p>This experiment implements the runtime side completely and "
      "scripts the model side, so the entire contract is visible without "
      "an API key or network access. The registry and dispatch function "
      "written here are reused in Experiment 4, where the same machinery "
      "sits behind the interleaved thought&ndash;action&ndash;observation "
      "steps of the ReAct loop.</p>")
    A("<p>Note the limitation visible in the sample run: dispatch trusts "
      "whatever it is handed, so a malformed JSON call or an unregistered "
      "tool name aborts the loop rather than producing a recoverable "
      "observation. Note also that the calculator is deliberately given a "
      "restricted evaluation environment, since a plain "
      "<span class=m>eval</span> would run any expression the model chose "
      "to emit. Hardening the runtime against both is Exercise 1.</p>")

    A("<p class=cap>Table 1. Tool registry exposed to the model.</p>")
    A(table(["Tool name", "Arguments (name: type)", "What it returns"],
            [["calculator", "expression: string",
              "Value of an arithmetic expression evaluated in a restricted "
              "namespace (sqrt, pow, pi)"],
             ["days_between", "d1: string, d2: string (ISO YYYY-MM-DD)",
              "Whole number of days between the two dates"],
             ["unit_convert", "value: number, frm: string, to: string",
              "The value converted between km/miles, kg/lb or &deg;C/&deg;F"]],
            widths=["18%", "38%", "44%"]))

    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Implement each tool as an ordinary Python function, register the "
      "functions in a name &rarr; function dictionary (the tool registry), "
      "and write a JSON schema for each one giving its name, description "
      "and argument types &mdash; the artifact a real model is shown.</li>"
      "<li>Implement <span class=m>dispatch()</span>: parse the JSON tool "
      "call, look the name up in the registry, invoke the function with "
      "the unpacked arguments and wrap the return value in a structured "
      "observation; then feed a scripted sequence of tool calls through "
      "it, printing each call with the observation it produced.</li>"
      "</ol>")
    A(code("def dispatch(tool_call_json):\n"
           "    call = json.loads(tool_call_json)          # parse\n"
           "    name = call[\"tool\"]\n"
           "    args = call.get(\"arguments\", {})\n\n"
           "    fn = TOOL_REGISTRY[name]                   # look up\n"
           "    result = fn(**args)                        # invoke\n\n"
           "    return {                                   # wrap as observation\n"
           "        \"tool\": name,\n"
           "        \"arguments\": args,\n"
           "        \"observation\": result,\n"
           "    }",
           size="8.5pt"))

    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<h3>Program &mdash; exp3_tool_agent.py</h3>")
    A(code(src_main))

    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A("<p class=cap>Snapshot of the console output "
      "(%s).</p>" % html.escape(env_line))
    A(out(o_main))

    A(PAGEBREAK)
    A("<h2>Observations</h2>")
    A("<h3>1. Which side of the contract executes the tool, and why the "
      "separation matters</h3>")
    A("<p>The model only ever <i>decides</i>: it emits a JSON object naming "
      "a tool and its arguments, and nothing more. Every actual side "
      "effect &mdash; evaluating an expression, computing a date "
      "difference, touching a file &mdash; happens inside "
      "<span class=m>dispatch()</span>, which is ordinary developer-owned "
      "Python. This separation matters because it keeps the model, which "
      "cannot be fully trusted to emit safe or correct instructions, out "
      "of the execution path entirely. Every call the model proposes still "
      "passes through code the developer wrote and can validate, sandbox "
      "or reject &mdash; here, the calculator's restricted namespace is "
      "exactly that control point, refusing to expose "
      "<span class=m>__builtins__</span> to whatever expression the model "
      "produced.</p>")

    A("<h3>2. What happens when a call names a tool that is not in the "
      "registry</h3>")
    A("<p>In the base <span class=m>dispatch()</span> implementation, "
      "<span class=m>TOOL_REGISTRY[name]</span> raises a "
      "<span class=m>KeyError</span> that is never caught, so the whole "
      "loop aborts on the first unregistered call &mdash; there is no "
      "recoverable observation to hand back to the model, and no way for "
      "an agent loop built on top of it to continue reasoning. Exercise 1's "
      "<span class=m>dispatch_safe()</span> fixes exactly this: it checks "
      "membership in the registry before invoking anything and returns a "
      "structured <span class=m>{\"error\": {\"type\": \"unknown_tool\", "
      "...}}</span> observation instead, so the surrounding loop can "
      "inspect the failure and decide what to do next rather than "
      "crashing.</p>")

    A("<h3>3. What the schema must contain for the model to call a tool "
      "correctly without seeing its implementation</h3>")
    A("<p>The schema is the entire interface the model has to a tool "
      "&mdash; it never sees the Python body. It must therefore state the "
      "exact <span class=m>name</span> the dispatch step will match "
      "against, a <span class=m>description</span> precise enough that the "
      "model can tell when the tool is applicable (e.g. distinguishing "
      "<span class=m>unit_convert</span>'s three supported unit pairs from "
      "an unsupported one), and for every argument its exact "
      "<span class=m>name</span> and <span class=m>type</span>. Argument "
      "names matter as much as their types: Exercise 1's Demo 3 shows that "
      "supplying a value under the wrong key (<span class=m>expr</span> "
      "instead of <span class=m>expression</span>) is indistinguishable, "
      "from the runtime's point of view, from omitting the argument "
      "entirely &mdash; the schema is the only contract preventing that "
      "mismatch.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Structured error handling in the runtime</h2>")
    A("<p><b>Task.</b> Add error handling to the runtime so that malformed "
      "JSON, an unknown tool name, a wrong argument name and an exception "
      "raised inside a tool each produce a structured error observation "
      "instead of crashing; demonstrate with one call of each kind.</p>")
    A("<p><b>Approach.</b> <span class=m>dispatch_safe()</span> wraps each "
      "of the four failure points in the original pipeline with an "
      "explicit check or a <span class=m>try/except</span>, returning "
      "<span class=m>{\"error\": {\"type\": ..., \"message\": ...}}</span> "
      "instead of propagating an exception: a "
      "<span class=m>json.JSONDecodeError</span> during parsing becomes a "
      "<span class=m>malformed_json</span> error; a name absent from the "
      "registry becomes <span class=m>unknown_tool</span>; a mismatch "
      "between the arguments given and the schema's expected argument "
      "names (extra, missing, or both) becomes <span class=m>bad_arguments"
      "</span>; and any exception the tool itself raises during invocation "
      "is caught and reported as <span class=m>tool_exception:&lt;type&gt;"
      "</span> with the original message preserved.</p>")
    A("<h3>Program &mdash; exp3_exercises.py</h3>")
    A(code(src_ex))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex))
    A("<h3>Discussion</h3>")
    A("<p>Each of the four demo calls exercises exactly one failure mode "
      "and none of them crash the process: a truncated JSON string is "
      "caught at the parsing step, a fictitious "
      "<span class=m>weather_lookup</span> tool is caught at the registry "
      "lookup, a calculator call using the key "
      "<span class=m>expr</span> instead of <span class=m>expression</span> "
      "is caught by the argument-name check before the function is ever "
      "invoked, and an unsupported <span class=m>km &rarr; kg</span> "
      "conversion is caught by the surrounding "
      "<span class=m>try/except</span> after "
      "<span class=m>unit_convert</span> raises "
      "<span class=m>ValueError</span> internally. In every case the "
      "caller receives a well-formed dictionary it can branch on, which is "
      "what lets a ReAct-style loop treat a failed tool call as just "
      "another observation to reason over, rather than a fatal error.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; A fourth tool: csv_mean</h2>")
    A("<p><b>Task.</b> Register a fourth tool that reads a CSV file and "
      "returns the mean of a named column. Write its schema and the tool "
      "call that invokes it, and report the observation returned.</p>")
    A("<p><b>Approach.</b> <span class=m>csv_mean(path, column)</span> "
      "opens the file with <span class=m>csv.DictReader</span>, checks "
      "the requested column exists, converts every non-empty cell in that "
      "column to <span class=m>float</span> and returns the arithmetic "
      "mean. It is registered in "
      "<span class=m>TOOL_REGISTRY_EXT</span> alongside the original three "
      "tools and given the schema below, so it is callable through the "
      "same <span class=m>dispatch_safe()</span> path with no special "
      "casing.</p>")
    A(code(
        '{\n'
        '  "name": "csv_mean",\n'
        '  "description": "Read a CSV file and return the mean of a named column.",\n'
        '  "arguments": {\n'
        '    "path": {"type": "string", "description": "Path to the CSV file"},\n'
        '    "column": {"type": "string", "description": "Name of the numeric column to average"}\n'
        '  }\n'
        '}', size="8.5pt"))
    A("<p>A five-row sample CSV (<span class=m>sample_temperatures.csv"
      "</span>, checked into the lab directory) with a "
      "<span class=m>temperature</span> column of "
      "[30.5, 31.2, 29.8, 33.0, 28.7] is read by the tool call</p>")
    A(code(
        '{"tool": "csv_mean", "arguments": {"path": "sample_temperatures.csv", '
        '"column": "temperature"}}', size="8.5pt"))
    A("<p>returns the observation <span class=m>30.64</span> (see the "
      "&ldquo;Exercise 2&rdquo; section of the output above for the exact "
      "run), matching the arithmetic mean of the five values by "
      "hand-check.</p>")

    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>The runtime half of the function-calling pattern was implemented "
      "end to end: three tools registered against their JSON schemas, and "
      "a <span class=m>dispatch()</span> function that parses a structured "
      "tool call, invokes the matching Python function and returns the "
      "result as an observation, exercised against five scripted calls. "
      "Because the model side is scripted rather than live, the entire "
      "decide/execute boundary that function calling depends on is visible "
      "without any external API.</p>")
    A("<p>The two exercises then hardened and extended that boundary. "
      "Exercise 1 replaced the runtime's four silent crash points "
      "&mdash; bad JSON, an unregistered tool, a misnamed argument, and an "
      "exception inside a tool &mdash; with structured error observations, "
      "which is what allows a calling loop to keep reasoning after a "
      "failed call instead of terminating. Exercise 2 showed the registry "
      "design scales cleanly: adding a fourth tool, "
      "<span class=m>csv_mean</span>, required only a new function, a new "
      "schema entry and a registry entry, with no change to "
      "<span class=m>dispatch()</span> itself.</p>")

    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "exp3_tool_agent.py, exp3_exercises.py, make_report.py"],
             ["Libraries used",
              "Python standard library only (<span class=m>json</span>, "
              "<span class=m>math</span>, <span class=m>datetime</span>, "
              "<span class=m>csv</span>). No agent framework or "
              "orchestration library was used, in accordance with clause "
              "3.1 of the Rules and Regulations."],
             ["Reproducibility",
              "All tool calls are fixed scripted JSON strings and every "
              "tool is a deterministic function, so every run of every "
              "program reproduces exactly."],
             ["Sources consulted",
              "Course manual for Experiment 3 (function-calling pattern, "
              "tool registry, dispatch contract)."]],
            widths=["22%", "78%"]))
    A("<p class=note>All output reproduced above was produced by executing "
      "the programs listed in this record on the machine and at the time "
      "stated in the table.</p>")
    A("</div>")

    return "".join(P), env_line


CSS = """
@page WordSection1 { size: 21.0cm 29.7cm; margin: 1.6cm 1.5cm 1.6cm 1.5cm; }
div.WordSection1 { page: WordSection1; }
body { font-family: 'Times New Roman', serif; font-size: 11.0pt; color: #000; }
p { margin: 0 0 7pt 0; text-align: justify; line-height: 1.25; }
p.inst { text-align: center; font-size: 13pt; font-weight: bold; margin-bottom: 2pt; }
p.dept { text-align: center; font-size: 11.5pt; font-weight: bold; margin-bottom: 2pt; }
p.course { text-align: center; font-size: 11pt; margin-bottom: 6pt; }
p.cap { font-size: 9.5pt; font-weight: bold; margin: 10pt 0 4pt 0; text-align: left; }
p.eq { text-align: center; font-style: italic; margin: 6pt 0; }
p.note { font-size: 9.5pt; font-style: italic; margin-top: 10pt; }
h1 { font-size: 14pt; text-align: center; margin: 14pt 0 4pt 0; }
h1.sub { font-size: 12.5pt; margin-top: 0; }
h2 { font-size: 12pt; margin: 14pt 0 6pt 0; border-bottom: 1px solid #888;
     padding-bottom: 2pt; }
h3 { font-size: 11pt; font-style: italic; margin: 10pt 0 4pt 0; }
ol, ul { margin: 0 0 8pt 0; }
li { margin-bottom: 3pt; text-align: justify; line-height: 1.25; }
table.g { border-collapse: collapse; width: 100%; margin: 0 0 8pt 0;
          font-size: 10pt; }
table.g th { border: 1px solid #666; background: #ececec; padding: 4pt;
             text-align: left; vertical-align: top; }
table.g td { border: 1px solid #666; padding: 4pt; vertical-align: top;
             text-align: left; }
pre.code, pre.out { font-family: Consolas, 'Courier New', monospace;
    border: 1px solid #999; background: #f6f6f6; padding: 5pt;
    white-space: pre; line-height: 1.15; margin: 0 0 8pt 0; }
pre.out { background: #fbfbfb; }
span.m { font-family: Consolas, 'Courier New', monospace; font-size: 9.5pt; }
hr { border: 0; border-top: 1.5px solid #000; margin: 4pt 0 8pt 0; }
img { border: 1px solid #999; }
"""

TEMPLATE = """<html xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:w="urn:schemas-microsoft-com:office:word"
xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<!--[if gte mso 9]><xml><w:WordDocument>
<w:View>Print</w:View><w:Zoom>100</w:Zoom>
</w:WordDocument></xml><![endif]-->
<style>%(css)s</style>
</head>
<body>%(body)s</body>
</html>
"""


if __name__ == "__main__":
    roll = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROLL

    body, env_line = build(roll)
    name = "LAB_3_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_3_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
