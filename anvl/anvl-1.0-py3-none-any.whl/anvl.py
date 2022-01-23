from pathlib import Path
import re
from textwrap import wrap

# This is free and unencumbered software released into the public domain
# under the terms of the Unlicense: https://unlicense.org/

def load(anvl: str | Path) -> list[dict[str, str]]:
    """Load an ANVL file. Returns ANVL records as a list of dictionaries.
    
    Parameters:
    -----------
    anvl : str | Path
        A string or Path object representing the ANVL file.
    Returns:
    --------
    list[dict[str, str]]
    """
    with open(anvl, "r", encoding="utf8") as fh:
        return decode(fh)


def loads(anvl: str) -> list[dict[str, str]]:
    """Load an ANVL string. Returns ANVL records as a list of dictionaries.
    
    Parameters:
    -----------
    anvl : str
        A string representing the ANVL record(s).
    Returns:
    --------
    list[dict[str, str]]
    """
    return decode(anvl.split("\n"))


def dump(
    dicts: list[dict],
    anvl_file: str | Path,
    width: int = 80,
    indent: str = "\t",
    line_end: str = "\r\n",
):
    """Serializes a list of dictionaries to an ANVL file.
    
    Parameters:
    -----------
    dicts : list[dict]
        A list of flat dictionaries to serialize.
    anvl_file: str | Path
        A string or Path object representing the ANVL file.
    width: int
        The maximum number of characters per line. Default is 80 characters.
    indent: str
        The indentation to use when wrapping long lines. Default is "\t".
    line_end: str
        Line ending to us in ANVL file. Default is "\r\n".
    Returns:
    --------
    None
    """
    anvl = encode(dicts, width, indent, line_end)
    with open(anvl_file, "w", encoding="utf8", newline="") as fh:
        fh.write(anvl)


def dumps(
    dicts: list[dict], width: int = 80, indent: str = "\t", line_end: str = "\r\n"
) -> str:
    """Serializes a list of dictionaries to an ANVL string.
    
    Parameters:
    -----------
    dicts : list[dict]
        A list of flat dictionaries to serialize.
    width: int
        The maximum number of characters per line. Default is 80 characters.
    indent: str
        The indentation to use when wrapping long lines. Default is "\t".
    line_end: str
        Line ending to us in ANVL file. Default is "\r\n".
    Returns:
    --------
    str
    """
    return encode(dicts, width, indent, line_end)


def decode(lines: list[str]) -> list[dict[str, str]]:
    """[summary]

    Parameters:
    -----------
        lines: list[str]
            A list of strings representing lines of a set of ANVL records.

    Returns:
    --------
        list[dict[str, str]]
    """
    records = []
    indented = re.compile(r"^\s+\S")
    current_record = {}

    for line in lines:
        # If the line starts with "#" it is a comment and can be  ignored
        if line.startswith("#"):
            continue
        # If the line contains a ":", treat it as a key-value pair
        elif ":" in line:
            # Split only the first colon, to allow URLs as values
            k, v = line.split(":", 1)
            current_record[k.strip()] = v.strip()
        # If the line begins with any indentation, append it to the value of
        # the most recent key-value pair
        elif re.match(indented, line):
            last_key = list(current_record.keys())[-1]
            current_record[last_key] = " ".join(
                [current_record[last_key], line.strip()]
            )
        # If a line is blank, we've reached the end of a record. Add the record
        # to the list and start anew.
        elif line.strip() == "":
            # Only add a record to the records list if it's not empty. This
            # skips multiple blank lines in poorly-formated files.
            if len(current_record) > 0:
                records.append(dict(current_record))
                current_record = {}

    # ANVL files should end with a single blank line. If the terminal blank
    # line is left out, the loop above won't add the final record to the
    # records list. Do a check here for one last record, and add it if found.
    if len(current_record) > 0:
        records.append(current_record)

    return records


def encode(
    
    dicts: list[dict], width: int = 80, indent: str = "\t", line_end: str = "\r\n"
) -> str:
    """Serializes a list of dictionaries to an ANVL string.
    
    Parameters:
    -----------
    dicts : list[dict]
        A list of flat dictionaries to serialize.
    width: int
        The maximum number of characters per line. Default is 80 characters.
    indent: str
        The indentation to use when wrapping long lines. Default is "\t".
    line_end: str
        Line ending to us in ANVL file. Default is "\r\n".
    Returns:
    --------
    str
    """
    anvl_rows = []
    for d in dicts:
        for k, v in d.items():
            row = f"{str(k)}: {str(v)}"
            if len(row) <= width:
                anvl_rows.append(row)
            else:
                anvl_rows.append(
                    line_end.join(wrap(row, width=width, subsequent_indent=indent))
                )
        anvl_rows.append("")

    return line_end.join(anvl_rows)
