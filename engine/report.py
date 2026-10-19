"""Attribution: what actually converts, per trigger, persona role and CTA."""
from collections import defaultdict


def rate(rows, key):
    groups = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        g = groups[r[key]]
        g[0] += 1
        g[1] += r["replied"] == "yes"
        g[2] += r["meeting"] == "yes"
    lines = [f"| {key} | sent | reply rate | meeting rate |", "|---|---:|---:|---:|"]
    for k, (n, rep, meet) in sorted(groups.items(), key=lambda kv: -kv[1][2] / kv[1][0]):
        lines.append(f"| {k} | {n} | {rep / n:.0%} | {meet / n:.0%} |")
    return "\n".join(lines)
