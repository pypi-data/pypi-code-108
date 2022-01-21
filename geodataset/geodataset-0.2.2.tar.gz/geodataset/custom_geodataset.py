import os
import re

import numpy as np
import pyproj

from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError

class CustomDatasetRead(GeoDatasetRead):
    pattern = None
    def _check_input_file(self):
        n = os.path.basename(self.filename)
        if not self.pattern.match(n):
            raise InvalidDatasetError


class CmemsMetIceChart(CustomDatasetRead):
    pattern = re.compile(r'ice_conc_svalbard_\d{12}.nc')
    lonlat_names = 'lon', 'lat'


class Dist2Coast(CustomDatasetRead):
    pattern = re.compile(r'dist2coast_4deg.nc')
    lonlat_names = 'lon', 'lat'
    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class Etopo(CustomDatasetRead):
    pattern = re.compile(r'ETOPO_Arctic_\d{1,2}arcmin.nc')

    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class JaxaAmsr2IceConc(CustomDatasetRead):
    pattern = re.compile(r'Arc_\d{8}_res3.125_pyres.nc')
    lonlat_names = 'longitude', 'latitude'
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'


class NerscSarProducts(CustomDatasetRead):
    lonlat_names = 'absent', 'absent'
    def get_lonlat_arrays(self):
        x_grd, y_grd = np.meshgrid(self['x'][:], self['y'][:])
        return self.projection(x_grd, y_grd, inverse=True)
    

class NerscDeformation(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_deformation_\d{8}T\d{6}.nc')


class NerscIceType(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_icetype_\d{8}T\d{6}.nc')


class OsisafDriftersNextsim(CustomDatasetRead):
    pattern = re.compile(r'OSISAF_Drifters_.*.nc')
    grid_mapping = pyproj.CRS.from_proj4(
        " +proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        " +a=6378273 +b=6356889.44891 "), 'absent'
    is_lonlat_2d = False


class SmosIceThickness(CustomDatasetRead):
    pattern = re.compile(r'SMOS_Icethickness_v3.2_north_\d{8}.nc')
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'
