"""
Code for defining examples that should be shown as part of instructions.

snippets.py

This module can be used in specifications files to define named examples,
which can then be compiled to HTML files using the --snippets option.
These examples will be evaluated within the context of the solution code,
and their output + return values will be formatted for display to the
students. By using snippets this way, as long as your solution file is
up-to-date, your example output will never be out-of-sync with what the
problem set is actually asking for.

Example usage:

```py
from potluck import snippets as sn

EXAMPLE = [
    {
        "key": "value",
        "key2": "value2",
    },
    {
        "key": "valueB",
        "key2": "value2B"
    }
]

sn.Variables(
    "vars", # snippet ID
    "<code>EXAMPLE</code> variable", # snippet displayed title
    (
        "A simple example of what the input data might look like, and"
        " the slightly more complex <code>DATA</code> variable provided"
        " in the starter code."
    ), # displayed snippet caption
    [ "EXAMPLE", "DATA" ] # list of variable names to display definitions of
).provide({ "EXAMPLE": EXAMPLE })
# provide overrides (or provides missing) solution module values

sn.FunctionCalls(
    "examples", # snippet ID
    "Example results", # title
    (
        "Some examples of what <code>processData</code> should return"
        " for various inputs, using the <code>EXAMPLE</code> and"
        " <code>DATA</code> variables shown above."
    ),
    # caption (note we're assuming the 'vars' snippet will be included
    # first, otherwise this caption doesn't make sense).
    [
        ("processData", (EXAMPLE, 1)),
        ("processData", (EXAMPLE, 2)),
        ("processData", (EXAMPLE, 3))",
        ("processData", (cu.SolnValue("DATA"), 3)),
    ], # list of function name, arguments tuples to evaluate
)

sn.RunModule(
    "run", # ID
    "Full output example", # title
    (
        "An example of what the output should look like when your code"
        " is run. Note that the blue text shows what inputs were"
        " provided in this example."
    ), # caption
).provide_inputs(["A", "B"]) # we're providing some inputs during the run
```

The various snippet classes like `Variable`, `Expressions`, and
`RunModule` each inherit from `potluck.specifications.TestGroup`
meaning that you can use the various modification methods from that
module (such as `provide_inputs` as shown above) to control exactly how
the code is run.
"""

import textwrap
import re
import os
import sys

import pygments

from . import logging
from . import specifications
from . import file_utils
from . import html_tools
from . import harness
from . import render
from . import rubrics
from . import contexts
from . import context_utils


#---------#
# Helpers #
#---------#

FMT_WIDTH = 80
"""
Line width we'll attempt to hit for formatting output nicely.
"""


def wrap_str(string, width):
    """
    Returns a list of strings, which when combined form the given
    string, where none is longer than the given width. Lines are broken
    at spaces whenever possible, but may be broken in the middle of
    words when a single word is longer than the target width. This
    function uses a greedy algorithm that doesn't optimize the evenness
    of the right margin. \\n and \\r are represented by those character
    pairs, but other characters are as-is.
    """
    escaped = string.replace('\n', '\\n')
    escaped = escaped.replace('\r', '\\r')
    words = escaped.split(' ')
    result = []
    while len(words) > 0: # until we've used up the words
        # Figure out how many words would fit on the next line
        i = 0
        # + i accounts for spaces we'll need
        while len(words[:i + 1]) + (i + 1) < width:
            i += 1

        # Back off to the number that fits
        i -= 1

        # first word doesn't fit!
        if i == -1:
            first = words[0]
            # Chop up the first word and put the pieces into the result
            pieces = len(first) // width
            for j in range(pieces):
                result.append(first[width * j:width * (j + 1)])

            # Handle leftovers
            rest = first[width * pieces:]
            # Note that even empty leftovers serve as a placeholder to
            # ensure that a space gets added.
            words[0] = rest # put rest back into words, replacing old
        else:
            # at least one word fits
            line = ' '.join(words[:i + 1]) + ' '
            result.append(line)
            words = words[i + 1:]

    # Remove the extra space introduced after the end of the last word
    # Works even for an empty string input
    result[-1] = result[-1][:-1]

    return result


