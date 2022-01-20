
class JAF:
    def __init__(self, response):
        # Parse meta
        self.meta = response.get("meta", {})

        # Parse data
        data = response.get('data', {})
        if isinstance(data, dict):
            self._parse_from_object(data)
        elif type(data) == list:
            self.items = []
            for item in data:
                self.items.append(JAF({"data": item}))

        # Parse cursor from meta
        self.next = self.meta.get('next', '')

    @staticmethod
    def serialize(type, attributes, relationships=None):
        """
        Creates a JSON API valid request
        @param type: The type of object we want to modify
        @param attributes: The objects attributes
        @param relationships: Any relationships should be passed through this filed
        @return:
        """
        data_obj = {
            "type": type,
            "attributes": attributes,
        }

        if relationships:
            data_obj["relationships"] = relationships

        return {"data": data_obj}

    def _parse_from_object(self, data):
        """
        Parses the data json into self.
        @param data: json in Json API Specification format
        @return: None
        """
        self.id = data.get("id", None)
        self.type = data.get("type", None)
        self.attributes = data.get("attributes", {})

        self.relationships = data.get("relationships", {})
        for key in self.relationships:
            self.relationships[key] = JAF(self.relationships.get(key, {}))
