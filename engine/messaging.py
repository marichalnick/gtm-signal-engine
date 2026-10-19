"""Turn a verified signal into one relevant question. No product pitch.

Templates keep the logic transparent. In production the draft step can be
handed to an LLM with the same inputs, but a human still approves every message.
"""

PLAYBOOK = {
    "ai_act_registration": {
        "angle": "registry_evidence",
        "hypothesis": "A registered high-risk system means auditors will ask for evidence of oversight, not only a policy.",
        "question": "when the first audit comes, where will the evidence of human oversight for {topic} come from?",
    },
    "ai_rollout": {
        "angle": "agent_visibility",
        "hypothesis": "Scaling AI to thousands of users creates actions nobody explicitly approved.",
        "question": "with {topic}, how will your team see what those assistants actually do with internal data?",
    },
    "keyword_post": {
        "angle": "public_statement",
        "hypothesis": "The stakeholder already named the gap publicly.",
        "question": "you wrote that knowing what your agents actually do is the biggest gap. Is that a tooling gap or an ownership gap today?",
    },
    "hiring_ai_governance": {
        "angle": "team_buildout",
        "hypothesis": "A new governance hire signals budget and ownership, but the role needs tooling to be effective.",
        "question": "now that you're hiring for {topic}, what should that person be able to show the board after 90 days?",
    },
    "new_exec": {
        "angle": "first_90_days",
        "hypothesis": "New leaders review risks and priorities in their first months.",
        "question": "as part of the first 90 days, is AI usage across the business already on your risk map?",
    },
    "regulation": {
        "angle": "ai_act_obligations",
        "hypothesis": "Regulatory pressure exists, but intent is unproven.",
        "question": "who owns {topic} today: IT, legal or risk?",
    },
}

CTA = "If useful, here's a 20-minute slot this week: [calendar link]"  # calendar link beats "send me your number"


def draft(row, persona):
    s = row["best_signal"]
    play = PLAYBOOK[s["type"]]
    first = persona["name"].split()[0]
    q = play["question"].format(topic=s["topic"])
    body = (f"Hi {first},\n\n"
            f"I saw {s['opener']}.\n\n"
            f"Quick question: {q}\n\n"
            f"{CTA}\n\nBest,\nNick")
    return play["angle"], play["hypothesis"], body
