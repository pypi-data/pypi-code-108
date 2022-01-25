import json
import os.path
import struct
import wave
from pathlib import Path
from typing import List


def create_voice_files(base_path: Path, files: List[str], voice_name='voice', touch_only=False) -> Path:
    audio_path = base_path.joinpath(voice_name)
    audio_path.mkdir()

    for f in files:
        filepath = audio_path.joinpath(f)
        if touch_only:
            filepath.touch()
            continue
        savefile = wave.open(str(filepath), "w")

        # channels, datasize (16 bit), sample rate, number of samples
        savefile.setparams((1, 2, 11025, 500, "NONE", "Uncompressed"))
        savefile.writeframes(struct.pack('h', 1))
        savefile.close()

    return audio_path


def create_info(info: dict, audio_path: Path):
    info_dir = Path(audio_path).joinpath("info/")

    info_dir.mkdir(parents=True, exist_ok=True)

    info_file = info_dir.joinpath("info.json")

    with open(info_file, 'w') as f:
        json.dump(info, f)
