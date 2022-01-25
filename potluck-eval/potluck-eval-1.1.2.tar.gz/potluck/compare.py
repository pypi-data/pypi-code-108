"""
Functions for comparing Python values, and for rendering the results of
those comparisons as HTML.

compare.py
"""

import re
import math
import cmath
import difflib

from . import html_tools
from . import phrasing


#-----------------#
# Strict equality #
#-----------------#

def report_unequal(val, ref):
    """
    Returns a status/explanation dictionary reporting that two values
    are unequal, including a report on their differences, which has
    different forms depending on the values themselves.
    """
    if isinstance(val, str) and isinstance(ref, str):
        val_lines = val.splitlines(keepends=True)
        ref_lines = ref.splitlines(keepends=True)

        diff = html_tools.html_diff_table(
            val_lines,
            ref_lines,
            'Actual value',
            'Corresponding lines (if any) in expected value'
        )
    else:
        rval = repr(val)
        rexp = repr(ref)
        if max(len(rval), len(rexp)) < 50:
            diff = "Actual: {}<br>\nExpected: {}".format(
                repr(val),
                repr(ref)
            )
        else:
            diff = "Actual:<br>\n{}<br><br>\nExpected:<br>\n{}".format(
                html_tools.dynamic_html_repr(val),
                html_tools.dynamic_html_repr(ref)
            )

    return {
        "status": "failed",
        "explanation": (
            "Actual value is different from the reference"
            " value:<br>\n{}"
        ).format(diff)
    }


def report_equal(val, ref):
    """
    Returns a status/explanation dictionary reporting that two values
    are equivalent.
    """
    val_repr = repr(val)
    if isinstance(val, str) and '\n' in val:
        val_repr = "'''\\\n{}'''".format(val)
    return {
        "status": "accomplished",
        "explanation": (
            "Actual value is the same as the reference value:<br>\n{}"
        ).format(
            html_tools.html_output_details(
                val_repr, # TODO: Pretty printing here
                "Value tested"
            )
        )
    }


def strict_equality_checker(val, ref, memo=None):
    """
    A checker to be used with OutputTest or ValueTest goals that ensures
    the output or value being checked is strictly equal to the reference
    output or value. If there is a difference, some kind of diff is
    printed, depending on the types of the values.

    Handles recursive structures composed of tuples, lists, sets, and/or
    dictionaries, but may choke on recursive structures stored in custom
    objects, in which case those objects will only be considered equal
    if they are the same object.
    """
    if memo is None:
        memo = set()

    mkey = (id(val), id(ref))
    # If we're already in the process of comparing these two objects to
    # each other, and we come across another comparison of the two, we
    # can safely return True for the sub-comparison, and let other
    # comparisons determine if they're equal or not.
    if mkey in memo:
        return {
            "status": "accomplished",
            "explanation": "Recursive comparison."
        }

    # Past this point, recursion might happen
    memo.add(mkey)

    if type(val) != type(ref):
        return report_unequal(val, ref)
    elif isinstance(val, (int, float, complex, type(None), bool, str)):
        if val == ref:
            return report_equal(val, ref)
        else:
            return report_unequal(val, ref)
    elif isinstance(val, (tuple, list)):
        if len(val) != len(ref):
            return report_unequal(val, ref)
        else:
            test = all(
                strict_equality_checker(v, r, memo)\
                    ["status"] == "accomplished" # noqa E211
                for (v, r) in zip(val, ref)
            )
            if test:
                return report_equal(val, ref)
            else:
                return report_unequal(val, ref)
    elif isinstance(val, (set)):
        sv = sorted(val)
        sr = sorted(ref)
        test = strict_equality_checker(sv, sr, memo)
        if test["status"] == "accomplished":
            return report_equal(val, ref)
        else:
            return report_unequal(val, ref)
    elif isinstance(val, (dict)):
        test = strict_equality_checker(
            sorted(val.keys()),
            sorted(ref.keys()),
            memo
        )
        if test["status"] != "accomplished":
            return report_unequal(val, ref)

        failed = False
        for key in val: # keys must be same at this point
            test = strict_equality_checker(val[key], ref[key], memo)
            if test["status"] != "accomplished":
                failed = True
                break

        if failed:
            return report_unequal(val, ref)
        else:
            return report_equal(val, ref)
    else:
        # Some kind of object that we don't know about; try calling
        # __eq__ if it has it, an upon a recursion error, simply
        # compare IDs (which is Python default behavior when __eq__
        # isn't present).
        if hasattr(val, "__eq__"):
            try:
                test = val == ref
            except RecursionError:
                test = val is ref
        else:
            test = val is ref

        if test:
            return report_equal(val, ref)
        else:
            return report_unequal(val, ref)


#---------------------------#
# Floating-point comparison #
#---------------------------#

def round_to_sig_figs(n, figs=5):
    """
    Rounds to the given number of significant figures (not decimal
    places). Computes the location of the first significant figure, and
    calls round with an appropriate (and possibly negative) precision
    value. Still subject to the limits of floating point numbers for very
    small values.
    """
    if n == 0:
        return 0
    exp = math.floor(math.log10(abs(n)))
    round_to = figs - exp
    return round(n, round_to)


def build_float_equality_checker(sig_figs=5, use_decimal_places=False):
    """
    Builds and returns a checker function that tests whether the
    submitted value (a float) is equal to the reference value (also a
    float) up to the given number of significant figures (to avoid
    penalizing students for floating point rounding issues if they did
    math operations in a different order from the solution. The
    significant figures are actually treated as such, not as decimal
    places, using round_to_sig_figs. This behavior is altered if
    use_decimal_places is True, in which case sig_figs is treated not as
    a number of significant figures but as a number of decimal places to
    round to.
    """
    def check_float_equality(val, ref):
        """
        Checks floating-point equality after rounding to a certain number
        of significant figures (or possibly decimal places).
        """
        if use_decimal_places:
            rval = round(val, sig_figs)
            rref = round(ref, sig_figs)
        else:
            rval = round_to_sig_figs(val, sig_figs)
            rref = round_to_sig_figs(ref, sig_figs)

        if rval == rref:
            return {
                "status": "accomplished",
                "explanation": (
                    "Value {} matches expected value to the required"
                  + " precision."
                ).format(val)
            }
        else:
            return {
                "status": "failed",
                "explanation": (
                    "Value {} does not match expected value {} to the "
                  + "required precision. Compared as:<br>\n"
                  + "{} (value)<br>\n"
                  + "{} (expected)"
                ).format(val, ref, rval, rref)
            }

    return check_float_equality


FLOAT_REL_TOLERANCE = 1e-8
"""
The relative tolerance for floating-point similarity (see
`cmath.isclose`).
"""

FLOAT_ABS_TOLERANCE = 1e-8
"""
The absolute tolerance for floating-point similarity (see
`cmath.isclose`).
"""


def numbers_are_equalish(val, ref):
    """
    Uses `cmath.isclose` to compare two floating-point numbers, and
    returns an evaluation result (a dictionary w/ status and explanation
    slots).

    The first number should be from the submitted code and the second
    should be the correct value.
    """
    if cmath.isclose(
        val,
        ref,
        rel_tol=FLOAT_REL_TOLERANCE,
        abs_tol=FLOAT_ABS_TOLERANCE
    ):
        return {
            "status": "accomplished",
            "explanation": {
                f"Value {val} matches expected value to the required"
                f"precision."
            }
        }
    else:
        return {
            "status": "failed",
            "explanation": (
                "Value {val} does not match expected value {ref} to the"
                " required precision."
            )
        }


#-------------------#
# String comparison #
#-------------------#

