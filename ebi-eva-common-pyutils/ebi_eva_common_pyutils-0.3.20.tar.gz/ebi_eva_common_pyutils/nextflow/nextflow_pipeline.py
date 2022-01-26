# Copyright 2021 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Rationale for a Nextflow pipeline abstraction
# ---------------------------------------------
# Dynamic pipeline generation
# Abstraction to represent process dependencies
# Unit testability of individual steps without scattering logic between Python and Nextflow
# Ability to combine pipelines

import networkx as nx
import os
from typing import List, Dict, Union

from ebi_eva_common_pyutils.logger import AppLogger
from ebi_eva_common_pyutils.command_utils import run_command_with_output


class NextFlowProcess:

    def __init__(self, process_name: str, command_to_run: str, process_directives: Dict[str, str] = None) -> None:
        """
        Create a Nextflow process
        :rtype: None
        :param process_name: Name of the process - should be a valid identifier - ex: p1_merge
        :type process_name: str
        :param command_to_run: Command to be run - ex: bash -c "echo p1"
        :type command_to_run: str
        :param process_directives: Additional process directives - ex: {"memory": "4GB", "executor": "lsf"}
        :type process_directives: dict
        """
        if not process_name.isidentifier():
            raise ValueError(f"{process_name} is not a valid Nextflow process name")
        self.process_name = process_name
        self.success_flag = f"{self.process_name}_success"
        self.command_to_run = command_to_run
        self.process_directives = process_directives if process_directives else dict()


