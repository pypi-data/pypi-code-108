# -*- coding: utf-8 -*-

# Strandard library imports
import os
import shutil
import sys
import gzip
import warnings
import time
import random
from collections import OrderedDict, namedtuple, defaultdict, Counter
from subprocess import Popen, PIPE
import bisect
import itertools
import zipfile
import tempfile
import glob
import re
from datetime import date

# Third party imports
import pandas as pd
import pysam as ps
from tqdm import tqdm, trange
import numpy as np
from IPython.core.display import Image, display, HTML
from matplotlib import pyplot as pl

##~~~~~~~ JUPYTER NOTEBOOK SPECIFIC TOOLS ~~~~~~~#


def jhelp(function, full=True, print_private=False, **kwargs):
    """
    Print a nice looking help string based on the name of a declared function. By default print the function
    definition and description
    * function
        Name of a declared function or class method
    * full
        If True, the help string will included a description of all arguments
    """
    # For some reason signature is not aways importable. In these cases the build-in help in invoqued
    try:
        from IPython.core.display import display, HTML, Markdown
        from inspect import signature, isfunction, ismethod
    except (NameError, ImportError) as E:
        warnings.warn(
            "jupyter notebook is required to use this function. Please verify your dependencies"
        )
        help(function)
        return

    if isfunction(function) or ismethod(function):
        # skip private functions
        if not print_private and function.__name__.startswith("_"):
            return
        if full:
            jprint(
                "<b>{}</b> {}\n{}".format(
                    function.__name__, signature(function), function.__doc__
                )
            )
        else:
            jprint("<b>{}</b> {}".format(function.__name__, signature(function)))


def stdout_print(*args):
    """
    Emulate print but uses sys stdout instead. It could sometimes be useful in specific situations where print
    is in is not behaving optimaly (like with tqdm for example)
    """
    cprint(args)


def cprint(*args, **kwargs):
    """
    Emulate print + colored output using color argument. Also used sys.stdout to
    avoid string buffering with print.
    Available colors: white, grey, red, green, yellow, blue, pink, purple, beige
    """
    color_codes = {
        "white": 29,
        "grey": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "pink": 35,
        "purple": 36,
        "beige": 37,
    }
    s = " ".join([str(i) for i in args])
    color = kwargs.get("color", "white")
    color_code = color_codes.get(color, 29)
    s = "\x1b[{}m{}\x1b[0m\n".format(color_code, s)
    sys.stdout.write(s)
    sys.stdout.flush()


def jprint(*args, **kwargs):
    """
    FOR JUPYTER NOTEBOOK ONLY
    Format a string in HTML and print the output. Equivalent of print, but
    highly customizable. Many options can be passed to the function.
    * *args
        One or several objects that can be cast in str
    * **kwargs
        Formatting options to tweak the html rendering
        Boolean options : bold, italic, highlight, underlined, striked, subscripted, superscripted
        String oprions: font, color, size, align, background_color, line_height
    """
    # Function specific third party import
    try:
        from IPython.core.display import display, HTML
    except (NameError, ImportError) as E:
        warnings.warn(
            "jupyter notebook is required to use this function. Please verify your dependencies"
        )
        print(args)
        return

    # Join the different elements together and cast in string
    s = " ".join([str(i) for i in args])

    # Replace new lines and tab by their html equivalent
    s = s.replace("\n", "<br>").replace("\t", "&emsp;")

    # For boolean options
    if "bold" in kwargs and kwargs["bold"]:
        s = "<b>{}</b>".format(s)
    if "italic" in kwargs and kwargs["italic"]:
        s = "<i>{}</i>".format(s)
    if "highlight" in kwargs and kwargs["highlight"]:
        s = "<mark>{}</mark>".format(s)
    if "underlined" in kwargs and kwargs["underlined"]:
        s = "<ins>{}</ins>".format(s)
    if "striked" in kwargs and kwargs["striked"]:
        s = "<del>{}</del>".format(s)
    if "subscripted" in kwargs and kwargs["subscripted"]:
        s = "<sub>{}</sub>".format(s)
    if "superscripted" in kwargs and kwargs["superscripted"]:
        s = "<sup>{}</sup>".format(s)

    # for style options
    style = ""
    if "font" in kwargs and kwargs["font"]:
        style += "font-family:{};".format(kwargs["font"])
    if "color" in kwargs and kwargs["color"]:
        style += "color:{};".format(kwargs["color"])
    if "size" in kwargs and kwargs["size"]:
        style += "font-size:{}%;".format(kwargs["size"])
    if "align" in kwargs and kwargs["align"]:
        style += "text-align:{};".format(kwargs["align"])
    if "background_color" in kwargs and kwargs["background_color"]:
        style += "background-color:{};".format(kwargs["background_color"])
    if "line_height" in kwargs and kwargs["line_height"]:
        line_height = kwargs["line_height"]
    else:
        line_height = 15
    style += "line-height:{}px;".format(line_height)

    # Format final string
    if style:
        s = '<p style="{}">{}</p>'.format(style, s)
    else:
        s = "<p>{}</p>".format(s)

    display(HTML(s))


def toogle_code(**kwargs):
    """
    FOR JUPYTER NOTEBOOK ONLY
    Hide code with a clickable link in a jupyter notebook
    """
    # Function specific third party import
    try:
        from IPython.core.display import display, HTML
    except (NameError, ImportError) as E:
        warnings.warn(
            "jupyter notebook is required to use this function. Please verify your dependencies"
        )
        return

    display(
        HTML(
            """<script>
    code_show=true;
    function code_toggle() {
     if (code_show){
     $('div.input').hide();
     } else {
     $('div.input').show();
     }
     code_show = !code_show
    }
    $( document ).ready(code_toggle);
    </script>
    <b><a href="javascript:code_toggle()">Toggle on/off the raw code</a></b>"""
        )
    )


def init_notebook(
    author="author",
    creation_date="XXXX/XX/XX",
    color="blue",
):
    """
    Display a basic initialization message for Jupyter notebooks
    """
    cprint(author, color=color)
    cprint(f"Starting date : {creation_date}", color=color)
    cprint(
        "Last modification date : {}/{:02}/{:02}".format(
            date.today().year, date.today().month, date.today().day
        ),
        color=color,
    )


# ~~~~~~~ PREDICATES ~~~~~~~#


def is_readable_file(fp, raise_exception=True, **kwargs):
    """
    Verify the readability of a file or list of file
    """
    if not os.access(fp, os.R_OK):
        if raise_exception:
            raise IOError("{} is not a valid file".format(fp))
        else:
            return False
    else:
        return True


def is_gziped(fp, **kwargs):
    """
    Return True if the file is Gziped else False
    """
    return fp[-2:].lower() == "gz"


def has_extension(fp, ext, pos=-1, raise_exception=False, **kwargs):
    """
    Test presence of extension in a file path
    * ext
        Single extension name or list of extension names  without dot. Example ["gz, "fa"]
    * pos
        Postition of the extension in the file path. -1 for the last, -2 for the penultimate and so on [DEFAULT -1 = Last position]
    """
    # Cast in list
    if type(ext) == str:
        ext = [ext]
    # Test ext presence
    if not fp.split(".")[pos].lower() in ext:
        if raise_exception:
            raise ValueError(
                "Invalid extension for file {}. Valid extensions: {}".format(
                    fp, "/".join(ext)
                )
            )
        else:
            return False
    else:
        return True


# ~~~~~~~ PATH MANIPULATION ~~~~~~~#


def file_basename(fp, **kwargs):
    """
    Return the basename of a file without folder location and extension
    """
    return fp.rpartition("/")[2].partition(".")[0]


