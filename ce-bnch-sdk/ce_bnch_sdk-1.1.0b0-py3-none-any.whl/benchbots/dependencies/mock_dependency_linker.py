from unittest import mock

from benchling_sdk.benchbots.dependencies.dependency_linker import DependencyLinker
from benchling_sdk.benchbots.dependencies.mock_dependency_resolver import MockDependencyResolver


class MockDependencyLinker(DependencyLinker):
    def __init__(self):
        super().__init__(MockDependencyResolver())
        # Silence typer CLI which is tightly coupled to logic in DependencyLinker
        self.mock_echo = mock.patch("typer.echo")
        self.mock_echo.start()
        self.mock_prompt = mock.patch("typer.prompt")
        self.mock_prompt.start()

    def __del__(self):
        self.mock_echo.stop()
        self.mock_prompt.stop()
