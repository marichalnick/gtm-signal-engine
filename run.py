"""Signal-to-Outreach Engine: run the full pipeline on the demo data.

    python run.py                    # uses the fixed demo date
    python run.py --today 2026-11-01 # see how signals decay over time
"""
import argparse
import csv
from datetime import date
from pathlib import Path

from engine.sources import SOURCES, collect_all
from engine.scoring import tier_accounts
from engine.committee import pick_persona
from engine.messaging import PLAYBOOK, draft
from engine.report import rate

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"


def read_csv(name):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default="2026-10-19")
    today = date.fromisoformat(ap.parse_args().today)

    accounts = read_csv("accounts.csv")
    for a in accounts:
        a["employees"] = int(a["employees"])
        a["ai_maturity"] = int(a["ai_maturity"])
        a["regulated"] = a["regulated"] == "yes"
    personas = read_csv("personas.csv")
    history = read_csv("outreach_history.csv")

    # 1-2. Collect signals from all sources
    signals = collect_all()
    # 3-4. Verify, decay, score and tier
    tiered = tier_accounts(accounts, signals, personas, today)

    OUT.mkdir(exist_ok=True)
    shortlist = [f"# Shortlist ({today})\n",
                 "| Tier | Account | Sector | Fit | Score | Reason |",
                 "|---|---|---|---:|---:|---|"]
    for r in tiered:
        a = r["account"]
        shortlist.append(f"| {r['tier']} | {a['name']} | {a['sector']} | {r['fit']} | {r['score']} | {r['reason']} |")

    verify = [r for r in tiered if r["unverified"]]
    if verify:
        shortlist.append("\n## Needs human verification before use\n")
        for r in verify:
            for s in r["unverified"]:
                shortlist.append(f"- **{r['account']['name']}**: {s['headline']} ({s['source']}, secondary source)")

    # 5-7. Pick a stakeholder, draft, queue for human review
    drafts, log_rows = [f"# Drafts for review ({today})\n",
                        "Nothing is sent automatically. Approve, edit or reject each draft.\n"], []
    for r in tiered:
        if r["tier"] not in ("Tier 1", "Tier 2"):
            continue
        angle = PLAYBOOK[r["best_signal"]["type"]]["angle"]
        persona, why = pick_persona(r, history, angle, today)
        a = r["account"]
        if persona is None:
            drafts.append(f"## {a['name']}: skipped\n{why}. Consider a different angle or stakeholder.\n")
            continue
        angle, hypothesis, body = draft(r, persona)
        s = r["best_signal"]
        drafts.append(
            f"## {a['name']} → {persona['name']}, {persona['title']} ({r['tier']})\n"
            f"- **Trigger:** {s['headline']} ({s['source']}, {s['age_days']} days old, {s['url']})\n"
            f"- **Why this person:** {why}\n"
            f"- **Pain hypothesis:** {hypothesis}\n\n"
            f"```\n{body}\n```\n- [ ] approve  - [ ] edit  - [ ] reject\n")
        log_rows.append({"date": today.isoformat(), "account_id": a["account_id"], "persona": persona["name"],
                         "trigger_type": s["type"], "angle": angle, "cta": "calendar_link",
                         "replied": "", "meeting": ""})

    # 8. Attribution on past outreach
    report = [f"# Attribution report (history up to {today})\n",
              "Synthetic demo history (10 touches). Small sample: read this as direction, not proof.\n",
              "## By trigger\n", rate(history, "trigger_type"),
              "\n## By angle\n", rate(history, "angle"),
              "\n## By call to action\n", rate(history, "cta")]

    (OUT / "shortlist.md").write_text("\n".join(shortlist) + "\n", encoding="utf-8")
    (OUT / "drafts.md").write_text("\n".join(drafts) + "\n", encoding="utf-8")
    (OUT / "attribution_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    with open(OUT / "new_outreach_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log_rows[0]) if log_rows else ["date"])
        w.writeheader()
        w.writerows(log_rows)

    counts = {}
    for r in tiered:
        counts[r["tier"]] = counts.get(r["tier"], 0) + 1
    print(f"Sources: {len(SOURCES)} | signals: {len(signals)} | accounts: {len(accounts)}")
    print("Tiers: " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
    print(f"Drafts queued for review: {len(log_rows)}")
    print("Wrote output/shortlist.md, output/drafts.md, output/attribution_report.md")


if __name__ == "__main__":
    main()
