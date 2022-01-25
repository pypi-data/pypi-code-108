"""
The fastfuels module loads a .fio directory-in-file resource on which a user can
perform spatial queries, view fuels data in 3D and export to QuicFire.
"""

import builtins
import json
import os

# external imports
import colorcet  # pip3 install colorcet
import numpy as np  # pip3 install numpy
from scipy.io import FortranFile  # pip3 install scipy
import zarr  # pip3 install zarr
import s3fs  # pip3 install s3fs
from shapely.strtree import STRtree  # pip3 install shapely
from shapely.geometry import Point, Polygon  # pip3 install shapely

try:
    from urllib.parse import urlparse
except ImportError:
    from urllib2.parse import urlparse

# --------------
# USERSPACE DEFS
# --------------


def open(fname, ftype='local', username=None, password=None):
    """
    Helper function for opening a .fio file. Additional user actions on
    fuels data can be accessed through the class instance returned by this
    function.

    Args:
        fname (str): path and filename of the .fio resource
        ftype (str): file type, either 'local' or 's3'
        username (str): user name to access file
        password (str): password to access file

    Returns:
        An instance of FuelsIO
    """

    return FuelsIO(fname, ftype, username=username, password=password)

# --------------
# HELPER CLASSES
# --------------


class AlbersEqualAreaConic:
    """
    Implements forward and inverse projection on Albers Equal Area Conic

    Attributes:
        lambda_0 (float): origin of longitude
        a (float): semi-major axis of earth (GRS80)
        e2 (float): eccentricity squared
        e (float): eccentricity
        n (float): stored map constant
        C (float): stored map constant
        rho_0 (float): stored map constant
    """

    def __init__(self, phi_1=29.5, phi_2=45.5, phi_0=23.0, lambda_0=-96.0):
        """
        Creates an instance of AlbersEqualAreaConic, initializes attributes and
        computes map constants

        Note:
            Geographic constants are based on the GRS 1980 ellipsoid

        Args:
            phi_1 (float): first standard parallel
            phi_2 (float): second standard parallel
            phi_0 (float): origin of latitude
            lambda_0 (float): origin of longitude
        """

        # convert map params to radians
        phi_0 = np.radians(phi_0)
        phi_1 = np.radians(phi_1)
        phi_2 = np.radians(phi_2)
        self.lambda_0 = np.radians(lambda_0)

        # GRS 1980 REFERENCE ELLIPSIOD CONSTANTS
        # geographic constants
        self.a = 6378137.0
        # derived geometrical constants
        f = 1.0/298.2572221010042  # flattening
        self.e2 = 2*f - f**2  # eccentricity squared
        self.e = np.sqrt(self.e2)  # eccentricity

        # preliminaries
        m_1 = self._m(phi_1)
        m_2 = self._m(phi_2)
        q_0 = self._q(phi_0)
        q_1 = self._q(phi_1)
        q_2 = self._q(phi_2)

        # map constants
        self.n = (m_1**2 - m_2**2)/(q_2 - q_1)
        self.C = m_1**2 + self.n*q_1
        self.rho_0 = self.a*(self.C - self.n*q_0)**0.5/self.n

    def _m(self, phi):
        """Private member
        Convenience method for computing map constants
        """

        return np.cos(phi)/np.sqrt(1 - self.e2*(np.sin(phi))**2)

    def _q(self, phi):
        """Private member
        Another convenience method for computing map constants
        """

        return (1 - self.e2)*(np.sin(phi)/(1 - self.e2*(
            np.sin(phi))**2) - (1.0/(2*self.e))*np.log((1-self.e*np.sin(
                phi))/(1 + self.e*np.sin(phi))))

    def forward(self, lat, lon):
        """
        Performs forward projection from geodetic coordinates to projected
        coordinates

        Args:
            lat (float): latitude
            lon (float): longitude

        Returns:
            (x,y) coordinate projected in Albers Equal Area Conic
        """

        # convert to radians for numpy trig functions
        lat = np.radians(lat)
        lon = np.radians(lon)

        # preliminaries
        q = self._q(lat)
        rho = self.a*(self.C - self.n*q)**0.5/self.n
        theta = self.n*(lon - self.lambda_0)

        # retrieve the projected coordinates
        x = rho*np.sin(theta)
        y = self.rho_0 - rho*np.cos(theta)

        return x, y

    def inverse(self, x, y):
        """
        Performs inverse projection from Albers to geodetic coordinates

        Args:
            x (float): x projected in Albers
            y (float): y projected in Albers

        Returns:
            lat and lon in geodetic coordinates
        """

        # preliminaries
        p = np.sqrt(x*x + (self.rho_0 - y)**2)
        theta = np.arctan2(x, self.rho_0 - y)
        q = (self.C - ((p*p)*(self.n**2))/(self.a**2))/self.n

        # convergence criteria
        epsilon = 1e-6

        # iterate latitude calculation until convergence
        phi = np.sin(q/2)
        next_phi = self._inverse_iteration(phi, q)
        while (np.abs(np.degrees(phi) - np.degrees(next_phi)) > epsilon):
            phi = next_phi
            next_phi = self._inverse_iteration(phi, q)

        return np.degrees(phi), np.degrees(self.lambda_0 + theta/self.n)

    def _inverse_iteration(self, phi, q):
        """Private member
        Formula to iterator until convergence for inverse projection of latitude
        """

        return np.radians(np.degrees(phi) + np.degrees((1 -
                                                        self.e2*(np.sin(phi)**2)**2)/(2*np.cos(phi))*(
            (q/(1-self.e2)) - (np.sin(phi)/(1-self.e2*(np.sin(phi)**2))) +
            (1/(2*self.e))*np.log((1 - self.e*np.sin(phi))/(1 +
                                                            self.e*np.sin(phi))))))


