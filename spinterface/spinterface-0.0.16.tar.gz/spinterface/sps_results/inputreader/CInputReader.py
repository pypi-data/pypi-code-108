r"""
Input reader for input files in the style of the spinaker code.
"""
from pathlib import Path
from typing import Union, List, Any, Dict


class CInputReader:
    r"""
    Class for reading input files with the style of spinaker code. The keywords are separated from the values by a
    white space. Several values may follow a key. The default comment character is the #.
    """

    def __init__(self, fpath: Union[Path, str], commentchar: str = '#') -> None:
        r"""
        Args:
            fpath(Path,str): path to input file
        """
        self._fpath = fpath
        self._commentchar = commentchar
        self._fcontent = self._loadfilecontent()

    def _loadfilecontent(self) -> Dict[str, List]:
        r"""
        Loads the content of the file ignoring the lines with comment char.

        Returns:
            A dictionary containing the key value pairs of the input file. As there could be more than one value assigned
            to each key the values are represented by a list.
        """
        fcontent = {}
        with open(self._fpath) as f:
            for line in f:
                if line == '\n':
                    continue
                line_stripped = line.strip()
                if line_stripped.startswith(self._commentchar):
                    continue
                # remove trailing comments from line
                line_key_value = line_stripped.split(self._commentchar, 1)[0]
                line_splitted = line_key_value.split()
                # assume that the key is the first entry in each line
                currentkey = str(line_splitted[0])
                currentvalues = [str(val) for val in line_splitted[1:]]
                # convert bool values from fortran style into python style
                fcontent[currentkey] = currentvalues
        return fcontent

    @property
    def content(self) -> Dict[str, List]:
        r"""
        Returns:
            content of the input file
        """
        return self._fcontent
