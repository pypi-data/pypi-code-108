# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os

from azure.common import AzureHttpError
from azureml._common.exceptions import AzureMLException
from azureml._common._error_definition import AzureMLError
from azureml._common._core_user_error.user_error import AuthorizationStorageAccount
from six.moves.urllib import parse

module_logger = logging.getLogger(__name__)


def get_block_blob_service_credentials(sas_url):
    parsed_url = parse.urlparse(sas_url)

    sas_token = parsed_url.query

    # Split the netloc into 3 parts: acountname, "blob", endpoint_suffix
    # https://docs.microsoft.com/en-us/rest/api/storageservices/create-service-sas#service-sas-example
    account_name, _, endpoint_suffix = parsed_url.netloc.split(".", 2)

    path = parsed_url.path
    # Remove leading / to avoid awkward parse
    if path[0] == "/":
        path = path[1:]
    container_name, blob_name = path.split("/", 1)

    return sas_token, account_name, endpoint_suffix, container_name, blob_name


def upload_blob_from_stream(stream, url, content_type=None, session=None, timeout=None, backoff=None, retries=None):
    # TODO add support for upload without azure.storage
    from azureml._vendor.azure_storage.blob import BlockBlobService
    from azureml._vendor.azure_storage.blob.models import ContentSettings
    sas_token, account_name, endpoint_suffix, container_name, blob_name = get_block_blob_service_credentials(url)
    content_settings = ContentSettings(content_type=content_type)
    blob_service = BlockBlobService(account_name=account_name,
                                    sas_token=sas_token,
                                    request_session=session,
                                    endpoint_suffix=endpoint_suffix)

    reset_func = StreamResetFunction(stream.tell())

    # Seek to end of stream to validate uploaded blob size matches the local stream size
    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    reset_func(stream)

    try:
        from azureml._restclient.clientbase import execute_func_with_reset
        execute_func_with_reset(backoff,
                                retries,
                                blob_service.create_blob_from_stream,
                                reset_func,
                                container_name=container_name,
                                blob_name=blob_name,
                                stream=stream,
                                content_settings=content_settings,
                                timeout=timeout,
                                validate_content=True)
    except AzureHttpError as e:
        if e.status_code == 403:
            azureml_error = AzureMLError.create(
                AuthorizationStorageAccount, account_name=account_name,
                container_name=container_name, status_code=e.status_code  # , error_code=e.error_code
            )  # error code not present in AzureHttpError
            raise AzureMLException._with_error(azureml_error, inner_exception=e)
        else:
            raise

    blob_size = blob_service.get_blob_properties(container_name, blob_name).properties.content_length
    module_logger.debug("Uploaded blob {} with size {}, file size {}.".format(blob_name, blob_size, file_size))


class StreamResetFunction():
    def __init__(self, position):
        self.position = position

    def __call__(self, stream, *args, **kwargs):
        stream.seek(self.position)
