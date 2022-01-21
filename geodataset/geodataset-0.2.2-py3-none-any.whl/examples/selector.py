from glob import glob
from os.path import join

import numpy as np
from pyresample import bilinear

from geodataset.tools import open_netcdf
from geodataset.interpolation import GridGridInterpolator


def main():
    search_folder = "/workspaces/Regridder/data"
    search_path = join(search_folder, "**/*.nc")
    target_file_address = '/workspaces/Regridder/data/ice_conc_nh_polstere-100_multi_202106131200.nc'
    target = open_netcdf(target_file_address)
    list_of_netcdf_files = glob(search_path, recursive=True)
    list_of_netcdf_files.remove(target_file_address)
    dictionary_of_objects = dict.fromkeys(list_of_netcdf_files)
    for file_ in list_of_netcdf_files:
        source = dictionary_of_objects[file_] = open_netcdf(file_)
        ggi = GridGridInterpolator(
                    source.area, target.area, method=bilinear.NumpyBilinearResampler,
                    radius_of_influence=15000
                                  )
        cons_from_nc_file = np.ones(source.area.shape)
        #cons_from_nc_file = source.get_var('sea_ice_concentration', time_index=0).values
        source._set_time_info()
        resampled_data_cons = ggi(cons_from_nc_file)

if __name__ == "__main__":
    main()
