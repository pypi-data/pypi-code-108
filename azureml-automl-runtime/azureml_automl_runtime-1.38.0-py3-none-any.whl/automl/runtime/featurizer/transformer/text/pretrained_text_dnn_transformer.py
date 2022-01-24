# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
BERT-esque finetuning+Transformer
"""

from __future__ import absolute_import, division, print_function
from sklearn.metrics import accuracy_score
from typing import List
import logging
import math
import numpy as np
import os
import random
import time

from ..automltransformer import AutoMLTransformer
from ..data.word_embeddings_info import EmbeddingInfo

from azureml.automl.core import _codegen_utilities as codegen_utilities
from azureml.automl.core._experiment_observer import ExperimentStatus, NullExperimentObserver
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AllTargetsOverlapping,
    TextDnnModelDownloadFailed)
from azureml.automl.core.shared.exceptions import FitException, TransformException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.transformer_runtime_exceptions import (
    PretrainedTextDnnTransformerFitUnsupportedTaskException,
    PretrainedTextDnnTransformerConvertUnsupportedTaskException)
from azureml.automl.runtime.distributed.utilities import is_master_process, horovod_initialized
from azureml._common._error_definition import AzureMLError

try:
    import torch
    from torch.utils.data import (DataLoader, RandomSampler,
                                  SequentialSampler,
                                  TensorDataset)
    from torch.utils.data.distributed import DistributedSampler
    from pytorch_transformers import AdamW, WarmupLinearSchedule
    from .automl_pytorch_transformers import (BertTransformerLowerDim,
                                              BertTransformerLinear,
                                              XLNetTransformerLinear,
                                              XLNetTransformerLowerDim,
                                              MODEL_CLASSES)

    import horovod.torch as hvd
except Exception:
    pass

_logger = logging.getLogger(__name__)


class PretrainedTextDNNTransformer(AutoMLTransformer):
    """ Class for fine-tuning pretrained text DNN's like BERT that
    relies on huggingface's pytorch implementation.
    This will be used as a scikit-style transformer.  Calling fit()
    will fine tune the model and transform() will
    output the fine-tuned model's sentence embedding.
    """
    is_distributable = True
    is_separable = True

    def __init__(self, provider,
                 task_name="classification",
                 max_seq_length=128,
                 do_lower_case=True,
                 train_batch_size=32,
                 per_gpu_train_batch_size=None,
                 per_gpu_eval_batch_size=None,
                 eval_batch_size=32,
                 learning_rate=5e-5,
                 max_grad_norm=1.0,
                 adam_epsilon=1e-8,
                 num_train_epochs=3,
                 warmup_proportion=0.1,
                 no_cuda=False,
                 seed=42,
                 gradient_accumulation_steps=1,
                 fp16=False,
                 loss_scale=0,
                 is_lower_dim=True,
                 load_from_file=False,
                 verbose=False,
                 weight_decay=0.01,
                 warmup_steps=0,
                 max_steps=0,
                 model_name=None,
                 fp16_opt_level='O1',
                 early_stopping=False,
                 patience=3,
                 min_train_epochs=1,
                 n_gpu=None,
                 epsilon=0.0001,
                 max_progress_updates=100):

        super().__init__()
        self.model_name = model_name
        self.task_name = task_name
        self.max_seq_length = max_seq_length
        self.do_lower_case = do_lower_case
        self.train_batch_size = train_batch_size
        self.eval_batch_size = eval_batch_size
        self.learning_rate = learning_rate
        self.num_train_epochs = num_train_epochs
        self.warmup_proportion = warmup_proportion
        self.no_cuda = no_cuda
        self.seed = seed
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.fp16 = fp16
        self.loss_scale = loss_scale
        self.is_lower_dim = is_lower_dim
        self.load_from_file = load_from_file
        self.verbose = verbose
        self.adam_epsilon = adam_epsilon
        self.per_gpu_train_batch_size = per_gpu_train_batch_size
        self.weight_decay = weight_decay
        self.warmup_steps = warmup_steps
        self.max_steps = max_steps
        self.fp16_opt_level = fp16_opt_level
        self.max_grad_norm = max_grad_norm
        self.per_gpu_eval_batch_size = per_gpu_eval_batch_size
        self.provider = provider
        self.early_stopping = early_stopping
        self.patience = patience
        self.min_train_epochs = min_train_epochs
        self.n_gpu = n_gpu
        self.epsilon = epsilon
        self.max_progress_updates = max_progress_updates
        self.horovod_distributed = False

        self.total_train_time = 0.0
        self.device = None
        self.model = None

        self.observer = NullExperimentObserver()
        self.curr_progress = 0.0
        self.num_total_steps = 0

    def __repr__(self):
        params = self.get_params()
        provider = params.pop("provider")

        return codegen_utilities.generate_repr_str(self.__class__, params, provider=provider)

    def _get_imports(self):
        return super()._get_imports() + [
            codegen_utilities.get_import(self.provider)
        ]

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(PretrainedTextDNNTransformer, self)._to_dict()
        dct['id'] = "pretrained_text_dnn"
        dct['type'] = 'text'
        return dct

    def __getstate__(self):
        state = self.__dict__
        # Override method to force model to be saved as a cpu for easy deserialization.
        # if deserialized in a gpu environment, in _evaluation and _train the .to(device) will be reset
        if self.model is not None:
            self.device = "cpu"
            self._to_device()
        state["observer"] = None
        return super(PretrainedTextDNNTransformer, self).__getstate__()

    def __setstate__(self, state):
        state['observer'] = NullExperimentObserver()
        return super(PretrainedTextDNNTransformer, self).__setstate__(state)

    def _gpu_detect(self):
        # set gpu parameters depending on detected compute,
        # latency of this method azure nc6 vm is ~ 2 microseconds
        gpu_is_available = torch.cuda.is_available()

        if gpu_is_available and not self.no_cuda:
            if self.horovod_distributed:
                self.device = torch.device("cuda", hvd.local_rank())
                torch.cuda.set_device(hvd.local_rank())
            else:
                self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        # Unless user wants to use only one GPU detect the GPUs
        if self.n_gpu != 1 and not self.horovod_distributed:
            self.n_gpu = torch.cuda.device_count()

        return gpu_is_available

    def _to_device(self):
        self.model.to(self.device)

    def _to_device_parallel(self):
        if self.n_gpu > 1:
            self.model = torch.nn.DataParallel(self.model)

    def set_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if self.n_gpu > 0:
            torch.cuda.manual_seed_all(self.seed)

    def handle_val_data(self, X_valid, y_valid, y_train):
        y_valid_extra = np.setdiff1d(y_valid, y_train)
        y_valid_filtered = []
        X_valid_filtered = []
        i = 0
        for y_i in y_valid:
            if np.isin(y_i, y_valid_extra, invert=True):
                y_valid_filtered.append(y_i)
                X_valid_filtered.append(X_valid[i])
            i += 1
        return X_valid_filtered, y_valid_filtered

    @horovod_initialized
    def fit(self, X_train, y_train, X_valid=None, y_valid=None):
        self._update_distributed()

        if self.task_name not in ["classification", "regression"]:
            raise PretrainedTextDnnTransformerFitUnsupportedTaskException(
                "{} is not supported".format(self.task_name),
                target="PretrainedTextDNNTransformer",
                reference_code=ReferenceCodes._TEXT_DNN_FIT_NOT_SUPPORT,
                has_pii=False)
        val_dataset = None
        if self.early_stopping and (X_valid is None or y_valid is None):
            from sklearn.model_selection import train_test_split
            # Create a train & val split from train data for early stopping
            X_train, X_valid, y_train, y_valid =\
                train_test_split(X_train, y_train, test_size=0.2,
                                 random_state=self.seed)

            # handle missing labels in train-data compared to val data
            X_valid, y_valid = self.handle_val_data(X_valid, y_valid, y_train)

        # This should be done after the train-labels have been generated
        self.label_list = np.unique(y_train)
        self.num_labels = len(self.label_list)

        # Set device and n_gpu attrs and logging.
        self._gpu_detect()
        self.set_seed()
        _logger.info("Device being used = {}".format(self.device))
        _logger.info("Number of GPUs = {}".format(self.n_gpu))

        self._initialize()

        self.n_train = len(y_train)
        self._to_device()

        if self.early_stopping:
            val_dataset = self._generate_dataset(X_valid, y_valid)

        train_dataset = self._generate_dataset(X_train, y_train)

        # Error classify any problems with model training
        try:
            self._train(train_dataset, val_dataset, y_valid)
        except Exception as e:
            raise FitException.from_exception(
                e, has_pii=True, target="PretrainedTextDNNTransformer--train problem",
                reference_code=ReferenceCodes._TEXT_DNN_FIT
            ).with_generic_msg("Exception raised while training PretrainedTextDNNTransformer for fit")
        # finished fine-tuning, so turn this off for back-compat with legacy multi-gpu code
        self.horovod_distributed = False
        return self

    def predict(self, X):
        # TODO: remove need for "prediction" transformer_type
        self.transformer_type = "prediction"
        dataset = self._generate_dataset(X, y=None)
        return self._evaluate(dataset, transform_type=self.transformer_type)

    def transform(self, X):
        self.transformer_type = "embedding"
        dataset = self._generate_dataset(X, y=None)
        try:
            return self._evaluate(dataset, transform_type=self.transformer_type)
        except Exception as e:
            raise TransformException.from_exception(
                e, has_pii=True, target="PretrainedTextDNNTransformer",
                reference_code=ReferenceCodes._TEXT_DNN_TRANSFORM
            ).with_generic_msg("Exception raised while transforming data using PretrainedTextDNNTransformer")

    def set_model_type(self):
        # TODO: figure out better way to find the model_name
        if self.model_name is None:
            self.model_name = self.provider._embedding_info._embedding_name

        if "xlnet" in self.model_name:
            self.model_type = "xlnet"
        elif "bert" in self.model_name:
            self.model_type = "bert"

    def _initialize(self):
        # Load logic in pytorch-transformer package
        # Error classify any problems with model downloading as a part of fit() calls
        try:
            self.set_model_type()
            config_class, model_class, tokenizer_class =\
                MODEL_CLASSES[self.model_type]

            # TODO: put the ...LowerDim and ...Linear transformers into
            # one class and just parametrize whether we use the the hidden
            # dimension.  When this was naively implemented there was a
            # pytorch-transformer exception thrown in trying to
            # instantiate the model.
            if self.model_type == "bert":
                if self.is_lower_dim:
                    model_class = BertTransformerLowerDim
                else:
                    model_class = BertTransformerLinear
            elif self.model_type == "xlnet":
                if self.is_lower_dim:
                    model_class = XLNetTransformerLowerDim
                else:
                    model_class = XLNetTransformerLinear
            model_path = self.provider.get_model_dirname()
            model_name = self.provider._embeddings_name
            self.do_lower_case = self.provider.is_lower

            self.config = config_class.from_pretrained(
                model_name, cache_dir=model_path, num_labels=self.num_labels,
                finetuning_task=self.task_name)
            self.tokenizer =\
                tokenizer_class.from_pretrained(model_name,
                                                do_lower_case=self.do_lower_case,
                                                cache_dir=model_path)
            self.model = model_class.from_pretrained(model_name, from_tf=False,
                                                     config=self.config,
                                                     cache_dir=model_path)
        except Exception as e:
            # TODO: Add FileDownloadException for error classification
            raise FitException._with_error(AzureMLError.create(TextDnnModelDownloadFailed,
                                                               transformer='PretrainedTextDnn',
                                                               error_details=str(e),
                                                               reference_code=ReferenceCodes._TEXT_DNN_FIT_INITIALIZE,
                                                               target="PretrainedTextDNNTransformer"),
                                           inner_exception=e) from e

    def _generate_dataset(self, X, y):
        return featurize_dataset_in_memory(X, y, self.model_type,
                                           self.task_name,
                                           self.tokenizer,
                                           self.label_list,
                                           self.max_seq_length)

    def _patience_reached(self, accuracy_scores, patience, epsilon=0.0001):
        acc_len = len(accuracy_scores)
        if acc_len > patience and\
                accuracy_scores[-(patience + 1)] >=\
                (max(accuracy_scores[-patience:]) - epsilon):
            return True
        return False

    def _early_stopping_func(self, step, curr_epoch, steps_per_epoch,
                             val_dataset, y_valid, accuracy_scores,
                             best_accuracy_score, patience_has_reached,
                             model_filename, checkpoint_step_divider=5):
        periodic_score_checkpoint = (
            (step
                + 1) %
            math.ceil(
                steps_per_epoch
                / checkpoint_step_divider) == 0) or (
            (step
                + 1) %
            steps_per_epoch == 0)
        epochs_completed = curr_epoch + ((step + 1) / steps_per_epoch)
        if epochs_completed > self.min_train_epochs and\
                periodic_score_checkpoint:
            _logger.info("Epochs Completed = {}".format(epochs_completed))

            preds_val = self._evaluate(val_dataset,
                                       transform_type="prediction",
                                       early_stopping_mode=True)
            accuracy_scores.append(accuracy_score(y_valid, preds_val))

            if accuracy_scores[-1] > best_accuracy_score:
                best_accuracy_score = accuracy_scores[-1]
                if is_master_process():
                    torch.save(self.model.state_dict(), model_filename)

            if self._patience_reached(accuracy_scores, self.patience,
                                      self.epsilon):
                patience_has_reached = True

        return accuracy_scores, best_accuracy_score, patience_has_reached

    def _update_and_set_progress(self, global_step):
        """ Method for setting progress percentage and for logging progress up to max_progress_updates times."""

        # Calculate delta steps between ExperimentObserver updates
        # If num_total_steps is small and less than max_progress_updates, then the update
        # will be for every batch, or delta_steps_update = 1.
        delta_steps_update = max(1, int(self.num_total_steps / self.max_progress_updates))
        # set progress fraction to be logged.
        self.curr_progress = float(global_step + 1) / self.num_total_steps * 100  # percentage points

        # Ensure we have an observer, then update according
        # to self.delta_steps_update cadence or if its the last iteration.
        has_observer = not isinstance(self.observer, NullExperimentObserver)

        if has_observer and self.observer.run_instance is not None:
            # The final stage of 100% progress should be retained onscreen
            is_last_step = (global_step + 1) == self.num_total_steps
            carriage_return = False if is_last_step else True
            if global_step % delta_steps_update == 0 or is_last_step:
                self.observer.report_progress(ExperimentStatus.TextDNNTrainingProgress,
                                              self.curr_progress,
                                              carriage_return=carriage_return)

    def _train(self, train_dataset, val_dataset=None, y_valid=None):
        """ Train the model

        Replace args.blah references with self.blah references
        (cmd-line args are now instance attrs)

        """
        self.model.set_transform_type("probabilities")
        if self.per_gpu_train_batch_size is None:
            self.per_gpu_train_batch_size =\
                int(self.train_batch_size / max(1, self.n_gpu))

        self.train_batch_size =\
            self.per_gpu_train_batch_size * max(1, self.n_gpu)

        if self.horovod_distributed:
            train_sampler = DistributedSampler(train_dataset, num_replicas=hvd.size(), rank=hvd.rank())
        else:
            train_sampler = RandomSampler(train_dataset)

        train_dataloader = DataLoader(train_dataset, sampler=train_sampler,
                                      batch_size=self.train_batch_size)

        if self.max_steps > 0:
            t_total =\
                len(train_dataloader) // self.gradient_accumulation_steps *\
                self.num_train_epochs
            t_total = t_total // hvd.size() if self.horovod_distributed else t_total
            t_total = min(self.max_steps, t_total)
            self.num_train_epochs =\
                t_total\
                // (len(train_dataloader) // self.gradient_accumulation_steps)\
                + 1
        else:
            t_total =\
                len(train_dataloader) // self.gradient_accumulation_steps *\
                self.num_train_epochs

        steps_per_epoch = t_total / self.num_train_epochs

        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in self.model.named_parameters()
                        if not any(nd in n for nd in no_decay)],
                'weight_decay': self.weight_decay},
            {'params': [p for n, p in self.model.named_parameters()
                        if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0}
        ]

        optimizer = AdamW(optimizer_grouped_parameters, lr=self.learning_rate,
                          eps=self.adam_epsilon)

        if self.horovod_distributed:
            # Distribute the optimizer
            optimizer = self._distribute_optimizer(optimizer)
            hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)
            hvd.broadcast_optimizer_state(optimizer, root_rank=0)

        scheduler = WarmupLinearSchedule(optimizer,
                                         warmup_steps=self.warmup_steps,
                                         t_total=t_total)

        # floating point precision being used during training is 32 by default
        precision_in_use = 32
        if self.fp16:
            # if we interfere with fp16 defaults, this will need to change
            try:
                from apex import amp
                self.model, optimizer =\
                    amp.initialize(self.model, optimizer,
                                   opt_level=self.fp16_opt_level)
                _logger.info("Using mixed or 16-bit floating point precision")
                precision_in_use = 16
            except Exception:
                _logger.error("Something went wrong with using mixed\
                                   or 16-bit floating point precision.\
                                   Falling back to 32-bit. You may want to\
                                   refer to:\
                                   https://www.github.com/nvidia/apex")
        else:
            _logger.info("Using 32-bit floating point precision")

        # multi-gpu training (should be after apex fp16 initialization)
        if not self.horovod_distributed:
            self._to_device_parallel()  # preserve single-node, multi-gpu; useful for feature sweeping.

        # Train
        _logger.info("***** Running pretrained text dnn training *****")
        _logger.info("  Num examples = {}".format(len(train_dataset)))
        _logger.info("  Num Epochs = {}".format(self.num_train_epochs))
        _logger.info("  Instantaneous batch size per GPU = {}".format(
            self.per_gpu_train_batch_size))

        global_step = 0
        tr_loss = 0.0
        self.model.zero_grad()
        train_iterator = range(int(self.num_train_epochs))

        patience_has_reached = False
        if self.early_stopping:
            best_accuracy_score = 0.0
            accuracy_scores = []  # type: List[float]
            model_filename = "checkpoint.pth"

        start_time = time.time()

        # total number of steps is deterministic, will either complete loop or run for max steps
        self.num_total_steps = min(len(train_iterator) * len(train_dataloader), self.max_steps)
        for curr_epoch in train_iterator:
            for step, batch in enumerate(train_dataloader):
                self.model.train()
                # Monitor training progress as percentage completed from UI and standard out
                if is_master_process():
                    self._update_and_set_progress(global_step)

                batch = tuple(t.to(self.device) for t in batch)

                inputs = {'input_ids': batch[0],
                          'attention_mask': batch[1],
                          # XLM don't use segment_ids
                          'token_type_ids': batch[2] if self.model_type
                          in ['bert', 'xlnet'] else None,
                          'labels': batch[3]}

                outputs = self.model(**inputs)

                # model outputs are always tuple in pytorch-transformers
                loss = outputs[0]

                if self.n_gpu > 1:
                    # mean() to average on multi-gpu parallel training
                    loss = loss.mean()
                if self.gradient_accumulation_steps > 1:
                    loss = loss / self.gradient_accumulation_steps

                if self.fp16 and precision_in_use == 16:
                    with amp.scale_loss(loss, optimizer) as scaled_loss:
                        scaled_loss.backward()
                    torch.nn.utils.clip_grad_norm_(
                        amp.master_params(optimizer),
                        self.max_grad_norm
                    )
                else:
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(),
                                                   self.max_grad_norm)

                tr_loss += loss.item()
                if (step + 1) % self.gradient_accumulation_steps == 0:
                    scheduler.step()  # Update learning rate schedule
                    optimizer.step()
                    self.model.zero_grad()
                    global_step += 1

                if self.early_stopping:
                    accuracy_scores,
                    best_accuracy_score,
                    patience_has_reached =\
                        self._early_stopping_func(
                            step,
                            curr_epoch,
                            steps_per_epoch,
                            val_dataset,
                            y_valid,
                            accuracy_scores,
                            best_accuracy_score,
                            patience_has_reached,
                            model_filename)

                if patience_has_reached or\
                        (self.max_steps > 0 and global_step >= self.max_steps):
                    break
            if patience_has_reached or\
                    (self.max_steps > 0 and global_step >= self.max_steps):
                break
        # The purpose of doing this outside the loop is to ensure that
        # if early_stopping is enabled then we must make use of the
        # best model found, even if the patience criterion was never met
        if self.early_stopping and os.path.exists(model_filename):
            self.model.load_state_dict(torch.load(model_filename))
            os.remove(model_filename)

        # Collect the model from the DataParallel module, if using
        # multi-GPUs, else just use the self.model. Note: the function
        # hasattr() doesn't work with Python 2
        self.model = self.model.module\
            if hasattr(self.model, 'module') else self.model

        end_time = time.time()
        self.total_train_time = end_time - start_time
        _logger.info("Total pretrained text dnn train time = {}".format(self.total_train_time))

    def _evaluate(self, eval_dataset, transform_type="prediction",
                  early_stopping_mode=False):
        # Inference
        # TODO: remove gpu detect and to_device() logic for
        # inference and put it in __statestate__
        if not early_stopping_mode:
            self._gpu_detect()
            self._to_device()
            self.model.transform_type = transform_type
            # handle case with multi-GPU devices
            self._to_device_parallel()

        if self.per_gpu_eval_batch_size is None:
            self.per_gpu_eval_batch_size =\
                int(self.eval_batch_size / max(1, self.n_gpu))
        self.model.transform_type = transform_type
        self.eval_batch_size =\
            self.per_gpu_eval_batch_size * max(1, self.n_gpu)

        # Note that DistributedSampler samples randomly
        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(eval_dataset, sampler=eval_sampler,
                                     batch_size=self.eval_batch_size)

        # Eval
        nb_eval_steps = 0
        preds = None
        out_label_ids = None
        for batch in eval_dataloader:
            self.model.eval()
            batch = tuple(t.to(self.device) for t in batch)

            with torch.no_grad():
                inputs = {'input_ids': batch[0],
                          'attention_mask': batch[1],
                          # XLM don't use segment_ids
                          'token_type_ids': batch[2] if self.model_type in
                          ['bert', 'xlnet'] else None,
                          'labels': batch[3]}

                outputs = self.model(**inputs)
                _, clf_out = outputs[:2]

            nb_eval_steps += 1
            if preds is None:
                preds = clf_out.detach().cpu().numpy()
                out_label_ids = inputs['labels'].detach().cpu().numpy()
            else:
                preds = np.append(preds, clf_out.detach().cpu().numpy(),
                                  axis=0)
                out_label_ids =\
                    np.append(out_label_ids,
                              inputs['labels'].detach().cpu().numpy(),
                              axis=0)

        if self.task_name == "classification" and\
                transform_type != "embedding":
            preds = np.argmax(preds, axis=1)
            preds = self.label_list[preds]  # Index into class names.
        elif self.task_name == "regression" and\
                transform_type != "embedding":
            preds = np.squeeze(preds)

        # Collect the model from the DataParallel module, if using
        # multi-GPUs, else just use the self.model. Note: the function
        # hasattr() doesn't work with Python 2
        if not early_stopping_mode:
            self.model = self.model.module\
                if hasattr(self.model, 'module') else self.model

        return preds

    def _update_distributed(self):
        """
        Update whether or not this instance is being distributed across multiple processes.

        :return: None.
        """
        try:
            self.horovod_distributed = hvd.size() > 1
            self.max_steps = self.max_steps // hvd.size()
        except NameError:  # Horovod import failed
            self.horovod_distributed = False

    def _distribute_optimizer(self, optimizer):
        return hvd.DistributedOptimizer(optimizer, named_parameters=self.model.named_parameters(),
                                        compression=hvd.Compression.fp16, op=hvd.Adasum)


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For
            single sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second
            sequence. Only must be specified for sequence pair tasks.
            label: (Optional) string. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_id):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id


def featurize_dataset_in_memory(X, y, model_type, task_name, tokenizer,
                                label_list, max_seq_length):
    # Load data features from cache or dataset file
    if y is None:
        y = -1 * np.ones(len(X))

    examples = create_examples_in_memory(X, y)
    features =\
        convert_examples_to_features(
            examples, label_list, max_seq_length,
            tokenizer, task_name,
            # xlnet has a cls token at the end
            cls_token_at_end=bool(model_type in ['xlnet']),
            cls_token=tokenizer.cls_token,
            sep_token=tokenizer.sep_token,
            cls_token_segment_id=2 if model_type in ['xlnet'] else 1,
            # pad on the left for xlnet
            pad_on_left=bool(model_type in ['xlnet']),
            pad_token_segment_id=4 if model_type in ['xlnet'] else 0)

    # Convert to Tensors and build dataset
    all_input_ids = torch.tensor([f.input_ids for f in features],
                                 dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in features],
                                  dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in features],
                                   dtype=torch.long)
    if task_name == "classification":
        all_label_ids = torch.tensor([f.label_id for f in features],
                                     dtype=torch.long)
    elif task_name == "regression":
        all_label_ids = torch.tensor([f.label_id for f in features],
                                     dtype=torch.float)

    dataset = TensorDataset(all_input_ids, all_input_mask,
                            all_segment_ids, all_label_ids)
    return dataset


def create_examples_in_memory(X, y):
    """Creates examples for the training and dev sets given X, y in memory."""
    examples = []
    for (i, line) in enumerate(zip(X, y)):
        guid = "%s" % (i)
        text_a = line[0]
        label = line[1]
        examples.append(
            InputExample(guid=guid, text_a=text_a, text_b=None, label=label))
    return examples


def convert_examples_to_features(examples, label_list, max_seq_length,
                                 tokenizer, task_name,
                                 cls_token_at_end=False, pad_on_left=False,
                                 cls_token='[CLS]', sep_token='[SEP]',
                                 pad_token=0, sequence_a_segment_id=0,
                                 sequence_b_segment_id=1,
                                 cls_token_segment_id=1,
                                 pad_token_segment_id=0,
                                 mask_padding_with_zero=True):
    """ Loads a data file into a list of `InputBatch`s
        `cls_token_at_end` define the location of the CLS token:
            - False (Default, BERT/XLM pattern): [CLS] + A + [SEP] + B + [SEP]
            - True (XLNet/GPT pattern): A + [SEP] + B + [SEP] + [CLS]
        `cls_token_segment_id` define the segment id associated to the CLS
        token (0 for BERT, 2 for XLNet)
    """

    label_map = {label: i for i, label in enumerate(label_list)}

    features = []
    for (ex_index, example) in enumerate(examples):
        tokens_a = tokenizer.tokenize(example.text_a)

        tokens_b = None
        if example.text_b:
            tokens_b = tokenizer.tokenize(example.text_b)
            # Modifies `tokens_a` and `tokens_b` in place so that the total
            # length is less than the specified length.
            # Account for [CLS], [SEP], [SEP] with "- 3"
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[:(max_seq_length - 2)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        # tokens: [CLS] is this jack ##son ##ville ? [SEP] no it is not.[SEP]
        # type_ids: 0   0  0    0    0     0       0   0   1  1  1  1  1   1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids:   0   0   0   0  0     0   0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0`
        # and `type=1` were learned during pre-training and are added to the
        # wordpiece embedding vector (and position vector). This is not
        # *strictly* necessary since the [SEP] token unambiguously separates
        #  the sequences, but it makes it easier for the model to learn the
        # concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS])
        # is used as as the "sentence vector". Note that this only makes
        # sense because the entire model is fine-tuned.
        tokens = tokens_a + [sep_token]
        segment_ids = [sequence_a_segment_id] * len(tokens)

        if tokens_b:
            tokens += tokens_b + [sep_token]
            segment_ids += [sequence_b_segment_id] * (len(tokens_b) + 1)

        if cls_token_at_end:
            tokens = tokens + [cls_token]
            segment_ids = segment_ids + [cls_token_segment_id]
        else:
            tokens = [cls_token] + tokens
            segment_ids = [cls_token_segment_id] + segment_ids

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        if pad_on_left:
            input_ids = ([pad_token] * padding_length) + input_ids
            input_mask = ([0 if mask_padding_with_zero else 1]
                          * padding_length) + input_mask
            segment_ids = ([pad_token_segment_id] * padding_length) +\
                segment_ids
        else:
            input_ids = input_ids + ([pad_token] * padding_length)
            input_mask = input_mask + ([0 if mask_padding_with_zero else 1]
                                       * padding_length)
            segment_ids = segment_ids + ([pad_token_segment_id]
                                         * padding_length)

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        if task_name == "classification":
            label_id = label_map.get(example.label, -1)
        # TODO: check to see type of label (int/float) for regression
        elif task_name == "regression":
            label_id = int(example.label)
        else:
            raise PretrainedTextDnnTransformerConvertUnsupportedTaskException(
                "the task '{}' is not supported".format(task_name),
                reference_code=ReferenceCodes._TEXT_DNN_CONVERT,
                has_pii=False)

        features.append(
            InputFeatures(input_ids=input_ids,
                          input_mask=input_mask,
                          segment_ids=segment_ids,
                          label_id=label_id))
    return features


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer
    # sequence one token at a time (end tokens first). This makes more
    #  sense than truncating an equal percent of tokens from each,
    # since if one sequence is very short then each token that's truncated
    # likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()
