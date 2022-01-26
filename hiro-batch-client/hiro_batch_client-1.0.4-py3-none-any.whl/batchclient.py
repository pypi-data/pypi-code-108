import concurrent.futures
import logging
import queue
from abc import abstractmethod
from enum import Enum
from typing import Optional, Tuple, Any, Iterator, IO

from hiro_graph_client.client import HiroGraph
from hiro_graph_client.clientlib import AbstractTokenApiHandler
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)
""" The logger for this module """


class Result(Enum):
    SUCCESS = "success"
    FAILURE = "fail"


class Action(Enum):
    UNDEFINED = "undefined"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Entity(Enum):
    UNDEFINED = "undefined"
    VERTEX = "vertex"
    EDGE = "edge"
    TIMESERIES = "timeseries"
    ATTACHMENT = "attachment"


class HiroResultCallback:
    """
    Abstract class for objects that receive each result of a command in its method *result(...)*.
    Objects of this type are given to the *HiroGraphBatch* as parameter *callback=*.
    """

    @abstractmethod
    def result(self, data: Any, code: int) -> None:
        pass


class AbstractIOCarrier:
    """
    Abstract class that handles IO. When a child of this class is encountered, its IO is opened and read,
    then closed.
    """
    __io_base: IO = None
    """ Private reference to the IO object. Starts with value None and needs to be set via property *io_base()*. """

    def __enter__(self) -> IO:
        """ To be able to use *with <child of AbstractIOCarrier> as io_item:* """
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ To be able to use *with <child of AbstractIOCarrier> as io_item:* """
        self.close()

    @property
    def io_base(self) -> IO:
        """
        Property reader io_base
        :return: Value of *self.__io_base*.
        """
        return self.__io_base

    @io_base.setter
    def io_base(self, io_base: IO) -> None:
        """
        Property setter io_base.
        """
        self.__io_base = io_base

    @abstractmethod
    def open(self) -> IO:
        """
        Abstract base class for opening IO. Needs to set *self.io_base* to the opened IO object.

        :return: The IO opened
        :raises IOError: Any IO Error
        :raises RuntimeError: When this method is not overwritten by a child class and got called directly.
        """
        raise RuntimeError("Cannot execute method of abstract class.")

    def close(self) -> None:
        """
        Close the IO
        """
        if self.__io_base:
            self.__io_base.close()


class BasicFileIOCarrier(AbstractIOCarrier):
    """
    An IO Carrier for file operations.
    """

    filename: str
    mode: str

    def __init__(self, filename: str, mode: str = 'rb'):
        """
        Constructor

        :param filename: Local filename to start
        :param mode: Open mode. Default is 'rb'.
        """
        self.filename = filename
        self.mode = mode

    def open(self) -> IO:
        """
        Just start the included *self.filename* with *self.mode*.

        :return: The IO handle after start.
        :raises IOError: Any IO error start might raise.
        """
        self.io_base = open(self.filename, self.mode)
        return self.io_base


class SessionData:
    """
    Contains caches and session parameters.
    At the moment it carries *xid_cache*, an *edge_store*, a *content_store* and an *issue_store*.
    The latter are for the command 'handle_vertices_combined'.
    """
    xid_cache: dict
    """Cache for xid:id"""

    edge_store: dict
    """Stores a copy of '_edge_data' under the value of 'ogit/_id' as key."""

    timeseries_store: dict
    """Stores a copy of '_timeseries_data' under the value of 'ogit/_id' as key."""

    content_store: dict
    """Stores a copy of '_content_data' under the value of 'ogit/_id' as key."""

    issue_store: dict
    """Stores a copy of '_issue_data' under the value of 'ogit/_id' as key."""

    def __init__(self, enable_cache: bool = True):
        """
        Constructor

        :param enable_cache: Enable or disable the xid_cache. Default is True.
        """
        self.xid_cache = {} if enable_cache else None
        self.edge_store = {}
        self.content_store = {}
        self.timeseries_store = {}
        self.issue_store = {}

    def get_id(self, ogit_xid: str) -> Optional[str]:
        """
        Get an ogit/_id from an ogit/_xid.

        :param ogit_xid: The ogit/_xid to use.
        :return: The ogit/_id from the cache or None if it is not in the cache.
        """
        return None if self.xid_cache is None else self.xid_cache.get(ogit_xid)

    def has_id(self, ogit_id: str) -> bool:
        """
        Check for existence of ogit_id in the cache.

        :param ogit_id: ogit/_id to look for.
        :return: True if ogit_id exists in the cache, False otherwise.
        """
        return False if self.xid_cache is None else bool(list(self.xid_cache.values()).count(ogit_id))

    def register_xid(self, ogit_xid: str, ogit_id: str) -> None:
        """
        Registers a new xid - id mapping in the *xid_cache* unless it or any params are None.

        :param ogit_xid: The xid (key) of the *xid_cache*.
        :param ogit_id: The id (value) of the *xid_cache*.
        """
        if None not in [self.xid_cache, ogit_xid, ogit_id]:
            self.xid_cache[ogit_xid] = ogit_id

    def register_response(self, attributes: dict, response: dict) -> None:
        """
        Collect all data that shall be saved in the session from the attributes and HIRO response.

        Registers a new xid:id mapping in the *xid_cache* unless it or any params are None.

        Saves any edge data, content data, timeseries and issue data from the attributes under the ogit/_id given by the
        response.

        :param attributes: Original attributes from the Runner command
        :param response: Response from the backend after the Runner command ran.
        """
        ogit_id = response.get("ogit/_id")
        ogit_xid = response.get("ogit/_xid")
        edge_data = attributes.get("_edge_data")
        timeseries_data = attributes.get("_timeseries_data")
        content_data = attributes.get("_content_data")
        issue_data = attributes.get("_issue_data")

        self.register_xid(ogit_id, ogit_xid)

        if None not in [self.edge_store, ogit_id, edge_data]:
            self.edge_store[ogit_id] = edge_data.copy()

        if None not in [self.timeseries_store, ogit_id, timeseries_data]:
            self.timeseries_store[ogit_id] = timeseries_data.copy()

        if None not in [self.content_store, ogit_id, content_data]:
            self.content_store[ogit_id] = content_data.copy()

        if None not in [self.issue_store, ogit_id, issue_data]:
            self.issue_store[ogit_id] = issue_data.copy()

    def unregister_by_response(self, response: dict) -> None:
        """
        Remove all cached values using HIRO response data.

        :param response: Response data from a removed vertex.
        """
        ogit_id = response.get("ogit/_id")
        if not ogit_id:
            return

        if self.edge_store:
            self.edge_store.pop(ogit_id, None)

        if self.timeseries_store:
            self.timeseries_store.pop(ogit_id, None)

        if self.content_store:
            self.content_store.pop(ogit_id, None)

        if self.issue_store:
            self.issue_store.pop(ogit_id, None)

        if self.xid_cache:
            for k, v in self.xid_cache.items():
                if v == ogit_id:
                    del self.xid_cache[k]
                    break


class HiroBatchRunner:
    """
    Handles a batch of data intended for the same command.

    This is an abstract class. The real commands need to derive from this.
    """

    entity: Entity
    action: Action

    connection: HiroGraph

    session_data: SessionData

    def __init__(self,
                 entity: Entity,
                 action: Action,
                 session_data: SessionData,
                 connection: HiroGraph):
        """
        Constructor

        :param entity: Entity that gets handled (vertex, edge, timeseries etc.)
        :param action: Action to execute on these entities (create, update, delete)
        :param session_data: Carries session data and caches.
        :param connection: The hiro client to use.
        """
        self.connection = connection
        self.entity = entity
        self.action = action

        self.session_data = session_data

    def get_id_by_xid(self, ogit_xid: str) -> Optional[str]:
        """
        Get an ogit/_id from the *xid_cache* or get it from HiroGraph when it is not in the cache is or it is
        disabled.

        :param ogit_xid: The xid to use to look for an ogit/_id.
        :return: The ogit/_id found or None
        """
        ogit_id = self.session_data.get_id(ogit_xid)

        if ogit_id is None:
            id_result = self.connection.get_node_by_xid(ogit_xid, 'ogit/_id')
            items: list = id_result.get('items')
            if items is None:
                raise KeyError("Response contains no key 'items': \"{}\"".format(id_result))

            if items:
                ogit_id = items[0].get('ogit/_id')

            self.session_data.register_xid(ogit_xid, ogit_id)

        return ogit_id

    def check_id(self, ogit_id: str) -> Optional[str]:
        """
        Check for existence of an id in *xid_cache* or, if not found there or cache is disabled, in HiroGraph.

        :param ogit_id: The ogit/_id to check.
        :return: The ogit/_id of the result or None
        """
        if self.session_data.has_id(ogit_id):
            return ogit_id

        id_result = self.connection.get_node(ogit_id, 'ogit/_id')
        return id_result.get('ogit/_id')

    def get_vertex_id(self,
                      attributes: dict,
                      id_key: str = "ogit/_id",
                      xid_key: str = "ogit/_xid") -> Optional[str]:
        """
        Get the ogit/_id from the source data given in *attributes*.

        * If the ogit/_id is present in *attributes*, return it.
        * If ogit/_id is missing but ogit/_xid is present, use the ogit/_xid to get the ogit/_id from HiroGraph and
          return it.

        :param attributes: Dict of attributes.
        :param id_key: The key for the ogit/_id in *attributes*. Defaults to "ogit/_id".
        :param xid_key: The key for the ogit/_id in *attributes*. Defaults to "ogit/_xid".

        :return: The ogit/_id found or None otherwise.
        """

        ogit_id = attributes.get(id_key)

        if ogit_id is None:
            ogit_xid = attributes.get(xid_key)
            if ogit_xid:
                ogit_id = self.get_id_by_xid(ogit_xid)

        return ogit_id

    def get_and_check_vertex_id(self,
                                attributes: dict,
                                id_key: str = "ogit/_id",
                                xid_key: str = "ogit/_xid") -> str:
        """
        Get the ogit/_id from the source data given in *attributes*.

        * If the ogit/_id is present in *attributes*, return it.
        * If ogit/_id is missing but ogit/_xid is present, use the ogit/_xid to get the ogit/_id from HiroGraph and
          return it.

        :param attributes: Dict of attributes.
        :param id_key: The key for the ogit/_id in *attributes*. Defaults to "ogit/_id".
        :param xid_key: The key for the ogit/_id in *attributes*. Defaults to "ogit/_xid".

        :return: The ogit/_id found.

        :raises ValueError: When no ogit/_id can be found.
        """

        ogit_id = self.get_vertex_id(attributes, id_key, xid_key)

        if not ogit_id:
            raise SourceValueError(
                "\"{}\" not found or empty in attributes and cannot be determined by any \"{}\"".format(id_key,
                                                                                                        xid_key))

        return ogit_id

    @staticmethod
    def get_and_check(attributes: dict, key: str, name: str = 'attributes') -> Any:
        """
        Raise ValueError when key is not in attributes or the value behind the key is empty.

        :param attributes: Dict of attributes.
        :param key: The key to look for in *attributes*.
        :param name: Name of the attributes dict. Default is 'attributes'.
        :return: the value in *attributes* of the key.
        :raises ValueError: When 'key' does not exist in *attributes*.
        """
        attribute = attributes.get(key)
        if not attribute:
            raise SourceValueError("\"{}\" not found or empty in \"{}\".".format(key, name))

        return attribute

    @staticmethod
    def for_each_attribute(attributes: dict, *funcs) -> dict:
        """
        Iterate over *attributes* and apply a list of functions to each item. Skips any attribute whose key is
        empty or starts with '_'. Returns a dict with the results after the *funcs* have been applied, leaving the
        original *attributes* unchanged.

        :param attributes: Dict of attributes.
        :param funcs: Set of functions to apply to each element of *attributes*.
        :return: The resulting copy of *attributes*
        """
        result = {}
        for key, value in attributes.items():
            if not key or key[0] == '_':
                continue

            for func in funcs:
                key, value = func(key, value)
                if key is None:
                    break

            if key is not None:
                result[key] = value

        return result

    def resolve_ids(self, key: str, value: str) -> Tuple[str, str]:
        """
        To be used with self.for_each_attribute()

        Try to resolve_ids keys that start with "id:" or "xid:". Try to find the
        ogit/_id of a vertex by using the value for such a key in the graph. Return a tuple of (key, value) with the key
        without its prefix "id:" or "xid:" and the value resolved to a real "ogit/_id".

        :param key: Attribute key
        :param value: Attribute value
        :return: The changed tuple (key, value).
        """
        if key.startswith("xid:"):
            ogit_id = self.get_id_by_xid(value)

            if ogit_id is None or not ogit_id:
                raise ValueError(
                    "Cannot resolve xid \"{}\" of \"{}\".".format(value, key))

            return key[4:], ogit_id

        elif key.startswith("id:"):
            ogit_id = self.check_id(value)

            if ogit_id is None or not ogit_id:
                raise ValueError(
                    "Cannot find id \"{}\" of \"{}\".".format(value, key))

            return key[3:], ogit_id

        else:
            return key, value

    @staticmethod
    def sanitize_for_update(key: str, value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        To be used with self.for_each_attribute()

        Return (None, None) when key starts with "ogit/_" unless "ogit/_owner", "ogit/_content" or "ogit/_tags".

        :param key: Attribute key
        :param value: Attribute value
        :return: The changed tuple (key, value) or (None, None) when this item should be skipped.
        """
        if key.startswith("ogit/_") and key not in ["ogit/_owner", "ogit/_content", "ogit/_tags"]:
            return None, None

        return key, value

    @staticmethod
    def success_message(entity: Entity, action: Action, order: int, data: dict) -> dict:
        """
        Success message format

        ::

            {
                "status": "success",
                "entity": entity.value,
                "action": action.value,
                "order": order,
                "data": data
            }

        :param entity: Entity handled
        :param action: Action done
        :param data: JSON to return
        :param order: Running number of commands.
        :return: The message
        """
        return {
            "status": Result.SUCCESS.value,
            "entity": entity.value,
            "action": action.value,
            "order": order,
            "data": data
        }

    @staticmethod
    def error_message(entity: Entity,
                      action: Action,
                      order: int,
                      error: Exception,
                      original: Optional[dict],
                      status_code: int = None,
                      interrupted: bool = None) -> dict:
        """
        Failure message format

        ::

            {
                "status": "fail",
                "entity": entity.value,
                "action": action.value,
                "order": order,
                "data": {
                    "error": error.__class__.__name__,
                    "message": str(error),
                    "original_data": original
                }
            }

        :param entity: Entity handled
        :param action: Action done
        :param order: Running number of commands.
        :param error: The exception raised
        :param original: The data that lead to the exception
        :param status_code: HTTP status code if available
        :param interrupted: Indicates, that the current batch processing has been interrupted.
        :return: The message
        """

        message = str(error)
        if interrupted:
            message = "BATCH PROCESSING ABORTED! " + message + \
                      " All further data has been ignored after this error occurred."

        return {
            "status": Result.FAILURE.value,
            "entity": entity.value,
            "action": action.value,
            "order": order,
            "data": {
                "error": error.__class__.__name__,
                "code": status_code,
                "message": message,
                "original_data": original
            }
        }

    def run(self, attributes: dict, order: int, result_queue: queue.Queue) -> None:
        """
        Run the Command with all data given by *attributes*.

        This is the enclosing code for all batch runners. The implementation of a handling a single entry of
        the *attributes* is defined in derived ...Runner-classes.

        :param attributes: Dict with attributes to handle in HIRO.
        :param order: Number of the command read from the *self._request_queue*.
        :param result_queue: Queue receiving the results.
        """
        try:
            response: dict = self.run_item(attributes)

            response_code = 200
            message = self.success_message(self.entity, self.action, order, response)

        except RequestException as error:
            response_code = error.response.status_code if error.response is not None else 999
            message = self.error_message(self.entity,
                                         self.action,
                                         order,
                                         error,
                                         attributes,
                                         response_code)

        except SourceValueError as error:
            response_code = 400
            message = self.error_message(self.entity, self.action, order, error, attributes, 400)

        except Exception as error:
            response_code = 500
            message = self.error_message(self.entity, self.action, order, error, attributes, 500)

        result_queue.put((message, response_code, order))

    @abstractmethod
    def run_item(self, attributes: dict) -> dict:
        """
        Abstract method overwritten by derived runner classes.

        :param attributes: A dict of attributes to handle.
        :return: A response dict - usually directly the structure received from the backend.
        """
        raise RuntimeError("Cannot call abstract method 'run_item()' within HiroCommandBatch directly.")


