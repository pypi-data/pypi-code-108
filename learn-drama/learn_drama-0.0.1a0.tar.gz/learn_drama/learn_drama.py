"""Main module."""

from xml.dom import minidom
import numpy as np
import pandas as pd
import warnings

from learn_drama.text_helper import check_line_break_string  # noqa: F401


class DramaLearner:
    """DramaLerner Object to help learning a text having verses and stanzas

    Args:
      textinput: Default="", text input to be processed to help learning.
      f:         Default="", file input with text to be processed for learning.

    Returns:
      DramaLearner Object

    Notes:
      - If both textinput and f are given, the file input f will only be used.
      - xml files are expected in special textgridlab.org (Faust-) format.
    """
    def __init__(self, text_input="", f=""):
        self._notes = ""
        if f != "":
            if text_input != "":
                warn = "Text and file input given. Will only use file input."
                warnings.warn(warn)
            if f[-4:] == ".xml":
                document = minidom.parse(f)
                df = pd.DataFrame()
                lements = np.array(document.getElementsByTagName('l'))
                page_break_str = '\n                                          '
                df['verses'] = [el.firstChild.data
                                if page_break_str not in el.firstChild.data
                                else check_line_break_string(el.lastChild.data)
                                for el in lements]
                df['xml_id'] = [el.getAttribute('xml:id') for el in lements]
                self.raw_text = "\n".join(df.verses)
            else:
                self.__read(f)
        else:
            self.raw_text = text_input

    def formatted_text(self):
        """Formats text input into lines preceded by descending
        numbers - verses. Verses are lines seperated by a line break.

        Args:

        Returns:
          str: Formatted string

        Example:
           drama_learner_object_instance.formatted_text() with
           self.raw_text == "One\nTwo" gives "1 One\n2 Two"
        """
        enumerate_line_break =\
            enumerate(self.raw_text.split("\n"), start=1)
        """
        The longest line of books is 30,097,[...]",
        https://www.guinnessworldrecords.com/world-records/118599-longest-line-of-books
        Therefore max width for verses about 5.
        """
        numbered_lines = [
                "{:>6} {}".format(str(nr), line) for nr, line
                in enumerate_line_break
                ]
        return "\n".join(map(str, numbered_lines))

    def __read(self, f):
        """Simple reading method to store content of file in self_raw_text.

        Args:
          f (str): File name as string

        Returns:
        """
        file = open(f, 'r')
        self.raw_text = file.read()
