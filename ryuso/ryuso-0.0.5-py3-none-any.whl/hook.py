import logging
import traceback

from ryuso import util

class Hook:
    '''
    Hook: The data structure that manages a specific hook in the RYU spec.

    To fully build this object, you must init it and then add all of the
    rectification functions.
    '''
    def __init__(self, function, qualified_name: str):
        '''
        :param function: The callable function that is the hook.
        :param qualified_name: The qualified name that appears in the spec as
            hook.reference. This is so that the hook can be indexed in
            containing objects.
        '''
        self.function = function
        self.qualified_name = qualified_name
        self.base_name = qualified_name.split('.')[-1]
        self.is_rectifier = False
        self.is_dependency = False
        self.rectifiers = []
        self.dependencies = []

    def _catch_failure(func): #pylint: disable=E0213
        def catch_failure_inner_wrapper(self, data_pool: dict):
            try:
                return func(self, data_pool) #pylint: disable=E1102
            except KeyboardInterrupt:
                # Catch everything except for ctrl+c
                pass
            except Exception as e:
                logging.warning(
                    'Hook %s failed to complete, traceback: %s',
                    self.qualified_name,
                    traceback.format_exc()
                )
                # Flag that runtime has failed (failed execution of program)
                data_pool['_program_fail'] = True
                # Flag that a rectifier failed. This means that all hope is lost
                data_pool['_rectifier_fail'] = self.is_rectifier
                data_pool['_dependency_fail'] = self.is_dependency
                data_pool['_last_failed_program'] = self.qualified_name
                return data_pool
        return catch_failure_inner_wrapper

    def _trace(func): #pylint: disable=E0213
        def trace_inner_wrapper(self, data_pool: dict):
            if not data_pool.get('_traceback', False):
                data_pool['_traceback'] = []
            data_pool['_traceback'].append(self.qualified_name)

            return func(self, data_pool) #pylint: disable=E1102
        return trace_inner_wrapper


    def add_rectifier(self, rectifier):
        rectifier.is_rectifier = True # Ensure that the hook to be added is a rectifier
        self.rectifiers.append(rectifier)

    def add_dependency(self, dependency):
        dependency.is_dependency = True # Ensure that the hook to be added is a dependency
        self.dependencies.append(dependency)

    def reverse_run(self, data_pool):
        logging.info('Rectification being run on %s', self.qualified_name)
        current_data_pool = data_pool
        for r in self.rectifiers:
            current_data_pool = r.run(current_data_pool)

            # If a rectifier failed, then fail everything
            if util.has_rectifier_failed(current_data_pool):
                logging.error('Rectification for %s failed at %s', self.qualified_name, r.qualified_name)
                return current_data_pool

        logging.debug('Rectification completed successfully')
        return current_data_pool

    def run_dependencies(self, data_pool):
        logging.debug('Running dependencies for %s', self.qualified_name)
        current_data_pool = data_pool

        for d in self.dependencies:
            current_data_pool = d.run(current_data_pool)

            if util.has_dependency_failed(current_data_pool):
                logging.error('Dependencies for %s failed at %s', self.qualified_name, d.qualified_name)
                return current_data_pool

        logging.debug('Dependencies completed successfully')
        return current_data_pool

    @_trace
    @_catch_failure
    def run(self, data_pool: dict):
        data_pool = self.run_dependencies(data_pool)

        if util.has_failed(data_pool):
            return data_pool

        return self.function(data_pool)

    def __del__(self):
        pass
