# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nr_oai_pmh_harvester',
 'nr_oai_pmh_harvester.rules',
 'nr_oai_pmh_harvester.rules.nusl',
 'nr_oai_pmh_harvester.rules.uk',
 'nr_oai_pmh_harvester.rules.utils']

package_data = \
{'': ['*']}

install_requires = \
['dojson>=1.4.0,<2.0.0',
 'oarepo-oai-pmh-harvester>=2.0.0-alpha.13,<3.0.0',
 'oarepo-taxonomies>=3.0.0a1,<4.0.0',
 'pycountry>=20.7.3',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'invenio_config.module': ['restoration = nr_oai_pmh_harvester.config'],
 'oarepo_oai_pmh_harvester.error_handlers': ['error_handler = '
                                             'nr_oai_pmh_harvester.error_handler'],
 'oarepo_oai_pmh_harvester.mappings': ['nusl = '
                                       'nr_oai_pmh_harvester.endpoint_handlers'],
 'oarepo_oai_pmh_harvester.parsers': ['parsers = nr_oai_pmh_harvester.parser'],
 'oarepo_oai_pmh_harvester.post_processors': ['post_processors = '
                                              'nr_oai_pmh_harvester.post_processors'],
 'oarepo_oai_pmh_harvester.rules': ['dc_contributor_advisor = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_contributor_advisor',
                                    'dc_contributor_referee = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_contributor_referee',
                                    'dc_creator = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_creator',
                                    'dc_date_issued = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_date_issued',
                                    'dc_description_abstract = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_description_abstract',
                                    'dc_description_department_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_description_department_cs_CZ_value',
                                    'dc_description_faculty_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_description_faculty_cs_CZ_value',
                                    'dc_identifier_uri = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_identifier_uri',
                                    'dc_language_iso = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_language_iso',
                                    'dc_publisher_cs_CS_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_publisher_cs_CS_value',
                                    'dc_publisher_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_publisher_cs_CZ_value',
                                    'dc_subject = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_subject',
                                    'dc_title = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_title',
                                    'dc_type_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dc_type_cs_CZ_value',
                                    'dcterms_dateAccepted_value = '
                                    'nr_oai_pmh_harvester.rules.uk.dcterms_dateAccepted_value',
                                    'field001 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field001',
                                    'field020 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field020',
                                    'field022 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field022__a',
                                    'field035 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field035',
                                    'field04107 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field04107',
                                    'field046__j = '
                                    'nr_oai_pmh_harvester.rules.nusl.field046__j',
                                    'field046__k = '
                                    'nr_oai_pmh_harvester.rules.nusl.field046__k',
                                    'field24500 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field24500',
                                    'field24630 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field24630',
                                    'field24633 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field24633',
                                    'field260 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field260',
                                    'field300 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field300',
                                    'field336__a = '
                                    'nr_oai_pmh_harvester.rules.nusl.field336__a',
                                    'field4900 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field4900',
                                    'field502__c = '
                                    'nr_oai_pmh_harvester.rules.nusl.field502__c',
                                    'field520 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field520',
                                    'field540 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field540',
                                    'field586 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field586',
                                    'field598__a = '
                                    'nr_oai_pmh_harvester.rules.nusl.field598__a',
                                    'field65007 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field65007',
                                    'field65017 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field65017',
                                    'field650_7 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field650_7',
                                    'field653 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field653',
                                    'field656_7a = '
                                    'nr_oai_pmh_harvester.rules.nusl.field656_7a',
                                    'field7102 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field7102',
                                    'field7112 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field7112',
                                    'field720 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field720',
                                    'field7201 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field7201',
                                    'field7731 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field7731',
                                    'field85640 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field85640',
                                    'field85642u = '
                                    'nr_oai_pmh_harvester.rules.nusl.field85642u',
                                    'field909COo = '
                                    'nr_oai_pmh_harvester.rules.nusl.field909COo',
                                    'field970__a = '
                                    'nr_oai_pmh_harvester.rules.nusl.field970__a',
                                    'field980__a = '
                                    'nr_oai_pmh_harvester.rules.nusl.field980__a',
                                    'field996 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field996',
                                    'field998 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field998',
                                    'field999C1 = '
                                    'nr_oai_pmh_harvester.rules.nusl.field999C1',
                                    'others_identifier = '
                                    'nr_oai_pmh_harvester.rules.uk.others_identifier',
                                    'thesis_grade_cs_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.thesis_grade_cs_cs_CZ_value',
                                    'uk_degree_discipline_cs_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_degree_discipline_cs_cs_CZ_value',
                                    'uk_degree_program_cs_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_degree_program_cs_cs_CZ_value',
                                    'uk_file_availability_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_file_availability_value',
                                    'uk_grantor_cs_CS_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_grantor_cs_CS_value',
                                    'uk_grantor_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_grantor_cs_CZ_value',
                                    'uk_publication_place_cs_CS_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_publication_place_cs_CS_value',
                                    'uk_publication_place_cs_CZ_value = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_publication_place_cs_CZ_value',
                                    'uk_publication_place_cs_CZ_value_2 = '
                                    'nr_oai_pmh_harvester.rules.uk.uk_publication_place_cs_CZ_value_2']}

setup_kwargs = {
    'name': 'techlib-nr-oai-pmh-harvester',
    'version': '1.0.0a12',
    'description': 'Czech National Repository oai-pmh-harvester',
    'long_description': '# oai-pmh-harvester\nWrapper that connects oarepo-oai-pmh-harvester with the National Repository.\n',
    'author': 'Daniel Kopecký',
    'author_email': 'Daniel.Kopecky@techlib.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