class Viewer:
    """
    This class wraps pyvista which wraps VTK. Provides simple convenience
    functions for plotting UniformGrids in 3D.

    Attributes:
        data (dict): dictionary of 3D fuel parameter arrays
        plotter: Pyvista plotter instance

    """

    def __init__(self, data):
        """
        Configures the Pyvista plotter instance

        Args:
            data (dict): dictionary of 3D fuel parameter arrays
        """

        # set pv theme
        import pyvista as pv  # pip3 install pyvista
        pv.set_plot_theme('document')
        self.data = data
        self.plotter = pv.Plotter(title='FastFuels')

    def add(self, property, topography=False):
        """
        Adds a 3D array to the plotter instance

        Args:
            property (str): fuel parameter to show, parameter string must be in
                the key list of the data dictionary
            topography (bool): use elevation data to show topography

        Note:
            Use the `get_properties()` method to get available fuel properties.
        """

        # extract the property array from the data dictionary
        fp = self.data[property]

        if topography:

            if 'elevation' not in self.data:
                raise Exception(
                    'Must query elevation in order to show topography.')

            #print('data shape', fp.shape)
            elev_min = np.min(self.data['elevation'])
            elev_max = np.max(self.data['elevation'])
            elev_diff = elev_max - elev_min
            #print('elev',  elev_max, '-', elev_min, '=', elev_diff)

            # expand
            z = np.zeros((fp.shape[0], fp.shape[1], elev_diff), dtype=fp.dtype)
            fp = np.concatenate((fp, z), axis=2)
            #print('new data shape', fp.shape)

            # roll
            for i in range(fp.shape[0]):
                for j in range(fp.shape[1]):
                    # np.roll is way to slow so use slicing instead
                    diff = self.data['elevation'][i][j] - elev_min + 1
                    fp[i][j][diff:] = fp[i][j][:-diff]
                    fp[i][j][:diff] = 0

        # move zeros to -1 for thresholding
        fp[fp == 0] = -1

        # convert the 3D array to a Pyvista UniformGrid
        import pyvista as pv  # pip3 install pyvista
        grid = pv.UniformGrid()
        grid.dimensions = np.array(fp.shape) + 1
        grid.spacing = [1, 1, 1]
        grid.cell_arrays['values'] = fp.flatten(order='F')
        grid = grid.threshold(0)

        # conditionally select the colormap based on property
        if property == 'species_group':
            cm = colorcet.glasbey[:10]
        else:
            cm = 'rainbow'

        # add the array to the plotter instance
        self.plotter.add_mesh(grid, cmap=cm)

    def show(self):
        """
        This will halt the program and display an interactive window populated
        will a 3D array
        """

        self.plotter.show()


