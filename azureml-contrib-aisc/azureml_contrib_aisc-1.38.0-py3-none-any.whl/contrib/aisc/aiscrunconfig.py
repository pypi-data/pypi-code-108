# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for managing the configuration of experiment runs
in Azure Machine Learning.

The key class in this module is :class:`azureml.contrib.core.k8srunconfig.K8sComputeConfiguration`,
which encapsulates information necessary to submit a training run on k8s compute target."""
import collections

from azureml._base_sdk_common.field_info import _FieldInfo
from azureml._base_sdk_common.abstract_run_config_element import _AbstractRunConfigElement


class ScalePolicy(_AbstractRunConfigElement):
    """The elasticity options for a job.

    By leveraging elastic training, the job will automatically scale up when there
    is extra capacity available, and automatically scale down when resources
    are gradually called back. You should only specify auto_scale_instance_type_count_set
    or min_instance_type_count and max_instance_type_count.

    :param auto_scale_instance_type_count_set: The list of instance type counts available for elastically scaling the
        job. Assume autoScaleInstanceTypeCountSet = [2,4,8],
        the job will automatically scale down as 8->4->2 when less capacity is available,
        and scale up as 2->4->8 when more capacity is available.
    :type auto_scale_instance_type_count_set: list
    :param auto_scale_interval_in_sec: The minimum interval in seconds between job autoscaling.
        You are recommended to set the autoScaleIntervalInSec longer than the checkpoint interval,
        to make sure at least one checkpoint is saved before auto-scaling of the job.
    :type auto_scale_interval_in_sec: int
    :param max_instance_type_count: The maximum instance type count.
    :type max_instance_type_count: int
    :param min_instance_type_count: The minimum instance type count.
    :type min_instance_type_count: int
    """

    _field_to_info_dict = collections.OrderedDict([
        ("auto_scale_instance_type_count_set", _FieldInfo(list,
                                                          "The list of instance type counts available for elastically "
                                                          "scaling the job."
                                                          , list_element_type=int)),
        ("auto_scale_interval_in_sec", _FieldInfo(int, "The minimum interval in seconds between job autoscaling.")),
        ("max_instance_type_count", _FieldInfo(int, "The maximum instance type count.")),
        ("min_instance_type_count", _FieldInfo(int, "The minimum instance type count."))
    ])

    def __init__(self):
        """Class ScalePolicy constructor."""
        self.auto_scale_instance_type_count_set = None
        self.auto_scale_interval_in_sec = None
        self.max_instance_type_count = None
        self.min_instance_type_count = None


class AISuperComputerConfiguration(_AbstractRunConfigElement):
    """Represents configuration information for experiments that target AISuperComputer.

    This class is used in the :class:`azureml.core.runconfig.RunConfiguration` class.

    :param instance_type: The class of compute to be used. Supported values: Any
        `AI Super Computer size <https://aiscaasdocs.azurewebsites.net/docs/instanceseries.md>`_.
    :type instance_type: str
    :param image_version: The image version to use.
    :type image_version: str
    :param location: The location where the run will execute. Will default to workspace region if not specified.
    :type location: str
    :param interactive: Whether or not the job should be run in interactive mode. Default: False.
    :type interactive: bool
    :param scale_policy: The elasticity options for the job.
    :type scale_policy: ScalePolicy
    :param virtual_cluster_arm_id: The ARM Resource Id for the Virtual Cluster to submit the job to.
    :type virtual_cluster_arm_id: str
    :param tensorboard_log_directory: The directory where the Tensorboard logs will be written.
    :type tensorboard_log_directory: str
    :param ssh_public_key: The SSH Public Key to use when enabling SSH access to the job.
    :type ssh_public_key: str
    :param enable_azml_int: Specifies whether the job should include the azml_int utility.
    :type enable_azml_int: bool
    :param priority: The priority for the job.
    :type priority: str
    :param sla_tier: The SLA tier for the job.
    :type sla_tier: str
    """

    # This is used to deserialize.
    # This is also the order for serialization into a file.
    _field_to_info_dict = collections.OrderedDict([
        ("instance_type", _FieldInfo(str, "The class of compute to be used."
                                          "The list of instance types is available in '"
                                          "https://aiscaasdocs.azurewebsites.net/docs/instanceseries.md")
         ),
        ("image_version", _FieldInfo(str, "The image version to use.")),
        ("location", _FieldInfo(str, "The location where the run will execute.")),
        ("interactive", _FieldInfo(bool, "Whether or not the job should run in interactive mode. Default: False.")),
        ("scale_policy", _FieldInfo(ScalePolicy, "The elasticity options for the job.")),
        ("virtual_cluster_arm_id", _FieldInfo(str, "The ARM Resource Id for the Virtual Cluster.")),
        ("tensorboard_log_directory", _FieldInfo(str, "The directory where the Tensorboard logs will be written.")),
        ("ssh_public_key", _FieldInfo(str, "The SSH Public Key to use when enabling SSH access to the job.",
                                      serialized_name="SSHPublicKey")),
        ("enable_azml_int", _FieldInfo(bool, "Specifies whether the job should include the azml_int utility.")),
        ("priority", _FieldInfo(str, "The priority for the job.")),
        ("sla_tier", _FieldInfo(str, "The SLA tier for the job.", serialized_name="SLATier"))
    ])

    def __init__(self):
        """Class AISuperComputerConfiguration constructor."""
        self.instance_type = None
        self.image_version = None
        self.location = None
        self.interactive = False
        self.scale_policy = ScalePolicy()
        self.virtual_cluster_arm_id = None
        self.tensorboard_log_directory = None
        self.ssh_public_key = None
        self.enable_azml_int = False
        self.priority = None
        self.sla_tier = None
