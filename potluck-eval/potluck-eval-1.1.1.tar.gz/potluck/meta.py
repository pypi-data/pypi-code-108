"""
Routines for checking whether specifications are correctly implemented
and working as intended.

meta.py
"""

import re

from . import file_utils


EXPECTATIONS = {}
"""
Global storage for expectations by spec module name, mode, and username.
Entries are module names with mode dictionaries as values, whose keys are
modes (i.e., "evaluation" or "validation") and whose values are
dictionaries that map usernames to lists of expectations.
"""

CURRENT_EXAMPLE = None
"""
Which username are expectations automatically registered for?
"""


def simplify(description):
    """
    Normalizes case and removes HTML tags from the given goal
    description, for use in expectation matching. Note that angle
    brackets which aren't used for HTML tags are assumed to already be
    escaped. Adds '^^^' at the start and '$$$' at the end so that rules
    can use those anchors (or part of them) for disambiguation.
    """
    stripped = re.sub(r"<[^>]*>", '', description)
    return '^^^' + stripped.casefold() + '$$$'


def all_row_trails(report_or_row, trail_prefix=None):
    """
    Visits each row & sub-row of a report (or a report row) one by one.
    For each row visited, it yields a tuple containing that row, followed
    by a trail: a list of the first description entry of each ancestor of
    that row, starting from the top-level ancestor and going down and
    including that row.

    If provided the given trail prefix (a list of strings) will be
    included before the start of each trail.
    """
    if trail_prefix is None:
        trail_prefix = []

    if "table" in report_or_row:
        for entry in report_or_row["table"]:
            yield from all_row_trails(entry, trail_prefix)
    else:
        desc = report_or_row["description"][0]
        below = trail_prefix + [ desc ]
        if "subtable" in report_or_row:
            yield (report_or_row, below)
            for entry in report_or_row["subtable"]:
                yield from all_row_trails(entry, below)
        else:
            yield (report_or_row, below)


class ExpectedWarning:
    """
    An expected warning provides a heads-up that a warning containing
    certain text is expected, so that getting such a warning won't fail a
    check.
    """
    def __init__(self, message_fragment=''):
        """
        A message fragment should be provided, or by default all warnings
        will be ignored. If a fragment is provided, all warnings which
        include that fragment as part of their raw HTML code string will
        be ignored, but other warnings will not be.
        """
        self.fragment = message_fragment

    def unexpected(self, warnings):
        """
        Returns all of the warnings from the given list which *aren't*
        expected, given this expectation that certain warning(s) might be
        present.
        """
        return [w for w in warnings if self.fragment not in w]


