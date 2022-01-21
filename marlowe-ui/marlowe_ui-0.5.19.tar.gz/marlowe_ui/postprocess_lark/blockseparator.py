'''blockseperation.py
seperate int large blocks for detail parsing

input data will be seperated to

  initial_config(1):
    starts with: MARLOWE: Atomic Collisions ...
    ends with: Initial State of RANX = ...

  cascade(+):
    starts with: Cascade{d6}:     Group{d5}     Number{d3}

    cascade_summary(1):
        starts with: "Cascade{d6}:     Group{d5}     Number{d3}"

    cascade_detail_initial_defect(?):
        starts with: "The Initial Defect Lattice Sites"

        cascade_detail_initial_defect_lattice:
            starts with: "The Initial Defect Lattice Sites"

        cascade_detail_initial_defect_atom:
            starts with: "The Initial Defect Atoms"

    cascade_detail_projectile(1):
        starts with "Projectile before Collision ..."

    cascade_report_summary(1):
        starts with: "Summary of Cascade<int>:     Group<int>     Number<int>"

    cascade_report_atom(+):
        starts with: "Cascade Summary for ELEM atoms"

    cascade_report_detail(?):
        starts with: "Detailed Description of the Cascade, Part 1 of 3"
        cascade_report_detai_1(1):
            starts with: "Detailed Description of the Cascade, Part 1 of 3"
        cascade_report_detai_2(1):
            starts with: "Detailed Description of the Cascade, Part 2 of 3"
        cascade_report_detai_3(1):
            starts with: "Detailed Description of the Cascade, Part 3 of 3"

    cascade_report_lattice_sites(?)
        starts with: "Locations of the Cascade Lattice Sites"

    cascade_rangex(?):
        starts with:
            ELEM "Primary Recoil Ranges" |
            "The" ELEM "primary escaped through the (front|back|side|other) "surface at" pfloat "fs"

    cascade_sequin(?):
        starts with: "No focuson events were found" | "The Final States of 'Focuson' Sequences"

    cascade_orgiv(?):
        starts with: "No distant vacancy-interstitial pairs found"
            | "Separations of Distant Interstitial-Vacancy Pairs"

    cascade_end(1):
        "Computation time  0.000     seconds      Cascade storage    61"
        "Final state of RANX =  22805,   2560,  24301,      0"

  final(1):
    starts with: r'Analysis of Primary Recoil Ranges \(\s*\d+ Stopped Particles\)'
    final_rangex(1):
        starts with: r'Analysis of Primary Recoil Ranges \(\s*\d+ Stopped Particles\)'

    final_slavex(1):
        starts with: "Statistical Analysis of Data from {d} cascades"

    final_slavex_atom(*):
        starts with: "Statistical Analysis of Data for" _S ELEM _S "Atoms in" _S pint _S "Cascades"

    final_sequex(1):
        starts with: "The Final States of 'Focuson' Sequences" | "No focuson events were found"

    final_orgex(1):
        starts with; "Proper Pairs:   Correlated Distant Frenkel Pair Separations (channel width 0.25000    )"

    summary_end(1):
        Computation time  1.250     seconds      Maximum cascade storage    72
        Final state of RANX =  20013,  25802,  14143,      7

  end(1):
    "End of program: total time  1.250    seconds

'''

import io
import re
import pathlib
import csv
import json
import math

from . import linereducer

from . import initial_config
from . import cascade_summary
from . import cascade_detail_projectile
from . import cascade_report_summary
from . import cascade_report_atom
from . import cascade_report_detail_1
from . import cascade_report_detail_2
from . import cascade_report_detail_3
from . import cascade_report_lattice_sites
from . import cascade_ranger
from . import cascade_sequin
from . import cascade_orgiv
from . import final_rangex
from . import final_slavex
from . import final_slavex_atom
from . import final_sequex
from . import final_orgex

from . import csv_header
from . import output_dir

import logging
logger = logging.getLogger(__name__)

class SyntaxError(Exception):
    pass

class BaseState():
    name = 'base'
    next_states = []

    def __init__(self, context=None):
        self.context = context

    def startswith(self, line):
        '''condition to enter this section'''
        return True

    def next(self, line):
        for next_state in self.next_states:
            if next_state.startswith(line):
                return next_state
        # other case, stay at this state
        return None


    def on_enter(self, startline):
        '''called when the state is initiated, the self.context may be modified
        startline: the stripped line object, which satisfies self.startswith() condition
        '''
        logger.debug(f'block:{self.name}:on_enter')

    def on_exit(self):
        '''called when the state is closed, the self.context may be modified''' 
        logger.debug(f'block:{self.name}:on_exit')


    def on_stay_state(self, line):
        '''called when the state stays at the same one
        line: the stripped line object'''
        logger.debug(f'block:{self.name}:on_stay_state')


