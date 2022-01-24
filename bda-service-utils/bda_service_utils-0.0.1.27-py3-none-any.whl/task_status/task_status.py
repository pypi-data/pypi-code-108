from abc import ABC, abstractmethod
from ..task_args import get_cmd_arg

class TaskStatus(ABC):
    """Helper class to help manage Task's status in the SCDF DB. """
    def __new__(cls, *args, **kw):
        
        # Check if running on SCDF or locally        
        if get_cmd_arg('spring.datasource.url') is not None:
            task_status_type = "scdf"
        else:
            task_status_type = "local"

        # Create a map of all subclasses based on storage type property (present on each subclass)
        subclass_map = {subclass.task_status_type: subclass for subclass in cls.__subclasses__()}

        # Select the proper subclass based on
        subclass = subclass_map[task_status_type]
        instance = super(TaskStatus, subclass).__new__(subclass)
        return instance

    @abstractmethod
    def running(self):
        pass
    
    @abstractmethod
    def completed(self):
        pass

    @abstractmethod
    def failed(self, exit_code, exit_message, error_message=''):
        pass

