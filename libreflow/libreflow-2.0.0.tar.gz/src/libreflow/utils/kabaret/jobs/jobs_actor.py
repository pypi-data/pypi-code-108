
from __future__ import print_function

import six
import os
import sys
import uuid
import time
import contextlib
import json
import getpass
import subprocess
import platform
import traceback

from kabaret.app._actor import Actor, Cmd, Cmds



#------ CMDS

class JobsCmds(Cmds):
    '''
    The Jobs actor manages a list of jobs and associated pool queues.
    blah blah...
    blah blah...
    blah blah documentation is awesome...
    blah blah...
    blah blah...
    '''

@JobsCmds.cmd
class Create_Flow_Job(Cmd):
    '''
    Create a Job that will execute an kabaret.flow.Object
    (the job<->object interface is still TBD)
    '''
    def _decode(
        self, 
        oid, pool, priority=100, paused=True,
        label=None, creator=None, owner=None,
        show_console=None,
        interpreter=None,
        worker_filename=None,
    ):
        self._oid = oid
        self._pool = pool
        self._priority = priority
        self._paused = paused
        self._label = label
        self._creator = creator
        self._owner = owner
        self._show_console = show_console
        self._interpreter = interpreter
        self._worker_filename = worker_filename

    def _execute(self):
        kwargs = {'oid':self._oid}
        if not self._show_console:
            kwargs['show_console'] = self._show_console
        if self._interpreter is not None:
            kwargs['interpreter'] = self._interpreter
        if self._worker_filename is not None:
            kwargs['worker_filename'] = self._worker_filename
        
        params = ((),kwargs)

        job = self.actor().create_job(
            'flow', self._label, self._creator, self._owner, params, self._pool, self._priority, self._paused,
        )
        return job.jid()

@JobsCmds.cmd
class Create_Job(Cmd):
    '''
    Create a Job in the given pool, with the given priority, with the given
    paused state, of the given job type and with the optionally given args and kwargs.
    '''
    def _decode(self, pool, priority, paused, job_type, *job_args, **job_kwargs):
        self._oid = oid
        self._pool = pool
        self._priority = priority
        self._paused = paused
        self._args = job_args
        self._kwargs = job_kwargs

    def _execute(self):
        job = self.actor().create_job(
            'flow', (self._args, self._kwargs), self._pool, self._priority, self._paused
        )
        return job.jid()

@JobsCmds.cmd
class Stop_Node(Cmd):
    '''
    Create a Job that will stop the Node picking it.
    If node_id is a pool name, the first Node in that poll will be stoped.
    If node_id is the exact identifier of an existing Node, this Node will
    pick the job and stop itself.
    '''
    def _decode(self, node_id, priority=100):
        self._node_id = node_id
        self._priority = priority

    def _execute(self):
        params = ((),dict(cmd='stop'))
        job = self.actor().create_job(
            'NODE_CMD', params, self._node_id, self._priority, False
        )  
        return job.jid()

@JobsCmds.cmd
class Kill_Node_Job(Cmd):
    '''
    Create a Job that will kill the current job of the Node picking it.
    If node_id is a pool name, the first Node in that poll will kill its job.
    If node_id is the exact identifier of an existing Node, this Node will
    pick the job and kill its job.

    If the Node picking the job has no current running job, the job will
    be ignored but still marked as Done.
    '''

    def _decode(self, node_id, priority=100):
        self._node_id = node_id
        self._priority = priority

    def _execute(self):
        params = ((),dict(cmd='kill_job'))
        job = self.actor().create_job(
            'NODE_CMD', params, self._node_id, self._priority, False
        )
        return job.jid()


@JobsCmds.cmd
class List_Jobs(Cmd):
    '''
    Returns a list of dicts describing all the known jobs.
    The dict keys are strings:
        jid         : uniq id of the job
        created_on  : timestamp float
        job_tye     : job type string
        job_label     : job label string
        jog_params  : (args_list, kwargs_dict) 
        pool        : pool name string
        paused      : pauded state bool
        priority    : priority int
        node        : node id of the Node executing or executed the job
        in_progress : bool
        done        : bool

    '''
    def _decode(self):
        pass

    def _execute(self):
        jobs = self.actor().get_all_jobs()
        return [j.to_dict() for j in jobs ]