def extensions(fp, comp_ext_list=["gz", "tgz", "zip", "xz", "bz2"], **kwargs):
    """
    Return The extension of a file in lower-case. If archived file ("gz", "tgz", "zip", "xz", "bz2")
    the method will output the base extension + the archive extension as a string
    """
    split_name = fp.split("/")[-1].split(".")
    # No extension ?
    if len(split_name) == 1:
        return ""
    # Manage compressed files
    elif len(split_name) > 2 and split_name[-1].lower() in comp_ext_list:
        return ".{}.{}".format(split_name[-2], split_name[-1]).lower()
    # Normal situation = return the last element of the list
    else:
        return ".{}".format(split_name[-1]).lower()


def extensions_list(fp, comp_ext_list=["gz", "tgz", "zip", "xz", "bz2"], **kwargs):
    """
    Return The extension of a file in lower-case. If archived file ("gz", "tgz", "zip", "xz", "bz2")
    the method will output the base extension + the archive extension as a list
    """
    split_name = fp.split("/")[-1].split(".")
    # No extension ?
    if len(split_name) == 1:
        return []
    # Manage compressed files
    elif len(split_name) > 2 and split_name[-1].lower() in comp_ext_list:
        return [split_name[-2].lower(), split_name[-1].lower()]
    # Normal situation = return the last element of the list
    else:
        return [split_name[-1].lower()]


def file_name(fp, **kwargs):
    """
    Return The complete name of a file with the extension but without folder location
    """
    return fp.rpartition("/")[2]


def dir_name(fp, **kwargs):
    """
    Return the name of the directory where the file is located
    """
    return fp.rpartition("/")[0].rpartition("/")[2]


def dir_path(fp, **kwargs):
    """
    Return the directory path of a file
    """
    return fp.rpartition("/")[0]


##~~~~~~~ STRING FORMATTING ~~~~~~~#


def supersplit(string, separator="", **kwargs):
    """
    like split but can take a list of separators instead of a simple separator
    """
    if not separator:
        return string.split()

    if type(separator) == str:
        return string.split(separator)

    for sep in separator:
        string = string.replace(sep, "#")
    return string.split("#")


def rm_blank(name, replace="", **kwargs):
    """Replace blank spaces in a name by a given character (default = remove)
    Blanks at extremities are always removed and nor replaced"""
    return replace.join(name.split())


# ~~~~~~~ FILE MANIPULATION ~~~~~~~#


def concatenate(src_list, dest, **kwargs):
    """
    Concatenate a list of scr files in a single output file. Handle gziped files (mixed input and output)
    """
    if is_gziped(dest):
        open_fun_dest, open_mode_dest = gzip.open, "wt"
    else:
        open_fun_dest, open_mode_dest = open, "w"
    with open_fun_dest(dest, open_mode_dest) as fh_dest:
        for src in src_list:
            if is_gziped(src):
                open_fun_src, open_mode_src = gzip.open, "rt"
            else:
                open_fun_src, open_mode_src = open, "r"
            with open_fun_src(src, open_mode_src) as fh_src:
                shutil.copyfileobj(fh_src, fh_dest)


def copyFile(src, dest, **kwargs):
    """
    Copy a single file to a destination file or folder (with error handling/reporting)
    * src
        Source file path
    * dest
        Path of the folder where to copy the source file
    """
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as E:
        print("Error: %s" % E)
    # eg. source or destination doesn't exist
    except IOError as E:
        print("Error: %s" % E.strerror)


def gzip_file(fpin, fpout=None, keep_source=False, **kwargs):
    """
    gzip a file
    * fpin
        Path of the input uncompressed file
    * fpout
        Path of the output compressed file (facultative)
    """
    # Generate a automatic name if none is given
    if not fpout:
        fpout = fpin + ".gz"

    # Try to initialize handle for
    try:
        in_handle = open(fpin, "rb")
        out_handle = gzip.open(fpout, "wb")
        # Write input file in output file
        print("Compressing {}".format(fpin))
        out_handle.write(in_handle.read())
        # Close both files
        in_handle.close()
        out_handle.close()
        if not keep_source:
            remove_file(fpin)

        return os.path.abspath(fpout)

    except IOError as E:
        print(E)
        if os.path.isfile(fpout):
            try:
                os.remove(fpout)
            except OSError:
                print("Can't remove {}".format(fpout))


def gunzip_file(fpin, fpout=None, keep_source=False, **kwargs):
    """
    ungzip a file
    * fpin
        Path of the input compressed file
    * fpout
        Path of the output uncompressed file (facultative)
    """
    # Generate a automatic name without .gz extension if none is given
    if not fpout:
        fpout = fpin[0:-3]

    try:
        # Try to initialize handle for
        in_handle = gzip.GzipFile(fpin, "rb")
        out_handle = open(fpout, "wb")
        # Write input file in output file
        print("Uncompressing {}".format(fpin))
        out_handle.write(in_handle.read())
        # Close both files
        out_handle.close()
        in_handle.close()
        if not keep_source:
            remove_file(fpin)

        return os.path.abspath(fpout)

    except IOError as E:
        print(E)
        if os.path.isfile(fpout):
            try:
                os.remove(fpout)
            except OSError:
                print("Can't remove {}".format(fpout))


def remove_file(fp, exception_if_exist=False):
    """
    Try to remove a file from disk.
    """
    try:
        os.remove(fp)
    except OSError as E:
        if exception_if_exist:
            raise E


# ~~~~~~~ FILE INFORMATION/PARSING ~~~~~~~#


def linerange(fp, range_list=[], line_numbering=True, max_char_line=150, **kwargs):
    """
    Print a range of lines in a file according to a list of start end lists. Handle gziped files
    * fp
        Path to the file to be parsed
    * range_list
        list of start, end coordinates lists or tuples
    * line_numbering
        If True the number of the line will be indicated in front of the line
    * max_char_line
        Maximal number of character to print per line
    """
    if not range_list:
        n_line = fastcount(fp)
        range_list = [[0, 2], [n_line - 3, n_line - 1]]

    if is_gziped(fp):
        open_fun = gzip.open
        open_mode = "rt"
    else:
        open_fun = open
        open_mode = "r"

    with open_fun(fp, open_mode) as f:
        previous_line_empty = False
        for n, line in enumerate(f):
            line_print = False
            for start, end in range_list:
                if start <= n <= end:
                    if line_numbering:
                        l = "{}\t{}".format(n, line.rstrip())
                    else:
                        l = line.rstrip()

                    if max_char_line and len(l) > max_char_line:
                        print(l[0:max_char_line] + "...")
                    else:
                        print(l)

                    line_print = True
                    previous_line_empty = False
                    break

            if not line_print:
                if not previous_line_empty:
                    print("...")
                    previous_line_empty = True


def cat(fp, max_lines=100, line_numbering=False, max_char_line=150, **kwargs):
    """
    Emulate linux cat cmd but with line cap protection. Handle gziped files
    * fp
        Path to the file to be parsed
    * max_lines
        Maximal number of lines to print
    * line_numbering
        If True the number of the line will be indicated in front of the line
    * max_char_line
        Maximal number of character to print per line
    """
    n_line = fastcount(fp)
    if n_line <= max_lines:
        range_list = [[0, n_line - 1]]
    else:
        range_list = [[0, max_lines / 2 - 1], [n_line - max_lines / 2, n_line]]
    linerange(
        fp=fp,
        range_list=range_list,
        line_numbering=line_numbering,
        max_char_line=max_char_line,
    )


def tail(fp, n=10, line_numbering=False, max_char_line=150, **kwargs):
    """
    Emulate linux tail cmd. Handle gziped files
    * fp
        Path to the file to be parsed
    * n
        Number of lines to print starting from the end of the file
    * line_numbering
        If True the number of the line will be indicated in front of the line
    * max_char_line
        Maximal number of character to print per line
    """
    n_line = fastcount(fp)
    if n_line <= n:
        range_list = [[0, n_line]]
        print("Only {} lines in the file".format(n_line))
    else:
        range_list = [[n_line - n + 1, n_line]]
    linerange(
        fp=fp,
        range_list=range_list,
        line_numbering=line_numbering,
        max_char_line=max_char_line,
    )


