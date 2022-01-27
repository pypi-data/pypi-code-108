from collections import defaultdict

from spell.api.models import (
    BatchingConfig,
    ContainerResourceRequirements,
    Environment,
    ModelServerModel,
    ModelServerUpdateRequest,
    PodAutoscaleConfig,
    ResourceRequirement,
)
from spell.shared.dependencies import format_apt_versions, merge_dependencies


def create_pod_autoscale_config(
    min_pods,
    max_pods,
    target_cpu_utilization,
    target_requests_per_second,
    default_min_pods=None,
    default_max_pods=None,
    default_target_cpu_utilization=None,
    default_target_requests_per_second=None,
):
    # All parameters may be None. If None, use the default value.
    pod_autoscale_config = PodAutoscaleConfig(
        min_pods=min_pods if min_pods is not None else default_min_pods,
        max_pods=max_pods if max_pods is not None else default_max_pods,
    )

    if target_cpu_utilization is not None:
        pod_autoscale_config.target_cpu_utilization = int(target_cpu_utilization * 100)
    else:
        pod_autoscale_config.target_cpu_utilization = default_target_cpu_utilization

    if target_requests_per_second is not None:
        pod_autoscale_config.target_avg_requests_per_sec_millicores = int(target_requests_per_second * 1000)
    else:
        pod_autoscale_config.target_avg_requests_per_sec_millicores = default_target_requests_per_second
    return pod_autoscale_config


def create_resource_requirements(
    ram_request,
    cpu_request,
    ram_limit,
    cpu_limit,
    gpu_limit,
    ram_request_default_value=None,
    cpu_request_default_value=None,
    ram_limit_default_value=None,
    cpu_limit_default_value=None,
    gpu_limit_default_value=None,
):
    # All parameters may be None. If so, use the default value.
    resource_request = ResourceRequirement(memory_mebibytes=ram_request or ram_request_default_value)
    if cpu_request is not None:
        resource_request.cpu_millicores = int(cpu_request * 1000)
    else:
        resource_request.cpu_millicores = cpu_request_default_value

    resource_limit = ResourceRequirement(
        memory_mebibytes=ram_limit or ram_limit_default_value, gpu=gpu_limit or gpu_limit_default_value
    )
    if cpu_limit is not None:
        resource_limit.cpu_millicores = int(cpu_limit * 1000)
    else:
        resource_limit.cpu_millicores = cpu_limit_default_value

    return ContainerResourceRequirements(
        resource_request=resource_request,
        resource_limit=resource_limit,
    )


def create_batching_config(
    enable_batching,
    max_batch_size,
    request_timeout,
    enable_batching_default_value=False,
    max_batch_size_default_value=BatchingConfig.DEFAULT_MAX_BATCH_SIZE,
    request_timeout_default_value=BatchingConfig.DEFAULT_REQUEST_TIMEOUT,
):
    # All parameters may be None. If None, use the default value.
    if (enable_batching is True) or (enable_batching is None and enable_batching_default_value is True):
        return BatchingConfig(
            is_enabled=True,
            max_batch_size=max_batch_size or max_batch_size_default_value,
            request_timeout_ms=request_timeout or request_timeout_default_value,
        )
    else:
        return BatchingConfig(is_enabled=False)


def create_environment(python_env_deps, pip_packages, requirements_file, conda_file, apt_packages, envvars):
    python_deps = merge_dependencies(python_env_deps, conda_file, requirements_file, pip_packages).to_payload()
    return Environment(
        pip_env=python_deps["pip_env"],
        requirements_file=python_deps["requirements_file"],
        pip=python_deps["pip"],
        conda_file=python_deps["conda_file"],
        apt=format_apt_versions(apt_packages),
        docker_image=None,
        env_vars=envvars,
    )


def make_modelserver_update_request(**kwargs):
    kwargs = defaultdict(lambda: None, kwargs)
    # All other kwargs accept None as a default except these
    kwargs["pip_packages"] = kwargs["pip_packages"] or []
    kwargs["apt_packages"] = kwargs["apt_packages"] or []
    kwargs["debug"] = kwargs["debug"] or False
    environment = None
    pod_autoscale_config = None
    resource_requirements = None
    if any(
        (
            kwargs["python_env_deps"],
            kwargs["pip_packages"],
            kwargs["requirements_file"],
            kwargs["conda_file"],
            kwargs["apt_packages"],
            kwargs["envvars"],
        )
    ):
        environment = create_environment(
            kwargs["python_env_deps"],
            kwargs["pip_packages"],
            kwargs["requirements_file"],
            kwargs["conda_file"],
            kwargs["apt_packages"],
            kwargs["envvars"],
        )

    if any(
        x is not None
        for x in (
            kwargs["min_pods"],
            kwargs["max_pods"],
            kwargs["target_cpu_utilization"],
            kwargs["target_requests_per_second"],
        )
    ):
        pod_autoscale_config = create_pod_autoscale_config(
            kwargs["min_pods"],
            kwargs["max_pods"],
            kwargs["target_cpu_utilization"],
            kwargs["target_requests_per_second"],
        )

    if any(
        x is not None
        for x in (
            kwargs["ram_request"],
            kwargs["cpu_request"],
            kwargs["ram_limit"],
            kwargs["cpu_limit"],
            kwargs["gpu_limit"],
        )
    ):
        resource_requirements = create_resource_requirements(
            kwargs["ram_request"],
            kwargs["cpu_request"],
            kwargs["ram_limit"],
            kwargs["cpu_limit"],
            kwargs["gpu_limit"],
        )

    new_models = None
    if kwargs["models"] is not None:
        new_models = [ModelServerModel(model_name=m[0], version_id=m[1], version_name=m[2]) for m in kwargs["models"]]
    batching_config = create_batching_config(
        kwargs["batching_flag"], kwargs["max_batch_size"], kwargs["request_timeout"]
    )

    return ModelServerUpdateRequest(
        models=new_models,
        entrypoint=kwargs["entrypoint"],
        config=kwargs["config"],
        node_group=kwargs["node_group"],
        predictor_class=kwargs["classname"],
        environment=environment,
        update_spell_version=kwargs["update_spell_version"],
        attached_resources=kwargs["attached_resources"],
        description=kwargs["description"],
        repository=kwargs["repo"],
        pod_autoscale_config=pod_autoscale_config,
        resource_requirements=resource_requirements,
        num_processes=kwargs["num_processes"],
        batching_config=batching_config,
        debug=kwargs["debug"],
    )
