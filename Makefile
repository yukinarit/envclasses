.PHONY: all setup test unittest lint typecheck docs

all: setup test

setup:
	uv sync
	uv run pip list

test: unittest lint typecheck

unittest:
	uv run pytest --doctest-modules envclasses test_envclasses.py -v

lint:
	uv run ruff check envclasses
	uv run ruff format --check envclasses

typecheck:
	uv run ty check envclasses

fmt:
	uv run ruff format envclasses
	uv run ruff check --fix envclasses

docs:
	uv run pip install pdoc
	uv run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses -o docs

serve-docs:
	uv run pip install pdoc
	uv run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses
