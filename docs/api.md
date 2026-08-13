# API and filtering contract

## Endpoints

- `GET /api/v1/health`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{category_id}/skills`
- `GET /api/v1/proficiency-levels`
- `GET /api/v1/candidates`
- `GET /api/v1/candidates/{candidate_id}`

## Candidate query

```text
GET /api/v1/candidates?q=301&category_id=1&skill=4:2&skill=8:3&match=all
```

Each repeated `skill` parameter is `skill_id:minimum_rank`. The UI's “Any proficiency” sends rank 1, meaning any assessed exposure. `match=all` is presented as “Every selected skill”; `match=any` is presented as “At least one selected skill.” Category-only filtering requires at least one skill at Beginner or above in that category. Search, category, and skill predicates combine with AND.

Invalid identifiers, ranks, or match modes return HTTP 422. Candidate details return HTTP 404 when the identifier does not exist.
