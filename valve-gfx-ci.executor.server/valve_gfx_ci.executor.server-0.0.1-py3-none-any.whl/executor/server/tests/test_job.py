from datetime import datetime, timedelta
from freezegun import freeze_time
import pytest
from unittest.mock import patch, MagicMock

from server.job import Target, Timeout, Timeouts, ConsoleState, _multiline_string, Deployment, Job

# Target


def test_Target_from_job__no_id_nor_tags():
    with pytest.raises(ValueError) as exc:
        Target.from_job({})

    msg = "The target is neither identified by tags or id. Use empty tags to mean 'any machines'."
    assert msg in str(exc.value)


def test_Target_from_job__id_only():
    target_job = {
        "id": "MyID",
    }

    target = Target.from_job(target_job)
    assert target.id == target_job['id']
    assert target.tags == []
    assert str(target) == f"<Target: id={target.id}, tags={target.tags}>"


def test_Target_from_job__tags_only():
    target_job = {
        "tags": ['tag 1', 'tag 2']
    }

    target = Target.from_job(target_job)
    assert target.id is None
    assert target.tags == target_job['tags']
    assert str(target) == f"<Target: id={target.id}, tags={target.tags}>"


def test_Target_from_job__both_id_and_tags():
    target_job = {
        "id": "MyID",
        "tags": ['tag 1', 'tag 2']
    }

    target = Target.from_job(target_job)
    assert target.id == target_job['id']
    assert target.tags == target_job['tags']
    assert str(target) == f"<Target: id={target.id}, tags={target.tags}>"


# Timeout


def test_Timeout__expiration_test():
    start_time = datetime(2021, 1, 1, 12, 0, 0)
    with freeze_time(start_time.isoformat()):
        timeout = Timeout(name="name", timeout=timedelta(minutes=1), retries=0)
        assert timeout.started_at is None
        assert timeout.active_for is None

        # Start the timeout and check the state
        timeout.start()
        assert timeout.started_at == start_time
        assert timeout.active_for == timedelta()
        assert not timeout.has_expired

        # Go right to the limit of the timeout
        delta = timedelta(seconds=60)
        with freeze_time((start_time + delta).isoformat()):
            assert timeout.started_at == start_time
            assert timeout.active_for == delta
            assert not timeout.has_expired

        # And check that an extra millisecond trip it
        delta = timedelta(seconds=60, milliseconds=1)
        with freeze_time((start_time + delta).isoformat()):
            assert timeout.started_at == start_time
            assert timeout.active_for == delta
            assert timeout.has_expired

        # Stop the timeout and check the state
        timeout.stop()
        assert timeout.started_at is None
        assert timeout.active_for is None


def test_Timeout__retry_lifecycle():
    timeout = Timeout(name="timeout name", timeout=timedelta(seconds=42), retries=1)

    # Check the default state
    assert timeout.started_at is None
    assert timeout.active_for is None
    assert timeout.retried == 0

    # Start the timeout
    start_time = datetime(2021, 1, 1, 12, 0, 0)
    with freeze_time(start_time.isoformat()):
        timeout.start()
        assert timeout.started_at == start_time
        assert timeout.retried == 0
        assert timeout.active_for == timedelta()
        assert not timeout.has_expired

    # Check that the default reset sets started_at to now()
    start_time = datetime(2021, 1, 1, 12, 0, 1)
    with freeze_time(start_time.isoformat()):
        timeout.reset()
        assert timeout.started_at == start_time

        # Check that a resetting to a certain time does as it should
        new_start = start_time - timedelta(seconds=1)
        timeout.reset(new_start)
        assert timeout.started_at == new_start

    # Do the first retry
    assert timeout.retry()
    assert timeout.started_at is None
    assert timeout.retried == 1

    # Second retry should fail
    assert not timeout.retry()


