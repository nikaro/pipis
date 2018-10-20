import sys

from helpers import set_env
from pipis.__main__ import main


def test_update(tmp_path, capsys):
    set_env(tmp_path)

    package = "pipis"
    sys.argv = ["pipis", "update", "-y", package]
    main()
    captured = capsys.readouterr()

    assert f"Successfully updated {package}" in captured.out
