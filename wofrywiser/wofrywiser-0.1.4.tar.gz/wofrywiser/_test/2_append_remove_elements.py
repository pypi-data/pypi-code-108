# -*- coding: utf-8 -*-
"""
Test script to try whether adding and removing an optical element still results in correct calculations.
"""
import PyQt5

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

from LibWiser import ToolLib as tl
from wofry.propagator.propagator import PropagationParameters, PropagationManager

from wofrywiser.beamline.beamline_elements import WiserBeamlineElement
from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from wofrywiser.propagator.wavefront1D.wise_wavefront import WiseWavefront
from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagator, WiserPropagationElements

def plot(oe):
    tl.CommonPlots.IntensityAtOpticalElement(oe)

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

    ww_s = WiserOpticalElement(name='FEL2 source',
                               boundary_shape=None,
                               isSource=True,
                               native_CoreOptics=Optics.SourceGaussian(Lambda=Lambda, Waist0=Waist0),
                               native_PositioningDirectives=Foundation.PositioningDirectives(
                                   ReferTo='absolute',
                                   XYCentre=[0, 0],
                                   Angle=pi/4.-AngleGrazing)
                               )

    s = ww_s.native_optical_element # Wiser optical element
    s.ComputationSettings.UseSmallDisplacements = True
    s.Orientation = Optics.OPTICS_ORIENTATION.ANY
    s.CoreOptics.SmallDisplacements.Long = DeltaSourceList[0]
    s.CoreOptics.SmallDisplacements.Rotation = 0.

    # PM1 (h)
    #==========================================================================
    ww_pm1_h = WiserOpticalElement(name='pm1h',
                                   boundary_shape=None,
                                   native_CoreOptics=Optics.MirrorPlane(L=L, AngleGrazing=AngleGrazing),
                                   native_PositioningDirectives=Foundation.PositioningDirectives(
                                       ReferTo='upstream',
                                       PlaceWhat='centre',
                                       PlaceWhere='centre',
                                       Distance=20.)
                                   )

    pm1_h = ww_pm1_h.native_optical_element # Wiser optical element
    pm1_h.ComputationSettings.UseFigureError = False
    pm1_h.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    pm1_h.ComputationSettings.Ignore = False          # Lo user decide di non simulare lo specchio ()
    pm1_h.ComputationSettings.UseCustomSampling = UseCustomSampling # l'utente decide di impostare a mano il campionamento
    pm1_h.ComputationSettings.NSamples = N

    # PM2 (h)
    # ==========================================================================
    ww_pm2_h = WiserOpticalElement(name='pm2h',
                                   boundary_shape=None,
                                   native_CoreOptics=Optics.MirrorPlane(L=L, AngleGrazing=AngleGrazing),
                                   native_PositioningDirectives=Foundation.PositioningDirectives(
                                       ReferTo='upstream',
                                       PlaceWhat='centre',
                                       PlaceWhere='centre',
                                       Distance=20.)
                                   )

    pm2_h = ww_pm2_h.native_optical_element # Wiser optical element
    pm2_h.ComputationSettings.UseFigureError = False
    pm2_h.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    pm2_h.ComputationSettings.Ignore = False  # Lo user decide di non simulare lo specchio ()
    pm2_h.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    pm2_h.ComputationSettings.NSamples = N

    # KB(v)
    # ==========================================================================
    ww_kb_v = WiserOpticalElement(name='kb_v',
                                  boundary_shape=None,
                                  native_CoreOptics=Optics.MirrorElliptic(f1=f1_v, f2=f2_v, L=L, Alpha=AngleGrazing),
                                  native_PositioningDirectives=Foundation.PositioningDirectives(
                                      ReferTo='source',
                                      PlaceWhat='upstream focus',
                                      PlaceWhere='centre')
                                  )

    kb_v = ww_kb_v.native_optical_element
    kb_v.CoreOptics.ComputationSettings.UseFigureError = False
    kb_v.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.VERTICAL
    kb_v.CoreOptics.ComputationSettings.UseRoughness = False
    kb_v.CoreOptics.ComputationSettings.UseSmallDisplacements = False  # serve per traslare/ruotare l'EO

    kb_v.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    kb_v.ComputationSettings.NSamples = N
    # kb_v.CoreOptics.FigureErrorLoad(File='DATA/LTP/kbh.txt', Step=2e-3, AmplitudeScaling=-1e-3)

    # KB(h)
    # ==========================================================================
    ww_kb_h = WiserOpticalElement(name='kb_h',
                                  boundary_shape=None,
                                  native_CoreOptics=Optics.MirrorElliptic(f1=f1_h, f2=f2_h, L=L, Alpha=AngleGrazing),
                                  native_PositioningDirectives=Foundation.PositioningDirectives(
                                      ReferTo='source',
                                      PlaceWhat='upstream focus',
                                      PlaceWhere='centre')
                                  )

    kb_h = ww_kb_h.native_optical_element
    kb_h.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL
    kb_h.CoreOptics.ComputationSettings.UseRoughness = False
    kb_h.CoreOptics.ComputationSettings.UseSmallDisplacements = False  # serve per traslare/ruotare l'EO
    kb_h.ComputationSettings.UseCustomSampling = UseCustomSampling  # l'utente decide di impostare a mano il campionamento
    kb_h.ComputationSettings.NSamples = N

    kb_h.CoreOptics.ComputationSettings.UseFigureError = True
    kb_h.CoreOptics.FigureErrorLoad(File='kbh.txt', Step=2e-3, AmplitudeScaling=-1e-3)

    ww_sl = WiserOpticalElement(name='sl',
                                boundary_shape=None,
                                native_CoreOptics=Optics.Slits(L=1e-3),
                                native_PositioningDirectives=Foundation.PositioningDirectives(
                                    ReferTo='source',
                                    PlaceWhat='centre',
                                    PlaceWhere='centre',
                                    Distance=f2_v + f1_v - 0.5),
                                )

    ww_sl.native_optical_element.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.VERTICAL
    ww_sl.native_optical_element.CoreOptics.UseAsReference = False

    # detector (v)
    # ==========================================================================
    ww_d_v = WiserOpticalElement(name='detector_v',
                                 boundary_shape=None,
                                 native_CoreOptics=Optics.Detector(L=DetectorSize, AngleGrazing=deg2rad(90)),
                                 native_PositioningDirectives=Foundation.PositioningDirectives(
                                     ReferTo='upstream',
                                     PlaceWhat='centre',
                                     PlaceWhere='downstream focus')
                                 )

    d_v = ww_d_v.native_optical_element
    d_v.ComputationSettings.UseCustomSampling = UseCustomSampling
    d_v.ComputationSettings.NSamples = N                          # come sopra. In teoria il campionamento può essere specificato elemento per elmeento
    d_v.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.VERTICAL

    # detector (h)
    # ==========================================================================
    ww_d_h = WiserOpticalElement(name='detector_h',
                                 boundary_shape=None,
                                 native_CoreOptics=Optics.Detector(L=DetectorSize, AngleGrazing=deg2rad(90)),
                                 native_PositioningDirectives=Foundation.PositioningDirectives(
                                     ReferTo='upstream',
                                     PlaceWhat='centre',
                                     PlaceWhere='downstream focus')
                                 )

    d_h = ww_d_h.native_optical_element
    d_h.ComputationSettings.UseCustomSampling = UseCustomSampling
    d_h.ComputationSettings.NSamples = N                          # come sopra. In teoria il campionamento può essere specificato elemento per elmeento
    d_h.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL

    beamline = WiserPropagationElements()
    beamline.get_wise_propagation_elements().ComputationSettings.OrientationToCompute = [Optics.OPTICS_ORIENTATION.HORIZONTAL, Optics.OPTICS_ORIENTATION.VERTICAL]

    wavefront = WiseWavefront(wise_computation_results=None)

    # Build the beamline
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_s))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_pm1_h))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_kb_v))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_kb_h))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_sl))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_d_v))
    beamline.add_beamline_element(WiserBeamlineElement(optical_element=ww_d_h))

    parameters = PropagationParameters(wavefront=WiseWavefront(wise_computation_results=None), propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", False)
    parameters.set_additional_parameters("NPools", 1)
    #
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters, handler_name=WiserPropagator.HANDLER_NAME)
    #
    beamline_before = beamline
    # # Plot the result

    plot(d_v)

    plot(d_h)
    #
    # # Insert an element
    beamline.insert_beamline_element(index=1, new_element=WiserBeamlineElement(optical_element=ww_pm2_h))

    parameters = PropagationParameters(wavefront=WiseWavefront(wise_computation_results=None),
                                       propagation_elements=beamline)
    parameters.set_additional_parameters("single_propagation", False)
    parameters.set_additional_parameters("NPools", 1)
    #
    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters,
                                                             handler_name=WiserPropagator.HANDLER_NAME)

    print('Original beamline')
    # print(beamline.get_wise_propagation_elements())
    print(beamline_before.get_wise_propagation_elements())

    plot(d_v)
    plot(d_h)

    print('Beamline with inserted element')
    print(beamline.get_wise_propagation_elements())



    plt.show()