@JobsCmds.cmd
class Get_Job_Info(Cmd):
    '''
    Returns a dict describing the job with the given job id.
    See list_jobs cmd for dict key list.
    '''
    def _decode(self, jid):
        self._jid = jid

    def _execute(self):
        try:
            job = self.actor().get_job(self._jid)
        except ValueError:
            return Job.UnknownJobDict(self._jid)
        else:
            return job.to_dict()

@JobsCmds.cmd
class Set_Job_Paused(Cmd):
    '''
    Changes the paused status of the job with the given id.
    '''
    def _decode(self, jid, paused=True):
        self._jid = jid
        self._paused = paused

    def _execute(self):
        job = self.actor().get_job(self._jid)
        job.set_paused(self._paused)

@JobsCmds.cmd
class Set_Job_Error(Cmd):
    '''
    Sets the job error status and message
    '''

    def _decode(self, jid, error_message):
        self._jid = jid
        self._error_message = error_message

    def _execute(self):
        try:
            job = self.actor().get_job(self._jid)
        except ValueError:
            return
        else:
            job.set_error(self._error_message)

@JobsCmds.cmd
class Set_Job_Done(Cmd):
    '''
    Mark the job as done.
    '''

    def _decode(self, jid):
        self._jid = jid

    def _execute(self):
        try:
            job = self.actor().get_job(self._jid)
        except ValueError:
            return
        else:
            job.set_done()

@JobsCmds.cmd
class Set_Job_In_Progress(Cmd):
    '''
    Mark the job as in progress.
    '''

    def _decode(self, jid):
        self._jid = jid

    def _execute(self):
        try:
            job = self.actor().get_job(self._jid)
        except ValueError:
            return
        else:
            job.set_in_progress()


@JobsCmds.cmd
class Delete_Job(Cmd):
    '''
    Deletes the job with the given id.
    If the job is in progress, the forced argument must be True
    for the job to be deleted.
    '''
    def _decode(self, jid, forced=False):
        self._jid = jid
        self._forced = forced

    def _execute(self):
        return self.actor().delete_job(self._jid, self._forced)


