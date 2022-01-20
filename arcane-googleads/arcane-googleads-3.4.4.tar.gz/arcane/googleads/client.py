from typing import Dict, Optional, Union, cast
import backoff

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import ServiceUnavailable
from google.auth.exceptions import RefreshError

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY, BadRequestError
from arcane.core.types import BaseAccount
from arcane.datastore import Client as DatastoreClient

from .exceptions import GoogleAdsAccountNoAccessException, GoogleAdsAccountException
from .helpers import (
    get_google_ads_account,
    remove_dash,
    _get_user_initialized_client,
    _init_datastore_client,
    get_login_customer_id_and_developer_token
)


_GOOGLE_ADS_VERSION = "v7"


class Client():
     def __init__(self, google_ads_client: GoogleAdsClient, creator_email: Optional[str] = None):
        self.google_ads_client = google_ads_client
        self.creator_email = creator_email


def get_google_ads_client(
    mcc_credentials_path: str,
    google_ads_account: Optional[Dict] = None,
    base_account: Optional[BaseAccount] = None,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    auth_enabled: bool = True,
    datastore_client: Optional[DatastoreClient] = None,
    gcp_project: Optional[str] = None,
    secret_key_file: Optional[str] = None,
    user_email: Optional[str] = None,
    login_customer_id: Optional[str] = None,
) -> Client:
    """Initialize google ads client depending on arguments furnished
    Priority order is: creator_email (obtained with google_ads_account/google_ads_account_id/user_email) > credentials_path
    Args:
        mcc_credentials_path (str): arcane mcc credentials. Defaults to None.
        google_ads_account (Optional[Dict], optional): Account for which we want to init google ads client. Defaults to None.
        base_account (Optional[BaseAccount], optional): Account information needed to get the account for which we want to init google ads client. Defaults to None.
        clients_service_url: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        firebase_api_key: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        gcp_credentials_path: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        auth_enabled: (bool, optional): Needed for getting goolge ads account if not provided. Defaults to True.
        datastore_client: (Optional[str], optional): Needed for getting google_ads_user_credential. Defaults to None.
        gcp_project: (Optional[str], optional): Needed for getting google_ads_user_credential. Defaults to None.
        secret_key_file: (Optional[str], optional): Needed for decrypting google_ads_user_credential. Defaults to None.
        user_email: (Optional[str], optional): Needed when the account related is not yet created in db. Defaults to None.
        login_customer_id: (Optional[str], optional): Needed when the account related is not yet created in db. Defaults to None.
    Raises:
        arcane.core.BadRequestError

    Returns:
        Client: Client
    """

    if mcc_credentials_path and (google_ads_account or base_account or user_email):
        if user_email:
            creator_email = user_email
        else:
            if google_ads_account is None and base_account is None:
                raise BadRequestError('google_ads_account and base_account should not be None simultaneously')
            if google_ads_account is None:
                base_account = cast(BaseAccount, base_account)
                google_ads_account = get_google_ads_account(
                    base_account=base_account,
                    clients_service_url=clients_service_url,
                    firebase_api_key=firebase_api_key,
                    gcp_credentials_path=gcp_credentials_path,
                    auth_enabled=auth_enabled
                )
            creator_email = google_ads_account.get('creator_email')
            login_customer_id = google_ads_account.get('login_customer_id')
        if creator_email:
            _, developer_token = get_login_customer_id_and_developer_token(mcc_credentials_path)
            if not secret_key_file:
                raise BadRequestError('secret_key_file should not be None while using user access protocol')
            elif not developer_token:
                raise BadRequestError('developer_token should not be None while using user access protocol')
            return Client(
                _get_user_initialized_client(
                    user_email=creator_email,
                    secret_key_file=secret_key_file,
                    developer_token=developer_token,
                    gcp_credentials_path=gcp_credentials_path,
                    gcp_project=gcp_project,
                    datastore_client=datastore_client,
                    login_customer_id=login_customer_id
                ),
                creator_email=creator_email
            )
        return get_gads_client_initialized_with_arcane_mcc_credentials(mcc_credentials_path)
    elif mcc_credentials_path:
        return get_gads_client_initialized_with_arcane_mcc_credentials(mcc_credentials_path)
    else:
        raise BadRequestError('one of the following arguments must be specified: mcc_credentials_path and (google_ads_account or base_account or user_email)')