def test_Timeout_from_job():
    delay = timedelta(days=5, hours=6, minutes=7, seconds=8, milliseconds=9)
    timeout = Timeout.from_job("Yeeepeee", {"days": 5, "hours": 6, "minutes": 7,
                                            "seconds": 8, "milliseconds": 9, "retries": 42})

    assert timeout.timeout == delay
    assert timeout.retries == 42
    assert str(timeout) == f"<Timeout Yeeepeee: value={delay}, retries=0/42>"


# Timeouts


def test_Timeouts__overall_with_retries():
    for t_type in [Timeouts.Type.OVERALL.value, Timeouts.Type.INFRA_TEARDOWN.value]:
        with pytest.raises(ValueError) as exc:
            Timeouts({t_type: Timeout("name", timedelta(), retries=1)})
        assert "Neither the overall nor the teardown timeout can have retries" in str(exc.value)


def test_Timeouts__default():
    timeouts = Timeouts({})

    for timeout in timeouts:
        assert timeout.timeout == timedelta.max
        assert timeout.retries == 0

    assert timeouts.expired_list == []
    assert not timeouts.has_expired


def test_Timeouts__expired():
    overall = Timeout("name", timedelta(days=1), retries=0)
    boot_cycle = Timeout("name", timedelta(seconds=0), retries=0)

    overall.start()
    boot_cycle.start()

    timeouts = Timeouts({Timeouts.Type.OVERALL.value: overall, Timeouts.Type.BOOT_CYCLE.value: boot_cycle})
    assert timeouts.has_expired
    assert timeouts.expired_list == [boot_cycle]


def test_Timeouts__from_job():
    job_timeouts = {
        "first_console_activity": {
            "seconds": 45
        },
        "console_activity": {
            "seconds": 13
        }
    }

    timeouts = Timeouts.from_job(job_timeouts)

    assert timeouts.first_console_activity.timeout == timedelta(seconds=45)
    assert timeouts.console_activity.timeout == timedelta(seconds=13)


# ConsoleState


def test_ConsoleState__missing_session_end():
    with pytest.raises(AttributeError):
        ConsoleState(session_end=None, session_reboot=None, job_success=None, job_warn=None)


def test_ConsoleState__simple_lifecycle():
    state = ConsoleState(session_end="session_end", session_reboot=None, job_success=None, job_warn=None)

    assert state.job_status == "INCOMPLETE"
    assert not state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"oh oh oh")
    assert state.job_status == "INCOMPLETE"
    assert not state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"blabla session_end blaba\n")
    assert state.job_status == "COMPLETE"
    assert state.session_has_ended
    assert not state.needs_reboot


def test_ConsoleState__lifecycle_with_extended_support():
    state = ConsoleState(session_end="session_end", session_reboot="session_reboot",
                         job_success="job_success", job_warn="job_warn")

    assert state.job_status == "INCOMPLETE"
    assert not state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"oh oh oh")
    assert state.job_status == "INCOMPLETE"
    assert not state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"blabla session_reboot blabla")
    assert state.job_status == "INCOMPLETE"
    assert not state.session_has_ended
    assert state.needs_reboot

    state.reset_per_boot_state()
    assert not state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"blabla session_end blaba\n")
    assert state.job_status == "FAIL"
    assert state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"blabla job_success blaba\n")
    assert state.job_status == "PASS"
    assert state.session_has_ended
    assert not state.needs_reboot

    state.process_line(b"blabla job_warn blaba\n")
    assert state.job_status == "WARN"
    assert state.session_has_ended
    assert not state.needs_reboot


def test_ConsoleState_from_job__default():
    console_state = ConsoleState.from_job({})

    assert console_state.session_end == "^\\[[\\d \\.]{12}\\] reboot: Power Down$"
    assert console_state.session_reboot is None
    assert console_state.job_success is None
    assert console_state.job_warn is None