class CreateVerticesRunner(HiroBatchRunner):
    """
    Create vertices
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Create vertices

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.VERTEX, Action.CREATE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to create a vertex from.
        :return: A response dict - usually directly the structure received from the backend.
        """

        ogit_type = self.get_and_check(attributes, "ogit/_type")
        final_attributes = self.for_each_attribute(attributes, self.resolve_ids)

        response: dict = self.connection.create_node(final_attributes, ogit_type)

        self.session_data.register_response(attributes, response)

        return response


class UpdateVerticesRunner(HiroBatchRunner):
    """
    Update vertices
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Update vertices

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.VERTEX, Action.UPDATE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to update a vertex from.
        :return: A response dict - usually directly the structure received from the backend.
        """
        ogit_id = self.get_and_check_vertex_id(attributes)
        final_attributes = self.for_each_attribute(attributes, self.resolve_ids, self.sanitize_for_update)

        response: dict = self.connection.update_node(ogit_id, final_attributes)

        self.session_data.register_response(attributes, response)

        return response


class DeleteVerticesRunner(HiroBatchRunner):
    """
    Delete vertices
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Delete vertices

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.VERTEX, Action.DELETE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to delete a vertex from.
        :return: A response dict - usually directly the structure received from the backend.
        """
        ogit_id = self.get_and_check_vertex_id(attributes)

        response: dict = self.connection.delete_node(ogit_id)

        self.session_data.unregister_by_response(response)

        return response


