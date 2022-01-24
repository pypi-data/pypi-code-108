'''
Created on Jun 23, 2010

@author: alexander
'''

from traits.api import \
    Float, Instance, Array, Property, cached_property, \
    Int

from traitsui.api import \
    View, Item, Group, \
    InstanceEditor, VGroup

import numpy as np

from scipy.optimize import fsolve

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

from bmcs_beam.mxn.reinf_laws import \
    ReinfLawBase

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

from .matresdev.db.simdb import SimDB
simdb = SimDB()

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

class ECBCalib(MxNTreeNode):

    # rupture moment and normal force measured in the calibration experiment
    # (three point bending test)
    #
    Mu = Float(3.5, calib_input=True)  # [kNm]
    Nu = Float(0.0, calib_input=True)  # [kN]

    #===========================================================================
    # Cross Section Specification (Geometry and Layout)
    #===========================================================================

    cs = Instance(CrossSection)
    def _cs_default(self):
        return CrossSection(reinf=[RLCTexUniform(n_layers=12, material='default_fabric')],
                               matrix_cs=MatrixCrossSection(geo=MCSGeoRect(width=0.2,
                                        height=0.06), n_cj=20, material='default_mixture',
                                                            material_law='constant'))

    u0 = Property(Array(float), depends_on='cs.changed')
    '''Construct the initial vector.
    '''
    @cached_property
    def _get_u0(self):
        u0 = self.cs.reinf_components_with_state[0].material_law_.u0

        eps_up = -self.cs.matrix_cs.material_law_.eps_c_u
        eps_lo = self.cs.reinf_components_with_state[0].convert_eps_u_2_lo(eps_up=eps_up)

        print('eps_up', eps_up)
        print('eps_lo', eps_lo)

        return np.array([eps_lo, u0[1] ], dtype='float')

    # iteration counter
    #
    n = Int(0)
    def get_lack_of_fit(self, u):
        '''Return the difference between 'N_external' and 'N_internal' as well as 'M_external' and 'M_internal'
        N_c (=compressive force of the compressive zone of the concrete)
        N_t (=total tensile force of the reinforcement layers)
        '''

        print('--------------------iteration', self.n, '------------------------')
        self.n += 1
        # set iteration counter
        #
        eps_up = -self.cs.matrix_cs.material_.eps_c_u
        eps_lo = u[0]

        self.cs.set(eps_lo=eps_lo, eps_up=eps_up)

        eps_tex_u = self.cs.reinf_components_with_state[0].converted_eps_lo_2_u
        self.cs.reinf_components_with_state[0].material_law_.set_cparams(eps_tex_u, u[1])

        N_internal = self.cs.N
        M_internal = self.cs.M

        d_N = N_internal - self.Nu
        d_M = M_internal - self.Mu

        return np.array([ d_N, d_M ], dtype=float)

    u_sol = Property(Array(Float), depends_on='cs.changed,+calib_input')
    '''Solution vector returned by 'fit_response'.'''
    @cached_property
    def _get_u_sol(self):
        '''iterate 'eps_t' such that the lack of fit between the calculated
        normal forces in the tensile reinforcement and the compressive zone (concrete)
        is smaller then 'xtol' defined in function 'brentq'.
        NOTE: the method 'get_lack_of_fit' returns the relative error.
        '''

        # use scipy-functionality to get the iterated value of 'eps_t'
        # NOTE: get_lack_of_fit must have a sign change as a requirement
        # for the function call 'brentq' to work property.

        # The method brentq has optional arguments such as
        #   'xtol'    - absolut error (default value = 1.0e-12)
        #   'rtol'    - relative error (not supported at the time)
        #   'maxiter' - maximum numbers of iterations used
        #
        return fsolve(self.get_lack_of_fit, self.u0, xtol=1.0e-5)

    calibrated_ecb_law = Property(Instance(ReinfLawBase), depends_on='cs.changed,+calib_input')
    '''Calibrated ecbl_mfn
    '''
    @cached_property
    def _get_calibrated_ecb_law(self):
        print('NEW CALIBRATION')
        self.cs.eps_lo = self.u_sol[0]
        eps_tex_u = self.cs.reinf_components_with_state[0].converted_eps_lo_2_u
        self.cs.reinf_components_with_state[0].material_law_.set_cparams(eps_tex_u, self.u_sol[1])
        self.n = 0
        self.cs.reinf_components_with_state[0].material_.save()
        return self.cs.reinf_components_with_state[0].material_law_

    ecb_law = Property(Instance(ReinfLawBase))
    '''Not calibrated law
    '''
    def _get_ecb_law(self):
        return self.cs.reinf_components_with_state[0].material_law_

    #===========================================================================
    # Visualisation related attributes
    #===========================================================================

    def plot(self, fig):
        self.calibrated_ecb_law.plot(fig)

    node_name = 'ECB law calibration'

    tree_node_list = Property
    @cached_property
    def _get_tree_node_list(self):
        return [self.cs]

    traits_view = View(
                Item('Mu'),
                Item('Nu'),
                buttons=['OK', 'Cancel'],
                )

    tree_view = View(VGroup(
                Group(
                Item('Mu'),
                Item('Nu'),
                ),
                Group(
                Item('ecb_law',
                     editor=InstanceEditor(editable=True),
                     style='custom',
                     show_label=False),
                label='Effective crack bridge law'
                ),
                ),
                buttons=['OK', 'Cancel'],
                )

if __name__ == '__main__':

    #------------------------------------------------
    # 1) CALIBRATION:
    # get 'eps_t' and the parameter of the effective
    # crack bridge function 'var_a' for a given 'eps_c_u'
    #------------------------------------------------
    #

    print('\n')
    print('setup ECBLCalib')
    print('\n')

    ec = ECBCalib(Mu=3.49)

