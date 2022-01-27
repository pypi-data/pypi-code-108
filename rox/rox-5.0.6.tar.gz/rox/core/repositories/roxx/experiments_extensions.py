import hashlib

from rox.core.entities.flag import Flag


class ExperimentsExtensions:
    def __init__(self, parser, target_groups_repository, flags_repository, experiment_repository):
        self.parser = parser
        self.target_groups_repository = target_groups_repository
        self.flags_repository = flags_repository
        self.experiment_repository = experiment_repository

    def extend(self):
        self.parser.add_operator('mergeSeed', merge_seed)
        self.parser.add_operator('isInPercentage', is_in_percentage)
        self.parser.add_operator('isInPercentageRange', is_in_percentage_range)
        self.parser.add_operator('flagValue', lambda parser, stack, context: flag_value(self.flags_repository, self.experiment_repository, parser, stack, context))
        self.parser.add_operator('isInTargetGroup', lambda parser, stack, context: is_in_target_group(self.target_groups_repository, parser, stack, context))


def merge_seed(parser, stack, context):
    seed1 = stack.pop()
    seed2 = stack.pop()
    stack.push("%s.%s" % (seed1, seed2))


def is_in_percentage(parser, stack, context):
    percentage = float(stack.pop())
    seed = stack.pop()

    bucket = get_bucket(seed)
    stack.push(bucket <= percentage)


def is_in_percentage_range(parser, stack, context):
    percentage_low = float(stack.pop())
    percentage_high = float(stack.pop())
    seed = stack.pop()

    bucket = get_bucket(seed)
    stack.push(percentage_low <= bucket < percentage_high)


def flag_value(flags_repository, experiment_repository, parser, stack, context):
    feature_flag_identifier = stack.pop()
    result = Flag.FLAG_FALSE_VALUE
    variant = flags_repository.get_flag(feature_flag_identifier)

    if variant is not None:
        result = variant.get_value(context)
    else:
        flags_experiment = experiment_repository.get_experiment_by_flag(feature_flag_identifier)
        if flags_experiment is not None and flags_experiment.condition:
            experiment_eval_result = parser.evaluate_expression(flags_experiment.condition, context).string_value()
            if experiment_eval_result:
                result = experiment_eval_result

    stack.push(result)


def is_in_target_group(target_groups_repository, parser, stack, context):
    target_group_identifier = stack.pop()
    target_group = target_groups_repository.get_target_group(target_group_identifier)
    if target_group is None:
        stack.push(False)
    else:
        stack.push(parser.evaluate_expression(target_group.condition, context).bool_value())


def get_bucket(seed):
    to_bytes = seed.encode('ascii')

    m = hashlib.md5()
    m.update(to_bytes)
    bytes = m.digest()
    bytes = [ord(b) if not isinstance(b, int) else b for b in bytes]

    hash = (bytes[0] & 0xFF) | ((bytes[1] & 0xFF) << 8) | ((bytes[2] & 0xFF) << 16) | ((bytes[3] & 0xFF) << 24)
    hash &= 0xFFFFFFFF
    bucket = hash * 1.0 / (2**32 - 1)

    return 0 if bucket == 1 else bucket
