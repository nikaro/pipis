import os
from pathlib import Path
import re
import sys

import pytest
from unittest import mock

from helpers import Args, set_env
from pipis.utils import Pipis


@pytest.fixture(scope="function", autouse=True)
def del_env():
    if "PIPIS_VENVS" in os.environ:
        del os.environ["PIPIS_VENVS"]
    if "PIPIS_BIN" in os.environ:
        del os.environ["PIPIS_BIN"]


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="skipping linux tests")
def test_linux_defaults_config_paths():
    args = Args()
    sys_base = "/etc"
    sys_path = str(Path(sys_base, args.package, f"{args.package}.cfg"))
    user_home = os.getenv("HOME", "")
    user_base = os.getenv("XDG_CONFIG_HOME", Path(user_home, ".config"))
    user_path = str(Path(user_base, args.package, f"{args.package}.cfg"))

    p = Pipis()

    assert isinstance(p.config_paths, list)
    assert p.config_paths[0] == sys_path
    assert p.config_paths[1] == user_path


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="skipping windows tests")
def test_windows_defaults_config_paths():
    args = Args()
    sys_base = os.getenv("ProgramFiles")
    sys_path = str(Path(sys_base, args.package, "config", f"{args.package}.cfg"))
    user_base = user_base = os.getenv("APPDATA")
    user_path = str(Path(user_base, args.package, "config", f"{args.package}.cfg"))

    p = Pipis()

    assert isinstance(p.config_paths, list)
    assert p.config_paths[0] == sys_path
    assert p.config_paths[1] == user_path


def test_args_config_paths():
    p = Pipis(config_paths=["hello", "world"])

    assert isinstance(p.config_paths, list)
    assert p.config_paths[0] == "hello"
    assert p.config_paths[1] == "world"


def test_args_config():
    p = Pipis(config={"hello": 1, "world": 2})

    assert isinstance(p.config, dict)
    assert p.config["hello"] == 1
    assert p.config["world"] == 2


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="skipping linux tests")
def test_linux_defaults_config():
    args = Args()
    home = os.getenv("HOME", "")
    base = os.getenv("XDG_DATA_HOME", Path(home, ".local", "share"))
    path = Path(base, args.package)
    default_venvs = str(Path(path, "venvs"))
    default_bin = str(Path(path, "bin"))
    defaults = {"venvs": default_venvs, "bin": default_bin}

    p = Pipis()

    assert isinstance(p.config, dict)
    assert p.config == defaults


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="skipping windows tests")
def test_windows_defaults_config():
    args = Args()
    base = os.getenv("APPDATA")
    path = Path(base, args.package, "data")
    default_venvs = str(Path(path, "venvs"))
    default_bin = str(Path(path, "bin"))
    defaults = {"venvs": default_venvs, "bin": default_bin}

    p = Pipis()

    assert isinstance(p.config, dict)
    assert p.config == defaults


def test_env_config(tmp_path):
    set_env(tmp_path)
    envvars = {"venvs": os.environ["PIPIS_VENVS"], "bin": os.environ["PIPIS_BIN"]}

    p = Pipis()

    assert isinstance(p.config, dict)
    assert p.config == envvars


def test_file_config(tmp_path):
    tmp_config_file = tmp_path / "config.cfg"
    tmp_config_file.write_text("[pipis]\nvenvs=hello\nbin=world\n")

    p = Pipis(config_paths=[str(tmp_config_file)])

    assert isinstance(p.config, dict)
    assert "venvs" in p.config.keys()
    assert "bin" in p.config.keys()
    assert p.config["venvs"] == "hello"
    assert p.config["bin"] == "world"


def test_venv_dir_path(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    venv_dir = p._venv_dir_path(args.package)

    assert isinstance(venv_dir, str)
    assert venv_dir.startswith(str(tmp_path))


def test_venv_py_path(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    venv_py = p._venv_py_path(args.package)

    assert isinstance(venv_py, str)
    assert venv_py.startswith(str(tmp_path))


def test_create_venv(tmp_path):
    set_env(tmp_path)

    args = Args()
    p = Pipis()
    venv_dir = p._create_venv(package=args.package)

    assert Path(venv_dir).is_dir()
    assert Path(venv_dir, "bin", "python").exists()
    assert Path(venv_dir, "bin", "pip").exists()


def test_dist_info(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    dist = p._dist_info(args.package)

    assert hasattr(dist, "location")
    assert hasattr(dist, "project_name")
    assert hasattr(dist, "version")
    assert hasattr(dist, "has_metadata")
    assert hasattr(dist, "get_metadata_lines")
    assert hasattr(dist, "get_entry_map")


def test_package_version(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    version = p._package_version(args.package)

    assert isinstance(version, str)
    assert re.match(r"^\d+(?:\.\d+){1,3}", version)


def test_package_scripts(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    scripts = p._package_scripts(args.package)

    assert isinstance(scripts, list)
    for script in scripts:
        assert Path(script).is_file()
        assert os.access(script, os.X_OK)
        assert "bin" in script


def test_requirements_list(tmp_path):
    tmp_requirements_file = tmp_path / "requirements.txt"
    tmp_requirements_file.write_text("pipis\nansible\n# comment\n")

    p = Pipis()
    requirements = p._requirements_list(str(tmp_requirements_file))

    assert "pipis" in requirements
    assert "ansible" in requirements
    assert "# comment" not in requirements


def test_add_dependency(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    p._add_dependency(args.package, "abc")
    req_file = p._add_dependency(args.package, "def")

    assert Path(req_file).is_file()
    assert Path(req_file).read_text() == "abc\ndef"


def test_show_version(tmp_path):
    p = Pipis()
    args = Args()
    message = p.show_version(args)

    assert message.startswith("pipis version: ")


def test_freeze(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    freeze = p.freeze(args)

    assert freeze[0].startswith(f"{args.package}==")


def test_search(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    search = p.search(args)

    assert "not found" not in search
    assert args.query in search


def test_search_inexistant(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(query="pipistache")
    p.install(args)
    search = p.search(args)

    assert search == f"Package '{args.query}' not found"


def test_install(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert package_bin.exists()


def test_install_input_yes(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(yes=False)
    with mock.patch("builtins.input", return_value="y"):
        p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert package_bin.exists()


def test_install_input_no(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(yes=False)
    with mock.patch("builtins.input", return_value="n"):
        with pytest.raises(SystemExit):
            p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert not package_bin.exists()


def test_install_already(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert package_bin.exists()


def test_install_upgrade(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(upgrade=True)
    p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert package_bin.exists()


def test_install_dependency(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(dependency="black")
    p.install(args)
    venv_dir = p._venv_dir_path(args.package)
    requirements = Path(venv_dir, "requirements.txt").read_text()
    dep_bin = Path(venv_dir, "bin", "black")

    assert requirements == "black"
    assert dep_bin.exists()


def test_install_lib_fail(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args(package="requests")

    with pytest.raises(Exception):
        p.install(args)


def test_update(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.update(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert package_bin.exists()


def test_uninstall(tmp_path):
    set_env(tmp_path)

    p = Pipis()
    args = Args()
    p.install(args)
    p.uninstall(args)
    venv_dir = p._venv_dir_path(args.package)
    package_bin = Path(venv_dir, "bin", args.package)

    assert not package_bin.exists()
