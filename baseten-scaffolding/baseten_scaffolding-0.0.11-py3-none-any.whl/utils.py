import os


def zipdir(path, zip_handler):
    for root, dirs, files in os.walk(path):
        relative_root = ''.join(root.split(path))
        for _file in files:
            zip_handler.write(
                os.path.join(root, _file), os.path.join(f'model{relative_root}', _file))
