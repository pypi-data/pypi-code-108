#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

from pyxel.pipelines import ModelFunction, ModelGroup


class DetectionPipeline:
    """TBW."""

    # TODO: develop a ModelGroupList class ? See #333
    def __init__(
        self,  # TODO: Too many instance attributes
        photon_generation: t.Optional[ModelGroup] = None,
        optics: t.Optional[ModelGroup] = None,
        phasing: t.Optional[ModelGroup] = None,
        charge_generation: t.Optional[ModelGroup] = None,
        charge_collection: t.Optional[ModelGroup] = None,
        charge_transfer: t.Optional[ModelGroup] = None,
        charge_measurement: t.Optional[ModelGroup] = None,
        signal_transfer: t.Optional[ModelGroup] = None,
        readout_electronics: t.Optional[ModelGroup] = None,
        doc: t.Optional[str] = None,
    ):
        self._is_running = False
        self.doc = doc

        self.photon_generation = photon_generation  # type: t.Optional[ModelGroup]
        self.optics = optics  # type: t.Optional[ModelGroup]
        self.phasing = phasing  # type: t.Optional[ModelGroup] # MKID-array
        self.charge_generation = charge_generation  # type: t.Optional[ModelGroup]
        self.charge_collection = charge_collection  # type: t.Optional[ModelGroup]
        self.charge_measurement = charge_measurement  # type: t.Optional[ModelGroup]
        self.readout_electronics = readout_electronics  # type: t.Optional[ModelGroup]
        self.charge_transfer = charge_transfer  # type: t.Optional[ModelGroup]  # CCD
        self.signal_transfer = signal_transfer  # type: t.Optional[ModelGroup]  # CMOS

        # TODO: this defines the order of steps in the pipeline.
        #       The ModelGroupList could do this. Is it really needed?
        self.MODEL_GROUPS = (
            "photon_generation",
            "optics",
            "phasing",
            "charge_generation",
            "charge_collection",
            "charge_transfer",
            "charge_measurement",
            "signal_transfer",
            "readout_electronics",
        )  # type: t.Tuple[str, ...]

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<is_running={self._is_running!r}, doc={self.doc!r}>"

    def __iter__(self) -> t.Iterable[ModelFunction]:
        for model in self.MODEL_GROUPS:
            models_grp = getattr(self, model)  # type: t.Optional[ModelGroup]
            if models_grp:
                yield from models_grp

    @property
    def model_group_names(self) -> t.Tuple[str, ...]:
        """TBW."""
        return self.MODEL_GROUPS

    @property
    def is_running(self) -> bool:
        """Return the running state of this pipeline."""
        return self._is_running

    def abort(self) -> None:
        """TBW."""
        self._is_running = False

    # TODO: Is this method used ?
    def get_model(self, name: str) -> ModelFunction:
        """Return a ModelFunction object for the specified model name.

        Parameters
        ----------
        name: str
            Name of the model.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            If model with the specified name is not found.
        """
        for group_name in self.model_group_names:  # type: str
            model_group = getattr(self, group_name)  # type: ModelGroup
            if model_group:
                for model in model_group.models:  # type: ModelFunction
                    if name == model.name:
                        return model
        raise AttributeError("Model has not been found.")
