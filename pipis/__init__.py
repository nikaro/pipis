import click
import importlib
from operator import methodcaller
import os
import pkg_resources
from shutil import rmtree
from subprocess import check_call, check_output
import sys
from venv import create

VENV_ROOT_DIR = os.path.expanduser('~/.local/venvs/')
BIN_DIR = os.path.expanduser('~/.local/bin/')


def _get_venv_data(package):
    venv_dir = os.path.join(VENV_ROOT_DIR, package)
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


def _show_package(package):
    if package is not None:
        return package


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Show version and exit."""
    version = _get_version(__name__)
    click.echo(version)


@cli.command('list')
def list_installed():
    click.echo('Installed:')
    for package in sorted(os.listdir(VENV_ROOT_DIR)):
        version = _get_version(package)
        click.echo('  - {} ({})'.format(package, version))


@cli.command()
@click.confirmation_option()
@click.option('-r', '--requirement')
@click.argument('name', nargs=-1, type=click.STRING)
def install(requirement, name):
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
    # process packages
    with click.progressbar(name, label='Installing', item_show_func=_show_package) as packages:
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
                check_call(cmd)
                # create scripts symlink
                scripts = _get_console_scripts(package)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(BIN_DIR, script_name)
                    if not os.path.islink(link):
                        os.symlink(script, link)
            else:
                click.secho(' is already installed, skip', fg='green')



@cli.command()
@click.confirmation_option()
@click.option('-r', '--requirement')
@click.argument('name', nargs=-1, type=click.STRING)
def update(requirement, name):
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
        name = os.listdir(VENV_ROOT_DIR)
    with click.progressbar(name, label='Updating', item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir, venv_py = _get_venv_data(package)
            if not os.path.isdir(venv_dir):
                click.secho(' is not installed, skip', fg='yellow')
                continue
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
                link = os.path.join(BIN_DIR, script_name)
                if not os.path.islink(link):
                    os.symlink(script, link)


@cli.command()
@click.confirmation_option()
@click.option('-r', '--requirement')
@click.argument('name', nargs=-1, type=click.STRING)
def uninstall(requirement, name):
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
    with click.progressbar(name, label='Removing', item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir = os.path.join(VENV_ROOT_DIR, package)
            if os.path.isdir(venv_dir):
                # remove scripts symlink
                scripts = _get_console_scripts(package)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(BIN_DIR, script_name)
                    if os.path.islink(link):
                        os.remove(link)
                # remove package venv
                rmtree(venv_dir)
            else:
                click.secho(' is not installed, skip', fg='yellow')

if __name__ == '__main__':
    cli()
