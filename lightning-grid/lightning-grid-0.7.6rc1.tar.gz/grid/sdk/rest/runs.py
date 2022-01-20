from typing import List, Optional, Dict

from grid.openapi.models import (
    Body8,
    V1CreateRunRequest,
    V1Run,
    V1RunSpec,
    V1RunState,
    V1RunActions,
    V1Resources,
    Externalv1ScratchSpace,
    Externalv1ImageSpec,
    V1DependencyFileInfo,
    V1PackageManager,
    V1DatastoreMounts,
    V1DeleteRunResponse,
)
from grid.sdk.rest.client import GridRestClient
from grid.sdk.rest.exceptions import throw_with_message


@throw_with_message
def create_run(
    client: GridRestClient,
    cluster_id: str,
    run_name: str,
    run_description: Optional[str],
    run_controller_command: str,
    source_code: str,
    localdir: bool,
    run_sweep_type: str,
    run_sweep_options: Optional[Dict[str, str]],
    scratch_mount_path: str,
    scratch_size_gb: int,
    instance_type: str,
    use_spot: bool,
    per_exp_resources_cpu: Optional[int] = None,
    per_exp_resources_gpu: Optional[int] = None,
    per_exp_resources_storage_gb: Optional[int] = None,
    per_exp_resources_extra: Optional[Dict[str, str]] = None,
    on_build_actions: Optional[List[str]] = None,
    on_build_start_actions: Optional[List[str]] = None,
    on_build_end_actions: Optional[List[str]] = None,
    on_experiment_start_actions: Optional[List[str]] = None,
    on_experiment_end_actions: Optional[List[str]] = None,
    image_dockerfile: Optional[str] = None,
    image_framework: Optional[str] = None,
    image_dep_file: Optional[str] = None,
    per_exp_env_vars: Optional[Dict[str, str]] = None,
    datastores: Optional[Dict[str, str]] = None,  # datastore_id: mount_path
    relative_work_dir: str = None,
    dry_run: bool = False,
    auto_resume: bool = False,
) -> V1Run:
    if image_dep_file and image_dep_file.endswith('.txt'):
        dep_file_info = V1DependencyFileInfo(
            path=image_dep_file,
            package_manager=V1PackageManager.PIP,
        )
    elif image_dep_file and (image_dep_file.lower().endswith('.yaml') or image_dep_file.lower().endswith('.yml')):
        dep_file_info = V1DependencyFileInfo(
            path=image_dep_file,
            package_manager=V1PackageManager.CONDA,
        )
    else:
        dep_file_info = None

    datastore_mounts = None
    if datastores:
        datastore_mounts = [V1DatastoreMounts(id=key, mount_path=value) for key, value in datastores.items()]

    request = V1CreateRunRequest(
        name=run_name,
        description=run_description,
        local_dir=localdir,
        spec=V1RunSpec(
            actions=V1RunActions(
                on_build=on_build_actions,
                on_build_start=on_build_start_actions,
                on_build_end=on_build_end_actions,
                on_experiment_start=on_experiment_start_actions,
                on_experiment_end=on_experiment_end_actions,
            ),
            cluster_id=cluster_id,
            datastores=datastore_mounts,
            desired_state=V1RunState.SUCCEEDED,
            dry_run=dry_run,
            env=per_exp_env_vars,
            image=Externalv1ImageSpec(
                dependency_file_info=dep_file_info,
                dockerfile=image_dockerfile,
                framework=image_framework,
            ),
            instance_type=instance_type,
            relative_work_dir=relative_work_dir,
            resources=V1Resources(
                cpu=per_exp_resources_cpu,
                gpu=per_exp_resources_gpu,
                storage_gb=per_exp_resources_storage_gb,
                extra=per_exp_resources_extra,
            ),
            run_controller_command=run_controller_command,
            scratch=[Externalv1ScratchSpace(mount_path=scratch_mount_path, size_gb=scratch_size_gb)],
            source_code=source_code,
            sweep_options=run_sweep_options,
            sweep_type=run_sweep_type,
            use_spot=use_spot,
            auto_resume=auto_resume,
        ),
    )
    return client.run_service_create_run(spec_cluster_id=cluster_id, body=request)


@throw_with_message
def cancel_run(client: GridRestClient, cluster_id: str, run_id: str) -> V1Run:
    run = get_run_from_id(client=client, cluster_id=cluster_id, run_id=run_id)
    run_spec = run.spec
    run_spec.desired_state = V1RunState.CANCELED
    return client.run_service_update_run(
        spec_cluster_id=cluster_id, id=run_id, body=Body8(name=run.name, spec=run_spec)
    )


@throw_with_message
def delete_run(client: GridRestClient, cluster_id: str, run_id: str) -> V1DeleteRunResponse:
    return client.run_service_delete_run(cluster_id=cluster_id, id=run_id)


@throw_with_message
def get_run_from_id(client: GridRestClient, cluster_id: str, run_id: str) -> V1Run:
    return client.run_service_get_run(cluster_id=cluster_id, id=run_id)


@throw_with_message
def get_run_from_name(client: GridRestClient, cluster_id: str, run_name: str) -> V1Run:
    runs = list_runs(client=client, cluster_id=cluster_id)
    for run in runs:
        if run.name == run_name:
            return run
    raise KeyError(f'Run with name {run_name} not found')


@throw_with_message
def list_runs(client: GridRestClient, cluster_id: str, user_ids=None) -> List[V1Run]:
    user_ids = user_ids or []
    phase_not_in = [V1RunState.DELETED]
    resp = client.run_service_list_runs(cluster_id=cluster_id, user_ids=user_ids, phase_not_in=phase_not_in)
    return resp.runs
