"""
parse .lst file to dump data
"""

import pathlib
import json
import csv
import logging

from . import headingreducer

from . import marlowe_output_root

from . import cascade_group_number as cgn
from . import statistical_analysis_of_data as sad
from . import analysis_of_primary_recoil_ranges as aprr

from . import output_dir

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class Parser(marlowe_output_root.Parser):
    def __init__(self, outputdir,
                 cascade_dir_form='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}'):
        """initialize parser

        outputdir is string or pathlib.Path object to save output data.
          If outputdir does not exist, try to create it.
        cascade_dir_form is formmatable string to save data for each cascade
        """

        marlowe_output_root.Parser.__init__(self)

        self.outputdir = outputdir

        # directry to save each cascade data and summary
        self.cascade_dir_form = cascade_dir_form

        # output directory
        if not isinstance(outputdir, pathlib.Path):
            self.outputdir = pathlib.Path(self.outputdir)

        # prepare output directory
        output_dir.prepare(self.outputdir)

        # cascade tables
        self.description_of_cascade_all = csv.writer(
            (self.outputdir / 'description_of_cascade_all.csv').open('w', newline=''))
        self.description_of_cascade_all.writerow(cgn.description_of_cascade_headers)

        self.lattice_sites_all = csv.writer(
            (self.outputdir / 'lattice_sites_all.csv').open('w', newline=''))
        self.lattice_sites_all.writerow(cgn.lattice_sites_headers)

        self.distant_iv_pairs_all = csv.writer(
            (self.outputdir / 'distant_iv_pairs_all.csv').open('w', newline=''))
        self.distant_iv_pairs_all.writerow(cgn.distant_iv_pairs_headers)

        # additional table
        self.description_of_cascade_primary_recoil_all = csv.writer(
            (self.outputdir / 'description_of_cascade_primary_recoil_all.csv').open('w', newline=''))
        self.description_of_cascade_primary_recoil_all.writerow(cgn.description_of_cascade_headers)

    # ------ after actions for each Parser
    # after for each cascade simulation
    def cascade_group_number_after(self, mobj):
        # create output directory
        cascadedir = self.outputdir / self.cascade_dir_form.format(**mobj['Index'])
        if cascadedir.exists():
            if not cascadedir.is_dir():
                raise Error('{} exists but not directory'.format(cascadedir))
        else:
            cascadedir.mkdir()

        # dump 'detailed description of cascade 1-3' table
        if 'Cascade Detail' in mobj:
            with (cascadedir / 'description_of_cascade.csv').open(
                    'w', newline='') as f:
                csvf = csv.writer(f)
                # output header
                csvf.writerow(cgn.description_of_cascade_headers)

                primary_recoil_output = False
                for rec in mobj['Cascade Detail']['records']:
                    rowdata = cgn.description_of_cascade_rowdata(mobj, rec)
                    csvf.writerow(rowdata)
                    self.description_of_cascade_all.writerow(rowdata)
                    # output to primary recoil ('rec['File'] == 1') data only
                    if not primary_recoil_output and rec['File'] == 1:
                        self.description_of_cascade_primary_recoil_all.writerow(rowdata)
                        primary_recoil_output = True

        # dump 'lattice sites' table
        if 'Lattice Sites' in mobj:
            with (cascadedir / 'lattice_sites.csv').open('w', newline='') as f:
                csvf = csv.writer(f)
                # output header
                csvf.writerow(cgn.lattice_sites_headers)
                for rec in mobj['Lattice Sites']['records']:
                    rowdata = cgn.lattice_sites_rowdata(mobj, rec)
                    csvf.writerow(rowdata)
                    self.lattice_sites_all.writerow(rowdata)

        # dump 'distance I-V pairs' table
        if 'Separations of Distant I-V Pairs' in mobj:
            with (cascadedir / 'distant_iv_pairs.csv').open('w', newline='') as f:
                csvf = csv.writer(f)
                # output header
                csvf.writerow(cgn.distant_iv_pairs_headers)
                for rec in mobj['Separations of Distant I-V Pairs']['records']:
                    rowdata = cgn.distant_iv_pairs_rowdata(mobj, rec)
                    csvf.writerow(rowdata)
                    self.distant_iv_pairs_all.writerow(rowdata)

        # primary recoil ranges
        if 'Primary Recoil Ranges' in mobj:
            with (cascadedir / 'primary_recoil_ranges.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(cgn.primary_recoil_ranges_headers)
                rowdata = cgn.primary_recoil_ranges_rowdata(mobj)
                fcsv.writerow(rowdata)

        # cascade summary
        if 'Summary of Cascade' in mobj:
            with (cascadedir / 'summary_of_cascade.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(cgn.summary_of_cascade_headers)
                rowdata = cgn.summary_of_cascade_rowdata(mobj)
                fcsv.writerow(rowdata)

        # cascade summary for each atom
        if 'Cascade Summary for each Atom' in mobj:
            with (cascadedir / 'summary_of_cascade_each_atom.csv').open('w', newline='') \
                    as f:
                fcsv = csv.writer(f)
                fcsv.writerow(cgn.cascade_summary_each_atom_headers)
                for rec in mobj['Cascade Summary for each Atom']:
                    rowdata = cgn.cascade_summary_each_atom_rowdata(mobj, rec)
                    fcsv.writerow(rowdata)

        # delete large table data
        if 'Cascade Detail' in mobj:
            del mobj['Cascade Detail']
        if 'Lattice Sites' in mobj:
            del mobj['Lattice Sites']
        if 'Separations of Distant I-V Pairs' in mobj:
            del mobj['Separations of Distant I-V Pairs']

        # dump parsed data in cascade subdir
        with (cascadedir / 'cascade_summary.json').open('wt') as f:
            json.dump(mobj, f, indent=2)

        # add to root parsed object
        if 'Cascade' not in self.mobj:
            self.mobj['Cascade'] = []
        self.mobj['Cascade'].append(mobj)

    def parse(self, input):
        """run parser

        input is input filestream
        """

        einput = headingreducer.HeadingReducer(input)

        # self.mobj is updated by parse()
        marlowe_output_root.Parser.parse(self, einput, None)
        # dump mobj as json
        with (self.outputdir / 'summary.json').open('wt') as f:
            json.dump(self.mobj, f, indent=2)

        # summary data for each cascade
        with \
            (self.outputdir / 'primary_recoil_ranges_all.csv').open('w', newline='') \
                as primary_recoil_ranges_file, \
            (self.outputdir / 'summary_of_cascade_all.csv').open('w', newline='') \
                as summary_of_cascade_file, \
            (self.outputdir / 'summary_of_cascade_each_atom_all.csv').open('w', newline='') \
                as summary_of_cascade_each_atom_file:

            # prepare csv file and write header
            primary_recoil_ranges = csv.writer(primary_recoil_ranges_file)
            primary_recoil_ranges.writerow(cgn.primary_recoil_ranges_headers)

            summary_of_cascade = csv.writer(summary_of_cascade_file)
            summary_of_cascade.writerow(cgn.summary_of_cascade_headers)

            summary_of_cascade_each_atom = csv.writer(summary_of_cascade_each_atom_file)
            summary_of_cascade_each_atom.writerow(cgn.cascade_summary_each_atom_headers)

            # for each cascade
            for casc in self.mobj['Cascade']:
                d = casc.get('Primary Recoil Ranges', None)
                if d:
                    primary_recoil_ranges.writerow(cgn.primary_recoil_ranges_rowdata(casc))

                d = casc.get('Summary of Cascade', None)
                if d:
                    summary_of_cascade.writerow(cgn.summary_of_cascade_rowdata(casc))

                d = casc.get('Cascade Summary for each Atom', None)
                if d:
                    for rec in d:
                        summary_of_cascade_each_atom.writerow(
                            cgn.cascade_summary_each_atom_rowdata(casc, rec))

        # "Statiatical Analysis of Data"
        d = self.mobj.get("Statiatical Analysis of Data", None)
        if d:
            with (self.outputdir / 'statistical_analysis_of_data.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(sad.csvheaders)
                for k in sad.csvrowheaders:
                    if k in d:
                        rowdata = [k] + [d[k][v] for v in sad.csvcolumnkeys]
                        fcsv.writerow(rowdata)

        # Analysis of Primary Recoil Ranges
        d = self.mobj.get("Analysis of Primary Recoil Ranges", None)
        if d:
            with (self.outputdir / 'analysis_of_primary_recoil_ranges.csv').open('w', newline='') as f:
                fcsv = csv.writer(f)
                fcsv.writerow(aprr.csvheaders)
                for k in aprr.csvrowheaders:
                    if k in d:
                        rowdata = [k] + [d[k][v] for v in aprr.csvcolumnkeys]
                        fcsv.writerow(rowdata)
