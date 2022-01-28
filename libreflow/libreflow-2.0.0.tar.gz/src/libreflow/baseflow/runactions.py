import os

from kabaret import flow
from kabaret.subprocess_manager.flow import RunAction


# RunActions
# -----------------


class OpenFileAction(RunAction):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    @classmethod
    def supported_extensions(cls):
        """
        Supported file extensions.

        Return None by default to allow any extension.
        """
        return None

    def allow_context(self, context):
        ext = os.path.splitext(self._file.path.get())[1]
        valid_ext = (
            self.supported_extensions() is None or ext in self.supported_extensions()
        )

        return context and context.endswith(".map") and valid_ext

    def extra_argv(self):
        return [self._file.path.get()]


class OpenWithBlenderAction(OpenFileAction):
    @classmethod
    def supported_extensions(cls):
        return [".blend"]

    def runner_name_and_tags(self):
        return "Blender", []


class OpenWithKritaAction(OpenFileAction):
    @classmethod
    def supported_extensions(cls):
        return [".kra", ".png", ".jpg"]

    def runner_name_and_tags(self):
        return "Krita", []
