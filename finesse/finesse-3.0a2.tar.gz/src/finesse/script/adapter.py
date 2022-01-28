"""Interface between script and Finesse.

Adapters provide a programmatic way to retrieve useful information about KatScript
directives using their corresponding Python objects, and vice versa. This is primarily
used for the compiler and generator, but is also used to improve syntax suggestions and
error messages.

The adapter class hierarchy is intentionally very generic. By default, an ordinary
KatScript directive corresponding to an ordinary Finesse object is quite simple to
specify and should "just work". When special behaviour is required, e.g. in cases where
the KatScript directive has different arguments than the corresponding Python object
(e.g. `tem`) or where there is no corresponding Python object (e.g. `modes`), the
methods and members of the adapter can be overridden.
"""

import abc
import inspect
from functools import partial, cached_property
from enum import unique, Enum
import logging
from typing import get_type_hints, Any, Union, List
from dataclasses import dataclass
from ..parameter import Parameter
from ..element import ModelElement
from ..env import TERMINAL_WIDTH, INDENT

LOGGER = logging.getLogger(__name__)


@unique
class ArgumentType(Enum):
    """Signature argument types.

    While we just copy those defined by :mod:`inspect`, note that the definitions here
    are more abstract than those of :mod:`inspect`: these refer to the different
    flavours of script argument, which may or may not map directly to or from a Python
    type's call signature.
    """

    POS_ONLY = inspect.Parameter.POSITIONAL_ONLY
    ANY = inspect.Parameter.POSITIONAL_OR_KEYWORD
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
    VAR_POS = inspect.Parameter.VAR_POSITIONAL
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD


_INSPECT_KIND_CONVERSIONS = {
    inspect.Parameter.POSITIONAL_ONLY: ArgumentType.POS_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD: ArgumentType.ANY,
    inspect.Parameter.KEYWORD_ONLY: ArgumentType.KEYWORD_ONLY,
    inspect.Parameter.VAR_POSITIONAL: ArgumentType.VAR_POS,
    inspect.Parameter.VAR_KEYWORD: ArgumentType.VAR_KEYWORD,
}


class _empty:
    """Marker object for empty values."""


# Sometimes `None` is an intended default value, so we define a special field to use for
# actually empty defaults.
# NOTE: this should *not* be set to the same as :attr:`inspect.Parameter.empty`, as
# doing so would interfere with the construction of dataclasses.
EMPTY_VALUE = _empty


@dataclass
class Argument:
    """A generic instruction argument.

    This is similar but not identical to :class:`inspect.Parameter`. Arguments in the
    Finesse sense are more general than :class:`inspect.Parameter` since they can refer
    to KatScript arguments, and KatScript instructions may not necessarily define their
    supported arguments via Python class signatures.
    """

    name: str
    kind: ArgumentType = ArgumentType.ANY
    default: Any = EMPTY_VALUE
    annotation: Any = EMPTY_VALUE

    @property
    def has_no_default(self):
        return self.default is EMPTY_VALUE


@dataclass
class BoundArgument(Argument):
    """A concrete argument originating from a call to a setter.

    This is the same as :class:`.Argument` except in its handling of variadic arguments.
    Where this represents a variadic argument, it contains information as to which
    variadic argument it represents (either the sequence number or keyword). It is used
    to resolve self-references and to map compilation errors back to the original
    script.
    """

    # The sequence number for variadic positional arguments.
    var_sequence: int = None


@dataclass
class ArgumentDump(Argument):
    """A Finesse object argument name, its current value, default value, kind,
    annotation, and whether it should be dumped by value or reference.

    This encapsulates an argument for a script instruction. It can represent Finesse
    object parameters like floats, strings and model parameters, and is primarily used
    to generate KatScript representations of Finesse objects.
    """

    value: Any = EMPTY_VALUE
    other_defaults: List[Any] = None
    reference: bool = False

    @property
    def is_default(self):
        """Whether the value is the parameter's default."""
        if self.default is EMPTY_VALUE and self.other_defaults is None:
            return False

        try:
            return any([self.value == default for default in self._defaults])
        except ValueError:
            # Assume we have a sequence.
            return any([all(self.value == default) for default in self._defaults])

    @property
    def _defaults(self):
        yield self.default
        if self.other_defaults:
            yield from self.other_defaults


