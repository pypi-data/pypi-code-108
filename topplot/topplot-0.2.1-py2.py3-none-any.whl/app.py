# pylint: disable=no-member

import os
import re
from typing import Callable

from .config import Config
from .dataframes import Dataframes
from .graphs import Grapher
from .parser import Parser
from .progress_window import ProgressWindow
from .toptype import TopType
from .graphmap import GraphMap, GraphMapEntry
from .utils import info

# ------------------------------------------------------------------------------


class App:
    def __init__(self, version):
        self.config = Config(self, version)

        self.setup_profiling()

        self.progress_window = (
            None
            if self.config.list_processes or not self.config.do_graph
            else ProgressWindow()
        )

    # --------------------------------------------------------------------------

    def update_status(self, msg):
        if self.config.verbosity > 0:
            print(f"status: {msg}")
        if self.progress_window is not None:
            self.progress_window.update_status(msg)

    # --------------------------------------------------------------------------

    def setup_profiling(self):
        try:
            # pylint: disable=import-outside-toplevel,unused-import
            from .profiler import Profiler
        except ImportError:
            # No profiler available, convert calls to empty stubs
            class DummyProfiler:
                def start(self, *args, **kwargs):
                    pass

                def start_new(self, *args, **kwargs):
                    pass

                def stop(self, *args, **kwargs):
                    pass

            self.profiler = DummyProfiler()
        else:
            tag1 = re.sub(  # strip everything after last '.'
                r"\.[^\.]+$", "", os.path.basename(self.config.toplog_filename)
            )

            if self.config.which_graphs is not None:
                tag1 = f"{tag1}_{self.config.which_graphs}"

            self.profiler = Profiler(
                self.config.profiling_tag is not None,
                tag1=tag1,
                tag2=self.config.profiling_tag,
            )

    # --------------------------------------------------------------------------

    def produce_graphs(
        self, dataframes: Dataframes, at_showtime: Callable, at_close: Callable
    ):
        self.update_status("producing graphs")

        cpus_graph_title = "cpu data"
        tasks_graph_title = "task data"
        poi_graph_title = f"processes of interest\n{self.config.poi_categories}"
        mem_graph_title = "mem data"

        # Awkward initialization sequence to allow graph_map to reference grapher functions
        graph_map = GraphMap()

        graphs = Grapher(
            graph_map,
            self.config,
            dataframes,
            self.config.mem_unit,
            self.config.mem_cached_or_available,
            self.progress_window,
        )

        tasks_graph = graphs.graph_procps_tasks
        if self.config.toptype == TopType.BUSYBOX:
            tasks_graph = graphs.graph_busybox_tasks

        # Note: Order here determines display order in overview figure
        graph_map[poi_graph_title] = GraphMapEntry(graphs.graph_poi, dataframes.poi_df)
        graph_map[cpus_graph_title] = GraphMapEntry(
            graphs.graph_cpus, dataframes.cpus_df
        )
        graph_map[mem_graph_title] = GraphMapEntry(graphs.graph_mem, dataframes.mem_df)
        graph_map[tasks_graph_title] = GraphMapEntry(tasks_graph, dataframes.tasks_df)

        graphs.doit(at_showtime, at_close)

    # --------------------------------------------------------------------------

    def run(self):
        self.update_status(f"parsing '{os.path.basename(self.config.toplog_filename)}'")
        self.profiler.start("parse")
        parser = Parser(self.config)
        parser.parse()

        if self.config.list_processes:
            parser.list_processes()
            self.progress_window.hide()
            self.profiler.stop()
            return

        self.update_status("munging")
        parser.munge_to_files()

        if parser.get_poi_count() < 1:
            info(
                "INFO: No processes of interest according to selection criteria:"
                f" {self.config.poi_categories}"
            )
            if self.progress_window:
                self.progress_window.hide()
            self.profiler.stop()
            return

        if self.config.do_graph:
            self.update_status("prepping dataframes")
            dataframes = parser.dataframes_from_files()
            self.profiler.start_new("graph")
            self.produce_graphs(
                dataframes, self.progress_window.hide, self.progress_window.destroy
            )

        self.profiler.stop()


# ------------------------------------------------------------------------------
# vi: sw=4:ts=4:et:tw=0
