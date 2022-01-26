#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause-Clear
# Copyright (c) 2019, The Numerical Algorithms Group, Ltd. All rights reserved.

from ipywidgets import Tab, Layout, VBox, Text
from ipysheet.sheet import Sheet


class TraceEditor(VBox):
    """Spreadsheet-like interface for capturing metrics by manual input
    """

    def __init__(self, trace, *args, **kwargs):
        """
        Parameters
        ----------
        """
        super().__init__(*args, **kwargs)

        self._trace = trace

        self._column_names = self._trace.all_statistics()

        self._controls = self._create_controls()
        self._sheet = Sheet()

        self.children = [self._controls, self._sheet]

    def _create_controls(self):
        return VBox()
