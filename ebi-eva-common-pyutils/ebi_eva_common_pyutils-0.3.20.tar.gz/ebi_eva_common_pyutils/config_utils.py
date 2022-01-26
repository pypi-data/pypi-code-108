# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from urllib.parse import quote_plus
from lxml import etree as et
import json
import yaml
import urllib.request

from pymongo.uri_parser import split_hosts
from retry import retry


class EVAPrivateSettingsXMLConfig:
    config_data = None

    def __init__(self, settings_xml_file: str):
        with open(settings_xml_file) as xml_file_handle:
            self.config_data = et.parse(xml_file_handle)

    def get_value_with_xpath(self, location: str, optional: bool = False):
        etree = self.config_data.getroot()
        result = etree.xpath(location)
        if not result and not optional:
            raise ValueError("Invalid XPath location: " + location)
        return result


def get_metadata_creds_for_profile(profile_name: str, settings_xml_file: str):
    """
    Gets host, username, and password for metadata postgres database.
    Useful for filling properties files, for connection purposes you can use
    `metadata_utils.get_metadata_connection_handle`.
    """
    properties = get_properties_from_xml_file(profile_name, settings_xml_file)
    pg_url = properties['eva.evapro.jdbc.url']
    pg_user = properties['eva.evapro.user']
    pg_pass = properties['eva.evapro.password']
    return pg_url, pg_user, pg_pass


def get_primary_mongo_creds_for_profile(profile_name: str, settings_xml_file: str):
    """
    Gets primary host, username, and password for mongo database.
    Useful for filling properties files, for connection purposes it is preferable to use
    `mongo_utils.get_mongo_connection_handle` as that will handle multiple hosts appropriately.
    """
    properties = get_properties_from_xml_file(profile_name, settings_xml_file)
    # Use the primary mongo host from configuration:
    # https://github.com/EBIvariation/configuration/blob/master/eva-maven-settings.xml#L111
    # TODO: revisit once accessioning/variant pipelines can support multiple hosts
    try:
        mongo_host = split_hosts(properties['eva.mongo.host'])[1][0]
    except IndexError:  # some profiles have only one host
        mongo_host = split_hosts(properties['eva.mongo.host'])[0][0]
    mongo_user = properties['eva.mongo.user']
    mongo_pass = properties['eva.mongo.passwd']
    return mongo_host, mongo_user, mongo_pass


def get_accession_pg_creds_for_profile(profile_name: str, settings_xml_file: str):
    """
    Gets host, username, and password for accessioning job tracker database.
    Useful for filling properties files.
    """
    properties = get_properties_from_xml_file(profile_name, settings_xml_file)
    pg_url = properties['eva.accession.jdbc.url']
    pg_user = properties['eva.accession.user']
    pg_pass = properties['eva.accession.password']
    return pg_url, pg_user, pg_pass


def get_count_service_creds_for_profile(profile_name: str, settings_xml_file: str):
    """
    Gets host, username, and password for eva count service.
    Useful for filling properties files.
    """
    properties = get_properties_from_xml_file(profile_name, settings_xml_file)
    counts_url = properties['eva.count-stats.url']
    counts_user = properties['eva.count-stats.username']
    counts_pass = properties['eva.count-stats.password']
    return counts_url, counts_user, counts_pass


def get_pg_uri_for_accession_profile(profile_name: str, settings_xml_file: str):
    return get_pg_uri_details_for_profile(profile_name, settings_xml_file, "eva.accession.jdbc.url")


def get_pg_uri_for_variant_profile(profile_name: str, settings_xml_file: str):
    return get_pg_uri_details_for_profile(profile_name, settings_xml_file, "eva.variant.jdbc.url")


def get_pg_metadata_uri_for_eva_profile(profile_name: str, settings_xml_file: str):
    return get_pg_uri_details_for_profile(profile_name, settings_xml_file, "eva.evapro.jdbc.url")


def get_pg_uri_details_for_profile(eva_profile_name: str, settings_xml_file: str, tag_name: str):
    config = EVAPrivateSettingsXMLConfig(settings_xml_file)
    xpath_location_template = '//settings/profiles/profile/id[text()="{0}"]/../properties/{1}/text()'
    # Format is jdbc:postgresql://host:port/db
    metadata_db_jdbc_url = config.get_value_with_xpath(
        xpath_location_template.format(eva_profile_name, tag_name))[0]
    return metadata_db_jdbc_url.split("jdbc:")[-1]


def get_mongo_uri_for_eva_profile(eva_profile_name: str, settings_xml_file: str):
    config = EVAPrivateSettingsXMLConfig(settings_xml_file)
    xpath_location_template = '//settings/profiles/profile/id[text()="{0}"]/../properties/{1}/text()'
    # Format is host1:port1,host2:port2
    mongo_hosts_and_ports = config.get_value_with_xpath(
        xpath_location_template.format(eva_profile_name, "eva.mongo.host"))[0]
    username = config.get_value_with_xpath(
        xpath_location_template.format(eva_profile_name, "eva.mongo.user"), optional=True)
    if not username:  # no authentication
        return f"mongodb://{mongo_hosts_and_ports}"
    username = username[0]
    password = config.get_value_with_xpath(
        xpath_location_template.format(eva_profile_name, "eva.mongo.passwd"))[0]
    authentication_db = config.get_value_with_xpath(
        xpath_location_template.format(eva_profile_name, "eva.mongo.auth.db"))[0]
    return "mongodb://{0}:{1}@{2}/{3}".format(username, quote_plus(password), mongo_hosts_and_ports, authentication_db)


def get_properties_from_xml_file(profile, xml_path):
    tree = et.parse(xml_path)
    root = tree.getroot()
    return get_profile_properties(profile, root)


def get_properties_from_xml_string(profile, str):
    root = et.fromstring(str)
    return get_profile_properties(profile, root)


def get_profile_properties(profile, root):
    properties = {}
    for property in root.xpath('//settings/profiles/profile/id[text()="' + profile + '"]/../properties/*'):
        properties[property.tag] = property.text
    return properties


@retry(tries=4, delay=2, backoff=1.2, jitter=(1, 3))
def get_eva_settings_xml_string(token):
    url = 'https://api.github.com/repos/EBIvariation/configuration/contents/eva-maven-settings.xml'
    headers = {'Authorization': 'token ' + token, 'Accept' : 'application/vnd.github.raw' }
    request = urllib.request.Request(url, None, headers)
    with urllib.request.urlopen(request) as response:
        return response.read()


def get_args_from_private_config_file(private_config_file):
    with open(private_config_file) as private_config_file_handle:
        if 'json' in private_config_file:
            return json.load(private_config_file_handle)
        else:
            if 'yml' in private_config_file:
                return yaml.safe_load(private_config_file_handle)
            else:
                raise TypeError('Configuration file should be either json or yaml')