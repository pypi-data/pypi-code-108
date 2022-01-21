import datetime as dt
from functools import lru_cache

from netCDF4 import Dataset
import netcdftime
import numpy as np
import pyproj
from pyproj.exceptions import CRSError
from scipy.interpolate import RegularGridInterpolator
from xarray.core.variable import MissingDimensionsError

from geodataset.utils import InvalidDatasetError, fill_nan_gaps

class GeoDatasetBase(Dataset):
    """ Abstract wrapper for netCDF4.Dataset for common input or ouput tasks """
    lonlat_names = None
    projection = None
    time_name = 'time'
    is_lonlat_2d = True


    def __init__(self, *args, **kwargs):
        """
        Initialise the object using netCDF4.Dataset()

        Sets:
        -----
        filename : str
            name of input file
        """
        super().__init__(*args, **kwargs)
        self.filename = args[0]
        self._check_input_file()

    def __setattr__(self, att, val):
        """ set object attributes (not netcdf attributes)
        This method overrides netCDF4.Dataset.__setattr__, which calls netCDF4.Dataset.setncattr """
        self.__dict__[att] = val

    def _check_input_file(self):
        """ Check if input file is valid for the current class or raise InvalidDatasetError """
        pass

    def convert_time_data(self, tdata):
        """
        Convert numeric time values to datetime.datetime objects.
        Uses time units of variable with name self.time_name

        Parameters:
        -----------
        time_num : numpy.ndarray(float)

        Returns:
        --------
        time : numpy.ndarray(datetime.datetime)
        """
        atts = vars(self.variables[self.time_name])
        cal = atts.get('calendar', 'standard')
        units = atts['units']
        datetimes = [netcdftime.num2date(t, units, calendar=cal) for t in tdata]
        return np.array(datetimes).reshape(tdata.shape)

    @property
    def is_lonlat_dim(self):
        """
        Returns:
        --------
        is_lonlat_dim : bool
            True if lon,lat are dimensions
        """
        return (self.lonlat_names[0] in self.dimensions)

    @property
    def datetimes(self):
        """
        Returns:
        --------
        datetimes : list(datetime.datetime)
            all the time values converted to datetime objects
        """
        if self.time_name is None:
            return []
        return list(self.convert_time_data(self.variables[self.time_name][:]))

    def get_nearest_date(self, pivot):
        """ Get date from the Dataset closest to the input date
        
        Parameters
        ----------
        pivot : datetime.datetime
            searching date

        Returns
        -------
        dto : datetime.datetime
            value nearest date
        time_index : int
            index of the nearest date

        """
        dto = min(self.datetimes, key=lambda x: abs(x - pivot))
        time_index = self.datetimes.index(dto)
        return dto, time_index


class GeoDatasetWrite(GeoDatasetBase):
    """ Wrapper for netCDF4.Dataset for common ouput tasks """
    grid_mapping_variable = None
    spatial_dim_names = ('x', 'y')
    time_name = 'time'
    lonlat_names = ('longitude', 'latitude')    
    projection = pyproj.Proj(
            "+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-45 "
            " +x_0=0 +y_0=0 +R=6378273 +ellps=sphere +units=m")

    def set_projection_variable(self):
        """
        set projection variable.

        See conventions in:
        http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html

        Check netcdf files at:
        http://cfconventions.org/compliance-checker.html
        """
        pvar = self.createVariable(self.grid_mapping_variable, 'i1')
        pvar.setncatts(self.get_grid_mapping_ncattrs())

    def set_time_variables_dimensions(self, time_data, time_atts, time_bnds_data):
        """
        set the temporal dimensions (time, nv)
        and variables (time, time_bnds)

        Parameters:
        -----------
        time_data : np.array
            data for time variable
        time_atts : dict
            netcdf attributes for time variable
        time_bnds_data : np.array
            data for time_bnds variable
        time_bnds_atts : dict
            netcdf attributes for time_bnds variable
        """
        # dimensions
        self.createDimension('time', None)#time should be unlimited
        self.createDimension('nv', 2)
        # time should have units and a calendar attribute
        ncatts = dict(**time_atts)
        ncatts['calendar'] = time_atts.get('calendar', 'standard')
        units = time_atts['units']
        # time var
        tvar = self.createVariable('time', 'f8', ('time',), zlib=True)
        tvar.setncatts(ncatts)
        tvar[:] = time_data
        # time_bnds var - just needs units
        tbvar = self.createVariable('time_bnds', 'f8', ('time', 'nv'), zlib=True)
        tbvar.setncattr('units', units)
        tbvar[:] = time_bnds_data

    def set_xy_dims(self, x, y):
        """
        set the x,y dimensions and variables

        Parameters:
        -----------
        x : np.ndarray
            vector of x coordinate (units = m)
        y : np.ndarray
            vector of y coordinate (units = m)
        """
        for dim_name, dim_vec in zip(['y', 'x'], [y, x]):
            dst_dim = self.createDimension(dim_name, len(dim_vec))
            dst_var = self.createVariable(dim_name, 'f8', (dim_name,), zlib=True)
            dst_var.setncattr('standard_name', 'projection_%s_coordinate' %dim_name)
            dst_var.setncattr('units', 'm')
            dst_var.setncattr('axis', dim_name.upper())
            dst_var[:] = dim_vec

    def set_lonlat(self, lon, lat):
        """
        set the lon, lat variables

        Parameters:
        -----------
        lon : np.ndarray
            array of longitudes (units = degrees_east)
        lat : np.ndarray
            array of latitudes (units = degrees_north)
        """
        data_units = [
                ('longitude', lon, 'degrees_east'),
                ('latitude',  lat, 'degrees_north'),
                ]
        dims = tuple(self.spatial_dim_names[::-1])
        for vname, data, units in data_units:
            dst_var = self.createVariable(vname, 'f8', dims, zlib=True)
            dst_var.setncattr('standard_name', vname)
            dst_var.setncattr('long_name', vname)
            dst_var.setncattr('units', units)
            dst_var[:] = data

    def set_variable(self, vname, data, dims, atts, dtype='f4'):
        """
        set variable data and attributes

        Parameters:
        -----------
        vname : str
            name of new variable
        data : numpy.ndarray
            data to set in variable
        dims : list(str)
            list of dimension names for the variable
        atts : dict
            netcdf attributes to set
        dtype : str
            netcdf data type for new variable (eg 'f4' or 'f8')
        """
        type_converter = dict(f4=np.float32, f8=np.double)[dtype]
        ncatts = {k:v for k,v in atts.items() if k != '_FillValue'}
        kw = dict(zlib=True)# use compression
        if '_FillValue' in atts:
            # needs to be a keyword for createVariable and of right data type
            kw['fill_value'] = type_converter(atts['_FillValue'])
        if 'missing_value' in atts:
            # needs to be of right data type
            ncatts['missing_value'] = type_converter(atts['missing_value'])
        dst_var = self.createVariable(vname, dtype, dims, **kw)
        ncatts['grid_mapping'] = self.grid_mapping_variable
        dst_var.setncatts(ncatts)
        dst_var[:] = data

    def get_grid_mapping_ncattrs(self):
        '''
        Get the netcdf attributes to set for a netcdf projection variable.
        See https://www.unidata.ucar.edu/software/netcdf-java/current/reference/StandardCoordinateTransforms.html

        '''
        gm_attrs = self.projection.crs.to_cf()
        gm_attrs.update({'proj4': str(self.projection.crs)})
        return gm_attrs


class GeoDatasetRead(GeoDatasetBase):
    """ Wrapper for netCDF4.Dataset for common input tasks """

    @property
    @lru_cache(1)
    def lonlat_names(self):
        """ Get names of latitude longitude following CF and ACDD standards 
        
        Returns
        -------
        lon_var_name : str
        lat_var_name : str
        
        """
        lon_standard_name = 'longitude'
        lat_standard_name = 'latitude'
        lon_var_name = lat_var_name = None
        for var_name, var_val in self.variables.items():
            if 'standard_name' in var_val.ncattrs():
                if var_val.standard_name == lon_standard_name:
                    lon_var_name = var_name
                if var_val.standard_name == lat_standard_name:
                    lat_var_name = var_name
            if lon_var_name and lat_var_name:
                return lon_var_name, lat_var_name
        raise InvalidDatasetError

    @property
    @lru_cache(1)
    def variable_names(self):
        """ Find valid names of variables excluding names of dimensions, projections, etc
        
        Returns
        -------
        var_names : list of str
            names of valid variables

        """
        bad_names = list(self.dimensions.keys())
        var_names = list(self.variables.keys())
        bad_names.append(self.grid_mapping_variable)
        bad_names += ['time_bnds']
        for bad_name in bad_names:
            if bad_name in var_names:
                var_names.remove(bad_name)
        return var_names

    @property
    def projection(self):
        """ Read projection of the dataset from self.grid_mapping
        
        Returns
        -------
        projection : pyproj.Proj

        """
        return pyproj.Proj(self.grid_mapping[0])

    @property
    def grid_mapping_variable(self):
        """ Read name of the grid mapping variable from self.grid_mapping
        
        Returns
        -------
        grid_mapping_variable : str

        """
        return self.grid_mapping[1]
    
    @property
    @lru_cache(1)
    def grid_mapping(self):
        """ Load CRS and grid mapping variable name from CF-attrinbutes OR from lon/lat
        If grid mapping cannot be loaded from file, InvalidDatasetError is raised
        
        Returns
        -------
        csr : pyproj.CRS
            coordinate reference system
        v : str
            name of grid_mapping_variable or "absent"

        """
        crs, v = self.get_grid_mapping_from_cf_attrs()
        if not crs:
            crs, v = self.get_grid_mapping_from_lonlat()
            if not crs:
                raise InvalidDatasetError
        return crs, v
        
    def get_grid_mapping_from_cf_attrs(self):
        """ Load CRS and grid mapping var name from CF-attributes
        
        Returns
        -------
        csr : pyproj.CRS or None
            coordinate reference system
        v : str or None
            name of grid mapping variable

        """
        for var_name, variable in self.variables.items():
            attrs = {attr:variable.getncattr(attr) for attr in variable.ncattrs()}
            try:
                crs = pyproj.CRS.from_cf(attrs)
            except CRSError:
                pass
            else:
                return crs, var_name
        return None, None

    def get_grid_mapping_from_lonlat(self):
        """ Check if longitude and latitude are dimentions and return longlat CRS and "absent",
        otherwise return None, None
        
        Returns
        -------
        csr : pyproj.CRS or None
            coordinate reference system
        v : str
            name of grid mapping variable

        """
        lon_is_dim = False
        lat_is_dim = False
        for d in self.dimensions:
            if d in self.variables:
                if 'standard_name' in self.variables[d].ncattrs():
                    if self.variables[d].standard_name == 'longitude':
                        lon_is_dim = True
                    elif self.variables[d].standard_name == 'latitude':
                        lat_is_dim = True
            if lon_is_dim and lat_is_dim:
                return pyproj.CRS(
                    '+proj=longlat +datum=WGS84 +no_defs +type=crs'), 'absent'
        return None, None

    def get_variable_array(
        self, var_name, time_index=0, ij_range=(None, None, None, None)):
        """ Get array with values from a given variable. 
        If variable has time dimension, time_index is used.
        
        Parameters
        ----------
        var_name : str
            name of variable
        time_index: int
            from which time layer to read data
        ij_range : tuple with 4 ints
            start/stop along i and j (y and x) axis

        Returns
        -------
        array : 2D numpy.array
            data from variable from time_index

        """
        if 'time' in self[var_name].dimensions:
            return self[var_name][
                time_index, ij_range[0]:ij_range[1], ij_range[2]:ij_range[3]]
        else:
            return self[var_name][
                ij_range[0]:ij_range[1], ij_range[2]:ij_range[3]]


    def get_lonlat_arrays(self, ij_range=(None, None, None, None)):
        """ Get array with longitude latidtude arrays 
        
        Parameters
        ----------
        ij_range : tuple with 4 ints
            start/stop along i and j (y and x) axis

        Returns
        -------
        lonlat_arrays : 2 2D-numpy.arrays
            longitude and latitude

        """        
        return [
            self.get_variable_array(name, ij_range) 
            for name in self.lonlat_names]

    def get_area_euclidean(self, mapping, ij_range=(None, None, None, None)):
        """
        Calculates element area from netcdf file
        Assumes regular grid in the given projection

        Parameters:
        -----------
        mapping : pyproj.Proj
            translate from lonlat to projected coordinates
        ij_range : tuple with 4 ints
            start/stop along i and j (y and x) axis

        Returns:
        --------
        * area (float)
        """
        lon, lat = self.get_lonlat_arrays(ij_range)
        x, y = mapping(lon, lat)
        dy, dx = [np.max([
            np.abs(np.mean(z[:, 2]-z[:, 1])), 
            np.abs(np.mean(z[1, :]-z[0, :]))])
            for z in [y, x]]
        return np.abs(dx*dy)

    def get_bbox(self, mapping):
        """ Get bounding box (extent)
        Parameters:
        * mapping: pyproj mapping

        Returns:
        * bbox = [xmin, xmax, ymin, ymax], where x,y are coordinates specified by mapping
        """

        lon, lat = self.get_lonlat_arrays()
        x, y = mapping(lon, lat)
        return [x.min(), x.max(), y.min(), y.max()]

    def get_xy_dims_from_lonlat(self, lon, lat, accuracy=1e3):
        """
        Get the x,y vectors for the dimensions if they are not provided in the netcdf file
        Assumes a regular grid in the input projection

        Parameters:
        -----------
        lon : np.ndarray
            2d longitude array, units = degrees_east
        lat : np.ndarray
            2d latitude array, units = degrees_north
        accuracy : float
            desired accuracy in m - we round to this accuracy so
            that x and y are regularly spaced

        Returns:
        --------
        x : np.ndarray
            x coordinate vector, units = m
        y : np.ndarray
            y coordinate vector, units = m
        """
        assert(not self.is_lonlat_dim)
        x = self.projection(lon[0,:], lat[0,:])[0]
        y = self.projection(lon[:,0], lat[:,0])[1]
        return [np.round(v/accuracy)*accuracy for v in [x, y]]

    def get_proj_info_kwargs(self):
        """ Create dictionary with NC attributes for grid mapping variable
        
        Returns
        -------
        kwargs : dict
            NC attributes for grid mapping variable + proj
        
        """
        g = self.projection.crs.get_geod()
        d = self.projection.crs.to_dict()
        kwargs = dict(
            proj = d['proj'],
            lat_0 = d['lat_0'],
            lat_ts = d['lat_ts'],
            lon_0 = d['lon_0'],
            a = g.a,
            ecc = g.es,
        )
        return kwargs

    def get_var_for_nextsim(self, var_name, nbo, 
        distance=5, on_elements=True, fill_value=np.nan, **kwargs):
        """ Interpolate netCDF data onto mesh from NextsimBin object
        
        Parameters
        ----------
        var_name : str
            name of variable
        nbo : NextsimBin
            nextsim bin object with mesh_info attribute
        distance : int
            extrapolation distance (in pixels) to avoid land contamintation
        on_elements : bool
            perform interpolation on elements or nodes?
        fill_value : bool
            value for filling out of bound regions
        kwargs : dict
            dummy
        
        Returns
        -------
        v_pro : 1D nupy.array
            values from netCDF interpolated on nextsim mesh
        
        """
        # get self coordinates
        nc_lon, nc_lat = self.get_lonlat_arrays()
        if len(nc_lon.shape) < 2 or len(nc_lat.shape) < 2:
            raise ValueError('Can inteporlate only 2D data from netCDF file')
        # get variable
        nc_v = self.get_variable_array(var_name).filled(np.nan)

        # get elements coordinates in neXtSIM projection
        nb_x, nb_y = nbo.mesh_info.get_nodes_xy()
        t = nbo.mesh_info.get_indices() - 1
        if on_elements:
            nb_x, nb_y = [i[t].mean(axis=1) for i in [nb_x, nb_y]]
        
        # transform nextsim coordinates to lon/lat
        nb_x, nb_y = nbo.mesh_info.projection.pyproj(nb_x, nb_y, inverse=True)
            
        # transform to common coordinate system if needed
        if not self.is_lonlat_dim: 
            nc_x, nc_y = self.get_xy_dims_from_lonlat(nc_lon, nc_lat)
            nb_x, nb_y = self.projection(nb_x, nb_y)
        else:
            nc_x, nc_y = nc_lon[0], nc_lat[:,0]
        
        # fill nan gaps to avoid land contamination
        nc_v = fill_nan_gaps(nc_v, distance)
        # swap Y axis if needed
        y_step = int(np.sign(np.mean(np.diff(nc_y))))
        # make interpolator
        rgi = RegularGridInterpolator((nc_y[::y_step], nc_x), nc_v[::y_step])
        # interpolate only values within self bbox
        gpi = ((nb_x > nc_x.min()) * 
            (nb_x < nc_x.max()) *
            (nb_y > nc_y.min()) *
            (nb_y < nc_y.max()))
        v_pro = np.zeros(nb_x.shape) + fill_value
        v_pro[gpi] = rgi((nb_y[gpi], nb_x[gpi]))
        return v_pro
