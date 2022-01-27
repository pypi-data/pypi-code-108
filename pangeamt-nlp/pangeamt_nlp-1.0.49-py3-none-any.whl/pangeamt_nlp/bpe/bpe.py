from subword_nmt.apply_bpe import BPE as _BPE
from subword_nmt.apply_bpe import read_vocabulary as _rv
from subword_nmt.learn_bpe import learn_bpe
import codecs
from subword_nmt.learn_joint_bpe_and_vocab import (
    learn_joint_bpe_and_vocab,
    create_parser,
)
from re import sub as _sub
import codecs as _codecs


class BPE:
    def __init__(
        self,
        bpe_codes,
        bpe_vocab=None,
        bpe_threshold=None,
        bpe_glossaries=None,
    ):
        if bpe_glossaries is None:
            _glossaries = []
        else:
            _glossaries = [self._parse_glossary(i) for i in bpe_glossaries]

        if bpe_vocab:
            _vocab = _rv(
                _codecs.open(bpe_vocab, encoding="utf-8"), bpe_threshold
            )
            self._bpe = _BPE(
                _codecs.open(bpe_codes, encoding="utf-8"),
                vocab=_vocab,
                glossaries=_glossaries,
            )
        else:
            self._bpe = _BPE(
                _codecs.open(bpe_codes, encoding="utf-8"),
                glossaries=_glossaries,
            )

    def _parse_glossary(self, str: str) -> str:
        return str.encode("utf-8").decode("utf-8")

    def apply(self, text: str) -> str:
        return self._bpe.process_line(text)

    @staticmethod
    def undo(text: str) -> str:
        return _sub("(@@ )|(@@ ?$)", "", text)

    @staticmethod
    def learn_joint(
        src_input: str,
        tgt_input: str,
        codes_out: str,
        src_vocab: str,
        tgt_vocab: str,
        num_iterations: int = 32000,
    ) -> None:
        parser = create_parser()
        args = parser.parse_args(
            [
                "-i",
                src_input,
                tgt_input,
                "-o",
                codes_out,
                "-s",
                str(num_iterations),
                "--write-vocabulary",
                src_vocab,
                tgt_vocab,
            ]
        )

        learn_joint_bpe_and_vocab(args)

    # train_joint = property(_train_joint)

    @staticmethod
    def learn(
        input, output, symbols,
    ):
        learn_bpe(
            codecs.open(input, encoding="utf-8"),
            codecs.open(output, "w", encoding="utf-8"),
            symbols,
        )

    # train = property(_train)
