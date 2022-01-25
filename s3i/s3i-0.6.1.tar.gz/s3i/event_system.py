import copy
import json
import time
import uuid
import hashlib
import pyrql
from jsonschema import validate
from pyrql.query import And, Or, Filter

from s3i import EventMessage


class NamedEvent(object):
    def __init__(self, topic, json_schema):
        self.__topic = topic
        self.__json_schema = json_schema
        self.__msg = {}

    @property
    def topic(self):
        return self.__topic

    @property
    def json_schema(self):
        return self.__json_schema

    @property
    def msg(self):
        return self.__msg

    def generate_event_msg(self, content):
        validate(instance=content, schema=self.__json_schema)
        _msg = EventMessage()
        _msg.fillEventMessage(
            sender=self.__topic.split(".")[0],
            msg_id="s3i:{}".format(uuid.uuid4()),
            topic=self.topic,
            timestamp=int(time.time() * 1000.0),
            content=content
        )
        self.__msg = _msg.msg


class CustomEvent(object):
    def __init__(self, filter_object, filter_attribute_paths,
                 attribute_paths, topic, json_entry):
        self.__filter_object = filter_object
        self.__filter_attribute_paths = filter_attribute_paths
        self.__attribute_paths = attribute_paths
        self.__topic = topic
        self.__is_triggered = False
        self.__msg = {}
        self.__json_entry = json_entry
        self.__cur_attributes_dict = {}

    @property
    def filter_object(self):
        return self.__filter_object

    @property
    def filter_attribute_paths(self):
        return self.__filter_attribute_paths

    @property
    def attribute_paths(self):
        return self.__attribute_paths

    @property
    def topic(self):
        return self.__topic

    @property
    def msg(self):
        return self.__msg

    def check_filter(self):
        """
        Check the rql filter being triggered
        """
        if self.check_filter_attributes_changed():
            return self.__filter_object(self.__cur_attributes_dict)
        return False 

    def check_filter_attributes_changed(self):
        new_cur_dict = {}
        for path in self.filter_attribute_paths:
            new_cur_dict[path.replace("/", " ")] = _uriToData(path, self.__json_entry)
            if new_cur_dict != self.__cur_attributes_dict:
                self.__cur_attributes_dict = copy.deepcopy(new_cur_dict)
                return True
        return False

    def generate_event_msg(self):
        _content = {}
        for i in self.__attribute_paths:
            var = _uriToData(i, self.__json_entry)
            _content[i] = var

        _msg = EventMessage()
        _msg.fillEventMessage(
            sender=self.__topic.split(".")[0],
            msg_id="s3i:{}".format(uuid.uuid4()),
            topic=self.__topic,
            timestamp=int(time.time() * 1000.0),
            content=_content
        )

        self.__msg = _msg.msg


class EventManager:
    def __init__(self, json_entry):
        self.__json_entry = json_entry
        self.__named_event_dict = {}
        self.__custom_event_dict = {}

    @property
    def json_entry(self):
        return self.__json_entry

    @json_entry.setter
    def json_entry(self, value):
        if isinstance(value, dict):
            self.__json_entry = value

    def add_named_event(self, topic, json_schema):
        """
        Add a namedEvent to EventManager

        """
        if topic in self.__named_event_dict.keys():
            return False
        _named_event = NamedEvent(topic, json_schema)
        self.__named_event_dict[topic] = _named_event
        return True

    def delete_named_event(self, topic):
        if topic not in self.__named_event_dict.keys():
            return False
        _deleted_obj = self.__named_event_dict.pop(topic)
        del _deleted_obj

    def add_custom_event(self, rql_expression, attribute_paths):
        rql = RQL(rql_expression=rql_expression)
        if not rql.is_rql_valid:
            return False, None

        for path in rql.get_attributes():
            if _uriToData(path, self.__json_entry) is None:
                return False, None

        for path in attribute_paths:
            if _uriToData(path, self.__json_entry) is None:
                return False, None

        rql_filter = rql.make_filter()
        topic = "{}.{}".format(self.__json_entry.get("thingId"),
                               hashlib.md5((rql_expression + str(attribute_paths)).encode("utf-8")).hexdigest())
        _custom_event = CustomEvent(filter_object=rql_filter, filter_attribute_paths=rql.get_attributes(),
                                    attribute_paths=attribute_paths, topic=topic, json_entry=self.__json_entry)
        self.__custom_event_dict[topic] = _custom_event
        return True, topic

    def delete_custom_event(self, topic):
        if topic not in self.__custom_event_dict.keys():
            return False
        _deleted_obj = self.__custom_event_dict.pop(topic)
        del _deleted_obj

    def emit_named_event(self, publisher, topic, content):
        """
        """
        event_obj = self.__named_event_dict.get(topic)

        """
        if isinstance(event_obj, NamedEvent):
            event_obj.generate_event_msg(content=content)
            publisher.send(
                msg=json.dumps(event_obj.msg),
                receiver_endpoints=[topic],
                exchange="eventExchange"
            )
        """
        if isinstance(event_obj, NamedEvent):
            event_obj.generate_event_msg(content=content)
            publisher.publish_event(
                topic=topic,
                msg=json.dumps(event_obj.msg)
            )

    def emit_custom_event(self, publisher, topic):
        event_obj = self.__custom_event_dict.get(topic)
        if isinstance(event_obj, CustomEvent):
            if event_obj.check_filter():
                event_obj.generate_event_msg()
                publisher.publish_event(
                    msg=json.dumps(event_obj.msg),
                    topic=topic
                )


