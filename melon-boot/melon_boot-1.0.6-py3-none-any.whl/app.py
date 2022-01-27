# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os
from melon import ROOT_DIR
from melon.settings import get_config

allure_data = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.pytest.allure_dir')))
report_dir = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.allure.report_dir')))
cases_path = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.pytest.cases_dir')))


def run_pytest():
    args = get_config('melon.pytest.args')
    os.system(f'pytest -{"".join(args)} {cases_path} --alluredir {allure_data}')


def run_allure(auto_open):
    os.system(f'allure generate {allure_data} -o {report_dir} --clean')
    if auto_open:
        os.system(f'allure open {report_dir}')


def run(auto_open_report=True):
    run_pytest()

    run_allure(auto_open_report)
