# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
"""
Read region netCDF files with cell data.

"""

from os import path
import numpy as np
from netCDF4 import Dataset
from .. import interfaces
from typing import Union
import pyproj
from functools import partial
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import transform
import re

from ... import shyftdata_dir
from ...orchestration.configuration.config_interfaces import RegionConfig, ModelConfig, RegionConfigError
from ...orchestration.configuration.dict_configs import DictModelConfig, DictRegionConfig
from .utils import create_ncfile, make_proj


class CFRegionModelRepositoryError(Exception):
    pass


class CFRegionModelRepository(interfaces.RegionModelRepository):
    """
    Repository that delivers fully specified shyft api region_models
    based on data found in netcdf files.
    """

    def __init__(self, region, model):
        """
        Parameters
        ----------
        region: either a dictionary suitable to be instantiated as a
            RegionConfig Object or a sublcass of the interface RegionConfig
            containing regional information, like
            catchment overrides, and which netcdf file to read
        model: either a dictionary suitable to be instantiated as a
            ModelConfig Object or a subclass of interface ModelConfig
            Object containing model information, i.e.
            information concerning interpolation and model
            parameters
        """

        if not isinstance(region, RegionConfig):
            region_config = DictRegionConfig(region)
        if not isinstance(model, ModelConfig):
            model_config = DictModelConfig(model)
        else:
            region_config = region
            model_config = model

        if not isinstance(region_config, RegionConfig) or \
                not isinstance(model_config, ModelConfig):
            raise interfaces.InterfaceError()
        self._rconf = region_config
        self._mconf = model_config
        self._region_model = model_config.model_type()  # region_model
        self._mask = None
        self._epsg = self._rconf.domain()["EPSG"]  # epsg
        filename = self._rconf.repository()["params"]["data_file"]
        filename = path.expandvars(filename)
        if not path.isabs(filename):
            # Relative paths will be prepended the data_dir
            filename = path.join(shyftdata_dir, filename)
        if not path.isfile(filename):
            raise CFRegionModelRepositoryError("No such file '{}'".format(filename))
        self._data_file = filename
        self._catch_ids = self._rconf.catchments()
        self.bounding_box = None

    def _limit(self, x, y, data_cs, target_cs):
        """
        Parameters
        ----------
        """
        # Get coordinate system for arome data
        data_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", data_cs)  # TODO: remove this workaround when Proj allows for +e=0
        target_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", target_cs)
        data_proj = make_proj(data_cs_)
        target_proj = make_proj(target_cs_)

        # Find bounding box in arome projection
        bbox = self.bounding_box
        bb_proj = pyproj.transform(target_proj, data_proj, bbox[0], bbox[1])
        x_min, x_max = min(bb_proj[0]), max(bb_proj[0])
        y_min, y_max = min(bb_proj[1]), max(bb_proj[1])

        # Limit data
        xy_mask = ((x <= x_max) & (x >= x_min) & (y <= y_max) & (y >= y_min))

        xy_inds = np.nonzero(xy_mask)[0]

        # Transform from source coordinates to target coordinates
        xx, yy = pyproj.transform(data_proj, target_proj, x, y)

        return xx, yy, xy_mask, xy_inds

    def get_region_model(self, region_id, catchments=None):
        """
        Return a fully specified shyft api region_model for region_id, based on data found
        in netcdf dataset.

        Parameters
        -----------
        region_id: string
            unique identifier of region in data

        catchments: list of unique integers
            catchment indices when extracting a region consisting of a subset
            of the catchments has attribs to construct params and cells etc.

        Returns
        -------
        region_model: shyft.hydrology type
        """

        with Dataset(self._data_file) as dset:
            Vars = dset.variables
            c_ids = Vars["catchment_id"][:]
            xcoord = Vars['x'][:]
            ycoord = Vars['y'][:]
            m_catch = np.ones(len(c_ids), dtype=bool)
            if self._catch_ids is not None:
                m_catch = np.in1d(c_ids, self._catch_ids)
                xcoord_m = xcoord[m_catch]
                ycoord_m = ycoord[m_catch]

            dataset_epsg = None
            if 'crs' in Vars.keys():
                dataset_epsg = Vars['crs'].epsg_code.split(':')[1]
            if not dataset_epsg:
                raise interfaces.InterfaceError("netcdf: epsg attr not found in group elevation")

            target_cs = "+init=EPSG:{}".format(self._epsg)
            source_cs = "+init=EPSG:{}".format(dataset_epsg)

            # Construct bounding region
            box_fields = set(("lower_left_x", "lower_left_y", "step_x", "step_y", "nx", "ny", "EPSG"))
            if box_fields.issubset(self._rconf.domain()):
                tmp = self._rconf.domain()
                epsg = tmp["EPSG"]
                x_min = tmp["lower_left_x"]
                x_max = x_min + tmp["nx"]*tmp["step_x"]
                y_min = tmp["lower_left_y"]
                y_max = y_min + tmp["ny"]*tmp["step_y"]
                bounding_region = BoundingBoxRegion(np.array([x_min, x_max]),
                                                    np.array([y_min, y_max]), epsg, self._epsg)
            else:
                bounding_region = BoundingBoxRegion(xcoord_m, ycoord_m, dataset_epsg, self._epsg)
            self.bounding_box = bounding_region.bounding_box(self._epsg)
            x, y, m_xy, _ = self._limit(xcoord, ycoord, source_cs, target_cs)

            mask = ((m_xy) & (m_catch))

            areas = Vars['area'][mask]
            elevation = Vars["z"][mask]
            coordinates = np.dstack((x[mask], y[mask], elevation)).reshape(-1, 3)

            c_ids = Vars["catchment_id"][mask]
            c_ids_unique = list(np.unique(c_ids))
            # c_indx = np.array([c_ids_unique.index(cid) for cid in c_ids]) # since ID to Index conversion not necessary

            ff = Vars["forest-fraction"][mask]
            lf = Vars["lake-fraction"][mask]
            rf = Vars["reservoir-fraction"][mask]
            gf = Vars["glacier-fraction"][mask]

        # Construct region parameter:
        region_parameter = self._region_model.parameter_t()
        for p_type_name, value_ in self._mconf.model_parameters().items():
            if hasattr(region_parameter, p_type_name):
                sub_param = getattr(region_parameter, p_type_name)
                for p, v in value_.items():
                    if hasattr(sub_param, p):
                        setattr(sub_param, p, v)
                    else:
                        raise RegionConfigError("Invalid parameter '{}' for parameter set '{}'".format(p, p_type_name))
            else:
                raise RegionConfigError("Invalid parameter set '{}' for selected model '{}'".format(p_type_name, self._region_model.__name__))

        radiation_slope_factor = 0.9  # TODO: Move into yaml file similar to p_corr_scale_factor
        unknown_fraction = 1.0 - gf - lf - rf - ff

        # Construct cells
        cell_geo_data = np.column_stack([x[mask], y[mask], elevation, areas, c_ids.astype(int), np.full(len(c_ids),
                                                                                                        radiation_slope_factor), gf, lf, rf, ff, unknown_fraction])
        cell_vector = self._region_model.cell_t.vector_t.create_from_geo_cell_data_vector(np.ravel(cell_geo_data))
        for c in cell_vector:  # ensure we propagate the epsg_id to all cells
            c.geo.epsg_id = int(self._epsg)
        # Construct catchment overrides
        catchment_parameters = self._region_model.parameter_t.map_t()
        for cid, catch_param in self._rconf.parameter_overrides().items():
            if cid in c_ids_unique:
                param = self._region_model.parameter_t(region_parameter)
                for p_type_name, value_ in catch_param.items():
                    if hasattr(param, p_type_name):
                        sub_param = getattr(param, p_type_name)
                        for p, v in value_.items():
                            if hasattr(sub_param, p):
                                setattr(sub_param, p, v)
                            else:
                                raise RegionConfigError("Invalid parameter '{}' for catchment parameter set '{}'".format(p, p_type_name))
                    else:
                        raise RegionConfigError("Invalid catchment parameter set '{}' for selected model '{}'".format(p_type_name, self._region_model.__name__))

                catchment_parameters[cid] = param
        region_model = self._region_model(cell_vector, region_parameter, catchment_parameters)
        region_model.bounding_region = bounding_region
        region_model.catchment_id_map = c_ids_unique

        def do_clone(x):
            clone = x.__class__(x)
            clone.bounding_region = x.bounding_region
            clone.catchment_id_map = x.catchment_id_map
            # clone.gis_info = polygons  # cell shapes not included yet
            return clone

        region_model.clone = do_clone
        return region_model

    def cell_data_to_netcdf(self, region_model, output_dir):
        """
        Writes cell_data from a shyft region_model in the same format the
         'cf_region_model_repository' expects.

        Parameters
        -----------
        region_model: shyft.region_model

        model_id: str identifier of region_model

        Returns
        -------


        """

        nc_file = "{}_cell_data.nc".format(output_dir)
        # repository = {'class': self.__class__,
        #               'params': {'data_file': nc_file}
        #               }

        # with open('{}.yaml'.format(nc_file), 'w') as yml:
        #     yaml.dump(repository, yml)

        dimensions = {'cell': len(region_model.cells)}

        variables = {'y': [float, ('cell',), {'axis': 'Y',
                                                 'units': 'm',
                                                 'standard_name': 'projection_y_coordinate'}],

                     'x': [float, ('cell',), {'axis': 'X',
                                                 'units': 'm',
                                                 'standard_name': 'projection_x_coordinate'}],

                     'z': [float, ('cell',), {'axis': 'Z',
                                                 'units': 'm',
                                                 'standard_name': 'height',
                                                 'long_name': 'height above mean sea level'}],

                     'crs': [np.int32, ('cell',), {'grid_mapping_name': 'transverse_mercator',
                                                   'epsg_code': 'EPSG:' + str(region_model.bounding_region.epsg()),
                                                   'proj4': "+proj = utm + zone = 33 + ellps = WGS84 + datum = WGS84 + units = m + no_defs"}],

                     'area': [float, ('cell',), {'grid_mapping': 'crs',
                                                    'units': 'm^2',
                                                    'coordinates': 'y x z'}],

                     'forest-fraction': [float, ('cell',), {'grid_mapping': 'crs',
                                                               'units': '-',
                                                               'coordinates': 'y x z'}],

                     'glacier-fraction': [float, ('cell',), {'grid_mapping': 'crs',
                                                                'units': '-',
                                                                'coordinates': 'y x z'}],

                     'lake-fraction': [float, ('cell',), {'grid_mapping': 'crs',
                                                             'units': '-',
                                                             'coordinates': 'y x z'}],

                     'reservoir-fraction': [float, ('cell',), {'grid_mapping': 'crs',
                                                                  'units': '-',
                                                                  'coordinates': 'y x z'}],

                     'catchment_id': [np.int32, ('cell',), {'grid_mapping': 'crs',
                                                            'units': '-',
                                                            'coordinates': 'y x z'}],
                     }

        create_ncfile(nc_file, variables, dimensions)
        nci = Dataset(nc_file, 'a')

        extracted_geo_cell_data = region_model.extract_geo_cell_data()
        nci.variables['x'][:] = [gcd.mid_point().x for gcd in extracted_geo_cell_data]
        nci.variables['y'][:] = [gcd.mid_point().y for gcd in extracted_geo_cell_data]
        nci.variables['z'][:] = [gcd.mid_point().z for gcd in extracted_geo_cell_data]
        nci.variables['area'][:] = [gcd.area() for gcd in extracted_geo_cell_data]
        nci.variables['crs'][:] = [len(region_model.cells)*[region_model.bounding_region.epsg()]]
        nci.variables['catchment_id'][:] = [gcd.catchment_id() for gcd in extracted_geo_cell_data]
        nci.variables['lake-fraction'][:] = [gcd.land_type_fractions_info().lake() for gcd in extracted_geo_cell_data]
        nci.variables['reservoir-fraction'][:] = [gcd.land_type_fractions_info().reservoir() for gcd in extracted_geo_cell_data]
        nci.variables['glacier-fraction'][:] = [gcd.land_type_fractions_info().glacier() for gcd in extracted_geo_cell_data]
        nci.variables['forest-fraction'][:] = [gcd.land_type_fractions_info().forest() for gcd in extracted_geo_cell_data]

        nci.close()


