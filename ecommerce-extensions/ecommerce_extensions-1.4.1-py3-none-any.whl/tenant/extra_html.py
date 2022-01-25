"""
This function gets called during every request by the
context processor to return all the custom html for a specific path.
"""
import re

from ecommerce_extensions.tenant.extra_options import check_attributes_required, set_default_option


def process_html(path, options):
    """
    Process and loads all the extra html for the template
    rendered during the request.

    Parameters:
        path (string): a regex for a url of a given site
        options (dict): a list of separate html separated by a path

    Returns:
        dict: a list of separate html scripts validated according to regex in path
    """
    html_list = options.get('html', {})
    html_returns = {}

    if not isinstance(html_list, dict):
        return html_returns

    for regex, values in html_list.items():
        regex_path_match = re.compile(regex)
        if regex_path_match.match(path):
            for html in values:
                set_default_to_html = set_default_option(
                    html,
                    'location',
                    ['head', 'body_start', 'body_end'],
                    'body_start'
                )

                # Validate 'content' key in html
                is_validate_html = check_attributes_required(
                    set_default_to_html,
                    ['content'],
                    "HTML"
                )

                if is_validate_html:
                    html_returns[set_default_to_html['location']] = set_default_to_html['content']

    return html_returns
