import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from hlvox.voice import Voice


class Manager:
    def __init__(self, voices_path: Union[Path, str], dbs_path: Union[Path, str]):
        self.voices_path = Path(voices_path)
        self.dbs_path = Path(dbs_path)
        self.voices = self._load_voices(self.voices_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit()

    def _load_voices(self, path: Path) -> Dict[str, Voice]:
        voices = {}
        voice_folders = list(x for x in path.iterdir() if x.is_dir())
        for voice_folder in voice_folders:
            db_path = self.dbs_path / voice_folder.name
            db_path.mkdir(parents=True, exist_ok=True)
            new_voice = Voice(path=voice_folder, db_path=db_path)
            voices[new_voice.name] = new_voice
        return voices

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
