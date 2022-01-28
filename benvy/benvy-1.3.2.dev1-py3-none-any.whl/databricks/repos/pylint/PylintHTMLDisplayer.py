import os
import IPython
from typing import List, Dict
from benvy.databricks.DatabricksContext import DatabricksContext


class PylintHTMLDisplayer:
    def __init__(
        self,
        databricks_context: DatabricksContext,
    ):
        self.__databricks_context = databricks_context

    def display(self, enhanced_pylint_results: List[Dict]):
        display_html = self.__get_display_html()
        html = self.__get_html(enhanced_pylint_results)
        display_html(html)

    def __get_html(self, enhanced_pylint_results: List[Dict]) -> str:
        html = f"""
            <!doctype html>
              <html lang="en">
              <head>
                <meta charset="utf-8">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">
                <style type="text/css">
                  tr:focus-within {{background: #FDFFD8;}}
                </style>
              </head>
              <body>
                <h1>Pylint Results</h1>
                {self.__generate_pylint_results(enhanced_pylint_results)}
              </body>
            </html>
        """

        return html

    def __generate_pylint_results(self, enhanced_pylint_results: List[Dict]) -> str:
        if not enhanced_pylint_results:
            return '<p style="color:green;font-size: 150%;">Linting OK</p>'

        return f"""
            <i>How to fix</i>
              <ul>
                <li>
                  <b>bad-indentation: </b>
                  clone code to your laptop and run <code>pip install reindent</code> and <code>reindent -rv src/</code>
                </li>
                <li>
                  <b>false-positives: </b>
                  add <code>pylint: disable = error-name</code> comment to the code line
                </li>
              </ul>
            <table class="table table-sm small">
              <tr>
                <th></th>
                <th>Problem</th>
                <th>Line</th>
                <th>File</th>
              </tr>
              {self.__generate_notebook_rows(enhanced_pylint_results)}
              {self.__generate_file_rows(enhanced_pylint_results)}
              {self.__generate_other_rows(enhanced_pylint_results)}
            </table>
        """

    def __generate_notebook_rows(self, enhanced_pylint_results: List[Dict]) -> str:
        base_url = self.__databricks_context.get_host()
        notebook_results = [result for result in enhanced_pylint_results if result.get("file_type") == "NOTEBOOK"]
        table_rows = []

        with open(os.path.join(os.path.dirname(__file__), "icons", "notebook_icon.base64"), "r") as f:
            notebook_icon = f.read()

        for result in notebook_results:
            notebook_id = result["notebook_id"]
            cell_id = result["cell_id"]
            path = result["path"]
            cell_number = result["cell_number"]
            cell_line = result["cell_line"]
            message = result["message"]
            symbol = result["symbol"]

            table_rows.append(
                f"<tr>"
                f'<td><img src="{notebook_icon}" width=24px height=24px/></td>'
                f"<td>{message} ({symbol})</td>"
                f"<td>{cell_line}</td>"
                f'<td><a href="{base_url}/?command={cell_number}&line={cell_line}#notebook/{notebook_id}/command/{cell_id}">{path}</a></td>'
                f"</tr>"
            )

        return "\n".join(table_rows)

    def __generate_file_rows(self, enhanced_pylint_results: List[Dict]) -> str:
        base_url = self.__databricks_context.get_host()
        file_results = [result for result in enhanced_pylint_results if result.get("file_type") == "FILE"]
        table_rows = []

        with open(os.path.join(os.path.dirname(__file__), "icons", "file_icon.base64"), "r") as f:
            file_icon = f.read()

        for result in file_results:
            file_id = result["file_id"]
            line = result["line"]
            path = result["path"]
            message = result["message"]
            symbol = result["symbol"]

            table_rows.append(
                f"<tr>"
                f'<td><img src="{file_icon}" width=24px height=24px/></td>'
                f"<td>{message} ({symbol})</td>"
                f"<td>{line}</td>"
                f'<td><a href="{base_url}/?line={line}#files/{file_id}">{path}</a></td>'
                f"</tr>"
            )

        return "\n".join(table_rows)

    def __generate_other_rows(self, enhanced_pylint_results: List[Dict]) -> str:
        other_results = [result for result in enhanced_pylint_results if result.get("file_type") == "OTHER"]
        table_rows = []

        with open(os.path.join(os.path.dirname(__file__), "icons", "question_mark_icon.base64"), "r") as f:
            question_mark_icon = f.read()

        for result in other_results:
            line = result["line"]
            path = result["path"]
            message = result["message"]
            symbol = result["symbol"]

            table_rows.append(
                f"<tr>"
                f'<td><img src="{question_mark_icon}" width=24px height=24px/></td>'
                f"<td>{message} ({symbol})</td>"
                f"<td>{line}</td>"
                f"<td>{path}</td>"
                f"</tr>"
            )

        return "\n".join(table_rows)

    def __get_display_html(self):
        ipython = IPython.get_ipython()

        if not hasattr(ipython, "user_ns") or "displayHTML" not in ipython.user_ns:
            raise Exception("displayHTML cannot be resolved")

        return ipython.user_ns["displayHTML"]
