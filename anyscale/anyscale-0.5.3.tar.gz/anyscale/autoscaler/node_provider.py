"""NodeProvider classes that add product-specific behaviour."""

import base64
import copy
import inspect
import json
import logging
import time
from types import ModuleType
from typing import Any, cast, Dict, List, Optional

from openapi_client.rest import ApiException
from ray import cloudpickle
from ray.autoscaler._private.aws.node_provider import to_aws_format
from ray.autoscaler._private.command_runner import DockerCommandRunner, SSHCommandRunner
from ray.autoscaler._private.util import hash_launch_conf
from ray.autoscaler.command_runner import CommandRunnerInterface
from ray.autoscaler.tags import (
    STATUS_UP_TO_DATE,
    TAG_RAY_CLUSTER_NAME,
    TAG_RAY_NODE_STATUS,
)
from urllib3.exceptions import HTTPError  # type: ignore
import wrapt

from anyscale.authenticate import get_auth_api_client


# This try block exists because
# 1. This module is passed to the autoscaler on the head node as an external node provider
# 2. Import paths are different for different versions of ray
try:
    from ray.autoscaler._private.providers import _get_node_provider, _NODE_PROVIDERS
    from ray.autoscaler.node_provider import NodeProvider
except ModuleNotFoundError:
    from ray.autoscaler.aws.node_provider import NodeProvider
    from ray.autoscaler.node_provider import (
        get_node_provider as _get_node_provider,
        NODE_PROVIDERS as _NODE_PROVIDERS,
    )

from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.models.add_instance_pool_member import (
    AddInstancePoolMember,
)
from anyscale.client.openapi_client.models.create_nodes_options import (
    CreateNodesOptions,
)
from anyscale.client.openapi_client.models.nodes_options import NodesOptions
from anyscale.client.openapi_client.models.non_terminated_nodes_options import (
    NonTerminatedNodesOptions,
)
from anyscale.client.openapi_client.models.query_pool_size import QueryPoolSize
from anyscale.client.openapi_client.models.request_instance_pool_member import (
    RequestInstancePoolMember,
)
from anyscale.client.openapi_client.models.set_node_tags_options import (
    SetNodeTagsOptions,
)
from anyscale.client.openapi_client.models.wait_until_stopped_options import (
    WaitUntilStoppedOptions,
)
from anyscale.shared_anyscale_utils.util import get_autoscaler_container_path


logger = logging.getLogger(__name__)
RETRY_COUNT = 5


def wrap_api_client_with_retries(api_client: DefaultApi) -> DefaultApi:
    @wrapt.decorator  # type: ignore
    def retrier(func: Any, instance: Any, args: List[Any], kwargs: Any) -> Any:
        for i in range(RETRY_COUNT):
            try:
                return func(*args, **kwargs)
            except (ConnectionResetError, HTTPError) as e:
                if i == (RETRY_COUNT - 1):
                    logger.error(f"{func.__name__} FAILED {RETRY_COUNT} times!")
                    raise e
                time.sleep(0.1 * i)
                continue

    for name, fn in inspect.getmembers(api_client):
        if inspect.ismethod(fn) and "with_http_info" not in name:
            setattr(api_client, name, retrier(fn))
    return api_client


