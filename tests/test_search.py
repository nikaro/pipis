import re
import sys

sys.path.append("..")

from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_search(tmpdir):
    set_env(tmpdir)

    runner.invoke(pipis.install, ["-y", "pipis"])

    result = runner.invoke(pipis.search, ["pipis"])

    assert result.exit_code == 0


def test_search_verbose(tmpdir):
    set_env(tmpdir)

    msg = "Starting new HTTP"

    runner.invoke(pipis.install, ["-y", "pipis"])

    result = runner.invoke(pipis.search, ["-v", "pipis"])

    # assert msg in result.output
    assert result.exit_code == 0


def test_search_missing_arg(tmpdir):
    set_env(tmpdir)

    msg = "Missing argument"

    runner.invoke(pipis.install, ["-y", "pipis"])

    result = runner.invoke(pipis.search)

    assert msg in result.output
    assert result.exit_code != 0


def test_search_inexistant(tmpdir):
    set_env(tmpdir)

    msg = "Cannot find"

    runner.invoke(pipis.install, ["-y", "pipis"])

    result = runner.invoke(pipis.search, ["pipistache"])

    assert msg in result.output
    assert result.exit_code != 0
