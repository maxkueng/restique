def test_bool_arg(restique):
    assert restique.get_cmd_arg('quiet', {'quiet': True}) == ['--quiet']
    assert restique.get_cmd_arg('quiet', {'quiet': False}) == []
    assert restique.get_cmd_arg('quiet', {}) == []


def test_list_arg_repeats_flag(restique):
    config = {'excludes': ['*.tmp', '*.log']}
    assert restique.get_cmd_arg('excludes', config) == [
        '--exclude', '*.tmp', '--exclude', '*.log',
    ]


def test_scalar_arg_is_stringified(restique):
    assert restique.get_cmd_arg('keep_last', {'keep_last': 7}) == ['--keep-last', '7']


def test_base_cmd(restique, restic):
    config = {'repository': '/repo', 'json': True, 'restic_path': restic}
    assert restique.get_base_cmd('snapshots', config) == [
        restic, '--repo', '/repo', '--json', 'snapshots',
    ]


def test_base_env_s3(restique):
    env = restique.get_base_env({
        'repository': 's3:example.com/bucket',
        'password': 'pw',
        'aws_access_key': 'id',
        'aws_secret_key': 'secret',
    })
    assert env == {
        'RESTIC_PASSWORD': 'pw',
        'AWS_ACCESS_KEY_ID': 'id',
        'AWS_SECRET_ACCESS_KEY': 'secret',
    }
