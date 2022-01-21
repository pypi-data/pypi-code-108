import datetime
from math import ceil
from typing import Union, Optional, Any

from imecilabt_utils.validation_utils import is_valid_email, is_valid_ssh_key
from dataclass_dict_convert import parse_rfc3339
from stringcase import snakecase

from imecilabt.gpulab.model.usage_statistics import GPULabUsageStatistics, ContainerUsageStatistics, GpuUsageStatistics

from imecilabt.gpulab.model.job import Job as Job1, JobState as Job1State, JobPortMapping as Job1PortMapping, \
    NVDockerData as Job1NVDockerData, NVDockerDataResources as Job1NVDockerDataResources, \
    JobRunDetails as Job1RunDetails, JobSchedulerInfo as Job1SchedulerInfo, JobDataLocation as Job1DataLocation
from imecilabt.gpulab.model.job2 import Job as Job2, JobOwner as Job2Owner, JobState as Job2State, JobRequest as Job2Request, \
    JobRequestResources as Job2RequestResources, JobRequestDocker as Job2RequestDocker, \
    JobRequestScheduling as Job2RequestScheduling, JobRequestExtra as Job2RequestExtra, JobStatus as Job2Status, \
    JobStateResources as Job2StateResources, JobStateScheduling as Job2StateScheduling, JobEventTimes as Job2EventTimes, \
    JobPortMapping as Job2PortMapping, JobStorage as Job2Storage

from imecilabt.gpulab.model.usage_statistics import GpuOverview as Job2GpuOverview, GpuInfo as Job2GpuInfo, \
    GPULabUsageStatistics as Job2GPULabUsageStatistics


def convert_job1state_to_job2status(status: Job1State) -> Job2Status:
    return {
        Job1State.ONHOLD: Job2Status.ONHOLD,
        Job1State.QUEUED: Job2Status.QUEUED,
        Job1State.ASSIGNED: Job2Status.ASSIGNED,
        Job1State.TRANSFER: Job2Status.STARTING,
        Job1State.STARTING: Job2Status.STARTING,
        Job1State.RUNNING: Job2Status.RUNNING,
        Job1State.CANCELLED: Job2Status.CANCELLED,
        Job1State.FINISHED: Job2Status.FINISHED,
        Job1State.DELETED: Job2Status.DELETED,
        Job1State.FAILED: Job2Status.FAILED,
    }.get(status, Job2Status.FAILED)


def convert_job2status_to_job1state(status: Job2Status) -> Job1State:
    return {
        Job2Status.ONHOLD: Job1State.ONHOLD,
        Job2Status.QUEUED: Job1State.QUEUED,
        Job2Status.ASSIGNED: Job1State.ASSIGNED,
        Job2Status.STARTING: Job1State.STARTING,
        Job2Status.RUNNING: Job1State.RUNNING,
        Job2Status.CANCELLED: Job1State.CANCELLED,
        Job2Status.FINISHED: Job1State.FINISHED,
        Job2Status.DELETED: Job1State.DELETED,
        Job2Status.FAILED: Job1State.FAILED,
        Job2Status.MUSTHALT: Job1State.RUNNING,
        Job2Status.HALTING: Job1State.RUNNING,
        Job2Status.HALTED: Job1State.FINISHED,
    }.get(status, Job1State.FAILED)


def convert_job1portmapping_to_job2_portmapping(port_mapping: Job1PortMapping) -> Job2PortMapping:
    def _handle_port_val(val: Union[str, int]) -> Optional[int]:
        if val is None:
            return None
        if val == 'None':
            return None
        if isinstance(val, int):
            return val
        val = str(val)
        val = val.replace("/tcp", "").replace("/udp", "")
        return int(val)

    container_port = _handle_port_val(port_mapping.container_port)
    return Job2PortMapping(container_port=container_port if container_port else 0,  # fallback to 0 if no port specified...
                           host_ip=port_mapping.host_ip,
                           host_port=_handle_port_val(port_mapping.host_port))