class RootBaseState(BaseState):
    def on_enter(self, startline):
        super().on_enter(startline)
        self.textbuf = io.StringIO()

    def on_stay_state(self, line):
        super().on_stay_state(line)
        self.textbuf.write(f'{line:s}\n')
    
    def on_exit(self):
        super().on_exit()
        # output text  
        output = self.context.outputdir / self.context.config_block_file_form.format(blockname=self.name)

        output.open('wt').write(self.textbuf.getvalue())


class CascadeBaseState(BaseState):
    def on_enter(self, startline):
        super().on_enter(startline)
        self.textbuf = io.StringIO()

    def on_stay_state(self, line):
        super().on_stay_state(line)
        self.textbuf.write(f'{line:s}\n')
    
    def on_exit(self):
        super().on_exit()
        # output text  
        output = self.context.cascadedir / self.context.config_block_file_form.format(blockname=self.name)

        output.open('wt').write(self.textbuf.getvalue())


class Initial(BaseState):
    name = 'initial'

class InitialConfig(RootBaseState):
    name = 'initial_config'

    def startswith(self, line):
        match = re.compile(r'MARLOWE: Atomic Collisions in Solids in the Binary Collision Approximation')
        return match.fullmatch(line)

    def on_enter(self, line):
        super().on_enter(line)
        logger.info(f'block:{self.name}') 

    def on_exit(self):
        # dump text
        super().on_exit()

        # parse initial_config block and set result
        self.context.initial_config = initial_config.parse(self.textbuf.getvalue())

        # save as initial_config.json file
        self.context.on_initial_end()

class Cascade(BaseState):
    name = 'cascade'
    # cascade/detail.mfs DETL2930
    match = re.compile(r'Cascade\s*(?P<Cascade>\d+):\s{5}Group\s*(?P<Group>\d+)\s{6}Number\s*(?P<Number>\d+)')

    def startswith(self, line):
        return self.match.fullmatch(line)

    def on_enter(self, line):
        super().on_enter(line)
        m = self.match.fullmatch(line)

        # set cascade_index and create cascade dir
        self.context.init_cascade_contexts(int(m.group('Cascade')), int(m.group('Group')), int(m.group('Number')))
        logger.info('block:cascade({Cascade}, {Group}, {Number})'.format(**self.context.cascade_index))


class CascadeSummary(CascadeBaseState):
    name = 'cascade_summary'
    # cascade/detail.mfs DETL2930
    match = re.compile(r'Cascade\s*\d+:\s{5}Group\s*\d+\s{6}Number\s*\d+')

    def startswith(self, line):
        return self.match.fullmatch(line)

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_summary = cascade_summary.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_summary = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeDetailInitialDefect(BaseState):
    name = 'cascade_detail_initial_defect'

    header1 = 'The Initial Defect Lattice Sites'

    def startswith(self, line):
        return line == self.header1

class CascadeDetailInitialDefectLattice(CascadeBaseState):
    name = 'cascade_detail_initial_defect_lattice'

    header1 = CascadeDetailInitialDefect.header1
    header2 = 'File    Site            ...........Location...........          Paired Atom'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        # create .csv output file
        self.csv_output = csv.writer(
            (self.context.cascadedir / 'initial_defect_lattice.csv').open('w', newline=''))
        self.csv_output.writerow(csv_header.cascade_detail_initial_defect_lattice)

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            self.csv_output.writerow(line.split())

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        del self.csv_output

class CascadeDetailInitialDefectAtom(CascadeBaseState):
    name = 'cascade_detail_initial_defect_atom'

    header1 = 'The Initial Defect Atoms'
    header2 = 'File  Atom    KARMA           .....Initial Atom Location....               ....Reference Lattice Site....        Site'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        # create .csv output file
        self.csv_output = csv.writer(
            (self.context.cascadedir / 'initial_defect_atom.csv').open('w', newline=''))
        self.csv_output.writerow(csv_header.cascade_detail_initial_defect_atom)

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            self.csv_output.writerow(line.split())

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        del self.csv_output

class CascadeDetailProjectile(CascadeBaseState):
    name = 'cascade_detail_projectile'

    def startswith(self, line):
        return line.startswith('Projectile Before Collision')

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_detail_projectile = cascade_detail_projectile.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_detail_projectile = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeReportSummary(CascadeBaseState):
    name = 'cascade_report_summary'

    def startswith(self, line):
        return line.startswith('Summary of Cascade')

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_report_summary = cascade_report_summary.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_report_summary = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeReportAtom(CascadeBaseState):
    name = 'cascade_report_atom'
    def startswith(self, line):
        match = re.compile(r'Cascade Summary for\s+(?P<ELEM>\w+)\s+atoms' )
        return match.fullmatch(line)

    def on_exit(self):
        # dump text
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_report_atom = cascade_report_atom.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_report_atom = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeReportDetail(BaseState):
    name = 'cascade_report_detail'

    header = 'Detailed Description of the Cascade, Part 1 of 3'

    def startswith(self, line):
        return line == self.header

