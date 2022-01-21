from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError
from geodataset.custom_geodataset import (
    CmemsMetIceChart, 
    Dist2Coast,
    Etopo,
    JaxaAmsr2IceConc, 
    NerscDeformation, 
    NerscIceType, 
    OsisafDriftersNextsim,
    SmosIceThickness,
)

custom_read_classes = [
    CmemsMetIceChart, 
    Dist2Coast,
    Etopo,
    JaxaAmsr2IceConc, 
    NerscDeformation, 
    NerscIceType,
    OsisafDriftersNextsim,
    SmosIceThickness,
    # always last:
    GeoDatasetRead,
]

def open_netcdf(file_address):
    """ Open NetCDF with read access and add geospatial metadata 
    
    Returns
    -------
    ds : GeoDataset or custom children
        similar to netCDF4.Dataset with geospatial metadata and methods
    """
    for class_ in custom_read_classes:
        try:
            obj = class_(file_address)
        except InvalidDatasetError:
            continue # skip to the next class in the list
        return obj # return object when try was successful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
