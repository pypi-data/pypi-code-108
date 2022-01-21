from .task_status import TaskStatus
import os

class Local(TaskStatus):
    """Helper class to help manage Task's status in the SCDF DB. """
    
    task_status_type = os.path.basename(__file__).split('.py')[0]

    def __init__(self):
        pass

    def running(self):
        print("Task is running.")

    def completed(self):
        print("Task completed.")

    def failed(self, exit_code, exit_message, error_message=''):
        print("Error! Task failed with exit code: " + str(exit_code))
        print("Exit message: ", exit_message)
        if error_message!="":
            print("Error message: ", error_message)
