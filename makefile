.PHONY: lint test run_tests run_docker build publish

all:

lint:
	poetry run pylint pipis/__init__.py

test:
	poetry run python -m pytest

run_tests: lint test

run_tests_docker:
	docker-compose up
