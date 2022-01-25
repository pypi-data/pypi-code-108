"""
Main classes for defining a rubric, including `Rubric` itself, as well as
`Goal` and `Context`.

rubrics.py

The big picture is that a `Rubric` contains `Goal` objects, which in
turn each get evaluated in one or more `potluck.contexts.Context`s.

The context graph determines what tests actually get run, and supplies
test results, often from both submitted and solution code, in the form of
a context dictionary containing various slots (there is a list of common
slot names in the documentation for `potluck.contexts.Context`).

`Goals` then read those values and make decisions: they are either
accomplished, partially accomplished, or failed in each particular
context that they list, and then they also get an overall status based on
combining the statuses from their evaluation in individual contexts.

One common `Goal` type is the `ComparisonTest` which compares two
context values, for example one produced from submitted code against
another produced by the same process from solution code.

Another common `Goal` type is the `ImplementationCheck`, which uses the
`mast` module to look for certain patterns in the AST of the submitted
code.

Once a `Rubric`'s goals have been evaluated and have individually been
assigned statuses, the entire rubric gets an overall evaluation via a
metric function, such as `core_extras_categorized_metric`. This process
is handled via the `Rubric.evaluate` method.
"""

import os
import copy
import math
import ast
import traceback

from . import mast
from . import patterns
from . import html_tools
from . import phrasing
from . import contexts
from . import context_utils
from . import logging

# TODO: Import Goal, and Rubric stuff from codder.buoy


GOAL_TYPE_RUBRICS = {
    "style": (
        "Style Requirements",
        "How your code is written.",
        "Style Requirements",
        (
            "Checks regarding the raw text of your code file and how it"
          + " is organized stylistically (e.g., how many characters are"
          + " in a line of code, or how many comments there are)."
        )
    ),
    "procedure": (
        "Procedure Requirements",
        "What code you use to solve the problem.",
        "Procedure Requirements",
        (
            "Code checks which require that your code is written in a"
          + " certain way, regardless of what happens when it runs"
          + " (e.g., how many lines of code call a certain function)."
        ),
    ),
    "process": (
        "Process Requirements",
        "How your code achieves its results.",
        "Process Requirements",
        (
            "Process checks which check how your code works by recording"
          + " each operation that happens in order (e.g., how many times"
          + " or with what arguments a certain function is called)."
        )
    ),
    "product": (
        "Product Requirements",
        "Your code's result values.",
        "Product Requirements",
        (
            "Result tests that run your code and check for the internal"
          + " result values it produces (e.g., the return value from a"
          + " specific function)."
        )
    ),
    "behavior": (
        "Behavior Requirements",
        "What your code does from the user's perspective.",
        "Behavior Requirements",
        (
            "Behavior tests that run your code and check what inputs it"
          + " requests from and what outputs it displays to the user"
          + " (e.g., what is printed given certain typed inputs)."
        )
    ),
    "testing": (
        "Testing Requirements",
        "What tests you define for your code and their results.",
        "Testing Requirements",
        (
            "Expectation tests that look at the test cases you've set up"
          + " and the expectations you've defined and ensure that you"
          + " have enough tests and/or that your tests are working."
        )
    ),
    "other": (
        "Other Requirements",
        "Requirements that don't fall into any other category."
    )
    # TODO: Long explanation with an e.g. part?
}
"""
A dictionary mapping goal types to 4-part descriptions that explain what
each goal type means, for use in rubric tables that categorize goals by
type.
"""


#---------------------#
# The base Goal class #
#---------------------#

BLANK_RESULT = {
    "status": "unknown",
    "explanation": "This goal has not been evaluated."
}
"""
The default blank result value that a goal acquires when first
constructed or whenever it is reset.
"""

STATUS_DESCRIPTORS = {
    "accomplished": "accomplished",
    "partial": "partially accomplished",
    "failed": "failed",
    "not applicable": "not applicable",
    "unknown": "unknown",
}
"""
Full human-oriented strings for each status string.
"""


class Goal:
    """
    A goal is a line-item on a rubric: something that a submission should
    accomplish. When evaluated, it updates its 'result' to an evaluation
    object that has a status (one of "unknown", "accomplished",
    "partial", "failed", or "not applicable") and an explanation. It also
    has a dictionary of strings that describe different tags it is labeled
    with.

    A Goal is able to produce a table of results (and possibly
    sub-results) via its table method.
    """
    USED_IDS = {}
    """
    A dictionary of identifier values that have been used already,
    organized into sub-dictionaries indexed by task IDs.
    """

    def unique_id(taskid, category, identifier):
        """
        A static method: given a task of interest, a category, and an
        identifier, keeps track of identifiers provided and returns them
        as-is, except when a duplicate is provided, in which case it
        appends a -number suffix to the duplicate to make it unique and
        returns that. The -number suffixes start at -2 for the second
        copy; -1 is never used because the first copy doesn't get a
        suffix added.

        The result is prefixed with 'goal:<category>.' which can also
        de-duplicate IDs without needing a suffix sometimes.
        """
        task_ids = Goal.USED_IDS.setdefault(taskid, {})

        full_id = "goal:" + category + '.' + identifier

        seen_before = task_ids.get(full_id, 0)

        if seen_before == 0: # not seen before
            task_ids[full_id] = 1
            return full_id
        else: # was seen before; would be a duplicate
            task_ids[full_id] += 1
            result = full_id + '-' + str(seen_before + 1)
            return result

    def __init__(
        self,
        taskid,
        identifier,
        description=("BLANK GOAL", "THIS GOAL HAS NOT BEEN DEFINED"),
        test_in=None,
        explanations=None,
        tags=None
    ):
        """
        You must supply a task ID (a string), an identifier (a string)
        and a description-tuple: the title of the goal, and a more
        detailed explanation that will be available if the user requests
        more information. The description-tuple may also include a third
        and/or fourth entry: these will be used instead of the first and
        second entry (respectively) when the Goal is being presented as
        part of graded feedback instead of as part of a blank rubric.
        This can be used to avoid showing exactly which tests are
        performed when the rubric is constructed, but include that
        information when feedback is given.

        Note that if the identifier you supply is already in use within
        the specified task, a numeric suffix will be appended to make it
        unique.

        You may also supply:

        1. A 'test_in' dictionary which has the following keys:
            - 'contexts': A list of Context objects within which
                this goal should be independently tested.
            - 'required': The amount of credit which this goal
                needs to count as accomplished overall. For
                contexts where it evaluates to "accomplished", one
                unit of credit is earned, and contexts where it
                evaluates to "partial" earn 1/2 unit of credit by
                default. The default value is the number of
                contexts supplied, implying conjunctive logic. Set
                this to 1 for disjunctive logic (and set 'strict'
                to True for pure disjunction).
            - 'partial': If present, the amount of credit needed to
                count as partially accomplished. If absent, will
                default to 1/2 the 'required' value. Set to False
                to prevent the goal from being marked as partially
                accomplished.
            - 'count_partial_as': If present, should be a number
                between 0 and 1, which specifies how much credit
                to give for contexts where this gaol evaluates as
                partially-accomplished when comparing results
                against required/partial thresholds. Default 0.5.
            - 'strict': If present and truthy, overrides 'partial'
                and 'count_partial_as' to set 'partial' to False
                and 'count_partial_as' to 0.
            - 'warn': If present and truthy, when a context builder
                fails, the failure explanation will be generated as
                a warning instead of as a note (the default).
            - 'fail_without_context': If context creation fails,
                the goal will be marked as failing in that context
                without even being evaluated. True by default.

            During evaluation, this goal will be independently
            evaluated in each provided context, and the aggregate
            results of those evaluations will be used to determine
            the overall status of this goal. Note that context keys
            provided by these Context objects override any context
            keys that may be established and provided by a super-goal
            during testing, and the super-goal context is not made
            available to these Context objects as part of their
            context construction process.

            If no test_in dictionary is provided, the goal is simply
            evaluated in a blank context (or in whatever context its
            parent goal passed down).

        2. An 'explanations' dictionary with some or all of the keys:
           "accomplished", "partial", "failed", and/or "crash"
           (typically used when a goal fails due to an exception). If
           a relevant key exists in this dictionary, the value will
           be used as the explanation for this goal if it has the
           specified outcome. If the value is a function instead of a
           string, it will be given the Goal object, which will
           already include a partial 'result' object, and the
           evaluation context, and the string that it returns will be
           used as an explanation.

        3. A 'tags' dictionary of strings that tag the goal. Some
           tags affect how certain types of goals behave.
        """
        if not isinstance(taskid, str):
            raise TypeError("A Goal's task ID must be a string.")

        self.taskid = taskid

        if not isinstance(identifier, str):
            raise TypeError("A Goal's identifier must be a string.")

        if (
            not isinstance(description, (list, tuple))
         or not 2 <= len(description) <= 4
        ):
            raise ValueError(
                (
                    "The description for a goal must be a 2-to-4-element"
                    " list or tuple (got: {})."
                ).format(repr(description))
            )
        self.description = description
        self.test_in = test_in
        # TODO: Figure this out.
        #if (
        #    not isinstance(self.test_in, (dict))
        # or any(
        #        not isinstance(x, contexts.Context)
        #        for x in self.test_in["contexts"]
        #    )
        #):
        #    raise ValueError(
        #        "Every item in the test_in 'contexts' slot must be a"
        #      + " Context, and test_in must be a dictionary."
        #    )
        self.explanations = explanations or {}
        self.tags = tags or {}

        # Get a unique ID for this goal
        category = self.tags.get("category", "unknown")
        self.identifier = Goal.unique_id(taskid, category, identifier)

        # Initialize blank result:
        self.reset()

    def __copy__(self):
        """
        `Goal`s may not be copied (there is no good way to do so since
        they're entangled with both each other and with
        `potluck.contexts.Context` objects).
        """
        raise NotImplementedError("Goals may not be copied.")

    def __deepcopy__(self, memo):
        """
        `Goals` may not be copied (they are entangled with other goals
        and with `potluck.contexts.Context` objects).
        """
        raise NotImplementedError("Goals may not be copied.")

    def description_topic(self):
        """
        Gets the rubric version of this `Goal`'s topic.
        """
        return self.description[0]

    def description_details(self):
        """
        Gets the rubric version of this `Goal`'s details.
        """
        return self.description[1]

    def feedback_topic(self):
        """
        Gets the feedback version of this `Goal`'s topic, or just the
        normal topic if there is no feedback version.
        """
        return self.description[::2][-1]

    def feedback_details(self):
        """
        Gets the feedback version of this `Goal's details, or just the
        normal details if there is no feedback version.
        """
        return self.description[1::2][-1]

    def get_goal_type(self):
        """
        Inspects this `Goal`'s tags for a "goal_type" slot and returns
        the associated value, or None if there is no such slot.
        """
        return self.tags.get("goal_type", None)

    def set_default_goal_type(self, default_type):
        """
        Sets the given goal type for this goal (adds a tag), but only
        does so if the goal doesn't already have a goal type tag.
        """
        if "goal_type" not in self.tags:
            self.tags["goal_type"] = default_type

    def reset(self):
        """
        Resets internal state so that the goal can be evaluated again.
        Does not affect internal state of any sub-goals, and does not
        affect cached context values.
        """
        self.result = copy.deepcopy(BLANK_RESULT)

    def reset_network(self):
        """
        Resets our internal state and the states of any sub-goals, but
        does not affect context caches.
        """
        self.reset()
        for goal in self.subgoals():
            goal.reset_network()

    def full_reset(self):
        """
        Does a full reset, including a full reset of subgoals plus
        burning of context caches.
        """
        self.reset()
        for goal in self.subgoals():
            goal.full_reset()
        if self.test_in:
            for ctx in self.test_in["contexts"]:
                ctx.burn_cache()

    def subgoals(self):
        """
        Returns a list of `Goal` objects that are considered subgoals of
        this goal. Different `Goal` classes have different relationships
        to their subgoals, but this method allows other code to discover
        the full tree of goals regardless of those relationships. `Goal`
        classes without subgoals can safely inherit this method, which
        returns an empty list.
        """
        # A base Goal has no subgoals.
        return []

    def evaluate(self, base_context=None):
        """
        Evaluates this goal independently within each of its contexts,
        and produces an overall evaluation that combines explanations
        from each context. If there are no contexts, simply evaluates the
        goal normally.

        A base context is normally required, as otherwise the goal won't
        have access to the submitted code or even basic info about the
        task being evaluated.

        Keeps track of the set of all distinct explanations generated,
        and if there was only a single shared explanation across all
        contexts, it uses that as the final explanation, but if there
        were multiple different explanations, creates a combined
        explanation with sections for the different contexts that had
        different explanations.

        Note: During this process, if the goal ever evaluates to "not
        evaluated" in one of the contexts, the end result will be "not
        evaluated" overall regardless of results from other contexts.

        Note: If one of the contexts cannot be created, the goal will
        count as failed in that context, and a note will be attached to
        the result. If a context builder function generates an error
        other than a `potluck.context_utils.ContextCreationError`, a
        warning is generated, but in other cases the 'warn' of the
        setting determines whether a warning or note is generated.
        """
        if not self.test_in or len(self.test_in["contexts"]) == 0:
            # No contexts listed: simply evaluate in base context
            try:
                # this will set self.result
                self.evaluate_in_context(base_context)
            except Exception:
                self.result = {
                    "status": "failed",
                    "warnings": [],
                    "notes": [
                        # generic context creation failure is usually not
                        # warning-worthy. TODO: Sometimes it is!
                        "Context creation failed"
                      + " unexpectedly:<br>\n{}".format(
                            html_tools.html_traceback(
                                title='Error:',
                                linkable=context_utils.linkmap(base_context)
                            )
                        )
                    ]
                }
            return self.result

        else: # has specific contexts to test in
            credit = 0
            full_count = 0
            partial_count = 0
            notes = []
            warnings = []
            # mapping from explanation strings to lists of status,
            # context pairs:
            explanations = {}
            for i, builder in enumerate(self.test_in["contexts"]):
                # Construct context:
                this_context = copy.copy(base_context)
                # Note: can't deep-copy things like modules

                # Set goal_id and which_context value to provide enough
                # information in the context dictionary to uniquely
                # identify a specific context-building operation.
                this_context["goal_id"] = self.identifier
                this_context["which_context"] = i

                add_failures_to = notes
                if self.test_in.get("warn"):
                    add_failures_to = warnings

                err = None
                try:
                    this_context.update(builder.create(this_context))
                except context_utils.ContextCreationError as e:
                    err = e.explanation()
                    add_failures_to.append(e.explanation())
                except Exception:
                    err = html_tools.html_traceback(
                        title="Unexpected Error:",
                        linkable=context_utils.linkmap(this_context)
                    )
                    notes.append(
                        "Context creation failed unexpectedly:<br>\n"
                      + err
                    )

                # reset this and subgoals, but don't disturb Context caches:
                self.reset_network()

                # evaluate ourselves:
                if (
                    self.test_in.get("fail_without_context", True)
                and err is not None
                ):
                    res = {
                        "status": "failed",
                        "explanation": (
                            "Failed to establish testing context:<br>\n{}"
                        ).format(err)
                    }
                else:
                    res = self.evaluate_in_context(this_context)

                if res["status"] == "accomplished":
                    credit += 1
                    full_count += 1
                elif res["status"] == "partial":
                    credit += self.test_in.get("count_partial_as", 0.5)
                    partial_count += 1
                elif res["status"] == "unknown":
                    # Immediately abandon evaluation across contexts:
                    return {
                        "status": "unknown",
                        "explanation": (
                            "Unable to evaluate in context:<br>\n{}"
                        ).format(builder.html_topic(in_feedback=True))
                        # TODO: Does this need to be html_context_tree
                        # for disambiguation?
                    }

                # record explanation & status:
                expl = res.get("explanation", "")
                if expl not in explanations:
                    explanations[expl] = []
                explanations[expl].append((res["status"], builder, res))

                # copy notes and warnings
                if "notes" in res:
                    notes.extend(res["notes"])
                if "warnings" in res:
                    warnings.extend(res["warnings"])

            # Compute credit required/partial
            required = self.test_in.get(
                "required",
                len(self.test_in["contexts"])
            )
            partial = self.test_in.get("partial", required / 2)

            # Compute status
            # TODO: Should credit-logic be made visible since it's not
            # always consistent?!?
            status = "failed"
            if credit >= required:
                status = "accomplished"
            elif partial is not False and credit >= partial:
                status = "partial"

            self.result = {
                "status": status,
                "notes": notes,
                "warnings": warnings
            }

            # Combine explanations:
            if len(explanations) == 0:
                # TODO: Should we be bypassing set_explanation here?
                self.result["explanation"] = "THIS SHOULDN'T BE POSSIBLE!"
            elif len(explanations) == 1:
                # Single explanation: don't bother worrying about
                # multiple contexts and statuses:
                # TODO: This logic is bad or hides stuff?
                self.result["explanation"] = list(explanations.keys())[0]
                # In this case pick up extra keys from the result...
                competing = list(explanations.values())[0]
                if len(competing) == 1:
                    sole_result = competing[0][2]
                    for k in sole_result:
                        if k not in self.result:
                            self.result[k] = sole_result[k]
            else:
                # Multiple explanations: mix & group by statuses/contexts
                # TODO: What to do about multiple potentially
                # contradictory custom result keys?

                # Group by status:
                by_status = {}
                for expl in explanations:
                    for status, builder, result in explanations[expl]:
                        if status not in by_status:
                            by_status[status] = []
                        by_status[status].append((expl, builder))

                # Order statuses:
                status_order = ["accomplished", "partial", "failed"]
                for status in by_status:
                    if status not in status_order:
                        status_order.append(status)

                # Build parts of explanation:
                expl_parts = []
                for status in status_order:
                    if status not in by_status:
                        continue
                    expls_and_builders = by_status[status]
                    n_ctx = len(expls_and_builders)
                    if n_ctx == 0:
                        raise ValueError("Shouldn't have zero explanations!")
                    elif n_ctx == 1:
                        in_ctx = "in one context"
                    else:
                        in_ctx = "in {} contexts".format(n_ctx)

                    this_expl = html_tools.build_html_details(
                        '{} {}:'.format(
                            STATUS_DESCRIPTORS.get(status, status)
                                .capitalize(),
                            in_ctx
                        ),
                        '<ul class="contextual_explanations">{}</ul>'.format(
                            '\n'.join(
                                (
                                    '<li>In context {}\n'
                                  + '<div class="expl_in_context {}">\n'
                                  + '{}\n{}\n'
                                  + '</div>\n'
                                  + '</li>'
                                ).format(
                                    builder.html_topic(in_feedback=True),
                                    # TODO: Does this need to be
                                    # html_context_tree for
                                    # disambiguation?
                                    html_tools.status_css_class(status),
                                    html_tools.build_status_indicator(status),
                                    expl
                                )
                                for expl, builder in expls_and_builders
                            )
                        )
                    )
                    expl_parts.append((status, this_expl))

                # Combine parts into one explanation:
                rstatus = self.result["status"]
                rsdesc = STATUS_DESCRIPTORS.get(rstatus, rstatus)
                if rstatus == "accomplished":
                    if full_count >= required:
                        self.result["explanation"] = "{} (in {})".format(
                            rsdesc,
                            phrasing.obj_num(full_count, "context")
                        )
                    else:
                        self.result["explanation"] = (
                            "{} (in {} and partially accomplished in {})"
                        ).format(
                            rsdesc,
                            phrasing.obj_num(full_count, "context"),
                            phrasing.obj_num(partial_count, "context")
                        )
                else:
                    if full_count > 0:
                        if partial_count > 0:
                            self.result["explanation"] = (
                                "{} (accomplished in {};"
                                " partially accomplished in {})"
                            ).format(
                                rsdesc.capitalize(),
                                phrasing.obj_num(full_count, "context"),
                                phrasing.obj_num(partial_count, "context")
                            )
                        else:
                            self.result["explanation"] = (
                                "{} (accomplished in {})"
                            ).format(
                                rsdesc.capitalize(),
                                phrasing.obj_num(full_count, "context")
                            )
                    else:
                        if partial_count > 0:
                            self.result["explanation"] = (
                                "{} (partially accomplished in {})"
                            ).format(
                                rsdesc.capitalize(),
                                phrasing.obj_num(partial_count, "context")
                            )
                        else:
                            self.result["explanation"] = (
                                "{} (not accomplished in any contexts)"
                            ).format(rsdesc.capitalize())

                # Append parts describing success/failure in different
                # contexts:
                self.result["explanation"] += "<br>\n".join(
                    '<div class="expl_part {}">{}</div>'.format(
                        html_tools.status_css_class(status),
                        part
                    )
                    for status, part in expl_parts
                )

            # Return our result:
            return self.result

    def evaluate_in_context(self, context=None):
        """
        The evaluate_in_context method of a Goal subclass should update
        its 'result' value and return that new value. The result value
        must be a dictionary with keys 'status' and 'explanation', where
        the 'status' is one of the strings "unknown", "accomplished",
        "partial", "failed", or "not applicable", and the 'explanation'
        value is a (possibly-HTML) string. The result dictionary may also
        optionally include a list of notes and/or a list of warnings,
        which are HTML strings.

        The evaluate_in_context method does not need to worry about a
        goal's test_in value or the associated Context objects:
        evaluate takes care of constructing context dictionaries which
        are given to evaluate, so evaluate should just evaluate this goal
        within the given context. Typical context keys are explained in
        the documentation for the `potluck.contexts.Context` class.
        """
        raise NotImplementedError("Cannot evaluate base Goal object!")

    def table(self, blank=False):
        """
        Creates a table report for this goal. The table includes a list
        of rows, where each row contains a result dictionary, with a
        "description" key including this goal's description and an
        optional extra "subtable" key containing a sub-table of
        additional results. The "notes" and "warnings" entries will
        always be lists, and will be empty if there were no such keys
        (or their values were explicitly None). The following keys are
        canonical:

        - 'id': This goal's unique ID (see `Goal.unique_id`). May be
            absent on some rows representing groups of goals rather than
            individual goals.
        - 'description': A pair of strings describing this goal.
        - 'tags': A dictionary of the tags for this goal.
        - 'status': The goal's status.
        - 'explanation': An explanation for the goal's success or
            failure.
        - 'notes': A list of strings describing additional feedback for
            this goal.
        - 'warnings': A list of strings describing any warnings that
            arose during the evaluation of this goal.
        - 'subtable': A list of table rows from sub-goals.

        If "blank" is given as True, the BLANK_RESULT will be used as the
        basis instead of this table's current result, so there will be no
        notes or warnings, and the status will be "unknown."
        """
        if blank:
            row = copy.deepcopy(BLANK_RESULT)
        else:
            row = copy.deepcopy(self.result)
            row["notes"] = self.result.get("notes") or []
            row["warnings"] = self.result.get("warnings") or []
        row["id"] = self.identifier
        row["description"] = list(self.description[:])
        row["tags"] = copy.copy(self.tags)
        row["subtable"] = []
        return [ row ]

    def set_explanation(
        self,
        context,
        status=None,
        default="",
        specific_context=True
    ):
        """
        Implements the explanations logic, where if self.explanations
        contains an appropriate key, the string or function value for
        that key is used to provide an explanation, and otherwise the
        given default explanation is used. If no status string is given,
        self.result.status is used as the key.

        For cross-context final evaluation, this function is not used,
        and explanation-overrides are ignored.
        TODO: Really that?

        The resulting explanation string is inserted into self.result
        under the "explanation" key, in addition to being returned.
        """
        status = status or self.result["status"]
        expl = self.explanations.get(status, default)
        if isinstance(expl, type(lambda x: x)):
            expl = expl(self, context)

        self.result["explanation"] = expl
        return expl


