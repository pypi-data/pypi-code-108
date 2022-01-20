from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
import shutil
import tempfile
import os
import importlib
import sys
import logging
import pkg_resources
import pandas as pd
import glob

from pathlib import PurePath, Path
from zipfile import ZipFile

# need dill to be able to pickle LIME
import dill
import docker

from arthurai.common.constants import Stage, ValueType, InputType
from arthurai.common.exceptions import ExpectedParameterNotFoundError, ArthurUserError, InternalTypeError, \
    UserValueError
from arthurai.core.util import NumpyEncoder
from arthurai.explainability.arthur_explainer import ArthurExplainer
#  imports ArthurModel for type checking, required due to circular import
if TYPE_CHECKING:
    from arthurai.core.models import ArthurModel

logger = logging.getLogger(__name__)


class ExplanationPackager(object):
    """Manages the project source code and explainer for this model.
    Intended only for internal use. Used to create explainer object, package files and format config for the 
    update enrichments API endpoint.

    See model.update_enrichments() for more details on usage
    """

    # fields required to geenerate explainability files
    FILE_FIELDS = ['project_directory', 'user_predict_function_import_path', 'requirements_file', ]

    def __init__(self, model: 'ArthurModel', **kwargs):
        """Constructor for ExplanationPackager. Explanation packager needs to handle case of
        user setting files, and user just updating config. Because of this, don't raise any
        exceptions in constructor for missing required fields. Instead check and raise the exception in
        the function that needs the field.
        """
        self._model = model

        # use all kwargs so its easy to call constructor using config dict in model.update_enrichments
        self.df: pd.DataFrame = kwargs.get('df')
        self.project_directory: Optional[str] = kwargs.get("project_directory")
        self.streaming_explainability_enabled = kwargs.get("streaming_explainability_enabled")
        self.ignore_dirs = set(kwargs.get("ignore_dirs", []))
        self.user_predict_function_import_path: Optional[str] = kwargs.get("user_predict_function_import_path")
        self.requirements_file = kwargs.get("requirements_file")
        self.python_version = kwargs.get("python_version")
        self.sdk_version = kwargs.get("sdk_version")
        self.explanation_nsamples = kwargs.get("explanation_nsamples")
        self.explanation_algo = kwargs.get("explanation_algo")
        self.model_server_num_cpu = kwargs.get('model_server_num_cpu')
        self.model_server_memory = kwargs.get('model_server_memory')
        self.model_server_max_replicas = kwargs.get('model_server_max_replicas')
        self.inference_consumer_num_cpu = kwargs.get('inference_consumer_num_cpu')
        self.inference_consumer_memory = kwargs.get('inference_consumer_memory')
        self.inference_consumer_thread_pool_size = kwargs.get('inference_consumer_thread_pool_size')
        self.inference_consumer_score_percent = kwargs.get('inference_consumer_score_percent')
        self.text_delimiter = model.text_delimiter
        self.shap_nrows = kwargs.get("shap_nrows", 20)

        # Get all hidden files and add them to the ignore_dirs list
        if self.project_directory:
            hidden_files_temp = glob.glob(os.path.join(self.project_directory, '.*'))
            hidden_files = set([path.split('/')[-1] for path in hidden_files_temp])
            self.ignore_dirs = self.ignore_dirs.union(hidden_files)

        # explanation_algo is saved on the model object, and determines which explainer to use
        # however we always create both lime and shap, if possible, regardless of explanation_algo
        # this is to more easily allow switching between the 2
        self.enable_shap = self._model.input_type != InputType.NLP
        self.enable_lime = True
        if (self._model.input_type == InputType.NLP or self._model.input_type == InputType.Image) and self.explanation_algo != ArthurExplainer.LIME:
            logger.warning(f"Only lime is supported for {self._model.input_type} explainabilty but shap was passed. "
                           "Automatically setting explanation_algo to lime")
            self.explanation_algo = ArthurExplainer.LIME

        self.explainer: ArthurExplainer = None
        self.zipfile: Optional[PurePath] = None

        self.dirname = "model_files"
        self.volume = os.path.join(tempfile.TemporaryDirectory(dir='/tmp').name, self.dirname)
        self.bind_path = "/mnt/model_files"
        self.test_script = "test.sh"
        self.example: Optional[List] = None

    def contains_file_fields(self) -> Tuple[bool, bool]:
        """Returns (onePresent, allPresent)
        onePresent is true if at least one file field was supplied
        AllPresent is true if all file fields are supplied
        """
        # NOTE if adding new file field check here, ensure its added to FILE_FIELDS at top of file
        checks = []
        checks.append(self.project_directory is not None)
        checks.append(self.user_predict_function_import_path is not None)
        checks.append(self.requirements_file is not None)

        return (any(checks), all(checks))

    def build_categorical_lookup_table(self) -> List[Optional[Dict[str, int]]]:
        """Builds the lookup table that ArthurExplainer needs for encoding strings"""
        num_attributes = len(self._model.get_attributes(Stage.ModelPipelineInput))
        label_mapping: List[Optional[Dict[str, int]]] = [None for _ in range(num_attributes)]
        sorted_attr = sorted(self._model.get_attributes(Stage.ModelPipelineInput), key=lambda x: x.position)
        for i, attr in enumerate(sorted_attr):
            if attr.categorical and attr.value_type == ValueType.String:
                label_mapping[i] = {val.value: j for j, val in enumerate(attr.categories)}
        return label_mapping

    def create(self) -> None:
        """Create an explainer for this model.

        :param: df: the training data for the explainer
        :param: shap_nrows: number of rows to sample the dataframe passed in
        """
        # this should never happen since we check for this at model onboarding
        if self._model.input_type == InputType.NLP and (self.text_delimiter is None or self.text_delimiter == ""):
            raise ExpectedParameterNotFoundError(f"Missing text delimiter. {InputType.NLP} require setting a text delimiter.")

        pipeline_attributes = self._model.get_attributes(Stage.ModelPipelineInput)
        pipeline_attributes_in_order = sorted(pipeline_attributes, key=lambda x: x.position)
        predicted_attrs = self._model.get_attributes(Stage.PredictedValue)

        # get categorical attr indices
        categorical_attr_indices = [i for i, attr in enumerate(pipeline_attributes_in_order) if attr.categorical]

        # pull out pipeline features from data
        # dataframe is not required for image models, only tabular and nlp
        if self.df is not None:
            attr_names = [attr.name for attr in pipeline_attributes_in_order]
            explanation_training_data = self.df[attr_names]
            self.example = list(explanation_training_data.iloc[0, :])
        else:
            explanation_training_data = None

        if self.project_directory is None:
            raise InternalTypeError("project_directory is None")
        if not os.path.isabs(self.project_directory):
            raise UserValueError(f"Failed to find '{self.project_directory}'."
                                f"Please ensure this is an absolute path.")
        sys.path.insert(0, self.project_directory)
        current_dir = os.getcwd()
        os.chdir(self.project_directory)
        try:
            req_file_errors = self.validate_requirements_add_sklearn()
            if len(req_file_errors) > 0:
                error_str = '\n' + '\n'.join(req_file_errors)
                raise UserValueError(f"Failed to validate requirements file: {error_str}")

            if self.user_predict_function_import_path is None:
                raise InternalTypeError("user_predict_function_import_path is None")
            try:
                customer_model: Any = importlib.import_module(self.user_predict_function_import_path)
            except ModuleNotFoundError:
                raise UserValueError(f"Failed to import user predict function "
                                     f"'{self.user_predict_function_import_path}'. Please ensure that the path "
                                     f"is available in the project directory '{self.project_directory}'.")
            load_image_func = customer_model.load_image if self._model.input_type == InputType.Image else None
            label_mapping = self.build_categorical_lookup_table()
            self.explainer = ArthurExplainer(model_type=self._model.output_type,
                                             model_input_type=self._model.input_type,
                                             num_predicted_attributes=len(predicted_attrs),
                                             predict_func=customer_model.predict,
                                             data=explanation_training_data,
                                             categorical_features=categorical_attr_indices,
                                             label_mapping=label_mapping,
                                             shap_training_samples=self.shap_nrows,
                                             text_delimiter=self.text_delimiter,
                                             enable_shap=self.enable_shap,
                                             load_image_func=load_image_func)
        finally:
            sys.path.remove(self.project_directory)
            os.chdir(current_dir)

    def get_request_files(self) -> List[Any]:
        """Returns files needed for request, for use with model.update_enrichments
        """
        if self.zipfile is None:
            raise InternalTypeError("zipfile is None")
        if self.project_directory is None:
            raise InternalTypeError("project_directory is None")
        if self.requirements_file is None:
            raise InternalTypeError("requirements_file is None")
        return [
            ("user_project.zip", open(self.zipfile, "rb")),
            ("user_requirements_file.txt",
             open(os.path.join(self.project_directory, self.requirements_file), "rb"),
             "text/plain"),
            ("explainer.pkl", dill.dumps(self.explainer)),
        ]

    def get_request_config(self) -> Dict[str, str]:
        """Generates config dict for explainer. For use with model.update_enrichments
        """
        config = {}

        # support shap not being enabled and not sending expected values
        if self.explainer is not None and self.explainer.enable_shap:
            expected_value = NumpyEncoder.convert_value(self.explainer.shap_expected_values())
            if not isinstance(expected_value, list):
                expected_value = [expected_value]
            config['shap_expected_values'] = expected_value

        if self.python_version:
            config['python_version'] = self.python_version.split()[0]
        if self.sdk_version:
            config['sdk_version'] = self.sdk_version.split()[0]
        if self.user_predict_function_import_path:
            config['user_predict_function_import_path'] = self.user_predict_function_import_path
        if self.explanation_algo:
            config['explanation_algo'] = self.explanation_algo
        if self.streaming_explainability_enabled is not None:
            config['streaming_explainability_enabled'] = self.streaming_explainability_enabled
        if self.explanation_nsamples:
            config['explanation_nsamples'] = self.explanation_nsamples
        if self.model_server_num_cpu:
            config['model_server_cpu'] = self.model_server_num_cpu
        if self.model_server_memory:
            config['model_server_memory'] = self.model_server_memory
        if self.model_server_max_replicas:
            config['model_server_max_replicas'] = self.model_server_max_replicas
        if self.inference_consumer_num_cpu:
            config['inference_consumer_cpu'] = self.inference_consumer_num_cpu
        if self.inference_consumer_memory:
            config['inference_consumer_memory'] = self.inference_consumer_memory
        if self.inference_consumer_thread_pool_size:
            config['inference_consumer_thread_pool_size'] = self.inference_consumer_thread_pool_size
        if self.inference_consumer_score_percent:
            config['inference_consumer_score_percent'] = self.inference_consumer_score_percent

        return config


    def make_zip(self) -> None:
        """Create the zip file for the project directory."""
        # ensure requirements file exists
        if self.project_directory is None:
            raise InternalTypeError("project_directory is None")
        if self.requirements_file is None:
            raise InternalTypeError("requirements_file is None")
        if not os.path.exists(os.path.join(self.project_directory, self.requirements_file)):
            raise ArthurUserError(
                "File {0} does not exist".format(os.path.join(self.project_directory, self.requirements_file)))

        zipfile = PurePath(self.volume, "project").with_suffix(".zip")
        base_dir = PurePath(self.project_directory)

        if not os.path.exists(self.volume):
            os.makedirs(self.volume)

        # create a ZipFile object
        with ZipFile(zipfile, 'w') as zip_file:
            # Iterate over all the files in directory
            for folder_name, sub_folders, filenames in os.walk(base_dir):
                print(f"Ignoring folder: {folder_name}")
                for filename in filenames:
                    file_path = PurePath(folder_name, filename)
                    relative_path = file_path.relative_to(base_dir)
                    parents_set = set(map(str, relative_path.parents))
                    if not parents_set.intersection(self.ignore_dirs):
                        zip_file.write(file_path, relative_path)

        self.zipfile = zipfile

    def test(self) -> None:
        """Download the docker container, install the files, and make sure the predict function can be run."""
        example = NumpyEncoder.convert_value(self.example)
        self.copy_files(example)

        volumes = {self.volume: {"bind": self.bind_path}}
        client = docker.from_env()
        print("Building docker image...")
        image = client.images.build(path=os.path.dirname(__file__), pull=True, rm=True)[0]
        print("Creating container and testing predict function...")
        command = "{0}".format(os.path.join(self.bind_path, self.test_script))
        client.containers.run(image.id, volumes=volumes, command=command)
        print("Success!")

    def copy_files(self, example: Any) -> None:
        """Copy the files that are required for testing the docker image.

        :param: example: the example to use in the test script
        """

        explainer = os.path.join(self.volume, "explainer.pkl")
        dill.dump(self.explainer, open(explainer, 'wb'))

        if self.project_directory is None:
            raise InternalTypeError("project_directory is None")
        if self.requirements_file is None:
            raise InternalTypeError("requirements_file is None")
        requirements = os.path.join(self.volume, self.requirements_file)
        shutil.copy2(os.path.join(self.project_directory, self.requirements_file), requirements)

        test = open(os.path.join(self.volume, self.test_script), "w")
        test.write(self.create_test_script(example))
        os.chmod(os.path.join(self.volume, self.test_script), 0o755)

    def create_test_script(self, example: Any) -> str:
        """Create a test script.

        :param: example:the example to use in the test script

        :return: the script contents
        """
        script = ";".join([
            "from user_bundle.project import {0}".format(self.user_predict_function_import_path),
            "output = {0}.predict({1})".format(self.user_predict_function_import_path, example),
            "print(output)",
        ])

        return "\n".join([
            '#!/usr/bin/env bash',
            'set -e',
            'CODE_DIR="`pwd`/user_bundle"',
            'export USER_PROJECT_SOURCE_DIR="${CODE_DIR}/project"',
            'export USER_REQUIREMENTS_FILE="${CODE_DIR}/requirements.txt"',
            'export EXPLAINER_FILE="${CODE_DIR}/explainer.pkl"',
            'ENV_NAME="model-server"',
            'mkdir -p $CODE_DIR',
            'unzip -qq /mnt/{0}/project.zip -d $USER_PROJECT_SOURCE_DIR'.format(self.dirname),
            'cp /mnt/{0}/{1} $USER_REQUIREMENTS_FILE'.format(self.dirname, self.requirements_file),
            'cp /mnt/{0}/explainer.pkl $EXPLAINER_FILE'.format(self.dirname),
            'conda init bash',
            'conda create --name $ENV_NAME python=$PYTHON_VERSION --quiet',
            'source ~/.bashrc',
            'source activate $ENV_NAME',
            'pip -qq install --no-cache-dir -r $USER_REQUIREMENTS_FILE',
            'python -c "{0}"'.format(script),
        ])

    def validate_requirements_add_sklearn(self) -> List[str]:
        """Checks the user requirements file to make sure versions are correct.

        Also handles making sure scikit-learn version is pinned in user requirements
        file, if it is installed in local environment and not specified.

        scikit-learn is a dependency of shap, and arthurai doesn't require scikit-learn explicitly.
        This can lead to version A being installed and used locally when pickling explainer, then version B
        getting installed on model server as part of shap install. This can lead to pickle errors,
        since the pickled version of shap (client side) used a different version of sklearn than what is on model
        server.
        """
        if self.requirements_file is None:
            raise InternalTypeError("requirements_file is None")
        with open(self.requirements_file, 'r') as f:
            user_reqs = f.readlines()

        # build dict of installed packages and versions
        cur_env = {
            pkg.project_name: pkg.version
            for pkg in pkg_resources.working_set
        }

        errors = []

        # validate each line in user requirements file
        sklearn_found = False
        for req in user_reqs:
            req = req.replace('\n', '')
            # validate single pinned version: pandas==1.0.0
            if '==' not in req:
                errors.append(f"Invalid line in requirements file: {req}. Each dependency must have a single specific "
                              f"version pinned using '=='")
                continue
            splt = req.split('==')
            if len(splt) != 2:
                errors.append(f"Invalid line in requirements file: {req}. Each dependency must have a single specific "
                              f"version pinned using '=='")

            # flag if sklearn is already pinned in requirements file
            package, version = splt
            sklearn_found = package == 'scikit-learn'

            # validate package version matches environment
            if package not in cur_env:
                logger.warn(f"Explainability requirements file contains package not installed in current environment: "
                            f"{package}.")
            if package in cur_env and cur_env[package] != version:
                error_str = f"Explainability requirements file lists {package}=={version} but found version " \
                            f"{cur_env[package]} currently installed."
                error_str += " Packages listed in the requirements file must match the currently installed version."
                error_str += f" To resolve, update the requirements file to version {package}=={cur_env[package]}"
                errors.append(error_str)

        # insert sklearn into requirements file if necessary
        if 'scikit-learn' in cur_env and not sklearn_found:
            cur_version = cur_env['scikit-learn']
            if self.requirements_file is None:
                raise InternalTypeError("requirements_file is None")
            with open(self.requirements_file, 'a') as f:
                # ensure we add on new line
                leading_newline = '' if user_reqs[-1][-1] == '\n' else '\n'
                f.write(f"{leading_newline}scikit-learn=={cur_version}\n")
            logger.info("scikit-learn was not included in explainer requirements file, but is installed in current "
                        "environment. Automatically adding current version to requirements file. This helps ensure "
                        "correct environment on model server.")

        return errors
