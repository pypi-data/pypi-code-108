"""
Fetches data required and formats output for `anyscale cloud` commands.
"""

import json
import os
from typing import Optional

import boto3
from click import ClickException, prompt

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.cloud_config import CloudConfig
from anyscale.client.openapi_client.models.write_cloud import WriteCloud
from anyscale.cloud import get_cloud_id_and_name, get_cloud_json_from_id
import anyscale.conf
from anyscale.controllers.base_controller import BaseController
from anyscale.formatters import clouds_formatter
from anyscale.util import (
    _CACHED_GCP_REGIONS,
    _get_role,
    _resource,
    confirm,
    get_available_regions,
    launch_gcp_cloud_setup,
)


class CloudController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def delete_cloud(
        self,
        cloud_name: Optional[str],
        cloud_id: Optional[str],
        skip_confirmation: bool,
    ) -> bool:
        """
        Deletes a cloud by name or id.
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        confirm(
            f"You'll lose access to existing sessions created with cloud {cloud_id} if you drop it.\nContinue?",
            skip_confirmation,
        )

        self.api_client.delete_cloud_api_v2_clouds_cloud_id_delete(cloud_id=cloud_id)

        self.log.info(f"Deleted cloud {cloud_name}")

        return True

    def list_clouds(self, cloud_name: Optional[str], cloud_id: Optional[str]) -> str:
        if cloud_id is not None:
            clouds = [
                self.api_client.get_cloud_api_v2_clouds_cloud_id_get(cloud_id).result
            ]
        elif cloud_name is not None:
            clouds = [
                self.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post(
                    {"name": cloud_name}
                ).result
            ]
        else:
            clouds = self.api_client.list_clouds_api_v2_clouds_get().results
        output = clouds_formatter.format_clouds_output(clouds=clouds, json_format=False)

        return str(output)

    def setup_cloud(
        self,
        is_aioa: bool,
        provider: str,
        region: Optional[str],
        name: str,
        yes: bool = False,
        folder_id: Optional[int] = None,
    ) -> None:
        """
        Sets up a cloud provider
        """

        if is_aioa:
            return self.setup_aioa(provider=provider, region=region, name=name, yes=yes)

        if provider == "aws":
            # If the region is blank, change it to the default for AWS.
            if region is None:
                region = "us-west-2"
            self.setup_aws(region=region, name=name, yes=yes)
        elif provider == "gcp":
            # If the region is blank, change it to the default for GCP.
            if region is None:
                region = "us-west1"
            # Warn the user about a bad region before the cloud configuration begins.
            # GCP's `list regions` API requires a project, meaning true verification
            # happens in the middle of the flow.
            if region not in _CACHED_GCP_REGIONS and not yes:
                confirm(
                    f"You selected the region: {region}, but it is not in"
                    f"the cached list of GCP regions:\n\n{_CACHED_GCP_REGIONS}.\n"
                    "Continue cloud setup with this region?",
                    False,
                )
            if not yes and not folder_id:
                folder_id = prompt(
                    "Please select the GCP Folder ID where the 'Anyscale' folder will be created.\n"
                    "\tYour GCP account must have permissions to create sub-folders in the specified folder.\n"
                    "\tView your organization's folder layout here: https://console.cloud.google.com/cloud-resource-manager\n"
                    "\tIf not specified, the 'Anyscale' folder will be created directly under the organization.\n"
                    "Folder ID (numerals only)",
                    default="",
                    type=int,
                    show_default=False,
                )
            # TODO: interactive setup process through the CLI?
            launch_gcp_cloud_setup(name=name, region=region, folder_id=folder_id)
        else:
            raise ClickException(
                f"Invalid Cloud provider: {provider}. Available providers are [aws, gcp]."
            )

    def setup_aioa(
        self, provider: str, region: Optional[str], name: str, yes: bool
    ) -> None:
        if provider == "aws":
            if region is None:
                region = "us-west-2"
        else:
            raise ClickException(
                f"Cannot use {provider}. "
                "Currently, only AWS is supported when running in Anyscale's cloud provider account."
            )

        self.api_client.create_cloud_api_v2_clouds_post(
            write_cloud=WriteCloud(
                provider=provider.upper(),
                region=region,
                credentials="",
                name=name,
                is_aioa=True,
                is_k8s=True,  # All AIOA clouds are K8s clouds.
            )
        )

    def setup_aws(self, region: str, name: str, yes: bool = False) -> None:
        from ray.autoscaler._private.aws.config import DEFAULT_RAY_IAM_ROLE

        os.environ["AWS_DEFAULT_REGION"] = region
        regions_available = get_available_regions()
        if region not in regions_available:
            raise ClickException(
                f"Region '{region}' is not available. Regions availables are {regions_available}"
            )

        confirm(
            "\nYou are about to give anyscale full access to EC2 and IAM in your AWS account.\n\n"
            "Continue?",
            yes,
        )

        self.setup_aws_cross_account_role(region, name)
        self.setup_aws_ray_role(region, DEFAULT_RAY_IAM_ROLE)

        self.log.info("AWS credentials setup complete!")
        self.log.info(
            "You can revoke the access at any time by deleting anyscale IAM user/role in your account."
        )
        self.log.info(
            "Head over to the web UI to create new sessions in your AWS account!"
        )

    def setup_aws_cross_account_role(self, region: str, name: str) -> None:
        response = (
            self.api_client.get_anyscale_aws_account_api_v2_clouds_anyscale_aws_account_get()
        )

        anyscale_aws_account = response.result.anyscale_aws_account
        anyscale_aws_iam_role_policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Sid": "1",
                "Effect": "Allow",
                "Principal": {"AWS": anyscale_aws_account},
                "Action": "sts:AssumeRole",
            },
        }

        role = _get_role(anyscale.conf.ANYSCALE_IAM_ROLE_NAME, region)

        if role is None:
            iam = _resource("iam", region)
            iam.create_role(
                RoleName=anyscale.conf.ANYSCALE_IAM_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(anyscale_aws_iam_role_policy),
            )
            role = _get_role(anyscale.conf.ANYSCALE_IAM_ROLE_NAME, region)

        assert role is not None, "Failed to create IAM role!"

        role.attach_policy(PolicyArn="arn:aws:iam::aws:policy/AmazonEC2FullAccess")
        role.attach_policy(PolicyArn="arn:aws:iam::aws:policy/IAMFullAccess")

        self.log.info(f"Using IAM role {role.arn}")

        self.api_client.create_cloud_api_v2_clouds_post(
            write_cloud=WriteCloud(
                provider="AWS", region=region, credentials=role.arn, name=name,
            )
        )

    def setup_aws_ray_role(self, region: str, role_name: str) -> None:
        iam = boto3.resource("iam", region_name=region)

        role = _get_role(role_name, region)
        if role is None:
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": {
                            "Effect": "Allow",
                            "Principal": {"Service": ["ec2.amazonaws.com"]},
                            "Action": "sts:AssumeRole",
                        },
                    }
                ),
            )

            role = _get_role(role_name, region)

        # Modified permissions from Ray (no EC2FullAccess)
        role.attach_policy(PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")

        # Also attach a role to allow it to launch more nodes with itself
        role.Policy("PassRoleToSelf").put(
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PassRoleToSelf",
                            "Effect": "Allow",
                            "Action": "iam:PassRole",
                            "Resource": role.arn,
                        }
                    ],
                }
            )
        )

    def update_cloud_config(
        self,
        cloud_name: Optional[str],
        cloud_id: Optional[str],
        max_stopped_instances: int,
    ) -> None:
        """Updates a cloud's configuration by name or id.

        Currently the only supported option is "max_stopped_instances."
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        self.api_client.update_cloud_config_api_v2_clouds_cloud_id_config_put(
            cloud_id=cloud_id,
            cloud_config=CloudConfig(max_stopped_instances=max_stopped_instances),
        )

        self.log.info(f"Updated config for cloud '{cloud_name}' to:")
        self.log.info(self.get_cloud_config(cloud_name=None, cloud_id=cloud_id))

    def get_cloud_config(
        self, cloud_name: Optional[str] = None, cloud_id: Optional[str] = None,
    ) -> str:
        """Get a cloud's current JSON configuration."""

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        return str(get_cloud_json_from_id(cloud_id, self.api_client)["config"])

    def set_default_cloud(
        self, cloud_name: Optional[str], cloud_id: Optional[str],
    ) -> None:
        """
        Sets default cloud for caller's organization. This operation can only be performed
        by organization admins, and the default cloud must have organization level
        permissions.
        """

        if not cloud_id and not cloud_name:
            raise ClickException("Must either provide the cloud name or cloud id.")

        cloud_id, cloud_name = get_cloud_id_and_name(
            self.api_client, cloud_id, cloud_name
        )

        self.api_client.update_default_cloud_api_v2_organizations_update_default_cloud_post(
            cloud_id=cloud_id
        )

        self.log.info(f"Updated default cloud to {cloud_name}")
