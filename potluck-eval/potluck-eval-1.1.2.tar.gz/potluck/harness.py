"""
Tools for testing Python code and recording things like results, printed
output, or even traces of calls to certain functions.

harness.py

These tools start with a few functions for creating "payloads" which are
functions that take a context dictionary as a single argument and which
return dictionaries of new context slots to establish (it's no
coincidence that this same formula is what is expected of a context
builder function; payloads are context builders).

Once a payload is established, this module offers a variety of
augmentation functions which can create modified payloads with additional
functionality. Note that some of these augmentations interfere with each
other in minor ways, and should therefore be applied before others.

Also note that not every augmentation makes sense to apply to every kind
of payload (in particular, module import payloads don't make use of the
"module" context slot, so augmentations like `with_module_decorations`
can't be usefully applied to them).
"""

import copy
import sys
import imp
import io
import re
import traceback
import shelve
import os
import ast

import turtle

from . import load
from . import mast
from . import context_utils
from . import html_tools
from . import timeout
from . import logging
from . import time_utils


#---------#
# Globals #
#---------#

AUGMENTATION_ORDER = [
    "with_module_decorations",
    "tracing_function_calls",
    "with_setup",
    "with_cleanup",
    "capturing_printed_output",
    "with_fake_input",
    "with_timeout",
    "capturing_turtle_drawings",
    "capturing_wavesynth_audio",
    "capturing_file_contents",
    "sampling_distribution_of_results",
    "run_in_sandbox",
    "run_for_base_and_ref_values"
]
"""
Ideal order in which to apply augmentations in this module when multiple
augmentations are being applied to the same payload. Because certain
augmentations interfere with others if not applied in the correct order,
applying them in order is important, although in certain cases special
applications might want to deviate from this order.

Note that even following this order, not all augmentations are really
compatible with each other. For example, if one were to use
`with_module_decorations` to perform intensive decoration (which is
somewhat time-consuming per-run) and also attempt to use
`sampling_distribution_of_results` with a large sample count, the
resulting payload might be prohibitively slow.
"""


#----------------------------#
# Payload creation functions #
#----------------------------#

def create_module_import_payload(
    name_prefix="loaded_",
    use_fix_parse=True,
    prep=None,
    wrap=None
):
    """
    This function returns a zero-argument payload function which imports
    file identified by the "file_path" slot of the given context, using
    the "filename" slot of the given context as the name of the file for
    the purpose of deciding a module name, and establishing the resulting
    module in the "module" slot along with "original_source" and "source"
    slots holding the original and (possibly modified) source code.

    It reads the "task_info" context slot to access the specification and
    load the helper files list to make available during module execution.

    A custom `name_prefix` may be given which will alter the name of the
    imported module in sys.modules and in the __name__ automatic
    variable as the module is being created; use this to avoid conflicts
    when importing submitted and solution modules that have the same
    filename.

    If `use_fix_parse` is provided, `potluck.load.fix_parse` will be used
    instead of just `mast.parse`, and in addition to generating
    "original_source", "source", "scope", and "module" slots, a
    "parse_errors" slot will be generated, holding a (hopefully empty)
    list of Exception objects that were 'successfully' ignored during
    parsing.

    `prep` and/or `wrap` functions may be supplied, the `prep` function
    will be given the module source as a string and must return it (or a
    modified version); the `wrap` function will be given the compiled
    module object and whatever it returns will be substituted for the
    original module.
    """
    def payload(context):
        """
        Imports a specific file as a module, using a prefix in addition
        to the filename itself to determine the module name. Returns a
        'module' context slot.
        """
        filename = context_utils.extract(context, "filename")
        file_path = context_utils.extract(context, "file_path")
        file_path = os.path.abspath(file_path)
        full_name = name_prefix + filename

        # Read the file
        with open(file_path, 'r', encoding="utf-8") as fin:
            original_source = fin.read()

        # Call our prep function
        if prep:
            source = prep(original_source)
        else:
            source = original_source

        # Decide if we're using fix_parse or not
        if use_fix_parse:
            # Parse using fix_parse
            fixed, node, errors = load.fix_parse(source, full_name)
        else:
            # Just parse normally without attempting to steamroll errors
            fixed = source
            node = mast.parse(source, filename=full_name)
            errors = None

        # Since this payload is already running inside a sandbox
        # directory, we don't need to provide a sandbox argument here.
        module = load.create_module_from_code(
            node,
            full_name,
            on_disk=file_path,
            sandbox=None
        )

        result = {
            "original_source": original_source,
            "source": fixed,
            "scope": node,
            "module": module
        }
        if errors:
            result["parse_errors"] = errors

        # Wrap the resulting module if a wrap function was provided
        if wrap:
            result["module"] = wrap(result["module"])

        # Return our result
        return result

    return payload


def create_read_variable_payload(varname):
    """
    Creates a payload function which retrieves the given variable from
    the "module" slot of the given context when run, placing the
    retrieved value into a "value" slot. If the variable name is a
    `potluck.context_utils.ContextualValue`, it will be replaced with a
    real value first. The "variable" slot of the result context will be
    set to the actual variable name used.
    """
    def payload(context):
        """
        Retrieves a specific variable from a certain module. Returns a
        "value" context slot.
        """
        nonlocal varname
        module = context_utils.extract(context, "module")
        if isinstance(varname, context_utils.ContextualValue):
            try:
                varname = varname.replace(context)
            except Exception:
                logging.log(
                    "Encountered error while attempting to substitute"
                    " contextual value:"
                )
                logging.log(traceback.format_exc())
                raise
        return {
            "variable": varname,
            "value": getattr(module, varname)
        }

    return payload


