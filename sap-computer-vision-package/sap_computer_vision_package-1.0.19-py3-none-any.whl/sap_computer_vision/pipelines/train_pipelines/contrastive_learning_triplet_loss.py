import pathlib
import json
import zipfile
import os
import logging
from functools import lru_cache
from collections.abc import Iterable

import numpy as np

from metaflow import FlowSpec, step, argo, argo_base, Parameter, JSONType

from detectron2.config import CfgNode
from detectron2.data import MetadataCatalog
import torch

from sap_computer_vision.datasets import image_folder as imgf
import sap_computer_vision.datasets.utils as utils
from sap_computer_vision import get_cfg, get_config_file, setup_loggers
from sap_computer_vision.evaluators.contrastive import ContrastiveEvaluator, get_metrics
from sap_computer_vision.engine import TripletDistanceTrainer


MODEL_OUTPUT_DIR = pathlib.Path('/tmp/model')
DATA_INPUT_DIR = pathlib.Path('/workdir/datain')


class Trainer(TripletDistanceTrainer):
    @classmethod
    def build_evaluator(cls, cfg, dataset_name):
        if cfg.TEST.EVAL_PERIOD <= 0:
            raise NotImplementedError
        else:
            return ContrastiveEvaluator(cfg)  # pylint: disable=E1124,E1125


@argo_base(
    labels={'scenarios.ai.sap.com/id': 'scenario-id',
            'ai.sap.com/version': 'scenario-version'},
    annotations={'scenarios.ai.sap.com/name': 'scenario-name',
                 'executables.ai.sap.com/name': 'executable-name',
                 'artifacts.ai.sap.com/datain.kind': 'dataset',
                 'artifacts.ai.sap.com/trainedmodel.kind': 'model'},
    image='mlf.docker.repositories.sapcdn.io/com.sap.ai/sap_cv_metaflow:0.0.25',
    imagePullSecrets=[{'name': 'your-image-pull-secret'}],
    envFrom=[{'secretRef': {'name': 'default-object-store-secret'}}],
    volumes=[{'name': 'dshm', 'emptyDir': {'medium': 'Memory'}}])
