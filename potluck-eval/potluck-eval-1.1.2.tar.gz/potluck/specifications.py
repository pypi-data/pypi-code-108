"""
High-level code for defining task specifications.

specifications.py

This is a layer on top of the `potluck.rubrics.Goal` classes and the
`potluck.contexts.Context` classes; if more direct control is needed
those modules can be used alongside this one.

Note that to define a specification, you'll need an evaluation directory
set up (see the top-level `README.md`) and you'll need to create a
`spec.py` file in a task-specific directory, as well as editing
`tasks.json` to define the task's meta-data.

## Example

Note: You can find this example in the "functionsTest" task defined in
the "potluck_testarea/test_course/fall2021" directory's specs.

Let's assume that an assignment requests that a student write the
following functions (this is the solution code):

```py
def indentMessage(message, targetLength):
    indent = max(0, targetLength - len(message))
    return ' ' * indent + message

def printMessage(message, targetLength):
    print(indentMessage(message, targetLength))

import math

def ellipseArea(radius1, radius2):
    return radius1 * radius2 * math.pi

from turtle import *

def polygon(sideLength, nSides):
    for i in range(nSides):
        fd(sideLength)
        lt(360 / nSides)
```

A spec for the task that includes these functions might include the
following code to both run unit tests and check implementation choices:

```py
import turtle

from potluck import specifications as spec
from potluck import compare
from potluck import harness

# Define a few simple unit tests
# Note each TestCase created in this loop will be part of a TestGroup for
# the function it's testing.
for case in [ ("hello", 10), ("hi", 12) ]:
    spec.TestCase("indentMessage", case)
    spec.TestCase("printMessage", case)

# These tests don't get grouped with the test cases above because they
# have an explicit non-default group name.
spec.TestCase("indentMessage", ("longword", 4), group_name="advanced")
spec.TestCase("printMessage", ("longword", 4), group_name="advanced")

# Tests in this loop will again form a TestGroup
for case in [ (5, 5), (5, 10), (12.6, 7.3) ]:
    spec.TestCase("ellipseArea", case)


# Tests in this loop are also grouped
for case in [ (90, 4), (50, 5), (30, 12) ]:
    spec.TestCase("polygon", case)

# Extra test case that doesn't start at the origin
spec.TestCase("polygon", (40, 6), group_name="advanced").do_setup(
    lambda context: (turtle.lt(45), turtle.fd(20), context)[-1]
)


# Build two goals based on our TestCases for "indentMessage"
spec.group("indentMessage").goal("core")
spec.group("indentMessage", group_name="advanced").goal("extra")

# Similar goals for printMessage, but here we need to go beyond the
# default (test values for strict equality, as a "product"-type goal) and
# test outputs. Note that the comparator for the core goal will pass with
# whitespace-only differences, which doesn't make sense for this function
# except that we're testing indentation explicitly in a separate goal.
spec.group("printMessage").test_output().goal("core").compare_strings_firmly()
spec.group("printMessage", "advanced").test_output().goal("extra")

# Here we create and refine our core printMessage tests to look just at
# the initial whitespace. Here we need to compare exactly, since
# whitespace-only differences shouldn't be treated as partial successes.
spec.group("printMessage").test_output()\
    .refine(spec.Find, pattern="^ *", pattern_desc="the indentation")\
    .goal("core")\
    .compare_exactly()\
    .set_goal_description(
        (
            (
                " <code>printMessage</code> uses correct indentation"
            ),
            (
                "We will verify that <code>printMessage</code> includes"
                " the correct number of spaces before the message itself."
            ),
            (
                " <code>printMessage</code> uses correct indentation"
            ),
            (
                "We checked whether <code>printMessage</code> included"
                " the correct number of spaces before the message itself."
            ),
        )
    )


# A comparison function that will treat two numbers as equal if they
# agree to 3 significant figures:
fequals = compare.build_float_equality_checker(3)
# A goal for ellipseArea that uses this equality checker
spec.group("ellipseArea").goal("core").compare_using(fequals)
# Note: this is usually unnecessary as the default comparator tries to
# ignore floating-point rounding errors...


# For polygon, we'll trace calls to forward and to polygon itself
to_trace = [ "polygon", ("fd", "forward") ]
core_state = [ "position", "heading" ]
traces = spec.group("polygon")\\
    .goal("core")\\
    .do_setup(harness.warp_turtle)\\
    .do_cleanup(harness.finalize_turtle)\\
    .test_trace(to_trace, harness.capture_turtle_state)\\
    .check_trace_state(core_state, check_args=True, only=["fd"])
adv_traces = spec.group("polygon", "advanced")\\
    .goal("extra")\\
    .do_setup(harness.warp_turtle)\\
    .do_cleanup(harness.finalize_turtle)\\
    .test_trace(to_trace, harness.capture_turtle_state)\\
    .check_trace_state(core_state, check_args=True, only=["fd"])

# check that the position and heading of the turtle are the same
# before/after the call to polygon.
traces.also()\\
    .goal("core")\\
    .check_invariant(core_state, only=["polygon"])
adv_traces.also()\\
    .goal("extra")\\
    .check_invariant(core_state, only=["polygon"])

# Implementation checks: functions must be defined and must use certain
# constructs internally. Note that the second argument to FunctionDef
# should usually be omitted, and can either be an integer requiring a
# specific number of parameters or a string specifying parameters names
# in `evaluation.mast` style (e.g., "firstArg, _, thirdArg").
spec.FunctionDef("indentMessage", 2).require(
    spec.FunctionCall("len")
)
spec.FunctionDef("printMessage").require(
    spec.FunctionCall("print"),
    spec.FunctionCall("indentMessage")
)
spec.FunctionDef("ellipseArea").require(
    spec.Return()
)
spec.FunctionDef("polygon").require(
    spec.Loop(only="block").require(
        spec.FunctionCall(["fd", "forward"]) # must be in the loop
    )
)

# Misc goals

spec.NoParseErrors()
spec.DontWasteFruit()
spec.DontWasteBoxes()
spec.RequireDocstrings()
```

Customization of tests is achieved through the methods of the `TestCase`,
`TestGroup`, `TestGoal`, `Check`, and related classes (and through the
use of `Check` subclasses). In the code above we used functions like
`HasGoal.compare_using` and `Check.require` to refine tests.

Once you have constructed some `TestGoal` and/or `Check` objects, simply
write:

```py
rubric = spec.rubric()
```

...and a `potluck.rubrics.Rubric` object will be created from the tests
that you've defined in the current module.

As long as your specification file defines a variable named `rubric`
which holds a `potluck.rubrics.Rubric` object, it will be usable.


## Testing your Specifications

How can you be sure your specifications will work correctly? There is a
built-in specifications checking system that can both check your
specification against example submissions, as well as make sure that the
solution code gets a perfect score. Running `potluck_eval` with the
`--check` option invokes this system for a particular task. By default it
will check just the solution code, but you may also provide example
submissions and then set up expectations for them other than perfect
success. To do this you can use the `potluck.meta` module's
`potluck.meta.example` and `potluck.meta.expect` functions. Here's an
example of what this might look like for the specification example above:

```py
# Specifications tests using the meta module:
from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect("partial", "style", "core", "documented")
meta.expect("partial", "style", "extra", "ignore the results")
meta.expect("failed", "procedure", "core", "define printMessage")
meta.expect("accomplished", "procedure", "core", "define printMessage",
            "call print")
meta.expect("failed", "procedure", "core", "define printMessage",
            "call indentMessage")
meta.expect("failed", "procedure", "core", "define polygon")
meta.expect("failed", "procedure", "core", "define polygon", "loop")
meta.expect("failed", "procedure", "core", "define polygon", "loop", "call")
meta.expect("failed", "process", "core", "correct function calls")
meta.expect("failed", "process", "core", "maintain invariants")
meta.expect("failed", "process", "extra", "correct function calls")
meta.expect("failed", "process", "extra", "maintain invariants")
meta.expect("failed", "product", "core", "ellipseArea")
meta.expect("failed", "behavior", "core", "correct indentation")
meta.expect("failed", "behavior", "extra", "correct output")
```

These expectations are based on the following broken submission:

```py
def indentMessage(message, targetLength):
    len(message)
    indent = targetLength - len(message)
    return ' ' * indent + message

def printMessage(message, width):
    '''
    Prints a message, taking up at least the required width (will be
    wider if the message itself is wider). Uses indentMessage.
    '''
    print(' ' * width + message)

import math

def ellipseArea(radius1, radius2):
    '''
    Computes the area of an ellipse with the given radii (you may specify
    the major and minor radii in either order). Returns the result as a
    floating-point number.
    '''
    return radius1 * radius2 + math.pi

from turtle import *

def polygon(sideLength, nSides):
    '''
    Draws a polygon with the given side length and number of sides.
    '''
    for _ in range(nSides + 1):
        bk(sideLength)
        lt(360 / nSides)
```

## Multi-file tasks (experimental)

If you want to grade a submission with multiple files, or otherwise use
more-than-default contexts for things like loading the submitted code,
you can instantiate a `contexts.FileContext` object pointing to one of
the files you want to grade, instantiate various tests for that file, and
then instantiate another file context for the next file to grade,
followed by tests for that file, and so on. Essentially, when a test or
check is created, it picks up some of the currently-registered auto
contexts (see `contexts.auto`), most notably `filename`, and so by
controlling the filename specified by the most-recently-instantiated
`contexts.FileContext`, you can control which file tests are applied to.
(TODO: test that!).
"""
# TODO: property -> payload -> condition description assembly...

import ast
import re
import copy

from . import logging
from . import mast
from . import rubrics
from . import contexts
from . import context_utils
from . import patterns
from . import phrasing
from . import html_tools
from . import compare
from . import explain
from . import harness
from . import file_utils
from . import validation


#---------#
# Globals #
#---------#

SPECS_DIR = '.'
"""
Directory for finding task specifications.
"""


CONTEXT_SLOT_IMPLIED_TYPES = {
    "filename": "other",
    "file_path": "other",
    "source": "style",
    "docstrings": "style",
    "parse_errors": "procedure",
    "defs": "procedure",
    "top_scope": "procedure",
    "scope": "procedure",
    "module": "product",
    "trace": "process",
    "value": "product",
    "output": "behavior",
    "output_file_contents": "behavior",
    "image": "behavior",
    "audio": "behavior",
    "notes": "behavior",
}
"""
Based on just the context slot being used for testing with an
`potluck.rubrics.ComparisonTest`, we can guess the goal type that the
goal will fall into. This dictionary stores those associations. Use
`HasGoal.set_goal_type` to set a goal type explicitly if the default
isn't correct.
"""


#------------#
# Registries #
#------------#

# A registry of TestGroup instances, organized according to the module
# they were instantiated within, their rubric category, and the name of
# the function they apply to.
# Keys by level are:
#   1. A module's __name__
#   2. A filename
#   3. A function name
#   4. A custom group name
# Ultimate values are `TestGroup` objects.
TEST_GROUP_REGISTRY = {}

# A registry of Check instances, organized according to the module they
# were instantiated within. Each key is a module's __name__ and maps to a
# list of Check objects.
CHECKS_REGISTRY = {}

# A mapping from module names to lists of HasGoal instances which will be
# called upon to provide goals for the rubric when it gets created.
GOAL_PROVIDERS = {}

# A mapping from module names to lists of Goal objects that should be
# added to the rubric when it gets created.
GOALS = {}

# Just like GOAL_PROVIDERS, but for goal providers that should be used
# to set up goals for the test validation process.
VALIDATION_GOAL_PROVIDERS = {}

# Just like GOALS, but for goals which apply to the test validation
# process.
VALIDATION_GOALS = {}


def register_goal_provider(provider):
    """
    Registers a goal-provider (must have a zero-parameter `provide_goal`
    method, so most likely to be a `HasGoal` instance) to provide a goal
    to the rubric. Mostly this is handled automatically via
    `HasGoal.goal`, but it's useful to call it manually in some cases.
    """
    sname = file_utils.get_spec_module_name()
    if sname not in GOAL_PROVIDERS:
        GOAL_PROVIDERS[sname] = []
    GOAL_PROVIDERS[sname].append(provider)


def register_goal(goal):
    """
    Registers a goal to be added to the rubric. Mostly this is handled
    automatically, but it's useful to call it manually if you want to
    define your own custom goals in tandem with automatically-created goals.
    """
    sname = file_utils.get_spec_module_name()
    if sname not in GOALS:
        GOALS[sname] = []
    GOALS[sname].append(goal)


def register_validation_goal_provider(provider):
    """
    Registers a goal-provider (must have a zero-parameter `provide_goal`
    method, so most likely to be a `HasGoal` instance) to provide a goal
    to the rubric's test validation stage. Mostly this is handled
    automatically via `HasGoal.validate`, but it's useful to call it
    manually in some cases.
    """
    sname = file_utils.get_spec_module_name()
    if sname not in VALIDATION_GOAL_PROVIDERS:
        VALIDATION_GOAL_PROVIDERS[sname] = []
    VALIDATION_GOAL_PROVIDERS[sname].append(provider)


def register_validation_goal(goal):
    """
    Registers a goal to be added to the rubric. Mostly this is handled
    automatically, but it's useful to call it manually if you want to
    define your own custom goals in tandem with automatically-created goals.
    """
    sname = file_utils.get_spec_module_name()
    if sname not in VALIDATION_GOALS:
        VALIDATION_GOALS[sname] = []
    VALIDATION_GOALS[sname].append(goal)


def checklist(category, goal_type, create=False):
    """
    Retrieves the list of `Check` objects which have been registered
    under the given category and goal type. Raises a `KeyError` if no
    checks have been registered under that category, or if create is
    True, it creates an entry for that category and returns an empty
    list.
    """
    mname = file_utils.get_spec_module_name()
    module_registry = CHECKS_REGISTRY.get(mname)

    if module_registry is None:
        if create:
            module_registry = CHECKS_REGISTRY.setdefault(mname, {})
        else:
            raise KeyError(
                f"There are no checks for module {mname}."
            )

    category_registry = module_registry.get(category)

    if category_registry is None:
        if create:
            category_registry = module_registry.setdefault(category, {})
        else:
            raise KeyError(
                f"There are no checks in module {mname} for category"
              + f" {category}."
            )

    list_for_type = category_registry.get(goal_type)

    if list_for_type is None:
        if create:
            list_for_type = category_registry.setdefault(goal_type, [])
        else:
            raise KeyError(
                f"There are no checks in module {mname} for category"
              + f" {category} and type {goal_type}."
            )

    return list_for_type


#------------------------------------------------#
# Base classes for payload/context/goal managers #
#------------------------------------------------#

def update_augmentations(base, extensions):
    """
    Takes two dictionaries and updates the first with the key/value
    pairs from the second, with special treatment of "with_setup" and
    "with_cleanup" keys so that setup/cleanup functions are accumulated
    via composition rather than overriding each other.

    Edits the first dictionary but doesn't have a return value.
    """
    for key in extensions:
        if (
            key in ("with_setup", "with_cleanup")
        and key in base
        ):
            keyarg = key[5:]
            already = base[key][keyarg]
            incomming = extensions[key][keyarg]
            base[key] = {
                keyarg: lambda val: incomming(already(val))
            }
        else:
            base[key] = extensions[key]


