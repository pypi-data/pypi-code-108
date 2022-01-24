from setuptools import setup

name = "types-protobuf"
description = "Typing stubs for protobuf"
long_description = '''
## Typing stubs for protobuf

This is a PEP 561 type stub package for the `protobuf` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `protobuf`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/protobuf. All fixes for
types and metadata should be contributed there.

Generated with aid from mypy-protobuf v3.2.0

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `35064a7f759facd7c3787ab6095964008f97d873`.
'''.lstrip()

setup(name=name,
      version="3.19.6",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=['types-futures'],
      packages=['google-stubs'],
      package_data={'google-stubs': ['__init__.pyi', 'protobuf/__init__.pyi', 'protobuf/any_pb2.pyi', 'protobuf/api_pb2.pyi', 'protobuf/compiler/__init__.pyi', 'protobuf/compiler/plugin_pb2.pyi', 'protobuf/descriptor.pyi', 'protobuf/descriptor_pb2.pyi', 'protobuf/descriptor_pool.pyi', 'protobuf/duration_pb2.pyi', 'protobuf/empty_pb2.pyi', 'protobuf/field_mask_pb2.pyi', 'protobuf/internal/__init__.pyi', 'protobuf/internal/api_implementation.pyi', 'protobuf/internal/containers.pyi', 'protobuf/internal/decoder.pyi', 'protobuf/internal/encoder.pyi', 'protobuf/internal/enum_type_wrapper.pyi', 'protobuf/internal/extension_dict.pyi', 'protobuf/internal/message_listener.pyi', 'protobuf/internal/python_message.pyi', 'protobuf/internal/well_known_types.pyi', 'protobuf/internal/wire_format.pyi', 'protobuf/json_format.pyi', 'protobuf/message.pyi', 'protobuf/message_factory.pyi', 'protobuf/reflection.pyi', 'protobuf/service.pyi', 'protobuf/source_context_pb2.pyi', 'protobuf/struct_pb2.pyi', 'protobuf/symbol_database.pyi', 'protobuf/text_format.pyi', 'protobuf/timestamp_pb2.pyi', 'protobuf/type_pb2.pyi', 'protobuf/util/__init__.pyi', 'protobuf/wrappers_pb2.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
