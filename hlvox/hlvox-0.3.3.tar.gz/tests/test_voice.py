import sys
from pathlib import Path

import pytest
from hlvox import Voice

from . import utils as th

# Stand-in files for testing
normal_files = ["hello.wav", "my.wav", "name.wav", "is.wav", "vox.wav"]
no_punct_files = ["hello.wav", "my.wav", "name.wav", "is.wav", "vox.wav"]
inconst_format_files = ["hello.mp3", "my.wav", "name", "is.wav", "vox.mp4"]
no_format_files = ["imatextfile", "whatami"]
alarm_files = ["hello.wav", "my.wav", "name.wav", "is.wav", "vox.wav",
               "dadeda.wav", "woop.wav"]
alph_files = ["a.wav", "b.wav", "c.wav"]

# Example info file
ex_info_file = {"alarms": ["dadeda", "woop"]}


class TestFileHandling():
    def test_empty_files(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, [])
        with pytest.raises(Exception) as e:
            Voice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "No words found"

    def test_inconsistent_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, inconst_format_files)
        with pytest.raises(Exception) as e:
            Voice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "Inconsistent Audio Formats"

    def test_no_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, no_format_files)
        with pytest.raises(Exception) as e:
            Voice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "No file format found"

    def test_audio_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, normal_files)
        with Voice(voice_dir, tmp_path.joinpath("db")) as unit:
            assert unit.get_audio_format() == "wav"


class TestDictContents():
    def test_basic_dict(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, normal_files)
        with Voice(voice_dir, tmp_path.joinpath("db")) as unit:

            expected_names = [name[:-4] for name in normal_files]
            expected_names.sort()

            tu_dict = unit.get_words()
        assert expected_names == tu_dict

    def test_alphab(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, alph_files)
        with Voice(voice_dir, tmp_path.joinpath("db")) as unit:

            expected_names = ["a", "b", "c"]

            tu_dict = unit.get_words()
        assert expected_names == tu_dict

    def test_caps(self, tmp_path: Path):
        words = [
            "Cap.wav",
            "Cappa.wav",
        ]
        voice_dir = th.create_voice_files(tmp_path, words)
        with Voice(voice_dir, tmp_path.joinpath("db")) as unit:
            expected_names = ["cap", "cappa"]

            tu_dict = unit.get_words()

        assert expected_names == tu_dict

    @pytest.mark.skipif(sys.platform == "win32", reason="Windows is not case sensitive so duplicates cant exist")
    def test_duplicates(self, tmp_path: Path):
        words = [
            "Cap.wav",
            "cAP.wav",
        ]
        voice_dir = th.create_voice_files(tmp_path, words, touch_only=True)

        with pytest.raises(ValueError):
            Voice(voice_dir, tmp_path.joinpath("db"))

    class TestVoiceInfoLoading():
        def test_alarm_read(self, tmp_path: Path):
            voice_dir = th.create_voice_files(tmp_path, normal_files)
            th.create_info(ex_info_file, voice_dir)
            with Voice(voice_dir, tmp_path.joinpath("db")) as unit:
                assert unit.alarms == ["dadeda", "woop"]


@pytest.fixture
def voice(tmp_path: Path):
    voice_dir = th.create_voice_files(tmp_path, normal_files)
    voice = Voice(voice_dir, tmp_path.joinpath("db"))
    yield voice
    voice.exit()


class TestSentenceList():
    def test_empty_sentence(self, voice: Voice):
        ret = voice.get_sentence_list("")

        assert ret == []

    def test_simple_sentence(self, voice):
        ret = voice.get_sentence_list("hello")

        assert ret == ["hello"]

    def test_simple_punct(self, voice):
        ret = voice.get_sentence_list("hello, world")

        assert ret == ["hello", ","]

    def test_comp_punct(self, voice):
        ret = voice.get_sentence_list("hello , world. Vox , , says hi")

        assert ret == ["hello", ",", ".",
                       "vox", ",", ","]

    def test_punct_only(self, voice):
        ret = voice.get_sentence_list(",")

        assert ret == [","]

    def test_no_space_punct(self, voice):
        ret = voice.get_sentence_list(",.")

        assert ret == [",", "."]

    def test_temp(self, voice):
        ret = voice.get_sentence_list("hello. my name, is, vox")

        assert ret == ["hello", ".", "my", "name",
                       ",", "is", ",", "vox"]

    def test_punct_location(self, voice):
        # Not sure how to deal with types like ".hello"
        # for now it will treat it as just a period and throw out all the characters after it
        ret1 = voice.get_sentence_list("hello.")
        ret2 = voice.get_sentence_list(".hello")
        ret3 = voice.get_sentence_list(".hello.")

        assert ret1 == ["hello", "."]
        assert ret2 == ["."]
        assert ret3 == [".", "."]

    def test_trailing_whitespace(self, voice):
        ret1 = voice.get_sentence_list("hello ")
        ret2 = voice.get_sentence_list("hello\n")
        ret3 = voice.get_sentence_list("hello \n")
        ret4 = voice.get_sentence_list("hello \n\r")
        ret5 = voice.get_sentence_list("hello \n\r vox ")

        assert ret1 == ["hello"]
        assert ret2 == ["hello"]
        assert ret3 == ["hello"]
        assert ret4 == ["hello"]
        assert ret5 == ["hello", "vox"]