def head(
    fp,
    n=10,
    ignore_comment_line=False,
    comment_char="#",
    max_char_line=300,
    sep="\t",
    max_char_col=200,
    **kwargs,
):
    """
    Emulate linux head cmd. Handle gziped files and bam files
    * fp
        Path to the file to be parsed. Works with text, gunziped and binary bam/sam files
    * n
        Number of lines to print starting from the begining of the file (Default 10)
    * ignore_comment_line
        Skip initial lines starting with a specific character. Pointless for bam files(Default False)
    * comment_char
        Character or string for ignore_comment_line argument (Default "#")
    * max_char_line
        Maximal number of character to print per line (Default 150)
    """
    line_list = []

    # For bam files
    if has_extension(fp=fp, ext=["bam", "sam"]):
        with ps.AlignmentFile(fp) as f:

            for line_num, read in enumerate(f):
                if line_num >= n:
                    break
                l = read.to_string()
                if sep:
                    line_list.append(l.split(sep)[0:11])
                else:
                    line_list.append(l)
                line_num += 1

    # Not bam file
    else:
        # For text files
        if is_gziped(fp):
            open_fun = gzip.open
            open_mode = "rt"
        else:
            open_fun = open
            open_mode = "r"

        try:
            with open_fun(fp, open_mode) as fh:
                line_num = 0
                while line_num < n:
                    l = next(fh).rstrip()
                    if ignore_comment_line and l.startswith(comment_char):
                        continue
                    if sep:
                        line_list.append(l.split(sep))
                    else:
                        line_list.append(l)
                    line_num += 1

        except StopIteration:
            print("Only {} lines in the file".format(line_num))

    # Print lines
    if sep:
        try:
            # Find longest elem per col
            col_len_list = [0 for _ in range(len(line_list[0]))]
            for ls in line_list:
                for i in range(len(ls)):
                    len_col = len(ls[i])
                    if len_col > max_char_col:
                        col_len_list[i] = max_char_col
                    elif len_col > col_len_list[i]:
                        col_len_list[i] = len_col

            line_list_tab = []
            for ls in line_list:
                s = ""
                for i in range(len(ls)):
                    len_col = col_len_list[i]
                    len_cur_col = len(ls[i])
                    s += ls[i][0:len_col] + " " * (len_col - len_cur_col) + " "
                line_list_tab.append(s)
            line_list = line_list_tab

        # Fall back to none tabulated display
        except IndexError:
            return head(
                fp=fp,
                n=n,
                ignore_comment_line=ignore_comment_line,
                comment_char=comment_char,
                max_char_line=max_char_line,
                sep=None,
            )

    for l in line_list:
        if max_char_line and len(l) > max_char_line:
            print(l[0:max_char_line] + "...")
        else:
            print(l)
    print()


def grep(fp, regex, max_lines=None):
    """
    Emulate linux head cmd. Handle gziped files and bam files
    * fp
        Path to the file to be parsed. Works with text, gunziped and binary bam/sam files
    * regex
        Linux style regular expression (https://docs.python.org/3.6/howto/regex.html#regex-howto)
        can also be a list, set or tuple of regex
    * max_lines
        Maximal number of line to print (Default None)
    """
    # Compile regular expression
    if not type(regex) in (list, set, tuple):
        regex_list = [re.compile(regex)]
    else:
        regex_list = [re.compile(r) for r in regex]

    # For text files
    if is_gziped(fp):
        open_fun = gzip.open
        open_mode = "rt"
    else:
        open_fun = open
        open_mode = "r"

    with open_fun(fp, open_mode) as fh:
        found = 0
        for line in fh:
            if max_lines and found == max_lines:
                break
            for r in regex_list:
                if r.search(line):
                    print(line.rstrip())
                    found += 1
                    break


def linesample(fp, n_lines=100, line_numbering=True, max_char_line=150, **kwargs):
    """
    Randomly sample lines in a file and print them. Handle gziped files
    * fp
        Path to the file to be parsed
    * n_lines
        Number of lines to sample in the file
    * line_numbering
        If True the number of the line will be indicated in front of the line
    * max_char_line
        Maximal number of character to print per line
    """
    n_lines_origin = fastcount(fp)

    # Take into account the situation in which there are less lines in the file than requested.
    if n_lines >= n_lines_origin:
        if verbose:
            print(
                "Not enough lines in source file. Writing all reads in the output file"
            )
        index_list = list(range(0, n_lines_origin - 1))
    else:
        index_list = sorted(random.sample(range(0, n_lines_origin - 1), n_lines))

    # Sample lines in input file according to the list of random line numbers
    if is_gziped(fp):
        open_fun = gzip.open
        open_mode = "rt"
    else:
        open_fun = open
        open_mode = "r"

    with open_fun(fp, open_mode) as fh:
        j = 0
        for i, l in enumerate(fh):
            if j >= n_lines:
                break
            if i == index_list[j]:
                j += 1
                l = l.rstrip()
                if max_char_line and len(l) > max_char_line:
                    l = l[0:max_char_line] + "..."
                if line_numbering:
                    l = "{}\t{}".format(i, l)
                print(l)


def count_uniq(
    fp,
    colnum,
    select_values=None,
    drop_values=None,
    skip_comment="#",
    sep="\t",
    **kwargs,
):
    """
    Count unique occurences in a specific column of a tabulated file
    * fp
        Path to the file to be parsed (gzipped or not)
    * colnum
        Index number of the column to summarize
    * select_values
        Select specific lines in the file based on a dictionary containing column index(es) and valu(es) or list
        of values to select. Exemple {2:["exon", "transcript"], 4:"lincRNA"}. DEFAULT=None
    * drop_values
        Same think that select_value but will drop the lines instead. DEFAULT=None
    * skip_comment
        Drop any comment lines starting with this character. DEFAULT="#"
    * sep
        Character or list of characters to use in order to split the lines. Exemple ["\t",";"]. DEFAULT="\t"
    """
    # Transform separator in regular expression if needed
    if type(sep) == list:
        sep = "[{}]".format("".join(sep))
        engine = "python"
    else:
        engine = "c"

    df = pd.read_csv(
        fp,
        sep=sep,
        index_col=False,
        header=None,
        comment=skip_comment,
        engine=engine,
    )

    if select_values:
        for i, j in select_values.items():
            if type(j) == str:
                df = df[(df[i] == j)]
            if type(j) == list:
                df = df[(df[i].isin(j))]

    if drop_values:
        for i, j in drop_values.items():
            if type(j) == str:
                df = df[(df[i] != j)]
            if type(j) == list:
                df = df[(~df[i].isin(j))]

    return df.groupby(colnum).size().sort_values(ascending=False)


def fastcount(fp, **kwargs):
    """
    Efficient way to count the number of lines in a file. Handle gziped files
    """
    if is_gziped(fp):
        open_fun = gzip.open
        open_mode = "rt"
    else:
        open_fun = open
        open_mode = "r"

    with open_fun(fp, open_mode) as fh:
        lines = 0
        buf_size = 1024 * 1024
        read_f = fh.read  # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count("\n")
            buf = read_f(buf_size)

    return lines


def simplecount(fp, ignore_hashtag_line=False, **kwargs):
    """
    Simple way to count the number of lines in a file with more options
    """
    if is_gziped(fp):
        open_fun = gzip.open
        open_mode = "rt"
    else:
        open_fun = open
        open_mode = "r"

    with open_fun(fp, open_mode) as fh:
        lines = 0
        for line in fh:
            if ignore_hashtag_line and line[0] == "#":
                continue
            lines += 1

    return lines


# ~~~~~~~ DIRECTORY MANIPULATION ~~~~~~~#


