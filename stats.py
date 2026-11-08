"""Plain-Python statistics: AUC, bootstrap intervals, Cohen and Fleiss kappa. No dependencies."""
import random
from itertools import combinations


def _ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def auc(scores, labels):
    """P(score of a random positive > score of a random negative), ties count half. None if one class is empty."""
    n_pos = sum(1 for y in labels if y)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = _ranks(list(scores))
    rank_sum = sum(r for r, y in zip(ranks, labels) if y)
    return (rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def tpr_at_fpr(scores, labels, fpr=0.10):
    """Threshold = the (1 - fpr) quantile of the negatives' scores; positive if score is strictly above it.
    Returns (tpr, actual_fpr, threshold). Chosen on the same data, so slightly optimistic."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = sorted(s for s, y in zip(scores, labels) if not y)
    if not pos or not neg:
        return None
    k = min(len(neg) - 1, int(len(neg) * (1 - fpr)))
    thr = neg[k]
    return (sum(s > thr for s in pos) / len(pos), sum(s > thr for s in neg) / len(neg), thr)


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def bootstrap(n, stat, n_boot=2000, seed=0):
    """Percentile 95% interval of stat(index_list) over resamples of range(n) with replacement.
    Resamples where stat returns None (e.g. one class missing) are skipped; returns (lo, hi, n_used)."""
    rng = random.Random(seed)
    vals = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        v = stat(idx)
        if v is not None:
            vals.append(v)
    vals.sort()
    if len(vals) < 20:
        return None, None, len(vals)
    return percentile(vals, 0.025), percentile(vals, 0.975), len(vals)


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fleiss_kappa(counts):
    """counts[i][j] = number of raters who put item i in category j; same number of raters per item."""
    N = len(counts)
    if N == 0:
        return None
    n = sum(counts[0])
    if n < 2:
        return None
    P_i = [(sum(c * c for c in row) - n) / (n * (n - 1)) for row in counts]
    Pbar = sum(P_i) / N
    cats = len(counts[0])
    p_j = [sum(row[j] for row in counts) / (N * n) for j in range(cats)]
    Pe = sum(p * p for p in p_j)
    return None if Pe == 1 else (Pbar - Pe) / (1 - Pe)


def mean_pairwise_cohen(labels_by_rater):
    ks = [cohen_kappa(labels_by_rater[i], labels_by_rater[j])
          for i, j in combinations(range(len(labels_by_rater)), 2)]
    ks = [k for k in ks if k is not None]
    return sum(ks) / len(ks) if ks else None


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion k/n. Returns (rate, lo, hi); (None, None, None) if n == 0."""
    if n == 0:
        return None, None, None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)
