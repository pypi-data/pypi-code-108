# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import hashlib
import math
import urllib.parse
from abc import ABC
from enum import Enum
from http import HTTPStatus
from typing import Tuple, List, Dict, Set, Any

import dateutil.parser
import requests
from qwikidata.entity import WikidataItem, WikidataClaimGroup, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api, InvalidEntityId
from qwikidata.sparql import get_subclasses_of_item
from qwikidata.typedefs import PropertyId, ItemId, LanguageCode

from knowledge.public import PROPERTY_MAPPING
from knowledge.utils.wikipedia import get_wikipedia_summary, get_wikipedia_summary_url


class WikiDataAPIException(Exception):
    pass


# OntologyPropertyReference constants
INSTANCE_OF_PROPERTY: str = 'P31'
IMAGE_PROPERTY: str = 'P18'
API_LIMIT: int = 50

THUMB_IMAGE_URL: str = 'https://upload.wikimedia.org/wikipedia/commons/thumb/{}/{}/{}/200px-{}'
MULTIPLE_ENTITIES_API: str = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&languages={}&format=json'


class Precision(Enum):
    """
    Precision enum for date.
    """
    BILLION_YEARS = 0
    MILLION_YEARS = 3
    HUNDREDS_THOUSAND_YEARS = 4
    MILLENIUM = 6
    CENTURY= 7
    DECADE = 8
    YEAR = 9
    MONTH = 10
    DAY = 11


# Wikidata Properties
STUDENT_OF: str = 'P1066'
STUDENT: str = 'P802'
INCEPTION: str = 'P571'
MOVEMENT: str = 'P135'
SUBCLASS_OF: str = 'P279'
TITLE: str = 'P1476'
COLLECTION: str = 'P195'
GENRE: str = 'P136'
CREATOR: str = 'P170'
LOGO_IMAGE: str = 'P154'
FLAG_IMAGE: str = 'P41'
GREGORIAN_CALENDAR: str = 'Q1985727'
START_TIME: str = 'P580'
END_TIME: str = 'P582'
FOLLOWS: str = 'P155'
FOLLOWED_BY: str = 'P156'
COUNTRY_OF_ORIGIN: str = 'P495'
COUNTRY: str = 'P17'
INSTANCE_OF: str = 'P31'
IMAGE: str = 'P18'
# URL - Wikidata
GREGORIAN_CALENDAR_URL: str = 'http://www.wikidata.org/entity/Q1985786'
# Template of wikidata entity
WIKIDATA_ORG_WIKI_TEMPLATE: str = 'https://www.wikidata.org/wiki/{}'
# URL - Wikidata service
WIKIDATA_SPARQL_URL: str = "https://query.wikidata.org/sparql"


def wikidate(param: Dict[str, Any]) -> dict:
    """
    Parse and extract wikidata structure.
    Parameters
    ----------
    param: Dict[str, Any]
        Entity wikidata

    Returns
    -------
    result: Dict[str, Any]
        Dict with pretty print of date
    """
    time: str = param['values'][0]['time']
    timezone: int = param['values'][0]['timezone']
    before: int = param['values'][0]['before']
    after: int = param['values'][0]['after']
    precision: int = param['values'][0]['precision']
    calendar_model: str = param['values'][0]['calendarmodel']
    after_christ: bool = True
    pretty: str = ''
    if time.startswith('+'):
        time = time[1:]
    elif time.startswith('-'):
        time = time[1:]
        after_christ = False
    # Probably not necessary
    date_str = time.strip()
    # Remove + sign
    if date_str[0] == '+':
        date_str = date_str[1:]
    # Remove missing month/day
    date_str = date_str.split('-00', maxsplit=1)[0]
    # Parse date
    dt = dateutil.parser.parse(date_str)
    if Precision.BILLION_YEARS.value == precision:
        pass
    elif Precision.MILLION_YEARS.value == precision:
        pass
    elif Precision.HUNDREDS_THOUSAND_YEARS.value == precision:
        pass
    elif Precision.MILLENIUM.value == precision:
        pass
    elif Precision.CENTURY.value == precision:
        century: int = int(math.ceil(dt.year / 100))
        pretty = '{}th century'.format(century)
    elif Precision.DECADE.value == precision:
        pretty = '{}s{}'.format(dt.year, '' if after_christ else ' BC')
    elif Precision.YEAR.value == precision:
        pretty = '{}{}'.format(dt.year, '' if after_christ else ' BC')
    elif Precision.MONTH.value == precision:
        pretty = dt.strftime("%B %Y")
    elif Precision.DAY.value == precision:
        pretty = dt.strftime("%-d %B %Y")
    return {
        'time': time,
        'timezone': timezone,
        'before': before,
        'after': after,
        'precision': precision,
        'calendarmodel': calendar_model,
        'pretty': pretty
    }


