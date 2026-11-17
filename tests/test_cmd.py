import pytest


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


def test_base_env_without_credentials(restique):
    env = restique.get_base_env({'repository': 's3:example.com/bucket', 'password': 'pw'})
    assert env == {'RESTIC_PASSWORD': 'pw'}


def test_base_env_partial_credentials(restique):
    env = restique.get_base_env({
        'repository': 'azure:container:/',
        'password': 'pw',
        'azure_account_name': 'account',
    })
    assert env == {'RESTIC_PASSWORD': 'pw', 'AZURE_ACCOUNT_NAME': 'account'}


@pytest.mark.parametrize('repository, credentials', [
    ('b2:bucket:/', {'b2_account_id': 'B2_ACCOUNT_ID', 'b2_account_key': 'B2_ACCOUNT_KEY'}),
    ('azure:c:/', {'azure_account_name': 'AZURE_ACCOUNT_NAME', 'azure_account_key': 'AZURE_ACCOUNT_KEY'}),
    ('gs:bucket:/', {
        'google_project_id': 'GOOGLE_PROJECT_ID',
        'google_application_credentials': 'GOOGLE_APPLICATION_CREDENTIALS',
    }),
])
def test_base_env_backend_credentials(restique, repository, credentials):
    config = {'repository': repository, 'password': 'pw'}
    config.update({key: key + '-value' for key in credentials})
    env = restique.get_base_env(config)
    expected = {name: key + '-value' for key, name in credentials.items()}
    assert env == {'RESTIC_PASSWORD': 'pw', **expected}


def test_base_env_ignores_other_backend_credentials(restique):
    env = restique.get_base_env({
        'repository': '/local/repo',
        'password': 'pw',
        'aws_access_key': 'id',
    })
    assert env == {'RESTIC_PASSWORD': 'pw'}
