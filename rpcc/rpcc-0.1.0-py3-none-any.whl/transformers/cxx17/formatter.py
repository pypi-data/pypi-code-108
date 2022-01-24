# Copyright 2021-2022, Barcelona Supercomputing Center (BSC), Spain
#
# This software was partially supported by the EuroHPC-funded project ADMIRE
#   (Project ID: 956748, https://www.admire-eurohpc.eu).
#
# This file is part of rpcc.
#
# rpcc is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# rpcc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with rpcc.  If not, see
# <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import itertools
import pathlib
import re
from typing import Optional, Union, Callable, Iterable, Tuple, List

from loguru import logger

from rpcc.ir import Argument, ReturnValue, RemoteProcedure, IRTree, ConditionalDefinition
from rpcc.transformers.cxx17.types import (
    CxxType, Integer, Double, String, Object, NameSpace, ReferenceType, Identifier, ConstLValueReference,
    RValueReference
)


class CxxParameterListFormatter:
    """Format a list of C++ function parameters."""

    sep: str = ", "

    def format(self, params: Callable[..., Iterable[Identifier]]) -> str:
        """Generate C++ code for a parameter list.

        :param params: A function that generates the parameters that should appear in the list.
        :return: A string with the generated C++ code.

        Example:
            >>> CxxParameterListFormatter().format(
            >>>     lambda: iter([
            >>>         Identifier("a", Integer(32, False)),
            >>>         Identifier("b", Double()),
            >>>         ConstLValueReference("c", String())
            >>> ]))
            'int a, double b, const std::string& c'
        """
        return self.sep.join(p.as_declarator() for p in params())


class CxxInitializerListFormatter:
    """Format a C++ member initializer list."""

    sep: str = ", "

    @staticmethod
    def _format_init_expr(member: Identifier, param: Identifier) -> str:
        if not member:
            return ""

        if not param:
            return f"{member}()"

        return f"{member}({param.as_member_of()})"

    def format(self, params: Callable[..., Iterable[Identifier]], members: Callable[..., Iterable[Identifier]]) -> str:

        init_list = self.sep.join(
            itertools.starmap(CxxInitializerListFormatter._format_init_expr,
                              itertools.zip_longest(members(), params())))

        if init_list:
            return f": {init_list}"
        return init_list


class CxxConstructorFormatter:
    """Format a C++ constructor function."""

    classname: str
    template: str = """\
{decl_specifier}{classname}({params}){initializers} {body}\n"""

    def __init__(self, classname: str) -> None:
        self.classname = classname

    def format(self, explicit: bool, ctor_params: Callable[..., Iterable[Identifier]],
               class_members: Callable[..., Iterable[Identifier]], body=None) -> str:
        return self.template.format(
            decl_specifier="explicit\n" if explicit else "",
            classname=self.classname,
            params=CxxParameterListFormatter().format(ctor_params),
            initializers=CxxInitializerListFormatter().format(ctor_params, class_members),
            body=body or "{ }"
        )


class CxxConvertingConstructorFormatter:
    """Format a C++ converting constructor function."""

    classname: str
    template: str = """\
{decl_specifier}{classname}({params}){initializers} {body}\n"""

    def __init__(self, classname: str) -> None:
        """ Create a `ConvertingConstructorFormatter` given a class name.

        :param classname: The output class name created by the constructor.
        """
        self.classname = classname

    def format(self, explicit: bool, class_members: Callable[..., Iterable[Identifier]], ctor_param: Identifier,
               member_values: Callable[..., Iterable[Identifier]], body: object = None) -> str:
        """Generate a C++ converting constructor.

        :param explicit: Whether the constructor should be explicit or not.
        :param ctor_param: The constructor parameter that should be converted to `classname`.
        :param class_members: The class members of `classname` that should be initialized when converting.
        :param member_values: The values from `ctor_param` that should be used to initialize `class_members`
        :param body: The body of the constructor.
        :return: A string with the generated code.
        """
        init_list = CxxInitializerListFormatter().format(class_members, member_values)

        if not init_list:
            body = f"{{ (void) {ctor_param}; }}"

        return self.template.format(
            decl_specifier="explicit\n" if explicit else "",
            classname=self.classname,
            params=CxxParameterListFormatter().format(lambda: iter([ctor_param])),
            initializers=init_list,
            body=body or "{ }"
        )


