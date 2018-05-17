import click
from operator import methodcaller
import os
from shutil import rmtree
from subprocess import check_call, check_output
import sys
from venv import create

VENV_ROOT_DIR = os.path.expanduser('~/.local/venvs/')
BIN_DIR = os.path.expanduser('~/.local/bin/')


def _show_package(package):
    if package is not None:
        return package


def _get_console_scripts(venv_dir, venv_py, package):
    venv_bin_dir = os.path.join(venv_dir, 'bin')
    # get the module path from its venv and append it to the current path
    venv_path = check_output(
        [venv_py, '-c', 'import sys; print(sys.path[-1])']).decode("utf-8").strip()
    sys.path.append(venv_path)
    # get informations about package
    import pkg_resources
    dist = pkg_resources.get_distribution(package)
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
        'startswith', venv_bin_dir), entry_points))

    return entry_points


@click.group()
def cli():
    pass


@cli.command('list')
def list_installed():
    click.echo('Installed:')
    for package in sorted(os.listdir(VENV_ROOT_DIR)):
        click.echo('  - {}'.format(package))


@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=True, type=click.STRING)
def install(name):
    with click.progressbar(name, label='Installing', item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir = os.path.join(VENV_ROOT_DIR, package)
            venv_py = os.path.join(venv_dir, 'bin', 'python')
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
                scripts = _get_console_scripts(venv_dir, venv_py, package)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(BIN_DIR, script_name)
                    if not os.path.islink(link):
                        os.symlink(script, link)
            else:
                click.secho(' Info: {} is already installed, skipping it'.format(
                    package), fg='green')



@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=False, type=click.STRING)
def update(name):
    if not name:
        name = os.listdir(VENV_ROOT_DIR)
    with click.progressbar(name, label='Updating', item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir = os.path.join(VENV_ROOT_DIR, package)
            if not os.path.isdir(venv_dir):
                click.secho(' Warning: {} is not installed, skipping it'.format(
                    package), fg='yellow')
                continue
            venv_py = os.path.join(venv_dir, 'bin', 'python')
            cmd = [venv_py, '-m', 'pip', 'install', '--quiet']
            # upgrade pip in venv
            cmd.extend(['--upgrade', 'pip'])
            check_call(cmd)
            # install package in venv
            cmd.extend(['--upgrade', package])
            check_call(cmd)
            # update scripts symlink
            scripts = _get_console_scripts(venv_dir, venv_py, package)
            for script in scripts:
                script_name = script.split('/')[-1]
                link = os.path.join(BIN_DIR, script_name)
                if not os.path.islink(link):
                    os.symlink(script, link)


@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=True, type=click.STRING)
def uninstall(name):
    with click.progressbar(name, label='Removing', item_show_func=_show_package) as packages:
        for package in packages:
            venv_dir = os.path.join(VENV_ROOT_DIR, package)
            venv_py = os.path.join(venv_dir, 'bin', 'python')
            if os.path.isdir(venv_dir):
                # remove scripts symlink
                scripts = _get_console_scripts(venv_dir, venv_py, package)
                for script in scripts:
                    script_name = script.split('/')[-1]
                    link = os.path.join(BIN_DIR, script_name)
                    if os.path.islink(link):
                        os.remove(link)
                # remove package venv
                rmtree(venv_dir)
            else:
                click.secho(' Warning: {} is not installed, skipping it'.format(
                    package), fg='yellow')

if __name__ == '__main__':
    cli()
