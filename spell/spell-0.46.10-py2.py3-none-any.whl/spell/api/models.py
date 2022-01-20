import abc
import decimal
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from spell.cli.utils import prettify_timespan
from spell.cli.utils.exceptions import ParseException

from spell.constants import (
    MODEL_SERVER_MAX_BATCH_SIZE_DEFAULT,
    MODEL_SERVER_BATCH_REQUEST_TIMEOUT_DEFAULT,
)

# hyperparameter scaling constants
LINEAR = "linear"
LOG = "log"
REVERSE_LOG = "reverse_log"

# hyperparameter type constants
FLOAT = "float"
INT = "int"


class Model(metaclass=abc.ABCMeta):

    compare_fields = abc.abstractproperty()

    def __eq__(self, other):
        if not hasattr(other, "__dict__"):
            return False
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        other_items = filter(lambda x: x[0] in self.compare_fields, other.__dict__.items())
        return set(my_items) == set(other_items)

    def __hash__(self):
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        return hash(tuple(sorted(my_items)))

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(x, repr(y)) for x, y in self.__dict__.items() if y]),
        )


class User(Model):

    compare_fields = ["email", "user_name", "full_name", "created_at"]

    def __init__(
        self,
        email,
        user_name,
        created_at,
        updated_at,
        is_admin=False,
        full_name=None,
        last_logged_in=None,
        **kwargs,
    ):
        self.email = email
        self.user_name = user_name
        self.full_name = full_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_admin = is_admin
        self.last_logged_in = last_logged_in
        self.memberships = kwargs.get("memberships")


class AccessToken(Model):
    compare_fields = ["name", "created_at"]

    def __init__(self, name, created_at, last_used_at):
        self.name = name
        self.created_at = created_at
        self.last_used_at = last_used_at


class Organization(Model):

    compare_fields = ["name", "created_at"]

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.members = kwargs.get("members", [])
        self.created_at = kwargs["created_at"]
        self.updated_at = kwargs["updated_at"]


class Owner(Model):

    compare_fields = ["name", "type"]

    def __init__(self, name, type, **kwargs):
        self.name = name
        self.type = type
        self.requestor_role = kwargs.get("requestor_role")
        self.permissions = kwargs.get("permissions")
        self.github_username = kwargs.get("github_username")
        self.clusters = kwargs.get("clusters")


class OrgMember(Model):

    compare_fields = ["organization", "user", "role", "created_at"]

    def __init__(self, **kwargs):
        self.organization = kwargs.get("organization")
        self.user = kwargs.get("user")
        self.role = kwargs["role"]
        self.created_at = kwargs["created_at"]
        self.updated_at = kwargs["updated_at"]


class Key(Model):

    compare_fields = ["id", "title", "fingerprint", "created_at"]

    def __init__(self, id, title, fingerprint, verified, created_at, **kwargs):
        self.id = int(id)
        self.title = title
        self.fingerprint = fingerprint
        self.verified = verified
        self.created_at = created_at


class Workspace(Model):

    compare_fields = [
        "id",
        "root_commit",
        "name",
        "description",
        "git_remote_url",
        "creator",
        "created_at",
    ]

    def __init__(
        self,
        id,
        root_commit,
        name,
        description,
        git_remote_url,
        creator,
        created_at,
        updated_at,
        git_commit_hash=None,
        **kwargs,
    ):
        self.id = int(id)
        self.root_commit = root_commit
        self.name = name
        self.description = description
        self.git_remote_url = git_remote_url
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at
        self.git_commit_hash = git_commit_hash


class Run(Model):

    compare_fields = [
        "id",
        "status",
        "command",
        "creator",
        "gpu",
        "git_commit_hash",
        "docker_image",
        "workspace",
        "pip_env_packages",
        "requirements_file",
        "pip_packages",
        "apt_packages",
        "conda_env_file",
        "attached_resources",
        "environment_vars",
        "tensorboard_directory",
        "distributed",
    ]

    def __init__(
        self,
        id,
        status,
        command,
        creator,
        gpu,
        git_commit_hash,
        description,
        docker_image,
        created_at,
        spell_project=None,
        workspace=None,
        pip_env_packages=None,
        requirements_file=None,
        pip_packages=None,
        apt_packages=None,
        conda_env_file=None,
        attached_resources=None,
        environment_vars=None,
        user_exit_code=None,
        started_at=None,
        ended_at=None,
        hyper_params=None,
        github_url=None,
        tensorboard_directory=None,
        distributed=None,
        resumed_as_run=None,
        resumed_from_run=None,
        labels=None,
        **kwargs,
    ):
        self.id = int(id)
        self.status = status
        self.user_exit_code = user_exit_code if user_exit_code is None else int(user_exit_code)
        self.command = command
        self.creator = creator
        self.gpu = gpu
        self.git_commit_hash = git_commit_hash
        self.github_url = github_url
        self.description = description
        self.distributed = distributed
        self.docker_image = docker_image
        self.created_at = created_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.project = spell_project
        self.workspace = workspace
        self.pip_env_packages = pip_env_packages or []
        self.requirements_file = requirements_file
        self.pip_packages = pip_packages or []
        self.apt_packages = apt_packages or []
        self.conda_env_file = conda_env_file
        self.attached_resources = attached_resources or {}
        self.environment_vars = environment_vars or {}
        self.already_existed = False
        self.hyper_params = hyper_params
        self.tensorboard_directory = tensorboard_directory
        self.resumed_as_run = resumed_as_run
        self.resumed_from_run = resumed_from_run
        self.labels = labels or []