def wrapped_repr(obj, width=FMT_WIDTH, indentation=1, prefix='', memo=None):
    """
    Returns a string representing the given object, whose lines are not
    longer than the given width, and which uses the given number of
    spaces to indent sub-objects when necessary. Replacement for
    pprint.pformat, which does NOT reorder dictionary keys. May violate
    the width restriction when given a complex object that it doesn't
    know how to wrap whose repr alone is wider than the specified width.

    A prefix may be supplied, which will be added to the first line of
    the given representation as-is. The prefix itself will not be subject
    to wrapping, but the first line of the result will in some cases wrap
    earlier to compensate for the prefix. The prefix should not include
    any newlines or carriage returns.

    The memo helps avoid problems with recursion, and doesn't need to be
    provided explicitly.
    """
    # Create a memo if we need to
    if memo is None:
        memo = set()

    # Check the memo
    if id(obj) in memo:
        return '...'

    # Add ourselves to the memo
    memo.add(id(obj))

    simple = prefix + repr(obj)

    if len(simple) <= width: # no need to do anything fancy
        return simple

    indent = ' ' * indentation
    between = '\n' + indent

    broken = repr(obj)
    if len(broken) < width - indentation:
        return prefix + '\\' + between + broken

    elif type(obj) == str: # need to wrap this string
        lines = wrap_str(obj, width - (indentation + 2))
        return (
            prefix + '(' + between
          + between.join('"' + line + '"' for line in lines)
          + '\n)'
        )

    elif type(obj) == bytes: # need to wrap these bytes
        lines = wrap_str(obj, width - (indentation + 3))
        return (
            prefix + '(' + between
          + between.join('b"' + line + '"' for line in lines)
          + '\n)'
        )

    elif type(obj) in (list, tuple, set): # need to wrap each item
        if type(obj) in (list, tuple):
            ldelim, rdelim = str(type(obj)())
        elif len(obj) == 0:
            return prefix + 'set()' # too bad if width is < 5
        else:
            ldelim = '{'
            rdelim = '}'

        result = prefix + ldelim + between
        for item in obj:
            result += textwrap.indent(
                wrapped_repr(item, width - indentation, indentation),
                indent
            ) + ',' + between

        return result[:-len(between)] + '\n' + rdelim

    elif type(obj) == dict: # need to wrap keys and values
        indent = ' ' * indentation
        between = '\n' + indent

        result = prefix + '{' + between
        for key in obj:
            key_repr = wrapped_repr(
                key,
                width - (indentation + 1),
                indentation
            )
            val = obj[key]
            val_repr = wrapped_repr(
                val,
                width - indentation * 2,
                indentation
            )

            # Can we fit on one line?
            if len(indent) + len(key_repr) + len(val_repr) + 3 <= width:
                result += key_repr + ': ' + val_repr + ',' + between
            elif val_repr[1] == '\n': # ldelim/newline start
                result += (
                    key_repr + ':' + val_repr[0] + '\n'
                  + textwrap.indent(val_repr[2:], indent)
                  + ',' + between
                )
            else:
                result += key_repr + ':\n' + textwrap.indent(
                    val_repr,
                    indent * 2
                ) + ',' + between

        # Chop off final between and add closing brace after a newline
        result = result[:-len(between)] + '\n}'

        return result

    else: # Not sure how to wrap this, so we give up...
        return prefix + repr(obj)


def wrapped_with_prefix(obj, prefix, indentation_level=0):
    """
    Returns a string representing the given object, as `wrapped_repr`
    would, except that:

    1. The first line includes the given prefix (as a string without
       repr applied to it; after indentation) and the wrapping of object
       values takes this into account.
    2. The entire representation is indented by the given indentation
       level (one space per level).
    """
    rep = wrapped_repr(
        obj,
        width=FMT_WIDTH - indentation_level,
        indentation=1,
        prefix=prefix
    )

    # remove extra indentation from tuple
    rep = textwrap.dedent(rep)

    # restore indent and add prefix
    return textwrap.indent(rep, ' ' * indentation_level)


def extract(context, key):
    """
    Gets value from a context but shows the context's error log if it
    can't.
    """
    if key in context:
        return context[key]
    else:
        if "ref_error_log" in context:
            print(
                (
                    "Error: context is missing the '{}' key. Error log"
                    " is:\n{}"
                ).format(key, context["ref_error_log"]),
                file=sys.stderr
            )
        else:
            print(
                "Error: context is missing the '{}' key. No error log"
                " available."
            )


#--------------#
# Registration #
#--------------#

SNIPPET_REGISTRY = {}
"""
All registered snippets, by defining module and then snippet ID.
"""


#-----------------------#
# Snippet setup/cleanup #
#-----------------------#

REMEMBER = {}
"""
Things to remember so we can undo setup changes.
"""


def snippet_setup(context):
    """
    If the wavesynth module is available, disables the playTrack and
    saveTrack functions from that module. If the optimism module is
    available, disables colors for that module.
    """
    try:
        import wavesynth
        REMEMBER["playTrack"] = wavesynth.playTrack
        wavesynth.playTrack = lambda _=None: None
        REMEMBER["saveTrack"] = wavesynth.saveTrack
        wavesynth.saveTrack = lambda _: None
    except ModuleNotFoundError:
        pass

    try:
        import optimism
        REMEMBER["opt_colors"] = optimism.COLORS
        optimism.colors(False)
    except ModuleNotFoundError:
        pass

    return context


