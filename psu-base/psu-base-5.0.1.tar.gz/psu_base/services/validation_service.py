import re
from psu_base.services import error_service


def get_max_field_length(field_name, model_instance):
    if model_instance and field_name:
        try:
            return model_instance._meta.get_field(field_name).max_length
        except Exception as eee:
            error_service.record(eee)
    elif not field_name:
        error_service.record("Field name not provided for max_length lookup")
    return None


# Characters allowed in Banner name fields
allowed_name_characters = [
    " ",
    '"',
    "&",
    "'",
    "(",
    ")",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "|",
    "~",
    "À",
    "Á",
    "Â",
    "Ã",
    "Ä",
    "Å",
    "Æ",
    "Ç",
    "È",
    "É",
    "Ê",
    "Ë",
    "Ì",
    "Í",
    "Î",
    "Ï",
    "Ñ",
    "Ò",
    "Ó",
    "Ô",
    "Õ",
    "Ö",
    "Ù",
    "Ú",
    "Û",
    "Ü",
    "Ý",
    "ß",
    "à",
    "á",
    "â",
    "ã",
    "ä",
    "å",
    "æ",
    "ç",
    "è",
    "é",
    "ê",
    "ë",
    "ì",
    "í",
    "î",
    "ï",
    "ð",
    "ñ",
    "ò",
    "ó",
    "ô",
    "õ",
    "ö",
    "ù",
    "ú",
    "û",
    "ü",
    "ü",
    "ý",
    "ÿ",
    "Œ",
    "œ",
    "Š",
    "Ÿ",
    "˜",
    "–",
    "—",
]

# Disallowed characters that can be swapped with look-alike characters
special_character_replacements = {
    "\\": "/",  # Only replaced in names
    "[": "(",
    "]": ")",  # Only replaced in names
    "{": "(",
    "}": ")",  # Only replaced in names
    "¢": "c",
    "¥": "Y",
    "P": "P",
    "ƒ": "f",
    "ª": "a",
    "º": "o",
    "¬": "-",
    "½": "1/2",
    "¼": "1/4",
    "¦": "|",
    "µ": "Mu",
    "±": "+-",
    "°": "o",
    "•": ".",
    "·": ".",
    "²": "2",
    "„": '"',
    "…": "...",
    "†": "t",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "™": "TM",
    "š": "s",
    "©": "(c)",
    "®": "(R)",
    "¯": "-",
    "³": "3",
    "´": "'",
    "¸": ",",
    "¹": "1",
    "¾": "3/4",
    "Ð": "D",
    "×": "x",
    "Ø": "0",
    "÷": "/",
    "ø": "o",
}


def clean_name(name):
    """Remove non-allowed characters, doing conversions when possible"""

    name_changed = False
    if name:
        cleaned = ""
        for cc in str(name):
            if cc in allowed_name_characters:
                cleaned += cc
            elif cc in special_character_replacements:
                cleaned += special_character_replacements[cc]
                name_changed = True
            else:
                # Character is removed
                name_changed = True
        name = cleaned

    return name, name_changed


def clean_special_characters(content):
    """
    Remove non-allowed characters, doing conversions when possible
    - Less strict than clean_name()
    """
    content_changed = False
    if content:
        cleaned = ""
        for cc in str(content):
            # Allow all basic ascii characters
            if 32 <= ord(cc) <= 126:
                cleaned += cc
            # Allow any special characters allowed in names
            elif cc in allowed_name_characters:
                cleaned += cc
            # Attempt to replace other special characters
            elif cc in special_character_replacements:
                cleaned += special_character_replacements[cc]
                content_changed = True
            # Remove any other characters
            else:
                # Character is removed
                content_changed = True
        content = cleaned

    return content, content_changed


def remove_special_characters(content):
    """
    Remove all special characters from a string
    """
    content_changed = False
    if content:
        cleaned = ""
        for cc in str(content):
            # Allow all basic ascii characters
            if 32 <= ord(cc) <= 126:
                cleaned += cc
            # Remove any other characters
            else:
                # Character is removed
                content_changed = True
        content = cleaned

    return content, content_changed


def has_unlikely_characters(value, unlikely_characters="`!*=\\$%^[]{}<>;"):
    return value and any(x in value for x in unlikely_characters)


def is_term(string):
    """Is the given string a term code?"""
    if re.match(r"^20\d{2}0[1234]$", string):
        return True
    else:
        return re.match(r"^19\d{2}0[1234]$", string)


def is_psu_id(string):
    """Is the given string (likely) a PSU ID?"""
    return re.match(r"^9\d{8}$", string)