class Expectation:
    """
    An expectation establishes that a specific goal should evaluate to a
    specific result within a report. These expectations can be tested
    to make sure that a specification is working as designed.

    To specify which goal the expectation applies to, there are two
    options: you can provide a fragment of the goal's identifier as a
    string (it must match exactly one goal; see
    `potluck.rubrics.Rubric.goals_by_id`), or you can provide a list of
    strings, each must uniquely match against an item in a report table
    at a specific level, with the next string matching against that row's
    sub-table, and so on. These matches are performed in a
    case-insensitive manner with HTML tags stripped out, against the
    primary obfuscated description entry for each goal/category. The
    specified string only has to match part of the goal description, but
    it must not match multiple goal descriptions at a given table level.
    The characters '^^^' are added to the beginning of the rubric string,
    and '$$$' to the end, to aid in disambiguation.

    Because of these matching rules, for a rubric where the standard
    metric `potluck.rubrics.core_extras_categorized_metric` is used,
    goal paths are usually straightforward to construct when default
    descriptions are in place. Some examples of both id-fragment and
    goal-path methods:

    - For a core FunctionDef Check for function 'foo':
        `"core.check:def-foo$"` OR
        `[ "procedure", "core", "define foo" ]`

    - For an extra FunctionCall Check for 'bar' as a sub-rule of the
        check above:
        `"core.check:def-foo:call-bar$"` OR
        `[ "procedure", "extra", "define foo", "call bar" ]`

    - For a core trace test of function 'foo', assuming it was created
        with group_name "trace":
        `"core.test:foo:trace"` OR
        `[ "process", "core", "the foo function must" ]`
    - (note that one could also use:)
        `"^goal:core.test:foo:trace$"` OR
        `[ "process", "core", "^the foo function must" ]`

    - For a core result value test of function 'foo' (with no group_name):
        `"core.test:foo$"` OR
        `[ "product", "core", "foo returns" ]`
        (Note for the ID version, the $ is important to distinguish from
        the case above.)

    - For a core printed output test of function 'foo' (with group_name
        "output"):
        `"core.test:foo:output"` OR
        `[ "behavior", "core", "foo prints" ]`
    """
    def __init__(self, goal_spec, expected_status):
        """
        The goal_spec is a list of strings specifying how to find the
        goal in a report (strings are matched against descriptions to
        find sub-tables). Alternatively, the goal_spec may be a single
        string, which will must match a single goal in the rubric using
        the same rules as `potluck.rubrics.Rubric.goals_by_id`. The
        expected evaluation result is also required, which should be one
        of the strings used for goal statuses (see
        `potluck.rubrics.Goal`).

        Note that the precise goal_spec list an `Expectation` should have
        depends on the metric used and the details of how a
        `potluck.rubrics.Rubric` object formulates its overall report,
        because any top-level organizational report rows (e.g. for goal
        types or categories) need to be accounted for. Specifying an
        identifier fragment doesn't depend on the metric, but requires
        understanding how identifiers are built up, and in some cases,
        automatic deduplication of goal identifiers must be accounted
        for.

        For matching using a goal spec that's a list of strings, the
        case-folded version of each goal_spec entry is checked using 'in'
        against a case-folded version of each rubric entry at the
        relevant level. Exactly 1 rubric entry must match.  The rubric
        entries also have HTML tags stripped out, and have '^^^' added at
        the front and '$$$' at the end to aid in disambiguation.

        For example, if there are rubric entries named "Bug #1" and
        "Bug #11", an expectation for the "Bug #1" rubric entry could use
        "bug #1$" as its goal_spec entry.
        """
        self.goal_spec = goal_spec
        self.expected_status = expected_status

    def check(self, report):
        """
        Checks whether this expectation is fulfilled in a given report.
        Returns a tuple containing:
            1. Either True or False indicating success or failure.
            2. A string description of why the check failed (or how it
               succeeded).
            3. A list of strings containing the full unmodified
               initial descriptions of each report table row on the path
               to the row that was checked. If the check failed because
               it could not find the row it was looking for, this will be
               None.
        """
        rows_here = report["table"]
        if rows_here == [] and report["files"] == []:
            raise ValueError("Report indicates no file to evaluate.")
        found = None
        trail = []

        if isinstance(self.goal_spec, str):
            candidates = []
            all_ids = []
            for (row, trail) in all_row_trails(report):
                if 'id' in row:
                    all_ids.append(row['id'])
                    if self.goal_spec in ('^^^' + row['id'] + '$$$'):
                        candidates.append((row, trail))

            if (
                len(all_ids) == 0
            and (
                    report["summary"]
                 == "You did not submit any code for this task."
                )
            ):
                return (
                    False,
                    "There was no submission.",
                    None
                )

            if len(candidates) == 0:
                options = '\n'.join(
                    '#' + ident
                    for ident in all_ids
                )
                return (
                    False,
                    (
                        f"0 goals matched"
                        f" '#{self.goal_spec}'. Available goal ids"
                        f" are:\n{options}"
                    ),
                    None
                )
            elif len(candidates) > 1:
                options = '\n'.join(
                    '#' + row['id']
                    for (row, trail) in candidates
                )
                return (
                    False,
                    (
                        f"{len(candidates)} goals matched"
                        f" '#{self.goal_spec}'. Matching goals"
                        f" are:\n{options}"
                    ),
                    None
                )

            # We found one match:
            found, trail = candidates[0]

            # String for reporting where we are
            where = "In " + ' → '.join(trail)

        else: # we assume it's a collection of strings
            # Match at each level of our goal path
            for match_key in self.goal_spec:
                # Match against descriptions at this level
                matches_here = []
                for row in rows_here:
                    match_against = simplify(row["description"][0])
                    look_for = match_key.casefold()
                    if look_for in match_against:
                        matches_here.append(row)

                # Check # of matching rows
                if len(matches_here) != 1: # zero or multiple matches
                    if trail:
                        where = "In " + ' → '.join(trail)
                    else:
                        where = "At the top level of the report"

                    options = '\n'.join(
                        row['description'][0]
                        for row in rows_here
                    )
                    return (
                        False,
                        (
                            f"{where}, {len(matches_here)} goals matched"
                            f" '{match_key}'. Goals here are:\n{options}"
                        ),
                        None
                    )
                else: # a single match, as required
                    # Record the goal or other table row we found:
                    found = matches_here[0]
                    # Extend our trail
                    trail.append(found["description"][0])
                    # Enter next level of the table:
                    rows_here = found["subtable"]

            # Strings for reporting our result
            where = "In " + ' → '.join(trail)

        # "found" should now be the matched goal's report row
        if found["status"] == self.expected_status:
            return (
                True,
                f"{where}, confirmed status '{self.expected_status}'.",
                trail
            )
        else:
            return (
                False,
                (
                    f"{where}, status '{found['status']}' did not match"
                    f" expected status '{self.expected_status}'."
                ),
                trail
            )


