from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg

import re as _re


class EnglishTimeNorm(NormalizerBase):
    NAME = "english_time_norm"

    DESCRIPTION_TRAINING = """
        
    """

    DESCRIPTION_DECODING = """
        
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if tgt_lang != "en":
            raise ValueError("English time normalizer"
                             "requires English in tgt")

        super().__init__(src_lang, tgt_lang)

        self._regex = _re.compile(
            r"((at|from|to)\s?[0-2]?[0-9][-.:][0-5][0-9]\s?(hours|h)?|"
            r"(at|from|to)?\s?[0-2]?[0-9][.:][0-5][0-9]\s?(hours|h))"
        )

    def normalize(self, txt: str) -> str:
        point_at_the_end = False
        noon = "12"
        midnight_first_option = "0"
        midnight_second_option = "24"
        o_clock = "00"
        if len(txt) > 0:
            if txt[-1] == ".":
                txt_clean = txt[:-1]
                point_at_the_end = True
            else:
                txt_clean = txt
            hours_iter = self._regex.finditer(txt_clean, _re.IGNORECASE)
            for hours in hours_iter:
                hour_content = hours.group()
                prehour = hours.group(2)
                if prehour:
                    posthour = hours.group(3)
                else:
                    posthour = hours.group(2)

                hour_content_normalized = _re.sub(r"[-.:]", ":",
                                              hour_content)
                if prehour:
                    prehour = prehour.replace(" ", "")
                    prehour += " "
                else:
                    prehour = ""

                if posthour:
                    hour_content_normalized = hour_content_normalized.replace(
                        posthour, "")

                exact_hour = _re.findall(r"\d{1,2}",
                                     hour_content_normalized.split(":")[0])[0]
                exact_minutes = _re.findall(r"\d{1,2}",
                                        hour_content_normalized.split(":")[1])[0]

                if exact_hour == noon and exact_minutes == o_clock:
                    txt_clean = txt_clean.replace(hour_content, prehour + "noon")
                elif (exact_hour == midnight_first_option or exact_hour == midnight_second_option) \
                  and exact_minutes == o_clock:
                    txt_clean = txt_clean.replace(hour_content, prehour + "midnight")
                elif int(exact_hour) > int(noon) or \
                    (exact_hour == noon and exact_minutes != o_clock):
                    if exact_minutes == o_clock:
                        txt_clean = txt_clean.replace(hour_content,
                                                  " " + prehour + str(int(exact_hour) - int(noon)) + " p.m. ")
                    else:
                        txt_clean = txt_clean.replace(hour_content,
                                                  " " + prehour + str(int(exact_hour) - int(noon)) + ":"
                                                  + exact_minutes + " p.m. ")
                elif int(exact_hour) < int(noon) or \
                    (exact_hour == midnight_first_option or exact_hour == midnight_second_option
                     and exact_minutes != o_clock):
                    if exact_minutes == o_clock:
                        txt_clean = txt_clean.replace(hour_content, " " + prehour + exact_hour + " a.m. ")
                    else:
                        txt_clean = txt_clean.replace(hour_content,
                                                  " " + hour_content_normalized + " a.m. ")
            if len(txt_clean) > 0 and txt_clean[-1] == " ":
                txt_clean = txt_clean[:-1]
            if point_at_the_end and len(txt_clean) > 0 and txt_clean[-1] != ".":
                txt_clean += "."
            return txt_clean.replace("  ", " ")

    def process_train(self, seg: Seg) -> None:
        if self.tgt_lang == 'en':
            seg.tgt = self.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "en":
            seg.tgt = self.normalize(seg.tgt)

