from textwrap import wrap
from typing import Union, List, Iterable

from matplotlib.text import Text
from pandas import Series

from mpl_format.compound_types import StringMapper
from mpl_format.settings import MAX_LABEL_WIDTH

HORIZONTAL_ALIGNMENTS = ('left', 'center', 'right')
VERTICAL_ALIGNMENTS = ('top', 'center', 'bottom',
                       'baseline', 'center_baseline')


def wrap_text(text: Union[str, Text, Iterable[str], Iterable[Text]],
              max_width: int = None) -> Union[str, List[str]]:
    """
    Wrap text that exceeds a given width of characters with new lines.

    :param text: The text to wrap.
    :param max_width: The maximum character width per line.
    """
    max_chars = max_width or MAX_LABEL_WIDTH

    if isinstance(text, Text):
        text = text.get_text()

    if isinstance(text, str):
        return '\n'.join(wrap(text=text, width=max_chars))
    elif isinstance(text, Iterable):
        return [wrap_text(str(t), max_width) for t in text]
    else:
        raise ValueError(f'Cannot wrap text for type {type(text)}.')


def remove_parenthesized_text(text: Union[str, Text]) -> str:
    """
    Remove any text inside parentheses, along with the parentheses.

    :param text: The text to modify.
    """
    if isinstance(text, Text):
        text = text.get_text()

    while '(' in text and ')' in text:
        l_pos = text.index('(')
        r_pos = text.index(')')
        text = text[:l_pos] + text[r_pos + 1:]
    return text


def map_text(
        text: Union[str, Text, Iterable[str], Iterable[Text]],
        mapping: StringMapper
) -> Union[str, List[str]]:
    """
    Replace text if it matches one of the dictionary keys.

    :param text: Text instance(s) to map.
    :param mapping: Mappings to replace text.
    """
    if isinstance(text, Text):
        text = text.get_text()
    if not isinstance(text, str):
        return [map_text(str(t), mapping) for t in text]

    if mapping is None:
        return text
    if isinstance(mapping, dict) or isinstance(mapping, Series):
        if text in mapping.keys():
            return mapping[text]
        else:
            return text
    elif callable(mapping):
        return mapping(text)
    else:
        raise TypeError('mapping must be a dict or callable')