class HandleVerticesRunner(HiroBatchRunner):
    """
    Handle vertices. Either update or create them based on incoming payload entries.
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Handle vertices. Either update or create them based on incoming payload entries.

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.VERTEX, Action.UNDEFINED, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to handle a vertex from. Updates the vertex when it can be found via
                           ogit/_id or ogit/_xid, creates the vertex otherwise when ogit/_type is present.
        :return: A response dict - usually directly the structure received from the backend.
        """
        self.action = Action.UNDEFINED

        ogit_id = self.get_vertex_id(attributes)

        self.action = Action.UPDATE if ogit_id else Action.CREATE

        if self.action == Action.CREATE:
            ogit_type = self.get_and_check(attributes, "ogit/_type")
            final_attributes = self.for_each_attribute(attributes, self.resolve_ids)

            response: dict = self.connection.create_node(final_attributes, ogit_type)
        else:
            final_attributes = self.for_each_attribute(attributes, self.resolve_ids, self.sanitize_for_update)

            response: dict = self.connection.update_node(ogit_id, final_attributes)

        self.session_data.register_response(attributes, response)

        return response


class CreateEdgesRunner(HiroBatchRunner):
    """
    Create edges between vertices
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Create edges between vertices

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.EDGE, Action.CREATE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to create edges from.
        :return: A response dict - usually directly the structure received from the backend.
        """
        from_node_id = self.get_and_check_vertex_id(attributes, "from:ogit/_id", "from:ogit/_xid")
        to_node_id = self.get_and_check_vertex_id(attributes, "to:ogit/_id", "to:ogit/_xid")
        verb = self.get_and_check(attributes, "verb")

        return self.connection.connect_nodes(from_node_id, verb, to_node_id)