def snippet_cleanup(context):
    """
    Puts things back how they were before `snippet_setup`.
    """
    try:
        import wavesynth
        wavesynth.playTrack = REMEMBER["playTrack"]
        wavesynth.saveTrack = REMEMBER["saveTrack"]
    except ModuleNotFoundError:
        pass

    try:
        import optimism
        optimism.colors(REMEMBER["opt_colors"])
    except ModuleNotFoundError:
        pass

    return context


#----------------------------#
# Snippet class & subclasses #
#----------------------------#

class Snippet(specifications.TestGroup):
    """
    Common functionality for snippets. Don't instantiate this class;
    instead use one of the subclasses `Variables`, `Expressions`, or
    `RunModule`.

    Note that a `Snippet` is a `potluck.specifications.TestGroup`, from
    which it inherits a powerful interface for customizing behavior. Some
    default modifications are applied to every snippet:

    1. Output, including stderr and error tracebacks, is captured.
    2. A setup function is run which disables turtle tracing, wavesynth
        track playing/saving, and optimism colors (only when the relevant
        module(s) are available). A cleanup function that reverses all of
        these changes except the turtle speed is also run afterwards.
    """
    @staticmethod
    def base_context(task_info):
        """
        Creates a base context object for a snippet, given a task info
        object.
        """
        return {
            "task_info": task_info,
            "username": "__soln__",
            "submission_root": task_info["specification"].soln_path,
            "default_file": task_info["target"],
            "actual_file": task_info["target"]
        }

    def __init__(
        self,
        sid,
        title,
        caption,
        tests,
        postscript='',
        glamers=None,
        ignore_errors=False
    ):
        """
        All `Snippet`s have a snippet ID, a title, a caption, and one or
        more tests. `tests` must be an iterable of unregistered
        `potluck.specifications.TestCase` objects.

        An optional postscript is markdown source to be placed after the
        code block.

        An optional list of glamer functions may be provided. These will
        be given individual pieces of HTML code and the associated
        context those were rendered from and their result value will
        replace the HTML code to be used; they are applied in-order.

        Unless ignore_errors is set to False (default is True), errors
        generated by the base payload and captured along with output will
        be logged under the assumption that in most cases an exception in
        a snippet is a bug with the snippet code rather than intentional.
        """
        # Set ourselves up as a TestGroup...
        super().__init__(sid, '_')

        # We store our arguments
        self.title = title
        self.caption = caption
        self.postscript = postscript
        self.glamers = glamers or []
        self.ignore_errors = ignore_errors

        # Final edit function to manipulate the context to be rendered
        self.editor = None

        # What's the name of our spec file?
        self.spec_file = file_utils.get_spec_file_name()

        # Add our tests to ourself
        for t in tests:
            self.add(t)

        # Fetch the defining-module-specific registry
        reg = SNIPPET_REGISTRY.setdefault(
            file_utils.get_spec_module_name(),
            {}
        )

        # Prevent ID collision
        if sid in reg:
            raise ValueError(
                "Multiple snippets cannot be registered with the same"
                " ID ('{sid}')."
            )

        # Register ourself
        reg[sid] = self

        # A place to cache our compiled result
        self.cached_for = None
        self.cached_value = None

        # Set up default augmentations
        self.capture_output(capture_errors=True, capture_stderr=True)
        self.do_setup(snippet_setup)
        self.do_cleanup(snippet_cleanup)

    def provide(self, vars_map):
        """
        A convenience function for providing the snippet with values not
        defined in the solution module. Under the hood, this uses
        `specifications.HasPayload.use_decorations`, so using that
        alongside this will not work (one will overwrite the other). This
        also means that you cannot call `provide` multiple times on the
        same instance to accumulate provided values: each call discards
        previous provided values.
        """
        self.use_decorations(
            {
                k: (lambda _: v)
                for (k, v) in vars_map.items()
            },
            ignore_missing=True
        )

    # TODO: define replacements so that formatting of calls can use
    # varnames?

    def compile(self, base_context):
        """
        Runs the snippet, collects its results, and formats them as HTML.
        Returns a string containing HTML code for displaying the snippet
        (which assumes that the potluck.css stylesheet will be loaded).

        This method will always re-run the compilation process,
        regardless of whether a cached result is available, and will
        update the cached result. Use `Snippet.get_html` to recompile
        only as needed.

        Requires a base context object (see `potluck.contexts.Context`
        for the required structure).

        The returned HTML's outermost tag is a &lt;section&gt; tag with
        an id that starts with 'snippet:' and then ends with the
        snippet's ID value.
        """
        # Set up traceback-rewriting for the specifications module we
        # were defined in
        html_tools.set_tb_rewrite(
            base_context["task_info"]["specification"].__file__,
            "<task specification>"
        )
        html_tools.set_tb_rewrite(
            base_context["submission_root"],
            "<solution>"
        )

        # Tell the run_for_base_and_ref_values augmentation to run only
        # for ref values.
        self.augmentations.setdefault(
            "run_for_base_and_ref_values",
            {}
        )["ref_only"] = True

        for case in self.tests:
            case.augmentations.setdefault(
                "run_for_base_and_ref_values",
                {}
            )["ref_only"] = True

        # Create our Goal object
        goal = self.provide_goal()

        # Reset and evaluate our goal:
        goal.reset_network()
        goal.evaluate(base_context)

        # Grab the contexts that were used for each test
        if goal.test_in and len(goal.test_in["contexts"]) > 0:
            contexts = goal.test_in["contexts"]
        else:
            # This shouldn't be possible unless an empty list of
            # variables or functions was provided...
            raise ValueError(
                "A Snippet must have at least one context to compile."
                " (Did you pass an empty list to Variables or"
                " FunctionCalls?)"
            )

        # Translate from markdown
        title = render.render_markdown(self.title)
        caption = render.render_markdown(self.caption)
        post = render.render_markdown(self.postscript)

        context_dicts = []
        for ctx in contexts:
            try:
                cdict = ctx.create(base_context)
            except context_utils.ContextCreationError:
                cdict = {
                    # for RunModule snippets (note no ref_)
                    "filename": "UNKNOWN",
                    # In case it's a Variables snippet
                    "ref_variable": "UNKNOWN",
                    # for FunctionCalls snippets
                    "ref_function": "UNKNOWN",
                    "ref_args": (),
                    "ref_kwargs": {},
                    # for Blocks snippets
                    "ref_block": "UNKNOWN",
                    # For all kinds of snippets
                    "ref_value": "There was an error compiling this snippet.",
                    "ref_output": "There was an error compiling this snippet.",
                    "ref_error_log": html_tools.string_traceback()
                }
            context_dicts.append(cdict)

        # Strip out solution file paths from output, and perform final
        # edits if we have an editor function
        soln_path = os.path.abspath(
            base_context["task_info"]["specification"].soln_path
        )
        for context in context_dicts:
            if (
                "ref_output" in context
            and soln_path in context["ref_output"]
            ):
                context["ref_output"] = context["ref_output"].replace(
                    soln_path,
                    '&lt;soln&gt;'
                )

            if (
                "ref_error_log" in context
            and soln_path in context["ref_error_log"]
            ):
                context["ref_error_log"] = context["ref_error_log"].replace(
                    soln_path,
                    '&lt;soln&gt;'
                )

            if self.editor:
                self.editor(context)

        # Include title & caption, and render each context to produce our
        # result
        result = (
            '<section class="snippet" id="snippet:{sid}">'
            '<div class="snippet_title">{title}</div>\n'
            '{caption}\n<pre>{snippet}</pre>\n{post}'
            '</section>'
        ).format(
            sid=self.base_name,
            title=title,
            caption=caption,
            post=post,
            snippet=''.join(
                self.compile_context(cd)
                for cd in context_dicts
            )
        )

        self.cached_for = base_context["task_info"]["id"]
        self.cached_value = result

        return result

    def compile_context(self, context):
        """
        Turns a context dictionary resulting from an individual snippet
        case into HTML code for displaying that result, using
        `render_context` but also potentially adding additional HTML for
        extra context slots (see e.g., `show_image` and `play_audio`).
        """
        if not self.ignore_errors and "ref_error" in context:
            logging.log(
                "Error captured by context creation:\n"
              + context["ref_error"]
              + "\nFull log is:\n"
              + context.get("ref_error_log", '<missing>')
            )
        result = self.render_context(context)
        for glamer in self.glamers:
            result = glamer(result, context)

        return result

    def render_context(self, context):
        """
        Override this to define how a specific Snippet sub-class should
        render a context dictionary into HTML code.
        """
        raise NotImplementedError(
            "Snippet is abstract and context rendering is only available"
            " via overrides in sub-classes."
        )

    def get_html(self, task_info):
        """
        Returns the snippet value, either cached or newly-compiled
        depending on the presence of an appropriate cached value.
        """
        if self.cached_for == task_info["id"]:
            return self.cached_value
        else:
            return self.compile(Snippet.base_context(task_info))

    def final_edit(self, editor):
        """
        Sets up a function to be run on each created context just before
        that context gets rendered. The editor may mutate the context it
        is given in order to change what gets rendered. Multiple calls to
        this function each simply replace the previous editor function.

        Note that the ref_* values from the context are used to create
        the snippet.
        """
        self.editor = editor

    def show_image(self):
        """
        Adds a glamer that augments output by appending a "Image "
        prompt followed by an image element which shows the contents of
        the "ref_image" context slot. To establish a "ref_image" slot,
        call a method like
        `potluck.specifications.HasPayload.capture_turtle_image`.

        Returns self for chaining.
        """
        self.glamers.append(append_image_result)
        return self

    def play_audio(self):
        """
        Adds a glamer that augments output by appending an "Audio "
        prompt followed by an audio element which plays the contents of
        the "ref_audio" context slot. To make an "ref_audio" slot, call a
        method like
        `potluck.specifications.HasPayload.capture_wavesynth`.

        Returns self for chaining.
        """
        self.glamers.append(append_audio_result)
        return self

    def show_file_contents(self):
        """
        Adds a glamer that augments output by appending a "File"
        prompt followed by a text box showing the filename and the
        contents of that file. Requires 'ref_output_filename' and
        'ref_output_file_contents' slots, which could be established
        using a method like
        `potluck.specifications.HasPayload.capture_file_contents`

        Returns self for chaining.
        """
        self.glamers.append(append_file_contents)
        return self


