from typing import List, Dict, Tuple
from collections import namedtuple
from prettytable import PrettyTable
from re import sub


class Pred_sent:
    def __init__(
        self,
        src_raw: str,
        sentence: str,
        attention_matrix: List,
        score: float
    ):
        self.src_raw = src_raw
        self.sentence = sentence
        self.attention_matrix = attention_matrix
        self.score = score

    def get_pretty_attention(self):
        if self.attention_matrix is not None:
            try:
                prt = PrettyTable()
                field_names = ["src ->"]
                for i, word in enumerate(self.src_raw.split(" ")):
                    field_names.append(f"#{i} {word}")
                prt.field_names = field_names
                print("len tokens src", len(field_names))
                print("Matrix:", len(self.attention_matrix), "x",
                    len(self.attention_matrix[0]), "len tokens tgt:",
                    len(self.sentence.split(" "))
                )
                for word, attn in zip(
                    self.sentence.split(" "), self.attention_matrix
                ):
                    row = [word] + attn
                    prt.add_row(row)
                return prt
            except Exception as e:
                prt = PrettyTable()
                for word, attn in zip(
                    self.sentence.split(" "), self.attention_matrix
                ):
                    row = [word] + attn
                    prt.add_row(row)
                return prt

Translation = namedtuple("Translation", ["pred_sents"])
File = str
