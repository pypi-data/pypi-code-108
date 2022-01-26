import os
import stat
from spell.api.exceptions import ClientException

from spell.client.model import SpellModel
from spell.client.workspaces import Workspace

from spell.shared.dependencies import get_run_request
from spell.shared.projects import get_project_by_name


class RunsService:
    """An object for managing Spell runs."""

    def __init__(self, client):
        self.client = client

    def new(self, **kwargs):
        """Create a run.

        Args:
            command (str): the command to run
            machine_type (str, optional): the machine type for the run (default: CPU)
            project (str, optional): the name of the project to associate this run with (default: None)
            description (str, optional): a description for the run (default: None)
            github_url (str, optional): a GitHub URL to a repository for code to include in the run. Not applicable
                when :obj:`workspace_id` or :obj:`commit_label` is specified.
            github_ref (str, optional): a reference to a commit, branch, or tag in the repository corresponding to
                :obj:`github_url` for code to include in the run (default: ``master``)
            pip_packages (:obj:`list` of :obj:`str`, optional): pip dependencies (default: None).
                For example: ``["moviepy", "scikit-image"]``
            requirements_file (str, optional): a path to a ``requirements.txt`` file
            apt_packages (:obj:`list` of :obj:`str`, optional): apt dependencies (default: None).
                For example: ``["python-tk", "ffmpeg"]``
            conda_file (str, optional): the path to a conda environment specification file (default: None)
            envvars (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): name to value mapping of
                environment variables to be set within the the run (default: None).
                For example: ``{"VARIABLE" : "VALUE", "LANG" : "C.UTF-8"}``
            docker_image (str, optional): the name of docker image to use as base (default: None)
            attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): resource name to mountpoint
                mapping of attached resouces for the run (default: None).
                For example: ``{"runs/42" : "/mnt/data"}``
            labels (:obj:`list` of :obj:`str`, optional): a list of labels to assign to the run
            cwd (str, optional): the working directory within the repository in which to execute the command. If
                ``github_url`` is not set, the run will default to the root directory of the run, ``/spell/``. If
                ``github_url`` is set, the run will default to the root of the repository.
            tensorboard_directory(str, optional): the path where tensorboard files will be read from. The Tensorboard
                integration will not be activated if this parameter is not set.
            distributed(int, optional): executes this run in distributed mode on ``N`` machines of the specified
                ``machine_type``
            idempotent (bool, optional): use an existing identical run if available in lieu of re-running
                (default: false)
            params (dict, optional): key-value pairs to be injected into the run command. Each ``key`` in the input
                will be matched to a corresponding ``:KEY:`` in the run command, and ``value`` will be substituted.
                For example, ``params={"foo": "bar"}`` and ``echo :FOO:`` will map to ``echo bar``. If this run is
                assigned to a project, this parameter will show up as a column (and be filterable) on its project
                details page.
            timeout (int, optional): run timeout in minutes. If this parameter is set, Spell will stop the run after
                this many minutes have elapsed. If this parameter is not set the run will never be timed out.
            auto_resume (bool, optional): spot instance machine types only. Enable or disable auto-resume. If left
                unspecified the default value for the machine type will be used.
            commit_label (str, optional): workflow runs only. A commit label for code to include in the run. The
                value must correspond to one of the commit labels set at workflow creation time
                (``spell workflow create``) using the ``--repo`` or ``--github-repo`` options.
            workflow_id (int, optional): workflow runs only. The id of the workflow to which this run will be
                associated (default: None). This argument takes precedence over
                :py:attr:`~spell.client.SpellClient.active_workflow`, the value set by the client.
        Returns:
            A :py:class:`Run` object.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        run = self.client.api.run(get_run_request(self.client, kwargs))
        return Run(self.client.api, run)

    def get(self, run_id):
        """Fetch an existing run by ID.

        Args:
            run_id (int): the ID of the run to fetch
        """
        return Run(self.client.api, self.client.api.get_run(run_id))

    def list(self, number=50, project=None, show_uncategorized=False, labels=[]):
        """Fetch a list of runs.

        Args:
            number (int, optional): the maximum number of runs to fetch (default: 50).
            project (str, optional): the project to fetch runs from (default: None).
            show_uncategorized (bool, optional): if set to ``True``, this command outputs only
                uncategorized runs (runs not assigned to a project). If set to ``False``, this
                command outputs only categorized runs. Defaults to ``False``.
            labels (list, optional). A list of labels to filter the output by. If set, will
                return only runs that have one or more of these labels set.

        Returns:
            An :obj:`list` of :py:class:`Run` objects.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        if project is not None and show_uncategorized is True:
            raise ClientException(
                "Cannot set 'project' to a non-null value when 'show_uncategorized' is set to "
                "True. These two parameters are mutually exclusive."
            )

        if project is not None:
            all_projects = self.client.api.list_projects()
            project = get_project_by_name(all_projects, project).id

        return self.client.api.list_runs(
            number=number,
            project=project,
            show_uncategorized=show_uncategorized,
            include_jupyter=False,
            labels=labels,
        )

    #: str : a constant for the "building" state
    BUILDING = "building"
    #: str : a constant for the "running" state
    RUNNING = "running"
    #: str : a constant for the "saving" state
    SAVING = "saving"
    #: str : a constant for the "pushing" state
    PUSHING = "pushing"
    #: str : a constant for the "complete" state
    COMPLETE = "complete"
    #: str : a constant for the "failed" state
    FAILED = "failed"
    #: str : a constant for the "stopped" state
    STOPPED = "stopped"
    #: str : a constant for the "killed" state
    KILLED = "killed"
    #: str : a constant for the "interrupted" state
    INTERRUPTED = "interrupted"
    #: str : a constant for the "build_failed" state
    BUILD_FAILED = "build_failed"
    #: str : a constant for the "mount_failed" state
    MOUNT_FAILED = "mount_failed"
    #: :obj:`tuple` of :obj:`str`: a tuple of the constants for the final states
    #: (i.e., :obj:`COMPLETE`, :obj:`FAILED`, :obj:`STOPPED`, :obj:`INTERRUPTED` and :obj:`KILLED`)
    FINAL = (COMPLETE, FAILED, BUILD_FAILED, MOUNT_FAILED, INTERRUPTED, KILLED, STOPPED)
    #: str : a constant for the equals condition (i.e. metric == b)
    EQUALS = "eq"
    #: str : a constant for the greater than condition (i.e. metric > b)
    GREATER_THAN = "gt"
    #: str : a constant for the greater than or equals condition (i.e. metric >= b)
    GREATER_THAN_EQUALS = "gte"
    #: str : a constant for the less than condition (i.e. metric < b)
    LESS_THAN = "lt"
    #: str : a constant for the less than or equals condition (i.e., metric <= b)
    LESS_THAN_EQUALS = "lte"


