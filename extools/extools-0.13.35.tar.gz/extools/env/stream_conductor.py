import io
import sys
from contextlib import contextmanager

class StreamConductor():
    """The StreamConductor manages standard I/O operations for Extender.

    The Extender environment isn't connected to stdout, stderr, or stdin.
    To allow applications that assume they'll be present to work,
    StreamConductor patches them to string buffers that can be read from
    or written to.

    :param stdout: file-like object for stdout.
    :type stdout: file-like object
    :param stderr: file-like object for stderr.
    :type stderr: file-like object
    :param stdin: file-like object for stdin.
    :type stdin: file-like object
    """

    def __init__(self, stdout=None, stderr=None, stdin=None):

        if not stdout:
            stdout = io.StringIO()
        if not stderr:
            stderr = io.StringIO()
        if not stdin:
            stdin = io.StringIO()

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        self.init_stdin = sys.stdin
        self.init_stdout = sys.stdout
        self.init_stderr = sys.stderr

    def patch_streams(self):
        """Patch stdout, stderr, and stdin."""
        sys.stdout = self.stdout
        sys.stdin = self.stdin
        sys.stderr = self.stderr

    def unpatch_streams(self):
        """Restore streams to their original state."""
        sys.stdout = self.init_stdout
        sys.stdin = self.init_stdin
        sys.stderr = self.init_stderr

    @contextmanager
    def patched_streams(self):
        """Temporarily patch streams, making sure they are restored.

        Context manager for working with patched streams temporarily.
        After the block exits, the streams will be restored to their
        original state.

        .. code-block:: python

            conductor = StreamConductor()
            with conductor.patched_streams():
                print("Hello")

            print(conductor.stdout.getValue()) # prints "Hello"
        """

        try:
            self.patch_streams()
            yield
        finally:
            self.unpatch_streams()