class HyperSearch(Model):

    compare_fields = [
        "id",
        "runs",
        "status",
        "command",
        "creator",
        "gpu",
        "parameter_spec",
    ]

    def __init__(
        self,
        id,
        gpu,
        parameter_spec,
        command,
        created_at,
        creator,
        description,
        status=None,
        runs=None,
        started_at=None,
        ended_at=None,
        **kwargs,
    ):
        self.id = int(id)
        self.status = status
        self.runs = runs or []
        self.gpu = gpu
        self.parameter_spec = parameter_spec
        self.command = command
        self.created_at = created_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.creator = creator
        self.description = description


class HyperSearchInfo(Model):

    compare_fields = ["id", "num_runs", "command", "created_at", "creator"]

    def __init__(self, id, num_runs, command, creator, created_at, started_at=None, ended_at=None, **kwargs):
        self.id = int(id)
        self.num_runs = int(num_runs)
        self.command = command
        self.created_at = created_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.creator = creator


class Workflow(Model):

    compare_fields = ["id", "workspace_specs", "run"]

    def __init__(self, id, workspace_specs=None, managing_run=None, runs=None, **kwargs):
        self.id = int(id)
        self.workspace_specs = workspace_specs or {}
        self.managing_run = managing_run
        self.runs = runs or []


class Project(Model):

    compare_fields = [
        "id",
        "name",
        "description",
    ]

    def __init__(
        self,
        id,
        name,
        description,
        creator=None,
        created_at=None,
        updated_at=None,
        total_run_count=0,
        active_run_count=0,
        total_runtime_seconds=0,
        archived_at=None,
        **kwargs,
    ):
        self.id = int(id)
        self.name = name
        self.description = description
        self.total_run_count = total_run_count
        self.active_run_count = active_run_count
        self.total_runtime_seconds = total_runtime_seconds
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at
        self.archived_at = archived_at


class LsLine(Model):

    compare_fields = ["path", "size"]

    def __init__(self, path, size, date=None, additional_info=None, link_target=None, **kwargs):
        self.path = path
        self.size = size
        self.date = date
        self.additional_info = additional_info
        self.link_target = link_target


class LogEntry(Model):

    compare_fields = ["status", "log", "status_event", "level", "timestamp", "important"]

    def __init__(self, status=None, log=None, status_event=None, level=None, important=None, **kwargs):
        self.status = status
        self.log = log
        self.status_event = status_event
        self.level = level
        self.important = important
        self.timestamp = kwargs.get("@timestamp")

    def __str__(self):
        return self.log


class OrgBucket(Model):

    compare_fields = ["name, provider"]

    def __init__(self, name, provider, created_at, **kwargs):
        self.name = name
        self.provider = provider
        self.created_at = created_at


class CPUStats(Model):

    compare_fields = [
        "cpu_percentage",
        "memory",
        "memory_total",
        "memory_percentage",
        "network_rx",
        "network_tx",
        "block_read",
        "block_write",
    ]

    def __init__(
        self,
        cpu_percentage,
        memory,
        memory_total,
        memory_percentage,
        network_rx,
        network_tx,
        block_read,
        block_write,
        **kwargs,
    ):
        self.cpu_percentage = cpu_percentage
        self.memory = memory
        self.memory_total = memory_total
        self.memory_percentage = memory_percentage
        self.network_rx = network_rx
        self.network_tx = network_tx
        self.block_read = block_read
        self.block_write = block_write


class GPUStats(Model):

    compare_fields = [
        "name",
        "temperature",
        "power_draw",
        "power_limit",
        "gpu_utilization",
        "memory_utilization",
        "memory_used",
        "memory_total",
        "perf_state",
    ]

    def __init__(
        self,
        name,
        temperature,
        power_draw,
        power_limit,
        gpu_utilization,
        memory_utilization,
        memory_used,
        memory_total,
        perf_state,
        **kwargs,
    ):
        self.name = name
        self.temperature = temperature
        self.power_draw = power_draw
        self.power_limit = power_limit
        self.gpu_utilization = gpu_utilization
        self.memory_utilization = memory_utilization
        self.memory_used = memory_used
        self.memory_total = memory_total
        self.perf_state = perf_state