def highlight_code(code):
    """
    Runs pygments highlighting but converts from a div/pre/code setup
    back to just a code tag with the 'highlight' class.
    """
    markup = pygments.highlight(
        code,
        pygments.lexers.PythonLexer(),
        pygments.formatters.HtmlFormatter()
    )
    # Note: markup will start a div and a pre we want to get rid of
    start = '<div class="highlight"><pre>'
    end = '</pre></div>\n'
    if markup.startswith(start):
        markup = markup[len(start):]
    if markup.endswith(end):
        markup = markup[:-len(end)]

    return '<code class="highlight">{}</code>'.format(markup)


class Variables(Snippet):
    """
    A snippet which shows the definition of one or more variables. Use
    this to display examples of input data, especially when you want to
    use shorter expressions in examples of running code. If you want to
    use variables that aren't defined in the solution module, use the
    `Snippet.provide` method (but note that that method is incompatible
    with using `specifications.HasPayload.use_decorations`).
    """
    def __init__(self, sid, title, caption, varnames, postscript=''):
        """
        A snippet ID, a title, and a caption are required, as is a list
        of strings indicating the names of variables to show definitions
        of. Use `Snippet.provide` to supply values for variables not in
        the solution module.

        A postscript is optional (see `Snippet`).
        """
        cases = [
            specifications.TestValue(
                varname,
                register=False
            )
            for varname in varnames
        ]
        super().__init__(sid, title, caption, cases, postscript)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        the definition of a variable, including Jupyter-notebook-style
        prompts.
        """
        varname = extract(context, "ref_variable")
        value = extract(context, "ref_value")

        # format value's repr using wrapped_repr, but leaving room for
        # varname = at beginning of first line
        rep = wrapped_with_prefix(value, varname + ' = ')

        # Use pygments to generate HTML markup for our assignment
        markup = highlight_code(rep)
        return (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">{}</div>\n'
        ).format(markup)


class RunModule(Snippet):
    """
    A snippet which shows the output produced by running a module.
    Functions like `potluck.specifications.HasPayload.provide_inputs`
    can be used to control exactly what happens.

    The module to import is specified by the currently active file
    context (see `potluck.contexts.FileContext`).
    """
    def __init__(self, sid, title, caption, postscript=''):
        """
        A snippet ID, title, and caption are required.

        A postscript is optional (see `Snippet`).
        """
        cases = [ specifications.TestImport(register=False) ]
        super().__init__(sid, title, caption, cases, postscript)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        running a module. Includes a Jupyter-style prompt with %run magic
        syntax to show which file was run.
        """
        filename = extract(context, "filename") # Note: no ref_ here
        captured = context.get("ref_output", '')
        captured_errs = context.get("ref_error_log", '')

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        result = (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">'
            '<code class="magic">%run {filename}</code>'
            '</div>\n'
        ).format(filename=filename)
        if captured:
            result += (
                '<span class="prompt printed">Prints</span>'
                '<div class="snippet-printed">{captured}</div>\n'
            ).format(captured=captured)
        if captured_errs:
            result += (
                '<span class="prompt stderr">Logs</span>'
                '<div class="snippet-stderr">{log}</div>\n'
            ).format(log=captured_errs)

        return result


