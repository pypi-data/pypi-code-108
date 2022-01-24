from benvy.databricks.notebook.CommandsConverter import CommandsConverter


class NotebookConverter:

    first_line = "# Databricks notebook source"
    cell_separator = "# COMMAND ----------"

    def __init__(
        self,
        commands_converter: CommandsConverter,
    ):
        self.__commands_converter = commands_converter

    def from_dbc_notebook(self, content: dict) -> str:
        return self.__commands_converter.convert(content["commands"], self.first_line, self.cell_separator)