def multiline_strings_are_exactly_equal(val, ref):
    """
    A checker to be used with harnesses which generate multi-line strings
    where the outputs can reasonable be expected to be exactly equal.
    Displays results more nicely than `omni_compare` because it knows
    they'll be strings.
    """
    if not isinstance(val, str) or not isinstance(ref, str):
        raise TypeError(
            (
                "Can't check string equality for non-string value(s):\n"
              + "{}\nand\n{}"
            ).format(repr(val), repr(ref))
        )

    if val == ref:
        return {
            "status": "accomplished",
            "explanation": "Values are the same.<br>\n{}".format(
                html_tools.html_output_details(val, "Value tested")
            )
        }
    else:
        val_lines = val.splitlines(keepends=True)
        ref_lines = ref.splitlines(keepends=True)
        diffTable = html_tools.html_diff_table(
            val_lines,
            ref_lines,
            "Actual result",
            "Corresponding lines (if any) in expected result"
        )
        return {
            "status": "failed",
            "explanation": "Values are different.<br>\n{}".format(
                diffTable
            )
        }


def strings_are_equal_modulo_whitespace(val, ref, ignore_case=True):
    """
    A checker to be used with OutputTest or ValueTest goals that checks
    whether the value and the reference value are equivalent strings if
    whitespace is ignored completely. Fails if either value isn't a
    string. Ignores case by default.
    """
    trans = {ord(c): '' for c in ' \t\n\r'}
    if not isinstance(val, str) or not isinstance(ref, str):
        raise TypeError(
            (
                "Can't check string equality for non-string value(s):\n"
              + "{}\nand\n{}"
            ).format(repr(val), repr(ref))
        )

    val_collapsed = val.translate(trans)
    ref_collapsed = ref.translate(trans)

    if ignore_case:
        val_collapsed = val_collapsed.casefold()
        ref_collapsed = ref_collapsed.casefold()

    if val == ref:
        return {
            "status": "accomplished",
            "explanation": "Strings are the same.<br>\n{}".format(
                html_tools.html_output_details(val, "Value tested")
            )
        }
    elif val_collapsed == ref_collapsed:
        return {
            "status": "accomplished",
            "explanation": (
                "Strings are the same (ignoring whitespace).<br>\n{}"
            ).format(
                html_tools.html_output_details(
                    val_collapsed,
                    "Simplified value"
                )
            )
        }
    else:
        val_lines = val.splitlines(keepends=True)
        ref_lines = ref.splitlines(keepends=True)

        diffTable = html_tools.html_diff_table(
            val_lines,
            ref_lines,
            'Actual output',
            'Corresponding lines (if any) in expected output'
        )

        return {
            "status": "failed",
            "explanation": (
                "Actual value is different from the reference value:<br>\n{}"
            ).format(diffTable)
        }


def without_trailing_whitespace(s):
    """
    Returns the given string with any trailing whitespace removed.
    Returns an empty string if given only whitespace.
    """
    trailing = 0
    for c in s:
        if re.match(r'\s', c): # it's whitespace
            trailing += 1
        else:
            trailing = 0

    if trailing > 0:
        return s[:-trailing]
    else:
        return s


def without_trailing_whitespace_per_line(s):
    """
    Returns a version of the given multi-line string where trailing
    whitespace has been stripped from each line.
    """
    return '\n'.join(
        without_trailing_whitespace(line)
        for line in s.split('\n')
    )


def compress_line(s):
    """
    Compresses internal whitespace and strips trailing whitespace from a
    single line of text.
    """
    w = without_trailing_whitespace(s)
    return re.sub(r'\s+', ' ', w)


def compress_whitespace(s):
    """
    Returns a version of the given string where all runs of one or more
    whitespace characters on each line have been replaced with a single
    space character, and all trailing whitespace has been stripped from
    each line, plus any blank lines have been removed.
    """
    return '\n'.join(
        filter(
            lambda x: x != '',
            [
                compress_line(line)
                for line in s.split('\n')
            ]
        )
    )


def strings_are_equal_modulo_most_whitespace(
    val,
    ref,
    track_internal_whitespace=False,
    ignore_case=True
):
    """
    A checker to be used with OutputTest or ValueTest goals that checks
    whether the value and the reference value are exactly equivalent
    strings after any trailing and extra internal whitespace is deleted.
    Fails if either value isn't a string.

    if track_internal_whitespace is True, will be only partially
    successful if there are differences in non-trailing whitespace or
    blank lines.

    By default, case is ignored.
    """
    if not isinstance(val, str) or not isinstance(ref, str):
        raise TypeError(
            (
                "Can't check string equality for non-string value(s):\n"
              + "{}\nand\n{}"
            ).format(repr(val), repr(ref))
        )

    if ignore_case:
        val_stripped = without_trailing_whitespace_per_line(val).casefold()
        ref_stripped = without_trailing_whitespace_per_line(ref).casefold()
    else:
        val_stripped = without_trailing_whitespace_per_line(val)
        ref_stripped = without_trailing_whitespace_per_line(ref)

    val_compressed = compress_whitespace(val_stripped)
    ref_compressed = compress_whitespace(ref_stripped)

    if val == ref: # full equality
        return {
            "status": "accomplished",
            "explanation": "Strings are the same.<br>\n{}".format(
                html_tools.html_output_details(val, "Value tested")
            )
        }
    elif val_stripped == ref_stripped: # equal modulo trailing whitespace
        return {
            "status": "accomplished",
            "explanation": (
                "Strings are the same (ignoring trailing whitespace).<br>\n{}"
            ).format(
                html_tools.html_output_details(
                    val_stripped,
                    "Simplified value"
                )
            )
        }
    elif val_compressed == ref_compressed: # equal when compressed
        if track_internal_whitespace:
            val_lines = val.splitlines(keepends=True)
            ref_lines = ref.splitlines(keepends=True)

            diffTable = html_tools.html_diff_table(
                val_lines,
                ref_lines,
                "Actual output",
                "Corresponding lines (if any) in expected output"
            )
            return {
                "status": "partial",
                "explanation": (
                    "Strings aren't the same, but all differences are just"
                  + " in whitespace:<br>\n{}"
                ).format(diffTable)
            }
        else:
            return {
                "status": "accomplished",
                "explanation": (
                    "Strings are the same (ignoring most whitespace).<br>\n{}"
                ).format(
                    html_tools.html_output_details(
                        val_compressed,
                        "Simplified value"
                    )
                )
            }
    else:
        val_lines = val.splitlines(keepends=True)
        ref_lines = ref.splitlines(keepends=True)

        diffTable = html_tools.html_diff_table(
            val_lines,
            ref_lines,
            "Actual output",
            "Corresponding lines (if any) in expected output"
        )

        return {
            "status": "failed",
            "explanation": (
                "Actual value is different from the reference value:<br>\n{}"
            ).format(diffTable)
        }


word_re = re.compile(r"[\w']+")


def clean_word_list(line):
    """
    Takes a single line of output and produces a list of words, which are
    taken to be strictly contiguous sequences of characters in the \\w
    class, plus apostrophe.
    """
    return word_re.findall(line)


