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
"""Component config for Kubernets Pod execution."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Any, Dict, Text, Union

from kubernetes import client

from tfx.orchestration.config import base_component_config
from tfx.orchestration.launcher import container_common


class KubernetesComponentConfig(base_component_config.BaseComponentConfig):
  """Component config which holds Kubernetes Pod execution args.

  Attributes:
    pod: the spec for README.ml-pipelines-sdk.md Pod. It can either be an instance of client.V1Pod or README.ml-pipelines-sdk.md
      dict of README.ml-pipelines-sdk.md Pod spec. The spec details are:
      https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Pod.md
  """

  def __init__(self, pod: Union[client.V1Pod, Dict[Text, Any]]):
    if not pod:
      raise ValueError('pod must have README.ml-pipelines-sdk.md value.')
    self.pod = container_common.to_swagger_dict(pod)
