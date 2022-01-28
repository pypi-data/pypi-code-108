from ..basis.immutable import Immutable


class Procedure(Immutable):

    def run(self, messenger):
        """
        This method will be called by the Worker to execute in a process.

        Override this method.
        Use __init__ to set any params needed for this call
        The messenger parameter is a Messenger instance

        Use messenger.debug/info/warning/error to send logs
        Use messenger.submit_tasks to submit sub tasks to the server
        Use messenger.query_results to query for results of the submitted sub tasks

        If you call predefined functions in this method, and would like to direct the print output to Worker's log.
        Do:
            predefined_function.__globals__["print"] = messenger.print  # inject messenger.print as print
        See the RunFunction procedure as an example

        ATTENTION: do not use multiprocessing in this method.

        :param messenger: Messenger
        :return: The data if the task is successful. The data will be constructed to a successful
            TaskResult by the TaskWorker.
        :raise raise TaskFailed exception with the failed data if the task is unsuccessful. e.g.
            raise TaskFailed("ID not found"). The "ID not found" will be constructed to a failed TaskResult.
            Other exceptions will be caught by the Worker and be constructed to a unsuccessful TaskResult using
            the Exception instance as data
        """
        raise NotImplementedError
