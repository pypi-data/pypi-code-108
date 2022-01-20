#!python
# -*- coding: utf-8 -*-
import argparse
import logging
import yaml
from pangeamt_nlp.processor.pipeline_decoding import PipelineDecoding
from pangeamt_nlp.seg import Seg


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Path to config file.")
    parser.add_argument("src_test", help="Src segment to test")
    parser.add_argument("tgt_test", help="Tgt segment to test")
    return parser


def main(src_test: str, tgt_test: str, config_path: str):
    logger = setup_log()
    pipeline = load_pipeline_from_config(config_path)
    seg = Seg(src_test, tgt_test)
    logger.info("=== SRC ===")
    pipeline.process_src(seg, logger)
    logger.info("=== TGT ===")
    pipeline.process_tgt(seg, logger)


def setup_log() -> logging.Logger:
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=logging.DEBUG
    )
    return logging.getLogger("main")


def load_pipeline_from_config(config_path: str) -> PipelineDecoding:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    processors = config["processors"]
    src_lang = config["src_lang"]
    tgt_lang = config["tgt_lang"]
    return PipelineDecoding.create_from_dict(
        src_lang, tgt_lang, processors
    )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args.src_test, args.tgt_test, args.config_file)
