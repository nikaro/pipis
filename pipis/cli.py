"""
commands for pipis
"""

import os

import click
from tabulate import tabulate

from . import lib as p


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
    package_version = p.get_version("pipis")
    click.echo(package_version)


@cli.command("list", context_settings=CONTEXT_SETTINGS)
def list_installed():
    """List installed packages."""
    pipis_venvs, _ = p.get_pipis()
    table = {"Package": [], "Version": []}
    for package in sorted(os.listdir(pipis_venvs)):
        package_version = p.get_version(package)
        table["Package"].append(package)
        table["Version"].append(package_version)
    click.echo(tabulate(table, headers="keys"))


@cli.command(context_settings=CONTEXT_SETTINGS)
def freeze():
    """Output installed packages in requirements format."""
    pipis_venvs, _ = p.get_pipis()
    for package in sorted(os.listdir(pipis_venvs)):
        package_version = p.get_version(package)
        click.echo("{}=={}".format(package, package_version))


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Install packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=p.abort_if_false,
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
    "--system",
    is_flag=True,
    help="Give the virtual environment access to the system site-packages dir.",
)
@click.option(
    "-U",
    "--upgrade",
    is_flag=True,
    help="Upgrade all specified packages to the newest available version.",
)
@click.option(
    "-I",
    "--ignore-installed",
    is_flag=True,
    help="Ignore the installed packages (reinstalling instead).",
)
@click.option("-v", "--verbose", is_flag=True, help="Give more output.")
@click.argument("name", nargs=-1, type=click.STRING)
def install(**kwargs):
    """
    Install packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    # check presence of args
    if not (kwargs["requirement"] or kwargs["name"]):
        raise click.UsageError("missing arguments/options")
    # check mutually esclusive args
    if kwargs["requirement"] and kwargs["name"]:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if kwargs["requirement"]:
        kwargs["name"] = p.get_requirement(kwargs["requirement"])
    # do not add dependency to multiple packages
    if len(kwargs["name"]) > 1 and kwargs["dependency"]:
        raise click.UsageError("cannot add dependecy to multiple packages")
    # process packages
    with click.progressbar(
        kwargs["name"], label="Installing", item_show_func=p.show_package
    ) as packages:
        for package in packages:
            p.venv(package, kwargs["system"])
            cmd = p.install(
                package,
                kwargs["verbose"],
                kwargs["upgrade"],
                kwargs["ignore_installed"],
            )
            p.install_dep(cmd, package, kwargs["dependency"])
            p.link(package)


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Update packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=p.abort_if_false,
    prompt="Do you want to continue?",
    expose_value=False,
    help="Confirm the action without prompting.",
)
@click.option("-r", "--requirement", help="Install from the given requirements file.")
@click.option(
    "-I",
    "--ignore-installed",
    is_flag=True,
    help="Ignore the installed packages (reinstalling instead).",
)
@click.option("-v", "--verbose", is_flag=True, help="Give more output.")
@click.argument("name", nargs=-1, type=click.STRING)
def update(**kwargs):
    """
    Update packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.

    If you do not specify package name or requirements file, it will update
    all installed packages.
    """
    pipis_venvs, _ = p.get_pipis()
    # check mutually esclusive args
    if kwargs["requirement"] and kwargs["name"]:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if kwargs["requirement"]:
        kwargs["name"] = p.get_requirement(kwargs["requirement"])
    # populate packages list with all currently installed
    if not kwargs["name"]:
        kwargs["name"] = os.listdir(pipis_venvs)
    with click.progressbar(
        kwargs["name"], label="Updating", item_show_func=p.show_package
    ) as packages:
        for package in packages:
            p.venv(package, upgrade=True)
            cmd = p.install(
                package,
                kwargs["verbose"],
                upgrade=True,
                ignore=kwargs["ignore_installed"],
            )
            p.install_dep(cmd, package)
            p.link(package, upgrade=True)


@cli.command(context_settings=CONTEXT_SETTINGS, short_help="Uninstall packages.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    callback=p.abort_if_false,
    prompt="Do you want to continue?",
    expose_value=False,
    help="Confirm the action without prompting.",
)
@click.option("-r", "--requirement", help="Install from the given requirements file.")
@click.argument("name", nargs=-1, type=click.STRING)
def uninstall(**kwargs):
    """
    Uninstall packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    # check presence of args
    if not (kwargs["requirement"] or kwargs["name"]):
        raise click.UsageError("missing arguments/options")
    # check mutually esclusive args
    if kwargs["requirement"] and kwargs["name"]:
        raise click.UsageError("too many arguments/options")
    # populate packages list with req file
    if kwargs["requirement"]:
        kwargs["name"] = p.get_requirement(kwargs["requirement"])
    with click.progressbar(
        kwargs["name"], label="Removing", item_show_func=p.show_package
    ) as packages:
        for package in packages:
            p.remove(package)
