"""
Tools for generating reports and managing jinja2 templates.

render.py
"""

import os
import sys
import json
import base64

import markdown
import jinja2
import pygments
import pygments.lexers
import pygments.formatters
import importlib_resources
import bs4

from . import logging
from . import html_tools
from . import time_utils


#-------------------#
# 2/3 compatibility #
#-------------------#

if sys.version_info[0] < 3:
    ModuleNotFound_or_Import_Error = ImportError
else:
    ModuleNotFound_or_Import_Error = ModuleNotFoundError

#---------#
# Globals #
#---------#

J2_ENV = None
"""
The global Jinja2 Environment.
"""


RESOURCES_DIR = None
"""
The global resource directory.
"""


BLANK_RUBRIC_TEMPLATE = "rubric.j2"
"""
The template name for blank rubrics.
"""

EVALUATION_REPORT_TEMPLATE = "standalone_report.j2"
"""
The template name for evaluation reports.
"""

TESTS_EVALUATION_REPORT_TEMPLATE = "standalone_tests_report.j2"
"""
The template name for tests evaluation reports.
"""

STANDALONE_INSTRUCTIONS_TEMPLATE = "standalone_instructions.j2"
"""
The template name for standalone instructions.
"""

INSTRUCTIONS_TEMPLATE = "instructions.j2"
"""
The template name for instructions (to be included in an HTML wrapper).
"""

ERROR_MSG = "FAILED TO COMPLETE"
"""
The message that will be logged if an error occurs during evaluation.
"""

DONE_MSG = "completed successfully"
"""
The message that will be printed if evaluation completes successfully.
"""


#-----------------------------------#
# Setup & template/resource loading #
#-----------------------------------#

def register_filter(name, filter_function):
    """
    Registers a function for use in jinja2 templates as a filter.
    """
    J2_ENV.filters[name] = filter_function


def setup(templates_directory=None, resources_directory=None):
    """
    Sets up for report generation. Template and resources directories
    are optional, with resources loaded from this package by default.
    """
    global J2_ENV, RESOURCES_DIR

    # Remember resources directory
    RESOURCES_DIR = resources_directory

    # Decide on loader type
    if templates_directory is None:
        loader = jinja2.PackageLoader('potluck', 'templates')
    else:
        loader = jinja2.FileSystemLoader(templates_directory)

    # Set up Jinja2 environment
    J2_ENV = jinja2.Environment(loader=loader, autoescape=False)

    # Register custom Jinja2 filters
    register_filter("fileslug", html_tools.fileslug)
    register_filter("at_time", time_utils.at_time)


def get_css():
    """
    Returns the CSS code for reports as a string.
    """
    if RESOURCES_DIR is None:
        pkg_files = importlib_resources.files("potluck") / "resources"
        return pkg_files.joinpath("potluck.css").read_text(encoding="utf-8")
    else:
        with open(os.path.join(RESOURCES_DIR, "potluck.css")) as fin:
            return fin.read()


def get_js():
    """
    Returns the Javascript code for reports as a string.
    """
    if RESOURCES_DIR is None:
        pkg_files = importlib_resources.files("potluck") / "resources"
        return pkg_files.joinpath("potluck.js").read_text(encoding="utf-8")
    else:
        with open(os.path.join(RESOURCES_DIR, "potluck.js")) as fin:
            return fin.read()


def load_template(template_name):
    """
    Loads a template by name (a relative path within the configured
    templates directory).
    """
    try:
        return J2_ENV.get_template(template_name)
    except jinja2.exceptions.TemplateSyntaxError as e:
        logging.log(
            (
                "Syntax error while building Jinja2 template:"
                " '{template_name}'\n"
                "Error occurred on line: {lineno}\n"
                "Error was: {error}\n"
                '-' * 80
            ).format(
                template_name=template_name,
                lineno=e.lineno,
                error=str(e)
            )
        )
        raise
    except Exception as e:
        logging.log(
            (
                "Unexpected non-syntax error while building Jinja2"
                " template: '{template_name}'\n"
                "Error was: {error}\n"
                '-' * 80
            ).format(
                template_name=template_name,
                error=str(e)
            )
        )
        raise


