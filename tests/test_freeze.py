import sys

from helpers import set_env
from pipis.__main__ import main


def test_freeze(tmp_path, capsys):
    set_env(tmp_path)
    # install a package before test
    package = "pipis"
    sys.argv = ["pipis", "install", "-y", package]
    main()

    sys.argv = ["pipis", "freeze"]
    main()
    captured = capsys.readouterr()

    assert f"{package}==" in captured.out