class CxxConvertingOperatorFormatter:
    """Format a C++ converting operator."""

    template: str = """\
{decl_specifier}operator {conversion_type}() {{
    return {{ {converting_operator_retval} }};
}}\n"""

    def format(self, explicit: bool, conversion_type: CxxType, conversion_func: Callable[[Identifier], str],
               values: Callable[..., Iterable[Identifier]]) -> str:
        return self.template.format(
            decl_specifier="explicit\n" if explicit else "",
            conversion_type=conversion_type,
            converting_operator_retval=CxxBracedInitializerListFormatter().format(conversion_func, values),
        )


class CxxFunctionFormatter:
    """Format a C++ function."""

    template: str = """\
{return_type} {func_name}({parameter_list}) {cv} {body}\n"""

    def format(self, return_type: CxxType, func_name: str, func_params: Callable[..., Iterable[Identifier]],
               is_const: bool,
               body: Optional[str] = None):
        return self.template.format(
            return_type=return_type,
            func_name=func_name,
            parameter_list=CxxParameterListFormatter().format(func_params),
            cv="const" if is_const else "",
            body=body or "{ }"
        )


class CxxBracedInitializerListFormatter:
    """Format a C++ brace-enclosed initializer list."""

    mapping_func: Callable
    sep: str = ",\n"

    def format(self, func: Callable[[Identifier], str], values: Callable[..., Iterable[Identifier]]):
        return self.sep.join(map(func, values()))


HERMES_NAMESPACE = NameSpace("hermes::detail")
HG_VOID = Object("hg_void_t", HERMES_NAMESPACE)

INPUT_CLASS_NAME = "input"
OUTPUT_CLASS_NAME = "output"
CONSTRUCTOR_VISIBILITY = "public"
OPERATOR_VISIBILITY = "public"
GETTER_VISIBILITY = "public"
MEMBER_VISIBILITY = "private"

RpcVar = Union[Argument, ReturnValue]


def as_members(args: Iterable[RpcVar], owner: Optional[Identifier] = None) -> Iterable[Identifier]:
    """Given a list of RPC variables, generate a sequence of appropriately formatted C++ class members.

    :param args: The list of RPC variables
    :param owner: An optional class instance owner for the member.
    """
    for a in args:
        yield Identifier("m_" + a.id, a.typeinfo, owner)


def as_function_parameters(args: Iterable[RpcVar]) -> Iterable[Identifier]:
    """Given a list of RPC variables, generate a sequence of appropriately formatted C++ function parameters.
    Fundamental types are formatted as by-value types, while compound types are formatted as const l-value references.

    :param args: The list of RPC variables
    """
    for a in args:
        if a.typeinfo.is_fundamental():
            yield Identifier(a.id, a.typeinfo)
        else:
            yield ConstLValueReference(a.id, a.typeinfo)


