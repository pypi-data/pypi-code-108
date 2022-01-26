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
import re
from urllib.parse import urlsplit

import psycopg2

from ebi_eva_common_pyutils.config_utils import get_metadata_creds_for_profile
from ebi_eva_common_pyutils.ncbi_utils import get_ncbi_assembly_dicts_from_term
from ebi_eva_common_pyutils.pg_utils import get_result_cursor, get_all_results_for_query
from ebi_eva_common_pyutils.taxonomy.taxonomy import get_scientific_name_from_ensembl


def get_metadata_connection_handle(profile, settings_xml_file):
    pg_url, pg_user, pg_pass = get_metadata_creds_for_profile(profile, settings_xml_file)
    return psycopg2.connect(urlsplit(pg_url).path, user=pg_user, password=pg_pass)


def get_db_conn_for_species(species_db_info):
    db_name = "dbsnp_{0}".format(species_db_info["dbsnp_build"])
    pg_conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}'  port={3}".
                               format(db_name, "dbsnp", species_db_info["pg_host"], species_db_info["pg_port"]))
    return pg_conn


def get_species_info(metadata_connection_handle, dbsnp_species_name="all"):
    get_species_info_query = "select distinct database_name, scientific_name, dbsnp_build, pg_host, pg_port from " \
                             "dbsnp_ensembl_species.import_progress a " \
                             "join dbsnp_ensembl_species.dbsnp_build_instance b " \
                                "on b.dbsnp_build = a.ebi_pg_dbsnp_build "
    if dbsnp_species_name != "all":
        get_species_info_query += "where database_name = '{0}' ".format(dbsnp_species_name)
    get_species_info_query += "order by database_name"

    pg_cursor = get_result_cursor(metadata_connection_handle, get_species_info_query)
    species_set = [{"database_name": result[0], "scientific_name": result[1], "dbsnp_build":result[2],
                    "pg_host":result[3], "pg_port":result[4]}
                   for result in pg_cursor.fetchall()]
    pg_cursor.close()
    return species_set


# Get connection information for each Postgres instance of the dbSNP mirror
def get_dbsnp_mirror_db_info(pg_metadata_dbname, pg_metadata_user, pg_metadata_host):
    with psycopg2.connect("dbname='{0}' user='{1}' host='{2}'".format(pg_metadata_dbname, pg_metadata_user,
                                                                      pg_metadata_host)) as pg_conn:
        dbsnp_mirror_db_info_query = "select * from dbsnp_ensembl_species.dbsnp_build_instance"
        dbsnp_mirror_db_info = [{"dbsnp_build": result[0], "pg_host": result[1], "pg_port": result[2]}
                                for result in get_all_results_for_query(pg_conn, dbsnp_mirror_db_info_query)]
    return dbsnp_mirror_db_info


def get_taxonomy_code_from_taxonomy(metadata_connection_handle, taxonomy):
    """
    Retrieve an existing taxonomy code registered in the metadata database.
    """
    query = f"select distinct t.taxonomy_code from  taxonomy t where t.taxonomy_id = {taxonomy}"
    rows = get_all_results_for_query(metadata_connection_handle, query)
    if len(rows) == 0:
        return None
    elif len(rows) > 1:
        options = ', '.join(rows)
        raise ValueError(f'More than one possible code for taxonomy {taxonomy} found: {options}')
    return rows[0][0]


def get_assembly_code_from_assembly(metadata_connection_handle, assembly):
    """
    Retrieve an existing assembly code registered in the metadata database.
    """
    query = f"select distinct assembly_code from assembly where assembly_accession='{assembly}';"
    rows = get_all_results_for_query(metadata_connection_handle, query)
    if len(rows) == 0:
        return None
    elif len(rows) > 1:
        options = ', '.join([row for row, in rows])
        raise ValueError(f'More than one possible code for assembly {assembly} found: {options}')
    return rows[0][0]


def build_variant_warehouse_database_name(taxonomy_code, assembly_code):
    if taxonomy_code and assembly_code:
        return f'eva_{taxonomy_code}_{assembly_code}'
    return None


def resolve_existing_variant_warehouse_db_name(metadata_connection_handle, assembly, taxonomy):
    """
    Retrieve an existing database name by combining the taxonomy_code and assembly code registered in the metadata
    database.
    """
    return build_variant_warehouse_database_name(
        get_taxonomy_code_from_taxonomy(metadata_connection_handle, taxonomy),
        get_assembly_code_from_assembly(metadata_connection_handle, assembly)
    )


# For backward compatibility
get_variant_warehouse_db_name_from_assembly_and_taxonomy = resolve_existing_variant_warehouse_db_name


def resolve_variant_warehouse_db_name(metadata_connection_handle, assembly, taxonomy):
    """
    Retrieve the database name for this taxonomy/assembly pair whether it exists or not.
    It will use existing taxonomy code or assembly code if available in the metadata database.
    """
    taxonomy_code = get_taxonomy_code_from_taxonomy(metadata_connection_handle, taxonomy)
    if not taxonomy_code:
        scientific_name = get_scientific_name_from_ensembl(taxonomy)
        taxonomy_code = scientific_name[0].lower() + re.sub('[^0-9a-zA-Z]+', '',
                                                            ''.join(scientific_name.split()[1:]).lower())
    assembly_code = get_assembly_code_from_assembly(metadata_connection_handle, assembly)
    if not assembly_code:
        assembl_dicts = get_ncbi_assembly_dicts_from_term(assembly)
        assembly_names = set([d.get('assemblyname') for d in assembl_dicts])
        if len(assembly_names) != 1:
            raise ValueError(f'Cannot resolve assembly name for assembly {assembly} in NCBI. '
                             f'Found {",".join([str(a) for a in assembly_names])}')
        assembly_code = re.sub('[^0-9a-zA-Z]+', '', assembly_names.pop().lower())
    return build_variant_warehouse_database_name(taxonomy_code, assembly_code)