def rough_sequence_contains(
    val_lines,
    ref_lines,
    sequence_match_threshold,
    partial_sequence_threshold,
    line_match_threshold,
):
    """
    Returns the string "full" if when diffing val_lines and ref_lines,
    the percentage of lines from ref_lines that are matched is at or
    above the sequence_match_threshold, and the string "partial" if that
    threshold isn't met bu the partial_sequence_threshold is. Returns None
    if neither threshold is met.

    Adjacent delete/add pairs where the deleted line has a difflib
    sequence similarity ratio of at least the line_match_threshold are
    considered matching lines.
    """
    differ = difflib.Differ()
    comparison = [
        line
        for line in differ.compare(val_lines, ref_lines)
        if line[:2] != '? ' # filter out comment lines
    ]

    # chunk the diff to group sequences of additions and deletions
    chunks = []
    while comparison:
        if comparison[0][:2] == '  ': # grab a chunk of matches
            i = 0
            while i < len(comparison) and comparison[i][:2] == '  ':
                i += 1
            matching_block = comparison[:i]
            comparison = comparison[i:]
            chunks.append(('match', matching_block))

        elif comparison[0][:2] == '- ': # grab a chunk of deletions
            i = 0
            while i < len(comparison) and comparison[i][:2] == '- ':
                i += 1
            # If next thing is a + that matches the last -, don't include
            # the last -
            if (
                i < len(comparison)
            and comparison[i][:2] == '+ '
            and difflib.SequenceMatcher(
                    None,
                    comparison[i - 1][2:],
                    comparison[i][2:]
                ).ratio() >= line_match_threshold # noqa: E123
            ):
                missing_block = comparison[:i - 1]
                paired_block = comparison[i - 1:i + 1]
                comparison = comparison[i + 1:]
            else:
                missing_block = comparison[:i]
                paired_block = None
                comparison = comparison[i:]
            if missing_block: # might be empty list
                chunks.append(('missing', missing_block))
            if paired_block: # might be None
                chunks.append(('paired', paired_block))

        elif comparison[0][:2] == '+ ': # grab a chunk of additions
            i = 0
            while i < len(comparison) and comparison[i][:2] == '+ ':
                i += 1
            added_block = comparison[:i]
            comparison = comparison[i:]
            chunks.append(('added', added_block))

    # Count matched + unmatched lines
    matched = 0
    unmatched = 0
    for chtype, lines in chunks:
        if chtype == 'match':
            matched += len(lines)
        elif chtype == 'paired':
            matched += 1
        elif chtype == 'added':
            unmatched += len(lines)

    # Note we don't care about the number of deletions necessary

    # Who knows if matched + unmatched will add up? Who cares?
    match_proportion = max(
        matched / len(ref_lines),
        (len(ref_lines) - unmatched) / len(ref_lines)
    )

    # Make our decision
    if (match_proportion >= sequence_match_threshold):
        return "full"
    elif (match_proportion >= partial_sequence_threshold):
        return "partial"
    else:
        return None


def very_fuzzy_string_compare(
    val,
    ref,
    line_match_threshold=0.5,
    sequence_match_threshold=0.8,
    partial_sequence_threshold=None,
):
    """
    A checker to be used with OutputTest or ValueTest goals that checks
    whether the value and the reference value are kinda related. What it
    does is chops each line of both strings up into words, which consist
    of one or more alphanumeric characters, and ignores the rest of the
    line. These ordered tuples of words are made into lists, and the test
    succeeds if there is some ordered mapping from the word-tuple-list of
    the value to the word-tuple-list of the reference value that covers
    at least sequence_match_threshold percent of the items in the
    reference list, no matter how many items in the value list are
    unmatched (in other words, there may be a huge amount of extra
    output, but we don't care).

    The mapping may only map together lines where the difflib sequence
    similarity is at least the line_match_threshold (but this is after
    collapsing the tuple to a string with spaces in between, meaning that
    punctuation is ignored).

    The partial_sequence_threshold serves as the threshold for what
    percent of the reference sequence must be matched for the result to
    be a partial success. If not given, it will be set to 1/2 of the
    sequence_match_threshold.

    Case and blank lines are ignored.
    """

    if partial_sequence_threshold is None:
        partial_sequence_threshold = sequence_match_threshold / 2

    if not isinstance(val, str) or not isinstance(ref, str):
        raise TypeError(
            (
                "Can't check string equality for non-string value(s):\n"
              + "{}\nand\n{}"
            ).format(repr(val), repr(ref))
        )

    val_folded = val.casefold()
    ref_folded = ref.casefold()

    val_compressed = compress_whitespace(val_folded)
    ref_compressed = compress_whitespace(ref_folded)

    if val_folded == ref_folded: # full equality ignoring case
        return {
            "status": "accomplished",
            "explanation": "Strings are the same.<br>\n{}".format(
                html_tools.html_output_details(val, "Value tested")
            )
        }
    elif val_compressed == ref_compressed: # equal when compressed
        return {
            "status": "accomplished",
            "explanation": (
                "Strings are the same (ignoring most whitespace).<br>\n{}"
            ).format(
                html_tools.html_output_details(
                    val_compressed,
                    "Simplified value"
                )
            )
        }

    else: # we actually have to check matches
        val_raw_lines = val.splitlines(keepends=True)
        ref_raw_lines = ref.splitlines(keepends=True)

        diffTable = html_tools.html_diff_table(
            val_raw_lines,
            ref_raw_lines,
            "Actual output",
            "Corresponding lines (if any) in expected output"
        )

        val_wordlists = [
            clean_word_list(line)
            for line in val_compressed.splitlines()
            if clean_word_list(line)
        ]
        ref_wordlists = [
            clean_word_list(line)
            for line in ref_compressed.splitlines()
            if clean_word_list(line)
        ]

        val_wordlines = [' '.join(wl) for wl in val_wordlists]
        ref_wordlines = [' '.join(wl) for wl in ref_wordlists]

        # Check for a rough match between the sequences...
        match_status = rough_sequence_contains(
            val_wordlines,
            ref_wordlines,
            sequence_match_threshold,
            partial_sequence_threshold,
            line_match_threshold
        )

        if match_status == "full":
            return {
                "status": "accomplished",
                "explanation": (
                    "Strings are similar enough.<br>\n{}"
                ).format(diffTable)
            }
        elif match_status == "partial":
            return {
                "status": "partial",
                "explanation": (
                    "Strings are somewhat similar.<br>\n{}"
                ).format(diffTable)
            }
        else:
            return {
                "status": "failed",
                "explanation": (
                    "Actual value is different from the reference"
                  + " value:<br>\n{}"
                ).format(diffTable)
            }


def build_contains_re_checker(name, expression, required_matches=1):
    """
    Returns a checker function that tests whether the submitted value
    contains at least the required number of matches for the given
    regular expression (a string, pre-compiled expression, or function
    which will produce an re.Pattern when given a reference string). The
    name is used to describe the pattern in the explanation returned.
    """
    if isinstance(expression, str):
        build_regex = lambda ref: re.compile(expression)
    elif isinstance(expression, re.Pattern):
        build_regex = lambda ref: expression
    else:
        build_regex = expression

    def string_contains_re(val, ref):
        """
        This will be replaced.
        """
        regex = build_regex(ref)
        if not isinstance(val, str):
            return {
                "status": "failed",
                "explanation": (
                    "Value is not a string! (was looking for: '{}')"
                ).format(name)
            }
        matches = regex.findall(val)
        if len(matches) >= required_matches:
            if required_matches == 1:
                return {
                    "status": "accomplished",
                    "explanation": "Found {}.".format(name)
                }
            else:
                return {
                    "status": "accomplished",
                    "explanation": (
                        "Found {} matches (of {} required) for {}."
                    ).format(len(matches), required_matches, name)
                }
        else:
            if required_matches == 1:
                return {
                    "status": "failed",
                    "explanation": ("Did not find {}.").format(name)
                }
            else:
                return {
                    "status": "failed",
                    "explanation": (
                        "Found {} matches (of {} required) for {}."
                    ).format(len(matches), required_matches, name)
                }

    string_contains_re.__doc__ = """\
Returns "accomplished" if the value contains at least {}
matche(s) for the regular expression:

    {}

In the output, it is referred to as:

    {}
""".format(
    required_matches,
    repr(expression),
    name
)
    return string_contains_re