def create_run_function_payload(
    fname,
    posargs=None,
    kwargs=None,
    copy_args=True
):
    """
    Creates a payload function which retrieves a function from the
    "module" slot of the given context and runs it with certain
    positional and/or keyword arguments, returning a "value" context slot
    containing the function's result. The arguments used are also placed
    into "args" and "kwargs" context slots in case those are useful for
    later checks, and the function name is placed into a "function"
    context slot.

    If `copy_args` is set to True (the default), deep copies of argument
    values will be made before they are passed to the target function
    (note that keyword argument keys are not copied, although they should
    be strings in any case). The "args" and "kwargs" slots will also get
    copies of the arguments, not the original values, and these will be
    separate copies from those given to the function, so they'll retain
    the values used as input even after the function is finished.
    However, "used_args" and "used_kwargs" slots will be added if
    `copy_args` is set to true that hold the actual arguments sent to the
    function so that any changes made by the function can be measured if
    necessary.

    If the function name or any of the argument values (or keyword
    argument keys) are `potluck.context_utils.ContextualValue` instances,
    these will be replaced with actual values using the given context
    before the function is run. This step happens before argument
    copying, and before the "args" and "kwargs" result slots are set up.
    """
    posargs = posargs or ()
    kwargs = kwargs or {}

    def payload(context):
        """
        Runs a specific function in a certain module with specific
        arguments. Returns a "value" context slot.
        """
        nonlocal fname
        module = context_utils.extract(context, "module")
        if isinstance(fname, context_utils.ContextualValue):
            try:
                fname = fname.replace(context)
            except Exception:
                logging.log(
                    "Encountered error while attempting to substitute"
                    " contextual value:"
                )
                logging.log(traceback.format_exc())
                raise
        fn = getattr(module, fname)

        real_posargs = []
        initial_posargs = []
        real_kwargs = {}
        initial_kwargs = {}
        for arg in posargs:
            if isinstance(arg, context_utils.ContextualValue):
                try:
                    arg = arg.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            if copy_args:
                real_posargs.append(copy.deepcopy(arg))
                initial_posargs.append(copy.deepcopy(arg))

            else:
                real_posargs.append(arg)
                initial_posargs.append(arg)

        for key in kwargs:
            if isinstance(key, context_utils.ContextualValue):
                try:
                    key = key.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            value = kwargs[key]
            if isinstance(value, context_utils.ContextualValue):
                try:
                    value = value.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            if copy_args:
                real_kwargs[key] = copy.deepcopy(value)
                initial_kwargs[key] = copy.deepcopy(value)
            else:
                real_kwargs[key] = value
                initial_kwargs[key] = value

        result = {
            "value": fn(*real_posargs, **real_kwargs),
            "function": fname,
            "args": initial_posargs,
            "kwargs": initial_kwargs,
        }

        if copy_args:
            result["used_args"] = real_posargs
            result["used_kwargs"] = real_kwargs

        return result

    return payload


def create_run_harness_payload(
    harness,
    fname,
    posargs=None,
    kwargs=None,
    copy_args=False
):
    """
    Creates a payload function which retrieves a function from the
    "module" slot of the given context and passes it to a custom harness
    function for testing. The harness function is given the function
    object to test as its first parameter, followed by the positional and
    keyword arguments specified here. Its result is placed in the "value"
    context slot. Like `create_run_function_payload`, "args", "kwargs",
    and "function" slots are established, and a "harness" slot is
    established which holds the harness function used.

    If `copy_args` is set to True, deep copies of argument values will be
    made before they are passed to the harness function (note that keyword
    argument keys are not copied, although they should be strings in any
    case).

    If the function name or any of the argument values (or keyword
    argument keys) are `potluck.context_utils.ContextualValue` instances,
    these will be replaced with actual values using the given context
    before the function is run. This step happens before argument
    copying and before these items are placed into their result slots.
    """
    posargs = posargs or ()
    kwargs = kwargs or {}

    def payload(context):
        """
        Tests a specific function in a certain module using a test
        harness, with specific arguments. Returns a "value" context slot.
        """
        nonlocal fname
        module = context_utils.extract(context, "module")
        if isinstance(fname, context_utils.ContextualValue):
            try:
                fname = fname.replace(context)
            except Exception:
                logging.log(
                    "Encountered error while attempting to substitute"
                    " contextual value:"
                )
                logging.log(traceback.format_exc())
                raise
        fn = getattr(module, fname)

        real_posargs = []
        real_kwargs = {}
        for arg in posargs:
            if isinstance(arg, context_utils.ContextualValue):
                try:
                    arg = arg.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            if copy_args:
                arg = copy.deepcopy(arg)

            real_posargs.append(arg)

        for key in kwargs:
            if isinstance(key, context_utils.ContextualValue):
                try:
                    key = key.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            value = kwargs[key]
            if isinstance(value, context_utils.ContextualValue):
                try:
                    value = value.replace(context)
                except Exception:
                    logging.log(
                        "Encountered error while attempting to substitute"
                        " contextual value:"
                    )
                    logging.log(traceback.format_exc())
                    raise

            if copy_args:
                value = copy.deepcopy(value)

            real_kwargs[key] = value

        return {
            "value": harness(fn, *real_posargs, **real_kwargs),
            "harness": harness,
            "function": fname,
            "args": real_posargs,
            "kwargs": real_kwargs
        }

    return payload


def make_module(statements):
    """
    Creates an ast.Module object from a list of statements. Sets empty
    type_ignores if we're in a version that requires them.
    """
    vi = sys.version_info
    if vi[0] > 3 or vi[0] == 3 and vi[1] >= 8:
        return ast.Module(statements, [])
    else:
        return ast.Module(statements)


def create_execute_code_block_payload(block_name, src, nodes=None):
    """
    Creates a payload function which executes a series of statements
    (provided as a multi-line code string OR list of AST nodes) in the
    current context's "module" slot. A block name (a string) must be
    provided and will appear as the filename if tracebacks are generated.

    The 'src' argument must be a string, and dictates how the code will
    be displayed, the 'nodes' argument must be a collection of AST nodes,
    and dictates what code will actually be executed. If 'nodes' is not
    provided, the given source code will be parsed to create a list of
    AST nodes.

    The payload runs the final expression or statement last, and if it
    was an expression, its return value will be put in the "value"
    context slot of the result; otherwise None will be put there (of
    course, a final expression that evaluates to None would give the same
    result).

    The source code given is placed in the "block" context slot, while
    the nodes used are placed in the "block_nodes" context slot, and the
    block name is placed in the "block_name" context slot.

    Note that although direct variable reassignments and new variables
    created by the block of code won't affect the module it's run in,
    more indirect changes WILL, so be extremely careful about side
    effects!
    """
    # Parse src if nodes weren't specified explicitly
    if nodes is None:
        nodes = ast.parse(src).body

    def payload(context):
        """
        Runs a sequence of statements or expressions (provided as AST
        nodes) in a certain module. Creates a "value" context slot with
        the result of the last expression, or None if the last node was a
        statement.
        """
        module = context_utils.extract(context, "module")

        # Separate nodes into start and last
        start = nodes[:-1]
        last = nodes[-1]

        # Create a cloned execution environment
        env = {}
        env.update(module.__dict__)

        if len(start) > 0:
            code = compile(make_module(start), block_name, 'exec')
            exec(code, env)

        if isinstance(last, ast.Expr):
            # Treat last line as an expression and grab its value
            last_code = compile(
                ast.Expression(last.value),
                block_name + "(final)",
                'eval'
            )
            value = eval(last_code, env)
        else:
            # Guess it wasn't an expression; just execute it
            last_code = compile(
                make_module([last]),
                block_name + "(final)",
                'exec'
            )
            exec(last_code, env)
            value = None

        return {
            "value": value,
            "block_name": block_name,
            "block": src,
            "block_nodes": nodes
        }

    return payload


#--------------------------------#
# Harness augmentation functions #
#--------------------------------#

