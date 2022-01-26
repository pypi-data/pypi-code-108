import requests
from codefast.io import FileIO
import tqdm
from pathlib import Path
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import os
from codefast.logger import Logger
from codefast.network.factory import Spider


class Network:
    log = Logger()
    spider = Spider().born()

    @classmethod
    def parse_headers(cls, str_headers: str) -> dict:
        lst = [u.split(':', 1) for u in str_headers.split('\n')]
        return dict((u[0].strip(), u[1].strip()) for u in lst)

    @classmethod
    def get(cls, url: str, **kwargs) -> requests.models.Response:
        return cls.spider.get(url, **kwargs)

    @classmethod
    def post(cls, url: str, **kwargs) -> requests.models.Response:
        return cls.spider.post(url, **kwargs)

    @staticmethod
    def upload_file(upload_url: str,
                    filepath: str,
                    fields={}) -> requests.Response:
        with tqdm(
                desc=filepath,
                total=Path(filepath).stat().st_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            with open(filepath, "rb") as f:
                fields["file"] = (FileIO.basename(filepath), f)
                e = MultipartEncoder(fields=fields)
                m = MultipartEncoderMonitor(
                    e, lambda monitor: bar.update(monitor.bytes_read - bar.n))
                headers = {"Content-Type": m.content_type}
                resp = requests.post(upload_url, data=m, headers=headers)
                return resp

    @classmethod
    def _resume(cls,
                url: str,
                name: str,
                resume_byte_pos: int = 0,
                proxies=None) -> None:
        resume_header = {'Range': 'bytes=%d-' % resume_byte_pos}
        if resume_byte_pos > 0:
            response = requests.get(url,
                                    stream=True,
                                    headers=resume_header,
                                    proxies=proxies)
            file_mode = 'ab'
        else:
            response = requests.get(url, stream=True, proxies=proxies)
            file_mode = 'wb'

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        cls.log.info("remain total size", total_size_in_bytes)
        block_size = 1024     # 8 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB',
                            unit_scale=True)

        with open(name, file_mode) as f:
            for chunk in response.iter_content(block_size):
                progress_bar.update(len(chunk))
                f.write(chunk)
        progress_bar.close()
        cls.log.info("download completed.")

    @classmethod
    def download(cls, url: str, name=None, proxies=None) -> None:
        name = name or url.split('/').pop().strip()

        if not FileIO.exists(name):
            cls.log.info("start new download task {}".format(name))
            cls._resume(url, name, proxies=proxies)
        else:
            resume_size_in_bytes = os.path.getsize(name)
            total_size_in_bytes = int(
                requests.get(url, stream=True,
                            proxies=proxies).headers.get('content-length',
                                                        resume_size_in_bytes))

            while total_size_in_bytes - resume_size_in_bytes > 8:
                cls.log.info(resume_size_in_bytes, total_size_in_bytes)
                cls.log.info('resume downloading {}'.format(name))
                try:
                    cls._resume(url, name, resume_size_in_bytes, proxies=proxies)
                except Exception as e:
                    cls.log.error(repr(e))
                resume_size_in_bytes = os.path.getsize(name)


def urljoin(*args):
    """Join args into a url. Trailing but not leading slashes are removed."""
    args = [str(x).rstrip('/').lstrip('/') for x in args]
    return '/'.join(args)
