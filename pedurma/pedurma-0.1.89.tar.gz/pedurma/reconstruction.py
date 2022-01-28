# coding='utf-8'

"""
Pedurma footnotes Reconstruction
footnotes reconstruction script for the ocred katen pedurma using annotation transfer with
google's dmp.(https://github.com/google/diff-match-patch)
This script allows to transfer a specific set of annotations(footnotes and footnotes markers)
from text A(OCRed etext) to text B(clean etext). We first compute a diff between  texts
A and B, then filter the annotations(dmp diffs) we want to transfer and then apply them to
text B.
"""

import re
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path

import pyewts
from antx import transfer

from pedurma.exceptions import PageNumMissing
from pedurma.preprocess import preprocess_google_notes, preprocess_namsel_notes
from pedurma.texts import (
    get_body_text_from_last_page,
    get_page_ann,
    get_pecha_paths,
    get_pedurma_text_obj,
)
from pedurma.utils import from_editor, optimized_diff_match_patch, translate_tib_number

EWTSCONV = pyewts.pyewts()


def rm_google_ocr_header(text):
    """Remove header of google ocr.

    Args:
        text (str): google ocr

    Returns:
        str: header removed
    """
    header_pattern = (
        "\n\n\n\n{1,18}.+\n(.{1,30}\n)?(.{1,15}\n)?(.{1,15}\n)?(.{1,15}\n)?"
    )
    result = re.sub(header_pattern, "\n\n\n", text)
    return result


def get_diffs(text1, text2):
    """Compute diff between source and target with DMP.

    Args:
        source (str): source text
        target (str): target text
        optimized (bool): whether to use optimized dmp with node.
    Returns:
        list: list of diffs
    """
    print("[INFO] Computing diffs ...")
    dmp = optimized_diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    print("[INFO] Diff computed!")
    return diffs


# HACK is that useful?


def rm_noise(diff):
    """Filter out noise from diff text.

    Args:
        diff (str): diff text
    Returns:
        str: cleaned diff text
    """
    result = diff
    patterns = ["\n", "\u0020+", "་+?"]
    for pattern in patterns:
        noise = re.search(pattern, diff)
        if noise:
            result = result.replace(noise[0], "")
    return result


def rm_markers_ann(text):
    """Remove page annotation and replace footnotesmarker with #.

    Args:
        text (str): diff applied text

    Returns:
        str: diff applied text without page annotation and replaced footnotesmarker with #
    """
    result = ""
    lines = text.splitlines()
    for line in lines:
        line = re.sub("<p.+?>", "", line)
        line = re.sub("<.+?>", "#", line)
        result += line + "\n"
    return result


def reformat_pg_ann(diff, vol_num):
    """Extract pedurma page and put page annotation.

    Args:
        diff (str): diff text
        vol_num (int): volume number

    Returns:
        str: page annotation
    """
    pg_no_pattern = fr"{vol_num}\S*?(\d+)"
    pg_pat = re.search(pg_no_pattern, diff)
    try:
        pg_num = pg_pat.group(1)
    except Exception:
        pg_num = 0
    return re.sub(pg_no_pattern, f"<p{vol_num}-{pg_num}>", diff)


def get_abs_marker(diff):
    """Extract absolute footnotes marker from diff text.

    Args:
        diff (str): diff text

    Returns:
        str: footnotes marker
    """
    marker_ = ""
    patterns = ["[①-⓪]+", "[༠-༩]+", "[0-9]+"]
    for pattern in patterns:
        if re.search(pattern, diff):
            marker = re.search(pattern, diff)
            marker_ += marker[0]
    return marker_


def get_excep_marker(diff):
    """Check is diff belong to exception marker or not if so returns it.

    Args:
        diff (str): diff text

    Returns:
        str: exception marker
    """
    marker_ = ""
    patterns = ["<u(.+?)>", "(.*#.*)"]
    for pattern in patterns:
        marker = re.search(pattern, diff)
        if re.search(pattern, diff):
            marker = re.search(pattern, diff)
            marker_ = marker.group(1)
    return marker_


