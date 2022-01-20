import time
from datetime import datetime

from cnvrgv2.data import ArtifactsDownloader
from cnvrgv2.config import routes
from cnvrgv2.config.error_messages import EMPTY_ARGUMENT, ARGUMENT_BAD_TYPE, NOT_LIST
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.base.workflow_instance_base import WorkflowInstanceBase, TagTypes
from cnvrgv2.utils.chart_utils import Chart, LineChart, BarChart, ScatterPlot, Heatmap
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.env_helper import ENV_KEYS
from cnvrgv2.modules.workflows.workflow_utils import WorkflowUtils, WorkflowStatuses
from cnvrgv2.utils.log_utils import (
    LOGS_TYPE_OUTPUT, LOGS_TYPE_ERROR, LOGS_TYPE_INFO, LOGS_TYPE_WARNING, timestamp_for_logs
)


class Experiment(WorkflowInstanceBase):
    available_attributes = {
        "input": str,
        "href": str,
        "full_href": str,
        "remote": str,
        "ma": str,
        "is_running": bool,
        "terminal_url": str,
        "termination_time": datetime,
        **WorkflowInstanceBase.available_attributes
    }

    CHART_CLASSES = {
        'none': LineChart,
        'scatter': ScatterPlot,
        'bar': BarChart,
        'heatmap': Heatmap
    }

    def __init__(self, context=None, slug=None, attributes=None):
        super().__init__()
        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.EXPERIMENT, slug)

        self.scope = self._context.get_scope(SCOPE.EXPERIMENT)

        self._proxy = Proxy(context=self._context)
        self._route = routes.EXPERIMENT_BASE.format(
            self.scope["organization"],
            self.scope["project"],
            self.scope["experiment"]
        )
        self._attributes = attributes or {}
        self._type = "Experiment"
        self.slug = self.scope["experiment"]

    def restart(self):
        """
        restarts an experiment
        @return: The restarted experiment object
        """
        return super().start()

    def finish(self, exit_status):
        # TODO: remove after uniting finish and stop in server.
        #  Ask Leah if experiment should have finish as syntax (product wise)
        """
        Finishes the current experiment
        @param exit_status: exit status of the experiment
        @return: The finished experiment
        """
        finish_url = urljoin(self._route, routes.EXPERIMENT_FINISH_SUFFIX)
        attributes = {
            "exit_status": exit_status
        }

        return self._proxy.call_api(
            route=finish_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def start(self):
        """
        Override start from workflows_base to remove functionality.
        start() is only relevant for Endpoints & Workspaces
        """
        raise AttributeError("'Experiment' object has no attribute 'start'")

    def create_chart(self, chart: Chart):
        """
        Creates a chart for the current experiment
        @param chart: A chart object
        @return: The created chart object
        """

        create_chart_url = urljoin(self._route, routes.EXPERIMENT_CHARTS_SUFFIX)

        response = self._proxy.call_api(
            route=create_chart_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=chart.to_dict())
        )

        NewChartClass = self.CHART_CLASSES.get(chart.chart_type)

        chart_kwargs = {**response.attributes, **response.attributes.get('settings')}
        chart_kwargs.pop('chart_type', None)

        new_chart = NewChartClass(**chart_kwargs)

        return new_chart

    def as_env(self):
        """
        @return: A dict representing current experiment for env use
        """
        return {
            ENV_KEYS["current_job_id"]: self.slug,
            ENV_KEYS["current_job_type"]: self._type,
            ENV_KEYS["current_project"]: self.scope["project"],
            ENV_KEYS["current_organization"]: self.scope["organization"],
        }

    def pull_artifacts(self, wait_until_success=False, poll_interval=10):
        """
        pulls current experiment's artifacts to the local working dir
        @param wait_until_success: Wait until current experiment is done before pulling artifacts
        @param poll_interval: Is wait_until_success is True, time between status poll loops
        @return: None
        """
        if wait_until_success:
            WorkflowUtils.wait_for_statuses(self, WorkflowStatuses.SUCCESS, poll_interval=poll_interval)

        self.reload()
        # if the experiment does not have any commit and artifacts, skip.
        # Can happen when cloning a git project and pulling artifact immediately after.
        if self.start_commit:
            return ArtifactsDownloader(self, base_commit_sha1=self.start_commit["sha1"], commit_sha1=self.last_commit)

    def log_param(self, key, value=None):
        """
        Adds the given tag to the current experiment
        @param key: [String] The tag name
        @param value: [String] The tag value
        @return: None
        """
        # TODO: add run async to this function and rest of log functions
        return self.tag(tag_type=TagTypes.SINGLE_TAG, key=key, value=value)

    def log_images(self, file_paths):
        """
        Saves the given images to the current experiment as a new commit
        Note that only images that will be saved via this function
        Will show as experiment visuals
        @param file_paths: list of paths of artifacts to save
        @return: None
        """
        commit_msg = "Log Images Commit"
        self.put_files(file_paths, message=commit_msg, job_slug=self.slug, tag_images=True)

    def log_artifacts(self, paths=None, git_diff=False):
        """
        Saves the given artifacts to the current experiment as a new commit
        @param paths: list of paths of artifacts to save
        @param git_diff: upload files from git diff output in addition to the given paths
        @return: None
        """
        if not paths and not git_diff:
            raise CnvrgArgumentsError(EMPTY_ARGUMENT.format("file_paths"))
        if not isinstance(paths, list):
            raise CnvrgArgumentsError(NOT_LIST.format("paths"))

        commit_msg = "Log Artifacts Commit"
        self.put_files(paths, message=commit_msg, job_slug=self.slug, git_diff=git_diff)
        self.reload()

    def get_utilization(self):
        """
        Get experiment's utilization stats
        @return: Experiment's system stats data
        """
        return self._proxy.call_api(
            route=urljoin(self._route, routes.EXPERIMENT_GET_UTILIZATION_SUFFIX),
            http_method=HTTP.GET
        )

    def log(self, logs, log_level=LOGS_TYPE_INFO, timestamp=None):
        """
        Method to add logs to the experiment log
        @param logs: an array of logs you want to send
        @param log_level: level of the logs, exists in log_utils
        @param timestamp: timestamp for the logs, UTC now by default
        """
        if timestamp is None:
            timestamp = timestamp_for_logs()

        if type(timestamp) is not str:
            raise CnvrgArgumentsError({"timestamp": ARGUMENT_BAD_TYPE % ("str", type(timestamp))})

        if log_level not in (LOGS_TYPE_OUTPUT, LOGS_TYPE_ERROR, LOGS_TYPE_INFO, LOGS_TYPE_WARNING):
            raise CnvrgArgumentsError({"level": ARGUMENT_BAD_TYPE % ("logs level enum", log_level)})

        if type(logs) is not list:
            if type(logs) is str:
                # give the user the option to only send one string
                logs = [logs]
            else:
                raise CnvrgArgumentsError({"level": ARGUMENT_BAD_TYPE % ("str", type(logs))})

        return self._proxy.call_api(
            route=urljoin(self._route, routes.EXPERIMENT_WRITE_LOGS),
            http_method=HTTP.POST,
            payload={
                "logs": logs,
                "log_level": log_level,
                "timestamp": timestamp
            }
        )

    def logs(self):
        """
        Retrieval of the last 40 logs of the experiment
        @return: a list of the last 40 logs
        """
        response = self._proxy.call_api(
            route=urljoin(self._route, routes.EXPERIMENT_LOGS_SUFFIX),
            http_method=HTTP.GET,
        )

        return response.attributes["logs"]

    def _rerun(self, sync=True, prerun=False, requirements=False):
        """
        Rerun experiment that's currently in debug mode
        @param sync: sync before rerunning
        @param prerun: run prerun.sh script
        @param requirements: install requirements file
        @return: None
        """
        rerun_url = urljoin(self._route, routes.EXPERIMENT_RERUN_SUFFIX)
        attributes = {
            "sync": sync,
            "prerun": prerun,
            "requirements": requirements
        }

        self._proxy.call_api(
            route=rerun_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def list_charts(self):
        """
        List charts of an experiment
        @return: List of charts for the experiment
        """
        charts_url = urljoin(self._route, routes.EXPERIMENT_CHARTS_SUFFIX)

        response = self._proxy.call_api(
            route=charts_url,
            http_method=HTTP.GET
        )

        charts_list = []
        for chart_jaf in response.items:
            chart_type = chart_jaf.attributes.get('settings').get('chart_type')
            ChartClass = self.CHART_CLASSES.get(chart_type)

            chart_kwargs = {**chart_jaf.attributes, **chart_jaf.attributes.get('settings')}
            chart_kwargs.pop('chart_type', None)

            chart = ChartClass(**chart_kwargs)
            charts_list.append(chart)

        return charts_list

    def get_chart(self, key):
        """
        Get charts of an experiment
        @param key: key of chart we wish to get
        @return: Chart with given key
        """
        chart_url = urljoin(self._route, routes.EXPERIMENT_CHART_SUFFIX.format(key))

        response = self._proxy.call_api(
            route=chart_url,
            http_method=HTTP.GET
        )

        # If we couldn't find a chart with given key
        if not len(response.attributes):
            return None

        chart_type = response.attributes.get('settings').get('chart_type')
        ChartClass = self.CHART_CLASSES.get(chart_type)

        chart_kwargs = {**response.attributes, **response.attributes.get('settings')}
        chart_kwargs.pop('chart_type', None)

        chart = ChartClass(**chart_kwargs)

        return chart

    def update_chart(self, key, data, series_name=None):
        """
        Add data to an existing series in a chart
        @param key: key of chart we wish to update
        @param data: new data to add to series
        @param series_name: name of series to update (optional, will update default series without name)
        @return: Chart with given key
        """

        current_chart = self.get_chart(key)

        # Do nothing if we couldn't find given chart
        if not current_chart:
            return None

        # This will validate our data is in the right format for our chart
        formatted_data = current_chart.validate_series(data)

        update_chart_url = urljoin(self._route, routes.EXPERIMENT_CHARTS_SUFFIX)

        attributes = {
            "key": key,
            "series": [{"data": formatted_data, "name": series_name}]
        }

        response = self._proxy.call_api(
            route=update_chart_url,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

        ChartClass = self.CHART_CLASSES.get(current_chart.chart_type)

        chart_kwargs = {**response.attributes, **response.attributes.get('settings')}
        chart_kwargs.pop('chart_type', None)

        chart = ChartClass(**chart_kwargs)

        return chart

    def _wait_until_experiment_finish(self, poll_interval=10):
        """
        Busy waits until current experiment run is done
        @param poll_interval: time between status poll loops
        @return: The status of the experiment when done.
        """
        while self.is_running:
            time.sleep(poll_interval)
            self.reload()
        return self.status
