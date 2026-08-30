.PHONY: all sync test lint reproduce quick report app crosscheck clean

all: sync reproduce app report

sync:
	uv sync --extra dev

reproduce:
	uv run pdlab reproduce --root .

quick:
	uv run pdlab reproduce --root . --quick --no-hero

test:
	uv run pytest

lint:
	uv run ruff check src tests scripts && uv run ruff format --check src tests scripts && uv run mypy

app:
	uv run python scripts/build_app.py

report:
	$(MAKE) -C report

crosscheck:  # needs an environment with `axelrod` installed, e.g. `uvx --with axelrod python`
	python scripts/crosscheck_axelrod.py > results/crosscheck_axelrod.md

clean:
	rm -rf results figures/*.png figures/*.pdf figures/*.gif report/build
