def get_parent_log_key_or_none(logger):
    return '{}|{}'.format(logger.parent_with_id.name, logger.parent_with_id.id) if logger.parent_with_id else None
