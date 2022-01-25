import os
import pickle
import time


class PickleManagement:
    """ Manage pickle files to be used as cached data
    """
    def __init__(self, path):
        """ Initialize the class
        :param path: Default path to store and retrieve the files
        """
        self.path = path

    def save_file(self, data, filename, path=''):
        """ Save data to path + table_nameSave data to path + table_name
        :param data: DataFrame gathering the data to store
        :param filename: Name of the file in which the data will be stored
        :param path: Path to the folder in which the file will be stored
        """
        t1 = time.time()

        if path == '':
            path = self.path

        filepath = path + filename
        self.remove_pickle(filepath)
        self.dump_pickle(data, filepath)

        print(time.time() - t1)

    def retrieve_file(self, filename, path=''):
        """ Retrieve the datasets from path
        :param filename: Name of the file to retrieve
        :param path: Path to the folder in which the file is stored
        """
        t1 = time.time()

        if path == '':
            path = self.path

        try:
            filepath = path + filename
            data_df = self.retrieve_pickle(filepath)
        except Exception:
            raise Exception("The file: %s cannot be found in path: %s" % (filename, path))

        print(time.time() - t1)

        return data_df

    @staticmethod
    def dump_pickle(df, filepath):
        """ Save the data to a filepath
        :param df: DataFrame gathering the data
        :param path: Path and filename to the file destination
        """
        pickle_out = open(filepath, 'wb')
        pickle.dump(df, pickle_out)
        pickle_out.close()

    @staticmethod
    def retrieve_pickle(filepath):
        """ Get the data from the indicated filepath
        :param path: Path and filename to the file destination
        """
        pickle_in = open(filepath, "rb")
        data_df = pickle.load(pickle_in)
        pickle_in.close()
        return data_df

    @staticmethod
    def remove_pickle(filepath):
        """ Delete a file allocated in filepath
        :param path: Path and filename to the file destination
        """
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == '__main__':
    PickleManagement(path='')
