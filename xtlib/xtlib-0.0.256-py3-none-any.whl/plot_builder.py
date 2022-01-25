#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# self.py: functions to help produce plots of metrics from runs
import math
import time
from azureml.core import experiment
import numpy as np
import pandas as pd

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import console
from xtlib import constants
from xtlib import run_helper
from xtlib import job_helper
from xtlib import store_utils

PRESMOOTH = "_PRE-SMOOTH_"
ERR = "_ERR_"
MEAN = "_MEAN_"
MIN = "_MIN_"
MAX = "_MAX_"

class PlotBuilder():
    def __init__(self, store, run_names, col_names, x_col, layout, break_on, title, show_legend, plot_titles,
            legend_titles, smoothing_factor, plot_type, timeout,
            aggregate, shadow_type, shadow_alpha, run_log_records, style, show_toolbar, max_traces,
            group_by, error_bars, show_plot, save_to, x_label, x_labels_col,
            y_label, colors, color_map, color_steps, legend_args, 
            x_min, x_max, y_min, y_max, alpha, color_indexes, line_styles, line_sizes, timebase, x_format, y_format, 
            x_share, y_share, background_color, grid_color, clean, width, height, highlight, color_highlight,
            legend_suffix, col_source, x_int, y_int, bins, legend_vars, margins, metric_aliases, y_ticks,
            plot_args):
        
        self.store = store
        self.group_names = None
        self.run_names = run_names
        self.col_names = col_names
        self.x_col = x_col
        self.legend_title_vars = legend_vars
        self.layout = layout
        self.break_on = break_on
        self.title = title
        self.show_legend = show_legend
        self.plot_titles = plot_titles
        self.legend_titles = legend_titles
        self.smoothing_factor = smoothing_factor
        self.plot_type = plot_type
        self.timeout = timeout
        self.aggregate = utils.zap_none(aggregate)
        self.shadow_type = utils.zap_none(shadow_type)
        self.shadow_alpha = shadow_alpha
        self.run_log_records = run_log_records
        self.style = utils.zap_none(style)
        self.show_toolbar = show_toolbar
        self.max_traces = max_traces
        self.group_by = group_by if group_by and group_by != "none" else "run"
        self.error_bars = utils.zap_none(error_bars)
        self.show_plot = show_plot
        self.save_to = save_to
        self.x_label = x_label
        self.x_labels_col = x_labels_col
        self.y_label = y_label
        self.legend_args = legend_args
        self.plot_args = plot_args
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.alpha = alpha
        self.color_indexes = color_indexes
        self.line_styles = line_styles
        self.line_sizes = line_sizes
        self.timebase = timebase
        self.x_format = x_format
        self.y_format = y_format
        self.x_share = x_share
        self.y_share = y_share
        self.background_color = background_color
        self.grid_color = grid_color
        self.clean = clean
        self.width = width 
        self.height = height
        self.highlight = highlight
        self.color_highlight = color_highlight
        self.legend_suffix = legend_suffix
        self.group_info = None
        self.ws_name = None
        self.col_source = col_source
        self.x_int = x_int
        self.y_int = y_int
        self.bins = bins
        self.break_filter_name = None
        self.break_filter_value = None
        self.runs_per_plot = None
        self.cols_per_plot = None
        self.x_values = None
        self.x_labels = None
        self.margins = margins
        self.metric_aliases = metric_aliases
        self.all_visible = True
        self.y_ticks = y_ticks

        if colors:
            self.colors = colors
        else:
            if not color_map:
                color_map = "cycle"
            self.colors = self.get_colors(color_map, color_steps)

    def get_colors(self, color_map_name, steps):
        from matplotlib import cm

        if color_map_name == "cycle":
            # matplotlab default colors (V2.0, category10 color palette)

            colors = \
                 ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                 '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                 '#bcbd22', '#17becf']
        else:
            color_map = cm.get_cmap(color_map_name)
            colors = color_map( np.linspace(0, 1, steps) )

        return colors

    def build(self):

        group_order_dict = {}

        data_frames_by_cols = self.build_data_frames(group_order_dict)
        if data_frames_by_cols:

            for cols, dfx in data_frames_by_cols.items():
                dfx = self.pre_preprocess_data_frame(dfx)
                data_frames_by_cols[cols] = dfx

            # this check is to enable faster testing
            if self.show_plot or self.save_to:
                self.plot_data(data_frames_by_cols)

    def get_group_value(self, group_by, run, node, job, experiment, workspace, record):
        value = None

        if group_by == "run":
            value = run
        elif group_by == "node":
            value = node
        elif group_by == "job":
            value = job
        elif group_by == "experiment":
            value = experiment
        elif group_by == "workspace":
            value = experiment
        elif group_by in record:
            value = record[group_by]
        else:
            raise Exception("unrecognized group-by name: " + str(group_by))

        return value

    def build_data_frames(self, group_order_dict):
        '''
        Processing:
            - for each run, collect the user-requested columns as metric sets 
            - append to the dataframe for that col list
            - report missing metrics
        '''
        # build "data_frames"
        no_metrics = []
        pp_run_names = []
        used_max = False
        data_frames_by_cols = {}
        explicit_options = qfe.get_explicit_options()
        missing_col_runs = 0
        missing_metrics = {}
        metric_sets = []

        self.group_info = {}
        
        # for each RUN (or node or job)
        for i, record in enumerate(self.run_log_records):
            # extract metrics for this run
            run = record["run_name"]
            console.diag(run)

            job = record["job_id"]
            node = job + "/" + utils.node_id(record["node_index"])
            experiment = record["exper_name"]
            workspace = record["ws_name"]

            # remember for later use
            self.ws_name = workspace

            group_value = self.get_group_value(self.group_by, run, node, job, experiment, workspace, record)
            if not group_value in group_order_dict:
                group_order_dict[group_value] = 1

            info_record = {"run": run, "job": job, "node": node, "experiment": experiment}   

            # fixup any aggregated items as "*"
            if not self.group_by in ["run"]:
                info_record["run"] = "run*"

            if not self.group_by in ["run", "node"]:
                info_record["node"] = "node*"

            if not self.group_by in ["run", "node", "job"]:
                info_record["job"] = "job*"

            # add fields used by legend titles
            for col in self.legend_title_vars:
                if col in record:
                    info_record[col] = record[col]
                
            self.group_info[group_value] = info_record

            # search_style = utils.safe_value(record, "search_style")
            # if search_style and search_style != "single":
            #     # parent run with children - skip it
            #     continue

            metric_sets = self.extract_data_from_run(record, no_metrics, run)
            
            missing_col_runs = self.build_data_frames_from_metric_sets(run, metric_sets, missing_metrics, 
                node, job, experiment, workspace, data_frames_by_cols, record)

            pp_run_names.append(run)

        # report on runs missing metrics
        for run, md in missing_metrics.items():
            cols = ", ".join(md.keys())
            console.print("warning: {} (missing columns: {})".format(run, cols))

        if no_metrics:
            console.print("\nnote: following runs currently have no logged metrics: \n    {}\n".format(", ".join(no_metrics)))

        # if used_max:
        #     console.print("plotting first {} runs (use --max-runs to override)".format(self.max_runs))
        elif pp_run_names:
            console.print("plotting {} runs...".format(len(pp_run_names)))
        else:
            console.print("no matching runs found")
            data_frames_by_cols = None

            if missing_col_runs:
                # some runs missing columns - display list of columns in all metric sets
                cols = set()
                for ms in metric_sets:
                    cols = cols.union(ms["keys"])

                cols = ", ".join(list(cols))
                console.print("available metrics to plot: \n  {}".format(cols))

        # update our list of run_names to proces
        self.run_names = pp_run_names

        # update our list of group names (the order they will be processed in)
        self.group_names = list(group_order_dict)

        return data_frames_by_cols

    def extract_data_from_run(self, record, no_metrics, run_name):
        if self.col_source == "metrics":

            # METRICS
            alias_to_actual = None
            if self.metric_aliases:
                alias_to_actual = {alias: actual for actual, alias in zip(self.col_names, self.metric_aliases)}

            log_records = utils.safe_value(record, "log_records", [])
            missing_col_runs = 0

            metric_sets = run_helper.build_metrics_sets(log_records, timebase=self.timebase, cleanup=self.clean, 
                alias_to_actual=alias_to_actual)

            if metric_sets:
                # add data from legend_title vars
                for ms in metric_sets:
                    for lg_col in self.legend_title_vars:
                        if lg_col in record:
                            value = record[lg_col]
                            for r in ms["records"]:
                                r[lg_col] = value

            else:
                no_metrics.append(run_name)
        else:
            # STD or HPARAMS
            mr = {}

            # add data for x_col
            if self.x_col:
                self.add_col_from_record(mr, record, self.x_col)

            # add data for group_col
            if self.group_by:
                self.add_col_from_record(mr, record, self.group_by)

            # add data for y_cols
            for y_col in self.col_names:
                self.add_col_from_record(mr, record, y_col)

            # add data for break_on cols
            if self.break_on:
                for i, col in enumerate(self.break_on):
                    if not col in ["run", "col", "group", "node"]:
                        self.add_col_from_record(mr, record, col)

            # add data from x_labels_col
            if self.x_labels_col:
                self.add_col_from_record(mr, record, self.x_labels_col)

            # add data from legend_title vars
            for lg_col in self.legend_title_vars:
                self.add_col_from_record(mr, record, lg_col)

            metric_sets = [ {"keys": list(mr), "records": [mr]} ]

        return metric_sets

    def add_col_from_record(self, mr, record, col_name):
        # if col_name.startswith("hparams."):
        #     col_name = col_name[8:]
        #     if "hparams" in record:
        #         hp = record["hparams"]
        #         if col_name in hp:
        #             mr[col_name] = hp[col_name]
        if col_name in record:
            mr[col_name] = record[col_name]

        return col_name

    def build_data_frames_from_metric_sets(self, run, metric_sets, missing_metrics, node, job, 
        experiment, workspace, data_frames_by_cols, record):
        '''
        Processing:
            - build a dataframe for each metric_set of run and add to data_frames_by_cols
            - return missing_col_runs
        '''
        missing_col_runs = 0

        if self.x_col:
            # ensure x_col is in this run
            if not self.is_col_in_sets(metric_sets, self.x_col):

                # add to missing_metrics
                if not run in missing_metrics:
                    missing_metrics[run] = {}
                missing_metrics[run][self.x_col] = True

                missing_col_runs += 1
                #continue    # SKIP this run
        else:
            #if not "x" in explicit_options:
            self.x_col = self.get_actual_x_column(metric_sets, self.x_col, self.col_names)
            
        if self.col_names:
            # ensure col_names are in run
            found_all = True

            for col in self.col_names:
                if not self.is_col_in_sets(metric_sets, col):

                    # add to missing_metrics
                    if not run in missing_metrics:
                        missing_metrics[run] = {}
                    missing_metrics[run][col] = True

                    found_all = False
                    break

            if not found_all:
                missing_col_runs += 1
                #continue    # SKIP this run
        else:
            # not specified by user, so build defaults
            self.col_names = self.get_default_y_columns(metric_sets, self.x_col)

        # merge metric sets into dfx
        for metric_set in metric_sets:

            # create a pandas DataFrame
            df = pd.DataFrame(metric_set["records"])
            cols = str(list(df.columns))
            
            # ensure this df has our x_col 
            if self.x_col and not self.x_col in cols:
                #continue
                pass

            # ensure this df has at least 1 y_col
            found_y = False
            for y in self.col_names:
                if y in cols:
                    found_y = True
                    break

            if not found_y:
                #continue
                pass

            # add run_name column
            count = df.shape[0]

            if self.col_source == "metrics":
                df_run_name = run
            else:
                # for std/hparam cols, treat each run as a single record of "runs" object
                #df_run_name = "runs"
                df_run_name = run

            df["run"] = [df_run_name] * count
            df["node"] = [node] * count
            df["job"] = [job] * count
            df["experiment"] = [experiment] * count
            df["workspace"] = [workspace] * count

            # add legend title variables
            for var in self.legend_title_vars:
                df[var] = record[var]

            if not cols in data_frames_by_cols:
                data_frames_by_cols[cols] = df
            else:
                dfx = data_frames_by_cols[cols]
                dfx = dfx.append(df)
                data_frames_by_cols[cols] = dfx

        return missing_col_runs

    def get_agg_df(self, df, agg_op, df_cols):
        agg_dict = {}
        df_out = None

        for col in self.col_names:
            if col in df_cols:
                agg_dict[col] = agg_op

        # if not agg_dict:
        #     errors.config_error("Some columns not found: {}".format(self.col_names))

        if agg_dict:
            df_out = df.agg(agg_dict)  
            #df3 = df2.fillna(method='ffill')
            df_out = df_out.reset_index()

        return df_out

    def pre_preprocess_data_frame(self, dfx):
        '''
        apply pre-processing operations to specified data frame:
            - data frame most likely will NOT contain all y cols
            - optionally smooth the Y-axis cols
            - optionally create aggregate VALUE Y-axis cols
            - optionally create aggregate SHADOW Y-axi cols
        '''
        if self.smoothing_factor:
            # SMOOTH each column of values

            for col in self.col_names:
                if col in dfx.columns:
                    self.apply_smooth_factor(dfx, col, self.smoothing_factor)

        # get a copy of columns before group-by
        dfx_pre = dfx
        df_cols = list(dfx.columns)

        if self.aggregate:
            # specifying an aggregate hides the the other runs' values (for now)

            if self.group_by:
                # GROUP data 
                group_col = self.group_by
                #group_prefix = "node" if self.group_by == "node_index" else ""
                x_col = self.x_col

                dfx = dfx.groupby([group_col, x_col], sort=False)
            
            # AGGREGATE data
            df_agg_from = dfx
            dfx = self.get_agg_df(df_agg_from, self.aggregate, df_cols)

            # ERROR BARS data
            if self.error_bars:
                dfx = self.build_agg_stat(df_agg_from, self.error_bars, df_cols, dfx)

            # SHADOW TYPE BARS data
            if self.shadow_type == "min-max":
                dfx = self.build_agg_stat(df_agg_from, "min", df_cols, dfx)
                dfx = self.build_agg_stat(df_agg_from, "max", df_cols, dfx)
            elif self.shadow_type and self.shadow_type != "pre-smooth":
                dfx = self.build_agg_stat(df_agg_from, "mean", df_cols, dfx)
                dfx = self.build_agg_stat(df_agg_from, self.shadow_type, df_cols, dfx)

            # if self.shadow_type:
            #     self.run_names.append(self.shadow_type)

            #     min_values, max_values = self.range_runs(runs_dict, self.shadow_type)
            #     runs_dict[self.shadow_type] = (min_values, max_values)

            # for col in self.legend_title_vars:
            #     dfx = self.build_agg_stat(df_agg_from, self.shadow_type, df_cols, dfx)

        return dfx

    def build_agg_stat(self, df_agg_from, stat, df_cols, dfx):
        df_stat = self.get_agg_df(df_agg_from, stat, df_cols)

        # not all data sets in job must be used, so allow some to be empty
        if df_stat is not None:
            stat_name = "_{}_".format(stat.upper())

            for col in self.col_names:
                if col in df_stat.columns:
                    # extract stat data for col
                    stat_data = df_stat[col]

                    # add col data as new name to dfx
                    dfx[col + stat_name] = stat_data

        return dfx

    def apply_smooth_factor(self, data_frame, col, weight):

        presmooth_values = list(data_frame[col])
        smooth_values = self.apply_smooth_factor_core(presmooth_values, weight)

        data_frame[col] = smooth_values
        data_frame[col + PRESMOOTH] = presmooth_values

    def apply_smooth_factor_core(self, values, weight):
        smooth_values = []

        if values:
            prev = values[0] 
            for value in values:
                smooth = weight*prev + (1-weight)*value
                smooth_values.append(smooth)                       
                prev = smooth                                 

        return smooth_values

    def calc_actual_layout(self, count, layout):
        if not "x" in layout:
            errors.syntax_error("layout string must be of form RxC (R=# rows, C=# cols)")

        r,c = layout.split("x", 1)

        if r:
            r = int(r)
            c = int(c) if c else math.ceil(count / r)
        elif c:
            c = int(c)
            r = int(r) if r else math.ceil(count / c)

        full_count = r*c
        if full_count < count:
            errors.combo_error("too many plots ({}) for layout cells ({})".format(count, full_count))

        return r, c

    def get_col_values(self, col_name):

        values = None

        for cols, df in self.data_frames_by_cols.items():
            if col_name in df.columns:
                #values = make_floats(df[ col_name ])
                values = list(df[ col_name ])

        return values
        
    def get_unique_values(self, col_name):

        values = None

        for cols, df in self.data_frames_by_cols.items():
            if col_name in df.columns:
                #values = make_floats(df[ col_name ])
                all_values = list(df[ col_name ])

                # extract the unique values while preserving order
                used = {value: 1 for value in all_values }
                values = list(used)

                #print("values", values)
                break

        return values

    def get_xy_values(self, data_frames_by_cols, group_name, x_col, y_col, stat_col, force_floats=True):

        x_values = None
        y_values = None
        stat_values = None

        '''
        Note: a specific y_col could exist in different data_frames, depending
        on the other columns logged with in during each run.  So, don't stop
        searching on the first match with y_col - keep going until we get a 
        matching set of group_name records also.
        '''

        for cols, df in data_frames_by_cols.items():
            #if y_col in df.columns:
            if df is not None and y_col in df.columns:  
                
                # filter values for specified run name
                group_indexes = df[self.group_by]==group_name 
                df = df[group_indexes]

                # filter for break on actual col
                if self.break_filter_name:
                    group_indexes = df[self.break_filter_name]==self.break_filter_value 
                    df = df[group_indexes]

                record_count = len(df.index)

                if record_count:  #  or force_value:
                    if force_floats:
                        y_values = make_floats(df[ y_col ])
                    else:
                        y_values = list(df[ y_col ])

                    if x_col and x_col in df.columns:
                        if x_col == "__time__":
                             x_values = df[ x_col ].to_numpy()
                        else:
                            x_values = make_floats(df[ x_col ])

                    if stat_col and stat_col in df.columns:
                        stat_values = df[ stat_col ].to_numpy(dtype=float)
                    break

        if x_values is not None and y_values is not None:
            if self.has_line_segments(x_values):

                x_values, y_values, stat_values = \
                    self.join_line_segments(x_values, y_values, stat_values)

        return x_values, y_values, stat_values

    def has_line_segments(self, x_values):
        last_x = None
        has_segments = False

        for x in x_values:
            if last_x and x <= last_x:
                has_segments = True
                break
            last_x = x

        return has_segments

    def join_line_segments(self, x_values, y_values, stat_values):
        '''
        Processing:
            Converts x and stat values into numpy masked arrays, which are honored
            by matplotlib to correctly draw line segments.  For every line segment
            detected, we insert a dummy point to be ignored in the mask.
        '''
        last_x = None
        has_segments = False
        new_x = []
        new_y = []
        new_stat = []
        mask = []

        for i, x in enumerate(x_values):
            if last_x and x <= last_x:
                # insert a dummy point to ignore
                new_x.append(x)
                new_y.append(0)
                if stat_values:
                    new_stat.append(0)
                mask.append(True)

            # add current point
            new_x.append(x)
            new_y.append(y_values[i])
            if stat_values:
                new_stat.append(stat_values[i])
            mask.append(False)
            last_x = x

        new_x = np.array(new_x)
        new_y = np.array(new_y)
        new_stat = np.array(new_stat) if stat_values else stat_values

        # build mask array for y
        import numpy.ma as ma
        new_y = ma.array(new_y, mask=mask)

        # build mask array for new_stat
        if new_stat:
            new_stat = ma.array(new_stat, mask=mask)

        return new_x, new_y, new_stat

    def build_series(self):
        break_on = self.break_on
        break_count = len(break_on) if break_on else 0

        if break_count > 2:
            errors.general_error("break_on cannot be more than 2 values: {}".format(break_on))

        group_names = self.group_names
        group_count = len(group_names)

        col_names = self.col_names
        col_count = len(col_names)

        # decide how layout, titles, etc. will be set
        break_on_groups = self.break_on and ("run" in self.break_on or "group" in self.break_on \
            or "node" in self.break_on)
        break_on_cols = self.break_on and "col" in self.break_on

        # build list of loops to be generated 
        loops = []

        col_entry = {"name": "_col_", "break": break_on_cols, "data": self.col_names}
        group_entry = {"name": "_group_", "break": break_on_groups, "data": self.group_names}

        if break_on_groups:
            loops.append(col_entry)
            loops.append(group_entry)
        elif break_on_cols:
            loops.append(group_entry)
            loops.append(col_entry)
        else:
            loops.append(col_entry)
            loops.append(group_entry)

        if break_on:
            # add loops from break_on
            for break_name in break_on:
                if not break_name in ["run", "node", "col", "group"]:
                    # its a actual col name

                    # for now, we only allow 1 of these
                    if self.break_filter_name:
                        errors.general_error("only 1 actual col name can be specifed in break-on: {}". \
                            format(break_on))

                    self.break_filter_name = break_name

                    break_values = self.get_unique_values(break_name)
                    actual_col = {"name": break_name, "break": True, "data": break_values}
                    loops.append(actual_col)

        series, plot_count = self.generate_series_from_loops(loops)

        runs_per_plot = 1 if break_on_groups else group_count
        cols_per_plot = 1 if break_on_cols else col_count
        
        return series, plot_count, runs_per_plot, cols_per_plot

    def generate_series_from_loops(self, loops):

        series = []
        line_index = 0
        plot_index = 0

        for loop_entry in loops:
            name = loop_entry["name"]
            is_break = loop_entry["break"]
            values = loop_entry["data"]
            new_series = []
            line_index = 0

            for value in values:
                if series:
                    # not the first series: copy existing series and add our name/value to each entry
                    for entry in series:
                        new_entry = dict(entry)

                        new_entry[name] = value
                        if is_break:
                            new_entry["plot_index"] = plot_index
                        else:
                            new_entry["line_index"] = line_index
                            line_index += 1

                        new_series.append(new_entry)

                    if is_break:
                        plot_index += 1
                        line_index = 0
                else:
                    # no series entries yet: create an entry for each data value in loop_entry
                    entry = {name: value, "line_index": line_index, "plot_index": plot_index}
                    new_series.append(entry)

                    if is_break:
                        plot_index += 1
                        line_index = 0
                    else:
                        line_index += 1

            series = new_series

        plot_count = max(1, plot_index)
        return series, plot_count

    def plot_data(self, data_frames_by_cols):
        console.diag("starting to plot data")
        self.data_frames_by_cols = data_frames_by_cols

        # on-demand import for faster XT loading
        import seaborn as sns
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        import pylab

        if not self.show_toolbar:
            # hide the ugly toolbar at bottom left of plot window
            mpl.rcParams['toolbar'] = 'None' 

        # apply seaborn styling
        if self.style:
            sns.set_style(self.style)

        series, plot_count, runs_per_plot, cols_per_plot = self.build_series()
        self.runs_per_plot = runs_per_plot
        self.cols_per_plot = cols_per_plot

        # calc true layout 
        if self.layout:
            plot_rows, plot_cols = self.calc_actual_layout(plot_count, self.layout) 
        else:
            plot_cols = plot_count
            plot_rows = 1

        if cols_per_plot == 1:
            plot_title = "$col"
            legend_text = "$group"
        elif runs_per_plot == 1:
            plot_title = "$group"
            legend_text = "$col"
        else:
            plot_title = None
            legend_text = "$col ($group)"

        if not self.plot_titles and plot_title:
            self.plot_titles = [plot_title]

        if not self.legend_titles:
            self.legend_titles = [legend_text]

        # configure matplotlib for our subplots
        sharex = self.x_share
        sharey = self.y_share

        #plt.close()
        window_size = (self.width, self.height)

        fig, plots = plt.subplots(plot_rows, plot_cols, figsize=window_size, sharex=sharex, sharey=sharey, constrained_layout=True)
        if not isinstance(plots, np.ndarray):
            # make it consistent with plot_count > 1 plots
            plots = [plots]
        elif plot_rows > 1:
            plots = plots.flatten()

        group = self.group_names[0]
        title = self.fixup_text(self.title, group, None)
        fig.suptitle(title, fontsize=16)

        if self.timeout:
            # build a thread to close our plot window after specified time
            from threading import Thread

            def set_timer(timeout):
                console.print("set_timer called: timeout=", self.timeout)
                time.sleep(self.timeout)
                console.diag("timer triggered!")

                plt.close("all")
                print("closed all plots and the fig")

            thread = Thread(target=set_timer, args=[self.timeout])
            thread.daemon = True    # mark as background thread
            thread.start()

        x_label = self.x_label if self.x_label else self.x_col
        y_label = self.y_label 
            
        if self.aggregate == "none":
            self.aggregate = None

        # plot each series in one of the subplots
        for i, entry in enumerate(series):
            line_index = entry["line_index"]
            plot_index = entry["plot_index"]
            group_name = entry["_group_"]
            col = entry["_col_"]

            if self.break_filter_name:
                self.break_filter_value = entry[self.break_filter_name]

            ax = plots[plot_index] #.gca()
            self.plot_middle(data_frames_by_cols, ax, group_name, col, \
                self.x_col, x_label, line_index, plot_index)

        self.finish_plot(plt, fig, plots, pylab)

    def finish_plot(self, plt, fig, plots, pylab):

        if self.save_to:
            plt.savefig(self.save_to)

        # maximize plot window
        # mgr = plt.get_current_fig_manager()
        # mgr.window.full_screen_toggle(True)

        self.adjust_legend_fonts(plots)

        ax = plots[0]

        if self.x_col == "__time__":
            import matplotlib.dates as mdates

            locator = mdates.AutoDateLocator(minticks=10, maxticks=20)
            formatter = mdates.ConciseDateFormatter(locator)

            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)            
            #plt.gcf().autofmt_xdate()

        elif self.x_format:
            import matplotlib
            user_fmt = lambda x, p: format(x, self.x_format)
            ff = matplotlib.ticker.FuncFormatter(user_fmt)
            ax.get_xaxis().set_major_formatter(ff)

        if self.y_format:
            import matplotlib
            user_fmt = lambda y, p: format(y, self.y_format)
            ff = matplotlib.ticker.FuncFormatter(user_fmt)
            ax.get_yaxis().set_major_formatter(ff)

        if self.x_int:
            # force x-axis ticks on integer values
            from matplotlib.ticker import MaxNLocator
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if self.y_int:
            # force y-axis ticks on integer values
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # force all axis labels visible
        for ax in plots:   
            ax.xaxis.set_tick_params(labelbottom=True)
            ax.yaxis.set_tick_params(labelleft=True)

            # set axis limits (on each subplot)
            ax.set_ylim(bottom=self.y_min, top=self.y_max)
            ax.set_xlim(left=self.x_min, right=self.x_max)

            # for now, we override xticks set during plot with a single (longest) values
            if self.x_labels is not None:
                ax.set_xticks(self.x_values)
                ax.set_xticklabels(self.x_labels)

            if self.margins:
                if "," in self.margins:
                    x, y = self.margins.split(",")
                    ax.margins(float(x), float(y))
                else:
                    ax.margins(float(self.margins))

        if self.y_ticks:
            ax.set_yticks(self.y_ticks)

        self.enable_legend_picking(fig, plots)

        if self.show_plot:
            pylab.show()
            #fig.canvas.draw()

    def enable_legend_picking(self, fig, plots):
        ''' set up legend picking to toggle line visibility'''
        plot_dict = dict()
        count = len(plots)   # this is the count of subplots 

        for ax in plots:
            legend = ax.get_legend()
            legend_lines = legend.get_lines()

            for i, legend_line in enumerate(legend_lines):
                legend_line.set_picker(True)  # 5 pts tolerance
                legend_line.set_pickradius(5)
                plot_dict[legend_line] = i

        def onpick(event):
            # on the pick event, find the orig line corresponding to the
            # legend proxy line, and toggle the visibility
            legend_line = event.artist
            line_index = plot_dict[legend_line]

            for ax in plots:
                lines = ax.get_lines()
                line = lines[line_index]

                was_visible = line.get_visible()

                visible = not was_visible
                line.set_visible(visible)

                legend = ax.get_legend()
                legend_lines = legend.get_lines()                # adjust alpha for corresponding legend line

                legend_line = legend_lines[line_index]
                if visible:
                    legend_line.set_alpha(1.0)
                else:
                    legend_line.set_alpha(0.2)

            # redraw changes to plot canvas
            fig.canvas.draw()

        def onclick(event):
            if event.button == 3:
                self.all_visible = not self.all_visible

                # toggle all lines visible/hidden
                for ax in plots:
                    lines = ax.get_lines()
                    legend = ax.get_legend()
                    legend_lines = legend.get_lines()

                    for line, legend_line in zip(lines, legend_lines):
                        line.set_visible(self.all_visible)
                        alpha = 1 if self.all_visible else .2
                        legend_line.set_alpha(alpha)

                # redraw changes to plot canvas
                fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', onpick)            
        fig.canvas.mpl_connect('button_press_event', onclick)

    def adjust_legend_fonts(self, plots):
        import matplotlib as mpl

        size = 10
        normal_font = mpl.font_manager.FontProperties(size=size)
        is_alive = False
        alive_font = None
        alive_color = None
        group_keys = list(self.group_info.keys())

        if self.highlight == "$alive":
            # choose a font that support color_highlight
            if self.color_highlight == "bold":
                alive_font = mpl.font_manager.FontProperties(size=size, weight='bold')
            elif self.color_highlight == "italic":
                alive_font = mpl.font_manager.FontProperties(size=size, style='italic')
            elif self.color_highlight:
                alive_color = self.color_highlight

        for ax in plots:
            # adjust font styling for legends
            legend = ax.get_legend()
            if legend:
                alive_dict = None

                if self.highlight == "$alive":
                    group_values = list(self.group_info.keys())
                    alive_dict = self.get_alive_status(group_values)

                for i, texts in enumerate(legend.get_texts()):

                    if self.highlight == "$alive":
                        key_index = i % len(group_keys)
                        group_name = group_keys[key_index]
                        is_alive = group_name in alive_dict

                    if is_alive:
                        if alive_color:
                            texts.set_color(alive_color)
                        else:
                            texts.set_fontproperties(alive_font)
                    else:
                        texts.set_fontproperties(normal_font)

    def get_alive_status(self, names):
        alive_dict = {}
        first_name = names[0]

        if run_helper.is_run_name(first_name):

            # are specified RUNS alive?
            id_list = [store_utils.make_id(self.ws_name, name) for name in names]
            filter_dict = {"_id": {"$in": id_list}}
            fields_dict = {"_id": 1, "status": 1}
            
            records = self.store.database.get_info_for_runs(self.ws_name, filter_dict, fields_dict)
            store_utils.simplify_records_id(records)

            for record in records:
                status = utils.safe_value(record, "status")
                if status in ["queued", "running"]:
                    run_name = record["_id"]
                    alive_dict[run_name] = True

        elif job_helper.is_job_id(first_name):
            # are RUNS alive in specified JOBS
            filter_dict = {"job_id": {"$in": names}}
            fields_dict = {"job_id": 1, "status": 1}
            
            records = self.store.database.get_info_for_runs(self.ws_name, filter_dict, fields_dict)
            store_utils.simplify_records_id(records)

            for record in records:
                status = utils.safe_value(record, "status")
                if status in ["queued", "running"]:
                    job_name = record["job_id"]
                    alive_dict[job_name] = True

        else:
            # are RUNS alive in specified EXPERIMENTS
            filter_dict = {"exper_name": {"$in": names}}
            fields_dict = {"exper_name": 1, "status": 1}
            
            records = self.store.database.get_info_for_runs(self.ws_name, filter_dict, fields_dict)
            store_utils.simplify_records_id(records)

            for record in records:
                status = utils.safe_value(record, "status")
                if status in ["queued", "running"]:
                    exper_name = record["exper_name"]
                    alive_dict[exper_name] = True

        return alive_dict

    def get_seaborn_color_map(self, name, n_colors=5):
        '''
        name: muted, xxx
        '''
        import seaborn as sns
        from matplotlib.colors import ListedColormap

        # Construct the colormap
        current_palette = sns.color_palette(name, n_colors=n_colors)
        cmap = ListedColormap(sns.color_palette(current_palette).as_hex())
        return cmap

    def plot_middle(self, data_frames_by_cols, ax, group_name, col, x_col, x_label, line_index, plot_index):
        
        if self.background_color:
            ax.set_facecolor((self.background_color))            

        if self.grid_color:
            ax.grid(color=self.grid_color)   # , linestyle='-', linewidth=2)

        if self.shadow_type == "pre-smooth":
            # draw PRESMOOTH SHADOW
            x, y, _ = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col + PRESMOOTH, None)

            self.plot_inner(ax, group_name, col, self.x_col, x_label, line_index, plot_index, x_values=x, y_values=y,
                alpha=self.shadow_alpha, use_y_label=False)
        elif self.shadow_type:

            if self.shadow_type == "min-max":
                x, y, _ = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col + MIN, None)
                x2, y2, _ = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col + MAX, None)
            else:
                # draw RANGE SHADOW
                stat_name = "_{}_".format(self.shadow_type.upper())
                x, y_mean, _ = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col + MEAN, None)
                x, y_stat, _ = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col + stat_name, None)

                if x is None or y_mean is None:
                    x = None
                    y = None
                    y2 = None
                else:
                    y = y_mean - y_stat
                    y2 = y_mean + y_stat

            self.plot_inner(ax, group_name, col, self.x_col, x_label, line_index, plot_index, x_values=x, y_values=y, 
                alpha=self.shadow_alpha, use_y_label=False, y2_values=y2)

        # DRAW NORMAL LINE
        err_col = col + "_{}_".format(self.error_bars.upper()) if self.error_bars else None
        x, y, err = self.get_xy_values(data_frames_by_cols, group_name, self.x_col, col, err_col)

        x_labels = None
        if self.x_labels_col:
            _, x_labels, _ = self.get_xy_values(data_frames_by_cols, group_name, None, self.x_labels_col, 
                None, force_floats=False)

            # update global that remembers longest value
            if self.x_values is None or len(x) > len(self.x_values):
                self.x_values = x
                self.x_labels = x_labels

        self.plot_inner(ax, group_name, col, self.x_col, x_label, line_index, plot_index, x_values=x, y_values=y, 
            alpha=self.alpha, use_y_label=True, err_values=err, x_labels=x_labels)
        
    def plot_inner(self, ax, group_name, col, x_col, x_label, line_index, plot_index, x_values, y_values, 
        alpha, use_y_label, y2_values=None, err_values=None, x_labels=None):

        import seaborn as sns
        from matplotlib.ticker import MaxNLocator

        if y_values is None or len(y_values) == 0:  
            # draw with dummy data to keep legend entries consistent and matching user specifed order
            alpha = 0
            if x_values:
                y_values = [0] * len(x_values)
            else:
                y_values = [0]

        if x_values is None:        
            x_values = range(len(y_values))
        else:
            ax.set_xlabel(x_label)

        if self.y_label and line_index == 0:
            ax.set_ylabel(self.y_label)

        if use_y_label:
            line_title = self.legend_titles[line_index % len(self.legend_titles)]

            if self.legend_suffix:
                line_title += self.legend_suffix

            line_title = self.fixup_text(line_title, group_name, col)

        else:
            line_title = None
            
        console.detail("x_values=", x_values)
        console.detail("y_values=", y_values)
        console.detail("y2_values=", y2_values)

        num_y_ticks = 10
        ax.get_yaxis().set_major_locator(MaxNLocator(num_y_ticks))
        #color = self.colors[line_index % len(self.colors)]

        cap_size = 5
        is_range_plot = bool(y2_values is not None)

        line_size = self.line_sizes[line_index % len(self.line_sizes)]

        # support for user mapping each plot line to different color indexes
        color_line_index = line_index
        if self.color_indexes:
            color_line_index = self.color_indexes[line_index % len(self.color_indexes)]
            
        color_index = color_line_index % len(self.colors)
        color = self.colors[color_index]

        # set line style
        if self.line_styles:
            line_style = self.line_styles[line_index % len(self.line_styles)]
        else:
            avail_line_styles = ["-", "--", "-.", ":"]
            style_index = color_line_index // 10
            style_index = style_index % len(avail_line_styles)
            line_style = avail_line_styles[style_index]

        # our default attributes
        kwargs = {"label": line_title, "color": color, "alpha": alpha, 
            "linewidth": line_size, "linestyle": line_style}
        
        if self.plot_type == "line" and err_values is not None:
            kwargs["capsize"] = cap_size

        # let user override
        if self.plot_args and not is_range_plot:

            for name, value in self.plot_args.items():
                value = utils.make_numeric_if_possible(value)
                kwargs[name] = value

        #cmap = self.get_seaborn_color_map("muted")
        if self.plot_type == "line":

            if is_range_plot:

                # RANGE plot
                ax.fill_between(x_values, y_values, y2_values, **kwargs)

            elif err_values is not None:

                # ERROR BAR plot
                trace = ax.errorbar(x_values, y_values, yerr=err_values, **kwargs)  
            else:

                # LINE plot
                ax.plot(x_values, y_values, **kwargs)

        elif self.plot_type == "bar":
            # SCATTER plot
            ax.bar(x_values, y_values, **kwargs)  

        elif self.plot_type == "scatter":
            # SCATTER plot
            ax.scatter(x_values, y_values, **kwargs)  

        elif self.plot_type == "histogram":
            # HISTOGRAM plot
            ax.hist(y_values, bins=self.bins, **kwargs)  

        else:
            errors.syntax_error("unknown plot type={}".format(self.plot_type))

        # this must be called AFTER plotting
        if self.plot_titles:
            # set the title of the subplot
            plot_title = self.plot_titles[plot_index % len(self.plot_titles)]

            plot_title = self.fixup_text(plot_title, group_name, col)
            ax.set_title(plot_title)

        if self.show_legend:
            if self.legend_args:
                # pass legend args to legend object
                ax.legend(**self.legend_args)
            else:
                ax.legend()

        if x_labels is not None:
            ax.set_xticks(x_values)
            ax.set_xticklabels(x_labels)

    def fixup_text(self, text, group_name, col):
        if text:
            group_info = self.group_info[group_name] if group_name else None

            if "$job" in text:
                job_name = group_info["job"]
                text = text.replace("$job", job_name)

            if "$run" in text:
                run_name = group_info["run"]
                text = text.replace("$run", run_name)

            if "$node" in text:
                node_name = group_info["node"]
                text = text.replace("$node", node_name)
            
            if "$experiment" in text:
                exper_name = group_info["experiment"]
                text = text.replace("$experiment", exper_name)
            
            if "$group" in text:
                text = text.replace("$group", group_name if group_name else "")

            if "$col" in text:
                text = text.replace("$col", col)

            if "@" in text:
                # look for a named column (@hparams.foo@) and replace it with its value
                parts = text.split("@")
                if len(parts) > 2:
                    # contains 1 or more @xxx@ entries
                    new_text = ""

                    while len(parts) >= 2:
                        left = parts.pop(0)
                        var_index = parts.pop(0)
                        col_name = self.legend_title_vars[int(var_index)]
                        
                        # update @N@ with value of arg   
                        if group_info and col_name in group_info:
                            value = group_info[col_name]
                        else:
                            _, value, _ = self.get_xy_values(self.data_frames_by_cols, group_name, x_col=None, y_col=col_name, 
                                stat_col=None, force_floats=False, force_value=True)

                            if isinstance(value, (tuple, list)):
                                value = value[0]
                        new_text += "{}{}".format(left, value)

                    new_text += parts.pop()
                    text = new_text

        return text

    def is_col_in_sets(self, metric_sets, col_name):
        found = False

        for ms in metric_sets:
            keys = ms["keys"]
            if col_name in keys:
                found = True
                break

        return found

    def get_actual_x_column(self, metric_sets, default_x_col, y_cols):
        '''
        x col search order:
            - specified in cmd line (explict_options, checked by caller)
            - specified as 'step_name" in logged metrics (matching y_cols)
            - specified as 'step_name" in first logged metrics (if no y_cols specified)
            - config file step_name property
            - guess from a list of commonly used named
        '''
        x_col = None
        first_y = y_cols[0] if y_cols else None

        for ms in metric_sets:
            keys = ms["keys"]
            if first_y and not first_y in keys:
                continue

            if constants.STEP_NAME in keys:
                records = ms["records"]
                x_col = records[0][constants.STEP_NAME]
            elif default_x_col:
                x_col = default_x_col
            else:
                # try guessing from common names (and __index__, sometimes added by XT)
                x_names = ["epoch", "step", "iter", "epochs", "steps", "iters", constants.INDEX]
                for xn in x_names:
                    if xn in keys:
                        x_col = xn
                    break

            # only look in first metric set 
            break

        return x_col

    def get_default_y_columns(self, metric_sets, x_col):
        y_cols = []

        for ms in metric_sets:
            keys = ms["keys"]
            omits = [x_col, constants.STEP_NAME, constants.TIME]

            for key in keys:
                if not key in omits:
                    y_cols.append(key)

            # only look in first metric set 
            break

        return y_cols

# flat functions
def make_floats(values):
    reg_values = list(values)
    if isinstance(reg_values[0], str):
        values = np.array(range(len(values)))
    else:
        values = values.to_numpy(dtype=float)
    return values
