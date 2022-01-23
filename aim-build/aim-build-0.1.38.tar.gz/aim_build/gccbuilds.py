import functools
from pathlib import PurePosixPath, Path
from typing import Dict, Tuple, Callable, List

from ninja_syntax import Writer

from aim_build import commonbuilds
from aim_build.commonbuilds import BuildTypes
from aim_build.typedefs import StringList, PurePathList
from aim_build.utils import (
    prefix,
    src_to_o,
    to_path_root,
    prepend_paths,
    to_str,
    escape_path,
    wrap_quotes
)

PrefixIncludePath = functools.partial(prefix, "-I")
PrefixSystemIncludePath = functools.partial(prefix, "-isystem")
PrefixQuoteIncludePath = functools.partial(prefix, "-iquote")
PrefixLibraryPath = functools.partial(prefix, "-L")
PrefixLibrary = functools.partial(prefix, "-l")
PrefixHashDefine = functools.partial(prefix, "-D")
ToObjectFiles = src_to_o


def add_compile(nfw: Writer):
    command = "$compiler $defines $flags -MMD -MF deps.d $includes -c $in -o $out"
    nfw.rule(
        name="compile",
        description="Compiles source files into object files",
        deps="gcc",
        depfile="deps.d",
        command=command,
    )
    nfw.newline()


def add_ar(nfw: Writer):
    nfw.rule(
        name="archive",
        description="Combine object files into an archive",
        command="$archiver crs $out $in",
    )
    nfw.newline()


def add_exe(nfw: Writer):
    # TODO: origin should only really be added when we need to link against an so.
    command = "$compiler $defines $flags $includes $in -o $out $linker_args"
    nfw.rule(name="exe", description="Builds an executable.", command=command)
    nfw.newline()


def add_shared(nfw: Writer):
    command = "$compiler $defines -shared $visibility -fPIC $flags $includes $in -o $out $linker_args"
    nfw.rule(name="shared", description="Builds a shared library.", command=command)
    nfw.newline()


# TODO: Should take version strings as well?
def linux_add_static_library_naming_convention(library_name: str) -> str:
    return f"lib{library_name}.a"


def linux_add_dynamic_library_naming_convention(library_name: str) -> str:
    return f"lib{library_name}.so"


# def linux_add_exe_naming_convention(exe_name: str) -> str:
#     return f"{exe_name}.exe"


def get_quote_include_paths(build: Dict, build_dir: PurePosixPath) -> PurePathList:
    rel_path = to_path_root(build_dir)

    include_paths = build.get("localIncludePaths", [])
    includes = [rel_path / PurePosixPath(path) for path in include_paths]

    return includes


def get_system_include_paths(build: Dict) -> PurePathList:
    paths = build.get("systemIncludePaths", [])
    paths = [PurePosixPath(path) for path in paths]
    return paths


def convert_strings_to_paths(paths):
    return [PurePosixPath(path) for path in paths]


def get_includes_for_build(build: Dict, parsed_toml: Dict) -> StringList:
    requires = [build["name"]] + build.get("requires", [])

    include_paths = set()
    system_include_paths = set()
    quote_include_paths = set()

    project_root = PurePosixPath(parsed_toml["projectRoot"])

    for required in requires:
        the_dep = commonbuilds.find_build(required, parsed_toml["builds"])

        includes = the_dep.get("includePaths", [])
        includes = convert_strings_to_paths(includes)
        includes = commonbuilds.get_include_paths(includes, project_root)
        include_paths.update(includes)

        quote_includes = get_quote_include_paths(the_dep, build["build_dir"])
        quote_include_paths.update(quote_includes)

        system_includes = get_system_include_paths(the_dep)
        system_include_paths.update(system_includes)

    include_paths = wrap_quotes(list(include_paths))
    system_include_paths = wrap_quotes(list(system_include_paths))
    quote_include_paths = wrap_quotes(list(quote_include_paths))

    include_paths.sort()
    system_include_paths.sort()
    quote_include_paths.sort()

    include_args = PrefixIncludePath(include_paths)
    system_include_args = PrefixSystemIncludePath(system_include_paths)
    quote_args = PrefixQuoteIncludePath(quote_include_paths)

    return include_args + system_include_args + quote_args


def get_external_libraries_paths(build: Dict) -> StringList:
    directory = build["directory"]
    library_paths = build.get("libraryPaths", [])
    result = []
    for path in library_paths:
        path = PurePosixPath(path)
        if not path.is_absolute():
            path = directory / path

        result.append(str(path))
    result = wrap_quotes(result)
    return result

    # library_paths = wrap_quotes(library_paths)
    # library_paths = prepend_paths(directory, library_paths)
    # return library_paths


def get_external_libraries_names(build: Dict) -> Tuple[StringList, StringList]:
    libraries = build.get("libraries", [])
    link_libraries = PrefixLibrary(libraries)
    return libraries, link_libraries


