import os
import sys

sys.path.append("..")

from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_install_missing_arg(tmpdir):
    set_env(tmpdir)

    msg = "Error: missing arguments/options"

    result = runner.invoke(pipis.install, ["-y"])

    assert msg in result.output
    assert result.exit_code == 2


def test_install(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", package])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_version(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    version = "1.0.0"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", package + "==" + version])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert os.path.exists(
        os.path.join(
            venv, "lib", "python3.6", "site-packages", "pipis-" + version + ".dist-info"
        )
    )
    assert result.exit_code == 0


def test_install_with_dependency(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    dependency = "pylint"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    dep_req = os.path.join(venv, "requirements.txt")
    dep_dir = os.path.join(venv, "lib", "python3.6", "site-packages", dependency)

    result = runner.invoke(pipis.install, ["-y", package, "-d", dependency])

    with open(dep_req) as req:
        dep_req_content = req.read().splitlines()

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(dep_req)
    assert dependency in dep_req_content
    assert os.path.isdir(dep_dir)
    assert result.exit_code == 0


def test_install_add_dependency(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    dependency = "pylint"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    dep_req = os.path.join(venv, "requirements.txt")
    dep_dir = os.path.join(venv, "lib", "python3.6", "site-packages", dependency)

    runner.invoke(pipis.install, ["-y", package])
    result = runner.invoke(pipis.install, ["-y", package, "-d", dependency])

    with open(dep_req) as req:
        dep_req_content = req.read().splitlines()

    assert "Installing" in result.output
    assert os.path.isfile(dep_req)
    assert dependency in dep_req_content
    assert os.path.isdir(dep_dir)
    assert result.exit_code == 0


def test_install_dependency_many_packages(tmpdir):
    set_env(tmpdir)

    packages = ["pipis", "pipsi"]
    dependency = "pylint"
    msg = "cannot add dependecy to multiple packages"

    result = runner.invoke(pipis.install, ["-y", "-d", dependency] + packages)

    assert msg in result.output
    assert result.exit_code != 0


def test_install_system_site_packages(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", "-s", package])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_ignore(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", "-I", package])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_update(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", "-U", package])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_inexistant_package(tmpdir):
    set_env(tmpdir)

    package = "rdnieuribiubsiesgppxna"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "Error: Cannot install {}".format(package)

    result = runner.invoke(pipis.install, ["-y", package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_install_library(tmpdir):
    set_env(tmpdir)

    package = "art"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "Error: library installation is not supported by pipis"

    result = runner.invoke(pipis.install, ["-y", package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_install_already_installed_package(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "Installing"

    runner.invoke(pipis.install, ["-y", package])
    result = runner.invoke(pipis.install, ["-y", package])

    assert msg in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_requirements(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    req = tmpdir.join("requirements.txt")
    with open(req, "w") as req_fh:
        req_fh.write(package)
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    result = runner.invoke(pipis.install, ["-y", "-r", req])

    assert "Installing" in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_inexistant_requirements(tmpdir):
    set_env(tmpdir)

    req = str(tmpdir.join("requirements.txt"))

    msg = "Error: Could not open file"

    result = runner.invoke(pipis.install, ["-y", "-r", req])

    assert msg in result.output
    assert result.exit_code != 0


def test_install_too_many_arg(tmpdir):
    set_env(tmpdir)

    package = "pipis"
    req = tmpdir.join("requirements.txt")
    with open(req, "w") as req_fh:
        req_fh.write(package)
    venv = os.path.join(os.environ["PIPIS_VENVS"], package)
    script = os.path.join(venv, "bin", package)
    link = os.path.join(os.environ["PIPIS_BIN"], package)

    msg = "Error: too many arguments/options"

    result = runner.invoke(pipis.install, ["-y", package, "-r", req])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 2