def mkdir(
    fp,
    error_if_existing=False,
    delete_existing=False,
    verbose=False,
    **kwargs,
):
    """
    Reproduce the ability of UNIX "mkdir -p" command
    (ie if the path already exits no exception will be raised).
    Can create nested directories by recursivity
    Remove existing directory is requested
    * fp
        path name where the folder should be created
    * error_if_existing
        Raise an error if the directory already exists
    * delete_existing
        Delete existing directory before creating a new one
    * verbose
        Print extra info
    """

    if os.path.exists(fp) and os.path.isdir(fp):
        if error_if_existing:
            raise FileExistsError("Directory already existing")
        elif delete_existing:
            if verbose:
                print(f"Removing existing directory and creating directory: {fp}")
            shutil.rmtree(fp)
            os.makedirs(fp)
        else:
            if verbose:
                print("Directory already existing. No need to create")
    else:
        if verbose:
            print(f"Creating directory: {fp}")
        os.makedirs(fp)


def get_size_str(fp):
    size = os.path.getsize(fp)
    for limit, unit in ((1, "B"), (1e3, "KB"), (1e6, "MB"), (1e9, "GB"), (1e12, "TB")):
        s = size / limit
        if s < 1000:
            return f"{round(s, 3)} {unit}"


def tree(
    dir_fn=".",
    depth=2,
    dir_only=False,
    tab="  ",
    show_hidden=False,
    level=0,
):
    """
    Print a directory arborescence
    """
    dir_fn = dir_fn.rstrip("/")
    for dir_fn in glob.glob(dir_fn):
        if not os.path.isdir(dir_fn):
            return
        else:
            if level == 0:
                print("\x1b[{}m{}\x1b[0m".format(34, os.path.basename(dir_fn)))

            dir_list = []
            other_list = []
            for fn in os.listdir(dir_fn):
                if not show_hidden and fn.startswith("."):
                    continue

                fn = os.path.join(dir_fn, fn)
                if os.path.isdir(fn):
                    dir_list.append(fn)
                else:
                    other_list.append(fn)

            if not dir_only:
                if other_list:
                    for fn in sorted(other_list):
                        if os.path.isfile(fn):
                            color = "32"
                        elif os.path.islink(fn):
                            color = "31"
                        else:
                            color = "37"
                        print(
                            "{}|_ \x1b[{}m{} [{}]\x1b[0m".format(
                                tab * level,
                                color,
                                os.path.basename(fn),
                                get_size_str(fn),
                            )
                        )

            if dir_list:
                for fn in sorted(dir_list):
                    print(
                        "{}|_ \x1b[{}m{}\x1b[0m".format(
                            tab * level, 34, os.path.basename(fn)
                        )
                    )
                    if not depth == 1:
                        tree(
                            dir_fn=fn,
                            depth=depth - 1,
                            dir_only=dir_only,
                            tab=tab,
                            level=level + 1,
                        )


def ls(dir_fn="./"):
    """
    Simple function to emulate ls -lahG
    """
    dir_fn = dir_fn.rstrip("/")

    if not os.path.isdir(dir_fn):
        print(f"{dir_fn} is not a directory")
    else:
        print(dir_fn)
        fn_list = os.listdir(dir_fn)
        fn_list.sort()

        for fn in sorted(fn_list):
            path = os.path.join(dir_fn, fn)

            if os.path.isdir(path):
                color = "34"
            elif os.path.isfile(path):
                color = "32"
            elif os.path.islink(path):
                color = "31"
            else:
                color = "37"

            print(" \x1b[{}m{:<12} {}\x1b[0m".format(color, get_size_str(path), fn))


# ~~~~~~~ SHELL MANIPULATION ~~~~~~~#


def make_cmd_str(
    prog_name,
    opt_dict={},
    opt_list=[],
    **kwargs,
):
    """
    Create a Unix like command line string from the prog name, a dict named arguments and a list of unmammed arguments
    exemple make_cmd_str("bwa", {"b":None, t":6, "i":"../idx/seq.fa"}, ["../read1", "../read2"])
    * prog_name
        Name (if added to the system path) or path of the program
    * opt_dict
        Dictionary of option arguments such as "-t 5". The option flag have to be the key (without "-") and the the
        option value in the dictionary value. If no value is requested after the option flag "None" had to be assigned
        to the value field.
    * opt_list
        List of simple command line arguments
    """

    # Start the string by the name of the program
    cmd = "{} ".format(prog_name)

    # Add options arguments from opt_dict
    if opt_dict:
        for key, value in opt_dict.items():
            if value:
                cmd += "{} {} ".format(key, value)
            else:
                cmd += "{} ".format(key)

    # Add arguments from opt_list
    if opt_list:
        for value in opt_list:
            cmd += "{} ".format(value)

    return cmd


def bash_basic(cmd, virtualenv=None, **kwargs):
    """
    Sent basic bash command
    * cmd
        A command line string formatted as a string
    * virtualenv
        If specified will try to load a virtualenvwrapper environment before runing the command
    """
    if virtualenv:
        cmd = "source ~/.bashrc && workon {} && {} && deactivate".format(
            virtualenv, cmd
        )
    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) as proc:
        stdout, stderr = proc.communicate()
        print(stdout.decode())
        print(stderr.decode())


def bash(
    cmd,
    virtualenv=None,
    conda=None,
    live="stdout",
    print_stdout=True,
    ret_stdout=False,
    log_stdout=None,
    print_stderr=True,
    ret_stderr=False,
    log_stderr=None,
    print_cmd=False,
    dry=False,
    **kwargs,
):
    """
    More advanced version of bash calling with live printing of the standard output and possibilities to log the
    redirect the output and error as a string return or directly in files. If ret_stderr and ret_stdout are True a
    tuple will be returned and if both are False None will be returned
    * cmd
        A command line string formatted as a string
    * virtualenv
        If specified will try to load a virtualenvwrapper environment before runing the command
    * conda
        If specified will try to load a conda environment before runing the command
    * print_stdout
        If True the standard output will be LIVE printed through the system standard output stream
    * ret_stdout
        If True the standard output will be returned as a string
    * log_stdout
        If a filename is given, the standard output will logged in this file
    * print_stderr
        If True the standard error will be printed through the system standard error stream
    * ret_stderr
        If True the standard error will be returned as a string
    * log_stderr
        If a filename is given, the standard error will logged in this file
    """
    if print_cmd:
        print(cmd)
    if dry:
        return

    if virtualenv:
        cmd = "source ~/.bashrc && workon {} && {} && deactivate".format(
            virtualenv, cmd
        )
    elif conda:
        cmd = "source ~/.bashrc && conda activate {} && {} && conda deactivate".format(
            conda, cmd
        )

    # empty str buffer
    stdout_str = ""
    stderr_str = ""

    # First execute the command parse the output
    with Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, executable="bash") as proc:

        # Only 1 standard stream can be output at the time stdout or stderr
        while proc.poll() is None:

            # Live parse stdout
            if live == "stdout":
                for line in iter(proc.stdout.readline, b""):
                    if print_stdout:
                        sys.stdout.write(line.decode())
                    if ret_stdout or log_stdout:
                        stdout_str += line.decode()

            # Live parse stderr
            elif live == "stderr":
                for line in iter(proc.stderr.readline, b""):
                    if print_stderr:
                        sys.stderr.write(line.decode())
                    if ret_stderr or log_stderr:
                        stderr_str += line.decode()

        # Verify that the command was successful and if not print error message and raise an exception
        if proc.returncode >= 1:
            sys.stderr.write(
                "Error code #{} during execution of the command : {}\n".format(
                    proc.returncode, cmd
                )
            )
            for line in iter(proc.stderr.readline, b""):
                sys.stderr.write(line.decode())
            return None

        if live != "stdout" and (print_stdout or ret_stdout or log_stdout):
            for line in iter(proc.stdout.readline, b""):
                if print_stdout:
                    sys.stdout.write(line.decode())
                if ret_stdout or log_stdout:
                    stdout_str += line.decode()

        if live != "stderr" and (print_stderr or ret_stderr or log_stderr):
            for line in iter(proc.stderr.readline, b""):
                if print_stderr:
                    sys.stderr.write(line.decode())
                if ret_stderr or log_stderr:
                    stderr_str += line.decode()

        # Write log in file if requested
        if log_stdout:
            with open(log_stdout, "w") as fp:
                fp.write(stdout_str)

        if log_stderr:
            with open(log_stderr, "w") as fp:
                fp.write(stderr_str)

    # Return standard output and err if requested
    if ret_stdout and ret_stderr:
        return (stdout_str, stderr_str)
    if ret_stdout:
        return stdout_str
    if ret_stderr:
        return stderr_str
    return None


