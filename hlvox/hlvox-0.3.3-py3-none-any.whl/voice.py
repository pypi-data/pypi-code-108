import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import tinydb
from pydub import AudioSegment

log = logging.getLogger(__name__)


@dataclass
class Sentence:
    sentence: str
    sayable: List[str]
    unsayable: List[str]
    audio: Optional[AudioSegment] = None


class Voice:
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
        self.path = path

        self.info_path = self.path.joinpath("info/")
        self.info_name = "info.json"

        self.db_path = Path(db_path)
        self.db_name = "db.json"

        self.name = self.path.name

        self._punctuation = [",", "."]
        self._punctuation_timing = {",": 250, ".": 500}

        self.alarms: List[str] = []

        self._db = self._setup_db(self.db_path, self.db_name)

        self._word_dict = self._build_word_dict(self.path)
        self._audio_format = self._find_audio_format(
            self._word_dict)  # TODO: Use properies?

        self._read_info(self.info_path, self.info_name)

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

    def _process_sentence(self, sentence: str) -> List[str]:
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
                    (punct for punct in self._punctuation if punct in item))
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
                    if punct in self._punctuation:
                        reduced_sent.append(punct)

            else:
                reduced_sent.append(item)

        # Clean blanks from reduced_sent
        if '' in reduced_sent:
            reduced_sent = [value for value in reduced_sent if value != '']

        log.info(f"Sentence processed: '{reduced_sent}'")
        return reduced_sent

    def _get_sayable_words(self, processed_sentence_arr: List[str], word_dict: Dict[str, Path]) -> List[str]:
        """Gets words in a sentence array that are available to be "said."

        Args:
            processed_sentence_arr (List[str]): Array of words in requested sentence.
            word_dict (Dict[str, Path]): Dict of {filepath: word} associations.

        Returns:
            List[str]: Sayable words.
        """
        sayable = [
            word for word in processed_sentence_arr if word in word_dict or word in self._punctuation]
        sayable_dedup = list(dict.fromkeys(sayable))  # removes duplicates
        sayable_dedup.sort()
        return sayable_dedup

    def _get_unsayable_words(self, processed_sentence_arr: List[str], sayable_words: List[str]) -> List[str]:
        """Gets words in a sentence array that are NOT available to be "said."

        Args:
            processed_sentence_arr (List[str]): Array of words in requested sentence.
            word_dict (List[str]): Dict of {filepath: word} associations.

        Returns:
            List[str]: Unsayable words.
        """
        unsayable = list(set(processed_sentence_arr) - set(sayable_words))
        return list(dict.fromkeys(unsayable))  # removes duplicates

    def _get_sayable_sentence_arr(self, processed_sentence_arr: List[str], sayable_words: List[str]) -> List[str]:
        """Removes words from sentence array that are not sayable.

        Args:
            processed_sentence_arr (List[str]): Array of words in sentence, in order.
            sayable_words (List[str]): Words from sentence that can actually be said.

        Returns:
            List[str]: Words in sentence that are sayable, in order.
        """
        # TODO: This is just a simple set operation. Function probably isn't needed. At least change to using a set.
        return [word for word in processed_sentence_arr if word in sayable_words]

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

    def get_words(self) -> List[str]:
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

    def get_sayable(self, sentence: str) -> List[str]:
        """Gets the words that the voice can say from a sentence

        Args:
            sentence (string): Sentence to check for sayable words
        Returns:
            List[str]: Words that can be said
        """

        proc_sentence = self._process_sentence(sentence)
        return self._get_sayable_words(proc_sentence, self._word_dict)

    def get_unsayable(self, sentence: str) -> List[str]:
        """Gets the words that the voice cannot say from a sentence

        Args:
            sentence (string): Sentence to check for un-sayable words
        Returns:
            List[str]: Words that cannot be said
        """

        proc_sentence = self._process_sentence(sentence)
        sayable_words = self._get_sayable_words(proc_sentence, self._word_dict)
        return self._get_unsayable_words(proc_sentence, sayable_words)

    def get_sentence_list(self, sentence: str) -> List[str]:
        """Converts sentence into list of words that can be said

        Args:
            sentence (string): Sentence to convert to list
        Returns:
            List[str]: Sentence in list format excluding words that cannot be said
        """

        proc_sentence = self._process_sentence(sentence)
        sayable_words = self._get_sayable_words(proc_sentence, self._word_dict)
        return self._get_sayable_sentence_arr(proc_sentence, sayable_words)

    def get_sentence_string(self, sentence: str) -> str:
        """Converts input sentence string to generalized output sentence string.
        Ex: "hello, there" -> "hello , there"

        Args:
            sentence (str): Sentence string.

        Returns:
            str: Generalized sentence string.
        """
        proc_sentence = self._process_sentence(sentence)
        sayable_words = self._get_sayable_words(
            proc_sentence, self._word_dict)
        sayable_sent_arr = self._get_sayable_sentence_arr(
            proc_sentence, sayable_words)

        return self._create_sentence_string(sayable_sent_arr)

    def get_generated_sentences(self) -> List[str]:
        """Gets the previously generated sentence strings

        Returns:
            List[str]: List of sentence strings generated previously
        """
        return [entry["sentence"] for entry in self._db.all()]

    def generate_audio(self, sentence: str, dry_run=False) -> Sentence:
        """Generates an audio file from the given sentence

        Args:
            sentence (string): Sentence string to be generated
            dry_run (bool, optional): Don't generate audio. Defaults to False.
        Returns:
            Sentence: Information about generated sentence.
        """

        log.info(f"Asked to generate {sentence}")
        proc_sentence = self._process_sentence(sentence)

        sayable_words = self._get_sayable_words(proc_sentence, self._word_dict)
        sayable_sent_arr = self._get_sayable_sentence_arr(
            proc_sentence, sayable_words)
        sayable_sent_str = self._create_sentence_string(sayable_sent_arr)
        unsayable_worlds = self._get_unsayable_words(
            proc_sentence, sayable_words)

        sentence_info = Sentence(
            sentence=sayable_sent_str,
            sayable=sayable_words,
            unsayable=unsayable_worlds,
            audio=None,
        )

        if dry_run:
            return sentence_info

        log.debug(f"Generating {sayable_sent_str}")

        words_audio: List[AudioSegment] = []

        # Only create sentence if there are words to put in it
        if len(sayable_words) == 0:
            log.warning(
                f"Can't say any words in {sentence}, not generating")
            return sentence_info

        q = self._db.search(tinydb.where("sentence") == sayable_sent_str)
        if not len(q):
            self._db.insert({"sentence": sayable_sent_str})

        for word in sayable_sent_arr:
            if word in self._punctuation_timing:
                words_audio.append(AudioSegment.silent(
                    self._punctuation_timing[word]))
            else:
                words_audio.append(AudioSegment.from_file(
                    self._word_dict[word], self._audio_format))

        # We set all audio segments to the lowest common frame rate
        # to avoid some really ugly artifacting when a low frame rate
        # clip is appended to a high frame rate one.
        frame_rates = [word.frame_rate for word in words_audio]
        frame_rate = min(frame_rates)

        sentence_audio = words_audio.pop(0)
        sentence_audio = sentence_audio.set_frame_rate(frame_rate)
        for word_audio in words_audio:
            word_audio = word_audio.set_frame_rate(frame_rate)
            sentence_audio = sentence_audio + word_audio
        sentence_info.audio = sentence_audio

        return sentence_info

    def get_generated_sentences_dict(self) -> Dict[int, str]:
        """Gets the previously generated sentence strings
        along with their corresponding ID in the database

        Returns:
            Dict[int, str]: Dict of sentence and id pairs
        """
        entries = self._db.all()
        return {entries.index(entry): entry["sentence"] for entry in entries}


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

    voice = Voice(path=voice_dir, db_path=db_path)
    sentence = voice.generate_audio(args.sentence)
    if sentence is None or sentence.audio is None:
        sys.exit(1)

    output_path = Path.cwd().joinpath(f"{sentence.sentence}.{args.format}")

    sentence.audio.export(output_path, format=args.format)
