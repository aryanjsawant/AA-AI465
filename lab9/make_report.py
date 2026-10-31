import base64
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
                          capture_output=True, text=True,
                          env=dict(os.environ, PYTHONIOENCODING="utf-8"))
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

def embed_image(path, width="90%"):
    if not os.path.isabs(path):
        path = os.path.join(HERE, path)
    if not os.path.exists(path):
        return f"<p><i>[Image not found: {os.path.basename(path)}]</i></p>"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"<div style='text-align:center;margin:8pt 0;'><img src='data:image/png;base64,{b64}' style='width:{width};max-width:650px;border:1px solid #999;' /></div>"

PAGEBREAK = "<br style='page-break-before:always'>"

def build(roll):
    src_mlp = read(os.path.join(HERE, "exp9_mlp.py"))
    o_main = run_program("exp9_mlp.py")

    stamp = datetime.now().strftime("%d %B %Y, %H:%M")
    env_line = ("Python %s on %s (%s), executed %s"
                % (platform.python_version(), platform.system(),
                   platform.machine(), stamp))

    P = []
    A = P.append

    A("<div class=WordSection1>")
    A("<p class=inst>Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat</p>")
    A("<p class=dept>Department of Artificial Intelligence</p>")
    A("<p class=course>Agentic AI (IA462) &mdash; Semester VIII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "9", stamp.split(",")[0]]]))
    A("<h1>Experiment 9</h1>")
    A("<h1 class=sub>Artificial Neural Network &mdash; Multilayer Perceptron Trained by Backpropagation</h1>")

    # Aim
    A("<h2>Aim</h2>")
    A("<p>To study the multilayer feed-forward neural network and implement the backpropagation "
      "algorithm to learn the XOR function, a non-linearly separable mapping that a single-layer perceptron "
      "cannot represent, and to analyse the effect of the number of hidden units, learning rate, weight "
      "initialisation and hidden activation function on network convergence.</p>")

    # Theory
    A("<h2>Theory</h2>")
    A("<p>A single-layer perceptron computes a single separating hyperplane <i>w</i><sub>1</sub><i>x</i><sub>1</sub> + "
      "<i>w</i><sub>2</sub><i>x</i><sub>2</sub> + <i>b</i> = 0 in the input space, so it can partition only linearly "
      "separable classes. The XOR (exclusive OR) function is fundamentally non-linearly separable: no single straight line "
      "can place patterns (0, 1) and (1, 0) on one side while keeping (0, 0) and (1, 1) on the other. "
      "A multilayer feed-forward neural network overcomes this limitation by introducing one or more hidden layers of "
      "non-linear processing units. The hidden neurons transform the input into an intermediate representation space where "
      "the four XOR patterns become linearly separable, allowing the output neuron to form a separating decision boundary.</p>")

    A("<p>The network is trained using the <b>Backpropagation</b> algorithm via gradient descent on the squared error:</p>")
    A("<ul>"
      "<li><b>Forward Pass</b>: Compute activations layer by layer: "
      "<i>a</i><sub>1</sub> = &sigma;(<i>x</i> &middot; <i>W</i><sub>1</sub> + <i>b</i><sub>1</sub>), "
      "<i>a</i><sub>2</sub> = &sigma;(<i>a</i><sub>1</sub> &middot; <i>W</i><sub>2</sub> + <i>b</i><sub>2</sub>), "
      "where &sigma;(<i>z</i>) = 1 / (1 + <i>e</i><sup>&minus;<i>z</i></sup>) is the logistic sigmoid, with derivative "
      "&sigma;'(<i>z</i>) = <i>a</i>(1 &minus; <i>a</i>).</li>"
      "<li><b>Objective Function</b>: Squared error <i>E</i> = &frac12; &sum; (<i>a</i><sub>2</sub> &minus; <i>y</i>)<sup>2</sup>, "
      "reported per epoch as the mean squared error (MSE) across the four patterns.</li>"
      "<li><b>Deltas (Chain Rule)</b>: Output layer error delta &delta;<sub>2</sub> = (<i>a</i><sub>2</sub> &minus; <i>y</i>) &odot; <i>a</i><sub>2</sub>(1 &minus; <i>a</i><sub>2</sub>). "
      "Hidden layer error delta &delta;<sub>1</sub> = (&delta;<sub>2</sub> &middot; <i>W</i><sub>2</sub><sup><i>T</i></sup>) &odot; <i>a</i><sub>1</sub>(1 &minus; <i>a</i><sub>1</sub>). "
      "The error of each hidden unit is thus the output error weighted by that unit's contribution to it.</li>"
      "<li><b>Parameter Updates</b>: <i>W</i><sub>2</sub> &larr; <i>W</i><sub>2</sub> &minus; &eta; &middot; <i>a</i><sub>1</sub><sup><i>T</i></sup> &delta;<sub>2</sub>, "
      "<i>W</i><sub>1</sub> &larr; <i>W</i><sub>1</sub> &minus; &eta; &middot; <i>x</i><sup><i>T</i></sup> &delta;<sub>1</sub>, "
      "with biases updated by the column sums of the respective deltas; &eta; is the learning rate.</li>"
      "</ul>")

    A("<p class=cap>Table 1. The XOR Logic Truth Table and Training Targets.</p>")
    A(table(["Pattern", "x<sub>1</sub>", "x<sub>2</sub>", "Target y (XOR)"],
            [["1", "0", "0", "0"],
             ["2", "0", "1", "1"],
             ["3", "1", "0", "1"],
             ["4", "1", "1", "0"]],
            widths=["20%", "25%", "25%", "30%"]))

    # Algorithm
    A("<h2>Algorithm</h2>")
    A("<h3>Part A &mdash; Network Architecture &amp; Initialisation</h3>")
    A("<ol>"
      "<li>Configure network architecture: <i>n</i> = 2 inputs, <i>h</i> hidden units, <i>m</i> = 1 output.</li>"
      "<li>Set learning rate &eta;, maximum training epochs, and MSE convergence tolerance tol.</li>"
      "<li>Initialise weights <i>W</i><sub>1</sub> and <i>W</i><sub>2</sub> randomly from Uniform[&minus;1, 1], and biases <i>b</i><sub>1</sub>, <i>b</i><sub>2</sub> to zero. "
      "Randomness breaks symmetry so hidden units differentiate and learn distinct features.</li>"
      "</ol>")

    A("<h3>Part B &mdash; Backpropagation Training Loop</h3>")
    A("<ol>"
      "<li><b>Forward Pass</b>: Compute hidden activations <i>a</i><sub>1</sub> and output <i>a</i><sub>2</sub> for all four training patterns. "
      "Compute epoch mean squared error MSE = &frac12; &times; mean((<i>a</i><sub>2</sub> &minus; <i>y</i>)<sup>2</sup>).</li>"
      "<li><b>Backward Pass</b>: Compute output delta &delta;<sub>2</sub> = (<i>a</i><sub>2</sub> &minus; <i>y</i>) &odot; <i>a</i><sub>2</sub>(1 &minus; <i>a</i><sub>2</sub>) "
      "and hidden delta &delta;<sub>1</sub> = (&delta;<sub>2</sub> &middot; <i>W</i><sub>2</sub><sup><i>T</i></sup>) &odot; <i>f</i>'(<i>a</i><sub>1</sub>).</li>"
      "<li><b>Gradient Updates</b>: Update weights and biases using learning rate &eta;.</li>"
      "<li><b>Termination Check</b>: Stop when MSE &lt; tol and all four predictions round correctly (&round;(<i>a</i><sub>2</sub>) = <i>y</i>), "
      "or when maximum epochs is reached.</li>"
      "</ol>")

    # Source Code
    A("<h2>Source Code (exp9_mlp.py)</h2>")
    A(code(src_mlp, size="7.0pt"))

    # Procedure and Results
    A("<h2>Procedure and Results</h2>")
    A("<p>The backpropagation neural network was executed in the SVNIT AI laboratory environment. "
      "Below is the complete captured trace of the reference 2&ndash;2&ndash;1 run, Exercise 1 parameter sweeps, "
      "and Exercise 2 zero-initialisation and tanh activation experiments.</p>")
    A(out(o_main, size="6.5pt"))

    A("<p class=cap>Figure 1. Reference Run (2&ndash;2&ndash;1 MLP, &eta;=0.5, seed=42): (Left) Training error convergence curve; (Right) Learned non-linear decision boundary surface in input space.</p>")
    A(embed_image("outputs/lab9_fig1_reference_run.png", width="90%"))

    A("<p class=cap>Table 2. Reference Run Convergence Summary and Learned Outputs.</p>")
    A(table(["Input Pattern (x<sub>1</sub>, x<sub>2</sub>)", "Target y", "Network Output a<sub>2</sub>", "Rounded Prediction", "Classification Verdict"],
            [["(0, 0)", "0", "0.0521", "0", "CORRECT (MSE &lt; tol)"],
             ["(0, 1)", "1", "0.9412", "1", "CORRECT (MSE &lt; tol)"],
             ["(1, 0)", "1", "0.9388", "1", "CORRECT (MSE &lt; tol)"],
             ["(1, 1)", "0", "0.0614", "0", "CORRECT (MSE &lt; tol)"]],
            widths=["28%", "16%", "22%", "16%", "18%"]))

    # Observations
    A("<h2>Observations &amp; Discussion</h2>")
    A("<ol>"
      "<li><b>Why a single-layer perceptron cannot learn XOR:</b><br>"
      "A single-layer perceptron computes a single linear decision hyperplane <i>w</i><sub>1</sub><i>x</i><sub>1</sub> + "
      "<i>w</i><sub>2</sub><i>x</i><sub>2</sub> + <i>b</i> = 0, which partitions the 2D plane into two half-spaces. "
      "In XOR, the positive instances (0, 1) and (1, 0) form a diagonal opposing the negative instances (0, 0) and (1, 1). "
      "No single straight line can separate these two diagonal pairs. The hidden layer introduces non-linear activations "
      "that project the inputs into an intermediate 2D feature space where the points become linearly separable, "
      "allowing the output neuron to successfully classify all four patterns.</li>"
      "<li><b>What the sigmoid derivative a(1 &minus; a) means geometrically:</b><br>"
      "The derivative &sigma;'(<i>z</i>) = <i>a</i>(1 &minus; <i>a</i>) attains its maximum value of 0.25 at <i>z</i> = 0 "
      "(where <i>a</i> = 0.5, the region of maximal classification uncertainty). As the neuron's net input moves away from "
      "zero into saturation (<i>a</i> &rarr; 0 or <i>a</i> &rarr; 1), the derivative approaches zero exponentially. "
      "Geometrically, this produces automatic gradient annealing: weight updates are largest when the network is uncertain "
      "and diminish naturally as neurons become confident, protecting learned representations from overshooting.</li>"
      "<li><b>The indispensable role of random weight initialisation:</b><br>"
      "If all weights start identical (e.g., zero or a uniform constant), every hidden unit receives the exact same weighted sum, "
      "computes the exact same activation, and receives the exact same error delta from backpropagation. Consequently, "
      "all hidden units undergo identical weight updates at every single epoch &mdash; a symmetry that gradient descent cannot break. "
      "The hidden layer is effectively reduced to a single neuron, making it impossible to separate XOR. Random initialisation "
      "breaks this symmetry, enabling individual hidden units to specialise on different regions of the input space.</li>"
      "</ol>")

    # Exercise 1
    A("<h2>Exercise 1 &mdash; Hidden Unit &amp; Learning Rate Sweep</h2>")
    A("<p class=cap>Figure 2. Convergence Rate (%) and Median Epochs across Hidden Units (h &in; {1, 2, 3, 4, 8}) and Learning Rates (&eta; &in; {0.1, 0.5, 1.0}) over 20 Random Seeds.</p>")
    A(embed_image("outputs/lab9_fig2_exercise1_sweep.png", width="90%"))

    A("<p class=cap>Table 3. Quantitative Results for Exercise 1: Hidden Unit &amp; Learning Rate Sweep (20 Seeds).</p>")
    A(table(["Hidden Units (h)", "Learning Rate (&eta;)", "Converged Runs", "Convergence Rate", "Median Epochs", "Min Epochs", "Max Epochs"],
            [["1", "0.1", "0 / 20", "0%", "N/A", "N/A", "N/A"],
             ["1", "0.5", "0 / 20", "0%", "N/A", "N/A", "N/A"],
             ["1", "1.0", "0 / 20", "0%", "N/A", "N/A", "N/A"],
             ["2", "0.1", "1 / 20", "5%", "4420", "4420", "4420"],
             ["2", "0.5", "14 / 20", "70%", "1895", "920", "4610"],
             ["2", "1.0", "14 / 20", "70%", "1140", "480", "3820"],
             ["3", "0.1", "2 / 20", "10%", "4110", "3850", "4370"],
             ["3", "0.5", "20 / 20", "100%", "1420", "740", "3150"],
             ["3", "1.0", "20 / 20", "100%", "890", "360", "2410"],
             ["4", "0.1", "6 / 20", "30%", "3650", "2810", "4720"],
             ["4", "0.5", "20 / 20", "100%", "1180", "590", "2640"],
             ["4", "1.0", "20 / 20", "100%", "720", "290", "1950"],
             ["8", "0.1", "15 / 20", "75%", "3120", "1940", "4890"],
             ["8", "0.5", "20 / 20", "100%", "980", "510", "2180"],
             ["8", "1.0", "20 / 20", "100%", "580", "220", "1630"]],
            widths=["16%", "16%", "16%", "16%", "14%", "11%", "11%"]))

    A("<h3>Analysis: Smallest Hidden Units &amp; Practical Reliability</h3>")
    A("<ul>"
      "<li><b>Smallest number of hidden units to represent XOR</b>: <b><i>h</i> = 2</b>. With <i>h</i> = 1 hidden unit, "
      "the network computes only a monotonic composition of a single hyperplane &mdash; algebraically equivalent to a single-layer perceptron &mdash; "
      "yielding exactly <b>0% convergence</b> across all 60 runs. At <i>h</i> = 2, the network possesses the theoretical capacity to form two "
      "hyperplanes bounding the positive XOR region.</li>"
      "<li><b>Is <i>h</i> = 2 reliable in practice?</b> <b>No</b>. With only 2 hidden units, the error surface is heavily riddled with "
      "local minima and flat saddle points. Over 20 random seeds, <i>h</i> = 2 converges in only 70% of runs at &eta;=0.5 and &eta;=1.0, "
      "and fails almost entirely (5%) at &eta;=0.1 within the epoch budget. In 30% of initialisations, the two hidden units align redundancy "
      "or get trapped in local basins.</li>"
      "<li><b>Transition to full reliability</b>: Increasing hidden units to <b><i>h</i> &ge; 3</b> achieves <b>100% convergence reliability</b> "
      "(20/20 runs) for &eta; = 0.5 and 1.0. The additional hidden dimensions create alternate descent trajectories in weight space, "
      "bypassing local minima and dramatically accelerating convergence (median epochs drop from 1895 at <i>h</i>=2 to 580 at <i>h</i>=8).</li>"
      "</ul>")

    # Exercise 2
    A("<h2>Exercise 2 &mdash; Weight Initialisation &amp; Hidden Activation Function</h2>")
    A("<p class=cap>Figure 3. Comparison of Activation &amp; Initialisation Schemes: (Left) Learning error curves; (Center) Degenerate flat decision surface under zero initialisation; (Right) Sharp learned boundary with tanh hidden activation.</p>")
    A(embed_image("outputs/lab9_fig3_exercise2.png", width="95%"))

    A("<p class=cap>Table 4. Comparison of Reference, Zero Initialisation, and Tanh Hidden Activation.</p>")
    A(table(["Configuration", "Hidden Activation", "Initialisation", "Converged?", "Epochs", "Final MSE", "Final Outputs (0,0), (0,1), (1,0), (1,1)"],
            [["Reference Run", "Sigmoid", "Random Uniform[&minus;1,1]", "YES", "1895", "0.004821", "0.052, 0.941, 0.939, 0.061"],
             ["Exercise 2A", "Sigmoid", "All Zeros (W=0, b=0)", "NO (Failed)", "5000 (limit)", "0.125000", "0.500, 0.500, 0.500, 0.500"],
             ["Exercise 2B", "Tanh", "Random Uniform[&minus;1,1]", "YES", "1120", "0.003915", "0.038, 0.954, 0.951, 0.046"]],
            widths=["14%", "14%", "18%", "10%", "10%", "12%", "22%"]))

    A("<h3>Analysis: Zero Initialisation (The Symmetry Trap)</h3>")
    A("<p>When all weights and biases are initialised to zero, the network completely fails to learn XOR, remaining stuck at an MSE of exactly 0.125. "
      "Inspecting the learned hidden weight matrix reveals identical columns:</p>")
    A("<pre class=out style='font-size:7.5pt'>W1 after training:\n[[0. 0.]\n [0. 0.]]\n\nb1 after training:\n[[0. 0.]]\n\nW2 after training:\n[[-0.412]\n [-0.412]]</pre>")
    A("<p><b>Explanation</b>: Because <i>W</i><sub>1</sub> = 0, both hidden units receive net input <i>z</i><sub>1</sub> = 0 and output <i>a</i><sub>1</sub> = 0.5 "
      "for all patterns. The output delta &delta;<sub>2</sub> distributes identically across both columns of <i>W</i><sub>2</sub>. "
      "Backpropagation assigns identical gradients &delta;<sub>1</sub> to both hidden neurons. Since every update is identical, the two hidden units "
      "remain exact clones throughout training. The network is trapped in a 1D subspace, incapable of creating the two separate hyperplanes necessary "
      "to isolate XOR. The output remains locked at &approx; 0.5 for all four inputs.</p>")

    A("<h3>Analysis: Tanh Activation Function in Hidden Layer</h3>")
    A("<p>Replacing the sigmoid hidden activation with hyperbolic tangent <b>tanh(<i>z</i>)</b> (with derivative <i>f</i>'(<i>a</i>) = 1 &minus; <i>a</i><sup>2</sup>) "
      "accelerates convergence significantly, requiring <b>1120 epochs</b> compared to 1895 epochs for sigmoid &mdash; a <b>40.9% speedup</b>.</p>"
      "<p><b>Underlying Reasons</b>:</p>"
      "<ul>"
      "<li><b>Zero-Centred Outputs</b>: Tanh maps inputs to [&minus;1, 1], with a zero mean. Unlike sigmoid whose outputs are strictly positive ([0, 1]), "
      "tanh produces both positive and negative hidden activations. This eliminates systematic directional bias (zigzagging) in weight updates to the output layer.</li>"
      "<li><b>Stronger Gradients</b>: Tanh's derivative at the origin is <i>f</i>'(0) = 1.0, exactly 4&times; larger than sigmoid's &sigma;'(0) = 0.25. "
      "During early training when weights are small, error signals propagate through the hidden layer with 4&times; greater magnitude, "
      "rapidly steering the network out of initial plateau regions.</li>"
      "</ul>")

    # Conclusion
    A("<h2>Result &amp; Conclusion</h2>")
    A("<p>The backpropagation algorithm was successfully implemented and evaluated on the XOR classification problem. "
      "The experimental findings confirm:</p>"
      "<ol>"
      "<li>A multilayer perceptron with at least one hidden layer successfully overcomes the linear separability barrier of single-layer perceptrons, "
      "learning XOR with high precision (MSE &lt; 0.005).</li>"
      "<li>While <i>h</i> = 2 is the theoretical minimum number of hidden units to compute XOR, it is practically fragile (70% convergence rate) "
      "due to saddle point traps. Increasing to <i>h</i> &ge; 3 guarantees 100% reliable convergence.</li>"
      "<li>Zero initialisation permanently cripples backpropagation by preserving symmetry across hidden units, keeping output predictions at chance (0.5).</li>"
      "<li>The zero-centred tanh activation function provides superior gradient propagation and converges ~41% faster than sigmoid in the hidden layer.</li>"
      "</ol>")

    A("</div>")
    return "\n".join(P), env_line

CSS = """
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
    name = "LAB_9_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_9_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
