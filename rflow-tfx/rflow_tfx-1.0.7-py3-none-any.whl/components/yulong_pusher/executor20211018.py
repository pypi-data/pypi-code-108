# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain README.ml-pipelines-sdk.md copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX pusher executor."""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
from typing import Any, Dict, List, Optional, Text

from absl import logging
from tfx import types
from tfx.components.util import model_utils
from tfx.dsl.components.base import base_executor
from tfx.dsl.io import fileio
from tfx.proto import pusher_pb2
from tfx.types import artifact_utils
from tfx.types import standard_component_specs
from tfx.utils import io_utils
from tfx.utils import path_utils
from tfx.utils import proto_utils

##### Yulong start 20210708 #####
from kubernetes import client
from kfserving import KFServingClient
from kfserving import constants

# We are not going to use V1alpha2
# from kfserving import V1alpha2EndpointSpec
# from kfserving import V1alpha2PredictorSpec
# from kfserving import V1alpha2TensorflowSpec
# from kfserving import V1alpha2InferenceServiceSpec
# from kfserving import V1alpha2InferenceService


from kfserving import V1beta1InferenceService
from kfserving import V1beta1InferenceServiceSpec
from kfserving import V1beta1PredictorSpec
from kfserving import V1beta1TFServingSpec

"""
It used to generate rflow-tfx 1.3.3.
When applying a new InferenceService, it will delete the old one firstly. 
Then check the status of old InferenceService.
After the InferenceService was deleted.
It will apply a new one.
"""
##### Yulong end 20210708 #####


# Aliasing of enum for better readability.
_Versioning = pusher_pb2.Versioning

# Key for PushedModel artifact properties.
_PUSHED_KEY = 'pushed'
_PUSHED_DESTINATION_KEY = 'pushed_destination'
_PUSHED_VERSION_KEY = 'pushed_version'