#-----------------------------#
# Generic Markdown Conversion #
#-----------------------------#

def render_markdown(md_source):
    """
    Renders markdown as HTML. Uses pymdownx.extra extensions if
    available, otherwise normal markdown.extra.
    """
    try:
        import pymdownx # noqa F401
        x = 'pymdownx.extra'
    except ModuleNotFound_or_Import_Error:
        x = 'extra'

    try:
        # Try to render with extensions
        result = markdown.markdown(md_source, extensions=[x])
        return result
    except Exception:
        # Backup: try without extensions, since in some cases they don't
        # work I guess :(
        print("Error rendering markdown with extensions:")
        print(html_tools.string_traceback())
        return markdown.markdown(md_source, extensions=[])


#-----------------------------#
# Rendering rubrics & reports #
#-----------------------------#

def render_blank_rubric(blank_report, output_file):
    """
    Renders a blank rubric report as HTML into the specified file. The
    report should come from `potluck.rubrics.Rubric.create_blank_report`.
    """
    # Load our report template
    template = load_template(BLANK_RUBRIC_TEMPLATE)

    # Augment the given blank report object
    augment_report(blank_report, blank=True)

    # Render the report to the output file
    with open(output_file, 'w', encoding="utf-8") as fout:
        fout.write(template.render(blank_report))


def render_report(
    report,
    instructions,
    snippets,
    output_file,
    html_output_file
):
    """
    Renders an evaluation report object as JSON into the specified output
    file, and as HTML into the specified html output file. The report
    should come from `potluck.rubrics.Rubric.evaluate`. In addition to
    the report, instructions markdown source and a list of HTML snippets
    are necessary.
    """
    # Load our report template
    template = load_template(EVALUATION_REPORT_TEMPLATE)

    # Add a timestamp to our report object
    report["timestamp"] = time_utils.timestring()

    # Render the basic report to the JSON output file
    with open(output_file, 'w', encoding="utf-8") as fout:
        json.dump(report, fout)

    # Augment the rubric report object with pre-rendered HTML stuff
    augment_report(report)

    # Render the HTML report to the html output file
    with open(html_output_file, 'w', encoding="utf-8") as fout:
        fout.write(
            template.render(
                report=report,
                instructions=instructions,
                snippets=snippets
            )
        )


def render_tests_report(
    report,
    output_file,
    html_output_file
):
    """
    Renders a tests validation report object as JSON into the specified
    output file, and as HTML into the specified html output file. The
    report should come from `potluck.rubrics.Rubric.validate_tests`.
    """
    # Load our report template
    template = load_template(TESTS_EVALUATION_REPORT_TEMPLATE)

    # Add a timestamp to our report object
    report["timestamp"] = time_utils.timestring()

    # Render the basic report to the JSON output file
    with open(output_file, 'w', encoding="utf-8") as fout:
        json.dump(report, fout)

    # TODO: Do we need to render any parts of the report as HTML?

    # Render the HTML report to the html output file
    with open(html_output_file, 'w', encoding="utf-8") as fout:
        fout.write(template.render(report=report))


#------------------------#
# Rendering instructions #
#------------------------#

