import json
from datetime import date


def validate_pycsw_with_shape_json(pycws_json, shape_json, sync_flag=False):
    missing_values = {}
    error_flag = True
    pycsw_history_json = pycws_json[0]
    pycsw_original_json = pycws_json[1]
    for dic in pycws_json:
        if dic.get('mc:productType') == 'OrthophotoHistory':
            pycsw_history_json = dic
        else:
            pycsw_original_json = dic
    if sync_flag:
        pycsw_original_json = pycsw_history_json
    shape_json_metadata = shape_json['metadata']
    if shape_json_metadata['productId']['value'] != pycsw_original_json['mc:productId']:
        missing_values['productId'] = {'Expected': shape_json_metadata['productId']['value'],
                                       'Actual': pycsw_original_json['mc:productId']}

    if shape_json_metadata['productName']['value'] != pycsw_original_json['mc:productName']:
        missing_values['productName'] = {'Expected': shape_json_metadata['productName']['value'],
                                         'Actual': pycsw_original_json['mc:productName']}

    if shape_json_metadata['productVersion']['value'] != pycsw_original_json['mc:productVersion']:
        missing_values['productVersion'] = {'Expected': shape_json_metadata['productVersion']['value'],
                                            'Actual': pycsw_original_json['mc:productVersion']}

    if shape_json_metadata['productType']['value'] != pycsw_original_json['mc:productType']:
        missing_values['productType'] = {'Expected': shape_json_metadata['productType']['value'],
                                         'Actual': pycsw_original_json['mc:productType']}

    if shape_json_metadata['description']['value'] != pycsw_original_json['mc:description']:
        missing_values['description'] = {'Expected': shape_json_metadata['description']['value'],
                                         'Actual': pycsw_original_json['mc:description']}
    #
    # if date.today().strftime('%Y-%m-%d') != pycsw_original_json['mc:creationDateUTC'].split('T')[0]:
    #     missing_values['creationDate'] = {'Expected': date.today().strftime('%Y-%d-%m'),
    #                                       'Actual': pycsw_original_json['mc:creationDateUTC'].split('T')[0]}
    # ToDo: Uncomment after bug fixed
    # if shape_json_metadata['resolution']['value'] != pycsw_original_json['mc:maxResolutionDeg']:
    #     missing_values['resolution'] = {'Expected': shape_json_metadata['resolution']['value'],
    #                                     'Actual': pycsw_original_json['mc:maxResolutionDeg']}

    if str(shape_json_metadata['accuracyCE90']) != pycsw_original_json['mc:minHorizontalAccuracyCE90']:
        missing_values['Accuracy'] = {'Expected': str(shape_json_metadata['accuracyCE90']),
                                      'Actual': pycsw_original_json['mc:minHorizontalAccuracyCE90']}
    # ToDo: Check if needed to test
    if shape_json_metadata['sensorType']['value'] != pycsw_original_json['mc:sensors']:
        missing_values['sensors'] = {'Expected': shape_json_metadata['sensorType']['value'],
                                     'Actual': pycsw_original_json['mc:sensors']}

    if shape_json_metadata['footprint']['type'] != json.loads(pycsw_original_json['mc:footprint'])['type']:
        missing_values['footprint.type'] = {'Expected': shape_json_metadata['footprint']['type'],
                                            'Actual': json.loads(pycsw_original_json['mc:footprint'])['type']}

    if [[round(k, 9), round(d, 9)] for k, d in shape_json_metadata['footprint']['coordinates'][0]] != [
        [round(k, 9), round(d, 9)] for k, d in (json.loads(pycsw_original_json['mc:footprint']))['coordinates'][0]]:
        missing_values['footprint.coordinates'] = {'Expected': str(
            [[round(k, 9), round(d, 9)] for k, d in shape_json_metadata['footprint']['coordinates'][0]]),
            'Actual': str([[round(k, 9), round(d, 9)] for k, d in
                           (json.loads(pycsw_original_json['mc:footprint']))[
                               'coordinates'][0]])}
    # if json.dumps(shape_json_metadata['footprint']) != pycsw_original_json['mc:footprint']:
    #     missing_values['footprint'] = {'Expected': json.dumps(shape_json_metadata['footprint']),
    #                                    'Actual': pycsw_original_json['mc:footprint']}

    # [[round(k, 9), round(d, 9)] for k, d in shapefile_layer_polygon_parts_json['geometry']['coordinates'][0]] != [
    # [round(x, 9), round(y, 9)] for x, y in pycsw_layer_polygon_parts_json['geometry']['coordinates'][0]]

    if shape_json_metadata['region']['value'] != pycsw_original_json['mc:region']:
        missing_values['region'] = {'Expected': shape_json_metadata['region']['value'],
                                    'Actual': str(pycsw_original_json['mc:region'])}

    if shape_json_metadata['srsId']['value'] != pycsw_original_json['mc:SRS']:
        missing_values['srsId'] = {'Expected': shape_json_metadata['srsId']['value'],
                                   'Actual': str(pycsw_original_json['mc:SRS'])}

    if shape_json_metadata['srsName']['value'] != pycsw_original_json['mc:SRSName']:
        missing_values['srsName'] = {'Expected': shape_json_metadata['srsName']['value'],
                                     'Actual': str(pycsw_original_json['mc:SRSName'])}

    if date.today().strftime('%Y-%m-%d') != pycsw_original_json['mc:ingestionDate'].split('T')[0]:
        missing_values['ingestionDate'] = {'Expected': date.today().strftime('%Y-%d-%m'),
                                           'Actual': pycsw_original_json['mc:ingestionDate'].split('T')[0]}

    if shape_json_metadata['type'] != pycsw_original_json['mc:type']:
        missing_values['type'] = {'Expected': shape_json_metadata['type'],
                                  'Actual': str(pycsw_original_json['mc:type'])}

    # if shape_json_metadata['maxResolutionMeter']['value'] != pycsw_original_json['mc:maxResolutionMeter']:
    #     missing_values['maxResolutionMeter'] = {'Expected': str(shape_json_metadata['maxResolutionMeter']['value']),
    #                                             'Actual': str(pycsw_original_json['mc:maxResolutionMeter'])}

    if shape_json_metadata['producerName']['value'] != pycsw_original_json['mc:producerName']:
        missing_values['producerName'] = {'Expected': str(shape_json_metadata['producerName']['value']),
                                          'Actual': str(pycsw_original_json['mc:producerName'])}

    # ToDo : Finish layerPolygonParts
    pycsw_layer_polygon_parts_json = json.loads(pycsw_original_json['mc:layerPolygonParts'])['features'][0]
    shapefile_layer_polygon_parts_json = shape_json_metadata['layerPolygonParts']['value']['features'][0]

    if shapefile_layer_polygon_parts_json['type'] != pycsw_layer_polygon_parts_json['type']:
        missing_values['layerPolygonParts.type'] = {'Expected': shapefile_layer_polygon_parts_json['type'],
                                                    'Actual': str(pycsw_layer_polygon_parts_json['type'])}

    if shapefile_layer_polygon_parts_json['geometry']['type'] != pycsw_layer_polygon_parts_json['geometry']['type']:
        missing_values['layerPolygonParts.geometry.type'] = {
            'Expected': shapefile_layer_polygon_parts_json['geometry']['type'],
            'Actual': str(pycsw_layer_polygon_parts_json['geometry']['type'])}
    #
    # if shapefile_layer_polygon_parts_json['geometry']['coordinates'] != pycsw_layer_polygon_parts_json['geometry'][
    #     'coordinates']:
    #     missing_values['layerPolygonParts.geometry.coordinates'] = {
    #         'Expected': str(shapefile_layer_polygon_parts_json['geometry']['coordinates']),
    #         'Actual': str(pycsw_layer_polygon_parts_json['geometry']['coordinates']).replace('[', '(').replace(']',
    #                                                                                                            ')')}

    if shapefile_layer_polygon_parts_json['properties']['Dsc'] != pycsw_layer_polygon_parts_json['properties']['Dsc']:
        missing_values['layerPolygonParts.properties.Dsc'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['Dsc']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['Dsc'])}

    if shapefile_layer_polygon_parts_json['properties']['Rms'] != pycsw_layer_polygon_parts_json['properties']['Rms']:
        missing_values['layerPolygonParts.properties.Rms'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['Rms']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['Rms'])}

    if shapefile_layer_polygon_parts_json['properties']['Ep90'] != pycsw_layer_polygon_parts_json['properties']['Ep90']:
        missing_values['layerPolygonParts.properties.Ep90'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['Ep90']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['Ep90'])}

    if shapefile_layer_polygon_parts_json['properties']['Scale'] != pycsw_layer_polygon_parts_json['properties'][
        'Scale']:
        missing_values['layerPolygonParts.properties.Scale'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['Scale']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['Scale'])}

    if shapefile_layer_polygon_parts_json['properties']['SensorType'] != pycsw_layer_polygon_parts_json['properties'][
        'SensorType']:
        missing_values['layerPolygonParts.properties.SensorType'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['SensorType']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['SensorType'])}

    if shapefile_layer_polygon_parts_json['properties']['SourceName'] != pycsw_layer_polygon_parts_json['properties'][
        'SourceName']:
        missing_values['layerPolygonParts.properties.SourceName'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['SourceName']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['SourceName'])}

    if shapefile_layer_polygon_parts_json['properties']['UpdateDate'] != pycsw_layer_polygon_parts_json['properties'][
        'UpdateDate']:
        missing_values['layerPolygonParts.properties.UpdateDate'] = {
            'Expected': str(shapefile_layer_polygon_parts_json['properties']['UpdateDate']),
            'Actual': str(pycsw_layer_polygon_parts_json['properties']['UpdateDate'])}

    # if str(shape_json_metadata['layerPolygonParts']['bbox']).replace('[', '').replace(']', '').replace(' ', '') != \
    #         pycsw_original_json['mc:productBBox']:
    #     missing_values['productBBox'] = {
    #         'Expected': (str(shape_json_metadata['layerPolygonParts']['bbox']).replace('[', '').replace(']',
    #                                                                                                     '').replace(
    #             ' ', '')),
    #         'Actual': str(pycsw_original_json['mc:productBBox'])}

    if [[round(k, 9), round(d, 9)] for k, d in shapefile_layer_polygon_parts_json['geometry']['coordinates'][0]] != [
        [round(x, 9), round(y, 9)] for x, y in pycsw_layer_polygon_parts_json['geometry']['coordinates'][0]]:
        missing_values['layerPolygonParts.bbox'] = {
            'Expected': str([[round(k, 9), round(d, 9)] for k, d in
                             shapefile_layer_polygon_parts_json['geometry']['coordinates'][0]]),
            'Actual': str([
                [round(x, 9), round(y, 9)] for x, y in pycsw_layer_polygon_parts_json['geometry']['coordinates'][0]])}

    #
    # for k, v in json.loads(pycsw_original_json['mc:layerPolygonParts']).items():
    #     try:
    #         if k == 'bbox':
    #             if shape_json_metadata['layerPolygonParts']['bbox'] != v:
    #                 missing_values[k] = {'Expected': str(shape_json_metadata['layerPolygonParts']['bbox']),
    #                                      'Actual': str(v)}
    #         elif shape_json_metadata['layerPolygonParts']['value'][k] != v:
    #             missing_values[k] = {'Expected': str(shape_json_metadata['layerPolygonParts']['value'][k]),
    #                                  'Actual': str(v)}
    #             # missmatch_values[o_k] = 'Expected : ' + str(o_v) + ' , Actual : ' + str(shape_json['metadata'][o_k])
    #     except KeyError:
    #         missing_values[k] = {'Expected': str(v), 'Actual': 'Missing Key in PYCSW JSON'}
    #         error_flag = False
    if len(missing_values) != 0:
        error_flag = False
    return error_flag, missing_values
    #
    # if is_history:
    #     pass
    # if pycws_json is None:
    #     missing_values['PYCSW_JSON'] = 'Empty JSON'
    #     return False, missing_values
    # if shape_json is None:
    #     missing_values['ShapeJSON'] = 'Empty JSON'
    #     return False, missing_values

    #
    #
    #
    #
    # try:
    #     # ToDo: Added History Ortophoto JSON.
    #     original_ortophoto_json = pycws_json['data']['search'][0]
    #
    # except KeyError:
    #     missing_values['data']['search'] = {'Expected': 'JSON', 'Actual': 'Missing JSON'}
    #     error_flag = False
    #
    # for o_k, o_v in original_ortophoto_json.items():
    #     if o_k is not '__typename':
    #         try:
    #             if shape_json['metadata'][o_k] != o_v:
    #                 missing_values[o_k] = {'Expected': str(o_v), 'Actual': str(shape_json['metadata'][o_k])}
    #                 # missmatch_values[o_k] = 'Expected : ' + str(o_v) + ' , Actual : ' + str(shape_json['metadata'][o_k])
    #         except KeyError:
    #             missing_values[o_k] = {'Expected': str(o_v), 'Actual': 'Missing Key in PYCSW JSON'}
    #             error_flag = False

    # history_ortophoto_json = pycws_json['data']['search'][1]

    # return error_flag, missing_values


def validate_pycsw_with_shape_json_old_version(pycws_json, shape_json):
    missing_values = {}
    error_flag = True

    if pycws_json is None:
        missing_values['PYCSW_JSON'] = 'Empty JSON'
        return False, missing_values
    if shape_json is None:
        missing_values['ShapeJSON'] = 'Empty JSON'
        return False, missing_values

    try:
        # ToDo: Added History Ortophoto JSON.
        original_ortophoto_json = pycws_json['data']['search'][0]

    except KeyError:
        missing_values['data']['search'] = {'Expected': 'JSON', 'Actual': 'Missing JSON'}
        error_flag = False

    for o_k, o_v in original_ortophoto_json.items():
        if o_k is not '__typename':
            try:
                if shape_json['metadata'][o_k] != o_v:
                    missing_values[o_k] = {'Expected': str(o_v), 'Actual': str(shape_json['metadata'][o_k])}
                    # missmatch_values[o_k] = 'Expected : ' + str(o_v) + ' , Actual : ' + str(shape_json['metadata'][o_k])
            except KeyError:
                missing_values[o_k] = {'Expected': str(o_v), 'Actual': 'Missing Key in PYCSW JSON'}
                error_flag = False

    return error_flag, missing_values
