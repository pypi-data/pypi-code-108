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

from omfit_classes.utils_math import *
from omfit_classes.omfit_base import OMFITtree
from omfit_classes.omfit_osborne import OMFITpFile
from omfit_classes.omfit_eqdsk import OMFITgeqdsk
from omfit_classes.omfit_data import OMFITncDataset, OMFITncDynamicDataset, importDataset
from omas import ODS, omas_environment, cocos_transform, define_cocos
from omfit_classes.omfit_omas_utils import add_generic_OMFIT_info_to_ods
from omfit_classes.omfit_rdb import OMFITrdb

import inspect
import numpy as np
from uncertainties import unumpy, ufloat
from uncertainties.unumpy import std_devs, nominal_values
from scipy import constants

np.seterr(invalid='ignore', divide='ignore')

__all__ = ['OMFITprofiles', 'OMFITprofilesDynamic', 'available_profiles']

model_tree_species = ['e', '2H1', '4He2', '6Li3', '10B5', '12C6', '14N7', '20Ne10']

# fmt: off
model_tree_quantities = ['angular_momentum', 'angular_momentum_density', 'angular_momentum_density_{species}', 'angular_momentum_{species}',
        'dn_{species}_dpsi', 'dT_{species}_dpsi', 'ELM_phase', 'ELM_since_last', 'ELM_until_next', 'Er_{species}_gradP', 'Er_{species}_gradP_Vtor',
        'Er_{species}_Vtor', 'f_Z', 'fpol', 'gamma_ExB_{species}_gradP', 'gamma_ExB_{species}_Vtor', 'J_BS', 'J_efit_norm', 'J_ohm', 'J_tot',
        'jboot_sauter', 'lnLambda', 'mass_density', 'n_fast_{species}', 'n_{species}', 'nclass_sigma', 'nu_star_{species}', 'nu_{species}',
        'omega_gyro_{species}_midplane', 'omega_LX_{species}_midplane', 'omega_N_{species}', 'omega_NTV0_{species}', 'omega_P_{species}',
        'omega_plasma_{species}', 'omega_RX_{species}_midplane', 'omega_T_{species}', 'omega_tor_{species}', 'omega_tor_{species}_KDG', 'P_brem',
        'p_fast_{species}', 'P_rad', 'P_rad_cNi', 'P_rad_cW', 'P_rad_int', 'P_rad_nNi', 'P_rad_nW', 'P_rad_ZnNi', 'P_rad_ZnW', 'p_thermal', 'p_tot',
        'p_total', 'p_{species}', 'pres', 'psi', 'psi_n', 'q', 'R_midplane', 'resistivity', 'rho', 'SAWTOOTH_phase', 'SAWTOOTH_since_last',
        'SAWTOOTH_until_next', 'sigma_nc', 'T_fast_{species}', 'T_i', 'T_i_T_e_ratio', 'T_{species}', 'time', 'Total_Zeff', 'V_pol_{species}_KDG',
        'V_tor_{species}', 'Zavg_Ni', 'Zavg_W', 'Zeff']
# fmt: on


def ugrad1(a2d):
    """
    Gradient along second axis with uncertainty propagation.
    :param a2d: 2D array or uarray
    :return:
    """
    if isinstance(a2d, DataArray):
        a2d = a2d.values
    if is_uncertain(a2d):
        dy = np.gradient(nominal_values(a2d), axis=1)
        ye = std_devs(a2d)
        sigma = np.zeros_like(ye)
        sigma[:, 1:-1] = 0.5 * np.sqrt(ye[:, :-2] ** 2 + ye[:, 2:] ** 2)
        sigma[:, 0] = 0.5 * np.sqrt(ye[:, 0] ** 2 + ye[:, 1] ** 2)
        sigma[:, -1] = 0.5 * np.sqrt(ye[:, -2] ** 2 + ye[:, -1] ** 2)
        result = unumpy.uarray(dy, sigma)
    else:
        result = np.gradient(a2d, axis=1)
    return result


