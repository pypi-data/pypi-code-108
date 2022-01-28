from ..dataframes import Dataframes
from ..tempfile import (
    CpuFiles,
    dataframe_from_process_graph_data,
    from_csv,
    write_datafile as write_temp_datafile,
)
from .topndict import TopNDict2
from ..utils import warn

# ------------------------------------------------------------------------------

CPU_COLUMNS = ["user", "system", "nice", "idle", "wait", "hw_irq", "sw_irq"]

# ------------------------------------------------------------------------------


def _write_datafile(self, filename, source, keys):
    """Write data if allowed by config."""
    if not self.config.allow_write:
        return
    write_temp_datafile(filename, source, keys)


# ------------------------------------------------------------------------------


def munge_to_files(self):
    """Convert internal data structures to temp files according to config."""
    _munge_header_info(self)
    _munge_poi_info(self)
    _munge_poi_data_to_files(self)


# ------------------------------------------------------------------------------


def _munge_header_info(self):
    """Munge top's header info to temp files."""
    if self._highest_cpuid:
        self.config.cores = int(self._highest_cpuid) + 1

    if self.config.has_cpu_rows:
        cpu_keys = ["load_average"]
        column_index = 3
        columns = CPU_COLUMNS
        if self.config.with_cpu_steal:
            columns.append("steal")
        for i in range(0, self.config.cores):
            for column in columns:
                cpu_keys.append(f"cpu{i}_{column}")
                column_index += 1
    else:
        cpu_keys = [
            "load_average",
            "cpu_user",
            "cpu_system",
            "cpu_nice",
            "cpu_idle",
            "cpu_wait",
            "cpu_hw_irq",
            "cpu_sw_irq",
        ]
        if self.config.with_cpu_steal:
            cpu_keys.append("steal")

    _write_datafile(self, self._cpu_data_filename, self._top_entries, cpu_keys)

    mem_keys = [
        "mem_used",
        "mem_free",
        "mem_buffers",
        self.config.mem_cached_or_available,
    ]

    if self.config.has_swap:
        mem_keys.append("swap_free")

    _write_datafile(self, self._mem_data_filename, self._top_entries, mem_keys)

    task_keys = ["task_running"]
    if self.config.has_full_task_info:
        task_keys += ["task_sleeping", "task_stopped", "task_zombie"]

    _write_datafile(self, self._task_data_filename, self._top_entries, task_keys)


# ------------------------------------------------------------------------------


def _munge_poi_info(self):
    """Munge top's poi info to temp data structures."""
    acc_cpu = None
    acc_mem = None
    peak_cpu = None
    peak_mem = None

    # Keep track of top N lists on request
    if self.config.poi_acc_cpu:
        acc_cpu = TopNDict2(
            self.config.poi_acc_cpu,
            "accumlated cpu",
            self._processes_of_interest,
            verbosity=self.config.verbosity,
        )

    if self.config.poi_acc_mem:
        acc_mem = TopNDict2(
            self.config.poi_acc_mem,
            "accumlated mem",
            self._processes_of_interest,
            verbosity=self.config.verbosity,
        )

    if self.config.poi_peak_cpu:
        peak_cpu = TopNDict2(
            self.config.poi_peak_cpu,
            "peak cpu",
            self._processes_of_interest,
            verbosity=self.config.verbosity,
        )

    if self.config.poi_peak_mem:
        peak_mem = TopNDict2(
            self.config.poi_peak_mem,
            "peak mem",
            self._processes_of_interest,
            verbosity=self.config.verbosity,
        )

    # Loop over all processes, keeping tabs on top N lists and filtering for POI
    for command in self._processes:  # pylint: disable=consider-using-dict-items
        for pid in self._processes[command]:
            # Update top-N lists if required
            if acc_cpu:
                acc_cpu.append(command, pid, self._processes[command][pid]["acc_cpu"])

            if acc_mem:
                acc_mem.append(command, pid, self._processes[command][pid]["acc_mem"])

            if peak_cpu:
                peak_cpu.append(command, pid, self._processes[command][pid]["max_cpu"])

            if peak_mem:
                peak_mem.append(command, pid, self._processes[command][pid]["max_mem"])

            # Run main filters
            for timestamp in self._processes[command][pid]["timestamps"].keys():
                if self.config.filterfoo(command, pid, timestamp):
                    if command not in self._processes_of_interest:
                        if command == "":
                            warn(
                                f"Adding empty command (?) for pid {pid} at"
                                f" {timestamp}"
                            )
                        self._processes_of_interest[command] = {}

                    self._processes_of_interest[command][pid] = True
                    continue

    # Extract POI from top-N lists if required. Also dump info to stdout on request
    if self.config.poi_acc_cpu:
        acc_cpu.complete()

    if self.config.poi_acc_mem:
        acc_mem.complete()

    if self.config.poi_peak_cpu:
        peak_cpu.complete()

    if self.config.poi_peak_mem:
        peak_mem.complete()


