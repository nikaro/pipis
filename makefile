.PHONY: lint test run_tests run_docker build publish

all:

lint:
	poetry run pylint pipis/__init__.py

test:
	poetry run python -m pytest --cov=pipis/

docker:
	docker-compose up

build:
	poetry build

publish:
	poetry publish
