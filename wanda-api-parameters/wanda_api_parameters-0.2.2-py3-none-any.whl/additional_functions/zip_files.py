import os
import zipfile

if __name__ == "__main__":
    fn_path = r"n:\Projects\11207000\11207361\B. Measurements and calculations\Optimization_folder\models"
    # List all available wdi's
    list_files = os.listdir(fn_path)
    case_files = [os.path.splitext(file)[0] for file in list_files if file.endswith(".wdi")]
    # Loop over the available models
    for case in case_files:

        with zipfile.ZipFile(os.path.join(fn_path, "{}.zip".format(case)), "w", zipfile.ZIP_DEFLATED) as zipF:
            zip_files = [file for file in list_files if (case == os.path.splitext(file)[0]) and (not file.endswith(".zip"))]
            for file in zip_files:
                filepath = os.path.join(fn_path, file)
                arcname = file
                zipF.write(filepath, arcname)
        zipF.close()


