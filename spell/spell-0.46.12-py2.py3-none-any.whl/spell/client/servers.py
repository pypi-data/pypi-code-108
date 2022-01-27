import requests

from spell.client.model import SpellModel
from spell.client.models import ModelVersion

from spell.shared.servers import (
    create_batching_config,
    create_environment,
    create_pod_autoscale_config,
    create_resource_requirements,
    make_modelserver_update_request,
)

from spell.api.models import ModelServerCreateRequest, ModelServerModel, Repository
from spell.shared.parse_utils import parse_model_versions


class ModelServersService:
    """A class for managing Spell model servers."""

    def __init__(self, client):
        self.client = client

    #: str : a constant for the "requested" state
    REQUESTED = "requested"
    #: str : a constant for the "created" state
    CREATED = "created"
    #: str : a constant for the "starting" state
    STARTING = "starting"
    #: str : a constant for the "updating" state
    UPDATING = "updating"
    #: str : a constant for the "running" state
    RUNNING = "running"
    #: str : a constant for the "stopping" state
    STOPPING = "stopping"
    #: str : a constant for the "stopped" state
    STOPPED = "stopped"
    #: str : a constant for the "failing" state
    FAILING = "failing"
    #: str : a constant for the "failed" state
    FAILED = "failed"

    def list(self):
        """Lists model servers.

        Parameters:
            name (str): Model server name

        Returns:
            A :obj:`list` of :py:class:`ModelServer` objects.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        model_servers = self.client.api.get_model_servers()
        model_servers = [ModelServer(self.client.api, server) for server in model_servers]
        return model_servers

    def get(self, name):
        """Get a model server.

        Parameters:
            name (str): model server name

        Returns:
            A :py:class:`ModelServer`.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        model_server = self.client.api.get_model_server(name)
        return ModelServer(self.client.api, model_server)

    def rm(self, name):
        """Remove a model server.

        Parameters:
            name (str): Model server name

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self.client.api.delete_model_server(name)

    def serve(self, entrypoint, github_url, **kwargs):
        """
        Create a new model server using a model.

        Parameters:
            entrypoint (str): Path to the file to be used as the model server entrypoint, e.g.
                ``serve.py`` or similar.
            github_url (str): a GitHub URL to a repository for code to include in the server.
            models (:obj:`list` of :obj:`str`, optional): Targeted models,
                each model should be in ``MODEL:VERSION`` format
            github_ref (str, optional): a reference to a commit, branch, or tag in the repository
                corresponding to ``github_url`` for code to include in the run
                (default: ``master``).
            commit_ref (str, optional): git commit hash to use (default: ``HEAD``).
            name (str, optional): Name of the model server. Defaults to the model name.
            node_group (str, optional): Name of the node group to serve from. Defaults to the
                default node group.
            classname (str, optional): Name of the ``Predictor`` class. Only required if more then
                one predictor exists in the entrypoint.
            pip_packages (:obj:`list` of :obj:`str`, optional): pip dependencies (default:
                ``None``). For example: ``["moviepy", "scikit-image"]``.
            requirements_file (str, optional): a path to a pip requirements file.
            conda_file (str, optional): a path to a conda environment file.
            apt_packages (:obj:`list` of :obj:`str`, optional): apt dependencies (default:
                ``None``). For example: ``["python-tk", "ffmpeg"]``
            envvars (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): name to value mapping of
                environment variables for the server (default: ``None``).
            attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): resource name
                to mountpoint mapping of attached resouces for the run (default: ``None``). For
                example: ``{"runs/42" : "/mnt/data"}``
            resource_requirements (:obj:`dict` of :obj:`str` -> :obj:`str`, optional):
                configuration mapping for node resource requirements: CPU, GPU, RAM, etcetera.
                Has sane default values.
            num_processes (:obj:`int`): The number of processes to run the model server on. By
                default this is ``(2 * numberOfCores) + 1``, or equal to the available GPUs if
                applicable.
            pod_autoscale_config (:obj:`dict` of :obj:`str` -> :obj:`str`, optional):
                configuration mapping for pod autoscaling: ``min_pods``, ``max_pods``,
                ``target_cpu_utilization``, ``target_requests_per_second``. Has sane default
                values.
            enable_batching (:obj:`bool`, optional): Whether or not to enable model server
                batching. Defaults to ``False``.
            batching_config (:obj:`dict` of :obj:`str` -> :obj:`int`, optional): If model server
                batching is enabled, the values passed to this parameter are used to configure it.
                If left empty, the default batching parameter values will be used. Has two keys:
                ``max_batch_size`` and ``request_timeout``.
            description: (:obj:`str`, optional): Model server description, defaults to ``None``.
            debug (:obj:`bool`, optional): Launches the model server in debug mode. Should not be
                used in production.

        Returns:
            A :py:class:`ModelServer`.

        Raises:
             :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        models = parse_model_versions(kwargs["models"]) if kwargs["models"] else []
        if kwargs["name"] is None:
            if len(models) == 0:
                raise ValueError("A server name must be provided with name parameter if not using a model")
            elif len(models) == 1:
                kwargs["name"] = models[0][0]
            else:
                raise ValueError("A server name must be provided with name parameter when using multiple models")

        create_request_environment = create_environment(
            None,
            kwargs.get("pip_packages", []),
            kwargs.get("requirements_file", None),
            kwargs.get("conda_file", None),
            kwargs.get("apt_packages", []),
            kwargs.get("envvars", None),
        )

        pod_autoscale_config = kwargs.get("pod_autoscale_config", {})
        pod_autoscale_config = create_pod_autoscale_config(
            pod_autoscale_config.get("min_pods", None),
            pod_autoscale_config.get("max_pods", None),
            pod_autoscale_config.get("target_cpu_utilization", None),
            pod_autoscale_config.get("target_requests_per_second", None),
        )
        resource_requirements = kwargs.get("resource_requirements", {})
        resource_requirements = create_resource_requirements(
            resource_requirements.get("ram_request", None),
            resource_requirements.get("cpu_request", None),
            resource_requirements.get("ram_limit", None),
            resource_requirements.get("cpu_limit", None),
            resource_requirements.get("gpu_limit", None),
        )

        batching_config = kwargs.get("batching_config", {})
        batching_config = create_batching_config(
            enable_batching=kwargs.get("enable_batching", None),
            max_batch_size=batching_config.get("max_batch_size", None),
            request_timeout=batching_config.get("request_timeout", None),
        )

        repository = Repository(
            github_url=github_url,
            commit_hash=kwargs.get("commit_hash", "HEAD"),
            github_ref=kwargs.get("github_ref", None),
        )

        create_request = ModelServerCreateRequest(
            entrypoint,
            kwargs["name"],
            models=[ModelServerModel(model_name=m[0], version_id=m[1], version_name=m[2]) for m in models],
            repository=repository,
            environment=create_request_environment,
            batching_config=batching_config,
            predictor_class=kwargs.get("classname", None),
            node_group=kwargs.get("node_group", None),
            description=kwargs.get("description", None),
            attached_resources=kwargs.get("attached_resources", None),
            pod_autoscale_config=kwargs.get("pod_autoscale_config", None),
            resource_requirements=kwargs.get("resource_requirements", None),
            num_processes=kwargs.get("num_processes", None),
            debug=kwargs.get("debug", False),
        )
        model_server = self.client.api.new_model_server(create_request)
        return ModelServer(self.client.api, model_server)


