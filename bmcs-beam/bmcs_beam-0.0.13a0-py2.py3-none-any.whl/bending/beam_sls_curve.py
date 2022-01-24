
import bmcs_utils.api as bu
from .deflection_profile import DeflectionProfile
import os.path

class BeamSLSCurve(bu.ParametricStudy):
    '''
    - link to data cache identifying the directory where to store the
    interim results

    - dictionary based storage of the individual runs of the study
      which makes it introspectable.

    -
    '''

    rc_beam = bu.Instance(DeflectionProfile)

    tree = ['rc_beam']

    def save(self):
        open( bu.data_cache.dir )

