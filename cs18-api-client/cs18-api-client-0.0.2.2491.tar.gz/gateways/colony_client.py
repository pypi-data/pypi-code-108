import json
from datetime import datetime
from typing import List, Optional, Dict
from urllib.parse import quote

import time
from isodate import duration_isoformat
from requests import Response

from gateways.apis.api_route_base import ApiRoot
from gateways.common.cs18_api_classes import BlueprintRepositoryDetails, AccessLink, \
    AddBlueprintUsingTokenRepositoryRequest, AddBlueprintGithubRepositoryRequest, \
    AddBlueprintBitbucketRepositoryRequest, BitbucketBlueprintRepositoryDetails, TerraformModuleDescriptor
from gateways.common.cs18_api_converters import Converters
from gateways.common.cs18_api_errors import UnauthorizedException, SandboxNotFound, \
    SandboxEndingFailed
from gateways.common.cs18_api_requests import (
    CreateInvitationsRequest,
    UpdateSpaceRequest,
    ProductionEnvironment, DebuggingServiceValue, SpaceCloudAccountInfraSettingsRequest,
    AddK8SComputeServiceToSpaceRequest, UpdateK8SComputeServiceInSpaceRequest, AwsCloudProviderSettingsModel,
    NewUserSurveyRequest, AddSpaceTerraformModuleRequest, UpdateSpaceTerraformModuleRequest)
from gateways.common.cs18_api_responses import (AccountStatusResponse, BlueprintFileResponse, BlueprintResponse,
                                                CatalogForGetAllResponse, CatalogForGetResponse, CloudAccountResponse,
                                                CreateProductionResponse, CreateSandboxResponse, GetSpaceResponse,
                                                GetSpacesResponse, ProductionBlueResponse, ProductionGreenResponse,
                                                ProductionResponseLean, RepositoryResponse, RoleListItemResponse,
                                                SandboxResponse, SandboxResponseLean, TokenResponse,
                                                UserInvitationResponse, UserPermittedToSpaceResponse,
                                                UserForAllUsersResponse, CloudAccountInSpaceResponse, RegionResponse,
                                                VerifyCloudProviderResponse, AccountRepositoryResponse,
                                                BlueprintValidationResponse, AccountRepositoryDetailsResponse,
                                                DirectAwsSshResponse, DirectAzureSshResponse, DirectRdpResponse,
                                                ParameterStoreItem, RepositoryProviderResponse,
                                                RepositoryRelationshipResponse, AccountExtraDetails,
                                                TerraformModuleDescriptorResponse, CustomTagOverrideResponse,
                                                SpaceTerraformModuleResponse, CustomTagWithStatisticsResponse)
from gateways.n_session import NSession
from gateways.the_gateway import TheGateway
from gateways.utils import GatewayUtils, Utils


