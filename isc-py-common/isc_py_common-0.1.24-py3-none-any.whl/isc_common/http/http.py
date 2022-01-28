from datetime import datetime


def str2Date(date_str):
    if date_str is None:
        return None
    else:
        return datetime.strptime(date_str, '%Y-%m-%dT%I:%M:%S.%fZ').date()


def str2Date4Django(date_str):
    if date_str is None:
        return None
    else:
        date = str2Date(date_str)
        if (date.month < 10):
            month = f"0{date.month}"
        else:
            month = date.month

        if (date.day < 10):
            day = f"0{date.day}"
        else:
            day = date.day

        return f"{date.year}-{month}-{day}"
