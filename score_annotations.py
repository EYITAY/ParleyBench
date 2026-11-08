"""Score returned annotation sheets.

  python score_annotations.py --returned annotation/returned --key annotation/annotation_key_PRIVATE.csv

Reads the 'Labels' sheet of every .xlsx in --returned. With one annotator it reports agreement with the automatic
label (Cohen kappa). With two or more it reports Fleiss kappa, mean pairwise Cohen kappa and the share of unanimous
items; with three or more also a leave-one-out Fleiss kappa. Writes majority_labels.csv (input to analyze.py --labels)
and annotation_report.md.
"""
import argparse, csv, glob, os
from collections import Counter
from openpyxl import load_workbook
import stats

ap = argparse.ArgumentParser()
ap.add_argument("--returned", default="annotation/returned")
ap.add_argument("--key", default="annotation/annotation_key_PRIVATE.csv")
ap.add_argument("--out", default="annotation")
a = ap.parse_args()
CATS = ["Yes", "No", "Unclear"]
norm = lambda v: (str(v).strip().capitalize() if v is not None and str(v).strip().capitalize() in CATS else None)

key = {r["item_id"]: r for r in csv.DictReader(open(a.key))}
files = sorted(glob.glob(os.path.join(a.returned, "*.xlsx")))
if not files:
    raise SystemExit(f"No .xlsx files in {a.returned}")
labels = {}
for f in files:
    ws = load_workbook(f, data_only=True)["Labels"]
    d = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            d[str(row[0]).strip()] = norm(row[1])
    labels[os.path.basename(f)[:-5]] = d
raters = sorted(labels)
items = [i for i in key if all(labels[r].get(i) for r in raters)]
dropped = len(key) - len(items)
rep = ["# Annotation report\n", f"{len(raters)} annotator(s): {', '.join(raters)}. {len(items)} items fully labelled"
       f" ({dropped} dropped for missing or invalid labels).\n"]
mat = {r: [labels[r][i] for i in items] for r in raters}
auto = {i: ("Yes" if key[i]["auto_deceptive"] == "True" else "No") for i in key}
f = lambda v: "n/a" if v is None else f"{v:.3f}"
if len(raters) >= 2:
    counts = [[sum(labels[r][i] == c for r in raters) for c in CATS] for i in items]
    rep.append(f"- Fleiss kappa (Yes / No / Unclear): **{f(stats.fleiss_kappa(counts))}**")
    rep.append(f"- Mean pairwise Cohen kappa: {f(stats.mean_pairwise_cohen([mat[r] for r in raters]))}")
    rep.append(f"- Unanimous items: {sum(max(c) == len(raters) for c in counts)} of {len(items)}")
    if len(raters) >= 3:
        rep.append("- Leave-one-out Fleiss kappa (the value when that annotator is removed):")
        for r in raters:
            rest = [x for x in raters if x != r]
            cts = [[sum(labels[x][i] == c for x in rest) for c in CATS] for i in items]
            rep.append(f"  - without {r}: {f(stats.fleiss_kappa(cts))}")
else:
    sub = [(m, auto[i]) for m, i in zip(mat[raters[0]], items) if m in ("Yes", "No")]
    rep.append(f"- Cohen kappa between this annotator and the automatic label: **{f(stats.cohen_kappa([m for m, _ in sub], [x for _, x in sub]))}** (n={len(sub)})")
rows = []
for i in items:
    c = Counter(labels[r][i] for r in raters)
    top = c.most_common()
    maj = top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else "Tie"
    rows.append({"game_id": key[i]["game_id"], "item_id": i, "majority": maj,
                 "yes": c["Yes"], "no": c["No"], "unclear": c["Unclear"], "auto_label": auto[i]})
with open(os.path.join(a.out, "majority_labels.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
cmp_ = [r for r in rows if r["majority"] in ("Yes", "No")]
if cmp_:
    tp = sum(r["majority"] == "Yes" and r["auto_label"] == "Yes" for r in cmp_)
    tn = sum(r["majority"] == "No" and r["auto_label"] == "No" for r in cmp_)
    fp = sum(r["majority"] == "No" and r["auto_label"] == "Yes" for r in cmp_)
    fn = sum(r["majority"] == "Yes" and r["auto_label"] == "No" for r in cmp_)
    rep += ["", "## Human majority vs automatic label", "",
            f"Items with a Yes/No majority: {len(cmp_)}. Agreement {100 * (tp + tn) / len(cmp_):.1f}%.", "",
            "| | auto Yes | auto No |", "| --- | --- | --- |",
            f"| human Yes | {tp} | {fn} |", f"| human No | {fp} | {tn} |", "",
            f"`human Yes, auto No` ({fn}) are lies the automatic label missed. `human No, auto Yes` ({fp}) are false alarms of the automatic label."]
open(os.path.join(a.out, "annotation_report.md"), "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
