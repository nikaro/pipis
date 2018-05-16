import click
import os
import subprocess
import sys
import venv


@click.group()
def cli():
    pass


@cli.command('list')
def list_installed():
    click.echo('list')


@cli.command()
@click.option('-y', '--yes', is_flag=True, help='Do not ask for confirmation.')
@click.argument('name', nargs=-1)
def install(name, yes):
    if name:
        click.echo('install {}'.format(name))
        for pkg in name:
            venv_path = os.path.expanduser('~/.local/venvs/{}'.format(pkg))
            venv_python = os.path.join(venv_path, 'bin', 'python')
            # create venv if not exists
            if not os.path.exists(venv_path):
                venv.create(venv_path, symlinks=True, with_pip=True)
            # install package in venv
            subprocess.check_call([venv_python, '-m', 'pip', 'install', pkg])
    else:
        click.echo('install')


@cli.command()
@click.argument('name', required=False)
def update(name):
    click.echo('update')


@cli.command()
@click.argument('name', required=False)
def uninstall(name):
    click.echo('uninstall')

if __name__ == '__main__':
    cli()
