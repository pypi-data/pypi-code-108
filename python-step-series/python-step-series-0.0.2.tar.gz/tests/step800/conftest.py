import random
import time

import pytest

from stepseries import commands, exceptions, responses
from stepseries.step800 import STEP800

# Test configurations
# Please configure these presets before running the tests. Ensure to set
# "is_configured" to True, otherwise these tests will be skipped.
# The defaults for these tests assume you are using an SM-42BYG011-25
# 12V stepper motor. Change the configurations as needed to match your
# motor. Examples for a variety of steppers can be found here:
# https://github.com/ponoor/step-series-support/tree/main/configGenerator

# Secondly, these tests do require the board to be powered via the
# barrel plug or screw terminal with at least 8V. USB power is not
# enough to power the drivers so some tests will fail.


class TestPresets:
    is_configured: bool = False

    # Device networking settings
    id: int = 0
    address: str = "10.1.16.20"
    port: int = 50000
    server_address: str = "0.0.0.0"
    server_port: int = 50100
    add_id_to_args: bool = True

    # The singular motor ID to test on (1 - 8, 255)
    # 255 means run the command on all motors
    # Keep at None to randomize (once per session)
    motor_id: int = None

    # Allow motors to be physically ran
    # Do not make True if you have no motor(s) connected
    enable_motors: bool = False

    # Are you using a config file?
    using_config_file: bool = False

    # Is there a homing switch connected?
    # Also keep this False if you do not wish to run homing tests
    # or tests that require the home switch
    homesw_exists: bool = False

    # Is the EM-brake connected?
    embrake_exists: bool = False

    # Motor Driver Settings
    microstep_mode: int = 7
    low_speed_optimize_threshold: int = 20

    # Voltage & Current Mode Settings
    kval_hold: int = 119
    kval_run: int = 238
    kval_acc: int = 238
    kval_dec: int = 238

    bemf_int_speed: int = 7895
    bemf_st_slp: int = 106
    bemf_fn_slp_acc: int = 234
    bemf_fn_slp_dec: int = 234

    # Speed Profile Settings
    acc: float = 2000
    dec: float = 2000
    max_speed: float = 620

    # These are defaults pre-set on the device
    # They may need to be changed depending on the above you set
    default_acc: float = 1000
    default_dec: float = 1000
    default_max_speed: float = 650

    fullstep_speed: float = 14625

    # Homing Settings
    homing_direction: int = 1  # 0 or 1
    homing_speed: float = 620.0


@pytest.fixture(scope="package")
def device(wait_for) -> STEP800:
    device = STEP800(
        TestPresets.id,
        TestPresets.address,
        TestPresets.port,
        TestPresets.server_address,
        TestPresets.server_port,
        TestPresets.add_id_to_args,
    )

    # Send the start-up command
    try:
        wait_for(device, commands.SetDestIP(), responses.DestIP)

        # Verify the device type through the firmware
        version: responses.Version = device.get(commands.GetVersion())
        if "STEP800" not in version.firmware_name:
            device.close()
    except (TimeoutError, exceptions.ClientClosedError):
        device.close()

    return device


@pytest.fixture(scope="package")
def motor_id() -> int:
    if not TestPresets.motor_id:
        valid_ids = list(range(1, 9))
        return valid_ids[random.randint(0, len(valid_ids) - 1)]

    return TestPresets.motor_id


@pytest.fixture(scope="class", autouse=True)
def reset_device(request, device: STEP800, wait_for) -> None:
    yield
    if request.node.get_closest_marker("reset_800_device"):
        try:
            # Reset the entire device
            wait_for(device, commands.ResetDevice(), responses.Booted)

            # Re-Initialize the device
            wait_for(device, commands.SetDestIP(), responses.DestIP)

            # Small delay to allow processes to boot
            time.sleep(0.5)
        except (TimeoutError, exceptions.ClientClosedError):
            device.close()


@pytest.fixture(autouse=True)
def skip_if_disconnected(request, device: STEP800):
    if request.node.get_closest_marker("skip_800_disconnected"):
        if device.is_closed:
            pytest.skip("hardware not detected")


@pytest.fixture(autouse=True)
def check_motors(request):
    if request.node.get_closest_marker("check_800_motors"):
        if not TestPresets.is_configured:
            pytest.skip("presets not configured")
        if not TestPresets.enable_motors:
            pytest.skip("motors are disabled")


@pytest.fixture(autouse=True)
def check_homing_switch(request):
    if request.node.get_closest_marker("check_800_homesw"):
        if not TestPresets.is_configured:
            pytest.skip("presets not configured")
        if not TestPresets.homesw_exists:
            pytest.skip("no homing switch is connected")


@pytest.fixture(autouse=True)
def check_embrake(request):
    if request.node.get_closest_marker("check_800_embrake"):
        if not TestPresets.is_configured:
            pytest.skip("presets not configured")
        if not TestPresets.embrake_exists:
            pytest.skip("no electromagnetic brake is connected")


@pytest.fixture(autouse=True)
def skip_if_not_configured(request):
    if request.node.get_closest_marker("skip_800_not_configured"):
        if not TestPresets.is_configured:
            pytest.skip("presets not configured")


@pytest.fixture
def presets():
    return TestPresets