# ------------------------------------------------------------------------------


def _munge_poi_data_to_files(self):
    """Munge data for processes of interest to temp file(s)"""

    data_by_core = CpuFiles(self.config, self.tmpdir, self._poi_combined_data_filename)

    with open(self._poi_data_filename, "w", encoding="ISO-8859-1") as poi_data:
        keys = ["cpu", "mem"]

        # Data
        block_index = -1

        for (
            command
        ) in self._processes_of_interest:  # pylint: disable=consider-using-dict-items
            if command == "":
                warn("Skipping empty command (?)")
                continue

            pids = self._processes_of_interest[command]

            for pid in pids:
                if not self._processes[command][pid]["timestamps"]:
                    warn(f"Unexpected lack of timestamps for {command}:{pid}")
                    continue

                block_index += 1

                if len(pids) > 1:
                    qualified_command = f"{command}:{pid}"
                    if "threadname" in self._processes[command][pid]:
                        qualified_command += ":" + self._processes[command][pid]["threadname"]
                else:
                    qualified_command = f"{command}"

                # Header
                line = "timestamp"
                for key in keys:
                    key = key.replace("_", " ")
                    line = f'{line} "{qualified_command} - {key}"'

                header = f"\n{line}\n"
                poi_data.write(header)

                # Data
                for timestamp in self._processes[command][pid]["timestamps"].keys():
                    line = f"{timestamp}"
                    for key in keys:
                        line = (
                            f"{line}"
                            f" {self._processes[command][pid]['timestamps'][timestamp][key]}"
                        )
                    txt = line + "\n"
                    poi_data.write(txt)
                    if self.config.has_cpu_column:
                        core = int(
                            self._processes[command][pid]["timestamps"][timestamp][
                                "cpu_id"
                            ]
                        )

                        # Write data to split out file
                        data_by_core.write(core, header, txt)

                        # Update per core aggregate pile(s) as appropriate
                        if self.config.plot_poi_cpu_sum:
                            data_by_core.add_poi_cpu(
                                core,
                                timestamp,
                                float(
                                    self._processes[command][pid]["timestamps"][
                                        timestamp
                                    ]["cpu"]
                                ),
                            )

                        if self.config.plot_poi_mem_sum:
                            data_by_core.add_poi_mem(
                                core,
                                timestamp,
                                self._processes[command][pid]["timestamps"][timestamp][
                                    "mem"
                                ],
                            )

                poi_data.write("\n")

                if self.config.has_cpu_column:
                    data_by_core.seal_register()

        data_by_core.close()


# ------------------------------------------------------------------------------


def dataframes_from_files(self) -> Dataframes:
    """Prepare dataframes from previously munged temp files."""
    dataframes = Dataframes()

    dataframes.cpus_df = from_csv(self._cpu_data_filename)
    dataframes.tasks_df = from_csv(self._task_data_filename)
    dataframes.poi_df = dataframe_from_process_graph_data(self._poi_data_filename)
    dataframes.mem_df = from_csv(self._mem_data_filename)

    # Add extra column(s) for summary CPU "exec" info
    ns = range(self.config.cores) if self.config.has_cpu_rows else [""]
    for n in ns:
        dataframes.cpus_df[f"cpu{n} exec"] = (
            dataframes.cpus_df[f"cpu{n} system"]
            + dataframes.cpus_df[f"cpu{n} user"]
            + dataframes.cpus_df[f"cpu{n} nice"]
        )

    # Prep the poi-by-core data
    dataframes.core_dfs = []
    if self.config.has_cpu_column and self.config.cores > 1:
        for core in range(self.config.cores):
            dataframes.core_dfs.append(
                dataframe_from_process_graph_data(
                    f"{self.tmpdir}/cpu{core}_process.data"
                )
            )

    return dataframes


# ------------------------------------------------------------------------------
