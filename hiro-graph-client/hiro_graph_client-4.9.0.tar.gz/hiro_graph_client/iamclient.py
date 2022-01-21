#!/usr/bin/env python3
from typing import Any, Iterator
from urllib.parse import quote_plus

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroIam(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO IAM REST API.
    See https://core.arago.co/help/specs/?url=definitions/iam.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='iam',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations against the IAM API
    ###############################################################################################################

    ###############################################################################################################
    # Accounts
    ###############################################################################################################

    def create_account(self, data: dict, import_flag: bool = None) -> dict:
        """
        create an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/post_accounts

        :param import_flag: Default is false
        :param data: The dict with the account data.
        :return: Dict with the result
        """
        query = {
            "import": import_flag
        }

        url = self.endpoint + "/accounts" + self._get_query_part(query)
        return self.post(url, data)

    def update_account(self, account_id: str, data: dict) -> dict:
        """
        update an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/post_accounts__id_

        :param account_id: ogit/_id of the ogit/Auth/Account
        :param data: The dict with the account data.
        :return: Dict with the result
        """
        url = self.endpoint + "/accounts/" + quote_plus(account_id)
        return self.post(url, data)

    def get_account(self, account_id: str, profile: bool = None) -> dict:
        """
        gets an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/get_accounts__id_

        :param profile: return account with profile. Default false.
        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result
        """
        query = {
            "profile": profile
        }

        url = self.endpoint + "/accounts/" + quote_plus(account_id) + self._get_query_part(query)
        return self.get(url)

    def delete_account(self, account_id: str) -> dict:
        """
        deletes an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/delete_accounts__id_

        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result
        """
        url = self.endpoint + "/accounts/" + quote_plus(account_id)
        return self.delete(url)

    def activate_account(self, node_id: str) -> dict:
        """
        activates an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/patch_accounts__id__activate

        :param node_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result
        """
        url = self.endpoint + "/accounts/" + quote_plus(node_id) + "/activate"
        return self.patch(url, data=None)

    def get_account_avatar(self, account_id: str) -> Iterator[bytes]:
        """
        gets avatar of account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/get_accounts__id__avatar

        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Binary content of the avatar
        """
        url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/avatar"
        return self.get_binary(url)

    def put_account_avatar(self, account_id: str, data: Any, content_type: str = 'image/png') -> str:
        """
        sets the avatar of account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/put_accounts__id__avatar

        :param account_id: ogit/_id of the ogit/Auth/Account
        :param data: Binary data for image of avatar.
        :param content_type: Content-Type. Default: image/png
        :return: The result payload / size of the avatar in bytes.
        """
        url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/avatar"
        return self.put_binary(url, data, content_type=content_type)

    def deactivate_account(self, account_id: str, reason: str) -> dict:
        """
        deactivates an account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/patch_accounts__id__deactivate

        :param reason: reason of deactivation of an ogit/Auth/Account.
                       Available values : UserDeactivated, AdminDeactivated, PasswordExpired, AutoDeactivated, None
        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result
        """
        query = {
            "reason": reason
        }

        url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/deactivate" + self._get_query_part(query)
        return self.patch(url, data=None)

    def put_account_password(self, account_id: str, data: dict) -> dict:
        """
        set password of account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/put_accounts__id__password

        :param account_id: ogit/_id of the ogit/Auth/Account
        :param data: The dict with the new password data.
        :return: Dict with the result
        """
        url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/password"
        return self.post(url, data)

    def get_account_profile(self, account_id: str = None, profile_id: str = None) -> dict:
        """
        get profile of account

        You need to specify either profile_id or account_id.

          With account_id: https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/get_accounts__id__profile

          With profile_id: https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/get_accounts_profile__profileId_

        :param profile_id: ogit/_id of the ogit/Auth/AccountProfile
        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result or an empty dict if neither account_id nor profile_id are given.
        """
        if account_id:
            url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/profile"
        elif profile_id:
            url = self.endpoint + "/accounts/profile/" + quote_plus(profile_id)
        else:
            return {}

        return self.get(url)

    def get_account_teams(self, account_id: str, include_virtual: bool = None) -> dict:
        """
        get teams of account
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/get_accounts__id__teams

        :param include_virtual: return virtual teams in output. Default false.
        :param account_id: ogit/_id of the ogit/Auth/Account
        :return: Dict with the result
        """
        query = {
            "include_virtual": include_virtual
        }

        url = self.endpoint + "/accounts/" + quote_plus(account_id) + "/teams" + self._get_query_part(query)
        return self.get(url)

    def update_account_profile(self, profile_id: str, data: dict) -> dict:
        """
        updates an account profile
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Account/post_accounts_profile__profileId_

        :param data: Dict with the new profile data.
        :param profile_id: ogit/_id of the ogit/Auth/AccountProfile
        :return: Dict with the result
        """
        url = self.endpoint + "/accounts/profile/" + quote_plus(profile_id)
        return self.post(url, data)

    ###############################################################################################################
    # DataScope
    ###############################################################################################################

    def create_scope(self, data: dict) -> dict:
        """
        creates a DataScope
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_DataScope/post_scope

        :param data: Dict with the new scope data.
        :return: Dict with the result
        """
        url = self.endpoint + "/scope"
        return self.post(url, data)

    def get_scope(self, scope_id: str) -> dict:
        """
        retrieves a DataScope
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_DataScope/get_scope__id_

        :param scope_id: ogit/_id of the ogit/Auth/DataScope
        :return: Dict with the result
        """
        url = self.endpoint + "/scope/" + quote_plus(scope_id)
        return self.get(url)

    def update_scope(self, scope_id: str, data: dict) -> dict:
        """
        updates a DataScope
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_DataScope/put_scope__id_

        :param scope_id: ogit/_id of the ogit/Auth/DataScope
        :param data: Dict with the new scope data.
        :return: Dict with the result
        """
        url = self.endpoint + "/scope/" + quote_plus(scope_id)
        return self.put(url, data)

    ###############################################################################################################
    # Organization
    ###############################################################################################################

    def create_organization(self, data: dict) -> dict:
        """
        creates an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/post_organization

        :param data: Dict with the new organization data.
        :return: Dict with the result
        """
        url = self.endpoint + "/organization"
        return self.post(url, data)

    def get_organization_configuration(self, organization_id: str) -> dict:
        """
        gets configuration of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__configuration

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/configuration"
        return self.get(url)

    def update_organization_configuration(self, organization_id: str, data: dict) -> dict:
        """
        updates configuration of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/put_organization__id__configuration

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :param data: Dict with the new organization data.
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/configuration"
        return self.put(url, data)

    def get_organization_datasets(self, organization_id: str) -> dict:
        """
        gets datasets of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__datasets

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/datasets"
        return self.get(url)

    def get_organization_domains(self, organization_id: str) -> dict:
        """
        gets domains of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__domains

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/domains"
        return self.get(url)

    def get_organization_roleassignments(self, organization_id: str) -> dict:
        """
        gets roleassignments of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__roleassignments

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/roleassignments"
        return self.get(url)

    def get_organization_scopes(self, organization_id: str) -> dict:
        """
        gets scopes of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__scopes

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/scopes"
        return self.get(url)

    def get_organization_teams(self, organization_id: str) -> dict:
        """
        gets teams of an Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__teams

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Dict with the result
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/teams"
        return self.get(url)

    def get_organization_avatar(self, organization_id: str) -> Iterator[bytes]:
        """
        gets avatar of Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/get_organization__id__avatar

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :return: Binary content of the avatar
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/avatar"
        return self.get_binary(url)

    def put_organization_avatar(self, organization_id: str, data: Any, content_type: str = 'image/png') -> str:
        """
        sets the avatar of Auth Organization
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Organization/put_organization__id__avatar

        :param organization_id: ogit/_id of the ogit/Auth/Organization
        :param data: Binary data for image of avatar.
        :param content_type: Content-Type. Default: image/png
        :return: The result payload / size of the avatar in bytes.
        """
        url = self.endpoint + "/organization/" + quote_plus(organization_id) + "/avatar"
        return self.put_binary(url, data, content_type=content_type)

    ###############################################################################################################
    # Org Domain
    ###############################################################################################################

    def create_domain(self, data: dict) -> dict:
        """
        creates an Org Domain
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_OrgDomain/post_domain

        :param data: Dict with the new domain data.
        :return: Dict with the result
        """
        url = self.endpoint + "/domain"
        return self.post(url, data)

    def get_domain(self, domain_id: str) -> dict:
        """
        retrieves an Org Domain
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_OrgDomain/get_domain__id_

        :param domain_id: ogit/_id of the ogit/Auth/OrgDomain
        :return: Dict with the result
        """
        url = self.endpoint + "/domain/" + quote_plus(domain_id)
        return self.get(url)

    def delete_domain(self, domain_id: str) -> dict:
        """
        deletes an Org Domain
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_OrgDomain/delete_domain__id_

        :param domain_id: ogit/_id of the ogit/Auth/OrgDomain
        :return: Dict with the result
        """
        url = self.endpoint + "/domain/" + quote_plus(domain_id)
        return self.delete(url)

    def get_domain_organization(self, domain_id: str) -> dict:
        """
        retrieves an Organization of Org Domain
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_OrgDomain/get_domain__id__organization

        :param domain_id: ogit/_id of the ogit/Auth/OrgDomain
        :return: Dict with the result
        """
        url = self.endpoint + "/domain/" + quote_plus(domain_id) + "/organization"
        return self.get(url)

    ###############################################################################################################
    # Auth Role
    ###############################################################################################################

    def create_role(self, data: dict) -> dict:
        """
        creates an Auth Role
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Role/post_role

        :param data: Dict with the new role data.
        :return: Dict with the result
        """
        url = self.endpoint + "/role"
        return self.post(url, data)

    def update_role(self, role_id: str, data: dict) -> dict:
        """
        updates an Auth Role
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Role/put_role__id_

        :param role_id: ogit/_id of the ogit/Auth/Role
        :param data: Dict with the new role data.
        :return: Dict with the result
        """
        url = self.endpoint + "/role/" + quote_plus(role_id)
        return self.put(url, data)

    def get_role(self, role_id: str) -> dict:
        """
        retrieves an Auth Role
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Role/get_role__id_

        :param role_id: ogit/_id of the ogit/Auth/Role
        :return: Dict with the result
        """
        url = self.endpoint + "/role/" + quote_plus(role_id)
        return self.get(url)

    def delete_role(self, role_id: str) -> dict:
        """
        deletes an Auth Role
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Role/delete_role__id_

        :param role_id: ogit/_id of the ogit/Auth/Role
        :return: Dict with the result
        """
        url = self.endpoint + "/role/" + quote_plus(role_id)
        return self.delete(url)

    def get_roles(self) -> dict:
        """
        retrieves public roles
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Role/get_roles

        :return: Dict with the result
        """
        url = self.endpoint + "/roles"
        return self.get(url)

    ###############################################################################################################
    # Auth RoleAssignment
    ###############################################################################################################

    def create_roleassignment(self, data: dict) -> dict:
        """
        creates an Auth RoleAssignment
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_RoleAssignment/post_roleassignment

        :param data: Dict with the new roleassignment data.
        :return: Dict with the result
        """
        url = self.endpoint + "/roleassignment"
        return self.post(url, data)

    def get_roleassignment(self, roleassignment_id: str) -> dict:
        """
        retrieves an Auth RoleAssignment
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_RoleAssignment/get_roleassignment__id_

        :param roleassignment_id: ogit/_id of the ogit/Auth/RoleAssignment
        :return: Dict with the result
        """
        url = self.endpoint + "/roleassignment/" + quote_plus(roleassignment_id)
        return self.get(url)

    def delete_roleassignment(self, roleassignment_id: str) -> dict:
        """
        deletes an Auth RoleAssignment
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_RoleAssignment/delete_roleassignment__id_

        :param roleassignment_id: ogit/_id of the ogit/Auth/RoleAssignment
        :return: Dict with the result
        """
        url = self.endpoint + "/roleassignment/" + quote_plus(roleassignment_id)
        return self.delete(url)

    ###############################################################################################################
    # Auth Team
    ###############################################################################################################

    def create_team(self, data: dict) -> dict:
        """
        creates an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/post_team

        :param data: Dict with the new team data.
        :return: Dict with the result
        """
        url = self.endpoint + "/team"
        return self.post(url, data)

    def update_team(self, team_id: str, data: dict) -> dict:
        """
        updates an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/put_team__id_

        :param team_id: ogit/_id of the ogit/Auth/Team
        :param data: Dict with the new team data.
        :return: Dict with the result
        """
        url = self.endpoint + "/team/" + quote_plus(team_id)
        return self.put(url, data)

    def get_team(self, team_id: str) -> dict:
        """
        retrieves an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/get_team__id_

        :param team_id: ogit/_id of the ogit/Auth/Team
        :return: Dict with the result
        """
        url = self.endpoint + "/team/" + quote_plus(team_id)
        return self.get(url)

    def delete_team(self, team_id: str) -> dict:
        """
        deletes an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/delete_team__id_

        :param team_id: ogit/_id of the ogit/Auth/Team
        :return: Dict with the result
        """
        url = self.endpoint + "/team/" + quote_plus(team_id)
        return self.delete(url)

    def get_team_members(self, team_id: str, profile: bool = None) -> dict:
        """
        gets members of an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/get_team__id__members

        :param profile: return account with profile. Default False.
        :param team_id: ogit/_id of the ogit/Auth/Team
        :return: Dict with the result
        """

        query = {
            "profile": profile
        }

        url = self.endpoint + "/team/" + quote_plus(team_id) + "/members" + self._get_query_part(query)
        return self.get(url)

    def add_team_members(self, team_id: str, data: dict) -> dict:
        """
        adds members to an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/post_team__id__members_add

        :param team_id: ogit/_id of the ogit/Auth/Team
        :param data: dict with the account data
        :return: Dict with the result
        """

        url = self.endpoint + "/team/" + quote_plus(team_id) + "/members/add"
        return self.post(url, data)

    def remove_team_members(self, team_id: str, data: dict) -> dict:
        """
        adds members to an Auth Team
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_Auth_Team/post_team__id__members_remove

        :param team_id: ogit/_id of the ogit/Auth/Team
        :param data: dict with the account data
        :return: Dict with the result
        """

        url = self.endpoint + "/team/" + quote_plus(team_id) + "/members/remove"
        return self.post(url, data)

    ###############################################################################################################
    # DataSet
    ###############################################################################################################

    def create_dataset(self, data: dict) -> dict:
        """
        creates a DataSet
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_DataSet/post_dataset

        :param data: Dict with the new dataset data.
        :return: Dict with the result
        """
        url = self.endpoint + "/dataset"
        return self.post(url, data)

    def update_dataset(self, dataset_id: str, data: dict) -> dict:
        """
        updates a DataSet
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_DataSet/put_dataset__id_

        :param dataset_id: ogit/_id of the ogit/Auth/DataSet
        :param data: Dict with the new dataset data.
        :return: Dict with the result
        """
        url = self.endpoint + "/dataset/" + quote_plus(dataset_id)
        return self.put(url, data)

    def get_dataset(self, dataset_id: str) -> dict:
        """
        retrieves a DataSet
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_DataSet/get_dataset__id_

        :param dataset_id: ogit/_id of the ogit/Auth/DataSet
        :return: Dict with the result
        """
        url = self.endpoint + "/dataset/" + quote_plus(dataset_id)
        return self.get(url)

    def delete_dataset(self, dataset_id: str) -> dict:
        """
        deletes a DataSet
        https://core.arago.co/help/specs/?url=definitions/iam.yaml#/[Management]_DataSet/delete_dataset__id_

        :param dataset_id: ogit/_id of the ogit/Auth/DataSet
        :return: Dict with the result
        """
        url = self.endpoint + "/dataset/" + quote_plus(dataset_id)
        return self.delete(url)
