import abc
import datetime
import json
import logging
import pickle
from dataclasses import dataclass, fields
from decimal import ROUND_HALF_EVEN, Context, Decimal
from enum import Enum
from inspect import getmembers, isclass, ismethod
from json import JSONEncoder
from typing import Generic, Iterable, List, TypeVar, Union
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key


class ConstantString(Enum):
    """
    Holds constant string values. Use it as ConstantString.<STRING_NAME>.value

    To use:
    >>> ConstantString.INVERSE_INDEX_NAME.value
    gsi1
    """

    ITEM_ATTR_NAME = "item_attr_name"
    ITEM_ATTR_TYPE = "item_attr_type"
    ITEM2OBJ_CONV = "item2obj"
    OBJ2ITEM_CONV = "obj2item"
    INVERSE_INDEX_NAME = "inv_index_name"
    INVERSE_INDEX_PK = "inv_index_pk"
    INVERSE_INDEX_SK = "inv_index_sk"
    ENDPOINT_URL = "endpoint_url"
    REGION_NAME = "region_name"
    AWS_ACCESS_KEY_ID = "aws_access_key_id"
    AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"


class SortKeyComparator(Enum):
    EQUALS = 1
    LESS_THAN = 2
    GREATER_THAN = 3
    LESS_THAN_OR_EQUALS = 4
    GREATER_THAN_OR_EQUALS = 5
    BEGINS_WITH = 6


###### ---------- Global parameters ---------- ######
@dataclass
class DynamoDBGlobalConfiguration:
    """
    A singleton to define global parameters related to DynamoDB
    Do not use the __init(...)__ constructor, use the get_instance(...) method
    """

    _instance = None

    _ddb: object
    _tables: dict
    use_aws_cli_credentials: bool
    access_params: dict
    single_table_name_env_var: str
    single_table_pk_attr_name: str
    single_table_sk_attr_name: str
    single_table_inverse_index_properties: dict
    log_debug_messages: bool

    @classmethod
    def get_instance(
        cls,
        ddb: object = None,
        tables: dict = None,
        use_aws_cli_credentials: bool = True,
        access_params: dict = None,
        single_table_name_env_var: str = "DYNAMODB_TABLE_NAME",
        single_table_pk_attr_name: str = "pk",
        single_table_sk_attr_name: str = "sk",
        single_table_inverse_index_properties: dict = None,
        overwrite_existing_instance: bool = False,
        log_debug_messages: bool = True,
    ) -> DynamoDBGlobalConfiguration:
        """
        Get an instance of the singleton.

        Args:
            ddb(str, optional):
                The database connection if None, a connection will be made using the access_params or the credentials
                configured in the aws cli. Defaults to None.
            use_aws_cli_credentials(bool, optional):
                If the aws cli credentials should be used instead of the access_params. Defaults to True.
            access_params(dict, optional):
                A dict with parameters to access the DynamoDB.
                To use this you need to set use_aws_cli_credentials as False.
                The dict should have the following format:
                Defaults to
                    access_params = {
                        ConstantString.ENDPOINT_URL.value: "http://localhost:8000",
                        ConstantString.REGION_NAME.value: "dummy",
                        ConstantString.AWS_ACCESS_KEY_ID.value: "dummy",
                        ConstantString.AWS_SECRET_ACCESS_KEY.value: "dummy"
                    }
            single_table_name_env_var(str, optional):
                The name of the environment variable that holds the name of the single real table on the database.
                Defaults to 'DYNAMODB_TABLE_NAME'.
            single_table_pk_attr_name(str, optional):
                The name of the attribute on the table that holds tha partition key. Defaults to 'pk'.
            single_table_sk_attr_name(str, optional):
                The name of the attribute on the table that holds tha sort key. Defaults to 'sk'.
            single_table_inverse_index_properties(dict, optional):
                The properties of the inverse gsi for querying in the single table design.
                Defaults to
                single_table_inverse_index_properties = {
                    ConstantString.INVERSE_INDEX_NAME.value: 'gsi1',
                    ConstantString.INVERSE_INDEX_PK.value: 'gsi1pk',
                    ConstantString.INVERSE_INDEX_SK.value: 'gsi1sk'
                }
            overwrite_existing_instance(bool, optional):
                If true an instance exists, it will be overwritten. Defaults to False.
            log_debug_messages(bool, optional):
                If true debug messages will be logged at the info level. Defaults to True.
                (The default will be changed to False in the near future)
        Returns:
            a DynamoDBGlobalConfiguration instance
        """

        if cls._instance is None or overwrite_existing_instance:
            tables = tables if tables is not None else {}
            if single_table_inverse_index_properties is None:
                single_table_inverse_index_properties = {
                    ConstantString.INVERSE_INDEX_NAME.value: "gsi1",
                    ConstantString.INVERSE_INDEX_PK.value: "gsi1pk",
                    ConstantString.INVERSE_INDEX_SK.value: "gsi1sk",
                }
            if access_params is None:
                access_params = {
                    ConstantString.ENDPOINT_URL.value: "http://localhost:8000",
                    ConstantString.REGION_NAME.value: "dummy",
                    ConstantString.AWS_ACCESS_KEY_ID.value: "dummy",
                    ConstantString.AWS_SECRET_ACCESS_KEY.value: "dummy",
                }
            elif (
                not {
                    ConstantString.ENDPOINT_URL.value,
                    ConstantString.REGION_NAME.value,
                    ConstantString.AWS_ACCESS_KEY_ID.value,
                    ConstantString.AWS_SECRET_ACCESS_KEY.value,
                }
                <= set(access_params)
            ):
                use_aws_cli_credentials = True
                logging.warning(
                    "The provided access_params "
                    + str(access_params)
                    + " is missing required values, trying"
                    " to use the aws cli credentials"
                )
            cls._instance = cls(
                ddb,
                tables,
                use_aws_cli_credentials,
                access_params,
                single_table_name_env_var,
                single_table_pk_attr_name,
                single_table_sk_attr_name,
                single_table_inverse_index_properties,
                log_debug_messages,
            )
        return cls._instance

    @classmethod
    def is_instantiated(cls) -> bool:
        return cls._instance is not None

    def get_connection(self) -> object:
        if self._ddb is None:  # Connect to the database if ddb is None
            try:
                if self.use_aws_cli_credentials:
                    self._ddb = boto3.resource("dynamodb")
                else:
                    self._ddb = boto3.resource(
                        "dynamodb",
                        endpoint_url=self.access_params["endpoint_url"],
                        region_name=self.access_params["region_name"],
                        aws_access_key_id=self.access_params["aws_access_key_id"],
                        aws_secret_access_key=self.access_params[
                            "aws_secret_access_key"
                        ],
                    )
            except Exception as ex:
                logging.error(str(ex))
                raise ConnectionRefusedError("Not able to connect to DynamoDB")
        return self._ddb

    def get_table(self, table_name) -> object:
        if table_name not in self._tables:
            try:
                self._tables[table_name] = self.get_connection().Table(table_name)
            except Exception as ex:
                logging.error(str(ex))
                warning_str = (
                    "Could not access table "
                    + str(table_name)
                    + " check if the table exists"
                )
                raise ResourceWarning(warning_str)
        return self._tables[table_name]


###### ---------- Global parameters ---------- ######

###### ---------- Wrapper fo mappable classes ---------- ######
def _dict_if_none(a_dict) -> dict:
    a_dict = a_dict if a_dict is not None else {}
    return a_dict


def _list_if_none(a_list) -> dict:
    a_list = a_list if a_list is not None else []
    return a_list


def _wrap_class(  # noqa: C901
    cls=None,  # noqa: C901
    table_name: str = None,  # noqa: C901
    unique_id: str = None,  # noqa: C901
    mapping_schema: dict = None,  # noqa: C901
    ignore_attributes: list = None,  # noqa: C901
):  # noqa: C901
    """
    Adds classmethods to the provided class, to be used by only the dynamo_entity decorator
    """

    if hasattr(cls, "dynamo_pk"):  # The class has already been decorated
        return cls
    mapping_schema = _dict_if_none(mapping_schema)
    ignore_attributes = _list_if_none(ignore_attributes)
    # May causes collisions if there are other entities with the same name
    table_name = table_name if table_name is not None else cls.__name__

    # The methods to be added to the class
    @classmethod
    def dynamo_table_name(cls) -> str:
        return table_name

    @classmethod
    def dynamo_id(cls) -> str:
        return unique_id

    @classmethod
    def dynamo_map(cls) -> dict:
        return mapping_schema

    @classmethod
    def dynamo_ignore(cls) -> list:
        return ignore_attributes

    # set the table name
    cls._dynamo_table_name = dynamo_table_name

    # set the id
    cls._dynamo_id = dynamo_id

    # set the mapping of class attributes to table attributes
    cls._dynamo_map = dynamo_map

    # set the class attributes that will be ignored (not saved on the database)
    cls._dynamo_ignore = dynamo_ignore

    # To add non lambda functions, define the function first them assign it to cls.<function_name>

    return cls


