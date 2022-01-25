"""
Functions for extracting data from a single R package
"""

import os
import pathlib
import tarfile
import urllib.request

from dataclasses import dataclass
from typing import List, Tuple

import deb_pkg_tools as deb  # type: ignore

from datetime import datetime
from dateutil import parser

from .file_functions import read_file
from .urls import CRAN_PKG_ARCHIVE_PATTERN, CRAN_PKG_CONTRIB_URL


@dataclass
class Description:
    """
    Stores data from a DESCRIPTION file
    """

    title: str
    description: str
    url: str
    bugreport: str
    version: str
    maintainer: str
    date: datetime
    import_list: list
    suggest_list: list


def download_package_tar(
    package: str, version: str, is_archive: bool, target_path: pathlib.Path
) -> pathlib.Path:
    """
    Downloads the package.tar.gz file for a version of a package from CRAN

    :param   package:  The name of the package to be downloaded
    :param   version:  The version of the package to be downloaded
    :param   is_archive:  Is this version of the package an archived package?
    :param   target_path:  Where should the downloaded package be stored

    :type   package:  pathlib.Path
    :type   version:  str
    :type   is_archive:   bool
    :type   target_path:   pathlib.Path

    :return:  The filepath for the downloaded package

    """
    # Download tar file
    url_prefixes = {
        "archived": CRAN_PKG_ARCHIVE_PATTERN.format(package=package),
        "current": CRAN_PKG_CONTRIB_URL,
    }
    if is_archive:
        url_prefix = url_prefixes["archived"]
    else:
        url_prefix = url_prefixes["current"]

    tar_file = f"{package}_{version}.tar.gz"
    src = f"{url_prefix}{tar_file}"

    if not os.path.exists(target_path):
        os.mkdir(target_path)

    target = target_path / tar_file

    try:
        urllib.request.urlretrieve(src, target)
    except urllib.error.HTTPError:
        try:
            url_prefix = url_prefixes["archived"]
            src = f"{url_prefix}{tar_file}"
            urllib.request.urlretrieve(src, target)
        except urllib.error.HTTPError:
            raise ValueError(
                f"Could not download package archive for {package} v{version}"
            )

    return target


def process_package_tar(tar_file: pathlib.Path, keep_tar_file=False) -> dict:
    """
    Processing a tar.gz file for a package (except reading the NEWS.md)

    :param   tar_file:  The .tar.gz file that is to be analysed
    :param   keep_tar_file:   Should the uncompressed tar file be kept after
    analysis?

    :type   tar_file:   pathlib.Path
    :type   keep_tar_file:   bool

    :return:   A dictionary containing all data that was extracted from the
    package
    """
    tar = tarfile.open(tar_file, "r:gz")

    tar_name = tar_file.name.rstrip(".tar.gz$")
    ix = tar_name.index("_")
    package_name = tar_name[:ix]
    tar_dir = tar_file.parent
    target_to_extract = tar_dir / tar_name

    tar.extractall(target_to_extract)
    tar.close()

    if not keep_tar_file:
        os.remove(tar_file)

    package_path = target_to_extract / package_name

    description_text = read_file(package_path / "DESCRIPTION")
    description = parse_description_file(description_text)

    function_list = read_doc_files(package_path)

    res = {
        "data": description_text,
        "name": package_name,
        "title": description.title,
        "description": description.description,
        "url": description.url,
        "bugreport": description.bugreport,
        "version": description.version,
        "maintainer": description.maintainer,
        "date": description.date,
        "imports": description.import_list,
        "suggests": description.suggest_list,
        "functions": function_list,
        "package_location": str(package_path),
    }
    return res


