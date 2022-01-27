from pathlib import Path
from multiprocessing import get_logger
from pbx_component_files_uploader.interfaces.base_uploader import BaseUploader
from pbx_component_files_uploader.exceptions.errors import UploadError
from .auth import Auth

import requests

log = get_logger()
log.name = 'selectel'


class Selectel(BaseUploader):

    DEFAULT_RETRIES = 3

    def __init__(self, authData: dict, options: dict = {}):
        self.maxRetries = options.get('max_retries', self.DEFAULT_RETRIES)
        self.auth = Auth(authData=authData, requests=requests,
                         tokenCacheDir=options.get('token_cache_dir', ''), logger=log)

    def build_url(self, storage_url, container, dstFile):
        return '{storage_url}/{name}/{key}'.format(
            storage_url=storage_url.rstrip('/'),
            name=container.strip('/'),
            key=dstFile.lstrip('/'),
        )

    def upload(self, srcFilePath: str, dstFileName: str) -> str:
        srcFile = Path(srcFilePath)
        if not srcFile.is_file():
            raise ValueError(f'No such file [{srcFilePath}]')

        if not dstFileName:
            raise ValueError('Empty [dstFileName] field')

        for i in range(self.DEFAULT_RETRIES):
            try:
                storageData = self.auth.get_storage_data()

                headers = {
                    'X-Auth-Token': storageData.get('secret')
                }
                url = self.build_url(storage_url=storageData.get(
                    'storage_url'), container=storageData.get('container'), dstFile=dstFileName)

                response = requests.put(
                    url=url, data=srcFile.open(mode='rb'), headers=headers)

                if response.status_code == 201:
                    return response.url
            except Exception as e:
                log.debug(
                    f'Attempt [{i + 1}]. Failed to upload. Cause [{e.__cause__}]')

        raise UploadError(400, f'Failed upload file [{srcFilePath}]')
