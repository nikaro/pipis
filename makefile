.PHONY: format lint test test_verbose docker install build dist-install publish clean

all: lint test_verbose build

format:
	poetry run python -m black .

lint:
	poetry run python -m pylint pipis/

test:
	poetry run python -m pytest --cov=pipis/

test_verbose:
	poetry run python -m pytest -v --cov-report term-missing --cov=pipis/

docker:
	docker-compose up

install:
	poetry install

build: install
	poetry build

dist-install: build
	python -m venv --symlinks --upgrade ~/.local/venvs/pipis
	~/.local/venvs/pipis/bin/pip install -I dist/pipis-*.whl

publish: build
	poetry publish

clean:
	@rm -rf .pytest_cache/ dist/
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@find . -type f -name *.pyc -exec rm -fv {} +