def build_approx_matcher(threshold=0.8, partial_threshold=0.6):
    """
    Returns a checker function that uses a difflib.SequenceMatcher to
    computer a difference ratio for the given values (should be strings)
    and compares it to the given threshold.
    """
    def approx_check(val, ref):
        """
        Uses a difflib.SequenceMatcher to compare two strings, and
        succeeds if their similarity is at least a certain threshold.
        """
        if not isinstance(val, str) or not isinstance(ref, str):
            raise TypeError("Value and reference value must both be strings.")

        ratio = difflib.SequenceMatcher(None, val, ref).ratio()

        if ratio >= threshold:
            status = "accomplished"
            status_desc = "similar enough"
            if ratio >= 0.9:
                status_desc = "almost identical"
            elif ratio == 1:
                status_desc = "exactly the same"
        elif ratio >= partial_threshold:
            status = "partial"
            status_desc = "somewhat similar"
        else:
            status = "failed"
            status_desc = "not the same"

        # TODO: NOT THIS HERE!
        explanation = (
            "Values were {}.<br>\n{}"
        ).format(
            status_desc,
            html_tools.html_diff_table(
                val,
                ref,
                joint_title="Values compared:"
            )
        )

        return {
            "status": status,
            "explanation": explanation
        }

    return approx_check


#-------------------------#
# Distribution comparison #
#-------------------------#

def result_distributions_have_same_keys(obs_dist, ref_dist):
    """
    Compares two result distribution dictionaries to ensure that they
    include the same set of keys, regardless of how common those keys
    are. Each dictionary should contain "trials" and "results" keys,
    where the "results" key maps different results to integer
    frequencies.
    """

    obs_res = obs_dist["results"]
    ref_res = ref_dist["results"]

    extra = set(obs_res) - set(ref_res)
    missing = set(ref_res) - set(obs_res)

    if extra or missing:
        return {
            "status": "failed",
            "explanation": html_tools.build_html_details(
                "Possibilities are different",
                "<ul>\n{}\n</ul>".format(
                    '\n'.join(
                        [
                            (
                                "<li>Observed result:\n<pre>{}</pre>"
                              + "\nnever occurred in reference"
                              + " distribution.</li>"
                            ).format(ext)
                            for ext in extra
                        ] + [
                            (
                                "<li>Expected result:\n<pre>{}</pre>"
                              + "\nnever occurred in observed"
                              + " distribution.</li>"
                            ).format(mis)
                            for mis in missing
                        ]
                    )
                )
            )
        }
    else:
        return {
            "status": "accomplished",
            "explanation": (
                "Observed distribution has the same set of possibilities"
              + " as the reference distribution."
            )
        }


def build_distribution_comparator(precision=2):
    """
    Returns a comparator function for result distributions, where
    fractions of the result in each distribution category are expected to
    agree after rounding to the given number of decimal places.
    """
    def result_distributions_are_similar(obs_dist, ref_dist):
        """
        Compares two result distribution dictionaries for statistical
        similarity. Each dictionary should contain "trials" and "results"
        keys, where the "results" key maps different results to integer
        frequencies.

        # TODO: Better statistical tests here...
        """

        obs_res = obs_dist["results"]
        ref_res = ref_dist["results"]

        extra = set(obs_res) - set(ref_res)
        missing = set(ref_res) - set(obs_res)

        if extra or missing:
            return {
                "status": "failed",
                "explanation": html_tools.build_html_details(
                    "Distributions are different",
                    "<ul>\n{}\n</ul>".format(
                        '\n'.join(
                            [
                                (
                                    "<li>Observed result:\n<pre>{}</pre>"
                                  + "\nnever occurred in reference"
                                  + " distribution.</li>"
                                ).format(ext)
                                for ext in extra
                            ] + [
                                (
                                    "<li>Expected result:\n<pre>{}</pre>"
                                  + "\nnever occurred in observed"
                                  + " distribution.</li>"
                                ).format(mis)
                                for mis in missing
                            ]
                        )
                    )
                )
            }

        disagree = []
        for key in sorted(obs_res):
            obs_fr = round(obs_res[key] / obs_dist["trials"], precision)
            ref_fr = round(ref_res[key] / ref_dist["trials"], precision)
            if obs_fr != ref_fr:
                disagree.append((key, obs_fr, ref_fr))

        if disagree:
            return {
                "status": "failed",
                "explanation": html_tools.build_html_details(
                    "Distributions were noticeably different",
                    "<ul>\n{}\n</ul>".format(
                        '\n'.join(
                            (
                                "<li>Result\n<pre>{}</pre>\n occurred"
                              + " about {}% of the time in the reference"
                              + " distribution but was observed about"
                              + " {}% of the time.</li>"
                            ).format(
                                key,
                                100 * ref_fr,
                                100 * obs_fr
                            )
                            for (key, obs_fr, ref_fr) in disagree
                        )
                    )
                )
            }
        else:
            return {
                "status": "accomplished",
                "explanation": (
                    "Distributions agreed to the required precision:<br>\n"
                  + str(ref_res) + " (ref)<br>\n"
                  + str(obs_res) + " (obs)"
                )
            }

    return result_distributions_are_similar


#-----------------------------------#
# Sequence and structure comparison #
#-----------------------------------#

_STUB_N = 0
_STUB_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_STUB_LEN = len(_STUB_CHARS)


def reset_stubs():
    """
    Resets the stub counter. Useful to ensure that equivalent data
    structures are equivalent when made hashable via equivalent stubs,
    although order really matters (i.e., recursive dictionaries with
    different key orders will not necessarily end up with the same
    stubs).
    """
    global _STUB_N
    _STUB_N = 0


def next_stub():
    """
    Generates a unique string to indicate the presence of a recursive
    structure encountered during make_hashable.
    """
    global _STUB_N
    n = _STUB_N
    _STUB_N += 1
    result = ""
    while n // _STUB_LEN > 0:
        result = _STUB_CHARS[n % _STUB_LEN] + result
        n //= _STUB_LEN
    result = _STUB_CHARS[n % _STUB_LEN] + result
    return "R&" + result


def make_hashable(dataStructure, memo=None):
    """
    Takes a data structure that may contain lists, tuples, dictionaries,
    and/or sets as well as strings, numbers, booleans, and Nones, and
    turns it into a similar structure using tuples in place of lists,
    sets, and dictionaries that can be hashed. Uses a ID-based memo to
    avoid re-processing recursive structures, with string stubs in place
    of already-visited objects.
    """
    if memo is None:
        reset_stubs()
        memo = {}

    # If this is a re-visit to a container object, return a stub string
    if (
        not isinstance(dataStructure, (int, float, str, bool))
    and id(dataStructure) in memo
    ):
        return memo[id(dataStructure)]

    # Save a stub string in case of a future re-visit
    memo[id(dataStructure)] = next_stub()

    if isinstance(dataStructure, (list, tuple)):
        return tuple([make_hashable(x, memo) for x in dataStructure])
    elif isinstance(dataStructure, set):
        # We sort sets so that ordering is irrelevant
        return tuple([make_hashable(x, memo) for x in sorted(dataStructure)])
    elif isinstance(dataStructure, dict):
        # We sort keys so that ordering is irrelevant
        return tuple(
            (key, make_hashable(dataStructure[key], memo))
            for key in sorted(dataStructure)
        )
    else:
        try:
            _ = hash(dataStructure)
        except TypeError as e:
            if "unhashable" in str(e):
                raise TypeError(
                    (
                        "Could not convert object of type {} to hashable"
                      + " equivalent:\n{}"
                    ).format(type(dataStructure), repr(dataStructure))
                )
            else:
                raise

        # If we get here it's fully hashable already
        return dataStructure


