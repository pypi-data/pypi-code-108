#!/usr/bin/env python3

from datetime import datetime
from threading import Thread, Event
from collections import defaultdict, namedtuple
from urllib.parse import urlsplit, urlparse
from enum import Enum, IntEnum

from .message import LogLevel, JobIOMessage, ControlMessage, SessionEndMessage, Message, MessageType
from .pdu import PDUState
from .message import JobStatus
from .job import Job
from .logger import logger
from .minioclient import MinioClient, MinIOPolicyStatement, generate_policy
from . import config

import traceback
import requests
import tempfile
import secrets
import random
import select
import shutil
import socket
import json
import time


# Constants
CONSOLE_DRAINING_DELAY = 1


class MachineState(Enum):
    WAIT_FOR_CONFIG = 0
    IDLE = 1
    TRAINING = 2
    QUEUED = 3
    RUNNING = 4


def str_to_int(string, default):
    try:
        return int(string)
    except Exception:
        return default


class JobConsoleState(IntEnum):
    CREATED = 0
    ACTIVE = 1
    DUT_DONE = 2
    TEAR_DOWN = 3
    OVER = 4


class JobConsole(Thread):
    def __init__(self, machine_id, client_endpoint, console_patterns,
                 client_version=None, log_level=LogLevel.INFO):
        super().__init__(name='ConsoleThread')

        self.machine_id = machine_id

        self.client_endpoint = client_endpoint
        self.console_patterns = console_patterns
        self.client_version = client_version
        self.log_level = log_level

        # Sockets
        self.client_sock = None
        self.salad_sock = self.connect_to_salad()

        # Job-long state
        self._state = JobConsoleState.CREATED
        self.start_time = None
        self.line_buffer = bytearray()
        self._user_session_state = dict()

        self.reset_per_boot_state()

    @property
    def salad_url(self):
        return f"{config.SALAD_URL}/api/v1/machine/{self.machine_id}"

    def connect_to_salad(self):
        parsed_url = urlsplit(config.SALAD_URL)

        r = requests.get(self.salad_url)
        r.raise_for_status()

        machine = r.json()
        port = machine.get("tcp_port")

        return socket.create_connection((parsed_url.hostname, port))

    def reset_per_boot_state(self):
        self.last_activity_from_machine = None
        self.last_activity_from_client = None

        self.console_patterns.reset_per_boot_state()
        self.needs_reboot = self.console_patterns.needs_reboot

    def close_salad(self):
        try:
            self.salad_sock.shutdown(socket.SHUT_RDWR)
            self.salad_sock.close()
        except OSError:
            pass

    def close_client(self):
        if self.client_version:
            try:
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()
            except OSError:
                pass

    def close(self):
        self.set_state(JobConsoleState.OVER)

    @property
    def state(self):
        if self._state == JobConsoleState.ACTIVE:
            return self._state if self.is_alive() else JobConsoleState.OVER

        return self._state

    def set_state(self, state, **kwargs):
        prev_state = self._state
        if state < prev_state:
            raise ValueError("The state can only move forward")
        elif state == prev_state:
            return
        else:
            self._state = state

        self.log(f"Job console state changed from {prev_state.name} -> {state.name}\n")

        if state == JobConsoleState.ACTIVE:
            self.start_time = datetime.now()

        elif state == JobConsoleState.DUT_DONE:
            # Skip the entire tear-down if we do not have a client
            if not self.client_version:
                self.set_state(JobConsoleState.OVER)

        elif state == JobConsoleState.TEAR_DOWN:
            # Kill the connection to SALAD
            self.close_salad()

            # Notify the client
            if self.client_version:
                if self.client_version == 0:
                    self.log(f"<-- End of the session: {self.console_patterns.job_status} -->\n")
                elif self.client_version == 1:
                    try:
                        status = JobStatus.from_str(self.console_patterns.job_status)
                        SessionEndMessage.create(job_bucket=kwargs.get('job_bucket'),
                                                 status=status).send(self.client_sock)
                    except (ConnectionResetError, BrokenPipeError, OSError):
                        traceback.print_exc()
                try:
                    self.client_sock.shutdown(socket.SHUT_WR)
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass

        elif state == JobConsoleState.OVER:
            # Make sure the connections to SALAD and the client are killed
            self.close_salad()
            self.close_client()

    def start(self):
        if self.client_version:
            logger.info(f"Connecting to the client endpoint {self.client_endpoint}")
            self.client_sock = socket.create_connection(self.client_endpoint)
        super().start()

    def match_console_patterns(self, buf):
        patterns_matched = set()

        # Process the buffer, line by line
        to_process = self.line_buffer + buf
        cur = 0
        while True:
            idx = to_process.find(b'\n', cur)
            if idx > 0:
                line = to_process[cur:idx+1]
                logger.info(f"{self.machine_id} -> {bytes(line)}")
                patterns_matched |= self.console_patterns.process_line(line)
                cur = idx + 1
            else:
                break
        self.line_buffer = to_process[cur:]

        # Tell the user what happened
        if len(patterns_matched) > 0:
            self.log(f"Matched the following patterns: {', '.join(patterns_matched)}\n")

        # Check if the state changed
        self.needs_reboot = self.console_patterns.needs_reboot

    def log(self, msg, log_level=LogLevel.INFO):
        # Ignore messages with a log level lower than the minimum set
        if log_level < self.log_level:
            return

        if self.start_time is not None:
            relative_time = (datetime.now() - self.start_time).total_seconds()
        else:
            relative_time = 0.0

        log_msg = f"+{relative_time:.3f}s: {msg}"
        logger.info(log_msg.rstrip("\r\n"))

        if self.client_version:
            try:
                if self.client_version == 0:
                    self.client_sock.send(log_msg.encode())
                elif self.client_version == 1:
                    ControlMessage.create(log_msg, severity=log_level).send(self.client_sock)
            except OSError:
                pass

    def stop(self):
        self.set_state(JobConsoleState.OVER)
        self.join()

    def run(self):
        self.set_state(JobConsoleState.ACTIVE)

        while self.state < JobConsoleState.OVER:
            fds = []
            if self.state < JobConsoleState.TEAR_DOWN:
                fds.extend([self.salad_sock.fileno()])
            if self.client_version:
                fds.extend([self.client_sock.fileno()])

            # Make sure all the FDs are valid, or exit!
            if any([fd < 0 for fd in fds]):
                self.log("Found a negative fd, aborting!")
                self.close()

            rlist, _, _ = select.select(fds, [], [], 1.0)

            for fd in rlist:
                try:
                    if fd == self.salad_sock.fileno():
                        # DUT's stdout/err: Salad -> Client
                        buf = self.salad_sock.recv(8192)
                        if len(buf) == 0:
                            self.set_state(JobConsoleState.DUT_DONE)

                        # Match the console patterns
                        try:
                            self.match_console_patterns(buf)
                        except Exception:
                            self.log(traceback.format_exc())

                        # Update the last console activity if we already had activity,
                        # or when we get the first newline character as serial
                        # consoles may sometimes send unwanted characters at power up
                        if self.last_activity_from_machine is not None or b'\n' in buf:
                            self.last_activity_from_machine = datetime.now()

                        # Forward to the client
                        if self.client_version:
                            if self.client_version == 0:
                                self.client_sock.send(buf)
                            elif self.client_version == 1:
                                JobIOMessage.create(buf).send(self.client_sock)

                        # The message got forwarded, close the session if it ended
                        if self.console_patterns.session_has_ended:
                            self.set_state(JobConsoleState.DUT_DONE)

                    elif fd == self.client_sock.fileno():
                        # DUT's stdin: Client -> Salad
                        if self.client_version == 0:
                            buf = self.client_sock.recv(8192)
                            if len(buf) == 0:
                                self.close()

                            # Forward to the salad
                            self.salad_sock.send(buf)
                        elif self.client_version == 1:
                            try:
                                msg = Message.next_message(self.client_sock)
                                if msg.msg_type == MessageType.JOB_IO:
                                    self.salad_sock.send(msg.buffer)
                            except EOFError:
                                # Do not warn when we are expecting the client to close its socket
                                if self.state < JobConsoleState.TEAR_DOWN:
                                    self.log(traceback.format_exc())

                                self.log("The client closed its connection")

                                # Clean up everything on our side
                                self.close()

                        self.last_activity_from_client = datetime.now()
                except (ConnectionResetError, BrokenPipeError, OSError):
                    self.log(traceback.format_exc())
                    self.close()
                except Exception:
                    logger.error(traceback.format_exc())


