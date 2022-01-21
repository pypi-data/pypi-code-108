import logging
from dataclasses import dataclass, field
from typing import Optional, List, Union

from imecilabt.gpulab.model.job2 import JobStatus
from stringcase import snakecase, camelcase

from imecilabt.gpulab.model.slave_info2 import SlaveInfo2
from dataclass_dict_convert import dataclass_dict_convert, dataclass_auto_type_check, dataclass_copy_method

##
## Version 2 of JobFilter: JobFilter2
##
## Changes:
##   - "version" renamed to "deployment_environment"
##   - a lot of (now) unneeded filters dropped
##


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class JobFilter2:
    deployment_environment: Optional[str] = None
    cluster_id: Optional[int] = None  # requested OR assigned cluster ID
    allowed_states: List[JobStatus] = field(default_factory=list)  # [] means: don't filter
    user_urn: Optional[str] = None
    user_name: Optional[str] = None
    project_urn: Optional[str] = None
    project_name: Optional[str] = None
    assigned_slave_name: Optional[str] = None
    assigned_slave_instance_id: Optional[str] = None

    @classmethod
    def for_pending(cls,
                    deployment_environment: str) -> 'JobFilter2':
        """typical JobFilter used to find all Pending Jobs"""
        return cls(
            deployment_environment=deployment_environment,
            allowed_states=[JobStatus.QUEUED]
        )

    @classmethod
    def for_slave(cls,
                  deployment_environment: str,
                  assigned_slave_instance_id: str,
                  assigned_slave_name: str,
                  project_urn: Optional[str],
                  ) -> 'JobFilter2':
        """typical JobFilter used to find all Jobs assigned to a slave"""
        return cls(
            deployment_environment=deployment_environment,
            assigned_slave_instance_id=assigned_slave_instance_id,
            assigned_slave_name=assigned_slave_name,
            project_urn=project_urn,
            allowed_states=[JobStatus.ASSIGNED]
        )

    @classmethod
    def no_filter(cls) -> 'JobFilter2':
        return cls(
            deployment_environment=None,
            allowed_states=[]
        )

    def fix_assigned_slave_name(self, slave_infos: List[SlaveInfo2]) -> 'JobFilter2':
        """
        :param slave_infos: list of current slaves
        :return: A copy of this JobFilter2, with the assigned_slave_name replaced by the slave name,
                 if it matches the slave. That means that if it matches an alias,
                 it will now match the slave name instead. As the slave name can be matched against, this is handy.
        """
        if not slave_infos:
            slave_infos = []
        fixed_assigned_slave_name = self.assigned_slave_name
        if self.assigned_slave_name:
            for slave_info in slave_infos:
                if slave_info.match_name(self.assigned_slave_name):
                    fixed_assigned_slave_name = slave_info.name
        return JobFilter2(
            deployment_environment=self.deployment_environment,
            cluster_id=self.cluster_id,
            allowed_states=self.allowed_states,
            user_urn=self.user_urn,
            user_name=self.user_name,
            project_urn=self.project_urn,
            project_name=self.project_name,
            assigned_slave_name=fixed_assigned_slave_name,
            assigned_slave_instance_id=self.assigned_slave_instance_id,
        )

    def to_params(self) -> dict:
        base = self.to_dict()
        res = {}
        for key, val in base.items():
            res[snakecase(key)] = val
        if self.allowed_states:
            res['allowed_states'] = ','.join(list(map(lambda state: state.name, self.allowed_states)))
        return res

    @classmethod
    def from_params(cls, params: dict, deployment_environment_override=None) -> 'JobFilter2':
        def _process_bool_arg(args: dict, key, default: Optional[bool] = None) -> Optional[bool]:
            value = args.pop(key, None)  # Note: this changes args!
            if value is None:
                return default
            if value == '':
                return True
            if str(value).lower() in ['true', 't', '1', 'yes']:
                return True
            if str(value).lower() in ['false', 'f', '0', 'no']:
                return False
            return default

        params = dict(params)  # Shallow copy. (This might be an ImmutableMultiDict.)

        # Remove old params no longer supported
        for ignored_key in ('max_hours', 'max_seconds', 'max_count', 'empty_cluster_id',
                            'cpu_sharing_jobs', 'max_system_memory_mb', 'max_gpu_count', 'max_cpu_count',
                            'other_user_running', 'max_duration_s', 'slave_cuda_version', 'slave_gpu_models',):
            params.pop(ignored_key, None)

        # translate backward compatible parameters
        for old, new in (('version', 'deployment_environment'), ('userurn', 'user_urn'), ('username', 'user_name'), ('projecturn', 'project_urn'), ('projectname', 'project_name')):
            backward_compat_version = params.pop(old, None)
            if params.get(new, None) is None and backward_compat_version:
                params[new] = backward_compat_version

        allowed_states_filter = params.get('allowed_states', None)  # overrules pending, finished, running and deleted if present
        pending_filter = _process_bool_arg(params, 'pending', default=False)
        finished_filter = _process_bool_arg(params, 'finished', default=False)
        running_filter = _process_bool_arg(params, 'running', default=False)
        deleted_filter = _process_bool_arg(params, 'deleted', default=False)

        # If nothing is filtered, show all states, except delete
        if not pending_filter and not finished_filter and not running_filter and not deleted_filter:
            pending_filter = True
            finished_filter = True
            running_filter = True

        allowed_states = []
        if allowed_states_filter:
            try:
                states_str_list = list(allowed_states_filter.strip().split(','))
                states_str_list = [s.strip() for s in states_str_list]
                # backward compatible: ignore TRANSFER
                allowed_states = [JobStatus[s] for s in states_str_list if s != 'TRANSFER']
            except Exception:
                raise ValueError('Invalid state in parameter allowed_states="{}"'.format(allowed_states_filter))
        else:
            if pending_filter:
                allowed_states.append(JobStatus.ONHOLD)
                allowed_states.append(JobStatus.QUEUED)
            if finished_filter:
                allowed_states.append(JobStatus.FINISHED)
                allowed_states.append(JobStatus.FAILED)
                allowed_states.append(JobStatus.CANCELLED)
                allowed_states.append(JobStatus.HALTED)
            if running_filter:
                allowed_states.append(JobStatus.RUNNING)
                allowed_states.append(JobStatus.STARTING)
                allowed_states.append(JobStatus.MUSTHALT)
                allowed_states.append(JobStatus.HALTING)
            if deleted_filter:
                allowed_states.append(JobStatus.DELETED)

        res = {}
        for key, val in params.items():
            translated_key = camelcase(key)
            if translated_key == 'clusterId' and val:
                res[translated_key] = int(val)
            else:
                res[translated_key] = val
        if allowed_states:
            res['allowedStates'] = list(map(lambda state: state.name, allowed_states))
        if deployment_environment_override:
            res['deploymentEnvironment'] = deployment_environment_override
        logging.debug('JobFilter2.from_params calls JobFilter2.from_dict({!r})'.format(res))
        return JobFilter2.from_dict(res)
