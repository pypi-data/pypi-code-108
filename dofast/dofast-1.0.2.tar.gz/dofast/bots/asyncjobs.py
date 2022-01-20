from dofast.web.celeryapi import produce_app
from typing import Any, Dict, List, Tuple, NamedTuple

import codefast as cf
from authc import authc
from codefast.fio import ffpb


class FileDownloader(object):
    def download(self, url: str, name: str) -> bool:
        if url.endswith('.m3u8'):
            return self.download_m3u8(url, name)
        else:
            cf.info(f'Downloading {url}')
            cf.net.download(url, name)
            return True

    def download_m3u8(self, url: str, name: str) -> bool:
        argv = ['-i', url, '-y', '-c:v', 'copy', name]
        cf.info(f'Downloading {url}')
        ffpb(argv)
        return True


class TaskDescriptor(NamedTuple):
    url: str
    name: str

    def __repr__(self) -> str:
        return str(self._asdict())


class PcloudFileUploader(object):
    def __init__(self) -> None:
        config = authc()
        self.folderid = config['pcloud_public_tmp_folderid']
        self.auth = config['pcloud_auth']
        self.url_prefix = config['pcloud_public_tmp_prefix']
        self.url = 'https://api.pcloud.com/uploadfile?folderid={}&filename=x&auth={}'.format(
            self.folderid, self.auth)
        self.video_format = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv')

    def upload(self, fpath: str, remove_after_upload: bool = True) -> bool:
        # upload file to pcloud vps directory
        cf.info(f'Uploading {fpath} to pcloud')
        resp = cf.net.upload_file(self.url, fpath)
        cf.info('{}, {}'.format(self.__class__.__name__, resp.text))

        if remove_after_upload:
            cf.info("Removing {}".format(fpath))
            cf.io.rm(fpath)

        base_name = cf.io.basename(fpath)
        return self.url_prefix + base_name

    def parse_url(self, text: str) -> TaskDescriptor:
        cf.info(f'Parsing {text}')
        placeholder = 'TEXT'
        url, name = ' '.join([text, placeholder]).split(' ')[:2]
        if name == placeholder:
            name = cf.io.basename(url)

        if text.endswith('m3u8') and not name.endswith(self.video_format):
            name += '.mp4'
        return TaskDescriptor(url=url, name=name)


app = produce_app('files')


@app.task(bind=True)
def cloudsync(self, text: str) -> str:
    pc = PcloudFileUploader()
    td = pc.parse_url(text)
    cf.info('Task descriptor {}'.format(repr(td)))

    downloader = FileDownloader()
    downloader.download(td.url, td.name)
    cf.info('Downloaded {}'.format(td.name))

    result_url = pc.upload(td.name, remove_after_upload=True)
    cf.info('Uploaded {}'.format(td.name))
    return result_url