def get_google_ads_service(service_name: str, google_ads_client: GoogleAdsClient, version: str = _GOOGLE_ADS_VERSION):
    return google_ads_client.get_service(service_name, version=version)


@backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
def check_access_account(
    google_ads_account: Optional[Dict] = None,
    base_account: Optional[BaseAccount] = None,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    mcc_credentials_path: Optional[str] = None,
    datastore_client: Optional[DatastoreClient] = None,
    gcp_project: Optional[str] = None,
    secret_key_file: Optional[str] = None,
    client: Optional[Client] = None,
    mcc_account_allowed: Optional[bool] = False
):
    """Check if we can access to an GAdsAccount stored in database

    Args:
        google_ads_account (Optional[Dict], optional): Account for which we want to init google ads client. Defaults to None.
        base_account (Optional[BaseAccount], optional): Account information needed to get the account for which we want to init google ads client. Defaults to None.
        clients_service_url (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        firebase_api_key (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        gcp_credentials_path (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        mcc_credentials_path (Optional[str], optional): mcc credentials. Defaults to None.
        datastore_client: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        gcp_project: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        secret_key_file: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        client: (Optional[Client], optional): google ads client if already initialized
        mcc_account_allowed: (Optional[bool], optional): Make mcc account accepted only when the client is given. Defaults to False.
    Raises:
        BadRequestError: Raised when arguments are not good
        GoogleAdsAccountNoAccessException: Raised when we have no access
    """
    if not client:
        if mcc_account_allowed:
            raise BadRequestError('mcc_account_allowed is not handled when client is not given')
        if google_ads_account is None:
            if base_account is None:
                raise BadRequestError('google_ads_account and base_account should not be None simultanelously')
            google_ads_account = get_google_ads_account(
                base_account=base_account,
                clients_service_url=clients_service_url,
                firebase_api_key=firebase_api_key,
                gcp_credentials_path=gcp_credentials_path
            )
            creator_email = google_ads_account.get('creator_email')
        else:
            creator_email = google_ads_account.get('creator_email')
        if mcc_credentials_path is None:
            raise BadRequestError('mcc_credentials_path should not be None')
        google_ads_client = get_google_ads_client(
            mcc_credentials_path=mcc_credentials_path,
            google_ads_account=google_ads_account,
            clients_service_url=clients_service_url,
            firebase_api_key=firebase_api_key,
            gcp_credentials_path=gcp_credentials_path,
            datastore_client=datastore_client,
            gcp_project=gcp_project,
            secret_key_file=secret_key_file
        ).google_ads_client
        account_id = google_ads_account['id']
    else:
        google_ads_client = client.google_ads_client
        creator_email = client.creator_email
        if base_account is None:
                    raise BadRequestError('base_account should not be None when google ads client is given')
        account_id = base_account['id']
    try:
        _check_access_account_lgq(account_id, google_ads_client, mcc_account_allowed)
    except GoogleAdsAccountNoAccessException:
        if creator_email:
            message = f"{creator_email} has no longer access to this account."
        else:
            message = "Arcane's Google Ads Manager Account can not access this account."
        raise GoogleAdsAccountNoAccessException(message)
    except (ServiceUnavailable, RefreshError) as err:
        if 'Token has been expired' in str(err) and creator_email:
            raise GoogleAdsAccountNoAccessException(f"{creator_email} authorization has expired.")
        raise


