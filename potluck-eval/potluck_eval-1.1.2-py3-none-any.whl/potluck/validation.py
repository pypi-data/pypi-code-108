"""
Machinery for defining requirements for tests. Tests are submitted in a
separate file using the `optimism` library, and we can require a certain
number of distinct test cases that target specific functions/files, and
require that all of the checks succeed.

The validation machinery runs the submitted tests file in a directory
with the solution code and checks what test cases it checks and whether
those checks succeed. `rubrics.Rubric.validate_tests` can then be used
to generate a report based on all validation goals; the goals in this
file should normally be used as validation goals, not evaluation goals.
"""

from . import rubrics
from . import contexts
from . import context_utils
from . import phrasing
from . import html_tools


#---------------------------------------#
# Goal subtypes for checking test cases #
#---------------------------------------#

class CasesTest(rubrics.Goal):
    """
    Runs a function against the auto-context for "validation_test_cases".
    Inherit and override the `check` method with a function that accepts
    a context and returns a goal evaluation result to define your test.

    Note that these can only be used when the 'optimism' module is
    available.
    """
    def check(self, context):
        """
        Not implemented; override to define specific tests.
        """
        raise NotImplementedError(
            "CasesTest is an abstract class that can't be used"
            " directly."
        )

    def __init__(
        self,
        taskid,
        identifier,
        description=(
            "BLANK EXPECTATIONS TEST",
            "THIS GOAL HAS NOT BEEN DEFINED"
        ),
        goal_type="testing",
        uses_slots=("validation_test_cases",),
        **kwargs
    ):
        """
        In addition to a task ID, an identifier, and a description, a
        goal type may be supplied other than the default "testing".

        The categorizer "tests:" will be prepended to the given
        identifier.

        The slots required should be given as uses_slots, and a relevant
        context will be selected or created as the testing context. By
        default the "validation_test_cases" slot is the only one used.

        Any extra arguments are passed through to the `rubrics.Goal`
        constructor.
        """
        # Auto context dependency based on uses_slots
        depends = contexts.auto(*uses_slots)
        if len(depends) == 1:
            test_context = depends[0]
        else:
            # TODO: De-duplicate stuff where one context actually
            # provides everything needed via inheritance but auto
            # doesn't see that?
            test_context = contexts.Context(
                description=(
                    "Test cases defined by your code",
                    (
                        "The " + phrasing.comma_list(
                            slot.replace("_", " ")
                            for slot in uses_slots
                        )
                      + " of your code."
                    )
                ),
                builder=lambda ctx: ctx,
                depends=depends
            )

        if "test_in" not in kwargs:
            kwargs["test_in"] = {}
        if "contexts" not in kwargs["test_in"]:
            kwargs["test_in"]["contexts"] = [ test_context ]

        # Specified goal type
        if "tags" not in kwargs:
            kwargs["tags"] = {}
        kwargs["tags"]["goal_type"] = goal_type

        # Set up rubrics.Goal stuff
        super().__init__(
            taskid,
            "tests:" + identifier,
            description,
            **kwargs
        )

    # subgoals is inherited (no subgoals)

    # table is inherited

    def evaluate_in_context(self, context=None):
        """
        Runs the checker and returns its result.
        """
        context = context or {}

        try:
            self.result = self.check(context)

            if self.result is None:
                raise ValueError(
                    f"Test case check for {self.__class__.__name__}"
                    f" returned None!"
                )
        except Exception:
            self.result = {
                "status": "failed",
                "traceback": html_tools.html_traceback(
                    linkable=context_utils.linkmap(context)
                )
            }
            self.set_explanation(
                context,
                status="crash",
                default=html_tools.html_traceback(
                    title="Error while checking your test cases.",
                    linkable=context_utils.linkmap(context)
                )
            )
            return self.result

        self.set_explanation(
            context,
            default=self.result["explanation"]
        )

        return self.result


