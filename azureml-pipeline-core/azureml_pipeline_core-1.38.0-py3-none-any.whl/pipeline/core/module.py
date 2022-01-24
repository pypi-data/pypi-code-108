# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains classes for creating and managing resusable computational units of an Azure Machine Learning pipeline.

Modules allow you to create computational units in a :class:`azureml.pipeline.core.Pipeline`, which can have
inputs, outputs, and rely on parameters and an environment configuration to operate. A module can be versioned
and be used in different Azure Machine Learning pipelines unlike :class:`azureml.pipeline.core.PipelineStep`
(and derived classes) which are used in one Pipeline.

Modules are designed to be reused in several pipelines and can evolve to adapt a specific computation logic
for different use cases. A step in a pipeline can be used in fast iterations to improve an algorithm,
and once the goal is achieved, the algorithm is usually published as a module to enable reuse.
"""
from __future__ import print_function
from azureml._html.utilities import to_html
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import InputPortDef, OutputPortDef, ModuleDef, ParamDef, PipelineParameter
from azureml.pipeline.core._annotated_arguments import _InputArgument, _OutputArgument, _ParameterArgument, \
    _StringArgument
from collections import OrderedDict
from ._module_builder import _ModuleBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider
from azureml.core.compute import AdlaCompute, BatchCompute

import os
import re
import logging


class Module(object):
    """
    Represents a computation unit used in an Azure Machine Learning pipeline.

    A module is a collection of files which will run on a compute target and a description of an interface.
    The collection of files can be script, binaries, or any other files required to execute on the compute target.
    The module interface describes inputs, outputs, and parameter definitions. It doesn't
    bind them to specific values or data. A module has a snapshot associated with it, which captures the
    collection of files defined for the module.

    .. remarks::

        A Module acts as a container of its versions. In the following example, a ModuleVersion is created
        from the :meth:`azureml.pipeline.core.module.Module.publish_python_script` method and has
        two inputs and two outputs. The create ModuleVersion is the default version (``is_default`` is set to True).

        .. code-block:: python

            out_sum = OutputPortDef(name="out_sum", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                    label="Sum of two numbers")
            out_prod = OutputPortDef(name="out_prod", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                     label="Product of two numbers")
            entry_version = module.publish_python_script("calculate.py", "initial",
                                                         inputs=[], outputs=[out_sum, out_prod], params = {"initialNum":12},
                                                         version="1", source_directory="./calc")

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-modulestep.ipynb


        This module can be used when defining a pipeline, in different steps, by using a
        :class:`azureml.pipeline.steps.ModuleStep`.

        The following sample shows how to wire the data used in the pipeline to inputs and outputs of
        a ModuleVersion using :class:`azureml.pipeline.core.builder.PipelineData`:

        .. code-block:: python

            middle_step_input_wiring = {"in1":first_sum, "in2":first_prod}
            middle_sum = PipelineData("middle_sum", datastore=datastore, output_mode="mount",is_directory=False)
            middle_prod = PipelineData("middle_prod", datastore=datastore, output_mode="mount",is_directory=False)
            middle_step_output_wiring = {"out_sum":middle_sum, "out_prod":middle_prod}

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-modulestep.ipynb


        The mapping can then be used when creating the ModuleStep:

        .. code-block:: python

            middle_step = ModuleStep(module=module,
                                     inputs_map= middle_step_input_wiring,
                                     outputs_map= middle_step_output_wiring,
                                     runconfig=RunConfiguration(), compute_target=aml_compute,
                                     arguments = ["--file_num1", first_sum, "--file_num2", first_prod,
                                                  "--output_sum", middle_sum, "--output_product", middle_prod])

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-modulestep.ipynb



        The resolution of which version of the module to use happens upon submission, and follows the following
        process:
        - Remove all disabled versions
        - If a specific version was stated, use that, else
        - If a default version was defined to the Module, use that, else
        - If all versions follow semantic versioning without letters, take the highest value, else
        - Take the version of the Module that was updated last

        Note that because a node's inputs and outputs mapping to a module's input and output is defined upon Pipeline
        creation, if the resolved version upon submission has a different interface from the one that is resolved
        upon pipeline creation, then the pipeline submission will fail.

        The underlying module can be updated with new versions while keeping the default version the same.

        Modules are uniquely named within a workspace.

    :param workspace: The workspace object this Module belongs to.
    :type workspace: azureml.core.Workspace
    :param module_id: The ID of the Module.
    :type module_id: str
    :param name: The name of the Module.
    :type name: str
    :param description: The description of the Module.
    :type description: str
    :param status: The new status of the Module: 'Active', 'Deprecated', or 'Disabled'.
    :type status: str
    :param default_version: The default version of the Module.
    :type default_version: str
    :param module_version_list: A list of :class:`azureml.pipeline.core.ModuleVersionDescriptor` objects.
    :type module_version_list: builtin.list
    :param _module_provider: (Internal use only.) The Module provider.
    :type _module_provider: azureml.pipeline.core._aeva_provider._AzureMLModuleProvider
    :param _module_version_provider: (Internal use only.) The ModuleVersion provider.
    :type _module_version_provider: azureml.pipeline.core._aeva_provider._AevaMlModuleVersionProvider
    """

    def __init__(self, workspace, module_id, name, description, status, default_version, module_version_list,
                 _module_provider=None, _module_version_provider=None):
        """
        Initialize Module.

        :param workspace: The workspace object this Module belongs to.
        :type workspace: azureml.core.Workspace
        :param module_id: The ID of the Module.
        :type module_id: str
        :param name: The name of the Module.
        :type name: str
        :param description: The description of the Module.
        :type description: str
        :param status: The new status of the Module: 'Active', 'Deprecated', or 'Disabled'.
        :type status: str
        :param default_version: The default version of the Module.
        :type default_version: str
        :param module_version_list: A list of :class:`azureml.pipeline.core.ModuleVersionDescriptor` objects.
        :type module_version_list: builtin.list
        :param _module_provider: The Module provider.
        :type _module_provider: _AevaMlModuleProvider object
        :param _module_version_provider: The ModuleVersion provider.
        :type _module_version_provider: azureml.pipeline.core._aeva_provider._AevaMlModuleVersionProvider
        """
        self._workspace = workspace
        self._id = module_id
        self._name = name
        self._description = description
        self._status = status
        self._default_version = default_version
        self._module_version_list = module_version_list
        self._workspace = workspace
        self._module_provider = _module_provider
        self._module_version_provider = _module_version_provider

    @staticmethod
    def create(workspace, name, description, _workflow_provider=None):
        """
        Create the Module.

        :param workspace: The workspace in which to create the Module.
        :type workspace: azureml.core.Workspace
        :param name: The name of the Module.
        :type name: str
        :param description: The description of the Module.
        :type description: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider

        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        azure_ml_module_provider = graph_context.workflow_provider.azure_ml_module_provider
        result = azure_ml_module_provider.create_module(name, description)
        return result

    @staticmethod
    def get(workspace, module_id=None, name=None, _workflow_provider=None):
        """
        Get the Module by name or by ID; throws an exception if either is not provided.

        :param workspace: The workspace in which to create the Module.
        :type workspace: azureml.core.Workspace
        :param module_id: The ID of the Module.
        :type module_id: str
        :param name: The name of the Module.
        :type name: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider

        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        azure_ml_module_provider = graph_context.workflow_provider.azure_ml_module_provider
        result = azure_ml_module_provider.get_module(module_id, name)
        return result

    @staticmethod
    def process_source_directory(name, source_directory, script_name):
        """
        Process source directory for the step and check that the script exists.

        :param name: The name of the step.
        :type name: str
        :param source_directory: The source directory for the step.
        :type source_directory: str
        :param script_name: The script name for the step.
        :type script_name: str

        :return: The source directory and hash paths.
        :rtype: str, builtin.list
        :raises: ValueError
        """
        script_path = os.path.join(source_directory, script_name)
        if not os.path.isfile(script_path):
            abs_path = os.path.abspath(script_path)
            raise ValueError("Step [%s]: script not found at: %s. Make sure to specify an appropriate "
                             "source_directory on the Step or default_source_directory on the Pipeline."
                             % (name, abs_path))

        return source_directory

    @staticmethod
    def module_def_builder(name, description, execution_type, input_bindings, output_bindings, param_defs=None,
                           create_sequencing_ports=True, allow_reuse=True, version=None, module_type=None,
                           step_type=None, arguments=None, runconfig=None, cloud_settings=None):
        """
        Create the module definition object that describes the step.

        :param name: The name the Module.
        :type name: str
        :param description: The description of the Module.
        :type description: str
        :param execution_type: The execution type of the Module.
        :type execution_type: str
        :param input_bindings: The Module input bindings.
        :type input_bindings: builtin.list
        :param output_bindings: The Module output bindings.
        :type output_bindings: builtin.list
        :param param_defs: The Module param definitions.
        :type param_defs: builtin.list
        :param create_sequencing_ports: Indicates whether sequencing ports will be created for the Module.
        :type create_sequencing_ports: bool
        :param allow_reuse: Indicates whether he Module will be available to be reused.
        :type allow_reuse: bool
        :param version: The version of the Module.
        :type version: str
        :param module_type: The Module type.
        :type module_type: str
        :param step_type: Type of step associated with this module, e.g. "PythonScriptStep", "HyperDriveStep", etc.
        :type step_type: str
        :param arguments: Annotated arguments list to use when calling this module
        :type arguments: builtin.list
        :param runconfig: Runconfig that will be used for python_script_step
        :type runconfig: str
        :param cloud_settings: Settings that will be used for clouds
        :type cloud_settings: str

        :return: The Module def object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        :raises: ValueError
        """
        all_datatypes = ["AnyFile", "AnyDirectory"]
        input_port_defs = []
        for input_binding in input_bindings:
            if isinstance(input_binding, InputPortDef):
                input_port_defs.append(input_binding)
            else:
                data_types = all_datatypes
                if hasattr(input_binding, 'data_type') and input_binding.data_type is not None:
                    data_types = [input_binding.data_type]
                data_ref_name = input_binding.data_reference_name\
                    if hasattr(input_binding, 'data_reference_name') else None
                is_resource = input_binding.is_resource\
                    if hasattr(input_binding, 'is_resource') else False
                label = input_binding.label if hasattr(input_binding, 'label') else input_binding.name
                additional_transformations = input_binding.additional_transformations \
                    if hasattr(input_binding, 'additional_transformations') else None
                is_input_promoted_to_dataset = input_binding._is_input_promoted_to_dataset \
                    if hasattr(input_binding, '_is_input_promoted_to_dataset') else False
                input_port_defs.append(InputPortDef(name=input_binding.name,
                                                    data_types=data_types,
                                                    default_datastore_mode=input_binding.bind_mode,
                                                    default_path_on_compute=input_binding.path_on_compute,
                                                    default_overwrite=input_binding.overwrite,
                                                    default_data_reference_name=data_ref_name,
                                                    is_resource=is_resource,
                                                    label=label,
                                                    additional_transformations=additional_transformations,
                                                    is_input_promoted_to_dataset=is_input_promoted_to_dataset))

        output_port_defs = []
        for output_binding in output_bindings:
            if isinstance(output_binding, OutputPortDef):
                output_port_defs.append(output_binding)
            else:
                if output_binding.training_output and execution_type not in ['AutoMLCloud', 'HyperDriveCloud']:
                    raise ValueError('TrainingOutput is not supported for this type of execution:', execution_type)
                label = output_binding.label if hasattr(output_binding, 'label') else output_binding.name
                output_port_defs.append(OutputPortDef(name=output_binding._output_name,
                                                      default_datastore_name=output_binding._datastore_name,
                                                      default_datastore_mode=output_binding.bind_mode,
                                                      default_path_on_compute=output_binding.path_on_compute,
                                                      default_overwrite=output_binding.overwrite,
                                                      data_type=output_binding.data_type,
                                                      is_directory=output_binding.is_directory,
                                                      training_output=output_binding.training_output,
                                                      label=label))

        module_def = ModuleDef(
            name=name,
            description=description,
            input_port_defs=input_port_defs,
            output_port_defs=output_port_defs,
            param_defs=param_defs,
            module_execution_type=execution_type,
            create_sequencing_ports=create_sequencing_ports,
            allow_reuse=allow_reuse,
            version=version,
            module_type=module_type,
            step_type=step_type,
            arguments=arguments,
            runconfig=runconfig,
            cloud_settings=cloud_settings)

        return module_def

    @staticmethod
    def get_versions(workspace, name, _workflow_provider=None):
        """
        Get all the versions of the Module.

        :param workspace: The workspace the Module was created on.
        :type workspace: azureml.core.Workspace
        :param name: The name of the Module.
        :type name: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider

        :return: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
        :rtype: builtin.list
        """
        module = Module.get(workspace, name=name,
                            _workflow_provider=_workflow_provider)
        return module.module_version_list()

    @property
    def id(self):
        """
        Get the ID of the Module.

        :return: The id.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """
        Get the name of the Module.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the Module.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def status(self):
        """
        Get the status of the Module.

        :return: The status.
        :rtype: str
        """
        return self._status

    @property
    def default_version(self):
        """
        Get the default version of the Module.

        :return: The default version string.
        :rtype: str
        """
        return self._default_version

    def module_version_list(self):
        """
        Get the Module version list.

        :return: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
        :rtype: builtin.list
        """
        return self._module_version_list

    def publish(self, description, execution_type, inputs, outputs,
                param_defs=None,
                create_sequencing_ports=True, version=None, is_default=False, content_path=None, hash_paths=None,
                category=None, arguments=None, runconfig=None):
        """
        Create a ModuleVersion and add it to the current Module.

        :param description: The description of the Module.
        :type description: str
        :param execution_type: The execution type of the Module.
            Acceptable values are ``esCloud``, ``adlcloud`` and ``AzureBatchCloud``
        :type execution_type: str
        :param inputs: The Module inputs.
        :type inputs: builtin.list
        :param outputs: The Module outputs.
        :type outputs: builtin.list
        :param param_defs: The Module parameter definitions.
        :type param_defs: builtin.list
        :param create_sequencing_ports: Indicates whether sequencing ports will be created for the Module.
        :type create_sequencing_ports: bool
        :param version: The version of the Module.
        :type version: str
        :param is_default: Indicates whether the published version is to be the default one.
        :type is_default: bool
        :param content_path: directory
        :type content_path: str
        :param hash_paths: A list of paths to hash when checking for changes to the step contents. If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default, the
            contents of the ``source_directory`` are hashed (except files listed in .amlignore or .gitignore).
            DEPRECATED: no longer needed.
        :type hash_paths: builtin.list
        :param category: The module version's category
        :type category: str
        :param arguments: Arguments to use when calling the module.  Arguments can be strings,
            input references (InputPortDef), output references (OutputPortDef), and
            pipeline parameters (PipelineParameter).
        :type arguments: builtin.list
        :param runconfig: An optional RunConfiguration. A RunConfiguration can be used to specify additional
                    requirements for the run, such as conda dependencies and a Docker image.
        :type runconfig: azureml.core.runconfig.RunConfiguration

        :rtype: azureml.pipeline.core.ModuleVersion
        :raises: Exception
        """
        if version is not None:
            found_version = next((item for item in self._module_version_list if item.version == version), None)
            if found_version is not None:
                raise Exception("provided version value already exist")

        PipelineStep._process_pipeline_io(None, inputs, outputs)

        annotated_arguments = Module._build_annotated_arguments(arguments)
        runconfig_str = repr(runconfig) if runconfig is not None else None
        mod_def = self.module_def_builder(self._name, description, execution_type, inputs, outputs,
                                          param_defs, create_sequencing_ports, True, version, step_type='ModuleStep',
                                          arguments=annotated_arguments, runconfig=runconfig_str)

        if hash_paths:
            logging.warning("Parameter 'hash_paths' is deprecated, will be removed. "
                            + "All files under source_directory is hashed "
                            + "except files listed in .amlignore or .gitignore.")

        fingerprint = _ModuleBuilder.calculate_hash(mod_def, content_path=content_path)

        module_version = self._module_version_provider.create_module_version(self._workspace,
                                                                             self._id, version,
                                                                             mod_def, content_path, fingerprint,
                                                                             category=category,
                                                                             arguments=annotated_arguments)

        module_version_descriptor = ModuleVersionDescriptor(module_version.version, module_version.module_version_id)
        self._module_version_list.append(module_version_descriptor)
        self._module_provider.update_module(module_version.module_id, versions=self._module_version_list)
        if is_default:
            self.set_default_version(module_version_descriptor.version)
        return module_version

    def publish_adla_script(self, script_name, description, inputs, outputs, params=None, create_sequencing_ports=True,
                            degree_of_parallelism=None, priority=None, runtime_version=None, compute_target=None,
                            version=None, is_default=False, source_directory=None, hash_paths=None, category=None,
                            arguments=None):
        """
        Create a ModuleVersion based on Azure Data Lake Analytics (ADLA) and add it to the current Module.

        :param script_name: The name of an ADLA script, relative to ``source_directory``.
        :type script_name: str
        :param description: The description of the Module version.
        :type description: str
        :param inputs: The Module input bindings.
        :type inputs: builtin.list
        :param outputs: The Module output bindings.
        :type outputs: builtin.list
        :param params: The ModuleVersion params, as name-default_value pairs.
        :type params: dict
        :param create_sequencing_ports: Indicates whether sequencing ports will be created for the Module.
        :type create_sequencing_ports: bool
        :param degree_of_parallelism: The degree of parallelism to use for this job.
        :type degree_of_parallelism: int
        :param priority: The priority value to use for the current job.
        :type priority: int
        :param runtime_version: The runtime version of the Azure Data Lake Analytics (ADLA) engine.
        :type runtime_version: str
        :param compute_target: The ADLA compute to use for this job.
        :type compute_target: azureml.core.compute.AdlaCompute, str
        :param version: The version of the module.
        :type version: str
        :param is_default: Indicates whether the published version is to be the default one.
        :type is_default: bool
        :param source_directory: directory
        :type source_directory: str
        :param hash_paths: hash_paths
        :type hash_paths: builtin.list
        :param category: The module version's category
        :type category: str
        :param arguments: Arguments to use when calling the module.  Arguments can be strings,
            input references (InputPortDef), output references (OutputPortDef), and
            pipeline parameters (PipelineParameter).
        :type arguments: builtin.list

        :rtype: azureml.pipeline.core.ModuleVersion
        """
        metadata_params = Module._create_adla_metadata_params(script_name, self._workspace, compute_target,
                                                              degree_of_parallelism, priority,
                                                              runtime_version)

        params = params or []
        param_defs = [ParamDef(param) for param in params]
        param_defs += [ParamDef(param, is_metadata_param=True) for param in metadata_params]

        return self.publish(description=description, execution_type="adlcloud",
                            inputs=inputs, outputs=outputs,
                            param_defs=param_defs, create_sequencing_ports=create_sequencing_ports,
                            version=version, is_default=is_default,
                            content_path=source_directory, hash_paths=hash_paths, category=category,
                            arguments=arguments)

    def publish_azure_batch(self, description, compute_target, inputs, outputs,
                            params=None, create_sequencing_ports=True, version=None, is_default=False,
                            create_pool=False, pool_id=None, delete_batch_job_after_finish=False,
                            delete_batch_pool_after_finish=False, is_positive_exit_code_failure=True,
                            vm_image_urn="urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter",
                            run_task_as_admin=False, target_compute_nodes=1, vm_size="standard_d1_v2",
                            executable=None, source_directory=None, category=None, arguments=None):
        """
        Create a ModuleVersion that uses Azure batch and add it to the current Module.

        :param description: The description of the Module version.
        :type description: str
        :param compute_target: The BatchCompute compute target.
        :type compute_target: azureml.core.compute.BatchCompute or str
        :param inputs: The Module input bindings.
        :type inputs: builtin.list
        :param outputs: The Module output bindings.
        :type outputs: builtin.list
        :param params: The ModuleVersion params, as name-default_value pairs.
        :type params: dict
        :param create_sequencing_ports: Indicates whether sequencing ports will be created for the Module.
        :type create_sequencing_ports: bool
        :param version: The version of the Module.
        :type version: str
        :param is_default: Indicates whether the published version is to be the default one.
        :type is_default: bool
        :param create_pool: Indicates whether to create the pool before running the jobs.
        :type create_pool: bool
        :param pool_id: (Mandatory) The ID of the Pool where the job will run.
        :type pool_id: str
        :param delete_batch_job_after_finish: Indicates whether to delete the job from
                                            Batch account after it's finished.
        :type delete_batch_job_after_finish: bool
        :param delete_batch_pool_after_finish: Indicates whether to delete the pool after
                                            the job finishes.
        :type delete_batch_pool_after_finish: bool
        :param is_positive_exit_code_failure: Indicates whether he job fails if the task exists
                                            with a positive code.
        :type is_positive_exit_code_failure: bool
        :param vm_image_urn: If ``create_pool`` is True and VM uses VirtualMachineConfiguration, then this
            parameter indicates the VM image to use. Value format: ``urn:publisher:offer:sku``.
            Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``.
        :type vm_image_urn: str
        :param run_task_as_admin: Indicates whether the task should run with Admin privileges.
        :type run_task_as_admin: bool
        :param target_compute_nodes: If ``create_pool`` is True, indicates how many compute nodes will be added
                                    to the pool.
        :type target_compute_nodes: int
        :param vm_size: If ``create_pool`` is True, indicates the virtual machine size of the compute nodes.
        :type vm_size: str
        :param executable: The name of the command/executable that will be executed as part of the job.
        :type executable: str
        :param source_directory: The source directory.
        :type source_directory: str
        :param category: The module version's category
        :type category: str
        :param arguments: Arguments to use when calling the module.  Arguments can be strings,
            input references (InputPortDef), output references (OutputPortDef), and
            pipeline parameters (PipelineParameter).
        :type arguments: builtin.list

        :rtype: azureml.pipeline.core.ModuleVersion
        :raises: ValueError
        """
        optional_parameters = Module._construct_azure_batch_optional_params_def(
            create_pool=create_pool,
            delete_batch_job_after_finish=delete_batch_job_after_finish,
            delete_batch_pool_after_finish=delete_batch_pool_after_finish,
            is_positive_exit_code_failure=is_positive_exit_code_failure,
            urn=vm_image_urn,
            run_task_as_admin=run_task_as_admin, target_compute_nodes=target_compute_nodes,
            vm_size=vm_size)
        parameters = params or dict()
        parameters["PoolId"] = pool_id
        if executable is None:
            raise ValueError('executable is required')
        parameters["Executable"] = executable
        metadata_params = Module._create_azure_batch_metadata_params(self._workspace, compute_target)
        param_defs = [ParamDef(param) for param in parameters]
        param_defs += [ParamDef(param, is_optional=True) for param in optional_parameters]
        param_defs += [ParamDef(param, is_metadata_param=True) for param in metadata_params]
        return self.publish(description=description, execution_type="AzureBatchCloud",
                            inputs=inputs, outputs=outputs,
                            param_defs=param_defs, create_sequencing_ports=create_sequencing_ports,
                            version=version, is_default=is_default,
                            content_path=source_directory, hash_paths=[source_directory], category=category,
                            arguments=arguments)

    def publish_python_script(self, script_name, description, inputs, outputs, params=None,
                              create_sequencing_ports=True, version=None, is_default=False,
                              source_directory=None, hash_paths=None, category=None, arguments=None,
                              runconfig=None):
        """
        Create a ModuleVersion that's based on a Python script and add it to the current Module.

        :param script_name: The name of a Python script, relative to ``source_directory``.
        :type script_name: str
        :param description: The description of the Module version.
        :type description: str
        :param inputs: The Module input bindings.
        :type inputs: builtin.list
        :param outputs: The Module output bindings.
        :type outputs: builtin.list
        :param params: The ModuleVersion params, as name-default_value pairs.
        :type params: dict
        :param create_sequencing_ports: Indicates whether sequencing ports will be created for the Module.
        :type create_sequencing_ports: bool
        :param version: The version of the Module.
        :type version: str
        :param is_default: Indicates whether the published version is to be the default one.
        :type is_default: bool
        :param source_directory: directory
        :type source_directory: str
        :param hash_paths: A list of paths to hash when checking for changes to the step contents. If there
            are no changes detected, the pipeline will reuse the step contents from a previous run.  By default the
            contents of the ``source_directory`` are hashed (except files listed in .amlignore or .gitignore).
            DEPRECATED: no longer needed.
        :type hash_paths: builtin.list
        :param category: The module version's category
        :type category: str
        :param arguments: Arguments to use when calling the module.  Arguments can be strings,
            input references (InputPortDef), output references (OutputPortDef), and
            pipeline parameters (PipelineParameter).
        :type arguments: builtin.list
        :param runconfig: An optional RunConfiguration. A RunConfiguration can be used to specify additional
                    requirements for the run, such as conda dependencies and a Docker image.
        :type runconfig: azureml.core.runconfig.RunConfiguration

        :rtype: azureml.pipeline.core.ModuleVersion
        """
        if hash_paths:
            logging.warning("Parameter 'hash_paths' is deprecated, will be removed. "
                            + "All files under source_directory is hashed "
                            + "except files listed in .amlignore or .gitignore.")

        source_directory = Module.process_source_directory(self.name, source_directory, script_name)
        params = params or {}
        param_defs = {}
        # initialize all the parameters for the module
        for module_provider_param in _ModuleParameterProvider().get_params_list():
            param_defs[module_provider_param.name] = module_provider_param
        for param_name in params:
            param_val = params[param_name]
            if isinstance(param_val, ParamDef):
                param_defs[param_name] = param_val
            else:
                param_defs[param_name] = ParamDef(name=param_name, set_env_var=True,
                                                  default_value=params[param_name],
                                                  env_var_override=ParamDef._param_name_to_env_variable(param_name))
        param_defs['Script'] = ParamDef('Script', script_name, is_optional=True)
        return self.publish(description=description, execution_type="escloud",
                            inputs=inputs, outputs=outputs,
                            param_defs=list(param_defs.values()), create_sequencing_ports=create_sequencing_ports,
                            version=version, is_default=is_default,
                            content_path=source_directory, hash_paths=hash_paths, category=category,
                            arguments=arguments, runconfig=runconfig)

    def resolve(self, version=None):
        """
        Resolve and return the right ModuleVersion.

        :return: The Module version to use.
        :rtype: azureml.pipeline.core.ModuleVersion
        """
        if version is not None:
            mvd = next((v for v in self._module_version_list if v.version == version), None)
            if mvd is not None:
                return self._get_module_version(mvd.module_version_id, mvd.version)
        mv = self.get_default()
        if mv is not None:
            return mv

        def find_highest_version(versions_list):
            if len(versions_list) == 1:
                return versions_list[0]["k"]
            else:
                # version list sorted desc by the first segment of the version
                versions_list.sort(key=lambda x: int(x["v"].split(".", 1)[0]), reverse=True)
                # filter only the largest ones
                tops = filter(lambda x: x["v"].split(".", 1)[0] == versions_list[0]["v"].split(".", 1)[0],
                              versions_list)
                # remove the first segment from the versions
                nexts = map(lambda y:
                            {"k": y["k"], "v": y["v"].split(".", 1)[1]} if len(y["v"].split(".", 1)) > 1 else None,
                            tops)
                # remove the empty cells
                next_version_list = list(filter(lambda k: k is not None, nexts))
                if len(next_version_list) == 0:
                    return versions_list[0]["k"]
                return find_highest_version(next_version_list)

        all_mvs = map(lambda v: self._get_module_version(v.module_version_id, v.version), self._module_version_list)
        non_disabled_versions = list(filter(lambda v: v.status != 'Disabled', all_mvs))
        if all(a.version is not None
               and ".." not in a.version
               and not a.version.startswith(".")
               and not a.version.endswith(".")
               and a.version.replace(".", "1").isdigit() for a in non_disabled_versions):
            ver = find_highest_version(list(map(lambda x: {"k": x.version, "v": x.version},
                                                non_disabled_versions)))
            return self.resolve(ver)
        else:
            date_and_mv = list(map(lambda x: {"dt": x._entity.data.last_modified_date, "mv": x},
                                   non_disabled_versions))
            return max(date_and_mv, key=lambda k: k["dt"])["mv"]

    def enable(self):
        """Set the Module to 'Active'."""
        self._set_status('Active')

    def disable(self):
        """Set the Module to 'Disabled'."""
        self._set_status('Disabled')

    def deprecate(self):
        """Set the Module to 'Deprecated'."""
        self._set_status('Deprecated')

    def _set_status(self, new_status):
        """Set the Module status."""
        self._module_provider.update_module(self._id, status=new_status)
        self._status = new_status

    def get_default_version(self):
        """
        Get the default version of Module.

        :return: The default version of the Module.
        :rtype: str
        """
        return self._default_version

    def set_default_version(self, version_id):
        """
        Set the default ModuleVersion of the Module.

        :return: The default version.
        :rtype: str
        :raises: Exception
        """
        if version_id is None:
            raise Exception("No version was provided to be set as default")

        found_module_version = next(
            (item for item in self._module_version_list if item.version == version_id),
            None)
        if found_module_version is None:
            raise Exception("provided version is not part of the module")
        self._module_provider.update_module(self._id, default_version=found_module_version.version)
        self._default_version = found_module_version.version

    def get_default(self):
        """
        Get the default module version.

        :return: The default module version.
        :rtype: azureml.pipeline.core.module.ModuleVersion
        """
        version_descriptor = next((mv for mv in self._module_version_list if mv.version == self.default_version),
                                  None)
        if version_descriptor is None:
            return None
        return self._get_module_version(version_descriptor.module_version_id)

    def set_name(self, name):
        """
        Set the name of Module.

        :param name: The name to set.
        :type name: str
        :raises: Exception
        """
        if name is None:
            raise Exception("No name was provided")
        self._module_provider.update_module(self._id, name=name)

    def set_description(self, description):
        """
        Set the description of Module.

        :param description: The description to set.
        :type description: str
        :raises: Exception
        """
        if description is None:
            raise Exception("No description was provided")
        self._module_provider.update_module(self._id, description=description)

    def _get_module_version(self, version_id, version=None):
        return self._module_version_provider.get_module_version(self._workspace,
                                                                module_version_id=version_id,
                                                                module_id=self.id,
                                                                version=version)

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Versions', self._get_list_info_dict(self._module_version_list))
        ])
        return info

    def _get_list_info_dict(self, versions):
        list_info = [self._get_module_version_info_dict(version_item) for version_item in versions]
        return list_info

    @staticmethod
    def _get_module_version_info_dict(module_version):
        info = OrderedDict([
            ('Version', module_version.version),
            ('Module_version_id', module_version.module_version_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the Module."""
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Versions', [(module_version.version, module_version.module_version_id)
                          for module_version in self._module_version_list])
        ])
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Module({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the Module."""
        return self.__str__()

    @staticmethod
    def _construct_azure_batch_optional_params_def(create_pool=False,
                                                   delete_batch_job_after_finish=False,
                                                   delete_batch_pool_after_finish=False,
                                                   is_positive_exit_code_failure=True,
                                                   urn="urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter",
                                                   run_task_as_admin=False,
                                                   target_compute_nodes=1, vm_size="standard_d1_v2"):
        """
        Create an Azure Data Lake Analytics (ADLA) metadata parameters dictionary.

        :param create_pool: Indicates whether create the pool before running the jobs.
        :type create_pool: bool
        :param delete_batch_job_after_finish: Indicates whether to delete the job from the
                                            Batch account after it's finished.
        :type delete_batch_job_after_finish: bool
        :param delete_batch_pool_after_finish: Indicates whether to delete the pool after
                                            the job finishes.
        :type delete_batch_pool_after_finish: bool
        :param is_positive_exit_code_failure: Indicates whether the job should fails if the task exists
                                            with a positive code.
        :type is_positive_exit_code_failure: bool
        :param urn: If ``create_pool`` is true and VM uses VirtualMachineConfiguration, then this parameter indicates
                the VM image to use. Value format: ``urn:publisher:offer:sku``.
                Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``
        :type urn: str
        :param run_task_as_admin: Indicates if the task should run with Admin privileges.
        :type run_task_as_admin: bool
        :param target_compute_nodes: If ``create_pool`` is true, this parameter indicates how many compute nodes
                will be added to the pool.
        :type target_compute_nodes: int
        :param vm_size: If ``create_pool`` is True, this parameter indicates the virtual machine size of the
            compute nodes.
        :type vm_size: str

        :return: Dictionary of name-value pairs
        :rtype: {str: str}

        """
        params = dict()
        params["RunTaskAsAdmin"] = run_task_as_admin
        params["IsPositiveExitCodeFailure"] = is_positive_exit_code_failure
        params["DeleteBatchPoolAfterFinish"] = delete_batch_pool_after_finish
        params["DeleteBatchJobAfterFinish"] = delete_batch_job_after_finish
        params["TargetComputeNodes"] = target_compute_nodes
        params["CreatePool"] = create_pool
        params["VmSize"] = vm_size
        tokens = urn.split(':')
        if len(tokens) < 4 or tokens[0] != "urn":
            raise TypeError("urn format is incorrect, expected format: 'urn:publisher:offer:sku'")
        params["ImagePublisher"] = tokens[1]
        params["ImageOffer"] = tokens[2]
        params["ImageSkuKeyword"] = tokens[3]
        return params

    @staticmethod
    def _create_adla_metadata_params(script_name, workspace, compute_target,
                                     degree_of_parallelism=None, priority=None, runtime_version=None):
        """
        Create an Azure Data Lake Analytics (ADLA) metadata parameters dictionary.

        :param script_name: The name of U-SQL script, relative to ``source_directory``.
        :type script_name: str
        :param workspace: The Workspace object that holds the AdlaCompute.
        :type workspace: azureml.core.Workspace
        :param compute_target: The compute to use for this job.
        :type compute_target: azureml.core.compute.AdlaCompute, str
        :param degree_of_parallelism: The degree of parallelism to use for this job. This must be greater than 0.
            If set to less than 0, defaults to 1.
        :type degree_of_parallelism: int
        :param priority: The priority value to use for the current job. Lower numbers have a higher priority.
            By default, a job has a priority of 1000. The value you specify must be greater than 0.
        :type priority: int
        :param runtime_version: The runtime version of the Data Lake Analytics engine.
        :type runtime_version: str

        :return: Dictionary of name-value pairs
        :rtype: {str: str}

        """
        metadata_params = {
            'ScriptName': script_name
        }

        if degree_of_parallelism is not None:
            metadata_params['DegreesOfParallelism'] = degree_of_parallelism
        if priority is not None:
            metadata_params['Priority'] = priority
        if runtime_version is not None:
            metadata_params['RuntimeVersion'] = runtime_version

        adla_resource_id = Module._get_adla_resource_id(workspace, compute_target)
        adla_config = Module._get_adla_config(adla_resource_id)

        metadata_params['AnalyticsAccountName'] = adla_config['AdlaAccountName']
        metadata_params['SubscriptionId'] = adla_config['AdlaSubscriptionId']
        metadata_params['ResourceGroupName'] = adla_config['AdlaResourceGroup']
        return metadata_params

    @staticmethod
    def _get_adla_resource_id(workspace, compute_target):
        """
        Get ADLA resource ID.

        :param workspace: Workspace object that holds the AdlaCompute.
        :type workspace: azureml.core.Workspace
        :param compute_target: the ADLA compute to use for this job
        :type compute_target: azureml.core.compute.AdlaCompute, str

        :return: The cluster resource id of adla compute.
        :rtype: str
        """
        if isinstance(compute_target, AdlaCompute):
            return compute_target.cluster_resource_id

        if isinstance(compute_target, str):
            try:
                compute_target = AdlaCompute(workspace, compute_target)
                return compute_target.cluster_resource_id
            except Exception as e:
                raise ValueError('error in getting adla compute: {}'.format(e))

        raise ValueError('compute_target is not specified correctly')

    @staticmethod
    def _get_adla_config(adla_resource_id):
        """
        Get ADLA config.

        :param adla_resource_id: adla resource id
        :type adla_resource_id: str

        :return: Dictionary of adl cluster info.
        :rtype: dict
        """
        resource_id_regex = \
            r'\/subscriptions\/([^/]+)\/resourceGroups\/([^/]+)\/providers' \
            r'\/Microsoft\.DataLakeAnalytics\/accounts\/([^/]+)'

        match = re.search(resource_id_regex, adla_resource_id, re.IGNORECASE)

        if match is None:
            raise ValueError('adla resource id is not in correct format: {}'.format(adla_resource_id))

        return {
            'AdlaSubscriptionId': match.group(1),
            'AdlaResourceGroup': match.group(2),
            'AdlaAccountName': match.group(3),
        }

    @staticmethod
    def _create_azure_batch_metadata_params(workspace, compute_target):
        """
        Create metadata params dictionary for azure batch module version.

        :param workspace: Workspace object that holds the BatchCompute.
        :type workspace: azureml.core.workspace.Workspace
        :param compute_target: BatchCompute compute
        :type compute_target: azureml.core.compute.BatchCompute or str

        :return: Dictionary of name-value pairs
        :rtype: {str: str}
        """
        azurebatch_resource_id = Module._get_azurebatch_resource_id(workspace, compute_target)
        resource_id_regex = \
            r'\/subscriptions\/([^/]+)\/resourceGroups\/([^/]+)\/providers\/Microsoft\.Batch\/batchAccounts\/([^/]+)'

        match = re.search(resource_id_regex, azurebatch_resource_id, re.IGNORECASE)

        if match is None:
            raise ValueError('AzureBatch resource Id format is incorrect: {0}, the correct format is: {1}'
                             .format(azurebatch_resource_id, "/subscriptions/{SubscriptionId}/"
                                                             "resourceGroups/{ResourceGroup}/"
                                                             "providers/Microsoft.Batch/batchAccounts/{BatchAccount}"))
        return {
            'SubscriptionId': match.group(1),
            'ResourceGroup': match.group(2),
            'AccountName': match.group(3)
        }

    @staticmethod
    def _get_azurebatch_resource_id(workspace, compute_target):
        """
        Get the AzureBatch resource id.

        :param workspace: Workspace object that holds the BatchCompute.
        :type workspace: azureml.core.workspace.Workspace
        :param compute_target: BatchCompute compute
        :type compute_target: azureml.core.compute.BatchCompute or str

        :return: The AzureBatch resource id.
        :rtype: str
        """
        if isinstance(compute_target, BatchCompute):
            return compute_target.cluster_resource_id

        if isinstance(compute_target, str):
            try:
                compute_target = BatchCompute(workspace, compute_target)
                return compute_target.cluster_resource_id
            except Exception as e:
                raise ValueError('Error in getting AzureBatch compute: {}'.format(e))

        raise ValueError('compute_target is not specified correctly.')

    @staticmethod
    def _build_annotated_arguments(arguments):
        """
        Construct the annotated arguments list which will be stored in the module entity.

        :param arguments: Arguments to use when calling the module, list of structured arguments for module execution.
        :type arguments: builtin.list
        :return: Annotated list of arguments (consisting of _InputArgument, _OutputArgument, _StringArgument, and
            _ParameterArgument)
        :rtype: builtin.list
        """
        if arguments is None:
            return None

        annotated_arguments = []
        for argument in arguments:
            if isinstance(argument, InputPortDef):
                annotated_arguments.append(_InputArgument(argument.name))
            elif isinstance(argument, OutputPortDef):
                annotated_arguments.append(_OutputArgument(argument.name))
            elif isinstance(argument, PipelineParameter):
                annotated_arguments.append(_ParameterArgument(argument.name))
            elif isinstance(argument, str):
                annotated_arguments.append(_StringArgument(argument))
            else:
                raise Exception("Unknown type in the argument list.")

        return annotated_arguments


class ModuleVersion(object):
    """
    Represents the actual computation unit within a :class:`azureml.pipeline.core.module.Module`.

    You should not use this class directly. Instead, use one of the publish methods of
    the :class:`azureml.pipeline.core.module.Module` class.

    .. Remarks::

        The following example shows how to create a ModuleVersion using a publish method of the
        :class:`azureml.pipeline.core.module.Module` class:

        .. code-block:: python

            in1_mid = InputPortDef(name="in1", default_datastore_mode="mount",
                               default_data_reference_name=datastore.name, label="First input number")
            in2_mid = InputPortDef(name="in2", default_datastore_mode="mount",
                               default_data_reference_name=datastore.name, label="Second input number")
            out_sum_mid = OutputPortDef(name="out_sum", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                        label="Sum of two numbers")
            out_prod_mid = OutputPortDef(name="out_prod", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                         label="Product of two numbers")
            module.publish_python_script(
                "calculate.py", "middle", inputs=[in1_mid, in2_mid], outputs=[out_sum_mid, out_prod_mid], version="2", is_default=True,
                source_directory="./calc")

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-modulestep.ipynb


    :param workspace: The workspace object this module will belong to.
    :type workspace: azureml.core.Workspace
    :param module_entity: The ModuleEntity object.
    :type module_entity: azureml.pipeline.core._restclients.aeva.models.azure_ml_module_version.AzureMLModuleVersion
    :param _module_version_provider: (Internal use only.) The version provider.
    :type _module_version_provider: azureml.pipeline.core._aeva_provider._AevaMlModuleVersionProvider
    :param version: The version number.
    :type version: str
    """

    def __init__(self, workspace, module_entity, version, _module_version_provider):
        """
        Initialize ModuleVersion.

        :param workspace: The workspace object this module will belong to.
        :type workspace: azureml.core.Workspace
        :param module_entity: The ModuleEntity object.
        :type module_entity:
            azureml.pipeline.core._restclients.aeva.models.azure_ml_module_version.AzureMLModuleVersion
        :param version: The version number.
        :type version: str
        :param _module_version_provider: The version provider.
        :type _module_version_provider: azureml.pipeline.core._aeva_provider._AevaMlModuleVersionProvider
        """
        self._workspace = workspace
        self._entity = module_entity
        self._version = version
        self._version_provider = _module_version_provider

    @staticmethod
    def get(workspace, module_version_id=None, _workflow_provider=None):
        """
        Get the Module by name or by ID; throws an exception if either is not provided.

        :param workspace: The workspace the Module was created in.
        :type workspace: azureml.core.Workspace
        :param module_version_id: The ID of the ModuleVersion.
        :type module_version_id: str
        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider

        :return: Module object.
        :rtype: azureml.pipeline.core.Module
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        azure_ml_module_version_provider = graph_context.workflow_provider.azure_ml_module_version_provider
        result = azure_ml_module_version_provider.get_module_version(workspace, module_version_id)
        return result

    @property
    def status(self):
        """
        Get the status of the ModuleVersion.

        :return: The status.
        :rtype: str
        """
        return self._entity.data.entity_status

    @property
    def module_id(self):
        """
        Get the ID of the containing module.

        :return: The ID.
        :rtype: str
        """
        return self._entity.module_id

    @property
    def description(self):
        """
        Get the description of the ModuleVersion.

        :return: The description.
        :rtype: str
        """
        return self._entity.data.description

    @property
    def module_version_id(self):
        """
        Get the ID of the ModuleVersion.

        :return: The ID.
        :rtype: str
        """
        return self._entity.data.id

    @property
    def version(self):
        """
        Get the version of the containing module.

        :return: The version.
        :rtype: str
        """
        return self._version

    @property
    def interface(self):
        """
        Get the interface of the module.

        :return: The structuredInterface.
        :rtype: azureml.pipeline.core._aeva_provider.StructuredInterface
        """
        return self._entity.data.structured_interface

    @property
    def category(self):
        """
        Get the category of the ModuleVersion.

        :return: The category.
        :rtype: str
        """
        return self._entity.data.category

    @property
    def runconfig(self):
        """
        Get the runconfig of the ModuleVersion.

        :return: The category.
        :rtype: str
        """
        return self._entity.data.runconfig

    def module(self, _workflow_provider=None):
        """
        Return the containing module element.

        :param _workflow_provider: (Internal use only.) The workflow provider.
        :type _workflow_provider:  azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        return Module.get(self._workspace, _workflow_provider=_workflow_provider, module_id=self.module_id)

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('status', self._entity.data.entity_status),
            ('version', self._version),
            ('module_id', self._entity.module_id),
            ('module_version_id', self._entity.data.id)
        ])
        return info

    def set_description(self, description):
        """
        Set the description of Module.

        :param description: The description to set.
        :type description: str
        :raises: Exception
        """
        if description is None:
            raise Exception("No description was provided")
        self._version_provider.update_module_version(self._entity.data.id,
                                                     version=self.version,
                                                     description=description)

    def enable(self):
        """Set the ModuleVersion state to 'Active'."""
        self._set_status('Active')

    def disable(self):
        """Set the ModuleVersion state to 'Disabled'."""
        self._set_status('Disabled')

    def deprecate(self):
        """Set the ModuleVersion state to 'Deprecated'."""
        self._set_status('Deprecated')

    def _set_status(self, new_status):
        """Set the Module status."""
        self._version_provider.update_module_version(self._entity.data.id, version=self.version,
                                                     status=new_status)
        self._entity.data.entity_status = new_status

    def __str__(self):
        """Return the string representation of the ModuleVersion."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "ModuleVersion({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the ModuleVersion."""
        return self.__str__()


class ModuleVersionDescriptor(object):
    """Defines the version and ID of a :class:`azureml.pipeline.core.module.ModuleVersion`."""

    def __init__(self, version, module_version_id):
        """
        Initialize ModuleVersionDescriptor.

        :param version: The version of the ModuleVersion.
        :type version: str
        :param module_version_id: The published ModuleVersion ID.
        :type module_version_id: str
        """
        self._version = version
        self._module_version_id = module_version_id

    @property
    def version(self):
        """
        Get the version of the ModuleVersion.

        :return: The version of ModuleVersion.
        :rtype: str
        """
        return self._version

    @property
    def module_version_id(self):
        """
        Get the ID of the ModuleVersion.

        :return: Get the ID of the ModuleVersion.
        :rtype: str
        """
        return self._module_version_id

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Version', self.version),
            ('ModuleVersionId', self.module_version_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the ModuleVersionDescriptor."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "ModuleVersionDescriptor({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the ModuleVersionDescriptor."""
        return self.__str__()
