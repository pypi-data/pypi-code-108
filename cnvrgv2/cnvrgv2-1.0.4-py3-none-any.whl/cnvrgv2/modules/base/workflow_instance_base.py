from datetime import datetime
from cnvrgv2.config import routes
from cnvrgv2.config.error_messages import EMPTY_ARGUMENT, NOT_LIST
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.base.data_owner import DataOwner
from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.log_utils import timestamp_for_logs, MAX_LOGS_PER_SEND, LOGS_TYPE_OUTPUT
from cnvrgv2.utils.url_utils import urljoin


class TagTypes:
    SINGLE_TAG = "single"
    LINECHART_TAG = "linechart"


class WorkflowInstanceBase(DataOwner):
    available_attributes = {
        "type": str,
        "title": str,
        "slug": str,
        "status": str,
        "username": str,
        "created_at": datetime,
        "start_time": datetime,
        "end_time": datetime,
        "start_commit": dict,
        "commit": str,
        "last_commit": str,
        "output_folder": str,
        "output_dir": str,
        "git_branch": str,
        "git_commit": str,
        "git": dict,
        "local_folders": list,
        "current_status": str,
        "compute_name": str,
        "external_disk": dict,
        "image_slug": str,
        "image_name": str,
        "datasets": list,
        "job_datasets": list
    }

    def start(self):
        """
        Starts the current workflow
        @return: The started workflow object
        """
        start_url = urljoin(self._route, routes.WORKflOW_START_SUFFIX)

        return self._proxy.call_api(
            route=start_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def sync_remote(self, commit_msg=None):
        """
        Syncing the current workflow
        @return: None
        """
        sync_url = urljoin(self._route, routes.WORKFLOW_SYNC_SUFFIX)

        attributes = {}
        if commit_msg:
            attributes["commit_msg"] = commit_msg

        self._proxy.call_api(
            route=sync_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def stop(self, sync=True):
        """
        Stops the current workflow
        @param sync: sync workflow before stop
        @return: None
        """
        stop_url = urljoin(self._route, routes.WORKFLOW_STOP_SUFFIX)

        attributes = {
            "sync": sync
        }

        self._proxy.call_api(
            route=stop_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def restart(self):
        """
        Restarts the current workflow
        @return: None
        """
        restart_url = urljoin(self._route, routes.WORKFLOW_RESTART_SUFFIX)

        self._proxy.call_api(
            route=restart_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def update(self, **kwargs):
        """
        Updates the current workflow
        @param kwargs: Dictionary of attributes to update.
        supported attributes: title, is_public
        @return: The updated workflow
        """
        if not kwargs:
            raise CnvrgArgumentsError(EMPTY_ARGUMENT.format("kwargs"))

        self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type=self._type, attributes=kwargs)
        )

        self.reload()
        return self

    def delete(self):
        """
        Deletes the current workflow
        @return: None
        """
        self._proxy.call_api(
            route=self._route,
            http_method=HTTP.DELETE
        )

    def tag(self, tag_type, key, value, *args, **kwargs):
        """
        Add new tag to workflow
        @param tag_type: string, 'single' or 'linechart'
        @param key: key of the tag
        @param value: value of the tag
        @param args:
        @param kwargs: additional arguments:
        xs: list of x values
        ys: list of y values
        x_axis:
        y_axis:
        grouping:
        key_type:
        @return:
        """
        tag_url = urljoin(self._route, routes.WORKFLOW_TAG_SUFFIX)
        attributes = {
            "tag_type": tag_type,
            "key": key,
            "value": value,
            **kwargs
        }

        return self._proxy.call_api(
            route=tag_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def write_logs(self, logs, log_type=LOGS_TYPE_OUTPUT):
        """
        write logs for the current workflow
        @param logs: list of logs to write
        @param log_type: log level
        @return: None
        """
        if logs is None:
            return

        write_logs_route = urljoin(self._route, routes.WORKFLOW_WRITE_LOGS_SUFFIX)

        if isinstance(logs, str):
            logs = [logs]

        for i in range(0, len(logs), MAX_LOGS_PER_SEND):
            attributes = {
                "logs": logs[i:i + MAX_LOGS_PER_SEND],
                "log_level": log_type,
                "timestamp": timestamp_for_logs()
            }

            self._proxy.call_api(
                route=write_logs_route,
                http_method=HTTP.POST,
                payload=JAF.serialize(type=self._type, attributes=attributes)
            )

    def get_logs(self, filter=None, **kwargs):
        """
        Get logs of the current workflow
        @param filter: list of logs type to filter ('stdout', 'cnvrg-info', 'cnvrg-error')
        @return: List of the logs
        """
        # TODO: Check that it works after server changes
        #  (currently results are not in JAF format, filter expects string with " and not ', so current doesn't work)
        if filter is None:
            filter = ["all"]
        elif type(filter) is not list:
            raise CnvrgArgumentsError(NOT_LIST.format("filter"))

        get_logs_url = urljoin(self._route, routes.WORKFLOW_GET_LOGS_SUFFIX)

        attributes = {
            "filter": str(filter),
            "search": "",
            **kwargs
        }

        return self._proxy.call_api(
            route=get_logs_url,
            http_method=HTTP.GET,
            payload=attributes
        )

    def _validate_config_ownership(self):
        return False

    def sync(self, job_slug=None, git_diff=False):
        return NotImplemented

    def save_config(self):
        return NotImplemented

    def download(self, sync=False, progress_bar_enabled=False, commit_sha1=None):
        return NotImplemented

    def upload(self, sync=False, job_slug=None, progress_bar_enabled=False, git_diff=False):
        return NotImplemented

    def clone(self, progress_bar_enabled=False, override=False):
        return NotImplemented