class DefinesEnoughTests(CasesTest):
    """
    A test cases checker which ensures that for each of certain listed
    functions (or files), a certain number of distinct test cases are
    established (using the `optimism` module).

    Note that functions are specified by name to be matched against
    __name__ attributes of actual functions checked, so if you're testing
    methods you just use the method name, and testing decorated functions
    may be tricky. (TODO: Check if this plays nicely with spec-specified
    decorations.)

    Test cases are counted as distinct if either their arguments or their
    provided inputs differ.
    """
    def __init__(self, taskid, function_reqs, file_reqs, **kwargs):
        """
        A task ID is required. The other required arguments are two
        dictionaries mapping function name strings and then filename
        strings to integers specifying how many tests are required.

        Other arguments get passed through to `CasesTest` and
        potentially thence to `rubrics.Goal`.

        The identifier will be "defines_enough".
        """
        self.function_reqs = function_reqs
        self.file_reqs = file_reqs

        # Check types for function requirements keys and values
        for fname in function_reqs:
            if not isinstance(fname, str):
                raise TypeError(
                    (
                        "Each function requirement must be a string."
                        " (You used {} as a key, which is a {})."
                    ).format(
                        repr(fname),
                        type(fname)
                    )
                )

            val = function_reqs[fname]
            if not isinstance(val, int):
                raise TypeError(
                    (
                        "Each function requirement must use an integer"
                        " as the value. (requirement with key {} had"
                        " value {} which is a {})."
                    ).format(
                        repr(fname),
                        repr(val),
                        type(val)
                    )
                )

        # Check types for file requirements keys and values
        for filename in file_reqs:
            if not isinstance(filename, str):
                raise TypeError(
                    (
                        "Each file requirement must be a string."
                        " (You used {} as a key, which is a {})."
                    ).format(
                        repr(filename),
                        type(filename)
                    )
                )

            val = file_reqs[filename]
            if not isinstance(val, int):
                raise TypeError(
                    (
                        "Each file requirement must use an integer as"
                        " the value. (requirement with key {} had"
                        " value {} which is a {})."
                    ).format(
                        repr(filename),
                        repr(val),
                        type(val)
                    )
                )

        # Check if optimism is available
        try:
            import optimism # noqa F401
        except Exception:
            raise NotImplementedError(
                "DefinesEnoughTests cannot be used because the"
                " 'optimism' module cannot be imported."
            )

        # Set automatic description
        if "description" not in kwargs:
            rlist = [
                "Function <code>{}</code>: {} cases".format(
                    fn,
                    required
                )
                for fn, required in self.function_reqs.items()
            ] + [
                "File '{}': {} cases".format(
                    filename,
                    required
                )
                for filename, required in self.file_reqs.items()
            ]
            kwargs["description"] = (
                "Defines required test cases",
                (
                    """\
Your code must use the <code>optimism</code> module to create a certain
number of test cases which use the following functions/files. Test cases
that are the same as each other (same arguments and/or inputs) don't
count. (Each test case must include at least one check).\n"""
                  + html_tools.build_list(rlist)
                )
            )

        super().__init__(taskid, "defines_enough", **kwargs)

    def check(self, context):
        """
        Looks for an adequate number of established test cases in the
        given context that have recorded checks.
        """
        cases = context_utils.extract(context, "validation_test_cases")
        by_fn = {}
        by_file = {}
        for case in cases:
            # Skip test cases that have not been checked
            if len(case.outcomes) == 0:
                continue

            # Categorize by function/file tested
            if case.manager.category == "function":
                fname = case.manager.target.__name__
                add_to = by_fn.setdefault(fname, [])

                # Don't record duplicate cases
                duplicate = False
                for recorded in add_to:
                    if (
                        case.args == recorded.args
                    and case.kwargs == recorded.kwargs
                    and case.inputs == recorded.inputs
                    ):
                        duplicate = True
                        break

                # Record this case
                if not duplicate:
                    add_to.append(case)

            elif case.manager.category == "file":
                add_to = by_file.setdefault(case.manager.target, [])

                # Don't record duplicate cases
                duplicate = False
                for recorded in add_to:
                    if (
                        case.args == recorded.args
                    and case.kwargs == recorded.kwargs
                    and case.inputs == recorded.inputs
                    ):
                        duplicate = True
                        break

                # Record this case
                if not duplicate:
                    add_to.append(case)

            # Note that we ignore block cases, which would be hard to
            # count/require...

        any_tests = False
        deficient = False
        reports = []
        for req_file, required in self.file_reqs.items():
            cases = by_file.get(req_file, [])
            count = len(cases)

            if count > 0:
                any_tests = True

            if count < required:
                deficient = True
                symbol = '✗'
            else:
                symbol = '✓'

            reports.append(
                f"{symbol} '{req_file}': {count} / {required}"
            )

        for req_fn, required in self.function_reqs.items():
            cases = by_fn.get(req_fn, [])
            count = len(cases)

            if count > 0:
                any_tests = True

            if count < required:
                deficient = True
                symbol = '✗'
            else:
                symbol = '✓'

            reports.append(
                f"{symbol} <code>{req_fn}</code>: {count} / {required}"
            )

        if not any_tests:
            return {
                "status": "failed",
                "explanation": (
                    "Running your module did not establish any test"
                    " cases for required functions or files."
                )
            }
        elif deficient:
            return {
                "status": "partial",
                "explanation": (
                    "Your module did not establish as many test cases as"
                    " were required for all functions/files:\n"
                ) + html_tools.build_list(reports)
            }
        else:
            return {
                "status": "accomplished",
                "explanation": (
                    "Your module established enough test cases for each"
                    " function or file it was required to test."
                )
            }