def run_for_base_and_ref_values(
    payload,
    used_by_both=None,
    cache_ref=True,
    ref_only=False
):
    """
    Accepts a payload function and returns a modified payload function
    which runs the provided function twice, the second time using ref_*
    context values and setting ref_* versions of the original payload's
    result slots. If a certain non-ref_* value needs to be available to
    the reference payload other than the standard
    `potluck.context_utils.BASE_CONTEXT_SLOTS`, it must be provided in
    the "used_by_both" list.

    Note that when applying multiple payload augmentations, this one
    should be applied last.

    The default behavior actually caches the reference values it
    produces, under the assumption that only if cached reference values
    are older than the solution file or the specification module should
    the reference run actually take place. If this assumption is
    incorrect, you should set `cache_ref` to False to actually run the
    reference payload every time.

    If you only care about the reference results (e.g., when compiling a
    snippet) you can set ref_only to true, and the initial run will be
    skipped.

    TODO: Shelf doesn't support multiple-concurrent access!!!
    TODO: THIS
    """
    used_by_both = used_by_both or []

    def double_payload(context):
        """
        Runs a payload twice, once normally and again against a context
        where all ref_* slots have been merged into their non-ref_*
        equivalents. Results from the second run are stored in ref_*
        versions of the slots they would normally occupy, alongside the
        original results. When possible, fetches cached results for the
        ref_ values instead of actually running the payload a second
        time.
        """
        # Get initial results
        if ref_only:
            full_result = {}
        else:
            full_result = payload(context)

        # Figure out our cache key
        taskid = context["task_info"]["id"]
        goal_id = context["goal_id"]
        nth = context["which_context"]
        # TODO: This cache key doesn't include enough info about the
        # context object, apparently...
        cache_key = taskid + ":" + goal_id + ":" + str(nth)
        ts_key = cache_key + "::ts"

        # Check the cache
        cache_file = context["task_info"]["reference_cache_file"]
        use_cached = True
        cached = None

        ignore_cache = context["task_info"]["ignore_cache"]
        # TODO: Fix caching!!!
        ignore_cache = True

        # Respect ignore_cache setting
        if not ignore_cache:
            with shelve.open(cache_file) as shelf:
                if ts_key not in shelf:
                    use_cached = False
                else: # need to check timestamp
                    ts = shelf[ts_key]

                    # Get modification times for spec + solution
                    spec = context["task_info"]["specification"]
                    mtimes = []
                    for fn in [ spec.__file__ ] + [
                        os.path.join(spec.soln_path, f)
                        for f in spec.soln_files
                    ]:
                        mtimes.append(os.stat(fn).st_mtime)

                    # Units are seconds
                    changed_at = time_utils.time_from_timestamp(
                        max(mtimes)
                    )

                    # Convert cache timestamp to seconds and compare
                    cache_time = time_utils.time_from_timestring(ts)

                    # Use cache if it was produced *after* last change
                    if cache_time <= changed_at:
                        use_cached = False
                    # else leave it at default True

                # grab cached values
                if use_cached:
                    cached = shelf[cache_key]

        # Skip re-running the payload if we have a cached result
        if cached is not None:
            ref_result = cached
        else:
            # Create a context where each ref_* slot value is assigned to
            # the equivalent non-ref_* slot
            ref_context = {
                key: context[key]
                for key in context_utils.BASE_CONTEXT_SLOTS
            }
            for key in context:
                if key in used_by_both:
                    ref_context[key] = context[key]
                elif key.startswith("ref_"):
                    ref_context[key[4:]] = context[key]
                    # Retain original ref_ slots alongside collapsed slots
                    ref_context[key] = context[key]

            # Get results from collapsed context
            try:
                ref_result = payload(ref_context)
            except context_utils.MissingContextError as e:
                e.args = (
                    e.args[0] + " (in reference payload)",
                ) + e.args[1:]
                raise e

            # Make an entry in our cache
            if not ignore_cache:
                with shelve.open(cache_file) as shelf:
                    # Just cache new things added by ref payload
                    hollowed = {}
                    for key in ref_result:
                        if (
                            key not in context
                         or ref_result[key] != context[key]
                        ):
                            hollowed[key] = ref_result[key]
                    # If ref payload produces uncacheable results, we
                    # can't cache anything
                    try:
                        shelf[cache_key] = ref_result
                        shelf[ts_key] = time_utils.timestring()
                    except Exception:
                        logging.log(
                            "Payload produced uncacheable reference"
                            " value(s):"
                        )
                        logging.log(html_tools.string_traceback())

        # Assign collapsed context results into final result under ref_*
        # versions of their slots
        for slot in ref_result:
            full_result["ref_" + slot] = ref_result[slot]

        return full_result

    return double_payload


def run_in_sandbox(payload):
    """
    Returns a modified payload function which runs the provided base
    payload, but first sets the current directory to the sandbox
    directory specified by the provided context's "sandbox" slot.
    Afterwards, it changes back to the original directory.

    TODO: More stringent sandboxing?
    """
    def sandboxed_payload(context):
        """
        A payload function which runs a base payload within a specific
        sandbox directory.
        """
        orig_cwd = os.getcwd()
        try:
            os.chdir(context_utils.extract(context, "sandbox"))
            result = payload(context)
        finally:
            os.chdir(orig_cwd)

        return result

    return sandboxed_payload


def with_setup(payload, setup):
    """
    Creates a modified payload which runs the given setup function
    (with the incoming context dictionary as an argument) right before
    running the base payload. The setup function's return value is used
    as the context for the base payload.

    Note that based on the augmentation order, function calls made during
    the setup WILL NOT be captured as part of a trace if
    tracing_function_calls is also used, but printed output during the
    setup WILL be available via capturing_printed_output if that is used.
    """
    def setup_payload(context):
        """
        Runs a base payload after running a setup function.
        """
        context = setup(context)
        if context is None:
            raise ValueError("Context setup function returned None!")
        return payload(context)

    return setup_payload


def with_cleanup(payload, cleanup):
    """
    Creates a modified payload which runs the given cleanup function
    (with the original payload's result, which is a context dictionary,
    as an argument) right after running the base payload. The return
    value is the cleanup function's return value.

    Note that based on the augmentation order, function calls made during
    the setup WILL NOT be captured as part of a trace if
    tracing_function_calls is also used, but printed output during the
    setup WILL be available via capturing_printed_output if that is used.
    """
    def cleanup_payload(context):
        """
        Runs a base payload and then runs a cleanup function.
        """
        result = payload(context)
        return cleanup(result)

    return cleanup_payload


