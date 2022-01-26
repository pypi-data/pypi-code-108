from miscSupports import flatten, meters_to_km_miles, terminal_time
from shapeObject import ShapeObject
from csvObject import write_csv
from pathlib import Path


class GeoLookup:
    def __init__(self, base_path, other_shapefiles, record_indexes, headers):

        # Set both the total indexes, and the sub-groups of base and other
        self._indexes = record_indexes
        self.base_index = self._indexes[0]
        self.other_indexes = self._indexes[1:]

        # Load the shapefiles
        self.base, self.others, self.headers = self._setup(base_path, other_shapefiles, headers)

        self._place_data = []

    def construct_lookup(self, write_directory, write_name):
        """
        This will construct a geo-relation csv from a base shapefile relative to a list of other shapefiles based on
        intersection of geometry. For this to work your base shapefile must be the lowest level, otherwise you will end
        up with large levels of ambiguity

        :param write_directory: Where to save this csv
        :param write_name: What to call this csv
        :return: Nothing, write file then stop
        :rtype: None
        """
        for i, (place, record) in enumerate(zip(self.base.polygons, self.base.records)):
            if i % 100 == 0:
                print(f"{i}/{len(self.base.records)}")

            # Set the place records via the first index as well as the area for the lowest order shape
            name_base = self._index_record(record, self.base_index, place)

            # Then do the same for all the other shapes that intersect with this shape
            match_names = [self._find_matches(place, match_shape, indexes)
                           for match_shape, indexes in zip(self.others, self.other_indexes)]

            self._place_data.append(flatten([name_base] + match_names))

        write_csv(write_directory, write_name, self.headers, self._place_data)
        print(f"Constructed GeoRelations {terminal_time()}")

    @staticmethod
    def _index_record(record, indexes, location):
        """
        Isolate the records from a given shapefile using the indexes related to that shapefile and the places area
        """
        return [rec for i, rec in enumerate(record) if i in indexes] + meters_to_km_miles(location.area)

    def _find_matches(self, place, match_shape, indexes):
        """
        If a place finds an intersection with a match place, append the name to the area in a dictionary. Then, assuming
        at least one match is found, return the largest match. If nothing is found, return Failed.
        """
        overlap_dict = {}
        for match, rec in zip(match_shape.polygons, match_shape.records):
            overlap = place.intersection(match).area
            if overlap > 0:
                overlap_dict[overlap] = self._index_record(rec, indexes, match)

        if len(overlap_dict.keys()) > 0:
            return overlap_dict[max(overlap_dict.keys())]
        else:
            # If we fail we need to have the number of index + 2 because of the two area variables produced
            return ["Failed" for _ in range(len(indexes) + 2)]

    def _setup(self, base_path, other_shapefiles, headers):
        """
        Validate all paths to shapefiles are valid and that headers are of a length that equals the number that will be
        produced. From there we then load shapefiles into memory and return base shapefile, the other shapefi
        """

        # Check all shapefiles are valid
        assert Path(base_path).exists(), f"Your base shapefile path of {base_path} is invalid"
        for shapefile_path in other_shapefiles:
            assert Path(shapefile_path).exists(), f"Shapefile at {shapefile_path} is invalid"

        # Check we have enough headers for all our indexes
        assert self._header_len == len(headers), f"{len(headers)} headers provided yet expected {self._header_len}"

        print("Loading Shapefiles into memory...")
        base = ShapeObject(base_path)
        others = [ShapeObject(shapefile_path) for shapefile_path in other_shapefiles]
        return base, others, headers

    @property
    def _header_len(self):
        """Target Length for headers"""
        return len(flatten(self._indexes)) + len(self._indexes) * 2