class RQL:
    """
    class for parsing, creating and checking rql filter
    """

    def __init__(self, rql_expression):
        """
        Constructor
        """

        self.__rql_expression = rql_expression
        self.__parsed_rql_expression = None
        self.__is_rql_valid = False

        self.__rql_logic_operator = ["and", "or"]
        self.__rql_math_operator = ["eq", "ne", "gt", "ge", "lt", "ge", "like", "exists"]

        self.__parse()

    @property
    def rql_expression(self):
        return self.__rql_expression

    @property
    def parsed_rql_expression(self):
        return self.__parsed_rql_expression

    @property
    def is_rql_valid(self):
        return self.__is_rql_valid

    def __parse(self):
        """
        Function to parse rql expression. If the expression is invalid, return empty dictionary

        :param rql_expr: rql expression
        :type rql_expr: str

        :return: parsed rql expression
        :rtype: dict

        """
        try:
            self.__parsed_rql_expression = pyrql.parse(self.__rql_expression.replace("/", " "))
            self.__is_rql_valid = True
        except pyrql.RQLSyntaxError:
            self.__parsed_rql_expression = {}
            self.__is_rql_valid = False

    def make_filter(self):
        """
        Function to create a RQL filter object. If the RQL expression is invalid, return None.

        :return: RQL filter

        Returns:

        """
        if self.__parsed_rql_expression.get("name") in self.__rql_math_operator:
            rql_filter = Filter(self.__parsed_rql_expression.get("name"),
                                self.__parsed_rql_expression.get("args")[0],
                                self.__parsed_rql_expression.get("args")[1])

        elif self.__parsed_rql_expression.get("name") in self.__rql_logic_operator:
            args = self.__parsed_rql_expression.get("args")
            rql_filter = self.__create_single_filter(args)
            for i in range(len(rql_filter) - 1):
                if self.__parsed_rql_expression.get("name") == "and":
                    rql_filter = And(rql_filter[i], rql_filter[i + 1])
                if self.__parsed_rql_expression.get("name") == "or":
                    rql_filter = Or(rql_filter[i], rql_filter[i + 1])
        else:
            return None
        return rql_filter

    def __create_single_filter(self, args, filters=None):
        """
        Function to create a single filter which only contains one related variable in filter expression

        """
        if filters is None:
            filters = []
        for i in range(len(args)):
            if args[i].get("name") not in self.__rql_logic_operator:
                filters.append(
                    Filter(args[i].get("name"), args[i].get("args")[0], args[i].get("args")[1]))
            else:
                filters.append([])
                self.__create_single_filter(args=args[i].get("args"), filters=filters[i])

                if args[i].get("name") == "and":

                    for j in range(len(filters[i]) - 1):
                        filters[i] = And(filters[i][j], filters[i][j + 1])

                if args[i].get("name") == "or":

                    for j in range(len(filters[i]) - 1):
                        filters[i] = Or(filters[i][j], filters[i][j + 1])

        return filters

    def get_attributes(self):
        """
        Function to get all attributes contained in the rql expression.
        If the rql expression is invalid, return empty list

        :return: attributes
        :rtype: list

        """
        _attributes = list()
        if self.__parsed_rql_expression.get("name") in self.__rql_math_operator:
            _attributes.append(self.__parsed_rql_expression.get("args")[0])

        elif self.__parsed_rql_expression.get("name") in self.__rql_logic_operator:
            args = self.__parsed_rql_expression.get("args")
            _attributes = self._get_attributes(args)

        for i in range(len(_attributes)):
            _attributes[i] = _attributes[i].replace(" ", "/")

        return _attributes

    def _get_attributes(self, args):
        _attributes = []
        for i in range(len(args)):
            if args[i].get("name") not in self.__rql_logic_operator:
                _attributes.append(args[i].get("args")[0])
            else:
                _temp_attributes = self._get_attributes(args=args[i].get("args"))
                for temp in _temp_attributes:
                    _attributes.append(temp)
        return _attributes