def capturing_printed_output(
    payload,
    capture_errors=False,
    capture_stderr=False
):
    """
    Creates a modified version of the given payload which establishes an
    "output" slot in addition to the base slots, holding a string
    consisting of all output that was printed during the execution of
    the original payload (specifically, anything that would have been
    written to stdout). During payload execution, the captured text is
    not actually printed as it would normally have been. If the payload
    itself already established an "output" slot, that value will be
    discarded in favor of the value established by this mix-in.

    If `capture_errors` is set to True, then any `Exception` generated
    by running the original payload will be captured as part of the
    string output instead of bubbling out to the rest of the system.
    However, context slots established by inner payload wrappers cannot
    be retained if there is an `Exception` seen by this wrapper, since
    any inner wrappers would not have gotten a chance to return in that
    case. If an error is captured, an "error" context slot will be set to
    the message for the exception that was caught.

    If `capture_stderr` is set to True, then things printed to stderr
    will be captured as well as those printed to stdout, and will be put
    in a separate "error_log" slot. In this case, if `capture_errors` is
    also True, the printed part of any traceback will be captured as part
    of the error_log, not the output.
    """
    def capturing_payload(context):
        """
        Runs a base payload while also capturing printed output into an
        "output" slot.
        """
        # Set up output capturing
        original_stdout = sys.stdout
        string_stdout = io.StringIO()
        sys.stdout = string_stdout

        if capture_stderr:
            original_stderr = sys.stderr
            string_stderr = io.StringIO()
            sys.stderr = string_stderr

        # Run the base payload
        try:
            result = payload(context)
        except Exception as e:
            if capture_errors:
                if capture_stderr:
                    string_stderr.write('\n' + html_tools.string_traceback())
                else:
                    string_stdout.write('\n' + html_tools.string_traceback())
                result = { "error": str(e) }
            else:
                raise
        finally:
            # Restore original stdout/stderr
            sys.stdout = original_stdout
            if capture_stderr:
                sys.stderr = original_stderr

        # Add our captured output to the "output" slot of the result
        result["output"] = string_stdout.getvalue()

        if capture_stderr:
            result["error_log"] = string_stderr.getvalue()

        return result

    return capturing_payload


def with_fake_input(payload, inputs, extra_policy="error"):
    """
    Creates a modified payload function which runs the given payload but
    supplies a pre-determined sequence of strings whenever `input` is
    called instead of actually prompting for values from stdin. The
    prompts and input values that would have shown up are still printed,
    although a pair of zero-width word-joiner characters is added before
    and after the fake input value at each prompt in the printed output.

    The `inputs` and `extra_policy` arguments are passed to
    `create_mock_input` to create the fake input setup.

    The result will have "inputs" and "input_policy" context slots added
    that store the specific inputs used, and the extra input policy.
    """
    # Create mock input function and input reset function
    mock_input, reset_input = create_mock_input(inputs, extra_policy)

    def fake_input_payload(context):
        """
        Runs a base payload with a mocked input function that returns
        strings from a pre-determined sequence.
        """
        # Replace `input` with our mock version
        import builtins
        original_input = builtins.input
        reset_input()
        builtins.input = mock_input

        # TODO: Is this compatible with optimism's input-manipulation?
        # TODO: Make this work with optimism's stdin-replacement

        # Run the payload
        try:
            result = payload(context)
        finally:
            # Re-enable `input`
            builtins.input = original_input
            reset_input()
            reset_input()

        # Add "inputs" and "input_policy" context slots to the result
        result["inputs"] = inputs
        result["input_policy"] = extra_policy

        return result

    return fake_input_payload


FAKE_INPUT_PATTERN = (
    "\u2060\u2060((?:[^\u2060]|(?:\u2060[^\u2060]))*)\u2060\u2060"
)
"""
A regular expression which can be used to find fake input values in
printed output from code that uses a mock input. The first group of each
match will be a fake output value.
"""


def strip_mock_input_values(output):
    """
    Given a printed output string produced by code using mocked inputs,
    returns the same string, with the specific input values stripped out.
    Actually strips any values found between paired word-joiner (U+2060)
    characters, as that's what mock input values are wrapped in.
    """
    return re.sub(FAKE_INPUT_PATTERN, "", output)


def create_mock_input(inputs, extra_policy="error"):
    """
    Creates two functions: a stand-in for `input` that returns strings
    from the given "inputs" sequence, and a reset function that resets
    the first function to the beginning of its inputs list.

    The extra_policy specifies what happens if the inputs list runs out:

    - "loop" means that it will be repeated again, ad infinitum.
    - "hold" means that the last value will be returned for all
        subsequent input calls.
    - "error" means an `EOFError` will be raised as if stdin had been
        closed.

    "hold" is the default policy.
    """

    input_index = 0

    def mock_input(prompt=""):
        """
        Function that retrieves the next input from the inputs list and
        behaves according to the extra_inputs_policy when inputs run out:

        - If extra_inputs_policy is "hold," the last input is returned
          repeatedly.

        - If extra_inputs_policy is "loop," the cycle of inputs repeats
          indefinitely.

        - If extra_inputs_policy is "error," (or any other value) an
          EOFError is raised when the inputs run out. This also happens
          if the inputs list is empty to begin with.

        This function prints the prompt and the input that it is about to
        return, so that they appear in printed output just as they would
        have if normal input() had been called.

        To enable identification of the input values, a pair of
        zero-width "word joiner" character (U+2060) is printed directly
        before and directly after each input value. These should not
        normally be visible when the output is inspected by a human, but
        can be searched for (and may also influence word wrapping in some
        contexts).
        """
        nonlocal input_index
        print(prompt, end="")
        if input_index >= len(inputs):
            if extra_policy == "hold":
                if len(inputs) > 0:
                    result = inputs[-1]
                else:
                    raise EOFError
            elif extra_policy == "loop":
                if len(inputs) > 0:
                    input_index = 0
                    result = inputs[input_index]
                else:
                    raise EOFError
            else:
                raise EOFError
        else:
            result = inputs[input_index]
            input_index += 1

        print('\u2060\u2060' + result + '\u2060\u2060')
        return result

    def reset_input():
        """
        Resets the input list state, so that the next call to input()
        behaves as if it was the first call with respect to the mock
        input function defined above (see create_mock_input).
        """
        nonlocal input_index
        input_index = 0

    # Return our newly-minted mock and reset functions
    return mock_input, reset_input


def with_timeout(payload, time_limit=5):
    """
    Creates a modified payload which terminates itself with a
    `TimeoutError` if if takes longer than the specified time limit (in
    possibly-fractional seconds).

    Note that on systems where `signal.SIGALRM` is not available, we
    have no way of interrupting the original payload, and so only after
    it terminates will a `TimeoutError` be raised, making this function
    MUCH less useful.

    Note that the resulting payload function is NOT re-entrant: only one
    timer can be running at once, and calling the function again while
    it's already running re-starts the timer.
    """
    def timed_payload(context):
        """
        Runs a base payload with a timeout, raising a
        `potluck.timeout.TimeoutError` if the function takes too long.

        See `potluck.timeout` for (horrific) details.
        """
        return timeout.with_sigalrm_timeout(time_limit, payload, (context,))

    return timed_payload


