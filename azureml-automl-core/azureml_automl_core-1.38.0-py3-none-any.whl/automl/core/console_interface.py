# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""
from typing import Optional, Union, TextIO, List, Any, Dict, Tuple
import json
import os
import sys
from collections import OrderedDict
import logging
import pkg_resources
from .console_writer import ConsoleWriter
from azureml.automl.core.shared import logging_utilities

WIDTH_ITERATION = 5
WIDTH_PIPELINE = 48
WIDTH_SAMPLING = 13
WIDTH_DURATION = 16
WIDTH_METRIC = 10
WIDTH_BEST = 10

PACKAGE_NAME = 'azureml.automl.core'
DEFAULT_GUARDRAIL_SCHEMA_VERSION = '1.0.0'

logger = logging.getLogger(__name__)


class Column:
    """Constants for column names."""

    ITERATION = 'ITER'
    PIPELINE = 'PIPELINE'
    SAMPLING = 'SAMPLING %'
    DURATION = 'DURATION'
    METRIC = 'METRIC'
    BEST = 'BEST'


class Guardrails:
    """Constants for guardrail names."""

    TYPE = "TYPE:"
    STATUS = "STATUS:"
    DESCRIPTION = "DESCRIPTION:"
    PARAMETERS = "DETAILS:"
    TYPE_TD = "friendly_type"
    STATUS_TD = "result"
    DESC_TD = "friendly_result"
    LEARN_MORE_TD = "friendly_learn_more"
    PARAM_PREFACE_TD = "friendly_parameter_preface"
    PARAM_TD = "friendly_parameters"
    TITLE_SPACE = len(DESCRIPTION) + 2


