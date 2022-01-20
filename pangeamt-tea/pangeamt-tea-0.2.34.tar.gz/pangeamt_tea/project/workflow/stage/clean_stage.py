import tempfile
import shutil
import os
import logging
from pathos.multiprocessing import Pool
from contextlib import closing
import click
from pangeamt_tea.project.workflow.stage.base_stage import BaseStage
from pangeamt_nlp.processor.pipeline_training import PipelineTraining
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.multilingual_resource.tmx.tmx_reader_bilingual import (
    TmxReaderBilingualText,
)
from pangeamt_nlp.multilingual_resource.af.af_reader import AfReader
from pangeamt_nlp.multilingual_resource.bilingual.bilingual_reader import (
    BilingualReader,
)
from pangeamt_nlp.multilingual_resource.dataset.dataset_reader import (
    DatasetReader,
)
from pangeamt_nlp.multilingual_resource.dataset.dataset import Dataset


NUM_GOOD_LINES = 0
DROPPED_FROM = {}
SEGMENT_FROM = {}


def process(data, pipeline):
    resource_index = data[0]
    text = data[1]
    seg = Seg(text[0], text[1])
    try:
        pipeline.process(seg)
        text = (seg.src, seg.tgt)
        return (resource_index, text)
    except Exception as e:
        return (resource_index, e)


def post(data, src_file, tgt_file, debug, log_file, dataset):
    global NUM_GOOD_LINES
    global SEGMENT_FROM
    global DROPPED_FROM
    resource = dataset.resources[data[0]].file
    if isinstance(resource, tuple):
        resource = resource[0]
    resource = os.path.basename(resource)
    text = data[1]
    if not isinstance(text, Exception):
        if SEGMENT_FROM.get(resource, None) is None:
            SEGMENT_FROM[resource] = NUM_GOOD_LINES
        NUM_GOOD_LINES += 1
        src_file.write(text[0] + "\n")
        tgt_file.write(text[1] + "\n")
    else:
        DROPPED_FROM[resource] = DROPPED_FROM.get(resource, 0) + 1
        if debug:
            log_file.write(str(text) + f" from file {resource}\n")


class CleanStage(BaseStage):
    NAME = "clean"
    DIR = "01_cleaned"

    def __init__(self, workflow):
        super().__init__(workflow, self.NAME)

    async def run(self, max_workers: int, debug: bool):
        project = self.workflow.project
        project_dir = project.config.project_dir

        src_lang = project.config.src_lang
        tgt_lang = project.config.tgt_lang

        data_dir = self.create_data_directory()

        dataset = Dataset(data_dir)

        processors = project.config.processors

        # Make preparation Directory
        workflow_dir = self.workflow.get_dir(project_dir)
        self.stage_dir = os.path.join(workflow_dir, CleanStage.DIR)

        if os.path.isdir(self.stage_dir):
            raise Exception("Workflow stage folder already exists.")

        os.mkdir(self.stage_dir)

        af_reader = AfReader(src_lang, tgt_lang)
        bilingual_reader = BilingualReader(src_lang, tgt_lang)
        tmx_reader = TmxReaderBilingualText(src_lang, tgt_lang)

        dataset_reader = DatasetReader(tmx_reader, af_reader, bilingual_reader)
        dataset_length = dataset.get_num_trans_units()

        pipeline = PipelineTraining.create_from_dict(
            src_lang, tgt_lang, processors
        )

        src_file = open(os.path.join(self.stage_dir, "data_src.txt"), "w+")
        tgt_file = open(os.path.join(self.stage_dir, "data_tgt.txt"), "w+")
        if debug:
            log_file = open(
                os.path.join(self.stage_dir, "clean_log.txt"), "w+"
            )
        else:
            log_file = None

        logging.info("Starting to clean")

        with closing(Pool(max_workers)) as pool:
            with click.progressbar(
                pool.imap(
                    lambda x: process(x, pipeline),
                    dataset.read(dataset_reader, with_resource_index=True),
                    chunksize=500,
                ),
                length=dataset_length,
                label="Cleaning: ",
            ) as bar:
                for result in bar:
                    post(result, src_file, tgt_file, debug, log_file, dataset)

        src_file.close()
        tgt_file.close()
        if log_file:
            log_file.close()

        logging.info("Finished cleaning")

        shutil.rmtree(data_dir)

        output = {
            "useful": NUM_GOOD_LINES,
            "dropped": dataset_length - NUM_GOOD_LINES,
            "dropped_from": DROPPED_FROM,
            "resource_intervals": SEGMENT_FROM
        }

        return output

    def create_data_directory(self):
        config = self.workflow.config
        path = tempfile.mkdtemp()
        for resource in config.init["report"]["resources"]:
            files = resource["file"]
            if isinstance(files, str):
                files = [files]
            for file in files:
                dst = os.path.join(path, os.path.basename(file))
                os.symlink(file, dst)
        return path