class UserDataset(Model):

    compare_fields = ["id", "name", "status", "created_at"]

    def __init__(self, id, name, status, updated_at, created_at, **kwargs):
        self.id = id
        self.name = name
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at


class Template(Model):

    compare_fields = ["body"]

    def __init__(self, body, **kwargs):
        self.body = body


class Error(Model):

    compare_fields = ["status", "error", "code"]

    def __init__(self, status, error, code):
        self.status = status
        self.error = error
        self.code = code

    @staticmethod
    def response_dict_to_object(obj):
        if "status" in obj or "error" in obj or "code" in obj:
            status = obj.get("status", None)
            error = obj.get("error", None)
            code = obj.get("code", None)
            return Error(status, error, code)
        return obj

    def __str__(self):
        if self.error:
            return self.error
        elif self.status:
            return self.status
        else:
            return None


class MachineStats(Model):
    compare_fields = ["machine_type_name", "total", "user_stats", "cost_cents_per_hour"]

    def __init__(self, machine_type_name, total, user_stats, cost_cents_per_hour):
        self.total = Stats(**total)
        self.user_stats = {name: Stats(**s) for name, s in user_stats.items()}
        self.machine_type_name = machine_type_name
        self.cost_cents_per_hour = cost_cents_per_hour


class Stats(Model):
    compare_fields = ["time_used", "cost_used_cents"]

    def __init__(self, time_used, cost_used_cents):
        self.time_used = timedelta(seconds=time_used)
        self.cost_used_usd = decimal.Decimal(cost_used_cents) / 100


def parseNullDate(dt):
    if dt is None:
        return None
    return dt.date()


class BillingStatus(Model):
    compare_fields = [
        "plan_id",
        "plan_name",
        "remaining_credits_usd",
        "period_machine_stats",
        "total_machine_stats",
        "last_machine_invoice_date",
        "total_runs",
        "concurrent_queued_runs",
        "concurrent_run_limit",
        "previous_stripe_billing_date",
        "next_stripe_billing_date",
        "used_credit_usd",
    ]

    def __init__(
        self,
        plan_id,
        plan_name,
        remaining_credit_cents,
        last_machine_invoice_date,
        period_machine_stats,
        total_machine_stats,
        concurrent_queued_runs,
        concurrent_run_limit,
        total_runs,
        previous_stripe_billing_date,
        next_stripe_billing_date,
        used_credit_cents,
        machine_charge_cents,
        total_charge_cents,
        **kwargs,
    ):
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.remaining_credits_usd = decimal.Decimal(remaining_credit_cents) / 100
        self.used_credits_usd = decimal.Decimal(used_credit_cents) / 100
        self.period_machine_stats = [MachineStats(**s) for s in period_machine_stats]
        self.total_machine_stats = [MachineStats(**s) for s in total_machine_stats]
        self.last_machine_invoice_date = parseNullDate(last_machine_invoice_date)
        self.previous_stripe_billing_date = parseNullDate(previous_stripe_billing_date)
        self.next_stripe_billing_date = parseNullDate(next_stripe_billing_date)

        self.total_charge_usd = decimal.Decimal(total_charge_cents) / 100
        self.machine_charge_usd = decimal.Decimal(machine_charge_cents) / 100

        self.total_runs = total_runs
        self.concurrent_queued_runs = concurrent_queued_runs
        self.concurrent_run_limit = concurrent_run_limit


class SpellModel(Model):
    compare_fields = ["id"]

    def __init__(self, id, name, creator, created_at, model_versions, **kwargs):
        self.id = id
        self.name = name
        self.creator = creator
        self.created_at = created_at
        self.model_versions = model_versions


