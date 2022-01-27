from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.processor.processor_factory import ProcessorFactory
from pangeamt_nlp.seg import Seg
from typing import List, Dict
from logging import Logger


class PipelineDecoding:
    def __init__(self, processors: List[NormalizerBase]):
        self._processors = processors

    def process_src(self, seg: Seg, logger: Logger = None) -> None:
        for p in self._processors:
            p.process_src_decoding(seg)
            if logger is not None:
                logger.debug(f"Applied: {p.NAME} -> {seg.src}")

    def process_tgt(self, seg: Seg, logger: Logger = None) -> None:
        for p in self._processors:
            p.process_tgt_decoding(seg)
            if logger is not None:
                logger.debug(f"Applied: {p.NAME} -> {seg.tgt}")

    # Method to create the decoding pipeline, expects src_lang, tgt_lang and
    # the processors dictionary from the config.
    @staticmethod
    def create_from_dict(
        src_lang: str, tgt_lang: str, processors_config: Dict
    ) -> "PipelineDecoding":
        # List that will be passed to initialize PipelineDecoding
        processors = []
        factory = ProcessorFactory
        # For each processor in the processors config dictionary
        for processor_name in processors_config:
            # Get the arguments to initialize the processor
            args = processors_config[processor_name]
            # Initialize the processor
            processor = factory.create(
                processor_name,
                src_lang,
                tgt_lang,
                *args
            )
            # Add the processor to the list of processors if it is a normalizer
            # discard if it is a validator
            if isinstance(processor, NormalizerBase):
                processors.append(processor)
        # Return the PipelineDecoding object
        return PipelineDecoding(processors)
