import os


image_types = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")


def list_images(basePath, contains=None, recursive=True):
    # return the set of files that are valid
    return list_files(basePath, validExts=image_types, contains=contains, recursive=recursive)


def list_files(basePath, validExts=None, contains=None, recursive=True):
    # loop over the directory structure
    for (rootDir, dirNames, filenames) in os.walk(basePath):
        # loop over the filenames in the current directory
        for filename in filenames:
            # if the contains string is not none and the filename does not contain
            # the supplied string, then ignore the file
            if contains is not None and filename.find(contains) == -1:
                continue

            # determine the file extension of the current file
            ext = filename[filename.rfind("."):].lower()

            # check to see if the file is an image and should be processed
            if validExts is None or ext.endswith(validExts):
                # construct the path to the image and yield it
                imagePath = os.path.join(rootDir, filename)
                yield imagePath
        if not recursive:
            break


def create_dir_of_file(file):
    """
    Crea el directorio de un archivo, si este no existe.
    :param file: fichero.
    :return:
    """
    directory, _ = os.path.split(file)
    if not os.path.exists(directory):
        os.makedirs(directory)