#------------------#
# The Rubric class #
#------------------#

class Rubric:
    """
    A rubric has a list of goals, and a method for determining overall
    performance based on the evaluation of each individual goal. It may
    also have a separate list of validation goals to be tested during the
    validation step (e.g., goals that a certain number of tests should be
    defined; see `potluck.validation`).
    """
    def __init__(
        self,
        evaluation_goals,
        performance_metric,
        validation_goals=None,
        spec_file=None
    ):
        """
        Sets up the rubric with a list of goals to be evaluated, and a
        performance metric function that accepts a list of evaluated
        goals and returns a performance report object.

        A filename for the specification the rubric was loaded from may
        be provided, in which case certain tracebacks within output may
        be rewritten to abbreviate that filename.
        """
        self.evaluation_goals = evaluation_goals
        self.validation_goals = validation_goals or []
        self.metric = performance_metric
        self.spec_file = spec_file

    def all_contexts(self, goals):
        """
        Crawls the provided list of goals and their subgoals to find all
        relevant `potluck.contexts.Context` objects that might possibly
        be used by evaluation tests in this rubric. Returns a list in
        breadth-first traversal order of this rubric's goals, their
        contexts, and those contexts' dependencies.
        """
        # Map of object IDs
        idmap = {}

        queue = goals[:]
        while queue:
            # pop first
            first = queue.pop(0)

            # Process a Goal object (queue subgoals and contexts)
            if isinstance(first, Goal):
                queue.extend(first.subgoals())

                # Add associated contexts to our queue
                if first.test_in:
                    queue.extend(first.test_in.get("contexts", []))

            # Process a Context object (accumulate and queue dependencies)
            elif isinstance(first, contexts.Context):
                queue.extend(first.depends)

                # Add novel contexts to our idmap
                if id(first) not in idmap:
                    idmap[id(first)] = first
                    queue.extend(first.depends)

        result = list(idmap.values())

        return result

    # TODO: HERE
    def create_contexts_list(self, goals, base_context=None):
        """
        Returns a list of context summary dictionaries describing all of
        the contexts used by goals in the given goals list. It has the
        same format as returned by
        `potluck.contexts.list_and_render_contexts`.

        A base context object is necessary to generate context values;
        if no base context is given then context slots will not include
        values and will use their redacted topics and details.
        """
        clist = self.all_contexts(goals)
        if self.spec_file:
            html_tools.set_tb_rewrite(
                self.spec_file,
                "<task specification>"
            )

        # Ensure that duplicate topics are distinguished
        contexts.add_context_numbering(clist)

        cgraph = contexts.build_context_graph(clist)

        if len(clist) == 0:
            return []

        return contexts.list_and_render_contexts(cgraph, base_context)

    def create_blank_report(self, task_info):
        """
        Creates a blank report for this rubric that simply shows what the
        goals and contexts are. This function will erase any existing
        results associated with rubric goals.

        It uses False as the in_feedback value, so included context
        descriptions will be obfuscated.

        The returned report is a dictionary with the following keys:

        - taskid: The task ID (from the given taskspec)
        - evaluation: The string 'unknown'
        - warnings: An empty list
        - summary: A description of the task that this rubric belongs to.
        - table: A table (in the format returned by `Goal.table`) detailing
            each goal and subgoal.
        - contexts: A list of context summary dictionaries in the format
            returned by `potluck.contexts.list_and_render_contexts`,
            which summarizes all contexts used by this rubric.
        """
        # Empty report:
        report = {
            "taskid": task_info["id"],
            "evaluation": "unknown",
            "warnings": [],
            "summary": f"Rubric for {task_info['id']}.",
            "table": [],
            "contexts": self.create_contexts_list(self.evaluation_goals)
        }

        # Reset our goals:
        for g in self.evaluation_goals:
            g.reset_network()

        # Just in case set up a rewrite rule for the spec file
        if self.spec_file:
            html_tools.set_tb_rewrite(
                self.spec_file,
                "<task specification>"
            )

        # Run metric over un-evaluated goals and ask for a blank result:
        metric_result = self.metric(self.evaluation_goals, blank=True)

        # Integrate results into our report:
        report["evaluation"] = metric_result["evaluation"]
        report["summary"] = metric_result["summary"]
        report["table"] = metric_result["table"]
        report["warnings"].extend(metric_result["warnings"])

        return report

    def create_blank_validation_report(self, task_info):
        """
        Creates a blank validation report for this rubric that simply
        shows what the validation goals and contexts are. Just like
        `Rubric.create_blank_report`, this function will erase any
        existing results associated with validation rubric goals.

        It uses False as the in_feedback value, so included context
        descriptions will be obfuscated.

        The result has the same keys as `Rubric.create_blank_report`
        does.
        """
        # Empty report:
        report = {
            "taskid": task_info["id"],
            "evaluation": "unknown",
            "warnings": [],
            "summary": f"Validation rubric for {task_info['id']}.",
            "table": [],
            "contexts": self.create_contexts_list(self.validation_goals)
        }

        # Reset our goals:
        for g in self.validation_goals:
            g.reset_network()

        # Just in case set up a rewrite rule for the spec file
        if self.spec_file:
            html_tools.set_tb_rewrite(
                self.spec_file,
                "<task specification>"
            )

        # Run metric over un-evaluated goals and ask for a blank result:
        metric_result = self.metric(self.validation_goals, blank=True)

        # Integrate results into our report:
        report["evaluation"] = metric_result["evaluation"]
        report["summary"] = metric_result["summary"]
        report["table"] = metric_result["table"]
        report["warnings"].extend(metric_result["warnings"])

        return report

    def evaluate(self, task_info, username, submission_target):
        """
        Evaluates this rubric based on the given submitted task (the
        task_info includes generic info about the task, the username
        identifies who submitted it, and the submission_target
        identifies the file or folder to be evaluated).

        See `tasks.json` for the task info format (it's a dictionary
        stored in the "tasks" slot under its taskid as a key).

        Returns a report object that has information about which goal(s)
        from the rubric passed or failed, and the overall performance as
        determined by the rubric's metric.

        If submitted code cannot be loaded due to a syntax error or
        parsing fails for some other reason, the report will mention
        that in as much detail as it can, and the normal rubric items
        will be skipped.

        Note: This function completely resets all evaluation goals and
        clears the caches of any associated `potluck.contexts.Context`
        objects before it starts evaluating goals.

        The returned report dictionary has the following keys:

        - taskid: The task ID (from the given taskspec)
        - evaluation: A string summarizing the performance on the entire
            task (from the metric function).
        - summary: An HTML string summarizing performance on the task
            (from the metric function).
        - files: A list of dictionaries with 'filename' and 'code' slots
            containing the file names and raw code text of the submitted
            file(s).
        - warnings: A list of warnings (from the metric function plus a
            few custom warnings if things are seriously wrong).
        - table: A table (in the format returned by `Goal.table`) detailing
            each goal and subgoal (from the metric function).
        - contexts: A list of context summary dictionaries in the format
            returned by `potluck.contexts.list_and_render_contexts`,
            which summarizes all contexts used by this rubric (see
            `Rubric.create_contexts_list`).
        - TODO: Add a partner_username field here?
        """
        # Empty report:
        report = {
            "taskid": task_info["id"],
            "evaluation": "unknown",
            "summary": "No summary has been generated.",
            "files": [],
            "warnings": [],
            "table": [],
            "contexts": []
        }

        # Set up a rewrite rule for the spec file
        if self.spec_file:
            html_tools.set_tb_rewrite(
                self.spec_file,
                "<task specification>"
            )

        # Check for a missing submission:
        if not os.path.exists(submission_target):
            report["warnings"] = [
                "You did not submit any code for this task."
            ]
            report["evaluation"] = "incomplete"
            report["summary"] = "You did not submit any code for this task."
            # Early return: no need to grade rubric items
            return report

        # Check for accidental submission of the starter file:
        if os.path.isfile(submission_target):
            with open(submission_target, 'r', encoding="utf-8") as fin:
                submitted_code = fin.read()
            if submitted_code == task_info["specification"].starter_src:
                report["warnings"] = [
                    "You submitted the starter file without any"
                    " changes (you probably submitted the wrong file?)."
                ]
                report["evaluation"] = "incomplete"
                report["summary"] = (
                    "You submitted an unchanged starter file."
                )

        # Reset each goal + any associated contexts:
        for g in self.evaluation_goals:
            g.full_reset()

        # Ensure context descriptions are unique:
        clist = self.all_contexts(self.evaluation_goals)
        contexts.add_context_numbering(clist)

        # Create our base context:
        if os.path.isdir(submission_target):
            submission_root = submission_target
            default_file = task_info["target"]
            actual_file = default_file
        else:
            submission_root, actual_file = os.path.split(submission_target)
            default_file = task_info["target"]
        base_context = {
            "task_info": task_info,
            "username": username,
            "submission_root": submission_root,
            "default_file": default_file,
            "actual_file": actual_file
        }

        if len(self.evaluation_goals) == 0:
            raise ValueError("Rubric does not have any goals!")

        # Evaluate each goal:
        for g in self.evaluation_goals:
            logging.debug_msg(
                "Evaluating goal '{}' @ {}...".format(
                    g.feedback_topic(),
                    id(g)
                )
            )
            # Task is automatically made available as part of context.
            result = g.evaluate(base_context)
            logging.debug_msg("...result is: {}".format(result))
            logging.debug_msg("...review result is: {}".format(g.result))

            # Double-check that the goal correctly stored the value it
            # returned
            if result != g.result:
                logging.debug_msg(
                    f"WARNING: Goal's returned result differs from"
                    f" stored result!\nGoal:"
                    f" '{g.feedback_topic()}'\nReturned:"
                    f" {result}\nStored: {g.result}"
                )

        # Run our metric over the evaluated goals:
        metric_result = self.metric(self.evaluation_goals)

        # Integrate results into our report:
        report["evaluation"] = metric_result["evaluation"]
        report["summary"] = metric_result["summary"]
        report["table"] = metric_result["table"]
        report["warnings"].extend(metric_result["warnings"])

        # Build our contexts list now that contexts should be caching the
        # same values used during testing:
        report["contexts"] = self.create_contexts_list(
            self.evaluation_goals,
            base_context
        )

        # Elevate warnings from contexts to the main warnings list.
        for creport in report["contexts"]:
            report["warnings"].extend(creport.get("warnings", []))

        # Build our files dictionary based on FileContext objects. It
        # maps file names to dictionaries with "path" slots (and possibly
        # more if we can dig up more info).
        all_filenames = {
            base_context["default_file"]: {
                "path": os.path.abspath(
                    os.path.join(
                        base_context["submission_root"],
                        base_context["actual_file"]
                    )
                )
            }
        }
        for ctx in clist:
            if isinstance(ctx, contexts.FileContext):
                if ctx.target_file is not None:
                    ctx_result = ctx.create(base_context)
                    name = ctx_result.get("filename", ctx.target_file)
                    path = ctx_result.get("file_path", name)
                    if name not in all_filenames:
                        all_filenames[name] = { "path": path }

        # Look for code contexts which have handled parsing on target
        # files, and add "source" and possibly "original_source" slots
        for ctx in clist:
            if isinstance(ctx, contexts.CodeContext):
                ctx_result = ctx.create(base_context)
                if "filename" in ctx_result:
                    name = ctx_result["filename"]
                    original = ctx_result["original_source"]
                    fixed = ctx_result["source"]
                    all_filenames[name]["source"] = fixed
                    if original != fixed:
                        all_filenames[name]["original_source"] = original
                # Otherwise there was some kind of error we assume

        # Grab file contents if we haven't already
        for filename in all_filenames:
            file_info = all_filenames[filename]
            entry = {
                "filename": filename,
                "path": file_info["path"]
            }
            report["files"].append(entry)
            if "source" in file_info:
                entry["code"] = file_info["source"]
            else:
                with open(entry["path"], 'r', encoding="utf-8") as fin:
                    if entry["path"].endswith(".py"):
                        entry["code"] = fin.read()
                    else:
                        entry["raw"] = fin.read()

            if "original_source" in file_info:
                entry["original_code"] = file_info["original_source"]

        return report

    def validate(self, task_info, username, tests_target, target):
        """
        Validates tests for this task based on the given submitted tests
        file and submission file (the task_info includes generic info
        about the task, the username identifies who submitted it, the
        tests_target identifies the file or folder to be evaluated, and
        the target identifies the base task file or folder to run tests
        against).

        See `tasks.json` for the task info format (it's a dictionary
        stored in the "tasks" slot under its taskid as a key).

        Returns a report object that has information about which
        validation goal(s) from the rubric passed or failed, and the
        overall performance as determined by the rubric's metric.

        If submitted tests cannot be loaded due to a syntax error or
        parsing fails for some other reason, the report will mention
        that in as much detail as it can, and the normal rubric items
        will be skipped.

        Note: This function completely resets all validation goals and
        clears the caches of any associated `potluck.contexts.Context`
        objects before it starts evaluating goals.

        TODO: We mostly effectively ignore the `target` argument because
        we grab the solution (see `contexts.TestsFileContext`). Get rid
        of it?

        The returned report dictionary has the same keys/values as the
        result from `Rubric.evaluate`.
        """
        # Empty report:
        report = {
            "taskid": task_info["id"],
            "evaluation": "unknown",
            "summary": "No summary has been generated.",
            "files": [],
            "warnings": [],
            "table": [],
            "contexts": []
        }

        # Set up a rewrite rule for the spec file
        if self.spec_file:
            html_tools.set_tb_rewrite(
                self.spec_file,
                "<task specification>"
            )

        # Check for a missing submission:
        if not os.path.exists(tests_target):
            report["warnings"] = [
                "You did not submit any tests for this task."
            ]
            report["evaluation"] = "incomplete"
            report["summary"] = "You did not submit any tests for this task."
            # Early return: no need to grade rubric items
            return report

        # Check for a missing submission:
        if not os.path.exists(target):
            report["warnings"] = [
                "We did not find the code to test."
            ]
            report["evaluation"] = "incomplete"
            report["summary"] = "We did not find the code to test."
            # Early return: no need to grade rubric items
            return report

        # Reset each goal + any associated contexts:
        for g in self.validation_goals:
            g.full_reset()

        # Ensure context descriptions are unique:
        clist = self.all_contexts(self.validation_goals)
        contexts.add_context_numbering(clist)

        # Figure out whether tests target is a directory or file
        if os.path.isdir(tests_target):
            submission_root = tests_target
            default_file = task_info.get(
                "tests_target",
                "test_" + task_info["target"]
            )
            actual_file = default_file
        else:
            submission_root, actual_file = os.path.split(tests_target)
            default_file = task_info.get(
                "tests_target",
                "test_" + task_info["target"]
            )

        # Figure out whether submission target is a directory or file
        if os.path.isdir(target):
            target_root = target
            target_default_file = task_info["target"]
            target_actual_file = target_default_file
        else:
            target_root, target_actual_file = os.path.split(target)
            target_default_file = task_info["target"]

        # Create our base context:
        base_context = {
            "task_info": task_info,
            "username": username,
            "submission_root": target_root,
            "default_file": target_default_file,
            "actual_file": target_actual_file,
            "tests_submission_root": submission_root,
            "default_tests_file": default_file,
            "actual_tests_file": actual_file
        }

        if len(self.validation_goals) == 0:
            raise ValueError("Rubric does not have any validation goals!")

        # Evaluate each goal:
        for g in self.validation_goals:
            logging.debug_msg(
                "Evaluating validation goal '{}' @ {}...".format(
                    g.feedback_topic(),
                    id(g)
                )
            )
            # Task is automatically made available as part of context.
            result = g.evaluate(base_context)
            logging.debug_msg("...result is: {}".format(result))
            logging.debug_msg("...review result is: {}".format(g.result))

            # Double-check that the goal correctly stored the value it
            # returned
            if result != g.result:
                logging.debug_msg(
                    f"WARNING: Validation goal's returned result differs"
                    f" from stored result!\nGoal:"
                    f" '{g.feedback_topic()}'\nReturned:"
                    f" {result}\nStored: {g.result}"
                )

        # Run our metric over the evaluated goals:
        # TODO: Allow/require separate validation metrics?
        metric_result = self.metric(self.validation_goals)

        # Integrate results into our report:
        report["evaluation"] = metric_result["evaluation"]
        report["summary"] = metric_result["summary"]
        report["table"] = metric_result["table"]
        report["warnings"].extend(metric_result["warnings"])

        # Build our contexts list now that contexts should be caching the
        # same values used during testing:
        report["contexts"] = self.create_contexts_list(
            self.validation_goals,
            base_context
        )

        # Elevate warnings from contexts to the main warnings list.
        for creport in report["contexts"]:
            report["warnings"].extend(creport.get("warnings", []))

        # Build our files dictionary based on TestsFileContext objects.
        # It maps file names to dictionaries with "path" slots (and
        # possibly more if we can dig up more info).
        all_filenames = {
            base_context["default_tests_file"]: {
                "path": os.path.abspath(
                    os.path.join(
                        base_context["submission_root"],
                        base_context["actual_tests_file"]
                    )
                )
            }
        }
        for ctx in clist:
            if isinstance(ctx, contexts.TestsFileContext):
                if ctx.target_tests_file is not None:
                    ctx_result = ctx.create(base_context)
                    name = ctx_result.get(
                        "tests_filename",
                        ctx.target_tests_file
                    )
                    path = ctx_result.get("tests_file_path", name)
                    if name not in all_filenames:
                        all_filenames[name] = { "path": path }

        # Look for code contexts which have handled parsing on target
        # files, and add "source" and possibly "original_source" slots
        for ctx in clist:
            if isinstance(ctx, contexts.CodeContext):
                ctx_result = ctx.create(base_context)
                if "tests_filename" in ctx_result:
                    name = ctx_result["tests_filename"]
                    original = ctx_result["original_tests_source"]
                    fixed = ctx_result["tests_source"]
                    all_filenames[name]["source"] = fixed
                    if original != fixed:
                        all_filenames[name]["original_source"] = original
                # Otherwise there was some kind of error we assume

        # Grab file contents if we haven't already
        for filename in all_filenames:
            file_info = all_filenames[filename]
            entry = {
                "filename": filename,
                "path": file_info["path"]
            }
            report["files"].append(entry)
            if "source" in file_info:
                entry["code"] = file_info["source"]
            else:
                with open(entry["path"], 'r', encoding="utf-8") as fin:
                    if entry["path"].endswith(".py"):
                        entry["code"] = fin.read()
                    else:
                        entry["raw"] = fin.read()

            if "original_source" in file_info:
                entry["original_code"] = file_info["original_source"]

        return report

    def goals_by_id(self, fragment):
        """
        Retrieves one or more of the goals from this rubric according to
        its identifier. Note that it's possible for multiple goals to
        share the same identifier (only when rendered into HTML do they
        get suffixes to make them unique), so this function always
        returns a list of goals, which is likely to be length-1. Of
        course, an empty list is returned if no goals have the given ID.
        Any goal whose identifier contains the provided string will be
        included in the goals returned, although '^^^' will be added to
        the front and a '$$$' to the end when checking this, so you can
        use those in your fragment; neither character normally appears
        inside of non-custom identifiers.
        """
        # TODO: Prefix these for evaluation/validation?
        return [
            g
            for g in self.evaluation_goals + self.validation_goals
            if fragment in ('^^^' + g.identifier + '$$$')
        ]


