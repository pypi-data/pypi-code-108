#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# reportt_builder.py: builds the report shown in "list jobs", "list runs", etc. cmds
import os
import json
import time
from xtlib.pc_utils import COLORS
import arrow
import datetime
import logging
import numpy as np
from fnmatch import fnmatch
from collections import OrderedDict

from xtlib.console import console

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import pc_utils
from xtlib import constants

class ReportBuilder():
    def __init__(self, config=None, store=None):
        self.config = config
        self.store = store
        self.user_col_args = {}

    def wildcard_matches_in_list(self, wc_name, name_list, omits):
        matches = []

        if name_list:
            matches = [name for name in name_list if fnmatch(name, wc_name) and not name in omits]
            
        return matches

    def default_user_name(self, col_name):
        user_name = col_name

        if col_name.startswith("hparams."):
            user_name = col_name[8:]
        elif col_name.startswith("metrics."):
            user_name = col_name[8:]
        else:
            user_name = col_name

        return user_name

    def get_requested_cols(self, user_col_args, avail_list):
        actual_cols = []
        new_col_args = {}
        
        for key, value in user_col_args.items():
            # if the requested key is available, include it
            if "*" in key:
                # wildcard match
                 matches = self.wildcard_matches_in_list(key, avail_list, ["metrics." + constants.STEP_NAME, "metrics.$step_name"])
                 actual_cols += matches

                 # replace our wilcard in request_list with matches
                 for match in matches:
                    user_name = self.default_user_name(match)
                    new_value = {"user_name": user_name, "user_fmt": None}
                    new_col_args[match] = new_value

            elif key in avail_list:
                actual_cols.append(key)
                new_col_args[key] = value
        
        return actual_cols, new_col_args

    def sort_records(self, records, sort_col, reverse):
        if reverse is None:
            reverse = 0

        console.diag("after reportbuilder SORT")
        console.diag("sort_col={}".format(sort_col))

        # normal sort
        records.sort(key=lambda r: r[sort_col] if sort_col in r and r[sort_col] else 0, reverse=reverse)

        console.diag("after reportbuilder SORT")

    def expand_special_symbols(self, value):

        if isinstance(value, str):
            value = value.strip()

            if value == "$none":
                value = {"$type": 10}
            elif value == "empty":
                value = ""
            elif value == "$true":
                value = True
            elif value == "$false":
                value = False
            elif value == "$exists":
                value = {"$exists": True}

        return value

    def process_filter_list(self, filter_dict, filter_exp_list, report2filter):
        '''
        used to filter records for following expressions of form:
            - <prop name> <relational operator> <value>

        special values:
            - $exists   (does property exist)
            - $none     (None, useful for matching properties with no value)
            - $empty    (empty string)
            - $true     (True)
            - $false    (False)
        '''
        for filter_exp in filter_exp_list:
            prop = filter_exp["prop"]
            op = filter_exp["op"]
            value = filter_exp["value"]
            
            # translate name, if needed
            if prop in report2filter:
                prop = report2filter[prop]

            if isinstance(value, str):
                value = self.expand_special_symbols(value)
                value = utils.make_numeric_if_possible(value)

            if op in ["=", "=="]:
                filter_dict[prop] = value
            elif op == "<":
                filter_dict[prop] = {"$lt": value}
            elif op == "<=":
                filter_dict[prop] = {"$lte": value}
            elif op == ">":
                filter_dict[prop] = {"$gt": value}
            elif op == ">=":
                filter_dict[prop] = {"$gte": value}
            elif op in ["!=", "<>"]:
                filter_dict[prop] = {"$ne": value}
            elif op == ":regex:":
                filter_dict[prop] = {"$regex" : value}
            elif op == ":exists:":
                filter_dict[prop] = {"$exists" : value}
            elif op == ":database:":
                # raw filter dict, but we need to translate quotes and load as json
                value = value.replace("`", "\"")
                value = json.loads(value)
                filter_dict[prop] = value
            else:
                errors.syntax_error("filter operator not recognized/supported: {}".format(op))
        
    def available_cols_report(self, report_type, std_list, std_cols_desc, hparams_list=None, metrics_list=None, tags_list=None):
        lines = []

        std_list.sort()

        #lines.append("")
        lines.append("Standard {} columns:".format(report_type))
        for col in std_list:
            if col in ["hparams", "metrics", "tags"]:
                continue

            if not col in std_cols_desc:
                console.print("internal error: missing description for std col: " + col)
                desc = ""
            else:
                desc = std_cols_desc[col]

            lines.append("  {:<14s}: {}".format(col, desc))

        if hparams_list:
            hparams_list.sort()
            lines.append("")
            lines.append("Logged hyperparameters:")
            for col in hparams_list:
                lines.append("  {}".format(col))

        if metrics_list:
            metrics_list.sort()
            lines.append("")
            lines.append("Logged metrics:")
            for col in metrics_list:
                lines.append("  {}".format(col))

        if tags_list:
            tags_list.sort()
            lines.append("")
            lines.append("Tags:")
            for col in tags_list:
                lines.append("  {}".format(col))

        return lines

    def build_avail_list(self, col_dict, record, prefix=""):
        subs = ["metrics", "hparams", "tags"]

        for key in record.keys():
            if key in subs:
                value = record[key]
                if value:
                    self.build_avail_list(col_dict, value, prefix=key + ".")
            else:
                col_dict[prefix + key] = 1

    def flatten_records(self, records, sort_col, need_alive, which, user_columns=None, args=None):
        '''
        pull out the AVAILABLE or USER SPECIFIED columns, flattening nested props to their dotted names.
        '''

        # build avail col list based on final set of filtered records
        avail_cols, actual_cols, user_col_args  = self.get_avail_actual_user_cols(records, user_columns, args)

        # add often-needed cols for processing report
        for col in ["status", "created", "started"]:
            if not col in actual_cols:
                actual_cols.append(col)

        # flatten each record's nested columns
        available = utils.safe_value(args, "available")

        add_if_missing_cols = ["queued", "duration"]
        get_cols = avail_cols if available else actual_cols

        records = [self.extract_actual_cols(rec, get_cols, add_if_missing_cols) for rec in records if rec]
        return records

    def extract_actual_cols(self, record, actual_cols, add_if_missing_cols=None):
        '''
        pull out the cols specified in actual_cols, flattening nested props to their dotted names.
        '''
        new_record = {}

        for actual_key in actual_cols:
            if not actual_key:
                continue

            empty_value = constants.EMPTY_TAG_CHAR if actual_key.startswith("tags.") else None

            if "." in actual_key:
                # its a NESTED reference
                outer_key, inner_key = actual_key.split(".")

                if outer_key in record:
                    inner_record = record[outer_key]
                    if inner_record and inner_key in inner_record:
                        value = inner_record[inner_key]
                        new_record[actual_key] = value if value is not None else empty_value
            else:
                # its a FLAT reference
                if actual_key in record:
                    value = record[actual_key]
                    new_record[actual_key] = value if value is not None else empty_value
    
        if add_if_missing_cols:
            for col in add_if_missing_cols:
                if not col in new_record:
                    new_record[col] = None

        return new_record

    def translate_record(self, record, actual_to_user):
        '''
        pull out the cols specified in actual_to_user, translating from storage names to user names.
        '''
        new_record = {}

        for actual_key, user_key in actual_to_user.items():
            if not actual_key:
                continue

            if actual_key in record:
                value = record[actual_key]
                new_record[user_key] = value 
    
        return new_record

    def get_first_last(self, args):
        first = utils.safe_value(args, "first")
        last = utils.safe_value(args, "last")
        show_all = utils.safe_value(args, "all")

        explict = qfe.get_explicit_options()

        # explict overrides default for all/first/last
        if "all" in explict:
            first = None
            last = None
        elif "first" in explict:
            show_all = None
            last = None
        elif "last" in explict:
            show_all = None
            first = None
        else:
            # priority if no explict options set
            if show_all:
                first = None
                last = None

        return first, last

    def get_db_records(self, database, filter_dict, workspace, which, actual_to_user,
            col_dict=None, col_names_are_external=True, flatten_records=True, need_alive=False, 
            user_columns=None, args=None):

        started = time.time()

        first, last = self.get_first_last(args)
        skip = utils.safe_value(args, "skip")

        list_nodes = utils.safe_value(args, "list_nodes")
        if list_nodes:
            which = "nodes"

        if first:
            limiter = "first"
            limiter_value = first
        elif last:
            limiter = "last"
            limiter_value = last
        else:
            limiter = None
            limiter_value = 0

        reverse = utils.safe_value(args, "reverse")
        # use database to do all of the work (query, sort, first/last)
        sort_col = utils.safe_value(args, "sort", "name")
        sort_dir = 1

        if sort_col:
            if sort_col == "name":

                # special sorting needed; we have created "xxx_num" fields just for this purpose
                if which == "runs":
                    sort_col = "run_num"
                elif which == "jobs":
                    sort_col = "job_num"
                elif which == "nodes":
                    sort_col = "node_num"

            elif not "." in sort_col:
                # translate name of std col from user-friendly version to logged version
                user_to_actual = {value: key for key, value in actual_to_user.items()}

                if not sort_col in user_to_actual:
                    errors.general_error("unknown standard property: {} (did you mean metrics.{}, hparams.{}, or tags.{}?)". \
                        format(sort_col, sort_col, sort_col, sort_col))

                sort_col = user_to_actual[sort_col]

            # this is a TRICK to avoid having to call for the exists_count for calculation of skip count
            # it works fine, since we re-sort records on the xt client anyway
            sort_dir = -1 if reverse else 1
            if last:
                sort_dir = -sort_dir
                first = last

            # ensure we only ask for records where sort_col exists, or else we MIGHT end up with less than LIMIT records
            if sort_col != "run_num" and not sort_col in filter_dict:
                filter_dict[sort_col] = { "$exists": True}

        # always include ws_name (for now)
        if workspace and not "ws_name" in filter_dict:
            filter_dict["ws_name"] = workspace

        container = "run_info" if which == "runs" else "job_info"

        orig_col_dict =  col_dict
        # if not col_dict:
        #     col_dict = {"log_records": 0}

        console.diag("get_db_records: first={}, last={}, ws: {}, filter_dict: {}, col_dict: {}". \
            format(first, last, workspace, filter_dict, col_dict))

        count_runs = utils.safe_value(args, "count")
        buffer_size = utils.safe_value(args, "buffer_size", 50)

        started = time.time()

        # here is where DATABASE SERVICE does all the hard work for us
        if which == "runs":
            records = database.get_filtered_sorted_run_info(workspace, filter_dict, col_dict, sort_col, sort_dir, skip, first, 
                count_runs, buffer_size)
        elif which == "jobs":
            records = database.get_filtered_sorted_job_info(workspace, filter_dict, col_dict, sort_col, sort_dir, skip, first, 
                count_runs, buffer_size)
        elif which == "nodes":
            records = database.get_filtered_sorted_node_info(workspace, filter_dict, col_dict, sort_col, sort_dir, skip, first, 
                count_runs, buffer_size)
        else:
            errors.internal_error("unrecognized value for which: {}".format(which))

        elapsed = time.time() - started
        console.diag("  query elapsed: {:.2f} secs".format(elapsed))

        console.diag("after full records retreival, len(records)={}".format(len(records)))

        if col_names_are_external:    # not orig_col_dict:
            # pull out standard cols, translating from actual to user-friendly names
            records = [self.translate_record(rec, actual_to_user) for rec in records if rec]

        if flatten_records:
            # pull out requested cols, flattening nested values to their dotted names
            records = self.flatten_records(records, sort_col, need_alive, which, user_columns=user_columns, args=args)

        if last:
            # we had to reverse the sort done by database, so correct it here
            records.reverse()
            #self.sort_records(records, sort_col, reverse)

        elapsed = time.time() - started
        #console.print("  query stats: round trips={}, elapsed: {:.2f} secs".format(round_trip_count, elapsed))

        return records, limiter, limiter_value

    def get_user_columns(self, requested_list, args):
        if requested_list is None:
            requested_list = args["columns"]
            
        add_cols = utils.safe_value(args, "add_columns")
        if add_cols:
            requested_list += add_cols

        return requested_list

    def get_avail_actual_user_cols(self, records, user_columns, args):
        col_dict = OrderedDict()
        for sr in records:
            if "metric_names" in sr:
                # seed col_dict with ordered list of metrics reported
                names = sr["metric_names"]
                if names:
                    for name in names:
                        col_dict["metrics." + name] = 1

            # build from log records
            self.build_avail_list(col_dict, sr)

        avail_list = list(col_dict.keys())

        # get list of user-requested columns
        user_columns = self.get_user_columns(user_columns, args)

        # parse out the custom column NAMES and FORMATS provided by the user
        user_col_args = self.build_user_col_args(user_columns)

        actual_cols, user_col_args = self.get_requested_cols(user_col_args, avail_list)
        return avail_list, actual_cols, user_col_args

    def build_report(self, records, user_columns, report_type, args):
        ''' build a tabular report of the records, or export to a table, as per args.  
        values in each record must have been flattened with a dotted key (e.g., hparams.lr).
        records must be in final sort order.
        '''
        row_count = 0
        was_exported = False
        max_column_width = utils.safe_value(args, "max_width")

        avail_list, actual_cols, user_col_args  = self.get_avail_actual_user_cols(records, user_columns, args)

        # store for later use
        self.user_col_args = user_col_args

        fn_export = args["export"]
        if fn_export:
            fn_ext = os.path.splitext(fn_export)[1]
            if not fn_ext:
                fn_ext = ".txt"
                fn_export += fn_ext

            sep_char = "," if fn_ext == ".csv" else "\t"

            col_list = user_col_args.keys()
            count = self.export_records(fn_export, records, col_list, sep_char)
            row_count = count - 1
            line = "report exported to: {} ({} rows)".format(fn_export, row_count)
            lines = [line]
            was_exported = True
        else:
            group_by = args["group"] if "group" in args else None
            number_groups = args["number_groups"] if "number_groups" in args else False
            actual_cols = list(user_col_args.keys())

            text, row_count = self.build_formatted_table(records, avail_cols=avail_list, col_list=actual_cols, 
                report_type=report_type, group_by=group_by, number_groups=number_groups, 
                max_col_width=max_column_width)

            lines = text.split("\n")

        return lines, row_count, was_exported

    def export_records(self, fn_report, records, col_list, sep_char):

        lines = []

        # write column header
        header = ""
        for col in col_list:
            if header == "":
                header = col
            else:
                header += sep_char + col
        lines.append(header)

        # write value rows
        for record in records:
            line = ""

            for col in col_list:
                value = record[col] if col in record else ""
                if value is None:
                    value = ""
                else:
                    value = str(value)

                if line == "":
                    line = value
                else:
                    line += sep_char + value
    
            lines.append(line)

        with open(fn_report, "wt") as outfile:
            text = "\n".join(lines)
            outfile.write(text)

        return len(lines)

    def build_user_col_args(self, requested_list):

        user_col_args = {}

        for col_spec in requested_list:
            col_name = col_spec
            user_fmt = None

            if "." in col_name:
                prefix, col_name = col_name.split(".", 1)
            else:
                prefix = None

            if "=" in col_name:
                # CUSTOM NAME
                col_name, user_name = col_name.split("=")
                if ":" in user_name:
                    # CUSTOM FORMAT
                    user_name, user_fmt = user_name.split(":")
                    user_fmt = "{:" + user_fmt + "}"
            else:
                if ":" in col_name:
                    # CUSTOM FORMAT
                    col_name, user_fmt = col_name.split(":")
                    
                    user_fmt = "{:" + user_fmt + "}"
                user_name = col_name

            # rebuild prefix_name (must be prefix + col_name)
            prefix_name = prefix + "." + col_name if prefix else col_name

            user_col_args[prefix_name] = {"user_name": user_name, "user_fmt": user_fmt}

        return user_col_args

    def xt_custom_format(self, fmt, value):
        blank_zero_fmt = "{:$bz}"
        date_only = "{:$do}"
        time_only = "{:$to}"
        right_trim = "{:$rt."

        if fmt == blank_zero_fmt:
            # blank if zero
            value = "" if value == 0 else str(value)
        elif fmt == date_only:
            # extract date portion of datetime string
            delim = " " if " " in value else "T"
            value, _ = value.split(delim)
        elif fmt == time_only:
            # extract time portion of datetime string
            delim = " " if " " in value else "T"
            _, value = value.split(delim)
            value = value.split(".")[0]    # extract hh:mm:ss part of fractional time
        elif fmt.startswith(right_trim):
            int_part = fmt[6:].split("}")[0]
            trim_len = int(int_part)
            value = str(value)[-trim_len:]
        
        return value

    def needed_precision(self, value, significance):
        # start with scientific notation formatting
        if value != value:   # test for nan
            return 0

        text = "%.*e" % (significance-1, value)

        # how much precision is required for specified significance?
        sd, exponent = text.split("e")
        exponent = int(exponent)

        # needed = max(0, significance - (exponent+1))
        if exponent <= 0:
            #my_precision = 1 - exponent
            needed = 2 - exponent
        else:
            needed = 0

        return needed

    def smart_float_format(self, value, significance, max_precision, max_fixed_length):
        if max_precision <= max_fixed_length:
            # FIXED POINT formatting
            text = "%.*f" % (max_precision, value)
        else:
            # SCIENTIFIC NOTATION formatting
            text = "%.*e" % (significance-1, value)
        return text

    def build_formatted_table(self, records, avail_cols=None, col_list=None, max_col_width=None, 
        report_type="run-reports", group_by=None, number_groups=False):
        '''
        Args:
            records:        a list of dict entries containing data to format
            avail_cols:     list of columns (unique dict keys found in records)
            actual_cols:    list of columns to be used for report (strict subset of 'avail_cols')
            report_type:    a dotted path to the report definition in the XT config file

        Processing:
            Builds a nicely formatted text table from a set of records.
        '''

        time_col_names = ["created", "started", "ended", "time"]
        duration_col_names = ["duration", "queued", "queue_duration", "prep_duration",
            "app_duration", "post_duration"]

        if not avail_cols:
            avail_cols = list(records[0].keys()) if records else []
        #console.print("self.user_col_args=", self.user_col_args)

        if self.config:
            if not max_col_width:
                max_col_width = int(self.config.get(report_type, "max-width"))    
                
            precision = self.config.get(report_type, "precision")
            significance = self.config.get(report_type, "significance")
            max_fixed_length = self.config.get(report_type, "max-fixed-length")
            
            uppercase_hdr_cols = self.config.get(report_type, "uppercase-hdr")
            right_align_num_cols = self.config.get(report_type, "right-align-numeric")
            truncate_with_ellipses = self.config.get(report_type, "truncate-with-ellipses")
        else:
            # default when running without config file
            if not max_col_width:
                max_col_width = 35
            precision = 3
            significance = 2
            max_fixed_length = 7
            uppercase_hdr_cols = True
            right_align_num_cols = True
            truncate_with_ellipses = True

        if not col_list:
            col_list = avail_cols

        col_space = 2               # spacing between columns
        col_infos = []              # {width: xxx, value_type: int/float/str, is_numeric: true/false}
        header_line = None

        # formatting strings with unspecified width and alignment
        int_fmt = "{:d}"
        str_fmt = "{:s}"
        #console.print("float_fmt=", float_fmt)

        # build COL_INFO for each col (will calcuate col WIDTH, formatting, etc.)
        for i, col in enumerate(col_list):

            # if col == "hparams.lr":
            #     print()
            # largest precision needed for this col
            max_precision = precision 

            # examine all records for determining max col_widths
            if self.user_col_args:
                user_args = self.user_col_args[col]
                user_col = user_args["user_name"]
                user_fmt = user_args["user_fmt"] 
            else:
                user_col = col
                user_fmt = None

            float_fmt = "{:." + str(precision) + "f}"

            col_width = len(user_col)
            #console.print("col=", col, ", col_width=", col_width)
            value_type = str
            is_numeric = False
            first_value = True

            for record in records:

                if not col in record:
                    # not all columns are defined in all records
                    continue

                try:
                    value = record[col]

                    # special formatting for time values
                    if col in duration_col_names:
                        value = self.format_duration(value, col, record)
                    elif col in time_col_names:
                        if isinstance(value, str):
                            value = arrow.get(value)
                        value = value.format('YYYY-MM-DD @HH:mm:ss')

                    # for sql, convert float types that are really integer values to int types
                    if isinstance(value, float) and value == int(value) and user_fmt is None and value_type is str:
                        value = int(value)

                    if user_fmt:
                        # user provided explict format for this column
                        if "$" in user_fmt:
                            value_str = self.xt_custom_format(user_fmt, value)
                        else:
                            value_str = user_fmt.format(value)
                    elif isinstance(value, float):

                        # default (smart) FLOAT formatting
                        needed = self.needed_precision(value, significance)
                        max_precision = max(max_precision, needed)
                        value_str = self.smart_float_format(value, significance, max_precision, max_fixed_length)
                        
                        if (value_type == str or value_type is int) and user_fmt is None:
                            value_type = float
                            is_numeric = True

                    elif isinstance(value, bool):
                        value_str = str(value)
                        value_type = bool
                        is_numeric = False
                    elif isinstance(value, int):
                        value_str = int_fmt.format(value)
                        if value_type == str:
                            value_type = int
                            is_numeric = True
                    elif value is not None:
                        # don't let None values influence the type of field
                        # assume value found is string-like
                        
                        # ensure value is a string
                        value = str(value)

                        value_str = str_fmt.format(value) if value else ""
                        if first_value:
                            is_numeric = utils.str_is_float(value)
                    else:
                        value_str = ""

                    # set width as max of all column values seen so far
                    col_width = max(col_width, len(value_str))
                    #console.print("name=", record["name"], ", col=", col, ", value_str=", value_str, ", col_width=", col_width)
                except BaseException as ex:
                    console.print("Exception formatting col={}: {}".format(col, ex))
                    console.print("  Exception record: {}".format(record))

                    # debug
                    raise ex

            # finish this col
            if is_numeric and not max_precision:
                max_precision = 3

            col_width = min(max_col_width, col_width)

            col_info = {"name": col, "user_name": user_col, "col_width": col_width, "value_type": value_type, 
                "is_numeric": is_numeric, "precision": max_precision, "user_fmt": user_fmt, 
                "value_padding": None}

            col_infos.append(col_info)
            #console.print(col_info)

        if group_by:
            # GROUPED REPORT
            text = ""
            row_count = 0
            group_count = 0

            grouped_records = self.group_by(records, group_by)
            for i, (group, grecords) in enumerate(grouped_records.items()):

                if number_groups:
                    text += "\n{}. {}:\n".format(i+1, group)
                else:
                    text += "\n{}:\n".format(group)

                txt, rc = self.generate_report(col_infos, grecords, right_align_num_cols, uppercase_hdr_cols, truncate_with_ellipses, 
                    col_space, duration_col_names, time_col_names, significance, max_fixed_length, precision)

                # indent report
                txt = "  " + txt.replace("\n", "\n  ")
                text += txt
                row_count += rc
                group_count += 1

            text += "\ntotal groups: {}\n".format(group_count)
        else:
            # UNGROUPED REPORT
            text, row_count = self.generate_report(col_infos, records, right_align_num_cols, uppercase_hdr_cols, truncate_with_ellipses, 
                col_space, duration_col_names, time_col_names, significance, max_fixed_length, precision)

        return text, row_count

    def should_highlight_row(self, highlight_exp, rd):
        should = False

        if highlight_exp == "$alive":
            status = utils.safe_value(rd, "status")
            should = status in ["submitted", "queued", "running"]

        return should

    def format_duration(self, value, col, record):
        # value = str(datetime.timedelta(seconds=value))
        # index = value.find(".")
        # if index > -1:
        #     value = value[:index]

        ongoing = False
        status = utils.safe_value(record, "status")
        if not value and status in ["queued", "running"]:
            value = 0
            start = None

            # need to compute on the fly
            if col == "queued":
                start = utils.safe_value(record, "created")
            elif col == "duration":
                start = utils.safe_value(record, "started")

            if start:
                start_value = utils.get_time_from_arrow_str(start)
                value = time.time() - start_value
                ongoing = True

        if not value:
            value = ""
        else:
            secs = float(value)   # in case its a string
            secs_per_day = 60*60*24
            days = secs/secs_per_day
            plus = "+" if ongoing else ""

            if days >= 1:
                value = "{}{:,.1f} days".format(plus, days)
            else:
                hrs = days*24
                if hrs >= 1:
                    value = "{}{:,.1f} hrs".format(plus, hrs)
                else:
                    mins = hrs*60
                    if mins > 1:
                        value = "{}{:,.1f} mins".format(plus, mins)
                    else:
                        secs = mins*60
                        value = "{}{:,.1f} secs".format(plus, secs)

        return value

    def get_report_color(self, config_section, config_name):
        color_name = self.config.get(config_section, config_name).upper()
        color = getattr(pc_utils, color_name) if color_name else pc_utils.NORMAL

        return color

    def generate_report(self, col_infos, records, right_align_num_cols, uppercase_hdr_cols, truncate_with_ellipses, 
        col_space, duration_col_names, time_col_names, significance, max_fixed_length, float_precision):

        # process COLUMN HEADERS
        text = ""
        first_col = True
        if self.config:
            color_highlight = self.get_report_color("run-reports", "color-highlight")
            color_hdr = self.get_report_color("run-reports", "color-hdr")
            highlight_exp = self.config.get("run-reports", "highlight")
        else:
            color_highlight = None
            highlight_exp = None
            color_hdr = None

        if color_highlight or color_hdr:
            pc_utils.enable_ansi_escape_chars_on_windows_10()

        if color_hdr:
            text += color_hdr

        for col_info in col_infos:
            if first_col:
                first_col = False
            else:
                text += " " * col_space

            user_fmt = col_info["user_fmt"] 
            col_width = col_info["col_width"]
            col_name = col_info["user_name"].upper() if uppercase_hdr_cols else col_info["user_name"]
            
            right_align = right_align_num_cols and (col_info["is_numeric"] or user_fmt) or \
                col_info["name"] in duration_col_names

            if truncate_with_ellipses and len(col_name) > col_width:
                col_text = col_name[0:col_width-3] + "..."
            elif right_align:
                fmt = ":>{}.{}s".format(col_width, col_width)
                fmt = "{" + fmt + "}"
                col_text = fmt.format(col_name)
            else:
                fmt = ":<{}.{}s".format(col_width, col_width)
                fmt = "{" + fmt + "}"
                col_text = fmt.format(col_name)

            text += col_text

        if color_hdr:
            text += pc_utils.NORMAL

        header_line = text
        text += "\n\n"
        row_count = 0

        # process VALUE ROWS
        for row_num, record in enumerate(records):
            first_col = True
            highlighted = False

            if highlight_exp and color_highlight:
                if self.should_highlight_row(highlight_exp, record):
                    text += color_highlight
                    highlighted = True

            if row_num % 500 == 0:
                console.diag("build_formatted_table: processing row: {}".format(row_num))

            col = None
            try:
                for col_info in col_infos:
                    if first_col:
                        first_col = False
                    else:
                        text += " " * col_space

                    user_fmt = col_info["user_fmt"] 
                    col = col_info["name"]
                    value_type = col_info["value_type"]

                    right_align = right_align_num_cols and (col_info["is_numeric"] or user_fmt or \
                        col_info["value_type"] == bool) or col in duration_col_names

                    col_width = col_info["col_width"]
                    align = ">" if right_align else "<"

                    if not col in record:
                        # not all records define all columns
                        str_fmt = "{:" + align + str(col_width)  + "." + str(col_width) + "s}"
                        text += str_fmt.format("")
                    else:
                        value = record[col]

                        # special handling for int values that were logged as floats
                        if isinstance(value, float) and value_type is int:
                            value = int(value)

                        #console.print("col=", col, ", value=", value, ", type(value)=", type(value))

                        # special formatting for time values
                        if col in duration_col_names:
                            value = self.format_duration(value, col, record)
                        elif col in time_col_names:
                            if isinstance(value, str):
                                value = arrow.get(value)
                            value = value.format('YYYY-MM-DD @HH:mm:ss')

                        if user_fmt:
                            # user provided explict format for this column
                            if "$" in user_fmt:
                                # custom XT formatting
                                value = self.xt_custom_format(user_fmt, value)
                            else:
                                value = user_fmt.format(value)   

                            # now treat as string that must fit into col_width
                            str_fmt = "{:" + align + str(col_width)  + "." + str(col_width) + "s}"
                            #value = value if value else ""
                            value = "" if value is None else value
                            text += str_fmt.format(value)
                        elif isinstance(value, float):

                            # default (smart) FLOAT formatting
                            precision = col_info["precision"] if "precision" in col_info else float_precision
                            if precision > max_fixed_length:
                                # use SCIENTIFIC NOTATION
                                float_fmt = "{:" + align + str(col_width) + "." + str(significance-1) + "e}"
                            else:
                                # use FIXED POINT formatting
                                float_fmt = "{:" + align + str(col_width) + "." + str(precision) + "f}"

                            text += float_fmt.format(value)

                        elif isinstance(value, bool):
                            bool_fmt = "{!r:" + align + str(col_width) + "}"
                            text += bool_fmt.format(value)
                        elif isinstance(value, int):
                            int_fmt = "{:" + align + str(col_width) + "d}"
                            text += int_fmt.format(value)
                        else:
                            if col == "sku":
                                dummy = 3
                            # ensure value is a string
                            value = "" if value is None else str(value)
                            str_fmt = "{:" + align + str(col_width)  + "." + str(col_width) + "s}"
                            text += str_fmt.format(value)

            except BaseException as ex:
                console.print("Exception formatting col={}: {}".format(col, ex))
                console.print("  Exception record: {}".format(record))

            if highlighted:
                text += pc_utils.NORMAL

            text += "\n"
            row_count += 1
        
        # all records processed
        if row_count > 5:
            # console.print header and run count
            text += "\n" + header_line + "\n"
    
        return text, row_count

    def group_by(self, records, group_col):
        groups = {}
        for rec in records:
            if not group_col in rec:
                continue

            group = rec[group_col]

            if not group in groups:
                groups[group] = []

            groups[group].append(rec)

        return groups

if __name__ == "__main__":
    # test out simple use of ReportBuilder
    builder = ReportBuilder()

    records = []
    for i in range(1, 11):
        age = np.random.randint(2*i)
        income = np.random.randint(10000*i)
        record = {"name": "roland" + str(i), "age": age, "income": income}
        records.append(record)

    text, _ = builder.build_formatted_table(records)
    print(text)

