# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML pipeline step to run a Databricks notebook or Python script on DBFS."""
from azureml.pipeline.core._databricks_step_base import _DatabricksStepBase


class DatabricksStep(_DatabricksStepBase):
    r"""Creates an Azure ML Pipeline step to add a DataBricks notebook, Python script, or JAR as a node.

    For an example of using DatabricksStep, see the notebook https://aka.ms/pl-databricks.

    :param name: [Required] The name of the step.
    :type name: str
    :param inputs: A list of input connections for data consumed by this step. Fetch this inside the notebook
                    using dbutils.widgets.get("input_name"). Can be DataReference or PipelineData. DataReference
                    represents an existing piece of data on a datastore. Essentially this is a path on a
                    datastore. DatabricksStep supports datastores that encapsulates DBFS, Azure blob, or ADLS v1.
                    PipelineData represents intermediate data produced by another step in a pipeline.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData]]
    :param outputs: A list of output port definitions for outputs produced by this step. Fetch this inside the
                    notebook using dbutils.widgets.get("output_name"). Should be PipelineData.
    :type outputs: list[typing.Union[azureml.pipeline.core.graph.OutputPortBinding,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.pipeline.core.builder.PipelineData]]
    :param existing_cluster_id: A cluster ID of an existing interactive cluster on the Databricks workspace.
        If you are passing this parameter, you cannot pass any of the following parameters which are used to
        create a new cluster:
        -   spark_version
        -   node_type
        -   instance_pool_id
        -   num_workers
        -   min_workers
        -   max_workers
        -   spark_env_variables
        -   spark_conf

        Note: For creating a new job cluster, you will need to pass the above parameters. You can pass
        these parameters directly or you can pass them as part of the RunConfiguration object using the
        runconfig parameter. Passing these parameters directly and through RunConfiguration results in
        an error.
    :type existing_cluster_id: str
    :param spark_version: The version of spark for the Databricks run cluster, for example: "4.0.x-scala2.11".
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type spark_version: str
    :param node_type: [Required] The Azure VM node types for the Databricks run cluster,
        for example: "Standard_D3_v2". Specify either ``node_type`` or ``instance_pool_id``.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type node_type: str
    :param instance_pool_id: [Required] The instance pool ID to which the cluster needs to be attached to.
        Specify either ``node_type`` or ``instance_pool_id``.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type instance_pool_id: str
    :param num_workers: [Required] The static number of workers for the Databricks run cluster.
        You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type num_workers: int
    :param min_workers: [Required] The min number of workers to use for auto-scaling the Databricks run cluster.
        You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type min_workers: int
    :param max_workers: [Required] The max number of workers to use for auto-scaling the Databricks run cluster.
        You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type max_workers: int
    :param spark_env_variables: The spark environment variables for the Databricks run cluster.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type spark_env_variables: dict
    :param spark_conf: The spark configuration for the Databricks run cluster.
        For more information, see the description for the ``existing_cluster_id`` parameter.
    :type spark_conf: dict
    :param init_scripts: The DBFS paths to init scripts for the new cluster.
    :type init_scripts: [str]
    :param cluster_log_dbfs_path: The DBFS paths where clusters logs are to be delivered.
    :type cluster_log_dbfs_path: str
    :param notebook_path: [Required] The path to the notebook in the Databricks instance. This class allows
        four ways of specifying the code to execute on the Databricks cluster.

                          1. To execute a notebook that is present in the Databricks workspace, use:
                             notebook_path=notebook_path,
                             notebook_params={'myparam': 'testparam'}
                          2. To execute a Python script that is present in DBFS, use:
                             python_script_path=python_script_dbfs_path,
                             python_script_params={'arg1', 'arg2'}
                          3. To execute a JAR that is present in DBFS, use:
                             main_class_name=main_jar_class_name, jar_params={'arg1', 'arg2'},
                             jar_libraries=[JarLibrary(jar_library_dbfs_path)]
                          4. To execute a Python script that is present on your local machine, use:
                             python_script_name=python_script_name,
                             source_directory=source_directory

        Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
        or ``main_class_name``.
    :type notebook_path: str
    :param notebook_params: A dictionary of parameters to pass to the notebook. ``notebook_params``
        are available as widgets. You can fetch the values from these widgets inside your notebook
        using `dbutils.widgets.get("myparam")`.
    :type notebook_params: dict[str, typing.Union[str, azureml.pipeline.core.PipelineParameter]]
    :param python_script_path: [Required] The path to the python script in the DBFS.
        Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
        or ``main_class_name``.
    :type python_script_path: str
    :param python_script_params: Parameters for the Python script.
    :type python_script_params: list[str, azureml.pipeline.core.PipelineParameter]
    :param main_class_name: [Required] The name of the entry point in a JAR module.
        Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
        or ``main_class_name``.
    :type main_class_name: str
    :param jar_params: Parameters for the JAR module.
    :type jar_params: list[str, azureml.pipeline.core.PipelineParameter]
    :param python_script_name: [Required] The name of a Python script relative to ``source_directory``.
        If the script takes inputs and outputs, those will be passed to the script as parameters.
        If ``python_script_name`` is specified then ``source_directory`` must be too.

        Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
        or ``main_class_name``.

        If you specify a DataReference object as input with `data_reference_name=input1` and a
        PipelineData object as output with `name=output1`, then the inputs and outputs will be passed to the script
        as parameters. This is how they will look like and you will need to parse the arguments
        in your script to access the paths of each input and output:
        `"-input1","wasbs://test@storagename.blob.core.windows.net/test","-output1",
        "wasbs://test@storagename.blob.core.windows.net/b3e26de1-87a4-494d-a20f-1988d22b81a2/output1"`

        In addition, the following parameters will be available within the script:
        -   AZUREML_RUN_TOKEN: The AML token for authenticating with Azure Machine Learning.
        -   AZUREML_RUN_TOKEN_EXPIRY: The AML token expiry time.
        -   AZUREML_RUN_ID: Azure Machine Learning Run ID for this run.
        -   AZUREML_ARM_SUBSCRIPTION: Azure subscription for your AML workspace.
        -   AZUREML_ARM_RESOURCEGROUP: Azure resource group for your Azure Machine Learning workspace.
        -   AZUREML_ARM_WORKSPACE_NAME: Name of your Azure Machine Learning workspace.
        -   AZUREML_ARM_PROJECT_NAME: Name of your Azure Machine Learning experiment.
        -   AZUREML_SERVICE_ENDPOINT: The endpoint URL for AML services.
        -   AZUREML_WORKSPACE_ID: ID of your Azure Machine Learning workspace.
        -   AZUREML_EXPERIMENT_ID: ID of your Azure Machine Learning experiment.
        -   AZUREML_SCRIPT_DIRECTORY_NAME: Directory path in DBFS where source_directory has been copied.
        (This parameter is only populated when ``python_script_name`` is used.  See more details below.)

        When you are executing a Python script from your local machine on Databricks using DatabricksStep
        parameters ``source_directory`` and ``python_script_name``, your source_directory is copied over to DBFS
        and the directory path on DBFS is passed as a parameter to your script when it begins execution.
        This parameter is labelled as --AZUREML_SCRIPT_DIRECTORY_NAME. You need to prefix it with the
        string "dbfs:/" or "/dbfs/" to access the directory in DBFS.
    :type python_script_name: str
    :param source_directory: The folder that contains the script and other files.
        If ``python_script_name`` is specified then ``source_directory`` must be too.
    :type source_directory: str
    :param hash_paths: DEPRECATED: no longer needed.

        A list of paths to hash when checking for changes to the step contents. If there
        are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
        the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
    :type hash_paths: [str]
    :param run_name: The name in Databricks for this run.
    :type run_name: str
    :param timeout_seconds: The timeout for the Databricks run.
    :type timeout_seconds: int
    :param runconfig: The runconfig to use.

        Note: You can pass as many libraries as you like as dependencies to your job
        using the following parameters: ``maven_libraries``, ``pypi_libraries``, ``egg_libraries``,
        ``jar_libraries``, or ``rcran_libraries``. Either pass these parameters directly with their
        corresponding parameters or as part of the RunConfiguration object using the ``runconfig``
        parameter, but not both.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param maven_libraries: Maven libraries to use for the Databricks run.
    :type maven_libraries: list[azureml.core.databricks.MavenLibrary]
    :param pypi_libraries: PyPi libraries to use for the Databricks run.
    :type pypi_libraries: list[azureml.core.databricks.PyPiLibrary]
    :param egg_libraries: Egg libraries to use for the Databricks run.
    :type egg_libraries: list[azureml.core.databricks.EggLibrary]
    :param jar_libraries: Jar libraries to use for the Databricks run.
    :type jar_libraries: list[azureml.core.databricks.JarLibrary]
    :param rcran_libraries: RCran libraries to use for the Databricks run.
    :type rcran_libraries: list[azureml.core.databricks.RCranLibrary]
    :param compute_target: [Required] An Azure Databricks compute. Before you can use DatabricksStep
        to execute your scripts or notebooks on an Azure Databricks workspace, you need to add the
        Azure Databricks workspace as a compute target to your Azure Machine Learning workspace.
    :type compute_target: str, azureml.core.compute.DatabricksCompute
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the step.
    :type version: str
    :param permit_cluster_restart: if existing_cluster_id is specified, this parameter tells whether cluster
        can be restarted on behalf of user.
    :type permit_cluster_restart: bool
    """

    def __init__(self, name, inputs=None, outputs=None, existing_cluster_id=None, spark_version=None,
                 node_type=None, instance_pool_id=None, num_workers=None, min_workers=None, max_workers=None,
                 spark_env_variables=None, spark_conf=None, init_scripts=None, cluster_log_dbfs_path=None,
                 notebook_path=None, notebook_params=None, python_script_path=None, python_script_params=None,
                 main_class_name=None, jar_params=None, python_script_name=None, source_directory=None,
                 hash_paths=None, run_name=None, timeout_seconds=None, runconfig=None, maven_libraries=None,
                 pypi_libraries=None, egg_libraries=None, jar_libraries=None, rcran_libraries=None,
                 compute_target=None, allow_reuse=True, version=None, permit_cluster_restart=None):
        """Create an Azure ML Pipeline step to add a DataBricks notebook, Python script, or JAR as a node.

        For an example of using DatabricksStep, see the notebook https://aka.ms/pl-databricks.

        :param name: [Required] The name of the step.
        :type name: str
        :param inputs: List of input connections for data consumed by this step. Fetch this inside the notebook
                        using dbutils.widgets.get("input_name"). Can be DataReference or PipelineData. DataReference
                        represents an existing piece of data on a datastore. Essentially this is a path on a
                        datastore. DatabricksStep supports datastores that encapsulates DBFS, Azure blob or ADLS v1.
                        PipelineData represents intermediate data produced by another step in a pipeline.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference,
                        azureml.pipeline.core.builder.PipelineData]]
        :param outputs: A list of output port definitions for outputs produced by this step. Fetch this inside the
                        notebook using dbutils.widgets.get("output_name"). Should be PipelineData.
        :type outputs: list[typing.Union[azureml.pipeline.core.graph.OutputPortBinding,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset,
                        azureml.pipeline.core.builder.PipelineData]]
        :param existing_cluster_id: A cluster ID of an existing interactive cluster on the Databricks workspace.
            If you are passing this parameter, you cannot pass any of the following parameters which are used to
            create a new cluster:
            -   spark_version
            -   node_type
            -   instance_pool_id
            -   num_workers
            -   min_workers
            -   max_workers
            -   spark_env_variables
            -   spark_conf

            Note: For creating a new job cluster, you will need to pass the above parameters. You can pass
            these parameters directly or you can pass them as part of the RunConfiguration object using the
            runconfig parameter. Passing these parameters directly and through RunConfiguration results in
            an error.
        :type existing_cluster_id: str
        :param spark_version: The version of spark for the Databricks run cluster, for example: "4.0.x-scala2.11".
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type spark_version: str
        :param node_type: [Required] The Azure VM node types for the Databricks run cluster,
            for example: "Standard_D3_v2". Specify either ``node_type`` or ``instance_pool_id``.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type node_type: str
        :param instance_pool_id: [Required] The instance pool ID to which the cluster needs to be attached to.
            Specify either ``node_type`` or ``instance_pool_id``.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type instance_pool_id: str
        :param num_workers: [Required] The static number of workers for the Databricks run cluster.
                            You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type num_workers: int
        :param min_workers: [Required] The min number of workers to use for auto-scaling the Databricks run cluster.
                            You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type min_workers: int
        :param max_workers: [Required] The max number of workers to use for auto-scaling the Databricks run cluster.
                            You must specify either ``num_workers`` or both ``min_workers`` and ``max_workers``.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type max_workers: int
        :param spark_env_variables: The spark environment variables for the Databricks run cluster.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type spark_env_variables: dict
        :param spark_conf: The spark configuration for the Databricks run cluster.
            For more information, see the description for the ``existing_cluster_id`` parameter.
        :type spark_conf: dict
        :param init_scripts: The DBFS paths to init scripts for the new cluster.
        :type init_scripts: [str]
        :param cluster_log_dbfs_path: The DBFS paths where clusters logs are to be delivered.
        :type cluster_log_dbfs_path: str
        :param notebook_path: [Required] The path to the notebook in the Databricks instance.
            This class allows four ways of specifying the code to execute on the Databricks cluster.

                            1. To execute a notebook that is present in the Databricks workspace, use:
                               notebook_path=notebook_path,
                               notebook_params={'myparam': 'testparam'}
                            2. To execute a Python script that is present in DBFS, use:
                               python_script_path=python_script_dbfs_path,
                               python_script_params={'arg1', 'arg2'}
                            3. To execute a JAR that is present in DBFS, use:
                               main_class_name=main_jar_class_name, jar_params={'arg1', 'arg2'},
                               jar_libraries=[JarLibrary(jar_library_dbfs_path)]
                            4. To execute a Python script that is present on your local machine, use:
                               python_script_name=python_script_name,
                               source_directory=source_directory
            Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
            or ``main_class_name``.
        :type notebook_path: str
        :param notebook_params: A dictionary of parameters to pass to the notebook. ``notebook_params``
            are available as widgets. You can fetch the values from these widgets inside your notebook
            using `dbutils.widgets.get("myparam")`.
        :type notebook_params: dict[str, (str or azureml.pipeline.core.PipelineParameter)]
        :param python_script_path: [Required] The path to the python script in the DBFS.
            Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
            or ``main_class_name``.
        :type python_script_path: str
        :param python_script_params: Parameters for the Python script.
        :type python_script_params: list[str, azureml.pipeline.core.PipelineParameter]
        :param main_class_name: [Required] The name of the entry point in a JAR module.
            Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
            or ``main_class_name``.
        :type main_class_name: str
        :param jar_params: Parameters for the JAR module.
        :type jar_params: list[str, azureml.pipeline.core.PipelineParameter]
        :param python_script_name:[Required] The name of a Python script relative to ``source_directory``.
            If the script takes inputs and outputs, those will be passed to the script as parameters.
            If ``python_script_name`` is specified then ``source_directory`` must be too.

            Specify exactly one of ``notebook_path``, ``python_script_path``, ``python_script_name``,
            or ``main_class_name``.

            If you specify a DataReference object as input with `data_reference_name=input1` and a
            PipelineData object as output with `name=output1`, then the inputs and outputs will be passed to the script
            as parameters. This is how they will look like and you will need to parse the arguments
            in your script to access the paths of each input and output:
            `"-input1","wasbs://test@storagename.blob.core.windows.net/test","-output1",
            "wasbs://test@storagename.blob.core.windows.net/b3e26de1-87a4-494d-a20f-1988d22b81a2/output1"`

            In addition, the following parameters will be available within the script:
            -   AZUREML_RUN_TOKEN: The AML token for authenticating with Azure Machine Learning.
            -   AZUREML_RUN_TOKEN_EXPIRY: The AML token expiry time.
            -   AZUREML_RUN_ID: Azure Machine Learning Run ID for this run.
            -   AZUREML_ARM_SUBSCRIPTION: Azure subscription for your AML workspace.
            -   AZUREML_ARM_RESOURCEGROUP: Azure resource group for your Azure Machine Learning workspace.
            -   AZUREML_ARM_WORKSPACE_NAME: Name of your Azure Machine Learning workspace.
            -   AZUREML_ARM_PROJECT_NAME: Name of your Azure Machine Learning experiment.
            -   AZUREML_SERVICE_ENDPOINT: The endpoint URL for AML services.
            -   AZUREML_WORKSPACE_ID: ID of your Azure Machine Learning workspace.
            -   AZUREML_EXPERIMENT_ID: ID of your Azure Machine Learning experiment.
            -   AZUREML_SCRIPT_DIRECTORY_NAME: Directory path in DBFS where source_directory has been copied.
                (This parameter is only populated when ``python_script_name`` is used.  See more details below.)

            When you are executing a Python script from your local machine on Databricks using DatabricksStep
            parameters ``source_directory`` and ``python_script_name``, your source_directory is copied over to DBFS
            and the directory path on DBFS is passed as a parameter to your script when it begins execution.
            This parameter is labelled as --AZUREML_SCRIPT_DIRECTORY_NAME. You need to prefix it with the
            string "dbfs:/" or "/dbfs/" to access the directory in DBFS.
        :type python_script_name: str
        :param source_directory: The folder that contains the script and other files.
            If ``python_script_name`` is specified then ``source_directory`` must be too.
        :type source_directory: str
        :param hash_paths: DEPRECATED: no longer needed.

            A list of paths to hash when checking for changes to the step contents. If there
            are no changes detected, the pipeline will reuse the step contents from a previous run. By default,
            the contents of ``source_directory`` is hashed except for files listed in .amlignore or .gitignore.
        :type hash_paths: [str]
        :param run_name: The name in Databricks for this run.
        :type run_name: str
        :param timeout_seconds: The timeout for the Databricks run.
        :type timeout_seconds: int
        :param runconfig: The runconfig to use.

            Note: You can pass as many libraries as you like as dependencies to your job
            using the following parameters: ``maven_libraries``, ``pypi_libraries``, ``egg_libraries``,
            ``jar_libraries``, or ``rcran_libraries``. Either pass these parameters directly with their
            corresponding parameters or as part of the RunConfiguration object using the ``runconfig``
            parameter, but not both.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param maven_libraries: Maven libraries to use for the Databricks run.
            For more information on the specification of Maven libraries,
            see ``help(azureml.core.runconfig.MavenLibrary)``.
        :type maven_libraries: list[azureml.core.runconfig.MavenLibrary]
        :param pypi_libraries: PyPi libraries to use for the Databricks run.
            For more information on the specification of PyPi libraries,
            see ``help(azureml.core.runconfig.PyPiLibrary)``.
        :type pypi_libraries: list[azureml.core.runconfig.PyPiLibrary]
        :param egg_libraries: Egg libraries to use for the Databricks run.
            For more information on the specification of Egg libraries,
            see ``help(azureml.core.runconfig.EggLibrary)``.
        :type egg_libraries: list[azureml.core.runconfig.EggLibrary]
        :param jar_libraries: Jar libraries to use for the Databricks run.
            For more information on the specification of Jar libraries,
            see ``help(azureml.core.runconfig.JarLibrary)``.
        :type jar_libraries: list[azureml.core.runconfig.JarLibrary]
        :param rcran_libraries: RCran libraries to use for the Databricks run.
            For more information on the specification of RCran libraries,
            see ``help(azureml.core.runconfig.RCranLibrary)``.
        :type rcran_libraries: list[azureml.core.runconfig.RCranLibrary]
        :param compute_target: [Required] Azure Databricks compute. Before you can use DatabricksStep
            to execute your scripts or notebooks on an Azure Databricks workspace, you need to add the
            Azure Databricks workspace as a compute target to your Azure Machine Learning workspace.
        :type compute_target: str, azureml.core.compute.DatabricksCompute
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the step.
        :type version: str
        :param permit_cluster_restart: if existing_cluster_id is specified, this parameter tells whether cluster
            can be restarted on behalf of user.
        :type permit_cluster_restart: bool
        """
        super(DatabricksStep, self).__init__(
            name=name, inputs=inputs, outputs=outputs, existing_cluster_id=existing_cluster_id,
            spark_version=spark_version,
            node_type=node_type, instance_pool_id=instance_pool_id, num_workers=num_workers, min_workers=min_workers,
            max_workers=max_workers, spark_env_variables=spark_env_variables, spark_conf=spark_conf,
            init_scripts=init_scripts, cluster_log_dbfs_path=cluster_log_dbfs_path, notebook_path=notebook_path,
            notebook_params=notebook_params, python_script_path=python_script_path,
            python_script_params=python_script_params, main_class_name=main_class_name, jar_params=jar_params,
            python_script_name=python_script_name, source_directory=source_directory, hash_paths=hash_paths,
            run_name=run_name, timeout_seconds=timeout_seconds, runconfig=runconfig, maven_libraries=maven_libraries,
            pypi_libraries=pypi_libraries, egg_libraries=egg_libraries, jar_libraries=jar_libraries,
            rcran_libraries=rcran_libraries, compute_target=compute_target, allow_reuse=allow_reuse, version=version,
            permit_cluster_restart=permit_cluster_restart)

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        result = "DatabricksStep_{0}".format(self.name)
        return result

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        return self.__str__()

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the Databricks step and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  typing.Union[azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore,
                                azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore]
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(DatabricksStep, self).create_node(graph=graph, default_datastore=default_datastore,
                                                       context=context)
