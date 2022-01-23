from functools import reduce
from hestia_earth.schema import SchemaType
from hestia_earth.utils.tools import non_empty_list

from . import _aggregated_version, _aggregated_node, _set_dict_array
from .term import _update_country, _format_country_name
from .measurement import _new_measurement


def _format_aggregate(aggregate: dict):
    node = aggregate.get('node')
    term = aggregate.get('term')
    value = aggregate.get('value')
    min = aggregate.get('min')
    max = aggregate.get('max')
    sd = aggregate.get('sd')
    observations = aggregate.get('observations')
    measurement = _new_measurement(term, value)
    _set_dict_array(measurement, 'observations', observations)
    _set_dict_array(measurement, 'min', min)
    _set_dict_array(measurement, 'max', max)
    _set_dict_array(measurement, 'sd', sd, True)
    if node.get('depthUpper') is not None:
        measurement['depthUpper'] = node.get('depthUpper')
    if node.get('depthLower') is not None:
        measurement['depthLower'] = node.get('depthLower')
    return _aggregated_version(measurement, 'min', 'max', 'sd', 'observations', 'depthUpper', 'depthLower')


def _format_results(results: tuple):
    aggregates, data = results
    sites = data.get('nodes', [])
    return {
        **_create_site(sites[0]),
        'measurements': list(map(_format_aggregate, aggregates))
    } if len(sites) > 0 else None


def _site_id(n: dict, include_siteType: bool):
    return '-'.join(non_empty_list([
        _format_country_name(n.get('country', {}).get('name')),
        n.get('siteType') if include_siteType else None
    ]))


def _site_name(n: dict, include_siteType: bool):
    return ' - '.join(non_empty_list([
        n.get('country', {}).get('name'),
        n.get('siteType') if include_siteType else None
    ]))


def _create_site(data: dict, include_siteType=True):
    site = {'type': SchemaType.SITE.value}
    site['country'] = data['country']
    site['siteType'] = data['siteType']
    site['name'] = _site_name(site, include_siteType)
    site['id'] = _site_id(site, include_siteType)
    site['dataPrivate'] = False
    return _aggregated_node(site)


def _update_site(country_name: str, source: dict = None, include_siteType=True):
    def update(site: dict):
        site['country'] = _update_country(country_name) if country_name else site.get('country')
        site['name'] = _site_name(site, include_siteType)
        site['id'] = _site_id(site, include_siteType)
        return site if source is None else {**site, 'defaultSource': source}
    return update


def _group_by_measurement(group: dict, node: dict):
    key = '-'.join(non_empty_list([
        node.get('term', {}).get('@id'),
        str(node.get('depthUpper', '')),
        str(node.get('depthLower', ''))
    ]))
    if key not in group:
        group[key] = []
    group[key].append(node)
    return group


def _group_by_measurements(sites: list):
    def group_by(group: dict, site: dict):
        group['site']['nodes'].append(site)
        measurements = list(map(
            lambda v: {
                **v,
                'country': site.get('country')
            }, site.get('measurements', [])))
        group['site']['measurements'] = reduce(_group_by_measurement, measurements, group['site']['measurements'])
        return group
    return reduce(group_by, sites, {'site': {'nodes': [], 'measurements': {}}})