def mZ(species):
    """
    Parse subscript strings and return ion mass and charge

    :param species: subscript strings such as `e`, `12C6`, `2H1`, 'fast_2H1`, ...

    :return: m and Z
    """
    species = str(species).replace('fast_', '')
    if species == 'e':
        Z = -1
        m = constants.m_e
    else:
        m = int(re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\1', species))
        name = re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\2', species)
        Z = int(re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\3', species))
        m *= constants.m_u
    return m, Z


def get_species(derived):
    """
    Identify species and ions that have density information
    """
    species = []
    for key in list(derived.data_vars.keys()):
        if not re.match('^[nT](_fast)?_([0-9]+[a-zA-Z]+[0-9]|e)$', key):
            continue
        s = key.split('_')[-1]
        if '_fast_' in key:
            s = 'fast_' + s
        species.append(s)
    species = tolist(np.unique(species))
    ions = [s for s in species if s not in ['e']]
    ions_with_dens = [i for i in ions if 'n_' + i in derived]
    ions_with_fast = [i.replace('fast_', '') for i in ions if 'fast_' in i]
    return species, ions, ions_with_dens, ions_with_fast


def available_profiles(server, shot, device='DIII-D', verbose=True):
    out = {}
    db = OMFITrdb(db='code_rundb', server='d3drdb', by_column=True)
    runs = db.select(f"SELECT * FROM plasmas WHERE code_name='OMFITprofiles' AND experiment='{device}' AND shot={shot}")
    if len(runs) == 0:
        print("No run_id found for this shot.")
        return out
    else:
        for i, runid in enumerate(runs['run_id']):
            out[
                runid
            ] = f"runid={runid} by {runs['run_by'][i]} from {runs['start_time'][i]} to {runs['stop_time'][i]} with comment: {runs['run_comment'][i]}"

    return out


class OMFITprofiles(OMFITncDataset):
    """
    Data class used by OMFITprofiles, CAKE and other
    OMFIT modules for storing experimental profiles data
    """

    def __init__(self, filename, data_vars=None, coords=None, attrs=None, comment=''):
        """
        :param filename: filename of the NetCDF file where data will be saved

        :param data_vars: see xarray.Dataset

        :param coords: see xarray.Dataset

        :param attrs: see xarray.Dataset

        :param comment: String that if set will show in the OMFIT tree GUI
        """
        self.dynaLoad = False
        super().__init__(filename, data_vars=data_vars, coords=coords, attrs=attrs)
        self.OMFITproperties['comment'] = comment

    @property
    def comment(self):
        return self.OMFITproperties['comment']

    @comment.setter
    def comment(self, comment):
        self.OMFITproperties['comment'] = comment

    def __tree_repr__(self):
        if self.comment:
            return self.__class__.__name__ + ': ' + self.comment, []
        else:
            return super().__tree_repr__()

    def to_omas(self, ods=None, times=None):
        """
        :param ods: ODS to which data will be appended

        :return: ods
        """

        if ods is None:
            ods = ODS()
            eq_times = None
        else:
            # Determine if equilibrium is avaliable and for what times.
            eq_times = ods.time('equilibrium') * 1e3  # ODS times are in s, and omfit_profiles are in ms.

        if 'device' in self.attrs:
            ods['dataset_description.data_entry.machine'] = self.attrs['device']
        if 'shot' in self.attrs:
            ods['dataset_description.data_entry.pulse'] = self.attrs['shot']

        # identify fitting coordinate
        for fit_coordinate in ['rho', 'psi_n', None]:
            if fit_coordinate in self.dims:
                break
        if fit_coordinate is None:
            raise ValueError("Fit coordinate should be 'rho' or 'psi_n'")

        # general info
        species, ions, ions_with_dens, ions_with_fast = get_species(self)
        nion = len(ions)
        if times is None:
            times = self['time'].values
        else:
            times = np.atleast_1d(times)

        # figure out time match between eq (if available) and profiles
        if eq_times is None:
            printw("No equilibrium data is avaliable to to_omas(). Some info will not be stored.")
        elif np.all([time in eq_times for time in times]):  # aka is all times have avaliable eq
            printd("Matching equilibrium times found")
        elif np.any([time in eq_times for time in times]):
            printw("Some time slices don't have corresponding equilibria!")
            printw("These time slices will be missing some information.")
        else:
            printw("No equilibrium data is avaliable to to_omas(). Some info will not be stored.")

        # assign both core_profies and edge_profiles but with data from different spatial ranges
        for coredgestring in ['core_profiles', 'edge_profiles']:
            if coredgestring.startswith('core'):
                derived = self.where(self[fit_coordinate] <= 1.0, drop=True)
                core = True
            else:
                derived = self.where(self[fit_coordinate] > 0.8, drop=True)
                core = False

            coredge = ods[coredgestring]
            prop = coredge['ids_properties']
            prop['comment'] = 'Data from OMFITprofiles.to_omas()'
            prop['homogeneous_time'] = True

            coredge['time'] = times / 1e3

            for ti, time in enumerate(times):
                profs = coredge[f'profiles_1d.{ti}']
                profs['time'] = time / 1e3

                # get corresponding eq and extract needed info
                geq = None
                R = None
                Bt = None
                Bp = None  # Make sure we don't accidentally use values from last timeslice
                if eq_times is not None and len(eq_times) > 0 and time in eq_times:
                    i_eq = np.where(time == eq_times)[0][0]  # just the first index
                    geq = OMFITgeqdsk('g0.0').from_omas(ods, time_index=i_eq)
                    # Not the most efficient but can access exiting functions better.
                    if fit_coordinate == 'psi_n':
                        psin = derived['psi_n'].values
                    else:
                        psin = derived['psi_n'].sel(time=time).values
                    psin_eq = np.linspace(0.0, 1.0, len(geq['PRES']))

                    # Re-interpolate
                    R = np.interp(psin, psin_eq, geq['fluxSurfaces']['midplane']['R'])
                    Bt = np.interp(psin, psin_eq, geq['fluxSurfaces']['midplane']['Bt'])
                    Bp = np.interp(psin, psin_eq, geq['fluxSurfaces']['midplane']['Bp'])

                for q in derived.variables:
                    fit = derived[q]
                    if q in ['time']:
                        continue
                    if q == 'rho':
                        if fit_coordinate == 'rho':
                            profs['grid.rho_tor_norm'] = derived['rho'].values
                        else:
                            profs['grid.rho_tor_norm'] = fit.sel(time=time).values
                    elif q == 'psi_n':
                        if fit_coordinate == 'psi_n':
                            profs['grid.rho_pol_norm'] = derived['psi_n'].values
                        else:
                            profs['grid.rho_pol_norm'] = fit.sel(time=time).values
                    elif q == 'n_e':
                        profs['electrons.density_thermal'] = fit.sel(time=time).values
                    elif q == 'T_e':
                        profs['electrons.temperature'] = fit.sel(time=time).values
                    elif q == 'omega_P_e' and core:  # this location is not valid OMAS location for edge profiles
                        profs['electrons.rotation.diamagnetic'] = fit.sel(time=time).values
                    elif '_' in q and q.split('_', 1)[1] in ions:
                        continue

                # thermal ions
                ni = 0
                for ion in ions[::-1]:
                    if ion == 'b' or ion.startswith('fast_'):
                        continue
                    profi = profs[f'ion.{ni}']
                    profi['density_thermal'] = derived[f'n_{ion}'].sel(time=time).values
                    if f'T_{ion}' in derived:
                        profi['temperature'] = derived[f'T_{ion}'].sel(time=time).values
                    ion_details = list(atomic_element(symbol=ion).values())[0]
                    profi['label'] = ion_details['symbol']
                    profi['z_ion'] = float(ion_details['Z_ion'])
                    profi['multiple_states_flag'] = 0
                    profi['element[0].atoms_n'] = 1
                    profi['element[0].z_n'] = float(ion_details['Z'])
                    profi['element[0].a'] = float(ion_details['A'])
                    profi['multiple_states_flag'] = 0
                    if f'V_tor_{ion}' in derived and not (f'omega_tor_{ion}' in derived and 'R_midplane' in derived):
                        profi['velocity.toroidal'] = derived[f'V_tor_{ion}'].sel(time=time).values
                    elif f'omega_tor_{ion}' in derived and 'R_midplane' in derived:
                        profi['velocity.toroidal'] = (
                            derived[f'omega_tor_{ion}'].sel(time=time) * derived['R_midplane'].sel(time=time)
                        ).values
                    if f'V_pol_{ion}' in derived:
                        profi['velocity.poloidal'] = derived[f'V_pol_{ion}'].sel(time=time).values
                    if core:  # extra rotation info for the core profiles. (Not valid nodes for edge)
                        if f'omega_P_{ion}' in derived:
                            profi['rotation.diamagnetic'] = derived[f'omega_P_{ion}'].sel(time=time).values
                        if f'omega_tor_{ion}' in derived:
                            profi['rotation_frequency_tor'] = derived[f'omega_tor_{ion}'].sel(time=time).values
                        if f'V_pol_{ion}' in derived and Bp is not None:
                            # Save to parallel streaming function, this will allow omegp to be calculated from ods
                            profi['rotation.parallel_stream_function'] = derived[f'V_pol_{ion}'].sel(time=time).values / Bp

                    # Advance ni; its important that if it is fast ion and the loop-iteration is skipped, then ni do not advance
                    ni += 1

                # fast ions
                for ion in ions:
                    if ion != 'b' and not ion.startswith('fast_'):
                        continue
                    # Get the 'base' ion for the fast population
                    if ion.startswith('fast_'):
                        base_ion = ion.replace('fast_', '')
                    elif ion == 'b':
                        base_ion == '2H1'  # back compat for '_b' notations
                    ion_details = list(atomic_element(symbol=base_ion).values())[0]

                    # Determin the corresponding ion index
                    ni = len(profs['ion'])
                    for nii in profs['ion']:
                        profi = profs[f'ion.{nii}']
                        if profi['label'] == ion_details['symbol']:
                            ni = nii
                            break
                    profi = profs[f'ion.{ni}']

                    # Add fast_ion data.
                    profi['density_fast'] = derived[f'n_{ion}'].sel(time=time).values
                    if f'p_{ion}' in derived:
                        pfast = derived[f'p_{ion}'].sel(time=time)  #'ion' here would have the form 'fast_2H1' for example
                    else:
                        pfast = derived[f'T_{ion}'].sel(time=time).values * constants.e * derived[f'n_{ion}'].sel(time=time).values
                    profi['pressure_fast_perpendicular'] = (
                        1.0 / 3.0 * pfast
                    )  # Assume isotropic fast ions. Also OMAS treats p_xxx_perp as pressure in one of the perp directions, I think.
                    profi['pressure_fast_parallel'] = 1.0 / 3.0 * pfast

                    # Attach atomic data (from base_ion)
                    profi['label'] = ion_details['symbol']
                    profi['z_ion'] = float(ion_details['Z_ion'])
                    profi['multiple_states_flag'] = 0
                    profi['element[0].atoms_n'] = 1
                    profi['element[0].z_n'] = float(ion_details['Z'])
                    profi['element[0].a'] = float(ion_details['A'])
                    profi['multiple_states_flag'] = 0

                if 'Total_Zeff' in derived:
                    profs['zeff'] = derived['Total_Zeff'].sel(time=time).values

        # Populate total pressure nodes under 'profiles_1d`
        ods.physics_core_profiles_pressures()
        # ods.physics_edge_profiles_pressures() # This function does not exist, but really should.
        return ods

    def model_tree_quantities(self, warn=True, no_update=False, details=False):
        """
        Returns list of MDS+ model_tree_quantities for all species.

        :param warn: [bool] If True, the function will warn if some of the `model_tree_quantities` are missing in
            OMFIT-source/omfit/omfit_classes/omfit_profiles.py and the model tree should be updated

        :param no_update: [bool] If True, the function will return only items that is in the object AND on the model
            tree, and ignore items that is not in model_tree_quantities.

        :return: list of strings
        """
        new_model_tree_quantities = set(model_tree_quantities)
        if not no_update:
            for item in self.variables:
                match = False
                dont_replace = ['T_i_T_e_ratio', 'J_efit_norm']  # Don't make this into T_i_T_{species} ratio please
                for s in model_tree_species:
                    if item not in dont_replace:
                        tmp = item.replace(f'_{s}', '_{species}')
                    if tmp != item:
                        match = True
                        break
                if match:
                    new_model_tree_quantities.add(tmp)
                elif not no_update:
                    new_model_tree_quantities.add(item)

        new_model_tree_quantities = sorted(list(new_model_tree_quantities), key=lambda x: x.lower())
        if new_model_tree_quantities != model_tree_quantities and warn:
            import textwrap

            if details:

                printe('WARNING!: Update model_tree_quantities in OMFIT-source/omfit/omfit_classes/omfit_profiles.py')
                printe('WARNING!: and update the OMFIT_PROFS MDS+ model tree')
                printe('-' * 140)
                printe('# fmt: off')
                printe(textwrap.fill(f'model_tree_quantities = {repr(new_model_tree_quantities)}', width=140))
                printe('# fmt: on')
                printe('-' * 140)
            else:
                printe("WARNING!: Profile vars mismatch with model tree!")
                printe("WARNING!: Consider using the 'relaxed' option with to_mds()")
                printe("WARNING!: Or use .model_tree_quantities(details=True) for instructions to update model tree.")

        quantities = []
        for item in new_model_tree_quantities:
            if '{' in item:
                for s in model_tree_species:
                    quantities.append(item.format(species=s))
            else:
                quantities.append(item)
        return quantities

    def create_model_tree(self, server, treename='OMFIT_PROFS'):
        """
        Generate MDS+ model tree

        :param server: MDS+ server

        :param treename: MDS+ treename
        """
        from omfit_classes.omfit_mds import OMFITmdsConnection

        conn = OMFITmdsConnection(server)

        quantities = {self.mds_translator(k): None for k in self.model_tree_quantities()}
        quantities['__content__'] = ''
        quantities['__x_coord__'] = ''
        quantities['__coords__'] = ''
        quantities['__dsp_name__'] = ''
        quantities['__attrs__'] = ''
        quantities['__comment__'] = ''
        conn.create_model_tree(treename, '', quantities, clear_subtree=True)

    def check_attrs(self, quiet=False):
        """
        Checks that basic/standard attrs are present. If not, they will be fill with standby values (usually 'unknown')
        Also checks that ints are ints and not int64, which would prevent json from working properly.

        :param quiet: If set to True, the function will not print warnings. By default set to False.
        """

        basic_atts = ['shot', 'produced_by_module', 'produced_by_user']

    def to_mds(self, server, shot, treename='OMFIT_PROFS', skip_vars=[], comment=None, tag=None, relaxed=False, commit=True):
        """
        This script writes the OMFITproflies datase to DIII-D MDS+ and updates d3drdb accordingly

        :param server: MDS+ server

        :param shot: shot to store the data to

        :param treename: MDS+ treename

        :param skip_vars: variables to skip uploading. Array-like

        :param relaxed: if set to True, then the function will only try to upload vars in the model_tree_quantities
            list as recorded at the beginging of this file. If False, then this funct will attempt to upload all
            variables stored in self, and fail if a profile variable cannot be uploaded (usually due there not being a
            corresponding node on the MDS+ tree).

        :param commit (bool): If set to False, the SQL query will not commit the data to the coderunrdb. This is required to be
            false for a jenkins test or else if it tries to write data to SQL database twice it will throw an error.

        :return: runid, treename
        """

        # Parse comments
        if comment is None:
            comment = self.comment
        else:
            self.comment = comment  # Update object comment to be consistent

        from omfit_classes.omfit_mds import OMFITmdsConnection, translate_MDSserver
        import json
        from omfit_classes.omfit_json import dumper

        conn = OMFITmdsConnection(server)

        if relaxed:
            quantities = self.model_tree_quantities(warn=False, no_update=True)
        else:
            quantities = self.model_tree_quantities()

        quantities = [x for x in quantities if x not in skip_vars]
        # Determine radial coord
        x_coord = None
        if 'psi_n' in self.coords.keys() and 'rho' in self.coords.keys():
            x_coord = 'unclear'
            # raise Exception("Confusion exist in radial coordinate used. Make sure dataset have a single radial coordinate.")
        elif 'psi_n' in self.coords.keys():
            x_coord = 'psi_n'
        elif 'rho' in self.coords.keys():
            x_coord = 'rho'

        # find next available runid in d3drdb for this shot
        from omfit_classes.omfit_rdb import OMFITrdb

        rdb = OMFITrdb(db='code_rundb', server='d3drdb', by_column=True)
        # add data to d3drdb (before MDS+ so that we can get a RUNID, only if it has not been allocated yet)
        data = {
            'shot': shot,
            'experiment': 'DIII-D',
            'run_type': 'user',
            'tree': treename,
            'start_time': np.min(self['time'].values),
            'stop_time': np.max(self['time'].values),
            'mdsserver': translate_MDSserver(server, ''),
            'run_comment': comment,
            #'runtag':tag
        }
        #'x_coord': x_coord,
        command = "SpGetNextOmfitProfsID"
        output = rdb.custom_procedure(command, commit=commit, **data)[-1]
        runid = output.run_id
        if runid == -1:
            print("Error fetching available runid from SQL database")
            return runid, treename
        print(f'Writing OMFITprofiles to MDS+ {runid}')

        # write to MDS+
        quantities = conn.write_dataset(
            treename=treename,
            shot=runid,
            subtree='',
            xarray_dataset=self,
            quantities=quantities,
            translator=lambda x: self.mds_translator(x),
        )
        # Store meta data
        # ====
        conn.write(treename=treename, shot=runid, node='__content__', data=';'.join(quantities))
        conn.write(treename=treename, shot=runid, node='__x_coord__', data=x_coord)

        coords_string = ''
        disp_name_string = ''
        for quant in quantities:
            coords_string = ';'.join([coords_string, ','.join(self[quant].dims[::-1])])
            # Upload reverses coord order, and above line accounts for it. But if upload behavior changes, this should
            # also change.
            try:
                disp_name = self[quant].attrs['display_name']
            except KeyError:
                disp_name = ''
            disp_name_string = ';'.join([disp_name_string, disp_name])

        # Trim the initial ':' that result from the way this is built
        if len(coords_string) > 1:
            coords_string = coords_string[1:]
        if len(disp_name_string) > 1:
            disp_name_string = disp_name_string[1:]

        conn.write(treename=treename, shot=runid, node='__coords__', data=coords_string)
        conn.write(treename=treename, shot=runid, node='__dsp_name__', data=disp_name_string)
        conn.write(treename=treename, shot=runid, node='__comment__', data=comment)

        attrs_str = json.dumps(self.attrs, default=dumper)
        conn.write(treename=treename, shot=runid, node='__attrs__', data=attrs_str)

        pprint(data)

        return runid, treename

    def mds_translator(self, inv=None, reverse=False):
        """
        Converts strings OMFITprofiles dataset keys to MDS+ nodes less than 12 chars long

        :param inv: string to which to apply the transformation
                    if `None` the transformation is applied to all of the OMFITprofiles.model_tree_quantities for sanity check

        :param reverse: reverse the translation. Used to tranlate mds+ node names back to OMFITprofile names

        :return: transformed sting or if inv is None the `mapped_model_2_mds` and `mapped_mds_2_model` dictionaries
        """
        mapper = SortedDict()
        mapper['_gradP_Vtor'] = 'gp_Vt'  # special case for 'Er_He_gradP_Vtor'
        mapper['SAWTOOTH_'] = 'ST_'
        mapper['angular_momentum_density'] = 'mom_dens'
        mapper['angular_momentum'] = 'mom'
        mapper['midplane'] = 'mid'
        mapper['omega_gyro_'] = 'gyrof_'
        mapper['omega_'] = 'w_'
        mapper['2H1'] = 'D'
        mapper['4He2'] = 'He'
        mapper['6Li3'] = 'Li'
        mapper['10B5'] = 'B'
        mapper['12C6'] = 'C'
        mapper['14N7'] = 'N'
        mapper['20Ne10'] = 'Ne'
        mapper['since_last'] = '_last'
        mapper['until_next'] = '_next'
        mapper['_total'] = '_tot'
        mapper['T_i_T_e'] = 'TiTe'
        mapper['gradP'] = 'gp'
        mapper['gamma'] = 'gm'
        mapper['_ExB'] = 'eb'

        if reverse:
            mapper = SortedDict({y.lower(): x for x, y in mapper.items()})
            inv = inv.lower()  # MDS+ is case insensitive, reverse mapping needs to adjust case for inputs
        if inv is not None:
            for match, sub in mapper.items():
                inv = inv.replace(match, sub)
            if len(inv) > 12 and not reverse:
                raise Exception(
                    f'MDS+ OMFITprofiles quantity is longer than 12 chars: {inv}\nUpdate the mds_translator function accordingly'
                )
            return inv
        else:
            model_tree_quantities = self.model_tree_quantities()
            mapped_model_2_mds = SortedDict()
            mapped_mds_2_model = SortedDict()
            for item0 in model_tree_quantities:
                item = item0
                for match, sub in mapper.items():
                    item = item.replace(match, sub)
                if len(item) > 12:
                    raise Exception(f'MDS+ string is longer than 12 chars: {item}')
                if item0 != item and item in model_tree_quantities:
                    raise Exception(f'MDS+ string shadows something else: {item}')
                if item in mapped_mds_2_model:
                    raise Exception(f'Multiple items map to the same quantity: {item0} {mapped_mds_2_model[item]}')
                mapped_model_2_mds[item0] = item
                mapped_mds_2_model[item] = item0
            return mapped_model_2_mds, mapped_mds_2_model

    def from_mds(self, server, runid):
        from omfit_classes.omfit_mds import OMFITmds
        import json

        tree = OMFITmds(server=server, treename='OMFIT_profs', shot=runid)
        contents = tree['__CONTENT__'].data()[0].split(";")
        x_coord = tree['__x_coord__'].data()[0]
        attrs_str = tree['__attrs__'].data()[0]
        coords = tree['__coords__'].data()[0].split(";")
        disp_names = tree['__dsp_name__'].data()[0].split(";")
        comment = tree['__comment__'].data()[0]
        if x_coord not in ['rho', 'psi_n']:
            raise Exception(f"x_coord was recorded as {x_coord}. It is not a recognized radial coordinate.")

        # Get the coords
        n_coord = {}
        for var in ['time', x_coord]:
            if var not in contents:
                # Tranlate exception to something that makes sense to user.
                raise Exception(f"Coordinate {var} missing from MDS+ data!")
            # Coord nodes by convention do not need translation, but might in the future
            dat = tree[var].xarray()
            dat = dat.rename(var)
            dat = dat.rename({'dim_0': var})
            self[var] = dat
            n_coord[var] = len(dat.values)

        for i, var in enumerate(contents):
            if var in ['time', x_coord]:
                # Skip, but process coord label and attrs
                self[var].attrs['display_name'] = disp_names[i]
            else:

                node = self.mds_translator(inv=var)
                dat = tree[node].xarray()
                dat = dat.rename(var)
                # Parse dims, and construct coord translator subset
                ndim_data = len(dat.dims)
                var_coords = coords[i].split(',')
                ndim_coords = len(var_coords)
                if ndim_data != ndim_coords:
                    printw(f"Dimension count does not match record for {var}.")
                else:
                    rename_dict = {}
                    for ii in np.arange(ndim_data):
                        rename_dict[f'dim_{ii}'] = var_coords[ii]
                    dat = dat.rename(rename_dict)
                self[var] = dat

        self.attrs = json.loads(attrs_str)
        self.comment = comment
        self.save()
        return self

    def to_pFiles(self, eq, times=None, shot=None):
        """
        :param eq: ODS() or dict. (OMFITtree() is a dict)  Needs to contain equilibria information, either in the form
            of the ODS with needed eq already loaded, or as OMFITgeqdsk() objects in the Dict with the time[ms] as
            keys. Times for the eq need to be strict matches to profiles times coord.

        :param times: array like. time for which you would like p files to be generated.

        :param shot: int. shot number, only relevant in generating p file names.

        :return: OMFITtree() containing a series of OMFITpfile objs.
        """

        # Generate times if needed
        if times is None:
            try:
                times = self['time'].values
            except KeyError:
                # Just here to add a helpful hint
                printw("Looking like your OMFITprofiles obj is missing 'time'. Is it properly initialized?")
                raise

        # Get shot if it can be found
        if shot is None:
            if 'shot' in self.attrs:
                shot = self.attrs['shot']
            else:
                shot = 0  # Dummy number for p file names.

        # get good_times
        good_times = []
        if isinstance(eq, ODS):
            # Check times
            good_times = [t for t in times if t in eq.time('equilibrium')]  # ODS().time('...') will throw error if time is inconsistent

        elif isinstance(eq, dict):
            for i, time in enumerate(times):
                d3_time = int(time)
                if d3_time in eq:
                    good_times.append(time)
                else:
                    printw(f"Missing eq data for {time}, it will be skipped!")
        else:
            printw("Input arg 'eq' is in unrecognized format. This will fail!")

        good_times = [t for t in good_times if t in self['time'].values]
        good_times = array(good_times)

        if len(good_times) == 0:
            printw("No valid time found! Each timesilce needs profiles and equilibrium.")
            return
        else:
            printd(f"The following time was found to be good: {good_times}")
            printd("pFiles will be produced for these times only.")

        ods = ODS()
        # Now inject eq info, but only for good_times
        if isinstance(eq, ODS):
            prof_ods.equilibrium.time = np.array(good_times)
            for i, time in enumerate(good_times):
                j = where(eq.times('equilibrium') == time)
                ods[f'equilibrium.time_slice.{i}'] = eq[f'equilibrium.time_slice.{j}']

            prof_ods.physics_consistent_times()  # Generate missing time array
        elif isinstance(eq, dict):
            for i, time in enumerate(good_times):
                d3_time = int(time)
                ods = eq[d3_time].to_omas(ods=ods, time_index=i)
                # This is not very efficient, but does make to_omas() more standardized. Open to change as needs change.
        ods = self.to_omas(times=good_times, ods=ods)

        out_tree = OMFITtree()
        for i, time in enumerate(good_times):
            d3_time = int(time)
            out_tree[d3_time] = OMFITpFile(f'p{shot:06}.{d3_time:05}').from_omas(ods, time_index=i)

        return out_tree

    def get_xkey(self):
        """
        Get the key of the x-coord associated with this data array.

        :returns: str. key of the x-coord associated with the profiles, like 'psi_n'.
        """
        dims = list(self.dims.keys())
        return dims[dims.index('time') - 1]

    def diamagnetic_frequencies(self, spc, update=True):
        """
        Calculate the diamagnetic frequency, and its density / temperature components.

        Formula: \omega_P = -\frac{T}{nZe}\frac{dn}{d\psi} - \frac{1}{Ze}\frac{dT}{d\psi}

        :param spc: Species for which temperature is fit

        :param update: bool. Set to true to update self, if False, only returns and does not update self.
            Gradients, if missing, will always update though.

        """
        freqs = xarray.Dataset()

        m, Z = mZ(spc)

        # calculate gradients if not avaliable
        if f'dn_{spc}_dpsi' not in self and f'n_{spc}' in self:
            dn_dpsi = self.xderiv('n_' + spc, coord='psi')

        if f'dT_{spc}_dpsi' not in self and f'T_{spc}' in self:
            dT_dpsi = self.xderiv('T_' + spc, coord='psi')

        # density part
        if self.check_keys(keys=[f'n_{spc}', f'T_{spc}'] + [f'dn_{spc}_dpsi'], name=f'omega_N_{spc}'):
            omega_N = -self[f'dn_{spc}_dpsi'] * self[f'T_{spc}'] * constants.eV / (self[f'n_{spc}'] * Z * constants.e)
            omega_N.attrs['long_name'] = r"$\omega_N = -\frac{T}{nZe}\frac{dn}{d\psi}$"
            freqs.update({f'omega_N_{spc}': omega_N})
        # temperature part
        if self.check_keys(keys=[f'T_{spc}'] + [f'dT_{spc}_dpsi'], name=f'omega_T_{spc}'):
            omega_T = -self[f'dT_{spc}_dpsi'] * constants.eV / (Z * constants.e)
            omega_T.attrs['long_name'] = r"$\omega_T = -\frac{1}{Ze}\frac{dT}{d\psi}$"
            freqs.update({f'omega_T_{spc}': omega_T})
        # total
        if len(freqs.data_vars) == 2:
            omega_P = omega_N + omega_T
            omega_P.attrs['long_name'] = r"$\omega_{p," + spc + r"} = -\frac{T}{nZe}\frac{dn}{d\psi} -\frac{1}{Ze}\frac{dT}{d\psi}$"
            freqs.update({f'omega_P_{spc}': omega_P})

        if update:
            self.update(freqs)
        return freqs

    def xderiv(self, key, coord='psi', update=True):
        """
        Returns the derivative of the value corresponding to key on the spatial coordinate coord.

        :param key: str. The variable

        :param coord: str. The radial coordinate with respect to which the derivative is taken

        :param update: bool. Set to true to update self, if False, only returns and does not update self.

        :return: Dataset
        """
        result = xarray.Dataset()
        xkey = self.get_xkey()
        if not self.check_keys([key, coord], name=f'd{key}_d{coord}'):
            return result
        dc = np.gradient(np.atleast_2d(self[coord].values), axis=-1)
        dkey = 'd' + key + '_d' + xkey
        if dkey in self and any(isfinite(v) for v in nominal_values(self[dkey].values).flat) and coord != xkey:
            # if we have derivative UQ from the fit method, keep it and just swap coordinates
            dx = np.gradient(np.atleast_2d(self[xkey].values), axis=-1)
            dkdc = DataArray(self[dkey] * (dx / dc), coords=self[key].coords)
        else:
            # otherwise we have to calculate the derivative numerically - huge uncertainties when propagated
            try:
                dkdc = DataArray(ugrad1(self[key].values) / dc, coords=self[key].coords)
            except ZeroDivisionError:  # This happens if dc array have 0s and self[key].values is a uarray/has uncertainty.
                i_bad = dc == 0
                dc[i_bad] = 1
                dkdc_arr = ugrad1(self[key].values) / dc
                dkdc_arr[i_bad] = ufloat(np.nan, np.nan)
                dkdc = DataArray(ugrad1(self[key].values) / dc, coords=self[key].coords)
        if coord in ['rho', 'psi_n']:
            dkdc.attrs['units'] = self[key].attrs.get('units', '')
        dkdc.attrs['long_name'] = r'd{:} / d$\{:}$'.format(key, coord)
        result['d' + key + '_d' + coord] = dkdc

        if update:
            self.update(result)
        return result

    def check_keys(self, keys=[], name='', print_error=True):
        """
        Check to make sure required data is available
        """
        missing = []
        for k in keys:
            if not k in self:
                missing.append(k)
        if missing:
            if not name:
                name = 'value'
            if print_error:
                printw('  WARNING: Could not form {:}. Missing {:}'.format(name, ', '.join(['`%s`' % x for x in missing])))
            return False
        return True

    @dynaLoad
    def reset_coords(self, names=None, drop=False):
        """
        Pass through implementation of Dataset.reset_coords(). Given names of coordinates, convert them to variables.
        Unlike Dataset.reset_corrds(), however, this function modifies in place!

        param names: Names of coords to reset. Cannot be index coords. Default to all non-index coords.

        param drop: If True, drop coords instead of converting. Default False.
        """
        self._dataset = self._dataset.reset_coords(names=names, drop=drop)

        return self


class OMFITprofilesDynamic(OMFITncDynamicDataset):
    """
    Class for dynamic calculation of derived quantities

    :Examples:

    Initialize the class with a filename and FIT Dataset.
    >> tmp=OMFITprofiles('test.nc', fits=root['OUTPUTS']['FIT'], equilibrium=root['OUTPUTS']['SLICE']['EQ'], root['SETTINGS']['EXPERIMENT']['gas'])

    Accessing a quantity will dynamically calculate it.
    >> print tmp['Zeff']

    Quantities are then stored (they are not calculated twice).
    >> tmp=OMFITprofiles('test.nc',
                          fits=root['OUTPUTS']['FIT'],
                          equilibrium=root['OUTPUTS']['SLICE']['EQ'],
                          main_ion='2H1')
    >> uband(tmp['rho'],tmp['n_2H1'])
    """

    def __init__(self, filename, fits=None, equilibrium=None, main_ion='2H1', **kw):
        OMFITncDataset.__init__(self, filename, **kw)

        if fits:
            self.update(fits)

            # profile fit dimension
            dims = list(self.dims.keys())
            xkey = dims[dims.index('time') - 1]

            # collect some meta data about which particle species have what info available
            self.attrs['main_ion'] = str(main_ion)
            species, ions, ions_with_dens, ions_with_fast = get_species(self)
            self['species'] = DataArray(species, dims=['species'])
            ions += [self.attrs['main_ion']]
            self['ions'] = DataArray(ions, dims=['ions'])
            ions_with_dens += [self.attrs['main_ion']]
            self['ions_with_dens'] = DataArray(ions_with_dens, dims=['ions_with_dens'])
            ions_with_rot = [key.replace('omega_tor_', '') for key in self if key.startswith('omega_tor') and key != 'omega_tor_e']
            self['ions_with_rot'] = DataArray(ions_with_rot, dims=['ions_with_rot'])

            # interpolate other radial coordinates from equilibrium
            printd('- Interpolating equilibrium quantities')
            needed = {
                'avg_R',
                'avg_R**2',
                'avg_1/R',
                'avg_1/R**2',
                'avg_Btot',
                'avg_Btot**2',
                'avg_vp',
                'avg_q',
                'avg_fc',
                'avg_F',
                'avg_P',
                'geo_psi',
                'geo_R',
                'geo_Z',
                'geo_a',
                'geo_eps',
                'geo_vol',
            }
            eqcoords = needed.intersection(list(equilibrium.keys()))
            for meas in eqcoords:
                if 'profile_' + xkey != meas and 'profile_psi_n' in equilibrium[meas]:
                    yy = []
                    for t in self['time'].values:
                        eq_t = equilibrium.sel(time=t, method='nearest')
                        x = np.squeeze(eq_t['profile_' + xkey])
                        y = np.squeeze(nominal_values(eq_t[meas].values))
                        yy.append(interp1e(x, y)(self[xkey].values))

                        # Ensure that 'q' is not extrapolated outside the separatrix
                        if meas == 'profile_q':
                            mask = self[xkey].values > 1.0
                            yy[-1][mask] = np.nan
                    yy = np.array(yy)
                    key = meas.replace('profile_', '')
                    self[key] = DataArray(
                        yy, coords=[fits['time'], fits[xkey]], dims=['time', xkey], attrs=copy.deepcopy(equilibrium[meas].attrs)
                    )
            self.set_coords(eqcoords)
            # reassign global attrs clobbered when assigning eq DataArrays with attrs
            self.attrs['main_ion'] = str(main_ion)
            self.save()

        self.update_dynamic_keys(self.__class__)

    def __getitem__(self, key):
        # map specific quantities to class functions
        mapper = {}
        mapper['n_' + self.attrs['main_ion']] = 'calc_n_main_ion'
        mapper['T_' + self.attrs['main_ion']] = 'calc_T_main_ion'

        # resolve mappings
        if key not in self:
            if key in mapper:
                getattr(self, mapper[key])()
                if mapper[key] in self._dynamic_keys:
                    self._dynamic_keys.pop(self._dynamic_keys.index(mapper[key]))

        # return value
        return OMFITncDynamicDataset.__getitem__(self, key)

    def calc_n_main_ion(self):
        """
        Density of the main ion species.
        Assumes quasi-neutrality.

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        mg, zg = mZ(main_ion)
        nz = self['n_e']
        for key in self['ions_with_dens'].values:
            if key != main_ion:
                nz -= self['n_' + key].values * mZ(key)[1]
        self['n_' + main_ion] = nz / zg
        invalid = np.where(self['n_' + main_ion].values <= 0)[0]
        if len(invalid) > 0:
            printe('  Had to force main ion density to be always positive!')
            printe('  This will likely present a problem when running transport codes!')
            valid = np.where(self['n_' + main_ion].values > 0)[0]
            self['n_' + main_ion].values[invalid] = np.nanmin(self['n_' + main_ion].values[valid])

    def calc_T_main_ion(self):
        """
        Temperature of the main ion species.
        Assumes it is equal to the measured ion species temperature.
        If there are multiple impurity temperatures measured, it uses the first one.

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        impurities_with_temp = [k for k in self['ions'].values if k != 'b' and 'T_' + k in list(self.keys())]
        nwith = len(impurities_with_temp)
        if nwith == 0:
            raise OMFITexception("No main or impurity ion temperatures measured")
        if nwith > 1:
            printw(
                "WARNING: Multiple impurities temperatures measured, setting main ion temperature based on {:}".format(
                    impurities_with_temp[0]
                )
            )
        for ion in impurities_with_temp:
            self['T_' + main_ion] = self[f'T_{ion}'] * 1
            break

    def calc_Zeff(self):
        r"""
        Effective charge of plasma.

        Formula: Z_{eff} = \sum{n_s Z_s^2} / \sum{n_s Z_s}

        :return: None. Updates the instance's Dataset in place.

        """
        # calculate Zeff (not assuming quasi-neutrality)
        nz_sum = np.sum([self['n_' + i].values * mZ(i)[1] for i in self['ions_with_dens'].values], axis=0)
        nz2_sum = np.sum([self['n_' + i].values * mZ(i)[1] ** 2 for i in self['ions_with_dens'].values], axis=0)
        z_eff = nz2_sum / nz_sum + 0 * self['n_e'].rename('Zeff')
        z_eff.attrs['long_name'] = r'$Z_{eff}$'
        self['Zeff'] = z_eff

    def calc_Total_Zeff(self):
        r"""
        Effective charge of plasma.

        Formula: Z_{eff} = \sum{n_s Z_s^2} / \sum{n_s Z_s}

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        mg, zg = mZ(main_ion)
        nz = self['n_e']
        for key in self['ions_with_dens'].values:
            if key != main_ion:
                nz -= self['n_' + key].values * mZ(key)[1]
        self['n_' + main_ion] = nz / zg
        invalid = np.where(self['n_' + main_ion].values <= 0)[0]
        if len(invalid) > 0:
            printe('  Had to force main ion density to be always positive!')
            printe('  This will likely present a problem when running transport codes!')
            valid = np.where(self['n_' + main_ion].values > 0)[0]
            self['n_' + main_ion].values[invalid] = np.nanmin(self['n_' + main_ion].values[valid])


if __name__ == '__main__':

    # ensure that all specified model_tree_quantities can be translated to have <=12 chars
    for s in model_tree_species:
        for q in model_tree_quantities:
            item0 = q.format(species=s)
            item = OMFITprofiles.mds_translator(None, item0)