class HasPayload:
    """
    An abstract base class for tests that track payload augmentations,
    since the augmentation system allows for common functionality.
    """
    def __init__(
        self,
        payload_constructor=harness.create_run_function_payload,
        default_payload_args=None,
        default_augmentations=None
    ):
        """
        A base payload creation function may be supplied (default is
        `potluck.harness.create_run_function_payload`).

        Defaults for payload arguments and/or augmentations may be
        supplied. Payload arguments are just passed as keyword arguments
        to the payload constructor.

        Augmentations should be a dictionary where keys name payload
        augmentation functions in the `potluck.harness` module, and
        values are dictionaries of keyword arguments to supply to those
        augmentations.
        """
        self.payload_constructor = payload_constructor
        self.default_payload_args = default_payload_args or {}
        self.default_augmentations = default_augmentations or {}
        self.payload_args = {}
        self.augmentations = {}

    def synthesize_payload_info(self, group=None):
        """
        Synthesizes payload construction arguments and augmentations,
        returning a tuple containing the results in that order. If a
        group is given, it should also be a `HasPayload` instance, and
        its information will be mixed with local information as follows:

          - First, group defaults will be loaded.
          - Next, this object's defaults will override those.
          - Third, group explicit values will be added.
          - Finally, local explicit values will have the final say.

        Note: setup and cleanup functions accumulate via composition
        rather than replacing each other.
        """
        args = {}
        augmentations = {}
        if group:
            args.update(group.default_payload_args)
            augmentations.update(group.default_augmentations)
        args.update(self.default_payload_args)
        update_augmentations(augmentations, self.default_augmentations)
        if group:
            args.update(group.payload_args)
            update_augmentations(augmentations, group.augmentations)
        args.update(self.payload_args)
        update_augmentations(augmentations, self.augmentations)

        return args, augmentations

    def construct_payload(self, parent=None):
        """
        Constructs the augmented payload function based on the
        information assembled so far.
        """
        # Synthesize payload arguments & augmentations
        args, augmentations = self.synthesize_payload_info(parent)

        # Construct base payload
        # TODO: less awkward here?
        # TODO NOT a HACK here!
        if (
            hasattr(parent, "payload_constructor")
        and parent.payload_constructor == harness.create_run_harness_payload
        ):
            cons = parent.payload_constructor
        else:
            cons = self.payload_constructor

        result = cons(**args)

        # Apply augmentations in order
        for fn_name in harness.AUGMENTATION_ORDER:
            if fn_name in augmentations:
                args = augmentations[fn_name]
                result = getattr(harness, fn_name)(result, **args)

        return result

    def describe_payload(self, parent=None, obfuscated=False):
        """
        Returns a pair of HTML strings for the topic and details of the
        payload that will be constructed by `construct_payload` (with an
        equivalent `parent` argument). If `obfuscated` is set to True,
        the obfuscated version of the description will be provided (see
        `potluck.explain.payload_description`)
        """
        # Synthesize info w/ parent
        args, augmentations = self.synthesize_payload_info(parent)
        return explain.payload_description(
            self.payload_constructor,
            args,
            augmentations,
            obfuscated=obfuscated
        )

    def ensure_payload_constructor_arg(self, desired):
        """
        Ensures that this object's payload constructor accepts the given
        argument value, raising a `TypeError` if it does not.
        """
        cobj = self.payload_constructor.__code__
        arg_names = cobj.co_varnames[:cobj.co_argcount]
        if desired not in arg_names:
            raise TypeError(
                f"This operation is only allowed for HasPayload classes"
                f" associated with payload bases that accept a '{desired}'"
                f" argument ({self.payload_constructor.__name__} does not)."
            )

    def prepare_source(self, prep):
        """
        Provides a prep function which will be run on the source code of
        the module being tested before the test. Only applicable to
        module import payloads. The string it returns will be used as the
        actual module source. Even if you don't need to modify the source
        code, this can be used to run some setup code right before the
        test itself.

        This function returns self for chaining.
        """
        self.ensure_payload_constructor_arg("prep")
        self.payload_args["prep"] = prep
        return self

    def wrap_module(self, wrapper):
        """
        Provides a wrapper function which will be applied to the module
        created by this test before the final checking step. Only
        applicable to module import payloads (use `use_decorations` to
        achieve a similar effect for other payload types). Mostly
        relevant when the `module` slot is being used somehow, such as
        when `HasGoal.test_module` is being used.

        This function returns self for chaining.
        """
        self.ensure_payload_constructor_arg("wrap")
        self.payload_args["wrap"] = wrapper
        return self

    def ignore_output(self):
        """
        Modifies the payload so that it no longer captures printed
        output. Useful for payloads that capture printed output by
        default when that functionality isn't needed.
        """
        # Modify default and explicit augmentations
        cpo = "capturing_printed_output"
        if cpo in self.default_augmentations:
            del self.default_augmentations[cpo]
        if cpo in self.augmentations:
            del self.augmentations[cpo]

        # If we're actually broadcasting, we need to delete from children
        if isinstance(self, TestGroup):
            for test in self.tests:
                if cpo in test.default_augmentations:
                    del test.default_augmentations[cpo]
                if cpo in test.augmentations:
                    del test.augmentations[cpo]

    def copy_args(self, copy=True):
        """
        Sets up the payload so that it will deeply copy argument values.
        Only works for payloads based on
        `evaluations.harness.create_run_function_payload`.

        Set copy to False to disable argument copying (which is the
        default behavior).

        Returns self for chaining.
        """
        self.ensure_payload_constructor_arg("copy_args")
        self.payload_args["copy_args"] = copy
        return self

    def use_harness(self, harness_fn):
        """
        Modifies the payload so that it will use a test harness function
        instead of calling a target function directly. The payload must
        already have `potluck.harness.create_run_function_payload` as its
        base, or a `TypeError` will result.

        The harness function will receive all the same positional and/or
        keyword arguments as the function being tested would have, except
        that it will also receive the function to test as its first
        positional argument.
        """
        if self.payload_constructor != harness.create_run_function_payload:
            raise TypeError(
                f"A test harness can only be applied to a test that's"
                f" normally based on a function call (but {self} is"
                f" has payload constructor: {self.payload_constructor})."
            )
        self.payload_constructor = harness.create_run_harness_payload
        self.payload_args["harness"] = harness_fn

    def set_timeout(self, time_limit):
        """
        Sets a timeout value that limits how long the payload will run.

        Returns self for chaining.
        """
        self.augmentations["with_timeout"] = { "time_limit": time_limit }
        return self

    def do_setup(self, setup_fn):
        """
        Adds a setup function for this payload, which will be run right
        before the payload starts. Returns self for chaining.

        See `potluck.harness.with_setup` for details.

        Note: `HasPayload.do_setup` and `HasPayload.do_cleanup` each
        accumulate setup/cleanup functions instead of replacing the
        previous setup/cleanup function, with setup functions added later
        affecting the results of setup functions added earlier. Also,
        setup/cleanup functions are accumulated between child and parent
        payload-bearing objects, rather than child setups/cleanups
        overriding parent setups/cleanups.
        """
        update_augmentations(
            self.augmentations,
            { "with_setup": { "setup": setup_fn } }
        )
        return self

    def do_cleanup(self, cleanup_fn):
        """
        Adds a cleanup function for this test, which will be run right
        after the payload is finished. Returns self for chaining.

        See `potluck.harness.with_cleanup` for details.
        """
        update_augmentations(
            self.augmentations,
            { "with_cleanup": { "cleanup": cleanup_fn } }
        )
        return self

    def capture_output(self, capture_errors=False, capture_stderr=False):
        """
        Sets up output capturing, so that everything that gets printed
        will be captured in the "output" slot. If `capture_errors` is
        set to True, errors will be captured as part of the output
        instead of actually breaking the test. If `capture_stderr` is set
        to True, messages written to stderr will be captured into an
        additional "error_log" slot. Returns self for chaining.
        """
        self.augmentations["capturing_printed_output"] = {
            "capture_errors": capture_errors,
            "capture_stderr": capture_stderr
        }
        return self

    def provide_inputs(self, strings, policy="hold"):
        """
        Set up a series of strings to use as the results of any `input()`
        calls made during the payload execution. For details, Refer to
        `potluck.harness.with_fake_input`.

        Returns self for chaining.
        """
        self.augmentations["with_fake_input"] = {
            "inputs": strings,
            "extra_policy": policy
        }
        return self

    def use_decorations(self, decorations, ignore_missing=False):
        """
        Sets the decorations dictionary for this payload, which maps
        function (or variable) names to decorator functions that will be
        temporarily applied to those values during testing. This has a
        lot of potential uses, like disabling a function ('decorate' it
        to return a new do-nothing function), performing some operation
        on the result of the test function before comparison happens (by
        decorating the function being tested), or even providing a new
        variable that's not defined by default (but that can often be
        accomplished via other means).

        If `ignore_missing` is set to True instead of the default
        (False), then if a decoration is supposed to apply to a value
        which doesn't exist, instead of an error being raised, the
        decoration function will be called with `potluck.harness.Missing`
        as the input value.

        This function returns self so that you can chain it with other
        modification functions.

        Any old decorations dictionary will be overridden.

        Note that decorations cannot be applied to payloads based on
        module imports, as the decorations are applied to a loaded
        module, and module import payloads re-load the target module with
        each test. `HasPayload.prepare_source` and
        `HasPayload.wrap_module` are the closest equivalents for module
        import payloads.
        """
        self.augmentations["with_module_decorations"] = {
            "decorations": decorations,
            "ignore_missing": ignore_missing
        }
        return self

    def capture_trace(self, trace_targets, state_function):
        """
        Causes the payload to produce a "trace" context slot in
        addition to other slots, which holds a trace of function calls
        to functions named in the provided `trace_targets` sequence. See
        `potluck.harness.tracing_function_calls` for details, including
        the functionality of the state function.

        The `trace_targets` list may include tuples, in which case calls
        to any of the functions in the tuple will be traced as if they
        were calls to the first function (useful for collapsing aliases
        like turtle.fd and turtle.forward).

        This function returns self so that you can chain it with other
        modification functions.

        Any old tracing setup will be overridden.
        """
        self.augmentations["tracing_function_calls"] = {
            "trace_targets": trace_targets,
            "state_function": state_function
        }
        return self

    def sample_result_distribution(
        self,
        slot_map={
            "value": "distribution",
            "ref_value": "ref_distribution"
        },
        trials=50000
    ):
        """
        Modifies the payload so that it runs many times and the
        distribution of results is recorded. For details, see
        `potluck.harness.sampling_distribution_of_results`.

        Returns self for chaining.

        Note that this is useful only in very specific cases, is
        often quite slow, and even in cases where it might be
        applicable, needs to be used with a very careful comparator.

        In particular, if you're sampling the distribution of results
        from a random function and comparing them to a reference
        distribution, even with a lot of trials, the chances that the
        two distributions diverge significantly just by bad luck are
        often unfortunately high. If you're evaluating hundreds of
        submissions per task and dozens of tasks per course and want to
        scrupulously avoid the chance of an erroneous test result,
        consider other methods of testing random functions, such as
        seed-based testing or other de-randomization techniques.
        """
        self.augmentations["sampling_distribution_of_results"] = {
            "slot_map": slot_map,
            "trials": trials
        }
        return self

    def capture_turtle_image(self, alt_text=None, skip_reset=False):
        """
        Captures what's drawn on the turtle canvas, into an "image"
        context slot. See `potluck.harness.capturing_turtle_drawings`,
        which explains the alt_text and skip_reset arguments.

        Returns self for chaining.
        """
        self.augmentations["capturing_turtle_drawings"] = {
            "alt_text": alt_text,
            "skip_reset": skip_reset,
        }
        return self

    def capture_wavesynth(
        self,
        just_capture=None,
        label="resulting_audio"
    ):
        """
        Captures the current track in `wavesynth` as a list of note
        description strings, in a "notes" context slot, and as raw audio,
        in the "audio" slot. See
        `potluck.harness.capturing_wavesynth_audio`.

        You can set either just_capture to "notes" or "audio" to capture
        just one or the other, or leave it at None (the default) to
        capture both.

        A custom label may be provided for any resulting audio elements.

        Returns self for chaining.
        """
        self.augmentations["capturing_wavesynth_audio"] = {
            "just_capture": just_capture,
            "label": label
        }
        return self

    def capture_file_contents(self, filename, binary=False):
        """
        Captures the contents of a specific file after the code has
        finished running. Stores the file name in the "output_filename"
        slot and the file contents as a string in the
        "output_file_contents" slot.

        If `binary` is set to True instead of the default False, the file
        will be read as a bytes object instead of a string.
        """
        self.augmentations["capturing_file_contents"] = {
            "filename": filename,
            "binary": binary
        }


class HasContext:
    """
    Abstract base class for tests which will create
    `potluck.contexts.Context` objects. Provides common tools for
    managing context creation.
    """
    def __init__(self, default_context_args=None):
        """
        Default context args may be provided.
        """
        self.default_context_args = default_context_args or {}
        self.context_args = {}

    def synthesize_context_info(self, group=None):
        """
        Synthesizes context construction arguments. If a group is
        given, it should also be a `HasContext` instance, and its
        information will be mixed with local information as follows:

          - First, group defaults will be loaded.
          - Next, this object's defaults will override those.
          - Third, group explicit values will be added.
          - Finally, local explicit values will have the final say.
        """
        args = {}
        if group:
            args.update(group.default_context_args)
        args.update(self.default_context_args)
        if group:
            args.update(group.context_args)
        args.update(self.context_args)

        return args

    def create_context(
        self,
        builder,
        group=None
    ):
        """
        Creates the implied `potluck.contexts.Context` object. Needs to
        be given the context-builder function that the context will use.
        If a group is provided, its information is merged with local
        information using `synthesize_context_info`.
        """
        # Synthesize arguments
        args = self.synthesize_context_info(group)

        if "builder" in args:
            logging.debug_msg(
                "Warning: overriding existing builder value in"
                " create_context."
            )

        args["builder"] = builder

        # Append our payload's description to our description if we have
        # a payload description
        if hasattr(self, "describe_payload"):
            obf_topic, obf_details = self.describe_payload(group, True)
            clear_topic, clear_details = self.describe_payload(group, False)
            defaults = (
                obf_topic,
                obf_details,
                clear_topic,
                clear_details
            )

            if "description" not in args: # default
                args["description"] = defaults

            # If we've only got a topic (shouldn't happen), double it
            if len(args["description"]) < 4:
                args["description"] = (
                    tuple(args["description"])
                  + defaults[len(args):]
                )

        # Create and return our context object
        return contexts.Context(**args)

    def set_context_description(self, description):
        """
        Sets a custom description for the context. Returns self for
        chaining. A description is a 2-tuple or 4-tuple of strings. If
        it's a 2-tuple, it specifies the title for the rubric entry and
        then the longer description. If it's a 4-tuple, the first two
        elements are the title and description used in blank rubrics,
        while the second two are used in displaying actual evaluation
        results.
        """
        self.context_args["description"] = description
        return self

    def set_context_displayer(self, displayer):
        """
        Sets a custom context product display function. Returns self for
        chaining.

        The function will be handed the context dictionary that was used
        for testing, and should return an HTML string which gets
        displayed in the "Test Results" section of the feedback.
        """
        self.context_args["display_product"] = displayer
        return self

    def describe_module_slot(self):
        """
        Sets up the context to describe itself as producing a module from
        the submitted file. Doesn't actually change how the context
        works; it's assumed that the context already produces a "module"
        value via a module import payload.
        """
        # Modify context arguments
        self.context_args["display_product"] = lambda context: (
            "&lt;the result of running your file&gt;"
        )

        return self


