"""This module provide class that convert shape file into readable geojson"""

import enum
import geopandas
import os
import datetime
import decimal


class ExtType(enum.Enum):
    """
    Types of file extention
    """
    Tiff = 'tif'

def shp_to_geojson(path):
    shp_file = geopandas.read_file(path)
    geo_json = shp_file._to_geo()
    return geo_json


def generate_oversear_request(shape_metadata_shp, product_shp, files_shp, img_dir):
    request_json = {}

    # generate filename key
    request_json['fileNames'] = []

    for file in files_shp['features']:
        request_json['fileNames'].append(os.path.join(file['properties']['Format'].lower(), ".".join([file['properties']['File Name'], ExtType[file['properties']['Format']].value])))

    # generate metadata
    request_json['metadata'] = {}
    request_json['metadata']['type'] = 'RECORD_RASTER'
    request_json['metadata']['productName'] = shape_metadata_shp['features'][0]['properties']['SourceName']
    request_json['metadata']['description'] = shape_metadata_shp['features'][0]['properties']['Dsc']
    iso_date_time = datetime.datetime.strptime(shape_metadata_shp['features'][0]['properties']['UpdateDate'], '%d/%m/%Y').strftime('%Y-%d-%mT%H:%M:%S:%fZ')
    request_json['metadata']['creationDate'] = iso_date_time
    request_json['metadata']['ingestionDate'] = iso_date_time
    request_json['metadata']['updateDate'] = iso_date_time
    request_json['metadata']['sourceDateStart'] = iso_date_time
    request_json['metadata']['sourceDateEnd'] = iso_date_time
    request_json['metadata']['accuracyCE90'] = shape_metadata_shp['features'][0]['properties']['Ep90']
    request_json['metadata']['sensorType'] = []
    for file in shape_metadata_shp['features']:
        request_json['metadata']['sensorType'].append(file['properties']['SensorType'])

    request_json['metadata']['productId'], request_json['metadata']['productVersion'] = shape_metadata_shp['features'][0]['properties']['Source'].split('-')
    request_json['metadata']['productType'] = product_shp['features'][0]['properties']['Type']
    tfw = ".".join([request_json['fileNames'][0].rsplit('.',1)[0],'tfw']).split('/')[-1]
    with open(os.path.join(img_dir, tfw)) as fp:
        request_json['metadata']['resolution'] = '{0:.10f}'.format(float(fp.readline()))
    request_json['metadata']['footprint'] = shape_metadata_shp['features'][0]['geometry']
    request_json['metadata']['layerPolygonParts'] = { "type":"FeatureCollection",
                                                      "features":shape_metadata_shp['features'],
                                                      "bbox": files_shp['features'][0]['geometry']['coordinates'][0][:-1]}

    return request_json


def add_ext_source_name(shape_file, ext, new_name=False):
    """
    will update shapefile source name
    :param shape_file: original metadata shape file
    :param ext: extension to original name
    :param new_name: if True -> will set ext as entire name
    :return: new rendered name [str]
    """
    shp_file = geopandas.read_file(shape_file)
    if new_name:
        source_new_name = ext
    else:
        source_new_name = "_".join([ext, shp_file.Source[0]])
    # shp_file.Source[0] = source_new_name
    shp_file.Source.update(source_new_name)
    shp_file.to_file(shape_file, encoding='utf-8')

    return source_new_name