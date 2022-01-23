######################################################
class input_profiles_adaptor(OMFITinterfaceAdaptor):
    type = 'input_profiles'

    @staticmethod
    def identify(data):
        import numpy as np
        import numpy
        printd('Attempting to identify {:} type...'.format('input_profiles'))
        if isinstance(data, dict) and np.all([k in data for k in ['Ti_1', 'ni_1']]):
            printd(' > Looks like it is {:} type!'.format('input_profiles'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('input_profiles'))

    def definitions(self, key, data):
        if self.register(key, 'time', 'Time', 's', ''):
            return 0

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            return data['rho']

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'r'):
            return data['polflux']

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'r'):
            return (self['psi'] - min(self['psi'])) / (max(self['psi']) - min(self['psi']))

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'r'):
            return data['ptot']

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'r'):
            return data['ne'] * 1E19

        # -------------------------
        # Other plasma parameters
        # -------------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'r'):
            return data['z_eff']


######################################################
class ONETWO_statefile_adaptor(OMFITinterfaceAdaptor):
    type = 'ONETWO_statefile'

    @staticmethod
    def identify(data):
        from omfit_classes.omfit_base import OMFITcollection
        printd('Attempting to identify {:} type...'.format('ONETWO_statefile'))
        if isinstance(data, dict) and not isinstance(data, OMFITcollection) and np.all([k in data for k in ['press', 'rho_grid']]):
            printd(' > Looks like it is {:} type!'.format('ONETWO_statefile'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('ONETWO_statefile'))

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('ONETWO_statefile definitions...')

        def interp_npsi_vars_to_rho(val):
            rho = data['rho_grid']['data']
            rho_mhd = np.flipud(data['rho_mhd_gridnpsi']['data'])
            val = np.flipud(val)
            return interp1e(rho_mhd, val, kind='linear')(rho)

        if self.register(key, 'time', 'Time', 's', ''):
            return data['time']['data']

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            return np.linspace(0, 1, len(data['rho_grid']['data']))

        if self.register(key, 'rho_m', 'Minor radius', 'm', 'r'):
            return data['rho_grid']['data']

        if self.register(key, 'a', 'Plasma midplane minor radius', 'm', ''):
            return interp_npsi_vars_to_rho(data['rminavnpsi']['data'])[-1]

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'r'):
            return data['psir_grid']['data']

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'r'):
            return (self['psi'] - min(self['psi'])) / (max(self['psi']) - min(self['psi']))

        if self.register(key, 'r_min', 'Geometric midplane minor radius', 'm', 'r'):
            return interp_npsi_vars_to_rho(data['rminavnpsi']['data'])

        if self.register(key, ['r_geo', 'r_maj'], 'Geometric midplane major radius', 'm', 'r'):
            return interp_npsi_vars_to_rho(data['rmajavnpsi']['data'])

        if self.register(key, ['rout', 'r_out'], 'Geometric midplane outer major radius', 'm', 'r'):
            return interp_npsi_vars_to_rho(data['rmajavnpsi']['data'] + data['rminavnpsi']['data'])

        if self.register(key, ['R0', 'vacuum major radius'], 'Major radius of vacuum BT0 reference == R0', 'm', ''):
            return data['rmajor']['data']

        if self.register(key, '1/R', '<1/R>', '1/m', 'r'):
            return interp_npsi_vars_to_rho(data['ravginpsi']['data'])

        if self.register(key, 'kappa', 'Elongation', '1', 'r'):
            return interp_npsi_vars_to_rho(data['elongxnpsi']['data'])

        if self.register(key, 'delta', 'Triangularity', '1', 'r'):
            return interp_npsi_vars_to_rho(0.5 * data['triangnpsi_l']['data'] + 0.5 * data['triangnpsi_u']['data'])

        if self.register(key, ['Acx', 'plasma cross section'], 'Total plasma cross section', 'm^2', ''):
            return data['areao']['data']

        if self.register(key, 'area', 'Cross sectional area enclosed by each flux surface', 'm^2', 'r'):
            return data['sfareanrho']['data']

        if self.register(key, 'darea', 'Gradient of cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return gradient(self['area'])

        if self.register(key, ['vol', 'V', 'volume'], 'Volume', 'm^3', 'r'):
            integrand = 4 * np.pi ** 2 * self['R0'] * self['rho_m'] * data['hcap']['data']
            return scipy.integrate.cumtrapz(integrand, self['rho_m'], initial=0)

        if self.register(key, ['dvol', 'dV/drho', 'differential volume'], 'Differential volume', 'm^3', 'r'):
            return deriv(self['rho'], self['volume'])

        if self.register(key, 'pprime', 'dp/dpsi', 'N/m^2', 'r'):
            return deriv(self['psi'], self['pressure'])

        # -------------------------
        # Fields
        # -------------------------
        if self.register(key, ['BT0', 'vacuum toroidal field'], 'Vacuum BT0 at R0', 'T', ''):
            return data['btor']['data']

        if self.register(key, ['Btot_out', 'total B field out', 'B magnitude out', 'btot_out'], 'B field magnitude at outboard midplane', 'T', 'r'):
            return data['btotrmaj']['data']

        if self.register(key, ['f', 'fpol', 'FPOL', 'I_psi'], 'Bz * R (including dia/paramagnetism)', 'm*T', 'r'):  # f of psi = R * Bt
            return data['fpsinrho']['data']

        if self.register(key, 'ffprime', 'f*df/dpsi', '(m*T)^2/(V*s/rad)', 'r'):
            return data['ffprim']['data']

        if self.register(key, ['Bp_avg', 'Bp_fsa', 'BPOL_AVG', 'Bpol_fsa'], 'Flux surface average of poloidal B field', 'T', 'r'):
            return data['bp']['data']

        ##        if self.register(key,['Btot_avg','total B field avg','B magnitude avg','btot_avg','btot_fsa'],'B field magnitude, flux surface average, tesla','T','r'):
        ##            bp_fsa=self['Bp_avg']
        ##            bt_fsa=
        ##            btotavg=np.sqrt(bp_fsa**2+bt_fsa**2)
        ##            return btotavg

        # -------------------------
        # Current
        # -------------------------
        if self.register(key, ['Ip', 'total current'], 'Total plasma current ', 'A', ''):
            return data['tot_cur']['data']

        if self.register(key, ['jtot', 'current'], 'Current density <Jtor R0/R>', 'A/m^2', 'r'):
            return data['curden']['data']

        if self.register(key, ['jpar', 'j//', 'parallel current'], 'Parallel current density <J.B/Bt0>', 'A/m^2', 'r'):
            return data['curpar']['data']

        if self.register(key, ['joh', 'johm', 'ohmic current'], 'Ohmic current density <Jtor R0/R>', 'A/m^2', 'r'):
            return data['curohm']['data']

        if self.register(key, ['jboot', 'bootstrap current'], 'Bootstrap current density <Jtor R0/R>', 'A/m^2', 'r'):
            return data['curboot']['data']

        if self.register(key, ['jb', 'beam current'], 'Beam current density <Jtor R0/R>', 'A/m^2', 'r'):
            return data['curbeam']['data']

        if self.register(key, ['jrf', 'rf current'], 'RF current density <Jtor R0/R>', 'A/m^2', 'r'):
            return data['currf']['data']

        if self.register(key, ['q_abs', 'safety factor magnitude'], 'Safety factor magnitude', '', 'r'):
            return data['q_value']['data']

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['betat'], 'Toroidal beta', '', ''):
            return data['beta']['data']

        if self.register(key, ['betap'], 'Poloidal beta', '', ''):
            return data['betap']['data']

        if self.register(key, ['betan'], 'Normalized beta', '', ''):
            bt = self['BT0'] * self['R0'] / self['r_geo'][-1]
            return abs(self['betat'] / (self['Ip'] / 1E6 / self['a'] / bt))

        if self.register(key, ['Wtot', 'energy'], 'Total energy', 'J/m^3', 'r'):
            return self['pressure'] * 3 / 2.

        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'r'):
            return data['press']['data']

        if self.register(key, ['Wbeam', 'beam energy'], 'Beam energy density', 'J/m^3', 'r'):
            return data['wbeam']['data'] * 1.60218e-16  # Conversion from keV/m^3 to J/m^3=N/m^2

        if self.register(key, ['pbeam', 'beam pressure'], 'Beam pressure', 'N/m^2', 'r'):
            return self['beam energy'] * 2 / 3.

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'r'):
            return data['Te']['data']

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'r'):
            return data['ene']['data']

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'ir'):
            return np.array([data['Ti']['data']] * len(self['ion species']))

        if self.register(key, 'ion species', 'Ion species', '1', 'i'):
            return data['enion']['long_name'].split(':')[1].strip().split()  # both primary and impurity ions

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'ir'):
            return data['enion']['data']  # includes both primary and impurity ions

        if self.register(key, 'beam species', 'Beam ion species', '1', 'b'):
            return data['enbeam']['long_name'].split(':')[1].strip().split()

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'br'):
            return data['enbeam']['data']  # includes all beam species

        # -------------------------
        # Other plasma parameters
        # -------------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'r'):
            return data['zeff']['data']

        if self.register(key, ['Z', 'Zi', 'charge state'], 'Ion charge state', 'amu', 'i'):
            result = data['z']['data'][:, 0]
            printd('  >> zi: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['ftrap', 'trapfrac', 'trapped fraction', 'ncft'], 'Trapped particle fraction', '', 'r'):
            result = data['ftrap']['data']
            printd('  >> ftrap: np.shape(result) = ', np.shape(result))
            return result


######################################################
class ONETWO_MDS_adaptor(OMFITinterfaceAdaptor):
    type = 'ONETWO_MDS'

    @staticmethod
    def identify(data):
        printd('Attempting to identify {:} type...'.format('ONETWO_MDS'))
        if 'EQU' in data and data['EQU']['ANGROT'].data() is not None:
            printd(' > Looks like it is {:} type!'.format('ONETWO_MDS'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('ONETWO_MDS'))

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('ONETWO_MDS definitions...')
        if self.register(key, 'device', 'Device', '1', ''):
            return 'D3D'

        if self.register(key, 'shot', 'Shot', '1', ''):
            return int(data['SHOT'].data())

        if self.register(key, 'time', 'Time', 's', 't'):
            return data['GOOD_TIMES'].data()

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, 'a', 'Plasma midplane minor radius', 'm', 't'):
            if 'RMIN_MILLER' in data['EQU']:
                return data['EQU']['RMIN_MILLER'].data()[-1, :]
            else:
                return data['EQU']['RMINOR'].data()[-1, :]

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'rt'):
            return data['EQU']['POL_FLUX'].data()

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'rt'):
            return (self['psi'] - np.min(self['psi'], axis=0)[np.newaxis, :]) / (np.max(self['psi'], axis=0)[np.newaxis, :] - np.min(self['psi'], axis=0)[np.newaxis, :])

        if self.register(key, 'r_min', 'Geometric midplane minor radius', 'm', 'rt'):
            return self['a']

        if self.register(key, ['r_geo', 'r_maj'], 'Geometric midplane major radius', 'm', 'rt'):
            return data['EQU']['RMAJOR'].data()

        if self.register(key, ['rout', 'r_out'], 'Geometric midplane outer major radius', 'm', 'rt'):
            return data['EQU']['RMAJOR'].data() + self['a']

        if self.register(key, ['R0', 'vacuum major radius'], 'Major radius of vacuum BT0 reference == R0', 'm', ''):
            specs = omfit_classes.utils_fusion.device_specs(tolist(self['device'])[0])
            if 'R0' in list(specs.keys()) and specs['R0'] is not None:
                return specs['R0']
            else:
                raise Exception('Plasma vacuum major radius is not defined for ' + str(self['device']))

        if self.register(key, ['BT0', 'vacuum toroidal field'], 'Vacuum BT0 at R0', 'T', 't'):
            return data['EQU']['BTOR'].data()

        if self.register(key, 'rho_m', 'Minor radius', 'm', 'rt'):
            return data['EQU']['RHOM'].data()  # same as data['EQU']['RMINOR'].data()

        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            return data['EQU']['RHO'].data()

        # if self.register(key,'1/R','1/R','1/m','rt'):
        #    return ???

        if self.register(key, 'kappa', 'Elongation', '1', 'rt'):
            return data['EQU']['KAPPAR'].data()

        if self.register(key, 'delta', 'Triangularity', '1', 'rt'):
            if 'DELTAR_L' in data['EQU'] and 'DELTAR_U' in data['EQU']:
                return 0.5 * data['EQU']['DELTAR_L'].data() + 0.5 * data['EQU']['DELTAR_U'].data()
            else:
                return data['EQU']['DELTAR'].data()

        if self.register(key, ['Acx', 'plasma cross section'], 'Total plasma cross section', 'm^2', 't'):
            return np.squeeze(data['EQU']['SURF_AREA'].data()[-1, :])

        if self.register(key, ['vol', 'V', 'volume'], 'Volume', 'm^3', 'rt'):
            return data['EQU']['VOL'].data()

        if self.register(key, ['dvol', 'dV/drho', 'differential volume'], 'Differential volume', 'm^3', 'rt'):
            return gradient(self['volume'])[0] / gradient(self.get('rho', 'rt'))[:, np.newaxis]

        if self.register(key, 'pprime', 'dp/dpsi', 'N/m^2', 'rt'):
            return gradient(self['pressure'])[0] / gradient(self['psi'])[0]

        # if self.register(key,'ffprime','f*df/dpsi','(m*T)^2/(V*s/rad)','r'):
        #     return ???

        # -------------------------
        # Current
        # -------------------------
        if self.register(key, ['Ip', 'total current'], 'Total plasma current ', 'A', 't'):
            return data['EQU']['IP'].data()

        if self.register(key, ['q_abs', 'safety factor magnitude'], 'Safety factor magnitude', '', 'rt'):
            return abs(data['EQU']['Q'].data())

        if self.register(key, ['jtot', 'current'], 'Current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return data['EQU']['J_EQUIL'].data()

        # if self.register(key,['jpar','j//','parallel current'],'Parallel current density <J.B/Bt0>','A/m^2','r'):
        #    return ???

        if self.register(key, ['joh', 'johm', 'ohmic current'], 'Ohmic current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return data['EQU']['J_OHM'].data()

        if self.register(key, ['jboot', 'bootstrap current'], 'Bootstrap current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return data['HCD']['J_NI'].data() - data['HCD']['J_CD'].data()

        if self.register(key, ['jb', 'beam current'], 'Beam current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return data['NBI']['J_NBCD'].data()

        if self.register(key, ['jrf', 'rf current'], 'RF current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return data['HCD']['J_CD'].data() - data['NBI']['J_NBCD'].data()

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['betat'], 'Toroidal beta', '', 't'):
            return data['EQU']['BETA'].data()

        if self.register(key, ['betap'], 'Poloidal beta', '', 't'):
            return data['EQU']['BETAP'].data()

        if self.register(key, ['betan'], 'Normalized beta', '', 't'):
            bt = self['BT0'] * self['R0'] / self['r_geo'][-1, :]
            return abs(self['betat'] / (self['Ip'] / 1E6 / self['a'] / bt))

        if self.register(key, ['Wtot', 'energy'], 'Total energy', 'J/m^3', 'rt'):
            return data['EQU']['PRESS_KIN'].data() * 3 / 2.

        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'rt'):
            return data['EQU']['PRESS_KIN'].data()

        if self.register(key, ['Wbeam', 'beam energy'], 'Beam energy density', 'J/m^3', 'rt'):
            return data['NBI']['WBEAM'].data()  # Already in J/m^3=N/m^2

        if self.register(key, ['pbeam', 'beam pressure'], 'Beam pressure', 'N/m^2', 'rt'):
            return data['EQU']['PRESS_BEAM'].data()

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'rt'):
            return data['EQU']['T_E'].data()

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'rt'):
            return data['EQU']['DENS_E'].data()

        if self.register(key, 'ion species', 'Ion species', '1', 'i'):
            return data['INPUTS']['NAMELIS1']['NAMEP'].data()[0][0].strip("'").split(',') + data['INPUTS']['NAMELIS1']['NAMEI'].data()[0][0].strip("'").split(',')

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'irt'):
            return np.array([data['EQU']['T_I'].data()] * len(self['ion species']))

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'irt'):
            nion = []
            nion.append(data['EQU']['DENS_I'].data())
            nion.append(data['EQU']['DENS_IMP'].data())
            return np.array(nion)

        if self.register(key, 'beam species', 'Beam ion species', '1', 'b'):
            return data['INPUTS']['NAMELIS2']['NAMEB'].data()[0][0].strip("'").split(',')

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'brt'):
            return np.array([data['NBI']['ENBEAM'].data()] * len(self['beam species']))

        if self.register(key, ['Tb', 'beam temperature'], 'Beam ion temperature', 'keV', 'brt'):
            return np.array([data['NBI']['TBEAM'].data()] * len(self['beam species']))  # includes all beam species

        # -------------------------
        # Other plasma parameters
        # -------------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'rt'):
            return data['EQU']['Z_EFF'].data()

        # -------------------------
        # Diffusivities and fluxes
        # -------------------------
        if self.register(key, ['chie', 'electron heat diffisivity'], 'Electron heat diffisivity', '1/m^2/s', 'rt'):
            return data['DIFF']['CHI_E'].data()

        if self.register(key, ['chii', 'ion heat diffisivity'], 'Ion heat diffisivity', '1/m^2/s', 'rt'):
            return data['DIFF']['CHI_I'].data()

        if self.register(key, ['Qconde', 'electron conductive heat flux'], 'Electron conductive heat flux', 'W/m^2', 'rt'):
            return data['DIFF']['QCONDE'].data()

        if self.register(key, ['Qcondi', 'ion conductive heat flux'], 'Ion conductive heat flux', 'W/m^2', 'rt'):
            return data['DIFF']['QCONDI'].data()

        if self.register(key, ['Qconve', 'electron convective heat flux'], 'Electron convective heat flux', 'W/m^2', 'rt'):
            return data['DIFF']['QCONVE'].data()

        if self.register(key, ['Qconvi', 'ion convective heat flux'], 'Ion convective heat flux', 'W/m^2', 'rt'):
            return data['DIFF']['QCONVI'].data()

        if self.register(key, ['Qcondx', 'exchange heat source'], 'Exchange heat source', 'J/m^3', 'rt'):
            return data['HCD']['Q_EI'].data()

        if self.register(key, ['grho', '<grad*rho>'], 'surface averaged gradient rho', '', 'rt'):
            return data['EQU']['GRAD1RHO'].data()

        if self.register(key, ['Qe', 'total anomalous electron heat flux'], 'Total anomalous electron heat flux (Qconde + Qconve - Qx)', 'W/m^2', 'rt'):
            return data['DIFF']['E_FLUXE'].data()

        if self.register(key, ['Qi', 'total anomalous ion heat flux'], 'Total anomalous ion heat flux (Qcondi + Qconvi + Qx)', 'W/m^2', 'rt'):
            return data['DIFF']['E_FLUXI'].data()

        if self.register(key, ['Ge', 'total anomalous electron particle flux'], 'Total anomalous electron particle flux', '1/s/m^2', 'rt'):
            return data['DIFF']['P_FLUX_ELCT'].data()

        if self.register(key, ['Gi', 'total anomalous ion particle flux'], 'Total anomalous ion particle flux', '1/s/m^2', 'rt'):
            return data['DIFF']['P_FLUX_ION'].data()

        if self.register(key, ['Pr', 'total anomalous momentum flux'], 'Total anomalous momentum flux', 'kg/s^2', 'rt'):
            return data['DIFF']['ROT_FLUX'].data()

        # -------------------------
        # radial derivatives
        # -------------------------
        for k in list(self['__quantities__'].keys()):
            if k.startswith('d('):
                continue
            for dd in ['r_min', 'rho_m', 'psi', 'rho']:
                if self['__quantities__'][k]['raw_dimension'] in ['rt', 'irt', 'brt']:
                    if self.register(key, ['d(' + k + ')/d(' + dd + ')'], 'd/dr(' + self['__quantities__'][k]['description'] + ')', self['__quantities__'][k]['units'] + '/' + self['__quantities__'][dd]['units'], self['__quantities__'][k]['raw_dimension']):
                        if self['__quantities__'][k]['raw_dimension'] == 'rt':
                            n = 1
                        else:
                            n = len(self[k])
                        out = []
                        for i in range(n):
                            if self['__quantities__'][k]['raw_dimension'] == 'rt':
                                tmp = self[k]
                            else:
                                tmp = self[k][i]
                            if self['__quantities__'][dd]['raw_dimension'] == 'r':
                                out.append(gradient(tmp, axis=0) / gradient(self[dd], axis=0)[:, np.newaxis])
                            else:
                                out.append(gradient(tmp, axis=0) / gradient(self[dd], axis=0))
                        if self['__quantities__'][k]['raw_dimension'] == 'rt':
                            return out[0]
                        else:
                            return np.array(out)


