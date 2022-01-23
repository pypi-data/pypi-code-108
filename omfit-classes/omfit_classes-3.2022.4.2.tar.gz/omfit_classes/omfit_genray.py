try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_nc import OMFITnc
from omfit_classes.fluxSurface import *

__all__ = ['OMFITgenray']


class OMFITgenray(OMFITnc):
    def pr(self, inp):
        out = inp.T.copy()
        #        out[np.where(self,['wr']['data'].T==0)]=np.nan
        #        out[np.where(self,['wr']['data'].T is nan)]=np.nan
        return out

    def slow_fast(self):
        n_par = self.pr(self['wnpar']['data'])
        n_per = self.pr(self['wnper']['data'])

        S = self.pr(self['cweps11']['data'])
        S = S[:, :, 0] + 1.0j * S[:, :, 1]
        D = self.pr(self['cweps12']['data'])
        D = (D[:, :, 0] + 1.0j * D[:, :, 1]) / -1.0j
        P = self.pr(self['cweps33']['data'])
        P = P[:, :, 0] + 1.0j * P[:, :, 1]
        R = S + D
        L = S - D

        A = S
        B = R * L + P * S - P * n_par ** 2 - S * n_par ** 2
        C = P * (R * L - 2 * S * n_par ** 2 + n_par ** 4)
        n_per2_f = (B - np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
        n_per2_s = (B + np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)

        tmp = np.zeros((n_per2_s.shape[0], n_per2_s.shape[1], 2))
        tmp[:, :, 0] = abs(n_per2_s - n_per ** 2)
        tmp[:, :, 1] = abs(n_per2_f - n_per ** 2)
        slow_fast = np.argmin(tmp, 2) * 1.0

        return slow_fast

    def to_omas(self, ods=None, time_index=0, new_sources=True, n_rho=201):
        """
        translate GENRAY class to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :param new_sources: wipe out existing sources

        :return: ODS
        """
        from omas import ODS, omas_environment

        if ods is None:
            ods = ODS()

        if new_sources or 'core_sources.source' not in ods:
            ods['core_sources']['source'] = ODS()
            s = 0
        else:
            s = len(ods['core_sources']['source'])

        freq = self['freqcy']['data'] / 1e9
        ergs_to_J = 1e-7
        cm_to_m = 1e-2
        with omas_environment(ods, cocosio=5):
            if self['freqcy']['data'] < 100e6:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY IC heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY IC'
                ods[f'core_sources.source.{s}.identifier.index'] = 5  # IC
            elif self['freqcy']['data'] < 1e9:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY Helicon heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY Helicon'
                ods[f'core_sources.source.{s}.identifier.index'] = 5  # Helicon
            elif self['freqcy']['data'] < 10e9:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY LH heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY LH'
                ods[f'core_sources.source.{s}.identifier.index'] = 4  # LH
            else:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY EC heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY EC'
                ods[f'core_sources.source.{s}.identifier.index'] = 3  # ECH
            source = ods[f'core_sources.source.{s}.profiles_1d'][time_index]

            source['j_parallel'] = self['s_cur_den_onetwo']['data'] / (cm_to_m ** 2)  # from A/cm^2 to A/m^2
            source['electrons']['energy'] = self['powden_e']['data'] * ergs_to_J / (cm_to_m ** 3)  # from erg/cm^3/s to J/m^3/s
            source['total_ion_energy'] = self['powden_i']['data'] * ergs_to_J / (cm_to_m ** 3)  # from erg/cm^3/s to J/m^3/s
            rho = np.linspace(0, 1, n_rho)
            rho_genray = self['rho_bin_center']['data']
            source['grid']['rho_tor_norm'] = rho
            source['j_parallel'] = interp1e(rho_genray, source['j_parallel'])(rho)
            source['electrons']['energy'] = interp1e(rho_genray, source['electrons']['energy'])(rho)
            source['total_ion_energy'] = interp1e(rho_genray, source['total_ion_energy'])(rho)
        return ods

    def plot(self, gEQDSK=None, showSlowFast=False):

        rayList = 'all'
        minPow = 0.01

        ax = pyplot.gcf().add_subplot(121, aspect='equal')
        if gEQDSK is None:
            gEQDSK = {}
            gEQDSK['RHORZ'] = self['eqdsk_psi']['data']
            gEQDSK['R'] = self['eqdsk_r']['data']
            gEQDSK['Z'] = self['eqdsk_z']['data']

            n = 10
            flx = fluxSurfaces(
                Rin=self['eqdsk_r']['data'],
                Zin=self['eqdsk_z']['data'],
                PSIin=self['eqdsk_psi']['data'],
                Btin=self['eqdsk_psi']['data'] * 0,
                levels=n,
                quiet=True,
                cocosin=1,
            )
            for k in range(n):
                pyplot.plot(flx['flux'][k]['R'], flx['flux'][k]['Z'], 'k', linewidth=0.5)
            pyplot.xlabel('R')
            pyplot.ylabel('Z')
        else:
            gEQDSK.plot(only2D=True)

        pyplot.title('Ray trajectories')

        # plot the rays
        mask = np.ones(self['wr']['data'].shape)
        mask[self['wr']['data'] == 0] = np.nan

        pow = self['delpwr']['data'].T
        pow_norm = pow / np.nanmax(pow)
        mask[pow_norm.T < minPow] = np.nan

        X_ = (self['wr']['data'] * mask).T / 100.0
        Y_ = (self['wz']['data'] * mask).T / 100.0
        Z_ = pow_norm
        if showSlowFast:
            SF_ = self.slow_fast()
        if rayList == 'all':
            X = X_
            Y = Y_
            Z = Z_
            if showSlowFast:
                SF = SF_
        else:
            X = X_[:, rayList[0]]
            Y = Y_[:, rayList[0]]
            Z = Z_[:, rayList[0]]
            SF = SF_[:, rayList[0]]
            for s in rayList[1:]:
                X = np.vstack((X, X_[:, s]))
                Y = np.vstack((Y, Y_[:, s]))
                Z = np.vstack((Z, Z_[:, s]))
                if showSlowFast:
                    SF = np.vstack((SF, SF_[:, s]))
            X = X.T
            Y = Y.T
            Z = Z.T
            if showSlowFast:
                SF = SF.T

        X = np.fliplr(X)
        Y = np.fliplr(Y)
        Z = np.fliplr(Z)
        if showSlowFast:
            SF = np.fliplr(SF)

        CS = plotc(X, Y, Z, linewidth=1.5)
        if CS is not None:
            pyplot.colorbar(CS[0])

        if showSlowFast:
            tmpX = X.copy()
            tmpY = Y.copy()
            tmpX[np.where(SF == 0)] = np.nan
            tmpY[np.where(SF == 0)] = np.nan
            pyplot.plot(tmpX, tmpY, '--w', linewidth=1.3)

        ax = pyplot.gcf().add_subplot(222)
        pyplot.plot(
            self['rho_bin_center']['data'],
            self['powden']['data'],
            'k-',
            linewidth=1.5,
            label='$P_{LH}$ $\\rightarrow$ ' + format(self['power_inj_total']['data'] / 1e7 / 1e6, '3.3g') + " MW",
        )
        pyplot.xlabel('$\\rho$')
        pyplot.ylabel(self['powden']['units'])
        pyplot.ylim([-max(abs(self['powden']['data'])), max(abs(self['powden']['data']))])
        pyplot.legend(loc=2)

        ax = pyplot.twinx(ax)
        pyplot.plot(
            self['rho_bin_center']['data'],
            self['s_cur_den_parallel']['data'],
            'r-',
            linewidth=1.5,
            label='$J_\\parallel$ $\\rightarrow$ ' + format(self['parallel_cur_total']['data'] / 1e6, '3.3g') + " MA",
        )
        pyplot.xlabel('$\\rho$')
        pyplot.ylabel(self['s_cur_den_parallel']['units'])
        pyplot.ylim([-max(abs(self['s_cur_den_parallel']['data'])), max(abs(self['s_cur_den_parallel']['data']))])
        pyplot.legend(loc=3)

        X = np.fliplr((self['ws']['data'] * mask).T)
        Y = np.fliplr((self['wnpar']['data'] * mask).T)

        ax = pyplot.gcf().add_subplot(224)
        plotc(X / 100.0, Y, Z, linewidth=1.5)
        pyplot.title('Parallel refractive index $n_\\parallel$')
        pyplot.xlabel('Rays poloidal distance [m]')