class Job(object):
    '''
    Job fields are stored in the <CLUSTER_NAME>:Jobs:jobs:<jid> hash.
    The list of jobs is stored in the <CLUSTER_NAME>:Jobs:job_ids set.

    If not paused at creation time, its jid is added to the <CLUSTER_NAME>:Jobs:pool_q:<pool_name> sorted set
    
    Unpausing a job adds it to the pool sorted set with its priority as score.
    Pausing a job removes it from the pool sorted set.

    The workers takes jid from their affected pool sorted set and alter the job's hash with infos.
    '''

    @classmethod
    def create(cls, actor, job_type, job_label, job_creator, job_owner, job_params, pool, priority, paused):
        if job_creator is None:
            job_creator = actor.get_current_login()
        if job_owner is None:
            job_owner = actor.get_current_login()

        # Create an entry in the job_ids set
        created = 0
        max_tries = 10
        tried = 0
        while not created:
            tried += 1
            jid = str(uuid.uuid4())
            created = actor._db.sadd(actor.jobids_set_name, jid)
            if tried > max_tries:
                raise Exception('Could not create a new job id !!!!')

        # Store the job in the jobs hash
        field_created = actor._db.hsetnx(actor.job_hashes_namespace+'/'+jid, 'created_on', time.time())
        if not field_created:
            raise Exception(
                'Error: looks like this job is already defined ({})!!! Aborting job definition.'.format(
                    actor.job_hashes_namespace+'/'+jid
                )
            )

        job = cls(actor, jid)
        job._send_touch = False
        job.set_job_creator(job_creator)
        job.set_job_owner(job_owner)
        job.set_job_type(job_type)
        job.set_job_label(job_label)
        job.set_job_params(job_params)
        job.set_pool(pool)
        job.set_priority(priority)
        job.set_paused(paused)
        job._send_touch = True
        actor.send_job_created(jid)

        return job

    @classmethod
    def delete(cls, actor, jid, forced):
        try:
            job = cls(actor, jid)
        except ValueError:
            print('WARNING: Job.delete(): job not found.')
            return False

        if job.get_in_progress() and not forced:
            return False

        job.remove_from_pool_queue()

        actor._db.srem(actor.jobids_set_name, jid)
        nb = actor._db.delete(actor.job_hashes_namespace+'/'+jid)
        if not nb:
            print('WARNING: Job.delete(): did not delete job hash :/')
        return bool(nb)

    @classmethod
    def UnknownJobDict(cls, jid):
        return dict(
            jid=jid,
            label='!!!',
            created_on=0,
            creator='!!!',
            owner='!!!',
            job_type='!!!',
            job_params=((),{}),
            pool='!!!',
            paused=False,
            priority=0,
            in_progress=False,
            done=False,
            status='Unknown',
            icon_ref=('icons.status', 'WARN'),
        )

    def __init__(self, actor, jid):
        super(Job, self).__init__()
        self._actor = actor
        self._jid = jid
        self._send_touch = True

        self.assert_exists()

    def assert_exists(self):
        actor = self._actor
        if not actor._db.exists(actor.job_hashes_namespace+'/'+self._jid):
            raise ValueError('This job does not exists: {}'.format(self._jid))

    @contextlib.contextmanager
    def after_touch(self):
        prev = self._send_touch
        self._send_touch = False
        try:
            yield
        finally:
            self._send_touch = prev
            self.touched()

    def _set_field(self, name, dumps_value):
        self._actor._db.hset(
            self._actor.job_hashes_namespace+'/'+self._jid,
            name,
            dumps_value
        )

    def _get_field(self, name):
        return self._actor._db.hget(
            self._actor.job_hashes_namespace+'/'+self._jid,
            name
        )

    def to_dict(self):
        d = self._actor._db.hgetall(
            self._actor.job_hashes_namespace+'/'+self._jid,
        )
        d['created_on'] = float(d['created_on'])
        d['paused'] = d.get('paused', '1') == '1'
        d['priority'] = int(d.get('priority',0))

        d['in_progress'] = bool(d.get('in_progress', ''))
        d['done'] = bool(d.get('done', ''))

        d['jid'] = self._jid
        status, icon_ref = self.get_status_and_icon()
        d['status'] = status
        d['icon_ref'] = icon_ref

        d['has_error'] = self.get_has_error()
        if d['has_error']:
            d['error_message'] = self.get_error()
        return d 

    def get_status_and_icon(self):
        status = ''
        if self.get_has_error():
            status = 'Warn'
        elif self.get_paused():
            status = 'Inv'
        elif self.get_in_progress():
            status = 'WIP'
        elif self.get_done():
            status = 'Done'
        else:
            status = 'Wait'
        return status, ('icons.status', status.upper())

    def touched(self):
        if self._send_touch:
            self._actor.send_job_touched(self._jid)

    def jid(self):
        return self._jid

    def set_job_creator(self, login):
        self._set_field('creator', login)

    def get_job_creator(self):
        return self._get_field('creator')

    def set_job_owner(self, login):
        self._set_field('owner', login)

    def get_job_owner(self):
        return self._get_field('owner')

    def set_job_type(self, job_type):
        if self.get_in_progress():
            # too late:
            return
        self._set_field('job_type', job_type)
        self.touched()

    def get_job_type(self):
        return self._get_field('job_type')

    def set_job_label(self, job_label):
        self._set_field('job_label', job_label)
    
    def get_job_label(self):
        return self._get_field('job_label')

    def set_job_params(self, job_params):
        if self.get_in_progress():
            # too late:
            return
        self._set_field('job_params', json.dumps(job_params))
        self.touched()

    def get_job_params(self):
        args, kwargs = json.loads(self._get_field('job_params'))
        str_key_kwargs = {}
        for k, v in kwargs.items():
            str_key_kwargs[str(k)] = v
        return args, str_key_kwargs

    def add_to_pool_queue(self):
        q = self._actor.get_pool_queue(self.get_pool())
        score = float(self.get_priority())
        
        if self._actor.redis_version[0] < 3:
            self._actor._db.zadd(self._key(key), **{member: score})
        else:
            self._actor._db.zadd(
                q, mapping={self._jid: score}
            )
        
        self.touched()

    def remove_from_pool_queue(self):
        q = self._actor.get_pool_queue(self.get_pool())
        removed = self._actor._db.zrem(q, self._jid)
        if removed:
            self.touched()

    def set_oid(self, oid):
        if self.get_in_progress():
            # too late:
            return
        self._set_field('oid', str(oid))
        self.touched()

    def get_oid(self):
        '''
        Returns the flow Ojbect id that the workers will "execute"
        '''
        return self._get_field('oid')

    def set_pool(self, pool):
        if self.get_in_progress():
            # too late...
            return 

        if self.get_pool() is None:
            # first set is straight forward:
            self._set_field('pool', str(pool))
            self.touched()
            return 

        with self.after_touch():
            unpause = False
            if not self.get_paused():
                unpause = True
                self.set_paused(True)
            
            self._set_field('pool', str(pool))

            if unpause:
                self.set_paused(False)

    def get_pool(self):
        return self._get_field('pool')

    def set_paused(self, b):
        if self.get_in_progress():
            # too late
            return 

        if self.get_paused() == b:
            return 

        with self.after_touch():
            if not b:
                self.add_to_pool_queue()
            else:
                self.remove_from_pool_queue()
            self._set_field('paused', b and '1' or '')

    def get_paused(self):
        s = self._get_field('paused')
        return s == '1'

    def set_priority(self, priority):
        with self.after_touch():
            unpause = False
            if not self.get_paused():
                unpause = True
                self.set_paused(True)

            self._set_field('priority', str(priority))

            if unpause:
                self.set_paused(False)

    def get_priority(self):
        return int(self._get_field('priority') or 0)

    def set_in_progress(self):
        with self.after_touch():
            self._set_field('in_progress', '1')
            self._set_field('done', '')

    def get_in_progress(self):
        return bool(self._get_field('in_progress'))

    def set_node(self, node_id):
        with self.after_touch():
            self.remove_from_pool_queue()
            self._set_field('node', node_id)
            self._set_field('in_progress', '1')

    def set_done(self):
        with self.after_touch():
            self._set_field('in_progress', '')
            self._set_field('done', '1')

    def get_done(self):
        return bool(self._get_field('done'))

    def clear_error(self):
        with self.after_touch():
            self._set_field('has_error', '')
            self._set_field('error', '')

    def set_error(self, error_message):
        with self.after_touch():
            self._set_field('has_error', '1')
            self._set_field('error', json.dumps(error_message))

    def get_has_error(self):
        return bool(self._get_field('has_error'))

    def get_error(self):
        return json.loads(self._get_field('error'))

