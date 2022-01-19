"""This module contains utility functions."""
import errno
import os

import pkg_resources

import myst_v1alpha1
from myst_v1alpha1.constants import USER_AGENT_PREFORMAT


def get_package_version():
    """Gets the version of the Myst Python client library.

    Returns:
        version (str): Myst Python client library version
    """
    version = pkg_resources.get_distribution(myst_v1alpha1.__package__).version
    return version


def get_user_agent():
    """Gets the `User-Agent` header string to send to the Myst API with requests.

    Returns:
        user_agent (str): user agent string
    """
    # Infer Myst API version and Myst Python client library version for current active versions.
    user_agent = USER_AGENT_PREFORMAT.format(
        api_version=myst_v1alpha1.api_version, package_version=get_package_version()
    )
    return user_agent


def get_pkg_resource_path(resource_name="", resource_package="myst_v1alpha1.data"):
    """Gets a package resource path.

    Args:
        resource_name (str, optional): relative path to resource from `myst_v1alpha1.data`; if not specified, will simply
            return the absolute path the the given resource package
        resource_package (str, optional): path to package where resource is stored

    Returns:
        resource_path (str): absolute path to resource
    """
    resource_path = os.path.abspath(pkg_resources.resource_filename(resource_package, resource_name))
    return resource_path


def make_directory(path):
    """Makes nested directories if needed safely.

    Args:
        path (str): path to directory to create
    """
    try:
        os.makedirs(path)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise


def format_repr(class_name, class_properties=None):
    """Formats the string representation of a class.

    Args:
        class_name (str): name of the class
        class_properties (dict): properties of the class

    Returns:
        formatted_repr (str): formatted string representation
    """
    if not class_properties:
        formatted_repr = "<{class_name}>".format(class_name=class_name)
    else:
        formatted_repr = "<{class_name}: {class_properties}>".format(
            class_name=class_name,
            class_properties=", ".join(
                map(
                    lambda class_property_tuple: "{key}={value}".format(
                        key=class_property_tuple[0], value=class_property_tuple[1]
                    ),
                    class_properties.items(),
                )
            ),
        )
    return formatted_repr