def check_entire_report(
    report,
    all_expectations,
    default_level=2,
    require_default="accomplished"
):
    """
    Given a report and a list of `Expectation` and/or `ExpectedWarning`
    objects, this function checks each of the expectations within the
    provided report, returning a tuple containing True or False to
    indicate success or failure, as well as a multi-line string
    explaining which checks failed or that all checks succeeded.

    If require_default is provided, then all rubric rows in the report
    which don't have an explicit `Expectation` provided for them or a
    sub-row at the given default_level must match the require_default
    status. Set require_default to None (the default is 'accomplished')
    to leave non-explicitly-checked rows unchecked.
    """
    explanation = "Some checks failed:\n"
    coverage = {}
    succeeded = True
    unexpected_warnings = report["warnings"]
    for exp in all_expectations:
        if isinstance(exp, ExpectedWarning):
            # Filter out warnings
            before = len(unexpected_warnings)
            unexpected_warnings = exp.unexpected(unexpected_warnings)
            if len(unexpected_warnings) == before: # nothing was filtered
                succeeded = False
                explanation += (
                    f"  Expected at least one warning containing the text"
                    f" '{exp.fragment}', but no such warning was present."
                    f"\n  (or it was filtered by a different warning"
                    f" expectation.)\n"
                )

        elif isinstance(exp, Expectation):
            # Test goal status
            success, expl, path = exp.check(report)
            if path is None:
                if isinstance(exp.goal_spec, str):
                    gs = '#' + exp.goal_spec
                else:
                    gs = ' → '.join(exp.goal_spec)
                raise ValueError(
                    "Unable to find expected goal:\n{}\n{}".format(gs, expl)
                )
            c = coverage
            for entry in path:
                c = c.setdefault(entry, {})
            c[None] = True
            if not success:
                explanation += expl + '\n'
                succeeded = False

        else:
            raise TypeError(f"Invalid expectation type: {type(exp)}")

    default_count = 0
    if require_default is not None:
        def check_default_statuses(rows, covered, path):
            """
            Checks that the status of every row at a certain default
            level within the report hierarchy is equal to the required
            default status. Needs a list of rows at this level of the
            table, a dictionary of covered paths pertaining to this
            level of the table, and a list of strings indicating the
            path taken to get to this part of the table.

            Returns a tuple starting with True or False for success or
            failure, followed by a string describing the failure(s) or
            explaining the success.
            """
            nonlocal default_count, default_level, require_default
            passed = True
            explanation = ""
            level = len(path)
            if level == default_level: # Check each non-covered row
                for row in rows:
                    desc = row["description"][0]
                    if desc in covered and covered[desc].get(None, False):
                        continue # don't check this covered row
                    else:
                        default_count += 1
                        if row["status"] != require_default:
                            where = "In " + " → ".join(path + [desc])
                            explanation += (
                                f"{where} status '{row['status']}' did"
                                f" not match required default status"
                                f" '{require_default}'.\n"
                            )
                            passed = False
            else: # Recurse
                for row in rows:
                    desc = row["description"][0]
                    subtable = row["subtable"]
                    sub_success, sub_expl = check_default_statuses(
                        subtable,
                        covered.get(desc, {}),
                        path + [desc]
                    )
                    if not sub_success:
                        passed = False
                        explanation += sub_expl

            if passed:
                explanation = (
                    f"All non-expected statuses were"
                    f" '{require_default}'."
                )
            return passed, explanation

        default_success, default_expl = check_default_statuses(
            report["table"],
            coverage,
            path=[]
        )
        if not default_success:
            succeeded = False
            explanation += default_expl

    if succeeded:
        explanation = "All {} expectation(s){} were met.".format(
            len(all_expectations),
            (
                f" (plus {default_count} default expectation(s))"
                if default_count > 0
                else ""
            )
        )

    # Check for warnings and replace/augment explanation
    if len(unexpected_warnings) > 0:
        wmsg = (
            "The report included unexpected warnings:\n  "
          + "\n ".join(unexpected_warnings)
        )
        if succeeded:
            explanation = wmsg
        else:
            explanation = wmsg + '\n' + explanation

        succeeded = False

    return (succeeded, explanation)


