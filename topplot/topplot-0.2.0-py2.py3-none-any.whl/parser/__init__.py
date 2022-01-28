from io import IOBase
import re
import os
import pathlib
import tempfile
from typing import Callable
import sys

from ..config import Config
from ..toptype import TopType
from ..utils import dhms_to_sec

# ------------------------------------------------------------------------------


class Parser:
    """Parses top logs, munges the data according to config, emits dataframes."""

    # pylint: disable=import-outside-toplevel
    from ._list_processes import list_processes
    from ._munge import (
        munge_to_files,
        dataframes_from_files,
    )
    from ._regex import (
        _setup_regex,
        _generate_procps_re_process,
        _generate_busybox_re_process,
    )

    # --------------------------------------------------------------------------

    class ParseContext:
        """Intermediary data shuttle."""

        def __init__(self):
            self.cpu_id = None
            self.current_entry = {}
            self.line_count = 0
            self.batch_count = 0
            self.first_secs = None
            self.prev_secs = None
            self.re_process = None

    # --------------------------------------------------------------------------

    def __init__(self, config: Config):
        self.config = config

        self._highest_cpuid = None
        self._processes = {}
        self._processes_of_interest = {}
        self._top_entries = []

        self._re_busybox_cpu = None
        self._re_busybox_load_average = None

        self._re_procps_cpu = None
        self._re_procps_mem = None
        self._re_procps_swap = None
        self._re_procps_tasks = None

        self._re_ignore_processes_regex = None
        self._re_process_header = None
        self._re_top_busybox = None
        self._re_top_procps = None

        self._setup_regex()
        self._setup_tmpdir_and_files()

    # --------------------------------------------------------------------------

    def get_poi_count(self) -> int:
        """Return count of processes of interest."""
        return len(self._processes_of_interest)

    # --------------------------------------------------------------------------

    def _setup_tmpdir_and_files(self) -> None:
        """Prepare for the temporary data files."""
        if self.config.tmpdir is None:
            self.tmpdir_context_manager = tempfile.TemporaryDirectory()
            self.tmpdir = self.tmpdir_context_manager.name
        else:
            self.tmpdir = self.config.tmpdir
            try:
                pathlib.Path(self.tmpdir).mkdir(mode=0o700, parents=True, exist_ok=True)
            except PermissionError as e:
                print(f"Can't create self.tmpdir: {e}")
                sys.exit(1)

        if self.config.verbosity > 0:
            print(f"tmpdir: {self.tmpdir}")

        self._cpu_data_filename = os.path.join(self.tmpdir, "cpu.data")
        self._mem_data_filename = os.path.join(self.tmpdir, "mem.data")
        self._task_data_filename = os.path.join(self.tmpdir, "task.data")
        self._poi_combined_data_filename = os.path.join(
            self.tmpdir, "poi combined.data"
        )
        self._poi_data_filename = os.path.join(self.tmpdir, "poi.data")

    # --------------------------------------------------------------------------

    def parse(self) -> None:
        """Extract info from the top log file.

        Note: This only extracts the data in to internal data structures.
              Further munging in to temporary files, and then to dataframes
              is needed for graphing."""

        context = Parser.ParseContext()

        re_first_line = None
        parse_header: Callable[[IOBase, Parser.ParseContext, re.Match], None] = None

        # Encoding set to ISO-8859-1 in response to 0xFF char used in a threadname (!)
        # causing topplot to die horribly. Will this have knock on effects in non-ASCII
        # environments?

        with open(self.config.toplog_filename, encoding="ISO-8859-1") as top_log:

            for (
                line
            ) in top_log:  # Swapping over to .readlines(10000): leads to Bad Things
                context.line_count += 1
                line = line.rstrip()
                if not line:
                    continue

                # print(f"{context.line_count}: len: {len(line)}", file=sys.stderr)

                line_handled = False

                if not re_first_line:
                    top_procps_line_match = self._re_top_procps.match(line)
                    if top_procps_line_match:
                        re_first_line = self._re_top_procps
                        parse_header = self._parse_procps_header
                        self.config.toptype = TopType.PROCPS
                        self.config.has_swap = True
                        self.config.has_full_task_info = True
                    else:
                        top_busybox_line_match = self._re_top_busybox.match(line)
                        if top_busybox_line_match:
                            re_first_line = self._re_top_busybox
                            parse_header = self._parse_busybox_header
                            self.config.toptype = TopType.BUSYBOX
                            self._highest_cpuid = 0

                if re_first_line:
                    top_line_match = re_first_line.match(line)
                    if top_line_match:
                        parse_header(top_log, context, top_line_match)
                        context.batch_count += 1
                        line_handled = True

                if not line_handled:
                    #  There won't be a current_entry if the start of the file
                    #  is corrupted or we're skipping content until
                    #  self.config.start_time
                    if context.current_entry:
                        # Expecting a process line at this point
                        # print(f"{context.line_count} : >{line}<", file=sys.stderr)
                        process_match = context.re_process.match(line)

                        if process_match:
                            if self.config.verbosity > 4:
                                print(
                                    f"process line match groups: {process_match.groups()}"
                                )
                            self._parse_process_line(
                                line, context.current_entry["timestamp"], process_match
                            )
                        else:
                            if self.config.verbosity > 3:
                                print(f"process line no match: '{line}'")

        if context.current_entry:  # stash the final entry
            self._top_entries.append(context.current_entry)

        if self._highest_cpuid is None:
            # Rather than expend effort on max() calls, assume that the header is sorted
            self._highest_cpuid = context.cpu_id

    # --------------------------------------------------------------------------

    def _parse_busybox_header(
        self, top_log: IOBase, context: ParseContext, header_match: re.Match
    ) -> None:
        """Parse a BusyBox format header block."""

        # When starting a new entry, stash previous one
        if context.current_entry:
            self._top_entries.append(context.current_entry)

        groupdict = header_match.groupdict()

        context.current_entry = groupdict

        # BusyBox doesn't emit a timestamp, so fake one with the batch count.
        # Sad times :(
        current_secs = context.batch_count
        context.current_entry["timestamp"] = context.batch_count

        if context.first_secs is None:
            context.first_secs = current_secs

        if self.config.start_time:
            if isinstance(self.config.start_time, str):
                self.config.start_time = int(self.config.start_time)

            if current_secs < self.config.start_time:
                context.current_entry = None
                return

        if self.config.stop_time:
            if isinstance(self.config.stop_time, str):
                if (
                    self.config.stop_time[0:1] == "+"
                    or self.config.stop_time[0:1] == "<"
                ):
                    self.config.stop_time = (
                        context.first_secs + self.config.stop_time[1:]
                    )

            if current_secs >= self.config.stop_time:
                context.current_entry = None
                return

        # BusyBox header lines are of structure:
        #
        #   Mem: 27436964K used, 5056536K free, 317416K shrd, 1433660K buff, 11810180K cached
        #   CPU:   5% usr   3% sys   0% nic  83% idle   7% io   0% irq   0% sirq
        #   Load average: 2.44 2.24 2.30 3/2473 953092
        #     PID  PPID USER     STAT   VSZ %VSZ %CPU COMMAND
        #    7418  7417 jonathan S     606m   2%   1% kitty
        #
        # But:
        #
        #  CPU may be CPU${n} with multiple lines
        #  Process lines may have an extra CPU column indicating cpu_id

        have_all_expected_header_lines = True
        pull_line = True
        line = ""
        for regex in [
            self._re_busybox_cpu,
            self._re_busybox_load_average,
        ]:
            if pull_line:
                line = top_log.readline()
            pull_line = True

            if line:
                context.line_count += 1
                match = regex.match(line)
                if match:
                    if regex is self._re_busybox_cpu:
                        context.cpu_id = match.group("cpu_id")
                        if context.cpu_id is not None:
                            # Handle split out CPU info
                            self.config.has_cpu_rows = True
                            pull_line = False
                            while match:
                                context.line_count += 1
                                context.cpu_id = match.group("cpu_id")
                                temp_dict = match.groupdict()
                                for key in [
                                    "user",
                                    "system",
                                    "nice",
                                    "idle",
                                    "wait",
                                    "hw_irq",
                                    "sw_irq",
                                ]:
                                    temp_dict[
                                        f"cpu{context.cpu_id}_{key}"
                                    ] = temp_dict.pop("cpu_" + key)
                                context.current_entry.update(temp_dict)

                                # Handle multiple cpu_id blocks on a single line
                                line = line[match.end() :]
                                line = line.lstrip()
                                if not line:
                                    line = top_log.readline()
                                match = regex.match(line)
                            context.line_count -= 1
                        else:
                            context.current_entry.update(match.groupdict())
                    else:
                        context.current_entry.update(match.groupdict())
                else:
                    have_all_expected_header_lines = False
                    print(
                        f">ERR: line {context.line_count}: >{line}<\n   :"
                        f" Unexpected match failure for {regex.pattern}",
                        file=sys.stderr,
                    )
            else:
                have_all_expected_header_lines = False

        if have_all_expected_header_lines:
            # Process header line
            line = top_log.readline()
            process_header_pattern = ""
            if not self._re_process_header:
                (
                    process_header_pattern,
                    self._re_process_header,
                    context.re_process,
                ) = self._generate_busybox_re_process(line)
                if re.search(r"[+*]CPU ", self._re_process_header.pattern):
                    self.config.has_cpu_column = True
            if not self._re_process_header.match(line):
                print(
                    f">ERR: line {context.line_count}: expected a process header"
                    f" line ({process_header_pattern}),\n got>{line}<",
                    file=sys.stderr,
                )

            context.line_count += 2

    # --------------------------------------------------------------------------

    def _parse_procps_header(
        self, top_log: IOBase, context: ParseContext, header_match: re.Match
    ) -> None:
        """Parse a procps format header block."""

        # starting a new entry, so stash previous one
        if context.current_entry:
            self._top_entries.append(context.current_entry)

        groupdict = header_match.groupdict()

        try:
            assert groupdict["timestamp"] is not None
        except AssertionError:
            print(f"ERR: Expected a timestamp field at line {context.line_count} !?")
            return

        context.current_entry = groupdict

        # Handle start/stop times
        current_secs = dhms_to_sec(context.current_entry["timestamp"])

        if context.first_secs is None:
            context.first_secs = current_secs

        if context.prev_secs is not None:
            # Handle midnight wrapping
            # Not sure that
            while current_secs < context.prev_secs:
                current_secs += 24 * 60 * 60

        # Convert to play nicely with matplotlib
        context.current_entry["timestamp"] = current_secs

        context.prev_secs = current_secs

        if self.config.start_time:
            if isinstance(self.config.start_time, str):
                offset = dhms_to_sec(self.config.start_time[1:])

                self.config.start_time = current_secs + offset

            if current_secs < self.config.start_time:
                context.current_entry = None
                return

        if self.config.stop_time:
            if isinstance(self.config.stop_time, str):
                offset = dhms_to_sec(self.config.stop_time[1:])

                if self.config.stop_time[0:1] == "+":
                    self.config.stop_time = current_secs + offset

                elif self.config.stop_time[0:1] == "<":
                    self.config.stop_time = context.first_secs + offset

            if current_secs >= self.config.stop_time:
                context.current_entry = None
                return

        # By default the header lines are of structure:
        #   Tasks:
        #   Cpu(s):
        #   Mem:
        #   Swap:
        #
        #   PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND
        #
        # But Cpu can be aggregate or split out by core, and the process header
        # line is mutable

        have_all_expected_header_lines = True
        pull_line = True
        line = ""
        for regex in [
            self._re_procps_tasks,
            self._re_procps_cpu,
            self._re_procps_mem,
            self._re_procps_swap,
        ]:
            if pull_line:
                line = top_log.readline()
            pull_line = True

            if line:
                context.line_count += 1
                match = regex.match(line)
                if match:
                    if regex is self._re_procps_cpu:
                        context.cpu_id = match.group("cpu_id")
                        if context.cpu_id is not None:
                            # Handle split out CPU info
                            self.config.has_cpu_rows = True
                            pull_line = False
                            while match:
                                context.line_count += 1
                                context.cpu_id = match.group("cpu_id")
                                temp_dict = match.groupdict()
                                for key in [
                                    "user",
                                    "system",
                                    "nice",
                                    "idle",
                                    "wait",
                                    "hw_irq",
                                    "sw_irq",
                                    "steal",
                                ]:
                                    temp_dict[
                                        f"cpu{context.cpu_id}_{key}"
                                    ] = temp_dict.pop("cpu_" + key)
                                context.current_entry.update(temp_dict)

                                # Handle multiple cpu_id blocks on a single line
                                line = line[match.end() :]
                                line = line.lstrip()
                                if not line:
                                    line = top_log.readline()
                                match = regex.match(line)
                            context.line_count -= 1
                        else:
                            context.current_entry.update(match.groupdict())
                    else:
                        context.current_entry.update(match.groupdict())
                else:
                    have_all_expected_header_lines = False
                    print(
                        f">ERR: line {context.line_count}: >{line}<\n   :"
                        f" Unexpected match failure for {regex.pattern}",
                        file=sys.stderr,
                    )
            else:
                have_all_expected_header_lines = False

        if have_all_expected_header_lines:
            # Blank line
            line = top_log.readline()  # blank line
            if len(line) != 1:  # 1 for newline char
                print(
                    f">ERR: line {context.line_count}: >{line}<\nExpected a blank line"
                    " here.",
                    file=sys.stderr,
                )

            # Process header line
            line = top_log.readline()
            process_header_pattern = ""
            if not self._re_process_header:
                (
                    process_header_pattern,
                    self._re_process_header,
                    context.re_process,
                ) = self._generate_procps_re_process(line)
                if " +P " in self._re_process_header.pattern:
                    self.config.has_cpu_column = True
                    # TODO: confirm no longer required
                    # if not self.config.has_cpu_rows:
                    #    print(
                    #        "Currently when tracking per process CPU core"
                    #        " use, topplot needs per core CPU information"
                    #        " too."
                    #    )
                    #    print(
                    #        "For more information see the 'Workaround'"
                    #        " section"
                    #        " here:"
                    #        " https://gitlab.com/eBardie/topplot/-/issues/11"
                    #    )
                    #    sys.exit(1)
            if not self._re_process_header.match(line):
                print(
                    f">ERR: line {context.line_count}: expected a process header"
                    f" line ({process_header_pattern}),\n got>{line}<",
                    file=sys.stderr,
                )

            context.line_count += 2

    # --------------------------------------------------------------------------

    def _parse_process_line(self, line: str, timestamp: int, process_match: re.Match):
        """Parse a process line."""
        groupdict = process_match.groupdict()

        pid = process_match.group("pid")

        if self.config.toptype == TopType.BUSYBOX:
            # BusyBox *can* merge PID with PPID, so we alway parse PPID in to PID.
            # This may leave a space in there, so remove it now for consistency.
            pid = pid.replace(" ", "")

        del groupdict["pid"]

        command = process_match.group("command")
        del groupdict["command"]

        # Just the basename please
        if command[0:1] == "/":
            slash = command.rfind("/")
            if slash > -1:
                command = command[slash + 1 :]

        if command == "" or len(command) == 0:
            print(f"WARN: command empty for line: {line}")

        # Skip this process if it matches the ignore regex and doesn't match
        # the POI regex
        if (
            self._re_ignore_processes_regex
            and self._re_ignore_processes_regex.match(command)
        ) and not (self.config.poi_regex and self.config.poi_regex.match(command)):
            return

        if command not in self._processes:
            self._processes[command] = {}

        if pid not in self._processes[command]:
            self._processes[command][pid] = {}
            self._processes[command][pid]["timestamps"] = {}

            # Storing at this point obviously won't cope with processes that
            # update their own ARGV[0]
            self._processes[command][pid]["commandline"] = groupdict["commandline"]

            if self.config.poi_acc_cpu:
                self._processes[command][pid]["acc_cpu"] = 0
            if self.config.poi_acc_mem:
                self._processes[command][pid]["acc_mem"] = 0
            if self.config.poi_peak_cpu:
                self._processes[command][pid]["max_cpu"] = 0
            if self.config.poi_peak_mem:
                self._processes[command][pid]["max_mem"] = 0

        # Bizarrely procps top can throw out reports where all processes' CPU
        # column entries are negative
        cpu_value = float(groupdict["cpu"])
        if cpu_value < 0:
            groupdict["cpu"] = str(cpu_value * -1)

        if self.config.poi_acc_cpu:
            self._processes[command][pid]["acc_cpu"] += float(groupdict["cpu"])

        if self.config.poi_acc_mem:
            self._processes[command][pid]["acc_mem"] += float(groupdict["mem"])

        if self.config.poi_peak_cpu:
            cpu = float(groupdict["cpu"])
            if cpu > self._processes[command][pid]["max_cpu"]:
                self._processes[command][pid]["max_cpu"] = cpu

        if self.config.poi_peak_mem:
            mem = float(groupdict["mem"])
            if mem > self._processes[command][pid]["max_mem"]:
                self._processes[command][pid]["max_mem"] = mem

        self._processes[command][pid]["timestamps"][timestamp] = groupdict

        if self.config.toptype == TopType.BUSYBOX:
            # BusyBox batch mode (at least <= 1.35.1) has no way of getting
            # per core CPU info, so spend energy extracting max CPU core on
            # every line :(
            if "cpu_id" in groupdict:
                if self._highest_cpuid is None:
                    self._highest_cpuid = 0
                cpu_id = int(groupdict["cpu_id"])
                if cpu_id > self._highest_cpuid:
                    self._highest_cpuid = cpu_id

    # --------------------------------------------------------------------------
