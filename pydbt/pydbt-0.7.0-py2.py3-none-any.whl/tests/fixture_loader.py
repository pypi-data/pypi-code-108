import os
import json
from mock import MagicMock
from dbt.contracts.results import RunResult, SourceFreshnessResult
from dbt.contracts.graph.compiled import CompiledNode, CompiledTestNode


def _load_file(fn):
    basedir = os.path.dirname(os.path.realpath(__file__))
    return json.load(open(os.path.join(basedir, 'fixtures', fn), 'r'))


def _load_freshness_file(fn):
    obj = _load_file(fn)
    return SourceFreshnessResult.from_dict(obj)


def _load_run_file(fn):
    obj = _load_file(fn)
    return RunResult.from_dict(obj)


def _load_test_file(fn):
    obj = _load_file(fn)
    return RunResult.from_dict(obj)


class ResultMock(MagicMock):
    load_snaphot_fixture = _load_run_file('snapshot_result.json')
    load_freshness_fixture = _load_freshness_file('freshness_result.json')
    load_freshness_fixture_warn = _load_freshness_file('freshness_result_warn.json')
    load_freshness_fixture_fail = _load_freshness_file('freshness_result_fail.json')
    load_model_fixture = _load_run_file('model_result.json')
    load_model_fixture_fail = _load_run_file('model_result_fail.json')
    load_test_fixture = _load_test_file('test_result.json')
    load_test_fixture_fail = _load_test_file('test_result_fail.json')
    load_test_fixture_warn = _load_test_file('test_result_warn.json')
