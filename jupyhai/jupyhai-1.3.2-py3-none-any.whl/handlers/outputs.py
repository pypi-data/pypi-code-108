from valohai_cli.commands.execution.outputs import get_execution_outputs

from jupyhai.handlers.base import JupyhaiHandler


class OutputsHandler(JupyhaiHandler):
    def get(self, execution_id: str) -> None:
        self.finish({'results': get_execution_outputs({'id': execution_id})})
