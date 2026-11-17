def test_scalars_are_overridden(restique):
    merged = restique.merge_profiles(
        {'repository': 'a', 'password': 'x'},
        {'repository': 'b'},
    )
    assert merged == {'repository': 'b', 'password': 'x'}


def test_lists_are_combined(restique):
    merged = restique.merge_profiles(
        {'files': ['/a'], 'excludes': ['*.tmp']},
        {'files': ['/b']},
    )
    assert merged == {'files': ['/a', '/b'], 'excludes': ['*.tmp']}


def test_repo_hooks_are_combined(restique):
    merged = restique.merge_profiles(
        {'hooks': {'pre_repo': ['a'], 'post_repo': ['x']}},
        {'hooks': {'pre_repo': ['b']}},
    )
    assert merged == {'hooks': {'pre_repo': ['a', 'b'], 'post_repo': ['x']}}


def test_command_hooks_are_combined(restique):
    merged = restique.merge_profiles(
        {'hooks': {'pre_backup': ['a']}},
        {'hooks': {'pre_backup': ['b'], 'post_forget': ['c']}},
    )
    assert merged == {'hooks': {'pre_backup': ['a', 'b'], 'post_forget': ['c']}}


def test_hook_env_is_merged_by_name(restique):
    merged = restique.merge_profiles(
        {'hook_env': {'A': '1', 'C': 'global'}},
        {'hook_env': {'B': '2', 'C': 'profile'}},
    )
    assert merged == {'hook_env': {'A': '1', 'B': '2', 'C': 'profile'}}


def test_hook_env_values_are_not_merged_recursively(restique):
    merged = restique.merge_profiles(
        {'hook_env': {'pre_x': 'a', 'hooks': 'h'}},
        {'hook_env': {'pre_x': 'b'}},
    )
    assert merged == {'hook_env': {'pre_x': 'b', 'hooks': 'h'}}


def test_profiles_merge_in_order(restique):
    config = {
        'global': {'files': ['/g'], 'repository': 'global-repo'},
        'profiles': {
            'one': {'files': ['/one'], 'repository': 'one-repo'},
            'two': {'files': ['/two']},
        },
    }
    profile = restique.get_profile_config(config, 'one,two')
    assert profile['files'] == ['/g', '/one', '/two']
    assert profile['repository'] == 'one-repo'
