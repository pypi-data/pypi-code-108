import pathlib
import json
import zipfile
import os
from functools import lru_cache
import logging

from metaflow import FlowSpec, step, argo, argo_base, Parameter, JSONType

from detectron2.config import CfgNode

import sap_computer_vision.datasets.pascal_voc_style as pvs
import sap_computer_vision.datasets.utils as utils
from sap_computer_vision import get_cfg, get_config_file, setup_loggers
from sap_computer_vision.evaluators import ObjectDetectionEvaluator
from sap_computer_vision.engine import ObjectDetectionTrainer


MODEL_OUTPUT_DIR = pathlib.Path('/tmp/model')
DATA_INPUT_DIR = pathlib.Path('/tmp/datain')


class Trainer(ObjectDetectionTrainer):
    @classmethod
    def build_evaluator(cls, cfg, dataset_name):
        if cfg.TEST.EVAL_PERIOD <= 0:
            raise NotImplementedError
        else:
            return ObjectDetectionEvaluator(cfg, dataset_names=(dataset_name, ))  # pylint: disable=E1124,E1125


@argo_base(
    labels={'scenarios.ai.sap.com/id': 'scenario-id',
            'ai.sap.com/version': 'scenario-version'},
    annotations={'scenarios.ai.sap.com/name': 'scenario-name',
                 'executables.ai.sap.com/name': 'train-od-model',
                 'executables.ai.sap.com/description': "Train Pipeline Object Detection",
                 'artifacts.ai.sap.com/datain.kind': 'dataset',
                 'artifacts.ai.sap.com/trainedmodel.kind': 'model'},
    image='mlf.docker.repositories.sapcdn.io/com.sap.ai/sap_cv_metaflow:0.0.25',
    imagePullSecrets=[{'name': 'your-image-pull-secret'}],
    envFrom=[{'secretRef': {'name': 'default-object-store-secret'}}],
    volumes=[{'name': 'dshm', 'emptyDir': {'medium': 'Memory'}}])