class ItemAdapter:
    """Adapter defining how a script instruction maps to/from a Python type.

    This encapsulates the required information to take a script instruction and generate
    a corresponding Python object (e.g. a :class:`.Laser` from a `laser l1 ...`
    instruction), to add it to a :class:`.Model` (or in the case of commands, set some
    model attribute), to dump that Python object back to script, and to generate
    documentation.

    Parameters
    ----------
    full_name : :class:`str`
        The instruction's unabbreviated name. This must be alphanumeric and can contain
        underscores but no spaces.

    short_name : :class:`str`, optional
        The instruction's short form name, used when generating compact script. If not
        specified, `full_name` is used in cases where the short form is desired.

    other_names : sequence, optional
        Any other supported names for this instruction.

    getter : :class:`.ItemDumper`, optional
        Object handling the retrieval of parameters from the Python object corresponding
        to this instruction.

    factory : :class:`.ItemFactory`, optional
        Object handling the creation of the Python object corresponding to this
        instruction.

    setter : :class:`.ItemSetter`, optional
        Object handling the setting of parameters in the Python object corresponding to
        this instruction's parameters.

    documenter : :class:`Documenter`
        Object handling the retrieval of docstrings and syntax suggestions for the
        instruction.

    singular : :class:`bool`, optional
        Flag indicating that this instruction can be defined only once per script.
        Defaults to `False`.

    build_last : :class:`bool`, optional
        Whether to build the Python object last, regardless of dependencies. This is
        useful for elements with implicit dependencies (see e.g. the cavity adapter). Be
        careful using this flag because statements for other adapters that depend on
        statements for adapters with this flag will be built first. Defaults to False.
    """

    def __init__(
        self,
        full_name,
        short_name=None,
        other_names=None,
        getter=None,
        factory=None,
        setter=None,
        documenter=None,
        singular=False,
        build_last=False,
    ):
        if other_names is None:
            other_names = []

        self.full_name = full_name
        self.short_name = short_name
        self.other_names = other_names
        self.getter = getter
        self.factory = factory
        self.setter = setter
        self.documenter = documenter
        self.singular = singular
        self.build_last = build_last

    @property
    def aliases(self):
        """The instruction alias(es).

        :getter: Sequence of aliases for this instruction.
        """
        aliases = [self.full_name]
        if self.short_name:
            aliases.append(self.short_name)
        if self.other_names:
            aliases.extend(self.other_names)
        return aliases

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.full_name} @ {hex(id(self))}>"


class ItemHandler(metaclass=abc.ABCMeta):
    """Root class for all dumper, setter, factory and documenter objects."""

    def __init__(self, *, item_type):
        self.item_type = item_type


class ItemDumper(ItemHandler, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, adapter, container):
        raise NotImplementedError


