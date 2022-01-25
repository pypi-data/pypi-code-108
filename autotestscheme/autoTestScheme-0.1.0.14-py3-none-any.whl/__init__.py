# -*- coding: utf-8 -*-
from . import conf
import traceback
from ._version import __version__
import os
import pytest
from _pytest.compat import NotSetType
from .data import tmp
from .common import constant, config as file, logger, common
from .run import json_name
from .pressure import case, httpBase


def pytest_addoption(parser):
    group = parser.getgroup(json_name, "distributed and subprocess testing")
    group.addoption(
        "--{}".format(json_name),
        action="store",
        help=(
            "provide an identifier shared amongst all workers as the value of "
            "the 'testrun_uid' fixture,\n\n,"
            "if not provided, 'testrun_uid' is filled with a new unique string "
            "on every test run."
        ),
    )


@common.singleton
class A(object):
    run_data = {}


a = A()


def pytest_configure(config):
    uuid = config.option.autoTestScheme
    if uuid is not None:
        _path = os.path.join(constant.RUN_TMP_DIR, uuid, 'case.json')
        a.run_data = file.Json(_path).get_object()
        conf.settings.run.test_env = a.run_data.get('__env')


def pytest_generate_tests(metafunc):
    _file = os.path.basename(metafunc.module.__file__).replace('.py', '')
    _func = metafunc.function.__name__
    conf.settings.run.test_env = a.run_data.get('__env')
    if 'filename' in dir(metafunc.cls):
        _file = metafunc.cls.filename
    if 'data' in metafunc.fixturenames and _file in list(a.run_data.keys()) \
            and _func in list(a.run_data[_file].keys()):
        data = a.run_data[_file][_func]
        _data = []
        for i in range(len(data)):
            _data.append(pytest.param(data[i], marks=pytest.mark.run(order=data[i]['__order'])))
        metafunc.parametrize("data", _data)
    else:
        metafunc.parametrize("data", [])


def pytest_runtest_setup(item):
    param = item.callspec.params.get('data')
    if param != NotSetType.token:
        _id = param.get('id')
        last = param.get('dependent')
        if param.get('last_dependent') is not None:
            last = param.get('last')
        if last is not None:
            item.callspec.params['data']['lastTmp'] = tmp.tmp.get_lastTmp(last)
            item.callspec.params['data']['dpTmp'] = tmp.tmp.get(last)
        if _id is not None:
            tmp.tmp.append_lastTmp(param.get('id'), param)

        logger.info('开始运行用例:{}'.format(param.get('title')))
        logger.info(item.callspec.params.get('data'))
        conf.settings.run.current_env = conf.settings.run.tag_env_list[param['tag']]
        conf.settings.run.current_tag = param['tag']


def pytest_runtest_call(__multicall__):
    """
    打印异常日志到日志文件内
    :param item:
    :return:
    """
    try:
        __multicall__.execute()
    except:
        logger.error(traceback.format_exc())
        raise

