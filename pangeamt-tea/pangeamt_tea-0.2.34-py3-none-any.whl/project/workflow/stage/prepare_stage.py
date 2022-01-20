import tempfile
import logging
import time
import shutil
import subprocess
import os
import click
import pathlib
from pathos.multiprocessing import Pool
from contextlib import closing
from pangeamt_nlp.tokenizer.tokenizer_factory import TokenizerFactory
from pangeamt_tea.project.workflow.stage.base_stage import BaseStage
from pangeamt_tea.project.workflow.stage.stage_factory import StageFactory
from pangeamt_nlp.truecaser.truecaser import Truecaser
from pangeamt_nlp.bpe.bpe import BPE
from pangeamt_nlp.bpe.sentencepiece import SentencePieceSegmenter
from pangeamt_nlp.data_batcher.batcher import batch


class PrepareStage(BaseStage):
    NAME = "prepare"
    NUM_LINES = 0
    CHUNKSIZE = 500
    DIR = "02_prepared"

    def __init__(self, workflow):
        super().__init__(workflow, self.NAME)

    async def run(self, max_workers: int, seed: int):
        start = time.ctime(int(time.time()))
        project = self.workflow.project
        project_dir = project.config.project_dir

        # Make preparation Directory
        workflow_dir = self.workflow.get_dir(project_dir)
        self.stage_dir = os.path.join(workflow_dir, PrepareStage.DIR)

        if not os.path.isdir(self.stage_dir):
            os.mkdir(self.stage_dir)

        if max_workers is None:
            max_workers = 1

        workflow_config = self.workflow.config

        report = workflow_config.prepare.get("report", {})
        if report is None:
            report = {}
        to_the_end = False

        if (
            workflow_config.prepare["report"] is None
            or "shuffle" not in workflow_config.prepare["report"]
        ):
            to_the_end = True
            start_shuf = time.ctime(int(time.time()))
            await self.shuffle(seed)
            report["shuffle"] = {
                "start": start_shuf,
                "seed": seed,
                "end": time.ctime(int(time.time()))
            }
            workflow_config.set_stage(
                self.name,
                {
                    BaseStage.START: start,
                    BaseStage.END: None,
                    BaseStage.REPORT: report
                }
            )
            workflow_config.save()

        if to_the_end or "tokenize" not in workflow_config.prepare["report"]:
            to_the_end = True
            start_tokenize = time.ctime(int(time.time()))
            await self.tokenize(max_workers)
            report["tokenize"] = {
                "start": start_tokenize,
                "end": time.ctime(int(time.time()))
            }
            workflow_config.set_stage(
                self.name,
                {
                    BaseStage.START: start,
                    BaseStage.END: None,
                    BaseStage.REPORT: report
                }
            )
            workflow_config.save()

        if to_the_end or "truecase" not in workflow_config.prepare["report"]:
            to_the_end = True
            start_truecase = time.ctime(int(time.time()))
            await self.truecase(max_workers)
            report["truecase"] = {
                "start": start_truecase,
                "end": time.ctime(int(time.time()))
            }
            workflow_config.set_stage(
                self.name,
                {
                    BaseStage.START: start,
                    BaseStage.END: None,
                    BaseStage.REPORT: report
                }
            )
            workflow_config.save()

        if to_the_end or "bpe" not in workflow_config.prepare["report"]:
            to_the_end = True
            start_bpe = time.ctime(int(time.time()))
            await self.bpe(max_workers)
            report["bpe"] = {
                "start": start_bpe,
                "end": time.ctime(int(time.time()))
            }
            workflow_config.set_stage(
                self.name,
                {
                    BaseStage.START: start,
                    BaseStage.END: None,
                    BaseStage.REPORT: report
                }
            )
            workflow_config.save()
        
        if project.config.translation_model["name"] == "onmt":
            if (
                to_the_end
                or "prepare_batch" not in workflow_config.prepare["report"]
            ):
                to_the_end = True
                start_prep_batch = time.ctime(int(time.time()))
                await self.prep_batch()
                report["prep_batch"] = {
                    "start": start_prep_batch,
                    "end": time.ctime(int(time.time()))
                }
        else: #marianMT
            report["prep_batch"] = {
                    "start": time.ctime(int(time.time())),
                    "end": time.ctime(int(time.time()))
                }
        return report

    # Read the clean data and join both langs in a file to shuffle it without
    # losing the alignment
    async def shuffle(self, seed: int):
        project = self.workflow.project
        project_dir = project.config.project_dir

        workflow_dir = self.workflow.get_dir(project_dir)
        clean_stage = StageFactory.new("clean", self.workflow)
        cleaned_dir = os.path.join(workflow_dir, clean_stage.DIR)

        dir = os.path.join(self.stage_dir, "01_raw")
        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        all_lines_path = os.path.join(dir, "all_lines.txt")
        all_lines_shuf = os.path.join(dir, "all_lines_shuf.txt")
        temp_path = tempfile.mkstemp()[1]
        all_lines = open(all_lines_path, "w+")
        special_order_src_langs = ["th"]

        # Reads the cleaned files and joins them in a file
        with open(os.path.join(cleaned_dir, "data_src.txt"), "r") as src_file:
            with open(
                os.path.join(cleaned_dir, "data_tgt.txt"), "r"
            ) as tgt_file:
                for src_line, tgt_line in zip(src_file, tgt_file):
                    if project.config.src_lang in special_order_src_langs:
                        line_to_write = (
                            f"{tgt_line.strip()}"
                            "###SEPARATOR###"
                            f"{src_line.strip()}\n"
                        )
                    else:
                        line_to_write = (
                            f"{src_line.strip()}"
                            "###SEPARATOR###"
                            f"{tgt_line.strip()}\n"
                        )
                    all_lines.write(line_to_write)

        all_lines.close()

        # Shuffle the data
        logging.info("Shufling and splitting data...")
        command1 = (
            f'cat {all_lines_path} | sed -e "s/\r//g" | sed "s/\t//g" '
            f"| sort | uniq > {temp_path}"
        )
        if seed is None:
            seed = 3
        command2 = (
            f"seeded_shuffle.sh {temp_path} {str(seed)} > {all_lines_shuf}"
        )

        subprocess.run(command1, shell=True)
        subprocess.run(command2, shell=True)

        os.remove(temp_path)

        train_src = open(
            os.path.join(dir, "train_src.txt"), "w+", encoding="utf-8"
        )
        train_tgt = open(
            os.path.join(dir, "train_tgt.txt"), "w+", encoding="utf-8"
        )
        test_src = open(
            os.path.join(dir, "test_src.txt"), "w+", encoding="utf-8"
        )
        test_tgt = open(
            os.path.join(dir, "test_tgt.txt"), "w+", encoding="utf-8"
        )
        dev_src = open(
            os.path.join(dir, "dev_src.txt"), "w+", encoding="utf-8"
        )
        dev_tgt = open(
            os.path.join(dir, "dev_tgt.txt"), "w+", encoding="utf-8"
        )

        # Open the shuffled file
        with open(all_lines_shuf, "r") as all_lines:
            for i, line in enumerate(all_lines):
                line = line.split("###SEPARATOR###")
                if project.config.src_lang in special_order_src_langs:
                    tgt = line[0].strip() + "\n"
                    src = line[1].strip() + "\n"
                else:
                    src = line[0].strip() + "\n"
                    tgt = line[1].strip() + "\n"

                # Take first 2000 lines for dev
                if i < 2000:
                    # Only src need to be appended a new line
                    dev_src.write(src)
                    dev_tgt.write(tgt)
                # Take second 2000 lines for test
                elif i < 4000:
                    test_src.write(src)
                    test_tgt.write(tgt)
                # Take the rest of the lines for train
                else:
                    train_src.write(src)
                    train_tgt.write(tgt)

        self.NUM_LINES = i

        # Close all the file handlers
        train_src.close()
        train_tgt.close()
        test_src.close()
        test_tgt.close()
        dev_src.close()
        dev_tgt.close()

        # Remove the files used to shuffle the data
        subprocess.run(
            f"rm {all_lines_path} && rm {all_lines_shuf}", shell=True
        )
        logging.info("Finished shufling and splitting data")

    # Tokenize corpus
    async def tokenize(self, max_workers):
        dir = os.path.join(self.stage_dir, "02_tokenized")
        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        # Directory of the previous stage
        prev_dir = os.path.join(self.stage_dir, "01_raw")

        project = self.workflow.project

        # Take the name of the tokenizer to use from the config file
        src_tok_name = project.config.tokenizer["src"]
        tgt_tok_name = project.config.tokenizer["tgt"]

        # Initialize the tokenizer for each language and pair it with the files
        # with a tuple

        if src_tok_name != "none":
            src_tokenizer = TokenizerFactory.new(
                project.config.src_lang, src_tok_name
            )
        else:
            src_tokenizer = None

        if tgt_tok_name != "none":
            tgt_tokenizer = TokenizerFactory.new(
                project.config.tgt_lang, tgt_tok_name
            )
        else:
            tgt_tokenizer = None

        files = (
            (
                [
                    ("train_src.txt", self.NUM_LINES),
                    ("test_src.txt", 2000),
                    ("dev_src.txt", 2000),
                ],
                src_tokenizer
            ),
            (
                [
                    ("train_tgt.txt", self.NUM_LINES),
                    ("test_tgt.txt", 2000),
                    ("dev_tgt.txt", 2000),
                ],
                tgt_tokenizer
            ),
        )

        # Tokenize each line
        for pair in files:
            tokenizer = pair[1]
            for file, size in pair[0]:
                in_path = os.path.join(prev_dir, file)
                out_path = os.path.join(dir, file)
                with open(in_path, "r", encoding="utf-8") as in_file:
                    with open(out_path, "w+") as out_file:
                        if tokenizer is not None:
                            with closing(Pool(max_workers)) as pool:
                                with click.progressbar(
                                    pool.imap(
                                        lambda x: tokenizer.tokenize(x),
                                        in_file,
                                        chunksize=self.CHUNKSIZE,
                                    ),
                                    length=size,
                                    label=f"Tokenizing: {file}",
                                ) as bar:
                                    for tokenized_line in bar:
                                        out_file.write(tokenized_line + "\n")
                        else:
                            for line in in_file:
                                out_file.write(line.strip() + "\n")

    # Apply the truecase to the data
    async def truecase(self, max_workers):
        dir = os.path.join(self.stage_dir, "03_truecased")
        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        prev_dir = os.path.join(self.stage_dir, "02_tokenized")

        logging.info("Training truecase models if enabled...")

        (src_model_path, tgt_model_path) = self.create_truecase_model(
            prev_dir,
            max_workers
        )

        logging.info("Finished training")

        # Initialize the truecaser for the different languages if the truecaser
        # is enabled, if not, let it None
        files = (
            (
                [
                    ("train_src.txt", self.NUM_LINES),
                    ("test_src.txt", 2000),
                    ("dev_src.txt", 2000),
                ],
                Truecaser(src_model_path)
                if (self.workflow.project.config.truecaser["src"] == "enabled")
                else None,
            ),
            (
                [
                    ("train_tgt.txt", self.NUM_LINES),
                    ("test_tgt.txt", 2000),
                    ("dev_tgt.txt", 2000),
                ],
                Truecaser(tgt_model_path)
                if (self.workflow.project.config.truecaser["tgt"] == "enabled")
                else None,
            ),
        )

        for pair in files:
            truecaser = pair[1]
            for file, size in pair[0]:
                in_path = os.path.join(prev_dir, file)
                out_path = os.path.join(dir, file)
                if truecaser is not None:
                    with open(in_path, "r", encoding="utf-8") as in_file:
                        with open(
                            out_path, "w+", encoding="utf-8"
                        ) as out_file:
                            with click.progressbar(
                                in_file,
                                length=size,
                                label=f"Truecasing: {file}",
                            ) as bar:
                                for line in bar:
                                    out_file.write(
                                        truecaser.truecase(line) + "\n"
                                    )
                else:
                    os.symlink(in_path, out_path)

    # Create truecase model
    def create_truecase_model(self, prev_dir: str, max_workers: int):
        config = self.workflow.project.config
        dir = os.path.join(self.stage_dir, "truecase_model")
        src_model_path = os.path.join(dir, "src_model.txt")
        tgt_model_path = os.path.join(dir, "tgt_model.txt")

        if config.truecaser["pretrained"] is not None:
            try:
                from pangeamt_tea.project.project import Project
                path = config.truecaser["pretrained"]
                # Checks if the folder is a project or the model folder
                project = Project.load(pathlib.Path(path))
                model_path = os.path.join(
                    path, "workflow", "02_prepared", "truecase_model"
                )
                os.symlink(model_path, dir)
            except Exception:
                os.symlink(config.truecaser["pretrained"], dir)
        else:
            try:
                os.mkdir(dir)
            except FileExistsError:
                shutil.rmtree(dir)
                os.mkdir(dir)

            def make_path(file: str):
                return os.path.join(prev_dir, file)

            if self.workflow.project.config.truecaser["src"] == "enabled":
                Truecaser().train_from_file(
                    make_path("train_src.txt"),
                    save_to=src_model_path,
                    processes=max_workers
                )

            if self.workflow.project.config.truecaser["tgt"] == "enabled":
                Truecaser().train_from_file(
                    make_path("train_tgt.txt"),
                    save_to=tgt_model_path,
                    processes=max_workers
                )

        return (src_model_path, tgt_model_path)

    # Apply bpe to data
    async def bpe(self, max_workers):
        dir = os.path.join(self.stage_dir, "04_bpe")
        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        # Directory of the previous stage
        prev_dir = os.path.join(self.stage_dir, "03_truecased")

        if self.workflow.project.config.bpe.get("sentencepiece"):
            src_segmenter, tgt_segmenter = self.sentencepiece_segmenter(
                prev_dir
            )
        else:
            src_segmenter, tgt_segmenter = self.bpe_segmenter(prev_dir)

        # Pair src and tgt files with the corresponding BPE objects
        files = (
            (
                [
                    ("train_src.txt", self.NUM_LINES),
                    ("test_src.txt", 2000),
                    ("dev_src.txt", 2000),
                ],
                src_segmenter,
            ),
            (
                [
                    ("train_tgt.txt", self.NUM_LINES),
                    ("test_tgt.txt", 2000),
                    ("dev_tgt.txt", 2000),
                ],
                tgt_segmenter,
            ),
        )
        logging.info("Starting to apply bpe")
        for pair in files:
            bpe = pair[1]
            if bpe:
                for file, size in pair[0]:
                    in_path = os.path.join(prev_dir, file)
                    out_path = os.path.join(dir, file)
                    with open(in_path, "r", encoding="utf-8") as in_file:
                        with open(
                            out_path, "w+", encoding="utf-8"
                        ) as out_file:
                            with closing(Pool(max_workers)) as pool:
                                with click.progressbar(
                                    pool.imap(
                                        lambda x: bpe.apply(x),
                                        in_file,
                                        chunksize=self.CHUNKSIZE,
                                    ),
                                    length=size,
                                    label=f"Applying bpe: {file}",
                                ) as bar:
                                    for bpe_line in bar:
                                        out_file.write(bpe_line.strip() + "\n")
        logging.info("Finished applying bpe")

    def bpe_segmenter(self, prev_dir):
        # BPE joint and threshold parameter from config
        joint = self.workflow.project.config.bpe["joint"]
        threshold = self.workflow.project.config.bpe["threshold"]

        logging.info("Training bpe models if enabled...")

        model_dir = self.create_bpe_model(prev_dir, joint)

        logging.info("Finished training bpe model")

        # If joint, train the bpe with all the corpus, else, train with the
        # corpus split by language
        if joint:
            src_bpe = BPE(
                os.path.join(model_dir, "codes32k.txt"),
                os.path.join(model_dir, "src_vocab.txt"),
                threshold,
            )
            tgt_bpe = BPE(
                os.path.join(model_dir, "codes32k.txt"),
                os.path.join(model_dir, "tgt_vocab.txt"),
                threshold,
            )
        else:
            src_bpe = BPE(
                os.path.join(model_dir, "src_codes.txt"),
                bpe_threshold=threshold,
            )
            tgt_bpe = BPE(
                os.path.join(model_dir, "tgt_codes.txt"),
                bpe_threshold=threshold,
            )
        return src_bpe, tgt_bpe

    # Create BPE model
    def create_bpe_model(self, prev_dir, joint):
        config = self.workflow.project.config
        dir = os.path.join(self.stage_dir, "bpe_model")
        src_input_path = os.path.join(prev_dir, "train_src.txt")
        tgt_input_path = os.path.join(prev_dir, "train_tgt.txt")

        if config.bpe["pretrained"]:
            try:
                from pangeamt_tea.project.project import Project
                path = config.bpe["pretrained"]
                # Checks if the folder is a project or the model folder
                project = Project.load(pathlib.Path(path))
                model_path = os.path.join(
                    path, "workflow", "02_prepared", "bpe_model"
                )
                os.symlink(model_path, dir)
            except Exception:
                os.symlink(config.bpe["pretrained"], dir)
        else:
            try:
                os.mkdir(dir)
            except FileExistsError:
                shutil.rmtree(dir)
                os.mkdir(dir)

            iterations = self.workflow.project.config.bpe["num_iterations"]

            if joint:
                codes_path = os.path.join(dir, "codes32k.txt")
                src_vocab_path = os.path.join(dir, "src_vocab.txt")
                tgt_vocab_path = os.path.join(dir, "tgt_vocab.txt")
                BPE.learn_joint(
                    src_input_path,
                    tgt_input_path,
                    codes_path,
                    src_vocab_path,
                    tgt_vocab_path,
                    iterations,
                )
            else:
                src_model_path = os.path.join(dir, "src_codes.txt")
                tgt_model_path = os.path.join(dir, "tgt_codes.txt")
                BPE.learn(src_input_path, src_model_path, iterations)
                BPE.learn(tgt_input_path, tgt_model_path, iterations)
        return dir

    def sentencepiece_segmenter(self, prev_dir):
        vocab_size = (
            8000
            if self.workflow.project.config.bpe["vocab_size"] is None
            else self.workflow.project.config.bpe["vocab_size"]
        )
        model_type = (
            "unigram"
            if self.workflow.project.config.bpe["model_type"] is None
            else self.workflow.project.config.bpe["model_type"]
        )
        logging.info("Training sentencepiece models if enabled...")
        model_dir = self.create_sentencepiece_model(
            prev_dir, vocab_size, model_type
        )
        logging.info("Finished training sentencepiece model")
        # If joint, train the bpe with all the corpus, else, train with the
        # corpus split by language
        src_sentencepiece = SentencePieceSegmenter(
            os.path.join(model_dir, "src_codes.model")
        )
        tgt_sentencepiece = SentencePieceSegmenter(
            os.path.join(model_dir, "tgt_codes.model")
        )
        return src_sentencepiece, tgt_sentencepiece

    # Create Sentencepiece model
    def create_sentencepiece_model(self, prev_dir, vocab_size, model_type):
        config = self.workflow.project.config
        dir = os.path.join(self.stage_dir, "bpe_model")
        src_input_path = os.path.join(prev_dir, "train_src.txt")
        tgt_input_path = os.path.join(prev_dir, "train_tgt.txt")

        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        src_model_path = os.path.join(dir, "src_codes")
        tgt_model_path = os.path.join(dir, "tgt_codes")
        SentencePieceSegmenter.learn(
            src_input_path, src_model_path, model_type, vocab_size
        )
        SentencePieceSegmenter.learn(
            tgt_input_path, tgt_model_path, model_type, vocab_size
        )
        return dir

    # Split the corpus in shards
    async def prep_batch(self):
        dir = os.path.join(self.stage_dir, "05_batched")
        try:
            os.mkdir(dir)
        except FileExistsError:
            shutil.rmtree(dir)
            os.mkdir(dir)

        prev_dir = os.path.join(self.stage_dir, "04_bpe")

        config = self.workflow.project.config
        shard_size = config.prepare.get("shard_size", "100000")
        src_seq_length = config.prepare.get("src_seq_length", "100")
        tgt_seq_length = config.prepare.get("tgt_seq_length", "100")

        args = [
            "-train_src",
            os.path.join(prev_dir, "train_src.txt"),
            "-train_tgt",
            os.path.join(prev_dir, "train_tgt.txt"),
            "-valid_src",
            os.path.join(prev_dir, "dev_src.txt"),
            "-valid_tgt",
            os.path.join(prev_dir, "dev_tgt.txt"),
            "-shard_size",
            shard_size,
            "-src_seq_length",
            src_seq_length,
            "-tgt_seq_length",
            tgt_seq_length,
            "-save_data",
            os.path.join(dir, "data"),
            "-log_file",
            os.path.join(dir, "prep.log"),
        ]

        batch(self.stage_dir, *args)