class ItemFactory(ItemHandler, metaclass=abc.ABCMeta):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class ItemSetter(ItemHandler, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, container, item):
        raise NotImplementedError

    def update_parameter(self, item, argument, value):
        """Update the built item's `name` parameter to `value`.

        This is used to update a parameter after the item has been created and added to
        the model, such as when resolving self-references.

        Parameters
        ----------
        item : object
            The item.

        argument : :class:`.BoundArgument`
            The item argument corresponding to the value to update.

        value : object
            The new value.
        """
        raise NotImplementedError(
            f"{self} does not support parameter updates after construction"
        )

    @abc.abstractmethod
    def arguments(self):
        """The supported constructor arguments for this item.

        Returns
        -------
        :class:`dict`
            Mapping of argument names to :class:`.Argument` objects for this setter.
        """
        raise NotImplementedError

    @property
    def var_positional_argument(self):
        for argument in self.arguments().values():
            if argument.kind is ArgumentType.VAR_POS:
                return argument

    @property
    def var_keyword_argument(self):
        for argument in self.arguments().values():
            if argument.kind is ArgumentType.VAR_KEYWORD:
                return argument

    def bind_argument(self, name_or_index):
        """Return a bound argument object for `name`.

        Parameters
        ----------
        name_or_index : :class:`str` or :class:`int`
            The argument keyword or index.

        Returns
        -------
        :class:`.BoundArgument`
            The argument metadata corresponding to `name_or_index`.
        """
        arguments = self.arguments()
        kwargs = {}

        if isinstance(name_or_index, int):
            # This is a positional argument.
            index = name_or_index
            args_by_index = list(arguments.values())

            try:
                argument = args_by_index[index]
            except IndexError as e:
                # This could either be a variadic positional argument or invalid.
                if var_argument := self.var_positional_argument:
                    argument = var_argument
                else:
                    raise TypeError(
                        f"positional argument at index {repr(index)} does not exist "
                        f"for {repr(self.item_type)}"
                    ) from e

                # This is a variadic positional argument. Its sequence is the offset
                # with respect to the index of the variadic argument.
                sequence = index - args_by_index.index(argument)
                assert sequence >= 0
                kwargs["var_sequence"] = sequence

                # Form the bound name from the variadic positional argument name and the
                # sequence.
                name = f"{argument.name}{sequence}"
            else:
                name = argument.name
        else:
            # This is a keyword argument.
            try:
                argument = arguments[name_or_index]
            except KeyError as e:
                # This could either be a variadic keyword argument or invalid.
                if var_argument := self.var_keyword_argument:
                    argument = var_argument
                else:
                    raise TypeError(
                        f"keyword argument {repr(name)} does not exist for "
                        f"{repr(self.item_type)}"
                    ) from e

                name = name_or_index
            else:
                name = argument.name

        kwargs["name"] = name
        kwargs["kind"] = argument.kind
        kwargs["default"] = argument.default
        kwargs["annotation"] = argument.annotation

        return BoundArgument(**kwargs)

    def positional_args(self, only=False, keyword_defaults=True):
        """The non-keyword-only arguments of the call signature.

        Parameters
        ----------
        only : :class:`bool`, optional
            Only include positional-only arguments. Defaults to `False`.

        keyword_defaults : :class:`bool`, optional
            Include keyword arguments that have default values. Defaults to `True`.

        Returns
        -------
        :class:`dict`
            The call object's positional parameters.
        """
        kinds = [ArgumentType.POS_ONLY]
        if not only:
            kinds.append(ArgumentType.ANY)
        return self._filter_signature(kinds, keyword_defaults=keyword_defaults)

    def keyword_args(self, only=False):
        """The non-positional-only arguments of the call signature.

        Parameters
        ----------
        only : :class:`bool`, optional
            Only include keyword-only arguments; defaults to `False`.

        Returns
        -------
        :class:`dict`
            The call object's keyword parameters.
        """
        kinds = [ArgumentType.KEYWORD_ONLY]
        if not only:
            kinds.append(ArgumentType.ANY)
        return self._filter_signature(kinds, keyword_defaults=True)

    def _filter_signature(self, kinds, keyword_defaults):
        sig = {}
        for name, argument in self.arguments().items():
            if argument.kind not in kinds:
                continue

            if not keyword_defaults and not argument.has_no_default:
                continue

            sig[name] = argument

        return sig