def convert_job1_gpu_fixed_info_to_job2_gpu_details(gpu_fixed_info) -> Optional[Job2GpuOverview]:
    if not gpu_fixed_info:
        return None
    if 'cuda_driver_version_major' not in gpu_fixed_info:
        return None
    return Job2GpuOverview(
        cuda_version_full='{}.{}'.format(
            gpu_fixed_info.get('cuda_driver_version_major'),
            gpu_fixed_info.get('cuda_driver_version_minor')),
        cuda_version_int=gpu_fixed_info.get('cuda_driver_version'),
        cuda_version_major=gpu_fixed_info.get('cuda_driver_version_major'),
        cuda_version_minor=gpu_fixed_info.get('cuda_driver_version_minor'),
        driver_version=gpu_fixed_info.get('driver_version'),
        nvml_version=gpu_fixed_info.get('nvml_version'),
        gpus=[
            Job2GpuInfo(
                index=g.get('index', -1),
                uuid=g.get('uuid', 'N/A'),
                serial=g.get('serial', 'N/A'),
                name=g.get('name', 'unknown'),
                brand=g.get('brand', 'unknown'),
                minor_number=g.get('minor_number', -1),
                board_id=g.get('board_id', -1),
                bridge_chip_info=g.get('bridge_chip_info', 'unknown'),
                is_multi_gpu_board=g.get('is_multi_gpu_board', False),
                max_pcie_link_generation=g.get('max_pcie_link_generation', -1),
                max_pcie_link_width=g.get('max_pcie_link_width', -1),
                vbios_version=g.get('vbios_version', 'unknown')
            ) for g in (gpu_fixed_info.get('gpu') or [])
        ]
    )


def convert_job1_summary_statistics_to_job2_final_usage_statistics(summary_statistics):
    if not summary_statistics:
        return None
    if 'agg_period_ns' not in summary_statistics:
        return None

    def parse_rfc3339_if_needed(str_or_date) -> Optional[datetime.datetime]:
        if str_or_date is None:
            return None
        if isinstance(str_or_date, datetime.datetime):
            return str_or_date
        else:
            return parse_rfc3339(str_or_date)

    def int_or_zero(val: Optional[Any]) -> Optional[int]:
        return int(val) if val is not None else 0

    def float_or_zero(val: Optional[Any]) -> Optional[float]:
        return float(val) if val is not None else 0.0

    return GPULabUsageStatistics(
        container_statistics=ContainerUsageStatistics(
            first_time=parse_rfc3339_if_needed(summary_statistics.get('first_time')),
            last_time=parse_rfc3339_if_needed(summary_statistics.get('last_time')),
            agg_period_ns=int_or_zero(summary_statistics.get('agg_period_ns')),
            cpu_count=int_or_zero(summary_statistics.get('cpu_count')),
            cpu_usage=float_or_zero(summary_statistics.get('cpu_usage')),
            cpu_usage_total_ns=int_or_zero(summary_statistics.get('cpu_usage_total_ns')),
            cpu_usage_kernelmode_ns=int_or_zero(summary_statistics.get('cpu_usage_kernelmode_ns')),
            cpu_usage_usermode_ns=int_or_zero(summary_statistics.get('cpu_usage_usermode_ns')),
            max_pid_count=int_or_zero(summary_statistics.get('max_pid_count')),
            mem_limit_byte=int_or_zero(summary_statistics.get('mem_limit_byte')),
            mem_max_usage_byte=int_or_zero(summary_statistics.get('mem_max_usage_byte')),
            network_rx_byte=int_or_zero(summary_statistics.get('network_rx_byte')),
            network_tx_byte=int_or_zero(summary_statistics.get('network_tx_byte')),
        ),
        gpu_statistics=GpuUsageStatistics(
            gpu_count=int_or_zero(summary_statistics.get('gpu_count')) or 0,
            average_utilization=float_or_zero(summary_statistics.get('gpu_all_utilization_average_%all')),
            average_mem_utilization=float_or_zero(summary_statistics.get('gpu_all_utilization_mem_average_%all'))
        )
    )


