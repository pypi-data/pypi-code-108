import cloudinary
import re

CLOUDINARY_FIELD_DB_RE = r"(?:(?P<resource_type>image|raw|video)/(?P<type>upload|private|authenticated)/)?(?:v(?P<version>\d+)/)?(?P<public_id>.*?)(\.(?P<format>[^.]+))?$"  # NOQA


class CloudinaryResource(cloudinary.CloudinaryResource):
    @property
    def base_url(self):
        config = cloudinary.config()
        base_url = "https://res.cloudinary.com/{name}/".format(name=config.cloud_name)
        return "{base_url}{resource_type}/{type}".format(
            base_url=base_url, resource_type=self.resource_type, type=self.type
        )

    @property
    def versioned_public_id(self):
        version = (
            "v{}/".format(self.version) if self.version else ""
        )  # if '/' not in self.public_id else 'v1/'
        return "/{version}{public_id}".format(version=version, public_id=self.public_id)


def str_to_cloudinary_resource(value, resource_type="image", _type="upload"):
    if value == "":
        return None
    m = re.match(CLOUDINARY_FIELD_DB_RE, value)
    resource_type = m.group("resource_type") or resource_type
    upload_type = m.group("type") or _type
    return CloudinaryResource(
        type=upload_type,
        resource_type=resource_type,
        version=m.group("version"),
        public_id=m.group("public_id"),
        format=m.group("format"),
    )