def longest_common_subsequence(
    seq1,
    seq2,
    start1=None, end1=None,
    start2=None, end2=None,
    matcher=lambda x, y: x == y,
    memo=None
):
    """
    Finds the longest common subsequence between the continuous
    subsequences of the two given sequences which start and end at the
    given start/end points for each sequence. Uses the memo (which should
    never be provided explicitly) to remember solutions to sub-problems
    and greatly speed up the results.

    The custom matcher function determines what counts as a match. If it
    returns a dictionary with a 'status' key, the two items are counted
    as matching only if that status value is exactly "accomplished".
    Otherwise, it should return a boolean, and any truthy return value
    will be counted as a match.

    The return value is actually a tuple of pairs of integer indices,
    where each pair contains one index from sequence 1 and the index of a
    matching item from sequence 2.

    If there are multiple different longest common subsequences, the one
    including the earliest items from sequence 1 is returned.
    """
    # Assign default start/end values if they're missing:
    if start1 is None:
        start1 = 0
    if end1 is None:
        end1 = len(seq1)
    if start2 is None:
        start2 = 0
    if end2 is None:
        end2 = len(seq2)

    # Create a new memo if this isn't a recursive call:
    if memo is None:
        memo = {}

    memo_key = (start1, end1, start2, end2)

    # If we've already solved this sub-problem return the stored solution
    if memo_key in memo:
        return memo[memo_key]

    # Recursive base case:
    if start1 == end1 or start2 == end2:
        result = () # no match -> an empty tuple
        memo[memo_key] = result
        return result
    else:
        # Look at first item from each (use it or lose it)
        item1 = seq1[start1]
        item2 = seq2[start2]

        match_test = matcher(item1, item2)
        # TODO: Some kind of handling for partial matches here?!?
        if isinstance(match_test, dict) and 'status' in match_test:
            match_test = match_test['status'] == 'accomplished'

        if match_test:
            # first items match: recurse and then add them to the results
            restMatches = longest_common_subsequence(
                seq1,
                seq2,
                start1 + 1, end1,
                start2 + 1, end2,
                matcher,
                memo
            )
            result = ((start1, start2),) + restMatches
            memo[memo_key] = result
            return result
        else:
            # first items don't match: check both possibilities (one or
            # the other won't be part of the overall match)
            case1Matches = longest_common_subsequence(
                seq1,
                seq2,
                start1 + 1, end1,
                start2, end2,
                matcher,
                memo
            )
            case2Matches = longest_common_subsequence(
                seq1,
                seq2,
                start1, end1,
                start2 + 1, end2,
                matcher,
                memo
            )
            if len(case1Matches) < len(case2Matches):
                # case 2 is longer
                memo[memo_key] = case2Matches
                return case2Matches
            else:
                # a tie gets biased towards earlier items from sequence 1
                memo[memo_key] = case1Matches
                return case1Matches


def diff_blocks(seq1, seq2, matcher=lambda x, y: x == y):
    """
    Returns a list of 3-element lists in the same format as
    difflib.SequenceMatcher's get_matching_blocks output: A list of
    [seq1-index, seq1-index, length] triples where each triple indicates
    that sequences 1 and 2 match starting at seq1-index in sequence 1 and
    seq2-index in sequence 2 and continuing for length items.

    The difference is that this method accepts an optional custom matcher
    function which is used to establish whether two items are equal or
    not. That matcher function may return a truthy value to indicate a
    match, or it could be a checker function which returns a dictionary
    containing a 'status' key, where the status being 'accomplished'
    indicates a match.
    """
    # Get longest common subsequence
    lcs = longest_common_subsequence(seq1, seq2, matcher=matcher)
    if len(lcs) == 0:
        return [] # no matches whatsoever...

    # Convert sequence of matched indices to a list of matching blocks

    # The first block is a length-1 block anchored at the first matching
    # indices
    blocks = [ [lcs[0][0], lcs[0][1], 1] ]

    # We go through all point matches and extend each block or create a
    # new block
    for i1, i2 in lcs[1:]:
        if (
            i1 == blocks[-1][0] + blocks[-1][2]
        and i2 == blocks[-1][1] + blocks[-1][2]
        ):
            blocks[-1][2] += 1 # block continues
        else:
            blocks.append([i1, i2, 1]) # new block starts

    return blocks


def correspondence_helper(
    pool1,
    pool2,
    indexset1,
    indexset2,
    lower_bound=0,
    matcher=lambda x, y: x == y,
    memo=None
):
    """
    Helper for best_correspondence that also takes frozen sets of live
    indices for each each pool so that memoization can be applied.

    The lower_bound argument allows it to abort early if it figures out
    that the upper bound for its match is smaller than that value.

    Returns a pool1 -> pool2 mapping.

    TODO: This function seems dangerously exponential in both time and
    memory... Can we do better? Should we do something else?
    """
    if memo is None:
        memo = {}

    if min(len(indexset1), len(indexset2)) < lower_bound:
        return None
        # special value indicating an aborted call; we don't memoize this.

    # Look up a result if we've got one
    memo_key = (indexset1, indexset2)
    if memo_key in memo:
        return memo[memo_key]

    # If either is exhausted, the result is an empty mapping:
    if len(indexset1) == 0 or len(indexset2) == 0:
        result = {}
        memo[memo_key] = result
        return result

    # Find all possible matches of the first available key in the first
    # pool:
    all_matches = []
    first_p1_index = next(indexset1.__iter__())
    first_p1_item = pool1[first_p1_index]
    for p2_index in indexset2:
        if matcher(first_p1_item, pool2[p2_index]): # it's a match
            all_matches.append(p2_index)

    # Now recurse for each possible match:
    best_so_far = None
    for p2_index in all_matches:
        sub_result = correspondence_helper(
            pool1,
            pool2,
            indexset1 - { first_p1_index },
            indexset2 - { p2_index },
            lower_bound=max(0, lower_bound - 1),
                # -1 because of the extra match we'll add to this result
            matcher=matcher,
            memo=memo
        )

        # Add match that we're assuming to this result
        full_result = { first_p1_index: p2_index }
        full_result.update(sub_result)

        # remember best so far
        if (
            sub_result is not None
        and (best_so_far is None or len(full_result) > len(best_so_far))
        ):
            # Remember this result
            best_so_far = full_result
            # Move our lower bound up if it can
            lower_bound = max(lower_bound, len(best_so_far))

    # One more possibility: that we find a better result by leaving
    # first_p1_index unmatched entirely (or it can't match)
    unmatch_result = correspondence_helper(
        pool1,
        pool2,
        indexset1 - { first_p1_index },
        indexset2,
        lower_bound=lower_bound, # same as
        matcher=matcher,
        memo=memo
    )

    # Update best_so_far:
    if (
        unmatch_result is not None
    and (best_so_far is None or len(unmatch_result) > len(best_so_far))
    ):
        best_so_far = unmatch_result
        # No need to update lower bound, as we're pretty much done
        # already

    # Turn any possible remaining None subresults into empty dictionaries
    if best_so_far is None:
        best_so_far = {}

    # Now we just return the best option that we found.
    memo[memo_key] = best_so_far
    return best_so_far


