from __future__ import print_function

import six
import os
import tempfile

from kabaret import flow

from . import jobs_flow

def make_default_temp_dir():
    '''
    Just a tool to have a kool default log path for the demo.
    Windows user have complicated tempdir, so Imake it shorter.
    '''
    fullpath = tempfile.gettempdir()
    drive, path = os.path.splitdrive(fullpath)
    if drive:
        fullpath = drive+os.path.sep

    return os.path.join(fullpath, 'KABARET_JOBS_DEMO')



class TaskJob(jobs_flow.Job):

    _task = flow.Parent(2)

    with flow.group('Task Parameters'):
        param_01 = flow.Param().ui(editable=False)
        param_02 = flow.Param().ui(editable=False)

    def get_log_filename(self):
        return os.path.join(self.root().project().log_path.get(), self._task.name(), self.name()+'.job_log')

    def _do_job(self):
        print('############# JOBS DEMO - TaskJob Starts #############')
        self._task.status.set('WIP')
        import time
        count = 5
        for i in range(count):
            self.set_progress(i, count, 'Working hard {}'.format(i))
            time.sleep(1)
        self._task.status.set('DONE')
        self.set_progress(count, count, 'Everything is Done !')
        print('############# JOBS DEMO - TaskJob Ends #############')
        

class SubmitTaskJobAction(jobs_flow.SubmitJobAction):

    with flow.group('Task Parameters'):
        job_param_01 = flow.Param()
        job_param_02 = flow.Param()

    sep = flow.Separator()

    def configure_job(self, job):
        job.param_01.set(self.job_param_01.get())
        job.param_02.set(self.job_param_02.get())

class TaskJobs(jobs_flow.Jobs):

    submit_job = flow.Child(SubmitTaskJobAction)

    @classmethod
    def job_type(cls):
        return TaskJob


class TaskStatusValue(flow.values.ChoiceValue):

    CHOICES = ('INV', 'WIP', 'DONE')

    @classmethod
    def default(cls):
        return cls.CHOICES[0]

class Task(flow.Object):

    status = flow.Param(TaskStatusValue.default(), TaskStatusValue)
    jobs = flow.Child(TaskJobs)

class CreateTaskAction(flow.Action):
    
    _tasks = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._tasks.create_new_task()

class Tasks(flow.Map):

    create_task = flow.Child(CreateTaskAction)

    @classmethod
    def mapped_type(cls):
        return Task

    def create_new_task(self):
        i = len(self)
        n = 'Task'+str(i).zfill(5)
        self.add(n)
        self.touch()

class JobsDemoFlow(flow.Object):

    log_path = flow.Param(make_default_temp_dir())
    exe = flow.Param('C:/Program Files/Sublime Text 3/sublime_text.exe')
    flags = flow.Param('')

    tasks = flow.Child(Tasks)

