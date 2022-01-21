#!/usr/bin/env python
"""Protoc Plugin to generate protoplus files. Loosely based on mypy's mypy-protobuf implementation"""
import importlib.metadata
import re
import os.path as op
import sys
import warnings
from abc import abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from itertools import groupby, chain
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)

try:
    from importlib.metadata import version
except ImportError: # for Python<3.8
    from importlib_metadata import version

import google.protobuf.descriptor_pb2 as d
from google.protobuf.compiler import plugin_pb2 as plugin_pb2
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.internal.well_known_types import WKTBASES
from google.protobuf.message import DecodeError

__dist__ = 'codestare-proto-plus'
try:
    __version__ = version(__dist__)
except importlib.metadata.PackageNotFoundError:
    print(f"Distribution {__dist__} is not installed.")

# SourceCodeLocation is defined by `message Location` here
# https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/descriptor.proto
SourceCodeLocation = List[int]

# So phabricator doesn't think codestare-proto-plus.py is generated
GENERATED = "@ge" + "nerated"
HEADER = f"""\"\"\"
{GENERATED} by codestare-proto-plus.  Do not edit manually!
isort:skip_file
\"\"\"
"""

# See https://github.com/dropbox/mypy-protobuf/issues/73 for details
PYTHON_RESERVED = {
    "False",
    "None",
    "True",
    "and",
    "as",
    "async",
    "await",
    "assert",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
}

PROTO_ENUM_RESERVED = {
    "Name",
    "Value",
    "keys",
    "values",
    "items",
}


def removeprefix(value: str, prefix=None):
    if sys.version_info >= (3, 9):
        return value.removeprefix(prefix or '')
    else:
        return value[len(prefix):] if value.startswith(prefix) else value


def _mangle_global_identifier(name: str) -> str:
    """
    Module level identifiers are mangled and aliased so that they can be disambiguated
    from fields/enum variants with the same name within the file.

    Eg:
    Enum variant `Name` or message field `Name` might conflict with a top level
    message or enum named `Name`, so mangle it with a global___ prefix for
    internal references. Note that this doesn't affect inner enums/messages
    because they get fuly qualified when referenced within a file"""
    return f"global___{name}"


class Descriptors(object):
    def __init__(self, request: plugin_pb2.CodeGeneratorRequest) -> None:
        files = {f.name: f for f in request.proto_file}
        to_generate = {n: files[n] for n in request.file_to_generate}
        self.files: Dict[str, d.FileDescriptorProto] = files
        self.to_generate: Dict[str, d.FileDescriptorProto] = to_generate
        self.messages: Dict[str, d.DescriptorProto] = {}
        self.message_to_fd: Dict[str, d.FileDescriptorProto] = {}

        def _add_enums(
                enums: "RepeatedCompositeFieldContainer[d.EnumDescriptorProto]",
                prefix: str,
                _fd: d.FileDescriptorProto,
        ) -> None:
            for enum in enums:
                self.message_to_fd[prefix + enum.name] = _fd
                self.message_to_fd[prefix + enum.name + ".ValueType"] = _fd

        def _add_messages(
                messages: "RepeatedCompositeFieldContainer[d.DescriptorProto]",
                prefix: str,
                _fd: d.FileDescriptorProto,
        ) -> None:
            for message in messages:
                self.messages[prefix + message.name] = message
                self.message_to_fd[prefix + message.name] = _fd
                sub_prefix = prefix + message.name + "."
                _add_messages(message.nested_type, sub_prefix, _fd)
                _add_enums(message.enum_type, sub_prefix, _fd)

        for fd in request.proto_file:
            start_prefix = "." + fd.package + "." if fd.package else "."
            _add_messages(fd.message_type, start_prefix, fd)
            _add_enums(fd.enum_type, start_prefix, fd)


