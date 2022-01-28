from . import utils
from .ascii import ASCII
from .data_container_csv import DataContainerCSV
from .gwinstek import Gwinstek
from .gwinstek_lsf import Gwinstek_LSF
from .hp4395a import HP4395A
from .hp4395a_gpib import HP4395A_GPIB
from .keysight_binary import KeysightBinary
from .keysight_csv import KeysightCSV
from .keysight_fra import KeysightFRA
from .keysight_visa import KeysightVisa
from .rohde_schwarz import RohdeSchwarz
from .rohde_schwarz_visa import RohdeSchwarzVisa
from .tektronix import Tektronix
from .tektronix_dpx import TektronixDPX
from .tektronix_spectrogram import TektronixSpectrogram

# TODO maybe refactoring
# IMPORTER_DIR = os.path.abspath(__file__)
#
# IMPORTER_DIR = os.path.dirname(IMPORTER_DIR)
#
# for fn in glob.glob(IMPORTER_DIR + "/*.py"):
#     importer = utils.get_file_basename(fn)
#     if importer in ("__init__", "utils"):
#         continue
#     try:
#         importer_module = importlib.import_module(
#             "openqlab.io.importers." + importer, package="openqlab.io.importers"
#         )
#         for m in inspect.getmembers(importer_module, inspect.isclass):
#             name, klass = m
#             if issubclass(klass, BaseImporter):
#                 globals()[name] = klass
#     except ImportError as e:
#         print(e)
#         continue