def is_punct(char):
    """Check whether char is tibetan punctuation or not.

    Args:
        diff (str): character from diff

    Returns:
        flag: true if char is punctuation false if not
    """
    if char in ["་", "།", "༔", ":", "། །", "༄", "༅", "\u0F7F", " "]:
        return True
    else:
        return False


def is_vowel(char):
    """Check whether char is tibetan vowel or not.

    Args:
        char (str): char to be checked

    Returns:
        boolean: true for vowel and false for otherwise
    """
    flag = False
    vowels = ["\u0F74", "\u0F72", "\u0F7A", "\u0F7C"]
    for pattern in vowels:
        if re.search(pattern, char):
            flag = True
    return flag


def is_midsyl(left_diff, right_diff):
    """Check if current diff is mid syllabus.

    Args:
        left_diff (str): left diff text
        right_diff (str): right diff text

    Returns:
        boolean : True if it is mid syllabus else False
    """
    if left_diff:
        right_diff_text = right_diff.replace("\n", "")
        left_diff_text = left_diff.replace("\n", "")
        if not right_diff_text or not left_diff_text:
            return False
        if not is_punct(left_diff_text[-1]) and not is_punct(right_diff_text[0]):
            return True
    return False


def double_mid_syl_marker(result):
    """Handle the consecutive marker occurance in body text.

    Args:
        result (list): filtered diffs

    Returns:
        Boolean: True if double consecutive marker detected in case of mid syl esle false
    """
    i = -1
    while abs(i) < len(result) and not is_punct(result[i][1]):
        if result[i][2] == "marker":
            return False
        else:
            i -= 1
    return True


def handle_mid_syl(
    result, diffs, left_diff, i, diff, right_diff_text, marker_type=None
):
    """Handle the middle of syllabus diff text in different situation.

    Args:
        result (list): Filtered diff list
        diffs (list): Unfilterd diff list
        left_diff (list): left diff type and text from current diff
        diff (list): current diff type and text
        i (int): current diff index
        right_diff (list): right diff type and text from current diff
        marker_type (str): marker type can be marker or candidate marker
    """
    # make it marker if marker found  (revision)
    if double_mid_syl_marker(result):
        diff_ = rm_noise(diff[1])
        if left_diff[1][-1] == " ":
            lasttwo = left_diff[1][-2:]
            result[-1][1] = result[-1][1][:-2]
            result.append([1, diff_, f"{marker_type}"])
            diffs[i + 1][1] = lasttwo + diffs[i + 1][1]
        elif right_diff_text[0] == " ":
            result.append([1, diff_, f"{marker_type}"])
        elif is_vowel(left_diff[1][-1]):
            syls = re.split("(་|།)", right_diff_text)
            first_syl = syls[0]
            result[-1][1] += first_syl
            diffs[i + 1][1] = diffs[i + 1][1][len(first_syl) :]
            result.append([1, diff_, f"{marker_type}"])
        else:
            if is_vowel(right_diff_text[0]):
                syls = re.split("(་|།)", right_diff_text)
                first_syl = syls[0]
                result[-1][1] += first_syl
                diffs[i + 1][1] = diffs[i + 1][1][len(first_syl) :]
                result.append([1, diff_, f"{marker_type}"])
            else:
                if left_diff[0] != (0 or 1):
                    lastsyl = left_diff[1].split("་")[-1]
                    result[-1][1] = result[-1][1][: -len(lastsyl)]
                    result.append([1, diff_, f"{marker_type}"])
                    diffs[i + 1][1] = lastsyl + diffs[i + 1][1]


def tseg_shifter(result, diffs, left_diff_text, i, right_diff_text):
    """Shift tseg if right diff starts with one and left diff ends with non punct.

    Args:
        result (list): filtered diff
        diffs (list): unfiltered diffs
        left_diff (list): contains left diff type and text
        i (int): current index if diff in diffs
        right_diff (list): contains right diff type and text
    """
    if right_diff_text and right_diff_text[0] == "་" and not is_punct(left_diff_text):
        result[-1][1] += "་"
        diffs[i + 1][1] = diffs[i + 1][1][1:]


