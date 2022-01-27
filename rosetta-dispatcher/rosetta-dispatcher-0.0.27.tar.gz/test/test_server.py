from time import sleep

from rosetta_dispatcher.dispatch_server import DispatchServer
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel
from rosetta_dispatcher.model.dispatch_types import DispatchResponseStatus

host = '10.130.64.136'
# host = '121.11.219.106'
port = 4012

# host = '123.57.176.234'
# port = 6379
passwd = None

ds = DispatchServer(redis_host=host, redis_port=port, password=passwd)

count = 0
while True:
    # result = ds.fetch('BATCH_WORKER_QUEUE_DEV', batch_count=128)
    result = ds.fetch('WSD_BATCH_RPC_QUEUE_DEV', batch_count=16)
    print(f'fetched: {len(result)}')
    response_list = [DispatchResponseModel(correlation_id=request.correlation_id, status=DispatchResponseStatus.OK,
                                         data=request.data) for request in result]

    ds.batch_send_response(result, response_list)


