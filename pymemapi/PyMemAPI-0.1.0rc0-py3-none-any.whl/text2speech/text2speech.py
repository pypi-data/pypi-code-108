from pathlib import Path
from typing import List
from ..exception import LanguageError
import re
import pyttsx3


VOICE_N = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\{name}"
LANGUAGE = {
    "en-gb": [VOICE_N.format(name="TTS_MS_EN-GB_HAZEL_11.0")],
    "en": [
        VOICE_N.format(name="TTS_MS_EN-US_ZIRA_11.0"),
        VOICE_N.format(name="TTS_MS_EN-US_DAVID_11.0"),
    ],
    "fr": [
        VOICE_N.format(name="TTS_MS_FR-FR_HORTENSE_11.0"),
        VOICE_N.format(name="TTS_V110_FR-FR_PAUL_11.0"),
    ],
    "jp": [
        VOICE_N.format(name="TTS_MS_JA-JP_HARUKA_11.0"),
        VOICE_N.format(name="TTS_MS_JA-JP_ICHIRO_11.0"),
    ],
}
TAG_XML = """<VOICE REQUIRED="NAME={name}">
<rate speed="{speed}" >
<silence msec="100"/>{text}<silence msec="100"/>
</rate>
</VOICE>
"""
CUSTOM = {
    "en": ["VW Julie", "VW Paul"],
    "jp": ["VW Misaki"],
}


def concat(words: str):
    mywords = re.findall("\\w+", words.lower())
    retstr = ""
    for myword in mywords:
        retstr += myword[0].upper() + myword[1:]
    return retstr


def external_generate_audio(language: str, text: str) -> None:
    if language not in CUSTOM.keys():
        raise LanguageError(language=language, message="Not support.")
    else:
        voices: List[str] = CUSTOM[language]

    for voice in voices:
        vname = voice.replace(" ", "")
        filename = concat(text)
        Path(f"./audio/{vname}/").mkdir(parents=True, exist_ok=True)
        with open(f"./audio/{vname}/{filename}.txt", "w") as fp:
            fp.seek(0)
            fp.write(TAG_XML.format(name=voice, speed=-2, text=text))


def info_voice() -> None:
    ENGINE = pyttsx3.init()
    VOICES = ENGINE.getProperty("voices")
    print("All avaiable voices:")
    for idx in range(len(VOICES)):
        print(f"{idx+1}. {VOICES[idx].name}")


def input_voice(message: str):
    choice = input(message)
    return int(choice) - 1


def choose_voices() -> List[str]:
    ENGINE = pyttsx3.init()
    VOICES = ENGINE.getProperty("voices")
    number_str = input("Enter the number of voices you wish: ")
    number = int(number_str)
    voices: List[str] = []
    info_voice()
    for idx in range(number):
        num = input_voice(f"Choose the voice number {idx+1}: ")
        voices.append(VOICES[num].id)
    return voices


def generate_audio(
    text: str, path: str, language: str = "", speed: int = 170
) -> List[str]:
    voices: List[str] = []
    files: List[str] = []
    ENGINE = pyttsx3.init()
    if language != "":
        if language not in LANGUAGE.keys():
            raise LanguageError(language=language, message="Not support.")
        voices = LANGUAGE[language]

    for v in voices:
        ENGINE.setProperty("voice", v)
        file = concat(f"{text}{v}")
        ENGINE.save_to_file(text, f"{path}/{file}.mp3")
        files.append(f"{path}/{file}.mp3")
        ENGINE.runAndWait()

    return files


def generate_audio_except(
    text: str, path: str, voices: List[str], speed: int = 170
) -> List[str]:
    files: List[str] = []
    ENGINE = pyttsx3.init()

    for v in voices:
        ENGINE.setProperty("voice", v)
        file = concat(f"{text}{v}")
        ENGINE.save_to_file(text, f"{path}/{file}.mp3")
        files.append(f"{path}/{file}.mp3")
        ENGINE.runAndWait()

    return files
