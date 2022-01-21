# V2021-6-25：Wriet by lyc at，基础功能封装
# V2021-6-30：Update by lyc at，注释优化，增加上传接口类

import os

# 从Python SDK导入BOS配置管理模块以及安全认证模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

# 导入BOS相关模块
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient


def md5file(file_name):
    """content_md5计算方法是对数据执行md5算法获取128位二进制数据，再进行base64编码

    Args:
        file_name ([str]): [文件绝对路径]

    Returns:
        [str]: [base64编码后的文件md5值]
    """
    import io
    import hashlib
    import base64

    # print(file_name)
    buf_size = 8192
    fp = open(file_name, 'rb')
    md5 = hashlib.md5()
    while True:
        bytes_to_read = buf_size
        buf = fp.read(bytes_to_read)
        if not buf:
            break
        md5.update(buf)
    content_md5 = base64.standard_b64encode(md5.digest())
    return content_md5


class BOS():
    """[百度云BOS对象存储  Python3 SDK封装]"""
    def __init__(self, key):
        self.ak = key['Access_Key']
        self.sk = key['Secret_Access_Key']
        self.endpoint = key['BOS']['Endpoint']
        self.bucket_name = key['BOS']['Bucket']
        try:
            # 创建BceClientConfiguration
            self.config = BceClientConfiguration(credentials=BceCredentials(self.ak, self.sk), endpoint=self.endpoint)
            # 新建BosClient
            self.bos_client = BosClient(self.config)
        
        except Exception as err:
            raise Exception(err)  # 连接失败主动抛出异常


    def list_Objects(self, prefix='', marker='None'):
        """[分页获取所有Object]

        Args:
            prefix (str, optional): [过滤指定前缀的object key返回]. Defaults to ''.
            marker (str, optional): [本次查询的起点]. Defaults to 'None'.

        Yields:
            [str]: [一次返回一个 object_key（生成器）]
        """
        isTruncated = True
        max_keys = 500  # 限定此次返回object的最大数，此数值不能超过1000，如果不设定，默认为1000。
        marker = None
        while isTruncated:
            response = self.bos_client.list_objects(self.bucket_name, prefix=prefix, max_keys=max_keys, marker=marker)
            for obj in response.contents:
                yield obj.key
            isTruncated = response.is_truncated
            marker = getattr(response, 'next_marker', None)


    def put_Object(self, file_name, object_key):
        """[简单上传：file_name < 5G]

        Args:
            file_name ([str]): [本地要上传文件的绝对路径]
            object_key ([str]): [文件在对象存储中的名称，文件名可以包含'/'表示目录]

        Returns:
            [int]: [200-成功;!=200 失败]
        """
        try:
            # 从文件中上传的Object
            content_md5 = md5file(file_name).decode('utf-8')  # 本地 content_md5
            response = self.bos_client.put_object_from_file(self.bucket_name, object_key, file_name)
            if content_md5 == response.metadata.content_md5:
                return 200
            else:
                return -1

        except Exception as err:
            print(err)
            return False


    def put_Object_Part(self, file_name, object_key):
        """[分块上传：file_name > 5G]

        Args:
            file_name ([str]): [本地要上传文件的绝对路径]
            object_key ([str]): [文件在对象存储中的名称，文件名可以包含'/'表示目录]

        Returns:
            [int]: [200-成功;!=200 失败]
        """
        try:
            raise Exception("分块上传程序未完成")
            # https://cloud.baidu.com/doc/BOS/s/sjwvyrg3l#%E5%88%86%E5%9D%97%E4%B8%8A%E4%BC%A0
        
        except Exception as err:
            print(err)
            return False


    def upload_File(self, file_name, object_key):
        """[上传文件接口类，自动识别上传文件来选择普通上传方法或分块上传方法]

        Args:
            file_name ([str]): [本地要上传文件的绝对路径]
            object_key ([str]): [文件在对象存储中的名称，文件名可以包含'/'表示目录]

        Returns:
            [int]: [200-成功;!=200 失败]
        """
        file_size = os.path.getsize(file_name)
        n = 1024  # count, 10count = 10M；这里我认为大于1024M的是大文件，采用分块上传方法
        size_threshold = n * 1024 * 1024  # 阈值：n=100 即 100M=104857600bytes
        if file_size <= size_threshold:  # 文件大小阈值判断
            return self.put_Object(file_name, object_key)
        else:
            return self.put_Object_Part(file_name, object_key)


    def delete_Object(self, object_key):
        """[删除单个/删除批量 Object文件]

        Args:
            object_key ([str]): [对象存储中的文件名，同时支持传入str或list类型]

        Returns:
            [int]: [200-成功;!=200 失败]
        """
        try:
            if isinstance(object_key, str):
                self.bos_client.delete_object(self.bucket_name, object_key)  # 删除单个文件
            elif isinstance(object_key, list):
                self.bos_client.delete_multiple_objects(self.bucket_name, object_key)  # 批量删除列表内的文件
            return 200

        except Exception as err:
            print(err)
            return False


    def head_Object(self, object_key):
        """[获取Object元数据信息（大小、最后更新时间等）]

        Args:
            object_key ([str]): [对象存储中的文件名]

        Returns:
            [response.metadata]: [数据元对象]
        """
        try:
            response = self.bos_client.get_object_meta_data(self.bucket_name, object_key)
            # print("Get meta:{}", response.metadata)
            return response.metadata

        except exception.BceError as err:
            print(err)
            return False


    def get_Object(self, object_key, save_dir):
        """[简单下载：下载Object到本地文件]

        Args:
            object_key ([str]): [对象存储中的文件名]
            save_dir ([str]): [保存到本地目录]

        Returns:
            [int]: [200-成功;!=200 失败]
        """
        file_name = save_dir + os.sep + object_key.replace('/', os.sep)  # 下载文件本地绝对路径拼接
        os.makedirs(os.path.dirname(file_name), exist_ok=True)  # 创建文件目录
        try:
            response = self.bos_client.get_object_to_file(self.bucket_name, object_key, file_name)
            if response.metadata.content_md5 == md5file(file_name).decode('utf-8'):
                return 200
            else:
                return -1

        except Exception as err:
            print(err)
            return False