class TripletDistanceMetricTrain(FlowSpec):
    """Pipeline to train a model for object detection.
    """
    model_name = Parameter("modelname",
                           help="Name of the model config.",
                           default="TripletDistanceLearner/FPN-Resnet50")
    train_input = Parameter("train",
                         help=f"Name of the file or folder within {DATA_INPUT_DIR} containing filenames of the train dataset. If {DATA_INPUT_DIR} " + \
                               "contain an \'images\' and \'annotations\' folder it can also be a float. This float is the ratio of images included in the train dataset",
                         default='train.txt')
    validation_input = Parameter("validation",
                         help=f"Name of the file or folder within {DATA_INPUT_DIR} containing filenames of the validation dataset. If {DATA_INPUT_DIR} " + \
                               "contain an \'images\' and \'annotations\' folder it can also be a float. This float is the ratio of images included in the train dataset. " + \
                               "For this to work \'train\' has to be a float as well.",
                       default="val.txt")
    test_input = Parameter("test",
                         help=f"Name of the file or folder within {DATA_INPUT_DIR} containing filenames of the test dataset. If {DATA_INPUT_DIR} " + \
                               "contain an \'images\' and \'annotations\' folder it can also be a float. This float is the ratio of images included in the train dataset." ,
                        default="test.txt")
    index_input = Parameter("index",
                         help=f"Name of the file or folder within {DATA_INPUT_DIR} containing filenames of the test dataset. If {DATA_INPUT_DIR} " + \
                               "contain an \'images\' and \'annotations\' folder it can also be a float. This float is the ratio of images included in the train dataset." ,
                        default="index.txt")
    sampler = Parameter("sampler",
                        help="Sampler used to create the triplets.",
                        default="PKSampler")
    loss = Parameter("loss",
                     help="Sampler used to create the triplets.",
                     default="MARGIN_LOSS")
    margin = Parameter("margin",
                       help="Sampler used to create the triplets.",
                       default="0.5")
    embedding_dim = Parameter("embeddingdim",
                               help="Sampler used to create the triplets.",
                               default="512")
    intermediate_layers = Parameter("projection_layers",
                         help="Json encoded list of class names of expected images types",
                         type=JSONType,
                         default='[]')
    lr_decay = Parameter("lrdecay",
                         help="Whether learning rate should be decreased over the training.",
                         type=JSONType,
                         default=json.dumps(True))
    early_stopping = Parameter("earlystopping",
                               help="Whether early stopping should be active.",
                               default=False)
    additional_augmentations = Parameter("additionalaugs",
                                         help="Enables cropping, random saturation, random lightning, ranodm brightness and random contrast as additional augmentations.",
                                         default=True)
    batch_size = Parameter("batchsize",
                           help="",
                           default=8)
    p_classes_per_batch = Parameter("pclasses",
                                  help="",
                                  default=8)
    k_examples_per_class = Parameter("kexamples",
                                     help="",
                                     default=8)
    n_steps = Parameter("ntrainsteps",
                        help="Number of training steps.",
                        default=3000)
    eval_freq = Parameter("evalfreq",
                          help="Frequency of evaluation. If > 1 it is treated as every \'evalfreq\' steps. If < 1 an evaluation in done every \'evalfreq\'×\'ntrainsteps\' steps",
                          default="0.1")
    base_lr = Parameter("baselr",
                        help="Base learning rate.",
                        default=0.00025)
    seed = Parameter("seed",
                     help="Random seed.",
                     default=1337)
    log_metrics_aif = Parameter("loggingtoaif",
                                help="Whether the evaluator should log to AIF",
                                type=bool,
                                default=False)
    imgtypes = Parameter("imgtypes",
                         help="Json encoded list of class names of expected images types",
                         type=JSONType,
                         default='[".jpg", ".jpeg", ".png"]')
    top_k = Parameter("evaltopk",
                      help="Json encoded list ints used as k values during evaluation",
                      type=JSONType,
                      default=json.dumps([1,3,5,10,30]))
    freeze_backbone = Parameter("freezebackbone",
                      help="",
                      type=bool,
                      default=False)
    workdirsize = Parameter("workdirsize",
                            help="Json encoded list of class names of expected images types",
                            default=20)
    @argo(output_artifacts=[{'name': 'trainedmodel',
                             'globalName': 'trainedmodel',
                             'path': str(MODEL_OUTPUT_DIR),
                             'archive': {'none': {}}}],
          input_artifacts=[{'name': 'datain',
                            'path': str(DATA_INPUT_DIR)}],
          labels={"ai.sap.com/resourcePlan": "train.l"},
          volumeMounts=[{'mountPath': '/dev/shm', 'name': 'dshm'}])
    @step
    def start(self):
        """In this step the model is trained.
        """
        setup_loggers(str(MODEL_OUTPUT_DIR), color=False, additional_loggers=[__name__])
        self.eval_frequency = float(self.eval_freq)
        img_extensions = utils.check_extensions(self.imgtypes)
        self.datasets, self.class_names_used = self.prepare_input_data(DATA_INPUT_DIR,
                                                                       train=self.train_input,
                                                                       validation=self.validation_input,
                                                                       test=self.test_input,
                                                                       index=self.index_input,
                                                                       img_extensions=img_extensions,
                                                                       seed=int(self.seed))
        cfg = self.get_train_cfg(self.datasets)
        module_output_path = pathlib.Path(MODEL_OUTPUT_DIR)
        module_output_path.mkdir(parents=True, exist_ok=True)
        with (module_output_path / 'used_config.yaml').open('w') as stream:
            stream.write(cfg.dump())
        trainer = Trainer(cfg)
        self.run_test(cfg, trainer, 'untrained')
        trainer.resume_or_load(resume=False)
        trainer.train()
        self.run_test(cfg, trainer)
        self.next(self.end)

    @step
    def end(self):
        """Currently this step is empty, but it is added because
        metaflow DAGs always need a \'start\' and \'end\' step.
        """
        pass


    @staticmethod
    def predict_dataset(cfg, dataset, trainer, class_names):
        labels = []
        file_names = []
        outputs_val = []
        with torch.no_grad():
            trainer.model.eval()
            dl_val = trainer.build_test_loader(cfg, dataset)
            metadata = MetadataCatalog.get(dataset)
            for batch in dl_val:
                labels.extend([class_names[d['class_id']] if d.get('class_id', None) else '' for d in batch])
                file_names.extend([str(d['file_name']).replace(metadata.base_dir, '') for d in batch])
                outputs_val.append(trainer.model(batch).cpu())
        return torch.cat(outputs_val).numpy(), np.array(labels), np.array(file_names) # pylint: disable=E1101


    def run_test(self, cfg, trainer, suffix=None):
        suffix = f"_{suffix}" if suffix is not None else ""
        test_name = f'test'
        index_name = f'index'
        if test_name in self.datasets and index_name not in self.datasets:
            cfg.defrost()
            cfg.DATASETS.TEST = (test_name,)
            results_test = trainer.test(cfg, trainer.model) # pylint: disable=E1101
        elif index_name in self.datasets:
            index_vectors, index_labels, index_file_names = self.predict_dataset(cfg, index_name, trainer, self.class_names_used)
            np.savez_compressed(cfg.OUTPUT_DIR + f'/index{suffix}.npz',
                                vectors=index_vectors,
                                labels=index_labels,
                                file_names=index_file_names)
            if test_name in self.datasets:
                test_vectors, test_labels, _ = self.predict_dataset(cfg, test_name, trainer, self.class_names_used)
                results_test = get_metrics(
                    embeddings=test_vectors,
                    labels=test_labels,
                    index_embeddings=index_vectors,
                    index_labels=index_labels,
                    ks=cfg.EVAL.CONTRASTIVE.TOP_KS)
        else:
            return
        with open(cfg.OUTPUT_DIR + f'/metrics_test{suffix}.json', 'w') as stream:
            json.dump(results_test, stream, indent=2)
        if self.log_metrics_aif:
            try:
                from sapai import tracking
            except ImportError:
                pass
            else:
                from sap_computer_vision.engine.trainers import AIFLogging
                formatted_metrics = AIFLogging.format_metrics(results_test, step=trainer.iter, labels=[{'name': 'data_split', 'value': 'test'}])
                tracking.log_metrics(formatted_metrics)

    @staticmethod
    def prepare_input_data(base_dir, class_names=None, img_extensions=None, seed=None, **dataset_inputs):
        f'''This function interprets the \'train\', \'test\', \'validation\' parameters.

        To register a dataset in detectron a lightweight version (list of dicts) of the dataset has to be created.
        The folder in which the images are located is used as the label for each image.
        So there must be a subfolder in the input artifact for each class.

        For the \'train\', \'test\', \'validation\' parameters in this pipeline different options are supported.
        The input data is provided as an input artifact and is copy to {DATA_INPUT_DIR}. The parameters for the
        different dataset can be either a subfolder with the input directory, a txt-file containing the filenames
        or a float between zero and 1.

        Examples
        ---------
            1.)
                Structure of the input artifact:
                input_artifact/
                    train/
                        class_1/
                            img1.jpg
                            img2.jpg
                        class_2/
                            ...
                        ...
                    val/
                        class_1/
                            img231.jpg
                            img2123.jpg
                        class_2/
                            ...
                        ...
                    test/
                        class_1/
                            img3213.jpg
                            img32231.jpg
                        class_2/
                            ...
                        ...

                Parameter values:
                \'train\'='train'
                \'validation\'='val'
                \'test\'='test'

                In this example the values of the parameters are relative paths to subfolders
                located in the input artifact.
                The files in the subfolders are used for the corresponding dataset.
            2.)
                Structure of the input artifact:
                input_artifact/
                    class_1/
                        img1.jpg
                        img2.jpg
                    class_2/
                        ...
                    ...
                    splits/
                        train.txt
                        val.txt
                        test.txt

                Parameter values:
                \'train\'='splits/train.txt'
                \'validation\'='splits/val.txt'
                \'test\'='splits/test.txt'
                In this example the values of the parameters are paths to txt files within the in the input artifact.
                The txt-files are expected to contain the file names (1 file name per line with or with file ending)
                for the datasets.
            3.)
                Structure of the input artifact:
                class_1/
                    img1.jpg
                    img2.jpg
                class_2/
                    ...
                ...
                Parameter values:
                \'train\'=0.8
                \'validation\'=0.2
                \'test\'=''
                In this example the values of the parameters are float values and '' for the test parameter.
                The numbers indicate which part of the files in the images/annotation folders should be used
                for the dataset. In the result folder of the pipeline a txt-file for each split will be placed.
                \'validation\' and \'test\' can be in empty string in all cases. If they are set
                to an empty string no evaluation/test is performed during the training.
            4.)
                Structure of the input artifact:
                input_artifact/
                    train.zip /
                        class_1/
                            img1.jpg
                            img2.jpg
                        class_2/
                            ...
                        ...
                    val.zip
                        class_1/
                            img231.jpg
                            img2123.jpg
                        class_2/
                            ...
                        ...
                    test.zip/
                        class_1/
                            img3213.jpg
                            img32231.jpg
                        class_2/
                            ...
                        ...

                Parameter values:
                \'train\'='train.zip'
                \'validation\'='val.zip'
                \'test\'='test.zip'
            '''
        if img_extensions is None:
            img_extensions = ['*.jpg', '*.jpeg']

        base_dir = pathlib.Path(base_dir)

        logger = logging.getLogger(__name__)
        logger.info(f"Preparing datsets:")

        @lru_cache(None)
        def _prepare_input_data(input):
            input_data = None
            if input != '' and input is not None:
                input_data = base_dir / str(input)
                if input_data.exists() and input_data.is_dir():
                    pass
                elif input_data.exists() and input_data.is_file():
                    if input_data.suffix == '.zip':
                        with zipfile.ZipFile(input_data, 'r') as zip_ref:
                            input_data_extracted = input_data.with_suffix('')
                            zip_ref.extractall(input_data_extracted)
                        os.remove(input_data)
                        input_data = input_data_extracted
                else:
                    try:
                        input_data = float(input)
                    except ValueError:
                        input_data = None
            return input_data

        for name, value in dataset_inputs.items():
            prepared = _prepare_input_data(value)
            dataset_inputs[name] = prepared
            logger.info(f"Parameter '{name}'={value} -> {prepared}")

        primary_parameter = next(iter(dataset_inputs.values()))
        if isinstance(primary_parameter, pathlib.Path):
            datasets = {}
            for n, input_ in dataset_inputs.items():
                if isinstance(input_, pathlib.Path):
                    datasets[n], class_names = imgf.register(n,
                                                             class_names=class_names,
                                                             extensions=img_extensions,
                                                             base_dir=(base_dir if input_.is_file() else input_),
                                                             filenames=(input_ if input_.is_file() else None))
        elif isinstance(primary_parameter, float):
            splits = {n: v for n, v in dataset_inputs.items() if isinstance(v, float)}
            datasets, class_names = imgf.split_and_register('',
                                                            base_dir=base_dir,
                                                            splits=splits,
                                                            extensions=img_extensions,
                                                            rnd_gen=seed)
            for n, file_ids in datasets.items():
                with (pathlib.Path(MODEL_OUTPUT_DIR) / f'{n}.txt').open('w') as stream:
                    stream.write('\n'.join([str(f) for f in file_ids]))
        else:
            raise ValueError(f'Invalid input for train data! Input artifact content: {os.listdir(base_dir)}')
        logger.info(f"Successfully registed datasets:")
        for n, v in datasets.items():
            logger.info(f"{n} with {len(v)} examples")
        return datasets, class_names

    def get_train_cfg(self, datasets):
        ''' This function prepares the training config.'''
        cfg = get_cfg()
        cfg.merge_from_file(get_config_file('Base-EarlyStopping'))
        cfg.merge_from_file(get_config_file('Base-Evaluation'))
        cfg.merge_from_file(get_config_file(self.model_name))

        cfg.SEED = int(self.seed)
        cfg.OUTPUT_DIR = str(MODEL_OUTPUT_DIR)

        cfg.SOLVER.MAX_ITER = int(self.n_steps)

        cfg.SOLVER.BASE_LR = float(self.base_lr)
        cfg.SOLVER.GAMMA = float(np.sqrt(0.1))
        cfg.SOLVER.IMS_PER_BATCH = int(self.batch_size)
        cfg.SOLVER.WARMUP_ITERS = max(int(0.01 * cfg.SOLVER.MAX_ITER), 0)
        if isinstance(self.lr_decay, Iterable):
            cfg.SOLVER.STEPS = [cfg.SOLVER.MAX_ITER * p for p in self.lr_decay]
        elif self.lr_decay:
            cfg.SOLVER.STEPS = [cfg.SOLVER.MAX_ITER * p for p in (0.5, 0.75, 0.9)]
        else:
            cfg.SOLVER.STEPS = []

        cfg.SOLVER.EARLY_STOPPING.ENABLED = bool(self.early_stopping)

        cfg.EVAL.LOG_METRICS = bool(self.log_metrics_aif)
        for aug in ['RANDOM_LIGHTING', 'RANDOM_BRIGHTNESS', 'RANDOM_SATURATION', 'RANDOM_CONTRAST', 'CROP', 'CUT_OUT']:
            if cfg.INPUT.get(aug, None) is not None:
                cfg.INPUT[aug].ENABLED = self.additional_augmentations

        cfg.MODEL.TRIPLET_DISTANCE_LEARNER.MARGIN_LOSS.MARGIN = float(self.margin)
        cfg.MODEL.TRIPLET_DISTANCE_LEARNER.CIRCLE_LOSS.MARGIN = float(self.margin)
        cfg.MODEL.TRIPLET_DISTANCE_LEARNER.LOSS = self.loss
        cfg.MODEL.FEATURE_EXTRACTION.PROJECTION_SIZE = None if int(self.embedding_dim) <= 0 else int(self.embedding_dim)
        cfg.MODEL.FEATURE_EXTRACTION.INTERMEDIATE_SIZE = self.intermediate_layers
        cfg.MODEL.FEATURE_EXTRACTION.FREEZE_BACKBONE = bool(self.freeze_backbone)

        sampler = 'PKSampler' if self.loss.upper() == 'CIRCLE_LOSS' else self.sampler

        if sampler.lower() == 'PKSampler'.lower():
            cfg.DATALOADER.SAMPLER_TRAIN = 'PKSampler'
            cfg.MODEL.TRIPLET_DISTANCE_LEARNER.TRIPLET_STRATEGY = ('*', '*')
            delay = (cfg.SOLVER.MAX_ITER  * 0.5)
            strategies_pos = np.linspace(0.5, 0.8, 21)
            strategies_neg = 1. - strategies_pos
            strategies = [(float(p), float(n)) for p, n in zip(strategies_pos, strategies_neg)]
            switch_steps = np.linspace(delay, cfg.SOLVER.MAX_ITER, len(strategies)+1)[:-1]
            cfg.DATALOADER.PK_SAMPLER.STRATEGY_SWITCHES = [(int(step), strat) for (step, strat) in zip(switch_steps, strategies)]
            cfg.DATALOADER.PK_SAMPLER.P_CLASSES_PER_BATCH = int(self.p_classes_per_batch)
            cfg.DATALOADER.PK_SAMPLER.K_EXAMPLES_PER_CLASS = int(self.k_examples_per_class)
        else:
            raise NotImplementedError

        train_name = f'train'
        validation_name = f'validation'
        cfg.DATASETS.TRAIN = (train_name, )

        if validation_name in datasets.keys():
            cfg.DATASETS.TEST = (validation_name, )
            if self.eval_frequency > 1:
                cfg.TEST.EVAL_PERIOD = int(self.eval_frequency)
            else:
                cfg.TEST.EVAL_PERIOD = int(cfg.SOLVER.MAX_ITER * float(self.eval_frequency))
        else:
            cfg.DATASETS.TEST = None
            cfg.TEST.EVAL_PERIOD = -1
        cfg.EVAL.CONTRASTIVE.TOP_KS = [int(k) for k in self.top_k]
        cfg.set_new_allowed(True)
        cfg.TRAINING_INFO = CfgNode()
        cfg.TRAINING_INFO.TASK = 'TRIPLET_DISTANCE_MERIC_LEARNING'
        cfg.freeze()
        return cfg



if __name__ == '__main__':
    from sap_computer_vision.utils.metaflow_utils import add_parameters_help_to_doc_string
    add_parameters_help_to_doc_string(TripletDistanceMetricTrain)
    TripletDistanceMetricTrain()