#----------------------------------------------------------------------#
# Performance metrics create evaluation, summary, and table from goals #
#----------------------------------------------------------------------#

def overall_evaluation(foundational, core, extra):
    """
    Given lists of evaluated foundational, core, and extra goals, returns
    a pair containing an overall evaluation string and a summary string
    based on the following rules. Treating each core goal as 1 point,
    with 1/2 point for partial accomplishment, the metric computes a
    point total for core goals and then:

    - If a score of at least 1/2 of the number of core goals is met, and
      all of the foundational goals are accomplished, the overall
      evaluation is "partially complete".
    - Depending on the number of core goals, a completeness point
      threshold is established (TODO: more principled than this?):
      - If there is only 1 core goal, the threshold is 1 (it's impossible
        to score 'almost complete' in this scenario).
      - Otherwise, the threshold is the number of core goals minus a
        fudge factor of 10% rounded up to the nearest 0.5. In other
        words, for 2-5 core goals the fudge factor is 0.5, for 5-10 it's
        1, for 11-15 it's 1.5, for 16-20 it's 2, etc.
    - If at least one core goal is not fully accomplished, but the core
      point total is equal to or greater than the completeness point
      threshold, then the overall evaluation is "almost complete".
    - If all of the core goals are fully accomplished, but at least one
      extra goal is not fully accomplished, the evaluation is "complete".
    - If all of the core goals and all of the extra goals are
      accomplished, the overall evaluation is "excellent".
    - If either at least one foundational goal is failed, or the score
      for core goals is less than 1/2 of the number of core goals, the
      evaluation is "incomplete".
    """
    # Check foundational goals
    failed_foundational = []
    for g in foundational:
        logging.debug_msg(
            "Reviewing foundational goal '{}' @ {}...".format(
                g.feedback_topic(),
                id(g)
            )
        )
        logging.debug_msg("...result is: {}".format(g.result))
        if g.result["status"] not in ("accomplished", "partial"):
            failed_foundational.append(g)

    # Check core goals
    core_score = 0
    core_accomplished = []
    core_partial = []
    for g in core:
        logging.debug_msg(
            "Reviewing core goal '{}' @ {}...".format(
                g.feedback_topic,
                id(g)
            )
        )
        logging.debug_msg("...result is: {}".format(g.result))
        if g.result["status"] == "accomplished":
            core_score += 1
            core_accomplished.append(g)
        elif g.result["status"] == "partial":
            core_score += 0.5
            core_partial.append(g)

    # Nicer repr
    if int(core_score) == core_score:
        core_score = int(core_score)

    # Check extra goals
    extra_unaccomplished = []
    for g in extra:
        logging.debug_msg(
            "Reviewing extra goal '{}' @ {}...".format(
                g.feedback_topic(),
                id(g)
            )
        )
        logging.debug_msg("...result is: {}".format(g.result))
        if g.result["status"] != "accomplished":
            extra_unaccomplished.append(g)

    # Feedback for core and extra goals:
    if len(core) < 2:
        core_threshold = len(core)
    else:
        core_threshold = len(core) - (math.ceil(0.2 * len(core)) / 2) - 0.01
        # the 0.01 is extra careful of rounding errors

    if core_score == len(core):
        # Perfect core score -> 'complete' or 'excellent' overall
        if len(extra_unaccomplished) == 0:
            # Extras all accomplished + core all accomplished -> 'excellent'
            return (
                "excellent",
                "<p>You accomplished all core and extra goals. Great job!</p>"
            )
        else:
            return (
                "complete",
                (
                    "<p>You accomplished the core goals. Good job!</p>"
                    "<p>You accomplished"
                    f" {len(extra) - len(extra_unaccomplished)} of"
                    f" {len(extra)} extra goals.</p>"
                )
            )

    elif core_score >= core_threshold:
        # Close-enough core score: "almost complete"
        return (
            "almost complete",
            (
                f"<p>You accomplished {core_score} (nearly all) of the"
                f" {len(core)} core goals.</p>"
            )
        )

    else:
        # Not even close-enough
        half = len(core) * 0.5
        if half == int(half): # Nicer repr
            half = int(half)
        if core_score >= half:
            return (
                "partially complete",
                (
                    f"<p>You accomplished {core_score} (at least {half})"
                    f" of the {len(core)} core goals.</p>"
                )
            )
        else:
            return (
                "incomplete",
                (
                    f"<p>You accomplished only {core_score} (less than"
                    f" {half}) of the {len(core)} core goals.</p>"
                )
            )