def check_access_before_creation(
    account_id: str,
    user_email: str,
    secret_key_file: str,
    gcp_credentials_path: str,
    gcp_project: str,
    developer_token: str,
) -> Union[str, None]:
    """Check if user identified by its email and our mcc have access or not to an account

    Args:
        account_id (str): Account to check if user has access
        user_email (str): user email
        secret_key_file (str): Path to rsa key to decrypt user credentials stored in datastore
        gcp_credentials_path (str): Needed for getting credentials stored in datastore
        gcp_project (str): Needed for getting credentials stored in datastore
        developer_token (str): developer token for accessing the API.

    Raises:
        GoogleAdsAccountNoAccessException
        GoogleAdsException

    Returns:
        bool: our mcc does it have access
    """
    user_access = False

    datastore_client = _init_datastore_client(gcp_credentials_path, gcp_project)

    client_initialized_with_user_direct_access = _get_user_initialized_client(
        user_email=user_email,
        secret_key_file=secret_key_file,
        developer_token=developer_token,
        gcp_credentials_path=gcp_credentials_path,
        gcp_project=gcp_project,
        datastore_client=datastore_client
    )
    customer_service = client_initialized_with_user_direct_access.get_service(
        "CustomerService")

    accessible_customers = customer_service.list_accessible_customers()
    mcc_list = []
    for customer_resource_name in accessible_customers.resource_names:
        accessible_account_id = str(customer_resource_name).replace('customers/', '')
        try:
            customers = get_customer(
                accessible_account_id, client_initialized_with_user_direct_access)
            customer_resp = customers[0]
        except GoogleAdsException:
            continue

        if customer_resp.customer.manager:
            mcc_list.append(accessible_account_id)
        if remove_dash(account_id) == accessible_account_id:
            ## Check if user have direct access
            user_access = True

    for login_customer_id in mcc_list:
        ## Check if user has access with an MCC
        try:
            client_initialized_with_user_access_via_mcc = _get_user_initialized_client(
                user_email=user_email,
                secret_key_file=secret_key_file,
                developer_token=developer_token,
                gcp_credentials_path=gcp_credentials_path,
                gcp_project=gcp_project,
                datastore_client=datastore_client,
                login_customer_id=login_customer_id
            )
            _check_access_account_lgq(
                account_id, client_initialized_with_user_access_via_mcc)
            return login_customer_id
        except GoogleAdsAccountNoAccessException:
            pass
    if user_access:
        return None
    else:
        raise GoogleAdsAccountNoAccessException(
            "You don't have access to this Google Ads account, you cannot link it to SmartFeeds. Please ask someone else who have access to do the linking")


def _check_access_account_lgq(
    google_ads_account_id: str,
    google_ads_client: GoogleAdsClient,
    mcc_account_allowed: Optional[bool] = False
):
    try:
        customers = get_customer(google_ads_account_id, google_ads_client)
        if len(customers) == 0:
            raise GoogleAdsAccountException(
                f"We cannot find this account ({google_ads_account_id}). Are you sure you entered the correct id?")
        customer_resp = customers[0]
    except GoogleAdsException as err:
        if "USER_PERMISSION_DENIED" in str(err):
            raise GoogleAdsAccountNoAccessException
        elif "INVALID_CUSTOMER_ID" in str(err):
            raise GoogleAdsAccountException(
                f"Invalid account id ({google_ads_account_id}). Are you sure you entered the correct id?"
            )
        elif "CUSTOMER_NOT_FOUND" in str(err):
            raise GoogleAdsAccountException(
                f"We cannot find this account ({google_ads_account_id}). Are you sure you entered the correct id?")
        elif "CUSTOMER_NOT_ENABLED" in str(err):
            raise GoogleAdsAccountException(
                f"This Account is not enabled ({google_ads_account_id}).")
        raise
    if not mcc_account_allowed and customer_resp.customer.manager:
        raise GoogleAdsAccountException(
            'This account ID is a MCC. Please enter a Google Ads Account.')


def get_customer(google_ads_account_id: str, google_ads_client: GoogleAdsClient):
    """Unlike customer_service.get_customer, this function use a search request that do not count in our daily quotas
    """
    account_id = remove_dash(google_ads_account_id)
    google_ads_service = get_google_ads_service(
        'GoogleAdsService', google_ads_client)

    query = f"""
        SELECT
          customer.manager
        FROM customer
        WHERE customer.id = '{account_id}'"""
    search_query = google_ads_client.get_type(
        "SearchGoogleAdsRequest"
    )
    search_query.customer_id = account_id
    search_query.query = query
    return list(google_ads_service.search(search_query))


def get_gads_client_initialized_with_arcane_mcc_credentials(mcc_credentials_path: str) -> Client:
    """Init a gads client with arcane mcc credentials

    Args:
        mcc_credentials_path (str): arcane mcc credentials.

    Returns:
        Client
    """
    return Client(GoogleAdsClient.load_from_storage(mcc_credentials_path))
