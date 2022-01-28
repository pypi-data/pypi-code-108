# coding='utf-8'
import re

from antx import transfer
from openpecha.utils import download_pecha

from pedurma.texts import get_hfml_text
from pedurma.utils import get_pages


def rm_ann(text, anns):
    result = text
    for ann in anns:
        result = re.sub(ann, "", result)
    return result


def is_note_page(g_page, dg_page):
    if (len(g_page) - len(dg_page) > 1000) or re.search("<d", g_page):
        return True
    else:
        return False


def get_derge_google_text(derge_hfml, google_hfml):
    derge_google_text = ""
    anns = [r"\n", r"\[\w+\.\d+\]", r"\[[𰵀-󴉱]?[0-9]+[a-z]{1}\]"]
    derge_hfml = rm_ann(derge_hfml, anns)
    dg_body = transfer(
        google_hfml,
        [["linebreak", r"(\n)"], ["pg_ann", r"(\[[𰵀-󴉱]?[0-9]+[a-z]{1}\])"]],
        derge_hfml,
        output="txt",
    )
    dg_pages = get_pages(dg_body)
    g_pages = get_pages(google_hfml)
    for g_page, dg_page in zip(g_pages, dg_pages):
        if is_note_page(g_page, dg_page):
            derge_google_text += g_page
        else:
            derge_google_text += dg_page
    return derge_google_text


def get_derge_hfml_text(text_id):
    derge_pecha_id = "P000002"
    derge_opf_path = download_pecha(derge_pecha_id, needs_update=False)
    derge_text = get_hfml_text(derge_opf_path / f"{derge_pecha_id}.opf", text_id)
    return derge_text


def put_derge_line_break(preview_text, derge_text):
    collation_text = ""
    for vol_id, text in preview_text.items():
        collation_text += re.sub("<p.+?>", "", text)
    full_derge_text = ""
    for vol_id, vol_text in derge_text.items():
        full_derge_text += vol_text
    anns = [r"\n"]
    collation_text = rm_ann(collation_text, anns)
    collation_text_with_derge_linebr = transfer(
        full_derge_text,
        [["linebreak", r"(\n)"], ["pg_ann", r"(\[[𰵀-󴉱]?[0-9]+[a-z]{1}\])"]],
        collation_text,
        output="txt",
    )
    return collation_text_with_derge_linebr


def derge_page_increment(p_num):
    sides = {"a": "b", r"b": "a"}
    page, side = int(p_num[1:-2]), p_num[-2:-1]

    # increment
    if side == "b":
        page += 1
    side = sides[side]

    return f"[{page}{side}]"


def preprocess_google_notes(text):
    """
    this cleans up all note markers
    :param text: plain text
    :return: cleaned text
    """
    patterns = [
        # delete tibetan numbers
        # ['[༠-༩]', ''],
        # normalize punct
        [r"\r", r"\n"],
        [r"༑", r"།"],
        [r"།།", r"། །"],
        [r"།་", r"། "],
        # normalize edition marks «<edition>»
        [r"〈〈?", r"«"],
        [r"〉〉?", r"»"],
        [r"《", r"«"],
        [r"》", r"»"],
        [r"([ཀགཤ།]) །«", r"\g<1> «"],
        [r"([ཀགཤ།])་?«", r"\g<1> «"],
        [r"»\s+", r"»"],
        [r"«\s+«", r"«"],
        [r"»+", r"»"],
        [r"[=—]", r"-"],
        [r"\s+-", r"-"],
        [r"\s+\+", r"+"],
        [r"»\s+«", r"»«"],
        # add missing markers
        [r" ([^«]+»)", r" «\g<1>"],
        [r"([^»]+«) ", r"\g<1>» "],
        [r"([^»]+«)-", r"\g<1>»-"],
        [r"(«[^་]+?་)([^»])", r"\g<1>»\g<2>"],
        [r"\s+", r" "],
        [r"།\s།\s*\n", r"།\n"],
        [r"།\s།\s«", r"། «"],
        [r"༌", r"་"],  # normalize NB tsek
        [r"ག\s*།", r"ག"],
        [r"་\s*", r"་"],
        [r"་\s*", r"་"],
        [r"་\s*\n", r"་"],
        [r"་+", r"་"],
        # normalize and tag page numbers '73ཝ་768' --> ' <p73-768> '
        [r"([0-9]+?)[ཝ—-]་?([0-9]+)", r" <p\g<1>-\g<2>> "],
        [r"། ([^།»\{\}]+)«", r"།\n<m\g<1>>«"],
        [r"<m\n(\}\{.+?)>«", r"\g<1>«"],  # fix special note markers
        [r"([ཀགཤ།] )([^།»\{\}]+)«", r"\g<1>\n<m\g<2>>«"],
        [r"»\n", r"»"],  # put all the notes split on two lines on a single one
        [r"། །\n", r"།\n"],
        [r"<m.+?>", r"4"],  # replace m tag with m only
    ]

    # «ཅོ་»«ཞོལ་»གྲག་༡༨)

    for p in patterns:
        text = re.sub(p[0], p[1], text)
    # text = translate_ref(text)
    return text


