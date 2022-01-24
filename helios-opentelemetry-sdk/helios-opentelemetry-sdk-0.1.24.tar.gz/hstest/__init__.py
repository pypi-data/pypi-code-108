import os

import pytest
import json
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.status import StatusCode
from opentelemetry import context

from helios import initialize, HeliosBase, HeliosTags
from helios.defaults import DEFAULT_HS_API_ENDPOINT
from helios.utils import encode_id_as_hex_string
from helios.helios_test_trace import HS_ACCESS_TOKEN_ENV_VAR

SERVICE_NAME = 'hs_test'
ROOT_SPAN_NAME = 'test_root'
HS_API_ENDPOINT = os.environ.get('HS_API_ENDPOINT') or DEFAULT_HS_API_ENDPOINT

self_test = False
span_exporter = None
test_span_exporter = None
active_span = None
tracer_provider = None
tracer = None
hs_test_enabled = False


class PytestSpanAttributes:
    LIBRARY = 'testLibrary'
    NAME = 'name'
    STATUS = 'status.code'
    ERROR_MESSAGE = 'status.message'


def is_self_test(config):
    self_test_str = config.getoption('--self_test') or os.environ.get('HS_SELF_TEST', 'False')
    return self_test_str.lower() == "true"


def get_api_token(config):
    api_token = config.getoption('--hs_access_token') or os.environ.get(HS_ACCESS_TOKEN_ENV_VAR)
    if api_token is None:
        raise RuntimeError('Helios access token is missing.'
                           f' please set {HS_ACCESS_TOKEN_ENV_VAR} env var,'
                           ' or provide --hs_access_token argument to pytest command')
    os.environ[HS_ACCESS_TOKEN_ENV_VAR] = api_token
    return api_token


def is_hs_test_enabled(config):
    if os.environ.get(HeliosBase.HS_DISABLED_ENV_VAR):
        return False

    hs_enabled = config.getoption('--hs_enabled')
    return hs_enabled in ['true', 'True']


def pytest_configure(config):
    global span_exporter, test_span_exporter, tracer_provider, tracer, self_test, hs_test_enabled

    hs_test_enabled = is_hs_test_enabled(config)
    if not hs_test_enabled:
        return

    api_token = get_api_token(config)
    collector_endpoint = config.getoption('--collector_endpoint')
    test_collector_endpoint = config.getoption('--test_collector_endpoint')
    environment = config.getoption('--environment')

    self_test = is_self_test(config)
    if self_test:
        span_exporter = InMemorySpanExporter()
        test_span_exporter = InMemorySpanExporter()

    hs = initialize(
        api_token=api_token,
        service_name=SERVICE_NAME,
        collector_endpoint=collector_endpoint,
        test_collector_endpoint=test_collector_endpoint,
        environment=environment,
        enabled=hs_test_enabled,
        span_exporter=span_exporter,
        test_span_exporter=test_span_exporter
    )

    tracer_provider = hs.get_tracer_provider()
    tracer = tracer_provider.get_tracer(__name__)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    if not hs_test_enabled:
        yield
    else:
        global active_span
        ctx = HeliosBase.set_test_triggered_baggage()
        token = context.attach(ctx)
        with tracer.start_as_current_span(ROOT_SPAN_NAME, ctx) as span:
            active_span = span
            # returns to test execution
            try:
                yield
            finally:
                context.detach(token)

        # When test is done
        active_span = None
        tracer_provider.force_flush()

        if self_test:
            run_self_test(item)


