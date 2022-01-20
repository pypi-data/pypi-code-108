import json
import os
import sys
import time
import requests
from datetime import datetime
from cnvrgv2.config import routes, error_messages
from cnvrgv2.errors import CnvrgError
from cnvrgv2.modules.base.workflow_instance_base import WorkflowInstanceBase
from cnvrgv2.modules.images.image import Image
from cnvrgv2.modules.workflows.endpoint.endpoint_rule import EndpointRule
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.cron import Cron
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin


class EndpointKind:
    WEB_SERVICE = 0
    STREAM = 1
    BATCH = 2


class EndpointEnvSetup:
    PYTHON2 = "python_2"
    PYTHON3 = "python_3"
    PYSPARK = "pyspark"
    RENDPOINT = "r_endpoint"


class FeedbackLoopKind:
    IMMEDIATE = 0
    RECURRING = 1


class Endpoint(WorkflowInstanceBase):
    available_attributes = {
        "kind": str,
        "compute": str,
        "updated_at": str,
        "last_deployment": dict,
        "deployments": dict,
        "deployments_count": int,
        "templates": list,
        "endpoint_url": str,
        "current_deployment": dict,
        "compute_name": str,
        "image_name": str,
        "image_slug": str,
        "url": str,
        "api_key": str,
        "created_at": datetime,
        "max_replica": int,
        "min_replica": int,
        "export_data": bool,
        "conditions": dict,
        **WorkflowInstanceBase.available_attributes
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.ENDPOINT, slug)

        self._scope = self._context.get_scope(SCOPE.ENDPOINT)

        self._proxy = Proxy(context=self._context)
        self._route = routes.ENDPOINT_BASE.format(
            self._scope["organization"],
            self._scope["project"],
            self._scope["endpoint"]
        )

        self._attributes = attributes or {}
        self._type = "Endpoint"
        self.slug = self._scope["endpoint"]

    def update_version(self, file_name=None, function_name=None, prep_file=None, prep_function=None, max_timeout=None,
                       **kwargs):
        """
        Update the endpoint version
        @param file_name: Name of new file
        @param function_name: Name of new function
        @param prep_file: Name of new preprocess file
        @param prep_function: Name of new preprocess function
        @param max_timeout: Time in minutes to wait until timeout
        @param kwargs:
        image: Image object to update endpoint with
        commit: Commit where files are.
        git_branch: Git branch where files are
        git_commit: Git commit where files are
        integer desired_percentage: Traffic ratio for canary rollout
        gunicorn_config: Array of key values in the following format: ["key=value", "key=value"]
        flask_config: Array of key values in the following format: ["key=value", "key=value"]
        kafka_brokers: List of kafka brokers
        kafka_input_topics: List of topics to register as input
        kafka_output_topics: List of topics to register as output
        input_file: Boolean. Does endpoint accepts file
        emails_to_notify: List. list of emails to send on success / error emails
        @return: updated endpoint
        """
        update_version_url = urljoin(self._route, routes.UPDATE_MODEL_VERSION)

        attributes = {
            "workflow_slug": self.slug,
            "file_name": file_name,
            "function_name": function_name,
            "prep_file": prep_file,
            "prep_function": prep_function,
            **kwargs
        }

        if isinstance(kwargs.get("image"), Image):
            attributes["image_slug"] = kwargs.get("image").slug

        start_time = datetime.now()

        res_attributes = self._proxy.call_api(
            route=update_version_url,
            http_method=HTTP.POST,
            payload=attributes
        ).attributes

        self.reload()
        while self.current_deployment["is_update"]:
            if max_timeout is not None:
                minutes_diff = (datetime.now() - start_time).total_seconds() / 60
                if minutes_diff > max_timeout:
                    raise CnvrgError(error_messages.ENDPOINT_UPDATE_TIMEOUT.format(self.slug))
            time.sleep(5)
            self.reload()

        self._attributes = {**self._attributes, **res_attributes}
        return self

    def rollback_version(self, version_slug=None):
        """
        Rollback an endpoint version
        @param version_slug: Version to rollback slug
        @return: None
        """
        rollback_version_url = urljoin(self._route, routes.ROLLBACK_MODEL_VERSION.format(version_slug))

        self._proxy.call_api(
            route=rollback_version_url,
            http_method=HTTP.POST,
        )

    def configure_feedback_loop(self, dataset_slug=None, scheduling_type=FeedbackLoopKind.IMMEDIATE, cron_string=None):
        """
        Update the endpoint version
        @param dataset_slug: Name of the dataset to export to
        @param Feedback loop kind: 0 - immediate export, 1 - recurring export
        @param cron_string: cron string if scheduling type is recurring
        @return: None
        """
        feedback_url = urljoin(self._route, routes.ENDPOINT_FEEDBACK_LOOP)
        if cron_string:
            Cron.validate_cron_syntax(cron_string)

        attributes = {
            "form_values": {
                "dataset": {
                    "slug": dataset_slug,
                },
                "sched_type": scheduling_type,
                "cron_string": cron_string
            }
        }

        self._proxy.call_api(
            route=feedback_url,
            http_method=HTTP.POST,
            payload=attributes
        )

        return

    def get_sample_code(self):
        """
        Get a sample code to query a running endpoint
        @return: Object with 2 properties: python & curl
        """

        route = urljoin(self._route, routes.ENDPOINT_SAMPLE_CODE)
        route = urljoin(self._route, "sample_code")
        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.GET
        )

        return response.attributes

    def update_replicas(self, min_replica, max_replica):
        """
        Update endpoint number of replicas
        @param min_replica: minimum number of replicas
        @param max_replica: maximum number of replicas
        @return: None
        """
        self.reload()
        if self.status != 'ongoing':
            raise CnvrgError(error_messages.ENDPOINT_NOT_RUNNING.format(self.slug))

        route = urljoin(self._route, routes.ENDPOINT_REPLICAS)

        attributes = {
            "min_replica": min_replica,
            "max_replica": max_replica
        }

        self._proxy.call_api(
            route=route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def poll_charts(self):
        """
        Get endpoint charts and metrics
        @return: endpoint logs object with requests and latency properties
        """
        route = urljoin(self._route, routes.ENDPOINT_POLL_CHARTS)
        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.GET
        )

        return response.attributes

    def stop_feedback_loop(self):
        """
        Stop existing endpoint feedback loop
        @return: None
        """
        route = urljoin(self._route, routes.ENDPOINT_FEEDBACK_LOOP)

        self._proxy.call_api(
            route=route,
            http_method=HTTP.DELETE
        )

    def batch_is_running(self):
        """
        Check whether batch endpoint is running or paused
        @return: True if running, false otherwise
        """
        route = urljoin(self._route, routes.ENDPOINT_STATUS)

        res = self._proxy.call_api(
            route=route,
            http_method=HTTP.GET
        )
        return res.meta['batch_is_running']

    def batch_scale_up(self):
        """
        Scale up batch endpoint
        @return: None
        """
        route = urljoin(self._route, routes.ENDPOINT_BATCH_SCALE_UP)

        self._proxy.call_api(
            route=route,
            http_method=HTTP.POST
        )

    def batch_scale_down(self):
        """
        Scale down batch endpoint
        @return: None
        """
        route = urljoin(self._route, routes.ENDPOINT_BATCH_SCALE_DOWN)

        self._proxy.call_api(
            route=route,
            http_method=HTTP.POST
        )

    def get_rules(self):
        """
        list endpoint rules
        @return: List of the endpoint rules (array of EndpointRule objects)
        """
        route = urljoin(self._route, routes.ENDPOINT_RULES)
        return api_list_generator(context=self._context, route=route, object=EndpointRule)

    def add_rule(
            self,
            title,
            metric,
            severity,
            operation,
            action,
            frequency=1,
            description=None,
            threshold=None,
            min_events=None
    ):
        """
        add a rule
        @param title: rule title
        @param description: rule description
        @param metric: The cnvrg SDK metric used for the trigger. (Only tags with numeric values are supported)
        @param threshold: The value you are comparing against.
        @param min_events: Minimum number of events before triggering action
        @param severity: An indication of the importance of this alert (Info, Warning or Critical).
        @param operation: The type of comparison used for comparing with your set value (greater than or less than).
        @param frequency: How often to run condition (in minutes)
        @param action: Action to occur when the alert is triggered (a json of: type, webhook slug, flow_slug and emails)
        @return: The new rule created
        """

        attributes = {
            "rule": {
                "title": title,
                "description": description,
                "metric": metric,
                "threshold": threshold,
                "min_events": min_events,
                "severity": severity.lower(),
                "operation": operation,
                "frequency": frequency,
                "action": {**action, "type": action.get("type", '').lower()}
            }
        }

        route = urljoin(self._route, routes.ENDPOINT_RULES)
        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

        slug = response.attributes['slug']
        return EndpointRule(context=self._context, slug=slug, attributes=response.attributes)

    def update_rule(self, slug, is_active):
        """
        update rule state
        @param slug: the rule slug
        @param is_active: is the rule active or not
        """

        route = urljoin(self._route, routes.ENDPOINT_RULES + "/{0}".format(slug))
        rule = {
            "rule": {
                "is_active": is_active
            }
        }

        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=rule)
        )

        slug = response.attributes['slug']
        return EndpointRule(context=self._context, slug=slug, attributes=response.attributes)

    def delete_rule(self, slug):
        """
        delete a rule
        @param slug: rule slug
        """

        route = urljoin(self._route, routes.ENDPOINT_RULES + "/{0}".format(slug))
        self._proxy.call_api(
            route=route,
            http_method=HTTP.DELETE
        )

    def log_metric(self, name, y: float = None, x=None):
        params = {}
        try:
            params[name] = float(y)
            params["y"] = float(y)
        except Exception as e:
            print("ERROR {}".format(e), file=sys.stderr)
            return
        params["x"] = x
        params["cnvrg_metric_name"] = name
        log = {
            "job_id": self.slug,
            "job_type": self._type,
            "owner": self._context.get_scope(SCOPE.ENDPOINT)["organization"],
            "project": self._context.get_scope(SCOPE.ENDPOINT)["project"],
            "model": os.environ.get("CNVRG_MODEL_NAME", "unknown"),
            "event_time": time.time(),
            **params
        }
        print(json.dumps(log))
        sys.stdout.flush()

    def set_metadata(self, metadata=None):
        """
        Get a metadata of an endpoint
        @param metadata: Hash. metadata of the endpoint
        """
        route = urljoin(self._route, "metadata")
        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.POST,
            payload={"metadata": metadata}
        )
        return response

    def get_metadata(self):
        """
        Get a metadata of an endpoint
        @return: Hash
        """
        route = urljoin(self._route, "metadata")
        response = self._proxy.call_api(
            route=route,
            http_method=HTTP.GET
        )

        return response.attributes.get("metadata")

    def predict(self, input_params):
        """
        Get a prediction from the endpoint's model
        @param input_params: the input parameters for the predict function
        @return: The prediction object
        """
        if not self.endpoint_url or not self.api_key:
            self.reload()
        headers = {
            'Cnvrg-Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        data = json.dumps({"input_params": input_params})
        response = requests.post(self.endpoint_url, headers=headers,
                                 data=data)
        res_content = response.content.decode()

        print(res_content)
        return res_content