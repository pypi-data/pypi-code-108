from pycld2 import detect, LANGUAGES, DETECTED_LANGUAGES
from pangeamt_nlp.locale.lang import PANGEAMT_LANG


class LangDetector:
    def __init__(self):
        # Cld2 code to lang
        self._cld2_code_to_lang = {}
        for name, code in LANGUAGES:
            if code not in self._cld2_code_to_lang:  # Repeated item in LANGUAGES!!!
                self._cld2_code_to_lang[code] = name

        # Cld2 lang to code
        self._cld2_lang_to_code = {v: k for k, v in self._cld2_code_to_lang.items()}

        # Detected language code
        self._detected_lang_codes = [self._cld2_lang_to_code[lang] for lang in DETECTED_LANGUAGES]

        # Pangeamt lang
        self._pangeamt_detected_lang_codes = [code for code in self._detected_lang_codes if code in PANGEAMT_LANG]

    def get_detected_lang_code(self):
        return self._detected_lang_codes

    def get_pangeamt_detected_lang_code(self):
        return self._pangeamt_detected_lang_codes

    def detect(self, text: str, best_effort:bool=False, use_pangeamt_lang:bool=True, hint_language=None):
        is_reliable, _, details = detect(
            text,
            bestEffort=best_effort,
            hintLanguage=hint_language,
        )

        if not is_reliable:
            return None
        else:

            code = details[0][1]
            if code == 'un':
                return None
            return code


