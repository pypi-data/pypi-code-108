# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the location closest selector class."""

import copy
import math
from typing import Union

import pandas as pd
from azureml.telemetry.activity import ActivityType
from pyspark.sql.functions import col, dense_rank, rank, udf
from pyspark.sql.types import BooleanType, DoubleType
from pyspark.sql.window import Window
from scipy.spatial import cKDTree

from .._utils.random_utils import random_tag
from ..accessories._loggerfactory import _LoggerFactory
from ..accessories.customer_data import CustomerData
from ..accessories.location_data import LocationData
from ..aggregators.aggregator import Aggregator
from ..environ import PandasEnv, SparkEnv
from ..granularities.granularity import LocationClosestGranularity
from .enricher_selector import EnricherLocationSelector


class LocationClosestSelector (EnricherLocationSelector):
    """Defines a join of customer data with public data using the criteria of closest spherical distance.

    .. remarks::

        The static method ``process(self, env, customer_data, public_data, aggregator, join_keys, debug)`` is
        used to join the data based on this selector where:

        * ``customer_data`` is an instance of azureml.opendatasets.accessories.location_data.LocationData
        * ``public_data`` is an instance of azureml.opendatasets.accessories.location_data.LocationData
        * ``aggregator`` is one of azureml.opendatasets.aggregators.aggregator.Aggregator
        * ``join_keys`` is a list of join key pairs
        * ``debug`` indicates whether to print debug logs.

        This method returns a tuple of: altered customer data class instance, altered public data class instance, and
        a list of join key pairs.

    :param _granularity: A location granularity to use in the joining of data.
    :type _granularity: azureml.opendatasets.granularities.granularity.LocationClosestGranularity
    :param enable_telemetry: Indicates whether to enable telemetry.
    :type enable_telemetry: bool
    """

    def __init__(self, _granularity: LocationClosestGranularity, enable_telemetry: bool = True):
        """Initialize with location granularity."""
        self.granularity = _granularity

        self.location_id = 'location_id' + random_tag()
        self.location_lat = 'location_lat' + random_tag()
        self.location_long = 'location_long' + random_tag()
        self.rank1 = 'rank1' + random_tag()
        self.public_rankgroup = 'public_rankgroup' + random_tag()
        self.customer_rankgroup = 'customer_rankgroup' + random_tag()
        self.distance_name = 'distance_name' + random_tag()
        self.enable_telemetry = enable_telemetry
        if self.enable_telemetry:
            self.log_properties = self._get_common_log_properties()

    def _find_lat_long_boundary(self, env: Union[SparkEnv, PandasEnv], customer_data: LocationData):
        """
        Find the max/min latitude/longitude of the input customer data.

        :param env: The runtime environment.
        :param customer_data: an instance of LocationData class
        :return: max longtitude, min longitude, max latiduce, min latitude
        """
        # if normal latlong, just find min max
        customer_dataset = customer_data.data
        if isinstance(env, SparkEnv):
            maxLong = float((customer_dataset.agg(
                {customer_data.longitude_column_name: "max"}).collect())[0][0])
            minLong = float((customer_dataset.agg(
                {customer_data.longitude_column_name: "min"}).collect())[0][0])
            maxLat = float((customer_dataset.agg(
                {customer_data.latitude_column_name: "max"}).collect())[0][0])
            minLat = float((customer_dataset.agg(
                {customer_data.latitude_column_name: "min"}).collect())[0][0])
            return maxLong, minLong, maxLat, minLat
        else:
            maxLong = customer_dataset[customer_data.longitude_column_name].max(
            )
            minLong = customer_dataset[customer_data.longitude_column_name].min(
            )
            maxLat = customer_dataset[customer_data.latitude_column_name].max()
            minLat = customer_dataset[customer_data.latitude_column_name].min()
            return maxLong, minLong, maxLat, minLat

    def _get_public_data_filtered_locations(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: LocationData,
            public_data: LocationData,
            cord_count: int):
        """Given inpt customer data, find the latitude/longitude boundary.

        It will filter the public data within the boundary +/- some degrees.
        """
        public_dataset = public_data.data
        maxLong, minLong, maxLat, minLat = self._find_lat_long_boundary(
            env, customer_data)
        if isinstance(env, SparkEnv):
            # get all unique public_data_filtered_location from 3p dataset
            public_data_filtered_location = public_dataset.select(
                public_dataset[public_data.id].alias(self.location_id),
                public_dataset[public_data.latitude_column_name].alias(
                    self.location_lat),
                public_dataset[public_data.longitude_column_name].alias(self.location_long)).dropDuplicates()

            fuzzy_boundary = self.granularity.lower_fuzzy_boundary \
                if cord_count > self.granularity.cord_limit \
                else self.granularity.upper_fuzzy_boundary
            public_data_filtered_location = public_data_filtered_location. \
                filter(public_data_filtered_location[self.location_long] < maxLong + fuzzy_boundary). \
                filter(public_data_filtered_location[self.location_long] > minLong - fuzzy_boundary). \
                filter(public_data_filtered_location[self.location_lat] < maxLat + fuzzy_boundary). \
                filter(
                    public_data_filtered_location[self.location_lat] > minLat - fuzzy_boundary)

            return public_data_filtered_location
        else:
            public_data_filtered_location = public_dataset[[
                public_data.id,
                public_data.latitude_column_name,
                public_data.longitude_column_name]].rename(
                    index=str,
                    columns={
                        public_data.id: self.location_id,
                        public_data.latitude_column_name: self.location_lat,
                        public_data.longitude_column_name: self.location_long}).drop_duplicates()

            fuzzy_boundary = self.granularity.lower_fuzzy_boundary \
                if cord_count > self.granularity.cord_limit else self.granularity.upper_fuzzy_boundary
            public_data_filtered_location = public_data_filtered_location[
                (public_data_filtered_location[self.location_long] < maxLong + fuzzy_boundary) & (
                    public_data_filtered_location[self.location_long] > minLong - fuzzy_boundary) & (
                        public_data_filtered_location[self.location_lat] < maxLat + fuzzy_boundary) & (
                            public_data_filtered_location[self.location_lat] > minLat - fuzzy_boundary)]

            return public_data_filtered_location

    def _get_possible_locations(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: LocationData,
            public_data: LocationData,
            join_keys: list):
        """Get possible public data locations that are close to customer data locations."""
        # get unique public_data_filtered_location as customer_datacord from customer customer_data
        keys = [customer_data.longitude_column_name,
                customer_data.latitude_column_name]
        for pair in join_keys:
            keys.append(pair[0])
        if isinstance(env, SparkEnv):
            customer_datacord = customer_data.data.select(
                keys).dropDuplicates()

            cord_count = customer_datacord.count()
            public_data_filtered_location = self._get_public_data_filtered_locations(
                env, customer_data, public_data, cord_count)

            return public_data_filtered_location, customer_datacord
        else:
            customer_data_cord = customer_data.data[keys].drop_duplicates()

            cord_count = len(customer_data_cord.index)
            public_data_filtered_location = self._get_public_data_filtered_locations(
                env, customer_data, public_data, cord_count)

            return public_data_filtered_location, customer_data_cord

    def _get_closest_location(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: CustomerData,
            public_data_filtered_location: object,
            customer_data_cord: object,
            close_to: object,
            get_distance: object):
        """
        Get closest 3p location to each customer location.

        public_data_filtered_location is latlong from third party,
        customer_data_cord is latlong from customer data.
        """
        # try binary search instead later for optimize, for now
        # cross join 3p data and custome rdata lat long. try to find closest lat/long pairing
        if isinstance(env, SparkEnv):
            result = public_data_filtered_location.alias(
                'a').crossJoin(customer_data_cord.alias('b'))
            result = result.filter(
                close_to(
                    self.location_long,
                    self.location_lat,
                    customer_data.longitude_column_name,
                    customer_data.latitude_column_name))
            result = result.withColumn(
                self.distance_name,
                get_distance(
                    self.location_long,
                    self.location_lat,
                    customer_data.longitude_column_name,
                    customer_data.latitude_column_name))

            result = result.select('*', dense_rank().over(
                Window.orderBy(
                    customer_data.latitude_column_name,
                    customer_data.longitude_column_name)).alias(self.public_rankgroup))

            result = result.withColumn(
                self.customer_rankgroup, col(self.public_rankgroup))

            # only keep shortest distance row for each store
            window = Window.partitionBy(
                customer_data.latitude_column_name,
                customer_data.longitude_column_name).orderBy(result[self.distance_name].asc())

            top = result.select('*', rank().over(window).alias(self.rank1))
            top = top.filter(top[self.rank1] <= self.granularity.closest_top_n)
            return top
        else:
            # try binary search instead later for optimize, for now
            # cross join 3p data and custome rdata lat long. try to find closest lat/long pairing
            result = public_data_filtered_location.assign(key=1).merge(
                customer_data_cord.assign(key=1), on='key').drop('key', 1)
            column_close_to = 'column_close_to' + random_tag()
            result[column_close_to] = result[[
                self.location_long,
                self.location_lat,
                customer_data.longitude_column_name,
                customer_data.latitude_column_name]].apply(close_to, axis=1)
            result = result[result[column_close_to]].drop(
                columns=[column_close_to], axis=1)
            result[self.distance_name] = result[[
                self.location_long,
                self.location_lat,
                customer_data.longitude_column_name,
                customer_data.latitude_column_name]].apply(get_distance, axis=1)

            column_tmp = 'column_tmp' + random_tag()

            result[column_tmp] = result[[
                customer_data.latitude_column_name,
                customer_data.longitude_column_name]].fillna(0).apply(
                    lambda x: math.ceil((90 + float(x[0])) * 1000) * 1000000 + math.ceil(
                        (180 + float(x[1])) * 1000), axis=1)
            result[self.public_rankgroup] = result[column_tmp].rank(
                axis=0, method='dense').astype(int)
            result[self.customer_rankgroup] = result[self.public_rankgroup]

            # only keep shortest distance row for each store
            result[column_tmp] = result[self.distance_name].groupby([
                result[customer_data.latitude_column_name],
                result[customer_data.longitude_column_name]]).rank()

            top = result[result[column_tmp] <= self.granularity.closest_top_n].drop(
                columns=[column_tmp], axis=1)

            return top

    def _get_closest_location_kdTree(
            self,
            customer_data,
            public_data_filtered_location,
            customer_data_cord):
        """
        Get closest 3p location to each customer location.

        public_data_filtered_location is latlong from third party,
        customer_data_cord is latlong from customer data.

        The method is using cKDTree to get nearest location for given long/lat pair.
        """
        # extract query source and target, only with long/lat fields
        publicDF = public_data_filtered_location[[
            self.location_long, self.location_lat]]
        publicArr = publicDF.values
        customerDF = customer_data_cord[[
            customer_data.longitude_column_name, customer_data.latitude_column_name]]
        customerArr = customerDF.values

        # build kdTree with default leafsize=16
        tree = cKDTree(publicArr)

        # do query with location granularity
        # ii is returned as ndarray containing the index set of publicDF
        dd, ii = tree.query(customerArr, k=self.granularity.closest_top_n)

        # e.g. [0, 5, 9, 3]
        # it means:
        #   the 1st row of publicDF is the nearest location to the 1st row of customerDF
        #   the 6th row of publicDF is the nearest location to the 2nd row of customerDF
        #   the 10th row of public DF is the nearest location to the 3rd row of customerDF
        #   ......
        # the count of ii is the same as the count of customer_data_cord, so just directly concat.
        if self.granularity.closest_top_n == 1:
            public_selection_index = ii
            customer_selection_index = range(0, len(customer_data_cord))
        # e.g. [[0, 3], [5, 4], [2, 0], [8, 3]]
        # it means:
        #   the 1st and 4th rows of publicDF are the first and second nearest locations to the 1st row of customerDF
        #   the 6th and 5th rows of publicDF are the first and second nearest locations to the 2nd row of customerDF
        #   the 3rd and 1st rows of publicDF are the first and second nearest locations to the 3rd row of customerDF
        #   ......
        # so we cannot just direct concat the two DFs,
        # we need to first duplicate the rows of customerDF for same sete of neaest locations in publicDF
        else:
            public_selection_index = [i for idr, r in enumerate(ii) for i in r]
            customer_selection_index = [
                idr for idr, r in enumerate(ii) for i in r]

        public_customer_selection = pd.concat(
            [public_data_filtered_location.iloc[public_selection_index, :].reset_index(drop=True),
                customer_data_cord.iloc[customer_selection_index, :].reset_index(drop=True)],
            axis=1,
            sort=False)

        column_tmp = 'column_tmp' + random_tag()

        # add ranking columns
        public_customer_selection[column_tmp] = public_customer_selection[[
            customer_data.latitude_column_name,
            customer_data.longitude_column_name]].fillna(0).apply(
                lambda x: math.ceil((90 + float(x[0])) * 1000) * 1000000 + math.ceil(
                    (180 + float(x[1])) * 1000), axis=1)

        public_customer_selection[self.public_rankgroup] = public_customer_selection[column_tmp].rank(
            axis=0,
            method='dense').astype(int)
        public_customer_selection[self.customer_rankgroup] = public_customer_selection[self.public_rankgroup]
        public_customer_selection = public_customer_selection.drop(
            columns=[column_tmp], axis=1)

        return public_customer_selection

    def process(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: LocationData,
            public_data: LocationData,
            aggregator: Aggregator,
            join_keys: list,
            debug: bool):
        """
        Join customer data and public data using the specified aggregator.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param customer_data: An instance of a LocationData derived class.
        :type customer_data: azureml.opendatasets.accessories.location_data.LocationData
        :param public_data: An instance of a LocationData derived class.
        :type public_data: azureml.opendatasets.accessories.location_data.LocationData
        :param aggregator: An aggregator.
        :type aggregator: azureml.opendatasets.aggregators.aggregator.Aggregator
        :param join_keys: A list of join key pairs.
        :type join_keys: builtin.list
        :param debug: Indicates whether to print debug logs.
        :type debug: bool
        :return: A tuple of: altered customer data class instance, altered public data class instance, and
            a list of join key pairs.
        :rtype: tuple
        """
        public_dataset = public_data.data

        public_dataset = aggregator.process_public_dataset(
            env, public_dataset, public_data.cols, join_keys)
        if isinstance(env, SparkEnv):
            if debug:
                print(
                    '* public_dataset in location_closest_selector: %d' %
                    public_dataset.count())
                print(public_dataset)

            # get possible 3p public_data_filtered_location
            # that are close to customer data public_data_filtered_location
            public_data_filtered_location, customer_data_cord = \
                self._get_possible_locations(
                    env, customer_data, public_data, join_keys)

            if debug:
                print('* public_data_filtered_location: %d' %
                      public_data_filtered_location.count())
                print(public_data_filtered_location)
                print('* customer_data_cord: %d' % customer_data_cord.count())
                print(customer_data_cord)

            # initialize udfs
            # find distance between two lat long pairs
            distance_udf = udf(self.get_distance, DoubleType())
            # find if two lat long pairs are within 10 degrees of each other
            close_to_udf = udf(self.close_to, BooleanType())

            # get closest 3p location to each customer location
            # top customer_dataset contains rows that have customer lat long pair
            # and closest 3p lat long pair and 3p id
            top = self._get_closest_location(
                env,
                customer_data,
                public_data_filtered_location,
                customer_data_cord,
                close_to_udf,
                distance_udf)
            top.cache()

            if debug:
                print('* top: %d' % top.count())
                print(top)

            # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
            join_keys.append((self.location_id, public_data.id))

            join_conditions = []
            for pair in join_keys:
                join_conditions.append(top[pair[0]] == public_dataset[pair[1]])
            public_dataset = public_dataset.alias('a').join(
                top.alias('b'),
                join_conditions)\
                .select('a.*', '.'.join(['b', self.public_rankgroup]))\
                .drop(public_data.latitude_column_name, public_data.longitude_column_name, public_data.id)

            join_keys.remove((self.location_id, public_data.id))

            # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
            join_keys.append((self.customer_rankgroup, self.public_rankgroup))

            if debug:
                print('* public_dataset after join with top: %d' %
                      public_dataset.count())
                print(public_dataset)
                print('* distance_name: %s' % self.distance_name)
                print('* location_id: %s' % self.location_id)

            altered_public_data = copy.copy(public_data)
            altered_public_data.data = public_dataset
            altered_public_data.id = self.public_rankgroup

            if debug:
                altered_customer_dataset = customer_data.data.alias('a').join(
                    top.alias('b'),
                    [customer_data.latitude_column_name,
                        customer_data.longitude_column_name],
                    how='left').select(
                        'a.*',
                        self.distance_name,
                        self.location_id,
                        '.'.join(['b', self.customer_rankgroup])).dropDuplicates()
            else:
                altered_customer_dataset = customer_data.data.alias('a').join(
                    top.alias('b'),
                    [customer_data.latitude_column_name,
                        customer_data.longitude_column_name],
                    how='left').select(
                        'a.*',
                        '.'.join(['b', self.customer_rankgroup])).dropDuplicates()

            altered_customer_dataset.cache()

            altered_customer_data = copy.copy(customer_data)
            altered_customer_data.data = altered_customer_dataset

            if debug:
                print('* join_keys: %s' % str(join_keys))

            altered_public_data.data.cache()

            return altered_customer_data, altered_public_data, join_keys
        else:
            if debug:
                print('* public_dataset in location_closest_selector: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))

            # get possible 3p public_data_filtered_location
            # that are close to customer data public_data_filtered_location
            public_data_filtered_location, customer_data_cord = self._get_possible_locations(
                env, customer_data, public_data, join_keys)

            if debug:
                print('* public_data_filtered_location: %d' %
                      len(public_data_filtered_location.index))
                print(public_data_filtered_location.head(5))
                print('* customer_data_cord: %d' %
                      len(customer_data_cord.index))
                print(customer_data_cord.head(5))

            # get closest 3p location to each customer location
            # top customer_dataset contains rows that have customer lat long pair
            # and closest 3p lat long pair and 3p id
            if self.enable_telemetry:
                self.log_properties['RegistryId'] = public_data.registry_id
                location_gran_log_property = self.granularity.get_log_property()
                if location_gran_log_property is not None and len(location_gran_log_property) == 2:
                    self.log_properties[location_gran_log_property[0]] = \
                        location_gran_log_property[1]
                self.log_properties['ActivityType'] = ActivityType.INTERNALCALL
                top = self._get_closest_location_kdTree(
                    customer_data,
                    public_data_filtered_location,
                    customer_data_cord)
                _LoggerFactory.log_event(
                    '_get_closest_location_kdTree', **self.log_properties)
            else:
                top = self._get_closest_location_kdTree(
                    customer_data,
                    public_data_filtered_location,
                    customer_data_cord)

            # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
            join_keys.append((self.location_id, public_data.id))
            customer_keys, public_keys = list(zip(*join_keys))

            if debug:
                print('* top: %d' % len(top.index))
                print(top.head(5))
                print(public_keys)
                print(customer_keys)

            public_dataset = public_dataset.merge(
                top,
                left_on=list(public_keys),
                right_on=list(customer_keys))[list(public_dataset.columns) + [self.public_rankgroup]]
            public_dataset = public_dataset[list(public_dataset.columns)].drop(
                columns=[
                    public_data.latitude_column_name,
                    public_data.longitude_column_name,
                    public_data.id], axis=1)

            join_keys.remove((self.location_id, public_data.id))

            # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
            join_keys.append((self.customer_rankgroup, self.public_rankgroup))

            if debug:
                print('* public_dataset after join with top: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))
                print('* distance_name: %s' % self.distance_name)
                print('* location_id: %s' % self.location_id)
                print('* public_rankgroup: %s' % self.public_rankgroup)

            altered_public_data = copy.copy(public_data)
            altered_public_data.data = public_dataset
            altered_public_data.id = self.public_rankgroup

            altered_customer_dataset = customer_data.data.merge(
                top,
                on=[customer_data.latitude_column_name,
                    customer_data.longitude_column_name],
                how='left')
            if debug:
                print(altered_customer_dataset.head(3))
                altered_customer_dataset = altered_customer_dataset[
                    list(customer_data.data.columns) + [
                        self.location_id, self.customer_rankgroup]].drop_duplicates()
            else:
                altered_customer_dataset = altered_customer_dataset[
                    list(customer_data.data.columns) + [self.customer_rankgroup]].drop_duplicates()

            altered_customer_data = copy.copy(customer_data)
            altered_customer_data.data = altered_customer_dataset

            if debug:
                print('* join_keys: ' + str(join_keys))

            return altered_customer_data, altered_public_data, join_keys