class FuelsIO:
    """
    This class handles the .fio resource, extracts metadata and performs spatial
    queries.

    Attributes:
        fio_file: Zarr file manager object
        albers (AlbersEqualAreaConic object): Instance of the
            `AlbersEqualAreaConic` class
        cache_limit (float): Memory cache limit in bytes for spatial queries
        fmwriter (FuelModleWriter object): Instance of the `FuelModleWriter`
            class
    """

    def __init__(self, fname, ftype='local', username=None, password=None):
        """
        Opens a connection to the fio resource, extracts metadata and
        initializes helper classes

        Args:
            fname (str): path and filename of the fio resource.
            ftype (str): file type, either 'local' or 's3'
            username (str): user name to access file
            password (str): password to access file
        """

        # No longer using the remote demo fio file hosted on GCP, moved data
        # over to UCSD server

        # open connection to fio resource
        # if fname == 'remote':
        #    print('connecting to remote FIO server...')
        #    gcs = gcsfs.GCSFileSystem()
        #    self.fio_file = zarr.open(gcs.get_mapper('gs://ca-11-2020/demo.fio'), 'r')
        # else:

        self._ftype = ftype

        #print(f'FuelsIO({fname}, {ftype}, {username}, {password}')

        if ftype == 'local':

            self.fio_file = None

            if not os.path.exists(fname):
                raise Exception(f'File does not exist: {fname}')

            # FIXME workaround for bug #769
            # https://github.com/zarr-developers/zarr-python/issues/769
            if os.path.exists(f'{fname}/surface/dem/.zarray'):
                with builtins.open(f'{fname}/surface/dem/.zarray') as f:
                    j = json.load(f)
                    if 'dimension_separator' in j:
                        if j['dimension_separator'] == '/':
                            store = zarr.NestedDirectoryStore(fname)
                            self.fio_file = zarr.group(
                                store=store, overwrite=False)
                        else:
                            raise Exception(
                                f'Unknown dimension_separator: {j["dimension_separator"]}')

            if not self.fio_file:
                self.fio_file = zarr.open(fname, 'r')

            self._fio_path = fname

        elif ftype == 's3':

            # use urlparse to separate the hostname and port from path
            url = urlparse(fname)
            endpoint = url.scheme + "://" + url.hostname
            if url.port:
                endpoint += ":" + str(url.port)

            if username and password:
                fs = s3fs.S3FileSystem(client_kwargs={
                    "endpoint_url": endpoint,
                    "verify": False,
                },
                    username=username,
                    password=password
                )
            else:
                fs = s3fs.S3FileSystem(client_kwargs={
                    "endpoint_url": endpoint,
                    "verify": False,
                },
                    anon=True
                )

            # FIXME workaround for bug #769
            # https://github.com/zarr-developers/zarr-python/issues/769
            sep = '.'
            zarray = f'{url.path}/surface/dem/.zarray'
            if fs.exists(zarray):
                with fs.open(zarray, 'r') as f:
                    j = json.load(f)
                    if 'dimension_separator' in j:
                        sep = j['dimension_separator']

            fs = None

            storage_options = {
                'client_kwargs': {
                    "endpoint_url": endpoint,
                    "verify": False
                },
                'dimension_separator': sep
            }

            if username and password:
                storage_options['username'] = username
                storage_options['password'] = password
            else:
                storage_options['anon'] = True

            self.fio_file = zarr.open_group(
                's3://' + url.path, mode='r', storage_options=storage_options)

            self._fio_path = url.path
            self._fio_endpoint = endpoint
            self._fio_username = username
            self._fio_password = password

        else:
            raise Exception('Unknown type: ' + ftype)

        # get metadata and datasets
        self.extract_meta_data()

        if not self._is_index:
            self.parse_contents()

        # instantiate helper classes
        self.albers = AlbersEqualAreaConic()

        # default cache limit
        self.cache_limit = 1e9

    def _parse_extent(self, extent, extent_fmt):
        """
        Parse the extent format to read the extent. Private method.

        Returns:
            (x1,y1,x2,y2): the extent bounding box values
        """
        if extent_fmt == '(x1, y1), (x2, y2)' and len(extent) == 4:
            return extent
        elif extent_fmt == '[[x1, y1], [x2, y2]]':
            return extent[0][0], extent[0][1], extent[1][0], extent[1][1]
        else:
            raise Exception(f'Unknown extent format: {extent_fmt}')

    def extract_meta_data(self):
        """
        Gets metadata from fio resource attributes
        """

        # new fio version changed extent format key from "extent_format" to
        # "extent_fmt"
        self.extent_fmt = self.fio_file.attrs['extent_fmt']

        self.extent_x1, self.extent_y1, self.extent_x2, self.extent_y2 = self._parse_extent(self.fio_file.attrs['extent'],
                                                                                            self.fio_file.attrs['extent_fmt'])

        self.n_cols = self.extent_x2 - self.extent_x1
        self.n_rows = self.extent_y1 - self.extent_y2

        self.proj = self.fio_file.attrs['proj']
        self.res = self.fio_file.attrs['resolution']
        self.units = self.fio_file.attrs['units']

        # old attributes (these are removed in new version of fio files)
        #self.dim = self.fio_file.attrs['dimensions']
        #self.dim_fmt = self.fio_file.attrs['dim_format']

        if 'index' in self.fio_file:
            #print(f'Is index with {self.fio_file["index"]["name"].shape[0]} parts.')
            self._is_index = True

            extents = []

            # copy all the index data since must faster than accessing
            # one at a time via s3 api.

            fio_extents = self.fio_file['index']['extent'][:]
            fio_extent_fmts = self.fio_file['index']['extent_fmt'][:]
            fio_names = self.fio_file['index']['name'][:]

            if len(fio_names) == 0:
                print('WARNING: empty index.')

            for i in range(len(fio_names)):

                #print(f'{i} {self.fio_file["index"]["name"][i]}')

                #ext = fio_extents[i]
                #width = ext[1][0] - ext[0][0]
                #height = ext[1][1] - ext[0][1]
                #print(fio_names[i], ext, width, height)

                x1, y1, x2, y2 = self._parse_extent(
                    fio_extents[i], fio_extent_fmts[i])

                if y1 > y2:
                    tmp = y1
                    y1 = y2
                    y2 = tmp

                ring = Polygon([Point(x1, y1),
                                Point(x2, y1),
                                Point(x2, y2),
                                Point(x1, y2)])
                ring.name = fio_names[i]
                extents.append(ring)

            self._index_stree = STRtree(extents)

        else:
            self._is_index = False

    def parse_contents(self):
        """
        Get references to fuel array datasets

        Note:
            This method will not load the arrays to memory
        """

        # extract surface fuel properties and elevation
        surface_group = self.fio_file['surface']
        # change key from "loading" to "load" in new fio
        self.surface_loading = surface_group['load']
        # change from "fuel_depth" to "depth" in new fio
        self.surface_fuel_depth = surface_group['depth']
        self.surface_sav = surface_group['sav']
        # change key from "elevation" to "dem" in new fio
        self.elevation = surface_group['dem']

        # removed emc parameter in new version of fio
        #self.surface_emc = surface_group['emc']

        # extract canopy fuel properties
        canopy_group = self.fio_file['canopy']
        # changed key from "bulk_density" to "bd" in new fio
        self.canopy_bulk_density = canopy_group['bd']
        self.canopy_sav = canopy_group['sav']

        # removed species_group parameter in new fio
        #self.canopy_sp_group = canopy_group['species_group']

    def get_extent(self, mode='projected'):
        """
        Get the geographic extent in projected or geographic coordinates

        Args:
            mode (str, default='projected'): mode of extent coordinate system;
                projected or geographic
        """

        if mode == 'projected':
            return self.extent_x1, self.extent_y1, self.extent_x2, self.extent_y2
        elif mode == 'geographic':
            lat1, lon1 = self.albers.inverse(self.extent_x1, self.extent_y1)
            lat2, lon2 = self.albers.inverse(self.extent_x2, self.extent_y2)
            return lon1, lat1, lon2, lat2

    def query(self, lon, lat, radius=None, xlen=None, ylen=None, property=None):
        """
        Performs a geographic spatial query on the fio resource. Extent of the
        query is defined by the point (lat, lon) and either a square bounding an 
        inscribed circle defined by the radius parameter, or a rectangle of width
        xlen and height ylen. Either radius, or xlen and ylen must be specified,
        but not both.

        Args:
            lon (float): longitude
            lat (float): latitude
            radius (int, default=None): radius of extent circle in meters
            xlen (int, default=None): x-length of extent in meters
            ylen (int, default=None): y-length of extent in meters
            property (list, default=None): properties to query, defaults to every property
        """

        return self.query_geographic(lon, lat, radius=radius, xlen=xlen, ylen=ylen, property=property)

        # changing the way we query fuels in version 0.3.1
        """
        if mode == 'relative':
            return self.query_relative(a, b)
        elif mode == 'projected':
            return self.query_projected(a, b)
        elif mode == 'geographic':
            return self.query_geographic(a, b)
        """

    def check_bounds(self, x1, y1, x2, y2):
        """
        Returns true if in bounds and false if out of bounds
        """

        if x1 < 0:
            return 0
        elif y1 < 0:
            return 0
        elif x2 > self.n_cols:
            return 0
        elif y2 > self.n_rows:
            return 0
        else:
            return 1

    def check_cache(self, x1, y1, x2, y2):
        """
        Returns true if query size is less than cache limit and false if
        query size of greater than cache limit
        """

        if 1700*((x2 - x1)*(y2 - y1)) > self.cache_limit:
            return 0
        return 1

    def query_relative(self, a, b, property=None, extent=None):

        x1, y1 = a
        x2, y2 = b

        if self.check_bounds(x1, y1, x2, y2):
            if self.check_cache(x1, y1, x2, y2):
                return self.slice_and_merge(y1, y2, x1, x2, property, extent)
            else:
                print('ERROR: area too large')
        else:
            print('ERROR: bounding box query out of bounds')
            return -1

    def query_projected(self, a, b, property=None):

        x1, y1 = a
        x2, y2 = b

        if self._is_index:

            polygon = Polygon([Point(x1, y1),
                               Point(x2, y1),
                               Point(x2, y2),
                               Point(x1, y2)])

            matches = self._index_stree.query(polygon)
            num_matches = len(matches)

            if num_matches == 0:
                print('ERROR: bounding box query not found in index.')
                return -1
            elif num_matches == 1:
                name = matches[0].name
                print(f'Bounding box query found in single source: {name}')
                return self._indexed_query_projected(name, a, b, property)
            else:
                print(
                    f'WARNING: bounding box query found in multiple ({num_matches}) sources; choosing a single one.')

                # TODO merge together the sources in the requested extent

                # for now, choose the source with the largest intersection
                max_area = -1
                max_name = None
                for i in matches:
                    intersection = polygon.intersection(i)

                    # note that area = 0 is possible when the intersection is a line
                    # and not a polygon
                    area = intersection.area
                    #print(i.name, area, intersection)

                    if area > max_area:
                        max_area = area
                        max_name = i.name

                #print('max is', max_name, max_area)
                print(f'choosing {max_name}')
                return self._indexed_query_projected(max_name, a, b, property)

        query_extent = int(x1), int(y1), int(x2), int(y2)

        x1_rel = int(x1 - self.extent_x1)
        y1_rel = int(self.extent_y1 - y1)
        x2_rel = int(x2 - self.extent_x1)
        y2_rel = int(self.extent_y1 - y2)

        return self.query_relative((x1_rel, y1_rel), (x2_rel, y2_rel), 
                                   property=property, extent=query_extent)

    def _indexed_query_projected(self, name, a, b, property):

        if name[0] != '/':
            full_path = '{}/{}'.format(os.path.dirname(
                self._fio_path.rstrip('/')), name)
        elif self._ftype == 'local':
            full_path = name
        elif self._ftype == 's3':
            raise Exception('Cannot use absolute paths with S3.')

        if self._ftype == 'local':
            #print(f'opening {full_path}')
            fuels = FuelsIO(full_path)

        elif self._ftype == 's3':
            url = f'{self._fio_endpoint}{full_path}'
            # print(url)
            fuels = FuelsIO(
                url, self._ftype, username=self._fio_username, password=self._fio_password)

        else:
            raise Exception(f'Unknown type: {self._ftype}')

        # set cache limit
        fuels.cache_limit = self.cache_limit

        return fuels.query_projected(a, b, property)


    def query_geographic(self, lon, lat, radius=None, xlen=None, ylen=None, property=None):

        x1, y1 = self.albers.forward(lat, lon)

        if radius and (xlen or ylen):
            raise Exception('Either radius, or xlen and ylen can be specified, but not both.')
        
        if not (radius or xlen or ylen):
            raise Exception('Either radius, or xlen and ylen need to be specified, but not both.')

        if radius:
            if radius < 1:
                raise Exception('Radius must be greater than 0.')
           
            xlen = radius * 2
            ylen = radius * 2
       
        else:
            if xlen < 2 or ylen < 2 \
                or xlen % 2 != 0 or ylen % 2 != 0:
                raise Exception('xlen and ylen must be greater than 1 and divisible by 2.')
            
        x1 -= xlen/2
        y1 += ylen/2

        x2 = x1 + xlen
        y2 = y1 - ylen
        
        return self.query_projected((x1, y1), (x2, y2), property)

    def slice_and_merge(self, y1, y2, x1, x2, prop, extent):
        """
        Queries the fuel array datasets and loads to memory

        Returns:
            An instance of the FuelsROI class
        """

        data_dict = {}

        if not prop or 'bulk_density' in prop:
            canopy_bulk_density = self.canopy_bulk_density[y1:y2, x1:x2, :].astype(
                np.float32)
            canopy_bulk_density = (canopy_bulk_density/255)*2.0

            canopy_moisture = np.zeros_like(canopy_bulk_density)
            canopy_moisture[canopy_bulk_density !=
                            0] = 1.0  # hardcoded for now

            surface_loading = self.surface_loading[y1:y2, x1:x2].astype(
                np.float32)
            surface_loading = (surface_loading/255)*3.0

            canopy_bulk_density[:, :, 0] = surface_loading
            data_dict['bulk_density'] = canopy_bulk_density

        if not prop or 'sav' in prop:
            canopy_sav = self.canopy_sav[y1:y2, x1:x2, :].astype(np.float32)
            canopy_sav = (canopy_sav/255)*8000.0

            surface_sav = self.surface_sav[y1:y2, x1:x2].astype(np.float32)
            surface_sav = (surface_sav/255)*8000.0

            canopy_sav[:, :, 0] = surface_sav
            data_dict['sav'] = canopy_sav

        if not prop or 'moisture' in prop:
            # surface_emc removed in new fio
            #surface_moisture = self.surface_emc[y1:y2, x1:x2]
            canopy_moisture[:, :, 0] = 0.2  # hardcoded for new
            data_dict['moisture'] = canopy_moisture

        if not prop or 'fuel_depth' in prop:
            fuel_depth = np.zeros_like(canopy_sav)
            fuel_depth[:, :, 0] = self.surface_fuel_depth[y1:y2,
                                                          x1:x2].astype(np.float32)
            fuel_depth = (fuel_depth/255)*2.0
            data_dict['fuel_depth'] = fuel_depth

        # removed species group parameter in new fio
        #data_dict['species_group'] = self.canopy_sp_group[y1:y2, x1:x2, :]

        if not prop or 'elevation' in prop:
            data_dict['elevation'] = self.elevation[y1:y2, x1:x2]

        return FuelsROI(data_dict, extent=extent, attrs=self.fio_file.attrs)


