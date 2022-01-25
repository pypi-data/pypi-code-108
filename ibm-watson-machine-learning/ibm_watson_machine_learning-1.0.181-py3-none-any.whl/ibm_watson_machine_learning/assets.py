#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import print_function
import ibm_watson_machine_learning._wrappers.requests as requests

from ibm_watson_machine_learning.messages.messages import Messages
from ibm_watson_machine_learning.utils import SPACES_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, MEMBER_DETAILS_TYPE,DATA_ASSETS_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from ibm_watson_machine_learning.metanames import AssetsMetaNames
from ibm_watson_machine_learning.wml_resource import WMLResource
from ibm_watson_machine_learning.wml_client_error import WMLClientError, ApiRequestFailure
import os

_DEFAULT_LIST_LENGTH = 50


class Assets(WMLResource):
    """
    Store and manage your data assets.
    """
    ConfigurationMetaNames = AssetsMetaNames()
    """MetaNames for Data Assets creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, asset_uid=None):
        """
            Get data asset details. If no asset_uid is passed, details for all assets will be returned.

            **Parameters**

            .. important::
                **returns**: Unique id  of asset\n
                **return type**: str

            **Output**

            .. important::
                #. **asset_details**:  Metadata of the stored data asset\n
                   **type**: dict\n

            **Example**

             >>> asset_details = client.data_assets.get_details(asset_uid)
        """
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, False)

        if asset_uid:
            response = requests.get(self._client.service_instance._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
                                    headers=self._client._get_headers())

            return self._get_required_element_from_response(self._handle_response(200, u'get asset details', response))

        else:
            href = self._client.service_instance._href_definitions.get_search_asset_href()

            data = {
                "query": "*:*"
            }

            response = requests.post(href,
                                    json=data,
                                    params=self._client._params(),
                                    headers=self._client._get_headers())

            return {'resources': [
                self._get_required_element_from_response(x)
                for x in self._handle_response(200, u'get assets details', response)['results']]}

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def create(self, name, file_path):
        """
                Creates a data asset and uploads content to it.

                **Parameters**

                .. important::
                   #. **name**:  Name to be given to the data asset\n

                      **type**: str\n

                   #. **file_path**:  Path to the content file to be uploaded\n

                      **type**: str\n

                **Output**

                .. important::

                    **returns**: metadata of the stored data asset\n
                    **return type**: dict\n

                **Example**

                 >>> asset_details = client.data_assets.create(name="sample_asset",file_path="/path/to/file")
        """
        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        WMLResource._chk_and_block_create_update_for_python36(self)
        Assets._validate_type(name, u'name', str, True)
        Assets._validate_type(file_path, u'file_path', str, True)
        return self._create_asset(name, file_path)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, meta_props):
        """
                Creates a data asset and uploads content to it.

                **Parameters**

                .. important::
                   #. **meta_props**:  meta data of the space configuration. To see available meta names use:\n
                                    >>> client.data_assets.ConfigurationMetaNames.get()

                      **type**: dict\n

                **Example**
                    Example for data asset creation for files :

                            >>> metadata = {
                            >>>  client.data_assets.ConfigurationMetaNames.NAME: 'my data assets',
                            >>>  client.data_assets.ConfigurationMetaNames.DESCRIPTION: 'sample description',
                            >>>  client.data_assets.ConfigurationMetaNames.DATA_CONTENT_NAME: 'sample.csv'
                            >>> }
                            >>> asset_details = client.data_assets.store(meta_props=metadata)

                    Example of data asset creation using connection:

                            >>> metadata = {
                            >>>  client.data_assets.ConfigurationMetaNames.NAME: 'my data assets',
                            >>>  client.data_assets.ConfigurationMetaNames.DESCRIPTION: 'sample description',
                            >>>  client.data_assets.ConfigurationMetaNames.CONNECTION_ID: '39eaa1ee-9aa4-4651-b8fe-95d3ddae',
                            >>>  client.data_assets.ConfigurationMetaNames.DATA_CONTENT_NAME: 't1/sample.csv'
                            >>> }
                            >>> asset_details = client.data_assets.store(meta_props=metadata)

                    Example for data asset creation with database sources type connection:

                            >>> metadata = {
                            >>>  client.data_assets.ConfigurationMetaNames.NAME: 'my data assets',
                            >>>  client.data_assets.ConfigurationMetaNames.DESCRIPTION: 'sample description',
                            >>>  client.data_assets.ConfigurationMetaNames.CONNECTION_ID: '23eaf1ee-96a4-4651-b8fe-95d3dadfe',
                            >>>  client.data_assets.ConfigurationMetaNames.DATA_CONTENT_NAME: 't1'
                            >>> }
                            >>> asset_details = client.data_assets.store(meta_props=metadata)
        """
        ##For CP4D, check if either spce or project ID is set
        WMLResource._chk_and_block_create_update_for_python36(self)
        self._client._check_if_either_is_set()

        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        Assets._validate_type(meta_props, u'meta_props', dict, True)

        name = meta_props[self.ConfigurationMetaNames.NAME]
        file_path = meta_props[self.ConfigurationMetaNames.DATA_CONTENT_NAME]
        connection_id = None
        description = ""
        if self.ConfigurationMetaNames.CONNECTION_ID in meta_props:
            connection_id = meta_props[self.ConfigurationMetaNames.CONNECTION_ID]

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            description = meta_props[self.ConfigurationMetaNames.DESCRIPTION]

        return self._create_asset(name, file_path, connection_id=connection_id, description=description)

    def _create_asset(self, name, file_path, connection_id=None, description=None):
        ##Step1: Create a data asset
        desc = description
        if desc is None:
            desc = ""
        try:
            import mimetypes
        except Exception as e:
            raise WMLClientError(Messages.get_message(message_id="module_mimetypes_not_found"), e)
        mime_type = mimetypes.MimeTypes().guess_type(file_path)[0]
        if mime_type is None:
            mime_type = "application/octet-stream"

        asset_meta = {
            "metadata": {
                "name": name,
                "description": desc,
                "asset_type": "data_asset",
                "origin_country": "us",
                "asset_category": "USER"
            },
            "entity": {
                "data_asset": {
                    "mime_type": mime_type
                }
            }
        }
        if connection_id is not None:
            asset_meta["metadata"].update({"tags": ["connected-data"]})

        #Step1  : Create an asset
        print(Messages.get_message(message_id="creating_data_asset"))

        if self._client.WSD:
            # For WSD the asset creation is done within _wsd_create_asset function using polyglot
            # Thus using the same for data_assets type
            input_payload = {
                    "name": name,
                    "mime_type": mime_type
                    }

            meta_props = {
                    "name": name
            }
            details = Assets._wsd_create_asset(self, "data_asset", input_payload, meta_props, file_path)
            return self._get_required_element_from_response(details)
        else:

            creation_response = requests.post(
                    self._client.service_instance._href_definitions.get_data_assets_href(),
                    headers=self._client._get_headers(),
                    params = self._client._params(),
                    json=asset_meta
            )


            asset_details = self._handle_response(201, u'creating new asset', creation_response)
            #Step2: Create attachment
            if creation_response.status_code == 201:
                asset_id = asset_details["metadata"]["asset_id"]
                attachment_name = file_path.split("/")[-1]
                attachment_meta = {
                        "asset_type": "data_asset",
                        "name": attachment_name,
                        "mime": mime_type
                    }
                if connection_id is not None:
                    attachment_meta.update({"connection_id": connection_id,
                                            "connection_path": file_path,
                                            "is_remote": True})

                attachment_response = requests.post(
                    self._client.service_instance._href_definitions.get_attachments_href(asset_id),
                    headers=self._client._get_headers(),
                    params=self._client._params(),
                    json=attachment_meta
                )
                attachment_details = self._handle_response(201, u'creating new attachment', attachment_response)
                if attachment_response.status_code == 201:
                    if connection_id is None:
                        attachment_id = attachment_details["attachment_id"]
                        attachment_url = attachment_details["url1"]
                        #Step3: Put content to attachment
                        with open(file_path, 'rb') as _file:
                            if not self._ICP:
                                    put_response = requests.put(
                                        attachment_url,
                                        data=_file
                                    )
                            else:
                                    put_response = requests.put(
                                        self._wml_credentials['url'] + attachment_url,
                                        files={'file': _file}
                                    )
                        if put_response.status_code == 201 or put_response.status_code == 200:
                            # Step4: Complete attachment
                            if not self._ICP:
                                complete_response = requests.post(
                                    # self._client.service_instance._href_definitions.get_attachment_href(asset_id,attachment_id)+"/complete",
                                    self._client.service_instance._href_definitions.get_attachment_complete_href(asset_id, attachment_id),
                                    headers=self._client._get_headers(),
                                    params = self._client._params()

                                )
                            else:
                                complete_response = requests.post(
                                    self._client.service_instance._href_definitions.get_attachment_href(asset_id,attachment_id)+"/complete",
                                    headers=self._client._get_headers(),
                                    params=self._client._params()
                                )
                            if complete_response.status_code == 200:
                                print(Messages.get_message(message_id="success"))
                                return self._get_required_element_from_response(asset_details)
                            else:
                                self._delete(asset_id)
                                raise WMLClientError(Messages.get_message(message_id="failed_while_creating_a_data_asset"))
                        else:
                            self._delete(asset_id)
                            raise WMLClientError(Messages.get_message(message_id="failed_while_creating_a_data_asset"))
                    else:
                        print(Messages.get_message(message_id="success"))
                        return self._get_required_element_from_response(asset_details)
                else:
                    self._delete(asset_id)
                    raise WMLClientError(Messages.get_message(message_id="failed_while_creating_a_data_asset"))
            else:
                raise WMLClientError(Messages.get_message(message_id="failed_while_creating_a_data_asset"))

    def list(self, limit=None):
        """
           List stored data assets. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all data assets in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.data_assets.list()
        """

        Assets._validate_type(limit, u'limit', int, False)
        href = self._client.service_instance._href_definitions.get_search_asset_href()

        data = {
                "query": "*:*"
        }
        if limit is not None:
            data.update({"limit": limit})

        response = requests.post(href, params=self._client._params(), headers=self._client._get_headers(),json=data)
        self._handle_response(200, u'list assets', response)
        asset_details = self._handle_response(200, u'list assets', response)["results"]
        space_values = [
            (m[u'metadata'][u'name'], m[u'metadata'][u'asset_type'], m[u'metadata'][u'size'], m["metadata"]["asset_id"]) for
            m in asset_details]

        self._list(space_values, [u'NAME', u'ASSET_TYPE', u'SIZE',u'ASSET_ID'], None, _DEFAULT_LIST_LENGTH)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, asset_uid, filename):
        """
            Download and store the content of a data asset.

            **Parameters**

            .. important::

                 #. **asset_uid**:  The Unique Id of the data asset to be downloaded\n
                    **type**: str\n

                 #. **filename**:  filename to be used for the downloaded file\n
                    **type**: str\n

            **Output**

            .. important::

                 **returns**: Normalized path to the downloaded asset content\n
                 **return type**: str\n

            **Example**

             >>> client.data_assets.download(asset_uid,"sample_asset.csv")
         """
        content = self.get_content(asset_uid)
        try:
            with open(filename, 'wb') as f:
                f.write(content)
            print(Messages.get_message(filename, message_id="successfully_saved_data_asset_content_to_file"))
            return os.path.abspath(filename)
        except IOError as e:
            raise WMLClientError(
                Messages.get_message(filename, message_id="saving_data_asset_to_local_file_failed"), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_content(self, asset_uid):
        """
            Download the content of a data asset.

            **Parameters**

            .. important::

                 #. **asset_uid**:  The Unique Id of the data asset to be downloaded\n
                    **type**: str\n

            **Output**

            .. important::

                 **returns**: the asset content\n
                 **return type**: binary\n

            **Example**

             >>> content = client.data_assets.get_content(asset_uid).decode('ascii')
        """
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)

        import urllib
        asset_response = requests.get(self._client.service_instance._href_definitions.get_data_asset_href(asset_uid),
                                      params=self._client._params(),
                                      headers=self._client._get_headers())
        asset_details = self._handle_response(200, u'get assets', asset_response)

        if self._WSD:
            attachment_url = asset_details['attachments'][0]['object_key']
            artifact_content_url = self._client.service_instance._href_definitions.get_wsd_model_attachment_href() + \
                                   urllib.parse.quote('data_asset/' + attachment_url, safe='')

            r = requests.get(artifact_content_url, params=self._client._params(), headers=self._client._get_headers(),
                             stream=True)
            if r.status_code != 200:
                raise ApiRequestFailure(Messages.get_message(message_id="failure_during_downloading_data_asset"), r)

            return r.content
        else:
            attachment_id = asset_details["attachments"][0]["id"]
            response = requests.get(self._client.service_instance._href_definitions.get_attachment_href(asset_uid,attachment_id),
                                    params=self._client._params(),
                                    headers=self._client._get_headers())
            if response.status_code == 200:
                if 'connection_id' in asset_details["attachments"][0] and \
                        asset_details["attachments"][0]['connection_id'] is not None:

                    conn_details = self._client.connections.get_details(asset_details["attachments"][0]['connection_id'])
                    attachment_data_source_type = conn_details['entity'].get('datasource_type')
                    cos_conn_data_source_id = self._client.connections.get_datasource_type_uid_by_name('cloudobjectstorage')
                    if attachment_data_source_type == cos_conn_data_source_id:
                        attachment_signed_url = response.json()["url"]
                        att_response = requests.get(attachment_signed_url)
                    else:
                        raise WMLClientError(Messages.get_message(message_id="download_api_not_supported_for_this_connection_type"))
                else:
                    attachment_signed_url = response.json()["url"]
                    if not self._ICP and not self._client.WSD:
                        if self._client.CLOUD_PLATFORM_SPACES:
                            att_response = requests.get(attachment_signed_url)
                        else:
                            att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url)
                    else:
                        att_response = requests.get(self._wml_credentials["url"]+attachment_signed_url)
                if att_response.status_code != 200:
                    raise ApiRequestFailure(Messages.get_message(message_id="failure_during_downloading_data_asset"), att_response)

                return att_response.content
            else:
                raise WMLClientError(Messages.get_message(message_id="failure_during_downloading_data_asset"))

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(asset_details):
        """
                Get Unique Id  of stored data asset. Deprecated!! Use get_id(details) instead

                **Parameters**

                .. important::

                   #. **asset_details**:  Metadata of the stored data asset\n
                      **type**: dict\n
                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: Unique Id of stored asset\n
                    **return type**: str\n

                **Example**


                 >>> asset_uid = client.data_assets.get_uid(asset_details)
        """
        Assets._validate_type(asset_details, u'asset_details', object, True)
        Assets._validate_type_of_details(asset_details, DATA_ASSETS_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(asset_details, u'data_assets_details',
                                                           [u'metadata', u'guid'])


    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_id(asset_details):
        """
                Get Unique Id of stored script asset.

                **Parameters**

                .. important::

                   #. **asset_details**:  Metadata of the stored script asset\n
                      **type**: dict\n
                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: Unique Id of stored data asset\n
                    **return type**: str\n

                **Example**

                     >>> asset_id = client.data_assets.get_id(asset_details)

        """

        return Assets.get_uid(asset_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(asset_details):
        """
            Get url of stored data asset.

           **Parameters**

           .. important::
                #. **asset_details**:  stored data asset details\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: href of stored data asset\n
                **return type**: str\n

           **Example**

             >>> asset_details = client.data_assets.get_details(asset_uid)
             >>> asset_href = client.data_assets.get_href(asset_details)
        """
        Assets._validate_type(asset_details, u'asset_details', object, True)
        Assets._validate_type_of_details(asset_details, DATA_ASSETS_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(asset_details, u'asset_details', [u'metadata', u'href'])


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, asset_uid):
        """
            Delete a stored data asset.

            **Parameters**

            .. important::
                #. **asset_uid**:  Unique Id of data asset\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.data_assets.delete(asset_uid)
        """
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)

        response = requests.delete(self._client.service_instance._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                headers=self._client._get_headers())
        if response.status_code == 200:
            return self._get_required_element_from_response(response.json())
        else:
            return self._handle_response(204, u'delete assets', response)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _delete(self, asset_uid):
        Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)

        response = requests.delete(self._client.service_instance._href_definitions.get_asset_href(asset_uid), params=self._client._params(),
                                   headers=self._client._get_headers())


        # if response.status_code == 200:
        #     return self._get_required_element_from_response(response.json())
        # else:
        #     return self._handle_response(204, u'delete assets', response)


    # @docstring_parameter({'str_type': STR_TYPE_NAME})
    # def get_href(self, asset_uid):
    #     """
    #        Get metadata of stored space(s). If space UID is not specified, it returns all the spaces metadata.
    #
    #        **Parameters**
    #
    #        .. important::
    #             #. **space_uid**: Space UID (optional)\n
    #                **type**: str\n
    #             #. **limit**:  limit number of fetched records (optional)\n
    #                **type**: int\n
    #
    #        **Output**
    #
    #        .. important::
    #             **returns**: metadata of stored space(s)\n
    #             **return type**: dict
    #             dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n
    #
    #        .. note::
    #             If UID is not specified, all spaces metadata is fetched\n
    #
    #        **Example**
    #
    #         >>> space_details = client.spaces.get_details(space_uid)
    #         >>> space_details = client.spaces.get_details()
    #     """
    #
    #
    #     Assets._validate_type(asset_uid, u'asset_uid', STR_TYPE, True)
    #
    #     if not self._ICP:
    #         response = requests.get(self._client.service_instance._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
    #                                 headers=self._client._get_headers())
    #     else:
    #         response = requests.get(self._client.service_instance._href_definitions.get_data_asset_href(asset_uid), params=self._client._params(),
    #                                 headers=self._client._get_headers())
    #     if response.status_code == 200:
    #         return response.json()["href"]
    #     else:
    #         return self._handle_response(200, u'spaces assets', response)

    def _get_required_element_from_response(self, response_data):

        WMLResource._validate_type(response_data, u'data assets response', dict)

        import copy
        new_el = {'metadata': copy.copy(response_data['metadata'])}

        try:
            new_el['metadata']['guid'] = response_data['metadata']['asset_id']
            new_el['metadata']['href'] = response_data['href'] if not (self._client.WSD and self._client.default_project_id) else self._client.service_instance._href_definitions.get_base_asset_href(response_data['metadata']['asset_id']) + "?" + "project_id=" + response_data['metadata']['project_id']

            new_el['metadata']['asset_type'] = response_data['metadata']['asset_type']
            new_el['metadata']['created_at'] = response_data['metadata']['created_at']
            new_el['metadata']['last_updated_at'] = response_data['metadata']['usage'].get('last_updated_at')

            if self._client.default_space_id is not None:
                new_el['metadata']['space_id'] = response_data['metadata']['space_id']

            elif self._client.default_project_id is not None:
                new_el['metadata']['project_id'] = response_data['metadata']['project_id']

            if 'entity' in response_data:
                new_el['entity'] = response_data['entity']

            if self._client.ICP_30 is not None or self._client.CLOUD_PLATFORM_SPACES or self._client.ICP_PLATFORM_SPACES:
                if "attachments" in response_data and response_data[u'attachments']:
                    new_el[u'metadata'].update({'attachment_id': response_data[u'attachments'][0][u'id']})
            if self._client.CLOUD_PLATFORM_SPACES or self._client.ICP_PLATFORM_SPACES:
                href_without_host = response_data['href'].split('.com')[-1]
                new_el[u'metadata'].update({'href':href_without_host})
            return new_el
        except Exception as e:
            raise WMLClientError(Messages.get_message(response_data, message_id="failed_to_read_response_from_down_stream_service"))