class Writer(object):
    def __init__(
            self,
            fd: d.FileDescriptorProto,
            descriptors: Descriptors,
            readable_imports: bool = False,
    ) -> None:
        self.fd = fd
        self.descriptors = descriptors
        self.readable_imports = readable_imports
        self.lines: List[str] = []
        self.indent = ""

        # Set of {x}, where {x} corresponds to to `import {x}`
        self.imports: Set[str] = set()
        # dictionary of x->(y,z) for `from {x} import {y} as {z}`
        # if {z} is None, then it shortens to `from {x} import {y}`
        self.from_imports: Dict[str, Set[Tuple[str, Optional[str]]]] = defaultdict(set)

    def _import(self, path: str, name: str) -> str:
        """Imports a stdlib path and returns a handle to it
        eg. self._import("typing", "Optional") -> "Optional"
        """
        imp = path.replace("/", ".")
        if self.readable_imports:
            self.from_imports[imp].add((name, None))
            return name
        else:
            self.imports.add(imp)
            return imp + "." + name

    def _builtin(self, name: str) -> str:
        return self._import("builtins", name)

    @contextmanager
    def _indent(self) -> Iterator[None]:
        self.indent = self.indent + "    "
        yield
        self.indent = self.indent[:-4]

    def _write_line(self, line: str, *args: Any) -> None:
        if args:
            line = line.format(*args)
        if line == "":
            self.lines.append(line)
        else:
            self.lines.append(self.indent + line)

    def _break_text(self, text_block: str) -> List[str]:
        if text_block == "":
            return []
        return [
            l[1:] if l.startswith(" ") else l for l in text_block.rstrip().split("\n")
        ]

    @abstractmethod
    def write_module_attributes(self) -> None:
        ...

    def write(self) -> str:
        import_lines = []
        for pkg in sorted(self.imports):
            import_lines.append(f"import {pkg}")

        for pkg, items in sorted(self.from_imports.items()):
            import_lines.append(f"from {pkg} import (")
            for (name, reexport_name) in sorted(items):
                if reexport_name is None:
                    import_lines.append(f"    {name},")
                else:
                    import_lines.append(f"    {name} as {reexport_name},")
            import_lines.append(")\n")
        import_lines.append("")

        return "\n".join(import_lines + self.lines)

    def _import_message(self, name: str) -> str:
        """Import a referenced message and return a handle"""
        message_fd = self.descriptors.message_to_fd[name]
        assert message_fd.name.endswith(".proto")

        # Strip off package name
        if message_fd.package:
            assert name.startswith("." + message_fd.package + ".")
            name = name[len("." + message_fd.package + "."):]
        else:
            assert name.startswith(".")
            name = name[1:]

        # Use prepended "_r_" to disambiguate message names that alias python reserved keywords
        split = name.split(".")
        for i, part in enumerate(split):
            if part in PYTHON_RESERVED:
                split[i] = "_r_" + part
        name = ".".join(split)

        # Message defined in this file.
        if message_fd.name == self.fd.name:
            return name

        # Not in file. Must import
        # Python generated code ignores proto packages, so the only relevant factor is
        # whether it is in the file or not.
        import_name = self._import(
            message_fd.name[:-6].replace("-", "_") + "_pb_plus", split[0]
        )

        remains = ".".join(split[1:])
        if not remains:
            return import_name

        # remains could either be a direct import of a nested enum or message
        # from another package.
        return import_name + "." + remains


