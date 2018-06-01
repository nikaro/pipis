from pathlib import Path
import os
import sys
sys.path.append('..')

import click
import pipis
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_install_missing_arg(tmpdir):
    set_env(tmpdir)

    msg = 'Error: missing arguments/options'

    result = runner.invoke(pipis.install, ['-y'])

    assert msg in result.output
    assert result.exit_code == 2


def test_install(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    result = runner.invoke(pipis.install, ['-y', package])

    assert 'Installing' in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_system_site_packages(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    result = runner.invoke(pipis.install, ['-y', '-s', package])

    assert 'Installing' in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_inexistant_package(tmpdir):
    set_env(tmpdir)

    package = 'rdnieuribiubsiesgppxna'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'Error: Cannot install {}'.format(package)

    result = runner.invoke(pipis.install, ['-y', package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_install_library(tmpdir):
    set_env(tmpdir)

    package = 'art'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'Error: library installation is not supported by pipis'

    result = runner.invoke(pipis.install, ['-y', package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_install_already_installed_package(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'is already installed, skip'

    runner.invoke(pipis.install, ['-y', package])
    result = runner.invoke(pipis.install, ['-y', package])

    assert msg in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_already_exists_symlink(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = '{} already exists'.format(link)

    Path(link).touch()
    result = runner.invoke(pipis.install, ['-y', package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_install_requirements(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    req = tmpdir.join('requirements.txt')
    with open(req, 'w') as f:
        f.write(package)
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    result = runner.invoke(pipis.install, ['-y', '-r', req])

    assert 'Installing' in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_install_inexistant_requirements(tmpdir):
    set_env(tmpdir)

    req = str(tmpdir.join('requirements.txt'))

    msg = 'Error: Could not open file'

    result = runner.invoke(pipis.install, ['-y', '-r', req])

    assert msg in result.output
    assert result.exit_code != 0


def test_install_too_many_arg(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    req = tmpdir.join('requirements.txt')
    with open(req, 'w') as f:
        f.write(package)
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'Error: too many arguments/options'

    result = runner.invoke(pipis.install, ['-y', package, '-r', req])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 2
