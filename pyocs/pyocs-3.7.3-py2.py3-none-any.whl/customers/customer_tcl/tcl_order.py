from pyocs import tcl_login
from pyocs import pyocs_software
from pyocs import pyocs_demand
from pyocs.pyocs_request import PyocsRequest
import requests
import logging
from urllib.parse import urlencode
from lxml import etree
import pprint
import os
import json
import re
import platform
import pathlib
from customers.customer_tcl import tcl_searchid
from pyocs import pyocs_searchid

from colorama import Fore, Back, Style


class TclOrder(object):
    _logger = logging.getLogger(__name__)
    _tcl = tcl_login.TclLogin()
    _tcl_order_release_url = 'http://scbcrd.tclking.com:8080/oem/dashboard/setajax_odf?'
    _tcl_key_check_url = 'https://cn.uc.qhmoka.com/scbc-server/clientType/getMessage.do'
    _ocs_base_link = 'http://ocs-api.gz.cvte.cn'
    _ocs_sw_search_url = _ocs_base_link + '/tv/Attachments/search_firmwares'
    _key_check_status = True
    _session = requests.Session()

    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self):
        self._logger.setLevel(level=logging.ERROR)
        self._cookies = tcl_login.TclLogin().get_login_cookies()
        self._logger.info(self._cookies)

    def get_html_by_url(self, url):
        r = self._tcl.login_by_cookies(url)
        return r

    def search_sw_status_by_number(self, search_number):
        params = {
            'pagination': 'sw_odf',
            'page': '1',
            'pageOffset': '0',
            'pageLimit': '10',
            'order': 'id',
            'direction': 'DESC',
            'pageSearch': search_number,
        }
        url = self._tcl_order_release_url + urlencode(params)
        try:
            response = self.get_html_by_url(url)
            if response.status_code == 200:
                return response.json()
        except requests.ConnectionError as e:
            print('Error', e.args)

    @staticmethod
    def _parse_sw_status(json_data):
        if json_data:
            items = json_data.get('rows')
            for item in items:
                tcl_order_status = {}
                tcl_order_status['bom'] = item.get('bom')
                tcl_order_status['movement_name'] = item.get('movement_name')
                tcl_order_status['number'] = item.get('number')
                tcl_order_status['pid'] = item.get('pid')
                tcl_order_status['se'] = item.get('se')
                tcl_order_status['status_name'] = item.get('status_name')
                tcl_order_status['supplier_name'] = item.get('supplier_name')
                tcl_order_status['versions'] = item.get('versions')
                return tcl_order_status

    def get_order_key_info_by_tcl_server(self, number, mac='54-E1-AD-43-7C-85'):
        """
        通过TCL服务器以订单编号查询对应的key信息
        :param number:TCL的订单批次号，每个订单唯一区分
        :param version:TCL的软件版本，处理后可以获取区域信息，用于区分key的类型
        :param mac:TCL的服务器查询必须通过报备的MAC，否则无返回数据。暂时先默认一个已经报备过的MAC地址
        :return:返回客户服务器网页Key信息json数据
        """
        header = {
            "Content-Type":"application/json",
            "Host": "cn.uc.qhmoka.com",
            "User-Agent": "PostmanRuntime/7.24.1",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
        }
        post_data = {
            'bid':number,
            'mac':mac
        }
        try:
            response = self._session.post(self._tcl_key_check_url, headers=header, data=json.dumps(post_data))
            if response.status_code == 200:
                return response.json()
        except requests.ConnectionError as e:
            print('Request Error', e.args)

    def get_order_key_info_from_json(self):
        if platform.system() == "Linux":
            home_dir = os.environ["HOME"]
            _program_key_json_file = home_dir + "/program_key_info.json"
        else:
            _program_key_json_file = "program_key_info.json"
        try:
            with open(_program_key_json_file, "r") as kfd:
                program_key_info_json = json.loads(json.dumps(eval(kfd.read())))
                return program_key_info_json
        except FileNotFoundError:
            self._logger.error('KEY检查需要创建program_key_info.json文件！详情可以咨询姜伯炎！')
            return None

    def adjust_order_server_key_info_is_match_need(self, number, pid, version):
        """
        根据订单编号查询TCL服务器上面的key是否与所需求的匹配
        :param number:TCL的订单批次号，每个订单唯一区分
        :param pid:TCL的project id，从释放信息就可以获取
        :param version:TCL的软件版本，处理后可以获取区域信息，用于区分key的类型
        :param mac:TCL的服务器查询必须通过报备的MAC，否则无返回数据
        :return:返回key检查的结果和key的字符串集合，显示到订单备注里面
        """
        search_version = version.split('-')[1]
        key_info_json = self.get_order_key_info_from_json()
        need_key_dict = key_info_json.get(search_version)
        if need_key_dict == None:
            self._key_check_status = False
            return '查询不到对应的key预设信息，请在program_key_info.json文件里面增加！'#这里可以考虑把返回值都定义在一个地方，返回error_code
        server_key_dict = self.get_order_server_key_status(number)
        if len(need_key_dict) != len(server_key_dict):
            self._key_check_status = False
            return '获取到的KEY数量不正确！服务器Key:\n'+str(server_key_dict)+'\n实际需要的Key:\n'+str(need_key_dict)
        for key_index in range(0, len(need_key_dict)):
            if(need_key_dict[key_index].get('name') == server_key_dict[key_index].get('name')) and (need_key_dict[key_index].get('type') == server_key_dict[key_index].get('type')):
                pass
            else:
                self._key_check_status = False
                return '获取到的KEY名称or类型不正确！服务器Key:\n'+str(server_key_dict)+'\n实际需要的key:\n'+str(need_key_dict)
        return '经过查询TCL服务器放置的KEY准确！'

    @staticmethod
    def is_not_sw(sw_name):
        """
        检查是否是正常的软件而非烧录bin或者OTA包
        :param sw_name:
        :return:
        """
        return sw_name.startswith("EMMCBIN") or sw_name.startswith("NANDBIN") or sw_name.startswith("OTA")
    @staticmethod
    def is_need_tcl_key(sw_version):
        """
        检查是否是需要烧录TCL的KEY的订单
        :param sw_version:
        :return:
        """
        return ("MS86" in sw_version) or ("MT659" in sw_version) or ("NT563" in sw_version)

    class Software:
        def __init__(self):
            self.name = ''  # 软件名
            self.attachment_id = ''  # 软件attachment id
            self.fw_id = ''  # 软件fw_id

    def get_sw_status(self, search_number):
        """
        通过客户批号搜索tcl的软件释放状态
        :param search_number: 客户批号;默认值设置为'无'，因为部分ocs订单的客户批号这个值为空，传入空值会导致tcl查询到错误的数据。给i他
        :return: sw状态
        """
        if search_number:
            json_data = self.search_sw_status_by_number(search_number)
            return self._parse_sw_status(json_data)

    def get_order_server_key_status(self, number):
        """
        通过客户批次号在TCL服务器查询此批次订单KEY的信息
        :param number: 客户批次号
        :return: 此批次订单KEY的信息
        """
        if number:
            key_info_server_dict = self.get_order_key_info_by_tcl_server(number)
            return key_info_server_dict.get('obj')

    def get_ocs_status_data(self, customer, engineer) -> dict:
        """
        批量搜索ocs->我的任务，所有待上传软件/待录入需求，返回这些订单的客户批号和ocs号
        :param search_type: 待上传软件/待录入需求
        :return:dict, key:客户批号， value:ocs号
        """
        ocs_status_data = {}
        ts = tcl_searchid.TclSearchid()
        searchid = ts.get_searchid_with_tcl(customer, engineer)
        si = pyocs_searchid.PyocsSearchid(searchid)
        ocs_list = si.get_ocs_id_list_info()
        after_sales_flag = '售后纸箱'
        after_sales_flag2 = '售后,纸箱'
        for ocs_number in ocs_list:
            ocs_title = pyocs_demand.PyocsDemand(ocs_number).get_ocs_title()
            if after_sales_flag in ocs_title:
                wordreg = re.compile(r'售后纸箱(.{10})')#只取售后纸箱字符后面10位字符串
                batch_code = re.search(wordreg,ocs_title).group(1)
            elif after_sales_flag2 in ocs_title:
                wordreg = re.compile(r'售后,纸箱(.{10})')#只取售后纸箱字符后面10位字符串
                batch_code = re.search(wordreg,ocs_title).group(1)
            else:
                batch_code = pyocs_demand.PyocsDemand(ocs_number).get_customer_batch_code()
            add_dict = {
                batch_code: ocs_number
            }
            ocs_status_data.update(add_dict)
        return ocs_status_data

    def get_tcl_sw_version_update_flag(self, ocs_number, tcl_sw_version):
        url = 'http://ocs-api.gz.cvte.cn/tv/TaskComments/get_all_task_comments_json/?order=DESC&task_id=' + ocs_number
        request = PyocsRequest()
        r = request.pyocs_request_get(url)
        comments = json.dumps(r.json())
        flag = not re.search(tcl_sw_version, comments)
        return flag

    def get_comment_message_with_html_format(self, data_dict, relese_sw_list, key_ckeck_msg):
        html_prefix = """
                  <table id="MyList" data-toggle="table" data-show-toggle="false" style="" class="table table-hover table-striped" xpath="1">
                   <thead>
                    <tr>
                     <th style="width: 10%; " data-field="number">
                      <div class="th-inner ">
                       订单编号
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="" data-field="bom">
                      <div class="th-inner ">
                       BOM
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="" data-field="movement_name">
                      <div class="th-inner ">
                       机芯
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="" data-field="versions">
                      <div class="th-inner ">
                       版本
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="width: 70px; " data-field="pid">
                      <div class="th-inner ">
                       PID
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="width: 90px; " data-field="status_name">
                      <div class="th-inner ">
                       发布状态
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="width: 70px; " data-field="supplier_name">
                      <div class="th-inner ">
                       供应商
                      </div>
                      <div class="fht-cell"></div></th>
                     <th style="width: 160px; " data-field="se">
                      <div class="th-inner ">
                       工程师（SE）
                      </div>
                      <div class="fht-cell"></div></th>
                    </tr>
                   </thead>
                   <tbody>
                    <tr data-index="0">
                    """
        html_postfix = """
                    </tr>
                   </tbody>
                  </table>
                    """
        html_number = '<td style="width: 10%; ">' + str(data_dict['number']) + '</td>'
        html_bom = '<td style="">' + str(data_dict['bom']) + '</td>'
        html_movement = '<td style="">' + str(data_dict['movement_name']) + '</td>'
        html_version = '<td style="">' + str(data_dict['versions']) + '</td>'
        html_pid = '<td style="width: 70px; ">' + str(data_dict['pid']) + '</td>'
        html_status_name = '<td style="width: 90px; "><span class="label label-success">' + str(data_dict['status_name']) + '</span></td>'
        html_supplier_name = '<td style="width: 70px; ">' + str(data_dict['supplier_name']) + '</td>'
        html_se = '<td style="width: 160px; ">' + "，".join(str(i) for i in data_dict['se']) + '</td>'
        sw_name_list=""
        for j in relese_sw_list:
            sw_name_list+=j.name + "\n"
        if len(relese_sw_list) > 1:
            html_sw_check = '<b style="width: 160px; color: #ff0000; font-weight: bold;">' + "存在多个同版本（同PID）软件，如下，请确认是否可以删除多余的！\n" + str(sw_name_list) + '</b>'
        elif len(relese_sw_list) == 1:
            html_sw_check = '<b style="width: 160px; color: #00ff00; font-weight: bold;">' + "根据释放版本信息，查询到的唯一满足要求的软件如下，已自动上传软件：\n" + str(sw_name_list) + '</b>'
        elif len(relese_sw_list) == 0:
            html_sw_check = '<b style="width: 160px; color: #ff0000; font-weight: bold;">' + "根据释放版本信息，系统中无法查询到软件！请确认！\n" + '</b>'
        if self._key_check_status:
            html_key_ckeck_msg = '<b style="width: 200px; color: #00ff00; font-weight: bold;">' + str(key_ckeck_msg) + '</b>'
        else:
            html_key_ckeck_msg = '<b style="width: 200px;  color: #ff0000; font-weight: bold;">' + str(key_ckeck_msg) + '</b>' + '<b style="width: 220px;  color: #ff0000; font-weight: bold;">\n如需要重新查询，请取消旗帜并且修改订单状态为非已完成状态！</b>'
        html = html_prefix + html_number + html_bom + html_movement + html_version + html_pid + html_status_name \
               + html_supplier_name + html_se  + html_postfix + html_sw_check + html_key_ckeck_msg
        return html

    def add_comment_and_set_flag_color_and_auto_upload_sw(self, data_dict, ocs_number, color="black"):
        """
        在ocs上添加软件释放状态的信息、设置旗子颜色和自动上传软件
        :param data_dict: tcl网站上的软件状态信息
        :param ocs_number:
        :param color:
        """
        sw = pyocs_software.PyocsSoftware()
        dm = pyocs_demand.PyocsDemand(ocs_number)
        # flag_color = dm.get_flag_color()
        relese_sw_list = list()
        comment_update_flag = self.get_tcl_sw_version_update_flag(ocs_number, data_dict['versions'])
        if comment_update_flag:
            search_str = self.adjust_search_str(data_dict['pid'],data_dict['versions'])
            relese_sw_list = self.get_software_list_from_ocs_sw_search_url_by_sw_info(search_str)
            if self.is_need_tcl_key(data_dict['versions']):
                key_ckeck_msg = self.adjust_order_server_key_info_is_match_need(data_dict['number'],data_dict['pid'],data_dict['versions'])
            else:
                key_ckeck_msg = "不需要客户烧录key"
                self._logger.info("不需要客户烧录key:" + str(data_dict['versions']))
            html = self.get_comment_message_with_html_format(data_dict, relese_sw_list, key_ckeck_msg)
            sw.add_comment_to_ocs(ocs_number, html)
            if len(relese_sw_list) == 1 and self._key_check_status:
                dm.set_flag_color("black")
                sw_name = ""
                for j in relese_sw_list:
                    sw_name += j.name
                sw_lists = sw.find_old_sw_id_by_name(sw_name.strip())
                for sw_list in sw_lists.items():
                    sw_id = sw_list[0]
                    sw_name = sw_list[1]
                    burn_place_hold_type = sw.get_flash_burn_hold_place_from_ocs(ocs_number)
                    if burn_place_hold_type == ' ':
                        burn_place_hold_type = None
                    burn_type = sw.sw_burn_type["离线烧录"]
                    sw.upload_old_sw_by_id(ocs_number, sw_id, burn_place_hold=burn_place_hold_type, burn_type=burn_type, disable_origin_sw=False)
        else:
            pass

    def adjust_search_str(self, str_pid, str_version):
        """
        :param str_pid:传入的PID
        :param str_version:传入的软件版本
        :return: 根据方案特性拼接好的查询字符
        """
        #处理PID，变成三位字符
        if str_pid == "0":
            pid_str = ""
        elif str_pid == "无":
            pid_str = ""
        elif len(str_pid) == 1:
            pid_str = "00"+str_pid+"_"
        elif len(str_pid) == 2:
            pid_str = "0"+str_pid+"_"
        else:
            pid_str = str_pid+"_"
        #处理特殊的软件版本
        if 'MT659' in str_version or 'MT510' in str_version or 'C358' in str_version:
            self._logger.info("MT5659 and MT5510 and MSD358 order no need pid in sw name!")
            return str_version
        else:
            return pid_str+str_version

    def query_my_order_and_set_comment(self, customer, engineer):
        # print('正在搜索' + type[2] + '...... 由于网速等问题，可能搜索过程比较慢，你可以稍后再回来查看 :)')
        data = self.get_ocs_status_data(customer, engineer)   # 从ocs获取我的任务中，待上传软件/代录入需求的订单及客户批号
        unreleased_sw = []
        released_sw = []
        tcl_status_list = []
        for number, ocs in data.items():
            tcl_status_list.append(
                self.get_sw_status(number))  # some of the element is none means the sw is not release!
            if not tcl_status_list[-1]:  # 这个元素为空，代表软件未释放
                unreleased_sw.append(ocs)
            else:
                released_sw.append(ocs)
        for sw in tcl_status_list:
            if sw:
                self._logger.info(sw)
                try:
                    self.add_comment_and_set_flag_color_and_auto_upload_sw(sw, data[sw['number']])
                except KeyError:
                    print('遇到一个奇怪的客户批号，此号码无法找到对应的OCS ID，请确认：%s' % sw['number'])

        print("已释放软件：%d个：" % len(released_sw))
        if released_sw:
            ts = tcl_searchid.TclSearchid()
            searchid = ts.get_searchid_with_tcl(customer, engineer)
            print(released_sw)
            print(
                "已上传状态截图和自动上传软件，请登录ocs查看：" + "http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:my/SearchId:" +
                searchid + Fore.WHITE)

        print("未释放软件：%d个：" % len(unreleased_sw))
        print(unreleased_sw) if unreleased_sw else None
        print("Done!")

    def query(self, customer: str, engineer: str):
        self.query_my_order_and_set_comment(customer, engineer)

        print(Fore.GREEN + 'All things done, just close me and enjoy your time:)' + Fore.WHITE)
        if platform.system() == 'Linux':
            pass
        else:
            os.system('pause')

    def get_software_list_from_ocs_sw_search_url_by_sw_info(self, sw_info: str):
        """从OCS搜索软件的页面（http://ocs-api.gz.cvte.cn/tv/Attachments/search_firmwares）搜索软件
        :param: sw_info: 软件名、软件版本号、或者软件名中的部分信息
        :return: 返回搜索到的软件(类型@Software，包含软件名和attachment id)列表，筛除烧录bin，筛除库存重复软件
        """
        software_list = list()
        sw_name_set = set()
        search_form_data = dict()
        search_form_data['_method'] = 'POST'
        search_form_data['AttachmentName'] = sw_info
        search_response = PyocsRequest().pyocs_request_post(self._ocs_sw_search_url, data=search_form_data)
        html = etree.HTML(search_response.text)
        sw_name_str_list = html.xpath('//a[@title="下载软件"]/../../td[@colspan="4"]/text()')
        for idx, sw_name_str in enumerate(sw_name_str_list):
            if self.is_not_sw(sw_name_str):  # 需要剔除bin包
                self._logger.info('剔除的软件包括：'+ str(sw_name_str))
                continue
            sw_name_set.add(sw_name_str)
        self._logger.info("软件名集合：" + str(sw_name_set))
        sw_name_list = list(sw_name_set)
        self._logger.info("软件名集合：" + str(sw_name_list))
        for sw_name in sw_name_list:
            sw = self.Software()
            attachment_xpath_str = '//td[text()="' + sw_name + '"]/..//a[@title="下载软件"]/@href'
            self._logger.info(attachment_xpath_str)
            tmp_attachment_id_list = html.xpath(attachment_xpath_str)
            self._logger.info(tmp_attachment_id_list)
            tmp_list = tmp_attachment_id_list[0].split('/')
            attachment_id = tmp_list[-1]
            sw.name = sw_name
            self._logger.info("软件名：" + sw.name)
            sw.attachment_id = attachment_id
            software_list.append(sw)
        return software_list

# if __name__ == '__main__':
# sw_to_be_uploaded = ['1156191', '#E3B7EB', '状态为 __待上传软件__ 的订单:']
# demand_to_be_confirmed = ['1198900', '#FFF494', '状态为 __待录入需求__ 的订单:']
# query_types = [sw_to_be_uploaded, demand_to_be_confirmed]
# t = TclOrder()
#
# for type in query_types:
#     t.query_my_order_and_set_comment(type)
#
# print('All things done, just close me and enjoy your time:)')
# if platform.system() == 'Linux':
#     pass
# else:
#     os.system('pause')
