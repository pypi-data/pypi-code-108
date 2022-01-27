import abc
import uuid
from dataclasses import dataclass, field


class TableInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    def scan(self):
        pass

    @abc.abstractmethod
    def delete_item(self, Key: dict):
        pass

    @abc.abstractmethod
    def get_item(self, Key: dict):
        pass

    @abc.abstractmethod
    def query(self, **kwargs):
        pass

    @abc.abstractmethod
    def put_item(self, Item: dict):
        pass


class BatchWriterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def delete_item(self, Key: dict):
        pass


@dataclass
class SimulatedTable(TableInterface):
    items: dict = field(default_factory=lambda: {})
    table_status: str = "ACTIVE"
    # for items with no specified sk
    std_sk: str = field(default_factory=lambda: str(uuid.uuid1()))
    pk_name: str = "pk"
    sk_name: str = "sk"
    writer: BatchWriterInterface = None

    @dataclass
    class SimulateBatchWriter(BatchWriterInterface):
        table: TableInterface

        def __init__(self, table: TableInterface = None):
            self.table = table

        def delete_item(self, Key: dict):
            self.table.delete_item(Key)

        def put_item(self, Item: dict):
            self.table.put_item(Item)

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

    def _inject_sk(self, Key: dict):
        if self.sk_name not in Key:
            Key[self.sk_name] = self.std_sk

    def _keys_from_item(self, item):
        Key = {}
        if self.pk_name not in item:
            raise KeyError(
                "The provide item must have a value for the partition key: ",
                self.pk_name,
            )
        Key[self.pk_name] = item[self.pk_name]
        if self.sk_name in item:
            Key[self.sk_name] = item[self.sk_name]
        else:
            self._inject_sk(Key)

        return Key

    def _expression_att_val2Key(self, ExpressionAttributeValues: dict):
        Key = {}
        for dirty_key in ExpressionAttributeValues:
            clean_key = dirty_key[1:-3]
            Key[clean_key] = ExpressionAttributeValues[dirty_key]
        return Key

    def batch_writer(self):
        if self.writer is None:
            self.writer = self.SimulateBatchWriter(table=self)
        return self.writer

    def delete(self):
        self.items = {}
        self.table_status = "DELETING"

    def _items_as_list(self):
        item_list = []
        for (
            _,
            partition,
        ) in self.items.items():  # The first ignored key is the partition key
            for _, item in partition.items():  # The second ignored key is the sort key
                item_list.append(item)
        return item_list

    def scan(self, **kwargs):
        scan_response = {
            "Count": len(self._items_as_list()),
            "Items": self._items_as_list(),
        }
        return scan_response

    def delete_item(self, Key: dict):
        aux = Key
        Key = aux.copy()
        self._inject_sk(Key)
        self.items[str(Key[self.pk_name])].pop(str(Key[self.sk_name]))

    def get_item(self, Key: dict):
        aux = Key
        Key = aux.copy()
        self._inject_sk(Key)
        try:
            return {"Item": self.items[str(Key[self.pk_name])][str(Key[self.sk_name])]}
        except Exception as ex:
            print(ex)
            return None

    def query(self, **kwargs):
        Key = self._expression_att_val2Key(kwargs["ExpressionAttributeValues"])
        response = {"Items": []}
        if self.sk_name in Key:  # One item
            item = self.get_item(Key)
            if item is not None:
                response["Items"].append(item)
        else:  # Multiple items
            for sk in self.items[str(Key[self.pk_name])]:
                response["Items"].append(self.items[str(Key[self.pk_name])][sk])
        return response

    def put_item(self, Item: dict):
        Key = self._keys_from_item(Item)
        if str(Key[self.pk_name]) not in self.items:
            self.items[str(Key[self.pk_name])] = {}
        self.items[str(Key[self.pk_name])][str(Key[self.sk_name])] = Item


class SimulatedDynamoDBResource:
    tables: dict = {}

    def create_table(self, **kwargs):
        table_name = kwargs["TableName"]
        key_schema = kwargs["KeySchema"]
        pk = None
        sk = None
        if table_name in self.tables:
            if self.tables[table_name].table_status != "DELETING":
                raise RuntimeError(
                    "A table with the name ", table_name, " already exists"
                )
            else:
                self.tables.pop(table_name)
        for key_schema_dict in key_schema:
            if key_schema_dict["KeyType"] == "HASH":
                pk = key_schema_dict["AttributeName"]

            elif key_schema_dict["KeyType"] == "RANGE":
                sk = key_schema_dict["AttributeName"]

        if pk is not None:
            if sk is not None:
                self.tables[table_name] = SimulatedTable(pk_name=pk, sk_name=sk)
            else:
                self.tables[table_name] = SimulatedTable(pk_name=pk)
            return self.tables[table_name]

        else:
            raise RuntimeError("Provided KeySchema missing the partition key")

    def Table(self, table_name: str):
        if (table_name is None) or (table_name not in self.tables):
            raise RuntimeError(
                "Provided table name does not correspond to a valid table"
            )
        return self.tables[table_name]