def tracing_function_calls(payload, trace_targets, state_function):
    """
    Augments a payload function such that calls to certain functions of
    interest during the payload's run are traced. This ends up creating
    a "trace" slot in the result context, which holds a trace object
    that consists of a list of trace entries.

    The `trace_targets` argument should be a sequence of strings
    identifying the names of functions to trace calls to. It may contain
    tuples, in which case calls to any function named in the tuple will
    be treated as calls to the first function in the tuple, which is
    useful for collapsing aliases like turtle.fd and turtle.forward.

    The `state_function` argument should be a one-argument function,
    which given a function name, captures some kind of state and returns
    a state object (typically a dictionary).

    Each trace entry in the resulting trace represents one function call
    in the outermost scope and is a dictionary with the following keys:

    - fname: The name of the function that was called.
    - args: A dictionary of arguments passed to the function, mapping
        argument names to their values. For calls to C functions (such as
        most built-in functions), arguments are not available, and this
        key will not be present.
    - result: The return value of the function. May be None if the
        function was terminated due to an exception, but there's no way
        to distinguish that from an intentional None return. For calls to
        C functions, this key will not be present.
    - pre_state: A state object resulting from calling the given
        state_function just before the traced function call starts, with
        the function name as its only argument. Calls made during the
        execution of the state function will not be traced.
    - post_state: The same kind of state object, but captured right
        before the return of the traced function.
    - during: A list of trace entries in the same format representing
        traced function calls which were initiated and returned before
        the end of the function call that this trace entry represents.

    Note that to inspect all function calls, the hierarchy must be
    traversed recursively to look at calls in "during" slots.

    Note that for *reasons*, functions named "setprofile" cannot be
    traced. Also note that since functions are identified by name,
    multiple functions with the same name occurring in different modules
    will be treated as the same function for tracing purposes, although
    this shouldn't normally matter.

    Note that in order to avoid tracing function calls made by payload
    augmentation, this augmentation should be applied before others.
    """

    # Per-function-name stacks of open function calls
    trace_stacks = {}

    # The trace result is a list of trace entries
    trace_result = []

    # The stack of trace destinations
    trace_destinations = [ trace_result ]

    # Create our tracing targets map
    targets_map = {}
    for entry in trace_targets:
        if isinstance(entry, tuple):
            first = entry[0]
            for name in entry:
                targets_map[name] = first
        else:
            targets_map[entry] = entry

    def tracer(frame, event, arg):
        """
        A profiling function which will be called for profiling events
        (see `sys.setprofile`). It logs calls to a select list of named
        functions.
        """
        nonlocal trace_stacks, trace_result
        if event in ("call", "return"): # normal function-call or return
            fname = frame.f_code.co_name
        elif event in ("c_call", "c_return"): # call/return to/from C code
            fname = arg.__name__
        else:
            # Don't record any other events
            return

        # Don't ever try to trace setprofile calls, since we'll see an
        # unreturned call when setprofile is used to turn off profiling.
        if fname == "setprofile":
            return

        if fname in targets_map: # we're supposed to trace this one
            fname = targets_map[fname] # normalize function name
            if "return" not in event: # a call event
                # Create new info object for this call
                info = {
                    "fname": fname,
                    "pre_state": state_function(fname),
                    "during": []
                    # args, result, and post_state added elsewhere
                }

                # Grab arguments if we can:
                if not event.startswith("c_"):
                    info["args"] = copy.copy(frame.f_locals)

                # Push this info object onto the appropriate stack
                if fname not in trace_stacks:
                    trace_stacks[fname] = []
                trace_stacks[fname].append(info)

                # Push onto the trace destinations stack
                trace_destinations.append(info["during"])

            else: # a return event
                try:
                    prev_info = trace_stacks.get(fname, []).pop()
                    trace_destinations.pop()
                except IndexError: # no matching call?
                    prev_info = {
                        "fname": fname,
                        "pre_state": None,
                        "during": []
                    }

                # Capture result if we can
                if not event.startswith("c_"):
                    prev_info["result"] = arg

                # Capture post-call state
                prev_info["post_state"] = state_function(fname)

                # Record trace event into current destination
                trace_destinations[-1].append(prev_info)

    def traced_payload(context):
        """
        Runs a payload while tracing calls to certain functions,
        returning the context slots created by the original payload plus
        a "trace" slot holding a hierarchical trace of function calls.
        """
        nonlocal trace_stacks, trace_result, trace_destinations

        # Reset tracing state
        trace_stacks = {}
        trace_result = []
        trace_destinations = [ trace_result ]

        # Turn on profiling
        sys.setprofile(tracer)

        # Run our original payload
        result = payload(context)

        # Turn off tracing
        sys.setprofile(None)

        # add a "trace" slot to the result
        result["trace"] = trace_result

        # we're done
        return result

    return traced_payload


def walk_trace(trace):
    """
    A generator which yields each entry from the given trace in
    depth-first order, which is also the order in which each traced
    function call frame was created. Each item yielded is a trace entry
    dictionary, as described in `tracing_function_calls`.
    """
    for entry in trace:
        yield entry
        yield from walk_trace(entry["during"])


def sampling_distribution_of_results(
    payload,
    slot_map={
        "value": "distribution",
        "ref_value": "ref_distribution"
    },
    trials=50000
):
    """
    Creates a modified payload function that calls the given base payload
    many times, and creates a distribution table of the results: for each
    of the keys in the slot_map, a distribution table will be
    built and stored in a context slot labeled with the corresponding
    value from the slot_map. By default, the "value" and
    "ref_value" keys are observed and their distributions are stored in
    the "distribution" and "ref_distribution" slots.

    Note: this augmentation has horrible interactions with most other
    augmentations, since either the other augmentations need to be
    applied each time a new sample is generated (horribly slow) or they
    will be applied to a payload which runs the base test many many times
    (often not what they're expecting). Accordingly, this augmentation is
    best used sparingly and with as few other augmentations as possible.

    Note that the distribution table built by this function maps unique
    results to the number of times those results were observed across
    all trials, so the results of the payload being augmented must be
    hashable for it to work.

    Note that the payload created by this augmentation does not generate
    any of the slots generated by the original payload.
    """
    def distribution_observer_payload(context):
        """
        Runs many trials of a base payload to determine the distribution
        of results. Stores that distribution under the 'distribution'
        context key as a dictionary with "trials" and "results" keys.
        The "trials" value is an integer number of trials performed, and
        the "results" value is a dictionary that maps distinct results
        observed to an integer number of times that result was observed.
        """
        result = {}

        distributions = {
            slot: {
                "trials": trials,
                "results": {}
            }
            for slot in slot_map
        }

        for _ in range(trials):
            rctx = payload(context)
            for slot in slot_map:
                outcome = rctx[slot]
                target_dist = distributions[slot]
                target_dist["results"][outcome] = (
                    target_dist["results"].get(outcome, 0) + 1
                )

        for slot in slot_map:
            result[slot_map[slot]] = distributions[slot]

        return result

    return distribution_observer_payload


