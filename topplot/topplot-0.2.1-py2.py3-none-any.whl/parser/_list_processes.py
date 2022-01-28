# ------------------------------------------------------------------------------
# Early non-graphing output


def list_processes(self):
    for command in sorted(self.processes.keys()):
        pids = []
        for pid in sorted(self.processes[command].keys()):
            if self.config.list_processes >= 2:
                print(
                    f"{command} [{pid}]"
                    f" {self.processes[command][pid]['commandline']}"
                )
            else:
                pids.append(pid)

        if self.config.list_processes == 0:
            print(f"{command}")
        elif self.config.list_processes == 1:
            print(f"{command} x{len(pids)} {pids}")


# ------------------------------------------------------------------------------
