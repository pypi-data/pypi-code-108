"""
Functions for serializing Python functions.

The only known areas where we will fail to serialize something usable are:

user imports like import foo.bar.baz instead of from foo.bar import baz
are not detected properly by the underlying library we use for looking up
dependencies. import json or other top-level modeuls still works just fine,
its just when you include multiple path components that we don't detect the
dependency properly

references to instantiated non-builtin types with a repr that can't be exec'd

users referring to a renamed version of an imported module has some wonky
behavior, for example `import json` then `foo=json` then referring to
`foo` in the func to be serialized.
"""
import inspect
from collections import defaultdict
from types import FunctionType
from types import ModuleType

from dill.detect import freevars
from dill.detect import globalvars

from tecton_proto.args.user_defined_function_pb2 import UserDefinedFunction
from tecton_spark.errors import TectonValidationError
from tecton_spark.logger import get_logger
from tecton_spark.repo_file_handler import ensure_prepare_repo
from tecton_spark.repo_file_handler import repo_files_set
from tecton_spark.time_utils import WINDOW_UNBOUNDED_PRECEDING

logger = get_logger("function_serialization")


def to_proto(transform):
    code = transform._code if hasattr(transform, "_code") else _getsource(transform)
    _validate_code(code)

    proto = UserDefinedFunction()
    proto.name = transform.__name__
    proto.body = code

    return proto


BANNED_INDIRECT_IMPORTS = ["materialization_context", "tecton_sliding_window_udf", "WINDOW_UNBOUNDED_PRECEDING"]


def _validate_code(code):
    for banned_import in BANNED_INDIRECT_IMPORTS:
        if f"tecton.{banned_import}" in code:
            raise Exception(
                f"Cannot serialize `tecton.{banned_import}`. Please use an import like `from tecton import {banned_import}`. Note that even comments may trigger this if your code contains `tecton.{banned_import}`"
            )


# If these are in the path to a module, we don't expect the function definitions to be inside a feature repo, but we still want to inline them
# integration_tests/ is added as a hack because our integration tests aren't run in a feature repo. But unless a customer is importing from a python package that has a directory named integration_tests, it
# shouldn't cause any wrong behavior.
TECTON_TRANSFORMATION_WHITELIST = ["builtin_transformations.py", "integration_tests/"]

# returns true if the module is defined by tecton, rather than by the user
def is_tecton_defined(module):
    return sum([whitelist_str in module for whitelist_str in TECTON_TRANSFORMATION_WHITELIST]) > 0


