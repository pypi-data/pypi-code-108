# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
APIs for federated learning.
"""
from shrike import pipeline
from shrike.pipeline.pipeline_config import federated_config, silo
from shrike.pipeline.pipeline_helper import AMLPipelineHelper
from shrike._core import experimental
from coolname import generate_slug
from dataclasses import MISSING, dataclass
from typing import List, Any, Optional, Union
from azure.ml.component import dsl
from azure.ml.component.pipeline import Pipeline
from azure.ml.component.component import Component
import logging
from omegaconf import OmegaConf, open_dict, DictConfig

log = logging.getLogger(__name__)

EXPERIMENTAL_WARNING_MSG = (
    "Federated APIs are experimental and could change at any time."
)


def dataset_name_to_reference(
    component_instance: Component, dataset_names: list
) -> list:
    res = []
    if not dataset_names:
        return res
    for dataset in dataset_names:
        res.append(component_instance.outputs[dataset])
    return res


@dataclass
class StepOutput:
    """Output object from preprocess/midprocess/postprocess/training step in a federated pipeline."""

    step: Union[Component, Pipeline] = None
    outputs: List[str] = None


class FederatedPipelineBase(AMLPipelineHelper):
    """
    Base class for Federated Learning pipelines.
    """

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_base_name(self) -> str:
        """The training outputs from each silo will be stored at <base_name>/<silo_name> on the central storage.
        By default, it will return a name of 2 word. User can override this method.

        Returns:
            base_name
        """
        rv = "fl-"
        rv += generate_slug(2)
        return rv

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def preprocess(
        self, config: DictConfig, input: Optional[list] = None
    ) -> StepOutput:
        """
        Optional user-defined preprocess step. The outputs will be distributed to each silo's datastore.

        Returns:
            a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def midprocess(self, config: DictConfig, input: list) -> StepOutput:
        """
        User-defined midprocess step which reads outputs from `train` in each silo. The outputs will be distributed to each silo's datastore.

        Returns:
            a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def postprocess(self, config: DictConfig, input: list) -> StepOutput:
        """
        Optional user-defined postprocess step which reads outputs from `train` in each silo and writes to the `noncompliant_datastore`.

        Returns:
            a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def train(self, config: DictConfig, input: list, silo: DictConfig) -> StepOutput:
        """
        User-defined train step happening at each silo. This reads outputs from `preprocess` or `midprocess`, and sends outputs back to the `noncompliant_datastore`.

        Returns:
            a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    def _data_transfer(
        self, input_list: list, destination_datastore: str, base_name: str
    ) -> list:
        """Moves data `input_list` to `destination_datastore` with path prefixed by `base_name`."""
        # assume one shared ADF
        dts_name = self.config.federated_config.data_transfer_component
        try:
            data_transfer_component = self.component_load(
                dts_name  # this component is subject to change
            )
            log.info(f"Using {dts_name} as data transfer component.")
        except Exception as e:
            log.error(
                f"Please specify the data transfer component name registered in your workspace in module manifest and `federated_config.data_transfer_component` pipeline yaml."
            )
            raise (e)

        res = []
        if not input_list:
            return res
        for input in input_list:
            data_transfer_step = data_transfer_component(source_data=input)
            self.apply_smart_runsettings(data_transfer_step, datatransfer=True)
            data_transfer_step.outputs.destination_data.configure(
                datastore=destination_datastore,
                path_on_datastore=base_name + "/" + input.port_name,
            )
            res.append(data_transfer_step.outputs.destination_data)
        return res

    def _process_at_orchestrator(self, prev: StepOutput) -> list:
        """Processes outputs at the orchestrator."""
        if isinstance(prev.step, Pipeline):
            prev_output = list(prev.step.outputs.values())
        elif isinstance(prev.step, Component):
            self.apply_smart_runsettings(prev.step)
            prev_output = dataset_name_to_reference(prev.step, prev.outputs)
        else:
            raise Exception(
                f"The output of preprocess/midprocess/postprocess step must be a Pipeline object or a Component object. You are using {type(prev.step)}."
            )
        return prev_output

    def _merge_config(self):
        """Merges and simplifies federated_config."""
        # override priority: default_config < customized shared config < per-silo setting
        # everything in customized shared config have equal priority
        federated_config = self.config.federated_config
        default_config = federated_config.config_group.get("default_config", {})
        for silo_name, silo_config in federated_config.silos.items():
            customized_config = {}
            if "inherit" in silo_config:
                for inherit_config in silo_config["inherit"]:
                    customized_config = OmegaConf.merge(
                        customized_config, federated_config.config_group[inherit_config]
                    )
            log.info(
                f"=== Original config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )
            with open_dict(default_config):
                merge = OmegaConf.merge(default_config, customized_config)
            log.info(f"=== Shared config {merge}")
            with open_dict(self.config.federated_config.silos[silo_name]):
                self.config.federated_config.silos[silo_name] = OmegaConf.merge(
                    merge, silo_config
                )
                self.config.federated_config.silos[silo_name].pop("inherit", None)
            log.info(
                f"=== Merged config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )

    def _check_if_data_transfer_is_activated_and_process(
        self, prev_output, datastore_name, base_name
    ):
        deactivate_data_transfer = self.config.federated_config.deactivate_data_transfer
        if deactivate_data_transfer:
            log.info("Data transfer is disabled; training outputs will remain in silo.")
            return prev_output
        else:
            log.info(f"Moving data {prev_output} into {datastore_name}.")
            return self._data_transfer(
                input_list=prev_output,
                destination_datastore=datastore_name,
                base_name=base_name,
            )

    def _train_in_silo_once(
        self, silo_name: str, silo: DictConfig, prev_output: list, cool_name: str
    ) -> list:
        """Runs the "training" step once at one silo."""
        prev_output = self._check_if_data_transfer_is_activated_and_process(
            prev_output, silo.datastore, cool_name
        )
        train_step = self.train(self.config, input=prev_output, silo=silo)
        if isinstance(train_step.step, Pipeline):
            train_output = list(train_step.step.outputs.values())
        elif isinstance(train_step.step, Component):
            self.apply_smart_runsettings(
                train_step.step,
                target=silo.compute,
                datastore_name=silo.datastore,
            )
            train_output = dataset_name_to_reference(
                train_step.step, train_step.outputs
            )
        else:
            raise Exception(
                f"The output of train step must be a Pipeline object or a Component object. You are using {type(train_step.step)}"
            )

        silo_output = self._check_if_data_transfer_is_activated_and_process(
            train_output,
            self.config.compute.noncompliant_datastore,
            cool_name + "/" + silo_name,
        )
        return silo_output

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def build(self, config: DictConfig):
        """Constructs the federated pipeline. User does not need to modify."""

        @dsl.pipeline()
        def pipeline_function():
            self._merge_config()
            prev = self.preprocess(self.config)
            prev_output = self._process_at_orchestrator(prev) if prev else None

            for iter in range(self.config.federated_config.max_iterations):
                cool_name = self.create_base_name()
                midprocess_input = []
                for silo_name, silo in self.config.federated_config.silos.items():
                    train_output = self._train_in_silo_once(
                        silo_name, silo, prev_output, cool_name
                    )
                    midprocess_input += train_output

                prev = self.midprocess(self.config, input=midprocess_input)
                prev_output = self._process_at_orchestrator(prev) if prev else None

            prev = self.postprocess(self.config, input=prev_output)
            prev_output = self._process_at_orchestrator(prev) if prev else None

        return pipeline_function

    def pipeline_instance(self, pipeline_function, config):
        """Creates an instance of the pipeline using arguments. User does not need to modify."""
        pipeline = pipeline_function()
        return pipeline