class NextFlowPipeline(AppLogger):
    def __init__(self, process_dependency_map: Dict[NextFlowProcess, List[NextFlowProcess]] = None) -> None:
        """
        Create a Nextflow pipeline with a process dependency map

        :param process_dependency_map: Map of Nextflow processes and their corresponding dependencies
        - ex: {p3 : [p2], p2: [p1]}  where p1, p2 and p3 are Nextflow processes that should be executed sequentially
        """
        # Modeling the dependency map as a DiGraph (Directed graph) is advantageous
        # in ordering/combining flows and detecting cycles
        self.process_dependency_map = nx.ordered.DiGraph()
        if process_dependency_map:
            self.add_dependencies(process_dependency_map)

    def add_dependencies(self, process_dependency_map: Dict[NextFlowProcess, List[NextFlowProcess]]):
        for process, dependencies in process_dependency_map.items():
            if dependencies:
                for dependency in dependencies:
                    self.add_process_dependency(process, dependency)
            else:
                self.add_process_dependency(process, None)

    def add_process_dependency(self, process: NextFlowProcess, dependency: Union[NextFlowProcess, None]):
        if dependency:
            self.process_dependency_map.add_edge(process, dependency)
            if not nx.dag.is_directed_acyclic_graph(self.process_dependency_map):
                raise ValueError(f"Cycles found in pipeline when adding process {process.process_name} "
                                 f"and its dependency {dependency.process_name}")
        else:
            # If no dependency is specified, the process will just be a single node in the DAG
            self.process_dependency_map.add_node(process)

    def _write_to_pipeline_file(self, workflow_file_path: str):
        with open(workflow_file_path, "a") as pipeline_file_handle:
            pipeline_file_handle.write(self.__str__() + "\n")

    def run_pipeline(self, workflow_file_path: str, nextflow_binary_path: str = 'nextflow',
                     nextflow_config_path: str = None, working_dir: str = ".", resume: bool = False,
                     other_args: dict = None):
        # Remove pipeline file if it already exists
        if os.path.exists(workflow_file_path):
            os.remove(workflow_file_path)
        self._write_to_pipeline_file(workflow_file_path)
        workflow_command = f"cd {working_dir} && {nextflow_binary_path} run {workflow_file_path}"
        workflow_command += f" -c {nextflow_config_path}" if nextflow_config_path else ""
        workflow_command += f" -with-report {workflow_file_path}.report.html"
        workflow_command += f" -with-dag {workflow_file_path}.dag.png"
        workflow_command += " -resume" if resume else ""
        workflow_command += " ".join([f" -{arg} {val}" for arg, val in other_args.items()]) if other_args else ""
        run_command_with_output(f"Running pipeline {workflow_file_path}...", workflow_command)

    @staticmethod
    def join_pipelines(main_pipeline: 'NextFlowPipeline', dependent_pipeline: 'NextFlowPipeline') -> 'NextFlowPipeline':
        """
        Join two pipelines.

        Returns a new pipeline where:
            1) root processes are those of the main pipeline.
            2) final processes are those of the dependent pipeline and
            3) every root process of the dependent pipeline depends on the final processes of the main pipeline.
        """
        joined_pipeline = NextFlowPipeline()
        # Aggregate dependency maps of both pipelines
        joined_pipeline.process_dependency_map = nx.compose(main_pipeline.process_dependency_map,
                                                            dependent_pipeline.process_dependency_map)
        for final_process_in_main_pipeline in main_pipeline._get_final_processes():
            for root_process_in_dependent_pipeline in dependent_pipeline._get_root_processes():
                joined_pipeline.add_process_dependency(root_process_in_dependent_pipeline,
                                                       final_process_in_main_pipeline)
        return joined_pipeline

    def _get_root_processes(self) -> List[NextFlowProcess]:
        # Root processes are those which have no dependencies
        # See https://stackoverflow.com/a/62948641
        roots = []
        for component in nx.weakly_connected_components(self.process_dependency_map):
            subgraph = self.process_dependency_map.subgraph(component)
            roots.extend([n for n, d in subgraph.out_degree() if d == 0])
        return roots

    def _get_final_processes(self) -> List[NextFlowProcess]:
        # Final processes are those which have no other processes depending on them
        # See https://stackoverflow.com/a/62948641
        roots = []
        for component in nx.weakly_connected_components(self.process_dependency_map):
            subgraph = self.process_dependency_map.subgraph(component)
            roots.extend([n for n, d in subgraph.in_degree() if d == 0])
        return roots

    @staticmethod
    def _get_process_repr(process: NextFlowProcess, dependencies: List[NextFlowProcess]) -> str:
        process_directives_str = "\n".join([f"{key}='{value}'" for key, value in process.process_directives.items()])
        input_dependencies = "val flag from true"
        if dependencies:
            input_dependencies = "\n".join([f"val {dependency.success_flag} from {dependency.success_flag}"
                                            for dependency in dependencies])
        return "\n".join(map(str.strip, f"""
                    process {process.process_name} {{
                    {process_directives_str}
                    input:
                    {input_dependencies}
                    output:
                    val true into {process.success_flag}
                    script:
                    \"\"\"
                    {process.command_to_run}
                    \"\"\"
                    }}""".split("\n")))

    def __str__(self):
        # Order the list of nodes based on the dependency
        # See https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.depth_first_search.dfs_postorder_nodes.html?highlight=dfs_postorder_nodes#networkx.algorithms.traversal.depth_first_search.dfs_postorder_nodes
        ordered_list_of_processes_to_run = list(nx.dfs_postorder_nodes(self.process_dependency_map))
        # Get a Nextflow pipeline representation of each process and its dependencies
        return "\n\n".join([NextFlowPipeline._get_process_repr(process, list(self.process_dependency_map[process]))
                            for process in ordered_list_of_processes_to_run])


class LinearNextFlowPipeline(NextFlowPipeline):
    """
    Simple linear pipeline that supports resumption
    """
    previous_process: NextFlowProcess = None

    def __init__(self, process_list: List[NextFlowProcess] = None):
        dependency_map = {}
        if process_list:
            for index, process in enumerate(process_list):
                dependency_map[process] = [] if index == 0 else [process_list[index - 1]]
        super().__init__(dependency_map)

    def add_process(self, process_name, command_to_run):
        current_process = NextFlowProcess(process_name=process_name, command_to_run=command_to_run)
        self._add_new_process(current_process)

    def _add_new_process(self, current_process):
        super().add_process_dependency(current_process, self.previous_process)
        self.previous_process = current_process
