from miscSupports import load_json, write_json
from csvObject.csvWriter import write_csv
from pathlib import Path


class AdjustWeights:
    def __init__(self, working_directory, weights_path):
        self._working_dir = working_directory
        self._weights_path = Path(weights_path)
        assert self._weights_path.exists(), "Path to weights is invalid"
        self._weights = load_json(self._weights_path)

    def replace_assigned_weight(self, fixed_json_path, name):
        """
        Find a place within the master dict called 'name' and add dates from the json file of fixed_json_path

        In some situations you may find a complex problem or a mistake and want to replace a given place rather than
        have to - rerun the whole constructor. This allows you to replace a given place by its key in the base_weights
        file you made on all your data, and a new smaller update file. The changes between the update and the master
        will be logged and then the master file will be updated.

        :param fixed_json_path: The path to the json file to load the fixed dates from
        :type fixed_json_path: Path | str

        :param name: The place key in the master _weights to load and replace dates from
        :type name: str
        """
        # Load the fix file
        fixed = load_json(fixed_json_path)

        # Create the restructured values for the named place
        key_list = self._replacement_keys(name, fixed)
        restructured = {str(year): self._replacement_values(fixed, name, year, new) for year, new in key_list}

        # Updating the existing json with the new information
        write_data = self._weights
        write_data[name] = restructured
        write_json(write_data, self._weights_path.parent, self._weights_path.stem)

    def _replacement_keys(self, name, fixed):
        """
        This Creates a true false list of keys, where True means that the values will be taken from then fixed file and
        false from the original

        :param name: The place name that exists in both the master _weights and the fixed file that was loaded
        :type name: str

        :param fixed: The json data that is going to be used to replace values in the master _weights database that has
            been loaded into a dict
        :type fixed: dict

        :return: A list of [weight: bool], to represent if we want to take the old or new weight for this place for each
            date found across both the original and new 'fixed' file. True represents the new fixed file, false the
            original.
        :rtype: list[list[int, bool]]
        """
        # Isolate the weight as a date, represent as an int, for all the weights in the current place in the _weights
        original_weights = [int(key) for key in self._weights[name].keys()]

        # If the date does not exist in the fixed file, keep the original, otherwise set the new value from fixed
        new_weights = [[key, False] for key in original_weights] + \
                      [[new, True] for new in [int(key) for key in fixed[name].keys()] if new not in original_weights]

        # Order the weights on the first element; the dates. Then return
        new_weights.sort(key=lambda x: x[0])
        return new_weights

    def _replacement_values(self, fixed, name, year, new):
        """
        Assign attribute data from the new, or old data based on where the data is.
        """
        if new:
            return fixed[name][str(year)]
        else:
            return self._weights[name][str(year)]

    def remove_weight(self, place, weight_date):
        """
        Remove a weight from a place

        Sometimes you may have a weight assigned that you do not want. For example, if a there is a minor error in the
        drawing of a shapefile between periods you will end up with a change which may not actually occur. You can
        remove a 'weight' from a 'place' by providing the place key to place, and the weight you want to remove to
        'weight'.

        :param place: The place to load from the master database
        :type place: str

        :param weight_date: The weight's date to remove from the master
        :type weight_date: str

        :return: Nothing, remove from the master then stop
        :rtype: None
        """
        # Load the current place form the weights
        current = self._weights[place]

        # Create the replacement, where the each date is assign its previous weight places as long as the date does not
        # equal the weight_date provided
        replacement = {date: weight_places for date, weight_places in current.items() if date != weight_date}

        # Replace original place weights with replacement
        self._weights[place] = replacement
        write_json(self._weights, self._weights_path.parent, self._weights_path.stem)

    def add_place(self, new_weight):
        """
        Add a place to master dict

        In some situations you may wish to add a place that was not set, or you have removed a weight and now want
        to add it's replacement. Here you just assign dict you want to assign to the master json dict, each key will
        be added to the master dict.

        :param new_weight: A dict of place: weights, where place is the name of the place to be weighted and the weights
            the weights assigned at given dates assigned to the place
        :return: Nothing, will add to master dict then stop
        :rtype: None
        """

        for key in new_weight.keys():
            self._weights[key] = new_weight[key]
        write_json(self._weights, self._weights_path.parent, self._weights_path.stem)

    def remove_place(self, places_to_remove):
        """
        Remove a place from the master dict

        You may have a place you do not want in the master dict, but do not want to edit the shapefile to ensure it is
        not added. You can remove as many places as you want by providing a list of places to remove to this method.

        :param places_to_remove: The places you wish to remove from the master dict, represents the master dicts keys.
        :type: list

        :return: Nothing, will remove from master then stop
        :rtype: None
        """

        self._weights = {key: value for key, value in self._weights.items() if key not in places_to_remove}
        write_json(self._weights, self._weights_path.parent, self._weights_path.stem)

    def write_out_changes(self, write_name, population_weights=True):
        """
        Write out a csv of all changes that occur on a per place

        To be able to write the weight file we need to know when the changes occur, not just how many changes occur. To
        do this we need a list of names and the expected number of changes. The assumption is, that a place will not
        change more than once between census years but when this is not the case we need to be explict about this so we
        can work of the change manually if need be.

        :return: Nothing, just write out the csv file with the number of expected changes and support search terms
        :rtype: None
        """
        write_holder = [[weight_group, len(self._determine_changes(weight_group, population_weights)) - 1]
                        for weight_group in self._weights]

        write_csv(self._working_dir, write_name, ["Place", "Expected_Changes"], write_holder)
        print("Written out changes!")

    def _determine_changes(self, weight_group, population_weights):
        """
        Check to see if any changes occur for the current places's weight_group within the base weights

        :param weight_group: The current changes for the current place
        :type weight_group: int

        :param population_weights: If population weights where used
        :type: bool

        :return: List of all the non duplicated changes
        :rtype: list
        """
        cleaned_of_duplication = []
        for value in self._weights[weight_group].values():
            if population_weights:
                non_duplication = [[k, v["Area"], v["Population"]] for k, v in zip(value.keys(), value.values())]
            else:
                non_duplication = [[k, v["Area"]] for k, v in zip(value.keys(), value.values())]

            if non_duplication not in cleaned_of_duplication:
                cleaned_of_duplication.append(non_duplication)

        return cleaned_of_duplication
