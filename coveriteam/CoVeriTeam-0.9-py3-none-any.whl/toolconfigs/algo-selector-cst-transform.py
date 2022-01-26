# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0


import benchexec.tools.template


class Tool(benchexec.tools.template.BaseTool2):
    """
    This tool selects a verification tool for a c program.
    url: https://github.com/cedricrupb/cst_transform
    """

    def name(self):
        return "Algorithm (Verifier) Selector based on CST Transform"

    def executable(self, tool_locator):
        return tool_locator.find_executable("run_selector.py")

    def version(self, executable):
        return self._version_from_tool(executable)

    def cmdline(self, executable, options, task, rlimits):
        # Not using the program file.
        return [executable] + options + [task.single_input_file]

    def determine_result(self, run):
        """
        The label of the selected tool is output in the last line.
        """
        selected_verifier = None
        # Note: this is abuse of this function, but it works.
        # TODO put try catch
        if run.output:
            selected_verifier = run.output[-1].strip().split()[-1]
        return selected_verifier if selected_verifier else "cpa-seq"