def get_external_libraries_information(build: Dict) -> Tuple[StringList, StringList]:
    libraries, _ = get_external_libraries_names(build)
    library_paths = get_external_libraries_paths(build)
    return libraries, library_paths


def get_src_for_build(build: Dict, parsed_toml: Dict) -> List[PurePosixPath]:
    files = commonbuilds.get_src_files(build, parsed_toml)
    return convert_strings_to_paths(files)


def add_compile_rule(
        writer: Writer,
        build: Dict,
        target_file: Dict,
        includes: StringList,
        extra_flags: StringList = None,
):
    build_name = build["name"]

    compiler, _, cxx_flags, defines, __, ___ = commonbuilds.get_toolchain_and_flags(
        build, target_file
    )
    defines = PrefixHashDefine(defines)

    if extra_flags:
        cxx_flags = extra_flags + cxx_flags

    src_files = get_src_for_build(build, target_file)
    obj_files = ToObjectFiles(src_files)
    obj_files = prepend_paths(Path(build_name), obj_files)

    file_pairs = zip(to_str(src_files), to_str(obj_files))
    for src_file, obj_file in file_pairs:
        writer.build(
            outputs=obj_file,
            rule="compile",
            inputs=src_file,
            variables={
                "compiler": compiler,
                "includes": includes,
                "flags": cxx_flags,
                "defines": defines,
            },
        )
        writer.newline()

    return obj_files


def get_rpath(build: Dict, parsed_toml: Dict) -> str:
    # Good blog post about rpath:
    # https://medium.com/@nehckl0/creating-relocatable-linux-executables-by-setting-rpath-with-origin-45de573a2e98
    requires = build.get("requires", [])
    library_names = set()

    # find_build_types("dynamicLib", parsed_toml["builds"])
    # TODO: replace the below with the above.
    for required in requires:
        the_dep = commonbuilds.find_build(required, parsed_toml["builds"])
        build_type = BuildTypes[the_dep["buildRule"]]
        if build_type == BuildTypes.dynamicLibrary:
            library_names.update([the_dep["name"]])

    # Note, thinking aloud here as not 100% sure this is the correct thing to do.
    # The current thought process is that the origin allows something like an executable to find the libraries it needs.
    # Therefore, the path to these dependencies is simply just up one directory, which takes us to the build directory,
    # and then down into the build dependency folder.

    library_names = list(library_names)
    library_names.sort()
    relative_paths = [PurePosixPath("..") / lib_path for lib_path in library_names]

    relative_paths = [f"$$ORIGIN/{rel_path}" for rel_path in relative_paths]
    relative_paths = ["$$ORIGIN"] + relative_paths

    relative_paths_string = escape_path(":".join(relative_paths))
    return f"-Wl,-rpath='{relative_paths_string}'"


def generate_linker_args(build, parsed_toml):
    lib_infos = commonbuilds.get_required_library_information(build, parsed_toml)

    rpath = get_rpath(build, parsed_toml)

    # Requires Libraries:
    #
    requires_libraries = PrefixLibrary([info.name for info in lib_infos])
    requires_library_paths = [info.path for info in lib_infos]
    requires_library_paths = wrap_quotes(requires_library_paths)
    requires_library_paths = PrefixLibraryPath(requires_library_paths)

    # External Libraries:
    #
    (
        external_libraries_names,
        external_libraries_paths,
    ) = get_external_libraries_information(build)

    external_libraries_names = PrefixLibrary(external_libraries_names)
    external_libraries_paths = wrap_quotes(external_libraries_paths)
    external_libraries_paths = PrefixLibraryPath(external_libraries_paths)

    # Reference Libraries:
    #
    (
        ref_libraries,
        ref_library_paths,
    ) = commonbuilds.get_reference_library_information(build, parsed_toml)

    ref_libraries = PrefixLibrary(ref_libraries)
    ref_library_paths = wrap_quotes(ref_library_paths)
    ref_library_paths = PrefixLibraryPath(ref_library_paths)

    linker_args = (
            [rpath]
            + requires_library_paths
            + external_libraries_paths
            + ref_library_paths
            + requires_libraries
            + external_libraries_names
            + ref_libraries
    )
    return linker_args


def run_build(build: Dict, parsed_toml: Dict, ninja_writer: Writer, args):
    # TODO forward args
    the_build = BuildTypes[build["buildRule"]]
    build_name = build["name"]
    build_dir = build["build_dir"]

    build_path = build_dir / build_name
    build_path.mkdir(parents=True, exist_ok=True)

    build["buildPath"] = build_path

    if the_build == BuildTypes.staticLibrary:
        build_static_library(
            ninja_writer,
            build,
            parsed_toml,
            linux_add_static_library_naming_convention,
        )
    elif the_build == BuildTypes.executable:
        build_executable(ninja_writer, build, parsed_toml)
    elif the_build == BuildTypes.dynamicLibrary:
        build_dynamic_library(ninja_writer, build, parsed_toml)
    elif the_build == BuildTypes.headerOnly:
        pass
    elif the_build == BuildTypes.libraryReference:
        pass
    else:
        raise RuntimeError(f"Unknown build type {the_build}.")


