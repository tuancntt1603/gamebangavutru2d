import json
import os

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'leaderboard.json')

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_score(score, pilot_name="Unknown Pilot"):
    scores = load_leaderboard()
    scores.append({"name": pilot_name, "score": score})
    # Sort by score descending
    scores.sort(key=lambda x: x["score"], reverse=True)
    # Keep top 10
    scores = scores[:10]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(scores, f, indent=4)
    return scores
