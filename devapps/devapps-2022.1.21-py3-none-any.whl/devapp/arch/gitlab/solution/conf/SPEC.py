#!/usr/bin/env python
# coding: utf-8

import os
import sys

from tree_builder import *

gitl_url = 'https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64'
hugo_url = 'https://github.com/gohugoio/hugo/releases/download/v0.59.0/hugo_0.59.0_Linux-64bit.tar.gz'
plnt_url = 'https://netcologne.dl.sourceforge.net/project/plantuml/plantuml.jar'


class Ports:
    gitlab = Env('DA_PORT_GITLAB', 5378)


class Project(T):
    'Gitlab'


class Service(T):
    runtime = 'systemd'
    service_restart_sec = 2


build_type_hirarchy(root=Project)


class GitlabRunner(Service):
    hugo_dir = Env('DA_DIR') + '/hugo'
    themes_dir = hugo_dir + '/themes'
    filesystem = [
        {
            'name': 'gitlab',
            'type': 'conda_env',
            'packages': ['python', 'java-1.7.0-openjdk-devel-cos6-x86_64'],
        },
        {'name': 'gitlab_runner', 'type': 'exe', 'url': gitl_url, 'fs_method': 'cp',},
        {
            'name': 'https://github.com/matcornic/hugo-theme-learn.git',
            'checkout_dir': themes_dir + '/hugo-theme-learn',
        },
        {
            'name': 'hugo',
            'type': 'exe',
            'url': hugo_url,
            'fs_method': 'cp',
            'checkout_dir': hugo_dir,
            'checkout_have_check_dir': hugo_dir + '/bin',
        },
        {
            'name': 'plantuml.jar',
            'type': 'lib',
            'url': plnt_url,
            'fs_method': 'cp',
            'checkout_dir': hugo_dir + '/lib',
        },
    ]
    CONFIG_FILE = '%(etc_dir)s/runner.toml'
    descr = 'devapps'
    tags = ['devapps', 'production']
    app = 'gitlab_runner'
    app_args = ['run']
    # shortcut for:
    # service_exec_start = [app, 'run'] + _cfg
    service_kill_mode = 'process'
    url = 'https://gitlab.my_company.com'
    java = '%(DA_DIR)s/envs/gitlab/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.131.x86_64/bin/java'

    # token = 'mFsHPcAsRKhpsnstXMVV'

    functions = {
        'java': [java],
        'plantuml': [java, '-jar', hugo_dir + '/lib/plantuml.jar', '-tsvg'],
        'plantrender': ['%(DA_DIR)s/conf/SPEC.py', 'render_plantuml'],
        'register': [
            app,
            'register',
            '--non-interactive',
            '--url',
            url,
            '--registration-token',
            Env(
                'registration_token',
                suggest=[
                    Env('HOME') + '/.config/devapps/creds',
                    'gitlab_runner_reg_token',
                ],
            ),
            '--executor',
            'shell',
            '--description',
            descr,
            '--tag-list',
            ','.join(tags),
            '--locked',
            'false',
        ],
        'unregister': [app, 'unregister', '--all-runners'],
    }
    service_exec_start_pre = 'register'
    # service_exec_stop_post_1 = 'unregister'


class Gitlab(Project, GitlabRunner):
    ''


root = create_tree(Gitlab)


args = sys.argv


def render_plantuml(dir_):
    """
    Replacing `` `plantuml fenced blocks with rendered svgs, inline

    - Intended to be run before hugo generating gitlab pages (i.e. within .gitlab-ci.yml)
    - Requires plantuml
    - Run via e.g. $app_run_script_path plantrender /home/gk/repos/axwifi-server/docs/content/
    - To be replaced with a rmarkdown function, once we have R-Merkdown
    """

    def repl(fn):
        with open(fn) as fd:
            s = fd.read()
        arsp = os.environ['app_run_script_path']
        parts = s.split('\n```plantuml\n')
        print('Replacing %s plantumls within %s' % (len(parts) - 1, fn))
        r = parts[0]
        for part in parts[1:]:
            uml, rest = part.split('\n```\n', 1)
            cmd = "echo '%s' | '%s' plantuml -tsvg -p " % (uml, arsp)
            svg = os.popen(cmd).read().split('<svg', 1)[1]
            svg, src = svg.split('<!--', 1)
            src = src.split('@startuml', 1)[1].split('@enduml', 1)[0]
            uml = '<svg%s</g></svg>' % svg
            r += '<div style="background: #eeeeFF">%s</div>' % uml
            r += (
                '<details><summary>Source</summary>\n\n```uml\n@startuml\n%s\n@enduml\n```\n</details>\n%s'
                % (src, rest)
            )
        with open(fn, 'w') as fd:
            fd.write(r)

    os.chdir(dir_)
    mds = set(
        [f.split(':', 1)[0] for f in os.popen('grep -ir plantuml').read().splitlines()]
    )
    [repl(f) for f in mds]


if __name__ == '__main__':
    if args[1] == 'render_plantuml':
        sys.exit(render_plantuml(args[2]))

    from tree_builder.links import dump_all

    print(dump_all(root, fmt='json'))