def example(username, extra_modes=()):
    """
    Registers a current username such that calls to `expect` and/or
    `expect_validation` create expectations for that example submission,
    and creates an "evaluation" entry in the expectations table for it so
    that even if no expectations are established it will still be tested
    using default expectations.

    If extra_modes is provided, it should be a list of strings naming
    extra modes to check (e.g., ["validation"]). Note that as soon as an
    expectation is established for any mode that mode will be checked
    even if it wasn't specified here.
    """
    global CURRENT_EXAMPLE
    CURRENT_EXAMPLE = username
    mname = file_utils.get_spec_module_name()
    for mode in ["evaluation"] + list(extra_modes):
        EXPECTATIONS\
            .setdefault(mname, {})\
            .setdefault(mode, {})\
            .setdefault(username, [])


def expect(status, *id_or_path, mode="evaluation"):
    """
    Creates an `Expectation` object and registers it under the current
    example username as an evaluation expectation.

    Arguments are:

    - status: The expected status. See `potluck.rubrics.Goal`.
    - id_or_path: One or more additional strings specifying which goal we're
        targeting (see `Expectation`). May also be a single string that
        starts with '#' to specify the goal using its identifier instead
        of a rubric-description-path. If it's a single string, it should
        start with the goal type and then category when using the default
        rubric metric.
    - mode: Keyword-only; sets which mode of testing the expectation
        applies to. Valid modes are "evaluation" (the default) and
        "validation".
    """
    mname = file_utils.get_spec_module_name()

    if len(id_or_path) == 1 and id_or_path[0].startswith('#'):
        goal_spec = id_or_path[0][1:]
    else:
        goal_spec = id_or_path

    EXPECTATIONS\
        .setdefault(mname, {})\
        .setdefault(mode, {})\
        .setdefault(CURRENT_EXAMPLE, [])\
        .append(
            Expectation(
                goal_spec,
                status
            )
        )


def expect_validation(*args):
    """
    Establishes an expectation for the validation step. This is just a
    shortcut for calling `expect` with mode set to "validation".
    """
    expect(*args, mode="validation")


def expect_warnings(fragment='', mode="evaluation"):
    """
    Creates an `ExpectedWarning` object and registers it under the
    current example username. Registers for evaluation by default, but
    you can specify a different mode (e.g., "validation").

    The `fragment` argument if omitted will cause all warnings to be
    treated as expected, but if provided, only warnings whose raw HTML
    message string contains that fragment as a substring will be treated
    as expected.
    """
    mname = file_utils.get_spec_module_name()

    EXPECTATIONS\
        .setdefault(mname, {})\
        .setdefault(mode, {})\
        .setdefault(CURRENT_EXAMPLE, [])\
        .append(ExpectedWarning(fragment))


def get_expectations(spec_module, mode="evaluation"):
    """
    Returns all expectations for the given specification module and mode,
    as a dictionary mapping user IDs to expectation lists. Returns None
    if there are no expectations for the target mode or for the target
    module, and an empty expectation set hasn't been set up either.
    """
    return EXPECTATIONS.get(spec_module.__name__, {}).get(mode, None)
