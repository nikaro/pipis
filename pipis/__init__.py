"""
'pipis' stands for 'pip isolated'
"""

import importlib
from operator import methodcaller
import os
from shutil import rmtree
from subprocess import check_call, check_output, CalledProcessError
import sys
from venv import create

import click
import pkg_resources
from tabulate import tabulate

DEFAULT_PIPIS_VENVS = "~/.local/venvs/"
DEFAULT_PIPIS_BIN = "~/.local/bin/"


def _set_pipis_vars():
    pipis_venvs = os.path.expanduser(os.environ.get("PIPIS_VENVS", DEFAULT_PIPIS_VENVS))
    pipis_bin = os.path.expanduser(os.environ.get("PIPIS_BIN", DEFAULT_PIPIS_BIN))

    return pipis_venvs, pipis_bin


def _get_package_data(package):
    req = pkg_resources.Requirement(package)
    package_name = req.project_name
    package_spec = str(req.specifier)

    return package_name, package_spec


def _get_venv_data(package):
    pipis_venvs, _ = _set_pipis_vars()
    venv_dir = os.path.join(pipis_venvs, package)
    venv_py = os.path.join(venv_dir, "bin", "python")

    return venv_dir, venv_py


def _get_dist(package):
    venv_dir, venv_py = _get_venv_data(package)
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


def _get_version(package):
    dist = _get_dist(package)

    return dist.version


def _get_console_scripts(package):
    venv_dir, _ = _get_venv_data(package)
    # get informations about package
    dist = _get_dist(package)
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


def _abort_if_false(ctx, _, value):
    if not value:
        ctx.abort()


def _show_package(package):
    return package


def _get_requirement(requirement):
    try:
        with open(requirement, "r") as req:
            return list(map(str.strip, req.readlines()))
    except IOError:
        raise click.FileError(requirement)