class ConsoleInterface:
    """Class responsible for printing iteration information to console."""

    def __init__(self, metric: str, console_writer: ConsoleWriter, mask_sampling: bool = False) -> None:
        """
        Initialize the object.

        :param metric: str representing which metric is being used to score the pipeline.
        :param console_writer: file-like object to output to. If not provided, output will be discarded.
        :param mask_sampling: bool decide whether the sample columns should be masked or not.
        """
        self.metric = metric
        self.metric_pretty = metric
        self.mask_sampling = mask_sampling

        self.console_writer = console_writer

        self.columns = [
            Column.ITERATION,
            Column.PIPELINE,
            Column.SAMPLING,
            Column.DURATION,
            Column.METRIC,
            Column.BEST,
        ]

        self.descriptions = [
            'The iteration being evaluated.',
            'A summary description of the pipeline being evaluated.',
            'Percent of the training data to sample.',
            'Time taken for the current iteration.',  # 'Error or warning message for the current iteration.',
            'The result of computing %s on the fitted pipeline.' % (self.metric_pretty,),
            'The best observed %s thus far.' % self.metric_pretty,
        ]

        self.widths = [
            WIDTH_ITERATION,
            WIDTH_PIPELINE,
            WIDTH_SAMPLING,
            WIDTH_DURATION,
            WIDTH_METRIC,
            WIDTH_BEST
        ]

        if mask_sampling:
            del self.columns[2]
            del self.descriptions[2]
            del self.widths[2]

        self.sep_width = 3
        self.filler = ' '
        self.total_width = sum(self.widths) + self.sep_width

    def _format_float(self, v: Optional[Union[float, str]]) -> Optional[str]:
        """
        Format float as a string.

        :param v:
        :return:
        """
        if isinstance(v, float):
            return '{:.4f}'.format(v)
        return v

    def _format_int(self, v: Union[int, str]) -> str:
        """
        Format int as a string.

        :param v:
        :return:
        """
        if isinstance(v, int):
            return '%d' % v
        return v

    def _handle_console_interface_exception(self,
                                            console_msg: str,
                                            logger_msg: str,
                                            e: Exception) -> None:
        try:
            self.console_writer.println(console_msg)
        except Exception:
            pass
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.warning(logger_msg)

    def print_descriptions(self) -> None:
        """
        Print description of AutoML console output.

        :return:
        """
        try:
            self.console_writer.println()
            self.print_section_separator()
            for column, description in zip(self.columns, self.descriptions):
                self.console_writer.println(column + ': ' + description)
            self.print_section_separator()
            self.console_writer.println()
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print description due to internal error: {}.".format(e),
                "print_descriptions failed.", e)

    def print_columns(self) -> None:
        """
        Print column headers for AutoML printing block.

        :return:
        """
        try:
            self.print_start(Column.ITERATION)
            self.print_pipeline(Column.PIPELINE, '', Column.SAMPLING)
            self.print_end(Column.DURATION, Column.METRIC, Column.BEST)
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print column headers due to internal error: {}.".format(e),
                "print_columns failed.", e)

    def _print_guardrail_parameters(self,
                                    parameters: List[Any] = [],
                                    print_limit: int = sys.maxsize) -> None:
        if len(parameters) == 0 or print_limit == 0:
            return

        min_space = self.total_width // 3

        self.console_writer.println(self._get_format_param_table_str(
            min_cell_width=min_space, cell_separator="|", table_cross_sign="+", header_separator="=",
            line_separator="-", list_of_parameter_dicts=parameters, number_of_params_output=print_limit
        ))

    def print_guardrails(self,
                         faults: List[Any],
                         include_parameters: bool = True,
                         number_parameters_output: int = sys.maxsize,
                         schema_version: Optional[str] = None) -> None:
        """
        Print guardrail information if any exists.
        :return:
        """
        try:
            if not faults or len(faults) == 0:
                return
            self.console_writer.println()
            self.print_section_separator()
            if include_parameters and number_parameters_output == sys.maxsize:
                self.console_writer.println("DATA GUARDRAILS: ")
            else:
                self.console_writer.println("DATA GUARDRAILS SUMMARY:")
                self.console_writer.println("For more details, use API: run.get_guardrails()")

            sorted_schema = sorted(
                self._get_guardrail_schema(schema_version), key=lambda x: x["print_order"])

            for f in faults:
                self.console_writer.println()
                for schema_item in sorted_schema:
                    guardrail_type_name, print_prefix, print_content = self._get_print_params(f, schema_item)
                    if guardrail_type_name != Guardrails.PARAM_PREFACE_TD and guardrail_type_name in f:
                        self.console_writer.println(
                            self._get_guardrail_item_str(print_prefix, print_content, Guardrails.TITLE_SPACE))
                    elif guardrail_type_name == Guardrails.PARAM_PREFACE_TD:
                        if include_parameters and len(f[Guardrails.PARAM_TD]) > 0 and number_parameters_output > 0:
                            self.console_writer.println(
                                self._get_guardrail_item_str(
                                    print_prefix, print_content, Guardrails.TITLE_SPACE))
                            self._print_guardrail_parameters(f[Guardrails.PARAM_TD], number_parameters_output)
                self.console_writer.println('\n' + ('*' * self.total_width))
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print guardrail results due to internal error: {}.".format(e),
                "print_guardrailse failed.", e)

    def _get_guardrail_schema(self, schema_version: Optional[str]) -> Any:
        """
        Get the guardrail schema.

        :param schema_version: The schema version.
        """
        verifier_schema_json = pkg_resources.resource_filename(PACKAGE_NAME, 'verifier_schema.json')
        with open(verifier_schema_json, 'r') as f:
            verifier_schema = json.load(f)
        if schema_version is None or verifier_schema.get(schema_version) is None:
            version = DEFAULT_GUARDRAIL_SCHEMA_VERSION
        else:
            version = schema_version
        schema = verifier_schema.get(version)

        return schema

    def _get_print_params(self, fault: Any, schema_item: Any) -> Tuple[str, str, str]:
        """
        Get all the parameters used for print as a tuple of guardrail_type_name, print_header, print_content.

        :param fault: A dict of one fault.
        :param schema_item: An item in the schema list.
        """
        guardrail_type_name = schema_item["name"]
        print_prefix = schema_item.get("print_prefix", "")
        is_upper = schema_item["is_upper"]
        print_content = str(fault.get(guardrail_type_name, ''))
        if is_upper:
            print_content = print_content.upper()
        return guardrail_type_name, print_prefix, print_content

    def _get_guardrail_item_str(self, print_prefix: str, print_content: str, title_space: int) -> str:
        """
        Get the guardrail item str in the format `{print_prefix}   {print_content}` where the character+space
        before the `print_content` is the title_space.

        :param print_prefix: The prefix.
        :param print_content: The content.
        :param title_space: total white space.
        """
        return print_prefix + " " * (title_space - len(print_prefix)) + print_content

    def print_start(self, iteration: Union[int, str] = '') -> None:
        """
        Print iteration number.

        :param iteration:
        :return:
        """
        try:
            iteration = self._format_int(iteration)

            s = iteration.rjust(self.widths[0], self.filler)[-self.widths[0]:] + self.filler * self.sep_width
            self.console_writer.print(s)
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print iteration number due to internal error: {}.".format(e),
                "print_start failed.", e)

    def print_pipeline(self, preprocessor: Optional[str] = '',
                       model_name: Optional[str] = '', train_frac: Union[str, float] = 1) -> None:
        """
        Format a sklearn Pipeline string to be readable.

        :param preprocessor: string of preprocessor name
        :param model_name: string of model name
        :param train_frac: float of fraction of train data to use
        :return:
        """
        try:
            separator = ' '
            if preprocessor is None:
                preprocessor = ''
                separator = ''
            if model_name is None:
                model_name = ''
            combined = preprocessor + separator + model_name
            self.console_writer.print(combined.ljust(self.widths[1], self.filler)[:(self.widths[1] - 1)])

            if not self.mask_sampling:
                try:
                    train_frac = float(train_frac)
                except ValueError:
                    pass
                sampling_percent = None  # type: Optional[Union[str,float]]
                sampling_percent = train_frac if isinstance(train_frac, str) else train_frac * 100
                sampling_percent = str(self._format_float(sampling_percent))
                self.console_writer.print(sampling_percent.ljust(self.widths[2], self.filler)[:(self.widths[2] - 1)])
            self.console_writer.flush()
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print pipeline details due to internal error: {}.".format(e),
                "print_pipeline failed.", e)

    def print_end(self, duration: Union[float, str] = "", metric: Union[float, str] = "",
                  best_metric: Optional[Union[float, str]] = "") -> None:
        """
        Print iteration status, metric, and running best metric.

        :param duration: Status of the given iteration
        :param metric: Score for this iteration
        :param best_metric: Best score so far
        :return:
        """
        try:
            if best_metric is None:
                best_metric = ""
            metric_float, best_metric = tuple(map(self._format_float, (metric, best_metric)))
            duration, metric_float, best_metric = tuple(map(str, (duration, metric_float, best_metric)))

            i = 2 if self.mask_sampling else 3
            s = duration[:self.widths[i]].ljust(self.widths[i], self.filler)
            s += metric_float.rjust(self.widths[i + 1], self.filler)
            s += best_metric.rjust(self.widths[i + 2], self.filler)
            self.console_writer.println(s)
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print iteration results due to internal error: {}.".format(e),
                "print_end failed.", e)

    def print_error(self, message: Union[BaseException, str]) -> None:
        """
        Print an error message to the console.

        :param message: Error message to display to user
        :return:
        """
        try:
            self.console_writer.print('ERROR: ')
            self.console_writer.println(str(message).ljust(self.widths[1], self.filler))
        except Exception as e:
            self._handle_console_interface_exception(
                "Could not print error details due to internal error: {}.".format(e),
                "print_error failed.", e)

    def print_line(self, message: str) -> None:
        """Print a message (and then a newline) on the console."""
        self.console_writer.println(message)

    def print_section_separator(self) -> None:
        """Print the separator for different sections during training on the console."""
        self.console_writer.println('*' * self.total_width)

    def _get_format_param_table_str(
            self,
            min_cell_width: int,
            cell_separator: str,
            table_cross_sign: str,
            header_separator: str,
            line_separator: str,
            list_of_parameter_dicts: List[Any],
            number_of_params_output: Optional[int] = None
    ) -> str:
        """
        Build a table from a list of parameter dicts. The parameter names are table headers and the values are the
        cell contents.

        :param min_cell_width: The minimum cell width in case any cell is too short.
        :param cell_separator: The cell separator sign.
        :param table_cross_sign: The table cross sign.
        :param header_separator: The header separate sign.
        :param line_separator: The general line separator.
        :param list_of_parameter_dicts: A list of parameter dicts as the table contents.
        :param number_of_params_output: The number of parameter to be printed.
        :return: The parameters in the formatted table string.
        """
        if number_of_params_output is None:
            number_of_params_output = sys.maxsize
        if len(list_of_parameter_dicts) == 0 or number_of_params_output <= 0:
            return ''
        parameter_space_dict = self._get_parameter_space_dict(min_cell_width, list_of_parameter_dicts)
        # Build header str.
        output_lines = [
            self._get_horizontal_separate_line_str(table_cross_sign, line_separator, parameter_space_dict),
            self._get_table_format_header_str(parameter_space_dict, cell_separator),
            self._get_horizontal_separate_line_str(table_cross_sign, header_separator, parameter_space_dict)]
        # BUild content str.
        print_counter = 0
        for fault_parameters in list_of_parameter_dicts:
            output_lines.append(
                self._get_format_parameter_content_str(parameter_space_dict, cell_separator, fault_parameters))
            print_counter += 1
            if print_counter >= number_of_params_output:
                break
        output_lines.append(self._get_horizontal_separate_line_str(
            table_cross_sign, line_separator, parameter_space_dict))
        return "\n".join(output_lines)

    def _get_table_format_header_str(self, parameter_space_dict: Dict[str, int], separator: str) -> str:
        """
        Get the table format header.

        :param parameter_space_dict: A dict mapping each parameters to the expected width.
        :param separator: Cell separator.
        :return: The str represents the table header.
        """
        tab_contents = []
        for parameter, space in parameter_space_dict.items():
            tab_contents.append(self._get_cell_content(space, parameter))
        return self._build_table_format_row_str(separator, separator.join(tab_contents))

    def _get_format_parameter_content_str(
            self,
            parameter_space_dict: Dict[str, int],
            separator: str,
            fault_parameter: Any
    ) -> str:
        """
        Get the formatted table content line.

        :param parameter_space_dict: A dict mapping each parameters to the expected width.
        :param separator: Cell separator.
        :return: The str represents the table header.
        """
        tab_contents = []
        for parameter, cell_width in parameter_space_dict.items():
            tab_contents.append(self._get_cell_content(cell_width, fault_parameter.get(parameter)))
        return self._build_table_format_row_str(separator, separator.join(tab_contents))

    def _get_horizontal_separate_line_str(
            self,
            cross_sign: str,
            line_separator: str,
            parameter_space_dict: Dict[str, int]
    ) -> str:
        """
        Get the horizontal separate line.

        :param cross_sign: The cross sign.
        :param line_separator: The line separator sign.
        :param parameter_space_dict: The dict contains each cell size.
        :return: string representation of a separate line.
        """
        return self._build_table_format_row_str(
            cross_sign, cross_sign.join([line_separator * width for width in parameter_space_dict.values()]))

    def _get_parameter_space_dict(
            self,
            min_cell_width: int,
            list_of_parameter_dicts: List[Any]
    ) -> Dict[str, int]:
        """
        Get the dict that each parameter maps to.

        :param min_cell_width: The minimum cell width in case any cell is too short.
        :param list_of_parameter_dicts: A list of parameter dicts as the table contents.
        :return: A dict mapping each parameters to the width.
        """
        parameter_space_dict = OrderedDict()
        for parameter in list_of_parameter_dicts:
            for parameter_name in parameter.keys():
                if parameter_name not in parameter_space_dict:
                    parameter_space_dict[parameter_name] = max(min_cell_width, len(parameter_name))
        return parameter_space_dict

    def _get_cell_content(self, max_cell_width: int, original_content: Optional[Any] = None) -> str:
        """
        Get the table cell content with max cell width if the desired content has more characters than the
        max_cell_width, it will print as ...

        :param max_cell_width: Max cell width allowed.
        :param original_content: the original content.
        """
        content = str(original_content) if original_content else ""
        if len(content) <= max_cell_width:
            return content + " " * (max_cell_width - len(content))
        elif max_cell_width < 3:
            return "." * max_cell_width
        else:
            return content[:max_cell_width - 3] + "..."

    def _build_table_format_row_str(self, separator: str, cell_content: str) -> str:
        """
        Build the table format line.

        :param separator: The separator sign.
        :param cell_content: The content in the cell.
        :return: The formatted table line.
        """
        return "{0}{1}{0}".format(separator, cell_content)
