# -*- coding: utf-8 -*-
"""
Basic test script showing how to initialize elements and construct a beamline with horizontal and vertical orientation
of optical elements. All the computation is done through an intermediate layer called wofrywiser.
"""
import importlib

import LibWiser.Rayman as rm
import LibWiser.Foundation as Foundation
import LibWiser.Optics as Optics
import LibWiser.ToolLib as tl
import LibWiser.FermiSource as Fermi

importlib.reload(Foundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
importlib.reload(Fermi)

from matplotlib import pyplot as plt

from numpy import *
import numpy as np

from wofry.propagator.propagator import PropagationParameters, PropagationManager

from wofrywiser.beamline.beamline_elements import WiserBeamlineElement
from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from wofrywiser.propagator.wavefront1D.wise_wavefront import WiseWavefront
from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagator, WiserPropagationElements

def plot(oe, id):
    S = oe.ComputationData.S
    E = oe.ComputationData.Field

    plt.figure(id)
    plt.plot(S*1e3, abs(E)**2/max(abs(E)**2))
    plt.xlabel('mm')
    plt.title('|E| (' + oe.Name + ')')

# PARAMETERS

Lambda = 2e-9
Waist0 = 180e-6

f1_h = Fermi.Dpi.Kbh.f1
f2_h = Fermi.Dpi.Kbh.f2
M_h = f1_h / f2_h
f1_v = Fermi.Dpi.Kbv.f1
f2_v = Fermi.Dpi.Kbv.f2
M_v = f1_v / f2_v

L = 0.4
UseFigureError = True

NPools = 1
DetectorSize = 150e-6
DetectorRestPosition = 0

DoCaustics = True
NDeltaFocus = 10
RangeOfDeltaFocus = 10e-3  # estensione del delta focus
DeltaFocusOffset = 0e-3  # dove centro il delta focus (se cambio la sorgente, dovrebbe cambiare)

DeltaSourceList = np.zeros(1)  # espressa in unità di ondulatori

AngleGrazing = deg2rad(2.)

single_time = []

print(__name__)
if __name__ == '__main__':

    PropagationManager.Instance().add_propagator(WiserPropagator())

    tl.Debug.On = True
    N = 3000
    UseCustomSampling = True
    # SOURCE
    #==========================================================================
    Lambda = 2e-9
    Waist0 = 180e-6#Fermi.Waist0E(Lambda)

    s = WiserOpticalElement(name='FEL2 source',
                            boundary_shape=None,
                            isSource=True,
                            native_CoreOptics=Optics.SourceGaussian(Lambda=Lambda, Waist0=Waist0),
                            native_PositioningDirectives=Foundation.PositioningDirectives(
                                ReferTo='absolute',
                                XYCentre=[0, 0],
                                Angle=pi/4.-AngleGrazing)
                            )

    s.native_optical_element.ComputationSettings.UseSmallDisplacements = True
    s.native_optical_element.Orientation = Optics.OPTICS_ORIENTATION.ANY
    s.native_optical_element.CoreOptics.SmallDisplacements.Long = DeltaSourceList[0]
    s.native_optical_element.CoreOptics.SmallDisplacements.Rotation = 0.

    # PM1 (h)
    #==========================================================================
    pm1_h = WiserOpticalElement(name='pm1h',
                               boundary_shape=None,
                               native_CoreOptics=Optics.MirrorPlane(L=L, AngleGrazing=AngleGrazing),
                               native_PositioningDirectives=Foundation.PositioningDirectives(
                                   ReferTo='upstream',
                                   PlaceWhat='centre',
                                   PlaceWhere='centre',
                                   Distance=20.)
                               )

    pm1_h.native_optical_element.ComputationSettings.UseFigureError = False
    pm1_h.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    pm1_h.native_optical_element.ComputationSettings.Ignore = False          # Lo user decide di non simulare lo specchio ()
    pm1_h.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling # l'utente decide di impostare a mano il campionamento
    pm1_h.native_optical_element.ComputationSettings.NSamples = N

    # PM2 (h)
    # ==========================================================================
    pm2_h = WiserOpticalElement(name='pm2h',
                                boundary_shape=None,
                                native_CoreOptics=Optics.MirrorPlane(L=L, AngleGrazing=AngleGrazing),
                                native_PositioningDirectives=Foundation.PositioningDirectives(
                                    ReferTo='upstream',
                                    PlaceWhat='centre',
                                    PlaceWhere='centre',
                                    Distance=20.)
                                )

    pm2_h.native_optical_element.ComputationSettings.UseFigureError = False
    pm2_h.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    pm2_h.native_optical_element.ComputationSettings.Ignore = False  # Lo user decide di non simulare lo specchio ()
    pm2_h.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    pm2_h.native_optical_element.ComputationSettings.NSamples = N

    # KB(v)
    # ==========================================================================
    kb_v = WiserOpticalElement(name='kb_v',
                               boundary_shape=None,
                               native_CoreOptics=Optics.MirrorElliptic(f1=f1_v, f2=f2_v, L=L, Alpha=AngleGrazing),
                               native_PositioningDirectives=Foundation.PositioningDirectives(
                                   ReferTo='source',
                                   PlaceWhat='upstream focus',
                                   PlaceWhere='centre')
                               )

    # ----- Impostazioni KB
    kb_v.native_optical_element.CoreOptics.ComputationSettings.UseFigureError = False
    kb_v.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.VERTICAL
    kb_v.native_optical_element.CoreOptics.ComputationSettings.UseRoughness = False
    kb_v.native_optical_element.CoreOptics.ComputationSettings.UseSmallDisplacements = False  # serve per traslare/ruotare l'EO
    kb_v.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    kb_v.native_optical_element.ComputationSettings.NSamples = N
    # kb_v.native_optical_element.CoreOptics.FigureErrorLoad(File='DATA/LTP/kbh.txt', Step=2e-3, AmplitudeScaling=-1e-3)

    # KB(h)
    # ==========================================================================
    kb_h = WiserOpticalElement(name='kb_h',
                               boundary_shape=None,
                               native_CoreOptics=Optics.MirrorElliptic(f1=f1_h, f2=f2_h, L=L, Alpha=AngleGrazing),
                               native_PositioningDirectives=Foundation.PositioningDirectives(
                                   ReferTo='source',
                                   PlaceWhat='upstream focus',
                                   PlaceWhere='centre')
                               )

    # ----- Impostazioni KB
    kb_h.native_optical_element.CoreOptics.ComputationSettings.UseFigureError = True
    kb_h.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL
    kb_h.native_optical_element.CoreOptics.ComputationSettings.UseRoughness = False
    kb_h.native_optical_element.CoreOptics.ComputationSettings.UseSmallDisplacements = False  # serve per traslare/ruotare l'EO
    kb_h.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    kb_h.native_optical_element.ComputationSettings.NSamples = N
    kb_h.native_optical_element.CoreOptics.FigureErrorLoad(File='kbh.txt', Step=2e-3, AmplitudeScaling=-1e-3)

    # detector (v)
    # ==========================================================================
    d_v = WiserOpticalElement(name='detector_v',
                              boundary_shape=None,
                              native_CoreOptics=Optics.Detector(L=DetectorSize, AngleGrazing=deg2rad(90)),
                              native_PositioningDirectives=Foundation.PositioningDirectives(
                                  ReferTo='upstream',
                                  PlaceWhat='centre',
                                  PlaceWhere='downstream focus')
                              )

    d_v.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling
    d_v.native_optical_element.ComputationSettings.NSamples = N                          # come sopra. In teoria il campionamento può essere specificato elemento per elmeento
    d_v.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.VERTICAL

    # detector (h)
    # ==========================================================================
    d_h = WiserOpticalElement(name='detector_h',
                              boundary_shape=None,
                              native_CoreOptics=Optics.Detector(L=DetectorSize, AngleGrazing=deg2rad(90)),
                              native_PositioningDirectives=Foundation.PositioningDirectives(
                                  ReferTo='upstream',
                                  PlaceWhat='centre',
                                  PlaceWhere='downstream focus')
                              )

    d_h.native_optical_element.ComputationSettings.UseCustomSampling = UseCustomSampling
    d_h.native_optical_element.ComputationSettings.NSamples = N                          # come sopra. In teoria il campionamento può essere specificato elemento per elmeento
    d_h.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    beamline = WiserPropagationElements()
    beamline._WisePropagationElements__wise_propagation_elements.ComputationSettings.OrientationToCompute = [Optics.OPTICS_ORIENTATION.HORIZONTAL, Optics.OPTICS_ORIENTATION.VERTICAL]#, Optics.OPTICS_ORIENTATION.VERTICAL]
    wavefront = WiseWavefront(wise_computation_results=None)

    beamline.add_beamline_element(WiserBeamlineElement(optical_element=s))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=pm1_h))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    if not pm1_h.native_optical_element.ComputationSettings.Ignore: plot(pm1_h.native_optical_element, 'pm1_h')

    beamline.add_beamline_element(WiserBeamlineElement(optical_element=pm2_h))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    if not pm2_h.native_optical_element.ComputationSettings.Ignore: plot(pm2_h.native_optical_element, 'pm2_h')

    beamline.add_beamline_element(WiserBeamlineElement(optical_element=kb_v))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    plot(kb_v.native_optical_element, 'kb_v')

    beamline.add_beamline_element(WiserBeamlineElement(optical_element=kb_h))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    plot(kb_h.native_optical_element, 'kb_h')

    # DETECTOR V
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=d_v))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    plot(d_v.native_optical_element, 'd_v')

    # # DETECTOR H
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=d_h))

    parameters = PropagationParameters(wavefront=wavefront, propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", True)
    parameters.set_additional_parameters("NPools", 1)
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    plot(d_h.native_optical_element, 'd_h')

    # print(beamline.get_wise_propagation_elements()) # comodo per controllare la rappresentazione interna di Beamline Element

    parameters = PropagationParameters(wavefront=WiseWavefront(wise_computation_results=None), propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", False)
    parameters.set_additional_parameters("NPools", 5)

    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)

    plot(d_v.native_optical_element, 'd_v complete')

    # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    # print(wise_propagation_elements.get_wise_propagation_element(-2 if parameters.get_additional_parameter("single_propagation") else 0).Name, type(wise_propagation_elements.get_wise_propagation_element(-2 if parameters.get_additional_parameter("single_propagation") else 0)))
    # print('FULL BEAMLINE')
    # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    # parameters = PropagationParameters(wavefront=WiseWavefront(wise_computation_results=None), propagation_elements=beamline)
    # parameters.set_additional_parameters("single_propagation", False)
    # parameters.set_additional_parameters("NPools", 1)

    # wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WisePropagator.HANDLER_NAME)

    # plot(pm1_h.native_optical_element, 'pm1_h')
    plot(d_h.native_optical_element, 'd_h complete')

    plt.show()