class FuelsROI:
    """
    Handles viewing and writing of 3D fuel arrays following a FuelsIO
    spatial query.

    Attributes:
        data_dict (dictionary): Keys are fuel properties and values are 3D
            arrays
        extent (list): Extent of ROI
        attrs (dictionary): Metadata of fuel zarr file.
    """

    def __init__(self, data_dict, extent=None, attrs=None):
        """
        initializes attributes and instantiates Viewer and FirelModelWriter
        objects.
        """

        self.data_dict = data_dict
        self.extent = extent
        self.writer = FireModelWriter(extent=extent, attrs=attrs)

    def get_properties(self):
        """
        Get the available fuel properties

        Returns:
            list of fuel properties
        """

        return list(self.data_dict.keys())

    def view(self, property, topography=False):
        """
        Display 3D array of given fuel property

        Args:
            property (str): fuel property
            topography (bool): use elevation data to show topography
        """

        viewer = Viewer(self.data_dict)
        viewer.add(property, topography)
        viewer.show()

    def write(self, path, model='quicfire', res_xyz=[1,1,1], property=None, **kwargs):
        """
        Writes fuel arrays to a fire model. Currently only implements QUICFire

        Args:
            path (str): path to write outputs
            model (str): the type of model outputs
            res_xyz (list): resolution of outputs
            property (str): data property to write
        """

        if model == 'quicfire':
            print('writing QUICFire input files...')

            # FIXME check property before writing each one

            self.writer.write_to_quicfire(self.data_dict['bulk_density'],
                                          path + '/' + 'bulk_density.dat', res_xyz)
            # NOTE: sav not used by quic-fire
            #self.writer.write_to_quicfire(self.data_dict['sav'],
                                          #path + '/' + 'sav.dat', res_xyz)
            self.writer.write_to_quicfire(self.data_dict['moisture'],
                                          path + '/' + 'moisture.dat', res_xyz)
            self.writer.write_to_quicfire(self.data_dict['fuel_depth'],
                                          path + '/' + 'depth.dat', res_xyz)
            self.writer.write_to_quicfire(self.data_dict['elevation'],
                                          path + '/' + 'topo.dat', res_xyz)
            print('complete')
        elif model == 'vtk':
            if not property:
                raise Exception('Must specify fuel property for VTK output.')
            elif property not in self.data_dict:
                raise Exception('Invalid fuel property {}'.format(property))
            self.writer.write_to_vtk(self.data_dict, property, path)
        elif model == 'wfds':
            print('wfds writer not implemented')
        elif model == 'zarr':
            if path:
                self.writer.write_to_zarr(self.data_dict, path + '/fastfuels.zarr', res_xyz, **kwargs)
            else:
                self.writer.write_to_zarr(self.data_dict, None, res_xyz, **kwargs)
        else:
            raise Exception('Unsupported model', model)