class _InnerClassFormatter:
    rpcname: str
    classname: str
    hg_type: Object
    params: Iterable[RpcVar]
    template: str = """\
class {classname} {{

    template <typename ExecutionContext>
    friend hg_return_t hermes::detail::post_to_mercury(ExecutionContext*);

    {constructors}

    {operators}

    {getters}

    {members}
}};\n"""

    def __init__(self, rpcname: str, classname: str, hg_type: Object):
        self.rpcname = rpcname
        self.classname = classname
        self.hg_type = hg_type

    def format(self, rpc_vars: Iterable[RpcVar]):
        return self.template.format(
            rpc_name=self.rpcname,
            classname=self.classname,
            constructors=self._format_constructors(CONSTRUCTOR_VISIBILITY, rpc_vars, sep="\n"),
            operators=self._format_operators(OPERATOR_VISIBILITY, rpc_vars, sep="\n"),
            getters=self._format_getters(GETTER_VISIBILITY, rpc_vars, sep="\n"),
            members=self._format_members(MEMBER_VISIBILITY, rpc_vars, sep="\n")
        )

    def _format_constructors(self, visibility: str, args: Iterable[RpcVar], sep: str) -> str:
        """Generate C++ code for the set of constructors required by this RPC inner class.

        The following constructors are generated:
            - A constructor for default-initialized members
            - A parameterized constructor (unless `args` contains no variables)
            - A copy constructor
            - A move constructor
            - A converting constructor

        :param visibility: The visibility that should be used for the generated constructors. Valid values are `public`,
        `private`, or `protected`.
        :param args: The RPC variables (arguments or return variables) that define this RPC.
        :param sep: The separator that should be used to separate constructor code.
        :return: A string with the generated C++ code.
        """

        if visibility not in ["public", "private", "protected"]:
            raise ValueError(f"Unexpected value '{visibility}' for constructor visibility")

        # constructor for default-initialized members
        logger.info(f"formatting constructor for '{self.classname}' default-initialized members")
        constructors = [
            CxxConstructorFormatter(self.classname).format(
                explicit=False,
                ctor_params=lambda: iter([]),
                class_members=lambda: as_members(args)
            )]
        logger.info(f"output:\n'{constructors[-1]}'")

        # parameterized constructor (only if args is not empty)
        if args:
            logger.info(f"formatting parameterized constructor for '{self.classname}'")
            constructors.append(
                CxxConstructorFormatter(self.classname).format(
                    explicit=False,
                    ctor_params=lambda: as_function_parameters(args),
                    class_members=lambda: as_members(args)
                ))
            logger.info(f"output:\n'{constructors[-1]}'")

        # move constructor
        logger.info(f"formatting move constructor for '{self.classname}'")
        constructors.append(
            CxxConstructorFormatter(self.classname).format(
                explicit=False,
                ctor_params=lambda: iter([RValueReference("rhs", Object(self.classname))]),
                class_members=lambda: iter([]),
                body="= default;"
            )
        )
        logger.info(f"output:\n'{constructors[-1]}'")

        # copy constructor
        logger.info(f"formatting copy constructor for '{self.classname}'")
        constructors.append(
            CxxConstructorFormatter(self.classname).format(
                explicit=False,
                ctor_params=lambda: iter([ConstLValueReference("other", Object(self.classname))]),
                class_members=lambda: iter([]),
                body="= default;"
            )
        )
        logger.info(f"output:\n'{constructors[-1]}'")

        # converting constructor
        logger.info(f"formatting converting constructor for '{self.classname}'")
        owner = ConstLValueReference("other", self.hg_type)
        constructors.append(
            CxxConvertingConstructorFormatter(self.classname).format(
                explicit=True,
                class_members=lambda: as_members(args, owner),
                ctor_param=owner,
                member_values=lambda: as_members(args))
        )
        logger.info(f"output:\n'{constructors[-1]}'")

        return f"{visibility}:\n" + sep.join(constructors)

    def _format_operators(self, visibility: str, args: Iterable[RpcVar], sep: str) -> str:
        """Generate C++ code for the set of operators required by this RPC inner class.

        The following operators are generated:
            - A move-assignment operator
            - An assignment operator
            - A conversion operator

        :param visibility: The visibility that should be used for the generated constructors. Valid values are `public`,
        `private`, or `protected`.
        :param args: The RPC variables (arguments or return variables) that define this RPC.
        :param sep: The separator that should be used to separate constructor code.
        :return: A string with the generated C++ code.
        """

        # move-assignment operator
        logger.info(f"formatting move-assignment operator for '{self.classname}'")
        operators = [
            CxxFunctionFormatter().format(
                return_type=ReferenceType(Object(self.classname)),
                func_name="operator=",
                func_params=lambda: iter([RValueReference("rhs", Object(self.classname))]),
                is_const=False,
                body="= default;"
            )
        ]
        logger.info(f"output:\n'{operators[-1]}'")

        # assignment operator
        logger.info(f"formatting assignment operator for '{self.classname}'")
        operators.append(
            CxxFunctionFormatter().format(
                return_type=ReferenceType(Object(self.classname)),
                func_name="operator=",
                func_params=lambda: iter([ConstLValueReference("other", Object(self.classname))]),
                is_const=False,
                body="= default;"
            )
        )
        logger.info(f"output:\n'{operators[-1]}'")

        # conversion operator
        logger.info(f"formatting converting operator for '{self.classname}'")
        operators.append(
            CxxConvertingOperatorFormatter().format(
                explicit=True,
                conversion_type=self.hg_type,
                conversion_func=lambda ident: ident.as_hg_conversion(),
                values=lambda: as_members(args),
            )
        )
        logger.info(f"output:\n'{operators[-1]}'")

        return f"{visibility}:\n" + sep.join(operators)

    def _format_getters(self, visibility: str, args: Iterable[RpcVar], sep) -> str:
        return ((f"{visibility}:\n" if args else "") +
                sep.join(map(lambda m:
                             CxxFunctionFormatter().format(
                                 return_type=m.typeinfo,
                                 func_name=m.id.replace('m_', ''),
                                 func_params=lambda: iter([]),
                                 is_const=True,
                                 body=f"{{ return {m.id}; }}"
                             ), as_members(args))
                         )
                )

    def _format_members(self, visibility: str, args: Iterable[RpcVar], sep) -> str:
        return ((f"{visibility}:\n" if args else "") +
                sep.join(f"{m.as_declarator()};" for m in as_members(args))
                )


