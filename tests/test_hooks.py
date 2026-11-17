import pytest


@pytest.fixture
def run_hooks(restique, tmp_path):
    log = tmp_path / 'log'

    def run(*hooks):
        config = {'hooks': {'pre_repo': list(hooks)}}
        result = restique.run_hooks(config, {}, 'pre_repo')
        lines = log.read_text().splitlines() if log.exists() else []
        return result, lines

    run.log = log
    return run


def test_no_hooks(restique):
    assert restique.run_hooks({}, {}, 'pre_repo') is True
    assert restique.run_hooks({'hooks': {}}, {}, 'pre_repo') is True


def test_hooks_run_in_order(run_hooks):
    ok, lines = run_hooks(f'echo one >> {run_hooks.log}', f'echo two >> {run_hooks.log}')
    assert ok is True
    assert lines == ['one', 'two']


def test_failing_hook_stops_execution(run_hooks):
    ok, lines = run_hooks('false', f'echo after >> {run_hooks.log}')
    assert ok is False
    assert lines == []


@pytest.mark.parametrize('prefix', ['-', '- ', '-   '])
def test_prefixed_hook_failure_is_ignored(run_hooks, prefix):
    ok, lines = run_hooks(prefix + 'false', f'echo after >> {run_hooks.log}')
    assert ok is True
    assert lines == ['after']


def test_prefixed_hook_still_runs(run_hooks):
    ok, lines = run_hooks(f'-echo ran >> {run_hooks.log}')
    assert ok is True
    assert lines == ['ran']


def test_prev_hook_rc(run_hooks):
    log = run_hooks.log
    ok, lines = run_hooks(
        f'echo "$RESTIQUE_PREV_HOOK_RC" >> {log}',
        '-exit 3',
        f'echo "$RESTIQUE_PREV_HOOK_RC" >> {log}',
        f'echo "$RESTIQUE_PREV_HOOK_RC" >> {log}',
    )
    assert ok is True
    assert lines == ['0', '3', '0']


def test_hook_env(restique, tmp_path):
    log = tmp_path / 'log'
    config = {
        'repository': '/some/repo',
        'hook_env': {'MY_VAR': 42},
        'hooks': {'pre_backup': [
            f'echo "$RESTIQUE_HOOK $RESTIQUE_REPOSITORY $MY_VAR" >> {log}',
        ]},
    }
    assert restique.run_hooks(config, {}, 'pre_backup') is True
    assert log.read_text().splitlines() == ['pre_backup /some/repo 42']
