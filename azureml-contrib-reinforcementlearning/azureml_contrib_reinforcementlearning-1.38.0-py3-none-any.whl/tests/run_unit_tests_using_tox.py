import subprocess
import os
import sys

# Get latest pip to catch pip errors faster
subprocess.check_call(["python", "-m", "pip", "install", "-U", "pip"])

# Install and run tox. The configuration is at the top level of the module
subprocess.check_call(["python", "-m", "pip", "install", "-U", "tox"])

curdir = os.path.dirname(os.path.abspath(__file__))
aml_core_path = os.path.join(curdir, "../../azureml-core")
aml_dataset_runtime_path = os.path.join(curdir, "../../azureml-dataset-runtime")
hd_rest_client_path = os.path.join(curdir, "../../azureml-train-restclients-hyperdrive")
aml_telemetry_path = os.path.join(curdir, "../../azureml-telemetry")
aml_contrib_nb_path = os.path.join(curdir, "../../azureml-contrib-notebook")
aml_pipeline_core_path = os.path.join(curdir, "../../azureml-pipeline-core")
aml_train_core_path = os.path.join(curdir, "../../azureml-train-core")
aml_auto_core_path = os.path.join(curdir, "../../azureml-automl-core")
aml_rl_path = os.path.join(curdir, "../../azureml-contrib-reinforcementlearning")
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_core_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_dataset_runtime_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", hd_rest_client_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_telemetry_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_pipeline_core_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_train_core_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_auto_core_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_contrib_nb_path])
subprocess.check_call(["python", "-m", "pip", "install", "-e", aml_rl_path])
tox_command = ["python", "-m", "tox"]
if len(sys.argv) > 1:
    tox_command = tox_command + ["--"] + sys.argv
subprocess.check_call(tox_command)