# UNDONE:
# this breaks for the following case:
# def f():
#    a = module.CONSTANT
#
# for some reason, the module/constant don't show up in globalvars.
# this case has not occurred in practice
def _getsource(func):
    imports = defaultdict(set)
    modules = set()
    code_lines = []
    seen_args = {}

    # file the func was defined in
    func_file = inspect.getfile(inspect.getmodule(func))

    # Check if the file is part of the tecton codebase, not the feature repo.
    # Only perform any feature repo initialization for functions in the feature repo.
    # We short-circuit any repo_file_handler functions that depend on initialization if we skip initialization here.
    if not is_tecton_defined(func_file):
        ensure_prepare_repo(func_file)

    def process_functiontype(name, obj, imports, modules, code_lines, seen_args):
        # if this is user-defined or otherwise unavailable to import at deserialization time
        # including anything without a module, with module of __main__, defined inside the feature repo
        # or anything with a qualified name containing characters invalid for an import path, like foo.<locals>.bar
        module = inspect.getfile(inspect.getmodule(obj))
        if (
            obj.__module__ in ("__main__", None)
            or "<" in obj.__qualname__
            or is_tecton_defined(module)
            or module in repo_files_set()
        ):
            objs = globalvars(obj, recurse=False)
            objs.update(freevars(obj))
            default_objs = {}
            for param in inspect.signature(obj).parameters.values():
                if param.default != inspect.Parameter.empty:
                    default_objs[param.name] = param.default
                    # these defaults shadow over obj
                    objs.pop(param.name, None)
            # need to sort the keys since globalvars ordering is non-deterministic
            for dependency, dep_obj in sorted(objs.items()):
                recurse(dependency, dep_obj, imports, modules, code_lines, seen_args, write_codelines=True)
            for dependency, dep_obj in sorted(default_objs.items()):
                # we dont re-write defaults at top-level since the `def` lines should have the declarations
                recurse(dependency, dep_obj, imports, modules, code_lines, seen_args, write_codelines=False)
            fdef = inspect.getsource(obj)
            fdef = fdef[fdef.find("def ") :]
            code_lines.append(fdef)
        else:
            imports[obj.__module__].add(obj.__name__)

    def recurse(name, obj, imports, modules, code_lines, seen_args, write_codelines):
        def _add_codeline(line):
            if write_codelines:
                code_lines.append(line)

        # prevent processing same dependency object multiple times, even if
        # multiple dependent objects exist in the tree from the original
        # func
        seen_key = str(name) + str(obj)
        if seen_args.get(seen_key) is True:
            return
        seen_args[seen_key] = True

        has_spark = True
        try:
            import pyspark
        except ImportError:
            has_spark = False

        is_spark_struct = False
        is_unbound_materialization_context = False
        is_tecton_sliding_window_udf = False
        if has_spark:
            from pyspark.sql import types as spark_types

            is_spark_struct = isinstance(obj, spark_types.StructType)
            from tecton_spark.materialization_context import UnboundMaterializationContext

            is_unbound_materialization_context = isinstance(obj, UnboundMaterializationContext)

            from tecton_spark.udfs import tecton_sliding_window_udf

            is_tecton_sliding_window_udf = obj is tecton_sliding_window_udf

        # Confusingly classes are subtypes of 'type'; non-classes are not
        if isinstance(obj, type):
            if obj.__module__ == "__main__":
                raise Exception(f"Cannot serialize class {obj.__name__} from module __main__")
            imports[obj.__module__].add(obj.__name__)

        elif isinstance(obj, FunctionType):
            process_functiontype(name, obj, imports, modules, code_lines, seen_args)
        elif isinstance(obj, ModuleType):
            module_file = inspect.getfile(obj)
            # skip this check for functions written by Tecton
            if not is_tecton_defined(func_file) and module_file in repo_files_set():
                raise Exception(
                    f"Cannot serialize usage of {obj.__name__}. Instead, directly import objects from the module, e.g. `from {obj.__name__} import obj`"
                )
            if f"{obj.__package__}.{name}" == obj.__name__:
                imports[obj.__package__].add(name)
            else:
                modules.add(obj.__name__)
        elif is_spark_struct:
            _add_codeline(f"{name} = StructType.fromJson(json.loads('{obj.json()}'))")
            modules.add("json")
            imports["pyspark.sql.types"].add("StructType")
        elif is_unbound_materialization_context:
            imports["tecton_spark.materialization_context"].add("materialization_context")
        elif is_tecton_sliding_window_udf:
            imports["tecton_spark.udfs"].add("tecton_sliding_window_udf")
        elif obj == WINDOW_UNBOUNDED_PRECEDING:
            imports["tecton_spark.time_utils"].add("WINDOW_UNBOUNDED_PRECEDING")
        else:
            try:
                repr_str = f"{name}={repr(obj)}"
                exec(repr_str)
                _add_codeline(repr_str)
            except Exception:
                raise Exception(f"Cannot evaluate object {obj} of type '{type(obj)}' for serialization")

    recurse(func.__name__, func, imports, modules, code_lines, seen_args, write_codelines=True)

    for module in sorted(imports):
        import_line = f"from {module} import "
        import_line += ", ".join(sorted(imports[module]))
        code_lines.insert(0, import_line)

    for module in sorted(modules):
        code_lines.insert(0, f"import {module}")

    return "\n".join(code_lines)


def inlined(func):
    # this a no-op that can be deleted later
    return func


def from_proto(serialized_transform: UserDefinedFunction, scope=None):
    """
    deserialize into global scope by default. if a scope if provided, deserialize into provided scope
    """

    if scope is None:
        # PySpark has issues if the UDFs are not in global scope
        scope = __import__("__main__").__dict__

    assert serialized_transform.HasField("body") and serialized_transform.HasField(
        "name"
    ), "Invalid UserDefinedFunction."

    try:
        exec(serialized_transform.body, scope)
    except NameError as e:
        raise TectonValidationError(
            "Failed to serialize function. Please note that all imports must be in the body of the function (not top-level) and type annotations cannot require imports. Additionally, be cautious of variables that shadow other variables. See https://docs.tecton.ai/v2/overviews/framework/transformations.html for more details.",
            e,
        )

    # Return function pointer
    try:
        fn = eval(serialized_transform.name, scope)
        fn._code = serialized_transform.body
        return fn
    except Exception as e:
        raise ValueError("Invalid transform") from e
