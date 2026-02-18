import json
import os

SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")


def load_scores():
    try:
        with open(SCORES_FILE, "r") as f:
            scores = json.load(f)
        scores = [s for s in scores if isinstance(s, dict) and "name" in s and "score" in s]
        scores.sort(key=lambda s: s["score"], reverse=True)
        return scores[:10]
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)


def is_high_score(score):
    scores = load_scores()
    if len(scores) < 10:
        return True
    return score > scores[-1]["score"]
