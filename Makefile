.PHONY: all sync test lint reproduce report app clean

all: sync reproduce report

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

report:
	$(MAKE) -C report

clean:
	rm -rf results figures/*.png figures/*.pdf figures/*.gif report/build
