import pandas as pd
import string
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
import pickle
import gzip

from streng.codes.greek.eak2000.raw.ch2.seismic_action import spectra
from streng.phd.building_models.model2d.slab_loads import *
from streng.phd.building_models.model2d.model_input import Model2d
import matplotlib.pyplot as plt

from streng.ppp.sections.geometry.tee import TeeSectionGeometry
from streng.ppp.sections.geometry.rectangular import RectangularSectionGeometry
from streng.ppp.opensees.pre.elements.modified_ibarra_krawinkler import ModifiedIbarraKrawinkler

from openseespy import opensees
import math

def ReadRecord(inFilename, outFilename):
    dt = 0.0
    npts = 0

    # Open the input file and catch the error if it can't be read
    inFileID = open(inFilename, 'r')

    # Open output file for writing
    outFileID = open(outFilename, 'w')

    # Flag indicating dt is found and that ground motion
    # values should be read -- ASSUMES dt is on last line
    # of header!!!
    flag = 0

    # Look at each line in the file
    for line in inFileID:
        if line == '\n':
            # Blank line --> do nothing
            continue
        elif flag == 1:
            # Echo ground motion values to output file
            outFileID.write(line)
        else:
            # Search header lines for dt
            words = line.split()
            lengthLine = len(words)

            if lengthLine >= 4:

                if words[0] == 'NPTS=':
                    # old SMD format
                    for word in words:
                        if word != '':
                            # Read in the time step
                            if flag == 1:
                                dt = float(word)
                                break

                            if flag == 2:
                                npts = int(word.strip(','))
                                flag = 0

                            # Find the desired token and set the flag
                            if word == 'DT=' or word == 'dt':
                                flag = 1

                            if word == 'NPTS=':
                                flag = 2


                elif words[-1] == 'DT':
                    # new NGA format
                    count = 0
                    for word in words:
                        if word != '':
                            if count == 0:
                                npts = int(word)
                            elif count == 1:
                                dt = float(word)
                            elif word == 'DT':
                                flag = 1
                                break

                            count += 1

    inFileID.close()
    outFileID.close()

    return dt, npts


@dataclass
class OpenSeesResults:
    elastic_periods: list = field(init=False, repr=False, default_factory=list)
    elastic_eigenvectors: list = field(init=False, repr=False, default_factory=list)
    elastic_gravity_element_forces: Dict[int, list] = field(init=False, repr=False, default_factory=dict)

    model_mIK_periods: list = field(init=False, repr=False, default_factory=list)
    model_mIK_eigenvectors: list = field(init=False, repr=False, default_factory=list)

    pushover_element_deformation: Dict[int, list] = field(init=False, repr=False, default_factory=dict)
    pushover_element_force: Dict[int, list] = field(init=False, repr=False, default_factory=dict)