class PkgWriter(Writer):
    """Writes a single pb_plus.py file"""

    _current_working_class = None

    @contextmanager
    def working_class(self, value):
        previous = self._current_working_class
        self._current_working_class = value
        yield self._current_working_class
        self._current_working_class = previous

    def __init__(
            self,
            fd: d.FileDescriptorProto,
            descriptors: Descriptors,
            readable_imports: bool = False,
            package=None,
    ) -> None:
        super().__init__(fd, descriptors, readable_imports)
        self.package = package
        self.source_code_info_by_scl = {
            tuple(location.path): location for location in fd.source_code_info.location
        }

    def _has_comments(self, scl: SourceCodeLocation) -> bool:
        sci_loc = self.source_code_info_by_scl.get(tuple(scl))
        return sci_loc is not None and bool(
            sci_loc.leading_detached_comments
            or sci_loc.leading_comments
            or sci_loc.trailing_comments
        )

    def _write_comments(self, scl: SourceCodeLocation) -> bool:
        """Return true if any comments were written"""
        if not self._has_comments(scl):
            return False

        sci_loc = self.source_code_info_by_scl.get(tuple(scl))
        assert sci_loc is not None

        lines = []
        for leading_detached_comment in sci_loc.leading_detached_comments:
            lines.extend(self._break_text(leading_detached_comment))
            lines.append("")
        if sci_loc.leading_comments is not None:
            lines.extend(self._break_text(sci_loc.leading_comments))
        # Trailing comments also go in the header - to make sure it gets into the docstring
        if sci_loc.trailing_comments is not None:
            lines.extend(self._break_text(sci_loc.trailing_comments))

        lines = [
            # Escape triple-quotes that would otherwise end the docstring early.
            line.replace("\\", "\\\\").replace('"""', r"\"\"\"")
            for line in lines
        ]
        if len(lines) == 1:
            line = lines[0]
            if line.endswith(('"', "\\")):
                # Docstrings are terminated with triple-quotes, so if the documentation itself ends in a quote,
                # insert some whitespace to separate it from the closing quotes.
                # This is not necessary with multiline comments
                # because in that case we always insert a newline before the trailing triple-quotes.
                line = line + " "
            self._write_line(f'"""{line}"""')
        else:
            for i, line in enumerate(lines):
                if i == 0:
                    self._write_line(f'"""{line}')
                else:
                    self._write_line(f"{line}")
            self._write_line('"""')

        return True

    def write_enum_values(
            self,
            values: Iterable[Tuple[int, d.EnumValueDescriptorProto]],
            scl_prefix: SourceCodeLocation,
    ) -> None:
        for i, val in values:
            if val.name in PYTHON_RESERVED:
                continue

            scl = scl_prefix + [i]
            self._write_line(
                f"{val.name} = {val.number}",
            )
            if self._write_comments(scl):
                self._write_line("")  # Extra newline to separate

    def write_module_attributes(self) -> None:
        l = self._write_line
        self.imports.add('proto')
        l(f"__protobuf__ = proto.module(")
        with self._indent():
            l(f'package="{self.package}",')
            l("manifest={")
            with self._indent():
                for message in self.fd.message_type:
                    l(f'"{message.name}",')
                for enum in self.fd.enum_type:
                    l(f'"{enum.name}",')
            l("}")
        l(")\n\n")

    def write_enums(
            self,
            enums: Iterable[d.EnumDescriptorProto],
            scl_prefix: SourceCodeLocation,
    ) -> None:
        l = self._write_line
        for i, enum in enumerate(enums):
            class_name = (
                enum.name if enum.name not in PYTHON_RESERVED else "_r_" + enum.name
            )
            enum_helper_class = self._import('proto', 'Enum')

            l(f"class {class_name}({enum_helper_class}):")
            with self._indent():
                scl = scl_prefix + [i]
                self._write_comments(scl)
                self.write_enum_values(
                    enumerate(enum.value),
                    scl + [d.EnumDescriptorProto.VALUE_FIELD_NUMBER],
                )
            l("")
            l("")

    def write_messages(
            self,
            messages: Iterable[d.DescriptorProto],
            scl_prefix: SourceCodeLocation,
    ) -> None:
        l = self._write_line

        for i, desc in enumerate(messages):
            # Reproduce some hardcoded logic from the protobuf implementation - where
            # some specific "well_known_types" generated protos to have additional
            # base classes
            addl_base = ""
            if self.fd.package + "." + desc.name in WKTBASES:
                # chop off the .proto - and import the well known type
                # eg `from google.protobuf.duration import Duration`
                well_known_type = WKTBASES[self.fd.package + "." + desc.name]
                addl_base = ", " + self._import(
                    "google.protobuf.internal.well_known_types",
                    well_known_type.__name__,
                )

            class_name = (
                desc.name if desc.name not in PYTHON_RESERVED else "_r_" + desc.name
            )
            message_class = self._import("proto.message", "Message")
            l(f"class {class_name}({message_class}{addl_base}):")
            with self._indent():
                scl = scl_prefix + [i]
                self._write_comments(scl)

                # Nested enums/messages
                with self.working_class(desc):
                    self.write_enums(
                        desc.enum_type,
                        scl + [d.DescriptorProto.ENUM_TYPE_FIELD_NUMBER],
                    )
                    self.write_messages(
                        desc.nested_type,
                        scl + [d.DescriptorProto.NESTED_TYPE_FIELD_NUMBER],
                    )

                for idx, field in enumerate(desc.field):
                    if field.name in PYTHON_RESERVED:
                        continue
                    if field.number is None:
                        warnings.warn(f"Field {field} has no number set in .proto file. "
                                      f"It's the {idx + 1} field for {class_name}")

                    field_class, field_type = self.protoplus_type(field)
                    args = {
                        'number': field.number,
                    }
                    if field.HasField('oneof_index'):
                        args['oneof'] = f"'{desc.oneof_decl[field.oneof_index].name}'"
                    else:
                        args['optional']: field.label == field.LABEL_OPTIONAL

                    # write field specification
                    l(f"{field.name} = {field_class}(")
                    if self._current_working_class:
                        field_type = removeprefix(field_type, f"{self._current_working_class.name}.")

                    field_type = removeprefix(field_type, f"{class_name}.")
                    with self._indent():
                        l(f'{field_type},')
                        for k, v in args.items():
                            l(f"{k}={v},")
                    l(")")

            l("\n\n")

    def protoplus_type(
            self, field: d.FieldDescriptorProto
    ) -> Tuple[Any, str]:
        """
        Generate imports and return correct type
        """

        mapping: Dict[d.FieldDescriptorProto.Type.V, Callable[[], str]] = {
            d.FieldDescriptorProto.TYPE_DOUBLE: lambda: self._import('proto', 'DOUBLE'),
            d.FieldDescriptorProto.TYPE_FLOAT: lambda: self._import('proto', 'FLOAT'),
            d.FieldDescriptorProto.TYPE_INT64: lambda: self._import('proto', 'INT64'),
            d.FieldDescriptorProto.TYPE_UINT64: lambda: self._import('proto', 'UINT64'),
            d.FieldDescriptorProto.TYPE_FIXED64: lambda: self._import('proto', 'FIXED64'),
            d.FieldDescriptorProto.TYPE_SFIXED64: lambda: self._import('proto', 'SFIXED64'),
            d.FieldDescriptorProto.TYPE_SINT64: lambda: self._import('proto', 'SINT64'),
            d.FieldDescriptorProto.TYPE_INT32: lambda: self._import('proto', 'INT32'),
            d.FieldDescriptorProto.TYPE_UINT32: lambda: self._import('proto', 'UINT32'),
            d.FieldDescriptorProto.TYPE_FIXED32: lambda: self._import('proto', 'FIXED32'),
            d.FieldDescriptorProto.TYPE_SFIXED32: lambda: self._import('proto', 'SFIXED32'),
            d.FieldDescriptorProto.TYPE_SINT32: lambda: self._import('proto', 'SINT32'),
            d.FieldDescriptorProto.TYPE_BOOL: lambda: self._import('proto', 'BOOL'),
            d.FieldDescriptorProto.TYPE_STRING: lambda: self._import('proto', 'STRING'),
            d.FieldDescriptorProto.TYPE_BYTES: lambda: self._import('proto', 'BYTES'),
            d.FieldDescriptorProto.TYPE_ENUM: lambda: self._import_message(field.type_name),
            d.FieldDescriptorProto.TYPE_MESSAGE: lambda: self._import_message(field.type_name),
            d.FieldDescriptorProto.TYPE_GROUP: lambda: self._import_message(field.type_name),
        }

        assert field.type in mapping, "Unrecognized type: " + repr(field.type)
        field_type = mapping[field.type]()

        # For non-repeated fields, use normal Field!
        if field.label != d.FieldDescriptorProto.LABEL_REPEATED:
            field_class = self._import('proto', 'Field')
        else:
            # else use MapField or RepeatedField
            msg = self.descriptors.messages.get(field.type_name)
            field_class = (
                self._import('proto', 'MapField')
                if msg is not None and msg.options.map_entry else
                self._import('proto', 'RepeatedField')
            )

        return field_class, field_type

    def write(self) -> str:
        for reexport_idx in self.fd.public_dependency:
            reexport_file = self.fd.dependency[reexport_idx]
            reexport_fd = self.descriptors.files[reexport_file]
            reexport_imp = (
                    reexport_file[:-6].replace("-", "_").replace("/", ".") + "_pb_plus"
            )
            names = (
                    [m.name for m in reexport_fd.message_type]
                    + [m.name for m in reexport_fd.enum_type]
                    + [v.name for m in reexport_fd.enum_type for v in m.value]
                    + [m.name for m in reexport_fd.extension]
            )
            if reexport_fd.options.py_generic_services:
                names.extend(m.name for m in reexport_fd.service)

            if names:
                # n,n to force a reexport (from x import y as y)
                self.from_imports[reexport_imp].update((n, n) for n in names)

        return super().write()


