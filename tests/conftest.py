import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / 'restique'


@pytest.fixture(scope='session')
def restique():
    loader = importlib.machinery.SourceFileLoader('restique', str(SCRIPT))
    module = importlib.util.module_from_spec(
        importlib.util.spec_from_loader('restique', loader)
    )
    loader.exec_module(module)
    return module


@pytest.fixture
def restic():
    path = shutil.which('restic')
    if not path:
        pytest.skip('restic not installed')
    return path


class Runner:
    def __init__(self, tmp_path, restic):
        self.tmp_path = tmp_path
        self.restic = restic
        self.config_path = tmp_path / 'restique.json'
        self.env = os.environ.copy()
        self.env['XDG_CACHE_HOME'] = str(tmp_path / 'cache')
        for name in list(self.env):
            if name.startswith('RESTIC_'):
                del self.env[name]

    def write_config(self, config):
        self.config_path.write_text(json.dumps(config))

    def run(self, *args, profile=None):
        cmd = [sys.executable, '-B', str(SCRIPT), '--config', str(self.config_path)]
        if profile:
            cmd += ['--profile', profile]
        cmd += list(args)
        return subprocess.run(
            cmd,
            cwd=self.tmp_path,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def snapshots(self, repo, password):
        result = subprocess.run(
            [self.restic, '-r', str(repo), 'snapshots', '--json'],
            env={**self.env, 'RESTIC_PASSWORD': password},
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)


@pytest.fixture
def runner(tmp_path, restic):
    return Runner(tmp_path, restic)
