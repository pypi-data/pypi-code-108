import re
import sys
from typing import Dict, List, Tuple

from .re_variants import Re_Variants
from ..toptype import TopType

# ------------------------------------------------------------------------------

MUSTHAVE_COLUMNS: Dict[TopType, List[str]] = {
    TopType.PROCPS: ["%CPU", "COMMAND", "%MEM", "PID"],
    TopType.BUSYBOX: ["%CPU", "COMMAND", "%VSZ", "PID"],
}

# ------------------------------------------------------------------------------


def _setup_regex(self):
    self._re_ignore_processes_regex = None
    if self.config.ignore_processes_regex:
        flags = 0
        if self.config.ignore_case:
            flags = re.IGNORECASE

        self._re_ignore_processes_regex = re.compile(
            self.config.ignore_processes_regex, flags
        )

    # --------------------------------------------------------------------------
    # Different versions of top require slightly different handling
    #
    # This is being handled by setting variables when what parses (!) for version
    # detection occurs.
    #
    # This is performed by optionally passing tuples of:
    #    ((var1_name, var1_value), (varN_name, varN_value))
    # in with regexes to Re_Variants instances.

    # --------------------------------------------------------------------------
    # Precompile regexps
    #
    # The group names, i.e the "word" in (?P<word>pattern), are used later
    # on as dictionary keys

    # top - 06:40:46 up 0 min,  0 users,  load average: 20.84, 5.41, 1.83
    self._re_top_procps = re.compile(
        r"^top - (?P<timestamp>[^ ]+) .*load average: (?P<load_average>[0-9.]+), .*"
    )

    # Did I mention yet how annoying I find BusyBox in so many ways?
    # Replacing common utilities with such hideous simulcra is an abomination :)
    # No timestamp, even in batch output. What were they thinking?
    # Mem: 27436964K used, 5056536K free, 317416K shrd, 1433660K buff, 11810180K cached
    self._re_top_busybox = re.compile(
        r"^Mem:"
        r" (?P<mem_used>[0-9]+)K used,"
        r" (?P<mem_free>[0-9]+)K free,"
        r" (?P<mem_shared>[0-9]+)K shrd,"
        r" (?P<mem_buffers>[0-9]+)K buff,"
        r" (?P<mem_cached>[0-9]+)K cached.*"
    )

    scope = locals()  # pylint: disable=used-before-assignment

    # Tasks: 301 total,  23 running, 209 sleeping,   0 stopped,   0 zombie
    self._re_procps_tasks = Re_Variants(
        "re_procps_tasks",
        re.compile(
            r"^Tasks:"
            r" (?P<task_total>[0-9]+) total,"
            r" +(?P<task_running>[0-9]+) running,"
            r" +(?P<task_sleeping>[0-9]+) sleeping,"
            r" +(?P<task_stopped>[0-9]+) stopped,"
            r" +(?P<task_zombie>[0-9]+) zombie"
        ),
    )

    # Threads: 1529 total,   4 running, 1525 sleeping,   0 stopped,   0 zombie
    self._re_procps_tasks.append(
        re.compile(
            r"^Threads:"
            r" (?P<task_total>[0-9]+) total,"
            r" +(?P<task_running>[0-9]+) running,"
            r" +(?P<task_sleeping>[0-9]+) sleeping,"
            r" +(?P<task_stopped>[0-9]+) stopped,"
            r" +(?P<task_zombie>[0-9]+) zombie"
        ),
        (("self.config.threads_not_tasks", "True"),),
        scope=scope,
    )

    # Cpu(s): 51.8%us, 28.7%sy,  0.5%ni, 13.9%id,  1.4%wa,  0.0%hi,  3.7%si,  0.0%st
    self._re_procps_cpu = re.compile(
        r"^%?Cpu(\(s\)|(?P<cpu_id>[0-9]+) +):"
        r" *(?P<cpu_user>[0-9.]*)[% ]us,"
        r" *(?P<cpu_system>[0-9.]+)[% ]sy,"
        r" *(?P<cpu_nice>[0-9.]+)[% ]ni,"
        r" *(?P<cpu_idle>[0-9.]+)[% ]id,"
        r" *(?P<cpu_wait>[0-9.]+)[% ]wa,"
        r" *(?P<cpu_hw_irq>[0-9.]+)[% ]hi,"
        r" *(?P<cpu_sw_irq>[0-9.]+)[% ]si,"
        r" *(?P<cpu_steal>[0-9.]+)[% ]st"
    )

    # CPU:   5% usr   3% sys   0% nic  83% idle   7% io   0% irq   0% sirq
    self._re_busybox_cpu = re.compile(
        r"^%?CPU(?P<cpu_id>[0-9]+)?:"
        r" *(?P<cpu_user>[0-9.]*)% usr"
        r" *(?P<cpu_system>[0-9.]+)% sys"
        r" *(?P<cpu_nice>[0-9.]+)% nic"
        r" *(?P<cpu_idle>[0-9.]+)% idle"
        r" *(?P<cpu_wait>[0-9.]+)% io"
        r" *(?P<cpu_hw_irq>[0-9.]+)% irq"
        r" *(?P<cpu_sw_irq>[0-9.]+)% sirq"
    )

    # Load average: 2.44 2.24 2.30 3/2473 953092
    self._re_busybox_load_average = re.compile(
        r"^%?Load average:"
        r" *(?P<load_average>[0-9.]+)"
        r" (?P<load_average_5>[0-9.]+)"
        r" (?P<load_average_15>[0-9.]+)"
        r" (?P<task_running>[0-9.]+)/(?P<task_total>[0-9]+)"
    )

    # Mem:   4046364k total,  2847408k used,  1198956k free,    37528k buffers
    self._re_procps_mem = Re_Variants(
        "re_procps_mem",
        re.compile(
            r"^Mem:"
            r" +(?P<mem_total>[0-9]+)k total,"
            r" +(?P<mem_used>[0-9]+)k used,"
            r" +(?P<mem_free>[0-9]+)k free,"
            r" +(?P<mem_buffers>[0-9]+)k buffers"
        ),
    )

    # Swap:  2047996k total,        0k used,  2047996k free,  1468792k cached
    self._re_procps_swap = Re_Variants(
        "re_procps_swap",
        re.compile(
            r"^Swap:"
            r" +(?P<swap_total>[0-9]+)k total,"
            r" +(?P<swap_used>[0-9]+)k used,"
            r" +(?P<swap_free>[0-9]+)k free,"
            r" +(?P<mem_cached>[0-9]+)k cached"
        ),
    )

    for unit in ["K", "M", "G", "T", "P", "E"]:
        # <unit>iB Mem : 15653.4 total,  6178.4 free,  7285.0 used,  2189.9 buff/cache
        self._re_procps_mem.append(
            re.compile(
                rf"^{unit}iB Mem :"
                r" +(?P<mem_total>[.0-9]+) total,"
                r" +(?P<mem_free>[.0-9]+) free,"
                r" +(?P<mem_used>[.0-9]+) used,"
                r" +(?P<mem_buffers>[.0-9]+)"
                r" buff/cache"
            ),
            (("self.mem_unit", f"{unit}iB"),),
            scope=scope,
        )

        # <unit>MiB Swap: 15792.0 total, 10146.5 free,  5645.5 used.  7242.8 avail Mem
        self._re_procps_swap.append(
            re.compile(
                rf"^{unit}iB Swap:"
                r" +(?P<swap_total>[.0-9]+) total,"
                r" +(?P<swap_free>[.0-9]+) free,"
                r" +(?P<swap_used>[.0-9]+) used\."
                r" +(?P<mem_available>[.0-9]+)"
                r" avail"
            ),
            (("self.config.mem_cached_or_available", "mem_available"),),
            scope=scope,
        )

    # 2019-01-31 06:40:41:709
    self._re_timestamp = re.compile(r"^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d:\d\d\d$")

    self._re_process = None
    self._re_process_header = None


