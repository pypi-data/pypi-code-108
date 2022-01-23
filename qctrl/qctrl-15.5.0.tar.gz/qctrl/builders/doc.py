# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring, too-few-public-methods

import re
import shutil
from functools import wraps
from textwrap import fill
from typing import (
    Callable,
    List,
    Optional,
)

import attr
import commonmark
import inflection

from qctrl.utils import (
    _convert_md_to_rst,
    _parse_to_rst,
)


def _get_title_underline(title: str, char: str = "-") -> str:
    """Returns the underline for the title of a docstring section.

    Parameters
    ----------
    title: str
        section title.
    char: str
        underline char. (Default value = "-")

    Returns
    -------
    str
        underline in str.
    """
    return "".join([char for _ in range(len(title))])


def docstring_section(title: str) -> Callable:
    """Builds a section of the docstring e.g. Parameters, Returns, etc.

    The decorated method should return a BaseDoc or list of
    BaseDoc objects.

    Parameters
    ----------
    title: str
        section title.

    Returns
    -------
    Callable
        decorator method
    """

    def customized_decorator(func):
        @wraps(func)
        def decorator(self, *args, **kwargs) -> Optional[str]:
            value = func(self, *args, **kwargs)

            if not value:
                return None

            lines = [
                title,
                _get_title_underline(title),
            ]

            # single BaseDoc object
            if isinstance(value, BaseDoc):
                lines.append(str(value))

            # list of BaseDoc objects
            elif isinstance(value, (tuple, list)):
                for item in value:
                    if not isinstance(item, BaseDoc):
                        raise ValueError(f"unexpected list item: {item}")

                    lines.append(str(item))

            else:
                raise ValueError(f"unexpected function result: {value}")

            return "\n".join(lines)

        return property(decorator)

    return customized_decorator


class BaseDoc:
    """The base class for all docstring pieces.

    Subclasses should implement the __str__ method.
    """

    _indent_char = " "
    _indent_length = 4

    @property
    def _indent_str(self) -> str:
        return self._indent_char * self._indent_length

    def _indent(self, text: str) -> str:
        terminal_width = shutil.get_terminal_size().columns

        # In numpydoc standard, the length of docstring is up to 75.
        # Convert width to 75 if terminal_width is larger than 75
        # (and to 1 if terminal_width is reported as 0, otherwise
        # `fill` throws an error).
        width = max(1, min(75, terminal_width))

        # wrap the single line description into paragraph
        return fill(
            text,
            width=width,
            initial_indent=self._indent_str,
            subsequent_indent=self._indent_str,
        )

    def __str__(self):
        """To be implemented by the subclass."""
        raise NotImplementedError


class Docstring(BaseDoc):  # pylint:disable=too-few-public-methods
    """Base class for dynamically building docstrings consisting of a number of
    sections.

    Attributes
    ----------
    _sections: list of str
        list of ordered attributes corresponding to
        sections of the docstring.
    """

    _sections = []

    def _get_sections(self) -> List[str]:
        """Returns the list of sections for the docstring."""
        sections = []

        for _attr in self._sections:
            value = getattr(self, _attr)

            if value:
                sections.append(value)

        return sections

    def __str__(self):
        sections = self._get_sections()
        return "\n\n".join(sections)


@attr.s(auto_attribs=True)
class ClassAttribute(BaseDoc):
    """Describes a class attribute.

    Format:
    name: attr_type
        description

    Attributes
    ----------
    name: str
        The name of the attribute.
    attr_type: str
        The type of the attribute.
    description: str
        Verbose description of the attribute.
    optional: bool
        If the attribute is optional.
    """

    name: str
    attr_type: str = None
    description: Optional[str] = attr.ib(default=None, converter=_convert_md_to_rst)
    optional: bool = None

    def __str__(self):
        result = self.name

        if self.attr_type:
            result = f"{result}: {self.attr_type}"

        if self.optional:
            result = f"{result}, optional"

        if self.description:
            result += f"\n{self._indent(self.description)}"

        return result


@attr.s(auto_attribs=True)
class ClassDocstring(Docstring):
    """Constructs a doc string for a class."""

    description: Optional[str] = attr.ib(default=None, converter=_convert_md_to_rst)
    attrs: List[ClassAttribute] = attr.ib(default=attr.Factory(list))

    _sections = ["fdescription", "fattrs"]

    @property
    def fdescription(self):
        """Ensures summary is non-empty for formatting."""
        return self.description or " "

    @docstring_section("Attributes")
    def fattrs(self) -> List[ClassAttribute]:
        """Formatted Attributes section."""
        return self.attrs


@attr.s(auto_attribs=True)
class FunctionArgument(BaseDoc):
    """Describes an argument to a function.

    Format:
    name (arg_type, optional): description

    Attributes
    ----------
    name: str
        The name of the argument.
    arg_type: str
        The type of the argument.
    description: str
        Verbose description of the argument.
    optional: bool
        If the argument is optional.
    """

    name: str
    arg_type: str = None
    description: Optional[str] = attr.ib(default=None, converter=_convert_md_to_rst)
    optional: bool = None

    def __str__(self):
        result = self.name

        if self.arg_type:
            result = f"{result}: {self.arg_type}"

        if self.optional:
            result = f"{result}, optional"

        if self.description:
            result = f"{result}\n{self._indent(self.description)}"

        return result


@attr.s(auto_attribs=True)
class PossibleException(BaseDoc):
    """Describes a possible exception that a function could raise.

    Format:
    name
        description

    Attributes
    ----------
    name: str
        The class name of the exception.
    description: str
        Verbose description of the exception and why it would
        be raised.
    """

    name: str
    description: Optional[str] = attr.ib(default=None, converter=_convert_md_to_rst)

    def __str__(self):
        result = self.name

        if self.description:
            result = f"{result}\n{self._indent(self.description)}"

        return result


