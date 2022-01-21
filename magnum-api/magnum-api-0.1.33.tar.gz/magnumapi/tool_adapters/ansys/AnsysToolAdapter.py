import os
from subprocess import Popen, PIPE

import pandas as pd
from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.core import Mapdl, launch_mapdl

from magnumapi.tool_adapters.ToolAdapter import ToolAdapter
import magnumapi.commons.text_file as text_file


class AnsysToolAdapter(ToolAdapter):
    """ An AnsysToolAdapter class with methods to execute an ANSYS model from command line, read figures of merit table
    and prepare a Lorentz force file

    """

    def __init__(self,
                 input_folder_rel_dir: str,
                 input_file: str,
                 output_file: str,
                 model_file: str,
                 rst_file: str
                 ) -> None:
        """ A constructor of AnsysToolAdapter instance

        :param input_folder_rel_dir: a relative directory with model inputs
        :param input_file: a name of an input file
        :param output_file: a name of an output file
        :param model_file: a name of a model file
        :param rst_file: a name of an output rst file
        """
        self.root_dir = os.getcwd()
        self.input_folder_rel_dir = input_folder_rel_dir
        self.input_file = input_file
        self.output_file = output_file
        self.model_file = model_file
        self.rst_file = rst_file
        self.output_lines = []

    def get_input_path(self):
        return os.path.join(self.root_dir, self.input_folder_rel_dir, self.input_file)

    def get_output_path(self):
        return os.path.join(self.root_dir, self.input_folder_rel_dir, self.output_file)

    def get_model_path(self):
        return os.path.join(self.root_dir, self.input_folder_rel_dir, self.model_file)

    def run(self) -> None:
        raise NotImplementedError('This method is not implemented for this class')

    def post_process(self):
        rst_path = os.path.join(self.input_folder_rel_dir, self.rst_file)

        result = pymapdl_reader.read_binary(rst_path)
        result.plot_principal_nodal_stress(0, 'SEQV', cpos='xy')
        result.plot_nodal_solution(0, cpos='xy')

    def read_figures_of_merit_table(self) -> pd.DataFrame:
        output_path = os.path.join(self.root_dir, self.input_folder_rel_dir, self.output_file)
        return self.read_figures_of_merit_table_from_file(output_path)

    @staticmethod
    def read_figures_of_merit_table_from_file(output_path):
        with open(output_path, 'r') as output:
            output_file_content = output.read().split('\n')
        keys = output_file_content[0].split(' ')
        keys = [key for key in keys if key != '']
        values = output_file_content[1].split(' ')
        values = [float(value) for value in values if value != '']
        key_value = {key: value for key, value in zip(keys, values)}
        return pd.DataFrame(key_value, index=[0])

    @staticmethod
    def convert_figures_of_merit_to_dict(fom_df: pd.DataFrame) -> dict:
        return fom_df.to_dict('records')[0]

    def prepare_force_file(self, input_force_file: str, output_force_file: str) -> None:
        """ Method preparing a force file for ANSYS from a ROXIE Lorentz force file, .force2d

        :param input_force_file: a name of a ROXIE Lorentz force file
        :param output_force_file: a name of an output file for ANSYS
        """
        input_force_file_path = os.path.join(self.root_dir, self.input_folder_rel_dir, input_force_file)
        output_force_file_path = os.path.join(self.root_dir, self.input_folder_rel_dir, output_force_file)

        AnsysToolAdapter.convert_roxie_force_file_to_ansys(input_force_file_path, output_force_file_path)

    @staticmethod
    def convert_roxie_force_file_to_ansys(input_force_file_path: str, output_force_file_path: str) -> None:
        """ Static method preparing a force file for ANSYS from a ROXIE Lorentz force file, .force2d

        :param input_force_file: a name of a ROXIE Lorentz force file
        :param output_force_file: a name of an output file for ANSYS
        """
        force_txt = text_file.readlines(input_force_file_path)
        
        ansys_force = []
        for force_txt_el in force_txt:
            row_float = [float(el) for el in force_txt_el.replace('\n', '').split(' ') if el != '']
            ansys_force.append('nodeNum = NODE(%f, %f, 0.0)' % tuple(row_float[:2]))
            ansys_force.append('F,nodeNum,FX, %f' % row_float[2])
            ansys_force.append('F,nodeNum,FY, %f' % row_float[3])

        text_file.writelines(output_force_file_path, ansys_force)

    @staticmethod
    def remove_ansys_output_files(root_dir: str, n_outputs: int):
        for i in range(n_outputs):
            ansys_output_file = 'vallone_%d.out' % i
            ansys_output_path = os.path.join(root_dir, ansys_output_file)
            if os.path.isfile(ansys_output_path):
                os.remove(ansys_output_path)

    @staticmethod
    def read_multiple_ansys_figures_of_merit(root_dir: str, n_outputs: int) -> list:
        fom_dcts = []

        for i in range(n_outputs):
            ansys_output_file = 'vallone_%d.out' % i
            ansys_output_path = os.path.join(root_dir, ansys_output_file)
            if os.path.isfile(ansys_output_path) and os.path.getsize(ansys_output_path) > 0:
                fom_df = AnsysToolAdapter.read_figures_of_merit_table_from_file(ansys_output_path)
                if fom_df['seqv'].values[0] < 1e-6:
                    fom_dct = {"seqv": float('nan')}
                else:
                    fom_dct = AnsysToolAdapter.convert_figures_of_merit_to_dict(fom_df)
            else:
                fom_dct = {"seqv": float('nan')}

            fom_dcts.append(fom_dct)

        return fom_dcts