def convert_job1_to_job2(job: Job1) -> Job2:
    assert isinstance(job, Job1)
    assert job.scheduler_info
    assert job.run_details
    assert job.nvdocker_data
    assert job.nvdocker_data.resources

    gpu_model_list = []
    if job.nvdocker_data.resources.gpu_model:
        if isinstance(job.nvdocker_data.resources.gpu_model, str):
            gpu_model_list = [job.nvdocker_data.resources.gpu_model,]
        elif isinstance(job.nvdocker_data.resources.gpu_model, list):
            gpu_model_list = job.nvdocker_data.resources.gpu_model
        else:
            raise TypeError('Unsupported type for gpu_model list: {!r}'
                            .format(type(job.nvdocker_data.resources.gpu_model)))
    # if not job.nvdocker_data.docker_image:
    #     raise ValueError('docker_image may not be empty')
    request_cluster_id = None
    if job.nvdocker_data.cluster_id:
        if isinstance(job.nvdocker_data.cluster_id, int):
            request_cluster_id = job.nvdocker_data.cluster_id
        elif isinstance(job.nvdocker_data.cluster_id, str):
            request_cluster_id = int(job.nvdocker_data.cluster_id)
        elif isinstance(job.nvdocker_data.cluster_id, list):
            # only 1 cluster ID support for Job2
            request_cluster_id = job.nvdocker_data.cluster_id[0] if job.nvdocker_data.cluster_id else None
        else:
            raise TypeError('Unsupported type for nvdocker_data.cluster_id: {!r}'
                            .format(type(job.nvdocker_data.cluster_id)))
    state_cluster_id = -1
    if job.run_details.cluster_id:
        if isinstance(job.run_details.cluster_id, int):
            state_cluster_id = job.run_details.cluster_id
        elif isinstance(job.run_details.cluster_id, str):
            state_cluster_id = int(job.run_details.cluster_id)
        else:
            raise TypeError('Unsupported type for job.run_details.cluster_id: {!r}'
                            .format(type(job.run_details.cluster_id)))
    requested_system_memory_gb = job.nvdocker_data.resources.system_memory_gb
    if job.nvdocker_data.resources.system_memory_mb > requested_system_memory_gb * 1024:
        # rounding up, because user wants at least the requested amount
        requested_system_memory_gb += 1
        assert requested_system_memory_gb == ceil(job.nvdocker_data.resources.system_memory_mb / 1024.0), \
            'requested_system_memory_gb={} nvdocker_data.resources.system_memory_mb={}'\
                .format(requested_system_memory_gb, job.nvdocker_data.resources.system_memory_mb)
    request = Job2Request(
        resources=Job2RequestResources(
            cpus=job.nvdocker_data.resources.cpu_cores or 0,
            gpus=job.nvdocker_data.resources.gpus or 0,
            cpu_memory_gb=requested_system_memory_gb,
            gpu_memory_gb=None,  # Not in Job1
            min_cuda_version=job.nvdocker_data.resources.min_cuda_version,
            cluster_id=request_cluster_id,
            gpu_model=gpu_model_list,
            slave_name=None,  # Not in Job1
            slave_instance_id=None,  # Not in Job1
            features=[],  # Not in Job1, but some will be auto_derived by GPULab
        ),
        docker=Job2RequestDocker(
            image=job.nvdocker_data.docker_image if job.nvdocker_data.docker_image else 'unspecified',
            command=job.nvdocker_data.command if job.nvdocker_data.command else [],
            environment=job.nvdocker_data.environment,
            project_gid_variable_name=job.nvdocker_data.project_gid_variable_name,
            user=job.nvdocker_data.docker_user,
            group_add=job.nvdocker_data.docker_group_add_list,
            working_dir=job.nvdocker_data.working_dir,
            storage=[
                # note: Job1 JobDataLocation protocol and share_host are ignored -> never used anyway
                Job2Storage(container_path=dl.mount_point, host_path=dl.share_path, size_gb=None)
                for dl in job.nvdocker_data.job_data_locations
            ] if job.nvdocker_data.job_data_locations else [],
            port_mappings=[
                convert_job1portmapping_to_job2_portmapping(pm) for pm in job.nvdocker_data.port_mappings
            ] if job.nvdocker_data.port_mappings else [],
        ),
        scheduling=Job2RequestScheduling(
            # None of this is in Job1, so we just fall back to the defaults
        ),
        extra=Job2RequestExtra(
            ssh_pub_keys=[sshkey for sshkey in job.ssh_pubkeys if is_valid_ssh_key(sshkey)] if job.ssh_pubkeys else [],
            email_on_end=[email for email in job.emails_end if is_valid_email(email)] if job.emails_end else [],
            email_on_queue=[email for email in job.emails_queue if is_valid_email(email)] if job.emails_queue else [],
            email_on_run=[email for email in job.emails_run if is_valid_email(email)] if job.emails_run else [],
            email_on_halt=[],
            email_on_restart=[],
        ),
    )
    state = Job2State(
        status=convert_job1state_to_job2status(job.state),
        resources=Job2StateResources(
            cluster_id=state_cluster_id,
            cpu_ids=job.run_details.cpu_ids if job.run_details.cpu_ids else [],
            gpu_ids=job.run_details.gpu_ids if job.run_details.gpu_ids else [],
            cpu_memory_gb=job.run_details.memory_gb,
            gpu_memory_gb=0,  # not in Job1
            slave_host=job.run_details.slave_dns_name if job.run_details.slave_dns_name else 'unknown',
            slave_name=job.run_details.slave_hostname if job.run_details.slave_hostname else 'unknown',
            slave_instance_id=job.run_details.slave_instance_id if job.run_details.slave_instance_id else 'unknown',
            slave_instance_pid=job.run_details.slave_instance_pid if job.run_details.slave_instance_pid else -1,
            worker_id=job.run_details.worker_id if job.run_details.worker_id else -1,
            ssh_host=job.run_details.slave_dns_name,
            ssh_port=22,
            ssh_username=job.run_details.ssh_username,
            ssh_proxy_host=job.run_details.ssh_proxy_host,
            ssh_proxy_port=job.run_details.ssh_proxy_port,
            ssh_proxy_username=job.run_details.ssh_proxy_username,
            port_mappings=[
                convert_job1portmapping_to_job2_portmapping(pm) for pm in job.run_details.port_mappings
            ] if job.run_details.port_mappings else [],
            gpu_details=convert_job1_gpu_fixed_info_to_job2_gpu_details(job.run_details.gpu_fixed_info)
        ) if job.run_details and job.run_details.slave_hostname else None,
        scheduling=Job2StateScheduling(
            assigned_cluster_id=job.scheduler_info.assigned_cluster_id,
            assigned_instance_id=job.scheduler_info.assigned_instance_id,
            assigned_slave_name=job.scheduler_info.assigned_slave_hostname,
            queued_explanations=job.scheduler_info.queued_explanations or [],
            within_max_simultaneous_jobs=job.scheduler_info.within_max_simultaneous_jobs,
            tally_increment=None
        ) if job.scheduler_info else Job2StateScheduling(),
        event_times=Job2EventTimes(
            created=job.created if job.created else datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            status_updated=job.state_updated if job.created else datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            QUEUED=job.queue_time,
            ASSIGNED=job.scheduler_info.assigned_time if job.scheduler_info else None,
            STARTING=job.run_details.start_date,
            RUNNING=job.run_details.start_date,
            FINISHED=None, #job.run_details.end_date,
            FAILED=None,
            MUSTHALT=None,
            HALTING=None,
            HALTED=None,
            CANCELLED=None,
            DELETED=None,
            long_run_notify=job.run_details.notify_date
        ),
        final_usage_statistics=convert_job1_summary_statistics_to_job2_final_usage_statistics(
            job.run_details.summary_statistics
        ) if job.run_details else None,
    ) if job.state or \
         (job.run_details and not job.run_details.is_default()) or \
         (job.scheduler_info and not job.scheduler_info.is_default()) \
        else None
    return Job2(
        uuid=job.uuid,
        name=job.name or job.nvdocker_data.name or 'unnamed',
        deployment_environment=job.deployment_environment if job.deployment_environment else 'production',
        request=request,
        description=job.nvdocker_data.description or job.nvdocker_data.description or None,
        owner=Job2Owner(
            user_urn=job.user_urn,
            user_email=job.user_email or 'unknown@unknown.unknown',
            project_urn=job.project_urn
        ) if job.user_urn and job.project_urn else None,
        state=state,
    )