def summarize_category_row(
    row,
    goals,
    all_or_nothing=False,
    half_matters=False,
    blank=False
):
    """
    Given a table row and a list of goals, adds "status" and
    "explanation" entries to the given row based on whether some,
    more/less than half, and/or all of the goals in the list were
    accomplished.

    If all_or_nothing is given as True, then the status will always be
    either "accomplished" if all goals were, or "failed" if at least one
    wasn't (even if it was partial).

    If half_matters is given as True, a note about whether or not at
    least half of the goals were accomplished will be added, counting
    partially-accomplished goals as 1/2 point.

    This function modifies the provided row and doesn't return anything.

    If blank is set to True, the status/explanation are set according to
    BLANK_RESULT.
    """
    if blank:
        row["status"] = BLANK_RESULT["status"]
        row["explanation"] = BLANK_RESULT["explanation"]
        return

    accomplished = len(
        [g for g in goals if g.result["status"] == "accomplished"]
    )
    partial = len(
        [g for g in goals if g.result["status"] == "partial"]
    )
    count = len(goals)

    if accomplished == count:
        row["status"] = "accomplished"
        row["explanation"] = "Accomplished all {} {}.".format(
            count,
            phrasing.plural(count, "goal")
        )
    else:
        points = accomplished + 0.5 * partial
        if all_or_nothing:
            row["status"] = "failed"
            row["explanation"] = "Failed to fully accomplish {} {}.".format(
                count - accomplished,
                phrasing.plural(count - accomplished, "goal")
            )
        else:
            row["explanation"] = "Accomplished {} of {} {}.".format(
                round(points) if round(points) == points else points,
                count,
                phrasing.plural(count, "goal")
            )
            if points < count / 2 - 0.001:
                row["status"] = "failed"
            else:
                row["status"] = "partial"

        if half_matters:
            if points < count / 2 - 0.001:
                half_msg = " (less than half overall)."
            else:
                half_msg = " (at least half overall)."
            row["explanation"] = row["explanation"][:-1] + half_msg


def foundational_core_extras_metric(goals, blank=False):
    """
    Summarizes a list of evaluated goals by looking at those tagged
    as "foundational" and "core" and treating the rest as extras, while
    ignoring any tagged with "feedback_only".  It assigns an evaluation
    using the overall_evaluation function.

    If blank is given as True, the report will include an evaluation of
    "not evaluated" and will not assign success or failure overall or to
    individual goal categories. Use this, along with unevaluated goals,
    to create a blank rubric.

    This function returns a dictionary with the following keys:

    - evaluation: A short string providing an overall evaluation of
        the submission, as described above.
    - summary: A string containing HTML code that summarizes the
        evaluation in a few sentences. It contains descriptions of
        how many goals in each category were accomplished.
    - table: A table dictionary, similar to those returned by
        `Goal.table. It will have 'description', 'tags', 'status',
        'explanation', and perhaps 'subtable' keys.
    - warnings: A list of HTML strings including all warnings
        generated by any goal. TODO: Actually just an empty list for
        now.
    """

    # Sort goals into categories (multiple membership allowed in some cases)
    foundational = []
    core = []
    extra = []
    feedback = []
    for g in goals:
        category = g.tags.get("category", "extra")
        if category == "foundational":
            foundational.append(g)
        elif category == "core":
            core.append(g)
        elif category == "feedback_only":
            feedback.append(g)
        else:
            extra.append(g)

    # Include foundational goals:
    foundation_row = {
        "description": (
            "Foundational goals",
            "If one fails, the assignment is incomplete."
        ),
        "tags": { "category": "foundational" },
        "status": "unknown",
        "explanation": "No explanation yet.",
        "subtable": [],
    }
    for g in foundational:
        foundation_row["subtable"].extend(g.table(blank=blank))
    summarize_category_row(
        foundation_row,
        foundational,
        all_or_nothing=True,
        blank=blank
    )

    # Include core goals:
    core_row = {
        "description": (
            "Core goals",
            (
                "Complete all of these for core credit. Get partial"
                " credit for completing at least half, and more"
              + " partial credit for completing at least 90%."
            )
        ),
        "tags": { "category": "core" },
        "status": "unknown",
        "explanation": "No explanation yet.",
        "subtable": [],
    }
    for g in core:
        core_row["subtable"].extend(g.table(blank=blank))
    summarize_category_row(core_row, core, half_matters=True, blank=blank)

    # Include extra goals:
    extra_row = {
        "description": (
            "Extra goals",
            (
                "Complete all of these in addition to all of the core"
              + " goals for a perfect score."
            )
        ),
        "tags": { "category": "extra" },
        "status": "unknown",
        "explanation": "No explanation yet.",
        "subtable": [],
    }
    for g in extra:
        extra_row["subtable"].extend(g.table(blank=blank))
    summarize_category_row(extra_row, extra, all_or_nothing=True, blank=blank)

    # Include feedback_only goals:
    feedback_row = {
        "description": ("Additional feedback (not graded):", ""),
        "tags": { "category": "feedback_only" },
        "status": "not applicable",
        "explanation": (
            "These extra items are not graded, but provide potentially "
          + "useful feedback ."
        ),
        "subtable": [],
    }
    for g in feedback:
        logging.debug_msg(
            "Reviewing feedback goal '{}' @ {}...".format(
                g.feedback_topic(),
                id(g)
            )
        )
        logging.debug_msg("...result is: {}".format(g.result))
        feedback_row["subtable"].extend(g.table(blank=blank))
    summarize_category_row(feedback_row, feedback, blank=blank)

    nonempty_rows = list(
        filter(
            lambda row: len(row.get("subtable", [])) > 0,
            [
                foundation_row,
                core_row,
                extra_row,
                feedback_row
            ]
        )
    )

    # If we're creating a blank rubric, stop here and just report what
    # the goals were.
    if blank:
        return {
            "evaluation": "not evaluated",
            "summary": "Blank rubric.",
            "table": nonempty_rows,
            "warnings": [] # TODO: Mechanism to generate these?
        }

    # Build summary and table rows; decide evaluation:
    evaluation, summary = overall_evaluation(foundational, core, extra)

    return {
        "evaluation": evaluation,
        "summary": summary,
        "table": nonempty_rows,
        "warnings": [] # TODO: Mechanism to generate these?
    }


def core_extras_categorized_metric(goals, blank=False):
    """
    Works like foundational_core_extras_metric, but does not use
    foundational goals (only goals tagged "core" vs. not are
    distinguished). However, this version looks at goal type tags and
    creates a table organizing goals by their types and then categories.
    The goal types (supplied via "goal_type" tags) are:

    - "style"
    - "procedure"
    - "process"
    - "product"
    - "behavior"
    - "tests"
    - "other" (any goal not tagged with a type will get this type)

    The overall evaluation and summary of the dictionary returned are the
    same as for the `codder.buoy.foundational_core_extras_metric`, and
    the goal types are not relevant to the evaluation result.
    """

    # Sort goals into categories
    core = []
    extra = []
    feedback = []
    for g in goals:
        cat = g.tags.get("category", "extra")
        if cat == "core":
            core.append(g)
        elif cat == "feedback_only":
            feedback.append(g)
        else:
            extra.append(g)

    # Get evaluation & summary for the goals (no foundational goals)
    evaluation, summary = overall_evaluation([], core, extra)

    # Sort goals again by type tags
    rows = []
    for gtype in GOAL_TYPE_RUBRICS:
        gtype_description = GOAL_TYPE_RUBRICS[gtype]
        gtype_goals = []
        for g in goals:
            if g.tags.get("goal_type", "other") == gtype:
                gtype_goals.append(g)

        # If there aren't any goals in this category, we skip it entirely
        if len(gtype_goals) == 0:
            continue

        # Core/extra/feedback sub-rows for this category
        core_subrow = {
            "description": (
                "Core goals",
                (
                    "Complete all core goals for core credit. Get partial"
                    " credit for completing at least half, and more"
                  + " partial credit for completing at least 90%."
                )
            ),
            "tags": { "category": "core", "goal_type": gtype },
            "status": "unknown",
            "explanation": "No explanation yet.",
            "subtable": [],
        }
        extra_subrow = {
            "description": (
                "Extra goals",
                (
                    "Complete all extra goals in addition to the core"
                  + " goals for a perfect score."
                )
            ),
            "tags": { "category": "extra", "goal_type": gtype },
            "status": "unknown",
            "explanation": "No explanation yet.",
            "subtable": [],
        }
        feedback_subrow = {
            "description": (
                "Additional feedback (not graded):",
                (
                    "These checks and tests are provided to give you"
                  + " more insight into the assignment, but are not part"
                  + " of the grading."
                )
            ),
            "tags": { "category": "feedback_only", "goal_type": gtype },
            "status": "not applicable",
            "explanation": (
                "These extra items are not graded, but provide potentially "
              + "useful feedback."
            ),
            "subtable": [],
        }

        # Add goals to sub-rows
        core_here = []
        extra_here = []
        feedback_here = []
        for g in gtype_goals:
            if g in core:
                core_here.append(g)
                core_subrow["subtable"].extend(g.table(blank=blank))
            elif g in feedback:
                feedback_here.append(g)
                feedback_subrow["subtable"].extend(g.table(blank=blank))
            else:
                extra_here.append(g)
                extra_subrow["subtable"].extend(g.table(blank=blank))

        # List the non-empty sub-rows
        nonempty_subrows = []
        for sub in (core_subrow, extra_subrow, feedback_subrow):
            if len(sub["subtable"]) > 0:
                nonempty_subrows.append(sub)

        # Main row for this category
        row = {
            "description": gtype_description,
            "tags": { "category": "type_group", "goal_type": gtype },
            "status": "unknown",
            "explanation": "No explanation yet.",
            "subtable": nonempty_subrows,
        }
        # Add this row to our rows list
        rows.append(row)

        # Summarize each sub-row
        summarize_category_row(core_subrow, core_here, blank=blank)
        summarize_category_row(extra_subrow, extra_here, blank=blank)
        summarize_category_row(feedback_subrow, feedback_here, blank=blank)

        # Status + explanation for this entire category
        if blank:
            # Blank status + explanation
            row["status"] = BLANK_RESULT["status"]
            row["explanation"] = BLANK_RESULT["explanation"]
        else:
            # Goal-type group status based on core goals alone
            row["status"] = core_subrow["status"]
            ngoals = len(core_subrow["subtable"])
            if ngoals == 0:
                # no core goals in this category
                if len(extra_subrow["subtable"]) == 0:
                    # no evaluated goals at all...
                    row["status"] = "unknown"
                    ngoals = len(feedback_subrow["subtable"])
                    row["explanation"] = (
                        "The {} {} {} contribute to your overall"
                        " evaluation ({} just informative)."
                    ).format(
                        gtype,
                        phrasing.plural(ngoals, "goal"),
                        phrasing.plural(ngoals, "does not", "do not"),
                        phrasing.plural(ngoals, "they're", "it's"),
                    )
                else:
                    # Base on the extra goals
                    row["status"] = extra_subrow["status"]
                    ngoals = len(extra_subrow["subtable"])
                    if row["status"] == "accomplished":
                        if ngoals > 1:
                            row["explanation"] = (
                                "Accomplished all {} extra {} goals."
                            ).format(ngoals, gtype)
                        else:
                            row["explanation"] = (
                                "Accomplished the {} extra {} goal."
                            ).format(ngoals, gtype)
                    elif row["status"] == "partial":
                        if ngoals > 1:
                            row["explanation"] = (
                                "Accomplished most of the {} extra {}"
                                " goals."
                            ).format(ngoals, gtype)
                        else:
                            row["explanation"] = (
                                "Partially accomplished the extra {}"
                                " goal."
                            ).format(gtype)
                    elif row["status"] == "failed":
                        if ngoals > 1:
                            row["explanation"] = (
                                "Did not accomplished at least half of"
                                " the {} extra {} goals."
                            ).format(ngoals, gtype)
                        else:
                            row["explanation"] = (
                                "Did not accomplish the extra {} goal."
                            ).format(gtype)
                    else:
                        row["explanation"] = (
                            "No conclusive evaluation for the extra {}"
                            " {}."
                        ).format(gtype, phrasing.plural(ngoals, "goal"))
            elif row["status"] == "accomplished":
                # Explanation tweaked based on extra goals
                nextra = len(extra_subrow["subtable"])
                cat_phrase = "core"
                if (
                    nextra > 0
                and extra_subrow["status"] == "accomplished"
                ):
                    cat_phrase = "core and extra"
                    ngoals += nextra
                if ngoals > 1:
                    row["explanation"] = (
                        "Accomplished all {} {} {} goals."
                    ).format(ngoals, cat_phrase, gtype)
                else:
                    row["explanation"] = (
                        "Accomplished the {} {} goal."
                    ).format(cat_phrase, gtype)
            elif row["status"] == "partial":
                if ngoals > 1:
                    row["explanation"] = (
                        "Accomplished most of the core {} goals."
                    ).format(gtype)
                else:
                    row["explanation"] = (
                        "Partially accomplished the core {} goal."
                    ).format(gtype)
            elif row["status"] == "failed":
                if ngoals > 1:
                    row["explanation"] = (
                        "Did not accomplish at least half of the core"
                        " {} goals."
                    ).format(gtype)
                else:
                    row["explanation"] = (
                        "Did not at least partially accomplish the core"
                        " {} goal."
                    ).format(gtype)
            else:
                row["explanation"] = (
                    "No conclusive evaluation for the core {} {}."
                ).format(gtype, phrasing.plural(ngoals, "goal"))

    # If we're creating a blank rubric, stop here and just report what
    # the goals were.
    if blank:
        return {
            "evaluation": "not evaluated",
            "summary": "Blank rubric.",
            "table": rows,
            "warnings": [] # TODO: Mechanism to generate these?
        }
    else:
        # Otherwise, include the evaluation and summary
        return {
            "evaluation": evaluation,
            "summary": summary,
            "table": rows,
            "warnings": [] # TODO: Mechanism to generate these?
        }


#---------------#
# Goal subtypes #
#---------------#

class NoteGoal(Goal):
    """
    A NoteGoal just serves as an extra rubric entry that's not associated
    with any test.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=("BLANK NOTE GOAL", "THIS GOAL HAS NOT BEEN DEFINED"),
        explanation="",
        **kwargs
    ):
        """
        A task ID (string), an identifier (string), and a description are
        required, and an explanation (shown only during feedback, but not
        on the rubric) may also be given. If no category tag is
        specified, the category tag will be set to "feedback_only".

        The categorizer "note:" will be prepended to the identifier.
        """
        tags = kwargs.setdefault("tags", {})
        if "category" not in tags:
            tags["category"] = "feedback_only"

        super().__init__(
            taskid,
            "node:" + identifier,
            description,
            **kwargs
        )
        self.set_default_goal_type("other")
        self.explanation = explanation

    def evaluate_in_context(self, context=None):
        """
        Simply returns the pre-defined explanation.
        """
        return {
            "status": "not applicable",
            "explanation": self.explanation
        }


class JointGoal(Goal):
    """
    A joint goal requires 1 or more subgoals to succeed and bases its
    success off of the success of its subgoals.

    If the `JointGoal` is tagged as "transparent", then when producing a
    table, it will not create an entry for itself and instead will just
    return the subtable containing sub-goals. This is useful when it is
    obvious from context how failure of a subgoal would affect the
    super-goal.

    The joint goal takes its goal type tag from the tags of its child
    goals, or sets its tag to "other" if its children have more than one
    goal type tag.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=("BLANK JOINT GOAL", "THIS GOAL HAS NOT BEEN DEFINED"),
        parts=None,
        required=None,
        partial_required=None,
        stop_early=False,
        **kwargs
    ):
        """
        You must provide a task ID, an identifier, a description, a list
        of parts (default empty list), and a number of parts required
        (default is the size of the given parts list).

        The categorizer "joint:" is prepended to the identifier.

        If partial_required is given, as long as that many parts are
        strictly accomplished, this goal will count as partially
        accomplished (must be lower than required).

        If stop_early is given as True, if the outcome is known based on
        goals already evaluated, the `JointGoal` will not evaluate
        subsequent goals.
        """
        parts = parts or []

        # Pre-specify goal type tag
        subgoal_types = set()
        for p in parts:
            subgoal_types |= set(
                [t for t in p.tags if t in GOAL_TYPE_RUBRICS]
            )

        if len(subgoal_types) == 1:
            goal_type = list(subgoal_types)[0]
        else:
            # Zero or more than one explicit subgoal type
            goal_type = "other"

        super().__init__(
            taskid,
            "joint:" + identifier,
            description,
            **kwargs
        )
        self.set_default_goal_type(goal_type)
        self.parts = parts
        if required is None:
            required = len(parts)
        self.required = required
        self.partial_required = partial_required
        self.stop_early = stop_early

    def subgoals(self):
        """
        List of subgoals of this goal (our sub-goals).
        """
        return self.parts

    def table(self, blank=False):
        """
        A `JointGoal`'s table by default contains a sub-table consisting of
        the combined tables for each of its sub-goals, but this is
        suppressed if the goal has the "hide_subgoals" tag.

        If it has the "hide_unevaluated" tag, parts which were never
        evaluated due to early stopping are omitted from the subtable.

        See `Goal.table` regarding the table format.
        """
        subtable = []
        if "hide_subgoals" in self.tags:
            subtable = None
        else:
            for i, subgoal in enumerate(self.parts):
                # Only goals that we actually evaluated belong in our result
                # table:
                if (
                    "hide_unevaluated" in self.tags
                and i >= self.result.get("goals_evaluated", len(self.parts))
                ):
                    break
                subtable.extend(subgoal.table(blank=blank))

        if "transparent" in self.tags:
            result = subtable
        else:
            result = super().table(blank=blank)
            result[0]["subtable"] = subtable

        return result

    def evaluate_in_context(self, context=None):
        """
        To evaluate a `JointGoal`, we evaluate each subgoal in order. If at
        least the required number of them are "accomplished", the joint
        goal is also "accomplished". If not, but at least the required
        number are either "accomplished" or "partial", the joint goal is
        "partial". Otherwise, it is "failed". If the result is known
        before all goals are evaluated, the `JointGoal` will skip
        unnecessary parts, unless it was created with stop_early=False.
        """
        context = context or {}

        passed = 0
        partial = 0
        remaining = len(self.parts)

        if self.required == 0 and self.stop_early:
            self.result = {
                "status": "accomplished",
                "goals_evaluated": 0
            }
            self.set_explanation(
                context,
                default="Context established; no testing required."
            )
            return self.result

        if self.required == 0:
            pass_msg = "Context established; no testing required."
            partial_msg = "ERROR: THIS MESSAGE SHOULD NEVER BE DISPLAYED (1)"
            fail_msg = "ERROR: THIS MESSAGE SHOULD NEVER BE DISPLAYED (2)"
        elif self.required == len(self.parts) and self.required > 1:
            pass_msg = "All parts accomplished."
            if self.partial_required is not None:
                partial_msg = (
                    "All parts at least partially accomplished, or at "
                  + "least {} of {} parts accomplished."
                ).format(self.partial_required, len(self.parts))
            else:
                partial_msg = "All parts at least partially accomplished."
            fail_msg = "At least one part failed."
        elif self.required == len(self.parts):
            pass_msg = "Subgoal accomplished."
            partial_msg = "Subgoal partially accomplished."
            fail_msg = "Subgoal failed."
        else:
            pass_msg = "At least {} of {} parts accomplished.".format(
                self.required,
                len(self.parts)
            )
            if self.partial_required is not None:
                partial_msg = (
                    "At least {} of {} parts accomplished or partially "
                  + "accomplished, or at least {} of {} parts accomplished."
                ).format(
                    self.required,
                    len(self.parts),
                    self.partial_required,
                    len(self.parts),
                )
                fail_msg = (
                    "Failed to accomplish at least {} of {} parts."
                ).format(
                    self.partial_required,
                    len(self.parts)
                )
            else:
                partial_msg = (
                    "At least {} of {} parts accomplished or partially "
                  + "accomplished."
                ).format(self.required, len(self.parts))
                fail_msg = (
                    "Failed to accomplish at least {} of {} parts."
                ).format(
                    self.required,
                    len(self.parts)
                )

        goals_evaluated = 0
        for subgoal in self.parts:
            # Shallow copy of our context:
            sub_context = {}
            sub_context.update(context)
            result = subgoal.evaluate(sub_context)
            goals_evaluated += 1
            result_status = result.get("status", "unknown")
            remaining -= 1
            if result_status == "accomplished":
                passed += 1
            elif result_status == "partial":
                partial += 1

            if self.stop_early:
                if passed >= self.required:
                    self.result = {
                        "status": "accomplished",
                        "goals_evaluated": goals_evaluated
                    }
                    self.set_explanation(context, default=pass_msg)
                    return self.result
                elif (
                    (
                        passed + partial >= self.required
                    and passed + remaining < self.required
                    )
                 or (
                        self.partial_required is not None
                    and passed >= self.partial_required
                    and passed + remaining < self.required
                    )
                ):
                    self.result = {
                        "status": "partial",
                        "goals_evaluated": goals_evaluated
                    }
                    self.set_explanation(context, default=partial_msg)
                    return self.result

        if passed >= self.required:
            self.result = {
                "status": "accomplished",
                "goals_evaluated": goals_evaluated
            }
            self.set_explanation(context, default=pass_msg)
            return self.result
        elif (
            (passed + partial >= self.required)
         or (
                self.partial_required is not None
            and passed >= self.partial_required
            )
        ):
            self.result = {
                "status": "partial",
                "goals_evaluated": goals_evaluated
            }
            self.set_explanation(context, default=partial_msg)
            return self.result
        else:
            self.result = {
                "status": "failed",
                "goals_evaluated": goals_evaluated
            }
            self.set_explanation(context, default=fail_msg)
            return self.result


class FailGoal(Goal):
    """
    A fail goal simply swaps accomplished for failed and vice versa in
    the result of a sub-goal.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=None,
        goal=None,
        permit_partial=True,
        **kwargs
    ):
        """
        Requires a task ID, an identifier, and a subgoal, with optional
        description, explanations, and tags. The description should
        generally be phrased as the negation of the subgoal's
        description, and the default (if None is given explicitly) is to
        add "Do not " in front of the subgoal's description title and add
        " You need to avoid this." to the end of its details.

        The categorizer "fail:" is prepended to the identifier.

        If permit_partial is specified, True means that partial success
        of the subgoal is partial success of this goal (the default), and
        False means that even partial success of the subgoal is full
        failure of this goal.
        """
        # Auto description
        if description is None:
            subrub = goal.description
            subtitle, subdetails = subrub
            if subtitle[0].isupper():
                subtitle = subtitle[0].lower() + subtitle[1:]
            description = (
                "Do not " + subtitle,
                subdetails + " You need to avoid this."
            )

        # Lift goal type from sub-goal
        goal_type = goal.tags.get("goal_type", "other")

        super().__init__(
            taskid,
            "fail:" + identifier,
            description,
            **kwargs
        )
        self.set_default_goal_type(goal_type)

        if goal is None:
            raise ValueError("A FailGoal must be provided a subgoal!")
        self.goal = goal
        self.permit_partial = permit_partial

    def subgoals(self):
        """
        List of subgoals of this goal (just our single goal).
        """
        if self.goal:
            return [ self.goal ]
        else:
            return []

    def table(self, blank=False):
        """
        The table for a `FailGoal` is a copy of it's subgoal's table,
        with the status, description, and explanation from the
        `FailGoal`'s result. This means that the `FailGoal` itself does
        not appear as a separate entry in rubric tables. Any tags for the
        `FailGoal` are added to the tags of the subgoal.

        See `Goal.table` regarding the table format.
        """
        row = self.goal.table(blank=blank)[0]
        category = self.tags.get("category", "unknown")
        row["id"] = "goal:" + category + '.' + self.identifier
        row["description"] = list(self.description[:])
        row["tags"] = list(set(row["tags"]) | set(self.tags))
        if not blank:
            row["status"] = self.result["status"]
            row["explanation"] = self.result["explanation"]

        return [ row ]

    def evaluate_in_context(self, context=None):
        """
        Evaluates the sub-goal, and returns a result which replaces
        "accomplished" with "failed" and vice versa. Does not affect a
        result of "partial" unless permit_partial is set to False, in
        which case a "partial" result is converted to "failed."
        """
        context = context or {}
        self.result = {}
        self.result.update(self.goal.evaluate(context))
        if self.result["status"] == "accomplished":
            self.result["status"] = "failed"
        elif self.result["status"] == "failed":
            self.result["status"] = "accomplished"
        elif self.result["status"] == "partial" and not self.permit_partial:
            self.result["status"] = "failed"
        # else don't modify the status

        # Update explanation from sub_result only if we have a matching
        # explanation function.
        self.set_explanation(context, default=self.result["explanation"])

        return self.result


class PreconditionGoal(Goal):
    """
    A precondition goal requires that a condition goal is achieved, and
    only if it is does it return an evaluation based on a subgoal.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=(
            "BLANK PRECONDITION GOAL",
            "THIS GOAL HAS NOT BEEN DEFINED"
        ),
        precondition=None,
        goal=None,
        **kwargs
    ):
        """
        You must provide a task ID, an identifier, a description, a
        precondition goal, and a subgoal.

        The categorizer "precondition:" is prepended to the identifier.
        """
        # Pre-specify goal type tag
        subgoal_types = set()
        for sg in [precondition, goal]:
            subgoal_types |= set(
                [t for t in sg.tags if t in GOAL_TYPE_RUBRICS]
            )

        if len(subgoal_types) == 1:
            goal_type = list(subgoal_types)[0]
        else:
            # Zero or more than one explicit subgoal type
            goal_type = "other"

        super().__init__(
            taskid,
            "precondition:" + identifier,
            description,
            **kwargs
        )
        self.set_default_goal_type(goal_type)
        if precondition is None or goal is None:
            raise ValueError(
                "A PreconditionGoal must have both a precondition and a goal!"
            )
        self.precondition = precondition
        self.goal = goal

    def subgoals(self):
        """
        List of subgoals of this goal (our precondition and our goal).
        """
        return [ self.precondition, self.goal ]

    def evaluate_in_context(self, context={}):
        """
        To evaluate a `PreconditionGoal`, we evaluate the precondition. If
        it does not evaluate as "accomplished," then the entire goal
        evaluates to "failed" immediately. If it does evaluate to
        "accomplished," the final goal is evaluated and that result is
        returned.

        If the precondition passes, it is not mentioned in the
        explanation that results, but if it fails, its failure
        explanation is used as the explanation for this goal's failure.

        Even if the precondition passes, this node's explanation function
        is still run on the results, but if it fails, the special
        explanation status "precondition_failed" is used (to
        differentiate from a failed sub-goal post-precondition).
        """
        pre = self.precondition.evaluate(context)
        if pre.get("status") != "accomplished":
            self.result = {
                "status": "failed",
                "precondition_failed": True,
            }
            self.set_explanation(
                context,
                status="precondition_failed",
                default="Precondition failed:<br>\n{}".format(
                    pre.get("explanation", "Cause unknown")
                )
            )
            return self.result
        else:
            self.result = self.goal.evaluate(context)
            self.result["precondition_failed"] = False
            self.set_explanation(context, default=self.result["explanation"])
            return self.result

    def table(self, blank=False):
        """
        A `PreconditionGoal`'s table depends on the result from its
        precondition. If the precondition failed, the table will be the
        precondition's table; otherwise it will be the main goal's table.
        The fact that there is a precondition is thus not visible from
        the table unless the precondition fails.
        TODO: Not that?

        See `Goal.table` regarding the table format.
        """
        if self.result.get("precondition_failed", False):
            return self.precondition.table(blank=blank)
        else:
            return self.goal.table(blank=blank)


class ComparisonTest(Goal):
    """
    Runs a checker function on two arbitrary context slots.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=(
            "BLANK COMPARISON TEST",
            "THIS GOAL HAS NOT BEEN DEFINED"
        ),
        context_slot="value",
        checker=None,
        ref_slot=None,
        **kwargs
    ):
        """
        In addition to a task ID (string) and an identifier (string), a
        description, and optional explanations and/or tags (see the
        `Goal` class), a checker function is needed, which should accept
        value and reference objects and return a goal result (a
        dictionary with status + explanation keys). The context_slot is
        used to determine which slot in the current context to check, and
        ref_slot specifies where to get the reference object, although if
        not given it will default to "ref_" + context_slot.

        The categorizer "test:" is prepended to the identifier.

        If the checker is omitted or given explicitly as None, the goal
        will succeed as long as the appropriate context_slot (and
        ref_slot) are present, and will only fail if the assigned context
        fails to even establish those keys.

        If the ref_slot is the same as the context_slot, the checker
        function will be called with only one value.
        """
        super().__init__(
            taskid,
            "test:" + identifier,
            description,
            **kwargs
        )
        self.context_slot = context_slot
        self.checker = checker
        if ref_slot is None:
            ref_slot = "ref_" + context_slot
        self.ref_slot = ref_slot

    # subgoals is inherited (no subgoals)

    # table is inherited

    def evaluate_in_context(self, context=None):
        """
        Runs the checker and returns its result.
        """
        context = context or {}

        if self.checker is None:
            if self.context_slot in context and self.ref_slot in context:
                self.result = {
                    "status": "accomplished",
                    "explanation": (
                        "Successfully established '{}' context."
                    ).format(self.context_slot)
                }
            elif self.context_slot not in context:
                self.result = {
                    "status": "failed",
                    "explanation": (
                        "Failed to establish '{}' context."
                    ).format(self.context_slot)
                }
            else:
                self.result = {
                    "status": "failed",
                    "explanation": (
                        "Failed to establish '{}' context."
                    ).format(self.ref_slot)
                }
        else:
            try:
                val = context[self.context_slot]
            except KeyError:
                self.result = {
                    "status": "failed",
                    "traceback": html_tools.html_traceback(
                        linkable=context_utils.linkmap(context)
                    )
                }
                self.set_explanation(
                    context,
                    status="crash",
                    default=(
                        "Could not access '{}' for testing."
                        " Context has keys:<br>{}"
                    ).format(
                        self.context_slot,
                        ', '.join(repr(k) for k in context.keys())
                    )
                )
                return self.result

            try:
                ref = context[self.ref_slot]
            except KeyError:
                self.result = {
                    "status": "failed",
                    "traceback": html_tools.html_traceback(
                        linkable=context_utils.linkmap(context)
                    )
                }
                self.set_explanation(
                    context,
                    status="crash",
                    default=(
                        "Could not access '{}' for testing."
                        " Context has keys:<br>{}"
                    ).format(
                        self.ref_slot,
                        ', '.join(repr(k) for k in context.keys())
                    )
                )
                return self.result

            try:
                if self.context_slot == self.ref_slot:
                    self.result = self.checker(val)
                else:
                    self.result = self.checker(val, ref)

                if self.result is None:
                    raise ValueError(
                        "Context checker {} returned None!".format(
                            self.checker
                        )
                    )

                self.set_explanation(
                    context,
                    default=self.result["explanation"]
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
                        title="Error while checking {}:".format(
                            self.context_slot
                        ),
                        linkable=context_utils.linkmap(context)
                    )
                )

        return self.result


class ImplementationCheck(Goal):
    """
    An `ImplementationCheck` inspects the AST of submitted code to
    determine whether it counts as accomplished or failed. An
    `ImplementationCheck`'s subrules must all be accomplished for the
    parent check to count as accomplished. An `ImplementationCheck` looks
    for the first match that can satisfy its subrules.

    `ImplementationCheck`s by default run on the 'scope' context slot
    which contains an AST for the submitted module, or (via refinement by
    `ImplementationCheck`s) a subset of that code. When created, unless
    explicit dependencies are specified via a `test_in` keyword argument,
    each `ImplementationCheck` will grab the current automatic "scope"
    context as its only dependency.
    """
    def __init__(
        self,
        taskid,
        identifier,
        description=(
            "BLANK IMPLEMENTATION CHECK",
            "THIS GOAL HAS NOT BEEN DEFINED"
        ),
        pattern="_",
        name=None,
        match=lambda code, node, env: True,
        use=None,
        min=None, max=None,
        softmin=False, softmax=False,
        outside=None,
        callees=False,
        subrules=None,
        match_identity=lambda code, node, envs: (
            tuple(node) if isinstance(node, list) else node
        ),
        subslip=None,
        normalize=False,
        check_in_def=False,
        force_smaller_match=False,
        **kwargs
    ):
        """
        A task ID, an identifier, and a description are required (see the
        `Goal` class). An appropriate `test_in` dictionary which will
        provide a "scope" slot is typically required.

        The categorizer "check:" is prepended to the identifier.

        `ImplementationCheck` itself uses the following arguments:

        - pattern: A string containing Python code that will be matched
            against using mast. May instead be a list of strings, in
            which case they will be tried in turn to generate matches.
        - name: specifies a name for the construct being searched for.
            The plural will be constructed by adding 's', unless name is
            a tuple, in which case the first entry will be used as the
            singular and the second as the plural. May contain HTML code.
            If pattern is not a list, this can be left out, and the
            pattern will be used as the name.
        - match: A function that accepts the entire submitted AST, the
            node being considered for a match right now, and the current
            binding environment. This function should return True or
            False, and any matches for which it does not return True will
            be ignored.
        - use/min/max: Either the 'use' argument, or one or both of the
            'min' and 'max' arguments should be given, but not both.
            Supplying 'use' sets both 'min' and 'max' to that value. If
            'max' is 0, the pattern is considered a negative pattern, and
            the goal will fail if any matches are found. Otherwise, the
            goal will succeed if the number of matches is between the
            given min and max values, inclusive. If none of these are
            given, the min defaults to 1 and the max to None (no limit).
        - softmin/softmax: If one of these is true, the minimum (or
            maximum) restriction on the number of matches will be treated
            as a soft constraint, and if violated the goal will be
            treated as partially accomplished instead of failed. If they
            are exactly either the string "warn" or "note", then the goal
            will still count as fully accomplished if that constraint is
            violated, but a warning or note will be attached mentioning
            the unexpectedly low/high number of matches. They may also be
            integers or floats, in which case they establish an alternate
            min/max threshold for partial completion. For softmin,
            partial matches are counted as 0.5 of a match towards
            achieving the threshold, but for softmax partial matches are
            ignored.
        - outside: If present, the 'outside' pattern (or list of
            patterns) is checked, and matches will only be considered
            valid if they are not sub-nodes of a match for one of the
            given outside patterns.
        - callees: If given as True, instead of simply searching within
            the context's scope node, this check will look for matches
            within other functions defined in the submitted code which
            are called from within the given scope node. TODO: This is
            still (as of 2020-6) experimental/unstable.
        - subrules: A list of `ImplementationCheck` goals to be tested
            within matches of this goal. Only matches where this goal and
            all of its subrules are accomplished (or partially
            accomplished) will be considered valid (respectively,
            partially valid). If this goal is a negative goal (max = 0),
            it fails if there are any fully valid matches, and partial
            matches are ignored. On the other hand, if it is a positive
            goal (max != 0), it counts as accomplished if the number of
            fully valid matches is within the min and max limits
            (inclusive), and partially accomplished if the number of
            fully valid matches is below the min limit but the number of
            fully valid + partially valid matches is at least the min
            limit.
        - match_identity: a function that returns a hashable object to
            represent the identity of a match for match-counting
            purposes. The function will be given the entire code context,
            the matching node, and a list of matching environments as
            input. It may return a list of identities instead of a single
            identity and each will be counted. By default this is a
            function which just returns the matching node, such that
            multiple matching environments based on the same node are not
            counted as separate matches. One reasonable alternative if
            you know what type of node you're matching would be to return
            some associated string (e.g., the id of a Call node that has
            a Name as its func).
        - subslip: A number of subgoals which are allowed to be violated
            and still count a potential match as a partial match. May be
            fractional, since partially-matched subgoals will be counted
            as 1/2 a point. By default this number will be set to half of
            the number of subgoals, rounded down.
        - normalize: default False; experimental mast option that tries
            to inline some local variable assignments into larger
            expressions for better matching.
        - check_in_def: default False, this option changes the context
            within which the check occurs by default: the check will use
            the 'scope' element from the current context as usual, but
            will then assume that that AST node is a Call to a function
            defined in the same file (within the 'code' element) and will
            look up that definition, running the check in the context of
            that definition rather than in the original scope context
            given to it. This is useful for placing requirements on
            helper functions whose names aren't known ahead of time: a
            parent `ImplementationCheck` can be used to match the helper
            function call, with child checks using check_in_def that
            place requirements on the code in the helper function. The
            check will fail if the 'scope' context provided to it is not
            a Call node, or if it can't find the matching FunctionDef
            node in the 'code' tree of the context it's given.
        - force_smaller_match: default False. If set to True, a match
            which matches the entire target scope will not be considered a
            real match. Use this in places where you want to require
            things like nested loops, since otherwise a sub-requirement
            that's the same as a super-requirement will simply match the
            entire node matched by the super-requirement.
        """
        # Grab parent context
        if "test_in" not in kwargs or kwargs["test_in"] is None:
            kwargs["test_in"] = {}
        if "contexts" not in kwargs["test_in"]:
            kwargs["test_in"]["contexts"] = contexts.auto("scope")

        # Set up Goal properties
        super().__init__(
            taskid,
            "check:" + identifier,
            description,
            **kwargs
        )
        self.set_default_goal_type("procedure")

        # Ensure patterns is a list
        if isinstance(pattern, str):
            self.patterns = [ pattern ]
        else:
            self.patterns = pattern

        # Figure out name
        if name is None:
            if len(self.patterns) > 1:
                raise ValueError(
                    (
                        "When building an ImplementationCheck, if there are "
                      + "multiple patterns, a name must be specified."
                      + " (topic: '{}' / patterns: {})"
                    ).format(self.feedback_topic(), self.patterns)
                )
            else:
                self.name = self.patterns[0]
                self.pl_name = self.name + 's'
        elif isinstance(name, (list, tuple)):
            self.name, self.pl_name = name
        else:
            self.name = name
            self.pl_name = self.name + 's'

        self.match = match

        # Figure out min and max
        if (min is not None or max is not None) and use is not None:
            raise ValueError(
                (
                    "When building an ImplementationCheck, you may supply "
                  + "*either* 'use' or 'min'/'max', but you may not supply "
                  + "'use' if either 'min' or 'max' is given."
                  + " (topic: '{}' / patterns: {})"
                ).format(self.feedback_topic(), self.patterns)
            )
        elif use is not None:
            self.min_allowed = use
            self.max_allowed = use
        elif min is None and max is None:
            # Default is "at least 1"
            self.min_allowed = 1
            self.max_allowed = None
        else:
            self.min_allowed = min
            self.max_allowed = max

        # Is this goal a positive goal (keep searching for any match
        # across possible environments?) or not (fail if any match is
        # found in any environment).
        self.is_positive = self.max_allowed != 0

        self.softmin = softmin
        self.softmax = softmax

        # Make sure outside is a list
        if outside is None:
            self.outside = []
        elif isinstance(outside, str):
            self.outside = [ outside ]
        else:
            self.outside = outside

        self.callees = callees

        self.force_smaller_match = force_smaller_match

        # Set subrules
        if subrules is None:
            self.subrules = []
        else:
            self.subrules = subrules

        self.match_identity = match_identity

        self.subslip = subslip
        if self.subslip is None:
            self.subslip = len(self.subrules) // 2

        self.normalize = normalize

        self.check_in_def = check_in_def

    def subgoals(self):
        """
        List of subgoals of this goal (our precondition and our goal).
        """
        return self.subrules

    def table(self, blank=False):
        """
        Includes sub-table with subrule statuses preserved from the last
        full match, or the last partial match if there are no full
        matches.

        See `Goal.table` regarding the table format.
        """
        result = super().table(blank=blank)

        # Maybe add a subtable:
        if blank:
            result[0]["subtable"] = self.build_subtable(blank=blank)
        elif self.is_positive:
            # TODO: What about tables requested during pre-evaluation
            # description construction?
            result[0]["subtable"] = self.result.get("subtable") or []
        elif self.result.get("status") != "accomplished":
            # For negative rules where we don't want any matches, reporting
            # the successful discovery of sub-rules only makes sense if
            # we failed the goal (because there was a match that
            # shouldn't have been there).
            result[0]["subtable"] = self.result.get("subtable") or []
        # Otherwise don't attach a subtable (negative rules that
        # succeeded because they didn't have any full matches).

        return result

    def build_subtable(self, blank=False):
        """
        Builds a sub-table using the results of each subrule as currently
        evaluated.
        """
        result = []
        for subrule in self.subrules:
            result.extend(subrule.table(blank=blank))
        return result

    def evaluate_in_context(self, context=None):
        """
        Checks the rule within the 'scope' node of the given context,
        respecting bindings in the 'env' dictionary from the given
        context. Uses the entire submitted code if no scope is present,
        and uses an empty dictionary if there is no binding environment.
        Use build_code_context to establish a top-level scope beforehand
        if you are worried about parsing issues causing code to be
        missing.
        """
        # Grab scope and top-scope slots
        task_info = context_utils.extract(context, "task_info")
        scope = context_utils.extract(context, "scope")
        top_scope = context_utils.extract(context, "top_scope")
        filename = context_utils.extract(context, "filename")

        # Create sub-context
        context = context or {}
        sub_context = {}
        sub_context.update(context)

        # Create/extract matching environment
        if sub_context.get("env") is not None:
            env = sub_context["env"]
        else:
            env = {}

        # Swap from the specified scope over to the matching definition
        # if check_in_def was specified:
        if self.check_in_def:
            if not isinstance(scope, ast.Call):
                raise context_utils.MissingContextError(
                    "Attempt to check in a definition but parent check"
                  + " didn't provide a function call to work from:"
                  + "\n{}\n{}".format(scope, self.description)
                )

            if not isinstance(scope.func, ast.Name):
                raise context_utils.MissingContextError(
                    "Attempt to check in a definition but the parent"
                  + " check provided a function call with a complex func"
                  + " expression:\n  {}".format(scope)
                )

            defs = mast.findall(
                top_scope,
                "def {}(___):\n  ___".format(scope.func.id),
                env=env,
                gen=False
            )

            if len(defs) == 0:
                raise context_utils.MissingContextError(
                    (
                        "Attempt to check in a definition but the parent"
                      + " check provided a function call (to {}) with no"
                      + " matching definitions:\n  {}"
                    ).format(scope.func.id, scope)
                )

            # last definition overrides earlier ones if there are multiple
            last_node, last_envs = defs[-1]
            # TODO: DEBUG
            if last_node is None:
                print("None last_node")

            scope = last_node
            # arbitrarily use first env; shouldn't be multiple we hope?
            env = last_envs[0]

        # list of matching AST nodes
        matches = []

        # Scope our match predicate:
        my_match = self.match

        # Our match filter:
        match_filter = lambda node, env: my_match(top_scope, node, env)

        # Define match-collecting function
        def collect_matches(in_scope, memo=None):
            """
            This local function collects matches to any of the patterns
            in this goal's patterns list, subject to the goal's matching
            rule. It accepts a scope (an AST node to search within) and
            uses a memo set to remember which callees have been
            investigated so that recursive functions with callees=True
            will not create an infinite loop.
            """
            nonlocal self
            if memo is None: # remember which callees we've investigated
                memo = set()
            for pat in self.patterns:
                try:
                    for node, envs in mast.findall(
                        in_scope,
                        pat,
                        outside=self.outside,
                        matchpred=match_filter,
                        env=env,
                        normalize=self.normalize,
                        gen=True
                    ):
                        for prev_node, prev_envs in matches:
                            if prev_node == node:
                                # TODO: worry whether this duplicates envs?
                                prev_envs.extend(envs)
                                break
                        else: # if we didn't ever break
                            if not (
                                self.force_smaller_match
                            and node is in_scope
                            ):
                                matches.append((node, envs))

                except Exception:
                    # Rule checks shouldn't crash no matter what students
                    # do...
                    traceback.print_exc()
                    logging.log(
                        (
                            'ERROR CHECKING RULE\n  rule name: "{}"\n'
                          + '  attempted pattern: {}'
                        ).format(self.name, pat)
                    )
                    raise # will be caught below

            # Check for matches in callees too.
            # WARNINGS:
            # - Matches only calls where the function position is a name
            #   (not an arbitrary expression)
            # - Searches the top-level task code node for this name
            #   without understanding shadowing and without considering
            #   arguments/parameters
            # - Attempts to match the full pattern within a single
            #   function (currently cannot automatically split pattern
            #   across a call)
            # - Likely to cause even more exponential blowup
            # - No attempts are made to respect scope when unifying
            #   env with match environments in callees
            if self.callees:
                callee_names = set(
                    call_env['f'].id
                        for call_node, call_envs in mast.findall(
                            in_scope,
                            '_f_(___)',
                            gen=True,
                            matchpred=(
                                lambda node, env: type(env['f']) == ast.Name
                            )
                        ) # noqa: E123
                        for call_env in call_envs
                )
                # Exclude already-checked callees and update memo:
                callee_names -= memo
                memo |= callee_names
                # Check each callee
                for callee_name in callee_names:
                    callee_patterns = [
                        pat.replace("_f_", callee_name)
                        for pat in patterns.ALL_DEF_PATTERNS
                    ]
                    outside_patterns = [
                        pat.replace("_f_", in_scope.name)
                        for pat in patterns.ALL_DEF_PATTERNS
                    ] if type(scope) == ast.FunctionDef else []
                    for cpat in callee_patterns:
                        for callee_def_node, callee_def_env in mast.findall(
                            top_scope,
                            cpat,
                            outside=outside_patterns,
                            gen=True
                        ):
                            collect_matches(callee_def_node, memo=memo)
                            pass
                        pass
                    pass
                pass
            pass

        # Now that we've defined our collect_matches function, let's use it:
        try:
            collect_matches(scope)
        except Exception:
            logging.log(
                '>>> WARNING: check_ast_rule exception:\n'
              + html_tools.string_traceback()
              + '\n<<<'
            )
            logging.log(
                (
                    "Exception while performing ImplementationCheck:\n"
                    "(topic: '{}', patterns: {})"
                ).format(self.feedback_topic(), self.patterns)
            )
            self.result = {
                "status": "unknown",
                "traceback": html_tools.html_traceback(
                    linkable=context_utils.linkmap(context)
                ),
                "warnings": [
                    "There was an error while checking your implementation."
                ]
            }
            self.set_explanation(
                context,
                status="crash",
                default=html_tools.html_traceback(
                    title="Error while checking implementation:",
                    linkable=context_utils.linkmap(context)
                )
            )
            return self.result

        # Used for messaging in presence of subrules:
        unrefined_match_count = len(matches)

        # Refine matches by running subrules:
        partial_matches = []
        full_matches = []
        full_match_subtable = None
        partial_match_subtable = None
        closest_subtable = None
        closest_successes = -1
        closest_partials = -1
        for (node, envs) in matches:
            for env in envs:
                subsuccesses = 0
                subpartials = 0
                for rule in self.subrules:
                    this_sub_context = {}
                    this_sub_context.update(sub_context)
                    this_sub_context["scope"] = node
                    this_sub_context["env"] = env
                    # evaluate sub-rule
                    sub_result = rule.evaluate_in_context(this_sub_context)
                    if sub_result["status"] == "accomplished":
                        subsuccesses += 1
                    elif sub_result["status"] == "partial":
                        subpartials += 1

                # tally sub-results
                if subsuccesses == len(self.subrules):
                    # all succeeded: this is a full match
                    if full_match_subtable is None:
                        full_match_subtable = self.build_subtable()
                    for prev_node, prev_envs in full_matches:
                        if prev_node == node:
                            prev_envs.append(env)
                            break
                    else: # if we didn't break
                        full_matches.append((node, [env]))
                elif (
                    (subsuccesses + subpartials) == len(self.subrules)
                 or (
                        (subsuccesses + subpartials / 2)
                     >= (len(self.subrules) - self.subslip)
                    )
                ):
                    # partially succeeded
                    if partial_match_subtable is None:
                        partial_match_subtable = self.build_subtable()
                    for prev_node, prev_envs in partial_matches:
                        if prev_node == node:
                            prev_envs.append(env)
                            break
                    else: # if we didn't break
                        partial_matches.append((node, [env]))
                elif (
                    subsuccesses > closest_successes
                 or (
                      subsuccesses == closest_successes
                  and subpartials > closest_partials
                    )
                ):
                    # Best so far in terms of subrule successes
                    closest_successes = subsuccesses
                    closest_partials = subpartials
                    closest_subtable = self.build_subtable()

        # Get counts:
        full_match_identities = []
        for n, envs in full_matches:
            identity_or_identities = self.match_identity(top_scope, n, envs)
            if isinstance(identity_or_identities, list):
                full_match_identities.extend(identity_or_identities)
            else:
                full_match_identities.append(identity_or_identities)

        n_full_matches = len(set(full_match_identities))

        partial_match_identities = []
        for n, envs in partial_matches:
            identity_or_identities = self.match_identity(top_scope, n, envs)
            if isinstance(identity_or_identities, list):
                partial_match_identities.extend(identity_or_identities)
            else:
                partial_match_identities.append(identity_or_identities)

        n_partial_matches = len(set(partial_match_identities))

        # Check bounds now that we know which matches are partial/full:
        violated_min = (
            self.min_allowed is not None
        and self.min_allowed > n_full_matches
        )
        violated_max = (
            self.max_allowed is not None
        and self.max_allowed < n_full_matches
        )
        obeyed_min_partially = (
            self.min_allowed is None
         or self.min_allowed <= n_partial_matches
        )
        # You can't use partial matches to satisfy the max limit

        # Notes and warnings for our ultimate result:
        notes = []
        warnings = []

        # Assign status
        result_status = None
        if violated_min:
            if obeyed_min_partially:
                result_status = "partial"

            if self.softmin:
                if isinstance(self.softmin, (str, list, tuple)):
                    if "note" in self.softmin:
                        notes.append(
                            "Found fewer {} than expected.".format(
                                self.pl_name
                            )
                        )

                    if "warn" in self.softmin:
                        warnings.append(
                            "Found fewer {} than expected.".format(
                                self.pl_name
                            )
                        )

                    if "partial" in self.softmin:
                        result_status = "partial"

                    if "fail" in self.softmin:
                        result_status = "failed"

                elif isinstance(self.softmin, (int, float)):
                    matchpoints = n_full_matches + 0.5 * n_partial_matches
                    if matchpoints >= self.softmin:
                        result_status = "partial"
                    else:
                        result_status = "failed"
                else:
                    result_status = "partial"

            elif not obeyed_min_partially:
                result_status = "failed"

        if violated_max:
            if self.softmax:
                if isinstance(self.softmax, (str, list, tuple)):
                    if "note" in self.softmax:
                        notes.append(
                            f"Found more {self.pl_name} than expected."
                        )

                    if "warn" in self.softmax:
                        warnings.append(
                            f"Found more {self.pl_name} than expected."
                        )

                    if "partial" in self.softmax:
                        # Don't upgrade failed (e.g. due to softmax):
                        if result_status != "failed":
                            result_status = "partial"

                    if "fail" in self.softmax:
                        # old status is irrelevant
                        result_status = "failed"

                elif isinstance(self.softmax, (int, float)):
                    # partial matches don't count against max
                    if (
                        n_full_matches <= self.softmax
                    and result_status != "failed"
                    ):
                        result_status = "partial"
                    else:
                        result_status = "failed"
                elif self.softmax:
                    if result_status != "failed":
                        result_status = "partial"
            else:
                result_status = "failed"

        # No status assigned by min/max constraints? Then it's accomplished:
        if result_status is None:
            result_status = "accomplished"

        # Figure out line numbers for matches
        matching_lines = [
            mast.node_line(node)
            for node, envs in full_matches
        ]
        partial_lines = [
            mast.node_line(node)
            for node, envs in partial_matches
        ]
        arent_extra = [
            node for node, env in full_matches
        ] + [
            node for node, env in partial_matches
        ]
        non_matching_lines = [
            mast.node_line(node)
            for node, envs in matches
            if node not in arent_extra
        ]

        # Create explanation:
        plural = True
        if self.max_allowed == 0:
            quantity = "zero"
        elif self.min_allowed is None:
            if self.max_allowed is None:
                quantity = "any number of"
            else:
                quantity = "no more than {}".format(self.max_allowed)
                plural = self.max_allowed != 1
        else:
            if self.max_allowed is None:
                quantity = "at least {}".format(self.min_allowed)
                plural = self.min_allowed != 1
            elif self.min_allowed == self.max_allowed:
                quantity = "exactly {}".format(self.min_allowed)
                plural = self.max_allowed != 1
            else:
                quantity = "between {} and {}".format(
                    self.min_allowed,
                    self.max_allowed
                )
                plural = True

        extra_unrefined = (
            unrefined_match_count
          - len(full_matches)
          - len(partial_matches)
        )
        explanation = (
            "Expected {quantity} {name}, found {found}{sub}."
        ).format(
            quantity=quantity,
            name=self.pl_name if plural else self.name,
            found=(
                str(len(full_matches))
                if (
                    result_status == "accomplished" # partials are irrelevant
                 or len(partial_matches) == 0 # no partials
                 or self.max_allowed == 0 # partials are irrelevant
                )
                else
                "{} full and {} partial matches".format(
                    len(full_matches),
                    len(partial_matches)
                )
            ),
            sub=(
                " (found {} possible {} which did not satisfy {})"
            ).format(
                extra_unrefined,
                phrasing.plural(extra_unrefined, "match", "matches"),
                phrasing.plural(
                    len(self.subrules),
                    "the sub-rule",
                    f"all {len(self.subrules)} sub-rules"
                ),
            ) if self.subrules and extra_unrefined else ""
        )

        # Add line numbers:
        if len(matching_lines) > 0:
            notes.append(
                "Found on line(s): {}".format(
                    ', '.join(
                        html_tools.html_link_to_line(
                            task_info["id"],
                            filename,
                            ln
                        )
                        for ln in matching_lines
                    )
                )
            )
        if len(partial_lines) > 0 and result_status != "accomplished":
            notes.append(
                "Found partial matches on line(s): {}".format(
                    ', '.join(
                        html_tools.html_link_to_line(
                            task_info["id"],
                            filename,
                            ln
                        )
                        for ln in partial_lines
                    )
                )
            )
        if (
            self.subrules
        and extra_unrefined
        and result_status != "accomplished"
        ):
            notes.append(
                "Found disqualified matches on line(s): {}".format(
                    ", ".join(
                        html_tools.html_link_to_line(
                            task_info["id"],
                            filename,
                            ln
                        )
                        for ln in non_matching_lines
                    )
                )
            )

        if full_match_subtable is not None:
            subtable = full_match_subtable
        elif partial_match_subtable is not None:
            subtable = partial_match_subtable
        else:
            subtable = closest_subtable # might still be None in some cases

        self.result = {
            "status": result_status,
            "notes": notes,
            "warnings": warnings,
            "subtable": subtable
        }

        self.set_explanation(context, default=explanation)
        # TODO: Bubble warnings from sub-rules?
        return self.result


class NoParseErrors(Goal):
    """
    This goal is simply accomplished if there are no parsing errors
    during task loading, and failed otherwise. If generate_warnings is given it
    generates a warning for each parse error. The created goal will
    always use the identifier "syntax:no_parse_errors".
    """
    def __init__(
        self,
        taskid,
        description=(
            "No errors loading code",
            (
                "Your code should be able to be loaded without errors. Run "
              + "your code before submitting it to make sure this is true."
            )
        ),
        generate_warnings=True,
        **kwargs
    ):
        """
        A task ID is required. A default description is available. If
        generate_warnings is given as False, parse errors will not be
        turned into warnings, but in the default case, they will be.

        The goal identifier will be "syntax:no_parse_errors".
        """
        super().__init__(
            taskid,
            "misc:no_parse_errors",
            description,
            **kwargs
        )
        self.set_default_goal_type("procedure")
        self.generate_warnings = generate_warnings

    # subgoals is inherited (no subgoals)

    # table is inherited

    def evaluate_in_context(self, context=None):
        """
        Checks whether there were any parse errors.
        """
        context = context or {}
        if (
            "parse_errors" not in context
         or len(context["parse_errors"]) == 0
        ):
            self.result = { "status": "accomplished" }
            self.set_explanation(
                context,
                default="There weren't any parsing errors."
            )
            return self.result
        else:
            message = "There were errors during parsing."
            if not self.generate_warnings:
                # Incorporate errors into message directly:
                message += "<br>\n" + '<br>\n'.join(
                    html_tools.summarize_parse_error(e)
                    for e in context["parse_errors"]
                )

            self.result = { "status": "failed" }

            if self.generate_warnings:
                # Generate a warning for each error:
                self.result["warnings"] = [
                    html_tools.summarize_parse_error(e)
                    for e in context["parse_errors"]
                ]

            self.set_explanation(context, default=message)
            return self.result


#--------------------------#
# Specialized linter goals #
#--------------------------#

class LintCheck(Goal):
    """
    Runs a linter function against the auto-context for "scope". Inherit
    and override the `check` method with a function that accepts a
    context and returns a goal evaluation result to define your linter.
    """
    def check(self, context):
        """
        Not implemented; override to define specific linters.
        """
        raise NotImplementedError(
            "LintCheck is an abstract class that can't be used directly."
        )

    def __init__(
        self,
        taskid,
        identifier,
        description=(
            "BLANK LINT CHECK",
            "THIS GOAL HAS NOT BEEN DEFINED"
        ),
        goal_type="style",
        uses_slots=("scope",),
        **kwargs
    ):
        """
        In addition to a task ID, an identifier, and a description, a
        goal type may be supplied other than the default "style".
        "procedure" is the most likely alternative.

        The categorizer "link:" will be prepended to the identifier
        provided.

        The slots required should be given as uses_slots, and a relevant
        context will be selected or created as the testing context.

        Any extra arguments are passed through to the `Goal` constructor.
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
                    "Details of your code",
                    (
                        "The " + phrasing.comma_list(uses_slots)
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

        # Set up Goal stuff
        super().__init__(
            taskid,
            "lint:" + identifier,
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
                    f"Linter for {self.__class__.__name__} returned None!"
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
                    title="Error while inspecting your code.",
                    linkable=context_utils.linkmap(context)
                )
            )
            return self.result

        self.set_explanation(
            context,
            default=self.result["explanation"]
        )

        return self.result


class AllFunctionsHaveDocstrings(LintCheck):
    """
    A `LintCheck` which requires that all functions defined in the
    submitted module must have non-empty docstrings.
    """
    def __init__(self, taskid, exclude=None, **kwargs):
        """
        A task ID is required. A list of function names to ignore may be
        given as `exclude`. All other keyword arguments are passed to the
        `LintCheck` constructor. If no description is specified, a
        default description will be included.

        The identifier will be "docstrings".
        """
        self.exclude = exclude or []

        if "description" not in kwargs:
            kwargs["description"] = (
                "All functions are documented",
                (
                    "Each function you define must include a non-empty"
                  + " documentation string as the very first thing in"
                  + " the function."
                )
            )

        super().__init__(
            taskid,
            "docstrings",
            uses_slots=["docstrings", "defs"],
            **kwargs
        )

    def check(self, context):
        """
        Checks that none of the extracted docstrings are None or
        empty. Requires a context that has a "docstrings" slot.
        """
        docmap = context_utils.extract(context, "docstrings")
        empty_docstrings = []
        has_docstrings = []
        for fname in sorted(docmap):
            if fname not in self.exclude and docmap[fname] == '':
                empty_docstrings.append(fname)
            elif fname not in self.exclude:
                has_docstrings.append(fname)

        if empty_docstrings:
            if has_docstrings:
                return {
                    "status": "partial",
                    "explanation": (
                        "Some functions had docstrings but others"
                        " didn't. Functions missing docstrings:"
                        "<br>\n{}"
                    ).format(
                        '<br>\n'.join(
                            '<code>{}</code>'.format(fname)
                            for fname in empty_docstrings
                        )
                    )
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        "One or more functions were missing"
                        " docstrings or had empty docstrings:"
                        "<br>\n{}"
                    ).format(
                        '<br>\n'.join(
                            '<code>{}</code>'.format(fname)
                            for fname in empty_docstrings
                        )
                    )
                }
        else:
            return {
                "status": "accomplished",
                "explanation": (
                    "All required functions included docstrings."
                )
            }


class FunctionsArentNested(LintCheck):
    """
    A `LintCheck` which requires that no functions are defined inside
    other functions.
    """
    def __init__(self, taskid, exclude=None, **kwargs):
        """
        A task ID is required. A list of function names to exclude from
        the check may be provided. These functions will be ignored if
        they are nested, and functions nested inside them will not be
        flagged.

        The identifier will be "functions_arent_nested".
        """
        self.exclude = exclude or []

        if "description" not in kwargs:
            kwargs["description"] = (
                "Do not define functions inside of other functions",
                (
                    "None of your function definitions may be placed"
                    " inside of other function definitions."
                )
            )

        super().__init__(
            taskid,
            "functions_arent_nested",
            uses_slots=["docstrings"],
            goal_type="procedure",
            **kwargs
        )

    def check(self, context):
        """
        A linter function that checks a defs context to make sure
        that none of the definitions includes an interior def.
        """
        filename = context_utils.extract(context, "filename")
        defsmap = context_utils.extract(context, "defs")
        task_info = context_utils.extract(context, "task_info")

        has_nested = {}
        for name in defsmap:
            if name not in self.exclude:
                inners = defsmap[name].body
                for pat in patterns.ALL_DEF_PATTERNS:
                    for inner_statement in inners:
                        for (match, bindings) in mast.findall(
                            inner_statement,
                            pat
                        ):
                            if match.name not in self.exclude:
                                has_nested.setdefault(
                                    name,
                                    set()
                                ).add(match)

        if has_nested:
            all_defs = set(
                [name for name in defsmap if name not in self.exclude]
            )
            nested_defs = set()
            for outer in has_nested:
                nested_defs |= has_nested[outer]

            pct_nested = len(nested_defs) / len(all_defs)

            nested_msg = (
                "We found the following functions defined within"
              + " other functions:<br>\n<ul>"
              + "\n".join(
                    "<li>Within {} (on line {}):<br>{}</li>".format(
                        outer,
                        html_tools.html_link_to_line(
                            task_info["id"],
                            filename,
                            defsmap[outer].lineno
                        ),
                        "<br>\n".join(
                            "<code>{}</code> on line {}".format(
                                inner.name,
                                html_tools.html_link_to_line(
                                    task_info["id"],
                                    filename,
                                    inner.lineno
                                )
                            )
                            for inner in has_nested[outer]
                        )
                    )
                    for outer in has_nested
                )
            )

            if pct_nested < 0.5:
                return {
                    "status": "partial",
                    "explanation": (
                        "Some relevant definitions were found inside"
                        " other definitions. "
                    ) + nested_msg
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        "More than half of relevant definitions were"
                        " found within other definitions! "
                    ) + nested_msg
                }

            return {
                "status": "accomplished",
                "explanation": "No defs were found within other defs."
            }
        else:
            return {
                "status": "accomplished",
                "explanation": "No defs were found within other defs."
            }


class DoesntWasteFruit(LintCheck):
    """
    A `LintCheck` that makes sure that any fruitful function or method
    calls get stored in variables or used as part of expressions. A
    fruitful function or method is one of:

    1. Defined in the submission itself with an interior return node that
       has an expression associated with it, which isn't inside a nested
       definition.
    2. One of the functions named in the `extra` list of strings, or a
       method named in that list with a '.' at the start.

    This goal will fail if at least one function call to a fruitful
    function or method doesn't use the result, but will partially succeed
    if there's at least one that does use the result.
    """
    def __init__(self, taskid, exclude=None, extra=None, **kwargs):
        """
        A task ID is required. A list of strings specifying names of
        functions to exclude from this check may be given. The code in
        those functions won't be inspected for wasting fruit, but calls
        to those functions in other contexts will still be inspected if
        they're fruitful.

        A description tuple can be supplied but a reasonable default will be
        use if it isn't given.

        The identifier will be "doesnt_waste_fruit".
        """
        self.exclude = exclude or []
        self.extra = extra or []

        if "description" not in kwargs:
            kwargs["description"] = (
                (
                    "Do not ignore the results of any fruitful function"
                    " calls"
                ),
                (
                    "According to the \"Don't waste fruit\" principle,"
                    " every place you call a fruitful function"
                    " (built-in or custom) you must store the result in"
                    " a variable, or that function call must be part of"
                    " a larger expression that uses its return value."
                )
            )

        super().__init__(
            taskid,
            "doesnt_waste_fruit",
            uses_slots=["scope"],
            goal_type="procedure",
            **kwargs
        )

    def check(self, context):
        """
        Returns success if none of the fruitful function and/or method
        calls in the given AST tree has a result but fails to either
        store it in a variable or use it as part of a larger expression
        or statement.
        """
        filename = context_utils.extract(context, "filename")
        scope = context_utils.extract(context, "scope")
        task_info = context_utils.extract(context, "task_info")

        # Variables to accumulate results
        fruitful_defs = {}

        used_calls = set()
        unused_calls = set()

        # Maps from function names (or method names prefixed with '.') to
        # AST Call nodes for good calls (fruitful functions called in a
        # way that uses their result) and bad calls (fruitful functions
        # called as bare expressions).
        good_calls = {}
        bad_calls = {}

        # Gather fruitful definitions
        for pat in patterns.ALL_DEF_PATTERNS:
            for (matching_node, bindings) in mast.findall(scope, pat):
                if mast.find(
                    matching_node.body, # so we don't exclude this def itself
                    "return _",
                    outside=patterns.ALL_DEF_PATTERNS
                ):
                    fruitful_defs[matching_node.name] = matching_node

        # Search entire code for used/unused function or method calls:
        self.accumulate_function_and_method_calls(
            scope,
            used_calls,
            unused_calls,
            self.exclude
        )

        # Find bad unused calls to fruitful functions
        for call in unused_calls:
            # Get the name of the function we're calling
            if isinstance(call.func, ast.Name):
                # A direct function call
                fname = call.func.id
                mname = fname
            elif isinstance(call.func, ast.Attribute):
                # A method call
                fname = call.func.attr
                mname = '.' + fname
            else:
                # Too complex to analyze; skip this function call
                continue

            # Decide if this call is bad or not:
            if (
                mname in self.extra
             or fname in fruitful_defs
            ):
                bad_calls.setdefault(mname, []).append(call)

        # Find good used calls to fruitful functions
        for call in used_calls:
            # Get the name of the function we're calling
            if isinstance(call.func, ast.Name):
                # A direct function call
                fname = call.func.id
                mname = fname
            elif isinstance(call.func, ast.Attribute):
                # A method call
                fname = call.func.attr
                mname = '.' + fname
            else:
                # Too complex to analyze; skip this function call
                continue

            # Decide if this call is good or not:
            if (
                mname in self.extra
             or fname in fruitful_defs
            ):
                good_calls.setdefault(mname, []).append(call)

        # Report results
        if (len(bad_calls) > 0):
            bad_call_report = (
                "We found the following calls to fruitful functions"
              + " whose results were ignored:\n<ul>{}</ul>"
            ).format(
                "\n".join(
                    "<li><code>{}</code> on line(s) {}</li>".format(
                        fname,
                        ", ".join(
                            html_tools.html_link_to_line(
                                task_info["id"],
                                filename,
                                call.lineno
                            )
                            for call in bad_calls[fname]
                        )
                    )
                    for fname in bad_calls
                )
            )

            if len(good_calls) == 0:
                return {
                    "status": "failed",
                    "explanation": (
                        "Your code used fruitful functions but ignored"
                      + " their results. "
                    ) + bad_call_report
                }
            else:
                return {
                    "status": "partial",
                    "explanation": (
                        "Your code used some fruitful functions but"
                      + " ignored their results. "
                    ) + bad_call_report
                }
        else: # no bad calls!
            return {
                "status": "accomplished",
                "explanation": (
                    "All calls to fruitful functions in your code"
                  + " correctly made use of their results."
                )
            }

    def accumulate_function_and_method_calls(
        self,
        node,
        used,
        unused,
        exclude=[]
    ):
        """
        Recursively accumulates used and unused function and method
        calls. Ignores function calls where the function being called is
        the result of an expression that's not an ast.Name or an
        ast.Attribute.

        The 'used' and 'unused' parameters are treated as sets of AST
        nodes.

        The `exclude` parameter is optional and lists functions whose
        definitions won't be inspected.
        """
        # We won't process things which come up in recursion that aren't AST
        # nodes (like strings, None, etc.). Note that when we recurse we make
        # sure to recurse into the AST nodes within lists like bodies.
        if not isinstance(node, ast.AST):
            return

        # If this is a function call that hasn't already been marked as
        # unused, mark it as used
        if isinstance(node, ast.Call) and node not in unused:
            # Only add it if it's a simple call to a function or method
            if isinstance(node.func, (ast.Name, ast.Attribute)):
                used.add(node)

        # Don't recurse or process statements if we're the definition of
        # an excluded function
        if isinstance(node, ast.FunctionDef) and node.name in exclude:
            return

        # Gather places to look for calls that qualify as unused:
        statements = []
        if isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.ClassDef,
                ast.ExceptHandler,
                ast.With
            )
        ):
            # A node that has a body
            statements = node.body

        elif isinstance(node, (ast.If, ast.For, ast.While)):
            # We need to inspect both the body and the orelse
            statements = node.body + node.orelse

        elif isinstance(node, ast.Try):
            # Inspect body, finalbody, and orelse (handlers will be inspected
            # when recursing on them)
            statements = node.body + node.finalbody + node.orelse

        # No other AST nodes define blocks, so they can't give rise to unused
        # function/method calls.

        # Inspect the block-level statements for unused expressions
        # TODO: Should we negate this? ANY expression which isn't a function
        # call to a non-fruitful function is wasting a value when it appears
        # as a statement...
        for statement in statements:
            if (
                isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            ):
                call = statement.value
                if isinstance(call.func, ast.Name):
                    unused.add(call)
                elif isinstance(call.func, ast.Attribute):
                    unused.add(call)
                # else ignore this call; it's too complex

        # Recurse to accumulate results from inner nodes
        for field in node._fields:

            if not hasattr(node, field): # skip missing fields
                continue

            child = getattr(node, field)
            if isinstance(child, list): # recurse into each element
                for child_part in child:
                    self.accumulate_function_and_method_calls(
                        child_part,
                        used,
                        unused,
                        exclude
                    )
            else: # Just recurse into this item
                self.accumulate_function_and_method_calls(
                    child,
                    used,
                    unused,
                    exclude
                )


class DoesntWasteBoxes(LintCheck):
    """
    A `LintCheck` which looks for unused variables, excluding a list of
    strings (named functions won't be inspected at all and named
    variables won't be counted as unused). The given partial tolerance
    value controls how many unused variables must exist before the goal
    is failed instead of partially completed. Set it to 0 to force a
    strict binary accomplished/failed result.

    The special name '_' will always be permitted, as it explicitly
    hints that a value will not be used.

    An unused variable is defined as a variable which is set but never
    loaded, which we detect via ast.Name nodes and
    ast.FunctionDef/ast.Lambda arguments and the presence of Store vs.
    Load contexts. This goal will be happily accept load-before-store,
    but other parts of your rubric will probably notice the code crashing
    when run...

    Note that our handling of scopes is primitive: we recognize the
    global scope and function def scopes, but not all the nuances of
    other scopes.
    """
    def __init__(self, taskid, exclude=None, tolerance=2, **kwargs):
        """
        A task ID is required. A list of strings specifying names of
        functions and/or variables to exclude from this check may be
        given. Excluded functions won't have their code inspected, and
        excluded variables won't be checked.

        The identifier will be "doesnt_waste_boxes".

        A category other than the default 'core' may also be specified.

        A tolerance (resulting in partial instead of complete failure)
        other than the default of 2 may be specified.

        A custom description tuple may be supplied, but a default
        description will be added if a custom one isn't provided.
        """
        self.exclude = exclude
        self.partial_tolerance = tolerance

        if "description" not in kwargs:
            kwargs["description"] = (
                (
                    "Do not create any variables that you never make"
                    " use of"
                ),
                (
                    "According to the \"Don't waste boxes\" principle,"
                    " every time you create a variable (using"
                    " <code>=</code> or by defining a parameter for a"
                    " function) you must also later use that variable"
                    " as part of another expression. If you need to"
                    " create a variable that you won't use, it must"
                    " have the name <code>_</code>, but you should only"
                    " do this if absolutely necessary."
                )
            )

        super().__init__(
            taskid,
            "doesnt_waste_boxes",
            uses_slots=["scope"],
            goal_type="procedure",
            **kwargs
        )

    def check(self, context):
        """
        A checker function which requires that there are no unused
        variables in the given scope or in any particular function
        definition scope inside it (more complex scoping rules aren't
        attended to).
        """
        node = context_utils.extract(context, "scope")
        task_info = context_utils.extract(context, "task_info")
        filename = context_utils.extract(context, "filename")

        # Variable to track scopes (see gather_loads_and_stores)
        scopes = {}

        # Find all Name nodes plus arguments, noting which scope(s) they
        # are a part of.
        self.gather_loads_and_stores(node, scopes, exclude=self.exclude)

        # Report string and boolean for state
        report = "Found the following variables that were never used:\n<ol>\n"
        num_unused = 0

        # Check each scope to look for stores that don't have
        # corresponding loads and assemble our report:
        for scope in scopes:
            missing_loads = (
                set(scopes[scope].get('store', {}))
              - scopes[scope].get('load', set())
              - set(self.exclude)
              - { '_' } # single-underscore is valid for an unused result
            )

            if missing_loads:
                num_unused += len(missing_loads)
                if scope == ("__global__",):
                    scope_repr = "the global scope"
                else:
                    scope_repr = ' → '.join(
                        "<code>{}</code>".format(sc)
                        for sc in scope[1:]
                    )

                report += "<li>In {}, found:\n<ol>\n{}\n</ol></li>\n".format(
                    scope_repr,
                    "\n".join(
                        "<li>Variable <code>{}</code> on line(s) {}</li>\n"
                        .format(
                            var,
                            ", ".join(
                                html_tools.html_link_to_line(
                                    task_info["id"],
                                    filename,
                                    node.lineno
                                )
                                for node in scopes[scope]['store'][var]
                            )
                        )
                        for var in missing_loads
                    )
                )

        # Succeed or fail
        if num_unused > 0:
            if num_unused > self.partial_tolerance:
                status = "failed"
            else:
                status = "partial"

            return {
                "status": status,
                "explanation": (
                    "Your code created {} variables which it did not"
                  + " make use of:\n{}"
                ).format(num_unused, report)
            }
        else:
            return {
                "status": "accomplished",
                "explanation": (
                    "Your code did not create any variables which it did"
                  + " not make use of."
                )
            }

    def gather_loads_and_stores(
        self,
        node,
        result,
        current_scopes=("__global__",),
        exclude=[]
    ):
        """
        Recursively traverses an AST and makes note of each time a Name
        appears including its Load or Store context. Accumulates results
        into the 'result' dictionary, which has scope-name-tuples (e.g.,
        ("__global__",) or ("__global__", "foo", "<lambda at line 12 col
        8>")) as keys and values which are dictionaries with 'load' and
        'store' keys. The 'load' value is a set of variable names, while
        the 'store' value is a dictionary mapping variable names to lists
        of AST nodes.

        As it traverses the AST tree, the current_scopes tuple indicates
        which scope(s) we're inside of. We add loads to all parent scopes
        but stores just to the innermost scope. Note that we aren't
        really keeping track of shadowing properly, so a shadowed global
        variable would still think that it's referenced even if it's not
        (TODO: fix that!)
        """
        # We won't process non-AST items
        if not isinstance(node, ast.AST):
            return

        # Don't process if we're the definition of an excluded function
        if isinstance(node, ast.FunctionDef) and node.name in exclude:
            return

        # Process this node if it's a Name...
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                for i in range(1, len(current_scopes) + 1):
                    result.setdefault(current_scopes[:i], {})\
                        .setdefault('load', set())\
                            .add(node.id)
            elif isinstance(node.ctx, ast.Store):
                result.setdefault(current_scopes, {})\
                    .setdefault('store', {})\
                        .setdefault(node.id, [])\
                            .append(node)
            # Note: we don't track Del-context Name references

        # If this node is a FunctionDef, it creates a scope and we've also
        # got to add its arguments as stored variables.
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.Lambda):
            if isinstance(node, ast.FunctionDef):
                inner_scopes = current_scopes + (node.name,)
            else: # Lambdas create anonymous scopes
                scope_id = "<lambda at line {} col {}>".format(
                    node.lineno,
                    node.col_offset
                )
                inner_scopes = current_scopes = (scope_id,)

            for arg in (
                # Note: some relevant Python versions don't have posonlyargs
                (
                    getattr(node.args, "posonlyargs")
                    if hasattr(node.args, "posonlyargs")
                    else []
                )
              + node.args.args
              + node.args.kwonlyargs
              + ([node.args.vararg] if node.args.vararg else [])
              + ([node.args.kwarg] if node.args.kwarg else [])
            ):
                result.setdefault(inner_scopes, {})\
                    .setdefault('store', {})\
                        .setdefault(arg.arg, [])\
                            .append(node)
        else:
            # Otherwise, the inner scopes are the same as the current scopes
            inner_scopes = current_scopes

        # Recurse to accumulate results from inner nodes
        for field in node._fields:

            if not hasattr(node, field): # skip missing fields
                continue

            child = getattr(node, field)
            if isinstance(child, list): # recurse into each element
                for child_part in child:
                    self.gather_loads_and_stores(
                        child_part,
                        result,
                        inner_scopes,
                        exclude
                    )
            else: # Just recurse into this item
                self.gather_loads_and_stores(
                    child,
                    result,
                    inner_scopes,
                    exclude
                )
