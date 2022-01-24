"""
Format analysis module.
=======================

This will use the regexp rules given in configuration file to identify errors.
It intends to follows the coding conventions
mentioned in
`OMS Documentation Wiki page <https://alm.engr.colostate.edu/cb/wiki/16983>`__

The repalcement pipeline exists but is not implemented fully,
since I am not so sure of the result for multiple errors in one line.

"""


TAB_WIDTH = 8


def fmt_analysis(lines, lines_with_comments, start_line, rules):
    """Start the linter of file FILENAME."""
    all_errors = dict()

    for i, (line, line_with_comments) in enumerate(zip(lines, lines_with_comments), start_line):
        errors_found = _parse_format_line(line, line_with_comments, i, rules)

        for key, value in errors_found.items():
            if key in all_errors:
                all_errors[key].extend(value)
            else:
                all_errors[key] = value

    return all_errors


def _parse_format_line(line, line_with_comments, line_no, rules):
    """Analyse line

    :param line: str, line itself
    :param line_no: int, position in the file
    :param rules: rules read from config
    """

    out = dict()
    for key, rule in rules.items():
        line_ = line_with_comments if rule["include-comments"] else line
        error_info = _parse_format_rule(line_, line_with_comments, rule)

        if error_info is not None:
            msg_info = {"line_no": line_no, "line": line_with_comments}
            msg_info.update(error_info)

            if key in out:
                out[key].append(msg_info)
            else:
                out[key] = [msg_info]

    return out


def _parse_format_rule(line, line_with_comments, rule):
    """Interpret rules

    :param line: str, line to check
    :param line: str, line to check with comments
    :param rule: key to the rules dictionary
    """

    # TODO: are multiple errors being accounted for?

    found_error = False
    for res in rule["regexp"].finditer(line):
        found_error = True
        column = _find_true_position(res.start(), line_with_comments)
        span = _find_true_position(res.end(), line_with_comments) - column

    if found_error:
        return {'column': column, 'span': span}

    return None


def _find_true_position(pos, line):
    return len(line[:pos].expandtabs(TAB_WIDTH))