"""
»འཁྲང་། ༄༅། «གཡུང་»
"""


def preprocess_namsel_notes(text):
    """
    this cleans up all note markers
    :param text: plain text
    :return: cleaned text
    """

    patterns = [
        # normalize single zeros '༥༥་' --> '༥༥༠'
        [r"([༠-༩])[་༷]", r"\g<1>༠"],
        # normalize double zeros '༧༷་' --> '༧༠༠'
        [r"༠[་༷]", r"༠༠"],
        [r"༠[་༷]", r"༠༠"],
        # normalize punct
        [r"\r", r"\n"],
        [r"༑", r"།"],
        [r"།།", r"། །"],
        [r"།་", r"། "],
        [r"\s+", r" "],
        [r"།\s།\s*\n", r"།\n"],
        [r"།\s།\s«", r"། «"],
        [r"༌", r"་"],  # normalize NB tsek
        [r"ག\s*།", r"ག"],
        [r"་\s*", r"་"],
        [r"་\s*", r"་"],
        [r"་\s*\n", r"་"],
        [r"་+", r"་"],
        # delete tibetan numbers
        # ['[༠-༩]', ''],
        # headers ++<header>++
        # ['#\n(.+?)«', '#\n++\g<1>\n++«'],
        # special notes
        [r"\(?(པོད་འདིའི་.+?)\)\s*", r"\n{\g<1>}\n"],
        # deal with spaces in special notes
        [r"(\{[^\}]+?) (.+?\})", r"\g<1>_\g<2>"],
        # deal with spaces in special notes
        [r"(\{[^\}]+?) (.+?\})", r"\g<1>_\g<2>"],
        # deal with spaces in special notes
        [r"(\{[^\}]+?) (.+?\})", r"\g<1>_\g<2>"],
        # normalize and tag page numbers '73ཝ་768' --> ' <p73-768> '
        [r"([0-9]+?)[ཝ—-]་?([0-9]+)", r" <p\g<1>-\g<2>> "],
        # tag page references '༡༤༥ ①' --> <p༡༤༥> ①'
        [r" ?([༠-༩]+?)(\s\(?[①-⓪༠-༩ ཿ༅]\)?)", r" \n<r\g<1>>\g<2>"],  # basic page ref
        # normalize edition marks «<edition>»
        [r"〈〈?", r"«"],
        [r"〈〈?", r"«"],
        [r"〉〉?", r"»"],
        [r"〉〉?", r"»"],
        [r"《", r"«"],
        [r"》", r"»"],
        [r"([ཀགཤ།]) །«", r"\g<1> «"],
        [r"([ཀགཤ།])་?«", r"\g<1> «"],
        [r"»\s+", r"»"],
        [r"«\s+«", r"«"],
        [r"»+", r"»"],
        [r"[=—]", r"-"],
        [r"\s+-", r"-"],
        [r"\s+\+", r"+"],
        [r"»\s+«", r"»«"],
        # add missing markers
        [r" ([^«]+»)", r" «\g<1>"],
        [r"([^»]+«) ", r"\g<1>» "],
        [r"([^»]+«)-", r"\g<1>»-"],
        [r"(«[^་]+?་)([^»])", r"\g<1>»\g<2>"],
        [r"(»[^«]+?)»", r"\g<1>"],  # fix extra
        # tag note markers <note>
        [r"([ཤཀག།\n] )([^།»\}<>]+)«", r"\g<1>\n<m\g<2>>«"],
        [r"<\n(\{.+?)>«", r"\g<1>«"],  # fix special note markers
        [r"([①-㊿]+)[^«]", r"\n<m\g<1>>"],
        [r"(\s?[①-㊿༠-༩]+)«", r"\n<m\g<1>>«"],
        [r"\n<m([^ >]+?[ཤཀག།] )", r"\g<1>\n<m"],  # fix multi-syls A
        [r"\n([^།»\{}<>]+)«", r"\n<m\g<1>>«"],  # fix ref at line start
        [r"> ?([^>«»]+?)«", r">\n<m\g<1>>«"],  # fix ref + marker
        [r"m\s+", r"m"],  # delete spaces after m
        [r"([^\n])<r", r"\g<1>\n<r"],  # fix inline ref
        [r"\s([^<>«» ]+?)«", r" \n<m\g<1>>«"],  # fix ?
        [r"«[^»]+?«ང་»", r"«གཡུང་»"],  # fix g.yung
        # [' ([^ༀ-࿚]+)«', '\n<\g<1>>«'],  # catch ། @ «
        # Add page references to first footnote marker
        # ['([༠-༩]+)([\n\s]*)<([\s]*①)', '\g<2><\g<1>\g<3>'],
        [
            r"»\n([^<])",
            r"»\g<1>",
        ],  # to put all the notes split on two lines on a single one
        [r"། །\n", r"།\n"],
        [r"(<[mpr])\n", r"\g<1>"],
        [r"\n<m\s*>", r""],  # fix multi-syls B
        [r"\n<m(\{[^<>]+?)>", r"\g<1>"],  # keep special notes on first line
        [r"\n<m([^>]+?།[^>]+?)>", r"\g<1>"],  # keep split notes on first line
        # Deal with multiple markers
        [r"<m\(?(.*?)\)?>", r"<m\g<1>>"],  # clear ()
        [r"<m>", r"<m0>"],  # add replacement where needed
        [r"<m.?དྷི.?>", r"<m4>"],
        [r"<m.?ཉེ.?>", r"<m༡༠>"],
        [r"<m.?ཀྱེ.?>", r"<m༨>"],
        [r"<m.?སྟེ.?>", r"<m10>"],
        [r"<m་?ཏུ་?>", r"<m9>"],
        [r"<m་?ཏུཉེ་?>", r"<m10>"],
        [r"<m་?ཏུམེ་?>", r"<m11>"],
        [r"<m་?པོཉེ་?>", r"<m༦>"],
        [r"<m་?ཕོཉེ་?>", r"<m11>"],
        [r"<m་?ཐོཉེ་?>", r"<m11>"],
        [r"<m་?ཐོའི་?>", r"<m11>"],
        [r"<m་?སྣེ་?>", r"<m༣>"],
        [r"<m་?ནི་?>", r"<m༣>"],
        [r"<m་?བེ་?>", r"<m༣>"],
        [r"<m་?ཐོ་?>", r"<m10>"],
        [r"<m་?ཐོན་?>", r"<m10>"],
        [r"<m་?ཡི་?>", r"<m10>"],
        [r"<m་?པེ་?>", r"<m༤>"],
        [r"<m་?འོན་?>", r"<m12>"],
        [r"<m་?ཧུཉེ་?>", r"<m13>"],
        [r"<m་?ཉུགེ?>", r"<m13>"],
        [r"<m་?གེ་?>", r"<m5>"],
        [r"<m་?དུ་?>", r"<m10>"],
        [r"<m་?༠་?>", r"<m0>"],
        [r"<m་?ཿ་?>", r"<m༡>"],
        [r"<mགདུ་>", r"<m⑧⑧>"],
        [r"<m88>", r"<m⑧⑧>"],
        [r"<m[^> །]{6,8}>", r"<m⑧⑧>"],
        [r"<m888>", r"<m⑧⑧⑧>"],
        [r"<m[^> །]{9,14}>", r"<m⑧⑧⑧>"],
        [r"<m8888>", r"<m⑧⑧⑧⑧>"],
        [r"<m[^> །]{15,20}>", r"<m⑧⑧⑧⑧>"],
        [r"<m88888>", r"<m⑧⑧⑧⑧⑧>"],
        [r"<m་?([①-⓪])་?>", r"<m\g<1>>"],
        [r"<m[0༠]>", r"<m⓪>"],
        [r"<m[༡1]>", r"<m①>"],
        [r"<m[2༢]>", r"<m②>"],
        [r"<m[3༣]>", r"<m③>"],
        [r"<m[4༤]>", r"<m④>"],
        [r"<m[5༥]>", r"<m⑤>"],
        [r"<m[6༦]>", r"<m⑥>"],
        [r"<m[7༧]>", r"<m⑦>"],
        [r"<m[8༨]>", r"<m⑧>"],
        [r"<m[9༩]>", r"<m⑨>"],
        [r"<m10>", r"<m⑩>"],
        [r"<m༡༠>", r"<m⑩>"],
        [r"<m11>", r"<m⑪>"],
        [r"<m༡༡>", r"<m⑪>"],
        [r"<m12>", r"<m⑫>"],
        [r"<m༡༢>", r"<m⑫>"],
        [r"<m13>", r"<m⑬>"],
        [r"<m༡༣>", r"<m⑬>"],
        [r"<m14>", r"<m⑭>"],
        [r"<m༡༤>", r"<m⑭>"],
        [r"<m15>", r"<m⑮>"],
        [r"<m༡༥>", r"<m⑮>"],
        [r"<m16>", r"<m⑯>"],
        [r"<m༡༦>", r"<m⑯>"],
        [r"<m17>", r"<m⑰>"],
        [r"<m༡༧>", r"<m⑰>"],
        [r"<m18>", r"<m⑱>"],
        [r"<m༡༨>", r"<m⑱>"],
        [r"<m19>", r"<m⑲>"],
        [r"<m༡༩>", r"<m⑲>"],
        [r"<m20>", r"<m⑳>"],
        [r"<m༢༠>", r"<m⑳>"],
        [r"<m21>", r"<m⑳>"],
        [r"<m༢༡>", r"<m⑳>"],
        [r"<m22>", r"<m⑳>"],
        [r"<m༢༢>", r"<m⑳>"],
        [r"<m23>", r"<m⑳>"],
        [r"<m24>", r"<m⑳>"],
        [r"<m25>", r"<m⑳>"],
        [r"<m26>", r"<m⑳>"],
        [r"<m27>", r"<m⑳>"],
        [r"<m28>", r"<m⑳>"],
        [r"<m29>", r"<m⑳>"],
        [r"<m30>", r"<m⑳>"],
    ]

    for p in patterns:
        text = re.sub(p[0], p[1], text)

    # text = translate_ref(text)

    return text


def translate_ref(content):
    # translating numbers to letters avoids tag splitting HACK
    list = re.split(r"(<[rp][༠-༩]+?>)", content)
    bo_ar = "".maketrans("༡༢༣༤༥༦༧༨༩༠", "abcdefghij")
    result = "".join([e.translate(bo_ar) if e[1] == "r" else e for e in list])
    return result
