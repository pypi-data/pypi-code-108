# -*- coding: utf-8 -*-
from functools import wraps

from tikit.client import Client

_default_client = Client()


def use_default_client(func):
    """装饰器，能把模块的函数转成调用_default_client的方法。
    虽然能把公共的内容都抽离出来，但使用装饰器的方式会导致IDE提示不友好，用户看到的注释不直观。

    :param func:    传入的模块的函数
    :type func:     对外的任意函数
    :return:        装饰器
    :rtype:         函数
    """
    @wraps(func)
    def wrapper(*args, **kw):
        _default_client.guarantee_valid()
        getattr(_default_client, func.__name__)(*args, **kw)
    # wrapper.__doc__ = getattr(_default_client, func.__name__).__doc__
    return wrapper


def describe_cos_buckets():
    """列出所有bucket

    :return:    bucket列表
    :rtype:     dict
    返回的结果如：
    {
      "Owner": {
        "ID": "qcs::cam::uin/100011011262:uin/100011011262",
        "DisplayName": "100011011162"
      },
      "Buckets": {
        "Bucket": [
          {
            "Name": "bucket-58565",
            "Location": "ap-beijing-fsi",
            "CreationDate": "2021-07-21T11:06:00Z",
            "BucketType": "cos"
          },
          {
            "Name": "tai-1300158565",
            "Location": "ap-guangzhou",
            "CreationDate": "2021-10-22T11:04:40Z",
            "BucketType": "cos"
          }
        ]
      }
    }
    """
    _default_client.guarantee_valid()
    return _default_client.describe_cos_buckets()


def upload_to_cos(local_path, bucket, cos_path):
    """
    把本地路径下的文件或者目录上传到cos上

    :param local_path:  本地路径
    :type local_path:   str
    :param bucket:      cos上的桶
    :type bucket:       str
    :param cos_path:    cos上的路径
    :type cos_path:     str
    :return:            None. 错误信息通过 raise 给出。
    :rtype:
    """
    _default_client.guarantee_valid()
    return _default_client.upload_to_cos(local_path, bucket, cos_path)


def describe_cos_path(bucket, path):
    """获取cos的目录的信息。目录下的内容最多显示1000个。要显示目录下的文件和文件夹，请以"/"结尾

    :param bucket:          cos的桶
    :type bucket:           str
    :param path:            路径
    :type path:             str
    :return:                目录信息
    :rtype:                 dict
    :param maker:           从marker开始列出条目
    :type maker:            str
    :param max_keys:        设置单次返回最大的数量,最大为1000.
    :type max_keys:         int
    :param encoding_type:   设置返回结果编码方式,只能设置为url.
    :type encoding_type:    str
    """
    _default_client.guarantee_valid()
    return _default_client.describe_cos_path(bucket, path)


def delete_cos_path(bucket, path):
    """删除cos目录。要删除目录下的文件和文件夹，请以"/"结尾，即：不带斜杠的，当成文件来删除；带斜杠的，当成文件夹来删除

    :param bucket:      cos的桶
    :type bucket:       str
    :param delete_path: 要删除的路径
    :type delete_path:  str
    """
    _default_client.guarantee_valid()
    return _default_client.delete_cos_path(bucket, path)


def download_from_cos(bucket, cos_path, local_path):
    """从cos上下载文件或者目录本地。
    注意：本地文件存在会直接覆盖。 cos_path为目录且local_path 为存在的目录的时候，cos_path的文件夹名会作为子目录保留。

    :param bucket:      cos上的桶
    :type bucket:       str
    :param cos_path:    cos上的路径
    :type cos_path:     str
    :param local_path:  本地路径
    :type local_path:   str
    :return:            None. 错误信息通过 raise 给出。
    :rtype:
    """
    _default_client.guarantee_valid()
    return _default_client.download_from_cos(bucket, cos_path, local_path)