def get_marker(diff):
    """Extarct marker from diff text.

    Args:
        diff (str): diff text

    Returns:
        str: marker
    """
    if get_abs_marker(diff):
        marker = get_abs_marker(diff)
        return marker
    elif get_excep_marker(diff):
        marker = get_excep_marker(diff)
        return marker
    else:
        return ""


def is_circle_number(footnotes_marker):
    """Check whether footnotes marker is number in circle or not and if so
       returns equivalent number.

    Args:
        footnotes_marker (str): footnotes marker
    Returns:
        str: number inside the circle
    """
    value = ""
    number = re.search("[①-⓪]", footnotes_marker)
    if number:
        circle_num = {
            "⓪": "0",
            "①": "1",
            "②": "2",
            "③": "3",
            "④": "4",
            "⑤": "5",
            "⑥": "6",
            "⑦": "7",
            "⑧": "8",
            "⑨": "9",
            "⑩": "10",
            "⑪": "11",
            "⑫": "12",
            "⑬": "13",
            "⑭": "14",
            "⑮": "15",
            "⑯": "16",
            "⑰": "17",
            "⑱": "18",
            "⑲": "19",
            "⑳": "20",
        }
        value = circle_num.get(number[0])
    return value


def get_tib_num(eng_num):
    tib_num = {
        "0": "༠",
        "1": "༡",
        "2": "༢",
        "3": "༣",
        "4": "༤",
        "5": "༥",
        "6": "༦",
        "7": "༧",
        "8": "༨",
        "9": "༩",
    }
    value = ""
    if eng_num:
        for num in str(eng_num):
            if re.search(r"\d", num):
                value += tib_num.get(num)
    return value


def get_page_ref_number(string):
    """Extract page referance number from string

    Args:
        string (str): can be any string

    Returns:
        int: page ref number
    """
    table = string.maketrans("༡༢༣༤༥༦༧༨༩༠", "1234567890", "<r>")
    tib_num = int(string.translate(table))
    return tib_num


def get_value(footnotes_marker):
    """Compute the equivalent numbers in footnotes marker payload and return it.

    Args:
        footnotes_marker (str): footnotes marker
    Returns:
        str: numbers in footnotes marker
    """
    value = ""
    if is_circle_number(footnotes_marker):
        value = is_circle_number(footnotes_marker)
        return value
    elif translate_tib_number(footnotes_marker):
        value = translate_tib_number(footnotes_marker)
        return value
    return value


def split_circle_marker(marker_text, type_):
    """Split multiple circle markers

    Args:
        marker_text (str): marker text which may contain circle marker

    Returns:
        list: list of circle markers
    """
    markers = [marker_text]
    if re.search("[①-⓪]", marker_text) and type_ == "body":
        markers = re.findall("[①-⓪]", marker_text)
    return markers


def format_diff(filter_diffs, vol_num, type_=None):
    """Format list of diff on target text.

    Args:
        diffs (list): list of diffs
        image_info (list): contains work_id, volume number and image source offset
        type_ (str): diff type can be footnotes or body
    Returns:
        str: target text with transfered annotations with markers.
    """
    diffs = filter_diffs
    vol_num = vol_num
    result = ""
    for diff_type, diff_text, diff_tag in diffs:
        if diff_type == 1 or diff_type == 0:
            if diff_tag:
                if diff_tag == "pedurma-page":
                    result += reformat_pg_ann(diff_text, vol_num)
                if diff_tag == "marker":
                    if get_abs_marker(diff_text):
                        marker_text = get_abs_marker(diff_text)
                        markers = split_circle_marker(marker_text, type_)
                        for marker in markers:
                            value = get_value(marker)
                            result += f"<{value},{marker}>"
                    elif get_excep_marker(diff_text):
                        marker = get_excep_marker(diff_text)
                        result += f"<{marker}>"
                    else:
                        result += f"<{diff_text}>"
                elif diff_tag == "pg_ref":
                    result += diff_text
            else:
                result += diff_text

    return result


