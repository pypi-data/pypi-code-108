# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML pipeline step to run a Kusto notebook."""
from azureml.pipeline.core._kusto_step_base import _KustoStepBase


class KustoStep(_KustoStepBase):
    """
    KustoStep enables the functionality of running Kusto queries on a target Kusto cluster in Azure ML Pipelines.

    :param name: Name of the step
    :type name: str
    :param compute_target: Name of the Kusto compute
    :type compute_target: str
    :param database_name: Name of the Kusto database to query from
    :type database_name: str
    :param query_directory: Path to directory that contains a single file with Kusto query
    :type query_directory: str
    :param output: Output port definition for outputs produced by this step
    :type output: typing.Union[azureml.pipeline.core.builder.PipelineData,
        azureml.pipeline.core.graph.OutputPortBinding]
    :param parameter_dict: Dictionary that maps the parameter name to parameter value in Kusto query
    :type parameter_dict: dict
    :param allow_reuse: Boolean that indicates whether the step should reuse previous results with same settings/inputs
    :type allow_reuse: bool
    """

    def __init__(self, name, compute_target, database_name, query_directory, output,
                 parameter_dict=None, allow_reuse=False):
        """
        Initialize KustoStep.

        :param name: Name of the step
        :type name: str
        :param compute_target: Name of the Kusto compute
        :type compute_target: str
        :param database_name: Name of the Kusto database to query from
        :type database_name: str
        :param query_directory: Path to directory that contains a single file with Kusto query
        :type query_directory: str
        :param output: Output port definition for outputs produced by this step
        :type output: typing.Union[azureml.pipeline.core.builder.PipelineData,
            azureml.pipeline.core.graph.OutputPortBinding]
        :param parameter_dict: Dictionary that maps the parameter name to parameter value in Kusto query
        :type parameter_dict: dict[str, object]
        :param allow_reuse: Boolean that indicates whether the step should reuse previous results
            with same settings/inputs
        :type allow_reuse: bool
        """
        super(KustoStep, self).__init__(name=name, compute_target=compute_target, database_name=database_name,
                                        query_directory=query_directory, output=output, parameter_dict=parameter_dict,
                                        allow_reuse=allow_reuse)

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the Kusto step.
        :rtype: str
        """
        result = "KustoStep_{0}".format(self.name)
        return result

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the Kusto step.
        :rtype: str
        """
        return self.__str__()

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the Kusto step and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(KustoStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                  context=context)
