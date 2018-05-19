import os

import click
from click.testing import CliRunner

import pipis

runner = CliRunner()


def set_env(tmpdir):
    os.environ['PIPIS_VENVS'] = str(tmpdir.mkdir('venvs'))
    os.environ['PIPIS_BIN'] = str(tmpdir.mkdir('bin'))


def test_cli(tmpdir):
    set_env(tmpdir)

    result = runner.invoke(pipis.cli)

    assert result.output.startswith('Usage: ')
    assert result.exit_code == 0


def test_cli_bad_arg(tmpdir):
    set_env(tmpdir)

    msg = 'Error: No such command "bad_arg".'

    result = runner.invoke(pipis.cli, ['bad_arg'])

    assert msg in result.output
    assert result.exit_code == 2