def best_correspondence(pool1, pool2, matcher=lambda x, y: x == y):
    """
    Finds the best pairing of elements from the two given pools (which
    aren't necessarily the same size) such that each pair satisfies the
    given matcher function (default is the items must be equal) and the
    total number of pairs is maximized. The order of items in each pool
    is irrelevant, but the pools must be indexable, because this function
    returns a dictionary that maps indices in pool1 to indices in pool2.
    """
    return correspondence_helper(
        pool1,
        pool2,
        frozenset(range(len(pool1))),
        frozenset(range(len(pool2))),
        matcher=matcher
    )


def sequence_diff(
    val,
    ref,
    order_matters=False,
    item_matcher=lambda x, y: x == y
):
    """
    Returns a tuple of three lists: a list of matching items, a list of
    missing items that are present in the reference sequence but not the
    value sequence, and a list of extra items that are present in the
    value sequence but not the reference sequence. If order_matters is
    given as True, some items may be listed as both "missing" and "extra"
    if they appear out-of-order in the value sequence.

    The item_matcher is used to determine what counts as a match, if it
    returns a truthy value, two items will be matched. However, it may
    also be a checker-style function that returns a dictionary with a
    'status' key, in which case a status value of 'accomplished' will
    count as a match and any other value will not.

    TODO: Actually respect "partial" as an item_matcher result!
    """
    # TODO: NOT THIS HACK!
    if order_matters is False:
        try:
            val = sorted(val)
            ref = sorted(ref)
            order_matters = True
        except Exception:
            pass

    vhashables = [make_hashable(x) for x in val]
    rhashables = [make_hashable(x) for x in ref]

    if order_matters:
        matching, missing, extra = [], [], []

        blocks = diff_blocks(vhashables, rhashables, matcher=item_matcher)

        # Convert blocks into matching/missing/extra format
        last_vidx = 0
        last_ridx = 0
        for vidx, ridx, blen in blocks:
            matching.extend(val[idx] for idx in range(vidx, vidx + blen))
            missing.extend(ref[idx] for idx in range(last_ridx, ridx))
            extra.extend(val[idx] for idx in range(last_vidx, vidx))

            last_vidx = vidx + blen
            last_ridx = ridx + blen

        # Catch extra missing/extra values (blocks might be empty)
        if last_vidx < len(val):
            extra.extend(val[idx] for idx in range(last_vidx, len(val)))
        if last_ridx < len(ref):
            missing.extend(ref[idx] for idx in range(last_ridx, len(ref)))

    else:
        # Find the best unordered correspondence between the hashable
        # versions of the values and reference items.

        # TODO: Safety value for values that are much longer than
        # expected?
        correspondence = best_correspondence(
            vhashables,
            rhashables,
            matcher=item_matcher
        )
        matched_indices = set(correspondence.values())

        # Slower than sets but preserves ordering in each list
        matching = [
            list(val)[idx]
            for idx in correspondence
        ]
        missing = [
            list(ref)[idx]
            for idx in range(len(ref))
            if idx not in matched_indices
        ]
        extra = [
            list(val)[idx]
            for idx in range(len(val))
            if idx not in correspondence
        ]

    return matching, missing, extra