class HasGoal:
    """
    Abstract base class for tests which will create
    `potluck.rubrics.Goal` objects. Provides common tools for managing
    goal creation. Subclasses must override the `create_goal` method with
    a zero-argument method that returns a goal object.
    """
    def create_goal(self):
        """
        Returns the `potluck.rubrics.Goal` implied by this object. Must
        be implemented in concrete subclasses.
        """
        raise NotImplementedError(
            "HasGoal is an abstract class and cannot be used directly."
        )

    def __init__(
        self,
        taskid,
        goal_constructor,
        default_goal_args=None,
    ):
        """
        A task ID string and a goal constructor must be specified.
        Default goal args may be provided. Set the goal category and/or
        type via goal args.
        """
        self.taskid = taskid
        self.default_goal_args = default_goal_args or {}
        self.goal_args = {}
        self.goal_constructor = goal_constructor
        self._cached_goal = None

    def provide_goal(self):
        """
        Returns the result of `create_goal`, but if `provide_goal` has
        been called previously, returns the cached result of that
        previous call instead.
        """
        if self._cached_goal is None:
            self._cached_goal = self.create_goal()
        return self._cached_goal

    def synthesize_goal_info(self, group=None):
        """
        Synthesizes goal construction arguments. If a group is given,
        it should also be a `HasGoal` instance, and its information will
        be mixed with local information as follows:

          - First, group defaults will be loaded.
          - Next, this object's defaults will override those.
          - Third, group explicit values will be added.
          - Finally, local explicit values will have the final say.

        A "goal_type" tag will be deduced from the context_slot goal
        argument if it hasn't been set explicitly.

        Note that the "tags" argument is itself a dictionary, and values
        will be synthesized according to the same procedure as for the
        whole dictionary.
        """
        args = {}
        tags = {}
        if group:
            args.update(group.default_goal_args)
            tags = args.get("tags", {})
        args.update(self.default_goal_args)
        tags.update(args.get("tags", {}))
        if group:
            args.update(group.goal_args)
            tags.update(args.get("tags", {}))
        args.update(self.goal_args)
        tags.update(args.get("tags", {}))
        args["tags"] = tags

        # Deduce goal type if it hasn't been specified explicitly
        if "goal_type" not in args["tags"]: # no explicit goal type
            if "context_slot" in args: # deduce from context slot
                args["tags"]["goal_type"] = CONTEXT_SLOT_IMPLIED_TYPES.get(
                    args["context_slot"],
                    "other"
                )
            else: # no slot to deduce from; guess "other"
                args["tags"]["goal_type"] = "other"

        return args

    def create_goal_from_contexts(self, contexts, group=None):
        """
        Creates the implied `potluck.rubrics.Goal` object. Needs to be
        provided with a list of contexts in which the goal should be
        evaluated. A group may be provided for info merging via
        `synthesize_goal_info`.
        """
        args = self.synthesize_goal_info(group)

        # Set testing contexts for this goal
        if "test_in" not in args:
            args["test_in"] = {}

        if "contexts" in args["test_in"]:
            logging.debug_msg(
                "Warning: overriding existing test_in/contexts value in"
                " create_goal_from_contexts."
            )

        args["test_in"]["contexts"] = contexts

        args["taskid"] = self.taskid

        # Create and return our goal object
        return self.goal_constructor(**args)

    def ensure_goal_constructor_arg(self, desired):
        """
        Raises a TypeError unless this object's goal constructor
        accepts an argument of the desired name.
        """
        cobj = self.goal_constructor.__init__.__code__
        arg_names = cobj.co_varnames[:cobj.co_argcount]
        if desired not in arg_names:
            raise TypeError(
                f"This operation is only allowed for HasGoal classes"
                f" associated with goal types that accept a '{desired}'"
                f" argument ({self.goal_constructor.__name__} does not)."
            )

    def goal(self, category="core"):
        """
        Registers this goal-provider as part of the rubric, under the
        given category (default is "core"). Returns self for chaining.
        """
        if "tags" not in self.goal_args:
            self.goal_args["tags"] = {}

        self.goal_args["tags"]["category"] = category
        register_goal_provider(self)

        return self

    def validate(self, category="core"):
        """
        Registers this goal-provider as part of the rubric's
        test-validation goals, under the given category (default is
        "core"). Returns self for chaining.
        """
        if "tags" not in self.goal_args:
            self.goal_args["tags"] = {}

        self.goal_args["tags"]["category"] = category
        register_validation_goal_provider(self)

        return self

    def set_identifier(self, identifier):
        """
        Sets the identifier that will be used for the goal produced.
        """
        self.goal_args["identifier"] = identifier

    def set_goal_type(self, goal_type):
        """
        Sets an explicit goal type for this goal. Normally, goal types
        can be deduced with reasonable accuracy from existing
        information, but if that isn't working, use this method to
        explicitly declare a goal type. Returns self for chaining.
        """
        if "tags" not in self.goal_args:
            self.goal_args["tags"] = {}
        self.goal_args["tags"]["goal_type"] = goal_type
        return self

    def set_goal_description(self, description):
        """
        Sets a custom description for the goal. Returns self for
        chaining. A description is a 2-tuple or 4-tuple of strings. If
        it's a 2-tuple, it specifies the title for the rubric entry and
        then the longer description. If it's a 4-tuple, the first two
        elements are the title and description used in blank rubrics,
        while the second two are used in displaying actual evaluation
        results.
        """
        self.goal_args["description"] = description
        return self

    def test_module(self, module_comparator):
        """
        Changes the implied goal so that instead of comparing the printed
        output between runs of the submitted and solution modules, it
        compares the module objects that result from those runs, using
        the given comparator function. Only applicable to goals derived
        from payloads that run modules.

        The comparator function will be given two module objects and will
        be expected to return an evaluation result, which is a dictionary
        with "status" and "explanation" keys (see `potluck.compare`).

        Note that one should almost always use `set_goal_description`
        along with this function to describe what the given comparison
        function actually does.

        This function returns self for chaining.
        """
        if (
            not hasattr(self, "ignore_output")
         or not hasattr(self, "describe_module_slot")
        ):
            raise TypeError(
                f"Module-based testing is only applicable for"
                f" Goal-generators which have ignore_output and"
                f" describe_module_slot methods ({self} does not)."
            )

        # Set up our payload to ignore output (since we're using the
        # module object instead)
        self.ignore_output()

        # Set up our context to focus on the module slot
        self.describe_module_slot()

        # Modify goal arguments
        self.goal_args["context_slot"] = "module"
        self.goal_args["tags"]["goal_type"] = "product"

        # Modify default (not explicit) description
        self.default_goal_args["description"] = (
            "Running your file must define the right values",
            (
                "Your file must define the same variables and functions"
                " as the solution file when run."
            )
        )

        return self

    def test_output(self, capture_errors=False):
        """
        Causes this test to compare printed output instead of result
        values. Automatically calls `self.capture_output` (which will
        normally be `HasPayload.capture_output`) to set that up, passing
        `capture_errors` on to that function if it exists.

        Returns self for chaining.
        """
        if hasattr(self, "capture_output"):
            self.capture_output(capture_errors)

        self.goal_args["context_slot"] = "output"

        # Set default (not explicit) description
        if hasattr(self, "base_name"):
            if self.base_name == "import":
                self.default_goal_args["description"] = (
                    "Your program must print the correct output",
                    (
                        "The output printed when your program is"
                        " run must match the solution output."
                    )
                )
            else:
                self.default_goal_args["description"] = (
                    (
                        f"<code>{self.base_name}</code> must print the"
                        f" correct output"
                    ),
                    (
                        f"The output printed when your"
                        f" <code>{self.base_name}</code> function is run"
                        f" must match the solution output."
                    )
                )
        else:
            self.default_goal_args["description"] = (
                "Your code must print the correct output",
                (
                    "The output printed when your code is run must"
                    " match the solution output."
                )
            )

        self.context_args["display_product"] = (
            contexts.build_context_value_displayer(
                "output",
                labels=[
                    "Your output",
                    "Solution output",
                    "Comparison"
                ]
            )
        )

        return self

    def test_with_harness(self, harness_fn):
        """
        Causes this test to compare test-harness results instead of
        direct function call results. Calls `self.use_harness` (which
        must be available, normally from `HasPayload.use_harness`).
        See `HasPayload.use_harness` for details on how the harness
        function will be applied.

        Only applicable to a Goal which is based on testing a function
        call.

        Note: If you want to test the printed output of a test harness
        rather than its return value, you can call both
        `test_with_harness` and `test_output`, but you should call
        `test_with_harness` second to set the description properly.
        """
        if (
            not hasattr(self, "base_name")
         or self.base_name == "import"
         or not hasattr(self, "use_harness")
        ):
            raise TypeError(
                f"Harness-based testing is only applicable for"
                f" Goal-generators which have a base_name attribute"
                f" which isn't 'import' and a use_harness method ({self}"
                f" does not)."
            )

        # Set up harness for our payload
        self.use_harness(harness_fn)

        # Set (default) description from the test harness
        self.default_goal_args["description"] = explain.harness_descriptions(
            harness_fn,
            self.base_name,
            '', # multiple TestCases so can't specify arguments
            '', # multiple TestCases so can't specify arguments
            'behavior' # TODO: less generic here
        )

        return self

    def test_trace(self, trace_targets, state_function):
        """
        Sets up this test to test a trace result instead of just what
        the function returns. Uses the `capture_trace` method to set up
        tracing, which must be available.

        You can use `check_trace_state` and/or `check_invariant`
        afterwards to alter how the trace will be compared with the
        solution trace.
        """
        if (
            not hasattr(self, "base_name")
         or self.base_name == "import"
         or not hasattr(self, "capture_trace")
        ):
            raise TypeError(
                f"Trace-based testing is only applicable for"
                f" Goal-generators which have a capture_trace method"
                f" and a base_name attribute that's not 'import' ({self}"
                f" does not)."
            )

        # Set up tracing
        self.capture_trace(trace_targets, state_function)

        # Target the "trace" context slot
        self.goal_args["context_slot"] = "trace"

        # Set our goal type to "process"
        self.goal_args.setdefault("tags", {})["goal_type"] = "process"

        # Set default (not explicit) description
        self.default_goal_args["description"] = (
            f"<code>{self.base_name}</code> must use the correct process",
            (
                f"The pattern of functions called when your"
                f" <code>{self.base_name}</code> function is run must"
                f" match the solution process."
            )
        )

        return self

    def check_trace_state(
        self,
        state_slots,
        check_args=None,
        check_results=False,
        pre_or_post="pre",
        order_matters=False,
        only=None,
        tolerance="auto"
    ):
        """
        You must call `test_trace` first to set up tracing. This function
        changes the comparison function so that instead of comparing
        entire traces directly, we identify each function call using the
        function name, the values of specific state slots, and the
        parameters used (if `check_args` is non-empty) and/or results
        (if `check_results` is True). After identifying each function
        call in this way, we create a list of those calls in linear
        sequence, and compare those lists between the submitted and
        solution traces (only caring about order if order_matters is set
        to True).

        The `state_slots` argument is required, it should be a list of
        strings and indicates which slots in the state dictionary we
        care about. It may be empty, in which case no state entries will
        be included in the call IDs.

        If `check_args` is set it should be None or a list of strings
        and/or integers; named (and/or indexed) parameters will be
        included as identifying information for trace entries). It may
        also be True to check all arguments.

        If `check_results` is set, the return value of each call will be
        included in its identifying information.

        `pre_or_post` determines whether states before function calls or
        just before their returns are used. Set it to the string 'pre',
        the string 'post', or the string 'both' to include both states.
        The default is 'pre'.

        `order_matters` can be set to True if you want to enforce
        matching of traces in-order, rather than allowing an equivalent
        set of function calls in any order to count as matched. Your
        specs will be more flexible if you can check correctness based
        on state-at-time-of-call rather than order-of-call so the
        default for this is False.

        `only` should be a list of function names, or None. If not None,
        then only functions names in this list will be included in the
        check performed.

        `tolerance` will be passed to `make_structure_comparator`; see
        that function for details; "auto" is the default.

        Returns self for chaining.

        For example, this kind of comparison could be used to ensure
        that a solution calls certain drawing commands with the right
        parameters from the right set of states, without regard to
        order, which is one way to specify that it "draws the right
        thing" even if we don't care what order things are drawn in.
        """
        # Check that tracing is set up
        if self.goal_args["context_slot"] != "trace":
            raise ValueError(
                "You must activate tracing using `test_trace` before"
                " calling `check_trace_state`."
            )

        # Make sure we've got goal which requires a checker
        self.ensure_goal_constructor_arg("checker")

        # Create our base comparator
        base_comparator = compare.make_structure_comparator(
            tolerance=tolerance,
            order_matters=order_matters
        )
        # TODO: Allow rounding differences in state by default, including
        # in args!

        # Define our full comparator
        def compare_trace_states(submitted, solution):
            """
            A custom comparator function which compares certain parts of
            captured trace states.
            """
            # TODO: Better explanation which turns trace state dicts into
            # human-readable explanations of call situations...
            processed = []
            for trace in submitted, solution:
                rendered = []
                processed.append(rendered)
                for entry in harness.walk_trace(trace):
                    if only and entry["fname"] not in only:
                        continue
                    entry_id = { "fname": entry["fname"] }

                    # Grab args if requested
                    if check_args:
                        if check_args is True:
                            entry_id["args"] = copy.copy(entry["args"])
                        else:
                            indices = [
                                i
                                for i in check_args
                                if isinstance(i, int)
                            ]
                            names = [
                                name
                                for name in check_args
                                if isinstance(name, str)
                            ]

                            # Which args are we actually taking?
                            take = []
                            for i, argname in enumerate(entry["args"]):
                                if i in indices or argname in names:
                                    take.append(argname)

                            entry_id["args"] = {
                                argname: entry["args"][argname]
                                for argname in take
                            }

                    # Grab result if we need it
                    if check_results:
                        entry_id["result"] = entry["result"]

                    # Grab pre- and/or post-call state values
                    if pre_or_post in ("pre", "both"):
                        entry_id["pre_state"] = {
                            slot: entry["pre_state"][slot]
                            for slot in state_slots
                        }
                    if pre_or_post in ("post", "both"):
                        entry_id["post_state"] = {
                            slot: entry["post_state"][slot]
                            for slot in state_slots
                        }

                    rendered.append(entry_id)

            # Run our base comparator on the two processed lists
            return base_comparator(processed[0], processed[1])

        # Set up our comparator as the checker for this goal
        self.goal_args["checker"] = compare_trace_states

        # Build description pieces
        targets = "the correct functions"
        if only:
            targets = "the " + phrasing.comma_list(
                f"<code>{fn}</code>"
                for fn in only
            ) + " " + phrasing.plural(len(only), "function")

        conditions = []
        if order_matters:
            conditions.append("in the correct order")

        if check_args:
            conditions.append("with the correct arguments")

        if state_slots:
            conditions.append(
                "while the correct "
              + phrasing.comma_list(state_slots)
              + " " + phrasing.plural(len(state_slots), "value")
              + " " + phrasing.plural(len(state_slots), "is", "are")
              + " set up"
            )

        if check_results:
            conditions.append(
                "and each call must return the correct result"
            )

        # Set default (not explicit) description
        if hasattr(self, "base_name") and self.base_name != "input":
            self.default_goal_args["description"] = (
                (
                    f"<code>{self.base_name}</code> must make the correct"
                    f" function calls"
                ),
                (
                    f"Your <code>{self.base_name}</code> function must"
                  + f" call {targets} "
                  + ', '.join(conditions)
                )
            )
        else:
            self.default_goal_args["description"] = (
                "Your code must make the correct function calls",
                (
                    f"When your code is run it must call {targets} "
                  + ', '.join(conditions)
                )
            )

        return self

    def check_invariant(
        self,
        state_slots,
        only=None,
        partial_tolerance=0.2
    ):
        """
        You must call `test_trace` first to set up tracing. This function
        changes the comparison function so that instead of comparing
        entire traces directly, we check that specific state slots
        specified do not change between the pre- and post- states of
        each trace entry.

        `only` may be set to None, in which case all entries are checked
        (the default), or a list of strings may be provided naming
        functions to check (others will be ignored).

        `partial_tolerance` should be a fraction which specifies what
        percentage of function calls are allowed to violate the
        invariant while still returning a partial-success result.

        By default for floating-point values there is a baseline level
        of tolerance for small changes.

        Returns self for chaining.
        """
        # Check that tracing is set up
        if self.goal_args["context_slot"] != "trace":
            raise ValueError(
                "You must activate tracing using `test_trace` before"
                " calling `check_trace_state`."
            )

        # Make sure we've got goal which requires a checker
        self.ensure_goal_constructor_arg("checker")

        # Set up base comparator
        base_comparator = compare.omni_compare

        # Build description of targets
        targets = "your functions"
        if only:
            targets = "the " + phrasing.comma_list(
                f"<code>{fn}</code>"
                for fn in only
            ) + " " + phrasing.plural(len(only), "function")

        # Build description of states
        states = "the " + phrasing.comma_list(
            f"<code>{slot}</code>"
            for slot in state_slots
        ) + " " + phrasing.plural(len(state_slots), "value")

        def check_for_invariants(submitted, *_):
            """
            Checks the submitted trace to make sure that certain state
            values don't change when certain functions are called. Any
            provided solution trace is ignored.
            """
            total = 0
            failed = []
            for entry in harness.walk_trace(submitted):
                # Only inspect targeted functions
                if only and entry["fname"] not in only:
                    continue

                total += 1

                # Grab pre/post states
                pre = entry["pre_state"]
                post = entry["post_state"]

                # Compare each slot value between pre and post
                different = []
                for slot in state_slots:
                    same = base_comparator(pre[slot], post[slot])
                    if same["status"] != "accomplished":
                        different.append((slot, pre[slot], post[slot]))

                if different:
                    failed.append((entry, different))

            # Return an evaluation based on how many calls failed to be
            # invariant in terms of the specified state slots
            pct_failed = len(failed) / total
            if pct_failed == 0:
                return {
                    "status": "accomplished",
                    "explanation": (
                        f"all {total} calls to {targets} maintained "
                      + phrasing.plural(
                          len(state_slots),
                          "an invariant", "invariants"
                        )
                      + f" for {states}"
                    )
                }
            else:
                status = "failed"
                if pct_failed <= partial_tolerance:
                    status = "partial"
                return {
                    "status": status,
                    "explanation": (
                        f"out of {total} calls to {targets},"
                        f" {len(failed)} failed to maintain "
                      + phrasing.plural(
                          len(state_slots),
                          "an invariant", "invariants"
                        )
                      + f" for {states}:<br>\n"
                      + html_tools.build_list(
                            (
                                f"<code>{entry['fname']}("
                              + ', '.join(
                                    "{name}={val}".format(
                                        name=name,
                                        val=html_tools.dynamic_html_repr(
                                            entry['args'][name]
                                        )
                                    )
                                  for name in entry['args']
                                )
                              + ")</code> changed "
                              + html_tools.build_list(
                                    (
                                        "<code>{slot}</code> from"
                                        " <code>{pre}</code>"
                                        " to <code>{post}</code>"
                                    ).format(
                                        slot=slot,
                                        pre=html_tools.dynamic_html_repr(
                                            pre
                                        ),
                                        post=html_tools.dynamic_html_repr(
                                            post
                                        )
                                    )
                                    for slot, pre, post in different
                                )
                            )
                            for entry, different in failed
                        )
                    )
                }

        # Set up our comparator as the checker for this goal
        self.goal_args["checker"] = check_for_invariants

        # Set default (not explicit) descriptions:
        self.default_goal_args["description"] = (
            (
                f"{targets} must maintain ".capitalize()
              + phrasing.plural(
                  len(state_slots),
                  "an invariant", "invariants"
                )
              + f" for {states}"
            ),
            (
                f"Each call to {targets} must return {states} to "
              + phrasing.plural(len(state_slots), "its", "their")
              + " initial state before " + phrasing.plural(
                    len(only) if only else 2,
                    "it returns.",
                    "they return."
                )
            )
        )

        # Now we're done; return self for chaining
        return self

    def check_trace_count(self, target, double_or_half=False):
        """
        You must call `test_trace` first to set up tracing. This function
        changes the comparison function so that instead of comparing
        entire traces directly, we look at only function calls in the
        trace to functions with the provided target name, and we just
        compare how many there are, ignoring the state-at-call-time and
        even arguments-supplied information in the trace.

        Returns partial success if the number of calls is close to
        correct, and if double_or_half is True, also returns partial
        success if the number of calls is double or half the correct
        value, or within one of double or half.
        """
        # Check that tracing is set up
        if self.goal_args["context_slot"] != "trace":
            raise ValueError(
                "You must activate tracing using `test_trace` before"
                " calling `check_trace_count`."
            )

        # Make sure we've got goal which requires a checker
        self.ensure_goal_constructor_arg("checker")

        # Define our full comparator
        def compare_trace_counts(submitted, solution):
            """
            A custom comparator function which compares the count of
            calls to a certain function in two traces.
            """
            counts = []
            # Count entries in each trace
            for trace in submitted, solution:
                count = 0
                for entry in harness.walk_trace(trace):
                    if entry["fname"] == target:
                        count += 1
                counts.append(count)

            sub_count, soln_count = counts

            if sub_count == soln_count:
                return {
                    "status": "accomplished",
                    "explanation": (
                        f"Number of function calls to"
                        f" <code>{target}</code> was correct"
                        f" ({soln_count})"
                    )
                }
            elif sub_count in (
                soln_count - 1,
                soln_count + 1
            ):
                return {
                    "status": "partial",
                    "explanation": (
                        f"Number of function calls to"
                        f" <code>{target}</code> ({sub_count}) was"
                        f" almost correct (should have been"
                        f" {soln_count})."
                    )
                }
            elif double_or_half and sub_count in (
                soln_count // 2,
                soln_count * 2
            ):
                return {
                    "status": "partial",
                    "explanation": (
                        f"Number of function calls to"
                        f" <code>{target}</code> ({sub_count}) was"
                        f" double or half of the correct value"
                        f" ({soln_count})."
                    )
                }
            elif double_or_half and sub_count in (
                soln_count // 2 - 1,
                soln_count // 2 + 1,
                soln_count * 2 - 1,
                soln_count * 2 + 1
            ):
                return {
                    "status": "partial",
                    "explanation": (
                        f"Number of function calls to"
                        f" <code>{target}</code> ({sub_count}) was"
                        f" nearly double or half of the correct value"
                        f" ({soln_count})."
                    )
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        f"Number of function calls to"
                        f" <code>{target}</code> ({sub_count}) was"
                        f" incorrect (should have been {soln_count})."
                    )
                }

        # Set up our comparator as the checker for this goal
        self.goal_args["checker"] = compare_trace_counts

        # Set default (not explicit) description
        if hasattr(self, "base_name") and self.base_name != "input":
            self.default_goal_args["description"] = (
                (
                    f"<code>{self.base_name}</code> must make the correct"
                    f" number of calls to <code>{target}</code>"
                ),
                (
                    f"Your <code>{self.base_name}</code> function must"
                    f" call <code>{target}</code> the correct number of"
                    f" times."
                )
            )
        else:
            self.default_goal_args["description"] = (
                (
                    f"Your code must make the correct number of function"
                    f" calls to <code>{target}</code>"
                ),
                (
                    f"When your code is run it must call"
                    f" <code>{target}<code> the correct number of"
                    f" times."
                )
            )

        return self

    def test_wavesynth_notes(self):
        """
        Sets up for testing note descriptions from the wavesynth module.
        """
        if hasattr(self, "capture_wavesynth"):
            self.capture_wavesynth(just_capture="notes")

        self.goal_args["context_slot"] = "notes"

        # Set default (not explicit) description
        if hasattr(self, "base_name"):
            if self.base_name == "import":
                what = "your program"
                What = "Your program"
                verb = "run"
            else:
                what = f"<code>{self.base_name}</code>"
                What = what
                verb = "called"

            self.default_goal_args["description"] = (
                f"{What} must produce the correct note sequence",
                (
                    f"The notes added to the current track when {what}"
                    f" is {verb} must match the solution notes"
                    f" in terms of timing, instruments, pitches, and"
                    f" volumes."
                ),
                (
                    f"{What} produces the correct note"
                    " sequence"
                ),
                (
                    "We checked that the notes {what} adds to the"
                    " current track match those added by the solution."
                )
            )

        else:
            self.default_goal_args["description"] = (
                "Your code must produce the correct note sequence",
                (
                    "The sequence of notes added to the current track"
                    " when your code is run must match the solution"
                    " notes."
                )
            )

        self.context_args["display_product"] = (
            contexts.build_context_value_displayer(
                "notes",
                labels=[
                    "Your notes",
                    "Solution notes",
                    "Comparison"
                ]
            )
        )

        return self

    def test_wavesynth_audio(self):
        """
        Sets up for testing raw audio from the wavesynth module.
        """
        if hasattr(self, "capture_wavesynth"):
            self.capture_wavesynth(just_capture="audio")

        self.goal_args["context_slot"] = "audio"

        # Set default (not explicit) description
        if hasattr(self, "base_name"):
            if self.base_name == "import":
                what = "your program"
                verb = "run"
            else:
                what = f"<code>{self.base_name}</code>"
                verb = "called"
            self.default_goal_args["description"] = (
                f"{what.capitalize()} must produce the correct audio",
                (
                    f"The audio produced by calling"
                    f" <code>playTrack</code> after {what} is {verb}"
                    f" must match the solution audio."
                )
            )
        else:
            self.default_goal_args["description"] = (
                "Your code must produce the correct audio",
                (
                    "The audio produced by calling"
                    " <code>playTrack</code> after your code is run"
                    " must match the solution audio."
                )
            )

        # TODO: Use snippet machinery!
        self.context_args["display_product"] = (
            contexts.build_context_value_displayer(
                "audio",
                labels=[
                    "Your audio",
                    "Solution audio",
                    "Comparison"
                ]
            )
        )

        return self

    def test_turtle_image(
        self,
        allowed_differences=0.03,
        partial_allowed=0.5,
        similarity_threshold=15
    ):
        """
        Sets up for testing the image drawn using turtle graphics. The
        arguments are passed on to `compare.make_image_comparator` to
        determine the strictness of the comparison. The defaults are
        fairly liberal, especially if what is being drawn does not take
        up a large area of the image.

        TODO: Background subtraction!
        """
        # Capture turtle image (if we can)
        if hasattr(self, "capture_turtle_image"):
            self.capture_turtle_image()

        # Set up image comparator
        self.compare_using(
            compare.make_image_comparator(
                allowed_differences,
                partial_allowed,
                similarity_threshold
            )
        )

        # Set context slot to compare
        self.goal_args["context_slot"] = "image"

        # Set default (not explicit) description
        if hasattr(self, "base_name"):
            if self.base_name == "import":
                what = "your program"
                verb = "run"
            else:
                what = f"<code>{self.base_name}</code>"
                verb = "called"
            self.default_goal_args["description"] = (
                f"{what.capitalize()} must draw the correct image",
                (
                    f"The image drawn in the turtle window after {what}"
                    f" is {verb} must match the solution image."
                )
            )
        else:
            self.default_goal_args["description"] = (
                "Your code must draw the correct image",
                (
                    "The image drawn in the turtle window after your"
                    " code is run must match the solution image."
                )
            )

        # TODO: Use snippet machinery?
        # Set context value displayer
        self.context_args["display_product"] = (
            contexts.create_image_result_displayer()
        )

        return self

    def test_file_contents(self, filename=None, binary=False):
        """
        Causes this test to compare the contents of the specified file
        instead of result values. Automatically calls
        `self.capture_file_contents` (which will normally be
        `HasPayload.capture_file_contents`) to set that up. The `binary`
        argument will be passed through to that function, and indicates
        that file contents should be read as bytes, not as a string.

        Note that if you are using a `TestGroup` that includes individual
        `SingleTest` objects which write to multiple different filenames,
        leave the filename argument out and
        `HasPayload.capture_file_contents` will not be called; you will
        have to call it yourself on individual `SingleTest` items.

        Returns self for chaining.
        """
        if hasattr(self, "capture_file_contents") and filename is not None:
            self.capture_file_contents(filename, binary)

        self.goal_args["context_slot"] = "output_file_contents"

        # Set default (not explicit) description
        file_desc = "the appropriate file"
        if filename is not None:
            file_desc = "<code>" + filename + "</code>"

        if hasattr(self, "base_name"):
            if self.base_name == "import":
                self.default_goal_args["description"] = (
                    (
                        f"Your program must write the correct data into"
                        f" {file_desc}"
                    ),
                    (
                        f"The data written into {file_desc} when your"
                        f" program is run must match what the solution"
                        f" writes."
                    )
                )
            else:
                self.default_goal_args["description"] = (
                    (
                        f"<code>{self.base_name}</code> must write the"
                        f" correct data into {file_desc}"
                    ),
                    (
                        f"The data written to {file_desc} when your"
                        f" <code>{self.base_name}</code> function is run"
                        f" must match what the solution writes."
                    )
                )
        else:
            self.default_goal_args["description"] = (
                (
                    f"Your code must write the correct data into"
                    f" {file_desc}"
                ),
                (
                    f"The data written into {file_desc} when your code"
                    f" is run must match the solution output."
                )
            )

        self.context_args["display_product"] = (
            contexts.build_context_value_displayer(
                "output_file_contents",
                labels=[
                    f"Contents of {file_desc}",
                    "Correct contents",
                    "Comparison"
                ]
            )
        )

        return self

    # TODO: property -> payload -> condition description assembly...
    def compare_using(
        self,
        comparator_fn=None,
        context_slot=None
    ):
        """
        Specifies an alternate comparator for this goal (only works for
        `potluck.rubrics.ComparisonTest` as the `goal_constructor`). If a
        context_slot is also (or only) given, changes the context slot
        which will be compared as well.

        The comparator function (if provided) must return a comparison
        result: a dictionary with "status" and "explanation" keys, where
        the status is one of "accomplished", "partial", or "failed". If
        no comparison function is provided, the current comparator will
        not be changed.

        The context slot (if provided) must be a string naming the slot
        to use; see `potluck.contexts.Context` for a list of common slot
        names, but you could use your own custom slots too by using
        `HasPayload.do_setup` and/or `HasPayload.do_cleanup`, which can
        modify the context dictionary directly. If no context slot is
        specified, the current value will not be changed. Note that
        several other methods, like `test_output`, also modify the
        context slot and ordering matters; the last method to be called
        will determine which context slot is used.

        Returns self for chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        if comparator_fn is not None:
            self.goal_args["checker"] = comparator_fn
        if context_slot is not None:
            self.goal_args["context_slot"] = context_slot
        return self

    def succeed_unless_crashed(self):
        """
        Overrides the comparator such that the goal always succeeds,
        unless the context builder fails because of a crash. Modifies
        the default goal arguments to note this.

        Note that this won't check for captured errors (e.g., by using
        `HasGoal.test_output` and/or `HasPayload.capture_output` with
        the `capture_errors` option).

        Returns self for chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = lambda _1, _2: {
            "status": "accomplished",
            "explanation": "Test ran without errors."
        }
        # Set default goal type
        self.default_goal_args.setdefault(
            "tags",
            {}
        )["goal_type"] = "process"

        # Set default (not explicit) description
        if hasattr(self, "base_name"):
            if self.base_name == "import":
                self.default_goal_args["description"] = (
                    "Your program must not crash",
                    "Your program must run without crashing.",
                    "Your program must not crash",
                    "We ran your program and checked if it crashed."
                )
            else:
                self.default_goal_args["description"] = (
                    f"<code>{self.base_name}</code> must not crash",
                    (
                        f"Your <code>{self.base_name}</code> function"
                        f" must run without crashing."
                    ),
                    f"<code>{self.base_name}</code> must not crash",
                    (
                        f"We ran your <code>{self.base_name}</code>"
                        f" function and checked whether it crashed."
                    )
                )
        else:
            self.default_goal_args["description"] = (
                "Your code must not crash",
                "Your code must run without crashing.",
                "Your code must not crash",
                "We ran your code and checked if it crashed."
            )

        return self

    def compare_exactly(self):
        """
        Overrides the comparator (see `compare_using`) with
        `potluck.compare.strict_equality_checker`, which compares items
        of any type for exact equality (the default
        `potluck.compare.omni_compare` function has various grades of
        partial success and ignores things like floating point rounding
        error). Returns the `TestGroup` for chaining.

        Note: this is very rarely what you want, since it has weird edge
        cases that the default `potluck.compare.omni_compare` smoothes
        over.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = compare.strict_equality_checker
        return self

    def compare_reports(self):
        """
        Overrides the comparator (see `compare_using`) with
        `potluck.compare.multiline_strings_are_exactly_equal`, which
        compares strings exactly and formats multi-line output nicely.
        This is just a convenience function to make this functionality
        more prominent; it returns the `TestGroup` for chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = compare.multiline_strings_are_exactly_equal
        return self

    def compare_strings_gently(self):
        """
        Overrides the comparator (see `compare_using`) with
        `potluck.compare.very_fuzzy_string_compare`, which compares
        strings very roughly. This is just a convenience function to make
        this functionality more prominent; it returns the `TestGroup` for
        chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = compare.very_fuzzy_string_compare
        return self

    def compare_strings_semi_strict(self):
        """
        Overrides the comparator (see `comparator`) with
        `potluck.compare.strings_are_equal_modulo_whitespace`, which
        compares strings somewhat roughly (errors in whitespace and
        capitalization are mostly ignored). This is just a convenience
        function to make this functionality more prominent; it returns
        the `TestGroup` for chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = (
            compare.strings_are_equal_modulo_whitespace
        )
        return self

    def compare_strings_firmly(self):
        """
        Overrides the comparator (see `comparator`) with
        `potluck.compare.strings_are_equal_modulo_most_whitespace`,
        which works like strings_are_equal_modulo_whitespace but it
        requires that word boundaries are preserved. This is just a
        convenience function to make this functionality more prominent;
        it returns the `TestGroup` for chaining.
        """
        self.ensure_goal_constructor_arg("checker")
        self.goal_args["checker"] = (
            compare.strings_are_equal_modulo_most_whitespace
        )
        return self

    def refine(self, refiner_class, *refiner_args, **refiner_kwargs):
        """
        Creates a new `RefinedTest` based on the goal to be created by
        the current test (actually, based on the associated context
        objects; see `RefinedTest`).

        You need to provide the class object to be instanced, and you may
        provide extra positional and/or keyword arguments that that
        refiner requires for initialization, beyond the parent object.
        This function returns the new `RefinedTest` instance for
        chaining.

        Note that typically, it is not necessary for both the original
        and refined goals to appear in the rubric, and to achieve that,
        simply avoid calling the `goal` method of the original goal.
        """
        return refiner_class(self, *refiner_args, **refiner_kwargs)


