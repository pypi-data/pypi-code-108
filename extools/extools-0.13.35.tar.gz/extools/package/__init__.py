"""Tools for working with packaged customizations and their contents."""
import pkg_resources

def get_package_file_content(package, resource_path):
    """Get the content of a file stored and distributed in a package.

    :param package: the package name. e.g. extools
    :type package: str
    :param resource_path: the relative path from the package root to the file.
        e.g. `tmpl/file.json`
    :type resource_path: Path or str
    """
    script_content = pkg_resources.resource_string(
            package, str(resource_path))

    content = script_content.decode()

    return content

