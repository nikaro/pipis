import click
import os
import shutil
import subprocess
import sys
import venv

VENV_ROOT_DIR = os.path.expanduser('~/.local/venvs')


@click.group()
def cli():
    pass


@cli.command('list')
def list_installed():
    click.echo('Installed:')
    for item in sorted(os.listdir(VENV_ROOT_DIR)):
        click.echo('  - {}'.format(item))


@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=True, type=click.STRING)
def install(name):
    click.echo('Install: {}'.format(', '.join(sorted(name))))
    with click.progressbar(name) as packages:
        for item in packages:
            venv_path = os.path.join(VENV_ROOT_DIR, item)
            venv_python = os.path.join(venv_path, 'bin', 'python')
            cmd = [venv_python, '-m', 'pip', 'install', '--quiet']
            # create venv if not exists
            if not os.path.exists(venv_path):
                venv.create(venv_path, symlinks=True, with_pip=True)
                # upgrade pip in venv
                cmd.extend(['--upgrade', 'pip'])
                subprocess.check_call(cmd)
            # install package in venv
            cmd.append(item)
            subprocess.check_call(cmd)
            # TODO: install binary symlink


@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=False, type=click.STRING)
def update(name):
    if not name:
        name = os.listdir(VENV_ROOT_DIR)
    click.echo('Update: {}'.format(', '.join(sorted(name))))
    with click.progressbar(name) as packages:
        for item in packages:
            venv_path = os.path.join(VENV_ROOT_DIR, item)
            venv_python = os.path.join(venv_path, 'bin', 'python')
            cmd = [venv_python, '-m', 'pip', 'install', '--quiet']
            # upgrade pip in venv
            cmd.extend(['--upgrade', 'pip'])
            subprocess.check_call(cmd)
            # install package in venv
            cmd.extend(['--upgrade', item])
            subprocess.check_call(cmd)
            # TODO: update binary symlink


@cli.command()
@click.confirmation_option()
@click.argument('name', nargs=-1, required=True, type=click.STRING)
def uninstall(name):
    click.echo('Uninstall: {}'.format(', '.join(sorted(name))))
    with click.progressbar(name) as packages:
        for item in packages:
            # remove package venv
            venv_path = os.path.join(VENV_ROOT_DIR, item)
            shutil.rmtree(venv_path)
            # TODO: remove binary symlink

if __name__ == '__main__':
    cli()