#-------------------------------#
# SingleTest and derived classes #
#-------------------------------#

class SingleTest(HasPayload, HasContext):
    """
    A `SingleTest` is a single test case for a function (or similar,
    like a test of a variable value or a test of importing a whole
    module). These things have a payload and a context, and can be (and
    usually are) registered as part of a `TestGroup`. The mere
    instantiation of a `SingleTest` object adds it to the test registry
    which means it will appear on the rubric created by `rubric`, unless
    `register` is set to False when it's constructed.

    Most modification methods chain by returning the `SingleTest`
    object.

    In terms of the rubric constructed by the `rubric` function, a
    `SingleTest` is actually a placeholder for a context
    (`potluck.contexts.Context`) which will be one of possibly multiple
    context objects used as testing contexts for a single
    `potluck.rubrics.Goal`. This goal object is derived from a
    `TestGroup`, which is automatically instantiated as soon as a
    `SingleTest` is created, but which will be associated with multiple
    `SingleTest` objects that share the same base name and group name.
    """
    def __init__(
        self,
        base_name,
        group_name="_",
        register=True,
        payload_constructor=harness.create_run_function_payload,
        default_payload_args=None,
        default_augmentations=None,
        default_context_args=None
    ):
        self.base_name = base_name
        self.group_name = group_name
        """
        A `base_name` is required and defines the base name for the
        `TestGroup` object that this `SingleTest` will register under; a
        `group_name` is optional and defaults to '_'. If `register` is
        set to False, this test won't automatically be registered with a
        test group, which generally means it also won't be used as part
        of a rubric.

        The keyword arguments for the `HasPayload` and `HasContext`
        constructors will be passed through, but also receive defaults
        if not provided at this stage.
        """
        default_augmentations = default_augmentations or {
            "capturing_printed_output": {"capture_errors": False},
            "with_timeout": {"time_limit": 5},
            "run_in_sandbox": {},
            "run_for_base_and_ref_values": {},
        }
        # leave default_payload_args and default_context_args as None if
        # not provided so that HasContext.__init__ and
        # HasPayload.__init__ can establish their own defaults

        # Initialize our payload setup
        HasPayload.__init__(
            self,
            payload_constructor=payload_constructor,
            default_payload_args=default_payload_args,
            default_augmentations=default_augmentations
        )

        # Initialize our context info
        HasContext.__init__(
            self,
            default_context_args=default_context_args
        )

        # Register ourself if requested to
        self.group = None
        if register:
            group(
                base_name,
                group_name,
                create=True
            ).add(self)


class TestImport(SingleTest):
    """
    A `TestImport` is a test which involves importing an entire module,
    and by default tests the printed output from that process. It is
    a `SingleTest`, and by default will be automatically registered under
    the name "import" with group name '_'.

    Specialization methods like `wrap_module` can be used to control the
    details of the test; see `HasPayload` and `HasContext` for more
    details.
    """
    def __init__(self, group_name="_", register=True):
        """
        The module to be imported is defined by the currently-active
        filename (see `potluck.contexts.FileContext`).

        A group name other than the default '_' may be provided, and
        automatic registration with a group may be disabled by setting
        `register` to False.
        """
        super().__init__(
            "import",
            group_name=group_name,
            register=register,
            payload_constructor=harness.create_module_import_payload,
            default_payload_args={
                "name_prefix": "test_",
                "use_fix_parse": True,
                "prep": None,
                "wrap": None
            },
            # default_augmentations is left as.. default
            default_context_args={
                # builder will be added elsehow
                # description if omitted has a smart default
                "display_product": (
                    contexts.build_context_value_displayer(
                        "output",
                        labels=[
                            "Your output",
                            "Solution output",
                            "Comparison"
                        ]
                    )
                ),
                # Capture auto-filename at instantiation time, and also
                # make sure we'll have access to sandboxes.
                "depends": contexts.auto(
                    "filename",
                    "file_path",
                    "ref_filename",
                    "ref_file_path",
                    "sandbox",
                    "ref_sandbox",
                ),
            }
        )

        # If we're in a group, update that group's default goal
        # description to include our relevant filename...
        if self.group:
            # Figure out which file we're (automatically) targeting
            target = None
            # (should be exactly one context, and it should have a
            # target_file attribute)
            for ctx in self.default_context_args["depends"]:
                if hasattr(ctx, "target_file"):
                    target = ctx.target_file
                    break

            # Override default description with a better one
            if target is not None:
                self.group.default_goal_args["description"] = (
                    (
                        f"Running <code>{target}</code> must exhibit"
                        f" the correct behavior"
                    ),
                    (
                        f"When we run <code>{target}</code> as a whole"
                        f" file, the pattern of printed output based"
                        f" on inputs must match the solution's"
                        f" behavior."
                    )
                )


class TestValue(SingleTest):
    """
    A `TestValue` is a test which involves inspecting the value of a
    variable in the submitted module. It is a `SingleTest`, and by
    default will be automatically registered under its variable name
    with group name '_'.

    Specialization methods like `use_decorations` can be used to control
    the details of the test; see `HasPayload` and `HasContext` for more
    details. Note that many of those methods don't apply to this test,
    since we're just retrieving a variable value, not running a function
    or importing a module.
    """
    def __init__(self, varname, group_name="_", register=True):
        """
        The name of the variable to be inspected required.

        A group name other than the default '_' may be provided, and
        automatic registration with a group may be disabled by setting
        `register` to False.
        """
        super().__init__(
            varname,
            group_name=group_name,
            register=register,
            payload_constructor=harness.create_read_variable_payload,
            default_payload_args={"varname": varname},
            default_augmentations={
                "with_timeout": {"time_limit": 5},
                "run_in_sandbox": {},
                "run_for_base_and_ref_values": {},
            },
            default_context_args={
                # builder will be added elsehow
                # description if omitted has a smart default
                "display_product": (
                    contexts.build_context_value_displayer(
                        "value",
                        labels=[
                            "Your value",
                            "Solution value",
                            "Comparison"
                        ]
                    )
                ),
                # Capture auto-filename at instantiation time
                "depends": contexts.auto("module", "ref_module"),
            }
        )


class TestCase(SingleTest):
    """
    A `TestCase` is a `SingleTest` representing a unit test for a
    function, with a basic setup (test equality of return values) by
    default. Different behavior may be achieved by calling various
    specialization methods (for example, to specify stdin contents).

    The base name for the test group a case registers with will be the
    name of the function being tested. If you want to separate tests
    that share a function name into multiple groups (i.e., goals),
    specify distinct `group_name` values for the different `TestCase`
    objects you create.

    Instantiating a `TestCase` is not enough to create a goal: goals are
    derived from `TestGroup` objects which group one or more test cases
    together (this is usually desirable, although it's possible to have
    groups that contain only a single test each). Call the `group`
    function to retrieve the implied group after instantiating one or
    more `TestCase` objects that share a function name and group name.
    """
    def __init__(
        self,
        fn_name,
        args=None,
        kwargs=None,
        group_name="_",
        register=True
    ):
        """
        The name of the function to test is the only required value,
        although a tuple of arguments is usually also provided (can be
        omitted to call without arguments). An optional dictionary of
        keyword arguments may also be supplied.

        Normally all tests of a single function will be collapsed into a
        single goal, but by giving tests different `group_name` strings
        you can change this (having more different goals generally makes
        things a bit more forgiving). The group name is arbitrary; the
        default group name is '_'.

        If `register` is given as False (True is the default), the test
        case won't be registered and will not be available for grouping
        or turning into a goal.
        """
        args = args or []
        kwargs = kwargs or {}
        self.args = args
        self.kwargs = kwargs

        self.fn_name = fn_name

        super().__init__(
            self.fn_name,
            group_name,
            register,
            payload_constructor=harness.create_run_function_payload,
            default_payload_args={
                "fname": fn_name,
                "posargs": args,
                "kwargs": kwargs,
                "copy_args": True
            },
            # default_augmentations has a good... default
            default_context_args={
                # builder will be added elsehow
                # description if omitted has a smart default
                "display_product": (
                    contexts.build_context_value_displayer(
                        "value",
                        labels=[
                            "Your result",
                            "Solution result",
                            "Comparison"
                        ]
                    )
                ),
                # Capture auto-filename at instantiation time
                "depends": contexts.auto("module", "ref_module"),
            }
        )


