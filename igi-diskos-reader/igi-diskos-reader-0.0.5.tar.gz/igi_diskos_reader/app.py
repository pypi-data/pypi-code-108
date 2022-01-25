from argparse import Namespace, ArgumentParser
import os
from typing import List

from igi_file_transformation_contract import (
    IFileTransformer, TransformationResult, Status, SuccessStatus)

from igi_diskos_reader.reader import build_reader
from igi_diskos_reader.writer import ExcelWriter

USE_FILE_SELECTOR = 'Use file selector to pick input file'
AUTO = "<AutoAssign>"


class DiskosFileTransformer(IFileTransformer):

    @property
    def title(self) -> str:
        return "Diskos (NPD-95) File Transformation"

    @property
    def user_description(self) -> str:
        return ("Upload a Diskos (NPD-95).asc file to get an import file ready for p:IGI+ "
                "/ Metis Transform.")

    @property
    def accepts_file_extensions(self) -> List[str]:
        return ['.asc', '.txt']
                
    def try_transform_file(self, in_path: str, out_path: str=AUTO) -> TransformationResult:
        """
        Transform Diskos (NPD-95).ASC file for p:IGI+/Transform import
        Returns: TransformationResult with path to transformed file and status
        """
        try:
            out_path = self.transform_file(in_path, out_path)
            result = TransformationResult(SuccessStatus, output_filepath=out_path)
            return result

        except Exception as e:
            status = Status(success=False, igi_exception=e)
            return TransformationResult(status)

    def transform_file(self, in_path: str, out_path: str = AUTO) -> str:
        """
        Transform Diskos (NPD-95).ASC file ready for p:IGI+/Transform import
        Returns: path to transformed file
        """
        if out_path == AUTO:
            out_path = self.get_default_output_path(in_path)

        reader = build_reader(in_path)
        parsed_file = reader.parse_file()
        with ExcelWriter(parsed_file, out_path) as writer:
            writer.write()
        return out_path

    def pick_and_transform_file(self) -> str:
        """
        Command line option to open file picker to select input file.
        Can also be used if you are using this lib within a Python script.
        For use in a web service use `transform_file` instead.
        """
        import tkinter.filedialog
        import tkinter as tk

        root = tk.Tk()  # to allow file selection dialog
        root.withdraw()  # hide root window
        input_path = tk.filedialog.askopenfilename(
            title="Select Diskos file",
            filetypes=(("ascii files", "*.asc"), ("all files", "*.*")),
        )
        return self.transform_file(input_path)

    @property
    def result_disclaimer(self) -> str:
        return ("Please check the output. We have tried to interpret the file correctly "
                "based on examples that we have seen. See the combined sheet for merged "
                "output. The header names have not been mapped to the IGI property model "
                "yet. Please contact IGI for help with a linking template (this may be "
                "included with the output shortly).")


def launch(input_path: str = USE_FILE_SELECTOR, suppress_excel_auto_open: bool = False) -> None:
    """
    Entry point for use as a package (rather than command line).
    """
    transformer = DiskosFileTransformer()
    if input_path == USE_FILE_SELECTOR:
        out_path = transformer.pick_and_transform_file()
    else:
        out_path = transformer.transform_file(input_path)
    if not suppress_excel_auto_open:
        os.startfile(out_path)


def build_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Parses diskos asc files and generates Excel spreadsheets from them.")
    parser.add_argument('-i', '--input', dest='input_path', type=str, default=USE_FILE_SELECTOR,
                        help="Path to the diskos asc file.")
    parser.add_argument('-s', '--suppress-excel', action='store_true', default=False,
                        dest='suppress_excel_auto_open',
                        help="If true the app will open the Excel file automatically when finished.")
    return parser


def main(args: Namespace):
    launch(args.input_path, args.suppress_excel_auto_open)


if __name__ == '__main__':
    main(build_arg_parser().parse_args())
