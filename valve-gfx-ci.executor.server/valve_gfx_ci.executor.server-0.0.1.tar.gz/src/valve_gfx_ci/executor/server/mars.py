from threading import Thread, Event
from dataclasses import asdict, field
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from pathlib import Path

from pydantic.dataclasses import dataclass
from pydantic import validator, PositiveInt
from inotify_simple import INotify, flags
import traceback
import time
import yaml

from .boots import split_mac_addr
from .logger import logger
from .pdu import PDU
from .executor import Executor
from . import config
from . import gitlab


@dataclass
class ConfigPDU:
    driver: str
    config: dict


@dataclass
class ConfigGitlabRunner:
    token: str = "<invalid default>"
    exposed: bool = True

    def verify_or_renew_token(self, gl, description, tags):
        # Remove the runner when not exposed
        if not self.exposed:
            self.remove(gl)
            return

        log_prefix = f"{description}'s {gl.name} runner"

        logger.debug(f"{log_prefix}: Verifying the token {self.token}")
        if not gitlab.verify_runner_token(gitlab_url=gl.url,
                                          token=self.token):
            logger.warning(f"{log_prefix}: The token {self.token} is invalid. "
                           "Starting the renewal process...")

            self.remove(gl)

            runner = gitlab.register_runner(gitlab_url=gl.url,
                                            registration_token=gl.registration_token,
                                            description=description,
                                            tag_list=tags,
                                            maximum_timeout=gl.maximum_timeout)
            if runner:
                self.token = runner.token
                logger.info(f"{log_prefix}: Got assigned the token {self.token}")
            else:
                logger.error(f"{log_prefix}: Could not register the runner on {gl.name}")

    def remove(self, gl):
        if self.token != "<invalid default>":
            print(f"Unregister {gl.name}'s runner {self.token}")

        gitlab.unregister_runner(gitlab_url=gl.url, token=self.token)
        self.token = "<invalid default>"


@dataclass
class ConfigDUT:
    base_name: str
    tags: list[str]
    ip_address: str  # TODO: Make sure all machines have a unique IP
    local_tty_device: str = None
    gitlab: dict[str, ConfigGitlabRunner] = field(default_factory=dict)
    pdu: str = None
    pdu_port_id: str = None
    pdu_off_delay: float = 30
    ready_for_service: bool = False
    is_retired: bool = False
    first_seen: datetime = field(default_factory=lambda: datetime.now())

    @validator('ip_address')
    def ip_address_is_valid(cls, v):
        IPv4Address(v)
        return str(v)

    @property
    def full_name(self):
        # Get the index of the dut by looking at how many duts with
        # the same base name were registered *before* us.
        idx = 1
        for dut in self.mars_db.duts.values():
            if dut.base_name == self.base_name and dut.first_seen < self.first_seen:
                idx += 1

        return f"{config.FARM_NAME}-{self.base_name}-{idx}"

    @property
    def available(self):
        return self.ready_for_service and not self.is_retired

    def expose_on_forges(self):
        # Make sure every gitlab instance is represented in the DUT's config
        for gl in self.mars_db.gitlab.values():
            if self.gitlab.get(gl.name) is None:
                self.gitlab[gl.name] = ConfigGitlabRunner()

        if self.available:
            for gl in self.mars_db.gitlab.values():
                local_cfg = self.gitlab.get(gl.name)
                if gl.expose_runners:
                    local_cfg.verify_or_renew_token(gl, description=self.full_name, tags=self.tags)
                else:
                    local_cfg.remove(gl)
        else:
            # Un-register every associated runner
            for gl_name, local_cfg in self.gitlab.items():
                if gl := self.mars_db.gitlab.get(gl_name):
                    local_cfg.remove(gl)


