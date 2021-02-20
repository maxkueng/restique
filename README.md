# ![restique](https://raw.githubusercontent.com/maxkueng/restique/master/restique.svg?sanitize=true)

**STABILITY: PROTOTYPE**  

Le **restique** is a wrapper around the [restic][restic] backup tool that
allows using multiple backup profiles defined in a JSON configuration file.  
You should be familiar with restic before using this. Read the [restic manual][restic-manual] first.

It's written in Python and uses only core modules so that there are no extra
dependencies to install, and no compilation or build steps.

_:see_no_evil:  I don't really know Python. So if you see some bad things in the
code please feel free to file an issue or create a pull request. It will be
appreciated._

Jump: [Installation](#installation) | [Usage](#usage) | [Configuration](#configuration) | [Examples](#examples) | [License](#license)

## Installation

First, install Python 3. You probably already have it. Then [install
restic][restic-install]. Then download the `restique` executable and put it
somewhere in your `PATH`. Don't forget to `chmod +x path/to/restique`

_:penguin: This program has only been tested on Linux with Python 3.6. It might not work
with older Python versions or on other platforms._

## Usage

```
restique [-h] [--debug] [--config PATH] [--profile NAME] command [resticargs]
```

 - `-h, --help`: Print the help / usage text.

 - `-V, --version`: Print the version number.

 - `-d, --debug`: Set the log level to debug.

 - `-c PATH, --config PATH`: Specify the path to the configuration file. If not
   specified restic will check `./.restiquerc`, `~/.restiquerc`,
   `~/.config/restique/config`, `/etc/restique.rc` in this exact order and use
   the first one that exists.

 - `-p NAME(S), --profile NAME(S)`: Specify the name of the backup profile to
   be used. If not specified, restique will use the `"default_profile"`
   provided in the config file.  
   Multiple profile names can be specified as a comma-separated list (without
   spaces). If multiple profile names are provided they will be merged into
   each other in the order they are specified. This can be useful when
   combining partial profiles.

 - `command`: The restic command to run. E.g. "init", "backup", "restore", ...
   check out the [restic manual][restic-manual] for a complete list.

 - `resticargs`: All additional arguments will be directly passed to the restic
   command.

#### Example

```sh
# Run a backup
restique -p home backup

# Restore the latest backup to /tmp/restore-home
restique -p home restore latest --target /tmp/restore-home
```

## Configuration

```js
{
  "restic_path": "/path/to/restic_executable",
  "default_profile": "my_profile",
  "global": {
    // ... profile config applied to all profiles
  },
  "profiles": {
    "my_profile": {
      "json": true,
      "no_lock": true,
      "quiet": true,
      "files": [
        "/path/to/directory/or/file_to_backup",
        "/path/to/directory/or/another_file_to_backup"
      ],
      "excludes": [
        "*.go",
        "foo/**/bar"
      ],
      "password": "correct horse battery staple",
      "repository": "/path/to/repo",
      "aws_access_key": "...",
      "aws_secret_key": "...",
      "b2_account_id": "...",
      "b2_account_key": "...",
      "azure_account_name": "...",
      "azure_account_key": "...",
      "google_project_id": "...",
      "google_application_credentials": "...",
      "hooks": {
        "pre-repo": [
          "some-shell-commands"
        ],
        "post_repo": [
          // ...
        ],
        "pre-<COMMAND>": [
          // ...
        ],
        "post_<COMMAND>": [
          // ...
        ]
      }
    },
    "my_other_profile": {
      // ...
    },
    ...
  }
}
```

 - `restic_path` _(string, optional, default: which(restic))_: Path to the
   `restic` executable. If not specified it will look up the path in the
   `PATH`.

 - `default_profile` _(string, optional):_ The name of the profile that will be
   used when no profile name is specified through the `--profile` argument.  
   Multiple profile names can be specified as a comma-separated list (without
   spaces). If multiple profile names are provided they will be merged into
   each other in the order they are specified. This can be useful when
   combining partial profiles.

 - `global` _(object, optional)_: A global profile that will be merged into
   all other profiles. If the non-global profile contains the same options the
   global options will be overridden by the profile. Except `files` and
   `excludes` will be combined.

 - `profiles.[NAME].initialize` _(boolean, optional, default: false)_: If true,
   it will automatically initialize an uninitialized repository.

 - `profiles.[NAME].json` _(boolean, optional, default: false)_: Calls restic
   with the `--json` argument.

 - `profiles.[NAME].no_lock` _(boolean, optional, default: false)_: Calls restic
   with the `--no-lock` argument.

 - `profiles.[NAME].quiet` _(boolean, optional, default: false)_: Calls restic
   with the `--quiet` argument.

 - `profile.[NAME].files` _(array, required)_: A list of paths to files and or
   directories that will be backed up.

 - `profile.[NAME].excludes` _(array, optional)_: A list of file patterns that
   will be excluded from the backup.  
   Note that this only applies to the `backup` command. Exclude patterns for
   the `restore` command must be provided through the `--exclude` and
   `--include` arguments.

 - `profile.[NAME].password` _(string, required)_: The password that will be
   used to encrypt and sign the backup.

 - `profile.[NAME].repository` _(string, required)_: The repository path for
   the backup. Read the [restic docs][restic-init] to see how to format the
   repository path for your storage backend.

 - `profile.[NAME].aws_access_key` _(string, optional)_: S3 access key. Used
   only when hosting the repository on S3.
 - `profile.[NAME].aws_secret_key` _(string, optional)_: S3 secret key. Used
   only when hosting the repository on S3.

 - `profile.[NAME].b2_account_id` _(string, optional)_: Backblaze B2 account
   ID. Used only when hosting the repository on Backblaze B2.
 - `profile.[NAME].b2_account_key` _(string, optional)_: Backblaze B2 access
   key. Used only when hosting the repository on Backblaze B2.

 - `profile.[NAME].azure_account_name` _(string, optional)_: Microsoft Azure
   account name. Used only when hosting the repository on Microsoft Azure.
 - `profile.[NAME].azure_account_key` _(string, optional)_: Microsoft Azure
   account key. Used only when hosting the repository on Microsoft Azure.

 - `profile.[NAME].google_project_id` _(string, optional)_: Google Cloud
   Storage project ID. Used only when hosting the repository on Google Cloud
   Storage.
 - `profile.[NAME].google_application_credentials` _(string, optional)_: File
   path to Google Cloud Storage application credentials file. Used only when
   hosting the repository on Google Cloud Storage.

 - `profile.[NAME].hooks.pre-repo` _(array of strings, optional)_: An array of
   shell commands that will be executed sequentially and in order before each
   restic command that accesses the repo. If one of the shell commands fails
   (i.e. exits with a non-zero exit code) all following commands including the
   restic command will not run and the program will exit.

 - `profile.[NAME].hooks.post_repo` _(array of strings, optional)_: An array of
   shell commands that will be executed sequentially and in order after each
   restic command that accesses the repo. If one of the shell commands fails
   (i.e. exits with a non-zero exit code) all following commands will not run
   and the program will exit.

 - `profile.[NAME].hooks.pre-[COMMAND]` _(array of strings, optional)_: An
   array of shell commands that will be executed sequentially and in order
   before each restic `[COMMAND]` command. If one of the shell commands fails
   (i.e. exits with a non-zero exit code) all following commands including the
   restic command will not run and the program will exit.

 - `profile.[NAME].hooks.post_[COMMAND]` _(array of strings, optional)_: An
   array of shell commands that will be executed sequentially and in order
   after each restic `COMMAND` command. If one of the shell commands fails
   (i.e. exits with a non-zero exit code) all following commands will not run
   and the program will exit.

### About Hooks

Hooks can be used to do stuff before and after the repo is accessed, or before
and after a specific command is executed. For example, a USB drive could be
mounted in the `pre-repo` hook and then unmounted in the `post_repo` hook.

Each hook is executed in a separate shell and has access to all environment
variables including the ones passed to restic. Hooks are executed in the
following order:

 - `pre-repo`
 - `pre-[COMMAND]` (unless pre-repo failed)
 - _call to restic_ (unless pre-[COMMAND] failed)
 - `post_[COMMAND]` (unless the restic command failed)
 - `post_repo` (unless post_[COMMAND] failed)

So in case of `restique backup` it would call `pre-repo`, `pre-backup`, `restic
backup`, `post_backup` and finally `post_repo`.

## Examples

### Simple Local Backup

**Config:**
```js
{
  "default_profile": "home",
  "profiles": {
    "home": {
      "repository": "/mnt/my_external_drive/backups",
      "password": "correct horse battery staple",
      "files": [
        "/home"
      ],
      "excludes": [
        "pr0n/**/*.mp4"
      ]
    }
  }
}
```

**Initialize:**
```sh
restique init
```

**Backup:**
```sh
restique backup
```

**Integrity check:**
```sh
restique check
```

**Restore:**
```sh
restique restore latest --target /tmp/home-restored
```

### Backing Up Docker Images to Backblaze

**Config:**
```js
{
  "default_profile": "dockerimages",
  "profiles": {
    "dockerimages": {
      "repository": "b2:mydockerbackups:/images",
      "b2_account_id": "1a2345b67890",
      "b2_account_key": "1234a5678b901c3d45678ef901g2h34567i89jklmn",
      "password": "correct horse battery staple"
    }
  }
}
```

**Initialize:**
```sh
restique init
```

**Export and backup the busybox docker image:**
```sh
docker save busybox | restique backup --stdin --stdin-name busybox.tar
```

**List the contents of the latest snapshot:**
```sh
restique ls latest
```
Output:
```
snapshot fb120820 of [busybox.tar] at 2017-10-01 20:30:03.222656757 +0200 CEST):
/busybox.tar
```

**Restore the docker image:**
```sh
restique restore latest --target /tmp/ --include busybox.tar
```

```sh
docker load < /tmp/busybox.tar
```

### Combining Partial Profiles

Here we are going to create four partial profiles. Two of them contain
information about different backups that we want to make, and the other two
contain information about two different repositories where we want to store our
backups. By combining one of the former profiles with one of the latter we can
save the same backup on different repositories.

**Config:**
```js
{
  "global": {
    "password": "correct horse battery staple"
  },
  "profiles": {
    "personal": {
      "files": [ "/home/user" ],
      "excludes": [ "/home/user/work" ]
    },
    "work": {
      "files": [ "/home/user/work" ]
    },
    "local": {
      "repository": "/mnt/my_external_drive/backups"
    },
    "remote": {
      "repository": "s3:s3.amazonaws.com/my_backups_bucket",
      "aws_access_key": "AAABBB999CCC666UU000",
      "aws_secret_key": "aaaa/BBBbBbBBbbbbBBBBBbBbBB/CCCcCcccCCCC"
    }
  }
}
```

**Initialize S3 repository:**
```sh
restique -p remote init
```

**Initialize local repository:**
```sh
restique -p local init
```

**Backup personal files to S3:**
```sh
restique -p personal,remote backup
```

**Backup personal files locally:**
```sh
restique -p personal,local backup
```

**Backup work files to S3:**
```sh
restique -p work,remote backup
```

**Backup work files locally:**
```sh
restique -p work,local backup
```

**Restore a snapshot from the S3 repository:**
```sh
restique -p remote restore e61c4ad7 --target /tmp/work-restored
```

**Restore a snapshot from the local repository:**
```sh
restique -p local restore 0eb99523 --target /tmp/personal-restored
```

### Run Only if External Drive is Mounted

**Config:**
```js
{
  "default_profile": "home",
  "profiles": {
    "home": {
      "repository": "/mnt/my_external_drive/backups",
      "password": "correct horse battery staple",
      "files": [
        "/home"
      ],
      "pre-repo": [
        "grep -qs '/mnt/my_external_drive/backups' /proc/mounts"
      ]
    }
  }
}
```

**Try backup:**

```sh
restique backup
```

Output:
```
ERROR: Command 'grep -qs '/mnt/my_external_drive/backups' /proc/mounts' returned non-zero exit status 1.
ERROR: One or more 'pre-repo' hooks failed.
```

## License

Copyright (c) 2017 Max Kueng

[MIT License][license]

[restic]: https://github.com/restic/restic
[restic-install]: http://restic.readthedocs.io/en/latest/installation.html
[restic-init]: http://restic.readthedocs.io/en/latest/manual.html#initialize-a-repository
[restic-manual]: http://restic.readthedocs.io/en/latest/manual.html
[license]: ./LICENSE