class ItemDocumenter(ItemHandler, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def docstring(self):
        raise NotImplementedError

    def syntax(
        self,
        spec,
        adapter,
        short_names=True,
        optional_as_positional=False,
        multiline=None,
    ):
        from .generator import KatUnbuilder

        unbuilder = KatUnbuilder(spec=spec)

        if short_names and adapter.short_name is not None:
            item_name = adapter.short_name
        else:
            item_name = adapter.full_name

        syntaxcall = partial(
            self._syntax,
            item_name,
            unbuilder,
            optional_as_positional=optional_as_positional,
        )

        if multiline is None:
            # Return appropriate syntax suggestion based on the console width.
            oneline_syntax = syntaxcall(multiline=False)

            if len(oneline_syntax) > TERMINAL_WIDTH:
                return syntaxcall(multiline=True)
            else:
                return oneline_syntax

        return syntaxcall(multiline=multiline)

    def syntax_correction(
        self, user_directive, spec, optional_as_positional=False, multiline=False
    ):
        """Suggest syntax using the user's directive."""
        from .generator import KatUnbuilder

        unbuilder = KatUnbuilder(spec=spec)

        return self._syntax(
            user_directive,
            unbuilder,
            optional_as_positional=optional_as_positional,
            multiline=multiline,
        )

    @abc.abstractmethod
    def _syntax(self, item_name, unbuilder, optional_as_positional, multiline):
        """Generate syntax for `item_name`."""
        raise NotImplementedError


class SignatureArgumentMixin(metaclass=abc.ABCMeta):
    """Mixin providing ability to retrieve signature arguments from a Python function.

    Parameters
    ----------
    sig_type : type, optional
        The signature type to retrieve arguments from. Defaults to `item_type`.

    sig_ignore : sequence, optional
        Signature argument names to ignore.
    """

    def __init__(self, *, sig_type=None, sig_ignore=None, **kwargs):
        super().__init__(**kwargs)

        if sig_ignore is None:
            sig_ignore = []

        self._sig_type = sig_type
        self._sig_ignore = sig_ignore

    @property
    def sig_type(self):
        sig_type = self._sig_type
        if sig_type is None:
            sig_type = self.item_type
        return sig_type

    def arguments(self):
        arguments = {}

        for name, parameter in inspect.signature(self.sig_type).parameters.items():
            if name in self._sig_ignore:
                continue

            default = parameter.default
            if default is inspect.Parameter.empty:
                default = EMPTY_VALUE

            annotation = parameter.annotation
            if annotation is inspect.Parameter.empty:
                annotation = EMPTY_VALUE

            arguments[name] = Argument(
                name=name,
                kind=_INSPECT_KIND_CONVERSIONS[parameter.kind],
                default=default,
                annotation=annotation,
            )

        return arguments


class SignatureAttributeParameterMixin(SignatureArgumentMixin, metaclass=abc.ABCMeta):
    """Mixin providing the ability to get and set item parameters by inspecting its
    constructor signature arguments matching equivalently named object attributes.

    Parameters
    ----------
    ref_args : sequence, optional
        Names of arguments that should be considered to be references. Corresponding
        :class:`.ArgumentDump` objects produced by this class will have their
        `reference` flags set to `True` to indicate to the generator that these should
        be treated as references instead of values.

    var_pos_attr : str or callable, optional
        The name of the field containing a sequence of variadic positional argument
        values, or a callable that returns the name of the field to set given the
        sequence number of the variadic argument, if the signature supports variadic
        positional arguments. Defaults to `"args"`.

    var_keyword_attr : str or callable, optional
        The name of the field containing a mapping of variadic keyword arguments to
        values, or a callable that returns the name of the field to set given the name
        of the keyword argument, if the signature supports variadic positional
        arguments. Defaults to the identity function.
    """

    def __init__(
        self, ref_args=None, var_pos_attr=None, var_keyword_attr=None, **kwargs
    ):
        super().__init__(**kwargs)

        if ref_args is None:
            ref_args = []
        self.ref_args = ref_args

        if var_pos_attr is None:
            var_pos_attr = "args"
        self.var_pos_attr = var_pos_attr

        if var_keyword_attr is None:
            var_keyword_attr = lambda field: field
        self.var_keyword_attr = var_keyword_attr

    def dump_parameters(self, adapter, item):
        """Build parameter mapping by retrieving object attributes using the
        signature."""
        # Get type hints for the dump signature type.
        #
        # NOTE: this information is also included in the :class:`inspect.Parameter`
        # objects returned by :func:`inspect.signature` used below, but these are
        # potentially unresolved due to Python 3.9+'s lazily evaluation of
        # annotations (see PEP 563). Instead we use the typing module to grab the
        # resolved type, which is the way recommended by the Python docs.
        hints = get_type_hints(self.sig_type)

        values = self._parameter_values(adapter, item)
        arguments = self.arguments().values()
        dump_parameters = {}
        for param, value in zip(arguments, values):
            ref_name = param.name
            if param.kind in (ArgumentType.VAR_POS, ArgumentType.VAR_KEYWORD):
                ref_name = f"*{ref_name}"

            if ref_name in self.ref_args:
                assert isinstance(value, Parameter)
                LOGGER.debug(
                    f"dumping parameter {repr(value)} by reference as it represents a "
                    f"target"
                )
                reference = True
            else:
                reference = False

            dump_parameters[param.name] = ArgumentDump(
                param.name,
                value=value,
                default=param.default,
                kind=param.kind,
                annotation=hints.get(param.name),
                reference=reference,
            )

        return dump_parameters

    def _parameter_values(self, adapter, item):
        values = []

        for arg, param in self.arguments().items():
            name = param.name

            try:
                # Try to get the attribute value.
                value = getattr(item, name)
            except AttributeError as e:
                expected_attrib = f"{item.__class__.__name__}.{name}"
                error_msg = (
                    f"Error while generating parameter {repr(name)} from {repr(item)} "
                    f"for instruction {repr(adapter.full_name)}. The adapter for this "
                    f"object, {repr(adapter)}, specifies that parameters should be "
                    f"generated by looking for attributes or properties in the object "
                    f"corresponding to the names of the arguments in the constructor "
                    f"signature, {repr(self.sig_type)}; yet, no attribute "
                    f"{repr(expected_attrib)} was found. To fix this, ensure that this "
                    f"attribute or property is defined, or specify a different type of "
                    f"{ItemDumper.__name__} class as the 'getter' for the directive in "
                    f"the language specification."
                )

                raise NotImplementedError(error_msg) from e

            values.append(value)

        return values

    def update_parameter(self, item, argument, value):
        if argument.kind is ArgumentType.VAR_POS:
            # This is a variadic positional argument.
            try:
                field = self.var_pos_attr(argument.var_index)
            except TypeError:
                field = self.var_pos_attr
        elif argument.kind is ArgumentType.VAR_KEYWORD:
            # This is a variadic keyword argument.
            try:
                field = self.var_keyword_attr(argument.name)
            except TypeError:
                field = self.var_keyword_attr
        else:
            # This is an ordinary positional or keyword argument.
            field = argument.name

        if not hasattr(item, field):
            # The setter is probably incorrectly configured.
            raise RuntimeError(
                f"cannot set {repr(argument.name)} for item {repr(item)} "
                f"(attribute {repr(field)} does not exist)"
            )

        setattr(item, field, value)


class NumpyStyleDocstringGetterMixin(metaclass=abc.ABCMeta):
    def __init__(self, *, doc_type=None, **kwargs):
        super().__init__(**kwargs)
        self._doc_type = doc_type

    @property
    def doc_type(self):
        doc_type = self._doc_type
        if doc_type is None:
            doc_type = self.item_type
        return doc_type

    @property
    def docstring(self):
        """The Python API item's docstring.

        Note: unlike :func:`inspect.getdoc`, this method returns only the docstring
        directly defined in `doc_type`, rather than taking the inherited docstring if
        not found. If no docstring is defined, `None` is returned.
        """
        try:
            doc = self.doc_type.__doc__
        except AttributeError:
            return None

        if doc is not None:
            doc = inspect.cleandoc(doc)

        return doc

    @cached_property
    def _parsed_docstring_obj(self):
        from finesse_numpydoc import NumpyDocString

        docstring = self.docstring
        if docstring is None:
            docstring = ""

        return NumpyDocString(docstring)

    def summary(self):
        """The item's summary, parsed from the docstring."""
        return self._docutils_implode(self._parsed_docstring_obj["Summary"])

    def argument_descriptions(self):
        """The types and descriptions for each argument as parsed from the docstring.

        Returns
        -------
        :class:`dict`
            Mapping of arguments to their type and docstrings as listed in the object's
            docstring. Note that the arguments may not correspond to signature argument
            names; numpydoc allows arguments to share docstrings so some keys may be
            e.g. `n, m`.
        """
        return {
            name: (type_, self._docutils_implode(description))
            for name, type_, description in self._parsed_docstring_obj["Parameters"]
        }

    def _docutils_implode(self, pieces):
        """Join docutils list of strings into a single string."""
        if not pieces:
            return None
        return " ".join(pieces)


class ElementDumper(SignatureAttributeParameterMixin, ItemDumper):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self", "name"],
            **kwargs,
        )

    def __call__(self, adapter, model):
        """Get element dump object(s) from `model`.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The adapter corresponding to this getter.

        model : :class:`.Model`
            The model from which to dump element(s) of this type.

        Yields
        ------
        :class:`.ElementDump`
            Object containing a mapping of keyword argument names to
            :class:`.ArgumentDump` objects and whether they are all default values.
        """
        for element in model.get_elements_of_type(self.item_type):
            parameters = self.dump_parameters(adapter, element)

            yield ElementDump(
                element=element,
                adapter=adapter,
                parameters=parameters,
                # The only element that is in a model by default is Fsig, which is
                # handled separately.
                is_default=False,
            )


