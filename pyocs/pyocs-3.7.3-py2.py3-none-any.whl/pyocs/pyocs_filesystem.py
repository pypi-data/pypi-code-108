import os
from pathlib import Path
import urllib.parse
import requests


class PyocsFileSystem:

    @staticmethod
    def get_current_code_root_dir():
        """获得当前代码的根目录
        Return:
            代码根目录名
        """
        cur_path = os.getcwd()  # 获得当前路径
        if 'customer' in cur_path.split('/')[-1]:
            code_root_dir = os.path.abspath(os.path.pardir)
        else:
            code_root_dir = cur_path
        repo_dir = Path(str(code_root_dir) + '/.repo')
        repo_mnt_dir = Path(str(code_root_dir) + '/code/.repo')
        svn_dir = Path(str(code_root_dir) + '/.svn')
        svn_mnt_dir = Path(str(code_root_dir) + '/code/.svn')
        git_dir = Path(str(code_root_dir) + '/.git')
        git_mnt_dir = Path(str(code_root_dir) + '/code/.git')
        if not code_root_dir.strip():
            raise RuntimeError("获取代码根目录为空")
        if not (repo_dir.exists() or svn_dir.exists() or git_dir.exists()
                or repo_mnt_dir.exists() or svn_mnt_dir.exists() or git_mnt_dir.exists()):
            raise RuntimeError('请在"代码根目录"或者"Customers目录"下执行')
        else:
            return code_root_dir

    @staticmethod
    def get_file_from_nut_driver(url: str, workspace: str):
        res_id = url.split('/')[-1]
        ret = requests.get("https://drive.cvte.com/d/ajax/fileops/pubFileLink?k=" + res_id + "&wm=false&forwin=1")
        download_url = ret.json()['url']
        parse_url = urllib.parse.unquote(download_url)
        file_name = parse_url.split('/')[-1].split('?')[0]
        r = requests.get(url=download_url)
        file_location = os.path.join(workspace, file_name)
        with open(file_location, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return file_location

    @staticmethod
    def get_baseline_version(customer_dir: str, customer_id: str):
        """
        仅用于linux下，利用配置管理封装的 cvt-baseline-versions 的命令获取基线版本号
        :param customer_dir:
        :param customer_id:
        :return:
        """
        os.chdir(customer_dir)
        cvt_baseline_cmd = "cvt-baseline-versions"
        baseline_info = os.popen(cvt_baseline_cmd).read()
        baseline_info_list = baseline_info.split('\n')
        laststable_version = ''
        hotfix_version = ''
        for version in baseline_info_list:
            if not version:
                continue
            pre_name = version.split(':')[0]
            if 'laststable' == pre_name:
                laststable_version = version
            elif customer_id in pre_name:
                hotfix_version = version
        baseline_version = hotfix_version if hotfix_version else laststable_version
        return baseline_version




