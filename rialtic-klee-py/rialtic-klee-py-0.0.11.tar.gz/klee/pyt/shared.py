
from fhir.resources.claim import Claim
from schema.insight_engine_response import InsightEngineResponse, Insight
from typing import List, Tuple

import pytest, re
import datetime as dt
from klee.internal import Structure, log
from klee.cases import InsightEngineTestCase
from klee.files import KleeFile


with KleeFile(Structure.reference.binary, 'rb') as file:
    local_test_cases = file.read_data()
    response_cache = {}

@pytest.mark.parametrize('label, case', local_test_cases.items(), ids=local_test_cases)
class TestEngineV1:
    @pytest.fixture
    def response(self, label, case: InsightEngineTestCase, run_engine) -> InsightEngineResponse:
        log.info("Preparing to run test label %s", label)

        log.debug('Test case billable period: %s', _period(case.request.claim))
        if case.request.history:
            periods = ", ".join(_period(x.claim) for x in case.request.history)
            log.debug('Historic claim periods: %s', periods)

        if label in response_cache:
            return response_cache[label]

        response_cache[label] = run_engine(case)
        return response_cache[label]

    @pytest.fixture
    def expected(self, case: InsightEngineTestCase) -> Insight:
        return case.response.insights[0]

    @pytest.fixture
    def actual(self, label, response: InsightEngineResponse, expected: Insight) -> Insight:
        line, insight = expected.claim_line_sequence_num, None
        # todo: create a ticket on someone's board so this hack isn't needed

        n = len(response.insights)
        log.info('Found %s insights for test label %s', n, label)
        for ix, item in enumerate(response.insights, 1):
            prefix = f">>> Insight {ix} of {n}"
            if item.trace is None:
                item.trace = []

            exits = []
            for trace in item.trace:
                header = f"\n\texit: {trace.end_label}::{trace.tree_name}"
                exits.append(header + _node_path(trace.traversal))

            log.info('%s\n\ttype: %s \n\tpolicy: %s %s \n', prefix, item.type, item.policy_name, "".join(exits))

        for item in response.insights:
            if item.claim_line_sequence_num == line:
                insight = item

        for item in response.insights:
            if item.claim_line_sequence_num == line and \
                    item.trace and item.trace[-1].end_label == label:
                insight = item

        return insight if insight else response.insights[line - 1]

    def test_insight_type(self, actual, expected):
        if actual.type == 'Error' and expected.type != 'Error':
            assert not expected.type, actual.description
        assert actual.type == expected.type

    def test_insight_description(self, actual, expected):
        if not re.search(r"{[^}]+}", expected.description):
            assert actual.description == expected.description
        else:
            assert_parameterized(actual.description, expected.description)

    def test_defense_message(self, actual, expected):
        def read_defense(x):
            msgs = x.defense.script.messages
            return msgs[0].message if msgs else ""

        actual, expected = map(read_defense, (actual, expected))
        # idk whats going on with defense remotely, but im going to view them as nuclear worthy
        normalize, scrub = lambda x: re.sub(r'[\n\r"]', "", x), lambda x: re.sub(r'[\s"]', "", x)

        try:
            assert scrub(actual) == scrub(expected)
            return
        except AssertionError:
            pass

        assert normalize(actual) == normalize(expected)

def assert_parameterized(actual, expected):
    # check for const chunks
    for chunk in re.split("{[^}]+}", expected):
        if chunk not in actual:
            assert actual == expected

    # check for replacement
    escaped = re.escape(expected)
    pattern = re.sub(r'\\{[^\\}]+\\}', "[^{].*", escaped)

    try:
        assert re.fullmatch(pattern, actual)
        return
    except AssertionError:
        pass

    # pretty printing cmp
    for var in re.findall(r"{[^}]+}", expected):
        idx = actual.find(var)
        if idx > -1:
            assert not var, actual

def _period(claim: Claim) -> str:
    return f"{_date(claim.billablePeriod.start)} - {_date(claim.billablePeriod.end)}"

def _date(date: dt.date):
    return date.strftime("%Y/%m/%d")

def _node_path(traversal: List[Tuple[str, ...]]) -> str:
    sep, nodes = "\n\t\t", ''
    for series in map(list, traversal or []):
        while len(series) < 4:
            series.append('')

        pred, result, label, ocl_info, *_ = series
        pred = (f"#{label}, " if label else "") + pred

        nodes += sep + f"{result.ljust(3)} <- {pred}"
        if ocl_info:
            nodes += sep + '\t' + ocl_info
    return nodes