class TestBlock(SingleTest):
    """
    A `SingleTest` which runs a block of code, using the result value
    of the final expression in the block as the value to be tested. A
    name for the block must be provided, and will be used as the base
    name of the `SingleTest`, with "_" as the default group name.

    A fake version of the block to display to students may be provided
    alongside the actual code to run.
    """
    def __init__(
        self,
        name,
        block,
        actual=None,
        group_name="_",
        register=True
    ):
        """
        The name for the block, plus the block of code itself (as a
        multi-line string) must be provided. The actual block name will
        be the provided name prefixed with 'block:', to prevent the
        possibility of identifier overlaps with other kinds of tests.

        Optionally, if you want to simplify the appearance of the code, a
        multi-line string of code to run, OR a list of AST nodes to
        execute may be provided as the "actual" argument, in which case
        the "block" value will just be used for display purposes.

        A group name other than the default '_' may be provided, and
        automatic registration with a group may be disabled by setting
        `register` to False.
        """
        self.name = "block:" + name

        self.block = block

        if not isinstance(block, str):
            raise TypeError(
                f"The block value must be a string. If you want to supply"
                f" a list of AST nodes, use the 'actual' parameter."
                f" (Failed for '{self.name}')"
            )

        if actual is None:
            actual = block

        if isinstance(actual, str):
            try:
                self.nodes = ast.parse(actual).body
            except Exception:
                raise ValueError(
                    f"Failed to compile code block for test"
                    f" '{self.name}'."
                )
            if len(self.nodes) == 0:
                raise ValueError(
                    f"Empty code string in `TestBlock` constructor."
                    f" (Failed for '{self.name}')"
                )
        else:
            try:
                actual = list(actual)
            except Exception:
                raise TypeError(
                    f"The 'actual' block of code must be provided as a"
                    f" string or as a list (or other iterable) of AST"
                    f" nodes). (Failed for '{self.name}')"
                )
            if len(block) == 0:
                raise ValueError(
                    f"Empty code block in `TestBlock` constructor."
                    f" (Failed for '{self.name}')"
                )
            if not isinstance(block[0], ast.AST):
                raise TypeError(
                    f"First code block item in `TestBlock` was not an"
                    f" AST node. (Failed for '{self.name}')"
                )
            self.nodes = actual

        super().__init__(
            self.name,
            group_name,
            register,
            payload_constructor=harness.create_execute_code_block_payload,
            default_payload_args={
                "block_name": self.name,
                "src": self.block,
                "nodes": self.nodes
            },
            # default_augmentations has a good... default
            default_context_args={
                # builder will be added elsehow
                # description if omitted has a smart default
                "display_product": (
                    contexts.build_context_value_displayer(
                        "value",
                        labels=[
                            "Your result",
                            "Solution result",
                            "Comparison"
                        ]
                    )
                ),
                # Capture auto-filename at instantiation time
                "depends": contexts.auto("module", "ref_module"),
            }
        )


#---------------#
# Check classes #
#---------------#

class Check:
    """
    `Check` is the base class for a few different classes that represent
    simplified/specialized `potluck.rubrics.ImplementationCheck`s. Each
    `Check` should be assigned to one of the categories:

    - foundational (deprecated)
    - core
    - extra
    - feedback_only
    - auto

    Generally only 'core' and 'extra' are needed; see
    `potluck.rubrics.foundational_core_extras_metric` and
    `potluck.rubrics.core_extras_categorized_metric`. Additionally, if
    using the later metric, a goal type should be included, which is
    "auto" by default but could reasonably be "procedure", "style" or
    "other".

    When a Check's category/goal-type is set to 'auto' (the default
    for both) that property will be inherited from the parent Check if
    this check is a sub-rule, or set to 'core'/'procedure' if not.

    When a check has a different category or goal type than its parent
    check, a copy of that parent check will be created belonging to the
    child category/type, and the original parent check won't include the
    different-category/type child. Also, any other children of the same
    parent that belong to the same category and goal type will be
    included on a single new-category/type copy of the parent, so it's
    not as if each alternate-category/type child creates its own parent
    `Check`.

    This setup allows for extra requirements to be specified as the
    leaves of a `Check` subrule tree without having to specify the whole
    tree twice.

    Note that the identifiers of each `Check` will be concatenated with
    their parent's identifiers, minus the 'check:' prefix, and separated
    by colons, so give each `Check` a better chance of ending up with a
    unique identifier before numeric-suffix-addition.
    """
    def __init__(
        self,
        identifier,
        patterns,
        limits,
        name=None,
        category='auto',
        goal_type='auto'
    ):
        """
        A check needs an identifier, a list of patterns (could be
        length-one), a tuple of limits (min/max, either or even both may
        be None), and it may specify a name instead of deriving one
        automatically from the patterns (see
        `potluck.rubrics.ImplementationCheck`), a category string (e.g.,
        'extra' instead of defaulting to 'auto'), and/or a goal type
        (e.g., 'style' instead of defaulting to 'auto'). All other
        `potluck.rubrics.ImplementationCheck` details are specified via
        calling methods on the object after it is created. The name may
        be a string containing HTML code, or a 2-item tuple to explicitly
        specify singular and plural forms of the name (otherwise an 's'
        will be added to the end of the name to generate the plural
        form).
        """
        self.taskid = file_utils.deduce_task_id()

        if not isinstance(identifier, str):
            raise TypeError(
                "The identifier for a Check must be a string."
            )
        self.identifier = identifier

        if not isinstance(patterns, (list, tuple)):
            raise TypeError(
                "Patterns for a check must be a list or tuple (may be"
              + " length-1)"
            )

        # When we instantiate the Check we get the auto-context-provider
        # for the "scope" slot; this will be used later during goal
        # instantiation.
        self.test_in = { "contexts": contexts.auto("scope") }

        # Core fields
        self.category = category
        self.goal_type = goal_type
        self.patterns = patterns
        self.limits = limits

        if isinstance(name, str):
            # automatic pluralization by default
            self.name = name, name + 's'
        else:
            # Use a 2-item tuple to specify singular and plural forms
            self.name = name

        self.subrules = []

        self._description = None
        self._match_filters = []
        self._softmin = False
        self._softmax = False
        self._outside = None
        self._callees = False
        self._subslip = None
        self._match_identity_function = lambda code, node, env: (
            tuple(node) if isinstance(node, list) else node
        )

        # Note: this is only set via FunctionCall.require_of_def
        self._check_in_def = False

        self._force_smaller_match = False

        # Register this Check
        checklist(category, goal_type, create=True).append(self)

    def set_description(
        self,
        title,
        summary,
        final_title=None,
        final_summary=None
    ):
        """
        Sets up a custom description for this `Check`. If not used, a
        default description will be constructed based on the parameters
        of the check. The `title` and `summary` arguments are the rubric
        entry and associated description to be used when displaying an
        ungraded rubric, while the optional `final_title` and
        `final_summary` are the items to be used when displaying the
        goal as part of a graded rubric. If the final title and/or
        summary are omitted, the normal title/summary are used.

        This function returns the `Check` for chaining.
        """
        if final_title is None:
            final_title = title

        if final_summary is None:
            final_summary = summary

        self._description = (title, summary, final_title, final_summary)
        return self

    def match_filter(self, filter_function):
        """
        Adds a custom filtering function to this check that can throw out
        some potential matches. The filtering function will be given the
        entire submitted AST tree, the (potentially) matching AST node,
        and the binding environment of the match, and it should return
        True or False, where False will filter out that match. You can
        call this function multiple times and each individual match
        filter will be ANDed with the others.

        This function returns the `Check` object for chaining.
        """
        self._match_filters.append(filter_function)
        return self

    def softmin(self, value=True):
        """
        Turns the lower limit for matches for this check into a soft
        limit, so that too few copies still counts as partially
        completing this check overall. If the value argument is either
        "warn" or "note", then when too few matches are found, the check
        still succeeds, but a warning (or note) is generated that
        describes the unexpectedly low number of occurrences.

        The value could also be a number, which establishes an alternate
        lower bound on the number of matches that will count for partial
        success on the check. E.g., if the min is 3, you could set the
        softmin at 2.5 and then a situation where there were 2 full and
        one partial matches would count as a partial match for the check
        overall.

        This function returns the `Check` object for chaining.
        """
        self._softmin = value
        return self

    def softmax(self, value=True):
        """
        Turns the upper limit for matches into a soft limit, just as with
        `softmin`. Also accepts the strings "warn" or "note", as well as
        integer values. Unlike `softmin`, when setting this value as a
        number, partial matches are ignored and will not push the rule
        over its hard or soft limits.

        This function returns the `Check` object for chaining.
        """
        self._softmax = value
        return self

    def outside(self, patterns):
        """
        Accepts a list of patterns (strings containing mast pseudo-code)
        or a single pattern string, and sets that as the exclusion
        pattern for this rule, which will ensure that matches which occur
        inside one of those patterns are ignored. Consider using values
        like `potluck.patterns.IF_PATTERN` or
        `potluck.patterns.ALL_FOR_AND_WHILE_LOOP_PATTERNS` as the
        patterns argument.

        Note that currently, this function's effects are not
        automatically described by the description of the Check it's
        applied to, so you'll almost always need to use set_description
        to describe what the check does yourself.
        TODO: Some automatic default for that?

        This function returns the `Check` object for chaining.
        """
        self._outside = patterns
        return self

    def check_callees(self, turn_on=True):
        """
        Turns on callee-checking for this rule (or turns it off if given
        False as an argument). This means that matches for this rule will
        be searched for within the code of any locally-defined functions
        that are called from the code being inspected, which helps find
        things that you're looking for which a student puts into a helper
        function. Applying this to a top-level check is generally not
        useful, since any top-level checks already look for matches in
        the entire submitted module; it should always be applied to
        sub-rules.

        TODO: This feature is still (as of 2020-6) a bit unstable and may
        slow things down substantially in some cases.

        This function returns the `Check` object for chaining.
        """
        self._callees = turn_on
        return self

    def subrule_tolerance(self, tolerance=0):
        """
        Sets the number of sub-rules that are allowed to go unmatched
        while still counting this rule as a partial match. The argument
        is a number, which may be fractional, since a partially-matched
        sub-rule counts as 0.5 of a fully-matched rule. By default the
        number is 0: if any sub-rule is unmatched, the entire
        match-in-consideration is ignored entirely.

        This function returns the `Check` object for chaining.
        """
        self._subslip = tolerance
        return self

    def count_using(self, identity_function):
        """
        Sets up a custom function to determine the identity of a match,
        which affects how matches are counting when considering limits.
        This function will be given three arguments: an AST node for the
        entire file, a matching AST node (or list of nodes if the match
        ends up matching something like a function body) and a list of
        matching environments (dictionaries mapping string keys to AST
        nodes). It must return a hashable object, and the number of
        matches will be determined by the cardinality of the set of
        such objects returned by all matching node/environments combos.
        It may also return a list of hashable objects in which case
        they'll each be mixed into the set to be counted.

        This function returns the `Check` object for chaining.
        """
        self._match_identity_function = identity_function

        return self

    def force_smaller(self, force=True):
        """
        Forces a match for this rule to be smaller than the match for its
        super-rule (or smaller than the whole module if there is no
        super-rule). Set force to False to disable this behavior instead
        once it's been enabled (default is disabled).

        Use this to force nested equivalent rules (like two nested Loops)
        to actually match nested structures.

        Returns self for chaining.
        """
        self._force_smaller_match = force

        return self

    def require(self, *checks):
        """
        Adds one or more new sub-rules which much be matched within the
        code matched by this rule in order for a full match to occur. Use
        the `subrule_tolerance` method on the parent `Check` if you want
        to allow some required sub-rules to go unmatched while still
        generating a partial match. Use the `check_callees` method on the
        subrule being added if you want to search for that pattern in
        helper functions as well as in the scope of the match created by
        the parent rule.

        The given `Check` objects will be appended to the subrules field
        of this parent object, which you can use to traverse all subrules
        if you need to. They will also be de-registered as top-level
        `Check`s.

        This function returns the `Check` object for chaining.

        WARNINGS:
        - Only inspects callees where the function position is a name
          (not an arbitrary expression)
        - Searches the top-level task code node for this name
          without understanding shadowing and without considering
          arguments/parameters
        - Attempts to match the full pattern within a single
          function (currently cannot automatically split pattern
          across a call)
        - Likely to cause even more exponential blowup
        - No attempts are made to respect scope when unifying
          env with match environments in callees
        """
        self.subrules.extend(checks)

        # Remove these things from our checklist since they'll be
        # reporting to this check as their parent
        for ch in checks:
            checklist(ch.category, ch.goal_type).remove(ch)

        return self

    def set_identifier(self, identifier):
        """
        Explicitly sets the identifier to the given string. Useful to
        manually disambiguate multiple goals whose identifiers would
        otherwise be the same.

        Returns self for chaining.
        """
        self.identifier = identifier
        return self

    def build_implementation_checks(
        self,
        id_prefix=None,
        prefix=None,
        default_category='core',
        default_goal_type='procedure'
    ):
        """
        Uses the current settings for this `Check` to create one or more
        `potluck.rubrics.ImplementationCheck` objects for use in a
        rubric. Recursively builds any sub-rules first, and disentangles
        categories which is why it might return multiple checks. It
        returns a dictionary mapping category-name/goal-type pairs to
        single `potluck.rubrics.ImplementationCheck` instances for those
        category/goal-type combinations.

        The id_prefix and prefix arguments specify prefixes to add to
        the identifier and description details of subgoals to help keep
        things specific. A prefix will be automatically added to the
        calls to `build_implementation_checks` for any sub-rules, which
        will include the existing prefix.

        The default_category argument specifies what category should be
        used if this `Check`'s category is 'auto', and in the same vein,
        the default_goal_type is used for checks with 'auto' as their
        goal_type.
        """

        # Determine a name for this construct
        if self.name is None:
            # Can't easily pluralize without an explicit name, so we don't try
            name = (self.patterns[0], self.patterns[0])
        else:
            name = self.name

        # Decide on prefixes
        if id_prefix is not None:
            qualified_id = id_prefix + ':' + self.identifier
        else:
            qualified_id = self.identifier

        if self.limits[0] == 1:
            sub_prefix = f"Within the {name[0]}"
        else:
            sub_prefix = f"Within {name[1]}"

        # Create a generic description if there isn't one already
        if self._description is None:
            description = explain.code_check_description(
                self.limits,
                (
                    phrasing.a_an(name[0])
                    if self.limits[0] in (None, 0, 1)
                    else name[1]
                ),
                phrasing.comma_list(
                    [f"<code>{pat}</code>" for pat in self.patterns],
                    junction="or"
                )
            )
        else:
            description = self._description

        if prefix is not None:
            # Adjust the sub-prefix
            sub_prefix = sub_prefix + " " + prefix[0].lower() + prefix[1:]

            # Adjust the description (both pre-feedback and
            # post-feedback details entries if they exist)
            description = list(description)
            description[1::2] = [
                prefix + ', ' + r[0].lower() + r[1:]
                for r in description[1::2]
            ]

        this_cat = self.category
        if this_cat == "auto":
            this_cat = default_category

        this_goal_type = self.goal_type
        if this_goal_type == "auto":
            this_goal_type = default_goal_type

        # Recursively create checks for sub-rules
        subs = []
        all_required_cat_types = set([(this_cat, this_goal_type)])
        for sub in self.subrules:
            sub_checks = sub.build_implementation_checks(
                qualified_id,
                sub_prefix,
                this_cat,
                this_goal_type
            )
            for cat, typ in sub_checks:
                all_required_cat_types.add((cat, typ))
            subs.append(sub_checks)

        return {
            (cat, gt): rubrics.ImplementationCheck(
                taskid=self.taskid,
                identifier=qualified_id,
                pattern=self.patterns,
                name=self.name,
                min=self.limits[0],
                max=self.limits[1],
                description=description,
                match=lambda code, node, env: (
                    all(flt(code, node, env) for flt in self._match_filters)
                ),
                softmin=self._softmin,
                softmax=self._softmax,
                outside=self._outside,
                callees=self._callees,
                subslip=self._subslip,
                match_identity=self._match_identity_function,
                check_in_def=self._check_in_def,
                force_smaller_match=self._force_smaller_match,
                subrules=[s[(cat, gt)] for s in subs if (cat, gt) in s],
                tags={ "category": cat, "goal_type": gt },
                test_in=(
                    None # use parent goal's context
                    if prefix is not None # if there is a parent
                    else self.test_in
                ),
            )
            for (cat, gt) in all_required_cat_types
        }


class Import(Check):
    """
    A `Check` which tests for an import of a certain module. Typically,
    of course, it's not possible to complete a task without importing all
    of the necessary modules, so a positive import goal can be a bit of a
    freebie, but that's not always a bad thing, especially for students
    reading the rubric for hints.

    The identifier will be 'import-' plus the module name for the module
    that must be imported.
    """
    def __init__(
        self,
        mname,
        import_names=None,
        limits=[1, 1],
        category='auto'
    ):
        """
        In addition to the module name and optional limits and category,
        a list of names to import may be specified, in which case the
        check requires a

        ```py
        from <module> import <names>
        ```

        import; otherwise it must be a simple

        ```py
        import <module>
        ```

        import. With import_names, importing more than the required
        names is allowed.

        WARNING (2021-8-31) mast currently DOES NOT support the matching
        rules required to use the from module import names version! A
        warning will be logged if you try to use this, and it may be
        extremely slow and/or fail to recognize valid imports that it
        should.

        If import_names is the special value `'*'`, a universal import
        will be required. `'*'` should not be provided as part of a list
        of specific import names.

        If import_names is the special value `'any'`, then EITHER a
        normal import or a from ... import will be accepted, with no
        restrictions on the names imported.
        """
        patterns = [ f"import {mname}" ]
        what = f"the <code>{mname}</code> module"

        if import_names == '*':
            patterns = [ f"from {mname} import *" ]
            what = f"everything from the <code>{mname}</code> module"
        elif import_names == "any":
            patterns.append(f"from {mname} import *")
            patterns.append(f"from {mname} import ___")
            what = f"the <code>{mname}</code> module or something from it"

        elif import_names is not None:
            # pattern to match
            names = ', '.join(import_names)
            logging.log(
                "Warning: Support for requiring the import of multiple"
                " names from a module is BROKEN."
            ) # TODO: Fix this!
            # TODO [2021-8-31]: mast DOES NOT support this properly!
            patterns = [
                f"from {mname} import {names}, ___"
            ]

            # description of the pattern
            names_desc = phrasing.comma_list(
                f"<code>{name}</code>"
                for name in import_names
            )
            what = f"{names_desc} from the <code>{mname}</code> module"

        super().__init__(
            identifier="import-" + mname,
            patterns=patterns,
            limits=limits,
            name=(f"import of {what}", f"imports of {what}"),
            category=category
        )

        # Set up a custom description (calling .set_description later
        # would override this)
        self.set_description(
            f"Import {what}",
            f"We will check to make sure that you import {what}.",
            f"Import {what}",
            f"We examined your code to check whether it imports {what}."
        )


