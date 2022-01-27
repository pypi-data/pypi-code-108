from tcell_agent.instrumentation.decorators import safe_wrap_function
from tcell_agent.rust.native_agent import get_native_lib
from tcell_agent.events.server_agent_packages import ServerAgentPackagesEvent
from tcell_agent.events.settings_event import SettingsEvent
from tcell_agent.system_info import get_packages


def add_packages_event(initial_events):
    sape = ServerAgentPackagesEvent()
    for package in get_packages():
        sape.add_package(package.key, package.version)
    initial_events.append(sape)


def get_startup_events():
    initial_events = []

    safe_wrap_function(
        "Create ServerAgentPackagesEvent",
        add_packages_event,
        initial_events
    )

    safe_wrap_function(
        "SettingsEvent: native_lib_loaded",
        lambda: initial_events.append(SettingsEvent("native_lib_loaded", get_native_lib() is not None))
    )

    return initial_events
