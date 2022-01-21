from __future__ import unicode_literals

import base64
import logging
import time
import traceback
import random
import requests
from datetime import datetime

from MammothAnalytics import const
from MammothAnalytics.const import USER_PERMISSIONS, RESERVED_BATCH_COLUMN_INTERNAL_NAMES_AND_KEYS
from MammothAnalytics.errors import AuthError, UnknownError
from MammothAnalytics.errors import MalformedRequestError, AuthenticationError, \
    NotFoundError, AuthorizationError
from .urls import get_url
import pydash

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)

MAX_RETRIES = 80
RETRY_DELAY_IN_SEC = 2


def handleError(f):
    def new_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AuthError, UnknownError, NotFoundError, AuthenticationError,
                AuthorizationError, MalformedRequestError) as e:
            raise e
        except Exception as e:
            fname = f.__name__
            log.error({
                'function_name': fname,
                'args': args,
                'kwrgs': kwargs
            })
            log.error(''.join(traceback.format_exc()))
            raise UnknownError(0, 'Error in: {0}'.format(fname))

    new_function.__name = f.__name__
    new_function.__doc__ = f.__doc__
    return new_function


def encode_integration_key(key):
    """encrypt the base 64 encrypted integration key to escape adblocker
    Args:
        key (string): base 64 encrypted integration key of the connector
    Returns:
        string: integration string of the connector
    """
    return base64.b64encode(key.encode('ascii')).decode()


