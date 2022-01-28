import inspect
import yappi  # pylint: disable=import-error # Never get here due to checks in App

from .utils import die, warn


class Profiler:
    def __init__(
        self, enabled, tag1: str, tag2: str = "", clocktype: str = "wall",
    ):
        """Ease of use wrapper for Yappi profiler.

        Only a single profile can be created at a time, but serial profiles
        are fine. Calling start() twice with no intervening stop() will
        terminate execution.

        Args:

            enabled (bool) : Whether profilng is enabled or not.

            tag1 (str): Component of output filenames e.g. denoting characteristic of run.

            tag2 (str, optional): Another component of output filenames. Defaults to "".

            clocktype (str, optional): "wall" or "cpu". Defaults to "wall".
        """
        self.enabled = enabled
        self.tag1 = tag1
        self.tag2 = tag2
        self.tag3 = None
        self.clocktype = clocktype
        self._start_frame_msg = None

    # --------------------------------------------------------------------------

    def __del__(self):
        """
        Close off any still running profiling.
        """
        if self._start_frame_msg:
            self.stop()

    # --------------------------------------------------------------------------

    def start(self, tag3, clocktype: str = None):
        """Configure and start profiling.

        Args:

            tag3 (str, optional): Another component of output filenames. Defaults to "".

            clocktype (str, optional): "wall" or "cpu". Defaults to None.
                                       If set, overrides instance setting.
        """
        if self.enabled:
            # If already profiling, bail with details of prior Profiler.start() call.
            if self._start_frame_msg is not None:
                # Some Python implementations don't produce anything useful
                # from currentframe(), so default to a blander message in that
                # case
                msg = self._start_frame_msg

                thisframe = inspect.currentframe()
                if thisframe is not None:
                    msg = (
                        f"Previous call:  {msg}.\n"
                        f"Current  call:  {get_frame_location(thisframe.f_back)}"
                    )

                # Clear to not trigger Profiler.stop() in destructor
                self._start_frame_msg = None

                die(  # pylint: disable=access-member-before-definition
                    f'Profiling already in progress (tagged: "{self.tag3}").'
                    "\nCan't call Profiler.start() again before calling"
                    f" Profiler.stop(). Use Profiler.start_new() instead?\n{msg}"
                )

            # Stash details of this call
            # As noted above, if currentframe() isn't helpful, default to a
            # blander message.
            thisframe = inspect.currentframe()
            if thisframe is None:
                self._start_frame_msg = ""
            else:
                self._start_frame_msg = get_frame_location(thisframe.f_back)

            self.tag3 = tag3

            # Configure and start the profiling
            yappi.set_clock_type(clocktype if clocktype is not None else self.clocktype)
            yappi.start()

    # --------------------------------------------------------------------------

    def start_new(self, tag3, clocktype: str = None):
        """Stop current profiling, configure and start new profiling.

        Bails if not currently profiling.

        Args:

            tag3 (str, optional): Another component of output filenames. Defaults to "".

            clocktype (str, optional): "wall" or "cpu". Defaults to None.
                                       If set, overrides instance setting.
        """
        if self.enabled:
            # If NOT already profiling, bail because of broken expectations
            if self._start_frame_msg is None:
                msg = ""
                thisframe = inspect.currentframe()
                if thisframe is not None:
                    msg = get_frame_location(thisframe.f_back)
                die(
                    f'Profiler.start_new("{tag3}") called when no profiling already'
                    f" taking place. Use Profiler.start() instead?{msg}"
                )

            self.stop()
            self.start(tag3, clocktype)

    # --------------------------------------------------------------------------

    def stop(self):
        """Stop profiling, dump output, tidy up."""
        if self.enabled:
            if self._start_frame_msg is None:
                warn("Profiler.stop() called when no profiling taking place.")
                return

            yappi.stop()

            tag2 = f".{self.tag2}" if self.tag2 else ""
            tag3 = f".{self.tag3}" if self.tag3 else ""

            callgrind_filename = f"callgrind.{self.tag1}{tag2}{tag3}.prof"
            yappi_filename = f"yappi.{self.tag1}{tag2}{tag3}.prof"

            func_stats = yappi.get_func_stats()
            func_stats.save(  # pylint: disable=no-member
                callgrind_filename, "CALLGRIND"
            )

            with open(yappi_filename, "w",) as yfile:
                func_stats.print_all(yfile)  # pylint: disable=no-member

            yappi.clear_stats()
            self._start_frame_msg = None


# ------------------------------------------------------------------------------


def get_class_from_frame(frame) -> str:
    """Discover if the frame was running a class' method.

    Args:
        frame (frame): Frame to probe

    Returns:
        str : Name of class or None if frame wasn't running a class method
    """
    # pylint: disable=deprecated-method # mistakenly deprecated, pylint not yet caught up
    args, _, _, value_dict = inspect.getargvalues(frame)
    # we check the first parameter for the frame function is
    # named 'self'
    if args and args[0] == "self":
        # in that case, 'self' will be referenced in value_dict
        instance = value_dict.get("self", None)
        if instance:
            # return its class
            return getattr(instance, "__class__", None)
    # return None otherwise
    return None


# ------------------------------------------------------------------------------


def get_frame_location(frame):
    """Return the method/function name, and filename and line number of callstack frame.

    Args:
        frame (frame): Frame to probe

    Returns:
        str : The method/function name, and file/line number details. Formatted.
    """
    frame_info = inspect.getframeinfo(frame)
    function_name = frame_info.function
    class_name = get_class_from_frame(frame)
    if class_name:
        function_name = f"{class_name}.{function_name}"
    return f"'{function_name}()' at '{frame_info.filename}:{frame_info.lineno}'"


# ------------------------------------------------------------------------------
