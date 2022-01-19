import json, yaml, os, datetime

def create_cocodata():
    cocodata = dict()
    cocodata['info'] = {    
        "description":  "Rendered.AI Synthetic Dataset",
        "url":          "https://rendered.ai/",
        "contributor":  "info@rendered.ai",
        "version":      "1.0",
        "year":         str(datetime.datetime.now().year),
        "date_created": datetime.datetime.now().isoformat()}
    cocodata['licenses'] = [{
        "id":   0,
        "url":  "https://rendered.ai/",     # "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "name": "Rendered.AI License"}]     # "name": "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License"}]
    cocodata['images'] = list()
    cocodata['categories'] = list()
    cocodata['annotations'] = list()
    return cocodata


def convert_coco(datadir, outdir, mapfile):
    """ Generate annotations in COCO format. Result will be placed in outdir.

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
    annsfiles = os.listdir(annsdir)
    with open(mapfile, 'r') as mf: mapping = yaml.safe_load(mf)
    
    cocodata = create_cocodata()
    annotations = []
    categories = []
    cats = []
    imgid = 0
    annid = 0
        
     # for each interpretation, gather annotations and map categories
    for f in sorted(annsfiles):
        with open(os.path.join(annsdir,f), 'r') as af: anns = json.load(af)
        with open(os.path.join(metadir,f.replace('ana','metadata')), 'r') as mf: metadata = json.load(mf)
        
        # for each object in the metadata file, check if any of the properties are true
        for obj in metadata['objects']:
            for prop in mapping['properties']:
                if eval(prop):
                    for ann in anns['annotations']:
                        if ann['id'] == obj['id']: 
                            objann = ann
                    cat = mapping['classes'][mapping['properties'][prop]]
                    if cat not in cats: cats.append(cat)
                    annotation = {}
                    annotation['id'] = annid
                    annotation['image_id'] = imgid
                    annotation['category_id'] = cats.index(cat)
                    annotation['segmentation'] = objann['segmentation']
                    annotation['area'] = objann['bbox'][2] * objann['bbox'][3]
                    annotation['bbox'] = objann['bbox']
                    annotation['iscrowd'] = 0
                    annid += 1
                    cocodata['annotations'].append(annotation)
                    break
        imgdata = {
            'id':               imgid, 
            'file_name':        metadata['filename'], 
            'date_captured':    metadata['date'], 
            'license':          0 }
        if 'sensor' in metadata:
            metadata['width'] =  metadata['sensor']['resolution'][0],
            metadata['height']=  metadata['sensor']['resolution'][1],
            if 'frame' in metadata['sensor']: metadata['frame'] = metadata['sensor']['frame']
        cocodata['images'].append(imgdata)
        imgid += 1
    for cat in cats:
        cocodata['categories'].append({
            'id':               cats.index(cat), 
            'name':             cat[-1],
            'supercategory':    cat[0]
        })

    with open(os.path.join(outdir,'coco.json'), 'w+') as of:
        json.dump(cocodata,of)



def coco_panoptic_segmentation(annsdir, metadir, outdir, mapfile):
    annsfiles = os.listdir(annsdir)
    with open(mapfile, 'r') as mf: mapping = yaml.safe_load(mf)
    
    cocodata = create_cocodata()
    annotations = []
    categories = []
    cats = []
    imgid = 0
        
        # for each interpretation, gather annotations and map categories
    for f in sorted(annsfiles):
        with open(os.path.join(annsdir,f), 'r') as af: anns = json.load(af)
        with open(os.path.join(metadir,f.replace('ana','metadata')), 'r') as mf: metadata = json.load(mf)
        with open(os.path.join(annsdir,f.replace('ana','legend')), 'r') as lf: imglegend = json.load(lf)
        imgcats = []

        # for each object in the metadata file, check if any of the properties are true
        annotation = {}
        annotation['image_id'] = imgid
        annotation['file_name'] = metadata['filename']
        annotation['segments_info'] = []
        for obj in metadata['objects']:
            for prop in mapping['properties']:
                if eval(prop):
                    for ann in anns['annotations']:
                        if ann['id'] == obj['id']: 
                            objann = ann
                    cat = mapping['classes'][mapping['properties'][prop]]
                    imgcats.append(obj['type'])
                    segment_info = {}
                    seg = ann['segmentation'].flatten()
                    r,g,b = imglegend[obj['type']]
                    segment_info['id'] = r + g*256 + b*256**2
                    segment_info['category_id'] = cats.index(cat)
                    segment_info['area'] = objann['bbox'][2] * objann['bbox'][3]
                    segment_info['bbox'] = objann['bbox']
                    segment_info['z'] = objann['distance']
                    segment_info['bbox3d'] = objann['bbox3d']   # added for amentum
                    segment_info['iscrowd'] = 0
                    annotation['segments_info'].append(annotation)
                    break
        for cat in imglegend.keys:
            if cat not in imgcats and cat not in imgcats: cats.append(cat)

        imgdata = {
            'id':               imgid, 
            'file_name':        metadata['filename'], 
            'date_captured':    metadata['date'], 
            'license':          0 }
        if 'sensor' in metadata:
            metadata['width'] =  metadata['sensor']['resolution'][0],
            metadata['height']=  metadata['sensor']['resolution'][1],
            if 'frame' in metadata['sensor']: metadata['frame'] = metadata['sensor']['frame']
        cocodata['images'].append(imgdata)
        imgid += 1

    for i,cat in enumerate(cats):
        cocodata['categories'].append({
            'id':               i, 
            'name':             cat[0],
            'supercategory':    cat[0],
            'isthing':          1,
        })

    with open(os.path.join(outdir,'coco.json'), 'w+') as of:
        json.dump(cocodata,of)