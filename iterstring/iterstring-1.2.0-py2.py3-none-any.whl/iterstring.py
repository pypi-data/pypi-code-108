"""See top level package docstring for documentation"""

import re

########################################################################

# helper functions


def numerify(x):
    """Coerce string into float or int if possible"""
    try:
        x = float(x)
        if x % 1 == 0:
            x = int(x)
    except ValueError:
        pass
    return(x)


def listr(x, lstrip=True, rstrip=True, comments=True, coerce=True):
    """Convenience function for Istr(x).to_list()"""
    return Istr(x).to_list(
        lstrip=lstrip,
        rstrip=rstrip,
        comments=comments,
        coerce=coerce,
    )


def distr(x, lstrip=True, rstrip=True, comments=True, coerce=True):
    """Convenience function for Istr(x).to_dict()"""
    return Istr(x).to_dict(
        lstrip=lstrip,
        rstrip=rstrip,
        comments=comments,
        coerce=coerce,
    )


def tlist(x, delimiter=r'\s+', comments=True, coerce=True):
    """Convenience function for TokenStr(x).to_list()"""
    return TokenList(x).to_list(
        delimiter=delimiter,
        comments=comments,
        coerce=coerce,
    )


########################################################################


class Istr(str):
    """
    String (str) subclass that adds to_list and to_dict convenience methods

    - By default, strip whitespace from left and right of each item
    - By default, coerce items to numbers where possible (see coerce)
    - Iterating over the object treats it like a list
    - Indexing the object treats it like a dictionary
    - For dictionaries, When keys clash, the last one wins
    - dict(Istr) does NOT work (dict makes assumptions about the iterable)
        - list(Istr) and list comprehensions work fine
    - to_list() and to_dict() reprocess the string every time
        - So listr and sistr may be more efficient and predictable

    Examples
    --------

    >>> from iterstring import listr # or distr

    A simple use case:

    >>> some_list = listr('''
    item one # with a comment
      2
    three
    ''')
    >>> some_list
    ['item one', 2, 'three']
    >>> type(some_list)
    <class 'list'>

    Using the class directly:

    >>> from iterstring import Istr
    >>> asdf = Istr('''
    item one # with a comment
      2
    three
    ''')
    >>> asdf.to_list()
    ['item one', 2, 'three']
    >>> type(asdf)
    <class 'iterstring.Istr'>

    >>> [x for x in asdf]
    ['item one', 2, 'three']

    >>> fdsa = Istr('''
    item one # with a comment
      2 some other value
    key3 3.14159
    ''')
    >>> asdf.to_dict()
    {'item': 'one', 2: 'some other value', 'key3': 3.14159}
    >>> asdf.to_dict(coerce=False)
    {'item': 'one', '2': 'some other value', 'key3': '3.14159'}

    Methods
    -------
    to_list(lstrip=True, rstrip=True, comments=True, coerce=True)
        Create line-based list representation of string
    to_dict(lstrip=True, rstrip=True, comments=True, coerce=True)
        Create line-based dictionary representation of string
    """

    def to_list(self, lstrip=True, rstrip=True, comments=True, coerce=True):
        """Create a list using each line as an item"""
        lines = self.split("\n")
        if comments:
            # strip out comments
            lines = [re.sub(r'#.*', '', x) for x in lines]
        if lstrip:
            # remove leading whitespace
            lines = [x.lstrip() for x in lines]
        if rstrip:
            # remove trailing whitespace
            lines = [x.rstrip() for x in lines]
        # remove empty lines
        lines = list([x for x in lines if not re.match(r'^\s*$', x)])
        if coerce:
            # convert values to numeric types where that makes sense
            lines = [numerify(x) for x in lines]
        return lines

    def to_dict(self, lstrip=True, rstrip=True, comments=True, coerce=True):
        """Create a dictionary using the first token of each line as key"""
        lines = self.to_list(
            lstrip=lstrip,
            rstrip=rstrip,
            comments=comments,
            coerce=False,
        )
        # split each item into tupe of first token and remaining tokens
        lines = [(lambda x: tuple(re.split(r'\s+', x, 1)))(i) for i in lines]
        # create a disctionary out of the list of tuples
        kv = {k: v for k, v in lines}
        if coerce:
            # convert keys, values to numeric types where that makes sense
            kv = {numerify(k): numerify(v) for k, v in lines}
        return kv

    def __iter__(self):
        return iter(self.to_list())

    def __next__(self):
        return self.to_list().__next__()

    def __getitem__(self, i):
        return self.to_dict()[i]

    def __len__(self):
        return len(self.to_list())


class TokenList(str):
    """
    """
    def to_list(self, delimiter=r'\s+', comments=True, coerce=True):
        lines = self.split("\n")
        if comments:
            # strip out comments
            lines = [re.sub(r'#.*', '', x) for x in lines]
        text = ' '.join(lines)
        tokens = re.split(delimiter, text)
        # drop empty strings
        tokens = [x for x in tokens if not re.search(r'^\s*$', x)]
        if coerce:
            # convert values to numeric types where that makes sense
            tokens = [numerify(x) for x in tokens]
        return tokens

    def __iter__(self):
        return iter(self.to_list())

    def __next__(self):
        return self.to_list().__next__()

    def __len__(self):
        return len(self.to_list())