@dataclass
class ConfigGitlab:
    url: str
    registration_token: str
    expose_runners: bool = True
    maximum_timeout: PositiveInt = 21600
    gateway_runner: ConfigGitlabRunner = None

    # Function called once all the objects have been converted from dict
    # to their dataclass equivalent
    def __post_init_post_parse__(self):
        if self.gateway_runner is not None:
            self.gateway_runner.mars_db = self

    @validator("url")
    def url_is_valid(cls, v):
        assert v.startswith("https://")
        return v

    @property
    def should_expose_gateway_runner(self):
        if not self.expose_runners or self.gateway_runner is None:
            return False

        return self.gateway_runner.exposed


@dataclass
class MarsDB:
    pdus: dict[str, ConfigPDU] = field(default_factory=dict)
    duts: dict[str, ConfigDUT] = field(default_factory=dict)
    gitlab: dict[str, ConfigGitlab] = field(default_factory=dict)

    def reset_taint(self):
        self._disk_state = asdict(self)

    @property
    def is_tainted(self):
        return asdict(self) != self._disk_state

    @validator('duts')
    def mac_addresses_are_understood_by_boots(cls, v):
        for addr in v.keys():
            split_mac_addr(addr)
        return v

    # Function called once all the objects have been converted from dict
    # to their dataclass equivalent
    def __post_init_post_parse__(self):
        # Since we do not want to repeat ourselves in the config file, the name
        # of objects is set in the parent dict. However, it is quite useful for
        # objects to know their names and have access to the DB. This function
        # adds it back!
        for name, pdu in self.pdus.items():
            pdu.name = name
            pdu.mars_db = self

        for mac_address, dut in self.duts.items():
            dut.mac_address = mac_address
            dut.mars_db = self

        for name, gitlab_instance in self.gitlab.items():
            gitlab_instance.name = name
            gitlab_instance.mars_db = self

        self.reset_taint()

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            return cls(**data if data else {})

    def save(self, file_path):
        with open(file_path, 'w') as f:
            yaml.dump(asdict(self), f, sort_keys=False)
        self.reset_taint()


# TODO: Finish the Machine -> DUT rename
class Machine:
    def __init__(self, db_dut, boots):
        self.db_dut = db_dut
        self.boots = boots

        self.pdu_port = self._create_pdu_port()

        # Executor associated (temporary)
        self.executor = Executor(self)

        # Make sure the updates are reflected in the runner's state
        self.update_config()

    def remove(self):
        self.executor.stop_event.set()
        self.executor.join()

    # Expose all the fields of the associated ConfigDUT object
    def __getattr__(self, attr):
        return getattr(self.db_dut, attr)

    @property
    def id(self):
        return self.mac_address

    @property
    def ready_for_service(self):
        return self.db_dut.ready_for_service

    @ready_for_service.setter
    def ready_for_service(self, val):
        self.db_dut.ready_for_service = val

        # Make sure the updates are reflected in the runner's state
        self.update_config()

        # Make sure the update gets written to disk.
        # HACK: This will force a reload of the configuration and thus
        # update the gitlab runner config
        self.db_dut.mars_db.save(config.MARS_DB_FILE)

    def _create_pdu_port(self):
        config_pdu = self.mars_db.pdus.get(self.db_dut.pdu)
        if config_pdu is None:
            return None

        if pdu := PDU.create(config_pdu.driver, config_pdu.name, config_pdu.config):
            for port in pdu.ports:
                if str(port.port_id) == str(self.db_dut.pdu_port_id):
                    port.min_off_time = self.db_dut.pdu_off_delay
                    return port

            raise ValueError('Could not find a matching port for %s on %s' % (self.db_dut.pdu_port_id, pdu))

    def update_config(self, db_dut=None):
        if db_dut:
            self.db_dut = db_dut

        self.pdu_port = self._create_pdu_port()

        # Make sure the test machines are assigned a static IP address
        # to facilitate testing services hosted on the test
        # machines themselves.
        self.boots.write_network_config(self.mac_address,
                                        self.db_dut.ip_address,
                                        self.full_name)


