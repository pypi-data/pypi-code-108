import argparse
import math
import os
from typing import Type

import torch
from torch.utils.data import DataLoader
from transformers import  BertConfig
from transformers import BertTokenizer

from .spert import models, prediction
from .spert import sampling
from .spert import util
from .spert.entities import Dataset
from .spert.input_reader import  BaseInputReader
from .spert.trainer import BaseTrainer

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


class Predictor(BaseTrainer):
    """ Joint entity and relation extraction training and evaluation """

    def __init__(self, args: argparse.Namespace,types_path: str, input_reader_cls: Type[BaseInputReader]):
        super().__init__(args)

        # byte-pair encoding
        self._tokenizer = BertTokenizer.from_pretrained(args.tokenizer_path,
                                                        do_lower_case=args.lowercase,
                                                        cache_dir=args.cache_path)
        self.input_reader = input_reader_cls(types_path, self._tokenizer,
                                        max_span_size=args.max_span_size,
                                        spacy_model=args.spacy_model)
        self.model = self._load_model( self.input_reader)
        self.model.to(self._device)

    def predict_on_raw_text(self, text_list):
        args = self._args
        dataset = self.input_reader.read(text_list,"dataset")

        # self.model.to(self._device)

        return self._predict(self.model, dataset, self.input_reader)

    def _load_model(self, input_reader):
        model_class = models.get_model(self._args.model_type)

        config = BertConfig.from_pretrained(self._args.model_path, cache_dir=self._args.cache_path)
        util.check_version(config, model_class, self._args.model_path)

        config.spert_version = model_class.VERSION
        model = model_class.from_pretrained(self._args.model_path,
                                            config=config,
                                            # SpERT model parameters
                                            cls_token=self._tokenizer.convert_tokens_to_ids('[CLS]'),
                                            relation_types=input_reader.relation_type_count - 1,
                                            entity_types=input_reader.entity_type_count,
                                            max_pairs=self._args.max_pairs,
                                            prop_drop=self._args.prop_drop,
                                            size_embedding=self._args.size_embedding,
                                            freeze_transformer=self._args.freeze_transformer,
                                            cache_dir=self._args.cache_path)

        return model

    
    def _predict(self, model: torch.nn.Module, dataset: Dataset, input_reader: BaseInputReader):
        # create data loader
        dataset.switch_mode(Dataset.EVAL_MODE)
        data_loader = DataLoader(dataset, batch_size=self._args.eval_batch_size, shuffle=False, drop_last=False,
                                 num_workers=self._args.sampling_processes, collate_fn=sampling.collate_fn_padding)

        pred_entities = []
        pred_relations = []

        with torch.no_grad():
            model.eval()

            # iterate batches
            total = math.ceil(dataset.document_count / self._args.eval_batch_size)
            for batch in data_loader:
                # move batch to selected device
                batch = util.to_device(batch, self._device)

                # run model (forward pass)
                result = model(encodings=batch['encodings'], context_masks=batch['context_masks'],
                               entity_masks=batch['entity_masks'], entity_sizes=batch['entity_sizes'],
                               entity_spans=batch['entity_spans'], entity_sample_masks=batch['entity_sample_masks'],
                               inference=True)
                entity_clf, rel_clf, rels = result

                # convert predictions
                predictions = prediction.convert_predictions(entity_clf, rel_clf, rels,
                                                             batch, self._args.rel_filter_threshold,
                                                             input_reader)

                batch_pred_entities, batch_pred_relations = predictions
                pred_entities.extend(batch_pred_entities)
                pred_relations.extend(batch_pred_relations)

        return prediction.store_predictions(dataset.documents, pred_entities, pred_relations, self._args.predictions_path)

    