class _RemoteProcedureFormatter:
    rpc: RemoteProcedure
    hg_input_type: Object = HG_VOID
    hg_output_type: Object = HG_VOID
    decl_template: str = """\
//==============================================================================
// definitions for {rpc_name}
namespace hermes::detail {{

// Generate Mercury types and serialization functions (field names match
// those defined in {rpc_name}::input and {rpc_name}::output). These
// definitions are internal and should not be used directly. Classes
// {rpc_name}::input and {rpc_name}::output are provided for public use.
{hg_input_type_definition}

{hg_output_type_definition}

}} // namespace hermes::detail

struct {rpc_name} {{

// forward declarations of public input/output types for this RPC
class input;

class output;

// traits used so that the engine knows what to do with the RPC
using self_type = {rpc_name};
using handle_type = hermes::rpc_handle<self_type>;
using input_type = input;
using output_type = output;
using mercury_input_type = {hg_input_type};
using mercury_output_type = {hg_output_type};

// RPC public identifier
constexpr static const uint64_t public_id = {rpc_id};

// RPC internal Mercury identifier
constexpr static const hg_id_t mercury_id = public_id;

// RPC name
constexpr static const auto name = "{rpc_name}";

// requires response?
constexpr static const auto requires_response = true;

// Mercury callback to serialize input arguments
constexpr static const auto mercury_in_proc_cb = 
    {hg_input_type_callback};

// Mercury callback to serialize output arguments
constexpr static const auto mercury_out_proc_cb = 
    {hg_output_type_callback};

{rpc_args}

{rpc_retval}

}};\n"""

    def_template: str = """\
(void) registered_requests().add <{rpc_name}>();"""

    def __init__(self, rpc: RemoteProcedure):
        self.rpc = rpc
        if len(self.rpc.args):
            self.hg_input_type = Object(f"{self.rpc.name}_in_t", HERMES_NAMESPACE)
        if len(self.rpc.retvals):
            self.hg_output_type = Object(f"{self.rpc.name}_out_t", HERMES_NAMESPACE)

    def _format_hg_type_definition(self, name: str, fields: Iterable[RpcVar]) -> str:

        # hg_void_t is generated elsewhere
        if name == "hg_void_t":
            return ""

        return (f"MERCURY_GEN_PROC(\n" +
                f"{name},\n" +
                "".join(f"(({f.typeinfo.hg_type()}) ({f.id}))" for f in fields) +
                ")"
                )

    def _format_hg_type_callback(self, classname: str, fields: List[RpcVar]) -> str:
        if not len(fields):
            return "hermes::detail::hg_proc_void_t"
        return f"HG_GEN_PROC_NAME({classname})"

    def format_declaration(self):
        logger.info(f"formatting rpc '{self.rpc.name}'")

        expr = self.rpc.include_if_expr

        pre = f"{expr.start_keyword} {expr.symbol}\n\n" if expr else ""
        post = f"{expr.end_keyword} // {expr.symbol}\n\n" if expr else ""

        return (pre +
                self.decl_template.format(
                    rpc_id=self.rpc.id,
                    rpc_name=self.rpc.name,
                    hg_input_type=self.hg_input_type,
                    hg_input_type_definition=self._format_hg_type_definition(self.hg_input_type.classname,
                                                                             self.rpc.args),
                    hg_input_type_callback=self._format_hg_type_callback(self.hg_input_type.classname, self.rpc.args),
                    hg_output_type=self.hg_output_type,
                    hg_output_type_definition=self._format_hg_type_definition(self.hg_output_type.classname,
                                                                              self.rpc.retvals),
                    hg_output_type_callback=self._format_hg_type_callback(self.hg_output_type.classname,
                                                                          self.rpc.retvals),
                    rpc_args=_InnerClassFormatter(
                        self.rpc.name,
                        INPUT_CLASS_NAME,
                        self.hg_input_type
                    ).format(self.rpc.args),
                    rpc_retval=_InnerClassFormatter(
                        self.rpc.name,
                        OUTPUT_CLASS_NAME,
                        self.hg_output_type
                    ).format(self.rpc.retvals),
                ) + "\n" +
                post)

    def format_definition(self, namespace: Optional[str]) -> str:
        rpc_fqname = self.rpc.name
        if namespace:
            rpc_fqname = '::'.join([namespace, rpc_fqname])
        return self.def_template.format(rpc_name=rpc_fqname)


