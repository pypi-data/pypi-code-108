from typing import Any
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from decimal import Decimal

from .constants import REGION_NAME, logger

def get_secret(secretId: str, regionName=REGION_NAME) -> Any:
    """Returns secret from SecretsManager in region."""
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=regionName
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secretId
        )
    except ClientError as e:
        raise e
    secret = get_secret_value_response['SecretString']

    return secret

def get_offender(offId, identifier, reason, expire_days=1, region="") -> dict:
    """Returns offender dict with needed parameters."""
    times = get_report_times(expire_days)
    reportTime = times['reportTime']
    expireTime = times['expireTime']
    offender = {'_id': offId,
                'region': region,
                'identifier': identifier,
                'reason':  reason,
                'reportTime': reportTime,
                'expireTime': expireTime
            }

    return offender

def get_report_times(expire_days=1) -> dict[str:Any]:
    """Returns dict with human-readable reportTime and expireTime(POSIX) as a keys."""
    now = datetime.utcnow()
    return {
        'reportTime': str(now),
        'expireTime': int((now + timedelta(days=expire_days)).timestamp())
    }

def serializeDDB(ddb_item: dict) -> dict:
    result = {}
    if type(ddb_item) is dict:
        for k,v in ddb_item.items():
            if type(v) is Decimal:
                try:
                    result[k] = int(v)
                except:
                    result[k] = str(v)
            elif type(v) is dict:
                    result[k] = serializeDDB(v)
            else:
                result[k] = v
    return result

async def putDataToDB(tableName:str, data:list[dict], ddb_resource=None, add_time=True, expire_days=1) -> bool:
    times = get_report_times(expire_days=expire_days)
    if not ddb_resource:
        ddb_resource = boto3.resource('dynamodb')
    table = ddb_resource.Table(tableName)
    logger.info(f"putting {len(data)} objects to {tableName}")
    with table.batch_writer() as batch:
        for item in data:
            if type(item) != dict:
                try:
                    item = item.json()
                except:
                    logger.error(f"wrong type of item ({type(item)}. Skipped)")
                    logger.debug(f"errored item: {item}")
                    continue
            if add_time:
                item['expireTime'] = times['expireTime']
                item['reportTime'] = times['reportTime']
            batch.put_item(Item=item)
    return True
        