class SergentHartman:
    def __init__(self, machine, boot_loop_counts=None, qualifying_rate=None):
        super().__init__()

        if boot_loop_counts is None:
            boot_loop_counts = int(config.SERGENT_HARTMAN_BOOT_COUNT)

        if qualifying_rate is None:
            qualifying_rate = int(config.SERGENT_HARTMAN_QUALIFYING_BOOT_COUNT)

        self.machine = machine
        self.boot_loop_counts = boot_loop_counts
        self.qualifying_rate = qualifying_rate

        self.reset()

    @property
    def is_machine_registered(self):
        return self.cur_loop > 0

    def reset(self):
        self.is_active = False
        self.cur_loop = 0
        self.statuses = defaultdict(int)

    def next_task(self):
        mid = self.machine.id

        if not self.is_active:
            # Start by forcing the machine to register itself to make sure the
            # its configuration is up to date (especially the serial console
            # port). Loop until it succeeds!
            self.reset()

            logger.info("SergentHartman/%s - Try registering the machine", mid)

            self.is_active = True

            return Job.from_path(config.EXECUTOR_REGISTRATION_JOB, self.machine)
        else:
            # Check that we got the expected amount of reports
            if self.cur_loop != sum(self.statuses.values()):
                raise ValueError("The previous next_task() call was not followed by a call to report()")

            # The registration went well, let's start the boot loop!
            self.cur_loop += 1

            statuses_str = [f"{status.name}: {values}" for status, values in self.statuses.items()]
            logger.info("SergentHartman/%s - loop %s/%s - statuses %s: "
                        "Execute one more round!",
                        mid,
                        self.cur_loop,
                        self.boot_loop_counts,
                        statuses_str)

            return Job.from_path(config.EXECUTOR_BOOTLOOP_JOB, self.machine)

    def report(self, job_status):
        mid = self.machine.id

        if self.cur_loop == 0:
            if job_status != JobStatus.PASS:
                delay = int(config.SERGENT_HARTMAN_REGISTRATION_RETRIAL_DELAY)
                logger.warning((f"SergentHartman/{mid} - Registration failed with status {job_status.name}. "
                                f"Retrying in {delay} second(s)"))
                self.reset()
                return delay
            else:
                logger.info(f"SergentHartman/{mid} - Registration succeeded, moving on to the boot loop")
        else:
            # We are in the boot loop
            self.statuses[job_status] += 1

            if self.cur_loop == self.boot_loop_counts:
                self.is_active = False

                # Update MaRS
                ready_for_service = self.statuses[JobStatus.PASS] >= self.qualifying_rate
                self.machine.ready_for_service = ready_for_service

        return 0

    @property
    def is_available(self):
        return config.EXECUTOR_REGISTRATION_JOB or config.EXECUTOR_BOOTLOOP_JOB


