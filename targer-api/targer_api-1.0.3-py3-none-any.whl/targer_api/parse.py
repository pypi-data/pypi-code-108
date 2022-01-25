from math import nan

from targer_api.model import ArgumentLabel, ArgumentTag, ArgumentSentence, \
    ArgumentSentences


def parse_argument_label(json) -> ArgumentLabel:
    return ArgumentLabel(str(json))


def parse_argument_tag(json: dict):
    return ArgumentTag(
        parse_argument_label(json["label"]),
        float(json["prob"]) if "prob" in json else nan,
        str(json["token"])
    )


def parse_argument_sentence(json: list) -> ArgumentSentence:
    return [
        parse_argument_tag(tag)
        for tag in json
    ]


def parse_argument_sentences(json: list) -> ArgumentSentences:
    return [
        parse_argument_sentence(sentence)
        for sentence in json
    ]
