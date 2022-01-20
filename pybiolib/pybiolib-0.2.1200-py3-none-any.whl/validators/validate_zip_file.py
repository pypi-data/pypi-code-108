from zipfile import ZipFile


def validate_zip_file(zip_file_path, app_path):
    try:
        zip_file = ZipFile(zip_file_path)
    except Exception:
        raise Exception('Failed to read source files zip for validation.') from None

    files = [filename.strip('/') for filename in zip_file.namelist()]
    top_level_files = [filename for filename in files if len(filename.split('/')) == 1]

    if len(top_level_files) > 1:
        raise Exception('Please place all your source files in a single folder and zip it')

    # Check if .biolib folder is present
    if f'{top_level_files[0]}/.biolib' in files and f'{top_level_files[0]}/biolib' in files:
        raise Exception('You provided both a biolib and a .biolib folder. Please only provide the .biolib folder')

    elif f'{top_level_files[0]}/.biolib' in files:
        biolib_folder_path = f'{top_level_files[0]}/.biolib'

    elif f'{top_level_files[0]}/biolib' in files:
        raise Exception('Your biolib folder appears to be called "biolib" - it must be called ".biolib".')

    else:
        raise Exception(f'Could not find a .biolib folder in provided application folder {app_path}')

    # Check if the config file is present
    if f'{biolib_folder_path}/config.yml' in files:
        # TODO: Changed to make sense in CLI. Rewrite this check at some point
        pass

    elif f'{biolib_folder_path}/config.yaml' in files:
        raise Exception('Your biolib config file has the .yaml file extension - it must be .yml')

    else:
        raise Exception(
            f'Could not find config.yml file. Please provide a yaml file named config.yml in the .biolib folder'
        )