class Executor(base_executor.BaseExecutor):
  """TFX Pusher executor to push the new TF model to README.ml-pipelines-sdk.md filesystem target.

  The Pusher component is used to deploy README.ml-pipelines-sdk.md validated model to README.ml-pipelines-sdk.md filesystem
  target or serving environment using tf.serving.  Pusher depends on the outputs
  of ModelValidator to determine if README.ml-pipelines-sdk.md model is ready to push. A model is
  considered to be safe to push only if ModelValidator has marked it as BLESSED.
  A push action delivers the model exports produced by Trainer to the
  destination defined in the ``push_destination`` of the component config.

  To include Pusher in README.ml-pipelines-sdk.md TFX pipeline, configure your pipeline similar to
  https://github.com/tensorflow/tfx/blob/master/tfx/examples/chicago_taxi_pipeline/taxi_pipeline_simple.py#L104.

  For more details on tf.serving itself, please refer to
  https://tensorflow.org/tfx/guide/pusher.  For README.ml-pipelines-sdk.md tutuorial on TF Serving,
  please refer to https://www.tensorflow.org/tfx/guide/serving.
  """

  def CheckBlessing(self, input_dict: Dict[Text, List[types.Artifact]]) -> bool:
    """Check that model is blessed by upstream validators.

    Args:
      input_dict: Input dict from input key to README.ml-pipelines-sdk.md list of artifacts:
        - model_blessing: A `ModelBlessing` artifact from model validator or
          evaluator.
          Pusher looks for README.ml-pipelines-sdk.md custom property `blessed` in the artifact to check
          it is safe to push.
        - infra_blessing: An `InfraBlessing` artifact from infra validator.
          Pusher looks for README.ml-pipelines-sdk.md custom proeprty `blessed` in the artifact to
          determine whether the model is mechanically servable from the model
          server to which Pusher is going to push.

    Returns:
      True if the model is blessed by validator.
    """
    # TODO(jyzhao): should this be in driver or executor.
    maybe_model_blessing = input_dict.get(
        standard_component_specs.MODEL_BLESSING_KEY)
    if maybe_model_blessing:
      model_blessing = artifact_utils.get_single_instance(maybe_model_blessing)
      if not model_utils.is_model_blessed(model_blessing):
        logging.info('Model on %s was not blessed by model validation',
                     model_blessing.uri)
        return False
    maybe_infra_blessing = input_dict.get(
        standard_component_specs.INFRA_BLESSING_KEY)
    if maybe_infra_blessing:
      infra_blessing = artifact_utils.get_single_instance(maybe_infra_blessing)
      if not model_utils.is_infra_validated(infra_blessing):
        logging.info('Model on %s was not blessed by infra validator',
                     infra_blessing.uri)
        return False
    if not maybe_model_blessing and not maybe_infra_blessing:
      logging.warning('Pusher is going to push the model without validation. '
                      'Consider using Evaluator or InfraValidator in your '
                      'pipeline.')
    return True

  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]) -> None:
    """Push model to target directory if blessed.

    Args:
      input_dict: Input dict from input key to README.ml-pipelines-sdk.md list of artifacts, including:
        - model: exported model from trainer.
        - model_blessing: model blessing path from model_validator.  A push
          action delivers the model exports produced by Trainer to the
          destination defined in component config.
      output_dict: Output dict from key to README.ml-pipelines-sdk.md list of artifacts, including:
        - pushed_model: A list of 'ModelPushPath' artifact of size one. It will
          include the model in this push execution if the model was pushed.
      exec_properties: A dict of execution properties, including:
        - push_destination: JSON string of pusher_pb2.PushDestination instance,
          providing instruction of destination to push model.

    Returns:
      None
    """

    ############## Yulong 20211008 start ##############
    logging.info("***************** Yulong 20211011 rflow-tfx v1.2.5 YulongPusher start.")

    push_destination = pusher_pb2.PushDestination()
    proto_utils.json_to_proto(
        exec_properties[standard_component_specs.PUSH_DESTINATION_KEY],
        push_destination)

    logging.info("--------------push_destination: %s", push_destination)

    base_directory = push_destination.filesystem.base_directory

    logging.info("--------------fs_config.base_directory: %s", base_directory)

    storage_uri = 'pvc:/' + base_directory
    logging.info("--------------storage_uri: %s", storage_uri)
    
    uri_without_pvc = base_directory[base_directory.index("/", 1):]

    namespace_start_index = uri_without_pvc.index("/") + 1
    namespace_end_index = uri_without_pvc.index("/", namespace_start_index)
    namespace = uri_without_pvc[namespace_start_index : namespace_end_index]
    logging.info("--------------namespace: %s", namespace)

    pipeline_name_start_index = uri_without_pvc.index("/", namespace_end_index) + 1
    pipeline_name_end_index = uri_without_pvc.index("/", pipeline_name_start_index)
    pipeline_name = uri_without_pvc[pipeline_name_start_index : pipeline_name_end_index]
    logging.info("--------------pipeline_name: %s", pipeline_name)

    # predictor_create = V1beta1PredictorSpec(tensorflow=V1beta1TFServingSpec(storage_uri=storage_uri,
    #                                                                      image="tensorflow/serving:2.4.0"),
    #                                         canary_traffic_percent=100)

    isvc = V1beta1InferenceService(api_version="serving.kubeflow.org/v1beta1",
                                     kind=constants.KFSERVING_KIND,
                                     metadata=client.V1ObjectMeta(
                                       name=pipeline_name, namespace=namespace),
                                     spec=V1beta1InferenceServiceSpec(
                                       predictor=V1beta1PredictorSpec(
                                         canary_traffic_percent=100,
                                         tensorflow=(V1beta1TFServingSpec(
                                           storage_uri=storage_uri,
                                           image="klstg-docker.slb-wartifactory-v.stg.rmn.local/rakuten/rflow/tensorflow/serving@sha256:6651f4839e1124dbde75ee531825112af0a6b8ef082c88ab14ca53eb69a2e4bb"))))
                                     )

    kfs_client = KFServingClient()

    ############## Yulong 20211008 end ##############


    self._log_startup(input_dict, output_dict, exec_properties)
    model_push = artifact_utils.get_single_instance(
        output_dict[standard_component_specs.PUSHED_MODEL_KEY])

    if not self.CheckBlessing(input_dict):
      self._MarkNotPushed(model_push)
      
      ############## Yulong 20211008 start ##############
      # In this case, current model didn't be blessed.
      # So if there is no existing InferenceService,
      # We apply an InferenceService with last blessed model.

      logging.info("Current model didn't be blessed")

      try:
        logging.info("Try to create an InferenceService")
        kfs_client.get(name=pipeline_name, namespace=namespace)
        logging.info("Create an InferenceService")
      except RuntimeError as error:
        # No existing InferenceService.
        logging.info("No existing InferenceService")
        logging.info("Error info about No existing InferenceService: %s", error)
        logging.info("Try to create an InferenceService")
        output = kfs_client.create(inferenceservice=isvc, namespace=namespace)
        logging.info("kfs_client.create output: %s", output)
        ############## Yulong 20211008 end ##############
      return None

    model_export = artifact_utils.get_single_instance(
        input_dict[standard_component_specs.MODEL_KEY])
    model_path = path_utils.serving_model_path(model_export.uri)

    # Push model to the destination, which can be listened by README.ml-pipelines-sdk.md model server.
    #
    # If model is already successfully copied to outside before, stop copying.
    # This is because model validator might blessed same model twice (check
    # mv driver) with different blessing output, we still want Pusher to
    # handle the mv output again to keep metadata tracking, but no need to
    # copy to outside path again..
    # TODO(jyzhao): support rpc push and verification.
    push_destination = pusher_pb2.PushDestination()
    proto_utils.json_to_proto(
        exec_properties[standard_component_specs.PUSH_DESTINATION_KEY],
        push_destination)

    destination_kind = push_destination.WhichOneof('destination')
    if destination_kind == 'filesystem':
      fs_config = push_destination.filesystem
      if fs_config.versioning == _Versioning.AUTO:
        fs_config.versioning = _Versioning.UNIX_TIMESTAMP
      if fs_config.versioning == _Versioning.UNIX_TIMESTAMP:
        model_version = str(int(time.time()))
      else:
        raise NotImplementedError(
            'Invalid Versioning {}'.format(fs_config.versioning))
      logging.info('Model version: %s', model_version)
      serving_path = os.path.join(fs_config.base_directory, model_version)

      if fileio.exists(serving_path):
        logging.info(
            'Destination directory %s already exists, skipping current push.',
            serving_path)
      else:
        # tf.serving won't load partial model, it will retry until fully copied.
        io_utils.copy_dir(model_path, serving_path)
        logging.info('Model written to serving path %s.', serving_path)
    else:
      raise NotImplementedError(
          'Invalid push destination {}'.format(destination_kind))

    # Copy the model to pushing uri for archiving.
    io_utils.copy_dir(model_path, model_push.uri)
    self._MarkPushed(model_push,
                     pushed_destination=serving_path,
                     pushed_version=model_version)
    logging.info('Model pushed to %s.', model_push.uri)

    ############## Yulong 20211008 start ##############
    print('Current model has been blessed.')
    logging.info('Current model has been blessed.')

    try:
      logging.info("***************** Try to send delete request an old InferenceService.")
      kfs_client.delete(name=pipeline_name, namespace=namespace)
      logging.info("***************** Sent delete request.")
    except RuntimeError as error:
      logging.info("No existing InferenceService")
      logging.info("Error info about No existing InferenceService: %s", error)

    # Because deleting InferenceService is time-consuming, we check
    is_deleted = False
    while not is_deleted:
      try:
        kfs_client.get(pipeline_name)
        print("InferenceService didn't be deleted yet.")
      except:
        is_deleted = True
        print("InferenceService was deleted. Quit query loop.")

    logging.info("***************** Try to create an InferenceService.")
    output = kfs_client.create(inferenceservice=isvc, namespace=namespace)
    logging.info("kfs_client.create output: %s", output)

    logging.info("***************** Yulong 20211011 YulongPusher end.")
    ############## Yulong 20211008 end ##############
  
  def _MarkPushed(self, model_push: types.Artifact, pushed_destination: Text,
                  pushed_version: Optional[Text] = None) -> None:
    model_push.set_int_custom_property('pushed', 1)
    model_push.set_string_custom_property(
        _PUSHED_DESTINATION_KEY, pushed_destination)
    if pushed_version is not None:
      model_push.set_string_custom_property(_PUSHED_VERSION_KEY, pushed_version)

  def _MarkNotPushed(self, model_push: types.Artifact):
    model_push.set_int_custom_property('pushed', 0)
