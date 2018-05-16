# PIPIS

## Somewhere between pip and pipsi

> "pipis" stands for "pip isolate" \
> and "pipi" is the french for "peepee" which is a fun name but [pipi](https://pypi.org/project/pipi/) was already taken…

Actually it is a rewrite of [pipsi](https://github.com/mitsuhiko/pipsi) but with [venv](https://docs.python.org/dev/library/venv.html) instead of [virtualenv](https://virtualenv.pypa.io/en/stable/).

## Why ?

Because i do not care about Python 2, and `virtualenv` copies python's binaries while `venv` just symlink them (which i think is cleaner, but it still copies `pip` which is not clean…).

## Installation

```
python3 -m venv ~/.local/venvs/pipis
source ~/.local/venvs/pipis/bn/activate
pip install pipis
deactivate
```

## Usage

```
pipis --help
pipis install django
```
