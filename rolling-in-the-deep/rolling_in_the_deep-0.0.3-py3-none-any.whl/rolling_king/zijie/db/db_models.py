#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: db_models.py
# @Software: PyCharm

from rolling_king.zijie.db.sqlalchemy_util import AlchemyUtil
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
import datetime
import json
import re


class CaseRecordModel(AlchemyUtil.Base):

    __tablename__ = 'pytest_case_record'

    uid = Column(Integer, primary_key=True, autoincrement=True)  # '测试用例唯一标识'
    test_project_name = Column(String(64))  # 'QA的Python测试项目名称'
    test_psm = Column(String(32))  # '被测PSM'
    test_interface = Column(String(64))  # '被测接口: Http接口是subrui, Thrift接口是Service.Method'
    test_inter_type = Column(String(8))  # '接口协议类型'
    test_class = Column(String(64))  # 'Pytest的测试类：package.Class'
    test_method = Column(String(64))  # 'Pytest的测试方法名'
    test_description = Column(String(128))  # '测试用例描述'
    version = Column(Integer)  # '用例版本号'
    gmt_create = Column(DateTime, default=datetime.datetime.now)  # '记录创建时间'
    gmt_modify = Column(DateTime, default=datetime.datetime.now)  # '记录修改时间'

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 重写JSONEncoder的default方法，object转换成dict
class CaseRecordEncoder(json.JSONEncoder):
    # 重写default方法
    def default(self, obj):
        """
        把【Object】转成【Dict字典】
        :param obj:
        :return:
        """
        if isinstance(obj, CaseRecordModel):
            return {
                'uid': obj.uid,
                'test_project_name': obj.test_project_name,
                'test_psm': obj.test_psm,
                'test_interface': obj.test_interface,
                'test_inter_type': obj.test_inter_type,
                'test_class': obj.test_class,
                'test_method': obj.test_method,
                'test_description': obj.test_description,
                'version': obj.version,
                'gmt_create': obj.gmt_create,
                'gmt_modify': obj.gmt_modify
            }
        else:
            return json.JSONEncoder.default(self, obj)

    # 重写encode方法
    def encode(self, obj):
        """
        把【Object】转成【Dict字典】再转成【String】
        :param obj:
        :return:
        """
        if isinstance(obj, CaseRecordModel):
            dict_val = {
                'uid': obj.uid,
                'test_project_name': obj.test_project_name,
                'test_psm': obj.test_psm,
                'test_interface': obj.test_interface,
                'test_inter_type': obj.test_inter_type,
                'test_class': obj.test_class,
                'test_method': obj.test_method,
                'test_description': obj.test_description,
                'version': obj.version,
                'gmt_create': obj.gmt_create,
                'gmt_modify': obj.gmt_modify
            }
            return str(dict_val)
        else:
            return json.JSONEncoder.encode(self, obj)


# 重写JSONDecoder的decode方法，dict转换成object
class CaseRecordDecoder(json.JSONDecoder):

    def decode(self, dict_str):
        """
        把【字符串】转成【字典】再转成【Object】
        :param dict_str: 字典的字符串
        :return:
        """
        dict_val = super().decode(dict_str)  # 先把str转dict
        # 下面是dict转object
        CaseRecordDecoder.dict_to_obj(dict_val)

    @staticmethod
    def dict_to_obj(dict_val):
        """
        把【字典Dict】直接转成对应的【Object】
        :param dict_val:
        :return:
        """
        case_record_model = CaseRecordModel()
        if 'uid' in dict_val.keys():
            case_record_model.uid = dict_val['uid']
        else:
            case_record_model.uid = 0
        case_record_model.test_project_name = dict_val['test_project_name']
        case_record_model.test_psm = dict_val['test_psm']
        case_record_model.test_interface = dict_val['test_interface']
        case_record_model.test_inter_type = dict_val['test_inter_type']
        case_record_model.test_class = dict_val['test_class']
        case_record_model.test_method = dict_val['test_method']
        case_record_model.test_description = dict_val['test_description']
        case_record_model.version = dict_val['version']
        return case_record_model

############################################################################


