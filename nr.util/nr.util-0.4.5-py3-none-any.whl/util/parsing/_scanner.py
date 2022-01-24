
"""
Provides the #Scanner class which is convenient for scanning through items of a sequence; such as characters
in a text.
"""

import enum
import re
import typing as t


class Cursor(t.NamedTuple):
  offset: int
  line: int
  column: int


class Seek(enum.Enum):
  SET = enum.auto()
  CUR = enum.auto()
  END = enum.auto()


class Scanner:
  """
  A convenient class for scanning through items of a sequence; such as characters in a text.
  """

  def __init__(self, text: str) -> None:
    self.text = text
    self.index = 0
    self.lineno = 1
    self.colno = 0

  def __repr__(self) -> str:
    return f'<Scanner at {self.lineno}:{self.colno}>'

  def __bool__(self) -> bool:
    return self.index < len(self.text)

  @property
  def pos(self) -> Cursor:
    return Cursor(self.index, self.lineno, self.colno)

  @pos.setter
  def pos(self, cursor: Cursor) -> None:
    """ Moves the scanner back (or forward) to the specified cursor location. """

    if not isinstance(cursor, Cursor):
      raise TypeError(f'expected Cursor object {type(cursor).__name__}')
    self.index, self.lineno, self.colno = cursor

  @property
  def char(self) -> str:
    """ Returns the current character. Returns an empty string at the end of the text. """

    if self.index >= 0 and self.index < len(self.text):
      return self.text[self.index]
    else:
      return type(self.text)()

  def seek(self, offset: int, mode: t.Union[str, Seek] = Seek.SET) -> None:  # NOSONAR
    """
    Moves the cursor of the Scanner to or by *offset* depending on the *mode*. The method is
    similar to a file's `seek()` method, but ensures that the line and column counts are tracked
    correctly.
    """

    if isinstance(mode, str):
      mode = Seek[mode.upper()]

    if mode not in Seek:
      raise ValueError(f'invalid mode: {mode!r}')

    # Translate the other modes into the 'set' mode.
    if mode == Seek.END:
      offset = len(self.text) + offset
      mode = Seek.SET
    elif mode == Seek.CUR:
      offset = self.index + offset
      mode = Seek.SET
    assert mode == Seek.SET

    if offset < 0:
      offset = 0
    elif offset > len(self.text):
      offset = len(self.text) + 1

    if self.index == offset:
      return

    # Update line/column counts. Figure which path is shorter:
    # 1) Start counting from the beginning of the file,
    if offset <= abs(self.index - offset):
      text, index, lineno, colno = self.text, 0, 1, 0
      while index != offset:
        # Find the next newline in the string.
        nli = text.find('\n', index)
        if nli >= offset or nli < 0:
          colno = offset - index
          index = offset
          break
        else:
          colno = 0
          lineno += 1
          index = nli + 1

    # 2) or step from the current position of the cursor.
    else:
      text, index, lineno, colno = self.text, self.index, self.lineno, self.colno

      if offset < index:  # backwards
        while index != offset:
          nli = text.rfind('\n', 0, index)
          if nli < 0 or nli <= offset:
            if text[offset] == '\n':
              assert (offset - nli) == 0, (offset, nli)
              nli = text.rfind('\n', 0, index-1)
              lineno -= 1
            colno = offset - nli - 1
            index = offset
            break
          else:
            lineno -= 1
            index = nli - 1
      else:  # forwards
        while index != offset:
          nli = text.find('\n', index)
          if nli < 0 or nli >= offset:
            colno = offset - index
            index = offset
          else:
            lineno += 1
            index = nli + 1

    assert lineno >= 1
    assert colno >= 0
    assert index == offset
    self.index, self.lineno, self.colno = index, lineno, colno

  def next(self) -> str:
    """ Move on to the next character in the text. """

    char = self.char
    if char == '\n':
      self.lineno += 1
      self.colno = 0
    else:
      self.colno += 1
    self.index += 1
    return self.char

  def readline(self) -> str:
    """ Reads a full line from the scanner and returns it. """

    start = end = self.index
    while end < len(self.text):
      if self.text[end] == '\n':
        end += 1
        break
      end += 1
    result = self.text[start:end]
    self.index = end
    if result.endswith('\n'):
      self.colno = 0
      self.lineno += 1
    else:
      self.colno += end - start
    return result

  def match(self, regex: t.Union[str, 're.Pattern'], flags: int = 0, *,
      _search: bool = False) -> t.Optional[t.Match[str]]:
    """
    Matches the *regex* from the current character of the *scanner* and returns the result. The
    scanners column and line numbers are updated respectively.
    """

    if isinstance(regex, str):
      regex = re.compile(regex, flags)
    match = (regex.search if _search else regex.match)(self.text, self.index)
    if not match:
      return None
    start, end = match.start(), match.end()
    if not _search:
      assert start == self.index
    else:
      start = self.index
    lines = self.text.count('\n', start, end)
    self.index = end
    if lines:
      self.colno = end - self.text.rfind('\n', start, end) - 1
      self.lineno += lines
    else:
      self.colno += end - start
    return match

  def search(self, regex: t.Union[str, 're.Pattern'], flags: int = 0) -> t.Optional['re.Match']:
    """
    Performs a regex search from the current position of the scanner. Note that searching in the
    scanner will potentially have you skip characters without consuming them.
    """

    return self.match(regex, flags, _search=True)

  def getmatch(self, regex: t.Union[str, 're.Pattern'], group: t.Union[int,str] = 0,
      flags: int = 0) -> t.Optional[str]:
    """
    The same as #Scanner.match(), but returns the captured group rather than
    the regex match object, or None if the pattern didn't match.
    """

    match = self.match(regex, flags)
    if match:
      return match.group(group)
    return None

  def getline(self, cursor: Cursor) -> str:
    """ Returns the contents of the current line marked by the specified cursor location. """

    start = cursor.offset - cursor.column
    end = self.text.find('\n', start)
    if end < 0:
      end = len(self.text)
    return self.text[start:end]
