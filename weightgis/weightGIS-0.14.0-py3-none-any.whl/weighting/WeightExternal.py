from miscSupports import load_json, write_json, flatten
from collections import Counter
from pathlib import Path


class WeightExternal:
    def __init__(self, external_data_path, weights_path, date_max, delimiter="__"):

        # Load the external data
        assert Path(external_data_path).exists(), "Path to external data is invalid"
        self.database = load_json(external_data_path)

        # The delimiter to access GID and the end date for weighting
        self.delimiter = delimiter
        self._user_end_date = date_max

        # Create a GID: Place lookup dict to aid extraction of data
        self.searcher = {place.split(self.delimiter)[0]: place for place in self.database.keys()}

        # The unique attributes from all places
        self.attributes = list(set([attr for place in self.database.keys() for attr in self.database[place].keys()
                               if isinstance(self.database[place][attr], dict)]))

        # The weight dates created via AssignWeights
        self._weights_dates = load_json(weights_path)

        # Output json's of the master weighting database as well as a non_common to aid finding weight errors
        self._master = {}
        self._non_common = {place_name: {} for place_name in self._weights_dates}

    def weight_external(self, write_path, write_name="Weighted"):
        """
        This will use all the places and weights from the weights by dates file, and use it to weight an external data
        source.
        """
        for place_name in self._weights_dates:

            # See how many changes exist for this place
            dates_of_change = [date for date in self._weights_dates[place_name].keys()]

            # If there is only one date, we have no weighting to do as the place remains unchanged from its first state
            if (len(dates_of_change) == 1) and self.extract_data(place_name):
                self._master[place_name] = self.extract_data(place_name)

            # Otherwise we need to weight the data, and potentially consider non-common dates across places
            else:
                self._master[place_name] = self._weight_place(place_name, dates_of_change)

        # Write out the weighted data
        print("Finished constructing weights - writing to file")
        write_json(self._master, write_path, write_name)
        if len(self._non_common.keys()) > 0:
            write_non_common = {key: value for key, value in self._non_common.items() if len(value) > 0}
            write_json(write_non_common, write_path, "NonCommonDates")

    def extract_data(self, place):
        """
        Check to see if the database contains a given place
        """
        try:
            return self.database[self._search_name(place)]
        except KeyError:
            return None

    def _search_name(self, place_name):
        """
        Extract the key from a place_name, and use that to get the data key from the using this place_name as key in the
        search_key dict
        """
        return self.searcher[place_name.split(self.delimiter)[0]]

    def _weight_place(self, place_name, dates_of_change):
        """
        Use weights and dates from a combination of ConstructWeights and AssignWeights to create a weight value set for
        a given place.

        If a place changes over time, then we need to weight data based on those changes. If there is only a single
        place, for example a place used to be 50% larger so in a previous change it represents 50% of the values, then
        we just need to weight all the values by that weight.

        If the place used to made up of multiple places, then we need to weight each place by that weight, and then sum
        the values. The later has more problems associated with it, as you need data in ALL of the places otherwise you
        end up with uncommon dates where you cannot weight a certain district because you don't have all the data you
        need.

        :param place_name: The place we wish to construct weights for
        :type place_name: str

        :param dates_of_change: The yyyymmdd dates of changes
        :type dates_of_change: list

        :return: A dict of all the weighted values for all the attributes found for this place
        :rtype: dict
        """
        place_dict = {attr: {} for attr in self.attributes}

        # For each change that occurs in this place
        for index, date in enumerate(dates_of_change, 1):

            # Set the date min and max dates for the current date change
            date_min, date_max = self._set_min_max_date(index, date, dates_of_change)

            # If there is only one place for this change, then we just need to weight the values relevant to the dates
            if len(self._weights_dates[place_name][date]) == 1:
                self._weight_single(place_name, date, place_dict, date_min, date_max)

            # Otherwise we have to make sure all places, have all dates, and sum weighted values appropriately .
            else:
                self._weight_multiple(place_name, date, place_dict, date_min, date_max)

        return place_dict

    def _set_min_max_date(self, index, date, dates_range):
        """
        If we have reached the last date provided, then set max date to be the max provided by the user, otherwise
        create a time period from the current date and the next date
        """
        if index < len(dates_range):
            return int(date), int(dates_range[index])
        else:
            return int(date), int(self._user_end_date)

    def _weight_single(self, place_name, weight_date, place_dict, date_min, date_max):
        """
        Extract data from a single location and weight the values between a min and max date

        If there is only a single place, then we don't need to worry about non-common dates across weight places and we
        can just weight the values of each attribute and append them to our place dict as long as the database contains
        information about this place.

        :param place_name: The current name of the place we are constructing weights for
        :type place_name: str

        :param weight_date: The current date of change to load weights from
        :type weight_date: str

        :param place_dict: The storage dict for all the data from this place which will be appended to the master json
        :type place_dict: dict

        :param date_min: The start date of this weight
        :type date_min: str | int

        :param date_max: The end date of this weight
        :param date_max: str | int

        :return: Nothing, append weight values per date with the date range to the place_dict then stop
        :rtype: None
        """
        # Extract the place_names place key and weight for this place
        place_key, weight = self._extract_weight_place(self._weights_dates[place_name][weight_date])

        # If the database contains information about this place
        if self.extract_data(place_key):

            # For each unique attribute
            for attr in self.attributes:

                # Isolate the data from the database for this place's attribute
                try:
                    data = self.extract_data(place_key)[attr]

                    # Assign the weight value for this date for this attribute to the place json database dict
                    for date, value in data.items():
                        if date_min <= int(date) < date_max:
                            place_dict[attr][int(date)] = self.calculate_weight(value, weight)

                # If the attribute doesn't exist for this place, pass
                except KeyError:
                    pass

        # Warn the user that we have failed to find a location, so it will be missing
        else:
            print(f"Warning: No data found for {place_key}")

    @staticmethod
    def _extract_weight_place(date_data):
        """
        Extract the places and weights for a given date for a given place in weight_dates
        """
        weight_places = [place for place in date_data.keys()]
        weight_list = [weight for weight in date_data.values()]

        if (len(weight_places) == 1) and (len(weight_list) == 1):
            return weight_places[0], weight_list[0]
        else:
            return weight_places, weight_list

    @staticmethod
    def calculate_weight(value, weight):
        """
        A weight value is equal to the value * (percentage weight / 100)

        Note
        -----
        Weights in weightGIS are storage as if out of 100.00. so 50% is 50.00. When weighting we need to multiple by
        a decimal so the weight is restructured back into a decimal form, for example 0.5, by dividing all the weights
        by 100.
        """
        if isinstance(value, str):
            return value
        else:
            return value * (weight / 100)

    def _weight_multiple(self, place_name, weight_date, place_dict, date_min, date_max):
        """
        weight a places values based on weights of multiple places

        If there are multiple places in this change period, then we need to extract the data and check that we have the
        same dates for each place in this change. If we do, we can sum the weighted values for each date.

        :param place_name: The current name of the place we are constructing weights for
        :type place_name: str

        :param weight_date: The current date of change to load weights from
        :type weight_date: str

        :param place_dict: The storage dict for all the data from this place which will be appended to the master json
        :type place_dict: dict

        :param date_min: The start date of this weight
        :type date_min: str | int

        :param date_max: The end date of this weight
        :param date_max: str | int

        :return: Nothing, append weight values per date with the date range to the place_dict then stop
        :rtype: None

        :raise AssertionError: If the len of validate dates is not equal to the number of places after trying to pass
            only places within common attributes
        """

        # Extract the places and weights involved in this change
        weight_places, weights = self._extract_weight_place(self._weights_dates[place_name][weight_date])

        # Determine if we have data for each place
        all_valid = [self.extract_data(place) for place in weight_places if self.extract_data(place)]

        # If we have data for both places
        if len(all_valid) == len(weight_places):

            for attr in self.attributes:
                try:
                    # Not all places will have the same attributes, This should be picked up by a KeyError but if not
                    # the assertion should catch it
                    validate_dates = [self.extract_data(place)[attr] for place in weight_places]
                    assert len(validate_dates) == len(weight_places), "Critical Error: KeyError failed to catch " \
                                                                      "missing attribute"

                    # Extract all the common dates
                    dates_list = self._extract_usable_dates(attr, date_min, date_max, weight_places, place_name)

                    # Use these dates to create a set of weight values
                    weight_values = [self._weight_summation(date, attr, weight_places, weights) for date in dates_list]

                    # Assign the weighted values to the dates
                    for date, value in zip(dates_list, weight_values):
                        place_dict[attr][int(date)] = value
                except KeyError:
                    pass

        else:
            print(f"Warning: Found {len(all_valid)} out of {len(weight_places)} places for {place_name}'s weighted "
                  f"places of: {weight_places}\n       : Data from {weight_date}-{date_max} will be dropped\n")

    def _extract_usable_dates(self, attr, date_min, date_max, weight_places, place_name):
        """
        Determine if all required dates are present and return the common dates between places. If the location does not
        contain common dates,  save the location date errors to a separate json

        If we have multiple places, not all places may have the same dates. We cannot create a weighted value from
        multiple places if some of those places are missing. So in these cases, nothing is written to the dataset, and
        a line explaining what was missing is written out to a csv file. If we do have common dates dates for a given
        place, then we return these dates which will be indexed to extract the values associated with them

        :param attr: The current attribute we are weight values for
        :type attr: str

        :param date_min: The start date of this weight
        :type date_min: str | int

        :param date_max: The end date of this weight
        :param date_max: str | int

        :param weight_places: The places that are involved in weighting for this place between date_min and date_max
        :type weight_places: list

        :param place_name: The current name of the place we are constructing weights for
        :type place_name: str

        :return: All the common dates for the weight_places involved in this place
        :rtype: list
        """

        # Isolate all the dates for all the weights places in place_list
        dates_list = flatten([list(self.extract_data(place)[attr].keys()) for place in weight_places])

        # Keep the dates within the time range we are looking for
        dates_list = [int(date) for date in dates_list if date_min <= int(date) < date_max]

        # Count each occurrence of a date to insure we have the same number in all places
        dates_dict = Counter(dates_list)

        # If we have any non_common dates, we can't use this date for weighting as we won't have data in all of the
        # places involved in the weight
        non_common_dates = [date for date in dates_dict if dates_dict[date] != len(weight_places)]
        if len(non_common_dates) > 0:
            # Write out this information for users so they can fix their raw data
            self._non_common[place_name][attr] = {"Places": weight_places, "Target": len(weight_places),
                                                  "Dates": {d: dates_dict[d] for d in non_common_dates}}
            print(f"Warning: Non Common dates found for {attr} in {weight_places}")

        # Return common dates list
        return sorted([date for date in dates_dict if date not in non_common_dates])

    def _weight_summation(self, date, attr, place_list, weights):
        """
        Create a summed value from all the weights of the places
        """

        # Isolate the raw value from each place
        values = [self.extract_data(place)[attr][str(date)] for place in place_list]

        # Weight these values
        weighted_values = [self.calculate_weight(value, weight) for value, weight in zip(values, weights)]

        # Return them if they are all ints or floats, else return NA
        if all(isinstance(v, (int, float)) for v in weighted_values):
            return sum(weighted_values)
        else:
            return "NA"