def is_scalar(fd: d.FieldDescriptorProto) -> bool:
    return not (
            fd.type == d.FieldDescriptorProto.TYPE_MESSAGE
            or fd.type == d.FieldDescriptorProto.TYPE_GROUP
    )


def generate_proto_plus(
        descriptors: Descriptors,
        response: plugin_pb2.CodeGeneratorResponse,
        package: str,
        readable_imports: bool,
        quiet: bool,
) -> None:
    for name, fd in descriptors.to_generate.items():
        pkg_writer = PkgWriter(
            fd,
            descriptors,
            readable_imports=readable_imports,
            package=package
        )

        pkg_writer.write_module_attributes()
        pkg_writer.write_enums(
            fd.enum_type, [d.FileDescriptorProto.ENUM_TYPE_FIELD_NUMBER]
        )
        pkg_writer.write_messages(
            fd.message_type, [d.FileDescriptorProto.MESSAGE_TYPE_FIELD_NUMBER]
        )

        if fd.options.py_generic_services:
            sys.stderr.write("GRPC compilation not implemented.")
            sys.exit(1)

        assert name == fd.name
        assert fd.name.endswith(".proto")
        output = response.file.add()
        output.name = fd.name[:-6].replace("-", "_").replace(".", "/") + "_pb_plus.py"
        output.content = HEADER + pkg_writer.write()
        if not quiet:
            print("Writing protoplus to", output.name, file=sys.stderr)

    # generate init files for packages
    by_package = {k: list(v) for k, v in groupby(descriptors.to_generate.values(), key=lambda d: d.package)}

    for pkg, modules in by_package.items():
        output = response.file.add()
        output.name = pkg.replace('-', '_').replace('.', '/') + "/__init__.py"

        init_writer = InitWriter(descriptors, {pkg: modules}, readable_imports)
        init_writer.write_module_attributes()
        output.content = HEADER + init_writer.write()

    root_dir = op.commonprefix([g.name for g in descriptors.to_generate.values()])
    if not root_dir:
        return

    root_init = root_dir.replace('-', '_').replace('.', '/') + '/__init__.py'

    if not any(o.name == root_init for o in response.file):
        output = response.file.add()
        output.name = root_init
        root_writer = InitWriter(descriptors,
                                 by_package,
                                 readable_imports)
        root_writer.write_module_attributes()
        output.content = HEADER + root_writer.write()