def bash_update(cmd, update_freq=1, **kwargs):
    """
    FOR JUPYTER NOTEBOOK
    Run a bash command and print the output in the cell. The output is updated each time until the output is None.
    This is suitable for monitoring tasks that log events until there is nothing else to print such as bjobs or bpeeks.
    * cmd
        A command line string formatted as a string
    * update_freq
        The frequency of output updating in seconds [DEFAULT: 1]
    """

    # imports
    try:
        from IPython.core.display import clear_output
    except (NameError, ImportError) as E:
        print(E)
        print(
            "jupyter notebook is required to use this function. Please verify your dependencies"
        )
        sys.exit()

    # Init stdout buffer
    stdout_prev = ""

    # Loop and update the line is something changes
    try:
        while True:
            stdout = bash(
                cmd,
                ret_stderr=False,
                ret_stdout=True,
                print_stderr=False,
                print_stdout=False,
            )
            if stdout != stdout_prev:
                clear_output()
                print(stdout)
                stdout_prev = stdout
            if not stdout:
                print("All done")
                break

            time.sleep(update_freq)
    except KeyboardInterrupt:
        print("Stop monitoring\n")


def qsub(
    cmd_list,
    mem="1G",
    threads=1,
    gpu=False,
    queue="algo",
    project="research",
    node="bowhead001",
    job_name=None,
    print_script=False,
    dry=False,
    shell="/bin/bash",
    stdout_fn="qsub_stdout.txt",
    stderr_fn="qsub_stderr.txt",
    script_fn="qsub_script.sh",
):

    # Remove existing log files
    if os.path.isfile(stdout_fn):
        os.remove(stdout_fn)
    if os.path.isfile(stderr_fn):
        os.remove(stderr_fn)

    with open(script_fn, "w") as fp:
        fp.write(f"#! {shell}\n")
        fp.write(f"#$ -S {shell}\n")
        fp.write("#$ -cwd\n")

        if job_name:
            fp.write(f"#$ -N {job_name}\n")
        if project:
            fp.write(f"#$ -P {project}\n")
        if threads:
            fp.write(f"#$ -pe mt {threads}\n")
        if gpu:
            fp.write(f"#$ -l gpu=1\n")
        if node:
            fp.write(f"#$ -l h={node}\n")
        if mem:
            fp.write(f"#$ -l m_mem_free={mem}\n")
        if queue:
            if queue == "algo":
                fp.write(f"#$ -l algo=1\n")
            else:
                fp.write(f"#$ -q {queue}\n")
        if stdout_fn:
            fp.write(f"#$ -o {stdout_fn}\n")
        if stderr_fn:
            fp.write(f"#$ -e {stderr_fn}\n")
        fp.write("\n")

        if type(cmd_list) == str:
            cmd_list = [cmd_list]

        fp.write(f"source ~/.bashrc\n")
        for cmd in cmd_list:
            fp.write(f"{cmd}\n")

    if print_script:
        with open(script_fn, "r") as fp:
            print(fp.read())

    if dry:
        return random.randint(0, 100000)
    else:
        stdout = bash(cmd=f"qsub {script_fn}", ret_stdout=True, print_stdout=False)
        try:
            if stdout:
                return stdout.split(" ")[2]

        except Exception as E:
            cprint("ERROR: job not submitted", color="red")
            cprint(str(E))


def qstat(
    jobid=None,
    user=None,
    state=None,
    queue=None,
    name=None,
):
    """
    FOR JUPYTER NOTEBOOK IN SGE environment
    Emulate SGE qstat command. Return a Dataframe of jobs
    """

    stdout = bash(
        "qstat -r",
        print_stderr=False,
        print_stdout=False,
        ret_stderr=False,
        ret_stdout=True,
    )

    if stdout:
        jobs = []
        header = []
        for l in stdout.split("\n"):
            if l:
                if not header:
                    l = l.replace("submit/start at", "submit/start_at")
                    field = ""
                    prev = " "
                    start = 0
                    for i, c in enumerate(l):
                        if c != " " and prev == " ":
                            if field:
                                header.append((field.strip(), start, i))
                            start = i
                            field = c
                        else:
                            field += c
                        prev = c

                elif l.strip().split()[0].isdigit():
                    job_dict = OrderedDict()
                    for field, start, end in header:
                        value = l[start:end].strip()
                        job_dict[field] = value

                elif l.strip().split(":")[0] == "Full jobname":
                    job_dict["name"] = l.split(":")[1].strip()
                    jobs.append(job_dict)

        df = pd.DataFrame(jobs)

        # filter if needed
        if jobid:
            df = df[df["job-ID"].str.match(jobid)]
        if user:
            df = df[df["user"].str.match(user)]
        if state:
            df = df[df["state"].str.match(state)]
        if queue:
            df = df[df["queue"].str.match(queue)]
        if name:
            df = df[df["name"].str.match(name)]

        return df


def bsub(
    cmd,
    virtualenv=None,
    conda=None,
    mem=None,
    threads=None,
    queue=None,
    wait_jobid=None,
    stdout_fp=None,
    stderr_fp=None,
    send_email=False,
    print_cmd=True,
    dry=False,
    job_name=None,
    other_options=None,
    **kwargs,
):
    """
    FOR JUPYTER NOTEBOOK IN LSF environment
    Send an LSF bsub command through bash and return the JOBID
    For more information read the bsub documentation
    * cmd
        A command line string formatted as a string
    * virtualenv
        If specified will try to load a virtualenvwrapper environment before runing the command
    * conda
        If specified will try to load a conda environment before runing the command
    * mem
        Memory to reserve (-M and -R 'rusage[mem=])
    * threads
        Number of thread to reserve (-n)
    * queue
        Name of the LSF queue to be used (-q)
    * wait_jobid
        jobid of list of jobid to wait before executing this command(-w 'post_done(jobid))
    * stdout_fp
        Path of the file where to write the standard output of the command (-oo)
    * stderr_fp
        Path of the file where to write the standard error of the command (-eo)
    * send_email
        If True, will force LSF to send an email even if stdout_fp and/or stderr_fp is given
    * job_name

    """
    bsub_cmd = "bsub "
    if job_name:
        bsub_cmd += "-J {} ".format(job_name)
    if mem:
        bsub_cmd += "-M {0} -R 'rusage[mem={0}]' ".format(mem)
    if threads:
        bsub_cmd += "-n {0} ".format(threads)
    if queue:
        bsub_cmd += "-q {0} ".format(queue)
    if stdout_fp:
        bsub_cmd += "-oo {0} ".format(stdout_fp)
    if stderr_fp:
        bsub_cmd += "-eo {0} ".format(stderr_fp)
    if send_email:
        bsub_cmd += "-N "
    if wait_jobid:
        if not type(wait_jobid) in (list, set, tuple):
            wait_jobid = [wait_jobid]
        jobid_str = "&&".join(["post_done({0})".format(jobid) for jobid in wait_jobid])
        bsub_cmd += "-w '{0}' ".format(jobid_str)
    if other_options:
        bsub_cmd += "{} ".format(other_options)

    full_cmd = '{} "{}"'.format(bsub_cmd, cmd)

    if print_cmd:
        print(full_cmd)
    if dry:
        return random.randint(0, 100000)
    else:
        stdout = bash(virtualenv=virtualenv, conda=conda, cmd=full_cmd, ret_stdout=True)
        return stdout.split("<")[1].split(">")[0]


