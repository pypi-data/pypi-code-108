# -*- coding: utf-8 -*-
"""
Test script - build a dpi horizontal beamline.
"""
from wofry.propagator.propagator import PropagationParameters, PropagationManager

from wofrywiser.beamline.beamline_elements import WiserBeamlineElement, WiserOpticalElement
from wofrywiser.propagator.wavefront1D.wise_wavefront import WiseWavefront
from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagator, WiserPropagationElements

from LibWiser.WiserImport import *
import LibWiser.FermiSource as FermiSource

Distances = FermiSource.DistancesF2
PathMetrologyFermi = Paths.MetrologyFermi

UseGrating = False
Set = 0
Lambda = 2e-9
Waist0 = 180e-6

def plot(oe):
    ToolLib.CommonPlots.IntensityAtOpticalElement(oe)

if Set ==0:
	Angle_pm2a_deg = 2.5
	Angle_presto_deg = 2.5
	Angle_kb_deg = 2.0

elif Set  == 1:
	Angle_pm2a_deg = 2.0
	Angle_presto_deg = 2.0
	Angle_kb_deg = 2.0

elif Set  == 2:
	Angle_pm2a_deg = 2.0
	Angle_presto_deg = 2.0
	Angle_kb_deg = 2.

elif Set == 3:
	Angle_pm2a_deg = 2.5
	Angle_presto_deg = 2.5
	Angle_kb_deg = 2.0

a = np.array([0])
tl.Debug.On = True

DetectorSize = 100e-6


