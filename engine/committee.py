"""Buying-committee selection with non-repetition rules."""
from datetime import date

# Which role should hear about which trigger, in order of preference.
ROLE_PREFERENCE = {
    "ai_act_registration": ["governance", "economic_buyer", "technical_evaluator"],
    "ai_rollout": ["strategic_buyer", "governance", "technical_evaluator"],
    "keyword_post": ["governance", "strategic_buyer", "technical_evaluator"],
    "hiring_ai_governance": ["governance", "economic_buyer", "strategic_buyer"],
    "new_exec": ["governance", "economic_buyer", "strategic_buyer"],
    "regulation": ["economic_buyer", "governance", "strategic_buyer"],
}

PERSON_COOLDOWN_DAYS = 30   # don't contact the same person twice within a month
ANGLE_COOLDOWN_DAYS = 45    # don't reuse the same angle at the same account


def pick_persona(row, history, angle, today):
    acc_id = row["account"]["account_id"]
    trigger = row["best_signal"]["type"]
    recent = [h for h in history if h["account_id"] == acc_id]

    for h in recent:
        if h["angle"] == angle and (today - date.fromisoformat(h["date"])).days < ANGLE_COOLDOWN_DAYS:
            return None, f"angle '{angle}' used {(today - date.fromisoformat(h['date'])).days}d ago at this account"

    for role in ROLE_PREFERENCE.get(trigger, []):
        for p in row["contacts"]:
            if p["role"] != role:
                continue
            last = [h for h in recent if h["persona"] == p["name"]]
            if last and (today - date.fromisoformat(last[-1]["date"])).days < PERSON_COOLDOWN_DAYS:
                continue
            return p, f"{role} matches trigger '{trigger}'"
    return None, "all suitable stakeholders contacted recently"
