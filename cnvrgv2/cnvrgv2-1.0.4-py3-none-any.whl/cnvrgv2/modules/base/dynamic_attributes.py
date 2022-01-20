import pprint
from cnvrgv2.proxy import HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import error_messages


class DynamicAttributes:
    def __getattr__(self, name):
        """
        Try to get the requested attribute from the attributes object, if it doesnt exists do an API call.
        This function fires when trying to access an attribute that doesnt exists in the object.
        @param name: The requested attribute
        @return: Attribute value/None
        """
        if name in self.__class__.available_attributes.keys():
            val = self._attributes.get(name, None)
            if val is None:
                response = self._proxy.call_api(route=self._route, http_method=HTTP.GET)
                response_attributes = response.attributes
                response_attributes.pop('slug', None)
                # We want to merge the response attributes with the current attributes in order to not override setter
                self._attributes = {**response_attributes, **self._attributes}
                return self._attributes.get(name, None)
            else:
                return val
        else:
            raise AttributeError("type object {} has no attribute {}".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        """
        The function checks if an attribute is a dynamic api attribute (from the class.attributes var)
        If the attribute is dynamic, we perform a type check and apply the change.
        @param name: The attribute name we want to set
        @param value: The attribute value
        @return: None
        """
        if name in self.__class__.available_attributes.keys():
            value_type = type(value)
            expected_type = self.__class__.available_attributes[name]
            if value_type != expected_type:
                bad_format_message = error_messages.ARGUMENT_BAD_TYPE.format(expected_type, value_type)
                raise CnvrgArgumentsError({name: bad_format_message})
            self._attributes[name] = value
        else:
            super().__setattr__(name, value)

    def __str__(self):
        hash_representation = {}
        if hasattr(self, 'slug'):
            hash_representation["slug"] = self.slug

        for key in self.__class__.available_attributes.keys():
            hash_representation[key] = getattr(self, key)

        return pprint.pformat(hash_representation)

    def reload(self):
        """
        Performs hard reload for the module attributes
        @return: None
        """
        response = self._proxy.call_api(route=self._route, http_method=HTTP.GET)
        # We want to merge the response attributes with the current attributes in order to not override setter
        self.__setattr__("_attributes", {**self._attributes, **response.attributes})
