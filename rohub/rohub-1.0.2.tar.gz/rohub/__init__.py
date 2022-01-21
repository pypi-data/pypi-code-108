# Let users know if they're missing any of our hard dependencies
hard_dependencies = (["requests", "pandas"])
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies

# MAIN IMPORTS
from rohub.admin import admin
from rohub.rohub import login
from rohub.rohub import whoami
from rohub.rohub import version
from rohub.rohub import set_retries
from rohub.rohub import set_sleep_time
from rohub.rohub import list_my_ros
from rohub.rohub import is_job_success
from rohub.rohub import show_my_user_profile_details
# ROS MAIN IMPORTS
from rohub.rohub import ros_find
from rohub.rohub import ros_search_using_id
from rohub.rohub import ros_create
from rohub.rohub import ros_load
from rohub.rohub import ros_content
from rohub.rohub import ros_full_metadata
from rohub.rohub import ros_fork
from rohub.rohub import ros_snapshot
from rohub.rohub import ros_archive
from rohub.rohub import ros_list_publications
from rohub.rohub import ros_triple_details
from rohub.rohub import ros_list_annotations
from rohub.rohub import ros_list_triples
from rohub.rohub import ros_list_authors
from rohub.rohub import ros_list_contributors
from rohub.rohub import ros_list_copyright
from rohub.rohub import ros_list_fundings
from rohub.rohub import ros_list_license
from rohub.rohub import ros_export_to_rocrate
from rohub.rohub import ros_list_resources
from rohub.rohub import ros_list_folders
# ROS ADD IMPORTS
from rohub.rohub import ros_add_geolocation
from rohub.rohub import ros_add_folders
from rohub.rohub import ros_add_annotations
from rohub.rohub import ros_add_internal_resource
from rohub.rohub import ros_add_external_resource
from rohub.rohub import ros_add_triple
from rohub.rohub import ros_set_authors
from rohub.rohub import ros_set_contributors
from rohub.rohub import ros_set_publishers
from rohub.rohub import ros_set_copyright_holders
from rohub.rohub import ros_add_funding
from rohub.rohub import ros_set_license
# ROS UPLOAD IMPORTS
from rohub.rohub import ros_upload
from rohub.rohub import ros_upload_resources
# ROS DELETE IMPORTS
from rohub.rohub import ros_delete
from rohub.rohub import ros_delete_funding
from rohub.rohub import ros_delete_license
# ROS UPDATE IMPORTS
from rohub.rohub import ros_update
from rohub.rohub import ros_update_funding
# RESOURCE MAIN IMPORTS
from rohub.rohub import resource_search_using_id
from rohub.rohub import resource_load
from rohub.rohub import resource_assign_doi
from rohub.rohub import resource_download
# RESOURCE DELETE IMPORTS
from rohub.rohub import resource_delete
# RESOURCE UPDATE IMPORTS
from rohub.rohub import resource_update_metadata
from rohub.rohub import resource_update_content
# FOLDER IMPORTS
from rohub.rohub import folder_delete
# ANNOTATION IMPORTS
from rohub.rohub import annotation_delete
# USERS IMPORTS
from rohub.rohub import users_find
from rohub.rohub import show_user_id
# EXTERNAL USERS IMPORTS
from rohub.rohub import external_user_add
from rohub.rohub import external_user_delete
# ORGANIZATIONS IMPORTS
from rohub.rohub import organization_add
from rohub.rohub import organizations_find
# AUXILIARY
from rohub.rohub import zenodo_list_funders
from rohub.rohub import zenodo_list_grants
from rohub.rohub import list_available_licenses
from rohub.rohub import list_valid_research_areas
from rohub.rohub import list_valid_publication_services
from rohub.rohub import list_valid_ros_types
from rohub.rohub import list_valid_templates
from rohub.rohub import list_valid_resource_types
from rohub.rohub import list_valid_creation_modes
from rohub.rohub import list_valid_access_modes
from rohub.rohub import list_triple_object_classes
from rohub.rohub import list_custom_licenses
from rohub.rohub import list_valid_license_status
from rohub.rohub import add_custom_license
from rohub.rohub import update_custom_license
from rohub.rohub import show_valid_type_matching_for_ros

__all__ = [
    "login",
    "whoami",
    "version",
    "set_retries",
    "set_sleep_time",
    "list_my_ros",
    "is_job_success",
    "ros_search_using_id",
    "ros_create",
    "ros_load",
    "ros_content",
    "ros_full_metadata",
    "ros_fork",
    "ros_archive",
    "ros_list_publications",
    "ros_add_geolocation",
    "ros_add_folders",
    "ros_add_annotations",
    "ros_add_internal_resource",
    "ros_add_external_resource",
    "ros_upload",
    "ros_upload_resources",
    "ros_delete",
    "folder_delete",
    "annotation_delete",
    "ros_update",
    "ros_add_triple",
    "ros_triple_details",
    "ros_list_annotations",
    "ros_list_triples",
    "ros_export_to_rocrate",
    "ros_set_authors",
    "show_user_id",
    "ros_list_authors",
    "ros_set_contributors",
    "ros_list_contributors",
    "ros_list_copyright",
    "ros_set_copyright_holders",
    "ros_list_fundings",
    "ros_add_funding",
    "zenodo_list_funders",
    "zenodo_list_grants",
    "ros_set_license",
    "list_available_licenses",
    "list_valid_research_areas",
    "list_valid_publication_services",
    "list_valid_ros_types",
    "list_valid_templates",
    "list_valid_resource_types",
    "list_valid_creation_modes",
    "list_valid_access_modes",
    "ros_list_resources",
    "resource_search_using_id",
    "resource_update_metadata",
    "resource_delete",
    "resource_assign_doi",
    "resource_load",
    "list_triple_object_classes",
    "list_custom_licenses",
    "list_valid_license_status",
    "add_custom_license",
    "update_custom_license",
    "ros_find",
    "resource_update_content",
    "resource_download",
    "users_find",
    "ros_set_publishers",
    "show_valid_type_matching_for_ros",
    "ros_list_folders",
    "external_user_add",
    "organization_add",
    "organizations_find",
    "external_user_delete",
    "ros_delete_funding",
    "ros_update_funding",
    "ros_delete_license",
    "admin",
    "show_my_user_profile_details",
]
