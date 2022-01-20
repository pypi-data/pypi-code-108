# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-02 15:17:41
@LastEditTime: 2021-12-29 17:57:33
@LastEditors: HuangJianYi
:description: 自定义实体模型
"""

class InvokeResult():
    """
    :description: 接口返回实体
    :return: InvokeResult
    :last_editors: HuangJianYi
    """
    def __init__(self):
        self.success = True
        self.data = InvokeResultData().__dict__


class InvokeResultData():
    """
    :description: 接口返回实体
    :return: InvokeResultData
    :last_editors: HuangJianYi
    """
    def __init__(self):
        self.success = True
        self.data = None
        self.error_code = ""
        self.error_message = ""


class FileUploadInfo():
    """
    :description: 文件上传信息实体
    :return: FileUploadInfo
    :last_editors: HuangJianYi
    """
    def __init__(self):
        # 检查值
        self.md5_value = ""
        # 上传路经
        self.resource_path = ""
        # 原文件名
        self.original_name = ""
        # 文件路经
        self.file_path = ""
        # 图片宽度
        self.image_width = 0
        # 图片高度
        self.image_height = 0


class PageInfo():
    """
    :description: 分页列表实体
    :param page_index：当前索引号
    :param page_size：页大小
    :param record_count：总记录数
    :param data：数据
    :return: PageInfo
    :last_editors: HuangJianYi
    """
    def __init__(self, page_index=0, page_size=10, record_count=0, data=None):
        """
        :description: 分页列表实体
        :param page_index：当前索引号
        :param page_size：页大小
        :param record_count：总记录数
        :param data：数据
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        # 数据
        self.data = data
        # 当前索引号
        self.page_index = page_index
        # 页大小
        self.page_size = page_size
        # 总记录数
        self.record_count = record_count

        # 页数
        self.page_count = record_count / page_size + 1
        if page_size == 0:
            self.page_count = 0
        if record_count % page_size == 0:
            self.page_count = record_count / page_size
        self.page_count = int(self.page_count)

        # 当前页号
        self.page_no = page_index + 1

        # 上一页索引
        self.previous_index = page_index - 1 if page_index > 0 else 0

        # 下一页索引
        self.next_index = page_index + 1
        if self.page_count == 0:
            self.next_index = 0
        if self.page_no >= self.page_count:
            self.next_index = self.page_index

        # 是否下一页
        self.is_next = True
        if self.page_count == 0:
            self.is_next = False
        if self.page_no >= self.page_count:
            self.is_next = False

        # 是否上一页
        self.is_previous = True
        if page_index == 0:
            self.is_previous = False


class ConditionWhere():
    """
    @description: 条件拼接实体
    """
    def __init__(self):
        
        self.condition_list = []

    def add_condition(self, condition):
        """
        :description: 添加条件
        :param condition:条件
        :return:
        :last_editors: HuangJianYi
        """
        self.condition_list.append(condition)

    def to_string(self, split_str="and"):
        """
        :description: 拼接成字符串
        :param split_str:分隔符
        :return:
        :last_editors: HuangJianYi
        """
        return str(" " + split_str + " ").join(self.condition_list)