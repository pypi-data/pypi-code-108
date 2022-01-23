class Entry:
    def __init__(self, identifier, name):
        self.__name = name
        self.__identifier = identifier
        self.__features = {}
        self.__roles = {}
        self.__ditto_features = {}

        self.__dt_json = {}
        self.__repo_json = {}
        self.__dir_json = {
            "thingId": "",
            "policyId": "",
            "attributes": {

            }
        }

    @property
    def features(self):
        return self.__features

    @features.setter
    def features(self, value):
        self.__features = value

    @property
    def ditto_features(self):
        return self.__ditto_features

    @ditto_features.setter
    def ditto_features(self, value):
        self.__ditto_features = value

    @property
    def roles(self):
        return self.__roles

    @roles.setter
    def roles(self, value):
        self.__roles = value

    @property
    def name(self):
        return self.__name

    @property
    def identifier(self):
        return self.__identifier

    @property
    def dt_json(self):
        return self.__dt_json

    @property
    def repo_json(self):
        return self.__repo_json

    @property
    def dir_json(self):
        return self.__dir_json

    def refresh_directory_entry(self, current_dir_json):
        self.__dir_json = current_dir_json
        if self.__identifier is not None:
            self.__dir_json["thingId"] = self.__identifier
            self.__dir_json["policyId"] = self.__identifier
        if self.__name is not None:
            self.__dir_json["attributes"]["name"] = self.__name
        self.__dir_json["attributes"]["dataModel"] = "fml40"
        self.__dir_json["attributes"]["thingStructure"] = {
            "class": "ml40::Thing",
            "links": []
        }
        for key in self.__roles.keys():
            role_entry = {
                "association": "roles",
                "target": self.__roles[key].to_json()
            }
            self.__dir_json["attributes"]["thingStructure"]["links"].append(role_entry)

        for key in self.features.keys():
            feature_target = {
                "class": self.__features[key].to_json()["class"],
            }
            if self.__features[key].to_json().get("identifier") is not None:
                feature_target["identifier"] = self.__features[key].to_json()["identifier"]

            feature_entry = {"association": "features", "target": feature_target}
            # if the feature has targets, like ml40::Composite
            if hasattr(self.__features[key], "targets"):
                feature_entry["target"]["links"] = list()
                for target in self.__features[key].targets.keys():
                    target_json = (
                        self.__features[key].targets[target].entry.refresh_sub_thing_dir_entry()
                    )
                    feature_entry["target"]["links"].append(target_json)
            self.__dir_json["attributes"]["thingStructure"]["links"].append(feature_entry)
        return self.__dir_json

    def refresh_repository_entry(self):
        self.__repo_json = {
            "thingId": self.__identifier,
            "policyId": self.__identifier,
            "attributes": {
                "class": "ml40::Thing",
                "name": self.__name,
            },
        }
        if self.roles:
            self.__repo_json["attributes"]["roles"] = []
        if self.features:
            self.__repo_json["attributes"]["features"] = []
        if self.ditto_features:
            self.__repo_json["features"] = {}
        for key in self.__roles.keys():
            self.__repo_json["attributes"]["roles"].append(self.__roles[key].to_json())
        for key in self.__features.keys():
            self.__repo_json["attributes"]["features"].append(self.__features[key].to_json())
        for key in self.__ditto_features.keys():
            self.__repo_json["features"][key] = self.__ditto_features[key].to_json()
        return self.__repo_json

    def refresh_dt_json(self):
        self.__dt_json = self.refresh_repository_entry()

    def refresh_sub_thing_repo_entry(self):
        """Returns a dictionary representing this thing in it's current state
        as a subordinate thing. This representation should be used for
        subordinate things in s3i repository entries.

        :returns: Representation of this object as a subordinate thing
        :rtype: dict

        """

        json_out = {
            "class": "ml40::Thing",
            "name": self.name,
            "roles": [],
            "features": [],
        }
        if self.__identifier:
            json_out["identifier"] = self.__identifier
        for key in self.__roles.keys():
            json_out["roles"].append(self.__roles[key].to_json())
        for key in self.__features.keys():
            json_out["features"].append(self.__features[key].to_json())
        return json_out

    def refresh_sub_thing_dir_entry(self):
        """Returns a dictionary representing this thing in it's current state
        as a subordinate thing. This representation should be used for
        subordinate things in s3i directory entries.

        :returns: Representation of this object as a subordinate thing.
        :rtype: dict

        """

        json_out = {"class": "ml40::Thing", "links": []}
        if self.__identifier:
            json_out["identifier"] = self.__identifier
        for key in self.__roles.keys():
            role_entry = {"association": "roles", "target": self.__roles[key].to_json()}
            json_out["links"].append(role_entry)
        for key in self.__features.keys():
            feature_target = {
                "class": self.__features[key].to_json()["class"],
            }
            if self.__features[key].to_json().get("identifier") is not None:
                feature_target["identifier"] = self.__features[key].to_json()["identifier"]
            feature_entry = {"association": "features", "target": feature_target}
            json_out["links"].append(feature_entry)
        return json_out
