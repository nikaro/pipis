"""
helpers lib for pipis
"""

import importlib
from operator import methodcaller
import os
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError
import sys
from time import time
from venv import EnvBuilder

import click
import pkg_resources


DEFAULT_PIPIS_VENVS = "~/.local/venvs/"
DEFAULT_PIPIS_BIN = "~/.local/bin/"


def get_pipis():
    """Get pipis environment variables or fallback on defaults."""
    pipis_venvs = os.path.expanduser(os.environ.get("PIPIS_VENVS", DEFAULT_PIPIS_VENVS))
    pipis_bin = os.path.expanduser(os.environ.get("PIPIS_BIN", DEFAULT_PIPIS_BIN))

    return pipis_venvs, pipis_bin


def get_package(package):
    """Normalize package name and version."""
    req = pkg_resources.Requirement(package)
    package_name = req.project_name
    package_spec = str(req.specifier)

    return package_name, package_spec


def get_venv(package):
    """Get vevn path."""
    pipis_venvs, _ = get_pipis()
    venv_dir = os.path.join(pipis_venvs, package)
    venv_py = os.path.join(venv_dir, "bin", "python")

    return venv_dir, venv_py


def get_dist(package):
    """Get dist object for a given package."""
    venv_dir, venv_py = get_venv(package)
    # get the module path from its venv and append it to the current path
    cmd_path = [
        "import sys;",
        "p = list(filter(lambda x: x.startswith('{}'), sys.path));".format(venv_dir),
        "print(p[0]);",
    ]
    cmd_path = " ".join(cmd_path)
    venv_path = check_output([venv_py, "-c", cmd_path])
    venv_path = venv_path.decode("utf-8").strip()
    sys.path.append(venv_path)
    # reload pkg_resources module to take into account new path
    importlib.reload(pkg_resources)
    # get informations about package
    dist = pkg_resources.get_distribution(package)
    # remove package venv from current path
    index = sys.path.index(venv_path)
    del sys.path[index]

    return dist


def get_version(package):
    """Get version number for a given package."""
    dist = get_dist(package)

    return dist.version


def get_scripts(package):
    """Get executables scripts for a given package."""
    venv_dir, _ = get_venv(package)
    # get informations about package
    dist = get_dist(package)
    # init list
    entry_points = []
    # get entry_points from RECORD file
    if dist.has_metadata("RECORD"):
        files = dist.get_metadata_lines("RECORD")
        for line in files:
            line = os.path.join(dist.location, line.split(",")[0])
            line = os.path.normpath(line)
            entry_points.append(line)
    # get entry_points from installed-files.txt file
    elif dist.has_metadata("installed-files.txt"):
        files = dist.get_metadata_lines("installed-files.txt")
        for line in files:
            line = os.path.join(dist.egg_info, line.split(",")[0])
            line = os.path.normpath(line)
            entry_points.append(line)
    # get entry_points from entry_points.txt file
    elif dist.has_metadata("entry_points.txt"):
        entry_points = dist.get_entry_map("console_scripts").keys()

    # filter only binaries
    entry_points = list(
        filter(methodcaller("startswith", os.path.join(venv_dir, "bin")), entry_points)
    )

    return entry_points


def abort_if_false(ctx, _, value):
    """Abort callback function."""
    if not value:
        ctx.abort()


def show_package(package):
    """Show package callback function."""
    return package


def get_requirement(requirement):
    """Get packages list of a given requirements file."""
    try:
        with open(requirement, "r") as req:
            return req.read().splitlines()
    except IOError:
        raise click.FileError(requirement)


def set_requirement(package, dependency):
    """Create or append requirements files for a given package."""
    venv_dir, _ = get_venv(package)
    requirement = os.path.join(venv_dir, "requirements.txt")
    req_content = set()

    if os.path.exists(requirement):
        with open(requirement, "r") as req:
            req_content = set(req.read().splitlines())

    if dependency not in req_content:
        req_content.add(dependency)
        with open(requirement, "w") as req:
            req.write("\n".join(sorted(req_content)))
            req.write("\n")

    return requirement


def venv(package, system=False, upgrade=False):
    """Define venv options and create it."""
    package, _ = get_package(package)
    venv_dir, _ = get_venv(package)
    # create or update venv
    venv_build = EnvBuilder(
        system_site_packages=system,
        clear=False,
        symlinks=True,
        upgrade=upgrade,
        with_pip=True,
    )
    if not os.path.isdir(venv_dir) or upgrade:
        venv_build.create(venv_dir)


def install(package, verbose=False, upgrade=False, ignore=False):
    """Install a given package into its venv."""
    package, version = get_package(package)
    venv_dir, venv_py = get_venv(package)
    # define pip install cmd
    cmd = [venv_py, "-m", "pip", "install"]
    # set verbosity
    if not verbose:
        cmd.append("--quiet")
    # upgrade pip in venv
    check_call(cmd + ["--upgrade", "pip"])
    # set upgrade
    if upgrade:
        cmd.append("--upgrade")
    # set reinstall
    if ignore:
        cmd.append("--ignore-installed")
    # install package (and eventual dependencies) in venv
    try:
        check_call(cmd + [package + version])
    except CalledProcessError:
        rmtree(venv_dir)
        message = "Cannot install {}".format(package)
        raise click.BadArgumentUsage(message)

    return cmd


def install_dep(cmd, package, dependency=None):
    """Install a given dependency package into the package venv."""
    package, _ = get_package(package)
    venv_dir, _ = get_venv(package)
    # set requirements file path
    dependencies = os.path.join(venv_dir, "requirements.txt")
    # if a dependency is passed, add it to requirements
    if dependency:
        dependencies = set_requirement(package, dependency)
    # install dependencies if needed
    if os.path.exists(dependencies):
        check_call(cmd + ["--requirement", dependencies])


def link(package, upgrade=False):
    """Create or update symlinks for a given package."""
    _, pipis_bin = get_pipis()
    package, _ = get_package(package)
    venv_dir, _ = get_venv(package)
    scripts = get_scripts(package)
    # check if there is no scripts
    if len(scripts) < 1:
        rmtree(venv_dir)
        message = "library installation is not supported by pipis"
        raise click.ClickException(message)
    # link each script found
    for script in scripts:
        script_name = script.split("/")[-1]
        target = os.path.join(pipis_bin, script_name)
        if os.path.realpath(target) == script:
            # already exists
            continue
        elif upgrade and not os.path.islink(target):
            # create
            os.symlink(script, target)
        else:
            # replace existing target
            temp_link = target + str(time())
            os.symlink(script, temp_link)
            os.replace(temp_link, target)


def remove(package):
    """Remove package venv and scripts."""
    pipis_venvs, pipis_bin = get_pipis()
    package, _ = get_package(package)
    venv_dir = os.path.join(pipis_venvs, package)
    if os.path.isdir(venv_dir):
        # remove scripts symlink
        scripts = get_scripts(package)
        for script in scripts:
            script_name = script.split("/")[-1]
            target = os.path.join(pipis_bin, script_name)
            if os.path.islink(target):
                os.remove(target)
        # remove package venv
        rmtree(venv_dir)
    else:
        click.secho(" is not installed, skip", fg="yellow")