def render_instructions(
    task_info,
    instructions,
    rubric_table,
    snippets,
    output_file,
    standalone=True,
    report_rubric_link_coverage=False
):
    """
    Renders instructions in an HTML template and combines them with a
    rubric table and snippets into one document.

    Requires a task_info dictionary, an HTML string for the instructions
    themselves, a blank rubric table for creating the rubric, and a list
    of snippet HTML code fragments for creating the examples section.

    The output file must be specified, and if you want to produce an HTML
    fragment (without CSS or JS) instead of a standalone HTML file you
    can pass standalone=False.

    If report_rubric_link_coverage is set to True, messages about an
    rubric goals which aren't linked to anywhere in the instructions will
    be printed.
    """
    # Load our report template
    if standalone:
        template = load_template(STANDALONE_INSTRUCTIONS_TEMPLATE)
    else:
        template = load_template(INSTRUCTIONS_TEMPLATE)

    # Get a timestamp
    timestamp = time_utils.timestring()

    # Augment our rubric table
    augment_report(rubric_table, blank=True)

    # Render the HTML instructions
    rendered = template.render(
        taskid=task_info["id"],
        task_info=task_info,
        timestamp=timestamp,
        instructions=instructions,
        rendered_rubric=rubric_table["rendered_table"],
        snippets=snippets,
        css=get_css(),
        js=get_js()
    )

    # Check link coverage
    if report_rubric_link_coverage:
        # Find all anchor links
        linked_to = set()
        soup = bs4.BeautifulSoup(rendered, "html.parser")
        for link in soup.find_all('a'):
            ref = link.get('href')
            if isinstance(ref, str) and ref.startswith('#goal:'):
                linked_to.add(ref[1:])

        # Find all goal IDs:
        core_ids = set()
        extra_ids = set()
        other_ids = set()
        soup = bs4.BeautifulSoup(
            rubric_table["rendered_table"],
            "html.parser"
        )
        for node in soup.find_all(
            lambda tag: (
                tag.has_attr('id')
            and tag.get('id').startswith('goal:')
            )
        ):
            parent_classes = node.parent.get('class', [])
            if 'tag-category-core' in parent_classes:
                core_ids.add(node['id'])
            elif 'tag-category-extra' in parent_classes:
                extra_ids.add(node['id'])
            else:
                other_ids.add(node['id'])

        core_unlinked = core_ids - linked_to
        extra_unlinked = extra_ids - linked_to
        other_unlinked = other_ids - linked_to

        invalid_links = linked_to - (core_ids | extra_ids | other_ids)

        total_unlinked = (
            len(core_unlinked)
          + len(extra_unlinked)
          + len(other_unlinked)
        )

        # Report on goals not linked
        if total_unlinked == 0:
            print("All goals were linked to from the instructions.")
        else:
            print(
                (
                    "{} goal(s) were not linked to from the"
                    " instructions:"
                ).format(total_unlinked)
            )
            if len(core_unlinked) > 0:
                print("Core goals that weren't linked:")
                for goal in sorted(core_unlinked):
                    print('  ' + goal)

            if len(extra_unlinked) > 0:
                print("Extra goals that weren't linked:")
                for goal in sorted(extra_unlinked):
                    print('  ' + goal)

            if len(other_unlinked) > 0:
                print("Other goals that weren't linked:")
                for goal in sorted(other_unlinked):
                    print('  ' + goal)

        # Report on invalid links last
        if len(invalid_links) == 0:
            print("All links to rubric goals were valid.")
        else:
            print(
                (
                    "{} link(s) to rubric goal(s) were invalid:"
                ).format(len(invalid_links))
            )
            for inv in sorted(invalid_links):
                print('  ' + inv)

    # Save to the output file
    with open(output_file, 'w', encoding="utf-8") as fout:
        fout.write(rendered)


#-------------------#
# Rendering helpers #
#-------------------#


