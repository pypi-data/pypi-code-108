import pprint
import sys
from pathlib import Path
from typing import Union, List

import cerberus

from aim_build.commonbuilds import BuildTypes
from aim_build.utils import to_native_path


class UniqueNameChecker:
    def __init__(self):
        self.name_lookup = []

    def check(self, field, value, error):
        if value in self.name_lookup:
            error(
                field,
                f'The build name must be unique. "{value}" has already been used.',
            )
        else:
            self.name_lookup.append(value)


# TODO: Can DefinesPrefixChecker be a function?
class DefinesPrefixChecker:
    def check(self, field, defines: List[str], error):
        for value in defines:
            if value.startswith("-D"):
                error(
                    field,
                    f"Unnecessary -D prefix in {field}: {defines}. Aim will add this automatically.",
                )


class RequiresExistChecker:
    def __init__(self, document):
        self.doc = document

    def check(self, field, requires, error):
        builds = self.doc["builds"]
        for value in requires:
            for build in builds:
                if value == build["name"]:
                    break
            else:
                error(field, f"Build name does not exist: {value}")


class DirectoryPathChecker:
    def __init__(self, project_dir):
        self.project_dir = project_dir

    def check(self, field, paths, error):
        abs_paths = [Path(path) for path in paths if Path(path).is_absolute() is True]
        rel_paths = [Path(path) for path in paths if Path(path).is_absolute() is False]
        rel_paths = [(self.project_dir / path) for path in rel_paths]

        all_paths = abs_paths + rel_paths

        for path in all_paths:
            if not path.is_dir():
                error(field, f'Path is not a directory: "{str(path)}"')
                break

            if not path.exists():
                error(field, f'Path does not exist: "{str(path)}"')
                break


class SrcPathsChecker:
    def __init__(self, project_dir):
        self.project_dir = project_dir

    def check(self, field, paths, error):
        paths = [to_native_path(path) for path in paths]

        # Resolve relative paths to the build directory, and leave absolute paths alone.
        #
        abs_paths = [path for path in paths if path.is_absolute() is True]
        rel_paths = [(self.project_dir / path) for path in paths if path.is_absolute() is False]
        all_paths = abs_paths + rel_paths

        for path in all_paths:
            # Historically, paths to directories were allowed, but I've decided that it is better to specify directories
            # using a glob with a file extension, as this means we can support any file type without having to
            # explicitly manage the file types that we support.

            # Remember paths can now be specific paths to files, or globs of the form <path>/*.<extension>.
            # We don't allow recursive globs. <path>/**/*.<extension>
            if path.stem == "**":
                error(field, f'Recursive globs are not supported: "{str(path)}"')
                return

            elif path.stem == "*":
                parent = path.parent
                if not parent.exists():
                    error(field, f'The parent glob directory does not exist: "{str(parent)}"')
                    break

                if len(list(parent.glob(path.name))) == 0:
                    error(field, f'The glob does not match any files: "{str(path)}"')
                    break

            elif path.is_dir():
                error(field, f'Src path is a directory. Src paths should be a glob or a specific file.: "{str(path)}"')
                break

            elif not path.exists():
                error(field, f'Path does not exist: "{str(path)}"')
                break


class AimCustomValidator(cerberus.Validator):
    def __init__(self, *args, **kwargs):
        super(AimCustomValidator, self).__init__(*args, **kwargs)
        self.name_lookup = []

    def check_output_is_unique(self, field, value):
        if value in self.name_lookup:
            self._error(
                field,
                f'The output name must be unique. "{value}" has already been used.',
            )
        else:
            self.name_lookup.append(value)

    def _check_with_output_naming_convention(self, field, value: Union[str, list]):
        # Only check the convention when building libraries. Exes need more flexibility when building for Arduino etc.

        library_types = [BuildTypes.staticLibrary.name, BuildTypes.dynamicLibrary.name]
        if self.document["buildRule"] not in library_types:
            return

        def check_convention(_field, _value):
            the_errors = []
            if _value.startswith("lib"):
                the_error_str = f"Unnecessary 'lib' prefix in {_value}. Aim will add this automatically."
                the_errors.append(the_error_str)

            suffix = Path(_value).suffix
            if suffix:
                the_error_str = (
                    f'Unecessary suffix "{suffix}". Aim will add this automatically.'
                )
                the_errors.append(the_error_str)

            return the_errors

        # Bit of a hack so strings go through the same code path as lists.
        if isinstance(value, str):
            value = [value]

        for item in value:
            # self.check_output_is_unique(field, item)
            errors = check_convention(field, item)

            if errors:
                plural = ""
                if len(errors) > 1:
                    plural = "s"

                error_str = f"Naming convention error{plural}: {item}. " + " ".join(
                    errors
                )
                self._error(field, error_str)