class Run(SpellModel):
    """An object representing a single Spell run.

    Attributes:
        id (int) : the run id
        status (str): the run status
        user_exit_code (int): the exit code of :obj:`command`
        command (str): the run command
        gpu (str): the GPU the run executed on
        git_commit_hash (str): the commit hash of the workspace repository for the run
        github_url (str): the URL of the GitHub repo used in the run
        description (str): the run description
        docker_image (str): the run docker image
        created_at (:py:class:`datetime.datetime`): the run creation time
        started_at (:py:class:`datetime.datetime`): the run start time
        ended_at (:py:class:`datetime.datetime`): the run end time
        workspace (:py:class:`~spell.client.workspaces.Workspace`): the run workspace
        pip_packages (:obj:`list` of :obj:`str`): pip dependencies
        apt_packages (:obj:`list` of :obj:`str`): apt dependencies
        attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`): resource name to
            mountpoint mapping of attached resouces for the run
        environment_vars (:obj:`dict` of :obj:`str` -> :obj:`str`): name to value mapping of
            environment variables for the run
        already_existed (bool): true if an existing identical run was used in lieu of re-running
        labels (:obj:`list` of :obj:`str`): labels applied to this run
    """

    model = "run"

    def __init__(self, api, run):
        self._api = api
        self.__set_from_api_run_object(api, run)

    def __set_from_api_run_object(self, api, run):
        self.run = run
        if run.workspace:
            self.workspace = Workspace(api, run.workspace)
        # The API returns labels as objects { 'name': 'SOME_NAME', 'background_color_hex': 16378031}
        # This doesn't make sense here so we overwrite this field with an array of strings
        if run.labels:
            self.run.labels = [label["name"] for label in run.labels]

    def stop(self):
        """Stop the run.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.stop_run(self.id)

    def kill(self):
        """Kill the run.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.kill_run(self.id)

    def refresh(self):
        """Refresh the run state.

        Refresh all of the run attributes with the latest information for the run
        from Spell.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.

        Example:
            >>> r.status
            'machine_requested'
            >>> r.refresh()
            >>> r.status
            'running'
        """
        api_run_object = self._api.get_run(self.id)
        self.__set_from_api_run_object(self._api, api_run_object)

    def wait_status(self, *statuses):
        """Wait until the run achieves one of the given statuses and then return.

        Args:
            *statuses (required): variable length list of statuses to wait for. Allowed values are
                :py:attr:`~RunsService.BUILDING`, :py:attr:`~RunsService.RUNNING`, :py:attr:`~RunsService.SAVING`,
                :py:attr:`~RunsService.SAVING`, :py:attr:`~RunsService.PUSHING`, :py:attr:`~RunsService.COMPLETE`,
                :py:attr:`~RunsService.FAILED`, :py:attr:`~RunsService.STOPPED`, :py:attr:`~RunsService.KILLED`,

        Raises:
            :py:class:`~spell.api.exceptions.WaitError`: none of the given statuses are reached.
            :py:class:`~spell.api.exceptions.ClientException`: any other error occurs.

        Example:
            >>> client = spell.client.from_environment()
            >>> r = client.runs.run(command="sleep 20", machine_type="CPU")
            >>> r.wait_status(client.runs.BUILDING)
            >>> r.wait_status(*client.runs.FINAL)
        """
        self._api.wait_status(self.id, *statuses)

    def wait_metric(self, metric_name, condition, value):
        """Wait until the run metric reaches the given condition and then return

        Args:
            metric_name (str): the name of the user metric
            condition(str): the condition to wait for. Allowed values are
                :py:attr:`~RunsService.EQUALS`, :py:attr:`~RunsService.GREATER_THAN`,
                :py:attr:`~RunsService.GREATER_THAN_EQUALS`, :py:attr:`~RunsService.LESS_THAN`,
                :py:attr:`~RunsService.LESS_THAN_EQUALS`,
            value (int, float, or str): the value to evaluate the condition against

        Raises:
            :py:class:`~spell.api.exceptions.WaitError`: the condition is never reached
            :py:class:`~spell.api.exceptions.ClientException`: any other error occurs
        """
        self._api.wait_metric(self.id, metric_name, condition, value)

    def add_label(self, label_name):
        """Add a label to this run.

        Args:
            label_name (str): the label to add

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.add_label_for_run(self.id, label_name)

    def remove_label(self, label_name):
        """Remove a label from this run.

        Args:
            label_name (str): the label to remove

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self._api.rm_label_for_run(self.id, label_name)

    def metrics(self, metric_name, follow=False, start=None):
        """Get metrics for the run.

        Args:
            metric_name (str): the name of the user metric
            start(:py:class:`datetime.datetime`, optional): the offset to start at. (default: None)
                A value of :py:obj:`None` will start from the oldest metric. This is an exclusive
                offset, so only metrics with timestamp greater than offset will be returned.
            follow (bool, optional): follow the metrics until the run reaches a final status (default: False)

        Yields:
            A 3-tuple of (``timestamp``, ``index``, ``value``) for each metric.
            ``timestamp`` is a :py:class:`datetime.datetime` object, ``index`` is a
            :py:obj:`int`, and ``value`` is one of :py:obj:`int`, :py:obj:`float`, or :py:obj:`str`.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        return self._api.get_run_metrics(self.id, metric_name, follow, start)

    def logs(self, follow=False, offset=0):
        """Get the logs for the run.

        A generator of log entries (:py:class:`~spell.api.models.LogEntry` objects).  Each log
        entry  corresponds to either an informational message from Spell regarding run status
        or any line from standard out or standard error that resulted from executing the run
        command.

        Args:
            follow (bool, optional): follow the log lines until the run reaches a final status (default: False)
            offset (int, optional): which log line to start from. Negative values represent offsets
                relative to the latest log line (default: 0)

        Yields:
            A :py:class:`~spell.api.models.LogEntry` object for each log line.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.

        Example:
            >>> client = spell.client.from_environment()
            >>> run = client.runs.run(command="echo 'HELLO!!!!'", machine_type="CPU")
            >>> for line in run.logs():
                ...     print(line)
                ...
                Run created -- waiting for a CPU machine.
                Run is building
                Machine acquired -- commencing run
                Run is running
                Retrieving cached environment...
                HELLO!!!!
                Run is saving
                Retrieving modified or new files from the run
                No modified or new files found
        """
        for line in self._api.get_run_log_entries(self.id, follow=follow, offset=offset):
            yield line

    def cp(self, source_path="", destination_directory=None):
        """Copy a file or directory from the run to local disk.

        Args:
            source_path (str, optional): the path within the run to copy
                (default: empty string, i.e., copy everything from the run)
            destination_directory (str, optional): destination directory to copy the file or directory to
                (default: the current working directory)

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.

        Example:
            >>> client = spell.client.from_environment()
            >>> run = client.runs.run(command="echo contents > file", machine_type="CPU")
            >>> run.wait_status(client.runs.COMPLETE)
            >>> run.cp("file")
            >>> with open("file") as f:
                ...     print(f.read())
                ...
                contents
        """
        if not destination_directory:
            destination_directory = os.getcwd()
        source_path = os.path.join("runs", str(self.id), source_path)
        with self._api.tar_of_path(source_path) as tar:
            for file in tar:
                if file.isdir() and not (file.mode & stat.S_IXUSR):
                    # Workaround for early uploads missing execute bit on directories, which breaks `ls`
                    file.mode |= stat.S_IXUSR
                tar.extract(file, path=destination_directory)
