import sys
import pytest
from qrunner.utils.log import logger
from qrunner.utils.config import conf


class TestMain(object):
    """
    Support for app and web
    """
    def __init__(self,
                 platform=None,
                 serial_no=None,
                 pkg_name=None,
                 browser_name='chrome',
                 case_path=None,
                 rerun='0',
                 concurrent=False
                 ):
        """
        :param platform: 平台，如browser、android、ios
        :param serial_no: 设备id，如UJK0220521066836、00008020-00086434116A002E
        :param pkg_name: 应用包名，如com.qizhidao.clientapp、com.qizhidao.company
        :param browser_name: 浏览器类型，如chrome、其他暂不支持
        :param case_path: 用例路径
        :param rerun: 失败重试次数
        :param concurrent: 是否需要并发执行，只支持platform为browser的情况
        """

        self.platform = platform
        self.serial_no = serial_no
        self.pkg_name = pkg_name
        self.browser_name = browser_name
        self.case_path = case_path
        if isinstance(rerun, int):
            self.rerun = str(rerun)
        self.rerun = rerun
        self.concurrent = concurrent

        # 将数据写入全局变量
        if self.platform is not None:
            conf.set_name('common', 'platform', self.platform)
        if self.serial_no is not None:
            conf.set_name('app', 'serial_no', self.serial_no)
        if self.pkg_name is not None:
            conf.set_name('app', 'pkg_name', self.pkg_name)
        if self.browser_name is not None:
            conf.set_name('web', 'browser_name', self.browser_name)

        # 执行用例
        logger.info('执行用例')
        logger.info(f'平台: {self.platform}')
        cmd_list = [
            '-sv',
            '--reruns', self.rerun,
            '--alluredir', 'allure-results', '--clean-alluredir',
            '--html=report.html', '--self-contained-html'
        ]
        if self.case_path:
            cmd_list.insert(0, self.case_path)
        if self.concurrent:
            if self.platform == 'browser':
                cmd_list.insert(1, '-n')
                cmd_list.insert(2, 'auto')
                cmd_list.insert(3, '--dist=loadscope')
            else:
                logger.info(f'{self.platform}平台不支持并发执行')
                sys.exit()
        logger.info(cmd_list)
        pytest.main(cmd_list)


main = TestMain


if __name__ == '__main__':
    main()

