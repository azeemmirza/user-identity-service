.PHONY: dev test lint fmt typecheck migrate makemigration

dev:
	uv run uvicorn src.main:app --reload --log-config logging.yaml

test:
	uv run pytest

format:
	uv run black .

lint:
	uv run ruff .

typecheck:
	uv run mypy src

gen_migration:
	uv run alembic revision --autogenerate -m "${m}"

migrate:
	uv run alembic upgrade head