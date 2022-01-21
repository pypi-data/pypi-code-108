import inspect
import os
import sys


# decorator on_event
def on_event(event):
    def decorator(func):
        if not hasattr(func, 'event'):
            func.event = []
        func.event.append(event)
        return func
    return decorator


class HandlerManager(object):

    def __init__(self, base_dir='', event_handler_dir='', handler_files_prefix=''):
        self.event_files = []
        self.observing_functions = []
        self.event_mapping = {}
        self.base_dir = base_dir
        self.event_handler_dir = event_handler_dir
        self.handler_files_prefix = handler_files_prefix

    def get_events_mapping(self):
        self._discover_handlers()
        return self.event_mapping

    def _discover_handlers(self):
        self._discover_event_handlers_files()
        self._recover_observing_functions()
        self._map_events_to_functions()

    def _discover_event_handlers_files(self):
        f = []
        event_files = []
        for (dirpath, dirnames, filenames) in os.walk(self.base_dir):
            f.extend(dirnames)
            break

        for folder in f:
            dirs = []
            for (dirpath, dirnames, filenames) in os.walk(os.path.join(self.base_dir, folder)):
                dirs = dirnames
                break
            if self.event_handler_dir in dirs:
                files_in_event_handlers = []
                for (a, b, c) in os.walk(os.path.join(self.base_dir, folder, self.event_handler_dir)):
                    files_in_event_handlers = c
                    break
                for x in files_in_event_handlers:
                    if str(x).startswith(self.handler_files_prefix) and str(x).endswith('py'):
                        event_files.append(folder + '.' + self.event_handler_dir + '.' + str(x).split('.py')[0])
        self.event_files = event_files

    def _recover_observing_functions(self):
        for c in self.event_files:
            __import__(c, globals(), locals(), ['*'])
            for x in inspect.getmembers(sys.modules[c], inspect.isfunction):
                function = x[1]
                if hasattr(function, 'event'):
                    self.observing_functions.append(function)

    def _map_events_to_functions(self):
        for x in self.observing_functions:
            events = x.event
            for ev in events:
                if ev not in self.event_mapping:
                    self.event_mapping[ev] = [x]
                else:
                    self.event_mapping[ev] = self.event_mapping[ev] + [x]
