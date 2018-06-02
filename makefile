.PHONY: lint test test_verbose docker build publish clean

all: lint test_verbose build

lint:
	poetry run python -m pylint pipis/__init__.py

test:
	poetry run python -m pytest --cov=pipis/

test_verbose:
	poetry run python -m pytest -v --cov-report term-missing --cov=pipis/

docker:
	docker-compose up

build:
	poetry build

install: build
	python -m venv --symlinks --upgrade ~/.local/venvs/pipis
	~/.local/venvs/pipis/bin/pip install -I dist/pipis-*.whl

publish: build
	poetry publish

clean:
	@rm -rf .pytest_cache/ dist/
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@find . -type f -name *.pyc -exec rm -fv {} +
