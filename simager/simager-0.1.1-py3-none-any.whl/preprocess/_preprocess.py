import re
import string
import unicodedata
import emoji
from bs4 import BeautifulSoup
import functools
import pkg_resources
import pickle


class TextPreprocess(object):
    """ Text Preprocessing

    Args:
        methods (list, optional): All sequence of cleaner methods. Defaults to `all`
            `all` methods not included `normalize` and `stopwords` method, you can put it manually
            Default values:
                [
                    "rm_hastag",
                    "rm_mention",
                    "rm_nonascii",
                    "rm_emoticons",
                    "rm_html",
                    "rm_url",
                    "sparate_str_numb",
                    "pad_punct",
                    "rm_punct",
                    "rm_repeat_char",
                    "rm_repeat_word",
                    "rm_numb",
                    "rm_whitespace"
                ]

    """

    def __init__(self, methods="all"):
        self.maps = {
            "rm_hastag": self.rm_hastag(),
            "rm_mention": self.rm_mention(),
            "rm_nonascii": self.rm_nonascii(),
            "rm_emoticons": self.rm_emoticons(),
            "rm_html": self.rm_html(),
            "rm_url": self.rm_url(),
            "sparate_str_numb": self.sparate_str_numb(),
            "pad_punct": self.pad_punct(),
            "rm_punct": self.rm_punct(),
            "rm_repeat_char": self.rm_repeat_char(),
            "rm_repeat_word": self.rm_repeat_word(),
            "rm_numb": self.rm_numb(),
            "rm_whitespace": self.rm_whitespace(),
            "normalize": self.normalize(),
            "stopwords": self.stopwords()
        }
        if methods == "all":
            self.methods = list(self.maps.values()[:-2])
        else:
            self._validate(methods)
            self.methods = [self.maps[i] for i in methods]

        self.norm_path = pkg_resources.resource_filename("simager", "data/normalizer.p")
        self.normalizer = pickle.load(open(self.norm_path, "rb"))
        self.stop_w_path = pkg_resources.resource_filename("simager", "data/stop_w.p")
        self.stop_w = pickle.load(open(self.stop_w_path, "rb"))

    def add_normalizer(self, norm):
        """ Adding normalizer dictionary

        Args:
            norm (dict, required): Dictionary of word normalizer, example: `{"yg": "yang"}`

        """
        if isinstance(norm, dict):
            self.normalizer.update(norm)
        else:
            raise Exception("normalizer must be a dict, example: `{'yg': 'yang'}`")

    def remove_normalizer(self, norm):
        """ Remove normalizer dictionary

        Args:
            norm (list, required): List of word that want to be remove from normalizer, example: `["yg"]`

        """
        if isinstance(norm, list):
            for i in norm:
                self.normalizer.pop(i)
        else:
            raise Exception("normalizer must be a list, example: `['yg']`")

    def add_stopwords(self, stopwords):
        """ Adding stopwords dictionary

        Args:
            stopwords (list, required): List of word that want to add on stopwords dictionary, example: `["yang"]`

        """
        if isinstance(stopwords, list):
            self.stop_w.update(set(stopwords))
        else:
            raise Exception("stopwords must be a list, example: `['yang']`")

    def remove_stopwords(self, stopwords):
        """ Remove stopwords from dictionary

        Args:
            stopwords (list, required): List of word that want to remove from stopwords dictionary, example: `["yang"]`

        """
        if isinstance(stopwords, list):
            for i in stopwords:
                self.stop_w.remove(i)
        else:
            raise Exception("stopwords must be a list, example: `['yg']`")

    def rm_punct(self):
        return (lambda text: text.translate(str.maketrans(dict.fromkeys(string.punctuation))))

    def rm_whitespace(self):
        return (lambda text: " ".join(x.strip() for x in text.split()))

    def rm_nonascii(self):
        return (lambda text: unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore"))

    def rm_emoticons(self):
        return (lambda text: re.sub(emoji.get_emoji_regexp(), r"", text))

    def rm_html(self):
        return (lambda text: BeautifulSoup(text, "html.parser").get_text())

    def rm_url(self):
        regex = r"""(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)*([\w\-]+)((\?)?[\w\s]*=\s*[\w\%&]*)*|www\S+"""
        return (lambda text: re.sub(regex, "", text))

    def rm_repeat_char(self):
        return (lambda text: re.sub(r"(.)\1+", r"\1\1", text))

    def rm_repeat_word(self):
        return (lambda text: re.sub(r"(?<!\S)((\S+)(?:\s+\2))(?:\s+\2)+(?!\S)", r"\1", text))

    def rm_numb(self):
        return (lambda text: re.sub(r"\d+", "", text))

    def rm_hastag(self):
        return (lambda text: re.sub("#(\w+)", "", text))

    def rm_mention(self):
        return (lambda text: re.sub("@(\w+)", "", text))

    def sparate_str_numb(self):
        return (lambda text: re.sub("(?<=\d)(?=[^\d\s])|(?<=[^\d\s])(?=\d)", " ", text))

    def pad_punct(self):
        regex = r'(?<=[.,!"#$%&\*+-/:;<=>?@])(?=[^\s])'
        return (lambda text: re.sub(regex, " ", text))

    def normalize(self):
        return (lambda text: self.normalizer.get(text, text))

    def stopwords(self):
        return (lambda text: text if text not in self.stop_w else "")

    def __call__(self, text):
        clean_text = []
        for wrd in str(text).split():
            tmp = str(functools.reduce(lambda s, func: func(s), self.methods, str(wrd)))
            clean_text.append(tmp)
        return " ".join(clean_text).strip()

    def _validate(self, methods):
        for i in methods:
            if i not in self.maps.keys():
                raise Exception(f"Methods must be in: {list(self.maps.keys())}")
