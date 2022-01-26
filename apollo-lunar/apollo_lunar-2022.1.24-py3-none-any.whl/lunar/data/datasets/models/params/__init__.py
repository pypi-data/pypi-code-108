from .dynamodb import DynamoDBParams, DynamoDBParamsPatchIn
from .docdb import DocDBParams


PARAMS = {"dynamodb": DynamoDBParams, "docdb": DocDBParams}
PARAMS_PATCH = {"dynamodb": DynamoDBParamsPatchIn, "docdb": DocDBParams}
