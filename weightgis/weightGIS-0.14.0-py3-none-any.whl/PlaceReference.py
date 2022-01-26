from miscSupports import directory_iterator, flip_list, flatten
from csvObject import CsvObject, write_csv
from shapely.geometry import Polygon
from shapeObject import ShapeObject
from pathlib import Path
import numpy as np
import re

# todo: The Final output should really be a yaml file not a csv that way we don't need to do these strand index level
#  things. 


class PlaceReference:
    def __init__(self, working_directory, base_name, level_names, cut_off=100):
        self._working_dir = working_directory
        self._cut_off = cut_off

        self._base_name = base_name
        self._level_names = level_names
        self._target_length = 2 + len(level_names)
        self._headers = [self._base_name] + self._level_names

    def link_places_across_time(self, lowest_level, other_shapefile_levels, record_indexes, base_gid=0):
        """
        This will link to geo-levels together, files must have a numeric component and each sub_unit must be matched
        with a match-unit file with the same numeric component

        Example
        --------
        District and county shapefiles must have the dates within the names and there must be a matching shapefile for
        each district. So if you have 1931 districts you must have a 1931 county. The actual names doesn't matter as
        long as the dates match. Whilst the defaults column indexes for gid, name and type for districts and name for
        county may work, you should check it against the column indexes you have in your download.

        :param lowest_level: A directory of shapefiles that are of the lowest level in terms of geo-levels
        :type lowest_level: str

        :param other_shapefile_levels: A list of lists, where each sub list is a list of shapefiles at a geo-level
        :type other_shapefile_levels: list[str]

        :param record_indexes: Indexes to slice names out of each level, base must be the first
        :type record_indexes: list[list[int]]

        :param base_gid: The gid index in the base shapefile, defaults to zero
        :type base_gid: int

        :return: Nothing, write the relations and ambiguity file is exists to file then stop.
        :rtype: None.
        """

        # Load the shapefiles, determine we have sufficient names
        base_shapefiles, other_shapefiles = self._setup_shapefiles(lowest_level, other_shapefile_levels)
        assert len(other_shapefiles) == len(self._level_names), f"Not all other shapefiles levels have name provided"

        # Get the name indexes from the list of record_indexes
        base_indexes = record_indexes[0]
        other_level_indexes = record_indexes[1:]

        ambiguous = []
        for base_file in base_shapefiles:
            print(f"\nProcessing {base_file}")

            # Determine the current year for this base unit
            year = re.sub(r"[\D]", "", base_file.file_name)

            # Determine the relations within this base file and set the headers of the output file
            relation_list, headers = self._determine_relations_to_base(
                ambiguous, base_file, base_gid, base_indexes, other_level_indexes, other_shapefiles, year)

            # Extract the base names from the first set of relations
            base_shape_names = [relation[:2] for relation in relation_list[0]]

            # Extract the relation names from all relations, then flip them so they are combined
            relation_names = [[relation[2:] for relation in relation_level] for relation_level in relation_list]
            relation_names = flip_list(relation_names)

            # Join the base names and relations two together then write it out
            relation_data = [base + flatten(relation) for base, relation in zip(base_shape_names, relation_names)]
            write_csv(self._working_dir, f"{year}_relation", ["GID", self._base_name] + headers, relation_data)

        if len(ambiguous) > 0:
            write_csv(self._working_dir, "Ambiguous_Relations", [], ambiguous)
            print(f"Please validate the {len(ambiguous)} ambiguous relations before proceeding by creating a file"
                  f"called 'SetAmbiguous.csv' where there is now only a single relation for each ambiguous link")
        else:
            print("No problems detected, please move to _write_linked_unique next but set ambiguity to False")

    def _setup_shapefiles(self, base_level_shapefiles, other_shapefiles):
        """
        Load all the shapefiles and determine they are of equal length.

        :param base_level_shapefiles: The base level shapefiles, there must be a matching year for each level in other
            shapefiles
        :param other_shapefiles: A list of levels, where each level contains as many shapefiles as base

        :return: The base and other level shapefiles
        """
        base_shapefiles = self._load_shapefiles(base_level_shapefiles)
        if isinstance(other_shapefiles, list):
            other_levels = []
            for level_path in other_shapefiles:
                assert Path(level_path).exists(), f"{level_path} does is invalid"
                other_levels.append(self._load_shapefiles(Path(level_path)))

        elif isinstance(other_shapefiles, str):
            other_levels = [self._load_shapefiles(other_shapefiles)]

        else:
            raise TypeError(f"Other_shapefiles takes list or str but found {type(other_shapefiles)}")
        for level in other_levels:
            assert len(level) == len(base_shapefiles), f"Found {len(level)} other shapefiles for {level} yet " \
                                                       f"expected {len(base_shapefiles)}"
        return base_shapefiles, other_levels

    @staticmethod
    def _load_shapefiles(path):
        """
        Load the shapefiles into memory
        """
        return [ShapeObject(f"{path}/{file}") for file in directory_iterator(path) if Path(path, file).suffix == ".shp"]

    def _determine_relations_to_base(self, ambiguous, base_file, base_gid, base_indexes, level_indexes,
                                     level_shapefiles, year):
        """
        For each level of shapefile use the year to load the shapefile of a given level relevant to the base_file and
        then use this to look for matching relations. Standardise these relations in length, and then return them.

        :param ambiguous: Holder list for ambiguous relations
        :type ambiguous: list

        :param base_file: Base shapefile for the current 'year'
        :type base_file: ShapeObject

        :param base_gid: Index for GID in base shape, defaults to zero in call method
        :type base_gid: int

        :param base_indexes: Indexes for constructing the name from the base shapefile
        :type base_indexes: list[int]

        :param level_indexes: Indexes for constructing names for each level in other shapefiles
        :type level_indexes: list[list[int]]

        :param level_shapefiles: A list levels, where each level contains a list of shapefiles we want to determine
            relations of relative to this 'year'
        :type level_shapefiles: list[list[ShapeObject]]

        :param year: The year we wish to match to our lists of shapefiles to determine which one to load
        :type year: str | int

        :return: A list of standard length relations and the headers for the non base level part of the headers
        :rtype: (list, list)
        """
        relation_list = []
        other_headers = []
        for level, indexes, name in zip(level_shapefiles, level_indexes, self._level_names):
            # Select the match file for this
            match_file = self._set_match_file(level, year)

            # Set a match unit for each sub unit
            level_relations = [self._link_locations(place, rec, match_file, year, base_indexes, base_gid,
                                                    indexes, ambiguous)
                               for place, rec in zip(base_file.polygons, base_file.records)]

            # Set the maximum number of rows so we can make a consistent length row
            relation_max = max([len(relation) for relation in level_relations])

            # Append the max - 2 (because of the GID and base name) number of level names to headers
            other_headers.append([name for _ in range(relation_max - 2)])

            # Reformat the level relations to all be of equal length
            reformat_on_length = []
            for relation in level_relations:
                if len(relation) != level_relations:
                    reformat_on_length.append(relation + ["" for _ in range(relation_max - len(relation))])
                else:
                    reformat_on_length.append(relation)

            relation_list.append(reformat_on_length)
        return relation_list, flatten(other_headers)

    @staticmethod
    def _set_match_file(match_files, year):
        """
        This takes a given list of match files and matches them against the same year of the base shape file. Returns
        the ShapeObject object of the match.

        :param year: The current year
        :type year: str

        :return: Matching county ShapeObject
        :rtype: ShapeObject

        :raises IndexError: If no match is found
        """
        for match in match_files:
            if year == re.sub(r"[\D]", "", match.file_name):
                return match

        raise IndexError(f"Failed to find a match file for {year}")

    def _link_locations(self, place, record, match_file, year, base_indexes, base_gid, level_indexes, ambiguous):
        """

        :param place: The current places shape to match against
        :type place: Polygon

        :param record: The record of the current place we wish to extract a name from via base_indexes
        :type record: list

        :param match_file: The ShapeObject of the level we are looking for overlapping geometry off
        :type match_file: ShapeObject

        :param year: The year that if we find ambiguous relations we write to the first column
        :type year: str | int

        :param base_indexes: The indexes used to set the name of the base shape
        :type base_indexes: list[int]

        :param base_gid: The index of the gid in the base shapefile, defaults to zero in call method
        :type base_gid: int

        :param level_indexes: The indexes used to set the name of the matching geometry
        :type level_indexes: list[int]

        :param ambiguous: Holder list for ambiguous relations
        :type ambiguous: list

        :return: Relations for this current base place shape, prepended with GID and the places name.
        :rtype: list
        """

        # Set the name for the current base place
        base_name = self._set_name(record, base_indexes)

        # Determine relations with the other shapefile that was matched on date
        location_overlaps = self._determine_overlaps(place, match_file, level_indexes)

        # If more than one location was found, updated ambiguous
        if len(location_overlaps) > 1:
            ambiguous.append([year, record[base_gid], base_name] + location_overlaps)
            print(f"Ambiguous Relationship found for {base_name} in {year} for {location_overlaps}")

        # Return the relation information.
        return [record[base_gid], base_name] + location_overlaps

    def _determine_overlaps(self, base_shape, other_shapefile, others_name_indexes):
        """
        A district will be overlapped by a county, but it may have multiple relations which we would need to sort out
        manually. To construct the list of relations and check for ambiguity the system iterates through each polygon
        within a district and sees which county overlaps.

        :param base_shape: The current base shape

        :param other_shapefile: The current level other shapefile ShapeObject
        :type other_shapefile: ShapeObject

        :param others_name_indexes: The indexes of the other shapefiles records to use to construct a name
        :type others_name_indexes: list[int]

        :return: County relationships for this given district
        """
        relationships = []
        for other_shape, rec in zip(other_shapefile.polygons, other_shapefile.records):
            if base_shape.intersection(other_shape).area > self._cut_off:
                if self._set_name(rec, others_name_indexes) not in relationships:
                    relationships.append(self._set_name(rec, others_name_indexes))
        return relationships

    @staticmethod
    def _set_name(record, indexes):
        """Set the name of a place via indexing the records of the shapefile"""
        return "".join([str(rec) for i, rec in enumerate(record) if i in indexes])

    def write_linked_unique(self, ambiguity=True, ambiguity_file_name="SetAmbiguous.csv"):
        """
        Construct a base lookup-file to append alternative names to as well as lists of unique name files

        :param ambiguity: If there is ambiguity in the file system
        :type ambiguity: bool

        :param ambiguity_file_name: The name of the fix file, defaults to SetAmbiguous.csv
        :type ambiguity_file_name: str

        :return: Nothing, construct files then stop
        :rtype: None
        """

        # Load the files for each shapefile that where written by link_districts_counties as well as the user ambiguous
        # file named ambiguity_file_name
        ambiguity_file = self._ambiguity_setter(ambiguity, ambiguity_file_name)
        relation_files = [CsvObject(f"{self._working_dir}/{file}")
                          for file in directory_iterator(self._working_dir) if "_relation" in file]

        # Construct a list of all the names without any ambiguity
        name_list = [self._fix_row_ambiguity(row, ambiguity_file, re.sub(r"[\D]", "", file.file_name))
                     for file in relation_files for row in file.row_data]

        # Write out the reference base
        unique_relations = [list(relation) for relation in list({tuple(i) for i in name_list})]

        if not Path(self._working_dir, "LookupBase.csv").exists():
            write_csv(self._working_dir, "LookupBase", ["GID"] + self._headers, unique_relations)
        else:
            print("Lookup already written, passing")

        # For each level, write out a list of unique names
        for index, level in enumerate(self._headers, 1):

            # Isolate the unique places for a given level
            unique_places = list(set([level_relation[index] for level_relation in name_list]))

            # Write it out if it doesn't already exist
            if not Path(self._working_dir, f"Unique_{level}.csv").exists():
                write_csv(self._working_dir, f"Unique_{level}", [level], unique_places)
            else:
                print(f"Unique_{level} Already exists, skipping")

    def _ambiguity_setter(self, ambiguity, ambiguity_file_name):
        """
        If there is ambiguity, load the fix file
        """
        if ambiguity:
            try:
                return CsvObject(f"{self._working_dir}/{ambiguity_file_name}", file_headers=False)
            except FileNotFoundError:
                raise FileNotFoundError(f"Ambiguity specified but no fix file named {ambiguity_file_name} found")
        else:
            return None

    def _fix_row_ambiguity(self, row, ambiguity_file, year):
        """
        If there is any ambiguity in a row then it will have more than the number of levels, determine by the target
        length. This method matches the ambiguity rows on gid and then returns the row without any ambiguity. If the row
        is does not suffer from ambiguity, return it stripped of blanks.

        :param row: The current row from the relational file
        :type row: list

        :param ambiguity_file: The csvObject loaded ambiguity file
        :type ambiguity_file: CsvObject

        :param year: The year we want to match
        :type year: int | str
        """
        append_row = [r for r in row if r != ""]

        if len(append_row) == self._target_length:
            return append_row
        else:
            ambiguity_row = self._get_ambiguous_row(ambiguity_file, row[0], year)
            if len(ambiguity_row) == self._target_length:
                return ambiguity_row
            else:
                raise IndexError(f"Critical Error: Ambiguity row length is {len(ambiguity_row)} but should be "
                                 f"{self._target_length}")

    @staticmethod
    def _get_ambiguous_row(ambiguity_file, match_gid, year):
        """
        Compare the year and row GID to the rows in the ambiguity file and return the match without the year.

        :param ambiguity_file: The csvObject loaded ambiguity file
        :type ambiguity_file: CsvObject

        :param match_gid: The Gid to search for in the row
        :type match_gid: int | str

        :param year: The year we want to match
        :type year: int | str

        :return: The row with ambiguity and without the year
        :rtype: list

        :raises IndexError: If a GID is not found but required to fix ambiguity
        """
        for row in ambiguity_file.row_data:
            if (match_gid in row) and (year in row):
                return row[1:]

        raise IndexError(f"Failed to find match gid {match_gid} for {ambiguity_file.file_name}")

    def construct_reference(self, base_weights_name="LookupBase.csv", alternative_key="Unique"):
        """
        The construct a reference of every name for every place for every level within the Lookup Base

        :param base_weights_name: Name of the base weights file
        :type base_weights_name: str

        :param alternative_key: Key within files that contains alternative names
        :type alternative_key: str

        :return: Nothing, write out place reference csv then stop
        :rtype: None
        """

        # Load the lookup base
        base_relation = CsvObject(Path(self._working_dir, base_weights_name))

        # Load alternative files
        alt_files = [CsvObject(Path(self._working_dir, file), set_columns=True)
                     for file in directory_iterator(self._working_dir) if alternative_key in file]

        # Order them in the same manner as the headers
        order = [index for header in self._headers for index, file in enumerate(alt_files) if header in file.file_name]
        alt_files = np.array(alt_files)[order].tolist()

        # Link each row to a unique list to create the reference place look up file
        rows = [flatten([[row[0]]] +
                        [self._match_row(match, match_file) for match, match_file in zip(row[1:], alt_files)])
                for row in base_relation.row_data]

        write_csv(self._working_dir, "PlaceReference", ["GID"] + flatten([file.headers for file in alt_files]), rows)

    @staticmethod
    def _match_row(match, match_file):
        """
        Find the match in a row within the match file, then return it
        """
        for match_row in match_file.row_data:
            if match in match_row:
                return match_row

        raise KeyError(f"Failed to find {match}")
