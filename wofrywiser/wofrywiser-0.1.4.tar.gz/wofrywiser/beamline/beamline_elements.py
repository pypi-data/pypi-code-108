from syned.beamline.optical_element import OpticalElement as SynedOpticalElement
from syned.beamline.beamline_element import BeamlineElement

from LibWiser.Foundation import OpticalElement, PositioningDirectives

class WiserOpticalElement(SynedOpticalElement):
    '''
    WiserOpticalElement acts as a generic adapter/wrapper for any optical element defined in LibWiser:
    - SourceGaussian
    - SourcePoint
    - MirrorPlane
    - MirrorElliptic
    - MirrorSpheric
    - Slits
    - Detector

    native_CoreOptics -> native_optical_element: LibWiser.Optics.<optical element>
    native_PositioningDirectives: LibWiser.Foundation.PositioningDirectives
    isSource: Flag if <optical element> is source
    native_OpticalElement: If you want to pass a ready made optical element, then leave the rest None and only pass this
    '''
    def __init__(self,
                 name="Undefined", boundary_shape=None, # Syned object
                 native_CoreOptics=None, # A LibWiser.Optics.Optics object
                 native_PositioningDirectives=PositioningDirectives(), # LibWiser Foundation PositioningDirectives
                 isSource=False,
                 native_OpticalElement=None
                 ):

        '''
        Parameters
        ---------------------
        name : str
            name of Wiser optical element
        boundary_shape: do not know
            No idea what this is...
        native_CoreOptics: LibWiser.Optics.<optical element>
            One of Wiser optical elements
        native_PositioningDirectives: LibWiser.Foundation.PositioningDirectives
            Wiser PositioningDirectives
        isSource: bool
            Source flat
        native_OpticalElement: LibWiser.Foundation.OpticalElement
            Pass the whole optical element, leave native_CoreOptics=None and native_PositioningDirectives=None
        '''

        # Init SynedOpticalElement
        # Fills: name, boundary_shape, as required by Syned
        super(WiserOpticalElement, self).__init__(name=name, boundary_shape=boundary_shape)

        if native_CoreOptics is not None:
            # Build the native Wiser OpticalElement
            # fills native_optical_element
            self.native_optical_element = OpticalElement(CoreOpticsElement=native_CoreOptics,
                                                         PositioningDirectives=native_PositioningDirectives,
                                                         Name=name,
                                                         # syned name and Wiser name will never be automatically synced...
                                                         IsSource=isSource)  # In case of source, to be discussed
        elif native_OpticalElement is not None:
            # In case the whole optical element is passed as an argument
            self.native_optical_element = native_OpticalElement
        else:
            print('Native OpticalElement not specified!')


class WiserBeamlineElement(BeamlineElement):
    '''
    Glue for beamline element. Nothing particular here.
    '''
    def __init__(self, optical_element=WiserOpticalElement()):
        super(WiserBeamlineElement, self).__init__(optical_element=optical_element, coordinates=None)

    def get_coordinates(self):
        raise NotImplementedError("this method cannot be used in WISE 2")