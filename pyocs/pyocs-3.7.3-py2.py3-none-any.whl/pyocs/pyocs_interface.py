import abc  # 利用abc模块实现抽象类
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_exception import *
import pyocs.pyocs_demand_xml


class UniteInterface(metaclass=abc.ABCMeta):
    _space = 60
    _code_branch = ''
    _customer_id = ''
    _test_type = ''

    _android_system = ''
    android_4_4 = '4_4'
    android_8_0 = '8_0'

    def __init__(self, ocs_demand: PyocsDemand):
        # super().__init__()
        self.request_dict = ocs_demand.get_request()
        self.ocs_demand = ocs_demand
        self.ocs_number = ocs_demand.get_ocs_number()
        self.demand_xml = pyocs.pyocs_demand_xml.PyocsDemand(self.ocs_number)  # 从ocs对比页获取到的需求

    @abc.abstractmethod
    def get_ocs_require(self):
        """
        强制要求实现，获取model id的配置内容
        :return:
        """
        pass

    @abc.abstractmethod
    def get_ocs_modelid(self):
        """
        强制要求实现，获取model id
        :return: str : model id
        """
        pass

    @abc.abstractmethod
    def get_code_branch(self):
        """
        强制要求实现，获取代码分支，用于提交配置
        :return: str : 代码分支
        """
        pass

    def get_customer_id(self):
        """
        无需实现，重写 _customer_id 变量即可
        :return: str : customer id
        """
        return self._customer_id

    def get_test_type(self):
        """
        无需实现，重写 _test_type 变量即可
        :return: str : 测试类型
        """
        return self._test_type

    def get_android_system(self):
        """
        非强制实现，获取安卓系统版本，仅用于358等类似的一个方案出两种系统的逆天方案
        :return: str : 安卓版本
        """
        return self._android_system

    def get_macro_line(self, macro: str, value):
        """
        根据宏和值创建一个配置行，自带换行符
        :param macro:
        :param value:
        :return:
        """
        define = '#define'.ljust(8)
        return define + macro.ljust(self._space) + value + '\n'