class ExecutionRecordModel(AlchemyUtil.Base):

    __tablename__ = 'pytest_execution_record'

    uid = Column(Integer, primary_key=True, autoincrement=True)  # '测试记录每一个TestCase的唯一标识'
    test_unique_tag = Column(String(64))  # '一次整体测试的唯一标签'
    test_project_name = Column(String(64))  # 'QA的Python测试项目名称'
    test_psm = Column(String(32))  # '被测PSM'
    test_interface = Column(String(64))  # '被测接口: Http接口是subrui, Thrift接口是Service.Method'
    test_inter_type = Column(String(8))  # '接口协议类型'
    test_class = Column(String(64))  # 'Pytest的测试类：package.Class'
    test_method = Column(String(64))  # 'Pytest的测试方法名'
    test_result = Column(String(8))  # '测试用例执行结果'
    test_params = Column(String(64))  # 'Pytest的测试方法入参'
    test_duration = Column(Integer)  # '测试用例执行耗时'
    test_start_time = Column(String(64))  # '测试用例执行起始时间'
    test_finish_time = Column(String(64))  # '测试用例执行完成时间'
    test_assert = Column(String(8))  # '测试用例是否使用Assert断言'
    test_error_msg = Column(String(32))  # '测试用例失败信息'
    gmt_create = Column(DateTime, default=datetime.datetime.now)  # '记录创建时间'
    gmt_modify = Column(DateTime, default=datetime.datetime.now)  # '记录修改时间'

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 重写JSONEncoder的default方法，object转换成dict
class ExecutionRecordEncoder(json.JSONEncoder):
    # 重写default方法
    def default(self, execution_obj):
        """
        把【Object】转成【Dict字典】
        :param execution_obj:
        :return:
        """
        if isinstance(execution_obj, ExecutionRecordModel):
            return {
                'uid': execution_obj.uid,
                'test_unique_tag': execution_obj.test_unique_tag,
                'test_project_name': execution_obj.test_project_name,
                'test_psm': execution_obj.test_psm,
                'test_interface': execution_obj.test_interface,
                'test_inter_type': execution_obj.test_inter_type,
                'test_class': execution_obj.test_class,
                'test_method': execution_obj.test_method,
                'test_result': execution_obj.test_result,
                'test_params': execution_obj.test_params,
                'test_duration': execution_obj.test_duration,
                'test_start_time': execution_obj.test_start_time,
                'test_finish_time': execution_obj.test_finish_time,
                'test_assert': execution_obj.test_assert,
                'test_error_msg': execution_obj.test_error_msg,
                'gmt_create': execution_obj.gmt_create,
                'gmt_modify': execution_obj.gmt_modify
            }
        else:
            return json.JSONEncoder.default(self, execution_obj)

    # 重写encode方法
    def encode(self, execution_obj):
        """
        把【Object】转成【Dict字典】再转成【String】
        :param execution_obj:
        :return:
        """
        if isinstance(execution_obj, CaseRecordModel):
            return str(ExecutionRecordEncoder.default(execution_obj))
        else:
            return json.JSONEncoder.encode(self, execution_obj)


# 重写JSONDecoder的decode方法，dict转换成object
class ExecutionRecordDecoder(json.JSONDecoder):

    def decode(self, dict_str):
        """
        把【字符串】转成【字典】再转成【Object】
        :param dict_str: 字典的字符串
        :return:
        """
        dict_val = super().decode(dict_str)  # 先把str转dict
        # 下面是dict转object
        ExecutionRecordDecoder.dict_to_obj(dict_val)

    @staticmethod
    def dict_to_obj(dict_val):
        """
        把【字典Dict】直接转成对应的【Object】
        :param dict_val:
        :return:
        """
        execution_record_model = ExecutionRecordModel()
        if 'uid' in dict_val.keys():
            execution_record_model.uid = dict_val['uid']
        else:
            execution_record_model.uid = 0
        execution_record_model.test_unique_tag = dict_val['test_unique_tag']
        execution_record_model.test_project_name = dict_val['test_project_name']
        execution_record_model.test_psm = dict_val['test_psm']
        execution_record_model.test_interface = dict_val['test_interface']
        execution_record_model.test_inter_type = dict_val['test_inter_type']
        execution_record_model.test_class = dict_val['test_class']
        execution_record_model.test_method = dict_val['test_method']
        execution_record_model.test_result = dict_val['test_result']
        execution_record_model.test_params = dict_val['test_params']
        execution_record_model.test_duration = dict_val['test_duration']
        execution_record_model.test_start_time = dict_val['test_start_time']
        execution_record_model.test_finish_time = dict_val['test_finish_time']
        execution_record_model.test_assert = dict_val['test_assert']
        execution_record_model.test_error_msg = dict_val['test_error_msg']
        return execution_record_model


#################################################################################
###### 下方是全部接口Model：BamInterModel 和 未覆盖接口Model：NonCovInterModel ######

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)


