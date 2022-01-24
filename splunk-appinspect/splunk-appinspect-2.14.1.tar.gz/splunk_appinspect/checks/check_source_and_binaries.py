# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Source code and binaries standards
"""

# TODO: Provide url link to the criteria here in the docstring
import logging
import os
import platform
import re
import stat

import splunk_appinspect
import splunk_appinspect.check_routine as check_routine

if not platform.system() == "Windows":
    import magic
else:
    import ntsecuritycon as con  # pylint: disable=E0401
    import win32security  # pylint: disable=E0401

logger = logging.getLogger(__name__)
report_display_order = 5


@splunk_appinspect.tags("splunk_appinspect", "appapproval", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.0.0")
def check_for_bin_files(app, reporter):
    """Check that files outside of the `bin/` and `appserver/controllers` directory do not have execute
    permissions and are not .exe files.
    On Unix platform, Splunk recommends 644 for all app files outside of the `bin/` directory, 644 for
    scripts within the `bin/` directory that are invoked using an interpreter (e.g. `python my_script.py`
    or `sh my_script.sh`), and 755 for scripts within the `bin/` directory that are invoked directly
    (e.g. `./my_script.sh` or `./my_script`).
    On Windows platform, Splunk recommends removing user's FILE_GENERIC_EXECUTE for all app files outside
    of the `bin/` directory except users in ['Administrators', 'SYSTEM', 'Authenticated Users', 'Administrator'].
    """
    directories_to_exclude_from_root = ["bin"]
    for dir, filename, ext in app.iterate_files(
        excluded_dirs=directories_to_exclude_from_root
    ):
        if dir == (os.path.join("appserver", "controllers") + os.sep):
            continue
        current_file_relative_path = os.path.join(dir, filename)
        current_file_full_path = app.get_filename(current_file_relative_path)
        exe_file_report_output = (
            f"An executable file was detected. File: {current_file_relative_path}"
        )
        if platform.system() == "Windows":
            EXCLUDED_USERS_LIST = [
                "Administrators",
                "SYSTEM",
                "Authenticated Users",
                "Administrator",
            ]
            ACCESS_ALLOWED_ACE = 0
            if ext == ".exe":
                reporter.fail(exe_file_report_output, current_file_relative_path)
            else:
                for ace_type, user, access in _read_windows_file_ace(
                    current_file_full_path
                ):
                    if (
                        ace_type == ACCESS_ALLOWED_ACE
                        and user not in EXCLUDED_USERS_LIST
                        and _has_permission(access, con.FILE_GENERIC_EXECUTE)
                    ):
                        reporter.warn(
                            "This file has execute permissions for users otherwise SYSTEM, Administrators, "
                            f"Administrator and Authenticated Users. File: {current_file_relative_path}",
                            current_file_relative_path,
                        )
        else:
            file_statistics = os.stat(current_file_full_path)
            # Checks the file's permissions against execute flags to see if the file
            # is executable
            if bool(
                file_statistics.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            ):
                reporter.fail(
                    "This file has execute permissions for owners, groups, or others. "
                    f"File: {current_file_relative_path}",
                    current_file_relative_path,
                )
            elif ext == ".exe":
                reporter.fail(exe_file_report_output, current_file_relative_path)


@splunk_appinspect.tags("splunk_appinspect", "appapproval", "manual", "cloud")
@splunk_appinspect.cert_version(min="1.0.0")
def check_for_executable_flag(app, reporter):
    """Check that files outside of the `bin/` directory do not appear to be
    executable according to the Unix `file` command. From `man file`: files have
    a ``magic number'' stored in a particular place near the beginning of the
    file that tells the UNIX operating system that the file is a binary
    executable."""
    if platform.system() == "Windows":
        # TODO: tests needed
        reporter_output = "Windows file permissions will be inspected during review."
        reporter.manual_check(reporter_output)
    else:
        directories_to_exclude = ["bin"]
        for directory, file, ext in app.iterate_files(
            excluded_dirs=directories_to_exclude
        ):
            # filter appserver/controllers/ out
            if directory == "appserver/controllers/":
                continue
            current_file_relative_path = os.path.join(directory, file)
            current_file_full_path = app.get_filename(current_file_relative_path)
            if current_file_relative_path in app.info_from_file:
                file_output = app.info_from_file[current_file_relative_path]
            else:
                with open(
                    current_file_full_path, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    file_output = magic.from_buffer(f.read())
            file_output_regex = re.compile(
                "(.)*executable(.)*", re.DOTALL | re.IGNORECASE | re.MULTILINE
            )
            if re.match(file_output_regex, file_output):
                if current_file_relative_path.endswith((".html", ".htm")):
                    if check_routine.is_mako_template(current_file_full_path):
                        continue
                reporter_output = (
                    "The executable will be inspected during code review: "
                    f"File: {current_file_relative_path}"
                )
                reporter.manual_check(reporter_output, current_file_relative_path)


@splunk_appinspect.tags("splunk_appinspect", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_urls_in_files(app, reporter):
    """Check that URLs do not include redirect or requests from external web
    sites.
    """
    # It's a little verbose but with the explicit-ness comes
    # References
    # http://tools.ietf.org/html/rfc3986
    # http://stackoverflow.com/questions/4669692/valid-characters-for-directory-part-of-a-url-for-short-links
    url_regex_pattern = (
        r"(\w*://)+"  # Captures protocol
        r"([\w\d\-]+\.[\w\d\-\.]+)+"  # Captures hostname
        r"(:\d*)?"  # Captures port
        r"(\/[^\s\?]*)?"  # Captures path
        r"(\?[^\s]*)?"
    )  # Capture query string

    excluded_types = [
        ".csv",
        ".gif",
        ".jpeg",
        ".jpg",
        ".md",
        ".org",
        ".pdf",
        ".png",
        ".svg",
        ".txt",
    ]
    excluded_directories = ["samples"]

    # Apps often contain links to Splunk resources in the documentation and such occurrence is flagged for manual
    # review. It is okay to trust and skip manual review for following base urls under splunk.com domain.
    # Splunk redirects http to https.
    excluded_base_urls = (
        "http://docs.splunk.com",
        "https://docs.splunk.com" "https://answers.splunk.com",
        "https://apps.splunk.com",
        "https://splunkbase.splunk.com",
    )

    url_matches = app.search_for_pattern(
        url_regex_pattern,
        excluded_dirs=excluded_directories,
        excluded_types=excluded_types,
    )

    if url_matches:
        # {url_pattern: {filename: [lineno_list]}}
        result_dict = {}

        for (fileref_output, match) in url_matches:
            url_match = match.group()
            filename, line_number = fileref_output.rsplit(":", 1)

            # Skip excluded base urls.
            if not url_match.startswith(excluded_base_urls):
                if url_match not in result_dict:
                    result_dict[url_match] = {}
                if filename not in result_dict[url_match]:
                    result_dict[url_match][filename] = []
                result_dict[url_match][filename].append(str(line_number))

                reporter_output = (
                    "A file was detected that contains that a url."
                    f" Match: {url_match}"
                    f" File: {filename}"
                    f" Line: {line_number}"
                )
                reporter.manual_check(reporter_output, filename, line_number)

        # create some extra manual checks in order to see results in a more convenient way
        for (url_match, file_dict) in result_dict.items():
            reporter_output = ""
            reporter_output += f"A url {url_match} was detected in the following files"
            for (file_name, lineno_list) in file_dict.items():
                reporter_output += ", (File: {}, Linenolist: [{}])".format(
                    file_name, ", ".join(lineno_list)
                )
            # don't need filename and line_number here, since it is an aggregated result
            reporter.manual_check(str(reporter_output))


@splunk_appinspect.tags("splunk_appinspect", "windows")
@splunk_appinspect.cert_version(min="1.0.0")
def check_for_expansive_permissions(app, reporter):
    """Check that no files have *nix write permissions for all users
    (xx2, xx6, xx7). Splunk recommends 644 for all app files outside of the
    `bin/` directory, 644 for scripts within the `bin/` directory that are
    invoked using an interpreter (e.g. `python my_script.py` or
    `sh my_script.sh`), and 755 for scripts within the `bin/` directory that are
    invoked directly (e.g. `./my_script.sh` or `./my_script`).
    Since appinspect 1.6.1, check that no files have nt write permissions for all users.
    """
    offending_files = []
    EXCLUDED_USERS_LIST = [
        "Administrators",
        "SYSTEM",
        "Authenticated Users",
        "Administrator",
    ]
    ACCESS_ALLOWED_ACE = 0
    for dir, file, ext in app.iterate_files():
        try:
            if os.name != "nt":
                st = os.stat(app.get_filename(dir, file))
                if bool(st.st_mode & stat.S_IWOTH):
                    offending_files.append(os.path.join(dir, file))
            else:
                # full path in GetFileSecurity should be
                # the absolute path in Windows
                full_path = os.path.join(app.app_dir, dir, file)
                file_owner = _get_windows_file_owner(full_path)
                for ace_type, user, access in _read_windows_file_ace(full_path):
                    # only need to consider AceType = ACCESS_ALLOWED_ACE
                    # not check users in EXCLUDED_USERS_LIST
                    if (
                        ace_type == ACCESS_ALLOWED_ACE
                        and user not in EXCLUDED_USERS_LIST
                        and user != file_owner
                        and _has_permission(access, con.FILE_GENERIC_WRITE)
                    ):
                        offending_files.append(full_path)
        except Exception:
            pass

    for offending_file in offending_files:
        reporter_output = (
            f"A {os.name} world-writable file was found. File: {offending_file}"
        )
        if os.name == "nt":
            reporter.warn(reporter_output)
        else:
            reporter.fail(reporter_output)


def _read_windows_file_ace(file_path):
    sd = win32security.GetFileSecurity(
        file_path, win32security.DACL_SECURITY_INFORMATION
    )
    dacl = sd.GetSecurityDescriptorDacl()
    if dacl is None:
        dacl = _new_dacl_with_all_control()
    # get the number of access control entries
    ace_count = dacl.GetAceCount()
    for i in range(ace_count):
        # rev: a tuple of (AceType, AceFlags)
        # access: ACCESS_MASK
        # usersid: SID
        rev, access, usersid = dacl.GetAce(i)
        user, _, _ = win32security.LookupAccountSid("", usersid)
        ace_type = rev[0]
        yield ace_type, user, access


def _has_permission(access, permission):
    return access & permission == permission


def _new_dacl_with_all_control():
    dacl = win32security.ACL()
    everyone, _, _ = win32security.LookupAccountName("", "Everyone")
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, everyone)
    return dacl


def _get_windows_file_owner(file_path):
    sd = win32security.GetFileSecurity(
        file_path, win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = sd.GetSecurityDescriptorOwner()
    user, _, _ = win32security.LookupAccountSid(None, owner_sid)
    return user


@splunk_appinspect.tags("splunk_appinspect", "appapproval", "manual")
@splunk_appinspect.cert_version(min="1.0.0")
def check_platform_specific_binaries(app, reporter):
    """Check that documentation declares platform-specific binaries."""
    # Can't read the documentation, but we can check for native binaries
    # TODO: we should not be generating manual checks if directories are empty
    bin_directories = [
        bin_directory
        for arch in app.arch_bin_dirs
        if arch != app.DEFAULT_ARCH
        for bin_directory in app.arch_bin_dirs[arch]
    ]
    if app.some_directories_exist(bin_directories):
        reporter_output = "Documentation will be read during code review."
        reporter.manual_check(reporter_output)
    else:
        reporter_output = "No platform-specific binaries found."
        reporter.not_applicable(reporter_output)
