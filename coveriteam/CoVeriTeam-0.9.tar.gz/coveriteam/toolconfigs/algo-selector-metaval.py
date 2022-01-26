# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0


import benchexec.tools.template


class Tool(benchexec.tools.template.BaseTool2):
    """
    This tool selects the verifier backend for MetaVal based on the specification.
    url: https://gitlab.com/sosy-lab/software/metaval
    """

    def name(self):
        return "Algorithm (Verifier) Selector for MetaVal"

    def executable(self, tool_locator):
        return tool_locator.find_executable("metaval-algo-selector.sh")

    def version(self, executable):
        return self._version_from_tool(executable)

    def cmdline(self, executable, options, task, rlimits):
        # Not using the program file.
        return [executable] + options + ["--spec"] + [task.property_file or "None"]

    def determine_result(self, run):
        """
        The label of the selected tool is output in the first line.
        """
        selected_verifier = None
        # Note: this is abuse of this function, but it works.
        if run.output:
            selected_verifier = run.output[0].rstrip()
        return selected_verifier if selected_verifier else "cpa-seq"
