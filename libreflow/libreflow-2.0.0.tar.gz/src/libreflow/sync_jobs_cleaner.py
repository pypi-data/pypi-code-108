import sys
import time
import datetime
import argparse

from kabaret.app.session import KabaretSession
from kabaret.app.actors.flow import Flow


class CleanSyncJobsSession(KabaretSession):

    def _create_actors(self):
        Flow(self)
    
    def clear_jobs(self, project_name, clear_every=900, clear_before=1800):
        clear_action_oid = f'/{project_name}/admin/multisites/working_sites/clear_site_queues'

        try:
            while True:
                self.log_info('Clearing jobs (%s)...' % datetime.datetime.fromtimestamp(time.time()))
                self.cmds.Flow.set_value(oid=clear_action_oid+'/emitted_since', value=clear_before)
                self.cmds.Flow.run_action(oid=clear_action_oid, button='Clear')
                time.sleep(clear_every)

        except KeyboardInterrupt:
            self.log_info('Cleaner stopped. Exiting...')
            return


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-p', '--clear-period', default=900, dest='period'
    )
    parser.add_argument(
        '-t', '--elapsed-time', default=1800, dest='time'
    )
    values, remaining_args = parser.parse_known_args(args)
    
    return (float(values.period), float(values.time), remaining_args)


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        remaining_args,
    ) = CleanSyncJobsSession.parse_command_line_args(argv)

    session = CleanSyncJobsSession(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    (
        period,
        time,
        remaining_args
    ) = process_remaining_args(remaining_args)

    if remaining_args:
        project_name = remaining_args[0]
    else:
        project_name = 'siren'

    # Check project existence
    if not session.cmds.Flow.exists('/'+project_name):
        session.log_error(
            f'No project /{project_name} found on this cluster. ' \
            'Please specify an existing project name.'
        )
        return

    # Check project root type
    project_type_name = session.get_actor('Flow').get_project_qualified_type_name(project_name)

    if project_type_name != 'libreflow.thesiren.flow.Project':
        session.log_error(
            f'Project root must be of type {project_type_name}, which this session is configured for.' \
            'Please specify a project with the valid root type.'
        )
        return

    session.clear_jobs(project_name, clear_every=period, clear_before=time)


if __name__ == "__main__":
    main(sys.argv[1:])