def build_static_library(pfw: Writer, build: Dict, parsed_toml: Dict, lib_name_func: Callable[[str], str]):
    build_name = build["name"]

    includes = get_includes_for_build(build, parsed_toml)
    obj_files = add_compile_rule(pfw, build, parsed_toml, includes)

    library_name = lib_name_func(build["outputName"])
    relative_output_name = str(PurePosixPath(build_name) / library_name)

    _, archiver, cxx_flags, defines, __, ___ = commonbuilds.get_toolchain_and_flags(
        build, parsed_toml
    )
    defines = PrefixHashDefine(defines)

    pfw.build(
        outputs=relative_output_name,
        rule="archive",
        inputs=to_str(obj_files),
        variables={
            "archiver": archiver,
            "includes": includes,
            "flags": cxx_flags,
            "defines": defines,
        },
    )

    pfw.newline()
    pfw.build(rule="phony", inputs=relative_output_name, outputs=library_name)
    pfw.build(rule="phony", inputs=library_name, outputs=build_name)
    pfw.newline()


def build_executable(pfw: Writer, build: Dict, parsed_toml: Dict):
    build_name = build["name"]

    _, __, ___, defines, linker, linker_flags = commonbuilds.get_toolchain_and_flags(
        build, parsed_toml
    )
    defines = PrefixHashDefine(defines)

    includes = get_includes_for_build(build, parsed_toml)
    obj_files = add_compile_rule(pfw, build, parsed_toml, includes)

    lib_infos = commonbuilds.get_required_library_information(build, parsed_toml)
    linker_args = generate_linker_args(build, parsed_toml)

    full_library_names = commonbuilds.get_full_library_name_convention(
        lib_infos,
        linux_add_static_library_naming_convention,
        linux_add_dynamic_library_naming_convention,
    )

    exe_name = build["outputName"]
    relative_output_name = str(Path(build_name) / exe_name)
    pfw.build(
        rule="exe",
        outputs=relative_output_name,
        inputs=to_str(obj_files),
        implicit=full_library_names,
        variables={
            "compiler": linker,
            "includes": includes,
            "flags": linker_flags,
            "defines": defines,
            "linker_args": " ".join(linker_args),
        },
    )
    pfw.newline()
    pfw.build(rule="phony", inputs=relative_output_name, outputs=exe_name)
    pfw.build(rule="phony", inputs=exe_name, outputs=build_name)
    pfw.newline()


def build_dynamic_library(pfw: Writer, build: Dict, parsed_toml: Dict):
    build_name = build["name"]

    vis = build.get("visibility", None)
    if vis is None:
        vis = "hidden"
    vis_flags = f"-fvisibility={vis}"

    extra_flags = ["-DEXPORT_DLL_PUBLIC", "-fPIC", vis_flags]

    compiler, _, cxxflags, defines, __, ___ = commonbuilds.get_toolchain_and_flags(
        build, parsed_toml
    )
    defines = PrefixHashDefine(defines)

    includes = get_includes_for_build(build, parsed_toml)
    obj_files = add_compile_rule(pfw, build, parsed_toml, includes, extra_flags)

    lib_infos = commonbuilds.get_required_library_information(build, parsed_toml)
    linker_args = generate_linker_args(build, parsed_toml)

    full_library_names = commonbuilds.get_full_library_name_convention(
        lib_infos,
        linux_add_static_library_naming_convention,
        linux_add_dynamic_library_naming_convention,
    )

    library_name = linux_add_dynamic_library_naming_convention(build["outputName"])
    relative_output_name = str(PurePosixPath(build_name) / library_name)

    pfw.build(
        rule="shared",
        inputs=to_str(obj_files),
        implicit=full_library_names,
        outputs=relative_output_name,
        variables={
            "compiler": compiler,
            "includes": includes,
            "flags": " ".join(cxxflags),
            "defines": " ".join(defines),
            "lib_name": library_name,
            "linker_args": " ".join(linker_args),
        },
    )
    pfw.newline()
    pfw.build(rule="phony", inputs=relative_output_name, outputs=library_name)
    pfw.build(rule="phony", inputs=library_name, outputs=build_name)
    pfw.newline()


def log_build_information(build):
    build_name = build["name"]
    cxx_flags = build["global_flags"] + build.get("flags", [])
    defines = build["global_defines"] + build.get("defines", [])
    includes = build["includes"]
    library_paths = build["libraryPaths"]
    output = build["outputName"]

    print(f"Running build: f{build_name}")
    print(f"FLAGS: {cxx_flags}")
    print(f"DEFINES: {defines}")
    print(f"INCLUDE_PATHS: {includes}")
    print(f"LIBRARY_PATHS: {library_paths}")
    print(f"OUTPUT NAME: {output}")
    print("")