class WikiDataAPIClient(ABC):
    """WikiData API client.
    """
    ACTIVATION_RELATIONS = [
        'P625',  # coordinate location',
        'P31',  # instance of',
        'P527',  # 'has part',
        'P361',  # 'part of',
        'P856',  # 'official website',
        'P47',  # 'shares border with',
        'P6',  # 'head of government',
        'P1082',  # 'population',
        'P421',  # 'located in timezone',
        'P17',  # 'country',
        'P910',  # 'topics main category',
        'P373',  # 'Commons category',
        'P901',  # 'FIPS 10-4 (countries and regions)',
        'P948',  # 'page banner',
        'P646',  # 'Freebase ID',
        'P1376',  # 'capital of',
        'P1814',  # 'name in kana',
        'P571',  # 'inception',
        'P2046',  # 'area',
        'P163',  # 'flag',
        'P2044',  # 'elevation above sea level',
        'P610',  # 'highest point',
        'P1365',  # 'replaces',
        'P36',  # 'capital',
        'P6794',  # 'minimum wage',
        'P18',  # 'image',
        # Person
        'P21',  # 'sex or gender',
        'P345',  # 'IMDb ID',
        'P27',  # 'country of citizenship',
        'P19',  # 'place of birth',
        'P569',  # 'date of birth',
        'P106',  # 'occupation',
        'P102',  # 'political party',
        'P166',  # 'award received',
        'P2002',  # 'Twitter username',
        'P26',  # 'spouse',
        'P735',  # 'given name',
        'P734',  # 'family name',
        'P1412',  # 'languages spoken, written or signed',
        'P69',  # 'educated at',
        'P1559',  # 'name in native language_code',
        'P1477',  # 'birth name',
        'P103',  # 'native language_code',
        'P793',  # 'significant event',
        'P2003',  # 'Instagram username',
        'P1340',  # 'eye color',
        'P1884',  # 'hair color',
        'P2048',  # 'height',
        'P2067',  # 'mass',
        'P108',  # 'employer',
        'P800',  # 'notable work',
        'P10',  # 'video',
        'P1971',  # 'number of children',
        'P91'  # 'sexual orientation'
    ]

    PROPERTY_OFFICIAL_WEBSITE: str = 'P856'
    PROPERTY_PERSON_FIRSTNAME: str = 'P735'
    PROPERTY_PERSON_LASTNAME: str = 'P734'

    def __init__(self):
        self.PROPERTIES = list(WikiDataAPIClient.ACTIVATION_RELATIONS)

    @staticmethod
    def image_url(img: str):
        extension: str = ''
        conversion: str = ''
        fixed_img: str = img.replace(' ', '_')
        if fixed_img.lower().endswith('svg'):
            extension: str = '.png'
        if fixed_img.lower().endswith('tif') or fixed_img.lower().endswith('tiff'):
            extension: str = '.jpg'
            conversion: str = 'lossy-page1-'
        hash_img = hashlib.md5(fixed_img.encode('utf-8')).hexdigest()
        url_img_part: str = urllib.parse.quote_plus(fixed_img)
        return THUMB_IMAGE_URL.format(hash_img[0], hash_img[:2], url_img_part, conversion + url_img_part + extension)

    @staticmethod
    def wikipedia_url(wikidata_id: str, lang: str = 'en'):
        url: str = 'https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks/urls&ids={}&format=json' \
            .format(wikidata_id)
        json_response = requests.get(url).json()
        entities: dict = json_response['entities']
        if entities:
            entity: dict = entities[wikidata_id]
            if entity:
                sitelinks: dict = entity['sitelinks']
                if sitelinks:
                    # filter only the specified language_code
                    sitelink: str = sitelinks.get(f'{lang}wiki')
                    if sitelink:
                        wiki_url = sitelink.get('url')
                        if wiki_url:
                            return requests.utils.unquote(wiki_url)
        return None

    @staticmethod
    def __entity_image__(entity: WikidataItem):
        p: WikidataClaimGroup = entity.get_claim_group(PropertyId(IMAGE_PROPERTY))
        if len(p) > 0 and p[0].mainsnak.datavalue:
            img: str = p[0].mainsnak.datavalue.value.replace(' ', '_')
            return WikiDataAPIClient.image_url(img)
        return ''

    @staticmethod
    def __entity_image_dict__(prop: List[dict]):
        if len(prop) > 0:
            img: str = prop[0]['mainsnak']['datavalue']['value'].replace(' ', '_')
            return WikiDataAPIClient.image_url(img)
        return ''

    @staticmethod
    def __entity_type__(entity: WikidataItem) -> str:
        p: WikidataClaimGroup = entity.get_claim_group(PropertyId('P31'))
        if len(p) > 0:
            type_entity = p[0].mainsnak.datavalue.value['id']
            return type_entity
        return ''

    @staticmethod
    def __entity_type_dict__(entity: dict) -> set:
        if INSTANCE_OF_PROPERTY in entity:
            props: dict = entity[INSTANCE_OF_PROPERTY]
            if len(props) > 0:
                return set([p['mainsnak']['datavalue']['value']['id'] for p in props])
        return set()

    @staticmethod
    def __entity_type_obj__(entity: WikidataItem) -> Set[str]:
        props: WikidataClaimGroup = entity.get_claim_group(PropertyId(INSTANCE_OF_PROPERTY))
        if len(props) > 0:
            return set([p.mainsnak.datavalue.value['id'] for p in props])
        return set()

    @staticmethod
    def __data_type__(prop: list):
        return prop[0]['mainsnak']['datatype']

    @staticmethod
    def __entity_id__(prop: list):
        if len(prop) > 0:
            if 'datavalue' in prop[0]['mainsnak']:
                return prop[0]['mainsnak']['datavalue']['value']['id']
        return None

    @staticmethod
    def __value__(prop: list):
        data_type: str = WikiDataAPIClient.__data_type__(prop)
        val = None
        if 'datavalue' in prop[0]['mainsnak']:
            if data_type == 'monolingualtext':
                val = prop[0]['mainsnak']['datavalue']['value']['text']
            elif data_type in ['string', 'external-id', 'url']:
                val = prop[0]['mainsnak']['datavalue']['value']
            elif data_type == 'commonsMedia':
                val = WikiDataAPIClient.__entity_image_dict__(prop)
            elif data_type == 'time':
                val = prop[0]['mainsnak']['datavalue']['value']['time']
            elif data_type == 'quantity':
                if 'amount' in prop[0]['mainsnak']['datavalue']['value']:
                    val = '{} {}'.format(prop[0]['mainsnak']['datavalue']['value']['amount'],
                                         prop[0]['mainsnak']['datavalue']['value']['unit'])

            elif data_type == 'wikibase-lexeme':
                val = prop[0]['mainsnak']['datavalue']['value']['id']
            elif data_type in ['geo-shape', 'wikibase-property']:
                # Not supported
                val = None
            elif data_type == 'globe-coordinate':
                val = {
                    'longitude': prop[0]['mainsnak']['datavalue']['value']['longitude'],
                    'latitude': prop[0]['mainsnak']['datavalue']['value']['latitude'],
                    'altitude': prop[0]['mainsnak']['datavalue']['value']['altitude']
                }
            else:
                raise WikiDataAPIException(f"Unkown type {data_type}")
        return val

    @staticmethod
    def __entity_to_dict__(entity: WikidataItem, language: LanguageCode = LanguageCode('en')) -> Dict[str, Any]:
        type_uris: set = WikiDataAPIClient.__entity_type_obj__(entity)
        return {
            'uri': entity.entity_id,
            'label': entity.get_label(language),
            'description': entity.get_description(language),
            'alias': entity.get_aliases(language),
            'image': WikiDataAPIClient.__entity_image__(entity),
            'types': type_uris
        }

    @staticmethod
    def __entity_to_dict_lang__(entity: WikidataItem, languages: List[LanguageCode]) -> Dict[str, Any]:
        type_uris: Set[str] = WikiDataAPIClient.__entity_type_obj__(entity)
        image: str = WikiDataAPIClient.__entity_image__(entity)
        return {
            'uri': entity.entity_id,
            'label': dict([(lang, entity.get_label(lang)) for lang in languages]),
            'description': dict([(lang, entity.get_description(lang)) for lang in languages]),
            'alias': dict([(lang, entity.get_aliases(lang)) for lang in languages]),
            'image': image,
            'types': type_uris
        }

    @staticmethod
    def __pull_entities__(language: str, uris: list):
        query = '|'.join(map(str, uris))
        response = requests.get(MULTIPLE_ENTITIES_API.format(query, language))
        if response.status_code != HTTPStatus.OK:
            raise WikiDataAPIException('Response return has not been successful. [HTTP Code:={}]'
                                       .format(response.status_code))
        return response.json()

    @staticmethod
    def __label__(v: dict, language: str):
        if 'labels' in v and language in v['labels']:
            return v['labels'][language]['value']
        return ''

    @staticmethod
    def __description__(v: dict, language: str):
        if 'descriptions' in v and language in v['descriptions']:
            return v['descriptions'][language]['value']
        return ''

    @staticmethod
    def __extract_entities__(result: dict, language: str, add_literals: bool = True, add_relations: bool = False):
        relations: list = []
        entities: list = []
        missing_entities: set = set()
        for qid, v in result['entities'].items():
            # Extracting the properties
            if IMAGE_PROPERTY in v['claims']:
                image_url: str = WikiDataAPIClient.__entity_image_dict__(v['claims'][IMAGE_PROPERTY])
            else:
                image_url: str = ''
            type_uris: set = WikiDataAPIClient.__entity_type_dict__(v['claims'])
            label: str = WikiDataAPIClient.__label__(v, language)
            description: str = WikiDataAPIClient.__description__(v, language)
            # Collect the literals for entity
            literals: dict = {}
            # Now iterate over claims
            for pid, value in v['claims'].items():
                if pid in WikiDataAPIClient.ACTIVATION_RELATIONS:
                    if WikiDataAPIClient.__data_type__(value) == 'wikibase-item':
                        # Extract the relations
                        if add_relations:
                            t_qid = WikiDataAPIClient.__entity_id__(value)
                            if pid in PROPERTY_MAPPING and t_qid:
                                missing_entities.add(t_qid)
                                relations.append({'property': pid,
                                                  'subject': qid, 'predicate': PROPERTY_MAPPING[pid], 'object': t_qid})
                    else:
                        # Extract the literals
                        if add_literals:
                            if pid in PROPERTY_MAPPING:
                                # Collect literals
                                literals[pid] = {
                                    'uri': pid,
                                    'label': PROPERTY_MAPPING[pid],
                                    'value': WikiDataAPIClient.__value__(value)
                                }

            # Adding entity to result list
            entities.append({'uri': qid, 'label': label, 'description': description,
                             'image': image_url,
                             'literals': literals})
        return entities, relations, missing_entities

    def activations(self, uris: list, language: str = 'en') -> tuple:
        """Activations of URIs
        :param uris: list of URIs
        :param language: language_code of entity
        :return: list of entities, list of relations
        """
        result = self.__pull_entities__(language, uris)
        entities, relations, missing_entities = WikiDataAPIClient.__extract_entities__(result, language,
                                                                                       add_literals=True,
                                                                                       add_relations=True)
        jobs = list(missing_entities)
        # pull missing entities
        while len(jobs) > 0:
            result_other = self.__pull_entities__(language, jobs[:API_LIMIT])
            more_entities, _, _ = WikiDataAPIClient.__extract_entities__(result_other, language,
                                                                         add_literals=True,
                                                                         add_relations=False)
            entities.extend(more_entities)
            del jobs[:API_LIMIT]
        return entities, relations

    def entity(self, qid: str, language: str = 'en', pull_wiki_content: bool = False) -> dict:
        """Get entity information from public including relations

        :param qid: QID representing the entity in the public knowledge graph
        :param language: language_code for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information
        """
        entity_dict = get_entity_dict_from_api(ItemId(qid))
        entity = WikidataItem(entity_dict)
        entity_dict: dict = self.__entity_to_dict__(entity, language=LanguageCode(language))
        if pull_wiki_content:
            url: str = WikiDataAPIClient.wikipedia_url(qid)
            if url:
                summary: dict = get_wikipedia_summary_url(url)
                entity_dict['image'] = summary['summary-image']
                entity_dict['description'] = summary['summary-text']
                entity_dict['wikiurl'] = url
        return entity_dict

    def entity_lang(self, qid: ItemId, languages: List[LanguageCode] = None, pull_wiki_content: bool = False) -> dict:
        """Get entity information from public including relations

        :param qid: str -
         QID representing the entity in the public knowledge graph
        :param languages: List[str] -
            List of languages for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information
        """
        entity_dict = get_entity_dict_from_api(qid)
        entity = WikidataItem(entity_dict)
        entity_dict: dict = self.__entity_to_dict_lang__(entity, languages=languages)
        if pull_wiki_content:
            entity_dict['wikiurl'] = {}
            for lang in languages:
                url: str = WikiDataAPIClient.wikipedia_url(qid, lang)
                if url:
                    summary: dict = get_wikipedia_summary_url(url, lang)
                    if len(summary['summary-image']) > 0:
                        entity_dict['image'] = summary['summary-image']
                    if len(summary['summary-text']) > 0:
                        entity_dict['description'][lang] = summary['summary-text']
                    entity_dict['wikiurl'][lang] = url
        return entity_dict

    def entity_rels(self, qid: str, language: str = 'en', pull_wiki_content: bool = False) -> Tuple[dict, dict]:
        """Get entity information from public including relations

        :param qid: QID representing the entity in the public knowledge graph
        :param language: language_code for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information
        """
        entity_dict: dict = get_entity_dict_from_api(ItemId(qid))
        entity: WikidataItem = WikidataItem(entity_dict)
        properties: dict = {}
        for p, claim_group in entity.get_truthy_claim_groups().items():
            literal = [
                claim.mainsnak.datavalue.value
                for claim in claim_group
                if claim.mainsnak.snaktype == "value"
            ]
            properties[p] = {
                'property-label': WikiDataAPIClient.property(p, LanguageCode(language)),
                'values': literal
            }
        entity_result: dict = self.__entity_to_dict__(entity, language=LanguageCode(language))
        wikiurl: dict = entity.get_sitelinks(f'{language}wiki')
        if len(wikiurl) > 0 and f'{language}wiki' in wikiurl:
            url: str = wikiurl[f'{language}wiki']['url']
            title: str = wikiurl[f'{language}wiki']['title']
            entity_result['wikiurl'] = url
            if pull_wiki_content:
                summary: dict = get_wikipedia_summary(title)
                # Only update if there is a meaningful update
                img: str = summary['summary-image']
                if img:
                    entity_result['image'] = img
                abstract: str = summary['summary-text']
                if abstract:
                    entity_result['description'] = abstract
        return entity_result, properties

    def entity_rels_lang(self, qid: str, languages: List[LanguageCode] = None, pull_wiki_content: bool = False,
                         default_language: str = 'en') -> tuple:
        """Get entity information from public including relations.

        :param qid: str -
            QID representing the entity in the public knowledge graph
        :param languages: List[str] -
            List of languages for text
        :param pull_wiki_content: bool -
            Pulling extended description and summary
        :param default_language: str -
            Default language_code
        :return: dict with relevant information
        """
        entity_dict: dict = get_entity_dict_from_api(ItemId(qid))
        entity: WikidataItem = WikidataItem(entity_dict)
        properties: Dict[str, dict] = {}
        # Properties
        for p, claim_group in entity.get_truthy_claim_groups().items():
            literal: List = [
                claim.mainsnak.datavalue.value
                for claim in claim_group
                if claim.mainsnak.snaktype == "value"
            ]
            properties[p] = {
                'property-label': WikiDataAPIClient.property(p, default_language),
                'values': literal
            }
        entity_result: dict = self.__entity_to_dict_lang__(entity, languages=languages)
        for lang in languages:
            wiki_url: dict = entity.get_sitelinks(f'{lang}wiki')
            if len(wiki_url) > 0 and f'{lang}wiki' in wiki_url:
                if 'wikiurl' not in entity_result:
                    entity_result['wikiurl'] = {}
                url: str = wiki_url[f'{lang}wiki']['url']
                title: str = wiki_url[f'{lang}wiki']['title']
                entity_result['wikiurl'][lang] = url
                if pull_wiki_content:
                    summary: dict = get_wikipedia_summary(title, lang)
                    # Only update if there is a meaningful update
                    img: str = summary['summary-image']
                    if img is not None or img == '':
                        entity_result['image'] = img
                    abstract: str = summary['summary-text']
                    if abstract is not None or abstract == '':
                        entity_result['description'][lang] = abstract
        return entity_result, properties

    def references(self, qid: str, language: str = 'en'):
        references = []
        entity, properties = self.entity_rels(qid, language)
        if WikiDataAPIClient.PROPERTY_OFFICIAL_WEBSITE in properties:
            references.append({'property': properties[WikiDataAPIClient.PROPERTY_OFFICIAL_WEBSITE],
                               'property-label': PROPERTY_MAPPING[WikiDataAPIClient.PROPERTY_OFFICIAL_WEBSITE]})
        return references

    def entities_rel(self, qids: list, language: str = 'en') -> tuple:
        """Return relations and entities for qids.

        :param qids: list of entities in Wikidata
        :param language: language_code the content
        :return: entities, relations
        """
        jobs = list(qids)
        entities: list = []
        relations: list = []
        while len(jobs) > 0:
            result = self.__pull_entities__(language, jobs[:API_LIMIT])
            p_entities, p_relations, _ = WikiDataAPIClient.__extract_entities__(result, language,
                                                                                add_literals=True,
                                                                                add_relations=True)
            del jobs[:API_LIMIT]
            entities.extend(p_entities)
            relations.extend(p_relations)

        return entities, relations

    @staticmethod
    def property(pid: str, language: str = 'en'):
        """Extract property.

        :param pid: property id
        :param language: language_code code for property name
        :return: property nam
        """
        try:
            if pid in PROPERTY_MAPPING:  # only English mappings
                return PROPERTY_MAPPING[pid]
            else:
                prop_dict = get_entity_dict_from_api(PropertyId(pid))
                return WikidataProperty(prop_dict).get_label(LanguageCode(language))
        except InvalidEntityId as e:
            return None

    @staticmethod
    def subclasses(qid: str) -> list:
        """Check for subclasses.

        :param qid: QID of entity
        :return: list of subclasses QIDs
        """
        subclasses_of_uri = get_subclasses_of_item(qid)
        return subclasses_of_uri
