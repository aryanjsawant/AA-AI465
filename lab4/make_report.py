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
    src_corpus = read(os.path.join(HERE, "corpus.py"))
    doc_texts = {name: read(os.path.join(HERE, "docs", name))
                 for name in ["doc1_bfs.txt", "doc2_ucs.txt", "doc3_tfidf.txt", "doc4_rag.txt"]}
    src_main = read(os.path.join(HERE, "exp4_rag_pipeline.py"))
    src_ex = read(os.path.join(HERE, "exp4_exercises.py"))

    o_main = run_program("exp4_rag_pipeline.py")
    o_ex = run_program("exp4_exercises.py")

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
    A("<p class=course>Agentic AI (AI465) &mdash; Semester VII</p>")
    A("<hr>")
    A(table(["Name", "Roll No.", "Experiment", "Date"],
            [[STUDENT_NAME or "&nbsp;", roll, "4", stamp.split(",")[0]]]))
    A("<h1>Experiment 4</h1>")
    A("<h1 class=sub>Retrieval-Augmented Generation &mdash; Grounding an "
      "Agent in a Document Store</h1>")

    A("<h2>Aim</h2>")
    A("<p>To build a retrieval-augmented generation pipeline &mdash; chunk "
      "a corpus, vectorise it into a store, retrieve the nearest chunks for "
      "a query and assemble a grounded prompt &mdash; and to compare its "
      "cited answers against an ungrounded baseline.</p>")

    A("<h2>Theory</h2>")
    A("<p>A language model carries its knowledge in its weights. That "
      "knowledge is fixed at training time, cannot be audited, and is "
      "produced with the same fluency whether the model has the fact or is "
      "inventing it. Retrieval-augmented generation moves the knowledge "
      "out of the weights and into a store the developer controls: the "
      "corpus is split into chunks, each chunk is turned into a vector, "
      "and at query time the chunks nearest the question are fetched and "
      "pasted into the prompt as evidence. The model's task narrows from "
      "recall to reading comprehension, the corpus can be updated without "
      "retraining, and because every retrieved chunk carries its source "
      "identifier, each answer can be traced back to the text that "
      "supports it.</p>")
    A("<p>This experiment implements the retrieval half completely and "
      "scripts the generation step, so the whole pipeline is visible "
      "without an API key or network access. The chunks are vectorised "
      "with TF-IDF and searched by cosine similarity; substituting dense "
      "sentence embeddings and a FAISS index replaces only the vectoriser "
      "and the search call, and leaves the chunking, context assembly and "
      "citation logic unchanged.</p>")
    A("<p>Note the two limitations visible in the sample run. First, "
      "top-k retrieval always returns k chunks, even for a question the "
      "corpus cannot answer, so the pipeline will ground an answer in "
      "whatever text happened to score highest; a similarity threshold is "
      "needed before the pipeline is allowed to answer at all (Exercise "
      "1). Second, retrieval can only return what chunking has made "
      "retrievable &mdash; a chunk boundary that cuts an answer in half "
      "makes that answer unreachable at any k (Exercise 2). Note also that "
      "the pipeline here retrieves exactly once per query; the agentic "
      "variant, where the agent itself decides when to retrieve inside a "
      "reasoning loop, is taken up in a later experiment.</p>")

    A("<p class=cap>Table 1. Stages of the pipeline and the design choice "
      "each one carries.</p>")
    A(table(["Stage", "What it produces", "Design choice exercised here"],
            [["Chunking",
              "A list of text chunks, each tagged with its source document "
              "and position",
              "Chunk size and overlap, in sentences"],
             ["Vectorisation", "One vector per chunk",
              "TF-IDF over the corpus vocabulary, with stop words removed"],
             ["Indexing",
              "The vector store &mdash; the chunk matrix searched at query "
              "time",
              "Exhaustive search over a dense matrix, in place of an "
              "approximate index"],
             ["Retrieval", "The top-k chunks with their similarity scores",
              "Value of k, and the cosine similarity measure"],
             ["Context assembly",
              "A grounded prompt: instruction, cited chunks, question",
              "Citation format and the instruction to use only the "
              "supplied context"],
             ["Generation", "The final answer with its source tag",
              "Scripted stand-in for the model, so the retrieval is what "
              "is being measured"]],
            widths=["14%", "38%", "48%"]))

    A("<h2>Algorithm</h2>")
    A("<ol>"
      "<li>Build the index: split every document in the corpus into "
      "overlapping chunks, tag each chunk with its source document and "
      "position, vectorise all chunks together, and keep the resulting "
      "matrix as the vector store.</li>"
      "<li>Answer a query: vectorise the query, score it by cosine "
      "similarity against every chunk, take the top-k, assemble a "
      "grounded prompt from those chunks and their source tags, and print "
      "the cited answer next to the answer the same question receives "
      "with no retrieval at all.</li>"
      "</ol>")
    A(code("class VectorStore:\n"
           "    def __init__(self, chunks):\n"
           "        self.chunks = chunks\n"
           "        self.vectorizer = TfidfVectorizer(stop_words=\"english\")\n"
           "        self.matrix = self.vectorizer.fit_transform([c[\"text\"] for c in chunks])\n\n"
           "    def search(self, query, k=3):\n"
           "        q_vec = self.vectorizer.transform([query])\n"
           "        scores = cosine_similarity(q_vec, self.matrix)[0]\n"
           "        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)\n"
           "        return [(self.chunks[i], float(scores[i])) for i in ranked[:k]]",
           size="8.5pt"))

    A(PAGEBREAK)
    A("<h3>Corpus</h3>")
    A("<p>A small fixed corpus of four documents on related but distinct "
      "topics (BFS, uniform-cost search, TF-IDF, and RAG itself), checked "
      "into <span class=m>docs/</span> as plain <span class=m>.txt</span> "
      "files, so that retrieval has real signal to discriminate on and "
      "out-of-corpus questions have no chunk that legitimately matches.</p>")
    for name, text in doc_texts.items():
        A(f"<p class=cap>docs/{name}</p>")
        A(out(text, size="8.5pt"))
    A("<p>Loaded by <span class=m>corpus.py</span>:</p>")
    A(code(src_corpus))

    A(PAGEBREAK)
    A("<h2>Procedure and Result</h2>")
    A("<h3>Program &mdash; exp4_rag_pipeline.py</h3>")
    A(code(src_main))

    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A("<p class=cap>Snapshot of the console output "
      "(%s), including the number of chunks indexed and, for every query, "
      "the retrieved chunks with their similarity scores, the grounded "
      "answer with citation, and the ungrounded baseline.</p>" % html.escape(env_line))
    A(out(o_main))

    A(PAGEBREAK)
    A("<h2>Observations</h2>")
    A("<h3>1. What the similarity scores tell you about retrieval "
      "confidence</h3>")
    A("<p>The four questions the corpus can actually answer retrieve their "
      "best chunk with a cosine similarity between 0.34 and 0.63, and in "
      "every case the correct fact sits in the highest-scoring chunk. The "
      "two questions the corpus cannot answer (quicksort's complexity, who "
      "invented the transformer) retrieve chunks that score at most 0.17, "
      "and several score exactly 0.000 &mdash; the query shares no "
      "vocabulary at all with those chunks after stop-word removal. The "
      "score is therefore a genuine, usable confidence signal: a high "
      "score means the retrieved text and the query share substantial "
      "TF-IDF-weighted vocabulary, while a near-zero score means the "
      "retriever found the least-irrelevant chunk in the store, not a "
      "relevant one, purely because top-k retrieval must return something.</p>")

    A("<h3>2. How the grounded and baseline answers differ in content and "
      "traceability</h3>")
    A("<p>On questions the corpus covers, both answers are correct, but "
      "only the grounded answer carries a citation tag such as "
      "<span class=m>[doc3_tfidf.txt#0]</span> pointing at the exact chunk "
      "that supports it &mdash; the ungrounded baseline states the same "
      "fact with no way to check where it came from. The difference "
      "becomes qualitative, not just cosmetic, on the two out-of-corpus "
      "questions: the ungrounded baseline answers quicksort's complexity "
      "and the transformer's inventor fluently and confidently from its "
      "parametric memory, with no indication that the corpus has nothing "
      "to do with either answer, while the grounded pipeline (once "
      "instructed to use only the supplied context) has no fact to point "
      "to and can only report that the retrieved context does not answer "
      "the question. Traceability is what exposes this: an ungrounded "
      "answer is equally fluent whether it is right or fabricated, and "
      "nothing in its output distinguishes the two cases.</p>")

    A("<h3>3. What happens to the retrieved set as k is increased</h3>")
    A("<p>Increasing k does not change the top-ranked chunk or its score "
      "&mdash; cosine similarity is computed independently for every chunk "
      "&mdash; it only widens the window of chunks appended to the "
      "context. For the answerable questions this mostly adds "
      "near-duplicate overlapping chunks from the same source document "
      "(visible above as consecutive <span class=m>#position</span> tags "
      "from one file), since the overlapping-chunk scheme means the "
      "sentence containing the fact is repeated across two or three "
      "adjacent chunks. For the unanswerable questions, a larger k does "
      "not surface a better chunk from elsewhere &mdash; it simply appends "
      "more low- or zero-score chunks to the context, which is precisely "
      "why a top-k pipeline with no threshold will happily assemble a "
      "confident-looking prompt out of chunks that have nothing to do with "
      "the question, motivating Exercise 1.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 1 &mdash; Similarity threshold / abstention</h2>")
    A("<p><b>Task.</b> Add a similarity threshold so that the pipeline "
      "abstains &mdash; reporting that the answer is not in the corpus "
      "&mdash; whenever the best retrieved chunk scores below it. Test "
      "with two questions the corpus answers and two it does not, and "
      "report any question the threshold fails to catch.</p>")
    A("<p><b>Approach.</b> <span class=m>answer_with_threshold()</span> "
      "runs retrieval as normal, then compares the top chunk's score "
      "against a fixed threshold of 0.20 &mdash; chosen because it sits "
      "clearly above the highest score any unanswerable question in the "
      "sample run reached (0.168) and clearly below the lowest score any "
      "answerable question reached (0.338). Below the threshold the "
      "pipeline reports abstention instead of calling the scripted "
      "generator at all.</p>")
    A("<h3>Program &mdash; exp4_exercises.py</h3>")
    A(code(src_ex))
    A(PAGEBREAK)
    A("<h3>Output</h3>")
    A(out(o_ex))
    A("<h3>Discussion</h3>")
    A("<p>At threshold=0.20 all four test questions are handled correctly: "
      "both answerable questions score well above the threshold and are "
      "answered normally, and both unanswerable questions score below it "
      "(0.168 and 0.000) and are correctly abstained on. No question in "
      "this test set is missed. The margin is comfortable rather than "
      "razor-thin, but it is corpus-specific: a larger or more topically "
      "overlapping corpus could push an unanswerable question's best "
      "score above 0.20 by accident (a near-miss topic sharing vocabulary "
      "with the query), which is why a shipped system would tune this "
      "threshold against a held-out set of known-answerable and "
      "known-unanswerable questions rather than fixing it by inspection of "
      "one sample run.</p>")

    A(PAGEBREAK)
    A("<h2>Exercise 2 &mdash; Chunk size and overlap sweep</h2>")
    A("<p><b>Task.</b> Vary the chunk size and overlap over at least four "
      "settings, and for a fixed set of questions report the rank and "
      "similarity score of the chunk that actually contains the answer. "
      "State which setting you would ship and why.</p>")
    A("<p><b>Approach.</b> Four (chunk_size, overlap) settings in "
      "sentences were tried: (1, 0), (2, 0), (2, 1) &mdash; the shipped "
      "default &mdash; and (4, 2). For each of four fixed questions, the "
      "rank and score of the first retrieved chunk whose text contains the "
      "key supporting fact was recorded (searched over the top-5, since a "
      "coarser chunking changes how many chunks exist at all).</p>")
    A("<p>See the &ldquo;Exercise 2&rdquo; section of the output above for "
      "the full sweep. The chunk_size=1/overlap=0 setting is the one that "
      "breaks: the uniform-cost-search finality fact is worded across two "
      "adjacent sentences in the corpus, so with single-sentence chunks "
      "and no overlap that fact is split across two separate chunks and "
      "the best matching chunk falls to rank 4 instead of rank 1 &mdash; a "
      "direct, concrete demonstration that retrieval can only return what "
      "chunking has made retrievable. Every 2-sentence setting keeps that "
      "fact whole in one chunk and recovers rank 1 with a substantially "
      "higher score.</p>")
    A("<h3>Setting to ship</h3>")
    A("<p><b>chunk_size=2, overlap=1</b> is the setting to ship. "
      "chunk_size=2/overlap=0 scores marginally higher on this small "
      "corpus, but it relies on the sentence boundaries happening to align "
      "with each fact; a one-sentence overlap costs only a modest increase "
      "in chunk count (13 vs. 9 chunks here) and directly guards against "
      "the same failure mode that broke the 1-sentence setting, should a "
      "future fact in the corpus straddle a 2-sentence boundary instead. "
      "The largest setting (4, 2) does not miss any fact in this small "
      "corpus because each document is short enough that a 4-sentence "
      "window still isolates one topic, but its wider window would "
      "increasingly dilute the TF-IDF vector with unrelated sentences on a "
      "longer, more varied corpus, which is a risk not worth taking for "
      "the small score gain it shows on two of the four questions here.</p>")

    A(PAGEBREAK)
    A("<h2>Conclusion</h2>")
    A("<p>A retrieval-augmented generation pipeline was implemented end to "
      "end: sentence-based chunking with configurable size and overlap, "
      "TF-IDF vectorisation with an exhaustive cosine-similarity search "
      "acting as the vector store, top-k retrieval, grounded-prompt "
      "assembly with source citations, and a scripted generation step that "
      "answers only from retrieved evidence, compared side by side against "
      "an ungrounded baseline drawing on a fixed parametric memory. The "
      "central result was visible in the similarity scores themselves: "
      "answerable questions retrieved supporting chunks scoring "
      "0.34&ndash;0.63, while unanswerable questions retrieved chunks "
      "scoring at most 0.17, giving retrieval confidence a concrete, "
      "usable number rather than a qualitative impression.</p>")
    A("<p>The two exercises then closed the pipeline's two structural "
      "gaps. Exercise 1 added a similarity threshold so the pipeline can "
      "refuse to answer when the best retrieved chunk is not actually "
      "relevant, rather than confidently grounding an answer in whatever "
      "chunk happened to score highest; a threshold of 0.20 correctly "
      "separated all four test questions with no misses. Exercise 2 swept "
      "chunk size and overlap and showed the second gap directly: with "
      "single-sentence chunks and no overlap, a fact worded across two "
      "adjacent sentences became split across two chunks and dropped from "
      "rank 1 to rank 4, while every setting using two-sentence chunks "
      "kept the fact whole and recovered top rank &mdash; concrete "
      "evidence that chunking, not just the similarity measure, bounds "
      "what a RAG pipeline can ever retrieve.</p>")

    A("<h2>Execution environment and declaration</h2>")
    A(table(["Item", "Detail"],
            [["Execution", html.escape(env_line)],
             ["Files",
              "docs/doc1_bfs.txt, docs/doc2_ucs.txt, docs/doc3_tfidf.txt, "
              "docs/doc4_rag.txt, corpus.py, exp4_rag_pipeline.py, "
              "exp4_exercises.py, make_report.py"],
             ["Libraries used",
              "scikit-learn (<span class=m>TfidfVectorizer</span>, "
              "<span class=m>cosine_similarity</span>) for vectorisation "
              "and similarity scoring; Python standard library "
              "(<span class=m>re</span>) for sentence splitting. No agent "
              "framework, orchestration library, or external API/network "
              "access was used, in accordance with clause 3.1 of the Rules "
              "and Regulations."],
             ["Reproducibility",
              "The corpus, queries, chunk settings and threshold are all "
              "fixed, and TF-IDF/cosine similarity are deterministic, so "
              "every run of every program reproduces exactly."],
             ["Sources consulted",
              "Course manual for Experiment 4 (retrieval-augmented "
              "generation pipeline, TF-IDF, cosine similarity, chunking "
              "trade-offs)."]],
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
    name = "LAB_4_%s.doc" % roll
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE % {"title": "LAB_4_%s" % roll,
                             "css": CSS, "body": body})
    print()
    print("Written : %s" % path)
    print("Traces  : %s" % OUTDIR)
    print("Run     : %s" % env_line)
    print()
    print("Open the .doc in Word, check it, and submit.")