def dynamo_entity(
    cls=None,
    table_name: str = None,
    unique_id: str = None,
    mapping_schema: dict = None,
    ignore_attributes: Union[list, tuple] = None,
):
    """
    Wraps a class so it is mappable to DynamoDB. Use it as a decorator.
    The entity class has to allow an empty constructor call.

    DynamoDB uses partition keys (pk) and sort keys (sk) to define a unique data entry,
    If you are not familiar with DynamoDB, this library can generate this keys if you provide just an id attribute
    However pay attention to this two rules:
    - If you provide a pk, the logical table and the id parameters will be ignored.
    - If you do not provide a pk, it is necessary to provide an id, the pk attribute's name on the database table as
    pk_name_on_table, and the sk attribute's name on the database table as sk_name_on_table.

    Args:
        dynamo_real_table(str, optional):
            The DynamoDB table name, if no name is provided, the class name will be used. Defaults to None
        pk(str, optional):
            The name of the attribute that will be used as the partition key on DynamoDB if the pk will be explicit in
            each object of the decorated class. Using this will ignore the id and logical_table. Defaults to None
        sk(str, optional):
            The name of the attribute that will be used as the sort key if the pk and sk will be explicit in each object
            of the decorated class. Can be also be None if there is no sort key. Defaults to None.
        table_name(str,optional):
            The name of the logical or real table on the database.
        unique_id(str, optional):
            The name of the attribute that will be used as the id, necessary if the pk parameter is not provided.
            The attribute will be cast to str. Defaults to None
        mapping_schema(dict, optional):
            A dict mapping the class attributes to the item attributes on DynamoDB.
            The map should have the following format:
            mapping_schema={
                <class_attribute_name>: {
                    ConstantString.ITEM_ATTR_NAME.value: <string with the attribute's name on the DynamoDB table>,
                    ConstantString.ITEM_ATTR_TYPE.value: <string with the attribute's type on the DynamoDB table>,
                    ConstantString.ITEM2OBJ_CONV.value: <convert function that receives the DynamoDB item's attribute
                                                        and returns the object attribute>,
                    ConstantString.OBJ2ITEM_CONV.value: <convert function that receives the object attribute and
                                                        returns DynamoDB item's attribute>
            }
            If no mapping is provided for a particular (or all) class attribute, the class attribute names and
            standard conversion functions will be used. Defaults to None
        ignore_attributes(list[str], optional):
            A list with the name of the class attributes that should not be saved to/loaded from the database.
            Defaults to None
    Returns:
        class: The decorated class.
    """

    def wrap(cls):
        return _wrap_class(
            cls,
            table_name,
            unique_id,
            mapping_schema,
            ignore_attributes,
        )

    if cls is None:
        return wrap

    return wrap(cls)


###### ---------- Wrapper fo mappable classes ---------- ######


###### ---------- Class with standard conversion functions ---------- ######


class DynamoConversions:
    """
    [In development]
    This is a static class with classmethods to convert data from python data types to DynamoDB data types
    """

    decimal_context = Context(prec=15, rounding=ROUND_HALF_EVEN)

    class CustomEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            try:
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            # Let the base class default method raise the TypeError
            return JSONEncoder.default(self, obj)

    @classmethod
    def get_custom_encoder(cls) -> JSONEncoder:
        return cls.CustomEncoder

    @classmethod
    def get_decimal_context(cls) -> Context:
        return cls.decimal_context

    @classmethod
    def type_cast(cls, target_type: type, value) -> object:
        return target_type(value)

    @classmethod
    def identity(cls, value) -> object:
        return value

    @classmethod
    def list_and_dict_to_dynamo(cls, value: Union[list, dict]) -> str:
        return json.dumps(value)

    @classmethod
    def list_and_dict_from_dynamo(cls, value: str) -> Union[list, dict]:
        return json.loads(value)

    @classmethod
    def tuple_to_dynamo(cls, value: tuple) -> str:
        return json.dumps(list(value))

    @classmethod
    def tuple_from_dynamo(cls, value: str) -> tuple:
        return tuple(json.loads(value))

    @classmethod
    def string_set_to_dynamo(cls, value: set) -> set:
        for old_elem in value:
            if not isinstance(old_elem, str):
                new_elem = str(old_elem)
                value.remove(old_elem)
                value.add(new_elem)
        return set(value)

    @classmethod
    def bytes_set_to_dynamo(cls, value) -> set:
        for old_elem in value:
            if not isinstance(old_elem, bytes):
                new_elem = bytes(old_elem)
                value.remove(old_elem)
                value.add(new_elem)
        return set(value)

    @classmethod
    def bytes_set_from_dynamo(cls, value) -> set:
        new_set = set()
        for old_elem in value:
            # boto3 uses its own binary type old_elm.value gets the binary value in the bytes python type
            new_set.add(old_elem.value)
        return new_set

    @classmethod
    def bytearray_set_from_dynamo(cls, value) -> set:
        new_set = set()
        for old_elem in value:
            # boto3 uses its own binary type old_elm.value gets the binary value in the bytes python type
            new_set.add(bytearray(old_elem.value))
        return new_set

    @classmethod
    def number_set_to_dynamo(cls, value) -> set:
        new_set = set()
        for old_elem in value:
            new_set.add(cls.decimal_context.create_decimal(old_elem))
        return new_set

    @classmethod
    def int_set_from_dynamo(cls, value) -> set:
        new_set = set()
        for old_elem in value:
            new_set.add(int(old_elem))
        return new_set

    @classmethod
    def float_set_from_dynamo(cls, value) -> set:
        new_set = set()
        for old_elem in value:
            new_set.add(float(old_elem))
        return new_set

    @classmethod
    def enum_to_dynamo(cls, value) -> object:
        return value.value

    @classmethod
    def gen_enum_from_dynamo_for_enum_type(cls, enum_type) -> Any:
        value2member_map = enum_type._value2member_map_
        return lambda value: value2member_map[value]


###### ---------- Repository Interfaces and Implementation ---------- ######

T = TypeVar("T")  # A generic type var to hold Entity classes


class Repository(Generic[T], metaclass=abc.ABCMeta):
    """
    Just a simple "interface" inspired by the Java Spring Repository Interface
    """

    entity_type: T
    pass

    def check_provided_type(self):
        """Returns True if obj is a dynamo_entity class or an instance of a dynamo_entity class."""
        cls = T if isinstance(T, type) else type(T)
        return hasattr(cls, "_FIELDS")


class CrudRepository(Repository, metaclass=abc.ABCMeta):
    """
    Just a simple "interface" inspired by the Java Spring CrudRepository Interface
    """

    @abc.abstractmethod
    def count(self) -> int:
        """
        Counts the number of items in the table

        Returns:
            An int with the number of items in the table.
        """
        pass

    @abc.abstractmethod
    def remove(self, entity: T) -> bool:
        """
        Removes an entity object from the database

        Args:
            entity: An object of the mapped entity class to be removed

        Returns:
            True if the object was removed or was not stored in the database
            False otherwise
        """
        pass

    @abc.abstractmethod
    def remove_all(self) -> bool:
        """
        Removes every entity of the mapped class from the database

        Returns:
            True if there are no entities of the mapped class in the database anymore
            False otherwise
        """
        pass

    @abc.abstractmethod
    def remove_by_keys(self, keys: Union[dict, list]) -> bool:
        """
        Removes every entity(ies) from the using the provided keys

        Args:
            keys(Union[dict, list]):
                A (pair of) key(s) that identify the entity(ies)

        Returns:
            True if the object was removed or was not there already;
            False otherwise
        """
        pass

    @abc.abstractmethod
    def remove_all_by_keys(self, keys: Union[Iterable[dict], Iterable[list]]) -> bool:
        """
        Removes every entity(ies) that matches the provided keys

        Args:
            keys(Union[Iterable[dict], Iterable[list]]):
                a (pair of) key(s) that identify the entity(ies)

        Returns:
            True if there are no entities of the mapped class in the database anymore;
            False otherwise
        """
        pass

    @abc.abstractmethod
    def exists_by_keys(self, keys: Union[dict, list]) -> bool:
        """
        Checks if an entity identified by the provided keys exist in the database

        Args:
            keys(Union[dict, list]):
                a (pair of) key(s) that identify the entity

        Returns:
            True if a matching entry exist in the database;
            False otherwise
        """
        pass

    @abc.abstractmethod
    def find_all(self) -> list:
        """
        Gets all entities of the mapped class from the database

        Returns:
            A list with all the entities of the mapped class
        """
        pass

    @abc.abstractmethod
    def find_by_keys(self, keys: Union[dict, list]) -> Union[object, list, None]:
        """
        Gets all entities of the mapped class that match the provided keys from the database

        Args:
            keys(Union[dict, list]):
                A (pair of) key(s) that identify the entity

        Returns:
            An object of the mapped class if only one entity matches the keys;
            A list of objects of the mapped class if multiple entities match the keys;
            None if no entities match the keys
        """
        pass

    @abc.abstractmethod
    def save(self, obj: T) -> bool:
        """
        Stores an entity in the database

        Args:
            obj: an object of the mapped class to save

        Returns:
            True if the object was stored in the database;
            False otherwise
        """
        pass

    @abc.abstractmethod
    def save_all(self, entities: Iterable[T]) -> bool:
        """
        Stores a collection of entities in the database

        Args:
            entities(Iterable): objects of the mapped class to save

        Returns:
            True if the objects were stored in the database;
            False otherwise
        """
        pass