def reformatting_body(text):
    """Reformat marker annotation using pedurma page.

    Args:
        text (str): unformatted text

    Returns:
        str: formatted text
    """
    result = ""
    page_anns = re.findall(r"<p\S+?>", text)
    pages = re.split(r"<p\S+?>", text)
    for page, ann in zip_longest(pages, page_anns, fillvalue=""):
        markers = re.finditer("<.+?>", page)
        for marker_walker, marker in enumerate(markers, 1):
            marker_walker = get_tib_num(marker_walker)
            repl = f"<{marker_walker},{marker[0][1:-1]}>"
            page = page.replace(marker[0], repl, 1)
        result += page + ann
    return result


def rm_marker(diff):
    """Remove marker of google ocr text.

    Args:
        diff (str): diff text

    Returns:
        str: diff text without footnotes marker of google ocr
    """
    result = diff
    patterns = [
        r"©",
        r"®",
        r"\“",
        r"•",
        r"[༠-༩]",
        r"[a-zA-Z]",
        r"\)",
        r"\(",
        r"\u0020+",
        r"@",
        r"་+?",
        r"། །",
        r"\d",
        r"།",
        r"༄༅",
    ]
    for pattern in patterns:
        if re.search(pattern, diff):
            result = re.sub(pattern, "", result)
    return result


def is_note(diff):
    """Check if diff text is note or marker.

    Args:
        diff (str): diff text

    Returns:
        boolean: True if diff text is note else False.
    """
    flag = True
    patterns = [r"[①-⑳]", r"[༠-༩]", r"\)", r"\(", r"\d", r"⓪"]
    for pattern in patterns:
        if re.search(pattern, diff):
            flag = False
    return flag


def parse_pg_ref_diff(diff, result):
    """Parse page ref and marker if both exist in one diff.

    Args:
        diff (str): diff text
        result (list): filtered diff
    """
    lines = diff.splitlines()
    for line in lines:
        if line:
            if re.search("<r.+?>", line):
                result.append([1, line, "page_ref"])
            elif re.search("(<u.+?>)(.+)", line):
                marker = re.search("(<u.+?>)(.+)", line)
                result.append([1, marker.group(1), "marker"])
                result.append([1, marker.group(2), ""])
            elif re.search("<u.+?>", line):
                marker = re.search("<u.+?>", line)
                result.append([1, marker[0], "marker"])


def double_marker_handler(result):
    if len(result) > 3:
        prev2 = result[-3]
        prev1 = result[-2]
        cur = result[-1]
        if cur[2] == "marker":
            if prev2[2] == "marker" and prev1[1] in ["\n", " ", "", "།"]:
                del result[-1]
    else:
        pass


def reformat_footnotes(text):
    """Replace edition name with their respective unique id and brings every footnotes to newline.
    Args:
        text (str): google OCRed footnotes with namsel footnotes markers transfered.
    Returns:
        (str): reformatted footnote
    """
    text = text.replace("\n", "")
    text = re.sub("(<+)", r"\n\1", text)
    result = demultiply_diffs(text)

    return result


def parse_pedurma_page_diff(pedurma_page_diff, vol_num, result):
    """extracting possible marker from pedurma page annotation diff

    Args:
        pedurma_page_diff (str): pedurma page ann diff text
        vol_num (int): volume number 
        result (list): filter diff list

    Returns:
        list: filter diff list
    """
    diff_parts = re.split(fr"(\n?{vol_num}་?\D་?\d+)", pedurma_page_diff)
    for diff_part in diff_parts:
        diff_part = diff_part.replace("\n", "")
        if re.search(fr"{vol_num}་?\D་?\d+", diff_part):
            result.append([1, diff_part, "pedurma-page"])
        elif get_marker(diff_part):
            result.append([1, diff_part, "marker"])
        else:
            result.append([1, diff_part, ""])
    return result


