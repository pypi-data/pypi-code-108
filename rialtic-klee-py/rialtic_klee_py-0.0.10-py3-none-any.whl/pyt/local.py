from schema.insight_engine_response import InsightEngineResponse

from klee.files import KleeFile, Inspection
from klee.cases import InsightEngineTestCase
from klee.internal import Structure, log
import pytest

@pytest.fixture(scope='module')
def run_engine():
    def closure(case: InsightEngineTestCase) -> InsightEngineResponse:
        with Inspection():
            # noinspection PyUnresolvedReferences
            from engine.engine import GetInsights

        with KleeFile(Structure.reference.history, 'w') as file:
            log.info('Creating temporary history file: %s items', len(case.history_list))
            file.write_and_flush(case.history_list)

            return GetInsights(case.request)

    return closure

pytest.register_assert_rewrite("klee.pyt.shared")
from klee.pyt.shared import TestEngineV1 as TestLocal

log.info('Start local testing \n')
