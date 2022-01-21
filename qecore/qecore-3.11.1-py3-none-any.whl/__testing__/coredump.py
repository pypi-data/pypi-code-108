#!/usr/bin/env python3
from qecore.utility import run
#
def _set_test_starting_time():
    self.test_execution_start = run("date +\%\s").strip("\n")
#
def _get_coredump_list():
    self.coredump_list = run(f"coredumpctl list --since=@{self.test_execution_start}")
    self.list_of_results = self.coredump_list.rstrip("\n").split("\n")[1:]
    return self.list_of_results


def get_coredump_data(pid):
    run(f"echo 'q' | coredumpctl gdb {pid} 2&> /tmp/coredump.log")

    desired_data = ""    
    with open("/tmp/coredump_log.txt", "r") as f:
        next_line = f.readline()
        while next_line:
            # Parse correct lines to fetch debuginfo packages.
            if "debug" in next_line and "install" in next_line:
                _, target = next_line.split("install ", 1)
                desired_data += target.strip("\n") + " "
            
            next_line = f.readline()

    return desired_data


def _install_debuginfo_packages(pid):
    # We need gdb to be installed.
    run(f"sudo dnf install -y gdb >> /tmp/debuginfo_install.log")
    
    # Iterate a few times over the gdb to get packages and install them. 
    for _ in range(10):
        packages_to_install = get_coredump_data(pid)
        if packages_to_install:
            run(f"sudo dnf debuginfo-install -y {packages_to_install} >> /tmp/debuginfo_install.log")
        break


def _debug_all_coredumps():
    for coredump_line in _get_coredump_list():
        coredump_pid_to_investigate = coredump_line.split(" ")[4]
        _install_debuginfo_packages(coredump_pid_to_investigate)

        # All debuginfo packages should be installed now.
        run(f"echo 'thread apply all bt full' | coredumpctl gdb {coredump_pid_to_investigate} 2&> /tmp/coredump.log")
        context.embed(mime="text/plain",
                      data=open("/tmp/coredump.log", "r").read(),
                      caption=f"Coredump{coredump_pid_to_investigate}Log")


    context.embed(mime="text/plain",
                data=open("/tmp/debuginfo_install.log", "r").read(),
                caption=f"DebugInfoInstallLog")
