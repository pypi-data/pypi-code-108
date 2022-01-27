from ocs_archive.input.file import FileSpecificationException
from ocs_archive.input.tarwithfitsfile import TarWithFitsFile
from ocs_archive.input.lcofitsfile import LcoFitsFile


class LcoTarWithFitsFile(TarWithFitsFile, LcoFitsFile):
    @staticmethod
    def _get_meta_file_from_targz(tarfileobj):
        for member in tarfileobj.getmembers():
            if any(x + '.fits' in member.name for x in ['e00', 'e90', 'e91']) and member.isfile():
                return tarfileobj.extractfile(member)
        raise FileSpecificationException('Tar file missing meta fits!')
