import sys

from helpers import Args, set_env
from pipis.__main__ import main
from pipis.utils import Pipis


def test_search(tmp_path, capsys):
    set_env(tmp_path)
    p = Pipis()
    args = Args()
    p.install(args)

    package = "pipis"
    sys.argv = ["pipis", "search", package]
    main()
    captured = capsys.readouterr()

    assert "not found" not in captured.out
    assert package in captured.out


def test_search_inexistant(tmp_path, capsys):
    set_env(tmp_path)
    p = Pipis()
    args = Args()
    p.install(args)
    capsys.readouterr()  # reset capture

    package = "pipistache"
    sys.argv = ["pipis", "search", package]
    main()
    captured = capsys.readouterr()

    assert captured.out == f"Package '{package}' not found\n"