def run_self_test(item):
    expected_status = os.environ.get('HS_SELF_TEST_EXPECTED_STATUS', 'passed')
    child_span = None
    test_span = None
    child_span_name = os.environ.get('HS_SELF_TEST_EXPECTED_CHILD_SPAN')
    if span_exporter:
        span_ids = []
        for span in span_exporter.get_finished_spans():
            span_ids.append(span.context.span_id)
            if span.attributes.get('otel.library.name') == child_span_name:
                child_span = span
            elif span.name == ROOT_SPAN_NAME:
                test_span = span

        test_span_ids = [x.context.span_id for x in test_span_exporter.get_finished_spans()]
        assert span_ids == test_span_ids

    assert test_span is not None
    assert test_span.attributes.get(PytestSpanAttributes.NAME) == item.location[-1]
    assert test_span.attributes.get(PytestSpanAttributes.STATUS) == (
        StatusCode.ERROR.value if expected_status != 'passed' else StatusCode.OK.value)
    if expected_status == 'passed':
        assert test_span.attributes.get(PytestSpanAttributes.ERROR_MESSAGE, None) is None
    else:
        assert test_span.attributes.get(PytestSpanAttributes.ERROR_MESSAGE) is not None

    if child_span_name:
        assert child_span is not None
        assert child_span.parent.span_id == test_span.context.span_id
        headers = json.loads(child_span.attributes['http.request.headers'])
        assert headers['baggage'] == f'{HeliosTags.TEST_TRIGGERED_TRACE}={HeliosTags.TEST_TRIGGERED_TRACE}'


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # returns to test execution
    outcome = yield

    # when test is done, do nothing if hs_test not enabled
    if not hs_test_enabled:
        return

    # when test is done, extract the attributes from the test report
    result = outcome.get_result()
    if result.when == 'call':
        if active_span:
            test_name = result.location[-1]
            test_successful = result.outcome == 'passed'
            err_msg = result.longrepr.reprcrash.message if not test_successful else None
            active_span.set_attributes({
                PytestSpanAttributes.LIBRARY: 'pytest',
                PytestSpanAttributes.NAME: test_name,
                PytestSpanAttributes.STATUS: StatusCode.OK.value if test_successful else StatusCode.ERROR.value
            })
            if os.environ.get('CI'):
                ci_attributes = get_ci_run_parameters()
                active_span.set_attributes(ci_attributes) if ci_attributes else None
            active_span.set_attribute(PytestSpanAttributes.ERROR_MESSAGE, err_msg) if err_msg else None
            # \u2713 is a "v" sign, \u2717 is an "x" sign.
            print('\n\n%s %s:' % ('\u2713' if test_successful else '\u2717', test_name))
            print_highlighted('View complete test run in Helios >' if test_successful else 'Investigate test failure in Helios >')
            print_highlighted(get_action_trace_string(active_span.context.trace_id, test_successful))


def get_ci_run_parameters():
    env = os.environ
    env_detected = False
    job_name = None
    job_id = None
    job_url = None
    ci_attributes = {}
    if env.get('GITHUB_ACTIONS'):
        job_name = env.get('GITHUB_WORKFLOW')
        job_id = env.get('GITHUB_RUN_ID')
        if env.get('GITHUB_SERVER_URL') and env.get('GITHUB_REPOSITORY') and env.get('GITHUB_RUN_ID'):
            job_url = f"{env.get('GITHUB_SERVER_URL')}/${env.get('GITHUB_REPOSITORY')}/actions/runs/${env.get('GITHUB_RUN_ID')}"
        env_detected = True

    if env.get('TRAVIS'):
        job_name = env.get('TRAVIS_JOB_NAME')
        job_id = env.get('TRAVIS_JOB_ID')
        job_url = env.get('TRAVIS_JOB_WEB_URL')
        env_detected = True

    if env.get('GITLAB_CI'):
        job_name = env.get('CI_JOB_NAME')
        job_id = env.get('CI_JOB_ID')
        job_url = env.get('CI_JOB_URL')
        env_detected = True

    if env.get('CIRCLECI'):
        job_name = env.get('CIRCLE_JOB')
        job_id = env.get('CIRCLE_WORKFLOW_ID')
        job_url = env.get('CIRCLE_BUILD_URL')
        env_detected = True

    if env_detected:
        ci_attributes['ci.job_name'] = job_name if job_name else None
        ci_attributes['ci.job_id'] = job_id if job_id else None
        ci_attributes['ci.job_url'] = job_url if job_url else None
        return ci_attributes


def get_action_trace_string(trace_id, success):
    x = '\u2715'
    v = '\u2713'
    icon = v if success else x
    return f'{icon} {HS_API_ENDPOINT}?actionTraceId={encode_id_as_hex_string(trace_id)}'


def print_highlighted(text):
    cyan_bg = '\x1b[46m'
    reset_colors = '\x1b[0m'
    black_text = '\x1b[30m'
    print(f'{cyan_bg}{black_text} {text} {reset_colors}')


def pytest_addoption(parser):
    parser.addoption('--hs_enabled', help="enable instrumented tests", default=None)
    parser.addoption('--hs_access_token', help='access token for Helios', default=None)
    parser.addoption('--environment', help='name of the environment where the tests are running', default='')
    parser.addoption('--collector_endpoint', help='OTEL collector endpoint', default=HeliosBase.HS_DEFAULT_COLLECTOR)
    parser.addoption('--test_collector_endpoint', help='OTEL test collector endpoint',
                     default=HeliosBase.HS_DEFAULT_TEST_COLLECTOR)
    parser.addoption('--self_test', help='run tests in dry run mode', default=None)
