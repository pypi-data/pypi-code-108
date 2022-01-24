# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper for file objects to ensure flushing."""
from typing import Any, cast, Optional, TextIO
import os
from azureml.core import Run


class ConsoleWriter:
    """Wrapper for file objects to ensure flushing."""

    def __init__(self, f: Optional[TextIO] = None, show_output: bool = True) -> None:
        """
        Construct a ConsoleWriter.

        :param f: the underlying file stream
        :return:
        """
        if f is None:
            import atexit

            devnull = open(os.devnull, "w", encoding="utf-8")
            atexit.register(devnull.close)
            self._file = devnull  # type: TextIO
        else:
            self._file = f

        self.show_output = show_output

    def print(self, text: str, carriage_return: bool = False) -> None:
        """
        Write to the underlying file. The file is flushed.

        :param text: the text to write
        :param carriage_return: Add the carriage return.
        :return:
        """
        if carriage_return:
            self.write(text + "\r")
        else:
            self.write(text)
        self.flush()

    def println(self, text: Optional[str] = None) -> None:
        """
        Write to the underlying file. A newline character is also written and the file is flushed.

        If the text provided is None, just a new line character will be written.

        :param text: the text to write
        :return:
        """
        if text is not None:
            self.write(text)
        self.write("\n")
        self.flush()

    def write(self, text: str) -> None:
        """
        Write directly to the underlying file.

        :param text: the text to write
        :return:
        """
        if self.show_output:
            self._file.write(text)

    def flush(self) -> None:
        """
        Flush the underlying file.

        :return:
        """
        self._file.flush()

    def print_run_info(self, run: Run) -> None:
        """
        Print the run id and a link to azure portal. For ipython contexts, format it via html.

        :param run: The run to print.
        :return: None
        """

        try:
            # If running in a terminal, display() prints <IPython.core.display.HTML object>
            # We only want to run this code in ipython environments, which contain a global variable 'get_ipython'
            get_ipython  # type: ignore
            from IPython.core.display import display, HTML
            display(HTML(run._repr_html_()))
        except (NameError, ImportError):
            # TODO: do we just want to catch generic Exception to be safe?
            self.println("Parent Run ID: " + cast(str, run.id))
            self.println(cast(str, run.get_portal_url()))