def bjobs(jobid=None, user=None, status=None, queue=None, cmd=None):
    """
    FOR JUPYTER NOTEBOOK IN LSF environment
    Emulate LSF bjobs command. Return a Dataframe of jobs
    """
    # Init collection
    job_info = namedtuple(
        "job_info",
        [
            "jobid",
            "user",
            "status",
            "queue",
            "cmd",
            "cpu_used",
            "mem",
            "swap",
            "submit_time",
            "start_time",
        ],
    )
    l = []

    # Get long job desriptions from bjobs
    stdout = bash("bjobs -W", ret_stdout=True, print_stdout=False)

    if not stdout:
        pd.DataFrame()

    # Parse bjobs output
    for line in stdout.split("\n"):
        if line[:1].isdigit():
            ls = line.split()
            l.append(
                job_info(
                    ls[0],
                    ls[1],
                    ls[2],
                    ls[3],
                    " ".join(ls[6:-8]),
                    ls[-6],
                    ls[-5],
                    ls[-4],
                    ls[-8],
                    ls[-2],
                )
            )

    # Cast to Dataframe
    df = pd.DataFrame(l)

    # filter if needed
    if jobid:
        df = df[df["jobid"].str.match(jobid)]
    if user:
        df = df[df["user"].str.match(user)]
    if status:
        df = df[df["status"].str.match(status)]
    if queue:
        df = df[df["queue"].str.match(queue)]
    if cmd:
        df = df[df["cmd"].str.match(cmd)]

    return df


def bjobs_update(
    update_freq=5, jobid=None, user=None, status=None, queue=None, cmd=None
):
    """
    FOR JUPYTER NOTEBOOK IN LSF environment
    Emulate LSF bjobs command but update the cell every x seconds
    Cell is locked
    """
    from time import sleep

    try:
        from IPython.core.display import display, clear_output
    except (NameError, ImportError) as E:
        print(E)
        print(
            "jupyter notebook is required to use this function. Please verify your dependencies"
        )
        sys.exit()

    try:
        while True:
            df = bjobs(jobid=jobid, user=user, status=status, queue=queue, cmd=cmd)
            if df.empty:
                raise StopIteration
            display(df)
            sleep(update_freq)
            clear_output()

    except KeyboardInterrupt:
        clear_output()
        display(bjobs(jobid=jobid, user=user, status=status, queue=queue, cmd=cmd))

    except StopIteration:
        print("All jobs done")


def bjobs_lock(jobid=None, update_freq=2, final_delay=2):
    """
    FOR JUPYTER NOTEBOOK IN LSF environment
    Check if bjobs has running or pending jobs until all are done
    * jobid
        List of jobid to Check
    * update_freq
        The frequency of output updating in seconds [DEFAULT: 2]
    * final_delay
        Final delay in seconds at the end of all jobs to prevent IO errors [DEFAULT: 5]
    """

    # Homogenize types to list of str
    if type(jobid) in [int, str]:
        jobid = [str(jobid)]
    elif type(jobid) in [list, set, tuple]:
        jobid = [str(j) for j in jobid]

    try:
        while True:
            df = bjobs()

            if df.empty:
                raise StopIteration

            # if a jobid list was provided Check if at least one of the jobs is still in the list
            if jobid:
                if not df["JobID"].isin(jobid).any():
                    raise StopIteration

            s = []
            for i, j in df["Status"].value_counts().items():
                s.append("{}:{}".format(i, j))
            stdout_print("Jobs Status {}\r".format("\t".join(s)))

            time.sleep(update_freq)

    except KeyboardInterrupt:
        stdout_print("\rUser interuption" + " " * 30 + "\n")
    except StopIteration:
        time.sleep(final_delay)
        stdout_print("All jobs done" + " " * 30 + "\n")


##~~~~~~~ DICTIONNARY FORMATTING ~~~~~~~#


def dict_to_md(
    d,
    key_label="",
    value_label="",
    transpose=False,
    sort_by_key=False,
    sort_by_val=True,
    max_items=None,
    **kwargs,
):
    """
    Transform a dict into a markdown formated table
    """
    # Preprocess dict
    if sort_by_key:
        d = OrderedDict(reversed(sorted(d.items(), key=lambda t: t[0])))

    if sort_by_val:
        d = OrderedDict(reversed(sorted(d.items(), key=lambda t: t[1])))

    if max_items and len(d) > max_items:
        d2 = OrderedDict()
        n = 0
        for key, value in d.items():
            d2[key] = value
            n += 1
            if n >= max_items:
                break
        d2["..."] = "..."
        d = d2

    # Prepare output
    if transpose:
        buffer = "|{}|".format(key_label)
        for key in d.keys():
            buffer += "{}|".format(key)
        buffer += "\n|:---|"
        for _ in range(len(d)):
            buffer += ":---|"
        buffer += "\n|{}|".format(value_label)
        for value in d.values():
            buffer += "{}|".format(value)
        buffer += "\n"

    else:
        buffer = "|{}|{}|\n|:---|:---|\n".format(key_label, value_label)
        for key, value in d.items():
            buffer += "|{}|{}|\n".format(key, value)

    return buffer


def dict_to_report(
    d, tab="\t", ntab=0, sep=":", sort_dict=True, max_items=None, **kwargs
):
    """
    Recursive function to return a text report from nested dict or OrderedDict objects
    """
    # Preprocess dict
    if sort_dict:

        # Verify that all value in the dict are numerical
        all_num = True
        for value in d.values():
            if not type(value) in [int, float]:
                all_num = False

        # Sort dict by val only if it contains numerical values
        if all_num:
            d = OrderedDict(reversed(sorted(d.items(), key=lambda t: t[1])))

            if max_items and len(d) > max_items:
                d2 = OrderedDict()
                n = 0
                for key, value in d.items():
                    d2[key] = value
                    n += 1
                    if n >= max_items:
                        break
                d2["..."] = "..."
                d = d2

        # Else sort alphabeticaly by key
        else:
            d = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    # Prepare output
    report = ""
    for name, value in d.items():
        if type(value) == OrderedDict or type(value) == dict:
            report += "{}{}\n".format(tab * ntab, name)
            report += dict_to_report(
                value,
                tab=tab,
                ntab=ntab + 1,
                sep=sep,
                sort_dict=sort_dict,
                max_items=max_items,
            )
        else:
            report += "{}{}{}{}\n".format(tab * ntab, name, sep, value)
    return report


##~~~~~~~ WEB TOOLS ~~~~~~~#


def url_exist(url, **kwargs):
    """
    Predicate verifying if an url exist without downloading all the link
    """

    # Function specific third party import
    try:
        import httplib2
    except (NameError, ImportError) as E:
        print(E)
        print(
            "httplib2 is required to use this function. Please verify your dependencies"
        )
        sys.exit()

    # Chek the url
    h = httplib2.Http()

    try:
        resp = h.request(url, "HEAD")
        return int(resp[0]["status"]) < 400
    except:
        return False


def wget(url, out_name=None, out_dir=None, ftp_proxy=None, http_proxy=None):
    """
    Download a file from an URL to a local storage using wget
    *  url
        A internet URL pointing to the file to download
    *  out_name
        Path of the output file (facultative)
    * out_dir
        Path of the output directory, if no out_name given (facultative)
    * ftp_proxy
        address of ftp proxy to use
    * http_proxy
        address of http proxy to use
    """
    cmd_l = []
    if ftp_proxy:
        cmd_l.append(f"export ftp_proxy={ftp_proxy} &&")
    if http_proxy:
        cmd_l.append(f"export http_proxy={http_proxy} &&")

    cmd_l.append("wget --no-verbose")
    if out_name:
        cmd_l.append(f"-O {out_name}")
    elif out_dir:
        cmd_l.append(f"-P {out_dir}")
    cmd_l.append(url)

    cmd = " ".join(cmd_l)
    bash(cmd)


