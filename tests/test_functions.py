import os
import re
import sys

sys.path.append("..")

import click
from click.testing import CliRunner
import pytest

from helpers import set_env
import pipis

runner = CliRunner()


def test_set_pipis_vars_default():
    del os.environ["PIPIS_VENVS"]
    del os.environ["PIPIS_BIN"]
    vars = tuple(
        map(os.path.expanduser, (pipis.DEFAULT_PIPIS_VENVS, pipis.DEFAULT_PIPIS_BIN))
    )

    result = pipis._set_pipis_vars()

    assert type(result) == type(tuple())
    assert result == vars


def test_set_pipis_vars_from_env(tmpdir):
    set_env(tmpdir)

    vars = tuple(
        map(os.path.expanduser, (os.environ["PIPIS_VENVS"], os.environ["PIPIS_BIN"]))
    )

    result = pipis._set_pipis_vars()

    assert type(result) == type(tuple())
    assert result == vars


def test_get_env_data(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    result = pipis._get_venv_data(package)
    venv_dir = result[0]
    venv_py = result[1]

    assert type(result) == type(tuple())
    assert venv_dir.startswith(str(tmpdir.dirpath()))
    assert venv_py.startswith(str(tmpdir.dirpath()))


def test_get_dist(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis._get_dist(package)

    assert hasattr(result, "location")
    assert hasattr(result, "project_name")
    assert hasattr(result, "version")
    assert hasattr(result, "has_metadata")
    assert hasattr(result, "get_metadata_lines")
    assert hasattr(result, "get_entry_map")


def test_get_console_scripts(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis._get_console_scripts(package)

    assert isinstance(result, list)
    assert os.path.isfile(result[0])
    assert "bin" in result[0]


def test_version(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis._get_version(package)

    assert re.match(r"^\d+\.\d+\.\d+", result)


def test_abort_if_false_none():
    ctx = click.Context(click.Command("hello"))

    with pytest.raises(click.exceptions.Abort):
        pipis._abort_if_false(ctx, None, None)


def test_abort_if_false():
    ctx = click.Context(click.Command("hello"))
    result = pipis._abort_if_false(ctx, None, "hello")

    assert result is None


def test_show_package():
    result = pipis._show_package("hello")

    assert result == "hello"