# ------------------------------------------------------------------------------


def _generate_re_process(
    self, columnheader_to_regex, line
) -> Tuple[str, re.Pattern, re.Pattern]:
    found = {}
    header_pattern = "^"
    process_pattern = "^"
    prespace = " *"

    line = line.rstrip("\n")

    for columnheader in re.findall(r"([^ ]+)", line):
        found[columnheader] = True
        header_pattern += prespace + columnheader.replace("+", "\\+")

        if columnheader in columnheader_to_regex:
            if columnheader_to_regex[columnheader]:
                process_pattern += prespace + columnheader_to_regex[columnheader]
                prespace = " +"
        else:
            print(
                ">INFO: header line contains unhandled columnheader"
                f" '{columnheader}'",
                file=sys.stderr,
            )
            process_pattern += prespace + r"(?:[^ ]+)"

    header_pattern += r"\s*$"
    process_pattern += r"$"

    missing = []

    for musthave in MUSTHAVE_COLUMNS[self.config.toptype]:
        if musthave not in found:
            missing.append(musthave)

    if len(missing) > 0:
        print(
            f">ERR: missing essential process column(s): {missing}\nAborting.",
            file=sys.stderr,
        )
        sys.exit(1)

    if self.config.verbosity > 2:
        print(f"header_pattern : {header_pattern}")
        print(f"process_pattern: {process_pattern}")

    return (
        header_pattern,
        re.compile(header_pattern),
        re.compile(process_pattern),
    )