class MammothConnector(object):
    def __init__(self, email=None, password=None, account_id=None, token=None, api_url=None, api_key=None, api_secret=None):

        """
        The main class for handling Mammoth Analytics API
        :param email: The email of the user
        :param password: The password of the user
        :param account_id: Account ID. If not given now, it can be given after `select accounts`
        """
        if not api_url:
            api_url = const.API
        self.api_url = api_url
        self.__account_id = None

        if token:
            self.__token = token
        elif password:
            response = requests.post(get_url('/login', self.api_url),
                                     json=dict(email=email, password=password, is_long_term=True))
            if response.status_code != 200:
                raise AuthError(response.json()["ERROR_CODE"],
                                '{0}'.format(response.status_code, response.json()['ERROR_MESSAGE']))
            self.__token = response.json()['token']
            response = requests.post(get_url('/login', self.api_url),
                                     json=dict(email=email, password=password, is_long_term=True))
            if response.status_code != 200:
                raise AuthError("username or password is not correct")
            self.__token = response.json()['token']
        elif api_key and api_secret:
            response = requests.post(get_url('/login', self.api_url),
                                     json=dict(api_key=api_key, api_secret=api_secret, is_long_term=True))
            if response.status_code != 200:
                raise AuthError(response.json()["ERROR_CODE"],
                                '{0}'.format(response.status_code, response.json()['ERROR_MESSAGE']))
            self.__token = response.json()['token']
            # adding account_id to the response object since the api key secret login returns the respective account id associated with the given key secret
            account_id = response.json().get('account_id')
        else:
            raise AuthError("Token /Password /Appkey Appsecret needed!")

        if account_id is not None:
            self.select_account(account_id)
        else:
            raise AuthError("Account ID needed!")
        log.info("Logged in as {0} into account {1}".format(email, self.__account_id))

    def __del__(self):
        try:
            if self.__token:
                self.logout()
        except:
            pass

    def _make_signed_request(self, rtype, api, **kwargs):
        log.info((rtype, api))
        headers = {'X-API-KEY': self.__token}
        if self.__account_id:
            headers['X-ACCOUNT-ID'] = str(self.__account_id)
        if 'headers' in kwargs.keys():
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        method_maps = {
            'get': requests.get,
            'post': requests.post,
            'delete': requests.delete,
            'patch': requests.patch
        }
        api_url = get_url(api, self.api_url)
        response = method_maps[rtype](api_url, **kwargs)
        resp = {'ERROR_CODE': 0, 'ERROR_MESSAGE': 'Unknown'}
        try:
            resp = response.json()
            log.debug('response json :{0}'.format(resp))
        except Exception as e:
            raise UnknownError(resp['ERROR_CODE'], 'Server responded with status code :{0}'.format(response.status_code,
                                                                                                   resp[
                                                                                                       'ERROR_MESSAGE']))
        if response.status_code == 200:
            return response
        elif response.status_code == 500:
            if resp['ERROR_CODE'] == 0:
                raise UnknownError(resp['ERROR_CODE'],
                                   'Server responded with status code :{0} and message:'.format(response.status_code,
                                                                                                resp['ERROR_MESSAGE']))
            else:
                raise UnknownError(resp.get('ERROR_CODE'), resp.get('ERROR_MESSAGE'))
        else:
            exc_class = UnknownError
            if response.status_code == 400:
                exc_class = MalformedRequestError
            elif response.status_code == 401:
                exc_class = AuthenticationError
            elif response.status_code == 403:
                exc_class = AuthorizationError
            elif response.status_code == 404:
                exc_class = NotFoundError
            raise exc_class(resp['ERROR_CODE'], resp['ERROR_MESSAGE'])

    @handleError
    def list_accounts(self):
        """
        Returns a list of accounts user has access to
        :return: List of dictionaries. Each dictionary contains id, name and other properties associated with an account
        """
        response = self._make_signed_request('get', '/accounts')
        return response.json()['accounts']

    @handleError
    def list_users(self):
        """
        Returns a list of accounts user has access to
        :return: List of dictionaries. Each dictionary contains id, name and other properties associated with an account
        """
        response = self._make_signed_request('get', '/accounts/{account_id}/users'.format(account_id=self.__account_id))
        return response.json()['users']

    @handleError
    def select_account(self, account_id):
        """
        Sets the account id on the class. This is important to use any other method in the class
        :param account_id: Account id to be selected
        :return: None
        """
        accounts = self.list_accounts()
        account_ids = [a['id'] for a in accounts]
        log.info("Account id list {0}".format(account_ids))
        if account_id in account_ids:
            self.__account_id = account_id
        else:
            raise AuthError(0, "Account ID is not valid")

    @handleError
    def auto_select_account(self):
        """
        selects the first account in the list of accounts the user belongs to
        """
        accounts = self.list_accounts()
        self.select_account(accounts[0]['id'])

    @handleError
    def logout(self):
        """
        Will log out from Mammoth. This is also done automatically when the object is garbage collected.
        :return:
        """
        self._make_signed_request('post', '/logout', json={})

    @handleError
    def add_user_to_account(self, email, full_name, user_permission=USER_PERMISSIONS.ANALYST,
                            get_access_token=False):
        log.info("Account id is {0}".format(self.__account_id))
        response = self._make_signed_request('post',
                                             '/accounts/{account_id}/users'.format(account_id=self.__account_id),
                                             json={
                                                 'email': email,
                                                 'full_name': full_name,
                                                 'perm_name': user_permission,
                                                 'get_access_token': get_access_token
                                             })
        return response.json()

    @handleError
    def remove_user_from_account(self, user_id):
        self._make_signed_request('delete', '/accounts/{account_id}/users/{user_id}'.format(
            account_id=self.__account_id, user_id=user_id
        ))

    @handleError
    def list_datasets(self):
        """
        Returns a list of datasets in the system
        :return: List of dictionaries containing info about the datasets in the system. Contains info such as id, name etc.
        """
        response = self._make_signed_request('get', '/datasets')
        return response.json()['datasets']

    @handleError
    def refresh_dataset(self, ds_id):
        response = self._make_signed_request('patch', '/datasets/{0}'.format(ds_id), json={
            "patch": [{"op": "replace", "path": "data", "value": "refresh"}]})
        return response.json()

    @handleError
    def delete_dataset(self, ds_id):
        response = self._make_signed_request('delete', '/datasets/{0}'.format(ds_id))
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def delete_identity(self, identity_key, integration_key):
        integration_key = encode_integration_key(integration_key)
        response = self._make_signed_request('delete',
                                             '/integrations/{0}/identities/{1}'.format(integration_key, identity_key))
        return response.json()

    @handleError
    def create_dataset(self, name, metadata, display_properties=None):
        """
        Create a dataset in Mammoth Analytics.

        TODO: explain metadata and display properties somewhere and put links here

        :param name: Name of the dataset
        :param metadata: Metadata for the given dataset. This is a list of dict objects. Each dict should contain `display_name`,
            `internal_name` and `type`. `type` should be one of `NUMERIC`, `TEXT` or `DATE`
        :param display_properties: A dictionary of display properties.
        :return: Datasource id
        """
        if not display_properties:
            display_properties = {'FORMAT_INFO': {}, "SORT": []}
        response = self._make_signed_request(
            'post', '/datasets',
            json={'name': name, 'metadata': metadata,
                  'display_properties': display_properties})
        return response.json()['id']

    @handleError
    def create_dataset_from_url(self, file_url):
        """
        Create a dataset from file url
        :params: file url
        :return: dataset id
        """

        file_url_ds_param = {"url": file_url}
        r = self._make_signed_request('post', '/weburls', json=file_url_ds_param)
        response = r.json()

        if response.get('STATUS') == 'SUCCESS':
            file_id = response.get('id')
            self.wait_till_file_processing_get_ds(file_id)
            ds_id = self.get_ds_for_file(file_id)['id']
            return ds_id
        else:
            raise UnknownError(response.get('ERROR_MESSAGE'))

    @handleError
    def create_webhook_dataset(self, name, is_secure=False, ds_mode="Replace"):
        """
        Create a webhook dataset in Mammoth Analytics.
        Args:
            name: Name of the dataset
            is_secure: Is secure True/False
            ds_mode: Dataset mode of the dataset Replace/Combine
        Return:
            response.json(): Datasource id
        """
        webhook_ds_param = {"name": name, "origins": "*", "is_secure": is_secure, "mode": ds_mode}
        response = self._make_signed_request(
            'post', '/webhooks',
            json=webhook_ds_param)
        return response.json()

    @handleError
    def get_webhook_by_uri(self, webhook_uri):
        webhook_details = None
        all_webhooks = self.list_webhooks()
        for wh in all_webhooks:
            if wh.get('url') == webhook_uri:
                webhook_details = wh
                break
        return webhook_details

    @handleError
    def list_webhooks(self):
        response = self._make_signed_request('get', 'webhooks').json()
        webhooks = response.get('webhooks', [])
        return webhooks

    @handleError
    def post_data_to_webhook(self, uri, data):
        if not isinstance(uri, str):
            raise TypeError("webhook uri should be of string type. found {0} instead".format(type(uri)))
        return self._make_signed_request('post', uri, json=data)

    @handleError
    def list_batches(self, ds_id):
        response = self._make_signed_request('get', '/datasets/{0}/batches'.format(ds_id))
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def delete_batches(self, ds_id, batches):
        response = self._make_signed_request('patch', '/datasets/{0}/batches'.format(ds_id), json={
            "patch": [{"op": "remove", "path": "datasources", "value": batches}]})
        return response.json()

    @handleError
    def get_dataset(self, ds_id, include_row_count=True):
        """
        Returns a dataset information dictionary for the given ID
        :param ds_id: The datasource id
        :return: dictionary containing information on the dataset
        """
        response = self._make_signed_request('get', '/datasets/{0}?INCLUDE_ROW_COUNT={1}'.format(ds_id, include_row_count))
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def get_batch(self, ds_id, batch_id, columns=None, condition=None, limit=None, offset=None):
        """
        Method to get paginated data for a particular batch of a dataset
        """
        paging_params = {
            'columns': columns,
            'condition': condition,
            'limit': limit,
            'offset': offset
        }
        response = self._make_signed_request('get',
                                             '/ datasets / {dataset_id} / batches / {batch_id}'.format(dataset_id=ds_id,
                                                                                                       batch_id=batch_id),
                                             json=paging_params)

        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def get_task(self, view_id):
        response = self._make_signed_request('get', '/workspaces/{0}/tasks'.format(view_id))
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response.get('tasks')

    @handleError
    def add_task(self, view_id, params, wait_till_ready=True):
        r = self._make_signed_request('post', '/workspaces/{0}/tasks'.format(view_id), json={'param': params})
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def update_task(self, view_id, task_id, params, wait_till_ready=True):
        r = self._make_signed_request('patch', '/workspaces/{0}/tasks/{1}'.format(view_id, task_id),
                                      json={"patch": [{"op": "replace", "path": "params", "value": params}]})
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def delete_task(self, view_id, task_id, wait_till_ready=True):
        r = self._make_signed_request('delete', '/workspaces/{0}/tasks/{1}'.format(view_id, task_id))
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def refresh_webhook_data(self, webhook_id):
        response = self._make_signed_request('post', 'webhooks/{0}'.format(webhook_id))
        return response.json()

    @handleError
    def get_task_statuses(self, view_id):
        response = self._make_signed_request('get', 'workspaces/{0}/task-statuses'.format(view_id))
        return response.json().get('statuses')

    @handleError
    def add_data_to_dataset(self, ds_id, data, end_batch=False):
        """
        Add data to a dataset as a list of dictionaries.

        :param ds_id: The target dataset id
        :param data: a list of dictionaries. Each dictionary represents a row of data where key is the column internal name and value is the value of the cell.
        :param end_batch: If true , this would be considered an end of batch.
        :return: A processing response dictionary
        """
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             json={"rows": data, "endBatch": end_batch})
        return response.json()

    @handleError
    def add_data_to_dataset_as_csv(self, ds_id, file_path, has_header):
        """
        To add clean data to a dataset as a csv. Should contain a csv that has the same structure has the metadata.
        use this only if you are sure that all the rows of the right format. That is, each row should contain comma
        separated values in the same order as dataset metadata

        :param has_header: If the file has a header row.
        :param ds_id: the destination ds id
        :param file_path: the path of the file where you want to upload
        """
        header_string = 'true'
        if not has_header:
            header_string = 'false'
        files = {'file': open(file_path, 'rb')}
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             files=files, data={"has_header": header_string})
        return response.json()

    @handleError
    def upload_csv(self, file_path, target_datasource_id=None, replace=False, file_name=None,
                   ds_with_no_header=False):
        """
        To upload an arbitrary csv file to the system. The system would return a file id based on which one can track
        the progress of the file through the mammoth system.
        Args:
            file_path - The file path
            target_datasource_id - if this is set to a dataset id, the arbitrary csv would be appended to the
            data of the dataset.
            replace - mode for which the file should be appended
            file_name - file name for .xlsx, .xls, .zip
            ds_with_no_header - if the given file has header or not
        Return:
            ds - A ds object.
        """
        files = {'file': open(file_path, 'rb')}
        post_data = {}
        if target_datasource_id:
            post_data = {'append_to_ds_id': target_datasource_id}
            if replace:
                post_data['replace'] = "true"
        response = self._make_signed_request('post', '/files', files=files, data=post_data)
        log.info(response.json())
        file_id = response.json()['id']
        ds = self.wait_till_file_processing_get_ds(file_id, file_name, ds_with_no_header)
        ds_id = ds['id']
        if ds_with_no_header is False:
            self.wait_till_ds_ready(ds_id)
            views = self.list_views(ds_id)
            if len(views) > 0:
                view_ids = [view['id'] for view in views]
                workspace_id = max(view_ids)
                self.wait_for_view_to_finish_processing(workspace_id)
            else:
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    if retry_count != 0:
                        time.sleep(RETRY_DELAY_IN_SEC)
                    views = self.list_views(ds_id)
                    if len(views) > 0:
                        view_ids = [view['id'] for view in views]
                        workspace_id = max(view_ids)
                        self.wait_for_view_to_finish_processing(workspace_id)
                        break
                    retry_count += 1
        return ds

    @handleError
    def append_datasets(self, source_dataset_id, target_dataset_id, column_mapping, change_map=None,
                        new_ds_params=None, replace=False):
        """
        Method to combine two datasets While appending datasets, target ds gets combined and new rows gets added.At
        this point, ds updated_at will change. Thereafter, the pipeline re-run happens in all workspaces and
        updated_at gets modified for all the workspace once after pipeline re-run. Therefore, we need wait till
        all workspaces updated_at gets changed. -
        1. Loop until updated_at not greater than last_updated_at. Once updated_at is greater than
        last_updated_at break the loop and return the response
        2. Try until retry_count is less than 50, to avoid stuck issue in worse case
        """
        wksp_data = []
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        params = {
            "source": "datasource",
            "source_id": source_dataset_id,
            "mapping": column_mapping,
            "replace": replace
        }
        if change_map:
            params.update({"change_map": change_map})
        if new_ds_params:
            params.update({"new_ds_params": new_ds_params})

        # List all workspaces of target dataset
        wksps = self.list_views(target_dataset_id)
        for wksp in wksps:
            view_id = int(wksp["id"])
            res = self.get_view_details(view_id)
            last_updated_at = res['updated_at']
            # store all workspace id and last_data_updated_at time into a dictionary
            wksp_data.append({'view_id': view_id, 'last_updated_at': last_updated_at})

        # append dataset
        response = self._make_signed_request('post', '/datasets/{0}/batches'.format(target_dataset_id), json=params)
        if response.json()['STATUS'] == 'SUCCESS':
            self.sync_now(target_dataset_id)
            time.sleep(5)
            for view_details in wksp_data:
                view_id = view_details['view_id']
                last_updated_at = view_details['last_updated_at']
                res = self.get_view_details(view_id)
                updated_at = res['updated_at']

                # convert string to datetime
                last_updated_at = datetime.strptime(last_updated_at, date_format)
                updated_at = datetime.strptime(updated_at, date_format)
                retry_count = 0

                while not (updated_at > last_updated_at) and retry_count < MAX_RETRIES:
                    # iterate until data_updated_at is not greater than last_data_updated_at
                    retry_count += 1
                    time.sleep(5)
                    res = self.get_view_details(view_id)
                    updated_at = res['updated_at']
                    updated_at = datetime.strptime(updated_at, date_format)

                if retry_count == MAX_RETRIES:
                    raise RuntimeError(f"Max retry limit reached to combine datasets.")

            self.sync_now(target_dataset_id)
            time.sleep(15)
            r = self._make_signed_request('get', '/datasets/{0}/batches'.format(target_dataset_id))
            future_id = r.json().get('future_id')
            future_response = self.track_future_id(future_id)
            self.wait_till_ds_ready(target_dataset_id)
            return future_response

    def wait_till_file_processing_get_ds(self, file_id, file_name=None, ds_with_no_header=False):
        """
        Method will wait till the file with given id has finished processing.
        Works for csv,txt,tsv files right now.
        Also if we pass file_name to the method it works fine for .xslx, .xls
        TODO: Write logic to support .zip file.
        :param file_id:
        :return: A dataset dictionary
        """
        retry_count = 0
        while retry_count < MAX_RETRIES * 4:
            response = self._make_signed_request('get', '/files/{0}'.format(file_id))
            file_info = response.json()['file']
            status = file_info['status']
            if status != 'processing':
                log.info(file_info)
                break
            else:
                time.sleep(RETRY_DELAY_IN_SEC)
            retry_count += 1
        if retry_count == MAX_RETRIES * 4:
            raise RuntimeError(f"Max time limit reached to get processed file .")
        response = self._make_signed_request('get', '/files/{0}'.format(file_id))
        file_info = response.json()['file']
        final_ds_id = file_info["additional_data"].get("final_ds_id")
        append_to_ds_id = file_info["additional_data"].get("append_to_ds_id")
        if final_ds_id is None and file_name is None:
            raise UnknownError(f"File name required for .xls, .xlsx, .zip file extensions.")
        # wait till the file reflects in resources to get dataset id by filtering resources
        time.sleep(5)
        if final_ds_id is None and file_name is not None:
            resources = self.list_resources()
            resources = list(filter(lambda x: x['resource_type'] == "datasource", resources))
            for i in resources:
                data = i['object_properties']['name']
                if data == file_name:
                    ds_id = i['object_properties']['id']
                    final_ds_id = ds_id
        try:
            self._wait_for_ds_status(final_ds_id, 'processing', check_for_status_equality=False)
        except UnknownError as e:
            # in case there is a append to ds id, final ds may get deleted before status check
            log.error(e)
        if append_to_ds_id and ds_with_no_header is False:
            self._wait_for_ds_status(append_to_ds_id, 'ready')
            ds = self.get_dataset(append_to_ds_id)
        else:
            ds = self.get_dataset(final_ds_id)
        return ds

    @handleError
    def _wait_for_ds_status(self, ds_id, status, check_for_status_equality=True):
        retry_count = 0
        while ds_id and retry_count < MAX_RETRIES * 4:
            ds = self.get_dataset(ds_id)
            ds_status = ds['status']
            if check_for_status_equality:
                if ds_status == status:
                    break
                else:
                    time.sleep(RETRY_DELAY_IN_SEC)
            else:
                if ds_status != status:
                    break
                else:
                    time.sleep(RETRY_DELAY_IN_SEC)
            retry_count += 1
        if retry_count == MAX_RETRIES * 4:
            raise RuntimeError(f"Max time limit reached in _wait_for_ds_status")

    @handleError
    def sync_now(self, ds_id):
        r = self._make_signed_request('post', '/datasets/{}/apply-data'.format(ds_id))
        log.debug("The response of sync now i.e apply data is {}".format(r.json()))
        return r.json()

    @handleError
    def get_ds_for_file(self, file_id):
        """
        Will return the dataset for the given file.
        :param file_id: The file id
        :return: A ds information dictionary
        """
        datasets = self.list_datasets()
        for i in range(len(datasets)):
            ds = datasets[len(datasets) - 1 - i]
            if 'source_id' in list(ds.keys()):
                if ds['source_id'] == file_id and ds['source_type'] == 'file':
                    return ds

    @handleError
    def list_views(self, ds_id):
        """
        Returns a list of views a dataset has
        :param ds_id: Dataset ID
        :return: list of workspace dictionaries
        """
        response = self._make_signed_request('get', '/datasets/{0}/workspaces'.format(ds_id))
        return response.json()['workspaces']

    @handleError
    def create_view(self, ds_id, duplicate_from_view_id=None):
        """
        Returns a workspace_id of the dataset
        :param ds_id: Dataset ID
        :param duplicate_from_view_id: duplicate existing view
        :return: workspace_id
        """
        try:
            params = {}
            if duplicate_from_view_id:
                params = {'clone_config_from': duplicate_from_view_id}
            response = self._make_signed_request('post', '/datasets/{0}/workspaces'.format(ds_id), json=params)

            # View duplication takes a while to reflect the data
            if 'workspace_id' not in response.json():
                time.sleep(10)
                views = self.list_views(ds_id)
                view_ids = [view['id'] for view in views]
                workspace_id = max(view_ids)
                self.wait_for_view_to_finish_processing(workspace_id)
            else:
                workspace_id = response.json()['workspace_id']
        except Exception as e:
            raise e
        return workspace_id

    @handleError
    def delete_view(self, view_id, wait_till_ready=True):
        """
        Safe deletes a workspace
        :param ds_id: Workspace id
        :return: response
        """
        params = {}
        r = self._make_signed_request('post', '/workspaces/{}/safe-delete-request'.format(view_id), json=params)
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def reset_view(self, view_id, wait_till_ready=True):
        """
        Make API call to reset the view - Resetting the View will remove all Transformations, Elements and Filters
        :param view_id: workspace_id
        :return: response
        """
        r = self._make_signed_request('post', '/workspaces/{0}/reset'.format(view_id), json={})
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def rerun_pipeline(self, view_id, force_run_pipeline=False):
        params = {'force_run': force_run_pipeline}
        response = self._make_signed_request('post', '/workspaces/{}/rerun'.format(view_id), json=params)
        return response.json()

    def reorder_tasks(self, view_id, param, wait_till_ready=True):
        r = self._make_signed_request('patch', '/workspaces/{0}/tasks'.format(view_id),
                                      json={"patch": [{"op": "replace", "path": "tasks", "value": param}]})
        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def get_view_data(self, view_id, columns=None, condition=None, limit=None, offset=None):
        """
        Makes api call to get view data which creates a future request
        Then calls future request tracker method to get future requets's response
        Finally returns the data of the wksp as per params passed
        """
        paging_params = {
            'columns': columns,
            'condition': condition,
            'limit': limit,
            'offset': offset
        }

        response = self._make_signed_request('post', 'workspaces/{workspace_id}/data'.format(workspace_id=view_id),
                                             json=paging_params)
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        log.debug("The future response is {}".format(future_response))
        return future_response['data']

    @handleError
    def run_transform(self, view_id, param):
        r = self._make_signed_request('post', '/workspaces/{0}/tasks'.format(view_id), json={'param': param})
        return r.json()

    @handleError
    def get_view_details(self, view_id):
        r = self._make_signed_request('get', '/workspaces/{0}'.format(view_id))
        future_id = r.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def set_view_properties(self, view_id, properties):
        r = self._make_signed_request('post', '/workspaces/{0}'.format(view_id), json=properties)
        future_id = r.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def wait_for_view_to_finish_processing(self, view_id):
        retry_count = 0
        while retry_count < MAX_RETRIES * 2:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            view = self.get_view_details(view_id)
            if view['status'] != 'processing':
                break
            retry_count += 1
        if retry_count == MAX_RETRIES * 2:
            raise RuntimeError(f"Max retry limit reached to get view in ready state")

    @handleError
    def wait_till_view_is_ready(self, view_id):
        retry_count = 0
        while retry_count < MAX_RETRIES * 2:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            view = self.get_view_details(view_id)
            if view['status'] == 'ready':
                break
            retry_count += 1
        if retry_count == MAX_RETRIES * 2:
            raise RuntimeError(f"Max retry limit reached to get view in ready state")

    @handleError
    def copy_template_from_view(self, ds_id, view_id):
        """
        use this method to copy template from another view and apply to the dataset's view. If the dataset has an
        empty view, it will be reused. Else, a new view will get created.

        :param ds_id: The dataset id
        :param view_id: The view ID from which you want to copy the template from.
        :return: Nothing
        """
        self._make_signed_request('post',
                                  '/datasets/{0}/workspaces'.format(ds_id),
                                  json={'clone_config_from': view_id})

    @handleError
    def add_action(self, view_id, param, wait_till_ready=False):
        """
        Adds an action.
        :param view_id: The view on which the action is to be performed
        :param param: The param for the action.
        :return: Request Id for the action
        """
        r = self._make_signed_request('post', '/workspaces/{0}/actions'.format(view_id), json={'param': param})
        response = r.json()['request_id']
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response)
        return response

    @handleError
    def run_action(self, view_id, action_id, param, wait_till_ready=False):
        """
        Runs an action.
        :param view_id: The view on which the action is to be performed
        :param action_id:The param to get applied action id
        :param param: The param for the action.
        :return: Request Id for the action
        """
        r = self._make_signed_request('post', '/workspaces/{0}/actions/{1}'.format(view_id, action_id),
                                      json={'param': param})
        response = r.json()['request_id']
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, r.json()['request_id'])
        return response

    @handleError
    def edit_action(self, view_id, action_id, param, wait_till_ready=False):
        """
        edit an action.
        :param wait_till_ready:
        :param view_id: The view on which the action is to be performed
        :param action_id:The param to get applied action id
        :param param: The param for the action.
        :return: Request Id for the action
        """

        r = self._make_signed_request('patch', '/workspaces/{0}/actions/{1}'.format(view_id, action_id),
                                      json={"patch": [{"op": "replace", "path": "params", "value": param}]})
        response = r.json()['request_id']
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, r.json()['request_id'])
        return response

    def _wait_till_request_is_complete_get_data(self, view_id, request_id):
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            r = self._make_signed_request('get', '/workspaces/{0}/requests/{1}'.format(view_id, request_id))
            data = r.json()
            log.debug("data in _wait_till_request_is_complete_get_data {}".format(data))
            if data['status'] in ['success', 'failure', 'referror', 'error']:
                return data
            retry_count += 1
        raise RuntimeError(f"Max retry limit reached to get workspace out of processing .")

    @handleError
    def list_actions(self, view_id):
        response = self._make_signed_request('get', '/workspaces/{0}/actions'.format(view_id))
        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        log.debug("List actions : {0}".format(response))
        return future_response['triggers']

    @handleError
    def delete_action(self, view_id, action_id):
        """
        Deletes action by action id
        :param view_id:
        :param param
        :param action_id:
        :param wait_till_ready:
        :return:
        """
        r = self._make_signed_request('delete', '/workspaces/{0}/actions/{1}'.format(view_id, action_id))
        return r.json()

    @handleError
    def push_view_data_to_mysql(self, view_id, host, username, password, port, database, target_table=None):
        action_param = {
            'run_immediately': True,
            # 'validate_only': True,
            'target_properties': {
                'username': username,
                'password': password,
                'database': database,
                'host': host,
                'table': target_table,
                'port': port
            },
            'trigger_type': 'none',
            'additional_properties': {},
            'handler_type': 'mysql'
        }
        request_id = self.add_action(view_id, action_param)
        self._wait_till_request_is_complete_get_data(view_id, request_id)

    @handleError
    def download_view_as_csv(self, view_id, file_prefix=None, condition=None):
        if not isinstance(file_prefix, str):
            file_prefix = 'file_{0}'.format(random.randint(1000, 2000))

        action_param = {
            "handler_type": "s3",
            "trigger_type": "none",
            "run_immediately": True,
            "sequence": None,
            "additional_properties": {},
            "WORKSPACE_ID": view_id,
            "target_properties": {
                "file": file_prefix,
                "use_format": True,
                "include_hidden": False
            }
        }
        action_response = self.add_action(view_id, action_param, wait_till_ready=True)
        log.debug("The response of download_view_as_csv is {}".format(action_response))
        notifications = self.list_notifications()
        for n in notifications:
            url = pydash.get(n, 'details.data.additional_data.url')
            if isinstance(url, str):
                if file_prefix in url:
                    return url

    @handleError
    def list_notifications(self):
        r = self._make_signed_request('get', '/resources')
        data = r.json()
        return data['notifications']['items']

    @handleError
    def _get_async_request_data(self, request_id):
        url = '/async/{0}'.format(request_id)
        r = self._make_signed_request('get', url)
        return r.json()

    @handleError
    def add_third_party_identity(self, integration_key, identity_config):
        integration_key = encode_integration_key(integration_key)
        url = '/integrations/{0}/identities'.format(integration_key)
        r = self._make_signed_request('post', url, json=identity_config)
        request_id = r.json()['request_id']
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            data = self._get_async_request_data(request_id)
            if data['STATUS'] == 'SUCCESS':
                return data['response']['identity_key']
            elif data['STATUS'] == 'PROCESSING':
                retry_count += 1
                continue
            else:
                raise AuthError(data['message'])

        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max retry limit reached to get third party identity created.")

    @handleError
    def get_third_party_identity_key_by_name(self, integration_key, name):
        integration_key = encode_integration_key(integration_key)
        url = "/integrations/{0}/identities".format(integration_key)
        r = self._make_signed_request('get', url)
        data = r.json()
        for identity in data['identities']:
            if identity['name'] == name:
                return identity['value']

    @handleError
    def get_third_party_identities(self, integration_key):
        integration_key = encode_integration_key(integration_key)
        url = "/integrations/{0}/identities".format(integration_key)
        r = self._make_signed_request('get', url)
        data = r.json()
        return data['identities']

    @handleError
    def validate_third_party_ds_config(self, integration_key, identity_key, ds_config):
        integration_key = encode_integration_key(integration_key)
        url = '/integrations/{0}/identities/{1}/dsConfigs'.format(integration_key, identity_key)
        r = self._make_signed_request('post', url, json=ds_config)
        data = r.json()
        # return data['is_valid']
        return data

    @handleError
    def create_third_party_dataset(self, ds_param, wait_till_ready=False):
        url = '/datasets'
        r = self._make_signed_request('post', url, json=ds_param)
        data = r.json()
        # if the response json(data) contains datasource_id it returns ds_id otherwise returns none(only in case of file type dataset creation such as sftp, google drive, dropbox)
        ds_id = data.get('datasource_id')
        if wait_till_ready:
            if ds_id is not None:
                self.wait_till_ds_ready(ds_id)
        return ds_id

    def wait_till_ds_ready(self, ds_id):
        retry_count = 0
        while retry_count < MAX_RETRIES * 4:
            datasets = self.list_datasets()
            ds_ready = False
            for i in range(len(datasets)):
                ds = datasets[len(datasets) - 1 - i]
                log.debug(ds)
                if ds['id'] == ds_id:
                    if ds['status'] == 'processing':
                        time.sleep(RETRY_DELAY_IN_SEC)
                        continue
                    if ds['status'] in ['ready', 'error']:
                        time.sleep(RETRY_DELAY_IN_SEC)
                        ds_ready = True
                        break
                    log.debug(ds['status'])
            if ds_ready:
                break
            retry_count += 1
        if retry_count == MAX_RETRIES * 4:
            raise RuntimeError(f"Max time limit reached to get ds ready.")

    @handleError
    def apply_template_to_view(self, view_id, template_config, wait_till_ready=False):
        url = '/workspaces/{0}/exportable-config'.format(view_id)
        r = self._make_signed_request('post', url, json={"config": template_config})
        data = r.json()

        if wait_till_ready:
            self.wait_till_view_is_ready(view_id)
        return data['STATUS'] == 'PROCESSING'

    @handleError
    def track_future_id(self, future_id):
        """
        Future request tracker that send GET request to Future API
        and returns response as JSON object when status is not in
        processing (i.e. SUCCESS/FAILED)
        """
        if not isinstance(future_id, int):
            raise RuntimeError(f"Future id should be a numeric value")

        response = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            resource_resp = self._make_signed_request('get', f'/future/{future_id}')
            resource_resp_json = resource_resp.json()
            future_object = resource_resp_json['future']
            if future_object['status'] != 'processing':
                response = future_object['response']
                break
            retry_count += 1

        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to future request response.")
        return response

    @handleError
    def add_explore_card(self, view_id, params):
        """
        Method to add explore card
        Make post request to derivatives api, fetch derivative id,
        Make get request to derivative api, fetch data of the derivative
        :param view_id:
        :type view_id:
        :param params:
        :type params:
        :return:
        :rtype:
        """
        response = self._make_signed_request('post', '/workspaces/{0}/derivatives'.format(view_id), json=params)
        add_derivative_response = response.json()
        log.debug("The add_derivative response id {}".format(add_derivative_response))
        if add_derivative_response['STATUS'] == 'FAILURE':
            return add_derivative_response
        derivative_id = add_derivative_response['id']
        query_response = {'STATUS': 'PROCESSING'}
        retry_count = 0
        data_response = query_response
        while data_response['STATUS'] != 'READY' and retry_count < MAX_RETRIES:
            response = self._make_signed_request('post', f'/workspaces/{view_id}/derivatives/{derivative_id}', json={})
            data_response = response.json()
            log.debug("Data response is {}".format(data_response))
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            retry_count += 1
        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to read query data.")

        return data_response

    @handleError
    def add_batch_columns(self, ds_id, param, wait_till_ready=True, ds_column_count=None):
        """
        Method to add batch columns to the Dataset
        :param ds_id:
        :param param - List of batch column/s to be added to the dataset
        :param ds_column_count - expected column count for ds after batch column edition
        """
        res = self._make_signed_request('patch', f'/datasets/{ds_id}',
                                             json={"patch": [{"op": "replace", "path": "batch_columns",
                                                              "value": {"add_columns": param, "remove_columns": []}}]})
        response = res.json()
        if wait_till_ready:
            future_id = response.get('future_id')
            self.track_future_id(future_id)
            self.wait_till_ds_ready(ds_id)
            if ds_column_count is not None:
                self.wait_till_batch_columns_are_updated_in_ds(ds_id, ds_column_count=ds_column_count)
        return response

    @handleError
    def get_batch_column_keys(self, ds_id):
        """
        Method to get batch columns of the dataset
        :param ds_id:
        :return - List of batch column/s keys
        """
        batch_column_keys = []
        metadata = self.get_dataset(ds_id)['meta_data']
        for value in metadata:
            if value['internal_name'] in RESERVED_BATCH_COLUMN_INTERNAL_NAMES_AND_KEYS.keys():
                batch_col_key = RESERVED_BATCH_COLUMN_INTERNAL_NAMES_AND_KEYS[value['internal_name']]
                batch_column_keys.append(batch_col_key)

        return batch_column_keys

    @handleError
    def remove_batch_columns(self, ds_id, rem_cols, wait_till_ready=True, ds_column_count=None):
        """
        Method to remove batch columns from the Dataset
        :param ds_id:
        :param rem_cols - List of batch column/s (keys) to be removed from the dataset
        :param ds_column_count - expected column count for ds after batch column deletion
        """
        # Get batch columns of the dataset
        batch_column_keys = self.get_batch_column_keys(ds_id)
        add_cols = list(set(batch_column_keys) - set(rem_cols))

        res = self._make_signed_request('patch', '/datasets/{0}'.format(ds_id),
                                             json={"patch": [{"op": "replace", "path": "batch_columns",
                                                              "value": {"add_columns": add_cols,
                                                                        "remove_columns": rem_cols}}]})
        response = res.json()
        if wait_till_ready:
            future_id = response.get('future_id')
            self.track_future_id(future_id)
            self.wait_till_ds_ready(ds_id)
            if ds_column_count is not None:
                self.wait_till_batch_columns_are_updated_in_ds(ds_id, ds_column_count=ds_column_count)
        return response

    @handleError
    def add_publish(self, view_id, params, wait_till_ready=True):
        r = self._make_signed_request('post', '/workspaces/{0}/publish'.format(view_id), json={'param': params})

        response = r.json()
        if wait_till_ready:
            response = self._wait_till_request_is_complete_get_data(view_id, response['request_id'])
        return response

    @handleError
    def delete_publish(self, view_id, publish_trigger_id):
        response = self._make_signed_request('delete', f'/workspaces/{view_id}/publish/{publish_trigger_id}')

        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def regenerate_publish_password(self, view_id, publish_odbc_type):
        param = {
            "patch": [{
                "op": "replace", "path": "reset_password",
                "value": {
                    "odbc_type": publish_odbc_type
                }
            }]
        }
        response = self._make_signed_request('patch', \
                                             f'/workspaces/{view_id}/publish', \
                                             json=param)

        future_id = response.json()['future_id']
        future_response = self.track_future_id(future_id)
        return future_response['password']

    @handleError
    def get_publish_credentials(self, odbc_type):
        response = self._make_signed_request('get', f'/publish_credentials?odbc_type={odbc_type}')
        return response.json()

    @handleError
    def create_folder(self, params):
        """
        Method to create folder
        :param params - params for the create folder
        """
        r = self._make_signed_request('post', '/labels', json=params)
        response = r.json()
        return response

    @handleError
    def move_file_to_folder(self, destination_folder_id, params, wait_till_ready=True):
        """
        Method to move files from one folder to another
        :param destination_folder_id - id of the folder to which files are moving
        :param params - params which contains files to be moved
        """
        response = self._make_signed_request('post', '/labels/{0}/resources'.format(destination_folder_id), json=params)
        future_id = response.json()['future_id']
        if wait_till_ready:
            future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def list_folders(self):
        """
        Method to list all the folders
        """
        response = self._make_signed_request('get', '/labels')
        return response.json().get('labels')

    @handleError
    def delete_folder(self, folder_id):
        """
        Method to delete folder
        :param folder_id - id of the folder to be deleted
        """
        r = self._make_signed_request('delete', '/labels/{0}'.format(folder_id))
        response = r.json()
        return response

    @handleError
    def list_resources(self):
        """
        Method to list all the resources
        """
        response = self._make_signed_request('get', '/resources')
        data = response.json()
        return data['resources']

    @handleError
    def rename_dataset(self, ds_id, dataset_name):
        """
        method to rename dataset
        :param
            ds_id: dataset id
            dataset_name: dataset name to be changed
        """
        res = self._make_signed_request('patch', '/datasets/{0}'.format(ds_id),
                                        json={"patch": [{"op": "replace", "path": "name",
                                                         "value": dataset_name}]})
        response = res.json()
        return response

    @handleError
    def rename_view(self, wksp_id, wksp_name):
        """
        method to rename view
        :param
            wksp_id: workspace id
            wksp_name: dataset name to be changed
        """
        res = self._make_signed_request('patch', '/workspaces/{0}'.format(wksp_id),
                                           json={"patch": [{"op": "replace", "path": "name",
                                                            "value": wksp_name}]})
        response = res.json()
        return response

    @handleError
    def apply_template(self, view_id, params):
        """
        method to apply template to the view
        :param
            view_id: workspace id
            params: pipeline to be added
        """
        res = self._make_signed_request('post', 'workspaces/{0}/exportable-config'.format(view_id),
                                        json={'config': params})
        response = res.json()
        return response

    @handleError
    def suspend_action(self, view_id, action_id):
        """
        method to suspend action
        :param
            view_id: workspace id
            action_id: action id
        """
        r = self._make_signed_request('patch', '/workspaces/{0}/actions/{1}'.format(view_id, action_id),
                                      json={"patch": [{"op": "replace", "path": "updateState", "value": "suspend"}]})
        response = r.json()
        return response

    @handleError
    def restore_action(self, view_id, action_id):
        """
        method to restore action
        :param
            view_id: workspace id
            action_id: action id
        """
        r = self._make_signed_request('patch', '/workspaces/{0}/actions/{1}'.format(view_id, action_id),
                                      json={"patch": [{"op": "replace", "path": "updateState", "value": "active"}]})
        response = r.json()
        return response

    @handleError
    def enable_sample_mode(self, view_id, wait_till_ready=True):
        """
        method to enable sample mode
        :param
            view_id: workspace id
        """
        response = self._make_signed_request('post', '/workspaces/{0}/preview-mode'.format(view_id),
                                             json={"limit": 10000})
        future_id = response.json()['future_id']
        if wait_till_ready:
            future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def disable_sample_mode(self, view_id, wait_till_ready=True):
        """
        method to disable sample mode
        :param
            view_id: workspace id
        """
        response = self._make_signed_request('delete', '/workspaces/{0}/preview-mode'.format(view_id))
        future_id = response.json()['future_id']
        if wait_till_ready:
            future_response = self.track_future_id(future_id)
        return future_response

    @handleError
    def fix_schema_header(self, ds_id, params, wait_till_ready=True):
        """
        method to fix the uploaded file which needs user input (ex: csv file does not have header)
        :param
            ds_id: datasest id,
            params: input params for the file to process
        """
        res = self._make_signed_request('post', '/datasets/{ds_id}/csvfile'.format(ds_id=ds_id), json=params)
        response = res.json()
        request_id = response.get('request_id')
        if wait_till_ready:
            response = self.track_async_request_id(request_id)
        return response

    @handleError
    def track_async_request_id(self, request_id):
        """
        Async request tracker that send GET request to Async API
        and returns response as JSON object when status is not in
        processing (i.e. SUCCESS/FAILED)
        """
        if not isinstance(request_id, int):
            raise RuntimeError(f"Request id should be a numeric value")

        response = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            resp_json = self._get_async_request_data(request_id)
            if resp_json['STATUS'] != 'PROCESSING':
                response = resp_json
                break
            retry_count += 1

        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to future request response.")
        return response

    @handleError
    def wait_till_batch_is_updated(self, ds_id, batch_count):
        """
        Method to wait until the batch is updated
        Args:
            ds_id: datasest id
            batch_count: expected task count
        Return:
            batch_details: updated batch details
        """
        batch_details = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            batches = self.list_batches(ds_id)
            if len(batches) == batch_count:
                batch_details = batches
                break
            retry_count += 1
        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to update batch details.")
        return batch_details

    @handleError
    def wait_till_task_details_updated(self, view_id, task_count):
        """
        Method to wait until the task details updated
        Args:
            view_id: workspace id
            task_count: expected task count
        Return:
            task_details: updated task details
        """
        task_details = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            tasks = self.get_task(view_id)
            if len(tasks) == task_count:
                task_details = tasks
                break
            retry_count += 1
        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to update task details.")
        return task_details

    @handleError
    def wait_till_pipeline_status_is_updated(self, view_id, status):
        """
        Method to wait until the pipeline status changes
        Args:
            view_id: workspace id
            status: expected status
        Return:
            pipeline_status: status of the pipeline
        """
        pipeline_status = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            view_details = self.get_view_details(view_id)
            if view_details['pipeline_status'] == status:
                pipeline_status = view_details['pipeline_status']
                break
            retry_count += 1
        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to update pipeline status.")
        return pipeline_status

    @handleError
    def wait_till_batch_columns_are_updated_in_ds(self, ds_id, ds_column_count):
        """
        Method to wait until the pipeline status changes
        Args:
            ds_id: dataset id
            ds_column_count: expected column count for dataset
        Return:
            dataset_details: dataset details
        """
        dataset_details = None
        retry_count = 0
        while retry_count < MAX_RETRIES:
            if retry_count != 0:
                time.sleep(RETRY_DELAY_IN_SEC)
            ds_details = self.get_dataset(ds_id)
            if ds_details['column_count'] == ds_column_count:
                dataset_details = ds_details
                break
            retry_count += 1
        if retry_count == MAX_RETRIES:
            raise RuntimeError(f"Max limit reached to add/edit batch columns.")
        return dataset_details
