from typing import Optional, List, Union

from imecilabt.gpulab.model.job import JobState, _int_or_none


class JobFilter:
    def __init__(self,
                 version: Optional[str],
                 cluster_id: Optional[Union[int, str]] = None,
                 empty_cluster_id: bool = True,  # If cluster_id is set, also match jobs that do not have clusterId?  If cluster_id not set, this is implicitly always True!
                 cpu_sharing_jobs: bool = True,  # Also match jobs that want to share a CPU? (jobs with 0 CPU requested)
                 max_system_memory_mb: Optional[int] = None,
                 max_gpu_count: Optional[int] = None,
                 max_cpu_count: Optional[int] = None,
                 allowed_states: Optional[List[JobState]] = None, # [JobState.QUEUED] is a common value  [] and None mean don't filter
                 user_urn: Optional[str] = None,
                 other_user_running: bool = False,
                 project_urn: Optional[str] = None,
                 max_duration_s: Optional[int] = None,
                 slave_cuda_version: Optional[int] = None,  # Only major cuda version should be passed
                 slave_gpu_models: Optional[List[str]] = None,
                 user_name: Optional[str] = None,
                 project_name: Optional[str] = None,
                 assigned_slave_hostname: Optional[str] = None,
                 assigned_slave_instance_id: Optional[str] = None,):
        self.version = version  #dev or stable
        self.allowed_states = allowed_states  # if allowed_states else None
        self.cluster_id: Optional[int] = int(cluster_id) if cluster_id is not None else None
        self.empty_cluster_id = empty_cluster_id or not cluster_id
        self.cpu_sharing_jobs = cpu_sharing_jobs
        # assert cluster_id is not None or empty_cluster_id  # empty_cluster_id may not be False when cluster_id == None
        self.max_gpu_count = _int_or_none(max_gpu_count)
        self.max_cpu_count = _int_or_none(max_cpu_count)
        self.max_system_memory_mb = _int_or_none(max_system_memory_mb)
        self.user_urn = user_urn
        self.other_user_running = other_user_running
        self.project_urn = project_urn
        self.max_duration_s = _int_or_none(max_duration_s)
        self.slave_cuda_version = slave_cuda_version
        self.slave_gpu_models = [] if slave_gpu_models is None else list(slave_gpu_models)
        self.user_name = user_name
        self.project_name = project_name
        self.assigned_slave_hostname = assigned_slave_hostname
        self.assigned_slave_instance_id = assigned_slave_instance_id

    # forward compatible with new name for gpulab_version
    @property
    def deployment_environment(self):
        return self.version

    @classmethod
    def for_slave(cls,
                 version: str,
                 assigned_slave_hostname: str,
                 assigned_slave_instance_id: str) -> 'JobFilter':
        """typical JobFilter used by slave to search a Job to execute"""
        return cls(
            version=version,
            allowed_states=[JobState.ASSIGNED],
            assigned_slave_hostname=assigned_slave_hostname,
            assigned_slave_instance_id=assigned_slave_instance_id
        )

    @classmethod
    def for_pending(cls,
                   version: str) -> 'JobFilter':
        """typical JobFilter used to find all Pending Jobs"""
        return cls(
            version=version,
            allowed_states=[JobState.QUEUED]
        )

    @classmethod
    def no_filter(cls):
        return cls(
            version=None,
            allowed_states=[]
        )

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    def to_dict(self) -> dict:
        res = dict()
        res['version'] = self.version
        res['cluster_id'] = self.cluster_id
        res['empty_cluster_id'] = self.empty_cluster_id
        res['cpu_sharing_jobs'] = self.cpu_sharing_jobs
        res['max_system_memory_mb'] = self.max_system_memory_mb
        res['max_gpu_count'] = self.max_gpu_count
        res['max_cpu_count'] = self.max_cpu_count
        res['allowed_states'] = list(map(lambda state: state.name, self.allowed_states)) if self.allowed_states is not None else None
        res['user_urn'] = self.user_urn
        res['other_user_running'] = self.other_user_running
        res['project_urn'] = self.project_urn
        res['max_duration_s'] = self.max_duration_s
        res['slave_cuda_version'] = self.slave_cuda_version
        res['slave_gpu_models'] = self.slave_gpu_models if self.slave_gpu_models is not None else None
        res['user_name'] = self.user_name
        res['project_name'] = self.project_name
        res['assigned_slave_hostname'] = self.assigned_slave_hostname
        res['assigned_slave_instance_id'] = self.assigned_slave_instance_id

        empty = []
        for key,value in res.items():
            if not value:
                empty.append(key)
        for key in empty:
            del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            version=d.get('version', d.get('deployment_environment')),  # forward compatible with new name for "deployment_environment": "version"
            cluster_id=d.get('cluster_id'),
            empty_cluster_id=d.get('empty_cluster_id'),
            cpu_sharing_jobs=d.get('cpu_sharing_jobs'),
            max_system_memory_mb=d.get('max_system_memory_mb'),
            max_gpu_count=d.get('max_gpu_count'),
            max_cpu_count=d.get('max_cpu_count'),
            allowed_states=list(map(lambda state: JobState[state], d.get('allowed_states'))) if d.get('allowed_states') else None,
            user_urn=d.get('user_urn'),
            other_user_running=d.get('other_user_running'),
            project_urn=d.get('project_urn'),
            max_duration_s=d.get('max_duration_s'),
            slave_cuda_version=d.get('slave_cuda_version'),
            slave_gpu_models=d.get('slave_gpu_models'),
            user_name=d.get('user_name'),
            project_name=d.get('project_name'),
            assigned_slave_hostname=d.get('assigned_slave_hostname'),
            assigned_slave_instance_id=d.get('assigned_slave_instance_id'),
        )

    def make_copy(self) -> 'JobFilter':
      return JobFilter.from_dict(self.to_dict())

    def to_params(self) -> dict:
        res = self.to_dict()
        if self.allowed_states:
            res['allowed_states'] = ','.join(list(map(lambda state: state.name, self.allowed_states)))
        if self.slave_gpu_models:
            res['slave_gpu_models'] = ','.join(self.slave_gpu_models)
        return res

    @classmethod
    def from_params(cls, params: dict, version_override=None):
        def _process_bool_arg(args, key, default: Optional[bool] = None) -> Optional[bool]:
            value = args.get(key, default=None)
            if value is None:
                return default
            if value == '':
                return True
            if str(value).lower() in ['true', 't', '1', 'yes']:
                return True
            if str(value).lower() in ['false', 'f', '0', 'no']:
                return False
            return default

        allowed_states_filter = params.get('allowed_states', None)  # overrules pending, finished, running and deleted if present
        pending_filter = _process_bool_arg(params, 'pending', default=False)
        finished_filter = _process_bool_arg(params, 'finished', default=False)
        running_filter = _process_bool_arg(params, 'running', default=False)
        deleted_filter = _process_bool_arg(params, 'deleted', default=False)

        # Make the implicit explicit  (implicit because of allowed_states = [] meaning all)
        if not pending_filter and not finished_filter and not running_filter and not deleted_filter:
            pending_filter = True
            finished_filter = True
            running_filter = True

        allowed_states = []
        if allowed_states_filter:
            try:
                allowed_states = map(lambda state: JobState[state], allowed_states_filter.strip().split(','))
            except Exception:
                raise ValueError('Invalid state in parameter allowed_states="{}"'.format(allowed_states_filter))
        else:
            if pending_filter:
                allowed_states.append(JobState.ONHOLD)
                allowed_states.append(JobState.QUEUED)
            if finished_filter:
                allowed_states.append(JobState.FINISHED)
                allowed_states.append(JobState.FAILED)
                allowed_states.append(JobState.CANCELLED)
            if running_filter:
                allowed_states.append(JobState.TRANSFER)
                allowed_states.append(JobState.RUNNING)
                allowed_states.append(JobState.STARTING)
            if deleted_filter:
                allowed_states.append(JobState.DELETED)

        return cls(
            allowed_states=allowed_states,
            user_urn=params.get('user_urn') if params.get('user_urn') else params.get('userurn'),
            other_user_running=_process_bool_arg(params, 'other_user_running', default=False),
            project_urn=params.get('project_urn', default=None) if params.get('project_urn', None) else params.get('projecturn', default=None),
            user_name=params.get('username', default=None) if params.get('username', None) else params.get('user_name', default=None),
            project_name=params.get('projectname', default=None) if params.get('projectname', None) else params.get('project_name', default=None),

            version=version_override if version_override else params.get('deployment_environment', default=params.get('version', default=None)),
            cluster_id=params.get('cluster_id'),
            empty_cluster_id=params.get('empty_cluster_id'),
            cpu_sharing_jobs=params.get('cpu_sharing_jobs'),
            max_system_memory_mb=params.get('max_system_memory_mb'),
            max_gpu_count=params.get('max_gpu_count'),
            max_cpu_count=params.get('max_cpu_count'),
            max_duration_s=params.get('max_duration_s'),
            slave_cuda_version=params.get('slave_cuda_version'),
            slave_gpu_models=params.get('slave_gpu_models'),
            assigned_slave_hostname=params.get('assigned_slave_hostname'),
            assigned_slave_instance_id=params.get('assigned_slave_instance_id'),
        )
