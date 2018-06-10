import re
import sys

sys.path.append("..")

from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_list(tmpdir):
    set_env(tmpdir)

    result = runner.invoke(pipis.list_installed)

    assert re.match(r"^Package\s+Version\n-+\s+-+\n$", result.output)
    assert result.exit_code == 0


def test_list_installed(tmpdir):
    set_env(tmpdir)

    runner.invoke(pipis.install, ["-y", "pipis"])
    result = runner.invoke(pipis.list_installed)

    assert "pipis" in result.output
    assert result.exit_code == 0


def test_list_uninstalled(tmpdir):
    set_env(tmpdir)

    runner.invoke(pipis.install, ["-y", "pipis"])
    runner.invoke(pipis.uninstall, ["-y", "pipis"])
    result = runner.invoke(pipis.list_installed)

    assert "pipis" not in result.output
    assert result.exit_code == 0


def test_list_bad_arg(tmpdir):
    set_env(tmpdir)

    msg = "Error: Got unexpected extra argument (bad_arg)"

    result = runner.invoke(pipis.list_installed, ["bad_arg"])

    assert msg in result.output
    assert result.exit_code == 2
