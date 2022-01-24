"""
execute subprocess command
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def call():
    """
    subprocess call, wait for command to complete
    """
    pass


@tags(TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def check_call():
    """
    execute_filesystem_commands
    """
    pass


@tags(TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def check_output():
    """
    execute_filesystem_commands
    """
    pass


@tags(
    TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION, TagConsts.PY3_ONLY
)
def getoutput():
    """Execute the string cmd in a shell, exit code is ignored"""
    pass


@tags(
    TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION, TagConsts.PY3_ONLY
)
def getstatusoutput():
    """Execute the string cmd in a shell"""
    pass


@tags(TagConsts.THREAD_SECURITY, TagConsts.EXTERNAL_COMMAND_EXECUTION)
class Popen:
    """
    subproces Popen execute commands
    """

    @tags(TagConsts.THREAD_SECURITY)
    def communicate(self):
        """
        execute_filesystem_commands
        """
        pass

    @tags(TagConsts.THREAD_SECURITY)
    def kill(self):
        """
        execute_filesystem_commands
        """
        pass

    @tags(TagConsts.THREAD_SECURITY)
    def send_signal(self):
        """
        execute_filesystem_commands
        """
        pass

    @tags(TagConsts.THREAD_SECURITY)
    def terminate(self):
        """
        execute_filesystem_commands
        """
        pass
