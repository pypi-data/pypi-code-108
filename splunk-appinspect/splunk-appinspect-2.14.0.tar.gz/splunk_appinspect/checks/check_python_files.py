# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Python file standards
"""
import ast
import logging
import os
import platform
import re

import splunk_appinspect
from splunk_appinspect.check_routine.python_ast_searcher.ast_searcher import AstSearcher
from splunk_appinspect.check_routine.python_ast_searcher.node_filters import (
    is_sub_class_def,
)
from splunk_appinspect.python_analyzer import utilities
from splunk_appinspect.python_analyzer.ast_info_query import Any
from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common import metadata_consts
from splunk_appinspect.python_modules_metadata.python_modules_metadata_store import (
    metadata_store,
)

logger = logging.getLogger(__name__)

report_display_order = 40


@splunk_appinspect.tags("cloud", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_hidden_python_files(app, reporter):
    """Check that there are no hidden python files included in the app."""
    if platform.system() == "Windows":
        for directory, file, _ in app.iterate_files(excluded_types=[".py"]):
            current_file_relative_path = os.path.join(directory, file)
            reporter_output = (
                "Please manual check this "
                "file to check if it is a hidden python file. "
                f"File: {current_file_relative_path}"
            )
            reporter.manual_check(
                reporter_output,
                file_name=current_file_relative_path,
            )
    else:
        client = app.python_analyzer_client
        for filepath in client.get_hidden_python_files():
            import chardet

            byte_string = open(os.path.join(app.app_temp_dir, filepath), "rb").read()
            encoding = chardet.detect(byte_string)["encoding"]
            content = open(
                os.path.join(app.app_temp_dir, filepath), "r", encoding=encoding
            ).read()
            content = re.sub("[\r\n]+", " ", content)

            # this check only focus on python template code
            network_patterns = "(urllib|socket|httplib|requests|smtplib|ftplib|nntplib|poplib|imaplib|telnetlib|gopherlib|xmlrpclib|SimpleHTTPServer|SimpleXMLRPCServer)"
            system_modules = "(subprocess|shutil|os|sys|distutils|threading|multiprocessing|commands)"
            from_import_modules = fr"from\s+import\s+{system_modules}"
            import_modules = fr"import\s+{system_modules}"
            file_manipulation = r"\.(read|write|open)"
            possible_injection = r"(subclasses|__class__|config)\.(iteritems|items)\(\)"
            patterns = [
                network_patterns,
                from_import_modules,
                import_modules,
                file_manipulation,
                possible_injection,
            ]
            template_pairs = [("<%.*", ".*%>"), ("{{.*", ".*}}"), ("{%.*", ".*%}")]

            for search_pattern in [
                pair[0] + pattern + pair[1]
                for pattern in patterns
                for pair in template_pairs
            ]:
                if re.search(search_pattern, content):
                    reporter_output = f"Hidden python script found. File: {filepath}"
                    reporter.manual_check(reporter_output, file_name=filepath)
                    break


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.0.0")
def check_for_compiled_python(app, reporter):
    """Check that there are no `.pyc` or `.pyo` files included in the app."""
    for directory, filename, _ in app.iterate_files(types=[".pyc", ".pyo"]):
        current_file_relative_path = os.path.join(directory, filename)
        reporter_output = (
            f"A Compiled Python file was detected. File: {current_file_relative_path}"
        )
        reporter.fail(reporter_output, current_file_relative_path)


@splunk_appinspect.tags("cloud", "ast", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_possible_threading(app, reporter):
    """Check for the use of threading, and multiprocesses. Threading or process must be
    used with discretion and not negatively affect the Splunk installation as a
    whole.
    """
    client = app.python_analyzer_client
    circle_check_namespace = [
        "os.forkpty",
        "os.fork",
        "thread.start_new_thread",
        "os.kill",
        "os.killpg",
        "threading.Thread.start",
        "multiprocessing.Process.start",
    ]
    modules = [
        metadata_consts.ModuleNameConsts.OS,
        metadata_consts.ModuleNameConsts.SUBPROCESS,
        metadata_consts.ModuleNameConsts.THREAD,
        metadata_consts.ModuleNameConsts.THREADING,
        metadata_consts.ModuleNameConsts._THREAD,  # pylint: disable=W0212
        metadata_consts.ModuleNameConsts.MULTIPROCESSING,
    ]
    check_objects = (
        metadata_store.query()
        .namespace_prefixes(modules)
        .tag(metadata_consts.TagConsts.THREAD_SECURITY)
        .python_compatible()
        .collect()
    )
    for file_path, ast_info in client.get_all_ast_infos():
        for check_object in check_objects:
            module_name = ".".join(check_object.namespace.split(".")[:-1])
            # questionable functions in circle invoke
            if check_object.namespace in circle_check_namespace:
                loop_nodes = utilities.find_python_function_in_loop(
                    ast_info, module_name, check_object.name
                )
                for node in loop_nodes:
                    reporter_output_for_loopcheck = (
                        f"The following line contains questionable usage `{check_object.namespace}` in loop. "
                        "Use threading and multiprocessing with discretion."
                        " "
                        f"File: {file_path} "
                        f"Line: {node.lineno}"
                    )
                    reporter.warn(
                        reporter_output_for_loopcheck,
                        file_name=file_path,
                        line_number=node.lineno,
                    )
            else:
                node_linenos = ast_info.get_module_function_call_usage(
                    module_name, check_object.name, lineno_only=True
                )
                for node_lineno in node_linenos:
                    reporter_output = (
                        f"The following line contains {check_object.namespace} usage. "
                        "Use threading and multiprocessing with discretion."
                        " "
                        f"File: {file_path} "
                        f"Line: {node_lineno}"
                    )
                    reporter.warn(
                        reporter_output,
                        file_name=file_path,
                        line_number=node_lineno,
                    )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_built_in_import_function(app, reporter):
    """Check that the python `__import__` method is not used in a way that
    can be exploited (e.g., __import__(conf_setting) is at risk of code
    injection).
    """
    # This method shouldn't be used because imports should be explicit to
    # prevent execution of unintended code. If you're dynamically loading
    # libraries via strings there is some concern
    # https://docs.python.org/2/library/functions.html#__import__
    # Nice SO dicussion on this here:
    # http://stackoverflow.com/questions/28231738/import-vs-import-vs-importlib-import-module
    # http://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
    # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
    reporter_output_template = (
        "The `{}` function was detected being"
        " used. Please use the `import` keyword instead."
        " Third-Party libraries are exempt from this"
        " requirement."
    )

    import_function = [metadata_consts.built_in_import_function()]

    files_with_results = AstSearcher(app.python_analyzer_client).search(import_function)

    reporter.ast_manual_check(reporter_output_template, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_file_and_directory_access(app, reporter):
    """Check for possible file and directory access, they could be used in external file manipulation"""
    function_reporter_output = (
        "The following line will be inspected during code review. "
        + "The `{}` module/method can be used to access file/directory outside of the app dir. "
        + "Function call arguments: {}, keywords: {} "
    )
    modules = [
        metadata_consts.ModuleNameConsts.OS,
        metadata_consts.ModuleNameConsts.SHUTIL,
        metadata_consts.ModuleNameConsts.TEMPFILE,
        metadata_consts.ModuleNameConsts.LINECACHE,
        metadata_consts.ModuleNameConsts.EMAIL,
        metadata_consts.ModuleNameConsts.IO,
    ]
    functions = (
        metadata_store.query()
        .namespace_prefixes(modules)
        .tag(metadata_consts.TagConsts.FILE_READ_AND_WRITE)
        .python_compatible()
        .functions()
    )

    files_with_results = AstSearcher(app.python_analyzer_client).search(
        functions, get_func_params=True
    )
    reporter.ast_manual_check(function_reporter_output, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_python_udp_network_communications(app, reporter):
    """Check for UDP network communication"""
    reporter_output = (
        "Please check for inbound or outbound UDP network communications."
        "Any programmatic UDP network communication is prohibited due to security risks in Splunk Cloud and App Certification."
        "The use or instruction to configure an app using Settings -> Data Inputs -> UDP within Splunk is permitted. (Note: "
        "UDP configuration options are not available in Splunk Cloud and as such do not impose a security risk."
    )
    client = app.python_analyzer_client
    for filepath, ast_info in client.get_all_ast_infos():
        # find inner call node usages
        query = ast_info.query().call_nodes(force_propagate=False)
        while not query.is_end():
            query.call_nodes(force_propagate=False)
        udp_nodes = (
            query.filter(
                Any(
                    ast_info.get_module_function_call_usage(
                        "socket", "socket", fuzzy=True
                    )
                )
            )
            .filter(Any(ast_info.get_module_usage("socket.AF_INET")))
            .filter(Any(ast_info.get_module_usage("socket.SOCK_DGRAM")))
            .collect()
        )
        for node in udp_nodes:
            reporter.fail(reporter_output, filepath, node.lineno)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_unencrypted_network_communications(app, reporter):
    """Check that all network communications are encrypted"""
    message = (
        "Please check for inbound or outbound unencrypted network communications in `{}`. "
        "All communications with Splunk Cloud must be encrypted."
    )

    components = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.APPLICATION_LAYER_PROTOCOL_CONNECTION)
        .python_compatible()
        .collect()
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_all_python_files_are_well_formed(app, reporter):
    """Check all python files are well formed under python2 and python3 standard"""

    error_template = (
        "Python script is not well formed, {message} when parser try to parse. "
        "Runtime errors and possible style issues could exist when it is executed. "
        "Please manual check if the whole app is broken, if yes, fail this app. "
        "If syntax error only block part of app's functionality, warn developer to fix it. "
        "File: {filepath}"
    )
    syntax_error_message = "syntax error found in python script"
    null_byte_error_message = "python script contains null byte"
    other_exception_message = "issues like `StackOverFlow` or `SystemError` may exist"

    client = app.python_analyzer_client
    for filepath in client.get_syntax_error_files():
        reporter.manual_check(
            error_template.format(message=syntax_error_message, filepath=filepath),
            filepath,
        )
    for filepath in client.get_null_byte_error_files():
        reporter.manual_check(
            error_template.format(message=null_byte_error_message, filepath=filepath),
            filepath,
        )
    for filepath in client.get_other_exception_files():
        reporter.manual_check(
            error_template.format(message=other_exception_message, filepath=filepath),
            filepath,
        )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_builtin_functions(app, reporter):
    """Check for builtin functions(`open`, `eval`, `execfile`, `file`) usages in python files"""
    # open, file, execfile usages
    reporter_output = (
        "The following line will be inspected during code review. "
        + "The `{}` module/method can be used to manipulate files outside of the app dir. "
    )
    built_in_file_functions = metadata_consts.file_manipulation_functions()

    def has_args(call_node, ast_info):  # pylint: disable=W0613
        return call_node.args

    files_with_results = AstSearcher(app.python_analyzer_client).search(
        built_in_file_functions, node_filter=has_args
    )
    reporter.ast_manual_check(reporter_output, files_with_results)

    # eval usage
    reporter_output = (
        "The following line will be inspected during code review. "
        + "The {} module/method can be used to execute arbitrary expression. "
    )

    built_in_eval_functions = [metadata_consts.built_in_eval_function()]

    def has_non_string_args(call_node, ast_info):
        if call_node.args:
            variable = ast_info.get_variable_details(call_node.args[0])
            # if variable could be parsed as string, analyzer could cover its usage
            return not AstVariable.is_string(variable)
        return False

    files_with_results = AstSearcher(app.python_analyzer_client).search(
        built_in_eval_functions, node_filter=has_non_string_args
    )
    reporter.ast_manual_check(reporter_output, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_python_untrusted_xml_functions(app, reporter):
    """Check for untrusted xml usages in python libraries"""
    message = (
        "The following lines should be inspected during code review, the xml functions not safe enough. "
        "Using various XLM methods to parse untrusted XML data is known to be vulnerable to XML attacks. "
        "Methods should be replaced with their defusedxml equivalents."
        "Module/Method is {} "
    )
    functions = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.FILE_READ_AND_WRITE)
        .namespace_prefix(metadata_consts.ModuleNameConsts.XML)
        .python_compatible()
        .functions()
    )
    classes = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.XML_RPC_CONNECTION)
        .python_compatible()
        .classes()
    )
    components = functions + classes

    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_data_persistence(app, reporter):
    """check for data persistence usage which could be used to invoke marshall function call"""

    # ignore nodes that creating in memory db
    def _is_non_in_memory_db_creation(node, ast_info):
        if node.args:
            arg = node.args[0]
            variable = ast_info.get_variable_details(arg)
            return not (
                AstVariable.is_string(variable)
                and variable.variable_value == ":memory:"
            )

        return True

    serialization_reporter_output = (
        "The following lines should be inspected during code review, `{}` could be used to "
        "serialize and deserialize python object. Check if serialization result will be stored "
        "outside of App dir."
    )
    persistence_reporter_output = (
        "The following lines should be inspected during code review, `{}` could be used to "
        "store memory data to disk. Check if in-memory data will be stored outside of App "
        "dir."
    )

    serialization_modules = [
        metadata_consts.ModuleNameConsts.PICKLE,
        metadata_consts.ModuleNameConsts.CPICKLE,
        metadata_consts.ModuleNameConsts.MARSHAL,
    ]
    persistence_modules = [
        metadata_consts.ModuleNameConsts.SHELVE,
        metadata_consts.ModuleNameConsts.ANYDBM,
        metadata_consts.ModuleNameConsts.DBM,
        metadata_consts.ModuleNameConsts.GDBM,
        metadata_consts.ModuleNameConsts.DUMBDBM,
    ]

    serialization_functions = (
        metadata_store.query()
        .namespace_prefixes(serialization_modules)
        .tag(metadata_consts.TagConsts.DATA_PERSISTENCE)
        .python_compatible()
        .functions()
    )
    persistence_functions = (
        metadata_store.query()
        .namespace_prefixes(persistence_modules)
        .tag(metadata_consts.TagConsts.DATA_PERSISTENCE)
        .python_compatible()
        .functions()
    )

    searcher = AstSearcher(app.python_analyzer_client)
    files_with_results = searcher.search(serialization_functions)
    reporter.ast_manual_check(serialization_reporter_output, files_with_results)

    files_with_results = searcher.search(persistence_functions)
    reporter.ast_manual_check(persistence_reporter_output, files_with_results)

    sqlite3_functions = (
        metadata_store.query()
        .namespace_prefix(metadata_consts.ModuleNameConsts.SQLITE3)
        .tag(metadata_consts.TagConsts.DATA_PERSISTENCE)
        .python_compatible()
        .functions()
    )

    files_with_results = searcher.search(
        sqlite3_functions, node_filter=_is_non_in_memory_db_creation
    )
    reporter.ast_manual_check(persistence_reporter_output, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_plain_text_credentials_in_python(app, reporter):
    """check for plain text credentials disclosure in python files"""
    sensitive_name_patterns = [
        "login",
        "password",
        "pwd",
        "passwd",
        "community",
        "privpass",
    ]

    def check_variable_name(variable_name):
        return any(
            map(
                lambda pattern: re.search(pattern, variable_name, re.IGNORECASE),
                sensitive_name_patterns,
            )
        )

    client = app.python_analyzer_client
    node_to_name_dict = {}
    for filepath, ast_info in client.get_all_ast_infos():
        all_ast_nodes = set()
        for variable_name, ast_node_set in filter(
            lambda tuple: check_variable_name(tuple[0]),
            iter(ast_info.variable_usage.items()),
        ):
            for ast_node in ast_node_set:
                node_to_name_dict[ast_node] = variable_name
                variable = ast_info.get_variable_details(ast_node)
                if AstVariable.is_number(variable) or AstVariable.is_string(variable):
                    all_ast_nodes.add(ast_node)
        all_assign_nodes = (
            ast_info.query()
            .propagate_nodes(ast.Assign)
            .filter(Any(all_ast_nodes))
            .collect()
        )
        sensitive_ast_nodes = set()
        for assign_node in all_assign_nodes:
            sensitive_ast_nodes |= utilities.fetch_all_nodes_belonging_to_given_subtree(
                assign_node, all_ast_nodes
            )
        for sensitive_node in sensitive_ast_nodes:
            node_variable = ast_info.get_variable_details(sensitive_node)
            reporter_output = (
                "The following lines should be inspected during code review, "
                "Possible plain text credentials disclosure here, "
                f"`{node_to_name_dict[sensitive_node]} = {node_variable.variable_value}` "
                f"File: {filepath} Line: {sensitive_node.lineno}"
            )

            reporter.manual_check(
                reporter_output,
                file_name=filepath,
                line_number=sensitive_node.lineno,
            )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_interprocess_communication_and_networking(app, reporter):
    """check if networking or file manipulation exist in interprocess modules usage"""
    inheritance_output_template = (
        "The following lines should be inspected during code review. "
        "Class inherited from `{}` could be used to communicate with outside services or "
        "files. "
    )
    socket_connection_template = (
        "The following lines should be inspected during code review. "
        "`{}` could be used to open socket connection to outside service. "
    )
    classes = (
        metadata_store.query()
        .namespace_prefixes(
            [
                metadata_consts.ModuleNameConsts.ASYNCHAT,
                metadata_consts.ModuleNameConsts.ASYNCORE,
            ]
        )
        .tag(metadata_consts.TagConsts.NETWORK_CONNECTION)
        .python_compatible()
        .classes()
    )

    searcher = AstSearcher(app.python_analyzer_client)
    files_with_results = searcher.search(
        classes, node_filter=is_sub_class_def, search_module_usage=True
    )
    reporter.ast_manual_check(inheritance_output_template, files_with_results)

    socket_functions = (
        metadata_store.query()
        .namespace_prefixes([metadata_consts.ModuleNameConsts.SOCKET])
        .tag(metadata_consts.TagConsts.NETWORK_CONNECTION)
        .python_compatible()
        .functions()
    )

    files_with_results = searcher.search(socket_functions)
    reporter.ast_manual_check(socket_connection_template, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_generic_operating_system_services(app, reporter):
    """check if generic operating system modules could be used to communicate with outside services, files or systems"""
    message = (
        "The following lines should be inspected during code review. `{}` could be used to receive data from "
        "outside or log data to outside. "
    )
    query = (
        metadata_store.query()
        .namespace_prefixes(
            [
                metadata_consts.ModuleNameConsts.ARGPARSE,
                metadata_consts.ModuleNameConsts.LOGGING,
                metadata_consts.ModuleNameConsts.GETPASS,
            ]
        )
        .tag(metadata_consts.TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
        .python_compatible()
    )
    components = query.functions() + query.classes()

    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_reverse_shell_and_backdoor(app, reporter):
    """check if possible reverse shell exist in python code"""
    client = app.python_analyzer_client
    for filepath, ast_info in client.get_all_ast_infos():
        # subprocess function call usage(e.g. `subprocess.call`, `subprocess.check_output`)
        subprocess_usages = set(
            ast_info.get_module_function_call_usage("subprocess", fuzzy=True)
        )
        # `socket.socket` usage
        socket_usages = set(ast_info.get_module_function_call_usage("socket", "socket"))
        # file descriptor manipulation(e.g. `os.dup`, `os.dup2`)
        dup_usages = set(ast_info.get_module_function_call_usage("os", "dup"))
        dup2_usages = set(ast_info.get_module_function_call_usage("os", "dup2"))
        dup_all_usages = dup_usages | dup2_usages

        candidate_subprocess_usage = set()
        for dup_usage in dup_all_usages:
            for subprocess_usage in subprocess_usages:
                for socket_usage in socket_usages:
                    if ast_info.is_in_same_code_block(
                        [dup_usage, subprocess_usage, socket_usage]
                    ):
                        candidate_subprocess_usage.add(subprocess_usage)

        for subprocess_usage in candidate_subprocess_usage:
            reporter_output = (
                "The following lines should be inspected during code review. "
                "Possible reverse shell detected in this code block, "
                f"`subprocess` module's usage is provided. File: {filepath}, Line: {subprocess_usage.lineno}"
            )
            reporter.manual_check(
                reporter_output,
                file_name=filepath,
                line_number=subprocess_usage.lineno,
            )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_python_runtime_services(app, reporter):
    """Check if python runtime services could be used to manipulate system python objects"""
    message = (
        "The following lines should be inspected during code review, "
        "Possible system python objects manipulation `{}` found here. "
    )

    functions = (
        metadata_store.query()
        .namespace_prefixes(
            [
                metadata_consts.ModuleNameConsts.GC,
                metadata_consts.ModuleNameConsts.INSPECT,
            ]
        )
        .python_compatible()
        .functions()
    )

    files_with_results = AstSearcher(app.python_analyzer_client).search(functions)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_custom_python_interpreters(app, reporter):
    """Check if custom python interpreters could be used in malicious code execution"""
    message = "The following lines should be inspected during code review, custom python interpreters trying to run unknown code, usage is `{}`"

    functions = (
        metadata_store.query()
        .namespace_prefixes([metadata_consts.ModuleNameConsts.CODE])
        .tag(metadata_consts.TagConsts.STRING_EXECUTION)
        .python_compatible()
        .functions()
    )

    files_with_results = AstSearcher(app.python_analyzer_client).search(functions)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_python_multimedia_services(app, reporter):
    """Check if multimedia services module could be used to execute unknown-source multimedia files"""
    message = "The following lines should be inspected during code review, multimedia service module usage `{}` detected."

    multimedia_modules = [
        metadata_consts.ModuleNameConsts.AIFC,
        metadata_consts.ModuleNameConsts.SUNAU,
        metadata_consts.ModuleNameConsts.WAVE,
        metadata_consts.ModuleNameConsts.CHUNK,
    ]
    query = (
        metadata_store.query()
        .namespace_prefixes(multimedia_modules)
        .tag(metadata_consts.TagConsts.FILE_READ_AND_WRITE)
        .python_compatible()
    )
    components = query.functions() + query.classes()

    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_data_compression_and_archiving(app, reporter):
    """check if data compression and archiving libraries could be used to read & write files outside of app dir"""
    message = (
        "The following lines should be inspected during code review, "
        "`{}` could be used to create an archiving object, it can read or write file "
        "outside of app dir."
    )
    query = (
        metadata_store.query()
        .namespace_prefixes(
            [
                metadata_consts.ModuleNameConsts.GZIP,
                metadata_consts.ModuleNameConsts.BZ2,
                metadata_consts.ModuleNameConsts.ZIPFILE,
                metadata_consts.ModuleNameConsts.TARFILE,
            ]
        )
        .tag(metadata_consts.TagConsts.DATA_COMPRESSION)
        .python_compatible()
    )
    components = query.functions() + query.classes()
    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_ms_windows_specific_services(app, reporter):
    """Check if MS Windows specific service modules could be used to execute dangerous windows platform commands"""
    client = app.python_analyzer_client
    for file_path, ast_info in client.get_all_ast_infos():
        for module_name in ["msilib", "msvcrt", "_winreg"]:
            for lineno in ast_info.get_module_usage(module_name, lineno_only=True):
                reporter.manual_check(
                    "The following lines should be inspected during code review, "
                    f"MS Windows specific services usage `{module_name}` has been detected",
                    file_name=file_path,
                    line_number=lineno,
                )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_optional_operating_system_services(app, reporter):
    """Check for operating system features that are available on selected operating systems only."""
    objects = (
        metadata_store.query()
        .namespace_prefixes([metadata_consts.ModuleNameConsts.MMAP])
        .tag(metadata_consts.TagConsts.MEMORY_MAPPING)
        .python_compatible()
        .collect()
    )
    message = (
        "The following lines should be inspected during code review, operating system feature `{}` has been "
        "detected. "
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(objects)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_restricted_execution(app, reporter):
    """Check if restricted execution exist in current app"""
    client = app.python_analyzer_client
    for file_path, ast_info in client.get_all_ast_infos():
        for module_name in ["rexec", "Bastion"]:
            for lineno in ast_info.get_module_usage(module_name, lineno_only=True):
                reporter.manual_check(
                    "The following lines should be inspected during code review, "
                    f"restricted execution `{module_name}` has been detected",
                    file_name=file_path,
                    line_number=lineno,
                )


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_internet_protocols_and_support(app, reporter):
    """Check for the use of web server classes, they could be used to start a internal server in current app"""
    message = "The following lines should be inspected during code review, web server could be run with `{}`."
    objects = (
        metadata_store.query()
        .namespace_prefixes(
            [
                metadata_consts.ModuleNameConsts.WSGIREF,
                metadata_consts.ModuleNameConsts.SOCKET_SERVER,
                metadata_consts.ModuleNameConsts.SOCKET_SERVER_PY3,
                metadata_consts.ModuleNameConsts.SIMPLE_XML_RPC_SERVER,
                metadata_consts.ModuleNameConsts.DOC_XML_RPC_SERVER,
                metadata_consts.ModuleNameConsts.BASE_HTTP_SERVER,
                metadata_consts.ModuleNameConsts.HTTP,
            ]
        )
        .tag(metadata_consts.TagConsts.WEB_SERVER)
        .python_compatible()
        .collect()
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(objects)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_root_privilege_escalation(app, reporter):
    """Check possible root privilege escalation"""

    def is_sudo_and_su_usage_exists(call_node, ast_info):
        for arg in call_node.args:
            for ast_node in ast.walk(arg):
                variable = ast_info.get_variable_details(ast_node)
                if AstVariable.is_string(variable):
                    # check exactly match and prefix match
                    if variable.variable_value in ["su", "sudo"]:
                        return True
                    if variable.variable_value.startswith(
                        "su "
                    ) or variable.variable_value.startswith("sudo "):
                        return True
        return False

    check_objects = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION)
        .python_compatible()
        .collect()
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(
        check_objects, node_filter=is_sudo_and_su_usage_exists
    )
    reporter.ast_fail("Root privilege escalation detected using {}", files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_program_frameworks(app, reporter):
    """Check if program frameworks could be used to interface with web part"""
    check_objects = (
        metadata_store.query()
        .namespace_prefix(metadata_consts.ModuleNameConsts.CMD)
        .tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION)
        .python_compatible()
        .collect()
    )
    message = "The following lines should be inspected during code review, {}'s derived class could be used to interface with other part of system. "
    searcher = AstSearcher(app.python_analyzer_client)
    files_with_results = searcher.search(
        check_objects, node_filter=is_sub_class_def, search_module_usage=True
    )
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_importing_modules(app, reporter):
    """Check Python code for importing modules dynamically."""
    components = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.MODULE_IMPORTING)
        .python_compatible()
        .collect()
    )
    message = (
        "The following lines should be inspected during code review, Python code `{}` for dynamically importing "
        "module has been detected."
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_manual_check(message, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "security", "ast", "manual")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_debugging_and_profiling(app, reporter):
    """Check if debugging library could be used to execute arbitrary commands"""
    check_objects = (
        metadata_store.query()
        .namespace_prefix(metadata_consts.ModuleNameConsts.TRACE)
        .tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION)
        .python_compatible()
        .collect()
    )
    message = "The following lines should be inspected during code review, `{}` could be used to execute arbitrary commands."
    files_with_results = AstSearcher(app.python_analyzer_client).search(check_objects)
    reporter.ast_manual_check(message, files_with_results)
