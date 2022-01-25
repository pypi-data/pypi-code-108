from ast import Mult
import sys
from pathlib import Path
from attr import mutable

import pytest
from hlvox import SingleVoice
from hlvox.voice import MultiVoice

from . import utils as th

# Stand-in files for testing
normal_files = ["hello.wav", "my.wav", "name.wav", "is.wav", "vox.wav"]
inconst_format_files = ["hello.mp3", "my.wav", "name", "is.wav", "vox.mp4"]
no_format_files = ["imatextfile", "whatami"]
alph_files = ["a.wav", "b.wav", "c.wav"]

# Example info file
ex_info_file = {"alarms": ["dadeda", "woop"]}


class TestFileHandling():
    def test_empty_files(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, [])
        with pytest.raises(Exception) as e:
            SingleVoice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "No words found"

    def test_inconsistent_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, inconst_format_files)
        with pytest.raises(Exception) as e:
            SingleVoice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "Inconsistent Audio Formats"

    def test_no_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, no_format_files)
        with pytest.raises(Exception) as e:
            SingleVoice(voice_dir, tmp_path.joinpath("db"))

        assert str(e.value) == "No file format found"

    def test_audio_format(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, normal_files)
        with SingleVoice(voice_dir, tmp_path.joinpath("db")) as unit:
            assert unit.get_audio_format() == "wav"


class TestDictContents():
    def test_basic_dict(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, normal_files)
        with SingleVoice(voice_dir, tmp_path.joinpath("db")) as unit:

            expected_names = [name[:-4] for name in normal_files]
            expected_names.sort()
        assert expected_names == unit.words

    def test_alphab(self, tmp_path: Path):
        voice_dir = th.create_voice_files(tmp_path, alph_files)
        with SingleVoice(voice_dir, tmp_path.joinpath("db")) as unit:

            expected_names = ["a", "b", "c"]

        assert expected_names == unit.words

    def test_caps(self, tmp_path: Path):
        words = [
            "Cap.wav",
            "Cappa.wav",
        ]
        voice_dir = th.create_voice_files(tmp_path, words)
        with SingleVoice(voice_dir, tmp_path.joinpath("db")) as unit:
            expected_names = ["cap", "cappa"]

        assert expected_names == unit.words

    @pytest.mark.skipif(sys.platform == "win32", reason="Windows is not case sensitive so duplicates cant exist")
    def test_duplicates(self, tmp_path: Path):
        words = [
            "Cap.wav",
            "cAP.wav",
        ]
        voice_dir = th.create_voice_files(tmp_path, words, touch_only=True)

        with pytest.raises(ValueError):
            SingleVoice(voice_dir, tmp_path.joinpath("db"))

    class TestSingleVoiceInfoLoading():
        def test_alarm_read(self, tmp_path: Path):
            voice_dir = th.create_voice_files(tmp_path, normal_files)
            th.create_info(ex_info_file, voice_dir)
            with SingleVoice(voice_dir, tmp_path.joinpath("db")) as unit:
                assert unit.alarms == ["dadeda", "woop"]


@pytest.fixture
def voice(tmp_path: Path):
    voice_dir = th.create_voice_files(tmp_path, normal_files)
    voice = SingleVoice(voice_dir, tmp_path.joinpath("db"))
    yield voice
    voice.exit()


class TestSentenceList():
    def test_empty_sentence(self, voice: SingleVoice):
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
    def test_empty_sent(self, voice: SingleVoice):
        ret_say = voice.get_sayable("")
        ret_unsay = voice.get_unsayable("")

        assert ret_say == []
        assert ret_unsay == []

    def test_simple_sent(self, voice: SingleVoice):
        ret_say = voice.get_sayable("hello")
        ret_unsay = voice.get_unsayable("hello")

        assert ret_say == ["hello"]
        assert ret_unsay == []

    def test_duplicates(self, voice: SingleVoice):
        sent = "hello hello world world , , . . duplicates! duplicates"

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", ",", "."])
        assert not set(ret_unsay) ^ set(["world", "duplicates", "duplicates!"])

    def test_comp_sent(self, voice: SingleVoice):
        sent = "hello, world. Vox can't say some of this."

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", ",", "vox", "."])
        assert not set(ret_unsay) ^ set(
            ["world", "can't", "say", "some", "of", "this"]
        )

    def test_dup_punct(self, voice: SingleVoice):
        sent = "hello... world"

        ret_say = voice.get_sayable(sent)
        ret_unsay = voice.get_unsayable(sent)

        assert not set(ret_say) ^ set(["hello", "."])
        assert not set(ret_unsay) ^ set(["world"])


