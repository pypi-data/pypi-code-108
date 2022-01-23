# pylint: disable=too-many-instance-attributes
"""
Container for Response objects used in cs18-api-client
"""
import abc

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

from gateways.common.cs18_api_classes import AccessLink, TerraformModuleDescriptor, \
    TerraformModuleInput, TerraformModuleComputeService, TerraformModuleOutput, SpaceTerraformModuleInput
from gateways.common.cs18_api_errors import SandboxError, Error


class BlueprintSourceResponse:
    def __init__(self, branch: str, commit: str):
        self.commit = commit
        self.branch = branch


class BlueprintTagResponse:
    def __init__(self, name: str, default_value: str, possible_values: [], description: str):
        self.name = name
        self.default_value = default_value
        self.possible_values = possible_values
        self.description = description


class AccountStatusUserDetails:
    def __init__(self, user_details: {}):
        self.last_name = user_details["last_name"]
        self.first_name = user_details["first_name"]
        self.email = user_details["email"]
        self.permitted_spaces = user_details["permitted_spaces"]
        self.account_permissions = user_details["account_permissions"]
        self.survey_done = user_details["survey_done"]


class AccountOnboardingLimitsResponse:
    def __init__(self, limits: {}):
        self.users = limits["users"]
        self.users_delta = limits["users_delta"]
        self.spaces = limits["spaces"]
        self.environments = limits["environments"]
        self.environments_delta = limits["environments_delta"]
        self.tags = limits["tags"]


class AccountStatusResponse:
    def __init__(
            self,
            limits: AccountOnboardingLimitsResponse,
            onboarding_status: str,
            license_expiration_date: datetime,
            ignore_expiration_date: bool,
            suspended_reason: str,
            salesforce_account_id: str,
            plan_id: str,
            user_details: AccountStatusUserDetails,
    ):
        self.limits = limits
        self.user_details = user_details  # type: AccountStatusUserDetails
        self.salesforce_account_id = salesforce_account_id
        self.suspended_reason = suspended_reason
        self.license_expiration_date = license_expiration_date
        self.ignore_expiration_date = ignore_expiration_date
        self.plan_id = plan_id
        self.onboarding_status = onboarding_status


class AccountExtraDetails:
    def __init__(
            self,
            account_id: str,
            name: str,
            sso_enabled: bool,
            anonymous_users: bool,
            sso_update_enabled: bool,
            company_name: str
    ):
        self.account_id = account_id
        self.name = name
        self.sso_enabled = sso_enabled
        self.anonymous_users = anonymous_users
        self.sso_update_enabled = sso_update_enabled
        self.company_name = company_name