@dataclass
class ElementDump:
    """A set of element parameters and metadata."""

    element: ModelElement
    adapter: ItemAdapter
    parameters: Union[List[ArgumentDump], List[List[ArgumentDump]]]
    is_default: bool


class AnalysisDumper(SignatureAttributeParameterMixin, ItemDumper):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self"],
            **kwargs,
        )

    def __call__(self, adapter, model):
        """Get analysis dump object(s) from `model`.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The adapter corresponding to this getter.

        model : :class:`.Model`
            The model from which to dump analysis (or analyses) of this type.

        Yields
        ------
        :class:`.AnalysisDump`
            Object containing a mapping of keyword argument names to
            :class:`.ArgumentDump` objects and whether they are all default values.
        """
        # Only yield something if there is an analysis to dump.
        if model.analysis is None:
            return

        yield from self.dump(adapter, model.analysis)

    def dump(self, adapter, analysis):
        """Get analysis dump object(s) for `analysis`.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The adapter corresponding to this getter.

        analysis : :class:`.Action`
            The action to dump.

        Yields
        ------
        :class:`.AnalysisDump`
            Object containing a mapping of keyword argument names to
            :class:`.ArgumentDump` objects and whether they are all default values.
        """
        # Only yield something if the analysis is an exact type match.
        if type(analysis) is not self.item_type:
            return

        parameters = self.dump_parameters(adapter, analysis)

        yield AnalysisDump(
            analysis=analysis,
            adapter=adapter,
            parameters=parameters,
            is_default=False,  # There is no default analysis in models.
        )


