# Imports
import importlib.resources as pkg_resources
from . import _template_resources


# Show templates
def get_template(template: str):
    """
    Retrieve the source of a template

    :param template: str
        Template name, can be either 'free_from_api' or 'single_obs"
    :return: str
        The source code of the template
    """

    return pkg_resources.read_text(_template_resources, f"{template}_template.py")


def print_template(template: str):
    """
    Displays the source of a template

    :param template: str
        Template name, can be either 'free' or 'single_obs"
    :return: str
        The source code of the template
    """

    print(get_template(template=template))
