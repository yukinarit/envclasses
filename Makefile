.PHONY: all setup test unittest pep8 mypy docs

all: setup test

setup:
	pipenv install --dev
	pipenv run pip list

test: unittest pep8 mypy

unittest:
	pipenv run pytest --doctest-modules envclasses test_envclasses.py -v

pep8:
	pipenv run pytest --flake8

mypy:
	pipenv run mypy envclasses

fmt:
	yapf -i -r envclasses
	isort -rc --atomic envclasses

docs:
	pipenv run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses -o docs

serve-docs:
	pipenv run pdoc -e envclasses=https://github.com/yukinarit/envclasses/envclasses/ envclasses
