from salgsanalyse.main import loop
from salgsanalyse.file_handling import merge_files

def analyser(file_path, default_sheet='Sheet0'):
    loop(file_path)

merge = merge_files