######################################################
class ONETWO_statefiles_adaptor(OMFITinterfaceAdaptor):
    type = 'ONETWO_statefiles' # this adapts the data output by ONETWOtime

    @staticmethod
    def identify(data):

        from omfit_classes.omfit_base import OMFITcollection
        printd('Attempting to identify {:} type...'.format('ONETWO_statefiles'))
        if isinstance(data, OMFITcollection) and np.all([k in data for k in ['press', 'rho_grid']]):
            printd(' > Looks like it is {:} type!'.format('ONETWO_statefiles'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('ONETWO_statefiles'))

    def gather_timeslices(self, key, data):
        import numpy as np
        import numpy
        printd('gather timeslices...')
        times = list(data.keys())
        printd(' > gather {:}... found timeslices: {:}'.format(key, times))
        sh = np.shape(data[times[0]][key]['data'])
        if len(sh) == 0:  # time dependent only
            nx = 0
            ns = 0
            var = np.zeros(len(times))
        else:
            nx = sh[-1]  # length of position grid
            if len(sh) > 1:
                ns = sh[0]  # number of species
            else:
                ns = 0  # 0 means the quantity doesn't vary by species
            if ns > 0:
                var = np.zeros([ns, nx, len(times)])
            else:
                var = np.zeros([nx, len(times)])
        printd(' >> expected final shape = ', np.shape(var))
        for i, t in enumerate(times):
            newslice = data[t][key]['data']
            # printd(' >> np.shape(newslice)=',np.shape(newslice))
            if nx == 0:
                var[i] = newslice
            else:
                if ns == 0:
                    var[:, i] = newslice
                else:
                    var[:, :, i] = newslice
        printd(' >> np.shape(var)={:}'.format(np.shape(var)))
        return var

    def define_from_first_slice(self, key, data):
        printd('define from first slice...')
        t = list(data.keys())[0]
        printd(' > using first slice ({:} ms) to define {:}'.format(t, key))
        var = data[t][key]  # some applications will require you to take var['data'] later
        return var

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('ONETWO_statefiles definitions for key {:}...'.format(key))

        def interp_npsi_vars_to_rho(val):
            printd(' > interp_npsi_vars_to_rho')
            rho = self.gather_timeslices('rho_grid', data)
            rho_mhd = self.gather_timeslices('rho_mhd_gridnpsi', data)  # rho_mhd and val had both been modified using flipud. I think this just reverses 1d arrays
            printd('  >> np.shape(val) = {:}'.format(np.shape(val)))
            # val = flipud(val)
            printd('  >> np.shape(val) = {:}'.format(np.shape(val)))
            printd('  >> np.shape(rho_mhd) = {:}'.format(np.shape(rho_mhd)))
            printd('  >> np.shape(rho) = {:}'.format(np.shape(rho)))
            nt = len(data)
            out = np.zeros([len(rho[:, 0]), nt])
            for i in range(nt):
                out[:, i] = interp1e(rho_mhd[:, i], val[:, i], kind='linear')(rho[:, i])
            printd('  >>> np.shape(out) = {:}'.format(np.shape(out)))
            return out

        if self.register(key, 'time', 'Time', 's', 't'):
            printd(' > returning time data')
            result = self.gather_timeslices('time', data)
            printd(' >> result = {:}'.format(result))
            return result

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            printd(' > rho')
            rhogrid = self.define_from_first_slice('rho_grid', data)['data']
            nx = len(rhogrid)
            printd('nx=', nx)
            printd('np.shape(rhogrid)=', np.shape(rhogrid), 'rhogrid.min()=', rhogrid.min(), 'rhogrid.max()=', rhogrid.max())
            result = np.linspace(0, 1, nx)
            printd('rho: np.shape(result) =', np.shape(result), 'result.min()=', result.min(), 'result.max()=', result.max())
            return result

        if self.register(key, 'rho_m', 'Minor radius', 'm', 'rt'):
            return self.gather_timeslices('rho_grid', data)

        if self.register(key, 'a', 'Plasma midplane minor radius', 'm', 't'):
            result = interp_npsi_vars_to_rho(self.gather_timeslices('rminavnpsi', data))[-1, :]  # -1 to select the end of the position array
            printd(' >> result = {:}'.format(result))
            return result

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'rt'):
            return self.gather_timeslices('psir_grid', data)

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'rt'):
            posaxis = 0
            return (self['psi'] - self['psi'].min(axis=posaxis)[np.newaxis, :]) / ((self['psi'].max(axis=posaxis) - self['psi'].min(axis=posaxis))[np.newaxis, :])

        if self.register(key, 'r_min', 'Geometric midplane minor radius', 'm', 'rt'):
            return interp_npsi_vars_to_rho(self.gather_timeslices('rminavnpsi', data))

        if self.register(key, ['r_geo', 'r_maj'], 'Geometric midplane major radius', 'm', 'rt'):
            printd('r_geo')
            result = interp_npsi_vars_to_rho(self.gather_timeslices('rmajavnpsi', data))
            printd('np.shape(result)= {:}'.format(np.shape(result)))
            return result

        if self.register(key, ['rout', 'r_out'], 'Geometric midplane outer major radius', 'm', 'rt'):
            return interp_npsi_vars_to_rho(self.gather_timeslices('rmajavnpsi', data) +
                                           self.gather_timeslices('rminavnpsi', data))  # does this make sense?

        if self.register(key, ['R0', 'vacuum major radius'], 'Major radius of vacuum BT0 reference == R0', 'm', ''):
            return self.gather_timeslices('rmajor', data)[0]

        if self.register(key, '1/R', '<1/R>', '1/m', 'rt'):
            return interp_npsi_vars_to_rho(self.gather_timeslices('ravginpsi', data))

        if self.register(key, 'kappa', 'Elongation', '1', 'rt'):
            return interp_npsi_vars_to_rho(self.gather_timeslices('elongxnpsi', data))

        if self.register(key, 'delta', 'Triangularity', '1', 'rt'):
            return interp_npsi_vars_to_rho(0.5 * self.gather_timeslices('triangnpsi_l', data) + 0.5 * self.gather_timeslices('triangnpsi_u', data))

        if self.register(key, ['Acx', 'plasma cross section'], 'Total plasma cross section', 'm^2', 't'):
            return self.gather_timeslices('areao', data)

        if self.register(key, 'area', 'Cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return self.gather_timeslices('cxareanrho', data)

        if self.register(key, 'darea', 'Gradient of cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return gradient(self['area'])[0]

        if self.register(key, ['vol', 'V', 'volume'], 'Volume', 'm^3', 'rt'):
            printd('volume')
            integrand = 4 * np.pi ** 2 * self['R0'] * self['rho_m'] * self.gather_timeslices('hcap', data)
            positionaxis = 0
            return scipy.integrate.cumtrapz(integrand, self['rho_m'], initial=0, axis=positionaxis)

        if self.register(key, ['dvol', 'dV/drho', 'differential volume'], 'Differential volume', 'm^3', 'rt'):
            positionaxis = 0  # I know I could just put the 0 directly on the next line, but I want to be very clear about which axis I want
            return gradient(self['volume'])[positionaxis] / gradient(self['rho'])[positionaxis]

        if self.register(key, 'pprime', 'dp/dpsi', 'N/m^2', 'rt'):
            positionaxis = 0
            return gradient(self['pressure'])[positionaxis] / gradient(self['psi'])[positionaxis]

        # -------------------------
        # Fields
        # -------------------------
        if self.register(key, ['BT0', 'vacuum toroidal field'], 'Vacuum BT0 at R0', 'T', 't'):
            return self.gather_timeslices('btor', data)

        if self.register(key, ['f', 'fpol', 'FPOL', 'I_psi'], 'Bz * R (including dia/paramagnetism)', 'm*T', 'rt'):  # f of psi = R * Bt
            return self.gather_timeslices('fpsinrho', data)

        if self.register(key, 'ffprime', 'f*df/dpsi', '(m*T)^2/(V*s/rad)', 'rt'):
            return self.gather_timeslices('ffprim', data)

        if self.register(key, ['Btot_out', 'total B field out', 'B magnitude out', 'btot_out'], 'B field magnitude at outboard midplane', 'T', 'rt'):
            return self.gather_timeslices('btotrmaj', data)

        if self.register(key, ['Bp_avg', 'Bp_fsa', 'BPOL_AVG', 'Bpol_fsa'], 'Flux surface average of poloidal B field', 'T', 'rt'):
            return self.gather_timeslices('bp', data)

        # -------------------------
        # Current
        # -------------------------
        if self.register(key, ['Ip', 'total current'], 'Total plasma current ', 'A', 't'):
            return self.gather_timeslices('tot_cur', data)

        if self.register(key, ['jtot', 'current'], 'Current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.gather_timeslices('curden', data)

        if self.register(key, ['jpar', 'j//', 'parallel current'], 'Parallel current density <J.B/Bt0>', 'A/m^2', 'rt'):
            return self.gather_timeslices('curpar', data)

        if self.register(key, ['joh', 'johm', 'ohmic current'], 'Ohmic current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.gather_timeslices('curohm', data)

        if self.register(key, ['jboot', 'bootstrap current'], 'Bootstrap current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.gather_timeslices('curboot', data)

        if self.register(key, ['jb', 'beam current'], 'Beam current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.gather_timeslices('curbeam', data)

        if self.register(key, ['jrf', 'rf current'], 'RF current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.gather_timeslices('currf', data)

        if self.register(key, ['q_abs', 'safety factor magnitude'], 'Safety factor magnitude', '', 'rt'):
            return abs(self.gather_timeslices('q_value', data))  ###

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['betat'], 'Toroidal beta', '', 't'):
            return self.gather_timeslices('beta', data)

        if self.register(key, ['betap'], 'Poloidal beta', '', 't'):
            return self.gather_timeslices('betap', data)

        if self.register(key, ['betan'], 'Normalized beta', '', 't'):
            bt = self['BT0'] * self['R0'] / self['r_geo'][-1, :]
            return abs(self['betat'] / (self['Ip'] / 1E6 / self['a'] / bt))

        if self.register(key, ['Wtot', 'energy'], 'Total energy', 'J/m^3', 'rt'):
            return self['pressure'] * 3 / 2.

        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'rt'):
            return self.gather_timeslices('press', data)

        if self.register(key, ['Wbeam', 'beam energy'], 'Beam energy density', 'J/m^3', 'rt'):
            return self.gather_timeslices('wbeam', data) * 1.60218e-16  # Conversion from keV/m^3 to J/m^3=N/m^2

        if self.register(key, ['pbeam', 'beam pressure'], 'Beam pressure', 'N/m^2', 'rt'):
            return self['beam energy'] * 2 / 3.

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'rt'):
            return self.gather_timeslices('Te', data)

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'rt'):
            return self.gather_timeslices('ene', data)

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'irt'):
            return np.array([self.gather_timeslices('Ti', data)] * len(self['ion species']))

        if self.register(key, 'ion species', 'Ion species', '1', 'i'):
            result = self.define_from_first_slice('enion', data)['long_name'].split(':')[1].strip().split()
            printd(' >> result =', result)
            return result  # both primary and impurity ions

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'irt'):
            result = self.gather_timeslices('enion', data)
            printd('  >> np.shape(result) = ', np.shape(result))
            return result  # includes both primary and impurity ions

        if self.register(key, 'beam species', 'Beam ion species', '1', 'b'):
            printd(' > beam species')
            longname = self.define_from_first_slice('enbeam', data)['long_name']
            result = longname.split(':')[1].strip().split()
            printd(' longname =', longname)
            printd(' result = ', result)
            return result

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'brt'):
            printd(' > beam densities')
            result = self.gather_timeslices('enbeam', data)
            printd('  >> np.shape(result) = ', np.shape(result))
            return result  # includes all beam species

        # -------------------------
        # Other plasma parameters
        # -------------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'rt'):
            result = self.gather_timeslices('zeff', data)
            printd('  >> zeff: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['Z', 'Zi', 'charge state'], 'Ion charge state', 'amu', 'i'):
            result = self.define_from_first_slice('z', data)['data'][:, 0]
            printd('  >> zi: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['ftrap', 'trapfrac', 'trapped fraction', 'ncft'], 'Trapped particle fraction', '', 'rt'):
            result = self.gather_timeslices('ftrap', data)
            printd('  >> ftrap: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['electron collisionality', 'nuste', 'nuestar'], 'Electron collisionality', '', 'rt'):
            return self.gather_timeslices('xnuse', data)

        if self.register(key, ['ion collisionality', 'nusti', 'nuistar'], 'Ion collisionality', '', 'irt'):
            return self.gather_timeslices('xnus', data)

        if self.register(key, ['resist'], 'Sauter neoclassical resistivity', 'Ohm m', 'rt'):
            return self.gather_timeslices('eta', data)


######################################################
class TRANSP_MDS_adaptor(OMFITinterfaceAdaptor):
    type = 'TRANSP_MDS'

    @staticmethod
    def identify(data):
        printd('Attempting to identify {:} type...'.format('TRANSP_MDS'))
        if 'OUTPUTS' in data and data['OUTPUTS']['ONE_D']['Q0'].data() is not None:
            printd(' > Looks like it is {:} type!'.format('TRANSP_MDS'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('TRANSP_MDS'))

    def tr2D(self, key, data):
        import numpy as np
        import numpy
        # * X is the normalized radius of the zone centers
        # * XB is the normalized radius of the zone boundaries
        # * RMAJM is the outer midplane radius defined at XB
        # TRANSP grids are not defined on axis, hence use linear extrapolation
        xname = data['OUTPUTS']['TWO_D'][key]['XAXIS'].data()[0].strip()
        y = data['OUTPUTS']['TWO_D'][key].data()
        if y is None:
            return np.zeros(self['rho'].size, self['time'].size)
        y = y.T
        # internally we convert all TRANSP outputs to normalized radius of the zone boundaries: XB
        xb = data['OUTPUTS']['TWO_D']['XB'].data().T[:, 0]
        xb0 = np.hstack((0, xb))
        if xname in ['X', 'XB']:
            x = data['OUTPUTS']['TWO_D'][xname].data().T[:, 0]
            tmp = interp1e(x, y.T)(xb0).T
            return tmp
        else:
            raise Exception(key + ': ' + xname + ' axis interpolation to XB has not been coded up yet!')

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('TRANSP_MDS definitions...')
        if self.register(key, 'device', 'Device', '1', ''):
            return data['DEVICE'].data()

        if self.register(key, 'shot', 'Shot', '1', ''):
            return int(data['SOURCE_SHOT'].data())

        if self.register(key, 'time', 'Time', 's', 't'):
            return data['TRANSP_OUT']['TIME2D'].data()

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, ['R0', 'vacuum major radius'], 'Major radius of vacuum BT0 reference == R0', 'm', ''):
            specs = omfit_classes.utils_fusion.device_specs(tolist(self['device'])[0])
            if 'R0' in list(specs.keys()) and specs['R0'] is not None:
                return specs['R0']
            else:
                raise Exception('Plasma vacuum major radius is not defined for ' + str(self['device']))

        if self.register(key, 'rho_m', 'Minor radius', 'm', 'rt'):
            return self.tr2D('RBOUN', data) / 100.

        if self.register(key, 'a', 'Plasma midplane minor radius', 'm', 't'):
            return self['r_min'][-1, :]

        if self.register(key, 'r_min', 'Geometric midplane minor radius', 'm', 'rt'):
            return self.tr2D('RMNMP', data) / 100.

        if self.register(key, ['r_geo', 'r_maj'], 'Geometric midplane major radius', 'm', 'rt'):
            return self.tr2D('RMJMP', data) / 100.

        if self.register(key, ['rout', 'r_out'], 'Geometric midplane outer major radius', 'm', 'rt'):
            return self['r_geo'] + self['r_min']

        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            return self.tr2D('XB', data)[:, 0]

        if self.register(key, '1/R', '<1/R>', '1/m', 'rt'):
            return self.tr2D('GRI', data) * 100

        if self.register(key, ['eps', 'inverse aspect ratio'], 'epsilon: Inverse aspect ratio', '', 'rt'):
            return 1.0 / self.tr2D('ARAT', data)

        if self.register(key, 'kappa', 'Elongation', '1', 'rt'):
            return self.tr2D('ELONG', data)

        if self.register(key, 'delta', 'Triangularity', '1', 'rt'):
            return self.tr2D('TRIANG', data)

        if self.register(key, ['Acx', 'plasma cross section'], 'Total plasma cross section', 'm^2', 't'):
            return data['OUTPUTS']['ONE_D']['PAREA'].data() / 1E4  # This might actually be cross section of psi_N=0.995

        if self.register(key, ['darea'], 'Gradient of cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return self.tr2D('DAREA', data) / 1e4

        if self.register(key, ['area'], 'Cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return np.cumsum(self['darea'], axis=0)  # Inconsistent w/ Acx because of interpolation; summing raw DAREA out
            #                                      to the edge agrees perfectly with PAREA, but the position baxis for
            #                                      DAREA is X, which ends at 0.995. Extrapolating to 1 makes the result
            #                                      larger.

        if self.register(key, ['vol', 'V', 'volume'], 'Volume', 'm^3', 'rt'):
            rho_rt = np.tile(self['rho'], (self['dvol'].shape[1], 1)).T
            return scipy.integrate.cumtrapz(self['dvol'], rho_rt, axis=0, initial=0)

        if self.register(key, ['dvol', 'dV/drho', 'differential volume'], 'Differential volume', 'm^3', 'rt'):
            return self.tr2D('DVOL', data) / gradient(self['rho'])[:, np.newaxis] / 1E6

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'rt'):
            return self.tr2D('PLFLX', data)

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'rt'):
            return (self['psi'] - np.min(self['psi'], 0)[np.newaxis, :]) / (np.max(self['psi'], 0)[np.newaxis, :] - np.min(self['psi'], 0)[np.newaxis, :])

        if self.register(key, 'pprime', 'dp/dpsi', 'N/m^2', 'rt'):
            return gradient(self['pressure'])[0] / gradient(self['psi'])[0]

        # -------------------------
        # Fields
        # -------------------------
        if self.register(key, ['BT0', 'vacuum toroidal field'], 'Vacuum BT0 at R0', 'T', 't'):
            return data['OUTPUTS']['ONE_D']['BZXR'].data() / (self['R0'] * 100)

        if self.register(key, ['f', 'fpol', 'FPOL', 'I_psi'], 'Bz * R (including dia/paramagnetism)', 'm*T', 'rt'):
            return self.tr2D('GFUN', data) * data['OUTPUTS']['ONE_D']['BZXR'].data()[np.newaxis, :] / 1E2

        if self.register(key, 'fprime', 'df/dpsi', '(m*T)/(V*s/rad)', 'rt'):
            return gradient(self['f'])[0] / gradient(self['psi'])[0]

        if self.register(key, 'ffprime', 'f*df/dpsi', '(m*T)^2/(V*s/rad)', 'rt'):
            return self['f'] * self['fprime']

        if self.register(key, ['<B>', 'GB1', 'B fsa'], '<B>', 'T', 'rt'):
            return self.tr2D('GB1', data)

        if self.register(key, ['<B**2>', 'GB2', 'B sq fsa'], '<B^2>', 'T^2', 'rt'):
            return self.tr2D('GB2', data)

        if self.register(key, ['<B**-2>', 'GB2I', 'inv B sq fsa'], '<B^-2>', 'T^-2', 'rt'):
            return self.tr2D('GB2I', data)

        # -------------------------
        # Current
        # -------------------------
        if self.register(key, ['Ip', 'total current'], 'Total plasma current ', 'A', 't'):
            return data['OUTPUTS']['ONE_D']['PCURC'].data()

        if self.register(key, ['jtot', 'current'], 'Current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CUR', data) * (1E2) ** 2

        if self.register(key, ['joh', 'johm', 'ohmic current'], 'Ohmic current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CUROH', data) * (1E2) ** 2

        if self.register(key, ['jboot', 'bootstrap current'], 'Bootstrap current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CURBS', data) * (1E2) ** 2

        if self.register(key, ['j.B fsa', 'jboot.B', 'bootstrap current times B fsa'], 'Flux surf avg of B . neoclassical bootstrap current density <Jtor R0/R>', 'T*A/m^2', 'rt'):
            return self.tr2D('PLJBSNC', data) * (1E2) ** 2

        if self.register(key, ['jbeam', 'beam current'], 'Beam current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CURB', data) * (1E2) ** 2

        if self.register(key, ['jec', 'ec current'], 'EC current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('ECCUR', data) * (1E2) ** 2

        if self.register(key, ['jlh', 'lh current'], 'LH current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('LHCUR', data) * (1E2) ** 2

        if self.register(key, ['jrf', 'rf current'], 'RF current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self['ec current'] + self['rf current']

        if self.register(key, ['q_abs', 'safety factor magnitude'], 'Safety factor magnitude', '', 'rt'):
            return self.tr2D('Q', data)

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['betat'], 'Toroidal beta', '', 't'):
            dvol = data['OUTPUTS']['TWO_D']['DVOL'].data()
            bttot = data['OUTPUTS']['TWO_D']['BTTOT'].data()
            return np.sum(bttot * dvol, 1) / np.sum(dvol, 1)

        # if self.register(key,['betap'],'Poloidal beta','','t'):
        #     return

        if self.register(key, ['betan'], 'Normalized beta', '', 't'):
            bt = self['BT0'] * self['R0'] / self['r_geo'][-1, :]
            return abs(self['betat'] / (self['Ip'] / 1E6 / self['a'] / bt))

        if self.register(key, ['Wtot', 'energy'], 'Total energy', 'J/m^3', 'rt'):
            # return self.tr2D('UTOTL',data)*(1E2)**3
            return self['pressure'] * 3 / 2.

        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'rt'):
            # return self['energy']*2/3.
            return self.tr2D('PTOWB', data)

        if self.register(key, ['Wth', 'thermal energy'], 'Thermal energy', 'J/m^3', 'rt'):
            return self.tr2D('UTHRM', data) * (1E2) ** 3

        if self.register(key, ['Pth', 'thermal pressure'], 'Thermal pressure', 'N/m^2', 'rt'):
            return self['thermal energy'] * 2 / 3.

        if self.register(key, ['Wbeam', 'beam energy'], 'Beam energy density', 'J/m^3', 'rt'):
            return self['energy'] - self['thermal energy']

        if self.register(key, ['pbeam', 'beam pressure'], 'Beam pressure', 'N/m^2', 'rt'):
            return self['pressure'] - self['thermal pressure']

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'rt'):
            return self.tr2D('TE', data) / 1E3

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'rt'):
            return self.tr2D('NE', data) * 1E6

        if self.register(key, ['<ne>'], 'Volume averaged electron density', '', 't'):
            dvol = data['OUTPUTS']['TWO_D']['DVOL'].data()
            ne = data['OUTPUTS']['TWO_D']['NE'].data() * 1E6
            return np.sum(ne * dvol, 1) / np.sum(dvol, 1)

        if self.register(key, ['fGW'], 'Greenwald fraction', '', 't'):
            nGW = (self['Ip'] / 1E6 / np.pi / self['a'] ** 2)
            return self['<ne>'] / 1E20 / nGW

        if self.register(key, 'ion species', 'Ion species', '1', 'i'):
            species = []
            for s in ['3', '4', '6', 'H', 'D', 'T', 'M']:
                if 'N' + s in data['OUTPUTS']['TWO_D']:
                    species.append(s)
            # First search for individually listed specific impurities named NIMPS_*
            imp_found = False
            for s in ['C', 'Ne', ]:  # List of impurity species to search for
                if 'NIMPS_{:}'.format(s) in data['OUTPUTS']['TWO_D']:
                    species.append(s)
                    imp_found = True
            # If we can't find specific impurities listed individually, try the generic NIMP and guess which impurity
            # it is based on which machine.
            if imp_found:
                printd('Found specifically listed impurities in TRANSP statefile.')
            else:
                if 'NIMP' in data['OUTPUTS']['TWO_D']:
                    if self['device'] == 'D3D':
                        s = 'C'
                    else:
                        # Generic species guess for unknown tokamak
                        s = 'C'
                    species.append(s)
                    printd('Could not find specifically listed impurities in TRANSP statefile so used NIMP.')
            return species

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'irt'):
            return np.array([self.tr2D('TI', data)] * len(self['ion species'])) / 1E3

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'irt'):
            nion = []
            for s in ['3', '4', '6', 'H', 'D', 'T', 'M']:
                if 'N' + s in data['OUTPUTS']['TWO_D']:
                    nion.append(self.tr2D('N' + s, data) * 1E6)
            # First search for individually listed specific impurities named NIMPS_*
            imp_found = False
            for s in ['C', 'Ne', ]:
                if 'NIMPS_{:}'.format(s) in data['OUTPUTS']['TWO_D']:
                    imp_found = True
                    nion.append(self.tr2D('NIMPS_{:}'.format(s), data) * 1e6)
            # If we can't find specific impurities listed individually, try the generic NIMP and guess which impurity
            # it is based on which machine.
            if imp_found:
                printd('Found specifically listed impurities in TRANSP statefile.')
            else:
                if 'NIMP' in data['OUTPUTS']['TWO_D']:
                    nion.append(self.tr2D('NIMP', data) * 1e6)
                    printd('Could not find specifically listed impurities in TRANSP statefile so used NIMP.')
            return np.array(nion)

        if self.register(key, 'beam species', 'Beam ion species', '1', 'b'):
            species = []
            for s in ['H', 'D', 'T', 'He4', 'He3']:
                if 'NB_F1_' + s in data['OUTPUTS']['TWO_D']:
                    species.append(s)
            return species

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'brt'):
            nion = []
            for s in ['H', 'D', 'T', 'He4', 'He3']:
                if 'NB_F1_' + s in data['OUTPUTS']['TWO_D']:
                    tot_s = self.tr2D('NB_F' + str(1) + '_' + s, data) * 1E6
                    for k in range(2, 4):
                        tot_s += self.tr2D('NB_F' + str(k) + '_' + s, data) * 1E6
                    nion.append(tot_s)
            return np.array(nion)

        # -----------------------
        # Other plasma parameters
        # -----------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'rt'):
            return self.tr2D('ZEFFP', data)

        if self.register(key, ['Z', 'Zi', 'charge state'], 'Ion charge state', 'amu', 'i'):
            # This could also have been implemented by looking for ZIMPS_* and then falling back to XZIMP if not found.
            s = self['ion species']
            z_lookup = {'3': 3, '4': 4, '6': 6,
                        'H': 1, 'D': 1, 'T': 1,
                        'He': 2, 'Li': 3, 'Be': 4, 'B': 5,
                        'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
                        'M': 0}  # I don't know what this is
            return [z_lookup.get(ss, 0) for ss in s]  # Defaults to zero if it can't find the element in its table

        if self.register(key, ['ftrap', 'trapfrac', 'trapped fraction', 'ncft'], 'Trapped particle fraction', '', 'rt'):
            result = self.tr2D('NCFT', data)
            printd('  >> ftrap: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['resist'], 'Sauter neoclassical resistivity', 'Ohm m', 'rt'):
            return self.tr2D('ETA_SNC', data) / 100.

        if self.register(key, ['spitzer'], 'Spitzer resistivity', 'Ohm m', 'rt'):
            return self.tr2D('ETA_SP', data) / 100.

        if self.register(key, ['lnLambda_e'], 'Coulomb logarithm lnLambda for electrons', '', 'rt'):
            return self.tr2D('CLOGE', data)

        if self.register(key, ['lnLambda_i'], 'Coulomb logarithm lnLambda for ions', '', 'rt'):
            return self.tr2D('CLOGI', data)

        if self.register(key, ['electron collisionality', 'nuste', 'nuestar'], 'Electron collisionality', '', 'rt'):
            return self.tr2D('NUSTE', data)

        if self.register(key, ['ion collisionality', 'nusti', 'nuistar'], 'Ion collisionality', '', 'irt'):
            return np.array([self.tr2D('NUSTI', data)] * len(self['ion species']))


######################################################
class TRANSP_CDF_adaptor(OMFITinterfaceAdaptor):
    type = 'TRANSP_CDF'

    @staticmethod
    def identify(data):
        printd('Attempting to identify {:} type...'.format('TRANSP_CDF'))
        if 'NZONES' in data.get('_globals', {}):
            printd(' > Looks like it is {:} type!'.format('TRANSP_CDF'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('TRANSP_CDF'))

    def tr2D(self, key, data):
        """
        Interpolates all 2D data from transp onto a consistent "zone boundary" grid,
        including interpolation to axis.

        :param key: str.
        :param data: OMFITnc. netcdf TRANSP output
        :return:

        """
        import numpy as np
        import numpy
        # * X is the normalized radius of the zone centers
        # * XB is the normalized radius of the zone boundaries
        # * RMAJM is the outer midplane radius defined at XB
        # TRANSP grids are not defined on axis, hence use linear extrapolation
        xname = data[key]['__dimensions__'][1].strip()
        y = data[key]['data']
        if y is None:
            return np.zeros(self['rho'].size, self['time'].size)
        y = y.T
        # internally we convert all TRANSP outputs to normalized radius of the zone boundaries: XB
        xb = data['XB']['data'].T[:, 0]
        xb0 = np.hstack((0, xb))
        if xname in ['X', 'XB']:
            x = data[xname]['data'].T[:, 0]
            tmp = interp1e(x, y.T)(xb0).T
            return tmp
        else:
            raise Exception(key + ': ' + xname + ' axis interpolation to XB has not been coded up yet!')

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('TRANSP_CDF definitions...')
        if self.register(key, 'device', 'Device', '1', ''):
            return tokamak(data['_globals'].get('device', 'UNKNOWN'))

        if self.register(key, 'shot', 'Shot', '1', ''):
            return int(data['_globals']['shot'])

        if self.register(key, 'time', 'Time', 's', 't'):
            return data['TIME']['data']

        # -------------------------
        # Geometry
        # -------------------------
        if self.register(key, ['R0', 'vacuum major radius'], 'Major radius of vacuum BT0 reference == R0', 'm', ''):
            specs = omfit_classes.utils_fusion.device_specs(tolist(self['device'])[0])
            if 'R0' in specs.keys() and specs['R0'] is not None:
                return specs['R0']
            else:
                raise Exception('Plasma vacuum major radius is not defined for ' + str(self['device']))

        if self.register(key, 'rho_m', 'Minor radius', 'm', 'rt'):
            return self.tr2D('RBOUN', data) / 100.

        if self.register(key, 'a', 'Plasma midplane minor radius', 'm', 't'):
            return self['r_min'][-1, :]

        if self.register(key, 'r_min', 'Geometric midplane minor radius', 'm', 'rt'):
            return self.tr2D('RMNMP', data) / 100.

        if self.register(key, ['r_geo', 'r_maj'], 'Geometric midplane major radius', 'm', 'rt'):
            return self.tr2D('RMJMP', data) / 100.

        if self.register(key, ['rout', 'r_out'], 'Geometric midplane outer major radius', 'm', 'rt'):
            return self['r_geo'] + self['r_min']

        if self.register(key, 'rho', 'Normalized minor radius', '1', 'r'):
            return self.tr2D('XB', data)[:, 0]

        if self.register(key, '1/R', '<1/R>', '1/m', 'rt'):
            return self.tr2D('GRI', data) * 100

        if self.register(key, ['eps', 'inverse aspect ratio'], 'epsilon: Inverse aspect ratio', '', 'rt'):
            return 1.0 / self.tr2D('ARAT', data)

        if self.register(key, 'kappa', 'Elongation', '1', 'rt'):
            return self.tr2D('ELONG', data)

        if self.register(key, 'delta', 'Triangularity', '1', 'rt'):
            return self.tr2D('TRIANG', data)

        if self.register(key, ['Acx', 'plasma cross section'], 'Total plasma cross section', 'm^2', 't'):
            return data['PAREA']['data'] / 1E4  # This might actually be cross section of psi_N=0.995

        if self.register(key, ['darea'], 'Gradient of cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return self.tr2D('DAREA', data) / 1e4

        if self.register(key, ['area'], 'Cross sectional area enclosed by each flux surface', 'm^2', 'rt'):
            return np.cumsum(self['darea'], axis=0)  # Inconsistent w/ Acx because of interpolation; summing raw DAREA out
            #                                      to the edge agrees perfectly with PAREA, but the position baxis for
            #                                      DAREA is X, which ends at 0.995. Extrapolating to 1 makes the result
            #                                      larger.

        if self.register(key, ['vol', 'V', 'volume'], 'Volume', 'm^3', 'rt'):
            rho_rt = np.tile(self['rho'], (self['dvol'].shape[1], 1)).T
            return scipy.integrate.cumtrapz(self['dvol'], rho_rt, axis=0, initial=0)

        if self.register(key, ['dvol', 'dV/drho', 'differential volume'], 'Differential volume', 'm^3', 'rt'):
            return self.tr2D('DVOL', data) / gradient(self['rho'])[:, np.newaxis] / 1E6

        if self.register(key, 'psi', 'Poloidal flux', 'V*s/rad', 'rt'):
            return self.tr2D('PLFLX', data)

        if self.register(key, ['psin', 'psi_n'], 'Normalized poloidal flux', '1', 'rt'):
            return (self['psi'] - np.min(self['psi'], 0)[np.newaxis, :]) / (
                    np.max(self['psi'], 0)[np.newaxis, :] - np.min(self['psi'], 0)[np.newaxis, :])

        if self.register(key, 'pprime', 'dp/dpsi', 'N/m^2', 'rt'):
            return gradient(self['pressure'])[0] / gradient(self['psi'])[0]

        # -------------------------
        # Fields
        # -------------------------
        if self.register(key, ['BT0', 'vacuum toroidal field'], 'Vacuum BT0 at R0', 'T', 't'):
            return data['BZXR']['data'] / (self['R0'] * 100)

        if self.register(key, ['f', 'fpol', 'FPOL', 'I_psi'], 'Bz * R (including dia/paramagnetism)', 'm*T', 'rt'):
            return self.tr2D('GFUN', data) * data['BZXR']['data'][np.newaxis, :] / 1E2

        if self.register(key, 'fprime', 'df/dpsi', '(m*T)/(V*s/rad)', 'rt'):
            return gradient(self['f'])[0] / gradient(self['psi'])[0]

        if self.register(key, 'ffprime', 'f*df/dpsi', '(m*T)^2/(V*s/rad)', 'rt'):
            return self['f'] * self['fprime']

        if self.register(key, ['<B>', 'GB1', 'B fsa'], '<B>', 'T', 'rt'):
            return self.tr2D('GB1', data)

        if self.register(key, ['<B**2>', 'GB2', 'B sq fsa'], '<B^2>', 'T^2', 'rt'):
            return self.tr2D('GB2', data)

        if self.register(key, ['<B**-2>', 'GB2I', 'inv B sq fsa'], '<B^-2>', 'T^-2', 'rt'):
            return self.tr2D('GB2I', data)

        # -------------------------
        # Current
        # -------------------------
        if self.register(key, ['Ip', 'total current'], 'Total plasma current ', 'A', 't'):
            return data['PCURC']['data']

        if self.register(key, ['jtot', 'current'], 'Current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CUR', data) * (1E2) ** 2

        if self.register(key, ['joh', 'johm', 'ohmic current'], 'Ohmic current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CUROH', data) * (1E2) ** 2

        if self.register(key, ['jboot', 'bootstrap current'], 'Bootstrap current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CURBS', data) * (1E2) ** 2

        if self.register(key, ['j.B fsa', 'jboot.B', 'bootstrap current times B fsa'],
                         'Flux surf avg of B . neoclassical bootstrap current density <Jtor R0/R>', 'T*A/m^2', 'rt'):
            return self.tr2D('PLJBSNC', data) * (1E2) ** 2

        if self.register(key, ['jbeam', 'beam current'], 'Beam current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('CURB', data) * (1E2) ** 2

        if self.register(key, ['jec', 'ec current'], 'EC current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('ECCUR', data) * (1E2) ** 2

        if self.register(key, ['jlh', 'lh current'], 'LH current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self.tr2D('LHCUR', data) * (1E2) ** 2

        if self.register(key, ['jrf', 'rf current'], 'RF current density <Jtor R0/R>', 'A/m^2', 'rt'):
            return self['ec current'] + self['rf current']

        if self.register(key, ['q_abs', 'safety factor magnitude'], 'Safety factor magnitude', '', 'rt'):
            return self.tr2D('Q', data)

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['betat'], 'Toroidal beta', '', 't'):
            dvol = data['DVOL']['data']
            bttot = data['BTTOT']['data']
            return np.sum(bttot * dvol, 1) / np.sum(dvol, 1)

        # if self.register(key,['betap'],'Poloidal beta','','t'):
        #     return

        if self.register(key, ['betan'], 'Normalized beta', '', 't'):
            bt = self['BT0'] * self['R0'] / self['r_geo'][-1, :]
            return abs(self['betat'] / (self['Ip'] / 1E6 / self['a'] / bt))

        if self.register(key, ['Wtot', 'energy'], 'Total energy', 'J/m^3', 'rt'):
            # return self.tr2D('UTOTL',data)*(1E2)**3
            return self['pressure'] * 3 / 2.

        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'rt'):
            # return self['energy']*2/3.
            return self.tr2D('PTOWB', data)

        if self.register(key, ['Wth', 'thermal energy'], 'Thermal energy', 'J/m^3', 'rt'):
            return self.tr2D('UTHRM', data) * (1E2) ** 3

        if self.register(key, ['Pth', 'thermal pressure'], 'Thermal pressure', 'N/m^2', 'rt'):
            return self['thermal energy'] * 2 / 3.

        if self.register(key, ['Wbeam', 'beam energy'], 'Beam energy density', 'J/m^3', 'rt'):
            return self['energy'] - self['thermal energy']

        if self.register(key, ['pbeam', 'beam pressure'], 'Beam pressure', 'N/m^2', 'rt'):
            return self['pressure'] - self['thermal pressure']

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'rt'):
            return self.tr2D('TE', data) / 1E3

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'rt'):
            return self.tr2D('NE', data) * 1E6

        if self.register(key, ['<ne>'], 'Volume averaged electron density', '', 't'):
            dvol = data['DVOL']['data']
            ne = data['NE']['data'] * 1E6
            return np.sum(ne * dvol, 1) / np.sum(dvol, 1)

        if self.register(key, ['fGW'], 'Greenwald fraction', '', 't'):
            nGW = (self['Ip'] / 1E6 / np.pi / self['a'] ** 2)
            return self['<ne>'] / 1E20 / nGW

        if self.register(key, 'ion species', 'Ion species', '1', 'i'):
            species = []
            for s in ['3', '4', '6', 'H', 'D', 'T', 'M']:
                if 'N' + s in data:
                    species.append(s)
            # First search for individually listed specific impurities named NIMPS_*
            imp_found = False
            for s in ['C', 'Ne', ]:  # List of impurity species to search for
                if 'NIMPS_{:}'.format(s) in data:
                    species.append(s)
                    imp_found = True
            # If we can't find specific impurities listed individually, try the generic NIMP and guess which impurity
            # it is based on which machine.
            if imp_found:
                printd('Found specifically listed impurities in TRANSP statefile.')
            else:
                if 'NIMP' in data:
                    if self['device'] == 'D3D':
                        s = 'C'
                    else:
                        # Generic species guess for unknown tokamak
                        s = 'C'
                    species.append(s)
                    printd('Could not find specifically listed impurities in TRANSP statefile so used NIMP.')
            return species

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'irt'):
            return np.array([self.tr2D('TI', data)] * len(self['ion species'])) / 1E3

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'irt'):
            nion = []
            for s in ['3', '4', '6', 'H', 'D', 'T', 'M']:
                if 'N' + s in data:
                    nion.append(self.tr2D('N' + s, data) * 1E6)
            # First search for individually listed specific impurities named NIMPS_*
            imp_found = False
            for s in ['C', 'Ne', ]:
                if 'NIMPS_{:}'.format(s) in data:
                    imp_found = True
                    nion.append(self.tr2D('NIMPS_{:}'.format(s), data) * 1e6)
            # If we can't find specific impurities listed individually, try the generic NIMP and guess which impurity
            # it is based on which machine.
            if imp_found:
                printd('Found specifically listed impurities in TRANSP statefile.')
            else:
                if 'NIMP' in data:
                    nion.append(self.tr2D('NIMP', data) * 1e6)
                    printd('Could not find specifically listed impurities in TRANSP statefile so used NIMP.')
            return np.array(nion)

        if self.register(key, 'beam species', 'Beam ion species', '1', 'b'):
            species = []
            for s in ['H', 'D', 'T', 'He4', 'He3']:
                if 'NB_F1_' + s in data:
                    species.append(s)
            return species

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'brt'):
            nion = []
            for s in ['H', 'D', 'T', 'He4', 'He3']:
                if 'NB_F1_' + s in data:
                    tot_s = self.tr2D('NB_F' + str(1) + '_' + s, data) * 1E6
                    for k in range(2, 4):
                        tot_s += self.tr2D('NB_F' + str(k) + '_' + s, data) * 1E6
                    nion.append(tot_s)
            return np.array(nion)

        # -----------------------
        # Other plasma parameters
        # -----------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'rt'):
            return self.tr2D('ZEFFP', data)

        if self.register(key, ['Z', 'Zi', 'charge state'], 'Ion charge state', 'amu', 'i'):
            # This could also have been implemented by looking for ZIMPS_* and then falling back to XZIMP if not found.
            s = self['ion species']
            z_lookup = {'3': 3, '4': 4, '6': 6,
                        'H': 1, 'D': 1, 'T': 1,
                        'He': 2, 'Li': 3, 'Be': 4, 'B': 5,
                        'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
                        'M': 0}  # I don't know what this is
            return [z_lookup.get(ss, 0) for ss in s]  # Defaults to zero if it can't find the element in its table

        if self.register(key, ['ftrap', 'trapfrac', 'trapped fraction', 'ncft'], 'Trapped particle fraction', '', 'rt'):
            result = self.tr2D('NCFT', data)
            printd('  >> ftrap: np.shape(result) = ', np.shape(result))
            return result

        if self.register(key, ['resist'], 'Sauter neoclassical resistivity', 'Ohm m', 'rt'):
            return self.tr2D('ETA_SNC', data) / 100.

        if self.register(key, ['spitzer'], 'Spitzer resistivity', 'Ohm m', 'rt'):
            return self.tr2D('ETA_SP', data) / 100.

        if self.register(key, ['lnLambda_e'], 'Coulomb logarithm lnLambda for electrons', '', 'rt'):
            return self.tr2D('CLOGE', data)

        if self.register(key, ['lnLambda_i'], 'Coulomb logarithm lnLambda for ions', '', 'rt'):
            return self.tr2D('CLOGI', data)

        if self.register(key, ['electron collisionality', 'nuste', 'nuestar'], 'Electron collisionality', '', 'rt'):
            return self.tr2D('NUSTE', data)

        if self.register(key, ['ion collisionality', 'nusti', 'nuistar'], 'Ion collisionality', '', 'irt'):
            return np.array([self.tr2D('NUSTI', data)] * len(self['ion species']))