class FunctionCalls(Snippet):
    """
    A snippet which shows the results (printed output and return values)
    of calling one or more functions. To control what happens in detail,
    use specialization methods from `potluck.specifications.HasPayload`
    and `potluck.specifications.HasContext`.
    """
    def __init__(self, sid, title, caption, calls, postscript=''):
        """
        A snippet ID, title, and caption are required, along with a list
        of function calls. Each entry in the list must be a tuple
        containing a function name followed by a tuple of arguments,
        and optionally, a dictionary of keyword arguments.

        A postscript is optional (see `Snippet`).
        """
        cases = [
            specifications.TestCase(
                fname,
                args,
                kwargs or {},
                register=False
            )
            for fname, args, kwargs in (
                map(lambda case: (case + (None,))[:3], calls)
            )
        ]
        super().__init__(sid, title, caption, cases, postscript)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        calling a function. Includes a Jupyter-style prompt for input as
        well as the return value.
        """
        if "ref_error" in context:
            print(
                "Error during context creation:"
              + context["ref_error"]
              + "\nFull log is:\n"
              + context.get("ref_error_log", '<missing>')
            )
        fname = context["ref_function"]
        value = context["ref_value"]
        args = context["ref_args"]
        kwargs = context["ref_kwargs"]
        captured = context.get("ref_output", '')
        captured_errs = context.get("ref_error_log", '')

        # Figure out representations of each argument
        argreps = []
        for arg in args:
            argreps.append(wrapped_with_prefix(arg, '', 1))

        for kw in kwargs:
            argreps.append(wrapped_with_prefix(kwargs[kw], kw + "=", 1))

        # Figure out full function call representation
        oneline = "{}({})".format(
            fname,
            ', '.join(rep.strip() for rep in argreps)
        )
        if '\n' not in oneline and len(oneline) <= FMT_WIDTH:
            callrep = oneline
        else:
            callrep = "{}(\n{}\n)".format(fname, ',\n'.join(argreps))

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        # Highlight the function call
        callrep = highlight_code(callrep)

        result = (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">{}</div>'
        ).format(callrep)

        if captured:
            result += (
                '<span class="prompt printed">Prints</span>'
                '<div class="snippet-printed">{}</div>\n'
            ).format(captured)

        if captured_errs:
            result += (
                '<span class="prompt stderr">Logs</span>'
                '<div class="snippet-stderr">{log}</div>\n'
            ).format(log=captured_errs)

        # Highlight the return value
        if value is not None:
            value = highlight_code(wrapped_with_prefix(value, ""))

            result += (
                '<span class="prompt output">Out[]:</span>'
                '<div class="snippet-output">{}</div>\n'
            ).format(value)

        return result


class Blocks(Snippet):
    """
    A snippet which shows the results (printed output and result value of
    final line) of one or more blocks of statements, just like Jupyter
    Notebook cells. To control what happens in detail, use specialization
    methods from `potluck.specifications.HasPayload` and
    `potluck.specifications.HasContext`.

    Note: Any direct side-effects of the blocks (like changing the value
    of a variable or defining a function) won't persist in the module
    used for evaluation. However, indirect effects (like appending to a
    list) will persist, and thus should be avoided because they could
    have unpredictable effects on other components of the system such as
    evaluation.

    Along the same lines, each block of code to demonstrate is executed
    independently of the others. You cannot define a variable in one
    block and then use it in another (although you could fake this using
    the ability to define separate presentation and actual code).
    """
    def __init__(self, sid, title, caption, blocks, postscript=''):
        """
        A snippet ID, title, and caption are required, along with a list
        of code blocks. Each entry in the list should be either a
        multi-line string, or a tuple of two such strings. In the first
        case, the string is treated as the code to run, in the second,
        the first item in the tuple is the code to display, while the
        second is the code to actually run.

        A postscript is optional (see `Snippet`).
        """
        cases = []
        for item in blocks:
            if isinstance(item, str):
                cases.append(
                    specifications.TestBlock(
                        sid,
                        item,
                        register=False
                    )
                )
            else:
                display, actual = item
                cases.append(
                    specifications.TestBlock(
                        sid,
                        display,
                        actual,
                        register=False
                    )
                )

        super().__init__(sid, title, caption, cases, postscript)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        executing a block of code. Includes a Jupyter-style prompt for
        input as well as the result value of the last line of the block
        as long as that's not None.
        """
        src = extract(context, "ref_block")
        value = extract(context, "ref_value")
        captured = context.get("ref_output", '')
        captured_errs = context.get("ref_error_log", '')

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        # Highlight the code block
        blockrep = highlight_code(src)

        result = (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">{}</div>\n'
        ).format(blockrep)

        if captured:
            result += (
                '<span class="prompt printed">Prints</span>'
                '<div class="snippet-printed">{}</div>\n'
            ).format(captured)

        if captured_errs:
            result += (
                '<span class="prompt stderr">Logs</span>'
                '<div class="snippet-stderr">{log}</div>\n'
            ).format(log=captured_errs)

        # Highlight the return value
        if value is not None:
            value = highlight_code(wrapped_with_prefix(value, ""))

            result += (
                '<span class="prompt output">Out[]:</span>'
                '<div class="snippet-output">{}</div>\n'
            ).format(value)

        return result


