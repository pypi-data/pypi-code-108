import oss2

from winhye_common.utils.exception_base import OSSException
from winhye_common.winhye_logger import logging as logging

__all__ = ["OssBucket"]
logger = logging.getLogger()


class OssBucket:
    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, bucket_name: str):
        """
        初始化oss链接
        :param access_key_id:  yourAccessKeyId，阿里云账号生成
        :param access_key_secret:  yourAccessKeySecret， 阿里云账号生成
        :param endpoint:  yourEndpoint，地域，北京为例：oss-cn-beijing.aliyuncs.com
        :param bucket_name:  Bucket名称，请查看阿里云桶名称
        """
        auth = oss2.Auth(access_key_id, access_key_secret)
        self.oss_bucket = oss2.Bucket(auth, endpoint, bucket_name, connect_timeout=30)

    def upload(self, oss_path, data):
        """
        二进制流、字符串上传
        :param oss_path: 文件在oss的存储路径
        :param data: 上传的文件内容
        :return:
        """
        retry_count = 0
        while True:
            try:
                retry_count += 1
                row = self.oss_bucket.put_object(oss_path, data)
                logger.debug(f"status: {row.status}")
                if row.status == 200:
                    break
            except Exception as e:
                if retry_count >= 3:
                    logger.error(e)
                    raise OSSException("cannot upload data, status: {exception}".format(exception=e))

    def upload_from_file(self, oss_path: str, local_path: str):
        """
        本地文件上传
        :param oss_path: 文件在oss的存储路径
        :param local_path: 文件的本地路径
        :return:
        """
        retry_count = 0
        while True:
            try:
                retry_count += 1
                row = self.oss_bucket.put_object_from_file(oss_path, local_path)
                logger.debug(f"status: {row.status}")
                if row.status == 200:
                    break
            except Exception as e:
                if retry_count >= 3:
                    logger.error(e)
                    raise OSSException("cannot upload file, status: {exception}".format(exception=e))

    def get_message(self, oss_path: str) -> str:
        """
        获取文件内容
        :param oss_path: 文件在oss的存储路径
        :return: object_stream 文件流文本
        """
        try:
            object_stream = self.oss_bucket.get_object(oss_path).read()
            return object_stream
        except Exception as e:
            logger.error(e)
            raise OSSException("cannot get message, status: {exception}".format(exception=e))

    def get_url(self, oss_path: str, method="GET", expires=5 * 60, slash_safe=True, headers=None, params=None) -> str:
        try:
            url = self.oss_bucket.sign_url(
                method,
                oss_path,
                expires,
                slash_safe=slash_safe,
                headers=headers,
                params=params
            )
            return url
        except Exception as e:
            logger.error(e)
            raise OSSException("cannot get url, status: {exception}".format(exception=e))

    def del_file(self, oss_path: str):
        """
        :param oss_path: 文件在oss的存储路径
        :return:
        """
        retry_count = 0
        while True:
            try:
                retry_count += 1
                row = self.oss_bucket.delete_object(oss_path)
                logger.debug(f"status: {row.status}")
                if row.status == 204:
                    break
            except Exception as e:
                if retry_count >= 3:
                    logger.error(e)
                    raise OSSException("cannot delete file, status: {exception}".format(exception=e))


if __name__ == '__main__':
    oss_conn = OssBucket(
        "LTAI5t99asZVXSnhnm3vSnaq",
        "3tnIF5zEiS90TC1Xgc6cK1Ecab3Ij8",
        "oss-cn-beijing.aliyuncs.com",
        "winhye-test"
    )
    # obj = oss_conn.upload("a/1627464446637.mp3", "1627464446637.mp3")
    obj = oss_conn.get_message("a/1627464446637.mp3")
    print(obj)
