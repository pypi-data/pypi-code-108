from attr import attrib
from attr import attrs
import pytest
from _pistar.pistar_pytest.models import AfterResult
from _pistar.pistar_pytest.models import AttachmentType
from _pistar.pistar_pytest.models import BeforeResult
from _pistar.pistar_pytest.models import Exceptions
from _pistar.pistar_pytest.models import Label
from _pistar.pistar_pytest.models import Status
from _pistar.pistar_pytest.models import TestResult
from _pistar.pistar_pytest.reporter import Reporter
from _pistar.pistar_pytest.utils import get_description
from _pistar.pistar_pytest.utils import get_outcome_status
from _pistar.pistar_pytest.utils import get_status
from _pistar.pistar_pytest.utils import now
from _pistar.pistar_pytest.utils import sha256
from _pistar.pistar_pytest.utils import suite_labels
from _pistar.pistar_pytest.utils import uuid4


@attrs
class Finish:
    start_time = attrib(default=None)
    end_time = attrib(default=None)
    duration = attrib(default=None)
    result = attrib(default=None)

    def finish(self):
        self.end_time = now()
        self.duration = self.end_time - self.start_time


class Cache:
    """
    A cache to covert an object to a uuid string.

    The items in cache can be a pytest node id,or a fixturedef object.
    A pytest case item will be pushed in pytest_runtest_protocol,and
    be popped in pytest_runtest_logfinish.
    """

    def __init__(self):
        self._items = dict()

    def get(self, _id):
        return self._items.get(str(_id))

    def push(self, _id):
        return self._items.setdefault(str(_id), uuid4())

    def pop(self, _id):
        return self._items.pop(str(_id), None)


class Collector:
    """Main implement of the pistar plugin for pytest."""

    def __init__(self, report_dir):
        self._reporter = Reporter(report_dir)
        self._cache = Cache()
        self._last_pytest_file = None
        self._cur_node_id = None
        self._cur_file_case_info = None

    def get_cur_id(self):
        return self._cur_node_id

    def get_cache(self) -> Cache:
        return self._cache

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        uuid = self._cache.get(item.nodeid)
        report = (yield).get_result()
        test_result = self._reporter.get_test(uuid)
        status = get_pytest_report_status(report)
        status_details = None

        if call.excinfo:
            message = call.excinfo.exconly()
            if hasattr(report, "wasxfail"):
                reason = report.wasxfail
                message = ("XFAIL {}".format(reason) if reason else "XFAIL") + "\n\n" + message
            trace = report.longreprtext
            status_details = Exceptions(title=message, detail=trace)
            if status != Status.SKIPPED and not (
                call.excinfo.errisinstance(AssertionError) or call.excinfo.errisinstance(pytest.fail.Exception)
            ):
                status = Status.BROKEN
        # calculate the file case result.set result failed
        # if we match a non-passed(skipped) result.
        if status not in (Status.PASSED, Status.SKIPPED):
            self._cur_file_case_info.result = Status.FAILED.val

        if status == Status.PASSED and hasattr(report, "wasxfail"):
            reason = report.wasxfail
            message = "XPASS {reason}".format(reason=reason) if reason else "XPASS"
            status_details = Exceptions(title=message)

        if report.when in ("setup", "call"):
            test_result.result = status.val
            test_result.add_exception(status_details)

        if report.when == "teardown":
            if status in (Status.FAILED, Status.BROKEN) and test_result.result == Status.PASSED.val:
                test_result.result = status.val
                test_result.add_exception(status_details)

            self._handle_attachment(report)

    def _handle_attachment(self, report):
        if report.caplog:
            self._attach_data(report.caplog, "log", AttachmentType.TEXT)
        if report.capstdout:
            self._attach_data(report.capstdout, "stdout", AttachmentType.TEXT)
        if report.capstderr:
            self._attach_data(report.capstderr, "stderr", AttachmentType.TEXT)

    def _attach_data(self, body, name, attachment_type):
        self._reporter.attach_data(uuid4(), body, name=name, attachment_type=attachment_type)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item, nextitem):
        uuid = self._cache.push(item.nodeid)
        self._cur_node_id = item.nodeid
        test_result = TestResult(name=item.name, uuid=uuid, start_time=now(), end_time=now())
        new_file_md5 = sha256(item.fspath.strpath)
        if self._last_pytest_file is None:
            self._update_file_case_info(item, new_file_md5)

        elif self._last_pytest_file != item.fspath.strpath:
            self._cur_file_case_info.finish()
            self._reporter.set_file_finished(self._cur_file_case_info)
            self._update_file_case_info(item, new_file_md5)
        self._reporter.schedule_test(uuid, test_result)
        yield

    def _update_file_case_info(self, item, new_file_md5):
        self._reporter.update_file_output_path(new_file_md5)
        self._cur_file_case_info = Finish(start_time=now(), result=Status.PASSED.val)
        self._last_pytest_file = item.fspath.strpath
        self._reporter.update_cur_file(item.fspath.strpath)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        fixture_name = fixturedef.argname

        uuid = self._cache.get(request.node.nodeid)
        test_result = self._reporter.get_test(uuid)

        before_fixture_uuid = uuid4()
        before_fixture = BeforeResult(name=fixture_name, start_time=now())
        self._reporter.start_before_fixture(before_fixture_uuid, before_fixture)

        outcome = yield

        fixture_result = get_outcome_status(outcome)
        self._reporter.stop_before_fixture(before_fixture_uuid, end_time=now(), result=fixture_result.val)

        before_fixture.cal_duration()
        test_result.before.append(before_fixture)

        self.hook_pytest_finalizer(fixturedef)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):

        yield
        uuid = self._cache.get(item.nodeid)
        test_result = self._reporter.get_test(uuid)
        full_name = item.nodeid
        test_result.fullName = full_name
        test_result.testCaseId = sha256(full_name)
        test_result.description = get_description(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        uuid = self._cache.get(item.nodeid)
        test_result = self._reporter.get_test(uuid)

        test_result.start_time = now()
        yield
        test_result.end_time = now()
        test_result.cal_duration()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item):
        yield
        uuid = self._cache.get(item.nodeid)
        test_result = self._reporter.get_test(uuid)
        if not test_result.duration:
            # handle tests raises error before run step.
            test_result.end_time = now()
            test_result.cal_duration()

        test_result.labels.extend([Label(name=name, value=value) for name, value in suite_labels(item)])

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_logfinish(self, nodeid, location):
        yield
        uuid = self._cache.pop(nodeid)
        self._reporter.close_test(uuid)

    def pytest_sessionfinish(self):
        # set last file case finished
        if self._cur_file_case_info:
            self._cur_file_case_info.finish()
            self._reporter.set_file_finished(self._cur_file_case_info)

    def hook_pytest_finalizer(self, fixturedef):
        """
        Hook pytest finalizer.

        Replace original finalizer by FinalizerWrapper to get statistic info,
        like duration.
        """
        finalizers = getattr(fixturedef, "_finalizers", [])
        fixture_name = fixturedef.argname
        for index, finalizer in enumerate(finalizers):
            name = "{fixture}::{finalizer}".format(
                fixture=fixture_name, finalizer=getattr(finalizer, "__name__", index)
            )
            finalizers[index] = FinalizerWrapper(self._reporter, self, finalizer, name=name)


