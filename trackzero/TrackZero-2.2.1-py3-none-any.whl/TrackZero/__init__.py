from datetime import datetime
from numbers import Number
import json
import requests
from uuid import uuid4, UUID
from requests.api import post, get

class TrackZero:
    base_url = "https://api.trackzero.io"
    def __init__(self, api_key):
        self.api_key = api_key

    def json_serializer(self, obj):
        if isinstance(obj, (datetime)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return obj.hex
        raise TypeError ("Type %s not serializable" % type(obj))

    def create_analytics_space(self, analytics_space_id: str) -> bool:
        """Creates a new Analytics Space Container

        Parameters:
        analytics_space_id (str): The id of the new Analytics Space.

        Returns:
        bool: represents if the operation was successful.
        """
        res = requests.post(self.base_url + "/analyticsSpaces", params={"analyticsSpaceId":analytics_space_id}, headers={"X-API-KEY": self.api_key})
        return res.status_code == 200

    def delete_analytics_space(self, analytics_space_id: str) -> bool:
        """Deletes Analytics Space Container

        Parameters:
        analytics_space_id (str): The id of the Analytics Space to delete.

        Returns:
        bool: represents if the operation was successful.

        Warning:
        This action is immediate and permanent.
        """
        res = requests.delete(self.base_url + "/analyticsSpaces", params={"analyticsSpaceId":analytics_space_id}, headers={"X-API-KEY": self.api_key})
        return res.status_code == 200

    def upsert_entity(self, entity, analytics_space_id: str) -> bool:
        """Adds or Updates an entity

        Parameters:
        analytics_space_id (str): The id of the Analytics Space to store this entity in.

        Returns:
        entity (Entity): The entity to upsert.
        bool: represents if the operation was successful.

        Warning:
        This action is immediate and permanent.
        """
        if not isinstance(entity, Entity):
            raise TypeError("Type %s is invalid for entity" % type(entity))
        
        res = requests.post(self.base_url + "/tracking/entities", params={"analyticsSpaceId":analytics_space_id}, data=json.dumps(entity.__dict__, default=self.json_serializer), headers={"X-API-KEY": self.api_key, "content-type":"application/json"})
        return res.status_code == 200

    def delete_entity(self, analytics_space_id: str, entity_type:str, entity_id) -> bool:
        """Deletes an entity

        Parameters:
        analytics_space_id (str): The id of the Analytics Space to delete this entity from.

        Returns:
        bool: represents if the operation was successful.
        
        Warning:
        This action is immediate and permanent.

        """

        if not isinstance(entity_id, ( str, Number, UUID )):
            raise TypeError("Type %s is invalid for entity_id" % type(entity_id) )
        res = requests.post(self.base_url + "/tracking/entities", params={"analyticsSpaceId":analytics_space_id}, data=json.dumps({"type":entity_type, "id": entity_id}), headers={"X-API-KEY": self.api_key, "content-type":"application/json"})
        return res.status_code == 200


    def create_analytics_space_session(self, analytics_space_id: str, ttl_seconds: int):
        """Adds or Updates an entity

        Parameters:
        analytics_space_id (str): The id of the Analytics Space to store this entity in.
        ttl_seconds (int): The life time of the session in seconds. This value must be between 300 and 3600 seconds.

        Returns:
        track_zero_space_session: The session object, use the url string to redirect the user to the Analytics Page.

        """
        if not (300 <= ttl_seconds <= 3600):
            raise ValueError("ttl_seconds must be between 300 and 3600" )
        res = requests.get(self.base_url + "/analyticsSpaces/session",params={"analyticsSpaceId": analytics_space_id, "ttl": ttl_seconds}, headers={"X-API-KEY": self.api_key})
        if res.status_code == 200:
            loaded = json.loads(res.text)
            return SpaceSession(True, loaded["url"], loaded["sessionKey"], loaded["embeddedDashboardsUrl"], loaded["embeddedReportsUrl"])
        return SpaceSession(False, "", "", "", "")

class Entity:
    def __init__(self, entity_type: str, entity_id: object) :
        """Creates a new entity

        Parameters:
        entity_type (str): The type of the entity.
        entity_id (str, Number, UUID): The id of the entity.

        """
        if not isinstance(entity_id, ( str, Number, UUID )):
            raise TypeError("Type %s is invalid for entity_id" % type(entity_id) )
        self.type = entity_type
        self.id = entity_id
        self.customAttributes = dict()

    def add_attribute(self, attribute_name: str, value):
        """Adds an attribute to the entity that holds a value

        Parameters:
        attribute_name (str): The name of the attribute on this entity.
        value (str, Number, UUID, datetime): The value of the new attribute.

        Returns:
        self for chaining.
        
        """
        if not isinstance(value, ( str, Number, UUID, datetime )):
            raise TypeError("Type %s is invalid for value" % type(value) )

        self.customAttributes.update({attribute_name: value})
        return self

    def add_entity_reference_attribute(self, attribute_name: str, referenced_attribute_type: str, referenced_attribute_id):
        """Adds an attribute to the entity that is linked to another entity

        Parameters:
        attribute_name (str): The name of the attribute on this entity.
        referenced_attribute_type (str): The type of the referenced entity.
        referenced_attribute_id (str, Number, UUID): The id of the referenced entity.

        Returns:
        self for chaining.

        """
        if not isinstance(referenced_attribute_id, ( str, Number, UUID )):
            raise TypeError("Type %s is invalid for entity_id" % type(referenced_attribute_id) )

        if attribute_name in self.customAttributes:
            self.customAttributes[attribute_name].append({ "type":referenced_attribute_type , "id":referenced_attribute_id})
        else:
            self.customAttributes[attribute_name] = [{ "type":referenced_attribute_type, "id":referenced_attribute_id}]

        return self

    def add_automatically_translated_geopoint(self, latitude: Number, longitude: Number):
        """Links this entity to Country / State by instructing the server to do translation. Country/State entities will be automatically created and referenced.

        Parameters:
        latitude (Number): The Latitude of the point to geo translate.
        longitude (Number): The Longitude of the point to geo translate.

        Returns:
        self for chaining.
        """
        self.autoGeography = dict()
        self.autoGeography["geoPoint"] = dict()
        self.autoGeography["geoPoint"]["Latitude"] = latitude
        self.autoGeography["geoPoint"]["Longitude"] = longitude
        return self

class SpaceSession:
    def __init__(self, is_success: bool, url: str, session_key: str, embedded_dashboards_url: str, embedded_reports_url: str) -> None:
        self.is_success = is_success
        self.url = url
        self.session_key = session_key
        self.embedded_dashboarsd_url = embedded_dashboards_url
        self.embedded_reports_url = embedded_reports_url

            