class FunctionDef(Check):
    """
    A `Function` is a type of `Check` which tests for the presence of a
    function definition (see also `FunctionCall`). Any sub-rules will be
    searched within the body of that function definition.

    The identifier will be "def-" plus the name of the function that must
    be defined.
    """
    def __init__(self, fn_name, params_spec=None, category='auto'):
        """
        You must specify the function name, and you may specify the
        parameters. If given, `params_spec` should be a string containing
        mast code that goes between the parentheses of a function
        definition, or a list or tuple of such strings providing
        alternates (see `potluck.patterns.function_def_patterns`).

        If `params_spec` is omitted, any function signature with the
        specified name is accepted. Instead of a single string, a list of
        strings may also be supplied as `fn_name`, in which case any
        function using one of those names will be considered as a
        potential match.

        You may also supply a rubric category string, which should
        usually be 'core' or 'extra'.
        """
        # determine mast patterns
        def_patterns = patterns.function_def_patterns(fn_name, params_spec)

        # figure out HTML tags for descriptions
        code_tag, details_tag = html_tools.function_def_code_tags(
            fn_name,
            params_spec
        )

        # Initialize the Check
        super().__init__(
            "def-" + fn_name,
            def_patterns,
            [1, 1],  # limits (exactly 1)
            (
                "definition of {}".format(code_tag),
                "definitions of {}".format(code_tag)
            ),  # name (w/ plural version)
            category=category
        )

        # By default, only generate a note if we find multiple
        # fully-matching definitions
        self.softmax("note")

        # Decide topic and details
        topic = "Define {}".format(code_tag)
        details = "Use <code>def</code> to define {}".format(details_tag)

        # Set up a custom description (calling .set_description later
        # would override this)
        self.set_description(topic, details)


class FunctionCall(Check):
    """
    A custom `Check` which checks for the presence of a call to a
    specific function (or to one of several functions).

    Note: Sub-rules aren't typically very useful, as they would be
    matched within the function call expression (not within the
    definition of the called function). You can the `callees` method of
    the super-rule instead of a FunctionCall sub-rule to check for things
    that might be placed in helper functions, or you can use the
    require_of_def method of a FunctionCall to place requirements on the
    AST makeup of the function being called (in conjunction with '_' as
    the fn_name, this provides a means of requiring helper functions that
    meet certain criteria without knowing their names).

    The identifier will be "call-" plus the name of the function that must
    be called, or the name of the first function if multiple are
    specified, or "call-(any)" if the function name isn't specified.
    """
    def __init__(
        self,
        fn_name,
        limits=[1, None],
        args_spec=None,
        announce=None,
        is_method=False,
        category='auto'
    ):
        """
        A function name is required, and everything else is optional. You
        may also pass a list of strings for the function name to count
        multiple different function calls (e.g., when a function has an
        alias, like 'fd' and 'forward' in the 'turtle' module). Use '_'
        as the function name to match any function; the description will
        account for that if you do.

        The `limits` parameter specifies the lower and upper limits on
        the number of calls required. Use `None` in the first (or second)
        position to specify no lower (or upper) limit. The default value
        is `[1, None]` which means "at least one."

        The `args_spec` argument can be used to require a certain
        arrangement of parameters (see
        `potluck.patterns.function_call_patterns`) and may be a string, a
        list of strings, or a pair of integers and/or None similar to
        'limits' specifying how many positional parameters there should
        be (one element of the pair must be an integer for this to work).

        The `announce` argument can be used to override the name of the
        function in the default description, although a custom
        description could also be applied using the `set_description`
        method. Unlike a custom description, an `announce` value is also
        used in the construction of explanation strings.

        Set `is_method` to True if you want to look for calls as methods
        instead of normal function calls. Note that this implies you need
        to know ahead of time how students will import modules, since a
        call to 'turtle.fd' would need to be identified as a method call,
        whereas a call to 'fd' after 'from turtle import *' would not be
        a method call.

        You may also supply a rubric category string, which should
        usually be 'core' or 'extra'.
        """
        if (
            isinstance(args_spec, (list, tuple))
        and len(args_spec) == 2
        and (
                isinstance(args_spec[0], int)
             or isinstance(args_spec[1], int)
            )
        ):
            args_limits = args_spec
            args_spec = "___"
            if args_limits[0] is None: # upper limit only
                args_desc = f"<at most {args_limits[1]} arguments>"
            elif args_limits[1] is None: # lower limit only
                args_desc = f"<at least {args_limits[0]} arguments>"
            else:
                args_desc = (
                    f"<{args_limits[0]}-{args_limits[1]} arguments>"
                )
        elif args_spec is None:
            args_limits = [None, None]
            args_desc = "-any arguments-"
        else:
            args_limits = [None, None]
            args_desc = args_spec

        if fn_name == "_":
            fn_desc = "-any function-"
            identifier = "call-(any)"
        else:
            fn_desc = fn_name
            if isinstance(fn_name, str):
                identifier = "call-" + fn_name
            else:
                identifier = "call-" + fn_name[0]

        # determine mast patterns
        call_patterns = patterns.function_call_patterns(
            fn_name,
            args_spec,
            is_method=is_method
        )

        # figure out HTML tags for descriptions
        code_tag, details_tag = html_tools.function_call_code_tags(
            fn_desc,
            args_desc,
            is_method=is_method
        )

        if announce:
            code_tag = announce

        # Initialize the Check
        super().__init__(
            identifier,
            call_patterns,
            limits,
            (
                "call to {}".format(code_tag),
                "calls to {}".format(code_tag)
            ), # name (w/ plural version)
            category=category,
        )

        # Add a custom match filter if we have argument count limits
        if args_limits != [None, None]:

            self._match_filters.append(
                lambda code, node, env: (
                    len(node.args) >= (args_limits[0] or 0)
                and (
                        (len(node.args) <= args_limits[1])
                        if args_limits[1] is not None
                        else True
                    ) # noqa E123
                )
            )

        description = explain.function_call_description(
            code_tag,
            details_tag,
            limits,
            None
        )

        # Set up a custom description (calling .set_description later
        # would override this)
        self.set_description(*description)

    def require_of_def(self, *subrules):
        """
        Establishes one or more sub-rules that must match on the
        definition of the function being called (which must be defined
        within the current file!).

        Note: this function modifies the provided subrules so that they
        will be set up to check within the definition of their parent.
        For this reason, they should be fresh sub-rules and should NOT be
        shared.

        This function returns the `FunctionCall` object for chaining.
        """
        # TODO: The subrule description-augmentation doesn't quite line
        # up for these, and that needs to be fixed. Ideally, create a
        # secondary list of subrules-in-defs and set up separate
        # description-augmentation logic for those.
        self.subrules.extend(subrules)
        for r in subrules:
            r._check_in_def = True

            # Remove these things from our checklist since they'll be
            # reporting to this check as their parent
            checklist(r.category, r.goal_type).remove(r)

        return self

    def must_be_local(self, exclude=[]):
        """
        Sets up a custom match match filter (via `Check.match_filter`)
        such that matches for this rule must be calls to locally-defined
        functions.

        Note that if you were to store a locally-defined function in a
        local variable of another name and then call it via that
        variable, it wouldn't be recognized as a match. Tracing is
        probably a better approach if you're concerned about such
        situations.

        If exclude is provided, it should be a collection of strings;
        function calls to functions whose names are in that collection
        will not be considered matches.

        This function returns the `FunctionCall` object for chaining.
        """
        self.match_filter(
            lambda code, node, envs: (
                isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id not in exclude
            and mast.find(
                    code,
                    "def {}(___):\n ___".format(node.func.id)
                ) is not None # noqa E123
            )
        )

        return self

    def count_by_names(self):
        """
        Sets up a custom match identity function (via `Check.count_using`
        such that matches for this rule are counted not by how many
        function calls appear, but by how many distinct function names
        are used for calls. If a matching function call doesn't use a
        Name as its func expression, it will not be counted at all. Note
        that this only really makes sense in conjunction with a bindable
        slot as the function name (e.g., '_'), or with multiple possible
        function names.

        Note that if you were to store a function in a variable with
        another name and then call it via that variable, it would be
        counted as a call to a different function. Tracing is probably a
        better approach if you're concerned about such situations.

        This function returns the `FunctionCall` object for chaining.
        """
        # We know that only things matching the filter above will be
        # given to the count_using function as matches, so we know that
        # node.func.id will be valid.
        self.count_using(
            lambda code, node, envs: (
                [] if (
                    not isinstance(node, ast.Call)
                 or not isinstance(node.func, ast.Name)
                ) else node.func.id
            )
        )

        return self


class IfElse(Check):
    """
    An `IfElse` is a `Check` which looks for an `if` or `if`/`else` node,
    and matches sub-rules within either the if or the else part. Note
    that Python turns `elifs` into nested if/else constructs behind the
    scenes, so the `if`/`else` pattern will potentially match once for
    each `elif` case, plus once for the original `if`, and the final
    `else` in an `elif` chain is attached to the last `elif` case, not
    the first `if` case.

    The identifier will be just "ifelse".
    """
    def __init__(self, limits=[1, None], name=None, category='auto'):
        """
        An `IfElse` only needs to specify the limits on how many matches we
        are looking for, and may additionally supply a custom name.

        You may also supply a rubric category string, which should
        usually be 'core' or 'extra'.
        """
        if name is None:
            name = "<code>if</code>/<code>else</code> block"

        super().__init__(
            "ifelse",
            [patterns.IF_PATTERN],
            limits,
            name,
            category=category
        )

        # Customize description a bit since patterns are pretty ugly
        super().set_description(
            *explain.code_check_description(
                limits=self.limits,
                short_desc="a conditional",
                long_desc=(
                    "an <code>if</code> statement (possibly accompanied"
                  + " by an <code>elif</code> or <code>else</code> block)"
                )
            )
        )


class Loop(Check):
    """
    A `Loop` is a `Check` which looks for any kind of looping construct,
    including for loops, while loops, and single list comprehensions (but
    not double list comprehensions).

    The identifier will be just "loop".
    """
    def __init__(
        self,
        limits=[1, None],
        name=None,
        only=None,
        category='auto'
    ):
        """
        Limits may be specified (defaults to 'at least 1'), and a custom
        `name` may also be given. If `only` is given, it should be one of
        the following strings:

            'for' - only accept for loops
            'while' - only accept while loops
            'block' - only accept for and while loops, not list
                comprehensions
            'comprehension' - only accept list comprehensions

        You may also supply a rubric category string, which should
        usually be 'core' or 'extra'.

        Note that any requirements attached to a Loop will be required of
        each loop for that loop to count as a match, so if you want to
        require two loops and require a certain construct be present in
        at least one of them, you should have one Loop check with [2, 2]
        limits and no inner requirements, and another Loop check with [1,
        None] limits (the default) that contains your required construct.
        """
        if name is None:
            name = "loop"

        loop_patterns = patterns.ALL_SINGLE_LOOP_AND_COMPREHENSION_PATTERNS

        if only == 'for':
            loop_patterns = patterns.ALL_FOR_PATTERNS
            loop_name = "a <code>for</code> loop"
        elif only == 'while':
            loop_patterns = patterns.ALL_WHILE_PATTERNS
            loop_name = "a <code>while</code> loop"
        elif only == 'block':
            loop_patterns = patterns.ALL_FOR_AND_WHILE_LOOP_PATTERNS
            loop_name = "a <code>for</code> or <code>while</code> loop"
        elif only == 'comprehension':
            loop_patterns = [
                patterns.SIMPLE_COMPREHENSION_PATTERN,
                patterns.FILTER_COMPREHENSION_PATTERN
            ]
            loop_name = "a list comprehension"
        else:
            loop_name = "any kind of loop"

        super().__init__(
            "loop",
            loop_patterns,
            limits,
            name,
            category=category
        )

        # Customize description a bit since patterns are pretty ugly
        super().set_description(
            *explain.code_check_description(
                limits=self.limits,
                short_desc="a loop",
                long_desc=loop_name
            )
        )


class Return(Check):
    """
    A `Return` is a `Check` which looks for a return statement.

    The identifier will be just "return".
    """
    def __init__(
        self,
        limits=[1, None],
        name=None,
        allow_bare=False,
        category='auto'
    ):
        """
        Limits may be specified (defaults to 'at least 1'), and a custom
        `name` may also be given.

        allow_bare may be set to True (default is False) to allow a bare
        return statement with no value to count.

        You may also supply a rubric category string, which should
        usually be 'core' or 'extra'.
        """
        if name is None:
            name = "<code>return</code> statement"

        patterns = [ "return _" ]
        if allow_bare:
            patterns.append("return")

        super().__init__(
            "return",
            patterns,
            limits,
            name,
            category=category
        )


#-------------#
# Test groups #
#-------------#

def group(base_name, group_name="_", create=False):
    """
    Retrieves a `TestGroup` object for a particular group of tests,
    identified by the name of the thing being tested and the group
    name (defaults to '_', the default group name). Note that the current
    relevant filename and the module in which the `group` function is
    being called are also used to determine which group is returned.

    For import tests, the base name is "import"; for function tests and
    variable value tests, the base name is the name of the function or
    variable being tested (since "import" is a keyword, it is not a valid
    function or variable name).

    The retrieved group's methods may be used to modify it (they
    chain together so you only have to call `group` once). If there are
    no tests matching the given criteria, a `KeyError` will be thrown
    unless create is given as True, in which case a new empty `TestGroup`
    will be created, registered, and returned.
    """
    result = (
        TEST_GROUP_REGISTRY
          .get(file_utils.get_spec_module_name(), {})
          .get(contexts.RELEVANT_FILENAME, {})
          .get(base_name, {})
          .get(group_name, None)
    )

    if result is None:
        if not create:
            raise KeyError(
                f"There are no tests for '{base_name}' in group"
              + f" '{group_name}' The tests registry is:\n"
              + f"{TEST_GROUP_REGISTRY}"
            )
        else:
            result = (
                TEST_GROUP_REGISTRY
                  .setdefault(file_utils.get_spec_module_name(), {})
                  .setdefault(contexts.RELEVANT_FILENAME, {})
                  .setdefault(base_name, {})
                  .setdefault(group_name, TestGroup(base_name, group_name))
            )

    return result


def merge(groups, base_name, group_name="_"):
    """
    Merges several existing groups, returning a new group which contains
    all of the tests from the merged groups, which are de-registered in
    the process. The new group has the given base and group names.

    Note that merge must be called after any operations on the groups to
    be merged, since their tests will be removed, and it MUST be called
    before any switch in the active fiename.

    # TODO: Make this less fragile?
    """
    new = TestGroup(base_name, group_name)
    for group in groups:
        # Re-register tests with the new group
        for test in group.tests:
            test.group = None
            new.add(test)

        # Remove all tests from old group:
        group.tests = []

        # De-register this group
        del TEST_GROUP_REGISTRY\
            [file_utils.get_spec_module_name()]\
            [contexts.RELEVANT_FILENAME]\
            [test.base_name]\
            [test.group_name] # noqa E211
        # TODO: Is it okay to leave empties behind?

    # Register our merged group and return it
    return TEST_GROUP_REGISTRY\
        .setdefault(file_utils.get_spec_module_name(), {})\
        .setdefault(contexts.RELEVANT_FILENAME, {})\
        .setdefault(base_name, {})\
        .setdefault(group_name, new)


class TestGroup(HasPayload, HasContext, HasGoal):
    """
    A class representing a group of tests, with methods that can modify
    the group. In the rubric, each group of tests becomes a single
    `potluck.rubrics.Goal`. Do not create these yourself as they are
    created automatically as `TestCase` objects are defined. Instead,
    call the `group` function to retrieve a test group after one or more
    of its `TestCase` instances have been created.

    Note that a `TestGroup` isn't actually `HasPayload` or `HasContext`
    but serves as a group object for its `TestCase` objects which are.
    """
    def __init__(self, base_name, group_name):
        """
        A group collects tests associated with a particular group name
        and base name. It starts out empty but
        goals are added to
        it automatically. It has various methods for modifying how tests
        are run.
        """
        self.base_name = base_name
        self.group_name = group_name
        if self.group_name == "_":
            group_ident = ""
        else:
            group_ident = ":" + self.group_name

        self.tests = []

        # No payload defaults (left to the Test objects)
        HasPayload.__init__(self)

        # No context defaults (left to the Test objects)
        HasContext.__init__(self)

        # Set up goal defaults (assuming our base name is the name of a
        # function being tested).
        if self.base_name == "import":
            HasGoal.__init__(
                self,
                file_utils.deduce_task_id(),
                rubrics.ComparisonTest,
                default_goal_args={
                    "identifier": "import" + group_ident,
                    "description": (
                        "Your code must exhibit the correct behavior",
                        (
                            "When we run your submitted code as a whole"
                            " file, the pattern of printed output based"
                            " on inputs must match the solution's"
                            " behavior."
                        )
                    ),
                    "context_slot": "output",
                    "checker": compare.omni_compare
                }
            )
        else:
            HasGoal.__init__(
                self,
                file_utils.deduce_task_id(),
                rubrics.ComparisonTest,
                default_goal_args={
                    "identifier": self.base_name + group_ident,
                    "description": (
                        (
                            f"<code>{base_name}</code> must return the"
                            f" correct result"
                        ),
                        (
                            f"The result returned when your"
                            f" <code>{base_name}</code> function is run must"
                            f" match the solution result."
                        )
                    ),
                    "context_slot": "value",
                    "checker": compare.omni_compare
                }
            )

    def add(self, test):
        """
        Adds the given test to this group.

        Throws an error if the test is already in a group.
        """
        if test.group is not None:
            raise ValueError(
                f"Can't add a test ({test}) to a second group ({self.name})."
            )
        self.tests.append(test)
        test.group = self

    def create_goal(self):
        """
        Constructs and returns the `potluck.rubrics.Goal` object implied
        by this `TestGroup`.
        """
        # Create contexts for our goal from each test in this group
        contexts = []
        for test in self.tests:
            payload = test.construct_payload(self)
            # TODO: auto-description here?
            # context_args
            # custom_context_description
            contexts.append(test.create_context(payload, self))

        # Create and return result
        return self.create_goal_from_contexts(contexts)

    def also(self):
        """
        Constructs a new GroupClone based on this test group (or clone).
        Returns the constructed clone. Note that the results of any
        customization methods called before this method will be reflected
        in the clone, but the results of customization methods called
        later will not be. Furthermore, customization methods called on
        the clone will not affect the original.

        However, new `Test` instances which get grouped into this
        `TestGroup` will also be covered by the clone, as long as
        `provide_goal` has not been called yet on either the original or
        the clone.
        """
        return GroupClone(self)


