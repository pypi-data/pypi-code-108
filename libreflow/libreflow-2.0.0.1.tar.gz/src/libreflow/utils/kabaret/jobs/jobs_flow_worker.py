'''

    This module is a main script for the flow jobs.
    It instanciates a JobWorkerSession and exexutes the job pointed by the env-var "KABARET_JOBS_FLOW_OID"


'''

from __future__ import print_function

import sys
import os
import traceback

from kabaret.app.session import KabaretSession
import libreflow.utils.kabaret as kutils
from libreflow.utils.kabaret.jobs import jobs_actor
from libreflow.baseflow.runners import (
    Blender,
    AfterEffectsRender,
    SessionWorker,
    MarkSequenceRunner,
)

from libreflow.resources import file_templates
from libreflow.thesiren_resources import file_templates


def try_initialize_maya():
    try:
        import maya.standalone
    except ImportError:
        pass
    else:
        print('This looks like a maya pythong, let us initialize it.')
        try:
            maya.standalone.initialize()
        except:
            print('!!! Error initializing Maya:')
            traceback.print_exc()
            print('!!! Error initializing Maya.')
            sys.exit(-1)
        print('Maya initialization done.')


class JobsWorkerSession(KabaretSession):

    def __init__(self):
        super(JobsWorkerSession, self).__init__('JobsWorker')

        self.cmds.Cluster.connect_from_env()
        self.execute_job()

    def _create_actors(self):
        super(JobsWorkerSession, self)._create_actors()
        self.jobs_actor = jobs_actor.Jobs(self)
        
        subprocess_manager = kutils.subprocess_manager.SubprocessManager(self)

        factory = subprocess_manager.create_new_factory('JobsWorker Tools')
        factory.ensure_runner_type(Blender)
        factory.ensure_runner_type(AfterEffectsRender)
        factory.ensure_runner_type(MarkSequenceRunner)
        factory.ensure_runner_type(SessionWorker)

        subprocess_manager.ensure_factory(factory)

    def execute_job(self):
        self.jobs_actor.worker_execute_job()


if __name__ == '__main__':
    try_initialize_maya()
    JobsWorkerSession()