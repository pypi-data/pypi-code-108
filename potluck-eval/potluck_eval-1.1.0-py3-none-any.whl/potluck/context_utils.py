"""
Support functions for contexts that are also needed by modules which the
`potluck.contexts` module depends on.

context_utils.py
"""

import io, os

from . import html_tools


#---------#
# Globals #
#---------#

BASE_CONTEXT_SLOTS = [
    "task_info",
    "username",
    "submission_root",
    "default_file",
    "actual_file"
]
"""
The context slots which can be expected to always be available, and which
are provided not via a `Context` object but by the evaluation system
itself.
"""


#---------------#
# Error classes #
#---------------#

class ContextError(Exception):
    """
    Custom exception class to use when context builders fail.
    """
    pass


class MissingContextError(ContextError):
    """
    Error indicating that required context is missing during
    testing/checking (i.e., an internal error in the construction of a
    Goal or Rubric).
    """
    pass


class ContextCreationError(ContextError):
    """
    Error indicating that context could not be created, usually because a
    submission was missing the required function or module, or because
    attempting to evaluate a function/module caused an error.
    """
    def __init__(self, context, message, cause=None):
        """
        Supply a Context object within which this error was generated, a
        message describing the error, and if there is one, an earlier
        Exception that caused this error.
        """
        self.context = context
        self.message = message
        self.cause = cause

    def __str__(self):
        return (
            "(arising in context '{}') {}"
        ).format(
            self.context.feedback_topic(), # errors won't appear in rubric
            (
                "<br>\n  caused by: {}".format(self.cause)
                if self.cause
                else ""
            )
        )

    def __repr__(self):
        return "ContextCreationError({}, {}, {})".format(
            repr(self.context), repr(self.message), repr(self.cause)
        )

    def explanation(self):
        """
        Chains through causes to return an HTML string describing why
        this context could not be established. Makes use of the html_tb
        property of our cause if it's present and the cause is not a
        ContextCreationError.
        """
        result = "Could not get '{}' because:".format(
            self.context.feedback_topic() # errors won't appear in rubric
        )
        if self.cause:
            # Short-circuit to the root of the chain if we can
            current = self
            chain = []
            while hasattr(current, "cause") and current.cause:
                chain.append(current)
                current = current.cause

            # Add the root cause's message first
            root_cause = current
            result += "<br>\n" + str(root_cause)

            # Try to get an HTML traceback for the root cause
            root_tb = str(root_cause)
            if hasattr(root_cause, "html_tb"):
                root_tb = root_cause.html_tb
            elif hasattr(root_cause, "__traceback__"):
                if self.context.cached_value is not None:
                    linkable = linkmap(self.context.cached_value)
                elif self.context.working_from is not None:
                    linkable = linkmap(self.context.working_from)
                else:
                    linkable = None
                root_tb = html_tools.html_traceback(
                    root_cause,
                    linkable=linkable
                )

            result += html_tools.build_html_details(
                "Details (click me):",
                html_tools.build_list(
                    [
                        "{}: {}".format(
                            error.context.feedback_topic(),
                            error.message
                        )
                        for error in chain
                    ] + [ root_tb ]
                )
            )
        else:
            result += "<br>\n" + self.message
        return result


#-------#
# Utils #
#-------#

def extract(context, slot):
    """
    Returns the value for the given slot of the given Context, raising a
    MissingContextError if there is no such value.
    """
    if slot in context:
        return context[slot]
    else:
        raise MissingContextError(
            f"Required context slot '{slot}' not found."
        )


def linkmap(context):
    """
    Returns a link dictionary suitable for the `linkable` parameter of
    `html_traceback`, based on the "task_info" and "filename" slots of
    the given context dictionary, or just based on the "task_info" if
    "filename" is not present. Returns None if "task_info" is missing.
    """
    if "task_info" in context and "filename" in context:
        return { context["filename"]: context["task_info"]["id"] }
    elif "task_info" in context:
        ti = context["task_info"]
        return { ti["target"]: ti["id"] }
    else:
        return None


class MashEnter(io.TextIOBase):
    """
    A fake input designed to be used in place of stdin. Reading anything
    just returns newlines.
    """
    def read(size=-1):
        """
        Returns a newline, or if a specific size is specified, that many
        newlines. Behavior is weird since normally you can't call read
        multiple times.
        """
        if size == -1:
            return '\n'
        else:
            return '\n' * size

    def readline(size=-1):
        """
        Returns a newline.
        """
        return '\n'


