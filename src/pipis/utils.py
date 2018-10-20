"""utils for pipis"""

from configparser import ConfigParser
import ctypes
import importlib
from pathlib import Path
import os
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError
import sys
from venv import EnvBuilder

from pipis import __version__
import pkg_resources


class Pipis:
    """
    Pipis installs Python packages into their own dedicated virtualenv to shield them
    from your system and from each other.

    Virtualenvs are created in `PIPIS_VENVS` (default: `~/.local/share/pipis/<package>`)
    and links the scripts to `PIPIS_BIN` (default: `~/.local/share/pipis/bin/`).
    """

    def __init__(self, config: dict = None, config_paths: list = None):
        self.is_admin = self._is_admin()
        self.config_paths = config_paths or self._get_config_paths()
        self.config = config or self._get_config()

    def _is_admin(self) -> bool:
        """Return wether the current user is administrator or not.

        :return: Administrator status
        :rtype: bool
        """
        try:
            return os.getuid() == 0
        except AttributeError:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0

    def _get_config_paths(self) -> list:
        """Get pipis configuration file paths.

        Get "system" and "user" config files.

        :return: Configuration file paths
        :rtype: list
        """

        name = "pipis"
        paths = []

        # system
        if os.name == "nt":
            sys_base = os.getenv("ProgramFiles")
            sys_path = Path(sys_base, name, "config")
        else:
            sys_base = "/etc"
            sys_path = Path(sys_base, name)
        paths.append(str(Path(sys_path, f"{name}.cfg")))

        # user
        if os.name == "nt":
            user_base = os.getenv("APPDATA")
            user_path = Path(user_base, name, "config")
        else:
            user_home = os.getenv("HOME", "")
            user_base = os.getenv("XDG_CONFIG_HOME", Path(user_home, ".config"))
            user_path = Path(user_base, name)
        paths.append(str(Path(user_path, f"{name}.cfg")))

        return paths

    def _get_config(self) -> dict:
        """Get pipis environment variables or fallback on defaults.

        :return: Configuration values
        :rtype: dict
        """

        name = "pipis"

        # default values
        if os.name == "nt":
            base = os.getenv("APPDATA")
            path = Path(base, name, "data")
        else:
            home = os.getenv("HOME", "")
            base = os.getenv("XDG_DATA_HOME", Path(home, ".local", "share"))
            path = Path(base, name)
        default_venvs = str(Path(path, "venvs"))
        default_bin = str(Path(path, "bin"))

        # config values, "user" values will override "system"
        config_file = {}
        for config_path in self.config_paths:
            if Path(config_path).exists():
                parser = ConfigParser()
                parser.read(config_path)
                config_file.update(dict(parser[name]))

        # use by priority order: env, config or default
        venvs = os.getenv("PIPIS_VENVS") or config_file.get("venvs") or default_venvs
        bins = os.getenv("PIPIS_BIN") or config_file.get("bin") or default_bin

        config = {"venvs": venvs, "bin": bins}

        return config

    def _normalize_name(self, package: str) -> str:
        """Normalize package name.

        :param package: Package name
        :type package: str
        :return: Package name
        :rtype: str
        """

        req = pkg_resources.Requirement(package)
        package_name = req.project_name

        return package_name

    def _normalize_version(self, package: str) -> str:
        """Normalize package version.

        :param package: Package name
        :type package: str
        :return: Package version
        :rtype: str
        """

        req = pkg_resources.Requirement(package)
        package_version = str(req.specifier)

        return package_version

    def _venv_dir_path(self, package: str) -> str:
        """Get package venv path.

        :param package: Package name
        :type package: str
        :return: Virtualenv path
        :rtype: str
        """

        pipis_venvs = self.config["venvs"]
        venv_dir = str(Path(pipis_venvs, package))

        return venv_dir

    def _venv_py_path(self, package: str) -> str:
        """Get package venv python path.

        :param package: Package name
        :type package: str
        :return: Virtualenv path
        :rtype: str
        """

        pipis_venvs = self.config["venvs"]
        venv_py = str(Path(pipis_venvs, package, "bin", "python"))

        return venv_py

    def _dist_info(self, package: str) -> pkg_resources.EggInfoDistribution:
        """Get dist object for a given package.

        :param package: Package name
        :type package: str
        :return: Package dist object
        :rtype: pkg_resources.Distribution
        """

        # append package venv path to current path
        venv_dir = self._venv_dir_path(package)
        venv_path = str(
            Path(
                venv_dir,
                "lib",
                f"python{sys.version_info.major}.{sys.version_info.minor}",
                "site-packages",
            )
        )
        sys.path.insert(0, venv_path)
        # reload pkg_resources module to take into account new path
        importlib.reload(pkg_resources)
        # get informations about package
        dist = pkg_resources.get_distribution(package)
        # remove package venv from current path
        index = sys.path.index(venv_path)
        del sys.path[index]

        return dist

    def _package_version(self, package: str) -> str:
        """Get version number for a given package.

        :param package: Package name
        :type package: str
        :return: Package version
        :rtype: str
        """

        dist = self._dist_info(package)

        return dist.version

    def _package_scripts(self, package: str) -> list:
        """Get executables scripts for a given package.

        :param package: Package name
        :type package: str
        :return: Package scripts
        :rtype: list
        """

        # get informations about package
        dist = self._dist_info(package)
        # init list
        scripts = []
        # get scripts from RECORD file
        if dist.has_metadata("RECORD"):
            files = dist.get_metadata_lines("RECORD")
            for line in files:
                script_path = Path(dist.location, line.split(",")[0]).resolve()
                scripts.append(script_path)
        # get scripts from installed-files.txt file
        elif dist.has_metadata("installed-files.txt"):
            files = dist.get_metadata_lines("installed-files.txt")
            for line in files:
                script_path = Path(dist.egg_info, line.split(",")[0]).resolve()
                scripts.append(script_path)
        # get scripts from entry_points.txt file
        elif dist.has_metadata("entry_points.txt"):
            scripts = [
                Path(script_path).resolve()
                for script_path in dist.get_entry_map("console_scripts").keys()
            ]

        # filter only binaries
        venv_bin_pattern = str(Path(self._venv_dir_path(package), "bin", "*"))
        scripts = [
            str(script_path)
            for script_path in scripts
            if script_path.match(venv_bin_pattern)
        ]

        return scripts

    def _requirements_list(self, requirement: str) -> list:
        """Get packages list of a given requirements file.

        :param requirement: Requirements file path
        :type requirement: str
        :raises click.FileError: Cannot open requirements file
        :return: Packages list
        :rtype: list
        """

        requirements = [
            r
            for r in Path(requirement).read_text().splitlines()
            if not r.startswith("#")
        ]

        return requirements

    def _add_dependency(self, package: str, dependency: str) -> str:
        """Create or append requirements files for a given package.

        :param package: Package name
        :type package: str
        :param dependency: Dependency name
        :type dependency: str
        :return: Requirements file path
        :rtype: str
        """

        venv_dir = self._venv_dir_path(package)
        requirement = str(Path(venv_dir, "requirements.txt"))
        req_content = set()

        if Path(requirement).exists():
            req_content = set(Path(requirement).read_text().splitlines())

        if dependency not in req_content:
            req_content.add(dependency)
            Path(requirement).write_text("\n".join(sorted(req_content)))

        return requirement

    def _create_venv(self, package: str, system: bool = False) -> str:
        """Create package dedicated virtualenv.

        :param package: Package name
        :type package: str
        :param system: Enable system packages, defaults to False
        :type system: bool, optional
        """

        package = self._normalize_name(package)
        venv_dir = self._venv_dir_path(package)
        # create or update venv
        venv_build = EnvBuilder(
            system_site_packages=system, clear=False, symlinks=True, with_pip=True
        )
        if not Path(venv_dir).is_dir():
            venv_build.create(venv_dir)

        return venv_dir

    def _install_dep(self, cmd: list, package: str, dependency: str = None):
        """Install a given dependency package into the package venv.

        :param cmd: Install command for the main package
        :type cmd: list
        :param package: Package name
        :type package: str
        :param dependency: Dependency package name, defaults to None
        :type dependency: str, optional
        """

        package = self._normalize_name(package)
        venv_dir = self._venv_dir_path(package)
        # set requirements file path
        dependencies = str(Path(venv_dir, "requirements.txt"))
        # if a dependency is passed, add it to requirements
        if dependency:
            dependencies = self._add_dependency(package, dependency)
        # install dependencies if needed
        if Path(dependencies).exists():
            check_call(cmd + ["--requirement", dependencies])

    def _create_link(self, package: str, upgrade: bool = False):
        """Create or update symlinks for a given package.

        :param package: Package name
        :type package: str
        :param upgrade: Enable link re-creation, defaults to False
        :type upgrade: bool, optional
        :raises Exception: When package has no scripts
        """

        pipis_bin = self.config["bin"]
        package = self._normalize_name(package)
        venv_dir = self._venv_dir_path(package)
        scripts = self._package_scripts(package)
        # check if there is no scripts
        if len(scripts) < 1:
            rmtree(venv_dir)
            raise Exception("library installation is not supported by pipis")
        # link each script found
        for script in scripts:
            script_name = Path(script).name
            target = Path(pipis_bin, script_name)
            if target.exists() and str(target.resolve()) == script:
                # already linked to script
                continue
            elif target.exists() and upgrade:
                # replace existing target
                target.unlink()
                target.symlink_to(script)
            elif not target.exists():
                # does not exist, create
                target.symlink_to(script)
            else:
                # exists and linked to different script, but not asked to update
                continue

    def _confirm(self, message: str = None):
        """Ask for confirmation."""

        if message:
            print(message)
        choice = input("Do you want to continue [y/N]? ").lower()

        if choice not in ["y", "yes"]:
            print("Exit.")
            exit(0)

    def show_version(self, args: list, **kwargs: dict) -> str:
        """show pipis version"""

        message = f"pipis version: {__version__}"
        print(message)

        return message

    def freeze(self, args: list, **kwargs: dict) -> dict:
        """output installed packages in requirements format"""

        pipis_venvs = Path(self.config["venvs"])
        packages = sorted([x.name for x in pipis_venvs.iterdir() if x.is_dir()])
        freeze = []
        for package in packages:
            package_version = self._package_version(package)
            freeze.append(f"{package}=={package_version}")
            print(f"{package}=={package_version}")

        return freeze

    def search(self, args: list, **kwargs: dict) -> str:
        """search for PyPI packages whose name or summary contains <query>"""

        venv_py = self._venv_py_path("pipis")
        # define pip install cmd
        cmd = [venv_py, "-m", "pip", "search", args.query]
        # set verbosity
        if args.verbose:
            cmd.append("--verbose")
        # run search
        try:
            search = check_output(cmd).decode("utf-8")
        except CalledProcessError:
            search = f"Package '{args.query}' not found"
        print(search)

        return search

    def install(self, args: list, **kwargs: dict) -> list:
        """install packages"""

        state = "installed" if not args.upgrade else "updated"
        if not args.yes:
            self._confirm(f"Package '{args.package}' will be {state}.")

        package = self._normalize_name(args.package)
        version = self._normalize_version(args.package)
        venv_dir = self._create_venv(package, args.system)
        venv_py = self._venv_py_path(package)

        # define pip install cmd
        cmd = [venv_py, "-m", "pip", "install"]
        # set verbosity
        if not args.verbose:
            cmd.append("--quiet")
        # upgrade pip in venv
        check_call(cmd + ["--upgrade", "pip", "wheel"])
        # set upgrade
        if args.upgrade:
            cmd.append("--upgrade")
        # set reinstall
        if args.ignore_installed:
            cmd.append("--ignore-installed")

        # install package (and eventual dependencies) in venv
        try:
            check_call(cmd + [package + version])
            self._install_dep(cmd, package, args.dependency)
        except CalledProcessError:
            if not args.upgrade:
                rmtree(venv_dir)
            raise Exception(f"Cannot install {package}")
        self._create_link(package, args.upgrade)
        print(f"Successfully {state} {package}{version}")

        return cmd

    def update(self, args: list, **kwargs: dict) -> list:
        """update packages"""

        # set defaults value to args
        args.upgrade = True
        args.dependency = None
        args.ignore_installed = False
        args.system = False
        # run update
        cmd = self.install(args)

        return cmd

    def uninstall(self, args: list, **kwargs: dict):
        """uninstall packages"""

        if not args.yes:
            self._confirm(f"Package '{args.package}' will be uninstalled.")

        pipis_bin = self.config["bin"]
        package = self._normalize_name(args.package)
        venv_dir = self._venv_dir_path(package)
        if Path(venv_dir).is_dir():
            # remove scripts symlink
            scripts = self._package_scripts(package)
            for script in scripts:
                script_name = Path(script).name
                target = Path(pipis_bin, script_name)
                if target.is_symlink():
                    target.unlink()
            # remove package venv
            rmtree(venv_dir)
            print(f"Successfully uninstalled {package}")
        else:
            print(f"Package {package} is not installed")