class ModelServerRequestBase(Model):
    """
    A class used to encapsulate all of the specifications of a Model Server

    Keyword arguments:
    entrypoint -- The path to the predictor module
    models -- The models to use
    config -- a YAML/JSON configuration which will be passed to the Predictor
    predictor_class -- name of the Predictor class
    node_group -- node group to assign model server pods to
    pip_packages -- list of pip dependencies to install
    apt_packages -- list of apt dependencies to install
    docker_image -- name of docker image to use as base
    envvars -- environment variables to set
    attached_resources -- resources to mount and the location to mount them at
    repository -- an object of type Repository containing information about the git repository
    debug -- Launch the server in debug mode. For security reasons, this should not be used in production
    resource_requirements -- the limits and requests for the pods
    description -- A desription of the model server
    num_processes -- the number of processes to use for the server
    batching_config -- the configuration for server-side batching
    """

    def __init__(
        self,
        entrypoint=None,
        models=None,
        config=None,
        predictor_class=None,
        node_group=None,
        commit_hash=None,
        description=None,
        environment=None,
        attached_resources=None,
        repository=None,
        pod_autoscale_config=None,
        resource_requirements=None,
        num_processes=None,
        batching_config=None,
        debug=False,
    ):
        self.entrypoint = entrypoint
        self.models = models or []
        self.config = config
        self.predictor_class = predictor_class
        self.node_group = node_group
        self.description = description
        self.environment = environment
        self.attached_resources = (
            {name: {"mount_point": value} for name, value in attached_resources.items()} if attached_resources else None
        )
        self.repository = repository
        self.pod_autoscale_config = pod_autoscale_config
        self.resource_requirements = resource_requirements
        self.num_processes = num_processes
        self.batching_config = batching_config
        self.debug = debug

    def to_payload(self):
        payload = {
            "entrypoint": self.entrypoint,
            "node_group": self.node_group,
            "config": self.config,
            "predictor_class": self.predictor_class,
            "attached_resources": self.attached_resources,
            "description": self.description,
            "debug": self.debug,
            "num_processes": self.num_processes,
        }
        if self.models is not None:
            payload["models"] = [m.to_payload() for m in self.models]
        if self.environment is not None:
            payload["environment"] = self.environment.to_payload()
        if self.repository is not None:
            payload["repository"] = self.repository.to_payload()
        if self.pod_autoscale_config is not None:
            payload["pod_autoscale_config"] = self.pod_autoscale_config.to_payload()
        if self.resource_requirements is not None:
            payload["resource_requirements"] = self.resource_requirements.to_payload()
        if self.batching_config is not None:
            payload["batching_config"] = self.batching_config.to_payload()
        return payload


class ModelServerCreateRequest(ModelServerRequestBase):
    """
    A class used to encapsulate all of the specifications to create a Model Server

    Arguments:
    entrypoint -- The path to the predictor module
    server_name -- name used when displaying the server

    Keyword arguments:
    models -- The models to use
    config -- a YAML/JSON configuration which will be passed to the Predictor
    node_group -- node group to assign model server pods to
    predictor_class -- name of the Predictor class
    environment -- An environment to use in the server
    attached_resources -- resources to mount and the location to mount them at
    repository -- an object of type Repository containing information about the git repository
    pod_autoscale_config -- the configuration for the HPA
    resource_requirements -- the limits and requests for the pods
    debug -- Launch the server in debug mode. For security reasons, this should not be used in production
    description -- A desription of the model server
    num_processes -- the number of processes to use for the server
    batching_config -- the configuration for server-side batching
    """

    # This class only differs from the ModelServerUpdateRequest in its required arguments, and its
    # additional server_name field, but using a base class gives us some type safety.

    compare_fields = ["server_name"]

    def __init__(
        self,
        entrypoint,
        server_name,
        models=None,
        config="",
        predictor_class=None,
        node_group=None,
        commit_hash=None,
        description=None,
        environment=None,
        attached_resources=None,
        repository=None,
        pod_autoscale_config=None,
        resource_requirements=None,
        num_processes=None,
        batching_config=None,
        debug=False,
    ):

        super().__init__(
            entrypoint=entrypoint,
            models=models or [],
            config=config,
            predictor_class=predictor_class,
            node_group=node_group,
            commit_hash=commit_hash,
            description=description,
            environment=environment,
            attached_resources=attached_resources,
            repository=repository,
            pod_autoscale_config=pod_autoscale_config,
            resource_requirements=resource_requirements,
            num_processes=num_processes,
            batching_config=batching_config,
            debug=debug,
        )
        self.server_name = server_name

    def to_payload(self):
        payload = super().to_payload()
        payload["server_name"] = self.server_name
        return payload


class ModelServerUpdateRequest(ModelServerRequestBase):
    """
    A class used to encapsulate all of the specifications to update a Model Server

    Keyword arguments:
    entrypoint -- The path to the predictor module
    models -- The models to use
    server_name -- name used when displaying the server
    config -- a YAML/JSON configuration which will be passed to the Predictor
    predictor_class -- name of the Predictor class
    node_group -- node group to assign model server pods to
    environment -- An environment to use in the server
    update_spell_version -- Update the version of Spell used to run the model server
    attached_resources -- resources to mount and the location to mount them at
    repository -- an object of type Repository containing information about the git repository
    pod_autoscale_config -- the configuration for the HPA
    resource_requirements -- the limits and requests for the pods
    debug -- Launch the server in debug mode. For security reasons, this should not be used in production
    description -- A desription of the model server
    num_processes -- the number of processes to use for the server
    batching_config -- the configuration for server-side batching
    """

    compare_fields = [
        "entrypoint",
        "models",
        "server_name",
        "config",
        "predictor_class",
        "node_group",
        "commit_hash",
        "description",
        "environment",
        "update_spell_version",
        "attached_resources",
        "repository",
        "pod_autoscale_config",
        "resource_requirements",
        "num_processes",
        "batching_config",
        "debug",
    ]

    def __init__(self, update_spell_version=False, **kwargs):
        super().__init__(**kwargs)
        self.update_spell_version = update_spell_version

    def to_payload(self):
        payload = super().to_payload()
        payload["update_spell_version"] = self.update_spell_version
        return payload