class WriteTee(object):
    '''
    Utility class used by LogTee
    '''
    def __init__(self, fh, orig, prefix=''):
        super(WriteTee, self).__init__()
        self._fh = fh
        self._orig = orig
        self._prefix = prefix

    def write(self, text):
        text = text.replace('\n', '\n'+self._prefix)
        self._fh.write(text)
        self._fh.flush()
        self._orig.write(text)

class LogTee(object):
    '''
    Utility class used by worker_execute_job to tee
    stdout and stderr to the log file.
    ''' 
    def __init__(self):
        self.log_filename = None
        self.log_fh = None
        
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        
        self.stdout = None
        self.stderr = None
        
    def redirect(self, filename):
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
    
        self.log_filename = filename
        self.log_fh = open(self.log_filename, 'w')
    
        self.stdout = WriteTee(self.log_fh, self.orig_stdout)
        sys.stdout = self.stdout
    
        self.stderr = WriteTee(self.log_fh, self.orig_stderr, 'ERROR: ')
        sys.stderr = self.stderr
    
    def close_log(self):
        sys.stdout = self.orig_stdout
        self.stdout = None
    
        sys.stderr = self.orig_stderr
        self.stderr = None
    
        self.log_fh.close()
        self.log_fh = None

class Jobs(Actor):

    JOB_OID_ENVVAR_NAME = 'KABARET_JOBS_FLOW_OID'


    def __init__(self, session, jobs_db_index=9):
        super(Jobs, self).__init__(session)
        import redis
        self.redis_version = [int(i) for i in redis.__version__.split('.')]

        self._db = None
        self._jobs_db_index = jobs_db_index
        self._job_touched_unsubscribe = None
        self._joblist_touched_unsubscribe = None

        self.jobids_set_name = None
        self.job_hashes_namespace = None
        self.pool_queue_namespace = None

        self._node_is_alive = True

    def _create_cmds(self):
        return JobsCmds(self)

    def on_session_connected(self):
        self.log('Configuring Job Manager')
        cluster = self.session().get_actor('Cluster')

        cluster_name = cluster.get_cluster_name()
        self.jobids_set_name = '{}:Jobs:job_ids'.format(cluster_name)
        self.job_hashes_namespace = '{}:Jobs:jobs'.format(cluster_name)
        self.pool_queue_namespace = '{}:Jobs:pool_q'.format(cluster_name)

        self._db = cluster.get_db()

        self.log('Subcribing to jobs messages.')
        self._job_touched_unsubscribe = self.session().channels_subscribe(
            job_touched=self._on_job_touched
        )
        self._job_created_unsubscribe = self.session().channels_subscribe(
            job_created=self._on_job_created
        )
        self._job_deleted_unsubscribe = self.session().channels_subscribe(
            job_deleted=self._on_job_deleted
        )
        self._joblist_touched_unsubscribe = self.session().channels_subscribe(
            joblist_touched=self._on_joblist_touched
        )

    def die(self):
        if self._job_touched_unsubscribe is not None:
            self._job_touched_unsubscribe()

        if self._joblist_touched_unsubscribe is not None:
            self._joblist_touched_unsubscribe()

    def _on_job_touched(self, message):
        jid = message['data']
        self.session().dispatch_event('job_touched', jid=jid)

    def _on_job_created(self, message):
        jid = message['data']
        self.session().dispatch_event('job_created', jid=jid)

    def _on_job_deleted(self, message):
        jid = message['data']
        self.session().dispatch_event('job_deleted', jid=jid)

    def _on_joblist_touched(self, message):
        self.session().dispatch_event('joblist_touched')

    def send_job_touched(self, jid):
        self.session().publish(job_touched=jid)
    
    def send_job_created(self, jid):
        self.session().publish(job_created=jid)

    def send_job_deleted(self, jid):
        self.session().publish(job_deleted=jid)

    def send_joblist_touched(self):
        self.session().publish(joblist_touched=self.jobids_set_name)

    def get_pool_queue(self, pool_name):
        return self.pool_queue_namespace+':'+pool_name

    def get_current_login(self):
        return getpass.getuser()

    def create_job(self, job_type, job_label, job_creator, job_owner, job_params, pool, priority, paused):
        job = Job.create(self, job_type, job_label, job_creator, job_owner, job_params, pool, priority, paused)
        return job

    def get_all_jobs(self):
        jids = self._db.smembers(self.jobids_set_name)
        return [ self.get_job(jid) for jid in jids ]

    def get_job(self, jid):
        return Job(self, jid)

    def delete_job(self, jid, forced):
        '''
        Delete the given job if it is not running.
        If forced is True, deletes the job whatever its status.
    
        Returns True if the job was actually deleted (found and allowed for deletion)
        '''
        deleted = Job.delete(self, jid, forced)
        if deleted:
            self.send_job_deleted(jid)
        return deleted


    #
    #   NODE STUFF
    #
    '''
In Kabaret Script View, access this actor with:

    self.root().session().get_actor('Jobs')

Or use the cmds like:

# JOB CREATE / LIST / DELTE
jid = self.root().session().cmds.Jobs.create_flow_job(
    oid='/path/to/my/job_object', pool='test', priority=100, paused=True
)

self.root().session().cmds.Jobs.set_job_paused(jid, False)
self.root().session().cmds.Jobs.delete_job(jid)

jobs = self.root().session().cmds.Jobs.list_jobs()
for job in jobs:
    self.root().session().cmds.Jobs.delete_job(job['jid'])

# NODE CONTROL

jid = self.root().session().cmds.Jobs.kill_node_job(
    node_id='<NODE_ID>'
)

jid = self.root().session().cmds.Jobs.stop_node(
    node_id='<NODE_ID>'
)

    '''
    def stop_node(self):
        #TODO: we should send a node list touched message 
        self._node_is_alive = False

    def node_stopped(self):
        return not self._node_is_alive

    def _poll_queues(self, qs, node_id):
        jids = None
        for q in qs:
            jids = self._db.zrange(q, 0, 0)
            if jids:
                break

        if jids:
            job = self.get_job(jids[0])
            job.set_node(node_id)
            return job

        return None

    def poll_control(self, node_id):
        qs = [
            self.get_pool_queue(node_id)
        ]
        return self._poll_queues(qs, node_id)

    def poll_pools(self, pools, node_id):
        qs = [
            self.get_pool_queue(pool)
            for pool in pools+[node_id]
        ]
        return self._poll_queues(qs, node_id)

    def node_do_control_job(self, cmd, *args, **kwargs):
        if cmd == 'kill_job':
            print('Killing Job')
            print('     !!! not yet implemented !!!')
        
        elif cmd == 'stop':
            self.stop_node()

        else:
            raise ValueError('Unknown Node control cmd {!r}'.format(cmd))

    def node_spawn_flow_worker(self, oid, interpretor=None, worker_filename=None, show_console=True):
        '''
        Will create a subprocess that runs the given worker_filename (or default) with
        the given python interpretor (or current).

        The worker_filename must be a script which executes the job.
        The default one (kabaret.jobs.jobs_flow_worker) uses the env to connect
        to the same cluster as this one and finds the oid to execute in env.
        '''
        print('Spawning Worker to execute on oid={!r}'.format(oid))
        interpretor = interpretor or sys.executable

        if worker_filename is None:
            import libreflow.utils.kabaret.jobs.jobs_flow_worker as worker
            worker_filename = worker.__file__

        env = os.environ.copy()
        env[self.JOB_OID_ENVVAR_NAME] = str(oid) # json dump in redis made it a unicode :/

        # using -u for unbuffered output. Don't really know if useful :p yolo ^_^ 
        cmd = [interpretor, '-u', worker_filename]

        shell = False
        if show_console:
            if platform.system() == 'Windows':
                cmd = ['start', '/WAIT', 'cmd', '/C']+cmd
                shell = True
            else:
                print("!!! Warning: show_console option ignored for system other that Windows :/")

        try:
            popen = subprocess.Popen(cmd, env=env, shell=shell)
        except:
            traceback.print_exc()
            print(
                '!!! Error Spawning Worker Subprocess:\n#--- CMD was:\n{}\n#--- ENV was:\n{}\n'.format(
                    ' '.join(cmd),
                    '\n'.join([ '{}:{!r}'.format(k,v) for k, v in env.iteritems() ])
                )
            )
            raise
        
        return popen


    def node_execute_job(self, job):
        job_type = job.get_job_type()
        args, kwargs = job.get_job_params()
        print(
            'Executing {} job: {}, {} ({})'.format(
                job_type, args, kwargs, job.jid()
            )
        )

        if job_type == 'NODE_CMD':
            try:
                job.set_in_progress()
                self.node_do_control_job(*args, **kwargs)
            except:
                error_message = traceback.format_exc()
                print('------------------------')
                print(error_message)
                print('------------------------')
                print('ERROR EXECUTING NODE CMD')
                job.set_error('ERROR EXECUTING NODE CMD:\n'+error_message)
                return None
            else:
                print('Command done')
                job.set_done()
                return None

        elif job_type == 'flow':
            try:
                popen = self.node_spawn_flow_worker(*args, **kwargs)
            except:
                error_message = traceback.format_exc()
                print('------------------------')
                print(error_message)
                print('------------------------')
                print('ERROR SPAWING FLOW WORKER')
                job.set_error('ERROR SPAWING FLOW WORKER:\n'+error_message)
                return None
            else:
                print('Worker Spawned.')
                return popen

    #
    #   WORKER STUFF
    #

    def worker_execute_job(self):
        '''
        This is called by the default JobsWorkerSession to execute
        a job picked by the JobsNodeSession which spawned it.
        '''
        try:
            job_oid = os.environ[self.JOB_OID_ENVVAR_NAME]
        except KeyError:
            raise Exception('Could not find {} env-var :/'.format(self.JOB_OID_ENVVAR_NAME))

        import kabaret.flow as flow
        try:
            job = self.session().get_actor('Flow').get_object(job_oid)
        except (flow.MissingChildError, flow.MissingRelationError):
            raise Exception('Could not find job to execute: {}'.format(job_oid))

        log_filename = job.get_log_filename()
        log_tee = LogTee()
        log_tee.redirect(log_filename)
        try:
            job.execute()
        finally:
            log_tee.close_log()
