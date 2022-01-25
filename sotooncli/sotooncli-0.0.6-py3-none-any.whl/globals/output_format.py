import json

import click
import yaml
from tabulate import tabulate

from sotooncli.core.param import SotoonParams


class OutputFormatOption(click.Option, SotoonParams):
    RAW_JSON_OUTPUT_FORMAT = "json-raw"
    FORMATTED_JSON_OUTPUT_FORMAT = "json"
    TABULAR_OUTPUT_FORMAT = "table"
    YAML_OUTPUT_FORMAT = "yaml"
    output_types = [
        FORMATTED_JSON_OUTPUT_FORMAT,
        RAW_JSON_OUTPUT_FORMAT,
        TABULAR_OUTPUT_FORMAT,
        YAML_OUTPUT_FORMAT,
    ]

    def __init__(self, default=output_types[0]):
        type_ = click.Choice(self.output_types)
        click.Option.__init__(self, ["-o", "--output"], show_default=True, type=type_)
        SotoonParams.__init__(
            self,
            name="output",
            placeholder="OUTPUT",
            is_required=False,
            description=f"Output format. One of {self.output_types}.",
            default_value=default,
        )

    @staticmethod
    def get_formatter(output_format):
        if output_format == OutputFormatOption.RAW_JSON_OUTPUT_FORMAT:
            return JSONFormatter()
        elif output_format == OutputFormatOption.TABULAR_OUTPUT_FORMAT:
            return TableFormatter()
        elif output_format == OutputFormatOption.FORMATTED_JSON_OUTPUT_FORMAT:
            return PrettyJSONFormatter()
        elif output_format == OutputFormatOption.YAML_OUTPUT_FORMAT:
            return YamlFormatter()
        else:
            raise click.BadParameter("Unknown output format")


class OutputFormatter:
    def format(self, data):
        raise NotImplementedError


class JSONFormatter(OutputFormatter):
    def format(self, data):
        return data


class PrettyJSONFormatter(OutputFormatter):
    INDENT = 4

    def format(self, data):
        return json.dumps(data, indent=self.INDENT, sort_keys=True)


class TableFormatter(OutputFormatter):
    def format(self, data):
        try:
            return tabulate(data, headers="keys", tablefmt="pretty")
        except TypeError:
            return tabulate([data], headers="keys", tablefmt="pretty")


class YamlFormatter(OutputFormatter):
    def format(self, data):
        data_ = yaml.dump(data, default_flow_style=False)
        return data_
