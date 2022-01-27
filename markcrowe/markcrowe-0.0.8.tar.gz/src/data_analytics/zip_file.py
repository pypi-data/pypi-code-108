from zipfile import ZipFile
import os


def join_split_zip_files(split_zip_files_directory: str, destination_dir: str = './temp/', zip_filename: str = 'temp.zip') -> None:
    split_zip_files = os.listdir(split_zip_files_directory)
    zip_filepath = os.path.join(destination_dir, zip_filename)
    if os.path.isfile(zip_filepath):
        os.remove(zip_filepath)
    for split_zip_file in split_zip_files:
        with open(zip_filepath, "ab") as zip_file:
            with open(os.path.join(split_zip_files_directory, split_zip_file), "rb") as split_zip:
                zip_file.write(split_zip.read())
    return zip_filepath


def unzip_file(zip_filepath: str, destination_dir: str) -> None:
    with ZipFile(zip_filepath, 'r') as zipfile:
        zipfile.extractall(destination_dir)


def unzip_required_asset(filepath: str, zip_path: str, destination_dir: str) -> None:
    if not os.path.isfile(filepath):
        if os.path.isfile(zip_path):
            unzip_file(zip_path, destination_dir)
        elif os.path.isdir(zip_path):
            zip_filepath = join_split_zip_files(zip_path, destination_dir)
            unzip_file(zip_filepath, destination_dir)
            os.remove(zip_filepath)