def _convert_dict_keys_to_snake_case(d: dict) -> dict:
    res = {}
    for k,v in d.items():
        res[snakecase(k)] = v
    return res


def convert_job2_to_job1(job: Job2) -> Job1:
    assert isinstance(job, Job2)
    if job.request:
        nvdocker_data = Job1NVDockerData(
            job_type='batch',
            ssh_pubkeys=job.request.extra.ssh_pub_keys,
            cluster_id=job.request.resources.cluster_id,
            command=job.request.docker.command if job.request.docker.command else None,
            name=job.name,
            description=job.description,
            docker_image=job.request.docker.image,
            docker_user=job.request.docker.user,
            environment=job.request.docker.environment,
            job_data_locations=[
                Job1DataLocation(mount_point=storage.container_path, share_path=storage.host_path)
                for storage in job.request.docker.storage
            ],
            port_mappings=[
                Job1PortMapping(container_port=pm.container_port, host_port=pm.host_port)
                for pm in job.request.docker.port_mappings
            ],
            project_gid_variable_name=job.request.docker.project_gid_variable_name,
            docker_group_add=job.request.docker.group_add,
            working_dir=job.request.docker.working_dir,
            resources=Job1NVDockerDataResources(
                cpu_cores=job.request.resources.cpus,
                gpus=job.request.resources.gpus,
                system_memory=job.request.resources.cpu_memory_mb,
                gpu_model=job.request.resources.gpu_model,
                min_cuda_version=job.request.resources.min_cuda_version,
            )
        )
    else:
        nvdocker_data = Job1NVDockerData(
            name=job.name,
            description=job.description,
        )
    summary_statistics = {
        'first_time': job.state.final_usage_statistics.container_statistics.first_time,
        'last_time': job.state.final_usage_statistics.container_statistics.last_time,
        'agg_period_ns': job.state.final_usage_statistics.container_statistics.agg_period_ns,
        'cpu_count': job.state.final_usage_statistics.container_statistics.cpu_count,
        'cpu_usage': job.state.final_usage_statistics.container_statistics.cpu_usage,
        'cpu_usage_total_ns': job.state.final_usage_statistics.container_statistics.cpu_usage_total_ns,
        'cpu_usage_kernelmode_ns': job.state.final_usage_statistics.container_statistics.cpu_usage_kernelmode_ns,
        'cpu_usage_usermode_ns': job.state.final_usage_statistics.container_statistics.cpu_usage_usermode_ns,
        'max_pid_count': job.state.final_usage_statistics.container_statistics.max_pid_count,
        'mem_limit_byte': job.state.final_usage_statistics.container_statistics.mem_limit_byte,
        'mem_max_usage_byte': job.state.final_usage_statistics.container_statistics.mem_max_usage_byte,
        'network_rx_byte': job.state.final_usage_statistics.container_statistics.network_rx_byte,
        'network_tx_byte': job.state.final_usage_statistics.container_statistics.network_tx_byte,
        'gpu_count': job.state.final_usage_statistics.gpu_statistics.gpu_count,
        'gpu_all_utilization_average_%all': job.state.final_usage_statistics.gpu_statistics.average_utilization,
        'gpu_all_utilization_mem_average_%all': job.state.final_usage_statistics.gpu_statistics.average_mem_utilization
    } if job.state and job.state.final_usage_statistics else None
    if job.state and job.state.resources:
        run_details = Job1RunDetails(
            cluster_id=job.state.resources.cluster_id,
            cpu_ids=job.state.resources.cpu_ids,
            deadline_date=None,
            gpu_fixed_info={
                'cuda_driver_version': job.state.resources.gpu_details.cuda_version_int,
                'cuda_driver_version_major': job.state.resources.gpu_details.cuda_version_major,
                'cuda_driver_version_minor': job.state.resources.gpu_details.cuda_version_minor,
                'driver_version': job.state.resources.gpu_details.driver_version,
                'gpu': [_convert_dict_keys_to_snake_case(gpu_info.to_dict()) for gpu_info in job.state.resources.gpu_details.gpus],
                'nvml_version': job.state.resources.gpu_details.nvml_version
            } if job.state.resources.gpu_details else None,
            gpu_ids=job.state.resources.gpu_ids,
            memory="{}b".format(job.state.resources.cpu_memory_byte),
            port_mappings=[
                {
                    'container_port': "{}/tcp".format(pm.container_port),
                    'host_ip': pm.host_ip,
                    'host_port': "{}".format(pm.host_port)
                }
                for pm in job.state.resources.port_mappings
            ],
            slave_dns_name=job.state.resources.slave_host,
            slave_hostname=job.state.resources.slave_name,
            slave_instance_id=job.state.resources.slave_instance_id,
            slave_instance_pid=job.state.resources.slave_instance_pid,
            ssh_proxy_host=job.state.resources.ssh_proxy_host,
            ssh_proxy_port=job.state.resources.ssh_proxy_port,
            ssh_proxy_username=job.state.resources.ssh_proxy_username,
            ssh_username=job.state.resources.ssh_username,
            start_date=job.state.event_times.STARTING or job.state.event_times.RUNNING,
            worker_id=job.state.resources.worker_id,
            notify_date=job.state.event_times.long_run_notify,
            summary_statistics=summary_statistics
        )
    else:
        run_details = Job1RunDetails(
            deadline_date=None,
            start_date=job.state.event_times.STARTING or job.state.event_times.RUNNING,
            notify_date=job.state.event_times.long_run_notify,
            summary_statistics=summary_statistics
        ) if job.state and job.state.event_times else None
    scheduler_info = Job1SchedulerInfo(
        assigned_cluster_id=job.state.scheduling.assigned_cluster_id,
        assigned_instance_id=job.state.scheduling.assigned_instance_id,
        assigned_slave_hostname=job.state.scheduling.assigned_slave_name,
        assigned_time=job.state.event_times.ASSIGNED,
        queued_explanations=job.state.scheduling.queued_explanations,
        within_max_simultaneous_jobs=job.state.scheduling.within_max_simultaneous_jobs
    ) if job.state and job.state.scheduling else None
    return Job1(
        uuid=job.uuid,
        state=convert_job2status_to_job1state(job.state.status) if job.state and job.state.status else None,
        gpulab_version=job.get_backward_compat_version(),
        user_email=job.owner.user_email,
        user_urn=job.owner.user_urn,
        project_urn=job.owner.project_urn,
        created=job.state.event_times.created if job.state and job.state.event_times else None,
        emails_end=job.request.extra.email_on_end,
        emails_queue=job.request.extra.email_on_queue,
        emails_run=job.request.extra.email_on_run,
        ssh_pubkeys=job.request.extra.ssh_pub_keys,
        name=job.name,
        queue_time=job.state.event_times.QUEUED if job.state and job.state.event_times else None,
        state_updated=job.state.event_times.status_updated if job.state and job.state.event_times else None,
        nvdocker_data=nvdocker_data,
        run_details=run_details,
        scheduler_info=scheduler_info,
    )