class AllOnes(io.TextIOBase):
    """
    A fake input designed to be used in place of stdin. Reading anything
    just returns the string '1' with a newline at the end.
    """
    def read(size=-1):
        """
        Returns a string containing the digit 1 followed by a newline, or
        if a specific size is specified, that many ones minus one, plus a
        single newline. Behavior is weird since normally you can't call
        read multiple times.
        """
        if size == -1:
            return '1\n'
        else:
            return '1' * (size - 1) + '\n'

    def readline(size=-1):
        """
        Returns the digit 1 followed by a newline.
        """
        return '1\n'


def sandbox_filemap(spec):
    """
    Extracts the standard symlink mapping for sandbox files from the
    given specification, based on its helper_files and starter_path
    properties. The result maps absolute filenames to sandbox-relative
    filenames and specifies how to copy helper files into a sandbox.
    """
    return {
        os.path.abspath(os.path.join(spec.starter_path, helper)): helper
        for helper in spec.helper_files
    }


#---------------------------#
# ContextualValue machinery #
#---------------------------#

class ContextualValue:
    """
    This class and its subclasses represent values that may appear as
    part of arguments in a code behavior test (see
    create_code_behavior_context_builder). Before testing, those
    arguments will be replaced (using the instance's replace method). The
    replace method will receive the current context as its first
    argument, along with a boolean indicating whether the value is being
    requested to test the submitted module (True) or solution module
    (False).

    The default behavior (this class) is to accept a function when
    constructed and run that function on the provided context dictionary,
    using the function's return value as the actual argument to the
    function being tested.

    Your extractor function should ideally raise MissingContextError in
    cases where a context value that it depends on is not present,
    although this is not critical.
    """
    def __init__(self, value_extractor):
        """
        There is one required argument: the value extractor function,
        which will be given a context dictionary and a boolean indicating
        submitted vs. solution testing, and will be expected to produce
        an argument value.
        """
        self.extractor = value_extractor

    def __str__(self):
        return "a contextual value based on {}".format(
            self.extractor.__name__
        )

    def __repr__(self):
        return "<a ContextualValue based on {}>".format(
            self.extractor.__name__
        )

    def replace(self, context):
        """
        This method is used to provide an actual argument value to take
        the place of this object.

        The argument is the context to use to retrieve a value.

        This implementation simply runs the provided extractor function
        on the two arguments it gets.
        """
        return self.extractor(context)


class ContextSlot(ContextualValue):
    """
    A special case ContextualValue where the value to be used is simply
    stored in a slot in the context dictionary, with no extra processing
    necessary. This class just needs the string name of the slot to be
    used.
    """
    def __init__(self, slot_name):
        """
        One required argument: the name of the context slot to use.
        """
        self.slot = slot_name

    def __str__(self):
        return "the current '{}' value".format(self.slot)

    def __repr__(self):
        return "<a ContextSlot for " + str(self) + ">"

    def replace(self, context):
        """
        We retrieve the slot value from the context. Notice that if the
        value is missing, we generate a MissingContextError that should
        eventually bubble out.
        """
        # Figure out which slot we're using
        slot = self.slot

        if slot not in context:
            raise MissingContextError(
                (
                    "Context slot '{}' is required by a ContextSlot dynamic"
                    " value, but it is not present in the testing context."
                ).format(slot)
            )
        return context[slot]


class ModuleValue(ContextualValue):
    """
    A kind of ContextualValue that evaluates a string containing Python
    code within the module stored in the "module" context slot.
    """
    def __init__(self, expression):
        """
        One required argument: the expression to evaluate, which must be
        a string that contains a valid Python expression.
        """
        self.expression = expression

    def __str__(self):
        return "the result of " + self.expression

    def __repr__(self):
        return "<a ModuleValue based on {}>".format(str(self))

    def replace(self, context):
        """
        We retrieve the "module" slot value from the provided context.

        We then evaluate our expression within the retrieved module, and
        return that result.
        """
        if "module" not in context:
            raise MissingContextError(
                "ModuleValue argument requires a 'module' context"
              + " key, but there isn't one."
            )
        module = context["module"]

        return eval(self.expression, module.__dict__)


class SolnValue(ContextualValue):
    """
    Like a ModuleValue, but *always* takes the value from the solution
    module, even when we're testing submitted code.
    """
    def __init__(self, expression):
        """
        One required argument: the expression to evaluate, which must be
        a string that contains a valid Python expression.
        """
        self.expression = expression

    def __str__(self):
        return "the correct value of " + self.expression

    def __repr__(self):
        return "<a SolnValue based on {}>".format(str(self))

    def replace(self, context):
        """
        We retrieve the "ref_module" slot value from the provided context.

        We then evaluate our expression within the retrieved module, and
        return that result.
        """
        if "ref_module" not in context:
            raise MissingContextError(
                f"SolnValue argument requires a 'ref_module' context"
                f" key, but there isn't one in: {list(context.keys())}"
            )
        module = context["ref_module"]

        return eval(self.expression, module.__dict__)