class BoundingBoxRegion(interfaces.BoundingRegion):

    def __init__(self, x, y, point_epsg, target_epsg):
        self._epsg = str(point_epsg)
        x_min = x.ravel().min()
        x_max = x.ravel().max()
        y_min = y.ravel().min()
        y_max = y.ravel().max()
        self.x = np.array([x_min, x_max, x_max, x_min], dtype="d")
        self.y = np.array([y_min, y_min, y_max, y_max], dtype="d")
        self.x, self.y = self.bounding_box(target_epsg)
        self._epsg = str(target_epsg)
        self._polygon = box(x_min, y_min, x_max, y_max)

    def bounding_box(self, epsg):
        epsg = str(epsg)
        if epsg == self.epsg():
            return np.array(self.x), np.array(self.y)
        else:
            source_cs = "+init=EPSG:{}".format(self.epsg())
            target_cs = "+init=EPSG:{}".format(epsg)
            source_cs = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", source_cs)  # TODO: remove this workaround when Proj allows for +e=0
            target_cs = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", target_cs)
            source_proj = make_proj(source_cs)
            target_proj = make_proj(target_cs)
            return [np.array(a) for a in pyproj.transform(source_proj, target_proj, self.x, self.y)]

    def bounding_polygon(self, epsg: int) -> Union[Polygon, MultiPolygon]:
        """Implementation of interface.BoundingRegion"""
        if epsg == self.epsg():
            return self._polygon
        else:
            source_cs = "+init=EPSG:{}".format(self.epsg())
            target_cs = "+init=EPSG:{}".format(epsg)
            source_cs = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", source_cs)  # TODO: remove this workaround when Proj allows for +e=0
            target_cs = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", target_cs)
            source_proj = make_proj(source_cs)
            target_proj = make_proj(target_cs)
            project = partial(pyproj.transform, source_proj, target_proj)
            return transform(project, self._polygon)

    def epsg(self):
        return self._epsg
