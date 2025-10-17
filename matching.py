# matching.py
# Distance + ranking utilities for power-profile matching

from math import sqrt

BASES = ["Legitimate", "Reward", "Coercive", "Referent", "Expert", "Informational"]

def euclidean_match_percent(user_scores: dict, profile_scores: dict, weights: dict | None = None):
    """
    Compute weighted Euclidean distance between user_scores and profile_scores (1..5 scale per base),
    then convert it to a 0..100% match where 100% is identical.
    """
    if weights is None:
        weights = {}

    acc = 0.0
    wsum = 0.0
    for base in BASES:
        w = float(weights.get(base, 1.0))
        u = float(user_scores.get(base, 0))
        p = float(profile_scores.get(base, 0))
        acc += w * (u - p) ** 2
        wsum += w

    d = sqrt(acc)
    # Max possible difference per base is 4 (from 1..5 scale)
    dmax = 4.0 * (wsum ** 0.5) if wsum > 0 else 1.0
    match = max(0.0, 1.0 - d / dmax) * 100.0
    return d, match

def rank_profiles(user_scores: dict, profiles: list[dict], weights: dict | None = None, top_k: int | None = None):
    """
    Rank profiles by match% descending.
    Each profile is expected to have a 'name' (str) and 'scores' (dict of base->1..5).
    Returns a list of dicts: {"id", "name", "match_percent"} sorted desc.
    """
    results = []
    for p in profiles:
        _, m = euclidean_match_percent(user_scores, p["scores"], weights)
        results.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "match_percent": round(m, 1)
        })
    results.sort(key=lambda r: r["match_percent"], reverse=True)
    return results[:top_k] if top_k else results
