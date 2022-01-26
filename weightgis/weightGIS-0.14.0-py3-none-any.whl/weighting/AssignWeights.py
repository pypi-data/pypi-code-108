from miscSupports import load_json, write_json, invert_dates
from csvObject.csvObject import CsvObject
from pathlib import Path


class AssignWeights:
    def __init__(self, weights_path, working_dir, write_name, dates_path, population_weights=True, raw_years=None):
        """
        This class contains the methods needed to actually assign the weights to a usable database
        """

        self._working_dir, self._weights, self._weight_key, self._dates, self._date_indexes = self._setup(
            working_dir, weights_path, population_weights, dates_path)

        self._working_dir = Path(working_dir)
        self._write_name = write_name
        self._raw_years = raw_years

    def assign_weights_dates(self, adjust_dates=False):
        """
        This takes all the weights that have occurred, and a file given by the user that contains information on when
        places change in terms of dates, and writes out the weights by the dates they occur.

        :param adjust_dates: if you data is recorded in years, but your dates of change in year-month-day, you can
            adjust all of your dates by assigning the additional characters here as a string
        :type adjust_dates: str

        :return: Nothing, just write out the file
        :rtype: None
        """

        weights_list = {}
        for place_over_time in self._weights:
            # Extract the number of possible changes from the weight data and determine if any changes occur from the
            # dates data
            shapefile_years = self._set_shapefile_years(adjust_dates, place_over_time)
            changes = self._extract_relevant_changes(place_over_time.split("__")[0], shapefile_years)

            if len(changes) == 0:
                # If no changes occur, just access the first entry and set our dictionary to these values
                weights_list[place_over_time] = {min(shapefile_years): {place_over_time: 100.0}}
            else:
                # Otherwise assign dates of the changes to occur over time.
                weights_over_time = self._assigned_dates_to_weights(
                    place_over_time, self._observed_dates(changes, shapefile_years), shapefile_years)

                weights_list[place_over_time] = {date: {place: weight for place, weight in place_weights}
                                                 for date, place_weights in weights_over_time}

        write_json(weights_list, self._working_dir, self._write_name)

    def _extract_relevant_changes(self, current_gid, shapefile_years, dl="-"):
        """
        If the GID is within the a given row of data from dates file then we want to extract the date columns from that
        row by using the dates_indexes as an indexer. The format that is used is yyyymmdd so we then want to invert
        these proper dates and only keep the ones that are within the range of our census years

        :param current_gid: The current GID of the current place
        :type: str

        :param dl: The character used as the blank
        :type dl: str

        :return: A list of relevant dates of changes in the format of [yyyymmdd, ... yyyymmdd]
        :rtype: list
        """

        place = self._get_place(current_gid)
        # Create the dates from Weight_Dates.csv
        dates = [int(invert_dates(place[i])) for i in range(len(place)) if i in self._date_indexes and place[i] != dl]

        # If we have raw years provided, because we have additional dates within the shapefiles, then look for
        # them
        if self._raw_years:
            return [s for s in shapefile_years if (s not in self._raw_years) and (s not in dates)] + dates

        # Otherwise just return dates from the dates file
        else:
            return dates

    def _get_place(self, current_gid):
        """Extract the row we need if the gid is in it"""
        for place in self._dates.row_data:
            if str(current_gid) in place:
                return place

    def _observed_dates(self, changes, shapefile_years):
        """
        Multiple changes can occur in a census period but only the latest can be observed. This groups the changes by
        census period and the returns a list of dates that can actually be observed

        :param changes: list of changes in yyyymmdd format
        :type changes: list

        :return: A list of observed dates in the form of [yyyymmdd ... yyyymmdd]
        :rtype: list
        """

        census_year_groupings = []
        for change_date in changes:
            for index in range(len(shapefile_years)):
                if (shapefile_years[index] < change_date <= shapefile_years[index + 1]) and \
                        (index < len(shapefile_years) - 1):
                    census_year_groupings.append([shapefile_years[index + 1], change_date])

        return self._select_latest(census_year_groupings)

    @staticmethod
    def _select_latest(grouped_census_dates):
        """
        This will selected the latest year between a given census period, as only the latest can be observed in the
        shapefile

        :param grouped_census_dates: List of dates in the form of [[census_year, date]] where both dates are in yyyymmdd
        :type grouped_census_dates: list

        :return: A list of observed dates in the form of [yyyymmdd ... yyyymmdd]
        :rtype: list
        """
        memory = []
        observed_dates = []
        for census_year, date in grouped_census_dates:
            if census_year not in memory:
                memory.append(census_year)
                observed_dates.append(max([match_date for match_year, match_date in grouped_census_dates
                                           if match_year == census_year]))

        return observed_dates

    def _set_shapefile_years(self, adjust_dates, place_over_time):
        """
        Set the shapefile dates based on the number of keys that exist for a given place_over_time in self.weights

        :param adjust_dates: If we need to adjust the dates by a set amount, concatenate this to the dates found
        :param place_over_time: The current place
        :return: List of dates to search between
        """
        if adjust_dates:
            return [int(date + adjust_dates) for date in list(self._weights[place_over_time].keys())]
        else:
            return [int(date) for date in list(self._weights[place_over_time].keys())]

    def _assigned_dates_to_weights(self, place_over_time, dates_observed, shapefile_years):
        """
        This assigns the date to the change that has been observed in the shapefile.

        Example
        -------
        | For a given shape that represents a region, lets call it Otley, we have 4 census year shapefiles we observe
         in 1931, 1951, 1961 and 1971. We want to weight on 1951 so we take that year as our reference and apply this to
         the other years and we get the following weights based on our reference in 1951:
        |
        | A [01, "OTLEY_UD", [01, "OTLEY_UD", 60, 60], [00, "AIREDALE_RD", 20, 50]
        | B [01, "OTLEY_UD", [01, "OTLEY_UD", 100, 100]"
        | C [01, "OTLEY_UD", [01, "OTLEY_UD", 90, 78], [02, "BRADFORD_CB, 10.2, 1.4]"
        | D [01, "OTLEY_UD", [01, "OTLEY_UD", 70, 40], [02, "BRADFORD_CB, 15, 3]"
        |
        | Now by loading in our dates file we know that changes to OTLEY's structure occurred in 1934, 56, 62 and 65.
         However, we can only observe the last change that occurs within a shapefile, as constructed by
         construct_observed_dates, so only 1934, 56, and 65 will be used. Regardless of which reference year is chosen,
         the system works chronologically for this process.
        |
        | The first Census year is 1931, given it is not our reference year it does not need to be 100% weight, and as
         such the weight for our 1951 shape in 1931 can be of multiple places. The weight we observe in this case is
         the weight before any changes have occurred as its the first observable date in our sample. As such it is
         always loaded by taking index = 0 and setting the 'change' date to the first census year.
        |
        | From this point forth changes may have occurred. The 1934 change is the last change that occurs between the
         1931 shapefile and the 1951 shapefile. So the weights we observe in 1951, are the reflection of the change that
         occurred in 1934. By searching dates with index-1, we are isolating the 1931, with index calling 1951.So we use
         index to then parse the correct observed weights from our place_over_time to this date.
        |
        | This then continues. So in this case B's weight is applied to the date of 1934, C's weight to 1956 and D's
         weight to 1965; as we cannot observe the change that occurs in 1962. The constructed weight for our reference
         shape is therefore going to take the form of the following
        |
        | [01, "OTLEY_UD", [19310401, [01, "OTLEY_UD", 60, 60], [00, "AIREDALE_RD", 20, 50]]...[date_of_change,
          [WeightA, WeightB]]

        Parameters
        ----------
        :param dates_observed: The dates that we observed for this place
        :type dates_observed: list

        :param place_over_time: The current Places weight changes from census years
        :type place_over_time: list

        :return: A list for all the weights changes that occur to a given place by the date of which the change occurs
            in the form of list[date1[gid, district_name, area_weight, pop_weight]... dateN[gid, district_name,
             area_weight, pop_weight]]
        :rtype: list
        """
        weights_by_date = []
        for index, values in enumerate(self._weights[place_over_time].values()):
            if index == 0:
                weights_by_date.append([min(shapefile_years)] + [[[v, values[v][self._weight_key]] for v in values]])
            else:
                for date in dates_observed:
                    if shapefile_years[index - 1] < date <= shapefile_years[index]:
                        weights_by_date.append([date] + [[[v, values[v][self._weight_key]] for v in values]])

        return weights_by_date

    @staticmethod
    def _setup(working_directory, weights_path, population_weights, dates_path):
        """
        Validate paths, load files, and set weight key nad date indexes
        """

        assert Path(working_directory).exists(), f"Working Directory invalid"

        # Validate dates and load the csv
        assert Path(dates_path).exists(), "Dates path invalid"
        dates = CsvObject(dates_path)
        date_indexes = [index for index, head in enumerate(dates.headers) if "Changes" in head]

        # Validate weights path and load the json
        weights_path = Path(weights_path)
        assert weights_path.exists()
        weights = load_json(weights_path)

        # Determine the population key based on the type specified
        if population_weights:
            weight_key = "Population"
        else:
            weight_key = "Area"

        return working_directory, weights, weight_key, dates, date_indexes
