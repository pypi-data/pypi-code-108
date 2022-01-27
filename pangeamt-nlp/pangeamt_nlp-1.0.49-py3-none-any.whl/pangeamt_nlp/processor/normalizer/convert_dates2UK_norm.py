from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from sacremoses import MosesTokenizer


class ConvertDates2UKNorm(NormalizerBase):
    NAME = "convert_dates2UK_norm"

    DESCRIPTION_TRAINING = """Convert Dates from US 2 UK format.
                             e.g: December 24 -> the 24th of December
                                                                   """

    DESCRIPTION_DECODING = """"""

    MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "November",
        "December"
    ]

    TOKENIZER = MosesTokenizer()

    def __init__(self, src_lang: str, tgt_lang: str):
        super().__init__(src_lang, tgt_lang)

    def _convert_dates2UK(self, text: str):
        text_tok = self.TOKENIZER.tokenize(text)
        if len(text_tok) <= 1:
            return text
        for month in self.MONTHS:
            # check if the are months in the text
            if month in text_tok:
                i = (text_tok.index(month))
                date = False
                # check if it is beginning of sentence to write "the" in capitals
                the = "the"
                # check if the next word is a month day, this is to make it work also with "December 24, it is a month."
                if len(text_tok) > i + 1:
                    day = text_tok[i + 1]
                    if day.isnumeric():
                        try:
                            if int(day) in range(1, 31):
                                date = True
                                # if month is at the beginning of sentence
                                if i == 0:
                                    the = "The"
                        except ValueError:
                            pass
                # check if the previous word is a month day, this is to make it work also with "24 December, it is a month."
                if date is False and i > 0:
                    day = text_tok[i - 1]
                    if day.isnumeric():
                        try:
                            if int(day) in range(1, 31):
                                date = True
                                # if day is at the beginning of sentence
                                if day == text_tok[0]:
                                    the = "The"
                        except ValueError:
                            pass
                if date:
                    # check which number is to write the correct ordinal
                    ordinal = "th"
                    if day in ["1", "21", "31"]:
                        ordinal = "st"
                    if day in ["2", "22"]:
                        ordinal = "nd"
                    if day in ["3", "23"]:
                        ordinal = "rd"
                    text = text.replace(
                        f"{month} {day}",
                        f"{the} {day}{ordinal} of {month}"
                    ).replace(
                        f"{day} {month}",
                        f"{the} {day}{ordinal} of {month}"
                    )
        return text

    # Called when training
    def process_train(self, seg: Seg) -> None:
        pass

    # Called when using model (before calling model to translate)
    def process_src_decoding(self, seg: Seg) -> None:
        pass

    # Called after the model translated (in case this would be necessary; usually not the case)
    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "en":
            seg.tgt = self._convert_dates2UK(seg.tgt)
