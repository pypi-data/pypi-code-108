from deb_pkg_tools.deb822 import parse_deb822  # type: ignore
from deb_pkg_tools.control import parse_control_fields  # type: ignore

from typing import List, Tuple, Any


def parse_metadata(cran_metadata: str) -> List[Tuple[str, str]]:
    """
    Create an enumerate object from cran metadata

    returns enumerate object, together with its length
    """
    # Split metadata into separate chunk for each package
    chunks = drop_duplicates(cran_metadata.split("\n\n"))
    return [get_package_and_version(chunk) for chunk in chunks]


def get_package_and_version(chunk: str) -> Tuple[str, str]:
    """Extracts the package and version from CRAN metadata chunk

    :params:
    chunk: A single string chunk of CRAN metadata

    """
    unparsed_fields = parse_deb822(chunk)
    parsed_fields = parse_control_fields(unparsed_fields)
    package = parsed_fields["Package"]
    version = parsed_fields["Version"]
    return package, version


def drop_duplicates(xs: List[Any]) -> List[Any]:
    """Returns a de-deduplicated list of entries

    :params:
    xs: a list of values
    """
    return list(set(xs))
