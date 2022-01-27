from salgsanalyse.main import loop
from salgsanalyse.file_handling import merge_files
from pathlib import Path
this_directory = Path(__file__).parent

def analyser(file_path, default_sheet='Sheet0'):
    loop(file_path)

def help():
    print((this_directory / "readme.md").read_text())

merge = merge_files