def _pk2id(pk) -> str:
    """
    Get a single table unique_id from a partition key
    Args:
        pk: the partition key

    Returns: the unique id

    """
    return pk.split("#", 1)[1]


class DynamoCrudRepository(CrudRepository, metaclass=abc.ABCMeta):
    table = None
    table_name: str = None
    map_dict: map = None
    map_filled: bool = False

    def __init__(self, entity_type: T, dynamo_table_name: str = None):
        """
        Creates a new DynamoCrudRepository for a specific dynamo_entity class

        Args:
            entity_type(class):
                The class decorated with dynamo_entity that should be mapped to DynamoDB items.
            dynamo_table_name(str, optional):
                The name of the real table on DynamoDB
        """
        if entity_type is None:
            raise ValueError("You need to provide an entity_type class")
        self.entity_type = entity_type

        self.map_dict = self.entity_type._dynamo_map()
        self._fill_map_dict(self.entity_type)

        # For a single table design, define the table name as a global parameter,
        # if the table name is not set in the global parameters, will use the entity class table name
        if dynamo_table_name is None:
            raise ValueError("You need to provide the dynamo table name")
        self.table_name = dynamo_table_name

    def get_table_if_none(self) -> None:
        """
        If self.table is None, gets the table using the DynamoDBGlobalConfiguration and sets self.table
        """
        if self.table is None:
            self.table = DynamoDBGlobalConfiguration.get_instance().get_table(
                self.table_name
            )

    def find_collection(
        self,
        key_condition_expression=None,
        index_name: str = None,
        keys: dict = None,
        ordered_key_names: Iterable[str] = None,
        sk_comparator: SortKeyComparator = None,
        limit: int = -1,
        exclusive_start_key=None,
        page: int = None,
        exceed_dynamo_query_limit: bool = False,
    ) -> List[Any]:
        """
        Finds the list of items that match the provided key_condition_expression using the provided index_name

        Args:
            key_condition_expression:
                a DynamoDB KeyConditionExpression
            index_name(str, optional):
                the name of the index to query
            keys(dict, optional):
                a dict {"attribute_name": "attribute_vale"} with a single key or a key pair
            ordered_key_names(Iterable[str], optional):
                the key names in the order [pk, sk].
                Defaults to the key names in alphabetic order.
            sk_comparator(SortKeyComparator, optional):
                the comparison operation between the item sort key and the provided value.
            limit(int, optional):
                the maximum number of items that should be returned.
                the page size for paginated queries.
                Mandatory if <page> is not None.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page
            page(int, optional):
                for paginated queries, the requested page. Each page will have <limit> items.
                Note: Page numbers start at 0.
                This parameter will be ignored if a exclusive_start_key is provided
            exceed_dynamo_query_limit(bool, optional):
                will exceed the limit that DynamoDB will return in a single table.query request if there are more items.
                This parameter will be ignored if an exclusive_start_key or a page is provided
                Defaults to False

        Returns:
            a list of instance objects
        """
        query_args = {}
        if key_condition_expression is not None:
            query_args["KeyConditionExpression"] = key_condition_expression
        elif keys is not None:
            keys_tuple = self.keys2KeyConditionExpression(
                keys, ordered_key_names, sk_comparator
            )
            query_args["KeyConditionExpression"] = keys_tuple[0]
            query_args["ExpressionAttributeValues"] = keys_tuple[1]
        else:
            raise TypeError(
                "missing argument, need to provide either 'key_condition_expression' or 'key' argument"
            )
        if index_name is not None:
            query_args["IndexName"] = index_name
        if limit is not None and limit > 0:
            query_args["Limit"] = limit
        self.get_table_if_none()

        if exclusive_start_key is not None:
            query_args["ExclusiveStartKey"] = exclusive_start_key
            exceed_dynamo_query_limit = False

        elif page is not None and page >= 0:
            if limit < 1:
                # LOG
                logging.warning(
                    "Not able get page "
                    + str(page)
                    + " of table "
                    + str(self.table_name)
                    + " with the specified limit (page size): "
                    + str(limit)
                    + " with parameters"
                    + str(query_args)
                    + "\nThe limit should be specified and an integer above 0 "
                )
                return None

            for i in range(
                page
            ):  # Skip the previous pages and sets the ExclusiveStartKey
                try:
                    response = self.table.query(**query_args)
                except Exception as ex:
                    # LOG
                    logging.warning(
                        "Not able to query table "
                        + str(self.table_name)
                        + " with parameters"
                        + str(query_args)
                        + "\nDynamoError: "
                        + str(ex)
                    )
                    return None
                if "LastEvaluatedKey" in response:
                    query_args["ExclusiveStartKey"] = response["LastEvaluatedKey"]
                else:
                    # LOG
                    logging.warning(
                        "Not able get page "
                        + str(page)
                        + " of table "
                        + str(self.table_name)
                        + " with parameters"
                        + str(query_args)
                        + "\nCheck if the table has sufficient items "
                    )
                    return None

        entity_list = []

        try:
            response = self.table.query(**query_args)
        except Exception as ex:
            # LOG
            logging.warning(
                "Not able to query table "
                + str(self.table_name)
                + " with parameters"
                + str(query_args)
                + "\nDynamoError: "
                + str(ex)
            )
            return None

        if "Items" in response:
            items = response["Items"]
            for item in items:
                entity_list.append(self.item2instance(item))

        if exceed_dynamo_query_limit and "LastEvaluatedKey" in response:
            query_args["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            while "LastEvaluatedKey" in response:
                # Making sure that it does not return more items than limit
                if isinstance(limit, int) and limit > 0:
                    query_args["Limit"] = limit - len(entity_list)
                    if query_args["Limit"] <= 0:
                        break
                try:
                    response = self.table.query(**query_args)
                except Exception as ex:
                    # LOG
                    logging.warning(
                        "Not able to query table "
                        + str(self.table_name)
                        + " with parameters"
                        + str(query_args)
                        + "\nDynamoError: "
                        + str(ex)
                    )
                    return None

                if "Items" in response:
                    items = response["Items"]
                    for item in items:
                        entity_list.append(self.item2instance(item))
                else:
                    break

        return entity_list

    def find_collection_with_start_key(
        self,
        key_condition_expression=None,
        index_name: str = None,
        keys: dict = None,
        ordered_key_names: Iterable[str] = None,
        sk_comparator: SortKeyComparator = None,
        limit: int = -1,
        exclusive_start_key=None,
    ) -> Tuple[list, object]:
        """
        Finds the list of items that match the provided key_condition_expression using the provided index_name.
        Returns a paged result with up to <limit> items starting at <exclusive_start_key>.

        Args:
            key_condition_expression:
                a DynamoDB KeyConditionExpression
            index_name(str, optional):
                the name of the index to query
            keys(dict, optional):
                a dict {"attribute_name": "attribute_vale"} with a single key or a key pair
            ordered_key_names(Iterable[str], optional):
                the key names in the order [pk, sk].
                Defaults to the key names in alphabetic order.
            sk_comparator(SortKeyComparator, optional):
                the comparison operation between the item sort key and the provided value.
            limit(int, optional):
                the maximum number of items that should be returned.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page

        Returns:
            a tuple with:
                1: a list of instance objects
                2: the LastEvaluatedKey returned by the DynamoDB query, None if it is the last page
        """
        query_args = {}
        if key_condition_expression is not None:
            query_args["KeyConditionExpression"] = key_condition_expression
        elif keys is not None:
            keys_tuple = self.keys2KeyConditionExpression(
                keys, ordered_key_names, sk_comparator
            )
            query_args["KeyConditionExpression"] = keys_tuple[0]
            query_args["ExpressionAttributeValues"] = keys_tuple[1]
        else:
            raise TypeError(
                "missing argument, need to provide either 'key_condition_expression' or 'key' argument"
            )
        if index_name is not None:
            query_args["IndexName"] = index_name
        if limit is not None and limit > 0:
            query_args["Limit"] = limit
        self.get_table_if_none()

        if exclusive_start_key is not None:
            query_args["ExclusiveStartKey"] = exclusive_start_key
        else:
            raise TypeError(
                "missing argument, need to provide the 'exclusive_start_key' argument"
            )

        entity_list = []
        last_evaluated_key = None

        try:
            response = self.table.query(**query_args)
        except Exception as ex:
            # LOG
            logging.warning(
                "Not able to query table "
                + str(self.table_name)
                + " with parameters"
                + str(query_args)
                + "\nDynamoError: "
                + str(ex)
            )
            return None

        if "Items" in response:
            items = response["Items"]
            for item in items:
                entity_list.append(self.item2instance(item))

        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]

        return entity_list, last_evaluated_key

    @abc.abstractmethod
    def count(self):
        """
        Counts the number of items in the table

        Returns:
            An int with the number of items in the table.
        """
        pass

    @abc.abstractmethod
    def key_list2key_map(self, keys: Union[dict, list]):
        pass

    def _id2key_pair(self, unique_id):
        """
        Generates the pk, sk key pair using an unique_id
        Args:
            unique_id: an object's unique_id

        Returns: a dict with pk and sk
        """
        sk = self.entity_type._dynamo_table_name()
        pk = self.entity_type._dynamo_table_name() + "#" + str(unique_id)
        keys = {
            DynamoDBGlobalConfiguration.get_instance().single_table_pk_attr_name: pk,
            DynamoDBGlobalConfiguration.get_instance().single_table_sk_attr_name: sk,
        }
        return keys

    def remove_by_keys(self, keys: Union[dict, list]):
        """
        Deletes objects stored in the database using the given keys
        Args:
            keys(Union[dict, list]): a set of keys to search for the object.
            If a list if provided, assumes the pattern [pk, sk]

        Returns:
            True if the object was removed or was not there already;
            False otherwise
        """

        self.get_table_if_none()
        if isinstance(keys, list):  # Produce dict from list
            keys = self.key_list2key_map(keys)
        try:
            return bool(self.table.delete_item(Key=keys))
        except Exception as ex:
            logging.error(str(ex))
            logging.warning(
                "Not able to delete item with keys"
                + str(keys)
                + "from table"
                + str(self.table_name)
                + "\nDynamoError: "
                + str(ex)
            )
            return False

    def remove_by_id(self, unique_id):
        """
        Remove an object of the mapped class from the database using a unique id

        Args:
            unique_id: a unique id that identify the object

        Returns:
            True if the object was removed or was not there already;
            False otherwise
        """
        pass

    # flake8: noqa: C901
    def item_attr2_instance_attr(
        self, item_attr_val, instance_attr_name: str, instance_attr_type: type
    ):  # flake8: noqa: C901
        """
        Converts an item attribute to an instance attribute
        Args:
            item_attr_val: the value of the item attribute
            instance_attr_name(str): the name of instance attribute that will be returned
            instance_attr_type(type): the type of the instance attribute

        Returns: the value of the equivalent instance attribute
        """

        if not isclass(instance_attr_type):  # Try to get the class type
            # Try to get the class type from typings.NewType
            if hasattr(instance_attr_type, "__supertype__"):
                instance_attr_type = instance_attr_type.__supertype__
            # Try to get the class type from typings.Generic. Not an elif, the NewType may be an alias for a Generic
            if hasattr(instance_attr_type, "__origin__"):
                instance_attr_type = instance_attr_type.__origin__

        if ConstantString.ITEM2OBJ_CONV.value in self.map_dict[instance_attr_name]:
            return self.map_dict[instance_attr_name][
                ConstantString.ITEM2OBJ_CONV.value
            ](item_attr_val)

        # boto3 uses its own binary type that can not be directly converted to bytes
        if isinstance(item_attr_val, boto3.dynamodb.types.Binary):
            item_attr_val = item_attr_val.value

        # convert to string then to the actual type to make sure the conversion will work
        if issubclass(instance_attr_type, int):
            return instance_attr_type(int(item_attr_val))

        elif issubclass(instance_attr_type, float):
            return instance_attr_type(float(item_attr_val))

        elif issubclass(instance_attr_type, Decimal):
            return instance_attr_type(Decimal(item_attr_val))

        elif issubclass(
            instance_attr_type, bytearray
        ):  # bytearrays are stored as bytes and need to be cast
            return bytearray(bytes(item_attr_val))

        elif issubclass(
            instance_attr_type, (bytes, bool, UUID)
        ):  # Perform a direct conversion
            return instance_attr_type(item_attr_val)

        elif issubclass(
            instance_attr_type, (set, frozenset, tuple)
        ):  # load the json and cast to set or tuple
            return instance_attr_type(json.loads(item_attr_val))

        elif issubclass(instance_attr_type, (dict, list)):  # json
            return json.loads(item_attr_val)

        elif issubclass(instance_attr_type, Enum):  # Enum
            return instance_attr_type[item_attr_val]

        elif issubclass(instance_attr_type, str):
            return str(item_attr_val)

        # Use the iso format for storing datetime as strings
        elif issubclass(
            instance_attr_type, (datetime.date, datetime.time, datetime.datetime)
        ):
            return instance_attr_type.fromisoformat(item_attr_val)

        elif issubclass(instance_attr_type, object):  # objects in general are pickled
            return pickle.loads(item_attr_val)

        else:  # No special case, use a simple cast, probably will never be reached
            return instance_attr_type(item_attr_val)

    def item2instance(self, item):
        """
        Converts a DynamoDB item to an instance of the mapped class.

        Args:
            item(dict): the DynamoDB item attributes

        Returns:
            an instance of the mapped class
        """
        log_dict = {
            "Level": "[FINE]",
            "method": "DynamoCrudRepository.item2instance",
            "Error": "No error, the method was just called",
            "Provided_Args": {
                "item": str(item),
            },
        }
        instance_attributes = {}
        logging.info("Converting item to instance, received item is\n: " + str(item))
        for fl in fields(self.entity_type):
            item_attr_name = self.map_dict[fl.name][ConstantString.ITEM_ATTR_NAME.value]
            if item_attr_name in item:
                instance_attributes[fl.name] = self.item_attr2_instance_attr(
                    item[item_attr_name], fl.name, fl.type
                )
        log_dict = {
            "Level": "[FINE]",
            "method": "DynamoCrudRepository.item2instance",
            "message": "trying to create the entity using packed arguments",
            "Packed_Args": str(instance_attributes),
        }
        entity_instance = self.entity_type(**instance_attributes)
        return entity_instance

    def find_by_keys(self, keys: Union[dict, list]):
        """
         Finds an object stored in the database using the given keys that compose a unique primary key
        Args:
            keys(Union[dict, list]): a set of keys to search for the object.

        Returns:
            an object of the mapped class
        """
        self.get_table_if_none()
        log_dict = {
            "Level": "[FINE]",
            "method": "SingleTableCrudRepository.find_by_keys",
            "Error": "No error, the method was just called",
            "Provided_Args": {
                "keys": str(keys),
            },
        }
        if isinstance(keys, list):  # Produce dict from list
            keys = self.key_list2key_map(keys)
        try:
            response = self.table.get_item(Key=keys)

            if "Item" in response:
                item = response[
                    "Item"
                ]  # item is a dict {table_att_name: table_att_value}
                return self.item2instance(item)
            else:
                if DynamoDBGlobalConfiguration.get_instance().log_debug_messages:
                    log_dict = {
                        "Level": "[FINE]",
                        "method": "SingleTableCrudRepository.find_by_keys",
                        "Error": "Item not found",
                        "Provided_Args": {
                            "keys": str(keys),
                        },
                    }
                    logging.info(str(log_dict))
                return None
        except Exception as ex:
            logging.error(str(ex))
            return None

    def find_by_id(self, unique_id):
        """
        Finds an entity object by the unique id
        Args:
            unique_id: the object id

        Returns:
            an object of the mapped class
        """
        self.get_table_if_none()
        instance_obj = self.find_by_keys(self._id2key_pair(unique_id))
        if (
            instance_obj is None
            and DynamoDBGlobalConfiguration.get_instance().log_debug_messages
        ):
            log_dict = {
                "Level": "[FINE]",
                "method": "DynamoCrudRepository.find_by_id",
                "Error": "Item not found",
                "Provided_Args": {
                    "unique_id": str(unique_id),
                },
            }
            logging.info(str(log_dict))
        return instance_obj

    def keys2KeyConditionExpression(
        self,
        keys: dict,
        ordered_key_names: Iterable[str] = None,
        sk_comparator: SortKeyComparator = None,
    ):
        """
        Generate KeyConditionExpression and ExpressionAttributeValues using a key set
        Args:
            keys(dict): the item keys
            ordered_key_names(Iterable[str], optional): the key names in the order [pk, sk].
            Defaults to the key names in alphabetic order.
            sk_comparator(SortKeyComparator, optional): the comparison operation between
            the item sort key and the provided value.

        Returns:
            KeyConditionExpression
            ExpressionAttributeValues
        """
        buffer = ""
        exp_att_val = {}
        if ordered_key_names is None:
            ordered_key_names = sorted(keys.keys())
        if sk_comparator is None:
            sk_comparator = SortKeyComparator.EQUALS
        # Partition Key
        key_name = ordered_key_names[0]
        buffer += str(key_name) + " = :" + str(key_name) + "val"
        exp_att_val[":" + str(key_name) + "val"] = keys[key_name]
        if len(ordered_key_names) > 1:
            key_name = ordered_key_names[1]
            buffer += " AND "
            if sk_comparator == SortKeyComparator.EQUALS:
                buffer += str(key_name) + " = :" + str(key_name) + "val"
            elif sk_comparator == SortKeyComparator.BEGINS_WITH:
                buffer += (
                    "begins_with ( " + str(key_name) + ", :" + str(key_name) + "val )"
                )
            elif sk_comparator == SortKeyComparator.LESS_THAN:
                buffer += str(key_name) + " < :" + str(key_name) + "val"
            elif sk_comparator == SortKeyComparator.GREATER_THAN:
                buffer += str(key_name) + " > :" + str(key_name) + "val"
            elif sk_comparator == SortKeyComparator.LESS_THAN_OR_EQUALS:
                buffer += str(key_name) + " <= :" + str(key_name) + "val"
            elif sk_comparator == SortKeyComparator.GREATER_THAN_OR_EQUALS:
                buffer += str(key_name) + " >= :" + str(key_name) + "val"
            else:
                raise ValueError("Invalid SortKeyComparator " + str(sk_comparator))

            exp_att_val[":" + str(key_name) + "val"] = keys[key_name]

        return buffer, exp_att_val

    @abc.abstractmethod
    def find_all(self):
        """
        Gets all entities of the mapped class from the database

        Returns:
            A list with all the entities of the mapped class
        """
        pass

    @abc.abstractmethod
    def instance2item_params_inject_keys(self, obj: T, item_params: dict = None):
        """
        Part of the process of converting an entity object to a DynamoDB item. Inject the keys to the item_params.
        Args:
            obj: the entity object that will be converted to a DynamoDB item
            item_params (dict, optional): the dictionary with the DynamoDB item attributes

        Returns:
            the item_params dict with the keys injected
        """
        pass

    # flake8: noqa: C901
    def instance_attr2_item_attr(
        self, instance_attr_val, instance_attr_name: str
    ):  # flake8: noqa: C901
        """
        Convert an instance attribute to the equivalent item attribute
        Args:
            instance_attr_val: the value of the instance attribute
            instance_attr_name(str): the name of the instance attribute

        Returns:
            item_attr_val: the value of the equivalent item attribute
            item_attr_name: the name of the equivalent item attribute
        """
        item_attr_name = self.map_dict[instance_attr_name][
            ConstantString.ITEM_ATTR_NAME.value
        ]
        item_attr_val = None
        if ConstantString.OBJ2ITEM_CONV.value in self.map_dict[instance_attr_name]:
            item_attr_val = self.map_dict[instance_attr_name][
                ConstantString.OBJ2ITEM_CONV.value
            ](instance_attr_val)
        # switch self.map_dict[<attribute_name>]
        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "N"
        ):  # case 'N' (number)
            item_attr_val = DynamoConversions.get_decimal_context().create_decimal(
                instance_attr_val
            )  # str cast to support numpy, pandas, etc

        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "B"
        ):  # case 'B' (bytes)
            if isinstance(instance_attr_val, (bytes, bytearray)):
                item_attr_val = bytes(instance_attr_val)
            elif isinstance(
                instance_attr_val, object
            ):  # objects in general are pickled
                item_attr_val = pickle.dumps(instance_attr_val)
            else:
                raise TypeError("Only bytes and objects should be stored as bytes")
        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "BOOL"
        ):  # case 'BOOL' (boolean)
            item_attr_val = 1 if instance_attr_val else 0

        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "BS"
        ):
            for old_value in instance_attr_val:
                if not isinstance(old_value, bytes):
                    new_value = bytes(old_value)
                    instance_attr_val.remove(old_value)
                    instance_attr_val.add(new_value)
            item_attr_val = set(instance_attr_val)

        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "NS"
        ):
            for old_value in instance_attr_val:
                if not isinstance(old_value, Decimal):
                    new_value = DynamoConversions.get_decimal_context().create_decimal(
                        old_value
                    )
                    instance_attr_val.remove(old_value)
                    instance_attr_val.add(new_value)
            item_attr_val = set(instance_attr_val)

        elif (
            self.map_dict[instance_attr_name][ConstantString.ITEM_ATTR_TYPE.value]
            == "SS"
        ):
            for old_value in instance_attr_val:
                if not isinstance(old_value, str):
                    new_value = str(old_value)
                    instance_attr_val.remove(old_value)
                    instance_attr_val.add(new_value)
            item_attr_val = set(instance_attr_val)

        else:  # default (string)
            # Consider special cases and use specific string formats
            # datetime
            if isinstance(
                instance_attr_val, (datetime.date, datetime.time, datetime.datetime)
            ):
                item_attr_val = instance_attr_val.isoformat()

            # enum
            elif isinstance(instance_attr_val, Enum):
                item_attr_val = instance_attr_val.name
            # sets and tuples (cast to list and converted to json)
            elif isinstance(instance_attr_val, (set, frozenset, tuple)):
                item_attr_val = json.dumps(
                    list(instance_attr_val), cls=DynamoConversions.get_custom_encoder()
                )

            # maps and lists (converted to json)
            elif isinstance(instance_attr_val, (dict, list)):
                item_attr_val = json.dumps(
                    instance_attr_val, cls=DynamoConversions.get_custom_encoder()
                )

            # strings
            elif isinstance(instance_attr_val, str):
                item_attr_val = str(instance_attr_val)
            # No special case, use a simple str cast
            else:
                item_attr_val = str(instance_attr_val)
        return item_attr_val, item_attr_name

    def instance2item_params_inject_attributes(self, obj: T, item_params: dict = None):
        """
        Part of the process of converting an entity object to a DynamoDB item. Inject the non-key attributes
        to the item_params.
        Args:
            obj: the entity object that will be converted to a DynamoDB item
            item_params (dict, optional): the dictionary with the DynamoDB item attributes

        Returns:
            the item_params dict with the non-key attributes injected
        """
        item_params = item_params if item_params is not None else {}
        # Get every attribute of obj, ignoring private members and methods
        for instance_attr in getmembers(obj):
            if (
                (not instance_attr[0].startswith("_"))  # ignore private attributes
                and (not ismethod(instance_attr[1]))  # ignore methods
                and (
                    not instance_attr[0] in obj._dynamo_ignore()
                )  # ignore the attributes on the list to ignore
            ):
                instance_attr_name = instance_attr[0]
                instance_attr_val = instance_attr[1]
                if instance_attr_val is not None and not (
                    hasattr(instance_attr_val, "__len__") and len(instance_attr_val) < 1
                ):
                    item_attr_val, item_attr_name = self.instance_attr2_item_attr(
                        instance_attr_val, instance_attr_name
                    )
                    item_params[item_attr_name] = item_attr_val
        return item_params

    def instance2item_params(self, obj: T):
        """
        Execute the conversion of an entity object to a DynamoDB item.
        Args:
            obj: the entity object that will be converted to a DynamoDB item

        Returns:
            a dict with the attributes of the equivalent DynamoDB item
        """
        item_params = {}
        self.instance2item_params_inject_keys(obj, item_params)
        self.instance2item_params_inject_attributes(obj, item_params)
        return item_params

    def save(self, obj: T):
        """
        Stores an entity in the database

        Args:
            obj: an object of the mapped class to save

        Returns:
            True if the object was stored in the database;
            False otherwise
        """
        self.get_table_if_none()
        item_params = self.instance2item_params(obj)
        try:
            self.table.put_item(Item=item_params)
            return True
        except Exception as ex:
            logging.error(str(ex))
            logging.warning(
                "Not able to put item"
                + str(item_params)
                + " in table"
                + str(self.table_name)
                + "\nDynamoError: "
                + str(ex)
            )
            return False

    @abc.abstractmethod
    def remove_entity_list(self, entity_list: Iterable):
        """
        Removes multiple entity objects from the database
        Args:
            entity_list(Iterable): the entities to be removed

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        pass

    def remove_all(self):
        """
        Removes all objects of the entity type from the database

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        entity_list = self.find_all()
        return self.remove_entity_list(entity_list)

    def remove_all_by_keys(self, keys_list: Union[Iterable[dict], Iterable[list]]):
        """
        Removes every entity(ies) that matches the provided keys

        Args:
            keys_list(Union[Iterable[dict], Iterable[list]]):
                a (pair of) key(s) that identify the entity(ies)

        Returns:
            True if there are no entities of the mapped class in the database anymore;
            False otherwise
        """
        self.get_table_if_none()
        try:
            with self.table.batch_writer() as batch:
                for keys in keys_list:
                    keys = self.key_list2key_map(keys)
                    batch.delete_item(Key=keys)
        except Exception as ex:
            logging.error(str(ex))
            logging.warning(
                "Not able to remove items with keys"
                + str(keys_list)
                + "from table"
                + str(self.table_name)
                + "\nDynamoError: "
                + str(ex)
            )
            return False
        return True

    @abc.abstractmethod
    def remove_all_by_id(self, unique_id_list: list):
        """
        Removes multiple entity objects from the database
        Args:
            unique_id_list(Iterable): the ids of the entities to be removed

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        pass

    def exists_by_keys(self, keys: Union[dict, list]):
        """
        Checks if an entity identified by the provided keys exist in the database

        Args:
            keys(Union[dict, list]):
                a (pair of) key(s) that identify the entity

        Returns:
            True if a matching entry exist in the database;
            False otherwise
        """
        if isinstance(keys, list):  # Produce dict from list
            keys = self.key_list2key_map(keys)
        try:
            response = self.table.get_item(Key=keys)
            if "Item" in response:
                return True
        except Exception as ex:  # Check if the keys do not compose a unique key
            logging.error(str(ex))
            key_cond_exp, exp_att_val = self.keys2KeyConditionExpression(keys)
            try:
                response = self.table.query(
                    KeyConditionExpression=key_cond_exp,
                    ExpressionAttributeValues=exp_att_val,
                )
            except Exception:
                logging.warning(
                    "Not able to query table"
                    + str(self.table_name)
                    + "\nDynamoError: "
                    + str(ex)
                )
                return False
            if "Items" in response and len(response["Items"]) > 0:
                return True
        return False

    def exists_by_id(self, unique_id):
        """
        Checks if an entity identified by the provided id exist in the database

        Args:
            unique_id: The id of the entity to be searched

        Returns:
            True if a matching entry exist in the database;
            False otherwise
        """
        return self.exists_by_keys(self._id2key_pair(unique_id))

    def save_all(self, entities: Iterable[T]):
        """
        Stores a collection of entities in the database

        Args:
            entities(Iterable): objects of the mapped class to save

        Returns:
            True if the objects were stored in the database;
            False otherwise
        """
        self.get_table_if_none()
        try:
            with self.table.batch_writer() as batch:
                for obj in entities:
                    item_params = self.instance2item_params(obj)
                    batch.put_item(Item=item_params)
        except Exception as ex:
            logging.error(str(ex))
            raise ResourceWarning(
                "Not able to save item list",
                entities,
                "into table",
                self.table_name + "\nDynamoError: " + str(ex),
            )

    # flake8: noqa: C901
    @classmethod  # flake8: noqa: C901
    def dynamo_type_from_type(
        cls, python_type: type, custom_conversions: list = None
    ):  # flake8: noqa: C901
        """
        Get the standard DynamoDB type for a given python type
        Args:
            python_type: The python type
            custom_conversions: custom functions to conver types

        Returns:
            A string with the DynamoDB type

        """
        if not isclass(python_type):  # Try to get the class type
            if hasattr(
                python_type, "__supertype__"
            ):  # Try to get the class type from typings.NewType
                python_type = python_type.__supertype__
            elif hasattr(
                python_type, "__origin__"
            ):  # Try to get the class type from typings.Generic
                # This will convert compatible python sets to DynamoDB sets
                if (
                    hasattr(python_type, "__args__")
                    and issubclass(python_type.__origin__, (set, frozenset))
                    and issubclass(
                        python_type.__args__[0],
                        (bytes, bytearray, str, int, float, Decimal),
                    )
                ):
                    # python_type.__args__ is a tuple that holds the typehints
                    if issubclass(python_type.__args__[0], bytes):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.bytes_set_to_dynamo
                            )
                            custom_conversions.insert(
                                1, DynamoConversions.bytes_set_from_dynamo
                            )
                        return "BS"
                    elif issubclass(python_type.__args__[0], bytearray):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.bytes_set_to_dynamo
                            )
                            custom_conversions.insert(
                                1, DynamoConversions.bytearray_set_from_dynamo
                            )
                        return "BS"
                    elif issubclass(python_type.__args__[0], str):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.string_set_to_dynamo
                            )
                            custom_conversions.insert(1, DynamoConversions.identity)
                        return "SS"
                    elif issubclass(python_type.__args__[0], int):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.number_set_to_dynamo
                            )
                            custom_conversions.insert(
                                1, DynamoConversions.int_set_from_dynamo
                            )
                        return "NS"
                    elif issubclass(python_type.__args__[0], float):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.number_set_to_dynamo
                            )
                            custom_conversions.insert(
                                1, DynamoConversions.float_set_from_dynamo
                            )
                        return "NS"
                    elif issubclass(python_type.__args__[0], Decimal):
                        if custom_conversions is not None:
                            custom_conversions.insert(
                                0, DynamoConversions.number_set_to_dynamo
                            )
                            custom_conversions.insert(1, DynamoConversions.identity)
                        return "NS"
                else:
                    python_type = python_type.__origin__
        # Get the type of the enum values
        if issubclass(python_type, Enum):
            if custom_conversions is not None:
                custom_conversions.insert(0, DynamoConversions.enum_to_dynamo)
                custom_conversions.insert(
                    1, DynamoConversions.gen_enum_from_dynamo_for_enum_type(python_type)
                )
            python_type = type(list(python_type._value2member_map_.keys())[0])

        # if using a specific library like numpy or pandas, the user should specify the "N" type himself
        if issubclass(python_type, (int, float, Decimal)):
            return "N"
        elif issubclass(
            python_type,
            (
                str,
                dict,
                list,
                set,
                frozenset,
                tuple,
                datetime.date,
                datetime.time,
                datetime.datetime,
                UUID,
            ),
        ):
            return "S"
        elif issubclass(python_type, bool):
            return "BOOL"
        elif issubclass(
            python_type, (bytes, bytearray, object)
        ):  # general objects will be pickled
            return "B"
        else:  # this will probably never be reached since general objects are converted to bytes
            return "S"

    def _fill_map_dict(self, cls):
        """
        Fill the entity_type map
        Args:
            cls: the mapped class
        """
        if not self.map_filled:
            fls = fields(cls)
            for fl in fls:
                attrib_type = str
                if fl.name not in self.map_dict:
                    self.map_dict[fl.name] = {}
                if fl.name not in self.entity_type._dynamo_ignore():
                    if (
                        ConstantString.ITEM_ATTR_TYPE.value
                        not in self.map_dict[fl.name]
                    ):
                        # Try to infer the type from the class  attribute type
                        custom_conversions = []
                        attrib_type = self.dynamo_type_from_type(
                            fl.type, custom_conversions=custom_conversions
                        )
                        self.map_dict[fl.name][
                            ConstantString.ITEM_ATTR_TYPE.value
                        ] = attrib_type
                        if len(custom_conversions) >= 2:
                            self.map_dict[fl.name][
                                ConstantString.OBJ2ITEM_CONV.value
                            ] = custom_conversions[0]
                            self.map_dict[fl.name][
                                ConstantString.ITEM2OBJ_CONV.value
                            ] = custom_conversions[1]
                    if (
                        ConstantString.ITEM_ATTR_NAME.value
                        not in self.map_dict[fl.name]
                    ):
                        self.map_dict[fl.name][
                            ConstantString.ITEM_ATTR_NAME.value
                        ] = fl.name
            self.map_filled = True

    ###### ---------- Repository Interfaces and Implementation ---------- ######


class SingleTableDynamoCrudRepository(DynamoCrudRepository):
    _logical_table_name: str = None

    def __init__(self, entity_type: T, dynamo_table_name: str = None):
        """
        Creates a new SingleTableDynamoCrudRepository for a specific dynamo_entity class

        Args:
            entity_type(class):
                The class decorated with dynamo_entity that should be mapped to DynamoDB items.
            dynamo_table_name(str, optional):
                The name of the real table on DynamoDB
        """
        if dynamo_table_name is None:
            import os

            global_values = DynamoDBGlobalConfiguration.get_instance()
            if global_values.single_table_name_env_var in os.environ:
                dynamo_table_name = os.environ[global_values.single_table_name_env_var]
            else:
                raise ValueError("You need to provide the dynamo table name")
        self._logical_table_name = entity_type._dynamo_table_name()
        super().__init__(entity_type, dynamo_table_name)

    def instance2item_params_inject_keys(self, obj: T, item_params: dict = None):
        """
        Part of the process of converting an entity object to a DynamoDB item. Inject the keys to the item_params.
        Args:
            obj: the entity object that will be converted to a DynamoDB item
            item_params (dict, optional): the dictionary with the DynamoDB item attributes

        Returns:
            the item_params dict with the keys injected
        """
        item_params = item_params if item_params is not None else {}
        sk = obj._dynamo_table_name()
        pk = obj._dynamo_table_name() + "#" + str(getattr(obj, obj._dynamo_id()))
        global_values = DynamoDBGlobalConfiguration.get_instance()
        item_params[
            DynamoDBGlobalConfiguration.get_instance().single_table_pk_attr_name
        ] = pk
        item_params[
            DynamoDBGlobalConfiguration.get_instance().single_table_sk_attr_name
        ] = sk
        item_params[
            global_values.single_table_inverse_index_properties[
                ConstantString.INVERSE_INDEX_PK.value
            ]
        ] = sk
        item_params[
            global_values.single_table_inverse_index_properties[
                ConstantString.INVERSE_INDEX_SK.value
            ]
        ] = pk
        return item_params

    def key_list2key_map(self, keys: Union[dict, list]):
        """
        If the keys are a list, convert it to a dict with the keys. Using the pk and sk name from
        DynamoDBGlobalConfiguration

        Returns:
            a dict with the keys
        """
        if isinstance(keys, list):  # Produce dict from list
            key_list = keys
            keys = {
                DynamoDBGlobalConfiguration.get_instance().single_table_pk_attr_name: key_list[
                    0
                ]
            }
            if len(keys) > 1:
                keys[
                    DynamoDBGlobalConfiguration.get_instance().single_table_sk_attr_name
                ] = key_list[1]
        return keys

    def count(
        self,
        limit: int = -1,
        exclusive_start_key=None,
        page: int = None,
        exceed_dynamo_query_limit: bool = False,
    ):
        """
        Counts the number of items in the table or in a table page

        Args:
            limit(int, optional):
                the maximum items that should be returned.
                the page size for paginated queries.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page
            page(int, optional):
                for paginated queries, the requested page. Each page will have <limit> items.
                Note: Page numbers start at 0.
                This parameter will be ignored if a exclusive_start_key is provided
            exceed_dynamo_query_limit(bool, optional):
                will exceed the limit that DynamoDB will return in a single table.query request if there are more items.
                This parameter will be ignored if an exclusive_start_key or a page is provided
                Defaults to False

        Returns:
            An int with the number of items in the table.
        """
        inverse_index = (
            DynamoDBGlobalConfiguration.get_instance().single_table_inverse_index_properties
        )
        index_name = inverse_index[ConstantString.INVERSE_INDEX_NAME.value]
        key_condition_expression = Key(
            inverse_index[ConstantString.INVERSE_INDEX_PK.value]
        ).eq(self.entity_type._dynamo_table_name())
        try:
            count = len(
                self.find_collection(
                    key_condition_expression,
                    index_name,
                    limit=limit,
                    exclusive_start_key=exclusive_start_key,
                    page=page,
                    exceed_dynamo_query_limit=exceed_dynamo_query_limit,
                )
            )
            return count if count is not None else 0
        except Exception:
            return 0

    def remove_by_id(self, unique_id):
        """
        Remove an object of the mapped class from the database using a unique id

        Args:
            unique_id: a unique id that identify the object

        Returns:
            True if the object was removed or was not there already;
            False otherwise
        """
        return self.remove_by_keys(self._id2key_pair(unique_id))

    def remove(self, to_delete: T):
        """
        Removes an entity object from the database

        Args:
            to_delete: An object of the mapped entity class to be removed

        Returns:
            True if the object was removed or was not stored in the database
            False otherwise
        """
        return self.remove_by_id(getattr(to_delete, to_delete._dynamo_id()))

    def find_by_id(self, unique_id):
        """
        Finds an entity object by the unique id
        Args:
            unique_id: the object id

        Returns:
            an object of the mapped class
        """
        log_dict = {
            "Level": "[FINE]",
            "method": "SingleTableDynamoCrudRepository.find_by_id",
            "Error": "No error, the method was just called",
            "Provided_Args": {
                "unique_id": str(unique_id),
            },
        }
        logging.info(str(log_dict))
        instance_obj = self.find_by_keys(self._id2key_pair(unique_id))
        if (
            instance_obj is None
            and DynamoDBGlobalConfiguration.get_instance().log_debug_messages
        ):
            log_dict = {
                "Level": "[FINE]",
                "method": "SingleTableDynamoCrudRepository.find_by_id",
                "Error": "Item not found",
                "Provided_Args": {
                    "unique_id": str(unique_id),
                },
            }
            logging.info(str(log_dict))
        return instance_obj

    def find_all(
        self,
        limit: int = -1,
        exclusive_start_key=None,
        page: int = None,
        exceed_dynamo_query_limit: bool = False,
    ):
        """
        Gets all entities of the mapped class from the database

        Args:
            limit(int, optional):
                the maximum items that should be returned.
                the page size for paginated queries.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page
            page(int, optional):
                for paginated queries, the requested page. Each page will have <limit> items.
                Note: Page numbers start at 0.
                This parameter will be ignored if a exclusive_start_key is provided
            exceed_dynamo_query_limit(bool, optional):
                will exceed the limit that DynamoDB will return in a single table.query request if there are more items.
                This parameter will be ignored if an exclusive_start_key or a page is provided
                Defaults to False

        Returns:
            A list with all the entities of the mapped class
        """
        inverse_index = (
            DynamoDBGlobalConfiguration.get_instance().single_table_inverse_index_properties
        )
        index_name = inverse_index[ConstantString.INVERSE_INDEX_NAME.value]
        key_condition_expression = Key(
            inverse_index[ConstantString.INVERSE_INDEX_PK.value]
        ).eq(self.entity_type._dynamo_table_name())
        entity_list = self.find_collection(
            key_condition_expression,
            index_name,
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            page=page,
            exceed_dynamo_query_limit=exceed_dynamo_query_limit,
        )
        return entity_list

    def remove_entity_list(self, entity_list: Iterable):
        """
        Removes multiple entity objects from the database
        Args:
            entity_list(Iterable): the entities to be removed

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        self.get_table_if_none()
        try:
            with self.table.batch_writer() as batch:
                for entity in entity_list:
                    batch.delete_item(
                        Key=self._id2key_pair(str(getattr(entity, entity._dynamo_id())))
                    )
        except Exception as ex:
            logging.error(str(ex))
            logging.warning(
                "Not able to remove items from table "
                + str(self.table_name)
                + "\nDynamoError: "
                + str(ex)
            )
            return False
        return True

    def remove_all_by_id(self, unique_id_list: Iterable):
        """
        Removes multiple entity objects from the database
        Args:
            unique_id_list(Iterable): the ids of the entities to be removed

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        keys_list = []
        for unique_id in unique_id_list:
            keys_list.append(self._id2key_pair(unique_id))
        return self.remove_all_by_keys(keys_list)

    def exists_by_id(self, unique_id):
        """
        Checks if an entity identified by the provided id exist in the database

        Args:
            unique_id: The id of the entity to be searched

        Returns:
            True if a matching entry exist in the database;
            False otherwise
        """
        return self.exists_by_keys(self._id2key_pair(unique_id))


class MultiTableDynamoCrudRepository(DynamoCrudRepository):
    def __init__(self, entity_type: T):
        """
        Creates a new MultiTableDynamoCrudRepository for a specific dynamo_entity class

        Args:
            entity_type(class):
                The class decorated with dynamo_entity that should be mapped to DynamoDB items.
        """
        dynamo_table_name = entity_type._dynamo_table_name()
        cls_map = entity_type._dynamo_map()
        if (
            entity_type._dynamo_id() in cls_map
            and ConstantString.ITEM_ATTR_NAME.value in cls_map[entity_type._dynamo_id()]
        ):
            self.pk_name = cls_map[entity_type._dynamo_id()][
                ConstantString.ITEM_ATTR_NAME.value
            ]
        else:
            self.pk_name = entity_type._dynamo_id()

        super().__init__(entity_type, dynamo_table_name)

    def instance2item_params_inject_keys(self, obj: T, item_params: dict = None):
        """
        Part of the process of converting an entity object to a DynamoDB item. Inject the keys to the item_params.
        Args:
            obj: the entity object that will be converted to a DynamoDB item
            item_params (dict, optional): the dictionary with the DynamoDB item attributes

        Returns:
            the item_params dict with the keys injected
        """
        item_params = item_params if item_params is not None else {}
        global_values = DynamoDBGlobalConfiguration.get_instance()
        gsi_pk = self.entity_type._dynamo_table_name()
        gsi_sk = (
            self.entity_type._dynamo_table_name()
            + "#"
            + str(getattr(obj, obj._dynamo_id(), ""))
        )
        item_params[
            global_values.single_table_inverse_index_properties[
                ConstantString.INVERSE_INDEX_PK.value
            ]
        ] = gsi_pk
        item_params[
            global_values.single_table_inverse_index_properties[
                ConstantString.INVERSE_INDEX_SK.value
            ]
        ] = gsi_sk

    def instance2item_params_inject_attributes(self, obj: T, item_params: dict = None):
        super().instance2item_params_inject_attributes(obj, item_params)
        if self.pk_name not in item_params:
            item_params[self.pk_name] = str(getattr(obj, obj._dynamo_id(), ""))

    def count(
        self,
        limit: int = -1,
        exclusive_start_key=None,
        page: int = None,
        exceed_dynamo_query_limit: bool = False,
    ):
        """
        Counts the number of items in the table or in a table page

        Args:
            limit(int, optional):
                the maximum items that should be returned.
                the page size for paginated queries.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page
            page(int, optional):
                for paginated queries, the requested page. Each page will have <limit> items.
                Note: Page numbers start at 0.
                This parameter will be ignored if a exclusive_start_key is provided
            exceed_dynamo_query_limit(bool, optional):
                will exceed the limit that DynamoDB will return in a single table.query request if there are more items.
                This parameter will be ignored if an exclusive_start_key or a page is provided
                Defaults to False

        Returns:
            An int with the number of items in the table.
        """
        inverse_index = (
            DynamoDBGlobalConfiguration.get_instance().single_table_inverse_index_properties
        )
        index_name = inverse_index[ConstantString.INVERSE_INDEX_NAME.value]
        key_condition_expression = Key(
            inverse_index[ConstantString.INVERSE_INDEX_PK.value]
        ).eq(self.entity_type._dynamo_table_name())
        try:
            count = len(
                self.find_collection(
                    key_condition_expression,
                    index_name,
                    limit=limit,
                    exclusive_start_key=exclusive_start_key,
                    page=page,
                    exceed_dynamo_query_limit=exceed_dynamo_query_limit,
                )
            )
            return count if count is not None else 0
        except Exception:
            return 0

    def _id2key_pair(self, unique_id):
        if unique_id is None:
            raise ValueError("unique_id can not be None")
        unique_id_attr_name = self.entity_type._dynamo_id()
        pk_val, pk_name = self.instance_attr2_item_attr(unique_id, unique_id_attr_name)
        return {pk_name: pk_val}

    def key_list2key_map(self, keys: Union[dict, list]):
        """
        If the keys are a list, convert it to a dict with the keys.

        Returns:
            a dict with the keys
        """
        if isinstance(keys, list):  # Produce dict from list
            keys = self._id2key_pair(keys[0])
        return keys

    def remove_by_id(self, unique_id):
        """
        Remove an object of the mapped class from the database using a unique id

        Args:
            unique_id: a unique id that identify the object

        Returns:
            True if the object was removed or was not there already;
            False otherwise
        """
        return self.remove_by_keys(self._id2key_pair(unique_id))

    def remove(self, to_delete: T):
        """
        Removes an entity object from the database

        Args:
            entity: An object of the mapped entity class to be removed

        Returns:
            True if the object was removed or was not stored in the database
            False otherwise
        """
        return self.remove_by_id(getattr(to_delete, to_delete._dynamo_id()))

    def find_by_id(self, unique_id):
        """
        Finds an entity object by the unique id
        Args:
            unique_id: the object id

        Returns:
            an object of the mapped class
        """
        instance_obj = self.find_by_keys(self._id2key_pair(unique_id))
        if (
            instance_obj is None
            and DynamoDBGlobalConfiguration.get_instance().log_debug_messages
        ):
            log_dict = {
                "Level": "[FINE]",
                "method": "MultiTableDynamoCrudRepository.find_by_id",
                "Error": "Item not found",
                "Provided_Args": {
                    "unique_id": str(unique_id),
                },
            }
            logging.info(str(log_dict))
        return instance_obj

    def find_all(
        self,
        limit: int = -1,
        exclusive_start_key=None,
        page: int = None,
        exceed_dynamo_query_limit: bool = False,
    ):
        """
        Gets all entities of the mapped class from the database

        Args:
            limit(int, optional):
                the maximum items that should be returned.
                the page size for paginated queries.
                Defaults to -1 which will return the maximum items per DynamoDB query
            exclusive_start_key(optional):
                for paginated queries, the first key of the requested page
            page(int, optional):
                for paginated queries, the requested page. Each page will have <limit> items.
                Note: Page numbers start at 0.
                This parameter will be ignored if a exclusive_start_key is provided
            exceed_dynamo_query_limit(bool, optional):
                will exceed the limit that DynamoDB will return in a single table.query request if there are more items.
                This parameter will be ignored if an exclusive_start_key or a page is provided
                Defaults to False

        Returns:
            A list with all the entities of the mapped class
        """
        inverse_index = (
            DynamoDBGlobalConfiguration.get_instance().single_table_inverse_index_properties
        )
        index_name = inverse_index[ConstantString.INVERSE_INDEX_NAME.value]
        key_condition_expression = Key(
            inverse_index[ConstantString.INVERSE_INDEX_PK.value]
        ).eq(self.entity_type._dynamo_table_name())
        entity_list = self.find_collection(
            key_condition_expression,
            index_name,
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            page=page,
            exceed_dynamo_query_limit=exceed_dynamo_query_limit,
        )
        return entity_list

    def remove_entity_list(self, entity_list: Iterable):
        """
        Removes multiple entity objects from the database
        Args:
            entity_list(Iterable): the entities to be removed

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        self.get_table_if_none()
        try:
            with self.table.batch_writer() as batch:
                for entity in entity_list:
                    keys = self._id2key_pair(getattr(entity, entity._dynamo_id()))
                    batch.delete_item(Key=keys)
        except Exception as ex:
            logging.error(str(ex))
            logging.warning(
                "Not able to remove items from table "
                + str(self.table_name)
                + "\nDynamoError: "
                + str(ex)
            )
            return False
        return True

    def remove_all_by_id(self, unique_id_list: list):
        """
        Removes multiple entity objects from the database
        Args:
            unique_id_list(Iterable): the ids of the entities to be removed from the database

        Returns:
            True if the objects were removed or were not there already;
            False otherwise
        """
        keys_list = []
        for unique_id in unique_id_list:
            keys_list.append(self._id2key_pair(unique_id))
        return self.remove_all_by_keys(keys_list)

    def exists_by_id(self, unique_id):
        """
        Checks if an entity identified by the provided id exist in the database

        Args:
            unique_id: The id of the entity to be searched

        Returns:
            True if a matching entry exist in the database;
            False otherwise
        """
        return self.exists_by_keys(self._id2key_pair(unique_id))
