"""ICP fit, signal verification, decay and account tiering."""
from datetime import date

SECTOR_WEIGHT = {
    "banking": 1.0, "insurance": 1.0, "asset_management": 0.9, "pharma": 0.9,
    "healthcare": 0.8, "telecom": 0.8, "energy": 0.7, "public_sector": 0.5,
    "retail": 0.5, "logistics": 0.4, "manufacturing": 0.4, "marketing": 0.1,
}

# How strongly a signal type suggests a change in priority.
SIGNAL_STRENGTH = {
    "ai_act_registration": 1.0,  # a concrete compliance obligation exists
    "ai_rollout": 0.9,           # new AI in production = new control questions
    "keyword_post": 0.85,        # a stakeholder said it publicly
    "hiring_ai_governance": 0.8, # budget and ownership are being created
    "new_exec": 0.8,             # first 90 days = open to new priorities
    "regulation": 0.5,           # pressure, but not proof of intent
}

HALF_LIFE_DAYS = 21       # a signal loses half its value every 3 weeks
MIN_CONFIDENCE = 0.7      # below this, a human must verify first
MIN_EMPLOYEES = 250       # disqualifier: too small for this offer
TIER_1, TIER_2 = 40, 20


def icp_fit(acc):
    size = 1.0 if acc["employees"] >= 1000 else 0.6 if acc["employees"] >= MIN_EMPLOYEES else 0.1
    return round(
        0.4 * SECTOR_WEIGHT.get(acc["sector"], 0.3)
        + 0.2 * size
        + 0.2 * acc["ai_maturity"] / 3
        + 0.2 * (1.0 if acc["regulated"] else 0.0), 2)


def confidence(signal):
    """Primary source (company site, registry, the person's own post) = 1.0.
    Secondary or hearsay = 0.5 and goes to manual verification."""
    return 1.0 if signal["primary_source"] else 0.5


def decay(signal, today):
    age = (today - date.fromisoformat(signal["date"])).days
    return round(0.5 ** (age / HALF_LIFE_DAYS), 2), age


def score_signal(signal, today):
    d, age = decay(signal, today)
    c = confidence(signal)
    strength = SIGNAL_STRENGTH.get(signal["type"], 0.3)
    return {**signal, "age_days": age, "decay": d, "confidence": c,
            "signal_score": round(strength * d * c, 2)}


def tier_accounts(accounts, signals, personas, today):
    results = []
    for acc in accounts:
        acc_signals = [score_signal(s, today) for s in signals if s["account_id"] == acc["account_id"]]
        contacts = [p for p in personas if p["account_id"] == acc["account_id"]]
        fit = icp_fit(acc)
        verified = [s for s in acc_signals if s["confidence"] >= MIN_CONFIDENCE]
        unverified = [s for s in acc_signals if s["confidence"] < MIN_CONFIDENCE]
        best = max(verified, key=lambda s: s["signal_score"], default=None)

        if acc["employees"] < MIN_EMPLOYEES:
            tier, reason = "Disqualified", "below minimum company size"
        elif not contacts:
            tier, reason = "Disqualified", "no reachable stakeholders mapped"
        elif best is None and unverified:
            tier, reason = "Verify first", "only unverified signals"
        elif best is None:
            tier, reason = "Nurture", "good fit, no current trigger"
        else:
            score = round(fit * best["signal_score"] * 100)
            tier = "Tier 1" if score >= TIER_1 else "Tier 2" if score >= TIER_2 else "Nurture"
            reason = f"{best['type']} ({best['age_days']}d old)"
        results.append({
            "account": acc, "fit": fit, "contacts": contacts,
            "best_signal": best, "unverified": unverified,
            "score": round(fit * best["signal_score"] * 100) if best else 0,
            "tier": tier, "reason": reason,
        })
    order = {"Tier 1": 0, "Tier 2": 1, "Verify first": 2, "Nurture": 3, "Disqualified": 4}
    return sorted(results, key=lambda r: (order[r["tier"]], -r["score"]))