class TerminalAnsysToolAdapter(AnsysToolAdapter):

    def __init__(self,
                 input_folder_rel_dir: str,
                 input_file: str,
                 output_file: str,
                 model_file: str,
                 rst_file: str,
                 out_temp_file: str,
                 executable_path: str,
                 license_type: str) -> None:
        """ A constructor of TerminalAnsysToolAdapter instance

        :param input_folder_rel_dir: a relative directory with model inputs
        :param input_file: a name of an input file
        :param output_file: a name of an output file
        :param model_file: a name of a model file
        :param rst_file: a name of an output rst file
        :param out_temp_file: a path to an output file
        :param executable_path: an absolute path to an ANSYS APDL executable
        :param license_type: a license type for ANSYS
        """
        super().__init__(input_folder_rel_dir, input_file, output_file, model_file, rst_file)
        self.input_file = input_file
        self.output_file = output_file
        self.model_file = model_file
        self.out_temp_file = out_temp_file
        self.executable_path = executable_path
        self.license_type = license_type

    def run(self):
        output_path = os.path.join(self.root_dir, self.input_folder_rel_dir, self.output_file)
        if os.path.isfile(output_path):
            os.remove(output_path)
        else:  ## Show an error ##
            print("Warning: %s file not found" % output_path)

        model_dir = os.path.join(self.root_dir, self.input_folder_rel_dir)
        input_path = os.path.join(self.root_dir, self.input_folder_rel_dir, self.input_file)
        out_temp_path = os.path.join(self.root_dir, self.input_folder_rel_dir, self.out_temp_file)
        cmd = [r'%s' % self.executable_path, '-b', '-p', self.license_type, '-smp', '-np', '2', '-lch',
               '-dir', model_dir, '-i', input_path, '-o', out_temp_path]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        byte_output, err = p.communicate(b"input data that is passed to subprocess' stdin")

        byte_output_decode = byte_output.decode()
        self.output_lines = byte_output_decode.split('\n')


class MapdlAnsysToolAdapter(AnsysToolAdapter):

    def __init__(self,
                 input_folder_rel_dir: str,
                 input_file: str,
                 output_file: str,
                 model_file: str,
                 rst_file: str,
                 single_upload_files: list,
                 reupload_files: list) -> None:
        """

        :param input_folder_rel_dir:
        :param input_file:
        :param output_file:
        :param model_file:
        :param rst_file: a name of an output rst file
        :param single_upload_files:
        :param reupload_files:
        """
        super().__init__(input_folder_rel_dir, input_file, output_file, model_file, rst_file)
        self.single_upload_files = single_upload_files
        self.reupload_files = reupload_files
        self.mapdl = None

    def _launch_mapdl(self):
        self.mapdl = launch_mapdl()

    def run(self):

        if not self.mapdl:
            self._launch_mapdl()
            for single_upload_file in self.single_upload_files:
                self.mapdl.upload(os.path.join(self.root_dir, self.input_folder_rel_dir, single_upload_file))

        for reupload_file in self.reupload_files:
            self.mapdl.upload(os.path.join(self.root_dir, self.input_folder_rel_dir, reupload_file))

        self.mapdl.input(self.input_file)
        self.mapdl.finish()

        self.mapdl.download(self.output_file, os.path.join(self.root_dir, self.input_folder_rel_dir, self.output_file))
        self.mapdl.download(self.rst_file, os.path.join(self.root_dir, self.input_folder_rel_dir, self.rst_file))


class DockerMapdlAnsysToolAdapter(MapdlAnsysToolAdapter):

    def __init__(self,
                 input_folder_rel_dir: str,
                 input_file: str,
                 output_file: str,
                 model_file: str,
                 rst_file: str,
                 single_upload_files: list,
                 reupload_files: list,
                 ip: str,
                 port: int) -> None:
        """

        :param input_folder_rel_dir:
        :param input_file:
        :param output_file:
        :param model_file:
        :param rst_file:
        :param single_upload_files:
        :param reupload_files:
        :param ip:
        :param port:
        """
        super().__init__(input_folder_rel_dir=input_folder_rel_dir,
                         input_file=input_file,
                         output_file=output_file,
                         model_file=model_file,
                         rst_file=rst_file,
                         single_upload_files=single_upload_files,
                         reupload_files=reupload_files)
        self.ip = ip
        self.port = port

    def _launch_mapdl(self):
        self.mapdl = Mapdl(ip=self.ip, port=self.port, request_instance=False)
