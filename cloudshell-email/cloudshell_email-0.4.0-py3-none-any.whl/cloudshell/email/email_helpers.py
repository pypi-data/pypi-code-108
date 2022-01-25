import os
from urllib.parse import urljoin

from cloudshell.api.cloudshell_api import ResourceInfo


def get_resource_attribute_value(resource: ResourceInfo, attribute_name: str) -> str:
    attribute_name = attribute_name.lower()
    attribute = next(filter(lambda x: x.Name.lower() == attribute_name
                            or x.Name.lower() == f'{resource.ResourceModelName.lower()}.{attribute_name}',
                            resource.ResourceAttributes), None)
    if not attribute:
        raise ValueError(f"Attribute {attribute_name} not found on resource {resource.Name}")

    return attribute.Value


def build_email_template_full_path(template_name: str, base_path: str = __file__) -> str:
    current_dir = os.path.dirname(os.path.abspath(base_path))
    template_full_path = os.path.join(current_dir, template_name)
    return template_full_path


def build_sandbox_url(portal_url: str, sandbox_id: str) -> str:
    return urljoin(str(portal_url), f"RM/Diagram/Index/{sandbox_id}")
