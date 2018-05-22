import os
import sys
sys.path.append('..')

import click
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_set_pipis_vars_default():
    vars = tuple(map(os.path.expanduser, (pipis.DEFAULT_PIPIS_VENVS,
                                          pipis.DEFAULT_PIPIS_BIN)))

    result = pipis._set_pipis_vars()

    assert type(result) == type(tuple())
    assert result == vars


def test_set_pipis_vars_from_env(tmpdir):
    set_env(tmpdir)

    vars = tuple(map(os.path.expanduser, (os.environ['PIPIS_VENVS'],
                                          os.environ['PIPIS_BIN'])))

    result = pipis._set_pipis_vars()

    assert type(result) == type(tuple())
    assert result == vars


def test_get_env_data(tmpdir):
    set_env(tmpdir)

    package = 'pipis'

    result = pipis._get_venv_data(package)
    venv_dir = result[0]
    venv_py = result[1]

    assert type(result) == type(tuple())
    assert venv_dir.startswith(str(tmpdir.dirpath()))
    assert venv_py.startswith(str(tmpdir.dirpath()))
