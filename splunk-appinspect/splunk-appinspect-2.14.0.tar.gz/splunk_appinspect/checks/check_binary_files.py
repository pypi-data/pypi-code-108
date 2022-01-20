# Copyright 2021 Splunk Inc. All rights reserved.

"""
### Binary file standards
"""

import logging
import os
import os.path
import platform
from collections import ChainMap
from lib2to3.main import main as exec_two_to_three

import splunk_appinspect
from splunk_appinspect.python_analyzer import utilities
from splunk_appinspect.python_analyzer.ast_analyzer import AstAnalyzer
from splunk_appinspect.python_analyzer.trustedlibs.utilities import get_hash_file

if not platform.system() == "Windows":
    import magic

logger = logging.getLogger(__name__)


def _check_binary_status(file_path):
    binary_status = {
        "python": False,
        "text": False,
        "binary": False,
        "x86_64": False,
        "arm": False,
        "error": None,
    }
    try:
        mimetype = magic.from_file(file_path, mime=True)
    except Exception as ex:
        output = f"Please investigate this file manually. File: {file_path} error={ex}"
        binary_status["error"] = output
    else:
        if "text" in mimetype:
            binary_status["text"] = True
            if os.path.splitext(file_path)[-1] == ".py":
                binary_status["python"] = True

        if "python" in mimetype:
            binary_status["python"] = True

        if (
            mimetype == "application/x-executable"
            or mimetype == "application/x-sharedlib"
        ):
            binary_status["binary"] = True

            human_readable_output = magic.from_file(file_path)
            if "x86-64" in human_readable_output.lower():
                binary_status["x86_64"] = True
            if "arm" in human_readable_output.lower():
                binary_status["arm"] = True

    return binary_status


def _traverse_all_imported_python_files(file_full_path):
    all_imported_python_file = set()
    invalid_files = ChainMap()

    def __traverse_all_imported_python_files(file_full_path):
        if file_full_path in all_imported_python_file:
            return
        all_imported_python_file.add(file_full_path)

        try:
            imported_files = utilities.find_imports(file_full_path)
        except (SyntaxError, TabError) as ex:
            try:
                exec_two_to_three(
                    fixer_pkg="lib2to3.fixes",
                    args=["-w", file_full_path, "--no-diffs", "-j", "2"],
                )
            except Exception:
                invalid_files[file_full_path] = str(ex)
            return

        for imports in imported_files:
            try:
                file_path = imports[3]
            except IndexError:
                continue
            if file_path not in all_imported_python_file:
                __traverse_all_imported_python_files(file_path)

    __traverse_all_imported_python_files(file_full_path)

    return all_imported_python_file, invalid_files


