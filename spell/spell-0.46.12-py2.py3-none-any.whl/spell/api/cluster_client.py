from spell.api import base_client
from spell.api.utils import url_path_join
import json

CLUSTER_RESOURCE_URL = "clusters"

# Note(Brian):
# - connection timeout is slightly larger than a multiple of 3 as recommended
#   here: http://docs.python-requests.org/en/master/user/advanced/#timeouts
# - read timeout is set to 120 seconds to mitigate previous issues seen with stale
#   long-lived connections
CONN_TIMEOUT = 6.05
READ_TIMEOUT = 120


class ClusterClient(base_client.BaseClient):
    def get_cluster(self, cluster_name):
        """Get info for a cluster given a cluster_name.

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name))
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def list_clusters(self):
        """List info for all current owner clusters."""
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner))
        self.check_and_raise(r)
        return self.get_json(r)["clusters"]

    def validate_cluster_name(self, name):
        """Throws an error if this name is an illegal name for a cluster.

        Keyword arguments:
        name -- a potential name for a cluster
        """
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner, "validate_name", name))
        self.check_and_raise(r)

    def create_aws_cluster(
        self,
        name,
        role_arn,
        external_id,
        read_policy,
        security_group_id,
        s3_bucket,
        vpc_id,
        subnets,
        region,
    ):
        """Construct a cluster to map to a users aws cluster.

        Keyword arguments:
        name -- a display name for the cluster
        role_arn -- the aws arn of a role granting Spell necessary permissions to manage the cluster
        external_id -- needed to assume the role
        read_policy -- name of the s3 read policy associated with the IAM role
        security_group_id -- security group in the VPC with SSH and Docker port access to workers
        s3_bucket - a bucket to store run outputs in
        vpc_id - the id of vpc to setup this cluster in
        subnets - all subnets which Spell will attempt to launch machines in
            (due to aws capacity constraints more is preferable)
        region - the aws region of this vpc
        """
        payload = {
            "cluster_name": name,
            "role_arn": role_arn,
            "external_id": external_id,
            "read_policy": read_policy,
            "security_group_id": security_group_id,
            "s3_bucket": s3_bucket,
            "vpc_id": vpc_id,
            "subnets": subnets,
            "region": region,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "aws")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def create_gcp_cluster(
        self,
        name,
        service_account_id,
        gs_bucket,
        vpc_id,
        subnet,
        region,
        project,
        gs_access_key_id,
        gs_secret_access_key,
        api_key,
    ):
        """Construct a cluster to map to a users gcp cluster.

        Keyword arguments:
        name -- a display name for the cluster
        service_account_id -- the email of a service account granting Spell necessary permissions to manage the cluster
        gs_bucket - a bucket to store run outputs in
        vpc_id - name of network to run machines in
        subnets - a subnet in vpc_id to run machines in
        region - region in which the subnets live
        project - project that network lives in
        gs_access_key_id - gs interoperable s3 access key
        gs_secret_access_key - gs interoperable s3 access secret
        """

        payload = {
            "cluster_name": name,
            "gs_bucket": gs_bucket,
            "vpc_id": vpc_id,
            "subnet": subnet,
            "region": region,
            "project": project,
            "service_account_id": service_account_id,
            "gs_access_key_id": gs_access_key_id,
            "gs_secret_access_key": gs_secret_access_key,
            "gcp_account_api_key": api_key,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "gcp")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def create_azure_cluster(
        self,
        name,
        app_object_id,
        client_id,
        client_secret,
        region,
        resource_group_name,
        sp_object_id,
        storage_account_name,
        storage_key,
        subscription_id,
        tenant_id,
        cluster_version,
    ):
        """Construct a cluster to map to a users azure cluster.

        Keyword arguments:
        name -- a display name for the cluster
        app_object_id - the object id of the app (needed for deletion)
        client_id -- service principal id
        client_secret -- service principal secret
        region - the region we are creating resources in
        resource_group_name - name of the resource group (default `spell-resource-group`)
        sp_object_id - the object id of the service principal (needed for deletion)
        storage_account_name - name of the storage account the run outputs are stored in
        storage_key - value of one of the 2 valid storage access keys for the storage account
        subscription_id -- the subscription we are using (billing)
        tenant_id -- tenant id chosen by the customer
        cluster_version -- identifier for the features included in this Spell Azure Cluster
        """

        payload = {
            "app_object_id": app_object_id,
            "cluster_name": name,
            "client_id": client_id,
            "client_secret": client_secret,
            "region": region,
            "resource_group_name": resource_group_name,
            "sp_object_id": sp_object_id,
            "storage_account_name": storage_account_name,
            "storage_key": storage_key,
            "subscription_id": subscription_id,
            "tenant_id": tenant_id,
            "cluster_version": cluster_version,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "azure")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def create_private_cluster(
        self,
        name,
        storage_path,
    ):
        """Construct a cluster of customer machines.

        Keyword arguments:
        name -- a display name for the cluster
        storage_path -- path to the networked file system on each instance
        """

        payload = {
            "cluster_name": name,
            "storage_path": storage_path,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "private")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def azure_rotate_storage_key(self, cluster_name, storage_key, bucket_name=""):
        """Sends the new key to be stored for an Azure storage account in either a cluster
        or orgbucket

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        bucket_name -- name of the org bucket, "" for the cluster storage account
        storage_key - value of one of the 2 valid storage access keys for the storage account
        """
        payload = {
            "bucket": bucket_name,
            "storage_key": storage_key,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "bucket", "azure_rotate_storage_key")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return r.status_code

    def register_serving_cluster(
        self,
        cluster_name,
        version,
        is_public=None,
        support_runs=False,
        kube_config=None,
        default_ng_config=None,
        serving_cluster_domain="",
        serving_cluster_name="",
        serving_cluster_status="",
        serving_cluster_location="",
    ):
        """Submit a model-server kubeconfig to be stored as the
        active model-server cluster for the current org.

        Important note on kwargs:
        On create kube_config can only be empty if status is "created"

        Args:
            cluster_name -- Spell cluster name for endpoint
            version -- serving cluster version

        Kwargs:
            is_public -- If false, model servers are only accessible through Spell VPC
            support_runs -- If true, alerts the API that this cluster is configured to support runs
            kube_config -- a string containing a kubeconfig generated by eksctl/gcloud.
            default_ng_config -- a dict containing the config params of the default node group
            serving_cluster_domain -- The * in *.spell.services; if not sent, the API will use org name for this
            serving_cluster_name -- Name of the serving cluster created in EKS/GKE
            serving_cluster_status -- One of "created", "provisioned" or "ready". See backend for description of status.
            serving_cluster_location -- location of serving cluster, if different from region

        """
        payload = {
            "kube_config": kube_config,
            "default_node_group_config": default_ng_config,
            "serving_cluster_version": version,
            "is_public": is_public,
            "support_runs": support_runs,
            "serving_domain_name": serving_cluster_domain,
            "serving_cluster_name": serving_cluster_name,
            "serving_cluster_status": serving_cluster_status,
            "serving_cluster_location": serving_cluster_location,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "register")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return r.status_code

    def update_serving_cluster(
        self,
        cluster_name,
        version,
        support_runs=False,
    ):
        """Update an existing model-server k8s cluster for the current org.

        Args:
            cluster_name -- Spell cluster name for endpoint
            version -- serving cluster version

        Kwargs:
            support_runs -- If true, alerts the API that this cluster is configured to support runs
        """
        payload = {
            "serving_cluster_version": version,
            "support_runs": support_runs,
            "serving_cluster_status": "ready",
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "k8s_update")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return r.status_code

    def deregister_serving_cluster(self, cluster_name):
        """Unregister a model server kubeconfig from the given cluster

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        """
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "kube_config")
        r = self.request("delete", endpoint)
        self.check_and_raise(r)

    def get_grafana_password(self, cluster_name):
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "k8s", "grafana", "credentials")
        r = self.request("get", endpoint)
        self.check_and_raise(r)
        return self.get_json(r).get("grafana_password")

    def check_supported_kube_versions(self, cluster_name):
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "k8s", "supported_versions")
        r = self.request("get", endpoint)
        self.check_and_raise(r)
        return self.get_json(r)

    def check_version_cli(self, commands, spell_version):
        payload = {
            "commands": commands,
            "spell_version": spell_version,
        }
        endpoint = url_path_join("check_cli", self.owner, "version_check")
        r = self.request("get", endpoint, payload=payload)
        self.check_and_raise(r)

    def generate_node_group_config(
        self,
        cluster_name,
        name,
        instance_type,
        accelerators=None,
        min_nodes=None,
        max_nodes=None,
        spot=None,
        disk_size=None,
    ):
        """Create an autoscaling node group within a model serving cluster

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        name -- the name of the new autoscaling group
        instance_type -- the instance type of the nodes to bring up
        accelerators -- (gcp specific) list of accelerators and counts to attach to nodes
        min_nodes -- minimum nodes for autoscaling
        max_nodes -- maximum nodes for autoscaling
        spot -- enable spot instances for nodes
        disk_size -- disk size (GB) to attach to nodes
        """
        payload = {
            "name": name,
            "instance_type": instance_type,
            "accelerators": accelerators,
            "is_spot": spot,
            "disk_size_gb": disk_size,
            "min_nodes": min_nodes,
            "max_nodes": max_nodes,
        }
        endpoint = url_path_join(
            CLUSTER_RESOURCE_URL,
            self.owner,
            cluster_name,
            "node_groups",
            "config",
        )
        r = self.request("get", endpoint, params=payload)
        self.check_and_raise(r)
        return self.get_json(r)["config"]

    def create_node_group(
        self,
        cluster_name,
        name,
        config_contents,
    ):
        """Create an autoscaling node group within a model serving cluster

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        name -- the name of the new node group
        config_contents -- contents of explicit eksctl or GKE node group config
        """
        payload = {
            "name": name,
            "config_contents": json.dumps(config_contents),
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "node_groups")
        r = self.request("post", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["node_group"]

    def scale_node_group(
        self,
        cluster_name,
        name,
        min_nodes=None,
        max_nodes=None,
    ):
        """Adjust min/max nodes of a node group

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        name -- the name of the node group
        min_nodes -- new min nodes value
        max_nodes -- new min nodes value
        """
        payload = {
            "min_nodes": min_nodes,
            "max_nodes": max_nodes,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "node_groups", name, "scale")
        r = self.request("post", endpoint, payload=payload)
        self.check_and_raise(r)

    def delete_node_group(
        self,
        cluster_name,
        name,
    ):
        """Delete a node group

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        name -- the name of the node group
        """
        endpoint = url_path_join(
            CLUSTER_RESOURCE_URL,
            self.owner,
            cluster_name,
            "node_groups",
            name,
        )
        r = self.request("delete", endpoint)
        self.check_and_raise(r)

    def add_bucket(self, bucket_name, cluster_name, provider, storage_key=None, cross_account=False):
        """Add a bucket to SpellFS using the permissions of the specified cluster

        Keyword arguments:
        bucket_name -- the name of the bucket (AWS/GCP) or blob container (Azure)
        cluster_name -- the name of the cluster
        provider -- storage provider for bucket ("s3", "gs", etc.)
        storage key (azure only) -- the storage key to the storage account they want to add
        cross_account (aws only) -- whether or not bucket access will be cross-account
        """
        payload = {
            "bucket": bucket_name,
            "provider": provider,
            "storage_key": storage_key,
            "cross_account": cross_account,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "bucket")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def remove_bucket(self, bucket_name, cluster_name, provider):
        """Add a bucket to SpellFS using the permissions of the specified cluster

        Keyword arguments:
        bucket_name -- the name of the bucket (AWS/GCP) or blob container (Azure)
        cluster_name -- the name of the cluster
        provider -- storage provider for bucket ("s3", "gs", etc.)
        """
        payload = {
            "bucket": bucket_name,
            "provider": provider,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "bucket")
        r = self.request("delete", endpoint, payload=payload)
        self.check_and_raise(r)

    def list_buckets(self, cluster_name):
        """List all buckets added to the given cluster

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "bucket"))
        self.check_and_raise(r)
        return self.get_json(r)["org_buckets"]

    def set_instance_role_identifier(self, instance_role_identifier, cluster_name):
        """Sets the instance role identifier for the cluster

        Keyword arguments:
        instance_role_identifier -- the identifier of the instance role
                                    (IAM Instance Role for AWS, IAM Service Account for GCP)
        """
        payload = {"instance_role_identifier": instance_role_identifier}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "update_instance_role_identifier")
        r = self.request("patch", endpoint, payload=payload)
        self.check_and_raise(r)

    def update_cluster_version(self, cluster_name, version):
        """Updates a cluster's version number in the database

        Keyword arguments:
        cluster_name -- the name of the cluster
        version -- the new version number to write to the database
        """
        payload = {"version": version}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "update_version")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def update_gcp_cluster_credentials(self, cluster_name, access_key=None, secret=None, api_key=None):
        """Updates a cluster's HMAC key and secret in the database

        Keyword arguments:
        cluster_name -- the name of the cluster
        access_key -- the access key for the service account, for hmac
        secret -- the secret associated with the access key, for hmac
        api_key -- api key for service account
        """
        payload = {"access_key": access_key, "secret": secret, "gcp_account_api_key": api_key}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "update_gcp_s3_key")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def delete_cluster_contents(self, cluster_name):
        """Deletes all associated Spell managed infrastructure for a cluster

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "delete_contents")
        r = self.request("put", url)
        self.check_and_raise(r)

    def is_cluster_drained(self, cluster_name):
        """Returns 200 if the cluster is drained and 400 if not

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "is_drained")
        r = self.request("get", url)
        self.check_and_raise(r)

    def delete_cluster(self, cluster_name):
        """Marks a cluster as deleted in the db

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name)
        r = self.request("delete", url)
        self.check_and_raise(r)

    def create_machine_type(
        self,
        cluster_name,
        machine_type_name,
        instance_type,
        spot,
        default_auto_resume,
        storage_size,
        min_instances,
        max_instances,
        idle_timeout_minutes,
    ):
        payload = {
            "name": machine_type_name,
            "instance_type": instance_type,
            "is_spot": spot,
            "default_auto_resume": default_auto_resume,
            "storage_size": storage_size,
            "min_instances": min_instances,
            "max_instances": max_instances,
            "idle_timeout_seconds": idle_timeout_minutes * 60,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "supply_config")
        r = self.request("post", endpoint, payload=payload)
        self.check_and_raise(r)

    def scale_machine_type(
        self,
        cluster_name,
        machine_type_id,
        min_instances,
        max_instances,
        idle_timeout_minutes,
        default_auto_resume,
    ):
        payload = {
            "min_instances": min_instances,
            "max_instances": max_instances,
            "idle_timeout_seconds": idle_timeout_minutes * 60,
            "default_auto_resume": default_auto_resume,
        }
        endpoint = url_path_join(
            CLUSTER_RESOURCE_URL,
            self.owner,
            cluster_name,
            "supply_config",
            machine_type_id,
            "edit",
        )
        r = self.request("post", endpoint, payload=payload)
        self.check_and_raise(r)

    def delete_machine_type(self, cluster_name, machine_type_id):
        endpoint = url_path_join(
            CLUSTER_RESOURCE_URL,
            self.owner,
            cluster_name,
            "supply_config",
            machine_type_id,
        )
        r = self.request("delete", endpoint)
        self.check_and_raise(r)

    def renew_token_machine_type(self, cluster_name, machine_type_id):
        endpoint = url_path_join(
            CLUSTER_RESOURCE_URL,
            self.owner,
            cluster_name,
            "supply_config",
            machine_type_id,
            "new_token",
        )
        r = self.request("post", endpoint)
        self.check_and_raise(r)
        return self.get_json(r)

    def get_node_groups(self, cluster_name):
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "node_groups")
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["node_groups"]

    def get_node_group(self, cluster_name, name):
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "node_groups", name)
        r = self.request("get", url)
        self.check_and_raise(r)
        return self.get_json(r)["node_group"]

    def cluster_kubectl(self, cluster_name, args):
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "kubectl")
        with self.request(
            "post",
            url,
            params={"args": args},
            stream=True,
            timeout=(CONN_TIMEOUT, READ_TIMEOUT),
        ) as log_stream:
            self.check_and_raise(log_stream)
            if log_stream.encoding is None:
                log_stream.encoding = "utf-8"
            for line in log_stream.iter_lines(decode_unicode=True):
                yield line
