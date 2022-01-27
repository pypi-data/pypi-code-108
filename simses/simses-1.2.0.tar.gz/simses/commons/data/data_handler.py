from abc import ABC, abstractmethod


class DataHandler(ABC):
    """
    Abstract Base Class for Data Export
    """

    def __init__(self):
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Function to write data from queue to csv.

        Parameters
        ----------

        Returns
        -------

        """
        pass

    @abstractmethod
    def transfer_data(self, data: dict) -> None:
        """
        Function to place data into the queue. This data is picked up by the run function and written into a CSV file_name.

        Parameters
        ----------
        data : list

        Returns
        -------

        """
        pass

    @abstractmethod
    def simulation_done(self) -> None:
        """
        Function to let the DataExport Thread know that the simulation is done and stop after emptying the queue.

        Parameters
        ----------

        Returns
        -------

        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Closing all open resources in data export

        Parameters
        ----------

        Returns
        -------

        """
        pass

    def is_alive(self) -> None:
        """
        Checks if a thread is running

        Parameters
        ----------

        Returns
        -------

        """
        pass