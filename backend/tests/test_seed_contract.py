from app.seed import CANDIDATES, TAXONOMY


def test_seed_has_eighteen_unique_synthetic_candidates():
    assert len(CANDIDATES) == 18
    assert len({candidate[0] for candidate in CANDIDATES}) == 18
    assert all(email_id.isdigit() for email_id, _, _ in CANDIDATES)


def test_seed_skills_belong_to_taxonomy():
    known = {skill for skills in TAXONOMY.values() for skill in skills}
    used = {skill for _, _, profile in CANDIDATES for skill in profile}
    assert used <= known
