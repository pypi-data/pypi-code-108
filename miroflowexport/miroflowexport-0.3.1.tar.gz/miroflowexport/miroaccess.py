from miroflowexport.internal import miroaccess as mac
from miroflowexport.internal import exporter as mac_exporter

class MiroAccess:

    def __init__(self, log, token, board_id):
        self._log = log
        self._token = token
        self._board_id = board_id

    def try_get_task_list(self):
        ###
        # Tries to fetch the list of sticky notes from the Miro board and returns them as tasks with additional information.
        #
        # Returns a tuple (success_as_bool, dict_of_tasks_by_id) with success is either True or False
        ###
        response = mac.send_request_widgets(self._log, token = self._token, board_id = self._board_id)
        self._log.debug("Response is: {}".format(response))
        success = mac.is_response_ok(self._log, response)

        if not success:
            return (False, {})

        tasks = mac.get_list_of_cards(self._log, response.text)
        mac.get_list_of_dependencies(self._log, response.text, tasks)
        return (True, tasks)

    def try_get_all_board_content(self):
        ###
        # Tries to get the complete list of widgets for backup.
        ###
        response = mac.send_request_widgets(self._log, token = self._token, board_id=self._board_id)
        self._log.debug("Response is: {}".format(response))
        success = mac.is_response_ok(self._log, response)

        if not success:
            self._log.error("Cannot fetch board content.")
            return {}

        return response.text

    def export_to_excel(self, tasks_dict, path = "tmp/excel.xlsx"):
        return mac_exporter.tasks_to_excel(self._log, tasks_dict, path)

    def export_board_to_excel(self, path = "tmp/excel.xlsx"):
        self._log.info("Fetching board content ...")
        (success, tasks_dict) = self.try_get_task_list()
        if not success:
            self._log.error("Fetching board content failed.")
            return False

        self._log.info("Exporting board content to file {} ...".format(path))
        success = mac_exporter.tasks_to_excel(self._log, tasks_dict, path)
        if not success:
            self._log.error("Exporting board content to Excel failed.")
            return False

        return True
