import json

import pytest


@pytest.fixture
def setup(runner, tmp_path):
    data = tmp_path / 'data'
    data.mkdir()
    (data / 'file').write_text('hello')
    repo = tmp_path / 'repo'
    log = tmp_path / 'hooks.log'

    def configure(**profile):
        base = {
            'repository': str(repo),
            'password': 'pw',
            'initialize': True,
            'files': [str(data)],
        }
        base.update(profile)
        runner.write_config({'default_profile': 'p', 'profiles': {'p': base}})

    configure()
    return runner, repo, data, log, configure


def test_backup_initializes_repo(setup):
    runner, repo, data, _, _ = setup
    result = runner.run('backup', '-q')
    assert result.returncode == 0, result.stderr
    snapshots = runner.snapshots(repo, 'pw')
    assert [s['paths'] for s in snapshots] == [[str(data)]]


def test_backup_to_existing_repo(setup):
    runner, repo, _, _, _ = setup
    assert runner.run('backup', '-q').returncode == 0
    result = runner.run('backup', '-q')
    assert result.returncode == 0, result.stderr
    assert len(runner.snapshots(repo, 'pw')) == 2


def test_missing_repo_without_initialize(setup):
    runner, repo, _, _, configure = setup
    configure(initialize=False)
    result = runner.run('backup', '-q')
    assert result.returncode == 1
    assert not repo.exists()


def test_wrong_password_is_reported(setup):
    runner, _, _, _, configure = setup
    assert runner.run('backup', '-q').returncode == 0
    configure(password='wrong')
    result = runner.run('backup', '-q')
    assert result.returncode == 12
    assert 'wrong password' in result.stderr


def test_backup_stdin_from_command(setup):
    runner, repo, _, _, _ = setup
    result = runner.run('backup', '-q', '--stdin-from-command', '--', 'echo', 'from-cmd')
    assert result.returncode == 0, result.stderr
    assert [s['paths'] for s in runner.snapshots(repo, 'pw')] == [['/stdin']]


def test_forget_keep_last(setup):
    runner, repo, _, _, configure = setup
    configure(keep_last=1)
    for _ in range(3):
        assert runner.run('backup', '-q').returncode == 0
    result = runner.run('forget')
    assert result.returncode == 0, result.stderr
    assert len(runner.snapshots(repo, 'pw')) == 1


def test_hook_order(setup):
    runner, _, _, log, configure = setup
    configure(hooks={
        name: [f'echo {name} >> {log}']
        for name in ['pre_repo', 'pre_backup', 'post_backup', 'post_repo']
    })
    result = runner.run('backup', '-q')
    assert result.returncode == 0, result.stderr
    assert log.read_text().splitlines() == [
        'pre_repo', 'pre_backup', 'post_backup', 'post_repo',
    ]


def test_failing_pre_hook_aborts_backup(setup):
    runner, repo, _, log, configure = setup
    configure(hooks={
        'pre_backup': ['false'],
        'post_repo': [f'echo post_repo >> {log}'],
    })
    result = runner.run('backup', '-q')
    assert result.returncode != 0
    assert not repo.exists()
    assert not log.exists()


def test_ignored_hook_failure_continues(setup):
    runner, repo, _, _, configure = setup
    configure(hooks={'pre_backup': ['- false']})
    result = runner.run('backup', '-q')
    assert result.returncode == 0, result.stderr
    assert len(runner.snapshots(repo, 'pw')) == 1


def test_json_output_is_clean(setup):
    runner, _, _, _, configure = setup
    configure(json=True, hook_env={'X': '1'}, hooks={'pre_repo': ['true']})
    assert runner.run('backup', '-q').returncode == 0
    result = runner.run('snapshots')
    assert result.returncode == 0, result.stderr
    assert len(json.loads(result.stdout)) == 1


def test_password_command_is_rejected(setup):
    runner, repo, _, _, _ = setup
    result = runner.run('backup', '-q', '--password-command', 'echo pw')
    assert result.returncode == 1
    assert 'not supported' in result.stderr
    assert not repo.exists()


@pytest.mark.parametrize('subcommand', ['add', 'passwd'])
def test_key_with_new_password(setup, tmp_path, subcommand):
    runner, repo, _, _, _ = setup
    assert runner.run('backup', '-q').returncode == 0
    new_password = tmp_path / 'new-password'
    new_password.write_text('new-pw')
    result = runner.run('key', subcommand, '--new-password-file', str(new_password))
    assert result.returncode == 0, result.stderr
    assert len(runner.snapshots(repo, 'new-pw')) == 1


def test_combined_short_password_flag_is_rejected(setup, tmp_path):
    runner, repo, _, _, _ = setup
    assert runner.run('backup', '-q').returncode == 0
    password_file = tmp_path / 'password'
    password_file.write_text('pw')
    result = runner.run('snapshots', '-qp', str(password_file))
    assert result.returncode == 1
    assert 'not supported' in result.stderr


def test_short_flag_value_containing_p_is_allowed(setup):
    runner, repo, data, _, _ = setup
    (data / 'skip.pyc').write_text('x')
    result = runner.run('backup', '-q', '-e*.pyc')
    assert result.returncode == 0, result.stderr
    snapshot_id = runner.snapshots(repo, 'pw')[0]['short_id']
    listing = runner.run('ls', snapshot_id)
    assert 'file' in listing.stdout
    assert 'skip.pyc' not in listing.stdout
