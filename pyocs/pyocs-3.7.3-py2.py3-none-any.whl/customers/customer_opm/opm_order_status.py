import logging
import xlrd
import time
import json
import os
import re
import glob
import platform
from os import path, remove
from pathlib import Path
from pyocs import pyocs_confluence
from pyocs.pyocs_exception import *
from pyocs import pyocs_demand
from pyocs import pyocs_software
from pyocs import pyocs_edit
from pyocs import pyocs_list
from pyocs import pyocs_email
from pyocs import pyocs_confluence
from pyocs import pyocs_searchid
# from pyocs import pyocs_progress_bar
from pyocs.pyocs_filesystem import PyocsFileSystem
import zipfile
import sys
sys.setrecursionlimit(1000000)
"""
# @author: chenfan3714
# @作用：特殊客户订单处理
# @className: SpecialOrderEdit
"""


class OpmOrderStatus:
    """特殊客户订单处理"""
    _logger = logging.getLogger(__name__)
    sender = 'chenfan3714@cvte.com'
    # cc_regular = 'chenfan3714@cvte.com,keyafen@cvte.com'
    subject = '[OSM] 待发放订单自动维护详情报告'

    def __init__(self):
        self._logger.setLevel(level=logging.WARN)  # 控制打印级别

    def get_filter_task_comment_list(self, ocs):
        task_comment_str = ""
        task_comment_list = list()
        ocs_request = pyocs_demand.PyocsDemand(ocs)

        # 获取评论区的信息，以关键信息进行分割；如果不存在关键信息，评论区实际上是不存在判断依据的，直接设置为空，便于后面处理
        try:
            task_comment_str = ocs_request.get_task_comment_area()
            task_comment_str = task_comment_str.replace(' ', '').replace('<br/>', '').replace('<span>', '').replace('<p>', '').replace('<div>', '').replace('parent_id', '').replace('TaskComment', '').replace('update_time', '')        # task_comment_list = task_comment_str.replace(' ', '').replace('<br/>', '').replace('', '').split('user_name')
            task_comment_list = task_comment_str.split('user_name')
        except:
            task_comment_str = ""

        return task_comment_str, task_comment_list

    def get_filter_task_comment_list_spec(self, ocs):
        task_comment_list = list()
        ocs_request = pyocs_demand.PyocsDemand(ocs)
        current_ocs_sw = pyocs_software.PyocsSoftware()
        task_comment_str = ocs_request.get_task_comment_area()
        task_comment_str = task_comment_str.replace(' ', '').replace('<br/>', '').replace('<span>', '').replace('<p>', '').replace('<div>', '').replace('parent_id', '').replace('TaskComment', '')        # task_comment_list = task_comment_str.replace(' ', '').replace('<br/>', '').replace('', '').split('user_name')
        task_comment_list = task_comment_str.split('email_hash')
        return task_comment_str, task_comment_list

    def get_reuse_ocs_test_status(self, ocs):
        ocs_request = pyocs_demand.PyocsDemand(ocs)
        current_ocs_sw = pyocs_software.PyocsSoftware()
        task_comment_str, task_comment_list = self.get_filter_task_comment_list(ocs)
        # 获取启用软件的软件名、测试类型和测试状态
        enable_sw_list = current_ocs_sw.get_enable_software_list(ocs, exclude_bin=0)
        if enable_sw_list:
            if len(enable_sw_list) == 1: # 主板软件或者外挂板软件
                enable_sw_name_str = enable_sw_list[0].name
            elif len(enable_sw_list) == 2: # 主板软件+烧录bin的情况或者主板软件+外挂板软件
                if enable_sw_list[0].name.startswith('CS') or enable_sw_list[0].name.startswith('CP'):
                    enable_sw_name_str = enable_sw_list[0].name
                elif enable_sw_list[1].name.startswith('CS') or enable_sw_list[1].name.startswith('CP'):
                    enable_sw_name_str = enable_sw_list[1].name
                else:
                    return False
            else:
                return False
        else:
            return False
        enable_sw_test_type_str = current_ocs_sw.get_test_type_from_ocs(ocs)
        # enable_sw_test_status_str = current_ocs_sw.get_enable_software_test_status_with_ocs(ocs, exclude_bin=0)
        # 如果软件不需测试或者为空，非引用软件：直接返回False；引用软件：需要查找引用软件的测试状态
        if enable_sw_test_type_str is None:
            return False
        elif "不用测试" in enable_sw_test_type_str:
            return False
        else:
            # 测试类型为A/B/C/D/E/F类等，只取前面两位，用于匹配评论区
            if 'B+C' in enable_sw_test_type_str:
                enable_sw_test_type_str = 'B类'  # B+C类组合测试，评论区只会显示B类通过，测试级别由高向低兼容
            else:
                enable_sw_test_type_str = enable_sw_test_type_str[0:2]
            match_sw_test_info_1 = enable_sw_test_type_str + '测试通过'
            match_sw_test_info_2 = enable_sw_test_type_str + '（代）测试通过'
            match_sw_test_info_3 = enable_sw_test_type_str + '测试完毕不通过'
            match_sw_test_info_4 = enable_sw_name_str + '测试通过'
            match_sw_test_info_5 = enable_sw_name_str + '问题已确认，测试通过'
            if (match_sw_test_info_3 in task_comment_str) and ((match_sw_test_info_4 in task_comment_str) or (match_sw_test_info_5 in task_comment_str)):
                return True
            for signal_comment_str in task_comment_list:
                if enable_sw_name_str in signal_comment_str:
                    if (match_sw_test_info_1 in signal_comment_str) or (match_sw_test_info_2 in signal_comment_str):
                        return True
        return False

    def send_mail_for_exception_ocs(self, ocs, content, type):
        mail = pyocs_email.PyocsEmail()
        ocs_request = pyocs_demand.PyocsDemand(ocs)
        sw = pyocs_software.PyocsSoftware()
        sw_engineer = ocs_request.get_ocs_software_engineer()
        receivers = sw.get_email_addr_from_ocs(sw_engineer)
        # cc = self.cc_regular

        content = content + "\nOCS评论区信息备注规范: https://kb.cvte.com/pages/viewpage.action?pageId=184429623"
        mail.send_email(self.sender, receivers, self.subject, content)

    def get_special_comment_match_state(self, comment_str):
        kb = pyocs_confluence.PyocsConfluence()
        dick = kb.get_kb_table_page_content("184429623")
        value_list = dick.values()
        # 删除list内部的方括号
        comment_list = [ i for item in value_list for i in item]
        for k in comment_list:
            if k in comment_str:
                return True
        return False

    def set_enable_software_finish_test_status(self, ocs_list, status):
        ocs_set_fail_type0_list = list()
        ocs_set_fail_type1_list = list()
        ocs_set_fail_type2_list = list()
        ocs_set_fail_type3_list = list()
        ocs_set_fail_type4_list = list()
        ocs_set_fail_type5_list = list()
        ocs_set_fail_type6_list = list()
        ocs_set_fail_type7_list = list()
        ocs_set_fail_type8_list = list()
        ocs_set_fail_type9_list = list()
        ocs_set_fail_type10_list = list()
        ocs_set_fail_type11_list = list()
        ocs_set_success_list = list()
        ret_status_dict = {}
        _ocs_link_Prefix = 'https://ocs-api.gz.cvte.cn/tv/Tasks/view/'

        for ocs in ocs_list:
            ocs_request = pyocs_demand.PyocsDemand(ocs)
            current_ocs_sw = pyocs_software.PyocsSoftware()
            # 研发专用OCS不做处理
            if "研发专用OCS" in ocs_request.get_ocs_title():
                ocs_set_fail_type11_list.append(ocs)
                continue
            # 首先判断订单状态，如果订单转为已完成，则不用处理
            if ocs_request.get_order_status_type() == "已完成":
                ocs_set_fail_type0_list.append(ocs)
                continue
            if ocs_request.get_ocs_customer() == "CVTE通用产品研发":
                ocs_set_success_list.append(ocs)
                current_ocs_sw.set_ocs_status(ocs, status)
                continue
            if ocs_request.get_ocs_customer() == "视睿":
                ocs_set_fail_type8_list.append(ocs)
                self._logger.info("视睿订单，需提醒")
                content = "视睿订单请确认能否关闭：" + _ocs_link_Prefix + ocs
                self.send_mail_for_exception_ocs(ocs, content, 'type8')
                continue
            task_comment_str, task_comment_list = self.get_filter_task_comment_list(ocs)
            # 特殊评论信息
            if task_comment_str:
                state = self.get_special_comment_match_state(task_comment_str)
                if state:
                    ocs_set_success_list.append(ocs)
                    current_ocs_sw.set_ocs_status(ocs, status)
                    continue

            # 获取启用软件的软件名、测试类型和测试状态
            enable_sw_list = current_ocs_sw.get_enable_software_list(ocs, exclude_bin=0)
            if enable_sw_list:
                if len(enable_sw_list) == 1: # 主板软件(包括CPS软件)或者外挂板软件
                    enable_sw_name_str = enable_sw_list[0].name
                elif len(enable_sw_list) == 2: # 主板软件+烧录bin的情况或者主板软件+外挂板软件
                    if enable_sw_list[0].name.startswith('CS') or enable_sw_list[0].name.startswith('CP'):
                        enable_sw_name_str = enable_sw_list[0].name
                    elif enable_sw_list[1].name.startswith('CS') or enable_sw_list[1].name.startswith('CP'):
                        enable_sw_name_str = enable_sw_list[1].name
                    else:
                        ocs_set_fail_type1_list.append(ocs)
                        self._logger.info("订单启用软件命名不规范，请确认")
                        continue
                else:
                    ocs_set_fail_type2_list.append(ocs)
                    self._logger.info("订单启用软件超过两个，请确认")
                    continue
            else: # 获取启用软件为空，软件被锁定
                if "禁用原因已确认，无需更新软件，可关闭订单" in task_comment_str or "订单评估先行关闭，后续需更新软件再打开" in task_comment_str:
                    ocs_set_success_list.append(ocs)
                    current_ocs_sw.set_ocs_status(ocs, status)
                    continue
                else:
                    ocs_set_fail_type3_list.append(ocs)
                    self._logger.info("获取启用软件为空，可能被锁定，请确认!")
                    content = "如下未自动关闭未解决任务失败订单，原因为 软件已被禁用，请工程师查看对应的订单处理措施：" + _ocs_link_Prefix + ocs + "\n1、软件需更新、需主动OTA--更新软件，安排测试；\n2、软件需更新，如由于客户暂时未提供需求等原因无法更新，建议可先行关闭--评论区备注：客户需求提供时间暂不定，此单可先关闭，后续有需求再重启跟进；\n3、订单措施为自然导入、被动处理、被动OTA–评论区备注：禁用的软件确认无需更新，可关闭订单。"
                    self.send_mail_for_exception_ocs(ocs, content, 'type3')
                    continue
            # 获取当前测试性质/测试级别/测试状态
            enable_sw_test_type_str = current_ocs_sw.get_test_type_from_ocs(ocs)
            enable_sw_test_level_str = current_ocs_sw.get_test_level_from_ocs(ocs)
            enable_sw_test_status_str = current_ocs_sw.get_enable_software_test_status_with_ocs(ocs, exclude_bin=0)

            if '待审核' in enable_sw_test_status_str:
                ocs_set_fail_type6_list.append(ocs)
                current_ocs_sw.set_ocs_status(ocs, 30)
                continue
            elif '待测试' in enable_sw_test_status_str:
                ocs_set_fail_type6_list.append(ocs)
                current_ocs_sw.set_ocs_status(ocs, 50)
                continue
            elif '测试不通过' in enable_sw_test_status_str:
                ocs_set_fail_type6_list.append(ocs)
                current_ocs_sw.set_ocs_status(ocs, 60)
                continue
            # 如果软件不需测试或者未知，非引用软件：直接返回False；引用软件：需要查找引用软件的测试状态
            if "不用测试" in enable_sw_test_type_str or "未知" in enable_sw_test_type_str:
                # 朝野特殊顶单操作
                if 'CY_PYOCS_AUTO_CLOSE_FLAG' in task_comment_str:
                    ocs_set_success_list.append(ocs)
                    current_ocs_sw.set_ocs_status(ocs, status)
                    continue
                if ocs in enable_sw_name_str: # 新软件不做测试，直接返回False
                    if ocs_request.get_ocs_customer() == "朝野":
                        ocs_set_fail_type9_list.append(ocs)
                        content = "此单无法关闭，测试类型是不用测试，是否属于朝野特殊订单，请尽快确认有没有遗漏标记位 CY_PYOCS_AUTO_CLOSE_FLAG ：" + _ocs_link_Prefix + ocs
                        self.send_mail_for_exception_ocs(ocs, content, 'type9')
                        continue
                    if "测试通过" in enable_sw_test_status_str:
                        flag = 0
                        reuse_ocs_list = current_ocs_sw.get_enable_software_reuse_ocs_with_ocs(ocs, exclude_bin=0)
                        for r_ocs in reuse_ocs_list:
                            reuse_ocs_request = pyocs_demand.PyocsDemand(r_ocs)
                            if reuse_ocs_request.get_task_type() != "意向订单任务":
                                reuse_ocs = r_ocs
                                reuse_ocs_test_status = self.get_reuse_ocs_test_status(reuse_ocs)
                                if reuse_ocs_test_status:
                                    flag = 1
                                    ocs_set_success_list.append(ocs)
                                    current_ocs_sw.set_ocs_status(ocs, status)
                                    break
                                else:
                                    continue
                        if flag == 0:
                            self._logger.info("引用库存软件测试不通过，请确认!")
                            ocs_set_fail_type5_list.append(ocs)
                            continue
                    else:
                        ocs_set_fail_type4_list.append(ocs)
                        self._logger.info("新的启用软件没有测试，请确认!")
                        content = "此单无法关闭，新的启用软件没有测试，请确认：" + _ocs_link_Prefix + ocs
                        self.send_mail_for_exception_ocs(ocs, content, 'type4')
                        continue
                else:
                    reuse_ocs_list = list()
                    flag = 0
                    # if 'CP' in enable_sw_name_str:
                    #     pos = enable_sw_name_str.find('CP')
                    #     reuse_ocs = enable_sw_name_str[(pos+2):(pos+8)]
                    # elif 'CS' in enable_sw_name_str:
                    #     pos = enable_sw_name_str.find('CS')
                    #     reuse_ocs = enable_sw_name_str[(pos+2):(pos+8)]
                    reuse_ocs_list = current_ocs_sw.get_enable_software_reuse_ocs_with_ocs(ocs, exclude_bin=0)
                    for r_ocs in reuse_ocs_list:
                        reuse_ocs_request = pyocs_demand.PyocsDemand(r_ocs)
                        if reuse_ocs_request.get_task_type() != "意向订单任务":
                            reuse_ocs = r_ocs
                            reuse_ocs_test_status = self.get_reuse_ocs_test_status(reuse_ocs)
                            if reuse_ocs_test_status:
                                flag = 1
                                ocs_set_success_list.append(ocs)
                                current_ocs_sw.set_ocs_status(ocs, status)
                                break
                            else:
                                continue
                    if flag == 0:
                        self._logger.info("引用库存软件测试不通过，请确认!")
                        ocs_set_fail_type5_list.append(ocs)
                        continue
            else: # 测试类型为A/B/C/D/E/F类等，只取前面两位，用于匹配评论区
                if 'B+C' in enable_sw_test_type_str:
                    enable_sw_test_type_str = 'B类'  # B+C类组合测试，评论区只会显示B类通过，测试级别由高向低兼容
                else:
                    enable_sw_test_type_str = enable_sw_test_type_str[0:2]
                match_sw_test_info_1 = enable_sw_test_type_str + '测试通过'
                match_sw_test_info_2 = enable_sw_test_type_str + '（代）测试通过'
                match_sw_test_info_3 = enable_sw_test_type_str + '测试完毕不通过'
                match_sw_test_info_4 = enable_sw_name_str + '测试通过'
                match_sw_test_info_5 = enable_sw_name_str + '问题已确认，测试通过'
                if (match_sw_test_info_3 in task_comment_str) and ((match_sw_test_info_4 in task_comment_str) or (match_sw_test_info_5 in task_comment_str)):
                    ocs_set_success_list.append(ocs)
                    current_ocs_sw.set_ocs_status(ocs, status)
                    continue
                for signal_comment_str in task_comment_list:
                    if enable_sw_name_str in signal_comment_str:
                        if (match_sw_test_info_1 in signal_comment_str) or (match_sw_test_info_2 in signal_comment_str):
                            ocs_set_success_list.append(ocs)
                            current_ocs_sw.set_ocs_status(ocs, status)
                            break
                        elif 'F类（代）测试通过' in signal_comment_str and enable_sw_test_type_str is not 'F类':
                            ocs_set_fail_type10_list.append(ocs)
                            content = "此单未做终测，是否安排补测，如需安排，改为待测试，提醒测试部安排！" + _ocs_link_Prefix + ocs
                            self.send_mail_for_exception_ocs(ocs, content, 'type10')
                            break

        ret_status_dict = {
            'type0': ocs_set_fail_type0_list if ocs_set_fail_type0_list else '无',
            'type1': ocs_set_fail_type1_list if ocs_set_fail_type1_list else '无',
            'type2': ocs_set_fail_type2_list if ocs_set_fail_type2_list else '无',
            'type3': ocs_set_fail_type3_list if ocs_set_fail_type3_list else '无',
            'type4': ocs_set_fail_type4_list if ocs_set_fail_type4_list else '无',
            'type5': ocs_set_fail_type5_list if ocs_set_fail_type5_list else '无',
            'type6': ocs_set_fail_type6_list if ocs_set_fail_type6_list else '无',
            'type7': ocs_set_fail_type7_list if ocs_set_fail_type7_list else '无',
            'type8': ocs_set_fail_type8_list if ocs_set_fail_type8_list else '无',
            'type9': ocs_set_fail_type9_list if ocs_set_fail_type9_list else '无',
            'type10': ocs_set_fail_type10_list if ocs_set_fail_type10_list else '无',
            'type11': ocs_set_fail_type11_list if ocs_set_fail_type11_list else '无',
            'typex': ocs_set_success_list if ocs_set_success_list else '无'
        }
        return ret_status_dict

    def set_enable_software_finish_test_status_by_comment(self, search_id, status):
        ocs_set_success_list = list()
        si = pyocs_searchid.PyocsSearchid(search_id)
        ocs_list = si.get_ocs_id_list_info()
        if ocs_list:
            for ocs in ocs_list:
                current_ocs_sw = pyocs_software.PyocsSoftware()
                task_comment_str, task_comment_list = self.get_filter_task_comment_list(ocs)
                # 特殊评论信息
                state = self.get_special_comment_match_state(task_comment_str)
                if state:
                    ocs_set_success_list.append(ocs)
                    current_ocs_sw.set_ocs_status(ocs, status)

        ret_status_dict = {
            'type': ocs_set_success_list if ocs_set_success_list else '无'
        }
        return ret_status_dict

    def set_ocs_status_by_ocs_list(self, ocs_list, status):
        ret_status_dict = self.set_enable_software_finish_test_status(ocs_list, status)
        return ret_status_dict

    def set_ocs_status_by_search_id(self, search_id, status):
        ret_status_dict = self.set_enable_software_finish_test_status_by_comment(search_id, status)
        return ret_status_dict

    def set_ocs_tasks_status_by_searchid(self, search_id, status):
        """
            通过search id 获取OCS订单列表，并设置此列表中OCS订单状态
            :param search_id:OCS 过滤器的search id
            :return:对应OCS设置状态是否成功
        """
        ocs_set_success_list = list()
        si = pyocs_searchid.PyocsSearchid(search_id)
        ocs_list = si.get_ocs_id_list_info()
        current_ocs_sw = pyocs_software.PyocsSoftware()
        if ocs_list:
            for ocs in ocs_list:
                ret_set = current_ocs_sw.set_ocs_status(ocs, status)
                if ret_set:
                    ocs_set_success_list.append(ocs)
        ret_status_dict = {
            'type': ocs_set_success_list if ocs_set_success_list else '无'
        }
        return ret_status_dict

    def compress_files(self, path):
            compress_dir_path = path  # 要压缩的文件夹路径
            compress_dir_name = compress_dir_path + '.zip'  # 压缩后文件夹的名字

            z = zipfile.ZipFile(compress_dir_name, 'w', zipfile.ZIP_DEFLATED)
            for dir_path, dir_names, file_names in os.walk(path):
                f_path = dir_path.replace(path, '')  # 这一句很重要，不replace的话，就从根目录开始复制
                f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
                for filename in file_names:
                    z.write(os.path.join(dir_path, filename), f_path + filename)
            z.close()
            return compress_dir_name

    def delfile(self, path):
        fileNames = glob.glob(path + '/*')
        for fileName in fileNames:
            try:
                os.remove( fileName)
            except:
                try:
                    os.rmdir( fileName)
                except:
                    delfile( fileName)
                    os.rmdir( fileName)

    def get_sw_download_link_with_searchid_ocs(self, searchid, ocs_number):
        """根据searchid下载所有ocs的软件，然后上传到指定的ocs作为附件，获取下载link
            workspace: 附件临时存放路径
        """
        sw = pyocs_software.PyocsSoftware()
        ocs_list = pyocs_list.PyocsList()
        ocs_sum, ocs_list = ocs_list.get_ocs_id_list(str(searchid))
        if ocs_sum == 0:
            print("Type - 当前没有需要处理的订单")
        else:
            for ocs_id in ocs_list:
                file_location = sw.get_software_file_from_ocs(ocs_id, self.workspace)
        compress_dir_name = self.compress_files(self.workspace)
        xml_path = re.sub(r'zip|tar', 'xml', compress_dir_name)
        ret = sw.upload_software_to_ocs(ocs_num=ocs_number, zip_path=compress_dir_name,
                                            xml_path=xml_path, test_type='100',
                                            burn_place_hold=' ', burn_type=' ', message='客户软件压缩包')
        result_list = sw.get_download_link_by_ocs(ocs_number)
        if result_list:
            result = result_list[0]
            sw_download_link = result.download_link
            self.delfile(self.workspace)
            os.remove(compress_dir_name)
            return sw_download_link
        else:
            return None

    def get_ocs_comment(self):
        kb = pyocs_confluence.PyocsConfluence()
        ret = kb.get_kb_table_page_content('184429623')
        dict_key_list = list(ret)
        tplt = "{0:<20}\t{1:<40}"
        for i in dict_key_list:
            dict_value = ret[i]
            print(tplt.format(str(i), ' '.join(dict_value), chr(12288)))
