import logging

from ryuso import Hook, util

class Orchestrator:
    '''
    Orchestrator: The result of a built RYU spec

    This class builds and implements all of the programs of the RYU spec.

    This class can directly take in a request and process it according to the spec.
    '''
    def __init__(self, ryu_spec: dict):
        assert util.validate_spec(ryu_spec)
        self.ryu_spec = util.compress_spec(ryu_spec)
        self.implementation = {}

        self.implementation['programs'] = {}
        self.implementation['hooks'] = {}

        for p in ryu_spec.get('programs'):
            # Each program consists of a list of keys for the hooks member
            # self.add_hook needs to be called to populate the hooks dictionary
            self.implementation['programs'][p] = [h.split('.')[-1] for h in ryu_spec.get('programs').get(p).get('hooks')]

    # STUB
    def validate_task(self, task: dict):
        '''
        Validates a task request to ensure that it is correct
        '''
        return True

    # STUB
    def validate_output(self, program_name: str, out_data: dict):
        '''
        Validates a task's output to see if it conforms to the spec
        '''
        return True

    def add_hook(self, hook: Hook):
        '''
        Adds a hook to the hook structure.
        '''
        self.implementation['hooks'][hook.base_name] = hook

    def load_runtime_for(self, program_name: str):
        '''
        Gets the list of function references for a particular program.
        The implementation structure stores programs and hook references and
        this simply dereferences that list of references.

        :returns: List of Hook objects representing the hooks of the
            program provided.
        '''
        runtime_hooks = self.implementation.get('programs').get(program_name)

        return [self.implementation.get('hooks').get(hook_ref) for hook_ref in runtime_hooks]

    def mask_output(self, program_name: str, out_data: dict):
        logging.debug('Raw program output: %s', out_data)
        # Get all the names of all the outputs for the program
        mask = set(self.ryu_spec.get('programs').get(program_name).get('outputs').keys())

        # Keep all debug info only if debugging is enabled or program unsuccessful
        if util.has_failed(out_data):
            debug_info_keys = filter(lambda k: k.startswith('_'), out_data)

            for k in debug_info_keys:
                mask.add(k)

        keys_to_remove = set(out_data.keys()) - mask

        for k in keys_to_remove:
            out_data.pop(k)

        return out_data

    def run_task(self, task: dict):
        '''
        Runs a single task. It will create a list of hooks to run and then run
        them based on the spec for the program provided.
        '''
        assert self.validate_task(task), 'The task requested is not valid'

        program = task.get('program', None)
        init_pool = task.get('data_pool', {})
        metadata = task.get('metadata', {})

        logging.info('Running program %s', program)

        if bool(metadata):
            logging.info('Metadata: %s', metadata)

        runtime = self.load_runtime_for(program)
        data_pool = init_pool

        logging.debug('Generated runtime: %s', runtime)

        for i, h in enumerate(runtime):
            data_pool = h.run(data_pool)

            # If a hook has flagged that it has failed, then begin the process
            # of rectification.
            if util.has_program_failed(data_pool):
                logging.info(
                    'Runtime fail detected in program %s, commencing rectification',
                    program
                )

                # From 1 before the erroneous hook, start executing rectification
                for h_idx in range(i - 1, -1, -1):
                    data_pool = runtime[h_idx].reverse_run(data_pool)

                    # If any rectifier fails, then stop doing everything
                    if util.has_rectifier_failed(data_pool):
                        logging.info(
                            'Program %s signalled failure at rectification for %s, stopping',
                            program,
                            runtime[h_idx].qualified_name
                        )
                        break
                break

        final = self.mask_output(program, data_pool)

        assert self.validate_output(program, final), 'The final output for the program is missing at least one item defined in the spec'

        return final

    def __del__(self):
        pass