class _HppHeaderFormatter:
    template: str = """\
{copyright_text}
// Generated by rpcc. DO NOT EDIT!
// source: {input_file}

#ifndef {header_guard_name}
#define {header_guard_name}

// C includes
#include <mercury.h>
#include <mercury_proc_string.h>
#include <mercury_macros.h>

// C++ includes
#include <string>

// hermes includes
#include <hermes.hpp>

#ifndef HG_GEN_PROC_NAME
#define HG_GEN_PROC_NAME(struct_type_name) \
    hermes::detail::hg_proc_ ## struct_type_name
#endif

// forward declarations
namespace hermes::detail {{

template <typename ExecutionContext>
hg_return_t post_to_mercury(ExecutionContext* ctx);

struct hg_void_t {{}};

static HG_INLINE hg_return_t
hg_proc_void_t(hg_proc_t proc, void* data) {{
    (void) proc;
    (void) data;

    return HG_SUCCESS;
}}

}} // namespace hermes::detail
"""

    def format(self, input_file: str, copyright_text: str, header_guard: str) -> str:
        return self.template.format(
            header_guard_name=header_guard,
            copyright_text=copyright_text,
            input_file=input_file)


class _HppFooterFormatter:
    template: str = """\
#undef HG_GEN_PROC_NAME

#endif // {header_guard_name}
"""

    def format(self, header_guard: str) -> str:
        return self.template.format(
            header_guard_name=header_guard,
        )


def _format_cxx_namespace(name: str, entry: bool) -> str:
    if entry:
        return f"namespace {name} {{\n"
    return f"}} // namespace {name}\n"


