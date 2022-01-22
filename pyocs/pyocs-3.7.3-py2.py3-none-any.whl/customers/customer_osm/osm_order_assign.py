import logging
import xlrd
import os
import platform
import json
from pathlib import Path
from pyocs import pyocs_demand
from pyocs import pyocs_software
from pyocs import pyocs_list
from pyocs import pyocs_searchid
from pyocs import pyocs_confluence
from pyocs.pyocs_filesystem import PyocsFileSystem
from string import digits
from customers.customer_osm import osm_searchid
from customers.customer_common.common_database import commonDataBase
"""
# @author: chenfan3714
# @作用：OCS订单自动分配功能
# @className: OsmOrderAssign
"""


class OsmOrderAssign:
    """自动分配订单对应流程负责人：软件审核人员、软件跟踪人员"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        workspace = '/'
        self._logger.setLevel(level=logging.WARN)  # 控制打印级别
        self.__ID_TV_HFCH_COMMON = '1'
        self.__ID_TV_HFCH_CHANGJIA = '11'
        self.__ID_TV_HFCH_HUIDI = '12'
        self.__ID_POWER_COMMON = '2'
        self.__ID_TV_HISENSE_COMMON = '3'
        self.__ID_TV_HISENSE_MS6683 = '31'
        self.__ID_XMB_COMMON = '4'
        self.__ID_SR_COMMON = '5'
		
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            self.workspace = home_dir + workspace
            self._logger.info("linux环境")
        else:
            self.workspace = workspace
            self._logger.info("windows环境")
        self.file_path = self.workspace + '/OSM订单分配规则表.xlsx'

    def get_distribute_rule_sheet(self):
        file = Path(self.file_path)
        # 如果文件不存在，下载文件
        if file.exists() is False:
            db = commonDataBase()
            map_list = db.get_osm_distribute_mapping_info_by_user("OSM订单分配规则表")
            download_link = map_list[0]
            PyocsFileSystem.get_file_from_nut_driver(download_link, self.workspace)
        wb = xlrd.open_workbook(filename=file)
        table = wb.sheets()[0]
        return table

    def get_id_list_by_excel(self):
        root_id_list = list()
        table = self.get_distribute_rule_sheet()
        nrows = table.nrows
        for i in range(1, nrows - 1):
            all_data = table.row_values(i)
            result = all_data[0]
            root_id_list.append(round(result))

        label = root_id_list
        root_id_list = [str(i) for i in label]
        # 去重不改变顺序
        id_list = list(set(root_id_list))
        id_list.sort(key=root_id_list.index)
        return id_list

    def get_assigner_by_id_and_rule(self, id, attr_str):
        assigner = ''
        sheet = self.get_distribute_rule_sheet()
        nrows = sheet.nrows

        for i in range(1, nrows):
            if (sheet.row(i)[0].value == int(id)):
                rule_list = str(sheet.row(i)[2].value).split(';')
                for rule in rule_list:
                    if id == '1':
                        if rule == attr_str:
                            assigner = sheet.row(i)[3].value
                            assigner = str(assigner)
                            return assigner
                    else:
                        if sheet.row(i)[1].value == "项目组":
                            if rule == attr_str:
                                assigner = sheet.row(i)[3].value
                                assigner = str(assigner)
                                return assigner
                        else:
                            if rule in attr_str:
                                assigner = sheet.row(i)[3].value
                                assigner = str(assigner)
                                return assigner
        return assigner

    def get_id_and_attr_dict(self):
        """获取id和Attribute映射关系
        Args:
            None
        Returns:
            返回id和Attribute映射关系，类型为dict
        """
        root_id_list = list()
        root_attr_list = list()
        table = self.get_distribute_rule_sheet()
        nrows = table.nrows
        for i in range(1, nrows):
            all_data = table.row_values(i)
            result_id = all_data[0]
            result_attr = all_data[1]
            root_id_list.append(round(result_id))
            root_attr_list.append(result_attr)
        root_id_list = [str(i) for i in root_id_list]
        id_attr_dict = dict(zip(root_id_list, root_attr_list))
        return id_attr_dict

    def get_searchid_from_id(self, id):
        """从id获取searchid
        Args:
            None
        Returns:
            返回Searchid
        """
        sw = osm_searchid.OsmSearchid()
        if id == self.__ID_TV_HFCH_COMMON:
            searchid = sw.get_ocs_assign_searchid_type1()
        elif id == self.__ID_TV_HFCH_CHANGJIA:
            searchid = sw.get_ocs_assign_searchid_type11()
        elif id == self.__ID_TV_HFCH_HUIDI:
            searchid = sw.get_ocs_assign_searchid_type12()
        elif id == self.__ID_POWER_COMMON:
            searchid = sw.get_ocs_assign_searchid_type2()
        elif id == self.__ID_TV_HISENSE_MS6683:
            searchid = sw.get_ocs_assign_searchid_type31()
        elif id == self.__ID_XMB_COMMON:
            searchid = sw.get_ocs_assign_searchid_type4()
        elif id == self.__ID_SR_COMMON:
            searchid = sw.get_ocs_assign_searchid_type5()
        else:
            print("请添加id=%s的动态获取searchid的方法！" %(id))
        return searchid

    def get_order_info_by_ocs_and_id(self, ocs, id):
        """获取订单ocs的关键信息
        Args:
            ocs: 订单ocs号
            id: 过滤器id
        Returns:
            返回订单ocs在id映射的分配属性信息，类型为字符串
        """
        id_attr_dict = self.get_id_and_attr_dict()
        attr = id_attr_dict[str(id)]
        demand = pyocs_demand.PyocsDemand(ocs)
        if "产品型号" == attr:
            order_info = demand.get_product_name()
        elif "项目组" == attr:
            order_info = demand.get_ocs_project_name()
        elif "默认区域" == attr:
            order_info = demand.get_region_name()
        elif "FlashSize" == attr:
            order_info = demand.get_flash_size()
        elif "客户机型" in attr:
            order_info = demand.get_customer_machine()
            if 'F4' in attr:
                order_info = order_info[0:4]
        elif "客户批号" in attr:
            order_info = demand.get_customer_batch_code()
            if 'F3' in attr:
                order_info = order_info[0:2]
            if "L1" in attr:
                order_info = order_info[-1:]
            if "L2" in attr:
                order_info = order_info[-2:]
        elif "OCS订单标题" in attr:
            order_info = demand.get_ocs_title()
            order_info_list = order_info.split('，')
            if "F0" in attr:
                order_info = order_info_list[0]
            if 'F1L1' in attr:
                order_info = order_info_list[1][-1:]
            if "F1L2" in attr:
                order_info = order_info_list[1][-2:]
            if "L1L1" in attr:
                order_info = order_info_list[-1][-1:]
            if "L1L2" in attr:
                order_info = order_info_list[-1][-2:]
        elif "摘要" in attr:
            order_info = demand.get_ocs_title()
            if '，' in order_info:
                order_info = order_info.split('，')
                if "F0" in attr:
                    order_info = order_info[0]
                elif "L1" in attr:
                    order_info = order_info[-1]
                elif "L2" in attr:
                    order_info = order_info[-2]
                else:
                    order_info = str(order_info)
        elif "根据id分配" in attr:
            order_info = "根据id分配"
        elif "分支量产状态" in attr:
            branch_info = demand.get_sw_branch_path()
            order_info_list = branch_info.split('#') if branch_info else ""
            order_info = order_info_list[1] if order_info_list else ""
        elif "OS 系统" == attr:
            order_info = demand.get_os_system()
        else:
            order_info = ''
        return order_info

    def set_ocs_assigner(self, id='ALL'):
        try:
            ocs_sum = 0
            id_list = list()
            ocs_attr_fail_list = list()
            ocs_rule_fail_list = list()
            ocs_dist_fail_list = list()
            ocs_dist_success_list = list()

            sw = pyocs_software.PyocsSoftware()
            if id == 'ALL':
                id_list = self.get_id_list_by_excel()
            else:
                id_list.append(str(id))

            # 循环遍历所有的 id
            for id in id_list:
                # 根据id获取searchid
                searchid = self.get_searchid_from_id(id)
                # 获取当前 search id 过滤器的订单列表 ocs list
                si = pyocs_searchid.PyocsSearchid(searchid)
                ocs_list = si.get_ocs_id_list_info()
                ocs_number = si.get_searchid_ocs_number()
                ocs_sum += ocs_number
                # 当前 searchid 没有订单，跳出本次循环
                if 0 == ocs_number:
                    continue
                # 循环遍历所有的 ocs id
                for ocs in ocs_list:
                    ocs_request = pyocs_demand.PyocsDemand(ocs)
                    if ocs_request.get_task_type() == "虚拟软件任务":
                        continue
                    # 根据 ocs 和 id 获取相应的订单属性信息
                    order_info_str = self.get_order_info_by_ocs_and_id(ocs, id)
                    if '' == order_info_str:
                        ocs_attr_fail_list.append(ocs)
                        continue
                    # 根据 id 和 order_info_str 获取需要表格对应的 assigner
                    assigner = self.get_assigner_by_id_and_rule(id, order_info_str)
                    if '' == assigner:  # 缺少分配规则
                        ocs_rule_fail_list.append(ocs)
                        continue
                    else:
                        assigner_dict = json.loads(assigner)
                        eng_user = assigner_dict['ENG']
                        aud_user = assigner_dict['AUD']
                        if eng_user == '无' and aud_user == '无':
                            ocs_rule_fail_list.append(ocs)
                            continue
                        if eng_user != '无':
                            ret1 = sw.set_engineer(ocs, eng_user)
                        else:
                            ret1 = False
                        if aud_user != '无':
                            ret2 = sw.set_sw_audit_user(ocs, aud_user)
                        else:
                            ret2 = False

                        if ret1 or ret2:
                            ocs_dist_success_list.append(ocs)
                        else:
                            ocs_dist_fail_list.append(ocs)
            if 0 == ocs_sum:
                ocs_dist_fail_list = []
        finally:
            file = Path(self.file_path)
            os.remove(file)

        return ocs_attr_fail_list, ocs_rule_fail_list, ocs_dist_fail_list, ocs_dist_success_list

