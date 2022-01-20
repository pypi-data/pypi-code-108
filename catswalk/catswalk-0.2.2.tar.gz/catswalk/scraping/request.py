import json
from bs4 import BeautifulSoup
import time
import sys
from datetime import datetime, timezone
import email.utils as eut
import logging
from catswalk.scraping.types.type_response import Response, ResponseHtml, ResponseJson
import requests

logger = logging.getLogger()


class CatsWalkRequestError(Exception):
    pass


class CWRequest:
    DEFAULT_TIMEOUT = (15.0, 20.5)

    def __init__(self, verify=True, timeout=DEFAULT_TIMEOUT):
        """[summary]

        Args:
            verify (bool, optional): [description]. Defaults to True.
        """
        self.verify = verify
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = self.verify
        self.timeout = self.timeout

    def __enter__(self):
        """

        :return:
        """
        self.print_global_info()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()

    @classmethod
    def parse_http_date(s):
        """[summary]

        Args:
            s ([type]): [description]

        Returns:
            [type]: [description]
        """
        return datetime(*eut.parsedate(s)[:6], tzinfo=timezone.utc)

    def close(self):
        """[Close session]
        """
        self.session.close()

    def get_cookie(self, key: str):
        """[Get cookie by key]

        Args:
            key ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.session.cookies.get(key)

    def get_cookies(self):
        """[Get cookies]

        Returns:
            [type]: [description]
        """
        return self.session.cookies.get_dict()


    def __mk_result(self, ret, response_content_type: str):
        """[Wrap response]

        Args:
            ret ([type]): [description]
            response_content_type (str): [description]

        Returns:
            [type]: [description]
        """
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseHtml(ret.headers, soup, ret)
        elif response_content_type == "json":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseJson(ret.headers, json.loads(str(soup)), ret)
        else:
            return Response(ret.headers, ret.content, ret)


    def __check_status_code(self, url, status_code):
        """[Check http status code]

        Args:
            url ([type]): [description]
            status_code ([type]): [description]

        Raises:
            CatsRequestSessionError: [description]

        Returns:
            [type]: [description]
        """
        if status_code != 200:
            raise CatsWalkRequestError(f"{url} response code is {status_code}")
        return True

    def retry_get(self, url, response_content_type=None, retry_num=4, wait=1):
        """[summary]

        Args:
            url ([type]): [description]
            response_content_type ([type], optional): [description]. Defaults to None.
            retry_num (int, optional): [description]. Defaults to 4.
            wait (int, optional): [description]. Defaults to 1.

        Raises:
            CatsRequestSessionError: [description]

        Returns:
            [type]: [description]
        """
        response = None
        for i in range(retry_num):
            try:
                response = self.get(url, response_content_type)
                return response
            except Exception:
                print(f"retry_get: {url} retry {i}")
                time.sleep(wait)
        raise CatsWalkRequestError(f"{url} retry count is {retry_num}")

    def get(self, url, response_content_type=None):
        """[summary]
        
        Arguments:
            url {[type]} -- [description]
        
        Keyword Arguments:
            response_content_type {[type]} -- [html or json] (default: {None})
        
        Raises:
            RuntimeError: [description]
        
        Returns:
            [type] -- [description]
        """
        ret = self.session.get(url, timeout=self.timeout)
        self.__check_status_code(url, ret.status_code)
        return self.__mk_result(ret, response_content_type)

    def post(self, url, post_data, response_content_type):
        """[summary]

        Args:
            url ([type]): [description]
            post_data ([type]): [description]
            response_content_type ([type]): [description]

        Returns:
            [type]: [description]
        """
        ret = self.session.post(url, post_data, timeout=self.timeout)
        self.__check_status_code(url, ret.status_code)
        return self.__mk_result(ret, response_content_type)

    def download(self, url: str, fullpath: str, request_type: str = "get", post_data=None):
        """[summary]

        Args:
            url (str): [description]
            fullpath (str): [description]
            request_type (str, optional): [description]. Defaults to "get".
            post_data ([type], optional): [description]. Defaults to None.
        """
        print(f"download: {url}")
        if request_type == "post":
            bi = self.post(url=url, post_data=post_data)
        else:
            bi = self.get(url=url).content
        with open(fullpath, "wb") as f:
            f.write(bi)

    def get_global_info(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        url = "https://ipinfo.io"
        result = None
        try:
            result = self.get(url=url, response_content_type="json").content
        except Exception:
            logger.warning(f"get_global_info response is null: {sys.exc_info()}")
        return result

    def print_global_info(self):
        """[summary]
        """
        logger.info(f"global network info is {self.get_global_info()}")
