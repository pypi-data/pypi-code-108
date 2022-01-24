import hashlib
import os

import git

import common
import coveragepy_parser

repo = git.Repo(os.getcwd())
master = repo.head.reference
commit = master.commit
commitHex = commit.hexsha


def merge_coverage(existing_file, source_file):
    target = existing_file['coverage']
    source = source_file['coverage']
    for index in range(0, len(source)):
        target[index] = source[index] if target[index] is None else target[index] + source[index]
    return target


def convert_coverage(data, report=None):
    if report:
        coveralls_files = report['source_files']
        coveralls_report = report
    else:
        coveralls_files = {}
        coveralls_report = {
            'repo_token': os.getenv('COVERALLS_REPO_TOKEN'),
            'service_name': 'local-ci'}
        head = {
            'id': commitHex,
            'author_name': commit.author.name,
            'author_email': commit.author.email,
            'committer_name': commit.committer.name,
            'committer_email': commit.committer.email,
            'message': commit.message
        }
        remotes = list(map(lambda remote: {'name': remote.name, 'url': remote.url}, repo.remotes))
        git_repo = {
            'head': head,
            'branch': repo.active_branch.name,
            'remotes': remotes
        }
        coveralls_report['git'] = git_repo
        coveralls_report['source_files'] = []
    source_files = coveralls_report['source_files']
    for file_name in data['files']:
        if common.valid(file_name):
            file_object = data['files'][file_name]
            text_file = open(file_name, "r")
            file_content_bytes = text_file.read().encode('utf-8')
            total_lines = coveragepy_parser.total_lines(file_object) + 2
            line_coverage = [None] * total_lines
            executed_lines = file_object['executed_lines']
            for entry in executed_lines:
                line_coverage[entry - 1] = 1
            missing_lines = file_object['missing_lines']
            for entry in missing_lines:
                line_coverage[entry - 1] = 0
            source_file = {
                'name': file_name,
                'source_digest': hashlib.md5(file_content_bytes).hexdigest(),
                'coverage': line_coverage,
            }
            filter_result = list(filter(lambda file: file['name'] == file_name, coveralls_files))
            existing_file = filter_result[0] if len(filter_result) > 0 else None
            if existing_file is None:
                source_files.append(source_file)
            else:
                existing_file['coverage'] = merge_coverage(existing_file, source_file)

    return coveralls_report
