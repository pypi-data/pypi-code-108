#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_
# order by taolei
import os
import time
import unittest
from operate import yamlPage
from HTest import HTMLTestRunner, get_yaml

TEST_REPORT = os.path.join(get_yaml().get('BASE_DIR'), "report")


# 加载所在目录下py文件
def add_case_py(test_path=os.getcwd(), result=True):
    discover = unittest.defaultTestLoader.discover(test_path, pattern='test*.py')
    if result:
        return discover
    else:
        pass


# 加载yaml格式的测试用例
def add_case_yaml():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(yamlPage))
    return suite


def run_case(case):
    now = time.strftime("%Y%m%d%H%M%S")
    filename = TEST_REPORT + '/' + now + '.html'
    fp = open(filename, 'w', encoding='utf-8')
    runner = HTMLTestRunner(stream=fp, title='自动化测试报告', description='运行环境：Linux deepin， 浏览器：Chrome',
                            verbosity=2, tester='Tao lei')
    runner.run(case)


class Run_all(unittest.TestCase):
    def test_all(self):
        self.caseUI = add_case_py()
        self.case2 = add_case_yaml()
        run_case(self.caseUI)
        run_case(self.case2)


if __name__ == '__main__':
    unittest.main()
