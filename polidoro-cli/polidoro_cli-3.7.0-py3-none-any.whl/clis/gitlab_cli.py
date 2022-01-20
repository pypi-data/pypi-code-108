try:  # noqa: C901
    import os
    from datetime import timedelta
    from time import sleep

    import polidoro_terminal
    from polidoro_argument import Command
    from polidoro_gitlab import GitLab as PolidoroGitLab
    from polidoro_gitlab import Project
    from polidoro_table import Table, Property
    from polidoro_terminal import Color, Format, cursor

    from polidoro_cli import CLI

    def sort_jobs(j):
        if j.status == 'failed':
            return 9
        for value, status in enumerate(['running', 'pending', 'created', 'success']):
            if status == j.status:
                return value
        return 8

    class GitLab:
        @staticmethod
        @Command
        def monitor(*args):
            pipeline_id = None
            if args:
                pipeline_id = args[0]
            t2 = None
            pipeline = None
            try:
                cursor.hide()
                gl = PolidoroGitLab('https://gitlab.buser.com.br/', private_token=os.environ.get('PRIVATE_TOKEN', ''))
                project = GitLab.get_project(gl)
                if pipeline_id:
                    pipeline = project.get_pipeline(pipeline_id)
                else:
                    pipeline = GitLab.get_pipeline(project)

                def paint(text, color):
                    return f'{color}{text}{Format.NORMAL}'

                def status_color(status):
                    return dict(
                        success=Format.BOLD + Color.GREEN,
                        running=Color.CYAN + Format.BLINK,
                        failed=Format.BOLD + Color.LIGHT_RED,
                        pending=Color.YELLOW,
                        others=Format.DIM,
                    ).get(status, '')
                properties = [
                    Property(format=status_color('others'), condition='C("status") in ["skipped", "manual", "created"]'),
                    Property(format=status_color('success'), condition='C("status") == "success"'),
                    Property(format=status_color('failed'), condition='C("status") == "failed"'),
                    Property(format=status_color('pending'), condition='C("status") == "pending"'),
                    Property(format=status_color('running') - Format.BLINK, condition='C("status") == "running"'),
                ]
                stop = False
                t2 = None
                while not stop:
                    t1 = Table(f'{pipeline.ref} (#{pipeline.id}) - '
                               f'{paint(pipeline.status, status_color(pipeline.status))} - '
                               f'{pipeline.web_url}')
                    t1.add_columns(['name', 'status', 'queue', 'time', 'url'])
                    jobs = list(filter(lambda _j: _j.status == 'pending', project.jobs.list()))

                    stop = True
                    pipe_jobs = pipeline.get_jobs()
                    for j in sorted(pipe_jobs, key=sort_jobs):
                        pos = '-'
                        if j in jobs:
                            pos = jobs.index(j)

                        row = [j.name, j.status, pos]
                        if j.duration:
                            row.append(timedelta(seconds=int(j.duration)))
                        else:
                            row.append('-')
                        row.append(j.web_url)
                        if j.status in ['running', 'pending']:
                            stop = False
                        t1.add_row(row, properties=properties)
                    if stop:
                        stop = pipeline.status not in ['running', 'pending']
                        pipeline.refresh()
                    t1.print()
                    t1.return_table_lines()
                    t2 = t1
                    sleep(0.5)
            except KeyboardInterrupt:
                polidoro_terminal.clear_to_end_of_line()
                print()
            finally:
                if t2 and pipeline:
                    t2.print()
                    icon = 'dialog-ok' if pipeline.status == 'success' else 'error'
                    CLI.execute(f'notify-send -i {icon} "Pipeline #{pipeline.id} finished"', show_cmd=False)
                if cursor:
                    cursor.show()

        @staticmethod
        def get_pipeline(project):
            # return project.get_pipelines()[0]
            branch, _ = CLI.execute('git rev-parse --abbrev-ref HEAD', capture_output=True, show_cmd=False)
            last_commit = project.commits.list(ref_name=branch.strip())[0]
            return project.get_pipeline(sha=last_commit.id)[0]

        @staticmethod
        def get_project(rest):
            out, _ = CLI.execute('git config --get remote.origin.url', capture_output=True, show_cmd=False)
            project_name = out.split('/')[-1].replace('.git', '').strip()
            projects = rest.projects.list(search=project_name)
            for p in projects:
                if p.name == project_name:
                    return Project(p)
except ModuleNotFoundError:
    raise