class AnyscaleInstanceManagerNodeProvider:
    """NodeProvider for managing nodes with instance manager.
    """

    def __init__(self, provider_config: Dict[str, Any], cluster_name: str) -> None:
        self.provider_config = provider_config
        self.inner_provider_config = provider_config["inner_provider"]
        self.inner_provider = _get_node_provider(
            self.inner_provider_config, cluster_name
        )
        self.cloud_id = self.inner_provider_config["cloud_id"]
        cli_token = self.inner_provider_config["cli_token"]
        host = self.inner_provider_config["host"]
        self.api_client = wrap_api_client_with_retries(
            get_auth_api_client(cli_token=cli_token, host=host).api_client
        )
        self.is_provider_supported = self._is_provider_supported()

    def _is_provider_supported(self) -> bool:
        """Currently instance manager only suppport AWS."""
        # TODO(yifei) move checks from _configure_for_cloud to here
        return True

    def __getattr__(self, name: str) -> Any:
        """Implements inheritance from self.inner_provider."""
        return getattr(self.inner_provider, name)

    # Use the same methodology as AnyscalePoolingNodeProvider for the following
    # static methods
    @staticmethod
    def _get_inner_provider_class_from_config(cluster_config: Dict[str, Any]) -> Any:

        inner_provider_config = cluster_config["provider"]["inner_provider"]
        importer = _NODE_PROVIDERS.get(inner_provider_config["type"])
        inner_provider_cls = importer(inner_provider_config)
        return inner_provider_cls

    @staticmethod
    def bootstrap_config(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        cluster_config = copy.deepcopy(cluster_config)
        inner_provider_cls = AnyscalePoolingNodeProvider._get_inner_provider_class_from_config(
            cluster_config
        )
        primary_provider = cluster_config["provider"]
        cluster_config["provider"] = cluster_config["provider"]["inner_provider"]

        cluster_config = inner_provider_cls.bootstrap_config(cluster_config)

        primary_provider["inner_provider"] = cluster_config["provider"]
        cluster_config["provider"] = primary_provider
        return cluster_config

    @staticmethod
    def fillout_available_node_types_resources(
        cluster_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        cluster_config = copy.deepcopy(cluster_config)
        inner_provider_cls = AnyscalePoolingNodeProvider._get_inner_provider_class_from_config(
            cluster_config
        )

        primary_provider = cluster_config["provider"]
        cluster_config["provider"] = cluster_config["provider"]["inner_provider"]

        cluster_config = inner_provider_cls.fillout_available_node_types_resources(
            cluster_config
        )

        primary_provider["inner_provider"] = cluster_config["provider"]
        cluster_config["provider"] = primary_provider
        return cluster_config

    def non_terminated_nodes(self, tag_filters: Dict[str, str]) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.non_terminated_nodes(tag_filters)

        non_terminated_nodes_request = NonTerminatedNodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            tag_filters=tag_filters,
        )
        resp = self.api_client.non_terminated_nodes_api_v2_instances_non_terminated_nodes_post(
            non_terminated_nodes_request
        )
        return [instance.instance_id for instance in resp.results]

    def is_running(self, node_id: str) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.is_running(node_id)

        resp = self.api_client.is_running_api_v2_instances_instance_id_is_running_get(
            node_id
        )
        return resp.result.is_running

    def is_terminated(self, node_id: str) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.is_terminated(node_id)

        resp = self.api_client.is_terminated_api_v2_instances_instance_id_is_terminated_get(
            node_id
        )
        return resp.result.is_terminated

    def node_tags(self, node_id: str) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.node_tags(node_id)

        resp = self.api_client.get_instance_api_v2_instances_instance_id_get(node_id)
        return resp.result.tags

    def external_ip(self, node_id: str) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.external_ip(node_id)

        resp = self.api_client.external_ip_api_v2_instances_instance_id_external_ip_get(
            node_id
        )
        return resp.result.external_ip

    def internal_ip(self, node_id: str) -> Any:
        if not self.is_provider_supported:
            return self.inner_provider.internal_ip(node_id)

        resp = self.api_client.internal_ip_api_v2_instances_instance_id_internal_ip_get(
            node_id
        )
        return resp.result.internal_ip

    def create_node_with_resources(
        self,
        node_config: Dict[str, Any],
        tags: Dict[str, str],
        count: int,
        resources: Dict[str, float],
    ) -> None:
        """Mirrors Ray's NodeProvider interface. Needed for compatibility with
        Ray Autoscaler version >=1.8.0

        Refer to
        https://github.com/anyscale/product/pull/8469
        https://github.com/ray-project/ray/blob/releases/1.8.0/python/ray/autoscaler/node_provider.py#L127
        https://github.com/ray-project/ray/blob/releases/1.8.0/python/ray/autoscaler/_private/node_launcher.py#L69
        """
        self.create_node(node_config, tags, count)

    def create_node(
        self, node_config: Dict[str, Any], tags: Dict[str, str], count: int
    ) -> None:
        if not self.is_provider_supported:
            self.inner_provider.create_node(node_config, tags, count)
            return

        create_node_request = CreateNodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            node_config=node_config,
            tags=tags,
            count=count,
        )
        # Catch, process, and repropagate remote exceptions.
        remote_exc = None
        try:
            self.api_client.create_nodes_api_v2_instances_post(create_node_request)
        except ApiException as api_exception:
            try:
                error_detail = json.loads(api_exception.body)
                ser_exc = error_detail["error"]["detail"]
                remote_exc = cloudpickle.loads(base64.b64decode(ser_exc))
            except Exception as deserialization_error:
                logger.warn(
                    "create_node() received an ApiException, "
                    "but we were unable to deserialize it "
                    f"({deserialization_error}). "
                    "Raising the ApiException unchanged."
                )
                raise api_exception

        # Raise the unwrapped error away from the try/except clause
        # so the ApiException codegenned frames do not tag along.
        if remote_exc:
            logger.warn(
                "create_node() received an ApiException. "
                "Unwrapping and raising the original remote exception instead."
            )
            raise remote_exc

    def set_node_tags(self, node_id: str, tags: Dict[str, str]) -> None:
        if not self.is_provider_supported:
            self.inner_provider.set_node_tags(node_id, tags)
            return

        set_node_tags_request = SetNodeTagsOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            instance_id=node_id,
            tags=tags,
        )

        self.api_client.set_node_tags_api_v2_instances_set_tags_post(
            set_node_tags_request
        )

    def terminate_node(self, node_id: str) -> None:
        if not self.is_provider_supported:
            self.inner_provider.terminate_node(node_id)
            return

        terminate_nodes_request = NodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            instance_ids=[node_id],
        )
        self.api_client.terminate_nodes_api_v2_instances_terminate_nodes_post(
            terminate_nodes_request
        )

    def terminate_nodes(self, node_ids: List[str]) -> None:
        if not self.is_provider_supported:
            self.inner_provider.terminate_nodes(node_ids)
            return

        terminate_nodes_request = NodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            instance_ids=node_ids,
        )
        self.api_client.terminate_nodes_api_v2_instances_terminate_nodes_post(
            terminate_nodes_request
        )

    def wait_until_stopped(self, node_id: str) -> None:
        wait_until_stopped_request = WaitUntilStoppedOptions(
            cloud_id=self.cloud_id, instance_id=node_id,
        )
        self.api_client.wait_until_stopped_api_v2_instances_wait_until_stopped_post(
            wait_until_stopped_request
        )

    def start_nodes(self, node_ids: List[str]) -> None:
        if not self.is_provider_supported:
            self.inner_provider.start_nodes(node_ids)
            return

        start_nodes_request = NodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            instance_ids=node_ids,
        )
        self.api_client.start_nodes_api_v2_instances_start_nodes_post(
            start_nodes_request
        )

    def stop_nodes(self, node_ids: List[str]) -> None:
        if not self.is_provider_supported:
            self.inner_provider.stop_nodes(node_ids)
            return

        stop_nodes_request = NodesOptions(
            provider_config=self.inner_provider.provider_config,
            cluster_name=self.inner_provider.cluster_name,
            instance_ids=node_ids,
        )
        self.api_client.stop_nodes_api_v2_instances_stop_nodes_post(stop_nodes_request)

    def get_node_id(
        self, ip_address: str, use_internal_ip: bool = False
    ) -> Optional[str]:
        if not self.is_provider_supported:
            return cast(
                str, self.inner_provider.get_node_id(ip_address, use_internal_ip)
            )

        if use_internal_ip:
            resp = self.api_client.get_node_id_by_internal_ip_api_v2_instances_internal_ip_get_node_id_by_internal_ip_get(
                ip_address
            )
        else:
            resp = self.api_client.get_node_id_by_external_ip_api_v2_instances_external_ip_get_node_id_by_external_ip_get(
                ip_address
            )

        if not resp.result.instance_id:
            raise ValueError("IP {ip_address} not found.")
        return cast(str, resp.result.instance_id)

    def get_command_runner(
        self,
        log_prefix: str,
        node_id: str,
        auth_config: Dict[str, Any],
        cluster_name: str,
        process_runner: ModuleType,
        use_internal_ip: bool,
        docker_config: Optional[Dict[str, Any]] = None,
    ) -> CommandRunnerInterface:
        """Copied from aws node provider. Need to pass
        """
        common_args = {
            "log_prefix": log_prefix,
            "node_id": node_id,
            "provider": self,
            "auth_config": auth_config,
            "cluster_name": cluster_name,
            "process_runner": process_runner,
            "use_internal_ip": use_internal_ip,
        }
        if docker_config and docker_config["container_name"] != "":
            return DockerCommandRunner(docker_config, **common_args)
        else:
            return SSHCommandRunner(**common_args)

    def prepare_for_head_node(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        cluster_config = copy.deepcopy(cluster_config)

        def delete_credentials_from_config(provider_config: Dict[str, Any]) -> None:
            """
            Context (as of 2020-12-11):
            * In order to allow an autoscaler running in our account to access a
              customer's account we have to place credentials into the cluster
              config so that the NodeProvider can find them.
            * The credentials we generate to access customer accounts are
              time-limited to expire after an hour.
            * The autoscaler will copy the provided cluster_config over to the
              head node for it to use for launching worker nodes
            * If there are credentials explicitly provided to boto3 (via the
              NodeProvider), it will not try to find alternatives if those are
              invalid.
            * The head node is launched with a role that allows it to launch
              more nodes, it does not need credentials explicitly passed to it.
            This creates a problem where we put time-limited credentials in the
            autoscaler config, which is then copied to the head node. The head
            node will then use those credentials for as long as they're valid to
            manage worker nodes. However once they expire the head node will no
            longer be able to make API calls using the explicitly provided
            credentials. 😞
            To work around this (until we have a better way to configure the
            autoscaler's API clients) is to delete any credentials we can find
            in the cluster_config before it gets handed to the node.
            """
            provider_config.pop("aws_credentials", None)

            # NodePool provider
            if "inner_provider" in provider_config:
                delete_credentials_from_config(provider_config["inner_provider"])

        delete_credentials_from_config(cluster_config.get("provider", {}))

        file_mounts = cluster_config.get("file_mounts", {})
        for remote, local in file_mounts.items():
            file_mounts[remote] = get_autoscaler_container_path(local)

        return cluster_config


class AnyscalePoolingNodeProvider(AnyscaleInstanceManagerNodeProvider):
    """NodeProvider wrapper for injecting product-specific functionality.

    https://docs.google.com/document/d/15goOexCiGkbzz7tUbILMc10Gmjf86PiyCtIl75-xGUw/edit
    """

    POOLED_INSTANCE_TAG = "anyscale-launched-from-pool"
    INSTANCE_REUSE_TAG = "anyscale-instance-reuse-id"

    def _get_from_configs(self, key: str, default: Any = KeyError) -> Any:
        """Searches both the main and inner provider configs for a key."""

        if key in self.provider_config:
            return self.provider_config[key]
        elif key in self.inner_provider_config:
            return self.inner_provider_config[key]
        elif default == KeyError:
            raise KeyError
        else:
            return default

    def create_node(
        self, node_config: Dict[str, Any], tags: Dict[str, str], count: int
    ) -> None:
        # Calculate the instance reuse ID straight away
        # so that it can be stored in the node's tags
        # for later potential insertion into the pool.
        #
        # The reuse ID is currently the hash of the node config, minus user tags.
        config_to_hash = copy.deepcopy(node_config)
        if "TagSpecifications" in config_to_hash:
            del config_to_hash["TagSpecifications"]
        instance_reuse_id = hash_launch_conf(config_to_hash, dict())
        tags[self.INSTANCE_REUSE_TAG] = instance_reuse_id

        # Only handle AWS for now.
        # TODO(xcl): add support for non-aws instances.
        bypass_rapid_start = self._get_from_configs("bypass_rapid_start", None)
        pool_disabled = self._pool_limit() == 0
        # Pooling version (with checks).
        if not (bypass_rapid_start or pool_disabled):
            if self._is_aws_provider():
                for _ in range(count):
                    self._create_single_node_aws(node_config, tags)
                return

        # Non-pooling version.
        logger.info("Configuration bypasses Rapid Start; launching node normally.")
        super().create_node(node_config, tags, count)

    def _create_single_node_aws(
        self, node_config: Dict[str, Any], tags: Dict[str, str],
    ) -> None:
        """create_node implementation for when inner provider is AWS."""

        instance_pool_request = RequestInstancePoolMember(
            cloud_id=self.cloud_id, instance_reuse_id=tags[self.INSTANCE_REUSE_TAG],
        )

        try:
            instance_pool_member = self.api_client.request_instance_from_pool_api_v2_instancepools_request_instance_post(
                instance_pool_request
            ).result
            node_id = instance_pool_member.instance_id
        except ApiException:
            # We expect to get this exception if there is no instance
            # that matches this request.
            node_id = None

        # If we get a node_id back from the instance pool,
        # start this node.
        if node_id is not None:
            logger.info("Launching node from instance pool! ID {}".format(node_id))
            super().start_nodes([node_id])

            tags[self.POOLED_INSTANCE_TAG] = "true"

            # Various mandatory tag modification logic
            # that happens in OSS under create_node.
            tags = to_aws_format(tags)
            tags[TAG_RAY_CLUSTER_NAME] = self.cluster_name
            # Add the tags from the node config's TagSpecifications.
            if "TagSpecifications" in node_config:
                for tagspec in node_config["TagSpecifications"]:
                    if tagspec["ResourceType"] == "instance":
                        for tagpair in tagspec["Tags"]:
                            tags[tagpair["Key"]] = tagpair["Value"]

            logger.info("Setting node tags on reused instance: {}".format(str(tags)))
            super().set_node_tags(node_id, tags)

        # Otherwise, start a node normally.
        else:
            logger.info("Instance pool empty; launching node from EC2.")
            super().create_node(node_config, tags, count=1)

    def terminate_node(self, node_id: str) -> None:
        # Only handle AWS for now.
        # TODO(xcl): add support for non-aws instances.
        tags = self.node_tags(node_id)
        launch_hash = tags.get(self.INSTANCE_REUSE_TAG)

        # Check prerequisites and fallback to normal termination
        # if prerequisites are not met.
        if launch_hash is None:
            logger.warn(
                "No instance reuse tag found, so node is ineligible for pool. "
                "This should only happen if the node was launched using an older CLI version. "
            )
            super().terminate_node(node_id)
            return

        if not self._is_aws_provider():
            logger.warn(
                "Instance pool not yet supported for this cloud provider; node will not be added to pool."
            )
            super().terminate_node(node_id)
            return

        if self._room_in_pool() <= 0:
            logger.warn("No room in pool; node will not be added to pool.")
            super().terminate_node(node_id)
            return

        # Prerequisites are met here;
        # proceed with putting node in instance pool.
        self._prepare_node_for_idempotent_reuse(node_id)
        # TODO(xcl): Determine which tags should be cleared vs left uncleared for correctness here.

        super().stop_nodes([node_id])
        super().wait_until_stopped(node_id)

        logger.info("Sending node {} to the instance pool.".format(node_id))

        instance_reuse_id = launch_hash
        instance_pool_submission = AddInstancePoolMember(
            instance_id=node_id,
            cloud_id=self.cloud_id,
            instance_reuse_id=instance_reuse_id,
        )
        self.api_client.add_instance_to_pool_api_v2_instancepools_add_instance_post(
            instance_pool_submission
        )

    def _prepare_node_for_idempotent_reuse(self, node_id: str) -> None:
        """Does necessary resets on node to prepare it for reuse."""

        # Currently, we will explicitly not do anything.
        # The only potential issue right now is file mounts from previous sessions,
        # which should ideally be garbage collected (TODO (xcl)),
        # but this is not a high priority because we may also just
        # expire sessions in the pool after they've been reused a lot.

    def terminate_nodes(self, node_ids: List[str]) -> None:
        # TODO(xcl): add support for non-aws instances.
        if self._is_aws_provider():
            for node_id in node_ids:
                self.terminate_node(node_id)
        else:
            super().terminate_nodes(node_ids)

    def _is_aws_provider(self) -> bool:
        """Helper method; whether the inner provider is AWS or not."""

        # 1. The inner provider can be AWS directly.
        if self.inner_provider_config["type"] == "aws":
            return True

        # 2. If the inner provider is of type "external",
        # it can still represent an AWS provider,
        # only if the corresponding module is our AnyscaleAWSNodeProvider.
        if (
            self.inner_provider_config["type"] == "external"
            and self.inner_provider_config["module"]
            == "anyscale.autoscaler.aws.node_provider.AnyscaleAWSNodeProvider"
        ):
            return True

        return False

    def _pool_size(self) -> int:
        """Get this cloud's current pool size."""
        query = QueryPoolSize(cloud_id=self.cloud_id)
        pool_size = self.api_client.pool_size_api_v2_instancepools_pool_size_post(query)
        return int(pool_size)

    def _pool_limit(self) -> int:
        """Get this cloud's pool size limit."""

        pool_limit = self.api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=self.cloud_id
        ).result.config.max_stopped_instances

        return int(pool_limit)  # already int; just cast for typing

    def _room_in_pool(self) -> int:
        return self._pool_limit() - self._pool_size()


class AnyscaleExecNodeProvider(NodeProvider):  # type: ignore
    """A temporary class for making `anyscale exec` faster.

    Only used in the frontend CLI.
    """

    def __init__(self, provider_config: Dict[str, Any], cluster_name: str) -> None:
        super().__init__(provider_config, cluster_name)
        self.dns_address = provider_config["dns_address"]

    def non_terminated_nodes(self, tag_filters: List[str]) -> List[str]:
        return [self.dns_address]

    def external_ip(self, node_id: str) -> str:
        return node_id

    def node_tags(self, node_id: str) -> Dict[str, Any]:
        # Necessary because Ray requires that head node to have this tag set.
        return {TAG_RAY_NODE_STATUS: STATUS_UP_TO_DATE}
