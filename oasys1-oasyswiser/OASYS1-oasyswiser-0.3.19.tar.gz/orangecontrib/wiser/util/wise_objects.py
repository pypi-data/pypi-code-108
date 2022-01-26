class WiserPreInputData:
	NONE = "None"

	def __init__(self,
				 figure_error_file=NONE,
				 figure_error_step=0.0,
				 figure_error_amplitude_scaling=1.0,
				 figure_user_units_to_m=1.0,
				 roughness_file=NONE,
				 roughness_x_scaling=1.0,
				 roughness_y_scaling=1.0
				 ):
		super().__init__()

		self.figure_error_file = figure_error_file
		self.figure_error_step = figure_error_step
		self.figure_error_amplitude_scaling = figure_error_amplitude_scaling
		self.figure_user_units_to_m = figure_user_units_to_m

		self.roughness_file = roughness_file
		self.roughness_x_scaling = roughness_x_scaling
		self.roughness_y_scaling = roughness_y_scaling


from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagationElements
from wofrywiser.propagator.wavefront1D.wise_wavefront import WiserWavefront
from wofrywiser.beamline.beamline_elements import WiserBeamlineElement, WiserOpticalElement

import copy


class WiserData(object):

	def __init__(self, wise_beamline=WiserPropagationElements(), wise_wavefront=WiserWavefront()):
		super().__init__()

		self.wise_beamline = wise_beamline
		self.wise_wavefront = wise_wavefront

	def duplicate(self):
		duplicated_wise_beamline = None

		if not self.wise_beamline is None:
			duplicated_wise_beamline = WiserPropagationElements()
			for beamline_element in self.wise_beamline.get_propagation_elements():
				duplicated_wise_optical_element = copy.deepcopy(beamline_element.get_optical_element().native_optical_element)

				duplicated_wise_beamline.add_beamline_element(WiserBeamlineElement(optical_element=WiserOpticalElement(native_OpticalElement=duplicated_wise_optical_element)))

		duplicated_wise_wavefront = None
		if not self.wise_wavefront is None:
			duplicated_wise_wavefront = WiserWavefront(wiser_computation_results=copy.deepcopy(self.wise_wavefront.wiser_computation_result))

		return WiserData(wise_beamline=duplicated_wise_beamline, wise_wavefront=duplicated_wise_wavefront)
