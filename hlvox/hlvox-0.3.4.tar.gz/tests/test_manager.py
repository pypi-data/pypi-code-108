import unittest
from pathlib import Path

import pytest
from hlvox import Manager, Voice

from . import utils as th

test_files = {
    "v1": ["hello.wav"],
    "v2": ["hello.wav"],
    "v3": ["hello.wav"]
}


@pytest.fixture()
def manager(tmp_path: Path):
    voices_dir = tmp_path.joinpath("voices")
    voices_dir.mkdir()
    for voice, words in test_files.items():
        th.create_voice_files(voices_dir, words, voice)
    m = Manager(voices_path=voices_dir, dbs_path=tmp_path.joinpath("db"))
    yield m
    m.exit()


class TestVoiceImport():
    def test_voice_list(self, manager: Manager):
        expected_voices = list(test_files.keys())
        expected_voices.append("multi")
        expected_voices.sort()
        assert manager.get_voice_names() == expected_voices


class TestGetVoice():
    def test_get_voice(self, manager: Manager):
        v = manager.get_voice("v1")

        assert v is not None
        assert v.name == "v1"

    def test_get_wrong_voice(self, manager: Manager):
        v = manager.get_voice("nope")

        assert not v
