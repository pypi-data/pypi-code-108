from csvObject import CsvObject, write_csv
from shapeObject import ShapeObject
from shapely.geometry import Point
from pathlib import Path


class IDLocate:
    def __init__(self, id_path, shapefile_path, write_directory, write_name, east_i=1, north_i=2, shape_match_i=0):
        """
        This will assist you locating individuals

        :param id_path: The path to a csv file filled with id's with a eastings and northings
        :type id_path: Path | str

        :param shapefile_path: path to the shapefile relevent to the operation you want to use
        :type shapefile_path: Path | str

        :param east_i: Index of the eastings in the id data
        :type east_i: int

        :param north_i: Index of the northings in the id data
        :type north_i: int

        :param shape_match_i: Index of the mating parameter, should be common in both geo reference and shapefile
        :type shape_match_i: int

        :param write_directory: Saved file will be writen here
        :type write_name: Path | str

        :param write_name: The name of the file to write
        :type write_name: str
        """

        # TODO: Validate write directory exists!

        self.id_file = CsvObject(id_path)
        self.shapefile = ShapeObject(shapefile_path)
        self.east_i = east_i
        self.north_i = north_i
        self.shape_match_index = shape_match_i
        self.write_directory = write_directory
        self.write_name = write_name

    def geo_ref_locate_individuals(self, geo_lookup):
        """
        This will assist you locating individuals with a geo lookup, so a single low level shapefile can identify all
        levels within a single loop

        :param geo_lookup: The path to the geo lookup
        :type geo_lookup: Path | str

        :return: Nothing, write the file then stop
        :rtype: None
        """
        geo_file = CsvObject(geo_lookup)

        # Create an id: all other rows lookup so we can identify each location from the lowest
        geo_lookup = {row[self.shape_match_index]: row for row in geo_file.row_data}

        # Link all the geometry
        geo_link = self._create_geo_link(geo_file, geo_lookup)

        # create the headers for the file, then write the located out
        headers = [h for i, h in enumerate(self.id_file.headers) if i not in (self.east_i, self.north_i)] + \
            geo_file.headers
        self._write_located(geo_link, headers)

    def _create_geo_link(self, geo_file, geo_lookup):
        """
        This will iterate each unique place, and determine where the point is within the lowest level shapefile.
        Then it will link this shapefile's `shape_match_index` within the geo lookup so that all layers that are
        associate with this unique place are linked at once

        :param geo_file: The csv file for the geo lookup, used to determine row length of failed
        :type geo_file: CsvObject

        :param geo_lookup: The GID: Geographic lookup row dict
        :type geo_lookup: dict

        :return: A dict of easting__northing: geo row to be used to match to individuals
        :rtype: dict
        """

        # Construct a unique list of places, to avoid duplicate in searchers
        unique_places = self._unique_places()

        geo_link = {}
        # Determine the location of each place
        for index, coordinate in enumerate(unique_places):
            if index % 100 == 0:
                print(f"{index + 1}/{len(unique_places)}")

            # Isolate the two coordinates
            east, north = coordinate.split("__")

            if len(east) == 0 or len(north) == 0:
                geo_link[coordinate] = ["No or invalid coordinates" for _ in range(geo_file.row_length)]
            else:
                point = Point(float(east), float(north))

                location_id = self._point_identification(point)
                try:
                    geo_link[coordinate] = geo_lookup[location_id]
                except KeyError:
                    print(f"Failed to find {location_id}")
                    geo_link[coordinate] = ["ID not found in geolookup" for _ in range(geo_file.row_length)]

        return geo_link

    def _unique_places(self):
        """Isolate the unique places within the id file"""
        return sorted(list(set([f"{ids[self.east_i]}__{ids[self.north_i]}" for ids in self.id_file.row_data])))

    def _point_identification(self, point):
        """
        Located the point within the shapefile

        :param point: A shapely Point from the eastings and northings
        :type point: Point

        :return: A match record from the shapefile that was returned
        :rtype:
        """
        for shape, record in zip(self.shapefile.polygons, self.shapefile.records):
            if shape.contains(point):
                return str(record[self.shape_match_index])

        # If we fail to find the location within, create a list of all the distances
        lowest_list = [[point.distance(shape), record[self.shape_match_index]] for shape, record in zip(
            self.shapefile.polygons, self.shapefile.records)]

        # Return the smallest distance of the sorted list [0] record [1] if we find anything. Else Return str of None
        try:
            return str(sorted(lowest_list)[0][1])
        except KeyError:
            return "None"

    def _write_located(self, geo_link, headers):
        """
        Using the unique linker, write the located individuals to a csv file

        :param headers: Headers of the csv file
        :type headers: list[str]

        :param geo_link: The unique dict of {Unique_place: details of that place}
        :type geo_link: dict

        :return: Nothing, write the file out to the write directory, called write_name, then stop
        :rtype: None
        """
        output_rows = []
        for respondent in self.id_file.row_data:
            # Isolate the rows that are not east/north
            non_location = [r for i, r in enumerate(respondent) if i not in (self.east_i, self.north_i)]

            # Prepend this along with the geo_link birth location
            birth_location = f"{respondent[self.east_i]}__{respondent[self.north_i]}"
            output_rows.append(non_location + geo_link[birth_location])

        write_csv(self.write_directory, self.write_name, headers, output_rows)

    def locate_individuals(self):
        """
        This will locate individuals within a single shapefile

        :return: Nothing, write the file out to the write directory, called write_name, then stop
        :rtype: None
        """
        self._write_located(self._link_unique(), ["ID", "GID"])

    def _link_unique(self):
        """
        For each unique place, this will locate where this point is with the shapefile if it exists, else sets entry to
        "No or invalidate coordinates"

        :return: A dict of easting__northing: shapefile reference to be used to match to individuals
        :rtype: dict
        """

        # Construct a unique list of places, to avoid duplicate in searchers
        unique_places = self._unique_places()

        geo_link = {}
        # Determine the location of each place
        for index, coordinate in enumerate(unique_places):
            if index % 100 == 0:
                print(f"{index + 1}/{len(unique_places)}")

            # Isolate the two coordinates
            east, north = coordinate.split("__")

            if len(east) == 0 or len(north) == 0:
                geo_link[coordinate] = ["No or invalid coordinates"]
            else:
                point = Point(float(east), float(north))
                geo_link[coordinate] = [self._point_identification(point)]

        return geo_link