def _set_requirement(package, dependency):
    venv_dir, _ = _get_venv_data(package)
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


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Pipis is a wrapper around venv and pip which installs python packages into
    separate venvs to shield them from your system and each other.

    It creates a venv in `~/.local/venvs/<package>`, updates pip, installs the
    package, and links the package's scripts to `~/.local/bin/`. These
    directory can be changed respectively through the environment variables
    `PIPIS_VENVS` and `PIPIS_BIN`.
    """
    pass


@cli.command("version", context_settings=CONTEXT_SETTINGS)
def show_version():
    """Show version and exit."""
    package_version = _get_version(__name__)
    click.echo(package_version)


@cli.command("list", context_settings=CONTEXT_SETTINGS)
def list_installed():
    """List installed packages."""
    pipis_venvs, _ = _set_pipis_vars()
    table = {"Package": [], "Version": []}
    for package in sorted(os.listdir(pipis_venvs)):
        package_version = _get_version(package)
        table["Package"].append(package)
        table["Version"].append(package_version)
    click.echo(tabulate(table, headers="keys"))


@cli.command(context_settings=CONTEXT_SETTINGS)
def freeze():
    """Output installed packages in requirements format."""
    pipis_venvs, _ = _set_pipis_vars()
    for package in sorted(os.listdir(pipis_venvs)):
        package_version = _get_version(package)
        click.echo("{}=={}".format(package, package_version))


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Install packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=_abort_if_false,
    prompt="Do you want to continue?",
    expose_value=False,
    help="Confirm the action without prompting.",
)
@click.option("-r", "--requirement", help="Install from the given requirements file.")
@click.option(
    "-d", "--dependency", help="Add the specified package as dependency in the venv."
)
@click.option(
    "-s",
    "--system-site-packages",
    is_flag=True,
    help="Give the virtual environment access to the system site-packages dir.",
)
@click.option("-v", "--verbose", is_flag=True, help="Give more output.")
@click.argument("name", nargs=-1, type=click.STRING)
def install(requirement, dependency, system_site_packages, verbose, name):
    """
    Install packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    _, pipis_bin = _set_pipis_vars()
    # check presence of args
    if not (requirement or name):
        raise click.UsageError("missing arguments/options")
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if requirement:
        name = _get_requirement(requirement)
    # do not add dependency to multiple packages
    if len(name) > 1 and dependency:
        raise click.UsageError("cannot add dependecy to multiple packages")
    # process packages
    with click.progressbar(
        name, label="Installing", item_show_func=_show_package
    ) as packages:
        for package in packages:
            package, version = _get_package_data(package)
            venv_dir, venv_py = _get_venv_data(package)
            cmd = [venv_py, "-m", "pip", "install"]
            if not verbose:
                cmd.append("--quiet")
            # create venv if not exists
            if not os.path.isdir(venv_dir):
                create(
                    venv_dir,
                    symlinks=True,
                    with_pip=True,
                    system_site_packages=system_site_packages,
                )
                # upgrade pip in venv
                check_call(cmd + ["--upgrade", "pip"])
                # install package in venv
                cmd.append(package + version)
                try:
                    check_call(cmd)
                    # install dependency on venv
                    if dependency:
                        dependencies = _set_requirement(package, dependency)
                        check_call(cmd + ["--requirement", dependencies])
                except CalledProcessError:
                    rmtree(venv_dir)
                    message = "Cannot install {}".format(package)
                    raise click.BadArgumentUsage(message)
                # create scripts symlink
                scripts = _get_console_scripts(package)
                if len(scripts) < 1:
                    rmtree(venv_dir)
                    message = "library installation is not supported by pipis"
                    raise click.ClickException(message)
                for script in scripts:
                    script_name = script.split("/")[-1]
                    link = os.path.join(pipis_bin, script_name)
                    try:
                        os.symlink(script, link)
                    except FileExistsError:
                        rmtree(venv_dir)
                        message = "{} already exists".format(link)
                        raise click.ClickException(message)
            # install dependency on venv
            elif dependency:
                dependencies = _set_requirement(package, dependency)
                check_call(cmd + ["--requirement", dependencies])
            else:
                click.secho(" is already installed, skip", fg="green")


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Update packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=_abort_if_false,
    prompt="Do you want to continue?",
    expose_value=False,
    help="Confirm the action without prompting.",
)
@click.option("-r", "--requirement", help="Install from the given requirements file.")
@click.option("-v", "--verbose", is_flag=True, help="Give more output.")
@click.argument("name", nargs=-1, type=click.STRING)
def update(requirement, verbose, name):
    """
    Update packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.

    If you do not specify package name or requirements file, it will update
    all installed packages.
    """
    pipis_venvs, pipis_bin = _set_pipis_vars()
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if requirement:
        name = _get_requirement(requirement)
    # populate packages list with all currently installed
    if not name:
        name = os.listdir(pipis_venvs)
    with click.progressbar(
        name, label="Updating", item_show_func=_show_package
    ) as packages:
        for package in packages:
            package, version = _get_package_data(package)
            venv_dir, venv_py = _get_venv_data(package)
            if not os.path.isdir(venv_dir):
                message = "{} is not installed".format(package)
                raise click.ClickException(message)
            cmd = [venv_py, "-m", "pip", "install"]
            if not verbose:
                cmd.append("--quiet")
            # upgrade pip in venv
            check_call(cmd + ["--upgrade", "pip"])
            # install package in venv
            check_call(cmd + ["--upgrade", package + version])
            # update dependency on venv
            req = os.path.join(venv_dir, "requirements.txt")
            if os.path.exists(req):
                check_call(cmd + ["--upgrade", "-r", req])
            # update scripts symlink
            scripts = _get_console_scripts(package)
            for script in scripts:
                script_name = script.split("/")[-1]
                link = os.path.join(pipis_bin, script_name)
                if not os.path.islink(link):
                    os.symlink(script, link)


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Uninstall packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=_abort_if_false,
    prompt="Do you want to continue?",
    expose_value=False,
    help="Confirm the action without prompting.",
)
@click.option("-r", "--requirement", help="Install from the given requirements file.")
@click.argument("name", nargs=-1, type=click.STRING)
def uninstall(requirement, name):
    """
    Uninstall packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    pipis_venvs, pipis_bin = _set_pipis_vars()
    # check presence of args
    if not (requirement or name):
        raise click.UsageError("missing arguments/options")
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if requirement:
        name = _get_requirement(requirement)
    with click.progressbar(
        name, label="Removing", item_show_func=_show_package
    ) as packages:
        for package in packages:
            package, _ = _get_package_data(package)
            venv_dir = os.path.join(pipis_venvs, package)
            if os.path.isdir(venv_dir):
                # remove scripts symlink
                scripts = _get_console_scripts(package)
                for script in scripts:
                    script_name = script.split("/")[-1]
                    link = os.path.join(pipis_bin, script_name)
                    if os.path.islink(link):
                        os.remove(link)
                # remove package venv
                rmtree(venv_dir)
            else:
                click.secho(" is not installed, skip", fg="yellow")


if __name__ == "__main__":
    cli()
