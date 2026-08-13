# PACE Fresher Talent Pool

Manager-facing talent discovery prototype for searching and filtering fresher candidates by technical category, skill, and proficiency, with a compact Candidate 360° profile.

## Stack

- React, Vite, TypeScript
- FastAPI, SQLAlchemy
- PostgreSQL
- Docker Compose and Nginx
- Terraform and AWS EC2

## Local run

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost`. The API is served below `/api/v1`.

## Tests

```bash
docker compose run --rm backend python -m pytest
docker compose run --rm frontend npm test -- --run
```

Documentation and diagrams are in [`docs/`](docs/README.md).