class TokenResponse:
    def __init__(
            self, access_token: str, refresh_token: str, token_type: str, expires_in: int
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in


class HyperlinkResponse:
    def __init__(self, rel: str, href: str, method: str):
        self.rel = rel
        self.href = href
        self.method = method


class CatalogApplicationResponse:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version


class CatalogForGetResponse:
    def __init__(
            self,
            name: str,
            description: str,
            url: str,
            last_modified: str,
            modified_by: str,
            clouds: List[str],
            applications: List[CatalogApplicationResponse],
            links: List[HyperlinkResponse],
            artifacts: Dict[str, str],
            errors: [],
            tags: List[BlueprintTagResponse],
    ):
        self.errors = errors
        self.links = links
        self.url = url
        self.description = description
        self.name = name
        self.last_modified = last_modified
        self.modified_by = modified_by
        self.clouds = clouds
        self.applications = applications
        self.artifacts = artifacts
        self.tags = tags


class CatalogForGetAllResponse:
    def __init__(
            self,
            name: str,
            description: str,
            url: str,
            last_modified: str,
            modified_by: str,
            clouds: List[str],
            links: List[HyperlinkResponse],
            artifacts: Dict[str, str],
            errors: [],
            tags: List[BlueprintTagResponse],
    ):
        self.links = links
        self.url = url
        self.description = description
        self.name = name
        self.last_modified = last_modified
        self.modified_by = modified_by
        self.clouds = clouds
        self.artifacts = artifacts
        self.errors = errors
        self.tags = tags


class BlueprintApplicationResponse:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version


class BlueprintServiceResponse:
    def __init__(self, name: str, service_type: str):
        self.name = name
        self.type = service_type


class BlueprintInputResponse:
    def __init__(
            self, name: str, default_value: str, display_style: str, description: str, optional: bool,
            possible_values: []
    ):
        self.name = name
        self.default_value = default_value
        self.display_style = display_style
        self.optional = optional
        self.description = description
        self.possible_values = possible_values


class BlueprintRegionResponse:
    def __init__(self, region_id: str, name: str):
        self.name = name
        self.region_id = region_id


class BlueprintComputeServiceResponse:
    def __init__(self, name: str, service_type: str, created_date: datetime, created_by: str, user_defined: bool):
        self.name = name
        self.type = service_type
        self.created_date = created_date
        self.created_by = created_by
        self.user_defined = user_defined


class BlueprintCloudResponse:
    def __init__(
            self, provider: str, cloud_account_name: str, region: BlueprintRegionResponse,
            compute_service: BlueprintComputeServiceResponse
    ):
        self.provider = provider
        self.cloud_account_name = cloud_account_name
        self.region = region
        self.compute_service = compute_service


class ArtifactRepoCreatedUser:
    def __init__(self, email: str, first_name: str, last_name: str):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email


class ArtifactRepoResponse:
    def __init__(
            self,
            repo_type: str,
            created_date: datetime,
            location: str,
            created_by: ArtifactRepoCreatedUser,
    ):
        self.created_by = created_by
        self.location = location
        self.created_date = created_date
        self.type = repo_type


class BlueprintResponse:
    def __init__(
            self,
            name: str,
            description: str,
            url: str,
            enabled: bool,
            last_modified: str,
            modified_by: str,
            clouds: List[BlueprintCloudResponse],
            applications: List[BlueprintApplicationResponse],
            links: List[HyperlinkResponse],
            artifacts: Dict[str, str],
            inputs: List[BlueprintInputResponse],
            errors: List[Error],
            is_sample,
            services: List[BlueprintServiceResponse],
            environment_type: str,
            tags: List[BlueprintTagResponse]
    ):
        self.errors = errors
        self.is_sample = is_sample
        self.links = links
        self.enabled = enabled
        self.url = url
        self.description = description
        self.name = name
        self.last_modified = last_modified
        self.modified_by = modified_by
        self.clouds = clouds
        self.applications = applications
        self.artifacts = artifacts
        self.inputs = inputs
        self.services = services
        self.environment_type = environment_type
        self.tags = tags


class SourceControlDetailsResponse:
    def __init__(
            self,
            branch_name: str,
            latest_commit_id: str,
            changed_by: str,
            changed_date: datetime,
    ):
        self.branch_name = branch_name
        self.latest_commit_id = latest_commit_id
        self.changed_by = changed_by
        self.changed_date = changed_date


class BlueprintFileResponse:
    def __init__(
            self,
            url: str,
            kind: str,
            content: str,
            source_control_details: SourceControlDetailsResponse,
            icon: str,
    ):
        self.url = url
        self.kind = kind
        self.content = content
        self.source_control_details = source_control_details
        self.icon = icon


class CreateSandboxResponse:
    def __init__(self, sandbox_id: str):
        self.sandbox_id = sandbox_id


class CreateProductionResponse:
    def __init__(self, production_id: str):
        self.production_id = production_id


class AppInstanceResponse:
    def __init__(
            self,
            private_ip: str,
            infra_id: str,
            deployment_status: str,
            access_links: List[AccessLink],
            links: List[HyperlinkResponse],
            instance_type: str = None,
            memory_limit: str = None,
            cpu_limit: str = None,
    ):
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.instance_type = instance_type
        self.links = links
        self.access_links = access_links
        self.private_ip = private_ip
        self.deployment_status = deployment_status
        self.infra_id = infra_id


class CloudRegionResponse:
    def __init__(self, region_id: str, region_name: str):
        self.region_id = region_id
        self.name = region_name


class CloudComputeServiceResponse:
    def __init__(self, name: str, service_type: str, created_date: datetime, created_by: str, user_defined: bool):
        self.name = name
        self.type = service_type
        self.created_date = created_date
        self.created_by = created_by
        self.user_defined = user_defined


class CloudResponse:
    def __init__(
            self,
            provider: str,
            cloud_account_name: str,
            region: CloudRegionResponse,
            compute_service: CloudComputeServiceResponse
    ):
        self.provider = provider
        self.cloud_account_name = cloud_account_name
        self.region = region
        self.compute_service = compute_service


class ApplicationResponseBase:
    def __init__(self, name: str, status: str, cloud: CloudResponse):
        self.name = name
        self.status = status
        self.cloud = cloud


class ApplicationResponseLean(ApplicationResponseBase):
    def __init__(self, name: str, status: str, cloud: CloudResponse):
        super().__init__(name=name, status=status, cloud=cloud)


class ApplicationResponse(ApplicationResponseBase):
    def __init__(
            self,
            name: str,
            shortcuts: List[str],
            status: str,
            instances: List[AppInstanceResponse],
            private_address: str,
            public_address: str,
            internal_ports: str,
            external_ports: str,
            internal_dns: str,
            image_name: str,
            icon: str,
            cloud: CloudResponse = None,
            direct_access_protocols: List[str] = None
    ):
        super().__init__(name=name, status=status, cloud=cloud)
        self.image_name = image_name
        self.internal_dns = internal_dns
        self.external_ports = external_ports
        self.internal_ports = internal_ports
        self.public_address = public_address
        self.private_address = private_address
        self.shortcuts = shortcuts
        self.instances = instances
        self.icon = icon
        self.direct_access_protocols = direct_access_protocols if direct_access_protocols else []


class SandboxOwnerResponse:
    def __init__(self, first_name: str, last_name: str, email: str, join_date: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.join_date = join_date


class LaunchingProgressStep:
    def __init__(self, total: int, succeeded: int, failed: int, status: str):
        self.failed = failed
        self.succeeded = succeeded
        self.total = total
        self.status = status


class LaunchingProgress:
    def __init__(self,
                 creating_infrastructure: LaunchingProgressStep,
                 preparing_artifacts: LaunchingProgressStep,
                 deploying_applications: LaunchingProgressStep,
                 verifying_environment: LaunchingProgressStep):
        self.verifying_environment = verifying_environment
        self.deploying_applications = deploying_applications
        self.preparing_artifacts = preparing_artifacts
        self.creating_infrastructure = creating_infrastructure


class SandboxResponseBase:
    def __init__(self,
                 sandbox_status: str,
                 create_time: str,
                 start_time: str,
                 status_details: str,
                 status_error_description: str,
                 links: List[HyperlinkResponse],
                 blueprint: str,
                 automation: bool,
                 owner: SandboxOwnerResponse,
                 sandbox_id: str,
                 errors: List[SandboxError],
                 scheduled_end_time: datetime,
                 end_time: datetime,
                 debugging_service: str,
                 source: BlueprintSourceResponse,
                 direct_access: str):
        self.source = source
        self.sandbox_status = sandbox_status
        self.create_time = create_time
        self.start_time = start_time
        self.status_details = status_details
        self.status_error_description = status_error_description
        self.links = links
        self.sandbox_id = sandbox_id
        self.blueprint = blueprint
        self.automation = automation
        self.owner = owner
        self.errors = errors
        self.scheduled_end_time = scheduled_end_time
        self.end_time = end_time
        self.debugging_service = debugging_service
        self.direct_access = direct_access


class InputResponse:
    def __init__(self, name: str, value: str, display_style: str, description: str, optional: bool):
        self.description = description
        self.display_style = display_style
        self.optional = optional
        self.value = value
        self.name = name


class SandboxOutput:
    def __init__(self,
                 name: str,
                 value: str,
                 display_style: str,
                 description: str):
        self.name = name
        self.value = value
        self.display_style = display_style
        self.description = description


class ServiceTfProgressResponse:
    def __init__(self,
                 tf_tagging_status: str,
                 tf_init_status: str,
                 tf_plan_status: str,
                 tf_apply_status: str,
                 tf_destroy_status: str):
        self.tf_tagging_status = tf_tagging_status
        self.tf_init_status = tf_init_status
        self.tf_plan_status = tf_plan_status
        self.tf_apply_status = tf_apply_status
        self.tf_destroy_status = tf_destroy_status


class ServiceTfLogInfo:
    def __init__(self,
                 location: str,
                 start_time: str,
                 duration: str):
        self.location = location
        self.start_time = start_time
        self.duration = duration


class ServiceTfLogsResponse:
    def __init__(self,
                 tf_tagging: ServiceTfLogInfo = None,
                 tf_init: ServiceTfLogInfo = None,
                 tf_plan: ServiceTfLogInfo = None,
                 tf_apply: ServiceTfLogInfo = None,
                 tf_destroy: ServiceTfLogInfo = None):
        self.tf_tagging = tf_tagging
        self.tf_init = tf_init
        self.tf_plan = tf_plan
        self.tf_apply = tf_apply
        self.tf_destroy = tf_destroy


class ServiceResponse:
    def __init__(self,
                 name: str,
                 service_type: str,
                 status: str,
                 progress: ServiceTfProgressResponse,
                 logs: ServiceTfLogsResponse = None):
        self.name = name
        self.type = service_type
        self.status = status
        self.progress = progress
        self.logs = logs


class CustomTagResponse:
    def __init__(self,
                 name: str,
                 value: str,
                 scope: str,
                 possible_values: [],
                 description: str,
                 modified_by: str,
                 last_modified: datetime,
                 created_by: str,
                 created_date: datetime):
        self.name = name
        self.value = value
        self.scope = scope
        self.possible_values = possible_values
        self.description = description
        self.modified_by = modified_by
        self.last_modified = last_modified
        self.created_date = created_date
        self.created_by = created_by


class CustomTagWithStatisticsResponse(CustomTagResponse):
    def __init__(self,
                 name: str,
                 value: str,
                 scope: str,
                 possible_values: [],
                 description: str,
                 modified_by: str,
                 last_modified: datetime,
                 created_by: str,
                 created_date: datetime,
                 overridden_values: int,
                 missing_overrides: int,
                 missing_overrides_space: List[str],
                 missing_overrides_sandbox_blueprints: List[str],
                 missing_overrides_production_blueprints: List[str]):
        super().__init__(name,
                         value,
                         scope,
                         possible_values,
                         description,
                         modified_by,
                         last_modified,
                         created_by,
                         created_date)
        self.overridden_values = overridden_values
        self.missing_overrides = missing_overrides
        self.missing_overrides_space = missing_overrides_space
        self.missing_overrides_sandbox_blueprints = missing_overrides_sandbox_blueprints
        self.missing_overrides_production_blueprints = missing_overrides_production_blueprints


class SandboxResponse(SandboxResponseBase):
    def __init__(self,
                 sandbox_id: str,
                 blueprint: str,
                 automation: bool,
                 applications: List[ApplicationResponse],
                 services: List[ServiceResponse],
                 inputs: List[InputResponse],
                 artifacts: Dict[str, str],
                 start_time: str,
                 create_time: str,
                 status_details: str,
                 links: List[HyperlinkResponse],
                 sandbox_status: str,
                 status_error_description: str,
                 owner: SandboxOwnerResponse,
                 errors: List[SandboxError],
                 scheduled_end_time: datetime,
                 end_time: datetime,
                 debugging_service: str,
                 launching_progress: LaunchingProgress,
                 source: BlueprintSourceResponse,
                 direct_access: str,
                 outputs: Optional[List[SandboxOutput]],
                 tags: List[CustomTagResponse]):
        super().__init__(sandbox_status,
                         create_time,
                         start_time,
                         status_details,
                         status_error_description,
                         links,
                         blueprint,
                         automation,
                         owner,
                         sandbox_id,
                         errors,
                         scheduled_end_time,
                         end_time,
                         debugging_service,
                         source,
                         direct_access)
        self.artifacts = artifacts
        self.inputs = inputs
        self.applications = applications
        self.services = services
        self.launching_progress = launching_progress
        self.outputs = outputs
        self.tags = tags


class SandboxResponseLean(SandboxResponseBase):
    def __init__(self,
                 sandbox_id: str,
                 blueprint: str,
                 automation: bool,
                 applications: List[ApplicationResponseLean],
                 services: List[ServiceResponse],
                 start_time: str,
                 create_time: str,
                 status_details: str,
                 status_error_description: str,
                 links: List[HyperlinkResponse],
                 sandbox_status: str,
                 owner: SandboxOwnerResponse,
                 name: str,
                 errors: List[SandboxError],
                 scheduled_end_time: datetime,
                 end_time: datetime,
                 debugging_service: str,
                 source: BlueprintSourceResponse,
                 direct_access: str):
        super().__init__(sandbox_status,
                         create_time,
                         start_time,
                         status_details,
                         status_error_description,
                         links,
                         blueprint,
                         automation,
                         owner,
                         sandbox_id,
                         errors,
                         scheduled_end_time,
                         end_time,
                         debugging_service,
                         source,
                         direct_access)
        self.end_time = end_time
        self.applications = applications
        self.name = name
        self.services = services


class ProductionResponseLean:
    def __init__(
            self,
            production_id: str,
            name: str,
            blueprint_description: str,
            blue_status: str,
            green_status: str,
            update_strategy: str,
            update_status: str,
            create_time: datetime,
            deployment_start_time: datetime,
            blue_applications: List[ApplicationResponseLean],
            blue_services: List[ServiceResponse],
            direct_access: str):
        self.production_id = production_id
        self.name = name
        self.blueprint_description = blueprint_description
        self.blue_status = blue_status
        self.green_status = green_status
        self.update_strategy = update_strategy
        self.update_status = update_status
        self.create_time = create_time
        self.deployment_start_time = deployment_start_time
        self.blue_applications = blue_applications
        self.blue_services = blue_services
        self.direct_access = direct_access


class ProductionResponse(metaclass=abc.ABCMeta):
    def __init__(
            self,
            production_id: str,
            sandbox_id: str,
            name: str,
            owner: SandboxOwnerResponse,
            blueprint_name: str,
            blueprint_description: str,
            applications: List[ApplicationResponse],
            services: List[ServiceResponse],
            artifacts: Dict[str, str],
            inputs: List[InputResponse],
            create_time: datetime,
            deployment_start_time: datetime,
            build: str,
            production_status: str,
            update_status: str,
            status_details: str,
            status_error_description: str,
            errors: List[SandboxError],
            links: List[HyperlinkResponse],
            debugging_service: str,
            launching_progress: LaunchingProgress,
            direct_access: str,
            outputs: Optional[List[SandboxOutput]],
            tags: List[CustomTagResponse]):
        self.production_id = production_id
        self.sandbox_id = sandbox_id
        self.name = name
        self.owner = owner
        self.blueprint_name = blueprint_name
        self.blueprint_description = blueprint_description
        self.applications = applications
        self.artifacts = artifacts
        self.inputs = inputs
        self.create_time = create_time
        self.deployment_start_time = deployment_start_time
        self.build = build
        self.production_status = production_status
        self.update_status = update_status
        self.status_details = status_details
        self.status_error_description = status_error_description
        self.errors = errors
        self.links = links
        self.services = services
        self.debugging_service = debugging_service
        self.launching_progress = launching_progress
        self.direct_access = direct_access
        self.outputs = outputs
        self.tags = tags


class ProductionBlueResponse(ProductionResponse):
    def __init__(self,
                 production_id: str,
                 sandbox_id: str,
                 name: str,
                 owner: SandboxOwnerResponse,
                 blueprint_name: str,
                 blueprint_description: str,
                 applications: List[ApplicationResponse],
                 services: List[ServiceResponse],
                 artifacts: Dict[str, str],
                 inputs: List[InputResponse],
                 create_time: datetime,
                 deployment_start_time: datetime,
                 build: str,
                 production_status: str,
                 update_status: str,
                 status_details: str,
                 status_error_description: str,
                 errors: List[SandboxError],
                 links: List[HyperlinkResponse],
                 has_green: bool,
                 debugging_service: str,
                 launching_progress: LaunchingProgress,
                 direct_access: str,
                 outputs: Optional[List[SandboxOutput]],
                 tags: List[CustomTagResponse]):
        super().__init__(
            production_id=production_id,
            sandbox_id=sandbox_id,
            name=name,
            owner=owner,
            blueprint_name=blueprint_name,
            blueprint_description=blueprint_description,
            applications=applications,
            services=services,
            artifacts=artifacts,
            inputs=inputs,
            create_time=create_time,
            deployment_start_time=deployment_start_time,
            build=build,
            production_status=production_status,
            update_status=update_status,
            status_details=status_details,
            status_error_description=status_error_description,
            errors=errors,
            links=links,
            debugging_service=debugging_service,
            launching_progress=launching_progress,
            direct_access=direct_access,
            outputs=outputs,
            tags=tags)
        self.has_green = has_green


class ProductionGreenResponse(ProductionResponse):
    def __init__(self,
                 production_id: str,
                 sandbox_id: str,
                 name: str,
                 owner: SandboxOwnerResponse,
                 blueprint_name: str,
                 blueprint_description: str,
                 applications: List[ApplicationResponse],
                 services: List[ServiceResponse],
                 artifacts: Dict[str, str],
                 inputs: List[InputResponse],
                 create_time: datetime,
                 deployment_start_time: datetime,
                 build: str,
                 production_status: str,
                 update_status: str,
                 status_details: str,
                 status_error_description: str,
                 errors: List[SandboxError],
                 links: List[HyperlinkResponse],
                 exposure: int,
                 debugging_service: str,
                 launching_progress: LaunchingProgress,
                 direct_access: str,
                 outputs: Optional[List[SandboxOutput]],
                 tags: List[CustomTagResponse]):
        super().__init__(
            production_id=production_id,
            sandbox_id=sandbox_id,
            name=name,
            owner=owner,
            blueprint_name=blueprint_name,
            blueprint_description=blueprint_description,
            applications=applications,
            services=services,
            artifacts=artifacts,
            inputs=inputs,
            create_time=create_time,
            deployment_start_time=deployment_start_time,
            build=build,
            production_status=production_status,
            update_status=update_status,
            status_details=status_details,
            status_error_description=status_error_description,
            errors=errors,
            links=links,
            debugging_service=debugging_service,
            launching_progress=launching_progress,
            direct_access=direct_access,
            outputs=outputs,
            tags=tags)
        self.exposure = exposure


class UserPermittedToSpaceResponse:
    def __init__(
            self,
            first_name: str,
            last_name: str,
            email: str,
            join_date: str,
            space_role: str,
            account_role: str,
            has_access_to_all_spaces: bool):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.join_date = join_date
        self.space_role = space_role
        self.account_role = account_role
        self.has_access_to_all_spaces = has_access_to_all_spaces


class CloudAccountCostResponse:
    def __init__(self, last_update: Optional[datetime]):
        self.last_update = last_update


class ComputeServiceBaseResponse:
    def __init__(self,
                 name: str,
                 service_type: str,
                 created_date: datetime,
                 created_by: str,
                 user_defined: bool,
                 status: str):
        self.created_by = created_by
        self.type = service_type
        self.created_date = created_date
        self.name = name
        self.user_defined = user_defined
        self.status = status


class ComputeServiceInAccountResponse(ComputeServiceBaseResponse):
    def __init__(self,
                 name: str,
                 service_type: str,
                 created_date: datetime,
                 created_by: str,
                 user_defined: bool,
                 status: str,
                 spaces: List[str]):
        super().__init__(name, service_type, created_date, created_by, user_defined, status)
        self.spaces = spaces


class CloudAccountResponse:
    def __init__(
            self,
            name: str,
            provider: str,
            created_date: datetime,
            created_by: str,
            spaces: List[str],
            compute_services: List[ComputeServiceInAccountResponse] = None,
            cost: CloudAccountCostResponse = None,
            errors: List[Error] = None
    ):
        self.name = name
        self.provider = provider
        self.created_date = created_date
        self.created_by = created_by
        self.spaces = spaces
        self.compute_services = compute_services
        self.cost = cost
        self.errors = errors


class CloudAccountSubnetsResponse:
    def __init__(self, gateway_subnet: str,
                 management_subnet: str,
                 application_subnets: List[str]):
        self.gateway_subnet = gateway_subnet
        self.management_subnet = management_subnet
        self.application_subnets = application_subnets


class CloudAccountInfraSetResponse:
    def __init__(self,
                 region: str,
                 virtual_network: str,
                 subnets: CloudAccountSubnetsResponse):
        self.region = region
        self.virtual_network = virtual_network
        self.subnets = subnets


class CloudAccountConnectivityResponse:
    def __init__(self,
                 existing_infra: bool,
                 existing_infra_sets: List[CloudAccountInfraSetResponse]):
        self.existing_infra = existing_infra
        self.existing_infra_sets = existing_infra_sets


class K8SComputeServiceSpaceInfraSettingsResponse:
    def __init__(self, namespace: str, internet_facing: bool):
        self.namespace = namespace
        self.internet_facing = internet_facing


class ComputeServiceSpaceSpecResponse:
    def __init__(self, kubernetes: Optional[K8SComputeServiceSpaceInfraSettingsResponse]):
        self.kubernetes = kubernetes


class ComputeServiceInSpaceResponse(ComputeServiceBaseResponse):
    def __init__(
            self,
            name: str,
            service_type: str,
            created_date: datetime,
            created_by: str,
            user_defined: bool,
            status: str,
            spec: Optional[ComputeServiceSpaceSpecResponse]
    ):
        super().__init__(name, service_type, created_date, created_by, user_defined, status)
        self.spec = spec


class CloudAccountInSpaceResponse:
    def __init__(
            self,
            name: str,
            provider: str,
            created_date: datetime,
            created_by: str,
            internet_facing: bool,
            connectivity: CloudAccountConnectivityResponse,
            compute_services: List[ComputeServiceInSpaceResponse] = None,
            cost: CloudAccountCostResponse = None,
            errors: List[Error] = None,
    ):
        self.name = name
        self.provider = provider
        self.created_date = created_date
        self.created_by = created_by
        self.compute_services = compute_services
        self.cost = cost
        self.errors = errors
        self.internet_facing = internet_facing
        self.connectivity = connectivity


class UserInvitationResponse:
    def __init__(
            self,
            email: str,
            send_date: str,
            account_role: str,
            space_name: str,
            space_role: str,
    ):
        self.email = email
        self.send_date = send_date
        self.account_role = account_role
        self.space_name = space_name
        self.space_role = space_role


class InvitedUserDetailsResponse:
    def __init__(
            self,
            email: str,
            account_name: str,
    ):
        self.email = email
        self.account_name = account_name


class RepositoryResponse:
    def __init__(self, repository_url: str, errors: List[Error], branch: str):
        self.errors = errors
        self.repository_url = repository_url
        self.branch = branch


class AccountRepositoryResponse:
    def __init__(self, repository_id: str, name: str, provider_name: str, allow_sharing: str,
                 open_access: str, account_id: str, is_valid: bool, connection_details, repository_url: str,
                 errors: List[Error], repository_relationships):
        self.repository_url = repository_url
        self.repository_id = repository_id
        self.name = name
        self.provider_name = provider_name
        self.allow_sharing = allow_sharing
        self.open_access = open_access
        self.account_id = account_id
        self.is_valid = is_valid
        self.errors = errors
        self.connection_details = connection_details
        self.repository_relationships = repository_relationships


class AccountRepositoryItemResponse:
    def __init__(self, repository_id: str, name: str, allow_sharing: str,
                 open_access: str, is_valid: bool, repository_url: str,
                 errors: List[Error], repository_relationships):
        self.repository_url = repository_url
        self.repository_id = repository_id
        self.name = name
        self.allow_sharing = allow_sharing
        self.open_access = open_access
        self.is_valid = is_valid
        self.errors = errors
        self.repository_relationships = repository_relationships


class RepositoryProviderResponse:
    def __init__(self, provider_id: str, name: str, details, status: str, account_id: str,
                 repositories: List[AccountRepositoryItemResponse], errors: List[Error]):
        self.provider_id = provider_id
        self.errors = errors
        self.account_id = account_id
        self.name = name
        self.type = type
        self.details = details
        self.status = status
        self.repositories = repositories


class RepositoryRelationshipResponse:
    def __init__(self, repo_relationship_id: str, space_id: str, deployment_type: str,
                 branch: str, is_valid: bool, errors: List[Error]):
        self.repo_relationship_id = repo_relationship_id
        self.space_id = space_id
        self.deployment_type = deployment_type
        self.branch = branch
        self.is_valid: bool = is_valid
        self.errors = errors


class SpaceAdmin:
    def __init__(self, first_name: str, last_name: str, account_role: str):
        self.last_name = last_name
        self.first_name = first_name
        self.account_role = account_role


class SpaceCloudAccount:
    def __init__(self, name: str, cloud_account_type: str):
        self.type = cloud_account_type
        self.name = name


class GetSpaceResponse:
    def __init__(self, space: {}):
        self.name = space["name"]


class GetSpacesResponse:
    def __init__(
            self,
            name: str,
            admins: List[SpaceAdmin],
            users_count: int,
            cloud_accounts: List[SpaceCloudAccount],
    ):
        self.users_count = users_count
        self.cloud_accounts = cloud_accounts
        self.admins = admins
        self.name = name


class RoleListItemResponse:
    def __init__(self, name: str):
        self.name = name


class UserForAllUsersResponse:
    def __init__(self,
                 email: str,
                 first_name: str,
                 last_name: str,
                 join_date: str,
                 account_role: str,
                 has_access_to_all_spaces: bool,
                 member_in_spaces: List[str]):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.join_date = join_date
        self.account_role = account_role
        self.has_access_to_all_spaces = has_access_to_all_spaces
        self.member_in_spaces = member_in_spaces


class RegionResponse:
    def __init__(
            self,
            region_id: str,
            region_name: str
    ):
        self.region_id = region_id
        self.region_name = region_name


class GetImagesResponse:
    def __init__(self, image_id: str, image_name: str):
        self.image_id = image_id
        self.image_name = image_name


class GetInstanceTypesResponse:
    def __init__(self, instance_type_name: str):
        self.instance_type_name = instance_type_name


class VerifyCloudProviderResourceResponse:
    def __init__(self,
                 resource_type: str,
                 resource_name: str,
                 resource_id: str = None,
                 resource_status: str = None,
                 resource_valid: bool = False):
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.resource_id = resource_id
        self.resource_status = resource_status
        self.resource_valid = resource_valid


class VerifyCloudProviderResponse:
    def __init__(self, success: bool,
                 resources_summary: List[VerifyCloudProviderResourceResponse] = None):
        self.success = success
        self.resources_summary = resources_summary


class AccountRepositoryDetailsBranchResponse:
    def __init__(self, name: str):
        self.name = name


class AccountRepositoryDetailsResponse:
    def __init__(self, repository_name: str,
                 repository_full_name: str,
                 default_branch: str,
                 branches: [AccountRepositoryDetailsBranchResponse]):
        self.repository_name = repository_name
        self.repository_full_name = repository_full_name
        self.default_branch = default_branch
        self.branches = branches


class BlueprintValidationResponse:
    def __init__(self,
                 name: str,
                 description: str,
                 url: str,
                 source: BlueprintSourceResponse,
                 artifacts: Dict[str, str],
                 inputs: List[BlueprintInputResponse],
                 errors: List[Error],
                 services: List[BlueprintServiceResponse],
                 applications: List[BlueprintApplicationResponse],
                 clouds: List[BlueprintCloudResponse]):
        self.name = name
        self.description = description
        self.url = url
        self.source = source
        self.artifacts = artifacts
        self.inputs = inputs
        self.errors = errors
        self.services = services
        self.applications = applications
        self.clouds = clouds


class SpaceRepositoryResponse:
    def __init__(self, repository_name: str,
                 repository_type: str,
                 repository_url: str,
                 branch: str):
        self.repository_name = repository_name
        self.repository_type = repository_type
        self.repository_url = repository_url
        self.branch = branch


class DirectAwsSshResponse:
    def __init__(self, connection: str, pem_file_url: str):
        self.connection = connection
        self.pem_file_url = pem_file_url


class DirectAzureSshResponse:
    def __init__(self, connection: str, password: str):
        self.connection = connection
        self.password = password


class DirectRdpResponse:
    def __init__(self, rdp_file_url: str, username: str, password: str):
        self.rdp_file_url = rdp_file_url
        self.username = username
        self.password = password


class ParameterStoreOrigin(str, Enum):
    Literal = 'literal'
    AwsSsm = 'aws-ssm'


class ParameterStoreValue(metaclass=abc.ABCMeta):
    def __init__(self):
        pass


class LiteralValue(ParameterStoreValue):
    def __init__(self, content: str):
        super().__init__()
        self.content = content


class AwsSsmValue(ParameterStoreValue):
    def __init__(self, path: str):
        super().__init__()
        self.path = path


class ParameterStoreItem:
    def __init__(self, name: str, origin: str, value: ParameterStoreValue, description: str = '', modified_by=None,
                 last_modified=None):
        self.name = name
        self.origin = origin
        self.description = description
        self.value = value
        self.last_modified = last_modified
        self.modified_by = modified_by


class CreateAccountFinalizeResponse:
    def __init__(self, account_name: str, user_email: str, first_name: str, last_name: str):
        self.account_name = account_name
        self.user_email = user_email
        self.first_name = first_name
        self.last_name = last_name





class CustomTagOverrideResponse:
    def __init__(self,
                 name: str,
                 value: str,
                 modified_by: str,
                 last_modified: datetime,
                 created_by: str,
                 created_date: datetime,
                 ):
        self.name = name
        self.value = value
        self.modified_by = modified_by
        self.last_modified = last_modified
        self.created_date = created_date
        self.created_by = created_by


class TerraformModuleDescriptorResponse(TerraformModuleDescriptor):
    def __init__(self, module_name: str = None, module_repo_name: str = None, module_root_path: str = None,
                 description: str = None, terraform_version: str = None, enable_auto_tagging: bool = None,
                 exclude_from_tagging: List[str] = None, inputs: List[TerraformModuleInput] = None,
                 outputs: List[TerraformModuleOutput] = None,
                 compute_services: List[TerraformModuleComputeService] = None,
                 allowed_spaces: List[str] = None, modified_by: str = None, last_modified: datetime = None,
                 created_by: str = None, created_date: datetime = None):
        super().__init__(module_name=module_name, module_repo_name=module_repo_name, module_root_path=module_root_path,
                         description=description, terraform_version=terraform_version,
                         enable_auto_tagging=enable_auto_tagging, exclude_from_tagging=exclude_from_tagging,
                         inputs=inputs, outputs=outputs, compute_services=compute_services,
                         allowed_spaces=allowed_spaces)
        self.created_date = created_date
        self.created_by = created_by
        self.last_modified = last_modified
        self.modified_by = modified_by

    def __eq__(self, other):
        if not isinstance(other, TerraformModuleDescriptor):
            return NotImplemented
        return super(TerraformModuleDescriptorResponse, self).__eq__(other)


class SpaceTerraformModuleResponse:
    def __init__(
            self,
            module_alias: str,
            module_name: str,
            description: Optional[str],
            cloud_account_name: str,
            compute_service_name: str,
            region: Optional[str],
            enable_logs: bool,
            inputs: Optional[List[SpaceTerraformModuleInput]]
    ):
        self.module_alias = module_alias
        self.module_name = module_name
        self.description = description
        self.cloud_account_name = cloud_account_name
        self.compute_service_name = compute_service_name
        self.region = region
        self.enable_logs = enable_logs
        self.inputs = inputs
