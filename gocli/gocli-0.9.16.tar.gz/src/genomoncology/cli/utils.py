from datetime import datetime as dt


# prints a user friendly error message if the dob is not formatted properly
def check_dob_format(dob):
    try:
        if dob is not None:
            dt.strptime(dob, "%Y-%m-%d")
    except ValueError as error:
        error.args = (
            "The date `{0}` does not match the format YYYY-MM-DD".format(dob),
        )
        raise


def filter_del_lines_from_load_annotations(call):
    return call.get("alt", "") != "<DEL>"
