import os
import click
from pangeamt_tea.project.workflow.stage.base_stage import BaseStage
# from pangeamt_tea.project.workflow.workflow import WorkflowAlreadyExists
from pangeamt_nlp.tokenizer.tokenizer_factory import TokenizerFactory
from pangeamt_nlp.truecaser.truecaser import Truecaser
from pangeamt_nlp.processor.pipeline_decoding import PipelineDecoding
from pangeamt_nlp.bpe.bpe import BPE
from pangeamt_nlp.bpe.sentencepiece import SentencePieceSegmenter
from sacrebleu.metrics import BLEU, CHRF, TER
from pangeamt_nlp.translation_model.translation_model_factory import (
    TranslationModelFactory,
)
from pangeamt_nlp.seg import Seg
from nteu_corporate_engine.engine import Engine
import logging


class EvalStage(BaseStage):
    NAME = "eval"
    DIR = "04_evaluated"

    def __init__(self, workflow):
        super().__init__(workflow, self.NAME)

    async def run(self, gpu: int = None, step: int = None):
        project = self.workflow.project
        project_dir = project.config.project_dir
        workflow_dir = self.workflow.get_dir(project_dir)
        self.stage_dir = os.path.join(workflow_dir, EvalStage.DIR)

        if not os.path.isdir(self.stage_dir):
            os.mkdir(self.stage_dir)

        model_dir = os.path.join(workflow_dir, "03_trained")
        model_path = None
        if project.config.translation_model["name"] == "onmt":
            sufix = f"{step}.pt" if step else ".pt"
        elif project.config.translation_model["name"] == "marianmt":
            sufix = "model.npz.decoder.yml"

        for file in os.listdir(model_dir):
            if file.endswith(sufix):
                model_path = os.path.join(model_dir, file)
        if model_path is None:
            raise Exception("No model found.")

        self._prepare_dir = os.path.join(workflow_dir, "02_prepared")

        src_path = os.path.join(self._prepare_dir, "01_raw", "test_src.txt")
        tgt_path = os.path.join(self._prepare_dir, "01_raw", "test_tgt.txt")
        out_path = os.path.join(self.stage_dir, "test_output.txt")

        final_score = await self.eval_files(
            gpu, step, src_path, tgt_path, out_path, None, False
        )

        return {
            "Score": final_score
        }

    async def eval_files(
        self,
        gpu: int,
        step: int,
        src_path: str,
        ref_path: str,
        out_name: str,
        log_file: str,
        debug: bool
    ):
        logging.info("Loading model")
        config = self.workflow.project.config.config_dict
        project = self.workflow.project
        project_dir = project.config.project_dir
        src_lang = project.config.src_lang
        tgt_lang = project.config.tgt_lang
        workflow_dir = self.workflow.get_dir(project_dir)
        self.stage_dir = os.path.join(workflow_dir, EvalStage.DIR)
        self._prepare_dir = os.path.join(workflow_dir, "02_prepared")

        if not os.path.isdir(self.stage_dir):
            os.mkdir(self.stage_dir)

        model_dir = os.path.join(workflow_dir, "03_trained")
        model_path = None

        if project.config.translation_model["name"] == "onmt":
            sufix = f"{step}.pt" if step else ".pt"
        elif project.config.translation_model["name"] == "marianmt":
            sufix = "model.npz.decoder.yml"

        for file in os.listdir(model_dir):
            if file.endswith(sufix):
                model_path = os.path.join(model_dir, file)
        if model_path is None:
            raise Exception("No model found.")

        config["translation_engine_server"] = {
                "model_path": model_path,
                "bpe": os.path.join(self._prepare_dir, "bpe_model"),
                "truecaser": os.path.join(self._prepare_dir, "truecase_model"),
                "gpu": True if gpu is not None else False,
                "sentencepiece": config["bpe"].get("sentencepiece")
        }

        if log_file is not None:
            log_path = os.path.join(self.stage_dir, log_file)
        else:
            log_path = None
        logging.info(f"Model path {model_path}")
        engine = Engine(config, log_path, debug)

        if out_name is not None:
            out_path = os.path.join(self.stage_dir, out_name)
        else:
            out_path = os.path.join(self.stage_dir, "test_output.txt")

        with open(src_path, "r") as src_file, open(out_path, "w") as out_file:
            async def _write_to_file(batch):
                for translation in await engine.process_batch(
                    batch
                ):
                    if not translation.endswith("\n"):
                        translation = translation + "\n"
                    out_file.write(translation)
            with open(ref_path, "r") as ref_file:
                batch = []
                with click.progressbar(
                    enumerate(src_file),
                    label="Evaluating: ",
                ) as bar:
                    if project.config.translation_model["name"] == "onmt":
                        for i, src_line in bar:
                            batch.append(src_line)
                            if (i + 1) % 20 == 0:
                                await _write_to_file(batch)
                                batch = []
                        if len(batch) != 0:
                            await _write_to_file(batch)
                    else:
                        for i, src_line in bar:
                            batch.append(src_line)
                        if len(batch) != 0:
                            await _write_to_file(batch)
        engine = None
        if tgt_lang == "ja":
            bleu = BLEU(tokenize='ja-mecab')
            ter = TER(asian_support=True, normalized=True)
        elif tgt_lang == "zh" or tgt_lang=="tw":
            bleu = BLEU(tokenize='zh')
            ter = TER(asian_support=True, normalized=True)
        else:
            bleu = BLEU()
            ter = TER()
        chrf = CHRF()
        with open(out_path, "r") as sys_file, open(ref_path, "r") as ref_file:
            sys_file = list(sys_file)
            ref_file = list(ref_file)
            final_score_bleu = bleu.corpus_score(sys_file, [ref_file]).score
            final_score_chrf = chrf.corpus_score(sys_file, [ref_file]).score
            final_score_ter = ter.corpus_score(sys_file, [ref_file]).score

        logging.info("CHRF: " + str(final_score_chrf))
        logging.info("TER: " + str(final_score_ter))
        logging.info("Score: " + str(final_score_bleu))
        return final_score_bleu
