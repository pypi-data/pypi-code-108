import jenkins
import sys
from pathlib import Path
import os
from pyocs import pyocs_login
import logging
import pkgutil
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs import pyocs_software
import pprint
import datetime
import time


class PyocsJenkinsStatus:

    server = jenkins.Jenkins

    def __init__(self):
        self.server = self._create_jenkins_server()

    @staticmethod
    # jenkins采用的账号即为域账号，直接利用Pyocs_Login模块中读取json的方式
    def _create_jenkins_server():
        account = pyocs_login.PyocsLogin().get_account_from_json_file()
        server = jenkins.Jenkins('http://tvci.gz.cvte.cn/', username=account['Username'], password=account['Password'],
                                 timeout=30)
        return server

    def progressbar(self,percentage,str1,str2):
        """
        以进度条的形式输出百分比
        :str1:表示 已完成部分 的字符
        :str2:表示 未完成部分 的字符
        :return:
        """
        a = str1 * int(percentage/2)
        b = str2 * (50-int(percentage/2))
        print('\r当前进度：{:^3.0f}%[{}{}]'.format(percentage,a,b),end='')
        print("\n")

    def _get_job_build_list(self,job):
        """
        获取指定job的build list
        :param model_id:
        :return:
        """
        build_info = self.server.get_job_info(job)
        builds_list = build_info['builds']  # 获取job所有的build历史记录
        return builds_list

    def _get_current_base_name(self,cur_dir: str):
        """
        #name:get_current_base_name
        #function:获得当前代码的代码名和分支名
        #return:代码名_B_分支名
        """
        repo_dir = Path(str(cur_dir) + '/.repo')
        repo_file = Path(str(cur_dir) + '/.repo/manifests.git/config')
        url_line = ''
        branch_line = ''
        if repo_dir.exists():
            with open(str(repo_file), 'r') as f:
                for line in f.readlines():
                    if "url" in line:
                        url_line = line  # 获得当前代码名所在行
                    if "merge" in line:
                        branch_line = line   # 获得当前代码分支所在行
            split_list = url_line.split('/')
            project_name = split_list[-3]
            split_list = branch_line.split(' = ')
            branch_name = split_list[1].strip()
            #code_name = project_name.upper()+'_B_'+branch_name  # (大写)代码名_B_(小写)分支名
            #logging.info(code_name)
            return project_name, branch_name
        else:
            print("此目录非repo仓库，请移步代码仓库的根目录下执行")

    def _get_jenkins_build_list(self):
        build_list = []
        jobs = self.server.get_all_jobs()
        # jobs = server.get_jobs(5)
        for job in jobs:
            if(('CLOUD_BUILD' in job['fullname']) & ('CB_S_' in job['fullname'])):
                build_list.append(job['fullname'])
        return build_list


    def _get_jenkins_project_name(self, project: str, branch: str):
        special_jenkins_project_name={
        'HISI350':'HISI35X'
        }
        build_list = self._get_jenkins_build_list()
        for build_job in build_list:
            build_name = build_job.split('/')[-1]
            branch_name = build_name.split('_B_')[-1]
            project_name = build_name.split('_B_')[0].split('S_')[-1]
            if project in special_jenkins_project_name:
                project = special_jenkins_project_name[project]
            if project == project_name and branch == branch_name:
                return build_job
        return ""

    def _get_build_number_by_model_id(self,project_name,model_id):
        """
        从指定job中查找指定model ID，并返回build number
        :param model_id:
        :return:
        """
        current_job_build_list = self._get_job_build_list(project_name)
        current_job_build_list_len = len(current_job_build_list)

        if current_job_build_list_len > 0 :
            check_times = 20 if current_job_build_list_len > 20 else current_job_build_list_len
            for i in range(check_times):#len(current_job_build_list)
                build_number = current_job_build_list[i]['number']
                build_id_info = self.server.get_build_info(project_name, build_number)
                for dict in build_id_info['actions']:
                    if 'parameters' in dict:
                        get_model_id_by_build_info = dict['parameters'][1]['value']
                        # print(get_model_id_by_build_info)
                        ocs_id = get_model_id_by_build_info.split('_',1)[0]
                    # print(ocs_id)
                        if ocs_id.find(model_id) != -1:
                            # print(ocs_id)
                            return build_number
                        else:
                            continue
        else:
            print("jenkins 无编译任务，请确认")
            os.sys.exit(1)

        print("未查询到此model ID的编译信息，请确认信息是否有误")
        os.sys.exit(1)

    def _get_build_status_param(self,project_name, model_id):
        """
        从指定job中查找指定model ID，并返回具体编译信息
        :param project_name,model_id:
        :return:
        """
        build_number = self._get_build_number_by_model_id(project_name,model_id)
        build_id_info = self.server.get_build_info(project_name, build_number)

        lastStableBuild_number =  self.server.get_job_info(project_name)['lastStableBuild']['number']
        lastStableBuild_info   = self.server.get_build_info(project_name, lastStableBuild_number)

        build_status_dict = {
            'build_result':'',
            'build_start_timestamp' : '',
            'build_end_estimated_time' : '',
            'estimated_duration_timestamp' : 0,
        }

        compile_param_dict = {
            'CUSTOMER_ID': 'CUSTOMER_CVTE',
            'MODEL_ID': '',
            'TEST_TYPE': 'N',
            'UPLOAD_OCS_MSG_0': 'update software',
            'AUTO_MAKE_BIN': '',
            'BUILD_NUMBER': ''
        }

        build_status_dict['build_result']                 = build_id_info['result']
        build_status_dict['build_start_timestamp']        = build_id_info['timestamp']
        #获取上一次稳定构建所需时间作为当前构建的预估时间,多加了5分钟
        build_status_dict['estimated_duration_timestamp'] = lastStableBuild_info['duration']+ datetime.timedelta(minutes=5).seconds*1000

        for dict in build_id_info['actions']:
            if 'parameters' in dict:
                compile_param_dict['CUSTOMER_ID']       = dict['parameters'][0]['value']
                compile_param_dict['MODEL_ID']          = dict['parameters'][1]['value']
                compile_param_dict['TEST_TYPE']         = dict['parameters'][5]['value']
                compile_param_dict['UPLOAD_OCS_MSG_0']  = dict['parameters'][6]['value']
                compile_param_dict['AUTO_MAKE_BIN']     = dict['parameters'][11]['value']   
                compile_param_dict['BUILD_NUMBER']      = build_number
        return  build_status_dict,compile_param_dict

    def _get_build_log(self,project_name,build_number):
        project,jenkins_project_name = project_name.split('/')[1:3]
        logLink = 'http://tvci.gz.cvte.cn/job/CLOUD_BUILD/job/' + project + '/job/' + jenkins_project_name + '/'+ '%d'%build_number + '/console'
        # print("logLink:%s\n"%logLink)
        return logLink


    def _get_sw_download(self,project_name,build_number):
        console_output = self.server.get_build_console_output(project_name,build_number)

        beging_index = console_output.rfind('swName')
        end_index = console_output.find(',',beging_index)
        
        swName = console_output[beging_index+7:end_index]
        # print("beging_index:%d,\nend_index:%d,\nswName:%s\n"% (beging_index,end_index,swName))

        result = pyocs_software.PyocsSoftware().get_refresh_software_download_link_by_sw_info(swName)
        if not result:
            return ""
        else:
            return result


    def require_jenkins_build_status(self, model_id):
        code_root_dir = PyocsFileSystem.get_current_code_root_dir()
        project, branch = self._get_current_base_name(cur_dir=code_root_dir)
        project_name = self._get_jenkins_project_name(project=project, branch=branch)
        # project_name = 'CLOUD_BUILD/MTK5510/CB_S_MTK5510_B_fae_eu'#'CLOUD_BUILD/V56/CB_S_V56_B_fae'
        
        build_status_dict,compile_param_dict = self._get_build_status_param(project_name,model_id)

        build_result = build_status_dict['build_result']
        build_start_timestamp = build_status_dict['build_start_timestamp']
        build_end_estimated_time = build_status_dict['build_end_estimated_time']
        estimated_duration_timestamp = build_status_dict['estimated_duration_timestamp']

        now_timestamp = int(round(time.time() * 1000))
        build_end_estimated_timestamp = build_start_timestamp + estimated_duration_timestamp
        builded_timestamp = now_timestamp - build_start_timestamp
        build_percentage = int((builded_timestamp/estimated_duration_timestamp)*100)

        if build_percentage > 100:
            build_percentage = 100

        build_start_time = time.strftime("%H:%M:%S", time.localtime(build_start_timestamp/1000))
        build_end_estimated_time = time.strftime("%H:%M:%S", time.localtime(build_end_estimated_timestamp/1000))
        build_remaining_time_minutes = datetime.timedelta(milliseconds=(build_end_estimated_timestamp - now_timestamp)).seconds/60

        print("\r查询结果如下：")
        print("=======================================")
        if build_result == "FAILURE" or build_result == "ABORTED":
            logLink = self._get_build_log(project_name,compile_param_dict['BUILD_NUMBER'])

            print("编译失败")
            print("具体原因查看：%s\n"%logLink)

        elif build_result == "SUCCESS" or build_result == "UNSTABLE":
            result = self._get_sw_download(project_name,compile_param_dict['BUILD_NUMBER'])

            print("编译完成，软件包名及下载链接如下：")
            if result != "":
                for sw_download in result:
                    print("软件包名：" + sw_download.name)
                    print("下载链接：" + sw_download.download_link + " 有效截止时间：" + sw_download.deadline + "\n")

        else:
            print("编译开始时间：%s"%build_start_time)

            if builded_timestamp > estimated_duration_timestamp:
                print("编译预计结束时间：本次编译时间超过以往平均编译时间，编译时间无法预估")
            else:
                print("编译预计结束时间：%s"%build_end_estimated_time)
                print("剩余所需时间：%d 分钟"%build_remaining_time_minutes)
                self.progressbar(build_percentage,'*','.')

        pp = pprint.PrettyPrinter(indent=4)
        print("构建参数如下：")
        print("=======================================")
        pp.pprint(compile_param_dict)
        print("=======================================")