class ModelServerModel(Model):
    """
    A class used to encapsulate the specifications of a model to use in a model server

    Keyword arguments:
    model_name -- name of the model to use
    version_id -- id of model version to use
    version_name -- name of model version to use
    """

    compare_fields = ["model_name", "version_id", "version_name"]

    def __init__(self, model_name, version_id=None, version_name=None):
        self.model_name = model_name
        self.version_id = version_id
        self.version_name = version_name

    def to_payload(self):
        return {
            "model_name": self.model_name,
            "version_id": self.version_id,
            "version_name": self.version_name,
        }


class ModelVersion(Model):
    compare_fields = ["id"]

    def __init__(
        self,
        id,
        formatted_version,
        version,
        creator,
        created_at,
        resource,
        files,
        description,
        **kwargs,
    ):
        self.id = id
        self.model_id = kwargs.get("model_id")
        self.model_name = kwargs.get("model_name")
        self.formatted_version = formatted_version
        self.version = version
        self.creator = creator
        self.created_at = created_at
        self.resource = resource
        self.files = [ModelFileSpec(**f) for f in files]
        self.description = description

    @property
    def specifier(self):
        return ":".join((self.model_name, self.formatted_version)) if self.model_name else ""


class PodAutoscaleConfig(Model):
    compare_fields = [
        "min_pods",
        "max_pods",
        "target_cpu_utilization",
        "target_avg_requests_per_sec_millicores",
    ]

    def __init__(
        self,
        min_pods,
        max_pods,
        target_cpu_utilization=None,
        target_avg_requests_per_sec_millicores=None,
        **kwargs,
    ):
        self.min_pods = min_pods
        self.max_pods = max_pods
        self.target_cpu_utilization = target_cpu_utilization
        self.target_avg_requests_per_sec_millicores = target_avg_requests_per_sec_millicores

    def to_payload(self):
        return {
            "min_pods": self.min_pods,
            "max_pods": self.max_pods,
            "target_cpu_utilization": self.target_cpu_utilization,
            "target_avg_requests_per_sec_millicores": self.target_avg_requests_per_sec_millicores,
        }


class ContainerResourceRequirements(Model):
    compare_fields = ["request", "limit"]

    def __init__(self, resource_request=None, resource_limit=None, **kwargs):
        self.request = resource_request
        self.limit = resource_limit

    def to_payload(self):
        return {
            "resource_request": self.request.to_payload(),
            "resource_limit": self.limit.to_payload(),
        }


class ResourceRequirement(Model):
    compare_fields = ["memory_mebibytes", "cpu_millicores", "gpu"]

    def __init__(self, memory_mebibytes=None, cpu_millicores=None, gpu=None, **kwargs):
        self.memory_mebibytes = memory_mebibytes
        self.cpu_millicores = cpu_millicores
        self.gpu = gpu

    def to_payload(self):
        return {
            "memory_mebibytes": self.memory_mebibytes,
            "cpu_millicores": self.cpu_millicores,
            "gpu": self.gpu,
        }


class ModelServerPod(Model):
    compare_fields = ["id"]

    def __init__(self, id, created_at, ready_at=None, deleted_at=None, **kwargs):
        self.id = id
        self.created_at = created_at
        self.ready_at = ready_at
        self.deleted_at = deleted_at


class BatchingConfig(Model):
    DEFAULT_MAX_BATCH_SIZE = MODEL_SERVER_MAX_BATCH_SIZE_DEFAULT
    DEFAULT_REQUEST_TIMEOUT = MODEL_SERVER_BATCH_REQUEST_TIMEOUT_DEFAULT
    compare_fields = ["is_enabled", "max_batch_size", "request_timeout_ms"]

    def __init__(self, max_batch_size=None, request_timeout_ms=None, is_enabled=False, **kwargs):
        self.is_enabled = is_enabled
        self.max_batch_size = max_batch_size
        self.request_timeout_ms = request_timeout_ms

    def to_payload(self):
        return {
            "is_enabled": self.is_enabled,
            "max_batch_size": self.max_batch_size,
            "request_timeout_ms": self.request_timeout_ms,
        }