class InitWriter(Writer):

    def __init__(self,
                 descriptors: Descriptors,
                 modules: Dict[str, List[d.FileDescriptorProto]],
                 readable_imports: bool = False,
                 ) -> None:
        self.modules = modules
        super().__init__(d.FileDescriptorProto(), descriptors, readable_imports)

    def write_module_attributes(self) -> None:
        l = self._write_line

        l("__all__ = (")
        with self._indent():
            for pkg, modules in self.modules.items():
                for message in chain(chain.from_iterable(m.enum_type for m in modules),
                                     chain.from_iterable(m.message_type for m in modules)):
                    name = (
                        message.name if message.name not in PYTHON_RESERVED else "_r_" + message.name
                    )
                    message = self._import_message(f".{pkg}.{name}")
                    l(f'"{message}",')
        l(")")


@contextmanager
def code_generation() -> Iterator[
    Tuple[plugin_pb2.CodeGeneratorRequest, plugin_pb2.CodeGeneratorResponse],
]:
    if len(sys.argv) > 1 and sys.argv[1] in ("-V", "--version"):
        print("codestare-proto-plus " + __version__)
        sys.exit(0)

    # Read request message from stdin
    data = sys.stdin.buffer.read()

    # Parse request
    request = plugin_pb2.CodeGeneratorRequest()

    # allow input as json for debug
    try:
        request.ParseFromString(data)
    except DecodeError as e1:
        from google.protobuf.json_format import Parse, ParseError
        try:
            Parse(data, request)
        except ParseError as e2:
            raise e2 from e1

    # Create response
    response = plugin_pb2.CodeGeneratorResponse()

    # Declare support for optional proto3 fields
    response.supported_features |= (
        plugin_pb2.CodeGeneratorResponse.FEATURE_PROTO3_OPTIONAL
    )

    yield request, response

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.buffer.write(output)


def main() -> None:
    # Generate protoplus
    with code_generation() as (request, response):
        redirect = re.findall(r'save_request=(.+?,|.+$)', request.parameter)
        package = re.findall(r'package=(.+?,|.+$)', request.parameter)

        if len(redirect) > 1:
            sys.stderr.write(f"Can't provide out= multiple times")
            sys.exit(1)

        if len(package) > 1:
            sys.stderr.write(f"Can't provide package= multiple times")
            sys.exit(1)

        if redirect:
            redirect = Path(redirect[0].strip(','))
            import google.protobuf.json_format
            with redirect.open('wb') as out:
                out.write(request.SerializeToString(deterministic=True))
            with (redirect.parent / f"{redirect.stem}.json").open('w') as json:
                json.write(google.protobuf.json_format.MessageToJson(request))

        generate_proto_plus(
            Descriptors(request),
            response,
            readable_imports="readable_imports" in request.parameter,
            quiet="quiet" in request.parameter,
            package=package[0].strip(',') if package else None
        )


if __name__ == "__main__":
    main()