@dataclass
class OpenSeesModel2d:
    model: Model2d

    tcl_make: bool = False
    tcl_filename: str = ''
    tcl_file_text: List[str] = field(default_factory=list)

    include_pdelta: bool = False

    inelastic_analysis: bool = False
    inelastic_analysis_type: str = '' # 'pushover' or 'time_history'

    # time_history: bool = False
    # pushover: bool = False

    etabs_pushocer_curve_check: str = ''

    results: OpenSeesResults = field(init=False, repr=False, default_factory=OpenSeesResults)


    def os_do_it(self):
        # self._os_start()
        # self._os_nodes()
        # self._os_node_fixes()
        # self._os_node_masses()
        # self._os_node_equal_displ()
        # self._os_elements()
        #
        # # if self.inelastic_analysis == True:
        # #     self._os_zero_length_elements()
        #
        #
        #
        # self.inelastic_analysis = True
        # if self.inelastic_analysis == True:
        #     self._os_nodes_extra()
        #
        # self.results.periods_elastic, self.results.eigenvectors_elastic = self._os_eigen_analysis()

        # self._os_gravity_loads()
        #
        # self._os_run_elastic_analysis()
        #
        # if self.pushover == True:
        #     self._os_run_pushover()
        #
        # if self.time_history == True:
        #     self._os_run_time_history()


        file = open(self.tcl_filename, 'w')
        file.write('\n'.join(self.tcl_file_text))
        file.close()


    def os_run_elastic(self):
        self._os_start()
        self._os_nodes()
        self._os_node_fixes()
        self._os_node_masses()
        self._os_node_equal_displ()
        self._os_elements(include_zero_length=False)
        self.results.elastic_periods, self.results.elastic_eigenvectors = self._os_eigen_analysis()
        self._os_gravity_loads()
        self._os_run_gravity_elastic()


    def os_run_pushover(self):
        self._os_start()
        self._os_nodes()
        self._os_nodes_extra()
        self._os_node_fixes()
        self._os_node_masses()
        self._os_node_equal_displ()
        self._os_elements(include_zero_length=True)
        self._os_zero_length_elements()
        self.results.model_mIK_periods, self.results.model_mIK_eigenvectors = self._os_eigen_analysis()
        self._os_run_push_grav()
        self._os_run_pushover()


    def os_run_time_history(self):
        self._os_start()
        self._os_nodes()
        self._os_nodes_extra()
        self._os_node_fixes()
        self._os_node_masses()
        self._os_node_equal_displ()
        self._os_elements(include_zero_length=True)
        self._os_zero_length_elements()
        self.results.model_mIK_periods, self.results.model_mIK_eigenvectors = self._os_eigen_analysis()
        self._os_run_push_grav()
        self.__os_run_time_history()



    def _os_start(self):
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('#')
        self.tcl_file_text.append('# M O D E L  D O M A I N  1  (3DOF)')
        self.tcl_file_text.append('#')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')

        opensees.wipe()
        self.tcl_file_text.append('wipe')
        opensees.model('Basic', '-ndm', 2)
        self.tcl_file_text.append('model BasicBuilder -ndm 2 -ndf 3')
        self.tcl_file_text.append('source rotSpring2DModIKModel.tcl')
        self.tcl_file_text.append('')

        if self.include_pdelta == False:
            opensees.geomTransf('Linear', 1)
            self.tcl_file_text.append('geomTransf Linear 1')
        else:
            opensees.geomTransf('PDelta', 1)
            self.tcl_file_text.append('geomTransf PDelta 1')


    def _os_nodes(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# N O D E S')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# node $NodeTag $XCoord $Ycoord')
        self.tcl_file_text.append('')

        for index, row in self.model.input_data['Nodes'].iterrows():
            # print(f'{index} {float(row["X"])} {row["Z"]}')
            opensees.node(index, float(row['X']), row['Z'])
            self.tcl_file_text.append(f'node{index:7}{float(row["X"]):13.2f}{float(row["Z"]):13.2f}')


    def _os_nodes_extra(self):
        self.tcl_file_text.append('# -----------------------------------------------')
        self.tcl_file_text.append('# Nodes for zero length elements')
        self.tcl_file_text.append('# -----------------------------------------------')

        dfElements = self.model.input_data['Elements']
        nodes_dict = self.model.input_data['Nodes'].to_dict('index')

        for index, row in dfElements.iterrows():
            _nodeI, _nodeJ = self.model.get_element_endpoints(index)
            if row['ElementType'] == 'BEAM':
                _extra_nodeI = 10 * _nodeI + 2
                _extra_nodeJ = 10 * _nodeJ + 4

            if 'COLUMN' in str(row['ElementType']):
                _extra_nodeI = 10 * _nodeI + 1
                _extra_nodeJ = 10 * _nodeJ + 3

            _extra_nodeI_X = float(nodes_dict[_nodeI]['X'])
            _extra_nodeI_Y = float(nodes_dict[_nodeI]['Z'])
            _extra_nodeJ_X = float(nodes_dict[_nodeJ]['X'])
            _extra_nodeJ_Y = float(nodes_dict[_nodeJ]['Z'])
            opensees.node(_extra_nodeI, _extra_nodeI_X, _extra_nodeI_Y)
            opensees.node(_extra_nodeJ, _extra_nodeJ_X, _extra_nodeJ_Y)

            self.tcl_file_text.append(f'node{_extra_nodeI:7}{_extra_nodeI_X:13.2f}{_extra_nodeI_Y:13.2f}')
            self.tcl_file_text.append(f'node{_extra_nodeJ:7}{_extra_nodeJ_X:13.2f}{_extra_nodeJ_Y:13.2f}')




    def _os_node_fixes(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# R E S T R A I N T S')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# fix $NodeTag x-transl y-transl z-rot')
        self.tcl_file_text.append('')
        for index, row in self.model.input_data['Nodes'].iterrows():
            if row['Z'] == 0.0:
                opensees.fix(index, 1, 1, 1)
                self.tcl_file_text.append(f'fix{index:7}{1:5}{1:5}{1:5}')


    def _os_node_masses(self):
        if self.tcl_make == True:
            self.tcl_file_text.append('')
            self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
            self.tcl_file_text.append('# M A S S E S')
            self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
            self.tcl_file_text.append('')
            self.tcl_file_text.append('# Mass Definition : mass $NodeTag $(ndf nodal mass values corresponding to each DOF)')
            self.tcl_file_text.append('')

            masses_dict = self.model.input_data['masses'].to_dict('index')

            for i in range(1, self.model.stories_total+1):
                # node = (self.input_data['Nodes']['Storey'] == i).idxmax()
                node = self.model.master_nodes[i-1]
                massX = masses_dict[i]['mass']
                opensees.mass(int(node), massX, 1.0e-10, 1.0e-10)
                self.tcl_file_text.append(f'mass{node:7}{massX:10.3f}{0:10.1f}{0:10.1f}')


    def _os_node_equal_displ(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# E Q U A L  C O N S T R A I N T S')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# Equal Constraint/equalDOF Definition : equalDOF $MasterNode $SlaveNode $DOFs')
        self.tcl_file_text.append('')
        dfNodes = self.model.input_data['Nodes']
        for storey_level in self.model.storey_levels[1:]:
            nodes_in_level = dfNodes[dfNodes.Z==storey_level].index.tolist()
            for node in nodes_in_level[1:]:
                opensees.equalDOF(nodes_in_level[0], node, 1)
                self.tcl_file_text.append(f'equalDOF{int(nodes_in_level[0]):8}{int(node):10}{1:7}      ; # StoreyLevel: {storey_level:5.2f}')


    def _os_elements(self, include_zero_length):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# E L A S T I C   T I M O S H E N K O   B E A M - C O L U M N   E L E M E N T S')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# element ElasticTimoshenkoBeam $eleTag $iNode $jNode $E $G $A $Iz $Avy $transfTag <-mass $massDens> <-cMass>')
        self.tcl_file_text.append('')

        conc_dict = self.model.input_data['Concrete'].to_dict('index')
        modFactors_dict = self.model.input_data['ModFactors'].to_dict('index')

        E = float(conc_dict['CONC']['E'])
        U = float(conc_dict['CONC']['U'])
        G = E / (2.0*(1.0+U))

        dfElements = self.model.input_data['Elements']
        sections_dict = self.model.input_data['Sections'].to_dict('index')
        for index, row in dfElements.iterrows():
            element_type = row['ElementType']
            section_name = row['SectionName']

            bw, h, beff, frame_location = sections_dict[section_name]['b'],\
                                          sections_dict[section_name]['h'], \
                                          sections_dict[section_name]['beff'], \
                                          sections_dict[section_name]['Frame_Loc']
            hf = self.model.misc['hf']

            A = 0.0
            Iz = 0.0
            Avy = 0.0

            mf_area = modFactors_dict[element_type]['Area']
            mf_mom = modFactors_dict[element_type]['Moment']
            mf_shear = modFactors_dict[element_type]['Shear']
            # mf_tor = modFactors_dict[element_type]['Torsional']

            if element_type == 'BEAM':
                tbeam = TeeSectionGeometry(bw = bw, h = h, beff=beff, hf = hf)
                A = tbeam.area * mf_area
                Iz = tbeam.moment_of_inertia_xx * mf_mom
                Avy = tbeam.shear_area_2 * mf_shear

            elif element_type == 'COLUMN_EX':
                rect = RectangularSectionGeometry(b=bw, h=h)
                A = rect.area * mf_area
                Iz = rect.moment_of_inertia_xx * mf_mom
                Avy = rect.shear_area_2 * mf_shear
            elif element_type == 'COLUMN_IN':
                rect = RectangularSectionGeometry(b=bw, h=h)
                A = rect.area * mf_area
                Iz = rect.moment_of_inertia_xx * mf_mom
                Avy = rect.shear_area_2 * mf_shear
            elif element_type == 'WALL':
                rect = RectangularSectionGeometry(b=bw, h=h)
                A = rect.area * mf_area
                Iz = rect.moment_of_inertia_xx * mf_mom
                Avy = rect.shear_area_2 * mf_shear
            elif element_type == 'RIGID':
                rect = RectangularSectionGeometry(b=bw, h=h)
                A = rect.area * mf_area
                Iz = rect.moment_of_inertia_xx * mf_mom
                Avy = rect.shear_area_2 * mf_shear

            n_MIK = 10
            if include_zero_length == True:
                Izmod = Iz * (n_MIK+1.0) / n_MIK
            else:
                Izmod = Iz

            _nodeI = int(row["NodeI"])
            _nodeJ = int(row["NodeJ"])
            if include_zero_length == True:
                if element_type == 'BEAM':
                    _nodeI = _nodeI * 10 + 2
                    _nodeJ = _nodeJ * 10 + 4
                elif 'COLUMN' in str(element_type):
                    _nodeI = _nodeI * 10 + 1
                    _nodeJ = _nodeJ * 10 + 3
            # if element_type == 'BEAM':
            #     _nodeI = _nodeI * 10 + 2
            #     _nodeJ = _nodeJ * 10 + 4
            # elif 'COLUMN' in str(element_type):
            #     _nodeI = _nodeI * 10 + 1
            #     _nodeJ = _nodeJ * 10 + 3


            opensees.element('ElasticTimoshenkoBeam', int(index), _nodeI, _nodeJ, E, G, A, Izmod, Avy, 1)  # , '-mass', 0., '-lMass')
            self.tcl_file_text.append(f'element ElasticTimoshenkoBeam{index:7}{_nodeI:7}{_nodeJ:7}'
                                      f'{E:13.3e}{G:13.5e}{A:13.5e}{Izmod:13.5e}{Avy:13.5e}'
                                      f'    1   -mass        0')
            # self.tcl_file_text.append(f'element elasticBeamColumn{index:7}{_nodeI:7}{_nodeJ:7}'
            #                           f'{A:13.5e}{E:13.3e}{Izmod:13.5e}     1')


    def _os_zero_length_elements(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# Z E R O   L E N G T H   E L E M E N T S')
        self.tcl_file_text.append('# --------------------------------------------------------------------------------------------------------------')

        conc_dict = self.model.input_data['Concrete'].to_dict('index')
        modFactors_dict = self.model.input_data['ModFactors'].to_dict('index')


        Ec = float(conc_dict['CONC']['E'])

        n_mIK = 10.

        dfElements = self.model.input_data['Elements']
        sections_dict = self.model.input_data['Sections'].to_dict('index')
        for index, row in dfElements.iterrows():
            element_type = row['ElementType']
            section_name = row['SectionName']
            reinforcement_name = row['ReinforcementID']

            mf_mom = modFactors_dict[element_type]['Moment']

            _nodeI, _nodeJ = self.model.get_element_endpoints(index)

            length = self.model.get_element_length_by_ID(index)

            bw, h, frame_location = sections_dict[section_name]['b'],\
                                   sections_dict[section_name]['h'], \
                                   sections_dict[section_name]['Frame_Loc']
            hf = self.model.misc['hf']

            if element_type == 'BEAM':
                tbeam = TeeSectionGeometry(bw = bw, h = h, beff=bw + 8.0 * hf, hf = hf)
                Iz = tbeam.moment_of_inertia_xx * mf_mom
                _extra_nodeI = 10 * _nodeI + 2
                _extra_nodeJ = 10 * _nodeJ + 4

                McMy = 1.001   # ratio of capping moment to yield moment, Mc / My

                # Left
                hinge_neg = self.model.reinforcement_beams_kanepe[f'{reinforcement_name}.L.neg']
                hinge_pos = self.model.reinforcement_beams_kanepe[f'{reinforcement_name}.L.pos']
                hinge_neg.calculate()
                hinge_pos.calculate()

                print(f'{index}: {reinforcement_name} Left:  My_P={hinge_pos.My}    My_N={-hinge_neg.My}')

                if self.inelastic_analysis_type != 'pushover':
                    beam_mIK_L = ModifiedIbarraKrawinkler(n=n_mIK, E=Ec, I=Iz, L=length,
                                                    My_P=hinge_pos.My, McMy_P=McMy, th_pP=hinge_pos.θpl, th_pcP=0.5*hinge_pos.θpl,
                                                    th_uP=4*hinge_pos.θpl,
                                                    My_N=-hinge_neg.My, McMy_N=McMy, th_pN=hinge_neg.θpl, th_pcN=0.5*hinge_neg.θpl,
                                                    th_uN=4*hinge_neg.θpl)
                else:
                    beam_mIK_L = ModifiedIbarraKrawinkler(n=n_mIK, E=Ec, I=Iz, L=length,
                                                    My_P=hinge_pos.My, McMy_P=McMy, th_pP=hinge_pos.θpl, th_pcP=0.5*hinge_pos.θpl,
                                                    th_uP=4*hinge_pos.θpl,
                                                    My_N=-hinge_pos.My, McMy_N=McMy, th_pN=hinge_pos.θpl, th_pcN=0.5*hinge_pos.θpl,
                                                    th_uN=4*hinge_pos.θpl)


                beam_mIK_L.opensees_peak_py(index * 10 + 1, _nodeI, _extra_nodeI)
                self.tcl_file_text.append(beam_mIK_L.opensees_command_tcl(index * 10 + 1, _nodeI, _extra_nodeI) + f'   # beam {index} {reinforcement_name}.L')
                # print(f'{_nodeI}-{_extra_nodeI}:{reinforcement_name}Left Mypos={hinge_pos.My:.2f}  Myneg={hinge_neg.My:.2f}')

                # Right
                hinge_neg = self.model.reinforcement_beams_kanepe[f'{reinforcement_name}.R.neg']
                hinge_pos = self.model.reinforcement_beams_kanepe[f'{reinforcement_name}.R.pos']
                hinge_neg.calculate()
                hinge_pos.calculate()

                print(f'{index}: {reinforcement_name} Right:  My_P={hinge_pos.My}    My_N={-hinge_neg.My}')


                if self.inelastic_analysis_type != 'pushover':
                    beam_mIK_R = ModifiedIbarraKrawinkler(n=n_mIK, E=Ec, I=Iz, L=length,
                                                    My_P=hinge_pos.My, McMy_P=McMy, th_pP=hinge_pos.θpl, th_pcP=0.5*hinge_pos.θpl,
                                                    th_uP=4*hinge_pos.θpl,
                                                    My_N=-hinge_neg.My, McMy_N=McMy, th_pN=hinge_neg.θpl, th_pcN=0.5*hinge_neg.θpl,
                                                    th_uN=4*hinge_neg.θpl)
                else:
                    beam_mIK_R = ModifiedIbarraKrawinkler(n=n_mIK, E=Ec, I=Iz, L=length,
                                                    My_P=hinge_neg.My, McMy_P=McMy, th_pP=hinge_neg.θpl, th_pcP=0.5*hinge_neg.θpl,
                                                    th_uP=4*hinge_neg.θpl,
                                                    My_N=-hinge_neg.My, McMy_N=McMy, th_pN=hinge_neg.θpl, th_pcN=0.5*hinge_neg.θpl,
                                                    th_uN=4*hinge_neg.θpl)

                beam_mIK_R.opensees_peak_py(index * 10 + 2, _nodeJ , _extra_nodeJ)
                self.tcl_file_text.append(beam_mIK_R.opensees_command_tcl(index * 10 + 2, _nodeJ, _extra_nodeJ) + f'   # beam {index} {reinforcement_name}.R')
                # print(f'{_nodeJ}-{_extra_nodeJ}:{reinforcement_name}Right Mypos={hinge_pos.My:.2f}  Myneg={hinge_neg.My:.2f}')


            if 'COLUMN' in str(row['ElementType']):
                col = RectangularSectionGeometry(b=bw, h=h)
                Iz = col.moment_of_inertia_xx * mf_mom
                _extra_nodeI = 10 * _nodeI + 1
                _extra_nodeJ = 10 * _nodeJ + 3

                hinge = self.model.reinforcement_columns_kanepe[f'{reinforcement_name}']
                hinge.calculate()

                McMy = 1.001   # ratio of capping moment to yield moment, Mc / My

                col_mIK = ModifiedIbarraKrawinkler(n=n_mIK, E=Ec, I=Iz, L=length,
                                                    My_P=hinge.My, McMy_P=McMy, th_pP=hinge.θpl, th_pcP=0.5*hinge.θpl,
                                                    th_uP=4*hinge.θpl,
                                                    My_N=-hinge.My, McMy_N=McMy, th_pN=hinge.θpl, th_pcN=0.5*hinge.θpl,
                                                    th_uN=4*hinge.θpl)

                # Bottom
                col_mIK.opensees_peak_py(index * 10 + 1, _nodeI, _extra_nodeI)
                self.tcl_file_text.append(col_mIK.opensees_command_tcl(index * 10 + 1, _nodeI, _extra_nodeI) + f'   # col {index} {reinforcement_name}.Bot')
                # print(f'{_nodeI}-{_extra_nodeI}:{reinforcement_name} My={hinge.My:.2f}')
                # Top
                col_mIK.opensees_peak_py(index * 10 + 2, _nodeJ, _extra_nodeJ)
                self.tcl_file_text.append(col_mIK.opensees_command_tcl(index * 10 + 2, _extra_nodeJ, _nodeJ) + f'   # col {index} {reinforcement_name}.Top')
                # print(f'{_nodeJ}-{_extra_nodeJ}:{reinforcement_name} My={hinge.My:.2f}')


    def _os_eigen_analysis(self):
        numEigen = self.model.stories_total
        eigenValues = opensees.eigen('-fullGenLapack', numEigen)

        _periods = []
        _eigenvectors = []
        for i in range(0, numEigen):
            lamb = eigenValues[i]
            period = 2 * math.pi / math.sqrt(lamb)
            _periods.append(period)
            print(f'Period {i+1} = {period:.4f}s')

            eigen = []
            for mn in self.model.master_nodes:
                # print(f'eigen {i} mn {mn}')
                eigen.append(opensees.nodeEigenvector(mn, i+1, 1))
            _eigenvectors.append(eigen)


        self.tcl_file_text.append('')
        self.tcl_file_text.append(
            '# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# E I G E N V A L U S   A N A L Y S I S   -   C A L C U L A T E   P E R I O D S')
        self.tcl_file_text.append(
            '# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append(f'eigen -fullGenLapack {numEigen}')
        self.tcl_file_text.append(f'set numModes {numEigen}')
        self.tcl_file_text.append(f'set lambda [eigen -fullGenLapack $numModes]')
        self.tcl_file_text.append(f'puts Periods')
        self.tcl_file_text.append('foreach lam $lambda {')
        self.tcl_file_text.append(f'    puts [expr 6.283185/sqrt($lam)]')
        self.tcl_file_text.append('}')

        return _periods, _eigenvectors

    def _os_gravity_loads(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append(
            '# --------------------------------------------------------------------------------------------------------------')
        self.tcl_file_text.append('# G R A V I T Y    L O A D S')
        self.tcl_file_text.append(
            '# --------------------------------------------------------------------------------------------------------------')

        self.tcl_file_text.append('timeSeries Linear 1')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('pattern Plain 101 1 {')

        opensees.timeSeries('Linear', 1)
        opensees.pattern('Plain', 101, 1)
        self._os_nodal_loads()
        self._os_element_loads()

        if self.tcl_make == True:
            self.tcl_file_text.append('}')


    def _os_nodal_loads(self):
        ds = self.model.input_data['node_loads'] # .query('Storey>=1' )
        for index, row in ds.iterrows():
            _storey = row['Storey']
            _point_etabs = row['Point_Etabs']
            _node = row['NodeID']
            _G = float(row['G'])
            _Q = float(row['Q'])
            _loadZ = _G+0.3*_Q
            if _loadZ>0:
                opensees.load(_node, 0., -_loadZ, 0.)
                self.tcl_file_text.append(f'    load   {_node}   0.0    {-_loadZ:.2f}   0.0')



    def _os_element_loads(self):
        ds = self.model.input_data['beam_loads']
        for index, row in ds.iterrows():
            _ElementID  = int(row['ElementID'])
            _g = float(row['gΔ'])
            _q = float(row['qΔ'])
            _loadZ = _g + 0.3 * _q
            if _loadZ>0:
                opensees.eleLoad('-ele', _ElementID, '-type', '-beamUniform', -_loadZ)
                if self.tcl_make == True:
                    self.tcl_file_text.append(f'    eleLoad -ele {_ElementID} -type -beamUniform {-_loadZ:.2f}')



    def _os_run_gravity_elastic(self):


        opensees.system('BandGeneral')
        opensees.constraints('Plain')
        opensees.numberer('RCM')

        opensees.algorithm('Linear')
        opensees.integrator('LoadControl', 1.)
        opensees.analysis('Static')
        opensees.analyze(1)


        _df_elements = self.model.input_data['Elements']
        for index, row in _df_elements.iterrows():
            self.results.elastic_gravity_element_forces[index] = opensees.eleResponse(int(index), 'force', 1)
        opensees.wipe('all')



    def _os_run_push_grav(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# ---------------------------------')
        self.tcl_file_text.append('# Create Analysis for Gravity Loads')
        self.tcl_file_text.append('# ---------------------------------')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('constraints Plain;               # Create the constraint handler, a Plain handler is used as homo constraints')
        self.tcl_file_text.append('numberer RCM;                    # Create the DOF numberer, the reverse Cuthill-McKee algorithm')
        self.tcl_file_text.append('system BandGeneral;              # Create the system of equation, a SPD using a band storage scheme')
        self.tcl_file_text.append('test NormDispIncr 1.0e-6 6;      # Create the solution algorithm, a Linear algorithm is created')
        self.tcl_file_text.append('algorithm Newton;')
        self.tcl_file_text.append('integrator LoadControl 0.1;      # Create the integration scheme, the LoadControl scheme using steps of 1.0')
        self.tcl_file_text.append('analyses Static;                 # create the analyses object')
        self.tcl_file_text.append('analyze 10;                      # Perform Gravity Analysis')
        self.tcl_file_text.append('')
        self.tcl_file_text.append('recorder Element -file EleForces.out -ele 1211 1221 1231 1241 forces')
        self.tcl_file_text.append('record')
        self.tcl_file_text.append('exit')

        opensees.constraints('Plain')
        opensees.numberer('RCM')
        opensees.system('BandGeneral')
        opensees.test('NormDispIncr', 1e-6, 6)
        opensees.algorithm('Newton')
        opensees.integrator('LoadControl', 0.1)
        opensees.analysis('Static')
        opensees.analyze(10)

        opensees.loadConst('-time', 0.0)

        print('Some gravity analyses results')
        print(opensees.nodeDisp(106))
        print(opensees.eleForce(1111))


    def _os_run_pushover(self):
        self.tcl_file_text.append('')
        self.tcl_file_text.append('# ---------------------------------')
        self.tcl_file_text.append('# Create Pushover Analysis')
        self.tcl_file_text.append('# ---------------------------------')
        self.tcl_file_text.append('')

        _df_nodes = self.model.input_data['Nodes']
        _df_elements = self.model.input_data['Elements']

        roof_node = max(self.model.master_nodes)

        opensees.recorder('Node', '-file', 'droof.out', '-node', roof_node, '-dof', 1, 'disp')
        opensees.recorder('Node', '-file', 'Vbase.out', '-node', 1011, 1021, 1031, 1041, '-dof', 1, 'reaction')

        # Ακόμα και αν δεν τυπώνω σε αρχείο, πρέπει να τρέχει το recorder για να βγάλει τις λίστες...γιατί όμως;;
        # Δεν είναι ανάγκη να υπάρχουν όλοι οι κόμβοι, φτάνει ένας, ακόμα και αν δεν είναι από αυτούς που ζητώ στη συνέχεια
        opensees.recorder('Node', '-file', 'base_level_nodes.out', '-node', self.model.base_level_nodes[0], '-dof', 1, 'reaction')

        opensees.timeSeries('Linear', 2)
        opensees.pattern('Plain', 200, 2)
        for node in self.model.master_nodes:
            opensees.load(node, 1.0, 0., 0.)

        # opensees.constraints('Plain')
        opensees.numberer('RCM')
        opensees.system('UmfPack')
        opensees.test('NormDispIncr', 1e-6, 2000)
        opensees.algorithm('Newton')
        opensees.integrator('DisplacementControl', roof_node, 1, 0.0001)
        opensees.analysis('Static')

        roof_displacements = [0]
        base_shears = [0]
        for index, row in _df_elements.iterrows():
            self.results.pushover_element_deformation[index * 10 + 1] = []
            self.results.pushover_element_deformation[index * 10 + 2] = []
            self.results.pushover_element_force[index * 10 + 1] = []
            self.results.pushover_element_force[index * 10 + 2] = []

        ok = 0
        currentDisp = 0.0
        while ok == 0 and currentDisp < 0.1 * max(self.model.storey_levels):
            ok = opensees.analyze(1)
            # if the analyses fails try initial tangent __iteration
            if ok != 0:
                print("modified newton failed")
                # break
                print("regular newton failed .. lets try an KrylovNewton for this step")
                opensees.test('NormDispIncr', 1.0e-6,  1000)
                opensees.algorithm('KrylovNewton')
                ok = opensees.analyze(1)
                if ok == 0:
                    print("that worked .. back to regular newton")
                    opensees.test('NormDispIncr', 1e-6, 1000)
                    opensees.algorithm('Newton')


            currentDisp = opensees.nodeDisp(roof_node, 1)
            roof_displacements.append(currentDisp)

            for index, row in _df_elements.iterrows():
                self.results.pushover_element_deformation[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'deformation', 1))
                self.results.pushover_element_deformation[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'deformation', 1))
                self.results.pushover_element_force[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'force', 1)[5])
                self.results.pushover_element_force[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'force', 1)[5])




            _base_shear_tmp = 0.
            for i in self.model.base_level_nodes:
                _base_shear_tmp += opensees.nodeReaction(int(i)*10+1, 1)
            base_shears.append(_base_shear_tmp)


        # self.results_test['base_shears']= base_shears
        # self.results_test['roof_displacements']= roof_displacements

        # print(base_shears)
        # print(self.results_test['base_shears'])


        # print(elem_12221_mom)
        # print(elem_12221_rot)

            # print(f'δ={currentDisp} ok={ok}')
        # opensees.analyze(1500)
        # print(roof_displacements)
        # print(base_shears)

        etabs_curve = pd.read_csv(self.etabs_pushocer_curve_check, skiprows=7,
                                  sep='\s+')
        etabs_d = etabs_curve['Displacement'].tolist()
        etabs_V = etabs_curve['Base'].tolist()

        f, ax = plt.subplots(figsize=(8, 5))
        ax.plot(roof_displacements, -np.array(base_shears), label="opensees", lw=2)
        ax.plot(etabs_d, etabs_V, label="etabs", lw=2)
        # ax.axis([0, 1.3 * max(roof_displacements), 0, 1.2 * max(base_shears)])
        ax.set_title('Καμπύλη αντίστασης')
        ax.set_ylabel('V (kN)')
        ax.set_xlabel('δ (m)')
        ax.legend()
        fig = (f, ax)
        plt.show()

        # f, ax = plt.subplots(figsize=(8, 5))
        # ax.plot(elem_12221_rot, elem_12221_mom, label="M - rot", lw=2)
        # # ax.axis([0, 1.3 * max(roof_displacements), 0, 1.2 * max(base_shears)])
        # ax.set_title('Καμπύλη αντίστασης')
        # ax.set_ylabel('V (kN)')
        # ax.set_xlabel('δ (m)')
        # ax.legend()
        # fig = (f, ax)
        # plt.show()

        # print('Some pushover results')
        # print(opensees.nodeDisp(106))
        # print(opensees.eleForce(1111))


        # VsRecords = np.genfromtxt('Vbase.out', delimiter=' ', skip_footer=1).transpose()
        # Vs = VsRecords.sum(0)
        #
        # print(Vs)
        #
        # droofRecords = np.genfromtxt('droof.out', delimiter=' ', skip_footer=1)#.transpose()
        # droofs = droofRecords[0]

        # import csv
        # VsRecords = pd.read_csv('Vbase.out')
        # droofRecords = pd.read_table('droof.out', quoting=csv.QUOTE_NONE, error_bad_lines=False)
        #
        # print(droofRecords)

        # print(len(Vs))
        # print(len(droofRecords))

        # no_rows = min(len(droofs), len(Vs))

        # fig, ax = plt.subplots(figsize=(10, 7))
        # # ax.plot(droofs[:no_rows], -Vs[:no_rows])
        # ax.plot(droofRecords, -Vs)
        # ax.set(xlabel='δ roof (m)', ylabel='Base shear (kN)',
        #        title='Pushover curve')
        # ax.grid()
        # plt.show()


        opensees.wipe('all')


    def __os_run_time_history(self):

        _df_nodes = self.model.input_data['Nodes']
        _df_elements = self.model.input_data['Elements']

        roof_node = max(self.model.master_nodes)


        # w1 = 2*math.pi / 0.4
        # w2 = 2*math.pi / 0.2

        n_mIK = 10.

        w1 = 2*math.pi / self.results.elastic_periods[0]
        w2 = 2 * math.pi / self.results.elastic_periods[1]

        zeta = 0.04
        a0 = zeta*2.0*w1*w2/(w1+w2)
        a1 = zeta * 2.0 / (w1+w2)
        a1_mod = a1*(1.0+n_mIK)/n_mIK

        # elelist = _df_elements.index.tolist()
        # opensees.region(1, '-eleRange', elelist[0], elelist[-1], '-rayleigh', 0.0, 0.0, a1_mod, 0.0)
        # for mn in self.master_nodes:



        opensees.rayleigh(a0, 0.0, 0.0, a1_mod)



        opensees.recorder('Node', '-file', 'droof.out', '-node', roof_node, '-dof', 1, 'disp')
        opensees.recorder('Node', '-file', 'Vbase.out', '-node', 1011, 1021, 1031, 1041, '-dof', 1, 'reaction')

        # Ακόμα και αν δεν τυπώνω σε αρχείο, πρέπει να τρέχει το recorder για να βγάλει τις λίστες...γιατί όμως;;
        # Δεν είναι ανάγκη να υπάρχουν όλοι οι κόμβοι, φτάνει ένας, ακόμα και αν δεν είναι από αυτούς που ζητώ στη συνέχεια
        opensees.recorder('Node', '-file', 'base_level_nodes.out', '-node', self.model.base_level_nodes[0], '-dof', 1, 'reaction')




        # Set some parameters
        record = 'elCentro'

        # Permform the conversion from SMD record to OpenSees record
        dt, nPts = ReadRecord(record + '.at2', record + '.dat')


        # Set time series to be passed to uniform excitation
        opensees.timeSeries('Path', 2, '-filePath', record + '.dat', '-dt', dt, '-factor', 6.*9.81)

        # Create UniformExcitation load pattern
        #                         tag dir
        opensees.pattern('UniformExcitation', 2, 1, '-accel', 2)

        print("zzz3")

        opensees.wipeAnalysis()
        opensees.pattern('Plain', 200, 2)
        opensees.constraints('Plain')
        opensees.numberer('RCM')
        opensees.system('UmfPack')
        opensees.test('NormDispIncr', 1e-5, 5500)
        opensees.algorithm('NewtonLineSearch')
        opensees.integrator('Newmark', 0.5, 0.25)
        opensees.analysis('Transient')



        roof_displacements = [0]
        base_shears = [0]
        for index, row in _df_elements.iterrows():
            self.results.pushover_element_deformation[index * 10 + 1] = []
            self.results.pushover_element_deformation[index * 10 + 2] = []
            self.results.pushover_element_force[index * 10 + 1] = []
            self.results.pushover_element_force[index * 10 + 2] = []

        tFinal = nPts * dt
        tCurrent = opensees.getTime()

        ok = 0
        time = [tCurrent]
        u3 = [0.0]

        # Perform the transient analyses
        while ok == 0 and tCurrent < tFinal:

            ok = opensees.analyze(1, .001)

            # if the analyses fails try initial tangent __iteration
            if ok != 0:
                print("regular newton failed .. lets try an initail stiffness for this step")
                opensees.test('NormDispIncr', 1.0e-5, 5500)
                opensees.algorithm('ModifiedNewton', '-initial')
                ok = opensees.analyze(1, .001)
                if ok == 0:
                    print("that worked .. back to regular newton")
                opensees.test('NormDispIncr', 1.0e-5, 5500)
                opensees.algorithm('NewtonLineSearch')

            tCurrent =opensees.getTime()

            time.append(tCurrent)
            u3.append(opensees.nodeDisp(109, 1))

            currentDisp = opensees.nodeDisp(roof_node, 1)
            roof_displacements.append(currentDisp)

            for index, row in _df_elements.iterrows():
                self.results.pushover_element_deformation[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'deformation', 1))
                self.results.pushover_element_deformation[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'deformation', 1))
                self.results.pushover_element_force[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'force', 1)[5])
                self.results.pushover_element_force[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'force', 1)[5])

            print(tCurrent)



        print("zz4z")
        # ok = 0
        # currentDisp = 0.0
        # while ok == 0:
        #     ok = opensees.analyze(1, dt)
        #     # if the analyses fails try initial tangent __iteration
        #     if ok != 0:
        #         print("modified newton failed")
        #         # break
        #         print("regular newton failed .. lets try an KrylovNewton for this step")
        #         opensees.test('NormDispIncr', 1.0e-5,  1500)
        #         opensees.algorithm('KrylovNewton')
        #         ok = opensees.analyze(1, dt)
        #         if ok == 0:
        #             print("that worked .. back to regular NewtonLineSearch")
        #             opensees.test('NormDispIncr', 1e-5, 1500)
        #             opensees.algorithm('NewtonLineSearch')
        #
        #
        #     currentDisp = opensees.nodeDisp(roof_node, 1)
        #     roof_displacements.append(currentDisp)
        #
        #     for index, row in _df_elements.iterrows():
        #         self.results.pushover_element_deformation[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'deformation', 1))
        #         self.results.pushover_element_deformation[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'deformation', 1))
        #         self.results.pushover_element_force[index * 10 + 1].append(opensees.eleResponse(int(index * 10 + 1), 'force', 1)[5])
        #         self.results.pushover_element_force[index * 10 + 2].append(opensees.eleResponse(int(index * 10 + 2), 'force', 1)[5])
        #
        #
        #
        #
        #     _base_shear_tmp = 0.
        #     for i in self.base_level_nodes:
        #         _base_shear_tmp += opensees.nodeReaction(int(i)*10+1, 1)
        #     base_shears.append(_base_shear_tmp)






    def save_results(self):
        file = open('results.pickled', 'wb')
        # dump information to that file
        pickle.dump(self, file)
        # close the file
        file.close()

        f = gzip.open('results.gzpickled', 'wb', compresslevel=9)
        pickle.dump(self, f)
        f.close()












