from typing import List

from pytest import fixture

from targer_api import (
    ArgumentLabel, ArgumentTag, ArgumentSentence, ArgumentSentences
)


@fixture
def argument_label() -> ArgumentLabel:
    return ArgumentLabel.C_I


@fixture
def argument_tag(argument_label: ArgumentLabel) -> ArgumentTag:
    return ArgumentTag(argument_label, 0.7, "house")


def test_argument_tag(argument_tag: ArgumentTag):
    assert isinstance(argument_tag.label, ArgumentLabel)
    assert argument_tag.label == ArgumentLabel.C_I
    assert argument_tag.probability == 0.7
    assert argument_tag.token == "house"


@fixture
def argument_sentence(argument_tag: ArgumentTag) -> ArgumentSentence:
    return [argument_tag]


def test_argument_sentence(argument_sentence: ArgumentSentence):
    assert len(argument_sentence) == 1
    assert isinstance(argument_sentence[0], ArgumentTag)


@fixture
def argument_sentences(
        argument_sentence: ArgumentSentence
) -> ArgumentSentences:
    return [argument_sentence]


def test_argument_sentences(argument_sentences: ArgumentSentences):
    assert len(argument_sentences) == 1
    assert isinstance(argument_sentences[0], List)