def parse_description_file(data: str) -> Description:
    """Parses DESCRIPTION file

    :param   data: string for DESCRIPTION file data
    :return: A Description object which contains DESCRIPTION metadata: title,
    description, url, bugreport, version, maintainer, date, import_list,
    suggest_list
    """
    unparsed_fields = deb.deb822.parse_deb822(data)
    parsed_fields = deb.control.parse_control_fields(unparsed_fields)

    version = parsed_fields.get("Version", "")
    title = parsed_fields.get("Title", "")
    description = parsed_fields.get("Description", "")
    url = parsed_fields.get("Url", "")
    bugreport = parsed_fields.get("Bugreports", "")
    maintainer = parsed_fields.get("Maintainer", "")

    # Parse dates
    # - some packages use "Date/publication", some use "Date", some don't include a date
    # - prefer "Date/publication" over "Date" when they are both present
    date_string = parsed_fields.get("Date/publication", parsed_fields.get("Date", None))
    date = parse_date(date_string)

    # Parse imports
    try:
        imports = parsed_fields["Imports"]
        # Imports does not get parsed properly,
        # so do this here
        imports = deb.deps.parse_depends(imports)
        import_list = create_relationship_dict(imports)
    except KeyError:
        import_list = []

    # Parse suggests
    try:
        suggests = parsed_fields["Suggests"]
        suggest_list = create_relationship_dict(suggests)
    except KeyError:
        suggest_list = []

    return Description(
        title,
        description,
        url,
        bugreport,
        version,
        maintainer,
        date,
        import_list,
        suggest_list,
    )


def read_doc_files(
    package: pathlib.Path,
) -> List[dict]:
    """
    Get the functions, arguments and defaults from the *.Rd files in this package

    :param   package: The filepath to an uncompressed R package
    :type   package: pathlib.Path

    :return: a list of function dictionaries containing name and arguments
    """
    function_list: List[dict] = []

    # First, check if there is a man folder
    if not os.path.exists(package / "man"):
        # This package has no docs- return empty lists
        return function_list

    # If man exists, read doc files
    file_list = os.listdir(package / "man")
    for filename in file_list:
        if filename[-3:] != ".Rd":
            continue
        rd_file = package / "man" / filename
        docs = read_file(rd_file)

        doc_sections = [
            "name",
            "alias",
            "title",
            "description",
            "usage",
            "arguments",
            "details",
            "value",
            "examples",
            "keyword",
        ]
        doc_sections = ["name", "alias", "usage"]  # noqa
        # joined_sections = '|'.join(doc_sections)
        # match_string = '\\\\(' + joined_sections + "){((?:[^\\\\]|\\\\(?!(" +
        #     joined_sections + ")))+)}"

        # comment = re.compile("^%.+$")
        # not_comments = "\n".join(l for l in docs.split("\n") if not comment.match(l))

        # matcher = re.compile(match_string)
        # choices = "|".join(
        #     "name", "alias", "title", "description", "usage", "arguments", "details",
        #     "value", "examples"
        # )
        # matcher = re.compile(
        #     '\\\\(' + choices + ')' +
        #     '{((?:[^\\\\]|\\\\(?!(' + choices + ')))+)}'
        # )
        # res = matcher.findall(docs)

        # aliases = list(set(map(
        #     lambda x: x[1], filter(lambda x: x[0] == 'alias' or x[0] == 'name', res)
        # )))
        # args = list(map(lambda x: x[1], filter(lambda x: x[0] == 'usage', res)))[0]
        # arg_list = list(
        #     map(lambda x: x[1], filter(lambda x: x[0] == 'arguments', res))
        # )[0]

        # matcher = re.compile('\\\\item{(.*)}')
        # arg_names = matcher.findall(arg_list)
        # re.split('(' + '|'.join(arg_names) + ')', args)

        # matcher = re.compile('.*\( (.*) \).*', re.MULTILINE)
        # matcher.findall(args)

        # args.replace(',','\n').split('\n')
        # matcher.sub(args, "\n").split('\n')

        # matcher = re.compile("\((.+)\)", re.MULTILINE)
        # [m.start() for m in re.finditer('\(', args)]
        # [m.start() for m in re.finditer('\)', args)]
        # matcher.findall(args)

        if "\\usage{" not in docs:
            # No 'usage' documentation
            continue
        # Use aliases to create a list of potential functions
        doc_functions = []
        with open(rd_file, "r", encoding="utf-8") as doc_file:
            for i in doc_file:
                if i.startswith("\\alias{"):
                    function = i[len("\\alias{") :]
                    function = function.rstrip("}\n")
                    doc_functions.append(function)
        # Extract 'usage' section contents
        usage_start = docs.find("\\usage{")
        usage = docs[usage_start:]
        try:
            bracket_pairs = match_brackets(usage, bracket_type="{")
        except IndexError:
            print(f"Warning: IndexError for match_brackets in {rd_file}")
            print(usage)
            bracket_pairs = -1
        if bracket_pairs == -1:
            end = usage.find("}\n")
            usage = usage[len("\\usage{") : end]
        else:
            [start, end] = bracket_pairs[0]
            usage = usage[start + 1 : end]
        # Check for and delete comments in usage
        if "%" in usage:
            # Remove Rd comments '%' (like LaTeX)
            starts = [i for i, char in enumerate(usage) if char == "%"]
            length_rm = 0
            while len(starts) > 0:
                if usage[starts[0] - length_rm - 1] == "\\":
                    # Escape character- not a comment
                    starts.pop(0)
                    continue
                # Want to delete any preceding spaces as well
                if starts[0] - length_rm - 1 >= 0:
                    if usage[starts[0] - length_rm - 1] == " ":
                        while usage[starts[0] - length_rm - 1] == " ":
                            starts[0] = starts[0] - 1
                comment = usage[starts[0] - length_rm :]
                # Comment should run only until '\n' if this exists
                comment_end = comment.find("\n")
                if comment_end != -1:
                    comment = comment[:comment_end]
                usage = (
                    usage[: starts[0] - length_rm]
                    + usage[starts[0] - length_rm + len(comment) :]
                )
                # Check for % signs within cut comment and remove from potential starts
                num_starts = [i for i, char in enumerate(comment) if char == "%"]
                starts = starts[len(num_starts) :]
                length_rm += len(comment)
        if "#" in usage:
            # Remove R-like '#' comments (including #ifdef statements- technically not
            # comments!)
            usage = remove_comments(usage)

        # Iterate through each potential function
        for f in doc_functions:
            function_arguments = []
            function_str = "\n" + f + "("
            if function_str in usage:
                # Confirms that f is a function
                function_start = usage.find(function_str)
                string_length = len(function_str)
            elif "\\method{" in usage:
                # Check for S3 method
                dots = [i for i, char in enumerate(f) if char == "."]
                found_method = False
                for d in dots:
                    method_str = "\\method{%s}{%s}(" % (f[:d], f[d + 1 :])
                    if method_str in usage:
                        # Confirms that f is a S3 method
                        function_start = usage.find(method_str)
                        found_method = True
                        string_length = len(method_str)
                        break
                if not found_method:
                    # No documentation for method with name f
                    continue
            elif f in usage:
                # f is not a function or method (could be data)
                continue
            else:
                # No documentation for function with name f
                continue
            # Extract contents of function parentheses
            arguments = usage[function_start:]
            bracket_pairs = match_brackets(arguments)
            if bracket_pairs == -1:
                end = arguments.find(")\n")
                arguments = arguments[string_length:end]
            else:
                [start, end] = bracket_pairs[0]
                arguments = arguments[start + 1 : end]
            # Use 'free' commas (outside () and "") to get a list of arguments
            arguments = split_arguments(arguments)
            for i in arguments:
                # Split into argument name and default using '=' sign
                argument = i.replace("\n  ", " ").split("=", maxsplit=1)
                argname = argument[0].strip("\t\n ")
                if len(argument) == 1:
                    # No default value: store empty string
                    argval = ""
                else:
                    # Default exists
                    argval = argument[1].strip("\t\n ")
                    argval = " ".join(argval.split())
                # Create argument dictionary, and append to arguments list
                arg_dict = {"name": argname, "value": argval}
                function_arguments.append(arg_dict)

            # Create function dictionary, and append to function list
            function_dict = {"name": f, "arguments": function_arguments}
            function_list.append(function_dict)
    return function_list