def gen_unique_key():
    dt = datetime.datetime.now()
    dt_str = dt.strftime('%Y%m%d%H%M%S')
    ts = datetime.datetime.timestamp(dt)
    ts_str = str(int(ts * 1000000))
    unique_key = dt_str + ts_str
    return unique_key


class BamInterModel(AlchemyUtil.Base):

    __bind_key__ = "site_reldb"  # 若不指定，则使用默认数据库。
    __tablename__ = 'psm_inter_info'

    id = Column(String(32), primary_key=True)
    psm = Column(String(64), nullable=False)
    endpoint_id = Column(String(64), nullable=False)
    method = Column(String(8))
    path = Column(String(128))
    level = Column(Integer)
    name = Column(String(64))
    note = Column(String(64))
    rpc_method = Column(String(64))
    creator = Column(String(16))
    updater = Column(String(32))
    modify_time = Column(String(32))
    create_time = Column(String(32))
    publish_status = Column(Integer)
    priority = Column(Integer)
    version = Column(String(8))
    gmt_create = Column(DateTime, default=datetime.datetime.now)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 重写JSONEncoder的default方法，object转换成dict
class BamInterEncoder(json.JSONEncoder):
    # 重写default方法
    def default(self, obj):
        """
        把【Object】转成【Dict字典】
        :param obj:
        :return:
        """
        if isinstance(obj, BamInterModel):
            return {
                'id': obj.id,
                'psm': obj.psm,
                'endpoint_id': obj.endpoint_id,
                'method': obj.method,
                'path': obj.path,
                'level': obj.level,
                'name': obj.name,
                'note': obj.note,
                'rpc_method': obj.rpc_method,
                'creator': obj.creator,
                'updater': obj.updater,
                'create_time': obj.create_time,
                'modify_time': obj.modify_time,
                'publish_status': obj.publish_status,
                'priority': obj.priority,
                'version': obj.version,
                'gmt_create': obj.gmt_create
            }
        else:
            return json.JSONEncoder.default(self, obj)

    # 重写encode方法
    def encode(self, obj):
        """
        把【Object】转成【Dict字典】再转成【String】
        :param obj:
        :return:
        """
        if isinstance(obj, BamInterModel):
            return str(self.default(obj))
        else:
            return json.JSONEncoder.encode(self, obj)


# 重写JSONDecoder的decode方法，dict转换成object
class BamInterDecoder(json.JSONDecoder):

    def decode(self, dict_str, _w=WHITESPACE.match):
        """
        把【字符串】转成【字典】再转成【Object】
        :param dict_str: 字典的字符串
        :param _w:
        :return:
        """
        dict_val = super().decode(dict_str)  # 先把str转dict
        # 下面是dict转object
        self.dict_to_obj(dict_val)

    @staticmethod
    def dict_to_obj(dict_val):
        """
        把【字典Dict】直接转成对应的【Object】
        :param dict_val:
        :return:
        """
        bam_inter_model = BamInterModel()
        if 'uid' in dict_val.keys():
            bam_inter_model.id = dict_val['id']
        else:
            bam_inter_model.id = gen_unique_key()
        bam_inter_model.psm = dict_val['psm']
        bam_inter_model.endpoint_id = dict_val['endpoint_id']
        bam_inter_model.method = dict_val['method']
        bam_inter_model.path = dict_val['path']
        bam_inter_model.level = dict_val['level']
        bam_inter_model.name = dict_val['name']
        bam_inter_model.note = dict_val['note']
        bam_inter_model.rpc_method = dict_val['rpc_method']
        bam_inter_model.creator = dict_val['creator']
        bam_inter_model.updater = dict_val['updater']
        bam_inter_model.create_time = dict_val['create_time']
        bam_inter_model.modify_time = dict_val['modify_time']
        bam_inter_model.publish_status = dict_val['publish_status']
        bam_inter_model.priority = dict_val['priority']
        bam_inter_model.version = dict_val['version']
        if 'gmt_create' in dict_val.keys():
            bam_inter_model.gmt_create = dict_val['gmt_create']
        return bam_inter_model


class NonCovInterModel(AlchemyUtil.Base):

    __bind_key__ = "site_reldb"  # 若不指定，则使用默认数据库。
    __tablename__ = 'psm_non_cov_inter'

    id = Column(String(32), primary_key=True)
    psm = Column(String(64), nullable=False)
    endpoint_id = Column(String(64), nullable=False)
    method = Column(String(8))
    path = Column(String(128))
    name = Column(String(64))
    note = Column(String(64))
    rpc_method = Column(String(64))
    version = Column(String(8))
    gmt_create = Column(DateTime, default=datetime.datetime.now)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