@attr.s(auto_attribs=True)
class Returns(BaseDoc):
    """Describes the object returned from a function.

    Format:
    return_type
        description

    Parameters
    ----------

    Returns
    -------

    Attributes
    ----------
    return_type: str
        cls type
    description: str
        Description of the returned object.
    """

    return_type: str
    description: Optional[str] = attr.ib(default=None, converter=_convert_md_to_rst)

    def __str__(self):
        result = self.return_type

        if self.description:
            # merge multiple lines to one line to avoid creating an item list
            merged_line_description = " ".join(self.description.splitlines())
            result = f"{result}\n{self._indent(merged_line_description)}"

        return result


@attr.s(auto_attribs=True)
class WarningsType(BaseDoc):
    """Describes the warnings section of NumpyDoc."""

    warnings: str

    def __str__(self):
        return self.warnings


@attr.s(auto_attribs=True)
class SeeAlsoType(BaseDoc):
    """Describes the see also section of NumpyDoc."""

    see_also: str

    def __str__(self):
        return self.see_also


@attr.s(auto_attribs=True)
class NotesType(BaseDoc):
    """Describes the notes section of NumpyDoc."""

    notes: str

    def __str__(self):
        return self.notes


@attr.s(auto_attribs=True)
class ReferencesType(BaseDoc):
    """Describes the references section of NumpyDoc."""

    references: str

    def __str__(self):
        """Replacing the references with reST specific directives."""
        reference_link_regex = r"\[([\d.]+)\]_"
        return re.sub(reference_link_regex, r".. [\1]", self.references)


@attr.s(auto_attribs=True)
class ExamplesType(BaseDoc):
    """Describes the examples section of NumpyDoc."""

    examples: str

    def __str__(self):
        return self.examples


@attr.s(auto_attribs=True)
class FunctionDocstring(Docstring):
    """Constructs a docstring for a function."""

    description: str = None
    params: List[FunctionArgument] = attr.ib(default=attr.Factory(list))
    returns: Returns = None
    raises: List[PossibleException] = attr.ib(default=attr.Factory(list))
    warnings: str = None
    see_also: str = None
    notes: str = None
    references: str = None
    examples: str = None

    _sections = [
        "description",
        "fparams",
        "freturns",
        "fraises",
        "fwarnings",
        "fsee_also",
        "fnotes",
        "freferences",
        "fexamples",
    ]

    @docstring_section("Parameters")
    def fparams(self) -> Optional[str]:
        """Formatted Args section."""
        return self.params

    @docstring_section("Returns")
    def freturns(self) -> Optional[str]:
        """Formatted Returns section."""
        return self.returns

    @docstring_section("Raises")
    def fraises(self) -> Optional[str]:
        """Formatted Raises section."""
        return self.raises

    @docstring_section("Warnings")
    def fwarnings(self) -> Optional[str]:
        """Formatted Warnings section."""
        return WarningsType(self.warnings) if self.warnings else None

    @docstring_section("See Also")
    def fsee_also(self) -> Optional[str]:
        """Formatted See Also section."""
        return SeeAlsoType(self.see_also) if self.see_also else None

    @docstring_section("Notes")
    def fnotes(self) -> Optional[str]:
        """Formatted Notes section."""
        return NotesType(self.notes) if self.notes else None

    @docstring_section("References")
    def freferences(self) -> Optional[str]:
        """Formatted Examples section."""
        return ReferencesType(self.references) if self.references else None

    @docstring_section("Examples")
    def fexamples(self) -> Optional[str]:
        """Formatted References section."""
        return ExamplesType(self.examples) if self.examples else None

    @classmethod
    def from_markdown(cls, markdown_text: str) -> "FunctionDocstring":
        """Generates an rst formatted FunctionDocstring from Markdown text.

        Parameters
        ----------
        markdown_text: str
            The markdown formatted docstring to process.

        Returns
        -------
        FunctionDocstring
            The FunctionDocstring class populated with the relevant sections.
        """
        _section_headings = (
            "description",
            "warnings",
            "see_also",
            "notes",
            "references",
            "examples",
        )
        docstring = cls()
        if markdown_text is None:
            return docstring

        # parse to ast
        parser = commonmark.Parser()
        ast = parser.parse(markdown_text)

        # start at the first child
        ast = ast.first_child

        current_text = ""

        if ast.t == "heading":
            current_heading = cls._parse_md_heading(ast.first_child.literal)
        else:
            current_heading = "description"
            current_text = _parse_to_rst(ast)

        event = ast.nxt
        sections = {}

        while event is not None:
            if event.t == "heading" and event.level == 1 and event.first_child.literal:
                sections[current_heading] = current_text
                heading = cls._parse_md_heading(event.first_child.literal)
                current_heading = heading
                current_text = ""
            else:  # it's a paragraph
                rst = _parse_to_rst(event) or ""
                current_text += rst

            event = event.nxt

        sections[current_heading] = current_text

        for key, value in sections.items():
            if key in _section_headings and value != "":
                setattr(docstring, key, value)

        return docstring

    @staticmethod
    def _parse_md_heading(heading: str) -> str:
        return inflection.underscore(inflection.parameterize(heading))


def add_deprecation_warning(object_name: str) -> str:
    """
    add deprecation warning for factories and models.

    Parameters
    ----------
    object_name: str
        name of the model/factory.

    Returns
    -------
    str
        formatted warning docstring.
    """
    deprecation_warning = f"""
Warning
-------
`{object_name}` will be deprecated soon. Please use
:class:`qctrl.dynamic.namespaces.TypeNamespace` instead.
"""
    return deprecation_warning