class CascadeReportDetail1(CascadeBaseState):
    name = 'cascade_report_detail_1'

    header1 = CascadeReportDetail.header
    header2 = 'File   Atom   KARMA   Initial Time   Initial Energy           ......Initial Location......          Site   TRAK   NSEQ'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        self.context.cascade_report_detail_1 = []

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            sp = line.split()
            self.context.cascade_report_detail_1.append(
                    [
                        int(sp[0]),
                        sp[1],
                        int(sp[2]),
                        float(sp[3]), float(sp[4]),
                        float(sp[5]), float(sp[6]), float(sp[7]),
                        int(sp[8]),
                        int(sp[9]),
                        int(sp[10])])

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

class CascadeReportDetail2(CascadeBaseState):
    name = 'cascade_report_detail_2'

    header1 = 'Detailed Description of the Cascade, Part 2 of 3'
    header2 = 'File   Atom    KARMA      Final Time       Final Energy            ...Final Direction Cosines....'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        self.context.cascade_report_detail_2 = []

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            sp = line.split()
            self.context.cascade_report_detail_2.append(
                    [
                        int(sp[0]),
                        sp[1],
                        int(sp[2]),
                        float(sp[3]), float(sp[4]),
                        float(sp[5]), float(sp[6]), float(sp[7])])

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

class CascadeReportDetail3(CascadeBaseState):
    name = 'cascade_report_detail_3'

    header1 = 'Detailed Description of the Cascade, Part 3 of 3'
    header2 = 'File   Atom    KARMA           ........Final Location........               ....Reference Lattice Site....        Site'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        self.context.cascade_report_detail_3 = []

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            sp = line.split()
            self.context.cascade_report_detail_3.append(
                    [
                        int(sp[0]),
                        sp[1],
                        int(sp[2]),
                        float(sp[3]), float(sp[4]), float(sp[5]),
                        float(sp[6]), float(sp[7]), float(sp[8]),
                        int(sp[9])])

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

class CascadeReportLatticeSites(CascadeBaseState):
    name = 'cascade_report_lattice_sites'

    header1 = 'Locations of the Cascade Lattice Sites'
    header2 = 'File    Site            ...........Location...........          Paired Atom'

    def startswith(self, line):
        return line == self.header1

    def on_enter(self, line):
        if self.context.config_dump_text_blocks:
            super().on_enter(line)

        self.context.cascade_report_lattice_sites = []

    def on_stay_state(self, line):
        if self.context.config_dump_text_blocks:
            super().on_stay_state(line)

        if line != self.header1 and line != self.header2:
            sp = line.split()
            self.context.cascade_report_lattice_sites.append(
                    [
                        int(sp[0]),
                        int(sp[1]),
                        float(sp[2]), float(sp[3]), float(sp[4]),
                        int(sp[5])
                        ])

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


