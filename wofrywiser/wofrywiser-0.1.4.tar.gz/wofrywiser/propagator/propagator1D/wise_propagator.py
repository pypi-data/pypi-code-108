import numpy

import scipy.constants as codata
angstroms_to_eV = codata.h*codata.c/codata.e*1e10

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
from wofry.propagator.propagator import Propagator1D, PropagationParameters, PropagationElements, PropagationManager, PropagationMode

from wofrywiser.propagator.wavefront1D.wise_wavefront import WiserWavefront
from wofrywiser.beamline.beamline_elements import WiserBeamlineElement

from LibWiser import Foundation, Optics

WISE_APPLICATION = "All"

class WiserPropagationElements(PropagationElements):

    __wise_propagation_elements = None

    def __init__(self):
        super(WiserPropagationElements, self).__init__()

        self.__wise_propagation_elements = Foundation.BeamlineElements()

    def add_beamline_element(self, beamline_element=WiserBeamlineElement()):
        super(WiserPropagationElements, self).add_beamline_element(beamline_element)

        self.__wise_propagation_elements.Append(beamline_element.get_optical_element().native_optical_element)

    def insert_beamline_element(self, index, new_element=WiserBeamlineElement(), mode=PropagationElements.INSERT_BEFORE):

        existing_element_name = self.get_wise_propagation_element(index).Name  # Has to be called before calling super()

        super(WiserPropagationElements, self).insert_beamline_element(index, new_element, mode)

        self.__wise_propagation_elements.Insert(NewItem=new_element.get_optical_element().native_optical_element,
                                                ExistingName=existing_element_name,
                                                Mode=1)

    def add_beamline_elements(self, beamline_elements=[]):
        for beamline_element in beamline_elements:
            self.add_beamline_element(beamline_element)

    def get_wise_propagation_element(self, index):
        return self.get_propagation_element(index).get_optical_element().native_optical_element

    def get_wise_propagation_elements(self):
        return self.__wise_propagation_elements

    def refresh_wise_positions(self):
        self.get_wise_propagation_elements().RefreshPositions()

class WiserPropagator(Propagator1D):

    HANDLER_NAME = "WISER_PROPAGATOR"

    def get_handler_name(self):
        return self.HANDLER_NAME

    def do_propagation(self, parameters=PropagationParameters()):
        wavefront = parameters.get_wavefront()

        if not wavefront is None:
            is_generic_wavefront = isinstance(wavefront, GenericWavefront1D)
        else:
            is_generic_wavefront = False

        try:
            if not is_generic_wavefront and not wavefront is None:
                if isinstance(wavefront, WiserWavefront):
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Wavefront cannot be managed by this propagator", str(e), QMessageBox.Ok)
            self.setStatusMessage("Wavefront cannot be managed by this propagator")

        if is_generic_wavefront:
            wavefront = WiserWavefront.fromGenericWavefront(wavefront)

        wise_propagation_elements = parameters.get_PropagationElements()

        beamline = wise_propagation_elements.get_wise_propagation_elements()
        beamline.ComputationSettings.NPools = int(parameters.get_additional_parameter("NPools"))

        # Element -1 is the last element of the array
        optical_element_end = wise_propagation_elements.get_propagation_element(-1).get_optical_element()

        oeEnd = optical_element_end.native_optical_element
        if parameters.get_additional_parameter("single_propagation"):
            oeStart = oeEnd.GetParent(SameOrientation=True, OnlyReference=False)
        else:
            oeStart = wise_propagation_elements.get_wise_propagation_element(0)

        # oeEnd = optical_element_end.native_optical_element
        # oeStart is the first element [0], or the previous element [-2]
        # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # print(wise_propagation_elements.get_wise_propagation_element(-2 if parameters.get_additional_parameter("single_propagation") else 0).Name, type(wise_propagation_elements.get_wise_propagation_element(-2 if parameters.get_additional_parameter("single_propagation") else 0)))
        # print(oeStart.Name, oeEnd.Name)
        # print(oeStart.CoreOptics.Orientation, oeEnd.CoreOptics.Orientation)
        # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # oeStart =wise_propagation_elements.get_wise_propagation_element(-2 if parameters.get_additional_parameter("single_propagation") else 0)# oeEnd.GetParent(SameOrientation=True)

        if PropagationManager.Instance().get_propagation_mode(WISE_APPLICATION) == PropagationMode.STEP_BY_STEP or parameters.get_additional_parameter("is_full_propagator"):

            beamline.RefreshPositions()
            beamline.ComputeFields(oeStart=oeStart, oeEnd=oeEnd, Verbose=False)

            result = WiserWavefront(wiser_computation_results=oeEnd.ComputationData)
        elif PropagationManager.Instance().get_propagation_mode(WISE_APPLICATION) == PropagationMode.WHOLE_BEAMLINE:

            beamline.RefreshPositions()
            beamline.ComputeFields()

            result = WiserWavefront(wiser_computation_results=oeEnd.ComputationData)
            # result = wavefront
        else:
            result = None

        if is_generic_wavefront:
            return None if result is None else result.toGenericWavefront()
        else:
            return result


