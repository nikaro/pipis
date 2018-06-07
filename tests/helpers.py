import os


def set_env(tmpdir):
    os.environ["PIPIS_VENVS"] = str(tmpdir.mkdir("venvs"))
    os.environ["PIPIS_BIN"] = str(tmpdir.mkdir("bin"))
