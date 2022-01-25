from dataclasses import dataclass, field
from typing import List  # , Dict, Tuple
from streng.phd.building_models.model2d_older.model_input import Model2d

@dataclass
class EtoolsOutput:
    input_log_filename: str
    log_lines: List[str] = field(default_factory=list)
    title_lines: List[tuple] = field(default_factory=list)
    column_bending_reinforcement: List[dict] = field(default_factory=list)
    column_shear_reinforcement: List[dict] = field(default_factory=list)
    beam_bending_reinforcement: List[dict] = field(default_factory=list)
    beam_shear_reinforcement: List[dict] = field(default_factory=list)

    model: Model2d = None


    def __post_init__(self):
        f = open(self.input_log_filename, 'r')
        self.log_lines = f.readlines()
        self.title_lines = [(i, s) for i, s in enumerate(self.log_lines) if '--- ' in s and ' ---' in s]
        self.get_column_bending_reinforcement()
        self.get_beam_bending_reinforcement()
        self.get_beam_shear_reinforcement()
        self.get_column_shear_reinforcement()

    def get_column_bending_reinforcement(self):
        # Βρίσκω αρχικά τον αύξοντα αριθμό του τίτλου και τη γραμμή του
        _title_index_col_bend, _line_col_bend = \
            [(i, x[0]) for i, x in enumerate(self.title_lines) if "Οπλισμοί κάμψης υποστυλωμάτων" in x[1]][0]
        _line_next_title = self.title_lines[_title_index_col_bend+1][0]

        _col_bending_block = self.log_lines[_line_col_bend:_line_next_title]
        _col_min_reinf_lines = [i for i, s in enumerate(_col_bending_block) if 'Ελάχιστοι οπλισμοι' in s]
        # print(f'_title_index_col_bend = {_title_index_col_bend}')
        # print(f'_line_col_bend = {_line_col_bend}')
        # print(f'_line_next_title = {_line_next_title}')
        _column_bending_reinforcement = []

        for i in _col_min_reinf_lines:
            _col_id_line = _col_bending_block[i-2].split()
            _col_id = _col_id_line[0] + '-' + _col_id_line[1]

            _Asminbot = _col_bending_block[i].split()[2]
            _Asmaxbot = _col_bending_block[i+1].split()[2]
            _Ascalcbot = _col_bending_block[i+2].split()[2]
            _Asreqbot = _col_bending_block[i + 3].split()[2]
            _Assuggestedbot = _col_bending_block[i + 4].split()[2]

            _Asmintop = _col_bending_block[i].split()[3]
            _Asmaxtop = _col_bending_block[i+1].split()[3]
            _Ascalctop = _col_bending_block[i+2].split()[3]
            _Asreqtop = _col_bending_block[i + 3].split()[3]
            _Assuggestedtop = _col_bending_block[i + 4].split()[3]

            _column_bending_reinforcement.append({'col_id': _col_id,
                                                  'Asminbot': _Asminbot,
                                                  'Asmaxbot': _Asmaxbot,
                                                  'Ascalcbot': _Ascalcbot,
                                                  'Asreqbot': _Asreqbot,
                                                  'Assuggestedbot': _Assuggestedbot,
                                                  'Asmintop': _Asmintop,
                                                  'Asmaxtop': _Asmaxtop,
                                                  'Ascalctop': _Ascalctop,
                                                  'Asreqtop': _Asreqtop,
                                                  'Assuggestedtop': _Assuggestedtop,
                                                  })

        self.column_bending_reinforcement = _column_bending_reinforcement

    def get_beam_bending_reinforcement(self):
        # Βρίσκω αρχικά τον αύξοντα αριθμό του τίτλου και τη γραμμή του
        _title_index_beam_bend, _line_beam_bend = \
            [(i, x[0]) for i, x in enumerate(self.title_lines) if "Οπλισμοί κάμψης δοκών" in x[1]][0]
        _line_next_title = self.title_lines[_title_index_beam_bend + 1][0]

        _beam_bending_block = self.log_lines[_line_beam_bend:_line_next_title]
        _beam_min_reinf_lines = [i for i, s in enumerate(_beam_bending_block) if 'Ελάχιστοι οπλισμοι' in s]

        _beam_bending_reinforcement = []

        for i in _beam_min_reinf_lines:
            _beam_id_line = _beam_bending_block[i - 2].split()
            _beam_id = _beam_id_line[0] + '-' + _beam_id_line[1]

            _Asmin_leftbot = _beam_bending_block[i].split()[2]
            _Asmax_leftbot = _beam_bending_block[i + 1].split()[2]
            _Ascalc_leftbot = _beam_bending_block[i + 2].split()[2]
            _Asreq_leftbot = _beam_bending_block[i + 3].split()[2]
            _Assuggested_leftbot = _beam_bending_block[i + 4].split()[2]

            _Asmin_lefttop = _beam_bending_block[i].split()[3]
            _Asmax_lefttop = _beam_bending_block[i + 1].split()[3]
            _Ascalc_lefttop = _beam_bending_block[i + 2].split()[3]
            _Asreq_lefttop = _beam_bending_block[i + 3].split()[3]
            _Assuggested_lefttop = _beam_bending_block[i + 4].split()[3]
            
            _Asmin_rightbot = _beam_bending_block[i].split()[6]
            _Asmax_rightbot = _beam_bending_block[i + 1].split()[6]
            _Ascalc_rightbot = _beam_bending_block[i + 2].split()[6]
            _Asreq_rightbot = _beam_bending_block[i + 3].split()[6]
            _Assuggested_rightbot = _beam_bending_block[i + 4].split()[6]

            _Asmin_righttop = _beam_bending_block[i].split()[7]
            _Asmax_righttop = _beam_bending_block[i + 1].split()[7]
            _Ascalc_righttop = _beam_bending_block[i + 2].split()[7]
            _Asreq_righttop = _beam_bending_block[i + 3].split()[7]
            _Assuggested_righttop = _beam_bending_block[i + 4].split()[7]

            _beam_bending_reinforcement.append({'beam_id': _beam_id,
                                                'Asmin_leftbot': _Asmin_leftbot,
                                                'Asmax_leftbot': _Asmax_leftbot,
                                                'Ascalc_leftbot': _Ascalc_leftbot,
                                                'Asreq_leftbot': _Asreq_leftbot,
                                                'Assuggested_leftbot': _Assuggested_leftbot,
                                                'Asmin_lefttop': _Asmin_lefttop,
                                                'Asmax_lefttop': _Asmax_lefttop,
                                                'Ascalc_lefttop': _Ascalc_lefttop,
                                                'Asreq_lefttop': _Asreq_lefttop,
                                                'Assuggested_lefttop': _Assuggested_lefttop,

                                                'Asmin_rightbot': _Asmin_rightbot,
                                                'Asmax_rightbot': _Asmax_rightbot,
                                                'Ascalc_rightbot': _Ascalc_rightbot,
                                                'Asreq_rightbot': _Asreq_rightbot,
                                                'Assuggested_rightbot': _Assuggested_rightbot,
                                                'Asmin_righttop': _Asmin_righttop,
                                                'Asmax_righttop': _Asmax_righttop,
                                                'Ascalc_righttop': _Ascalc_righttop,
                                                'Asreq_righttop': _Asreq_righttop,
                                                'Assuggested_righttop': _Assuggested_righttop,
                                                })

        self.beam_bending_reinforcement = _beam_bending_reinforcement

    def get_beam_shear_reinforcement(self):
        # Βρίσκω αρχικά τον αύξοντα αριθμό του τίτλου και τη γραμμή του
        _title_index_beam_shear, _line_beam_shear = \
            [(i, x[0]) for i, x in enumerate(self.title_lines) if "Οπλισμοί διάτμησης δοκών" in x[1]][0]
        _line_next_title = self.title_lines[_title_index_beam_shear + 1][0]
        _beam_shear_block = self.log_lines[_line_beam_shear:_line_next_title]

        _beam_shear_reinforcement = []
        i = 5  # start line after title
        while len(_beam_shear_block[i].split()) > 2:
            _line = _beam_shear_block[i].split()
            _beam_id = _line[0] + '-' + _line[1]
            _shear_reinf_left = _line[7]
            _shear_reinf_right = _line[13]
            _beam_shear_reinforcement.append({'beam_id': _beam_id,
                                              'shear_reinf_left': _shear_reinf_left,
                                              'shear_reinf_right': _shear_reinf_right,
                                              })
            i += 1
        self.beam_shear_reinforcement = _beam_shear_reinforcement

    def get_column_shear_reinforcement(self):
        # Βρίσκω αρχικά τον αύξοντα αριθμό του τίτλου και τη γραμμή του
        _title_index_col_shear, _line_col_shear = \
            [(i, x[0]) for i, x in enumerate(self.title_lines) if "Οπλισμοί διάτμησης υποστυλωμάτων" in x[1]][0]
        if _title_index_col_shear != len(self.title_lines) - 1:
            _line_next_title = self.title_lines[_title_index_col_shear + 1][0]
        else:
            _line_next_title = len(self.log_lines)
        _col_shear_block = self.log_lines[_line_col_shear:_line_next_title]

        _column_shear_reinforcement = []
        i = 5  # start line after title
        while len(_col_shear_block[i].split()) > 2:
            _line = _col_shear_block[i].split()
            _beam_id = _line[0] + '-' + _line[1]
            _shear_reinf_left = _line[7]
            _shear_reinf_right = _line[14]
            _column_shear_reinforcement.append({'col_id': _beam_id,
                                              'shear_reinf_left': _shear_reinf_left,
                                              'shear_reinf_right': _shear_reinf_right,
                                              })
            i += 1
        self.column_shear_reinforcement = _column_shear_reinforcement



    def write_group_section_reinforcements(self, filename):
        out = []

        out.append('Οπλισμός δοκών')
        out.append('')
        out.extend(self.get_group_beam_bending_reinforcement())

        out.append('Οπλισμός στύλων')
        out.append('')
        out.extend(self.get_group_column_bending_reinforcement())

        file = open(filename, 'w')
        file.write('\n'.join(out))
        file.close()

    def get_group_beam_bending_reinforcement(self):
        out = []

        beam_section_names = [index for index, row in self.model.input_data['sections'].iterrows() if
                              row['ElementType'] == 'BEAM']
        # print(beam_section_names)

        for beam_name in beam_section_names:
            out.append(f'Δοκοί με διατομή: {beam_name}')
            out.append('')

            elements_with_section = [f'STORY{row["Storey"]}-{row["Line_Etabs"]}' for index, row in
                                     self.model.input_data['elements'].iterrows() if row['GeometryName'] == beam_name]

            out.append(f'Οπλισμός κάμψης δοκών με διατομή: {beam_name}')

            out.append(f'{"Στοιχείο":^15}{" || "}{"Αριστερά πάνω":^30}{" | "}{"Αριστερά κάτω":^30}{" || "}' + \
                       f'{"Δεξιά πάνω":^30}{" | "}{"Δεξιά κάτω":^30}{" || "}')
            out.append(f'{"":^15}{" || "}{"Aslt_min":^10}{"Aslt_calc":^10}{"Aslt_sug":^10}{" | "}' + \
                       f'{"Aslb_min":^10}{"Aslb_calc":^10}{"Aslb_sug":^10}{" || "}' + \
                       f'{"Asrt_min":^10}{"Asrt_calc":^10}{"Asrt_sug":^10}{" | "}' + \
                       f'{"Asrb_min":^10}{"Asrb_calc":^10}{"Asrb_sug":^10}{" || "}')

            for el in elements_with_section:
                bbr = next(x for x in self.beam_bending_reinforcement if x['beam_id'] == el)
                out.append(
                    f'{el:^15}{" || "}{bbr["Asmin_lefttop"]:^10}{bbr["Ascalc_lefttop"]:^10}{bbr["Assuggested_lefttop"]:^10}{" | "}' + \
                    f'{bbr["Asmin_leftbot"]:^10}{bbr["Ascalc_leftbot"]:^10}{bbr["Assuggested_leftbot"]:^10}{" || "}' + \
                    f'{bbr["Asmin_righttop"]:^10}{bbr["Ascalc_righttop"]:^10}{bbr["Assuggested_righttop"]:^10}{" | "}' + \
                    f'{bbr["Asmin_rightbot"]:^10}{bbr["Ascalc_rightbot"]:^10}{bbr["Assuggested_rightbot"]:^10}{" || "}')

            out.append(
                '-----------------------------------------------------------------------------------------------------------------------------------------------------------')
            out.append('')

        return out

    def get_group_column_bending_reinforcement(self):
        out = []

        column_section_names = [index for index, row in self.model.input_data['sections'].iterrows() if
                                row['ElementType'] == 'COLUMN']
        # print(column_section_names)

        for column_name in column_section_names:
            out.append(f'Στύλοι με διατομή: {column_name}')
            out.append('')

            elements_with_section = [f'STORY{row["Storey"]}-{row["Line_Etabs"]}' for index, row in
                                     self.model.input_data['elements'].iterrows() if row['GeometryName'] == column_name]

            out.append(f'Οπλισμός κάμψης δοκών με διατομή: {column_name}')

            out.append(f'{"Στοιχείο":^15}{" || "}{"Πόδας":^30}{" | "}{"Κεφαλή":^30}{" || "}')
            out.append(f'{"":^15}{" || "}{"Asb_min":^10}{"Asb_calc":^10}{"Asb_sug":^10}{" | "}' + \
                       f'{"Ast_min":^10}{"Ast_calc":^10}{"Ast_sug":^10}{" || "}')

            for el in elements_with_section:
                cbr = next(x for x in self.column_bending_reinforcement if x['col_id'] == el)
                out.append(
                    f'{el:^15}{" || "}{cbr["Asminbot"]:^10}{cbr["Ascalcbot"]:^10}{cbr["Assuggestedbot"]:^10}{" | "}' + \
                    f'{cbr["Asmintop"]:^10}{cbr["Ascalctop"]:^10}{cbr["Assuggestedtop"]:^10}{" || "}')

            out.append(
                '-----------------------------------------------------------------------------------------------------------------------------------------------------------')
            out.append('')

        return out



#
#
# lumn_bending_reinforcement.append({'col_id': _col_id,
#                                                   'Asminbot': _Asminbot,
#                                                   'Asmaxbot': _Asmaxbot,
#                                                   'Ascalcbot': _Ascalcbot,
#                                                   'Asreqbot': _Asreqbot,
#                                                   'Assuggestedbot': _Assuggestedbot,
#                                                   'Asmintop': _Asmintop,
#                                                   'Asmaxtop': _Asmaxtop,
#                                                   'Ascalctop': _Ascalctop,
#                                                   'Asreqtop': _Asreqtop,
#                                                   'Assuggestedtop': _Assuggestedtop,