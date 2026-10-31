"""
The decoding strategies compared in the project.

Every function takes `preds`, the extracted answers of one question's
samples in the order they were drawn (None = no answer found), and returns

    (answer, samples_used, rounds)

where `rounds` is the number of sequential requests the strategy needs:
a strategy that asks for all its samples at once needs one round, a strategy
that looks at the answers before deciding to continue needs one round per
look. Nothing here calls the model, so the same functions drive both the
offline evaluation (evaluate.py) and the live demo (demo.py).
"""

from collections import Counter
from math import comb


def vote(preds):
    """Majority answer. Unparsed samples do not vote; ties go to the answer
    that appeared first, so the result does not depend on dict ordering."""
    counts = Counter(p for p in preds if p is not None)
    if not counts:
        return None
    best = max(counts.values())
    for p in preds:
        if p is not None and counts[p] == best:
            return p


# --- baseline --------------------------------------------------------------

def sc(preds, k):
    """Self-consistency (Wang et al., 2023): k samples in one request."""
    return vote(preds[:k]), k, 1


# --- method under study ----------------------------------------------------

def window_is_unanimous(window):
    return window[0] is not None and all(p == window[0] for p in window)


def esc(preds, w, L):
    """Early-stopping self-consistency (Li et al., 2024, Algorithm 1).

    Samples are drawn in windows of w. If every answer in a window is the
    same, sampling stops and that answer is returned. Otherwise the window is
    added to the candidates and the next one is drawn; after L // w windows
    the candidates are voted on, exactly as SC would.
    """
    candidates = []
    n_windows = L // w
    for j in range(n_windows):
        window = preds[j * w:(j + 1) * w]
        if window_is_unanimous(window):
            return window[0], (j + 1) * w, j + 1
        candidates += window
    return vote(candidates), n_windows * w, n_windows


def esc_stop_round(preds, w, L):
    """Index of the window ESC stopped in, or None if it ran to the budget."""
    for j in range(L // w):
        if window_is_unanimous(preds[j * w:(j + 1) * w]):
            return j
    return None


# --- second adaptive rule, for context -------------------------------------

def beta_confidence(v1, v2):
    """P(p1 > p2) under a Beta(v1 + 1, v2 + 1) posterior.

    For integer parameters the Beta tail is a binomial sum:
    P(X > 1/2) = P(Bin(a + b - 1, 1/2) <= a - 1), with a = v1 + 1, b = v2 + 1.
    """
    a, b = v1 + 1, v2 + 1
    n = a + b - 1
    return sum(comb(n, j) for j in range(a)) / 2 ** n


def adaptive_consistency(preds, L, threshold=0.95):
    """Adaptive-Consistency with the Beta stopping rule (Aggarwal et al.,
    2023). One sample per request; stop when the leading answer beats the
    runner-up with posterior probability above the threshold."""
    for n in range(1, L + 1):
        counts = Counter(p for p in preds[:n] if p is not None).most_common(2)
        v1 = counts[0][1] if counts else 0
        v2 = counts[1][1] if len(counts) > 1 else 0
        if v1 and beta_confidence(v1, v2) > threshold:
            return vote(preds[:n]), n, n
    return vote(preds[:L]), L, L