def remove_comments(string, comment_char="#"):
    starts = [i for i, char in enumerate(string) if char == comment_char]
    quotes = [i for i, char in enumerate(string) if char == '"']
    # Ignore quotes preceded by escape character \\
    for q_id, quote in enumerate(quotes):
        if quote - 2 >= 0:
            if string[quote - 2 : quote] == "\\\\":
                # Make sure no escape character \\ before escape character
                if quote - 4 >= 0:
                    if string[quote - 4 : quote - 2] == "\\\\":
                        continue
                quotes.pop(q_id)
                continue
        # Also check for single '\' escape
        if quote - 1 >= 0:
            if string[quote - 1 : quote] == "\\":
                quotes.pop(q_id)
    pairs = []
    # Search for '#' symbol within quote pairs
    if len(quotes) % 2 != 0:
        print("Warning: uneven number of quote pairs in # search")
        print(string)
    else:
        # Only add quote pairs if even number
        quote_pairs = [quotes[i : i + 2] for i in range(0, len(quotes), 2)]
        pairs.extend(quote_pairs)
    length_rm = 0
    while len(starts) > 0:
        if True in [pairs[i][0] < starts[0] < pairs[i][1] for i in range(len(pairs))]:
            # Hash '#' symbol is found within a set of brackets or quotes: not a comment
            starts.pop(0)
            continue
        # Want to delete any preceding spaces as well
        if starts[0] - length_rm - 1 >= 0:
            if string[starts[0] - length_rm - 1] == " ":
                while string[starts[0] - length_rm - 1] == " ":
                    starts[0] = starts[0] - 1
        comment = string[starts[0] - length_rm :]
        # Comment should run only until '\n' if this exists
        comment_end = comment.find("\n")
        if comment_end != -1:
            comment = comment[:comment_end]
        comment = comment[:comment_end]
        string = (
            string[: starts[0] - length_rm]
            + string[starts[0] - length_rm + len(comment) :]
        )
        # Check for '#' signs within cut comment and remove from potential starts
        num_starts = len([i for i, char in enumerate(comment) if char == comment_char])
        starts = starts[num_starts:]
        length_rm += len(comment)
    return string


