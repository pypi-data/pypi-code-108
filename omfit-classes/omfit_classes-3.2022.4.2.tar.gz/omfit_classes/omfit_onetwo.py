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

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_nc import OMFITnc, OMFITncData, OMFITncDataTmp
from omfit_classes.utils_math import atomic_element, deriv, interp1e
from omfit_classes.utils_fusion import is_device

import numpy as np
from scipy import integrate, interpolate

__all__ = ['OMFIToutone', 'OMFITstatefile', 'OMFIT_dump_psi', 'OMFITiterdbProfiles', 'ONETWO_beam_params_from_ods']


class OMFIToutone(SortedDict, OMFITascii):
    """
    OMFITobject used to read the ONETWO outone file

    :param filename: filename passed to OMFITascii class

    :param debug: provide verbose statements of parts of the outone file that may be skipped

    :param skip_inone: don't parse the inone section of the outone file as a Namelist (default=True)

    :param keyw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, *args, **keyw):
        self.debug = keyw.pop('debug', False)
        self.skip_inone = keyw.pop('skip_inone', True)
        OMFITascii.__init__(self, filename, *args, **keyw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        printi('Loading OUTONE file... this may take some time')
        import time as time_

        self.dynaLoad = False

        def setup_block_nodes(block_name, time):
            if block_name not in self:
                self[block_name] = SortedDict()
            if time in self[block_name]:
                tmp_num = 1
                while '%s (%d)' % (time, tmp_num) in self[block_name]:
                    tmp_num += 1
                time = '%s (%d)' % (time, tmp_num)
            self[block_name][time] = SortedDict()
            return time

        def parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=False):
            """
            bl - block split into lines (block.splitlines())
            """
            if self.debug:
                print('Calling parse_block with block_name=%s, time=%s, keys=%s' % (block_name, time, keys))
            if not isinstance(bl, list):
                raise TypeError('Expected bl to be a list')
            if len(bl) == 0:
                raise ValueError('Expected bl to be a non-zero length list')
            time = setup_block_nodes(block_name, time)
            try:
                for l in bl:
                    ls = l.strip().split()
                    if len(ls) == 0:
                        continue
                    if keys is None:
                        keys = ls
                        continue
                    if len(ls) != len(keys) and ('irf' not in keys or ('irf' in keys and ls[0] == '(s)')):
                        if not (len(ls) == 1 and ls[0] == '(cm)'):
                            if not ignore_length_mismatch and not ('(cm)' in ls or '(s)' in ls):
                                printe('Warning: In block %s, there was an unknown parsing error' % block_name)
                                printe('len(ls)!=len(keys)')
                                printe('line to be parsed=')
                                printe(l)
                                printe('keys=')
                                printe(keys)
                        continue
                    for ki, k in enumerate(keys):
                        if k == 'irf' or k == 'kmax':
                            continue
                        else:
                            self[block_name][time].setdefault(k, []).append(ls[ki])
                for k in keys:
                    if k == 'kmax' or k == 'irf':
                        continue
                    try:
                        self[block_name][time][k] = np.array(self[block_name][time][k], dtype=float)
                    except ValueError:
                        self[block_name][time][k] = np.array(
                            [re.sub(r'(\d)([-+])(\d)', r'\1E\2\3', x) for x in self[block_name][time][k]], dtype=float
                        )
            except Exception as _excp:
                printe('Error in parsing %s' % block_name)
                printe('keys=%s' % keys)
                printe(bl)
                raise

        tload = time_.time()
        with open(self.filename, 'r') as f:
            fr = f.read()
        if True:  # define all of the static patterns in a block
            spline_patt = re.compile(r'\s*SUMMARY FOR INPUT SPLINE PROFILE[ ]*(\w+)')
            plasma_shape_patt = re.compile(
                r'\s*plasma shape parameters - MKS units\s*width ={0}'
                'height ={0}h/w ={0}volume ={0}magnetic '
                'axis{0}{0}kappa0 ={0}'.format(r'\s*(%s)\s*' % number_ptrn.pattern)
            )
            onetime_patt = re.compile(
                r'1(time =\s*{0}\s*ms(ec)?,  time point={0}.*?'
                r'equilibrium point =\s*(\d+)\s*equilibrium '
                r'iteration number =\s*(\d+)(\s*equilibrium)?|\s+n\s+ex|\s+coil\s+exp)'.format(r'\s*(%s)\s*' % number_ptrn.pattern),
                flags=re.S,
            )
            flux_patt = re.compile(r'fluxes\s+?(j\s+?r\s+?ion\s+#.*\(anl\).*)', flags=re.S)
            energy_flux_header = (
                'energy fluxes (keV/cm**2-s)\n\n\n NOTE: in this '
                'table conde and condi are calculated\n from models '
                '(i.e., neoc, rlw, etc.) conve and convi\n are '
                'defined as energy flux - cond . The energy\n '
                'flux in turn is given in the previous table \n '
                'and was determined either from models (simulation)\n '
                'or from div flux = source (analysis)\n                            '
                'electron energy                           ion energy\n  j         '
                'r        cond         conv         sum          '
                'cond         conv         omegapi      cvctvrot      sum\n          (cm)'
            )
            pflux_header = (
                'components of particle flux (1/cm**2-s) for ion#  1'
                '\n\n\n    j       r         (1,1)        (1,2)        '
                '(1,3)        (1,4)        (1,5)        (1,6)       '
                'sum\n          (cm)'
            )
            pflux_patt = re.compile(
                pflux_header.replace('(1/cm**2-s)', '.*?')
                .replace(r'(', r'\(')
                .replace(')', r'\)')
                .replace('ion#  1', r'ion#\s*(\d+)\s*')
                .replace('1,', '\\1,'),
                flags=re.S,
            )
            pflux_patt = re.compile(
                'components of particle flux .*? for ion#\\s+(\\d+)\\s*' '\n\n\n(    j       r.*?sum)\n          (cm)', flags=re.S
            )
            pflux_patt = re.compile(r'components of particle flux .*? for ion#\s+(\d+)\s*(.*)', flags=re.S)
            electron_energy_flux_header = 'components of electron energy flux (keV/(cm**2*s) due to conduction'
            ion_energy_flux_header = 'components of ion energy flux (keV/(cm**2*s) due to conduction'
            ohms_law_header = "terms in generalized ohm's law (V/cm)"
            ion_diffusion_header = 'ion diffusion coefficients (cm**2/s)'
            ion_thermal_cond_header = 'ion thermal conductivities (1/cm-s)'
            elec_thermal_cond_header = 'electron thermal conductivities (1/cm-s)'
            trapped_patt = re.compile(
                r'trapped electron fraction, resistivity, ' 'resistive skin time and collision frequencies' '(.*?)(multiplicative.*?)=(.*)',
                flags=re.S,
            )
            particle_source_patt = re.compile(
                r'particle sources .*? for (electrons|'
                r'species # (\d+), name:\s*(\w+)\s+itenp =\s*(\d+)    '
                r'ineut =\s*(\d+).*?sources)(.*?)average(.*?)'
                r'particle balance and confinement time(.*?)average'
                r'(.*?)',
                flags=re.S,
            )
            energy_sources_patt = re.compile(r'(\w+) energy sources .*?  mode =(analysis|simulation)')
            ion_rot_esource_patt = re.compile(r'-+\s*(\w*)\s*ION ENERGY SOURCES DUE TO ANGULAR ROTATION,.*?-+')
            FdayLaw_patt = re.compile('charge balance.*?(analysis|simulation)')
            nbi_patt = re.compile(r'neutral beam injection sources, beam number\s+(\d+)\s+component\s+(\d+)\s*')
            diag_header = 'electron and ion DIAGONAL conductive heat flux w/cm**2'
            transp_coeff_header = 'selected transport coefficients'
            es_dw_header = '----------------------------------------ELECTROSTATIC DRIFT WAVE RELATED QUANTITIES----------------------------------------'
            RL_model_patt = re.compile(r'-+ Rebut-Lallia .*?-+.*?RLW calculations(.*?)confinement times \(s\)', flags=re.S)
            ydebug_header = 'j         r       ydebug(1-8)'
            trot_patt = re.compile(r'-+TOROIDAL ROTATION RESULTS-+.*?sec\s+g/cm(.*?)volume avg\. (.*?)diffusivity', flags=re.S)
            trot_source_patt = re.compile(r'-+TOROIDAL ROTATION SOURCES-+.*?stotal(.*?)volume avg\. (.*?)sprbeame', flags=re.S)
            torque_patt = re.compile(r'-+ TORQUE DENSITIES.*?-+(.*?)vol\..+?:(.+?)spbolt', flags=re.S)
            th_fus_pb_patt = re.compile(
                r'thermal fusion energy balance.*?\)\s+(electrons\s+ions)?(.*?)\s+average\s+(.*?)($|totals)', flags=re.S
            )
            alpha_slow_patt = re.compile(r'alpha particle slowing down data, .*?\)(.*?)vol avg', flags=re.S)
            dt_fus_patt = re.compile(r'THERMAL, BEAM-THERMAL AND TOTAL DT FUSION RATES\s+(.*?)vol intgrtd', flags=re.S)
            dt_fus2_patt = re.compile(
                r'THERMAL, BEAM-THERMAL AND BEAM-BEAM DT FUSION RATES\s+(.*?)Integrated.*?(thermal.*?)($|total)', flags=re.S
            )
            global_patt = re.compile(r'entot\s*=\s*{0}'.format(r'\s*(%s)\s*' % number_ptrn.pattern))
            neut_patt = re.compile(r'Neutral profiles for species((?:\s+\w+\s*=\s*\d+)+)\s*?%s(.*)' % ('\n'), flags=re.S)
            densei_patt = re.compile(r'densities for electrons and ions\s*(.*?)\s*average', flags=re.S)
            densfn_patt = re.compile(r'densities: fast ions, neutrals.*?\)\s*(.*?)average', flags=re.S)
            impdens_patt = re.compile(r'density and charge for impurity element\s+(\w+)\s+(j.*)', flags=re.S)
            temp_B_etc_patt = re.compile(
                r'temperatures, magnetic field, current density, ' r'electric field, safety factor, and ' r'helical flux\s*(.*?)volume',
                flags=re.S,
            )
            bootstrap_patt = re.compile(
                r'bootstrap current from density gradient\s*(.*?)total\s+(.*?)\s*'
                r'bootstrap current from temperature gradient\s*(.*?)total\s+(.*?)\s*',
                flags=re.S,
            )
            neutDD_patt = re.compile(r'Neutrons produced by D-D fusion.*?](.*?)total', flags=re.S)
            dens_temp_patt = re.compile(
                r'densities, temperatures, currents, and ' r'related quantities\s*(.*?)(j    r   r/a      te.*)', flags=re.S
            )
            summary_patt = re.compile(r'Transport analysis summary')
            geometry_check_patt = re.compile(r'geometry check.*?rho max(.*?)fcap\s*gcap(.*?)hcap\s*r2cap(.*?)%', flags=re.S)

        m = re.match(r'^.*?\n\n', fr, flags=re.S)
        self['header'] = fr[m.start() : m.end()]
        fr = fr[: m.start()] + fr[m.end() :]
        fr = fr.replace(self['header'], '')
        if self.debug:
            print('Finding namelist strings')
        nml_str_m = fr[: list(re.finditer(r'&\w*.*?/', fr, flags=re.S))[-1].end()]
        if self.debug:
            print('Removing namelist string')
        fr = fr.replace(nml_str_m, '')
        if self.debug:
            print('Parsing namelist string')
        if self.skip_inone:
            self['inone'] = nml_str_m
        else:
            self['inone'] = NamelistFile(input_string=nml_str_m, outsideOfNamelistIsComment=True)
        if self.debug:
            print('Done with namelist part')
        self['input_splines'] = {}
        m = spline_patt.match(fr)
        while m:
            quant = m.group(1)
            fr = fr[: m.start()] + fr[m.end() :]
            spline_array_patt = re.compile(
                r'\s*PROFILE\s+{2}.+?({0}).+?RHO =\s*(({0}\s+)*)'
                r'VALUES AT KNOTS FOR\s+{2}\s+(({0}\s+)*)BPAR =\s+'
                r'(({0}\s+){1})'.format('(%s)' % number_ptrn.pattern[:-4], '{4}', quant),
                flags=re.S,
            )
            ma = spline_array_patt.match(fr)
            while ma:
                t = str(float(ma.group(1)))
                if t not in self['input_splines']:
                    self['input_splines'][t] = SortedDict()
                self['input_splines'][t][quant + '_rho'] = np.array(list(map(float, ma.group(3).split())))
                self['input_splines'][t][quant] = np.array(list(map(float, ma.group(6).split())))
                fr = fr[: ma.start()] + fr[ma.end() :]
                ma = spline_array_patt.match(fr)
            m = spline_patt.match(fr)
        if self.debug:
            print('Done with splines')
        m = plasma_shape_patt.search(fr)
        self['width'] = float(m.group(1))
        self['height'] = float(m.group(2))
        self['h_over_w'] = float(m.group(3))
        self['volume'] = float(m.group(4))
        self['magnetic_axis'] = np.array(list(map(float, m.group(5, 6))))
        self['kappa0'] = float(m.group(7))
        fr = fr[: m.start()] + fr[m.end() :]

        m1t = onetime_patt.search(fr)
        m1t_next = onetime_patt.search(fr, m1t.end())
        t0 = time_.time()
        if self.debug:
            print('Time to load header, splines, and inone: %g s' % (t0 - tload))
        mtime = 0
        ptime = 0
        self['unparsed'] = []
        while m1t_next:
            t1 = time_.time()
            block = re.sub('(-?NaN)', r' \1 ', fr[m1t.end() : m1t_next.start()].strip())
            if m1t.lastindex is None:
                self['unparsed'].append(block)
                if self.debug:
                    print('Didn\'t parse:')
                    print(block)
                fr = fr[: m1t.start()] + fr[m1t_next.start() :]
            elif m1t.group(1).startswith('time'):
                time = m1t.group(2)
                m = plasma_shape_patt.match(block)
                mpsi = re.search(r'values on psi grid\s*(.*?)values on rho grid', block, flags=re.S)
                mgeo = re.search(r'\s*geometric quantities\s*(.*?)(1     coil|host|> elapsed|$)', block, flags=re.S)
                mflux = flux_patt.search(block)
                indeflux = block.find(energy_flux_header)
                mpflux = pflux_patt.search(block)
                ind_elec_energy_flux = block.find(electron_energy_flux_header)
                ind_ion_energy_flux = block.find(ion_energy_flux_header)
                ind_ohms_law = block.find(ohms_law_header)
                ind_ion_diff = block.find(ion_diffusion_header)
                ind_elec_thermal_cond = block.find(elec_thermal_cond_header)
                ind_ion_thermal_cond = block.find(ion_thermal_cond_header)
                mtrapped = trapped_patt.search(block)
                mpsource = particle_source_patt.search(block)
                mesource = energy_sources_patt.search(block)
                mirotesource = ion_rot_esource_patt.search(block)
                mFdayLaw = FdayLaw_patt.search(block)
                mnbi = nbi_patt.search(block)
                ind_diag = block.find(diag_header)
                ind_tcoeff = block.find(transp_coeff_header)
                ind_es_dw = block.find(es_dw_header)
                mRL = RL_model_patt.search(block)
                ind_ydebug = block.find(ydebug_header)
                mtrot = trot_patt.search(block)
                mtrot_source = trot_source_patt.search(block)
                mtorque = torque_patt.search(block)
                mth_fus_pb = th_fus_pb_patt.search(block)
                malpha_slow = alpha_slow_patt.search(block)
                mdt_fus = dt_fus_patt.search(block)
                mdt_fus2 = dt_fus2_patt.search(block)
                mglobal = global_patt.search(block)
                mneut = neut_patt.search(block)
                mdensei = densei_patt.search(block)
                mdensfn = densfn_patt.search(block)
                mimpdens = impdens_patt.search(block)
                mtemp_B = temp_B_etc_patt.search(block)
                mboot = bootstrap_patt.search(block)
                mneutDD = neutDD_patt.search(block)
                mdens_temp = dens_temp_patt.search(block)
                msummary = summary_patt.search(block)
                mgeo_check = geometry_check_patt.search(block)
                mtime += time_.time() - t1
                t2 = time_.time()
                if mpsi:
                    block_name = 'on_psi_grid'
                    bl = mpsi.group(1).splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    block_name = 'on_rho_grid'
                    bl = block[mpsi.end() :].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mgeo:
                    block_name = 'geometric'
                    bl = mgeo.group(1).splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mflux:
                    keys = [
                        'j',
                        'r',
                        'pflux_ion_1 (1/cm**2-s)',
                        'pflux_ion_2 (1/cm**2-s)',
                        'eflux_e (keV/cm**2-s)',
                        'eflux_i (keV/cm**2-s)',
                        'ang_momentum_flux (g/s**2)',
                    ]
                    block_name = 'fluxes'
                    bl = mflux.group(1).splitlines()
                    keys = bl[0].replace('ion ', 'ion_').split()
                    parse_block(bl[3:], block_name, time, keys=keys)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif indeflux != -1:
                    keys = ['j', 'r', 'conde', 'conve', 'tote', 'condi', 'convi', 'omegapi', 'cvctvrot', 'toti']
                    block_name = 'energy_flux'
                    bl = block[indeflux + len(energy_flux_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=keys)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mpflux:
                    block_name = 'components_of_particle_flux_for_ion_%s' % mpflux.group(1)
                    bl = mpflux.group(2).strip().splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_elec_energy_flux != -1:
                    block_name = 'electron energy_flux components'
                    bl = block[ind_elec_energy_flux + len(electron_energy_flux_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_ion_energy_flux != -1:
                    block_name = 'ion_energy_flux_components'
                    bl = block[ind_ion_energy_flux + len(ion_energy_flux_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_ohms_law != -1:
                    block_name = 'ohms law components'
                    bl = block[ind_ohms_law + len(ohms_law_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_ion_diff != -1:
                    block_name = 'ion_diffusion_coeff'
                    bl = block[ind_ion_diff + len(ion_diffusion_header) :].strip().splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_elec_thermal_cond != -1:
                    block_name = 'electron_thermal_cond'
                    bl = block[ind_elec_thermal_cond + len(elec_thermal_cond_header) :].strip().splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_ion_thermal_cond != -1:
                    block_name = 'ion_thermal_cond'
                    bl = block[ind_ion_thermal_cond + len(ion_thermal_cond_header) :].strip().splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mtrapped:
                    block_name = 'trapped_resistivity_collision'
                    bl = mtrapped.group(1).replace(' -xnus', '-xnus').strip().splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    self[block_name][time][mtrapped.group(2).replace(' ', '_')] = float(mtrapped.group(3))
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mpsource:
                    if mpsource.group(1).startswith('electrons'):
                        ion_num = 'electrons'
                    else:
                        ion_num = 'ion' + mpsource.group(2)
                    block_name = 'particle sources %s' % ion_num
                    bl = block[mpsource.end(1) : block.find('average')].splitlines()[2:]
                    parse_block(bl, block_name, time, keys=None)

                    block_name = 'particle_balance %s' % ion_num
                    bl = mpsource.group(8).splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    if ion_num != 'electrons':
                        block_name = 'momentum_balance %s' % ion_num
                        mmomentum = re.search('momentum balance and confinement time(.*?)average', block, flags=re.S)
                        if mmomentum:
                            bl = mmomentum.group(1).splitlines()
                            parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mesource:
                    block_name = '%s_energy_sources' % (mesource.group(1))
                    eeblock = block[mesource.end() :].replace('int 1.5', 'int_1.5')
                    j_patt = re.compile(r'\bj\b')
                    j1 = j_patt.search(eeblock)
                    j2 = j_patt.search(eeblock, j1.end())
                    j3 = j_patt.search(eeblock, j2.end())
                    j4 = j_patt.search(eeblock, j3.end())
                    mcont = re.search(r'(\bj\b.*?)integrated', eeblock[j2.start() :], flags=re.S)
                    bl = eeblock[j1.start() : j2.start()].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    bl = mcont.group(1).splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    block_name = 'integrated ' + block_name
                    bl = eeblock[j3.start() : j4.start()].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    bl = eeblock[j4.start() :].splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mirotesource:
                    tag = mirotesource.group(1).lower()
                    if tag:
                        tag += '_'
                    block_name = '%sion_rotational_energy_source' % (tag)
                    bl = (
                        block[mirotesource.end() :]
                        .replace('int 1.5', 'int_1.5')
                        .replace('th cx', 'th_cx')
                        .replace('rec +fcx', 'rec_+fcx')
                        .splitlines()
                    )
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mFdayLaw:
                    block_name = 'Faraday_law'
                    bl = block[mFdayLaw.end() :].splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mnbi:
                    beam_num = mnbi.group(1)
                    beam_comp = mnbi.group(2)
                    block_name = 'neutral_beam_%s_comp_%s' % (beam_num, beam_comp)
                    keys = (
                        'j r norm_hot_ion_birthrate norm_hot_ion_deprate cos(avg_pitch_angle)'
                        ' fast_ion_energy_source delayed_energy_source '
                        'frac_energy_electrons frac_energy_ions part_slowing_down_time '
                        'energy_slowing_down_time'.split()
                    )
                    nbi_block_patt = re.compile(r'electrons\s+ions\s+\(s\)\s+\(s\)(.*?)(particle energy)', re.S)
                    mnbi_block = nbi_block_patt.search(block)
                    bl = mnbi_block.group(1).splitlines()
                    parse_block(bl, block_name, time, keys=keys)
                    if beam_comp == '1' and beam_num == '1':
                        beam_tot_name = 'beam_tot'
                        setup_block_nodes(beam_tot_name, time)
                    for l in block[mnbi_block.start(2) :].splitlines():
                        for bi, beam_quant in enumerate(
                            [
                                'particle energy',
                                'neutral beam intensity',
                                'neutral beam power (W) to ap',
                                'fraction stopped by aperture',
                                'fraction incident on wall (shinethrough)',
                                'fraction lost on orbits',
                                'neutral beam power (W) in plasma',
                                'slowed  beam power (W) in plasma',
                                'fraction deposited in electrons',
                                'fraction deposited in ions',
                                'fraction lost by fast ion charge ex',
                            ]
                        ):
                            if beam_quant in l:
                                key = '_'.join(beam_quant.split())
                                ls = l.split()
                                self[block_name][time][key] = float(ls[-1])
                                if mnbi.group(1) == '1' and mnbi.group(2) == '1' and bi > 1:
                                    self[beam_tot_name][time][key] = float(ls[-2])
                        for bi, beam_quant in enumerate(
                            [
                                'passing and axis-circling',
                                'passing and not circling',
                                'trapped and axis-circling',
                                'trapped and not circling',
                                'lost on orbit',
                                'error detected',
                            ]
                        ):
                            if l.strip().startswith(beam_quant):
                                key = '_'.join(beam_quant.split())
                                self[block_name][time][key] = float(l[35:44])
                                if bi < 4:
                                    self[block_name][time][key + '_width'] = float(l.split()[-1])
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_diag != -1:
                    block_name = 'diag_cond_heat_flux'
                    bl = block[ind_diag + len(diag_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_tcoeff != -1:
                    block_name = 'transport coefficients'
                    diag_tcoeff_header = 'diagnostic transport coefficients'
                    ind_diag_tcoeff = block.find(diag_tcoeff_header)
                    bl = block[ind_tcoeff + len(transp_coeff_header) : ind_diag_tcoeff].replace('d -xnus', 'd_-xnus').splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    block_name = 'diagnostic transport coefficients'
                    bl = block[ind_diag_tcoeff + len(diag_tcoeff_header) :].replace('xki/', 'xki/xkineo').splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_es_dw != -1:
                    block_name = 'ES_drift-wave'
                    bl = block[ind_es_dw + len(es_dw_header) :].splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mRL:
                    block_name = 'Rebut-Lallia'
                    bl = mRL.group(1).replace('=', '').replace('rho', 'r').splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    block_name = 'Confinement_times'
                    bl = block[mRL.end() :].splitlines()
                    parse_block(bl, block_name, time, keys=None)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif ind_ydebug != -1:
                    block_name = 'ydebug'
                    ydebug_header2 = 'j         r       ydebug(8-16)'
                    ind_ydebug2 = block.find(ydebug_header2)
                    bl = block[ind_ydebug + len(ydebug_header) : ind_ydebug2].splitlines()
                    keys = ['j', '?', 'r'] + ['ydebug(%d)' % i for i in range(1, 9)]
                    parse_block(bl, block_name, time, keys=keys, ignore_length_mismatch=True)
                    block_name = 'ydebug2'
                    bl = block[ind_ydebug2 + len(ydebug_header2) :].splitlines()
                    keys = ['j', '?', 'r'] + ['ydebug(%d)' % i for i in range(9, 17)]
                    parse_block(bl, block_name, time, keys=keys, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mtrot:
                    block_name = 'toroidal_rotation'
                    bl = mtrot.group(1).splitlines()
                    keys = (
                        'j r omega_(ang_speed) d(omega)/dt angmtm_density d(angmtm)/dt '
                        'vionz_(ion_speed) flux total_ang._momtm_diffusivity '
                        'local_ang._momtm_conf._time momt_inrta_density'
                    ).split()
                    parse_block(bl, block_name, time, keys=keys, ignore_length_mismatch=True)
                    block_name = 'global_toroidal_rotation'
                    time = setup_block_nodes(block_name, time)
                    for k, v in zip(keys[2:], mtrot.group(2).split()):
                        self[block_name][time][k] = float(v)
                    for l in block[mtrot.end(2) :].splitlines():
                        for patt in ['stored ang. mtm.', 'global ang. mtm. conf. time,sec', 'total momt. of inertia,kg*m**2']:
                            if patt in l:
                                self[block_name][time][patt.replace(' ', '_')] = float(l.split()[-1])
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mtrot_source:
                    block_name = 'toroidal_rotation_sources'
                    bl = mtrot_source.group(1).splitlines()
                    keys = 'j      r      sprbeame    sprbeami    ssprcxl     sprcxre     spreimpt     sprcx       spr2d       stotal rot_energy'.split()
                    parse_block(bl, block_name, time, keys=keys)
                    for k, v in zip(keys[2:], mtrot_source.group(2).split()):
                        self[block_name][time]['volume_avg_%s' % k] = float(v)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mtorque:
                    block_name = 'torques'
                    bl = mtorque.group(1).strip().splitlines()
                    keys = bl[0].replace('r(j)', 'r').split()
                    parse_block(bl[1:], block_name, time, keys=keys)
                    for k, v in zip(keys[2:], mtorque.group(2).split()):
                        self[block_name][time]['volume_avg_%s' % k] = float(v)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mth_fus_pb:
                    block_name = 'thermal_fusion_power_balance'
                    bl = mth_fus_pb.group(2).strip().splitlines()
                    keys = bl[0].split()
                    parse_block(bl[1:], block_name, time, keys=keys)
                    for k, v in zip(keys[2:], mth_fus_pb.group(3).split()):
                        self[block_name][time]['volume_avg_%s' % k] = float(v)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif malpha_slow:
                    block_name = 'alpha_slowing'
                    bl = malpha_slow.group(1).strip().splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mdt_fus or mdt_fus2:
                    if mdt_fus2:
                        mdt_fus = mdt_fus2
                    block_name = 'dt_fusion'
                    bl = mdt_fus.group(1).strip().splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    if mdt_fus2:
                        block_name = 'rates'
                        time = setup_block_nodes(block_name, time)
                        for l in mdt_fus2.group(2).strip().splitlines():
                            if len(l.strip()) == 0:
                                continue
                            m = re.search(r'(\w+[-_]\w+)\s+(.*?)rate per second:?\s+(.*)', l)
                            self[block_name][time].setdefault(m.group(2).strip(), SortedDict())
                            self[block_name][time][m.group(2).strip()][m.group(1)] = float(m.group(3))
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif len(block) == 0:
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mglobal:
                    block_name = 'global'
                    time = setup_block_nodes(block_name, time)
                    bl = block.splitlines()
                    for q in [
                        'entot',
                        'dentot',
                        'stot',
                        'taup',
                        'eetot',
                        'deetot',
                        'qetot',
                        'tauee',
                        'etot',
                        'detot',
                        'qtot',
                        'taue',
                        'volume',
                        'entaue',
                        'surface area .*?',
                        'ec',
                        'dec',
                        'qcen',
                        'tauec',
                        r'angmtot.*?\)',
                        r'dangmtot/dt.*?\)',
                        r'storquet.*?\)',
                        r'tauang.*?\)',
                    ]:
                        p = re.compile(r'(\b{1})\s*=\s*({0})'.format(r'\s*(%s)\s*' % number_ptrn.pattern, q))
                        m = p.search(block)
                        if m:
                            self[block_name][time][m.group(1).strip()] = float(m.group(2))
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mneut:
                    block_name = 'neutrals_%s' % mneut.group(1)
                    bl = mneut.group(2).strip().splitlines()
                    keys = bl[0].split()[:-1] + ['vz2']
                    parse_block(bl[1:], block_name, time, keys=keys, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mdensei:
                    block_name = 'ei_densities'
                    bl = re.sub(r'\b\s+ions', '_ions', mdensei.group(1).strip()).splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    # ignore entotn, enitn, snaddt; averages
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mdensfn:
                    block_name = 'fast_neut_densities'
                    bl = re.sub(r'([^s])\s+neut', r'\1_neut', mdensfn.group(1).strip()).splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mimpdens:
                    block_name = 'impurity_%s' % (mimpdens.group(1))
                    bl = mimpdens.group(2).splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mtemp_B:
                    block_name = 'misc profiles'
                    bl = mtemp_B.group(1).strip().splitlines()
                    keys = bl[0].split()
                    if len(bl[2].split()) == len(keys) - 1:
                        keys = keys[:-1]
                    parse_block(bl[2:], block_name, time, keys=keys, ignore_length_mismatch=False)
                    curr_patt = re.compile(r'current densities .*? and total currents \(a\).*?\)(.*?)total\s+(.*?)(totcur)', flags=re.S)
                    mcurr = curr_patt.search(block)
                    if mcurr:
                        block_name = 'current_densities'
                        bl = mcurr.group(1).strip().splitlines()
                        keys = bl[0].split()
                        parse_block(bl[1:], block_name, time, keys=keys)
                        for k, v in zip(keys[2:-1], mcurr.group(2).split()):
                            self[block_name][time]['total_' + k] = float(v)
                    block_name = 'beta_misc'
                    time = setup_block_nodes(block_name, time)
                    for q in [
                        'totcur',
                        'voltag',
                        'betae',
                        'betae0',
                        'betai',
                        'betai0',
                        'betab',
                        'betab0',
                        'betaa',
                        'betaa0',
                        'beta',
                        'beta0',
                        'betap',
                        'li',
                    ]:
                        p = re.compile(r'(\b{1})\s*=\s*({0})'.format(r'\s*(%s)\s*' % (number_ptrn.pattern), q))
                        m = p.search(block[mcurr.end(2) if mcurr else 0 :])
                        if m:
                            self[block_name][time][m.group(1).strip()] = float(m.group(2))
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mboot:
                    for gi, grad in enumerate(['density_gradient', 'temperature_gradient']):
                        block_name = 'bootstrap_current_from_%s' % grad
                        bl = mboot.group(gi * 2 + 1).strip().splitlines()
                        keys = re.sub(r'([^s])\s+ions', r'\1_ions', bl[0]).split()
                        parse_block(bl[1:], block_name, time, keys=keys, ignore_length_mismatch=True)
                        for k, v in zip(keys[2:], mboot.group(gi * 2 + 2).strip().split()):
                            self[block_name][time]['total_' + k] = float(v)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mneutDD:
                    block_name = 'neutrons_from_DD'
                    bl = mneutDD.group(1).strip().splitlines()
                    keys = (
                        bl[0].replace('D-beam neutrons', 'D-beam_neutrons').replace('D-D neutrons', 'D-D_neutrons')
                        + ' beam_thermal_neutrons beam_thermal_protons'
                    ).split()
                    parse_block(bl[1:], block_name, time, keys=keys, ignore_length_mismatch=True)
                    for l in block[mneutDD.end(1) :].splitlines():
                        if l.strip() == '':
                            continue
                        k, v = l.split(':')
                        self[block_name][time][k.strip().replace(' ', '_')] = float(v.split()[0])
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif mdens_temp:
                    block_name = 'densities'
                    bl = mdens_temp.group(1).strip().splitlines()
                    keys = re.sub(r'([^s])\s+neuts', r'\1_neuts', re.sub(r'([^s])\s+ions', r'\1_ions', bl[0])).split()
                    parse_block(bl[1:], block_name, time, keys=keys, ignore_length_mismatch=True)
                    block_name = 'temps'
                    bl = mdens_temp.group(2).strip().splitlines()
                    parse_block(bl, block_name, time, keys=None, ignore_length_mismatch=True)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif msummary:
                    block_name = 'summary'
                    time = setup_block_nodes(block_name, time)
                    summ_block = block
                    for k in [
                        'Minor radius a (cm):',
                        'b/a:',
                        'Nominal Rmajor (cm):',
                        'R at geom. cent. (cm):',
                        'R at mag. axis (cm):',
                        'Z at mag. axis (cm):',
                        'Volume (cm**3):',
                        'Pol. circum. (cm):',
                        'surface area (cm**2):',
                        'cross. sect area   :',
                        'Bt (G):',
                        'Ip  (A):',
                        'Bt at Rgeom (G):',
                        'r(q = 1)/a:',
                        'Line-avg den (1/cm**3):',
                        'Tau-particle-d  (s):',
                        'Beam power elec. (W):',
                        'ke at a/2. (1/cm-s):',
                        'Beam power ions  (W):',
                        'ki at a/2. (1/cm-s):',
                        'Beam power cx loss (W):',
                        'ki/kineo at a/2.:',
                        'Shinethrough (%):',
                        'chi electrons at a/2.:',
                        'RF power absorbed:',
                        'chi ions at a/2.:',
                        'Radiated power   (W):',
                        'r*/a: Te = (Te(0)+Te(a))/2.',
                        'Brems prim ions  (W):',
                        'Brems imp ions :',
                        'Poloidal B field (G):',
                        'Beta-poloidal:',
                        'beam torque (nt-m)',
                        'total torque (nt-m):',
                        'stored ang mtm (kg*m2/s):',
                        'momt inertia (kg*m**2):',
                        'kinetic energy of rotation (j) :',
                        'Normalized beta',
                        'total power input (W) =',
                        'time =',
                        'Itot =',
                        'total power input (MW) =',
                        'totfwpe:',
                        'totfwpi:',
                        'Iohm =',
                        'Iboot =',
                        'Ibeam =',
                        'Irf =',
                        'QDD =',
                        'QDT =',
                        'QTT =',
                        'QHe3d =',
                        'P DD  =',
                        'P DT =',
                        'P TT =',
                        'P He3d',
                        'D(D,n) =',
                        'D(T,n) =',
                        'T(T,2n) =',
                        'He3(D,p)He4 =',
                        'paux (MW) =',
                        'palpha =',
                        'prad =',
                        'Ptransport =',
                        'H(89p) =',
                        'H(89pm) =',
                        'H_ITER98y2 =',
                        'H_Petty =',
                        'angular momentum confinement time (sec)',
                    ]:
                        key = k.strip('=: ')
                        ind = summ_block.find(k)
                        if ind == -1:
                            if self.debug and k != 'total power input (MW) =':
                                printe('Warning: %s not found in transport summary' % key)
                            continue
                        if key == 'total power input (MW)':  # this was a mistake in early outone files
                            key = 'total power input (W)'
                        if key in self[block_name][time]:
                            printe('Warning: %s already exists in transport summary' % key)
                        mval = re.match(r'(\s*%s)' % number_ptrn.pattern, summ_block[ind + len(k) :])
                        if mval:
                            if self.debug:
                                printi('Processing summary key %s' % key)
                            self[block_name][time][key] = float(mval.group(1))
                            summ_block = summ_block[:ind] + summ_block[ind + len(k) + mval.end(1) :]
                        else:
                            printe('Non-number encountered for value of %s' % key)
                    mrf_summ = re.search('(cd,amps.*?)QDD', block, flags=re.S)
                    if not mrf_summ:
                        if self.debug:
                            print('Warning: RF block not found in summary')
                    else:
                        bl = mrf_summ.group(1).replace(' ,', ',').replace(', ', ',').splitlines()
                        keys = ['rf_' + k for k in bl[0].split()]
                        for k in keys:
                            self[block_name][time][k] = SortedDict()
                        for num, l in enumerate(bl[1:], 1):
                            ls = l.split()
                            if len(ls) == 0:
                                continue
                            for ki, k in enumerate(keys, 1):
                                self[block_name][time][k]['_'.join([ls[0], str(num)])] = float(ls[ki])
                        summ_block = summ_block.replace(mrf_summ.group(1), '')
                    mbeta_summ = re.search(r'(Beta-toroidal\s+volume-avg.*?)(Normalized|total power input)', block, flags=re.S)
                    if not mbeta_summ:
                        printe('Warning: Beta-toroidal block not found in transport summary')
                    else:
                        bl = mbeta_summ.group(1).strip().splitlines()
                        keys = ['beta_toroidal_' + l for l in bl[0].split()[1:]]
                        for k in keys:
                            self[block_name][time][k] = SortedDict()
                        for l in bl[1:]:
                            ls = l.split()
                            if len(ls) == 0:
                                continue
                            for ki, k in enumerate(keys, 1):
                                self[block_name][time][k][ls[0]] = float(ls[ki])
                        summ_block = summ_block.replace(mbeta_summ.group(1), '')
                    mPB = re.search(r'(electrons\s+ions\s+thermal\s+total.*?)H\(89p\)', block, flags=re.S)
                    if not mPB:
                        printe('Warning: Stored energy block not found in transport summary')
                    else:
                        bl = mPB.group(1).splitlines()
                        keys = bl[0].split()
                        for l in bl[1:]:
                            label = l[:24].strip()
                            if label == '':
                                continue
                            self[block_name][time][label] = SortedDict()
                            for ki, k in enumerate(keys):
                                val = l[24 + ki * 12 : 24 + (ki + 1) * 12].strip()
                                if val != '':
                                    try:
                                        self[block_name][time][label][k] = float(val)
                                    except Exception:
                                        print('Failed to parse %s %s %s %s = %s' % (block_name, time, label, k, val))
                        summ_block = summ_block.replace(mPB.group(1), '')
                    mexp_code = re.search(r'(exper\.\s+code.*?)computed quantities', block, flags=re.S)
                    if not mexp_code:
                        printe('Warning: Exp-code comparison block not found in transport summary')
                    else:
                        bl = mexp_code.group(1).splitlines()
                        keys = bl[0].split()
                        bn2 = 'exp_code comparison'
                        self[block_name][time][bn2] = SortedDict()
                        for l in bl[1:]:
                            if l.strip() == '':
                                continue
                            label, data = l.split(':')
                            ds = data.split()
                            for ki, k in enumerate(keys):
                                self[block_name][time][bn2][label.strip() + '_' + k] = float(ds[ki].replace('******', 'NaN'))
                        summ_block = summ_block.replace(mexp_code.group(1), '')
                    mprof_summ = re.search(r'(profiles\s+ucenter.*?)\s+exper', block, flags=re.S)
                    if not mprof_summ:
                        printe('Warning: profiles block not found in transport summary')
                    else:
                        bl = mprof_summ.group(1).splitlines()
                        keys = bl[0].split()[1:]
                        bn2 = 'profiles'
                        self[block_name][time][bn2] = SortedDict()
                        for l in bl[1:]:
                            label = l[:24].strip()
                            dest = self[block_name][time][bn2][label] = SortedDict()
                            for ki, k in enumerate(keys):
                                val = l[24 + ki * 12 : 24 + (ki + 1) * 12].strip()
                                if len(val):
                                    dest[k] = float(val)
                        summ_block = summ_block.replace(mprof_summ.group(1), '')
                    # if self.debug:
                    # print(summ_block)
                    self[block_name][time]['unparsed'] = '\n'.join([x for x in summ_block.splitlines() if x.strip() != ''])
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                elif m:
                    block_name = 'global_params'
                    time = setup_block_nodes(block_name, time)
                    self[block_name][time]['width'] = float(m.group(1))
                    self[block_name][time]['height'] = float(m.group(2))
                    self[block_name][time]['h/w'] = float(m.group(3))
                    self[block_name][time]['volume'] = float(m.group(4))
                    self[block_name][time]['magnetic axis'] = np.array(list(map(float, m.group(5, 6))))
                    self[block_name][time]['kappa0'] = float(m.group(7))
                    fr = fr.replace(m.group(0), '').strip()
                elif mgeo_check:
                    for bi, base in enumerate(['rhomax', 'fcap_gcap', 'hcap_r2cap'], 1):
                        block_name = 'geo_check' + base
                        bl = mgeo_check.group(bi).strip().splitlines()
                        kb = ['_' + k for k in 'old   pred  new   logdt  rel_err'.split()]
                        bn = base.split('_')
                        if len(bn) == 1:
                            keys = [bn[0] + k for k in kb]
                        elif len(bn) == 2:
                            keys = ['j'] + [bn[0] + k for k in kb] + [bn[1] + k for k in kb]
                        parse_block(bl[1:], block_name, time, keys=keys)
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                else:
                    self['unparsed'].append(block)
                    print('Warning: Not parsing the block with the following first 300 chars:')
                    print(block[:300])
                    fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                    # break
            elif m1t.group(1).strip().startswith('coil'):
                if self.debug:
                    print('Starting coil')
                coil_patt = re.compile(r'--+\s*(.*?)sum\s+red\.\s+xchisq ={0}'.format(r'\s*(%s)\s*' % number_ptrn.pattern), flags=re.S)
                mcoil = coil_patt.search(block)
                diag = 'coil'
                keys = ['number', 'exp_current (A)', 'calc_current (A)', 'red_chi_sq']
                bl = mcoil.group(1).splitlines()
                parse_block(bl, diag, time, keys=keys)
                self[diag][time]['total_reduced_chisq'] = float(mcoil.group(2))
                mcoil = coil_patt.search(block, mcoil.end())
                diag = 'psi_loop'
                keys = ['number', 'exp (V-s)', 'calc_(V-s)', 'red_chi_sq']
                bl = mcoil.group(1).splitlines()
                parse_block(bl, diag, time, keys=keys)
                self[diag][time]['total_reduced_chisq'] = float(mcoil.group(2))
                mcoil = coil_patt.search(block, mcoil.end())
                diag = 'mag_probe'
                keys = ['number', 'exp (T)', 'calc_(T)', 'red_chi_sq']
                bl = mcoil.group(1).splitlines()
                parse_block(bl, diag, time, keys=keys)
                self[diag][time]['total_reduced_chisq'] = float(mcoil.group(2))
                fr = fr[: m1t.start()] + fr[m1t_next.start() :]
                if self.debug:
                    print('Done with coil')
            elif m1t.group(1).strip().startswith('n'):
                block_name = 'time_steps'
                m_time_block = re.search('(\n\\s*[a-zA-Z*]+|$)', block)
                bl = ('n ex' + block[: m_time_block.start(1)]).replace('. ', '._').splitlines()
                parse_block(bl, block_name, time)
                fr = fr[: m1t.start()] + fr[m1t_next.start() :]
            else:
                self['unparsed'].append(block)
                print('Didn\'t parse:')
                print(block)
                fr = fr[: m1t.start()] + fr[m1t_next.start() :]
            ptime += time_.time() - t2
            m1t = onetime_patt.search(fr)
            if m1t is None:
                m1t = re.search('^', fr)
            m1t_next = onetime_patt.search(fr, m1t.end())
            if m1t_next is None:
                m1t_next = re.search('$', fr)
            if len(fr.strip()) == 0:
                break
        if self.debug:
            print('Time to figure out blocks: %g s' % mtime)
            print('Time to parse blocks: %g s' % ptime)
            print('Time to run load: %g s' % (time_.time() - tload))
        if fr.strip() != '':
            self['unparsed'].append(fr)
            if self.debug:
                print(fr[:300])
        self.combine_times()

    def combine_times(self):
        """
        In the course of parsing, there could be duplicate times for some quantities
        These can be combined into a single time
        """
        import time as time_

        if self.debug:
            print('Starting to combine_times')
            tcombine = time_.time()
        for k, v in list(self.items()):
            if not isinstance(v, SortedDict):
                continue
            times = list(v.keys())
            tref = times[0]
            delt = []
            for t in times[1:]:
                if t.startswith(tref):
                    delq = []
                    for q, qv in list(v[t].items()):
                        if q in v[tref]:
                            if np.array(v[tref][q] == v[t][q]).all():
                                delq.append(q)
                            else:
                                if self.debug:
                                    print(k, '%s %s != %s %s' % (tref, q, t, q))
                        else:
                            v[tref][q] = v[t][q]
                            delq.append(q)
                    for q in delq:
                        del v[t][q]
                    if len(v[t]) == 0:
                        delt.append(t)
                else:
                    tref = t
            for t in delt:
                del v[t]
        if self.debug:
            print('Finished combine_times in %s sec' % (time_.time() - tcombine))

    def convert_outone_to_nc(self):
        """
        Convert self to a netCDF format file, which is returned from this function
        """
        nc = OMFITnc('', format='NETCDF3_CLASSIC')  # this will generate an empty unique filename in the OMFITcwd directory
        unparsed_keys = list(self.keys())

        for k in ['on_psi_grid', 'on_rho_grid', 'geometric', 'coil', 'psi_loop', 'mag_probe']:
            if self.debug:
                printe('Warning: Skipping conversion of %s to netcdf' % k)
            if k in unparsed_keys:
                unparsed_keys.remove(k)

        nc['header'] = self['header']
        unparsed_keys.remove('header')
        # nc['inone'] = self['inone']
        unparsed_keys.remove('inone')
        if 'unparsed' in unparsed_keys:
            unparsed_keys.remove('unparsed')
        time_grids = SortedDict()
        rho_grids = SortedDict()
        for k, v in list(self.items()):
            if k not in unparsed_keys:
                continue
            if is_float(v) or k == 'magnetic_axis':
                nc[k] = OMFITncData(v)
                unparsed_keys.remove(k)
                continue
            if isinstance(v, SortedDict):
                times = list(map(float, list(v.keys())))
                match_t = False
                for kt, vt in list(time_grids.items()):
                    if isinstance(vt, list) and vt == times:
                        time_grids[re.sub(r'\W', '_', k)] = kt
                        match_t = True
                        break
                if not match_t:
                    time_grids[re.sub(r'\W', '_', k)] = times
                match_g = False
                for t in list(v.keys()):
                    if 'r' in v[t]:
                        for kr, vr in list(rho_grids.items()):
                            if isinstance(vr, np.ndarray) and (len(vr) == len(v[t]['r'])) and (vr == v[t]['r']).all():
                                rho_grids[re.sub(r'\W', '_', '%s_%s' % (k, t))] = kr
                                match_g = True
                                break
                        if not match_g:
                            rho_grids[re.sub(r'\W', '_', '%s_%s' % (k, t))] = v[t]['r']
        for k, v in list(time_grids.items()):
            if isinstance(v, str):
                continue
            tvar = 't_' + re.sub(r'\W', '_', k)
            nc['__dimensions__'][tvar] = len(v)
            nc[tvar] = OMFITncData(np.array(v), dimension=(tvar,))
            nc[tvar]['units'] = 'msec'
        for k, v in list(rho_grids.items()):
            if isinstance(v, str):
                continue
            rvar = 'r_' + re.sub(r'\W', '_', k)
            nc['__dimensions__'][rvar] = len(v)
            nc[rvar] = OMFITncData(v, dimension=(rvar,))
            nc[rvar]['units'] = 'cm'
        for k, v in list(self.items()):
            if k not in unparsed_keys:
                continue
            if 'geo_check' in k:
                continue
            if not hasattr(v, 'keys'):
                if self.debug:
                    raise ValueError('%s\'s values have no keys' % k)
                continue
            t0 = list(v.keys())[0]
            k0 = list(v[t0].keys())
            rdim = False
            if 'r' in k0:
                for tk in list(v.keys()):
                    rdimk = re.sub(r'\W', '_', '%s_%s' % (k, tk))
                    if rdimk in rho_grids:
                        if isinstance(rho_grids[rdimk], str):
                            rdimk = rho_grids[rdimk]
                        rdim = True
                        break
            tdimk = re.sub(r'\W', '_', k)
            if tdimk not in time_grids:
                if self.debug:
                    print(tdimk, 'not in time_grids')
                continue
            if isinstance(time_grids[tdimk], str):
                tdimk = time_grids[tdimk]
            for key in k0:
                if key == 'j' or key == '?' or key == 'unparsed' or key == 'magnetic axis' or key.startswith('chiimatdm'):
                    if self.debug and key not in ['j', 'r']:
                        print('Skipping %s' % key)
                    continue
                val = np.array(self[k].across("['.*']['%s']" % key))
                if str(val.dtype) == 'object':
                    if self.debug:
                        print('Not yet parsing non-numerical types:', k, key)
                    continue
                try:
                    if val.min() == val.max() == 0:
                        if self.debug:
                            print('Skipping conversion of %s, becuase it is all zeros' % key)
                        continue
                except Exception:
                    print('Problem evaluating 0-ness of ', key)
                units = ''
                for unit in ['(1/cm**2-s)', '(keV/cm**2-s)', '(g/s**2)']:
                    if unit in key:
                        key = key.replace(unit, '')
                        units = unit
                        break
                if key.startswith('1.5'):
                    key = key.replace('1.5', 'three_halves')
                key = re.sub(r'\W', '_', key.strip())
                key = '%s_%s' % (re.sub(r'\W', '_', k.strip()), key)
                if rdim and nc['__dimensions__']['r_%s' % rdimk] in val.shape:
                    nc[key] = OMFITncData(val, dimension=('t_%s' % tdimk, 'r_%s' % rdimk))
                else:
                    nc[key] = OMFITncData(val, dimension=('t_%s' % tdimk,))
                nc[key]['units'] = units
                if self.debug:
                    print(key + ' added to ncfile')
            unparsed_keys.remove(k)
        if self.debug:
            print('Need to convert %s to netcdf' % unparsed_keys)
        return nc

    @dynaSave
    def save(self):
        if os.path.splitext(self.filename)[1] in ['.nc', '.cdf']:
            tmp_name = self.filename
            if self.dynaLoad:
                self.filename = self.link
            try:
                tmp = None
                tmp = self.convert_outone_to_nc()
                tmp.saveas(self.filename)
            finally:
                self.filename = tmp_name
            return tmp
        else:
            return OMFITascii.save(self)


class OMFITstatefile(OMFITnc):
    """
    Class for handling the netcdf statefile from ONETWO,
    with streamlining for plotting and summing heating terms
    """

    volumetric_electron_heating_terms = SortedDict(
        list(
            zip(
                ['qohm', 'qdelt', 'qrad', 'qione', 'qbeame', 'qrfe', 'qfuse'],
                [[1, 7], [-1, 11], [-1, 10], [-1, 602], [1, 2], [1, 3], [1, 6]],  # [sign, index_id]
            )
        )
    )
    volumetric_ion_heating_terms = SortedDict(
        list(zip(['qdelt', 'qioni', 'qcx', 'qbeami', 'qrfi', 'qfusi'], [[1, 11], [1, 602], [-1, 305], [1, 2], [1, 5], [1, 6]]))
    )
    volumetric_electron_particles_terms = SortedDict(
        list(
            zip(
                ['sion_thermal_e', 'sbeame', 'srecom_e', 'sion_imp_e', 's2d_e', 'ssaw_e', 'spellet'],
                [[1, 601], [1, 2], [1, 602], [1, 0], [1, 0], [1, 0], [1, 14]],
            )
        )
    )
    volumetric_momentum_terms = SortedDict(list(zip(['storqueb'], [[1, 1]])))  # this is the total rather than individual components

    def __init__(self, filename, verbose=False, persistent=False, **kw):
        """
        :param filename: The location on disk of the statefile

        :param verbose: Turn on printing of debugging messages for this object

        :param persistent: Upon loading, this class converts some variables from the
            psi grid to the rho grid, but it only saves these variables back to the
            statefile if persistent is True, which is slower
        """
        OMFITnc.__init__(self, filename, **kw)
        # For backward compatibility we must check if this statefile
        # comes from a version of ONETWO which had the 'qdelt' sign wrong
        if True:
            tmp = OMFITnc(filename)
            if 'V5.8' in tmp['_globals']['title']:
                self.volumetric_electron_heating_terms['qdelt'][0] = -1
                self.volumetric_ion_heating_terms['qdelt'][0] = -1
            del tmp
        self.verbose = verbose
        self.persistent = persistent

    @dynaLoad
    def load(self):
        """
        Load the variable names, and convert variables on the
        psi grid to the rho grid
        """
        OMFITnc.load(self)
        new_val = self['rho_grid']['data'] / max(self['rho_grid']['data'])
        dimensions = self['rho_grid']['__dimensions__']
        dtype = self['rho_grid']['__dtype__']
        if self.persistent:
            self['rhon_grid'] = OMFITncData(variable=new_val, dimension=dimensions, dtype=dtype)
        else:
            self['rhon_grid'] = OMFITncDataTmp(variable=new_val, dimension=dimensions, dtype=dtype)
        self['rhon_grid']['long_name'] = '* normalized rho grid'

        self.interp_npsi_vars_to_rho(verbose=self.verbose)

    def interp_npsi_vars_to_rho(self, verbose=False):
        """
        Some variables are only defined on the psi grid.
        Iterpolate these onto the rho grid.
        """
        npsi_vars = []
        for k, v in list(self.items()):
            if k == 'rho_mhd_gridnpsi':
                continue
            if '__dimensions__' not in v:
                continue
            if 'dim_npsi' in v['__dimensions__']:
                npsi_vars.append(k)
        if verbose:
            print('Interpolating the following variables to the rho grid')
            print(npsi_vars)
        rho = self['rho_grid']['data']
        rho_mhd = self['rho_mhd_gridnpsi']['data'][-1::-1]
        for k in npsi_vars:
            new_key = k.replace('npsi', 'nrho')
            if new_key in self:
                if verbose:
                    print('Skipping recalculation of %s' % (new_key,))
                continue
            v = self[k]
            if len(v['__dimensions__']) > 1:
                if verbose:
                    print('%s not interpolated because it has more than 1 dimension' % k)
                continue
            val = v['data'][-1::-1]
            interp = interpolate.interp1d(rho_mhd, val, kind='linear')
            new_val = interp(rho)  # ,rho_mhd,val)

            try:
                long_name = v['long_name'].replace('npsi', 'nrho')
            except KeyError:
                long_name = ''
            try:
                units = v['units']
            except KeyError:
                units = ''
            dtype = v['__dtype__']
            dimensions = ('dim_rho',)
            if k == 'rminavnpsi':
                neg_inds = new_val < 0
                new_val[neg_inds] = 0
            if self.persistent:
                self[new_key] = OMFITncData(variable=new_val, dimension=dimensions, dtype=dtype)
            else:
                self[new_key] = OMFITncDataTmp(variable=new_val, dimension=dimensions, dtype=dtype)
            self[new_key]['units'] = units
            self[new_key]['long_name'] = long_name
        return

    def volume_integral(self, v):
        """
        Volume integrate v up to flux surface rho::

         /rho                      /rho
         |    v dV  =>  4 pi^2 R_0 |      v hcap rho' drho'
         /0                        /0

        :param v: can be a variable string (key of variable dictionary) or an array on the rho grid
        """
        rho = self['rho_grid']['data']
        hcap = self['hcap']['data']
        R0 = self['rmajor']['data']
        if isinstance(v, str):
            integrand = 4 * np.pi ** 2 * R0 * rho * hcap * self[v]['data']
        else:
            integrand = 4 * np.pi ** 2 * R0 * rho * hcap * v
        return integrate.cumtrapz(integrand, rho, initial=0)

    def surface_integral(self, v):
        """
        Surface integrate v up to flux surface rho::

         /rho                /rho
         |    v dS  =>  2 pi |      v hcap rho' drho'
         /0                  /0

        :param v: can be a variable string (key of variable dictionary) or an array on the rho grid
        """
        rho = self['rho_grid']['data']
        hcap = self['hcap']['data']
        if isinstance(v, str):
            integrand = 2 * np.pi * rho * hcap * self[v]['data']
        else:
            integrand = 2 * np.pi * rho * hcap * v
        return np.array([0] + list(integrate.cumtrapz(integrand, rho, initial=0)))

    def plot(self, plotChoice=0):
        if plotChoice == 0 or str(plotChoice).lower() == 'summary':
            return self.plotSummary()
        elif plotChoice == 1 or str(plotChoice).lower() == 'volumetricheating':
            return self.plotVolumetricHeating()
        elif plotChoice == 2 or str(plotChoice).lower() == 'powerflows':
            return self.plotPowerFlows()
        elif plotChoice == 3 or str(plotChoice).lower() == 'transp':
            return self.plotTransp()

    def plotPowerFlows(self):
        # Created by smithsp at 2013/07/18 15:37

        suptitle('Power flow')

        rho = self['rho_grid']['data'][:]
        rho = rho / max(rho)

        ax = pyplot.subplot(2, 1, 1)
        pyplot.title('Electrons')
        Pe = 0
        for v, (sign, id_index) in self.volumetric_electron_heating_terms.items():
            if max(abs(self[v]['data'])) == 0:
                continue
            pyplot.plot(rho, sign * self.volume_integral(v) / 1e6, label=v.replace('q', 'P'))
            print('Total electron power %s: %3.3g MW' % (v[1:], sign * self.volume_integral(v)[-1] / 1e6))
            Pe = Pe + sign * self.volume_integral(v) / 1e6
        pyplot.plot(rho, Pe, '--k', label='Pe_tot')
        legend(loc='best').draggable(True)
        pyplot.ylabel('$[MW]$')

        ax2 = pyplot.subplot(2, 1, 2, sharex=ax, sharey=ax)
        pyplot.title('Ions')
        Pi = 0
        for v, (sign, id_index) in self.volumetric_ion_heating_terms.items():
            if max(abs(self[v]['data'])) == 0:
                continue
            pyplot.plot(rho, sign * self.volume_integral(v) / 1e6, label=v.replace('q', 'P'))
            print('Total ion power %s: %3.3g MW' % (v[1:], sign * self.volume_integral(v)[-1] / 1e6))
            Pi = Pi + sign * self.volume_integral(v) / 1e6
        pyplot.plot(rho, Pi, '--k', label='Pi_tot')
        legend(loc='best').draggable(True)
        pyplot.ylabel('$[MW]$')

        pyplot.xlabel('$\\rho$')

    def plotVolumetricHeating(self):
        # Created by smithsp at 2013/07/18 15:12

        suptitle('Volumetric heating')

        rho = self['rho_grid']['data'][:]
        rho = rho / max(rho)

        ax = pyplot.subplot(2, 1, 1)
        pyplot.title('Electrons')
        Pe = 0
        for v, (sign, id_index) in self.volumetric_electron_heating_terms.items():
            if max(abs(self[v]['data'])) == 0:
                continue
            pyplot.plot(rho, sign * self[v]['data'][:] / 1e6, label=v)
            Pe = Pe + sign * self[v]['data'][:] / 1e6
        pyplot.plot(rho, Pe, '--k', label='qe_tot')
        legend(loc='best').draggable(True)
        pyplot.ylabel('$[MW/m^3]$')

        ax2 = pyplot.subplot(2, 1, 2, sharex=ax, sharey=ax)
        pyplot.title('Ions')
        Pi = 0
        for v, (sign, id_index) in self.volumetric_ion_heating_terms.items():
            if max(abs(self[v]['data'])) == 0:
                continue
            pyplot.plot(rho, sign * self[v]['data'][:] / 1e6, label=v)
            Pi = Pi + sign * self[v]['data'][:] / 1e6
        pyplot.plot(rho, Pi, '--k', label='qi_tot')
        legend(loc='best').draggable(True)
        pyplot.ylabel('$[MW/m^3]$')

        pyplot.xlabel('$\\rho$')

    def get_power_flows(self):
        """
        :return: Dictionary having non-zero power flow terms, including the total;
            keys of the dictionary end in ``e`` or ``i`` to indicate electron or ion
            heating; units are MW
        """
        result = SortedDict()
        Pe = 0
        for v, (sign, id_index) in self.volumetric_electron_heating_terms.items():
            if v not in self:
                continue
            if max(abs(self[v]['data'])) == 0:
                continue
            vkey = v
            if not vkey[-1] == 'e':
                vkey = vkey + 'e'
            result[vkey] = sign * self.volume_integral(v) / 1e6
            Pe = Pe + result[vkey]
        result['ptote'] = Pe
        Pi = 0
        for v, (sign, id_index) in self.volumetric_ion_heating_terms.items():
            if v not in self:
                continue
            if max(abs(self[v]['data'])) == 0:
                continue
            vkey = v
            if not vkey[-1] == 'i':
                vkey = vkey + 'i'
            result[vkey] = sign * self.volume_integral(v) / 1e6
            Pi = Pi + result[vkey]
        result['ptoti'] = Pi
        return result

    def get_volumetric_heating(self):
        """
        :return: Dictionary having non-zero heating terms, including the total;
            keys of the dictionary end in ``e`` or ``i`` to indicate electron or ion
            heating; units are MW/m^3
        """
        result = {}
        Pe = 0
        for v, (sign, id_index) in self.volumetric_electron_heating_terms.items():
            if v not in self:
                continue
            if max(abs(self[v]['data'])) == 0:
                continue
            vkey = v
            if not vkey[-1] == 'e':
                vkey = vkey + 'e'
            result[vkey] = sign * self[v]['data'][:] / 1e6
            Pe = Pe + sign * self[v]['data'][:] / 1e6
        result['qtote'] = Pe

        Pi = 0
        for v, (sign, id_index) in self.volumetric_ion_heating_terms.items():
            if v not in self:
                continue
            if max(abs(self[v]['data'])) == 0:
                continue
            vkey = v
            if not vkey[-1] == 'i':
                vkey = vkey + 'i'
            result[vkey] = sign * self[v]['data'][:] / 1e6
            Pi = Pi + sign * self[v]['data'][:] / 1e6
        result['qtoti'] = Pi
        return result

    def plot_te_ti(self, styles=['-', '--'], widths=[1, 1], color='b', alpha=1):
        rho = self['rho_grid']['data']
        rho = rho / max(rho)
        ax = pyplot.gca()
        ax.plot(rho, self['Te']['data'], label='Te', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        color = ax.lines[-1].get_color()
        ax.plot(rho, self['Ti']['data'], label='Ti', linestyle=styles[1], linewidth=widths[1], color=color, alpha=alpha)
        pyplot.title('Temperatures')
        pyplot.ylabel('$[keV]$')
        pyplot.xlabel('$\\rho$')
        ax.ticklabel_format(style='sci', scilimits=(1, 2), axis='y')

    def plot_chie_chii(self, styles=['-', '--'], widths=[1, 1], color='b', alpha=1):
        rho = self['rho_grid']['data']
        rho = rho / max(rho)
        ax = pyplot.gca()
        ax.plot(rho, self['chieinv']['data'], label='$\\chi_e$', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        color = ax.lines[-1].get_color()
        ax.plot(rho, self['chiinv']['data'], label='$\\chi_i$', linestyle=styles[1], linewidth=widths[1], color=color, alpha=alpha)
        pyplot.title('Thermal diffusivity')
        pyplot.ylabel('$[m^2/s]$')
        pyplot.xlabel('$\\rho$')
        try:
            ax.set_yscale('log')
        except Exception:
            ax.set_yscale('linear')

    def plot_Qe_Qi(self, styles=['-', '--'], widths=[1, 1], color='b', alpha=1):
        rho = self['rho_grid']['data']
        rho = rho / max(rho)
        ax = pyplot.gca()
        ax.plot(
            rho,
            self['e_fluxe']['data'] + self['e_fluxe_conv']['data'],
            label='$Q_e$',
            linestyle=styles[0],
            linewidth=widths[0],
            color=color,
            alpha=alpha,
        )
        color = ax.lines[-1].get_color()
        ax.plot(
            rho,
            self['e_fluxi']['data'] + self['e_fluxi_conv']['data'],
            label='$Q_i$',
            linestyle=styles[1],
            linewidth=widths[1],
            color=color,
            alpha=alpha,
        )
        pyplot.title('Thermal fluxes')
        pyplot.ylabel('$[W/m^2]$')
        pyplot.xlabel('$\\rho$')
        try:
            ax.set_yscale('log')
        except Exception:
            ax.set_yscale('linear')

    def plot_current(
        self,
        styles=['-', '--', '-.', ':', '-'],
        widths=[1] * 5,
        color='b',
        currents=['curden', 'curboot', 'curohm', 'curbeam', 'currf'],
        alpha=1,
    ):
        rho = self['rho_grid']['data']
        rho = rho / max(rho)
        ax = pyplot.gca()
        if 'curden' in currents:
            ax.plot(rho, self['curden']['data'] / 1.0e6, label='Total', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
            color = ax.lines[-1].get_color()
        if np.sum(abs(self['curboot']['data'])) and 'curboot' in currents:
            ax.plot(
                rho, self['curboot']['data'] / 1.0e6, label='Bootstrap', linestyle=styles[1], linewidth=widths[1], color=color, alpha=alpha
            )
            color = ax.lines[-1].get_color()
        if np.sum(abs(self['curohm']['data'])) and 'curohm' in currents:
            ax.plot(rho, self['curohm']['data'] / 1.0e6, label='Ohmic', linestyle=styles[2], linewidth=widths[2], color=color, alpha=alpha)
            color = ax.lines[-1].get_color()
        if np.sum(abs(self['curbeam']['data'])) and 'curbeam' in currents:
            ax.plot(rho, self['curbeam']['data'] / 1.0e6, label='NBI', linestyle=styles[3], linewidth=widths[3], color=color, alpha=alpha)
            color = ax.lines[-1].get_color()
        if np.sum(abs(self['currf']['data'])) and 'currf' in currents:
            ax.plot(rho, self['currf']['data'] / 1.0e6, label='RF', linestyle=styles[4], linewidth=widths[4], color=color, alpha=alpha)
        pyplot.title('Current density $J$')
        pyplot.ylabel('$[MA/m^2]$')
        ax.ticklabel_format(style='sci', scilimits=(1, 2), axis='y')
        pyplot.xlabel('$\\rho$')

    def plot_qvalue(self, styles=['-', '--'], widths=[1, 1], color='b', alpha=1):
        rho = self['rho_grid']['data']
        rho = rho / max(rho)
        ax = pyplot.gca()
        ax.plot(rho, self['q_value']['data'], label='q', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        pyplot.title('Safety factor')
        ax.ticklabel_format(style='sci', scilimits=(1, 2), axis='y')
        pyplot.xlabel('$\\rho$')

    def plotTransp(self, color=None, alpha=1.0):

        styles = ['-', '--', '-.', ':', '-']
        widths = [1.5, 1.5, 1.5, 2, 0.5]

        rho = self['rho_grid']['data']
        rho = rho / max(rho)

        ax = pyplot.gcf().add_subplot(221)
        pyplot.plot([0], [np.nan])
        if color is None:
            color = ax.lines[-1].get_color()

        ax = []

        # -------------------
        ax.append(pyplot.gcf().add_subplot(221))
        self.plot_current(styles=styles, widths=widths, color=color, alpha=alpha, currents=['curden', 'curbeam'])
        pyplot.title('')
        title_inside('Current density')

        # -------------------
        ax.append(pyplot.gcf().add_subplot(222, sharex=ax[0]))
        self.plot_te_ti(styles=styles, widths=widths, color=color, alpha=alpha)
        pyplot.title('')
        title_inside('Temperatures')

        # -------------------
        ax.append(pyplot.gcf().add_subplot(223, sharex=ax[0]))
        self.plot_qvalue(styles=styles, widths=widths, color=color, alpha=alpha)
        pyplot.title('')
        title_inside('Safety factor')

        # -------------------
        ax.append(pyplot.gcf().add_subplot(224, sharex=ax[0]))
        self.plot_Qe_Qi(styles=styles, widths=widths, color=color, alpha=alpha)
        pyplot.title('')
        title_inside('Thermal fluxes')

        autofmt_sharex()
        return ax

    def plotSummary(self, color=None, alpha=1.0):
        styles = ['-', '--', '-.', ':', '-']
        widths = [1.5, 1.5, 1.5, 2, 0.5]

        rho = self['rho_grid']['data']
        rho = rho / max(rho)

        pyplot.subplots_adjust(hspace=0.3)

        # -------------------
        ax = pyplot.gcf().add_subplot(241)
        pyplot.plot([0], [np.nan])
        if color is None:
            color = ax.lines[-1].get_color()

        # -------------------
        ax = pyplot.gcf().add_subplot(241)
        self.plot_current(styles=styles, widths=widths, color=color, alpha=alpha)

        # -------------------
        ax = pyplot.gcf().add_subplot(245, sharex=ax)
        self.plot_qvalue(styles=styles, widths=widths, color=color, alpha=alpha)

        # -------------------
        # -------------------
        ax = pyplot.gcf().add_subplot(242, sharex=ax)
        self.plot_te_ti(styles=styles, widths=widths, color=color, alpha=alpha)

        # -------------------
        ax = pyplot.gcf().add_subplot(246, sharex=ax)
        self.plot_chie_chii(styles=styles, widths=widths, color=color, alpha=alpha)

        # -------------------
        # -------------------
        ax = pyplot.gcf().add_subplot(243, sharex=ax)
        ax.plot(rho, self['ene']['data'], label='ne', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        for k in range(self['enion']['data'].shape[0]):
            ax.plot(
                rho,
                self['enion']['data'][k, :],
                label='ni ' + str(k),
                linestyle=styles[k + 1],
                linewidth=widths[k + 1],
                color=color,
                alpha=alpha,
            )
        pyplot.title('Densities')
        pyplot.ylabel('$[m^-3]$')
        ax.ticklabel_format(style='sci', scilimits=(1, 2), axis='y')
        pyplot.xlabel('$\\rho$')

        # -------------------
        ax = pyplot.gcf().add_subplot(247, sharex=ax)
        ax.plot(rho, self['p_flux_ion']['data'], label='$\\Gamma_i$', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        pyplot.title('Main ion particle flux')
        pyplot.ylabel('$[m^2/s]$')
        pyplot.xlabel('$\\rho$')
        try:
            ax.set_yscale('log')
        except Exception:
            ax.set_yscale('linear')

        # -------------------
        # -------------------
        ax = pyplot.gcf().add_subplot(244, sharex=ax)

        ax.plot(rho, self['angrot']['data'], label='$\\omega$', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        pyplot.title('Toroidal rotation')
        pyplot.ylabel('$[rad/s]$')
        pyplot.xlabel('$\\rho$')

        ax = pyplot.gcf().add_subplot(248, sharex=ax)
        ax.plot(rho, self['rot_flux']['data'], label='$\\Pi$', linestyle=styles[0], linewidth=widths[0], color=color, alpha=alpha)
        pyplot.title('Rotation flux')
        pyplot.ylabel('$[kg/s^2]$')
        pyplot.xlabel('$\\rho$')

    def plotEquilibrium(self, **kw):
        ax = pyplot.gca()
        kw.setdefault('linewidth', 1)

        levels = np.r_[0.1:10:0.1]

        rlim = self['rlimiter']['data']
        zlim = self['zlimiter']['data']
        R = self['rmhdgrid']['data']
        Z = self['zmhdgrid']['data']
        psi = self['psir_grid']['data']
        PSIRZ = self['psi']['data']
        RHORZ = interp1e(psi, np.linspace(0, 1, len(psi)))(PSIRZ)

        # contours
        line = np.array([np.nan, np.nan])
        rx = []
        zx = []
        for k, item1 in enumerate(contourPaths(R, Z, RHORZ, levels)):
            for item in item1:
                line = np.vstack((line, item.vertices, np.array([np.nan, np.nan])))
                if levels[k] == 1 and len(item.vertices[:, 0]) > len(rx):
                    rx = item.vertices[:, 0]
                    zx = item.vertices[:, 1]

        # masking
        path = matplotlib.path.Path(np.transpose(np.array([rlim, zlim])))
        patch = matplotlib.patches.PathPatch(path, facecolor='none')
        ax.add_patch(patch)
        pyplot.plot(line[:, 0], line[:, 1], **kw)
        ax.lines[-1].set_clip_path(patch)

        kw1 = copy.deepcopy(kw)
        kw1['linewidth'] = kw['linewidth'] + 1
        kw1.setdefault('color', ax.lines[-1].get_color())
        ax.plot(rx, zx, **kw1)
        ax.lines[-1].set_clip_path(patch)

        ax.plot(rlim, zlim, 'k', linewidth=2)
        ax.axis([min(rlim), max(rlim), min(zlim), max(zlim)])
        dx = np.diff(ax.get_xlim()) / 100.0
        dy = np.diff(ax.get_ylim()) / 100.0
        ax.set_aspect('equal')

    def get_psin(self):
        """
        Return the psi_n grid
        """
        psi = self['psir_grid']['data']
        psiax = self['psiaxis']['data']
        psibd = self['psibdry']['data']
        return (psi - psiax) / (psibd - psiax)

    def to_omas(self, ods=None, time_index=0, update=['summary', 'core_profiles', 'equilibrium', 'core_sources'], clear_sources=True):
        """
        Translate ONETWO statefile to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :update: list of IDS to update from statefile

        :return: ODS
        """

        from omas import ODS, omas_environment, transform_current

        if ods is None:
            ods = ODS()

        # ONETWO always has positive current, so COCOS changes
        # statefile is COCOS 1 for CCW current and COCOS 2 for CW current
        Ipsign = np.sign(self['Ipsign']['data'])  # take sign from statefile
        with omas_environment(ods, cocosio=1):
            # consistency check with equilibrium
            ip_path = 'equilibrium.time_slice.%d.global_quantities.ip' % time_index
            if ip_path in ods:
                if self['Ipsign']['data'] * ods[ip_path] < 0:
                    printw("Sign of current in statefile and ODS equilibrium are inconsistent")
                    printw("Assuming sign from ODS equilibrium")
                    Ipsign = np.sign(ods[ip_path])

        if Ipsign > 0:
            cocosio = 1  # Normal-Ip:  positive current is counter-clockwise
        else:
            cocosio = 2  # Reverse-Ip: positive current is clockwise

        # ------------------
        # Summary
        # ------------------

        if 'summary' in update:
            # with omas_environment(ods, cocosio=cocosio):
            gqs = ods['summary.global_quantities']
            for i in ['current_ohm.value', 'current_bootstrap.value', 'current_non_inductive.value']:
                if i not in gqs:
                    gqs[i] = np.zeros(time_index + 1)
                elif time_index >= len(gqs[i]):
                    gqs[i] = np.append(gqs[i], np.zeros(time_index - len(gqs[i]) + 1))

            gqs['current_ohm.value'][time_index] = self['totohm_cur']['data']
            gqs['current_bootstrap.value'][time_index] = self['totboot_cur']['data']
            gqs['current_non_inductive.value'][time_index] = self['tot_cur']['data'] - self['totohm_cur']['data']

            fus = ods['summary.fusion']
            for i in ['neutron_fluxes.total.value', 'neutron_fluxes.thermal.value', 'neutron_power_total.value', 'power.value']:
                if i not in fus:
                    fus[i] = np.zeros(time_index + 1)
                elif time_index >= len(fus[i]):
                    fus[i] = np.append(fus[i], np.zeros(time_index - len(fus[i]) + 1))

            fus['neutron_fluxes.total.value'][time_index] = self['total_neutr_ddn']['data']
            fus['neutron_fluxes.thermal.value'][time_index] = self['total_neutr_ddn_th']['data']
            pfus = self.volume_integral('qfusi')[-1]
            pfus += self.volume_integral('qfuse')[-1]

            # "Power coupled to the plasma by fusion reactions" - IMAS data schema
            fus['power.value'][time_index] = pfus

            # "Total neutron power (from all reactions)" - IMAS data schema
            fus['neutron_power_total.value'][time_index] = (14.1 / 3.5) * pfus

        # ------------------
        # Core profiles
        # ------------------
        if 'core_profiles' in update:
            with omas_environment(
                ods,
                cocosio=cocosio,
                coordsio={
                    'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: self['rho_grid']['data'] / max(self['rho_grid']['data'])
                },
            ):
                ods.set_time_array('core_profiles.time', time_index, int(self['time']['data'] * 1000))
                prof1d = ods['core_profiles.profiles_1d'][time_index]
                prof1d['grid.psi'] = self['psir_grid']['data']

                prof1d['electrons.density_thermal'] = self['ene']['data']
                prof1d['electrons.temperature'] = self['Te']['data'] * 1e3

                if 'ion' in prof1d:
                    del prof1d['ion']
                ks_ions = {}  # ks is the ion index used in OMAS
                kt_ions = {'ip': 0, 'b': 0, 'a': 0}  # kt is the ion index used in the statefile
                for i in ['p', 'i', 'b', 'a']:
                    for k, ion_name in enumerate(map(lambda x: str(x).strip(), self.get('name' + i, {'data': ['He']})['data'])):
                        ion_name = ion_name[0].upper() + ion_name.lower()[1:]
                        if ion_name not in ks_ions:
                            ks_ions[ion_name] = len(ks_ions)
                        ks = ks_ions[ion_name]

                        if i in ['p', 'i']:
                            kt = kt_ions['ip']
                            prof1d['ion'][ks]['density_thermal'] = self['enion']['data'][kt, :]
                            prof1d['ion'][ks]['temperature'] = self['Ti']['data'] * 1e3
                            ion = list(atomic_element(symbol=ion_name).values())[0]
                            kt_ions['ip'] += 1
                        elif i == 'b':
                            kt = kt_ions['b']
                            prof1d['ion'][ks]['density_fast'] = self['enbeam']['data'][kt, :]
                            prof1d['ion'][ks]['pressure_fast_perpendicular'] = self['pressb']['data'] / 3.0
                            prof1d['ion'][ks]['pressure_fast_parallel'] = self['pressb']['data'] / 3.0
                            ion = list(atomic_element(symbol=ion_name).values())[0]
                            kt_ions['b'] += 1
                        elif i == 'a':
                            if not np.sum(self['enalp']['data'][:]):
                                continue
                            prof1d['ion'][ks]['density_fast'] = self['enalp']['data'][:]
                            prof1d['ion'][ks]['pressure_fast_perpendicular'] = (2.0 / 3.0) * self['walp']['data'] * constants.e * 1e3 / 3.0
                            prof1d['ion'][ks]['pressure_fast_parallel'] = (2.0 / 3.0) * self['walp']['data'] * constants.e * 1e3 / 3.0
                            ion = {'Z': 2, 'A': 4}
                            kt_ions['a'] += 1

                        prof1d['ion'][ks]['label'] = ion_name
                        prof1d['ion'][ks]['element'][0]['z_n'] = ion['Z']
                        prof1d['ion'][ks]['element'][0]['a'] = ion['A']
                        prof1d['ion'][ks]['multiple_states_flag'] = 0

                prof1d['zeff'] = self['zeff']['data']
            # prof1d['rotation_frequency_tor_sonic'] = ?

        # ------------------
        # Equilibrium
        # ------------------
        if 'equilibrium' in update:
            ods.set_time_array('equilibrium.time', time_index, int(self['time']['data'] * 1000))
            eq = ods['equilibrium.time_slice'][time_index]
            coordsio = {'equilibrium.time_slice.%d.profiles_1d.psi' % time_index: self['psir_grid']['data']}
            if 'equilibrium.time_slice.%d.profiles_1d.psi' % time_index in ods:
                with omas_environment(ods, cocosio=cocosio):
                    ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index] = (
                        ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index]
                        - ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index][0]
                        + coordsio['equilibrium.time_slice.%d.profiles_1d.psi' % time_index][0]
                    )

            with omas_environment(ods, coordsio=coordsio, cocosio=cocosio):

                eq['global_quantities.magnetic_axis.b_field_tor'] = float(self['btor']['data'])
                eq['global_quantities.magnetic_axis.r'] = float(self['rmajor']['data'])
                eq['global_quantities.magnetic_axis.z'] = self['zma']['data']
                eq['global_quantities.ip'] = float(self['tot_cur']['data'])

                ods['equilibrium.vacuum_toroidal_field.r0'] = float(self['rmajor']['data'])
                ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', time_index, self['btor']['data'])

                eq['profiles_1d.rho_tor_norm'] = self['rho_grid']['data'] / max(self['rho_grid']['data'])
                eq['profiles_1d.dpressure_dpsi'] = self['pprim']['data']
                eq['profiles_1d.f'] = self['fpsinrho']['data']
                eq['profiles_1d.f_df_dpsi'] = self['ffprim']['data']
                eq['profiles_1d.gm1'] = self['r2cap']['data'] / self['rmajor']['data'] ** 2
                eq['profiles_1d.gm5'] = self['xhm2']['data'] * self['btor']['data'] ** 2
                eq['profiles_1d.gm9'] = self['ravginrho']['data']
                eq['profiles_1d.dvolume_dpsi'] = deriv(self['psir_grid']['data'], self['psivolpnrho']['data'])

                eq['profiles_1d.r_outboard'] = self['rmajavnrho']['data'] + self['rminavnrho']['data']
                eq['profiles_1d.r_inboard'] = self['rmajavnrho']['data'] - self['rminavnrho']['data']

                eq['profiles_1d.elongation'] = self['elongxnrho']['data']

                eq['profiles_1d.triangularity_upper'] = self['triangnrho_u']['data']
                eq['profiles_1d.triangularity_lower'] = self['triangnrho_l']['data']

                # eq['profiles_1d.squareness_upper_outer']
                # eq['profiles_1d.squareness_upper_inner']
                # eq['profiles_1d.squareness_lower_outer']
                # eq['profiles_1d.squareness_lower_inner']

                eq['profiles_1d.q'] = self['q_value']['data']

        # ------------------
        # Core sources
        # ------------------
        if 'core_sources' in update:
            ods.set_time_array('core_sources.time', time_index, int(self['time']['data'] * 1000))
            source = ods['core_sources.source']
            if clear_sources:
                ods['core_sources.source'].clear()
            volume = self.volume_integral(1)
            ks_source = {}

            def add_source(location, identifier, sign, id_index):
                if identifier in self:  # some terms may not be written by ONETWO in the statefile if the array is all zeros
                    if identifier not in ks_source:
                        ks_source[identifier] = len(ks_source)
                    ks = ks_source[identifier]
                    coordsio = {
                        "core_sources.source.%d.profiles_1d.%d.grid.rho_tor_norm"
                        % (ks, time_index): self['rho_grid']['data']
                        / max(self['rho_grid']['data'])
                    }
                    with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                        source[ks]['profiles_1d'][time_index]['grid.volume'] = volume
                        source[ks]['identifier.name'] = identifier
                        source[ks]['identifier.index'] = id_index
                        source[ks]['identifier.description'] = re.sub('^\\*\\s+', '', self[identifier]['long_name'])
                        src = source[ks]['profiles_1d'][time_index]
                        src[location] = sign * self[identifier]['data']

            # electrons energy [W.m^-3]
            for identifier, (sign, id_index) in self.volumetric_electron_heating_terms.items():
                add_source('electrons.energy', identifier, sign, id_index)

            # ions energy [W.m^-3]
            for identifier, (sign, id_index) in self.volumetric_ion_heating_terms.items():
                add_source('total_ion_energy', identifier, sign, id_index)

            # electron particle [m^-3.s^-1]
            for identifier, (sign, id_index) in self.volumetric_electron_particles_terms.items():
                add_source('electrons.particles', identifier, sign, id_index)

            # momentum kg.m^-1.s^-2
            for identifier, (sign, id_index) in self.volumetric_momentum_terms.items():
                add_source('momentum_tor', identifier, sign, id_index)

            eq = ods['equilibrium.time_slice'][time_index]
            rho_tor_norm = self['rho_grid']['data'] / max(self['rho_grid']['data'])
            coordsio = {'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: rho_tor_norm}
            with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                ods['core_profiles.vacuum_toroidal_field.r0'] = R0 = ods['equilibrium.vacuum_toroidal_field.r0']
                ods.set_time_array(
                    'core_profiles.vacuum_toroidal_field.b0', time_index, ods['equilibrium.vacuum_toroidal_field.b0'][time_index]
                )
                B0 = ods['core_profiles.vacuum_toroidal_field.b0'][time_index]

                prof1d['q'] = self['q_value']['data']

                rhon = self['rho_grid']['data'] / max(self['rho_grid']['data'])

            isource = len(ods['core_sources.source'])
            for item, value in {'curbeam': 2, 'currf': 3}.items():
                j_actuator = (1.0 / B0) * transform_current(
                    rhon, JtoR=self[item]['data'] / R0, equilibrium=ods['equilibrium.time_slice'][time_index], includes_bootstrap=False
                )
                ods[f'core_sources.source.{isource}.profiles_1d.{time_index}.j_parallel'] = j_actuator
                ods[f'core_sources.source.{isource}.identifier.description'] = item
                ods[f'core_sources.source.{isource}.identifier.name'] = item
                ods[f'core_sources.source.{isource}.identifier.index'] = value
                isource += 1

        # ------------------
        # Plasma currents
        # ------------------
        if 'core_profiles' in update and 'equilibrium' in ods:
            eq = ods['equilibrium.time_slice'][time_index]
            rho_tor_norm = self['rho_grid']['data'] / max(self['rho_grid']['data'])
            coordsio = {'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: rho_tor_norm}
            with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                ods['core_profiles.vacuum_toroidal_field.r0'] = R0 = ods['equilibrium.vacuum_toroidal_field.r0']
                ods.set_time_array(
                    'core_profiles.vacuum_toroidal_field.b0', time_index, ods['equilibrium.vacuum_toroidal_field.b0'][time_index]
                )
                B0 = ods['core_profiles.vacuum_toroidal_field.b0'][time_index]

                prof1d['q'] = self['q_value']['data']

                rhon = self['rho_grid']['data'] / max(self['rho_grid']['data'])

                # must transform these currents from <J*R0/R> to <J.B>/B0
                JtoR_ohmic = self['curohm']['data'] / R0
                j_ohmic = (1.0 / B0) * transform_current(rhon, JtoR=JtoR_ohmic, equilibrium=eq, includes_bootstrap=False)

                JtoR_bs = (self['curboot']['data']) / R0
                j_bootstrap = (1.0 / B0) * transform_current(rhon, JtoR=JtoR_bs, equilibrium=eq, includes_bootstrap=True)

                JtoR_act = (self['curbeam']['data'] + self['currf']['data']) / R0
                j_actuator = (1.0 / B0) * transform_current(rhon, JtoR=JtoR_act, equilibrium=eq, includes_bootstrap=False)

                # j_total, j_tor, and integrated currents are calculated by this function
                # j_total set to None to make sure it's recalculated
                ods.physics_core_profiles_currents(
                    time_index,
                    rho_tor_norm,
                    j_actuator=j_actuator,
                    j_bootstrap=j_bootstrap,
                    j_non_inductive=None,
                    j_ohmic=j_ohmic,
                    j_total=None,
                )

        return ods


class OMFIT_dump_psi(OMFITascii, SortedDict):
    """
    A class for loading the dump_psi.dat file produced by ONETWO when it fails in the contouring

    :param filename: (str) The filename of the dump_psi.dat file (default: 'dump_psi.dat')
    :param plot_on_load: (bool) If true, plot the psi filled contour map and the specific problem value of psi
    """

    def __init__(self, filename='dump_psi.dat'):
        OMFITascii.__init__(self, filename)
        SortedDict.__init__(self)
        self.dynaLoad = True
        return

    @dynaLoad
    def load(self):
        with open(self.filename) as f:
            fl = f.readlines()
        l = fl[0].split()
        self['nw'] = int(l[0])
        self['nh'] = int(l[1])
        self['isgnpsi'] = int(l[2])
        self['isym'] = l[3]
        self['mapset'] = l[4] in 'T'
        self['mf'] = int(l[5])
        fr = '\n'.join(fl[1:]).split()
        self['rgrid'] = np.zeros((self['nw'],), dtype=float)
        for i in range(self['nw']):
            self['rgrid'][i] = float(fr.pop(0))
        self['zgrid'] = np.zeros((self['nh'],), dtype=float)
        for i in range(self['nh']):
            self['zgrid'][i] = float(fr.pop(0))
        self['psi'] = np.zeros((self['nw'], self['nh']), dtype=float, order='C')
        for j in range(self['nh']):
            for i in range(self['nw']):
                self['psi'][i, j] = float(fr.pop(0))
        self['psi'] = self['psi'].T
        self['zeros'] = np.zeros((self['nw'], self['nh']), dtype=float, order='C')
        for j in range(self['nh']):
            for i in range(self['nw']):
                self['zeros'][i, j] = float(fr.pop(0))  # Not all zeros!!!
        if self['mapset']:
            self['map'] = np.zeros((self['nw'], self['nh']), dtype=float)
            for j in range(self['nh']):
                for i in range(self['nw']):
                    self['map'][i, j] = float(fr.pop(0))
        if self['mf'] > 0:
            self['psif'] = np.zeros((self['mf'],), dtype=float)
            for i in range(self['mf']):
                self['psif'][i] = float(fr.pop(0))
        self['psi_trace'] = float(fr.pop(0))
        from fluxSurface import fluxSurfaces

        self['flx'] = fluxSurfaces(self['rgrid'], self['zgrid'], self['psi'])
        return

    def plot(self, ax=None):
        """
        Plot the psi mapping as filled contours, with the problem surface as a
        contour

        :return: None
        """
        if ax is None:
            ax = pyplot.gca()
        ax.set_aspect('equal')
        contourf(self['rgrid'], self['zgrid'], self['psi'])
        CS = contour(self['rgrid'], self['zgrid'], self['psi'], levels=[self['psi_trace']])
        clabel(CS, inline=True, fmt='%r')
        pyplot.title(r'Psi map with problem $\psi=%s$' % (self['psi_trace']))
        return

    # End of class OMFIT_dump_psi


class OMFITiterdbProfiles(SortedDict, OMFITascii):
    """FREYA profiles data files"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not len(line):
                continue
            if line[0] == '*':
                tmp = line[1:].strip().split(',')
                species = None
                if len(tmp) == 1:
                    key = tmp[0]
                    units = ''
                elif len(tmp) == 2:
                    key, units = tmp
                elif len(tmp) == 3:
                    key, units, species = tmp
                    key = key + ' , ' + species.split(':')[1].strip()
                self[key] = SortedDict()
                self[key]['units'] = units.strip()
                self[key]['data'] = []
                self[key]['long_name'] = line
            else:
                self[key]['data'].extend(list(map(float, line.split())))
        for key in list(self.keys()):
            self[key]['data'] = np.array(self[key]['data'])

    @dynaSave
    def save(self):
        data = []
        n = 5
        for key in list(self.keys()):
            data.append(self[key]['long_name'])
            for items in [self[key]['data'][n * i : n * (i + 1)] for i in range(20)]:
                if not len(items):
                    continue
                data.append('  ' + '  '.join(['% 14.5e' % x for x in items]))
        data = '\n'.join(data)
        with open(self.filename, 'w') as f:
            f.write(data)

    @dynaLoad
    def plot(self):
        ls = ['o', '.', 's', 'd', 'x']
        for k, item in enumerate([k for k in list(self.keys()) if k != 'rho grid' and isinstance(self[k]['data'], np.ndarray)]):
            if k == 0:
                ax = pyplot.subplot(2, 4, k + 1)
            else:
                pyplot.subplot(2, 4, k + 1, sharex=ax)
            pyplot.plot(self['rho grid']['data'] / max(self['rho grid']['data']), self[item]['data'])
            title_inside(item, y=0.8)
            pyplot.ylabel(self[item]['units'])
        autofmt_sharex()
        pyplot.xlim([0, 1])


