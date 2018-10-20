import sys

from helpers import Args, set_env
from pipis.__main__ import main
from pipis.utils import Pipis


def test_uninstall(tmp_path, capsys):
    set_env(tmp_path)
    p = Pipis()
    args = Args()
    p.install(args)
    capsys.readouterr()  # reset capture

    sys.argv = ["pipis", "uninstall", "-y", args.package]
    main()
    captured = capsys.readouterr()

    assert captured.out == f"Successfully uninstalled {args.package}\n"
