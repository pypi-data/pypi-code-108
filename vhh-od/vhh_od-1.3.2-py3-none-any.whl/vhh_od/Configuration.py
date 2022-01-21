from vhh_od.utils import *
import yaml


class Configuration:
    """
    This class is needed to read the configuration parameters specified in the configuration.yaml file.
    The instance of the class is holding all parameters during runtime.

    .. note::
       e.g. ./config/config_vhh_test.yaml

        the yaml file is separated in multiple sections
        config['Development']
        config['PreProcessing']
        config['StcCore']
        config['Evaluation']

        whereas each section should hold related and meaningful parameters.
    """

    def __init__(self, config_file: str):
        """
        Constructor

        :param config_file: [required] path to configuration file (e.g. PATH_TO/config.yaml)
                                       must be with extension ".yaml"
        """
        printCustom("create instance of configuration ... ", STDOUT_TYPE.INFO)

        if(config_file.split('.')[-1] != "yaml"):
            printCustom("Configuration file must have the extension .yaml!", STDOUT_TYPE.ERROR)

        self.config_file = config_file

        self.debug_flag = -1
        self.stc_results_path = None
        self.save_debug_pkg_flag = -1

        self.batch_size = -1

        self.save_raw_results = -1
        self.path_postfix_raw_results = None
        self.path_prefix_raw_results = None
        self.path_raw_results = None

        self.save_final_results = -1
        self.path_prefix_final_results = None
        self.path_postfix_final_results = None
        self.path_final_results = None

        self.path_videos = None
        self.path_pre_trained_model = None

        self.path_eval_results = None
        self.path_raw_results_eval = None
        self.save_eval_results = -1
        self.path_gt_data = None

        self.model_config_path = None
        self.confidence_threshold = -1
        self.model_class_names_path = None
        self.model_class_selection_path = None

        self.use_deepsort = -1
        self.ds_model_path = None
        self.ds_max_dist = -1
        self.ds_min_conf = -1
        self.ds_nms_max_overlap = -1
        self.ds_max_iou_dist = -1
        self.ds_max_age = -1
        self.ds_num_init = -1

    def loadConfig(self):
        """
        Method to load configurables from the specified configuration file
        """

        fp = open(self.config_file, 'r')
        config = yaml.load(fp, Loader=yaml.BaseLoader)

        developer_config = config['Development']
        pre_processing_config = config['PreProcessing']
        od_core_config = config['OdCore']
        evaluation_config = config['Evaluation']

        # developer_config section
        self.debug_flag = int(developer_config['DEBUG_FLAG'])
        self.stc_results_path = developer_config['STC_RESULTS_PATH']
        self.save_debug_pkg_flag = int(developer_config['SAVE_DEBUG_PKG'])

        # pre-processing section
        self.resize_dim = (int(pre_processing_config['RESIZE_DIM'].split(',')[0]),
                           int(pre_processing_config['RESIZE_DIM'].split(',')[1]))

        # od_core_config section
        self.batch_size = int(od_core_config['BATCH_SIZE'])

        self.path_stc_results = od_core_config['PATH_STC_RESULTS']

        self.save_raw_results = int(od_core_config['SAVE_RAW_RESULTS'])
        self.path_postfix_raw_results = od_core_config['POSTFIX_RAW_RESULTS']
        self.path_prefix_raw_results = od_core_config['PREFIX_RAW_RESULTS']
        self.path_raw_results = od_core_config['PATH_RAW_RESULTS']

        self.save_final_results = int(od_core_config['SAVE_FINAL_RESULTS'])
        self.path_prefix_final_results = od_core_config['PREFIX_FINAL_RESULTS']
        self.path_postfix_final_results = od_core_config['POSTFIX_FINAL_RESULTS']
        self.path_final_results = od_core_config['PATH_FINAL_RESULTS']

        self.path_videos = od_core_config['PATH_VIDEOS']
        self.path_pre_trained_model = od_core_config['PATH_PRETRAINED_MODEL']

        self.model_config_path = od_core_config['MODEL_CONFIG_PATH']

        self.confidence_threshold = float(od_core_config['MODEL_CONF_THRES'])
        self.nms_threshold = float(od_core_config['MODEL_NMS_THRESH'])

        self.model_class_names_path = od_core_config['MODEL_CLASS_NAMES_PATH']
        self.model_class_selection_path = od_core_config['MODEL_CLASS_SELECTION_PATH']

        self.max_frames = int(od_core_config['MAX_FRAMES'])

        self.use_classifier = od_core_config['USE_CLASSIFIER'] == "1"
        self.use_classifier_majority_voting = od_core_config['USE_CLASSIFIER_MAJORITY_VOTING'] == "1"
        self.classifier_model_path = od_core_config['PATH_TO_CLASSIFIER_MODEL']
        self.classifier_model_architecture = od_core_config['CLASSIFIER_MODEL_ARCHITECTURE']

        self.do_normalize_coordinates = od_core_config['DO_NORMALIZE_COORDINATES'] == "1"
        self.others_factor = od_core_config['OTHERS_FACTOR']
        self.shot_types_do_not_run_od = od_core_config['SHOT_TYPES_TO_NOT_RUN_OD']
        
        #DeepSort Parameters
        if od_core_config["USE_DEEPSORT"] == "1":
            self.use_deepsort = True
        else:
            self.use_deepsort = False
        self.ds_model_path = od_core_config["DEEPSORT_MODEL_PATH"]
        self.ds_max_dist = float(od_core_config["DS_MAX_DIST"])
        self.ds_min_conf = float(od_core_config["DS_MIN_CONF"])
        self.ds_nms_max_overlap = float(od_core_config["DS_NMS_MAX_OVERLAP"])
        self.ds_max_iou_dist = float(od_core_config["DS_MAX_IOU_DIST"])
        self.ds_max_age = int(od_core_config["DS_MAX_AGE"])
        self.ds_num_init = int(od_core_config["DS_NUM_INIT"])

        # evaluation section
        self.path_raw_results_eval = evaluation_config['PATH_RAW_RESULTS']
        self.path_eval_results = evaluation_config['PATH_EVAL_RESULTS']
        self.save_eval_results = int(evaluation_config['SAVE_EVAL_RESULTS'])
        self.path_gt_data = evaluation_config['PATH_GT_ANNOTATIONS']
