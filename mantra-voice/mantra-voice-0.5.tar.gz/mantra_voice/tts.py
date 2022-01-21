import pyttsx3
import sox
import sounddevice as sd
import soundfile as sf
from gtts import gTTS, gTTSError
from .exceptions import *

DEFAULT_CONFIG = {
    "engine": "gtts",
    "gtts_params": {
        "lang": "en",
        "tld": "co.za"
    },
    "tfm_effects": {
        "tempo": 1.3,
        "chorus": [0.8, 1, 3],
        "pitch": 0,
        "gain": [2, False],
        "rate": 48000
    },
    "pyttsx3_properties": {
        "rate": 130
    }
}


class TextToSpeech:
    def __init__(self, raw_path: str, processed_path: str, config: dict = None, **kwargs) -> None:
        self.raw_path = raw_path
        self.processed_path = processed_path
        self.config = config

        self.pyttsx3_engine = pyttsx3.init()
        self.tfm = sox.Transformer()
        self.mixer = kwargs.get("mixer")
        self.track = kwargs.get("track")

        self.effect_mappings = {
            "tempo": self.tfm.tempo,
            "chorus": self.tfm.chorus,
            "pitch": self.tfm.pitch,
            "vol": self.tfm.vol,
            "gain": self.tfm.gain,
            "rate": self.tfm.rate
        }

        if not self.config:
            self.config = DEFAULT_CONFIG

        self.validate_config()
        self._init_effects()

    def validate_config(self) -> None:
        if self.config["engine"] not in ["pyttsx3", "gtts"]:
            raise InvalidEngine(self.config["engine"])

    def _init_effects(self) -> None:
        """Initialize the tfm_effects and pyttsx3 properties."""

        tfm_effects = self.config.get("tfm_effects", {})
        pyttsx3_properties = self.config.get("pyttsx3_properties", {})

        for k, v in tfm_effects.items():
            if not isinstance(v, list):
                v = [v]

            func = self.effect_mappings.get(k)
            if func:
                func(*v)
            else:
                raise InvalidEffect(k)

        for k, v in pyttsx3_properties.items():
            self.pyttsx3_engine.setProperty(k, v)

    def update_config(self, config: dict) -> None:
        self.config = config
        self.validate_config()
        self.tfm.clear_effects()
        self._init_effects()

    async def _save_raw(self, text: str, engine: str) -> None:
        if engine == "pyttsx3":
            self.pyttsx3_engine.save_to_file(text, self.raw_path)
            self.pyttsx3_engine.runAndWait()
        elif engine == "gtts":
            try:
                params = self.config.get("gtts_params", {})
                gt = gTTS(text, **params)
                gt.save(self.raw_path)
            except gTTSError:
                await self._save_raw(text, "pyttsx3")

    async def _build_tfm(self) -> None:
        self.tfm.build_file(self.raw_path, self.processed_path)

    async def _play(self, blocking: bool = False) -> None:

        if not self.mixer:
            data, rs = sf.read(self.processed_path, dtype="float32")
            sd.play(data, rs, blocking=blocking)
        else:
            await self.mixer.play_file(self.processed_path, blocking=blocking, track=self.track)

    async def say(self, text: str, blocking: bool = False) -> None:
        await self._save_raw(text, self.config["engine"])
        await self._build_tfm()
        await self._play(blocking)