class Colony:
    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-lines
    def __init__(self, account: str, **kwargs):
        """
        :param account: account name
        :param Keyword Arguments:
            * access_token: either access token, or long token
            * email: account email
            * password: account password
            * host: address of Colony host machine, including port. Example: 'http://192.168.30.22:5050'
            * space: current space to be used
            * api_version: api version to be used
        """
        # raising an error when not provided valid credentials
        if (not kwargs.get("access_token")) and not (kwargs.get("email") and kwargs.get("password")):
            credentials = {
                "access_token": kwargs.get("access_token"),
                "email": kwargs.get("email"),
                "password": kwargs.get("password")
            }
            raise UnauthorizedException(credentials)

        gateway = TheGateway(provider=kwargs.get("provider"), host=kwargs.get("host"))
        self.session = NSession()
        self.api_address = GatewayUtils.get_cs18_api_address(
            provider=kwargs.get("provider"), host=kwargs.get("host")
        ).lower()

        self.refresh_token = \
            kwargs.get("access_token") if kwargs.get("access_token") else \
                gateway.account_login(
                    account=account,
                    email=kwargs.get("email"),
                    password=kwargs.get("password")
                ).refresh_token

        # use either provided access_token, or login with provided credentials
        self.access_token = \
            kwargs.get("access_token") if kwargs.get("access_token") else \
                gateway.account_login(
                    account=account,
                    email=kwargs.get("email"),
                    password=kwargs.get("password")
                ).access_token

        self.session.add_header(
            "Authorization",
            "Bearer {}".format(self.access_token)
        )
        self.space = kwargs.get("space", "Trial")
        self._api_version = kwargs.get("api_version")
        self._api_root = ApiRoot(
            api_address=self.api_address, space=self.space, version=self._api_version
        )

    def change_space(self, space: str):
        self.space = space
        self._api_root = ApiRoot(
            api_address=self.api_address, space=self.space, version=self._api_version
        )
        return self

    def get_spaces(self) -> List[GetSpacesResponse]:
        method_url = self._api_root.spaces.spaces()
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        spaces_json = json.loads(resp.text)
        return [Converters.create_spaces_response(space) for space in spaces_json]

    def get_account_status(self) -> AccountStatusResponse:
        method_url = self._api_root.settings.status()
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return Converters.create_account_status_response(json.loads(resp.text))

    def get_about(self):
        method_url = self._api_root.about.api_about()
        resp = self.session.get(url=method_url)
        json_response = json.loads(resp.text)
        return json_response

    def remove_compute_service(self, cloud_account: str, compute_service: str):
        method_url = self._api_root.settings.compute_services()
        body = {"compute_service_name": f'{cloud_account}/{compute_service}'}
        res = self.session.delete(url=method_url, json=body)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_cloud_accounts_under_account(self) -> List[CloudAccountResponse]:
        method_url = self._api_root.settings.cloud_accounts()
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        json_response = json.loads(resp.text)
        cloud_accounts = [
            Converters.create_cloud_account_response(x) for x in json_response
        ]
        return cloud_accounts

    def register_azure_account(self, with_tags: bool = False, **kwargs):
        """
        :param with_tags: bool
        :param kwargs:  name: str
                        subscription_id: str,
                        tenant_id: str,
                        application_id: str,
                        application_secret: str,
                        management_resource_group: str,
                        external_key: [str]
        """
        params = {"add_tags": with_tags}
        method_url = self._api_root.settings.azure_cloud_accounts()
        request = {
            "name": kwargs.get("name"),
            "subscription_id": kwargs.get("subscription_id"),
            "tenant_id": kwargs.get("tenant_id"),
            "application_id": kwargs.get("application_id"),
            "application_secret": kwargs.get("application_secret"),
            "management_resource_group": kwargs.get("management_resource_group"),
        }
        if kwargs.get("external_key"):
            request["id"] = kwargs.get("external_key")

        resp = self.session.post(url=method_url, json=request, params=params)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def register_aws_account(
            self,
            arn_role: str,
            external_id: str,
            name: str = None,
            external_key: str = None,
    ):
        """ Register AWS
        :param arn_role: IAM role ARN required for assume role to the customer cloud account
        :param external_id: External ID required for assume role to the customer cloud account
        :param name: Cloud account given name. If not passed its automatically generated by some pattern.
        :param external_key: Predefined external key that was already generated for another cloud account.
        May be used only for CI, tests and developers environments. Should not be used in production
        """
        method_url = self._api_root.settings.aws_cloud_accounts()
        request = {"arn_role": arn_role, "external_id": external_id}

        if arn_role is not None:
            print("arn_role " + arn_role)

        if name:
            request["name"] = name
        if external_key:
            request["id"] = external_key

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def register_gcp_stub_account(self, name: str):
        method_url = self._api_root.settings.gcp_stub_cloud_accounts()
        request = {
            "name": name
        }
        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    # todo old function -> tomer delete this in phase 2
    def add_azure_aks(self,
                      name: str,
                      cloud_account_name: str,
                      kube_config: str,
                      ingress_controller_type: str = None,
                      ingress_class: str = None,
                      configure_dns: bool = False,
                      generate_certificate: bool = False):
        """ Register AKS"""
        method_url = self._api_root.settings.add_compute_service_aks()
        request = {
            "kube_config": kube_config,
            "name": name,
            "cloud_account_name": cloud_account_name,
            "ingress_controller_type": ingress_controller_type,
            "ingress_class": ingress_class,
            "configure_dns": configure_dns,
            "generate_certificate": generate_certificate
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    # todo old function -> tomer delete this in phase 2
    def add_aws_k8s_unmanaged(self,
                              name: str,
                              cloud_account_name: str,
                              kube_config: str,
                              ingress_controller_type: str = None,
                              ingress_class: str = None,
                              configure_dns: bool = False,
                              generate_certificate: bool = False):
        method_url = self._api_root.settings.add_compute_service_aws_k8s_unmanaged()
        request = {
            "kube_config": kube_config,
            "name": name,
            "cloud_account_name": cloud_account_name,
            "ingress_controller_type": ingress_controller_type,
            "ingress_class": ingress_class,
            "configure_dns": configure_dns,
            "generate_certificate": generate_certificate
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    # new api
    def add_k8s_compute_service(self,
                                compute_service_name: str,
                                cloud_account_name: str,
                                agent_namespace: str,
                                ingress_controller_type: str = None,
                                ingress_class: str = None,
                                configure_dns: bool = False,
                                generate_certificate: bool = False):
        method_url = self._api_root.settings.add_k8s_compute_service_under_cloud_account()
        request = {
            "compute_service_name": compute_service_name,
            "cloud_account_name": cloud_account_name,
            "agent_namespace": agent_namespace,
            "configure_dns": configure_dns,
            "generate_certificate": generate_certificate
        }
        if ingress_controller_type:
            request["ingress_controller_type"] = ingress_controller_type
        if ingress_class:
            request["ingress_class"] = ingress_class

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_eks_compute_service(self, cloud_account_name: str, name: str, agent_namespace: str,
                                ingress_controller_type: str = "alb", ingress_class: str = "alb",
                                configure_dns: bool = False,
                                generate_certificate: bool = False):
        method_url = self._api_root.settings.add_eks_compute_service()
        request = {
            'cloud_account_name': cloud_account_name,
            'name': name,
            'agent_namespace': agent_namespace,
            'ingress_controller_type': ingress_controller_type,
            'ingress_class': ingress_class,
            'configure_dns': configure_dns,
            'generate_certificate': generate_certificate,
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def delete_compute_service(self, cloud_account_name: str, name: str):
        method_url = self._api_root.settings.delete_compute_service()

        request = {
            'compute_service_name': cloud_account_name + "/" + name
        }

        resp = self.session.delete(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_eks_template(self, cloud_account_name: str, compute_service_name: str, sandboxes_namespace: str,
                         oidc_provider_arn: str):
        method_url = self._api_root.settings.get_aws_k8s_template()
        params = {
            'cloudAccount': cloud_account_name,
            'computeService': compute_service_name,
            'sandboxNamespaces': sandboxes_namespace,
            'oidcProviderArn': oidc_provider_arn
        }

        resp = self.session.get(url=method_url, params=params)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text

    def get_eks_agent_deployment_yaml(self, cloud_account_name: str, compute_service_name: str,
                                      sandboxes_namespace: str, role_arn: str):
        method_url = self._api_root.settings.get_eks_agent_deployment_yaml()
        params = {
            'cloudAccount': cloud_account_name,
            'computeService': compute_service_name,
            'sandboxNamespace': sandboxes_namespace,
            'roleArn': role_arn
        }

        resp = self.session.get(url=method_url, params=params)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text

    def get_k8s_agent_deployment_yaml(self, cloud_account_name: str, compute_service_name: str,
                                      sandbox_namespaces: List[str]):
        method_url = self._api_root.settings.k8s_agent_deployment_yaml(cloud_account_name=cloud_account_name,
                                                                       compute_service_name=compute_service_name,
                                                                       sandbox_namespaces=','.join(sandbox_namespaces))
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text

    def get_k8s_cluster_agents(self, cluster_id: str):
        method_url = self._api_root.agent_connector.get_k8s_cluster_agents(cluster_id=cluster_id)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text

    def rename_cloud_account(self, old_name: str, new_name: str):
        method_url = self._api_root.settings.rename_cloud_accounts(old_name, new_name)

        resp = self.session.put(url=method_url)
        GatewayUtils.handle_response(resp, return_codes=[200])

    def get_account_template_url(self, external_id: str):
        """ Register AWS
        :param external_id: External ID required for assume role to the customer cloud account"""

        method_url = "{}?external_id={}".format(
            self._api_root.settings.aws_template(), external_id
        )
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        template_json = json.loads(resp.text)
        return template_json

    def unregister_cloud_account(self, cloud_account_name: str):
        method_url = self._api_root.settings.cloud_accounts()
        body = {"cloud_account_name": cloud_account_name}
        resp = self.session.delete(url=method_url, json=body)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_aws_s3_artifacts_repo(self, account_name: str, bucket_name: str):
        method_url = self._api_root.artifacts_repository.aws_s3_storage(
            space_name=self.space
        )
        request = {"account_name": account_name, "bucket_name": bucket_name}
        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_azure_artifact_repository(self, account_name: str, storage_name: str):
        method_url = self._api_root.artifacts_repository.azure_storage(
            space_name=self.space
        )
        request = {"account_name": account_name, "storage_name": storage_name}
        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_artifact_repository(self):
        method_url = self._api_root.artifacts_repository.artifact_repos(
            space_name=self.space
        )
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return Converters.create_artifact_repo_response(json.loads(res.text))

    def get_artifact_repo_storage(self, cloud_account: str):
        method_url = self._api_root.artifacts_repository.artifact_repos_by_cloud_account_name(
            cloud_account_name=cloud_account, space_name=self.space
        )
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return json.loads(res.text)

    def remove_artifact_repository(self):
        method_url = self._api_root.artifacts_repository.artifact_repos(
            space_name=self.space
        )
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def create_long_token(self) -> TokenResponse:
        method_url = self._api_root.token.long_token()
        resp = self.session.post(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        token_json = json.loads(resp.text)
        return Converters.create_token_response(token_json)

    def revoke_long_token(self, long_token: str):
        method_url = self._api_root.token.revoke_long_token()
        self.session.add_header("Authorization", "Bearer {}".format(long_token))
        resp = self.session.post(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def list_blueprints(
            self, exclude_samples=False, deployment_type: str = None,
            branch: str = None, commit: str = None, space_name: str = None
    ) -> List[BlueprintResponse]:
        params = {}
        selected_space = space_name or self.space

        if deployment_type:
            params["type"] = deployment_type
        if branch:
            params["branch"] = branch
        if commit:
            params["commit"] = commit
        method_url = self._api_root.blueprint.blueprints_by_space_name(selected_space)
        resp = self.session.get(url=method_url, params=params)
        GatewayUtils.handle_response(response=resp, return_codes=[200, 400, 404])
        if resp.status_code in [400, 404]:
            return []
        blueprints_json = json.loads(resp.text)
        all_blueprints = [
            Converters.create_blueprint_response(blueprint)
            for blueprint in blueprints_json
        ]
        if exclude_samples:
            all_blueprints = [
                blueprint for blueprint in all_blueprints if not blueprint.is_sample
            ]
        return all_blueprints

    def list_space_users(self) -> List[UserPermittedToSpaceResponse]:
        method_url = self._api_root.spaces.space_users(self.space)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        users_json = json.loads(resp.text)
        return [
            Converters.create_user_permitted_to_space_response(user)
            for user in users_json
        ]

    def publish_blueprint_in_catalog(self, blueprint_name: str):
        method_url = self._api_root.catalog.catalog(space_name=self.space)
        request = {"blueprint_name": blueprint_name}
        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def list_blueprint_files(
            self, blueprint_name: str, branch: str
    ) -> List[BlueprintFileResponse]:
        method_url = self._api_root.blueprint.blueprint_files(
            space_name=self.space, blueprint_name=blueprint_name, branch=branch
        )
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        files = json.loads(resp.text)
        return [Converters.create_blueprint_file_response(file) for file in files]

    def list_blueprints_in_catalog(self) -> List[CatalogForGetAllResponse]:
        method_url = self._api_root.catalog.catalog(space_name=self.space)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        blueprints_json = json.loads(resp.text)
        return [
            Converters.create_catalog_blueprint_response(blueprint)
            for blueprint in blueprints_json
        ]

    def unpublish_blueprint_in_catalog(self, blueprint_name: str):
        method_url = self._api_root.catalog.blueprint_in_catalog(
            space_name=self.space, blueprint_name=blueprint_name
        )
        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_blueprint_details_in_catalog(
            self, blueprint_name: str
    ) -> CatalogForGetResponse:
        method_url = self._api_root.catalog.blueprint_in_catalog(
            space_name=self.space, blueprint_name=blueprint_name
        )
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        blueprint = json.loads(resp.text)
        return Converters.create_catalog_blueprint_full_response(blueprint)

    def list_sandboxes(self, retry: bool = True, **kwargs) -> List[SandboxResponseLean]:
        """
       :param retry: bool
       :param kwargs:  filter: str(automation/all/my),
                       sandbox_name: str,
                       count: int
       """

        method_url = self._api_root.sandbox.sandboxes()
        resp = self.session.get(url=method_url, params=kwargs)
        if resp.status_code in [408, 429]:
            if retry:
                time.sleep(30)
                return self.list_sandboxes(False, **kwargs)
            raise TimeoutError()
        GatewayUtils.handle_response(resp, return_codes=[200])
        result = json.loads(resp.text)
        return [
            Converters.create_sandbox_response_list_item(sandbox) for sandbox in result
        ]

    def list_productions(self, retry: bool = True) -> List[ProductionResponseLean]:
        url = self._api_root.production.productions()
        response = self.session.get(url=url)
        if response.status_code in [408, 429]:
            if retry:
                time.sleep(30)
                return self.list_productions(False)
            raise TimeoutError()
        GatewayUtils.handle_response(response, return_codes=[200])
        json_result = json.loads(response.text)
        return [
            Converters.create_production_response_list_item(item)
            for item in json_result
        ]

    def start_production(self, blueprint_name: str, artifacts: dict = None, inputs=None, compute_availability=None,
                         runtime_tags: Dict[str, str] = None):
        url = self._api_root.production.productions()
        response = self.session.post(
            url=url,
            json={
                "blueprint_name": blueprint_name,
                "artifacts": artifacts if artifacts else {},
                "inputs": inputs if inputs else {},
                "compute_availability": compute_availability,
                "tags": runtime_tags if runtime_tags else {}
            },
        )
        GatewayUtils.handle_response(response=response, return_codes=[202])
        json_result = json.loads(response.text)
        return CreateProductionResponse(production_id=json_result["id"])

    def start_production_green(self,
                               production_id: str,
                               artifacts: dict = None,
                               inputs=None,
                               compute_availability: str = None,
                               runtime_tags: Dict[str, str] = None):
        url = self._api_root.production.green_by_id(production_id=production_id)
        response = self.session.post(url=url, json={
            "artifacts": artifacts if artifacts else {},
            "inputs": inputs if inputs else {},
            "compute_availability": compute_availability,
            "tags": runtime_tags if runtime_tags else {}
        })
        GatewayUtils.handle_response(response=response, return_codes=[202])
        json_result = json.loads(response.text)
        return CreateProductionResponse(production_id=json_result["id"])

    def update_production_debugging_service(self, production_id: str,
                                            environment: ProductionEnvironment,
                                            value: DebuggingServiceValue):
        if environment == ProductionEnvironment.BLUE:
            url = f'{self._api_root.production.blue_debugging_service(production_id=production_id)}'
        elif environment == ProductionEnvironment.GREEN:
            url = f'{self._api_root.production.green_debugging_service(production_id=production_id)}'
        else:
            raise ValueError(f'Unknown environment "{environment}"')

        response = self.session.put(url=f'{url}?value={value.value}')
        GatewayUtils.handle_response(response=response, return_codes=[200, 202])

    def expose_green(self, production_id: str, exposure_value: int):
        url = self._api_root.production.expose_green(production_id=production_id, exposure_value=exposure_value)
        response = self.session.put(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 202])

    def delete_green(self, production_id: str):
        url = f'{self._api_root.production.delete_green(production_id=production_id)}'
        response = self.session.delete(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[202])

    def promote_green(self, production_id: str):
        url = self._api_root.production.promote_green(production_id=production_id)
        response = self.session.put(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 202])

    def start_sandbox(
            self, sandbox_name: str, blueprint_name: str, **kwargs
    ) -> CreateSandboxResponse:
        """
        :param sandbox_name: str
        :param blueprint_name: str
        :param kwargs:  artifacts: dict,
                        inputs: dict,
                        scheduled_end_time: datetime,
                        automation: bool,
                        duration: timedelta,
                        compute_availability: str,
                        lazy_load_artifacts: bool,
                        lazy_load_artifacts_timeout: int,
                        visibility: str
        """
        method_url = self._api_root.sandbox.sandboxes()
        request = {
            "blueprint_name": blueprint_name,
            "sandbox_name": sandbox_name,
            "artifacts": kwargs.get("artifacts", {}),
            "inputs": kwargs.get("inputs", {}),
            "tags": kwargs.get("tags", {}),
            "automation": kwargs.get("automation", False),
            "compute_availability": kwargs.get("compute_availability"),
            "lazy_load_artifacts": kwargs.get("lazy_load_artifacts", False),
            "lazy_load_artifacts_timeout": kwargs.get("lazy_load_artifacts_timeout", 0),
            "visibility": kwargs.get("visibility")
        }

        if kwargs.get("scheduled_end_time"):
            request["scheduled_end_time"] = datetime.isoformat(kwargs.get("scheduled_end_time"))

        if kwargs.get("duration"):
            request["duration"] = duration_isoformat(kwargs.get("duration"))

        if "branch" in kwargs or "commit" in kwargs:
            request["source"] = {
                "branch": kwargs.get("branch"),
                "commit": kwargs.get("commit"),
            }

        resp = self.session.post(
            url=method_url,
            json=request,
        )
        GatewayUtils.handle_response(response=resp, return_codes=[202])
        result = json.loads(resp.text)
        return CreateSandboxResponse(sandbox_id=result["id"])

    def end_sandbox(
            self,
            sandbox_id: str,
            retry: bool = True
    ):
        method_url = self._api_root.sandbox.sandbox_by_id(sandbox_id=sandbox_id)
        resp = self.session.delete(url=method_url)

        if resp.status_code in [408, 423, 429, 504]:
            if retry:
                time.sleep(30)  # need to make sure that the next call will not use the cached timedout error
                self.end_sandbox(sandbox_id, False)
                return

        GatewayUtils.handle_response(response=resp, return_codes=[202])

    def end_production(self, production_id: str):
        method_url = self._api_root.production.production_by_id(
            production_id=production_id
        )
        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[202])

    def end_production_green(self, production_id: str):
        method_url = self._api_root.production.green_by_id(production_id=production_id)
        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[202])

    def get_sandbox_details(
            self, sandbox_id: str, retry: bool = True
    ) -> Optional[SandboxResponse]:
        method_url = self._api_root.sandbox.sandbox_by_id(sandbox_id=sandbox_id)
        resp = self.session.get(url=method_url)
        if resp.status_code == 404:
            return None
        if resp.status_code in [408, 429]:
            if retry:
                time.sleep(30)
                return self.get_sandbox_details(sandbox_id, False)
            raise TimeoutError()

        GatewayUtils.handle_response(response=resp, return_codes=[200])
        result = json.loads(resp.text)
        sandbox_response = Converters.create_sandbox_response(result)
        return sandbox_response

    def get_production_details(
            self, production_id: str, retry: bool = True) \
            -> Optional[ProductionBlueResponse]:
        url = self._api_root.production.production_by_id(production_id)
        response = self.session.get(url=url)
        if response.status_code == 404:
            return None
        if response.status_code in [408, 429]:
            if retry:
                time.sleep(30)
                return self.get_production_details(production_id, False)
            raise TimeoutError()

        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        production_response = Converters.create_production_blue_response(json_result)
        return production_response

    def get_production_green_details(
            self,
            production_id: str,
            retry: bool = True
    ) -> Optional[ProductionGreenResponse]:
        url = self._api_root.production.green_by_id(production_id)
        response = self.session.get(url=url)
        if response.status_code == 404:
            return None
        if response.status_code in [408, 429]:
            if retry:
                time.sleep(30)
                return self.get_production_green_details(production_id, False)
            raise TimeoutError()

        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        production_response = Converters.create_production_green_response(json_result)
        return production_response

    def add_account_blueprint_repository_using_token(self, request: AddBlueprintUsingTokenRepositoryRequest):
        method_url = self._api_root.settings.add_repository_by_token()
        resp = self.session.post(url=method_url, json=request.__dict__)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_account_blueprint_github_repository(self, request: AddBlueprintGithubRepositoryRequest):
        method_url = self._api_root.settings.add_github_repository()
        resp = self.session.post(url=method_url, json=request.__dict__)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_account_blueprint_bitbucket_repository(self, request: AddBlueprintBitbucketRepositoryRequest):
        method_url = self._api_root.settings.add_bitbucket_repository()
        resp = self.session.post(url=method_url, json=request.__dict__)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def delete_account_blueprint_repository(self, name: str):
        method_url = self._api_root.settings.repository(name)
        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_account_blueprint_repositories(self) -> List[AccountRepositoryResponse]:
        url = self._api_root.settings.repositories()
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

        repositories_json = json.loads(response.text)
        return [Converters.create_account_repository_response(repository) for repository in repositories_json]

    def get_account_blueprint_repository(self, repository_name: str) -> AccountRepositoryResponse:
        method_url = self._api_root.settings.repository(repository_name)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

        repository_json = json.loads(response.text)
        return Converters.create_account_repository_response(repository_json)

    def get_account_blueprint_repository_details(self, repository_name: str) -> AccountRepositoryDetailsResponse:
        method_url = self._api_root.settings.repository_details(repository_name)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

        repository_details_json = json.loads(response.text)
        return Converters.create_account_repository_details_response(repository_details_json)

    def add_repository_to_space(
            self,
            repository_details: BlueprintRepositoryDetails,
            deployment_type: str = None,
            space_name: str = None,
            wait_for_cache_refresh: bool = False,
    ):
        print(
            f'repository_url: {repository_details.repository_url} access_token: {repository_details.access_token}')
        if space_name is None:
            space_name = self.space
        method_url = self._api_root.spaces.space_repositories(space_name=space_name)
        request = {
            "repository_url": repository_details.repository_url,
            "access_token": repository_details.access_token,
            "repository_type": repository_details.repository_type,
            "branch": repository_details.branch,
            "type": deployment_type
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

        if wait_for_cache_refresh:
            Utils.wait_for(
                func=lambda: (self.list_blueprints(exclude_samples=True) is not False),
                interval_sec=5,
                max_retries=24,
                subject="blueprints ready",
            )

    def add_bitbucket_repository_to_space_via_token(
            self,
            bitbucket_blueprint_repository_details: BitbucketBlueprintRepositoryDetails,
            deployment_type: str = None,
            wait_for_cache_refresh: bool = False,
    ):

        method_url = self._api_root.spaces.space_repositories(space_name=self.space, repository_type="bitbucket")
        request = {
            "repository_url": bitbucket_blueprint_repository_details.blueprint_repository_details.repository_url,
            "code": bitbucket_blueprint_repository_details.auth_code,
            "repository_type": bitbucket_blueprint_repository_details.blueprint_repository_details.repository_type,
            "branch": bitbucket_blueprint_repository_details.blueprint_repository_details.branch,
            "type": deployment_type,
            "redirection_url": bitbucket_blueprint_repository_details.redirect_url
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

        if wait_for_cache_refresh:
            Utils.wait_for(
                func=lambda: (self.list_blueprints(exclude_samples=True) is not False),
                interval_sec=5,
                max_retries=24,
                subject="blueprints ready",
            )

    def remove_repository_from_space(self, wait_for_cache_refresh=False, space_name: str = None,
                                     deployment_type: str = None):
        if space_name is None:
            space_name = self.space
        method_url = self._api_root.spaces.space_repositories(space_name=space_name, deployment_type=deployment_type)
        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

        if wait_for_cache_refresh:
            Utils.wait_for(
                func=lambda: (self.list_blueprints(exclude_samples=True) is not True),
                interval_sec=5,
                max_retries=24,
                subject="blueprints removed",
            )

    def get_tfstate_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_tfstate(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def get_prepatetags_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_preparetags(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def get_tfinit_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_tfinit(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def get_tfplan_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_tfplan(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def get_tfapply_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_tfapply(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def get_tfdestroy_file(self, sandbox_id: str, service_name: str) -> bytes:
        method_url = self._api_root.sandbox.sandbox_tfdestroy(sandbox_id=sandbox_id, service_name=service_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.content

    def validate_blueprint(self, blueprint: str, deployment_type: str = 'sandbox', branch: str = None,
                           commit: str = None) -> BlueprintValidationResponse:
        method_url = self._api_root.blueprint_validation.blueprint_validation_by_space_name(space_name=self.space)
        request = {"blueprint_name": blueprint,
                   "type": deployment_type}
        if branch or commit:
            request['source'] = {"branch": branch,
                                 "commit": commit}
        response = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        return Converters.create_blueprint_validation_response(json_result)

    def invite_user(self, invites: CreateInvitationsRequest):
        method_url = self._api_root.account.invitations()
        resp = self.session.post(url=method_url, json=invites.__dict__)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_invites(self, space_name: str = None) -> List[UserInvitationResponse]:
        method_url = self._api_root.account.account_invitations(space=space_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        result = json.loads(resp.text)
        return [Converters.create_user_invitation_response(x) for x in result]

    def get_invited_user_details_by_secret(self, secret: str):
        method_url = self._api_root.account.account_signup_by_secret(secret=secret)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        result = json.loads(resp.text)
        return Converters.create_invited_user_details_response(result)

    def remove_invites(self, emails: List[str]):
        method_url = self._api_root.account.account_invitations()
        req = {"emails": emails}
        resp = self.session.delete(url=method_url, json=req)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def list_repositories(
            self, repository_type: str = None
    ) -> List[RepositoryResponse]:
        params = {}
        if repository_type:
            params["type"] = repository_type
        url = self._api_root.spaces.space_repositories(space_name=self.space)
        response = self.session.get(url=url, params=params)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        return [Converters.create_repository_response(x) for x in json_result]

    def update_scheduled_end_time(self, sandbox_id: str, scheduled_end_time: datetime):
        url = "{base}?value={end_time}".format(
            base=self._api_root.sandbox.sandbox_scheduled_end_time(
                sandbox_id=sandbox_id
            ),
            end_time=quote(scheduled_end_time.isoformat()),
        )
        response = self.session.put(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def turn_on_debugging_service(self, sandbox_id: str):
        self.update_debugging_service(sandbox_id=sandbox_id, value=DebuggingServiceValue.ON)

    def turn_off_debugging_service(self, sandbox_id: str):
        self.update_debugging_service(sandbox_id=sandbox_id, value=DebuggingServiceValue.OFF)

    def update_debugging_service(self, sandbox_id: str, value: DebuggingServiceValue):
        url = self._api_root.sandbox.sandbox_debugging_service(sandbox_id=sandbox_id)
        response = self.session.put(url=f'{url}?value={value.value}')
        GatewayUtils.handle_response(response=response, return_codes=[200, 202])

    def get_space_achievements(self) -> dict:
        url = self._api_root.achievements.achievements(space_name=self.space)
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response, [200])
        return json.loads(response.text)

    def create_space(self, space_name: str, cloud_accounts: List[str] = None):
        url = self._api_root.spaces.spaces()
        request = {"name": space_name, "cloud_accounts": cloud_accounts}

        response = self.session.post(url=url, json=request)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def delete_space(self, space_name: str):
        url = self._api_root.spaces.space_by_name(space_name=space_name)
        response = self.session.delete(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_space(self, name: str) -> GetSpaceResponse:
        url = self._api_root.spaces.space_by_name(space_name=name)
        res = self.session.get(url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return GetSpaceResponse(json.loads(res.text))

    def get_images(self, space_name: str, cloud_account_name: str, region_id: str):
        url = self._api_root.spaces.get_images(space_name, cloud_account_name, region_id)
        res = self.session.get(url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return [Converters.get_image_response(x) for x in json.loads(res.text)]

    def get_instance_types(self, space_name: str, cloud_account_name: str, region_id: str):
        url = self._api_root.spaces.get_instance_types(space_name, cloud_account_name, region_id)
        res = self.session.get(url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return [Converters.get_instance_type_response(x) for x in json.loads(res.text)]

    def update_space(self, space: str, update_space_request: UpdateSpaceRequest):
        url = self._api_root.spaces.space_by_name(space_name=space)
        response = self.session.put(url=url, json=update_space_request.__dict__)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_space_roles(self) -> List[RoleListItemResponse]:
        url = self._api_root.settings.space_roles()
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        roles_json = json.loads(response.text)
        return [Converters.create_role_list_item_response(role) for role in roles_json]

    def get_account_roles(self) -> List[RoleListItemResponse]:
        url = self._api_root.settings.account_roles()
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        roles_json = json.loads(response.text)
        return [Converters.create_role_list_item_response(role) for role in roles_json]

    def remove_cloud_account_from_space(self, cloud_account: str):
        method_url = self._api_root.spaces.space_cloud_account(
            self.space, cloud_account
        )
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def add_cloud_account_to_space(self, cloud_account: str,
                                   infra_settings: SpaceCloudAccountInfraSettingsRequest = None):
        method_url = self._api_root.spaces.space_cloud_accounts(self.space)
        data = {"name": cloud_account}
        if infra_settings:
            data['internet_facing'] = infra_settings.internet_facing
            data['existing_infra'] = infra_settings.existing_infra
            if infra_settings.existing_infra_sets:
                existing_infra_sets = []
                for infra_set in infra_settings.existing_infra_sets:
                    existing_infra_sets.append(
                        {
                            'region': infra_set.region,
                            'virtual_network': infra_set.virtual_network,
                            'subnets': {'gateway_subnet': infra_set.subnets.gateway_subnet,
                                        'management_subnet': infra_set.subnets.management_subnet,
                                        'application_subnets': infra_set.subnets.application_subnets
                                        } if infra_set.subnets else None
                        }
                    )
                data['existing_infra_sets'] = existing_infra_sets
        res = self.session.post(url=method_url, json=data)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_cloud_account_in_space(self, cloud_account: str, infra_settings: SpaceCloudAccountInfraSettingsRequest):
        method_url = self._api_root.spaces.space_cloud_account(space_name=self.space, cloud_account=cloud_account)
        data = {
            'internet_facing': infra_settings.internet_facing,
            'existing_infra': infra_settings.existing_infra
        }
        if infra_settings.existing_infra_sets:
            existing_infra_sets = []
            for infra_set in infra_settings.existing_infra_sets:
                existing_infra_sets.append(
                    {
                        'region': infra_set.region,
                        'virtual_network': infra_set.virtual_network,
                        'subnets': {'gateway_subnet': infra_set.subnets.gateway_subnet,
                                    'management_subnet': infra_set.subnets.management_subnet,
                                    'application_subnets': infra_set.subnets.application_subnets
                                    } if infra_set.subnets else None
                    }
                )
            data['existing_infra_sets'] = existing_infra_sets
        res = self.session.put(url=method_url, json=data)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_cloud_accounts_under_space(self) -> List[CloudAccountInSpaceResponse]:
        method_url = self._api_root.spaces.space_cloud_accounts(self.space)
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return [
            Converters.create_cloud_account_in_space_response(x) for x in json.loads(res.text)
        ]

    def add_compute_service_to_space(self, cloud_account: str, request: AddK8SComputeServiceToSpaceRequest):
        method_url = self._api_root.spaces.space_cloud_account_compute_services(space_name=self.space,
                                                                                cloud_account=cloud_account)
        res = self.session.post(url=method_url, json=request.__dict__)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_compute_service_in_space(self, cloud_account: str, compute_service: str,
                                        request: UpdateK8SComputeServiceInSpaceRequest):
        method_url = self._api_root.spaces.space_cloud_account_compute_service(space_name=self.space,
                                                                               cloud_account=cloud_account,
                                                                               compute_service=compute_service)
        res = self.session.put(url=method_url, json=request.__dict__)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def remove_compute_service_from_space(self, cloud_account: str, compute_service: str):
        method_url = self._api_root.spaces.space_cloud_account_compute_service(space_name=self.space,
                                                                               cloud_account=cloud_account,
                                                                               compute_service=compute_service)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_account_users(self) -> List[UserForAllUsersResponse]:
        method_url = self._api_root.account.account_users()
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        users_json = json.loads(res.text)
        return [Converters.create_user_for_all_users_response(x) for x in users_json]

    def get_space_permissions(self) -> List[str]:
        method_url = self._api_root.spaces.user_permissions(self.space)
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return json.loads(res.text)

    def delete_account(self, account_name: str):
        method_url = self._api_root.account.delete_account(account_name)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return res.text

    def contact_me(self, first_name: str, last_name: str, email: str, phone: str):
        method_url = self._api_root.account.contact_me()
        request = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone
        }
        res = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def add_user_to_space(self, user_email: str, space_role: str):
        method_url = self._api_root.spaces.space_users(self.space)
        request = {"email": user_email, "space_role": space_role}
        res = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_user_space_role(self, user_email: str, space_role: str):
        method_url = self._api_root.spaces.user_space_role(self.space, user_email, space_role)
        res = self.session.put(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def remove_user_from_space(self, user_email: str):
        method_url = self._api_root.spaces.space_user(self.space, user_email)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_user_account_role(self, user_email: str, account_role: str):
        method_url = self._api_root.account.account_user_account_role_value(user_email, account_role)
        res = self.session.put(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def remove_user_account_role(self, user_email: str):
        method_url = self._api_root.account.account_user_account_role(user_email)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_access_url_by_link(self, access_link: AccessLink) -> str:
        method_url = f"{self.api_address}{access_link.link}"
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        res_json = json.loads(res.text)
        return res_json['url']

    def get_access_url_by_params(self, sandbox_id: str, instance_id: str, protocol: str) -> str:
        method_url = self._api_root.qualiy.connect(sandbox_id=sandbox_id, instance_id=instance_id, protocol=protocol)
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        res_json = json.loads(res.text)
        return res_json['url']

    def delete_user(self, user_email: str):
        method_url = self._api_root.account.account_user(user_email)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def add_artifactory_repo(self, server_url: str, artifactory_username: str, api_key: str):
        method_url = self._api_root.artifacts_repository.artifactory(space_name=self.space)
        request = {
            "server_url": server_url,
            "artifactory_username": artifactory_username,
            "api_key": api_key
        }
        response = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_account_cost_breakdown(self, frm: datetime, until: datetime, criteria: str = 'blueprint') -> dict:
        url = self._api_root.account_cost.breakdown(frm=frm, until=until, criteria=criteria)
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response, [200])
        return json.loads(response.text)

    def get_cost_breakdown(self, frm: datetime, until: datetime, criteria: str = 'blueprint') -> dict:
        url = self._api_root.cost.breakdown(space_name=self.space, frm=frm, until=until, criteria=criteria)
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response, [200])
        return json.loads(response.text)

    def get_cost_usage(self, date: datetime, timezone: str = '') -> dict:
        url = self._api_root.cost.usage(space_name=self.space, date=date, timezone=timezone)
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response, [200])
        return json.loads(response.text)

    def post_request(self, url: str, request_json: dict, return_codes: List = None):
        return_codes = return_codes or [200]
        response = self.session.post(url=url, json=request_json)
        GatewayUtils.handle_response(response=response, return_codes=return_codes)

    def put_request(self, url: str, request_json: dict, return_codes: List = None):
        return_codes = return_codes or [200]
        response = self.session.put(url=url, json=request_json)
        GatewayUtils.handle_response(response=response, return_codes=return_codes)

    def set_account_extra_details(self, account_name: str, sso_enabled: bool, anonymous_users: bool,
                                  sso_update_enabled: bool):
        set_account_extra_details_url = self._api_root.account.set_account_extra_details(account_name)
        self.put_request(set_account_extra_details_url, {"sso_enabled": sso_enabled, "anonymous_users": anonymous_users,
                                                         "sso_update_enabled": sso_update_enabled}
                         , return_codes=[200])

    def get_account_extra_details(self, account_name: str) -> AccountExtraDetails:
        get_account_extra_details_url = self._api_root.account.get_account_extra_details(account_name)
        response = self.session.get(url=get_account_extra_details_url)
        GatewayUtils.handle_response(response, [200])
        return Converters.create_account_extra_details(json=json.loads(response.text))

    def get_space_cloud_account_regions(self, space_name: str, cloud_account_name: str) -> List[RegionResponse]:
        method_url = self._api_root.spaces.space_cloud_account_regions(space_name=space_name,
                                                                       cloud_account_name=cloud_account_name)
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        regions_json = json.loads(resp.text)
        return [Converters.create_space_cloud_account_regions_response(region) for region in regions_json]

    def verify_cloud_account(self, cloud_account_name: str) -> VerifyCloudProviderResponse:
        method_url = self._api_root.settings.verify_cloud_account(cloud_account_name)
        res = self.session.put(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        verify_json = json.loads(res.text)
        return Converters.create_verify_response(verify_json)

    def get_space_sandbox_repository(self, space_name: str):
        method_url = self._api_root.spaces.space_sandbox_repository(space_name)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 204])
        if not response.text:
            return None
        response_json = json.loads(response.text)
        return Converters.create_space_repository_response(response_json)

    def get_space_production_repository(self, space_name: str):
        method_url = self._api_root.spaces.space_production_repository(space_name)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 204])
        if not response.text:
            return None
        response_json = json.loads(response.text)
        return Converters.create_space_repository_response(response_json)

    def get_debugging_pem_file_content(self, space_name: str, sandbox_id: str, instance_id: str) -> str:
        method_url = self._api_root.debugging.get_aws_pem_file(space_name, sandbox_id, instance_id)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        return response.text

    def get_direct_aws_ssh_connect(self, space_name: str, sandbox_id: str, instance_id: str) -> DirectAwsSshResponse:
        method_url = self._api_root.debugging.get_direct_aws_ssh_connect(space_name, sandbox_id, instance_id)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        response_json = json.loads(response.text)
        return Converters.create_direct_aws_ssh_response(response_json)

    def get_direct_azure_ssh_connect(self, space_name: str, sandbox_id: str, instance_id: str) \
            -> DirectAzureSshResponse:
        method_url = self._api_root.debugging.get_direct_azure_ssh_connect(space_name, sandbox_id, instance_id)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        response_json = json.loads(response.text)
        return Converters.create_direct_azure_ssh_response(response_json)

    def get_debugging_rdp_file_content(self, space_name: str, sandbox_id: str, instance_id: str) -> str:
        method_url = self._api_root.debugging.get_direct_rpd_file(space_name, sandbox_id, instance_id)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        return response.text

    def get_direct_rdp_connect(self, space_name: str, sandbox_id: str, instance_id: str) -> DirectRdpResponse:
        method_url = self._api_root.debugging.get_direct_rpd_connect(space_name, sandbox_id, instance_id)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        response_json = json.loads(response.text)
        return Converters.create_direct_rdp_response(response_json)

    def add_parameter_store(self, parameter: ParameterStoreItem):
        method_url = self._api_root.parameterStore.parameters()
        response = self.session.post(url=method_url, json=Utils.get_as_json(parameter))
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_all_parameters(self):
        method_url = self._api_root.parameterStore.parameters()
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 204])
        response_json = json.loads(response.text)
        return Converters.create_get_all_parameters_response(response_json)

    def get_parameter(self, parameter_name: str):
        method_url = self._api_root.parameterStore.parameter(parameter_name=parameter_name)
        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200, 204])
        response_json = json.loads(response.text)
        return Converters.create_get_parameter_response(response_json)

    def delete_parameter(self, parameter_name: str):
        method_url = self._api_root.parameterStore.parameter(parameter_name=parameter_name)
        response = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def set_aws_cloud_provider_settings(self, model: AwsCloudProviderSettingsModel):
        method_url = self._api_root.settings.aws_cloud_providers()

        response = self.session.put(url=method_url, json=model.__dict__)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_aws_cloud_provider_settings(self) -> AwsCloudProviderSettingsModel:
        method_url = self._api_root.settings.aws_cloud_providers()

        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        response_json = json.loads(response.text)
        return Converters.aws_cloud_provider_settings_model(data=response_json)

    def add_repository_provider_to_account(
            self,
            provider_name: str,
            repository=None,
            repo_relationship=None,
            repo_type="github"
    ):
        method_url = self._api_root.settings.repository_providers()
        request = {
            "name": provider_name,
            "type": repo_type,
        }

        if repository:
            repos = [{
                "name": repository['repository_name'],
                "allow_sharing": True,
                "open_access": True,
                "repository_url": repository['repository_details'].repository_url,
                "connection_details": {
                    "token": repository['repository_details'].access_token
                },
                "repository_relationships": None
            }]

            request["repos"]: List[dict] = repos

            if repo_relationship:
                repository_relationships = [{
                    "deployment_type": repo_relationship['deployment_type'],
                    "account_repository_name": repo_relationship['repository_name'],
                    "branch": repo_relationship['branch'],
                    "space_name": repo_relationship['space_name'],
                }]

                request["repos"][0]["repository_relationships"]: List[dict] = repository_relationships

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text.replace('"', '')

    def get_repository_provider(
            self,
            provider_name: str
    ) -> RepositoryProviderResponse:
        method_url = self._api_root.settings.repository_provider(provider_name)

        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        json_result = json.loads(resp.text)
        return Converters.create_repository_provider_response(json_result)

    def get_repository_providers(
            self,
    ) -> List[RepositoryProviderResponse]:
        method_url = self._api_root.settings.repository_providers()

        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        json_result = json.loads(resp.text)
        return [Converters.create_repository_provider_response(provider) for provider in json_result]

    def delete_repository_provider(
            self,
            provider_name: str
    ):
        method_url = self._api_root.settings.repository_provider(provider_name)

        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def add_repository_to_account(
            self,
            repository_details: BlueprintRepositoryDetails,
            repository_provider_id: str,
            repository_name: str,
            repo_relationship: dict = None

    ):
        method_url = self._api_root.settings.repositories()

        request = {
            "provider_id": repository_provider_id,
            "name": repository_name,
            "allow_sharing": True,
            "open_access": True,
            "repository_url": repository_details.repository_url,
            "connection_details": {
                "token": repository_details.access_token
            },
        }

        if repo_relationship:
            repository_relationships = [{
                "deployment_type": repo_relationship['deployment_type'],
                "account_repository_name": repo_relationship['repository_name'],
                "branch": repo_relationship['branch'],
                "space_name": repo_relationship['space_name'],
            }]

            request["repository_relationships"]: List[dict] = repository_relationships

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def list_account_repositories(self) -> List[AccountRepositoryResponse]:
        url = self._api_root.settings.repositories()
        response = self.session.get(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        return [Converters.create_account_repository_response(x) for x in json_result]

    def delete_account_repository(self, name: str):
        url = self._api_root.settings.repository(name)
        response = self.session.delete(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def add_repository_relationship_to_space(
            self,
            deployment_type: str,
            account_repository_name: str,
            space: str):

        self.__add_repository_relationship(deployment_type, account_repository_name, space, None)

    def add_repository_relationship(
            self,
            deployment_type: str,
            account_repository_name: str,
            branch: str = None):

        self.__add_repository_relationship(deployment_type, account_repository_name, self.space, branch)

    def __add_repository_relationship(
            self,
            deployment_type: str,
            account_repository_name: str,
            space: str,
            branch: str):

        method_url = self._api_root.spaces.add_repository_relationship(space)

        request = {
            "deployment_type": deployment_type,
            "account_repository_name": account_repository_name,
            "branch": branch
        }

        resp = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_repository_relationship(
            self,
            deployment_type: str
    ) -> RepositoryRelationshipResponse:
        method_url = self._api_root.spaces.repository_relationship(self.space, deployment_type)

        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        json_result = json.loads(resp.text)
        return Converters.create_repository_relationship_response(json_result)

    def delete_repository_relationship(
            self,
            deployment_type: str,
    ):
        self.delete_repository_relationship_from_space(deployment_type, self.space)

    def delete_repository_relationship_from_space(
            self,
            deployment_type: str,
            space: str
    ):
        method_url = self._api_root.spaces.repository_relationship(space, deployment_type)

        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def submit_new_user_survey(self, survey: NewUserSurveyRequest) -> Response:
        method_url = self._api_root.account.submit_new_user_survey()
        resp = self.session.post(url=method_url, json=survey.__dict__)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

        return resp

    def add_terraform_modules_descriptor_to_account(self, request: TerraformModuleDescriptor):
        method_url = self._api_root.settings.terraform_modules()
        resp = self.session.post(url=method_url,  json=Utils.get_as_json(request))
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text.replace('"', '')

    def update_terraform_modules_descriptor_to_account(self, request: TerraformModuleDescriptor, module_name: str):
        method_url = self._api_root.settings.terraform_module(module_name)
        resp = self.session.put(url=method_url,  json=Utils.get_as_json(request))
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        return resp.text.replace('"', '')

    def get_terraform_modules_descriptors(self) -> List[TerraformModuleDescriptorResponse]:
        method_url = self._api_root.settings.terraform_modules()
        resp = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])
        json_result = json.loads(resp.text)
        return [Converters.create_terraform_module_descriptor_response(terraform_module)
                for terraform_module in json_result]

    def delete_terraform_modules_descriptor(
            self,
            descriptor_name: str
    ):
        method_url = self._api_root.settings.terraform_module(descriptor_name)

        resp = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=resp, return_codes=[200])

    def get_terraform_modules_available_for_space(self):
        method_url = self._api_root.spaces.available_space_terraform_modules(space_name=self.space)

        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        return [Converters.create_terraform_module_descriptor_response(terraform_module)
                for terraform_module in json_result]

    def get_space_terraform_modules(self) -> List[SpaceTerraformModuleResponse]:
        method_url = self._api_root.spaces.attached_space_terraform_modules(space_name=self.space)

        response = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        json_result = json.loads(response.text)
        return [Converters.create_space_terraform_module_response(item)
                for item in json_result]

    def add_space_terraform_module(self, request: AddSpaceTerraformModuleRequest):
        method_url = self._api_root.spaces.attached_space_terraform_modules(space_name=self.space)

        response = self.session.post(url=method_url, json=Utils.get_as_json(request))
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def update_space_terraform_module(self, module_alias: str, request: UpdateSpaceTerraformModuleRequest):
        method_url = self._api_root.spaces.attached_space_terraform_module(space_name=self.space,
                                                                           module_alias=module_alias)

        response = self.session.put(url=method_url, json=Utils.get_as_json(request))
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def delete_space_terraform_module(self, module_alias: str):
        method_url = self._api_root.spaces.attached_space_terraform_module(space_name=self.space,
                                                                           module_alias=module_alias)
        response = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_terraform_versions(self) -> List[str]:
        method_url = self._api_root.settings.terraform_versions()
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        return json.loads(res.text)

    def get_custom_tags(self) -> List[CustomTagWithStatisticsResponse]:
        method_url = self._api_root.settings.custom_tags()
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        custom_tags_json = json.loads(res.text)
        return [Converters.create_custom_tag_with_statistics_response(custom_tag) for custom_tag in custom_tags_json]

    def create_custom_tag(self, name: str, value: str, scope: str, possible_values: [], description: str):
        method_url = self._api_root.settings.custom_tags()
        request = {
            "name": name,
            "value": value,
            "scope": scope,
            "possible_values": possible_values,
            "description": description
        }
        res = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_custom_tag(self, old_name: str, name: str, value: str, scope: str, possible_values: [],
                          description: str, force_remove_possible_values: bool = False):
        method_url = self._api_root.settings.custom_tag(old_name)
        request = {
            "name": name,
            "value": value,
            "scope": scope,
            "possible_values": possible_values,
            "description": description,
            "force_remove_possible_values": force_remove_possible_values
        }
        res = self.session.put(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def delete_custom_tag(self, name: str):
        method_url = self._api_root.settings.custom_tag(name)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_space_custom_tags(self, space_name: str) -> List[CustomTagOverrideResponse]:
        method_url = self._api_root.spaces.custom_space_tags(space_name)
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        custom_tags_json = json.loads(res.text)
        return [Converters.create_custom_tag_override_response(custom_tag) for custom_tag in custom_tags_json]

    def create_space_custom_tag(self, space_name: str, name: str, value: str):
        method_url = self._api_root.spaces.custom_space_tags(space_name)
        request = {
            "name": name,
            "value": value
        }
        res = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_space_custom_tag(self, space_name: str, name: str, value: str):
        method_url = self._api_root.spaces.custom_space_tag(space_name, name)
        request = {
            "value": value
        }
        res = self.session.put(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def delete_space_custom_tag(self, space_name: str, name: str):
        method_url = self._api_root.spaces.custom_space_tag(space_name, name)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def get_blueprint_custom_tags(self, space_name: str,
                                  blueprint_name: str, deployment_type: str) -> List[CustomTagOverrideResponse]:
        method_url = self._api_root.spaces.custom_blueprint_tags(space_name, blueprint_name, deployment_type)
        res = self.session.get(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])
        custom_tags_json = json.loads(res.text)
        return [Converters.create_custom_tag_override_response(custom_tag) for custom_tag in custom_tags_json]

    def create_blueprint_custom_tag(self, space_name: str,
                                    blueprint_name: str, deployment_type: str, name: str, value: str):
        method_url = self._api_root.spaces.custom_blueprint_tags(space_name, blueprint_name, deployment_type)
        request = {
            "name": name,
            "value": value
        }
        res = self.session.post(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def update_blueprint_custom_tag(self, space_name: str,
                                    blueprint_name: str, deployment_type: str, name: str, value: str):
        method_url = self._api_root.spaces.custom_blueprint_tag(space_name, blueprint_name, name, deployment_type)
        request = {
            "value": value
        }
        res = self.session.put(url=method_url, json=request)
        GatewayUtils.handle_response(response=res, return_codes=[200])

    def delete_blueprint_custom_tag(self, space_name: str, blueprint_name: str, deployment_type: str, name: str):
        method_url = self._api_root.spaces.custom_blueprint_tag(space_name, blueprint_name, name, deployment_type)
        res = self.session.delete(url=method_url)
        GatewayUtils.handle_response(response=res, return_codes=[200])


class SandboxesHandler:
    def __init__(self):
        self.sandboxes_set = set()

    def add_sandbox(self, sandbox_id):
        self.sandboxes_set.add(sandbox_id)
        print("Sandbox {id} added to cleaner".format(id=sandbox_id))

    def remove_sandbox(self, sandbox_id):
        self.sandboxes_set.remove(sandbox_id)
        print("Sandbox {id} removed from cleaner".format(id=sandbox_id))


class SandboxCleaner:
    def __init__(self, client: Colony, end_on_exception=True):
        self.end_on_exception = end_on_exception
        self.client = client
        self.sandboxes = SandboxesHandler()
        self.space = self.client.space

    def __enter__(self):
        return self.sandboxes

    def __exit__(self, exc_type, exc_val: str, exc_tb):
        for sandbox in self.sandboxes.sandboxes_set:
            # if exc_type is MaxRetriesException:
            #     print(f"Sandbox {sandbox} failed on timeout")
            if exc_type is SandboxNotFound:
                print(f"Sandbox {sandbox} failed on not found")
            elif exc_type is SandboxEndingFailed:
                print(f"Sandbox {sandbox} failed to end")
            else:
                if self.end_on_exception:
                    print("Sandbox {} is being removed by cleaner".format(sandbox))
                    self.client.end_sandbox(sandbox_id=sandbox)


class ProductionCleaner:
    def __init__(self, client: Colony):
        self.client = client
        self.ids = []
        self.space = self.client.space

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for production_id in self.ids:
            print("Production {} is being removed by cleaner".format(production_id))

            self.client.end_production(production_id=production_id)

    def add(self, production_id):
        self.ids.append(production_id)
        print("Production {id} added to cleaner".format(id=production_id))

    def remove(self, production_id):
        self.ids.remove(production_id)
        print("Production {id} removed from cleaner".format(id=production_id))
