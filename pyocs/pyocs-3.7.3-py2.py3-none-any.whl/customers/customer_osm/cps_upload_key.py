import logging
import os
import re
import time
import platform
import mimetypes
import requests
from requests_toolbelt import MultipartEncoder
from bs4 import BeautifulSoup
from lxml import etree

from pyocs.cps_login import CpsLogin
from pyocs.pyocs_logger import PyocsLogger

"""
# @author:ludaijun
# @作用：上传HDCPkey至CPS
# @className：PyocsSoftware
"""


class CpsUploadKey:
    _burn_key_base_link = 'http://cps.cvte.com/tv/BurnKeys'  # cps上传key的基础页面
    _key_view_url_prefix = 'http://cps.cvte.com/tv/BurnKeyTypes/view/'  # cps某一个仓库信息的页面
    _upload_key_url_prefix = _burn_key_base_link + "/import/"  # cps上传key的前缀地址，加上仓库ID之后就是具体某一个仓库的上传地址
    alert_msg = ""
    email_receiver = ""
    warehouse_id = 0
    upload_file_failed_count = 1
    _logger = ""

    def __init__(self, account):
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            folder_path = home_dir + "/upload_log"
        else:
            folder_path = os.getcwd() + "/../upload_log"

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        log_file_name = folder_path + "/" + time.strftime('%Y_%m', time.localtime(time.time())) + ".log"
        self._logger = PyocsLogger(name="CPS_UPLOAD_KEY", log_file_path=log_file_name).getPyocsLogger()

        self._logger.setLevel(level=logging.WARN)
        self._cookies = CpsLogin().get_login_cookies(account_path=account)


    @staticmethod
    def get_content_type(file_path):
        return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    # 设置邮件接收人，将每一个仓库信息页面的仓库所有人的邮箱作为邮件接收人
    def set_alert_message_receiver(self, warehouse_id):
        receiver = ""
        headers = dict()
        headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
        })

        key_view_session = requests.get(url=self._key_view_url_prefix + warehouse_id, cookies=self._cookies,
                                        allow_redirects=False, headers=headers)
        soup = BeautifulSoup(key_view_session.text, features="lxml")
        info_table = soup.find_all('td')
        email_end = "@cvte.com"
        for table_node in info_table:
            if email_end in str(table_node.string):
                receiver = table_node.string
        self._logger.info("warehouse user email(receiver): " + receiver)
        self.email_receiver = receiver

    # 上传单一key包
    def upload_key_to_cps(self, warehouse_id, zip_file_path, file_name):
        """
        根据warehouse_id 和key package path， 上传软件
        Args:
            warehouse_id: 仓库ID
            zip_file_path: key包地址

        Returns:
            成功则返回为True
        """

        encoded_key_package_name = 'key_package_name'  # 此举是为了解决中文的问题，MultipartEncoder 存在中文方面的BUG

        data_fields = dict()
        data_fields.update({
            'data[Upload][file]': (encoded_key_package_name,
                                   open(zip_file_path, 'rb'), self.get_content_type(zip_file_path)),
            'data[Upload][is_check_key_name]': '1',
            'data[Upload][is_check_key_ksv]': '1',
        }
        )

        data = MultipartEncoder(
            fields=data_fields
        )

        data_str = data.to_string()
        data_str = data_str.replace(encoded_key_package_name.encode('utf-8'),
                                    os.path.basename(zip_file_path).encode('utf-8'))
        self._logger.info("data_str: " + str(data_str))

        headers = dict()
        headers.update({
            'Referer': self._upload_key_url_prefix + warehouse_id
        })
        headers['Content-Type'] = data.content_type
        self._logger.info(headers)

        self._logger.info(self._cookies)

        ret = requests.post(self._upload_key_url_prefix + warehouse_id, data=data_str,
                            cookies=self._cookies, allow_redirects=False, headers=headers)

        self._logger.info("url: " + ret.url)
        self._logger.info("headers: " + str(ret.headers))
        self._logger.info(ret.status_code)

        # 上传文件之后，判断返回状态，若返回异常，设置提醒消息及邮件接收者
        self._logger.warning("Upload <" + file_name + "> return status: " + str(ret.status_code))
        if ret.status_code == 200:
            if len(self.alert_msg) == 0:
                self.set_alert_message_receiver(warehouse_id=warehouse_id)

            html = etree.HTML(ret.text)
            alert_msg = html.xpath('//*[@id="main"]/div/h2/text()')[0]
            alert_msg = "第" + str(
                self.upload_file_failed_count) + "个上传错误的压缩包信息， <" + file_name + "> " + alert_msg + "              "
            self.alert_msg = self.alert_msg + alert_msg
            self.upload_file_failed_count = self.upload_file_failed_count + 1
            #self._logger.warning(" alert_msg:" + self.alert_msg)

        return ret.status_code == 302

    def check_warehouse_id(self, warehouse_id, key_folder_path):
        self._logger.warning("上传的仓库ID： " + warehouse_id + ", key目录路径： <" + key_folder_path + "> ")
        find_warehouse_id = re.findall(re.compile(r'[\[|\【](.+?)[\]|\】]', re.S), key_folder_path)
        if len(find_warehouse_id):
            folder_path_warehouse_id = find_warehouse_id[0]
            if folder_path_warehouse_id != warehouse_id:
                self.alert_msg = "error: 填写的仓库ID和文件夹名称上的不一致！！"
                return False
        else:
            self.alert_msg = "error: 文件夹名称中没有仓库ID，不能确认仓库ID是正确!!!"
            return False

        return True


    # 上传某一路径下的多个key包
    def upload_key_to_cps_multiple(self, warehouse_id, key_folder_path):
        if self._cookies is None:
            self.alert_msg = "error: 登陆CPS失败!!!"
            return False

        self.warehouse_id = warehouse_id
        ret = True
        is_file_exists = False
        count_uploaded_keys = 0

        check_ret = self.check_warehouse_id(warehouse_id, key_folder_path)
        if not check_ret:
            return False

        for key_file_name in os.listdir(key_folder_path):
            file_path = os.path.join(key_folder_path, key_file_name)
            if os.path.isfile(file_path):
                self._logger.info("key_file_name: " + key_file_name)
                cps_id_string = re.findall(re.compile(r'ID_(.+?)_C', re.S), key_file_name)
                if cps_id_string and (cps_id_string[0] == warehouse_id):
                    is_file_exists = True

                    # 每上传50K的数据之后， 延时10秒之后再上传
                    if count_uploaded_keys >= 50000:
                        count_uploaded_keys = 0
                        time.sleep(10)

                    sub_ret = self.upload_key_to_cps(warehouse_id=warehouse_id, zip_file_path=file_path, file_name=key_file_name)
                    if not sub_ret:
                        ret = sub_ret
                    else:
                        self._logger.warning("<" + key_file_name + "> 上传成功！！")
                        try:
                            key_count_string = re.findall(re.compile(r'C_(.+?)_B', re.S), key_file_name)
                            if key_count_string:
                                count_uploaded_keys = count_uploaded_keys + int(key_count_string[0])
                        except Exception:
                            self._logger.warning("error key file name format")
                            continue
                else:
                    self._logger.warning("<" + key_file_name + "> There is a wrong warehouse id in file name")
                    continue

        if not is_file_exists:
            ret = False
            self.alert_msg = "没有key压缩包文件!!! \n\n"

        if ret:
            self._logger.warning("所有key均上传成功！！\n\n\n")

        return ret

    # 获取异常信息
    def get_alert_msg(self):
        if self._cookies is not None:
            self.alert_msg = r"From warehouse " + str(self.warehouse_id) + " return message: " + self.alert_msg
            self._logger.warning(self.alert_msg + "\n\n\n")
        return self.alert_msg

    # 获取邮件接收人
    def get_email_receiver(self):
        return self.email_receiver
