#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sbt_pre_post_sphinx_bak.py is called before sphinx is called, and again after
sphinx has completed. The pre call comments out the overloaded functions in
time_hdr to prevent sphinx from trying to document the overloaded
functions which ends up looking bad. The post call restores the overload
functions and also fixes the documentation by removing the extra slash
that appears for the default value for the end parameter shown in the
function signatures.Sphinx builds the doc with the end parameter shown as:
end = '\\n'

The sbt_pre_post_sphinx_bak.py code will set it to: end = '\n'

"""
import sys


def hide_overloaded_functions(path_to_file) -> None:
    with open(path_to_file, 'r') as file:  # open for read
        file_lines = file.readlines()  # giant list

    overload_detected = False
    for idx, file_line in enumerate(file_lines):
        if '@overload' in file_line:
            overload_detected = True
            if file_line[0] == '#':
                return  # already done - don't do again, don't write file

        if overload_detected:
            if 'def time_box(wrapped: Optional[F]' in file_line:
                break  # we are at end of section to hide
            file_lines[idx] = '# ' + file_lines[idx]  # comment out

    with open(path_to_file, 'w') as file:  # open for write
        file.writelines(file_lines)


def remove_slash(path_to_file) -> None:
    with open(path_to_file, 'r') as file:  # open for read
        file_lines = file.readlines()

    search_text_items = ['&quot;' + repr('\\n') + '&quot', repr('\\n')]
    for search_text in search_text_items:
        for idx, file_line in enumerate(file_lines):
            if search_text in file_line:
                file_lines[idx] = file_lines[idx].replace(search_text,
                                                          repr('\n'))

    with open(path_to_file, 'w') as file:
        file.writelines(file_lines)


def main() -> None:
    if sys.argv[1] == '--pre':
        # sys.argv[2] has file path to time_hdr.py that has overload
        # statements to hide
        hide_overloaded_functions(sys.argv[2])
    if sys.argv[1] == '--post':
        # sys.argv[2] has file path to index.html that needs slashes removed
        remove_slash(sys.argv[2])


if __name__ == '__main__':
    sys.exit(main())
