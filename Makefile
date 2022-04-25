.PHONY: all setup test unittest pep8 mypy docs

all: setup test

setup:
	poetry install
	poetry run pip list

test: unittest pep8 mypy

unittest:
	poetry run pytest --doctest-modules envclasses test_envclasses.py -v

pep8:
	poetry run pytest --flake8

mypy:
	poetry run mypy envclasses | true

fmt:
	yapf -i -r envclasses
	isort -rc --atomic envclasses

docs:
	poetry run pip install pdoc
	poetry run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses -o docs

serve-docs:
	poetry pip install pdoc
	poetry run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses
