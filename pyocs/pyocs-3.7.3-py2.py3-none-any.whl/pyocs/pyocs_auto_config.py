import json
import logging
import os
import platform
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs import pyocs_confluence
from pyocs.pyocs_ruler_choose import PyocsRulerChoose
from pyocs.pyocs_demand import PyocsDemand
from pathlib import Path
from pyocs.pyocs_vcs import PyocsVcs
from pyocs.pyocs_interface import UniteInterface
from customers.customer_common.common_database import commonDataBase
import re
import git
from pyocs import pyocs_constant
import os
import portalocker
from pyocs.pyocs_exception import *


class Lock:
    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'w')

        # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock

    def acquire(self):
        portalocker.lock(self.handle, portalocker.LOCK_EX)

    def release(self):
        portalocker.lock(self.handle, portalocker.LOCK_UN)

    def __del__(self):
        self.handle.close()

    # Usage
    """
        try:
        lock = Lock("/tmp/lock_name.tmp")
        lock.acquire()
        # Do important stuff that needs to be synchronized
    
    finally:
        lock.release()
    """


class PyocsAutoConfig:
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        self.db = commonDataBase()
        home_dir = os.environ['HOME']
        self._lock_file = home_dir + '/.autoconf.lock'

    def auto_config_by_ocs(self, ocs_number, test, message, is_make_bin):
        """
        根据ocs订单信息，自动配置
        :param ocs_number:
        :param test:
        :param message:
        :param is_make_bin:
        :return:
        """
        lock = Lock(self._lock_file)
        try:
            lock.acquire()
            ocs_demand = PyocsDemand(ocs_number)
            ruler = PyocsRulerChoose()
            uni = ruler.get_sample_ruler(ocs_demand=ocs_demand)
            ret = self.auto_config(project_name=ocs_demand.get_ocs_project_name(), uni=uni,
                                   test=test, message=message, is_make_bin=is_make_bin)
            return ret
        finally:
            lock.release()

    def get_ruler_for_customer_excel(self, ocs_num, excel_para, workspace):
        ocs_demand = PyocsDemand(ocs_num)
        download_link = self.db.get_download_link_of_dt_by_customer(ocs_demand.get_ocs_customer())
        if download_link:
            excel_file_location = PyocsFileSystem.get_file_from_nut_driver(url=download_link, workspace=workspace)
        else:
            raise RuntimeError('没有获取到此客户的需求表的下载链接，请check')
        self.get_or_update_json_base()
        ruler = PyocsRulerChoose()
        uni = ruler.get_customer_excel_ruler(ocs_demand=ocs_demand, excel_para=excel_para,
                                             excel_file_location=excel_file_location)
        project_name = ocs_demand.get_ocs_project_name()
        return uni, project_name

    def pre_check_for_customer_demand_excel_resource(self, ocs_num, excel_para, workspace):
        uni, project_name = self.get_ruler_for_customer_excel(ocs_num=ocs_num, excel_para=excel_para, workspace=workspace)
        message_dict = uni.resource_check()
        ret = json.dumps(message_dict)
        return ret

    def auto_config_by_excel(self, ocs_num, excel_para, workspace, test, message, is_make_bin):
        # 1、首先在工作目录下下载excel 表格
        uni, project_name = self.get_ruler_for_customer_excel(ocs_num=ocs_num, excel_para=excel_para, workspace=workspace)
        ret = self.auto_config(project_name=project_name, uni=uni,
                               test=test, message=message, is_make_bin=is_make_bin)
        return ret

    @staticmethod
    def get_or_update_json_base():
        remote_git_url = 'git@gitlab.gz.cvte.cn:pyocs/pyocs_map_json.git'
        if platform.system() == "Linux":
            home = Path(os.environ['HOME'])
        else:
            home = Path.home()
        json_base_path = home / pyocs_constant.JSON_BASE_DIR_NAME
        if json_base_path.exists():
            customers_repo = PyocsVcs(json_base_path)
            customers_repo.git_update(branch="master")
        else:
            git.Repo.clone_from(remote_git_url, json_base_path, branch='master')

    def auto_config(self, project_name: str, uni: UniteInterface, test: str, message: str, is_make_bin: str):
        """
        仅用于linux平台下，用于自动配置的flow
        :param project_name:
        :param uni:
        :param test:
        :param message:
        :param is_make_bin:
        :return:
        """
        customer_repo_dir = 'customer_repo'

        branch = uni.get_code_branch()
        android_sys = uni.get_android_system()
        project_name += '_' + android_sys if android_sys else ''
        map_list = self.db.get_code_mapping_info_by_project(project_name)
        code_base_url = map_list[0]
        jenkins_project_url = map_list[1]
        test = uni.get_test_type()
        customer_id = uni.get_customer_id()
        jenkins_project_name = jenkins_project_url + branch

        # 2、获取工作目录
        home = Path(os.environ['HOME'])  # 兼容
        workspace = home / customer_repo_dir / project_name
        if not workspace.exists():
            workspace.mkdir(parents=True)

        branch, baseline_name = self.get_baseline_version(workspace=workspace, branch=branch,
                                                          code_base_url=code_base_url, customer_id=customer_id)
        customers_dir = self.get_customer_base(workspace=workspace, branch=branch, code_base_url=code_base_url)

        # 3、配置代码
        model_config = uni.get_ocs_require()
        model_id = uni.get_ocs_modelid()
        h_file = customers_dir / self.get_h_file_by_customer_id(workspace=customers_dir, customer_id=customer_id)

        # 4、配置代码插入规则指定的头文件
        ret = self.insert_config_to_hfile(customer_hfile_name=h_file, model_id=model_id, model_content=model_config)
        git_dir = customers_dir / '.git'
        if ret and git_dir.exists():
            # 5、提交修改
            git_repo = PyocsVcs(customers_dir)
            git_log = self.create_git_log(customer_id=customer_id, model_id=model_id)
            h_file_relative = h_file.relative_to(str(customers_dir))
            try:
                if re.search('29418/', code_base_url):
                    git_repo.add_commit_gerrit_push(str(h_file_relative), branch, git_log)
                else:
                    git_repo.add_commit_git_push(str(h_file_relative), branch, git_log)
            except:
                raise GitError("代码服务器存在问题")
                

        # 6、用json返回编译参数
        compile_param_dict = {
            'JENKINS_JOB': jenkins_project_name,
            'CUSTOMER_ID': customer_id,
            'MODEL_ID': model_id,
            'BUILD_CMD': 'make ocs',
            'UPLOAD_OCS': 'True',
            'TEST_TYPE': test,
            'UPLOAD_OCS_MSG_0': message,
            'AUTO_MAKE_BIN': is_make_bin,
            'OTA_BASE_BACKUP': 'False'
        }
        if baseline_name:
            compile_param_dict['BASELINE_VERSION'] = baseline_name

        ret = json.dumps(compile_param_dict)
        return ret

    def jdy_auto_config(self, project_name: str, branch_name: str, customerid: str, modelid_name: str, modelid: str, test: str, message: str, is_make_bin: str):
        """
        仅用于linux平台下，用于自动配置的flow
        :param project_name:
        :param uni:
        :param test:
        :param message:
        :param is_make_bin:
        :return:
        """
        customer_repo_dir = 'customer_repo'

        # branch = uni.get_code_branch()
        # android_sys = uni.get_android_system()
        # project_name += '_' + android_sys if android_sys else ''
        map_list = self.db.get_code_mapping_info_by_project(project_name)
        code_base_url = map_list[0]
        jenkins_project_url = map_list[1]
        # test = uni.get_test_type()
        # customer_id = uni.get_customer_id()
        jenkins_project_name = jenkins_project_url + branch_name

        # 2、获取工作目录
        home = Path(os.environ['HOME'])  # 兼容
        workspace = home / customer_repo_dir / project_name
        if not workspace.exists():
            workspace.mkdir(parents=True)

        branch, baseline_name = self.get_baseline_version(workspace=workspace, branch=branch_name,
                                                          code_base_url=code_base_url, customer_id=customerid)
        customers_dir = self.get_customer_base(workspace=workspace, branch=branch, code_base_url=code_base_url)

        # 3、配置代码
        # model_config = uni.get_ocs_require()
        # model_id = uni.get_ocs_modelid()
        h_file = customers_dir / self.get_h_file_by_customer_id(workspace=customers_dir, customer_id=customerid)

        # 4、配置代码插入规则指定的头文件
        ret = self.jdy_insert_config_to_hfile(customer_hfile_name=h_file, model_id=modelid_name, model_content=modelid)
        git_dir = customers_dir / '.git'
        if ret and git_dir.exists():
            # 5、提交修改
            git_repo = PyocsVcs(customers_dir)
            git_log = self.create_git_log(customer_id=customerid, model_id=modelid_name)
            h_file_relative = h_file.relative_to(str(customers_dir))
            try:
                if re.search('29418/', code_base_url):
                    git_repo.add_commit_gerrit_push(str(h_file_relative), branch, git_log)
                else:
                    git_repo.add_commit_git_push(str(h_file_relative), branch, git_log)
            except:
                raise GitError("代码服务器存在问题")

        # 6、用json返回编译参数
        compile_param_dict = {
            'JENKINS_JOB': jenkins_project_name,
            'CUSTOMER_ID': customerid,
            'MODEL_ID': modelid_name,
            'BUILD_CMD': 'make ocs',
            'UPLOAD_OCS': 'True',
            'TEST_TYPE': test,
            'UPLOAD_OCS_MSG_0': message,
            'AUTO_MAKE_BIN': is_make_bin,
            'OTA_BASE_BACKUP': 'False'
        }
        if baseline_name:
            compile_param_dict['BASELINE_VERSION'] = baseline_name

        ret = json.dumps(compile_param_dict)
        return ret

    @staticmethod
    def create_git_log(customer_id, model_id):
        git_log = "[config][" + customer_id + "][" + model_id + "]new sw config\r\n\n" \
                                                           "[what]新建model id\r\n" \
                                                           "[why]客户需求\r\n" \
                                                           "[how]脚本自动生成软件\r\n"
        return git_log

    @staticmethod
    def insert_config_to_hfile(customer_hfile_name: Path, model_id, model_content):
        if not customer_hfile_name.exists():
            raise RuntimeError('头文件没有找到')
        _space = 120
        with open(str(customer_hfile_name), "rb") as f_cus:
            old_file_content_list = f_cus.readlines()
            new_file_content_list = old_file_content_list[:]
            # self._logger.info("文件内容：" + str(old_file_content_list))
            for idx, line in enumerate(old_file_content_list):
                if model_id in str(line):
                    # self._logger.info("此model id 已经配置过，不会新增配置，只会重新发起FAE软件云编译")
                    return False
                if "//model_id_define_end" in str(line):
                    # self._logger.info("插入model id的定义")
                    # self._logger.info("上一行的信息：" + old_file_content_list[idx -1].decode())
                    pre_line_str = ''
                    n = 1
                    while not pre_line_str:
                        pre_line_str = old_file_content_list[idx - n].decode().strip()
                        n += 1
                    pre_model_id_number_str = pre_line_str.split(' ')[-1].strip('\n').strip()
                    pre_model_id_number = pre_model_id_number_str.split('//')[0]
                    if not pre_model_id_number.isdigit():
                        raise RuntimeError('头文件中的model id获取错误')
                    cur_model_id_number = str(int(pre_model_id_number) + 1)
                    # self._logger.info("自动model id : " + model_id)
                    model_id_define_line = "#define " + model_id.ljust(_space) \
                                           + cur_model_id_number + '\n'
                    # self._logger.info("model_id_define_line:" + model_id_define_line)
                    new_file_content_list.insert(idx, model_id_define_line.encode())
                    continue
                if "//model_id_content_end" in str(line):
                    # self._logger.info("插入model id的内容")
                    # self._logger.info("自动配置\n: " + str(model_content))
                    new_file_content_list.insert(idx+1, model_content.encode())
                    continue
        with open(str(customer_hfile_name), "wb") as f_cus:
            f_cus.writelines(new_file_content_list)
        return True

    @staticmethod
    def jdy_insert_config_to_hfile(customer_hfile_name: Path, model_id, model_content):
        if not customer_hfile_name.exists():
            raise RuntimeError('头文件没有找到')
        _space = 120
        with open(str(customer_hfile_name), "rb") as f_cus:
            old_file_content_list = f_cus.readlines()
            new_file_content_list = old_file_content_list[:]
            # self._logger.info("文件内容：" + str(old_file_content_list))
            for idx, line in enumerate(old_file_content_list):
                if model_id in str(line):
                    # self._logger.info("此model id 已经配置过，不会新增配置，只会重新发起FAE软件云编译")
                    return False
                if "//JDY_AUTO_SW_DEFINE_END" in str(line):
                    # self._logger.info("插入model id的定义")
                    # self._logger.info("上一行的信息：" + old_file_content_list[idx -1].decode())
                    pre_line_str = ''
                    n = 1
                    while not pre_line_str:
                        pre_line_str = old_file_content_list[idx - n].decode().strip()
                        n += 1
                    pre_model_id_number_str = pre_line_str.split(' ')[-1].strip('\n').strip()
                    pre_model_id_number = pre_model_id_number_str.split('//')[0]
                    if not pre_model_id_number.isdigit():
                        raise RuntimeError('头文件中的model id获取错误')
                    cur_model_id_number = str(int(pre_model_id_number) + 1)
                    # self._logger.info("自动model id : " + model_id)
                    model_id_define_line = "#define " + model_id.ljust(_space) \
                                           + cur_model_id_number + '\n'
                    # self._logger.info("model_id_define_line:" + model_id_define_line)
                    new_file_content_list.insert(idx, model_id_define_line.encode())
                    continue
                if "//JDY_AUTO_SW_MODEID_END" in str(line):
                    # self._logger.info("插入model id的内容")
                    # self._logger.info("自动配置\n: " + str(model_content))
                    new_file_content_list.insert(idx, model_content.encode())
                    continue
        with open(str(customer_hfile_name), "wb") as f_cus:
            f_cus.writelines(new_file_content_list)
        return True

    @staticmethod
    def get_baseline_version(workspace: Path, branch: str, code_base_url: str, customer_id: str):
        """用于处理基线逻辑，根据分支获取基线分支，原理是维护最新的repo_manifest，从中获取最新的baseline version
        
        :param workspace: 方案工作目录
        :param branch: 方案代码分支
        :param code_base_url: 方案代码路径
        :param customer_id: 方案代码路径
        :return: 基线代码：返回增加基线版本后的分支名,和基线版本 ；非基线代码：返回原分支名，基线版本返回为空
        """""
        os.chdir(str(workspace))
        # 基线逻辑，确认基线版本
        repo_manifest = workspace / 'repo_manifest'
        if repo_manifest.exists():
            repo_manifest_repo = PyocsVcs(repo_manifest)
            repo_manifest_repo.git_checkout(branch=branch)
            repo_manifest_repo.git_update(branch=branch)
        else:
            if 'AMLT962X2/base/customers' in code_base_url:
                repo_manifest_download_cmd = code_base_url.replace('base/customers', 'source/repo_manifest') \
                                             + ' -b ' + branch
            else:
                repo_manifest_download_cmd = code_base_url.replace('base/customers', 'repo_manifest') \
                                             + ' -b ' + branch
            os.system(repo_manifest_download_cmd)
        baseline_version = ''
        baseline_name = None
        hotfix_version = None
        hotfix_name = None

        baseline_version_file = repo_manifest.joinpath('versions/versions.txt')
        if baseline_version_file.exists():
            with baseline_version_file.open() as f:
                lines = f.readlines()
                for line in lines:
                    if line.find('laststable') != -1:
                        baseline_version = line.split(':')[-1].strip('\n').strip().strip('\r')
                        baseline_name = line.strip('\n').strip('\r')
                    if line.find(customer_id) != -1:
                        hotfix_version = line.split(':')[-1].strip('\n').strip().strip('\r')
                        hotfix_name = line.strip('\n').strip('\r')

        if hotfix_version:
            if hotfix_version > baseline_version:
                baseline_version = hotfix_version
                baseline_name = hotfix_name

        code_branch = 'r_' + branch + '_v' + baseline_version if baseline_version else branch
        return code_branch, baseline_name

    @staticmethod
    def get_customer_base(workspace: Path, branch: str, code_base_url: str) -> Path:
        """在工作路径根据代码下载路径和分支获取customer仓库，如果已经存在则拉取到最新

        :param workspace: 方案工作路径
        :param branch: 方案分支
        :param code_base_url: 方案代码下载路径
        :return: PATH路径
        """
        cus_dir_name = code_base_url.split('/')[-1]
        hook = ' && scp -p -P 29418 cvtesqm@tvgit.gz.cvte.cn:hooks/commit-msg customers/.git/hooks'
        os.chdir(str(workspace))
        customers_dir = workspace / cus_dir_name
        if customers_dir.exists():
            # 如果存在，则只需要切换到相应的分支，并且更新代码即可
            customers_repo = PyocsVcs(customers_dir)
            customers_repo.git_checkout(branch=branch)
            customers_repo.git_update(branch=branch)
        else:
            code_download_cmd = code_base_url + ' -b ' + branch + hook
            # 如果不存在，则需要根据配置的命令，下载代码
            os.system(code_download_cmd)
        return customers_dir

    @staticmethod
    def get_h_file_by_customer_id(workspace: Path, customer_id: str):
        """
        根据customer id 获取头文件地址
        :param workspace: 方案工作路径
        :param customer_id: customer id
        :return: 返回相对方案配置工作路径（customers仓库）的相对地址
        """
        os.chdir(str(workspace))
        customer_file = workspace / 'customer/customer.h'
        with open(str(customer_file), "rb") as f_cus:
            file_content_list = f_cus.readlines()
            for idx, line in enumerate(file_content_list):
                if ("IsCustomerID(" + customer_id + ")") in str(line):
                    h_file_idx = idx + 1
                    strs = file_content_list[h_file_idx].split()[-1].decode().strip('"')
                    return "customer/" + strs
            else:
                # nuwa 3.0 之后采用此方式
                cus = customer_id.lower()
                return "customer/" + cus + "/" + cus + '.h'

