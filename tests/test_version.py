import re
import sys

from helpers import set_env
from pipis.__main__ import main


def test_version(tmp_path, capsys):
    set_env(tmp_path)

    sys.argv = ["pipis", "version"]
    main()
    captured = capsys.readouterr()

    assert re.match(r"^pipis version: \d+\.\d+\.\d+", captured.out)
