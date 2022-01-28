import datetime as dt
from io import StringIO
import re
import sys

import matplotlib as mpl
import pandas as pd


class CpuFiles:
    def __init__(self, config, directory, poi_combined_data_filename):
        self.config = config
        self.dir = directory
        self.poi_combined_data_filename = poi_combined_data_filename

        self.files = []
        self.poi_combined_data = {}
        self.registry = {}
        for core in range(0, self.config.cores):
            self.files.append(open(f"{directory}/cpu{core}_process.data", "w"))

    def close(self):
        if self.files:
            for f in self.files:
                f.close()
            self.files = []

            poi_keys = []
            for core in range(0, self.config.cores):
                poi_keys.append(f"cpu{core} poi cpu")
                poi_keys.append(f"cpu{core} poi mem")

            for core in range(0, self.config.cores):
                if self.config.plot_poi_cpu_sum or self.config.plot_poi_mem_sum:
                    # Generate data file
                    write_datafile(
                        self.poi_combined_data_filename,
                        self.poi_combined_data,
                        poi_keys,
                    )

    def write(self, core, header, txt):
        if core not in self.registry:
            self.registry[core] = self.files[core]
            if self.config.allow_write:
                self.files[core].write(header)

        if self.config.allow_write:
            self.files[core].write(txt)

    def seal_register(self):
        if self.config.allow_write:
            for cpu_id in self.registry:
                self.registry[cpu_id].write("\n")
        self.registry = {}

    def init_poi_timestamp(self, timestamp):
        self.poi_combined_data[timestamp] = {}
        for i in range(0, self.config.cores):
            self.poi_combined_data[timestamp][f"cpu{i} poi cpu"] = 0
            self.poi_combined_data[timestamp][f"cpu{i} poi mem"] = 0

    def add_poi_cpu(self, core, timestamp, value):
        if timestamp not in self.poi_combined_data:
            self.init_poi_timestamp(timestamp)
        self.poi_combined_data[timestamp][f"cpu{core} poi cpu"] += float(value)

    def add_poi_mem(self, core, timestamp, value):
        if timestamp not in self.poi_combined_data:
            self.init_poi_timestamp(timestamp)
        self.poi_combined_data[timestamp][f"cpu{core} poi mem"] += float(value)


# ------------------------------------------------------------------------------

MIDNIGHT = dt.datetime.combine(dt.date.today(), dt.time())


def from_csv(f):
    df = pd.read_csv(f, sep=" ")
    # Using Pandas datetimes lead to a weird issue with plotting dataframes on
    # multiplot figures.
    # Using MPL datetimes just works
    df.timestamp = df.timestamp.apply(
        lambda x: mpl.dates.date2num((MIDNIGHT + dt.timedelta(seconds=x)))
    )
    df.set_index("timestamp", inplace=True)
    return df


# --------------------------------------------------------------------------


def dataframe_from_process_graph_data(datafile):
    df_mono = None
    lines = []

    def closeoff(lines):
        # close off and process current set
        nonlocal df_mono
        csv = StringIO("".join(lines))
        df = from_csv(csv)
        if df_mono is None:
            df_mono = df
        else:
            df_mono = pd.concat([df_mono, df], axis=1)

    with open(datafile) as poi_data:
        process_name = None
        lines = []
        re_starts_with_timestamp_header = re.compile(r'^timestamp "(.*) - cpu"')
        re_parse_data = re.compile(r"^(\d+) ([0-9.]+) ([0-9.]+)\n$")
        for line in poi_data.readlines():
            if line == "\n":
                continue
            header_match = re_starts_with_timestamp_header.match(line)
            if header_match:
                if process_name is not None:
                    closeoff(lines)

                process_name = header_match.group(1)
                lines = [line]
            else:
                match = re_parse_data.match(line)
                if match:
                    lines.append(line)
                else:
                    print(
                        f"ERR: poi graphing Don't know what to do with line: '{line}'",
                        file=sys.stderr,
                    )

    if lines:
        closeoff(lines)
    else:
        df_mono = pd.DataFrame()

    return df_mono


def write_datafile(filename, source, keys):
    with open(filename, "w") as data_file:
        # Header
        line = '"timestamp"'
        for key in keys:
            key = key.replace("_", " ")
            line = f'{line} "{key}"'
        data_file.write(line + "\n")

        # Data
        # First with an integrated timestamp
        if isinstance(source, list):
            for entry in source:
                added = False
                line = entry["timestamp"]
                for key in keys:
                    added = True
                    line = f"{line} {entry[key]}"
                if added:
                    data_file.write(line + "\n")
        elif isinstance(source, dict):
            # Otherwise the key *is* the timestamp
            for timestamp, columns in source.items():
                line = timestamp
                for key in keys:
                    line = f"{line} {columns[key]}"
                data_file.write(line + "\n")