def list_case_outcomes(cases):
    """
    Creates an HTML list out of test case objects.
    """
    items = []
    for case in cases:
        for (passed, tag, message) in case.outcomes:
            short_tag = tag.split('/')[-1]
            message = html_tools.escape(message)
            lines = message.splitlines()
            lines[0] = lines[0][:2] + lines[0].split('/')[-1]
            message = html_tools.wrap_text_with_indentation(
                '\n'.join(lines)
            )
            items.append(f"✗ {short_tag}<br><pre>{message}</pre>")
    return html_tools.build_list(items)


class ChecksSucceed(CasesTest):
    """
    An test case checker which ensures that each recorded outcome for
    each established test case in the submitted testing module is a
    success.

    Note that when this goal is checked during validation, tests in the
    "validation_test_cases" slot have been run against the solution
    code, whereas when this goal is used during evaluation, those same
    test cases have been run against the student's submitted code.

    TODO: Manage multi-file submission and/or test file copying so that
    "validation_test_cases" is actually available during evaluation.
    """
    def __init__(self, taskid, **kwargs):
        """
        A task ID is required. Arguments are passed through to
        `CasesTest`.

        The identifier will be "checks_succeeded".
        """

        try:
            import optimism # noqa F401
        except Exception:
            raise NotImplementedError(
                "ChecksSucceed cannot be used because the 'optimism'"
                " module cannot be imported."
            )

        if "description" not in kwargs:
            kwargs["description"] = (
                (
                    "All checks must succeed"
                ),
                (
                    "Every time your code checks a test case using the"
                    " <code>optimism</code> module the check must"
                    " succeed."
                )
            )

        super().__init__(taskid, "checks_succeeded", **kwargs)

    def check(self, context):
        """
        Looks for any failed outcomes in test cases within the given
        context.
        """
        cases = context_utils.extract(context, "validation_test_cases")
        any_failed = False
        any_passed = False
        failing = []
        for case in cases:
            failed_here = False
            for (succeeded, tag, msg) in case.outcomes:
                if succeeded:
                    any_passed = True
                else:
                    failed_here = True

            if failed_here:
                any_failed = True
                failing.append(case)

        if any_failed:
            fail_list = list_case_outcomes(failing)
            if any_passed:
                return {
                    "status": "partial",
                    "explanation": (
                        "Some of your code's checks failed:\n"
                    ) + fail_list
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        "None of your code's checks succeeded:\n"
                    ) + fail_list
                }
        else:
            if any_passed:
                return {
                    "status": "accomplished",
                    "explanation": (
                        "All of your code's checks succeeded."
                    )
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        "Your code did not check any test cases."
                    )
                }
