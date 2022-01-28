def validate_argument(argument_name: str, arg_spec: dict):
    mandatory_keys = ('type', 'required')

    # Check that all the keys exist by doing a set subtraction
    assert set(arg_spec.keys()) & set(mandatory_keys) == set(mandatory_keys), 'Missing required keys in the hook {}'.format(argument_name)

    # Check the type of all the key's values
    assert isinstance(arg_spec.get('type'), str), 'Hook {} has malformed type, should be string'.format(argument_name)
    assert isinstance(arg_spec.get('required'), bool), 'Hook {} has malformed required, should be bool'.format(argument_name)
    assert isinstance(arg_spec.get('description', ''), str), 'Hook {} has malformed description, should be string'.format(argument_name)

    arg_type = arg_spec.get('type')
    assert arg_type in ('string', 'int', 'float', 'list', 'dict', 'bool'), 'Invalid type provided for argument {}'.format(argument_name)

    return True


def validate_hook(hook: str, hook_spec: dict, hooks: dict):
    mandatory_keys = ('reference', 'args')

    # Check that all the keys exist by doing a set subtraction
    assert set(hook_spec.keys()) & set(mandatory_keys) == set(mandatory_keys), 'Missing required keys in the hook {}'.format(hook)

    # Check the type of all the key's values
    assert isinstance(hook_spec.get('reference'), str), 'Hook {} has malformed reference, should be string'.format(hook)
    assert isinstance(hook_spec.get('args'), dict), 'Hook {} has malformed args, should be dict structure'.format(hook)
    assert isinstance(hook_spec.get('dependencies', []), list), 'Hook {} has malformed dependencies, should be list structure'.format(hook)
    assert isinstance(hook_spec.get('rectifiers', []), list), 'Hook {} has malformed rectifiers, should be list structure'.format(hook)
    assert isinstance(hook_spec.get('description', ''), str), 'Hook {} has malformed description, should be string'.format(hook)

    for arg in hook_spec.get('args'):
        validate_argument(arg, hook_spec.get('args').get(arg))

    all_hook_refs = hook_spec.get('dependencies', []) + hook_spec.get('rectifiers', [])
    for h in all_hook_refs:
        assert h.split('.')[-1] in hooks, 'Hook {} referenced a hook that does not exist (referencing {})'.format(hook, h)
        # A hook cannot reference itself
        assert h.split('.')[-1] != hook, 'Hook {} attempted to depend on itself'.format(hook)

    return True


def validate_program(program_name: str, program_spec: dict, hooks: tuple):
    mandatory_keys = ('hooks', 'args', 'outputs')

    # Check that all the keys exist by doing a set subtraction
    assert set(program_spec.keys()) & set(mandatory_keys) == set(mandatory_keys), 'Missing required keys in the program {}'.format(program_name)

    # Check the type of all the key's values
    assert isinstance(program_spec.get('hooks'), list), 'Program {} has malformed hooks, should be list structure'.format(program_name)
    assert isinstance(program_spec.get('args'), dict), 'Program {} has malformed args, should be dict structure'.format(program_name)
    assert isinstance(program_spec.get('outputs'), dict), 'Program {} has malformed outputs, should be dict structure'.format(program_name)
    assert isinstance(program_spec.get('description', ''), str), 'Program {} has malformed description, should be string'.format(program_name)

    for arg in program_spec.get('args'):
        validate_argument(arg, program_spec.get('args').get(arg))

    for h in program_spec.get('hooks'):
        assert h.split('.')[-1] in hooks, 'Program {} referenced a hook that does not exist (referencing {})'.format(program_name, h)

    return True


def validate_spec(ryu_spec: dict):
    mandatory_keys = ('name', 'programs', 'hooks')

    # Check that all the keys exist by doing a set subtraction
    assert set(ryu_spec.keys()) & set(mandatory_keys) == set(mandatory_keys), 'Missing required keys in the spec'

    hook_names = tuple(ryu_spec.get('hooks').keys())

    for p in ryu_spec.get('programs'):
        validate_program(p, ryu_spec.get('programs').get(p), hook_names)

    refs = set()
    for h in ryu_spec.get('hooks'):
        validate_hook(h, ryu_spec.get('hooks').get(h), hook_names)

        # Check for duplicate implementation references in hooks
        ref = ryu_spec.get('hooks').get(h).get('reference')
        assert not ref in refs, 'A duplicate hook implementation reference {} was found. Each hook must have a unique reference'.format(ref)
        refs.add(ref)

    return True


def compress_spec(ryu_spec: dict):
    # Remove non-mandatory output arguments
    to_remove_outputs = []

    for p in ryu_spec.get('programs'):
        for o in ryu_spec.get('programs').get(p).get('outputs'):
            if not ryu_spec.get('programs').get(p).get('outputs').get(o).get('required', False):
                to_remove_outputs.append(o)

        for o in to_remove_outputs:
            ryu_spec['programs'][p]['outputs'].pop(o)

    return ryu_spec

'''
Failure-checking functions for hooks
'''
def has_failed(data_pool):
    return any([
        has_rectifier_failed(data_pool),
        has_dependency_failed(data_pool),
        has_program_failed(data_pool)
    ])


def has_rectifier_failed(data_pool):
    return data_pool.get('_rectifier_fail', False)


def has_dependency_failed(data_pool):
    return data_pool.get('_dependency_fail', False)


def has_program_failed(data_pool):
    return data_pool.get('_program_fail', False)
