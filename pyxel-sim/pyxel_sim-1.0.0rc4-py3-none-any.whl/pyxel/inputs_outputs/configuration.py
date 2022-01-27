#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Configuration loader."""

import typing as t
from functools import partial
from pathlib import Path
from shutil import copy2

import attr
import yaml

from pyxel import __version__ as version
from pyxel.calibration import Algorithm, Calibration

from ..detectors import (
    CCD,
    CMOS,
    CCDCharacteristics,
    CCDGeometry,
    CMOSCharacteristics,
    CMOSGeometry,
    Environment,
    Material,
)
from ..dynamic import Dynamic
from ..evaluator import evaluate_reference
from ..parametric import ParameterValues, Parametric
from ..pipelines import DetectionPipeline, ModelFunction, ModelGroup
from ..single import Single
from .calibration_outputs import (  # CalibrationPlot,; ChampionsPlot,; FittingPlot,; PopulationPlot,
    CalibrationOutputs,
)
from .dynamic_outputs import DynamicOutputs
from .outputs import PlotArguments
from .parametric_outputs import ParametricOutputs  # , ParametricPlot
from .single_outputs import SingleOutputs  # , SinglePlot


@attr.s
class Configuration:
    """Configuration class."""

    pipeline: DetectionPipeline = attr.ib(init=False)
    single: t.Optional[Single] = attr.ib(default=None)
    parametric: t.Optional[Parametric] = attr.ib(default=None)
    calibration: t.Optional[Calibration] = attr.ib(default=None)
    dynamic: t.Optional[Dynamic] = attr.ib(default=None)
    ccd_detector: t.Optional[CCD] = attr.ib(default=None)
    cmos_detector: t.Optional[CMOS] = attr.ib(default=None)


def load(yaml_file: t.Union[str, Path]) -> Configuration:
    """Load a YAML file.

    Parameters
    ----------
    yaml_file

    Returns
    -------
    configuration: Configuration
    """
    filename = Path(yaml_file).resolve()
    if not filename.exists():
        raise FileNotFoundError(f"Cannot find configuration file '{filename}'.")
    with filename.open("r") as file_obj:
        return build_configuration(load_yaml(file_obj))


def load_yaml(stream: t.Union[str, t.IO]) -> t.Any:
    """Load a YAML document.

    Parameters
    ----------
    stream

    Returns
    -------
    result: dict

    """
    result = yaml.load(stream, Loader=yaml.SafeLoader)
    return result


def to_plot_arguments(dct: t.Optional[dict]) -> t.Optional[PlotArguments]:
    """Create a PlotArguments class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    PlotArguments
    """
    if dct is None:
        return None
    return PlotArguments(**dct)


# def to_single_plot(dct: t.Optional[dict]) -> t.Optional[SinglePlot]:
#     """Create a SinglePlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     SinglePlot
#     """
#     if dct is None:
#         return None
#     dct.update({"plot_args": to_plot_arguments(dct["plot_args"])})
#     return SinglePlot(**dct)


def to_single_outputs(dct: dict) -> SingleOutputs:
    """Create a SingleOutputs class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    SingleOutputs
    """
    # dct.update({"single_plot": to_single_plot(dct["single_plot"])})
    return SingleOutputs(**dct)


def to_single(dct: dict) -> Single:
    """Create a Single class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Single
    """
    dct.update({"outputs": to_single_outputs(dct["outputs"])})
    return Single(**dct)


# TODO: Sampling uses single plot for now
def to_dynamic_outputs(dct: dict) -> DynamicOutputs:
    """Create a DynamicOutputs class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    DynamicOutputs
    """
    # dct.update({"single_plot": to_single_plot(dct["single_plot"])})
    return DynamicOutputs(**dct)


def to_dynamic(dct: dict) -> Dynamic:
    """Create a Sampling class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Dynamic
    """
    dct.update({"outputs": to_dynamic_outputs(dct["outputs"])})
    return Dynamic(**dct)


# def to_parametric_plot(dct: t.Optional[dict]) -> t.Optional[ParametricPlot]:
#     """Create a ParametricPlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     ParametricPlot
#     """
#     if dct is None:
#         return None
#     dct.update({"plot_args": to_plot_arguments(dct["plot_args"])})
#     return ParametricPlot(**dct)