def is_jsondict_job1(json_dict: dict) -> bool:
    # return 'gpulab_version' in json_dict and ('nvdocker_data' in json_dict or 'jobDefinition' in json_dict)
    return 'nvdocker_data' in json_dict or 'jobDefinition' in json_dict


def is_jsondict_job2(json_dict: dict) -> bool:
    return 'request' in json_dict or 'owner' in json_dict
    # return 'deploymentEnvironment' in json_dict and 'request' in json_dict and 'owner' in json_dict


def convert_any_to_job1(job: Union[Job1,Job2]) -> Job1:
    if isinstance(job, Job2):
        return convert_job2_to_job1(job)
    assert isinstance(job, Job1)
    return job


def convert_any_to_job2(job: Union[Job1,Job2]) -> Job2:
    if isinstance(job, Job1):
        return convert_job1_to_job2(job)
    assert isinstance(job, Job2)
    return job


def any_jsondict_to_job2(json_dict: dict) -> Job2:
    if is_jsondict_job1(json_dict):
        job1 = Job1.from_dict(json_dict)
        return convert_job1_to_job2(job1)
    if is_jsondict_job2(json_dict):
        return Job2.from_dict(json_dict)
    raise TypeError('Unknown job type for {}'.format(json_dict))


def any_jsondict_to_job1(json_dict: dict) -> Job1:
    if is_jsondict_job2(json_dict):
        job2 = Job2.from_dict(json_dict)
        return convert_job2_to_job1(job2)
    if is_jsondict_job1(json_dict):
        return Job1.from_dict(json_dict)
    raise TypeError('Unknown job type for {}'.format(json_dict))
