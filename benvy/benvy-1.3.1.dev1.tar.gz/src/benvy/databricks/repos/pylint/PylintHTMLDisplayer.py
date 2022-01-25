import IPython
from benvy.databricks.DatabricksContext import DatabricksContext


class PylintHTMLDisplayer:
    def __init__(
        self,
        databricks_context: DatabricksContext,
    ):
        self.__databricks_context = databricks_context

    def display(self, enhanced_pylint_results: list):
        display_html = self.__get_display_html()
        html = self.__get_html(enhanced_pylint_results)
        display_html(html)

    def __get_html(self, enhanced_pylint_results: list) -> str:
        html = f"""
            <!doctype html>
              <html lang="en">
              <head>
                <meta charset="utf-8">
                <style type="text/css">
                  table, th, td {{border: 1px solid gray;}}
                  td, th {{padding: 5px 10px;}}
                  ul {{font-size: 120%}}
                  code {{font-family: Consolas,"courier new"; color: crimson; background-color: #f1f1f1; padding: 2px; font-size: 105%;}}
                  tr:focus-within {{background: #FDFFD8;}}
                  .text-center {{text-align: center;}}
                </style>
              </head>
              <body>
                <h1>How to fix</h1>
                  <ul>
                    <li>
                      <b>bad-indentation: </b>
                      clone code to your laptop and run <code>python .venv/Tools/scripts/reindent.py -rv src/</code>
                    </li>
                    <li>
                      <b>false-positives: </b>
                      add <code>pylint: disable = error-name</code> comment to the code line
                    </li>
                  </ul>
                <h1>Notebooks</h1>
                  {self.__generate_notebook_lint_table(enhanced_pylint_results)}
                <h1>Files</h1>
                  {self.__generate_file_lint_table(enhanced_pylint_results)}
              </body>
            </html>
        """

        return html

    def __generate_notebook_lint_table(self, enhanced_pylint_results: list) -> str:
        base_url = self.__databricks_context.get_host()
        notebook_results = [result for result in enhanced_pylint_results if result["file_type"] == "NOTEBOOK"]
        table_rows = []

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
                f'<td><a href="{base_url}/?command={cell_number}&line={cell_line}#notebook/{notebook_id}/command/{cell_id}">{path}</a></td>'
                f"<td>{cell_line}</td>"
                f"<td>{message} ({symbol})</td>"
                f"</tr>"
            )

        return f"""
            <table width="100%">
            {self.__get_lint_table_header()}
            {' '.join(table_rows)}
            </table>
        """

    def __generate_file_lint_table(self, enhanced_pylint_results: list) -> str:
        base_url = self.__databricks_context.get_host()
        file_results = [result for result in enhanced_pylint_results if result["file_type"] == "FILE"]
        table_rows = []

        for result in file_results:
            file_id = result["file_id"]
            line = result["line"]
            path = result["path"]
            message = result["message"]
            symbol = result["symbol"]

            table_rows.append(
                f"<tr>"
                f'<td><a href="{base_url}/?line={line}#files/{file_id}">{path}</a></td>'
                f"<td>{line}</td>"
                f"<td>{message} ({symbol})</td>"
                f"</tr>"
            )

        return f"""
            <table width="100%">
            {self.__get_lint_table_header()}
            {' '.join(table_rows)}
            </table>
        """

    def __get_lint_table_header(self) -> str:
        return """
            <tr>
            <th>File</th>
            <th>Line</th>
            <th>Problem</th>
            </tr>
        """

    def __get_display_html(self):
        ipython = IPython.get_ipython()

        if not hasattr(ipython, "user_ns") or "displayHTML" not in ipython.user_ns:
            raise Exception("displayHTML cannot be resolved")

        return ipython.user_ns["displayHTML"]