def filter_diffs(diffs_list, type, vol_num):
    """Filter diff of text A and text B.

    Args:
        diffs_list (list): list of diffs
        type (str): type of text
        image_info (list): contains work_id, volume number and source image offset.

    Returns:
        list: filtered diff
    """
    left_diff = [0, ""]
    result = []
    vol_num = vol_num
    diffs = diffs_list
    for i, diff in enumerate(diffs):
        diff_type, diff_text = diff
        if diff_type == 0:  # in both
            if re.search(
                fr"{vol_num}་?\D་?\d+", diff_text
            ):  # checking diff text is page or not
                result.append([0, diff_text, "pedurma-page"])
            else:
                result.append([diff_type, diff_text, ""])

        elif diff_type == 1:  # in target
            result.append([diff_type, diff_text, ""])
        elif diff_type == -1:  # in source

            if re.search(
                fr"{vol_num}་?\D་?\d+", diff_text
            ):  # checking diff text is page or not
                result = parse_pedurma_page_diff(diff_text, vol_num, result)
            else:
                left_diff = [0, ""]
                right_diff = [0, ""]
                if i > 0:  # extracting left context of current diff
                    left_diff = diffs[i - 1]
                left_diff_type, left_diff_text = left_diff
                if i < len(diffs) - 1:  # extracting right context of current diff
                    right_diff = diffs[i + 1]
                right_diff_type, right_diff_text = right_diff
                diff_ = rm_noise(
                    diff_text
                )  # removes unwanted new line, space and punct
                if left_diff_type == 0 and right_diff_type == 0:
                    # checks if current diff text is located in middle of a syllable
                    if is_midsyl(left_diff_text, right_diff_text) and get_marker(
                        diff_text
                    ):
                        handle_mid_syl(
                            result,
                            diffs,
                            left_diff,
                            i,
                            diff,
                            right_diff_text,
                            marker_type="marker",
                        )
                    # checks if current diff text contains absolute marker or not
                    elif get_marker(diff_text):
                        # Since cur diff is not mid syl, hence if any right diff starts with tseg will
                        # be shift to left last as there are no marker before tseg.
                        tseg_shifter(result, diffs, left_diff_text, i, right_diff_text)
                        result.append([1, diff_, "marker"])
                    # Since diff type of -1 is from namsel and till now we are not able to detect
                    # marker from cur diff, we will consider it as candidate marker.
                    elif diff_:
                        if (
                            "ང" in left_diff_text[-3:]
                            and diff_ == "སྐེ"
                            or diff_ == "ུ"
                        ):  # an exception case where candidate fails to be marker.
                            continue
                        # print(diffs.index(right_diff), right_diff)
                        elif is_midsyl(left_diff_text, right_diff_text):
                            handle_mid_syl(
                                result,
                                diffs,
                                left_diff,
                                i,
                                diff,
                                right_diff_text,
                                marker_type="marker",
                            )

                        else:
                            tseg_shifter(
                                result, diffs, left_diff_text, i, right_diff_text
                            )
                            result.append([1, diff_, "marker"])
                elif right_diff_type == 1:
                    # Check if current diff is located in middle of syllabus or not.
                    if is_midsyl(left_diff_text, right_diff_text) and get_marker(
                        diff_text
                    ):
                        handle_mid_syl(
                            result,
                            diffs,
                            left_diff,
                            i,
                            diff,
                            right_diff_text,
                            marker_type="marker",
                        )
                    elif get_marker(diff_text):
                        # Since cur diff is not mid syl, hence if any right diff starts with tseg will
                        # be shift to left last as there are no marker before tseg.
                        tseg_shifter(result, diffs, left_diff_text, i, right_diff_text)
                        result.append([1, diff_, "marker"])
                        # if "#" in right_diff[1]:
                        #     diffs[i + 1][1] = diffs[i + 1][1].replace("#", "")
                    else:
                        if diff_ != "" and right_diff_text in ["\n", " ", "་"]:
                            if (
                                "ང" in left_diff_text[-2:] and diff_ == "སྐེ"
                            ):  # an exception case where candidate fails to be marker.
                                continue
                            elif is_midsyl(left_diff_text, right_diff_text):
                                handle_mid_syl(
                                    result,
                                    diffs,
                                    left_diff,
                                    i,
                                    diff,
                                    right_diff_text,
                                    marker_type="marker",
                                )
                            else:
                                tseg_shifter(
                                    result, diffs, left_diff_text, i, right_diff_text
                                )
                                result.append([1, diff_, "marker"])
                                # if "#" in right_diff[1]:
                                #     diffs[i + 1][1] = diffs[i + 1][1].replace("#", "")
                    # if diff_ is not empty and right diff is ['\n', ' '] then make it candidate markrer
                double_marker_handler(result)

    filter_diffs = result

    return filter_diffs


