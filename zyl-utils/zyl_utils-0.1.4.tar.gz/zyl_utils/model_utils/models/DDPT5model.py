# encoding: utf-8
'''
@author: zyl
@file: my_DDPT5model.py
@time: 2021/11/11 11:00
@desc:
'''
import logging
import math
import os
import random
from dataclasses import asdict

import pandas as pd
import torch
import torch.multiprocessing as mp
import torch.nn.functional as F
from simpletransformers.t5.t5_model import T5Model
from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from tqdm.auto import tqdm, trange
from transformers.optimization import AdamW, Adafactor
from transformers.optimization import (
    get_constant_schedule,
    get_constant_schedule_with_warmup,
    get_linear_schedule_with_warmup,
    get_cosine_schedule_with_warmup,
    get_cosine_with_hard_restarts_schedule_with_warmup,
    get_polynomial_decay_schedule_with_warmup,
)

try:
    import wandb

    wandb_available = True
except ImportError:
    wandb_available = False

logger = logging.getLogger(__name__)


class DDPT5Model(T5Model):
    """The DDP version of T5Model"""

    def __init__(
            self,
            model_type,
            model_name,
            args=None,
            tokenizer=None,
            use_cuda=True,
            cuda_device=-1,
            **kwargs,
    ):

        """
        Initializes a DDP T5Model model. Turn off multi-processing settings.

        Args:
            model_type: The type of model (t5, mt5)
            model_name: The exact architecture and trained weights to use. This may be a Hugging Face Transformers compatible pre-trained model, a community model, or the path to a directory containing model files.
            args (optional): Default args will be used if this parameter is not provided. If provided, it should be a dict containing the args that should be changed in the default args.
            use_cuda (optional): Use GPU if available. Setting to False will force model to use CPU only.
            cuda_device (optional): Specific GPU that should be used. Will use the first available GPU by default.
            **kwargs (optional): For providing proxies, force_download, resume_download, cache_dir and other options specific to the 'from_pretrained' implementation where this will be supplied.
        """  # noqa: ignore flake8"
        super().__init__(model_type, model_name, args, tokenizer, use_cuda, cuda_device, **kwargs)
        self.args.use_multiprocessing = False
        self.args.use_multiprocessing_for_evaluation = False
        if self.args.n_gpu == 1:
            raise ValueError("You are using DDP with single GPU.")

    def train_model(
            self,
            train_data,
            output_dir=None,
            show_running_loss=True,
            args=None,
            eval_data=None,
            verbose=True,
            **kwargs,
    ):
        """
        Trains the model using 'train_data'

        Args:
            train_data: Pandas DataFrame containing the 3 columns - `prefix`, `input_text`, `target_text`.
                        - `prefix`: A string indicating the task to perform. (E.g. `"question"`, `"stsb"`)
                        - `input_text`: The input text sequence. `prefix` is automatically prepended to form the full input. (<prefix>: <input_text>)
                        - `target_text`: The target sequence
            output_dir: The directory where model files will be saved. If not given, self.args.output_dir will be used.
            show_running_loss (optional): Set to False to prevent running loss from being printed to console. Defaults to True.
            args (optional): Optional changes to the args dict of the model. Any changes made will persist for the model.
            eval_data (optional): A DataFrame against which evaluation will be performed when evaluate_during_training is enabled. Is required if evaluate_during_training is enabled.
            verbose (optional): whether output staff.
            **kwargs: Additional metrics that should be used. Pass in the metrics as keyword arguments (name of metric: function to use).
                        A metric function should take in two parameters. The first parameter will be the true labels, and the second parameter will be the predictions. Both inputs
                        will be lists of strings. Note that this will slow down training significantly as the predicted sequences need to be generated.

        Returns: 
        """  # noqa: ignore flake8"

        if args:
            self.args.update_from_dict(args)

        if self.args.evaluate_during_training and eval_data is None:
            raise ValueError(
                "evaluate_during_training is enabled but eval_data is not specified."
                " Pass eval_data to model.train_model() if using evaluate_during_training."
            )

        if not output_dir:
            output_dir = self.args.output_dir

        if os.path.exists(output_dir) and os.listdir(output_dir) and not self.args.overwrite_output_dir:
            raise ValueError(
                "Output directory ({}) already exists and is not empty."
                " Set args.overwrite_output_dir = True to overcome.".format(output_dir)
            )

        train_dataset = self.load_and_cache_examples(train_data, verbose=verbose)

        os.makedirs(output_dir, exist_ok=True)

        os.environ['MASTER_ADDR'] = 'localhost'
        port = random.randint(10000, 20000)
        os.environ['MASTER_PORT'] = str(port)
        mp.spawn(self.train_each_proc, nprocs=self.args.n_gpu,
                 args=(train_dataset, output_dir,
                       show_running_loss, eval_data, verbose, kwargs))

        # self.save_model(model=self.model)

        if verbose:
            logger.info(" Training of {} model complete. Saved to {}.".format(self.args.model_name, output_dir))

    def train_each_proc(self, process_index, train_dataset, *train_args):
        """
        A wrapper function of train() for each process of DDP.
        :param process_index: param train_dataset passed into train().
        :param train_dataset: The training set.
        :param train_args: other position arguments passed to train().
        :return: The same as train().
        """
        self._local_rank = process_index
        self._world_size = self.args.n_gpu
        self.train(train_dataset, *train_args[:-1], **train_args[-1])

    def train(
            self, train_dataset, output_dir, show_running_loss=True, eval_data=None, verbose=True, **kwargs,
    ):
        """
        Trains the model on train_dataset.

        Utility function to be used by the train_model() method. Not intended to be used directly.
        """

        args = self.args
        self.device = torch.device(f"cuda:{self._local_rank}")
        self._move_model_to_device()
        torch.distributed.init_process_group(
            backend='nccl',
            init_method='env://',
            world_size=self._world_size,
            rank=self._local_rank
        )
        self.model = torch.nn.parallel.DistributedDataParallel(self.model, device_ids=[self._local_rank])
        model = self.model

        if self._local_rank == 0:
            tb_writer = SummaryWriter(logdir=args.tensorboard_dir)
        train_sampler = DistributedSampler(
            train_dataset,
            num_replicas=self._world_size,
            rank=self._local_rank
        )
        train_dataloader = DataLoader(
            train_dataset,
            sampler=train_sampler,
            batch_size=args.train_batch_size // self._world_size,
            pin_memory=True
        )

        if args.max_steps > 0:
            t_total = args.max_steps
            args.num_train_epochs = args.max_steps // (len(train_dataloader) // args.gradient_accumulation_steps) + 1
        else:
            t_total = len(train_dataloader) // args.gradient_accumulation_steps * args.num_train_epochs

        no_decay = ["bias", "LayerNorm.weight"]

        optimizer_grouped_parameters = []
        custom_parameter_names = set()
        for group in self.args.custom_parameter_groups:
            params = group.pop("params")
            custom_parameter_names.update(params)
            param_group = {**group}
            param_group["params"] = [p for n, p in model.named_parameters() if n in params]
            optimizer_grouped_parameters.append(param_group)

        for group in self.args.custom_layer_parameters:
            layer_number = group.pop("layer")
            layer = f"layer.{layer_number}."
            group_d = {**group}
            group_nd = {**group}
            group_nd["weight_decay"] = 0.0
            params_d = []
            params_nd = []
            for n, p in model.named_parameters():
                if n not in custom_parameter_names and layer in n:
                    if any(nd in n for nd in no_decay):
                        params_nd.append(p)
                    else:
                        params_d.append(p)
                    custom_parameter_names.add(n)
            group_d["params"] = params_d
            group_nd["params"] = params_nd

            optimizer_grouped_parameters.append(group_d)
            optimizer_grouped_parameters.append(group_nd)

        if not self.args.train_custom_parameters_only:
            optimizer_grouped_parameters.extend(
                [
                    {
                        "params": [
                            p
                            for n, p in model.named_parameters()
                            if n not in custom_parameter_names and not any(nd in n for nd in no_decay)
                        ],
                        "weight_decay": args.weight_decay,
                    },
                    {
                        "params": [
                            p
                            for n, p in model.named_parameters()
                            if n not in custom_parameter_names and any(nd in n for nd in no_decay)
                        ],
                        "weight_decay": 0.0,
                    },
                ]
            )

        warmup_steps = math.ceil(t_total * args.warmup_ratio)
        args.warmup_steps = warmup_steps if args.warmup_steps == 0 else args.warmup_steps

        if 0 < args.save_after < 1:
            args.save_after = math.ceil(t_total * args.save_after)

        if args.optimizer == "AdamW":
            optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
        elif args.optimizer == "Adafactor":
            optimizer = Adafactor(
                optimizer_grouped_parameters,
                lr=args.learning_rate,
                eps=args.adafactor_eps,
                clip_threshold=args.adafactor_clip_threshold,
                decay_rate=args.adafactor_decay_rate,
                beta1=args.adafactor_beta1,
                weight_decay=args.weight_decay,
                scale_parameter=args.adafactor_scale_parameter,
                relative_step=args.adafactor_relative_step,
                warmup_init=args.adafactor_warmup_init,
            )
            if self._local_rank == 0:
                print("Using Adafactor for T5")
        else:
            raise ValueError(
                "{} is not a valid optimizer class. Please use one of ('AdamW', 'Adafactor') instead.".format(
                    args.optimizer
                )
            )

        if args.scheduler == "constant_schedule":
            scheduler = get_constant_schedule(optimizer)

        elif args.scheduler == "constant_schedule_with_warmup":
            scheduler = get_constant_schedule_with_warmup(optimizer, num_warmup_steps=args.warmup_steps)

        elif args.scheduler == "linear_schedule_with_warmup":
            scheduler = get_linear_schedule_with_warmup(
                optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=t_total
            )

        elif args.scheduler == "cosine_schedule_with_warmup":
            scheduler = get_cosine_schedule_with_warmup(
                optimizer,
                num_warmup_steps=args.warmup_steps,
                num_training_steps=t_total,
                num_cycles=args.cosine_schedule_num_cycles,
            )

        elif args.scheduler == "cosine_with_hard_restarts_schedule_with_warmup":
            scheduler = get_cosine_with_hard_restarts_schedule_with_warmup(
                optimizer,
                num_warmup_steps=args.warmup_steps,
                num_training_steps=t_total,
                num_cycles=args.cosine_schedule_num_cycles,
            )

        elif args.scheduler == "polynomial_decay_schedule_with_warmup":
            scheduler = get_polynomial_decay_schedule_with_warmup(
                optimizer,
                num_warmup_steps=args.warmup_steps,
                num_training_steps=t_total,
                lr_end=args.polynomial_decay_schedule_lr_end,
                power=args.polynomial_decay_schedule_power,
            )

        else:
            raise ValueError("{} is not a valid scheduler.".format(args.scheduler))

        if (
                args.model_name
                and os.path.isfile(os.path.join(args.model_name, "optimizer.pt"))
                and os.path.isfile(os.path.join(args.model_name, "scheduler.pt"))
        ):
            # Load in optimizer and scheduler states
            optimizer.load_state_dict(torch.load(os.path.join(args.model_name, "optimizer.pt")))
            scheduler.load_state_dict(torch.load(os.path.join(args.model_name, "scheduler.pt")))

        if self._local_rank == 0:
            logger.info(" Training started")

        global_step = 0
        training_progress_scores = None
        tr_loss, logging_loss = 0.0, 0.0
        model.zero_grad()
        train_iterator = trange(int(args.num_train_epochs), desc="Epoch",
                                disable=args.silent or self._local_rank != 0, mininterval=0)
        epoch_number = 0
        best_eval_metric = None
        current_loss = None
        early_stopping_counter = 0
        steps_trained_in_current_epoch = 0
        epochs_trained = 0
        stop_training = False

        if args.model_name and os.path.exists(args.model_name):
            try:
                # set global_step to global_step of last saved checkpoint from model path
                checkpoint_suffix = args.model_name.split("/")[-1].split("-")
                if len(checkpoint_suffix) > 2:
                    checkpoint_suffix = checkpoint_suffix[1]
                else:
                    checkpoint_suffix = checkpoint_suffix[-1]
                global_step = int(checkpoint_suffix)
                epochs_trained = global_step // (len(train_dataloader) // args.gradient_accumulation_steps)
                steps_trained_in_current_epoch = global_step % (
                        len(train_dataloader) // args.gradient_accumulation_steps
                )

                logger.info("   Continuing training from checkpoint, will skip to saved global_step")
                logger.info("   Continuing training from epoch %d", epochs_trained)
                logger.info("   Continuing training from global step %d", global_step)
                logger.info("   Will skip the first %d steps in the current epoch", steps_trained_in_current_epoch)
            except ValueError:
                logger.info("   Starting fine-tuning.")

        if args.evaluate_during_training:
            training_progress_scores = self._create_training_progress_scores(**kwargs)

        if args.wandb_project and self._local_rank == 0:
            wandb.init(project=args.wandb_project, config={**asdict(args)}, **args.wandb_kwargs)
            wandb.watch(self.model)

        if args.fp16:
            from torch.cuda import amp

            scaler = amp.GradScaler()

        for epoch in train_iterator:
            model.train()
            train_sampler.set_epoch(epoch)
            if epochs_trained > 0:
                epochs_trained -= 1
                continue
            if self._local_rank == 0:
                train_iterator.set_description(f"Epoch {epoch_number + 1} of {args.num_train_epochs}")
            batch_iterator = tqdm(
                train_dataloader,
                desc=f"Running Epoch {epoch_number} of {args.num_train_epochs} on process {self._local_rank}",
                disable=args.silent or self._local_rank != 0,
                mininterval=0,
            )
            for step, batch in enumerate(batch_iterator):
                if steps_trained_in_current_epoch > 0:
                    steps_trained_in_current_epoch -= 1
                    continue

                inputs = self._get_inputs_dict(batch)
                if args.fp16:
                    with amp.autocast():
                        loss = self.compute_loss(model, args, inputs)
                else:
                    loss = self.compute_loss(model, args, inputs)

                loss_ = loss.clone()
                torch.distributed.barrier()
                torch.distributed.reduce(loss_, 0)
                current_loss = loss_.item() / self._world_size

                if show_running_loss and self._local_rank == 0:
                    batch_iterator.set_description(
                        f"Epochs {epoch_number}/{args.num_train_epochs}. Running Loss: {current_loss:9.4f}"
                    )

                if args.gradient_accumulation_steps > 1:
                    loss = loss / args.gradient_accumulation_steps

                if args.fp16:
                    scaler.scale(loss).backward()
                else:
                    loss.backward()

                tr_loss += loss.item()
                if (step + 1) % args.gradient_accumulation_steps == 0:
                    if args.fp16:
                        scaler.unscale_(optimizer)
                    if args.optimizer == "AdamW":
                        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

                    if args.fp16:
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        optimizer.step()
                    scheduler.step()  # Update learning rate schedule
                    model.zero_grad()
                    global_step += 1

                    if args.logging_steps > 0 and global_step % args.logging_steps == 0 and self._local_rank == 0:
                        # Log metrics
                        tb_writer.add_scalar("lr", scheduler.get_last_lr()[0], global_step)
                        tb_writer.add_scalar("loss", (tr_loss - logging_loss) / args.logging_steps, global_step)
                        logging_loss = tr_loss
                        if args.wandb_project or self.is_sweeping:
                            wandb.log(
                                {
                                    "Training loss": current_loss,
                                    "lr": scheduler.get_last_lr()[0]
                                },
                                step=global_step
                            )

                    if args.save_steps > 0 and global_step % args.save_steps == 0 and self._local_rank == 0:
                        # Save model checkpoint
                        output_dir_current = os.path.join(output_dir, "checkpoint-{}".format(global_step))

                        self.save_model(output_dir_current, optimizer, scheduler, model=model)

                    if args.evaluate_during_training and (
                            args.evaluate_during_training_steps > 0
                            and global_step % args.evaluate_during_training_steps == 0
                    ):
                        results = self.eval_model(
                            eval_data,
                            verbose=verbose and args.evaluate_during_training_verbose,
                            silent=args.evaluate_during_training_silent or self._local_rank != 0,
                            **kwargs,
                        )

                        if self._local_rank == 0:
                            for key, value in results.items():
                                tb_writer.add_scalar("eval_{}".format(key), value, global_step)

                            output_dir_current = os.path.join(output_dir, "checkpoint-{}".format(global_step))

                            if args.save_eval_checkpoints:
                                self.save_model(output_dir_current, optimizer, scheduler, model=model, results=results)

                            stop_training, best_eval_metric, early_stopping_counter = self.logging_and_saving(
                                args,
                                results,
                                global_step,
                                train_iterator,
                                optimizer,
                                scheduler,
                                model,
                                training_progress_scores,
                                current_loss,
                                best_eval_metric,
                                verbose,
                                early_stopping_counter)

                        torch.distributed.barrier()
                        stop_training_tensor = torch.tensor([stop_training], device=self.device)
                        torch.distributed.broadcast(stop_training_tensor, src=0)
                        stop_training = bool(stop_training_tensor.cpu()[0])
                        if stop_training:
                            break

                        model.train()

            if stop_training:
                break
            epoch_number += 1
            output_dir_current = os.path.join(output_dir, "checkpoint-{}-epoch-{}".format(global_step, epoch_number))

            if (args.save_model_every_epoch or args.evaluate_during_training) and self._local_rank == 0:
                os.makedirs(output_dir_current, exist_ok=True)

            if args.save_model_every_epoch and self._local_rank == 0:
                self.save_model(output_dir_current, optimizer, scheduler, model=model)

            if args.evaluate_during_training and args.evaluate_each_epoch:
                results = self.eval_model(
                    eval_data,
                    verbose=verbose and args.evaluate_during_training_verbose,
                    silent=args.evaluate_during_training_silent or self._local_rank != 0,
                    **kwargs,
                )

                if self._local_rank == 0:
                    if args.save_eval_checkpoints:
                        self.save_model(output_dir_current, optimizer, scheduler, results=results)

                    stop_training, best_eval_metric, early_stopping_counter = self.logging_and_saving(
                        args,
                        results,
                        global_step,
                        train_iterator,
                        optimizer,
                        scheduler,
                        model,
                        training_progress_scores,
                        current_loss,
                        best_eval_metric,
                        verbose,
                        early_stopping_counter)

                torch.distributed.barrier()
                stop_training_tensor = torch.tensor([stop_training], device=self.device)
                torch.distributed.broadcast(stop_training_tensor, src=0)
                stop_training = bool(stop_training_tensor.cpu()[0])
                if stop_training:
                    break

        # close tensorboard writer to avoid EOFError.
        if self._local_rank == 0:
            tb_writer.close()
            wandb.finish()

    def eval_model(
            self, eval_data, output_dir=None, verbose=True, silent=False, **kwargs
    ):
        """
        Evaluates the model on eval_data. Saves results to output_dir.
        Args:
            eval_data: Pandas DataFrame containing the 3 columns - `prefix`, `input_text`, `target_text`.
                        - `prefix`: A string indicating the task to perform. (E.g. `"question"`, `"stsb"`)
                        - `input_text`: The input text sequence. `prefix` is automatically prepended to form the full input. (<prefix>: <input_text>)
                        - `target_text`: The target sequence
            output_dir: The directory where model files will be saved. If not given, self.args.output_dir will be used.
            verbose: If verbose, results will be printed to the console on completion of evaluation.
            silent: If silent, tqdm progress bars will be hidden.
            **kwargs: Additional metrics that should be used. Pass in the metrics as keyword arguments (name of metric: function to use).
                        A metric function should take in two parameters. The first parameter will be the true labels, and the second parameter will be the predictions. Both inputs
                        will be lists of strings. Note that this will slow down evaluation significantly as the predicted sequences need to be generated.
        Returns:
            results: Dictionary containing evaluation results.
        """  # noqa: ignore flake8"

        if not output_dir:
            output_dir = self.args.output_dir

        eval_dataset = self.load_and_cache_examples(
            eval_data, evaluate=True, verbose=verbose, silent=silent
        )
        os.makedirs(output_dir, exist_ok=True)

        result = self.evaluate(
            eval_dataset, output_dir, verbose=verbose, silent=silent, **kwargs
        )
        self.results.update(result)

        if self.args.evaluate_generated_text:
            if self.args.preprocess_inputs:
                to_predict = [
                    prefix + ": " + input_text
                    for prefix, input_text in zip(
                        eval_data["prefix"], eval_data["input_text"]
                    )
                ]
            else:
                to_predict = [
                    prefix + input_text
                    for prefix, input_text in zip(
                        eval_data["prefix"], eval_data["input_text"]
                    )
                ]
            preds = self.predict(to_predict)

            result = self.compute_metrics(
                eval_data["target_text"].tolist(), preds, **kwargs
            )
            self.results.update(result)

        if verbose:
            logger.info(self.results)

        return self.results

    def evaluate(self, eval_dataset, output_dir, verbose=True, silent=False, **kwargs):
        """
        Evaluates the model on eval_dataset.
        Utility function to be used by the eval_model() method. Not intended to be used directly.
        """

        model = self.model
        args = self.args
        eval_output_dir = output_dir

        results = {}
        eval_sampler = DistributedSampler(
            eval_dataset,
            num_replicas=self._world_size,
            rank=self._local_rank
        )
        eval_dataloader = DataLoader(
            eval_dataset,
            sampler=eval_sampler,
            batch_size=args.eval_batch_size // self._world_size,
            pin_memory=True
        )

        eval_loss = 0.0
        nb_eval_steps = 0
        model.eval()

        if self.args.fp16:
            from torch.cuda import amp

        for batch in tqdm(
                eval_dataloader,
                disable=args.silent or silent,
                desc="Running Evaluation"
        ):
            inputs = self._get_inputs_dict(batch)
            with torch.no_grad():
                if self.args.fp16:
                    with amp.autocast():
                        outputs = model(**inputs)
                        loss = outputs[0]
                else:
                    outputs = model(**inputs)
                    loss = outputs[0]
                torch.distributed.barrier()
                torch.distributed.reduce(loss, 0)
                eval_loss += loss.item()
            nb_eval_steps += 1

        eval_loss = eval_loss / nb_eval_steps / self._world_size

        if self._local_rank == 0:
            print(eval_loss)

        results["eval_loss"] = eval_loss

        if self._local_rank == 0:
            output_eval_file = os.path.join(eval_output_dir, "eval_results.txt")
            with open(output_eval_file, "w") as writer:
                for key in sorted(results.keys()):
                    writer.write("{} = {}\n".format(key, str(results[key])))

        return results

    def logging_and_saving(
            self,
            args,
            results,
            global_step,
            train_iterator,
            optimizer,
            scheduler,
            model,
            training_progress_scores,
            current_loss,
            best_eval_metric,
            verbose,
            early_stopping_counter):
        training_progress_scores["global_step"].append(global_step)
        training_progress_scores["train_loss"].append(current_loss)
        for key in results:
            training_progress_scores[key].append(results[key])
        report = pd.DataFrame(training_progress_scores)
        report.to_csv(
            os.path.join(args.output_dir, "training_progress_scores.csv"), index=False,
        )

        if args.wandb_project or self.is_sweeping:
            wandb.log(self._get_last_metrics(training_progress_scores), step=global_step)

        stop_training = False
        if global_step > args.save_after:
            if not best_eval_metric:
                best_eval_metric = results[args.early_stopping_metric]
                self.save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)

            if args.early_stopping_metric_minimize:
                if results[args.early_stopping_metric] - best_eval_metric < args.early_stopping_delta:
                    best_eval_metric = results[args.early_stopping_metric]
                    self.save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)
                    early_stopping_counter = 0
                else:
                    stop_training, early_stopping_counter = \
                        self.check_early_stopping(early_stopping_counter, args, train_iterator, verbose)
            else:
                if results[args.early_stopping_metric] - best_eval_metric > args.early_stopping_delta:
                    best_eval_metric = results[args.early_stopping_metric]
                    self.save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)
                    early_stopping_counter = 0
                else:
                    stop_training, early_stopping_counter = \
                        self.check_early_stopping(early_stopping_counter, args, train_iterator, verbose)

        return stop_training, best_eval_metric, early_stopping_counter

    def check_early_stopping(self, early_stopping_counter, args, train_iterator, verbose):
        stop_training = False
        if args.use_early_stopping:
            if early_stopping_counter < args.early_stopping_patience:
                early_stopping_counter += 1
                if verbose:
                    logger.info(f" No improvement in {args.early_stopping_metric}")
                    logger.info(f" Current step: {early_stopping_counter}")
                    logger.info(f" Early stopping patience: {args.early_stopping_patience}")
            else:
                if verbose:
                    logger.info(f" Patience of {args.early_stopping_patience} steps reached")
                    logger.info(" Training terminated.")
                    train_iterator.close()
                stop_training = True
        return stop_training, early_stopping_counter

    def compute_loss(self, model, args, inputs):
        outputs = model(**inputs)
        if args.r_drop:
            outputs_ = model(**inputs)
            loss = self.compute_r_drop_loss(
                outputs['loss'],
                outputs_['loss'],
                outputs['logits'],
                outputs_['logits'],
                inputs['attention_mask'],
                args.r_drop_alpha
            )
        else:
            loss = outputs[0]
        return loss

    def compute_kl_loss(self, p, q, pad_mask=None, reduction='mean'):

        p_loss = F.kl_div(F.log_softmax(p, dim=-1), F.softmax(q, dim=-1), reduction='none')
        q_loss = F.kl_div(F.log_softmax(q, dim=-1), F.softmax(p, dim=-1), reduction='none')

        if pad_mask is not None:
            p_loss.masked_fill_(pad_mask.to(bool).unsqueeze(-1), 0.)
            q_loss.masked_fill_(pad_mask.to(bool).unsqueeze(-1), 0.)

        if reduction == 'mean':
            p_loss = p_loss.mean()
            q_loss = q_loss.mean()
        elif reduction == 'sum':
            p_loss = p_loss.sum()
            q_loss = q_loss.sum()
        else:
            raise ValueError('Only mean or sum reduction is supported in computing KL Divergence!')

        loss = (p_loss + q_loss) / 2
        return loss

    def compute_r_drop_loss(self, ce1, ce2, logit1, logit2, attention_mask, alpha, reduction='mean'):
        kl_loss = self.compute_kl_loss(logit1, logit2, attention_mask, reduction=reduction)
        ce_loss = 0.5 * (ce1 + ce2)
        return ce_loss + alpha * kl_loss