class FireModelWriter:
    """
    Writes fuel arrays to disk as fire model input files
    """

    def __init__(self, extent=None, attrs=None):
        self.extent = extent
        self.attrs = attrs

    def _change_resolution(self, data, res_xyz):

        if res_xyz == [1, 1, 1]:
            pass
        elif res_xyz == [2, 2, 1]:

            if len(data.shape) == 3:
                h, w, d = data.shape
                # average pool subsampling
                data = data.reshape((h//2, 2, w//2, 2, d)).mean(3).mean(1)
            elif len(data.shape) == 2:
                h, w = data.shape
                data = data.reshape((h//2, 2, w//2, 2)).mean(3).mean(1)

        elif res_xyz != [1,1,1]:

            print(f'Resolution can be either [1,1,1] or [2,2,1], not {res_xyz}. ' +
                  'Defaulting to [1,1,1] resolution')

        rx, ry, rz = res_xyz
        print(f'Output resolution is x: {rx}, y: {ry}, z: {rz}\n')

        return data.astype(np.float32)

    def write_to_quicfire(self, data, fname, res_xyz):
        """
        Write fuel array as QF input file
        """

        print(f'Writing data to {fname}...')

        data = self._change_resolution(data, res_xyz)
   
        # if 3d, convert from yxz to zyx since this is xyz in fortran
        # if 2d, don't need to convert since yx is xy in fortran
        if len(data.shape) == 3:
            data = np.moveaxis(data, [0,1,2], [1,2,0])

        f = FortranFile(fname, 'w', 'uint32')
        # NOTE: do NOT transpose the axes
        f.write_record(data)
        f.close()

    def write_to_vtk(self, data, property, fname):
        """
        Write to VTK input file.
        """

        # FIXME this mostly duplicates Viewer.add()

        fp = data[property]

        if 'elevation' in data:

            #print('data shape', fp.shape)
            elev_min = np.min(data['elevation'])
            elev_max = np.max(data['elevation'])
            elev_diff = elev_max - elev_min
            #print('elev',  elev_max, '-', elev_min, '=', elev_diff)

            # expand
            z = np.zeros((fp.shape[0], fp.shape[1], elev_diff), dtype=fp.dtype)
            fp = np.concatenate((fp, z), axis=2)
            #print('new data shape', fp.shape)

            # roll
            for i in range(fp.shape[0]):
                for j in range(fp.shape[1]):
                    # np.roll is way to slow so use slicing instead
                    diff = data['elevation'][i][j] - elev_min + 1
                    fp[i][j][diff:] = fp[i][j][:-diff]
                    fp[i][j][:diff] = 0

        # move zeros to -1 for thresholding
        fp[fp == 0] = -1

        # convert the 3D array to a Pyvista UniformGrid
        import pyvista as pv  # pip3 install pyvista
        grid = pv.UniformGrid()
        grid.dimensions = np.array(fp.shape) + 1
        grid.spacing = [1, 1, 1]
        grid.cell_arrays['values'] = fp.flatten(order='F')
        grid = grid.threshold(0)

        grid.extract_geometry().save(fname, binary=True)

    def write_to_wfds(self, data, fname):
        """
        TODO: write to FDS input file
        """
        pass

    def write_to_zarr(self, data, fname, res_xyz, **kwargs):

        if 'zarr' in kwargs:
            print(f'Writing data to user-supplied zarr...')
        else:
            print(f'Writing data to {fname}...')
       
        if 'zarr' in kwargs:
            z = kwargs['zarr']
        else:
            z = zarr.open(fname, mode='w')


        for n in ['proj', 'units']:
            if n in self.attrs:
                z.attrs[n] = self.attrs[n]

        if 'version' in self.attrs:
            z.attrs['fastfuels-data-version'] = self.attrs['version']
        else:
            z.attrs['fastfuels-data-version'] = 1.0

        z.attrs['dimension'] = ['z', 'y', 'x']

        # write resolution in zyx order
        z.attrs['resolution'] = [res_xyz[2], res_xyz[1], res_xyz[0]]

        z.attrs['extent'] = self.extent
        z.attrs['extent_fmt'] ='[[x1, y1], [x2, y2]]'

        canopy = z.create_group('canopy')
        canopy_chunks = (128, 1000, 1000)
        for n in ['bulk_density', 'moisture', 'fuel_depth', 'sav']:

            # first change the resolution so we get the shape for create_dataset()
            arr_res = self._change_resolution(data[n][:,:,:], res_xyz)

            # convert from yxz to zyx
            arr_res = np.moveaxis(arr_res, [0,1,2], [1,2,0])

            arr = canopy.create_dataset(n, shape=arr_res.shape,
                                        chunks=canopy_chunks, dtype='f4')
            
            arr[:,:,:] = arr_res

        
        surface = z.create_group('surface')
        arr_res = self._change_resolution(data['elevation'][:,:], res_xyz)
        arr = surface.create_dataset('elevation', shape=arr_res.shape,
                                     chunks=(3000,3000), dtype='f4')
        arr[:,:] = arr_res

        # cleanup
        del arr_res
        arr = None
