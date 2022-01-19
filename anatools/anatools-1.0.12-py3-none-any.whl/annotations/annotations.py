from .convert_coco import convert_coco
from .convert_kitti import convert_kitti
from .convert_pascal import convert_pascal

class Annotations:
    """Generates annotations given a dataset directory, an output directory and mapping file.
    The dataset directory must include the Ana annotations, images and metadata folders.
    Examples of mapfiles are in the example channel at /ana/channels/example/mapfiles/.
    """

    def dump_coco(self, datadir, outdir, mapfile):
        """Generates annotations in the format of COCO Object Detection. See https://cocodataset.org/#format-data.
        
        Parameters
        ----------
        datadir : str
            The location of the Ana dataset.
        outdir : str
            The location to output the annotation files to.
        mapfile: str
            The location of the mapping file.
        """
        convert_coco(datadir, outdir, mapfile)

    def dump_kitti(self, datadir, outdir, mapfile):
        """Generates annotations in the format of KITTI. See https://docs.nvidia.com/metropolis/TLT/archive/tlt-20/tlt-user-guide/text/preparing_data_input.html.
        
        Parameters
        ----------
        datadir : str
            The location of the Ana dataset.
        outdir : str
            The location to output the annotation files to.
        mapfile: str
            The location of the mapping file.
        """
        convert_kitti(datadir, outdir, mapfile)

    def dump_pascal(self, datadir, outdir, mapfile):
        """Generates annotations in the format of PASCAL VOC. See https://pjreddie.com/media/files/VOC2012_doc.pdf.
        
        Parameters
        ----------
        datadir : str
            The location of the Ana dataset.
        outdir : str
            The location to output the annotation files to.
        mapfile: str
            The location of the mapping file.
        """
        convert_pascal(datadir, outdir, mapfile)