class ModelServer(Model):
    compare_fields = [
        "id",
        "server_name",
        "state",
        "created_at",
        "updated_at",
        "url",
        "auth_token",
    ]

    def __init__(
        self,
        id,
        server_name,
        status,
        url,
        created_at,
        updated_at,
        cluster=None,
        model_versions=None,
        entrypoint=None,
        config=None,
        predictor_class=None,
        debug=False,
        git_commit_hash=None,
        has_uncommitted=None,
        github_url=None,
        workspace=None,
        request_limits=None,
        model_server_pods=None,
        node_group_name=None,
        creator=None,
        resource_requirements=None,
        pod_autoscale_config=None,
        additional_resources=None,
        num_processes=None,
        batching_config=None,
        environment=None,
        kubernetes_name=None,
        **kwargs,
    ):
        self.id = id
        self.server_name = server_name
        self.status = status
        self.url = url
        self.kubernetes_name = kubernetes_name
        self.pods = model_server_pods
        self.cluster = cluster
        self.created_at = created_at
        self.updated_at = updated_at
        self.model_versions = model_versions
        self.entrypoint = entrypoint
        self.config = config
        self.predictor_class = predictor_class
        self.debug = debug
        self.git_commit_hash = git_commit_hash
        self.has_uncommitted = has_uncommitted
        self.github_url = github_url
        self.workspace = workspace
        self.request_limits = request_limits
        self.node_group_name = node_group_name
        self.creator = creator
        self.resource_requirements = resource_requirements
        self.pod_autoscale_config = pod_autoscale_config
        self.additional_resources = additional_resources or {}
        self.environment = environment
        self.num_processes = num_processes
        self.batching_config = batching_config

    def get_age(self):
        if self.status != "running":
            return "--"
        return prettify_timespan(self.updated_at, datetime.now(tzutc()))


class ModelServerLogEntry(Model):

    compare_fields = ["log"]

    def __init__(self, log=None, **kwargs):
        self.log = log

    def __str__(self):
        return self.log


