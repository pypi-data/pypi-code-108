"""Text helper for drama helper"""


def check_line_break_string(text2check):
    """Because command line strings often escape
    the '\\' character, this is tested here.

    Args:
      text2check (str):  String to be checked.

    Returns:
      string: Checked String were command line
      escaped line breaks are replaced by line breaks.
    """
    if text2check.find("\\n"):
        print("Line break seems to be \\n instead of \n. Is corrected now.")
    return text2check.replace("\\n", "\n")