######################################################
class pFile_adaptor(OMFITinterfaceAdaptor):
    # NOTE: this adaptor has hardwired 3 ion species: impurities, beam, main
    type = 'OSBORNE_pFile'

    @staticmethod
    def identify(data):
        import numpy as np
        import numpy
        printd('Attempting to identify {:} type...'.format('OSBORNE_pFile'))
        if isinstance(data, dict) and np.all([k in data for k in ['ne', 'N Z A']]):
            if len(data['N Z A']['Z']) != 3:
                return False
            printd(' > Looks like it is {:} type!'.format('OSBORNE_pFile'))
            return True
        else:
            printd(' > It does not seem to be {:} type.'.format('OSBORNE_pFile'))

    def definitions(self, key, data):
        import numpy as np
        import numpy
        printd('%s definitions...' % self.type)

        if self.register(key, 'psin', 'Normalized poloidal flux', '1', 'r'):
            return np.linspace(0, 1, len(data['ne']['data']))

        # -------------------------
        # Energy, pressure and power
        # -------------------------
        if self.register(key, ['ptot', 'pressure'], 'Total pressure', 'N/m^2', 'r'):
            # return self['energy']*2/3.
            return interp1e(data['ptot']['psinorm'], data['ptot']['data'])(self['psin']) * 1E3

        # -------------------------
        # Temperature and densities
        # -------------------------
        if self.register(key, ['Te', 'electron temperature'], 'Electron temperature', 'keV', 'r'):
            return interp1e(data['te']['psinorm'], data['te']['data'])(self['psin'])

        if self.register(key, ['Ti', 'ion temperature'], 'Ion temperature', 'keV', 'ir'):
            return np.array([interp1e(data['ti']['psinorm'], data['ti']['data'])(self['psin'])] * 2)

        if self.register(key, ['ne', 'electron density'], 'Electron density', '1/m^3', 'r'):
            return interp1e(data['ne']['psinorm'], data['ne']['data'])(self['psin']) * 1E20

        if self.register(key, ['ni', 'ion densities'], 'Ion densities', '1/m^3', 'ir'):
            ni = interp1e(data['ni']['psinorm'], data['ni']['data'])(self['psin']) * 1E20
            nimp = interp1e(data['nz1']['psinorm'], data['nz1']['data'])(self['psin']) * 1E20
            return np.array([ni, nimp])

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'br'):
            nb = interp1e(data['nb']['psinorm'], data['nb']['data'])(self['psin']) * 1E20
            return np.array([nb])

        if self.register(key, ['nb', 'beam densities'], 'Beam ion densities', '1/m^3', 'br'):
            nb = interp1e(data['nb']['psinorm'], data['nb']['data'])(self['psin']) * 1E20
            return np.array([nb])

        # -------------------------
        # Other plasma parameters
        # -------------------------
        if self.register(key, 'Zeff', 'Effective impurity charge', 'amu', 'r'):
            # np.sum(ni*Z^2)/np.sum(ni*Z)=np.sum(ni*Z^2)/ne
            ni = self['ni']
            nb = self['nb']
            Zi = data['N Z A']['Z']
            return (ni[1] * Zi[0] ** 2 +  # impurity
                    nb[0] * Zi[1] ** 2 +  # beam
                    ni[0] * Zi[2] ** 2  # main
                    ) / (
                           ni[1] * Zi[0] +
                           nb[0] * Zi[1] +
                           ni[0] * Zi[2]
                   )
