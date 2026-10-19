"""Signal sources. Each adapter returns a list of signal dicts.

In this demo every adapter reads a mock JSON file. In production each one
would call a real, permitted source (an RSS feed, a job-board API, a public
registry, a compliant LinkedIn export, or a person pasting a URL).
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "sources"

SOURCES = {
    "google_news": "Google News alerts (RSS)",
    "job_boards": "Job postings (public job-board feeds)",
    "ai_act_registry": "EU AI Act registry (high-risk AI systems)",
    "linkedin_keywords": "LinkedIn keyword listener (compliant export)",
    "manual_input": "Manual input (URL or company)",
}


def load_source(name):
    with open(DATA / f"{name}.json", encoding="utf-8") as f:
        signals = json.load(f)
    for s in signals:
        s["source"] = name
    return signals


def collect_all():
    signals = []
    for name in SOURCES:
        signals.extend(load_source(name))
    return signals