def with_module_decorations(payload, decorations, ignore_missing=False):
    """
    Augments a payload such that before it gets run, certain values in
    the module that's in the "module" slot of the current context are
    replaced with decorated values: the results of running a decoration
    function on them. Then, after the payload is complete, the
    decorations are reversed and the original values are put back in
    place.

    The `decorations` argument should be a map from possibly-dotted
    attribute names within the target module to decoration functions,
    whose results (when given original attribute values as arguments)
    will be used to replace those values temporarily.

    If `ignore_missing` is set to True, then even if a specified
    decoration entry names an attribute which does not exist in the
    target module, an attribute with that name will be created; the
    associated decorator function will receive the special class
    `Missing` as its argument in that case.
    """
    def decorated_payload(context):
        """
        Runs a base payload but first pins various decorations in place,
        undoing the pins afterwards.
        """
        # Remember original values and pin new ones:
        orig = {}
        prefixes = {}

        target_module = context_utils.extract(context, "module")

        # Pin everything, remembering prefixes so we can delete exactly
        # the grafted-on structure if ignore_missing is true:
        for key in decorations:
            if ignore_missing:
                orig[key] = get_dot_attr(
                    target_module,
                    key,
                    NoAttr
                )
                prefixes[key] = dot_attr_prefix(target_module, key)
            else:
                orig[key] = get_dot_attr(target_module, key)

            decorated = decorations[key](orig[key])
            set_dot_attr(target_module, key, decorated)

        # Run the payload with pins in place:
        try:
            result = payload(context)
        finally:
            # Definitely clean afterwards up by unpinning stuff:
            for key in decorations:
                orig_val = orig[key]
                prefix = prefixes.get(key)
                if ignore_missing:
                    if orig_val == NoAttr:
                        if prefix == '':
                            delattr(target_module, key.split('.')[0])
                        else:
                            last_val = get_dot_attr(target_module, prefix)
                            rest_key = key[len(prefix) + 1:]
                            delattr(last_val, rest_key.split('.')[0])
                    else:
                        set_dot_attr(target_module, key, orig_val)
                else:
                    set_dot_attr(target_module, key, orig_val)

        # Now return our result
        return result

    return decorated_payload


#--------------------------------#
# Pinning & decorating functions #
#--------------------------------#

class Missing:
    """
    Class to indicate missing-ness when None is a valid value.
    """
    pass


class Generic:
    """
    Class for creating missing parent objects in `set_dot_attr`.
    """
    pass


class NoAttr:
    """
    Class to indicate that an attribute was not present when pinning
    something.
    """
    pass


def get_dot_attr(obj, dot_attr, default=Missing):
    """
    Gets an attribute from a obj, which may be a dotted attribute, in which
    case bits will be fetched in sequence. Returns the default if nothing is
    found at any step, or throws an AttributeError if no default is given
    (or if the default is explicitly set to Missing).
    """
    if '.' in dot_attr:
        bits = dot_attr.split('.')
        first = getattr(obj, bits[0], Missing)
        if first is Missing:
            if default is Missing:
                raise AttributeError(
                    "'{}' object has no attribute '{}'".format(
                        type(obj),
                        bits[0]
                    )
                )
            else:
                return default
        else:
            return get_dot_attr(first, '.'.join(bits[1:]), default)
    else:
        result = getattr(obj, dot_attr, Missing)
        if result == Missing:
            if default == Missing:
                raise AttributeError(
                    "'{}' object has no attribute '{}'".format(
                        type(obj),
                        dot_attr
                    )
                )
            else:
                return default
        else:
            return result


def dot_attr_prefix(obj, dot_attr):
    """
    Returns the longest prefix of attribute values that are part of the
    given dotted attribute string which actually exists on the given
    object. Returns an empty string if even the first attribute in the
    chain does not exist. If the full attribute value exists, it is
    returned as-is.
    """
    if '.' in dot_attr:
        bits = dot_attr.split('.')
        first, rest = bits[0], bits[1:]
        if hasattr(obj, first):
            suffix = dot_attr_prefix(getattr(obj, first), '.'.join(rest))
            if suffix:
                return first + '.' + suffix
            else:
                return first
        else:
            return ""
    else:
        if hasattr(obj, dot_attr):
            return dot_attr
        else:
            return ""


def set_dot_attr(obj, dot_attr, value):
    """
    Works like get_dot_attr, but sets an attribute instead of getting one.
    Creates instances of Generic if the target attribute lacks parents.
    """
    if '.' in dot_attr:
        bits = dot_attr.split('.')
        g = Generic()
        parent = getattr(obj, bits[0], g)
        if parent == g:
            setattr(obj, bits[0], parent)
        set_dot_attr(parent, '.'.join(bits[1:]), value)
    else:
        setattr(obj, dot_attr, value)


#-------------------#
# Turtle management #
#-------------------#

def warp_turtle(context):
    """
    Disables turtle tracing, and resets turtle state. Use as a setup
    function with `with_setup` and/or via
    `specifications.HasPayload.do_setup`. Note that you MUST also use
    `finalize_turtle` as a cleanup function, or else some elements may
    not actually get drawn.
    """
    turtle.reset()
    turtle.tracer(0, 0)
    return context


def finalize_turtle(result):
    """
    Paired with `warp_turtle`, makes sure that everything gets drawn. Use
    as a cleanup function (see `with_cleanup` and
    `specifications.HasPayload.do_cleanup`).
    """
    turtle.update()
    return result


def capture_turtle_state(_):
    """
    This state-capture function logs the following pieces of global
    turtle state:

    - position: A 2-tuple of x/y coordinates.
    - heading: A floating point number in degrees.
    - pen_is_down: Boolean indicating pen state.
    - is_filling: Boolean indicating whether we're filling or not.
    - pen_size: Floating-point pen size.
    - pen_color: String indicating current pen color.
    - fill_color: String indicating current fill color.

    This state-capture function ignores its argument (which is the name
    of the function being called).
    """
    return {
        "position": turtle.position(),
        "heading": turtle.heading(),
        "pen_is_down": turtle.isdown(),
        "is_filling": turtle.filling(),
        "pen_size": turtle.pensize(),
        "pen_color": turtle.pencolor(),
        "fill_color": turtle.fillcolor()
    }


