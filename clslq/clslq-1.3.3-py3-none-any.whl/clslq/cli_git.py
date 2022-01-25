# -*- encoding: utf-8 -*-

import click
import os
"""git quick tools"""

_help = """
    GIT command quick tools: 

    push: Only commit changes to remote branches

    pushall: Add * and commit changes to remote branches

    pushtag: Add tag and commit changes to remote branches
    
"""

cm = {
    "first": ":tada:first commit",
    "new": ":new:new function",
    "tag": ":bookmark:add tags",
    "bug": ":bug:bug fixed",
    "ess": ":ambulance:essential bug fixed",
    "cfg": ":wrench:configure file fixed",
    "rock": ":rocket:function of deplay",
    "memo": ":memo:document updated",
    "fire": ":fire:huge modification",
    "heart": ":heart:green_heart building relations",
}


@click.option('--repo',
              '-r',
              default="origin",
              help='repository, default is origin')
@click.option('--branch',
              '-b',
              default="master",
              help='branch, default is master')
@click.option('--msg', '-m', default=cm['new'], help='commit message')
@click.option('--tagv', '-v', default="1.0.0", help='tag version')
@click.command(context_settings=dict(
    allow_extra_args=True,
    ignore_unknown_options=True,
),
               help=_help)
@click.argument('command', required=False)
def git(command, repo, branch, msg, tagv):
    click.secho("{:<10} : {}".format('[command]', command), fg='green')
    click.secho("{:<10} : {}".format('[repo]', repo), fg='green')
    click.secho("{:<10} : {}".format('[branch]', branch), fg='green')
    click.secho("{:<10} : {}".format('[msg]', msg), fg='green')
    click.secho("{:<10} : {}".format('[tagv]', tagv), fg='green')

    click.secho("Pull from git repository, default is origin master",
                fg='green')
    os.system("git pull {} {}".format(repo, branch))
    if command and 'push' in command:
        for k,v in cm.items():
            click.secho("{:<10} {}".format(k, v), fg='green')
        input = click.prompt('Select commit message', default=cm['new'])
        msg = cm[input]

    if 'push' == command:
        click.secho("Commit with message: {}".format(msg), fg='green')
        os.system("git commit -a -m \"{}\"".format(msg))
        os.system("git push")
        exit()
    if 'pushall' == command:
        click.secho("Add * and commit with message: {}".format(msg), fg='green')
        os.system("git add *")
        os.system("git commit -a -m \"{}\"".format(msg))
        os.system("git push")
        exit()

    if 'pushtag' == command:
        click.secho("Add tag and commit with message: {}".format(msg), fg='green')
        os.system("git add .")
        os.system("git commit -a -m \"publish on version %s\"" % tagv)
        os.system("git tag -a v{} -m \"add tag on {}\"".format(tagv, tagv))
        os.system("git push")
        os.system("git push origin --tags")
        exit()


    if command:
        click.secho("Unsupport command: {}".format(command), fg='red')