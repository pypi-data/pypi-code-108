# -*- coding: utf-8 -*-
"""Created on some day of 2018 or 2019.

@author: cottephi@gmail.com
"""

import os
import shutil
import time
import tempfile
from pathlib import Path
from typing import Any, Dict, TypeVar, Union, Optional

import pandas as pd

T = TypeVar("T")
DONE = "  ...done"
LATEX_TEXT_COLOR = r"\textcolor{"


class TableWriter(object):
    """Class used to produce a ready-to-compile .tex file containing a table from a pandas or dask DataFrame object.
    Can also compile the .tex to produce a .pdf.

    Handles using additional latex packages through the *packages* argument. The given DataFrame is copied so any
    modification of the  said DataFrame after instensiation of the TableWriter object has no effect on the
    TableWriter object, and vice-versa.
    You should not however modify the DataFrame contained in the TableWriter object, you should just create the
    TableWriter once you are sure that your DataFrame is ready.

    TableWriter uses pandas.DataFrame.to_latex and adds some more options to produce the .tex and the .pdf. Any
    option that must be given to the to_latex method can be given to TableWriter through the *to_latex_args*
    argument.

    Note that the content of the DataFrame will be converted to string. If the DataFrame contains one the following
    characters ("$", "_", "^", "%", "&"), a '\' is put before them.
    Mathmode using '$' is handled.

    Examples
    --------

    >>> from tablewriter import TableWriter  # doctest: +SKIP
    >>> # noinspection PyShadowingNames
    >>> import pandas as pd  # doctest: +SKIP
    >>> df = pd.DataFrame(columns=["$x$", "$x^2$"],  # doctest: +SKIP
    >>>                   index=["$A_{00}$", "$A_{01}$"], data=[[2, 4], [3, 9]])  # doctest: +SKIP
    >>> table = TableWriter(df, path="ouput")  # doctest: +SKIP
    >>> table.compile()  # doctest: +SKIP

    TableWriter will use os.system('pdflatex ...') to create the pdf, so you need a working installation of it.
    In order not to flood the stdout with pdflatex ouput, which is quite verbose, it is silenced by default. If the
    compilation fails TableWriter will return 'ValueError: Failed to compile pdf'. In that case, you can try to
    recompile if using

    >>> table.compile(silenced=False)  # doctest: +SKIP

    To have the full output and try to understand what went wrong.

    By default, all files produced by LaTeX are deleted except the .tex and the .pdf. You can change this default
    behavior :

    >>> # To keep all files :  # doctest: +SKIP
    >>> table.compile(clean=False)  # doctest: +SKIP
    >>> # Or on the contrary, to remove also .tex :  # doctest: +SKIP
    >>> table.compile(clean_tex=True)  # doctest: +SKIP

    You can also do a compilation that will reuse the .tex file if it already exists:

    >>> table.compile(recreate=False)

    Here is a more complete example of table generation :

    >>> from tablewriter import TableWriter  # doctest: +SKIP
    >>> # noinspection PyShadowingNames
    >>> import pandas as pd  # doctest: +SKIP
    >>> df = pd.DataFrame(columns=["$x$", "$x^2$"], index=["$A_{00}$", "$A_{01}$"],    # doctest: +SKIP
    >>>                   data=[["2", "$2^2$"], ["3", "$3^2$"]])  # doctest: +SKIP
    >>> table = TableWriter(  # doctest: +SKIP
    >>>     path="path_output",  # doctest: +SKIP
    >>>     data=df,  # doctest: +SKIP
    >>>     to_latex_args={"column_format": "lr"},  # doctest: +SKIP
    >>>     label="tab::example",  # doctest: +SKIP
    >>>     caption="TableWriter example",  # doctest: +SKIP
    >>>     packages={"inputenc": {"T1": ""}},  # doctest: +SKIP
    >>>     hide_numbering=True
    >>> )  # doctest: +SKIP
    >>> table.compile()  # doctest: +SKIP

    """

    # //////////////////
    # // Initialisers //
    # //////////////////

    # noinspection PyUnresolvedReferences
    def __init__(
        self,
        path_output: Optional[Union[str, Path, "TransparentPath"]] = None,
        data: Optional[Union[pd.DataFrame, "dask.dataframe.DataFrame"]] = None,
        path_input: Optional[Union[str, Path, "TransparentPath"]] = None,
        to_latex_args: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
        caption: Optional[str] = None,
        packages: Dict[str, Union[None, Dict[str, Union[None, str]]]] = None,
        read_from_file_args: Dict = None,
        paperwidth: Union[int, float] = 0,
        paperheight: Union[int, float] = 0,
        number: int = 1,
        hide_numbering: bool = False,
    ):
        """All parameters are optionnal and can be modified by dedicated
        setters.

        Parameters
        ----------
        path_output: Union[str, Path, TransparentPath]
            Path to the .tex file to create. If the path's suffix is not .tex, it will be changed to .tex.
            You can set this path later using mytable.path = ... or mytable.path_output = ...
            (Default value = None)
        data: Union[pd.DataFrame, dask.dataframe.DataFrame]
            Data to transform to table. Can not be specified alongside path_input. (Default value = None)
        path_input: Union[str, Path, TransparentPath]
            Path to the file to use to read the DataFrame from. Can not be specified alongside data.
            (Default value = None)
        to_latex_args: Dict[str, Any]
            Dict of arguments to give to the DataFrame.to_latex method. See valid arguments at
            https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_latex.html
            (Default value = None)
        label: str
            Label to use for the table (callable by LateX's \\ref)
            (Default value = None)
        caption: str
            Caption to use for the table
            (Default value = None)
        packages: Dict[str, Dict[str, str]]
            Packages to use. Keys of first dict are the package names. values are dict of option: value options to
            use with the package. Can be empty if no options are to be specified.
            (Default value = None)
        read_from_file_args: Dict
            Dict of argument to pass to the read method.
        paperwidth: Union[int, float]
            Width of the output table in the pdf. If 0, TableWriter will try to guess a default value from table
            content, but that is not very accurate. (Default value = 0)
         paperheight: Union[int, float]
            Height of the page of the output pdf. If table is too long to fit on the page, it will be split in
            several pages using longtable package. (Default value = 0)
         number: int
            Number LateX should show after 'Table'.  (Default value = 1)
         hide_numbering: bool
            Do not show 'Table N' in the caption. (Default value = False)
        """

        if data is None and path_input is None:
            raise ValueError("You must give data or path_input argument.")
        if data is not None and path_input is not None:
            raise ValueError("You must give data or path_input argument, but not both.")

        if path_input is not None:
            if read_from_file_args is None:
                read_from_file_args = {}
            if type(path_input) == str:  # Do not use isinstance because isinstance(TransparentPath, str) is True
                path_input = Path(path_input)
            if "read" in dir(path_input):
                data = path_input.read(**read_from_file_args)
            elif path_input.suffix == ".csv":
                data = pd.read_csv(path_input, **read_from_file_args)
            elif path_input.suffix == ".parquet":
                data = pd.read_parquet(path_input, **read_from_file_args)
            else:
                raise ValueError(f"Can not read file {path_input} : unsupported extension.")

        if "dask.dataframe" in str(type(data)):
            data = data.head(len(data.index))

        if data is not None and not isinstance(data, pd.DataFrame):
            raise ValueError(f"Data must be a DataFrame, got {type(data)}")

        if packages is None:
            packages = {}
        if to_latex_args is None:
            to_latex_args = {}

        self.header = ""
        self.body = "\\begin{document}\\end{document}"
        self.footer = ""

        self.data = data
        self.to_latex_args = to_latex_args
        self.__path = path_output
        self.label = label
        self.caption = caption
        self.packages = packages

        self.paperwidth, self.paperheight = None, None
        self._get_dimensions(paperwidth, paperheight)
        self.number = number
        self.hide_numbering = hide_numbering

        self.special_char = ["_", "^", "%", "&"]

        if self.caption is not None:
            self.to_latex_args["caption"] = self.caption
        if self.label is not None:
            self.to_latex_args["label"] = self.label
        if "column_format" not in self.to_latex_args:
            if isinstance(self.data.index, pd.MultiIndex):
                self.to_latex_args["column_format"] = (
                    "|" + self.data.index.nlevels * "l" + "|" + len(self.data.columns) * "c" + "|"
                )
            else:
                self.to_latex_args["column_format"] = "|l|" + len(self.data.columns) * "c" + "|"
        if "escape" not in self.to_latex_args:
            self.to_latex_args["escape"] = True
        if "longtable" not in self.to_latex_args:
            self.to_latex_args["longtable"] = True

        if "geometry" not in self.packages:
            self.packages["geometry"] = {}
        if "marging" not in self.packages["geometry"]:
            self.packages["geometry"]["margin"] = "0.5cm"
        if "paperwidth" not in self.packages["geometry"]:
            self.packages["geometry"]["paperwidth"] = f"{str(self.paperwidth)}cm"
        if "paperheight" not in self.packages["geometry"]:
            self.packages["geometry"]["paperheight"] = f"{str(self.paperheight)}cm"
        if "caption" not in self.packages:
            self.packages["caption"] = {}
        if "xcolor" not in self.packages:
            self.packages["xcolor"] = {"dvipsnames": None}
        if "booktabs" not in self.packages:
            self.packages["booktabs"] = {}
        if "inputenc" not in self.packages:
            self.packages["inputenc"] = {"utf8": None}
        if "longtable" not in self.packages and self.to_latex_args["longtable"] is True:
            self.packages["longtable"] = {}

        if isinstance(self.number, str):
            self.number = int(self.number)
        if self.number > 0:
            self.number -= 1
        self.number = str(int(self.number))

        if self.__path is not None:
            if type(self.__path) == str:
                self.__path = Path(self.__path)
            if self.__path.suffix != ".tex":
                self.__path = self.__path.with_suffix(".tex")

    # noinspection PyUnresolvedReferences
    @property
    def path(self) -> Union[Path, "TransparentPath"]:
        return self.__path

    # noinspection PyUnresolvedReferences
    @property
    def path_output(self) -> Union[Path, "TransparentPath"]:
        return self.__path

    # noinspection PyUnresolvedReferences
    @path.setter
    def path(self, apath: Union[str, Path, "TransparentPath", None]):
        if type(apath) == str:
            if self.__path is not None:
                apath = type(self.__path)(apath)
            else:
                apath = Path(apath)
        if apath.suffix != ".tex":
            apath = apath.with_suffix(".tex")
        self.__path = apath

    # noinspection PyUnresolvedReferences
    @path_output.setter
    def path_output(self, apath: Union[str, Path, "TransparentPath", None]):
        self.path = apath

    # ////////////
    # // Makers //
    # ////////////

    def _get_dimensions(self, paperwidth, paperheight):

        self.paperwidth = paperwidth
        self.paperheight = paperheight

        # Try to guess a kind of optimal width for the table
        if not self.data.empty and self.paperwidth == 0:

            charswidth = (
                len("".join(list(self.data.columns.dropna().astype(str)))) + max([len(str(e)) for e in self.data.index])
            ) * 0.178
            self.paperwidth = charswidth + 0.8 * (len(self.data.columns)) + 1
            if self.paperwidth < 9:
                self.paperwidth = 9
        # Same for height
        if not self.data.empty and self.paperheight == 0:
            self.paperheight = 3.5 + (len(self.data.index)) * 0.45
            if self.paperheight < 4:
                self.paperheight = 4
            if self.paperheight > 24:
                # Limit page height to A4's 24 cm
                self.paperheight = 24
                self.to_latex_args["longtable"] = True
            else:
                self.to_latex_args["longtable"] = False

    def _make_header(self) -> None:
        """Makes the header of the tex file."""

        self.header = "\\documentclass{article}\n"

        # Add specified packages if any
        for p in self.packages:
            if len(self.packages[p]) == 0:
                self.header += p.join(["\\usepackage{", "}\n"])
            else:
                self.header += "\\usepackage["
                for o in self.packages[p]:
                    if self.packages[p][o] is None:
                        self.header += o + ","

                    else:
                        self.header += o + "=" + self.packages[p][o] + ","
                self.header = self.header[:-1] + "]{" + p + "}\n"
        self.header += "\\begin{document}\n\\nonstopmode\n\\setcounter{table}{" + self.number + "}\n"

    def _make_body(self) -> None:
        """Makes the main body of tex file."""

        # Needed if you do not want long names to be truncated with "..."
        # by pandas, giving bullshit results in the .tex file
        def_max_col = pd.get_option("display.max_colwidth")
        if pd.__version__.split(".")[0] == "0":
            # pandas is older than 1.0.0
            pd.set_option("display.max_colwidth", -1)
        else:
            # pandas is 1.0.0 or newer
            pd.set_option("display.max_colwidth", None)

        if self.data.empty:
            self.body = self.caption + ": Empty Dataframe\n"
            return
        else:
            self.body = self.data.to_latex(**self.to_latex_args)
        pd.set_option("display.max_colwidth", def_max_col)

        if self.caption is not None and self.hide_numbering:
            self.body = self.body.replace("\\caption{", "\\caption*{")

        # if self.caption is not None or self.label is not None:
        #     self.body = self.body.replace("\n\\toprule", "\\\\\n\\toprule")
        self.body = self.body.replace("\\\\\\\\", "\\\\")

    def _make_footer(self) -> None:
        """Makes the footer of tex file."""

        self.footer = "\\end{document}\n"

    def _escape_special_chars(self, s: T) -> T:
        """Will add '\\' before special characters outside of mathmode to given
        string.

        Parameters
        ----------
        s: T
            If s is not a string, will return it without changing anything

        Returns
        -------
        T
            String with special char escaped, or unmodified non-string object
        """

        if not isinstance(s, str):
            return s
        in_math = False
        previous_c = ""
        s2 = ""
        for c in s:
            if c == "$":
                in_math = not in_math
            if in_math:
                s2 += c
                previous_c = c
                continue
            if c in self.special_char and not previous_c == "\\":
                c = "\\" + c
            previous_c = c
            s2 += c
        return s2

    # //////////////////
    # // Output files //
    # //////////////////

    def build(self):
        """build header body and footer."""
        if "escape" in self.to_latex_args and self.to_latex_args["escape"]:
            if isinstance(self.data.index, pd.MultiIndex):
                names = [self._escape_special_chars(s) for s in self.data.index.names]
                # noinspection PyTypeChecker
                self.data.index = pd.MultiIndex.from_tuples(
                    [[self._escape_special_chars(s) for s in l_] for l_ in self.data.index]
                )
                self.data.index.names = names
            else:
                name = self._escape_special_chars(self.data.index.name)
                self.data.index = [self._escape_special_chars(s) for s in self.data.index]
                self.data.index.name = name
            if isinstance(self.data.columns, pd.MultiIndex):
                self.data.columns = [[self._escape_special_chars(s) for s in l_] for l_ in self.data.columns]
            else:
                self.data.columns = [self._escape_special_chars(s) for s in self.data.columns]
            self.data = self.data.applymap(self._escape_special_chars)
        self.to_latex_args["escape"] = False
        self._make_header()
        self._make_body()
        self._make_footer()

    def create_tex_file(self) -> None:
        """Creates the tex file."""

        with open(self.__path, "w") as outfile:
            # escape argument only works on column names. We need to apply
            # it on entier DataFrame, so do that then set it to False
            self.build()
            outfile.write(self.header)
            outfile.write(self.body)
            outfile.write(self.footer)

    # noinspection StandardShellInjection
    def compile(
        self,
        silenced: bool = True,
        recreate: bool = True,
        clean: bool = True,
        clean_tex: bool = False,
    ) -> None:
        """Compile the pdf.

        Parameters
        ----------
        silenced: bool
            Will or will not print on terminal the pdflatex output. (Default value = True)
        recreate: bool
            If False and .tex file exists, compile from it. If True, recreate the .tex file first.
        clean: bool
            Removes all files created by the compilation which are not the .tex or the .pdf file.
        clean_tex: bool
            Also removes the .tex file, leaving only the .pdf.

        Returns
        -------
        None
        """

        if self.__path is None:
            raise ValueError("Must specify a file path.")
        if recreate or not self.__path.is_file():
            self.create_tex_file()

        if not self.__path.is_file():
            raise ValueError(f"Tex file {self.__path} not found.")

        path_to_compile = self.__path
        # noinspection PyUnresolvedReferences
        if "fs_kind" in dir(self.__path) and "gcs" in self.__path.fs_kind:  # Using TransparentPath on gcs
            path_to_compile = tempfile.NamedTemporaryFile(delete=False, suffix=".tex")
            path_to_compile.close()
            # noinspection PyUnresolvedReferences
            self.__path.get(path_to_compile.name)
            path_to_compile = type(self.__path)(path_to_compile.name, fs="local")

        command = "pdflatex -synctex=1 -interaction=nonstopmode "
        parent = path_to_compile.parent
        if parent != ".":
            command = f'{command} -output-directory="{parent}"'

        command = f'{command} "{path_to_compile}"'
        if silenced:  # unix
            if os.name == "posix":
                command = f"{command} > /dev/null"
            else:  # windows
                command = f"{command} > NUL"
        x1 = os.system(command)
        time.sleep(0.5)
        x2 = os.system(command)
        time.sleep(0.5)
        x3 = os.system(command)

        # noinspection PyUnresolvedReferences
        if "fs_kind" in dir(self.__path) and "gcs" in self.__path.fs_kind:
            glob_in = path_to_compile.parent
            for path in glob_in.glob(f"{path_to_compile.stem}*"):
                path_gcs = self.__path.with_suffix(path.suffix)
                # noinspection PyUnresolvedReferences
                path.put(path_gcs)
                # noinspection PyUnresolvedReferences
                path.rm()

        if x1 != 0 or x2 != 0 or x3 != 0:
            raise ValueError("Failed to compile pdf")

        if clean:
            self.clean(clean_tex)

    def clean(self, clean_tex: bool = False) -> None:
        """Clean files produced by latex. Also remove .tex if clean_tex is
        True.

        Parameters
        ---------
        clean_tex: bool
            To also remove the .tex file

        Returns
        -------
        None
        """
        to_keep = [".pdf", ".csv", ".excel"]
        if not clean_tex:
            to_keep.append(".tex")
        files = self.__path.parent.glob(f"{self.__path.stem}*")
        for f in files:
            if f.suffix not in to_keep:
                if f.is_file():
                    f.unlink()
                elif "rm" in dir(f):
                    # noinspection PyUnresolvedReferences
                    f.rm()
                else:
                    shutil.rmtree(f)