class TestSentenceGeneration():
    def test_empty_sent(self, voice: SingleVoice):
        ret = voice.generate_audio("")

        assert ret.sentence == ""
        assert ret.sayable == []
        assert ret.unsayable == []
        assert ret.audio is None

        assert voice.get_generated_sentences_dict() == {}

    def test_unsayable_sent(self, voice: SingleVoice):
        ret = voice.generate_audio("whatthefuckdidyoujustsaytome")

        assert ret.sentence == ""
        assert ret.sayable == []
        assert ret.unsayable == ["whatthefuckdidyoujustsaytome"]
        assert ret.audio is None

        assert voice.get_generated_sentences_dict() == {}

    def test_sayable_sent(self, voice: SingleVoice):
        sentence = "hello, my name is vox"
        ret = voice.generate_audio(sentence)

        assert ret.sentence == "hello , my name is vox"
        assert ret.sayable == [",", "hello", "is", "my", "name", "vox"]
        assert ret.unsayable == []
        assert ret.audio is not None

        assert voice.get_generated_sentences_dict() == {0: "hello , my name is vox"}

    def test_duplicate_sent(self, voice: SingleVoice):
        voice.generate_audio("hello")
        voice.generate_audio("hello")

        assert voice.get_generated_sentences_dict() == {0: "hello"}
        assert len(voice._db) == 1

    def test_duplicate_words(self, voice: SingleVoice):
        ret = voice.generate_audio("hello hello hello")

        assert ret.sentence == "hello hello hello"
        assert ret.sayable == ["hello"]
        assert ret.unsayable == []
        assert ret.audio is not None

    def test_dup_punct(self, voice: SingleVoice):
        ret = voice.generate_audio("hello... hello")

        assert ret.sentence == "hello . . . hello"
        assert ret.sayable == [".", "hello"]
        assert ret.unsayable == []
        assert ret.audio is not None

    def test_multiple_sent(self, voice: SingleVoice):

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

    def test_dry_run(self, voice: SingleVoice):
        ret = voice.generate_audio("hello", dry_run=True)
        assert ret.audio is None


class TestGetSayableString():
    def test_simple_sent(self, voice: SingleVoice):
        ret = voice.get_sentence_string("hello")

        assert ret == "hello"

    def test_comp_sent(self, voice: SingleVoice):
        ret = voice.get_sentence_string("hello. my name, is, vox")

        assert ret == "hello . my name , is , vox"


class TestGetGeneratedSentences():
    def test_no_sentences(self, voice: SingleVoice):
        ret = voice.get_generated_sentences()

        assert ret == []

    def test_single_sentences(self, voice: SingleVoice):
        voice.generate_audio("hello")

        ret = voice.get_generated_sentences()

        assert ret == ["hello"]

    def test_multiple_sentences(self, voice: SingleVoice):
        voice.generate_audio("hello")
        voice.generate_audio("vox")

        ret = voice.get_generated_sentences()

        assert ret == ["hello", "vox"]


class TestGetGeneratedSentencesDict():
    def test_no_sentences(self, voice: SingleVoice):
        ret = voice.get_generated_sentences_dict()

        assert ret == {}

    def test_single_sentences(self, voice: SingleVoice):
        voice.generate_audio("hello")

        ret = voice.get_generated_sentences_dict()

        assert ret == {0: "hello"}

    def test_multiple_sentences(self, voice: SingleVoice):
        voice.generate_audio("hello")
        voice.generate_audio("vox")

        ret = voice.get_generated_sentences_dict()

        assert ret == {0: "hello", 1: "vox"}


@pytest.fixture
def multi_voice(tmp_path: Path):
    norm_voice_dir = th.create_voice_files(tmp_path, normal_files, voice_name='norm')
    alph_voice_dir = th.create_voice_files(tmp_path, alph_files, voice_name='alph')
    alph_2_voice_dir = th.create_voice_files(tmp_path, alph_files, voice_name='alph2')
    norm_voice = SingleVoice(norm_voice_dir, tmp_path.joinpath("norm-db"))
    alph_voice = SingleVoice(alph_voice_dir, tmp_path.joinpath("alph-db"))
    alph_2_voice = SingleVoice(alph_2_voice_dir, tmp_path.joinpath("alph2-db"))
    voices = {
        'norm': norm_voice,
        'alph': alph_voice,
        'alph2': alph_2_voice,
    }
    multi_voice = MultiVoice(
        voices=voices,
        db_path=tmp_path.joinpath('multi-db'),
    )
    yield multi_voice
    multi_voice.exit()
    [voice.exit() for voice in voices.values()]


EXPECTED_MULTI_VOICE_WORDS = [
    'norm:hello', 'norm:is', 'norm:my', 'norm:name',  'norm:vox',
    'alph:a', 'alph:b', 'alph:c',
    'alph2:a', 'alph2:b', 'alph2:c',
]

# Multi-voice tests


class TestMultiWords:
    def test_normal(self, multi_voice: MultiVoice):
        assert multi_voice.words == EXPECTED_MULTI_VOICE_WORDS