@splunk_appinspect.tags(
    "splunk_appinspect", "cloud", "self-service", "future",
)
def check_idx_binary_compatibility(app, reporter):
    """Checks that binaries that are distributed to the IDX tier of a distributed Splunk platform deployment are
    compatible with aarch64."""
    if platform.system() == "Windows":
        reporter_output = "Please run AppInspect using another OS to enable this check. Or use AppInspect API."
        reporter.warn(reporter_output)
        return

    whitelist_hash_files = (
        # Splunklib external_search_command.py
        "047eff10d2f10452b850579e886bbb919a53a77d3c34537c99193b24a8abab73",
        "0a2c2e0a72bb85b1ca9916147bf69a706355f2f7bea2ff3ff5cea796b982c2e8",
        "22f651c1bc32e8f9a75290fdb815200972d17ebd12ed0b3bb9638628b10bf849",
        "24da27069eac27d5979dc8b564116060a7beafadd55519a26e0cd747ddd0edbf",
        "268297fa7375241623e3775ba33326752acacafb3abd976eb160bd688699c671",
        "48fa70a0ddd89af6a78dbd47f798500cbc224e8712292bccf77e8f023cbe58a2",
        "623fd10c4f61fc3b9112d31284e8ab5741007baa427abaf7e7bf4093fd0eb8eb",
        "6f79090c85c810a294bc642d5072d320d11dbc2c40eed6957869c0f183427839",
        "992d81bb729f43252ab07235c7bb13713295cee4da17c1afae3336cc8c285ed4",
        "9a5fbfe2a301671fccd0e62209ebc076945904b1bf8a1ee94d1b261256e7d9ad",
        "a8c3e417dc80eb96b132d8a571b81726a6b06c7b9bad62d13b97ae483eb85853",
        "b0e75e31669ba763a6545775940d2b54aea138340fc659a9c179cd48e4fa2320",
        "b48636726d2234720be6f16c000ae8b04bd3c2021f121256adf03a788f5664fd",
        "bdc90bae58b1c93f953f5001ccebec73c528ac3cb68e2c4861cd483d4b89667b",
        "edef82986765acf5e3491f537b6388385ccd6bdf30140e220275a0b8b7554fe4",
    )

    executable_files = []
    if app.file_exists("default", "commands.conf"):
        executable_files.extend(app.get_custom_executable_files(local=False))

    if app.file_exists("default", "transforms.conf"):
        executable_files.extend(app.get_transforms_executable_files())

    if app.file_exists("default", "distsearch.conf"):
        executable_files = list(
            set(executable_files) - set(app.get_non_distributed_files())
        )

    # List all imports python file. Warn if it's not a python file and not an arm binary
    all_imported_python_file = set()
    invalid_files = ChainMap()
    for executable_file in set(executable_files):
        file_full_path = app.get_filename(executable_file)
        binary_status = _check_binary_status(file_full_path)
        if binary_status["error"]:
            reporter.warn(binary_status["error"], executable_file)
        elif binary_status["python"]:
            (
                traversed_imported_files,
                traversed_invalid_files,
            ) = _traverse_all_imported_python_files(file_full_path)
            all_imported_python_file = (
                all_imported_python_file | traversed_imported_files
            )
            invalid_files.update(traversed_invalid_files)
        elif binary_status["binary"] and not binary_status["arm"]:
            # Change from warning to fail 3 months after deploying
            reporter.warn(
                f"The following file is incompatible with the ARM aarch64 architecture. "
                f"Compatibility with this architecture is required for code that will be executed "
                f"on the Indexer tier of the Splunk Cloud Platform.",
                file_name=executable_file,
            )
    for file, error in invalid_files.items():
        all_imported_python_file.remove(file)
        reporter.warn(
            f"AppInspect is unable to validate whether the following files are compatible with execution "
            f"on the ARM aarch64 platform because they do not appear to be compatible with Python 3. "
            f"This may cause issues when your app is run on the Splunk Cloud Platform. Error: {error}",
            file_name=file,
        )

    def check_report_binary_file_in_code(ast_node, file_name):
        inspect_file_name = None
        if (
            hasattr(ast_node, "elts")
            and ast_node.elts
            and hasattr(ast_node.elts[0], "s")
            and ast_node.elts[0].s
        ):
            # ex) ast_node.elts = ["test.py", "option1", "option2"] => "test.py"
            inspect_file_name = os.path.join("bin", ast_node.elts[0].s)
        elif hasattr(ast_node, "s") and ast_node.s:
            # ex) ast_node.s = "test.py option1 option2" => "test.py"
            inspect_file_name = os.path.join("bin", ast_node.s.strip().split(" ")[0])
        else:
            reporter.warn(
                "Code has been found that may have executed the binary file.",
                file_name=file_name,
                line_number=ast_node.lineno,
            )
            return

        if app.file_exists(inspect_file_name):
            binary_status = _check_binary_status(app.get_filename(inspect_file_name))
            if binary_status["error"]:
                reporter.warn(binary_status["error"], inspect_file_name)
            elif binary_status["binary"] and not binary_status["arm"]:
                # Change from warning to fail 3 months after deploying
                reporter.warn(
                    f"The following file is incompatible with the ARM aarch64 architecture. "
                    f"Compatibility with this architecture is required for code that will be executed "
                    f"on the Indexer tier of the Splunk Cloud Platform.",
                    file_name=file_name,
                    line_number=ast_node.lineno,
                )
        else:
            reporter.warn(
                "May have run a binary file, but the file was not found.",
                file_name=file_name,
                line_number=ast_node.lineno,
            )

    # Determine if the script imports .so files or running by subprocess.
    # Warn if the binary file is not an arm binary
    for python_path in all_imported_python_file:
        try:
            analyzer = AstAnalyzer(python_file_path=python_path)
        except Exception as ex:
            reporter.warn(
                f"AppInspect is unable to validate whether the following files are compatible with execution "
                f"on the ARM aarch64 platform because they do not appear to be compatible with Python 3. "
                f"This may cause issues when your app is run on the Splunk Cloud Platform. Error: {ex}",
                file_name=python_path,
            )
            continue

        if analyzer.content_hash in whitelist_hash_files:
            continue

        if analyzer.get_module_usage("ctypes"):
            for name, ctypes_usages in analyzer.function_call_usage.items():
                if name == "CDLL" or name == "LoadLibrary":
                    for ctypes_usage in ctypes_usages:
                        if hasattr(ctypes_usage, "args") and ctypes_usage.args:
                            check_report_binary_file_in_code(
                                ctypes_usage.args[0], python_path
                            )

        if analyzer.get_module_usage("subprocess"):
            subprocess_usages = set(
                analyzer.get_module_function_call_usage("subprocess", fuzzy=True)
            )
            for subprocess_usage in subprocess_usages:
                if hasattr(subprocess_usage, "args") and subprocess_usage.args:
                    check_report_binary_file_in_code(
                        subprocess_usage.args[0], python_path
                    )
