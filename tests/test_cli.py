import sys
sys.path.append('..')

import click
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


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