resGetValue = []


def _uriToData(uri, ml40_model):
    """Returns a copy of the value found at uri.

    :param uri: Path to value
    :rtype: Feature

    """
    global resGetValue
    if uri == "":
        return ml40_model
    else:
        uri_list = uri.split("/")
        if uri_list[0] == "features":
            try:
                return ml40_model[uri]
            except KeyError:
                return None

        try:
            _getValue(ml40_model, uri_list, ml40_model)
        except Exception:
            return None
        if resGetValue.__len__() == 0:
            return None
        response = copy.deepcopy(resGetValue)
        resGetValue.clear()
        if response.__len__() == 1:
            return response[0]
        else:
            return response


def _getValue(source, uri_list, ml40_model):
    """Searches for the value specified by uri_list in source and stores
    the result in __resGetValue.

    :param source: Object that is scanned
    :param uri_list: List containing path

    """
    global resGetValue
    value = source[uri_list[0]]
    if uri_list.__len__() == 1:
        # if is ditto-feature
        if isinstance(value, str):
            try:
                stringValue_split = value.split(":")
                if stringValue_split[0] == "ditto-feature":
                    value = ml40_model["features"][stringValue_split[1]][
                        "properties"
                    ][uri_list[0]]
            except:
                pass
        resGetValue.append(value)
        return
    if isinstance(value, dict):
        # ??? uri_list.pop(0) better?!
        del uri_list[0]
        _getValue(value, uri_list, ml40_model)
    if isinstance(value, list):
        if isinstance(value[0], (str, int, float, bool, list)):
            return value
        if isinstance(value[0], dict):
            for item in value:
                if item["class"] == "ml40::Thing":
                    for i in item["roles"]:
                        if _findValue(i, uri_list[1]):
                            uri_list_1 = copy.deepcopy(uri_list)
                            del uri_list_1[:2]
                            _getValue(item, uri_list_1, ml40_model)
                    _f = _findValue({"identifier": item.get("identifier")}, uri_list[1]) or \
                         _findValue({"name": item.get("name")}, uri_list[1])
                    if _f:
                        uri_list_1 = copy.deepcopy(uri_list)
                        del uri_list_1[:2]
                        _getValue(item, uri_list_1, ml40_model)
                else:
                    if _findValue(item, uri_list[1]):
                        uri_list_1 = copy.deepcopy(uri_list)
                        del uri_list_1[:2]
                        if not uri_list_1:
                            resGetValue.append(item)
                            return
                        else:
                            _getValue(item, uri_list_1, ml40_model)
    if isinstance(value, (str, int, float, bool)):
        # if is ditto-feature
        if isinstance(value, str):
            try:
                stringValue_split = value.split(":")
                if stringValue_split[0] == "ditto-feature":
                    value = ml40_model["features"][stringValue_split[1]][
                        "properties"
                    ][uri_list[0]]
            except:
                pass
        resGetValue.append(value)


def _findValue(json, value):
    """Returns true if value has been found in json, otherwise returns false.

    :param json: dictionary
    :param value:
    :returns:
    :rtype:

    """

    # TODO: Simplify: value in json.values()
    for item in json:
        if json[item] == value:
            # print("Parameter: ", json[item])
            return True
    return False
