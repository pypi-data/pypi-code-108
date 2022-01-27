from .data_handler import DataHandler


class NoDataHandler(DataHandler):
    """
    Does not export anything.
    """

    def __init__(self):
        super().__init__()

    def start(self) -> None:
        """
        Function to write data from queue to csv.

        Parameters
        ----------

        Returns
        -------

        """
        pass

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

    def simulation_done(self) -> None:
        """
        Function to let the DataExport Thread know that the simulation is done and stop after emptying the queue.

        Parameters
        ----------

        Returns
        -------

        """
        pass

    def close(self) -> None:
        """
        Closing all open resources in data export

        Parameters
        ----------

        Returns
        -------

        """
        pass
