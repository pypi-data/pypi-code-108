from time import sleep

try:  # noqa: C901
    import os
    import re

    from polidoro_argument import Command
    from github import Github

    from polidoro_cli import CLI

    class GitHub(object):
        @staticmethod
        @Command
        def monitor_workflow():
            gh = Github(os.environ['GITHUB_TOKEN'])
            out, _ = CLI.execute('git config --get remote.origin.url', capture_output=True, show_cmd=False)
            repo_name = re.search(r'github.com[:/](?P<repo>.*)\.git', out).groupdict()['repo']
            repo = gh.get_repo(repo_name)
            # table = Table()
            while True:
                for wf in repo.get_workflows():
                    wfrs = wf.get_runs()
                    print(wf.name, end='\t->\t')
                    if list(wfrs):
                        wfr = wfrs[0]
                        info = wfr.conclusion if wfr.conclusion else wfr.status
                        print(info, end='')
                    print()
                print('------------------------')
                sleep(0.1)
            # print(remote_origin.replace('git@github.com:', '').strip())
except ModuleNotFoundError as error:
    if error.name != 'github':
        raise
