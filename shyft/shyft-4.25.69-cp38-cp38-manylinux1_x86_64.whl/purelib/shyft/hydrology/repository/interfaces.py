# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from abc import ABCMeta, abstractmethod
from copy import deepcopy
#from shyft import api
from ...time_series import (time,UtcPeriod)

from typing import List, Any, Dict, Optional

"""Module description: This module contain the abstract base-classes for the
repositories in shyft, defining the contracts that a repository should
implement.

Brief intro to Repository pattern here:
    http://martinfowler.com/eaaCatalog/repository.html
    http://www.codeproject.com/Articles/526874/Repositorypluspattern-cplusdoneplusright
    https://msdn.microsoft.com/en-us/library/ff649690.aspx
    http://www.remondo.net/repository-pattern-example-csharp/

According to architecture diagram/current code we do have
repositories for

* region-model - for reading/providing the region-model, consisting of
                 cell/catchment information, (typicall GIS system) for a given
                 region/model spec.


* state         - for reading region model-state, cell-level (snapshot of
                  internal state variables of the models).

* geo-located time-series
                - for input observations,forecasts, run-off time-series, that is
                 useful/related to the region model. E.g. precipitation,
                 temperature, radiation, wind-speed, relative humidity and even
                 measured run-off, and other time-series that can be utilized
                 by the region-model. Notice that this repository can serve
                 most type of region-models.

* configuration - helps *orchestration* to assemble data (region, model,
                  sources etc) and repository impl.

We try to design the interfaces, input types, return types, so that the number
of lines needed in the orchestration part of the code is kept to a minimum.

This implies that the input arguments to the repositories are types that goes
easily with the shyft.hydrology. The returned types should also be shyft.hydrology
compatible types, - thus the orchestrator can just pass on values returned into
the shyft.hydrology.
"""


