# import pyxel
from pyxel.detectors import Detector

# @pyxel.register(group='charge_generation', name='my_class_model')
# class MyClassModel:
#     def __call__(self, detector: Detector, level: int, noise: float = 2.0) -> Detector:
#         setattr(detector, "level", level)
#         setattr(detector, "noise", noise)
#         return detector


# @pyxel.register(group='charge_generation', name='my_other_class_model')
# class MyOtherClassModel:
#     def __call__(self, detector: Detector, std: float = 2.0) -> Detector:
#         setattr(detector, "std", std)
#         return detector


# def my_function_model(detector: Detector, level, noise: float = 2.0) -> Detector:
#     # set a new attribute so it can be checked later
#     setattr(detector, "level", level)
#     setattr(detector, "noise", noise)
#     return detector


# pyxel.register(group='charge_generation', maybe_func=my_function_model)


# @pyxel.register(group='charge_generation', name='my_dec_model_class')
class MyDecoratedModel:
    def __call__(self, detector: Detector, class_std=1.0):
        setattr(detector, "class_std", class_std)
        return detector


# @pyxel.register(group='charge_generation', name='my_dec_model_func')
# def my_decorated_function(detector: Detector, func_std=2.0):
#     setattr(detector, "func_std", func_std)
#     return detector


registry_map = {
    "photon_generation": [
        {"func": "pyxel.models.photon_generation.load_image"},
        {"func": "pyxel.models.photon_generation.illumination"},
        {"func": "pyxel.models.photon_generation.shot_noise"},
    ],
    "optics": [],
    "charge_generation": [
        {
            "func": "pyxel.models.charge_generation.simple_conversion",
            "name": "photoelectrons",
        },
        {"func": "pyxel.models.run_tars", "name": "tars"},
    ],
    "charge_collection": [
        {
            "func": "pyxel.models.charge_collection.fix_pattern_noise",
            "type": "ccd",
        },
        {
            "func": "pyxel.models.charge_collection.simple_full_well",
            "name": "full_well",
        },
    ],
    "charge_transfer": [{"func": "pyxel.models.charge_transfer.cdm", "type": "ccd"}],
    "charge_measurement": [
        {
            "func": "pyxel.models.charge_measurement.output_node_noise",
            "type": "ccd",
        },
        {
            "func": "pyxel.models.signal_transfer.nghxrg.nghxrg.ktc_bias_noise",
            "type": "cmos",
        },
        {"func": "pyxel.models.signal_transfer.nghxrg.nghxrg.white_read_noise"},
    ],
    "signal_transfer": [
        {
            "func": "pyxel.models.signal_transfer.nghxrg.nghxrg.corr_pink_noise",
            "type": "cmos",
        },
        {
            "func": "pyxel.models.signal_transfer.nghxrg.nghxrg.uncorr_pink_noise",
            "type": "cmos",
        },
        {
            "func": "pyxel.models.signal_transfer.nghxrg.nghxrg.acn_noise",
            "type": "cmos",
        },
    ],
    "readout_electronics": [
        {
            "func": "pyxel.models.signal_transfer.nghxrg.nghxrg.pca_zero_noise",
            "type": "cmos",
        }
    ],
}
