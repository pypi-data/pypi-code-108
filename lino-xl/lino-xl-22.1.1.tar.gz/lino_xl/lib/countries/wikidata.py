# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# Copyright 2021 8lurry
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""

CLI:

Examples:
-- languages "en fr de nl bn"

Usage::

  $ go xl
  $ inv updatefixtures

Status:

This is not yet being used anywhere. The results are not yet stable enough
because wikidata structure is chaotic and differs by country. We do not yet have
the type of each place.  If we get things more reliable, then the next step
would be easier: add a `Site.use_wikidata` attribute and read the json files in
the :fixture:`all_countries` fixture (and the `be` and `ee` fixtures, which are
expected load the places)



"""

import os
import requests
import json
import datetime
dt = datetime.datetime

import logging

logger = logging.getLogger(__name__)

from pathlib import Path
from pprint import pprint
from jinja2 import Template

class CountryNotFoundError(Exception):
    pass

url = "https://query.wikidata.org/sparql"

class WD:

    file_dir = Path(os.path.abspath(__file__)).parent

    countries = None
    cities = None
    not_found_threshold = 15
    max_depth = 100

    class Properties:
        instance_of = "P31"
        subclass_of = "P279"
        country = "P17"
        series_ordinal = "P1545"
        iso_3166_1_alpha_2_code = "P297"
        iso_3166_1_alpha_3_code = "P298"
        postal_code = "P281"
        contains_administrative_territorial_entity = "P150"
        located_in_the_administrative_territorial_entity = "P131"

    p = Properties

    country = "Q6256"
    sovereign_state = "Q3624078"
    city = "Q515"
    human_settlement = "wd:Q486972"
    administrative_subdivisions = ['Q10864048', 'Q13220204', 'Q13221722', 'Q14757767', 'Q15640612', 'Q22927291']
    first_level_administrative_country_subdivision = "Q10864048"
    second_level_administrative_country_subdivision = "Q13220204"
    third_level_administrative_country_subdivision = "Q13221722"
    fourth_level_administrative_country_subdivision = "Q14757767"
    fifth_level_administrative_country_subdivision = "Q15640612"
    sixth_level_administrative_country_subdivision = "Q22927291"
    administrative_territorial_entity_of_a_specific_level = "Q1799794"

iso2wikidata = {
    'ee': 'Q191',
    'bd': 'Q902',
    'be': 'Q31',
    'ca': 'Q16'
}


def write_wdqs_json(obj, file):
    with open(file, 'w') as f:
        json.dump(obj, f)

def read_wdqs_json(file):
    with open(file, 'r') as f:
        obj = json.load(f)
    return obj

def query_wdqs(query):
    resp = requests.get(url, params={'format': 'json', 'query': query})
    if resp.status_code == 429:
        return []
    return resp.json()['results']['bindings']

def parse_object(obj, languages=[]):
    if 'en' in languages:
        languages.remove('en')

    name = obj['entityLabel']['value'] # .lower()
    c = dict(
        name=name,
        entity=obj['entity']['value'].split('entity')[1].split('/')[1]
    )

    isoCode3 = obj.get('isoCode3', None)
    if isoCode3 is not None:
        c['isoCode3'] = isoCode3['value']

    isoCode2 = obj.get('isoCode2', None)
    if isoCode2 is not None:
        c['isoCode2'] = isoCode2['value']

    desc = obj.get('entityDescription', None)
    if desc is not None:
        c['description'] = desc['value']

    zipCode = obj.get('zipCode', None)
    if zipCode is not None:
        c['zipCode'] = zipCode['value']

    for lang in languages:
        c['name_' + lang] = obj['entity_' + lang]['value'] # .lower()
        desc = obj.get('entityDesc_' + lang, None)
        if desc is not None:
            c['description_' + lang] = desc['value']

    return name, c

def build_query(languages=[], entity='country', of=None, **kw):
    if 'en' in languages:
        languages.remove('en')

    select = "SELECT ?entity ?entityLabel ?entityDescription"

    if entity == 'country':
        select += " ?isoCode2 ?isoCode3"
    if entity in ['human_settlement', 'admin_entity_contains']:
        select += " ?zipCode"

    for lang in languages:
        select += " ?entity_" + lang + " ?entityDesc_" + lang

    select += "\n"

    where = "WHERE {\n"

    if entity != "admin_entity_contains":
        where += "\t?entity (wdt:"+WD.p.instance_of+"|wdt:"+WD.p.subclass_of+") wd:"

    if entity == 'country':
        where += WD.sovereign_state + ".\n\t?entity wdt:P297 ?isoCode2.\n"
        where += "\t?entity wdt:P298 ?isoCode3.\n"
    elif of is None:
        raise ValueError("Parameter of cannot be None.")
    elif entity == 'city':
        where += WD.city+".\n\t?entity wdt:P17 wd:"+of+".\n"
    elif entity == 'country_subdivision':
        series_ordinal = kw.get('series_ordinal', None)
        if series_ordinal is None:
            raise KeyError("series_ordinal must be provided is an argument.")
        where += (
            WD.administrative_subdivisions[series_ordinal]+".\n"+
            "\t?entity wdt:P17 wd:"+of+".\n"
        )
    elif entity == 'human_settlement':
        subdivision = kw.get('subdivision', None)
        if subdivision is None:
            raise KeyError("subdivision must be provided is an argument.")
        where += (
            subdivision+".\n"+
            "\t?entity wdt:P17 wd:" + of + ".\n" +
            "\tOPTIONAL {?entity wdt:P281 ?zipCode.}\n"
        )
    elif entity in ['admin_entity_contains']:
        where += (
            "\t?entity wdt:P131 wd:" + of + ".\n" +
            "\tOPTIONAL {?entity wdt:P281 ?zipCode.}\n"
        )
    else:
        raise ValueError('Value of entity must be one of the following:\n'+
        '"country", "city", "country_subdivision" or "human_settlement".')

    where += "\tSERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }\n"

    if languages:
        where += "\tOPTIONAL {\n"
        for lang in languages:
            where += ("\t\tSERVICE wikibase:label {\n"+
                    "\t\t\tbd:serviceParam wikibase:language '"+lang+"'.\n"+
                    "\t\t\t?entity rdfs:label ?entity_"+lang+".\n"+
                    "\t\t\t?entity schema:description ?entityDesc_"+lang+".\n"+
                "\t\t} hint:Prior hint:runLast false.\n")
        where += "\t}\n"

    where += "}"

    return select+where

def _update_countries(filepath, languages=[]):
    print("Getting countries data from WDQS server.")
    q = build_query(languages=languages, entity='country')
    resp = query_wdqs(q)

    countries = dict()
    isoMap = dict()

    for country in resp:
        isoCode2 = country['isoCode2']['value'].lower()
        name, c = parse_object(country, languages)
        countries[isoCode2] = c
        isoMap[name.lower().replace(' ', '_')] = isoCode2

    if 'en' not in languages:
        languages += ['en']
    obj = dict(
        title='countries',
        languages=languages,
        updated=dt.timestamp(dt.utcnow()),
        timeZone='UTC',
        isoMap=isoMap,
        data=countries)

    write_wdqs_json(obj, filepath)
    WD.countries = obj

    return obj

def get_countries(languages=[], filename='countries.json', force_update=False):
    languages = [lang.split('-')[0] for lang in languages]
    filepath = WD.file_dir / filename
    if not force_update:
        if WD.countries is None:
            if os.path.isfile(filepath):
                print("Read countries data from file: " + str(filepath) + ".")
                obj = read_wdqs_json(filepath)
                WD.countries = obj
        if WD.countries is not None:
            obj = WD.countries
            new_langs = [lang for lang in languages if lang not in obj['languages']]
            if new_langs:
                languages = obj['languages'] + new_langs
                return _update_countries(filepath, languages)
            return obj
    return _update_countries(filepath, languages)

def country_lookup(iso, languages=[]):
    countries = get_countries(languages=languages)
    if len(iso) > 2:
        c = countries['isoMap'].get(iso.lower().replace(' ', '_'), None)
        if iso is None:
            raise CountryNotFoundError("Country code (iso) was not found in the data elements for the country: "+iso)
        else:
            iso = c
    c_data = countries['data'].get(iso.lower(), None)
    if c_data is not None:
        entity = c_data['entity']
    elif iso2wikidata.get(iso.lower(), False):
        entity = iso2wikidata[iso.lower()]
    else:
        raise CountryNotFoundError("Country was not found in the data elements for the iso code: "+iso)
    return entity

def _query_cities(entity, languages=[]):
    q = build_query(languages=languages, entity='city', of=entity)
    resp = query_wdqs(q)

    cities = dict()
    for city in resp:
        name, c = parse_object(city, languages)
        cities[name.lower().replace(" ", '_')] = c
    return cities

def get_cities(of=[], languages=[], filename='cities.json', force_update=False):
    languages = [lang.split('-')[0] for lang in languages]
    filepath = WD.file_dir / filename
    results = dict()
    if not force_update and os.path.isfile(filepath):
        obj = read_wdqs_json(filepath)
        if not of:
            return obj
        new_langs = [lang for lang in languages if lang not in obj['languages']]
        languages = new_langs + obj['languages']
        for iso in of:
            entity = country_lookup(iso, languages)
            if iso not in obj['countries']:
                print("Getting cities data from WDQS server for ",
                    entity+":"+iso, " (iso code)")
                cities = _query_cities(entity, languages)
                obj['countries'].append(iso)
                obj['updated'] = dt.timestamp(dt.utcnow())
            elif new_langs:
                print("Getting cities data from WDQS server for ",
                    entity+":"+iso, " (iso code)")
                cities = _query_cities(entity, languages)
            else:
                print("Read cities data from " + str(filepath) + " for ",
                    entity+":"+iso, " (iso code)")
                cities = obj['data'][iso]
            results[iso] = cities
        obj['languages'] = languages
        obj['data'].update(results)
        write_wdqs_json(obj, 'cities.json')
        return results
    else:
        if not of:
            raise ValueError("Parameter of cannot be empty.")
        country_codes = []
        for iso in of:
            entity = country_lookup(iso, languages)
            country_codes.append(iso)
            print("Getting cities data from WDQS server for",
                entity+":"+iso, "(iso code)")
            cities = _query_cities(entity, languages)
            results[iso] = cities

        if 'en' not in languages:
            languages += ['en']

        obj = dict(
            title='cities',
            languages=languages,
            countries=country_codes,
            updated=dt.timestamp(dt.utcnow()),
            timeZone='UTC',
            data=results,
        )
        write_wdqs_json(obj, 'cities.json')
        return obj

def _query_subdivisions(country, languages=[], query_by='bulk'):
    subdivisions = dict()
    subdivisionLevelMap = dict()
    if query_by in ['bulk', 'subdivision']:
        for i in range(1, 7):
            q = build_query(languages=languages, entity='country_subdivision',
                of=country, series_ordinal=i-1)
            resp = query_wdqs(q)
            if not len(resp):
                continue
            else:
                if len(resp) == 1:
                    _, subdivision = parse_object(resp[0], languages=languages)
                else:
                    subdivision = dict(name='Unknown', entity='Unknown')
                arias = dict()
                print(("Getting places by 'country subdivision' " +
                    "within subdivision: {name: " + subdivision['name'] +
                    ", level: " + str(i) + "} from WDQS server."))
                for sd in resp:
                    name, sda = parse_object(sd, languages=languages)
                    if len(resp) > 1:
                        arias[name.lower().replace(' ', '_')] = sda
                    q = build_query(languages=languages, entity='human_settlement',
                        of=country, subdivision=sda['entity'])
                    rsp = query_wdqs(q)
                    for aria in rsp:
                        name, a = parse_object(aria, languages=languages)
                        arias[name.lower().replace(' ', '_')] = a
                subdivision['data'] = arias
                subdivisions[str(i)] = subdivision
                if len(resp) == 1:
                    subdivisionLevelMap[subdivision['name']] = i

    if query_by in ['bulk', 'admin_entity']: # This is expensive
        def query_ad_ety(ety, name, controller):
            q = build_query(languages=languages, entity='admin_entity_contains',
                of=ety)
            print(("Getting places by 'administrative entity cotaining' " +
                "within administrative entity: " + ety + ":" + name +
                " of subdivision level: " + str(controller['level']) +
                " from WDQS server."))
            resp = query_wdqs(q)
            controller_child = dict(
                level=controller['level'] + 1,
                not_found_threshold = WD.not_found_threshold
            )

            subdivision = subdivisions.get(str(controller['level']), None)
            if subdivision is None:
                subdivision = dict(data=dict(), name='Unknown', entity='Unknown')
            for adety in resp:
                name, ety = parse_object(adety, languages=languages)
                subdivision['data'][name.lower().replace(' ', '_')] = ety
                if controller_child['not_found_threshold'] != 0 and WD.max_depth > controller['level']:
                    query_ad_ety(ety['entity'], name, controller_child)
                elif WD.max_depth == 100:
                    WD.max_depth = controller['level']
            if len(resp):
                subdivisions[str(controller['level'])] = subdivision
            elif controller['not_found_threshold'] > 0:
                controller['not_found_threshold'] -= 1

        controller = dict(level=1, not_found_threshold=WD.not_found_threshold)
        query_ad_ety(country, 'country', controller)
        WD.max_depth = 100

    if 'en' not in languages:
        languages += ['en']
    obj = dict(
        title='human_settlements',
        languages=languages,
        updated=dt.timestamp(dt.utcnow()),
        timeZone='UTC',
        data=subdivisions,
        subdivisionLevelMap=subdivisionLevelMap)
    return obj

def get_human_settlements(
        of, series_ordinal=-1, languages=[], filename=None, force_update=False):

    languages = [lang.split('-')[0] for lang in languages]
    country = country_lookup(of, languages)

    if filename is None:
        filepath = WD.file_dir / ("human_settlements_in_"+of+".json")
    else:
        filepath = WD.file_dir / filename

    def ready_resp(langs):
        print("Getting places within ", country, ":", of,
            " (iso code) from WDQS server.")
        obj = _query_subdivisions(country, langs)
        obj['country'] = of
        write_wdqs_json(obj, filepath)
        return obj

    if not force_update and os.path.isfile(filepath):
        obj = read_wdqs_json(filepath)
        new_langs = [lang for lang in languages if lang not in obj['languages']]
        if new_langs:
            languages = obj['languages'] + new_langs
            return ready_resp(languages)
        elif series_ordinal == -1:
            print("Read places within " + of + " (iso code) from file: " + str(filepath))
            return obj
        else:
            print(("Read places within " + of +
                " (iso code) of subdivision level: " + series_ordinal +
                " from file: " + str(filepath)))
            return obj[series_ordinal-1]
    else:
        return ready_resp(languages)


if __name__ == "__main__":
    languages = ['en', 'fr']
    # get_cities(['bd', 'de'], languages=languages)
    # for iso_code in ['bd', 'de', 'ee', 'be']:
    #     get_human_settlements(iso_code, languages=languages)
    # get_human_settlements('be', languages=languages)
    # get_countries(languages)
    # _query_subdivisions(country_lookup('ee'), query_by='admin_entity')
