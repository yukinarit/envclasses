all: setup test

setup:
	pipenv install --dev --skip-lock
	pipenv run pip list

test: unittest pep8 mypy

unittest:
	pipenv run pytest

pep8:
	pipenv run pytest --codestyle

mypy:
	pipenv run mypy envclasses.py
