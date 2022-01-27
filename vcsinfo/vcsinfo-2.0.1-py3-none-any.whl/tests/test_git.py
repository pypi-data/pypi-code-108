"""
Copyright 2021 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in accordance
with the terms of the Adobe license agreement accompanying it.
"""

import os
import shutil
import tempfile

import pytest

from vcsinfo import detect_vcs


# Since we cannot have a git repo checked into another repo, instead use a git repo that was previously
# created and the .git folder renamed and then move it to another location and rename the .git folder
REPO_DIR = os.path.join(os.path.dirname(__file__), 'repos/git-repo')


@pytest.fixture(name='git_repo_path')
def fixture_git_repo_path():
    with tempfile.TemporaryDirectory(suffix='-test-vcsinfo-git') as temp_dir:
        git_repo_path = os.path.join(temp_dir, 'git-repo')
        shutil.copytree(REPO_DIR, git_repo_path)
        shutil.move(os.path.join(git_repo_path, 'dotgit'), os.path.join(git_repo_path, '.git'))
        yield git_repo_path


def test_git_repo(git_repo_path):
    result = detect_vcs(git_repo_path)
    assert result
    assert result.vcs == 'git'
    assert str(result) == f'VCSGit({git_repo_path})'
    assert result.id == 'a23bf7e941d6edf95ec1ba3dc2e4999a544c6b5d'
    # Comes from the origin repo
    assert result.name == 'vcsinfo-test-git'
    assert result.branch == 'main'
    assert result.id_short == 'a23bf7'
    assert result.id_string == f'main-2.Ia23bf7.M{result.modified}'
    assert result.modified != 0
    assert result.number == 2
    assert result.release == f'2.Ia23bf7.M{result.modified}'
    assert result.source_root == git_repo_path
    assert result.upstream_repo == 'git@github.com:adobe/vcsinfo-test-git-upstream.git'
    assert result.user == 'saville'
    assert result.list_files() == ['hello', 'hello2', 'hello3']
    assert result.info() == {
        'type': 'git',
        'upstream_repo': 'git@github.com:adobe/vcsinfo-test-git-upstream.git',
        'name': 'vcsinfo-test-git',
        'branch': 'main',
        'id': 'a23bf7e941d6edf95ec1ba3dc2e4999a544c6b5d',
        'id_short': 'a23bf7',
        'id_string': f'main-2.Ia23bf7.M{result.modified}',
        'number': 2,
        'user': 'saville',
        'release': f'2.Ia23bf7.M{result.modified}',
    }
    assert result.info(include_files=True)['files'] == ['hello', 'hello2', 'hello3']
    assert result.status() == [
        ['hello'], ['hello3'], [], [], [], [], ['hello2']
    ]
