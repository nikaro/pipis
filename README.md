# PIPIS

| **tests** | [![Build Status](https://travis-ci.org/nikaro/pipis.svg?branch=master)](https://travis-ci.org/nikaro/pipis) |
|-|-|
| **package** | [![PyPI version](https://img.shields.io/pypi/v/pipis.svg)](https://pypi.org/project/pipis) [![Supported versions](https://img.shields.io/pypi/pyversions/pipis.svg)](https://pypi.org/project/pipis) [![PyPI - Status](https://img.shields.io/pypi/status/pipis.svg)](https://github.com/nikaro/pipis) |

## Somewhere between pip and pipsi

> "pipis" stands for "pip isolate" \
> and "pipi" is the french for "peepee" which is a fun name but [pipi](https://pypi.org/project/pipi/) was already taken…

Actually it is a rewrite of [pipsi](https://github.com/mitsuhiko/pipsi) but with [venv](https://docs.python.org/dev/library/venv.html) instead of [virtualenv](https://virtualenv.pypa.io/en/stable/).

## What does it do?

Pipis is a wrapper around venv and pip which installs scripts provided by python packages into separate venvs to shield them from your system and each other.

It creates a venv in `~/.local/venvs/`, update pip, installs the package, and links the package's scripts to `~/.local/bin/`. These directory can be changed respectively through the environment variables `PIPIS_VENVS` and `PIPIS_BIN`.

## Why not pipsi?

Because i do not care about Python 2, and `virtualenv` copies python's binaries while `venv` just symlink them (which i think is cleaner, but it still copies `pip` which is not clean…).

## How to install

### Automatic

Coming soon…

### Manual

Create the pipis venvs and bin directories:
```sh
mkdir -p ~/.local/share/pipis/{venvs,bin}
```

Create and activate the pipis virtual environment:
```sh
python3 -m venv ~/.local/share/pipis/venvs/pipis
source ~/.local/share/pipis/venvs/pipis/bin/activate
```

Upgrade the pip package:
```sh
pip install -U pip
```

Install pipis:
```sh
pip install pipis
```

Exit the virtual environment:
```sh
deactivate
```

Link the pipis script into the "global" bin directory:
```sh
ln -s ~/.local/share/pipis/venvs/pipis/bin/pipis ~/.local/share/pipis/bin/
```

Add the pipis "global" bin directory to your PATH:
```sh
export PATH="~/.local/share/pipis/bin:${PATH}"
```

## How to update

```
pipis update pipis
```

## How to uninstall

```
pipis uninstall pipis
```

## How to use

### Show help

```
$ pipis --help
Usage: pipis [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  install
  list
  uninstall
  update
```

You can also invoke `--help` on each commands.

### Install package(s)

```
$ pipis install ansible
Do you want to continue? [y/N]: y
Installing  [####################################]  100%
```

You can install multiple packages:

```
$ pipis install ansible ansible-lint jmespath
Do you want to continue? [y/N]: y
Installing  [####################################]  100%
```

### Unattended install package(s)

```
$ pipis install --yes awscli
Installing  [####################################]  100%
```

### Update package(s)

```
$ pipis update ansible
Do you want to continue? [y/N]: y
Updating  [####################################]  100%
```

You can also update all installed packages at once:

```
$ pipis update
Do you want to continue? [y/N]: y
Updating  [####################################]  100%
```

### List installed packages

```
$ pipis list
Installed:
  - ansible
  - ansible-lint
  - awscli
  - bashate
  - docker-compose
  - flake8
  - jmespath
  - pipis
  - poetry
  - pylint
  - python-language-server
  - twine
```

### Uninstall package(s)

```
$ pipis uninstall ansible
Do you want to continue? [y/N]: y
Removing  [####################################]  100%
```

## Credits

- [Armin Ronacher](https://github.com/mitsuhiko): the author of pipsi, for the inspiration
- [Nicolas Karolak](https://github.com/nikaro): myself, the author of pipis
