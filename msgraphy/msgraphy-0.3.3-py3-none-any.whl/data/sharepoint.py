from datetime import datetime

from msgraphy.data import graphdataclass


@graphdataclass
class SharePointIds:
    list_id: str = None
    list_item_id: str = None
    list_item_unique_id: str = None
    site_id: str = None
    site_url: str = None
    tenant_id: str = None
    web_id: str = None


@graphdataclass
class SiteResource:
    name: str = None
    site_collection: dict = None

    @property
    def resource(self):
        try:
            if self.id:
                return f"sites/{self.id}"
        except AttributeError:
            pass

        resource = f"sites/{self.site_collection.get('hostname', 'root')}" if self.site_collection else "/sites/root"
        if self.name is not None and self.name != "":
            resource += f":/sites/{self.name}:"
        return resource


@graphdataclass
class Site(SiteResource):
    display_name: str = None
    id: str = None
    description: str = None
    created_date_time: datetime = None
    last_modified_date_time:  datetime = None
    web_url: str = None
    root: str = None