def test_ConsoleState_from_job__full():
    console_state = ConsoleState.from_job({
        "session_end": {
            "regex": "session_end"
        }, "session_reboot": {
            "regex": "session_reboot"
        }, "job_success": {
            "regex": "job_success"
        }, "job_warn": {
            "regex": "job_warn"
        }
    })

    assert console_state.session_end == "session_end"
    assert console_state.session_reboot == "session_reboot"
    assert console_state.job_success == "job_success"
    assert console_state.job_warn == "job_warn"


# _multiline_string


def test_multiline_string():
    assert _multiline_string("toto") == "toto"
    assert _multiline_string(["tag1", "tag2"]) == "tag1 tag2"

    with pytest.raises(AssertionError):
        _multiline_string(1234)


# Deployment


def test_Deployment():
    deployment = Deployment()

    assert deployment.kernel_url is None
    assert deployment.initramfs_url is None
    assert deployment.kernel_cmdline is None

    deployment.update({})

    assert deployment.kernel_url is None
    assert deployment.initramfs_url is None
    assert deployment.kernel_cmdline is None

    deployment.update({"kernel": {"url": "kernel_url", "cmdline": "cmdline"}, "initramfs": {"url": "initrd_url"}})

    assert deployment.kernel_url == "kernel_url"
    assert deployment.initramfs_url == "initrd_url"
    assert deployment.kernel_cmdline == "cmdline"

    assert str(deployment) == """<Deployment:
    kernel_url: kernel_url
    initramfs_url: initrd_url
    kernel_cmdline: cmdline>
"""

# Job


def test_Job__simple():
    simple_job = """
version: 1
target:
  id: "b4:2e:99:f0:76:c5"
console_patterns:
  session_end:
    regex: "session_end"
deployment:
  start:
    kernel:
      url: "kernel_url"
      cmdline:
        - my
        - start cmdline
    initramfs:
      url: "initramfs_url"
"""
    job = Job.from_job(simple_job)

    assert job.version == 1
    assert job.deadline == datetime.max

    assert job.target.id == "b4:2e:99:f0:76:c5"
    assert job.target.tags == []

    assert job.deployment_start.kernel_url == "kernel_url"
    assert job.deployment_start.initramfs_url == "initramfs_url"
    assert job.deployment_start.kernel_cmdline == "my start cmdline"

    assert job.deployment_continue.kernel_url == job.deployment_start.kernel_url
    assert job.deployment_continue.initramfs_url == job.deployment_start.initramfs_url
    assert job.deployment_continue.kernel_cmdline == job.deployment_start.kernel_cmdline

    # Make sure the job's __str__ method does not crash
    str(job)


def test_Job__override_continue():
    override_job = """
version: 1
deadline: "2021-03-31 00:00:00"
target:
  id: "b4:2e:99:f0:76:c6"
  tags: ["amdgpu:gfxversion::gfx10"]
console_patterns:
  session_end:
    regex: "session_end"
deployment:
  start:
    kernel:
      url: "kernel_url"
      cmdline:
        - my
        - start cmdline
    initramfs:
      url: "initramfs_url"
  continue:
    kernel:
      url: "kernel_url 2"
      cmdline: "my continue cmdline"
    initramfs:
      url: "initramfs_url 2"
"""
    job = Job.from_job(override_job)

    assert job.version == 1
    assert job.deadline == datetime.fromisoformat("2021-03-31 00:00:00")

    assert job.target.id == "b4:2e:99:f0:76:c6"
    assert job.target.tags == ["amdgpu:gfxversion::gfx10"]

    assert job.deployment_start.kernel_url == "kernel_url"
    assert job.deployment_start.initramfs_url == "initramfs_url"
    assert job.deployment_start.kernel_cmdline == "my start cmdline"

    assert job.deployment_continue.kernel_url == "kernel_url 2"
    assert job.deployment_continue.initramfs_url == "initramfs_url 2"
    assert job.deployment_continue.kernel_cmdline == "my continue cmdline"


class MockMachine:
    @property
    def ready_for_service(self):
        return True

    @property
    def id(self):
        return "b4:2e:99:f0:76:c5"

    @property
    def tags(self):
        return ["some", "tags"]

    @property
    def local_tty_device(self):
        return "ttyS0"