def match_brackets(string, bracket_type="("):
    if bracket_type == "(":
        opens = [i for i, letter in enumerate(string) if letter == "("]
        closes = [i for i, letter in enumerate(string) if letter == ")"]
    if bracket_type == "{":
        opens = [i for i, letter in enumerate(string) if letter == "{"]
        closes = [i for i, letter in enumerate(string) if letter == "}"]
    if len(opens) != len(closes):
        # Uneven bracket pairs: return with flag -1
        pairs = -1
    else:
        pairs = []
        # Find the corresponding opening bracket for each closing bracket
        for i in closes:
            open_id = [j for j in opens if j < i][-1]
            pairs.append([open_id, i])
            opens.remove(open_id)
        # Sort in order of the opening bracket
        pairs = sorted(pairs, key=lambda x: x[0])
    return pairs


def split_arguments(string):
    # Locate pairs of brackets and double-quotes
    pairs = match_brackets(string)
    if pairs == -1:
        # Do not check for commas within bracket pairs
        pairs = []
    quotes = [i for i, char in enumerate(string) if char == '"']
    # Ignore quotes preceded by escape character \\
    for q_id, quote in enumerate(quotes):
        if quote - 2 >= 0:
            if string[quote - 2 : quote] == "\\\\":
                # Make sure no escape character before escape character
                if quote - 4 >= 0:
                    if string[quote - 4 : quote - 2] == "\\\\":
                        continue
                quotes.pop(q_id)
                continue
        # Also check for single '\' escape
        if quote - 1 >= 0:
            if string[quote - 1 : quote] == "\\":
                quotes.pop(q_id)

    if len(quotes) % 2 != 0:
        print("Warning: uneven number of quotes in arg splitting")
        print(string)
    else:
        # Search for commas within quote pairs as well as bracket pairs
        quote_pairs = [quotes[i : i + 2] for i in range(0, len(quotes), 2)]
        pairs.extend(quote_pairs)
    commas = [i for i, char in enumerate(string) if char == ","]
    # Split up arguments only using commas outside () and "" pairs
    segments = []
    remainder = string
    length_removed = 0
    for loc in commas:
        if True in [pairs[i][0] < loc < pairs[i][1] for i in range(len(pairs))]:
            # Comma is found within a set of brackets or quotes
            continue
        segments.append(string[length_removed:loc])
        remainder = string[loc + 1 :]
        length_removed = len(string) - len(remainder)
    # Remaining string is also an argument
    segments.append(remainder)
    return segments


def create_relationship_dict(field):
    """Creates a list of dependencies (imports or suggests)

    :param: field: string for the field name
    :return: list of dictionaries with name and version number
    """
    relationship = field.relationships
    # Create list of name, version dicts
    package_list = []
    for i in relationship:
        version = ""
        if hasattr(i, "version"):
            version = i.version
        package_dict = {"name": i.name.strip("\n"), "version": version}
        package_list.append(package_dict)
    return package_list


def parse_date(date_string: str) -> datetime:
    """
    Convert a date string to a datetime object

    When the date_string is None, return None
    """
    if date_string is None:
        return None

    try:
        date = parser.parse(date_string)
    except ValueError:
        date = parser.parse(date_string, dayfirst=True)

    return date
