from __future__ import print_function

import time
import traceback

from kabaret import flow


class Job(flow.Object):
    ''' 
    This is the base class for Flow jobs.

    You must subclass it and implement:

        get_log_filename():
            Return the filename of the log file.
            (make it quick and stable !)

        _do_job(self):
            Do the job you need to do, periodically calling:
                self.set_progress()
                self.show_message()
                self.on_error()
            Use simple print call to write to the log file.
            
    You may subclass it and override:
        get_worker_interpreter() => to use another python (mayapy, hython, ...)
        get_worker_filename() => to use you own worker (if you're using custom actors in your flow)

    '''
    _jobs = flow.Parent()

    job_id = flow.Param(None).ui(editable=False)
    owner = flow.Computed()
    status = flow.Computed()
    created_on = flow.Computed()
    icon = flow.Computed()
    log_filename = flow.Computed()
    progress = flow.Param(0).ui(editor='percent', editable=False)
    message = flow.Param('').ui(editor='textarea', editable=False)

    def compute_child_value(self, child_value):
        if child_value is self.owner:
            self.owner.set(self.get_owner())
        elif child_value in (self.status, self.icon):
            self._compute_status_and_icon()
        elif child_value is self.created_on:
            self.created_on.set(self.get_created_on())
        elif child_value is self.log_filename:
            self.log_filename.set(self.get_log_filename())

    def touch(self):
        self.status.touch()
        self.icon.touch()
        self._jobs.touch()

    def get_job(self):
        return self.root().session().cmds.Jobs.get_job_info(self.job_id.get())

    def get_owner(self):
        return self.get_job().get('owner', '???')

    def get_created_on(self):
        return self.get_job().get('created_on', '???')

    def _compute_status_and_icon(self):
        job = self.get_job()
        self.status.set(job.get('status', '?!?'))
        self.icon.set(job.get('icon_ref', None))

    def get_log_filename(self):
        raise NotImplementedError('You must return the filename of the log file.')

    def get_worker_interpreter(self):
        '''
        Subclasses may override this to specify a arbitrary python interpreter to
        use to exectute the job.

        Default is to return None, which leads to using current interpretor.
        '''
        return None

    def get_worker_filename(self):
        '''
        Subclasses may override this to specify a arbitrary filename to
        use to as worker for the job.

        Default is to return None, which leads to using kabaret.jobs.jobs_flow_worker.
        '''
        return None

    def submit(self, pool, priority, label, creator, owner, paused, show_console):
        jid = self.root().session().cmds.Jobs.create_flow_job(
            oid=self.oid(),
            pool=pool,
            priority=priority,
            paused=paused,
            label=label,
            creator=creator,
            owner=owner,
            show_console=show_console,
            interpreter=self.get_worker_interpreter(),
            worker_filename=self.get_worker_filename(),
        )
        self.job_id.set(jid)

    def execute(self):
        print('----------------EXECUTING JOB', self.oid())
        self.touch()
        self.root().session().cmds.Jobs.set_job_in_progress(self.job_id.get())
        try:
            self._do_job()
        except Exception as err:
            self.on_error(traceback.format_exc())
        else:
            self.root().session().cmds.Jobs.set_job_done(self.job_id.get())
            self.status.touch()
            self.touch()
        finally:
            self.touch()

    def set_progress(self, step_index, step_count, step_message):
        percent = (step_index*100.0/step_count)
        self.progress.set(percent)
        print('[PROGRESS] {:.2f}%'.format(percent))
        message = '{}/{}: {}'.format(step_index, step_count, step_message)
        self.show_message(message)
        self.touch()

    def show_message(self, message):
        print(message)
        self.message.set(message)
        self.touch()

    def on_error(self, error_message):
        self.show_message('!!! ERROR: {}'.format(error_message))
        self.root().session().cmds.Jobs.set_job_error(self.job_id.get(), error_message)
        self.status.touch()
        self.touch()

    def _do_job(self):
        '''
        Override this to implement your job.
        (See constructor doc)
        '''
        raise NotImplementedError('You must implement the job to do here.')


class SubmitJobAction(flow.Action):

    _jobs = flow.Parent()

    with flow.group('Job Dispatch'):
        pool = flow.Param('Farm')
        priority = flow.IntParam(100)
        paused = flow.BoolParam(True)
        show_console = flow.BoolParam(True)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        return ['Submit', 'Submit and Open']

    def run(self, button):
        job = self._jobs.create_job()
        self.configure_job(job)
        self._jobs.touch()
        job.submit(
            self.pool.get(),
            self.priority.get(),
            self.paused.get(),
            self.show_console.get(),
        )

        if 'Open' in button:
            return self.get_result(goto=job.oid())
        return 

    def configure_job(self, job):
        pass

class Jobs(flow.Map):

    _next_id = flow.IntParam(0)

    @classmethod
    def job_type(cls):
        raise NotImplementedError('This should return your subclass of Job')

    @classmethod
    def mapped_type(cls):
        return cls.job_type()

    def mapped_names(self, *args, **kwargs):
        names = super(Jobs, self).mapped_names(*args, **kwargs)
        return reversed(names)

    def _get_next_job_id(self):
        self._next_id.incr()
        return self._next_id.get()

    def _get_job_prefix(self):
        return 'J'

    def create_job(self):
        name = '{}{:>05}'.format(self._get_job_prefix(), self._get_next_job_id())
        job = self.add(name)
        return job

    def columns(self):
        return ['Owner', 'Status', 'Created On']

    def _fill_row_cells(self, row, item):
        on = item.created_on.get()
        try:
            on = float(on)
        except:
            pass
        else:
            on = time.ctime(on)

        row.update(dict(
            Owner=item.owner.get(),
            Status=item.status.get(),
        ))
        row['Created On'] = on

    def _fill_row_style(self, style, item, row):
        style['icon'] = item.icon.get()
