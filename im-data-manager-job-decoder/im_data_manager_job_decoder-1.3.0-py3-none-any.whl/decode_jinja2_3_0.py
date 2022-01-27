"""A decoder for jinja2 3.0.x formatted strings.
"""
from typing import Dict, Optional, Set, Tuple

import jinja2
from jinja2.exceptions import TemplateSyntaxError
from jinja2.meta import find_undeclared_variables


def decode(template_text: str,
           variable_map: Optional[Dict[str, str]],
           subject: str) -> Tuple[str, bool]:
    """Decodes text expected to conform to Jinja2 (v3.0.x)
    """
    assert template_text
    assert subject

    # Make a template from the text
    env: jinja2.Environment = jinja2.\
        Environment(undefined=jinja2.DebugUndefined)
    try:
        template: jinja2.Template = env.from_string(template_text)
    except TemplateSyntaxError as ex:
        msg: str = f'TemplateSyntaxError with {subject}: {ex}'
        return msg, False

    # Render (this works even if there are variables in the rendered text
    # The rendered text, when stripped of whitespace, must not be empty.
    rendered_text = template.render(variable_map).strip()
    if len(rendered_text) == 0:
        msg = f'Rendered text for {subject} is blank'
        return msg, False

    # Check if rendering was done correctly.
    # It's a little odd with Jinja2 - as undefined variables are not
    # considered errors. See https://stackoverflow.com/a/55699590 in the
    # StackOverflow topic: -
    #   How to get ALL undefined variables from a Jinja2 template?
    abstract_syntax_tree = env.parse(rendered_text)
    undefined: Set[str] = find_undeclared_variables(abstract_syntax_tree)
    if undefined:
        # We
        msg = f'Undefined template variables for {subject}:'
        for variable in undefined:
            msg += f' {variable},'
        # Return the message, stripping the last comma from it
        return msg[:-1], False

    # OK if we get here.
    # Just return the rendered text
    return rendered_text, True
