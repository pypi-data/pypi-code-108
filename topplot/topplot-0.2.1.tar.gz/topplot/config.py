# pylint: disable=no-member

import argparse
import os
import re
import sys

from .rcparams import rcParams
from .utils import dhms_to_sec, die, is_dir_writable

poi_acc_cpu_default = 10

# ------------------------------------------------------------------------------


class Config:
    def __init__(self, app, version):
        self._app = app
        self.version = version

        self._filterfoos = []

        self.cores = 1
        self.toptype = None

        # Some versions of procps top have values that others don't
        # So far it's either mem_cached or mem_available
        self.mem_cached_or_available = "mem_cached"
        self.mem_unit = "KiB"

        self.has_cpu_column = False
        self.has_cpu_rows = False
        self.has_full_task_info = False
        self.has_swap = False

        self.poi_acc_cpu = None
        self.poi_categories = "categories: "  # subtitle of processes graph key
        self.profiling_tag = None
        self.start_time = None
        self.stop_time = None
        self.threads_not_tasks = False

        self._parse_commandline_arguments()
        self._handle_commandline_arguments()

    # --------------------------------------------------------------------------

    def _parse_commandline_arguments(self):
        self.parser = argparse.ArgumentParser(
            description=(
                "Munge data logged from the top utility in to graphs using"
                " GnuPlot.\nNote that Processes of Interest (POI) is a common-or-garden"
                " bucket, so however you select the processes, once they're in the"
                " bucket, they're just another process sloshing around in the bucket."
            )
        )

        self.parser.add_argument(
            "-f",
            "--file",
            dest="toplog_filename",
            metavar="PATH",
            default="top.log",
            help="Name of the file to munge (default: top.log)",
        )

        self.parser.add_argument(
            "-s",
            "--start",
            dest="start_time",
            metavar="TIMESTAMP",
            help=(
                "Start with timestamp TIMESTAMP ([D:]HH:MM:SS or >[[[D:]H+:]M+:]SS"
                " where the prefix '>' indicates an offset from the earliest log entry)"
            ),
        )

        self.parser.add_argument(
            "-S",
            "--stop",
            dest="stop_time",
            metavar="TIMESTAMP",
            help=(
                "Stop  with timestamp TIMESTAMP ([D:]HH:MM:SS or (+|<)[[[D:]H+:]M+:]SS"
                " where the prefix '<'indicates an offset from the earliest log entry"
                " and the + prefix an offset from the starting entry's timestamp)"
            ),
        )

        self.parser.add_argument(
            "-c",
            "--acc-cpu",
            dest="poi_acc_cpu",
            metavar="N",
            nargs="?",
            type=int,
            const=poi_acc_cpu_default,
            help="Top N processes ranked by accumulated CPU use (default: 10)",
        )

        self.parser.add_argument(
            "-m",
            "--acc-mem",
            dest="poi_acc_mem",
            metavar="N",
            nargs="?",
            type=int,
            const=10,
            help="Top N processes ranked by accumulated MEM use (default: 10)",
        )

        self.parser.add_argument(
            "--peak-cpu",
            dest="poi_peak_cpu",
            metavar="N",
            nargs="?",
            type=int,
            const=10,
            help="Top N processes ranked by peak CPU use (default: 10)",
        )

        self.parser.add_argument(
            "--peak-mem",
            dest="poi_peak_mem",
            metavar="N",
            nargs="?",
            type=int,
            const=10,
            help="Top N processes ranked by peak MEM use (default: 10)",
        )

        self.parser.add_argument(
            "--pct-cpu",
            dest="poi_cpu",
            metavar="PCT",
            nargs="?",
            type=int,
            const=20,
            help=(
                "Any process using more than PCT%% of memory will be graphed"
                " (default: 20)"
            ),
        )

        self.parser.add_argument(
            "--pct-mem",
            dest="poi_mem",
            metavar="PCT",
            nargs="?",
            type=int,
            const=3,
            help=(
                "Any process using more than PCT%% of cpu will be graphed (default: 3)"
            ),
        )

        self.parser.add_argument(
            "--prio",
            dest="poi_prio",
            metavar="cmpPRIO",
            nargs="?",
            type=str,
            const="=RT",
            help=(
                "Any process with priority =, <=, >=, <, or > to PRIO (default: '=RT',"
                " note the prefixed comparison operator)"
            ),
        )

        self.parser.add_argument(
            "-C",
            "--only-proc-cpu",
            dest="include_process_mem",
            action="store_false",
            help="Don't plot processes' mem info",
        )

        self.parser.add_argument(
            "-M",
            "--only-proc-mem",
            dest="include_process_cpu",
            action="store_false",
            help="Don't plot processes' cpu info",
        )

        self.parser.add_argument(
            "--with-cpu-steal",
            dest="with_cpu_steal",
            action="store_true",
            help="Plot CPU steal data",
        )

        self.parser.add_argument(
            "poi_regex",
            metavar="REGEX",
            nargs="?",
            help="Python style regex for names of processes to graph",
        )

        self.parser.add_argument(
            "-I",
            "--ignore",
            dest="ignore_processes_regex",
            metavar="REGEX",
            help="Python style regex for names of processes to ignore",
        )

        self.parser.add_argument(
            "-i",
            dest="ignore_case",
            action="store_true",
            help="Use case insensitive matching",
        )

        self.parser.add_argument(
            "--dont-plot-cpu-lines",
            dest="plot_poi_cpu_lines",
            action="store_false",
            help=(
                "Don't display the individual processes' cpu usage. Implies"
                " --plot-cpu-sum"
            ),
        )

        self.parser.add_argument(
            "--dont-plot-mem-lines",
            dest="plot_poi_mem_lines",
            action="store_false",
            help=(
                "Don't display the individual processes' mem usage. Implies"
                " --plot-mem-sum"
            ),
        )

        self.parser.add_argument(
            "--plot-cpu-sum",
            dest="plot_poi_cpu_sum",
            action="store_true",
            help="Add a line for the sum of the ploted processes' cpu usage",
        )

        self.parser.add_argument(
            "--plot-mem-sum",
            dest="plot_poi_mem_sum",
            action="store_true",
            help="Add a line for the sum of the ploted processes' mem usage",
        )

        self.parser.add_argument(
            "-G",
            "--no-graph",
            dest="do_graph",
            action="store_false",
            help=(
                'Don\'t plot a graph. Useful with "-v" to get just get info from stdout'
            ),
        )

        self.parser.add_argument(
            "-g",
            "--graph",
            dest="which_graphs",
            default="",
            metavar="STR",
            help=(
                "Display pane/s of the overview graph (1-4), the cpu data by core (C),"
                " or the poi data by core (c). E.g. '-g13' to display panes 1 and 3."
                " Also accepts 'q' and 'Q' for debugging purposes."
            ),
        )

        self.parser.add_argument(
            "--display-cpu-markers",
            action="store_true",
            help=(
                "Adding core markers to the lines on the CPU graph takes a long time,"
                " so they are not displayed by default. The overview figure never"
                " displays them. Use this option to have the separate CPU figure"
                " display them."
            ),
        )

        self.parser.add_argument(
            "--rcParams",
            dest="display_rc_params",
            action="store_true",
            help="Display MatPlotLib rcParams and exit",
        )

        self.parser.add_argument(
            "-O",
            "--outputdir",
            dest="output_dir",
            metavar="DIR",
            help="Location for saving files.",
        )

        self.parser.add_argument(
            "-l",
            "--list",
            dest="list_processes",
            action="count",
            default=0,
            help=(
                "List the processes recorded in the top logs (-ll and -lll increase"
                " info)"
            ),
        )

        self.parser.add_argument(
            "--nowrite",
            dest="allow_write",
            action="store_false",
            default=True,
            help="Don't write data. For debugging; use with --tmpdir DIR",
        )

        self.parser.add_argument(
            "--tmpdir",
            dest="tmpdir",
            metavar="DIR",
            help=(
                "Unmanaged directory to store temporary files in. For debugging or the"
                " curious."
            ),
        )

        try:
            # pylint: disable=import-outside-toplevel,unused-import
            from .profiler import Profiler  # noqa: F401 unused import
        except ImportError:
            pass
        else:
            self.parser.add_argument(
                "-P",
                "--profile",
                dest="profiling_tag",
                metavar="STR",
                nargs="?",
                default=None,
                const="",
                help=(
                    "Run with profiling turned on. If STR is given, this will be used"
                    " to tag in the filenames of emitted .prof files."
                ),
            )

        self.parser.add_argument(
            "-v",
            "--verbose",
            dest="verbosity",
            action="count",
            default=0,
            help="Increase verbosity to stdout (can be given multiple times)",
        )

        self.parser.add_argument(
            "-V", "--version", action="version", version=self.version
        )

        self.parser.parse_args(namespace=self)

    # --------------------------------------------------------------------------

    def filterfoo(self, command, pid, timestamp):
        for func in self._filterfoos:
            if func(command, pid, timestamp):
                return True
        return False

    # --------------------------------------------------------------------------

    def _handle_commandline_arguments(self):
        if self.display_rc_params:
            rcParams()
            sys.exit(0)

        # Preflight checks and conversions

        if not self.plot_poi_cpu_lines:
            self.plot_poi_cpu_sum = True
            if "c" in self.which_graphs or "C" in self.which_graphs:
                die("'-g [cC]' and '--dont-graph-cpu-lines' are incompatible.")

        if not self.plot_poi_mem_lines:
            self.plot_poi_mem_sum = True

        if not os.path.exists(self.toplog_filename):
            self.parser.print_usage()
            die(f"Can't see a file called '{self.toplog_filename}'.")

        if self.output_dir is not None:
            if not os.path.isdir(self.output_dir):
                if not os.path.exists(self.output_dir):
                    die(f"Can't see a directory called '{self.output_dir}'.")
                else:
                    die(f"'{self.output_dir}' is not a directory.")
            try:
                is_dir_writable(self.output_dir)
            except OSError as e:
                die(f"Can't write to '{self.output_dir}' : {e}.")

        if not self.include_process_cpu and not self.include_process_mem:
            die("Can't disable processing both processes' cpu and processes' mem")

        if self.poi_prio:
            if self.poi_prio[0:1] not in "=<>":
                die("--prio argument must start with =, <=, >=, <, or >")

        if self.start_time:
            check = re.compile(r"^([>0-9])")
            result = check.match(self.start_time[0:1])
            if not result:
                die(
                    "-s | --start : offset requires leading '>'. Dunno about"
                    f" {self.start_time[0:1]}"
                )

            if result.group(0) != ">":
                self.start_time = dhms_to_sec(self.start_time)

        if self.stop_time:
            check = re.compile(r"^([<+0-9])")
            result = check.match(self.stop_time[0:1])
            if not result:
                die(
                    "-S | --stop : offset requires leading '+' or '<'. Dunno about"
                    f" {self.stop_time[0:1]}"
                )

            if result.group(0) != "+" and result.group(0) != "<":
                self.stop_time = dhms_to_sec(self.stop_time)

        # ----------------------------------------------------------------------
        # Processes of interest are identified by filtering through a list of
        # lambda functions and by creating top-N lists of cpu and mem values

        no_specific_interest = not (
            self.poi_cpu
            or self.poi_mem
            or self.poi_acc_cpu
            or self.poi_acc_mem
            or self.poi_peak_cpu
            or self.poi_peak_mem
            or self.poi_prio
            or self.poi_regex
        )

        if self.poi_mem:
            self._filterfoos.append(
                lambda command, pid, timestamp: float(
                    self._app.processes[command][pid]["timestamps"][timestamp]["mem"]
                )
                > self.poi_mem
            )
            self.poi_categories += f"mem>{self.poi_mem} "

        if self.poi_cpu:
            self._filterfoos.append(
                lambda command, pid, timestamp: float(
                    self._app.processes[command][pid]["timestamps"][timestamp]["cpu"]
                )
                > self.poi_cpu
            )
            self.poi_categories += f"cpu>{self.poi_cpu} "

        if self.poi_prio:
            if self.poi_prio[0:1] == "=" or self.poi_prio[0:2] == "==":
                i = 2 if self.poi_prio[0:2] == "==" else 1
                self._filterfoos.append(
                    lambda command, pid, timestamp: self._app.processes[command][pid][
                        "timestamps"
                    ][timestamp]["priority"]
                    == self.poi_prio[i:]
                )
            elif self.poi_prio[0:2] == "<=":
                self._filterfoos.append(
                    lambda command, pid, timestamp: self._app.processes[command][pid][
                        "timestamps"
                    ][timestamp]["priority"]
                    <= self.poi_prio[2:]
                )
            elif self.poi_prio[0:2] == ">=":
                self._filterfoos.append(
                    lambda command, pid, timestamp: self._app.processes[command][pid][
                        "timestamps"
                    ][timestamp]["priority"]
                    >= self.poi_prio[2:]
                )
            elif self.poi_prio[0:1] == "<":
                self._filterfoos.append(
                    lambda command, pid, timestamp: self._app.processes[command][pid][
                        "timestamps"
                    ][timestamp]["priority"]
                    < self.poi_prio[1:]
                )
            elif self.poi_prio[0:1] == ">":
                self._filterfoos.append(
                    lambda command, pid, timestamp: self._app.processes[command][pid][
                        "timestamps"
                    ][timestamp]["priority"]
                    > self.poi_prio[1:]
                )

            self.poi_categories += f"prio{self.poi_prio} "

        if self.poi_regex:
            flags = 0
            if self.ignore_case:
                flags = re.IGNORECASE

            self.poi_regex = re.compile(self.poi_regex, flags)
            self._filterfoos.append(
                lambda command, pid, timestamp: self.poi_regex.match(command) is not None
            )
            self.poi_categories += (
                f"/{self.poi_regex}/{'i' if self.ignore_case else ''} "
            )

        if self.poi_acc_cpu or no_specific_interest:
            if not self.poi_acc_cpu:
                self.poi_acc_cpu = poi_acc_cpu_default

            self.poi_categories += f"cpu+{self.poi_acc_cpu} "

        if self.poi_acc_mem:
            self.poi_categories += f"mem+{self.poi_acc_mem} "

        if self.poi_peak_cpu:
            self.poi_categories += f"cpu^{self.poi_peak_cpu} "

        if self.poi_peak_mem:
            self.poi_categories += f"mem^{self.poi_peak_mem} "

        self.poi_categories = self.poi_categories.strip()


# ------------------------------------------------------------------------------
