import json, yaml, os, datetime
from pascal_voc_writer import Writer
from jinja2 import Environment, PackageLoader
from PIL import Image

# !!! WARNING: MONKEY PATCH !!!
def _monkey__init__(self, path, width, height, depth=3, database='Unknown', segmented=0):
        environment = Environment(loader=PackageLoader('pascal_voc_writer', 'templates'), keep_trailing_newline=True)
        self.annotation_template = environment.get_template('annotation.xml')

        self.template_parameters = {
            'path': path,
            'filename': os.path.basename(path),
            'folder': 'images',
            'width': width,
            'height': height,
            'depth': depth,
            'database': database,
            'segmented': segmented,
            'objects': []
        }

Writer.__init__ = _monkey__init__

def convert_pascal(datadir, outdir, mapfile):
    """ Generate annotations in PASCAL VOC format. Result will be placed in outdir.

    Parameters
    ----------
    datadir : str
        Location of Rendered.ai dataset output.
    outdir : str
        Location where the results should be written.
    mapfile: str
        The map file used for annotations (YAML only).
    
    Returns
    -------
    """
    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")
    imagedir = os.path.join(datadir, "images")
    annsfiles = os.listdir(annsdir)
    with open(mapfile, 'r') as mf: mapping = yaml.safe_load(mf)

        
    # for each interpretation, gather annotations and map categories
    for f in sorted(annsfiles):
        with open(os.path.join(annsdir,f), 'r') as af: anns = json.load(af)
        with open(os.path.join(metadir,f.replace('ana','metadata')), 'r') as mf: metadata = json.load(mf)
        
        if 'sensor' in metadata and "resolution" in metadata['sensor']:
            width = metadata['sensor']['resolution'][0]
            height = metadata['sensor']['resolution'][1]
        else:
            image = Image.open(os.path.join(imagedir,anns['filename']))
            width = image.size[0]
            height = image.size[1]

        # Writer(path, width, height)
        # TODO: where to get the folder name?
        writer = Writer(anns['filename'], width, height)

        # for each object in the metadata file, check if any of the properties are true
        for obj in metadata['objects']:
            for prop in mapping['properties']:
                if eval(prop):
                    for ann in anns['annotations']:
                        if ann['id'] == obj['id']: 
                            objann = ann
                    cat = mapping['classes'][mapping['properties'][prop]]
                    xmin = objann['bbox'][0]
                    ymin = objann['bbox'][1]
                    xmax = xmin + objann['bbox'][2]
                    ymax = ymin + objann['bbox'][3]
                    # ::addObject(name, xmin, ymin, xmax, ymax)
                    writer.addObject(cat[1], xmin, ymin, xmax, ymax)
                    break
        
        # ::save(path)
        writer.save(os.path.join(outdir,f.replace('-ana.json','.xml')))