class Mars(Thread):
    def __init__(self, boots):
        super().__init__(name='MarsClient')

        self.boots = boots
        self.mars_db = None

        self._machines = {}

        self.stop_event = Event()

    @property
    def known_machines(self):
        return list(self._machines.values())

    def get_machine_by_id(self, machine_id, raise_if_missing=False):
        machine = self._machines.get(machine_id)
        if machine is None and raise_if_missing:
            raise ValueError(f"Unknown machine ID '{machine_id}'")
        return machine

    def _machine_update_or_create(self, db_dut):
        machine = self._machines.get(db_dut.mac_address)
        if machine is None:
            machine = Machine(db_dut, self.boots)
            self._machines[machine.mac_address] = machine
        else:
            machine.update_config(db_dut)

        self.mars_db.duts[machine.mac_address] = db_dut

        return machine

    def save_db_if_needed(self):
        if self.mars_db.is_tainted:
            print("Write-back the MarsDB to disk, after some local changes")
            # TODO: Print a list of the changes, possibly using deepdiff?
            self.mars_db.save(config.MARS_DB_FILE)

    def add_or_update_machine(self, fields: dict):
        mac_address = fields.pop("mac_address")

        if db_dut := self.mars_db.duts.get(mac_address):
            cur_state = asdict(db_dut)
            db_dut = ConfigDUT(**(cur_state | fields))
        else:
            db_dut = ConfigDUT(**fields)

        # TODO: Try to find a way not to have to add these fields
        db_dut.mac_address = mac_address
        db_dut.mars_db = self.mars_db

        machine = self._machine_update_or_create(db_dut)
        self.save_db_if_needed()

        return machine

    def sync_machines(self):
        self.mars_db = MarsDB.from_file(config.MARS_DB_FILE)

        local_only_machines = set(self.known_machines)
        for m in self.mars_db.duts.values():
            # Ignore retired machines
            if m.is_retired:
                continue

            machine = self._machine_update_or_create(m)

            # Remove the machine from the list of local-only machines
            local_only_machines.discard(machine)

        # Delete all the machines that are not found in MaRS
        for machine in local_only_machines:
            self._machines[machine.id].remove()
            del self._machines[machine.id]

        # Expose the gateway runners
        for gl in self.mars_db.gitlab.values():
            if gl.should_expose_gateway_runner:
                gl.gateway_runner.verify_or_renew_token(gl,
                                                        description=f"{config.FARM_NAME}-gateway",
                                                        tags=[f"{config.FARM_NAME}-gateway", 'CI-gateway'])
            else:
                gl.gateway_runner.remove(gl)

        # Expose the DUTs on all the forges
        for m in self.mars_db.duts.values():
            m.expose_on_forges()

        # Update the gitlab runner configuration
        gitlab.generate_runner_config(self.mars_db)

        # Save any change that may have happened after reloading
        self.save_db_if_needed()

    def stop(self, wait=True):
        self.stop_event.set()

        # Signal all the executors we want to stop
        for machine in self.known_machines:
            machine.executor.stop_event.set()

        if wait:
            self.join()

    def join(self):
        for machine in self.known_machines:
            machine.executor.join()
        super().join()

    def run(self):
        # Make sure the config file exists
        Path(config.MARS_DB_FILE).touch(exist_ok=True)

        # Set up a watch
        inotify = INotify()
        watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
        inotify.add_watch(config.MARS_DB_FILE, watch_flags)

        # Now wait for changes to the file
        last_sync = None
        while not self.stop_event.is_set():
            try:
                reason = None
                if last_sync is None:
                    reason = "Initial boot"
                elif len(inotify.read(timeout=1000)) > 0:
                    reason = "Got updated on disk"
                elif datetime.now() - last_sync > timedelta(minutes=30):
                    reason = "Periodic check"

                if reason:
                    logger.info(f"Syncing the MaRS DB. Reason: {reason}")

                    self.sync_machines()
                    last_sync = datetime.now()
            except Exception:
                traceback.print_exc()
                logger.info("Trying again in 60 seconds")
                time.sleep(60)
