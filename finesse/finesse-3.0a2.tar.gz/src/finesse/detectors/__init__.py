"""The ``detectors`` sub-module contains various non-physical detectors that can be used
to probe to simulation at any point.

Listed below are all the sub-modules within ``detectors`` with brief descriptions of
what is contained in each.
"""

from finesse.detectors.general import (
    Detector,
    MaskedDetector,
    NoiseDetector,
    SymbolDetector,
)
from finesse.detectors.amplitude_detector import AmplitudeDetector
from finesse.detectors.field_detector import FieldDetector
from finesse.detectors.bpdetector import BeamProperty, BeamPropertyDetector
from finesse.detectors.camera import (
    Camera,
    CCDCamera,
    CCD,
    CCDScanLine,
    CCDPixel,
    ComplexCamera,
    FieldCamera,
    FieldScanLine,
    FieldPixel,
)
from finesse.detectors.cavity_detector import CavityProperty, CavityPropertyDetector
from finesse.detectors.gouy import Gouy
from finesse.detectors.astigmatism_detector import AstigmatismDetector
from finesse.detectors.knmdetector import KnmDetector
from finesse.detectors.mismatch_detector import ModeMismatchDetector
from finesse.detectors.motion_detector import MotionDetector
from finesse.detectors.powerdetector import (
    PowerDetector,
    PowerDetectorDemod1,
    PowerDetectorDemod2,
)
from finesse.detectors.quantum_noise_detector import (
    QuantumNoiseDetector,
    QuantumNoiseDetectorDemod1,
    QuantumNoiseDetectorDemod2,
    QuantumShotNoiseDetector,
    QuantumShotNoiseDetectorDemod1,
    QuantumShotNoiseDetectorDemod2,
    GeneralQuantumNoiseDetector,
)
from .optimal_q import OptimalQ


__all__ = (
    "Detector",
    "MaskedDetector",
    "NoiseDetector",
    "SymbolDetector",
    "AmplitudeDetector",
    "FieldDetector",
    "BeamProperty",
    "BeamPropertyDetector",
    "Camera",
    "CCDCamera",
    "CCD",
    "CCDScanLine",
    "CCDPixel",
    "ComplexCamera",
    "FieldCamera",
    "FieldScanLine",
    "FieldPixel",
    "CavityProperty",
    "CavityPropertyDetector",
    "Gouy",
    "AstigmatismDetector",
    "KnmDetector",
    "ModeMismatchDetector",
    "MotionDetector",
    "PowerDetector",
    "PowerDetectorDemod1",
    "PowerDetectorDemod2",
    "QuantumNoiseDetector",
    "QuantumNoiseDetectorDemod1",
    "QuantumNoiseDetectorDemod2",
    "QuantumShotNoiseDetector",
    "QuantumShotNoiseDetectorDemod1",
    "QuantumShotNoiseDetectorDemod2",
    "GeneralQuantumNoiseDetector",
    "OptimalQ",
)