@dataclass
class AnalysisDump:
    """A set of analysis parameters and metadata."""

    analysis: Any  # FIXME: We should have an Analysis type.
    adapter: ItemAdapter
    parameters: Union[List[ArgumentDump], List[List[ArgumentDump]]]
    is_default: bool

    @property
    def item_name(self):
        return self.analysis.__class__.__name__


class ElementFactory(ItemFactory):
    def __init__(self, last=False, **kwargs):
        super().__init__(**kwargs)
        self.last = last

    def __call__(self, *args, **kwargs):
        return self.item_type(*args, **kwargs)


class ElementSetter(SignatureAttributeParameterMixin, ItemSetter):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self", "name"],
            **kwargs,
        )

    def __call__(self, model, item):
        model.add(item)


class AnalysisFactory(ItemFactory):
    def __call__(self, *args, **kwargs):
        return self.item_type(*args, **kwargs)


class AnalysisSetter(SignatureAttributeParameterMixin, ItemSetter):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self"],
            **kwargs,
        )

    def __call__(self, model, item):
        model.analysis = item


class SyntaxMixin(SignatureArgumentMixin, metaclass=abc.ABCMeta):
    def _argument_syntax(self, unbuilder, optional_as_positional):
        """Sequence of formatted, ordered argument syntax."""
        parameters = self.arguments()

        positional = []
        var_positional = None
        keyword = []
        var_keyword = None

        for name, param in parameters.items():
            kind = param.kind

            if kind is ArgumentType.VAR_POS:
                var_positional = f"*{name}"
                continue
            elif kind is ArgumentType.VAR_KEYWORD:
                var_keyword = f"**{name}"
                continue
            elif kind is ArgumentType.ANY:
                if optional_as_positional or param.has_no_default:
                    kind = ArgumentType.POS_ONLY
                else:
                    kind = ArgumentType.KEYWORD_ONLY

            if kind is ArgumentType.POS_ONLY:
                positional.append(name)
            else:
                default = unbuilder.unbuild(param.default)
                keyword.append(f"{name}={default}")

        # Stack arguments in the correct order.
        items = positional
        if var_positional:
            items.append(var_positional)
        items.extend(keyword)
        if var_keyword:
            items.append(var_keyword)
        return items


class ElementSyntaxMixin(SyntaxMixin, metaclass=abc.ABCMeta):
    def _syntax(self, item_name, unbuilder, multiline, **kwargs):
        # Multiline is ignored.
        args = self._argument_syntax(unbuilder, **kwargs)
        argstr = " " + " ".join(args) if args else " "
        return f"{item_name} name{argstr}"