def capturing_turtle_drawings(payload, skip_reset=False, alt_text=None):
    """
    Creates a modified version of the given payload which establishes an
    "image" slot in addition to the base slots, holding a PILlow image
    object which captures everything drawn on the turtle canvas by the
    time the function ended. It creates an "image_alt" slot with the
    provided alt_text, or if none is provided, it copies the "output"
    slot value as the image alt, assuming that `turtleBeads` has been
    used to create a description of what was drawn.

    The function will reset the turtle state and turn off tracing
    before calling the payload function (see `warp_turtle`). It will
    also update the turtle canvas before capturing an image (see
    `finalize_turtle`). So you don't need to apply those as
    setup/cleanup functions yourself. If you want to disable the
    automatic setup/cleanup, set the skip_reset argument to False,
    although in that case tracing will still be disabled and one update
    will be performed at the end.

    In default application order, the turtle reset/setup from this
    function is applied before any setup functions set using
    `with_setup`, and the output image is captured after any cleanup
    functions set using `with_cleanup` have been run, so you could for
    example apply a setup function that moves the turtle to a
    non-default starting point to test the flexibility of student code.

    Note: you must have Pillow >=6.0.0 to use this augmentation, and you
    must also have Ghostscript installed (which is not available via
    PyPI, although most OS's should have a package manager via which
    Ghostscript can be installed)!
    """
    # Before we even build our payload, verify that PIL will be
    # available (we let any exception bubble out naturally).
    import PIL
    # Check for full Ghostscript support necessary to read EPS
    import PIL.EpsImagePlugin as p
    if not p.has_ghostscript():
        raise NotImplementedError(
            "In order to capture turtle drawings, you must install"
            " Ghostscript (which is not a Python package) manually."
        )

    def capturing_payload(context):
        """
        Resets turtle state, disables tracing, runs a base payload, and
        then captures what was drawn on the turtle canvas as a PILlow
        image.
        """
        # Reset turtle & disable tracing
        if skip_reset:
            turtle.tracer(0, 0)
        else:
            context = warp_turtle(context)

        # Run the base payload
        result = payload(context)

        # Ensure all drawing is up-to-date
        # Note: this if/else is future-proofing in case finalize_turtle
        # needs to do more in the future.
        if skip_reset:
            turtle.update()
        else:
            result = finalize_turtle(result)

        # capture what's on the turtle canvas as a PILlow image
        canvas = turtle.getscreen().getcanvas()

        # Capture postscript commands to recreate the canvas
        ps = canvas.postscript()

        # Wrap as if it were a file and Use Ghostscript to turn the EPS
        # into a PIL image
        bio = io.BytesIO(ps.encode(encoding="utf-8"))
        captured = PIL.Image.open(bio, formats=["EPS"])

        # Convert to RGB mode if it's not in that mode already
        if captured.mode != "RGB":
            captured = captured.convert("RGB")

        # Add our captured image to the "image" slot of the result
        result["image"] = captured

        # Add alt text
        if alt_text is not None:
            result["image_alt"] = alt_text
        else:
            result["image_alt"] = result.get(
                "output",
                "no alt text available"
            )

        return result

    return capturing_payload


#----------------------#
# Wavesynth management #
#----------------------#

_PLAY_WAVESYNTH_TRACK = None
"""
The original wavesynth playTrack function, stored here temporarily while
it's disabled via `disable_track_actions`.
"""

_SAVE_WAVESYNTH_TRACK = None
"""
The original wavesynth saveTrack function, stored here temporarily when
saveTrack is disabled via `disable_track_actions`.
"""


def disable_track_actions():
    """
    Disables the `playTrack` and `saveTrack` `wavesynth` functions,
    turning them into functions which accept the same arguments and
    simply instantly return None. This helps ensure that students'
    testing calls to `saveTrack` or `playTrack` don't eat up evaluation
    time. Saves the original functions in the `_PLAY_WAVESYNTH_TRACK` and
    `_SAVE_WAVESYNTH_TRACK` global variables.

    Only saves original functions the first time it's called, so that
    `reenable_track_actions` will work even if `disable_track_actions` is
    called multiple times.

    Note that you may want to use this function with
    `specifications.add_module_prep` to ensure that submitted code
    doesn't try to call `playTrack` or `saveTrack` during import and
    waste evaluation time.
    """
    global _PLAY_WAVESYNTH_TRACK, _SAVE_WAVESYNTH_TRACK
    import wavesynth
    if _PLAY_WAVESYNTH_TRACK is None:
        _PLAY_WAVESYNTH_TRACK = wavesynth.playTrack
        _SAVE_WAVESYNTH_TRACK = wavesynth.saveTrack
    wavesynth.playTrack = lambda wait=None: None
    wavesynth.saveTrack = lambda filename: None


def reenable_track_actions():
    """
    Restores the `saveTrack` and `playTrack` functions after
    `disable_track_actions` has disabled them.
    """
    global _PLAY_WAVESYNTH_TRACK, _SAVE_WAVESYNTH_TRACK
    import wavesynth
    if _PLAY_WAVESYNTH_TRACK is not None:
        wavesynth.playTrack = _PLAY_WAVESYNTH_TRACK
        wavesynth.saveTrack = _SAVE_WAVESYNTH_TRACK
        _PLAY_WAVESYNTH_TRACK = None
        _SAVE_WAVESYNTH_TRACK = None


def ensure_or_stub_simpleaudio():
    """
    Tries to import the `simpleaudio` module, and if that's not possible,
    creates a stub module named "simpleaudio" which raises an attribute
    error on any access attempt. The stub module will be inserted in
    `sys.modules` as if it were `simpleaudio`.

    Note that you may want to set this up as a prep function using
    `specifications.add_module_prep` to avoid crashing if submitted code
    tries to import `simpleaudio` (although it will still crash if
    student code tries to use anything from `simpleaudio`).
    """
    # We also try to import simpleaudio, but set up a dummy module in its
    # place if it's not available, since we don't need or want to play
    # the sounds for grading purposes.
    try:
        import simpleaudio # noqa F401
    except Exception:
        def missing(name):
            """
            Fake getattr to raise a reasonable-seeming error if someone
            tries to use our fake simpleaudio.
            """
            raise AttributeError(
                "During grading, simpleaudio is not accessible. We have"
                " disabled playTrack and saveTrack for testing purposes"
                " anyway, and your code should not need to use"
                " simpleaudio directly either."
            )
        fake_simpleaudio = imp.new_module("simpleaudio")
        fake_simpleaudio.__getattr__ = missing
        sys.modules["simpleaudio"] = fake_simpleaudio


def capturing_wavesynth_audio(payload, just_capture=None, label=None):
    """
    Creates a modified version of the given payload which establishes
    "notes" and "audio" slots in addition to the base slots. "notes"
    holds the result of `wavesynth.trackDescription` (a list of strings)
    while "audio" holds a dictionary with the following keys:

    - "mimetype": The MIME type for the captured data.
    - "data": The captured binary data, as a bytes object.
    - "label": A text label for the audio, if a 'label' value is
        provided; not present otherwise

    The data captured is the WAV format audio that would be saved by the
    wavesynth module's `saveTrack` function, which in particular means
    it only captures whatever is in the "current track." The
    `resetTracks` function is called before the payload is executed, and
    again afterwards to clean things up.

    If the `wavesynth` module is not installed, a `ModuleNotFoundError`
    will be raised.
    """
    # Before we even build our payload, verify that wavesynth will be
    # available (we let any exception bubble out naturally).
    import wavesynth

    # We do this here just in case student code attempts to use
    # simpleaudio directly, since installing simpleaudio for evaluation
    # purposes shouldn't be necessary.
    ensure_or_stub_simpleaudio()

    def capturing_payload(context):
        """
        Resets all tracks state, runs a base payload, and then captures
        what was put into the current track as both a list of note
        descriptions and as a dictionary indicating a MIME type, raw
        binary data, and maybe a label.
        """
        # Reset all tracks
        wavesynth.resetTracks()

        # Disable playTrack and saveTrack
        disable_track_actions()

        # Run the base payload
        try:
            result = payload(context)
        finally:
            reenable_track_actions()

        # capture the descriptions of the notes in the current track
        if just_capture in (None, "notes"):
            result["notes"] = wavesynth.trackDescription()

        # capture what's in the current track as raw WAV bytes
        if just_capture in (None, "audio"):
            bio = io.BytesIO()
            wavesynth.saveTrack(bio)
            data = bio.getvalue()

            # Add our captured audio to the "audio" slot of the result
            result["audio"] = {
                "mimetype": "audio/wav",
                "data": data,
            }

            # Add a label
            if label is not None:
                result["audio"]["label"] = label

        # Reset all tracks (again)
        wavesynth.resetTracks()

        return result

    return capturing_payload


