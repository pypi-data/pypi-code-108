import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from hlvox.voice import Voice, SingleVoice, MultiVoice

log = logging.getLogger(__name__)


class Manager:
    def __init__(self, voices_path: Union[Path, str], dbs_path: Union[Path, str]):
        self.voices_path = Path(voices_path)
        self.dbs_path = Path(dbs_path)
        # TODO: How do I make mypy happy here regarding Voice: SingleVoice, MultiVoice?
        self.voices: Dict[str, Voice] = self._load_voices(self.voices_path)
        self.voices['multi'] = self._create_multi_voice(self.voices)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit()

    def _create_db_path(self, dbs_path: Path, voice_name: str) -> Path:
        db_path = dbs_path / voice_name
        db_path.mkdir(parents=True, exist_ok=True)
        return db_path

    def _load_voices(self, path: Path) -> Dict[str, SingleVoice]:
        voices = {}
        voice_folders = list(x for x in path.iterdir() if x.is_dir())
        for voice_folder in voice_folders:
            db_path = self._create_db_path(dbs_path=self.dbs_path, voice_name=voice_folder.name)
            new_voice = SingleVoice(path=voice_folder, db_path=db_path)
            voices[new_voice.name] = new_voice
        return voices

    def _create_multi_voice(self, voices: Dict[str, SingleVoice]) -> MultiVoice:
        db_path = self._create_db_path(dbs_path=self.dbs_path, voice_name='multi')
        return MultiVoice(
            voices=voices,
            db_path=db_path,
        )

    def get_voice_names(self) -> List[str]:
        """Gets names of available voices

        Returns:
            list -- list of voice name strings
        """

        voice_names = list(self.voices.keys())
        voice_names.sort()
        return voice_names

    def get_voice(self, name: str) -> Optional[Voice]:
        """Get voice of requested name

        Args:
            name ({string}): name of voice to get

        Returns:
            {voxvoice}: requested voice
        """
        if name in self.voices:
            return self.voices[name]
        else:
            return None

    def exit(self):
        for voice_name in self.voices:
            self.voices[voice_name].exit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description='Generate a sentence using voices')
    parser.add_argument('-s', '--voices-dir', type=str, required=True, help='Path to folder with voice audio file folders')
    parser.add_argument('-d', '--db', type=str, required=True, help='Path to store database files')
    parser.add_argument('-f', '--format', type=str, required=False, default='wav', help='Audio format to export as')
    parser.add_argument('voice', type=str)
    parser.add_argument('sentence', type=str)
    args = parser.parse_args()

    voices_dir = Path(args.voices_dir)
    if not voices_dir.is_dir():
        print(f'Voices dir at {voices_dir} does not exist!')
        sys.exit(1)

    dbs_path = Path(args.db)

    manager = Manager(
        voices_path=voices_dir,
        dbs_path=dbs_path,
    )

    voice = manager.get_voice(args.voice)
    if voice is None:
        print(f'Voice {voice} was not found')
        sys.exit(1)

    sentence = voice.generate_audio(args.sentence)
    if sentence is None or sentence.audio is None:
        log.error(f'Cannot generate {sentence.sentence}: {sentence}')
        sys.exit(1)

    # Paths can't have : in them, so replace with % as a stand-in
    sanitized_sentence = sentence.sentence.replace(':', '%')
    output_path = Path.cwd().joinpath(f"{sanitized_sentence}.{args.format}")

    log.info(f'Exporting to {output_path}')
    sentence.audio.export(output_path, format=args.format)
