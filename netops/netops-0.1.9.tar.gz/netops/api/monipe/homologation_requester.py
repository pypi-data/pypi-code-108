from time import sleep

from .homologation_manager import HomologationRequestManager
from ...utils.utils import print_json


def request_test(request_file_path):
    """
	TODO: write docstrings
	"""
    
    try:
        manager = HomologationRequestManager(request_file_path)
        manager.schedule_test()

        finished = False
        result = None
        while not finished:
            # TODO: find a better way to schedule this task
            sleep(60)
            status = manager.get_test_status()
            if not manager.test_status_error:
                finished = status['status']['description'] == 'finished'
                #print("Status: ", str(status))
                print("Status: ")
                print_json(dict(status))
            else:
                raise Exception(manager.test_status_error)
        result = status['result']['description']
        print("Result: ", result)
        while result == "not_started":
            sleep(10)
            result = status['result']['description']
            print("Result: ", result)

        if result != 'approved':
            raise Exception(result)
        print("Tests Done!")

        min = 1
        get_repo_confirm = False
        while min<=5 and not get_repo_confirm:
            print("Trying to get report...")
            print(f"Get report try number {min}")
            get_repo_confirm = manager.get_test_report()
            sleep(60)
            min += 1

    except Exception as e:
        print("Error: ", str(e))
        exit(1)
