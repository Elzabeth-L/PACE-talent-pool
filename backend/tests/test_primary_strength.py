from collections import Counter


def capability_focus(category_ranks: dict[str, list[int]]) -> str:
    scores = Counter({category: sum(ranks) for category, ranks in category_ranks.items()})
    highest = max(scores.values())
    leaders = [category for category, score in scores.items() if score == highest]
    return leaders[0] if len(leaders) == 1 else "Cross-domain profile"


def test_cross_domain_profile_when_top_categories_are_tied():
    assert capability_focus({"Containers": [3], "CI": [3], "SCM": [3]}) == "Cross-domain profile"


def test_concentrated_category_wins_by_combined_proficiency():
    assert capability_focus({"Testing & QA": [4, 3, 3, 3], "Programming": [2]}) == "Testing & QA"