class ObjectDetectionTrain(FlowSpec):
    """Pipeline to train a model for object detection.
    """
    model_name = Parameter("modelname",
                           help="Format of the boxes in the annotation files.",
                           default="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
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
    class_names = Parameter("classnames",
                            help="Json encoded list of class names. If empty or not valid json. Classes will " + \
                                 "extracted from the train/val/test datasets.",
                            type=JSONType,
                            default=json.dumps([]))
    box_mode = Parameter("boxmode",
                         help="Format of the boxes in the annotation files.",
                         default="XYXY_ABS")
    batch_size = Parameter("batchsize",
                           help="Number of images per batch.",
                           default=8)
    lr_decay = Parameter("lrdecay",
                         help="Whether learning rate should be decreased over the training.",
                         default=True)
    early_stopping = Parameter("earlystopping",
                               help="Whether early stopping should be active.",
                               default=True)
    additional_augmentations = Parameter("additionalaugs",
                                         help="Enables cropping, random saturation, random lightning, ranodm brightness and random contrast as additional augmentations.",
                                         default=True)
    n_steps = Parameter("ntrainsteps",
                        help="Number of training steps.",
                        default=3000)
    eval_freq = Parameter("evalfreq",
                          help="Frequency of evaluation. If > 1 it is treated as every \'evalfreq\' steps. If < 1 an evaluation in done every \'evalfreq\'×\'ntrainsteps\' steps",
                          default=0.1)
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
                         default=json.dumps([".jpg", ".jpeg", ".png"]))
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
        class_names = None if len(self.class_names) == 0 else self.class_names
        img_extensions = utils.check_extensions(self.imgtypes)
        self.datasets, self.class_names_used = self.prepare_input_data(DATA_INPUT_DIR,
                                                                  train=self.train_input,
                                                                  validation=self.validation_input,
                                                                  test=self.test_input,
                                                                  class_names=class_names,
                                                                  img_extensions=img_extensions,
                                                                  seed=int(self.seed))
        cfg = self.get_train_cfg(self.datasets, self.class_names_used)
        module_output_path = pathlib.Path(MODEL_OUTPUT_DIR)
        module_output_path.mkdir(parents=True, exist_ok=True)
        with (module_output_path / 'used_config.yaml').open('w') as stream:
            stream.write(cfg.dump())
        trainer = Trainer(cfg)
        trainer.resume_or_load(resume=False)
        trainer.train()

        test_name = f'test'
        if test_name in self.datasets:
            cfg.defrost()
            cfg.DATASETS.TEST = (test_name,)
            results_test = trainer.test(cfg, trainer.model) #  # pylint: disable=E1101
            with open(cfg.OUTPUT_DIR + '/metrics_test.json', 'w') as stream:
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
        self.next(self.end)

    @step
    def end(self):
        """Currently this step is empty, but it is added because
        metaflow DAGs always need a \'start\' and \'end\' step.
        """
        pass



    @staticmethod
    def prepare_input_data(base_dir, class_names=None, img_extensions=None, seed=None, **dataset_inputs):
        f'''This function interprets the \'train\', \'test\', \'validation\' parameters.

        To register a dataset in detectron a lightweight version (list of dicts) of the dataset has to be created.
        Currently this pipeline supports only datasets in the "Pascal VOC" format. Data in the "Pascal VOC" format
        consists of two folders "images" and "annotations". The image folder contains the images and the annotaions
        folder xmls. The xmls contain the bounding boxes and labels for each image. The name of the image and its
        corresponding xml file should be identical except of the file ending.

        For the \'train\', \'test\', \'validation\' parameters in this pipeline different options are supported.
        The input data is provided as in input artifact and is copy to {DATA_INPUT_DIR}. The parameters for the
        different dataset can be either a subfolder with the input directory, a txt-file containing the filenames
        or a float between zero and 1.

        Examples
        ---------
            1.)
                Structure of the input artifact:
                input_artifact/
                    train/
                        images/
                        annotaions/
                    val/
                        images/
                        annotaions/
                    test/
                        images/
                        annotaions/

                Parameter values:
                \'train\'='train'
                \'validation\'='val'
                \'test\'='test'

                In this example the values of the parameters are paths to subfolders in the input artifact.
                The files in the subfolders are used for the corresponding dataset.
            2.)
                Structure of the input artifact:
                input_artifact/
                    images/
                    annotaions/
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
                input_artifact/
                    images/
                    annotaions/

                Parameter values:
                \'train\'=0.8
                \'validation\'=0.2
                \'test\'=''
                In this example the values of the parameters are float values and '' for the test parameter.
                The numbers indicate which part of the files in the images/annotation folders should be used
                for the dataset. In the result folder of the pipeline a txt-file for each split will be placed.
                \'validation\' and \'test\' can be in empty string in all cases. If they are set
                to an empty string no evaluation/test is performed during the training.
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
                    datasets[n], class_names = pvs.register(n,
                                                            *(pvs.find_folders(input_.parent) if input_.is_file() else pvs.find_folders(input_)),
                                                            filenames=input_ if input_.is_file() else None,
                                                            class_names=class_names,
                                                            extensions=img_extensions)
        elif isinstance(primary_parameter, float):
            img_dir, xml_dir = pvs.find_folders(base_dir)
            splits = {n: v for n, v in dataset_inputs.items() if isinstance(v, float)}
            datasets, class_names = pvs.split_and_register('',
                                                           img_dir=img_dir,
                                                           xml_dir=xml_dir,
                                                           splits=splits,
                                                           extensions=img_extensions,
                                                           rnd_gen=seed)
            for n, file_ids in datasets.items():
                with (pathlib.Path(MODEL_OUTPUT_DIR) / f'{n}.txt').open('w') as stream:
                    stream.write('\n'.join([str(f) for f in file_ids]))
        else:
            raise ValueError('Invalid input for train data. Please provide a path to a file containing image names '
                             f'or path to folder containing image or a float so the images under \'{base_dir}/images\'')
        for n, v in datasets.items():
            if not isinstance(v, pathlib.Path):
                logger.info(f"{n} with {len(v)} examples")
            else:
                logger.info(f"{n} from {v}")
        return datasets, class_names

    def get_train_cfg(self, datasets, class_names):
        ''' This function prepares the training config.'''
        cfg = get_cfg()
        cfg.merge_from_file(get_config_file('Base-EarlyStopping'))
        cfg.merge_from_file(get_config_file('Base-Evaluation'))
        cfg.merge_from_file(get_config_file(self.model_name))
        cfg.SEED = int(self.seed)
        cfg.SOLVER.EARLY_STOPPING.ENABLED = bool(self.early_stopping)
        cfg.OUTPUT_DIR = str(MODEL_OUTPUT_DIR)

        cfg.SOLVER.MAX_ITER = int(self.n_steps)
        cfg.SOLVER.BASE_LR = float(self.base_lr)
        cfg.SOLVER.IMS_PER_BATCH = int(self.batch_size)
        cfg.SOLVER.WARMUP_ITERS = max(int(0.01 * cfg.SOLVER.MAX_ITER), 0)
        if bool(self.lr_decay):
            cfg.SOLVER.STEPS = [cfg.SOLVER.MAX_ITER * p for p in (0.5, 0.75, 0.9)]
        else:
            cfg.SOLVER.STEPS = []

        train_name = 'train'
        validation_name = 'validation'
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
        cfg.set_new_allowed(True)
        cfg.TRAINING_INFO = CfgNode()
        cfg.TRAINING_INFO.THING_CLASSES = class_names
        cfg.TRAINING_INFO.TASK = 'OBJECT_DETECTION'
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(class_names)
        cfg.EVAL.LOG_METRICS = bool(self.log_metrics_aif)
        for aug in ['RANDOM_LIGHTING', 'RANDOM_BRIGHTNESS', 'RANDOM_SATURATION', 'RANDOM_CONTRAST', 'CROP']:
            if cfg.INPUT.get(aug, None) is not None:
                cfg.INPUT[aug].ENABLED = self.additional_augmentations
        cfg.freeze()
        return cfg



if __name__ == '__main__':
    from sap_computer_vision.utils.metaflow_utils import add_parameters_help_to_doc_string
    add_parameters_help_to_doc_string(ObjectDetectionTrain)
    ObjectDetectionTrain()