class ModelServer(SpellModel):
    """Object representing a Spell model server.

    Attributes:
        id (int): Model server id
        server_name (str): Model server name
        status (str): Model server status (e.g. ``Running``, ``Stopped``)
        url (str): Model server endpoint URL
        created_at (datetime.datetime): Model server creation timestamp
        updated_at (datetime.datetime): Timestamp for the last time an action was performed on
            this server.
        cluster (dict): Model serving cluster configuration details such as provider, region,
            subnet, and cloud provider credentials.
        model_versions (list of ModelVersion): A list of :py:class:`~spell.client.models.ModelVersion` object
            containing information on the models being served. See the corresponding docs for more
            information.
        entrypoint (str): The model server entrypoint (e.g. ``serve.py``).
        workspace (dict): Details describing the git repository the model server was launched
            from.
        git_commit_hash (str): Commit hash fingerprinting the version of the code this server
            is running.
        pods (list of ``ModelServerPod``): Lists current and historic Kubernetes pods that served
            or are serving this server.
        creator (``User``): The Spell user who created this model server initially.
        resource_requirements (``ContainerResourceRequirements``): The resource requirements and
            limits currently set for this model server. To learn more refer to the model server
            documentation.
        pod_autoscale_config (``PodAutoscaleConfig``): A mapping of server performance
            configuration values: ``min_pods``, ``max_pods``, ``target_cpu_utilization``,
            ``target_requests_per_second``.
        additional_resources (list of ``Resource``): Lists additional files (besides the model)
            attached to this model server.
        batching_config (``BatchingConfig``): Batching configuration details. Refer to the
            corresponding section of the docs for more information.
        environment (``Environment``): A mapping of additional ``pip`` and ``apt`` dependencies
            installed onto this model server.
    """

    model = "model_server"

    def __init__(self, api, model_server):
        self._api = api
        self.model_server = model_server

    def __set_from_model_server_object(self, api, model_server):
        model_server.model_versions = [ModelVersion(api, m) for m in model_server.model_versions]
        self.model_server = model_server

    def stop(self):
        """Stops the model server.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.stop_model_server(self.model_server.server_name)

    def start(self):
        """Starts the model server.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.start_model_server(self.model_server.server_name)

    def update(self, **kwargs):
        """Updates the model server.

        Parameters:
            models (:obj: `list` of :obj:`str`, optional): Targeted models, should be in ``MODEL:VERSION`` format
            entrypoint (str, optional): Path to the file to be used as the model server
                entrypoint, e.g. ``serve.py`` or similar.
            github_url (str, optional): a GitHub URL to a repository for code to include in the
                server.
            github_ref (str, optional): a reference to a commit, branch, or tag in the repository
                corresponding to the ``github_url`` for code to include in the run (default:
                ``master``).
            commit_ref (str, optional): git commit hash to use (default: ``HEAD``).
            node_group (str, optional): Name of the node group to serve from. Defaults to the
                default node group.
            classname (str, optional): Name of the ``Predictor`` class. Only required if more then
                one predictor exists in the entrypoint.
            pip_packages (:obj:`list` of :obj:`str`, optional): pip dependencies (default:
                ``None``). For example: ``["moviepy", "scikit-image"]``.
            requirements_file (str, optional): a path to a requirements file
            conda_file (str, optional): a path to a conda environment file
            apt_packages (:obj:`list` of :obj:`str`, optional): apt dependencies (default:
                ``None``). For example: ``["python-tk", "ffmpeg"]``
            envvars (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): name to value mapping of
                environment variables for the server (default: ``None``).
            attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): resource name
                to mountpoint mapping of attached resouces for the run (default: ``None``). For
                example: ``{"runs/42" : "/mnt/data"}``
            resource_requirements (:obj:`dict` of :obj:`str` -> :obj:`str`, optional):
                Configuration mapping for node resource requirements: ``cpu_limit``,
                ``cpu_request``, ``ram_limit``, ``ram_request``, ``gpu_limit``. Has sane default
                values.
            num_processes (:obj:`int`): The number of processes to run the model server on. By
                default this is ``(2 * numberOfCores) + 1`` or equal to the available GPUs if
                applicable.
            pod_autoscale_config (:obj:`dict` of :obj:`str` -> :obj:`str`, optional):
                configuration mapping for pod autoscaling: ``min_pods``, ``max_pods``,
                ``target_cpu_utilization``, ``target_requests_per_second``. Has sane default
                values.
            enable_batching (:obj:`bool`, optional): Whether or not to enable model server
                batching. Defaults to ``False``.
            batching_config (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): If model server
                batching is enabled, the values passed to this parameter are used
                to configure it: ``max_batch_size``, ``request_timeout``.
                If left empty, the default batching parameter values will be used.
            debug (:obj:`bool`, optional): Launches the model server in debug mode. Should not be
                used in production.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        if not kwargs:
            raise ValueError("At least one parameter must be specified to update a model server")
        # TODO(Justin): Should validate attached resources like we do in the CLI
        kwargs["models"] = parse_model_versions(kwargs["models"]) if kwargs["models"] is not None else None
        if "github_url" in kwargs or "github_ref" in kwargs:
            kwargs["repo"] = Repository(
                github_url=kwargs.get("github_url", self.model_server.github_url),
                commit_hash=kwargs.get("github_ref", "HEAD"),
            )
        # To match the kwargs from the CLI
        kwargs["batching_flag"] = kwargs.get("enable_batching", None)
        for key in ("resource_requirements", "pod_autoscale_config", "batching_config"):
            kwargs.update(kwargs.get(key, {}))
        update_request = make_modelserver_update_request(**kwargs)
        self._api.update_model_server(self.model_server.server_name, update_request)
        if kwargs["models"] == []:
            self._api.delete_model_server_models(self.model_server.server_name)

    def refresh(self):
        """Refresh the model server state.

        Refresh all of the server attributes with the latest information for the server
        from Spell.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occurred.
        """
        model_server = self._api.get_model_server(self.model_server.server_name)
        self.__set_from_model_server_object(self._api, model_server)

    def logs(self, pod, follow=False, offset=None):
        """Get long entries for a model server.

        Parameters:
            pod (int): the ID of the pod to get logs for. For a list of pods for this model
                server (and their associated IDs) refer to the attribute ``pods``.
            follow (bool, optional): follow the log lines until the server reaches a final
                status (default: ``False``).
            offset (int, optional): which log line to start from. Note that this value, if set,
                must be a positive integer value (default: ``None``).
        """
        if offset is not None and (not isinstance(offset, int) or offset < 0):
            raise ValueError(f"Expected 'offset' to be a positive integer or None, but got {offset} instead.")
        for idx, line in enumerate(
            self._api.get_model_server_log_entries(self.model_server.server_name, pod, follow=follow)
        ):
            if offset and idx < offset:
                continue
            yield line

    def predict(self, payload, **kwargs):
        """Query the model server HTTPS endpoint.

        Parameters:
            payload (dict): a JSON serializable dictionary containing query parameters understood
                by your model server.
            **kwargs: additional keyword arguments to be passed to ``requests.post``.

        Returns:
            ``requests.Response``: the server response.

        Raises:
            ``requests.exceptions.RequestException``: an error occurred.
        """
        return requests.post(
            self.url, json=payload, headers=kwargs.get("headers", {"Content-Type": "application/json"}), **kwargs
        )

    def healthcheck(self, **kwargs):
        """Query the model server HTTPS health check endpoint.

        Parameters:
            **kwargs: additional keyword arguments to be passed to ``requests.get``. For eaxmple,
            the ``timeout`` parameter may be helpful for the case that the server request hangs.

        Returns:
            ``requests.Response``: the server response. Use the ``ok`` field, ``status_code``
            field, or ``raise_for_status`` object method to verify server health.

        Raises:
            ``requests.exceptions.RequestException``: an error occurred.
        """
        # NOTE(aleksey): the model server healthcheck endpoint is a GET endpoint. The HTTP
        # specification states that GET requests must not contain a payload, and the requests API
        # conforms to this specification. As a result, this API does not take healthcheck params.
        healthcheck = self.url[: -len("predict")] + "health"
        return requests.get(healthcheck, headers=kwargs.get("headers", {"Content-Type": "application/json"}))

    def list_metrics(self):
        return self._api.list_model_server_metric_names(self.model_server.server_name)

    def metrics(self, metric_name, follow=False, start=None):
        """Get a server metric. Metrics are sorted by tag.

        Args:
            metric_name (str): the name of the metric being fetched.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        return self._api.get_model_server_metric(self.model_server.server_name, metric_name)

    def wait_status(self, *statuses):
        """Wait until the model server achieves one of the given statuses and then return.

        Args:
            *statuses (required): variable length list of statuses to wait for. Allowed values are
                :py:attr:`~ModelServersService.REQUESTED`, :py:attr:`~ModelServersService.CREATED`,
                :py:attr:`~ModelServersService.STARTING`, :py:attr:`~ModelServersService.UPDATING`,
                :py:attr:`~ModelServersService.RUNNING`, :py:attr:`~ModelServersService.STOPPING`,
                :py:attr:`~ModelServersService.STOPPED`, :py:attr:`~ModelServersService.FAILING`,
                :py:attr:`~ModelServersService.FAILED`,

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occurs.
        """
        return self._api.wait_model_server_status(self.model_server.server_name, *statuses)
