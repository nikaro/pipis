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


def test_get_pipis_default():
    del os.environ["PIPIS_VENVS"]
    del os.environ["PIPIS_BIN"]
    envvar = tuple(
        map(
            os.path.expanduser,
            (pipis.lib.DEFAULT_PIPIS_VENVS, pipis.lib.DEFAULT_PIPIS_BIN),
        )
    )

    result = pipis.lib.get_pipis()

    assert type(result) == type(tuple())
    assert result == envvar


def test_get_pipis_from_env(tmpdir):
    set_env(tmpdir)

    envvar = tuple(
        map(os.path.expanduser, (os.environ["PIPIS_VENVS"], os.environ["PIPIS_BIN"]))
    )

    result = pipis.lib.get_pipis()

    assert type(result) == type(tuple())
    assert result == envvar


def test_get_env_data(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    result = pipis.lib.get_venv(package)
    venv_dir = result[0]
    venv_py = result[1]

    assert type(result) == type(tuple())
    assert venv_dir.startswith(str(tmpdir.dirpath()))
    assert venv_py.startswith(str(tmpdir.dirpath()))


def test_get_dist(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis.lib.get_dist(package)

    assert hasattr(result, "location")
    assert hasattr(result, "project_name")
    assert hasattr(result, "version")
    assert hasattr(result, "has_metadata")
    assert hasattr(result, "get_metadata_lines")
    assert hasattr(result, "get_entry_map")


def test_get_scripts(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis.lib.get_scripts(package)

    assert isinstance(result, list)
    assert os.path.isfile(result[0])
    assert "bin" in result[0]


def test_version(tmpdir):
    set_env(tmpdir)

    package = "pipis"

    runner.invoke(pipis.install, ["-y", package])
    result = pipis.lib.get_version(package)

    assert re.match(r"^\d+\.\d+\.\d+", result)


def test_abort_if_false_none():
    ctx = click.Context(click.Command("hello"))

    with pytest.raises(click.exceptions.Abort):
        pipis.lib.abort_if_false(ctx, None, None)


def test_show_package():
    result = pipis.lib.show_package("hello")

    assert result == "hello"
