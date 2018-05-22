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


def test_update(tmpdir):
    set_env(tmpdir)

    package = 'pipis'

    runner.invoke(pipis.install, ['-y', package])
    result = runner.invoke(pipis.update, ['-y', package])

    assert 'Updating' in result.output
    assert result.exit_code == 0


def test_update_all(tmpdir):
    set_env(tmpdir)

    packages = ['pipis', 'pep8']

    for package in packages:
        runner.invoke(pipis.install, ['-y', package])
    result = runner.invoke(pipis.update, ['-y'])

    assert 'Updating' in result.output
    assert result.exit_code == 0


def test_update_uninstalled_package(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'is not installed'

    result = runner.invoke(pipis.update, ['-y', package])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code != 0


def test_update_requirements(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    req = tmpdir.join('requirements.txt')
    with open(req, 'w') as f:
        f.write(package)
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    runner.invoke(pipis.install, ['-y', '-r', req])
    result = runner.invoke(pipis.update, ['-y', '-r', req])

    assert 'Updating' in result.output
    assert os.path.isdir(venv)
    assert os.path.isfile(script)
    assert os.path.islink(link)
    assert result.exit_code == 0


def test_update_inexistant_requirements(tmpdir):
    set_env(tmpdir)

    req = str(tmpdir.join('requirements.txt'))

    msg = 'Error: Could not open file'

    result = runner.invoke(pipis.update, ['-y', '-r', req])

    assert msg in result.output
    assert result.exit_code != 0


def test_update_too_many_arg(tmpdir):
    set_env(tmpdir)

    package = 'pipis'
    req = tmpdir.join('requirements.txt')
    with open(req, 'w') as f:
        f.write(package)
    venv = os.path.join(os.environ['PIPIS_VENVS'], package)
    script = os.path.join(venv, 'bin', package)
    link = os.path.join(os.environ['PIPIS_BIN'], package)

    msg = 'Error: too many arguments/options'

    result = runner.invoke(pipis.update, ['-y', package, '-r', req])

    assert msg in result.output
    assert not os.path.isdir(venv)
    assert not os.path.isfile(script)
    assert not os.path.islink(link)
    assert result.exit_code == 2
