import cld3
from pangeamt_nlp.locale.lang import PANGEAMT_LANG


class LangDetector:
    def __init__(self):
        # Cld3 code to lang
        pass


    def detect(self, text: str):
        detection = cld3.get_language(
            text
        )
        is_reliable = detection.is_reliable

        if not is_reliable:
            return None
        else:
            code = detection.language
            if code == 'un':
                return None
            return code


