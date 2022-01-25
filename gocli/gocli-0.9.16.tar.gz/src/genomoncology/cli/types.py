from click.types import ParamType
import os

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "../../datasets/")


class DatasetPath(ParamType):
    """
    A dataset can be one of three types of values:
        - local, relative file path (e.g. ./subdir/my_file.txt)
        - local, absolute file path (e.g. /opt/subdir/my_file.txt)
        - gocli dataset src/datasets (e.g. @snv_cancer.bed)
    """

    def convert(self, value, param, ctx):
        if value.startswith("@"):
            value = os.path.join(DATASETS_DIR, value[1:])
            print(f"HERE! {value}")

        return value

        # # if a full path, leave it, otherwise get from src/datasets
        # if not os.path.exists(file_path):
        #     file_path = os.path.join(DATASETS_DIR, file_path)
        #
        # assert os.path.exists(file_path), f"{file_path} not found."

        #
        # try:
        #     st = os.stat(rv)
        # except OSError:
        #     if not self.exists:
        #         return self.coerce_path_result(rv)
        #     self.fail('%s "%s" does not exist.' % (
        #         self.path_type,
        #         filename_to_ui(value)
        #     ), param, ctx)
