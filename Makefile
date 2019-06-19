.PHONY: format lint test test_verbose develop build install publish publish_dry clean

all: lint test_verbose build

format:
	black .

lint:
	black --check src/ bin/
	flake8 src/ bin/
	bandit -c .bandit -r src/ bin/

tests:
	pytest --cov=pipis

tests_verbose:
	pytest -v --cov-report=term-missing --cov=pipis

develop:
	pip install -e .[dev]

build:
	python setup.py sdist bdist_wheel

install: build
	mkdir -pv ~/.local/share/pipis/venvs
	mkdir -pv ~/.local/share/pipis/bin
	python -m venv --symlinks --upgrade ~/.local/share/pipis/venvs/pipis
	~/.local/share/pipis/venvs/pipis/bin/pip install -U pip wheel
	~/.local/share/pipis/venvs/pipis/bin/pip install -I dist/pipis-*.whl

publish: build
	twine check dist/*.{whl,tar.gz}
	twine upload dist/*.{whl,tar.gz}

publish_dry: build
	twine check dist/*.{whl,tar.gz}
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*.{whl,tar.gz}

clean:
	rm -rf .eggs/ .pytest_cache/ .tox/ build/ dist/ src/*.egg-info/ .coverage
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