class CascadeRanger(CascadeBaseState):
    name = 'cascade_ranger'
    def startswith(self, line):
        match1 = re.compile(r'(?P<ELEM>\w+)\s+Primary Recoil Ranges' )
        m = match1.fullmatch(line)
        if m:
            return m
        match2 = re.compile(r'The\s+(?P<ELEM>\w+)\s+primary escaped through the' )
        return match2.match(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_ranger = cascade_ranger.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_ranger = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e

class CascadeSequin(CascadeBaseState):
    name = 'cascade_sequin'
    def startswith(self, line):
        return line == 'No focuson events were found' or line == "The Final States of 'Focuson' Sequences"

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


        # parse block-separated text
        try:
            self.context.cascade_sequin = cascade_sequin.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_sequin = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeOrgiv(CascadeBaseState):
    name = 'cascade_orgiv'
    def startswith(self, line):
        return line == 'No distant vacancy-interstitial pairs found' or\
            line == 'Separations of Distant Interstitial-Vacancy Pairs'

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.cascade_orgiv = cascade_orgiv.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.cascade_orgiv = {}
                logging.warning(f'Parse error occured in "{self.name} - {self.context.cascade_index_text}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class CascadeEnd(BaseState):
    name = 'cascade_end'

    def startswith(self, line):
        match = re.compile(r'Computation time\s+([0-9]*[.])?[0-9]+([eE][-+]?\d+)?\s+(seconds|minutes|hours|days)\s+Cascade storage(\s*\d+|\*{6})')
        return match.fullmatch(line)

    def on_exit(self):
        self.context.on_cascade_end()


class Final(BaseState):
    name = 'final'
    def startswith(self, line):
        match = re.compile(r'Analysis of Primary Recoil Ranges \(\s*\d+ Stopped Particles\)')
        return match.fullmatch(line)

    def on_enter(self, line):
        super().on_enter(line)
        logger.info(f'block:{self.name}') 


class FinalRangex(RootBaseState):
    name = 'final_rangex'
    def startswith(self, line):
        match = re.compile(r'Analysis of Primary Recoil Ranges \(\s*\d+ Stopped Particles\)')
        return match.fullmatch(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


        # parse block-separated text
        try:
            self.context.final_rangex = final_rangex.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.final_rangex = {}
                logging.warning(f'Parse error occured in "{self.name}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e

class FinalSlavex(RootBaseState):
    name = 'final_slavex'
    def startswith(self, line):
        match = re.compile(r'Statistical Analysis of Data from\s+\d+\s+Cascades')
        return match.fullmatch(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


        # parse block-separated text
        try:
            self.context.final_slavex = final_slavex.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.final_slavex = {}
                logging.warning(f'Parse error occured in "{self.name}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e


class FinalSlavexAtom(RootBaseState):
    name = 'final_slavex_atom'
    def startswith(self, line):
        match = re.compile(r'Statistical Analysis of Data for\s+\w+\s+Atoms in\s+\d+\s+Cascades')
        return match.fullmatch(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


        # parse block-separated text
        try:
            self.context.final_slavex_atom = final_slavex_atom.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.final_slavex_atom = {}
                logging.warning(f'Parse error occured in "{self.name}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e

class FinalSequex(RootBaseState):
    name = 'final_sequex'
    def startswith(self, line):
        return line == "The Final States of 'Focuson' Sequences" or\
                line == "No focuson events were found"

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()


        # parse block-separated text
        try:
            self.context.final_sequex = final_sequex.parse(self.textbuf.getvalue(),
                    self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.final_sequex = {}
                logging.warning(f'Parse error occured in "{self.name}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e

class FinalOrgex(RootBaseState):
    name = 'final_orgex'
    def startswith(self, line):
        match = re.compile(r'(P|Imp)roper Pairs:\s+(Unc|C)orrelated Distant\s+(Frenkel|Surface)\s+Pair Separations \(channel width\s+([0-9]*[.])?[0-9]+([eE][-+]?\d+)?\s+\)')
        return match.fullmatch(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()

        # parse block-separated text
        try:
            self.context.final_orgex = final_orgex.parse(self.textbuf.getvalue(), self.context.config_debug_parser)
        except Exception as e:
            if self.context.config_ignore_block_parse_error:
                self.context.final_orgex = {}
                logging.warning(f'Parse error occured in "{self.name}", but continued.')
                logging.warning(str(e), exc_info=True)
                pass
            else:
                raise e

class FinalEnd(RootBaseState):
    name = 'final_end'

    def startswith(self, line):
        match = re.compile(r'Computation time\s+([0-9]*[.])?[0-9]+([eE][-+]?\d+)?\s+(seconds|minutes|hours|days)\s+Maximum cascade storage(\s*\d+|\*{6})')
        return match.fullmatch(line)

    def on_exit(self):
        if self.context.config_dump_text_blocks:
            super().on_exit()
        self.context.on_final_end()


class End(BaseState):
    name = 'end'

    def startswith(self, line):
        match = re.compile(r'End of program:  total time\s+([0-9]*[.])?[0-9]+([eE][-+]?\d+)?\s+(seconds|minutes|hours|days)')
        return match.fullmatch(line)


class Context():
    
    def __init__(self, 
                outputdir,
                cascadedir_form='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
                config_dump_text_blocks=True,
                config_cascade_table_output='BOTH',
                config_ignore_block_parse_error=False,
                config_block_file_form='00.{blockname:s}.txt',
                config_debug_parser=False):
        """initialize parser
        outputdir: string or pathlib.Path object to save output data.
          If outputdir does not exist, try to create it.
        cascadedir_form: formmatable string to save data for each cascade
        config_dump_text_blocks: if True, 'as-is' text block is saved, otherwise skipped if it is not needed.
        config_cascade_table_output: chooses whether large output data generated at each cascade
            is written in one file ('BUNDLE'), in each cascade dir('SEPARATE'),  or both('BOTH')
        config_ignore_block_parse_error: if True, continue even an error occurs during parsing each block.
        config_block_file_form: is fileformat to output parsed block text
        """

        self.outputdir = outputdir

        # dumper options
        self.config_dump_text_blocks = config_dump_text_blocks
        self.config_cascade_table_output = config_cascade_table_output
        self.config_debug_parser = config_debug_parser
        self.config_block_file_form = config_block_file_form
        self.config_ignore_block_parse_error = config_ignore_block_parse_error

        # prepare output directory and files
        # output directory
        if not isinstance(outputdir, pathlib.Path):
            self.outputdir = pathlib.Path(self.outputdir)
        # prepare directory frame
        output_dir.prepare(self.outputdir)

        # cascade index
        self.cascade_index = {'Cascade':0, 'Group':0, 'Number':0}
        self.cascade_index_text = 'cascade(0, 0, 0)'
        self.csv_rowindex = [0, 0, 0]

        # directry to save each cascade data and summary
        self.cascadedir_form = cascadedir_form
        self.cascadedir = self.outputdir / self.cascadedir_form.format(**self.cascade_index)

        # cascade tables bundles all cascade data
        if self.config_cascade_table_output == 'SEPARATE':
            # no bundled cascade table
            self.file_cascade_report_detail_all = None
            self.csv_cascade_report_detail_all = None
            self.file_cascade_report_detail_primary_all = None
            self.csv_cascade_report_detail_primary_all = None
            self.file_cascade_report_lattice_sites_all = None
            self.csv_cascade_report_lattice_sites_all = None
            self.file_cascade_orgiv_all = None
            self.csv_cascade_orgiv_all = None
            self.file_cascade_ranger_all = None
            self.csv_cascade_ranger_all = None
        else: # 'BUNDLE' or 'BOTH'
            self.file_cascade_report_detail_all\
                    = (self.outputdir / 'description_of_cascade_all.csv').open('w', newline='')
            self.csv_cascade_report_detail_all = csv.writer(self.file_cascade_report_detail_all)
            self.csv_cascade_report_detail_all.writerow(csv_header.cascade_report_detail_all)

            self.file_cascade_report_detail_primary_all\
                    = (self.outputdir / 'description_of_cascade_primary_recoil_all.csv').open('w', newline='')
            self.csv_cascade_report_detail_primary_all = csv.writer(self.file_cascade_report_detail_primary_all)
            self.csv_cascade_report_detail_primary_all.writerow(csv_header.cascade_report_detail_all)


            self.file_cascade_report_lattice_sites_all\
                    = (self.outputdir / 'lattice_sites_all.csv').open('w', newline='')
            self.csv_cascade_report_lattice_sites_all = csv.writer(self.file_cascade_report_lattice_sites_all)
            self.csv_cascade_report_lattice_sites_all.writerow(csv_header.cascade_report_lattice_sites_all)

            self.file_cascade_orgiv_all = (self.outputdir / 'distant_iv_pairs_all.csv').open('w', newline='')
            self.csv_cascade_orgiv_all = csv.writer(self.file_cascade_orgiv_all)
            self.csv_cascade_orgiv_all.writerow(csv_header.cascade_orgiv_all)

            self.file_cascade_ranger_all = (self.outputdir / 'primary_recoil_ranges_all.csv').open('w', newline='')
            self.csv_cascade_ranger_all = csv.writer(self.file_cascade_ranger_all)
            self.csv_cascade_ranger_all.writerow(csv_header.cascade_ranger_all)

    def close_bundled_files_explicitly(self):
        '''explicitly close csv files, which are created on BUNDLE and BOTH mode'''
        if self.file_cascade_report_detail_all:
            self.file_cascade_report_detail_all.close()
        self.csv_cascade_report_detail_all = None

        if self.file_cascade_report_detail_primary_all:
            self.file_cascade_report_detail_primary_all.close()
        self.csv_cascade_report_detail_primary_all = None

        if self.file_cascade_report_lattice_sites_all:
            self.file_cascade_report_lattice_sites_all.close()
        self.csv_cascade_report_lattice_sites_all = None

        if self.file_cascade_orgiv_all:
            self.file_cascade_orgiv_all.close()
        self.csv_cascade_orgiv_all = None

        if self.file_cascade_ranger_all:
            self.file_cascade_ranger_all.close()
        self.csv_cascade_ranger_all = None

    # contexts durinng parsing cascade 
    def init_cascade_contexts(self, cascade, group, number):
        '''update cascade_index and cascadedir, then create cascadedir'''
        self.cascade_index = {
                'Cascade':cascade,
                'Group':group,
                'Number':number} 
        self.cascade_index_text = f'cascade({cascade:d}, {group:d}, {number:d})'
        self.csv_rowindex = [cascade, group, number]
        self.cascade_summary = None
        self.cascade_detail_projectile = None
        self.cascade_report_summary = None
        self.cascade_report_atom = None
        self.cascade_report_detail_1 = None
        self.cascade_report_detail_2 = None
        self.cascade_report_detail_3 = None
        self.cascade_report_lattice_sites = None
        self.cascade_sequin = None
        self.cascade_ranger = None
        self.cascade_orgiv = None

        self.cascadedir = self.outputdir / self.cascadedir_form.format(**self.cascade_index)
        if self.cascadedir.exists():
            if not self.cascadedir.is_dir():
                raise Error('{} exists but not directory'.format(self.cascadedir))
        else:
            self.cascadedir.mkdir()

    def on_cascade_end(self):
        # on exit cascade entry
        obj = self.cascade_summary
        obj['Projectile Before Collision'] = self.cascade_detail_projectile
        obj['Summary of Cascade'] = self.cascade_report_summary
        obj['Cascade Summary for each Atom'] = self.cascade_report_atom
        obj['Primary Recoil Ranges'] = self.cascade_ranger
        obj['Sequences'] = self.cascade_sequin
        with (self.cascadedir / 'cascade.json').open('wt') as f:
            json.dump(obj, f, indent=2)

        # create .csv files (bundled and seperated)
        self.output_csv_cascade_report_detail()
        self.output_csv_cascade_report_lattice_sites()
        self.output_csv_cascade_orgiv()
        self.output_csv_cascade_ranger()

    def output_csv_cascade_report_detail(self):
        cascade_report_detail_valid = self.cascade_report_detail_1 and self.cascade_report_detail_2 and\
                self.cascade_report_detail_3

        if not cascade_report_detail_valid:
            return

        # description_of_cascade_all
        primary_recoil_output = False
        if self.config_cascade_table_output != 'BUNDLE': # 'SEPARATE' or 'BOTH'
            csv_cascade_report_detail = csv.writer(
                (self.cascadedir / 'description_of_cascade.csv').open('w', newline=''))
            csv_cascade_report_detail.writerow(csv_header.cascade_report_detail_all)

            csv_cascade_report_detail_primary = csv.writer(
                (self.cascadedir / 'description_of_cascade_primary_recoil.csv').open('w', newline=''))
            csv_cascade_report_detail_primary.writerow(csv_header.cascade_report_detail_all)
        else:
            csv_cascade_report_detail = None
            csv_cascade_report_detail_primary = None

        for d1, d2, d3 in zip(self.cascade_report_detail_1,
                self.cascade_report_detail_2, self.cascade_report_detail_3):
            rowdata = self.csv_rowindex + d1 + d2[3:] + d3[3:]
            if self.csv_cascade_report_detail_all:
                self.csv_cascade_report_detail_all.writerow(rowdata)
            if csv_cascade_report_detail:
                csv_cascade_report_detail.writerow(rowdata)

            # output to primary recoil ('rec['File'] == 1') data only
            if not primary_recoil_output and d1[0] == self.cascade_detail_projectile['File']['Index']:
                primary_recoil_output = True
                if self.csv_cascade_report_detail_primary_all:
                    self.csv_cascade_report_detail_primary_all.writerow(rowdata)
                if csv_cascade_report_detail_primary:
                    csv_cascade_report_detail_primary.writerow(rowdata)

    def output_csv_cascade_report_lattice_sites(self):
        # cascade_report_lattice_sites_all
        if not self.cascade_report_lattice_sites:
            return

        if self.config_cascade_table_output != 'BUNDLE': # 'SEPARATE' or 'BOTH'
            csv_cascade_report_lattice_sites = csv.writer(
                (self.cascadedir / 'lattice_sites.csv').open('w', newline=''))
            csv_cascade_report_lattice_sites.writerow(csv_header.cascade_report_lattice_sites_all)
        else:
            csv_cascade_report_lattice_sites = None

        if self.cascade_report_detail_3:
            for d in self.cascade_report_lattice_sites:
                rowdata = self.csv_rowindex + d
                atomindex = d[5]
                if atomindex:
                    atomindex -= 1
                    final_atom = self.cascade_report_detail_3[atomindex][1]
                    final_x, final_y, final_z = self.cascade_report_detail_3[atomindex][3:6]
                    distance = math.sqrt(
                            (d[2] - final_x)**2
                            + (d[3] - final_y)**2
                            + (d[4] - final_z)**2)
                    rowdata += [final_atom, final_x, final_y, final_z, distance]
                else:
                    rowdata += [None]*7
                if self.csv_cascade_report_lattice_sites_all:
                    self.csv_cascade_report_lattice_sites_all.writerow(rowdata)
                if csv_cascade_report_lattice_sites:
                    csv_cascade_report_lattice_sites.writerow(rowdata)
        else:
            for d in self.cascade_report_lattice_sites:
                rowdata = self.csv_rowindex + d + [None]*7
                if self.csv_cascade_report_lattice_sites_all:
                    self.csv_cascade_report_lattice_sites_all.writerow(rowdata)
                if csv_cascade_report_lattice_sites:
                    csv_cascade_report_lattice_sites.writerow(rowdata)

    def output_csv_cascade_orgiv(self):
        # cascade_orgiv_all
        if self.cascade_orgiv.get('status', None) != 'valid':
            return 

        if self.config_cascade_table_output != 'BUNDLE': # 'SEPARATE' or 'BOTH'
            csv_cascade_orgiv = csv.writer(
                (self.cascadedir / 'distant_iv_pairs.csv').open('w', newline=''))
            csv_cascade_orgiv.writerow(csv_header.cascade_orgiv_all)
        else:
            csv_cascade_orgiv = None

        for d in self.cascade_orgiv['records']:
            vacfile = d[2]
            intfile = d[4]

            if vacfile and self.cascade_report_lattice_sites:
                vacrowdata = self.cascade_report_lattice_sites[vacfile-1][2:5]
            else:
                vacrowdata = [None]*3

            if intfile and self.cascade_report_detail_3:
                introwdata = self.cascade_report_detail_3[intfile-1][3:6]
            else:
                introwdata = [None]*3

            rowdata = self.csv_rowindex + d + vacrowdata + introwdata
            if self.csv_cascade_orgiv_all:
                self.csv_cascade_orgiv_all.writerow(rowdata)
            if csv_cascade_orgiv:
                csv_cascade_orgiv.writerow(rowdata)
        
    def output_csv_cascade_ranger(self):
        # cascade_ranger_all
        if not self.cascade_ranger:
            return

        range_ = self.cascade_ranger.get('Recoil Range', None)
        if not range_:
            return

        elem = self.cascade_ranger.get('Elem')
        rowdata = self.csv_rowindex + [elem,
                range_['Radial Range'], 
                range_['Penetration'],
                range_['Spread'],
                range_['Total Path'],
                range_['Slowing Down Time']]
        if self.csv_cascade_ranger_all:
            self.csv_cascade_ranger_all.writerow(rowdata)

        if self.config_cascade_table_output != 'BUNDLE': # 'SEPARATE' or 'BOTH'
            csv_cascade_ranger = csv.writer(
                (self.cascadedir / 'primary_recoil_ranges.csv').open('w', newline=''))
            csv_cascade_ranger.writerow(csv_header.cascade_ranger_all)
            csv_cascade_ranger.writerow(rowdata)

    def on_initial_end(self):
        obj = {
            'initial_config': self.initial_config
                }
        with (self.outputdir / 'initial.json').open('wt') as f:
            json.dump(obj, f, indent=2)


    def on_final_end(self):
        obj = {
            'initial_config': self.initial_config,
            'final_rangex': self.final_rangex,
            'final_slavex': self.final_slavex,
            'final_sequex': self.final_sequex,
            'final_orgex': self.final_orgex}
        obj['final_slavex']['final_slavex_atom'] = self.final_slavex_atom
        with (self.outputdir / 'summary.json').open('wt') as f:
            json.dump(obj, f, indent=2)

        # final_rangex
        if self.final_rangex and 'Analysis of Primary Recoil Ranges' in self.final_rangex:
            d = self.final_rangex.get('Analysis of Primary Recoil Ranges', None)
            count = [d['Stopped Particles']]
            with (self.outputdir / 'analysis_of_primary_recoil_ranges.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(csv_header.final_rangex)
                for k in ['Radial Range', 'Penetration', 'Spread', 'Total Path', 'Slowing Down Time',
                        'Front Escape Time']:
                    if k in d:
                        rowdata = [k] + [d[k][v] for v in csv_header.final_rangex[1:-1]] + count
                        fcsv.writerow(rowdata)

        # final_slavex (statistical number)
        if self.final_slavex and 'Statistical Analysis from Cascades' in self.final_slavex:
            d = self.final_slavex.get('Statistical Analysis from Cascades', None)
            count = [d['header']['Number of Cascades']]
            with (self.outputdir / 'statistical_analysis_of_data.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(csv_header.final_slavex_number)
                for k in d['data']:
                    rowdata = [k['label']] + [k[v] for v in csv_header.final_slavex_number[1:-1]] + count
                    fcsv.writerow(rowdata)


class BlockSeparator():

    def __init__(self, input_, context=None):
        # self context
        if context is None:
            self.context = self
        else:
            self.context = context

        # build up parser chain
        self.build_states()

        # set input stream
        self.linereducer = linereducer.LineReducer(input_, return_stripped=True)
        self.state = self.initial
        self.lineno, self.line = next(self.linereducer)
        self.no_eof = True

    def build_states(self):
        self.initial = Initial(self.context)
        self.initial_config = InitialConfig(self.context)
        self.cascade = Cascade(self.context)
        self.cascade_summary = CascadeSummary(self.context)
        self.cascade_detail_initial_defect = CascadeDetailInitialDefect(self.context)
        self.cascade_detail_initial_defect_lattice = CascadeDetailInitialDefectLattice(self.context)
        self.cascade_detail_initial_defect_atom = CascadeDetailInitialDefectAtom(self.context)
        self.cascade_detail_projectile = CascadeDetailProjectile(self.context)
        self.cascade_report_summary = CascadeReportSummary(self.context)
        self.cascade_report_atom = CascadeReportAtom(self.context)
        self.cascade_report_detail = CascadeReportDetail(self.context)
        self.cascade_report_detail_1 = CascadeReportDetail1(self.context)
        self.cascade_report_detail_2 = CascadeReportDetail2(self.context)
        self.cascade_report_detail_3 = CascadeReportDetail3(self.context)
        self.cascade_report_lattice_sites = CascadeReportLatticeSites(self.context)
        self.cascade_ranger = CascadeRanger(self.context)
        self.cascade_sequin = CascadeSequin(self.context)
        self.cascade_orgiv = CascadeOrgiv(self.context)
        self.cascade_end = CascadeEnd(self.context)
        self.final = Final(self.context)
        self.final_rangex = FinalRangex(self.context)
        self.final_slavex = FinalSlavex(self.context)
        self.final_slavex_atom = FinalSlavexAtom(self.context)
        self.final_sequex = FinalSequex(self.context)
        self.final_orgex = FinalOrgex(self.context)
        self.final_end = FinalEnd(self.context)
        self.end = End(self.context)

        self.initial.next_states = [self.initial_config]
        self.initial_config.next_states = [self.cascade]
        self.cascade.next_states = [self.cascade_summary]
        self.cascade_summary.next_states = [
                self.cascade_detail_initial_defect,
                self.cascade_detail_projectile]
        self.cascade_detail_initial_defect.next_states = [
                self.cascade_detail_initial_defect_lattice,
                self.cascade_detail_initial_defect_atom,
                self.cascade_detail_projectile]
        self.cascade_detail_initial_defect_lattice.next_states = [
                self.cascade_detail_initial_defect_atom,
                self.cascade_detail_projectile]
        self.cascade_detail_initial_defect_atom.next_states = [
                self.cascade_detail_projectile]
        self.cascade_detail_projectile.next_states = [self.cascade_report_summary]
        self.cascade_report_summary.next_states = [self.cascade_report_atom]
        self.cascade_report_atom.next_states = [
                self.cascade_report_detail,
                self.cascade_end]
        self.cascade_report_detail.next_states = [self.cascade_report_detail_1]
        self.cascade_report_detail_1.next_states = [self.cascade_report_detail_2]
        self.cascade_report_detail_2.next_states = [self.cascade_report_detail_3]
        self.cascade_report_detail_3.next_states = [
                self.cascade_report_lattice_sites,
                self.cascade_ranger,
                self.cascade_sequin,
                self.cascade_orgiv,
                self.cascade_end]
        self.cascade_report_lattice_sites.next_states = [
                self.cascade_ranger,
                self.cascade_sequin,
                self.cascade_orgiv,
                self.cascade_end]
        self.cascade_ranger.next_states = [
                self.cascade_sequin,
                self.cascade_orgiv,
                self.cascade_end]
        self.cascade_sequin.next_states = [
                self.cascade_orgiv,
                self.cascade_end]
        self.cascade_orgiv.next_states = [self.cascade_end]
        self.cascade_end.next_states = [
                self.cascade,
                self.final]
        self.final.next_states = [self.final_rangex]
        self.final_rangex.next_states = [self.final_slavex]
        self.final_slavex.next_states = [self.final_slavex_atom]
        self.final_slavex_atom.next_states = [self.final_sequex]
        self.final_sequex.next_states = [self.final_orgex]
        self.final_orgex.next_states = [self.final_end]
        self.final_end.next_states = [self.end]


    def __iter__(self):
        return self

    def __next__(self):
        '''returns blockname
             blockname: one of BlockSeparator.state'''
        while self.no_eof:
            next_state = self.state.next(self.line)
            if next_state is None or next_state.name == self.state.name:
                # stay at current state
                self.state.on_stay_state(self.line)

                # get next line
                try:
                    self.lineno, self.line = next(self.linereducer)
                except StopIteration:
                    # dump and flush buffer
                    self.no_eof = False
                    self.state.on_exit()
                    return self.state
            else:
                # leave current state
                # dump and flush buffer
                ret_state = self.state
                self.state.on_exit()

                # move to next state
                self.state = next_state
                self.state.on_enter(self.line)

                return ret_state

                # self.lineno and self.line are kept
        raise StopIteration


if __name__ == '__main__':
    import sys
    import argparse

    from .. import smart_argparse

    argparser = argparse.ArgumentParser(formatter_class=smart_argparse.SmartHelpFormatter)
    argparser.add_argument('input', type=argparse.FileType('rt'), help="Input file. '-' for stdin")
    argparser.add_argument(
        'output', type=str, default=None, nargs='?',
        help='output data directory to output parsed data. '
        'If ommitted, INPUT.post is set INPUT.lst for data file. '
        'If input is stdin, this option should be given.')
    argparser.add_argument(
        '--cascade-directory-format', type=str,
        default='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
        help='directory form to store data for each cascade, which is created under '
        'OUTPUT directory (default: %(default)s)')
    argparser.add_argument(
        '--skip-verbose-textblock-output', action='store_true', default=False,
        help='skip output of verbose text block')
    argparser.add_argument(
            '-l', '--logging', dest='loglevel',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='choose logging level (default : %(default)s)',
            default='INFO')
    argparser.add_argument(
            '--cascade-table-output', choices=['BUNDLE', 'SEPARATE', 'BOTH'],
            default='BUNDLE',
            help='R|Select output form for large cascade data tables (ex. description_of_cascade{_all}.csv) '
            '(default: %(default)s)\n'
            '  SEPARATE: output as <root>/<each cascade>/xxx.csv\n'
            '  BUNDLE: output as <root>/xxx_all.csv\n'
            '  BOTH: SEPARATE and BUNDLE')

    args = argparser.parse_args()

    # set logging & debug level
    logging.basicConfig(level=logging.getLevelName(args.loglevel))

    # test output directory
    if args.output is None:
        if args.input.name == '<stdin>':
            print('Error: input is stdin, but no output name is provided.')
            sys.exit(1)
        else:
            # generate output name
            args.output = re.sub('\.lst$', '.post', args.input.name)
    if args.output == args.input.name:
        print('Error: same input ({}) and output ({}) name'.format(args.input.name,
                                                                   args.output))
        sys.exit(2)

    context = Context(outputdir=args.output,
            cascadedir_form=args.cascade_directory_format,
            config_dump_text_blocks = not args.skip_verbose_textblock_output,
            config_cascade_table_output = args.cascade_table_output)

    for _ in BlockSeparator(args.input, context):
        pass
