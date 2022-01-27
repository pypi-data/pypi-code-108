# @Time    : 2022/1/25 20:52
# @Author  : kang.yang@qizhidao.com
# @File    : run.py

import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='browser'
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
