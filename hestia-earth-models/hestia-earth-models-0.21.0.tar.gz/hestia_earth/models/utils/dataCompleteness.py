from hestia_earth.utils.api import download_hestia


def _get_term_type_completeness(cycle: dict, term):
    term_type = (download_hestia(term) if isinstance(term, str) else term).get('termType')
    return cycle.get('dataCompleteness', {}).get(term_type, False)


def _is_term_type_complete(cycle: dict, term):
    return _get_term_type_completeness(cycle, term) is True


def _is_term_type_incomplete(cycle: dict, term):
    return _get_term_type_completeness(cycle, term) is False
