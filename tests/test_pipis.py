import re

import click
from click.testing import CliRunner

import pipis

runner = CliRunner()


def test_cli():
    result = runner.invoke(pipis.cli)
    assert result.exit_code == 0
    assert result.output.startswith('Usage: ')


def test_cli_bad_arg():
    result = runner.invoke(pipis.cli, ['bad_arg'])
    msg = 'Error: No such command "bad_arg".'
    assert result.exit_code == 2
    assert msg in result.output


def test_version():
    result = runner.invoke(pipis.version)
    assert result.exit_code == 0
    assert re.match(r'^\d+\.\d+\.\d+', result.output)


def test_version_bad_arg():
    result = runner.invoke(pipis.version, ['bad_arg'])
    msg = 'Error: Got unexpected extra argument (bad_arg)'
    assert result.exit_code == 2
    assert msg in result.output


def test_list():
    result = runner.invoke(pipis.list_installed)
    assert re.match(r'^Package\s+Version', result.output)
    assert result.exit_code == 0


def test_list_bad_arg():
    result = runner.invoke(pipis.list_installed, ['bad_arg'])
    msg = 'Error: Got unexpected extra argument (bad_arg)'
    assert result.exit_code == 2
    assert msg in result.output