class JobBucket:
    Credentials = namedtuple('Credentials', ['username', 'password', 'policy_name'])

    def __init__(self, minio, bucket_name, initial_state_tarball_file=None):
        self.minio = minio
        self.name = bucket_name

        self._credentials = dict()

        if initial_state_tarball_file:
            self.initial_state_tarball_file = tempfile.NamedTemporaryFile("w+b")
            shutil.copyfileobj(initial_state_tarball_file, self.initial_state_tarball_file)
            self.initial_state_tarball_file.seek(0)
        else:
            self.initial_state_tarball_file = None

        self.minio.make_bucket(bucket_name)

    def remove(self):
        self.minio.remove_bucket(self.name)

        for credentials in self._credentials.values():
            self.minio.remove_user_policy(credentials.policy_name, credentials.username)
            self.minio.remove_user(credentials.username)

    def __del__(self):
        try:
            self.remove()
        except Exception:
            traceback.print_exc()

    def credentials(self, role):
        return self._credentials.get(role)

    def create_owner_credentials(self, role, user_name=None, password=None,
                                 groups=None, whitelisted_ips=None):
        if user_name is None:
            user_name = f"{self.name}-{role}"

        if password is None:
            password = secrets.token_hex(16)

        if groups is None:
            groups = []

        if whitelisted_ips is None:
            whitelisted_ips = []

        policy_name = f"policy_{user_name}"

        self.minio.add_user(user_name, password)

        policy_statements = [
            MinIOPolicyStatement(buckets=[self.name], source_ips=whitelisted_ips)
        ]
        if len(whitelisted_ips) > 0:
            restrict_to_whitelisted_ips = MinIOPolicyStatement(allow=False, not_source_ips=whitelisted_ips)
            policy_statements.append(restrict_to_whitelisted_ips)
        policy = json.dumps(generate_policy(policy_statements))
        logger.debug(f"Applying the MinIO policy: {policy}")

        try:
            self.minio.apply_user_policy(policy_name, user_name, policy_statements)
        except Exception as e:
            self.minio.remove_user(user_name)
            raise e from None

        # Add the user to the wanted list of groups
        for group_name in groups:
            self.minio.add_user_to_group(user_name, group_name)

        credentials = self.Credentials(user_name, password, policy_name)
        self._credentials[role] = credentials

        return credentials

    def setup(self):
        if self.initial_state_tarball_file:
            self.minio.extract_archive(self.initial_state_tarball_file, self.name)

    def access_url(self, role=None):
        endpoint = urlparse(self.minio.url)

        role_creds = self.credentials(role)
        if role_creds:
            credentials = f"{role_creds[0]}:{role_creds[1]}@"
        else:
            credentials = ""
        return f'{endpoint.scheme}://{credentials}{endpoint.netloc}'

    @classmethod
    def from_job_request(cls, minio, request, machine):
        # Generate a job id
        bucket_name = MinioClient.create_valid_bucket_name(f"job-{machine.id}-{request.job_id}")

        try:
            # BUG: It seems like this is not a reliable way to detect re-use of existing buckets...
            return cls(minio, bucket_name=bucket_name,
                       initial_state_tarball_file=request.job_bucket_initial_state_tarball_file)
        except ValueError:
            # The bucket already exists, let's try to make it more unique!
            now = int(datetime.utcnow().timestamp())
            rand_int = random.randrange(10e6)
            return cls(minio, bucket_name=f"{bucket_name}-{now}-{rand_int}",
                       initial_state_tarball_file=request.job_bucket_initial_state_tarball_file)


