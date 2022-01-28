TEXT_LIST_URL = "https://raw.githubusercontent.com/OpenPecha-dev/editable-text/main/t_text_list.json"
NOTE_REF_NOT_FOUND_TEXT_LIST_URL = "https://raw.githubusercontent.com/OpenPecha-dev/editable-text/main/no_note_ref.json"
KANGYUR_ARCHIVE_ID = "870326402308432ba173ee3d9043224a"
TENGYUR_ARCHIVE_ID = "187ed94f85154ea5b1ac374a651e1770"

CHENYIK2EDITOR = [
    (r"\(", r"⦇"),
    (r"\)", r"⦈"),
    (r"\[", r"⟦"),
    (r"\]", r"⟧"),
    (r"\n(<?[\d༠-༩]+)>?", r"\n      (\g<1>)"),
    (r"\n\s*<s([^>]*)>\s*\n      ", r"\n\g<1>\n      "),
    (r"<p([^>]+)>", r"\n[\g<1>]"),
]

EDITOR2CHENYIK = [
    (r"\n\s*([\d༠-༩]+)\s*(\n\s+\()", r"\n<s\g<1>>\g<2>"),
    (r"\n\s+\(([\d༠-༩]+)\)", r"\n\g<1>"),
    (r"\n\s*\[([^\]]+)\]\s*$", r"\n<p\g<1>>"),  # will strips whitespaces
    (r"⦇", r"("),
    (r"⦈", r")"),
    (r"⟦", r"["),
    (r"⟧", r"]"),
]


CHENDRANG2EDITOR = [
    (r"\(", r"⦇"),
    (r"\)", r"⦈"),
    (r"\[", r"⟦"),
    (r"\]", r"⟧"),
    (r"\n<u([^>]+)>", r"\n      (\g<1>)"),
    (r"\n\s*<r([^>]*)>\s*\n      ", r"\n\g<1>\n      "),
    (r"<p([^>]+)>", r"\n[\g<1>]"),
]

EDITOR2CHENDRANG = [
    (r"\n\s*([\d༠-༩]+)\s*(\n\s+\()", r"\n<r\g<1>>\g<2>"),
    (r"\n\s+\(([^\)]+)\)", r"\n<u\g<1>>"),
    (r"\n\s*\[([^\]]+)\]\s*$", r"\n<p\g<1>>"),  # will strips whitespaces
    (r"⦇", r"("),
    (r"⦈", r")"),
    (r"⟦", r"["),
    (r"⟧", r"]"),
]
