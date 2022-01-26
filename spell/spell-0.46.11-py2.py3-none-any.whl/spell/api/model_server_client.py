import json
from spell.api import base_client
from spell.api.utils import url_path_join

from requests.exceptions import ChunkedEncodingError
from spell.api.exceptions import JsonDecodeError

MODEL_SERVER_URL = "model_servers"
METRICS_RESOURCE_URL = "user-metrics"


class ModelServerClient(base_client.BaseClient):
    def new_model_server(self, server_req):
        """Create and start a model server

        Arguments:
        server_req - ModelServerCreateRequest object describing the model to start

        Returns:
        A ModelServer object with the specified name
        """
        r = self.request("post", url_path_join(MODEL_SERVER_URL, self.owner), payload=server_req)
        self.check_and_raise(r)
        return self.get_json(r)["model_server"]

    def get_model_servers(self, owner=None):
        """Get a list of model servers.

        Returns:
        a list of Model Server objects for this user

        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner)
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["model_servers"]

    def get_model_server(self, server_name, owner=None):
        """Get a info about a model server

        Keyword arguments:
        server_name - name of the model server to retrieve

        Returns:
        a ModelServer object with the specified name
        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner, server_name)
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["model_server"]

    def delete_model_server(self, server_name, owner=None):
        """Removes a model server

        Keyword arguments:
        server_name - name of the model server to remove

        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner, server_name)
        r = self.request("delete", url)
        self.check_and_raise(r)

    def start_model_server(self, server_name, owner=None):
        """Starts a model server

        Keyword arguments:
        server_name - name of the model server to start

        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner, server_name, "start")
        r = self.request("post", url)
        self.check_and_raise(r)

    def stop_model_server(self, server_name, owner=None):
        """Stops a model server

        Keyword arguments:
        server_name - name of the model server to stop

        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner, server_name, "stop")
        r = self.request("post", url)
        self.check_and_raise(r)

    def update_model_server(self, server_name, server_req):
        """Update a model server

        Arguments:
        server_name - The name of the server to update
        server_req - ModelServerUpdateRequest object describing the model to update
        """
        r = self.request(
            "patch",
            url_path_join(MODEL_SERVER_URL, self.owner, server_name),
            payload=server_req,
        )
        self.check_and_raise(r)

    def delete_model_server_mounts(self, server_name):
        """Removes all model server mounts
        Arguments:
        server_name - The name of the server to update
        """
        r = self.request(
            "delete",
            url_path_join(MODEL_SERVER_URL, self.owner, server_name, "attached_resources"),
        )
        self.check_and_raise(r)

    def delete_model_server_models(self, server_name):
        """Remove all models from a model server

        Arguments:
        server_name - The name of the server to update
        """
        r = self.request(
            "delete",
            url_path_join(MODEL_SERVER_URL, self.owner, server_name, "models"),
        )
        self.check_and_raise(r)

    def get_model_server_log_entries(self, server_name, pod, follow, owner=None):
        """Get log entries for a model server

        Keyword arguments:
        server_name - name of the model server
        pod - the ID of the pod to get logs for
        follow -- true if the logs should be followed

        Returns:
        a generator for entries of model sever logs
        """
        owner = owner or self.owner
        url = url_path_join(MODEL_SERVER_URL, owner, server_name, "logs")
        params = {"pod_id": pod}
        if follow:
            params["follow"] = follow
        with self.request("get", url, params=params, stream=True) as log_stream:
            self.check_and_raise(log_stream)
            try:
                if log_stream.encoding is None:
                    log_stream.encoding = "utf-8"
                for chunk in log_stream.iter_lines(decode_unicode=True):
                    try:
                        chunk = json.loads(chunk, cls=base_client.SpellDecoder)
                    except ValueError as e:
                        message = "Error decoding the model server log response chunk: {}".format(e)
                        raise JsonDecodeError(msg=message, response=log_stream, exception=e)
                    logEntry = chunk.get("model_server_log_entry")
                    if logEntry:
                        yield logEntry
            except ChunkedEncodingError:
                return

    def list_model_server_metric_names(self, server_name):
        """List the names of metrics associated with this model server."""
        url = url_path_join(MODEL_SERVER_URL, self.owner, server_name, METRICS_RESOURCE_URL, "list")
        r = self.request("get", url)
        return self.get_json(r)["names"]

    def get_model_server_metric(self, server_name, metric_name):
        """Get a metrics from this model server."""
        url = url_path_join(MODEL_SERVER_URL, self.owner, server_name, METRICS_RESOURCE_URL)
        r = self.request("get", url, params={"metric_name": metric_name})
        return self.get_json(r)["data"]

    def wait_model_server_status(self, server_name, *statuses):
        url = url_path_join(MODEL_SERVER_URL, self.owner, server_name, "wait_status")
        r = self.request("post", url, params={"statuses": statuses})
        return self.get_json(r)
