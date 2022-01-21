import pandas as pd

from magnumapi.tool_adapters.roxie import RoxieAPI


class RoxieInputBuilder:
    """ Class RoxieInputBuilder builds a ROXIE input

    """

    comment = ''
    bhdata_path = ''
    cadata_path = ''
    iron_path = ''
    flags = {'LEND': False, 'LWEDG': False, 'LPERS': False, 'LQUENCH': False, 'LALGO': False, 'LMIRIRON': False,
             'LBEMFEM': False, 'LPSI': False, 'LSOLV': False, 'LIRON': False, 'LMORPH': False, 'LHARD': False,
             'LPOSTP': False, 'LPEAK': True, 'LINMARG': False, 'LMARG': True, 'LSELF': False, 'LMQE': False,
             'LINDU': False, 'LEDDY': False, 'LSOLE': False, 'LFIELD3': False, 'LFISTR': False, 'LSELF3': False,
             'LBRICK': False, 'LLEAD': False, 'LVRML': False, 'LOPERA': False, 'LOPER20': False, 'LANSYS': False,
             'LRX2ANS': False, 'LANS2RX': False, 'LDXF': False, 'LMAP2D': False, 'LMAP3D': False, 'LEXPR': False,
             'LFIL3D': False, 'LFIL2D': False, 'LCNC': False, 'LANSYSCN': False, 'LWEIRON': False, 'LCATIA': False,
             'LEXEL': False, 'LFORCE2D': False, 'LAXIS': True, 'LIMAGX': False, 'LIMAGY': False, 'LRAEND': False,
             'LMARKER': False, 'LROLER2': False, 'LROLERP': False, 'LIMAGZZ': False, 'LSTEP': False, 'LIFF': False,
             'LICCA': False, 'LICC': False, 'LICCIND': False, 'LITERNL': False, 'LTOPO': False, 'LQUEN3': False,
             'LAYER': True, 'LEULER': True, 'LHEAD': True, 'LPLOT': True, 'LVERS52': True, 'LHARM': True,
             'LMATRF': False, 'LF3LIN': False}
    global2doption = pd.DataFrame()
    global3d = pd.DataFrame()
    block = pd.DataFrame()
    blockoption = pd.DataFrame()
    block3d = pd.DataFrame()
    lead = pd.DataFrame()
    brick = pd.DataFrame()
    iron_yoke = pd.DataFrame()
    extrusion = pd.DataFrame()
    permanentmag2 = pd.DataFrame()
    permanentmag1 = pd.DataFrame()
    layer = pd.DataFrame()
    algo = pd.DataFrame(data=[12], columns=['algo'], index=[0])
    design = pd.DataFrame()
    euler = pd.DataFrame()
    peak = pd.DataFrame()
    timetable2 = pd.DataFrame()
    timetable1 = pd.DataFrame()
    eddy = pd.DataFrame(data=[0], columns=['pers'], index=[0])
    eddyoptions = pd.DataFrame()
    quenchg = pd.DataFrame()
    quenchen = pd.DataFrame()
    quenchtm = pd.DataFrame()
    quenchp = pd.DataFrame()
    quenchs = pd.DataFrame()
    harmonictable = pd.DataFrame([{'no': 1, 'type': 1, 'x': 0, 'y': 0, 's1': 0, 's2': 0,
                                  'rref': 16.667, 'bref': 2, 'field': 0}])
    matrf = pd.DataFrame([{'start': 0, 'end': 0, 'no': 0, 'field': ''},
                          {'start': 0, 'end': 0, 'no': 0, 'field': ''},
                          {'start': 0, 'end': 0, 'no': 0, 'field': 0}])
    linefield = pd.DataFrame()
    harmonicoption = pd.DataFrame()
    graph = pd.DataFrame()
    graphoption = pd.DataFrame()
    plot2d = pd.DataFrame()
    plot2doption = pd.DataFrame()
    plot3d = pd.DataFrame()
    plot3doption = pd.DataFrame()
    objective = pd.DataFrame()

    def set_flag(self, flag_name: str, flag_value: bool) -> "RoxieInputBuilder":
        """ Method setting a flag in a ROXIE input file. An error is thrown if a flag does not exist

        :param flag_name: name of a flag
        :param flag_value: value of a flag
        :return: an updated RoxieInputBuilder instance
        """
        if flag_name in self.flags.keys():
            self.flags[flag_name] = flag_value
        else:
            raise KeyError('Key')
        return self

    def build(self, output_path: str) -> None:
        """ Method building a ROXIE input based on a template file

        :param output_path: an output path for the input .data file
        """
        output_str = self.prepare_data_file_str()

        with open(output_path, 'wb') as input_file:
            input_file.write(bytes(output_str, 'utf-8').replace(b'\r\n', b'\n'))

    def prepare_data_file_str(self) -> str:
        """ Method preparing a data file string content

        :return: a string with lines for an input data file
        """
        outputs = ['VERSION 10.2.1',
                   '\'%s\'' % self.comment,
                   '\'%s\'' % self.bhdata_path,
                   '\'%s\'' % self.cadata_path,
                   '\'%s\'' % self.iron_path,
                   '\n'
                   '&OPTION']
        # Add OPTION
        outputs.append(RoxieInputBuilder.convert_flag_dct_to_str(self.flags))
        # Add GLOBAL2DOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'GLOBAL2DOPTION', self.global2doption)
        # Add GLOBAL3D
        RoxieInputBuilder.append_to_outputs(outputs, 'GLOBAL3D', self.global3d)
        # Add BLOCK
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCK', self.block)
        # Add BLOCKOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCKOPTION', self.blockoption)
        # Add BLOCK3D
        RoxieInputBuilder.append_to_outputs(outputs, 'BLOCK3D', self.block3d)
        # Add LEAD
        RoxieInputBuilder.append_to_outputs(outputs, 'LEAD', self.lead)
        # Add BRICK
        RoxieInputBuilder.append_to_outputs(outputs, 'BRICK', self.brick)
        # Add IRONYOKE
        RoxieInputBuilder.append_to_outputs(outputs, 'IRONYOKE', self.iron_yoke)
        # Add EXTRUSION
        RoxieInputBuilder.append_to_outputs(outputs, 'EXTRUSION', self.extrusion)
        # Add PERMANENTMAG2
        RoxieInputBuilder.append_to_outputs(outputs, 'PERMANENTMAG2', self.permanentmag2)
        # Add PERMANENTMAG1
        RoxieInputBuilder.append_to_outputs(outputs, 'PERMANENTMAG1', self.permanentmag1)
        # Add LAYER
        RoxieInputBuilder.append_to_outputs(outputs, 'LAYER', self.layer, line_suffix=' /')
        # Add ALGO
        RoxieInputBuilder.append_to_outputs(outputs, 'ALGO', self.algo, header_suffix=' /')
        # Add DESIGN
        RoxieInputBuilder.append_to_outputs(outputs, 'DESIGN', self.design)
        # Add EULER
        RoxieInputBuilder.append_to_outputs(outputs, 'EULER', self.euler)
        # Add PEAK
        self.peak = pd.DataFrame(data=[self.block['no'].values], columns=['']*len(self.block), index=[0])
        RoxieInputBuilder.append_to_outputs(outputs, 'PEAK', self.peak, header_suffix=str(len(self.block['no'])))
        # Add TIMETABLE2
        RoxieInputBuilder.append_to_outputs(outputs, 'TIMETABLE2', self.timetable2)
        # Add TIMETABLE1
        RoxieInputBuilder.append_to_outputs(outputs, 'TIMETABLE1', self.timetable1)
        # Add EDDY
        RoxieInputBuilder.append_to_outputs(outputs, 'EDDY', self.eddy, header_suffix=' /')
        # Add EDDYOPTIONS
        RoxieInputBuilder.append_to_outputs(outputs, 'EDDYOPTIONS', self.eddyoptions)
        # Add QUENCHG
        RoxieInputBuilder.append_to_outputs(outputs, 'QUENCHG', self.quenchg)
        # Add QUENCHEN
        RoxieInputBuilder.append_to_outputs(outputs, 'QUENCHEN', self.quenchen)
        # Add QUENCHTM
        RoxieInputBuilder.append_to_outputs(outputs, 'QUENCHTM', self.quenchtm)
        # Add QUENCHP
        RoxieInputBuilder.append_to_outputs(outputs, 'QUENCHP', self.quenchp)
        # Add QUENCHS
        RoxieInputBuilder.append_to_outputs(outputs, 'QUENCHS', self.quenchs)
        # Add HARMONICTABLE
        RoxieInputBuilder.append_to_outputs(outputs, 'HARMONICTABLE', self.harmonictable)
        # Add MATRF
        RoxieInputBuilder.append_to_outputs(outputs, 'MATRF', self.matrf, header_suffix='1')
        # Add LINEFIELD
        RoxieInputBuilder.append_to_outputs(outputs, 'LINEFIELD', self.linefield)
        # Add HARMONICOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'HARMONICOPTION', self.harmonicoption)
        # Add GRAPH
        RoxieInputBuilder.append_to_outputs(outputs, 'GRAPH', self.graph)
        # Add GRAPHOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'GRAPHOPTION', self.graphoption)
        # PLOT2D
        RoxieInputBuilder.append_to_outputs(outputs, 'PLOT2D', self.plot2d, line_suffix=' /')
        # PLOT2DOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'PLOT2DOPTION', self.plot2doption)
        # PLOT3D
        RoxieInputBuilder.append_to_outputs(outputs, 'PLOT3D', self.plot3d)
        # PLOT3DOPTION
        RoxieInputBuilder.append_to_outputs(outputs, 'PLOT3DOPTION', self.plot3doption)
        # OBJECTIVE
        RoxieInputBuilder.append_to_outputs(outputs, 'OBJECTIVE', self.objective)

        outputs.append('')
        return '\n'.join(outputs)

    @staticmethod
    def convert_flag_dct_to_str(flags: dict) -> str:
        """ Static method converting a dictionary with flags into a formatted string

        :param flags: a dictionary with flags
        :return: a formatted string representation of the dictionary with flags
        """
        COLUMN_WIDTH = 11
        flag_per_line_count = 1
        flag_str = '  '
        for key, value in flags.items():
            temp = "%s=%s" % (key, "T" if value else "F")
            temp += (COLUMN_WIDTH - len(temp)) * ' '
            if flag_per_line_count < 6:
                flag_str += temp
                flag_per_line_count += 1
            else:
                flag_str += temp + "\n  "
                flag_per_line_count = 1

        flag_str += '\n  /'
        return flag_str

    @staticmethod
    def append_to_outputs(outputs, keyword, df, line_suffix='', header_suffix='') -> None:
        """ Static method appending to the output list (in place) a dataframe with a keyword

        :param outputs: a list of outputs for an input file
        :param keyword: a table keyword
        :param df: a dataframe
        """
        outputs.append('')
        outputs.append(RoxieAPI.convert_bottom_header_table_to_str(df, keyword, line_suffix, header_suffix))
