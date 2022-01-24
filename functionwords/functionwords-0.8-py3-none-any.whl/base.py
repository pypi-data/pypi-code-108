"""
@author: Haining Wang
Created on March 17, 2021. v.0.5, launch.
Modified on Nov. 19, 2021. v.0.6, fix bugs in extracting Chinese ngram features.
Modified on Jan. 03, 2022. v.0.7, adding in `chinese_comprehensive` feature set.
Modified on Jan. 23, 2022. v.0.8, finely counting Chinese ngram features.
"""

import re
import os
import json

FUNCTION_WORDS_LISTS = ["chinese_classical_comprehensive",
         "chinese_classical_naive",
         "chinese_simplified_modern", 
         "english", 
         "chinese_comprehensive"]


class FunctionWords(object):
    """
    The main class does the heavy lifting.

    Attr:
        function_words_list: Which function word list is called. Either 'chinese_comprehensive', 'chinese_classical_comprehensive', 'chinese_classical_naive',
         'chinese_simplified_modern', or 'english'.
        function_words: The corresponding function word list.
        description: The description of the function word list.
    """

    def __init__(self, function_words_list):
        self.__path__ = os.path.dirname(__file__)
        if function_words_list.lower() in FUNCTION_WORDS_LISTS:
            self.function_words_list = function_words_list.lower()
        else:
            raise ValueError(f"""Pass in desired function word list in {FUNCTION_WORDS_LISTS}.""")
        self.function_words = json.load(
            open(os.path.join(self.__path__, "resources", self.function_words_list + ".json"), "r")
        )
        self.description = json.load(
            open(os.path.join(self.__path__, "resources", "description.json"), "r")
        )[self.function_words_list]

    def get_feature_names(self):
        """
        Returns a list of desired function words.
        """

        return self.function_words

    def transform(self, raw):
        """
        Counts function words in `raw`.
        param:
            raw: A string.
        return:
            A list of count of function words.
        """
        if not isinstance(raw, str):
            raise ValueError(
                f"""List of raw text documents expected, {type(raw)} object received."""
            )
        if self.function_words_list == 'english':
            counts = [len(re.findall(r"\b" + function_word + r"\b", raw.lower())) for function_word in self.function_words]
        else:
            """
            Update in v.0.8: a finer Chinese ngram counter
            when counting "于是" and "是", "是" will be counted twice if using standard `re.findall`
            this phenomenon is considered artificial and '是' should be counted once
            a finer ngram tokenizer should be useful in modern Chinese when function ngram's n is larger than 1
            """
            # counts = [len(re.findall(function_word, raw)) for function_word in self.function_words]
            counts = []
            for function_word in self.function_words:
                count = len(re.findall(function_word, raw))
                count_redundant = sum(len(re.findall(f_, raw)) for f_ in self.function_words
                                      if (f_.count(function_word) > 0 and f_ != function_word))
                counts.append(count-count_redundant)
        return counts

    def fit_transform(self, raw):

        return self.transform(raw)

    def fit(self, raw):

        return self.transform(raw)
