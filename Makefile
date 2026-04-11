.PHONY: all setup test unittest lint typecheck docs

all: setup test

setup:
	poetry install
	poetry run pip list

test: unittest lint typecheck

unittest:
	poetry run pytest --doctest-modules envclasses test_envclasses.py -v

lint:
	poetry run ruff check envclasses
	poetry run ruff format --check envclasses

typecheck:
	poetry run ty check envclasses

fmt:
	poetry run ruff format envclasses
	poetry run ruff check --fix envclasses

docs:
	poetry run pip install pdoc
	poetry run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses -o docs

serve-docs:
	poetry pip install pdoc
	poetry run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses
