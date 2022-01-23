"""
The `Context` class and related functions which form the backbone of the
testing process.

contexts.py

A `Context` represents a specific situation derived from
other contexts and ultimately submitted and/or solution code.
`potluck.rubrics.Goal` objects actually evaluate things, but they depend
on one or more contexts to provide material to be evaluated.

For example, a typical unit test consists of a
`potluck.rubrics.ComparisonTest` which runs a checker function on the
'value' and 'ref_value' context keys in a `Context` which is created by
running the function to test with particular arguments (it will run the
submitted function to generate a 'value' entry and the solution function
to generate a `ref_value` entry). This `Context` will in turn depend on
another `Context` which loads the submitted and solution modules so that
they are ready for testing, etc.

In general, `Context` objects will form a directed acyclic graph of
dependencies, and because they cache their results, duplicate work is
avoided. `Context` objects also have user-facing text to describe how
they are derived, as well as the ability to explain their results to the
user.

Although `Context` objects represent the abstract idea of a certain test
result, the actual value of that result is stored in a context
dictionary, which is created and cached by the `Context` and supplied to
`Goal` objects on-demand.
"""

import copy
import os
import time
import re
import sys
import io
import tempfile
import shutil

try:
    import optimism
    OPTIMISTIC = True
except Exception:
    OPTIMISTIC = False

from . import html_tools
from . import phrasing
from . import load
from . import patterns
from . import mast
from . import context_utils
from . import compare


#---------#
# Globals #
#---------#

RELEVANT_FILENAME = None
"""
A string (or None before it gets set) which holds the file name given to
the most recent instantiation of a `FileContext`, which is thus also
almost certainly the filename that will be used in any new contexts that
are created (unless hijinks have ensued).
"""

RELEVANT_TESTS_FILENAME = None
"""
Like `RELEVANT_FILENAME`, but for a tests file to be validated rather
than a submission file to be evaluated.
"""

VALUE_SIZE_LIMIT = 10000
"""
Limit (in terms of string length, not bytes) after which we truncate
large values that would be displayed by `build_context_value_displayer`.
"""


#----------------------------------------#
# Context class and associated functions #
#----------------------------------------#

def generic_context_displayer(context):
    """
    The default display_product function for a Context, this just returns
    the string "no details available." This may help cut down on report
    sizes where displaying all context values would include highlighted
    copies of the source code, etc.
    """
    return "no details available"


class Context:
    """
    Represents some kind of product of submitted code, like an
    AST tree, or produced output. Contexts can specialize each other, so
    for example a regular expression could be used to transform a context
    containing all output from a program into a context containing just a
    single line of output. Context objects organize context_builder
    functions into hierarchies, and manage caching of their results.

    A `Context` object also needs to know how to render its results into
    HTML to display to the user as part of the feedback process.

    A `Context` object, via its context_builder function, knows how to
    produce, on demand, a dictionary mapping context keys to values.
    The base context (and therefore all derived contexts) will always
    include the following `potluck.context_utils.BASE_CONTEXT_SLOTS`:

    - "task_info": A task info dictionary for the current task, which
        will have the following keys:
        - "id": The task ID.
        - "specification": the specification module for this task.
        - "target": The default file or folder to grade in a submission.
        - "title": The title of this task.
        - "desc": The short description of this task.
        - "reference_cache_file": The filename where reference values
            may be cached.
        - "ignore_cache": Whether or not to ignore the cache (might not
            be present; ignore cache only if present and truthy).
    - "username": The user who submitted the code we're evaluating.
    - "submission_root": The root directory within which the
        submission we're evaluating can be found.
    - "default_file": The official name of the default file to evaluate.
    - "actual_file": The actual name of the default file as submitted.
    - "tests_submission_root": The root directory where the test's we're
        validating can be found (present during validation).
    - "default_tests_file": The official name of the default tests file
        to validate.
    - "actual_tests_file": The actual name of the tests file as
        submitted.

    When a context is associated with a specific goal, the context
    dictionary will also always contain the following extra slots:

    - "goal_id": The unique-per-task identifier string for the goal that
        this context is associated with.
    - "which_context": The index of this context within the goal's
        testing contexts. Along with the task ID and goal ID, this can be
        used to build a unique identifier for the context.
        TODO: Context IDs?

    The typical slots of derived context dictionaries include:

    - "filename": The file name (without path) of the file we're
        evaluating.
    - "file_path": The full absolute path to the file we're evaluating.
    - "source": A string containing the source code of the submitted
        module.
    - "parse_errors": A list of Exception objects which were
        generated but ignored when parsing the submitted code.
    - "defs": A mapping from function names to AST nodes covering
        every `def` node in the submitted code (but note that
        functions with identical names will shadow each other in this
        map).
    - "scope": an AST node to check within (e.g., for a function
        definition check). See ImplementationCheck for an example of
        how these contexts are created and used.
    - "docstrings": A mapping from function names to documentation
        strings for those functions.
    - "top_scope": The top-level AST node for the submitted code.
    - "module": a loaded (submitted or solution) module
        (for a suite of tests that relies on the code).
    - "value": arbitrary Python value returned from a function call.
    - "output": a string containing output from tested code. This may be
        the full output, or may be filtered by additional Context objects
        to contain just part of the full output.
    - "trace": a trace list recording certain function calls made
        during a test, along with arbitrary state snapshots (see
        `potluck.harness.tracing_function_calls`).
    - "image": a Pillow Image object holding a captured image.
    - "audio": a dictionary with "mimetype", "data", and optionally
        "label" slots, holding captured audio data in binary form. The
        mimetype should indicate a MIME type for the data, while the
        "data" slot holds a bytes object containing the raw data in that
        format. The label slot holds a string used to label the audio in
        output to users.
    - "output_filename": the filename for an output file written to by
        testing code.
    - "output_file_contents": a string containing the contents of a file
        that was written to by tested code.
    - "expectations": a list of dictionaries defining expectations
        established using the `optimism` module (only present if that
        module is available) Each has the following keys:
        - "tag" A string indicating the file name and line number where
            this expectation was established
        - "case" The test case info. This is a dictionary with "result",
            "output", and "context" slots, holding the result value,
            printed output, and context details for a test case (see
            `optimism.get_my_context` for details of the "context"
            value).
        - "type" The type of expectation: "result", "output", or
            "custom".
        - "value" The expected value (or output fragment, or the checker
            function, depending on the expectation type).
    - Other keys not defined here may be established and/or used by
        certain Context or Goal classes.
    - Versions of the keys above with "ref_" as a prefix hold
        equivalent values derived from solution instead of submitted
        code.

    Note: For various reasons, the context building process creates
    shallow copies of contexts, not deep copies (the context values, such
    as modules, are often not deep-copyable). Accordingly, it is possible
    for changes to some sub-component of a context to be seen by other
    places where that context is being used, and thus YOU SHOULD NEVER
    MUTATE A CONTEXT VALUE. Context builder functions may safely
    synthesize new values based on old ones, and may freely update
    context keys with new values, but should not mutate the values under
    those keys.
    """
    def __init__(
        self,
        description=(
            "UNSPECIFIED TOPIC",
            "UNSPECIFIED DETAILS",
            "UNSPECIFIED FULL TOPIC",
            "UNSPECIFIED FULL DETAILS"
        ),
        builder=None,
        display_product=generic_context_displayer,
        depends=None,
        failure_explanation=None,
        cache_values=True,
        base=None,
        hidden=False,
        generate_warnings=False
    ):
        """
        You must supply a description pair (topic + details), triple
        (topic + details + feedback topic), or quad (topic + details +
        feedback topic + feedback details). Each item must be an HTML
        string to be displayed to the students as part of the rubric; the
        feedback versions if provided are used instead of the originals
        when generating a feedback document as opposed to a blank rubric.

        You must also supply a builder function, to be run when this
        context is required. If depends is supplied, it should be a list
        of Context objects, and before this context is established, each
        of those contexts will be created and merged in turn, to
        establish the prev_context argument to the builder function. The
        builder function must accept one argument (a context dictionary)
        and must return a dictionary of any new or modified keys that it
        wants to update in that context dictionary.

        You may supply a failure_explanation, which can be either a
        string, or a function that will be given the context in which the
        failure occurred and an Exception object (with an html_tb
        attached) and expected to return a string. This will be used to
        set the error message for a ContextCreationError thrown when the
        context_builder crashes, and that can ultimately become part of
        an explanation for a failed goal.

        If cache_values is given as False, the context_builder function
        will be re-run every time this context is requested, but by
        default, the result will be run only when one of our dependencies
        has a newer timestamp than our cached value.

        To supply seed values to bootstrap context creation, a Context
        may have a base value, which is used to start the
        dependency-merging process to provide a context for its builder.

        If hidden is given as True, this Context will not show up in the
        Contexts list, and will only be visible as a context associated
        with a goal when that goal is evaluated (use with care).

        If generate_warnings is set to True (default is False) then
        issues with context creation of this context (but not with
        creation of dependencies) will be logged as warnings in
        `list_and_render_contexts` output.
        """
        self.description = description
        if builder is None:
            raise ValueError(
                "Must specify a context builder when creating a Context."
            )
        self.builder = builder
        self.display_product = display_product
        self.depends = depends or []
        self.failure_explanation = failure_explanation
        self.cache_values = cache_values
        self.base = base or {}
        self.hidden = hidden
        self.generate_warnings = generate_warnings

        self.cached_value = None
        self.cache_timestamp = None

        self.working_from = None
        # which base context we're currently working from, for better
        # exception reporting

    def __str__(self):
        """
        Uses the first description entry to hint which context this is.
        """
        return 'Context "' + self.feedback_topic() + '"'

    def __repr__(self):
        """
        Weaves in the description.
        """
        return f'<{type(self).__name__} "{self.feedback_topic()}">'

    def __copy__(self):
        """
        Contexts may not be copied. They are entangled with each other,
        and we also don't want to create multiple copies which will
        duplicate the same work.
        """
        raise NotImplementedError("Contexts may not be copied.")

    def __deepcopy__(self, memo):
        """
        Contexts may not be copied (see __copy__).
        """
        raise NotImplementedError("Contexts may not be copied.")

    def changed_at(self):
        """
        Returns the timestamp of the most recent update to our cached
        context dictionary, so that contexts that depend on this one can
        know if they need to update themselves. May return None if no
        cached value has been created yet.
        """
        return self.cache_timestamp

    def clear_cache(self):
        """
        Removes cached info & resets cache timestamp.
        """
        self.cached_value = None
        self.cache_timestamp = None

    def burn_cache(self):
        """
        Clears our cache, and burns caches of our dependencies.
        """
        self.clear_cache()
        for dep in self.depends:
            dep.burn_cache()

    def create(self, base_context):
        """
        Creates and returns a context dictionary, using our builder
        function. If caching is enabled, a (shallow copy of a) cached
        value will be returned if we think that it was created after any
        changes in our dependencies.

        A base context is required, and should be a dictionary; normally
        it should have all the `potluck.context_utils.BASE_CONTEXT_SLOTS`
        already populated.

        The resulting context will have a special "__builder__" slot
        which contains a reference to this `Context` object. Of course,
        this slot will get overwritten by each context in a chain, so it
        only stores the last builder to touch the context (but see below).

        The resulting context will have a special "__unmerged__" slot
        which contains a list of context dictionaries for each dependency
        of this context, holding the context state created by just that
        dependency before merging with later dependencies. This can be
        used to retrieve separate values for the same slot from multiple
        dependencies, where only the last of those values would normally
        be retained. Those context dictionaries will of course have
        "__builder__" and "__unmerged__" slots, so the full chain of
        `Context` objects responsible for a given context can be
        recursively retrieved if necessary.
        """
        rerun = False
        if not self.cache_values:
            rerun = True
        else:
            # Check whether we even have a result yet:
            if self.cache_timestamp is None:
                rerun = True
            else:
                # Check timestamps of our dependencies
                for dep in self.depends:
                    when = dep.changed_at()
                    if when is None or when > self.cache_timestamp:
                        rerun = True
                        break

        if not rerun:
            # Return a shallow copy of our cached value
            result = copy.copy(base_context)
            result.update(self.cached_value)
            return result
        else:
            # Create new cached value and update our timestamp
            self.working_from = base_context
            prev_context = copy.copy(base_context)
            prev_context.update(self.base)
            unmerged = []
            for dep in self.depends:
                try:
                    dep_context = dep.create(base_context)
                    prev_context.update(dep_context)
                    unmerged.append(dep_context)
                except Exception as e:
                    e.html_tb = html_tools.html_traceback(
                        linkable=context_utils.linkmap(prev_context)
                    )
                    raise context_utils.ContextCreationError(
                        self,
                        "Dependency failed.",
                        e
                    )
            prev_context["__unmerged__"] = unmerged
            prev_context["__builder__"] = self

            try:
                our_results = self.builder(prev_context)
                prev_context.update(our_results)
                self.cached_value = prev_context
            except Exception as e:
                e.html_tb = html_tools.html_traceback(
                    linkable=context_utils.linkmap(prev_context)
                )
                if isinstance(self.failure_explanation, str):
                    msg = self.failure_explanation
                elif self.failure_explanation:
                    msg = self.failure_explanation(prev_context, e)
                else:
                    msg = "Test setup failed."
                raise context_utils.ContextCreationError(self, msg, e)
            self.cache_timestamp = time.time()
            # Return shallow copy of cached value
            result = {}
            result.update(self.cached_value)
            return result

    def deps_are_a_stick(self):
        """
        Returns true if the transitive dependencies of this context form
        a stick, not a real tree (i.e., each context, including this one,
        has exactly 1 or 0 dependencies).
        """
        return (
            len(self.depends) in (0, 1)
        and all(dep.deps_are_a_stick for dep in self.depends)
        )

    def rubric_topic(self):
        """
        Gets the rubric version of this Context's topic.
        """
        return self.description[0]

    def rubric_details(self):
        """
        Gets the rubric version of this Context's details.
        """
        return self.description[1]

    def feedback_topic(self):
        """
        Gets the feedback version of this Context's topic, or just the
        normal topic if there is no feedback version.
        """
        return self.description[::2][-1]

    def feedback_details(self):
        """
        Gets the feedback version of this Context's details, or just the
        normal details if there is no feedback version.
        """
        return self.description[1::2][-1]

    def html_topic(self, in_feedback=False):
        """
        Returns an HTML string representing just this context object as a
        div.topic, without including information about dependencies. If
        in_feedback is given as True, the feedback version of the topic
        and details is shown instead of the normal (rubric) version.

        Details are included behind a help button.
        """
        if in_feedback:
            topic = self.feedback_topic()
            details = self.feedback_details()
        else:
            topic = self.rubric_topic()
            details = self.rubric_details()
        return '<div class="topic">{}</div>'.format(
            topic + ' ' + html_tools.create_help_button(details)
        )

    def html_context_tree(self, in_feedback=False):
        """
        Produces an HTML string which shows this context and those that
        it depends on in a tree structure, with dependencies nested
        inside the contexts that depend on them. In the special case of a
        stick, a different format is used.

        If in_feedback is given as true, the feedback topic and details
        values from the description are used if present, instead of the
        normal (rubric) topic and details.
        """
        if self.deps_are_a_stick():
            if self.depends:
                dep_chain = (
                    '(depends on <div class="context_depends">{}</div>)'
                ).format(
                    self.depends[0].html_context_tree(in_feedback)
                    # there is only one
                )
                return (
                    '<details class="context">\n<summary>{}</summary>\n'
                  + '{}\n</details>'
                ).format(
                    self.html_topic(in_feedback),
                    dep_chain
                )
            else:
                return '<div class="context">\n{}\n</div>'.format(
                    self.html_topic(in_feedback)
                )
        else:
            # Dependencies are a tree...
            dep_entries = '<br>\n'.join(
                dep.html_context_tree(in_feedback)
                for dep in self.depends
            )
            depends_full = (
                '<div class="context_depends">\n'
              + 'Depends on:<br>\n'
              + '{}\n'
              + '</div>'
            ).format(dep_entries) if self.depends else ''
            return (
                '<details class="context">\n<summary>{}</summary>\n'
              + '{}\n</details>'
            ).format(
                self.html_topic(in_feedback),
                depends_full
            )

    def html_representation(self, base_context):
        """
        Builds an HTML representation of this context's result using the
        display_product function. A base context is required because
        create is used to fetch the current value (or build a new one).

        If context creation fails, the result will be a string describing
        the error.
        """
        try:
            return self.display_product(self.create(base_context))
        except context_utils.ContextCreationError as e:
            tb = html_tools.html_traceback(e)
            return f"""\
<div class="context_error">
  <h3>An error was encountered while attempting to run this test.</h3>
{tb}
</div>
"""

    def warnings(self, base_context):
        """
        Returns a list of HTML strings representing warnings generated by
        this context (excluding warnings generated by contexts this one
        depends on). A base context is required because we need to
        generate the context value to see if there are warnings, although
        a cached value will be used in most cases. Returns an empty list
        when no warnings have been generated.
        """
        try:
            ctx = self.create(base_context)
            return ctx.get("warnings", [])
        except context_utils.ContextCreationError as e:
            if isinstance(e.cause, context_utils.ContextCreationError):
                # Error comes from a dependency, not directly from this
                # context, so report nothing to avoid duplicating
                # warnings
                return []
            else:
                # Error comes from this context, so report it
                tb = html_tools.html_traceback(e)
                return [ f"Error during context creation:<br>{tb}" ]


def add_context_numbering(all_context_objs):
    """
    Takes a list of Context objects and looks for objects with duplicated
    short descriptions, adding numerical suffixes to these.
    """
    # Map topics to lists of contexts
    by_topic = {}
    by_feedback_topic = {}
    for ctx in all_context_objs:
        topic = ctx.description[0]
        by_topic.setdefault(topic, []).append(ctx)

        if len(ctx.description) > 2:
            by_feedback_topic.setdefault(ctx.description[2], []).append(ctx)

    # Assign numbers to topics that are duplicated
    for topic in by_topic:
        contexts = by_topic[topic]
        if len(contexts) > 1:
            # these duplicates need numbering
            for i, ctx in enumerate(contexts):
                ctx.description = (
                    ctx.description[0] + f" #{i+1}",
                ) + ctx.description[1:]

    # Repeat for feedback topics (numbering will hopefully be consistent
    # because of consistent iteration order over all context objects, but
    # if it's not, too bad.
    for topic in by_feedback_topic:
        contexts = by_feedback_topic[topic]
        if len(contexts) > 1:
            # these duplicates need numbering
            for i, ctx in enumerate(contexts):
                ctx.description = ctx.description[:2] + (
                    ctx.description[2] + f" #{i+1}",
                ) + ctx.description[3:]


def build_context_graph(all_context_objs):
    """
    Takes a list of Context objects and traces dependencies to build a
    top-down rather than bottom-up graph. The graph consists of a list of
    top-level node dictionaries with the following keys:

    - context: The Context object for this node.
    - children: A list containing pointers to the node dictionaries of
        each Context that depends on this one.
    - parents: A list containing pointers to the node dictionaries of
        each Context that this one depends on.
    - level: An integer indicating the longest chain of ancestors that
        this node has (0 for nodes without dependencies).

    The exact same node dictionary may appear as a child and/or parent of
    multiple other nodes.

    The ordering of children will be the same as the ordering of context
    dependencies, while the ordering of the top-level nodes will match
    the order that they occur within the given all_context_objs list.
    """

    dict_cache = {}

    def dict_for(cobj):
        """
        Returns the dictionary for the given Context object, either by
        creating it or remembering one already constructed during the
        current construction process. For new encounters, the children
        value will be an empty list.
        """
        nonlocal dict_cache
        if id(cobj) in dict_cache:
            return dict_cache[id(cobj)]
        else:
            result = { "context": cobj, "children": [], "parents": [] }
            dict_cache[id(cobj)] = result
            return result

    nodeps = []
    for ctx in all_context_objs:
        d = dict_for(ctx)
        if ctx.depends:
            for dep in ctx.depends:
                pd = dict_for(dep)
                pd["children"].append(d)
                d["parents"].append(pd)
        else:
            nodeps.append(d)

    # Loop again and assign "level" values now that the graph is complete
    for ctx in all_context_objs:
        d = dict_for(ctx)
        assign_cgraph_level(d)

    return nodeps


def assign_cgraph_level(node):
    """
    Determines the level of a node in a contexts graph, which is 0 for
    nodes without parents, and one plus the highest parent level for all
    other nodes.

    Store this value in the "level" slot of the node, and does the same
    for any ancestor nodes encountered.

    Returns an already-computed level if there is one, or else returns
    the level value that it assigns to the node.
    """
    if "level" in node:
        return node["level"]
    else:
        if len(node["parents"]) == 0:
            node["level"] = 0
        else:
            mp = 0
            for pn in node["parents"]:
                pl = assign_cgraph_level(pn)
                if pl > mp:
                    mp = pl
            node["level"] = mp + 1

        return node["level"]


def render_context_graph(cgraph, in_feedback=False):
    """
    Renders a context graph (see `build_context_graph`) into HTML. Uses a
    simple algorithm which includes duplicate entries for nodes with
    multiple dependencies.

    The in_feedback argument controls whether context items should show
    their full or redacted versions.
    """
    result = '<ol class="context_list">'
    for cnode in cgraph:
        result += '\n<li>{}</li>'.format(
            html_tools.build_html_details(
                cnode["context"].html_topic(in_feedback),
                render_context_graph(cnode["children"], in_feedback)
            )
            if cnode.get("children")
            else cnode["context"].html_topic(in_feedback)
        )

    result += '\n</ol>' # close .context_list ol
    return result


def list_and_render_contexts(cgraph, base_context=None):
    """
    Transforms a context graph (see `build_context_graph`) into a list of
    context summaries, which are dictionaries with the following keys:

    - description: An HTML code string that describes the context item,
        including a detailed description behind a help button.
    - depends: A list containing integer indices into the entire context
        list of the other contexts on which this context depends. Will be
        empty for contexts without dependencies.
    - level: An integer specifying how far this context should be
        indented, which will be one greater than the maximum level of
        contexts that this one depends on, starting with 0 for contexts
        that have no dependencies.
    - value: An HTML code string that displays or summarizes the value
        produced by this context. This will be the result of the
        context's display_product function run on the most recent result
        of that context (or on a fresh result if caching is disabled for
        the context). There may be a description of a context creation
        error here if there is an error building the context value.
    - warnings: A list of strings indicating context-based rather than
        test-based warnings. In general contexts should only create
        warnings in very specific circumstances, since tests are
        responsible for most warnings, and might want to ignore issues
        that a context could warn about.

    The base_context argument is used to generate context results (will
    only happen if cached results are not available or caching is
    disabled for one or more contexts). If omitted or specified
    explicitly as None, the result will have empty strings in each
    "value" slot, and the descriptions will use redacted topic and
    detail values; use this when generating a list for a rubric rather
    than for a feedback document.

    The contexts in the list will be ordered such that every context
    comes later in the list than all contexts it depends on.
    """
    result = []

    # Produce a flat list of nodes in an order that respects
    # dependencies.
    nodeslist = []

    # Processing queue and processed set
    queue = cgraph[:] # place all top-level nodes in queue to start
    processed = set()

    while len(queue) > 0:
        this = queue.pop(0)

        depends = this["parents"]
        if any(id(dep) not in processed for dep in depends):
            continue
            # we'll come back to this node later when its next
            # unprocessed dependency queues it up
        else: # no unprocessed dependencies
            processed.add(id(this))
            nodeslist.append(this)
            for child in reversed(this["children"]):
                # Insert children at the front of the queue, doing so in
                # reverse order so they end up in their natural order at
                # the front
                if id(child) not in processed: # should always be true?
                    queue.insert(0, child)
                else:
                    raise NotImplementedError(
                        f"Unexpectedly encountered pre-processed child."
                        f"\n  Parent is '{this['context'].html_topic()}'"
                        f"\n  Child is '{child['context'].html_topic()}'"
                    )

    # A mapping from node IDs to their indices in the nodeslist
    indexmap = {
        id(cnode): idx
        for idx, cnode in enumerate(nodeslist)
    }

    # Iterate over all nodes in order
    for cnode in nodeslist:
        ctx = cnode["context"]
        result.append(
            {
                "description": ctx.html_topic(
                    base_context is not None
                ),
                "depends": [
                    indexmap[id(child)]
                    for child in cnode["children"]
                ],
                "level": cnode["level"],
                "value": (
                    ctx.html_representation(base_context)
                    if base_context is not None
                    else ""
                ),
                "warnings": (
                    ctx.warnings(base_context)
                    if base_context is not None and ctx.generate_warnings
                    else []
                )
            }
        )

    return result


#-----------------------------#
# Automatic Context Mechanism #
#-----------------------------#

class AutoContext(Context):
    """
    A `AutoContext` provides a way to automatically create dependencies
    on common contexts without saving them in variables that have to get
    passed around everywhere. When a `AutoContext` is created, it
    registers itself as the current provider for certain context slots,
    overwriting any previously-registered provider for those slots.
    Then, another context may use the `auto` function to create a list
    of `Context` objects to use as dependencies based on the slots it
    needs; this list will be populated with the set of
    most-recently-registered `AutoContext` objects for each slot
    requested.

    In addition to inheriting from `AutoContext`, `Context`s which
    should be automatic must call their own `register` method and
    provide it with one or more slot name strings as arguments.
    """
    _registry = {}
    _on_demand = {}

    def reset(relevant_filename=None, relevant_tests_filename=None):
        """
        This is a class method which resets the automatic contexts
        registry, erasing all registered `Context` objects. Used prior
        to loading a new task spec.

        Note that this does not reset the on-demand factory functions
        registry.

        A `relevant_filename` may be provided to set the global
        RELEVANT_FILENAME variable; setting this to the default filename
        for the task we're about to load is helpful since it prevents the
        spec from treating things created after an explicit-default file
        context as different from things created before any file contexts
        have been declared. If no `relevant_filename` is provided, the
        global will be set back to its default of None.

        A `relevant_tests_filename` may be provided and follows the same
        logic as `relevant_filename`.
        """
        global RELEVANT_FILENAME, RELEVANT_TESTS_FILENAME
        RELEVANT_FILENAME = relevant_filename
        RELEVANT_TESTS_FILENAME = relevant_tests_filename
        AutoContext._registry = {}

    def on_demand(factory, *slots):
        """
        This class method registers a given factory function as the
        on-demand provider of one or more slots.

        The factory function must be able to run with no arguments and
        must produce a `Context` object which can create the requested
        slot(s).

        Essentially, if `auto` is used to request an automatic context
        for a slot, but no such context has been registered, an
        on-demand factory function may be called to construct such a
        context automatically in some simple cases. Calling this
        function a second time re-using an old slot value will overwrite
        the factory function for that slot.
        """
        for slot in slots:
            AutoContext._on_demand[slot] = factory

    def register(self, *slots):
        """
        Registers this auto context as the current provider for one or
        more slots (named using strings). Subsequent calls to `auto`
        that include one or more of those slots will include this object
        in the resulting list.

        The slots for which a context registers itself are stored in the
        context's `_provides` attribute.
        """
        for slot in slots:
            AutoContext._registry[slot] = self

        self._provides = slots

    def refresh(self):
        """
        Any `AutoContext` may call this method to re-register itself as
        the current provider of all of its relevant slots. The slots to
        register under are remembered from the initial call to
        `register`.
        """
        self.register(*self._provides)


def auto(*slots):
    """
    This function returns a list of `Context` objects, suitable for use
    as all or part of a `depends` value for the creation of a new
    `Context`, and/or as all or part of a `test_in` value for the
    creation of a new `potluck.rubrics.Goal`. It does this by looking for
    the most recent `AutoContext` objects that have registered themselves
    as providers of the given slot or slots (these are just strings).

    If no `AutoContext` has registered itself for a given slot, but
    there is an on-demand factory registered for that slot, the factory
    function will be called to generate a `Context` to use as a
    dependency (which should also end up registering the resulting
    `Context` under the appropriate slot(s)).

    If multiple slots are given and one `Context` is registered under
    several of them, that `Context` will only appear in the resulting
    list once. Likewise, if an on-demand factory function creates a
    `Context` which registers itself for several slots, and one or more
    other slots in that list are also being requested, the factory
    function will not be re-run for the subsequent slots, and the
    resulting `Context` will only appear in the result list once.

    If no slots are given, this function returns an empty list.

    If a slot is requested for which there is no currently-registered
    `AutoContext` and for which there is no registered on-demand
    `Context` factory, an `ContextError` will be raised.
    """
    result = []
    for slot in slots:
        if slot in AutoContext._registry:
            match = AutoContext._registry[slot]
            if match not in result:
                result.append(match)
        elif slot in AutoContext._on_demand:
            created = AutoContext._on_demand[slot]()
            if created not in result:
                result.append(created)
        else:
            raise context_utils.ContextError(
                f"Automatic context request for slot '{slot}' could not"
                f" be fulfilled because no AutoContext was registered"
                f" for that slot, and no on-demand Context factory"
                f" function was available for that slot either."
            )

    return result


#-------------------------#
# Derived Context classes #
#-------------------------#


