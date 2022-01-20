from pangeamt_nlp.processor.pipeline_decoding import PipelineDecoding
from pangeamt_nlp.processor.pipeline_training import PipelineTraining
from pangeamt_nlp.truecaser.truecaser import Truecaser
from pangeamt_nlp.bpe.bpe import BPE
from pangeamt_nlp.bpe.sentencepiece import SentencePieceSegmenter
from pangeamt_nlp.tokenizer.tokenizer_factory import TokenizerFactory
from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase
from pangeamt_nlp.seg import Seg
from typing import Dict, Tuple
import os
import logging
from logging import Logger


class Pipeline:

    def __init__(self, config: Dict) -> "Pipeline":
        self._config = config
        self._src_lang = config["src_lang"]
        self._tgt_lang = config["tgt_lang"]
        self._decoding_pipeline = self.load_decoding_pipeline()
        self._training_pipeline = self.load_training_pipeline()
        self._src_bpe, self._tgt_bpe = self.load_bpe()
        self._src_truecaser, self._tgt_truecaser = self.load_truecaser()
        self._src_tokenizer, self._tgt_tokenizer = self.load_tokenizer()

    async def preprocess(self, seg: Seg):
        self._decoding_pipeline.process_src(seg, logger=logging.getLogger())
        seg.src = self._src_tokenizer.tokenize(seg.src)
        logging.debug("Tokenizing: " + seg.src)
        if self._src_truecaser is not None:
            seg.src = self._src_truecaser.truecase(seg.src)
            logging.debug("Truecasing: " + seg.src)
        if self._src_bpe is not None:
            seg.src = self._src_bpe.apply(seg.src)
            logging.debug("BPE: " + seg.src)

    async def postprocess(self, seg: Seg):
        seg.tgt = self._tgt_bpe.undo(seg.tgt)
        logging.debug("Undo BPE" + seg.tgt)
        seg.tgt = self._tgt_tokenizer.detokenize(seg.tgt.split(" "))
        logging.debug("Detokenize: " + seg.tgt)
        if self._tgt_truecaser:
            seg.tgt = self._tgt_truecaser.detruecase(seg.tgt)
            logging.debug("Detruecasing: " + seg.tgt)
        self._decoding_pipeline.process_tgt(seg, logger=logging.getLogger())

    async def process_train(self, seg: Seg):
        self._training_pipeline.normalize(seg)
        seg.src = self._src_tokenizer.tokenize(seg.src)
        seg.tgt = self._tgt_tokenizer.tokenize(seg.tgt)
        logging.debug("Tokenizing: " + seg.src + ", " + seg.tgt)
        if self._src_truecaser is not None:
            seg.src = self._src_truecaser.truecase(seg.src)
            logging.debug("Truecasing: " + seg.src)
        if self._tgt_truecaser is not None:
            seg.tgt = self._tgt_truecaser.truecase(seg.tgt)
            logging.debug("Truecasing: " + seg.tgt)
        if self._src_bpe is not None:
            seg.src = self._src_bpe.apply(seg.src)
            logging.debug("BPE: " + seg.src)
        if self._tgt_bpe is not None:
            seg.tgt = self._tgt_bpe.apply(seg.tgt)
            logging.debug("BPE: " + seg.tgt)

    def load_decoding_pipeline(self) -> PipelineDecoding:
        return PipelineDecoding.create_from_dict(
            self._src_lang, self._tgt_lang, self._config["processors"]
        )

    def load_training_pipeline(self) -> PipelineTraining:
        return PipelineTraining.create_from_dict(
            self._src_lang, self._tgt_lang, self._config["processors"]
        )

    def load_bpe(self) -> Tuple[BPE, BPE]:
        if self._config["bpe"] is not None:
            path = self._config["translation_engine_server"]["bpe"]
            if self._config["bpe"].get("sentencepiece"):
                src_bpe, tgt_bpe = self.load_sentencepiece(path)
            else:
                if self._config["bpe"]["joint"]:
                    src_bpe, tgt_bpe = self.load_joint_bpe(path)
                else:
                    src_bpe, tgt_bpe = self.load_split_bpe(path)
            return src_bpe, tgt_bpe
        else:
            return None, None

    def load_sentencepiece(self, path: str):
        src_model = os.path.join(path, "src_codes.model")
        tgt_model = os.path.join(path, "tgt_codes.model")
        return (
            SentencePieceSegmenter(src_model),
            SentencePieceSegmenter(tgt_model)
        )

    def load_joint_bpe(self, path: str) -> Tuple[BPE, BPE]:
        codes = os.path.join(path, "codes32k.txt")
        src_vocab = os.path.join(path, "src_vocab.txt")
        tgt_vocab = os.path.join(path, "tgt_vocab.txt")
        return BPE(codes, src_vocab), BPE(codes, tgt_vocab)

    def load_split_bpe(self, path: str) -> Tuple[BPE, BPE]:
        src_codes = os.path.join(path, "src_codes.txt")
        tgt_codes = os.path.join(path, "tgt_codes.txt")
        return BPE(src_codes), BPE(tgt_codes)

    def load_truecaser(self) -> Tuple[Truecaser, Truecaser]:
        src_truecaser, tgt_truecaser = None, None
        if self._config["truecaser"]["src"] == "enabled":
            path = os.path.join(
                self._config["translation_engine_server"]["truecaser"],
                "src_model.txt"
            )
            src_truecaser = Truecaser(path)
        if self._config["truecaser"]["tgt"] == "enabled":
            path = os.path.join(
                self._config["translation_engine_server"]["truecaser"],
                "tgt_model.txt"
            )
            tgt_truecaser = Truecaser(path)
        return src_truecaser, tgt_truecaser

    def load_tokenizer(self) -> Tuple[TokenizerBase, TokenizerBase]:
        src_tok_name = self._config["tokenizer"]["src"]
        tgt_tok_name = self._config["tokenizer"]["tgt"]

        src_tokenizer = TokenizerFactory.new(self._src_lang, src_tok_name)
        tgt_tokenizer = TokenizerFactory.new(self._tgt_lang, tgt_tok_name)

        return (src_tokenizer, tgt_tokenizer)
