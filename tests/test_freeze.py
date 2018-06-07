import sys

sys.path.append("..")

import click
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_freeze(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    runner.invoke(pipis.install, ["-y", package])
    version = pipis._get_version(package)
    msg = "{}=={}".format(package, version)

    result = runner.invoke(pipis.freeze)

    assert msg in result.output
    assert result.exit_code == 0
