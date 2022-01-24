from pathlib import Path
from typing import List

from pytest import approx, fixture

from targer_api import analyze_text, ArgumentTag, ArgumentLabel


@fixture
def text() -> str:
    return (
        "The alternative vote is advantageous. "
        "The President is directly elected by secret ballot "
        "under the system of the Alternative Vote."
    )


@fixture
def model() -> str:
    return "tag-ibm-fasttext"


@fixture
def api_url() -> str:
    return "https://demo.webis.de/targer-api/"


@fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_fetch_arguments_single(
        text: str,
        model: str,
        api_url: str,
        cache_dir: Path,
):
    sentences = analyze_text(text, model, api_url, cache_dir)

    assert isinstance(sentences, List)
    assert len(sentences) == 2

    sentence1, sentence2 = sentences
    assert isinstance(sentence1, List)
    assert len(sentence1) == 6
    assert isinstance(sentence2, List)
    assert len(sentence2) == 16

    sentence1_token2 = sentence1[1]
    assert isinstance(sentence1_token2, ArgumentTag)
    assert isinstance(sentence1_token2.label, ArgumentLabel)
    assert sentence1_token2.label == ArgumentLabel.C_B
    assert sentence1_token2.probability == approx(0.6908648)
    assert sentence1_token2.token == "alternative"

    sentence2_token2 = sentence2[1]
    assert isinstance(sentence2_token2, ArgumentTag)
    assert isinstance(sentence2_token2.label, ArgumentLabel)
    assert sentence2_token2.label == ArgumentLabel.P_B
    assert sentence2_token2.probability == approx(0.9999801)
    assert sentence2_token2.token == "President"


def test_fetch_arguments_multi(
        text: str,
        model: str,
        api_url: str,
        cache_dir: Path,
):
    model_sentences = analyze_text(text, {model}, api_url, cache_dir)

    assert len(model_sentences) == 1
    assert model in model_sentences.keys()

    sentences = model_sentences[model]
    assert isinstance(sentences, List)
    assert len(sentences) == 2

    sentence1, sentence2 = sentences
    assert isinstance(sentence1, List)
    assert len(sentence1) == 6
    assert isinstance(sentence2, List)
    assert len(sentence2) == 16

    sentence1_token2 = sentence1[1]
    assert isinstance(sentence1_token2, ArgumentTag)
    assert isinstance(sentence1_token2.label, ArgumentLabel)
    assert sentence1_token2.label == ArgumentLabel.C_B
    assert sentence1_token2.probability == approx(0.6908648)
    assert sentence1_token2.token == "alternative"

    sentence2_token2 = sentence2[1]
    assert isinstance(sentence2_token2, ArgumentTag)
    assert isinstance(sentence2_token2.label, ArgumentLabel)
    assert sentence2_token2.label == ArgumentLabel.P_B
    assert sentence2_token2.probability == approx(0.9999801)
    assert sentence2_token2.token == "President"
