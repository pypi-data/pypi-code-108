import logging
import os

logger = logging.getLogger("preprocessing_helper")

class FileNameGenerator:
    """Class to construct full file names out of a table_names dictionary of 
    the form:
    table_names = {
    "table_1": "table_1_name",
    "table_2": "table_2_name",
    }
    The values of the table_names must align to the root names of the files 
    i.e. table_1_name.csv
    """
    
    def __init__(self, table_names, file_loc) -> None:
        files = os.listdir(file_loc)
        tmp_file_lookup = {
            raw_file.split(".")[0]:raw_file for raw_file in files}
        
        self.__file_lookup = {
            table_nm:os.path.join(
                file_loc, tmp_file_lookup[table_names[table_nm]])
            for table_nm in table_names.keys()}
    
    @property
    def file_lookup(self):
        return self.__file_lookup

