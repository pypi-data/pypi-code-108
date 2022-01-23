from dataclasses import dataclass
from enum import Enum, auto
from pathlib import PurePosixPath, PurePath
from typing import Dict, Tuple, Callable, List

from aim_build.typedefs import StringList
from aim_build.utils import prepend_paths, to_native_path, to_pure_posix_path, relpaths


class BuildTypes(Enum):
    staticLibrary = auto()
    dynamicLibrary = auto()
    executable = auto()
    headerOnly = auto()
    libraryReference = auto()


@dataclass
class LibraryInformation:
    name: str
    path: str
    type: str


def get_project_dir(build: Dict, target_file: Dict):
    root_dir = target_file["projectRoot"]
    project_dir = build["build_dir"] / root_dir
    return project_dir


def find_build(build_name: str, builds: Dict) -> Dict:
    # Note, this should never fail, as required dependencies are checked by the schema.
    for build in builds:
        if build["name"] == build_name:
            return build

    raise RuntimeError(f"Failed to find build with name: {build_name}")


def find_builds_of_type(build_type: str, builds: Dict) -> List[Dict]:
    return [build for build in builds if build["buildRule"] == build_type]


def get_include_paths(include_paths: List[PurePath], build_dir: PurePath) -> List[PurePath]:
    include_paths = [to_native_path(path) for path in include_paths]
    abs_paths = [PurePosixPath(str(p).replace("\\", "/")) for p in include_paths if p.is_absolute()]
    rel_paths = [PurePosixPath(str(p).replace("\\", "/")) for p in include_paths if not p.is_absolute()]
    rel_paths = prepend_paths(build_dir, rel_paths)

    includes = abs_paths + rel_paths
    return includes


def get_toolchain_and_flags(build: Dict,
                            target_file: Dict) \
        -> Tuple[str, str, StringList, StringList, str, StringList]:
    local_compiler = build.get("compiler", None)
    local_archiver = build.get("archiver", None)
    local_flags = build.get("flags", None)
    local_defines = build.get("defines", None)
    local_linker = build.get("linker", None)
    local_linker_flags = build.get("linker_flags", None)

    compiler = local_compiler if local_compiler else target_file["compiler"]
    archiver = local_archiver if local_archiver else target_file["archiver"]
    cxx_flags = local_flags if local_flags else target_file.get("flags", [])
    defines = local_defines if local_defines else target_file.get("defines", [])
    global_linker = target_file.get("linker", compiler)

    linker = local_compiler if local_linker else global_linker
    linker_flags = local_linker_flags if local_linker_flags else cxx_flags

    return compiler, archiver, cxx_flags, defines, linker, linker_flags


def get_src_files(build: Dict, target_file: Dict) -> StringList:
    project_dir = get_project_dir(build, target_file)
    paths = build["sourceFiles"]
    paths = [to_native_path(path) for path in paths]

    # Resolve relative paths to the build directory, and leave absolute paths alone.
    #
    abs_paths = [path for path in paths if path.is_absolute() is True]
    rel_paths = [path for path in paths if path.is_absolute() is False]

    src_paths = []
    for path in abs_paths:
        if path.stem == "*":
            globbed_files = list(path.parent.glob(path.name))
            src_paths += globbed_files
        else:
            src_paths.append(path)

    build_path = build["build_dir"]
    for path in rel_paths:
        path = project_dir / path
        if path.stem == "*":
            globbed_files = list(path.parent.glob(path.name))

            rel_paths = relpaths(globbed_files, build_path)
            src_paths += rel_paths
        else:
            rel_path = relpaths(path, build_path)
            src_paths += rel_path

    src_paths = [to_pure_posix_path(path) for path in src_paths]
    return [str(file) for file in src_paths]


def get_required_library_information(build: Dict,
                                     parsed_toml: Dict) -> List[LibraryInformation]:
    requires = build.get("requires", [])
    if not requires:
        return []

    build_names = []  # Used to prevent duplicates.
    result = []

    library_types = [BuildTypes.staticLibrary, BuildTypes.dynamicLibrary]

    for required in requires:
        the_dep = find_build(required, parsed_toml["builds"])
        build_type = BuildTypes[the_dep["buildRule"]]
        if build_type not in library_types:
            continue

        build_name = the_dep["name"]
        if build_name not in build_names:
            build_names.append(build_name)

            # If we are going to dynamically load the library, then we don't want to generate linker flags for it.
            dynamic_loading = the_dep.get("dynamicLoading", False)
            if dynamic_loading:
                continue

            lib_info = LibraryInformation(
                the_dep["outputName"],
                the_dep["name"],
                the_dep["buildRule"]
            )
            result.append(lib_info)

    return result


def get_reference_library_information(
        build: Dict, parsed_toml: Dict
) -> Tuple[List[str], List[str]]:
    requires = build.get("requires", [])
    if not requires:
        return [], []

    build_names = []  # Used to prevent duplicates.
    libraries = []
    library_paths = []
    for required in requires:
        the_dep = find_build(required, parsed_toml["builds"])
        build_type = BuildTypes[the_dep["buildRule"]]
        if build_type != BuildTypes.libraryReference:
            continue

        build_name = the_dep["name"]
        if build_name not in build_names:
            build_names.append(build_name)
            libraries += the_dep.get("libraries", [])
            library_paths += the_dep.get("libraryPaths", [])

    return libraries, library_paths


def get_full_library_name_convention(
        lib_infos: List[LibraryInformation],
        static_convention_func: Callable[[str], str],
        dynamic_convention_func: Callable[[str], str],
) -> StringList:
    # Here we just need to manage the fact that the linker's library flag (-l) needs the library name without
    # lib{name}.a/.so but the build dependency rule does need the full convention to find the build rule in the
    # build.ninja file.
    full_library_names = []
    for info in lib_infos:
        build_type = BuildTypes[info.type]
        if build_type == BuildTypes.staticLibrary:
            full_library_names.append(static_convention_func(info.name))
        elif build_type == BuildTypes.dynamicLibrary:
            full_library_names.append(dynamic_convention_func(info.name))

    return full_library_names