def filter_footnotes_diffs(diffs_list, vol_num):
    """Filter the diffs of google ocr output and namsel ocr output.

    Args:
        diffs (list): diff list
        vol_num (int): colume number

    Returns:
        list: filtered diff containing notes from google ocr o/p and marker from namsel ocr o/p
    """
    diffs = diffs_list
    left_diff = [0, "", ""]
    filtered_diffs = []
    for i, diff in enumerate(diffs):
        diff_type, diff_text, diff_tag = diff
        if diff_type == 0:
            filtered_diffs.append(diff)
        elif diff_type == 1:
            if i > 0:  # extracting left context of current diff
                left_diff = diffs[i - 1]
            if i < len(diffs) - 1:  # extracting right context of current diff
                right_diff = diffs[i + 1]
            left_diff_tag = left_diff[2]
            if left_diff_tag != "marker" and left_diff_tag != "pedurma-page":
                if "4" in diff_text:
                    right_diff_text = rm_noise(right_diff[1])
                    if re.search(r"\d{2}", diff_text) or not right_diff_text:
                        continue
                    clean_diff = re.sub("[^4|\n]", "", diff_text)
                    filtered_diffs.append([0, clean_diff, "marker"])
                else:
                    diff_text = rm_marker(diff_text)
                    filtered_diffs.append(diff)
        else:
            filtered_diffs.append(diff)

    return filtered_diffs


def postprocess_footnotes(footnotes, vol_num):
    """Save the formatted footnotes to dictionary with key as page ref and value as footnotes in that page.
    Args:
        footnotes (str): formatted footnote
    Returns:
        dict: key as page ref and value as footnotes in that page
    """
    footnote_result = {}
    page_refs = re.findall("<r.+?>", footnotes)
    pages = re.split("<r.+?>", footnotes)[1:]
    print(
        f"number of page ref found -{len(page_refs)} number of page found-{len(pages)}"
    )
    for (page, page_ref) in zip_longest(pages, page_refs, fillvalue=""):
        markers = re.finditer("<.+?>", page)
        marker_l = []
        for i, marker in enumerate(markers, 1):
            repl = f"<{i},{marker[0][1:-1]}>"
            page = page.replace(marker[0], repl, 1)
        marker_list = [footnotes.strip() for footnotes in page.splitlines()]
        # Removes the noise marker without footnote
        for marker in marker_list:
            if marker:
                if re.search("<.+?>(.+?)", marker):
                    marker_l.append(marker)
                else:
                    if "<" not in marker:
                        marker_l.append(marker)
        body_pg_num = get_page_ref_number(page_ref)
        footnote_result[body_pg_num] = marker_l
    return footnote_result


def demultiply_diffs(text):
    """ '<12,⓪⓪>note' --> '<12,⓪>note\n<12,⓪>note'
    Arguments:
        text {str} -- [description]

    Returns:
        str -- [description]
    """
    patterns = [
        [
            r"(\n<\d+,)([①-⓪])([①-⓪])([①-⓪])([①-⓪])([①-⓪])(>.+)",
            r"\g<1>\g<2>\g<7>\g<1>\g<3>\g<7>\g<1>\g<4>\g<7>\g<1>\g<5>\g<7>\g<1>\g<6>\g<7>",
        ],
        [r"(\n<u)([①-⑨])([①-⑨])(>.+)", r"\g<1>\g<2>\g<4>\g<1>\g<3>\g<4>"],
        [
            r"(\n<\d+,)([①-⓪])([①-⓪])([①-⓪])([①-⓪])(>.+)",
            r"\g<1>\g<2>\g<6>\g<1>\g<3>\g<6>\g<1>\g<4>\g<6>\g<1>\g<5>\g<6>",
        ],
        [
            r"(\n<\d+,)([①-⓪])([①-⓪])([①-⓪])(>.+)",
            r"\g<1>\g<2>\g<5>\g<1>\g<3>\g<5>\g<1>\g<4>\g<5>",
        ],
        [r"(\n<\d+,)([①-⓪])([①-⓪])(>.+)", r"\g<1>\g<2>\g<4>\g<1>\g<3>\g<4>"],
    ]
    for p in patterns:
        text = re.sub(p[0], p[1], text)
    return text


