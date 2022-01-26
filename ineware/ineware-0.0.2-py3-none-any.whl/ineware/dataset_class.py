import json
import requests
import itertools


class DatasetValue:
    """
    This class represents a set formed by a dataset value together with the labels that identify it.
    For example in a dataset related with population, sexes and age, a DatasetValue could be:
    ["Hombres", "35 años", 2.35]

    Attributes:
        labels : list
            a list containing the labels that identify the DatasetValue
        value : int
            the value related to the labels

    """
    def __init__(self, labels, value):
        """
        This method initializes DatasetValue with its labels and value

        Args
        -----
        labels : list
            a list containing the labels that identify the DatasetValue
        value : int
            the value related to the labels

        """
        self.labels = labels
        self.value = value

    def __str__(self):
        """
        This method converts a DatasetValue item in a string

        Returns:
            a string containing the labels and value

        """
        return str(self.labels) + " value: " + str(self.value)

    def __eq__(self, other):
        """
        This method compares two instances of DatasetValue

        Returns:
            -- True if both objects are from DatasetValue class and have the same labels and value
            -- False otherwise

        """
        if isinstance(other, DatasetValue):
            return self.get_value() == other.get_value() and self.get_labels() == other.get_labels()
        else:
            return False

    def get_labels(self):
        """
        This method gets the labels of the DatasetValue

        Returns:
            a list containing the labels

        """
        return self.labels

    def get_value(self):
        """
        This method gets the value of the DatasetValue

        Returns:
            an integer corresponding to the value

        """
        return self.value