class GroupClone(TestGroup):
    """
    A semi-shallow clone of a test group which creates a separate
    `potluck.rubrics.Goal` based on the same `potluck.contexts.Context`s
    as the original group. Create it using `TestGroup.also` which will
    set it up as a clone of the group (or clone) that `also` was called
    on.

    Method calls on the original object after the call to `also` do not
    affect the goal created by the clone, while methods called on the
    clone do not affect the original object's goal. However, `Test`
    objects created after the creation of the group will be picked up by
    both the original and the clone.

    The goal that the clone creates will have the same base identifier as
    the original goal, although if it's in a different category it will
    have a different qualified identifier. Use `HasGoal.set_identifier`
    to change the identifier if necessary; the ID system will
    automatically append a -number suffix to non-unique identifiers at
    rendering time of course.
    """
    def __init__(self, parent):
        """
        A parent `TestGroup` instance is required (`GroupClone`s are
        also `TestGroup`s). Goal construction parameters for this shadow
        will be cloned from that parent at the time of instantiation.
        """
        self.parent = parent

        # Clone payload info from parent
        HasPayload.__init__(
            self,
            parent.payload_constructor,
            copy.copy(parent.default_payload_args),
            copy.copy(parent.default_augmentations)
        )
        # Copy explicit args as well
        self.payload_args = copy.copy(parent.payload_args)

        # Clone context info from parent
        HasContext.__init__(
            self,
            copy.copy(parent.default_context_args)
        )
        # Copy explicit args as well
        self.context_args = copy.copy(parent.context_args)

        # Clone goal info from parent
        HasGoal.__init__(
            self,
            parent.taskid,
            parent.goal_constructor,
            copy.copy(parent.default_goal_args)
        )
        # Copy explicit args as well
        self.goal_args = copy.copy(parent.goal_args)

        # Copy parent names
        self.base_name = parent.base_name
        self.group_name = parent.group_name

        # Note: we never actually call TestGroup.__init__
        # As a result we do not have tests

    def add(self):
        """
        Override to disable adding tests.
        """
        raise NotImplementedError("Cannot add a test to a cloned group.")

    def create_goal(self):
        """
        Constructs and returns the `potluck.rubrics.Goal` object implied
        by this `GroupClone`.
        """
        # TODO: This breaks a lot of things you might want to do with a
        # clone, since they DON'T get their own contexts, so you can't
        # call something like test_trace and actually get trace. We need
        # better error messages around that, AND/or to fix it!
        # Dig up parent contexts via goal (w/ caching)
        pgoal = self.parent.provide_goal()
        parent_contexts = pgoal.test_in["contexts"]

        # Warn if for some reason we had explicit contexts
        if (
            "test_in" in self.goal_args
        and "contexts" in self.goal_args["test_in"]
        ):
            logging.debug_msg(
                "Warning: overriding existing test_in/contexts value in"
                " GroupClone.create_goal."
            )

        # Return a goal created using our parent's contexts
        return self.create_goal_from_contexts(parent_contexts)


#------------#
# Refinement #
#------------#

class RefinedTest(HasContext, HasGoal):
    """
    Represents further processing of a test result, via a new
    `potluck.rubrics.Goal` object that gets tested in a group of
    `potluck.contexts.Context` objects which are based on extensions of
    the context(s) used for the parent object (or which will be tested in
    a single context which merges information from parent contexts, if
    `_merge` is set). Any `HasGoal` subclass can support refinement (and
    `HasGoal.refine` is the proper way to instantiate refined tests).

    Subclasses should override the `build_context` method to define what
    kind of additional processing they want to do to each context of the
    parent goal. This method needs to accept a context dictionary as its
    only argument (besides self) and return a dictionary of any new
    context slots it creates/updates, just like all context builder
    functions.

    Subclasses may also set the `_merge` property to True instead of the
    default False, which will cause them to derive a single context that
    depends on all of the parent contexts instead of deriving one child
    context per parent context.

    Note that by default the goal constructed will be an
    `potluck.rubrics.ComparisonTest`, and the same context slot as the
    parent will be used as the slot to test. You can use the `HasGoal`
    machinery to change these defaults.

    The refined goal's identifier will be the parent goal's identifier
    plus a colon plus the identifier given to the refined goal.
    """

    _merge = False
    """
    Set this to True in a child class if rather than creating one derived
    context for each parent context, the resulting goal should be tested
    in just a single context that depends on ALL of the parent context
    objects individually.
    """

    def build_context(self, prev_context):
        """
        Not implemented (override to specify how refined contexts are
        created from base contexts).
        """
        raise NotImplementedError(
            "RefinedTest is an abstract class and cannot be used"
            " directly."
        )

    def __init__(
        self,
        parent,
        identifier,
        context_slot=None,
        checker=None
    ):
        """
        A parent object is required; it must have a provide_goal method,
        and should be a `HasGoal` instance.

        An identifier is also required, it will be combined with the
        parent's identifier (separated by a colon).

        A specific context slot to target and checker to use may be
        specified, or if left as defaults these will be inherited from
        the parent object.

        Note that supplying context and/or goal descriptions via
        `HasContext.set_context_description` and/or
        `HasGoal.set_goal_description` is almost always necessary.
        """
        self.parent = parent

        # No context defaults (but note that builder & depends will be
        # overwritten in the end.
        HasContext.__init__(self)

        if context_slot is None:
            context_slot = parent.goal_args.get(
                "context_slot",
                parent.goal_args.get(
                    "context_slot",
                    parent.default_goal_args.get("context_slot", "value")
                )
            )

        if checker is None:
            checker = parent.default_goal_args.get(
                "checker",
                compare.omni_compare
            )

        pident = parent.goal_args.get(
            "identifier",
            parent.default_goal_args.get("identifier")
        )
        if pident is None:
            id_prefix = ""
        else:
            id_prefix = pident + ":"

        # Set up goal defaults
        HasGoal.__init__(
            self,
            parent.taskid,
            rubrics.ComparisonTest,
            default_goal_args={
                "identifier": id_prefix + identifier,
                "context_slot": context_slot,
                "checker": checker
            }
        )

    def create_goal(self):
        """
        Returns the `potluck.rubrics.Goal` implied by this refined test.
        """
        pgoal = self.parent.provide_goal()
        parent_contexts = pgoal.test_in["contexts"]

        if "depends" in self.context_args:
            logging.debug_msg(
                "Warning: overriding existing depends value in"
                " Refine.create_goal."
            )

        # Construct a child context for each parent context
        if self._merge:
            # derive one child context that depends on all parent
            # contexts at once
            self.context_args["depends"] = parent_contexts
            contexts = [ self.create_context(self.build_context) ]
        else: # derive one child context from each parent context
            contexts = []
            for pc in parent_contexts:
                # Create context w/ specific dependency
                self.context_args["depends"] = [ pc ]
                contexts.append(self.create_context(self.build_context))

        # Clean up dependency information for future
        del self.context_args["depends"]

        # Create & return our goal
        return self.create_goal_from_contexts(contexts)


class AlterContext(RefinedTest):
    """
    A `RefinedTest` which simply applies an arbitrary context-builder
    function to the unrefined context. As usual for a context builder,
    the function's results will be updated into the existing context
    automatically. Note that a simpler way to achieve similar
    functionality is to use `HasPayload.do_setup` and/or
    `HasPayload.do_cleanup` to add custom context slots, along with
    `HasGoal.compare_using` to set the context slot to compare.
    """
    def __init__(
        self,
        parent,
        identifier,
        context_builder,
        **kwargs
    ):
        """
        A parent goal provider, an identifier, and a context builder
        function are necessary.

        Further keyword arguments will be passed through to
        `RefinedTest`'s constructor.
        """
        self.builder = context_builder

        super().__init__(
            parent,
            identifier,
            **kwargs
        )

        cs = self.default_goal_args.get("context_slot", "value")

        self.default_context_args["display_product"] = (
            contexts.build_context_value_displayer(
                cs,
                labels=[
                    f"Your {cs}",
                    f"Solution {cs}",
                    "Comparison",
                ]
            )
        )

    def build_context(self, prev_context):
        """
        A context builder that simply runs the specified custom context
        builder function.
        """
        return self.builder(prev_context)


class Transform(RefinedTest):
    """
    A Transform is a kind of refinement which applies an arbitrary
    function to a context slot, sorting the result of that function in
    the same slot. The specific slot that the transformation is applied
    to is implied by the "context_slot" default goal argument of the goal
    being refined, although a specific context slot to target may be
    specified via the arguments passed through to `RefinedTest`.
    """
    def __init__(
        self,
        parent,
        identifier,
        transformer,
        result_desc="a transformed result",
        refine_ref=True,
        **kwargs
    ):
        """
        A parent goal provider, an identifier, and a transformation
        function are necessary. A description for the result may be
        provided if a full custom description isn't being used.
        `refine_ref` may be set to False to avoid also transforming the
        equivalent reference slot.

        Further keyword arguments will be passed through to
        `RefinedTest`'s constructor.
        """
        self.transformer = transformer

        self.refine_ref = refine_ref

        super().__init__(
            parent,
            identifier,
            **kwargs
        )

        cs = self.default_goal_args.get("context_slot", "value")

        # TODO: Some way to name individual parent contexts here...
        self.default_context_args["description"] = (
            f"{result_desc} of the {cs}".capitalize(),
            f"We will create {result_desc} from the {cs}.",
            f"{result_desc} of the {cs}".capitalize(),
            f"We created {result_desc} from the {cs}.",
        )

        self.default_context_args["display_product"] = (
            contexts.build_context_value_displayer(
                cs,
                labels=[
                    f"Your {cs}",
                    f"Solution {cs}",
                    "Comparison",
                ]
            )
        )

        self.default_goal_args["description"] = (
            f"{result_desc} of the {cs} must be correct".capitalize(),
            f"{result_desc} of the {cs} must match the solution's {cs}.",
            f"{result_desc} of the {cs} must be correct".capitalize(),
            (
                f"We checked whether {result_desc} of the {cs} matched"
                f" the solution's {cs}."
            )
        )

    def build_context(self, prev_context):
        """
        A context builder that replaces certain context fields with the
        results of running a transformation function over them.
        """
        result = {}
        # TODO: Args synthesis here?!?
        context_slot = self.default_goal_args.get("context_slot", "value")
        target_slots = [ context_slot ]
        if self.refine_ref:
            target_slots.append("ref_" + context_slot)

        for slot in target_slots:
            orig = context_utils.extract(prev_context, slot)
            transformed = self.transformer(orig)
            result[slot] = transformed

        return result


class Find(RefinedTest):
    """
    A Find is a kind of refinement which applies a regular expression to
    a context slot (which we hope will be holding a string).
    """
    def __init__(
        self,
        parent,
        pattern,
        pattern_desc="a specific part",
        missing_result=None,
        first_match=True,
        match_details=False,
        refine_ref=True,
        **kwargs
    ):
        """
        A parent goal provider and a pattern (either a string or a
        compiled regular expression) are necessary.

        The identifier will be based on replacing spaces in the pattern
        description with underscores.

        Behavior may be controlled by the following keyword arguments:

        - `pattern_desc`: A string that will be used to provide automatic
            context and goal descriptions. Use `set_context_description`
            and/or `set_goal_description` if this isn't expressive
            enough.
        - `first_match`: If set to False, the result will be a (possibly
            empty) list of all matches. If set to True (the default) only
            the first match is used, and None is used if there are no
            matches.
        - `missing_result`: A value to use if no match is found and
            first_match is set to True.
        - `match_details`: If True, the result will take the form of one
            or more re.Match objects instead of strings.
        - `refine_ref`: If True, the "ref_" context slot that matches the
            target context slot will be refined in addition to the base
            slot.

        Further keyword arguments will be passed through to
        `RefinedTest`'s constructor.

        Note that only very generic default context and goal descriptions
        are provided.
        """
        self.pattern = pattern
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern)

        self.first_match = first_match
        self.missing_result = missing_result
        self.match_details = match_details
        self.refine_ref = refine_ref

        if "identifier" not in kwargs:
            kwargs["identifier"] = pattern_desc.replace(' ', '_')

        super().__init__(parent, **kwargs)

        cs = self.default_goal_args.get("context_slot", "value")

        # TODO: Some way to name individual parent contexts here...
        self.default_context_args["description"] = (
            f"{pattern_desc} of the {cs}".capitalize(),
            f"We will search through the {cs} for {pattern_desc}.",
            f"{pattern_desc} of the {cs}".capitalize(),
            f"We searched through the {cs} for {pattern_desc}.",
        )

        self.default_context_args["display_product"] = (
            contexts.build_context_value_displayer(
                cs,
                labels=[
                    f"Your {cs}",
                    f"Solution {cs}",
                    "Comparison",
                ]
            )
        )

        self.default_goal_args["description"] = (
            f"{pattern_desc} of the {cs} must be correct".capitalize(),
            f"{pattern_desc} of the {cs} must match the solution's {cs}.",
            f"{pattern_desc} of the {cs} must be correct".capitalize(),
            (
                f"We checked whether {pattern_desc} of the {cs} matched"
                f" the solution's {cs}."
            )
        )

    def build_context(self, prev_context):
        """
        A context builder that replaces certain context fields with the
        results of running a regular expression over them.
        """
        result = {}
        # TODO: Args synthesis here?!?
        context_slot = self.default_goal_args.get("context_slot", "value")
        target_slots = [ context_slot ]
        if self.refine_ref:
            target_slots.append("ref_" + context_slot)

        for slot in target_slots:
            orig = context_utils.extract(prev_context, slot)
            if not isinstance(orig, str):
                raise TypeError(
                    (
                        "Attempted to refine '{}' context, but it was "
                      + "not a string."
                    ).format(slot)
                )

            matches = self.pattern.finditer(orig)

            if self.first_match:
                try:
                    first = next(matches)
                    if self.match_details:
                        result[slot] = first
                    else:
                        result[slot] = first.group()
                except StopIteration:
                    result[slot] = self.missing_result
            else:
                if self.match_details:
                    objs = [m for m in matches]
                else:
                    objs = [m.group() for m in matches]

                result[slot] = objs

        return result


class DistinctionReport(RefinedTest):
    """
    A `RefinedTest` which analyzes results from the context slot
    originally targeted, and determines, among parent contexts that were
    originally going to be separate tests, which results are distinct and
    which are identical. It creates a "distinctions" context slot
    containing a multi-line string reporting on these distinctions, and
    sets up that slot as the test target.
    """
    _merge = True # we are going to merge parent contexts

    def build_context(self, prev_context):
        """
        Uses the "__unmerged__" special context slot to access
        individual results from each parent context, and creates a
        mapping in the "distinctions" slot that maps unique results to
        lists of context dictionaries in which the test produced those
        results (note that this means that results must be hashable!).

        The slot of each parent context that it pays attention to is
        determined by the slot which the unrefined goal would have
        tested.
        """
        result = { "distinctions": {}, "ref_distinctions": {} }

        # Process both actual and reference values
        for prefix in ("", "ref_"):
            slot = prefix + self.original_slot
            dest = prefix + "distinctions"

            # produce our mapping from results to lists of contexts
            mapping = {}
            for i, parent_context in enumerate(
                prev_context["__unmerged__"]
            ):
                # get value and signature
                val = parent_context[slot]
                if self.filters:
                    for filt in self.filters:
                        val = filt(val)
                # update our mapping
                mapping.setdefault(val, []).append(parent_context)

            result[dest] = mapping

        return result

    def render(report):
        """
        A class method for rendering a distinction report as HTML.
        """
        uniques = []
        groups = []
        all_contexts = []
        for result in report:
            contexts = report[result]
            all_contexts.extend(contexts)
            if len(contexts) == 1:
                uniques.append(contexts[0])
            else:
                groups.append(contexts)

        if len(groups) == 0:
            return (
                f"All {len(all_contexts)} contexts produced distinct"
                f" outcomes:<br>\n"
            ) + html_tools.build_list(
                ctx["__builder__"].feedback_topic()
                for ctx in all_contexts
            )
        elif len(uniques) == 0 and len(groups) == 1:
            return (
                f"All {len(all_contexts)} contexts produced equivalent"
                f" outcomes:<br>\n"
            ) + html_tools.build_list(
                ctx["__builder__"].feedback_topic()
                for ctx in all_contexts
            )
        else:
            items = [
                f"Group #{i+1}:<br>\n" + html_tools.build_list(
                    ctx["__builder__"].feedback_topic()
                    for ctx in group
                )
                for i, group in enumerate(groups)
            ] + [
                "Unique: " + ctx["__builder__"].feedback_topic()
                for ctx in uniques
            ]
            return (
                "The contexts' outcomes were grouped as follows:\n"
            ) + html_tools.build_list(items)

    def display_context_value(context):
        """
        A class method to be used as a context value displayer.
        """
        val = context["distinctions"]
        ref = context["ref_distinctions"]

        return html_tools.build_html_tabs(
            [
                ("Your distinctions", DistinctionReport.render(val)),
                ("Correct distinctions", DistinctionReport.render(ref)),
            ]
        )

    def compare(val, ref):
        """
        A class method for comparing distinction mappings. Succeeds if
        the mappings have equivalent groupings with respect to the
        `potluck.contexts.Context` objects that produce different
        results, and fails otherwise.
        """
        val_rmap = {}
        ref_rmap = {}

        val_groups = []
        ref_groups = []

        for result in val:
            contexts = val[result]
            val_groups.append(
                set(id(context["__builder__"]) for context in contexts)
            )
            for context in contexts:
                val_rmap[id(context["__builder__"])] = result

        for result in ref:
            contexts = ref[result]
            ref_groups.append(
                set(id(context["__builder__"]) for context in contexts)
            )
            for context in contexts:
                ref_rmap[id(context["__builder__"])] = result

        # Make sure ordering is the same because it shouldn't matter
        val_groups.sort(key=lambda group: sorted(group))
        ref_groups.sort(key=lambda group: sorted(group))

        # Groupings are the same
        if val_groups == ref_groups:
            return {
                "status": "accomplished",
                "explanation": (
                    "The distinctions among the results of your code"
                    " were the same as the distinctions among results"
                    " for the solution code:<br>"
                ) + DistinctionReport.render(val)
            }
        else:
            return {
                "status": "failed",
                "explanation": (
                    "The distinctions among the results of your code"
                    " were different than the distinctions among"
                    " results for the solution:<br>"
                ) + html_tools.build_html_tabs(
                    [
                        (
                            "Your distinctions",
                            DistinctionReport.render(val)
                        ),
                        (
                            "Correct distinctions",
                            DistinctionReport.render(ref)
                        )
                    ]
                    # TODO: Add a tab reporting differences in terms of
                    # pairwise constraints violated?
                )
            }

    def __init__(
        self,
        parent,
        filters=None,
        **kwargs
    ):
        """
        Only a parent is required; extra keyword arguments will be
        passed on to `RefinedTest.__init__`.

        `filters` allows one to specify a list of filter functions, which
        will be applied to the raw result values that are being
        distinguished.

        The identifier will be "distinctions".
        """
        super().__init__(
            parent,
            "distinctions",
            **kwargs
        )

        self.filters = filters or []

        # Fetch the old context slot and set our new one
        cs = self.default_goal_args.get("context_slot", "value")
        # TODO: Args synthesis here?!?
        self.original_slot = cs
        self.default_goal_args["context_slot"] = "distinctions"

        # Set a goal-type tag based on the parent slot
        tags = self.default_goal_args.setdefault("tags", {})
        tags["goal_type"] = CONTEXT_SLOT_IMPLIED_TYPES.get(cs, "other")

        # TODO: Some way to name individual parent contexts here...
        self.default_context_args["description"] = (
            f"Distinctions between {cs}s",
            (
                f"We gather {cs}s from multiple tests and check which"
                f" tests have distinct results."
            ),
            f"Distinctions between {cs}s",
            (
                f"We gathered {cs}s from multiple tests and checked"
                f" which tests had distinct results."
            )
        )

        self.default_context_args["display_product"] = (
            DistinctionReport.display_context_value
        )

        self.default_goal_args["description"] = (
            f"{cs} distinctions must be correct".capitalize(),
            (
                f"Distinctions between {cs}s based on arguments and/or"
                f" inputs must match the solution's distinctions."
            ),
            f"{cs} distinctions must be correct".capitalize(),
            (
                f"We checked whether, for different arguments and/or"
                f" inputs, your code created the same distinct (or"
                f" identical) {cs}s as the solution code."
            )
        )

        # Set up report-based comparison
        self.compare_using(DistinctionReport.compare)