class DeleteEdgesRunner(HiroBatchRunner):
    """
    Delete edges between vertices
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Delete edges between vertices

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.EDGE, Action.DELETE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to delete edges from.
        :return: A response dict - usually directly the structure received from the backend.
        """
        from_node_id = self.get_and_check_vertex_id(attributes, "from:ogit/_id", "from:ogit/_xid")
        to_node_id = self.get_and_check_vertex_id(attributes, "to:ogit/_id", "to:ogit/_xid")
        verb = self.get_and_check(attributes, "verb")

        return self.connection.disconnect_nodes(from_node_id, verb, to_node_id)


class AddTimeseriesRunner(HiroBatchRunner):
    """
    Attach timeseries values to a vertex.
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Attach timeseries values to a vertex.

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.TIMESERIES, Action.CREATE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to attach timeseries to a vertex.
        :return: A response dict - usually directly the structure received from the backend.
        """
        node_id = self.get_and_check_vertex_id(attributes)
        items = self.get_and_check(attributes, "items")

        return self.connection.post_timeseries(node_id, items)


class AddAttachmentRunner(HiroBatchRunner):
    """
    Attach an attachment to a vertex.
    """

    def __init__(self, session_data: SessionData, connection: HiroGraph):
        """
        Attach an attachment to a vertex.

        :param session_data: Required: Session data / caches.
        :param connection: Required: The handler for the connection to HIRO HiroGraph.
        """
        super().__init__(Entity.ATTACHMENT, Action.CREATE, session_data, connection)

    def run_item(self, attributes: dict) -> dict:
        """
        :param attributes: A dict of attributes to attach attachments to a vertex.
        :return: A response dict - usually directly the structure received from the backend.
        """
        node_id = self.get_and_check_vertex_id(attributes)
        content_data = self.get_and_check(attributes, '_content_data')
        mimetype = content_data.get('mimetype')

        data = content_data.get('data')

        if isinstance(data, AbstractIOCarrier):
            with data as io_item:
                return self.connection.post_attachment(node_id=node_id,
                                                       data=io_item,
                                                       content_type=mimetype)
        elif data:
            return self.connection.post_attachment(node_id=node_id,
                                                   data=data,
                                                   content_type=mimetype)
        else:
            raise SourceValueError('"data" not found or empty in "attributes._content_data".')


