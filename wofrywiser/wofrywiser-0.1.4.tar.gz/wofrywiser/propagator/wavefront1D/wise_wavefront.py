import numpy

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D, WavefrontDimension
from wofry.propagator.decorators import WavefrontDecorator

from LibWiser.Foundation import ComputationResults

class WiserWavefront(WavefrontDecorator):

    def __init__(self,
                 wiser_computation_results=ComputationResults()):

        self.wiser_computation_result = wiser_computation_results

    def get_dimension(self):
        return WavefrontDimension.ONE

    def toGenericWavefront(self):
        wavelength = self.wiser_computation_result.Lambda
        position = self.wiser_computation_result.S
        electric_field = numpy.real(self.wiser_computation_result.Field) + 1j*numpy.imag(self.wiser_computation_result.Field)

        return GenericWavefront1D.initialize_wavefront_from_arrays(x_array=position, y_array=electric_field, wavelength=wavelength)

    @classmethod
    def fromGenericWavefront(cls, wavefront):
        wiser_computation_result = ComputationResults()
        wiser_computation_result.Lambda = wavefront.get_wavelength()
        wiser_computation_result.S = wavefront.get_abscissas()
        wiser_computation_result.Field = wavefront.get_complex_amplitude()

        return WiserWavefront(wiser_computation_results=wiser_computation_result)
