from itertools import islice

class UtilsTimeSeries():

    def _tsCollectionToString(collection:list) -> str:
        """Converts a list of dicts with time series data into graphQL string"""

        tsData = '[\n'
        for item in collection:
            tsData += '{\n'
            for key, value in item.items():
                if key in ['sys_inventoryId', 'sys_inventoryItemId']:
                    tsData += f'  {key}: "{value}"\n'
                elif key == 'data':
                    tsData += '  data: {\n'
                    for dkey, dvalue in value.items():
                        if dkey == 'resolution':
                            tsData += f'''  resolution: {{timeUnit: {dvalue['timeUnit']}, factor: {dvalue['factor']}}}\n'''
                        elif dkey == 'unit':
                            tsData += f'''  unit: "{dvalue}"\n'''
                        elif dkey == 'dataPoints':
                            tsData += '    dataPoints: [\n'
                            for dp_key in dvalue:
                                tsData += f'''     {{timestamp: "{dp_key['timestamp']}", value: {dp_key['value']}}}\n'''
                            tsData += '    ]\n'
                        else: pass
                    tsData += '  }\n'
                else:pass
            tsData += '}\n'
        tsData += ']\n'
        return tsData

    def _dataPointsToString(dataPoints:dict) -> str:
        """Converts a dictionary of datapoints to graphQL string"""

        _dataPoints = ''
        for timestamp, value in dataPoints.items():
            if value == None:
                _dataPoints += f'''{{
                    timestamp: "{timestamp}"
                    value: 0
                    flag: MISSING
                    }}\n'''
            else: 
                _dataPoints += f'''{{
                        timestamp: "{timestamp}"
                        value: {value}
                        }}\n'''

        return _dataPoints

    def _sliceDataPoints(dataPoints:dict, start:int, stop:int):
        """Return a slice of the dataPoints dictionary"""

        return dict(islice(dataPoints, start, stop))