print(__name__)
if __name__ == '__main__':

    PropagationManager.Instance().add_propagator(WiserPropagator())

    # SOURCE (H, V)
    # -----------------------------------------------------------------------------
    DeltaSource = 0
    ww_s = WiserOpticalElement(name='FEL2',
                               boundary_shape=None,
                               isSource=True,
                               native_CoreOptics=Optics.SourceGaussian(
                                   Lambda=Lambda,
                                   Waist0=Waist0,
                                   Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL),
                               native_PositioningDirectives=Foundation.PositioningDirectives(
                                   ReferTo='absolute',
                                   XYCentre=[0,0],
                                   Angle=0.)
                               )

    s = ww_s.native_optical_element # Wiser optical element


    # PM2A (H)
    # -----------------------------------------------------------------------------

    ww_pm2a = WiserOpticalElement(name='PM2a',
                                  boundary_shape=None,
                                  native_CoreOptics=Optics.MirrorPlane(
                                      L=0.4,
                                      AngleGrazing=np.deg2rad(Angle_pm2a_deg),
                                      Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL),
                                  native_PositioningDirectives=Foundation.PositioningDirectives(
                                      ReferTo='source',
                                      PlaceWhat='centre',
                                      PlaceWhere='centre',
                                      Distance=41.4427)
                                  )

    pm2a = ww_pm2a.native_optical_element

    # Presto (H)
    # -----------------------------------------------------------------------------

    ww_presto = WiserOpticalElement(name='presto',
                                    boundary_shape=None,
                                    native_CoreOptics=Optics.MirrorPlane(
                                        L=0.4,
                                        AngleGrazing=np.deg2rad(Angle_presto_deg),
                                        Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL),
                                    native_PositioningDirectives=Foundation.PositioningDirectives(
                                        ReferTo='source',
                                        PlaceWhat='centre',
                                        PlaceWhere='centre',
                                        Distance=49.8466)
                                    )

    presto = ww_presto.native_optical_element

    # dpi kb (H)
    # -----------------------------------------------------------------------------

    ww_dpi_kbh = WiserOpticalElement(name='kb',
                                     boundary_shape=None,
                                     native_CoreOptics=Optics.MirrorElliptic(
                                         L=0.4,
                                         f1=91.55,
                                         f2=1.2,
                                         Alpha=np.deg2rad(Angle_kb_deg),
                                         Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL),
                                     native_PositioningDirectives=Foundation.PositioningDirectives(
                                         ReferTo='source',
                                         PlaceWhat='centre',
                                         PlaceWhere='centre',
                                         Distance=91.55)
                                     )

    dpi_kbh = ww_dpi_kbh.native_optical_element

    # Detector (H)
    # -----------------------------------------------------------------------------

    ww_d_h = WiserOpticalElement(name='d_h',
                                 boundary_shape=None,
                                 native_CoreOptics=Optics.Detector(
                                     L=DetectorSize,
                                     AngleGrazing=np.deg2rad(90),
                                     Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL),
                                 native_PositioningDirectives=Foundation.PositioningDirectives(
                                     ReferTo='upstream',
                                     PlaceWhat='centre',
                                     PlaceWhere='centre',
                                     Distance=1.2)
                                 )

    d_h = ww_d_h.native_optical_element

    # Create beamline
    # -----------------------------------------------------------------------------

    th = WiserPropagationElements()
    th.get_wise_propagation_elements().ComputationSettings.OrientationToCompute = [Optics.OPTICS_ORIENTATION.HORIZONTAL]
    th.add_beamline_element(WiserBeamlineElement(optical_element=ww_s))
    th.add_beamline_element(WiserBeamlineElement(optical_element=ww_pm2a))
    th.add_beamline_element(WiserBeamlineElement(optical_element=ww_presto))
    th.add_beamline_element(WiserBeamlineElement(optical_element=ww_dpi_kbh))
    th.add_beamline_element(WiserBeamlineElement(optical_element=ww_d_h))

    th.refresh_wise_positions()
    print(th.get_wise_propagation_elements())

    # Computation settings
    # -----------------------------------------------------------------------------
    NSampling = int(5e3)

    pm2a.ComputationSettings.UseCustomSampling = True
    pm2a.ComputationSettings.NSamples = NSampling

    presto.ComputationSettings.UseCustomSampling = True
    presto.ComputationSettings.NSamples = NSampling

    dpi_kbh.ComputationSettings.UseCustomSampling = True
    dpi_kbh.ComputationSettings.NSamples = NSampling

    d_h.ComputationSettings.UseCustomSampling = True
    d_h.ComputationSettings.NSamples = NSampling

    # Surface settings
    # -----------------------------------------------------------------------------
    # pm2a
    x, y, FileInfo = tl.Metrology.ReadLtp2File(PathMetrologyFermi / "PM2A" / "PM2A_I06.SLP")  # read slopes
    h = tl.Metrology.SlopeIntegrate(y, dx=FileInfo.XStep)  # integrate slopes
    pm2a.CoreOptics.FigureErrorLoad(h,
                                    Step=FileInfo.XStep,
                                    AmplitudeScaling=1,  # => m  UNDERSTAND IF -1 or +1
                                    Append=False)
    pm2a.CoreOptics.ComputationSettings.UseFigureError = True

    # presto
    h = tl.FileIO.ReadYFile(PathMetrologyFermi / "HE_WISE_FigureError.txt", SkipLines=1)
    h = h*1e-3 # mm => m
    if UseGrating:
        hGrating, GratingStep = tl.Metrology.RectangularGrating(
            L0=250e-3,
            L1=60e-3,
            N=3e5,
            LinesPerMillimiter=3750,
            GrooveHeight=9.5e-9,
            HighDuty=0.65,
            ReturnStep=True)
        NGrating = len(hGrating)
        hNew = rm.FastResample1d(h, NGrating) # FigureError and Grating profiles have equal sampling

        hTot = hNew + hGrating
        XStep = GratingStep

    else:
        hTot = h
        XStep = 1e-3

    presto.CoreOptics.FigureErrorLoad(hTot, Step=XStep, AmplitudeScaling=1, Append=False)

    # kbh
    dpi_kbh.CoreOptics.ComputationSettings.UseFigureError = True      # use figure error?
    dpi_kbh.CoreOptics.FigureErrorLoad(
        File=PathMetrologyFermi / "dpi_kbh.txt",
        Step=2e-3, # passo del file
        AmplitudeScaling=-1 * 1e-3,  # fattore di scala
        Append=False
    )

    # Ignore settings
    # -----------------------------------------------------------------------------
    # Ignore List
    pm2a.ComputationSettings.Ignore = False
    presto.ComputationSettings.Ignore = False
    dpi_kbh.ComputationSettings.Ignore = False
    d_h.ComputationSettings.Ignore = False

    UseFigureError = True
    pm2a.CoreOptics.ComputationSettings.UseFigureError = UseFigureError
    presto.CoreOptics.ComputationSettings.UseFigureError = UseFigureError
    dpi_kbh.CoreOptics.ComputationSettings.UseFigureError = UseFigureError

    # Initialize computation parameters
    # -----------------------------------------------------------------------------

    wavefront = WiseWavefront(wise_computation_results=None)
    parameters = PropagationParameters(wavefront=WiseWavefront(wise_computation_results=None), propagation_elements=th)
    parameters.set_additional_parameters("single_propagation", False)
    parameters.set_additional_parameters("NPools", 1)

    wavefront = PropagationManager.Instance().do_propagation(propagation_parameters=parameters,
                                                             handler_name=WiserPropagator.HANDLER_NAME)
    # Plot results
    # -----------------------------------------------------------------------------

    plot(d_h)
    plt.show()
