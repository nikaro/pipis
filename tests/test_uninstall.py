import os
import sys

sys.path.append("..")

from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_uninstall_missing_arg(tmpdir):
    set_env(tmpdir)

    msg = "Error: missing arguments/options"

    result = runner.invoke(pipis.uninstall, ["-y"])

    assert msg in result.output
    assert result.exit_code == 2


def test_uninstall(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    runner.invoke(pipis.install, ["-y", package])
    result = runner.invoke(pipis.uninstall, ["-y", package])

    assert "Removing" in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 0


def test_uninstall_inexistant_package(tmpdir):
    set_env(tmpdir)

    package = "rdnieuribiubsiesgppxna"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "is not installed"

    result = runner.invoke(pipis.uninstall, ["-y", package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 0


def test_uninstall_requirements(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    req = tmpdir.join("requirements.txt")
    with open(req, "w") as req_fh:
        req_fh.write(package)
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    runner.invoke(pipis.install, ["-y", "-r", req])
    result = runner.invoke(pipis.uninstall, ["-y", "-r", req])

    assert "Removing" in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 0


def test_uninstall_inexistant_requirements(tmpdir):
    set_env(tmpdir)

    req = str(tmpdir.join("requirements.txt"))

    msg = "Error: Could not open file"

    result = runner.invoke(pipis.uninstall, ["-y", "-r", req])

    assert msg in result.output
    assert result.exit_code != 0


def test_uninstall_too_many_arg(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    req = tmpdir.join("requirements.txt")
    with open(req, "w") as req_fh:
        req_fh.write(package)
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "Error: too many arguments/options"

    result = runner.invoke(pipis.uninstall, ["-y", package, "-r", req])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 2