def to_parametric_outputs(dct: dict) -> ParametricOutputs:
    """Create a ParametricOutputs class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    ParametricOutputs
    """
    # dct.update({"parametric_plot": to_parametric_plot(dct["parametric_plot"])})
    return ParametricOutputs(**dct)


def to_parameters(dct: dict) -> ParameterValues:
    """Create a ParameterValues class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    ParameterValues
    """
    return ParameterValues(**dct)


def to_parametric(dct: dict) -> Parametric:
    """Create a Parametric class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Parametric
    """
    dct.update(
        {"parameters": [to_parameters(param_dict) for param_dict in dct["parameters"]]}
    )
    dct.update({"outputs": to_parametric_outputs(dct["outputs"])})
    return Parametric(**dct)


# def to_champions_plot(dct: t.Optional[dict]) -> t.Optional[ChampionsPlot]:
#     """Create a ChampionsPlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     ChampionsPlot
#     """
#     if dct is None:
#         return None
#     dct.update({"plot_args": to_plot_arguments(dct["plot_args"])})
#     return ChampionsPlot(**dct)
#
#
# def to_population_plot(dct: t.Optional[dict]) -> t.Optional[PopulationPlot]:
#     """Create a PopulatonPlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     PopulationPlot
#     """
#     if dct is None:
#         return None
#     dct.update({"plot_args": to_plot_arguments(dct["plot_args"])})
#     return PopulationPlot(**dct)
#
#
# def to_fitting_plot(dct: t.Optional[dict]) -> t.Optional[FittingPlot]:
#     """Create a FittingPlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     FittingPlot
#     """
#     if dct is None:
#         return None
#     dct.update({"plot_args": to_plot_arguments(dct["plot_args"])})
#     return FittingPlot(**dct)
#
#
# def to_calibration_plot(dct: t.Optional[dict]) -> t.Optional[CalibrationPlot]:
#     """Create a CalibrationPlot class from a dictionary.
#
#     Parameters
#     ----------
#     dct
#
#     Returns
#     -------
#     CalibrationPlot
#     """
#     if dct is None:
#         return None
#     else:
#         if "champions_plot" in dct:
#             dct.update({"champions_plot": to_champions_plot(dct["champions_plot"])})
#         if "population_plot" in dct:
#             dct.update({"population_plot": to_population_plot(dct["population_plot"])})
#         if "fitting_plot" in dct:
#             dct.update({"fitting_plot": to_fitting_plot(dct["fitting_plot"])})
#         return CalibrationPlot(**dct)


def to_calibration_outputs(dct: dict) -> CalibrationOutputs:
    """Create a CalibrationOutputs class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CalibrationOutputs
    """
    # dct.update({"calibration_plot": to_calibration_plot(dct["calibration_plot"])})
    return CalibrationOutputs(**dct)


def to_algorithm(dct: t.Optional[dict]) -> t.Optional[Algorithm]:
    """Create an Algorithm class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Algorithm
    """
    if dct is None:
        return None
    return Algorithm(**dct)


def to_callable(dct: dict) -> t.Callable:
    """Create a callable from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    callable
    """
    func = evaluate_reference(dct["func"])
    arguments = dct["arguments"]
    if arguments is None:
        arguments = {}
    return partial(func, **arguments)


def to_calibration(dct: dict) -> Calibration:
    """Create a Calibration class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Calibration
    """
    dct.update({"outputs": to_calibration_outputs(dct["outputs"])})
    dct.update({"fitness_function": to_callable(dct["fitness_function"])})
    dct.update({"algorithm": to_algorithm(dct["algorithm"])})
    dct.update(
        {"parameters": [to_parameters(param_dict) for param_dict in dct["parameters"]]}
    )
    dct["result_input_arguments"] = [
        to_parameters(value) for value in dct.get("result_input_arguments", {})
    ]

    return Calibration(**dct)


def to_ccd_geometry(dct: dict) -> CCDGeometry:
    """Create a CCDGeometry class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CCDGeometry
    """

    return CCDGeometry(**dct)


