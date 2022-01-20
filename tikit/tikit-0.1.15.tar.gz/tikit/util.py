# -*- coding: utf-8 -*-
from tikit.tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tikit.tencentcloud.tione.v20211111 import models


def parse_cos_str(cos_str):
    """ 解析cos 字符串成结构体

    :param cos_str: 格式如： <bucket>/<cos path>/
    :type cos_str: str
    :return:
    :rtype: :class:`tikit.tencentcloud.tione.v20211111.models.CosPathInfo`
    """
    try:
        if cos_str[-1] != '/':
            raise TencentCloudSDKException(message='cos string should end with "/"')
        cos_info = models.CosPathInfo()
        bucket_index = cos_str.index('/')
        cos_info.Bucket = cos_str[:bucket_index]
        if len(cos_info.Bucket) == 0:
            raise TencentCloudSDKException(message='bucket cannot be empty')
        cos_info.Paths = [cos_str[bucket_index + 1:]]
        return cos_info
    except Exception as err:
        raise TencentCloudSDKException(message='cos string is not invalid, should be "<bucket>/<cos path>/"')