class TestSayableUnsayable():
    def test_empty_sent(self, voice: Voice):
        ret_say = voice.get_sayable("")
        ret_unsay = voice.get_unsayable("")

        assert ret_say == []
        assert ret_unsay == []

    def test_simple_sent(self, voice: Voice):
        ret_say = voice.get_sayable("hello")
        ret_unsay = voice.get_unsayable("hello")

        assert ret_say == ["hello"]
        assert ret_unsay == []

    def test_duplicates(self, voice: Voice):
        sent = "hello hello world world , , . . duplicates! duplicates"

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", ",", "."])
        assert not set(ret_unsay) ^ set(["world", "duplicates", "duplicates!"])

    def test_comp_sent(self, voice: Voice):
        sent = "hello, world. Vox can't say some of this."

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", ",", "vox", "."])
        assert not set(ret_unsay) ^ set(
            ["world", "can't", "say", "some", "of", "this"]
        )

    def test_dup_punct(self, voice: Voice):
        sent = "hello... world"

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", "."])
        assert not set(ret_unsay) ^ set(["world"])


class TestSentenceGeneration():
    def test_empty_sent(self, voice: Voice):
        ret = voice.generate_audio("")

        assert ret.sentence == ""
        assert ret.sayable == []
        assert ret.unsayable == []
        assert ret.audio is None

        assert voice.get_generated_sentences_dict() == {}

    def test_unsayable_sent(self, voice: Voice):
        ret = voice.generate_audio("whatthefuckdidyoujustsaytome")

        assert ret.sentence == ""
        assert ret.sayable == []
        assert ret.unsayable == ["whatthefuckdidyoujustsaytome"]
        assert ret.audio is None

        assert voice.get_generated_sentences_dict() == {}

    def test_sayable_sent(self, voice: Voice):
        sentence = "hello, my name is vox"
        ret = voice.generate_audio(sentence)

        assert ret.sentence == "hello , my name is vox"
        assert ret.sayable == [",", "hello", "is", "my", "name", "vox"]
        assert ret.unsayable == []
        assert ret.audio is not None

        assert voice.get_generated_sentences_dict() == {0: "hello , my name is vox"}

    def test_duplicate_sent(self, voice: Voice):
        voice.generate_audio("hello")
        voice.generate_audio("hello")

        assert voice.get_generated_sentences_dict() == {0: "hello"}
        assert len(voice._db) == 1

    def test_duplicate_words(self, voice: Voice):
        ret = voice.generate_audio("hello hello hello")

        assert ret.sentence == "hello hello hello"
        assert ret.sayable == ["hello"]
        assert ret.unsayable == []
        assert ret.audio is not None

    def test_dup_punct(self, voice: Voice):
        ret = voice.generate_audio("hello... hello")

        assert ret.sentence == "hello . . . hello"
        assert ret.sayable == [".", "hello"]
        assert ret.unsayable == []
        assert ret.audio is not None

    def test_multiple_sent(self, voice: Voice):

        voice.generate_audio("hello")
        voice.generate_audio("vox")
        voice.generate_audio(".")
        voice.generate_audio(",")

        assert voice.get_generated_sentences_dict() == {
            0: "hello",
            1: "vox",
            2: ".",
            3: ",",
        }

    def test_dry_run(self, voice: Voice):
        ret = voice.generate_audio("hello", dry_run=True)
        assert ret.audio is None


class test_get_sayable_string():
    def test_simple_sent(self, voice: Voice):
        ret = voice.get_sentence_string("hello")

        assert ret == "hello"

    def test_comp_sent(self, voice: Voice):
        ret = voice.get_sentence_string("hello. my name, is, vox")

        assert ret == "hello . my name , is , vox"


class test_get_generated_sentences():
    def test_no_sentences(self, voice: Voice):
        ret = voice.get_generated_sentences()

        assert ret == []

    def test_single_sentences(self, voice: Voice):
        voice.generate_audio("hello")

        ret = voice.get_generated_sentences()

        assert ret == ["hello"]

    def test_multiple_sentences(self, voice: Voice):
        voice.generate_audio("hello")
        voice.generate_audio("vox")

        ret = voice.get_generated_sentences()

        assert ret == ["hello", "vox"]


class test_get_generated_sentences_dict():
    def test_no_sentences(self, voice: Voice):
        ret = voice.get_generated_sentences_dict()

        assert ret == {}

    def test_single_sentences(self, voice: Voice):
        voice.generate_audio("hello")

        ret = voice.get_generated_sentences_dict()

        assert ret == {0: "hello"}

    def test_multiple_sentences(self, voice: Voice):
        voice.generate_audio("hello")
        voice.generate_audio("vox")

        ret = voice.get_generated_sentences_dict()

        assert ret == {0: "hello", 1: "vox"}