def ONETWO_beam_params_from_ods(ods, t, device, nml2=None, smooth_power=None, time_avg=70):
    """
    Return the parts of NAMELIS2 that are needed by ONETWO or FREYA to describe the beams

    :param ods: An ODS object that contains beam information in the nbi IDS

    :param t: (ms) The time at which the beam parameters should be determined

    :param device: The device this is being set up for

    :param nml2: A namelist object pointing to inone['NAMELIS2'], which will be modified *in place*

    :param smooth_power: This function returns an instantaneous power, for a single time slice, but the beam ods presumably
        has fairly continuous power that should be smoothed, since the beam slowing down time is such as to smooth out
        instantaneous beam changes

    :param time_avg: (ms) If smooth_power is not given, then the beam power is causally smoothed using time_avg for the
        window_size of smooth_by_convolution.  time_avg is also used to determine how far back the beams should be reported as
        being on

    :return: nml2
    """
    from omfit_classes.utils_math import interp1e

    if nml2 is None:
        nml2 = {}

    bunit = ods['nbi.unit']
    nbeams = len(bunit)
    btime = ods['nbi.time']
    if smooth_power is None:
        smooth_power = smooth_by_convolution(
            bunit[':.power_launched.data'].T, btime, btime, window_size=time_avg / 1e3, window_function='boxcar', causal=True
        )
    nml2['NBEAMS'] = nbeams
    nml2['SFRAC1'] = np.zeros(nbeams)
    bt_ind = closestIndex(btime, t / 1e3)
    pinj = smooth_power[bt_ind, :]
    if sum(pinj) == 0:
        nml2['NBEAMS'] = 0
        return nml2
    bspecies_a = list(set(bunit[':.species.a'][pinj > 0]))
    bspecies_z = list(set(bunit[':.species.z_n'][pinj > 0]))
    if len(bspecies_a) > 1 or len(bspecies_z) > 1:
        raise NotImplementedError('ONETWO itself can only handle 1 beam species')
    nml2['NAMEB'] = element_symbol(bspecies_z[0], n=bspecies_a[0]).lower()
    beamon = array([99.0] * nbeams)
    beamon[pinj > 0] = t / 1e3 - 2 * time_avg / 1e3
    nml2['BEAMON'] = beamon
    nml2['BTIME'] = array([4 * time_avg / 1e3] * nbeams)
    nml2['NSOURC'] = 1  # Decision was made to have sources from omas be just one source beams

    energy = array([0.0] * nbeams)
    # Put non-zero power first
    r_ordered_index = list(reversed(np.argsort(pinj)))
    for k in list(nml2.keys()):
        if k.startswith('FBCUR'):
            del nml2[k]
    for ik, i in enumerate(r_ordered_index):
        E = bunit['%d.energy.data' % i] / 1e3
        if E[E > 1].sum() > 0 and pinj[i] > 0:
            energy[i] = interp1e(btime[E > 1], E[E > 1])(t / 1e3)
        else:
            continue
        fbcur = bunit['%d.beam_current_fraction.data' % i]
        fbcur0 = fbcur[0, :]
        nz_ind = fbcur0 != 0  # Non-zero on first fraction
        for ie in range(fbcur.shape[0]):
            nml2['FBCUR(%d,%d)' % (ie + 1, ik + 1)] = float(interp1e(btime[nz_ind], fbcur[ie, nz_ind])(t / 1e3))
    nml2['EBKEV'] = energy
    nml2['BPTOR'] = pinj
    if is_device(device, 'DIII-D'):
        RPIVOT = nml2['RPIVOT'] = pinj * 0 + 286.56  # This is DIII-D specific
    elif 'RPIVOT' in nml2 and len(nml2['RPIVOT']) == len(pinj):
        RPIVOT = nml2['RPIVOT']
    else:
        raise NotImplementedError('Need to figure out RPIVOT for device %s' % device)
    nml2['ANGLEH'] = (
        bunit[':.beamlets_group[0].direction']
        * np.arcsin(bunit[':.beamlets_group[0].tangency_radius'] / (nml2['RPIVOT'] / 1e2))
        * 180.0
        / np.pi
    )
    source_r = bunit[':.beamlets_group[0].position.r']
    source_z = bunit[':.beamlets_group[0].position.z']
    source_phi = bunit[':.beamlets_group[0].position.phi']
    ap_r = bunit[':.aperture[0].centre.r']
    ap_z = bunit[':.aperture[0].centre.z']
    ap_phi = bunit[':.aperture[0].centre.phi']
    XLBAPA = np.sqrt((source_z - ap_z) ** 2 + ap_r ** 2 + source_r ** 2 - 2 * ap_r * source_r * np.cos(source_phi - ap_phi))
    anglev = nml2['ANGLEV'] = np.arcsin((source_z - ap_z) / XLBAPA) * 180.0 / np.pi
    # Known: RPIVOT,
    s_x = source_r * np.cos(source_phi)
    s_y = source_r * np.sin(source_phi)
    s_z = source_z
    a_x = ap_r * np.cos(ap_phi)
    a_y = ap_r * np.sin(ap_phi)
    a_z = ap_z
    d_x = s_x - a_x
    d_y = s_y - a_y
    d_z = s_z - a_z
    # Beam path parameterization
    # b_x = s_x * t + a_x * (1 - t) = (s_x - a_x) * t + a_x = d_x * t + a_x
    # b_y = d_y * t + a_y
    # b_z = d_z * t + a_z
    # Want to know when b_x**2 + b_y**2 == RPIVOT**2
    # d_x^2*t^2 + 2*d_x*a_x*t + a_x^2 + d_y^2*t^2 + 2*d_y*a_y*t + a_y^2 = RPIVOT^2
    A = d_x ** 2 + d_y ** 2
    B = 2 * d_x * a_x + 2 * d_y * a_y
    C = a_x ** 2 + a_y ** 2 - (RPIVOT / 1e2) ** 2  # cm to m
    tPIVOT = (-B + np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
    # Establish position of pivot in 3D space
    b_x_pivot = d_x * tPIVOT + a_x
    b_y_pivot = d_y * tPIVOT + a_y
    b_z_pivot = d_z * tPIVOT + a_z
    nml2['ZPIVOT'] = b_z_pivot * 100.0  # m to cm
    # Also want to know how far from pivot point to source
    nml2['BLENP'] = np.sqrt((b_x_pivot - s_x) ** 2 + (b_y_pivot - s_y) ** 2 + (b_z_pivot - s_z) ** 2) * 100.0  # m to cm

    # Put non-zero power first
    r_ordered_index = list(reversed(np.argsort(pinj)))
    for bk in ['ZPIVOT', 'ANGLEV', 'ANGLEH', 'RPIVOT', 'BPTOR', 'BTIME', 'BEAMON', 'EBKEV', 'SFRAC1']:  # 'FBCUR' already sorted
        nml2[bk] = np.array(nml2[bk])[r_ordered_index]
    nml2['NBEAMS'] = int((pinj > 0).sum())
    return nml2