def target_schema(document, project_dir):
    unique_name_checker = UniqueNameChecker()
    requires_exist_checker = RequiresExistChecker(document)
    source_path_checker = SrcPathsChecker(project_dir)
    directory_path_checker = DirectoryPathChecker(project_dir)
    defines_checker = DefinesPrefixChecker()

    schema = {
        "compiler": {"required": True, "type": "string"},
        "archiver": {"required": True, "type": "string"},
        "compilerFrontend": {
            "required": True,
            "type": "string",
            "allowed": ["msvc", "gcc", "osx"],
        },
        "flags": {
            "type": "list",
            "schema": {"type": "string"},
            "empty": False
        },
        "defines": {
            "type": "list",
            "schema": {"type": "string"},
            "empty": False,
            "check_with": defines_checker.check,
        },
        "projectRoot": {
            "required": True,
            "type": "string",
            "empty": False
        },
        "builds": {
            "required": True,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {
                        "required": True,
                        "type": "string",
                        "check_with": unique_name_checker.check,
                    },
                    "buildRule": {
                        "required": True,
                        "type": "string",

                        # Validates if exactly one of the provided constraints applies.
                        "oneof": [
                            {
                                # No output, so exclude output name.
                                # Not a dynamic library so exclude visibility and dynamicLoading
                                "excludes": ["outputName", "visibility", "dynamicLoading"],
                                "allowed": ["headerOnly", "libraryReference"],
                            },
                            {
                                # Generates an output so make outputName required.
                                # Not a dynamic library so exclude visibility and dynamicLoading.
                                "excludes": ["visibility", "dynamicLoading"],
                                "dependencies": ["outputName"],
                                "allowed": ["executable", "staticLibrary"],
                            },
                            {
                                # Generates an output so make outputName required.
                                # Allows visibility if frontend is gcc or osx.
                                "dependencies": ["outputName"],
                                "allowed": ["dynamicLibrary"],
                            },
                        ],
                    },
                    "visibility": {
                        "required": False,
                        "type": "string",
                        "allowed": [
                            "hidden",
                            "default"
                        ],
                        "dependencies": {"^compilerFrontend": ["gcc", "osx"]},
                    },
                    "dynamicLoading": {
                        "required": False,
                        "type": "boolean",
                    },
                    "compiler": {
                        "required": False,
                        "type": "string",
                        "dependencies": {
                            "buildRule": ["executable", "staticLibrary", "dynamicLibrary"]
                        },
                    },
                    "linker": {
                        "required": False,
                        "type": "string",
                        "dependencies": {
                            "buildRule": ["executable"]
                        },
                    },
                    "linker_flags": {
                        "required": False,
                        "type": "list",
                        "dependencies": {
                            "buildRule": ["executable"]
                        },
                    },
                    "defines": {
                        "type": "list",
                        "schema": {"type": "string"},
                        "empty": False,
                        "check_with": defines_checker.check,
                        "dependencies": {
                            "buildRule": ["executable", "staticLibrary", "dynamicLibrary"]
                        },
                    },
                    "flags": {
                        "type": "list",
                        "schema": {"type": "string"},
                        "empty": False,
                        "dependencies": {
                            "buildRule": ["executable", "staticLibrary", "dynamicLibrary"]
                        },
                    },
                    "requires": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": requires_exist_checker.check,
                        "dependencies": {
                            "buildRule": ["executable", "staticLibrary", "dynamicLibrary"]
                        },
                    },
                    # Required but the requirement is handled by build rule.
                    "outputName": {
                        "type": "string",
                        "empty": False,
                        "check_with": "output_naming_convention",
                    },
                    "sourceFiles": {
                        "required": False,
                        "empty": False,
                        "type": "list",
                        "schema": {"type": "string"},
                        "check_with": source_path_checker.check,
                        "dependencies": {
                            "buildRule": ["executable", "staticLibrary", "dynamicLibrary"]
                        },
                    },
                    "includePaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": directory_path_checker.check,
                    },
                    "systemIncludePaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": directory_path_checker.check,
                        "dependencies": {"compilerFrontend": "gcc"},
                    },
                    "localIncludePaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": directory_path_checker.check,
                        "dependencies": {"compilerFrontend": "gcc"},
                    },
                    "libraryPaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        # you can't check the library dirs as they may not exist if the project not built before.
                        # "check_with": path_checker.check,
                        "dependencies": {
                            "buildRule": ["executable", "dynamicLibrary", "libraryReference"]
                        },
                    },
                    "libraries": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": "output_naming_convention",
                        "dependencies": {
                            "buildRule": ["executable", "dynamicLibrary", "libraryReference"]
                        },
                    },
                },
            },
        },
    }

    validator = AimCustomValidator()
    validator.validate(document, schema)

    pretty = pprint.PrettyPrinter(indent=2, width=100)

    # TODO: Handle schema errors. https://docs.python-cerberus.org/en/stable/errors.html
    if validator.errors:
        for key, value in validator.errors.items():
            if key != "builds":
                print(f'Error for field "{key}"')
                pretty.pprint(f"{value}")
                print()

        builds_errors = validator.errors.get("builds", {})
        if builds_errors:
            assert len(builds_errors) == 1, "Build error list size is greater than 1."
            for key, value in builds_errors[0].items():
                builds = document["builds"]
                the_build = builds[key]
                the_build_name = the_build["name"]

                print(f'Error in build: "{the_build_name}"')
                assert (
                        len(value) == 1
                ), "Length is not 1. Not sure if it can ever be more than."
                pretty.pprint(value[0])
                print()
        sys.exit(-1)
