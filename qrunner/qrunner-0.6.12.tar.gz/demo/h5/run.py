# @Time    : 2022/1/27 13:47
# @Author  : kang.yang@qizhidao.com
# @File    : run.py

import qrunner
from qrunner.utils.config import conf


if __name__ == '__main__':
    # 设置app内置的webview版本、app需要打开webview调试开关（WebView.setWebContentsDebuggingEnabled(true);）
    # 需要参考淘宝镜像：https://npm.taobao.org/mirrors/chromedriver，不一定有完全一样的，只要前三个版本一样就行
    conf.set_name('app', 'webview', '77.0.3865.40')
    qrunner.main(
        platform='android',
        serial_no='UJK0220521066836',
        pkg_name='com.qizhidao.clientapp',
    )

'''
:param platform: 平台，如browser、android、ios
:param serial_no: 设备id，如UJK0220521066836、00008020-00086434116A002E
:param pkg_name: 应用包名，如com.qizhidao.clientapp、com.qizhidao.company
:param browser_name: 浏览器类型，如chrome、其他暂不支持
:param case_path: 用例路径
:param rerun: 失败重试次数
:param concurrent: 是否需要并发执行，只支持platform为browser的情况
'''
