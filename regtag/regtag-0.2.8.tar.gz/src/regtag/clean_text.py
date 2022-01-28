#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import nltk
from nltk import word_tokenize

try:
    word_tokenize('test')
except:
    nltk.download('punkt')

SPACE_NORMALIZER = re.compile(r"\s+")
PUNCTUATION = ".,?!"
READ_PUNCTUATION = "/%-@$&><:"
CHARACTERS = "0123456789aAàÀảẢãÃáÁạẠăĂằẰẳẲẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬbBcCdDđĐeEèÈẻẺẽẼéÉẹẸêÊềỀểỂễỄếẾệỆfFgGhHiIìÌỉỈĩĨíÍịỊjJkKlL" \
             "mMnNoOòÒỏỎõÕóÓọỌôÔồỒổỔỗỖốỐộỘơƠờỜởỞỡỠớỚợỢpPqQrRsStTuUùÙủỦũŨúÚụỤưƯừỪửỬữỮứỨựỰvVwWxXyYỳỲỷỶỹỸýÝỵỴzZ"
ALL_CHARS = PUNCTUATION + CHARACTERS + READ_PUNCTUATION
WORD_NORMALIZER = re.compile(r"[^{}]".format(re.escape(ALL_CHARS)))
PUNC_NORMALIZER = re.compile(r"\s+(([{}])+)($|\s+)".format(re.escape(PUNCTUATION)))


def punc_priority(group_punc):
    if "?" in group_punc:
        return "?"
    if "!" in group_punc:
        return "!"
    if "." in group_punc:
        return "."
    return ","


def clean_line(raw):
    formatted_str = WORD_NORMALIZER.sub(' ', raw)
    formatted_str = PUNC_NORMALIZER.sub(r' \1 ', formatted_str)
    formatted_str = re.sub(r'\s+', ' ', formatted_str)
    formatted_str = ' '.join(word_tokenize(formatted_str)).replace('``', '"')

    formatted_str = re.sub(r"\s+([{}]+\s*)+".format(re.escape(PUNCTUATION)),
                           lambda x: " {} ".format(punc_priority(x.group(0))), formatted_str)

    formatted_str = re.sub(r"\s*([{}]+\s+)+".format(re.escape(PUNCTUATION)),
                           lambda x: " {} ".format(punc_priority(x.group(0))), formatted_str)

    formatted_str = re.sub(r"\s+", ' ', formatted_str)

    return formatted_str.strip()


if __name__ == "__main__":
    print(clean_line(
        'hay như Bloomberg,.  ?cũng đánh. giá Việt,,, ,,, . .Nam đồng (VND) là một trong, những đồng... tiền ổn định nhất châu Á. Một năm thành công!!!...  .của ngành ngân hàng Việt Nam.'))
