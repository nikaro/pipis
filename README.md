# PIPIS

## Somewhere between pip and pipsi

> "pipis" stands for "pip isolate" \
> and "pipi" is the french for "peepee" which is a fun name but [pipi](https://pypi.org/project/pipi/) was already taken…

Actually it is a rewrite of [pipsi](https://github.com/mitsuhiko/pipsi) but with [venv](https://docs.python.org/dev/library/venv.html) instead of [virtualenv](https://virtualenv.pypa.io/en/stable/).

## What does it do?

Pipis is a wrapper around venv and pip which installs scripts provided by python packages into separate venvs to shield them from your system and each other.

It creates a venv in `~/.local/venvs/`, update pip, installs the package, and links the package's scripts to `~/.local/bin/`.

## Why not pipsi?

Because i do not care about Python 2, and `virtualenv` copies python's binaries while `venv` just symlink them (which i think is cleaner, but it still copies `pip` which is not clean…).

## How to install

```
python3 -m venv ~/.local/venvs/pipis
source ~/.local/venvs/pipis/bin/activate
pip install -U pip
pip install pipis
deactivate
ln -s ~/.local/venvs/pipis/bin/pipis ~/.local/bin/pipis
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
- [Nicolas Karolak](): myself, the author of pipis