class FunctionalSyntaxMixin(SyntaxMixin, metaclass=abc.ABCMeta):
    def _syntax(self, item_name, unbuilder, multiline, **kwargs):
        args = self._argument_syntax(unbuilder, **kwargs)

        if multiline:
            mlargs = []
            for arg in args:
                mlargs.append(f"{INDENT}{arg}")
            mlargstr = ",\n".join(mlargs)
            syntax = f"{item_name}(\n{mlargstr}\n)"
        else:
            argstr = ", ".join(args) if args else ""
            syntax = f"{item_name}({argstr})"

        return syntax


class ElementDocumenter(
    NumpyStyleDocstringGetterMixin, ElementSyntaxMixin, ItemDocumenter
):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self", "name"],
            **kwargs,
        )


class AnalysisDocumenter(
    NumpyStyleDocstringGetterMixin, FunctionalSyntaxMixin, ItemDocumenter
):
    def __init__(self, *, item_type, **kwargs):
        super().__init__(
            item_type=item_type,
            sig_type=item_type.__init__,
            sig_ignore=["self"],
            **kwargs,
        )


class CommandMethodSetter(SignatureAttributeParameterMixin, ItemSetter):
    def __init__(self, *, sig_ignore=("self",), **kwargs):
        super().__init__(sig_ignore=sig_ignore, **kwargs)

    def __call__(self, model, argskwargs):
        args, kwargs = argskwargs

        # Wrap the call in a partial so that invalid argument errors correctly
        # correspond to those available in the script instruction.
        setter = partial(self.item_type, model)
        setter(*args, **kwargs)


class CommandMethodDocumenter(
    NumpyStyleDocstringGetterMixin, FunctionalSyntaxMixin, ItemDocumenter
):
    def __init__(self, *, sig_ignore=("self",), **kwargs):
        super().__init__(sig_ignore=sig_ignore, **kwargs)


class CommandPropertyDumper(SignatureAttributeParameterMixin, ItemDumper):
    def __init__(self, *, item_type, default=EMPTY_VALUE, **kwargs):
        assert isinstance(item_type, property)

        # The sig_type is the setter because we use the setter to add metadata to the
        # ArgumentDump below.
        super().__init__(
            item_type=item_type,
            sig_type=item_type.fset,
            sig_ignore=("self",),
            **kwargs,
        )
        self._prop_default = default

    def __call__(self, adapter, model):
        arguments = self.arguments()
        assert len(arguments) == 1
        argument = next(iter(arguments.values()))

        if self._prop_default is not EMPTY_VALUE:
            if (
                argument.default is not EMPTY_VALUE
                and self._prop_default != argument.default
            ):
                raise RuntimeError(
                    f"default specified in spec, {repr(self._prop_default)}, differs "
                    f"from that specified in the property setter, "
                    f"{repr(argument.default)}"
                )

            default = self._prop_default
        else:
            default = argument.default

        parameter = ArgumentDump(
            argument.name,
            value=self.item_type.fget(model),
            default=default,
            kind=argument.kind,
        )

        yield CommandDump(
            adapter=adapter,
            parameters={argument.name: parameter},
            is_default=parameter.is_default,
        )


class CommandPropertyDocumenter(CommandMethodDocumenter):
    def __init__(self, *, item_type, **kwargs):
        assert isinstance(item_type, property)
        super().__init__(
            item_type=item_type,
            sig_type=item_type.fset,
            doc_type=item_type.fset,
            **kwargs,
        )


class CommandPropertySetter(CommandMethodSetter):
    def __init__(self, *, item_type, **kwargs):
        assert isinstance(item_type, property)
        super().__init__(item_type=item_type, **kwargs)

    def __call__(self, model, argskwargs):
        args, kwargs = argskwargs

        # Wrap the call in a partial so that invalid argument errors correctly
        # correspond to those available in the script instruction.
        setter = partial(self.item_type.fset, model)
        setter(*args, **kwargs)


@dataclass
class CommandDump:
    """A set of command parameters and metadata."""

    adapter: ItemAdapter
    parameters: Union[List[ArgumentDump], List[List[ArgumentDump]]]
    is_default: bool

    @property
    def item_name(self):
        return self.adapter.full_name