# ------------------------------------------------------------------------------


def _generate_procps_re_process(self, line) -> Tuple[str, re.Pattern, re.Pattern]:
    if self.config.threads_not_tasks:
        # Command *must* be the rightmost column
        command_pattern = r"(?P<commandline>(?P<command>.+))"
    else:
        # Command shouldn't contain spaces
        command_pattern = r"(?P<commandline>(?P<command>[^ ]+).*)"

    columnheader_to_regex = {
        "%CPU": r"(?P<cpu>[\d.]+)",
        "COMMAND": command_pattern,
        "%MEM": r"(?P<mem>[\d.]+[mg]?)",
        "NI": r"(?P<nice>[\d-]+)",
        "P": r"(?P<cpu_id>\d+)",
        "PID": r"(?P<pid>[0-9]+)",
        "PR": r"(?P<priority>[\drRtT-]+)",
        "RES": r"(?P<res>[\d.]+[mg]?)",
        "S": r"(?P<state>[DINRSTtWXZ<]+)",
        "SHR": r"(?P<shr>[\d.]+[mg]?)",
        "SWAP": r"(?P<swap>[\d.]+[mg]?)",
        "TIME+": r"(?P<time>[\d:.]+)",
        "USER": r"(?P<user>[\w+-]+)",
        "VIRT": r"(?P<virt>[\d.]+[mg]?)",
    }

    return _generate_re_process(self, columnheader_to_regex, line)


# ------------------------------------------------------------------------------


def _generate_busybox_re_process(self, line) -> Tuple[str, re.Pattern, re.Pattern]:
    # PID  PPID USER     STAT   VSZ %VSZ %CPU COMMAND
    #
    # Can also have a CPU column, compile time config option
    #
    # Have I maaned about BusyBox enough yet?
    # But FFS, sometimes there's no space between the PID and PPID columns.
    # PID's min width is 5 digits, PPID's is 6.
    #
    # Some examples from running BusyBox top 1.30.1 on my laptop:
    #
    #     275     2
    #     277     2
    #   1211762     2
    #   911329     1
    #   911456911329
    #   1155184187009
    #   10164901016486

    columnheader_to_regex = {
        "CPU": r"(?P<cpu_id>[\d.]+)",
        "%CPU": r"(?P<cpu>[\d.]+)%?",
        "COMMAND": r"(?P<commandline>(?P<command>[^ ]+).*)",
        # Since topplot isn't (currently) using PPID, we can use a merged
        # PID/PPID as a single identifier. Merge can include a space. Try
        # to avoid USER starting with a digit. (Can that ever happen?)
        #
        #        (1      2     (3       (4          ))5)
        "PID": r"(?P<pid>[0-9]+( +[0-9]+(?![a-zA-Z_]))?)",
        #
        # 1 : The named capture group "pid"
        #
        # 2 : A continuous run of digits
        #
        # 3 : An unamed sub-group starting with a space followed by a
        #     continuous run of digits. Spoiler: the '?' at 5 makes this
        #     entire sub-group optional, i.e capture if present, but don't
        #     sweat if it's absent.
        #
        # 4 : A negative lookahead (non-capturing) to make 3 not match when
        #     3's run of digits is immediately followed by an alphabetic or
        #     underscore. This is in case a username starting with a digit
        #     would otherwise be captured when following a merged PID/PPID.
        #     Obvs. will still capture a username soley consiting in digits.
        #
        # Could do the following which which capture PPID when it's not
        # merged with PID, but I'm not sure that this is useful:
        #
        #   "PID": r"(?P<pid>[0-9]+( (?P<ppid>[0-9]+(?![a-zA-Z_])))?)",
        "PPID": None,
        "STAT": r"(?P<stat>[DINRSTtWXZ<]+)",
        "USER": r"(?P<user>[\w+-]+)",
        "VSZ": r"(?P<mem_abs>[\d.]+[mg]?)",
        "%VSZ": r"(?P<mem>[\d.]+)%?",
    }

    return _generate_re_process(self, columnheader_to_regex, line)


# ------------------------------------------------------------------------------