class FileContext(AutoContext):
    """
    Establishes a 'filename' context slot that holds the name of a
    specific file being evaluated. By default, the created `Context` has
    no dependencies and is hidden.

    The filename provided should be relative to the submission root,
    which is either the directory where the target file exists, or the
    target directory for multi-file submissions. If no target file is
    identified, the default_file context slot value is used to target
    the submission's default file.

    Establishes 'ref_*' slots for each normal slot it establishes.
    """
    def __init__(self, target_file=None, depends=None, hidden=True):
        """
        A target_file string specifies the path to the target file that
        this context will focus evaluation on, relative to the
        submission root. If not provided, the "default_file" context
        slot value will be used.

        Both 'filename' and 'file_path' context slots will be
        established by this builder; the former holds just the file (or
        directory) name of the target file, while the latter holds a
        full path to the file.

        It's up to other `Context`s to make use of the slots established
        by this one.
        """
        global RELEVANT_FILENAME
        # Set the relevant filename global, or fetch it
        if target_file is not None:
            RELEVANT_FILENAME = target_file
        elif RELEVANT_FILENAME is not None:
            target_file = RELEVANT_FILENAME

        self.target_file = target_file

        # First, create our context-builder function for this instance
        def establish_context(prev_context):
            """
            Establishes 'filename' and 'file_path' slots based on the
            target_file value given to the `FileContext` that this is
            the context builder function for. Also establishes
            'ref_filename' and 'ref_file_path' slots pointing to the
            equivalent file in the solution code.
            """
            task_info = context_utils.extract(prev_context, "task_info")
            soln_root = task_info["specification"].soln_path
            submission_root = context_utils.extract(
                prev_context,
                "submission_root"
            )
            # Revise our description when we build our context if we're
            # forced to fetch the default file:
            file_target = self.target_file
            default_filename = context_utils.extract(
                prev_context,
                "default_file"
            )
            if file_target is None:
                file_target = default_filename
                self.description = (
                    f"File '{file_target}'",
                    f"We will evaluate your submitted file '{file_target}'.",
                )
            if file_target == default_filename:
                actual_filename = context_utils.extract(
                    prev_context,
                    "actual_file"
                )
                full_target = os.path.join(
                    submission_root,
                    actual_filename
                )
                # Even if we're grading a custom-named file, the solution
                # won't have a custom name...
                ref_target = os.path.abspath(
                    os.path.join(soln_root, default_filename)
                )
                target_filename = default_filename
            else:
                # TODO: How can we properly handle ref targets for
                # custom-named files here?
                full_target = os.path.join(submission_root, file_target)
                ref_target = os.path.abspath(
                    os.path.join(soln_root, file_target)
                )
                _, target_filename = os.path.split(full_target)

            if not os.path.exists(submission_root):
                # If the submission root directory is missing...
                raise context_utils.ContextCreationError(
                    self,
                    (
                        f"Submission root directory"
                        f" '{submission_root}' does not exist."
                    )
                )
            elif not os.path.exists(full_target):
                # If the target file is missing
                raise context_utils.ContextCreationError(
                    self,
                    (
                        f"Target submission file"
                        f" '{full_target}' does not exist."
                    )
                )
            elif not os.path.exists(ref_target):
                # If there is no equivalent solution file
                raise context_utils.ContextCreationError(
                    self,
                    f"No solution file '{ref_target}' is available."
                )
            # else both submission root and full target exist

            return {
                "filename": target_filename,
                "file_path": os.path.abspath(full_target),
                "ref_filename": target_filename,
                "ref_file_path": os.path.abspath(ref_target)
            }

        # Now we can call the super-class init with the context builder
        # function we just created.
        super().__init__(
            description=(
                f"File '{target_file}'",
                f"We will evaluate your submitted file '{target_file}'."
            ),
            builder=establish_context,
            display_product=lambda context: (
                f"Evaluating '{context['filename']}'"
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, we can register ourselves as an auto-context for the
        # "filename" and "file_path" slots.
        self.register(
            "filename",
            "file_path",
            "ref_filename",
            "ref_file_path"
        )


# Register a factory for a default FileContext as an on-demand option
# for "filename", "file_path", and the associated ref_ slots:
AutoContext.on_demand(
    (lambda: FileContext()),
    "filename", "file_path", "ref_filename", "ref_file_path"
)


class TestsFileContext(AutoContext):
    """
    Establishes a 'tests_filename' context slot that holds the name of a
    specific tests file being validated. By default, the created
    `Context` has no dependencies and is hidden.

    The filename provided should be relative to the submission root,
    which is either the directory where the target tests file exists, or
    the target directory for multi-file submissions. If no target file is
    identified, the "default_tests_file" context slot value is used to
    target the submission's default tests file.

    Establishes 'ref_*' slots for each normal slot it establishes.
    """
    def __init__(self, target_tests_file=None, depends=None, hidden=True):
        """
        A target_tests_file string specifies the path to the target tests
        file that this context will focus validation on, relative to the
        submission root. If not provided, the "default_tests_file"
        context slot value will be used.

        Both 'tests_filename' and 'tests_file_path' context slots will be
        established by this builder; the former holds just the file (or
        directory) name of the target tests file, while the latter holds
        a full path to the file.

        It's up to other `Context`s to make use of the slots established
        by this one.
        """
        global RELEVANT_TESTS_FILENAME
        # Set the relevant filename global, or fetch it
        if target_tests_file is not None:
            RELEVANT_TESTS_FILENAME = target_tests_file
        elif RELEVANT_TESTS_FILENAME is not None:
            target_tests_file = RELEVANT_TESTS_FILENAME

        self.target_tests_file = target_tests_file

        # First, create our context-builder function for this instance
        def establish_context(prev_context):
            """
            Establishes 'tests_filename' and 'tests_file_path' slots
            based on the target_tests_file value given to the
            `FileContext` that this is the context builder function for.
            Also establishes 'ref_tests_filename' and
            'ref_tests_file_path' slots pointing to the equivalent file
            in the solution code.
            """
            task_info = context_utils.extract(prev_context, "task_info")
            soln_root = task_info["specification"].soln_path
            submission_root = context_utils.extract(
                prev_context,
                "tests_submission_root"
            )
            # Revise our description when we build our context if we're
            # forced to fetch the default file:
            file_target = self.target_tests_file
            default_filename = context_utils.extract(
                prev_context,
                "default_tests_file"
            )
            if file_target is None:
                file_target = default_filename
                self.description = (
                    f"Tests file '{file_target}'",
                    (
                        f"We will validate your submitted tests file"
                        f"'{file_target}'."
                    )
                )
            if file_target == default_filename:
                actual_filename = context_utils.extract(
                    prev_context,
                    "actual_tests_file"
                )
                full_target = os.path.join(
                    submission_root,
                    actual_filename
                )
                # Even if we're grading a custom-named file, the solution
                # won't have a custom name...
                ref_target = os.path.abspath(
                    os.path.join(soln_root, default_filename)
                )
                target_filename = default_filename
            else:
                # TODO: How can we properly handle ref targets for
                # custom-named files here?
                full_target = os.path.join(submission_root, file_target)
                ref_target = os.path.abspath(
                    os.path.join(soln_root, file_target)
                )
                _, target_filename = os.path.split(full_target)

            if not os.path.exists(submission_root):
                # If the submission root directory is missing...
                raise context_utils.ContextCreationError(
                    self,
                    (
                        f"Tests submission root directory"
                        f" '{submission_root}' does not exist."
                    )
                )
            elif not os.path.exists(full_target):
                # If the target file is missing
                raise context_utils.ContextCreationError(
                    self,
                    (
                        f"Target tests submission file"
                        f" '{full_target}' does not exist."
                    )
                )
            elif not os.path.exists(ref_target):
                # If there is no equivalent solution file
                raise context_utils.ContextCreationError(
                    self,
                    (
                        f"No solution tests file '{ref_target}' is"
                        f" available."
                    )
                )
            # else both submission root and full target exist

            return {
                "tests_filename": target_filename,
                "tests_file_path": os.path.abspath(full_target),
                "ref_tests_filename": target_filename,
                "ref_tests_file_path": os.path.abspath(ref_target)
            }

        # Now we can call the super-class init with the context builder
        # function we just created.
        super().__init__(
            description=(
                f"Tests file '{target_tests_file}'",
                (
                    f"We will validate your submitted tests file"
                    f" '{target_tests_file}'."
                )
            ),
            builder=establish_context,
            display_product=lambda context: (
                f"Validating '{context['tests_filename']}'"
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, we can register ourselves as an auto-context for the
        # "filename" and "file_path" slots.
        self.register(
            "tests_filename",
            "tests_file_path",
            "ref_tests_filename",
            "ref_tests_file_path"
        )


# Register a factory for a default TestsFileContext as an on-demand
# option for "tests_filename", "tests_file_path", and the associated ref_
# slots:
AutoContext.on_demand(
    (lambda: TestsFileContext()),
    "tests_filename", "tests_file_path", "ref_tests_filename",
    "ref_tests_file_path"
)


class SandboxContext(AutoContext):
    """
    Establishes two sandbox directories to be used for running all code
    being tested, including the initial loading of the module itself. One
    directory is for the submitted code and a second is for the solution
    code.
    """
    def __init__(self, depends=None, hidden=True):
        """
        Creates a context which establishes two new unique sandbox
        directories. The context creation function places the full paths
        to those directories in the "sandbox" and "ref_sandbox" context
        slots. A list of dependencies may be provided, and hidden can be
        set to False if desired.
        """
        self.dir = None
        self.ref_dir = None
        # TODO: Clean up these temporary directories rather than letting
        # Python do that on shutdown...

        def establish_context(prev_context):
            """
            Creates a new temporary directory and puts its absolute path
            in the "sandbox" context slot. Creates a second temporary
            directory and puts its path in the "ref_sandbox" slot.
            Copies helper files into both directories, and copies the
            actual solution file(s) into the reference sandbox.
            """
            sub_root = context_utils.extract(prev_context, "submission_root")
            sub_file = context_utils.extract(prev_context, "actual_file")
            tinfo = context_utils.extract(prev_context, "task_info")
            spec = tinfo["specification"]

            self.dir = tempfile.TemporaryDirectory(
                suffix="__tmp",
                dir=load.SANDBOX_DIR
            )
            self.ref_dir = tempfile.TemporaryDirectory(
                suffix="__ref_tmp",
                dir=load.SANDBOX_DIR
            )

            # Set up the sandboxes
            for sb in [self.dir, self.ref_dir]:
                # Copy helper files into the sandbox if there are any
                # Note that we don't use symlinks here, because we don't
                # want destructive student code to modify files outside
                # the sandbox...
                # TODO: Use symlinks in places where we feel safe,
                # especially for large starter files!!!
                helpers = context_utils.sandbox_filemap(spec)
                if helpers is not None:
                    for filepath in helpers:
                        to = os.path.join(sb.name, helpers[filepath])
                        if os.path.isdir(filepath):
                            shutil.copytree(filepath, to)
                        else:
                            shutil.copy(filepath, to)

            # Copy the submitted target file/directory into the sandbox
            subm_target = os.path.join(sub_root, sub_file)
            sandbox_target = os.path.join(self.dir.name, tinfo["target"])
            if os.path.isdir(subm_target):
                shutil.copytree(subm_target, sandbox_target)
            else:
                shutil.copy(subm_target, sandbox_target)

            # Copy the target file/directory from the solution dir into
            # the ref sandbox
            soln_target = os.path.join(spec.soln_path, tinfo["target"])
            sandbox_target = os.path.join(self.ref_dir.name, tinfo["target"])
            if os.path.isdir(soln_target):
                shutil.copytree(soln_target, sandbox_target)
            else:
                shutil.copy(soln_target, sandbox_target)

            return {
                "sandbox": os.path.abspath(self.dir.name),
                "ref_sandbox": os.path.abspath(self.ref_dir.name)
            }

        # Now we can call the super-class init with the context builder
        # function we just created.
        super().__init__(
            description=(
                "Sandbox directories",
                (
                    "We will create sandbox directories for running"
                    " your submitted code and the solution code."
                )
            ),
            builder=establish_context,
            display_product=lambda context: (
                "Running in a sandbox"
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, we can register ourselves as an auto-context for the
        # "filename" and "file_path" slots.
        self.register(
            "sandbox",
            "ref_sandbox"
        )


# Register a factory for a default SandboxContext as an on-demand option
# for the "sandbox" and "ref_sandbox" slots.
AutoContext.on_demand(
    (lambda: SandboxContext()),
    "sandbox", "ref_sandbox"
)


class TestsSandboxContext(AutoContext):
    """
    Establishes a sandbox directory for validating tests. The process is
    largely the same as that used by SandboxContext, but a separate
    directory is used to prevent any possible interference between test
    validation and submission evaluation.
    """
    def __init__(self, depends=None, hidden=True):
        """
        Creates a context which establishes a new sandbox directory. The
        context creation function places the full path to this
        directory in the "tests_sandbox" context slot. A list of
        dependencies may be provided, and hidden can be set to False if
        desired.
        """
        self.dir = None
        # TODO: Clean up this temporary directory rather than letting
        # Python do that on shutdown...

        def establish_context(prev_context):
            """
            Creates a new temporary directory and puts its absolute path
            in the "tests_sandbox" context slot. Copies helper files and
            the solution default target into this sandbox.
            """
            tinfo = context_utils.extract(prev_context, "task_info")
            spec = tinfo["specification"]

            self.dir = tempfile.TemporaryDirectory(
                suffix="__validation_tmp",
                dir=load.SANDBOX_DIR
            )

            # Copy helper files into the sandbox if there are any
            # Note that we don't use symlinks here, because we don't
            # want destructive student code to modify files outside
            # the sandbox...
            # TODO: Use symlinks in places where we feel safe,
            # especially for large starter files!!!
            helpers = context_utils.sandbox_filemap(spec)
            if helpers is not None:
                for filepath in helpers:
                    to = os.path.join(self.dir.name, helpers[filepath])
                    if os.path.isdir(filepath):
                        shutil.copytree(filepath, to)
                    else:
                        shutil.copy(filepath, to)

            # Copy the target file/directory from the solution dir
            soln_target = os.path.join(spec.soln_path, tinfo["target"])
            sandbox_target = os.path.join(self.dir.name, tinfo["target"])
            if os.path.isdir(soln_target):
                shutil.copytree(soln_target, sandbox_target)
            else:
                shutil.copy(soln_target, sandbox_target)

            return { "tests_sandbox": os.path.abspath(self.dir.name) }

        # Now we can call the super-class init with the context builder
        # function we just created.
        super().__init__(
            description=(
                "Test validation sandbox",
                (
                    "We will create a sandbox directory for validating"
                    " your submitted tests."
                )
            ),
            builder=establish_context,
            display_product=lambda context: (
                "Validating tests in a sandbox"
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, we can register ourselves as an auto-context for the
        # "filename" and "file_path" slots.
        self.register("tests_sandbox")


# Register a factory for a default TestsSandboxContext as an on-demand
# option for the "tests_sandbox" slot:
AutoContext.on_demand((lambda: TestsSandboxContext()), "tests_sandbox")


class CodeContext(AutoContext):
    """
    Requires "filename" and "file_path" slots (see `FileContext`), and
    establishes a "source" slot which contains the raw text of the
    target file, along with a "scope" slot which contains the parsed AST
    from the code.

    If the code cannot be parsed due to a `SyntaxError` or the like, a
    `ContextCreationError` will be generated naming the parsing error as
    its cause, although note that `potluck.load.fix_parse` is used which
    will attempt to steamroll some kinds of parsing errors while
    generating associated warnings.
    """
    def __init__(self, depends=None, hidden=False, prep=None):
        """
        Dependencies are optional; if not specified `auto` will be used
        to fill them in. `hidden` may be provided; by default this
        context is not hidden. A `prep` function may be provided; it will
        be applied to the source code string and its result will be used
        instead of the original source.
        """
        # First, create our context builder
        def establish_context(prev_context):
            """
            Establishes the following context slots based on the
            "file_path" slot, by reading the indicated file:

            - original_source: The raw file contents.
            - source: Possibly-edited (to steamroll syntax errors or by a
                prep function) file contents.
            - scope: An AST module node resulting from parsing the
                modified file contents.
            - top_scope: Same as above (but not designed to be modified).
            - parse_errors: A list of Exception objects that were
                'successfully' steamrolled by editing the source code.
            """
            filename = context_utils.extract(prev_context, "filename")
            target = context_utils.extract(prev_context, "file_path")
            with open(target, 'r', encoding="utf-8") as fin:
                original_source = fin.read()

            if prep:
                source = prep(original_source)
            else:
                source = original_source

            try:
                fixed, node, errors = load.fix_parse(source, filename)
            except Exception as e:
                raise context_utils.ContextCreationError(
                    self,
                    f"Unable to parse submitted file '{filename}'.",
                    cause=e
                )

            if node is None:
                raise context_utils.ContextCreationError(
                    self,
                    f"Unable to parse submitted file '{filename}'.",
                    cause=errors[0]
                )

            result = {
                "original_source": original_source,
                "source": fixed,
                "scope": node,
                "top_scope": node,
                "parse_errors": errors
            }

            # Report parsing issues as warnings
            if errors:
                result["warnings"] = [
                    (
                        "The following errors were encountered when parsing"
                      + " your code:<br>"
                      + html_tools.build_list(
                            html_tools.html_traceback(e)
                            for e in errors
                        )
                    )
                ]

            return result

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto("filename", "file_path")

        # Now we can call the super constructor
        super().__init__(
            description=(
                "Code in the target file",
                (
                    "We will parse the code in the target file and pay"
                    "attention to how it was written."
                ),
                "Code in the target file",
                (
                    "We parsed the code in the target file and paid"
                    "attention to how it was written."
                ),
            ),
            builder=establish_context,
            display_product=lambda context: (
                f"The code for '{context['filename']}' (shown elsewhere)."
            ),
            depends=depends,
            hidden=hidden,
            # Errors at this level need to be reported!
            generate_warnings=True
        )

        # Finally, register ourselves as an auto provider for the slots
        # that we generate:
        self.register(
            "original_source",
            "source",
            "scope",
            "top_scope",
            "parse_errors"
        )


# Register a factory for a default CodeContext as an on-demand option
# for the slots it can generate.
AutoContext.on_demand(
    (lambda: CodeContext()),
    "original_source",
    "source",
    "scope",
    "top_scope",
    "parse_errors"
)


class SolnCodeContext(AutoContext):
    """
    Requires "ref_filename" and "ref_file_path" slots (see
    `FileContext`), and establishes a "ref_source" slot which contains
    the raw text of the equivalent file from the solution code, along
    with a "ref_scope" slot which contains the parsed AST from the
    solution code. Also establishes "ref_original_source" which may be
    different from "ref_source" when a prep function is used.

    "task_info" and "submission_root" slots are also required, but those
    should always be present.

    If the solution code cannot be parsed due to a `SyntaxError` or the
    like or because no equivalent solution file exists, a
    `ContextCreationError` will be generated naming the relevant error as
    its cause.
    """
    def __init__(self, depends=None, hidden=False, prep=None):
        """
        Dependencies are optional; if not specified `auto` will be used
        to fill them in. `hidden` may be provided; by default this
        context is not hidden. A `prep` function may be supplied, which
        will be given the source code and its return value will be used
        in place of the original source code.
        """
        # First, create our context builder
        def establish_context(prev_context):
            """
            Establishes the following context slots based on the
            "ref_file_path" slot, by reading the solution version of the
            indicated file:

                ref_source: The source of the solution file.
                ref_scope: An AST module node resulting from parsing the
                    solution file.
                ref_top_scope: As above, but won't be modified.
            """
            soln_equivalent = context_utils.extract(
                prev_context,
                "ref_file_path"
            )
            ref_filename = context_utils.extract(
                prev_context,
                "ref_filename"
            )

            if not os.path.isfile(soln_equivalent):
                raise context_utils.ContextCreationError(
                    self,
                    f"Target file {soln_equivalent} does not exist in the"
                    f" solution directory."
                )

            with open(soln_equivalent, 'r', encoding="utf-8") as fin:
                contents = fin.read()

            if prep:
                source = prep(contents)
            else:
                source = contents

            try:
                node = mast.parse(source, filename=ref_filename)
            except Exception as e:
                raise context_utils.ContextCreationError(
                    self,
                    f"Unable to parse solution file '{soln_equivalent}'.",
                    cause=e
                )

            return {
                "ref_original_source": contents,
                "ref_source": source,
                "ref_scope": node,
                "ref_top_scope": node
            }

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto("ref_filename", "ref_file_path")

        # Now we can call the super constructor
        super().__init__(
            description=(
                "Code in the solution file",
                "We will parse the code in the solution file.",
            ),
            builder=establish_context,
            display_product=lambda context: (
                f"The solution code for '{context['filename']}'"
                f" (available after the revision period is over)."
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, register ourselves as an auto provider for the slots
        # that we generate:
        self.register(
            "ref_original_source",
            "ref_source",
            "ref_scope",
            "ref_top_scope"
        )


# Register a factory for a default CodeContext as an on-demand option
# for the slots it can generate.
AutoContext.on_demand(
    (lambda: SolnCodeContext()),
    "ref_source", "ref_scope", "ref_top_scope"
)


class TestsCodeContext(AutoContext):
    """
    Requires "tests_filename" and "tests_file_path" slots (see
    `TestsFileContext`), and establishes a "tests_source" slot which
    contains the raw text of the target file, along with a "tests_scope"
    slot which contains the parsed AST from the code.

    If the code cannot be parsed due to a `SyntaxError` or the like, a
    `ContextCreationError` will be generated naming the parsing error as
    its cause, although note that `potluck.load.fix_parse` is used which
    will attempt to steamroll some kinds of parsing errors while
    generating associated warnings.
    """
    def __init__(self, depends=None, hidden=False, prep=None):
        """
        Dependencies are optional; if not specified `auto` will be used
        to fill them in. `hidden` may be provided; by default this
        context is not hidden. A `prep` function may be provided; it will
        be applied to the source code string and its result will be used
        instead of the original source.
        """
        # First, create our context builder
        def establish_context(prev_context):
            """
            Establishes the following context slots based on the
            "tests_file_path" slot, by reading the indicated file:

            - original_tests_source: The raw file contents.
            - tests_source: Possibly-edited (to steamroll syntax errors
                or by a prep function) file contents.
            - tests_scope: An AST module node resulting from parsing the
                modified file contents.
            - top_tests_scope: Same as above (but not designed to be
                modified).
            - tests_parse_errors: A list of Exception objects that were
                'successfully' steamrolled by editing the source code.
            """
            filename = context_utils.extract(prev_context, "tests_filename")
            target = context_utils.extract(prev_context, "tests_file_path")
            with open(target, 'r', encoding="utf-8") as fin:
                original_tests_source = fin.read()

            if prep:
                tests_source = prep(original_tests_source)
            else:
                tests_source = original_tests_source

            try:
                fixed, node, errors = load.fix_parse(tests_source, filename)
            except Exception as e:
                raise context_utils.ContextCreationError(
                    self,
                    f"Unable to parse submitted tests file '{filename}'.",
                    cause=e
                )

            if node is None:
                raise context_utils.ContextCreationError(
                    self,
                    f"Unable to parse submitted tests file '{filename}'.",
                    cause=errors[0]
                )

            result = {
                "original_tests_source": original_tests_source,
                "tests_source": fixed,
                "tests_scope": node,
                "top_tests_scope": node,
                "tests_parse_errors": errors
            }

            # Report parsing issues as warnings
            if errors:
                result["warnings"] = [
                    (
                        "The following errors were encountered when parsing"
                      + " your tests:<br>"
                      + html_tools.build_list(
                            html_tools.html_traceback(e)
                            for e in errors
                        )
                    )
                ]

            return result

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto("tests_filename", "tests_file_path")

        # Now we can call the super constructor
        super().__init__(
            description=(
                "Code in the tests file",
                (
                    "We will parse the code in the tests file and pay"
                    " attention to how it was written."
                ),
                "Code in the tests file",
                (
                    "We parsed the code in the tests file and paid"
                    "attention to how it was written."
                ),
            ),
            builder=establish_context,
            display_product=lambda context: (
                f"The tests code in '{context['tests_filename']}'"
                f" (shown elsewhere)."
            ),
            depends=depends,
            hidden=hidden,
            # Errors at this level need to be reported!
            generate_warnings=True
        )

        # Finally, register ourselves as an auto provider for the slots
        # that we generate:
        self.register(
            "original_tests_source",
            "tests_source",
            "tests_scope",
            "top_tests_scope",
            "tests_parse_errors"
        )


# Register a factory for a default CodeContext as an on-demand option
# for the slots it can generate.
AutoContext.on_demand(
    (lambda: TestsCodeContext()),
    "original_tests_source",
    "tests_source",
    "tests_scope",
    "top_tests_scope",
    "tests_parse_errors"
)


class ModuleContext(AutoContext):
    """
    Requires a "top_scope" slot (see `CodeContext` which must hold an
    entire module's AST, and creates a "module" slot which holds the
    module object that results from running that code.

    If `optimism` is available, any test cases established will be
    cleared when the module is loaded, and then any cases established by
    loading the module will be saved in a "test_cases" context slot.
    """
    _filename = "filename"
    _src = "file_path"
    _from = "top_scope"
    _sandbox = "sandbox"
    _to = "module"
    _to_cases = "test_cases"
    _description = (
        "The values defined by the code",
        (
            "We will run your code so that we can run tests on the"
            " values it defines."
        )
    )

    def display_result(self, context):
        """
        Context result display function which lists names defined in the
        loaded module.
        """
        loaded = context[self._to]
        defined = [
            name
            for name in dir(loaded)
            if not name.startswith("__") or not name.endswith("__")
        ]
        if len(defined) == 0:
            result = "No values were defined in the file."
        else:
            result = (
                "The following values were defined in the file:\n"
              + html_tools.build_list(
                    "<code>{}</code>".format(name)
                    for name in defined
                )
            )

        if OPTIMISTIC:
            ndef = len(context[self._to_cases])
            if ndef > 0:
                result += (
                    "<br>\nYour file defined {} test cases.".format(ndef)
                )

        return result

    def __init__(self, depends=None, hidden=False, prep=None, wrap=None):
        """
        Dependencies are optional; if not specified `auto` will be used
        to fill them in. `hidden` may be provided; by default this
        context is not hidden.

        `prep` may be supplied; it is a function which receives the
        current context dictionary and will be run before the module is
        loaded.

        `wrap` may be supplied; it is a function which will be given the
        module once it's loaded and its return value will be used instead
        of the original module.
        """
        # First, create our context builder
        def establish_context(prev_context):
            """
            Establishes the "module" context slot by executing the code
            in the "top_scope" slot. Actually, uses self._from and
            self._to to determine the slots to read/write, since it can
            also be used to create "ref_module" from "ref_top_scope".
            Also uses self._src if available to find the source file.
            """
            # Fetch the AST node that we'd like to turn into a module
            node = context_utils.extract(prev_context, self._from)

            # Prefix the file name so that submitted and solution
            # modules with the same name don't collide
            filename = context_utils.extract(prev_context, self._filename)
            if self._from == "top_scope":
                prefix = "subm_"
            elif self._from == "ref_top_scope":
                prefix = "soln_"
            elif self._from == "top_tests_scope":
                prefix = "tests_"
            else:
                prefix = "loaded_"
            full_name = prefix + filename

            # Figure out our file source if we can
            src_path = prev_context.get(self._src)
            if src_path:
                src_path = os.path.abspath(src_path)

            # Run the prep function if one was supplied
            if prep is not None:
                prep(prev_context)

            # Set up phony stdin, so that stray inputs won't immediately
            # crash the program (if their results are used in a delicate
            # manner, they still will of course, but we supply '1' for
            # each input, which will survive conversion to an int or
            # float).
            old_stdin = sys.stdin
            sys.stdin = context_utils.AllOnes()
            # Note: we don't care about echoing inputs to stdout here...

            # Set up phony stdout and stderr
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()

            # Prepare for capturing test cases
            test_cases = None

            if OPTIMISTIC:
                # Ask for the default level of failure messages
                optimism.detailLevel(0)
                # Get rid of any previously-recorded cases
                optimism.deleteAllTestSuites()

            # Actually load the module
            try:
                module = load.create_module_in_sandbox(
                    node,
                    full_name,
                    sandbox_dir=context_utils.extract(
                        prev_context,
                        self._sandbox
                    ),
                    on_disk=src_path
                )
            except Exception as e:
                raise context_utils.ContextCreationError(
                    self,
                    "Unable to run code.",
                    e
                )
            finally: # clean up input/output streams
                sys.stdin = old_stdin
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            if OPTIMISTIC:
                try:
                    # Capture defined test cases
                    test_cases = optimism.listAllCases()
                except Exception as e:
                    raise context_utils.ContextCreationError(
                        self,
                        "Error managing optimism tests.",
                        e
                    )

            # Wrap our module result if necessary
            if wrap is not None:
                module = wrap(module)

            # Return our new slot
            result = { self._to: module }
            if test_cases is not None:
                result[self._to_cases] = test_cases

            return result

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto(self._filename, self._from, self._sandbox)

        # Now we can call the super constructor
        super().__init__(
            description=self._description,
            builder=establish_context,
            display_product=self.display_result,
            depends=depends,
            hidden=hidden
        )

        # Finally, register ourselves as an auto provider for the slots
        # that we generate:
        if OPTIMISTIC:
            self.register(self._to, self._to_cases)
        else:
            self.register(self._to)


# Register a factory for a default ModuleContext as an on-demand option
# for the "module" slot, or for that slot plus the "test_cases" slot if
# optimism is available.
if OPTIMISTIC:
    AutoContext.on_demand(
        (lambda: ModuleContext()),
        "module", "test_cases"
    )
else:
    AutoContext.on_demand((lambda: ModuleContext()), "module")


class SolnModuleContext(ModuleContext):
    """
    Works like `ModuleContext`, but for the solution module: Requires a
    "ref_top_scope" slot (see `SolnCodeContext`) which must hold the
    solution module's AST, and creates a "ref_module" slot which holds
    the module object that results from running that code.

    If the optimism module is available, also creates a
    "ref_expectations" slot.
    """
    _filename = "ref_filename"
    _src = "ref_file_path"
    _from = "ref_top_scope"
    _sandbox = "ref_sandbox"
    _to = "ref_module"
    _to_cases = "ref_test_cases"
    _description = (
        "The values defined by the solution code",
        (
            "We will run the solution code so that we can compare"
            " its results to the results of your code."
        )
    )

    # Note: just by overriding these fields we've done all that we need
    # to to change where we're reading from and where we're putting our
    # results.


# Register a factory for a default SolnModuleContext as an on-demand
# option for the "ref_module" slot, or for that slot plus the
# "ref_test_cases" slot if optimism is available.
if OPTIMISTIC:
    AutoContext.on_demand(
        (lambda: SolnModuleContext()),
        "ref_module", "ref_test_cases"
    )
else:
    AutoContext.on_demand((lambda: SolnModuleContext()), "ref_module")


class TestsModuleContext(ModuleContext):
    """
    Requires a "top_tests_scope" slot (see `TestsCodeContext` which must
    hold an entire module's AST, and creates a "tests_module" slot which
    holds the module object that results from running that code.
    """
    _filename = "tests_filename"
    _src = "tests_file_path"
    _from = "top_tests_scope"
    _sandbox = "tests_sandbox"
    _to = "tests_module"
    _to_cases = "validation_test_cases"
    _description = (
        "The values defined by the solution code",
        (
            "We will run the solution code so that we can compare"
            " its results to the results of your code."
        )
    )

    # Note: just by overriding these fields we've done all that we need
    # to to change where we're reading from and where we're putting our
    # results.


# Register a factory for a default TestsModuleContext as an on-demand
# option for the "tests_module" slot, or for "tests_module" and
# "validation_test_cases" if optimism is available.
if OPTIMISTIC:
    AutoContext.on_demand(
        (lambda: TestsModuleContext()),
        "tests_module", "validation_test_cases"
    )
else:
    AutoContext.on_demand((lambda: TestsModuleContext()), "tests_module")


class DefinitionsContext(AutoContext):
    """
    Creates a "defs" slot based on a "top_scope" slot which holds a
    mapping from function names to AST nodes covering every `def` which
    occurs in the provided scope, including nested and method
    definitions.

    Note that nested definitions may shadow exterior definitions in the
    map if they have the same name. (TODO: Not that?)
    """
    _from = "top_scope"
    _to = "defs"

    def __init__(self, depends=None, hidden=False):
        """
        Dependencies may be supplied and the context may be hidden. If no
        dependencies are given, an auto-dependency for the "top_scope"
        slot will be generated.
        """
        def establish_context(prev_context):
            """
            This context_builder function depends on a "scope" context
            holding an AST node, and adds a "defs" context item which
            contains a dicitonary of all AST nodes in that scope which
            are function definitions (includes interior defs). The keys
            of the dictionary are the names of the functions. Lambdas
            are not included in the list.
            """
            within = context_utils.extract(prev_context, self._from)

            # Find definition AST nodes
            alldefs = set()
            for pat in patterns.ALL_DEF_PATTERNS:
                alldefs |= set(
                    node
                    for node, bindings in mast.findall(within, pat)
                )

            # Create the mapping
            defmap = {}
            for defn in alldefs:
                defmap[defn.name] = defn

            # Return our resulting slot
            return { self._to: defmap }

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto(self._from)

        # Now we can call the super constructor
        super().__init__(
            description=(
                "The function definitions in the code",
                (
                    "We will inspect the code and extract all of the"
                    " function definitions."
                )
            ),
            builder=establish_context,
            display_product=lambda context: (
                "The following functions were defined:\n"
              + html_tools.build_list(
                    f"<code>{name}</code>"
                    for name in context[self._to]
                )
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, register ourselves as an auto provider for the slot
        # that we generate:
        self.register(self._to)


# Register a factory for a default DefinitionsContext as an on-demand
# option for the "defs" slot.
AutoContext.on_demand((lambda: DefinitionsContext()), "defs")


class SolnDefinitionsContext(DefinitionsContext):
    """
    Works like `DefinitionsContext` but extracts a "ref_defs" slot from
    the "ref_top_scope" slot.
    """
    _from = "ref_top_scope"
    _to = "ref_defs"


# Register a factory for a default SolnDefinitionsContext as an on-demand
# option for the "ref_defs" slot.
AutoContext.on_demand((lambda: DefinitionsContext()), "ref_defs")


class DocstringsContext(AutoContext):
    """
    Establishes a "docstrings" slot based on "defs" and "module" slots,
    which contains a mapping from function names to their docstrings.
    This mapping will only include functions defined at the top level of
    the module.
    """

    def __init__(self, depends=None, hidden=False):
        """
        May have non-automatic dependencies and/or be hidden. If manual
        dependencies are provided, make sure they establish the "defs"
        and "module" slots.
        """
        def establish_context(prev_context):
            """
            This context_builder requires *both* a "defs" node (see
            `DefinitionsContext`) *and* a "module" node (see
            `ModuleContext`), because it makes use of both the AST and
            the actual imported module.

            It uses the defs map to figure out what functions to look
            for, and then for every function defined *at the top level*
            of the submitted code, it looks up the docstring from the
            module object, returning a mapping from function names to
            docstrings. If there are functions defined inside of other
            functions, they will not show up in the resulting
            "docstrings" context item.
            """
            defs = context_utils.extract(prev_context, "defs")
            submitted = context_utils.extract(prev_context, "module")

            docsmap = {}

            for fname in defs:
                fcn = getattr(submitted, fname, None)
                if fcn:
                    # this function is defined at the module level
                    doc = getattr(fcn, "__doc__", None) or ""
                    doc = doc.strip()
                    docsmap[fname] = doc

            return { "docstrings": docsmap }

        # Figure out if we need to use automatic dependencies:
        if depends is None:
            depends = auto("defs", "module")

        super().__init__(
            description=(
                "The function docstrings",
                (
                    "We will extract the docstrings from each function"
                    " defined by your code."
                )
            ),
            builder=establish_context,
            display_product=lambda context: (
                "The following docstrings were found:\n"
              + html_tools.build_list(
                    (
                        f"Function <code>{name}</code>:<br>"
                        f"<pre>{doc}</pre>"
                    )
                    for name, doc in context["docstrings"].items()
                )
            ),
            depends=depends,
            hidden=hidden
        )

        # Finally, register ourselves as an auto provider for the slot
        # that we generate:
        self.register("docstrings")


# Register a factory for a default DocstringsContext as an on-demand
# option for the "docstrings" slot.
AutoContext.on_demand((lambda: DocstringsContext()), "docstrings")


#--------------------------------------------------#
# Functions for displaying context builder results #
#--------------------------------------------------#

def build_context_value_displayer(
    key,
    compare_ref=True,
    include_diff=True,
    labels=["Your value", "Solution value", "Comparison"]
):
    """
    Creates a display_product function which will show the contents of a
    single specific context key, and by default, will include multiple
    tabs that show the value, the reference value, and a diff of the two
    values. String values are shown as-is; non-string values are
    converted to strings using html_tools.big_repr.

    If the number of characters in a value's representation would exceed
    VALUE_SIZE_LIMIT, we will truncate it.

    Set compare_ref to False to simply show the value for the specified
    key, and set include_diff to False when compare_ref is True to omit
    the difference tab in the comparison.

    Custom labels for the two values and their difference (second and/or
    third labels may be ignored depending on other flags) may be given
    using the labels argument.

    Returns a function suitable for use as the display_product argument
    to a Context.
    """
    def display_context_value(context):
        """
        A function that returns HTML code which displays the value of a
        single specific context key, possibly with tabs to view the value
        produced by submitted code, the reference value, and the
        difference between the two (as a diff).

        See build_context_value_displayer, which created this function.
        """
        if not compare_ref:
            if key in context:
                # simply return a single <pre> containing a representation of
                # the value
                if isinstance(context[key], str):
                    rep = context[key]
                else:
                    try:
                        rep = html_tools.big_repr(context[key])
                    except TypeError:
                        rep = repr(context[key])
                rep = html_tools.escape(
                    html_tools.truncate(rep, VALUE_SIZE_LIMIT)
                )
                return f"<pre class='context-value'>{rep}</pre>"
            else:
                # failed to create the context key we're looking for!
                return (
                    f"<div class='context-missing'>Failed to establish"
                    f" context '{key}'!</div>"
                )
        else:
            if key in context:
                if isinstance(context[key], str):
                    rep = context[key]
                else:
                    try:
                        rep = html_tools.big_repr(context[key])
                    except TypeError:
                        rep = repr(context[key])
                rep = html_tools.truncate(rep, VALUE_SIZE_LIMIT)
                erep = html_tools.escape(rep)
                rep_html = f"<pre class='context-value'>{erep}</pre>"
            else:
                rep = ""
                rep_html = (
                    f"<div class='context-missing'>Failed to establish"
                    f" context '{key}'!</div>"
                )

            if "ref_" + key in context:
                if isinstance(context["ref_" + key], str):
                    ref_rep = context["ref_" + key]
                else:
                    try:
                        ref_rep = html_tools.big_repr(context["ref_" + key])
                    except TypeError:
                        ref_rep = repr(context["ref_" + key])
                ref_rep = html_tools.truncate(ref_rep, VALUE_SIZE_LIMIT)
                ref_erep = html_tools.escape(ref_rep)
                ref_rep_html = f"<pre class='context-value'>{ref_erep}</pre>"
            else:
                ref_rep = ""
                ref_rep_html = (
                    f"<div class='context-missing'>Failed to establish"
                    f" context 'ref_{key}'!</div>"
                )

            if include_diff:
                # Include a tab for the differences
                diff = html_tools.html_diff_table(
                    rep,
                    ref_rep,
                    out_title=labels[0],
                    ref_title=labels[1]
                )
                return html_tools.build_html_tabs(
                    [
                        (labels[0], rep_html),
                        (labels[1], ref_rep_html),
                        (labels[2], diff),
                    ]
                )
            else:
                # No tab for the differences
                return html_tools.build_html_tabs(
                    [
                        (labels[0], rep_html),
                        (labels[1], ref_rep_html),
                    ]
                )

    return display_context_value


def build_simple_context_value_displayer(
    key,
    compare_ref=True,
    labels=["Your value", "Solution value"]
):
    """
    Creates a display_product function similar to the
    `build_context_value_displayer` result, but for simple values which
    don't need a pre wrapper and which can be displayed side-by-side
    (e.g., numbers). No diff is included, as it's presumed that any
    differences will be obvious, and values are converted to strings
    using str() instead of html_tools.big_repr. Representations that end
    up longer than VALUE_SIZE_LIMIT are still truncated.

    Set compare_ref to False to include only the main value.

    Custom labels for the two values may be given using the labels
    argument. These are not used if compare_ref is False.

    Returns a function suitable for use as the display_product argument
    to a Context.
    """
    def display_context_value(context):
        """
        A function that returns HTML code which displays the value of a
        single specific context key, possibly side-by-side with the
        corresponding reference value.

        See build_simple_context_value_displayer, which created this function.
        """
        if not compare_ref:
            if key in context:
                return str(context[key])
            else:
                return (
                    f"<div class='context-missing'>Failed to establish"
                    f" context '{key}'!</div>"
                )
        else:
            if key in context:
                rep = html_tools.truncate(
                    repr(context[key]),
                    VALUE_SIZE_LIMIT
                )
                erep = html_tools.escape(rep)
                rep_html = "<code>{}</code>".format(erep)
            else:
                rep_html = (
                    f"<div class='context-missing'>Failed to establish"
                    f" context '{key}'!</div>"
                )

            if "ref_" + key in context:
                ref_rep = html_tools.truncate(
                    repr(context["ref_" + key]),
                    VALUE_SIZE_LIMIT
                )
                ref_erep = html_tools.escape(ref_rep)
                ref_rep_html = "<code>{}</code>".format(ref_erep)
            else:
                ref_rep_html = (
                    f"<div class='context-missing'>Failed to establish"
                    f" context 'ref_{key}'!</div>"
                )

            return f"""
<table class='context-values'>
  <tbody>
    <tr> <th>{labels[0]}</th> <td>{rep_html}</td>  </tr>
    <tr> <th>{labels[1]}</th> <td>{ref_rep_html}</td>  </tr>
  </tbody>
</table>
"""

    return display_context_value


def create_distribution_result_displayer(context_key="distribution"):
    """
    Creates a distribution results display function, which will read
    values from the given context key ("distribution" by default). Also
    reads a value from the matching "ref_" key.
    """
    def display_distribution_results(context):
        """
        Displays the 'distribution' and 'ref_distribution' context keys
        side-by-side.
        """
        sub_dist = context[context_key]["results"]
        ref_dist = context["ref_" + context_key]["results"]

        all_results = set(sub_dist) | set(ref_dist)

        n_samples = context[context_key]["trials"]

        rows = []
        for result in sorted(all_results):
            rows.append(
                (
                    "<tr> <td>{result}</td> <td>{n}</td>"
                  + " <td>{ref_n}</td> </tr>"
                ).format(
                    result=html_tools.dynamic_html_repr(
                        result,
                        limit=VALUE_SIZE_LIMIT
                    ),
                    n=repr(sub_dist.get(result, 0)),
                    ref_n=repr(ref_dist.get(result, 0))
                )
            )

        return """
The distribution of results from your function and the solution function
after {n_samples} trials (note: distributions may differ somewhat due to
random chance.):
<table class='result_distribution'>
  <thead>
    <tr>
      <th>Result value</th>
      <th>Observed count</th>
      <th>Solution count</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>
""".format(n_samples=n_samples, rows='\n    '.join(rows))

    return display_distribution_results


def create_image_result_displayer(context_key="image", alt_key="output"):
    """
    Creates a context value display function which shows the "image" slot
    (or an image from another slot) with alt text from the "output" slot
    (assuming turtleBeads descriptions are used).

    If a ref_ slot and an alt ref_ slot are available, a comparison will
    be included.
    """
    def image_displayer(context):
        """
        Returns HTML code for displaying an image from the given context,
        with alt text from a different slot.
        """
        img = context[context_key]
        alt = context[alt_key]
        if "ref_" + context_key in context and "ref_" + alt_key in context:
            ref_img = context["ref_" + context_key]
            ref_alt = context["ref_" + alt_key]
            return html_tools.build_html_tabs(
                [
                    (
                        "Your image:",
                        html_tools.html_image(img, alt)
                    ),
                    (
                        "Solution image:",
                        html_tools.html_image(ref_img, ref_alt)
                    ),
                    (
                        "Animation:",
                        html_tools.html_animation(
                            compare.diff_anim_frames(img, ref_img, 10),
                            (
                                # TODO: Diff of alt texts here?
                                "An animation between your image and the"
                                " solution image."
                            ),
                            delays=[500] + [100] * 10 + [500]
                        )
                    )
                ]
            )
        else:
            # No ref values available for a comparison
            return html_tools.html_image(img, alt)

    return image_displayer


#---------------#
# SiftedContext #
#---------------#

class SiftedContext(Context):
    """
    Working from the "output" and "ref_output" slots (or some other
    custom list of slots), this `Context` creates "sifted" and
    "ref_sifted" slots which hold the results of matching a regular
    expression against the input value.
    """
    def __init__(
        self,
        pattern,
        depends,
        description=None,
        slot_map={"output": "sifted", "ref_output": "ref_sifted"},
        first_match=False,
        require_match=True,
        use_matchobjs=False
    ):
        """
        Dependencies must be supplied. A custom description may be
        supplied (and is often useful). A custom slot map may be supplied
        to specify which incoming slots to process, and for each incoming
        slot, which new slot to create to store the result from that
        slot.
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        def establish_context(prev_context):
            """
            This context_builder function processes a custom list of
            slots by applying a regular expression to them.
            """
            result = {}
            # Process each requested slot
            for from_slot in slot_map:
                to_slot = slot_map[from_slot]

                # Grab our input value
                value = context_utils.extract(prev_context, from_slot)
                if not isinstance(value, str):
                    raise TypeError(
                        f"SiftedContext can only refine string values,"
                        f" but was asked to refine value of slot"
                        f" {from_slot} which was a {type(value)}."
                    )

                # Apply our regular expression
                matches = pattern.finditer(value)

                # Grab the first match if that's what we need
                if first_match:
                    try:
                        first = next(matches)
                    except StopIteration:
                        raise ValueError(
                            f"While refining '{from_slot}' context,"
                            f" found no matches for pattern."
                        )
                    # Add either the match object or matching string
                    if use_matchobjs:
                        result[to_slot] = first
                    else:
                        result[to_slot] = first.group()
                else: # Grab all matches
                    if use_matchobjs:
                        objs = [m for m in matches]
                    else:
                        objs = [m.group() for m in matches]

                    # list might be empty...
                    if require_match and len(objs) == 0:
                        raise ValueError(
                            f"While refining '{from_slot}' context,"
                            f" found no matches for pattern."
                        )

                    result[to_slot] = objs

            # Return our results
            return result

        def display_result(context):
            """
            Displays the results of slot sifting as a tabbed HTML
            structure with one tab per input slot.
            """
            tablist = []
            for from_slot in slot_map:
                to_slot = slot_map[from_slot]
                result = context_utils.extract(context, to_slot)

                if isinstance(result, re.Match):
                    display = f"<pre>{result.group(0)}</pre>"
                elif isinstance(result, list):
                    if len(result) == 0:
                        display = "&lt;no matches&gt;"
                    elif isinstance(result[0], str):
                        display = html_tools.build_list(
                            [
                                f"<pre>{entry}</pre>"
                                for entry in result
                            ]
                        )
                    else: # results are Match objects
                        display = html_tools.build_list(
                            [
                                f"<pre>{match.group(0)}</pre>"
                                for match in result
                            ]
                        )
                else: # results should be strings
                    display = f"<pre>{result}</pre>"

                tablist.append((from_slot, display))

            return (
                "Results for expression <pre><code>{expr}</code></pre>:<br>"
              + html_tools.build_html_tabs(tablist)
            )

        # Create a default description if necessary
        if description is None:
            stuff = phrasing.comma_list(
                slot
                for slot in slot_map
                if not slot.startswith("ref_")
            )
            description = (
                f"Certain parts of the {stuff}",
                (
                    f"We will search for the pattern"
                    f"<pre><code>{pattern.pattern}</code></pre> within"
                    f" the {stuff} and inspect the results."
                )
            )

        # Now we can call the super constructor
        super().__init__(
            description=description,
            builder=establish_context,
            display_product=display_result,
            depends=depends
        )
