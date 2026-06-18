# API service — AI Act Navigator

FastAPI backend: deterministic rule engine, assessments, document generation, admin.

## Layer rules

```
public_api/ admin_api/  → routers only (HTTP I/O)
services/               → orchestration
dal/                    → DB queries
rules/                  → PURE engine (no SQL, no HTTP)
models.py               → ORM only, zero business logic
documents/              → renderers + templates
workers/                → RQ jobs
```

## Testing docs

Each API router package has a colocated `TESTING.md`. Index: [`docs/testing/README.md`](../../docs/testing/README.md).

| Package | Guide |
|---|---|
| `public_api/` | [TESTING.md](./public_api/TESTING.md) |
| `admin_api/` | [TESTING.md](./admin_api/TESTING.md) |
| `tests/` | [README.md](./tests/README.md) |

When adding a new router package, add `TESTING.md` there and link it from `docs/testing/README.md`.

## Key commands

```bash
uv sync
uv run alembic upgrade head
uv run python -m app.scripts.seed
uv run pytest
uv run uvicorn app.main:app --reload
```

## Adding a risk rule

1. Add row to seed or admin API
2. Add fixture in `tests/test_risk_engine.py` or `tests/fixtures/`
3. Run `uv run pytest` — must pass before publish