def augment_report(report, blank=False):
    """
    Adds the following keys to the given rubric report:

    - 'rendered_table' - HTML code representing the report's table
    - 'rendered_contexts' - HTML code representing the report's contexts
        list
    - 'css' - CSS code for reports
    - 'js' - JavaScript code for reports

    For each file dictionary in the 'files' slot, it also adds:

    - 'code_html' - a rendering of the file's submitted code as HTML

    (but only if that file has a "code" slot).
    """
    if "files" in report:
        for file_entry in report["files"]:
            if "original_code" in file_entry:
                # We render the fixed code, but encode the original
                file_entry["base64"] = base64.standard_b64encode(
                    file_entry["original_code"].encode("utf-8")
                ).decode("utf-8")
                file_entry["code_html"] = render_code(
                    report["taskid"],
                    file_entry["filename"],
                    file_entry["code"]
                )
            elif "code" in file_entry:
                # Render & encode the same code
                file_entry["base64"] = base64.standard_b64encode(
                    file_entry["code"].encode("utf-8")
                ).decode("utf-8")
                file_entry["code_html"] = render_code(
                    report["taskid"],
                    file_entry["filename"],
                    file_entry["code"]
                )
            elif "raw" in file_entry:
                # Encode raw data but don't render anything
                # We won't try to present the file data in any fancy way
                file_entry["base64"] = base64.standard_b64encode(
                    file_entry["raw"].encode("utf-8")
                ).decode("utf-8")
            # File entires should all have either 'raw' or 'code'
            # slots, but if one doesn't, we'll just leave it alone

    if "table" in report:
        report['rendered_table'] = render_rubric_table(
            report["taskid"],
            report["table"],
            blank=blank
        )
    else:
        report["rendered_table"] = "No table found."

    if "contexts" in report:
        # Note: contexts have already been formatted with/without values
        # before this step, so blank can be ignored here.
        report['rendered_contexts'] = render_contexts_list(report["contexts"])
    else:
        report['rendered_contexts'] = "No context information available."

    # Add CSS & JS to report
    report["css"] = get_css()
    report["js"] = get_js()


def render_code(taskid, filename, raw_code):
    """
    Given a task ID, a filename, and a string containing submitted code,
    creates an HTML string containing markup for displaying that code in
    a report. Each line is given a line ID so that other parts of the
    report can reference specific lines of the file.
    """
    if raw_code == '':
        return "<pre># NO CODE AVAILABLE</pre>"

    markup = pygments.highlight(
        raw_code,
        pygments.lexers.PythonLexer(),
        pygments.formatters.HtmlFormatter()
    )

    # TODO: Re-instate some kind of annotation mechanism where code lines
    # can have back-links to annotations that target them?

    highlighted = markup\
        .replace('<div class="highlight"><pre>', '')\
        .replace('</pre></div>', '')

    annotated = '\n'.join(
        annotate_line(taskid, filename, n + 1, line)
        for n, line in enumerate(highlighted.split('\n'))
    )
    return (
        '<pre id="{}">'.format(html_tools.block_id(taskid, filename))
      + annotated
      + '</pre>'
    )


def annotate_line(taskid, filename, lineno, line_html):
    """
    Takes a task ID, a file name, a line number, and a line of
    already-highlighted Python code (an HTML string), and returns the
    same line wrapped in a span which includes a line ID. The returned
    span also includes a `linenum` span before the line text which
    includes a line number.

    These lines will have click handlers added by `resources/potluck.js`
    so that clicking on them will highlight/unhighlight the line.
    """
    lineid = html_tools.line_id(taskid, filename, lineno)
    return (
        '<span id="{lineid}"'
        ' class="codeline codeline_plain">'
        '<span class="linenum">{lineno} </span>'
        ' {line_html}'
        '</span>'
    ).format(
        lineid=lineid,
        lineno=lineno,
        line_html=line_html
    )


def render_rubric_table(taskid, table, blank=False):
    """
    Renders a rubric table for a specific task (from the 'table' slot of
    an evaluation; see `potluck.rubrics.Rubric.evaluate`) as an HTML
    string. Returns an HTML string that builds a div with class
    "rubric_table".

    blank can be set to True (instead of the default False) to make
    rubric details more visible in blank rubrics where explanations
    haven't been generated yet, but it means that explanations will not
    be rendered in the output (warnings and notes still will be). Setting
    blank to True will also cause table rows to display the rubric
    versions of row topics and details even when feedback versions are
    available.
    """
    return '<div class="rubric_table">\n{}\n</div>'.format(
        '\n'.join(
            render_rubric_row(taskid, row, blank)
            for row in table
        )
    )