class Executor(Thread):
    def __init__(self, machine):
        super().__init__(name=f'ExecutorThread-{machine.id}')

        self.machine = machine

        self.state = MachineState.WAIT_FOR_CONFIG
        self.minio = MinioClient()

        # Training / Qualifying process
        self.sergent_hartman = SergentHartman(machine)

        # Outside -> Inside communication
        self.job_ready = Event()
        self.job_config = None
        self.job_console = None
        self.job_bucket = None

        # Remote artifacts (typically over HTTPS) are stored in our
        # local minio instance which is exposed over HTTP to the
        # private LAN. This makes such artifacts amenable to PXE
        # booting, for which HTTPS clients are not available.  Less
        # critically, it makes access easier for the boards in our
        # private LAN, for which HTTPS offers no advantage.
        self.remote_url_to_local_cache_mapping = {}

        # Start the background thread that will manage the machine
        self.stop_event = Event()
        self.start()

    def start_job(self, job_request):
        if self.state != MachineState.IDLE:
            raise ValueError(f"The machine isn't idle: Current state is {self.state.name}")

        # Prepare the job bucket
        self.job_bucket = JobBucket.from_job_request(self.minio, job_request, self.machine)
        if self.job_bucket:
            self.job_bucket.create_owner_credentials("dut", groups=job_request.minio_groups,
                                                     whitelisted_ips=[f'{self.machine.ip_address}/32'])

        # Bit nasty to render twice, but better than duplicating
        # template render in the various call-sites within
        # executor. Rendering it up front reduces the chances for
        # mistakes. (Meta-point: using an HTTP query to specify the
        # "target" could avoid this duplication of work, and might
        # actually make more sense)
        job = Job.render_with_resources(job_request.raw_job, self.machine, self.job_bucket)
        logger.debug("rendered job:\n%s", job)

        self.state = MachineState.QUEUED
        self.job_request = job_request
        self.job_config = job
        self.job_console = JobConsole(self.machine.id,
                                      client_endpoint=job_request.callback_endpoint,
                                      console_patterns=self.job_config.console_patterns,
                                      client_version=job_request.version)
        self.job_ready.set()

    def log(self, msg, log_level=LogLevel.INFO):
        if self.job_console is not None:
            self.job_console.log(msg, log_level=log_level)

    def _cache_remote_artifact(self, artifact_name, start_url, continue_url):
        artifact_prefix = f"{artifact_name}-{self.machine.id}"

        # Assume the remote artifacts already exist locally
        self.remote_url_to_local_cache_mapping[start_url] = start_url
        self.remote_url_to_local_cache_mapping[continue_url] = continue_url

        def cache_it(url, suffix):
            if self.minio.is_local_url(url):
                logger.debug(f"Ignore caching {url} as it is already hosted by our minio cache")
                return
            self.remote_url_to_local_cache_mapping[url] = f"http://10.42.0.1:9000/boot/{artifact_prefix}-{suffix}"
            self.log(f'Caching {url} into minio...\n')
            self.minio.save_boot_artifact(start_url, f"{artifact_prefix}-start")

        cache_it(start_url, 'start')
        if start_url != continue_url:
            cache_it(continue_url, 'continue')

    def _cache_remote_artifacts(self):
        deploy_strt = self.job_config.deployment_start
        deploy_cnt = self.job_config.deployment_start

        logger.info("Caching the kernel...")
        self._cache_remote_artifact("kernel", deploy_strt.kernel_url,
                                    deploy_cnt.kernel_url)

        logger.info("Caching the initramfs...")
        self._cache_remote_artifact("initramfs", deploy_strt.initramfs_url,
                                    deploy_cnt.initramfs_url)

        if self.job_bucket:
            logger.info("Initializing the job bucket with the client's data")
            self.job_bucket.setup()

    def run(self):
        def session_init():
            # Reset the state
            self.job_config = None
            self.job_console = None
            self.machine.boots.remove_pxelinux_config(self.machine.mac_address)

            # Pick a job
            if self.sergent_hartman.is_available and not self.machine.ready_for_service:
                self.state = MachineState.TRAINING

                self.job_config = self.sergent_hartman.next_task()
                self.job_console = JobConsole(self.machine.id,
                                              client_endpoint=None,
                                              client_version=None,
                                              console_patterns=self.job_config.console_patterns)
            else:
                self.sergent_hartman.reset()

                # Wait for a job to be set
                self.state = MachineState.IDLE
                if not self.job_ready.wait(1):
                    return False
                self.job_ready.clear()

                self.state = MachineState.RUNNING

            # Cut the power to the machine, we do not need it
            self.machine.pdu_port.set(PDUState.OFF)

            # Mark the start time to now()
            self.job_start_time = datetime.now()

            # Connect to the client's endpoint, to relay the serial console
            self.job_console.start()

            return True

        def session_end():
            cooldown_delay_s = 0

            if self.sergent_hartman.is_active and self.job_config is not None:
                status = JobStatus.from_str(self.job_config.console_patterns.job_status)
                cooldown_delay_s = int(self.sergent_hartman.report(status))

            self.job_config = None

            # Signal to the job that we reached the end of the execution
            if self.job_console is not None:
                self.job_console.close()
                self.job_console = None
                self.machine.boots.remove_pxelinux_config(self.machine.mac_address)
                if self.job_bucket:
                    del self.job_bucket

            # Interruptible sleep
            for i in range(cooldown_delay_s):
                if self.stop_event.is_set():
                    return
                time.sleep(1)

        def log_exception():
            logger.debug("Exception caught:\n%s", traceback.format_exc())
            self.log(f"An exception got caught: {traceback.format_exc()}\n", LogLevel.ERROR)
            # If exceptions start firing, throttle the parent loop, since it's
            # very heavy spam if left to run at full speed.
            time.sleep(2)

        def execute_job():
            # Start the overall timeout
            timeouts = self.job_config.timeouts
            timeouts.overall.start()

            # Download the kernel/initramfs
            self.log("Setup the infrastructure\n")
            timeouts.infra_setup.start()
            self._cache_remote_artifacts()
            self.log(f"Completed setup of the infrastructure, after {timeouts.infra_setup.active_for} s\n")
            timeouts.infra_setup.stop()

            # Keep on resuming until success, timeouts' retry limits is hit, or the entire executor is going down
            deployment = self.job_config.deployment_start
            while (not self.stop_event.is_set() and not timeouts.overall.has_expired and
                   self.job_console.state < JobConsoleState.DUT_DONE):
                self.job_console.reset_per_boot_state()

                # Make sure the machine shuts down
                self.machine.pdu_port.set(PDUState.OFF)

                # Set up the deployment
                self.log("Setting up the boot configuration\n")
                self.machine.boots.write_pxelinux_config(
                    mac_addr=self.machine.id,
                    kernel_path=self.remote_url_to_local_cache_mapping.get(deployment.kernel_url),
                    cmdline=deployment.kernel_cmdline,
                    initrd_path=self.remote_url_to_local_cache_mapping.get(deployment.initramfs_url))

                self.log(f"Power up the machine, enforcing {self.machine.pdu_port.min_off_time} seconds of down time\n")
                self.machine.pdu_port.set(PDUState.ON)

                # Start the boot, and enable the timeouts!
                self.log("Boot the machine\n")
                timeouts.boot_cycle.start()
                timeouts.first_console_activity.start()
                timeouts.console_activity.stop()

                while (self.job_console.state < JobConsoleState.DUT_DONE and
                       not self.job_console.needs_reboot and
                       not self.stop_event.is_set() and not timeouts.has_expired):
                    # Update the activity timeouts, based on when was the
                    # last time we sent it data
                    if self.job_console.last_activity_from_machine is not None:
                        timeouts.first_console_activity.stop()
                        timeouts.console_activity.reset(when=self.job_console.last_activity_from_machine)

                    # Wait a little bit before checking again
                    time.sleep(0.1)

                # Cut the power
                self.machine.pdu_port.set(PDUState.OFF)

                # Increase the retry count of the timeouts that expired, and
                # abort the job if we exceeded their limits.
                abort = False
                for timeout in timeouts.expired_list:
                    retry = timeout.retry()
                    decision = "Try again!" if retry else "Abort!"
                    self.log(f"Hit the timeout {timeout} --> {decision}\n", LogLevel.ERROR)
                    abort = abort or not retry

                # Check if the DUT asked us to reboot
                if self.job_console.needs_reboot:
                    retry = timeouts.boot_cycle.retry()
                    retries_str = f"{timeouts.boot_cycle.retried}/{timeouts.boot_cycle.retries}"
                    dec = f"Boot cycle {retries_str}, go ahead!" if retry else "Exceeded boot loop count, aborting!"
                    self.log(f"The DUT asked us to reboot: {dec}\n", LogLevel.WARN)
                    abort = abort or not retry

                if abort:
                    return

                # Stop all the timeouts, except the overall
                timeouts.first_console_activity.stop()
                timeouts.console_activity.stop()
                timeouts.boot_cycle.stop()

                # We went through one boot cycle, update the
                deployment = self.job_config.deployment_continue

            # We either reached the end of the job, or the client got disconnected
            if self.job_console.state == JobConsoleState.DUT_DONE:
                # Tearing down the job
                self.log("The job has finished executing, starting tearing down\n")
                timeouts.infra_teardown.start()

                # Delay to make sure messages are read before the end of the job
                time.sleep(CONSOLE_DRAINING_DELAY)

                # Start the tear down, which will create and send the credentials
                # for the job bucket to the client
                self.log("Creating credentials to the job bucket for the client\n")
                self.job_console.set_state(JobConsoleState.TEAR_DOWN, job_bucket=self.job_bucket)

                # Wait for the client to close the connection
                self.log("Waiting for the client to download the job bucket\n")
                while (self.job_console.state < JobConsoleState.OVER and
                       not self.stop_event.is_set() and
                       not timeouts.infra_teardown.has_expired):
                    # Wait a little bit before checking again
                    time.sleep(0.1)

                self.log(f"Completed the tear down procedure in {timeouts.infra_teardown.active_for} s\n")
                timeouts.infra_teardown.stop()
            else:
                self.log("The job is over, skipping sharing the job bucket with the client")

            # We are done!

        while not self.stop_event.is_set():
            try:
                # Wait for the machine to have an assigned PDU port
                if self.machine.pdu_port is None:
                    time.sleep(1)
                    continue
                try:
                    if not session_init():
                        # No jobs for us to run!
                        continue

                    self.log(f"Starting the job: {self.job_config}\n\n", LogLevel.DEBUG)
                    execute_job()
                except Exception:
                    log_exception()
                finally:
                    session_end()
            except Exception:
                # Capture any further exceptions from session_end
                # TODO: Refactor to avoid the cyclomatic complexity.
                # Note: Do not be tempted to log_exception() here! Any
                # exceptions thrown by *that* method could crash our
                # thread.
                traceback.print_exc()

            # TODO: Keep the state of the job in memory for later querying