def to_cmos_geometry(dct: dict) -> CMOSGeometry:
    """Create a CMOSGeometry class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CMOSGeometry
    """
    return CMOSGeometry(**dct)


def to_material(dct: t.Optional[dict]) -> Material:
    """Create a Material class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Material
    """
    if dct is None:
        dct = {}
    return Material(**dct)


def to_environment(dct: t.Optional[dict]) -> Environment:
    """Create an Environment class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Environment
    """
    if dct is None:
        dct = {}
    return Environment(**dct)


def to_ccd_characteristics(dct: t.Optional[dict]) -> CCDCharacteristics:
    """Create a CCDCharacteristics class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CCDCharacteristics
    """
    if dct is None:
        dct = {}
    return CCDCharacteristics(**dct)


def to_cmos_characteristics(dct: t.Optional[dict]) -> CMOSCharacteristics:
    """Create a CMOSCharacteristics class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CMOSCharacteristics
    """
    if dct is None:
        dct = {}
    return CMOSCharacteristics(**dct)


def to_ccd(dct: dict) -> CCD:
    """Create a CCD class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CCD
    """
    return CCD(
        geometry=to_ccd_geometry(dct["geometry"]),
        material=to_material(dct["material"]),
        environment=to_environment(dct["environment"]),
        characteristics=to_ccd_characteristics(dct["characteristics"]),
    )


def to_cmos(dct: dict) -> CMOS:
    """Create a CMOS class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    CMOS
    """
    return CMOS(
        geometry=to_cmos_geometry(dct["geometry"]),
        material=to_material(dct["material"]),
        environment=to_environment(dct["environment"]),
        characteristics=to_cmos_characteristics(dct["characteristics"]),
    )


def to_model_function(dct: dict) -> ModelFunction:
    """Create a ModelFunction class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    ModelFunction
    """
    dct.update({"func": evaluate_reference(dct["func"])})
    return ModelFunction(**dct)


def to_model_group(
    models_list: t.Optional[t.Sequence[dict]], name: str
) -> t.Optional[ModelGroup]:
    """Create a ModelGroup class from a dictionary.

    Parameters
    ----------
    models_list
    name

    Returns
    -------
    ModelGroup
    """
    if models_list is None:
        return None
    models = [to_model_function(model_dict) for model_dict in models_list]
    return ModelGroup(models=models, name=name)


def to_pipeline(dct: dict) -> DetectionPipeline:
    """Create a DetectionPipeline class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    DetectionPipeline
    """
    for model_group_name in dct.keys():
        dct.update(
            {
                model_group_name: to_model_group(
                    models_list=dct[model_group_name], name=model_group_name
                )
            }
        )
    return DetectionPipeline(**dct)


def build_configuration(dct: dict) -> Configuration:
    """Create a Configuration class from a dictionary.

    Parameters
    ----------
    dct

    Returns
    -------
    Configuration
    """

    configuration = Configuration()  # type: Configuration

    configuration.pipeline = to_pipeline(dct["pipeline"])

    if "single" in dct:
        configuration.single = to_single(dct["single"])
    elif "parametric" in dct:
        configuration.parametric = to_parametric(dct["parametric"])
    elif "calibration" in dct:
        configuration.calibration = to_calibration(dct["calibration"])
    elif "dynamic" in dct:
        configuration.dynamic = to_dynamic(dct["dynamic"])
    else:
        raise ValueError("No mode configuration provided.")

    if "ccd_detector" in dct:
        configuration.ccd_detector = to_ccd(dct["ccd_detector"])
    elif "cmos_detector" in dct:
        configuration.cmos_detector = to_cmos(dct["cmos_detector"])
    else:
        raise (ValueError("No detector configuration provided."))

    return configuration


def save(input_filename: t.Union[str, Path], output_dir: Path) -> Path:
    """TBW."""

    input_file = Path(input_filename)
    copy2(input_file, output_dir)

    # TODO: sort filenames ?
    copied_input_file_it = output_dir.glob("*.yaml")  # type: t.Iterator[Path]
    copied_input_file = next(copied_input_file_it)  # type: Path

    with copied_input_file.open("a") as file:
        file.write("\n#########")
        file.write(f"\n# Pyxel version: {version}")
        file.write("\n#########")

    return copied_input_file