def render_rubric_row(taskid, row, blank=False):
    """
    Renders a single row of a rubric table for a given task into an HTML
    div (see `render_rubric_table`). The resulting div has class
    "rubric_row", plus an additional class depending on the status of
    the given row with the string 'status_' prefixed and any spaces
    replaced by underscores. There are also 'tag_' classes added for
    each tag that the row has.

    If blank is given as True, the explanation for this row will be
    discarded and replaced by the rubric details, which will then be
    omitted from the topic area. By default (when blank is False), the
    rubric details are available on expansion within the topic div and
    the explanation is put in the assessment area. Also, when blank is
    True, the rubric versions of the topic and details for this row are
    displayed instead of the feedback versions.
    """
    contents = ''

    description = row.get(
        "description",
        ("Unknown", "No description available.")
    )
    if blank:
        topic, details = description[:2]
    else:
        topic = description[::2][-1]
        details = description[1::2][-1]

    topic_class = "topic"
    details_node = ' ' + html_tools.create_help_button(details)
    if blank:
        topic_class += " no_details"
        details_node = ''

    rowid = row.get("id", "")
    contents += (
        '<div {}class="{}" tabindex="0">\n{}\n{}\n{}\n{}\n</div>'
    ).format(
        'id="{}" '.format(rowid) if rowid else '',
        topic_class,
        html_tools.build_status_indicator(row["status"]),
        "<span class='sr-only'>{}</span>".format(row["status"]),
        "<span class='goal-topic'>{}</span>".format(topic),
        details_node
    )

    expl_text = row.get("explanation", '')
    if blank:
        expl_text = details

    explanation = '<div class="explanation">{}</div>'.format(expl_text)
    # Add notes to explanation if they exist:
    if row.get("notes"):
        notes = '<details class="notes">\n<summary>Notes</summary>\n<ul>'
        for note in row.get("notes"):
            notes += '\n<li class="note">{}</li>'.format(note)
        notes += '</ul>\n</details>'
        explanation += '\n' + notes

    # Add warnings to explanation if they exist:
    if row.get("warnings"):
        warnings = (
            '<details class="warnings">\n<summary>Warnings</summary>\n<ul>'
        )
        for warning in row.get("warnings"):
            warnings += '\n<li class="warning">{}</li>'.format(warning)
        warnings += '</ul>\n</details>'
        explanation += '\n' + warnings

    # Add assessment (explanation + notes + warnings) to result:
    contents += '<div class="assessment">{}</div>'.format(explanation)

    # Add subtable if there is one:
    subtable = ''
    if row.get("subtable"):
        subtable = render_rubric_table(taskid, row.get("subtable"), blank)

    contents += subtable

    # CSS classes for the rubric row
    classes = [
        "rubric_row",
        html_tools.status_css_class(row["status"])
    ] + [
        "tag-{k}-{v}".format(k=k, v=v)
        for (k, v) in row.get("tags", {}).items()
    ]
    # CSS class 'goal_category' for non-ID's items
    if rowid == '':
        classes.append("goal_category")
    return '<div class="{}">{}</div>'.format(
        ' '.join(classes),
        contents
    )


def render_contexts_list(contexts_list):
    """
    Accepts a contexts list in the format returned by
    `potluck.contexts.list_and_render_contexts`. Each context gets its
    own details element that collapses to a single row, but expands to
    show the context value(s).

    This function returns a single HTML string containing code for all of
    the contexts, wrapped in a div with class 'context_info'.
    """
    result = "<div class='context_info'>"
    for index, ctx in enumerate(contexts_list):
        tl = min(ctx["level"], 8) # truncated level value
        # TODO: Some way of drawing connectors that's not horribly
        # fragile...
        if ctx["value"] != "":
            result += """
<details id='ctx_{index}' class='context_details level_{tl}'>
  <summary>{desc}</summary>
  {val}
</details>
""".format(
    index=index,
    tl=tl,
    desc=ctx["description"],
    val=ctx["value"],
)
        else:
            result += """
<div id='ctx_{index}' class='context_details level_{tl}'>
  {desc}
</div>
""".format(
    index=index,
    tl=tl,
    desc=ctx["description"]
)

    result += "</div>"
    return result