def remove_color(obj: str) -> str:
    """Remove coloration of given object.

    Parameters
    ----------
    obj: str
        The object from which to remove the color

    Return
    ------
    str
        Object without color
    """

    if LATEX_TEXT_COLOR not in obj:
        return obj
    to_find = LATEX_TEXT_COLOR
    before_color = obj[: obj.find(to_find)]
    after_color = obj[obj.find("textcolor") + 10:]
    no_color = after_color[after_color.find("{") + 1:].replace("}", "", 1)
    return before_color + no_color


def set_color(obj: Any, color: str) -> str:
    """Add color to a given object.

    Parameters
    ----------
    obj : Any
        The object to which color must be added.
    color: str
        Must be a valid LateX color string

    Return
    ------
    str
        "\\textcolor{color}{str(obj)}"
    """
    if pd.isna(obj):
        return obj
    return LATEX_TEXT_COLOR + color + "}{" + str(obj) + "}"


# noinspection PyTypeChecker
def set_color_dataframe(
    df: Union[pd.DataFrame, pd.Series],
    color: str,
    color_index: bool = False,
    color_columns: bool = False,
) -> Union[pd.DataFrame, pd.Series]:
    r"""Sets color for the entier DataFrame's or Series's entries.

    To change the color of some elements in the dataframe under some condition

    Parameters
    ----------
    df: Union[pd.DataFrame, pd.Series]
        The DataFrame or Series to change the colors of
    color: str
        LateX-recognized color string
        Default ''
    color_index: bool
        To color the index too
        Default False.
    color_columns: str
        To color the columns (or Series name if df is a Series) too
        Default False.
    color_index: bool
        whether to color index or not
    color_columns: bool
        whether to color columns or not

    Returns
    -------
    Union[pd.DataFrame, pd.Series]
        Colored DataFrame or Series (dtype will be str)

    Examples
    --------

    dff = dff.mask(dff < 0, TableWriter.set_color_dataframe(dff, "red"))
    dff = pd.DataFrame(columns=dff.columns, index=dff.index, data=dff.values.astype(str))
    dff = dff.mask(dff == "nan", "")
    writer = TableWriter(data=dff)

    """
    if isinstance(df, pd.DataFrame):
        df_c = df.applymap(lambda x: set_color(x, color))
    else:
        df_c = df.apply(lambda x: set_color(x, color))
    if color_index:
        df_c.index = [set_color(x, color) for x in df_c.index]
    if color_columns:
        if isinstance(df, pd.DataFrame):
            df_c.columns = [set_color(x, color) for x in df_c.columns]
        else:
            df_c.name = set_color(df_c.name, color)
    return df_c
