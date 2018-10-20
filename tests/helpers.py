import os


def set_env(tmp_path):
    venvs = tmp_path / "venvs"
    bins = tmp_path / "bin"
    venvs.mkdir()
    bins.mkdir()
    os.environ["PIPIS_VENVS"] = str(venvs)
    os.environ["PIPIS_BIN"] = str(bins)


class Args:
    def __init__(
        self,
        package="pipis",
        query="pipis",
        yes=True,
        dependency=None,
        system=False,
        upgrade=False,
        ignore_installed=False,
        verbose=False,
    ):
        self.package = package
        self.query = query
        self.yes = yes
        self.dependency = dependency
        self.system = system
        self.upgrade = upgrade
        self.ignore_installed = ignore_installed
        self.verbose = verbose
