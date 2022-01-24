# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for managing Azure Machine Learning compute targets in Azure Machine Learning."""


from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from azureml._restclient.workspace_client import WorkspaceClient
from azureml._restclient.constants import DEFAULT_PAGE_SIZE


class AISuperComputer(ComputeTarget):
    """Manages an AI super computer in Azure Machine Learning.

    An AI Super Computer (AISuperComputer) is a managed-compute infrastructure that
    allows you to easily submit jobs to server-less compute.

    :param workspace: The workspace object containing the AISuperComputer object to retrieve.
    :type workspace: azureml.core.Workspace
    """

    _compute_type = 'Aisc'

    def __new__(cls, workspace):
        """Gets the compute target for the AISuperComputer"""
        return super(AISuperComputer, cls).__new__(cls, workspace, "aisupercomputer")

    def __init__(self, workspace):
        """Class AISuperComputer constructor.

        Retrieve a cloud representation of a Compute object associated with the provided workspace. Returns an
        instance of a child class corresponding to the specific type of the retrieved Compute object.

        :param workspace: The workspace object containing the Compute object to retrieve.
        :type workspace: azureml.core.Workspace
        :param name: The name of the of the Compute object to retrieve.
        :type name: str
        :return: An instance of :class:`azureml.core.AISuperComputer`
        :rtype: azureml.core.AISuperComputer
        :raises azureml.exceptions.ComputeTargetException:
        """
        pass

    def _initialize(self, workspace, obj_dict):
        """Initialize implementation method.

        :param workspace:
        :type workspace: azureml.core.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        name = obj_dict['name']
        compute_resource_id = MLC_COMPUTE_RESOURCE_ID_FMT.format(workspace.subscription_id, workspace.resource_group,
                                                                 workspace.name, name)
        resource_manager_endpoint = self._get_resource_manager_endpoint(workspace)
        mlc_endpoint = '{}{}'.format(resource_manager_endpoint, compute_resource_id)
        location = obj_dict['location']
        compute_type = obj_dict['properties']['computeType']
        tags = obj_dict['tags']
        description = obj_dict['properties']['description']
        created_on = obj_dict['properties'].get('createdOn')
        modified_on = obj_dict['properties'].get('modifiedOn')
        cluster_resource_id = obj_dict['properties']['resourceId']
        cluster_location = obj_dict['properties']['computeLocation'] \
            if 'computeLocation' in obj_dict['properties'] else None
        provisioning_state = obj_dict['properties']['provisioningState'] \
            if 'provisioningState' in obj_dict['properties'] else None
        provisioning_errors = obj_dict['properties']['provisioningErrors'] \
            if 'provisioningErrors' in obj_dict['properties'] else None
        is_attached = obj_dict['properties']['isAttachedCompute'] \
            if 'isAttachedCompute' in obj_dict['properties'] else None

        super(AISuperComputer, self)._initialize(compute_resource_id, name, location, compute_type, tags, description,
                                                 created_on, modified_on, provisioning_state, provisioning_errors,
                                                 cluster_resource_id, cluster_location, workspace, mlc_endpoint, None,
                                                 workspace._auth, is_attached)

    def __repr__(self):
        """Return the string representation of the AISuperComputer object.

        :return: String representation of the AISuperComputer object
        :rtype: str
        """
        return super().__repr__()

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        This method updates the properties based on the current state of the corresponding cloud object.
        This is primarily used for manual polling of compute state.
        """
        cluster = AISuperComputer(self.workspace)
        self.modified_on = cluster.modified_on

    def delete(self):
        """Delete is not supported for AISuperComputer object.

        .. remarks::

            If this object was created through Azure Machine Learning,
            the corresponding cloud based objects will also be deleted. If this object was created externally and only
            attached to the workspace, it will raise exception and nothing will be changed.

        :raises: :class:`azureml.exceptions.ComputeTargetException`
        """
        raise ComputeTargetException('Delete is not supported for AISuperComputer object.')

    def detach(self):
        """Detach is not supported for AISuperComputer object.

        :raises azureml.exceptions.ComputeTargetException:
        """
        raise ComputeTargetException('Detach is not supported for AISuperComputer object.')

    def serialize(self):
        """Convert this AISuperComputer object into a JSON serialized dictionary.

        :return: The JSON representation of this AISuperComputer object.
        :rtype: dict
        """
        created_on = self.created_on.isoformat() if self.created_on else None
        modified_on = self.modified_on.isoformat() if self.modified_on else None
        return {'id': self.id, 'name': self.name, 'location': self.location, 'tags': self.tags,
                'description': self.description, 'created_on': created_on, 'modified_on': modified_on}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a JSON object into an AISuperComputer object.

        .. remarks::

            Raises a :class:`azureml.exceptions.ComputeTargetException` if the provided
            workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the AISuperComputer object is associated with.
        :type workspace: azureml.core.Workspace
        :param object_dict: A JSON object to convert to an AISuperComputer object.
        :type object_dict: dict
        :return: The AISuperComputer representation of the provided JSON object.
        :rtype: azureml.core.compute.aisupercomputer.AISuperComputer
        :raises azureml.exceptions.ComputeTargetException:
        """
        AISuperComputer._validate_get_payload(object_dict)
        target = AISuperComputer(workspace)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))

    def get(self):
        """Return compute object."""
        return ComputeTarget._get(self.workspace, self.name)

    def get_active_runs(self, instance_type=None, type=None, tags=None, properties=None, status=None):
        """Return a generator of the runs for this compute.

        :param instance_type: Filters the returned generator of runs by the instance type.
        :type instance_type: str
        :param type: Filter the returned generator of runs by the provided type. See
            :func:`azureml.core.Run.add_type_provider` for creating run types.
        :type type: str
        :param tags: Filter runs by "tag" or {"tag": "value"}
        :type tags: str or dict
        :param properties: Filter runs by "property" or {"property": "value"}
        :type properties: str or dict
        :param status: Run status - either "Running" or "Queued"
        :type status: str
        :return: a generator of ~_restclient.models.RunDto
        :rtype: builtin.generator
        """
        workspace_client = WorkspaceClient(self.workspace.service_context)
        return workspace_client.get_runs_by_compute(self.name,
                                                    0,
                                                    DEFAULT_PAGE_SIZE,
                                                    None,
                                                    None,
                                                    type=type,
                                                    tags=tags,
                                                    properties=properties,
                                                    status=status)
