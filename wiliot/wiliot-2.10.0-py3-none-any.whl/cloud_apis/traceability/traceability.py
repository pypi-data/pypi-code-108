import requests
from wiliot.cloud_apis.api_client import Client, WiliotCloudError
import json
import urllib.parse


class AssetNotFound(Exception):
    pass


class AssetTypeNotFound(Exception):
    pass


class POINotFound(Exception):
    pass


class ProjectNotFound(Exception):
    pass


class TraceabilityClient(Client):
    def __init__(self, oauth_username, oauth_password, owner_id, env='', log_file=None):
        self.client_path = "traceability/owner/{owner_id}/project".format(owner_id=owner_id)
        super().__init__(oauth_username, oauth_password, env, log_file)

    # Project calls

    def get_projects(self):
        """
        Get all projects for an owner
        :return: A list of project dictionaries
        """
        path = ""
        res = self._get(path)
        return res.get('data', [])

    def get_project(self, project_id):
        """
        Get one project by it ID
        :param project_id: String - mandatory - the ID of the project to return
        :return: The requested project dictionary
        :raises: ProjectNotFoundError if the requested project ID cannot be found
        """
        path = "/{}".format(project_id)
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise ProjectNotFound
        return res.get('data', [])

    def create_project(self, project_id, project_type=None, name=None):
        """
        Create a project
        :param project_id: String - mandatory
        :param project_type: String - optional - currently unused
        :param name: String - optional. If not provided an asset ID will be generated automatically
        :return: The created project if successful
        """
        path = ""
        payload = {
            "id": project_id,
            "projectType": project_type,
            "name": name
        }
        try:
            res = self._post(path, payload)
            return res["data"]
        except WiliotCloudError as e:
            print("Failed to create project")
            raise e

    def update_project(self, project):
        """
        Update a project
        :param project: Dictionary containing updated project properties
        :return: The updated asset if successful
        """
        path = "/{}".format(project["id"])
        payload = {
            "projectType": project["projectType"],
            "name": project["name"]
        }
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update project")
            raise e

    def delete_project(self, project_id):
        """
        Delete a project by its ID
        :param project_id: String - mandatory
        :return: True if the project was deleted
        """
        path = "/{}".format(project_id)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete project")
            raise e

    # Asset calls

    def get_assets(self, project_id):
        """
        Get all assets for a project
        :param project_id: String - mandatory
        :return: A list of asset dictionaries
        """
        path = "/{}/asset".format(project_id)
        res = self._get(path)
        return res["data"]

    def get_asset(self, project_id, asset_id):
        """
        Get a single assets for a project
        :param project_id: string
        :param asset_id: string
        :return: a dictionary with asset properties
        :raises: An AssetNotFound exception if an asset with the
        provided ID cannot be found
        """
        path = "/{}/asset/{}".format(project_id, asset_id)
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise AssetNotFound
        return res.get('data', [])

    def create_asset(self, project_id,
                     name, asset_id=None, asset_type_id=None,
                     tag_ids=[], poi_id=None,
                     status=None):
        """
        Create an asset, and optionally assign tags, poi and asset type and status
        :param project_id: String
        :param name: String - A name for the asset (mandatory)
        :param asset_id: String - optional. If not provided an asset ID will be generated automatically
        :param asset_type_id: String - optional - the type of asset
        :param tag_ids: List - optional - a list of tag IDs to assign to the asset
        :param poi_id: String - optional - an ID for a POI to associate with the asset
        :param status: String - optional - A status
        :return: The created asset if successful
        """
        assert isinstance(tag_ids, list), "Was expecting a list of strings for tag_ids"
        path = "/{}/asset".format(project_id)
        payload = {
            "id": asset_id,
            "name": name,
            "assetTypeId": asset_type_id,
            "tagId": tag_ids[0] if len(tag_ids) else None,
            "poiId": poi_id,
            "status": status
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create asset")
            raise e

    def update_asset(self, project_id, asset):
        """
        Update an asset, and optionally assign tags, poi and asset type and status
        :param project_id: String
        :param asset: Dictionary describing an existing asset
        :return: The updated asset if successful
        """
        path = "/{}/asset/{}".format(project_id, asset["id"])
        payload = {
            "id": asset["id"],
            "name": asset["name"],
            "assetTypeId": asset.get("assetTypeId", None),
            "tagId": asset.get("tagId", None),
            "poiId": asset.get("poiId", None),
            "status": asset.get("status", None)
        }
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update asset")
            raise e

    def delete_asset(self, project_id, asset_id):
        """
        Delete an asset by its ID
        :param project_id: String - mandatory
        :param asset_id: String - mandatory - the ID of the asset to delete
        :return: True if the asset was deleted
        """
        path = "/{}/asset/{}".format(project_id, asset_id)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete asset")
            raise e

    # Asset type calls

    def get_asset_types(self, project_id):
        """
        Get all asset types for a project
        :param project_id: string
        :return: a list of dictionaries with asset types
        """
        path = "/{}/asset/type".format(project_id)
        res = self._get(path)
        return res.get('data', [])

    def get_asset_type(self, project_id, asset_type_id):
        """
        Get a single asset type for a project
        :param project_id: string
        :param asset_type_id: string
        :return: a dictionary with asset type properties
        :raises: An AssetTypeNotFound exception if an asset with the
        provided ID cannot be found
        """
        path = "/{}/asset/type/{}".format(project_id, asset_type_id)
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise AssetTypeNotFound
        return res.get('data', [])

    def create_asset_type(self, project_id, name, asset_type_id=None):
        """
        Create an asset type
        :param project_id: String
        :param name: String - A name for the asset (mandatory)
        :param asset_type_id: String - optional. If not provided an asset ID will be generated automatically
        :return: The created asset if successful
        """
        path = "/{}/asset/type".format(project_id)
        payload = {
            "id": asset_type_id,
            "name": name
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create asset type")
            raise e

    def update_asset_type(self, project_id, asset_type):
        """
        Update an asset, and optionally assign tags, poi and asset type and status
        :param project_id: String
        :param asset_type: Dictionary describing an existing asset type
        :return: The updates asset if successful
        """
        path = "/{}/asset/type/{}".format(project_id, asset_type['id'])
        try:
            res = self._put(path, asset_type)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update asset type")
            raise e

    def delete_asset_type(self, project_id, asset_type_id):
        """
        Delete an asset by its ID
        :param project_id: String - mandatory
        :param asset_type_id: String - mandatory - the ID of the asset type to delete
        :return: True if the asset was deleted
        """
        path = "/{}/asset/type/{}".format(project_id, asset_type_id)
        try:
            res = self._delete(path)
            print(res['message'])
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete asset type")
            raise e

    # POI calls

    def get_pois(self, project_id):
        """
        Get all POIs for a project
        :param project_id: string
        :return:
        """
        path = "/{}/poi".format(project_id)
        res = self._get(path)
        return res.get('data', [])

    def get_poi(self, project_id, poi_id):
        """
        Get a single POI for a project, by ID
        :param project_id: string
        :param poi_id: string
        :return: a dictionary with asset properties
        :raises: An AssetNotFound exception if an asset with the
        provided ID cannot be found
        """
        path = "/{}/poi/{}".format(project_id, poi_id)
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise POINotFound
        return res.get('data', [])

    def create_poi(self, project_id,
                   name, poi_id=None, address=None, country=None, city=None, lat=None, lng=None):
        """
        Create a POI
        :param project_id: String
        :param name: String - A name for the POI (mandatory)
        :param poi_id: String - optional - An ID for the POI. Must be unique. If not provided one will be generated
        :param address: String - optional. If not provided an asset ID will be generated automatically
        :param country: String - optional - The country the POI is located in
        :param city: String - optional - The city the POI is located in
        :param lat: Float - optional - The POI's latitude
        :param lng: Float - optional - The POI's longitude
        :return: The created asset if successful
        """
        path = "/{}/poi".format(project_id)
        payload = {
            "id": poi_id,
            "name": name,
            "address": address,
            "country": country,
            "city": city,
            "lat": lat,
            "lng": lng
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create POI")
            raise e

    def update_poi(self, project_id, poi):
        """
        Update a POI,
        :param project_id: String
        :param poi: Dictionary describing an existing POI
        :return: The updated POI if successful
        """
        path = "/{}/poi/{}".format(project_id, poi["id"])
        payload = {
            "id": poi["id"],
            "name": poi["name"],
            "address": poi.get("address", None),
            "country": poi.get("country", None),
            "city": poi.get("city", None),
            "lat": poi.get("lat", None),
            "lng": poi.get("lng", None)
        }
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update asset")
            raise e

    def delete_poi(self, project_id, poi_id):
        """
        Delete an asset by its ID
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - the ID of the POI to delete
        :return: True if the POI was deleted
        """
        path = "/{}/poi/{}".format(project_id, poi_id)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete POI")
            raise e

    # POI Label calls

    def get_poi_labels(self, project_id, poi_id):
        """
        Get all labels for a POI by its ID
        :param project_id:
        :param poi_id:
        :return: list of labels
        """
        path = "/{}/poi/{}/label".format(project_id, poi_id)
        res = self._get(path)
        return res.get("data", [])

    def create_poi_label(self, project_id, poi_id, label):
        """
        Create a label for a POI
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - the POI to create the label for
        :param label: String - the label to create
        :return: True if label created
        """
        path = "/{}/poi/{}/label".format(project_id, poi_id)
        payload = {"label": label}
        res = self._post(path, payload)
        return res

    def delete_poi_labels(self, project_id, poi_id):
        """
        Create all labels for a POI identified by an ID
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - The ID of the POI for which labels should be deleted
        :return: True if successful
        """
        path = "/{}/poi/{}/label".format(project_id, poi_id)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete POI label")
            raise e

    def delete_poi_label(self, project_id, poi_id, label):
        """
        Create all labels for a POI identified by an ID
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - The ID of the POI for which labels should be deleted
        :return: True if successful
        """
        path = "/{}/poi/{}/label/{}".format(project_id, poi_id, label)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete POI label")
            raise e

    # POI association calls

    def get_poi_associations(self, project_id, poi_id):
        """
        Get all POI associations for a project
        :param project_id: string
        :param poi_id: string - The POI's ID
        :return:
        """
        path = "/{}/poi/{}/association".format(project_id, poi_id)
        res = self._get(path)
        return res.get('data', [])

    def create_poi_association(self, project_id, poi_id, association_type, association_value):
        """
        Create a POI association. At the moment two association types are supported: gateway or location
        :param project_id: String
        :param poi_id: String - The POI to associate to
        :param association_type: String - Either "gateway" or "location"
        :param association_value: String - The gateway or geohas to associate to the POI
        :return: True if the association was created successfully
        """
        allowed_association_types = ["gateway", "location"]
        assert association_type in allowed_association_types, "association_type must be one of {}".format(
            allowed_association_types)
        path = "/{}/poi/{}/association".format(project_id, poi_id)
        payload = {
            "associationType": association_type,
            "associationValue": association_value
        }
        try:
            res = self._post(path, payload)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to create POI association")
            raise e

    def delete_poi_associations(self, project_id, poi_id):
        """
        Delete all of the associations for a POI by ID
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - the ID of the POI who's associations should be deleted
        :return: True if the POI was deleted
        """
        path = "/{}/poi/{}/association".format(project_id, poi_id)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete POI associations")
            raise e

    def delete_poi_association(self, project_id, poi_id, association_value):
        """
        Delete one POI association using the POI Id and the association value
        :param project_id: String - mandatory
        :param poi_id: String - mandatory - the ID of the POI who's associations should be deleted
        :param association_value: String - mandatory - The association value to delete
        :return: True if the POI was deleted
        """
        path = "/{}/poi/{}/association/{}".format(project_id, poi_id, association_value)
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete POI assocation")
            raise e
