from flask import url_for
from oarepo_records_draft import current_drafts


# TODO: refactor to nr_common

def nr_links_factory(pid, record=None, **kwargs):
    if record:
        return dict(self=record.canonical_url)
    if pid:
        endpoint = current_drafts.endpoint_for_pid(pid).rest_name
        return dict(self=url_for(
            f'invenio_records_rest.{endpoint}_item',
            pid_value=pid.pid_value,
            _external=True
        ))
    return {}
