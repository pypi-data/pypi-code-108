#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_

from .runner import Runner
from .HTMLTestRunner import HTMLTestRunner
from .basepage import BasePage
from .loader import Loader
from .get_excel import Getexcel
from .get_yaml import get_yaml, write_yaml, clear_yaml
from .testcase import get_data
from .send_email import send_email
from .new_report import new_report


__all__ = ['BasePage', 'Loader', 'Runner', 'new_report', 'Getexcel', 'get_data',
           'HTMLTestRunner', 'send_email', 'get_yaml', 'write_yaml', 'clear_yaml']

# Expose obsolete functions for backwards compatibility


__all__.extend(['find_test_method'])