def get_pytest_report_status(pytest_report) -> Status:
    """
    Get pytest execution result from report.

    Parameter "pytest_report" is a pytest built-in object,which has three
    attributes named passed,failed,skipped.Only one can be true.

    :return:real pytest execution result
    """
    for status in (Status.PASSED, Status.SKIPPED):
        if getattr(pytest_report, status.key):
            return status

    return Status.FAILED


class FinalizerWrapper:
    """
    A Wrapper for pytest fixture_post_finalizer.
    we hack all fixture_post_finalizer in pytest_fixture_setup
    to collect some additional data,like time.
    """

    def __init__(self, reporter: Reporter, collector: Collector, fixture_function, name):
        self._reporter = reporter
        self._collector = collector
        self._fixture_function = fixture_function
        self._uuid = uuid4()
        self._name = name

    def __enter__(self):
        self.start_fixture(uuid=self._uuid, name=self._name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_fixture(uuid=self._uuid, exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    def __call__(self, *args, **kwargs):
        with self:
            return self._fixture_function(*args, **kwargs)

    def start_fixture(self, uuid, name):
        after_fixture = AfterResult(name=name, start_time=now())
        self._reporter.start_after_fixture(uuid, after_fixture)

    def stop_fixture(self, uuid, exc_type, exc_val, exc_tb):
        after_fixture = self._reporter.get_item(uuid)
        cur_nodeid = self._collector.get_cur_id()
        test_uuid = self._collector.get_cache().get(cur_nodeid)
        test_result = self._reporter.get_test(test_uuid)
        status = get_status(exc_val)
        self._reporter.stop_after_fixture(uuid, end_time=now(), result=status.val)
        after_fixture.cal_duration()
        test_result.after.append(after_fixture)