def make_structure_comparator(
    tolerance="auto",
    order_matters=False,
    item_matcher=lambda x, y: x == y,
    item_repr=html_tools.dynamic_html_repr,
    key_repr=None,
    include_full_results=True
):
    """
    Creates a comparator that looks at two data structures (composed of
    lists, tuples, dictionaries, and/or sets) and reports on their
    differences. If the tolerance is left at the default (the string
    'auto'), a partial success will be returned if only a few items
    are different at the top level of the given data structure. It may be
    given as 0, in which case only full success or failure will result.
    If it is a number other than 0, that many total missing + extra items
    will be tolerated, if it is not a number or the string "auto", it
    must be a function which will be given the reference value being
    compared to and which should return a number of different items to be
    tolerated.

    If the order of the given sequence matters, set order_matters to
    True (only apply this to sets and dictionaries if you expect them to
    be ordered).

    A custom item_matcher may be provided, in which case it will be
    applied to pairs of items from the two lists, tuples, or sets being
    compared to decide which are equal. Normally, any truthy value will
    count as a match, but if the return value from the item_matcher is a
    dictionary which contains a 'status' key, the match will only be
    counted if the status value is 'accomplished', which allows the use
    of checker-style functions as item matchers.

    TODO: Would be nice to support partial matching at the item level,
    but that's hard!

    When an item_matcher is provided for comparing dictionaries, it will
    be applied to key/value pairs (i.e., it will be given two arguments
    which are both tuples, not four arguments). Sometimes the values will
    be None during the first phase when only keys are being compared.

    A custom item_repr function may be provided to be used to generate
    item representations in explanations where lists of
    missing/extra/moved items appear. A custom key_repr may also be
    provided for representing dictionary keys; if left out it defaults to
    the same thing as item_repr (which itself defaults to `repr`).

    Both of these custom repr functions should be able to accept one
    argument: the thing to be represented.

    If attempts to compare or list full results are not desired,
    include_full_results may be given as False.
    """
    if tolerance == "auto":
        tolerance_fcn = lambda ref: min(len(ref) // 5, 3 + len(ref) // 50)
    elif isinstance(tolerance, (int, float)):
        tolerance_fcn = lambda ref: tolerance
    else:
        tolerance_fcn = tolerance

    if key_repr is None:
        key_repr = item_repr

    def compare_structures(val, ref):
        """
        Comparator for structured data (lists, tuples, sets, and/or
        dictionaries) according to the arguments given to
        make_structure_comparator.
        """
        if not isinstance(ref, (list, tuple, set, dict)):
            raise TypeError(
                "Reference value for compare_structures must"
              + " be a list, tuple, set, or dictionary."
            )
        elif type(val) != type(ref):
            return {
                "status": "failed",
                "explanation": (
                    "Your result was a {} but should have been a {}."
                ).format(type(val).__name__, type(ref).__name__)
            }

        # Define our tolerance value
        tolerance = tolerance_fcn(ref)

        if isinstance(val, dict):
            kmatch, kmiss, kext = sequence_diff(
                val.keys(),
                ref.keys(),
                # order doens't matter for dict keys...
                # TODO: What if it's a subclass though...?
                item_matcher=lambda k1, k2: (
                    item_matcher((k1, None), (k2, None))
                )
            )
            wrong = len(kmiss) + len(kext)
            if wrong > 0:
                if wrong > tolerance:
                    status = "failed"
                    expl = (
                        "Your result has the wrong keys (out of {},"
                      + " {} matched).<br>\n"
                    ).format(
                        phrasing.obj_num(len(ref), "expected key"),
                        len(kmatch)
                    )
                else:
                    status = "partial"
                    expl = (
                        "Your result has some incorrect keys (out of {},"
                      + " {} matched).<br>\n"
                    ).format(
                        phrasing.obj_num(len(ref), "expected key"),
                        len(kmatch)
                    )
                if kmiss:
                    expl += html_tools.build_html_details(
                        "Missing keys:",
                        html_tools.build_list(key_repr(x) for x in kmiss)
                    )
                if kext:
                    expl += html_tools.build_html_details(
                        "Extra keys:",
                        html_tools.build_list(key_repr(x) for x in kext)
                    )

                if include_full_results:
                    expl += html_tools.html_diff_table(
                        html_tools.truncate(
                            html_tools.big_repr(val),
                            limit=5000
                        ),
                        html_tools.truncate(
                            html_tools.big_repr(ref),
                            limit=5000
                        ),
                        "Full result",
                        "Expected result",
                        "Detailed differences:"
                    )
                return { "status": status, "explanation": expl }

            # otherwise, we can check values

            imatch, imiss, iext = sequence_diff(
                list(val.items()),
                list(ref.items()),
                order_matters=order_matters,
                item_matcher=item_matcher
            )

            if order_matters:
                # Find items that moved
                imoved = []
                imoved_missing = []
                imoved_extra = []
                for midx, miss in enumerate(imiss):
                    if miss in iext:
                        eidx = iext.index(miss)
                        imoved_missing.append(midx)
                        imoved_extra.append(eidx)
                        imoved.append(miss)

                imiss = [
                    imiss[idx]
                    for idx in range(len(imiss))
                    if idx not in imoved_missing
                ]

                iext = [
                    iext[idx]
                    for idx in range(len(iext))
                    if idx not in imoved_extra
                ]

            else: # order doesn't matter
                imoved = []

            wrong = len(imiss) + len(iext) + len(imoved)
            if wrong > 0:
                if wrong > tolerance:
                    status = "failed"
                    expl = (
                        "Your result has the right keys but some values"
                      + " are wrong (out of {}, {} matched)."
                    ).format(
                        phrasing.obj_num(len(ref), "expected value"),
                        len(imatch)
                    )
                else:
                    status = "partial"
                    expl = (
                        "Your result has the right keys but a few values"
                      + " are wrong (out of {}, {} matched)."
                    ).format(
                        phrasing.obj_num(len(ref), "expected value"),
                        len(imatch)
                    )
                if imiss:
                    expl += html_tools.build_html_details(
                        "Missing values (by key):",
                        html_tools.build_list(
                            key_repr(k) + ": " + item_repr(v)
                            for (k, v) in imiss
                        )
                    )
                if iext:
                    expl += html_tools.build_html_details(
                        "Extra values (by key):",
                        html_tools.build_list(
                            key_repr(k) + ": " + item_repr(v)
                            for (k, v) in iext
                        )
                    )
                if imoved:
                    expl += html_tools.build_html_details(
                        "Out-of-order values (by key):",
                        html_tools.build_list(
                            key_repr(k) + ": " + item_repr(v)
                            for (k, v) in imoved
                        )
                    )
                if include_full_results:
                    expl += html_tools.html_diff_table(
                        html_tools.truncate(
                            html_tools.big_repr(val),
                            limit=5000
                        ),
                        html_tools.truncate(
                            html_tools.big_repr(ref),
                            limit=5000
                        ),
                        "Full result",
                        "Expected result",
                        "Detailed differences:"
                    )

                return { "status": status, "explanation": expl }
            else:
                if include_full_results:
                    results = "<br>\n" + html_tools.build_html_details(
                        "Your result:",
                        html_tools.dynamic_html_repr(val)
                    )
                else:
                    results = ""

                return {
                    "status": "accomplished",
                    "explanation": (
                        "Your result has the correct keys and values ({}"
                      + " matched).{}"
                    ).format(
                        phrasing.obj_num(len(imatch), "item"),
                        results
                    )
                }

        else: # anything other than a dictionary
            matching, missing, extra = sequence_diff(
                val,
                ref,
                order_matters=order_matters,
                item_matcher=item_matcher
            )

            if order_matters:
                # Find items that moved
                moved = []
                moved_missing = []
                moved_extra = []
                for midx, miss in enumerate(missing):
                    for eidx, xtra in enumerate(extra):
                        if item_matcher(miss, xtra):
                            # TODO: What if multiple copies are out-of-order?
                            moved_missing.append(midx)
                            moved_extra.append(eidx)
                            moved.append(miss)
                            break

                new_missing = [
                    missing[idx]
                    for idx in range(len(missing))
                    if idx not in moved_missing
                ]
                missing = new_missing

                new_extra = [
                    extra[idx]
                    for idx in range(len(extra))
                    if idx not in moved_extra
                ]
                extra = new_extra

            else: # order doesn't matter
                moved = []

            wrong = len(missing) + len(extra) + len(moved)
            if wrong > 0:
                if wrong > tolerance:
                    status = "failed"
                    expl = (
                        "Your result has the wrong values (out of {},"
                      + " {} matched)."
                    ).format(
                        phrasing.obj_num(len(ref), "expected value"),
                        phrasing.obj_num(len(matching), "value")
                    )
                else:
                    status = "partial"
                    expl = (
                        "Your result is mostly correct but some values"
                      + " are wrong (out of {}, {} matched)."
                    ).format(
                        phrasing.obj_num(len(ref), "expected value"),
                        phrasing.obj_num(len(matching), "value")
                    )
                # TODO: better management of small differences in large
                # structures here!
                if missing:
                    expl += html_tools.build_html_details(
                        "Missing values:",
                        html_tools.build_list(
                            item_repr(x) for x in missing
                        )
                    )
                if extra:
                    expl += html_tools.build_html_details(
                        "Extra values:",
                        html_tools.build_list(
                            item_repr(x) for x in extra
                        )
                    )
                if moved:
                    expl += html_tools.build_html_details(
                        "Out-of-order values:",
                        html_tools.build_list(
                            item_repr(x) for x in moved
                        )
                    )
                if include_full_results:
                    # TODO: We'd like scrollable full-content diffs here,
                    # but... that's a Project.
                    expl += html_tools.html_diff_table(
                        html_tools.truncate(
                            html_tools.big_repr(val),
                            limit=5000
                        ),
                        html_tools.truncate(
                            html_tools.big_repr(ref),
                            limit=5000
                        ),
                        "Full result",
                        "Expected result",
                        "Detailed differences:"
                    )
                return { "status": status, "explanation": expl }
            else:
                if include_full_results:
                    results = "<br>\n" + html_tools.build_html_details(
                        "Your result:",
                        html_tools.dynamic_html_repr(val)
                    )
                else:
                    results = ""
                return {
                    "status": "accomplished",
                    "explanation": (
                        "Your result has the correct values ({}"
                      + " matched).{}"
                    ).format(
                        phrasing.obj_num(len(matching), "value"),
                        results
                    )
                }

    return compare_structures


#------------------#
# Image comparison #
#------------------#

def diff_anim_frames(val, ref, steps=10):
    """
    Creates and returns a list of PIL.Image objects representing
    animation frames that fade between the two given images. A custom
    number of fade steps may be provided, which specifies the number of
    intermediate frames, so the result will have that many frames plus
    two. The fade is linear.
    """
    import PIL.Image # we import here and let a potential error bubble out
    # TODO: Draw label text on anim frames!

    result = [val]
    for step in range(1, steps + 1):
        t = step / (steps + 1)
        result.append(PIL.Image.blend(val, ref, t))
    result.append(ref)
    return result


def make_image_comparator(
    allowed_differences=0.03,
    partial_allowed=0.5,
    similarity_threshold=15
):
    """
    Returns a comparison function suitable for use with 'image' context
    slots. It checks pixels in the two images (which it checks are
    actually images and are the same size) and returns a status of
    accomplished if the fraction of the area of the image in which pixels
    differ is less than or equal to the given allowed fraction. Pixels
    which have a 255-basis-RGB-space Euclidean distance (TODO: better
    distance metric) below the given similarity threshold are counted as
    1/2 of a pixel difference instead of a full pixel difference. (TODO:
    Better controls for this?). A partially-complete result is returned
    as long as the fractional area of different pixels is no more than
    the given partial_allowed value.
    """
    import PIL.Image # we import here and let a potential error bubble out

    def compare_images(val, ref):
        """
        Compares two PILlow images, ensuring that the total percentage of
        pixels which differ between the two images is below a threshold.
        Pixels which differ only slightly will count as 1/2 a pixel in
        terms of the area difference computation. Images of different
        sizes will always be treated as totally different (TODO: More
        nuance there?).
        """
        if not isinstance(ref, PIL.Image.Image):
            raise TypeError(
                f"Reference image capture failed (got a {type(ref)},"
                f" not a PIL.Image)"
            )
        if not isinstance(val, PIL.Image.Image):
            return {
                "status": "failed",
                "explanation": (
                    f"Image capture failed (got a {type(val)}, not an"
                    f" image)."
                )
            }

        if val.size != ref.size:
            return {
                "status": "failed",
                "explanation": (
                    f"Your image ({val.width}x{val.height}) did not"
                    f" have the same size as the solution image"
                    f" ({ref.width}x{ref.height})."
                )
            }

        # Should be 0-255 RGB data
        # TODO: Verify mode
        val_pixels = val.getdata()
        ref_pixels = ref.getdata()
        diff_area = 0
        half_diff_area = 0
        for index in range(len(val_pixels)):
            px = val_pixels[index]
            ref_px = ref_pixels[index]
            dist = sum((px[i] - ref_px[i])**2 for i in range(3))**0.5
            if 0 < dist <= similarity_threshold:
                half_diff_area += 1
            elif similarity_threshold < dist:
                diff_area += 1

        # Build an HTML image comparison
        comparison = html_tools.build_html_tabs(
            [
                # TODO: Proper alt text here!
                (
                    "Your image:",
                    html_tools.html_image(val, "Your image")
                ),
                (
                    "Solution image:",
                    html_tools.html_image(ref, "Solution image")
                ),
                (
                    "Animation:",
                    html_tools.html_animation(
                        diff_anim_frames(val, ref, 10),
                        (
                            "An animation between your image and the"
                            " solution image."
                        ),
                        delays=[500] + [100] * 10 + [500]
                    )
                )
            ]
        )

        # Return a status based on the difference fraction
        diff_fraction = diff_area / len(val_pixels)
        half_diff_fraction = half_diff_area / len(val_pixels)
        diff_score = diff_fraction + half_diff_fraction / 2

        diff_msg = (
            f"{diff_fraction * 100:.1f}% of pixels were"
            f" different"
        )
        if half_diff_fraction > 0:
            diff_msg += (
                f" and {half_diff_fraction * 100:.1f}% of pixels were"
                f" somewhat different"
            )

        if diff_score == 0:
            return {
                "status": "accomplished",
                "explanation": (
                    f"Your image and the solution image were exactly the"
                    f" same: {comparison}"
                )
            }
        elif diff_score <= allowed_differences:
            return {
                "status": "accomplished",
                "explanation": (
                    f"Your image and the solution image were almost the"
                    f" same ({diff_msg}): {comparison}"
                )
            }
        elif diff_score <= partial_allowed:
            return {
                "status": "partial",
                "explanation": (
                    f"Your image and the solution image were similar,"
                    f" but not the same ({diff_msg}): {comparison}"
                )
            }
        else:
            return {
                "status": "failed",
                "explanation": (
                    f"Your image and the solution image were not the"
                    f" same ({diff_msg}): {comparison}"
                )
            }

    return compare_images


#---------------------------#
# One-size-fits-all default #
#---------------------------#

LONG_STRING_LINES = 3
"""
Threshold in terms of newlines before we treat a string as long.
"""

LONG_STRING_LEN = 120
"""
Threshold in terms of raw characters even without any newlines before we
treat a string as long.
"""


def omni_compare(val, ref, memo=None):
    """
    A one-size-kinda-fits-all comparison method (although note that it
    assumes order matters in lists and tuples).

    Tries its best to give a concise-ish description of differences when
    they exist.
    """
    if memo is None:
        memo = {}

    vid = id(val)
    rid = id(ref)
    if vid in memo and rid in memo[vid]:
        return True
        # Recursive comparison that's already in-progress

    memo.setdefault(vid, set()).add(rid)

    # TODO: Better/safer here!
    try:
        matched = val == ref
    except RecursionError:
        matched = False # might be, but we'll have to check further

    if matched:
        return {
            "status": "accomplished",
            "explanation": (
                f"Actual value is the same as the reference"
                f" value.<br>\n{html_tools.dynamic_html_repr(val)}"
            )
        }
    else: # let's hunt for differences
        if isinstance(val, bool) and isinstance(ref, bool):
            # Bools are isinstance of int so we need this case before the
            # one below
            return {
                "status": "failed",
                "explanation": (
                    f"Your result ({val}) was the opposite of the"
                    f" expected result ({ref})."
                )
            }
        elif (
            isinstance(val, (int, float, complex))
        and isinstance(ref, (int, float, complex))
        ): # what if they're both numbers?
            ncomp = numbers_are_equalish(val, ref)
            if ncomp["status"] == "accomplished": # close-enough numbers
                return ncomp
            else: # not close-enough
                return {
                    "status": "failed",
                    "explanation": (
                        f"Your result ({val}) and the expected"
                        f" result ({ref}) are consequentially"
                        f" different numbers."
                    )
                }
        elif type(val) != type(ref): # different types; not both numbers
            vt = html_tools.escape(str(type(val).__name__))
            rt = html_tools.escape(str(type(ref).__name__))
            return {
                "status": "failed",
                "explanation": (
                    f"Your result was {phrasing.a_an(vt)},"
                    f" but the correct result was"
                    f" {phrasing.a_an(rt)}."
                )
            }
        elif isinstance(val, str): # both strings
            val_lines = val.splitlines()
            ref_lines = ref.splitlines()
            if (
                max(len(val_lines), len(ref_lines)) >= LONG_STRING_LINES
             or max(len(val), len(ref)) >= LONG_STRING_LEN
            ): # longish strings so there should be some tolerance
                return very_fuzzy_string_compare(
                    val,
                    ref,
                    line_match_threshold=1.0,
                    sequence_match_threshold=1.0,
                    partial_sequence_threshold=0.5
                ) # partial success only unless equal
            else: # shorter strings so very little tolerance
                close = strings_are_equal_modulo_most_whitespace(val, ref)
                diff_table = html_tools.html_diff_table(
                    val_lines,
                    ref_lines,
                    "Actual output",
                    "Corresponding lines (if any) in expected output"
                )
                if close["status"] == "accomplished":
                    return {
                        "status": "partial",
                        "explanation": (
                            f"Strings aren't the same, but they're"
                            f" close:<br>\n{diff_table}"
                        )
                    }
                else:
                    return {
                        "status": "failed",
                        "explanation": (
                            f"Actual value is different from the"
                            f" reference value:<br>\n{diff_table}"
                        )
                    }

        elif isinstance(val, (list, tuple)): # same-type sequences
            # TODO: Less inefficient here!
            # TODO: More detailed explication of deep differences here?
            return make_structure_comparator(
                order_matters=True,
                item_matcher=lambda val, ref: omni_compare(val, ref, memo)
            )(val, ref)
        elif isinstance(val, (set, dict)): # both sets or dicts
            # TODO: Less inefficient here!
            # TODO: More detailed explication of deep differences here?
            return make_structure_comparator(
                order_matters=True,
                item_matcher=lambda val, ref: omni_compare(val, ref, memo)
            )(val, ref)
        else: # not sure what kind of thing this is...
            return {
                "status": "failed",
                "explanation": (
                    f"Your value ({html_tools.dynamic_html_repr(val)})"
                    f" and the reference value"
                    f" ({html_tools.dynamic_html_repr(ref)}) are not"
                    f" the same."
                )
            }