##~~~~~~~ FUNCTIONS TOOLS ~~~~~~~#


def print_arg(**kwargs):
    """
    Print calling function named and unnamed arguments
    """

    # Function specific standard lib imports
    from inspect import getargvalues, stack

    # Parse all arg
    posname, kwname, args = getargvalues(stack()[1][0])[-3:]
    # For enumerated named arguments
    if args:
        print("Enumerated named argument list:")
        for i, j in args.items():
            if i != posname and i != kwname:
                print("\t{}: {}".format(i, j))
        # For **kwarg arguments
        if kwname:
            print("Unenumerated named arguments list:")
            for i, j in args[kwname].items():
                print("\t{}: {}".format(i, j))
        args.update(args.pop(kwname, []))
        if posname:
            print("Unnamed positional arguments list:")
            for i in args[posname]:
                print("\t{}".format(i))


##~~~~~~~ DNA SEQUENCE TOOLS ~~~~~~~#


def base_generator(
    bases=["A", "T", "C", "G"],
    weights=[0.280788, 0.281691, 0.193973, 0.194773],
    **kwargs,
):
    """
    Generator returning DNA/RNA bases according to a probability weightning
    * bases: list (default ["A","T","C","G"])
        DNA RNA bases allowed
    * weights: list (default [0.280788,0.281691,0.193973,0.194773])
        Probability of each base to be returned. Should match the index of bases. The sum does not need to be equal to 1.
        If the list is empty bases will be returned with a flat probability. The default values represent the frequency in the human
        genome (excluding N).
    """
    # If weights is provided create weighted generator
    if weights:

        # Verify that the 2 lists are the same size
        if len(bases) != len(weights):
            raise ValueError("weights is not the same length as bases.")

        # Calculate cumulated weights
        cum_weights = list(itertools.accumulate(weights))

        while True:
            # Emit a uniform probability between 0 and the max value of the cumulative weights
            p = random.uniform(0, cum_weights[-1])
            # Use bisect to retun the corresponding base
            yield bases[bisect.bisect(cum_weights, p)]

    # If not weight if required, will return each base with the same probability
    else:
        while True:
            yield random.choice(bases)


def make_random_sequence(
    bases=["A", "T", "C", "G"],
    weights=[0.280788, 0.281691, 0.193973, 0.194773],
    length=1000,
    **kwargs,
):
    """
    return a sequence of DNA/RNA bases according to a probability weightning
    * bases: list (default ["A","T","C","G"])
        DNA RNA bases allowed in the sequence
    * weights: list (default [0.280788,0.281691,0.193973,0.194773])
        Probability of each base to be returned. Should match the index of bases. The sum does not need to be equal to 1.
        If the list is empty bases will be returned with a flat probability. The default values represent the frequency in the human
        genome (excluding N).
    * length: int (default 1000)
        length of the sequence to be returned
    """
    bgen = base_generator(bases=bases, weights=weights)
    seq_list = [next(bgen) for _ in range(length)]
    return "".join(seq_list)


def make_kmer_guided_sequence(
    how="min",
    bases=["A", "G", "T", "C"],
    kmer_len=3,
    hp_max=3,
    seq_len=100,
    n_seq=10,
    init_seq="",
    seed=None,
    verbose=True,
):
    """
    Generate a list of sequences with an optimized kmer content.
    * how
        min = Always choose the kmer with the lower kmer count in the previous sequence. Random in case of ties
        weights = Bases are randomly picked based on a probability invertly corelated to the kmer counts in the prvious sequence
    * bases = ["A","T","C","G"],
        DNA RNA bases allowed in the sequence
    * kmer_len: int (default 3)
        Length of kmer to optimize the distribution
    * hp_max: int (default 3)
        Maximal length of homopolymers
    * seq_len: int (default 100)
        Length of each sequence to be generated
    * init_seq: str (default None)
        Sequence to initialise the kmer counter from
    * n_seq: int (default 10)
        Overall number of sequences to be generated
    * seed: None or int
        If given the random generator will behave in a deterministic way
    """
    # Set seed if needed
    random.seed(seed)
    np.random.seed(seed)

    kmer_c = Counter()
    if init_seq and len(init_seq) >= kmer_len:
        for i in range(0, len(init_seq) - kmer_len):
            kmer = init_seq[i:i+kmer_len]
            if set(kmer).difference(set(bases)):
                continue
            kmer_c[kmer]+=1

    seq_l = []
    for _ in trange(n_seq, disable=not verbose):
        seq = []

        # First base
        hp = 1
        seq.append(random.choice(bases))

        # Extend seed to length kmer_len
        for i in range(kmer_len - 1):
            # Reduce choice if max homopolymer reached
            choices = [i for i in bases if i != seq[-1]] if hp >= hp_max else bases
            # Sample from available choices
            seq.append(random.choice(choices))
            # Check if homopolymers extends
            hp = hp + 1 if seq[-2] == seq[-1] else 1
        kmer_c["".join(seq)] += 1

        # Extend sequence
        for _ in range(seq_len - kmer_len):

            # Reduce choice if max homopolymer reached
            choices = [i for i in bases if i != seq[-1]] if hp >= hp_max else bases
            prev = seq[-kmer_len + 1 :]

            if how == "min":
                count_d = defaultdict(list)
                # Collect count for each possible kmers
                for b in choices:
                    kmer = "".join(prev + [b])
                    if not kmer in kmer_c:
                        count_d[0].append(b)
                    else:
                        count_d[kmer_c[kmer]].append(b)
                # Choose randomly fron base kmer with lower count
                b = random.choice(count_d[min(count_d.keys())])

            elif how == "weights":
                p = []
                # Collect count per kmer
                for b in choices:
                    kmer = "".join(prev + [b])
                    if not kmer in kmer_c:
                        p.append(0)
                    else:
                        p.append(kmer_c[kmer])
                # transform counts in inverted frequency weights
                p = np.array(p)
                p = 1 / (p - p.min() + 1)
                p = p / p.sum()
                # Choose randomly using weight matrix
                b = np.random.choice(choices, p=p)
            else:
                raise ValueError("how must be 'min' or 'weights'")

            # extend current sequence
            seq.append(b)
            # Update kmer counter
            kmer_c["".join(prev + [b])] += 1
            # Check if homopolymers extends
            hp = hp + 1 if seq[-2] == seq[-1] else 1

        # Append to list
        seq_l.append("".join(seq))

    if verbose:
        cc = Counter()
        for i in kmer_c.values():
            cc[i] += 1
        for i, j in cc.most_common():
            print("kmer counts {} / Occurences: {:,}".format(i, j))

    if n_seq == 1:
        return seq_l[0]
    return seq_l


def kmer_content(seq_list, min_kmer=3, max_kmer=9, figsize=(10, 2), yscale="log"):
    """
    Plot kmer content information from a list of DNA/RNA sequences
    * seq_list
        List a sequences or single sequence
    * min_kmer
        Minimal kmer size
    * max_kmer
        Maximal kmer size
    """
    # Cast to list if single seq
    if type(seq_list) == str:
        seq_list = [seq_list]

    # Collect kmer info in several passses
    for kmer_len in range(min_kmer, max_kmer + 1):
        jprint("Kmer of length {}".format(kmer_len), bold=True)
        c = Counter()

        # Count each kmer occurence
        for seq in seq_list:
            for i in range(0, len(seq) - kmer_len + 1):
                c[seq[i : i + kmer_len]] += 1
        print(
            "Found {:,} kmers out of {:,} possibilities".format(
                len(c), pow(4, kmer_len)
            )
        )

        # Compute Stats
        l = []
        for i in c.values():
            l.append(i)
        print(
            "Median occurences: {:,}, Min occurences: {:,}, Max occurences: {:,}".format(
                int(np.median(l)), np.min(l), np.max(l)
            )
        )

        # Bin kmer occurence counts
        cc = Counter()
        for i in c.values():
            cc[i] += 1

        # plot distribution
        with pl.style.context("ggplot"):
            fig, ax = pl.subplots(figsize=figsize)
            ax.bar(list(cc.keys()), list(cc.values()))
            ax.set_yscale(yscale)
            ax.set_xlabel("Occurences count")
            pl.show()