class MockBucket:
    @property
    def name(self):
        return "bucket_name"

    @property
    def minio(self):
        return MagicMock(url="minio_url")

    @property
    def credentials(self):
        return MagicMock(dut=("access", "secret"))


@patch('server.config.job_environment_vars')
def test_Job__sample(job_env):
    job_env.return_value = {'MINIO_URL': 'testing-url',
                            'NTP_PEER': '10.42.0.1',
                            'PULL_THRU_REGISTRY': '10.42.0.1:8001'}

    m = MockMachine()
    job = Job.from_path("src/valve_gfx_ci/executor/server/tests/sample_job.yml", m)

    assert job.version == 1
    assert job.deadline == datetime.fromisoformat("2021-03-31 00:00:00")

    assert job.target.id == m.id
    assert job.target.tags == m.tags

    assert job.deployment_start.kernel_url == "testing-url/test-kernel"
    assert job.deployment_start.initramfs_url == "testing-url/test-initramfs"

    assert job.deployment_start.kernel_cmdline == 'b2c.container="docker://10.42.0.1:8001/infra/machine_registration:latest check" b2c.ntp_peer="10.42.0.1" b2c.pipefail b2c.cache_device=auto b2c.container="-v /container/tmp:/storage docker://10.42.0.1:8002/tests/mesa:12345" console=ttyS0,115200 earlyprintk=vga,keep SALAD.machine_id=b4:2e:99:f0:76:c5'  # noqa: E501

    assert job.deployment_continue.kernel_url == "testing-url/test-kernel"
    assert job.deployment_continue.initramfs_url == "testing-url/test-initramfs"
    assert job.deployment_continue.kernel_cmdline == 'b2c.container="docker://10.42.0.1:8001/infra/machine_registration:latest check" b2c.ntp_peer=10.42.0.1 b2c.pipefail b2c.cache_device=auto b2c.container="-v /container/tmp:/storage docker://10.42.0.1:8002/tests/mesa:12345 resume"'  # noqa: E501


def test_Job__invalid_format():
    job = """
version: 1
target:
  id: "b4:2e:99:f0:76:c6"
console_patterns:
  session_end:
    regex: "session_end"
  reboot:
    regex: "toto"
deployment:
  start:
    kernel:
      url: "kernel_url"
      cmdline:
        - my
        - start cmdline
    initramfs:
      url: "initramfs_url"
"""

    with pytest.raises(ValueError) as exc:
        Job.from_job(job)

    assert str(exc.value) == "{'console_patterns': {'reboot': ['Unknown field.']}}"


@patch('server.config.job_environment_vars')
def test_Job__from_machine(job_env):
    job_env.return_value = {'NTP_PEER': '10.42.0.1'}

    simple_job = """
version: 1
target:
  id: {{ machine_id }}
console_patterns:
  session_end:
    regex: "session_end"
deployment:
  start:
    kernel:
      url: "kernel_url"
      cmdline:
        - my {{ minio_url }}
        - start cmdline {{ ntp_peer }}
    initramfs:
      url: "initramfs_url"
"""
    job = Job.render_with_resources(simple_job, MockMachine(), MockBucket())

    assert job.version == 1
    assert job.deadline == datetime.max

    assert job.target.id == "b4:2e:99:f0:76:c5"
    assert job.target.tags == []

    assert job.deployment_start.kernel_url == "kernel_url"
    assert job.deployment_start.initramfs_url == "initramfs_url"
    assert job.deployment_start.kernel_cmdline == "my minio_url start cmdline 10.42.0.1"

    assert job.deployment_continue.kernel_url == job.deployment_start.kernel_url
    assert job.deployment_continue.initramfs_url == job.deployment_start.initramfs_url
    assert job.deployment_continue.kernel_cmdline == job.deployment_start.kernel_cmdline