def merge_footnotes_per_page(page, foot_notes):
    """Merge the footnote of a certain page to its body text.

    Args:
        page (str): content in page
        foot_notes (list): list of footnotes

    Returns:
        str: content of page attached with their footnote adjacent to their marker
    """
    preview_page = page
    markers = re.findall("<.+?>", page)
    for marker_walker, (marker, foot_note) in enumerate(
        zip_longest(markers, foot_notes, fillvalue=""), 1
    ):
        if re.search("<p.+>", marker):
            repl2 = f"\n{marker[2:-1]}"
        else:
            footnotes_parts = foot_note.split(">")
            try:
                note = footnotes_parts[1]
            except Exception:
                note = ""
            marker_walker = get_tib_num(marker_walker)
            if note:
                note = re.sub(r"\d+", "", note)
                repl2 = f"({marker_walker}) <{note}>"
            else:
                repl2 = ""
        if marker:
            preview_page = preview_page.replace(marker, repl2, 1)
    preview_page = re.sub("<p(.+?)>", r"\n\g<1>", preview_page)
    return preview_page


def reconstruct_body(source, target, vol_num):
    namsel_text = source
    google_text = target
    print("Calculating diffs...")
    diffs = get_diffs(namsel_text, google_text)
    diffs_list = list(map(list, diffs))
    print("Filtering diffs...")
    filtered_diffs = filter_diffs(diffs_list, "body", vol_num)
    new_text = format_diff(filtered_diffs, vol_num, type_="body")
    new_text = reformatting_body(new_text)
    return new_text


def get_clean_google_durchen(google_footnote):
    google_footnote = rm_google_ocr_header(google_footnote)
    clean_google_footnote = preprocess_google_notes(google_footnote)
    return clean_google_footnote


def get_clean_namsel_durchen(namsel_footnote):
    clean_namsel_footnote = preprocess_namsel_notes(namsel_footnote)
    return clean_namsel_footnote


def reconstruct_footnote(namsel_footnote, google_footnote, vol_num):
    annotations = [
        ["marker", "(<u.+?>)"],
        ["marker", "([①-⑩])"],
        ["pg_ref", "(<r.+?>)"],
        ["pedurma-page", "(<p.+?>)"],
    ]
    print("Calculating diffs..")
    diffs = transfer(namsel_footnote, annotations, google_footnote, output="diff")
    diffs_list = list(map(list, diffs))
    filtered_diffs = filter_footnotes_diffs(diffs_list, vol_num)
    new_text = format_diff(filtered_diffs, vol_num, type_="footnotes")
    reformatted_footnotes = reformat_footnotes(new_text)
    formatted_footnotes = postprocess_footnotes(reformatted_footnotes, vol_num)
    return formatted_footnotes


def get_page_num(body_text, vol_num):
    vol = vol_num
    pg_pat = re.search(fr"<p{vol}-(\d+)>", body_text)
    try:
        pg_num = int(pg_pat.group(1))
    except Exception:
        pg_num = 0
    return pg_num


def get_durchen_pgs_content(durchen_pages, type_):
    durchen_pgs_content = ""
    for durchen_page in durchen_pages:
        if durchen_page:
            durchen_pgs_content += from_editor(durchen_page.content, type_) + "\n\n"
    return durchen_pgs_content


