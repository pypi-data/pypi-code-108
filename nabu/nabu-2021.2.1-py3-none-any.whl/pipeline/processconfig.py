import os
from .config import parse_nabu_config_file
from ..utils import deprecation_warning
from ..resources.logger import Logger, PrinterLogger
from .config import validate_config
from ..resources.dataset_analyzer import analyze_dataset, _tomoscan_has_nxversion
from .estimators import DetectorTiltEstimator

class ProcessConfigBase:
    """
    A class for describing the Nabu process configuration.
    """
    # Must be overriden by inheriting class
    default_nabu_config = None
    config_renamed_keys = None

    def __init__(
        self,
        conf_fname=None,
        conf_dict=None,
        dataset_infos=None,
        dataset_info=None,
        checks=True,
        remove_unused_radios=True,
        create_logger=False,
    ):
        """
        Initialize a ProcessConfig class.

        Parameters
        ----------
        conf_fname: str
            Path to the nabu configuration file. If provided, the parameters
            `conf_dict` is ignored.
        conf_dict: dict
            A dictionary describing the nabu processing steps.
            If provided, the parameter `conf_fname` is ignored.
        dataset_info: DatasetAnalyzer
            A `DatasetAnalyzer` class instance.
        checks: bool, optional, default is True
            Whether to perform checks on configuration and datasets (recommended !)
        remove_unused_radios: bool, optional, default is True
            Whether to remove unused radios, i.e radios present in the dataset,
            but not explicitly listed in the scan metadata.
        create_logger: str or bool, optional
            Whether to create a Logger object. Default is False, meaning that the logger
            object creation is left to the user.
            If set to True, a Logger object is created, and logs will be written
            to the file "nabu_dataset_name.log".
            If set to a string, a Logger object is created, and the logs will be written
            to the file specified by this string.
        """
        # COMPAT.
        if dataset_infos is not None:
            deprecation_warning(
                "The parameter 'dataset_infos' will be renamed 'dataset_info' in a future version",
                func_name="processconfig_dataset_infos"
            )
        if (dataset_infos is not None) and (dataset_info is not None):
            raise ValueError("Please provide either 'dataset_info' or 'dataset_infos'")
        dataset_info = dataset_info or dataset_infos
        # TODO add this in doc.
        # deprecation_warning(
            # "The parameters 'checks' and 'remove_unused_radios' are not used anymore and will be removed in a future version",
            # func_name='processconfig_checks'
        # )
        # ---

        # Step (1a): create 'nabu_config'
        self._parse_configuration(conf_fname, conf_dict)
        self._create_logger(create_logger)

        # Step (1b): create 'dataset_info'
        self._browse_dataset(dataset_info)

        # Step (2a)
        self._update_dataset_info_with_user_config()

        # Step (3): estimate tilt, CoR, ...
        self._dataset_estimations()

        # Step (4)
        self._coupled_validation()

        # Step (5)
        self._build_processing_steps()

        # Step (6)
        self._configure_save_steps()
        self._configure_resume()


    # COMPAT.
    @property
    def dataset_infos(self):
        deprecation_warning(
            "The name 'dataset_infos' is deprecated. Please use 'dataset_info'.",
            func_name="processconfig_dataset_infos_attr"
        )
        return self.dataset_info
    # ---

    def _create_logger(self, create_logger):
        if create_logger is False:
            self.logger = PrinterLogger()
            return
        elif create_logger is True:
            dataset_loc = self.nabu_config["dataset"]["location"]
            dataset_fname_rel = os.path.basename(dataset_loc)
            if os.path.isfile(dataset_loc):
                logger_filename = os.path.join(
                    os.path.abspath(os.getcwd()),
                    os.path.splitext(dataset_fname_rel)[0] + "_nabu.log"
                )
            else:
                logger_filename = os.path.join(
                    os.path.abspath(os.getcwd()),
                    dataset_fname_rel + "_nabu.log"
                )
        elif isinstance(create_logger, str):
            logger_filename = create_logger
        else:
            raise ValueError("Expected bool or str for create_logger")
        self.logger = Logger(
            "nabu",
            level=self.nabu_config["pipeline"]["verbosity"],
            logfile=logger_filename
        )


    def _parse_configuration(self, conf_fname, conf_dict):
        """
        Parse the user configuration and builds a dictionary.

        Parameters
        ----------
        conf_fname: str
            Path to the .conf file. Mutually exclusive with 'conf_dict'
        conf_dict: dict
            Dictionary with the configuration. Mutually exclusive with 'conf_fname'
        """
        if not((conf_fname is None) ^ (conf_dict is None)):
            raise ValueError("You must either provide 'conf_fname' or 'conf_dict'")
        if conf_fname is not None:
            if not os.path.isfile(conf_fname):
                raise ValueError("No such file: %s" % conf_fname)
            self.conf_fname = conf_fname
            self.conf_dict = parse_nabu_config_file(conf_fname)
        else:
            self.conf_dict = conf_dict
        if self.default_nabu_config is None or self.config_renamed_keys is None:
            raise ValueError(
                "'default_nabu_config' and 'config_renamed_keys' must be specified by classes inheriting from ProcessConfig"
            )
        self.nabu_config = validate_config(
            self.conf_dict,
            self.default_nabu_config,
            self.config_renamed_keys,
        )


    def _browse_dataset(self, dataset_info):
        """
        Browse a dataset and builds a data structure with the relevant information.
        """
        self.logger.debug("Browsing dataset")
        if dataset_info is not None:
            self.dataset_info = dataset_info
        else:
            extra_options = {
                "exclude_projections": self.nabu_config["dataset"]["exclude_projections"],
                "hdf5_entry": self.nabu_config["dataset"]["hdf5_entry"],
            }
            if _tomoscan_has_nxversion: # legacy - should become "if True" soon
                extra_options["nx_version"] = self.nabu_config["dataset"]["nexus_version"]
            else:
                self.logger.warning("Cannot use 'nx_version' for browsing dataset: need tomoscan > 0.6.0")
            self.dataset_info = analyze_dataset(
                self.nabu_config["dataset"]["location"],
                extra_options=extra_options,
                logger=self.logger
            )


    def _update_dataset_info_with_user_config(self):
        """
        Update the 'dataset_info' (DatasetAnalyzer class instance) data structure with options from user configuration.
        """
        raise ValueError("Base class")

    def _get_rotation_axis_position(self):
        self.dataset_info.axis_position = self.nabu_config["reconstruction"]["rotation_axis_position"]


    def _update_rotation_angles(self):
        raise ValueError("Base class")


    def _dataset_estimations(self):
        """
        Perform estimation of several parameters like center of rotation and detector tilt angle.
        """
        self.logger.debug("Doing dataset estimations")
        self._get_tilt()
        self._get_cor()


    def _get_cor(self):
        raise ValueError("Base class")


    def _get_tilt(self):
        tilt = self.nabu_config["preproc"]["tilt_correction"]
        user_rot_projs = self.nabu_config["preproc"]["rotate_projections"]
        if user_rot_projs is not None and tilt is not None:
            msg = "=" * 80 + "\n"
            msg += "Both 'detector_tilt' and 'rotate_projections' options were provided. The option 'rotate_projections' will take precedence. This means that the projections will be rotated by %f degrees and the option 'detector_tilt' will be ignored." % user_rot_projs
            msg += "\n" + "=" * 80
            self.logger.warning(msg)
            tilt = user_rot_projs
        #
        if isinstance(tilt, str): # auto-tilt
            self.tilt_estimator = DetectorTiltEstimator(
                self.dataset_info,
                logger=self.logger,
                autotilt_options=self.nabu_config["preproc"]["autotilt_options"]
            )
            tilt = self.tilt_estimator.find_tilt(tilt_method=tilt)
        self.dataset_info.detector_tilt = tilt


    def _coupled_validation(self):
        """
        Validate together the dataset information and user configuration.
        Update 'dataset_info' and 'nabu_config'
        """
        raise ValueError("Base class")


    def _build_processing_steps(self):
        """
        Build the processing steps, i.e a tuple (steps, options) where
           - steps is a list of str (list of processing steps names)
           - options is a dict with processing options
        """
        raise ValueError("Base class")


    build_processing_steps = _build_processing_steps # COMPAT.


    def _configure_save_steps(self):
        raise ValueError("Base class")


    def _configure_resume(self):
        raise ValueError("Base class")


