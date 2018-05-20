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

DEFAULT_PIPIS_VENVS = '~/.local/venvs/'
DEFAULT_PIPIS_BIN = '~/.local/bin/'


def _get_venv_data(package):
    PIPIS_VENVS = os.path.expanduser(
        os.environ.get('PIPIS_VENVS', DEFAULT_PIPIS_VENVS))
    venv_dir = os.path.join(PIPIS_VENVS, package)
    venv_py = os.path.join(venv_dir, 'bin', 'python')

    return venv_dir, venv_py


def _get_dist(package):
    _, venv_py = _get_venv_data(package)
    # get the module path from its venv and append it to the current path
    cmd_last_path = 'import sys; print(sys.path[-1])'
    venv_path = check_output([venv_py, '-c', cmd_last_path])
    venv_path = venv_path.decode("utf-8").strip()
    sys.path.append(venv_path)
    # reload pkg_resources module to take into account new path
    importlib.reload(pkg_resources)
    # get informations about package
    dist = pkg_resources.get_distribution(package)
    # remove package venv from current path
    del sys.path[-1]

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
    if dist.has_metadata('RECORD'):
        files = dist.get_metadata_lines('RECORD')
        for line in files:
            line = os.path.join(dist.location, line.split(',')[0])
            line = os.path.normpath(line)
            entry_points.append(line)
    # get entry_points from installed-files.txt file
    elif dist.has_metadata('installed-files.txt'):
        files = dist.get_metadata_lines('installed-files.txt')
        for line in files:
            line = os.path.join(dist.egg_info, line.split(',')[0])
            line = os.path.normpath(line)
            entry_points.append(line)
    # get entry_points from entry_points.txt file
    elif dist.has_metadata('entry_points.txt'):
        entry_points = dist.get_entry_map('console_scripts').keys()

    # filter only binaries
    entry_points = list(filter(methodcaller(
        'startswith', os.path.join(venv_dir, 'bin')), entry_points))

    return entry_points


def _abort_if_false(ctx, _, value):
    if not value:
        ctx.abort()


def _show_package(package):
    return package


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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


@cli.command(context_settings=CONTEXT_SETTINGS)
def version():
    """Show version and exit."""
    package_version = _get_version(__name__)
    click.echo(package_version)


@cli.command('list', context_settings=CONTEXT_SETTINGS)
def list_installed():
    """List installed packages."""
    PIPIS_VENVS = os.path.expanduser(
        os.environ.get('PIPIS_VENVS', DEFAULT_PIPIS_VENVS))
    table = {'Package': [], 'Version': []}
    for package in sorted(os.listdir(PIPIS_VENVS)):
        package_version = _get_version(package)
        table['Package'].append(package)
        table['Version'].append(package_version)
    click.echo(tabulate(table, headers='keys'))


@cli.command(context_settings=CONTEXT_SETTINGS)
def freeze():
    """Output installed packages in requirements format."""
    PIPIS_VENVS = os.path.expanduser(
        os.environ.get('PIPIS_VENVS', DEFAULT_PIPIS_VENVS))
    for package in sorted(os.listdir(PIPIS_VENVS)):
        package_version = _get_version(package)
        click.echo('{}=={}'.format(package, package_version))


@cli.command(context_settings=CONTEXT_SETTINGS, short_help='Install packages.')
@click.option('-y', '--yes', is_flag=True, callback=_abort_if_false,
              prompt='Do you want to continue?', expose_value=False,
              help='Confirm the action without prompting.')
@click.option('-r', '--requirement',
              help='Install from the given requirements file.')
