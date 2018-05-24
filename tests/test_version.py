import re
import sys
sys.path.append('..')

import click
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_version(tmpdir):
    set_env(tmpdir)

    runner.invoke(pipis.install, ['-y', 'pipis'])

    result = runner.invoke(pipis.version)

    assert re.match(r'^\d+\.\d+\.\d+', result.output)
    assert result.exit_code == 0


def test_version_bad_arg(tmpdir):
    set_env(tmpdir)

    msg = 'Error: Got unexpected extra argument (bad_arg)'

    runner.invoke(pipis.install, ['-y', 'pipis'])
    result = runner.invoke(pipis.version, ['bad_arg'])

    assert msg in result.output
    assert result.exit_code == 2
