

import sys
import time
import traceback
import argparse
import os

from kabaret.app.session import KabaretSession

from .jobs_actor import Jobs


class JobsNodeSession(KabaretSession):

    def __init__(self, pool_names, *args, **kwargs):
        self.jobs_actor = None
        self.pool_names = pool_names
        self.queues = []
        self._current_job = None
        super(JobsNodeSession, self).__init__(*args, **kwargs)

    def _create_actors(self):
        super(JobsNodeSession, self)._create_actors()
        self.jobs_actor = Jobs(self)

    # def do_flow_job(self, oid, interpretor=None):
    #     #print 'Faking exection 5sec for oid={!r}'.format(oid)
    #     #time.sleep(5)
    #     print 'Spawning Worker to execute on oid={!r}'.format(oid)
    #     try:
    #         #self.cmds.Flow.call(oid, 'execute', (), {})
    #         popen = self.cmds.Jobs.node_spawn_flow_worker()
    #     except:
    #         traceback.print_exc()
    #         print 'Oops :/'
    #         raise

    # def _process_job(self, job):
    #     print 'Got job:', job.to_dict()
    #     job_type = job.get_job_type()
    #     if job_type == 'NODE_CMD':
    #         params = job.get_job_params()
    #         print ' ---> node cmd:', params
    #         args, kwargs = params
    #         self._current_job = job
    #         try:
    #             self.do_node_control_job(*args, **kwargs)
    #         except:
    #             traceback.print_exc()
    #         else:
    #             print 'Command done'
    #             job.set_done()
    #         finally:
    #             self._current_job = None

    #     elif job_type == 'flow':
    #         params = job.get_job_params()
    #         print ' ---> Params:', params
    #         args, kwargs = params
    #         try:
    #             self.do_flow_job(*args, **kwargs)
    #         except:
    #             traceback.print_exc()
    #         else:
    #             print 'Marking job done'
    #             job.set_done()

    def wait_for_jobs(self):
        node_id = self.session_uid()
        working_job_popen = None

        self.log_info('Jobs Node {} started...'.format(self.session_uid()))

        while not self.jobs_actor.node_stopped():
            self.tick()

            self.log_debug('{}:: waiting for control jobs...'.format(self.session_uid()))
            control_job = self.jobs_actor.poll_control(node_id)
            if control_job is not None:
                #self._process_job(control_job)
                self.log_info('{}:: received control job {} with command {}'.format(
                    self.session_uid(),
                    control_job.jid(),
                    control_job.get_job_params()[1].get('cmd', None)))
                self.jobs_actor.node_execute_job(control_job)

            self.tick()

            if working_job_popen is not None:
                retcode = working_job_popen.poll()
                if retcode is not None:
                    # process ended
                    working_job_popen = None

            if working_job_popen is None:
                self.log_debug('{}:: waiting for jobs...'.format(self.session_uid()))
                job = self.jobs_actor.poll_pools(self.pool_names, node_id)
                if job is not None:
                    #self._process_job(job)
                    working_job_popen = self.jobs_actor.node_execute_job(job)
                    self.log_info('Jobs Node worker started. PID: {}'.format(working_job_popen.pid))
            
            else:
                self.log_debug('Jobs Node worker in progress. PID: {}'.format(working_job_popen.pid))

            time.sleep(1)


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-r', '--root_dir', dest='root_dir'
    )
    values, remaining_args = parser.parse_known_args(args)

    if values.root_dir:
        os.environ["ROOT_DIR"] = values.root_dir
    
    return remaining_args


if __name__ == '__main__':
    argv = sys.argv[1:]  # get ride of first args wich is script filename
    session_name, host, port, cluster_name, db, password, debug, remaining_args \
        = JobsNodeSession.parse_command_line_args(argv)
    pools = process_remaining_args(remaining_args)
    if not pools:
        print('\n!!!\nUsage:', sys.argv[0], 'pool_name pool_name ...\n\n')
    else:
        node = JobsNodeSession(pools, session_name=session_name, debug=debug)
        node.cmds.Cluster.connect(host, port, cluster_name, db, password)

        node.wait_for_jobs()
        print('Jobs Node closed.')
        