class DatasetINE:
    """
    This class represents a dataset from INE. It stores all the information available about an
    specific dataset from INE, just specifying the url associated to it when creating the object.

    Attributes
    ----------
    url : str
        the url the dataset is obtained from after sending a request
    data : dict
        a dictionary containing the entire json file obtained from url
    name : str
        the title of the dataset
    values : list
        a list of every value this dataset stores (just numeric values)
    notes : str
        a string representing the notes associated to the dataset. It gives us information such as unit
        of measure (days, migration movements, travelers...) and other important details
    datasetValues : list
        a list containing class DatasetValue objects. It stores every value from dataset associated to
        its identifying labels
    dimensions : list
        this list contains every dimension of this dataset. A dimension is every label category the dataset
        has. For example, dimensions for dataset "Estancia media por comunidades autónomas y provincias" are:
        ['Comunidades Autónomas y Provincias', 'Periodo']
    dimLabels : dict
        this dictionary contains every dimension and its different labels. Following the previous example,
        for dataset "Estancia media por comunidades autónomas y provincias" dimLabels is:
        { "Comunidades Autónomas y Provincias": [
              "Andalucía",
              "Almería",
              "Cádiz",
               ...
          ],
          "Periodo": [
              "2021M11",
              "2021M10",
              ...
          ]
        }
    """
    def __init__(self, url):
        """
        This method initializes a DatasetINE object using its url as argument

        Args
        -----
        url : str
            the url of the dataset you want to load into the new object

        """
        self.url = url
        if request_error_handler(url):
            self.data = requests.get(url).json()
            self.name = self.data['label']
            self.values = self.data['value']
            self.notes = str(self.data['note'])
            self.datasetValues = []
            self.dimensions, self.dimLabels = self.create_dict()
            self.save_values()

    def __str__(self):
        """
        This method gives us the main info about a DatasetINE object

        Returns:
            a string containing the title and url of the dataset

        """
        return "------- Dataset info --------\n" + \
               "Name = " + self.name + "\n" +\
               "url = " + self.url + "\n" +\
               "-----------------------------\n"

    def create_dict(self):
        """
        This method creates the dimensions list and the dimLabels dictionary of the DatasetINE object

        Returns:
            -- 1) a list with dimensions of the dataset
            -- 2) a dictionary containing every dimension and its labels

        """
        new_dict = {}
        my_labels = []
        for key, value in self.data['dimension'].items():
            new_dict[value['label']] = {}
            my_labels.append(value['label'])
            aux_list = []
            for key1, value1 in value['category']['label'].items():
                aux_list.append(value1)
            new_dict[value['label']] = aux_list
        return my_labels, new_dict

    def export_json(self, filename):
        """
        This method exports a file in json format containing the raw dataset data

        Args
        -----
        filename : str
            the path of the generated file

        """
        print("exporting dataset json to file", filename, "...")
        f = open(filename, "w", encoding='utf8')
        f.write(json.dumps(self.data, ensure_ascii=False, indent=4))
        f.close()
        print("file", filename, "saved")

    def export_values(self, filename):
        """
        This method exports a file containing the list of DatasetValues of our dataset

        Args
        -----
        filename : str
            the path of the generated file

        """
        print("exporting values to file", filename, "...")
        f = open(filename, "w", encoding='utf8')
        for item in self.datasetValues:
            my_string = str(item) + '\n'
            f.write(my_string)
        f.close()
        print("file", filename, "saved")

    def add_value(self, value):
        """
        This method appends a new item to the datasetValues list of our dataset

        Args
        -----
        value : DatasetValue
            the value to insert in the list

        """
        self.datasetValues.append(value)

    def print_values_list(self):
        """
        This method prints to console every DatasetValue item in our dataset

        """
        for item in self.datasetValues:
            print(item)

    def get_value(self, **kwargs):
        """
        This method looks for specific values contained in our dataset. If values match the pattern
        given as argument, they are included in the returning list. For example we can give as argument:
            Sexo="Hombres", Edad="20 años", Periodo="2021S1"

        Args
        ------
        kwargs : dict
            the labels and values we want to get.

        Returns:
            a list containing every matching DatasetValue object or empty list if there are no matches,
            showing a message in this case.

        """
        result_list = []
        for value in self.datasetValues:
            if exist_label(value, kwargs):
                result_list.append(value)
        if len(result_list) > 0:
            return result_list
        else:
            print('No values found for labels ' + str(kwargs))
            return []

    def save_values(self):
        """
        This method insert into our dataset values list every item found on the raw
        data. In order to do this, it relates every possible combination of labels
        with the corresponding value.

        """
        all_list = []
        for i in range(len(self.dimensions)):
            all_list.append(self.dimLabels[self.dimensions[i]])

        res = list(itertools.product(*all_list))

        for item, value in zip(res, self.data['value']):
            my_labels = list(item)
            if value is not None:
                if value.is_integer():
                    my_value = DatasetValue(my_labels, int(value))
                else:
                    my_value = DatasetValue(my_labels, value)
                self.add_value(my_value)


def exist_label(value: DatasetValue, args):
    """
    This method checks if the arguments given match the DatasetValue passed as parameter.

    Args
    ------
    value : DatasetValue
        the DatasetValue to check if matches
    args : list
        the labels we want to check if match

    Returns:
        -- True if every label from args match the ones in DatasetValue
        -- False otherwise

    """
    label_found = [False] * len(args)
    counter = 0
    final_flag = True
    for item in value.get_labels():
        for label in args.values():
            if item == label:
                label_found[counter] = True
                counter += 1
    for flag in label_found:
        if flag is False:
            final_flag = False
    return final_flag


def request_error_handler(url):
    """
    This method is a handler for the request sent to the dataset url. It manages possible
    errors thrown by the request and informs the user about what happened.

    Args
    url : str
        the url to send the request to

    Returns:
        True if the request is completed successfuly

    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err_h:
        print("Http Error:", err_h)
    except requests.exceptions.ConnectionError as err_c:
        print("Error Connecting:", err_c)
    except requests.exceptions.Timeout as err_t:
        print("Timeout Error:", err_t)
    except requests.exceptions.RequestException as err:
        print("Oops: Something happened!", err)