@click.argument('name', nargs=-1, type=click.STRING)
def install(requirement, name):
    """
    Install packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    PIPIS_BIN = os.path.expanduser(
        os.environ.get('PIPIS_BIN', DEFAULT_PIPIS_BIN))
    # check presence of args
    if not (requirement or name):
        raise click.UsageError('missing arguments/options')
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError('too many arguments/options')
    # populate packages list with req file
    if requirement:
        try:
            with open(requirement, 'r') as req:
                name = map(str.strip, req.readlines())
        except IOError:
            raise click.FileError(requirement)
    # process packages
    with click.progressbar(name, label='Installing',
                           item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir, venv_py = _get_venv_data(package)
            cmd = [venv_py, '-m', 'pip', 'install', '--quiet']
            # create venv if not exists
            if not os.path.isdir(venv_dir):
                create(venv_dir, symlinks=True, with_pip=True)
                # upgrade pip in venv
                cmd.extend(['--upgrade', 'pip'])
                check_call(cmd)
                # install package in venv
                cmd.append(package)
                try:
                    check_call(cmd)
                except CalledProcessError:
                    rmtree(venv_dir)
                    message = 'Cannot install {}'.format(package)
                    raise click.BadArgumentUsage(message)
                # create scripts symlink
                scripts = _get_console_scripts(package)
                if len(scripts) < 1:
                    rmtree(venv_dir)
                    message = 'library installation is not supported by pipis'
                    raise click.ClickException(message)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(PIPIS_BIN, script_name)
                    try:
                        os.symlink(script, link)
                    except FileExistsError:
                        rmtree(venv_dir)
                        message = '{} already exists'.format(link)
                        raise click.ClickException(message)
            else:
                click.secho(' is already installed, skip', fg='green')


@cli.command(context_settings=CONTEXT_SETTINGS, short_help='Update packages.')
@click.option('-y', '--yes', is_flag=True, callback=_abort_if_false,
              prompt='Do you want to continue?', expose_value=False,
              help='Confirm the action without prompting.')
@click.option('-r', '--requirement',
              help='Install from the given requirements file.')
@click.argument('name', nargs=-1, type=click.STRING)
def update(requirement, name):
    """
    Update packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.

    If you do not specify package name or requirements file, it will update
    all installed packages.
    """
    PIPIS_VENVS = os.path.expanduser(
        os.environ.get('PIPIS_VENVS', DEFAULT_PIPIS_VENVS))
    PIPIS_BIN = os.path.expanduser(
        os.environ.get('PIPIS_BIN', DEFAULT_PIPIS_BIN))
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError('too much arguments/options')
    # populate packages list with req file
    if requirement:
        try:
            with open(requirement, 'r') as req:
                name = map(str.strip, req.readlines())
        except IOError:
            raise click.FileError(requirement)
    # populate packages list with all currently installed
    if not name:
        name = os.listdir(PIPIS_VENVS)
    with click.progressbar(name, label='Updating',
                           item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir, venv_py = _get_venv_data(package)
            if not os.path.isdir(venv_dir):
                message = '{} is not installed'.format(package)
                raise click.ClickException(message)
            cmd = [venv_py, '-m', 'pip', 'install', '--quiet']
            # upgrade pip in venv
            cmd.extend(['--upgrade', 'pip'])
            check_call(cmd)
            # install package in venv
            cmd.extend(['--upgrade', package])
            check_call(cmd)
            # update scripts symlink
            scripts = _get_console_scripts(package)
            for script in scripts:
                script_name = script.split('/')[-1]
                link = os.path.join(PIPIS_BIN, script_name)
                if not os.path.islink(link):
                    os.symlink(script, link)


@cli.command(context_settings=CONTEXT_SETTINGS,
             short_help='Uninstall packages.')
@click.option('-y', '--yes', is_flag=True, callback=_abort_if_false,
              prompt='Do you want to continue?', expose_value=False,
              help='Confirm the action without prompting.')
@click.option('-r', '--requirement',
              help='Install from the given requirements file.')
@click.argument('name', nargs=-1, type=click.STRING)
def uninstall(requirement, name):
    """
    Uninstall packages, where NAME is the package name.
    You can specify multiple names.

    Packages names and "requirements files" are mutually exclusive.
    """
    PIPIS_VENVS = os.path.expanduser(
        os.environ.get('PIPIS_VENVS', DEFAULT_PIPIS_VENVS))
    PIPIS_BIN = os.path.expanduser(
        os.environ.get('PIPIS_BIN', DEFAULT_PIPIS_BIN))
    # check presence of args
    if not (requirement or name):
        raise click.UsageError('missing arguments/options')
    # check mutually esclusive args
    if requirement and name:
        raise click.UsageError('too much arguments/options')
    # populate packages list with req file
    if requirement:
        try:
            with open(requirement, 'r') as req:
                name = map(str.strip, req.readlines())
        except IOError:
            raise click.FileError(requirement)
    with click.progressbar(name, label='Removing',
                           item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir = os.path.join(PIPIS_VENVS, package)
            if os.path.isdir(venv_dir):
                # remove scripts symlink
                scripts = _get_console_scripts(package)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(PIPIS_BIN, script_name)
                    if os.path.islink(link):
                        os.remove(link)
                # remove package venv
                rmtree(venv_dir)
            else:
                click.secho(' is not installed, skip', fg='yellow')


if __name__ == '__main__':
    cli()
