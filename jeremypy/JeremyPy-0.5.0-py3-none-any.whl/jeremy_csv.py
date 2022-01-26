import os
import csv

from jeremypy.jeremy_exceptions import CSVFileNotFoundError


def read_csv(path, headers=False, create_if_missing=True):
    """Reads csv file and returns list of lists if no headers, or list of dicts if headers."""
    if not os.path.isfile(path):
        if create_if_missing:
            open(path, 'w').close()
        else:
            raise CSVFileNotFoundError(path)
        return
    with open(path, 'r') as fp:
        reader = csv.reader(fp)
        csv_list = []
        if headers:
            headers = reader.__next__()
            for row in reader:
                item = {}
                for i in range(len(row)):
                    item[headers[i]] = row[i]
                csv_list.append(item)
            return csv_list
        else:
            for row in reader:
                csv_list.append(row)
            return csv_list
