import argparse
from email.mime import audio
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import tinydb
from pydub import AudioSegment

log = logging.getLogger(__name__)


# How much delay should be added in place of punctuation (in milliseconds)
PUNCTUATION_TIMING = {
    ',': 250,
    '.': 500,
}

DB_NAME = 'db.json'


@dataclass
class Sentence:
    sentence: str
    sayable: List[str]
    unsayable: List[str]
    audio: Optional[AudioSegment] = None


class Voice:
    """Base class for Voice-like interfaces.
    Intended to involve generation of audio
    files from some source (files, web, etc).
    """

    def __init__(self, name: str, db_path: Path):
        self.name = name

        self._db_path = db_path
        self._db = self._setup_db(self._db_path, DB_NAME)

        self.words: List[str] = []
        self.alarms: List[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.close()

    # TODO: Need a better way to handle this
    def exit(self):
        self._db.close()

    def _setup_db(self, path: Path, db_name: str) -> tinydb.TinyDB:
        """Sets up or finds existing database.

        Args:
            path (Path): Path to find or create database at.
            db_name (str): Name of database file.

        Returns:
            tinydb.TinyDB: Database.
        """
        path.mkdir(parents=True, exist_ok=True)
        return tinydb.TinyDB(path.joinpath(db_name))

    def _get_sentence_info(self, words: List[str]) -> Tuple[Sentence, List[str]]:
        """Get basic sentence info for a given
        split sentence.

        Args:
            words (List[str]): Words of sentence split into array

        Returns:
            Tuple[Sentence, List[str]]: Sentence info and sayable sentence array
        """
        sayable_words, unsayable_worlds = self.get_sayable_unsayable(words)
        sayable_sent_arr = self._get_sayable_sentence_arr(
            words, sayable_words)
        sayable_sent_str = self._create_sentence_string(sayable_sent_arr)

        sentence = Sentence(
            sentence=sayable_sent_str,
            sayable=sayable_words,
            unsayable=unsayable_worlds,
            audio=None,
        )
        return sentence, sayable_sent_arr

    def _generate_audio_from_array(self, words: List[str], dry_run=False) -> Sentence:
        """Generates audio segment from sentence array.

        Args:
            words (List[str]): Words to try and turn into audio segment.
            dry_run (bool, optional): Skip actual segment generation. Defaults to False.

        Returns:
            Sentence: Sentence with audio segment.
        """
        sentence_info, sayable_sentence_array = self._get_sentence_info(words=words)

        if dry_run:
            return sentence_info

        log.debug(f"Generating {sentence_info.sentence}")

        # Only create sentence if there are words to put in it
        if len(sentence_info.sayable) == 0:
            log.warning(
                f"Can't say any words in {sentence_info.sentence}, not generating")
            return sentence_info

        q = self._db.search(tinydb.where("sentence") == sentence_info.sentence)
        if not len(q):
            self._db.insert({"sentence": sentence_info.sentence})

        words_audio = self._create_audio_segments(sayable_sentence_array)

        sentence_info.audio = self.assemble_audio_segments(words_audio)

        return sentence_info

    def _create_audio_segments(self, word_array: List[str]) -> List[AudioSegment]:
        """Create audio segments for each entry in an array of words.

        Args:
            word_array (List[str]): Words to turn into audio segments.

        Returns:
            List[AudioSegment]: Audio segments.
        """
        return []

    def generate_audio(self, sentence: str, dry_run=False) -> Sentence:
        """Generates audio from the given sentence

        Args:
            sentence (string): Sentence string to be generated
            dry_run (bool, optional): Don't generate audio. Defaults to False.
        Returns:
            Sentence: Information about generated sentence.
        """
        log.info(f"Asked to generate {sentence}")
        proc_sentence = self.process_sentence(sentence)
        return self._generate_audio_from_array(
            words=proc_sentence,
            dry_run=dry_run
        )

    @staticmethod
    def process_sentence(sentence: str) -> List[str]:
        """
        Takes a normally formatted sentence and breaks it into base elements

        Args:
            sentence (string): normally formatted sentence to be processed

        Returns:
            List[str]: array of elements in sentence
        """
        # TODO: This could use some rethinking. Should be easier to just always break punctuation marks
        # into their own elements, rather than selectively only dealing with trailing ones.
        split_sent = sentence.lower().rstrip().split(" ")
        log.info(f"Processing sentence '{sentence}'")

        # Pull out punctuation
        reduced_sent = []
        for item in split_sent:
            # find first punctuation mark, if any
            first_punct: Optional[str] = None
            try:
                first_punct = next(
                    (punct for punct in PUNCTUATION_TIMING if punct in item))
            except StopIteration:
                pass

            if first_punct:
                # Get its index
                first_punct_ind = item.find(first_punct)

                # Add everything before punct (the word)
                reduced_sent.append(item[:first_punct_ind])

                # Add all the punctuation if its actually punctuation
                # TODO: Figure out if I want to deal with types like ".hello" throwing out all the characters after the period.
                for punct in item[first_punct_ind:]:
                    if punct in PUNCTUATION_TIMING:
                        reduced_sent.append(punct)

            else:
                reduced_sent.append(item)

        # Clean blanks from reduced_sent
        if '' in reduced_sent:
            reduced_sent = [value for value in reduced_sent if value != '']

        log.info(f"Sentence processed: '{reduced_sent}'")
        return reduced_sent

    def get_sayable_unsayable(self, words: List[str]) -> Tuple[List[str], List[str]]:
        """Get words that are sayable or unsayable
        from a list of words.

        Args:
            words (List[str]): Words to check.

        Returns:
            Tuple[List[str], List[str]]: Sayable and unsayable words.
        """
        # TODO: This shouldn't need two separate processings of the same sentence. Sets, people. Sets!
        sayable_words = self.words
        sayable_words_set = set(sayable_words)
        sayable_words_set.update(list(PUNCTUATION_TIMING.keys()))

        words_set = set((dict.fromkeys(words)))  # removes duplicates

        unsayable_set = words_set - sayable_words_set
        sayable_set = words_set - unsayable_set
        unsayable = list(unsayable_set)
        unsayable.sort()
        sayable = list(sayable_set)
        sayable.sort()
        return sayable, unsayable

    def _get_sayable_sentence_arr(self, words: List[str], sayable_words: List[str]) -> List[str]:
        """Removes words from sentence array that are not sayable.

        Args:
            words (List[str]): Array of words in sentence, in order.
            sayable_words (List[str]): Words from sentence that can actually be said.

        Returns:
            List[str]: Words in sentence that are sayable, in order.
        """
        # TODO: This is just a simple set operation. Function probably isn't needed. At least change to using a set.
        return [word for word in words if word in sayable_words]

    def _create_sentence_string(self, words: List[str]) -> str:
        """Joins sentence array into a string.

        Args:
            words (List[str]): Words in sentence, in order.

        Returns:
            str: Sentence string.
        """
        if len(words) == 1:
            return words[0]
        else:
            return " ".join(words)

    def get_sayable(self, sentence: str) -> List[str]:
        """Gets the words that the voice can say from a sentence

        Args:
            sentence (string): Sentence to check for sayable words
        Returns:
            List[str]: Words that can be said
        """

        proc_sentence = self.process_sentence(sentence)
        sayable, _ = self.get_sayable_unsayable(proc_sentence)
        return sayable

    def get_unsayable(self, sentence: str) -> List[str]:
        """Gets the words that the voice cannot say from a sentence

        Args:
            sentence (string): Sentence to check for un-sayable words
        Returns:
            List[str]: Words that cannot be said
        """

        proc_sentence = self.process_sentence(sentence)
        _, unsayable = self.get_sayable_unsayable(proc_sentence)
        return unsayable

    def get_sentence_list(self, sentence: str) -> List[str]:
        """Converts sentence into list of words that can be said

        Args:
            sentence (string): Sentence to convert to list
        Returns:
            List[str]: Sentence in list format excluding words that cannot be said
        """

        proc_sentence = self.process_sentence(sentence)
        sayable, _ = self.get_sayable_unsayable(proc_sentence)
        return self._get_sayable_sentence_arr(proc_sentence, sayable)

    def get_sentence_string(self, sentence: str) -> str:
        """Converts input sentence string to generalized output sentence string.
        Ex: "hello, there" -> "hello , there"

        Args:
            sentence (str): Sentence string.

        Returns:
            str: Generalized sentence string.
        """
        proc_sentence = self.process_sentence(sentence)
        sayable_words, _ = self.get_sayable_unsayable(proc_sentence)
        sayable_sent_arr = self._get_sayable_sentence_arr(
            proc_sentence, sayable_words)

        return self._create_sentence_string(sayable_sent_arr)

    def get_generated_sentences(self) -> List[str]:
        """Gets the previously generated sentence strings

        Returns:
            List[str]: List of sentence strings generated previously
        """
        return [entry["sentence"] for entry in self._db.all()]

    @staticmethod
    def assemble_audio_segments(segments: List[AudioSegment]) -> AudioSegment:
        """Assemble audio segments into one audio segment.

        Args:
            segments (List[AudioSegment]): Segments to assemble.

        Returns:
            AudioSegment: Assembled audio segment.
        """
        # We set all audio segments to the lowest common frame rate
        # to avoid some really ugly artifacting when a low frame rate
        # clip is appended to a high frame rate one.
        frame_rates = [word.frame_rate for word in segments]
        frame_rate = min(frame_rates)

        sentence_audio = segments.pop(0)
        sentence_audio = sentence_audio.set_frame_rate(frame_rate)
        for word_audio in segments:
            word_audio = word_audio.set_frame_rate(frame_rate)
            sentence_audio = sentence_audio + word_audio

        return sentence_audio

    def get_generated_sentences_dict(self) -> Dict[int, str]:
        """Gets the previously generated sentence strings
        along with their corresponding ID in the database

        Returns:
            Dict[int, str]: Dict of sentence and id pairs
        """
        entries = self._db.all()
        return {entries.index(entry): entry["sentence"] for entry in entries}


class SingleVoice(Voice):
    """Comprises all information and methods
    needed to index a folder of voice audio files
    and generate audio from them given a sentence string.
    """

    def __init__(self, path: Path, db_path: Path):
        """
        Args:
            path (Path): Path to folder of voice audio files.
            db_path (Path): Path to find or create database at.
        """
        super().__init__(name=path.name, db_path=db_path)
        self.path = path

        self.info_path = self.path.joinpath("info/")
        self.info_name = "info.json"

        self._word_dict = self._build_word_dict(self.path)
        self._audio_format = self._find_audio_format(
            self._word_dict)  # TODO: Use properies?

        self.words = self._get_words()

        self._read_info(self.info_path, self.info_name)

    def _build_word_dict(self, path: Path) -> Dict[str, Path]:
        """Builds dictionary of all available words.

        Args:
            path (Path): Path to folder of voice audio files.

        Raises:
            ValueError: Raised if there are duplicate filenames present.
            Exception: Raised if no words are found.

        Returns:
            Dict[str, Path]: Dict of {filepath: word} associations.
        """
        word_dict = {}
        word_files = list(x for x in path.iterdir() if x.is_file())

        for word in word_files:
            word = Path(word)
            name = str(word.stem).lower()
            if name in word_dict:
                raise ValueError(f"Word {name} is duplicated")
            word_dict[name] = word

        if len(word_dict) == 0:
            log.error("No words found")
            # TODO: Better default exception, or make some custom ones
            raise Exception("No words found")

        return word_dict

    def _read_info(self, path: Path, info_name: str):
        """Reads info file (if it exists)
        which may contain information about special
        groupings of words (like alarms)

        Args:
            path (Path): Path where info file resides.
            info_name (str): Name of info file.
        """
        # TODO: Allow arbitrary groupings of words
        info_path = path.joinpath(info_name)
        if info_path.exists():
            with open(info_path, 'r') as info_file:
                info = json.load(info_file)
                self.alarms = info["alarms"]
        log.info(f"Available alarms are {self.alarms}")

    def _find_audio_format(self, word_dict: Dict[str, Path]) -> str:
        """Determines audio format of voice audio files.

        Args:
            word_dict (Dict[str, Path]): Dict of {filepath: word} associations.

        Raises:
            Exception: Raised if no audio format can be determined,
                or if there are inconsistent audio formats.

        Returns:
            str: Audio format.
        """
        file_format = None
        for path in word_dict.values():
            if file_format == None:
                file_format = path.suffix[1:]
            else:
                if str(file_format) != str(path.suffix[1:]):
                    log.error(
                        "Inconsistent audio formats in the word dict. "
                        f"File {path} does not match expected format of {file_format}"
                    )
                    # TODO: Better default exception, or make some custom ones
                    raise Exception("Inconsistent Audio Formats")
        if not file_format:
            # TODO: Better default exception, or make some custom ones
            raise Exception("No file format found")
        log.info(f"Audio format found: {file_format}")
        return file_format

    def _get_words(self) -> List[str]:
        """Gets the available words for the voice

        Returns:
            List[str]: Words available to the voice
        """
        word_list = list(self._word_dict.keys())
        word_list.sort()
        return word_list

    def get_audio_format(self) -> str:
        """Get the audio format of the voice files as well as generated files
        Returns:
            (string): Audio format
        """
        return self._audio_format

    def _create_audio_segments(self, word_array: List[str]) -> List[AudioSegment]:
        words_audio: List[AudioSegment] = []
        for word in word_array:
            if word in PUNCTUATION_TIMING:
                words_audio.append(AudioSegment.silent(
                    PUNCTUATION_TIMING[word]))
            else:
                words_audio.append(AudioSegment.from_file(
                    self._word_dict[word], self._audio_format))
        return words_audio


class MultiVoice(Voice):
    """Voice class that uses other voices to assemble
    multi-voice sentences.

    Example: vox:hello hev:there
    Generates a sentence with one word from a voice
    called "vox" and another from a voice called "hev."
    """

    def __init__(self, voices: Dict[str, SingleVoice], db_path: Path):
        """
        Args:
            voices (Dict[str, SingleVoice]): Voices to use to assemble sentences.
            db_path (Path): Path to database.
        """
        super().__init__(name='multi', db_path=db_path)
        self._voices = voices

        self.words = self._get_words(voices)
        self.alarms = []

    def _get_words(self, voices: Dict[str, SingleVoice]):
        words = []
        for name, voice in voices.items():
            voice_words = [f'{name}:{word}' for word in voice.words]
            words.extend(voice_words)
        return words

    def _get_word_and_voice_strings(self, words_and_voices: List[Tuple[str, SingleVoice]]) -> List[str]:
        """Turns array of word:voice assignments into string.

        Example: "vox:hello vox:there hev:doctor hev:freeman

        Args:
            words_and_voices (List[Tuple[str, SingleVoice]]): Word:voice assignments

        Returns:
            List[str]: Combined string
        """
        return [f'{voice.name}:{word}' for word, voice in words_and_voices]

    def _get_sentence_info(self, words: List[str]) -> Tuple[Sentence, List[str]]:
        # TODO: There is a good amount of double-processing going on here
        words_and_voices = self._get_word_voice_assignment(words)
        words_and_voices_strings = self._get_word_and_voice_strings(words_and_voices)
        sayable_words, unsayable_words = self.get_sayable_unsayable(words_and_voices_strings)
        sayable_sent_arr = [word_voice for word_voice in words_and_voices_strings if word_voice in sayable_words]
        sayable_sent_str = ' '.join(sayable_sent_arr)

        sentence = Sentence(
            sentence=sayable_sent_str,
            sayable=sayable_words,
            unsayable=unsayable_words,
            audio=None,
        )
        return sentence, sayable_sent_arr

    def get_sayable_unsayable(self, words: List[str]) -> Tuple[List[str], List[str]]:
        sayable = []
        unsayable = []
        words_and_voices = self._get_word_voice_assignment(words=words)
        combined_voice_sentences = self.get_combined_voice_sentences(words_and_voices)
        for voice, words in combined_voice_sentences:
            voice_sayable, voice_unsayable = voice.get_sayable_unsayable(words)
            voice_sayable = [f'{voice.name}:{word}' for word in voice_sayable]
            voice_unsayable = [f'{voice.name}:{word}' for word in voice_unsayable]
            sayable.extend(voice_sayable)
            unsayable.extend(voice_unsayable)
        sayable.sort()
        unsayable.sort()
        return sayable, unsayable

    def _create_audio_segments(self, word_array: List[str]) -> List[AudioSegment]:
        words_and_voices = self._get_word_voice_assignment(word_array)
        combined_voice_sentences = self.get_combined_voice_sentences(words_and_voices)
        return self.get_combined_audio(
            voice_sentences=combined_voice_sentences,
        )

    def _get_word_voice_assignment(self, words: List[str]) -> List[Tuple[str, SingleVoice]]:
        """Determins voice for each word in a list separated
        from a raw sentence. Only the first word must have a voice
        assignment, further assignments are inferred.

        Example: vox:hello there hev:doctor freeman
        The first two words are assigned to vox, second two to hev

        Args:
            words (List[str]): Words to determine voice assignment of

        Returns:
            List[Tuple[str, SingleVoice]]: word:voice assignments
        """
        words_and_voices: List[Tuple[str, SingleVoice]] = []

        current_voice: Optional[SingleVoice] = None
        for word_maybe_voice in words:
            word_split = word_maybe_voice.split(':')
            word: Optional[str] = None
            voice: Optional[str] = None
            if len(word_split) == 1:
                word = word_split[0]
            elif len(word_split) == 2:
                voice = word_split[0]
                word = word_split[1]
            if not word:
                raise Exception(f"Failed to split {word_maybe_voice}")

            if voice:
                current_voice = self._voices[voice]
            if not current_voice:
                raise Exception("No voice was specified for starting word!")
            word_and_voice = (word, current_voice)
            words_and_voices.append(word_and_voice)

        return words_and_voices

    def get_combined_voice_sentences(self, words_and_voices: List[Tuple[str, SingleVoice]]) -> List[Tuple[SingleVoice, List[str]]]:
        """Turns individual word:voice assignments into
        combined sentences for each word in sequence:

        Example: vox:hello vox: there hev:doctor hev:freeman vox:boop
        Returns vox:[hello, there] hev:[doctor freeman] vox:[boop]

        Args:
            words_and_voices (List[Tuple[str, SingleVoice]]): Word:voice assignments

        Returns:
            List[Tuple[SingleVoice, List[str]]]: Voice:sentence assignments
        """
        current_voice: Optional[SingleVoice] = None
        current_voice_sentence: List[str] = []
        voice_sentences: List[Tuple[SingleVoice, List[str]]] = []
        for word, voice in words_and_voices:
            if not current_voice:
                current_voice = voice
            if voice == current_voice:
                current_voice_sentence.append(word)
            else:
                voice_sentences.append((current_voice, current_voice_sentence))
                current_voice = voice
                current_voice_sentence = [word]
        if current_voice and current_voice_sentence:
            voice_sentences.append((current_voice, current_voice_sentence))
        return voice_sentences

    def get_combined_audio(self, voice_sentences: List[Tuple[SingleVoice, List[str]]]) -> List[AudioSegment]:
        """Generates audio segments for each voice sentence

        Args:
            voice_sentences (List[Tuple[SingleVoice, List[str]]]): Voice:sentence assignments

        Returns:
            List[AudioSegment]: List of generated audio segments
        """
        audio_segments = []
        for voice, words in voice_sentences:
            sentence = voice._generate_audio_from_array(words)
            if sentence.audio:
                audio_segments.append(sentence.audio)
        return audio_segments


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description='Generate a sentence using a voice')
    parser.add_argument('-s', '--voice-dir', type=str, required=True, help='Path to folder with voice audio files')
    parser.add_argument('-d', '--db', type=str, required=True, help='Path to store database file')
    parser.add_argument('-f', '--format', type=str, required=False, default='wav', help='Audio format to export as')
    parser.add_argument('sentence', type=str)
    args = parser.parse_args()

    voice_dir = Path(args.voice_dir)
    if not voice_dir.is_dir():
        print(f'Voice dir at {voice_dir} does not exist!')
        sys.exit(1)

    db_path = Path(args.db)

    voice = SingleVoice(path=voice_dir, db_path=db_path)
    sentence = voice.generate_audio(args.sentence)
    if sentence is None or sentence.audio is None:
        sys.exit(1)

    output_path = Path.cwd().joinpath(f"{sentence.sentence}.{args.format}")

    sentence.audio.export(output_path, format=args.format)