class TestMultiProcessSentence:
    # Just want to check that punctuation works as expected
    def test_normal(self, multi_voice: MultiVoice):
        sentence = "norm:hello, my name alph:a, alph2:b."
        exp_words = ["norm:hello", ",", "my", "name", "alph:a", ",", "alph2:b", "."]
        assert multi_voice.process_sentence(sentence) == exp_words


class TestMultiSayableUnsayable:
    def test_empty(self, multi_voice: MultiVoice):
        sayable, unsayable = multi_voice.get_sayable_unsayable(words=[])
        assert not sayable
        assert not unsayable

    def test_all_sayable(self, multi_voice: MultiVoice):
        words = ["norm:hello", "norm:my", "alph:a", "alph2:a"]
        sayable, unsayable = multi_voice.get_sayable_unsayable(words=words)
        words.sort()
        assert sayable == words
        assert not unsayable

    def test_some_unsayable(self, multi_voice: MultiVoice):
        exp_unsayable = ["norm:nope", "alph:butter", "alph2:404"]
        exp_sayable = ["norm:vox", "alph:c", "alph2:c"]
        words = exp_sayable + exp_unsayable
        sayable, unsayable = multi_voice.get_sayable_unsayable(words=words)
        exp_sayable.sort()
        exp_unsayable.sort()
        assert sayable == exp_sayable
        assert unsayable == exp_unsayable

    def test_punctuation(self, multi_voice: MultiVoice):
        words = ["norm:hello", "norm:,", "alph:a", "alph2:."]
        words.sort()
        sayable, unsayable = multi_voice.get_sayable_unsayable(words=words)
        assert sayable == words
        assert not unsayable


class TestMultiWordVoiceAssignment:
    def test_empty(self, multi_voice: MultiVoice):
        assert not multi_voice._get_word_voice_assignment(words=[])

    def test_no_initial_voice(self, multi_voice: MultiVoice):
        words = ["hello", "norm:my"]

        with pytest.raises(Exception):
            multi_voice._get_word_voice_assignment(words=words)

    def test_normal(self, multi_voice: MultiVoice):
        voices = multi_voice._voices
        words = ["norm:hello", "my", "alph:a", "a", "alph2:a", "norm:vox", "is", "alph:b"]
        exp_words_and_voices = [
            ("hello", voices["norm"]),
            ("my", voices["norm"]),
            ("a", voices["alph"]),
            ("a", voices["alph"]),
            ("a", voices["alph2"]),
            ("vox", voices["norm"]),
            ("is", voices["norm"]),
            ("b", voices["alph"]),
        ]

        assert multi_voice._get_word_voice_assignment(words=words) == exp_words_and_voices

    def test_punctuation(self, multi_voice: MultiVoice):
        voices = multi_voice._voices
        words = ["norm:hello", ",", "alph:a", "a", ".", "alph2:a", "norm:vox", "is", "alph:b"]
        exp_words_and_voices = [
            ("hello", voices["norm"]),
            (",", voices["norm"]),
            ("a", voices["alph"]),
            ("a", voices["alph"]),
            (".", voices["alph"]),
            ("a", voices["alph2"]),
            ("vox", voices["norm"]),
            ("is", voices["norm"]),
            ("b", voices["alph"]),
        ]

        assert multi_voice._get_word_voice_assignment(words=words) == exp_words_and_voices


class TestMultiCombinedVoiceSentences:
    def test_empty(self, multi_voice: MultiVoice):
        assert not multi_voice.get_combined_voice_sentences(words_and_voices=[])

    def test_single(self, multi_voice: MultiVoice):
        voices = multi_voice._voices
        words_and_voices = [
            ("hello", voices["norm"])
        ]

        exp = [(voices["norm"], ["hello"])]
        assert multi_voice.get_combined_voice_sentences(words_and_voices=words_and_voices) == exp

    def test_multiple(self, multi_voice: MultiVoice):
        voices = multi_voice._voices
        words_and_voices = [
            ("hello", voices["norm"]),
            ("my", voices["norm"]),
            ("a", voices["alph"]),
            ("a", voices["alph"]),
            ("a", voices["alph2"]),
            ("vox", voices["norm"]),
            ("is", voices["norm"]),
            ("b", voices["alph"]),
        ]

        exp = [
            (voices["norm"], ["hello", "my"]),
            (voices["alph"], ["a", "a"]),
            (voices["alph2"], ["a"]),
            (voices["norm"], ["vox", "is"]),
            (voices["alph"], ["b"]),
        ]
        assert multi_voice.get_combined_voice_sentences(words_and_voices=words_and_voices) == exp


class TestMultiGenerateAudio:
    def test_normal(self, multi_voice: MultiVoice):
        sentence = "norm:hello, my name is vox. alph:a b c"
        ret = multi_voice.generate_audio(sentence=sentence)

        exp_sentence = "norm:hello norm:, norm:my norm:name norm:is norm:vox norm:. alph:a alph:b alph:c"
        assert ret.sentence == exp_sentence
