from spell.api import base_client
from spell.api.utils import url_path_join

from spell.api.exceptions import ClientException
from spell.api.models import ValueSpec, RangeSpec


RUNS_RESOURCE_URL = "runs"
KILL_RESOURCE_URL = "kill"
STOP_RESOURCE_URL = "stop"
HYPER_SEARCH_RESOURCE_URL = "hyper_search"
METRICS_RESOURCE_URL = "metrics"
METRICS_NAMES_RESOURCE_URL = "metric-names"


class HyperClient(base_client.BaseClient):
    def hyper_grid_search(self, params, run_req):
        """Create a hyperparameter grid search

        Keyword arguments:
        params -- a dictionary mapping str -> models.ValueSpec
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        payload = {
            "grid_params": params,
            "run": run_req,
        }
        r = self.request(
            "post",
            url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
            payload=payload,
        )
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def hyper_random_search(self, params, num_runs, run_req):
        """Create a hyperparameter random search

        Keyword arguments:
        params -- a dictionary mapping str -> models.ValueSpec or models.RangeSpec objects
        num_runs -- an int specifying the number of runs to create
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        param_payload = {}
        for k, v in params.items():
            if isinstance(v, ValueSpec):
                param_payload[k] = {"value_spec": v}
            elif isinstance(v, RangeSpec):
                param_payload[k] = {"range_spec": v}
            else:
                raise ClientException("values of params must be either a ValueSpec of RangeSpec")
        payload = {
            "num_runs": num_runs,
            "random_params": param_payload,
            "run": run_req,
        }
        r = self.request(
            "post",
            url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
            payload=payload,
        )
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def hyper_bayesian_search(self, params, num_runs, parallel_runs, metric, metric_agg, run_req):
        """Create a hyperparameter bayesian search

        Keyword arguments:
        params -- a dictionary mapping str -> models.RangeSpec objects
        num_runs -- an int specifying the maximum number of runs to create
        parallel_runs -- an int specifying the number of runs to parallelize
        metric -- the metric used to evaluate runs
        metric_agg -- the aggregation method for the metric
        run_req -- a RunRequest object

        Returns:
        a HyperSearch object

        """
        param_payload = {}
        for k, v in params.items():
            if isinstance(v, RangeSpec):
                param_payload[k] = {"range_spec": v}
            else:
                raise ClientException("values of params must be a RangeSpec")
        payload = {
            "num_runs": num_runs,
            "parallel_runs": parallel_runs,
            "metric": metric,
            "metric_aggregation": metric_agg,
            "bayesian_params": params,
            "run": run_req,
        }
        r = self.request(
            "post",
            url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL),
            payload=payload,
        )
        self.check_and_raise(r)
        resp = self.get_json(r)
        hyper = resp["hyper_search"]
        return hyper

    def get_hyper_search(self, hyper_search_id):
        """Get a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search

        Returns:
        a HyperSearch object
        """
        r = self.request(
            "get",
            url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL, hyper_search_id),
        )
        self.check_and_raise(r)
        return self.get_json(r)["hyper_search"]

    def kill_hyper_search(self, hyper_search_id):
        """Kill a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search
        """
        r = self.request(
            "post",
            url_path_join(
                RUNS_RESOURCE_URL,
                self.owner,
                HYPER_SEARCH_RESOURCE_URL,
                hyper_search_id,
                KILL_RESOURCE_URL,
            ),
        )
        self.check_and_raise(r)

    def stop_hyper_search(self, hyper_search_id):
        """Stop a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search
        """
        r = self.request(
            "post",
            url_path_join(
                RUNS_RESOURCE_URL,
                self.owner,
                HYPER_SEARCH_RESOURCE_URL,
                hyper_search_id,
                STOP_RESOURCE_URL,
            ),
        )
        self.check_and_raise(r)

    def list_hyper_searches(self):
        """List hyperparameter searches."""
        r = self.request("get", url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL))
        return self.get_json(r)["hyper_searches"]

    def get_hyper_metric(self, hyper_search_id, metric_name):
        """Get a hyperparameter search metric."""
        r = self.request(
            "get",
            url_path_join(
                RUNS_RESOURCE_URL,
                self.owner,
                HYPER_SEARCH_RESOURCE_URL,
                hyper_search_id,
                METRICS_RESOURCE_URL,
                metric_name,
            ),
        )
        return self.get_json(r)["metrics"]

    def list_hyper_metric_names(self, hyper_search_id):
        """List metric names associated with a hyperparameter search."""
        r = self.request(
            "get",
            url_path_join(
                RUNS_RESOURCE_URL,
                self.owner,
                HYPER_SEARCH_RESOURCE_URL,
                hyper_search_id,
                METRICS_NAMES_RESOURCE_URL,
            ),
        )
        return self.get_json(r)["metric_names"]

    def archive_hyper_search(self, hyper_search_id):
        """Archive a hyperparameter search.

        Keyword arguments:
        hyper_search_id -- the id of the hyperparameter search
        """
        r = self.request(
            "delete",
            url_path_join(RUNS_RESOURCE_URL, self.owner, HYPER_SEARCH_RESOURCE_URL, hyper_search_id),
        )
        self.check_and_raise(r)