##~~~~~~~ FASTQ SEQUENCE TOOLS ~~~~~~~#


def fastqc_summary(
    fastqc_res_dir,
    max_table_row=10,
    plot_width=500,
    table_module_list=["Basic Statistics", "Overrepresented sequences", "Kmer Content"],
    plot_module_list=[
        "Per base sequence quality",
        "Per tile sequence quality",
        "Per sequence quality scores",
        "Per base sequence content",
        "Per sequence GC content",
        "Per base N content",
        "Sequence Length Distribution",
        "Sequence Duplication Levels",
        "Kmer Content",
        "Adapter Content",
    ],
):

    """
    Summarize and display fastqc results in IPYTHON/JUPYTER. Don't try to use in another interface or in terminal
    Works directly from the zipped results obtained by FastQC v0.11.5+
    * fastqc_res_dir
        Directory containing the zipped folders obtained with fastQC
    * max_table_row
        Maximal number of row for the tables [DEFAULT 10]
    * table_module_list
        List of the table modules to include. Default = All
    * plot_module_list
        List of the plot modules to include. Default = All
    """

    # Convert pictures names to module names
    all_plot_modules = {
        "Per base sequence quality": "per_base_quality.png",
        "Per tile sequence quality": "per_tile_quality.png",
        "Per sequence quality scores": "per_sequence_quality.png",
        "Per base sequence content": "per_base_sequence_content.png",
        "Per sequence GC content": "per_sequence_gc_content.png",
        "Per base N content": "per_base_n_content.png",
        "Sequence Length Distribution": "sequence_length_distribution.png",
        "Sequence Duplication Levels": "duplication_levels.png",
        "Kmer Content": "kmer_profiles.png",
        "Adapter Content": "adapter_content.png",
    }

    for fp in glob.glob(fastqc_res_dir + "/*_fastqc.zip"):
        display(HTML("<hr></hr>"))
        display(HTML('<font size="4"><b>{}</b></font>'.format(fp.rpartition("/")[2])))

        # Extract the zip file in a temporary folder
        with tempfile.TemporaryDirectory() as tmpdirname:
            zfile = zipfile.ZipFile(fp)
            zfile.extractall(tmpdirname)
            base_dir = glob.glob(tmpdirname + "/*/")[0]

            # Iterate over the fastqdata file
            with open(base_dir + "fastqc_data.txt", "r") as fastqc_data:
                # Set bool flag to false
                found_module = found_header = False

                # Parse the file
                for line in fastqc_data:
                    line = line.strip()

                    # If End of section a table section can be rendered
                    if line.startswith(">>END_MODULE"):
                        if found_module and found_header:
                            df_html = df.head(max_table_row).to_html()
                            display(HTML("<font size=2>" + df_html + "</font>"))
                            found_module = found_header = False

                    # Detect the start of a module section
                    elif line.startswith(">>"):
                        ls = line[2:].split("\t")
                        module_name = ls[0]
                        module_status = ls[1]

                        # Detect the start of a table section
                        if module_name in table_module_list:
                            display(
                                HTML(
                                    '<font size="3"><b>{} : {}</b></font>'.format(
                                        module_name, module_status
                                    )
                                )
                            )
                            found_module = True

                        # Detect the header of a plot section
                        if module_name in plot_module_list:
                            display(
                                HTML(
                                    '<font size="3"><b>{} : {}</b></font>'.format(
                                        module_name, module_status
                                    )
                                )
                            )
                            image = "{}Images/{}".format(
                                base_dir, all_plot_modules[module_name]
                            )
                            display(Image(image, width=plot_width))

                    # Fill a dataframe if a table section was found
                    elif found_module:
                        if not found_header:
                            df = pd.DataFrame(columns=line.split("\t")[1:])
                            found_header = True
                        else:
                            ls = line.split("\t")
                            df.loc[ls[0]] = ls[1:]


def bam_align_summary(fp, min_mapq=30):
    """
    Parse bam files and return a summary dataframe
    * fp
        file path to a bam file or regular expression matching multiple files
    * min_mapq
        minimal score to be considered high mapq
    """
    counter_dict = defaultdict(Counter)
    for bam in glob.glob(fp):

        label = bam.split("/")[-1].split(".")[0]
        jprint("Parse bam {}".format(label), bold=True)

        with ps.AlignmentFile(bam, "rb") as f:
            for read in f:
                if read.is_unmapped:
                    counter_dict[label]["unmapped"] += 1
                elif read.is_secondary:
                    counter_dict[label]["secondary"] += 1
                elif read.is_supplementary:
                    counter_dict[label]["supplementary"] += 1
                else:
                    counter_dict[label]["primary"] += 1
                    counter_dict[label]["primary bases"] += read.infer_read_length()
                    if read.mapping_quality >= min_mapq:
                        counter_dict[label]["primary high mapq"] += 1

    return pd.DataFrame(counter_dict)


def _convert_sec_to_h(s):
    """
    Convert seconds to hour, minutes, secondes
    """
    s = s % (24 * 3600)
    h = s // 3600
    s %= 3600
    m = s // 60
    s %= 60
    return (int(h), int(m), int(s))


def line_profiler_parse(fn, percent_cufoff=0.1, sort_by_time=True):
    """
    Parse the output of python line_profiler and display for jupyter
    """

    # Define data header and type
    header = ["Line #", "Hits", "Time", "Time Per Hit", "% Time", "Line Contents"]
    dtypes = [int, int, float, float, float, str]
    dtypes_header = {i: j for i, j in zip(header, dtypes)}

    all_results = []

    with open(fn) as fp:
        try:
            while True:
                line = next(fp).strip()
                if line.startswith("Total time: "):
                    time = float(line.split(":")[-1].strip().split(" ")[0])
                    file = next(fp).split("/")[-1].strip()
                    function = next(fp).split(":")[-1].strip()

                    # Flush out useles lines
                    for i in range(3):
                        _ = next(fp)

                    # Parse data lines
                    data_lines = []
                    while True:
                        line = next(fp).strip()
                        if line == "":
                            break
                        # parse messy lprun lines
                        try:
                            ls = line.split()
                            parsed_line = []
                            if len(ls) >= 6:
                                for e, t in zip(
                                    ls[0:5], (int, int, float, float, float)
                                ):
                                    parsed_line.append(t(e))
                            parsed_line.append(" ".join(ls[5:]))
                            data_lines.append(parsed_line)
                        except:
                            pass

                    if data_lines:
                        df = pd.DataFrame(data=data_lines, columns=header)
                        if sort_by_time:
                            df.sort_values("% Time", inplace=True, ascending=False)
                        df = df[df["% Time"] >= percent_cufoff]
                    all_results.append(
                        {"time": time, "file": file, "function": function, "df": df}
                    )

        except StopIteration:
            if data_lines:
                df = pd.DataFrame(data=data_lines, columns=header)
                df.sort_values("% Time", inplace=True, ascending=False)
                df = df[df["% Time"] > 0]
            all_results.append(
                {"time": time, "file": file, "function": function, "df": df}
            )

        all_results.sort(key=lambda item: item.get("time"), reverse=True)
        for i in all_results:
            cprint(f"Function {i['function']} from {i['file']}", color="blue")
            h, m, s = _convert_sec_to_h(i["time"])
            cprint(f"Execution time: {h}h:{m}m:{s}s", color="red")
            display(i["df"])
