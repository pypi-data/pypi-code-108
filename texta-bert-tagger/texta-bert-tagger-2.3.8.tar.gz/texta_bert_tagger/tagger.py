import torch
import os
import io
import json
import pandas as pd
import numpy as np
import time
import datetime
import random
import GPUtil
import dill
import math
import psutil
import warnings
import logging
import torch.nn.functional as F
import regex as re

from copy import deepcopy
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo

from typing import List, Dict, Tuple, Union

from .tagging_report import TaggingReport
from .config import Config

from .validators import ModelExistingValidator, ModelLoadedValidator
from .validators import InputValidator, ArgumentValidator
from . import exceptions

from transformers import BertTokenizer, BertForSequenceClassification, BertConfig, RobertaForSequenceClassification, CamembertTokenizer, AutoTokenizer, AutoConfig
from transformers import AdamW, get_linear_schedule_with_warmup

from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data import RandomSampler, SequentialSampler
from torch.utils.data import random_split
from collections import OrderedDict

warnings.filterwarnings("ignore")

class BertTagger:
    def __init__(self,
        allow_standard_output: bool = True,
        test_mode: bool = False,
        autoadjust_batch_size: bool = True,
        min_available_memory: int = 500,
        sklearn_avg_function: str = "macro",
        use_gpu: bool = True,
        save_pretrained: bool = True,
        pretrained_models_dir: str = "",
        logger = None,
        cache_dir = ""
    ):
        self.logger = logger
        self.stdout = allow_standard_output
        self.cache_dir = cache_dir

        if self.cache_dir:
            self._print(f"Using {self.cache_dir} as cache dir.")
            if self.logger: self.logger.info(f"Using {self.cache_dir} as cache dir.")

        self.config = Config()
        self.test_mode = test_mode
        self.use_gpu = use_gpu

        self.device_available_memory = None
        self.device_type = ""
        self.gpu_max_memory = 0.99

        self.autoadjust_batch_size = autoadjust_batch_size
        self.min_available_memory = min_available_memory
        self.sklearn_avg_function = sklearn_avg_function
        self.save_pretrained = save_pretrained
        self.pretrained_models_dir = pretrained_models_dir

        self.model = None

        self.device = self._get_device()

        self.models_dir = os.path.join(".","saved_models")

        self.optimizer = None
        self.scheduler = None
        self.tokenizer = None


    def _make_dir(self, _dir: str):
        """ Make directories.
        """
        if not os.path.exists(_dir):
            os.makedirs(_dir)


    def _print(self, text: str):
        """ Print output if printing results to stdout is enabled.
        """
        if self.stdout:
            print(text)


    def _adjust_batch_size(self, max_length: int, available_memory: int) -> int:
        """ Adjust batch size based on max sequence length and available memory.

        Parameters:
            max_length - Max sequence length of the BERT model.
            available_memory - Available memory in MBs.
        """
        benchmark_gpu_memory = 11000
        divider = benchmark_gpu_memory/(available_memory * 0.75)
        exp = math.log2(64) - (math.log2(max_length) - math.log2(64))
        adjusted_batch_size = math.floor((2**exp)/divider)
        return max(adjusted_batch_size, 1)


    def set_models_dir(self, model_dir: str):
        self.models_dir = model_dir


    def _to_megabytes(self, _bytes: int) -> int:
        """ Convert bytes to megabytes.

        Paramters:
            _bytes - Bytes to convert.
        """
        return round(_bytes* 9.537*(10**(-7)), 2)


    def _get_free_memory_cpu(self) -> float:
        """ Get available memory for device = CPU.
        """
        vm = psutil.virtual_memory()
        return self._to_megabytes(vm.free)


    def _get_gpu_memory_info(self, device_id: int) -> Dict[str, float]:
        """ Get GPU memory information.

        Parameters:
            device_id - GPU device id.
        """
        nvmlInit()
        h = nvmlDeviceGetHandleByIndex(device_id)
        info = nvmlDeviceGetMemoryInfo(h)

        m_total = self._to_megabytes(info.total)
        m_free = self._to_megabytes(info.free)
        m_used = self._to_megabytes(info.used)

        return {"total": m_total, "free": m_free, "used": m_used}


    def _sort_by_memory(self, device_ids: List[int], sort_by_key: str = "free") -> List[str]:
        """ Sort devices based on available/used/total memory.

        Parameters:
            device_ids - List of device ids.
            sort_by_key - Param. that should be used for sorting. Options = ['free', 'used', 'total']
        """
        device_memories = []
        for device_id in device_ids:
            device_memory_info = self._get_gpu_memory_info(device_id)
            device_memories.append((device_id, device_memory_info))
        device_memories.sort(key=lambda x: x[1][sort_by_key], reverse=True)
        return device_memories


    def _get_device(self):
        """ Get device to run the process on (GPU, if available, else CPU).
        """
        device = None
        use_cpu = True
        cpu_free_memory = self._get_free_memory_cpu()
        # If there's a GPU available...
        if self.use_gpu and torch.cuda.is_available():

            # Check if available GPU(s) have required amount of available memory.
            device_ids = GPUtil.getAvailable(order ="memory", maxMemory = self.gpu_max_memory)
            try:
                device_id, device_memory_info = self._sort_by_memory(device_ids, "free")[0]
                use_cpu = False

                if device_memory_info["free"] >= self.min_available_memory or cpu_free_memory < self.min_available_memory:
                    torch.cuda.empty_cache()
                    device = torch.device("cuda")
                    torch.cuda.set_device(device_id)
                    self._print(f"We will use the GPU: {torch.cuda.get_device_name(device_id)}")
                    self._print(f"Device memory: [Free: {device_memory_info['free']} MB; Used: {device_memory_info['used']} MB; Total: {device_memory_info['total']} MB]")
                    self._print(f"Device index: {torch.cuda.current_device()}")
                    if self.logger:
                        self.logger.info(f"We will use the GPU: {torch.cuda.get_device_name(device_id)}")
                        self.logger.info(f"Device memory: [Free: {device_memory_info['free']} MB; Used: {device_memory_info['used']} MB; Total: {device_memory_info['total']} MB]")
                        self.logger.info(f"Device index: {torch.cuda.current_device()}")
                    self.device_available_memory = device_memory_info["free"]
                    self.device_type = "gpu"
                else:
                    self._print(f"No GPU available with free memory >= {self.min_available_memory}. Using CPU.")
                    if self.logger:
                        self.logger.info(f"No GPU available with free memory >= {self.min_available_memory}. Using CPU.")
                    device = torch.device("cpu")
                    self.device_type = "cpu"
                    self.device_available_memory = cpu_free_memory
            except:
                use_cpu = True


        if use_cpu:
            self._print("No GPU available, not enough GPU memory, or GPU usage turned off, using the CPU instead.")
            self._print(f"Available memory: {cpu_free_memory} MB")
            if self.logger:
                self.logger.info("No GPU available, not enough GPU memory, or GPU usage turned off, using the CPU instead.")
                self.logger.info(f"Available memory: {cpu_free_memory} MB")

            device = torch.device("cpu")
            self.device_type = "cpu"
            self.device_available_memory = cpu_free_memory

        return device


    @staticmethod
    def normalize_name(bert_model_name: str) -> str:
        """ Normalize BERT model name to make it usable as a file name.

        Parameters:
            bert_model_name - Name of the BERT model to normalize.
        """
        normalized_name = re.sub("[/]", "_slash_", bert_model_name)
        return normalized_name


    @staticmethod
    def restore_name(normalized_name: str) -> str:
        """ Restore original BERT model name from the normalized version.

        Parameters:
            normalized_name - Normalized BERT model name.
        """
        bert_model_name = re.sub("_slash_", "/", normalized_name)
        return bert_model_name


    def load_pretrained(self, state_dict = OrderedDict()):
        """ Load pretrained BERT model.

        Parameters:
            state_dict - Fine-tuned model's loaded state_dict.
        """
        model_to_load = self.config.bert_model
        model_downloaded = False
        model_dir = os.path.join(self.pretrained_models_dir, BertTagger.normalize_name(self.config.bert_model), "model")

        if os.path.exists(model_dir) and len(os.listdir(model_dir)) > 0:
            self._print(f"Loading pretrained model from directory {model_dir}")
            model_to_load = model_dir
            model_downloaded = True

        if self.config.use_state_dict:
            # Initializing state_dict as None forces the usage of default state dict (not an empty one)
            state_dict = None

        model_kwargs = {"state_dict": state_dict, "num_labels": self.config.n_classes}

        if self.cache_dir:
             model_kwargs.update({"cache_dir": self.cache_dir})

        if not BertTagger.is_roberta_model(model_to_load):

            model = BertForSequenceClassification.from_pretrained(model_to_load, **model_kwargs)
        else:
            model = RobertaForSequenceClassification.from_pretrained(model_to_load, **model_kwargs)

        if self.device_type == "gpu" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            model.cuda()

        if self.save_pretrained and not model_downloaded:
            # Save model without specified number of labels
            del model_kwargs["num_labels"]
            # Save model without classes initialization
            if not BertTagger.is_roberta_model(model_to_load):
                model_to_save = BertForSequenceClassification.from_pretrained(model_to_load, **model_kwargs)
            else:
                model_to_save = RobertaForSequenceClassification.from_pretrained(model_to_load, **model_kwargs)
            self._print(f"Saving pretrained {self.config.bert_model} model files to {model_dir}.")
            model_to_save.save_pretrained(model_dir)
        return model


    @staticmethod
    def save_pretrained_model(bert_model: str, save_dir: str, state_dict: OrderedDict = None, logger: logging.Logger = None, cache_dir: str = "", num_labels: int = None):
        model_dir = os.path.join(save_dir, BertTagger.normalize_name(bert_model), "model")
        if not os.path.exists(model_dir) or len(os.listdir(model_dir)) < 1:
            if logger: logger.info(f"Downloading pretrained model {bert_model}...")

            model_kwargs = {"state_dict": state_dict}

            if num_labels:
                model_kwargs.update({"num_labels": num_labels})
            if cache_dir:
                 model_kwargs.update({"cache_dir": cache_dir})

            if not BertTagger.is_roberta_model(bert_model):
                model = BertForSequenceClassification.from_pretrained(bert_model, **model_kwargs)
            else:
                model = RobertaForSequenceClassification.from_pretrained(bert_model, **model_kwargs)
            model.save_pretrained(model_dir)
            if logger: logger.info(f"Download finished! Pretrained model saved into {model_dir}.")
        else:
            if logger: logger.info(f"Model {bert_model} already downloaded. Skipping.")


    @staticmethod
    def save_pretrained_tokenizer(bert_model: str, save_dir: str, logger: logging.Logger = None, cache_dir: str = ""):
        tokenizer_dir = os.path.join(save_dir, BertTagger.normalize_name(bert_model), "tokenizer")
        if not os.path.exists(tokenizer_dir) or len(os.listdir(tokenizer_dir)) < 1:
            if logger: logger.info(f"Downloading pretrained tokenizer {bert_model}...")
            model_kwargs = {}
            if cache_dir:
                 model_kwargs.update({"cache_dir": cache_dir})

            if not BertTagger.is_roberta_model(bert_model):
                tokenizer = BertTokenizer.from_pretrained(bert_model, **model_kwargs)
            else:
                try:
                    if logger: logger.info(f"Trying to use CamembertTokenizer...")
                    tokenizer = CamembertTokenizer.from_pretrained(bert_model, **model_kwargs)

                except Exception as e:
                    if logger: logger.info(f"Failed loading CamembertTokenizer, trying to use AutoTokenizer...")
                    model_kwargs.update({"use_fast": False})
                    config = AutoConfig.from_pretrained(bert_model)
                    tokenizer = AutoTokenizer.from_pretrained(bert_model, **model_kwargs)
                    config.save_pretrained(tokenizer_dir)

            tokenizer.save_pretrained(tokenizer_dir)
            if logger: logger.info(f"Download finished! Pretrained tokenizer saved into {tokenizer_dir}.")
        else:
            if logger: logger.info(f"Tokenizer {bert_model} already downloaded. Skipping.")


    @staticmethod
    def download_pretrained_models(bert_models: List[str], save_dir: str, logger: logging.Logger = None, cache_dir: str = "", num_labels: int = None):
        """ Download pretrained BERT models and tokenizers.

        Parameters:
            bert_models - Names of the BERT models to download.
            save_dir - Directory where to save the pretrained models and tokenizers.
            cache_dir - Directory where to save cache files.
        """
        failed_models = []
        errors = []
        for bert_model in bert_models:
            try:
                BertTagger.save_pretrained_tokenizer(bert_model, save_dir, logger=logger, cache_dir = cache_dir)
                BertTagger.save_pretrained_model(bert_model, save_dir, logger=logger, cache_dir = cache_dir, num_labels = num_labels)
            except:
                failed_models.append(bert_model)
        if failed_models:
            errors.append(f"Failed downloading models: {failed_models}. Make sure to use the correct model identifiers listed in https://huggingface.co/models.")
        return (errors, failed_models)


    def add_optimizer(self, optimizer):
        self.optimizer = optimizer


    def add_scheduler(self, scheduler):
        self.scheduler = scheduler


    def _get_pos_index(self):
        pos_class_index = 0
        if self.config.pos_label:
            pos_class_index = self.config.label_index[self.config.pos_label]
        elif len(self.config.label_index) == 2:
            if "true" in self.config.classes:
                pos_class_index = self.config.label_index["true"]
            else:
                raise exceptions.PosLabelNotSpecifiedError("Label set must contain label 'true' or positive label must be specified.")
        return pos_class_index


    def evaluate_model(self, iterator: DataLoader) -> TaggingReport:
        """ Evaluates the model using evaluation set & Tagging Report.

        Parameters:
            iterator - Instance of torch.utils.data.DataLoader

        Returns:
            report - Instance of TaggingReport containing the results.
        """
        # Measure evaluation time
        t0 = time.time()

        all_preds = []
        all_y = []
        all_probs = []

        total_eval_loss = 0

        # Put model into evaluation mode
        self.model.eval()

        # Evaluate data for one epoch
        for i, batch in enumerate(iterator):

            # As we unpack the batch, we'll also copy each tensor to the GPU
            b_input_ids  = batch[0].to(self.device)
            b_input_mask = batch[1].to(self.device)
            b_labels     = batch[2].to(self.device)
            b_segment_ids = None

            # Tell pytorch not to bother with constructing the compute graph during
            # the forward pass, since this is only needed for backprop (training).
            with torch.no_grad():
                outputs = self.model(b_input_ids,
                                       token_type_ids=b_segment_ids,
                                       attention_mask=b_input_mask,
                                       labels=b_labels)

            loss, logits = outputs['loss'], outputs['logits']
            # Accumulate the validation loss.
            total_eval_loss+=loss.item()

            # Move logits and labels to CPU
            logits = logits.detach().cpu()#.numpy() # preds
            label_ids = b_labels.to("cpu").numpy()
            labels_flat = label_ids

            preds_flat = np.argmax(logits.numpy(), axis=1).flatten()

            # Probabilities of the positive class
            pos_class_index = self._get_pos_index()
            probabilities = logits.softmax(1).numpy()[:, pos_class_index]

            all_preds.extend(preds_flat)
            all_y.extend(labels_flat)
            all_probs.extend(probabilities)

        # Calculate the average loss over all of the batches.
        avg_loss = total_eval_loss / len(iterator)

        # Measure how long the validation run took.
        time_elapsed = time.time() - t0

        report = TaggingReport(all_y, all_preds, all_probs, pos_class_index, self.config.classes, self.config.class_indices, average=self.sklearn_avg_function)
        report.validation_time = time_elapsed
        report.validation_loss = avg_loss

        return report


    def _run_epoch(self, train_iterator: DataLoader,
                         val_iterator: DataLoader,
                         epoch: int) -> TaggingReport:
        """ Run one training epoch epoch.

        Parameters:
            train_iterator - Iterator containing training data.
            val_iterator   - Iterator containing validation data.
            epoch - epoch number.

        Returns:
            report - Instance of TaggingReport containg results for one epoch.
        """

        # Measure how long the training epoch takes.
        t0 = time.time()

        # Reset the total loss for this epoch.
        total_train_loss = 0

        # Put the model into training mode.
        self.model.train()

        # For each batch of training data...
        for i, batch in enumerate(train_iterator):
            # Unpack this training batch from our dataloader.
            #
            # As we unpack the batch, we'll also copy each tensor to the GPU
            b_input_ids   = batch[0].to(self.device)
            b_input_mask  = batch[1].to(self.device)
            b_labels      = batch[2].to(self.device)
            b_segment_ids = None

            # Always clear any previously calculated gradients before performing a
            # backward pass. PyTorch doesn't do this automatically because
            # accumulating the gradients is "convenient while training RNNs".
            self.model.zero_grad()

            # Perform a forward pass (evaluate the model on this training batch).
            outputs = self.model(b_input_ids,
                                      token_type_ids = b_segment_ids,
                                      attention_mask = b_input_mask,
                                      labels = b_labels)

            loss, logits = outputs['loss'], outputs['logits']
            # Accumulate the training loss.
            total_train_loss += loss.item()

            # Perform a backward pass to calculate the gradients.
            loss.backward()

            # Clip the norm of the gradients to 1.0.
            # This is to help prevent the "exploding gradients" problem.
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            # Update parameters and take a step using the computed gradient.
            # The optimizer dictates the "update rule"--how the parameters are
            # modified based on their gradients, the learning rate, etc.
            self.optimizer.step()

            # Update the learning rate.
            self.scheduler.step()

        # Calculate the average loss over all of the batches.
        avg_train_loss = total_train_loss / len(train_iterator)

        # Measure how long this epoch took.
        training_time = time.time() - t0

        report = self.evaluate_model(val_iterator)

        # Add training time, training_loss and epoch number to report
        report.training_time = training_time
        report.training_loss = avg_train_loss
        report.epoch = epoch

        return report


    @staticmethod
    def is_roberta_model(model_to_load: str) -> bool:
        if re.search("roberta", model_to_load, re.IGNORECASE):
            return True
        return False


    def load_tokenizer(self):
        """ Load pretrained BERT tokenizer.
        """
        model_to_load = self.config.bert_model
        model_downloaded = False
        model_dir = os.path.join(self.pretrained_models_dir, BertTagger.normalize_name(self.config.bert_model), "tokenizer")

        if os.path.exists(model_dir) and len(os.listdir(model_dir)) > 0:
            self._print(f"Loading pretrained tokenizer from directory {model_dir}")
            if self.logger: self.logger.info(f"Loading pretrained tokenizer from directory {model_dir}")
            model_to_load = model_dir
            model_downloaded = True


        model_kwargs = {}
        if self.cache_dir:
            model_kwargs.update({"cache_dir": self.cache_dir})

        if not BertTagger.is_roberta_model(model_to_load):
            self._print("Using regular BERT tokenizer...")
            if self.logger: self.logger.info(f"Using regular BERT tokenizer...")
            tokenizer = BertTokenizer.from_pretrained(model_to_load, **model_kwargs)
        else:
            try:
                self._print("Using CamembertTokenizer...")
                if self.logger: self.logger.info(f"Using CamembertTokenizer...")

                tokenizer = CamembertTokenizer.from_pretrained(model_to_load, **model_kwargs)

            except Exception as e:
                self._print("Failed loading CamembertTokenizer, trying to use AutoTokenizer...")
                if self.logger: self.logger.info(f"Failed loading CamembertTokenizer, trying to use AutoTokenizer...")
                model_kwargs.update({"use_fast": False})

                tokenizer = AutoTokenizer.from_pretrained(model_to_load, **model_kwargs)


        if self.save_pretrained and not model_downloaded:
            self._print(f"Saving pretrained {self.config.bert_model} tokenizer model files to {model_dir}.")
            if self.logger: self.logger.info(f"Saving pretrained {self.config.bert_model} tokenizer model files to {model_dir}.")
            tokenizer.save_pretrained(model_dir)
        return tokenizer

    def tokenize(self, sentences: List[str], labels: list=[]):
        """ Tokenize all the sentences and map the tokens to their corresponding IDs.

        Parameters:
            sentences - List of (short) texts.
            labels - Labels corresponding to each text.

        Returns:
            input_ids - IDs corresponding to each token.
            attention_mask - Attention masks.
            labels - Labels as torch.tensors instance.

        """
        if not self.tokenizer:
            self.tokenizer = self.load_tokenizer()

        input_ids = []
        attention_masks = []

        # For every sentence...
        for sentence in sentences:
            # `encode_plus` will:
            #   (1) Tokenize the sentence.
            #   (2) Prepend the `[CLS]` token to the start.
            #   (3) Append the `[SEP]` token to the end.
            #   (4) Map tokens to their IDs.
            #   (5) Pad or truncate the sentence to `max_length`
            #   (6) Create attention masks for [PAD] tokens.
            encoded_dict = self.tokenizer.encode_plus(
                                sentence,
                                add_special_tokens = self.config.add_special_tokens,
                                max_length = self.config.max_length,
                                padding = self.config.padding,
                                truncation = self.config.truncation,
                                return_attention_mask = self.config.return_attention_mask,
                                return_tensors = self.config.return_tensors
                           )

            # Add the encoded sentence to the list.
            input_ids.append(encoded_dict["input_ids"])

            # And its attention mask (simply differentiates padding from non-padding).
            attention_masks.append(encoded_dict["attention_mask"])

        # Convert the lists into tensors.
        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        #if labels:
        labels = torch.tensor(labels)

        return (input_ids, attention_masks, labels)


    def _force_str(self, data_sample: Dict[str, list]) -> Dict[str, List[str]]:
        """ Force string on each value.

        Parameters:
            data_sample: Training (and valiation) data as dict where keys = labels, values = example texts.

        """
        self._print("Forcing all values to string...")
        if self.logger: self.logger.info("Forcing all values to string...")
        for key, values in list(data_sample.items()):
            data_sample[key] = [str(v) for v in values]
        return data_sample


    def _get_dataset(self, input_ids, attention_masks, labels=[]) -> TensorDataset:
        """ Combine the training inputs into a TensorDataset.

        Parameters:
            input_ids - tokenizer output IDs as torch tensors.
            attention_masks - tokenizer output attention_masks as torch tensors.
            labels - tokenizer output labels as torch tensors.

        """
        if isinstance(labels, list) and not labels:
            dataset = TensorDataset(input_ids, attention_masks)
        else:
            dataset = TensorDataset(input_ids, attention_masks, labels)
        return dataset


    def _split_dataset(self, dataset: TensorDataset) -> Tuple[TensorDataset, TensorDataset]:
        """ Split dataset into training and validation set.

        Parameters:
            dataset - TensorDataset instance to split.

        Returns:
            train_dataset - TensorDataset instance containing training examples.
            val_dataset - TensorDataset instance containing validation examples.
        """
        # Calculate the number of samples to include in each set.
        train_size = int(self.config.split_ratio * len(dataset))
        val_size = len(dataset) - train_size

        # Divide the dataset by randomly selecting samples.
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        return (train_dataset, val_dataset)


    def _get_iterator(self, dataset: TensorDataset,
                            dataset_type: str = "train") -> DataLoader :
        """ Get DataLoader based on dataset type (random for training,
            sequential for validation.

        Parameters:
            dataset - TensorDataset instance to iterate.
            dataset_type - Indicatior if dataset is used for training or validation.

        Returns:
            iterator - Instance of type DataLoader for iterating over datasets.
        """
        if dataset_type == "train":
            sampler = RandomSampler(dataset)
        else:
            sampler = SequentialSampler(dataset)
        iterator = DataLoader(dataset, sampler=sampler, batch_size=self.config.batch_size)
        return iterator


    def get_optimizer(self) -> AdamW:
        """ Get AdamW optimizer for training the model.

        Returns:
            optimizer - AdamW optimizer.
        """
        ModelLoadedValidator().validate(self.model)
        # Note: AdamW is a class from the huggingface library (as opposed to pytorch)
        optimizer = AdamW( self.model.parameters(),
                           lr  = self.config.lr,
                           eps = self.config.eps
                         )
        return optimizer


    def get_scheduler(self, n_training_batches: int, optimizer: AdamW):
        """ Get learning rate scheduler.

        Parameters:
            n_training_batches - Number of training batches.
            optimizer - AdamW optimizer.

        Returns:
            scheduler - Learning rate scheduler.
        """
        # Total number of training steps is [number of batches] x [number of epochs].
        # (Note that this is not the same as the number of training samples).
        total_steps = n_training_batches * self.config.n_epochs

        # Create the learning rate scheduler.
        scheduler = get_linear_schedule_with_warmup(
                        optimizer,
                        num_warmup_steps = 0, # Default value in run_glue.py
                        num_training_steps = total_steps
                    )
        return scheduler


    def _get_examples_and_labels(self, data_sample: Dict[str, List[str]]) -> Tuple[List[str], List[int]]:
        """ Extract examples and labels from data_samples.

        Parameters:
            data_sample - Training (and valiation) data as dict where keys = labels, values = example texts.

        Returns:
            examples - Training (and validation) examples.
            labels - Labels corresponding to each example.
        """
        examples = []
        labels = []

        # Retrieve examples for each class
        for label, class_examples in data_sample.items():
            for example in class_examples:
                examples.append(example)
                labels.append(self.config.label_index[label])

        return (examples, labels)


    def _create_label_indices(self, data_sample: Dict[str, List[str]]):
        """ Create label indices.
        """
        self.config.label_index = {a: i for i, a in enumerate(data_sample.keys())}
        self.config.label_reverse_index = {b: a for a, b in self.config.label_index.items()}


    def _prepare_data(self, data_sample: Dict[str, List[str]]) -> Tuple[DataLoader, DataLoader]:
        """ Prepare training data.
        """
        self._print("Preparing data...")
        if self.logger: self.logger.info("Preparing_data...")
        self.config.n_classes = len(data_sample)


        data_sample = self._force_str(data_sample)

        self._create_label_indices(data_sample)
        self.config.classes = list(self.config.label_index.keys())
        self.config.class_indices = list(self.config.label_index.values())

        sentences, labels = self._get_examples_and_labels(data_sample)

        self._print(f"Using trainset size {len(sentences)}...")
        self._print(f"Tokenizing data...")

        if self.logger:
            self.logger.info(f"Using trainset size {len(sentences)}...")
            self.logger.info(f"Tokenizing data...")

        input_ids, attention_masks, labels = self.tokenize(sentences, labels)
        dataset = self._get_dataset(input_ids, attention_masks, labels)
        train_dataset, val_dataset = self._split_dataset(dataset)

        train_iterator = self._get_iterator(train_dataset, "train")
        val_iterator = self._get_iterator(val_dataset, "validation")

        return (train_iterator, val_iterator)


    def update_config(self, **kwargs):
        """ Update configuration.
        """
        ArgumentValidator().validate_arguments(**kwargs)
        if self.autoadjust_batch_size:
            max_length = kwargs["max_length"] if "max_length" in kwargs else self.config.max_length
            adjusted_batch_size = self._adjust_batch_size(max_length, self.device_available_memory)
            self._print(f"Adjusted batch size: {adjusted_batch_size}")
            if self.logger: self.logger.info(f"Adjusted batch size: {adjusted_batch_size}")
            if "batch_size" in kwargs:
                # If the batch size given by the user is smaller than automatically adjusted one, use users input
                batch_size = min(adjusted_batch_size, kwargs["batch_size"])
            else:
                batch_size = adjusted_batch_size
            self._print(f"Using batch size: {batch_size}")
            if self.logger: self.logger.info(f"Using batch size: {batch_size}")
            kwargs["batch_size"] = batch_size

        self.config.update_bulk(kwargs)
        # Make sure not to use old pos label
        if not "pos_label" in kwargs:
            self.config.pos_label = ""
        # Update tokenizer as it might have been changed
        self.tokenizer = self.load_tokenizer()
        return True


    def _set_seeds(self):
        random.seed(self.config.seed_val)
        np.random.seed(self.config.seed_val)
        torch.manual_seed(self.config.seed_val)
        torch.cuda.manual_seed_all(self.config.seed_val)


    def train(self, data_sample: Dict[str, List[str]], from_checkpoint: bool = False, **kwargs) -> TaggingReport:
        """ Fine-tune BERT model.

        Parameters:
            data_sample - Training (and valiation) data as dict where
                          keys = labels, values = example texts.
            from_checkpoint - If enabled, use a loaded fine-tuned model.

        """

        InputValidator().validate(data_sample, **kwargs)

        self.update_config(**kwargs)

        train_iterator, val_iterator = self._prepare_data(data_sample)

        # Set the seed value all over the place to make this reproducible.
        self._set_seeds()

        n_training_batches = len(train_iterator)

        # Measure the total training time for the whole run.
        total_t0 = time.time()
        self.epoch_reports = []


        # If from_checkpoint is enabled, check if the model to fine-tune actually exists
        if from_checkpoint:
            if self.model:
                self._print("Continuing training from a checkpoint...")
                if self.logger: self.logger.info(f"Continuing training from a checkpoint...")
            else:
                raise exceptions.ModelNotLoadedError(f"No model found. You should load a fine-tuned model or train a model with 'from_checkpoint' set to False.")

        # If from checkpoint is disabled, load a fresh state of a pre-trained model.
        else:
            self.model = self.load_pretrained()

        optimizer = self.get_optimizer()
        scheduler = self.get_scheduler(n_training_batches, optimizer)

        self.add_optimizer(optimizer)
        self.add_scheduler(scheduler)

        self._print("Start training...")
        if self.logger: self.logger.info("Start training...")

        # For each epoch...
        for epoch_i in range(self.config.n_epochs):
            self._print(f"Running epoch {epoch_i+1}/{self.config.n_epochs}...")
            if self.logger: self.logger.info(f"Running epoch {epoch_i+1}/{self.config.n_epochs}...")

            report = self._run_epoch(train_iterator, val_iterator, epoch_i)
            self.epoch_reports.append(report)

        self._print("Finished training!")
        if self.logger: self.logger.info("Finished training!")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return report


    def tag_text(self, text: str) -> Dict[str, Union[str, float]]:
        """ Tag text with previously loaded or trained model.

        Parameters:
            text - Text to tag.

        Returns:
            prediction - Predicted label for the input text.
            probability - Probability of the predicted label.
        """
        ModelLoadedValidator().validate(self.model)

        input_ids, attention_masks, labels = self.tokenize([text])
        prediction_dataset = self._get_dataset(input_ids, attention_masks)
        prediction_iterator= self._get_iterator(prediction_dataset)

        # Put model in evaluation mode
        self.model.eval()

        # Tracking variables
        predictions = []
        probabilities = []

        # Predict
        for batch in prediction_iterator:
            # Add batch to GPU
            batch = tuple(t.to(self.device) for t in batch)

            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask = batch

            # Telling the model not to compute or store gradients, saving memory and
            # speeding up prediction
            with torch.no_grad():
                # Forward pass, calculate logit predictions
                outputs = self.model(b_input_ids, token_type_ids=None,
                                     attention_mask=b_input_mask)

            logits = outputs['logits']
            #logits = outputs[0]

            # Move logits and labels to CPU
            logits = logits.detach().cpu()#.numpy()

            # Store predictions and true labels
            predictions.append(logits.numpy())

            # Add class probabilities
            probabilities.append(logits.softmax(1).numpy().flatten())


        flat_predictions = np.concatenate(predictions, axis=0)

        # For each sample, pick the label (0 or 1) with the higher score.
        flat_predictions = np.argmax(flat_predictions, axis=1).flatten()

        prediction = flat_predictions[0]
        probability = probabilities[0][prediction]
        predicted_label = self.config.label_reverse_index[prediction]

        return {"prediction": predicted_label, "probability": probability}


    def tag_doc(self, doc: json) -> Dict[str, Union[str, float]]:
        """
        Tag document with previously loaded or trained model by combining
        all fields in the document into one text.

        Parameters:
            doc - JSON document to tag. NB! each input field is used for tagging!

        Returns:
            prediction - Predicted label for the input document.
            probability - Probability of the predicted label.
        """
        combined_text = []
        for field_content in list(doc.values()):
            combined_text.append(str(field_content))
        combined_text = " ".join(combined_text)
        predicted_item = self.tag_text(combined_text)
        return predicted_item


    def save(self, path: str):
        """ Save fine-tuned model.

        Parameters:
            path - Path of the file where the model is saved.
        """
        directory = directory = os.path.dirname(path)
        self._make_dir(directory)

        buffer = io.BytesIO()
        torch.save(self.model, buffer)

        to_save = {"tagger_conf": self.config.to_dict(),
                   "model": buffer}

        with open(path, "wb") as f:
            dill.dump(to_save, f)

        self._print(f"Model saved into: {path}")
        if self.logger: self.logger.info(f"Model saved into: {path}")


    def _set_loaded_values(self, loaded):
        """ Use loaded configuration values.
        """

        if isinstance(loaded["model"], io.BytesIO):
            buffer = loaded["model"]
            buffer.seek(0)
            self.model = torch.load(buffer, map_location=self.device)

        # Make it compatible with older models
        else:
            self.model = loaded["model"]

        self.config.update_bulk(loaded["tagger_conf"])

        # Assign model to current device
        if not self.test_mode:
            self.model.to(self.device)


    def load(self, path: str):
        """ Load fine-tuned model.

        Parameters:
            path - Path to model file.
        """
        ModelExistingValidator().validate_saved_model(path)

        with open(path, "rb") as f:
            try:
                loaded = dill.load(f)
            except RuntimeError:
                raise exceptions.IncompatibleVersionAndDeviceError(f"The models trained on texta-bert-tagger version <=2.2.0 cannot be loaded onto device '{self.device_type}' if they were trained on another type of device.")

        self._set_loaded_values(loaded)
        return True
