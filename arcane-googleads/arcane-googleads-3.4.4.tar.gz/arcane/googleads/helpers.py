from typing import Dict, Optional
from yaml import load, FullLoader
import json

from google.ads.googleads.client import GoogleAdsClient
from google.oauth2.credentials import Credentials

from arcane.datastore import Client as DatastoreClient
from arcane.core import UserRightsEnum, RightsLevelEnum, BadRequestError, BaseAccount, GOOGLE_ADS_USER_CREDENTIAL_KIND
from arcane.requests import call_get_route
from arcane.secret import decrypt

from .exceptions import EmptyCredentialsError

def remove_dash(account_id: str) -> str:
    """ Removes '-' from account_id to make it valid for requests """
    return account_id.replace('-', '')


def format_id_with_dashes(id):
    """ format id to be a string in the format XXX-XXX-XXXX (as stored in db)"""
    account_id = list(remove_dash(id))
    account_id.insert(3, '-')
    account_id.insert(7, '-')
    return ''.join(account_id)


def get_google_ads_account(
    base_account: BaseAccount,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    auth_enabled: bool = True
) -> Dict:
    if not clients_service_url or not firebase_api_key or not gcp_credentials_path:
                raise BadRequestError('clients_service_url or firebase_api_key or  gcp_credentials_path should not be None if google_ads_account is not provided')
    url = f"{clients_service_url}/api/google-ads-account?account_id={base_account['id']}&client_id={base_account['client_id']}"
    accounts = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights':{UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=gcp_credentials_path
    )
    if len(accounts) == 0:
        raise BadRequestError(f'Error while getting google ads account with: {base_account}. No account corresponding.')
    elif len(accounts) > 1:
        raise BadRequestError(f'Error while getting google ads account with: {base_account}. Several account corresponding: {accounts}')

    return accounts[0]


def _get_google_ads_user_crendential(
    user_email: str,
    datastore_client: Optional[DatastoreClient] = None,
    gcp_credentials_path: Optional[str] = None,
    gcp_project: Optional[str] = None
) -> Dict:
    if not datastore_client:
        datastore_client = _init_datastore_client(gcp_credentials_path, gcp_project)
    query = datastore_client.query(kind=GOOGLE_ADS_USER_CREDENTIAL_KIND).add_filter('email', '=', user_email)
    users_credential = list(query.fetch())
    if len(users_credential) == 0:
        raise BadRequestError(f'Error while getting google ads user credentials with mail: {user_email}. No entity corresponding.')
    elif len(users_credential) > 1:
        raise BadRequestError(f'Error while getting google ads user credentials with mail: {user_email}. Several entities corresponding: {users_credential}')
    return users_credential[0]


def get_login_customer_id_and_developer_token(mcc_credentials_path: str):
    ads_credentials_file = open(mcc_credentials_path)
    parsed_credentials_file = load(ads_credentials_file, Loader=FullLoader)

    return str(parsed_credentials_file["login_customer_id"]), parsed_credentials_file["developer_token"]


def _init_datastore_client(gcp_credentials_path, gcp_project):
    if not gcp_credentials_path and not gcp_project:
            raise BadRequestError('gcp_credentials_path or gcp_project should not be None if datastore_client is not provided')
    return DatastoreClient.from_service_account_json(
            gcp_credentials_path, project=gcp_project)


def _get_user_initialized_client(
    user_email: str,
    secret_key_file: str,
    developer_token: str,
    gcp_credentials_path: Optional[str] = None,
    gcp_project: Optional[str] = None,
    datastore_client: Optional[DatastoreClient] = None,
    login_customer_id: Optional[str] = None,
):
    user_credentials = _get_google_ads_user_crendential(user_email, datastore_client, gcp_credentials_path, gcp_project)

    if user_credentials.get('credentials') is None:
        error_message = "Please renew the access you give us. To do so: \n \n" \
            "1 - Please visit: https://myaccount.google.com/permissions \n" \
            "2 - Search for AMS in 'Third-party apps with account access' list \n" \
            "3 - Click on it and press on 'Remove Access' \n" \
            "4 - Close this dialog and try again to add an account \n \n" \
            "If the problem persists, please contact our support team."
        raise EmptyCredentialsError(error_message)

    credentials = init_google_ads_credentials(user_credentials['credentials'], secret_key_file)

    if login_customer_id is None:
        return GoogleAdsClient(
            credentials,
            developer_token
        )
    return GoogleAdsClient(
        credentials,
        developer_token,
        login_customer_id=login_customer_id
    )


def init_google_ads_credentials(credentials_encrypt: bytes, secret_key_file: str,):
    credentials = json.loads(decrypt(credentials_encrypt, secret_key_file).decode('utf-8'))
    credentials['token'] = None
    return Credentials(**credentials)