def get_preview_page(g_body_page, n_body_page, g_durchen_pages, n_durchen_pages):
    preview_page = g_body_page.content
    g_body_page_content = g_body_page.content
    n_body_page_content = n_body_page.content
    g_durchen_page_content = get_durchen_pgs_content(g_durchen_pages, type_="google")
    n_durchen_page_content = get_durchen_pgs_content(n_durchen_pages, type_="namsel")
    vol_num = g_body_page.vol
    n_body_page_content = transfer(
        g_body_page_content, [["pedurma", "(#)"]], n_body_page_content, output="txt"
    )
    g_body_page_content = g_body_page_content.replace("#", "")
    body_result = reconstruct_body(n_body_page_content, g_body_page_content, vol_num)
    footnotes = reconstruct_footnote(
        n_durchen_page_content, g_durchen_page_content, vol_num
    )
    pg_num = get_page_num(body_result, vol_num)
    if pg_num not in footnotes:
        cur_pg_footnotes = []
        raise PageNumMissing
    else:
        cur_pg_footnotes = footnotes[pg_num]
    if cur_pg_footnotes:
        preview_page = merge_footnotes_per_page(body_result, cur_pg_footnotes)
    return preview_page


def get_vol_note_text(notes, vol_num, type_):
    note_text = ""
    for note in notes:
        if note.vol == vol_num:
            note_text += from_editor(note.content, type_) + "\n\n"
    return note_text


def get_body_pages(body_result, vol):
    result = []
    pg_text = ""
    pages = re.split(fr"(<p{vol}-\d+>)", body_result)
    for i, page in enumerate(pages):
        if i % 2 == 0:
            pg_text += page
        else:
            pg_text += page
            result.append(pg_text)
            pg_text = ""
    return result


def get_vol_preview(dg_body, namsel_body, dg_note_text, namsel_note_text, vol_num):
    preview_text = ""
    namsel_body = transfer(dg_body, [["pedurma", "(#)"]], namsel_body, output="txt")
    dg_body = dg_body.replace("#", "")
    body_result = reconstruct_body(namsel_body, dg_body, vol_num)
    footnotes = reconstruct_footnote(namsel_note_text, dg_note_text, vol_num)
    body_pages = get_body_pages(body_result, vol_num)
    for body_page in body_pages:
        pg_num = get_page_num(body_page, vol_num)
        cur_pg_footnotes = footnotes.get(pg_num, [])
        preview_text += merge_footnotes_per_page(body_page, cur_pg_footnotes) + "\n"
    return preview_text


def pecha_path_2_id(pecha_path):
    pecha_path_obj = Path(pecha_path)
    return pecha_path_obj.stem


def get_reconstructed_text(text_id, pecha_paths=None):
    if pecha_paths is None:
        pecha_paths = get_pecha_paths(text_id)
    pedurmatext = get_pedurma_text_obj(text_id, pecha_paths)
    google_pecha_id = pecha_path_2_id(pecha_paths["google"])
    derge_google_text_obj = pedurmatext.google
    namsel_text_obj = pedurmatext.namsel
    preview_text = defaultdict(str)
    dg_pages = derge_google_text_obj.pages
    dg_notes = derge_google_text_obj.notes
    namsel_pages = namsel_text_obj.pages
    namsel_notes = namsel_text_obj.notes
    dg_body = ""
    namsel_body = ""
    cur_vol_preview = ""
    for dg_page, namsel_page in zip(dg_pages, namsel_pages):
        vol_num = dg_page.vol
        if "--" in dg_page.note_ref:
            dg_body += (
                f"{get_body_text_from_last_page(dg_page)}\n{get_page_ann(dg_page)}"
            )
            namsel_body += f"{get_body_text_from_last_page(namsel_page)}\n{get_page_ann(namsel_page)}"
            dg_note_text = get_vol_note_text(dg_notes, vol_num, type_="google")
            namsel_note_text = get_vol_note_text(namsel_notes, vol_num, type_="namsel")
            cur_vol_preview = get_vol_preview(
                dg_body, namsel_body, dg_note_text, namsel_note_text, vol_num
            )
            preview_text[f"v{int(vol_num):03}"] = cur_vol_preview
            dg_body = ""
            namsel_body = ""
            cur_vol_preview = ""
            continue
        dg_body += dg_page.content
        namsel_body += namsel_page.content
    return preview_text, google_pecha_id