class Fakes(Snippet):
    """
    One or more fake snippets, which format code, printed output, stderr
    output, and a result value (and possibly glamer additions) but each
    of these things is simply specified ahead of time. Note that you want
    to avoid using this if at all possible, because it re-creates the
    problems that this module was trying to solve (namely, examples
    becoming out-of-sync with the solution code). The specialization
    methods of this kind of snippet are ignored and have no effect,
    because no code is actually run.
    """
    def __init__(self, sid, title, caption, fake_contexts, postscript=''):
        """
        A snippet ID, title, and caption are required, along with a list
        of fake context dictionary objects to be rendered as if they came
        from a real test. Each dictionary must contain a "code" slot, and
        may contain "ref_value", "ref_output", and/or "ref_error_log"
        keys. If using glamers, relevant keys should be added directly to
        these fake contexts.

        If "ref_value" or "ref_output" slots are missing, defaults of
        None and '' will be added, since these slots are ultimately
        required.

        A postscript is optional (see `Snippet`).
        """
        self.fake_contexts = fake_contexts
        for ctx in self.fake_contexts:
            if 'code' not in ctx:
                raise ValueError(
                    "Fake context dictionaries must contain a 'code'"
                    " slot."
                )
            if 'ref_value' not in ctx:
                ctx['ref_value'] = None
            if 'ref_output' not in ctx:
                ctx['ref_output'] = ''
        super().__init__(sid, title, caption, [], postscript)

    def create_goal(self):
        """
        We override TestGroup.create_goal to just create a dummy goal
        which depends on dummy contexts.
        """
        ctx_list = []
        for fake in self.fake_contexts:
            def make_builder():
                """
                We need to capture 'fake' on each iteration of the loop,
                which is why this extra layer of indirection is added.
                """
                nonlocal fake
                return lambda _: fake
            ctx_list.append(contexts.Context(builder=make_builder()))

        return rubrics.NoteGoal(
            self.taskid,
            "fakeSnippetGoal:" + self.base_name,
            (
                "NoteGoal for fake snippet '{}'.".format(self.base_name),
                "A fake NoteGoal."
            ),
            test_in={ "contexts": ctx_list }
        )

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        executing a block of code. Includes a Jupyter-style prompt for
        input as well as the result value of the last line of the block
        as long as that's not None.
        """
        src = extract(context, "code")
        value = extract(context, "ref_value")
        captured = context.get("ref_output", '')
        captured_errs = context.get("ref_error_log", '')

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        # Highlight the code block
        blockrep = highlight_code(src)

        result = (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">{}</div>\n'
        ).format(blockrep)

        if captured:
            result += (
                '<span class="prompt printed">Prints</span>'
                '<div class="snippet-printed">{}</div>\n'
            ).format(captured)

        if captured_errs:
            result += (
                '<span class="prompt stderr">Logs</span>'
                '<div class="snippet-stderr">{log}</div>\n'
            ).format(log=captured_errs)

        # Highlight the return value
        if value is not None:
            value = highlight_code(wrapped_with_prefix(value, ""))

            result += (
                '<span class="prompt output">Out[]:</span>'
                '<div class="snippet-output">{}</div>\n'
            ).format(value)

        return result


class Files(Snippet):
    """
    A snippet which shows the contents of one or more files, without
    running any code, in the same Jupyter-like format that file contents
    are shown when `Snippet.show_file_contents` is used. Most
    specialization methods don't work properly on this kind of snippet.

    By default, file paths are interpreted as relative to the solutions
    directory, but specifying a different base directory via the
    constructor can change that.
    """
    def __init__(
        self,
        sid,
        title,
        caption,
        filepaths,
        base='__soln__',
        postscript=''
    ):
        """
        A snippet ID, title, and caption are required, along with a list
        of file paths. Each entry in the list should be a string path to
        a starter file relative to the starter directory. The versions of
        files in the solution directory will be used. But only files
        present in both starter and solution directories will be
        available.

        If `base` is specified, it should be either '__soln__' (the
        default), '__starter__', or a path string. If it's __soln__ paths
        will be interpreted relative to the solution directory; if it's
        __starter__ they'll be interpreted relative to the starter
        directory, and for any other path, paths are interpreted relative
        to that directory. In any case, absolute paths will not be
        modified.

        A postscript is optional (see `Snippet`).
        """
        if base == "__soln__":
            base = file_utils.current_solution_path()
        elif base == "__starter__":
            base = file_utils.current_starter_path()
        # else leave base as-is

        self.filepaths = {
            path: os.path.join(base, path)
            for path in filepaths
        }

        super().__init__(sid, title, caption, [], postscript)

    def create_goal(self):
        """
        We override TestGroup.create_goal to just create a dummy goal
        which depends on dummy contexts.
        """
        ctx_list = []
        for showpath in self.filepaths:
            filepath = self.filepaths[showpath]
            with open(filepath, 'r', encoding="utf-8") as fileInput:
                contents = fileInput.read()

            def make_builder():
                """
                We need to capture 'filepath' on each iteration of the
                loop, which is why this extra layer of indirection is
                added.
                """
                nonlocal showpath, filepath, contents
                sp = showpath
                fp = filepath
                ct = contents
                return lambda _: {
                    "path": sp,
                    "real_path": fp,
                    "contents": ct
                }

            ctx_list.append(contexts.Context(builder=make_builder()))

        return rubrics.NoteGoal(
            self.taskid,
            "fileSnippetGoal:" + self.base_name,
            (
                "NoteGoal for file snippet '{}'.".format(self.base_name),
                "A file-displaying NoteGoal."
            ),
            test_in={ "contexts": ctx_list }
        )

    def render_context(self, context):
        """
        Renders a context with just file information as HTML markup for
        displaying a file with %more magic. Includes a Jupyter-style
        prompt for input as well as the contents of the file.
        """
        path = extract(context, "path")
        contents = extract(context, "contents")

        result = (
            '<span class="prompt input">In []:</span>'
            '<div class="snippet-input">'
            '<code class="magic">%more {filename}</code>'
            '</div>\n'
            '<span class="prompt special">File</span>'
            '<div class="snippet-filename">{filename}</div>\n'
            '<div class="snippet-file-contents">{contents}</div>\n'
        ).format(filename=path, contents=contents)

        return result


#---------#
# Glamers #
#---------#

def append_image_result(markup, context):
    """
    Given some HTML markup and a context dictionary, turns the
    "ref_image" context slot into an HTML img tag and returns the given
    markup with that appended, prefixed by an "Image " prompt. If the
    context has no "image" value, the original markup is returned
    unmodified.

    The "ref_image_alt" slot of the context is used as alt text for the
    image, with the "ref_output" slot being used as backup (under a
    hopeful assumption about turtleBeads being imported for printed
    descriptions). If neither is present, "no alt text available" will be
    used.
    """
    # Short-circuit unless we've got an image
    if "ref_image" not in context:
        return markup

    image = extract(context, "ref_image")
    alt = context.get(
        "ref_image_alt",
        context.get("ref_output", "no alt text available")
    )

    img_tag = html_tools.html_image(image, alt, ["example"])
    return (
        markup
      + '<span class="prompt special">Image </span>'
      + img_tag
    )


def append_audio_result(markup, context):
    """
    Given some HTML markup and a context dictionary, turns the
    "ref_audio" context slot into an HTML audio tag and returns the given
    markup with that appended, prefixed by an "Audio " prompt.

    Note that this can result in a pretty large string if the WAV format
    is used, since the string needs to be base64-encoded and WAV is
    uncompressed (and we double the size by including the data URL twice)
    :(

    TODO: Maybe use Ogg/Vorbis?

    If there is no "ref_audio" context slot, the given markup is returned
    unmodified.

    The "ref_audio" context value must be a dictionary with at least
    "mimetype" and "data" slots containing the MIME type for the data and
    the data itself (as a bytes object). It may also include a "label"
    slot which will be used invisibly as an aria-label property of the
    audio element; if absent no aria-label will be attached.
    """
    # Short-circuit unless we've got audio
    if "ref_audio" not in context:
        return markup

    audio = extract(context, "ref_audio")
    mime = audio["mimetype"]
    data = audio["data"]
    label = audio.get("label")

    audio_tag = html_tools.html_audio(data, mime, label)
    return (
        markup
      + '\n<span class="prompt special">Audio </span>'
      + audio_tag
    )


def append_file_contents(markup, context):
    """
    Given some HTML markup and a context dictionary, turns the
    "ref_output_filename" and "ref_output_file_contents" context slots
    into HTML markup displaying the contents of that file, which gets
    appended to the given markup and returned.

    Note that this is intended to display the contents of text files.

    If either of the "ref_output_filename" or "ref_output_file_contents"
    context slots are missing, the given markup is returned unmodified.
    """
    # Short-circuit unless we've got output file contents
    if (
        "ref_output_filename" not in context
     or "ref_output_file_contents" not in context
    ):
        return markup

    filename = extract(context, "ref_output_filename")
    contents = extract(context, "ref_output_file_contents")

    return (
        markup
      + (
            '\n<span class="prompt special">File</span>'
        )
      + '<div class="snippet-filename">{}</div>\n'.format(filename)
      + '<div class="snippet-file-contents">{}</div>\n'.format(contents)
    )


#--------#
# Lookup #
#--------#

def list_snippets(task_info):
    """
    Returns a list containing all snippet IDs (strings) for the given
    task (as a task info dictionary).
    """
    reg = SNIPPET_REGISTRY.get(task_info["specification"].__name__, {})
    return list(reg.keys())


def get_html(task_info, sid):
    """
    Retrieves the HTML code (a string) for the snippet with the given ID
    in the given task (as a task info dictionary). Returns None if there
    is no such snippet.
    """
    reg = SNIPPET_REGISTRY.get(task_info["specification"].__name__, {})
    if sid not in reg:
        return None
    return reg[sid].get_html(task_info)


def get_all_snippets(task_info):
    """
    Returns a list of HTML strings containing each registered snippet for
    the given (as a task_info dictionary) task.
    """
    return [
        get_html(task_info, sid)
        for sid in list_snippets(task_info)
    ]