class NodeGroup(Model):

    compare_fields = ["id", "name"]

    def __init__(
        self,
        id,
        name,
        instance_type,
        accelerators,
        is_spot,
        disk_size_gb,
        min_nodes,
        max_nodes,
        config,
        is_default,
        model_servers,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.instance_type = instance_type
        self.accelerators = accelerators
        self.is_spot = is_spot
        self.disk_size_gb = disk_size_gb
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.config = config
        self.is_default = is_default
        self.model_servers = model_servers


class NameVersionPair(Model):

    compare_fields = ["name", "version"]

    def __init__(self, name, version=None, **kwargs):
        self.name = name
        self.version = version

    def to_payload(self):
        return {
            "name": self.name,
            "version": self.version,
        }

    def __str__(self):
        ret = self.name
        if self.version:
            ret += "=={}".format(self.version)
        return ret


class Environment(Model):
    # TODO(Justin): In process of deprecation. pip_strings and pip_env_strings should be removed after 0.47.0

    compare_fields = [
        "apt",
        "conda_file",
        "pip_env",
        "requirements_file",
        "pip",
        "env_vars",
        "docker_image",
        "pip_strings",
        "pip_env_strings",
    ]

    def __init__(
        self,
        apt=None,
        conda_file=None,
        pip_env=None,
        requirements_file=None,
        pip=None,
        env_vars=None,
        docker_image=None,
        pip_strings=None,
        pip_env_strings=None,
        **kwargs,
    ):
        self.apt = [NameVersionPair(**package) for package in apt] if apt else None
        self.conda_file = conda_file
        self.pip_env = [NameVersionPair(**package) for package in pip_env] if pip_env else None
        self.pip_env_strings = pip_env_strings
        self.requirements_file = requirements_file
        self.pip = [NameVersionPair(**package) for package in pip] if pip else None
        self.pip_strings = pip_strings
        self.env_vars = env_vars
        self.docker_image = docker_image

    def to_payload(self):
        return {
            "apt": self.apt,
            "conda_env_file": self.conda_file,
            "pip_env": self.pip_env,
            "requirements_file": self.requirements_file,
            "pip": self.pip,
            "env_vars": self.env_vars,
            "docker_image": self.docker_image,
            "pip_strings": self.pip_strings,
            "pip_env_strings": self.pip_env_strings,
        }


class RunRequest:
    """
    A class used to encapsulate all of the specifications of a Run

    Keyword arguments:
    machine_type -- which machine_type to use for the actual run (classic runs only)
    node_group -- which node_group to use for the actual run (k8s only)
    command -- the command to run on this workspaces
    workspace_id -- the id of the workspace for this repo
    workspace_remote_url -- the users remote of this repo if it exists
    commit_hash -- the current commit hash on the repo to run
    commit_label -- the commit label for the workspace/commit hash, if the run is associated with a workflow
    cwd -- the current working directory that the user ran this cmd in
    root_directory -- the name of the top level directory for the git repository
    conda_file -- contents of conda environment.yml
    pip_env_packages -- list of pip dependencies in the current Python environment to install
    requirements_file -- contents of a requirements.txt file to install
    pip_packages -- list of pip dependencies to install
    apt_packages -- list of apt dependencies to install
    docker_image -- name of docker image to use as base
    tensorboard_directory -- indicates which directory tensorboard files will be written to
    attached_resources -- ids and mount points of runs to attach
    description -- a human readable description of this run
    labels -- labels to apply to the run
    envvars -- environment variables to set
    run_type -- type of run
    idempotent -- should we use an existing identical run
    provider -- if specified only machines from that provider will be used, e.g. aws
    local_root -- Used for jupyter runs
    workflow_id -- ID of the workflow to associate this run to
    github_url -- the url of a GitHub repository
    github_ref -- commit hash, branch, or tag of the repository to pull
    distributed -- the number of machines to create for the distributed run
    uncommitted_hash -- the commit hash of the uncommitted changes to run
    auto_resume -- boolean to enable (or disable) auto resume. Passing None will default to the machine type's default
    timeout - minutes after which if the run is still running we will stop it and save any outputs
    params - dict of names with values that are subsituted for :NAME: in the command
    """

    def __init__(
        self,
        machine_type="CPU",
        node_group=None,
        command=None,
        workspace_id=None,
        workspace_remote_url=None,
        commit_hash=None,
        commit_label=None,
        cwd=None,
        root_directory=None,
        conda_file=None,
        pip_env_packages=None,
        requirements_file=None,
        pip_packages=None,
        apt_packages=None,
        docker_image=None,
        tensorboard_directory=None,
        attached_resources=None,
        description=None,
        envvars=None,
        run_type="user",
        idempotent=False,
        timeout=None,
        provider=None,
        local_root=None,
        workflow_id=None,
        github_url=None,
        github_ref=None,
        distributed=None,
        stop_conditions=None,
        uncommitted_hash=None,
        labels=None,
        auto_resume=None,
        project_id=None,
        params=None,
    ):
        self.machine_type = machine_type
        self.node_group = node_group
        self.command = command
        self.workspace_id = workspace_id
        self.workspace_remote_url = workspace_remote_url
        self.commit_hash = commit_hash
        self.uncommitted_hash = uncommitted_hash
        self.commit_label = commit_label
        self.cwd = cwd
        self.root_directory = root_directory
        self.conda_file = conda_file
        self.pip_env_packages = pip_env_packages
        self.requirements_file = requirements_file
        self.pip_packages = pip_packages
        self.apt_packages = apt_packages
        self.docker_image = docker_image
        self.tensorboard_directory = tensorboard_directory
        self.description = description
        self.labels = labels
        self.envvars = envvars
        self.attached_resources = (
            {name: {"mount_point": attached_resources[name]} for name in attached_resources}
            if attached_resources
            else None
        )
        self.run_type = run_type
        self.idempotent = idempotent
        self.provider = provider
        self.local_root = local_root
        self.workflow_id = workflow_id
        self.github_url = github_url
        self.github_ref = github_ref
        self.distributed = distributed
        self.stop_conditions = stop_conditions
        self.auto_resume = auto_resume
        self.project_id = project_id
        self.timeout = timeout
        self.params = params

    def to_payload(self):
        return {
            "command": self.command,
            "workspace_id": self.workspace_id,
            "workspace_remote_url": self.workspace_remote_url,
            "gpu": self.machine_type,
            "node_group": self.node_group,
            "conda_file": self.conda_file,
            "pip_env_packages": self.pip_env_packages if self.pip_env_packages is not None else [],
            "requirements_file": self.requirements_file,
            "pip_packages": self.pip_packages if self.pip_packages is not None else [],
            "apt_packages": self.apt_packages if self.apt_packages is not None else [],
            "docker_image": self.docker_image,
            "git_commit_hash": self.commit_hash,
            "uncommitted_hash": self.uncommitted_hash,
            "description": self.description,
            "labels": self.labels,
            "environment_vars": self.envvars,
            "attached_resources": self.attached_resources,
            "run_type": self.run_type,
            "cwd": self.cwd,
            "root_directory": self.root_directory,
            "idempotent": self.idempotent,
            "provider": self.provider,
            "workflow_id": self.workflow_id,
            "commit_label": self.commit_label,
            "github_url": self.github_url,
            "github_ref": self.github_ref,
            "tensorboard_directory": self.tensorboard_directory,
            "distributed": self.distributed,
            "stop_conditions": self.stop_conditions,
            "timeout_minutes": self.timeout,
            "auto_resume": self.auto_resume,
            "project_id": self.project_id,
            "params": self.params,
        }


class RangeSpec:
    """A range parameter specification for hyperparameter search

    Attributes:
        min (:obj:`int` or :obj:`float`): the minimum value for the hyperparameter range
        max (:obj:`int` or :obj:`float`): the maximum value for the hyperparameter range
        scaling (:obj:`str`, optional): the scaling for the hyperparameter. Allowed values are
            :py:attr:`~HyperService.LINEAR`, :py:attr:`~HyperService.LOG`,
            :py:attr:`~HyperService.REVERSE_LOG`
        type (:obj:`str`, optional): the type for the hyperparameter. Allowed values are
            :py:attr:`~HyperService.INT`, :py:attr:`~HyperService.FLOAT`
    """

    def __init__(self, min, max, scaling=LINEAR, type=FLOAT):
        self.min = min
        self.max = max
        self.scaling = scaling
        self.type = type

    def to_payload(self):
        return {
            "min": self.min,
            "max": self.max,
            "scaling": self.scaling,
            "type": self.type,
        }


class ValueSpec:
    """A value parameter specification for hyperparameter search

    Attributes:
        values (:obj:`list` of :obj:`float`, :obj:`int`, or :obj:`str`): discrete values for
            this hyperparameter.
    """

    def __init__(self, values):
        self.values = values

    def to_payload(self):
        return {"values": self.values}


class StopConditions:
    """This takes a list of lists of ConditionSpecs. The outer lists are ORed together
    and the inner are ANDed together
    """

    def __init__(self, stop_conditions):
        self.stop_conditions = stop_conditions

    def __eq__(self, other):
        return self.stop_conditions == other.stop_conditions

    def to_payload(self):
        return [[c.to_payload() for c in condition_specs] for condition_specs in self.stop_conditions]


class ConditionSpecs:
    def __init__(self, metric, operator, value, min_indices):
        self.metric = metric
        self.operator = operator
        self.value = value
        self.min_indices = min_indices

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_payload(self):
        return {
            "metric": self.metric,
            "operator": self.operator,
            "value": self.value,
            "min_indices": self.min_indices,
        }


class ModelFileSpec:
    """A class for files to include in a model

    Attributes:
        resource_path (:obj:`str`): A path to a file/folder within a Spell FS resource
        destination_path (:obj:`str`): A path to mount this file/folder at within any future model server
        is_dir (:obj:`bool`): Indicates whether this is a directory or single file
    """

    def __init__(self, resource_path, destination_path, is_dir=None):
        self.resource_path = resource_path
        self.destination_path = destination_path
        self.is_dir = is_dir

    @classmethod
    def from_string(cls, raw_string):
        resource_path, _, destination_path = raw_string.partition(":")
        if ":" in destination_path:
            raise ParseException("Invalid file argument", raw_string)
        return cls(resource_path, destination_path or None)

    def to_payload(self):
        payload = {
            "resource_path": self.resource_path,
            "destination_path": self.destination_path,
        }
        if self.is_dir is not None:
            payload["is_dir"] = self.is_dir
        return payload


class Repository(Model):
    compare_fields = [
        "github_url",
        "github_ref",
        "local_root",
        "workspace_id",
        "workspace_remote_url",
        "commit_hash",
        "uncommitted_hash",
        "relative_path",
        "root_directory",
        "description",
    ]

    def __init__(
        self,
        local_root=None,
        workspace_id=None,
        workspace_remote_url=None,
        commit_hash=None,
        uncommitted_hash=None,
        relative_path=None,
        root_directory=None,
        description=None,
        github_url=None,
        github_ref=None,
    ):
        self.local_root = local_root
        self.workspace_id = workspace_id
        self.workspace_remote_url = workspace_remote_url
        self.commit_hash = commit_hash
        self.relative_path = relative_path
        self.root_directory = root_directory
        self.description = description
        self.uncommitted_hash = uncommitted_hash
        self.github_url = github_url
        self.github_ref = github_ref

    def has_github(self):
        return self.github_url is not None

    def to_payload(self):
        return {
            "local_root": self.local_root,
            "workspace_id": self.workspace_id,
            "workspace_remote_url": self.workspace_remote_url,
            "commit_hash": self.commit_hash,
            "relative_path": self.relative_path,
            "root_directory": self.root_directory,
            "description": self.description,
            "uncommitted_hash": self.uncommitted_hash,
            "github_url": self.github_url,
            "github_ref": self.github_ref,
        }
