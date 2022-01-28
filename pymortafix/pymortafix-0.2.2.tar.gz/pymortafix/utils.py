from re import findall, match, sub

from colorifix.colorifix import erase
from pymortafix._getchar import _Getch

# ---- Dictionary


def gets(dictionary, *keys, safety=True):
    """get multiple key innested dictionary"""
    for key in keys:
        dictionary = dictionary.get(key, dict() if safety else None)
    return dictionary


# ---- Substitution


def get_sub_from_matching(dictionary, matching):
    index = [i for i, group in enumerate(matching.groups()) if group]
    matched = list(dictionary)[index[0]] if index else None
    return dictionary.get(matched)


def multisub(sub_dict, string, sequential=False):
    """Infinite sub in one iteration # sub_dict: {what_to_sub:substitution}"""
    if not sequential:
        rgx = "|".join(f"({s})" for s in sub_dict.keys())
        return sub(rgx, lambda m: get_sub_from_matching(sub_dict, m), string)
    else:
        for rgx, substitution in sub_dict.items():
            string = sub(rgx, substitution, string)
        return string


# ---- Input


def strict_input(
    text, wrong_text=None, choices=None, regex=None, check=None, flush=False
):
    """Get user input with some requirements"""
    inp = input(text)
    if flush:
        erase(len(findall(r"\n", text)) + 1)
    while (
        (not choices or choices and inp not in choices)
        and (not regex or regex and not match(regex, inp))
        and (not check or check and not check(inp))
        and (choices or regex or check)
    ):
        if wrong_text:
            inp = input(wrong_text)
        else:
            inp = input(text)
        if flush:
            erase(len(findall(r"\n", wrong_text or text)) + 1)
    return inp


def direct_input(choices=None):
    """Get user single char input w/o return, with optional restricted choices"""
    inkey = _Getch()
    k = inkey()
    while (
        choices
        and (isinstance(k, str) and k or k.decode(errors="replace")) not in choices
    ):
        k = inkey()
    return isinstance(k, str) and k or k.decode(errors="replace")