def _format_cxx_conditional_expression(expr: ConditionalDefinition, entry: bool) -> str:
    if entry:
        return f"{expr.start_keyword} {expr.symbol}"
    return f"{expr.end_keyword} // {expr.symbol}"


class _CxxHppFileFormatter:
    @staticmethod
    def _format_cxx_header_guard(input_file: pathlib.Path) -> str:
        prefix = input_file.name
        extensions = input_file.suffixes

        if extensions:
            prefix = re.compile('|'.join(map(re.escape, extensions))).sub('', prefix)

        return f"RPCC_{prefix.upper()}_INCLUDED_HPP"

    @staticmethod
    def format(input_file: pathlib.Path, copyright_text: str, namespace: Optional[str],
               rpcs: Iterable[RemoteProcedure]) -> str:
        return (
                _HppHeaderFormatter().format(
                    input_file=str(input_file),
                    copyright_text=copyright_text,
                    header_guard=_CxxHppFileFormatter._format_cxx_header_guard(input_file)
                ) + "\n" +
                (_format_cxx_namespace(namespace, entry=True) + "\n" if namespace else "") +
                "\n".join(_RemoteProcedureFormatter(rpc).format_declaration() for rpc in rpcs) + "\n" +
                (_format_cxx_namespace(namespace, entry=False) + "\n" if namespace else "") +
                _HppFooterFormatter().format(
                    header_guard=_CxxHppFileFormatter._format_cxx_header_guard(input_file)
                )
        )


class _CppHeaderFormatter:
    template: str = """\
{copyright_text}
// Generated by rpcc. DO NOT EDIT!
// source: {input_file}

// hermes includes
#include <hermes.hpp>
#include "{hpp_file}"

namespace hermes::detail {{

//==============================================================================
// register request types so that they can be used by users and the engine
//
"""

    def format(self, input_file: str, copyright_text: str, hpp_file: str) -> str:
        return self.template.format(
            copyright_text=copyright_text,
            input_file=input_file,
            hpp_file=hpp_file)


class _CppFooterFormatter:
    def format(self) -> str:
        return "\n} // namespace hermes::detail"


class _CxxCppFileFormatter:
    @staticmethod
    def format(input_file: pathlib.Path, copyright_text: str, hpp_file: str, namespace: Optional[str],
               rpcs: Iterable[RemoteProcedure]) -> str:
        return (
                _CppHeaderFormatter().format(
                    input_file=str(input_file),
                    copyright_text=copyright_text,
                    hpp_file=hpp_file
                ) +
                "\n".join(_RemoteProcedureFormatter(rpc).format_definition(namespace) for rpc in rpcs) + "\n" +
                _CppFooterFormatter().format()
        )


class FileFormatter:
    input_file: pathlib.Path
    copyright_file: pathlib.Path
    header_output_path: pathlib.Path
    impl_output_path: pathlib.Path

    def __init__(self, input_file: pathlib.Path, copyright_file: pathlib.Path, header_output_path: pathlib.Path,
                 impl_output_path: pathlib.Path):
        self.input_file = input_file
        self.copyright_file = copyright_file
        self.header_output_path = header_output_path
        self.impl_output_path = impl_output_path

    def format(self, tree: IRTree) -> Tuple[str, str]:
        # since C++17 allows collapsing namespaces, we can just replace '.' with '::' in the package name
        ns = tree.package.replace('.', '::') if tree.package else None

        copyright_text = self.copyright_file.read_text() if self.copyright_file else ""

        hpp_text = _CxxHppFileFormatter.format(
            input_file=self.input_file,
            copyright_text=copyright_text,
            namespace=ns,
            rpcs=tree.rpcs)

        cpp_text = _CxxCppFileFormatter.format(
            input_file=self.input_file,
            copyright_text=copyright_text,
            hpp_file=self.header_output_path.name,
            namespace=ns,
            rpcs=tree.rpcs)

        return hpp_text, cpp_text
