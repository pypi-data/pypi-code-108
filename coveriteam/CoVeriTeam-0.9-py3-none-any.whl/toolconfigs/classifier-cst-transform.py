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
        return "A classifier based on CST Transform"

    def executable(self, tool_locator):
        return tool_locator.find_executable("run_selector.py")

    def version(self, executable):
        return self._version_from_tool(executable)

    def cmdline(self, executable, options, task, rlimits):
        # Not using the program file.
        return [executable] + options

    def determine_result(self, run):
        """
        The tool produces target label and confidence.
        """
        if run.output:
            label = run.output[-2].strip().split()[-1]
            confidence = run.output[-1].strip().split()[-1]
            return label, confidence
        return None
