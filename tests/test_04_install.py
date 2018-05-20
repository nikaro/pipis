import os
import sys
sys.path.append('..')

import click
import pipis
from click.testing import CliRunner

from helpers import set_env
import pipis

runner = CliRunner()


def test_install_missing(tmpdir):
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
