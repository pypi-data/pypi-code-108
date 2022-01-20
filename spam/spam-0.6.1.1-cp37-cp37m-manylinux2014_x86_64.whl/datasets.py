import pkg_resources as pkg
import tifffile
import pickle
import sys
import numpy

# Should avoid following error in python3
#   UnicodeDecodeError: 'ascii' codec can't decode byte 0xba in position 1: ordinal not in range(128)
# Generic functions


def loadtiff(filepath):
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        return tifffile.imread(f)
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0


def load(filepath):
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        return open(f, 'rb')
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0


def loadPickle(filepath):
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        # Different pickle-loading options for different python versions
        if sys.version[0] == '2':
            # on 3 lines to close pickle
            with open(f, 'r') as fh:
                ret = pickle.load(fh)
            return ret
        else:
            with open(f, 'rb') as fh:
                ret = pickle.load(fh, encoding='latin1')
            return ret
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0


# Usage example ##

# def loadtiffexample():
#    print("print something funny")
#    return loadtiff('image.tiff')


# def loadsomething():
#     print("print something funny")
#     return load('placeholder.txt')


def loadSnow():
    # print("spam.datasets.snow(): Brrr, enjoy this cold data")
    return loadtiff("snow/snow.tif")


def loadStructuredMesh():
    return loadPickle("mesh/structuredMesh.p")


def loadUnstructuredMesh():
    return loadPickle("mesh/unstructuredMesh.p")


def loadConcreteXr():
    return loadtiff("concrete/concrete_x-ray-bin16.tif")


def loadConcreteNe():
    return loadtiff("concrete/concrete_neutron-bin16.tif")


def loadDEMboxsizeCentreRadius():
    filepath = "DEM/spheres.txt"
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        # loading the dem file
        boxSizeDEM = numpy.genfromtxt(f, max_rows=1, comments='%', usecols=(1,2,3))
        centres    = numpy.loadtxt(f, skiprows=0, usecols=(4,3,2)) #! x,y,z
        radii      = numpy.loadtxt(f, skiprows=0, usecols=(5))
        return [boxSizeDEM, centres, radii]
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0

def loadUniformDEMboxsizeCentreRadius():
    filepath = "DEM/uniformSpheres.txt"
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        # loading the dem file
        centres    = numpy.loadtxt(f, skiprows=1, usecols=(2, 1, 0)) #! x,y,z
        # remove negative numbers
        centres   -= numpy.min(centres, axis=0)
        radii      = numpy.loadtxt(f, skiprows=1, usecols=(3))
        boxSizeDEM = (numpy.max(centres[:, :], axis=0) - numpy.min(centres[:, :], axis=0))+2*numpy.max(radii)
        return [boxSizeDEM, centres, radii]
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0

def loadDEMtouchingGrainsAndBranchVector():
    filepath = "DEM/contacts.txt"
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        # loading the dem file
        labels = numpy.loadtxt(f, skiprows=1, usecols=(0, 1))
        zyxBranch = numpy.loadtxt(f, skiprows=1, usecols=(4, 3, 2))
        return [labels.astype(numpy.int), zyxBranch]
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0
    return loadtxt("DEM/spheres.txt")

def loadDEMspheresMMR():
    filepath = "DEM/SpheresMMR.txt"
    data_file_path = 'data/' + filepath
    if (pkg.resource_exists('spam', data_file_path)):
        f = pkg.resource_filename('spam', data_file_path)
        # loading the dem file
        return numpy.genfromtxt(f)
    else:
        # raise IOError("File %s not found" % data_file_path)
        print(IOError("File %s not found" % data_file_path))
        return 0
