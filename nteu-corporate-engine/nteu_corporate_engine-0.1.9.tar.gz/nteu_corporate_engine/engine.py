from pangeamt_nlp.translation_model.translation_model_factory import (
    TranslationModelFactory,
)
import logging
from pangeamt_nlp.seg import Seg
from nteu_corporate_engine.pipeline import Pipeline
from typing import Dict, List
from asyncio import Lock


class Engine:
    def __init__(self, config: Dict, log_file: str = None, dbug: bool = False):
        self.setup_log(log_file, dbug)
        self._config = config
        self._pipeline = Pipeline(self._config)
        self._model = self.load_model()
        online_learning_args = config["translation_engine_server"].get(
            "online_learning", None
        )
        if online_learning_args is not None:
            self._model.setup_online_trainer(online_learning_args)

    def load_model(self):
        name = self._config["translation_model"]["name"]
        args = self._config["translation_model"]["args_decoding"]
        if self._config["translation_engine_server"]["gpu"]:
            args["gpu"] = 0
        model_path = self._config["translation_engine_server"]["model_path"]
        if args == {}:
            msg = f"Loading Model -> {name} with default args"
        else:
            msg = f"Loading Model -> {name} with arguments {args}."
        logging.info(msg)
        translation_model = TranslationModelFactory.get_class(name)
        return translation_model(model_path, **args)

    async def translate(self, srcs: List, n_best: int = 1):
        if self._config["translation_model"]["name"] == "onmt":
            translations = self._model.translate(srcs, n_best=n_best)
            result = []
            for translation in translations:
                self.log_translation(translation)
                result.append(translation.pred_sents[0].sentence)
        elif self._config["translation_model"]["name"] == "marianmt":
            args_dec = self._config["translation_model"]["args_decoding"]
            if not args_dec["in_training_servers"]:
                result = self._model.translate(srcs, n_best=n_best)
            else:
                model_path = self._config["translation_engine_server"]["model_path"]
                marian_path = self._config["translation_model"]["marian_path"]
                if self._config["translation_engine_server"]["gpu"]:
                    gpu = "0"
                else:
                    gpu = None
                result = self._model.translate_training_servers(srcs,\
                                        model_path, marian_path, gpu)
            for translation in result:
                self.log_translation(translation)
        return result

    async def process_batch(self, batch: List, lock: Lock = None):
        srcs = []
        segs = []
        ans = []
        for src in batch:
            seg = Seg(src)
            await self._pipeline.preprocess(seg)
            srcs.append(seg.src)
            segs.append(seg)
        if lock is not None:
            async with lock:
                translations = await self.translate(srcs)
        else:
            translations = await self.translate(srcs)
        for translation, seg in zip(translations, segs):
            seg.tgt = seg.tgt_raw = translation
            await self._pipeline.postprocess(seg)
            ans.append(seg.tgt)
            logging.info(
                f"Translated -> {seg.src_raw} -> {seg.src} "
                f"-> {seg.tgt_raw} -> {seg.tgt}"
            )
        return ans

    async def online_train(
        self, batch: List, num_steps: int = 1, lock: Lock = None
    ):
        tus = []
        for src, tgt in [tu for tu in batch]:
            seg = Seg(src, tgt)
            await self._pipeline.process_train(seg)
            tus.append((seg.src, seg.tgt))
        if lock is not None:
            async with lock:
                self._model.online_train(tus, num_steps)
        else:
            self._model.online_train(tus, num_steps)

    @classmethod
    def setup_log(cls, log_file: str=None, dbug: bool=None):
        hdlrs = [logging.StreamHandler()]
        if log_file is not None:
            hdlrs.append(logging.FileHandler(log_file))
        cls.lvl = logging.DEBUG if dbug else logging.INFO
        logging.basicConfig(
            handlers=hdlrs,
            level=cls.lvl,
            format="%(asctime)s :: %(levelname)s :: %(message)s"
        )

    def log_translation(self, translation: "Translation"):
        if self.lvl == logging.DEBUG:
            n_best = len(translation)
            log_msg = (
                f"For sentence {translation.pred_sents[0].src_raw}",
                f"{n_best}-best translations:"
            )
            logging.debug(log_msg)
            f = "\nOption #{0} with score {1}:\n{2}\nAttention:\n"
            for i, prediction in enumerate(translation.pred_sents):
                log_msg = f.format(
                    i,
                    prediction.score,
                    prediction.sentence
                )
                table = prediction.get_pretty_attention()
                if table is not None:
                    table_fields = table._field_names
                    table_width = len(table_fields)
                    for column_index in range(0, table_width, 3):
                        f_index = column_index
                        l_index = min([column_index + 3, table_width])
                        fields_to_take = table_fields[f_index:l_index]
                        str_to_add = table.get_string(
                            fields=fields_to_take
                        ) + "\n"
                        log_msg += str_to_add
                logging.debug(log_msg)
