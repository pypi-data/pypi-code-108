# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 11:30:45
@LastEditTime: 2021-12-07 11:07:53
@LastEditors: HuangJianYi
@Description: 
"""
import oss2
import os

from seven_framework.uuid import *
from seven_framework import ExcelHelper, config


class OSS2Helper:
    """
    :description: 阿里云存储帮助类 上传文件、数据导入excel并返回下载地址
    :param {type} 
    :return: 
    :last_editors: HuangJianYi
    """
    @classmethod
    def get_oss_config(self):
        oss_config = config.get_value("oss_config")
        if not oss_config:
            oss_config = {}
            oss_config["AK_ID"] = "LTAI4GAV8q6wxi2gqispR4my"
            oss_config["AK_SECRET"] = "LWBuIALo4X4pnBDCwiuRjZur1Yhm5h"
            oss_config["BUCKET_NAME"] = "mang-he"
            oss_config["END_POINT"] = "oss-cn-zhangjiakou.aliyuncs.com"
            oss_config["DOMAIN"] = "https://mang-he.oss-cn-zhangjiakou.aliyuncs.com/"
        self.AK_ID = oss_config["AK_ID"]
        self.AK_SECRET = oss_config["AK_SECRET"]
        self.BUCKET_NAME = oss_config["BUCKET_NAME"]
        self.END_POINT = oss_config["END_POINT"]
        self.DOMAIN = oss_config["DOMAIN"]

    @classmethod
    def upload(self, file_name, local_file='', folder='', is_auto_name=True, data=None):
        """
        :description: 上传文件
        :param file_name：文件名称
        :param local_file：本地文件地址
        :param is_auto_name：是否生成随机文件名
        :param data：需要上传的数据
        :return: 
        :last_editors: HuangJianYi
        """
        self.get_oss_config()
        # 文件名
        file_name = os.path.basename(local_file) if local_file != "" else file_name

        if is_auto_name:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        auth = oss2.Auth(self.AK_ID, self.AK_SECRET)
        bucket = oss2.Bucket(auth, self.END_POINT, self.BUCKET_NAME)

        folder = folder.strip('/')
        folder = folder + "/" if folder != "" else folder
        file_name = folder + file_name

        # 上传文件
        # 如果需要上传文件时设置文件存储类型与访问权限，请在put_object中设置相关headers, 参考如下。
        # headers = dict()
        # headers["x-oss-storage-class"] = "Standard"
        # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
        # result = bucket.put_object('<yourObjectName>', 'content of object', headers=headers)
        if local_file:
            result = bucket.put_object_from_file(file_name, local_file)
        else:
            result = bucket.put_object(file_name, data)

        resource_path = ''
        if result.status == 200:
            resource_path = self.DOMAIN + file_name
            # # HTTP返回码。
            # print('http status: {0}'.format(result.status))
            # # 请求ID。请求ID是请求的唯一标识，强烈建议在程序日志中添加此参数。
            # print('request_id: {0}'.format(result.request_id))
            # # ETag是put_object方法返回值特有的属性。
            # print('ETag: {0}'.format(result.etag))
            # # HTTP响应头部。
            # print('date: {0}'.format(result.headers['date']))

        return resource_path

    @classmethod
    def export_excel(self, import_data):
        """
        :description: 把数据导入excel并返回下载地址
        :param import_data:导入数据
        :return excel下载地址
        :last_editors: HuangJianYi
        """
        resource_path = ""
        if import_data:
            try:
                if not os.path.exists("temp"):
                    os.makedirs("temp")
                path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
                ExcelHelper.export(import_data, path)
                resource_path = self.upload("", path, config.get_value("oss_folder"), False)
                os.remove(path)
            except Exception as ex:
                pass
        return resource_path