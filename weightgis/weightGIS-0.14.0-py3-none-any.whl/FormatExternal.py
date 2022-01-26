from miscSupports import directory_iterator, find_duplicates, chunk_list, write_json, load_json, validate_path, \
    invert_dates, flatten, parse_as_numeric
from csvObject import CsvObject, write_csv
from multiprocessing import Process
from collections import Counter
from pathlib import Path
import numpy as np
import re


class FormatExternal:
    def __init__(self, place_reference, data_name, correction_path=None, cpu_cores=1, splitter="__", name_index=0,
                 place_map=None):
        # Set the standardised name reference from a path to its csv
        self._reference = CsvObject(validate_path(place_reference), set_columns=True)

        # The name for this particular sub set of data
        self._data_name = data_name

        # Number of cores to use for multi-core enabled methods
        self._cpu_cores = cpu_cores

        # Match lists to standardise names to, set the number of match types, -1 is from removing GID
        self._matcher, self._reference_types, self.isolates = self._construct_match_list()
        self._gid, self._did, self._cid = self.isolates
        self._match_types = len(self._matcher[0]) - 1

        # If there is a correction file, validate it exists, then load it; else None.
        if correction_path:
            self._corrections = self._set_corrections(correction_path)
        else:
            self._corrections = None

        # How to break names into chunks and the column index of names in the reformatted data
        self._splitter = splitter
        self._name_index = name_index

        if place_map:
            # If names need to be remapped then assert there are as many maps as places in the matcher
            assert self._match_types == len(place_map)
            self.order = place_map
        else:
            # Otherwise set the place_map to be just an ordered list of ints of range equal to the place types
            self.order = [i for i in range(len(self._matcher[0]) - 1)]

    def _construct_match_list(self):
        """
        Take the relations provided in the place reference and construct lists of matches for each place type to match
        names against

        :return: A list of lists, where sub lists contain the gid of the place, and then sub lists of strings for each
            place type
        """

        # Isolate the place types within the reference file
        reference_types = [header for header in self._reference.headers
                           if "GID" not in header and not self._has_numbers(header)]

        # Set the indexes for each area
        type_indexes = [[index for index, header in enumerate(self._reference.headers) if area in header]
                        for area in reference_types]

        # Construct validation lookup
        validation = []
        for place in self._reference.row_data:
            validation.append([place[0]] + [self._place_type_names(place, place_type) for place_type in type_indexes])

        # Isolate the min values for each category
        isolates = [self._reference.headers.index("GID")] + [min(i) for i in type_indexes]
        return validation, ["GID"] + reference_types, isolates

    @staticmethod
    def _has_numbers(string):
        """
        Check to see if the string as a digit within it

        Source: https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
        """
        return any(char.isdigit() for char in string)

    def _place_type_names(self, place, indexes):
        """
        Isolates all the valid names for this place type

        :param place: The current place we want to find equivalent names for
        :type place: str

        :param indexes: A list of indexes that represents the columns to isolate for this row that are valid for this
            place type
        :type indexes: list

        :return: A list of all the valid places for this type
        :rtype: list
        """
        return [self._simplify_string(place[i]) for i in range(min(indexes), max(indexes) + 1) if place[i] != ""]

    @staticmethod
    def _simplify_string(string_to_simplify):
        """
        strip a string of all non alphanumeric characters, white space, as well as underscore

        :param string_to_simplify: String to simplify
        :type string_to_simplify: str

        :return: String stripped of all non alphanumeric characters, white space and underscores
        :rtype: str
        """
        # This seems rather specific?
        string_to_simplify = string_to_simplify.replace("&", "and")
        return re.sub(r"[\W_\s]", "", string_to_simplify).lower()

    def _set_corrections(self, correction_path):
        """
        Set the correction list for changing names after reformatting

        This is designed to change names when names occur via spelling mistakes in the original source material. You
        could clean these in the reformatting stage, but if you have multiple dataset's where the spelling errors occur
        but the formatting is different then this allows for a standardised approach to fixing the error.

        :param correction_path: A path to the correction file, which contains as many rows as twice the number of types,
            + 1 for the operator column.
        :type correction_path: str | Path

        :return: A list of length match_type + 1, where the addtional is from the operator column so we know to delete
            or replace a value.
        """

        # Load the data into memory
        correction_data = CsvObject(validate_path(correction_path))

        # Assert there are as many rows as twice the number of types, + 1 for the operator column
        assert (self._match_types * 2) + 1 == correction_data.row_length

        # Create the original, correction rows
        original_i, new_i = [[i * self._match_types, (i * self._match_types) + self._match_types] for i in range(2)]

        correction_list = []
        for row in correction_data.row_data:
            # Isolate the original names and the replacements
            originals = [self._simplify_string(name) for name in row[original_i[0]:original_i[1]]]
            corrections = [self._simplify_string(name) for name in row[new_i[0]:new_i[1]]]

            # Append this to a list with the operator column; the last one hence -1
            correction_list.append([originals, corrections, row[-1]])

        return correction_list

    # TODO: I think raw-name conversion is bascially just a better standardise names, we need to standardise these
    #  methods with the aim of keeping standardise_names. HOWEVER: we need the name splitting in standardise names!
    def standardise_names(self, data_directory, write_directory):
        """
        Standardise each place name to a single name if it has multiple

        If working with time series data places may change their names over time which can lead to a lot of merge errors
        or difficulty in linking data. This will standardise all names to a single entry, ensuring that regardless of
        the actual name of the place in that year that all data from that place is grouped to a single entry.

        :param data_directory: Directory containing csv files named in a yyyymmdd format
        :type data_directory: Path | str

        :param write_directory: Output directory
        :type write_directory: Path | str

        :return: Nothing, write out the data for each file found in the data_directory and then stop
        :rtype: None
        """
        for file in directory_iterator(data_directory):
            print(file)

            # Load the data into memory.
            data = CsvObject(Path(data_directory, file), set_columns=True)

            # Standardise the name via the matcher
            rows = []
            for i, name in enumerate(data.column_data[self._name_index], 0):
                reformatted = self._convert_names(name, i, data)
                if reformatted:
                    rows.append(reformatted)

            # Set the headers of the output file then write the file of the same name to the write_directory
            headers = self._reference_types + data.headers[1:]
            write_csv(write_directory, data.file_path.stem, headers, rows)

    def _convert_names(self, name, index, data):
        """
        Convert a name to a standardised representation from _matcher loaded via a PlaceReference output file

        Names may not be standardised over time. Names are stored in the reformatted file with a _splitter separating
        the geo-levels. The names are split, stripped of all non-characters and set to be lower case. The names are
        then correct for spelling or deletion requests if required via _corrections. If the data is not deleted, we then
        look to match the name to our reference. If we do so successfully, then the name is merged with the row_data and
        then return; otherwise a IndexError from _match_to_reference will be raised.

        :param name: Current place name
        :type name: str

        :param index: Current row index for parsing out the row_data
        :type index: int

        :param data: The csvObject of the current file
        :type data: CsvObject

        :return: The row's standardised names with GID and the row_data in a list
        :rtype: list
        """
        # Split the names on the _splitter and order them based on the original order or that provided by the user.
        ordered_names = np.array(name.split(self._splitter))[self.order].tolist()

        # Simplify each name
        simplified = [self._simplify_string(name) for name in ordered_names]

        # Isolate the row data for this file
        row_data = [row for i, row in enumerate(data.row_data[index]) if i != self._name_index]

        # Correct the names if required
        place_names = self._correct_data(simplified)
        if place_names:
            # If we are not deleting the row, standardise the names
            return self._match_to_reference(place_names) + row_data
        else:
            return None

    def _correct_data(self, simplified):
        """
        Correct or delete the names if required

        If corrections are required, validate that the name is not within the correction list. If it is and it's flag
        is set to FALSE, then accept the correction name. If it is match to the corrections but the FLAG is not FALSE
        (Ideally set to TRUE) then it will return None and this entry will not be brought across.

        :param simplified: Simplified names
        :type simplified: list

        :return: The original names if corrections are not set, or if the current names where not matched. If matched
            and flag of FALSE it returns the correction names from the correction file. Otherwise None
        :rtype: list | None
        """
        if self._corrections:
            for errors, corrections, flag in self._corrections:
                if simplified == errors:
                    if flag == "FALSE":
                        return corrections
                    else:
                        return None

            return simplified
        else:
            return simplified

    def _match_to_reference(self, place_names):
        """
        Match the place to a PlaceReference from _matcher.

        This will iterate though each row in the matcher until it finds a match for all place types and then return the
        first element of the reference as the standardised name. Raises and IndexError if it fails.

        :param place_names: The simplified and corrected place names for this place
        :type place_names: list

        :return: The standardised place names for this place
        :rtype: list

        :raises IndexError: If the place names are not successfully matched.
        """
        for row in self._matcher:

            # See if we can match each place type to a a group in an a given row in the matcher.
            checked_row = [True if match in match_group else False for match, match_group in zip(place_names, row[1:])]

            # If all are true, isolate the first element as the standardised name.
            if all(checked_row):
                return self._set_standardised_place(row)

        # If we fail raise an index error
        raise IndexError(f"{place_names} was not matched. Please update your Place Reference file accordingly.")

    @staticmethod
    def _set_standardised_place(place_groups):
        """Extract the GID from the first entry, and the first name of each group for all others"""
        return [place if i == 0 else place[0] for i, place in enumerate(place_groups)]

    def solve_ambiguity(self, standardised_directory, write_directory):
        """
        Remove perfect duplicates and combine non perfect duplicates so that all GIDs are unique.

        Some places may end up being duplicated, in the raw data or after standardisation. This method will remove
        perfect duplicates, and combine non perfect duplicates into a single entry. Keep in mind, that if this is not
        desirable, that the system will print out each non-perfect duplication merge it has done. You may wish to alter
        your original data set, or change your place reference to avoid this from happening.

        :param standardised_directory: The data directory of the output from standardise_names
        :type standardised_directory: str | Path

        :param write_directory: The output directory
        :type write_directory: str | Path
        """
        for file in directory_iterator(standardised_directory):
            print(file)

            # Load the original file and look for duplicate GIDs; which should be unique
            data = CsvObject(Path(standardised_directory, file), set_columns=True)
            duplicate_list = find_duplicates(data.column_data[0])

            # Isolate any row that does not suffer from duplication as the base of the write return
            reset_row = [row for row in data.row_data if row[0] not in duplicate_list]

            for dup in duplicate_list:
                # Isolate the row names
                row_names = data.row_data[data.column_data[0].index(dup)][:len(self._reference_types)]

                # Isolate the values for each duplicate name
                sub_list = [[parse_as_numeric(rr, float) for rr in r[len(self._reference_types):]]
                            for r in data.row_data if dup == r[0]]

                # Isolate unique lists, to remove duplicates
                unique_sub_lists = [list(x) for x in set(tuple(x) for x in sub_list)]

                # Warn the user that some values have been combined.
                if len(unique_sub_lists) > 1:
                    print(f"Found and combined multiple entries that where not perfect duplicates for {row_names}")

                # Add the combined values or singular entry of duplicate values to the reset list
                reset_row.append(row_names + [sum(i) for i in zip(*unique_sub_lists)])

            write_csv(write_directory, data.file_path.stem, data.headers, reset_row)

    def relational_database(self, cleaned_directory, write_directory):
        """
        Create a json file for place that contains all the information across time from the standardised data via sub
        processing to speed up the process. Loads the names from the PlaceReference file set to _matcher

        At present we have multiple files, one file for each entry of data. This method will standardise all the data
        from a given place into a single dict so that we can easily combine multiple dataset's.

        Note
        ----
        This is normally quite a slow process, hence allow for multi-core functionality, but also it will NOT over-write
        files. This is so you can fix smaller areas and not have to regenerate the whole list. Keep in mind therefore
        that if you do wish to re-run the program you will need an empty write_directory.

        :param cleaned_directory: The files that have been standardised and then checked for ambiguity
        :type cleaned_directory: Path | str

        :param write_directory: The output directory
        :type write_directory: Path | str

        :return: Nothing, write each json file out and then stop
        :rtype: None
        """

        chunked = chunk_list([i for i in range(len(self._matcher))], int(len(self._matcher) / self._cpu_cores))
        processes = [Process(target=self.relational_subprocess,
                             args=(index_list, index, cleaned_directory, write_directory))
                     for index, index_list in enumerate(chunked, 1)]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def relational_subprocess(self, index_list, index_of_process, data_directory, write_directory):
        """
        This sub process is run via a call from relational_database via Process

        Each process is set a sub selection of indexes from the PlaceReference loaded into _matcher. Each process will
        then isolate this name and create a output json database for it by extracting any matching entries attributes
        from the data directory.

        :param index_list: A list of indexes to load from the PlaceReference for this process
        :type index_list: list[int]

        :param index_of_process: Which process thread this is
        :type index_of_process: int

        :param data_directory: Load directory the of standardised, cleaned, and correct data
        :type data_directory: str | Path

        :param write_directory: Write Directory for the json database
        :type write_directory: str | Path

        :return: Nothing, write a json database for each location that has been indexed from the PlaceReference.
        :rtype: None
        """

        # Currently processed files in the output directory
        current_files = [f for f in directory_iterator(write_directory)]

        for call_index, place_index in enumerate(index_list, 1):
            print(f"{call_index} / {len(index_list)} for process {index_of_process}")

            # Create the unique name from the groups and isolate the gid for parsing the csv
            unique_name = "__".join(self._set_standardised_place(self._matcher[place_index]))
            gid = self._matcher[place_index][0]

            # Set the output stub for this place's json database
            place_data = {"Place_Name": unique_name, "GID": gid}

            # If the data has not already been processed
            if self._not_processed(unique_name, current_files):
                for file in directory_iterator(data_directory):

                    # Load the data into memory
                    data = CsvObject(Path(data_directory, file), set_columns=True)

                    # Isolate any data pertaining to this place from this file and add them to the place_data dict
                    self._process_relation_data(data, gid, place_data)

                write_json(place_data, write_directory, f"{unique_name}_{self._data_name}")

    def _not_processed(self, unique_name, current_files):
        """
        If a file doesn't exist, then we want to process it.
        """
        if f"{unique_name}_{self._data_name}.txt" not in current_files:
            return True
        else:
            print(f"Already processed {unique_name}")

    def _process_relation_data(self, data, gid, place_data):
        """
        Set the attribute values to the date of this file's data.

        Each place should now be unique after going through the cleaning procedures. This isolates all the headers that
        are not places, and if they are not already, sets them as attributes to out json place_data dict. The values
        are then set in a date: value dict per attribute, where the date is isolated from the data's filename.

        :param data: A CsvObject of the current file's data
        :type data: CsvObject

        :param gid: The unique number for this location

        :param place_data: Output json data dict
        :type place_data: dict

        :return: Nothing, update the json data dict's attributes then stop or do not process if the place is not present
        :rtype: None

        :raises KeyError: If the gid is not unique
        """

        # Isolate the non place name headers to be used as attribute keys
        header_keys = data.headers[len(self._reference_types):]

        # Count the occurrences of the GID
        gid_count = data.column_data[0].count(gid)

        # If it happens more than once, raise an KeyError as it should be unique
        if gid_count > 1:
            raise KeyError(f"ERROR: {gid} found twice in {data.file_name}")

        # If it is less than 1 then return none and stop, this place doesn't exist at this point in time
        elif gid_count < 1:
            return None

        # Otherwise extract the data for this place.
        else:
            # Add headers to the place data dict if it does not already exist
            for header in header_keys:
                if header not in place_data:
                    place_data[header] = {}

            # Isolate the data from this file relating to this GID
            row_isolate = data.row_data[(data.column_data[0].index(gid))][len(self._reference_types):]

            # Update the attributes, assigning them as floats if possible.
            for attribute, value in zip(header_keys, row_isolate):
                try:
                    place_data[attribute][int(data.file_path.stem)] = float(value)
                except ValueError:
                    place_data[attribute][int(data.file_path.stem)] = value

    def combine_dataset(self, path_list, write_directory, database_name):
        """
        This will combine all the dataset's you have made into a single json database

        This will combine all the regional data from all standardised dataset's into a single json database. If you only
        had 1 database to begin with, then this just adds all the separate json databases into a single 1. Where it is
        mostly used, is when you have run this process on multiple dataset's and now want all the standardised places to
        share attribute data in a single database.

        :param path_list: A list of paths, where each path goes to a set directory
        :type path_list: list[str | Path]

        :param write_directory: The write directory of the master database
        :type write_directory: str | Path

        :param database_name: The master database name
        :type database_name: str

        :return: Nothing, write the database to file then stop
        :rtype: None
        """

        # Initialise the output database
        master_database = {}

        # Isolate all the paths to all the files we want to load across all the database for this geo-level
        level_data = [Path(path, file) for path in path_list for file in directory_iterator(path)]

        for index, file in enumerate(level_data):
            if index % 100 == 0:
                print(f"{index}/{len(level_data)}")

            # Load the data for this file into memory, set the master database assign name via Place_Name
            load_data = load_json(file)
            assign_name = load_data["Place_Name"]

            # If the current attribute does not exist within the current database, add it to it
            current_attributes = self._current_attributes(master_database, assign_name)
            for attr in load_data.keys():
                if attr not in current_attributes:
                    master_database[assign_name][attr] = load_data[attr]

        write_json(master_database, write_directory, database_name)

    @staticmethod
    def _current_attributes(master_database, assign_name):
        """
        Return all the attributes for the current place if it exists in the master database, otherwise return an empty
        dict and set the mater database to contain an entry equal to the name.
        """
        try:
            return [attr for attr in master_database[assign_name]]
        except KeyError:
            master_database[assign_name] = {}
            return []

    def places_into_dates(self, cleaned_data, write_directory, file_gid=0):
        """
        Sometimes you may have data that is not missing in dates, but just wasn't recorded. This places every place in
        into ever date.
        """

        # Format the reference into lower case
        formatted = [[r.lower() for r in row] for row in self._reference.row_data]

        for file in directory_iterator(cleaned_data):
            # Load the file as a csv object
            loaded_file = CsvObject(Path(cleaned_data, file))

            # Isolate the GID: Row relation from the file
            gid = {row[file_gid]: row for row in loaded_file.row_data}

            # If the place exists in our file, use the file row, else use set to zero's
            all_places = []
            for row in formatted:
                if row[file_gid] in gid:
                    all_places.append(gid[row[file_gid]])
                else:
                    all_places.append([row[i] for i in self.isolates] + [0, 0, 0, 0])

            write_csv(write_directory, Path(cleaned_data, file).stem, loaded_file.headers, all_places)

    def reformat_raw_names(self, raw_csv, raw_name_i, date_i, data_start, out_directory, date_type="yyyymmdd",
                           date_delimiter="/"):
        """
        This will attempt to reformat names that are in a different style to the required weightGIS format

        :param raw_csv: The path of the csv of data you want to standardise
        :type raw_csv: Path | str

        :param raw_name_i: The place name index in the raw file
        :type raw_name_i: int

        :param date_i: The date index in the raw file
        :type date_i: int

        :param data_start: The column index wherein after the data starts
        :type data_start: int

        :param out_directory: Where you want this file to be written to
        :type out_directory: str | Path

        :param date_type: The type of date, takes the values of yyyy, yyyymmdd, or ddmmyyyy.
        :type date_type: str

        :param date_delimiter: Delimiter for if dates are standard dd/mm/yyyy
        :type date_delimiter: str

        :return:
        """

        raw_csv = CsvObject(raw_csv, set_columns=True)
        headers = ["Place"] + raw_csv.headers[data_start:]

        place_dict = self._create_place_dict(raw_csv, raw_name_i)

        unique_dates = self._set_name_dates(date_delimiter, date_i, date_type, raw_csv)

        for row_date, date in unique_dates.items():
            place_rows = []
            for row in raw_csv.row_data:
                if row[date_i] == row_date:
                    place_rows.append([place_dict[self._simplify_string(row[raw_name_i])]] + row[data_start:])

            write_csv(out_directory, date, headers, place_rows)

    def _create_place_dict(self, raw_csv, name_i):
        """
        Names from the town level data are not linkable to districts, attempt to do so via this method.
        """

        # Isolate unique names and simplify them for matching
        unique_names = sorted(list(set(raw_csv[name_i])))
        search_names = [self._simplify_string(name) for name in self._reference[1]]

        place_dict = {}
        for place in unique_names:

            # Create a simplified reference of this place
            place = self._simplify_string(place)

            # Search for the place name in the search names
            place_names = [name for name in search_names if place == name]

            # If we fail to find a single name
            if len(place_names) < 1 or len(place_names) > 1:

                # Try to find a unique name from alternatives
                place_reformatted = self._search_alternate(place)

                # If we fail
                if not place_reformatted:
                    # Try to load a correction from the yaml file
                    try:
                        # Create a place_reformatted if not flagged for deletion
                        corrected_place = self._attempt_correction(place)
                        if not corrected_place:
                            continue
                        else:
                            place_reformatted = self._search_alternate(corrected_place)
                            if not place_reformatted:
                                raise IndexError(f"Failed to find {place}")

                    # Otherwise push failed name to terminal
                    except (KeyError, TypeError):
                        raise KeyError(F"No correction for unknown {place}")

            # If we do find a unique name, isolate the gid, district, county
            else:
                data_row = self._reference.row_data[search_names.index(place_names[0])]
                place_reformatted = f"{data_row[self._cid]}__{data_row[self._did]}"

            place_dict[place] = place_reformatted

        return place_dict

    def _search_alternate(self, place):
        """If we fail to identify a single name, look for alternative names"""
        for row in self._reference.row_data:
            for name in row:
                name = self._simplify_string(name)
                if place in name:
                    return f"{row[self._cid]}__{row[self._did]}"

    def _attempt_correction(self, place):
        """
        If we have failed to find the name, then it may be that this name requires correcting first. This iterates
        though looking for corrections on the first name and then returns the correction if the flag is not set to
        True, which indicates a deletion.

        :param place: Correct place we failed to find
        :type place: str

        :return: A correction if we found it and it was not set to be deleted, else None
        :rtype: str | None

        :raises IndexError: If the place was not found
        """

        for (error_district, error_county), (correction_district, correction_county), flag in self._corrections:
            if place == error_district:
                if flag == "FALSE":
                    return correction_district
                else:
                    return None

        raise IndexError(f"Failed to Find a correction for {place}")

    @staticmethod
    def _set_name_dates(date_delimiter, date_i, date_type, raw_csv):
        """
        This will attempt to standardise the date column into a yyyymmdd date

        :param date_delimiter: Delimiter for if dates are standard dd/mm/yyyy
        :type date_delimiter: str

        :param date_i: Index for the date in the raw data
        :type date_i: int

        :param date_type: The type of date, takes the values of yyyy, yyyymmdd, or ddmmyyyy.
        :type date_type: str

        :param raw_csv: The raw csv
        :type raw_csv: CsvObject

        :return: A dict of {row date name: yyyymmdd}
        :rtype: dict

        :raises TypeError: If a value other than yyyy, yyyymmdd, or ddmmyyyy is passed to date_type
        """
        # todo: delimitor is abatory, needs delimiting first and only if set rather than ddmmyyyy being the only delimit
        unique_dates = sorted(list(set([row[date_i] for row in raw_csv.row_data])))
        if date_type == "yyyy":
            return {date: f"{date}1231" for date in unique_dates}
        elif date_type == "yyyymmdd":
            return {date: date for date in unique_dates}
        elif date_type == "ddmmyyyy":
            return {date: inv for date, inv in zip(unique_dates, invert_dates(unique_dates, date_delimiter))}
        else:
            raise TypeError(f"Expected yyyy, yyyymmdd, or ddmmyyyy yet was passed {date_type}")

    @staticmethod
    def remove_duplicates(raw_csv, write_directory):
        """
        Sometimes we may have known duplicates in a file which does not link to ambiguity, in this case we can just
        purge the duplicates and re-write the file

        :param raw_csv: The csv with potential duplicates within them
        :type raw_csv: str | Path

        :param write_directory: The output directory for the file
        :type write_directory: Path | str

        :return: Nothing, write file then stop
        :rtype: None
        """

        csv_obj = CsvObject(validate_path(raw_csv))
        unique_values = [list(v) for v in list(Counter([tuple(r) for r in csv_obj.row_data]).keys())]
        write_csv(write_directory, csv_obj.file_path.stem, csv_obj.headers, unique_values)

    def combine(self, unique_id, data_start, root_directory, write_directory, write_name):
        """
        weightGIS expects each file to have a single date, so if you have lots of files of the same date that you wan
        to process at the same time you will need ot combine them

        :param unique_id: The unique id index
        :type unique_id: int

        :param data_start: The index wherein the data starts from
        :type data_start: int

        :param root_directory: The root directory of the csv files
        :type root_directory: Path | str

        :param write_directory: The output directory for the file
        :type write_directory: Path | str

        :param write_name: Name of the combined file
        :type write_name: str

        :return: Nothing, write file then stop
        :rtype: None
        """

        # Create the unique ID's
        unique_id_list = sorted(list(set(flatten([CsvObject(Path(root_directory, file), set_columns=True)[unique_id]
                                                 for file in directory_iterator(root_directory)]))))

        # For each unique ID
        out_list = []
        for count_i, ids in enumerate(unique_id_list):

            if count_i % 10 == 0:
                print(f"{count_i} / {len(unique_id_list)}")

            # Check each file for a matching row, and then
            ids_list = []
            for index, file in enumerate(directory_iterator(root_directory)):

                # If its the first index, take the full values
                if index == 0:
                    ids_list += self._isolate(root_directory, file, unique_id, ids)

                # Otherwise only take the values after the data start
                else:
                    ids_list += self._isolate(root_directory, file, unique_id, ids)[data_start:]

            out_list.append(ids_list)

        headers = []
        for index, file in enumerate(directory_iterator(root_directory)):
            if index == 0:
                headers += CsvObject(Path(root_directory, file)).headers
            else:
                headers += CsvObject(Path(root_directory, file)).headers[data_start:]

        write_csv(write_directory, write_name, headers, out_list)

    @staticmethod
    def _isolate(root_directory, file, unique_id, ids):
        """
        Isolate the row that match's the ID if it exists, else return an empty list

        Note
        ----
        This assumes no duplicates, and if you have duplicates where the values are different you will need to clean
        that yourself. Otherwise, run the remove_duplicates command first before this method.

        :param root_directory: The root directory of the csv files
        :type root_directory: Path | str

        :param file: The name of the file to search
        :type file: str

        :param unique_id: The unique id index
        :type unique_id: int

        :param ids: The current match id
        :type ids: str

        :return: The row in the data that was matched if it was found, else an empty list of length CsvObject
        :rtype: list
        """

        csv_obj = CsvObject(Path(root_directory, file))

        for row in csv_obj.row_data:
            if row[unique_id] == ids:
                return row
        return ["" for _ in range(csv_obj.row_length)]