class Reference:
    """
    A class used for representing object references in memory maps and
    diagrams. A reference us really just an integer.
    """
    def __init__(self, num):
        """
        Needs to know what number we're assigned.
        """
        self.num = num

    def __hash__(self):
        """
        Hash function based on the number.
        """
        return 1928928 + self.num

    def __eq__(self, other):
        """
        Comparison for references (two refs with the same num are the
        same).
        """
        return self.num == other.num

    def __repr__(self):
        """
        The representation is an @ sign followed by the integer.
        """
        return "@{}".format(self.num)


def memory_map(obj, assigned, count_from=0):
    """
    Modifies the given assignment dictionary to include an assignment
    between the given object's ID and a tuple containing the current
    counter (the third arugment) and a shallow object based on the given
    object, where any complex sub-objects replaced by References which
    will also appear in the assignment map. The assignment map provided
    to start from must be a dictionary, but it may be empty.

    For example, if the original value were the list [[1, 2], 3, [1, 2]]
    where both [1, 2] sublists are the same list, the final `assigned`
    dictionary would be:

    {
        <id1>: (0, [ Reference(1), 3, Reference(1) ]),
        <id2>: (1, [1, 2])
    }

    Where <id1> and <id2> are the ids of the two lists.

    This function returns a tuple containing the highest ID it assigned
    within the assignments, and the provided object if it's small, or a
    Reference instance if it's large. Only tuples, lists, sets, and
    dicts have their contents replaced; custom objects don't. Strings
    are treated as references, but of course not altered, and any custom
    objects are treated this way too.
    """
    if id(obj) in assigned:
        return None, Reference(assigned[id(obj)][0])

    if isinstance(obj, (int, float, complex, bool, type(None))):
        # Simple values are used as-is:
        return None, obj
    elif isinstance(obj, (tuple, list, set)):
        # Structures are made shallow and referenced
        original_n = count_from
        # Must happen before recursion
        assigned[id(obj)] = (original_n, None) # placeholder
        count_from += 1
        parts = []
        for sub in obj:
            highest_id, repl = memory_map(sub, assigned, count_from)
            parts.append(repl)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs
        shallow = type(obj)(parts)
        assigned[id(obj)] = (original_n, shallow)
        return count_from - 1, Reference(original_n)
    elif isinstance(obj, dict):
        # Dictionaries use references for both keys and values
        original_n = count_from
        count_from += 1
        shallow = {}
        # Must happen before recursion
        assigned[id(obj)] = (original_n, shallow)
        for key in obj:
            highest_id, krepl = memory_map(key, assigned, count_from)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs
            highest_id, vrepl = memory_map(obj[key], assigned, count_from)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs

            # Insert key/value pair
            shallow[krepl] = vrepl

        return count_from - 1, Reference(original_n)
    else:
        # All other values including strings  are referenced but not
        # made shallow
        assigned[id(obj)] = (count_from, obj)
        return count_from, Reference(count_from)


def memory_report(obj):
    """
    Returns a memory report, which is like an exploded repr of an object
    where 'large' values like strings and lists get assigned an ID and
    are reported on a separate line.
    """
    refs = {}
    _ = memory_map(obj, refs, 0) # modifies ref; we ignore the result

    result = ''
    for num, shallow in sorted(refs.values()):
        result += '@{}: {}\n'.format(num, repr(shallow))

    return result


class MemoryDiagram(RefinedTest):
    """
    A `RefinedTest` which produces a text-based memory diagram from the
    contents of the context slot originally targeted. It creates a
    "memory_report" context slot
    containing a multi-line string which specifies the memory layout of
    the original object, which may contains tuples. lists, dictionaries,
    and/or sets, as well as primitive values like numbers, Booleans,
    strings, and Nones. It sets up that slot as the test target.
    """
    def build_context(self, prev_context):
        """
        Based on the original target slot, creates a "memory_report"
        slot which holds a multi-line string representing the memory
        layout of the original object. See the `memory_report` function
        for details on what the diagram will look like.
        """
        result = {
            "memory_report": 'NO REPORT GENERATED',
            "ref_memory_report": 'NO REPORT GENERATED'
        }

        # Process both actual and reference values
        for prefix in ("", "ref_"):
            slot = prefix + self.original_slot
            dest = prefix + "memory_report"

            # produce our mapping from results to lists of contexts
            result[dest] = memory_report(prev_context[slot])

        return result

    def __init__(
        self,
        parent,
        **kwargs
    ):
        """
        Only a parent is required; extra keyword arguments will be
        passed on to `RefinedTest.__init__`.

        The identifier will be "memory_report".
        """
        super().__init__(
            parent,
            "memory_report",
            **kwargs
        )

        # Fetch the old context slot and set our new one
        cs = self.default_goal_args.get("context_slot", "value")
        # TODO: Args synthesis here?!?
        self.original_slot = cs
        self.default_goal_args["context_slot"] = "memory_report"

        # Set a goal-type tag based on the parent slot
        tags = self.default_goal_args.setdefault("tags", {})
        tags["goal_type"] = CONTEXT_SLOT_IMPLIED_TYPES.get(cs, "other")

        self.default_context_args["description"] = (
            f"Memory report of the {cs}",
            (
                f"We will produce a memory report from the {cs} which"
                f" indicates the structure of the value in memory,"
                f" including which parts are aliases of each other."
            ),
            f"Memory report of the {cs}",
            (
                f"We produced a memory report from the {cs} which"
                f" indicates the structure of the value in memory,"
                f" including which parts are aliases of each other."
            )
        )

        self.default_context_args["display_product"] = (
            contexts.build_context_value_displayer(
                "memory_report",
                labels=[
                    "Your memory report:",
                    "Solution memory report:",
                    "Differences"
                ]
            )
        )

        self.default_goal_args["description"] = (
            f"The {cs} must have the correct memory structure",
            (
                f"The memory structure of the {cs} produced by your code"
                f" must match that of the {cs} produced by the solution"
                f" code, including which parts are aliases of each other."
            ),
            f"The {cs} must have the correct memory structure",
            (
                f"We checked whether the memory structure of the {cs}"
                f" produced by your code matched the memory structure"
                f" produced by the solution code."
            )
        )

        # Set up report-based comparison
        self.compare_reports()


#-------------#
# Extra Goals #
#-------------#


def NoParseErrors(category="core"):
    """
    Registers a miscellaneous goal requiring that there not be any parse
    errors.

    The goal is a `potluck.rubrics.NoParseErrors` instance.
    """
    register_goal(
        rubrics.NoParseErrors(
            file_utils.deduce_task_id(),
            tags={ "category": category }
        )
    )


def RequireDocstrings(exclude=None, category="core"):
    """
    Registers a miscellaneous goal requiring that all functions have
    non-empty docstrings. Capitalized to feel like Test or Check, but not
    a class because it has no reason to be.

    A list of strings specifying function names to exclude may be given,
    and is useful for preventing penalties for students who choose not to
    do optional tasks.

    A category other than the default 'core' may also be specified.

    The goal is a `potluck.rubrics.AllFunctionsHaveDocstrings` instance.
    """
    register_goal(
        rubrics.AllFunctionsHaveDocstrings(
            file_utils.deduce_task_id(),
            exclude,
            tags={ "category": category }
        )
    )


# Builtin functions & methods we use with ARE fruitful
FRUITFUL_BUILTINS = [
    'input',
    'max', 'min',
    'round',
    'ceil', '.ceil', 'floor', '.floor',
    'len',
    'int', 'float', 'str', 'repr', 'list', 'tuple', 'dict', 'set', 'type',
    'range', 'reversed',
    '.lower', '.upper', '.capitalize'
    '.startswith', '.endswith',
    '.isspace', '.isalpha', '.isdigit', '.isnumeric', '.isalnum',
    '.format',
    '.join', '.split',
    '.index',
    '.keys', '.values', '.items',
    '.get',
    # Note: .pop is very often used legitimately without actually needing
    # the return value, so we don't include it as a fruitful function
    # here
    # '.pop',
]
"""
A list of fruitful built-in functions and methods, for use with
`DontWasteFruit` and/or `DontWasteBoxes`.
"""


# Buitin functions and methods we use which are NOT fruitful
NON_FRUITFUL_BUILTINS = [
    'print',
    '.append',
    '.insert',
    '.extend',
    '.remove',
    '.update',
]
# Note that we *don't* include .pop in this list either!
"""
A list of non-fruitful built-in functions and methods, for use with
`DontWasteFruit` and/or `DontWasteBoxes`.
"""


def DontNestFunctions(exclude=None, category='core', description=None):
    """
    Registers a miscellaneous goal requiring that within the code of the
    submission, there aren't any function definitions within other
    definitions. A list of function names to exclude from the check may
    be provided, and a category other than the default 'core' may also be
    provided. Finally, a custom description tuple can be supplied,
    although in most situations the default should be fine.

    The goal is a `potluck.rubrics.FunctionsArentNested` instance.
    """
    args = {
        "exclude": exclude,
        "tags": {"category": category}
    }
    if description is not None:
        args["description"] = description

    register_goal(
        rubrics.FunctionsArentNested(
            file_utils.deduce_task_id(),
            **args
        )
    )


def DontWasteFruit(
    extra=FRUITFUL_BUILTINS,
    exclude=[],
    category="extra",
    description=None
):
    """
    Registers a miscellaneous goal requiring that the submitted code
    doesn't ignore return values from fruitful functions. See
    `potluck.rubrics.DoesntWasteFruit`.
    """
    args = {
        "extra": extra,
        "exclude": exclude,
        "tags": { "category": category },
    }
    if description is not None:
        args["description"] = description

    register_goal(
        rubrics.DoesntWasteFruit(
            file_utils.deduce_task_id(),
            **args
        )
    )


def DontWasteBoxes(
    exclude=[],
    category="extra",
    tolerance=2,
    description=None
):
    """
    Registers a miscellaneous goal requiring that within the code of the
    submission, there aren't any unused variables, unless they're named
    '_'. See `potluck.rubrics.DoesntWasteBoxes`.
    """
    args = {
        "exclude": exclude,
        "tolerance": tolerance,
        "tags": { "category": category },
    }
    if description is not None:
        args["description"] = description

    register_goal(
        rubrics.DoesntWasteBoxes(
            file_utils.deduce_task_id(),
            **args
        )
    )


#------------------#
# Validation Goals #
#------------------#

def RequireTestCases(
    requirements,
    category="core",
    description=None
):
    """
    Registers a validation goal requiring that the submitted code
    creates a certain number of expectations (using the `optimism`
    module) for each of certain target functions and/or files.
    `requirements` must be a dictionary mapping function name strings
    (which can't end in '.py') and/or file name strings (which do end in
    '.py') that need testing to the minimum number of test cases
    required for each. A custom category and description may be
    provided; the default category is core. The underlying goal created
    is a `potluck.validation.DefinesEnoughTests`.
    """
    args = { "tags": { "category": category } }
    if description is not None:
        args["description"] = description

    # Sort out function/file requirements
    function_reqs = {}
    file_reqs = {}
    for req in requirements:
        if req.endswith('.py'):
            file_reqs[req] = requirements[req]
        else:
            function_reqs[req] = requirements[req]

    args["function_reqs"] = function_reqs
    args["file_reqs"] = file_reqs

    register_validation_goal(
        validation.DefinesEnoughTests(
            file_utils.deduce_task_id(),
            **args
        )
    )


def TestsMustPass(
    category="extra",
    description=None
):
    """
    Registers a validation goal requiring that all test cases checked by
    the submitted code (using the `optimism` module) must pass (when run
    against the solution code during validation). The goal is a
    `potluck.validation.ChecksSucceed`. A category (other than the
    default "extra") and a custom description are optional.
    """
    args = { "tags": { "category": category } }
    if description is not None:
        args["description"] = description

    register_validation_goal(
        validation.ChecksSucceed(
            file_utils.deduce_task_id(),
            **args
        )
    )


#-----------------#
# Rubric creation #
#-----------------#

def rubric():
    """
    Creates a `potluck.rubrics.Rubric` based on the test and check
    objects instantiated within the current module.
    """
    validation_goals = []
    evaluation_goals = []

    # Name of the specifications module this function is being called in
    sname = file_utils.get_spec_module_name()

    # Directly-registered validation goals
    validation_goals.extend(VALIDATION_GOALS.get(sname, []))

    # Goals via providers
    for provider in VALIDATION_GOAL_PROVIDERS.get(sname, []):
        try:
            validation_goals.append(provider.provide_goal())
        except Exception:
            raise ValueError(
                "Unable to create validation goal from: " + repr(provider)
            )
            # TODO: Better reporting (e.g., which line goal was defined on)

    # Directly-registered evaluation goals
    evaluation_goals.extend(GOALS.get(sname, []))

    # Goals via providers
    for provider in GOAL_PROVIDERS.get(sname, []):
        try:
            evaluation_goals.append(provider.provide_goal())
        except Exception:
            raise ValueError("Unable to create goal from: " + repr(provider))
            # TODO: Better reporting (e.g., which line goal was defined on)

    # Checks
    checks = CHECKS_REGISTRY.get(sname, {})
    for cat in checks:
        cat_registry = checks[cat]
        for goal_type in cat_registry:
            list_of_checks = cat_registry[goal_type]
            for check_obj in list_of_checks:
                cat_gt_map = check_obj.build_implementation_checks()
                evaluation_goals.extend(cat_gt_map.values())

    # Result
    return rubrics.Rubric(
        evaluation_goals,
        rubrics.core_extras_categorized_metric,
        validation_goals,
        file_utils.get_spec_file_name()
    )


#-----------------#
# Context control #
#-----------------#

_PREP_FUNCTIONS = []
"""
A list of prep functions to apply on module import. Note that these
don't apply to `TestImport` contexts, which use
`HasPayload.prepare_source` for that purpose.
"""

_WRAPPERS = []
"""
A list of wrapper functions to apply on module import. Note that these
don't apply to `TestImport` contexts, which use `HasPayload.wrap_module`
for that purpose.
"""


def file(filename):
    """
    After calling this function, subsequent tests, checks, etc. will all
    by default run against the submitted file with the given filename,
    rather than the default submitted file. Can be called multiple times
    to establish segments of the spec file that apply to different
    submitted files.

    Calling this function will reset any establish prep and/or wrap
    functions.

    TODO: What if a lower-level auto-context has been established, such
    that changing the File auto-context doesn't matter?!?

    TODO: Test this!
    """
    global _PREP_FUNCTIONS, _WRAPPERS
    _PREP_FUNCTIONS = []
    _WRAPPERS = []
    contexts.FileContext(filename)
    contexts.ModuleContext()


def add_module_prep(prep_fn):
    """
    Adds an additional module prep function to the list of active module
    prep functions, to be run when a submitted module is imported for
    testing. The prep function will be applied to imports for tests
    below where this Function is called; `TestImport` imports are not
    affected because they use `HasPayload.prepare_source` instead.

    The prep function must accept a context dictionary as an argument,
    and should return the same dictionary (or a modified dictionary). If
    a zero-argument function is provided, it will be modified to accept
    and return a context dictionary without alteration.
    """
    global _PREP_FUNCTIONS
    _PREP_FUNCTIONS.append(prep_fn)
    activate_preps_and_wraps()


def add_module_wrapper(wrapper):
    """
    Adds an additional module wrapper function to the list of active
    module wrapper functions, to be run when a submitted module is
    imported for testing. The wrapper function will be applied to
    imports for tests below where this Function is called; `TestImport`
    imports are not affected because they use `HasPayload.wrap_module`
    instead.

    The wrap function must accept the imported module as an argument,
    and its return value will be used in place of that module. If a
    zero-argument function is provided, it will be modified to accept
    and return a module without alteration.
    """
    global _WRAPPERS
    _WRAPPERS.append(wrapper)
    activate_preps_and_wraps()


def activate_preps_and_wraps():
    """
    Activates the current prep/wrap function lists by constructing a
    `contexts.ModuleContext` using them.
    """
    def do_prep(ctx):
        """
        Combined prep function
        """
        for fn in _PREP_FUNCTIONS:
            if fn.__code__.co_argcount == 0:
                fn()
            else:
                ctx = fn(ctx)
        return ctx

    def do_wrap(mod):
        """
        Combined module wrapper.
        """
        for fn in _WRAPPERS:
            if fn.__code__.co_argcount == 0:
                fn()
            else:
                mod = fn(mod)

        return mod

    contexts.ModuleContext(prep=do_prep, wrap=do_wrap)