class RegionModelRepository:
    """
    Interface for RegionModel objects.

    The responsibility is to provide shyft.hydrology RegionModel objects to the
    orchestrator, hiding away any implementation specific details regarding how
    the model is stored (e.g. just a mock-model, a netcdf-file based model, a
    GIS-system based model etc.).
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_region_model(self, region_id, catchments=None):
        """
        Return a fully specified shyft api region_model for region_id.

        Parameters
        -----------
        region_id: string
            unique identifier of region in data, helps
            repository to identify which model, *including model type*
            and other stuff needed in order to return a fully
            operational model.
        catchments: list of unique integers
            catchment indices when extracting a region consisting of a subset
            of the catchments

        Returns
        -------
        region_model: shyft.hydrology type

        ```
        # Pseudo code below
        # Concrete implementation must construct cells, region_parameter
        # and catchment_parameters and return a region_model

        # Use data to create cells
        cells = [region_model.cell_type(*args, **kwargs) for cell in region]

         # Use data to create regional parameters
        region_parameter = region_model.parameter_type(*args, **kwargs)

        # Use data to override catchment parameters
        catchment_parameters = {}
        for all catchments in region:
            catchment_parameters[c] = region_model.parameter_type(*args,
                                                                  **kwargs)
        return region_model(cells, region_parameter, catchment_parameters)
        ```
        """
        raise NotImplementedError(
            "Method 'get_region_model' not implemented for repository {}.".format(self.__class__.__name__))


class StateInfo:
    """
    Keeps needed information for a persisted region model state.  Currently,
    the StateInfo of a region model is unique to the model, but we plan to do
    some magic so that you can extract part of state in order to transfer/apply
    to other state.

    This simple structure is utilized by the StateRepository to provide
    information about the stored state

    state_id
    A unique identifier for this state, -note that there might be infinite
    number of a state for a specific region-model/time

    region_model_id
    As a minimum the state contains the region_model_id that uniquely (within
    context) identifies the model that the state originated from.

    utc_timestamp
    The point in time where the state was sampled

    tags
    Not so important, but useful text list that we think could be useful in
    order to describe the state

    """

    def __init__(self, state_id=None, region_model_id=None,
                 utc_timestamp=None, tags=None):
        self.state_id = state_id
        self.region_model_id = region_model_id
        self.utc_timestamp = utc_timestamp
        self.tags = tags


class StateRepository:
    """
    Provides the needed functionality to maintain state for a region-model.

    We provide simple search functionality, based on StateInfo. The class
    should provide ready to use shyft.hydrology type of state for a specified
    region-model. It should also be able to stash away new states for later
    use/retrieval.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def find_state(self, region_model_id_criteria=None,
                   utc_period_criteria=None, tag_criteria=None):
        """
        Find the states in the repository that matches the specified criterias
        (note: if we provide match-lambda type, then it's hard to use a db to
        do the matching)

        Parameters
        ----------
        region_model_id_criteria:
            match-lambda, or specific string, list of strings
        utc_period_criteria:
            match-lambda, or period
        tag_criteria:
            match-lambda, or list of strings ?

        Returns
        -------
        List of StateInfo objects that matches the specified criteria
        """
        raise NotImplementedError(
            "Method 'find_state' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def get_state(self, state_id):
        """
        Parameters
        ----------
        state_id: string
            unique identifier of state

        Returns
        -------
        The state for a specified state_id, - the returned object/type can be
        passed directly to the region-model
        """
        raise NotImplementedError(
            "Method 'get_state' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def put_state(self, region_model_id, utc_timestamp,
                  region_model_state, tags=None):
        """
        Persist the state into the repository, assigning a new unique state_id,
        so that it can later be retrieved by that return state_id assigned.
        Parameters
        ----------
        region_model_id: string
            name of the model
        utc_timestamp:time
            time for which the state is (considered) valid
        region_model_state:string
            something that can be interpreted as state elsewhere
        tags:list of string
            optional, tags can be associated with a state so that it can be filtered later.
            note: we are not sure if this is useful, so it's optional feature
        Returns
        -------
        state_id: immutable id
            Identifier that can be used as argument to get_state.
        """
        raise NotImplementedError(
            "Method 'put_state' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def delete_state(self, state_id):
        """
        Delete the state associated with state_id,
        Throws
        ------
        StateRepositoryError: if invalid state_id, or not able to delete the
        state (access rights)

        Parameters
        ----------
        state_id: immutable id
            Identifier that uniquely identifies the state


        """
        raise NotImplementedError(
            "Method 'delete_state' not implemented for repository {}.".format(self.__class__.__name__))


class ForecastSelectionCriteriaError(Exception):
    pass


class ForecastSelectionCriteria:
    """
    A fc_selection_criteria is a tuple which specifies the collection of forecasts to be returned by
    GeoTsRepository methods get_forecast_collection and get_forecast_ensemble_collection.
    See Interfaces.GeoTsRepository

    Initialisation
    --------------
    The following initialisations are supported:
        * forecast created within period=UtcPeriod
            get forecast created within period
        * forecasts_with_start_within_period=UtcPeriod
            get forecast with nb_to_drop-horizon within period
        * forecasts_that_cover_period=UtcPeriod
            get forecast that cover period
        * forecast_that_intersect_period
            get forecast that intersects period
        * latest_available_forecasts={'number_of_forecast': int, 'forecasts_older_than': int}
            get latest number_of_forecast older than time_stamp
        * 'forecasts_at_reference_times': list(int)
            get latest forecast for list of time_stamps

    Examples
    --------
    fc_selection_criteria = ForecastSelectionCriteria(forecasts_created_within_period=UtcPeriod(0,3600))
    fc_selection_criteria.criterion
    Out: ('forecasts_created_within_period', <UtcPeriod at 0xc9c39ef538>)

    fc_selection_criteria = ForecastSelectionCriteria(latest_available_forecasts=
                            {'number_of_forecasts': 1, 'forecasts_older_than': api.Calendar().time(2018, 1, 20, 7)})
    fc_selection_criteria.criterion
    Out: ('latest_available_forecasts', {'forecasts_older_than': 1516431600, 'number_of_forecasts': 1})
    """

    def __init__(self, **kwargs):
        cri_lst = [(k, deepcopy(v)) if k in ['latest_available_forecasts', 'forecasts_at_reference_times']
                   else (k, v) for k, v in kwargs.items()]
        is_not_none = [cri[1] is not None for cri in cri_lst]
        if sum(is_not_none) != 1:
            raise ForecastSelectionCriteriaError('Only one of the selection criteria should be specified!')
        self._selected_criterion = cri_lst[is_not_none.index(True)]
        self._validate()

    @property
    def criterion(self):
        return self._selected_criterion

    def _validate(self):
        k, v = self._selected_criterion
        if k == 'forecasts_created_within_period':
            if not isinstance(v, UtcPeriod):
                raise ForecastSelectionCriteriaError(
                    "'forecasts_created_within_period' selection criteria should be of type UtcPeriod.")
        elif k == 'forecasts_with_start_within_period':
            if not isinstance(v, UtcPeriod):
                raise ForecastSelectionCriteriaError(
                    "'forecasts_with_start_within_period' selection criteria should be of type UtcPeriod.")
        elif k == 'forecasts_that_cover_period':
            if not isinstance(v, UtcPeriod):
                raise ForecastSelectionCriteriaError(
                    "'forecasts_that_cover_period' selection criteria should be of type UtcPeriod.")
        elif k == 'forecasts_that_intersect_period':
            if not isinstance(v, UtcPeriod):
                raise ForecastSelectionCriteriaError(
                    "'forecasts_that_intersect_period' selection criteria should be of type UtcPeriod.")
        elif k == 'latest_available_forecasts':
            v['forecasts_older_than'] = time(v['forecasts_older_than'])
            if not all([isinstance(v, dict), isinstance(v['number_of_forecasts'], int)]):
                raise ForecastSelectionCriteriaError(
                    "'latest_available_forecasts' selection criteria should be of type dict with keys "
                    "'number_of_forecasts' and 'forecasts_older_than', and with values of type int and "
                    "time respectively.")
        elif k == 'forecasts_at_reference_times':
            if not isinstance(v, list):
                raise ForecastSelectionCriteriaError(
                    "'forecasts_at_reference_times' selection criteria should be of type list.")
            v[:] = [time(t) for t in v]
        else:
            raise ForecastSelectionCriteriaError("Unrecognized forecast selection criteria.")


class GeoTsRepository:
    """
    Interface for GeoTsRepository (Geo Located Timeseries) objects.

    Responsibility:
     - to provide all hydrology relevant types of geo-located time-series,
       forecasts and ensembles needed for region-model inputs/calibrations.


    These are typical (but not limited to)
        precipitation: [mm/h]
        temperature: [deg C]
        wind (speed,direction): [m/s]
        radiation: [W/m^2]
        relative humidity: [%rh], range 0..1
        snow (depth,snow water equivalent, other snow-stuff,
              like coverage etc.)
        runoff/discharge (historical observed, we use this for calibration)

    geo-located time-series def:
        A time-series where the geographic location, (area) for which the
        values apply is well defined.

        For historical observations, we usually have point observations
        (xyz + coord-system id). Forecasts, might or might not be points, they
        could be a grid-shape. So far these have been treated as points (centre
        of grid-shape).
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_timeseries(self, input_source_types: List[str], utc_period: Any,
                       geo_location_criteria: Optional[Any] = None) -> Dict[str, Any]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation,temperature..)
        utc_period: UtcPeriod
            The utc time period that should (as a minimum) be covered.
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        geo_loc_ts: dictionary
            dictionary keyed by source type, where values are api vectors of geo
            located timeseries.
            Important notice: The returned time-series should at least cover the
            requested period. It could return *more* data than in
            the requested period, but must return sufficient data so
            that the f(t) can be evaluated over the requested period.
        """
        raise NotImplementedError(
            "Interface method 'get_timeseries' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def get_timeseries_ensemble(self, input_source_types: List[str], utc_period: Any,
                       geo_location_criteria: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation,temperature..)
        utc_period: UtcPeriod
            The utc time period that should (as a minimum) be covered.
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        ensemble: list of same type as get_timeseries
            Important notice: The returned time-series should at least cover the
            requested period. It could return *more* data than in
            the requested period, but must return sufficient data so
            that the f(t) can be evaluated over the requested period.
        """
        raise NotImplementedError(
            "Interface method 'get_timeseries_ensemble' not implemented for repository {}.".format(
                self.__class__.__name__))

    @abstractmethod
    def get_forecast(self, input_source_types: List[str], utc_period: Any, t_c: int,
                     geo_location_criteria: Optional[Any] = None) -> Dict[str, Any]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation, temperature, ...)
        utc_period: UtcPeriod
            The utc time period that should (as a minimum) be covered.
        t_c: int
            Forecast specification; return newest forecast older than t_c.
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        geo_loc_ts: dictionary
            dictionary keyed by source type, where values are api vectors of geo
            located timeseries.
            Important notice: The returned forecast time-series should at least cover the
            requested period. It could return *more* data than in
            the requested period, but must return sufficient data so
            that the f(t) can be evaluated over the requested period.
        """
        raise NotImplementedError(
            "Interface method 'get_forecast' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def get_forecast_ensemble(self, input_source_types: List[str], utc_period: Any, t_c: int,
                              geo_location_criteria: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation, temperature, ...)
        utc_period: UtcPeriod
            The utc time period that should (as a minimum) be covered.
        t_c: int
            Forecast specification; return newest forecast older than t_c.
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        ensemble: list of same type as get_forecast
            Important notice: The returned forecast time-series should at least cover the
            requested period. It could return *more* data than in
            the requested period, but must return sufficient data so
            that the f(t) can be evaluated over the requested period.
        """
        raise NotImplementedError(
            "Interface method 'get_forecast_ensemble' not implemented for repository {}.".format(
                self.__class__.__name__))

    @abstractmethod
    def get_forecast_collection(self, input_source_types: List, fc_selection_criteria: ForecastSelectionCriteria,
                                geo_location_criteria: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation, temperature, ...)
        fc_selection_criteria: ForecastSelectionCriteria
            Forecasts specifications; return all forecast that meet specification
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        List of geo_loc_ts:
            List of dictionaries keyed by source type, where values are
            api vectors of geo located timeseries.
        """
        raise NotImplementedError(
            "Interface method 'get_forecast_collection' not implemented for repository {}.".format(
                self.__class__.__name__))

    @abstractmethod
    def get_forecast_ensemble_collection(self, input_source_types: List, fc_selection_criteria: ForecastSelectionCriteria,
                                         geo_location_criteria: Optional[Any] = None) -> List[List[Dict[str, Any]]]:
        """
        Parameters
        ----------
        input_source_types: list
            List of source types to retrieve (precipitation, temperature, ...)
        fc_selection_criteria: ForecastSelectionCriteria
            Forecasts specification; return all forecast that meet specification
        geo_location_criteria: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            Polygon defining the boundary for selecting points. All points located inside this boundary will be fetched.

        Returns
        -------
        List (collection) of lists (ensemble members) of geo_loc_ts:
            List (collection indexed) of lists (ensemble indexed) dictionaries
            keyed by source type, where values are api vectors of geo located
            timeseries.
        """
        raise NotImplementedError(
            "Interface method 'get_forecast_ensemble_collection' not implemented for repository {}.".format(
                self.__class__.__name__))


class InterpolationParameterRepository:
    """
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_parameters(self, interpolation_id):
        """
        Parameters
        ----------
        interpolation_id: identifier (int| string)
            unique identifier within this repository that identifies one set of interpolation-parameters
        Returns
        -------
        parameter: shyft.hydrology type
            Interpolation parameter object
        """
        raise NotImplementedError(
            "Interface method 'get_parameters' not implemented for repository {}.".format(self.__class__.__name__))


class BoundingRegion:
    __metaclass__ = ABCMeta

    @abstractmethod
    def bounding_box(self, epsg):
        """
        Parameters
        ----------
        epsg: string
            epsg id of the resulting coordinates

        Returns
        -------
        x: np.ndarray
           x coordinates of the four corners, numbered clockwise from
           upper left corner.
        y: np.ndarray
           x coordinates of the four corners, numbered clockwise from
           upper left corner.
        """
        raise NotImplementedError(
            "Interface method 'bounding_box' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def bounding_polygon(self, epsg):
        """
        Parameters
        ----------
        epsg: string
            epsg id of the resulting coordinates

        Returns
        -------
        polygon: {shapely.geometry.Polygon, shapely.geometry.MultiPolygon}
            The boundary of the region.
        """
        raise NotImplementedError(
            "Interface method 'bounding_polygon' not implemented for repository {}.".format(self.__class__.__name__))

    @abstractmethod
    def epsg(self):
        """
        Returns
        -------
        epsg: string
            Epsg id of coordinate system
        """
        raise NotImplementedError(
            "Interface method 'epsg' not implemented for repository {}.".format(self.__class__.__name__))


class InterfaceError(Exception):
    pass


class TsStoreItem:
    """Represent a minimal mapping between the destination_id in the
    ts-store (like SmG, ts-name), and the lambda/function that from a
    supplied model extracts, and provides a ts possibly
    transformed/clipped to the wanted resolution and range.

    See: TimeseriesStore for usage

    """

    def __init__(self, destination_id, extract_method):
        """
        Parameters
        ----------
        destination_id: string or id
            meaningful for the time-series store, identifes a unique time-series

        extract_method: callable
            takes shyft.hydrology model as input and return a shyft.hydrology time-series
        """
        self.destination_id = destination_id
        self.extract_method = extract_method


class TimeseriesStore:
    """Represent a repository, that is capable of storing time-series
    (with almost no metadata, or they are provided elsewhere) Typical
    example would be Powel SmG, a netcdf-file-based ts-store etc.

    The usage of this class would be as a final step in orchestration,
    where we would like to save some simulation result to a database.

    """

    def __init__(self, tss, ts_item_list):
        """
        Parameters
        ----------
        tss: TsRepository
             provides a method tss.store({ts_id:shyft.hydrology.TimeSeries})
        ts_item_list: TsStoreItem
             provide a list of mappings between ts_id and model extract function
             ref. to TsStoreItem class for description.
        """
        self.tss = tss
        self.ts_item_list = ts_item_list

    def store_ts(self, region_model, is_forecast=False):
        """
        Extracts time-series from the region_model, according to
        the ts_item_list (ref. to constructor description and TsStoreItem)
        and store the result by means of the self.tss.store method.

        Parameters
        ----------
        region_model: shyft.hydrology model type, like PTGSKModel
            the model is passed to the extract-methods so that correct ts
            is fetched out.

        Returns
        -------
        True if storing all ts went well, otherwise False
        """
        tsid_ts_map = {tsi.destination_id: tsi.extract_method(region_model) for tsi in self.ts_item_list}
        return self.tss.store(tsid_ts_map, is_forecast)


class GeoLocationRepository:
    """
    Responsible for providing geo-locations for specified gis-identifiers
    It plays a similar role as TsRepository, but this one just
    provides geo-location information, given a specific id.

    A candidate for interfaces
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_locations(self, location_id_list, epsg_id=32632):
        """
        Given that we know the location-id (typically an integer, could be string)
        provide the locations (x,y,z) in a specified coordinate system
        Parameters
        ----------
        location_id_list:list of type integer
            identifies the gis-locationns, uniquely
        epsg_id: integer
            identifies the coordinate system

        Returns
        -------
        dictionary of identifier:tuple(x,y,z)
        """
        pass


class TsRepository:
    """
    Defines the contract of a time-series repository for this specific use
    The responsibility is to read and store time-series,forecasts, ensembles
    Notice that this TsRepository do not have geo-location associated with
    the time-series (forecast or ensembles) that it stores.
    The correlation between location/area and time-series are stored elsewhere,
    so this interface  mereyly provide methods to retrieve/store
    timeseries/forecast/ensembles.
    """

    @abstractmethod
    def read(self, list_of_ts_id, period):
        """
        """
        raise NotImplementedError("read")

    @abstractmethod
    def read_forecast(self, list_of_fc_id, period):
        """
        read and return the newest forecast that have the biggest overlap with specified period
        note that we should check that the semantic of this is reasonable
        """
        raise NotImplementedError("read_forecast")

    @abstractmethod
    def store(self, timeseries_dict):
        """ Store the supplied time-series to the underlying db-system.
            Parameters
            ----------
            timeseries_dict: dict string:timeseries
                the keys are the wanted ts(-path) names
                and the values are shyft time-series.
                If the named time-series does not exist, create it.
        """
        raise NotImplementedError("read_forecast")
