import sys
import pathlib
import os
import shutil

root_path = pathlib.Path(__file__).parent.resolve()

def cli():
    if len(sys.argv) > 1:
        print("Initializing django project.... This may take a while")
        try:
            path = sys.argv[1]
            folder_path = os.path.join(root_path, "django-template")

            if path == "." or path == "./":
                path = os.getcwd()

            shutil.copytree(folder_path, path, dirs_exist_ok=True)

        except Exception as e:
            print(e)
    else:
        print("Please provide a path to create the project")
