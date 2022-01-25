"""
This function gets called during every request by the
context processor to return all the custom scripts for a specific path.
"""
import re

from ecommerce_extensions.tenant.extra_options import check_attributes_required, set_default_option


def process_scripts(path, options):
    """
    Process and loads all the extra scripts for the template
    rendered during the request.

    Parameters:
        path (string): a regex for a url of a given site
        options (dict): a list of javascript scripts separated by a path

    Returns:
        dict: a list of separate javascript scripts validated according to regex in path
    """
    scripts = options.get('scripts', {})

    if isinstance(scripts, dict):
        for regex, values in scripts.items():
            regex_path_match = re.compile(regex)
            if regex_path_match.match(path):
                scripts = []
                for script in values:
                    set_defaul_to_script = set_default_option(
                        script,
                        'media_type',
                        ['module', 'text/javascript'],
                        'text/javascript'
                    )

                    # Validate 'src' or 'content' key in script
                    is_validate_script = check_attributes_required(
                        set_defaul_to_script,
                        ['src', 'content'],
                        "Script"
                    )
                    if is_validate_script:
                        scripts.append(set_defaul_to_script)
                if scripts:
                    return scripts

    return None
