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

It creates a venv in `~/.local/share/pipis/venvs/`, update pip, installs the package, and links the package's scripts to `~/.local/share/pipis/bin/`. These directory can be changed respectively through the environment variables `PIPIS_VENVS` and `PIPIS_BIN`.

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
$ pipis -h
usage: pipis [-h] [-v] {version,freeze,search,install,update,uninstall} ...

Pipis installs Python packages into their own dedicated virtualenv to shield
them from your system and from each other. Virtualenvs are created in
`PIPIS_VENVS` (default: `~/.local/share/pipis/<package>`) and links the
scripts to `PIPIS_BIN` (default: `~/.local/share/pipis/bin/`).

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         enable verbose ouput

available commands:
  {version,freeze,search,install,update,uninstall}
    version             show pipis version
    freeze              output installed packages in requirements format
    search              search for PyPI packages whose name or summary
                        contains <query>
    install             install packages
    update              update packages
    uninstall           uninstall packages
```

You can also invoke `--help` on each commands.

### Install package(s)

```
$ pipis install ansible
Package 'ansible' will be installed.
Do you want to continue [y/N]? y
Successfully installed ansible
```

### Unattended install package(s)

```
$ pipis install -y awscli
Successfully installed awscli
```

### Update package(s)

```
$ pipis update ansible
Package 'ansible' will be updated.
Do you want to continue [y/N]? y
Successfully updated ansible
```

### List installed packages

```
$ pipis freeze
ansible==2.8.1
awscli==1.16.181
gcal2redmine==0.2.0
gitignore-cli==1.0.3
pipenv==2018.11.26
pipis==2.0.0
poetry==0.12.16
speedtest-cli==2.1.1
tldr==0.4.4
youtube-dl==2019.6.8
```

### Uninstall package(s)

```
$ pipis uninstall ansible
Package 'ansible' will be uninstalled.
Do you want to continue [y/N]? y
Successfully uninstalled ansible
```

## Credits

- [Armin Ronacher](https://github.com/mitsuhiko): the author of pipsi, for the inspiration
- [Nicolas Karolak](https://github.com/nikaro): myself, the author of pipis
