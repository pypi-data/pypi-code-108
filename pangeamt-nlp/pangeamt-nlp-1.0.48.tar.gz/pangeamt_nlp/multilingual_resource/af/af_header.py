import json


class AfHeader:
    def __init__(
        self,
        left_lang,
        left_translator,
        left_translation_type,
        right_lang,
        right_translator,
        right_translation_type,
        corpus_file,
        corpus_name,
        corpus_domain,
    ):
        self._left = AfHeaderPart(
            left_lang, left_translator, left_translation_type
        )

        self._right = AfHeaderPart(
            right_lang, right_translator, right_translation_type
        )

        self._corpus = AfHeaderCorpus(corpus_file, corpus_name, corpus_domain)

    def to_string(self):
        header = {
            "left": {
                "lang": self._left.lang,
                "translator": self._left.translator,
                "translationType": self._left.translation_type,
            },
            "right": {
                "lang": self._right.lang,
                "translator": self._right.translator,
                "translationType": self._right.translation_type,
            },
            "corpus": {
                "file": self._corpus.file,
                "name": self._corpus.name,
                "domain": self._corpus.domain,
            },
        }
        return json.dumps(header, ensure_ascii=False, indent=4) + "\n###\n"

    def get_left(self):
        return self._left

    left = property(get_left)

    def get_right(self):
        return self._right

    right = property(get_right)

    def get_corpus(self):
        return self._corpus

    corpus = property(get_corpus)

    @staticmethod
    def create_from_json(data):
        return AfHeader(
            data["left"]["lang"],
            data["left"]["translator"],
            data["left"]["translationType"],
            data["right"]["lang"],
            data["right"]["translator"],
            data["right"]["translationType"],
            data["corpus"]["file"],
            data["corpus"]["name"],
            data["corpus"]["domain"],
        )


class AfHeaderPart:
    def __init__(self, lang, translator, translation_type):
        self._lang = lang
        self._translator = translator
        if translation_type is None:
            translation_type = "default"
        self._translation_type = translation_type

    def get_lang(self):
        return self._lang

    lang = property(get_lang)

    def get_translator(self):
        return self._translator

    translator = property(get_translator)

    def get_translation_type(self):
        return self._translation_type

    translation_type = property(get_translation_type)


class AfHeaderCorpus:
    def __init__(self, file, name, domain):
        self._file = file
        self._name = name
        self._domain = domain

    def get_file(self):
        return self._file

    file = property(get_file)

    def get_name(self):
        return self._name

    name = property(get_name)

    def get_domain(self):
        return self._domain

    domain = property(get_domain)