#---------------------------------#
# Miscellaneous harness functions #
#---------------------------------#

def report_argument_modifications(target, *args, **kwargs):
    """
    This function works as a test harness but doesn't capture the value
    or output of the function being tested. Instead, it generates a text
    report on whether or not each mutable argument to the function was
    modified or not after the function is finished. It only checks
    arguments which are are lists or dictionaries at the top level, so
    its definition of modifiable is rather narrow.

    (Note: the last two paragraphs of this docstring are picked up
    automatically as rubric values for tests using this harness. fname
    will be substituted in, which is why it appears in curly braces
    below.)

    Description:

    <code>{fname}</code> must only modify arguments it is supposed to
    modify.

    We will call <code>{fname}</code> and check to make sure that the
    values provided as arguments are not changed by the function, except
    where such changes are explicitly required. Note that only mutable
    values, like dictionaries or lists, may be modified by a function, so
    this check is not applied to any string or number arguments.
    """
    # Identify mutable arguments
    mposargs = [
        i
        for i in range(len(args))
        if isinstance(args[i], (list, dict))
    ]
    mkwargs = [k for k in kwargs if isinstance(kwargs[k], (list, dict))]
    if target.__kwdefaults__ is not None:
        mkwdefaults = [k for k in target.__kwdefaults__ if k not in kwargs]
    else:
        mkwdefaults = []
    nargs = target.__code__.co_argcount + target.__code__.co_kwonlyargcount
    margnames = [target.__code__.co_varnames[:nargs][i] for i in mposargs]
    mposnames = margnames[:len(mposargs)]
    mposvals = [copy.deepcopy(args[i]) for i in mposargs]
    mkwvals = [copy.deepcopy(kwargs[k]) for k in mkwargs]
    mkwdefvals = {
        k: copy.deepcopy(target.__kwdefaults__[k])
        for k in mkwdefaults
    }

    # Call the target function
    _ = target(*args, **kwargs)

    # Report on which arguments were modified
    result = ""

    # Changes in positional argument values
    for argindex, orig in zip(mposargs, mposvals):
        final = args[argindex]
        name = mposnames[argindex]
        result += "Your code {} the value of the '{}' argument.\n".format(
            "modified" if orig != final else "did not modify",
            name
        )

    # Changes in keyword argument values
    for name, orig in zip(mkwargs, mkwvals):
        final = kwargs[name]
        result += "Your code {} the value of the '{}' argument.\n".format(
            "modified" if orig != final else "did not modify",
            name
        )

    # Changes in values of unsupplied keyword arguments (i.e., changes to
    # defaults, which if unintentional is usually bad!)
    for name, orig in zip(mkwdefaults, mkwdefvals):
        final = target.__kwdefaults__[name]
        result += "Your code {} the value of the '{}' argument.\n".format(
            "modified" if orig != final else "did not modify",
            name
        )

    # The report by default will be compared against an equivalent report
    # from the solution function, so that's how we figure out which
    # arguments *should* be modified or not.
    return result


def returns_a_new_value(target, *args, **kwargs):
    """
    Checks whether or not the target function returns a value which is
    new (i.e., not the same object as one of its arguments). Uses the
    'is' operator to check for same-object identity, so it will catch
    cases in which an object is modified and then returned. Returns a
    string indicating whether or not a newly-constructed value is
    returned.

    Note: won't catch cases where the result is a structure which
    *includes* one of the arguments. And does not check whether the
    result is equivalent to one of the arguments, just whether it's
    actually the same object or not.

    (Note: the last two paragraphs of this docstring are picked up
    automatically as rubric values for tests using this harness. fname
    will be substituted in, which is why it appears in curly braces
    below.)

    Description:

    <code>{fname}</code> must return a new value, rather than returning
    one of its arguments.

    We will call <code>{fname}</code> and check to make sure that the
    value it returns is a new value, rather than one of the arguments it
    was given (modified or not).
    """
    # Call the target function
    fresult = target(*args, **kwargs)

    # Check the result against each of the arguments
    nargs = target.__code__.co_argcount + target.__code__.co_kwonlyargcount
    for argindex, argname in enumerate(target.__code__.co_varnames[:nargs]):
        if argindex < len(args):
            # a positional argument
            argval = args[argindex]
        else:
            # a keyword argument (possibly defaulted via omission)
            argval = kwargs.get(argname, target.__kwdefaults__[argname])

        if fresult is argval:
            return (
                "Returned the '{}' argument (possibly with modifications)."
            ).format(argname)

    # Since we didn't return in the loop above, there's no match
    return "Returned a new value."


#------------------#
# File I/O Helpers #
#------------------#

def file_contents_setter(filename, contents):
    """
    Returns a setup function (use with `with_setup`) which replaces the
    contents of the given file with the given contents. Be careful,
    because this will happily overwrite any file. If the desired contents
    is a bytes object, the file will be written in binary mode to contain
    exactly those bytes, otherwise contents should be a string.
    """
    def setup_file_contents(context):
        """
        Returns the provided context as-is, but before doing so, writes
        data to a specific file to set it up for the coming test.
        """
        if isinstance(contents, bytes):
            with open(filename, 'wb') as fout:
                fout.write(contents)
        else:
            with open(filename, 'w') as fout:
                fout.write(contents)
        return context

    return setup_file_contents


def capturing_file_contents(payload, filename, binary=False):
    """
    Captures the entire contents of the given filename as a string (or a
    bytes object if binary is set to True), and stores it in the
    "output_file_contents" context slot. Also stores the file name of the
    file that was read in in the "output_filename" slot.
    """
    def capturing_payload(context):
        """
        Runs a base payload and then reads the contents of a specific
        file, adding that data as a "output_file_contents" context slot
        and also adding an "output_filename" slot holding the filename
        that was read from.
        """
        # Run base payload
        result = payload(context)

        # Record filename in result
        result["output_filename"] = filename

        # Decide on open flags
        if binary:
            flags = 'rb'
        else:
            flags = 'r'

        with open(filename, flags) as fin:
            file_contents = fin.read()

        # Add file contents
        result["output_file_contents"] = file_contents

        return result

    return capturing_payload