class HiroGraphBatch:
    """
    This class handles lists of vertex-, edge- or timeseries-data via HiroGraph.
    """
    request_queue: queue.Queue
    result_queue: queue.Queue

    _parallel_workers: int
    """Counts the current amount of parallel workers."""
    _order: int
    """Counts the commands that have been put onto the request_queue and the errors that prevent that."""

    callback: HiroResultCallback

    _api_handler: AbstractTokenApiHandler

    use_xid_cache: bool
    """Use xid caching. Default is True when omitted or set to None."""

    command_map = {
        "create_vertices": CreateVerticesRunner,
        "update_vertices": UpdateVerticesRunner,
        "handle_vertices": HandleVerticesRunner,
        "delete_vertices": DeleteVerticesRunner,
        "create_edges": CreateEdgesRunner,
        "delete_edges": DeleteEdgesRunner,
        "add_timeseries": AddTimeseriesRunner,
        "add_attachments": AddAttachmentRunner
    }
    """This is the map of commands that HiroGraphBatch handles."""

    def __init__(self,
                 api_handler: AbstractTokenApiHandler,
                 callback: HiroResultCallback = None,
                 use_xid_cache: bool = True,
                 max_parallel_workers: int = 8,
                 queue_depth: int = None):
        """
        Constructor

        HiroGraphBatch is using API HiroGraph internally.

        :param api_handler: External API handler.
        :param callback: required when multi_command() is used, optional otherwise: Callback object for results.
        :param use_xid_cache: Use xid caching. Default is True when omitted or set to None.
        :param max_parallel_workers: Amount of maximum parallel workers for requests. Default is 8.
        :param queue_depth: Amount of entries the *self.request_queue* and *self.result_queue* can hold. Default is to
                            set it to the same value as *parallel_workers*.
        """
        if not api_handler:
            raise ValueError('Need attribute "api_handler" for HIRO Graph API.')

        self._api_handler = api_handler

        self.request_queue = queue.Queue(maxsize=queue_depth or max_parallel_workers)
        self.result_queue = queue.Queue(maxsize=queue_depth or max_parallel_workers)

        self.callback = callback

        self.max_parallel_workers = max_parallel_workers
        self._parallel_workers = 0
        self._order = 0

        self.use_xid_cache = False if use_xid_cache is False else True

    def _edges_from_session(self, executor: concurrent.futures.ThreadPoolExecutor, session: SessionData) -> None:
        """
        Recreate attributes to create edges saved in a session.

        :param executor: The thread executor to create additional threads if necessary.
        :param session: The session with the edge data.
        """
        for ogit_id, edge_data in session.edge_store.items():
            for edge in edge_data:
                other_ogit_id = edge.get("vertex_id")
                other_ogit_xid = edge.get("vertex_xid")
                verb = edge.get('verb')
                direction = edge.get("direction")

                attributes = {
                    "verb": verb
                }
                if direction == 'in':
                    attributes["to:ogit/_id"] = ogit_id
                    if other_ogit_id:
                        attributes["from:ogit/_id"] = other_ogit_id
                    else:
                        attributes["from:ogit/_xid"] = other_ogit_xid
                else:
                    attributes["from:ogit/_id"] = ogit_id
                    if other_ogit_id:
                        attributes["to:ogit/_id"] = other_ogit_id
                    else:
                        attributes["to:ogit/_xid"] = other_ogit_xid

                self._request_queue_put(executor, session, 'create_edges', attributes)

    def _timeseries_from_session(self, executor: concurrent.futures.ThreadPoolExecutor, session: SessionData) -> None:
        """
        Recreate attributes to create timeseries saved in a session.

        :param executor: The thread executor to create additional threads if necessary.
        :param session: The session with the timeseries data.
        """
        for ogit_id, timeseries_data in session.timeseries_store.items():
            attributes = {
                'ogit/_id': ogit_id,
                'items': timeseries_data
            }

            self._request_queue_put(executor, session, 'add_timeseries', attributes)

    def _attachments_from_session(self, executor: concurrent.futures.ThreadPoolExecutor, session: SessionData) -> None:
        """
        Recreate attributes to create attachments saved in a session.

        :param executor: The thread executor to create additional threads if necessary.
        :param session: The session with the attachment data.
        """
        for ogit_id, content_data in session.content_store.items():
            attributes = {
                'ogit/_id': ogit_id,
                '_content_data': content_data
            }

            self._request_queue_put(executor, session, 'add_attachments', attributes)

    def _issues_from_session(self, executor: concurrent.futures.ThreadPoolExecutor, session: SessionData) -> None:
        """
        Handle issue vertices from the data saved in a session.

        :param executor: The thread executor to create additional threads if necessary.
        :param session: The session with the issue data.
        """
        for ogit_id, issue_data in session.issue_store.items():

            if isinstance(issue_data, dict):
                issue_data = [issue_data]
            if isinstance(issue_data, list):
                counter = 0
                for issue in issue_data:
                    counter += 1

                    issue.update({
                        "ogit/_type": "ogit/Automation/AutomationIssue",
                        "ogit/Automation/originNode": ogit_id
                    })

                    self._request_queue_put(executor, session, 'create_vertices', issue)

    def _reader(self, collected_results: list) -> None:
        """
        Thread executor function. Read items from the *self.result_queue*. Since either *self.callback*
        or *collected_results* is set usually, the results either get passed through the callback function or get
        collected in *collected_results*.

        Thread exits when *self.result_queue.get()* reads None.
        """
        for result, code, order in iter(self.result_queue.get, None):
            try:
                if self.callback is not None:
                    self.callback.result(result, code)
                if collected_results is not None:
                    collected_results.append(result)
            except Exception as err:
                logger.error("Error handling result_queue.get", err)
            finally:
                self.result_queue.task_done()

    def _worker(self, session: SessionData) -> None:
        """
        Thread executor function. Create a connection, then read data from the *self.request_queue* and execute
        the command with the attributes from the queue and the session provided.

        Thread exits when *self.request_queue.get()* reads None.

        :param session: The session object to share between all connections.
        """

        connection = HiroGraph(self._api_handler)

        for command, attributes, order in iter(self.request_queue.get, None):
            try:
                runner_ref = self.command_map.get(command)
                if runner_ref is not None:
                    runner_ref(session, connection).run(attributes, order, self.result_queue)
            except Exception as err:
                logger.error("Error handling request_queue.get", err)
            finally:
                self.request_queue.task_done()

    def _request_queue_put(self,
                           executor: concurrent.futures.ThreadPoolExecutor,
                           session: SessionData,
                           command: str,
                           attributes: dict) -> None:
        """
        Put a command onto the queue. Create additional threads if necessary.
        Also handle *self._parallel_workers* and *self._order*.

        :param executor: The thread executor to create additional threads.
        :param session: Session data object.
        :param command: Command name to put on the queue.
        :param attributes: Command attributes to put on the queue.
        """

        if not isinstance(attributes, dict):
            raise SourceValueError("Found attributes that are not a dict.")

        if self._parallel_workers < self.max_parallel_workers:
            executor.submit(HiroGraphBatch._worker, self, session)
            self._parallel_workers += 1

        self.request_queue.put((command, attributes, self._order))
        self._order += 1

    def multi_command(self, command_iter: Iterator[dict]) -> Optional[list]:
        """
        Run a multi-command batch.

        The command_iter iterates over a list of dicts with pairs like

        ::

            {
                "[command]": { "[key]": "[value]", ... }
            },
            {
                "[command]": { "[key]": "[value]", ... }
            },
            ...

        or

        ::

            {
                "[command]": [
                    { "[key]": "[value]", ... },
                    { "[key]": "[value]", ... }
                ]
            },
            ...

        with payload being a list of dict containing the attributes to run with that command.

        If iterating over command_iter throws an exception, the loop is aborted and an according error message
        is given back.

        If you do not want to interrupt the loop on an error, you can return/yield an exception with the command
        "error" from the iterator. An error message will be put into the result list and operation will continue:

        ::

            {
                "error": (Exception object)
            },
            ...


        :param command_iter: An iterator for a dict of pairs "[command]:payload".
        :return a list with results when no callback is set, None otherwise.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:

            try:
                session = SessionData(self.use_xid_cache)

                collected_results = [] if self.callback is None else None

                executor.submit(HiroGraphBatch._reader, self, collected_results)

                handle_session_data = False
                attributes = None
                for command_entry in command_iter:
                    for command, attributes in command_entry.items():

                        if command == "handle_vertices_combined":
                            command = "handle_vertices"
                            handle_session_data = True

                        try:

                            if command == "error":
                                try:
                                    attributes = str(attributes) if attributes else None
                                except Exception as err:
                                    attributes = err.__class__.__name__

                                raise SourceValueError("Error while iterating over source.")

                            if command not in self.command_map:
                                raise SourceValueError(f"No such command \"{command}\".")

                            if not isinstance(attributes, list):
                                attributes = [attributes]

                            for attribute_entry in attributes:
                                self._request_queue_put(
                                    executor,
                                    session,
                                    command,
                                    attribute_entry)

                            # Empty old attributes, so they do not show up on exceptions
                            # that might be thrown before the new attributes have been
                            # read (i.e. read-in-exceptions while iterating over *command_iter*).
                            attributes = None

                        except SourceValueError as err:
                            sub_result, sub_code = HiroBatchRunner.error_message(
                                entity=Entity.UNDEFINED,
                                action=Action.UNDEFINED,
                                order=self._order,
                                error=err,
                                original=attributes,
                                status_code=400), 400

                            self.result_queue.put((sub_result, sub_code, self._order))
                            self._order += 1

                if handle_session_data:
                    self.request_queue.join()
                    self._edges_from_session(executor, session)
                    self._timeseries_from_session(executor, session)
                    self._attachments_from_session(executor, session)
                    # Ensure, that all data related to the original vertex has been sent
                    # before creating any issues.
                    self.request_queue.join()
                    self._issues_from_session(executor, session)

                return collected_results

            except Exception as err:
                sub_result, sub_code = HiroBatchRunner.error_message(
                    entity=Entity.UNDEFINED,
                    action=Action.UNDEFINED,
                    order=self._order,
                    error=err,
                    original=attributes,
                    status_code=400,
                    interrupted=True), 400

                self.result_queue.put((sub_result, sub_code, self._order))

            finally:
                self.request_queue.join()
                self.result_queue.join()

                for _ in range(self._parallel_workers):
                    self.request_queue.put(None)

                self._parallel_workers = 0
                self._order = 0

                self.result_queue.put(None)


class SourceValueError(ValueError):
    """
    An error occurred with missing or invalid source data.
    """
    pass
