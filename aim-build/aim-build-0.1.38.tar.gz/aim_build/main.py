import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from ninja_syntax import Writer
from tabulate import tabulate

from aim_build import gccbuilds
from aim_build import msvcbuilds
from aim_build.common import DEMO_ZIP_FILE_NAME
from aim_build.commonbuilds import find_build, BuildTypes
from aim_build.schema import target_schema
from aim_build.version import __version__


def run_ninja(working_dir, build_name):
    command = ["ninja", "-C", str(working_dir), "-v", build_name]
    # command_str = " ".join(command)
    # print(f'Executing "{command_str}"')

    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        for line in iter(process.stdout.readline, b""):
            sys.stdout.write(line.decode("utf-8"))
        for line in iter(process.stderr.readline, b""):
            sys.stderr.write(line.decode("utf-8"))

        ret_code = process.returncode

    return ret_code


def entry():
    script_path = Path(__file__).parent

    # TODO: Get version automatically from the pyproject.toml file.
    parser = argparse.ArgumentParser(prog="aim", description=f"Version {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.add_parser(name="version", help="Displays the version number")

    def make_init_command(_subparsers):
        init_parser = _subparsers.add_parser(name="init",
                                             help="Creates a project structure with optional demo files")

        init_parser.add_argument("--demo-files",
                                 help="Creates additional demo files",
                                 action="store_true")


    def make_clobber_command(_subparsers):
        clobber_parser = _subparsers.add_parser(name="clobber",
                                                help="Deletes all build artifacts")

        clobber_parser.add_argument("path",
                                 help="The directorty containing target.py")

    def make_list_command(_subparsers):
        list_parser = _subparsers.add_parser(name="list",
                                             help="Lists the builds in target.py")

        list_parser.add_argument("path",
                                 help="The directorty containing target.py")


    def make_build_command(_subparsers):
        build_parser = _subparsers.add_parser(name="build",
                                              help="Executes a build specified in target.py")

        build_parser.add_argument("path",
                                  help="The directorty containing target.py")

        build_parser.add_argument("build",
                                  type=str,
                                  help="The name of the build to execute")

        build_parser.add_argument(
            "-s",
            "--skip-ninja",
            help="Skip regenerating build.ninja file on build",
            action="store_true",
        )

    def make_run_command(_subparsers):
        run_parser = _subparsers.add_parser(name="run",
                                            help="Launches executable")

        run_parser.add_argument("path",
                                help="The directorty containing target.py")

        run_parser.add_argument("build",
                                type=str,
                                help="The name of the build to execute")

        run_parser.add_argument("args",
                                nargs=argparse.REMAINDER,
                                help="arguments forwarded to the executable")

    def make_exec_command(_subparsers):
        exec_parser = _subparsers.add_parser(name="exec",
                                            help="Executes several commands in one")

        exec_parser.add_argument("path",
                                help="The directorty containing target.py")

        exec_parser.add_argument("build",
                                type=str,
                                help="The name of the build to execute")

        exec_parser.add_argument(
            "-s",
            "--skip-ninja",
            help="Skip regenerating build.ninja file on build",
            action="store_true",
        )

        exec_parser.add_argument("operations",
                                 nargs="*",
                                 choices=["clobber", "list", "build", "run"],
                                 help="The commands to execute.")

        exec_parser.add_argument("args",
                                nargs=argparse.REMAINDER,
                                help="arguments forwarded to the executable")

    make_init_command(subparsers)
    make_clobber_command(subparsers)
    make_list_command(subparsers)
    make_build_command(subparsers)
    make_run_command(subparsers)
    make_exec_command(subparsers)

    args = parser.parse_args()
    command = args.command

    if command == "init":
        if args.demo_files:
            print("Initialising from demo project...")
            relative_dir = "demo/Calculator"
        else:
            relative_dir = "demo/Empty"

        zip_path = script_path / f"{DEMO_ZIP_FILE_NAME}"

        assert zip_path.exists(), f"Failed to find demo zip files: {str(zip_path)}"
        with zipfile.ZipFile(str(zip_path)) as zip_file:
            run_init(zip_file, relative_dir)

    elif command == "clobber":
        run_clobber(args.path)

    elif command == "list":
        run_list(args.path)

    elif command == "build":
        forwarding_args = []
        ret_code = run_build(args.build, args.path, args.skip_ninja, forwarding_args)
        sys.exit(ret_code)

    elif command == "run":
        forward = args.args if args.args else []
        ret_code = run_run(args.path, args, forward)
        sys.exit(ret_code)

    elif command == "exec":
        for command in args.operations:
            if "list" == command:
                run_list(args.path)

            elif "clobber" == command:
                run_clobber(args.path)

            elif "build" == command:
                # TODO: forwardarding build args.
                forwarding_args = []
                ret_code = run_build(args.build, args.path, args.skip_ninja, forwarding_args)
                if ret_code:
                    sys.exit(ret_code)

            elif "run" == command:
                forward = args.args if args.args else []
                ret_code = run_run(args.path, args, forward)
                if ret_code:
                    sys.exit(ret_code)
    else:
        parser.print_help(sys.stdout)


def run_run(path, args, unknown):
    target_file = load_target_file(path)

    the_build = find_build(args.build, target_file["builds"])

    build_type = the_build["buildRule"]
    if build_type != "executable":
        print(f"Error: {args.build} is not executable")
        exit(-1)
    name = the_build["outputName"]

    build_dir = make_build_path(path)
    if target_file["compilerFrontend"] == "msvc":
        command = build_dir / name
    else:
        command = build_dir / args.build / name
    # forward_args = args.args if args.args else []
    forward_args = unknown
    str_repr = " ".join(forward_args)
    print(f"Running: {command} {str_repr}")
    return_code = subprocess.run([command] + forward_args)
    return return_code.returncode


def run_init(demo_zip: zipfile.ZipFile, subdir_name):
    project_dir = Path().cwd()
    dirs = ["include", "src", "lib", "tests", "builds"]
    dirs = [project_dir / x for x in dirs]
    print("Creating directories...")
    for a_dir in dirs:
        print(f"\t{str(a_dir)}")
        a_dir.mkdir(exist_ok=True)

    assert demo_zip, "Zip file error"
    print("Initialising from demo project...")

    files = [filename for filename in demo_zip.namelist() if filename.startswith(subdir_name)]
    assert len(files) > 0, f"Failed to find files for sub dir {subdir_name}"

    for file_name in files:
        with demo_zip.open(file_name) as the_file:
            file_path = Path(file_name)
            relative_path = file_path.relative_to(subdir_name)
            sys.stdout.write(f"\tCreating {str(relative_path)} ...")
            if relative_path.exists():
                print("warning, file already exists.")
                continue
            print("okay")

            relative_path.parent.mkdir(parents=True, exist_ok=True)
            relative_path.touch()
            relative_path.write_bytes(the_file.read())


def generate_flat_ninja_file(target_dict, project_dir, build_dir, args):
    frontend = target_dict["compilerFrontend"]
    project_ninja = build_dir / "build.ninja"

    builds = target_dict["builds"]

    with project_ninja.open("w+") as project_fd:
        project_writer = Writer(project_fd)
        # project_writer.include(str(build_dir / "rules.ninja"))
        if frontend == "msvc":
            msvcbuilds.add_compile(project_writer)
            msvcbuilds.add_ar(project_writer)
            msvcbuilds.add_exe(project_writer)
            msvcbuilds.add_shared(project_writer)
        elif frontend == "osx":
            # builder = osxbuilds.OsxBuilds()
            assert False, "OSX frontend is currently not supported."
        else:
            gccbuilds.add_compile(project_writer)
            gccbuilds.add_ar(project_writer)
            gccbuilds.add_exe(project_writer)
            gccbuilds.add_shared(project_writer)

        for build_info in builds:
            current_build = build_info
            current_build["directory"] = project_dir
            current_build["build_dir"] = build_dir

            if frontend == "msvc":
                builder = msvcbuilds.run_build
            elif frontend == "osx":
                # builder = osxbuilds.OsxBuilds()
                assert False, "OSX frontend is currently not supported."
            elif frontend == "gcc":
                builder = gccbuilds.run_build
            else:
                assert False, f"Error: Unknown frontend {frontend}"

            builder(build_info, target_dict, project_writer, args)


def make_build_path(target_path: Path):
    target_path = Path(target_path)
    if target_path.is_absolute():
        build_dir = target_path
    else:
        build_dir = Path().cwd() / target_path

    return build_dir


def make_project_path(root_dir: Path, build_dir: Path):
    project_dir = build_dir / root_dir
    assert project_dir.exists(), f"{str(project_dir)} does not exist."
    return project_dir


def vdir(obj):
    import inspect

    results = []

    # dir only gets the name of the attribute ...
    for x in dir(obj):
        # Remove _ and __ vars, as these aren't apart of our schema and will cause the validator to fail.
        if x.startswith("_"):
            continue

        # ... so when we want to check for modules, we need to explicitly access them using getattr.
        #
        # Remove modules, because we don't want to force users to do the following:
        # import os as _os.
        # Because that would be annoying.
        at = getattr(obj, x)
        if inspect.ismodule(at):
            continue

        results.append(x)
    return results


def load_target_py_file(file_path: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("target", str(file_path))
    target_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target_module)
    return target_module


def convert_target_module_to_dict(target_module):
    keys = vdir(target_module)
    the_dict = {k: getattr(target_module, k) for k in keys}
    return the_dict


def run_build(build_name, target_path, skip_ninja_regen, args):
    print("Running build...")

    build_dir = make_build_path(target_path)
    file_path = build_dir / "target.py"

    completed_path = (Path().cwd() / file_path).resolve()
    assert file_path.exists(), f"Error: Could not find target.py at {str(completed_path)}"

    target_module = load_target_py_file(file_path)
    target_dict = convert_target_module_to_dict(target_module)

    builds = target_dict["builds"]
    the_build = find_build(build_name, builds)

    project_dir = make_project_path(target_dict["projectRoot"], build_dir)

    try:
        target_schema(target_dict, project_dir)
    except RuntimeError as exception:
        print(f"Error: {exception.args[0]}")
        sys.exit(-1)

    if not skip_ninja_regen:
        print("Generating ninja files...")
        generate_flat_ninja_file(target_dict, project_dir, build_dir, args)
        COMPILE_COMMANDS = True
        if COMPILE_COMMANDS:
            with (build_dir.resolve() / "compile_commands.json").open("w+") as cc_json:
                command = ["ninja", "-C", str(build_dir.resolve()), "-t", "compdb"]
                subprocess.run(command, stdout=cc_json, check=True)

    return run_ninja(build_dir, the_build["name"])


def add_naming_convention(
        output_name: str,
        build_type: BuildTypes,
        static_convention_func,
        dynamic_convention_func,
):
    if build_type == BuildTypes.staticLibrary:
        new_name = static_convention_func(output_name)
    elif build_type == BuildTypes.dynamicLibrary:
        new_name = dynamic_convention_func(output_name)
    else:
        assert False, f"Error Invalid build type: {build_type}"

    return new_name


def load_target_file(target_path):
    build_dir = make_build_path(target_path)

    target_file = build_dir / "target.py"
    assert target_file.exists(), f"Error: {str(target_file)} does not exists."

    target_module = load_target_py_file(target_file)
    target_dict = convert_target_module_to_dict(target_module)
    return target_dict

    # builds = target_dict["builds"]
    # return builds


def run_list(target_path):
    target_dict = load_target_file(target_path)
    builds = target_dict["builds"]

    frontend = target_dict["compilerFrontend"]

    if frontend == "msvc":
        static_convention_func = (
            msvcbuilds.windows_add_static_library_naming_convention
        )
        dynamic_convection_func = (
            msvcbuilds.windows_add_dynamic_library_naming_convention
        )
    elif frontend == "osx":
        assert False, "OSX frontend is currently not supported."
    elif frontend == "gcc":
        static_convention_func = (
            gccbuilds.linux_add_static_library_naming_convention
        )
        dynamic_convection_func = (
            gccbuilds.linux_add_dynamic_library_naming_convention
        )
    else:
        assert False, f"Error: Unknown compiler frontend: {frontend}"

    header = ["Item", "Name", "Build Rule", "Output Name"]
    table = []

    for number, build in enumerate(builds):
        build_type = BuildTypes[build["buildRule"]]
        if build_type in [BuildTypes.libraryReference, BuildTypes.headerOnly]:
            output_name = "n.a."
        elif build_type in [BuildTypes.staticLibrary, BuildTypes.dynamicLibrary]:
            output_name = add_naming_convention(
                build["outputName"],
                build_type,
                static_convention_func,
                dynamic_convection_func,
            )
        else:
            output_name = build["outputName"]

        row = [number, build["name"], build["buildRule"], output_name]
        table.append(row)

    print()
    print(tabulate(table, header))
    print()


def run_clobber(target_path):
    build_dir = Path().cwd()

    if target_path:
        target_path = Path(target_path)
        if target_path.is_absolute():
            build_dir = target_path
        else:
            build_dir = build_dir / Path(target_path)

    assert (build_dir / "target.py").exists(), (
        f"Failed to find target.py file in {str(build_dir)}.\n"
        "You might be trying to delete a directory that you want to keep."
    )

    print(f"Clobbering {str(build_dir)}...")

    dir_contents = build_dir.glob("*")
    for item in dir_contents:
        if item.name not in ["target.toml", "target.py"]:
            print(f"Deleting {item.name}")
            if item.is_dir():
                shutil.rmtree(str(item))
            else:
                os.remove(str(item))


if __name__ == "__main__":
    entry()
