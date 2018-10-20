import sys

from helpers import set_env
from pipis.__main__ import main


def test_install(tmp_path, capsys):
    set_env(tmp_path)

    package = "pipis"
    sys.argv = ["pipis", "install", "-y", package]
    main()
    captured = capsys.readouterr()

    assert f"Successfully installed {package}" in captured.out


def test_install_version(tmp_path, capsys):
    set_env(tmp_path)

    package = "pipis==1.0.0"
    sys.argv = ["pipis", "install", "-y", package]
    main()
    sys.argv = ["pipis", "freeze"]
    main()
    captured = capsys.readouterr()

    assert f"Successfully installed {package}" in captured.out
    assert package in captured.out


def test_install_dependency(tmp_path, capsys):
    set_env(tmp_path)

    package = "pipis"
    dependency = "flake8"
    sys.argv = ["pipis", "install", "-y", package, "-d", dependency]
    main()
    captured = capsys.readouterr()

    assert f"Successfully installed {package}" in captured.out
